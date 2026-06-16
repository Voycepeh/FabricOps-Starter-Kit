# enforce_profile_behavior

Enforce static, changing, or skipped profile behavior against accepted catalogue profile evidence.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/guardrails.py:714`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L714-L936">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use this when promoting or running a pipeline that should follow a previously approved profile behavior pattern. It is especially useful when full-table static data changes unexpectedly or when a previous watermark group changes or disappears.

**Do not use when:**

- Do not use for simple schema validation or DQ-rule enforcement; use validate_schema or enforce_dq_rules for those checks.

**Additional context:**

This function protects against silent data behavior changes. It compares current static_data or changing_data profile evidence with previous accepted catalogue evidence. If the current profile no longer matches the approved baseline, the function returns a failed guardrail result so the pipeline can stop before writing data.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def enforce_profile_behavior(
    spark,
    dataframe,
    metadata_table: str,
    dataset_name: str,
    table_name: str,
    stage: str,
    run_id: str,
    profile_mode: str | None=None,
    watermark_column: str | None=None,
    severity: str='blocking',
    rule_key: str='profile_behavior_default',
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None,
    exclude_run_id: str | None=None,
    config=None,
    env: str | None=None,
    catalogue_df=None,
    current_profile=None,
    write_results: bool=True,
    rules_table: str='METADATA_GUARDRAIL_RULES',
    rules_df=None,
) -> dict:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
stability_result = enforce_profile_behavior(
    spark=spark,
    dataframe=df,
    metadata_table="METADATA_DATA_CATALOGUE",
    dataset_name="sales_orders",
    table_name="orders_raw",
    stage="target",
    run_id=run_id,
    profile_mode="changing_data",
    watermark_column="business_date",
)
stop_if_failed(stability_result)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `spark` | `Any` | Yes | Spark session used to read accepted profile evidence from the configured metadata target. |
| `dataframe` | `Any` | Yes | Current source or target DataFrame being checked. |
| `metadata_table` | `str` | Yes | Metadata table that stores accepted catalogue profile evidence. |
| `dataset_name` | `str` | Yes | Dataset name used to find matching catalogue evidence. |
| `table_name` | `str` | Yes | Table name used to find matching catalogue evidence. |
| `stage` | `str` | Yes | The part of the pipeline being checked, such as source or target. |
| `run_id` | `str` | Yes | Current pipeline run identifier recorded in the generated profile evidence. |
| `profile_mode` | `str \| None` | No | Profile behavior mode to evaluate: static_data, changing_data, or skip. |
| `watermark_column` | `str \| None` | No | Column used to group changing_data profile evidence when configured. |
| `severity` | `str` | No | Blocking failures stop continuation; warning failures report but allow continuation. |
| `rule_key` | `str` | No | Rule identifier written to guardrail result evidence when no approved rule row supplies one. |
| `exclude_columns` | `list[str] \| set[str] \| tuple[str, ...] \| None` | No | Optional columns to ignore while comparing profile fields. |
| `exclude_run_id` | `str \| None` | No | Optional run id to exclude when selecting the accepted baseline evidence. |
| `config` | `object` | No | Runtime configuration from ``00_env_config`` used to read metadata and write result evidence when paired with ``env``. |
| `env` | `str \| None` | No | Environment key used with ``config`` for configured metadata routing. |
| `catalogue_df` | `DataFrame or iterable of mappings` | No | Preloaded ``METADATA_DATA_CATALOGUE`` evidence. |
| `current_profile` | `DataFrame or iterable of mappings` | No | Current profile evidence for static mode. |
| `write_results` | `bool` | No | Whether to append runtime outcome rows to ``METADATA_GUARDRAIL_RESULTS`` when ``config`` and ``env`` are supplied. |
| `rules_table` | `str` | No | Metadata table used to load approved profile behavior rules when ``rules_df`` is not supplied. |
| `rules_df` | `DataFrame or iterable of mappings` | No | Preloaded guardrail rules. When supplied, no rules-table read is performed. |

## Returns

Guardrail result dictionary with status, can_continue, message, current profile, baseline details, and profile behavior checks.

### Return interpretation

If can_continue is true, the current profile behavior matches the accepted baseline and the pipeline can continue. If can_continue is false, review whether the behavior change is intentional before writing the table. If intentional, review or supersede the relevant guardrail rule in governance. If not intentional, fix the source data or pipeline configuration.

## Raises / Errors

Raises Spark or metadata-read errors when baseline profile evidence cannot be loaded or compared.

### Common failure causes

- Accepted profile evidence has not been created or approved yet.
- The current profile behavior does not match the accepted baseline.
- The configured dataset or table name does not match catalogue evidence.
- The configured stage does not match the accepted evidence.
- The metadata lakehouse or catalogue profile table cannot be read.
- The accepted evidence is missing required profile behavior fields.
- The current profile_mode value is invalid or unsupported.
- The accepted evidence is stale or incomplete.

## Relationships

### Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Calls

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.guardrails._accepted_profile_rows`
- `fabricops_kit.guardrails._apply_bypass_post_review_warning`
- `fabricops_kit.guardrails._catalogue_value`
- `fabricops_kit.guardrails._guardrail_exclude_columns`
- `fabricops_kit.guardrails._is_missing_table_error`
- `fabricops_kit.guardrails._json_dumps_stable`
- `fabricops_kit.guardrails._profile_hash`
- `fabricops_kit.guardrails._profile_payload_from_profile`
- `fabricops_kit.guardrails._select_profile_behavior_rule`
- `fabricops_kit.guardrails._string_value`
- `fabricops_kit.metadata._write_guardrail_result_row`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`

**Side effects:**

Reads baseline profile metadata and computes current profile evidence; it does not write target data.

**Notes:**

Baselines are never reset here. Current profile evidence is compared to the
previous accepted or passed catalogue evidence. Intentional blocked changes
should be reviewed in governance or handled by superseding/resetting the
relevant guardrail rule.

</details>

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in Implementation details.

    ```text
    enforce_profile_behavior(...)
    ├── _accepted_profile_rows(...)
    │   ├── _catalogue_value(...)
    │   ├── _row_to_dict(...)
    │   └── _string_value(...)
    ├── _apply_bypass_post_review_warning(...)
    │   └── _rule_review_status(...)
    │       └── …
    ├── _catalogue_value(...)
    ├── _configured_lakehouse_schema(...)
    │   ├── _get_store(...)
    │   │   └── …
    │   └── _normalize_schema_name(...)
    ├── _guardrail_exclude_columns(...)
    ├── _is_missing_table_error(...)
    ├── _json_dumps_stable(...)
    ├── _profile_hash(...)
    │   └── _json_dumps_stable(...)
    ├── _profile_payload_from_profile(...)
    │   ├── _normalize_profile(...)
    │   │   └── …
    │   ├── _profile_row_count(...)
    │   │   └── …
    │   ├── _schema_signature(...)
    │   │   └── …
    │   └── _string_value(...)
    ├── _select_profile_behavior_rule(...)
    │   ├── _catalogue_value(...)
    │   ├── _is_active_guardrail_rule(...)
    │   │   └── …
    │   ├── _row_to_dict(...)
    │   └── _string_value(...)
    ├── _string_value(...)
    ├── _write_guardrail_result_row(...)
    │   ├── _build_runtime_audit_fields(...)
    │   │   └── …
    │   ├── _configured_lakehouse_schema(...)
    │   │   └── …
    │   ├── _now_utc_iso(...)
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
    └── read_lakehouse_table(...)
        ├── _get_spark(...)
        ├── _get_store(...)
        │   └── …
        ├── _normalize_table_name(...)
        └── _resolve_lakehouse_table_path(...)
            └── …
    ```

??? info "Internal helpers used: 28"

    This callable uses 28 internal helpers for audit timestamp, metadata loading, rule parsing, profile comparison, column handling, rule evaluation, and other.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/metadata.py#L200-L273"><code>_build_runtime_audit_fields</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/config.py#L70-L76"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/config.py#L62-L67"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/config.py#L27-L59"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L938-L941"><code>_is_missing_table_error</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L204-L205"><code>_json_dumps_stable</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L217-L238"><code>_profile_payload_from_profile</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/metadata.py#L89-L136"><code>_write_guardrail_result_row</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L136-L182"><code>_normalize_datatype</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/config.py#L661-L701"><code>_normalize_path_config</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L397-L465"><code>_normalize_profile</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Profile comparison</h4>
        <p>Compare current evidence with accepted profile values and behavior baselines.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L664-L675"><code>_catalogue_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L490-L502"><code>_profile_row_count</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L468-L475"><code>_row_to_dict</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L678-L679"><code>_string_value</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Column handling</h4>
        <p>Select, exclude, and normalize column names used by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L478-L482"><code>_guardrail_exclude_columns</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule evaluation</h4>
        <p>Convert configured rules into executable checks and evaluation results.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L36-L39"><code>_is_active_guardrail_rule</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L32-L33"><code>_rule_review_status</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L242-L267"><code>_select_profile_behavior_rule</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Other</h4>
        <p>Support lower-level implementation details that do not fit the main helper areas.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L269-L298"><code>_accepted_profile_rows</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L185-L200"><code>_actual_schema</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L78-L85"><code>_apply_bypass_post_review_warning</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/metadata.py#L154-L166"><code>_context_get</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/metadata.py#L64-L65"><code>_now_utc_iso</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L208-L209"><code>_profile_hash</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/metadata.py#L173-L197"><code>_runtime_context</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/metadata.py#L169-L170"><code>_safe_str</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L212-L214"><code>_schema_signature</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.guardrails.enforce_profile_behavior`
