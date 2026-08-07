# `profile_frequency_distribution`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.2.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Profile exact value frequencies for eligible Spark DataFrame columns.

<div class="reference-docstring-intro" markdown="1">

The function profiles the complete DataFrame exactly as supplied by the
caller and does not perform sampling internally. By default, all
eligible non-technical scalar columns are selected and every distinct
value is returned for each selected column, including null. Returned
values are converted to their string representation,
``FREQUENCY_PERCENT`` is calculated from the total number of rows in the
supplied DataFrame, and rankings are calculated independently for each
profiled column.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_frequency_distribution.py:8`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_frequency_distribution.py#L8-L72">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">02_pipeline</span>
</p>

**Used in notebooks:** `02_pipeline`

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def profile_frequency_distribution(df, *, columns=None, top_n: int | None=None)
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
frequency_df = profile_frequency_distribution(source_df)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to profile exactly as supplied by the caller. |
| `columns` | `list[str] or set[str] or tuple[str, ...]` | No | Source columns to profile. When supplied, each named column is profiled. When omitted, eligible non-technical scalar columns are selected automatically. Array, map, struct, and binary columns are excluded from automatic selection. |
| `top_n` | `int \| None` | No | Optional maximum ranked frequency rows to retain per profiled column. ``None`` returns every distinct value. A positive integer restricts output size only; it does not sample the DataFrame or avoid counting all distinct values before ranking them. |

## Returns

Spark DataFrame containing ranked frequency rows per profiled column. Null is included as a value, non-null counts are reported separately, and top_n restricts output only when supplied.

### Return interpretation

Each returned row describes one retained value for one source column.

## Raises / Errors

Raises ValueError when supplied top_n is not positive or requested columns do not exist.

### Common failure causes

- top_n is not greater than zero when supplied.
- Requested columns are missing.
- No eligible scalar columns are available when columns is omitted.
- High-cardinality columns can produce expensive full frequency output; top_n limits only returned rows when supplied.

## Notes

<div class="reference-docstring-notes" markdown="1">

The function performs an exact Spark grouped count over the supplied
DataFrame for every selected column. ``top_n`` optionally limits the
returned rows, not the cost of grouping all distinct values. Full
frequency output may be expensive for identifiers, timestamps, free text,
and other high-cardinality columns. For large DataFrames,
explicitly select useful categorical or low-to-medium-cardinality columns
and generally avoid identifiers, UUIDs, timestamps, free-text fields, and
columns where most values are unique. For exploratory analysis, callers may
pass a manually filtered or sampled DataFrame; when they do, the returned
counts and percentages describe that filtered or sampled input rather than
the original full DataFrame.

</div>

## See also

- [Pipeline Execution](../../guided-demo/02-run-pipeline.md)


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
| Live-critical dependencies | 2 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.2.0 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.pipeline.shared.build_frequency_distribution_dataframe</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_profiled_columns</code></li>
</ul>


</details>
