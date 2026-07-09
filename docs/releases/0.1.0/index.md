<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# FabricOps Starter Kit 0.1.0

- Package version: `0.1.0`
- Release status: <span class="fabricops-release-status fabricops-release-status--live">Live</span>
- Release date: `2026-07-08`

<a class="md-button md-button--primary" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/tag/v0.1.0">
  View GitHub Release
</a>

## Live in this release

<details class="fabricops-release-inventory" markdown>
<summary>9 Live functions</summary>

| Function | Description |
| --- | --- |
| [`profile_dataframe`](functions/profile_dataframe.md) | Build canonical DQ-ready profiling rows from a Spark DataFrame. |
| [`read_lakehouse_csv`](functions/read_lakehouse_csv.md) | Read a CSV file from a configured Fabric-resolved path through Spark. |
| [`read_lakehouse_excel`](functions/read_lakehouse_excel.md) | Read an Excel workbook from a configured Fabric-resolved path. |
| [`read_lakehouse_parquet`](functions/read_lakehouse_parquet.md) | Read a Parquet file from a configured Fabric-resolved path through Spark. |
| [`read_lakehouse_table`](functions/read_lakehouse_table.md) | Read a Delta table from a Fabric lakehouse. |
| [`read_warehouse_query`](functions/read_warehouse_query.md) | Read warehouse rows with SQL pushdown. |
| [`read_warehouse_table`](functions/read_warehouse_table.md) | Read a full table from a Microsoft Fabric warehouse. |
| [`write_lakehouse_table`](functions/write_lakehouse_table.md) | Write a Spark DataFrame to a Fabric lakehouse Delta table. |
| [`write_warehouse_table`](functions/write_warehouse_table.md) | Write a Spark DataFrame to a Microsoft Fabric warehouse table. |

</details>

<details class="fabricops-release-inventory" markdown>
<summary>4 Live metadata tables</summary>

| Metadata table | Purpose |
| --- | --- |
| [`METADATA_DATA_AGREEMENT`](metadata/metadata_data_agreement.md) | Supported FabricOps metadata table for data agreement. |
| [`METADATA_DATA_AGREEMENT_EVIDENCE`](metadata/metadata_data_agreement_evidence.md) | Supported FabricOps metadata table for data agreement evidence. |
| [`METADATA_DATA_CATALOGUE`](metadata/metadata_data_catalogue.md) | Supported FabricOps metadata table for data catalogue. |
| [`METADATA_DATA_STEWARD`](metadata/metadata_data_steward.md) | Supported FabricOps metadata table for data steward. |

</details>

<details class="fabricops-release-inventory" markdown>
<summary>3 Live notebook templates</summary>

| Notebook template | Purpose |
| --- | --- |
| [`00_env_config`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.1.0/templates/notebooks/00_env_config.ipynb) | Environment bootstrap for FabricOps Starter Kit notebooks. This notebook defines environment-wide values and assembles framework config. |
| [`01_agreement`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.1.0/templates/notebooks/01_agreement.ipynb) | Defines what should be built, who owns it, which rules apply, and what readiness means. This is the first required delivery notebook after `00_env_config`. |
| [`99_explore`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.1.0/templates/notebooks/99_explore.ipynb) | Use this optional support notebook for discovery, profiling, troubleshooting, investigation, and ad hoc analysis. The required delivery path remains: `01_agreement` → `02_pipeline` → `03_governance`. |

</details>

## Changelog

### Added

- Established the first supported FabricOps Starter Kit release surface for governed Microsoft Fabric notebook projects.
- Shipped Live Fabric input/output helpers, dataframe profiling support, agreement-driven metadata tables, and the supported `00_env_config`, `01_agreement`, and `99_explore` notebook templates.
- Published the release lifecycle manifest used to separate Live release assets from Preview capabilities.

### Known limitations

- Pipeline execution, governance review, DQ rule authoring and enforcement, and notebook registry capabilities remain Preview in this release.

### Upgrade instructions

- This is the first supported release; no prior supported release upgrade is required.
