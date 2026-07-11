# `read_warehouse_table`

This page documents `read_warehouse_table` as released in version `0.1.0`.

Release version: `0.1.0`

<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>

[Current function page](../../../api/reference/read_warehouse_table.md) · [Release function index](index.md)

Read a full table from a Microsoft Fabric warehouse.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_warehouse_table.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/10f60521772adabe0fb92be4a01405555d34d586/src/fabricops_kit/io/read_warehouse_table.py#L10-L70">View on GitHub</a>
</div>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_warehouse_table(
    schema: str,
    table_name: str,
    target: str='warehouse',
    spark_session=None,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `schema` | `str` | Yes | Warehouse schema name. |
| `table_name` | `str` | Yes | Warehouse table name. |
| `target` | `str` | No | Logical warehouse target from ``00_env_config``. |
| `spark_session` | `object, optional` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Fabric Warehouse Spark connector reader options. Required Fabric connector options are always set from ``00_env_config``. |

## Returns

pyspark.sql.DataFrame
    Spark DataFrame loaded through the Fabric warehouse connector.

## Raises / Errors

Not documented yet

<details>
<summary>Maintainer architecture details</summary>

- Downstream callables: 15
- Frozen source ref: `10f60521772adabe0fb92be4a01405555d34d586`

</details>
