# Step 2C. Run the SCD1 and SCD2 Demo

**Run three Product Master snapshots in Microsoft Fabric and compare a current-state SCD1 target with a history-preserving SCD2 target.**

Each notebook run replaces the Bronze source with one complete eight-row snapshot, then publishes that snapshot to both Silver targets. Run the days in order so you can watch the two load strategies respond to the same business changes.

## Before you begin

1. Download [`02C_scd_demo.ipynb`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/DemoData/02C_scd_demo.ipynb) and import it into the Engineering Development workspace.
2. Keep `00_env_config.ipynb` beside it and attach the same Fabric Environment used in Step 00B.
3. Make sure you have already uploaded the demo files required for this demo in the previous step [Step 00B](00B-configure-environment-and-load-assets.md).

 The notebook reads `Demo/products_day1.csv`, `Demo/products_day2.csv`, and `Demo/products_day3.csv` directly from Bronze Lakehouse `Files/Demo`. There is no `scd_product_master` subfolder.
![File upload](../assets/2c/File%20Upload.png)


4. Use a fresh demo state and run Day 1, then Day 2, then Day 3.

## What you will do <img class="fabricops-step-mascot" src="../../../assets/robot-scanning.png" alt="" loading="lazy">

| Run | Business change | Expected SCD1 rows | Expected SCD2 versions |
| --- | --- | ---: | ---: |
| Day 1 | Load the initial eight products. | 8 | 8 |
| Day 2 | Change `P002.list_price`. | 8 | 9 |
| Day 3 | Change `P001.product_category`. | 8 | 10 |

The notebook uses these governed tables throughout:

| Role | Location | Processing |
| --- | --- | --- |
| Source | Bronze Lakehouse · `demo.product_master_updates` | Full Read |
| Current-state target | Silver Lakehouse · `demo.product_master_scd1` | SCD1 keyed by `product_id` |
| Historical target | Silver Lakehouse · `demo.product_master_scd2` | SCD2 effective on `modified_datetime` and tracking `product_category` and `list_price` |

## Run Day 1 in Fabric

### 1. Run the Environment block

Run the two cells under **0. Environment**:

```python
%run 00_env_config
```

Then run the import cell immediately below it. The import cell provides the public APIs used by that notebook, so its exact list can vary by demo.

`00_env_config` loads the configured Bronze, Silver, Gold, and Metadata stores, the environment and notebook identity, the Spark session, and metadata routing. You should see the shared FabricOps configuration load without an error.

![Notebook after loading the shared FabricOps environment](../assets/02/Setup.png)

### 2. Choose Day 1

Leave the value under **1. Choose the demo day** as:

```python
DEMO_DAY = 1
```

Run the cell. It validates that the selected day is supported.

### 3. Stage the Day 1 snapshot

Run both cells under **2. Read the selected snapshot and overwrite Bronze**.

The notebook reads `products_day1.csv`, checks that it contains exactly eight rows, and overwrites Bronze `demo.product_master_updates`.

The cell should complete without an error. Bronze now contains the complete Day 1 Product Master snapshot.

*Image coming soon: Day 1 Product Master snapshot saved in Bronze.*

### 4. Run the Data Contract block

Run the Data Contract cell:

```python
CONTRACTS = widget_select_data_contract(spark_session=spark)
```

For the initial Guided Demo run, there is no Data Contract yet, so leave the selection unchanged. Contract-backed checks will return as skipped, and the targets can publish in Engineering Development.

If you revisit the notebook after Data Contracts exist, choose **Enforce** to allow publication after the required checks pass. Choose **Validate** to evaluate a frozen candidate without publishing the target.

![Data Contract selector before a contract exists](../assets/02/Data%20_Contract_None.png)

### 5. Run the Governed Full Read

First, run the source results dictionary cell:

```python
sources = {}
```

This creates an empty dictionary for the governed Read result. Keeping the complete result by name gives the Transform block access to its DataFrame and lets both Write blocks pass the same governed source identity into lineage and source-aware checks.

Then run the remaining cell under **4. Governed Full Read**.

The block reads all eight rows from Bronze `demo.product_master_updates` and saves the result as `sources["product_master"]`.

You should see the Read stages complete and the Full Read profile the source snapshot.

*Image coming soon: Day 1 Product Master Full Read output.*

### 6. Run the PySpark Transform

Run the cell under **5. PySpark Transform**.

The block selects the Product Master columns and casts `list_price` to double and `modified_datetime` to timestamp. The resulting `transformed_df` contains eight rows ready for both targets.

*Image coming soon: transformed Day 1 Product Master DataFrame.*

### 7. Run the Sequence safety block

Run the cell under **Sequence safety**.

Nothing is checked on Day 1 because no earlier SCD2 state is required. The cell should complete without output.

### 8. Run WRITE 1 — SCD1 current state

First, run the write results dictionary cell:

```python
writes = {}
```

This creates an empty dictionary for both governed Write results. Keeping each complete result by target name makes the publication status, orchestration stages, Guardrail results, and, when published, target profiles available for inspection.

Then run **WRITE 1 — SCD1 current state**.

The block publishes the eight products to Silver `demo.product_master_scd1`, keyed by `product_id`.

You should see the Write stages complete successfully.

*Image coming soon: Day 1 SCD1 Write output.*

### 9. Run WRITE 2 — SCD2 history

