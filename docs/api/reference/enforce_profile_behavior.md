# enforce_profile_behavior

Enforce append, overwrite, or skip profile behavior against accepted catalogue profile evidence.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/guardrails.py:639`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L639-L832">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use this when promoting or running a pipeline that should follow a previously approved loading pattern. It is especially useful when an overwrite could remove existing history, or when an append-only table suddenly behaves like a full refresh.

**Do not use when:**

- Do not use for simple schema validation or DQ-rule enforcement; use validate_schema or enforce_dq_rules for those checks.

**Additional context:**

This function protects against accidental changes in how a table is loaded. For example, it can stop a pipeline from overwriting a dataset that was previously approved as append-only.

It compares the current load behavior with the previously accepted catalogue profile. If the current behavior no longer matches the approved baseline, the function returns a failed guardrail result so the pipeline can stop before writing data.

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
    load_behavior: str,
    watermark_column: str | None=None,
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None,
    exclude_run_id: str | None=None,
    config=None,
    env: str | None=None,
    catalogue_df=None,
    current_profile=None,
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
    load_behavior="append",
    watermark_column="updated_at",
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
| `load_behavior` | `str` | Yes | Current load behavior to compare with the accepted baseline, commonly append, overwrite, or skip. |
| `watermark_column` | `str \| None` | No | Optional column used to compare append watermark movement when available. |
| `exclude_columns` | `list[str] \| set[str] \| tuple[str, ...] \| None` | No | Optional columns to ignore while comparing profile fields. |
| `exclude_run_id` | `str \| None` | No | Optional run id to exclude when selecting the accepted baseline evidence. |
| `config` | `object, str` | No | Metadata route from ``00_env_config`` used to read the catalogue table via ``read_lakehouse_table`` when ``catalogue_df`` is not supplied. |
| `env` | `str \| None` | No | Not documented yet |
| `catalogue_df` | `DataFrame or iterable of mappings` | No | Preloaded ``METADATA_DATA_CATALOGUE`` evidence. When provided, no metadata read is performed. |
| `current_profile` | `DataFrame or iterable of mappings` | No | Current profile evidence that has already been computed for this table. When supplied, this function reuses it instead of profiling ``dataframe`` again. |

## Returns

Guardrail result dictionary with status, can_continue, message, current profile, baseline details, and profile behavior checks.

### Return interpretation

If can_continue is true, the current load behavior matches the accepted baseline and the pipeline can continue. If can_continue is false, review whether the behavior change is intentional before writing the table. If intentional, update or reapprove the catalogue profile evidence. If not intentional, fix the pipeline configuration.

## Raises / Errors

Raises Spark or metadata-read errors when baseline profile evidence cannot be loaded or compared.

### Common failure causes

- Accepted profile evidence has not been created or approved yet.
- The current load behavior does not match the accepted baseline.
- The configured dataset or table name does not match catalogue evidence.
- The configured stage does not match the accepted evidence.
- The metadata lakehouse or catalogue profile table cannot be read.
- The accepted evidence is missing required behavior fields.
- The current behavior value is invalid or unsupported.
- The accepted evidence is stale or incomplete.

## Relationships

### Used by

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Calls

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.guardrails._catalogue_value`
- `fabricops_kit.guardrails._guardrail_exclude_columns`
- `fabricops_kit.guardrails._is_greater_than`
- `fabricops_kit.guardrails._is_less_than`
- `fabricops_kit.guardrails._is_missing_table_error`
- `fabricops_kit.guardrails._latest_catalogue_behavior_profile_row`
- `fabricops_kit.guardrails._profile_row_count`
- `fabricops_kit.guardrails._profile_watermark_bounds`
- `fabricops_kit.guardrails._string_value`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`

**Side effects:**

Reads baseline profile metadata and computes current profile evidence; it does not write target data.

**Notes:**

This guardrail uses existing profile evidence: row count plus the configured
watermark column's ``min_value`` and ``max_value``. Schema and DQ checks are
enforced by their own guardrails.

</details>

??? info "Call flow"

    ```text
    enforce_profile_behavior(...)
    ├── _catalogue_value(...)
    ├── _guardrail_exclude_columns(...)
    ├── _is_greater_than(...)
    │   └── _comparable_value(...)
    ├── _is_less_than(...)
    │   └── _comparable_value(...)
    ├── _is_missing_table_error(...)
    ├── _latest_catalogue_behavior_profile_row(...)
    │   ├── _catalogue_value(...)
    │   ├── _is_missing_table_error(...)
    │   ├── _row_to_dict(...)
    │   └── _string_value(...)
    ├── _profile_row_count(...)
    │   └── _normalize_profile(...)
    │       └── _normalize_profile(...) (recursive)
    ├── _profile_watermark_bounds(...)
    │   ├── _normalize_profile(...)
    │   │   └── _normalize_profile(...) (recursive)
    │   └── _string_value(...)
    ├── _string_value(...)
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
    └── read_lakehouse_table(...)
        ├── _get_spark(...)
        ├── _get_store(...)
        └── _normalize_table_name(...)
    ```

??? info "Internal helpers used: 12"

    This callable uses 12 internal helpers for metadata loading, rule parsing, profile comparison, and column handling.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Metadata loading</h4>
        <p>Load and identify the metadata or table context needed by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L834-L837"><code>_is_missing_table_error</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Rule parsing</h4>
        <p>Normalize stored or user-provided values before applying rules.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L201-L269"><code>_normalize_profile</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Profile comparison</h4>
        <p>Compare current evidence with accepted profile values and behavior baselines.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L467-L478"><code>_catalogue_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L485-L494"><code>_comparable_value</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L507-L514"><code>_is_greater_than</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L497-L504"><code>_is_less_than</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L527-L636"><code>_latest_catalogue_behavior_profile_row</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L294-L306"><code>_profile_row_count</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L517-L524"><code>_profile_watermark_bounds</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L272-L279"><code>_row_to_dict</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L481-L482"><code>_string_value</code></a>
        </div>
      </section>
      <section class="reference-helper-group">
        <h4>Column handling</h4>
        <p>Select, exclude, and normalize column names used by the callable.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L282-L286"><code>_guardrail_exclude_columns</code></a>
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
- Source line: `639`
- Inbound references count: 1
- Outbound references count: 11
- Used in templates: 02_pipeline
- Glossary terms: profile behavior, accepted catalogue profile evidence, baseline profile, stage, profile behavior check, guardrail, can_continue, append, overwrite, skip, metadata lakehouse

### AI implementation contract

- **required_context:** Requires profile metadata routed through the configured 00_env_config metadata target and a valid source/target stage.
- **inputs:** - `spark`: Spark session used to read accepted profile evidence from the configured metadata target.
- `dataframe`: Current source or target DataFrame being checked.
- `metadata_table`: Metadata table that stores accepted catalogue profile evidence.
- `dataset_name`: Dataset name used to find matching catalogue evidence.
- `table_name`: Table name used to find matching catalogue evidence.
- `stage`: The part of the pipeline being checked, such as source or target.
- `run_id`: Current pipeline run identifier recorded in the generated profile evidence.
- `load_behavior`: Current load behavior to compare with the accepted baseline, commonly append, overwrite, or skip.
- `watermark_column`: Optional column used to compare append watermark movement when available.
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
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>
- `fabricops_kit.guardrails._catalogue_value`
- `fabricops_kit.guardrails._guardrail_exclude_columns`
- `fabricops_kit.guardrails._is_greater_than`
- `fabricops_kit.guardrails._is_less_than`
- `fabricops_kit.guardrails._is_missing_table_error`
- `fabricops_kit.guardrails._latest_catalogue_behavior_profile_row`
- `fabricops_kit.guardrails._profile_row_count`
- `fabricops_kit.guardrails._profile_watermark_bounds`
- `fabricops_kit.guardrails._string_value`

### Raw source metadata

- Source file path: `src/fabricops_kit/guardrails.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L639-L832">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b2463f3ad64a5b0679b3763509f3526351aa247c/src/fabricops_kit/guardrails.py#L639-L832</a>
- Start line: `639`
- End line: `832`
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
    load_behavior: str,
    watermark_column: str | None=None,
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None=None,
    exclude_run_id: str | None=None,
    config=None,
    env: str | None=None,
    catalogue_df=None,
    current_profile=None,
) -> dict:
```

### Internal relationship graph

### Public related functions

- <a href="../profile_dataframe/"><code>fabricops_kit.data_profiling.profile_dataframe</code></a>
- <a href="../validate_schema/"><code>fabricops_kit.guardrails.validate_schema</code></a>
- <a href="../enforce_freshness/"><code>fabricops_kit.guardrails.enforce_freshness</code></a>
- <a href="../stop_if_failed/"><code>fabricops_kit.guardrails.stop_if_failed</code></a>

### Internal implementation summary

- Internal helper count: 12
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

<details class="reference-glossary-details">
<summary>Glossary terms</summary>

- **Profile behavior:** The expected way a table is loaded.
- **Accepted catalogue profile evidence:** The approved profile record that FabricOps treats as the trusted baseline for a table.
- **Baseline profile:** The previous approved profile used as the comparison point.
- **Stage:** The part of the pipeline being checked, such as source or target.
- **Profile behavior check:** A check that confirms the current table load pattern still matches the approved pattern.
- **Guardrail:** A check that tells the notebook whether it is safe to continue.
- **can_continue:** A returned true/false value that tells downstream code whether the pipeline should keep running.
- **Append:** Add new rows without replacing existing rows.
- **Overwrite:** Replace the existing table contents with the current output.
- **Skip:** Do not run that behavior check or write step for the table.
- **Metadata lakehouse:** The configured Fabric lakehouse where FabricOps stores governance and runtime metadata.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

</details>

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
- [Governance Review](../../how-fabricops-works/governance-review.md)
