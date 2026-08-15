# Solution Bank

The FabricOps Solution Bank shows practical data problems already solved by the starter kit. Every solution is backed by an implemented FabricOps function, notebook workflow, or both.

| Solution | Why it is useful |
| --- | --- |
| [Read and write to multiple Lakehouses and Warehouses within a single notebook](multiple-fabric-items.md) | A Fabric notebook supports only one default Lakehouse or Warehouse attachment. Working across multiple Fabric items otherwise requires hardcoded paths or connection details throughout the notebook. |
| [Query a Warehouse from PySpark](warehouse-query.md) | Lakehouse Delta tables work naturally with PySpark, but Warehouse data is queried through SQL. This allows an existing SQL query to be used directly within a PySpark pipeline. |
| [Standardized data profiling](profile-data.md) | DataFrames often need to be profiled before transformation, validation, or analysis. A standard profiling function makes this repeatable across pipelines instead of rebuilding profiling logic each time. |
| [Table-level Data Lineage capture in an ETL pipeline](capture-data-lineage.md) | Trace how data moves from source to target alongside the transformation code that actually performs the ETL, rather than documenting lineage separately. |
| [ETL Guardrails](etl-guardrails.md) | Check schema, freshness, source changes, and data quality as part of an ETL run so problems can be detected before the pipeline continues. |

!!! note "Implementation-backed solutions only"

    This is not a roadmap or architecture-pattern catalogue. Add a solution only after its FabricOps notebook workflow, public function, or both exist.
