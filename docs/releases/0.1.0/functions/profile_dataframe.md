<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# `profile_dataframe`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.1.0`

Qualified callable: `fabricops_kit.pipeline.profile_dataframe`

Source path: `src/fabricops_kit/pipeline/profile_dataframe.py`

Signature: `profile_dataframe(df, table_name: 'str', *, exclude_columns=None, run_timestamp_timezone: 'str | None' = None, config: 'Any' = None, include_distributions: 'bool' = False, distribution_columns: 'list[str] | set[str] | tuple[str, ...] | None' = None, distribution_bin_edges: 'dict[str, list[float]] | None' = None, categorical_categories: 'dict[str, list[str]] | None' = None, categorical_top_n: 'int' = 20)`

## Description

Build canonical DQ-ready profiling rows from a Spark DataFrame.

## Parameters

df : Any
    Spark DataFrame to profile.
table_name : str
    Logical table name written into each profile row.
exclude_columns : list[str] or set[str], optional
    Additional columns to skip, on top of standard technical columns.
run_timestamp_timezone : str, optional
    Explicit IANA time zone used for profile evidence timestamps.
config : Any, optional
    Framework-like configuration carrying audit settings.
include_distributions : bool, default=False
    Whether to include distribution metadata.
distribution_columns : list[str] or set[str] or tuple[str, ...], optional
    Columns to profile with distributions.
distribution_bin_edges : dict[str, list[float]], optional
    Explicit numeric bin edges by column.
categorical_categories : dict[str, list[str]], optional
    Explicit categorical values by column.
categorical_top_n : int, default=20
    Maximum categorical values to include when inferred.

## Return value

pyspark.sql.DataFrame
    Metadata-compatible profile DataFrame.

## Usage notes

Not documented in the source docstring.

[Back to 0.1.0 functions](index.md)
