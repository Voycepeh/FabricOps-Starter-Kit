# Step 0B: Set up the operating environment

**Configure `00_env_config` so every FabricOps notebook can resolve the correct workspace, Fabric items, runtime settings, widgets, and metadata target.**

Complete [Step 0A: Prepare Fabric artifacts](00A-setup-fabric-artifacts.md) first.

!!! info "Key concepts for this step"

    [**Configuration**](../glossary.md#configuration) — named settings that control environment targets, processing choices, and runtime behaviour.  
    [**Configuration-driven Engineering**](../glossary.md#configuration-driven-engineering) — reusable engineering behaviour controlled through configuration rather than rewritten code.  
    [**Notebook**](../glossary.md#notebook) — the Fabric document used to run the FabricOps setup and workflow code.

    These are the only glossary concepts you need before starting this step.

## High-level flow

```text
Open config → Attach Environment → Configure paths → Review widgets → Set up metadata → Reuse context
```

???+ success "Live — Open `00_env_config`"

    Open the copied `00_env_config` notebook in the target workspace. Run it in Governance, Engineering Development, and Engineering Production.

    FabricOps keeps environment configuration in a notebook so downstream notebooks can load the configured context naturally through `%run 00_env_config` rather than introducing a separate YAML or file-parsing step.

???+ success "Live — Attach the Fabric Environment"

    1. Open the notebook.
    2. Select the Fabric Environment containing the FabricOps wheel.
    3. Restart the notebook session after changing the Environment or its libraries.

    You can skip this when the workspace default Environment already contains the correct FabricOps package.

    ![Fabric notebook Environment selection example](../assets/00B/fabric-example-set-notebook-environment.png)

???+ success "Live — Configure Fabric item paths"

    Update `ENV_PATHS` for the active environment so FabricOps can resolve the required workspaces and Fabric items.

    A Fabric item URL contains the workspace ID and item ID, which can be used to populate the configuration.

    ![Path config](../assets/00B/00_config_paths.png)

    !!! note "Why this configuration exists"

        A Fabric notebook works naturally with its attached/default item, but a real pipeline may need several Lakehouses, Warehouses, or workspaces. Without central configuration, those cross-item reads and writes can push physical OneLake paths, workspace IDs, and item IDs into individual `02_pipeline` notebooks.

        FabricOps centralises those environment-specific identities in `00_env_config`. The `02_pipeline` keeps logical target names while the FabricOps I/O functions resolve the correct Development or Production item at runtime. That means promotion does not require rewriting paths in every pipeline, and replacing or adding a Fabric item can be handled in the environment configuration instead of across many notebooks.

        Read the deeper rationale in the [FabricOps Engineering Guide — Config-driven engineering and why FabricOps has I/O functions](../reference/engineering-cheat-sheet.md#config-driven-engineering-and-why-fabricops-has-io-functions).

???+ success "Live — Review widget settings"

    Change widget settings only when you need different dropdown options or additional custom fields.

    Custom fields are stored as JSON and do not create additional physical table columns.

    ![Widget config](../assets/00B/00_config_widgets_config_setup.png)

???+ success "Live — Set up metadata tables"

    Complete this block in the Governance workspace.

    1. Confirm that the `metadata` target points to the correct metadata Lakehouse.
    2. Run the metadata setup cell.
    3. Allow the setup to create or validate the required metadata tables.
    4. Leave the setup cell unchanged during normal Guided Demo runs.

    ![Setup Metadata Tables](../assets/00B/00_config_metadata_tables_setup_code.png)

    The cell should complete without errors and confirm that the metadata tables are ready.

    ![Metadata Tables Done](../assets/00B/Metadata-Tables-Created.png)

???+ success "Live — Confirm reusable context"

    `00_env_config` prepares reusable context for downstream FabricOps functions and notebooks.

    ![For Downstream Usage](../assets/00B/00_config_resuable_context.png)

## Expected result

`00_env_config` is ready when the Fabric Environment is attached, package imports work, paths and runtime settings are configured, metadata tables exist, and `FABRIC_CONTEXT["env"]` plus `FABRIC_CONTEXT["config"]` are available.

**Previous:** [Step 0A: Prepare Fabric artifacts](00A-setup-fabric-artifacts.md)  
**Next:** [Step 1: Create Data Stewards and Data Agreements](01-create-agreement.md)
