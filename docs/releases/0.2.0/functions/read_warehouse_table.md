<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `read_warehouse_table`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.io.read_warehouse_table.read_warehouse_table`

Source path: `src/fabricops_kit/io/read_warehouse_table.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/io/read_warehouse_table.py)

Signature: `read_warehouse_table(schema: 'str', table_name: 'str', *, target: 'str' = 'warehouse', spark_session=None, context: 'dict[str, Any] | None' = None, **options)`

## Description

Read every row and every column from a Microsoft Fabric Warehouse table.

## Parameters

schema : str
    Physical Warehouse schema name for the source table.
table_name : str
    Physical Warehouse table name for the source table.
target : str, default="warehouse"
    Logical Warehouse configuration name from ``00_env_config``. This
    identifies the configured Warehouse target, while ``schema`` and
    ``table_name`` identify the physical Warehouse table.
spark_session : object, optional
    Spark session to use instead of the notebook global ``spark``.
context : dict[str, Any], optional
    Active Fabric context override.
**options
    Additional Fabric Warehouse Spark connector reader options. Required
    Fabric connector options are always set from ``00_env_config``.

## Return value

pyspark.sql.DataFrame
    A Spark DataFrame containing all rows and columns returned from the
    resolved Warehouse table.

## Usage notes

FabricOps resolves the configured Warehouse target and table name, then
delegates to the Fabric Warehouse Spark connector. Conceptual example:

``df = read_warehouse_table(schema="dbo", table_name="DimDepartment")``

Use ``read_warehouse_query`` instead when you need selected columns, row
filtering, aggregation, joins, row limits, or other caller-controlled SQL
pushdown before Spark receives rows.

[Back to release overview](../index.md)
