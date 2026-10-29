<!-- Generated file. Edit docs/releases/manifests/0.3.0.yml or the authoritative source metadata and regenerate. -->

# `read_warehouse_query`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.0`

Qualified callable: `fabricops_kit.io.read_warehouse_query.read_warehouse_query`

Source path: `src/fabricops_kit/io/read_warehouse_query.py`

Frozen source ref: `v0.3.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.0/src/fabricops_kit/io/read_warehouse_query.py)

Signature: `read_warehouse_query(query: 'str', *, store: 'str' = 'warehouse', context: 'dict[str, Any] | None' = None, **options)`

## Description

Execute a read-only Warehouse SQL query and return the query result.

## Parameters

query : str
    Read-only SQL ``SELECT`` statement, or a CTE beginning with ``WITH``
    and ending in a ``SELECT``, to execute through the Fabric Warehouse SQL
    serving engine.
store : str, default="warehouse"
    Logical Warehouse store key from ``00_env_config``.
context : dict[str, Any], optional
    Active Fabric context override.
**options
    Additional Fabric Warehouse Spark connector reader options. Required
    Fabric connector options are always set from ``00_env_config``.

## Return value

pyspark.sql.DataFrame
    A Spark DataFrame containing exactly the rows and columns returned by
    the supplied Warehouse SQL query.

## Usage notes

``store`` selects a logical configuration alias. Set ``FabricStore.name``
to the actual Warehouse name when it differs from that alias. Without a
configured name, the alias remains the physical name for existing deployments.

FabricOps resolves the configured Warehouse store, sets the Fabric
connector database to that warehouse artifact, and delegates the read-only
SQL text to the Fabric Warehouse Spark connector for pushdown. Query callers
can use two-part names such as ``dbo.orders`` when the configured store
identifies the warehouse database/artifact. Conceptual example:

``df = read_warehouse_query("""SELECT DepartmentId, DepartmentName FROM dbo.DimDepartment WHERE IsActive = 1""")``

That query returns only the selected columns, filters rows in the
Warehouse engine, and transfers only the resulting dataset to Spark.

[Back to release overview](../index.md)
