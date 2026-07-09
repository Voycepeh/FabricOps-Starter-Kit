<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# `read_lakehouse_csv`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.1.0`

Qualified callable: `fabricops_kit.io.read_lakehouse_csv.read_lakehouse_csv`

Source path: `src/fabricops_kit/io/read_lakehouse_csv.py`

Signature: `read_lakehouse_csv(relative_path: 'str', *, target: 'str' = 'source', spark_session=None, header: 'bool' = True, context: 'dict[str, Any] | None' = None, **options)`

## Description

Read a CSV file from a configured Fabric-resolved path through Spark.

## Parameters

relative_path : str
    CSV file or folder path resolved by the Fabric resolver.
target : str, default="source"
    Logical lakehouse target from ``00_env_config``.
spark_session : object, optional
    Spark session to use instead of the notebook global ``spark``.
header : bool, default=True
    Whether the first row contains column names.
context : dict[str, Any], optional
    Active Fabric context override.
**options
    Additional Spark CSV reader options forwarded to Spark's CSV reader.

## Return value

pyspark.sql.DataFrame
    Spark DataFrame loaded from the CSV path.

## Usage notes

FabricOps resolves the configured Lakehouse Files path from
``00_env_config`` and then delegates to Spark's CSV reader with the supplied
options.

[Back to release overview](../index.md)
