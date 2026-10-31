<!-- Generated file. Edit docs/releases/manifests/0.3.1.yml or the authoritative source metadata and regenerate. -->

# `read_lakehouse_table`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.1`

Qualified callable: `fabricops_kit.io.read_lakehouse_table.read_lakehouse_table`

Source path: `src/fabricops_kit/io/read_lakehouse_table.py`

Frozen source ref: `v0.3.1`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.1/src/fabricops_kit/io/read_lakehouse_table.py)

Signature: `read_lakehouse_table(table_name: 'str | None' = None, *, table_id: 'str | None' = None, store: 'str' = 'Bronze', schema: 'str | None' = None, context: 'dict[str, Any] | None' = None, **options)`

## Description

Read a configured Lakehouse Delta table as a lazy Spark DataFrame.

## Parameters

table_name : str, optional
    Required unless table_id is supplied. Lakehouse table name. Pass schemas with ``schema`` rather than as a
    qualified name. Omit it when ``table_id`` is supplied.
table_id : str, optional
    Canonical registered table identity. When supplied, FabricOps resolves
    ``table_name``, ``store``, and ``schema`` from the Catalogue. Do not
    combine with table_name, schema, or a non-default store.
store : str, default="Bronze"
    Logical Lakehouse store key from ``00_env_config``, such as ``bronze`` or
    ``silver``. FabricOps resolves this store key to the configured physical
    Lakehouse and Delta table path.
schema : str or None, default=None
    Optional schema override for schema-enabled Lakehouses. Supply it
    separately from ``table_name``: use ``schema="sales"`` and
    ``table_name="orders"`` rather than ``table_name="sales.orders"``.
    This is normally omitted for Lakehouses without schemas.
context : dict[str, Any], optional
    Active Fabric context override.
**options
    Additional Spark Delta ``DataFrameReader`` options forwarded to the
    Delta reader. These options do not provide FabricOps-level filtering or
    projection.

## Return value

pyspark.sql.DataFrame
    A lazy Spark DataFrame representing the governed rows and all columns
    in the resolved Lakehouse Delta table. The data is evaluated when a
    downstream Spark action runs.

## Usage notes

Use either table_name with store and optional schema, or table_id to resolve
the registered physical location from METADATA_DATA_CATALOGUE. Reader options
are forwarded to Spark Delta. The call does not register or profile data.

[Back to release overview](../index.md)
