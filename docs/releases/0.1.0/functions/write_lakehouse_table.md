<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# `write_lakehouse_table`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.1.0`

Qualified callable: `fabricops_kit.io.write_lakehouse_table.write_lakehouse_table`

Source path: `src/fabricops_kit/io/write_lakehouse_table.py`

Signature: `write_lakehouse_table(df, table_name: 'str', *, target: 'str' = 'unified', schema=None, mode='append', partition_by=None, repartition_by=None, options=None, verbose=True, context=None)`

## Description

Write a Spark DataFrame to a Fabric lakehouse Delta table.

## Parameters

df : pyspark.sql.DataFrame
    Spark DataFrame to write.
table_name : str
    Lakehouse table name. Pass schemas with ``schema`` rather than as a qualified name.
target : str, default="unified"
    Logical lakehouse target from ``00_env_config``.
schema : str or None, default=None
    Optional schema override for schema-enabled lakehouses.
mode : str, default="append"
    Spark write mode: ``append``, ``overwrite``, ``errorifexists``, or ``ignore``.
partition_by : str or list[str], optional
    Column or columns used to physically partition the Delta table.
repartition_by : int, str, list, or tuple, optional
    Optional repartitioning before write.
options : dict, optional
    Additional Spark Delta ``DataFrameWriter`` options forwarded before
    saving the configured Lakehouse Tables path.
verbose : bool, default=True
    Whether to print the resolved output path before writing.
context : dict[str, Any], optional
    Active Fabric context override.

## Return value

None
    The DataFrame is written to the configured Delta table path.

## Usage notes

FabricOps resolves the configured Lakehouse Tables path from
``00_env_config`` and then delegates to Spark's Delta writer with any
supplied writer options.

[Back to 0.1.0 functions](index.md)
