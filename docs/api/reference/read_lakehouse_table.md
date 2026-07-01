# read_lakehouse_table

??? info "Downstream callables: 16"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><span class="reference-call-tree-source">[io/read_lakehouse_table.py]</span> <code>read_lakehouse_table(...)</code> <span class="reference-call-tree-type">[public callable]</span></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L116-L123"><span class="reference-call-tree-source">[io/shared.py]</span> <code>get_spark_session(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L216-L218"><span class="reference-call-tree-source">[io/shared.py]</span> <code>read_delta_path(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L146-L150"><span class="reference-call-tree-source">[io/shared.py]</span> <code>resolve_configured_lakehouse_table(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L166-L170"><span class="reference-call-tree-source">[io/shared.py]</span> <code>resolve_lakehouse_table_location(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L37-L46"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_normalize_table_name(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L85-L87"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_resolve_lakehouse_schema(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L49-L60"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_normalize_schema_name(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L90-L93"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_resolve_lakehouse_table_path(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L27-L29"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_join_lakehouse_area_path(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L126-L136"><span class="reference-call-tree-source">[io/shared.py]</span> <code>resolve_target_store(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L595-L634"><span class="reference-call-tree-source">[config/shared.py]</span> <code>get_store(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L547-L587"><span class="reference-call-tree-source">[config/shared.py]</span> <code>_normalize_path_config(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L88-L108"><span class="reference-call-tree-source">[config/shared.py]</span> <code>resolve_fabric_context(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L26-L83"><span class="reference-call-tree-source">[config/shared.py]</span> <code>get_default_fabric_context(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L63-L66"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_validate_lakehouse_store(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L69-L72"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_validate_warehouse_store(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
    </div>

Read a Delta table from a configured Fabric lakehouse target.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_table.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_table.py#L10-L38">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `02_pipeline`, `99_explore`

## Usage guidance

### Use when

- Use near the start of a notebook when Spark processing needs a full Lakehouse table DataFrame.

### Do not use when

- Do not use for lakehouse Files paths or warehouse SQL serving-engine reads.

### Additional context

Reads a Delta table from configured Lakehouse Tables storage using explicit Lakehouse routing.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_table(
    table_name: str,
    target: str='source',
    schema: str | None=None,
    spark_session=None,
    context: dict[str, Any] | None=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df_orders = read_lakehouse_table("orders", target="source", schema=SOURCE_SCHEMA, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_name` | `str` | Yes | Lakehouse table name. Pass schemas with ``schema`` rather than as a qualified name. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `schema` | `str \| None` | No | Optional schema override for schema-enabled lakehouses. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. |

## Returns

Spark DataFrame loaded from the configured Lakehouse Delta table path.

### Return interpretation

The returned DataFrame represents the resolved Lakehouse table.

## Raises / Errors

Raises ValueError for unsafe names or non-lakehouse targets and RuntimeError when Spark is unavailable.

### Common failure causes

- The target or table name is misspelled.
- The selected environment does not define the requested lakehouse target.
- Spark cannot access the table.
- The caller lacks permission to read the lakehouse.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Source data</span><span class="glossary-chip-definition">Input data read from configured upstream files, tables, Lakehouses, or Warehouses before transformation.</span> <a href="../../../reference/glossary/#source-data">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Metadata lakehouse</span><span class="glossary-chip-definition">Configured Fabric Lakehouse target where FabricOps stores metadata tables.</span> <a href="../../../reference/glossary/#metadata-lakehouse">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
