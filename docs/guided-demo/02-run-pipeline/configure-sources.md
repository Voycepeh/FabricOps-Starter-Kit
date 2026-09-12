# Unit 3: Configure the managed sources

**Use the pre-wired Read blocks for the managed sources created in Step 0B.**

## The Guided Demo uses three Read blocks

| Read block | Managed source | Pattern exercised |
| --- | --- | --- |
| Orders | Source Lakehouse `demo.orders` | Lakehouse table |
| Products | Source Lakehouse `demo.products` | Lakehouse table |
| Order History | Product Warehouse `demo.order_history` | Warehouse query |

Edit or copy the intended Read blocks when adapting the template, but do not rebuild them function by function. The visible dispatch keeps the Lakehouse table and Warehouse query choices explicit while `00_env_config` supplies environment-specific Fabric routing.

Step 0B already used the raw `orders.csv`/`.json`/`.parquet`/`.xlsx`, `products.csv`, and `order_history.csv` files to create these tables. Do not substitute raw file readers into the normal Step 2 walkthrough.

## Use the Warehouse query intentionally

The Order History block runs a project-owned query over the managed Warehouse source to aggregate history by customer before Spark transformation. Because the result is derived rather than the complete physical table, it must not replace the canonical Profile of `demo.order_history`.

## Other supported patterns

FabricOps also supports Lakehouse file readers, full Warehouse table reads, and other configured I/O patterns. They are not the source blocks exercised by this Step 2 walkthrough.

For those supported patterns, see [Lakehouse Files vs Tables](../../reference/engineering-cheat-sheet.md#lakehouse-files-vs-tables), [Lakehouse first — and when Warehouse fits](../../reference/engineering-cheat-sheet.md#lakehouse-first), and the [Function Reference](../../reference/index.md).

## Read preparation stays source-focused

For each managed source, `read_pipeline_prep()` resolves its canonical identity and registers source Lineage. Unit 5 explains how target processing remains separate at the Write boundary.

## Function details

The Guided Demo teaches the concrete template behaviour rather than every function signature. Use the [Function Reference](../../reference/index.md) when you need exact parameters for `read_lakehouse_table()` or `read_warehouse_query()`.

**Previous:** [Unit 2: Run the baseline pipeline](run-baseline-etl.md)<br>
**Next:** [Unit 4: Transform and write](transform-and-load.md)
