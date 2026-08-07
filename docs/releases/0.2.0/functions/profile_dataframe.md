<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `profile_dataframe`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.pipeline.profile_dataframe`

Source path: `src/fabricops_kit/pipeline/profile_dataframe.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/pipeline/profile_dataframe.py)

Signature: `profile_dataframe(df, *, exclude_columns=None)`

## Description

Calculate column-level profiling statistics for a Spark DataFrame.

## Parameters

df : pyspark.sql.DataFrame
    Spark DataFrame to profile.
exclude_columns : list[str] or set[str], optional
    Additional caller-selected columns to skip after standard FabricOps
    technical-column exclusions are applied.

## Return value

pyspark.sql.DataFrame
    Spark DataFrame containing one profiling row for each column in the
    input DataFrame, excluding FabricOps technical columns and any columns
    supplied through ``exclude_columns``. Returned columns are
    ``COLUMN_NAME`` (input column name), ``DATA_TYPE`` (Spark data type),
    ``ROW_COUNT`` (rows in ``df``), ``NON_NULL_COUNT`` (non-null values),
    ``NULL_COUNT`` (null values), ``NULL_PERCENT`` (null percentage),
    ``DISTINCT_COUNT`` (distinct value count), ``DISTINCT_PERCENT``
    (distinct value percentage), ``MEAN`` (numeric average), ``STDDEV``
    (numeric sample standard deviation), ``MIN_VALUE`` (minimum value as a
    string when supported), ``PERCENTILE_25`` (25th percentile for numeric
    columns), ``MEDIAN`` (50th percentile for numeric columns),
    ``PERCENTILE_75`` (75th percentile for numeric columns), and
    ``MAX_VALUE`` (maximum value as a string when supported).

## Usage notes

Not documented in the source docstring.

[Back to release overview](../index.md)
