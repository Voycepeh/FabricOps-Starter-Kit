# write_lakehouse_table

??? info "Uses 7 internal helper functions"

    <div class="reference-call-tree" role="tree">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>write_lakehouse_table(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L196-L247"><code>write_lakehouse_table_core(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L682-L721"><code>_get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L639-L679"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L227-L248"><code>PathConfig(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L85-L96"><code>_normalize_schema_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L73-L82"><code>_normalize_table_name(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L99-L104"><code>_normalize_write_mode(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L107-L110"><code>_resolve_lakehouse_table_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L121-L124"><code>_validate_lakehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L26-L83"><code>get_default_fabric_context(...)</code></a></div>
    </div>

Write a Spark DataFrame to a configured Fabric lakehouse Delta table.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Module: <code>fabric_input_output</code></span>
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">example_pipeline_demo</span>
<span class="reference-chip">example_dq_rule_smoke_test</span>
</p>

**Used in notebooks:** `02_pipeline`, `example_pipeline_demo`, `example_dq_rule_smoke_test`

## Usage guidance

### Use when

- Use after transformations and guardrail checks when the destination is a Lakehouse table.

### Do not use when

- Do not use for warehouse publishing or metadata mutation outside configured metadata routing.

### Additional context

Writes a Spark DataFrame to configured Lakehouse Tables storage using explicit Lakehouse routing.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_lakehouse_table(
    df,
    table_name: str,
    target: str='unified',
    schema=None,
    mode='append',
    partition_by=None,
    repartition_by=None,
    options=None,
    verbose=True,
    context=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
write_lakehouse_table(df_orders, "orders_clean", target="unified", schema=UNIFIED_SCHEMA, mode="overwrite")
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to write. |
| `table_name` | `str` | Yes | Lakehouse table name. Pass schemas with ``schema`` rather than as a qualified name. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `schema` | `str or None` | No | Optional schema override for schema-enabled lakehouses. |
| `mode` | `str, default="append"` | No | Spark write mode: ``append``, ``overwrite``, ``errorifexists``, or ``ignore``. |
| `partition_by` | `str or list[str]` | No | Column or columns used to physically partition the Delta table. |
| `repartition_by` | `int, str, list, or tuple` | No | Optional repartitioning before write. |
| `options` | `dict` | No | Additional Spark DataFrameWriter options. |
| `verbose` | `bool, default=True` | No | Whether to print the resolved output path before writing. |
| `context` | `dict[str, Any]` | No | Active Fabric context override. |

## Returns

None; the DataFrame is written to the configured Lakehouse Delta table path.

### Return interpretation

No value is returned; successful completion means the configured Lakehouse write was submitted.

## Raises / Errors

Raises ValueError for unsafe names, invalid write modes, or non-lakehouse targets.

### Common failure causes

- Guardrails were skipped before a target write.
- The target lakehouse is not configured for the environment.
- The write mode is unsupported for the destination.
- The caller lacks write permission or Spark cannot create the table.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Target table</span><span class="glossary-chip-definition">A written table produced by a pipeline output.</span> <a href="../../../reference/glossary/#target-table">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Guardrails</span><span class="glossary-chip-definition">Approved checks that evaluate schema, freshness, profile behavior, or DQ expectations during a pipeline run.</span> <a href="../../../reference/glossary/#guardrails">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
