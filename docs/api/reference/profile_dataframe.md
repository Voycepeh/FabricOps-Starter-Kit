# `profile_dataframe`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

## Call-flow summary

- Downstream callables: 4
- Shared helpers: 2
- Private helpers: 2

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=profile_dataframe">Open Preview call flow</a>

Profile a Spark DataFrame for structural and statistical exploration.

<div class="reference-docstring-intro" markdown="1">

The returned profile includes row and null counts, null percentages,
distinct counts and percentages, numeric summary statistics, and minimum
and maximum values for each included input column.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_dataframe.py:8`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_dataframe.py#L8-L49">View on GitHub</a>
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
def profile_dataframe(df, *, exclude_columns=None, approximate_distinct: bool=True)
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
profile_rows_df = profile_dataframe(source_df, exclude_columns=["_ingested_at"], approximate_distinct=True)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to profile. |
| `exclude_columns` | `list[str] or set[str]` | No | Additional caller-selected columns to skip after standard FabricOps technical-column exclusions are applied. |
| `approximate_distinct` | `bool` | No | When True, use Spark ``approx_count_distinct`` for per-column cardinality. When False, use exact ``count_distinct``. |

## Returns

Spark DataFrame with one profiling row per eligible input column and columns COLUMN_NAME, DATA_TYPE, ROW_COUNT, NON_NULL_COUNT, NULL_COUNT, NULL_PERCENT, DISTINCT_COUNT, DISTINCT_PERCENT, MEAN, STDDEV, MIN_VALUE, PERCENTILE_25, MEDIAN, PERCENTILE_75, and MAX_VALUE.

### Return interpretation

Each returned row describes one eligible source column, not one input record. Counts and percentages describe exactly the DataFrame supplied by the caller.

## Raises / Errors

Raises Spark/DataFrame errors when profiling expressions cannot be evaluated.

### Common failure causes

- No eligible non-technical columns remain after exclusions.
- Unsupported complex types or Spark expression limitations can prevent specific statistics.
- Exact distinct counts are more expensive when approximate_distinct is False.
- Spark actions can fail while computing counts, summaries, or percentiles.

## See also

- [Pipeline Execution](../../guided-demo/run-pipeline.md)
- [Governance Review](../../guided-demo/review-guardrails.md)


<details>
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview public function |
| Contract risk | Preview |
| Live-critical dependencies | 0 |

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.1.0 |


</details>
