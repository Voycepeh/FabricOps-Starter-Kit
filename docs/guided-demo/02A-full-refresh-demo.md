# Step 2A. Run the Full Refresh Demo

### Before you begin

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

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## The big picture

Follow the same notebook lifecycle as Step 2 with concrete Full Read and Overwrite examples.

</div>
</div>

| Notebook section | What happens |
| --- | --- |
| Environment | Loads the shared Fabric configuration and imports the functions used by this demo. |
| Data Contract | Selects whether each target runs without a contract, validates a frozen candidate, or enforces an active contract. |
| Governed Read | Reads Orders, Products, and Order History in full. |
| PySpark Transform | Produces detailed orders and a customer summary. |
| Governed Write | Overwrites a Silver Lakehouse target and a Gold Warehouse target. |
| Inspection | Verifies the published data and FabricOps metadata. |

### Load the shared environment

Run the two cells under **0. Environment**:

```python
%run 00_env_config
```

Then run the import cell immediately below it.

```python
from pyspark.sql import functions as F

from fabricops_kit import (
    orchestrate_read,
    orchestrate_write,
    widget_select_data_contract,
)
```

`00_env_config` loads the configured Bronze, Silver, Gold, and Metadata stores, the environment and notebook identity, the Spark session, and metadata routing. You should see the shared FabricOps configuration load without an error.

![Notebook after loading the shared FabricOps environment](../assets/02/Setup.png)

### Run the Data Contract block

```python
CONTRACTS = widget_select_data_contract(spark_session=spark)
```

For the initial Guided Demo run, there is no Data Contract yet, so leave the selection unchanged. Contract-backed checks will return as skipped, and the targets can publish in Engineering Development.

![Data Contract selector before a contract exists](../assets/02/Data%20_Contract_None.png)

### Initialize the source results dictionary

```python
sources = {}
```

This creates an empty dictionary for the three governed Read results. Keeping each complete result by name lets the Transform block use the source DataFrames and lets the Write blocks pass their governed source identities into lineage and source-aware checks.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Configure the Governed Reads

Read Orders, Products, and Order History using the governed Full Read pattern.

</div>
</div>

### Run READ 1 — Orders

Run **READ 1 — Orders**. The block reads the complete Bronze `demo.orders` table and saves the result as `sources["orders"]`.

You should see the five Read stages complete. With no selected Data Contract, contract-backed checks show as `SKIPPED`; the Full Read still returns the Orders DataFrame and profiles it.

![Orders Full Read output](../assets/02/Read_Block_Output.png)

### Run READ 2 — Products

Run **READ 2 — Products**.

The block reads the complete Bronze `demo.products` table and saves the result as `sources["products"]`.

You should see the same Read-stage summary for Products.

![Products Full Read output](../assets/02/Read_Block_Output_2.png)

### Run READ 3 — Order History

Run **READ 3 — Order History**.

This block pushes its `SELECT` query to the Gold Warehouse, returns the selected `demo.order_history` columns, and saves the result as `sources["history"]`.

You should see the Warehouse Read complete and the governed Read-stage summary appear.

![Order History Full Read output](../assets/02/Read_Block_Output_3.png)

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-dev.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Write your PySpark Transform

Transform the three input sources into the curated and customer-level outputs.

</div>
</div>

Run the cell under **3. Transform**.

The PySpark code:

1. summarizes historical orders by `customer_id`;
2. joins Orders, Products, and the history summary;
3. calculates `order_net_amount`;
4. creates `transformed_df` at order level; and
5. creates `customer_summary_df` at customer level.

Uncomment these lines if you want to inspect both DataFrames before publishing:

```python
# Detailed order-level transformed output that will feed WRITE 1.
display(transformed_df)
# Customer-level aggregated output that will feed WRITE 2.
display(customer_summary_df)
```

You should see:

- one detailed row per current order in `transformed_df`:

  ![Detailed order-level transformed output](../assets/02/Transform_Output.png)

- one aggregated row per customer in `customer_summary_df`:

  ![Customer-level aggregated output](../assets/02/Transform_Output_2.png)

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Configure the Governed Writes

Overwrite the curated Lakehouse table and Warehouse customer summary.

</div>
</div>

First, run the write results dictionary cell:

```python
writes = {}
```

