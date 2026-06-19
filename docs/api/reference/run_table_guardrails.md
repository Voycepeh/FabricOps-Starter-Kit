# run_table_guardrails

Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:686`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L686-L949">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use in 02_pipeline before transformations or writes when table configs should be validated by the standard guardrail sequence.

### Do not use when

- Do not use as a replacement for individual helper calls when debugging one specific guardrail interactively.

### Additional context

Coordinates profiling, schema, freshness, profile behavior, DQ, and evidence checks for a group of pipeline table configs.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def run_table_guardrails(
    table_configs: list[dict[str, Any]],
    run_id: str | None=None,
    context: dict[str, Any] | None=None,
    spark_session: Any | None=None,
    agreement_id: str='',
    agreement_contract_version: str='',
    notebook_registry_id: str='',
    notebook_id: str='',
    pipeline_name: str='',
    table_role: str='',
    mode: str='profile',
    stop_on_failure: bool | None=None,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
source_guardrail_results = run_table_guardrails(SOURCE_TABLES, config=CONFIG, env=ENV, run_id=RUN_ID, spark_session=spark, stop_on_failure=True)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_configs` | `list[dict[str, Any]]` | Yes | Source or target table configs. Each config must contain ``key``, ``df``, and ``expected_schema``. Optional keys such as ``dataset_name``, ``stage``, ``schema_preset``, ``profile_mode``, ``profile_behavior_severity``, ``watermark_column``, ``dq_preset``, ``distribution_columns``, and ``exclude_columns`` control the guardrail behavior. |
| `run_id` | `str \| None` | No | Current pipeline run identifier. When omitted, the active context from :func:`start_pipeline_run` is used. |
| `context` | `dict[str, Any] \| None` | No | Advanced override for the active Fabric context. When omitted, the helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``. |
| `spark_session` | `Any \| None` | No | Spark session used by profile behavior and DQ helpers. When omitted, the active context from :func:`start_pipeline_run` is used. |
| `agreement_id` | `str` | No | Governance context written with catalogue evidence. Omitted values are resolved from the active context when available. |
| `agreement_contract_version` | `str` | No | Not documented yet |
| `notebook_registry_id` | `str` | No | Not documented yet |
| `notebook_id` | `str` | No | Not documented yet |
| `pipeline_name` | `str` | No | Not documented yet |
| `table_role` | `str` | No | Template-facing table role used to retain source and target definitions in the active context for summary defaults. |
| `mode` | `str` | No | Template-facing mode. ``profile`` defaults to non-blocking display, and ``enforce`` defaults to ``stop_on_failure=True``. |
| `stop_on_failure` | `bool \| None` | No | When True, collect all guardrail results and catalogue evidence, then stop notebook execution via the standard guardrail stopper if any table cannot continue. When omitted, the default is derived from ``mode``. |

## Returns

Guardrail result bundle with profiles, schema results, freshness results, stability results, DQ results, catalogue status, evidence definitions, summary, can_continue, and failed_tables.

### Return interpretation

The result groups each guardrail outcome and a summary DataFrame. If any blocking result has can_continue false, stop before writing data.

## Raises / Errors

Not documented yet

### Common failure causes

