# Unit 3: Configure sources

**Choose the source that `02_pipeline` should read. The template keeps environment-specific Fabric routing out of your project logic.**

## Supported source patterns

| Source | Use when |
| --- | --- |
| Lakehouse CSV | Source data arrives as CSV files. |
| Lakehouse Excel | Source data arrives in an Excel workbook. |
| Lakehouse Parquet | Source data arrives as Parquet files. |
| Lakehouse table | The source is already a managed Delta table. |
| Warehouse table | The complete source is a named Warehouse table. |
| Warehouse SQL | The source should be filtered, joined, or aggregated in SQL before Spark processing. |

The template uses FabricOps IO helpers behind these patterns rather than hardcoding workspace and item paths throughout the notebook.

## Lakehouse file examples

![Read Excel](../../assets/02/Read_Excel.png)

![Read Parquet](../../assets/02/Read_Parquet.png)

![Read CSV for Warehouse](../../assets/02/Read_CSV_WH_DEMO.png)

## Warehouse example

Use the Warehouse table path when you need the complete physical table. Use the SQL path when source-side filtering, joins, or aggregation are more appropriate.

![Read Warehouse](../../assets/02/Read_WH.png)

A filtered, joined, or aggregated query result should not replace the canonical profile of one complete physical source table.

## Source strategy is a separate choice

Where the data lives and how much of it should be processed are different questions. After choosing the source, Unit 5 explains the processing strategies available to the template: Full Dataset, Incremental Watermark, and Incremental Partition.

## Function details

The Guided Demo teaches the template behaviour rather than every function signature. Use the [Function Reference](../../reference/index.md) when you need exact parameters for `read_lakehouse_csv()`, `read_lakehouse_excel()`, `read_lakehouse_parquet()`, `read_lakehouse_table()`, `read_warehouse_table()`, or `read_warehouse_query()`.

**Previous:** [Unit 2: Run the baseline ETL](run-baseline-etl.md)  
**Next:** [Unit 4: Transform and load](transform-and-load.md)
