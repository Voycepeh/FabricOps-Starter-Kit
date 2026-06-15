# run_table_guardrails

Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:291`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/pipeline.py#L291-L485">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use in 02_pipeline before transformations or writes when table configs should be validated by the standard guardrail sequence.

**Do not use when:**

- Do not use as a replacement for individual helper calls when debugging one specific guardrail interactively.

**Additional context:**

Coordinates profiling, schema, freshness, profile behavior, DQ, and catalogue evidence checks for a group of pipeline table configs.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def run_table_guardrails(
    table_configs: list[dict[str, Any]],
    config: Any,
    env: str,
    run_id: str,
    spark_session: Any,
    agreement_id: str='',
    agreement_contract_version: str='',
    notebook_registry_id: str='',
    notebook_id: str='',
    pipeline_name: str='',
    stop_on_failure: bool=False,
) -> dict[str, Any]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
source_guardrail_results = run_table_guardrails(SOURCE_TABLES, config=CONFIG, env=ENV_NAME, run_id=RUN_ID, spark_session=spark, stop_on_failure=True)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_configs` | `list[dict[str, Any]]` | Yes | Source or target table configs. Each config must contain ``key``, ``df``, and ``expected_schema``. Optional keys such as ``dataset_name``, ``stage``, ``schema_preset``, ``profile_mode``, ``profile_behavior_severity``, ``watermark_column``, ``dq_preset``, ``distribution_columns``, and ``exclude_columns`` control the guardrail behavior. |
| `config` | `Any` | Yes | FabricOps framework configuration from ``00_env_config``. |
| `env` | `str` | Yes | Environment key used for configured metadata routing. |
| `run_id` | `str` | Yes | Current pipeline run identifier. |
| `spark_session` | `Any` | Yes | Spark session used by profile behavior and DQ helpers. |
| `agreement_id` | `str` | No | Governance context written with catalogue evidence. |
| `agreement_contract_version` | `str` | No | Not documented yet |
| `notebook_registry_id` | `str` | No | Not documented yet |
| `notebook_id` | `str` | No | Not documented yet |
| `pipeline_name` | `str` | No | Not documented yet |
| `stop_on_failure` | `bool` | No | When True, collect all guardrail results and catalogue evidence, then stop notebook execution via the standard guardrail stopper if any table cannot continue. |

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

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.guardrails.validate_schema</code></a>
- `fabricops_kit.pipeline._build_guardrail_evidence_definitions`
- `fabricops_kit.pipeline._guardrail_can_continue`
- `fabricops_kit.pipeline._table_key`
- `fabricops_kit.pipeline._table_name`
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`

**Side effects:**

Profiles DataFrames, reads stability/DQ metadata through configured metadata routing, writes catalogue evidence, and may update table config DataFrames with DQ annotations.

**Notes:**

This helper intentionally collects all per-table schema, freshness, profile behavior, and DQ
results before reporting blocking failures. DQ results that return an
annotated DataFrame update the corresponding table config ``df`` in place
so downstream writes use the checked DataFrame. Metadata reads and writes
are routed through the configured metadata target by the called helpers.

</details>

??? info "Call flow"

    ```text
    run_table_guardrails(...)
    ├── _build_guardrail_evidence_definitions(...)
    │   ├── _table_key(...)
    │   └── _table_name(...)
    ├── _guardrail_can_continue(...)
    ├── _table_key(...)
    ├── _table_name(...)
    ├── enforce_dq_rules(...)
    │   ├── _dq_failed_row_count(...)
    │   │   ├── _dq_failed_expression(...)
    │   │   │   ├── _spark_sql_helpers(...)
    │   │   │   └── _validate_dq_rules(...)
    │   │   │       └── _canonical_dq_rule_type(...)
    │   │   └── _spark_sql_helpers(...)
    │   ├── _dq_summary(...)
    │   │   ├── _current_audit_timestamp(...)
    │   │   │   └── _get_audit_timezone(...)
    │   │   │       └── _validate_audit_timezone(...)
    │   │   └── _summarize_dq_guardrail(...)
    │   ├── _dq_tagged_dataframe(...)
    │   │   ├── _dq_failed_expression(...)
    │   │   │   ├── _spark_sql_helpers(...)
    │   │   │   └── _validate_dq_rules(...)
    │   │   │       └── _canonical_dq_rule_type(...)
    │   │   └── _spark_sql_helpers(...)
    │   ├── _load_active_dq_rules(...)
    │   │   ├── _canonical_dq_rule_type(...)
    │   │   ├── _coerce_rows(...)
    │   │   ├── _latest_dq_rule_versions(...)
    │   │   │   └── _spark_sql_helpers(...)
    │   │   ├── _spark_sql_helpers(...)
    │   │   └── _validate_dq_rules(...)
    │   │       └── _canonical_dq_rule_type(...)
    │   ├── _read_guardrail_rule_metadata(...)
    │   │   ├── _configured_lakehouse_schema(...)
    │   │   │   ├── _get_store(...)
    │   │   │   │   └── _normalize_path_config(...)
    │   │   │   │       └── PathConfig(...)
    │   │   │   └── _normalize_schema_name(...)
    │   │   ├── _spark_sql_helpers(...)
    │   │   └── read_lakehouse_table(...)
    │   │       ├── _get_spark(...)
    │   │       ├── _get_store(...)
    │   │       │   └── _normalize_path_config(...)
    │   │       │       └── PathConfig(...)
    │   │       ├── _normalize_table_name(...)
    │   │       └── _resolve_lakehouse_table_path(...)
    │   │           ├── _normalize_table_name(...)
    │   │           └── _resolve_lakehouse_schema(...)
    │   │               └── _normalize_schema_name(...)
    │   ├── _run_dq_guardrail_checks(...)
    │   │   ├── _dq_check_status(...)
    │   │   ├── _dq_failed_expression(...)
    │   │   │   ├── _spark_sql_helpers(...)
    │   │   │   └── _validate_dq_rules(...)
    │   │   │       └── _canonical_dq_rule_type(...)
    │   │   ├── _spark_sql_helpers(...)
    │   │   └── _validate_dq_rules(...)
    │   │       └── _canonical_dq_rule_type(...)
    │   └── _summarize_dq_guardrail(...)
    ├── enforce_freshness(...)
    │   ├── _coerce_date(...)
    │   ├── _iso_date_value(...)
    │   │   └── _coerce_date(...)
    │   └── _max_column_value(...)
    ├── enforce_profile_behavior(...)
    │   ├── _accepted_profile_rows(...)
    │   │   ├── _catalogue_value(...)
    │   │   ├── _row_to_dict(...)
    │   │   └── _string_value(...)
    │   ├── _catalogue_value(...)
    │   ├── _configured_lakehouse_schema(...)
    │   │   ├── _get_store(...)
    │   │   │   └── _normalize_path_config(...)
    │   │   │       └── PathConfig(...)
    │   │   └── _normalize_schema_name(...)
    │   ├── _guardrail_exclude_columns(...)
    │   ├── _is_missing_table_error(...)
    │   ├── _json_dumps_stable(...)
    │   ├── _profile_hash(...)
    │   │   └── _json_dumps_stable(...)
    │   ├── _profile_payload_from_profile(...)
    │   │   ├── _normalize_profile(...)
    │   │   │   └── _normalize_profile(...) (recursive)
    │   │   ├── _profile_row_count(...)
    │   │   │   └── _normalize_profile(...)
    │   │   │       └── _normalize_profile(...) (recursive)
    │   │   ├── _schema_signature(...)
    │   │   │   └── _actual_schema(...)
    │   │   │       └── _normalize_datatype(...)
    │   │   └── _string_value(...)
    │   ├── _select_profile_behavior_rule(...)
    │   │   ├── _catalogue_value(...)
    │   │   ├── _row_to_dict(...)
    │   │   └── _string_value(...)
    │   ├── _string_value(...)
    │   ├── profile_dataframe(...)
    │   │   ├── _audit_timestamp_expr(...)
    │   │   │   └── _get_audit_timezone(...)
    │   │   │       └── _validate_audit_timezone(...)
    │   │   ├── _build_distribution_summaries(...)
    │   │   │   ├── _build_categorical_distribution(...)
    │   │   │   ├── _build_numeric_distribution(...)
    │   │   │   └── _numeric_bin_edges(...)
    │   │   ├── _get_audit_timezone(...)
    │   │   │   └── _validate_audit_timezone(...)
    │   │   ├── _get_profiled_columns(...)
    │   │   └── _is_min_max_supported_type(...)
    │   ├── read_lakehouse_table(...)
    │   │   ├── _get_spark(...)
    │   │   ├── _get_store(...)
    │   │   │   └── _normalize_path_config(...)
    │   │   │       └── PathConfig(...)
    │   │   ├── _normalize_table_name(...)
    │   │   └── _resolve_lakehouse_table_path(...)
    │   │       ├── _normalize_table_name(...)
    │   │       └── _resolve_lakehouse_schema(...)
    │   │           └── _normalize_schema_name(...)
    │   └── write_lakehouse_table(...)
    │       ├── _get_store(...)
    │       │   └── _normalize_path_config(...)
    │       │       └── PathConfig(...)
    │       ├── _normalize_table_name(...)
    │       └── _resolve_lakehouse_table_path(...)
    │           ├── _normalize_table_name(...)
    │           └── _resolve_lakehouse_schema(...)
    │               └── _normalize_schema_name(...)
    ├── profile_dataframe(...)
    │   ├── _audit_timestamp_expr(...)
    │   │   └── _get_audit_timezone(...)
    │   │       └── _validate_audit_timezone(...)
    │   ├── _build_distribution_summaries(...)
    │   │   ├── _build_categorical_distribution(...)
    │   │   ├── _build_numeric_distribution(...)
    │   │   └── _numeric_bin_edges(...)
    │   ├── _get_audit_timezone(...)
    │   │   └── _validate_audit_timezone(...)
    │   ├── _get_profiled_columns(...)
    │   └── _is_min_max_supported_type(...)
    ├── stop_if_failed(...)
    │   └── SchemaDriftError(...)
    ├── validate_schema(...)
    │   ├── _actual_schema(...)
    │   │   └── _normalize_datatype(...)
    │   └── _normalize_datatype(...)
    └── write_catalogue_evidence(...)
        ├── _build_metadata_table_key(...)
        │   └── _stable_metadata_key(...)
        ├── _canonical_catalogue_profile_df(...)
        ├── _configured_lakehouse_schema(...)
        │   ├── _get_store(...)
        │   │   └── _normalize_path_config(...)
        │   │       └── PathConfig(...)
        │   └── _normalize_schema_name(...)
        ├── _definition_name(...)
        ├── _dq_summary_fields(...)
        │   └── _now_iso(...)
        │       └── _current_audit_timestamp(...)
        │           └── _get_audit_timezone(...)
        │               └── _validate_audit_timezone(...)
        ├── _normalize_catalogue_evidence_types(...)
        ├── _now_iso(...)
        │   └── _current_audit_timestamp(...)
        │       └── _get_audit_timezone(...)
        │           └── _validate_audit_timezone(...)
        ├── _runtime_audit_fields(...)
        │   ├── _build_runtime_audit_fields(...)
        │   │   ├── _context_get(...)
        │   │   ├── _current_audit_timestamp(...)
        │   │   │   └── _get_audit_timezone(...)
        │   │   │       └── _validate_audit_timezone(...)
        │   │   ├── _get_store(...)
        │   │   │   └── _normalize_path_config(...)
        │   │   │       └── PathConfig(...)
        │   │   ├── _runtime_context(...)
        │   │   │   └── _context_get(...)
        │   │   └── _safe_str(...)
        │   └── _now_iso(...)
        │       └── _current_audit_timestamp(...)
        │           └── _get_audit_timezone(...)
        │               └── _validate_audit_timezone(...)
        └── write_lakehouse_table(...)
            ├── _get_store(...)
            │   └── _normalize_path_config(...)
            │       └── PathConfig(...)
            ├── _normalize_table_name(...)
            └── _resolve_lakehouse_table_path(...)
                ├── _normalize_table_name(...)
                └── _resolve_lakehouse_schema(...)
                    └── _normalize_schema_name(...)
    ```

??? info "Internal helpers used: 4"

    This callable uses 4 internal helpers for metadata loading and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/pipeline.py#L258-L288"><code>_build_guardrail_evidence_definitions</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/pipeline.py#L246-L247"><code>_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/pipeline.py#L250-L251"><code>_table_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/pipeline.py#L254-L255"><code>_guardrail_can_continue</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.run_table_guardrails`
