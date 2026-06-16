# prepare_pipeline_table_configs

Prepare source or target table configs for 02_pipeline.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:412`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/pipeline.py#L412-L501">View on GitHub</a>
</div>

<details class="reference-usage-details">
<summary>Usage guidance</summary>

**Use when:**

- Use before running table guardrails or writes when notebook-editable table configs need package defaults and derived keys.

**Do not use when:**

- Do not use for ad hoc reads or writes outside the pipeline table-config pattern.

**Additional context:**

Normalizes source and target table configuration dictionaries so pipeline guardrail, write, lineage, and evidence helpers receive consistent fields.

</details>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def prepare_pipeline_table_configs(
    table_configs: list[dict[str, Any]],
    default_settings: Mapping[str, Any],
    table_role: str,
    run_id: str='',
    pipeline_name: str='',
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
SOURCE_TABLES, SOURCE_CONFIG_BY_KEY = prepare_pipeline_table_configs(SOURCE_TABLES, {}, table_role="source")
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_configs` | `list[dict[str, Any]]` | Yes | User-authored table config dictionaries from ``SOURCE_TABLES`` or ``TARGET_TABLES``. |
| `default_settings` | `Mapping[str, Any]` | Yes | Default guardrails, and for targets write options, merged before each table config. Table-specific values take precedence. |
| `table_role` | `str` | Yes | Role-specific preparation mode. Source mode validates that each config already includes a DataFrame; target mode adds FabricOps audit columns and derives write metadata. |
| `run_id` | `str` | No | Pipeline run identifier used for target audit columns. Required for target role. |
| `pipeline_name` | `str` | No | Pipeline name used for target audit columns. Required for target role. |

## Returns

Enriched table configs and a dictionary keyed by table key.

### Return interpretation

The returned configs are enriched copies keyed for downstream helpers. Confirm each table has the expected stage, key, and write settings.

## Raises / Errors

ValueError
    If ``table_role`` is not ``"source"`` or ``"target"``.

### Common failure causes

- A table config is missing key or table_name fields.
- Stage or write settings are inconsistent.
- Source and target config shapes differ from expected dictionaries.
- Defaults in CONFIG do not match the notebook environment.

## Relationships

### Used by

Not documented yet

### Calls

- `fabricops_kit.pipeline._add_audit_columns`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

- `02_pipeline`

**Side effects:**

Source role validates pre-loaded DataFrames. Target role adds FabricOps audit columns to target DataFrames.

**Notes:**

Source configs derive ``dataset_name`` from ``table_name`` and ``stage`` from
``layer``. Source
DataFrames must be loaded directly in the notebook with the existing
FabricOps read helpers and supplied in each source config as ``df``.

Target configs derive ``dataset_name``, ``stage``, ``target_layer``,
``target_name``, and ``target_kind`` unless overridden, then add standard
FabricOps audit columns.

</details>

??? info "Call flow"

    ```text
    prepare_pipeline_table_configs(...)
    └── _add_audit_columns(...)
        └── _current_audit_timestamp(...)
            └── _get_audit_timezone(...)
                └── _validate_audit_timezone(...)
    ```

??? info "Internal helpers used: 4"

    This callable uses 4 internal helpers for audit timestamp.

    <div class="reference-helper-groups">
      <section class="reference-helper-group">
        <h4>Audit timestamp</h4>
        <p>Resolve and stamp audit time consistently.</p>
        <div class="reference-helper-chip-wrap">
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/pipeline.py#L399-L409"><code>_add_audit_columns</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/config.py#L66-L72"><code>_current_audit_timestamp</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/config.py#L58-L63"><code>_get_audit_timezone</code></a>
          <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/config.py#L23-L55"><code>_validate_audit_timezone</code></a>
        </div>
      </section>
    </div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.prepare_pipeline_table_configs`
- Short name: `prepare_pipeline_table_configs`
- Module: `pipeline`
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `412`
- Inbound references count: 0
- Outbound references count: 1
- Used in templates: 02_pipeline
- Glossary terms: source table, target table, stage, guardrail

### AI implementation contract

- **required_context:** Source DataFrames should be loaded directly in the notebook with existing FabricOps read helpers. Target audit columns require a Spark-compatible DataFrame.
- **inputs:** table_configs, default_settings, table_role, and role-specific context such as run_id/pipeline_name for targets.
- **output:** Enriched table configs and a dictionary keyed by table key.
- **side_effects:** Source role validates pre-loaded DataFrames. Target role adds FabricOps audit columns to target DataFrames.
- **failure_modes:** ValueError
    If ``table_role`` is not ``"source"`` or ``"target"``.
- **verification:** Verify the correct table_role is used and enriched configs are passed to run_table_guardrails before transformation or writes.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.pipeline._add_audit_columns`

### Raw source metadata

- Source file path: `src/fabricops_kit/pipeline.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/pipeline.py#L412-L501">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b6f6908f896cb15a6dbf5d2f1019a02e0a4f3d4b/src/fabricops_kit/pipeline.py#L412-L501</a>
- Start line: `412`
- End line: `501`
- Signature:

```python
def prepare_pipeline_table_configs(
    table_configs: list[dict[str, Any]],
    default_settings: Mapping[str, Any],
    table_role: str,
    run_id: str='',
    pipeline_name: str='',
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
```

### Internal relationship graph

### Public related functions

- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../read_lakehouse_table/"><code>fabricops_kit.fabric_input_output.read_lakehouse_table</code></a>

### Internal implementation summary

- Internal helper count: 4
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- **Source table:** An input table or file read by the pipeline.
- **Target table:** An output table written by the pipeline.
- **Stage:** The part of the pipeline being checked, such as source or target.
- **Guardrail:** A check that tells the notebook whether it is safe to continue.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)
- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
