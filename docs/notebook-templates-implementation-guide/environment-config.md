# 00 Environment Configuration

`00_env_config` is the control panel for a FabricOps workspace.

Run this notebook first in each environment. It tells FabricOps:

- which environment is active;
- where the source, unified, product, and metadata Lakehouses or Warehouses are;
- where FabricOps should write metadata;
- which runtime checks should be applied;
- which metadata tables must exist before the workflow continues.

Most downstream notebooks depend on this configuration. If `00_env_config` is wrong, agreement, pipeline, governance, and metadata writes may point to the wrong Fabric items.

## What you configure here

### Active environment

Set `ENV` to the environment you are running, such as `dev`, `qat`, or `prd`.

`ENV` is the only active environment key. It must exist in `ENV_PATHS`.

After `00_env_config` runs, downstream notebooks use the active FabricOps context exposed as:

- `FABRIC_CONTEXT["env"]` for the active environment;
- `FABRIC_CONTEXT["config"]` for the active FabricOps configuration.

### Fabric targets

`ENV_PATHS` maps each logical FabricOps target to a real Fabric item.

Typical targets are:

- `source`: where source data is read from;
- `unified`: where cleaned or conformed data may be written;
- `product`: where data product outputs may be written;
- `metadata`: where FabricOps metadata tables are stored.

Each target should define its workspace, item ID, item name, item kind, schema settings, and environment.

### Config objects

`00_env_config` keeps the main configuration objects visible and editable:

- `RUNTIME_CONFIG`: notebook naming, validation, required-target, schema, and audit settings;
- `PATH_CONFIG`: environment-specific Fabric target routing from `ENV_PATHS`;
- `DATA_AGREEMENT_CONFIG`: reusable `01_agreement` widget and table setup;
- `GOVERNANCE_CONFIG`: reusable `03_governance` review and enrichment setup;
- `CONFIG`: the combined FabricOps configuration passed to setup helpers and exposed through `FABRIC_CONTEXT["config"]`.

### Metadata routing

FabricOps metadata must write to the configured `metadata` target.

Do not depend on the default attached Lakehouse for metadata. Downstream helpers use `FABRIC_CONTEXT["env"]` and `FABRIC_CONTEXT["config"]` to read and write FabricOps tables through the configured metadata target.

### Agreement configuration

`DATA_AGREEMENT_CONFIG` controls `01_agreement` table names, data steward role options, visible widget columns, and widget `custom_fields`.

Custom steward and agreement fields are captured by the widgets and stored in `custom_fields_json` on the relevant metadata table. They are reusable widget configuration, not new physical table columns.

### Governance configuration

`GOVERNANCE_CONFIG` controls `03_governance` sensitivity labels, PII classifications, and enrichment widget `custom_fields`.

Use `enrichment_context_widget` and `enrichment_classification_widget` to configure enrichment widgets. Each widget can define `custom_fields` that are captured with the governance review evidence.

## What this notebook does

`00_env_config` uses [`setup_notebook`](../api/reference/setup_notebook.md) to validate the notebook runtime and configured targets.

It then uses [`setup_metadata_tables`](../api/reference/setup_metadata_tables.md) to create missing FabricOps metadata tables and validate existing ones in the configured metadata target.

On first run, this prepares the empty metadata structures needed by the rest of the workflow.

It does not create business evidence rows. Those are written later by:

- `01_agreement`;
- `02_pipeline`;
- `03_governance`.

## What should be true before moving on

After this notebook runs successfully:

- the active environment is known through `FABRIC_CONTEXT["env"]`;
- `CONFIG` is available through `FABRIC_CONTEXT["config"]`;
- source, unified, product, and metadata targets are validated;
- FabricOps metadata tables exist in the configured metadata target;
- downstream notebooks can safely write agreement, catalogue, guardrail, lineage, pipeline, governance, and enrichment evidence.

## Related navigation

Use the Function Reference when you need callable-level details for `setup_notebook` or `setup_metadata_tables`; the inline links above remain direct because this page is already explaining those exact setup calls.

[Back to Template Notebooks](index.md){ .md-button } [View Function Reference](../reference/index.md){ .md-button }
