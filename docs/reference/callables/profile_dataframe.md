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
      <td data-label="Meaning">Explicit IANA time zone used for the ``RUN_TIMESTAMP`` evidence field. When omitted, ``config.audit_timezone`` is used and falls back to UTC.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Framework-like configuration carrying ``audit_timezone`` for audit timestamp consistency.</td>
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

- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

### Call flow

```text
profile_dataframe(...)
├── _audit_timestamp_expr(...)
│   └── _get_audit_timezone(...)
│       └── _validate_audit_timezone(...)
├── _build_distribution_summaries(...)
│   ├── _build_categorical_distribution(...)
│   ├── _build_numeric_distribution(...)
│   └── _numeric_bin_edges(...)
├── _get_audit_timezone(...)
│   └── _validate_audit_timezone(...)
├── _get_profiled_columns(...)
└── _is_min_max_supported_type(...)
```

### Internal helpers used by this callable

### `def _audit_timestamp_expr(config: Any=None, timezone_name: str | None=None)`

**What it does:**

Return a Spark expression for the current audit timestamp timezone.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/config.py#L78-L83">View `_audit_timestamp_expr` on GitHub</a>

**Code:**

```python
def _audit_timestamp_expr(config: Any = None, timezone_name: str | None = None):
    """Return a Spark expression for the current audit timestamp timezone."""
    from pyspark.sql import functions as F

    tz_name = _get_audit_timezone(config, timezone_name)
    return F.current_timestamp() if tz_name == "UTC" else F.from_utc_timestamp(F.current_timestamp(), tz_name)
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_audit_timestamp_expr`.

### `def _get_audit_timezone(config: Any=None, timezone_name: str | None=None) -> str`

**What it does:**

Resolve the configured FabricOps audit timezone, defaulting to UTC.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/config.py#L61-L66">View `_get_audit_timezone` on GitHub</a>

**Code:**

```python
def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
    """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
    if timezone_name is not None:
        return _validate_audit_timezone(timezone_name)
    value = getattr(config, "audit_timezone", None) if config is not None else None
    return _validate_audit_timezone(value)
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_get_audit_timezone`.

### `def _validate_audit_timezone(timezone_name: str | None) -> str`

**What it does:**

Return a valid IANA audit timezone name.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/config.py#L27-L58">View `_validate_audit_timezone` on GitHub</a>

**Code:**

```python
def _validate_audit_timezone(timezone_name: str | None) -> str:
    """Return a valid IANA audit timezone name.

    Parameters
    ----------
    timezone_name : str or None
        IANA timezone name to validate. Blank values default to ``"UTC"``.

    Returns
    -------
    str
        Validated timezone name.

    Raises
    ------
    ValueError
        If a non-blank value is not a valid IANA timezone name.
    """
    value = str(timezone_name or DEFAULT_AUDIT_TIMEZONE).strip() or DEFAULT_AUDIT_TIMEZONE
    if value != DEFAULT_AUDIT_TIMEZONE and "/" not in value:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        )
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        ) from exc
    return value
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_validate_audit_timezone`.

### `def _build_distribution_summaries(df, eligible_columns: list[str], dtype_map: dict[str, str], *, include_distributions: bool, distribution_columns: list[str] | set[str] | tuple[str, ...] | None, distribution_bin_edges: dict[str, list[float]] | None, categorical_categories: dict[str, list[str]] | None, categorical_top_n: int) -> dict[str, tuple[str, dict[str, Any]]]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L192-L222">View `_build_distribution_summaries` on GitHub</a>

**Code:**

```python
def _build_distribution_summaries(
    df,
    eligible_columns: list[str],
    dtype_map: dict[str, str],
    *,
    include_distributions: bool,
    distribution_columns: list[str] | set[str] | tuple[str, ...] | None,
    distribution_bin_edges: dict[str, list[float]] | None,
    categorical_categories: dict[str, list[str]] | None,
    categorical_top_n: int,
) -> dict[str, tuple[str, dict[str, Any]]]:
    if not include_distributions:
        return {}

    selected = set(distribution_columns) if distribution_columns is not None else set(eligible_columns)
    summaries: dict[str, tuple[str, dict[str, Any]]] = {}
    for column_name in eligible_columns:
        if column_name not in selected:
            continue
        data_type = dtype_map[column_name]
        lowered_type = (data_type or "").lower()
        if any(token in lowered_type for token in ("tinyint", "smallint", "int", "bigint", "float", "double", "decimal")):
            edges = (distribution_bin_edges or {}).get(column_name) or _numeric_bin_edges(df, column_name)
            distribution = _build_numeric_distribution(df, column_name, edges)
            if distribution is not None:
                summaries[column_name] = ("numeric", distribution)
        elif any(token in lowered_type for token in ("string", "char", "varchar", "boolean")):
            distribution = _build_categorical_distribution(df, column_name, top_n=categorical_top_n, categories=(categorical_categories or {}).get(column_name))
            if distribution is not None:
                summaries[column_name] = ("categorical", distribution)
    return summaries
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_build_distribution_summaries`.

