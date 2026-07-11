# `read_lakehouse_parquet`

This page documents `read_lakehouse_parquet` as released in version `0.1.0`.

Release version: `0.1.0`

<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>

[Current function page](../../../api/reference/read_lakehouse_parquet.md) · [Release function index](index.md)

Read a Parquet file from a configured Fabric-resolved path through Spark.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_parquet.py:15`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b3d0d480883f2a7acf3e10f08806edfceedcafe8/src/fabricops_kit/io/read_lakehouse_parquet.py#L15-L119">View on GitHub</a>
</div>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def read_lakehouse_parquet(
    relative_path: str,
    target: str='source',
    verbose: bool=True,
    spark_session=None,
    context: dict[str, Any] | None=None,
    **options,
):
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `relative_path` | `str` | Yes | Parquet file path resolved by the Fabric resolver. Root-level files such as ``customers.parquet`` and nested paths such as ``input/customers.parquet`` are supported. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `verbose` | `bool` | No | Whether to print read and timestamp-conversion fallback progress. |
| `spark_session` | `object, optional` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **options Additional Spark Parquet reader options forwarded to every original and timestamp-converted fallback read attempt. |

## Returns

pyspark.sql.DataFrame
    Spark DataFrame loaded from the Parquet path.

## Raises / Errors

Not documented yet

<details>
<summary>Maintainer architecture details</summary>

- Downstream callables: 18
- Frozen source ref: `b3d0d480883f2a7acf3e10f08806edfceedcafe8`

</details>
