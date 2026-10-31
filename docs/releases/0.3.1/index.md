<!-- Generated file. Edit docs/releases/manifests/0.3.1.yml or the authoritative source metadata and regenerate. -->

# FabricOps Starter Kit 0.3.1

- Package version: `0.3.1`
- Release status: <span class="fabricops-release-status fabricops-release-status--live">Live</span>
- Release date: `2026-10-31`

<a class="md-button md-button--primary" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/tag/v0.3.1">
  View GitHub Release
</a>

## Formal release scope

<details class="fabricops-release-inventory" markdown>
<summary>20 Live functions</summary>

| Function | Description |
| --- | --- |
| [`finalize_pipeline`](functions/finalize_pipeline.md) | Finalize a Dry Run, Ungoverned or Governed execution accurately. |
| [`orchestrate_read`](functions/orchestrate_read.md) | Read a source using the active pipeline's contracts and runtime. |
| [`orchestrate_write`](functions/orchestrate_write.md) | Evaluate or publish a target using the active pipeline's runtime. |
| [`pipeline_read`](functions/pipeline_read.md) | Read one governed pipeline source through the appropriate Fabric store. |
| [`profile_table`](functions/profile_table.md) | Profile a Spark DataFrame or a complete governed physical table. |
| [`read_lakehouse_csv`](functions/read_lakehouse_csv.md) | Read CSV files from a configured Lakehouse Files location. |
| [`read_lakehouse_excel`](functions/read_lakehouse_excel.md) | Read an Excel workbook from a configured Fabric-resolved path. |
| [`read_lakehouse_json`](functions/read_lakehouse_json.md) | Read JSON data from a configured Lakehouse ``Files`` path through Spark. |
| [`read_lakehouse_parquet`](functions/read_lakehouse_parquet.md) | Read Parquet data from the configured Lakehouse ``Files`` area through Spark. |
| [`read_lakehouse_table`](functions/read_lakehouse_table.md) | Read a configured Lakehouse Delta table as a lazy Spark DataFrame. |
| [`read_warehouse_query`](functions/read_warehouse_query.md) | Execute a read-only Warehouse SQL query and return the query result. |
| [`read_warehouse_table`](functions/read_warehouse_table.md) | Read every row and every column from a Microsoft Fabric Warehouse table. |
| [`resolve_table_id`](functions/resolve_table_id.md) | Return the canonical table identity for configured physical coordinates. |
| [`setup_metadata_tables`](functions/setup_metadata_tables.md) | Create or check the FabricOps metadata tables for one workspace_id. |
| [`setup_notebook`](functions/setup_notebook.md) | Validate notebook startup configuration and resolve required Fabric targets. |
| [`setup_pipeline`](functions/setup_pipeline.md) | Start an isolated pipeline in Dry Run, Ungoverned or Governed mode. |
| [`widget_render_data_agreement`](functions/widget_render_data_agreement.md) | Render a wide, single-flow data-agreement editor. |
| [`widget_render_data_steward`](functions/widget_render_data_steward.md) | Render append-only data steward create/update maintenance. |
| [`write_lakehouse_table`](functions/write_lakehouse_table.md) | Write a Spark DataFrame to a configured Fabric lakehouse Delta table. |
| [`write_warehouse_table`](functions/write_warehouse_table.md) | Write a Spark DataFrame to a configured Fabric Warehouse table. |

</details>

<details class="fabricops-release-inventory" markdown>
<summary>11 Live metadata tables</summary>

| Metadata table | Purpose |
| --- | --- |
| [`METADATA_DATA_AGREEMENT`](metadata/metadata_data_agreement.md) | Supported FabricOps metadata table for data agreement. |
| [`METADATA_DATA_CATALOGUE`](metadata/metadata_data_catalogue.md) | Supported FabricOps metadata table for data catalogue. |
| [`METADATA_DATA_CONTRACT`](metadata/metadata_data_contract.md) | Supported FabricOps metadata table for data contract. |
| [`METADATA_DATA_LINEAGE`](metadata/metadata_data_lineage.md) | Supported FabricOps metadata table for data lineage. |
| [`METADATA_DATA_PROFILED`](metadata/metadata_data_profiled.md) | Supported FabricOps metadata table for data profiled. |
| [`METADATA_DATA_PROFILED_FREQUENCY`](metadata/metadata_data_profiled_frequency.md) | Supported FabricOps metadata table for data profiled frequency. |
| [`METADATA_DATA_STEWARD`](metadata/metadata_data_steward.md) | Supported FabricOps metadata table for data steward. |
| [`METADATA_GUARDRAIL_RESULTS`](metadata/metadata_guardrail_results.md) | Supported FabricOps metadata table for guardrail results. |
| [`METADATA_PIPELINE_REGISTRY`](metadata/metadata_pipeline_registry.md) | Supported FabricOps metadata table for pipeline registry. |
| [`METADATA_PIPELINE_RUN`](metadata/metadata_pipeline_run.md) | Supported FabricOps metadata table for pipeline run. |
| [`METADATA_PROCESSING_STATE`](metadata/metadata_processing_state.md) | Supported FabricOps metadata table for processing state. |

</details>

## Changelog

### Fixed

- Allow pipeline Reads and Writes to use configured Lakehouse and Warehouse stores in Fabric workspaces other than the execution workspace, while preserving each participant's frozen physical binding for the run.

### Upgrade instructions

- Upgrade the package and use the matching v0.3.1 `00_env_config.ipynb` and `02_pipeline.ipynb` release snapshots. The environment template accepts an explicit workspace ID for each configured store.
