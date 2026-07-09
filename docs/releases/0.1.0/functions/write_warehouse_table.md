<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# `write_warehouse_table`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.1.0`

Qualified callable: `fabricops_kit.io.write_warehouse_table.write_warehouse_table`

Source path: `src/fabricops_kit/io/write_warehouse_table.py`

Signature: `write_warehouse_table(df, schema: 'str', table_name: 'str', *, target: 'str' = 'warehouse', mode: 'str' = 'append', repartition_by=None, options: 'dict[str, Any] | None' = None, context: 'dict[str, Any] | None' = None)`

## Description

Write a Spark DataFrame to a Microsoft Fabric warehouse table.

## Parameters

df : pyspark.sql.DataFrame
    Spark DataFrame to publish.
schema : str
    Warehouse schema name.
table_name : str
    Warehouse table name.
target : str, default="warehouse"
    Logical warehouse target from ``00_env_config``.
mode : str, default="append"
    Spark writer mode supported by the Fabric connector.
repartition_by : int, str, list, or tuple, optional
    Optional repartitioning before write. This controls Spark write
    parallelism and does not create a physically partitioned Warehouse
    table.
options : dict, optional
    Additional Fabric Warehouse Spark connector writer options. Required
    Fabric connector options are always set from ``00_env_config``.
context : dict[str, Any], optional
    Active Fabric context override.

## Return value

None
    The DataFrame is written through the Fabric warehouse connector.

## Usage notes

FabricOps resolves the configured Warehouse target and table name, then
delegates to the Fabric Warehouse Spark connector. ``options`` are passed to
the underlying ``DataFrameWriter`` after required Fabric connector options.

[Back to 0.1.0 functions](index.md)
