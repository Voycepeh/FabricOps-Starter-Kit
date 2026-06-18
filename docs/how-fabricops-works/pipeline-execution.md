# 02 Pipeline Execution

`02_pipeline` is the executable delivery notebook. It selects the agreement context, reads data, prepares source and target table configs, runs guardrails, writes outputs, and records evidence for support and governance review.

## Agreement selection

Use [`widget_select_agreement`](../api/reference/widget_select_agreement.md) to select the agreement for the notebook run. Then use [`get_selected_agreement`](../api/reference/get_selected_agreement.md) to retrieve the selected agreement values for pipeline metadata and evidence.

## Source read

Use [`read_data`](../api/reference/read_data.md) for source reads. The template keeps source table names and transformations visible so notebook users can understand what is being read and changed.

## Pipeline table config preparation

Use [`prepare_pipeline_table_configs`](../api/reference/prepare_pipeline_table_configs.md) to enrich beginner-editable table settings into the config shape expected by guardrail and evidence helpers. The template prepares source configs before source profiling/checks and target configs before target profiling/checks.

![FabricOps pipeline guardrails](../assets/fabricops-pipeline-guardrails.png)

## Guardrail execution

Use [`run_table_guardrails`](../api/reference/run_table_guardrails.md) to evaluate table guardrails and write runtime evidence. Guardrail results are not just UI messages: they are evidence rows and continuation decisions. The dropdowns used during authoring save rule records in `METADATA_GUARDRAIL_RULES`; runtime interprets those saved records later.

### Schema mode

[`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) offers schema mode options `strict`, `relaxed`, and `skip`. Runtime maps those as follows:

| Widget option | Runtime preset | Runtime effect |
| --- | --- | --- |
| `strict` | `strict` | Blocks missing columns, datatype mismatches, and unexpected columns. |
| `relaxed` | `allow_new_columns` | Blocks missing columns and datatype mismatches. Unexpected columns are warnings and `can_continue` remains true. |
| `skip` | `monitor_only` | Reports differences as warnings when checks exist, but `can_continue` remains true. |

### Freshness

Freshness options are `enforce` and `skip`. `enforce` writes a `max_lag_days` rule with `freshness_column` and `max_lag_days`. `skip` writes a `skip` rule. At runtime, skip returns `skipped` with `can_continue=true`. Enforced freshness checks whether the latest value in the freshness column is older than the allowed lag; stale data fails or warns depending on rule severity.

### Profile mode

Profile mode options are `static_data`, `changing_data`, and `skip`. `static_data` profiles the full table as one baseline. `changing_data` requires `watermark_column` and profiles each distinct watermark value separately. `skip` returns `skipped` with `can_continue=true`.

When previous accepted catalogue evidence exists, current profile evidence is compared to previous accepted `METADATA_DATA_CATALOGUE` evidence. If no previous evidence exists, the current profile establishes the baseline. If differences are found, status depends on severity.

### DQ rules

[`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) offers DQ severity options `warning` and `error`. Runtime loads DQ rules from `METADATA_GUARDRAIL_RULES`. Error-severity failures return `failed` and `can_continue=false`; warning-severity failures return `warning` and `can_continue=true`. Passing or absent DQ rules return `passed` and `can_continue=true`.

DQ does not quarantine rows, write row-level failure metadata, filter invalid rows, send alerts, or partially write targets. It records aggregate rule outcomes and continuation decisions.

## Target write

Use [`write_data`](../api/reference/write_data.md) after source and target guardrails allow the run to continue. The template keeps write mode and target routing visible so users understand what will be published.

## Lineage writing

Use [`write_pipeline_lineage`](../api/reference/write_pipeline_lineage.md) to append source-to-target lineage evidence to `METADATA_DATA_LINEAGE_TABLE`.

## Pipeline run summary

Use [`write_pipeline_run_summary`](../api/reference/write_pipeline_run_summary.md) to append run-level status and selected agreement context to `METADATA_PIPELINE_RUNS`.

## Guardrail result display

Use [`display_guardrail_results`](../api/reference/display_guardrail_results.md) to show guardrail outcomes in `summary`, `detailed`, or `debug` mode. The display mode changes presentation only; the runtime result bundle remains available to the notebook.

## Optional metadata enrichment and guardrail authoring

After profiling evidence exists, `02_pipeline` can use [`widget_select_guardrail_target`](../api/reference/widget_select_guardrail_target.md) to pick a profiled table, [`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md) and [`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md) to author guardrail intent, and [`widget_enrich_table_metadata`](../api/reference/widget_enrich_table_metadata.md) to author descriptive enrichment. The current `02_pipeline` template also imports and calls [`widget_review_guardrail_governance`](../api/reference/widget_review_guardrail_governance.md); formal table governance review is still owned by [03 Governance Review](governance-review.md).

## Guardrail evidence tables

| Evidence area | Metadata table | Why it matters during `02_pipeline` |
| --- | --- | --- |
| Profile/catalogue evidence | `METADATA_DATA_CATALOGUE` | Stores observed table/column profiles, profile hashes, watermark values, and run context for later comparison and review. |
| Rule intent | `METADATA_GUARDRAIL_RULES` | Stores schema, freshness, profile-behaviour, and DQ rules that runtime enforcement loads. |
| Runtime results | `METADATA_GUARDRAIL_RESULTS` | Stores pass/warn/fail/skipped status, severity, continuation flag, reason, expected/actual values, and result payloads. |
| Run summary | `METADATA_PIPELINE_RUNS` | Summarizes source/target counts, guardrail rollups, lineage/catalogue write status, and JSON detail. |
| Lineage | `METADATA_DATA_LINEAGE_TABLE` | Records source-to-target relationships for handover, dashboarding, and review context. |

![FabricOps schema guardrails](../assets/fabricops-schema-guardrails.png)

![FabricOps freshness guardrails](../assets/fabricops-freshness-guardrails.png)

![FabricOps DQ guardrails](../assets/fabricops-DQ-guardrails.png)

### Implementation guidance

- Keep source and target table config dictionaries beginner-editable, then let [`prepare_pipeline_table_configs`](../api/reference/prepare_pipeline_table_configs.md) normalize them for runtime helpers.
- Treat `append` and `overwrite` as physical write modes only; profile behaviour uses `static_data`, `changing_data`, or `skip`.
- Use warning DQ rules for observability that should not block writes, and error DQ rules for checks that must stop publication.
- Do not reset baselines silently in `02_pipeline`; intentional changes should be reviewed by governance or represented by superseding rule/evidence history.
