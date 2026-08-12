# Read data through Fabric paths and Warehouse queries

## Problem

Fabric data can live in a Lakehouse `Files` area, a managed Lakehouse table, or a Warehouse. A notebook needs to bring the right data into Spark without scattering hardcoded Fabric paths and connection details through the workflow.

## How FabricOps solves it

**FabricOps provides separate read paths for file-oriented, table-oriented, and SQL-oriented access.**

- [`read_lakehouse_csv()`](../api/reference/read_lakehouse_csv.md), [`read_lakehouse_excel()`](../api/reference/read_lakehouse_excel.md), and [`read_lakehouse_parquet()`](../api/reference/read_lakehouse_parquet.md) read those formats from a configured Lakehouse `Files` area.
- [`read_lakehouse_table()`](../api/reference/read_lakehouse_table.md) reads a managed Lakehouse table into Spark.
- [`read_warehouse_table()`](../api/reference/read_warehouse_table.md) retrieves a complete named Warehouse table.
- [`read_warehouse_query()`](../api/reference/read_warehouse_query.md) executes caller-provided SQL against a configured Warehouse and returns the result to the Spark/notebook workflow. This is useful when the data is stored in a Fabric Warehouse but SQL should select or shape it before Spark processing.

These are existing functions rather than a new abstraction. The [`02_pipeline` guided demo](../guided-demo/02-run-pipeline.md) uses them across three flows:

```text
Files → Lakehouse and Warehouse
Lakehouse → transformation → Warehouse
Warehouse → SQL query → Lakehouse
```

## Use it in FabricOps

**Notebook:** [`02_pipeline`](../guided-demo/02-run-pipeline.md)

**Functions:**

- [`read_lakehouse_csv()`](../api/reference/read_lakehouse_csv.md)
- [`read_lakehouse_excel()`](../api/reference/read_lakehouse_excel.md)
- [`read_lakehouse_parquet()`](../api/reference/read_lakehouse_parquet.md)
- [`read_lakehouse_table()`](../api/reference/read_lakehouse_table.md)
- [`read_warehouse_query()`](../api/reference/read_warehouse_query.md)
- [`read_warehouse_table()`](../api/reference/read_warehouse_table.md)

## What happens

The selected function resolves the configured Fabric target and returns a Spark DataFrame for profiling, transformation, or another notebook step. Choose a file helper for a file in a Lakehouse, the Lakehouse table helper for managed Delta data, the Warehouse table helper for a whole table, or the Warehouse query helper when SQL selection is part of the read.

## Related documentation

- [Run the Common Pipeline Patterns](../guided-demo/02-run-pipeline.md)
- [Set up the operating environment](../guided-demo/00B-run-environment-setup.md)
