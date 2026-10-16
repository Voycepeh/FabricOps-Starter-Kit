# Step 2B. Run the Incremental Append Demo

### Before you begin

1. Download [`02B_incremental_append_demo.ipynb`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/DemoData/02B_incremental_append_demo.ipynb) and import it into the Engineering Development workspace.
2. Keep `00_env_config.ipynb` beside it and attach the same Fabric Environment used in Step 00B.
3. Make sure you have already uploaded the demo files required for this demo in the previous step [Step 00B](00B-configure-environment-and-load-assets.md).

4. Run [Step 00C](00C-prepare-demo-data-with-fabricops-io.md) first to stage Day 1. For Day 2, the notebook reads `Demo/inventory_day2.csv` directly from Bronze Lakehouse `Files/Demo`. There is no `incremental_inventory` subfolder.

![File upload](../assets/2b/File%20Upload.png)

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## The big picture

Change the Step 2 scaffold to an Incremental Read and Append Write, then compare its state across three runs.

</div>
</div>

| Run | What changes | Expected Silver rows |
| --- | --- | ---: |
| Day 1 | Use the eight movements staged by 00C and bootstrap the Incremental Read. | 8 |
| Day 2 | Add four movements and append only the newly eligible rows. | 12 |
| Day 3 | Add no source rows and observe an empty incremental scope. | 12 |

The notebook uses these governed tables throughout:

| Role | Location | Processing |
| --- | --- | --- |
| Source | Bronze Lakehouse · `demo.inventory_movements` | Incremental on `modified_datetime` |
| Target | Silver Lakehouse · `demo.inventory_movements_incremental` | Append |

??? info "Frequency profiling controls"

    The notebook sets `frequency_enabled=True` and `frequency_top_n=5` on its `orchestrate_read()` and `orchestrate_write()` calls. This retains up to five frequency values per eligible column.

    For faster runs when frequency distributions are not needed, set `frequency_enabled=False` on the relevant orchestrator call. The standard statistical profile still runs. Setting `frequency_top_n=None` retains all frequency values when enabled, but does not avoid the cost of calculating them.

The standard Environment, Data Contract, result-storage, and inspection patterns are explained in [Step 2](02-build-and-run-etl.md). This page covers only the day selection, source staging, incremental scope, and resulting target state.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Run Day 1 in Fabric

Establish the baseline with one complete Incremental Read, PySpark Transform, and Append Write.

</div>
</div>

### Choose Day 1

Leave the value under **1. Choose the demo day** as:

```python
DEMO_DAY = 1
```

![Day 1 demo day selection](../assets/2b/Day%201.png)

Run the cell. It validates that the selected day is supported.

### Stage the Day 1 source

Run the short cell under **2. Advance the Bronze source (Day 2 only)**. Day 1 needs no additional staging.

00C has already loaded the Day 1 Bronze `demo.inventory_movements` table. The scenario cell does nothing on Day 1. On Day 2, it adds the new inventory movements to Bronze without duplicating existing `movement_id` values.

You should see:

![Day 1 Bronze staging output showing 8 rows](../assets/2b/Day%201%20Bronze%20staging%20output%20showing%208%20rows.png)

### Run the changed pipeline blocks

Run the remaining blocks through **5. Inspect**. For the initial Guided Demo run, leave the Data Contract selection unchanged.

The changes from Step 2 are:

- **Governed Incremental Read:** resolves the Silver target identity, uses `modified_datetime` as the watermark, and saves the Bronze result as `sources["inventory_movements"]`.
- **PySpark Transform:** derives `movement_date`, `quantity_in`, and `quantity_out` from the eligible rows.
- **Governed Append Write:** appends `transformed_df` to Silver `demo.inventory_movements_incremental` and saves the result as `writes["inventory_movements_incremental"]`.

On Day 1, there is no earlier successful watermark for this source-to-target relationship. The incremental scope therefore bootstraps with all eight source rows.

*Image coming soon: Day 1 Incremental Read output and bootstrap scope.*

*Image coming soon: transformed Day 1 inventory movements.*

*Image coming soon: Day 1 Append Write output.*

### Inspect the Day 1 profile

Run the cell under **5. Inspect**. It uses the `profile_result` already returned by the governed Write; it does not read the Silver table again.

You should see:

- an incremental scope covering the initial eight rows;
- the persisted-target profile for `demo.inventory_movements_incremental`; and
- `row_count = 8` on its profiled columns.

*Image coming soon: Day 1 incremental scope and persisted-target profile.*

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

![Day 2](../assets/2b/Day 2.png)

### Rerun the complete notebook

Use **Run all** or run every block again from **0. Environment** through **5. Inspect**.

The Bronze staging block adds the four Day 2 movements and keeps the eight existing movements by `movement_id`. You should see:

```text
Bronze inventory rows after Day 2: 12
```

The Incremental Read returns only the four rows after the successful Day 1 watermark. The Append Write adds those rows to the Silver target.

### Check the Day 2 output

The final inspection should show:

- four newly eligible rows in the incremental scope;
- the new persisted-target profile; and
- `row_count = 12` on its profiled columns.

*Image coming soon: Day 2 incremental scope and 12-row target profile.*

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
![Day 3 demo run](../assets/2b/Day%203.png)

Day 3 intentionally has no CSV file and adds no source records.

### Rerun the complete notebook

Run every block again. The notebook still calls the Read and Write orchestrators; do not skip those blocks.

You should see:

```text
Bronze inventory rows after Day 3: 12
```

The Incremental Read returns an empty scope. The Append target remains unchanged.

### Check the Day 3 output

The final inspection should show:

- an empty/no-change incremental scope;
- a new persisted-target profile with `row_count = 12`; and
- the same target row count as Day 2.

*Image coming soon: Day 3 empty scope and unchanged 12-row target profile.*

### Expected result

Day 1 publishes the eight-row baseline, Day 2 appends four newly eligible rows, and Day 3 leaves the 12-row target unchanged because its incremental scope is empty.

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
