# Read and write across multiple Fabric items

## Problem

A Fabric notebook can easily read from and write to its attached default Lakehouse or Warehouse. Real pipelines often need to work across multiple Lakehouses and Warehouses.

Exact Fabric paths can reach those items, but hardcoding the paths throughout a notebook makes the pipeline harder to maintain and promote between environments.

## How FabricOps solves it

FabricOps keeps Fabric item routing in [`00_env_config`](../guided-demo/00B-run-environment-setup.md) and resolves the configured Lakehouse or Warehouse at runtime through its read and write functions.

A pipeline can therefore read from one Fabric item and write to another without embedding environment-specific paths throughout the notebook. [`02_pipeline`](../guided-demo/02-run-pipeline.md) demonstrates this across file, Lakehouse, and Warehouse sources and targets.

## Use it with

**Notebooks:** [`00_env_config`](../guided-demo/00B-run-environment-setup.md), [`02_pipeline`](../guided-demo/02-run-pipeline.md)

**Read functions:** [`read_lakehouse_csv()`](../api/reference/read_lakehouse_csv.md), [`read_lakehouse_excel()`](../api/reference/read_lakehouse_excel.md), [`read_lakehouse_parquet()`](../api/reference/read_lakehouse_parquet.md), [`read_lakehouse_table()`](../api/reference/read_lakehouse_table.md), [`read_warehouse_table()`](../api/reference/read_warehouse_table.md), and [`read_warehouse_query()`](../api/reference/read_warehouse_query.md)

**Write functions:** [`write_lakehouse_table()`](../api/reference/write_lakehouse_table.md) and [`write_warehouse_table()`](../api/reference/write_warehouse_table.md)

## Related documentation

- [Set up the operating environment](../guided-demo/00B-run-environment-setup.md)
- [Run the Common Pipeline Patterns](../guided-demo/02-run-pipeline.md)
