# read_warehouse_table

## Call-flow summary

- Downstream callables: 15
- Shared helpers: 8
- Private helpers: 7

<a class="reference-source-link" href="../../assets/public-function-call-flows-dashboard.html?function=read_warehouse_table">Open focused call flow in dashboard</a>


Read a table from a configured Fabric warehouse target.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_warehouse_table.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/io/read_warehouse_table.py#L10-L49">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

## Usage notes

These IO helpers exist because Fabric notebooks can only attach to one lakehouse or warehouse at a time. Use them when a notebook needs a supported and repeatable way to read from or write to the configured Fabric store.

They keep IO behavior consistent across Starter Kit notebooks and avoid ad hoc connection logic.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_warehouse_table(
    schema: str,
    table_name: str,
    target: str='warehouse',
    spark_session=None,
    context: dict[str, Any] | None=None,
):
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
df = read_warehouse_table(schema="dbo", table="orders", spark_session=spark)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `schema` | `str` | Yes | Warehouse schema name. |
| `table_name` | `str` | Yes | Warehouse table name. |
| `target` | `str` | No | Logical warehouse target from ``00_env_config``. |
| `spark_session` | `object` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. |

## Returns

Spark DataFrame loaded from the configured warehouse table.

### Return interpretation

The returned DataFrame represents the warehouse read result; confirm filters and row counts before profiling or transformation.

## Raises / Errors

Raises configuration, Spark SQL, or warehouse-read errors when the target/table cannot be resolved/read.

### Common failure causes

- The warehouse target is not configured.
- The table or SQL text is invalid.
- Warehouse connector context is unavailable.
- The caller lacks warehouse read permission.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
