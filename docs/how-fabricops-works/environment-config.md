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

Set `ENV` / `ENV_NAME` to the environment you are running, such as `dev`, `qat`, or `prd`.

This key must exist in `ENV_PATHS`.

### Fabric targets

`ENV_PATHS` maps each logical FabricOps target to a real Fabric item.

Typical targets are:

- `source`: where source data is read from;
- `unified`: where cleaned or conformed data may be written;
- `product`: where data product outputs may be written;
- `metadata`: where FabricOps metadata tables are stored.

Each target should define its workspace, item ID, item name, item kind, schema settings, and environment.

### Metadata routing

FabricOps metadata must write to the configured `metadata` target.

Do not depend on the default attached Lakehouse for metadata. Downstream helpers use the active environment and configured metadata target to read and write FabricOps tables.

### Runtime settings

Keep runtime settings visible in this notebook so users can review them before running the rest of the workflow.

This includes required targets, validation mode, notebook naming checks, schema settings, default schemas, metadata schema, and audit timezone.

### Agreement widget configuration

`00_env_config` is also the source of truth for reusable `01_agreement` widget configuration. Configure agreement intake through `DataAgreementConfig` rather than hardcoding widget choices in `01_agreement` or downstream notebooks.

Use this configuration area for:

- agreement metadata table names prepared by `setup_metadata_tables`;
- visible standard columns for the data steward and data agreement widgets;
- controlled dropdown values such as the data steward role options;
- custom steward and agreement metadata fields that should appear in the widgets.

Custom steward and agreement fields are captured by the widgets and stored in `custom_fields_json` on the relevant metadata table. They are reusable widget configuration, not new physical table columns.

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

- the active environment is known;
- `CONFIG` is available;
- source, unified, product, and metadata targets are validated;
- FabricOps metadata tables exist in the configured metadata target;
- downstream notebooks can safely write agreement, catalogue, guardrail, lineage, pipeline, governance, and enrichment evidence.
