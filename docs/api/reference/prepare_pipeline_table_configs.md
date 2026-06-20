# prepare_pipeline_table_configs

Prepare source or target table configs for 02_pipeline.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Module: <code>pipeline</code></span>
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

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

??? info "Uses 4 internal helper functions"

    <div class="reference-call-tree" role="tree">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>prepare_pipeline_table_configs(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline.py#L538-L548"><code>_add_audit_columns(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L207-L213"><code>_current_audit_timestamp(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">            └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone(...)</code></a></div>
    </div>

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
