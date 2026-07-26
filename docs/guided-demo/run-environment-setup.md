# Step 0B: Set up the operating environment

After completing [Step 0A: Prepare Fabric artifacts](setup-fabric-artifacts.md), run `00_env_config` in the Governance, Engineering Development, and Engineering Production workspaces. It is the control panel for the governed workflow: every downstream notebook depends on its active `ENV`, shared `CONFIG`, Fabric item routes, metadata target, runtime validation choices, widget configuration, and audit settings.

## 1. Open `00_env_config`

Open the copied `00_env_config` template after uploading the template notebooks to your workspace. Attach the same Fabric Environment that contains the FabricOps wheel before running setup cells.

## 2. Attach the Environment to notebooks

Attach the Environment to every template notebook unless your workspace already has a default Environment with the FabricOps library installed. Restart the notebook session after attachment or library changes so the runtime loads the published Environment.

![Fabric notebook Environment selection example](../assets/fabric-example-set-notebook-environment.png)

## 3. Set runtime configuration

Review the visible `RUNTIME_CONFIG` values. These control notebook naming, validation behavior, required target checks, schema defaults, timezone handling, and audit values that helpers write with metadata rows.

![Runtime config](../assets/fabric-example-00_config_runtime_config.png)

## 4. Set path configuration

Update `ENV_PATHS` for the active environment. Each logical target, such as `source`, `unified`, `product`, and `metadata`, should point to the correct Fabric workspace item, item kind, schema, and environment.

Metadata operations must use the configured `metadata` target from `00_env_config`; do not rely on the notebook's attached or default Lakehouse for `METADATA_*` tables.

![Path config](../assets/fabric-example-00_config_paths.png)

## 5. Review widget-specific configuration

Edit `DATA_AGREEMENT_CONFIG` and `GOVERNANCE_CONFIG` only where the demo or your team needs different dropdown values, visible columns, or reusable custom fields. Custom steward, agreement, and governance fields are stored in JSON metadata columns; they do not create new physical metadata table columns.

![Widget config](../assets/fabric-example-00_config_widgets_config_setup.png)

## 6. Create or validate metadata tables in Governance

In the Governance workspace, run the metadata setup cell once for the configured metadata target, then freeze or leave the cell unchanged for routine demo runs. The setup validates required environment keys and creates or validates the metadata tables needed by agreement, pipeline, governance, lineage, and run evidence.

![Setup Metadata Tables](../assets/fabric-example-00_config_metadata_tables_setup_code.png)

Completed creation of the tables:

![Metadata Tables Done](../assets/fabric-example-00_config_metadata_tables_setup.png)

## Expected result

After `00_env_config` succeeds, `FABRIC_CONTEXT["env"]` and `FABRIC_CONTEXT["config"]` are available, source/unified/product/metadata targets are validated, and downstream notebooks can safely route agreement, catalogue, guardrail, lineage, pipeline, governance, and enrichment evidence through the configured metadata target.

Previous: [Step 0A: Prepare Fabric artifacts](setup-fabric-artifacts.md).

Next, continue to [Step 1: Create data stewards and a data agreement](create-agreement.md).