- Short name: `run_table_guardrails`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `291`
- Inbound references count: 0
- Outbound references count: 11
- Used in templates: 02_pipeline
- Glossary terms: guardrail, can_continue, source table, target table, catalogue evidence

### AI implementation contract

- **required_context:** Requires CONFIG and env from 00_env_config so metadata operations use the configured metadata target.
- **inputs:** table_configs plus config, env, run_id, spark_session, and agreement/notebook context.
- **output:** Guardrail result bundle with profiles, schema results, freshness results, stability results, DQ results, catalogue status, evidence definitions, summary, can_continue, and failed_tables.
- **side_effects:** Profiles DataFrames, reads stability/DQ metadata through configured metadata routing, writes catalogue evidence, and may update table config DataFrames with DQ annotations.
- **failure_modes:** Not documented yet
- **verification:** Verify stop_on_failure=True is used before transformation or writes when blocking guardrails should stop execution.

### Inbound references

Not documented yet

### Outbound references

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../enforce_dq_rules/"><code>fabricops_kit.governance_review.enforce_dq_rules</code></a>
- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.guardrails.validate_schema</code></a>
- `fabricops_kit.pipeline._build_guardrail_evidence_definitions`
- `fabricops_kit.pipeline._guardrail_can_continue`
- `fabricops_kit.pipeline._table_key`
- `fabricops_kit.pipeline._table_name`
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/pipeline.py#L291-L485">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/3e001614cf85795444c3c0452f682de48e8b826e/src/fabricops_kit/pipeline.py#L291-L485</a>
- Start line: `291`
- End line: `485`
- Signature:

```python
def run_table_guardrails(
    table_configs: list[dict[str, Any]],
    config: Any,
    env: str,
    run_id: str,
    spark_session: Any,
    agreement_id: str='',
    agreement_contract_version: str='',
    notebook_registry_id: str='',
    notebook_id: str='',
    pipeline_name: str='',
    stop_on_failure: bool=False,
) -> dict[str, Any]:
```

### Internal relationship graph

### Public related functions

- <a href="../prepare_pipeline_table_configs/"><code>fabricops_kit.pipeline.prepare_pipeline_table_configs</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

### Internal implementation summary

- Internal helper count: 4
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **can_continue:** A returned true/false value that tells downstream code whether the pipeline should keep running.
- **Source table:** An input table or file read by the pipeline.
- **Target table:** An output table written by the pipeline.
- **Catalogue evidence:** Reviewed metadata that explains what FabricOps knows about a dataset or table.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
