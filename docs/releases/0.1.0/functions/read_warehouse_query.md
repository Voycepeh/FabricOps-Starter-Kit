# `read_warehouse_query`

This page documents `read_warehouse_query` as released in version `0.1.0`.

Release version: `0.1.0`

<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>

[Current function page](../../../api/reference/read_warehouse_query.md) · [Release function index](index.md)

Read warehouse rows with SQL pushdown.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_warehouse_query.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/10f60521772adabe0fb92be4a01405555d34d586/src/fabricops_kit/io/read_warehouse_query.py#L15-L74">View on GitHub</a>
</div>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_warehouse_query(
    query: str,
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
| `query` | `str` | Yes | SQL ``SELECT`` statement, or a CTE beginning with ``WITH`` and ending in a ``SELECT``, to execute through the Fabric warehouse connector. |
| `target` | `str` | No | Logical warehouse target from ``00_env_config``. |
| `spark_session` | `object, optional` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Fabric Warehouse Spark connector reader options. Required Fabric connector options are always set from ``00_env_config``. |

## Returns

pyspark.sql.DataFrame
    Spark DataFrame returned by the SQL serving engine.

## Raises / Errors

Not documented yet

<details>
<summary>Maintainer architecture details</summary>

- Downstream callables: 12
- Frozen source ref: `10f60521772adabe0fb92be4a01405555d34d586`

</details>
