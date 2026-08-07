# `profile_dataframe`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Profile a Spark DataFrame for structural and statistical exploration.

<div class="reference-docstring-intro" markdown="1">

The returned profile includes row and null counts, null percentages,
exact distinct counts and percentages, numeric summary statistics, and
minimum and maximum values for each included input column. Exact distinct
counts exclude null values.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_dataframe.py:8`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_dataframe.py#L8-L47">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `02_pipeline`, `99_explore`

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def profile_dataframe(df, *, exclude_columns=None)
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
profile_rows_df = profile_dataframe(source_df, exclude_columns=["_ingested_at"])
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to profile. |
| `exclude_columns` | `list[str] or set[str]` | No | Additional caller-selected columns to skip after standard FabricOps technical-column exclusions are applied. |

## Returns

Spark DataFrame with one profiling row per eligible input column and columns COLUMN_NAME, DATA_TYPE, ROW_COUNT, NON_NULL_COUNT, NULL_COUNT, NULL_PERCENT, DISTINCT_COUNT, DISTINCT_PERCENT, MEAN, STDDEV, MIN_VALUE, PERCENTILE_25, MEDIAN, PERCENTILE_75, and MAX_VALUE.

### Return interpretation

Each returned row describes one eligible source column, not one input record. Counts and percentages describe exactly the DataFrame supplied by the caller.

## Raises / Errors

Raises Spark/DataFrame errors when profiling expressions cannot be evaluated.

### Common failure causes

- No eligible non-technical columns remain after exclusions.
- Unsupported complex types or Spark expression limitations can prevent specific statistics.
- Exact distinct counts can be expensive for high-cardinality columns.
- Spark actions can fail while computing counts, summaries, or percentiles.

## See also

- [Pipeline Execution](../../guided-demo/02-run-pipeline.md)
- [Governance Review](../../guided-demo/03-enrich-guardrails.md)


<details>
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.2.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 4 |

### Release history

| Status | Version |
| --- | --- |
| Preview | 0.1.0 |
| Live | 0.2.0 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.pipeline.shared._profile_column_expr</code></li>
<li><code>fabricops_kit.pipeline.shared._profile_percent_expr</code></li>
<li><code>fabricops_kit.pipeline.shared.build_profile_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_profiled_columns</code></li>
</ul>


</details>