### `def _build_categorical_distribution(df, column_name: str, *, top_n: int=20, categories: list[str] | set[str] | tuple[str, ...] | None=None) -> dict[str, Any] | None`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L152-L189">View `_build_categorical_distribution` on GitHub</a>

**Code:**

```python
def _build_categorical_distribution(df, column_name: str, *, top_n: int = 20, categories: list[str] | set[str] | tuple[str, ...] | None = None) -> dict[str, Any] | None:
    from pyspark.sql import functions as F

    non_null = df.where(F.col(column_name).isNotNull())
    total_count = int(non_null.agg(F.count(F.lit(1)).alias("total_count")).collect()[0]["total_count"])
    if total_count == 0:
        return None

    if categories is not None:
        selected_categories = [str(category) for category in categories]
        if not selected_categories:
            return {"category_counts": {}, "other_count": total_count, "new_categories": []}
        grouped = non_null.groupBy(F.col(column_name).cast("string").alias("_profile_category")).count()
        rows = grouped.where(F.col("_profile_category").isin(selected_categories)).collect()
        category_counts = {category: 0 for category in selected_categories}
        for row in rows:
            category_counts[str(row["_profile_category"])] = int(row["count"])
        kept_count = int(sum(category_counts.values()))
        new_rows = grouped.where(~F.col("_profile_category").isin(selected_categories)).orderBy(F.col("count").desc(), F.col("_profile_category").asc()).limit(top_n).collect()
        return {
            "category_counts": category_counts,
            "other_count": max(total_count - kept_count, 0),
            "new_categories": [str(row["_profile_category"]) for row in new_rows],
        }

    grouped = (
        non_null
        .groupBy(F.col(column_name).cast("string").alias("_profile_category"))
        .count()
        .orderBy(F.col("count").desc(), F.col("_profile_category").asc())
    )
    rows = grouped.limit(top_n).collect()
    if not rows:
        return None
    category_counts = {str(row["_profile_category"]): int(row["count"]) for row in rows}
    kept_count = int(sum(category_counts.values()))
    other_count = max(total_count - kept_count, 0)
    return {"category_counts": category_counts, "other_count": other_count}
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_build_categorical_distribution`.

### `def _build_numeric_distribution(df, column_name: str, edges: list[float]) -> dict[str, list[float] | list[int]] | None`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L120-L149">View `_build_numeric_distribution` on GitHub</a>

**Code:**

```python
def _build_numeric_distribution(df, column_name: str, edges: list[float]) -> dict[str, list[float] | list[int]] | None:
    from pyspark.sql import functions as F

    cleaned_edges: list[float] = []
    for edge in edges:
        value = float(edge)
        if not cleaned_edges or value > cleaned_edges[-1]:
            cleaned_edges.append(value)
    if len(cleaned_edges) < 2:
        return None

    bucket_expr = None
    numeric_value = F.col(column_name).cast("double")
    for index, (lower, upper) in enumerate(zip(cleaned_edges[:-1], cleaned_edges[1:])):
        if index == 0:
            condition = numeric_value < F.lit(upper)
        elif index == len(cleaned_edges) - 2:
            condition = numeric_value >= F.lit(lower)
        else:
            condition = (numeric_value >= F.lit(lower)) & (numeric_value < F.lit(upper))
        bucket_expr = F.when(condition, F.lit(index)) if bucket_expr is None else bucket_expr.when(condition, F.lit(index))

    bucketed = df.where(F.col(column_name).isNotNull()).select(bucket_expr.alias("_profile_bucket"))
    rows = bucketed.where(F.col("_profile_bucket").isNotNull()).groupBy("_profile_bucket").count().collect()
    counts = [0 for _ in range(len(cleaned_edges) - 1)]
    for row in rows:
        bucket = int(row["_profile_bucket"])
        if 0 <= bucket < len(counts):
            counts[bucket] = int(row["count"])
    return {"bin_edges": cleaned_edges, "bin_counts": counts}
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_build_numeric_distribution`.

