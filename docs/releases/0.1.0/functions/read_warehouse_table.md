<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# `read_warehouse_table`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.1.0`

Qualified callable: `fabricops_kit.io.read_warehouse_table.read_warehouse_table`

Source path: `src/fabricops_kit/io/read_warehouse_table.py`

Signature: `read_warehouse_table(schema: 'str', table_name: 'str', *, target: 'str' = 'warehouse', spark_session=None, context: 'dict[str, Any] | None' = None, **options)`

## Description

Read a full table from a Microsoft Fabric warehouse.

## Parameters

schema : str
    Warehouse schema name.
table_name : str
    Warehouse table name.
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
    Spark DataFrame loaded through the Fabric warehouse connector.

## Usage notes

FabricOps resolves the configured Warehouse target and table name, then
delegates to the Fabric Warehouse Spark connector. Use this full-table read
for small tables, lookup tables, smoke tests, or intentional full extracts;
prefer ``read_warehouse_query`` for large Warehouse sources so filters and
projections run before Spark receives rows.

[Back to release overview](../index.md)
