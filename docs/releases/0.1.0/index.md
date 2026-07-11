<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# FabricOps Starter Kit 0.1.0

- Package version: `0.1.0`
- Release status: <span class="fabricops-release-status fabricops-release-status--live">Live</span>
- Release date: `2026-07-11`

<a class="md-button md-button--primary" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/tag/v0.1.0">
  View GitHub Release
</a>

## Live in this release

<details class="fabricops-release-inventory" markdown>
<summary>9 Live functions</summary>

| Function | Description |
| --- | --- |
| [`profile_dataframe`](functions/profile_dataframe.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Build canonical DQ-ready profiling rows from a Spark DataFrame. |
| [`read_lakehouse_csv`](functions/read_lakehouse_csv.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read a CSV file from a configured Fabric-resolved path through Spark. |
| [`read_lakehouse_excel`](functions/read_lakehouse_excel.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read an Excel workbook from a configured Fabric-resolved path. |
| [`read_lakehouse_parquet`](functions/read_lakehouse_parquet.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read a Parquet file from a configured Fabric-resolved path through Spark. |
| [`read_lakehouse_table`](functions/read_lakehouse_table.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read a Delta table from a Fabric lakehouse. |
| [`read_warehouse_query`](functions/read_warehouse_query.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read warehouse rows with SQL pushdown. |
| [`read_warehouse_table`](functions/read_warehouse_table.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read a full table from a Microsoft Fabric warehouse. |
| [`write_lakehouse_table`](functions/write_lakehouse_table.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Write a Spark DataFrame to a Fabric lakehouse Delta table. |
| [`write_warehouse_table`](functions/write_warehouse_table.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Write a Spark DataFrame to a Microsoft Fabric warehouse table. |

</details>

<details class="fabricops-release-inventory" markdown>
<summary>4 Live metadata tables</summary>

| Metadata table | Purpose |
| --- | --- |
| [`METADATA_DATA_AGREEMENT`](metadata/metadata_data_agreement.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data agreement. |
| [`METADATA_DATA_AGREEMENT_EVIDENCE`](metadata/metadata_data_agreement_evidence.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data agreement evidence. |
| [`METADATA_DATA_CATALOGUE`](metadata/metadata_data_catalogue.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data catalogue. |
| [`METADATA_DATA_STEWARD`](metadata/metadata_data_steward.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data steward. |

</details>

<details class="fabricops-release-inventory" markdown>
<summary>3 Live notebook templates</summary>

| Notebook template | Purpose |
| --- | --- |
| [`00_env_config`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.1.0/templates/notebooks/00_env_config.ipynb) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Environment bootstrap for FabricOps Starter Kit notebooks. This notebook defines environment-wide values and assembles framework config. |
| [`01_agreement`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.1.0/templates/notebooks/01_agreement.ipynb) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Defines what should be built, who owns it, which rules apply, and what readiness means. This is the first required delivery notebook after `00_env_config`. |
| [`99_explore`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.1.0/templates/notebooks/99_explore.ipynb) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Use this optional support notebook for discovery, profiling, troubleshooting, investigation, and ad hoc analysis. The required delivery path remains: `01_agreement` → `02_pipeline` → `03_governance`. |

</details>

## Changelog

### Added

- Stable Fabric lakehouse and warehouse read/write helpers.
- Dataframe profiling.
- Core agreement, agreement evidence, catalogue, and steward metadata contracts.
- Supported `00_env_config`, `01_agreement`, and `99_explore` notebook templates.
- Generated lifecycle-aware release contracts and reference material.
- Formalized the GitHub-only release workflow for tagged FabricOps releases.
- Added CI expectations for locked dependency installation, linting, tests, strict documentation builds, distribution builds, distribution validation, and wheel import smoke tests.
- Added build-time release traceability documentation for package version, Mike documentation version, and Git commit SHA.

### Changed

- Before v1.0.0, FabricOps simplified the notebook sequence to match the intended delivery flow: Agreement → Pipeline → Review. Explore remains available as optional support and is now placed at `99_explore`.

### Deprecated

### Removed

### Fixed

### Security

### Python package

### Notebook templates

### Metadata model

### Documentation

- Added the release management guide and standardized documentation versioning guidance for Mike `latest`, `stable`, and `dev` aliases.

### Breaking changes

### Known limitations

- Pipeline execution remains Preview for v0.1.0.
- Governance review remains Preview for v0.1.0.
- DQ rule authoring and enforcement remain Preview for v0.1.0.
- Pipeline lineage and run-summary evidence remain Preview for v0.1.0.
- The notebook registry remains Preview for v0.1.0.
- Interactive widget APIs remain Preview for v0.1.0.

### Upgrade instructions

- This is the first supported FabricOps Starter Kit release; no prior supported-version migration is required.
