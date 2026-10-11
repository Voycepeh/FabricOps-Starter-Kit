# Step 2B. Run the Incremental Append Demo

**Run the inventory pipeline three times in Microsoft Fabric to see an initial load, a new incremental batch, and a no-change run.**

This demo uses a watermark on `modified_datetime` and an Append target. Run the days in order and compare the visible row counts after each complete notebook run.

## Before you begin

1. Download [`02B_incremental_append_demo.ipynb`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/DemoData/02B_incremental_append_demo.ipynb) and import it into the Engineering Development workspace.
2. Keep `00_env_config.ipynb` beside it and attach the same Fabric Environment used in Step 00B.
3. Make sure you have already uploaded the demo files required for this demo in the previous step [Step 00B](00B-configure-environment-and-load-assets.md).
![File upload](../assets/2b/File%20Upload.png)

## What you will do

| Run | What changes | Expected Silver rows |
| --- | --- | ---: |
| Day 1 | Stage eight movements and bootstrap the Incremental Read. | 8 |
| Day 2 | Add four movements and append only the newly eligible rows. | 12 |
| Day 3 | Add no source rows and observe an empty incremental scope. | 12 |

The notebook uses these governed tables throughout:

| Role | Location | Processing |
| --- | --- | --- |
| Source | Bronze Lakehouse · `demo.inventory_movements` | Incremental on `modified_datetime` |
| Target | Silver Lakehouse · `demo.inventory_movements_incremental` | Append |


### 1. Run the Environment block

Run the two cells under **0. Environment**:

```python
%run 00_env_config
```
Then run the import cell immediately below it. 

```python
from pyspark.errors import AnalysisException
from pyspark.sql import functions as F

from fabricops_kit import (
    orchestrate_read,
    orchestrate_write,
    read_lakehouse_csv,
    read_lakehouse_table,
    resolve_table_id,
    widget_select_data_contract,
    write_lakehouse_table,
)
```

`00_env_config` loads the configured Bronze, Silver, Gold, and Metadata stores, the environment and notebook identity, the Spark session, and metadata routing. You should see the shared FabricOps configuration load without an error.

![Notebook after loading the shared FabricOps environment](../assets/02/Setup.png)

## Run Day 1 in Fabric

Leave the value under **1. Choose the demo day** as:

```python
DEMO_DAY = 1
```
![Day 1 demo day selection](../assets/2b/Day%201.png)

Run the cell. It validates that the selected day is supported.

### 3. Stage the Day 1 source

Run both cells under **2. Read the CSV batch and stage Bronze**.

The notebook reads `inventory_day1.csv`, removes duplicate `movement_id` values, and overwrites Bronze `demo.inventory_movements`.

You should see:

![Day 1 Bronze staging output showing 8 rows](../assets/2b/Day%201%20Bronze%20staging%20output%20showing%208%20rows.png)

### 4. Run the Data Contract block

Run the Data Contract cell:

```python
CONTRACTS = widget_select_data_contract(spark_session=spark)
```

For the initial Guided Demo run, there is no Data Contract yet, so leave the selection unchanged. Contract-backed checks will return as skipped, and the targets can publish in Engineering Development.



![Data Contract selector before a contract exists](../assets/02/Data%20_Contract_None.png)

### 5. Run the Governed Incremental Read

First, run the source results dictionary cell:

```python
sources = {}
```

This creates an empty dictionary for the governed Read result. Keeping the complete result by name gives the Transform block access to its DataFrame and gives the Write block the governed source identity needed for lineage, source-aware checks, and incremental processing.

Then run the remaining cell under **4. Governed Incremental Read**.

The notebook resolves the Silver target identity, reads Bronze `demo.inventory_movements` with `modified_datetime` as the watermark, and saves the result as `sources["inventory_movements"]`.

On Day 1, there is no earlier successful watermark for this source-to-target relationship. The incremental scope therefore bootstraps with all eight source rows.

*Image coming soon: Day 1 Incremental Read output and bootstrap scope.*

### 6. Run the PySpark Transform

Run the cell under **5. PySpark Transform**.

The block creates `movement_date`, `quantity_in`, and `quantity_out` for the eight eligible movement rows. It stores the result in `transformed_df`.

*Image coming soon: transformed Day 1 inventory movements.*

### 7. Run the Governed Append Write

First, run the write results dictionary cell:

```python
writes = {}
```

This creates an empty dictionary for the governed Write result. Keeping the complete result by target name makes its publication status, orchestration stages, Guardrail results, and, when published, target profile available for inspection.

Then run the remaining cell under **6. Governed Append Write**.

The block appends the eight transformed rows to Silver `demo.inventory_movements_incremental` and saves the Write result as `writes["inventory_movements_incremental"]`.

You should see the Write stages complete and the target publish successfully.

*Image coming soon: Day 1 Append Write output.*

### 8. Inspect the Day 1 result

