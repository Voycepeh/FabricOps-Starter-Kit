# Table-level Data Lineage capture in an ETL pipeline

## Problem

Pipeline lineage is useful, but it can become another manual task to maintain. If every notebook implements it differently, the records can become inconsistent or incomplete.

## How FabricOps solves it

FabricOps captures **Data Lineage** as part of the standard [`02_pipeline`](../guided-demo/02-run-pipeline.md) workflow.

When [`profile_and_register_table()`](../api/reference/profile_and_register_table.md) is used for the source and target, FabricOps records whether each dataset participated as a `source` or `target` in the current pipeline activity. The lineage evidence is created alongside the profiling and metadata registration already happening in the pipeline.

There is no separate public lineage function to call in this workflow. Following the standard FabricOps pipeline captures basic source-to-target lineage instead of making it a separate process to maintain.

## Use it with

**Notebook:** [`02_pipeline`](../guided-demo/02-run-pipeline.md)

**Function:** [`profile_and_register_table()`](../api/reference/profile_and_register_table.md)

## Related documentation

- [Data Lineage metadata reference](../reference/metadata/metadata_data_lineage.md)
