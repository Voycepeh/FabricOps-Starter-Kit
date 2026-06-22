# read_lakehouse_parquet

??? info "Uses 7 internal helper functions"

    <div class="reference-call-tree" role="tree">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>read_lakehouse_parquet(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L285-L356"><code>read_lakehouse_parquet_core(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L500-L515"><code>_convert_single_parquet_ns_to_us(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L63-L70"><code>_get_spark(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L682-L721"><code>_get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L639-L679"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L227-L248"><code>PathConfig(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L113-L118"><code>_lakehouse_file_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L121-L124"><code>_validate_lakehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io_core.py#L133-L140"><code>_validate_relative_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L141-L161"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L26-L83"><code>get_default_fabric_context(...)</code></a></div>
    </div>

Read a Parquet path from a configured Fabric lakehouse Files path.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Module: <code>fabric_input_output</code></span>
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">No starter notebook usage detected</span>
</p>

**Used in notebooks:** Not currently detected in starter notebooks.

## Usage guidance

### Use when

- Use for file-based source ingestion when the source is Parquet rather than a managed table.

### Do not use when

- Do not use for Delta tables, CSV files, Excel files, or warehouse SQL tables.

### Additional context

Reads a Parquet file or folder from the Files area of a configured Fabric lakehouse into a Spark DataFrame.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_parquet(
    relative_path: str,
    target: str='source',
    verbose: bool=True,
    spark_session=None,
    context: dict[str, Any] | None=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_lakehouse_parquet(relative_path="raw/orders/orders.parquet", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `relative_path` | `str` | Yes | Parquet file path under the lakehouse ``Files`` area. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `verbose` | `bool` | No | Whether to print read and timestamp-conversion fallback progress. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. |

## Returns

Spark DataFrame loaded from the original Parquet path or timestamp-converted fallback path.

### Return interpretation

The returned DataFrame uses the Parquet schema read by Spark; validate it before downstream profile or guardrail checks.

## Raises / Errors

Raises ValueError for invalid relative paths and Spark/read errors when the Parquet path cannot be loaded.

### Common failure causes

- The Parquet path is missing or misspelled.
- The file is not valid Parquet.
- The configured lakehouse target is unavailable.
- The caller lacks read permission.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Source data</span><span class="glossary-chip-definition">Input data read from configured upstream files, tables, Lakehouses, or Warehouses before transformation.</span> <a href="../../../reference/glossary/#source-data">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Notebook template</span><span class="glossary-chip-definition">Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
