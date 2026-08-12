# Write data using parallel processing where appropriate

## Problem

A prepared Spark DataFrame may need to be stored as a managed Lakehouse table or transferred to a Warehouse table. Larger writes can benefit from additional Spark tasks, while unnecessary partitions add shuffle and file or connector overhead.

## How FabricOps solves it

**FabricOps uses the existing table writers, with optional Spark-side repartitioning when it fits the workload.**

- [`write_lakehouse_table()`](../api/reference/write_lakehouse_table.md) writes to a configured Lakehouse Delta table and accepts `repartition_by` for Spark execution. Its separate `partition_by` option controls the persisted Delta layout, not write-task parallelism.
- [`write_warehouse_table()`](../api/reference/write_warehouse_table.md) writes through the configured Warehouse path and accepts `repartition_by` before connector transfer. It does not create Lakehouse-style physical partitions.

The [`02_pipeline` demo](../guided-demo/02-run-pipeline.md#7-read-from-warehouse-and-write-back-to-lakehouse) demonstrates repartitioning before a Lakehouse write. Parallel processing can help larger workloads, but additional partitions also create overhead. The appropriate strategy depends on workload size, the existing partition count, and the data shape; more partitions are not always faster.

## Use it in FabricOps

**Notebook:** [`02_pipeline`](../guided-demo/02-run-pipeline.md)

**Functions:**

- [`write_lakehouse_table()`](../api/reference/write_lakehouse_table.md)
- [`write_warehouse_table()`](../api/reference/write_warehouse_table.md)

## What happens

FabricOps writes the DataFrame to the configured target. When `repartition_by` is supplied, Spark redistributes the DataFrame before that write so the operation can use the requested task distribution. Omitting it keeps the DataFrame's existing execution partitions.

## When to use it

Start with the normal write path. Consider repartitioning when a larger workload has too little or poorly balanced Spark-side concurrency, then test the choice against the real data. Avoid forcing extra partitions on small workloads.

## Related documentation

- [`02_pipeline`: write and profile the Lakehouse target](../guided-demo/02-run-pipeline.md#write-and-profile-the-target)
- [`02_pipeline`: read from Warehouse and write back to Lakehouse](../guided-demo/02-run-pipeline.md#7-read-from-warehouse-and-write-back-to-lakehouse)
