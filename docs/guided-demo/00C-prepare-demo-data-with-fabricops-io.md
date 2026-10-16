# 0C. Prepare the demo data with FabricOps I/O

### Before you begin

Complete [Step 0B](00B-configure-environment-and-load-assets.md) before preparing the demo data.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Import the setup notebook

Import the setup notebook and connect it to the configured Fabric Environment.

</div>
</div>

1. If you havent done so , download [`00C_demo_setup.ipynb`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/DemoData/00C_demo_setup.ipynb) and import it into Fabric Engineering Workspace (Dev).

2. Attach the same Fabric Environment used by the other notebooks.

3. Make sure you have already uploaded the demo files required for this demo in the previous step [Step 00B](00B-configure-environment-and-load-assets.md).

![File upload](../assets/00C/File%20Upload.png)

4. Run the first two steps in the notebook.

![Demo setup](../assets/00C/Demo%20Set%20Up.png)

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Read the same Orders dataset from four file formats

Read the same canonical Orders dataset using CSV, JSON, Parquet, and Excel.

</div>
</div>



![Read CSV](../assets/00C/Read_csv.png)

```python
# Optional: uncomment to inspect the loaded data
display(orders_csv_df)
```

??? tip "Optional: verify all four file formats match"

    Copy and paste this into an empty code cell.

    Normalize the format-specific inferred schemas, then verify that CSV, JSON, Parquet, and Excel resolve to the same canonical Orders dataset using a checksum comparison.

    ```python
    from pyspark.sql import functions as F

    schema = {
        "order_id": "string",
        "customer_id": "string",
        "order_datetime": "timestamp",
        "modified_datetime": "timestamp",
        "product_id": "string",
        "quantity": "int",
        "unit_price": "double",
        "discount": "double",
        "order_status": "string",
        "shipping_country": "string",
    }

    def normalize(df):
        return df.select(*[
            F.col(c).cast(dtype).alias(c)
            for c, dtype in schema.items()
        ])

    formats = {
        "CSV": orders_csv_df,
        "JSON": orders_json_df,
        "PARQUET": orders_parquet_df,
        "EXCEL": orders_excel_df,
    }

    normalized = {name: normalize(df) for name, df in formats.items()}

    def checksum(df):
        cols = sorted(df.columns)
        return (
            df.select(F.sha2(F.concat_ws("||", *[F.coalesce(F.col(c).cast("string"), F.lit("<NULL>")) for c in cols]), 256).alias("hash"))
            .agg(F.sha2(F.concat_ws("", F.sort_array(F.collect_list("hash"))), 256).alias("hash"))
            .first()["hash"]
        )

    hashes = [checksum(df) for df in normalized.values()]
    assert len(set(hashes)) == 1, "Orders file variants do not match."

    print("✓ CSV = JSON = PARQUET = EXCEL")
    print("✓ 1:1:1:1 data match")
    ```

    The expected output confirms that all four file formats resolve to equivalent data. This step is only used to demonstrate the FabricOps file I/O capabilities.

    ```text
    ✓ CSV = JSON = PARQUET = EXCEL
    ✓ 1:1:1:1 data match
    ```


<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Write Orders table to the Bronze lakehouse

Prepare the Orders baseline that feeds the Full Refresh demo.

</div>
</div>

![Orders demo](../assets/00C/Orders_Demo.png)

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Read and Write Products table to the Bronze lakehouse 

Prepare the product records needed for the retail pipeline.

</div>
</div>

![Products demo](../assets/00C/Products_Demo.png)

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-dev.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Create the Warehouse schema, 

Create the Warehouse schema required before the demo writes its summary.
Do not skip this step ! Unlike lakehouse warehouse requires the schema to be created before you can write to it. 

</div>
</div>

![Create Warehouse schema](../assets/00C/Create_Schema_Warehouse.png)

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Read and Write the Order history table to the Bronze Lakehouse

Prepare the history source used for the governed retail reads.

</div>
</div>
![Orders history demo](../assets/00C/Orders_History_Demo.png)

!!! tip "FabricOps provides two Warehouse read helpers"

    * `read_warehouse_table()` reads the full Warehouse table into a Spark DataFrame.
    * `read_warehouse_query()` executes SQL in the Warehouse first, then returns only the query result to Spark.

    Use `read_warehouse_query()` when filtering, selecting columns, joining, or aggregating Warehouse data. This pushes the SQL work down to the Warehouse before the result crosses into PySpark, avoiding translation of more Warehouse data into Spark than necessary.

    Use SQL pushdown when it materially reduces Warehouse data before Spark. For repeated heavy PySpark engineering, prefer landing the required data into Lakehouse Delta rather than repeatedly crossing the Warehouse-to-Spark boundary.


<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Prepare Day 1 for Incremental and SCD Demos

Initialize the Day 1 Bronze source tables for the Incremental Append (02B) and SCD1/SCD2 (02C) demos.

</div>
</div>

This step prepares two dedicated Bronze tables using the sample CSV files:

| Source file | Bronze table | Used by |
|---|---|---|
| `Demo/inventory_day1.csv` | `demo.inventory_movements` | 02B Incremental Append |
| `Demo/products_day1.csv` | `demo.product_master_updates` | 02C SCD1/SCD2 |

### Run the **5. Prepare Day 1 for incremental and SCD demos** block in `00C_demo_setup`.

![Step 5: Prepare Day 1 for incremental and SCD demos](../assets/00C/step5.png)

The notebook reads each CSV file using `read_lakehouse_csv()` and writes it to the Bronze Lakehouse using `write_lakehouse_table()` with `mode="overwrite"`.

This initializes the Day 1 source tables before the first execution of the 02B and 02C notebooks.


### Expected result

After the notebook finishes, Engineering Development should contain the starting tables for all three Step 2 demos:

```text
bronze Lakehouse
  demo.orders
  demo.products
  demo.inventory_movements      # 02B incremental Day 1 baseline
  demo.product_master_updates   # 02C SCD Day 1 baseline

gold Warehouse
  demo.order_history
```

**Next:** [Step 1. Establish Governance context](01-establish-governance-context.md)