- One of the table configs is incomplete.
- A schema, freshness, profile behavior, or DQ check fails.
- Approved metadata evidence cannot be read.
- Spark cannot profile or validate one of the DataFrames.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.config.resolve_fabric_context`
- <a href="profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- `fabricops_kit.guardrails.enforce_freshness`
- `fabricops_kit.guardrails.enforce_freshness_rule`
- `fabricops_kit.guardrails.enforce_profile_behavior`
- `fabricops_kit.guardrails.stop_if_failed`
- `fabricops_kit.metadata._build_metadata_table_key`
- `fabricops_kit.metadata._write_guardrail_result_row`
- `fabricops_kit.pipeline._active_pipeline_context`
- `fabricops_kit.pipeline._build_guardrail_blocking_message_from_bundle`
- `fabricops_kit.pipeline._build_guardrail_evidence_definitions`
- `fabricops_kit.pipeline._guardrail_can_continue`
- `fabricops_kit.pipeline._table_key`
- `fabricops_kit.pipeline._table_name`
- `fabricops_kit.pipeline.build_guardrail_detail_rows`
- `fabricops_kit.pipeline.build_guardrail_summary_rows`
- `fabricops_kit.pipeline.write_catalogue_evidence`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `02_pipeline`

**Side effects:**

Profiles DataFrames, reads stability/DQ metadata through configured metadata routing, writes evidence, and may update table config DataFrames with DQ annotations.

**Notes:**

This helper intentionally collects all per-table schema, freshness, profile behavior, and DQ
results before reporting blocking failures. DQ results that return an
annotated DataFrame update the corresponding table config ``df`` in place
so downstream writes use the checked DataFrame. Metadata reads and writes
are routed through the configured metadata target by the called helpers.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    run_table_guardrails(...)
    ├── _active_pipeline_context(...)
    ├── _build_guardrail_blocking_message_from_bundle(...)
    │   ├── _blocking_guardrail_message(...)
    │   └── build_guardrail_summary_rows(...)
    │       └── …
    ├── _build_guardrail_evidence_definitions(...)
    │   ├── _table_key(...)
    │   └── _table_name(...)
    ├── _build_metadata_table_key(...)
    │   └── _stable_metadata_key(...)
    ├── _check_schema_rule_runtime(...)
    │   ├── _apply_bypass_post_review_warning(...)
    │   │   └── …
    │   ├── _catalogue_value(...)
    │   ├── _check_schema_runtime(...)
    │   │   └── …
    │   ├── _parse_rule_parameters(...)
    │   │   └── …
    │   ├── _select_table_guardrail_rule(...)
    │   │   └── …
    │   └── _string_value(...)
    ├── _check_schema_runtime(...)
    │   ├── _actual_schema(...)
    │   │   └── …
    │   └── _normalize_datatype(...)
    ├── _guardrail_can_continue(...)
    ├── _table_key(...)
    ├── _table_name(...)
    ├── _write_guardrail_result_row(...)
    │   ├── _build_runtime_audit_fields(...)
    │   │   └── …
    │   ├── _configured_lakehouse_schema(...)
    │   │   └── …
    │   ├── _now_utc_iso(...)
    │   │   └── …
    │   └── write_lakehouse_table(...)
    │       └── …
    ├── build_guardrail_detail_rows(...)
    │   ├── _guardrail_reason(...)
    │   │   └── …
    │   ├── _next_action(...)
    │   ├── _result_can_continue(...)
    │   ├── _result_status(...)
    │   ├── _table_keys(...)
    │   └── _yes_no(...)
    ├── build_guardrail_summary_rows(...)
    │   ├── _guardrail_reason(...)
    │   │   └── …
    │   ├── _next_action(...)
    │   ├── _result_can_continue(...)
    │   ├── _result_status(...)
    │   ├── _table_keys(...)
    │   └── _yes_no(...)
    ├── enforce_dq_rules(...)
    │   ├── _dq_failed_row_count(...)
    │   │   └── …
    │   ├── _dq_summary(...)
    │   │   └── …
    │   ├── _dq_tagged_dataframe(...)
    │   │   └── …
    │   ├── _load_active_dq_rules(...)
    │   │   └── …
    │   ├── _read_guardrail_rule_metadata(...)
    │   │   └── …
    │   ├── _run_dq_guardrail_checks(...)
    │   │   └── …
    │   ├── _summarize_dq_guardrail(...)
    │   └── _write_guardrail_result_row(...)
    │       └── …
    ├── enforce_freshness(...)
    │   ├── _coerce_date(...)
    │   ├── _iso_date_value(...)
    │   │   └── …
    │   └── _max_column_value(...)
    ├── enforce_freshness_rule(...)
    │   ├── _apply_bypass_post_review_warning(...)
    │   │   └── …
    │   ├── _catalogue_value(...)
    │   ├── _parse_rule_parameters(...)
    │   │   └── …
    │   ├── _select_table_guardrail_rule(...)
    │   │   └── …
    │   ├── _string_value(...)
    │   └── enforce_freshness(...)
    │       └── …
    ├── enforce_profile_behavior(...)
    │   ├── _accepted_profile_rows(...)
    │   │   └── …
    │   ├── _apply_bypass_post_review_warning(...)
    │   │   └── …
    │   ├── _catalogue_value(...)
    │   ├── _configured_lakehouse_schema(...)
    │   │   └── …
    │   ├── _guardrail_exclude_columns(...)
    │   ├── _is_missing_table_error(...)
    │   ├── _json_dumps_stable(...)
    │   ├── _profile_hash(...)
    │   │   └── …
    │   ├── _profile_payload_from_profile(...)
    │   │   └── …
    │   ├── _select_profile_behavior_rule(...)
    │   │   └── …
    │   ├── _string_value(...)
    │   ├── _write_guardrail_result_row(...)
    │   │   └── …
    │   ├── profile_dataframe(...)
    │   │   └── …
    │   └── read_lakehouse_table(...)
    │       └── …
    ├── profile_dataframe(...)
    │   ├── _audit_timestamp_expr(...)
    │   │   └── …
    │   ├── _build_distribution_summaries(...)
    │   │   └── …
    │   ├── _get_audit_timezone(...)
    │   │   └── …
    │   ├── _get_profiled_columns(...)
    │   └── _is_min_max_supported_type(...)
    ├── resolve_fabric_context(...)
    │   └── get_default_fabric_context(...)
    ├── stop_if_failed(...)
    │   └── SchemaDriftError(...)
    └── write_catalogue_evidence(...)
        ├── _build_metadata_table_key(...)
        │   └── …
        ├── _canonical_catalogue_profile_df(...)
        ├── _configured_lakehouse_schema(...)
        │   └── …
        ├── _definition_name(...)
        ├── _normalize_catalogue_evidence_types(...)
        ├── _now_iso(...)
        │   └── …
        ├── _runtime_audit_fields(...)
        │   └── …
        └── write_lakehouse_table(...)
            └── …
    ```

