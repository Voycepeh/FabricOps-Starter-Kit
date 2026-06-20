# prepare_pipeline_table_configs

Prepare source or target table configs for 02_pipeline.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline.py:551`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L551-L640">View on GitHub</a>
</div>

## Usage guidance

### Use when

- Use before running table guardrails or writes when notebook-editable table configs need package defaults and derived keys.

### Do not use when

- Do not use for ad hoc reads or writes outside the pipeline table-config pattern.

### Additional context

Normalizes source and target table configuration dictionaries so pipeline guardrail, write, lineage, and evidence helpers receive consistent fields.


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

## Maintainer/developer implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

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

??? info "Maintainer/developer call flow"

    This maintainer/developer view is for source navigation, dependency review, and refactor planning. Internal/private helpers shown here are implementation details, not public API or normal notebook-callable concepts.

    Unique internal/private helpers: 4. Repeated calls may appear in multiple branches.

    <div class="reference-call-tree" role="tree">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>prepare_pipeline_table_configs(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L538-L548"><code>_add_audit_columns(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone(...)</code></a></div>
    </div>

    ### Refactor signals

    These generated hints point maintainers to call-tree shapes worth reviewing; they are not automatic refactor requirements.

    **Helpers appearing in multiple branches**

    - None detected in the reachable package-local call tree.

    **Call chains deeper than 4 levels**

    - None detected.

    **Helpers that only call one package-local helper**

    - `_current_audit_timestamp` only delegates to `_get_audit_timezone`.
    - `_get_audit_timezone` only delegates to `_validate_audit_timezone`.
    - `_add_audit_columns` only delegates to `_current_audit_timestamp`.

    **Helpers grouped into possibly wrong areas**

    - None detected from helper names, doc summaries, and module placement.

This callable uses 4 internal helpers for audit timestamp.

<div class="reference-helper-groups">
  <section class="reference-helper-group">
    <h4>Audit timestamp</h4>
    <p>Resolve and stamp audit time consistently.</p>
    <div class="reference-helper-chip-wrap">
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L538-L548"><code>_add_audit_columns</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone</code></a>
      <a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone</code></a>
    </div>
  </section>
</div>

<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.pipeline.prepare_pipeline_table_configs`
- Short name: `prepare_pipeline_table_configs`
- Module: `pipeline`
- Public surface: Public Starter Kit function
- Classification: Callable
- Related module: `pipeline`
- Source file path: `src/fabricops_kit/pipeline.py`
- Source line: `551`
- Inbound references count: 0
- Outbound references count: 1
- Used in templates: 02_pipeline
- Glossary terms: source data, target table, stage, guardrails

### Implementation contract

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
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L551-L640">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L551-L640</a>
- Start line: `551`
- End line: `640`
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

### Maintainer/developer relationship graph

### Public related functions

- <a href="run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="read_data/"><code>fabricops_kit.fabric_input_output.read_data</code></a>

### Internal implementation summary

- Internal helper count: 4
- Grouped helper summary is rendered in the page-level maintainer/developer implementation details section; helper chips link to source.

</details>

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Source data</span><span class="glossary-chip-definition">Input data read from configured upstream files, tables, Lakehouses, or Warehouses before transformation.</span> <a href="../../../reference/glossary/#source-data">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Target table</span><span class="glossary-chip-definition">A written table produced by a pipeline output.</span> <a href="../../../reference/glossary/#target-table">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Stage</span><span class="glossary-chip-definition">Named part of a pipeline such as source, transformation, or target.</span> <a href="../../../reference/glossary/#stage">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Guardrails</span><span class="glossary-chip-definition">Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</span> <a href="../../../reference/glossary/#guardrails">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
- [Pipeline Execution](../../notebook-templates-implementation-guide/pipeline-execution.md)
