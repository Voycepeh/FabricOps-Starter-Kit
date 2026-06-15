# run_table_guardrails

Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:292`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/pipeline.py#L292-L506">View on GitHub</a>
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
- `fabricops_kit.pipeline._write_guardrail_result_row`
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

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    run_table_guardrails(...)
    ├── _build_guardrail_evidence_definitions(...)
    │   ├── _table_key(...)
    │   └── _table_name(...)
    ├── _guardrail_can_continue(...)
    ├── _table_key(...)
    ├── _table_name(...)
    ├── _write_guardrail_result_row(...)
    │   ├── _configured_lakehouse_schema(...)
    │   │   └── …
    │   ├── _now_iso(...)
    │   │   └── …
    │   ├── _runtime_audit_fields(...)
    │   │   └── …
    │   └── write_lakehouse_table(...)
    │       └── …
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
    ├── enforce_profile_behavior(...)
    │   ├── _accepted_profile_rows(...)
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
    │   ├── profile_dataframe(...)
    │   │   └── …
    │   ├── read_lakehouse_table(...)
    │   │   └── …
    │   └── write_lakehouse_table(...)
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
    ├── stop_if_failed(...)
    │   └── SchemaDriftError(...)
    ├── validate_schema(...)
    │   ├── _actual_schema(...)
    │   │   └── …
    │   └── _normalize_datatype(...)
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

??? info "Internal helpers used: 18"

    This callable uses 18 internal helpers for audit timestamp, metadata loading, rule parsing, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/metadata.py#L149-L222"><code>_build_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/config.py#L70-L76"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/config.py#L62-L67"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/pipeline.py#L50-L61"><code>_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/config.py#L27-L59"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/pipeline.py#L259-L289"><code>_build_guardrail_evidence_definitions</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/fabric_input_output.py#L155-L168"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/pipeline.py#L247-L248"><code>_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/pipeline.py#L251-L252"><code>_table_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/pipeline.py#L509-L556"><code>_write_guardrail_result_row</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/config.py#L645-L685"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/fabric_input_output.py#L108-L119"><code>_normalize_schema_name</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/config.py#L688-L727"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/metadata.py#L103-L115"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/pipeline.py#L255-L256"><code>_guardrail_can_continue</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/pipeline.py#L20-L21"><code>_now_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/metadata.py#L122-L146"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/metadata.py#L118-L119"><code>_safe_str</code></a>
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
- Source line: `292`
- Inbound references count: 0
- Outbound references count: 12
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
- `fabricops_kit.pipeline._write_guardrail_result_row`
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/pipeline.py#L292-L506">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c24f473b71c0f84854756792a922952af3d534a7/src/fabricops_kit/pipeline.py#L292-L506</a>
- Start line: `292`
- End line: `506`
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

- Internal helper count: 18
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
