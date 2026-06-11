# profile_dataframe

Profile a source or target DataFrame for schema, quality, and catalogue evidence.

## What this is for and when to use it

Profile a source or target DataFrame for schema, quality, and catalogue evidence.

- Use to create schema, null, distinct, min/max, and optional distribution evidence from a Spark DataFrame.

## When not to use it

- Do not use as a data-quality enforcement step or as a persistence helper; it builds profile rows but does not approve governance evidence.

## Example

```python
profile_rows_df = profile_dataframe(df, table_name="orders", include_distributions=True, distribution_columns=["status"] )
```

## Inputs

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Required</th>
      <th>Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>df</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Spark DataFrame to profile.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>table_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Logical table name written into each profile row.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>exclude_columns</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Additional columns to skip, on top of the standard technical columns.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>run_timestamp_timezone</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Time zone used for the ``RUN_TIMESTAMP`` evidence field.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>include_distributions</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">When true, add lightweight distribution summaries for suitable numeric and categorical columns. The default preserves the existing lightweight profile shape and behavior.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>distribution_columns</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Optional allow-list of important columns for distribution summaries. ``None`` profiles every suitable business column.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>distribution_bin_edges</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Optional numeric bin edges keyed by column name. Pass baseline edges to make the current profile directly comparable with a previous profile.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>categorical_categories</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Optional baseline category vocabulary keyed by column name. When supplied, those categories are counted explicitly and all other non-null values are rolled into ``other_count`` so the current profile remains comparable with the baseline.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>categorical_top_n</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Maximum number of non-null category values to keep per categorical column before rolling the remainder into ``other_count``.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Spark DataFrame containing one profile row per eligible business column.

## Errors and side effects

**Errors:** Raises Spark/DataFrame errors when profiling expressions cannot be evaluated.

**Side effects:** Computes profiling aggregations on the provided DataFrame; it does not write metadata, tables, or files.

## Related functions

- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>
- <a href="../internal/governance_review__prepare_dq_profile_input_rows/"><code>fabricops_kit.governance_review._prepare_dq_profile_input_rows</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../internal/data_profiling__build_distribution_summaries/"><code>fabricops_kit.data_profiling._build_distribution_summaries</code></a>
- <a href="../internal/data_profiling__get_profiled_columns/"><code>fabricops_kit.data_profiling._get_profiled_columns</code></a>
- <a href="../internal/data_profiling__is_min_max_supported_type/"><code>fabricops_kit.data_profiling._is_min_max_supported_type</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/data_profiling.py#L223-L337">View profile_dataframe on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def profile_dataframe(
    df,
    table_name: str,
    *,
    exclude_columns=None,
    run_timestamp_timezone="Asia/Singapore",
    include_distributions: bool = False,
    distribution_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    distribution_bin_edges: dict[str, list[float]] | None = None,
    categorical_categories: dict[str, list[str]] | None = None,
    categorical_top_n: int = 20,
):
    """Build canonical DQ-ready profiling rows from a Spark DataFrame.

    Parameters
    ----------
    df : Any
        Spark DataFrame to profile.
    table_name : str
        Logical table name written into each profile row.
    exclude_columns : list[str] or set[str], optional
        Additional columns to skip, on top of the standard technical columns.
    run_timestamp_timezone : str, default="Asia/Singapore"
        Time zone used for the ``RUN_TIMESTAMP`` evidence field.
    include_distributions : bool, default=False
        When true, add lightweight distribution summaries for suitable numeric
        and categorical columns. The default preserves the existing lightweight
        profile shape and behavior.
    distribution_columns : list[str] or set[str] or tuple[str, ...], optional
        Optional allow-list of important columns for distribution summaries.
        ``None`` profiles every suitable business column.
    distribution_bin_edges : dict[str, list[float]], optional
        Optional numeric bin edges keyed by column name. Pass baseline edges to
        make the current profile directly comparable with a previous profile.
    categorical_categories : dict[str, list[str]], optional
        Optional baseline category vocabulary keyed by column name. When
        supplied, those categories are counted explicitly and all other non-null
        values are rolled into ``other_count`` so the current profile remains
        comparable with the baseline.
    categorical_top_n : int, default=20
        Maximum number of non-null category values to keep per categorical
        column before rolling the remainder into ``other_count``.

    Returns
    -------
    Any
        Spark DataFrame containing one profile row per eligible business
        column. Existing columns are preserved; distribution-enabled runs also
        include ``DISTRIBUTION_TYPE`` and ``DISTRIBUTION_JSON``.

    Notes
    -----
    Distribution profiling only collects aggregated Spark results such as
    quantiles, bucket counts, and grouped category counts. It does not collect
    complete datasets to the driver.
    """
    from pyspark.sql import functions as F

    eligible_columns = _get_profiled_columns(df, exclude_columns=exclude_columns)
    if not eligible_columns:
        raise ValueError("No eligible non-technical columns found for metadata profiling.")

    dtype_map = dict(df.dtypes)
    row_count = int(df.count())
    distributions = _build_distribution_summaries(
        df,
        eligible_columns,
        dtype_map,
        include_distributions=include_distributions,
        distribution_columns=distribution_columns,
        distribution_bin_edges=distribution_bin_edges,
        categorical_categories=categorical_categories,
        categorical_top_n=categorical_top_n,
    )

    agg_exprs = []
    for column_name in eligible_columns:
        agg_exprs.append(F.sum(F.col(column_name).isNull().cast("int")).alias(f"{column_name}_NULL_COUNT"))
        agg_exprs.append(F.countDistinct(F.col(column_name)).alias(f"{column_name}_DISTINCT_COUNT"))
        if _is_min_max_supported_type(dtype_map[column_name]):
            agg_exprs.append(F.min(F.col(column_name)).alias(f"{column_name}_MIN"))
            agg_exprs.append(F.max(F.col(column_name)).alias(f"{column_name}_MAX"))

    agg_df = df.agg(*agg_exprs)
    denominator = F.lit(row_count if row_count > 0 else 1).cast("double")

    rows = []
    for column_name in eligible_columns:
        select_exprs = [
            F.lit(table_name).alias("TABLE_NAME"),
            F.from_utc_timestamp(F.current_timestamp(), run_timestamp_timezone).alias("RUN_TIMESTAMP"),
            F.lit(column_name).alias("COLUMN_NAME"),
            F.lit(dtype_map[column_name]).alias("DATA_TYPE"),
            F.lit(row_count).alias("ROW_COUNT"),
            F.coalesce(F.col(f"{column_name}_NULL_COUNT"), F.lit(0)).cast("long").alias("NULL_COUNT"),
            F.round((F.coalesce(F.col(f"{column_name}_NULL_COUNT"), F.lit(0)).cast("double") / denominator) * 100, 3).alias("NULL_PERCENT"),
            F.coalesce(F.col(f"{column_name}_DISTINCT_COUNT"), F.lit(0)).cast("long").alias("DISTINCT_COUNT"),
            F.round((F.coalesce(F.col(f"{column_name}_DISTINCT_COUNT"), F.lit(0)).cast("double") / denominator) * 100, 3).alias("DISTINCT_PERCENT"),
            F.col(f"{column_name}_MIN").cast("string").alias("MIN_VALUE") if f"{column_name}_MIN" in agg_df.columns else F.lit(None).cast("string").alias("MIN_VALUE"),
            F.col(f"{column_name}_MAX").cast("string").alias("MAX_VALUE") if f"{column_name}_MAX" in agg_df.columns else F.lit(None).cast("string").alias("MAX_VALUE"),
        ]
        if include_distributions:
            distribution_type, distribution_payload = distributions.get(column_name, (None, None))
            select_exprs.extend(
                [
                    F.lit(distribution_type).cast("string").alias("DISTRIBUTION_TYPE"),
                    F.lit(json.dumps(distribution_payload, sort_keys=True) if distribution_payload is not None else None).cast("string").alias("DISTRIBUTION_JSON"),
                ]
            )
        rows.append(agg_df.select(*select_exprs))

    out = rows[0]
    for next_row in rows[1:]:
        out = out.unionByName(next_row)
    return out
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_profiling.profile_dataframe`
- Short name: `profile_dataframe`
- Module: `data_profiling`
- Classification: Callable
- Related module: `data_profiling`
- Source file path: `src/fabricops_kit/data_profiling.py`
- Source line: `223`
- Inbound references count: 3
- Outbound references count: 3

### AI implementation contract

- **required_context:** Use after reading source/target data and before metadata persistence or governance review workflows that need profile evidence.
- **inputs:** df, table_name, optional exclude_columns, timezone, distribution options, bin edges, category baselines, and top-N settings.
- **output:** Spark DataFrame containing one profile row per eligible business column.
- **side_effects:** Computes profiling aggregations on the provided DataFrame; it does not write metadata, tables, or files.
- **failure_modes:** Raises Spark/DataFrame errors when profiling expressions cannot be evaluated.
- **verification:** Verify the profile row count matches expected business columns and inspect key schema/profile fields before writing evidence.

### Inbound references

- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>
- <a href="../internal/governance_review__prepare_dq_profile_input_rows/"><code>fabricops_kit.governance_review._prepare_dq_profile_input_rows</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- <a href="../internal/data_profiling__build_distribution_summaries/"><code>fabricops_kit.data_profiling._build_distribution_summaries</code></a>
- <a href="../internal/data_profiling__get_profiled_columns/"><code>fabricops_kit.data_profiling._get_profiled_columns</code></a>
- <a href="../internal/data_profiling__is_min_max_supported_type/"><code>fabricops_kit.data_profiling._is_min_max_supported_type</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/data_profiling.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/data_profiling.py#L223-L337">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/b37a3d3a2b947b2e265229d7ea688a0bac6a5396/src/fabricops_kit/data_profiling.py#L223-L337</a>
- Start line: `223`
- End line: `337`
- Signature:

```python
def profile_dataframe(df, table_name: str, *, exclude_columns=None, run_timestamp_timezone='Asia/Singapore', include_distributions: bool=False, distribution_columns: list[str] | set[str] | tuple[str, ...] | None=None, distribution_bin_edges: dict[str, list[float]] | None=None, categorical_categories: dict[str, list[str]] | None=None, categorical_top_n: int=20)
```

### Internal relationship graph

### Public related functions

- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

### Internal implementation helpers

- <a href="../enforce_catalogue_stability/"><code>fabricops_kit.drift.enforce_catalogue_stability</code></a>
- <a href="../internal/governance_review__prepare_dq_profile_input_rows/"><code>fabricops_kit.governance_review._prepare_dq_profile_input_rows</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>
- <a href="../internal/data_profiling__build_distribution_summaries/"><code>fabricops_kit.data_profiling._build_distribution_summaries</code></a>
- <a href="../internal/data_profiling__get_profiled_columns/"><code>fabricops_kit.data_profiling._get_profiled_columns</code></a>
- <a href="../internal/data_profiling__is_min_max_supported_type/"><code>fabricops_kit.data_profiling._is_min_max_supported_type</code></a>

</details>
