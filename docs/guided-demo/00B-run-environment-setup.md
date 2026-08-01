# Step 0B: Set up the operating environment

After completing [Step 0A: Prepare Fabric artifacts](00A-setup-fabric-artifacts.md), configure and run `00_env_config`.

`00_env_config` controls the settings used by the other FabricOps notebooks, including:


* Path to other workspace 
* Path to Fabric objects
* Runtime settings
* Widget settings


Run it in the Governance, Engineering Development, and Engineering Production workspaces.

## 1. Open `00_env_config`

Open the copied `00_env_config` notebook in the target workspace.

Before running it, confirm that the notebook uses the Fabric Environment containing the FabricOps wheel.

## 2. Attach the Fabric Environment

Attach the same Fabric Environment to each template notebook.

1. Open the notebook.
2. Select the Fabric Environment containing the FabricOps wheel.
3. Restart the notebook session after changing the Environment or its libraries.

You can skip this step when the workspace default Environment already contains the correct FabricOps package.

![Fabric notebook Environment selection example](../assets/00B/fabric-example-set-notebook-environment.png)

## 3. Configure Fabric item paths

Update `ENV_PATHS` for the active environment.

Via clicking on the lakehouse/warehouse and seeing the url ie 
https://app.powerbi.com/groups/68fa4319-1945-458f-bd21-05334c51cbb4/lakehouses/329b3989-4546-4331-b9ff-df898d49ee73

workspace id : 68fa4319-1945-458f-bd21-05334c51cbb4
item id: 329b3989-4546-4331-b9ff-df898d49ee73
name : Metadata
kind : lakehouse 

![Path config](../assets/00B/00_config_paths.png)


```
Why do we even bother with this? 

As per writing this Fabric notebook can only have one default lakehouse/warehouse connected to it at one point of time so when we need to read and write from one place to another we need to resort to coding , but hard coding the exact path in every notebook is bad coding practice so we define a singlar config file similar to a .yml but using a fabric notebook.
```

## 4. Widget settings

Change these settings only when you need different:

* dropdown options for predefined fields 
* additional custom fields

Custom fields are stored as JSON in a cell. They do not create additional physical table columns.

![Widget config](../assets/00B/00_config_widgets_config_setup.png)

## 5. Set up metadata tables

Complete this step in the Governance workspace.

1. Confirm that the `metadata` target points to the correct metadata lakehouse.
2. Run the metadata setup cell.
3. Allow the setup to create or validate the required metadata tables.
4. Leave the setup cell unchanged during normal guided demo runs.

![Setup Metadata Tables](../assets/00B/00_config_metadata_tables_setup_code.png)


The cell should complete without errors and confirm that the metadata tables are ready.

![Metadata Tables Done](../assets/00B/Metadata-Tables-Created.png)

## 6. Resuable Context is prepared for downstream function usage
![For Downstream Usage](../assets/00B/00_config_resuable_context.png)

## Expected result

00 env config is ready when:

* the Fabric Environment is attached
* the FabricOps package can be imported
* runtime and path settings are configured
* required metadata tables have been created or validated
* `FABRIC_CONTEXT["env"]` and `FABRIC_CONTEXT["config"]` are available

Previous: [Step 0A: Prepare Fabric artifacts](00A-setup-fabric-artifacts.md).

Next: [Step 1: Create data stewards and a data agreement](01-create-agreement.md).
