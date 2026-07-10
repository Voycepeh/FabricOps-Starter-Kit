# Changelog

All notable changes to **FabricOps Starter Kit** are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use semantic versioning across the public FabricOps surface: Python APIs, notebook contracts, configuration structures, metadata schemas, agreement and pipeline contract structures, and data-quality rule formats.

## [Unreleased]

### Added

- Drafted the first supported FabricOps Starter Kit release surface for governed Microsoft Fabric notebook projects.
- Drafted Live Fabric input/output helpers, dataframe profiling support, agreement-driven metadata tables, and the supported `00_env_config`, `01_agreement`, and `99_explore` notebook templates for v0.1.0 lifecycle review.
- Published the draft release lifecycle manifest used to separate provisional Live release assets from Preview capabilities during v0.1.0 preparation.
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

- Pipeline execution, governance review, DQ rule authoring and enforcement, and notebook registry capabilities are draft Preview decisions for the v0.1.0 lifecycle review.

### Upgrade instructions

- No runtime upgrade is required for this process-only change. Future released sections should document version-specific upgrade steps here when needed.
- Draft v0.1.0 notes currently assume this will be the first supported release; no prior supported release upgrade is expected.

## Historical notes

A standardized changelog was not maintained before this file. Do not invent historical release entries; add released sections only from reviewed release notes and repository history.
