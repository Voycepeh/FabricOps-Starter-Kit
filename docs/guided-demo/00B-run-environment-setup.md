# 0B. Configure the environment and load the baseline data

**Configure `00_env_config`, create the metadata tables, and land the managed Day 1 source tables used by `02_pipeline`.**

This is the second foundation step. When it is complete, the seven-step FabricOps lifecycle can start against real Fabric data.

## Configure `00_env_config`

Attach the Fabric Environment containing FabricOps and update the environment-specific configuration so these logical stores resolve correctly:

- `metadata` → Governance metadata Lakehouse
- `source` → Source Lakehouse
- `unified` → Unified Lakehouse
- `product` → Product Warehouse

![Path config](../assets/00B/00_config_paths.png)

The walkthrough notebooks should refer to these logical names rather than embedding workspace IDs, item IDs, SQL endpoints, or OneLake paths.

## Create or validate metadata tables

In the Governance context, run the metadata setup block in `00_env_config`.

![Setup Metadata Tables](../assets/00B/00_config_metadata_tables_setup_code.png)

![Metadata Tables Done](../assets/00B/Metadata-Tables-Created.png)

## Load the Day 1 source data

Use a plain setup notebook after `%run 00_env_config`. This is intentionally not `02_pipeline`: 0B is only preparing the managed source tables that the governed pipeline will later read.

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

At this point the managed sources are:

```text
Source Lakehouse
  demo.orders       # 120 Day 1 rows
  demo.products

Product Warehouse
  demo.order_history
```

## Keep the Day 2 file aside

Do **not** append `orders_incremental.csv` yet. It contains the 12 later Orders rows used after the first pipeline run to demonstrate changing source data and target load strategies.

Later in the walkthrough, append it to the managed source table with the same foundational setup pattern:

```python
day2_orders_df = read_lakehouse_csv(
    "DemoData/orders_incremental.csv",
    store="source",
    spark_session=spark,
    header=True,
    inferSchema=True,
)

write_lakehouse_table(
    day2_orders_df,
    "orders",
    store="source",
    schema="demo",
    mode="append",
)
```

After that update, `source.demo.orders` contains 132 rows. `02_pipeline` still reads the complete persisted source on its next run.

## Expected result

The shared environment resolves correctly, Governance metadata tables exist, and the Day 1 managed sources are ready for the first real Engineering run.

**Next:** [Step 1. Establish Governance context](01-create-agreement.md)
