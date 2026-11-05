<!-- Generated file. Edit docs/releases/manifests/0.4.0.yml or the authoritative source metadata and regenerate. -->

# FabricOps Starter Kit 0.4.0

- Package version: `0.4.0`
- Release status: <span class="fabricops-release-status fabricops-release-status--live">Live</span>
- Release date: `2026-11-05`

<a class="md-button md-button--primary" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/tag/v0.4.0">
  View GitHub Release
</a>

## Formal release scope

<details class="fabricops-release-inventory" markdown>
<summary>21 Live functions</summary>

| Function | Description |
| --- | --- |
| [`widget_activate_data_contract`](functions/widget_activate_data_contract.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Select and review a physical table, frozen Contract and applicable Agreement. |
| [`finalize_pipeline`](functions/finalize_pipeline.md) | Finalize execution or reopen persisted Engineering deployment/recovery controls. |
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
| [`setup_metadata_tables`](functions/setup_metadata_tables.md) | Create, validate and safely evolve the 14 canonical metadata tables. |
| [`setup_notebook`](functions/setup_notebook.md) | Validate notebook startup configuration and resolve required Fabric targets. |
| [`setup_pipeline`](functions/setup_pipeline.md) | Start a pipeline using the current Fabric notebook identity and one execution mode. |
| [`widget_render_data_agreement`](functions/widget_render_data_agreement.md) | Render a wide, single-flow data-agreement editor. |
| [`widget_render_data_steward`](functions/widget_render_data_steward.md) | Render append-only data steward create/update maintenance. |
| [`write_lakehouse_table`](functions/write_lakehouse_table.md) | Write a Spark DataFrame to a configured Fabric lakehouse Delta table. |
| [`write_warehouse_table`](functions/write_warehouse_table.md) | Write a Spark DataFrame to a configured Fabric Warehouse table. |

</details>

<details class="fabricops-release-inventory" markdown>
<summary>13 Live metadata tables</summary>

| Metadata table | Purpose |
| --- | --- |
| [`METADATA_DATA_CONTRACT_ACTIVATION`](metadata/metadata_data_contract_activation.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Stores retained Governance-owned exact frozen Data Contract selections and scoped Agreement associations per physical workspace and Table ID. |
| [`METADATA_PIPELINE_ACTIVATION`](metadata/metadata_pipeline_activation.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Stores immutable accepted pipeline submission packages and conditional Governance decision history. |
| [`METADATA_DATA_CATALOGUE`](metadata/metadata_data_catalogue.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data catalogue. |
| [`METADATA_PIPELINE_REGISTRY`](metadata/metadata_pipeline_registry.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for pipeline registry. |
| [`METADATA_PIPELINE_RUN`](metadata/metadata_pipeline_run.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for pipeline run. |
| [`METADATA_DATA_AGREEMENT`](metadata/metadata_data_agreement.md) | Supported FabricOps metadata table for data agreement. |
| [`METADATA_DATA_CONTRACT`](metadata/metadata_data_contract.md) | Supported FabricOps metadata table for data contract. |
| [`METADATA_DATA_LINEAGE`](metadata/metadata_data_lineage.md) | Supported FabricOps metadata table for data lineage. |
| [`METADATA_DATA_PROFILED`](metadata/metadata_data_profiled.md) | Supported FabricOps metadata table for data profiled. |
| [`METADATA_DATA_PROFILED_FREQUENCY`](metadata/metadata_data_profiled_frequency.md) | Supported FabricOps metadata table for data profiled frequency. |
| [`METADATA_DATA_STEWARD`](metadata/metadata_data_steward.md) | Supported FabricOps metadata table for data steward. |
| [`METADATA_GUARDRAIL_RESULTS`](metadata/metadata_guardrail_results.md) | Supported FabricOps metadata table for guardrail results. |
| [`METADATA_PROCESSING_STATE`](metadata/metadata_processing_state.md) | Supported FabricOps metadata table for processing state. |

</details>

## Changelog

### Added

- Add Live `METADATA_DATA_CONTRACT_ACTIVATION` and `METADATA_PIPELINE_ACTIVATION` contracts so Data Contract selection, accepted pipeline submissions, and Governance decisions no longer share the Pipeline Registry structure.
- Restore `widget_activate_data_contract()` as a Live Governance entry point for exact frozen Data Contract selections and scoped Agreement associations.

### Changed

- Store nested `METADATA_DATA_CATALOGUE` processing definitions and `METADATA_PIPELINE_RUN` operations, profiling, and failures as validated SQL-compatible JSON strings so the physical tables can be opened in native Microsoft Fabric viewers. FabricOps continues to expose typed logical values to package workflows.
- Record immutable per-workspace Pipeline Promotion versions in `METADATA_PIPELINE_REGISTRY`, with exact Governance approval references from `METADATA_PIPELINE_ACTIVATION` and execution provenance in version 3 Pipeline Run records.
- Apply compatible metadata evolution directly in `setup_metadata_tables()`, preserving Catalogue values, retained Pipeline Run content and hashes, Processing State checkpoints, and publication receipts. Incompatible schemas fail without deleting data.
- Preserve reviewed notebook promotion archives, saved-code and binding verification, preserved-copy integrity repair, retry-safe target claims, configured write strategies, profiling, lineage, and publication receipts.

### Fixed

- Correct unified Read and Write execution metrics, retained failure details, prepared publication inputs, and input-snapshot lifecycle logging.
- Resolve destination schemas through configured workspace bindings and validate consumer physical bindings before Data Agent provisioning.

### Upgrade instructions

- Upgrade the package and use the matching v0.4.0 `00_env_config.ipynb` and `02_pipeline.ipynb` release snapshots.
- Run `setup_metadata_tables()` against the configured Metadata Lakehouse to apply the supported automatic metadata evolution. Existing rows are preserved; incompatible schemas fail without deleting data.
- Validate governed execution in signed-in Microsoft Fabric before enabling Production admission.
