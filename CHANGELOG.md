# Changelog

All notable changes to **FabricOps Starter Kit** are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use semantic versioning across the formal FabricOps release surface: public Python functions and metadata schemas.

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

### Python package

### Notebook templates

### Metadata model

### Documentation

### Breaking changes

### Known limitations

### Upgrade instructions

## [0.2.0] - 2026-08-07

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

## [0.1.0] - 2026-07-11

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

## Historical notes

A standardized changelog was not maintained before this file. Do not invent historical release entries; add released sections only from reviewed release notes and repository history.
