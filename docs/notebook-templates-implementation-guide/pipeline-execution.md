# 02 Pipeline Execution

`02_pipeline` is the executable delivery notebook. It starts a guided pipeline context, reads data, prepares source and target table configs, runs guardrails, writes outputs, and records evidence for support and governance review. The notebook flow is intentionally small: establish context once, keep table settings visible, call reduced-API helpers, and let active defaults carry shared run metadata downstream.

## Guided pipeline context startup

Start each `02_pipeline` run with [`start_pipeline_run`](../api/reference/start_pipeline_run.md):

```python
PIPELINE = start_pipeline_run(
    notebook_type="02_pipeline",
    select_agreement=True,
    register_notebook=True,
)
```

This single startup step captures the run id, audit timestamp, notebook metadata, and selected agreement context. It also stores active defaults for downstream helpers, so later pipeline calls can reuse the same run and agreement metadata without repeating those values in every function call.

## Source read

Use explicit Fabric IO callables such as [`read_lakehouse_table`](../api/reference/read_lakehouse_table.md), [`read_lakehouse_csv`](../api/reference/read_lakehouse_csv.md), or [`read_warehouse_query`](../api/reference/read_warehouse_query.md) for source reads. The template keeps storage intent, source table names, and transformations visible so notebook users can understand what is being read and changed.

## Warehouse sources and Spark performance

FabricOps is optimized for PySpark transformations over Lakehouse Delta tables. The Warehouse SQL endpoint is useful for SQL pushdown, reference lookups, ad hoc slices, and serving, but Warehouse access from Spark uses a connector path rather than native Delta file access. Do not treat full Warehouse table reads as the default processing layer for large or repeatedly transformed data.

Recommended pattern:

1. Initial load: copy or materialize Warehouse data into the Source Lakehouse as Delta.
2. Ongoing load: load incremental rows only, using a watermark or stable partition column.
3. Transformations: run PySpark against Lakehouse Delta with [`read_lakehouse_table`](../api/reference/read_lakehouse_table.md).
4. Outputs: write curated Delta outputs, and publish small serving outputs to Warehouse with [`write_warehouse_table`](../api/reference/write_warehouse_table.md) only when needed.

As a rule of thumb, small Warehouse reads are usually acceptable for narrow reference tables, filtered slices, or one-time ad hoc data under roughly 1 million rows or 1 GB. For 1 million to 10 million rows or 1 to 10 GB, benchmark first and prefer Lakehouse Delta if the data will be reused. For larger data, wide tables, large text columns, or repeated processing, use chunked incremental loading or Fabric Copy/Data Factory style movement into Lakehouse Delta before Spark processing.

## Pipeline table config preparation

Use [`prepare_pipeline_table_configs`](../api/reference/prepare_pipeline_table_configs.md) to enrich beginner-editable table settings into the config shape expected by guardrail and evidence helpers. The template prepares source configs before source profiling/checks and target configs before target profiling/checks.

![FabricOps pipeline guardrails](../assets/fabricops-pipeline-guardrails.png)

## Guardrail execution

Guardrails are part of `02_pipeline`. They are the runtime checks that decide whether a run can continue, continue with warnings, or stop before writing pipeline outputs. They turn agreement and rule expectations into executable checks for schema, freshness, profile behaviour, and data quality.

Use [`run_table_guardrails`](../api/reference/run_table_guardrails.md) for guardrail orchestration to evaluate table guardrails and write runtime evidence. Run profile checks before writes for non-blocking visibility, then run enforcement checks before publishing targets:

```python
source_profile_results = run_table_guardrails(
    SOURCE_TABLES,
    table_role="source",
    mode="profile",
)

target_profile_results = run_table_guardrails(
    TARGET_TABLES,
    table_role="target",
    mode="profile",
)

source_enforcement_results = run_table_guardrails(
    SOURCE_TABLES,
    table_role="source",
    mode="enforce",
)

target_enforcement_results = run_table_guardrails(
    TARGET_TABLES,
    table_role="target",
    mode="enforce",
)
```

`mode="profile"` is non-blocking by default, so the notebook can collect catalogue and guardrail visibility without stopping the run. `mode="enforce"` defaults `stop_on_failure=True`, so failed error-severity checks stop before unsafe target publication. Omitted `run_id`, `spark_session`, `pipeline_name`, `notebook_id`, `notebook_registry_id`, `agreement_id`, and `agreement_contract_version` values are resolved from the active pipeline context created by `start_pipeline_run`.

Guardrail results are not just UI messages. They are evidence rows and continuation decisions. A Warning-severity failure can continue with evidence; an Error-severity failure blocks before the next critical step.