Run the cell under **7. Inspect results**.

You should see:

- an incremental scope covering the initial eight rows;
- `Silver rows: 8`;
- eight movement records ordered by `modified_datetime` and `movement_id`; and
- an inventory balance summarized by `product_id`.

*Image coming soon: Day 1 Silver rows and inventory balances.*

## Run Day 2 in Fabric

### 1. Change only the demo day

Return to the day cell and change it to:

```python
DEMO_DAY = 2
```

![Day 2](../assets/2b/Day 2.png)

### 2. Rerun the complete notebook

Use **Run all** or run every block again from **0. Environment** through **7. Inspect results**.

The Bronze staging block adds the four Day 2 movements and keeps the eight existing movements by `movement_id`. You should see:

```text
Bronze inventory rows after Day 2: 12
```

The Incremental Read returns only the four rows after the successful Day 1 watermark. The Append Write adds those rows to the Silver target.

### 3. Check the Day 2 output

The final inspection should show:

- four newly eligible rows in the incremental scope;
- `Silver rows: 12`;
- all twelve movements in the target; and
- updated inventory balances.

*Image coming soon: Day 2 incremental scope, 12 Silver rows, and updated balances.*

## Run Day 3 in Fabric

### 1. Change only the demo day

Return to the day cell and change it to:

```python
DEMO_DAY = 3
```
![Day 3 demo run](../assets/2b/Day%203.png)

Day 3 intentionally has no CSV file and adds no source records.

### 2. Rerun the complete notebook

Run every block again. The notebook still calls the Read and Write orchestrators; do not skip those blocks.

You should see:

```text
Bronze inventory rows after Day 3: 12
```

The Incremental Read returns an empty scope. The Append target remains unchanged.

### 3. Check the Day 3 output

The final inspection should show:

- an empty/no-change incremental scope;
- `Silver rows: 12`; and
- the same twelve target rows and inventory balances as Day 2.

*Image coming soon: Day 3 empty scope and unchanged 12-row Silver target.*

## Expected result

### Data saved by the demo

| Location | Table | Final state after Day 3 |
| --- | --- | --- |
| Bronze Lakehouse | `demo.inventory_movements` | 12 unique source movements from Days 1 and 2. |
| Silver Lakehouse | `demo.inventory_movements_incremental` | 12 transformed movements appended across the successful incremental runs. |

### Metadata saved by FabricOps

All metadata is routed to the Metadata Lakehouse configured by `00_env_config`.

| Metadata table or governed record | What this demo records |
| --- | --- |
| `METADATA_DATA_CATALOGUE` | Canonical source and target table and column identities. |
| `METADATA_DATA_PROFILED` | Profile snapshots of the published Silver target. Incremental Read batches themselves are not profiled. |
| `METADATA_DATA_PROFILED_FREQUENCY` | Target frequency rows linked to profile snapshots where applicable. |
| `METADATA_DATA_LINEAGE` | The Bronze source and Silver target participation for this notebook pipeline. |
| `METADATA_SOURCE_OBSERVATION` | Source-state observations and history used by Incremental execution. |
| Governed target watermark | Successful watermark progress for the exact Bronze-to-Silver relationship. |
| `METADATA_GUARDRAIL_RESULTS` | Guardrail evaluation results when a selected Data Contract supplies executable Guardrails. |

*Image coming soon: Metadata Lakehouse records after the three Incremental Append runs.*

### Reset the demo

An Incremental demo cannot be reset by rerunning Day 1 or deleting only the Silver target. FabricOps remembers successful progress for the exact Bronze-to-Silver relationship.

The safest clean reset is to run the demo in a fresh Guided Demo environment. To reset the same environment through an approved maintenance process:

1. In the Bronze Lakehouse, delete `demo.inventory_movements` from the table explorer.
2. In the Silver Lakehouse, delete `demo.inventory_movements_incremental` from the table explorer. This removes the appended business data and the successful watermark progress stored with the governed target.
3. Remove only the `METADATA_SOURCE_OBSERVATION` rows for the `inventory_movements` → `inventory_movements_incremental` relationship and the current environment. Do not clear observations for other pipelines.
4. Set `DEMO_DAY = 1`.
5. Run the notebook from the top. The Day 1 CSV recreates Bronze with eight rows, the Incremental Read bootstraps again, and the Append Write recreates the eight-row Silver target.

!!! warning "Keep incremental state aligned"

    The Bronze source, Silver target, scoped Source Observation history, and governed target watermark belong to one incremental state. Reset all four together. If you cannot perform the scoped metadata cleanup safely, use a fresh Guided Demo environment instead.

**Next optional processing mode:** [Step 2C. Run the SCD1 and SCD2 Demo](02C-build-and-run-scd-etl.md)

**Continue the main Guided Demo:** [Step 3. Author and freeze the Data Contract](03-author-and-freeze-data-contract.md)
