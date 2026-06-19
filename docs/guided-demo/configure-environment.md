# Configure Environment

Run `00_env_config` first so every later notebook uses the same environment routes, metadata target, and audit settings.

## What to do

1. Confirm you completed [Setup Fabric Workspace](setup-fabric-workspace.md).
2. Edit `00_env_config` with public-safe workspace, lakehouse, warehouse, schema, and environment values.
3. Run the cells that build `CONFIG`, `ENV`, and the metadata table registry.

## Expected evidence

The configured metadata lakehouse contains the implemented `METADATA_*` tables, and downstream notebooks can reuse the same `CONFIG` and `ENV` values.

See also: [Setup Fabric Workspace](setup-fabric-workspace.md), [Install](../install.md), [Create Wheel](../setup/create-wheel.md), and [List of Metadata Tables](../reference/metadata-tables/index.md).