### `def _numeric_bin_edges(df, column_name: str, *, bin_count: int=10) -> list[float]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L107-L117">View `_numeric_bin_edges` on GitHub</a>

**Code:**

```python
def _numeric_bin_edges(df, column_name: str, *, bin_count: int = 10) -> list[float]:
    values = df.select(column_name).where(f"`{column_name}` is not null")
    try:
        quantiles = values.approxQuantile(column_name, [i / bin_count for i in range(bin_count + 1)], 0.01)
    except Exception:
        return []
    edges: list[float] = []
    for value in quantiles:
        if value is not None and (not edges or float(value) > edges[-1]):
            edges.append(float(value))
    return edges if len(edges) >= 2 else []
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_numeric_bin_edges`.

### `def _get_profiled_columns(df, exclude_columns: list[str] | set[str] | None=None) -> list[str]`

**What it does:**

Return non-technical column names from a Spark DataFrame.

**Source:**

- `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L59-L81">View `_get_profiled_columns` on GitHub</a>

**Code:**

```python
def _get_profiled_columns(df, exclude_columns: list[str] | set[str] | None = None) -> list[str]:
    """Return non-technical column names from a Spark DataFrame.

    Parameters
    ----------
    df : Any
        Spark DataFrame-like object with a ``dtypes`` attribute.
    exclude_columns : list[str] | set[str] | None, optional
        Additional columns to exclude from profiling.

    Returns
    -------
    list[str]
        Eligible business columns to profile.
    """
    excluded = set(_DEFAULT_PROFILE_EXCLUDE_COLUMNS)
    if exclude_columns:
        excluded.update(exclude_columns)
    return [
        name
        for name, _dtype in df.dtypes
        if name not in excluded and not any(str(name).startswith(prefix) for prefix in _DEFAULT_PROFILE_EXCLUDE_PREFIXES)
    ]
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_get_profiled_columns`.

### `def _is_min_max_supported_type(data_type: str) -> bool`

**What it does:**

Return whether min/max aggregation is safe for a Spark type string.

**Source:**

- `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L84-L104">View `_is_min_max_supported_type` on GitHub</a>

**Code:**

```python
def _is_min_max_supported_type(data_type: str) -> bool:
    """Return whether min/max aggregation is safe for a Spark type string."""
    value = (data_type or "").lower()
    unsupported = ("array", "map", "struct", "binary")
    if any(token in value for token in unsupported):
        return False
    supported = (
        "tinyint",
        "smallint",
        "int",
        "bigint",
        "float",
        "double",
        "decimal",
        "date",
        "timestamp",
        "string",
        "char",
        "varchar",
    )
    return any(token in value for token in supported)
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_is_min_max_supported_type`.


</details>

## Source

- Source file path: `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L225-L345">View profile_dataframe on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def profile_dataframe(
    df,
    table_name: str,
    *,
    exclude_columns=None,
    run_timestamp_timezone: str | None = None,
    config: Any = None,
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
    run_timestamp_timezone : str, optional
        Explicit IANA time zone used for the ``RUN_TIMESTAMP`` evidence field.
        When omitted, ``config.audit_timezone`` is used and falls back to UTC.
    config : Any, optional
        Framework-like configuration carrying ``audit_timezone`` for audit
        timestamp consistency.
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

    run_timestamp_timezone = _get_audit_timezone(config=config, timezone_name=run_timestamp_timezone)
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
            _audit_timestamp_expr(timezone_name=run_timestamp_timezone).alias("RUN_TIMESTAMP"),
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
- Source line: `225`
- Inbound references count: 3
- Outbound references count: 5

### AI implementation contract

- **required_context:** Use after reading source/target data and before metadata persistence or governance review workflows that need profile evidence.
- **inputs:** df, table_name, optional exclude_columns, timezone, distribution options, bin edges, category baselines, and top-N settings.
- **output:** Spark DataFrame containing one profile row per eligible business column.
- **side_effects:** Computes profiling aggregations on the provided DataFrame; it does not write metadata, tables, or files.
- **failure_modes:** Raises Spark/DataFrame errors when profiling expressions cannot be evaluated.
- **verification:** Verify the profile row count matches expected business columns and inspect key schema/profile fields before writing evidence.

### Inbound references

- `fabricops_kit.governance_review._prepare_dq_profile_input_rows`
- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../run_table_guardrails/"><code>fabricops_kit.pipeline.run_table_guardrails</code></a>

### Outbound references

- `fabricops_kit.config._audit_timestamp_expr`
- `fabricops_kit.config._get_audit_timezone`
- `fabricops_kit.data_profiling._build_distribution_summaries`
- `fabricops_kit.data_profiling._get_profiled_columns`
- `fabricops_kit.data_profiling._is_min_max_supported_type`

### Raw source metadata

- Source file path: `src/fabricops_kit/data_profiling.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L225-L345">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L225-L345</a>
- Start line: `225`
- End line: `345`
- Signature:

