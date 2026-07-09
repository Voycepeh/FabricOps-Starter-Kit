<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# `read_lakehouse_table`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.1.0`

Qualified callable: `fabricops_kit.io.read_lakehouse_table.read_lakehouse_table`

Source path: `src/fabricops_kit/io/read_lakehouse_table.py`

Signature: `read_lakehouse_table(table_name: 'str', *, target: 'str' = 'source', schema: 'str | None' = None, spark_session=None, context: 'dict[str, Any] | None' = None, **options)`

## Description

Read a Delta table from a Fabric lakehouse.

## Parameters

table_name : str
    Lakehouse table name. Pass schemas with ``schema`` rather than as a qualified name.
target : str, default="source"
    Logical lakehouse target from ``00_env_config``.
schema : str or None, default=None
    Optional schema override for schema-enabled lakehouses.
spark_session : object, optional
    Spark session to use instead of the notebook global ``spark``.
context : dict[str, Any], optional
    Active Fabric context override.
**options
    Additional Spark Delta reader options forwarded to ``DataFrameReader``.

## Return value

pyspark.sql.DataFrame
    Spark DataFrame loaded from the configured Delta table path.

## Usage notes

FabricOps resolves the configured Lakehouse Tables path from
``00_env_config`` and then delegates to Spark's Delta reader with any
supplied reader options.

[Back to 0.1.0 functions](index.md)
