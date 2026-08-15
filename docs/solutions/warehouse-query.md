# Query a Warehouse from PySpark

## Problem

FabricOps standardizes its pipeline workflow around PySpark notebooks. When a source is in a Fabric Warehouse, useful data logic may already be written in SQL.

Without a direct query path, users may translate that SQL into PySpark only to use its result in `02_pipeline`.

## How FabricOps solves it

[`read_warehouse_query()`](../api/reference/read_warehouse_query.md) executes SQL directly against the Warehouse configured in [`00_env_config`](../guided-demo/00B-run-environment-setup.md) and returns the result as a Spark DataFrame.

Teams can keep appropriate Warehouse logic in SQL and continue the rest of the FabricOps pipeline in PySpark. [`02_pipeline`](../guided-demo/02-run-pipeline.md#7-read-from-warehouse-and-write-back-to-lakehouse) demonstrates this path.

## Use it with

**Notebooks:** [`00_env_config`](../guided-demo/00B-run-environment-setup.md), [`02_pipeline`](../guided-demo/02-run-pipeline.md)

**Function:** [`read_warehouse_query()`](../api/reference/read_warehouse_query.md)
