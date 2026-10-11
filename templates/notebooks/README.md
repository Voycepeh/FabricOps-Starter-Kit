# Notebook templates

Download these notebooks and import them into Microsoft Fabric.

| Notebook | Purpose |
| --- | --- |
| `00_env_config.ipynb` | Configure environments and Fabric stores. |
| `01_governance.ipynb` | Manage Governance metadata and Data Contracts. |
| `02_pipeline.ipynb` | Reusable governed Read → PySpark Transform → Write scaffold. |
| `99_explore.ipynb` | Explore approved Production data. |

Completed learning demos are kept separately under `templates/DemoData/`:

| Demo notebook | Purpose |
| --- | --- |
| `02A_full_refresh_demo.ipynb` | Orders, Products, and Order History Full → Overwrite example. |
| `02B_incremental_append_demo.ipynb` | Multi-day inventory Incremental → Append example. |
| `02C_scd_demo.ipynb` | Multi-day Product Master SCD1 and SCD2 example. |

> **Multiple Write blocks:** each `orchestrate_write()` publishes independently. If an earlier Write succeeds and a later Write fails, the pipeline is partially published. A retry runs the earlier Write again, which can duplicate or otherwise repeat non-idempotent writes such as Append. If partial publication or duplicate writes are unacceptable, use separate pipeline executions for each governed target.

For the end-to-end workflow, follow the [Guided Demo](https://voycepeh.github.io/FabricOps-Starter-Kit/guided-demo/).
