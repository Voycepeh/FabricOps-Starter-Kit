# Changelog

All notable changes to **FabricOps Starter Kit** are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use semantic versioning across the public FabricOps surface: Python APIs, notebook contracts, configuration structures, metadata schemas, agreement and pipeline contract structures, and data-quality rule formats.

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

## [0.1.0] - 2026-07-11

### Added

- Stable Fabric lakehouse and warehouse read/write helpers as the only Live v0.1.0 public API surface.
- Versioned `00_env_config` and `99_explore` notebook templates are included in the release pack as Preview templates with explicitly marked Live Fabric I/O sections.
- Preview dataframe profiling, metadata contracts, widgets, governance workflows, and DQ capabilities remain available for evaluation but outside the supported v0.1.0 contract.
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

- Notebook templates remain Preview overall; only explicitly marked Live sections in `00_env_config` and `99_explore` are part of the supported v0.1.0 workflow.
- Metadata contracts remain Preview for v0.1.0.
- Dataframe profiling remains Preview for v0.1.0.
- Pipeline execution remains Preview for v0.1.0.
- Governance review remains Preview for v0.1.0.
- DQ rule authoring and enforcement remain Preview for v0.1.0.
- Pipeline lineage and run-summary evidence remain Preview for v0.1.0.
- The notebook registry remains Preview for v0.1.0.
- Interactive widget APIs remain Preview for v0.1.0.

### Upgrade instructions

- This is the first supported FabricOps Starter Kit release; no prior supported-version migration is required.

## Historical notes

A standardized changelog was not maintained before this file. Do not invent historical release entries; add released sections only from reviewed release notes and repository history.