```python
def profile_dataframe(df, table_name: str, *, exclude_columns=None, run_timestamp_timezone: str | None=None, config: Any=None, include_distributions: bool=False, distribution_columns: list[str] | set[str] | tuple[str, ...] | None=None, distribution_bin_edges: dict[str, list[float]] | None=None, categorical_categories: dict[str, list[str]] | None=None, categorical_top_n: int=20)
```

### Internal relationship graph

### Public related functions

- <a href="../enforce_profile_behavior/"><code>fabricops_kit.guardrails.enforce_profile_behavior</code></a>
- <a href="../record_table_governance/"><code>fabricops_kit.governance_review.record_table_governance</code></a>

### Internal implementation helpers

### Call flow

```text
profile_dataframe(...)
├── _audit_timestamp_expr(...)
│   └── _get_audit_timezone(...)
│       └── _validate_audit_timezone(...)
├── _build_distribution_summaries(...)
│   ├── _build_categorical_distribution(...)
│   ├── _build_numeric_distribution(...)
│   └── _numeric_bin_edges(...)
├── _get_audit_timezone(...)
│   └── _validate_audit_timezone(...)
├── _get_profiled_columns(...)
└── _is_min_max_supported_type(...)
```

### Internal helpers used by this callable

### `def _audit_timestamp_expr(config: Any=None, timezone_name: str | None=None)`

**What it does:**

Return a Spark expression for the current audit timestamp timezone.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/config.py#L78-L83">View `_audit_timestamp_expr` on GitHub</a>

**Code:**

```python
def _audit_timestamp_expr(config: Any = None, timezone_name: str | None = None):
    """Return a Spark expression for the current audit timestamp timezone."""
    from pyspark.sql import functions as F

    tz_name = _get_audit_timezone(config, timezone_name)
    return F.current_timestamp() if tz_name == "UTC" else F.from_utc_timestamp(F.current_timestamp(), tz_name)
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_audit_timestamp_expr`.

### `def _get_audit_timezone(config: Any=None, timezone_name: str | None=None) -> str`

**What it does:**

Resolve the configured FabricOps audit timezone, defaulting to UTC.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/config.py#L61-L66">View `_get_audit_timezone` on GitHub</a>

**Code:**

```python
def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
    """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
    if timezone_name is not None:
        return _validate_audit_timezone(timezone_name)
    value = getattr(config, "audit_timezone", None) if config is not None else None
    return _validate_audit_timezone(value)
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_get_audit_timezone`.

### `def _validate_audit_timezone(timezone_name: str | None) -> str`

**What it does:**

Return a valid IANA audit timezone name.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/config.py#L27-L58">View `_validate_audit_timezone` on GitHub</a>

**Code:**

```python
def _validate_audit_timezone(timezone_name: str | None) -> str:
    """Return a valid IANA audit timezone name.

    Parameters
    ----------
    timezone_name : str or None
        IANA timezone name to validate. Blank values default to ``"UTC"``.

    Returns
    -------
    str
        Validated timezone name.

    Raises
    ------
    ValueError
        If a non-blank value is not a valid IANA timezone name.
    """
    value = str(timezone_name or DEFAULT_AUDIT_TIMEZONE).strip() or DEFAULT_AUDIT_TIMEZONE
    if value != DEFAULT_AUDIT_TIMEZONE and "/" not in value:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        )
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        ) from exc
    return value
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_validate_audit_timezone`.

