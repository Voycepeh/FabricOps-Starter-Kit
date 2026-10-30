<!-- Generated file. Edit docs/releases/manifests/0.3.0.yml or the authoritative source metadata and regenerate. -->

# FabricOps Starter Kit 0.3.0

- Package version: `0.3.0`
- Release status: <span class="fabricops-release-status fabricops-release-status--live">Live</span>
- Release date: `2026-10-30`

<a class="md-button md-button--primary" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/tag/v0.3.0">
  View GitHub Release
</a>

## Formal release scope

<details class="fabricops-release-inventory" markdown>
<summary>20 Live functions</summary>

| Function | Description |
| --- | --- |
| [`finalize_pipeline`](functions/finalize_pipeline.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Finalize a Dry Run, Ungoverned or Governed execution accurately. |
| [`setup_pipeline`](functions/setup_pipeline.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Start an isolated pipeline in Dry Run, Ungoverned or Governed mode. |
| [`orchestrate_read`](functions/orchestrate_read.md) | Read a source using the active pipeline's contracts and runtime. |
| [`orchestrate_write`](functions/orchestrate_write.md) | Evaluate or publish a target using the active pipeline's runtime. |
| [`pipeline_read`](functions/pipeline_read.md) | Read one governed pipeline source through the appropriate Fabric store. |
| [`profile_table`](functions/profile_table.md) | Profile a Spark DataFrame or a complete governed physical table. |
| [`read_lakehouse_csv`](functions/read_lakehouse_csv.md) | Read CSV files from a configured Lakehouse Files location. |
| [`read_lakehouse_excel`](functions/read_lakehouse_excel.md) | Read an Excel workbook from a configured Fabric-resolved path. |
| [`read_lakehouse_json`](functions/read_lakehouse_json.md) | Read JSON data from a configured Lakehouse ``Files`` path through Spark. |
| [`read_lakehouse_parquet`](functions/read_lakehouse_parquet.md) | Read Parquet data from the configured Lakehouse ``Files`` area through Spark. |
| [`read_lakehouse_table`](functions/read_lakehouse_table.md) | Read a configured Lakehouse Delta table as a lazy Spark DataFrame. |
| [`read_warehouse_query`](functions/read_warehouse_query.md) | Execute a read-only Warehouse SQL query and return the query result. |
| [`read_warehouse_table`](functions/read_warehouse_table.md) | Read every row and every column from a Microsoft Fabric Warehouse table. |
| [`resolve_table_id`](functions/resolve_table_id.md) | Return the canonical table identity for configured physical coordinates. |
| [`setup_metadata_tables`](functions/setup_metadata_tables.md) | Create or check the FabricOps metadata tables for one workspace_id. |
| [`setup_notebook`](functions/setup_notebook.md) | Validate notebook startup configuration and resolve required Fabric targets. |
| [`widget_render_data_agreement`](functions/widget_render_data_agreement.md) | Render a wide, single-flow data-agreement editor. |
| [`widget_render_data_steward`](functions/widget_render_data_steward.md) | Render append-only data steward create/update maintenance. |
| [`write_lakehouse_table`](functions/write_lakehouse_table.md) | Write a Spark DataFrame to a configured Fabric lakehouse Delta table. |
| [`write_warehouse_table`](functions/write_warehouse_table.md) | Write a Spark DataFrame to a configured Fabric Warehouse table. |

</details>

<details class="fabricops-release-inventory" markdown>
<summary>11 Live metadata tables</summary>

| Metadata table | Purpose |
| --- | --- |
| [`METADATA_DATA_CONTRACT`](metadata/metadata_data_contract.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for data contract. |
| [`METADATA_GUARDRAIL_RESULTS`](metadata/metadata_guardrail_results.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for guardrail results. |
| [`METADATA_PIPELINE_REGISTRY`](metadata/metadata_pipeline_registry.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for pipeline registry. |
| [`METADATA_PIPELINE_RUN`](metadata/metadata_pipeline_run.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for pipeline run. |
| [`METADATA_PROCESSING_STATE`](metadata/metadata_processing_state.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | Supported FabricOps metadata table for processing state. |
| [`METADATA_DATA_CATALOGUE`](metadata/metadata_data_catalogue.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data catalogue. |
| [`METADATA_DATA_LINEAGE`](metadata/metadata_data_lineage.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data lineage. |
| [`METADATA_DATA_PROFILED`](metadata/metadata_data_profiled.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data profiled. |
| [`METADATA_DATA_PROFILED_FREQUENCY`](metadata/metadata_data_profiled_frequency.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Supported FabricOps metadata table for data profiled frequency. |
| [`METADATA_DATA_AGREEMENT`](metadata/metadata_data_agreement.md) | Supported FabricOps metadata table for data agreement. |
| [`METADATA_DATA_STEWARD`](metadata/metadata_data_steward.md) | Supported FabricOps metadata table for data steward. |

</details>

## Changelog

### Breaking changes

- Establish workspace-ID-based configuration and routing as the new architectural baseline. Earlier package versions (v0.2.5 and before) are superseded and must not be combined with v0.3.0 notebook templates.
- Existing legacy environment-keyed metadata layouts are not automatically migrated. Use a fresh workspace-model metadata installation; preserve existing Live metadata until an explicit migration is approved.
- Replace environment-keyed configuration with workspace-keyed paths. `FabricStore.env`, `setup_notebook(env=...)`, `setup_metadata_tables(env=...)`, scanner `environment_name` arguments and returned environment fields are removed/replaced. Ordinary no-argument setup and orchestration calls retain their calling patterns.
- Replace the Live `pipeline_write()` public entry point with `orchestrate_write()`. The orchestration entry point owns contract selection, Guardrail execution, publication, and final execution evidence.
- Remove the separate Coverage Gate stage and `coverage_result` return field from `orchestrate_write()`. Both orchestrators use selected Data Contract Guardrails; no minimum active-check count is required.
- Contract column definitions enforce required presence by default, explicit optional presence, and exact normalized data types. Unexpected columns block, and structural Schema checking is mandatory.

### Metadata lifecycle

- Promote `METADATA_DATA_CONTRACT`, `METADATA_GUARDRAIL_RESULTS`, `METADATA_PIPELINE_REGISTRY`, `METADATA_PIPELINE_RUN`, and `METADATA_PROCESSING_STATE` to Live in v0.3.0. These form supported governance, guardrail-result, registration, execution, and processing-state persistence contracts. `METADATA_DATA_ACCESS` remains Preview. Live schemas may evolve additively; breaking structural changes require an explicit migration.
- Discontinue the Preview `METADATA_ENRICHMENT` and `METADATA_GUARDRAIL` contracts in favor of authored Enrichment and executable Guardrails in `METADATA_DATA_CONTRACT.contract_payload_json`.
- Discontinue the Preview `METADATA_SOURCE_OBSERVATION` contract in favor of typed source observations, accepted progress, Source Drift baselines, and publication receipts in `METADATA_PROCESSING_STATE`.

### Pipeline execution

- Introduce Dry Run, Ungoverned, and Governed execution paths, with Live `setup_pipeline()` and `finalize_pipeline()` lifecycle entry points and workspace-scoped governance behaviour.
- Freeze matching `00_env_config` and `02_pipeline` notebook templates for this release.

### Removed

- Remove the standalone `check_schema()`, `check_freshness()`, `check_source_drift()`, `check_dq()`, `check_sensitive_data()`, and `check_guardrail_coverage()` public surfaces. The applicable checks remain internal execution stages of `orchestrate_read()` and `orchestrate_write()`.
- Remove the Preview `widget_activate_data_contract()` and `widget_select_data_contract()` surfaces in favor of pipeline setup, Data Contract selection, and pipeline activation workflows.
- Remove the Preview Data Catalogue Viewer widget and the optional exploration notebook template. Query centralized metadata directly through PySpark or SQL, and use native Fabric interfaces or project-specific notebooks for consumption.

### Changed

- **Observe locally → Govern globally → Test locally → Activate locally.** Data Contract histories remain global per table ID. Governance selects workspace evidence; different workspaces can independently activate different frozen versions. New profiles never alter contracts.
- Data Contract and Pipeline Activation selectors filter Table/Pipeline and Workspace in either order. Workspace appears at the far right; optional selections have no arbitrary defaults. New drafts capture current observation columns once and keep profile evidence separate.
- Configured blocking failures and checks that cannot execute prevent Live publication. Warn decisions, intentionally disabled checks, contract integrity, writer ownership, SCD and incremental safeguards remain enforced. Testing retains diagnostics without persistent data or metadata writes.
- Living Pipeline 02 and 02A–02C demos, contract inspection, glossary and current API guidance reflect contract-driven Guardrails. Frozen release references and notebook snapshots retain historical behavior.

### Upgrade instructions

- Upgrade the package and both notebook templates together. Do not mix v0.3.0 notebooks with v0.2.5 or earlier packages.
- Use a fresh workspace-model metadata installation; no automatic migration or compatibility aliases are supplied for legacy environment-keyed metadata.
- Replace direct `pipeline_write()` calls with `orchestrate_write()` and consume the orchestrator's stage and finalization results.
- Validate full refresh, incremental append, and SCD demo workflows in Microsoft Fabric before publishing.
