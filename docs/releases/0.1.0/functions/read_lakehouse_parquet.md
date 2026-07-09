<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# `read_lakehouse_parquet`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.1.0`

Qualified callable: `fabricops_kit.io.read_lakehouse_parquet.read_lakehouse_parquet`

Source path: `src/fabricops_kit/io/read_lakehouse_parquet.py`

Signature: `read_lakehouse_parquet(relative_path: 'str', *, target: 'str' = 'source', verbose: 'bool' = True, spark_session=None, context: 'dict[str, Any] | None' = None, **options)`

## Description

Read a Parquet file from a configured Fabric-resolved path through Spark.

## Parameters

relative_path : str
    Parquet file path resolved by the Fabric resolver. Root-level files such
    as ``customers.parquet`` and nested paths such as
    ``input/customers.parquet`` are supported.
target : str, default="source"
    Logical lakehouse target from ``00_env_config``.
verbose : bool, default=True
    Whether to print read and timestamp-conversion fallback progress.
spark_session : object, optional
    Spark session to use instead of the notebook global ``spark``.
context : dict[str, Any], optional
    Active Fabric context override.
**options
    Additional Spark Parquet reader options forwarded to every original and
    timestamp-converted fallback read attempt.

## Return value

pyspark.sql.DataFrame
    Spark DataFrame loaded from the Parquet path.

## Usage notes

FabricOps resolves the configured Lakehouse Files path from
``00_env_config`` and then delegates to Spark's Parquet reader. If Spark
cannot read the original path because of timestamp precision issues, the
existing ``_tsus`` fallback conversion path is attempted with the same
reader options.

[Back to 0.1.0 functions](index.md)
