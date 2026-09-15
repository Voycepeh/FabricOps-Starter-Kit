# `00_env_config`: configure the operating environment

**Use `00_env_config` to define the reusable Fabric context that Governance, Engineering Development, Engineering Production, and optional exploration notebooks load with `%run 00_env_config`.**

This is the setup layer. It should contain environment-specific Fabric wiring, not project transformation logic.

## 1. Prepare the Fabric items

For the full operating pattern, prepare:

- Governance workspace with the metadata Lakehouse,
- Engineering Development workspace,
- Engineering Production workspace,
- Source and Unified Lakehouses,
- Product Warehouse,
- Fabric Environment containing the FabricOps wheel.

For a lightweight demo, the items can live in one workspace. Keep the same logical store names so the notebook examples remain easy to follow.

![Fabric workspace setup example](../assets/00A/Objects.png)

## 2. Install FabricOps in the Fabric Environment

1. Download the FabricOps `.whl` for the release you are testing.
2. Open the Fabric Environment.
3. Add the wheel under **Custom libraries**.
4. Save or publish the Environment.
5. Attach that Environment to the FabricOps notebooks.

![Fabric custom wheel install example](../assets/00A/install-custom-whl.png)

Restart a notebook session after changing its Environment or custom libraries.

## 3. Copy the current notebook templates

Use the notebooks from [`templates/notebooks`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks):

| Notebook | Role |
| --- | --- |
| `00_env_config` | Shared environment and Fabric-store configuration. |
| `01_governance` | Steward, agreement, Data Contract authoring, freezing, and activation. |
| `02_pipeline` | Full-read governed engineering pipeline. |
| `99_explore` | Optional exploration and troubleshooting support. |

Keep `00_env_config` available under the same notebook name when using the supplied templates because the other notebooks load it with `%run 00_env_config`.

## 4. Configure logical Fabric stores

Open `00_env_config` and update the environment-specific paths and item identities used by your deployment.

The supplied walkthrough uses these logical names:

- `metadata` for the Governance metadata Lakehouse,
- `source` for governed input data,
- `unified` for curated Lakehouse outputs,
- `product` for Warehouse data.

![Path config](../assets/00B/00_config_paths.png)

The important idea is that project notebooks refer to logical store names. Workspace IDs, item IDs, OneLake paths, and environment-specific routing stay centralized here.

## 5. Create or validate the metadata tables

In the Governance context:

1. Confirm the `metadata` target points to the intended metadata Lakehouse.
2. Run the metadata setup cell in `00_env_config`.
3. Allow FabricOps to create or validate the required metadata tables.

![Setup Metadata Tables](../assets/00B/00_config_metadata_tables_setup_code.png)

![Metadata Tables Done](../assets/00B/Metadata-Tables-Created.png)

## 6. Upload and seed the demo data

Upload the supplied files from [`templates/DemoData`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/DemoData) to the Source Lakehouse.

For the main Orders walkthrough, prepare these managed tables before opening `02_pipeline`:

```text
Source Lakehouse
  demo.orders
  demo.products

Product Warehouse
  demo.order_history
```

A simple setup notebook can load the raw files with the foundational FabricOps readers and write the managed tables with `write_lakehouse_table()` and `write_warehouse_table()`. This setup is intentionally separate from `02_pipeline`: the governed pipeline starts from managed Fabric tables with stable table identities.

For example, after `%run 00_env_config`:

```python
from fabricops_kit import (
    read_lakehouse_csv,
    write_lakehouse_table,
    write_warehouse_table,
)

orders_df = read_lakehouse_csv(
    "DemoData/orders.csv",
    store="source",
    spark_session=spark,
    header=True,
    inferSchema=True,
)

products_df = read_lakehouse_csv(
    "DemoData/products.csv",
    store="source",
    spark_session=spark,
    header=True,
    inferSchema=True,
)

order_history_df = read_lakehouse_csv(
    "DemoData/order_history.csv",
    store="source",
    spark_session=spark,
    header=True,
    inferSchema=True,
)

write_lakehouse_table(
    orders_df,
    "orders",
    store="source",
    schema="demo",
    mode="overwrite",
)

write_lakehouse_table(
    products_df,
    "products",
    store="source",
    schema="demo",
    mode="overwrite",
)

write_warehouse_table(
    order_history_df,
    "demo",
    "order_history",
    store="product",
    mode="overwrite",
)
```

## Expected result

`00_env_config` is ready when:

- the Fabric Environment imports FabricOps successfully,
- logical stores resolve to the intended Fabric items,
- the metadata tables exist,
- downstream notebooks can load the shared context with `%run 00_env_config`,
- the three managed demo source tables are available for the pipeline walkthrough.

**Next:** [`01_governance`: establish Governance context](01-governance.md)