### `def _build_distribution_summaries(df, eligible_columns: list[str], dtype_map: dict[str, str], *, include_distributions: bool, distribution_columns: list[str] | set[str] | tuple[str, ...] | None, distribution_bin_edges: dict[str, list[float]] | None, categorical_categories: dict[str, list[str]] | None, categorical_top_n: int) -> dict[str, tuple[str, dict[str, Any]]]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L192-L222">View `_build_distribution_summaries` on GitHub</a>

**Code:**

```python
def _build_distribution_summaries(
    df,
    eligible_columns: list[str],
    dtype_map: dict[str, str],
    *,
    include_distributions: bool,
    distribution_columns: list[str] | set[str] | tuple[str, ...] | None,
    distribution_bin_edges: dict[str, list[float]] | None,
    categorical_categories: dict[str, list[str]] | None,
    categorical_top_n: int,
) -> dict[str, tuple[str, dict[str, Any]]]:
    if not include_distributions:
        return {}

    selected = set(distribution_columns) if distribution_columns is not None else set(eligible_columns)
    summaries: dict[str, tuple[str, dict[str, Any]]] = {}
    for column_name in eligible_columns:
        if column_name not in selected:
            continue
        data_type = dtype_map[column_name]
        lowered_type = (data_type or "").lower()
        if any(token in lowered_type for token in ("tinyint", "smallint", "int", "bigint", "float", "double", "decimal")):
            edges = (distribution_bin_edges or {}).get(column_name) or _numeric_bin_edges(df, column_name)
            distribution = _build_numeric_distribution(df, column_name, edges)
            if distribution is not None:
                summaries[column_name] = ("numeric", distribution)
        elif any(token in lowered_type for token in ("string", "char", "varchar", "boolean")):
            distribution = _build_categorical_distribution(df, column_name, top_n=categorical_top_n, categories=(categorical_categories or {}).get(column_name))
            if distribution is not None:
                summaries[column_name] = ("categorical", distribution)
    return summaries
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_build_distribution_summaries`.

### `def _build_categorical_distribution(df, column_name: str, *, top_n: int=20, categories: list[str] | set[str] | tuple[str, ...] | None=None) -> dict[str, Any] | None`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L152-L189">View `_build_categorical_distribution` on GitHub</a>

**Code:**

```python
def _build_categorical_distribution(df, column_name: str, *, top_n: int = 20, categories: list[str] | set[str] | tuple[str, ...] | None = None) -> dict[str, Any] | None:
    from pyspark.sql import functions as F

    non_null = df.where(F.col(column_name).isNotNull())
    total_count = int(non_null.agg(F.count(F.lit(1)).alias("total_count")).collect()[0]["total_count"])
    if total_count == 0:
        return None

    if categories is not None:
        selected_categories = [str(category) for category in categories]
        if not selected_categories:
            return {"category_counts": {}, "other_count": total_count, "new_categories": []}
        grouped = non_null.groupBy(F.col(column_name).cast("string").alias("_profile_category")).count()
        rows = grouped.where(F.col("_profile_category").isin(selected_categories)).collect()
        category_counts = {category: 0 for category in selected_categories}
        for row in rows:
            category_counts[str(row["_profile_category"])] = int(row["count"])
        kept_count = int(sum(category_counts.values()))
        new_rows = grouped.where(~F.col("_profile_category").isin(selected_categories)).orderBy(F.col("count").desc(), F.col("_profile_category").asc()).limit(top_n).collect()
        return {
            "category_counts": category_counts,
            "other_count": max(total_count - kept_count, 0),
            "new_categories": [str(row["_profile_category"]) for row in new_rows],
        }

    grouped = (
        non_null
        .groupBy(F.col(column_name).cast("string").alias("_profile_category"))
        .count()
        .orderBy(F.col("count").desc(), F.col("_profile_category").asc())
    )
    rows = grouped.limit(top_n).collect()
    if not rows:
        return None
    category_counts = {str(row["_profile_category"]): int(row["count"]) for row in rows}
    kept_count = int(sum(category_counts.values()))
    other_count = max(total_count - kept_count, 0)
    return {"category_counts": category_counts, "other_count": other_count}
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_build_categorical_distribution`.

### `def _build_numeric_distribution(df, column_name: str, edges: list[float]) -> dict[str, list[float] | list[int]] | None`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L120-L149">View `_build_numeric_distribution` on GitHub</a>

**Code:**

