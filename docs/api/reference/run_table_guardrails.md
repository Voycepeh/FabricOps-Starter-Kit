# run_table_guardrails

Run profiling, schema, freshness, profile behavior, DQ, and catalogue guardrails for table configs.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:548`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/pipeline.py#L548-L774">View on GitHub</a>
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
- <a href="../enforce_freshness_rule/"><code>fabricops_kit.guardrails.enforce_freshness_rule</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>
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

??? info "Internal helpers used: 33"

    This callable uses 33 internal helpers for audit timestamp, metadata loading, rule parsing, profile comparison, rule evaluation, result summary, fabric or spark access, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/config.py#L66-L72"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/config.py#L58-L63"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/config.py#L23-L55"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/pipeline.py#L515-L545"><code>_build_guardrail_evidence_definitions</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/metadata.py#L80-L81"><code>_build_metadata_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/guardrails.py#L88-L106"><code>_check_schema_rule_runtime</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/guardrails.py#L309-L404"><code>_check_schema_runtime</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/fabric_input_output.py#L155-L168"><code>_configured_lakehouse_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/guardrails.py#L50-L75"><code>_select_table_guardrail_rule</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/metadata.py#L75-L77"><code>_stable_metadata_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/pipeline.py#L503-L504"><code>_table_key</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/pipeline.py#L507-L508"><code>_table_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/guardrails.py#L141-L187"><code>_normalize_datatype</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/config.py#L651-L691"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/fabric_input_output.py#L108-L119"><code>_normalize_schema_name</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/guardrails.py#L42-L47"><code>_parse_rule_parameters</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Profile comparison</h4>
        <p>Compare current evidence with accepted profile values and behavior baselines.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/guardrails.py#L669-L680"><code>_catalogue_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/guardrails.py#L478-L485"><code>_row_to_dict</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/guardrails.py#L683-L684"><code>_string_value</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/guardrails.py#L36-L39"><code>_is_active_guardrail_rule</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/guardrails.py#L32-L33"><code>_rule_review_status</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Result summary</h4>
        <p>Build final statuses, counts, and messages for the caller.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/pipeline.py#L338-L349"><code>_blocking_guardrail_message</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/pipeline.py#L352-L358"><code>_build_guardrail_blocking_message_from_bundle</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Fabric or Spark access</h4>
        <p>Access Fabric or Spark runtime services used by the implementation.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/config.py#L694-L733"><code>_get_store</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/guardrails.py#L190-L205"><code>_actual_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/guardrails.py#L78-L85"><code>_apply_bypass_post_review_warning</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/pipeline.py#L511-L512"><code>_guardrail_can_continue</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/metadata.py#L169-L170"><code>_safe_str</code></a>
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
- Source line: `548`
- Inbound references count: 0
- Outbound references count: 7
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
- <a href="../enforce_freshness_rule/"><code>fabricops_kit.guardrails.enforce_freshness_rule</code></a>
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>
- <a href="../write_catalogue_evidence/"><code>fabricops_kit.pipeline.write_catalogue_evidence</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/pipeline.py#L548-L774">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bdb0b4d9d3c04f7f2dc4b803cc434e4f387f213f/src/fabricops_kit/pipeline.py#L548-L774</a>
- Start line: `548`
- End line: `774`
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

- Internal helper count: 33
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
