# read_lakehouse_excel

??? info "Downstream callables: 15"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><span class="reference-call-tree-source">[io/read_lakehouse_excel.py]</span> <span class="reference-call-tree-type">[public callable]</span> <code>read_lakehouse_excel(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L116-L123" class="reference-call-tree-callable"><code>get_spark_session(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L302-L312" class="reference-call-tree-callable"><code>read_excel_file(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L22-L24" class="reference-call-tree-callable"><code>_load_pandas(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L139-L143" class="reference-call-tree-callable"><code>resolve_configured_file_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L173-L176" class="reference-call-tree-callable"><code>resolve_lakehouse_file_location(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L75-L82" class="reference-call-tree-callable"><code>_validate_relative_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │   └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L179-L182" class="reference-call-tree-callable"><code>resolve_lakehouse_file_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    │       └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L27-L29" class="reference-call-tree-callable"><code>_join_lakehouse_area_path(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L126-L136" class="reference-call-tree-callable"><code>resolve_target_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L595-L634" class="reference-call-tree-callable"><code>get_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L547-L587" class="reference-call-tree-callable"><code>_normalize_path_config(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L88-L108" class="reference-call-tree-callable"><code>resolve_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        │   └── </span><span class="reference-call-tree-source">[config/shared.py]</span> <span class="reference-call-tree-type">[shared helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/shared.py#L26-L83" class="reference-call-tree-callable"><code>get_default_fabric_context(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        ├── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L63-L66" class="reference-call-tree-callable"><code>_validate_lakehouse_store(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">        └── </span><span class="reference-call-tree-source">[io/shared.py]</span> <span class="reference-call-tree-type">[private helper]</span> <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/shared.py#L69-L72" class="reference-call-tree-callable"><code>_validate_warehouse_store(...)</code></a></div>
    </div>

Read an Excel file from a configured Fabric-resolved path.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_excel.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_lakehouse_excel.py#L10-L35">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage guidance

### Use when

- Use when source data arrives as an Excel workbook and should still follow configured Fabric lakehouse routing.

### Do not use when

- Do not use for Delta tables, CSV files, Parquet files, or warehouse SQL tables.

### Additional context

Reads an Excel file from a configured lakehouse Files path and converts it into a Spark DataFrame for notebook processing.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_excel(
    relative_path: str,
    target: str='source',
    sheet_name=0,
    spark_session=None,
    context: dict[str, Any] | None=None,
    **read_excel_kwargs,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
mapping_df = read_lakehouse_excel(relative_path="reference/faculty_mapping.xlsx", sheet_name=0, spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `relative_path` | `str` | Yes | Excel file path resolved by the Fabric resolver. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `sheet_name` | `str or int, default=0` | No | Worksheet name or index to read. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **read_excel_kwargs Additional keyword arguments passed to ``pandas.read_excel``. |

## Returns

Spark DataFrame converted from the selected Excel worksheet.

### Return interpretation

The returned DataFrame depends on workbook sheet and parsing options; confirm headers and types before using it as pipeline input.

## Raises / Errors

Raises ValueError for invalid or non-Excel paths and Fabric/Spark/pandas errors when the file cannot be read.

### Common failure causes

- The workbook path or sheet name is incorrect.
- Excel parsing dependencies are unavailable.
- The workbook layout does not match expected headers.
- The configured lakehouse target cannot be read.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
