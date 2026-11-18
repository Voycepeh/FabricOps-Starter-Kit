<!-- Generated file. Edit docs/releases/manifests/0.5.0.yml or the authoritative source metadata and regenerate. -->

# `read_lakehouse_query`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.5.0`

Qualified callable: `fabricops_kit.io.read_lakehouse_query.read_lakehouse_query`

Source path: `src/fabricops_kit/io/read_lakehouse_query.py`

Frozen source ref: `v0.5.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.5.0/src/fabricops_kit/io/read_lakehouse_query.py)

Signature: `read_lakehouse_query(query: 'str', *, table_name: 'str', store: 'str' = 'Bronze', schema: 'str | None' = None, context: 'dict[str, Any] | None' = None)`

## Description

Run read-only Spark SQL against a configured Lakehouse source.

## Parameters

query : str
    One read-only Spark SQL SELECT or CTE referencing the declared source.
    Simple integer T-SQL TOP projections are also supported.
table_name : str
    Required Lakehouse table name referenced by the query. Supply its schema
    separately with ``schema``.
store : str, default "Bronze"
    Logical Lakehouse store key configured in ``00_env_config``.
schema : str | None, optional
    Schema for the declared source in a schema-enabled Lakehouse.
context : dict[str, Any] | None, optional
    Active Fabric context override containing an existing Spark session
    and configured Lakehouse routing.

## Return value

pyspark.sql.DataFrame
    Lazy query result bound to the configured physical source. A downstream
    Spark action evaluates the data.

## Usage notes

Not documented in the source docstring.

[Back to release overview](../index.md)