This creates an empty dictionary for the governed Write results. Keeping each complete result by target name makes the publication status, orchestration stages, Guardrail results, and, when published, target profile available for inspection after the Write.

### Run WRITE 1 — Lakehouse Curated Orders

Run **WRITE 1 — Lakehouse Curated Orders**. The block overwrites Silver Lakehouse `demo.curated_orders` with `transformed_df` and saves the result as `writes["curated_orders_lakehouse"]`.

You should see the Write stages complete and `published=True`. 

![Curated Orders Write output](../assets/02/Write_Block_Output.png)

### Run WRITE 2 — Warehouse Customer Summary

Run **WRITE 2 — Warehouse Customer Summary**.

The block overwrites Gold Warehouse `demo.customer_summary` with `customer_summary_df` and saves the result as `writes["customer_summary_warehouse"]`.

You should see the Write stages complete and `published=True`.

![Customer Summary Write output](../assets/02/Write_Block_Output_2.png)

!!! note "The two Writes publish independently"

    WRITE 1 and WRITE 2 are not one atomic transaction. If WRITE 1 succeeds and WRITE 2 fails, `demo.curated_orders` remains published. Fix the error and rerun the notebook; both targets use Overwrite, so a successful rerun replaces their contents.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-validate.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Inspect the saved results

Verify the target tables and the recorded governance metadata.

</div>
</div>

Open the target tables in Fabric or use the notebook's optional inspection cell.

**Silver Lakehouse**

`demo.curated_orders` contains the detailed joined order data.

![Curated Orders saved in the Silver Lakehouse](../assets/02/Silver_Table_LH.png)

**Gold Warehouse**

`demo.customer_summary` contains the customer-level aggregation.

![Customer Summary saved in the Gold Warehouse](../assets/02/Gold_Table_WH.png)

### Expected result

The three Full Reads complete, both Overwrite targets publish, and the saved tables and metadata reflect the same successful notebook run.

### Data saved by the demo

| Store | Table | What was saved |
| --- | --- | --- |
| Bronze Lakehouse | `demo.orders` | Existing source prepared in Step 00C; unchanged by this notebook. |
| Bronze Lakehouse | `demo.products` | Existing source prepared in Step 00C; unchanged by this notebook. |
| Gold Warehouse | `demo.order_history` | Existing source prepared in Step 00C; unchanged by this notebook. |
| Silver Lakehouse | `demo.curated_orders` | Detailed order-level result, fully replaced by WRITE 1. |
| Gold Warehouse | `demo.customer_summary` | Customer-level result, fully replaced by WRITE 2. |

### Metadata saved by FabricOps

![FabricOps metadata captured for the Full Refresh pipeline](../assets/02/Metadat_Captured.png)

All metadata is routed to the Metadata Lakehouse configured by `00_env_config`.

| Metadata table | What this run records |
| --- | --- |
| `METADATA_DATA_CATALOGUE` | Canonical table and column identities for the governed sources and targets. |
| `METADATA_DATA_PROFILED` | Profile snapshots for the three Full Read sources and both published targets. |
| `METADATA_DATA_PROFILED_FREQUENCY` | Frequency rows linked to those profile snapshots where applicable. |
| `METADATA_DATA_LINEAGE` | Source and target participation for this notebook pipeline. |
| `METADATA_SOURCE_OBSERVATION` | Source-state observations associated with successful target publication where applicable. |
| `METADATA_GUARDRAIL_RESULTS` | Guardrail evaluation results when a selected Data Contract supplies executable Guardrails. |

!!! note "Reset the demo to a clean data state"

    Use these steps when you want the next run to behave like the first Full Refresh run:

    1. In the Silver Lakehouse, delete `demo.curated_orders` from the table explorer.
    2. In the Gold Warehouse query editor, drop the other demo target:

        ```sql
        DROP TABLE IF EXISTS demo.customer_summary;
        ```

    3. This notebook does not change its sources. If they have changed, rerun [Step 00C. Prepare the demo data](00C-prepare-demo-data-with-fabricops-io.md) to restore Bronze `demo.orders`, Bronze `demo.products`, and Gold `demo.order_history`.

**Next optional processing mode:** [Step 2B. Run the Incremental Append Demo](02B-build-and-run-incremental-append-etl.md)

**Continue the main Guided Demo:** [Step 3. Author and freeze the Data Contract](03-author-and-freeze-data-contract.md)