## Contract expectation versus enforcement

FabricOps keeps the responsibility split clear:

| Concept | Responsibility |
| --- | --- |
| Data contract | Describes what the data should look like, how fresh it should be, how it should behave over time, and which DQ expectations matter. |
| Guardrail | Turns an expectation into a runtime pass, warning, fail, or skipped result. |
| `02_pipeline` | Enforces schema, freshness, profile behaviour, and active DQ rules before pipeline outputs are written. |
| `03_governance` | Reviews, approves, rejects, replaces, and deactivates guardrail rules and table governance state. |

## Guardrail flow in `02_pipeline`

| Point in the run | What happens | Why it matters |
| --- | --- | --- |
| After source read | Validate source schema, freshness, profile behaviour, and active source DQ guardrail rules. | Catch upstream structure, recency, behaviour, and quality issues before transformation. |
| Transformation | Apply user-defined deterministic business logic. | Keep the output repeatable and explainable. |
| Before target write | Validate target schema, freshness, profile behaviour, and active target DQ guardrail rules. | Avoid publishing stale, unexpected, or DQ-failing pipeline outputs. |
| After successful checks | Write the output, lineage, profile, and run summary. | Keep governance review and support grounded in what actually ran. |

## Guardrail types

| Guardrail | Checks |
| --- | --- |
| Schema guardrail | Checks expected columns and data types. |
| Freshness guardrail | Checks whether `max(freshness_column)` is recent enough based on `freshness_max_lag_days`. |
| Profile behaviour guardrail | Checks whether the current profile follows `profile_mode`: `static_data`, `changing_data`, or `skip`. |
| DQ guardrail | Checks active DQ guardrail rules from governance metadata. |

## Schema mode

[`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) offers schema mode options `strict`, `relaxed`, and `skip`. Runtime maps those as follows:

| Widget option | Runtime preset | Runtime effect |
| --- | --- | --- |
| `strict` | `strict` | Blocks missing columns, datatype mismatches, and unexpected columns. |
| `relaxed` | `allow_new_columns` | Blocks missing columns and datatype mismatches. Unexpected columns are warnings and `can_continue` remains true. |
| `skip` | `monitor_only` | Reports differences as warnings when checks exist, but `can_continue` remains true. |

![FabricOps schema guardrails](../assets/fabricops-schema-guardrails.png)

## Freshness

Freshness options are `enforce` and `skip`. `enforce` writes a `max_lag_days` rule with `freshness_column` and `max_lag_days`. `skip` writes a `skip` rule. At runtime, skip returns `skipped` with `can_continue=true`. Enforced freshness checks whether the latest value in the freshness column is older than the allowed lag; stale data fails or warns depending on rule severity.

Freshness is separate from profile behaviour: a table can follow its `profile_mode` and still be stale if the newest business date is too old.

```python
"freshness_column": "business_date",
"freshness_max_lag_days": 1,
"freshness_severity": "blocking"
```

![FabricOps freshness guardrails](../assets/fabricops-freshness-guardrails.png)

## Profile behaviour

Profile mode options are `static_data`, `changing_data`, and `skip`. `static_data` profiles the full table as one baseline. `changing_data` requires `watermark_column` and profiles each distinct watermark value separately. `skip` returns `skipped` with `can_continue=true`.

When previous accepted evidence exists, the current profile is compared to previous approved `METADATA_DATA_CATALOGUE` evidence. If no previous evidence exists, the current profile establishes the baseline. If differences are found, status depends on severity.

`append` and `overwrite` are physical write modes only. They are not profile behaviour concepts. Baselines are not silently reset inside `02_pipeline`; intentional blocked changes should be reviewed by governance or represented by superseding rule or evidence history.

![FabricOps load behaviour guardrails](../assets/fabricops-load-behaviour-guardrails.png)

| `rule_type` | Use when | Guardrail behaviour |
| --- | --- | --- |
| `static_data` | The full table should remain stable. | Treat the full table as one profile group with `watermark_value="__FULL_TABLE__"`. Row count, schema signature, profile hash, and configured profile differences must match the previous accepted or passed full-table profile. |
| `changing_data` | New business periods or partitions can arrive, but old periods must remain stable. | Require `watermark_column`, profile one group per watermark value, allow new watermark values, and fail or warn when a previously seen watermark group changes or disappears. |
| `skip` | Profile behaviour should not run for the table. | Do not create profile-behaviour comparison evidence; other guardrails still run. |

## DQ rules

[`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) offers DQ severity options `warning` and `error`. Runtime loads DQ rules from `METADATA_GUARDRAIL_RULES`. An Error-severity failure returns `failed` and `can_continue=false`; a Warning-severity failure returns `warning` and `can_continue=true`. Passing or absent DQ rules return `passed` and `can_continue=true`.

