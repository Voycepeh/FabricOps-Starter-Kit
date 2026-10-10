# Step 2A. Run the Full Refresh Demo

**Run the completed retail pipeline in Microsoft Fabric: three Full Reads, one PySpark transformation, and two Overwrite targets.**

This is the recommended first demo after learning the reusable pipeline structure in [Step 2. Build a Pipeline](02-build-and-run-etl.md). Follow the notebook from top to bottom and compare each result with this page.

## Before you begin

1. Complete [Step 00C. Prepare the demo data](00C-prepare-demo-data-with-fabricops-io.md).
2. Download [`02A_full_refresh_demo.ipynb`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/DemoData/02A_full_refresh_demo.ipynb) and import it into the Engineering Development workspace.
3. Keep `00_env_config.ipynb` beside the demo notebook.
4. Attach the same Fabric Environment configured in [Step 00B](00B-configure-environment-and-load-assets.md).
5. Confirm these source tables exist:

| Source | Location |
| --- | --- |
| Orders | Bronze Lakehouse · `demo.orders` |
| Products | Bronze Lakehouse · `demo.products` |
| Order History | Gold Warehouse · `demo.order_history` |

## What you will do

1. Load the shared environment.
2. Run the Data Contract selector.
3. Read Orders, Products, and Order History.
4. Build detailed orders and a customer summary with PySpark.
5. Overwrite a Silver Lakehouse table and a Gold Warehouse table.
6. Inspect the saved data and FabricOps metadata.

## Run the demo in Fabric

### 1. Run the Environment block

Run the two cells under **0. Environment**:

```python
%run 00_env_config
```

Then run the import cell immediately below it. The import cell provides the public APIs used by that notebook, so its exact list can vary by demo.

`00_env_config` loads the configured Bronze, Silver, Gold, and Metadata stores, the environment and notebook identity, the Spark session, and metadata routing. You should see the shared FabricOps configuration load without an error.

![Notebook after loading the shared FabricOps environment](../assets/02/Setup.png)

### 2. Run the Data Contract block

Run the Data Contract cell:

```python
CONTRACTS = widget_select_data_contract(spark_session=spark)
```

For the initial Guided Demo run, there is no Data Contract yet, so leave the selection unchanged. Contract-backed checks will return as skipped, and the targets can publish in Engineering Development.

If you revisit the notebook after Data Contracts exist, choose **Enforce** to allow publication after the required checks pass. Choose **Validate** to evaluate a frozen candidate without publishing the target.

![Data Contract selector before a contract exists](../assets/02/Data%20_Contract_None.png)

**Run the source results dictionary cell:**

```python
sources = {}
```

This creates an empty dictionary for the three governed Read results. Keeping each complete result by name lets the Transform block use the source DataFrames and lets the Write blocks pass their governed source identities into lineage and source-aware checks.

### 3. Run READ 1 — Orders

The block reads the complete Bronze `demo.orders` table and saves the result as `sources["orders"]`.

You should see the five Read stages complete. With no selected Data Contract, contract-backed checks show as `SKIPPED`; the Full Read still returns the Orders DataFrame and profiles it.

![Orders Full Read output](../assets/02/Read_Block_Output.png)

### 4. Run READ 2 — Products

Run **READ 2 — Products**.

The block reads the complete Bronze `demo.products` table and saves the result as `sources["products"]`.

You should see the same Read-stage summary for Products.

![Products Full Read output](../assets/02/Read_Block_Output_2.png)

### 5. Run READ 3 — Order History

Run **READ 3 — Order History**.

This block pushes its `SELECT` query to the Gold Warehouse, returns the selected `demo.order_history` columns, and saves the result as `sources["history"]`.

You should see the Warehouse Read complete and the governed Read-stage summary appear.

![Order History Full Read output](../assets/02/Read_Block_Output_3.png)

### 6. Run the Transform block

Run the cell under **3. Transform**.

The PySpark code:

1. summarizes historical orders by `customer_id`;
2. joins Orders, Products, and the history summary;
3. calculates `order_net_amount`;
4. creates `transformed_df` at order level; and
5. creates `customer_summary_df` at customer level.

Uncomment these lines if you want to inspect both DataFrames before publishing:

```python
display(transformed_df)
display(customer_summary_df)
```

You should see one detailed row per current order in `transformed_df` and one aggregated row per customer in `customer_summary_df`.

*Image coming soon: transformed orders and customer summary DataFrames in Fabric.*

### 7. Run WRITE 1 — Lakehouse Curated Orders

**Run the write results dictionary cell:**

```python
writes = {}
```

This creates an empty dictionary for the governed Write results. Keeping each complete result by target name makes the publication status, orchestration stages, Guardrail results, and, when published, target profile available for inspection after the Write.

Then run **WRITE 1 — Lakehouse Curated Orders**.

The block overwrites Silver Lakehouse `demo.curated_orders` with `transformed_df` and saves the result as `writes["curated_orders_lakehouse"]`.

