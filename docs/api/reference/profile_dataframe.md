# `profile_dataframe`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

## Call-flow summary

- Downstream callables: 12
- Shared helpers: 7
- Private helpers: 5

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=profile_dataframe">Open Live contract call flow</a>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.1.0 |
| Discontinued in | — |
| Contract classification | Live · Live since 0.1.0 |
| Live-critical dependencies | 10 |
| Direct Live dependents | 0 |
| Transitive Live dependents | 0 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.shared._validate_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.build_audit_timestamp_expr</code></li>
<li><code>fabricops_kit.config.shared.get_audit_timezone</code></li>
<li><code>fabricops_kit.pipeline.shared._build_categorical_distribution</code></li>
<li><code>fabricops_kit.pipeline.shared._build_numeric_distribution</code></li>
<li><code>fabricops_kit.pipeline.shared._numeric_bin_edges</code></li>
<li><code>fabricops_kit.pipeline.shared.build_distribution_summaries</code></li>
<li><code>fabricops_kit.pipeline.shared.is_min_max_supported_type</code></li>
<li><code>fabricops_kit.pipeline.shared.profile_dataframe_core</code></li>
<li><code>fabricops_kit.pipeline.shared.resolve_profiled_columns</code></li>
</ul>


Profile a source or target DataFrame for schema, quality, and catalogue evidence.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/pipeline/profile_dataframe.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/profile_dataframe.py#L10-L65">View on GitHub</a>
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


!!! info "Generated reference freshness"
    Reference pages generated: 08 Jul 2026, 1:08 PM SGT
    Call-flow data generated: 09 Jul 2026, 8:52 PM SGT
