# read_warehouse_query

??? info "Downstream callables: 12"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>read_warehouse_query(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L116-L123"><code>get_spark_session(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L290-L293"><code>read_warehouse_synapsesql(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L101-L108"><code>_require_fabric_connector(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L160-L163"><code>resolve_configured_warehouse_query_target(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L126-L136"><code>resolve_target_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L600-L639"><code>get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L557-L597"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L98-L118"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L36-L93"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L63-L66"><code>_validate_lakehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L69-L72"><code>_validate_warehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L206-L213"><code>validate_select_query(...)</code></a></div>
    </div>

Read warehouse rows with SQL pushdown through a configured Fabric warehouse target.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_warehouse_query.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_warehouse_query.py#L10-L46">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

## Usage guidance

### Use when

- Use when warehouse data should be filtered or projected before Spark processing.

### Do not use when

- Do not use for lakehouse Delta tables, lakehouse Files paths, or non-SELECT warehouse mutations.

### Additional context

Encourages warehouse SQL pushdown for filtered or projected reads instead of full table extracts.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_warehouse_query(
    query: str,
    target: str='warehouse',
    spark_session=None,
    context: dict[str, Any] | None=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_warehouse_query("SELECT order_id, status FROM dbo.orders WHERE status = 'OPEN'", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `query` | `str` | Yes | SQL ``SELECT`` statement, or a CTE beginning with ``WITH`` and ending in a ``SELECT``, to execute through the Fabric warehouse connector. |
| `target` | `str` | No | Logical warehouse target from ``00_env_config``. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. |

## Returns

Spark DataFrame returned by the Fabric warehouse connector.

### Return interpretation

The returned DataFrame contains the query result from the warehouse SQL serving engine.

## Raises / Errors

Raises ValueError for blank or non-SELECT SQL and RuntimeError when the Fabric connector is unavailable.

### Common failure causes

- The SQL is blank or not a SELECT/CTE.
- The warehouse target is not configured.
- The Fabric connector is unavailable.
- The caller lacks warehouse read permission.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Source data</span><span class="glossary-chip-definition">Input data read from configured upstream files, tables, Lakehouses, or Warehouses before transformation.</span> <a href="../../../reference/glossary/#source-data">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Notebook template</span><span class="glossary-chip-definition">Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