You should see the Write stages complete and `published=True`. If you selected **Validate**, the notebook exits after successful validation because Validate deliberately does not publish.

![Curated Orders Write output](../assets/02/Write_Block_Output.png)

### 8. Run WRITE 2 — Warehouse Customer Summary

Run **WRITE 2 — Warehouse Customer Summary**.

The block overwrites Gold Warehouse `demo.customer_summary` with `customer_summary_df` and saves the result as `writes["customer_summary_warehouse"]`.

You should see the Write stages complete and `published=True`.

![Customer Summary Write output](../assets/02/Write_Block_Output_2.png)

!!! note "The two Writes publish independently"

    WRITE 1 and WRITE 2 are not one atomic transaction. If WRITE 1 succeeds and WRITE 2 fails, `demo.curated_orders` remains published. Fix the error and rerun the notebook; both targets use Overwrite, so a successful rerun replaces their contents.

### 9. Inspect the saved results

Open the target tables in Fabric or use the notebook's optional inspection cell.

**Silver Lakehouse**

`demo.curated_orders` contains the detailed joined order data.

![Curated Orders saved in the Silver Lakehouse](../assets/02/Silver_Table_LH.png)

**Gold Warehouse**

`demo.customer_summary` contains the customer-level aggregation.

![Customer Summary saved in the Gold Warehouse](../assets/02/Gold_Table_WH.png)

## Expected result

### Data saved by the demo

| Store | Table | What was saved |
| --- | --- | --- |
| Bronze Lakehouse | `demo.orders` | Existing source prepared in Step 00C; unchanged by this notebook. |
| Bronze Lakehouse | `demo.products` | Existing source prepared in Step 00C; unchanged by this notebook. |
| Gold Warehouse | `demo.order_history` | Existing source prepared in Step 00C; unchanged by this notebook. |
| Silver Lakehouse | `demo.curated_orders` | Detailed order-level result, fully replaced by WRITE 1. |
| Gold Warehouse | `demo.customer_summary` | Customer-level result, fully replaced by WRITE 2. |

### Metadata saved by FabricOps

All metadata is routed to the Metadata Lakehouse configured by `00_env_config`.

| Metadata table | What this run records |
| --- | --- |
| `METADATA_DATA_CATALOGUE` | Canonical table and column identities for the governed sources and targets. |
| `METADATA_DATA_PROFILED` | Profile snapshots for the three Full Read sources and both published targets. |
| `METADATA_DATA_PROFILED_FREQUENCY` | Frequency rows linked to those profile snapshots where applicable. |
| `METADATA_DATA_LINEAGE` | Source and target participation for this notebook pipeline. |
| `METADATA_SOURCE_OBSERVATION` | Source-state observations associated with successful target publication where applicable. |
| `METADATA_GUARDRAIL_RESULTS` | Guardrail evaluation results when a selected Data Contract supplies executable Guardrails. |

![FabricOps metadata captured for the Full Refresh pipeline](../assets/02/Metadat_Captured.png)

### What happens if I click Run all?

The notebook runs again from the top. Both targets use Overwrite, so a successful rerun replaces their full contents instead of adding duplicate rows. This is a replay, not a clean reset: the target tables and previously captured FabricOps metadata still exist before the run begins.

### Reset the demo to a clean data state

Use these steps when you want the next run to behave like the first Full Refresh run:

1. In the Silver Lakehouse, delete `demo.curated_orders` from the table explorer.
2. In the Gold Warehouse query editor, drop the other demo target:

    ```sql
    DROP TABLE IF EXISTS demo.customer_summary;
    ```

3. Check the three source tables:
    - Bronze Lakehouse · `demo.orders`
    - Bronze Lakehouse · `demo.products`
    - Gold Warehouse · `demo.order_history`
4. This notebook does not change those sources. If they still contain the Step 00C data, leave them in place. If they were changed, rerun [Step 00C. Prepare the demo data](00C-prepare-demo-data-with-fabricops-io.md) from the top; its Overwrite cells restore all three sources from the canonical demo files.
5. Return to this notebook and run it from the top. WRITE 1 recreates `demo.curated_orders`, and WRITE 2 recreates `demo.customer_summary`.

!!! note "Business data reset versus full environment reset"

    These steps reset the business tables. FabricOps metadata remains as run history, which is useful when continuing to Step 3. If you need the entire Guided Demo—including Catalogue, profile, lineage, Source Observation, Guardrail, and Data Contract history—to look completely new, use a fresh Guided Demo environment or an approved, precisely scoped metadata-maintenance process. Do not delete complete `METADATA_*` tables to reset one demo.

**Next optional processing mode:** [Step 2B. Run the Incremental Append Demo](02B-build-and-run-incremental-append-etl.md)

**Continue the main Guided Demo:** [Step 3. Author and freeze the Data Contract](03-author-and-freeze-data-contract.md)
