<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `profile_frequency_distribution`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.pipeline.profile_frequency_distribution`

Source path: `src/fabricops_kit/pipeline/profile_frequency_distribution.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/pipeline/profile_frequency_distribution.py)

Signature: `profile_frequency_distribution(df, *, columns=None, top_n: 'int | None' = None)`

## Description

Calculate exact value frequencies for selected Spark DataFrame columns.

## Parameters

df : pyspark.sql.DataFrame
    Spark DataFrame to profile exactly as supplied by the caller.
columns : list[str] or set[str] or tuple[str, ...], optional
    Source columns to profile. When supplied, each named column is
    profiled. When omitted, eligible non-technical scalar columns are
    selected automatically. Array, map, struct, and binary columns are
    excluded from automatic selection.
top_n : int or None, optional
    Optional maximum ranked frequency rows to retain per profiled column.
    ``None`` returns every distinct value. A positive integer restricts
    output size only; it does not sample the DataFrame or avoid counting
    all distinct values before ranking them.

## Return value

pyspark.sql.DataFrame
    A Spark DataFrame containing ranked frequency rows for each selected
    input column. Each row represents one distinct value,
    including null, and contains its count, percentage, rank, source data
    type, total profiled row count, and non-null count. Returned columns
    are ``COLUMN_NAME`` (profiled input column name), ``DATA_TYPE`` (Spark
    data type of the input column), ``VALUE`` (distinct value converted to
    a string; null remains null), ``FREQUENCY_COUNT`` (number of input rows
    containing the value), ``FREQUENCY_PERCENT`` (percentage of all
    supplied DataFrame rows containing the value), ``FREQUENCY_RANK``
    (rank within the profiled column ordered by descending frequency),
    ``PROFILED_ROW_COUNT`` (total number of rows in the supplied
    DataFrame), and ``PROFILED_NON_NULL_COUNT`` (number of non-null rows
    for the profiled column).

## Usage notes

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

[Back to release overview](../index.md)
