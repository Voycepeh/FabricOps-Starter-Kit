# Changelog

All notable changes to **FabricOps Starter Kit** are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use semantic versioning across the public FabricOps surface: Python APIs, notebook contracts, configuration structures, metadata schemas, agreement and pipeline contract structures, and data-quality rule formats.

## [Unreleased]

### Added

- Curated the formal FabricOps Starter Kit v0.1.0 release inventory while keeping the release in preparation.
- Documented supported Fabric lakehouse and warehouse input/output helpers for the first v0.1.0 release surface.
- Documented dataframe profiling as part of the supported v0.1.0 release surface.
- Documented the core agreement, evidence, catalogue, and steward metadata contracts as the supported v0.1.0 metadata boundary.
- Documented the supported `00_env_config`, `01_agreement`, and `99_explore` notebook templates for v0.1.0.
- Added release lifecycle visibility that separates Live v0.1.0 assets from Preview capabilities still being stabilised.
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

- No runtime upgrade is required for this process-only release-preparation change. Future released sections should document version-specific upgrade steps here when needed.
- Draft v0.1.0 notes currently assume this will be the first supported release; no prior supported release upgrade is expected.

## Historical notes

A standardized changelog was not maintained before this file. Do not invent historical release entries; add released sections only from reviewed release notes and repository history.
