# Run Environment Setup

Run `00_env_config` first in each Fabric workspace. It is the control panel for the guided demo and for later governed workflows: every downstream notebook depends on its active `ENV`, shared `CONFIG`, Fabric item routes, metadata target, runtime validation choices, widget configuration, and audit settings.

## 1. Open `00_env_config`

Open the copied `00_env_config` template after uploading the template notebooks to your workspace. Attach the same Fabric Environment that contains the FabricOps wheel before running setup cells.

## 2. Attach the Environment to notebooks

Attach the Environment to every template notebook unless your workspace already has a default Environment with the FabricOps library installed. Restart the notebook session after attachment or library changes so the runtime loads the published Environment.

![Microsoft Fabric notebook Environment menu with a published FabricOps Environment selected](../assets/fabric-example-set-notebook-environment.png)

*Select the published FabricOps Environment from the notebook toolbar before running the workspace's `00_env_config` notebook.*

## 3. Set runtime configuration

Review the visible `RUNTIME_CONFIG` values. These control notebook naming, validation behavior, required target checks, schema defaults, timezone handling, and audit values that helpers write with metadata rows.

![The runtime configuration cell defining audit timezone, Lakehouse schema routing, and validation mode](../assets/fabric-example-00_config_runtime_config.png)

*Review environment-specific runtime values before the shared configuration is consumed by downstream notebook templates.*

## 4. Set path configuration

Update `ENV_PATHS` for the active environment. Each logical target, such as `source`, `unified`, `product`, and `metadata`, should point to the correct Fabric workspace item, item kind, schema, and environment.

Metadata operations must use the configured `metadata` target from `00_env_config`; do not rely on the notebook's attached or default Lakehouse for `METADATA_*` tables.

## 5. Review widget-specific configuration

Edit `DATA_AGREEMENT_CONFIG` and `GOVERNANCE_CONFIG` only where the demo or your team needs different dropdown values, visible columns, or reusable custom fields. Custom steward, agreement, and governance fields are stored in JSON metadata columns; they do not create new physical metadata table columns.

## 6. Create or validate metadata tables

Run the metadata setup cell once for the configured metadata target, then freeze or leave the cell unchanged for routine demo runs. The setup validates required environment keys and creates or validates the metadata tables needed by agreement, pipeline, governance, lineage, and run evidence.

![The metadata setup call using the shared Spark session, configured environment, metadata schema, and FabricOps configuration](../assets/fabric-example-00_config_metadata_tables_setup_code.png)

*Run the setup call against the configured Governance metadata target to initialize or validate the metadata tables required by the installed release.*

## Expected result

After `00_env_config` succeeds, `FABRIC_CONTEXT["env"]` and `FABRIC_CONTEXT["config"]` are available, source/unified/product/metadata targets are validated, and downstream notebooks can safely route agreement, catalogue, guardrail, lineage, pipeline, governance, and enrichment evidence through the configured metadata target.

Next, continue to [Create Agreement](create-agreement.md). If you want to smoke-test configured IO targets before agreement registration, run [Run exploration notebook template](run-io-and-profiling-demo.md).
