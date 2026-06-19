# Configure Environment

Edit `00_env_config` before running setup so every later notebook uses the same environment routes, metadata target, validation behavior, and audit settings.

## What to do

1. Confirm you created the workspace and data items from [Create Fabric Workspace](create-fabric-workspace.md) and [Create Lakehouses / Warehouse](create-lakehouses-warehouse.md).
2. Open the copied `00_env_config` notebook.
3. Enter the demo environment name, workspace item names, lakehouse or warehouse names, schemas, and metadata routing values.
4. Review runtime validation and audit settings.
5. Keep the default demo table names for your first run.

## Expected result

`00_env_config` is ready to run, but no later notebook should run until [Run Environment Setup](run-environment-setup.md) completes.

For the complete `00_env_config` reference, see [Template Notebooks](../how-fabricops-works/notebook-templates.md#00_env_config).
