# Solution Bank

The FabricOps Solution Bank shows practical data problems already solved by the starter kit. Every solution is backed by an implemented FabricOps function, notebook workflow, or both.

| Solution | Why it is useful |
| --- | --- |
| [Read and write across multiple Lakehouses and Warehouses in one notebook](multiple-fabric-items.md) | Read from one Fabric Lakehouse or Warehouse and write to another without hardcoding environment-specific Fabric paths throughout the notebook. |
| [Query a Warehouse directly from the PySpark pipeline](warehouse-query.md) | Use existing Warehouse SQL inside the standard FabricOps PySpark pipeline without rewriting it as PySpark. |
| [Profile and understand your data](profile-data.md) | Produce repeatable column profiles and useful frequency distributions before deciding how to transform, validate, or govern data. |
| [Capture Data Lineage automatically in `02_pipeline`](capture-data-lineage.md) | Record source and target participation as part of the standard pipeline workflow rather than maintaining lineage separately. |
| [ETL Guardrails](etl-guardrails.md) | Validate governed sources and order target publication by environment. |

!!! note "Implementation-backed solutions only"

    This is not a roadmap or architecture-pattern catalogue. Add a solution only after its FabricOps notebook workflow, public function, or both exist.
