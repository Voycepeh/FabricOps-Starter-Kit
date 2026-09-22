<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# FabricOps Starter Kit 0.2.0

- Package version: `0.2.0`
- Release status: <span class="fabricops-release-status fabricops-release-status--live">Live</span>
- Release date: `2026-09-22`

<a class="md-button md-button--primary" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/tag/v0.2.0">
  View GitHub Release
</a>

## Formal release scope

<details class="fabricops-release-inventory" markdown>
<summary>17 Live functions</summary>

| Function | Description |
| --- | --- |
| [`pipeline_read`](functions/pipeline_read.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read one governed pipeline source through the appropriate Fabric store. |
| [`pipeline_write`](functions/pipeline_write.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Publish one governed pipeline table target through its configured Fabric store. |
| [`profile_table`](functions/profile_table.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Profile a Spark DataFrame or a complete governed physical table. |
| [`read_lakehouse_json`](functions/read_lakehouse_json.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read JSON data from a configured Lakehouse ``Files`` path through Spark. |
| [`resolve_table_id`](functions/resolve_table_id.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Return the canonical table identity for configured physical coordinates. |
| [`setup_metadata_tables`](functions/setup_metadata_tables.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Create or check the FabricOps metadata tables for one environment. |
| [`widget_render_data_agreement`](functions/widget_render_data_agreement.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Render a wide, single-flow data-agreement editor. |
| [`widget_render_data_steward`](functions/widget_render_data_steward.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Render append-only data steward create/update maintenance. |
| [`read_lakehouse_csv`](functions/read_lakehouse_csv.md) | Resolve CSV data in a Lakehouse Files path and return a lazy Spark DataFrame. |
| [`read_lakehouse_excel`](functions/read_lakehouse_excel.md) | Read an Excel workbook from a configured Fabric-resolved path. |
| [`read_lakehouse_parquet`](functions/read_lakehouse_parquet.md) | Read Parquet data from the configured Lakehouse ``Files`` area through Spark. |
| [`read_lakehouse_table`](functions/read_lakehouse_table.md) | Resolve a configured Lakehouse Delta table and return a Spark DataFrame. |
| [`read_warehouse_query`](functions/read_warehouse_query.md) | Execute a read-only Warehouse SQL query and return the query result. |
| [`read_warehouse_table`](functions/read_warehouse_table.md) | Read every row and every column from a Microsoft Fabric Warehouse table. |
| [`setup_notebook`](functions/setup_notebook.md) | Validate notebook startup configuration and resolve required Fabric targets. |
| [`write_lakehouse_table`](functions/write_lakehouse_table.md) | Write a Spark DataFrame to a configured Fabric lakehouse Delta table. |
| [`write_warehouse_table`](functions/write_warehouse_table.md) | Write a Spark DataFrame to a configured Fabric Warehouse table. |

</details>

<details class="fabricops-release-inventory" markdown>
<summary>6 Live metadata tables</summary>

| Metadata table | Purpose |
| --- | --- |
| [`METADATA_DATA_AGREEMENT`](metadata/metadata_data_agreement.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data agreement. |
| [`METADATA_DATA_CATALOGUE`](metadata/metadata_data_catalogue.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data catalogue. |
| [`METADATA_DATA_LINEAGE`](metadata/metadata_data_lineage.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data lineage. |
| [`METADATA_DATA_PROFILED`](metadata/metadata_data_profiled.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data profiled. |
| [`METADATA_DATA_PROFILED_FREQUENCY`](metadata/metadata_data_profiled_frequency.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data profiled frequency. |
| [`METADATA_DATA_STEWARD`](metadata/metadata_data_steward.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data steward. |

</details>

## Changelog

### Added

- Expanded the supported FabricOps workflow from notebook setup and Fabric data movement to metadata setup, dataframe profiling, catalogue registration, normalized frequency evidence, and profiling lineage.

### Changed

- Promoted `setup_metadata_tables()` to the supported Live public API.
- Promoted `profile_dataframe()`, `profile_frequency_distribution()`, and `profile_and_register_table()` to Live.
- Promoted `read_lakehouse_json()` to the supported Live public API.
- Promoted `pipeline_read()`, `pipeline_write()`, and `resolve_table_id()` to the supported Live public API after Fabric validation of the current governed pipeline flow.
- Promoted `widget_render_data_steward()` and `widget_render_data_agreement()` to the supported Live public API after Fabric validation of the governance setup flow.
- Promoted the catalogue, profile, normalized frequency, and profiling-lineage metadata schemas to Live.

### Deprecated

### Removed

### Fixed

### Security

### Python package

### Notebook templates

### Metadata model

- `METADATA_DATA_STEWARD`, `METADATA_DATA_AGREEMENT`, `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY`, and `METADATA_DATA_LINEAGE` are Live in v0.2.0.
- Data Contract, access, enrichment, guardrail, guardrail-results, and source-observation metadata schemas remain Preview.

### Documentation

### Breaking changes

### Known limitations

- Data Contract, access, enrichment, guardrail, guardrail-results, and source-observation schemas remain Preview.
- Data Contract authoring/selection/activation, catalogue exploration, access scanning, and Guardrail check surfaces remain Preview.
- Notebook templates, skills, samples, guided demos, DQ assets, and environment resources remain independently maintained outside the formal package release contract.
- `setup_metadata_tables()` does not automatically migrate, overwrite, or delete incompatible existing metadata tables.
- Existing metadata environments using the legacy `frequency_json` design may require recreation or an explicit migration before using the normalized frequency schema.

- Incremental pipeline scenarios have not yet completed manual Fabric acceptance testing; defects found in supported Live APIs will be handled as compatible bug fixes.

### Upgrade instructions

- Upgrade the Fabric Environment custom library to the v0.2.0 wheel.
- Restart notebook sessions after the Environment library update.
- Existing v0.1.0 Live read/write calls should remain compatible.
- Run `setup_metadata_tables()` in a development metadata Lakehouse after upgrading.
- Review failed-table results before recreating or migrating an incompatible existing table.
- Do not silently destroy existing metadata records.
