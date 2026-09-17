# 0C. Prepare the demo data with FabricOps I/O

**Run the tested `00C_demo_setup` flow to demonstrate the FabricOps I/O helpers and prepare the tables required by the `02_pipeline` demo.**

## 1. Import and run the setup notebook

1. Download [`00C_demo_setup.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/DemoData/00C_demo_setup.ipynb) and import it into Fabric Engineering Workspace (Dev).
2. Attach the same Fabric Environment used by the other notebooks.
3. Run the first two steps in the notebook to load `00_env_config` and import the FabricOps I/O helpers.

![Demo setup](../assets/00C/Demo%20Set%20Up.png)

## 2. Read the same Orders dataset from four file formats

The notebook reads the same 120 logical Orders rows through the CSV, JSON, Parquet, and Excel helpers. This demonstrates that the FabricOps file readers use the same configured Bronze Lakehouse while allowing the physical source format to vary.

The paths are relative to the configured Lakehouse `Files` area. For example, `Demo/orders.csv` resolves under `Files/Demo/orders.csv`.

![Read CSV](../assets/00C/Read_csv.png)

The four DataFrames created by this section are:

```python
orders_csv_df
orders_json_df
orders_parquet_df
orders_excel_df
```

The `display(...)` calls are intentionally commented out in the notebook. Uncomment any of them when you want to inspect the loaded rows interactively.

## 3. Write and read back the Orders table

The CSV DataFrame becomes the managed Orders source used by the later `02_pipeline` walkthrough.

`write_lakehouse_table()` writes the DataFrame to the Bronze Lakehouse as `demo.orders`. The notebook then uses `read_lakehouse_table()` to resolve the same configured store and read the managed table back.

![Orders demo](../assets/00C/Orders_Demo.png)

The read-back is optional for the walkthrough, but it is useful when you want to confirm that the table was written successfully before continuing.

## 4. Read, write, and read back Products

The notebook reads `Demo/products.csv`, writes it to the Bronze Lakehouse as `demo.products`, and reads the managed table back with `read_lakehouse_table()`.

![Products demo](../assets/00C/Products_Demo.png)

This table becomes the lookup input used by the later pipeline flow.

## 5. Create the Warehouse schema

Before writing `demo.order_history`, create the `demo` schema in the Gold Warehouse if it does not already exist. Warehouse schemas are created through Warehouse SQL rather than by the PySpark write helper.

![Create Warehouse schema](../assets/00C/Create_Schema_Warehouse.png)

## 6. Read, write, and read back Order history

The notebook reads `Demo/order_history.csv` from the Bronze Lakehouse Files area and writes it to the Gold Warehouse as `demo.order_history`.

![Orders history demo](../assets/00C/Orders_History_Demo.png)

FabricOps provides two Warehouse read helpers:

* `read_warehouse_table()` reads the full Warehouse table into a Spark DataFrame.
* `read_warehouse_query()` executes SQL in the Warehouse first and returns only the query result to Spark.

The notebook demonstrates both approaches. The query example returns only five rows:

```python
order_history_sample_df = read_warehouse_query(
    "SELECT TOP 5 * FROM demo.order_history ORDER BY 1",
    store="Gold",
    spark_session=spark,
)
```

Use `read_warehouse_query()` when filtering, selecting columns, joining, or aggregating Warehouse data so that the SQL work is pushed down before the result crosses into PySpark. For the broader engineering guidance, see [Lakehouse-first engineering](../reference/engineering-cheat-sheet.md#lakehouse-first).

## What the notebook prepares

After the notebook finishes, Engineering Development should contain the managed sources required by `02_pipeline`:

```text
Bronze Lakehouse
  demo.orders
  demo.products

Gold Warehouse
  demo.order_history
```

The setup notebook deliberately stops here. Later source changes, load-strategy examples, and Guardrail failure fixtures belong to the later Guided Demo steps rather than this initial preparation flow.

**Next:** [Step 1. Establish Governance context](01-create-agreement.md)
