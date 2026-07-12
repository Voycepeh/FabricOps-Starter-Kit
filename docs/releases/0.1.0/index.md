<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->

# FabricOps Starter Kit 0.1.0

- Package version: `0.1.0`
- Release status: <span class="fabricops-release-status fabricops-release-status--live">Live</span>
- Release date: `2026-07-11`

<a class="md-button md-button--primary" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/tag/v0.1.0">
  View GitHub Release
</a>

## Formal release scope

<details class="fabricops-release-inventory" markdown>
<summary>8 Live functions</summary>

| Function | Description |
| --- | --- |
| [`read_lakehouse_csv`](functions/read_lakehouse_csv.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read a CSV file from a configured Fabric-resolved path through Spark. |
| [`read_lakehouse_excel`](functions/read_lakehouse_excel.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read an Excel workbook from a configured Fabric-resolved path. |
| [`read_lakehouse_parquet`](functions/read_lakehouse_parquet.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read a Parquet file from a configured Fabric-resolved path through Spark. |
| [`read_lakehouse_table`](functions/read_lakehouse_table.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read a Delta table from a Fabric lakehouse. |
| [`read_warehouse_query`](functions/read_warehouse_query.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read warehouse rows with SQL pushdown. |
| [`read_warehouse_table`](functions/read_warehouse_table.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Read a full table from a Microsoft Fabric warehouse. |
| [`write_lakehouse_table`](functions/write_lakehouse_table.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Write a Spark DataFrame to a Fabric lakehouse Delta table. |
| [`write_warehouse_table`](functions/write_warehouse_table.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Write a Spark DataFrame to a Microsoft Fabric warehouse table. |

</details>

## Changelog

### Added

- Stable Fabric lakehouse and warehouse read/write helpers as the only Live v0.1.0 public API surface.
- Notebook templates, samples, skills, and DQ assets remain manually maintained outside the formal package release contract.
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

- Notebook templates are manually maintained living applications and are not frozen or packaged by v0.1.0.
- Metadata contracts remain Preview for v0.1.0.
- Dataframe profiling remains Preview for v0.1.0.
- Pipeline execution remains Preview for v0.1.0.
- Governance review remains Preview for v0.1.0.
- DQ rule authoring and enforcement are not part of the formal v0.1.0 release contract.
- Pipeline lineage and run-summary evidence remain Preview for v0.1.0.
- The notebook registry remains Preview for v0.1.0.
- Interactive widget APIs remain Preview for v0.1.0.

### Upgrade instructions

- This is the first supported FabricOps Starter Kit release; no prior supported-version migration is required.