??? info "Internal helpers used: 89"

    This callable uses 89 internal helpers for audit timestamp, metadata loading, validation, rule parsing, profile comparison, column handling, rule evaluation, result summary, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L216-L221"><code>_audit_timestamp_expr</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L188-L199"><code>_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L653-L683"><code>_build_guardrail_evidence_definitions</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L92-L110"><code>_check_schema_rule_runtime</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L313-L408"><code>_check_schema_runtime</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L164-L177"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L915-L918"><code>_is_missing_table_error</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L213-L214"><code>_json_dumps_stable</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1309-L1330"><code>_latest_dq_rule_versions</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1333-L1380"><code>_load_active_dq_rules</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L233-L250"><code>_normalize_catalogue_evidence_types</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L105-L114"><code>_normalize_table_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L226-L247"><code>_profile_payload_from_profile</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1600-L1607"><code>_read_guardrail_rule_metadata</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L138-L144"><code>_resolve_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L147-L154"><code>_resolve_lakehouse_table_path</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L54-L79"><code>_select_table_guardrail_rule</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L641-L642"><code>_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L368-L375"><code>_table_keys</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L645-L646"><code>_table_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1235-L1307"><code>_validate_dq_rules</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Validation</h4>
        <p>Validate inputs and guard conditions before the workflow continues.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1468-L1471"><code>_dq_check_status</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L201-L204"><code>_normalize_dq_severity</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1474-L1509"><code>_run_dq_guardrail_checks</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L202-L230"><code>_canonical_catalogue_profile_df</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L197-L198"><code>_canonical_dq_rule_type</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L162-L163"><code>_definition_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L145-L191"><code>_normalize_datatype</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L637-L677"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L411-L479"><code>_normalize_profile</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L117-L128"><code>_normalize_schema_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L46-L51"><code>_parse_rule_parameters</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L259-L261"><code>_result_status</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Profile comparison</h4>
        <p>Compare current evidence with accepted profile values and behavior baselines.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L673-L684"><code>_catalogue_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L499-L511"><code>_profile_row_count</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L482-L489"><code>_row_to_dict</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L687-L688"><code>_string_value</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Column handling</h4>
        <p>Select, exclude, and normalize column names used by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L59-L82"><code>_get_profiled_columns</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L492-L496"><code>_guardrail_exclude_columns</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1384-L1466"><code>_dq_failed_expression</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1548-L1558"><code>_dq_failed_row_count</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L340-L352"><code>_dq_reason</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1561-L1576"><code>_dq_summary</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1512-L1545"><code>_dq_tagged_dataframe</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L36-L43"><code>_is_active_guardrail_rule</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L32-L33"><code>_rule_review_status</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L251-L276"><code>_select_profile_behavior_rule</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1225-L1232"><code>_spark_sql_helpers</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L1579-L1596"><code>_summarize_dq_guardrail</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Result summary</h4>
        <p>Build final statuses, counts, and messages for the caller.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L476-L487"><code>_blocking_guardrail_message</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L193-L223"><code>_build_distribution_summaries</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L490-L496"><code>_build_guardrail_blocking_message_from_bundle</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L278-L289"><code>_next_action</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L264-L268"><code>_result_can_continue</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L271-L275"><code>_result_reason</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/fabric_input_output.py#L187-L218"><code>_get_spark</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L680-L719"><code>_get_store</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L85-L105"><code>_is_min_max_supported_type</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L278-L307"><code>_accepted_profile_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L153-L155"><code>_active_pipeline_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L194-L209"><code>_actual_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L82-L89"><code>_apply_bypass_post_review_warning</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L153-L190"><code>_build_categorical_distribution</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L121-L150"><code>_build_numeric_distribution</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L547-L564"><code>_coerce_date</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/governance_review.py#L62-L67"><code>_coerce_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L306-L310"><code>_freshness_reason</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L649-L650"><code>_guardrail_can_continue</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L355-L365"><code>_guardrail_reason</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L567-L569"><code>_iso_date_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L514-L544"><code>_max_column_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L158-L159"><code>_now_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L108-L118"><code>_numeric_bin_edges</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L313-L337"><code>_profile_behavior_reason</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L217-L218"><code>_profile_hash</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/metadata.py#L169-L170"><code>_safe_str</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L292-L303"><code>_schema_reason</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/guardrails.py#L221-L223"><code>_schema_signature</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L254-L256"><code>_yes_no</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.run_table_guardrails`
