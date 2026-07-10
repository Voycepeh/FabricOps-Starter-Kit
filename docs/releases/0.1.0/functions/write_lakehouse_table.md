# `write_lakehouse_table`

This page documents `write_lakehouse_table` as released in version `0.1.0`.

Release version: `0.1.0`

<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>

[Current function page](../../../api/reference/write_lakehouse_table.md) · [Release function index](../index.md)

Write a Spark DataFrame to a Fabric lakehouse Delta table.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/write_lakehouse_table.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/0f77d1a/src/fabricops_kit/io/write_lakehouse_table.py#L15-L87">View on GitHub</a>
</div>

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

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to write. |
| `table_name` | `str` | Yes | Lakehouse table name. Pass schemas with ``schema`` rather than as a qualified name. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `schema` | `str or None, default=None` | No | Optional schema override for schema-enabled lakehouses. |
| `mode` | `str, default="append"` | No | Spark write mode: ``append``, ``overwrite``, ``errorifexists``, or ``ignore``. |
| `partition_by` | `str or list[str], optional` | No | Column or columns used to physically partition the Delta table. |
| `repartition_by` | `int, str, list, or tuple, optional` | No | Optional repartitioning before write. |
| `options` | `dict, optional` | No | Additional Spark Delta ``DataFrameWriter`` options forwarded before saving the configured Lakehouse Tables path. |
| `verbose` | `bool, default=True` | No | Whether to print the resolved output path before writing. |
| `context` | `dict[str, Any], optional` | No | Active Fabric context override. |

## Returns

None
    The DataFrame is written to the configured Delta table path.

## Raises / Errors

Not documented yet

<details>
<summary>Maintainer architecture details</summary>

- Downstream callables: 17
- Frozen source ref: `0f77d1a`

</details>
