# Step 0A: Prepare Fabric artifacts
Set up the Fabric items needed for the guided workflow.
This is expected to be done only once customised for your own fabric setup.

After completing this page, continue to [Step 00B: Set up the 00 env config file](00B-run-environment-setup.md) to configure and run `00_env_config`.

## What you will prepare

1. Workspaces
2. Lakehouses and Warehouses
3. Fabric Environment Object with FabricOps wheel
4. Template notebooks
5. Demo datasets & files

## 1. Create the Fabric workspaces

Open Microsoft Fabric and create or select a safe workspace for testing.

For the full governed workflow, prepare these workspaces

1. A governance workspace
2. A engineering development workspace
3. A engineeering production workspace

```
For demo purpose you can simply create a singular demo workspace.
```

## 2. Create the Lakehouse and Warehouses

1. Open The Governance workspace and create a lakehouse object name it 'METADATA'
2. Open The Engineering dev workspace and create a bronze lakehouse , a silver lakehouse and a gold warehouse - feel free to rename accordingly
3. Read up on medallion structure https://learn.microsoft.com/en-us/azure/databricks/lakehouse/medallion
4. Read up on lakehouse vs warehouse https://learn.microsoft.com/en-us/fabric/fundamentals/decision-guide-lakehouse-warehouse
5. Repeat step 2 for The Engineering prod workspace make sure the naming of the lakehouse and warehouse are exactly the same

```
For demo purpose you can simply create all these objects in the same demo workspace
in our case we simply renamed bronze - source , silver - unified , gold - product
```

![Fabric workspace setup example](../assets/00A/Objects.png)


## 3. Create a Fabric Environment and install the FabricOps whl file

1. Download the `.whl` file from the GitHub Release you want to use. ie `fabricops_kit-0.1.0-py3-none-any.whl`
2. Create a Fabric Environment
3. Open the Fabric Environment.
4. Go to **Custom libraries**.
5. Upload the `.whl` file.
6. Save or publish the Environment.

![Fabric custom wheel install example](../assets/00A/install-custom-whl.png)

## 4. Upload the notebook templates

Download the notebooks from the GitHub [`templates/notebooks`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) folder into the relevant Fabric workspaces.

| Notebook        | Purpose                                                                             |
| --------------- | ----------------------------------------------------------------------------------- |
| `00_env_config` | Configures workspaces, lakehouses, warehouse, metadata routing, and audit settings. |
| `01_governance` | Manages steward, agreement, contract, enrichment, guardrail, and review workflows.  |
| `02_pipeline`   | Processes data, profiles outputs, checks guardrails, and records evidence.          |
| `99_explore`    | Uses approved Production data for project exploration, AI, or BI work.              |

```
Suggested to keep prefix and add task or project name behind for your own use `01_governance_projectname` , `02_pipeline_emaildata`
```

## 5. Upload the data files that will be used in the guided demo

Download the notebooks from the GitHub [`templates/DemoData`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/DemoData) folder into the relevant Fabric workspaces.

 Demo Data        | Purpose                                                                             |
| --------------- | ----------------------------------------------------------------------------------- |
| `laptop_inventory_demo.csv` | A demo data that we will use throughout step 1-6 to showcas the full workflow of FabricOps |
| `demo.csv` | A simple demo data that we will use to show you can read from csv file |
| `demo.xlsx` | A simple demo data that we will use to show you can read from xlsx file |
| `demo.parquet` | A simple demo data that we will use to show you can read from parquet file |

## Expected result

You should now have:

* The required Fabric workspaces
* The required lakehouses and warehouses
* Fabric Environment with the FabricOps wheel installed
* Editable copies of the guided demo notebooks
* The demo data files so you can follow the guided demo directly

Next, continue to [Step 00B: Set up the 00 env config file](00B-run-environment-setup.md).