- Short name: `enforce_profile_behavior`
- Module: `guardrails`
- Classification: Callable
- Related module: `guardrails`
- Source file path: `src/fabricops_kit/guardrails.py`
- Source line: `714`
- Inbound references count: 1
- Outbound references count: 14
- Used in templates: 02_pipeline
- Glossary terms: profile behavior, accepted catalogue profile evidence, baseline profile, stage, profile behavior check, guardrail, can_continue, static_data, changing_data, skip, metadata lakehouse

### AI implementation contract

- **required_context:** Requires profile metadata routed through the configured 00_env_config metadata target and a valid source/target stage.
- **inputs:** - `spark`: Spark session used to read accepted profile evidence from the configured metadata target.
- `dataframe`: Current source or target DataFrame being checked.
- `metadata_table`: Metadata table that stores accepted catalogue profile evidence.
- `dataset_name`: Dataset name used to find matching catalogue evidence.
- `table_name`: Table name used to find matching catalogue evidence.
- `stage`: The part of the pipeline being checked, such as source or target.
- `run_id`: Current pipeline run identifier recorded in the generated profile evidence.
- `profile_mode`: Profile behavior mode to evaluate: static_data, changing_data, or skip.
- `watermark_column`: Column used to group changing_data profile evidence when configured.
- `exclude_columns`: Optional columns to ignore while comparing profile fields.
- `exclude_run_id`: Optional run id to exclude when selecting the accepted baseline evidence.
- **output:** Guardrail result dictionary with status, can_continue, message, current profile, baseline details, and profile behavior checks.
- **side_effects:** Reads baseline profile metadata and computes current profile evidence; it does not write target data.
- **failure_modes:** Raises Spark or metadata-read errors when baseline profile evidence cannot be loaded or compared.
- **verification:** Verify baseline selection, status, and can_continue before allowing downstream writes or calling stop_if_failed.

