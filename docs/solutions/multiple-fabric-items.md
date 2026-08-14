# Read and write across multiple Lakehouses and Warehouses in one notebook

## Problem

A single Fabric notebook may need to read from one Lakehouse or Warehouse and write to another. This is common when a pipeline combines data from multiple Fabric items or moves data between source and target items.

Working with the notebook's attached default Lakehouse or Warehouse is straightforward. Reading from and writing to additional Fabric items requires the notebook to resolve the correct item and path for each operation.

Hardcoding those Fabric paths throughout the notebook makes the pipeline harder to maintain and harder to promote between Development and Production.

## How FabricOps solves it

FabricOps keeps Lakehouse and Warehouse routing in [`00_env_config`](../guided-demo/00B-run-environment-setup.md). Its read and write functions resolve the configured Fabric item at runtime.

The same notebook can therefore read from one or more Lakehouses and Warehouses and write to another without carrying environment-specific Fabric paths throughout the pipeline. [`02_pipeline`](../guided-demo/02-run-pipeline.md) demonstrates this across file, Lakehouse, and Warehouse sources and targets.

## Use it with

**Notebooks:** [`00_env_config`](../guided-demo/00B-run-environment-setup.md), [`02_pipeline`](../guided-demo/02-run-pipeline.md)

**Read functions:** [`read_lakehouse_csv()`](../api/reference/read_lakehouse_csv.md), [`read_lakehouse_excel()`](../api/reference/read_lakehouse_excel.md), [`read_lakehouse_parquet()`](../api/reference/read_lakehouse_parquet.md), [`read_lakehouse_table()`](../api/reference/read_lakehouse_table.md), [`read_warehouse_table()`](../api/reference/read_warehouse_table.md), and [`read_warehouse_query()`](../api/reference/read_warehouse_query.md)

**Write functions:** [`write_lakehouse_table()`](../api/reference/write_lakehouse_table.md) and [`write_warehouse_table()`](../api/reference/write_warehouse_table.md)

## Related documentation

- [Set up the operating environment](../guided-demo/00B-run-environment-setup.md)
- [Run the Common Pipeline Patterns](../guided-demo/02-run-pipeline.md)
