# `read_lakehouse_csv`

This page documents `read_lakehouse_csv` as released in version `0.1.0`.

Release version: `0.1.0`

<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>

[Current function page](../../../api/reference/read_lakehouse_csv.md) · [Release function index](index.md)

Read a CSV file from a configured Fabric-resolved path through Spark.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_csv.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bfce157/src/fabricops_kit/io/read_lakehouse_csv.py#L10-L49">View on GitHub</a>
</div>

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

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `relative_path` | `str` | Yes | CSV file or folder path resolved by the Fabric resolver. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `spark_session` | `object, optional` | No | Spark session to use instead of the notebook global ``spark``. |
| `header` | `bool` | No | Whether the first row contains column names. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Spark CSV reader options forwarded to Spark's CSV reader. |

## Returns

pyspark.sql.DataFrame
    Spark DataFrame loaded from the CSV path.

## Raises / Errors

Not documented yet

<details>
<summary>Maintainer architecture details</summary>

- Downstream callables: 15
- Frozen source ref: `bfce157`

</details>
