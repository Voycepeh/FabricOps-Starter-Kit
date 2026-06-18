# 00 Environment Configuration

`00_env_config` is the implementation guide for bootstrapping FabricOps in a Fabric workspace. It defines the active environment, validates the configured Fabric targets, and prepares the metadata tables used by the rest of the notebook handshake.

## Environment setup

Set `ENV` / `ENV_NAME` to the active environment key, such as `dev`, and keep that key aligned with `ENV_PATHS`. The notebook assembles `PathConfig`, `NotebookRuntimeConfig`, governance config, agreement config, and audit timezone into one `FrameworkConfig`.

The key setup helper is [`setup_notebook`](../api/reference/setup_notebook.md). It validates the runtime context, required target configuration, notebook naming/readiness checks, and returns the run context used by downstream cells.

## Workspace, lakehouse, metadata routing, and runtime configuration

`ENV_PATHS` maps logical targets such as `source`, `unified`, `product`, and `metadata` to `FabricStore` values. Each target carries workspace ID, item ID, item name, kind, schema settings, and environment.

Metadata must route through the configured `metadata` target. Do not rely on a default attached Lakehouse for metadata tables. Later helpers read and write metadata through the environment and `CONFIG.path_config.paths[ENV]["metadata"]`.

Runtime values such as audit timezone, schema-enabled Lakehouse settings, default schemas, metadata schema, required targets, and validation mode should stay visible in `00_env_config` so users can see what the workflow will do before they run agreement, pipeline, or governance notebooks.

## Metadata table setup

Use [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) to create missing FabricOps metadata tables and validate existing metadata structures in the configured metadata target. On first run it creates empty tables for agreement, notebook registry, catalogue, guardrail, lineage, pipeline run, and governance/enrichment metadata. It does not create business rows; `01_agreement`, `02_pipeline`, and `03_governance` populate those tables.

## Handoff to the next notebooks

When `00_env_config` finishes successfully, later templates receive:

- the active environment name;
- a validated `CONFIG`;
- configured source, unified, product, and metadata targets;
- metadata tables ready for agreement, pipeline, and governance evidence.
