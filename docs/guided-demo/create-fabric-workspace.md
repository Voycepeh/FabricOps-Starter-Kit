# Create Fabric Workspace

Create or choose the Microsoft Fabric workspace that will host the copied demo notebooks and runtime items. This step uses the FabricOps wheel created in [Create Wheel](create-wheel.md).

## What to do

1. Open Microsoft Fabric.
2. Create a workspace for the demo, or choose an existing safe workspace.
3. Create or select a Fabric Environment for the notebooks.
4. Upload the FabricOps wheel created in the previous step to the Environment by following [Install](../install.md).
5. Copy the notebook templates from `templates/notebooks` into the workspace.
6. Attach the Environment to each copied notebook and save the notebooks.

## Expected result

The workspace contains editable copies of `00_env_config`, `01_agreement`, `example_pipeline_demo`, `02_pipeline`, `03_governance`, and `99_explore`, and at least one notebook can import `fabricops_kit`.

Next, continue to [Create Lakehouses / Warehouse](create-lakehouses-warehouse.md). For the detailed role of each notebook, see [Template Notebooks](../how-fabricops-works/notebook-templates/index.md).
