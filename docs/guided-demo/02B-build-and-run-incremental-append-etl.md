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

Profiling schedules and Read/Write triggers are saved per table in Data Contract Authoring. Standard pipeline calls need no profiling options.

### Set up the pipeline

Run Environment, choose `DEMO_DAY`, and run the explicit Bronze source-preparation cell. That setup can change Bronze before pipeline selection. The default pipeline setup is:

```python
PIPELINE_ID = "02B_incremental_append_demo"
PIPELINE_MODE = "Test"  # Test or Live
CONTRACTS = setup_pipeline(pipeline_id=PIPELINE_ID, pipeline_mode=PIPELINE_MODE)
```



After Governance freezes contracts, select exact frozen versions in Test setup before Read. Test never publishes or commits metadata. Existing approved Live configurations remain subject to activation and destination checks. See the [execution boundary and activation limits](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/README.md#source-participation-and-execution-boundaries).

Individual Guardrail stages are omitted when no Data Contract is selected; skipped check fields remain in the returned dictionaries. Persisted row counts and saved-data screenshots below require approved Live publication. Advance the demo day only after publication succeeds.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Run Day 1 in Fabric with approved Live publication

For Day 1 , we load 8 rows of data from 
Bronze Lakehouse "demo.inventory_movements" table and load all 8 rows into
Silver Lakehouse "demo.inventory_movements_incremental" and set "modified_datetime" column as our watermark column

</div>
</div>


![Day 1 demo day selection](../assets/2b/Day%201.png)

Ocestrate Read: 
Set a target table a read mode (incremental/full) and a Watermark Column

![Incremental Read configuration](../assets/2b/Incremental_Read.png)

The inline Read preview displays the eligible rows directly below `orchestrate_read()`. The initial Day 1 run should read 8 rows.

![Incremental Read DataFrame preview](../assets/2b/Incremental_Read_inspect.png)

Ocestrate Write: 
Set a single or multiple source table and Write mode = "Append"

![Incremental Write configuration](../assets/2b/Incremental_Write.png)

The inline Write preview displays the submitted rows directly below `orchestrate_write()`. Verify committed rows in the Silver target separately.

![Incremental Write DataFrame preview](../assets/2b/Incremental_Write_Inspect.png)

## Info How Does Incremental Load Work in FabricOps?

### FabricOps handles incremental loading through two orchestrators:

Each Read and Write block displays its actual DataFrame directly after orchestration; there is no separate Inspect selector. The Read preview shows the eligible incremental batch, not the full persisted target.

1. orchestrate_read() identifies and reads only new or modified records using a watermark.

2. orchestrate_write() applies the selected write strategy, such as Append, and commits watermark progress only after a successful publication.

### How It Works

1. Identify the source: Bronze Lakehouse demo.inventory_movements.
2. Identify the target: Silver Lakehouse demo.inventory_movements_incremental.
3. Retrieve the committed watermark for this source-to-target relationship.
4. Check Bronze for records where:modified_datetime > last_committed_watermark
5. Read only newer records, transform them, and append them to Silver.
6. Advance the watermark only after successful write.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Restart the session and repeat Day 1 with a fresh Testing plan

Run through setup again with approved Live publication, then continue. Since Day 1 already committed its watermark, the Read and Write have an empty incremental scope.

</div>
</div>

No new data so its empty read

![Incremental Read preview after rerunning Day 1](../assets/2b/Incremental_Read_Day1_again.png)

No new data so its empty write

![Incremental Write preview after rerunning Day 1](../assets/2b/Incremental_Write_Day1_again.png)

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Change the demo day to 2 and select a fresh plan

For Day 2 , our underlying data has 12 rows of data in 
Bronze Lakehouse "demo.inventory_movements" table of which 8 were already loaded into Silver Lakehouse "demo.inventory_movements_incremental" in day 1 , hence only 4 rows of data was read and appended

</div>
</div>

![Day 2](../assets/2b/Day 2.png)

4 new rows are read based on the watermark column

![Day 2 incremental Read preview](../assets/2b/Incremental_Read_Day2.png)

Only this 4 rows are appended

![Day 2 incremental Write preview](../assets/2b/Incremental_Write_Day2.png)

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Change the demo day to 3 and select a fresh plan

For Day 3, our underlying data still has 12 rows of data in 
Bronze Lakehouse "demo.inventory_movements" table of which 12 were already loaded into Silver Lakehouse "demo.inventory_movements_incremental" in day 1 , hence only 0 rows of data was read and appended

</div>
</div>

![Day 3 demo run](../assets/2b/Day%203.png)

No new data so its empty read

![Incremental Read inspection after rerunning Day 1](../assets/2b/Incremental_Read_Day1_again.png)

No new data so its empty write

![Incremental Write inspection after rerunning Day 1](../assets/2b/Incremental_Write_Day1_again.png)


### Expected result

Day 1 publishes the eight-row baseline, Day 2 appends four newly eligible rows, and Day 3 leaves the 12-row target unchanged because its incremental scope is empty.

Complete Read → Transform → Write for each pending batch before reading a newer source state for this target. If a newer Read reports that another state is awaiting publication, publish or retry the existing prepared DataFrame first, then repeat the newer Read. If that DataFrame was discarded, create a fresh pipeline plan/run and rerun Read → Transform → Write in the same notebook session; do not reset the checkpoint. Re-reading unchanged state remains allowed.

### Data saved by the demo

| Location | Table | Final state after Day 3 |
| --- | --- | --- |
| Bronze Lakehouse | `demo.inventory_movements` | 12 unique source movements from Days 1 and 2. |
| Silver Lakehouse | `demo.inventory_movements_incremental` | 12 transformed movements appended across the successful incremental runs. |

### Metadata saved by FabricOps

The following records are committed by successful runs with approved **Live** publication and routed to the Metadata Lakehouse configured by `00_env_config`. Test retains diagnostics in memory during Read and Write; `finalize_pipeline(CONTRACTS)` publishes only run and Guardrail results for activation review.

| Metadata table or governed record | What this demo records |
| --- | --- |
| `METADATA_DATA_CATALOGUE` | Canonical source and target table and column identities. |
| `METADATA_DATA_PROFILED` | Profile snapshots of the published Silver target. Incremental Read batches themselves are not profiled. |
| `METADATA_DATA_PROFILED_FREQUENCY` | Target frequency rows linked to profile snapshots where applicable. |
| `METADATA_DATA_LINEAGE` | The Bronze source and Silver target participation for this notebook pipeline. |
| `METADATA_SOURCE_OBSERVATION` | Source-state observations and history used by Incremental execution. |
| Governed target watermark | Successful watermark progress for the exact Bronze-to-Silver relationship. |
| `METADATA_GUARDRAIL_RESULTS` | Guardrail evaluation results when a selected Data Contract supplies executable Guardrails. |

### If Silver has eight rows but the checkpoint already covers Day 2

Pause this target's scheduled and interactive writers. Keep the existing tables and `METADATA_SOURCE_OBSERVATION` history. An empty Incremental Read cannot repair a previously accepted checkpoint that is ahead of Silver, and the package never automatically lowers that checkpoint.

1. Upgrade the package and run `setup_metadata_tables()` through the configured environment to add nullable `publication_payload_json` and `run_id` columns. This additive setup preserves existing metadata. Restart the owning notebook's Fabric session so it loads the corrected package and has no pending state from the failed run.
2. Read Bronze and Silver explicitly with `read_lakehouse_table()`. Verify Bronze contains exactly M001–M012, Silver has unique, non-null movement keys, and every existing Silver business row equals the corresponding transformed Bronze row. Use the notebook's Transform expression, including `movement_date`, `quantity_in` and `quantity_out`. Compare all business columns, excluding FabricOps audit columns. **Stop if any existing key has conflicting values, unexpected rows, or duplicates.** This repair applies to this immutable Append demo; it is not a general repair for mutable source history.
3. Build a fresh **Live** plan in the same owning notebook, with the approved active source and target contracts. Select Full Read for the repair, then run the existing Transform against that complete source. Evaluation-only Testing can validate the repair input. Publication to a Live-owned destination requires the approved Live configuration; if the repair changes Read strategy, complete Testing and coordinated approval of that repair configuration first.
4. Construct and inspect only the missing keys before choosing to publish:

    ```python
    existing = read_lakehouse_table(
        "inventory_movements_incremental", store="Silver", schema="demo",

    )
    # transformed_df comes from the Full Read and the unchanged demo Transform.
    business_columns = [
        "movement_id", "product_id", "movement_type", "quantity_change",
        "modified_datetime", "movement_date", "quantity_in", "quantity_out",
    ]
    expected = transformed_df.select(*business_columns)
    existing_business = existing.select(*business_columns)
    for frame in (expected, existing_business):
        if frame.where(F.col("movement_id").isNull()).limit(1).count() or frame.groupBy("movement_id").count().where("count > 1").limit(1).count():
            raise ValueError("Null or duplicate movement keys; stop reconciliation.")
    if existing_business.exceptAll(expected).limit(1).count():
        raise ValueError("Existing Silver rows conflict with the transformed source; stop reconciliation.")
    missing = expected.join(existing.select("movement_id"), "movement_id", "left_anti")
    display(missing)
    ```

    For the reported mismatch, the missing set must be exactly M009–M012. Review that set and explicitly choose to execute the existing `orchestrate_write()` call with `missing` as its DataFrame, the Full Read result in `sources`, `write_mode="append"`, and the fresh Live plan. Do not execute the ordinary incremental write in this repair run. Do not bypass Guardrails or notebook ownership.
6. Restore Incremental Read, build a fresh plan, and run Day 3. It should return an empty scope and keep Silver at 12 rows. Repeat Day 2 and Day 3 to verify stable results.

Source Observation records use the same `run_id` as `METADATA_PIPELINE_RUN`; multiple runs may retain the same real `_activity_id`. New runs isolate pending source state, while exact batch receipts allow recovery across run IDs. Run `setup_metadata_tables()` to add nullable `run_id` and `publication_payload_json` columns without resetting existing history.

New writes stage an exact batch receipt before publication. Recovery verifies its Delta commit and target marker; legacy activity-only staged observations are not automatically promoted. A fresh target with a populated Silver table and no accepted baseline still fails safely. If the subset checks above do not hold, reconcile the exact source-to-target relationship with its owner rather than resetting production metadata.

The Write result distinguishes `published`, `already_applied`, and `empty_incremental_scope`; Testing reports no publication. `already_applied` means the exact batch was verified. SCD row metrics remain `Not available` when the runtime cannot measure business changes reliably.

### Reset the disposable demo environment

Use this only to start a disposable demo over. For checkpoint/target divergence, use the verification and repair procedure above.

An Incremental demo cannot be reset by rerunning Day 1 or deleting only the Silver target. FabricOps remembers successful progress for the exact Bronze-to-Silver relationship.

1. In the Bronze Lakehouse, delete `demo.inventory_movements` from the table explorer.
2. In the Silver Lakehouse, delete `demo.inventory_movements_incremental` from the table explorer. This removes the appended business data and the successful watermark progress stored with the governed target.
3. Remove only the `METADATA_SOURCE_OBSERVATION` rows for the `inventory_movements` → `inventory_movements_incremental` relationship and the current environment. Do not clear observations for other pipelines.
4. Set `DEMO_DAY = 1`.
5. Rerun [Step 00C](00C-prepare-demo-data-with-fabricops-io.md) to restore the eight-row Day 1 Bronze source. Day 1 of this notebook does not load its own CSV.
6. Run the notebook with an existing approved Live configuration, then continue. The Incremental Read bootstraps again and Append recreates the eight-row Silver target.

!!! warning "Keep incremental state aligned"

    The Bronze source, Silver target, scoped Source Observation history, and governed target watermark belong to one incremental state. Reset all four together. If you cannot perform the scoped metadata cleanup safely, use a fresh Guided Demo environment instead.

**Next optional processing mode:** [Step 2C. Run the SCD1 and SCD2 Demo](02C-build-and-run-scd-etl.md)

**Continue the main Guided Demo:** [Step 3. Author and freeze the Data Contract](03-author-and-freeze-data-contract.md)
