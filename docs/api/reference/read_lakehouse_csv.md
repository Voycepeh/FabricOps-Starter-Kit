# read_lakehouse_csv

??? info "Downstream callables: 14"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><span class="reference-call-tree-source">[io/read_lakehouse_csv.py]</span> <code>read_lakehouse_csv(...)</code> <span class="reference-call-tree-type">[public callable]</span></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L116-L123"><span class="reference-call-tree-source">[io/shared.py]</span> <code>get_spark_session(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L221-L226"><span class="reference-call-tree-source">[io/shared.py]</span> <code>read_csv_path(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L139-L143"><span class="reference-call-tree-source">[io/shared.py]</span> <code>resolve_configured_file_path(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L173-L176"><span class="reference-call-tree-source">[io/shared.py]</span> <code>resolve_lakehouse_file_location(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L75-L82"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_validate_relative_path(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L179-L182"><span class="reference-call-tree-source">[io/shared.py]</span> <code>resolve_lakehouse_file_path(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L27-L29"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_join_lakehouse_area_path(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L126-L136"><span class="reference-call-tree-source">[io/shared.py]</span> <code>resolve_target_store(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L595-L634"><span class="reference-call-tree-source">[config/shared.py]</span> <code>get_store(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L547-L587"><span class="reference-call-tree-source">[config/shared.py]</span> <code>_normalize_path_config(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L88-L108"><span class="reference-call-tree-source">[config/shared.py]</span> <code>resolve_fabric_context(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L26-L83"><span class="reference-call-tree-source">[config/shared.py]</span> <code>get_default_fabric_context(...)</code> <span class="reference-call-tree-type">[shared helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L63-L66"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_validate_lakehouse_store(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L69-L72"><span class="reference-call-tree-source">[io/shared.py]</span> <code>_validate_warehouse_store(...)</code> <span class="reference-call-tree-type">[private helper]</span></a></div>
    </div>

Read a CSV file from a configured Fabric-resolved path.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_csv.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_csv.py#L10-L35">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage guidance

### Use when

- Use for file-based source ingestion when the source is CSV and should be resolved through configured Fabric targets.

### Do not use when

- Do not use for Delta tables, Parquet files, Excel files, or warehouse SQL tables.

### Additional context

Reads a CSV file from the configured file path resolved by the Fabric resolver and returns it as a Spark DataFrame.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_csv(
    relative_path: str,
    target: str='source',
    spark_session=None,
    header: bool=True,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_lakehouse_csv(relative_path="raw/orders/orders.csv", header=True, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `relative_path` | `str` | Yes | CSV file or folder path resolved by the Fabric resolver. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `header` | `bool` | No | Whether the first row contains column names. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Spark CSV reader options. |

## Returns

Spark DataFrame loaded from the Fabric-resolved CSV path.

### Return interpretation

The returned DataFrame reflects Spark CSV parsing options; inspect schema and sample rows before profiling or writing.

## Raises / Errors

Raises ValueError for invalid file paths and configuration/Spark errors when the file cannot be read.

### Common failure causes

- The file path is wrong or outside the configured Fabric target.
- CSV options do not match the file shape.
- Spark cannot access the file.
- The selected environment is missing the source lakehouse target.

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Source data</span><span class="glossary-chip-definition">Input data read from configured upstream files, tables, Lakehouses, or Warehouses before transformation.</span> <a href="../../../reference/glossary/#source-data">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Notebook template</span><span class="glossary-chip-definition">Reusable starter notebook workflow that shows how to run a FabricOps phase.</span> <a href="../../../reference/glossary/#notebook-template">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
