<!-- Generated file. Edit docs/releases/manifests/0.2.5.yml or the authoritative source metadata and regenerate. -->

# FabricOps Starter Kit 0.2.5

- Package version: `0.2.5`
- Release status: <span class="fabricops-release-status fabricops-release-status--live">Live</span>
- Release date: `2026-10-17`

<a class="md-button md-button--primary" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/tag/v0.2.5">
  View GitHub Release
</a>

## Formal release scope

<details class="fabricops-release-inventory" markdown>
<summary>19 Live functions</summary>

| Function | Description |
| --- | --- |
| [`orchestrate_read`](functions/orchestrate_read.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Execute the standard FabricOps governed Read lifecycle. |
| [`orchestrate_write`](functions/orchestrate_write.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Execute the standard FabricOps governed Write lifecycle. |
| [`pipeline_read`](functions/pipeline_read.md) | Read one governed pipeline source through the appropriate Fabric store. |
| [`pipeline_write`](functions/pipeline_write.md) | Publish one governed pipeline table target through its configured Fabric store. |
| [`profile_table`](functions/profile_table.md) | Profile a Spark DataFrame or a complete governed physical table. |
| [`read_lakehouse_csv`](functions/read_lakehouse_csv.md) | Resolve CSV data in a Lakehouse Files path and return a lazy Spark DataFrame. |
| [`read_lakehouse_excel`](functions/read_lakehouse_excel.md) | Read an Excel workbook from a configured Fabric-resolved path. |
| [`read_lakehouse_json`](functions/read_lakehouse_json.md) | Read JSON data from a configured Lakehouse ``Files`` path through Spark. |
| [`read_lakehouse_parquet`](functions/read_lakehouse_parquet.md) | Read Parquet data from the configured Lakehouse ``Files`` area through Spark. |
| [`read_lakehouse_table`](functions/read_lakehouse_table.md) | Resolve a configured Lakehouse Delta table and return a Spark DataFrame. |
| [`read_warehouse_query`](functions/read_warehouse_query.md) | Execute a read-only Warehouse SQL query and return the query result. |
| [`read_warehouse_table`](functions/read_warehouse_table.md) | Read every row and every column from a Microsoft Fabric Warehouse table. |
| [`resolve_table_id`](functions/resolve_table_id.md) | Return the canonical table identity for configured physical coordinates. |
| [`setup_metadata_tables`](functions/setup_metadata_tables.md) | Create or check the FabricOps metadata tables for one environment. |
| [`setup_notebook`](functions/setup_notebook.md) | Validate notebook startup configuration and resolve required Fabric targets. |
| [`widget_render_data_agreement`](functions/widget_render_data_agreement.md) | Render a wide, single-flow data-agreement editor. |
| [`widget_render_data_steward`](functions/widget_render_data_steward.md) | Render append-only data steward create/update maintenance. |
| [`write_lakehouse_table`](functions/write_lakehouse_table.md) | Write a Spark DataFrame to a configured Fabric lakehouse Delta table. |
| [`write_warehouse_table`](functions/write_warehouse_table.md) | Write a Spark DataFrame to a configured Fabric Warehouse table. |

</details>

<details class="fabricops-release-inventory" markdown>
<summary>6 Live metadata tables</summary>

| Metadata table | Purpose |
| --- | --- |
| [`METADATA_DATA_AGREEMENT`](metadata/metadata_data_agreement.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data agreement. |
| [`METADATA_DATA_CATALOGUE`](metadata/metadata_data_catalogue.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data catalogue. |
| [`METADATA_DATA_LINEAGE`](metadata/metadata_data_lineage.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data lineage. |
| [`METADATA_DATA_PROFILED`](metadata/metadata_data_profiled.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data profiled. |
| [`METADATA_DATA_PROFILED_FREQUENCY`](metadata/metadata_data_profiled_frequency.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data profiled frequency. |
| [`METADATA_DATA_STEWARD`](metadata/metadata_data_steward.md) | Supported FabricOps metadata table for data steward. |

</details>

## Changelog

### Added

- Promoted `orchestrate_read()` and `orchestrate_write()` to the Live public API after validating full refresh, incremental append, and SCD write flows in Microsoft Fabric.

### Changed

- `profile_table()` now enables frequency profiling by default and uses a top-five frequency limit by default. Set `frequency_enabled=False` to disable frequency profiling.
- `setup_metadata_tables()` additively adds missing canonical metadata columns while preserving existing rows and extra columns.

### Fixed

- Corrected SCD2 effective-time validation, reused-activity reconciliation, and incremental target probing across governed writes.

### Metadata model

- Added identity and descriptive columns to metadata schemas, including readable table, column, and steward names. `setup_metadata_tables()` adds missing canonical columns while retaining existing rows and extra columns; incompatible canonical types and known legacy schemas still require explicit remediation.

### Notebook templates

- The full refresh, incremental append, and SCD demo flows passed manual Microsoft Fabric validation.

### Upgrade instructions

- Upgrade the Fabric Environment custom library to the v0.2.5 wheel and restart notebook sessions. Run `setup_metadata_tables()` against the configured metadata target to add missing canonical columns; existing rows and extra columns are preserved. Review `profile_table()` frequency defaults if your workflow expects frequency profiling to be disabled or a different top-N limit.