```python
def _build_numeric_distribution(df, column_name: str, edges: list[float]) -> dict[str, list[float] | list[int]] | None:
    from pyspark.sql import functions as F

    cleaned_edges: list[float] = []
    for edge in edges:
        value = float(edge)
        if not cleaned_edges or value > cleaned_edges[-1]:
            cleaned_edges.append(value)
    if len(cleaned_edges) < 2:
        return None

    bucket_expr = None
    numeric_value = F.col(column_name).cast("double")
    for index, (lower, upper) in enumerate(zip(cleaned_edges[:-1], cleaned_edges[1:])):
        if index == 0:
            condition = numeric_value < F.lit(upper)
        elif index == len(cleaned_edges) - 2:
            condition = numeric_value >= F.lit(lower)
        else:
            condition = (numeric_value >= F.lit(lower)) & (numeric_value < F.lit(upper))
        bucket_expr = F.when(condition, F.lit(index)) if bucket_expr is None else bucket_expr.when(condition, F.lit(index))

    bucketed = df.where(F.col(column_name).isNotNull()).select(bucket_expr.alias("_profile_bucket"))
    rows = bucketed.where(F.col("_profile_bucket").isNotNull()).groupBy("_profile_bucket").count().collect()
    counts = [0 for _ in range(len(cleaned_edges) - 1)]
    for row in rows:
        bucket = int(row["_profile_bucket"])
        if 0 <= bucket < len(counts):
            counts[bucket] = int(row["count"])
    return {"bin_edges": cleaned_edges, "bin_counts": counts}
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_build_numeric_distribution`.

### `def _numeric_bin_edges(df, column_name: str, *, bin_count: int=10) -> list[float]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L107-L117">View `_numeric_bin_edges` on GitHub</a>

**Code:**

```python
def _numeric_bin_edges(df, column_name: str, *, bin_count: int = 10) -> list[float]:
    values = df.select(column_name).where(f"`{column_name}` is not null")
    try:
        quantiles = values.approxQuantile(column_name, [i / bin_count for i in range(bin_count + 1)], 0.01)
    except Exception:
        return []
    edges: list[float] = []
    for value in quantiles:
        if value is not None and (not edges or float(value) > edges[-1]):
            edges.append(float(value))
    return edges if len(edges) >= 2 else []
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_numeric_bin_edges`.

### `def _get_profiled_columns(df, exclude_columns: list[str] | set[str] | None=None) -> list[str]`

**What it does:**

Return non-technical column names from a Spark DataFrame.

**Source:**

- `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L59-L81">View `_get_profiled_columns` on GitHub</a>

**Code:**

```python
def _get_profiled_columns(df, exclude_columns: list[str] | set[str] | None = None) -> list[str]:
    """Return non-technical column names from a Spark DataFrame.

    Parameters
    ----------
    df : Any
        Spark DataFrame-like object with a ``dtypes`` attribute.
    exclude_columns : list[str] | set[str] | None, optional
        Additional columns to exclude from profiling.

    Returns
    -------
    list[str]
        Eligible business columns to profile.
    """
    excluded = set(_DEFAULT_PROFILE_EXCLUDE_COLUMNS)
    if exclude_columns:
        excluded.update(exclude_columns)
    return [
        name
        for name, _dtype in df.dtypes
        if name not in excluded and not any(str(name).startswith(prefix) for prefix in _DEFAULT_PROFILE_EXCLUDE_PREFIXES)
    ]
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_get_profiled_columns`.

### `def _is_min_max_supported_type(data_type: str) -> bool`

**What it does:**

Return whether min/max aggregation is safe for a Spark type string.

**Source:**

- `src/fabricops_kit/data_profiling.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/83d4716971843467c062fedf57d0ef56cc62beea/src/fabricops_kit/data_profiling.py#L84-L104">View `_is_min_max_supported_type` on GitHub</a>

**Code:**

```python
def _is_min_max_supported_type(data_type: str) -> bool:
    """Return whether min/max aggregation is safe for a Spark type string."""
    value = (data_type or "").lower()
    unsupported = ("array", "map", "struct", "binary")
    if any(token in value for token in unsupported):
        return False
    supported = (
        "tinyint",
        "smallint",
        "int",
        "bigint",
        "float",
        "double",
        "decimal",
        "date",
        "timestamp",
        "string",
        "char",
        "varchar",
    )
    return any(token in value for token in supported)
```

**Used here because:**

`profile_dataframe` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `profile_dataframe` or another caller that reaches `_is_min_max_supported_type`.


</details>