DQ does not quarantine rows, write row-level failure metadata, filter invalid rows, send alerts, or partially write targets. It records aggregate rule outcomes and continuation decisions.

![FabricOps DQ guardrails](../assets/fabricops-DQ-guardrails.png)

## Guardrail authoring and governance handoff

Guardrail authoring is still part of the pipeline workflow, not a separate public documentation page. After profiling evidence exists, the simplified `02_pipeline` flow can use [`widget_select_guardrail_target`](../api/reference/widget_select_guardrail_target.md) to pick a profiled table, [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) and [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) to author guardrail intent, and [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) to author descriptive enrichment.

For ungoverned tables, engineering-authored saves remain active and non-pending with `review_status="self_approved"`. For governed tables, authors can save drafts, submit rules for governance review, or apply rules immediately as `active_pending_governance_review` when pipeline continuity requires it.

Formal table governance review is still owned by [03 Governance Review](governance-review.md). `03_governance` uses [`widget_review_guardrail_governance`](../api/reference/widget_review_guardrail_governance.md) to review enrichment and guardrail rows, approve pending records, reject records, replace records, deactivate approved records, and view history.

## Target write

Use explicit Fabric IO callables such as [`write_lakehouse_table`](../api/reference/write_lakehouse_table.md) or [`write_warehouse_table`](../api/reference/write_warehouse_table.md) after enforcement guardrails allow the run to continue. The template keeps write mode and target routing visible so users understand what will be published, while active pipeline defaults keep shared run metadata consistent.

## Lineage writing

Use [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) to append source-to-target lineage evidence to `METADATA_DATA_LINEAGE_TABLE`. The simplified flow writes lineage after successful target writes so the run summary can include lineage status.

## Pipeline run summary

Use [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) to append run-level status to `METADATA_PIPELINE_RUNS`:

```python
runtime_summary_result = write_pipeline_run_summary(
    source_guardrail_results=source_enforcement_results,
    target_guardrail_results=target_enforcement_results,
    target_write_status=target_write_status,
    lineage_result=lineage_result,
)
```

The summary helper derives status, guardrail rollups, target write status, lineage status, and active agreement/run metadata from the result bundles and active pipeline context. Notebook authors should pass the result objects produced by the reduced flow instead of rebuilding summary fields manually.

## Guardrail result display

Use [`display_guardrail_results`](../api/reference/display_guardrail_results.md) to show profile or enforcement outcomes in `summary`, `detailed`, or `debug` mode. The display mode changes presentation only; the runtime result bundles remain available for continuation checks and run summary writing.

## Guardrail evidence tables

| Evidence area | Metadata table | Why it matters during `02_pipeline` |
| --- | --- | --- |
| Profile/evidence | `METADATA_DATA_CATALOGUE` | Stores observed table/column profiles, profile hashes, watermark values, and run context for later comparison and review. |
| Rule intent | `METADATA_GUARDRAIL_RULES` | Stores schema, freshness, profile-behaviour, and DQ rules that enforcement loads. |
| Runtime results | `METADATA_GUARDRAIL_RESULTS` | Stores pass/warn/fail/skipped status, severity, continuation flag, reason, expected/actual values, and result payloads. |
| Run summary | `METADATA_PIPELINE_RUNS` | Summarizes source/target counts, guardrail rollups, lineage/catalogue write status, and JSON detail. |
| Lineage | `METADATA_DATA_LINEAGE_TABLE` | Records source-to-target relationships for handover, dashboarding, and review context. |

## Implementation guidance

- Start the notebook with [`start_pipeline_run`](../api/reference/start_pipeline_run.md), then rely on active defaults instead of repeating run and agreement metadata in every helper call.
- Keep source and target table config dictionaries beginner-editable, then let [`prepare_pipeline_table_configs`](../api/reference/prepare_pipeline_table_configs.md) normalize them for runtime helpers.
- Treat `append` and `overwrite` as physical write modes only; profile behaviour uses `static_data`, `changing_data`, or `skip`.
- Use warning DQ rules for observability that should not block writes, and error DQ rules for checks that must stop publication.
- Do not reset baselines silently in `02_pipeline`; intentional changes should be reviewed by governance or represented by superseding rule/evidence history.

## Related navigation

Use the Function Reference when you need callable-level details for pipeline helpers; the inline links above remain direct because they sit next to the notebook step that invokes each function.

[Back to Template Notebooks](index.md){ .md-button } [View Function Reference](../reference/index.md){ .md-button }