- Short name: `run_table_guardrails`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `686`
- Inbound references count: 0
- Outbound references count: 18
- Used in templates: 02_pipeline
- Glossary terms: guardrails, can_continue, source data, target table, evidence

### Implementation contract

- **required_context:** Requires CONFIG and env from 00_env_config so metadata operations use the configured metadata target.
- **inputs:** table_configs plus config, env, run_id, spark_session, and agreement/notebook context.
- **output:** Guardrail result bundle with profiles, schema results, freshness results, stability results, DQ results, catalogue status, evidence definitions, summary, can_continue, and failed_tables.
- **side_effects:** Profiles DataFrames, reads stability/DQ metadata through configured metadata routing, writes evidence, and may update table config DataFrames with DQ annotations.
- **failure_modes:** Not documented yet
- **verification:** Verify stop_on_failure=True is used before transformation or writes when blocking guardrails should stop execution.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.config.resolve_fabric_context`
- <a href="profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- `fabricops_kit.guardrails.enforce_freshness`
- `fabricops_kit.guardrails.enforce_freshness_rule`
- `fabricops_kit.guardrails.enforce_profile_behavior`
- `fabricops_kit.guardrails.stop_if_failed`
- `fabricops_kit.metadata._build_metadata_table_key`
- `fabricops_kit.metadata._write_guardrail_result_row`
- `fabricops_kit.pipeline._active_pipeline_context`
- `fabricops_kit.pipeline._build_guardrail_blocking_message_from_bundle`
- `fabricops_kit.pipeline._build_guardrail_evidence_definitions`
- `fabricops_kit.pipeline._guardrail_can_continue`
- `fabricops_kit.pipeline._table_key`
- `fabricops_kit.pipeline._table_name`
- `fabricops_kit.pipeline.build_guardrail_detail_rows`
- `fabricops_kit.pipeline.build_guardrail_summary_rows`
- `fabricops_kit.pipeline.write_catalogue_evidence`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L686-L949">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L686-L949</a>
- Start line: `686`
- End line: `949`
- Signature:

```python
def run_table_guardrails(
    table_configs: list[dict[str, Any]],
    run_id: str | None=None,
    context: dict[str, Any] | None=None,
    spark_session: Any | None=None,
    agreement_id: str='',
    agreement_contract_version: str='',
    notebook_registry_id: str='',
    notebook_id: str='',
    pipeline_name: str='',
    table_role: str='',
    mode: str='profile',
    stop_on_failure: bool | None=None,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="prepare_pipeline_table_configs/"><code>fabricops_kit.pipeline.prepare_pipeline_table_configs</code></a>
- `fabricops_kit.pipeline.write_catalogue_evidence`

### Internal implementation summary

- Internal helper count: 89
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Guardrails</summary>Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</details>
- <details class="glossary-chip"><summary>can_continue</summary>Boolean result that tells downstream notebook code whether processing can keep running.</details>
- <details class="glossary-chip"><summary>Source data</summary>Input data read from configured upstream files, tables, Lakehouses, or Warehouses before transformation.</details>
- <details class="glossary-chip"><summary>Target table</summary>A written table produced by a pipeline output.</details>
- <details class="glossary-chip"><summary>Evidence</summary>Stored proof that a profile, decision, result, or relationship existed at a point in time.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
