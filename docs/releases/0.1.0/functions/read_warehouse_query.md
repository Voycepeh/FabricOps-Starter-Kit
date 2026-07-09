<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# `read_warehouse_query`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.1.0`

Qualified callable: `fabricops_kit.io.read_warehouse_query.read_warehouse_query`

Source path: `src/fabricops_kit/io/read_warehouse_query.py`

Signature: `read_warehouse_query(query: 'str', *, target: 'str' = 'warehouse', spark_session=None, context: 'dict[str, Any] | None' = None, **options)`

## Description

Read warehouse rows with SQL pushdown.

## Parameters

query : str
    SQL ``SELECT`` statement, or a CTE beginning with ``WITH`` and ending in
    a ``SELECT``, to execute through the Fabric warehouse connector.
target : str, default="warehouse"
    Logical warehouse target from ``00_env_config``.
spark_session : object, optional
    Spark session to use instead of the notebook global ``spark``.
context : dict[str, Any], optional
    Active Fabric context override.
**options
    Additional Fabric Warehouse Spark connector reader options. Required
    Fabric connector options are always set from ``00_env_config``.

## Return value

pyspark.sql.DataFrame
    Spark DataFrame returned by the SQL serving engine.

## Usage notes

FabricOps resolves the configured Warehouse target, sets the Fabric
connector database to that warehouse artifact, and delegates the read-only
SQL text to the Fabric Warehouse Spark connector for pushdown. Query callers
can use two-part names such as ``dbo.orders`` when the configured target
identifies the warehouse database/artifact.

[Back to 0.1.0 functions](index.md)
