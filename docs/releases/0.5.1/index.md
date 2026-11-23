<!-- Generated file. Edit docs/releases/manifests/0.5.1.yml or the authoritative source metadata and regenerate. -->

# FabricOps Starter Kit 0.5.1

- Package version: `0.5.1`
- Release status: <span class="fabricops-release-status fabricops-release-status--live">Live</span>
- Release date: `2026-11-23`

<a class="md-button md-button--primary" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/tag/v0.5.1">
  View GitHub Release
</a>

## Formal release scope

<details class="fabricops-release-inventory" markdown>
<summary>21 Live functions</summary>

| Function | Description |
| --- | --- |
| [`finalize_pipeline`](functions/finalize_pipeline.md) | Finalize execution or reopen persisted Engineering deployment/recovery controls. |
| [`orchestrate_demo_reset`](functions/orchestrate_demo_reset.md) | Preview or reset the Guided Demo data and its processing progress to Day 1. |
| [`orchestrate_read`](functions/orchestrate_read.md) | Read a source using the active pipeline's contracts and runtime. |
| [`orchestrate_write`](functions/orchestrate_write.md) | Evaluate or publish a target using the active pipeline's runtime. |
| [`profile_table`](functions/profile_table.md) | Profile a Spark DataFrame or a complete governed physical table. |
| [`read_lakehouse_csv`](functions/read_lakehouse_csv.md) | Read CSV files from a configured Lakehouse Files location. |
| [`read_lakehouse_excel`](functions/read_lakehouse_excel.md) | Read an Excel workbook from a configured Fabric-resolved path. |
| [`read_lakehouse_json`](functions/read_lakehouse_json.md) | Read JSON data from a configured Lakehouse ``Files`` path through Spark. |
| [`read_lakehouse_parquet`](functions/read_lakehouse_parquet.md) | Read Parquet data from the configured Lakehouse ``Files`` area through Spark. |
| [`read_lakehouse_query`](functions/read_lakehouse_query.md) | Run read-only Spark SQL against a configured Lakehouse source. |
| [`read_lakehouse_table`](functions/read_lakehouse_table.md) | Read a configured Lakehouse Delta table as a lazy Spark DataFrame. |
| [`read_warehouse_query`](functions/read_warehouse_query.md) | Execute a read-only Warehouse SQL query and return the query result. |
| [`read_warehouse_table`](functions/read_warehouse_table.md) | Read every row and every column from a Microsoft Fabric Warehouse table. |
| [`setup_metadata_tables`](functions/setup_metadata_tables.md) | Create, validate and safely evolve the 13 canonical metadata tables. |
| [`setup_notebook`](functions/setup_notebook.md) | Validate notebook startup configuration and resolve required Fabric targets. |
| [`setup_pipeline`](functions/setup_pipeline.md) | Start a pipeline using the current Fabric notebook identity and one execution mode. |
| [`widget_data_agreement`](functions/widget_data_agreement.md) | Render a wide, single-flow data-agreement editor. |
| [`widget_data_steward`](functions/widget_data_steward.md) | Render current data steward create/update maintenance. |
| [`write_lakehouse_file`](functions/write_lakehouse_file.md) | Write CSV, Parquet or newline-delimited JSON beneath configured Files. |
| [`write_lakehouse_table`](functions/write_lakehouse_table.md) | Write a Spark DataFrame to a configured Fabric lakehouse Delta table. |
| [`write_warehouse_table`](functions/write_warehouse_table.md) | Write a Spark DataFrame to a configured Fabric Warehouse table. |

</details>

<details class="fabricops-release-inventory" markdown>
<summary>12 Live metadata tables</summary>

| Metadata table | Purpose |
| --- | --- |
| [`METADATA_DATA_CATALOGUE`](metadata/metadata_data_catalogue.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data catalogue. |
| [`METADATA_DATA_CONTRACT`](metadata/metadata_data_contract.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data contract. |
| [`METADATA_DATA_CONTRACT_ACTIVATION`](metadata/metadata_data_contract_activation.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data contract activation. |
| [`METADATA_DATA_LINEAGE`](metadata/metadata_data_lineage.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data lineage. |
| [`METADATA_DATA_PROFILED`](metadata/metadata_data_profiled.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data profiled. |
| [`METADATA_DATA_PROFILED_FREQUENCY`](metadata/metadata_data_profiled_frequency.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data profiled frequency. |
| [`METADATA_GUARDRAIL_RESULTS`](metadata/metadata_guardrail_results.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for guardrail results. |
| [`METADATA_PIPELINE_RUN`](metadata/metadata_pipeline_run.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for pipeline run. |
| [`METADATA_DATA_AGREEMENT`](metadata/metadata_data_agreement.md) | Supported FabricOps metadata table for data agreement. |
| [`METADATA_DATA_STEWARD`](metadata/metadata_data_steward.md) | Supported FabricOps metadata table for data steward. |
| [`METADATA_PIPELINE_ACTIVATION`](metadata/metadata_pipeline_activation.md) | Supported FabricOps metadata table for pipeline activation. |
| [`METADATA_PIPELINE_REGISTRY`](metadata/metadata_pipeline_registry.md) | Supported FabricOps metadata table for pipeline registry. |

</details>

## Changelog

### Changed

- Use physical workspace, Table ID and asset type to identify table and file assets consistently across Catalogue, Contracts, profiling and Pipeline Runs. Keep each file's selector identity and latest observed columns in `METADATA_DATA_CATALOGUE`.
- Store Pipeline participation in typed `METADATA_PIPELINE_RUN.operations` and project versioned column lineage to `METADATA_DATA_LINEAGE` at finalization.
- Move Processing State to `misc.PROCESSING_STATE` in the configured shared Lakehouse; metadata setup initializes that operational table.
- Remove redundant approval fields and legacy workspace placeholders from current metadata schemas while preserving supported v0.5.0 rows through the automatic setup upgrade.
- Consolidate preview OneLake role membership scanning in `scan_onelake_role_members()` and persist its access snapshots in `METADATA_DATA_ACCESS`.

### Fixed

- Preserve file Catalogue and profile metadata through governed reads and writes, including file write row counts and profile stage ordering.
- Retry confirmed metadata write conflicts, and correct Pipeline Run confirmation for retained Governance columns and differing driver timezones.

### Upgrade instructions

- Upgrade the package and run `setup_metadata_tables()` against the configured Metadata Lakehouse. The supported v0.5.0 upgrade preserves retained rows while applying the current schema and initializing `misc.PROCESSING_STATE`.
