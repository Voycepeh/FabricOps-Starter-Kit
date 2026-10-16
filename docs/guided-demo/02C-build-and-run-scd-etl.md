# Step 2C. Run the SCD1 and SCD2 Demo

### Before you begin

1. Download [`02C_scd_demo.ipynb`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/DemoData/02C_scd_demo.ipynb) and import it into the Engineering Development workspace.
2. Keep `00_env_config.ipynb` beside it and attach the same Fabric Environment used in Step 00B.
3. Make sure you have already uploaded the demo files required for this demo in the previous step [Step 00B](00B-configure-environment-and-load-assets.md).

4. Run [Step 00C](00C-prepare-demo-data-with-fabricops-io.md) first for Day 1. For Days 2 and 3, the notebook reads `Demo/products_day2.csv` and `Demo/products_day3.csv` directly from Bronze Lakehouse `Files/Demo`. There is no `scd_product_master` subfolder.
5. Use a fresh demo state and run Day 1, then Day 2, then Day 3.

![File upload](../assets/2c/File%20Upload.png)

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## The big picture

Change the Step 2 Write strategy to SCD1 and SCD2, then compare how both targets record the same source changes.

</div>
</div>

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

??? info "Frequency profiling controls"

    The notebook sets `frequency_enabled=True` and `frequency_top_n=5` on its `orchestrate_read()` and `orchestrate_write()` calls. This retains up to five frequency values per eligible column.

    For faster runs when frequency distributions are not needed, set `frequency_enabled=False` on the relevant orchestrator call. The standard statistical profile still runs. Setting `frequency_top_n=None` retains all frequency values when enabled, but does not avoid the cost of calculating them.

The standard Environment, Data Contract, result-storage, and inspection patterns are explained in [Step 2](02-build-and-run-etl.md). This page covers only the day selection, snapshot staging, and SCD outcomes.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Run Day 1 in Fabric

Establish the baseline with one complete Full Read, PySpark Transform, and pair of SCD Writes.

</div>
</div>

### Choose Day 1

Leave the value under **1. Choose the demo day** as:

```python
DEMO_DAY = 1
```

Run the cell. It validates that the selected day is supported.

### Stage the Day 1 snapshot

Run the short cell under **2. Advance the Bronze product snapshot**.

00C has already loaded Day 1 into Bronze `demo.product_master_updates`. The scenario cell does nothing on Day 1; for Days 2 and 3 it overwrites Bronze with the selected eight-row snapshot.

The cell should complete without an error. Bronze now contains the complete Day 1 Product Master snapshot.

*Image coming soon: Day 1 Product Master snapshot saved in Bronze.*

### Run the changed pipeline blocks

Run the remaining blocks through **5. Inspect**. For the initial Guided Demo run, leave the Data Contract selection unchanged.

The changes from Step 2 are:

- **Governed Full Read:** reads the complete eight-row Product Master snapshot into `sources["product_master"]`.
- **PySpark Transform:** selects the Product Master columns and casts `list_price` to double and `modified_datetime` to timestamp.
- **WRITE 1 — SCD1 current state:** keys Silver `demo.product_master_scd1` by `product_id` and keeps one current row per product.
- **WRITE 2 — SCD2 history:** uses `modified_datetime` as the effective column and tracks changes to `product_category` and `list_price` in Silver `demo.product_master_scd2`.

*Image coming soon: Day 1 Product Master Full Read output.*

*Image coming soon: transformed Day 1 Product Master DataFrame.*

*Image coming soon: Day 1 SCD1 Write output.*

*Image coming soon: Day 1 SCD2 Write output.*

### Inspect the Day 1 profiles

Run the cell under **5. Inspect**. It displays the `profile_result` already returned by each governed Write; it does not read either Silver table again.

The SCD1 and SCD2 profiles should both show `row_count = 8` on their profiled columns.

*Image coming soon: Day 1 SCD1 and SCD2 target profiles.*

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Run Day 2 in Fabric

Apply the next source change and compare the resulting governed output.

</div>
</div>

### Change only the demo day

Return to the day cell and change it to:

```python
DEMO_DAY = 2
```

### Rerun the complete notebook

Use **Run all** or run every block again from **0. Environment** through **5. Inspect**.

The notebook replaces Bronze with the complete Day 2 snapshot. The sequence-safety block confirms that the expected earlier SCD2 state exists before either target is updated.

Product `P002` has a new `list_price`:

- SCD1 updates the value on `P002`'s existing row and keeps eight rows.
- SCD2 closes the earlier `P002` version and inserts a new current version.

### Check the Day 2 output

The SCD1 profile should show `row_count = 8`; the SCD2 profile should show `row_count = 9`, confirming that the changed `P002` created one additional historical version.

*Image coming soon: Day 2 SCD1 and SCD2 target profiles.*

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Run Day 3 in Fabric

Run the final scenario and inspect how the output changes.

</div>
</div>

### Change only the demo day

Return to the day cell and change it to:

```python
DEMO_DAY = 3
```

### Rerun the complete notebook

Run every block again. The notebook replaces Bronze with the complete Day 3 snapshot and verifies the prior SCD2 state.

Product `P001` has a new `product_category`:

- SCD1 replaces the category on `P001`'s current row and keeps eight rows.
- SCD2 closes the earlier `P001` version and inserts a new current version.

### Check the Day 3 output

The SCD1 profile should show `row_count = 8`; the SCD2 profile should show `row_count = 10`, confirming that the changed `P001` created one additional historical version.

*Image coming soon: Day 3 SCD1 and SCD2 target profiles.*

!!! warning "Keep the days in order"

    Run Day 1 → Day 2 → Day 3. The sequence-safety block stops if an expected prior state is missing. Replaying the current day is safe because unchanged tracked values do not create another SCD2 version.

### Expected result

Day 1 creates eight current records in each target, Day 2 creates the first historical SCD2 version, and Day 3 creates the second while SCD1 remains at eight current rows.

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
