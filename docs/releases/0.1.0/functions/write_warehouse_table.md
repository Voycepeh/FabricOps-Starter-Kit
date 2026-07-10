# `write_warehouse_table`

This page documents `write_warehouse_table` as released in version `0.1.0`.

Release version: `0.1.0`

<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>

[Current function page](../../../api/reference/write_warehouse_table.md) · [Release function index](index.md)

Write a Spark DataFrame to a Microsoft Fabric warehouse table.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/write_warehouse_table.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bfce157/src/fabricops_kit/io/write_warehouse_table.py#L10-L78">View on GitHub</a>
</div>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def write_warehouse_table(
    df,
    schema: str,
    table_name: str,
    target: str='warehouse',
    mode: str='append',
    repartition_by=None,
    options: dict[str, Any] | None=None,
    context: dict[str, Any] | None=None,
):
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to publish. |
| `schema` | `str` | Yes | Warehouse schema name. |
| `table_name` | `str` | Yes | Warehouse table name. |
| `target` | `str` | No | Logical warehouse target from ``00_env_config``. |
| `mode` | `str` | No | Spark writer mode supported by the Fabric connector. |
| `repartition_by` | `int, str, list, or tuple, optional` | No | Optional repartitioning before write. This controls Spark write parallelism and does not create a physically partitioned Warehouse table. |
| `options` | `dict[str, Any] \| None` | No | Additional Fabric Warehouse Spark connector writer options. Required Fabric connector options are always set from ``00_env_config``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. |

## Returns

None
    The DataFrame is written through the Fabric warehouse connector.

## Raises / Errors

Not documented yet

<details>
<summary>Maintainer architecture details</summary>

- Downstream callables: 15
- Frozen source ref: `bfce157`

</details>
