<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# FabricOps Starter Kit 0.2.0

- Package version: `0.2.0`
- Release status: <span class="fabricops-release-status fabricops-release-status--live">Live</span>
- Release date: `2026-08-07`

<a class="md-button md-button--primary" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/tag/v0.2.0">
  View GitHub Release
</a>

## Formal release scope

<details class="fabricops-release-inventory" markdown>
<summary>13 Live functions</summary>

| Function | Description |
| --- | --- |
| [`profile_and_register_table`](functions/profile_and_register_table.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Profile a supplied Spark DataFrame and save its metadata records. |
| [`profile_dataframe`](functions/profile_dataframe.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Calculate column-level profiling statistics for a Spark DataFrame. |
| [`profile_frequency_distribution`](functions/profile_frequency_distribution.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Calculate exact value frequencies for selected Spark DataFrame columns. |
| [`setup_metadata_tables`](functions/setup_metadata_tables.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Create or check the FabricOps metadata tables for one environment. |
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
<summary>4 Live metadata tables</summary>

| Metadata table | Purpose |
| --- | --- |
| [`METADATA_DATA_CATALOGUE`](metadata/metadata_data_catalogue.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data catalogue. |
| [`METADATA_DATA_LINEAGE`](metadata/metadata_data_lineage.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data lineage. |
| [`METADATA_DATA_PROFILED`](metadata/metadata_data_profiled.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data profiled. |
| [`METADATA_DATA_PROFILED_FREQUENCY`](metadata/metadata_data_profiled_frequency.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data profiled frequency. |

</details>

## Changelog

### Added

- Expanded the supported FabricOps workflow from notebook setup and Fabric data movement to metadata setup, dataframe profiling, catalogue registration, normalized frequency evidence, and profiling lineage.

### Changed

- Promoted `setup_metadata_tables()` to the supported Live public API.
- Promoted `profile_dataframe()`, `profile_frequency_distribution()`, and `profile_and_register_table()` to Live.
- Promoted the catalogue, profile, normalized frequency, and profiling-lineage metadata schemas to Live.

### Deprecated

### Removed

### Fixed

### Security

### Python package

### Notebook templates

### Metadata model

- `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY`, and `METADATA_DATA_LINEAGE` are Live in v0.2.0.
- All other metadata schemas remain Preview.

### Documentation

### Breaking changes

### Known limitations

- Steward, agreement, contract, access, enrichment, guardrail, and guardrail-results schemas remain Preview.
- Governance, authoring, review, and guardrail widgets remain Preview.
- Notebook templates, skills, samples, guided demos, DQ assets, and environment resources remain independently maintained outside the formal package release contract.
- `setup_metadata_tables()` does not automatically migrate, overwrite, or delete incompatible existing metadata tables.
- Existing metadata environments using the legacy `frequency_json` design may require recreation or an explicit migration before using the normalized frequency schema.

### Upgrade instructions

- Upgrade the Fabric Environment custom library to the v0.2.0 wheel.
- Restart notebook sessions after the Environment library update.
- Existing v0.1.0 Live read/write calls should remain compatible.
- Run `setup_metadata_tables()` in a development metadata Lakehouse after upgrading.
- Review failed-table results before recreating or migrating an incompatible existing table.
- Do not silently destroy existing metadata records.
