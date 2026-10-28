# Changelog

All notable changes to **FabricOps Starter Kit** are documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases use semantic versioning across the formal FabricOps release surface: public Python functions and metadata schemas.

## [Unreleased]

## [0.3.0] - Pending release

### Breaking changes

- Establish workspace-ID-based configuration and routing as the new architectural baseline. Earlier package versions (v0.2.5 and before) are superseded and must not be combined with v0.3.0 notebook templates.
- Existing legacy environment-keyed metadata layouts are not automatically migrated. Use a fresh workspace-model metadata installation; preserve existing Live metadata until an explicit migration is approved.

### Metadata lifecycle

- Promote `METADATA_DATA_CONTRACT`, `METADATA_GUARDRAIL_RESULTS`, `METADATA_PIPELINE_REGISTRY`, `METADATA_PIPELINE_RUN`, and `METADATA_PROCESSING_STATE` to Live in v0.3.0. These form supported governance, guardrail-result, registration, execution, and processing-state persistence contracts. `METADATA_DATA_ACCESS` remains Preview. Live schemas may evolve additively; breaking structural changes require an explicit migration.

### Pipeline execution

- Introduce Dry Run, Ungoverned, and Governed execution paths, with explicit setup and finalization and workspace-scoped governance behaviour.
- Freeze matching `00_env_config` and `02_pipeline` notebook templates for this release.

### Upgrade instructions

- Upgrade the package and both notebook templates together. Do not mix v0.3.0 notebooks with v0.2.5 or earlier packages.
- Validate full refresh, incremental append, and SCD demo workflows in Microsoft Fabric before publishing.



### Removed

- Removed the Preview Data Catalogue Viewer widget and the optional exploration notebook template. Query the centralized metadata tables directly through PySpark or SQL, and use native Fabric interfaces or project-specific notebooks for consumption. Metadata schemas, population, profiling, lineage, and orchestration are unchanged.

### Breaking changes

- **Major breaking architecture change:** FabricOps now uses stable workspace IDs for configuration, physical observations, profiling, Processing State, Testing and activation. Environment is removed as an identity/routing namespace. This work is unreleased; the major version will be selected in a separate release PR.
- Replace environment-keyed configuration with workspace-keyed paths. `FabricStore.env`, `setup_notebook(env=...)`, `setup_metadata_tables(env=...)`, scanner `environment_name` arguments and returned environment fields are removed/replaced. Ordinary no-argument setup and Read/Write orchestration calls retain their calling patterns. No compatibility aliases or metadata migration are supplied; use a fresh workspace-model metadata installation.
- Contract column definitions enforce required presence by default, explicit optional presence and exact normalized datatypes. Unexpected columns block. Structural Schema checking is mandatory and cannot be disabled by omitting an authored rule.

- Removed the separate Coverage Gate stage and `coverage_result` return field from the Live public `orchestrate_write()` interface. Both orchestrators use selected Data Contract Guardrails; no minimum active-check count is required. Their shared execution-plan signatures are unchanged. The internal `check_guardrail_coverage()` implementation is removed; it was already excluded from the supported public API. The Preview `widget_select_data_contract()` inspector adds available execution results and a `refresh` callback.
- Frozen released documentation and notebook snapshots remain unchanged. The new workspace metadata layout starts fresh; a separate release PR will select the major version.

### Changed

- **Observe locally → Govern globally → Test locally → Activate locally.** Data Contract histories remain global per table ID. Governance selects workspace evidence; different workspaces can independently activate different frozen versions. New profiles never alter contracts.
- Data Contract and Pipeline Activation selectors filter Table/Pipeline and Workspace in either order. Workspace appears at the far right; optional selections have no arbitrary defaults. New drafts capture current observation columns once and keep profile evidence separate.

- Configured blocking failures and checks that cannot execute prevent Live publication. Warn decisions, intentionally disabled checks, contract integrity, writer ownership, SCD and incremental safeguards remain enforced. Testing retains diagnostics without persistent data or metadata writes.
- Living Pipeline 02 and 02A–02C demos, contract inspection, glossary and current API guidance reflect contract-driven Guardrails. Frozen release references and notebook snapshots retain historical behavior.

## [0.2.5] - 2026-10-17

### Added

- Promoted `orchestrate_read()` and `orchestrate_write()` to the Live public API after validating full refresh, incremental append, and SCD write flows in Microsoft Fabric.

### Changed

- `profile_table()` enables frequency profiling by default (`frequency_enabled=True`) and limits each eligible column to five ranked values by default (`frequency_top_n=5`). Set `frequency_enabled=False` to disable profiling or `frequency_top_n=None` to retain all values.
- `setup_metadata_tables()` additively adds missing canonical metadata columns while preserving existing rows and extra columns.

### Fixed

- Corrected SCD2 effective-time validation, reused-activity reconciliation, and incremental target probing across governed writes.

### Metadata model

- Added identity and descriptive columns to metadata schemas, including readable table, column, and steward names. `setup_metadata_tables()` adds missing canonical columns while retaining existing rows and extra columns; incompatible canonical types and known legacy schemas still require explicit remediation.

### Notebook templates

- The full refresh, incremental append, and SCD demo flows passed manual Microsoft Fabric validation.

### Upgrade instructions

- Upgrade the Fabric Environment custom library to the v0.2.5 wheel and restart notebook sessions. Run `setup_metadata_tables()` against the configured metadata target to add missing canonical columns; existing rows and extra columns are preserved. Review `profile_table()` frequency defaults if your workflow expects frequency profiling to be disabled or a different top-N limit.

## [0.2.0] - 2026-09-22

### Added

- Expanded the supported FabricOps workflow from notebook setup and Fabric data movement to metadata setup, dataframe profiling, catalogue registration, normalized frequency evidence, and profiling lineage.

### Changed

- Promoted `setup_metadata_tables()` to the supported Live public API.
- Promoted `profile_table()` to the supported Live public API as the consolidated profiling entry point for ad hoc and governed table workflows.
- Promoted `read_lakehouse_json()` to the supported Live public API.
- Promoted `pipeline_read()`, `pipeline_write()`, and `resolve_table_id()` to the supported Live public API after Fabric validation of the current governed pipeline flow.
- Promoted `widget_render_data_steward()` and `widget_render_data_agreement()` to the supported Live public API after Fabric validation of the governance setup flow.
- Promoted Steward, Agreement, Catalogue, Profiled, Profiled Frequency, and Lineage metadata schemas to Live.

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

- Append pipeline behavior has been manually validated in Fabric. Other incremental strategies remain subject to compatible bug fixes within the supported `pipeline_write()` contract.

### Upgrade instructions

- Upgrade the Fabric Environment custom library to the v0.2.0 wheel.
- Restart notebook sessions after the Environment library update.
- Existing v0.1.0 Live read/write calls should remain compatible.
- Run `setup_metadata_tables()` in a development metadata Lakehouse after upgrading.
- Review failed-table results before recreating or migrating an incompatible existing table.
- Do not silently destroy existing metadata records.

## [0.1.0] - 2026-07-11

### Added

- Established the configuration-driven engineering starter workflow through the `00_env_config` notebook template, centralizing environment and Fabric item configuration used by the supported I/O functions.
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
