# profile_dataframe

Profile a source or target DataFrame for schema, quality, and catalogue evidence.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/data_profiling.py:226`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L226-L347">View on GitHub</a>
</div>

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
| `exclude_columns` | `list[str] or set[str]` | No | Additional columns to skip, on top of the standard technical columns. |
| `run_timestamp_timezone` | `str \| None` | No | Explicit IANA time zone used for the ``RUN_TIMESTAMP`` evidence field. When omitted, ``config.audit_timezone`` is used and falls back to UTC. |
| `config` | `Any` | No | Framework-like configuration carrying ``audit_timezone`` for audit timestamp consistency. |
| `include_distributions` | `bool` | No | When true, add lightweight distribution summaries for suitable numeric and categorical columns. The default preserves the existing lightweight profile shape and behavior. |
| `distribution_columns` | `list[str] \| set[str] \| tuple[str, ...] \| None` | No | Optional allow-list of important columns for distribution summaries. ``None`` profiles every suitable business column. |
| `distribution_bin_edges` | `dict[str, list[float]] \| None` | No | Optional numeric bin edges keyed by column name. Pass baseline edges to make the current profile directly comparable with a previous profile. |
| `categorical_categories` | `dict[str, list[str]] \| None` | No | Optional baseline category vocabulary keyed by column name. When supplied, those categories are counted explicitly and all other non-null values are rolled into ``other_count`` so the current profile remains comparable with the baseline. |
| `categorical_top_n` | `int` | No | Maximum number of non-null category values to keep per categorical column before rolling the remainder into ``other_count``. |

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

## Relationships

### Used by

- `fabricops_kit.governance_review._prepare_dq_profile_input_rows`
- `fabricops_kit.guardrails.enforce_profile_behavior`
- <a href="run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Calls

- `fabricops_kit.config._audit_timestamp_expr`
- `fabricops_kit.config._get_audit_timezone`
- `fabricops_kit.data_profiling._build_distribution_summaries`
- `fabricops_kit.data_profiling._get_profiled_columns`
- `fabricops_kit.data_profiling._is_min_max_supported_type`

## Implementation details

<details class="reference-implementation-details">
<summary>Notes, side effects, and template usage</summary>

**Used in templates:**

Direct starter notebook code-cell invocations only; import-only, markdown-only, generated metadata, and internal helper calls are not counted.

- `99_explore`

**Side effects:**

Computes profiling aggregations on the provided DataFrame; it does not write metadata, tables, or files.

**Notes:**

Distribution profiling only collects aggregated Spark results such as
quantiles, bucket counts, and grouped category counts. It does not collect
complete datasets to the driver.

</details>

??? info "Call flow"

    Unique internal helpers: 9. Repeated calls may appear in multiple branches.

    <div class="reference-call-tree" role="tree">
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix"></span><a href="profile_dataframe/"><code>profile_dataframe(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L216-L221"><code>_audit_timestamp_expr(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│       └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L193-L223"><code>_build_distribution_summaries(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L153-L190"><code>_build_categorical_distribution(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   ├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L121-L150"><code>_build_numeric_distribution(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L108-L118"><code>_numeric_bin_edges(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L199-L204"><code>_get_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">│   └── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L164-L196"><code>_validate_audit_timezone(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">├── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L59-L82"><code>_get_profiled_columns(...)</code></a></div>
      <div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">└── </span><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L85-L105"><code>_is_min_max_supported_type(...)</code></a></div>
    </div>


<details class="reference-metadata-details">
<summary>Machine-readable metadata / metadata details</summary>

These generated fields are for automation tooling, maintainers, and documentation tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_profiling.profile_dataframe`
- Short name: `profile_dataframe`
- Module: `data_profiling`
- Classification: Callable
- Related module: `data_profiling`
- Source file path: `src/fabricops_kit/data_profiling.py`
- Source line: `226`
- Inbound references count: 3
- Outbound references count: 5
- Used in templates: 99_explore
- Glossary terms: evidence, source data, target table

### Implementation contract

- **required_context:** Use after reading source/target data and before metadata persistence or governance review workflows that need profiles.
- **inputs:** df, table_name, optional exclude_columns, timezone, distribution options, bin edges, category baselines, and top-N settings.
- **output:** Spark DataFrame containing one profile row per eligible business column.
- **side_effects:** Computes profiling aggregations on the provided DataFrame; it does not write metadata, tables, or files.
- **failure_modes:** Raises Spark/DataFrame errors when profiling expressions cannot be evaluated.
- **verification:** Verify the profile row count matches expected business columns and inspect key schema/profile fields before writing evidence.

### Inbound references

- `fabricops_kit.governance_review._prepare_dq_profile_input_rows`
- `fabricops_kit.guardrails.enforce_profile_behavior`
- <a href="run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- `fabricops_kit.config._audit_timestamp_expr`
- `fabricops_kit.config._get_audit_timezone`
- `fabricops_kit.data_profiling._build_distribution_summaries`
- `fabricops_kit.data_profiling._get_profiled_columns`
- `fabricops_kit.data_profiling._is_min_max_supported_type`

### Raw source metadata

- Source file path: `src/fabricops_kit/data_profiling.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L226-L347">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/data_profiling.py#L226-L347</a>
- Start line: `226`
- End line: `347`
- Signature:

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

### Internal relationship graph

### Public related functions

- `fabricops_kit.guardrails.enforce_profile_behavior`
- <a href="widget_review_guardrail_governance/"><code>fabricops_kit.governance_review.widget_review_guardrail_governance</code></a>

### Internal implementation summary

- Internal helper count: 9
- Grouped helper summary is rendered in the page-level Implementation details section; helper chips link to source.

</details>

## Glossary

- <details class="glossary-chip"><summary>Evidence</summary>Stored proof that a profile, decision, result, or relationship existed at a point in time.</details>
- <details class="glossary-chip"><summary>Source data</summary>Input data read from configured upstream files, tables, Lakehouses, or Warehouses before transformation.</details>
- <details class="glossary-chip"><summary>Target table</summary>A written table produced by a pipeline output.</details>

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## See also

- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)
- [Governance Review](../../how-fabricops-works/governance-review.md)
