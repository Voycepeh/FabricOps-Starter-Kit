# read_lakehouse_csv


Read a CSV file from a configured Fabric lakehouse Files path.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Module: <code>io.read_lakehouse_csv</code></span>
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">No starter notebook usage detected</span>
</p>

**Used in notebooks:** Not currently detected in starter notebooks.

## Usage guidance

### Use when

- Use for file-based source ingestion when the source is CSV and should be resolved through configured lakehouse paths.

### Do not use when

- Do not use for Delta tables, Parquet files, Excel files, or warehouse SQL tables.

### Additional context

Reads a CSV file from the Files area of a configured Fabric lakehouse and returns it as a Spark DataFrame.


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
| `relative_path` | `str` | Yes | CSV file or folder path under the lakehouse ``Files`` area. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `header` | `bool` | No | Whether the first row contains column names. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Spark CSV reader options. |

## Returns

Spark DataFrame loaded from the lakehouse Files CSV path.

### Return interpretation

The returned DataFrame reflects Spark CSV parsing options; inspect schema and sample rows before profiling or writing.

## Raises / Errors

Raises ValueError for invalid file paths and configuration/Spark errors when the file cannot be read.

### Common failure causes

- The file path is wrong or outside the configured lakehouse.
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
