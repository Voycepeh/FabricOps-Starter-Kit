# 0C. Prepare the demo data with FabricOps I/O

**Run one Engineering Development notebook that demonstrates the FabricOps I/O helpers and prepares the managed source tables required by `02_pipeline`.**

This is still setup, not one of the seven FabricOps lifecycle steps. Run it in **Engineering Development** after completing 0B.

## 1. Import the setup notebook

Download and import the Guided Demo notebook from the same DemoData package used in 0B:

[`00C_demo_setup.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/DemoData/00C_demo_setup.ipynb)

Place it in the **Engineering Development** workspace beside `00_env_config` and `02_pipeline`.

Attach the same Engineering Development Fabric Environment used by the other notebooks.

`00C_demo_setup` is a Guided Demo notebook rather than one of the four reusable FabricOps notebook templates. Its job is to exercise the I/O helpers and seed the demo tables before the seven-step lifecycle begins.

## 2. Run `00C_demo_setup`

The notebook starts with:

```python
%run 00_env_config
```

It then uses the configured logical stores from `00_env_config`; you do not need to paste workspace or item IDs into the notebook itself.

The notebook demonstrates the public FabricOps I/O surface in one runnable story:

1. Read the same canonical Orders dataset from CSV, JSON, Parquet, and Excel.
2. Confirm the four file formats resolve to the same 120-row logical dataset.
3. Read `products.csv` and `order_history.csv` from the Bronze `Files/Demo` folder.
4. Write the managed Lakehouse tables `bronze.demo.orders` and `bronze.demo.products`.
5. Write the managed Warehouse table `gold.demo.order_history`.
6. Read the Lakehouse tables back with `read_lakehouse_table()`.
7. Read the Warehouse back with both `read_warehouse_table()` and `read_warehouse_query()` so the difference between a full table read and SQL pushdown is visible.

## 3. What the notebook intentionally does not load

`orders_incremental.csv` remains in `bronze/Files/Demo/` and is **not** appended here. It is revisited later in the `02_pipeline` walkthrough so the source-change story happens at the right point in the lifecycle.

The partition and watermark fixtures are also left untouched for the later incremental/load-strategy showcase.

`orders_guardrail_failures.csv` is left untouched until the later Guardrail validation step. The normal baseline stays valid so the first Engineering run is deterministic.

## Expected result

After the notebook finishes, Engineering Development should contain the managed sources required by `02_pipeline`:

```text
bronze Lakehouse
  demo.orders       # canonical Day 1 Orders baseline
  demo.products

gold Warehouse
  demo.order_history
```

The raw demo files remain under:

```text
bronze/Files/Demo/
```

You have now exercised the FabricOps file, Lakehouse, and Warehouse I/O helpers and prepared the data for the seven-step lifecycle.

**Next:** [Step 1. Establish Governance context](01-create-agreement.md)
