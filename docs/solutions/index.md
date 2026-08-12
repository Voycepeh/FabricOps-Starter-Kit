# Solution Bank

The FabricOps Solution Bank shows practical data problems already solved by the starter kit. Every solution is backed by an implemented FabricOps function, notebook workflow, or both.

| Problem | FabricOps approach | Main entry points | Solution |
| --- | --- | --- | --- |
| Bring file, Lakehouse, or Warehouse data into Spark. | Read configured Lakehouse paths and tables, or retrieve Warehouse tables and SQL query results. | `02_pipeline`; `read_lakehouse_*()`; `read_warehouse_*()` | [Read data through Fabric paths and Warehouse queries](read-data.md) |
| Write Spark DataFrames to Fabric storage with workload-appropriate parallelism. | Write to a configured Lakehouse or Warehouse, with optional Spark repartitioning. | `02_pipeline`; `write_lakehouse_table()`; `write_warehouse_table()` | [Write data using parallel processing where appropriate](write-data.md) |
| Understand column statistics and useful value frequencies, then register the evidence. | Produce compact profiles and frequency records through the integrated profiling workflow. | `02_pipeline`; `profile_dataframe()`; `profile_frequency_distribution()`; `profile_and_register_table()` | [Profile data and inspect frequency distributions](profile-data.md) |
| Record which datasets participated as pipeline inputs and outputs. | Register Data Lineage while source and target tables are profiled in `02_pipeline`. | `02_pipeline`; `profile_and_register_table()` | [Capture Data Lineage as part of `02_pipeline`](capture-data-lineage.md) |

!!! note "Implementation-backed solutions only"

    The Solution Bank documents capabilities that already exist in a FabricOps function, notebook workflow, or both. It is not a roadmap or a catalogue of proposed patterns.
