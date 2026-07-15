# `profile_frequency_distribution`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

## Call-flow summary

- Downstream callables: 3
- Shared helpers: 1
- Private helpers: 2

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=profile_frequency_distribution">Open Preview call flow</a>

Profile top-N value frequencies for selected Spark DataFrame columns.

<div class="reference-docstring-intro" markdown="1">

The function profiles the complete DataFrame exactly as supplied by the
caller and does not perform sampling internally. It returns up to ``top_n``
most frequent values for each selected column, includes null as a frequency
value, converts returned values to their string representation, and
calculates ``FREQUENCY_PERCENT`` from the total number of rows in the
supplied DataFrame. Rankings are calculated independently for each
profiled column.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_frequency_distribution.py:46`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_frequency_distribution.py#L46-L159">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">Usage detection may exclude indirect or generated references.</span>
</p>

**Used in notebooks:** Usage detection may exclude indirect or generated references.

## Usage notes

Use this as part of the standard Starter Kit pipeline flow. Pipeline helpers prepare, validate, profile, write, and document pipeline data in a consistent way across notebooks.

For profiling-related pipeline functions, the output captures the important details and profile of the data so downstream users can review the dataset consistently instead of relying on one-off summaries.


## Signature

<div class="reference-api-definition" markdown="1">

```python
def profile_frequency_distribution(df, *, columns=None, top_n: int=20)
```

</div>

## Example usage

<div class="reference-example-usage" markdown="1">

```python
frequency_df = profile_frequency_distribution(source_df, columns=["enrolment_status", "programme_code"], top_n=10)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to profile exactly as supplied by the caller. |
| `columns` | `list[str] or set[str] or tuple[str, ...]` | No | Source columns to profile. When supplied, each named column is profiled. When omitted, eligible non-technical scalar columns are selected automatically. Array, map, struct, and binary columns are excluded from automatic selection. |
| `top_n` | `int` | No | Maximum ranked frequency rows to retain per profiled column. This limits returned result size only; it does not sample the DataFrame or avoid counting all distinct values before ranking them. To return every distinct value, supply a sufficiently large positive ``top_n``. |

## Returns

Spark DataFrame containing up to top_n ranked frequency rows per profiled column. Null is included as a value and non-null counts are reported separately.

### Return interpretation

Each returned row describes one retained value for one source column.

## Raises / Errors

Raises ValueError when top_n is not positive or requested columns do not exist.

### Common failure causes

- top_n is not greater than zero.
- Requested columns are missing.
- No eligible scalar columns are available when columns is omitted.
- High-cardinality columns require expensive grouped counts before the top-N limit is applied.

## Notes

<div class="reference-docstring-notes" markdown="1">

The function performs an exact Spark grouped count over the supplied
DataFrame for every selected column. ``top_n`` limits the returned rows,
not the cost of grouping all distinct values. For large DataFrames,
explicitly select useful categorical or low-to-medium-cardinality columns
and generally avoid identifiers, UUIDs, timestamps, free-text fields, and
columns where most values are unique. For exploratory analysis, callers may
pass a manually filtered or sampled DataFrame; when they do, the returned
counts and percentages describe that filtered or sampled input rather than
the original full DataFrame.

</div>

## See also

- [Pipeline Execution](../../guided-demo/run-pipeline.md)


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


</details>

!!! info "Generated reference freshness"
    Reference pages generated: 15 Jul 2026, 11:42 PM SGT
    Call-flow data generated: 15 Jul 2026, 11:41 PM SGT
