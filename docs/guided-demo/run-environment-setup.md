# Run Environment Setup

Run `00_env_config` after editing the demo settings.

## What to do

1. Open the copied `00_env_config` notebook.
2. Confirm the selected environment and item names are correct.
3. Run the setup cells that create the shared `CONFIG` and `ENV` values.
4. Run metadata setup so the configured metadata target has the required `METADATA_*` tables.
5. Leave the notebook available so later notebooks can reuse the same settings.

## Expected evidence

The configured metadata lakehouse contains the implemented `METADATA_*` tables, and downstream notebooks can use the same `CONFIG` and `ENV` values.

For all editable and advanced `00_env_config` settings, see [Template Notebooks](../how-fabricops-works/notebook-templates.md#00_env_config).
