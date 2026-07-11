# `profile_dataframe`

This page documents `profile_dataframe` as released in version `0.1.0`.

Release version: `0.1.0`

<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>

[Current function page](../../../api/reference/profile_dataframe.md) · [Release function index](index.md)

Build canonical DQ-ready profiling rows from a Spark DataFrame.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_dataframe.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/10f60521772adabe0fb92be4a01405555d34d586/src/fabricops_kit/pipeline/profile_dataframe.py#L10-L65">View on GitHub</a>
</div>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def profile_dataframe(
    df,
    table_name: str,
    exclude_columns=None,
    run_timestamp_timezone: str | None=None,
    config: Any=None,
    include_distributions: bool=False,
    distribution_columns: list[str] | set[str] | tuple[str, ...] | None=None,
    distribution_bin_edges: dict[str, list[float]] | None=None,
    categorical_categories: dict[str, list[str]] | None=None,
    categorical_top_n: int=20,
):
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `Any` | Yes | Spark DataFrame to profile. |
| `table_name` | `str` | Yes | Logical table name written into each profile row. |
| `exclude_columns` | `list[str] or set[str], optional` | No | Additional columns to skip, on top of standard technical columns. |
| `run_timestamp_timezone` | `str \| None` | No | Explicit IANA time zone used for profile evidence timestamps. |
| `config` | `Any` | No | Framework-like configuration carrying audit settings. |
| `include_distributions` | `bool` | No | Whether to include distribution metadata. |
| `distribution_columns` | `list[str] \| set[str] \| tuple[str, ...] \| None` | No | Columns to profile with distributions. |
| `distribution_bin_edges` | `dict[str, list[float]] \| None` | No | Explicit numeric bin edges by column. |
| `categorical_categories` | `dict[str, list[str]] \| None` | No | Explicit categorical values by column. |
| `categorical_top_n` | `int` | No | Maximum categorical values to include when inferred. |

## Returns

pyspark.sql.DataFrame
    Metadata-compatible profile DataFrame.

## Raises / Errors

Not documented yet

<details>
<summary>Maintainer architecture details</summary>

- Downstream callables: 12
- Frozen source ref: `10f60521772adabe0fb92be4a01405555d34d586`

</details>
