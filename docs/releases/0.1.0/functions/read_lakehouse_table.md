# `read_lakehouse_table`

This page documents `read_lakehouse_table` as released in version `0.1.0`.

Release version: `0.1.0`

<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>

[Current function page](../../../api/reference/read_lakehouse_table.md) · [Release function index](index.md)

Read a Delta table from a Fabric lakehouse.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_table.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bfce15756427d96277b26f87924380a748007acc/src/fabricops_kit/io/read_lakehouse_table.py#L10-L56">View on GitHub</a>
</div>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_table(
    table_name: str,
    target: str='source',
    schema: str | None=None,
    spark_session=None,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `table_name` | `str` | Yes | Lakehouse table name. Pass schemas with ``schema`` rather than as a qualified name. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `schema` | `str \| None` | No | Optional schema override for schema-enabled lakehouses. |
| `spark_session` | `object, optional` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Spark Delta reader options forwarded to ``DataFrameReader``. |

## Returns

pyspark.sql.DataFrame
    Spark DataFrame loaded from the configured Delta table path.

## Raises / Errors

Not documented yet

<details>
<summary>Maintainer architecture details</summary>

- Downstream callables: 16
- Frozen source ref: `bfce15756427d96277b26f87924380a748007acc`

</details>
