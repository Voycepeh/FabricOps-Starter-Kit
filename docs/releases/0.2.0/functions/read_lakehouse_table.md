<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `read_lakehouse_table`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.io.read_lakehouse_table.read_lakehouse_table`

Source path: `src/fabricops_kit/io/read_lakehouse_table.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/io/read_lakehouse_table.py)

Signature: `read_lakehouse_table(table_name: 'str', *, target: 'str' = 'source', schema: 'str | None' = None, spark_session=None, context: 'dict[str, Any] | None' = None, **options)`

## Description

Resolve a configured Lakehouse Delta table and return a Spark DataFrame.

## Parameters

table_name : str
    Lakehouse table name. Pass schemas with ``schema`` rather than as a
    qualified name.
target : str, default="source"
    Logical Lakehouse target from ``00_env_config``, such as ``source`` or
    ``unified``. FabricOps resolves this target to the configured physical
    Lakehouse and Delta table path.
schema : str or None, default=None
    Optional schema override for schema-enabled Lakehouses. Supply it
    separately from ``table_name``: use ``schema="sales"`` and
    ``table_name="orders"`` rather than ``table_name="sales.orders"``.
    This is normally omitted for Lakehouses without schemas.
spark_session : object, optional
    Spark session to use instead of the notebook global ``spark``.
context : dict[str, Any], optional
    Active Fabric context override.
**options
    Additional Spark Delta ``DataFrameReader`` options forwarded to the
    Delta reader. These options do not provide FabricOps-level filtering or
    projection.

## Return value

pyspark.sql.DataFrame
    A lazy Spark DataFrame representing all rows and columns in the
    resolved Lakehouse Delta table. The data is evaluated when a downstream
    Spark action runs.

## Usage notes

FabricOps resolves the configured Lakehouse Tables path from
``00_env_config`` and then delegates to Spark's Delta reader with any
supplied reader options. Filtering and column selection are applied later
through normal Spark DataFrame operations. Conceptual examples:

``df = read_lakehouse_table(table_name="orders", target="source")``

``df = read_lakehouse_table(table_name="orders", target="source", schema="sales")``

``orders_df = read_lakehouse_table(table_name="sales_orders", target="source")``

``recent_orders_df = orders_df.select("order_id", "customer_id", "order_date", "amount").where("order_date >= '2026-01-01'")``

``read_lakehouse_table`` itself does not accept filtering or projection
arguments, but Spark may push compatible downstream filters and
projections into the Delta scan during execution.

This function does not read through the Warehouse SQL connector, execute a
SQL query, write or copy the table, register metadata, create the table,
mutate the source table, or automatically cache or persist the returned
DataFrame.

[Back to release overview](../index.md)
