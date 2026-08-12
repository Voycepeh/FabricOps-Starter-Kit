# Capture Data Lineage as part of `02_pipeline`

## Problem

A pipeline needs lightweight evidence of which governed datasets participated as inputs and outputs, without requiring notebook authors to maintain a separate lineage process.

## How FabricOps solves it

**Data Lineage registration is woven into the standard `02_pipeline` profiling workflow.**

The notebook calls [`profile_and_register_table()`](../api/reference/profile_and_register_table.md) after a complete source read with `profile_role="source"`, and after a successful target write and confirmation with `profile_role="target"`. The function profiles and registers the table, then writes its participation in the current notebook activity to Data Lineage.

There is no separate public lineage function in this workflow. Lineage is a documented side effect of the public integrated profiling callable used by `02_pipeline`.

## Use it in FabricOps

**Notebook:** [`02_pipeline`](../guided-demo/02-run-pipeline.md)

**Function:** [`profile_and_register_table()`](../api/reference/profile_and_register_table.md)

## What it produces

Each Data Lineage row identifies a profiled dataset snapshot participating as a source or target in one Fabric activity. The registered evidence includes the stable table key, schema fingerprint, source or target role, profile timestamp, environment, deterministic lineage event identifier, and the standard FabricOps runtime audit context.

FabricOps derives the event identifier from the activity, table, schema fingerprint, and role, then upserts the event. This keeps the solution deliberately small: it records dataset participation alongside the Data Catalogue, Data Profiled, and Data Profiled Frequency evidence already produced by the pipeline.

## Related documentation

- [Run the Common Pipeline Patterns](../guided-demo/02-run-pipeline.md)
- [Data Lineage metadata reference](../reference/metadata/metadata_data_lineage.md)
- [`profile_and_register_table()` reference](../api/reference/profile_and_register_table.md)
