# profile_dataframe

## Call-flow summary

- Downstream callables: 12
- Shared helpers: 7
- Private helpers: 5

<a class="reference-source-link" href="../../assets/public-function-call-flows-dashboard.html?function=profile_dataframe">Open focused call flow in dashboard</a>


Profile a source or target DataFrame for schema, quality, and catalogue evidence.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_dataframe.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_dataframe.py#L10-L65">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `99_explore`

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


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

## Example usage

<div class="reference-example-usage" markdown="1">

```python
profile_rows_df = profile_dataframe(df, table_name="orders", include_distributions=True, distribution_columns=["status"] )
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `Any` | Yes | Spark DataFrame to profile. |
| `table_name` | `str` | Yes | Logical table name written into each profile row. |
| `exclude_columns` | `list[str] or set[str]` | No | Additional columns to skip, on top of standard technical columns. |
| `run_timestamp_timezone` | `str \| None` | No | Explicit IANA time zone used for profile evidence timestamps. |
| `config` | `Any` | No | Framework-like configuration carrying audit settings. |
| `include_distributions` | `bool` | No | Whether to include distribution metadata. |
| `distribution_columns` | `list[str] \| set[str] \| tuple[str, ...] \| None` | No | Columns to profile with distributions. |
| `distribution_bin_edges` | `dict[str, list[float]] \| None` | No | Explicit numeric bin edges by column. |
| `categorical_categories` | `dict[str, list[str]] \| None` | No | Explicit categorical values by column. |
| `categorical_top_n` | `int` | No | Maximum categorical values to include when inferred. |

## Returns

Spark DataFrame containing one profile row per eligible business column.

### Return interpretation

Each returned profile row describes one table or column metric. Downstream governance and guardrail helpers use those rows as evidence.

## Raises / Errors

Raises Spark/DataFrame errors when profiling expressions cannot be evaluated.

### Common failure causes

- The DataFrame is empty or missing expected columns.
- Requested statistics are unsupported for a column type.
- Spark actions fail while computing counts or summaries.
- Excluded columns remove fields needed for review.

## See also

- [Pipeline Execution](../../notebook-templates-implementation-guide/pipeline-execution.md)
- [Governance Review](../../notebook-templates-implementation-guide/governance-review.md)