Run **WRITE 2 — SCD2 history**.

The block publishes the initial version of every product to Silver `demo.product_master_scd2`. It uses `modified_datetime` as the effective column and tracks changes to `product_category` and `list_price`.

You should see the Write stages complete successfully.

*Image coming soon: Day 1 SCD2 Write output.*

### 10. Inspect the Day 1 result

Run the cell under **7. Inspect current and historical results**.

You should see:

```text
SCD1 rows: 8
SCD2 versions: 8
```

The first display shows one current SCD1 row per product. The second shows one current SCD2 version per product with `_is_current=True`.

*Image coming soon: Day 1 SCD1 and SCD2 result tables.*

## Run Day 2 in Fabric

### 1. Change only the demo day

Return to the day cell and change it to:

```python
DEMO_DAY = 2
```

### 2. Rerun the complete notebook

Use **Run all** or run every block again from **0. Environment** through **7. Inspect current and historical results**.

The notebook replaces Bronze with the complete Day 2 snapshot. The sequence-safety block confirms that the expected earlier SCD2 state exists before either target is updated.

Product `P002` has a new `list_price`:

- SCD1 updates the value on `P002`'s existing row and keeps eight rows.
- SCD2 closes the earlier `P002` version and inserts a new current version.

### 3. Check the Day 2 output

You should see:

```text
SCD1 rows: 8
SCD2 versions: 9
```

In the SCD2 display, `P002` now has one historical version and one current version.

*Image coming soon: Day 2 SCD1 result and the two SCD2 versions for P002.*

## Run Day 3 in Fabric

### 1. Change only the demo day

Return to the day cell and change it to:

```python
DEMO_DAY = 3
```

### 2. Rerun the complete notebook

Run every block again. The notebook replaces Bronze with the complete Day 3 snapshot and verifies the prior SCD2 state.

Product `P001` has a new `product_category`:

- SCD1 replaces the category on `P001`'s current row and keeps eight rows.
- SCD2 closes the earlier `P001` version and inserts a new current version.

### 3. Check the Day 3 output

You should see:

```text
SCD1 rows: 8
SCD2 versions: 10
```

The final SCD2 display shows the historical and current versions ordered by `product_id` and `_effective_from`. Use `_effective_to` and `_is_current` to distinguish closed history from the current record.

*Image coming soon: Day 3 SCD1 result and final 10-version SCD2 history.*

!!! warning "Keep the days in order"

    Run Day 1 → Day 2 → Day 3. The sequence-safety block stops if an expected prior state is missing. Replaying the current day is safe because unchanged tracked values do not create another SCD2 version.

## Expected result

### Data saved by the demo

| Location | Table | Final state after Day 3 |
| --- | --- | --- |
| Bronze Lakehouse | `demo.product_master_updates` | The complete eight-row Day 3 Product Master snapshot. |
| Silver Lakehouse | `demo.product_master_scd1` | Eight current product rows with the latest values. |
| Silver Lakehouse | `demo.product_master_scd2` | Ten versions: eight current versions and two closed historical versions created by the Day 2 and Day 3 changes. |

### Metadata saved by FabricOps

All metadata is routed to the Metadata Lakehouse configured by `00_env_config`.

| Metadata table | What this demo records |
| --- | --- |
| `METADATA_DATA_CATALOGUE` | Canonical table and column identities for the Bronze source and both Silver targets. |
| `METADATA_DATA_PROFILED` | Profile snapshots for each Full Read source snapshot and each published SCD target. |
| `METADATA_DATA_PROFILED_FREQUENCY` | Frequency rows linked to those profile snapshots where applicable. |
| `METADATA_DATA_LINEAGE` | The source and both target roles for this notebook pipeline. |
| `METADATA_SOURCE_OBSERVATION` | Source-state observations associated with successful target publication where applicable. |
| `METADATA_GUARDRAIL_RESULTS` | Guardrail evaluation results when a selected Data Contract supplies executable Guardrails. |

*Image coming soon: Metadata Lakehouse records after the three SCD runs.*

### Reset the demo

Do not restart at Day 1 while either SCD target still contains later-day state. Reset the source and both targets together:

1. In the Bronze Lakehouse, delete `demo.product_master_updates` from the table explorer.
2. In the Silver Lakehouse, delete both targets:
    - `demo.product_master_scd1`
    - `demo.product_master_scd2`
3. Set `DEMO_DAY = 1`.
4. Run the notebook from the top. The Day 1 CSV recreates the eight-row Bronze snapshot, WRITE 1 recreates the eight-row SCD1 target, and WRITE 2 recreates the eight initial SCD2 versions.
5. Continue with Day 2 and Day 3 in order.

Deleting only the Bronze source is not enough: retained SCD targets still contain the previous current state and history. Conversely, deleting only the targets leaves the Bronze table on its later snapshot until the Day 1 staging cells run.

!!! note "Governance and metadata history"

    The steps above reset the business data. Existing Catalogue, profile, and lineage records remain as FabricOps run history. If Data Contracts or other Governance metadata were authored specifically for these demo identities and you need a completely new governance lifecycle, use a fresh Guided Demo environment or reset those records only through the normal FabricOps Governance workflow.

**Continue the main Guided Demo:** [Step 3. Author and freeze the Data Contract](03-author-and-freeze-data-contract.md)
