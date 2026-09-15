# 0A. Prepare the Fabric artifacts

**Create the Fabric items and upload the files the Guided Demo will use.**

This is foundation setup, not one of the seven lifecycle steps.

## Create the Fabric items

For the full operating model, prepare:

1. Governance workspace with a metadata Lakehouse.
2. Engineering Development workspace.
3. Engineering Production workspace.
4. Source Lakehouse.
5. Unified Lakehouse.
6. Product Warehouse.
7. Fabric Environment for the FabricOps wheel.

For a lightweight learning run, these items can live in one workspace. Keep the logical store names used by the walkthrough so the supplied notebook variables remain easy to follow.

![Fabric workspace setup example](../assets/00A/Objects.png)

## Install FabricOps

Download the release wheel you are testing, add it to the Fabric Environment under **Custom libraries**, publish the Environment, and attach it to the walkthrough notebooks.

![Fabric custom wheel install example](../assets/00A/install-custom-whl.png)

## Copy the notebook templates

Use the current notebooks from `templates/notebooks`:

| Notebook | Guided Demo role |
| --- | --- |
| `00_env_config` | Shared environment and Fabric-store configuration. |
| `01_governance` | Steward, agreement, Data Contract authoring, freezing, and activation. |
| `02_pipeline` | Full-read Engineering workflow used in Development and Production. |
| `99_explore` | Read-oriented consumer and exploration support. |

## Upload the demo files

Upload the files from `templates/DemoData` to the Source Lakehouse under `Files/DemoData/`.

The main walkthrough uses:

| File | Role |
| --- | --- |
| `orders.csv` | Day 1 Orders baseline: 120 rows. |
| `orders_incremental.csv` | Day 2 arrival: 12 later Orders rows. Keep this separate until the walkthrough asks for it. |
| `products.csv` | Product reference data. |
| `order_history.csv` | Historical customer/order context. |

The other Orders formats and negative fixtures remain useful for I/O or release testing, but they are not required for the main seven-step story.

## Expected result

You now have the Fabric workspaces and stores, the FabricOps Environment, editable copies of the four notebooks, and the raw demo files available in the Source Lakehouse.

**Next:** [0B. Configure the environment and load demo data](00B-run-environment-setup.md)