### Inbound references

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- `fabricops_kit.fabric_input_output._configured_lakehouse_schema`
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.guardrails._accepted_profile_rows`
- `fabricops_kit.guardrails._apply_bypass_post_review_warning`
- `fabricops_kit.guardrails._catalogue_value`
- `fabricops_kit.guardrails._guardrail_exclude_columns`
- `fabricops_kit.guardrails._is_missing_table_error`
- `fabricops_kit.guardrails._json_dumps_stable`
- `fabricops_kit.guardrails._profile_hash`
- `fabricops_kit.guardrails._profile_payload_from_profile`
- `fabricops_kit.guardrails._select_profile_behavior_rule`
- `fabricops_kit.guardrails._string_value`
- `fabricops_kit.metadata._write_guardrail_result_row`

### Raw source metadata

- Source file path: `src/fabricops_kit/guardrails.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L714-L936">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/de90c79557ef917619c03dd5fb6b9d9c5db78f7a/src/fabricops_kit/guardrails.py#L714-L936</a>
- Start line: `714`
- End line: `936`
- Signature:

```python
def enforce_profile_behavior(
    spark,
    dataframe,
    metadata_table: str,
    dataset_name: str,
    table_name: str,
    stage: str,
    run_id: str,
    profile_mode: str | None=None,
    watermark_column: str | None=None,
    severity: str='blocking',
    rule_key: str='profile_behavior_default',
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None,
    exclude_run_id: str | None=None,
    config=None,
    env: str | None=None,
    catalogue_df=None,
    current_profile=None,
    write_results: bool=True,
    rules_table: str='METADATA_GUARDRAIL_RULES',
    rules_df=None,
) -> dict:
```

### Internal relationship graph

### Public related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.guardrails.validate_schema</code></a>
- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Internal implementation summary

- Internal helper count: 28
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

<details class="reference-glossary-details">
<summary>Glossary terms</summary>

- **Profile behavior:** The expected way a table profile should behave over time.
- **Accepted catalogue profile evidence:** The approved profile record that FabricOps treats as the trusted baseline for a table.
- **Baseline profile:** The previous approved profile used as the comparison point.
- **Stage:** The part of the pipeline being checked, such as source or target.
- **Profile behavior check:** A check that confirms the current table load pattern still matches the approved pattern.
- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **can_continue:** A returned true/false value that tells downstream code whether the pipeline should keep running.
- **static_data:** The full table should keep the same profile unless governance accepts a change.
- **changing_data:** New groups may arrive, but previously seen groups should not change or disappear.
- **Skip:** Do not run that behavior check or write step for the table.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

</details>

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
- [Governance Review](../../how-fabricops-works/governance-review.md)
