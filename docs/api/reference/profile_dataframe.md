# profile_dataframe

??? info "Downstream callables: 2"

    Dependency data is generated from the callable architecture inventory.

    <div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><code>profile_dataframe(...)</code></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L18-L73"><code>profile_dataframe_core(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">    └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/_profiling_workflows.py#L19-L140"><code>profile_dataframe_core(...)</code></a></div>
    </div>

Profile a source or target DataFrame for schema, quality, and catalogue evidence.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">99_explore</span>
</p>

**Used in notebooks:** `99_explore`

## Source

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L80-L135">View source on GitHub</a>

Implemented in `src/fabricops_kit/data_profiling.py`:80.

## Usage guidance

### Use when

- Use during exploration, governance review, or guardrail preparation when a table needs reproducible profiles.

### Do not use when

- Do not use as a data-quality enforcement step or as a persistence helper; it builds profile rows but does not approve governance evidence.

### Additional context

Builds deterministic profiles for a DataFrame, including schema, row counts, nulls, distinct counts, and optional summary values.


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

## Glossary

<div class="reference-glossary-term-list" aria-label="Glossary terms used on this page">
<span class="glossary-chip"><span class="glossary-chip-label">Evidence</span><span class="glossary-chip-definition">Stored proof that a profile, decision, result, or relationship existed at a point in time.</span> <a href="../../../reference/glossary/#evidence">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Source data</span><span class="glossary-chip-definition">Input data read from configured upstream files, tables, Lakehouses, or Warehouses before transformation.</span> <a href="../../../reference/glossary/#source-data">Full definition</a></span>
<span class="glossary-chip"><span class="glossary-chip-label">Target table</span><span class="glossary-chip-definition">A written table produced by a pipeline output.</span> <a href="../../../reference/glossary/#target-table">Full definition</a></span>
</div>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Execution](../../notebook-templates-implementation-guide/pipeline-execution.md)
- [Governance Review](../../notebook-templates-implementation-guide/governance-review.md)
