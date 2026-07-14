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

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_frequency_distribution.py:46`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_frequency_distribution.py#L46-L123">View on GitHub</a>
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
frequency_df = profile_frequency_distribution(df, columns=["status"], top_n=10)
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `df` | `pyspark.sql.DataFrame` | Yes | Spark DataFrame to profile exactly as supplied by the caller. |
| `columns` | `list[str] or set[str] or tuple[str, ...]` | No | Source columns to profile. By default, eligible non-technical scalar columns are selected. |
| `top_n` | `int` | No | Maximum ranked values to retain per source column. |

## Returns

Spark DataFrame containing ranked top-N value frequencies per profiled column.

### Return interpretation

Each returned row describes one retained value for one source column.

## Raises / Errors

Raises ValueError when top_n is not positive or requested columns do not exist.

### Common failure causes

- Requested columns are missing.
- top_n is not greater than zero.
- Spark actions fail while computing frequency counts.

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
    Reference pages generated: 14 Jul 2026, 1:33 PM SGT
    Call-flow data generated: 13 Jul 2026, 11:33 PM SGT
