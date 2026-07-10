# `read_lakehouse_excel`

This page documents `read_lakehouse_excel` as released in version `0.1.0`.

Release version: `0.1.0`

<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>

[Current function page](../../../api/reference/read_lakehouse_excel.md) · [Release function index](index.md)

Read an Excel workbook from a configured Fabric-resolved path.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/io/read_lakehouse_excel.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/bfce15756427d96277b26f87924380a748007acc/src/fabricops_kit/io/read_lakehouse_excel.py#L10-L52">View on GitHub</a>
</div>

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

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `relative_path` | `str` | Yes | Excel file path resolved by the Fabric resolver. |
| `target` | `str` | No | Logical lakehouse target from ``00_env_config``. |
| `sheet_name` | `str or int, default=0` | No | Worksheet name or index to read. |
| `spark_session` | `object, optional` | No | Spark session to use instead of the notebook global ``spark``. |
| `context` | `dict[str, Any] \| None` | No | Active Fabric context override. **read_excel_kwargs Additional keyword arguments passed to ``pandas.read_excel``. |

## Returns

pyspark.sql.DataFrame
    Spark DataFrame converted from the selected Excel worksheet.

## Raises / Errors

Not documented yet

<details>
<summary>Maintainer architecture details</summary>

- Downstream callables: 16
- Frozen source ref: `bfce15756427d96277b26f87924380a748007acc`

</details>
