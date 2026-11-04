# Step 2B. Compare Append All and Append New Only

Run the same Full Read output through two Write Modes and observe which rows each target retains.

### Before you begin

1. Download [`02B_incremental_append_demo.ipynb`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/DemoData/02B_incremental_append_demo.ipynb) into Engineering Development. The existing filename is retained; the notebook now compares both append modes.
2. Keep `00_env_config.ipynb` beside it and attach the Fabric Environment from [Step 00B](00B-configure-environment-and-load-assets.md).
3. Upload the demo CSVs from Step 00B and run [Step 00C](00C-prepare-demo-data-with-fabricops-io.md) to stage Day 1. Day 2 reads `Demo/inventory_day2.csv` directly from Bronze Lakehouse `Files/Demo`.
4. Start with fresh targets and run Day 1, Day 2 and Day 3 in order. Do not rerun 00C after advancing Bronze.

![File upload](../assets/2b/File%20Upload.png)

!!! note "Publication and Governance"
    Use Ungoverned for the initial observation run against targets that are not already governed. Read and Write calculate due profiles automatically; finalize with `pipeline_result = finalize_pipeline(pipeline)`. Dry Run evaluates the prepared input without persisting target data, observations or run records; it does not demonstrate the persisted counts or target hash filtering below.

    After observation, author and freeze separate target Contracts with Processing strategies **Append All** and **Append New Only** in `01_governance`. Governed requires approved activations and remains blocked pending trusted deployment verification. See the [execution boundaries](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/README.md#source-participation-and-execution-boundaries).

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-carrying.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## The big picture

One Bronze source, one Full Read, one transformed DataFrame and two separate Silver targets.

</div>
</div>

| Role | Location | Mode |
| --- | --- | --- |
| Source | Bronze · `demo.inventory_movements` | `read_mode="full"` |
| Target A | Silver · `demo.inventory_movements_append_all` | `write_mode="append_all"` |
| Target B | Silver · `demo.inventory_movements_append_new_only` | `write_mode="append_new_only"` |

| Day | Source rows | Append All total | Append New Only total |
| --- | ---: | ---: | ---: |
| 1 | 8 | 8 | 8 |
| 2 | 12 | 20 | 12 |
| 3 | 12 | 32 | 12 |

Counts assume exactly one complete persistent execution per day, fresh Silver targets and unchanged transformation/schema. Both Write blocks receive exactly the same `transformed_df` object. Full Read needs no watermark or target checkpoint.

### Configure Read → Transform → Write

Run Environment, the demo-day and Bronze preparation cells, then Setup Pipeline. Setup Pipeline discovers notebook identity automatically in persistent modes; pipeline source participation is automatic.

```python
source = orchestrate_read(
    store="Bronze", schema="demo", table_name="inventory_movements",
    read_mode="full", verbose=True,
)
sources["inventory_movements"] = source

transformed_df = (
    sources["inventory_movements"]["dataframe"]
    .withColumn("movement_date", F.to_date("modified_datetime"))
    .withColumn("quantity_in", F.greatest(F.col("quantity_change"), F.lit(0)))
    .withColumn("quantity_out", F.greatest(-F.col("quantity_change"), F.lit(0)))
)

writes["inventory_movements_append_all"] = orchestrate_write(
    transformed_df,
    store="Silver", schema="demo", table_name="inventory_movements_append_all",
    write_mode="append_all", verbose=True,
)
writes["inventory_movements_append_new_only"] = orchestrate_write(
    transformed_df,
    store="Silver", schema="demo", table_name="inventory_movements_append_new_only",
    write_mode="append_new_only", verbose=True,
)
```

The notebook retains separate Read, Transform and Write cells. `F`, `sources` and `writes` are initialized there. Inline previews show prepared input; read persisted Silver separately to assess publication.

!!! warning "Independent publications"
    The two Writes are not atomic together. If Target A succeeds and Target B fails, inspect publication results and recover the failed publication before starting another execution. A new full execution adds the complete input to Append All again. Exact publication retries use verified receipts; they are different from new executions.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Run Day 1

Read all eight staged movements and publish eight rows to each fresh target.

</div>
</div>

Set `DEMO_DAY = 1`, then run the notebook from the top through Finalize. The preparation cell leaves the Day 1 source staged by 00C unchanged. Both targets should contain eight rows.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Run Day 2

Add four Bronze movements, then send all 12 source rows to both targets.

</div>
</div>

Set `DEMO_DAY = 2` and start a fresh execution from the top. The preparation cell unions the Day 2 CSV with Bronze and deduplicates `movement_id`, so repeating preparation does not add extra source movements. This source preparation happens before pipeline selection and can change Bronze even when the later pipeline uses Dry Run.

Append All adds 12 rows to the existing eight, reaching **20**. Append New Only collapses incoming identical hashes and compares them with published `_row_hash` values using a distributed anti-join. Only the four unseen rows are inserted, reaching **12**.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Run Day 3

Leave Bronze unchanged and submit the same 12-row Full Read again.

</div>
</div>

Set `DEMO_DAY = 3` and start a fresh execution from the top. Append All adds 12 more rows, reaching **32**. Append New Only stays at **12**. The Read is still full and nonempty.

??? info "Unchanged data, no-op and publication receipts"
    A newly evaluated Append New Only batch with no unseen hashes returns `published=False` and `publication_status="no_unseen_hashes"`: a nonpublishing no-op. An unchanged exact batch may instead recover a verified earlier receipt as `already_applied` (or `metadata_recovered`); that also inserts no additional rows. Do not confuse either result with `empty_incremental_scope`.

    `METADATA_PROCESSING_STATE` stores target-specific publication receipts and accepted Source Observation baselines. Physical target markers and commits verify recovery before progress is accepted. A nonpublishing no-op does not accept a newer full observation baseline or consume its interval. Receipts do not make a new Append All full execution deduplicate its input.

### Inspect the persisted counts

After both Writes, inspect the actual targets in a persistent run, then run Finalize:

```python
for target in ("inventory_movements_append_all", "inventory_movements_append_new_only"):
    saved = read_lakehouse_table(store="Silver", schema="demo", table_name=target)
    print(target, saved.count())

pipeline_result = finalize_pipeline(pipeline)
```

Do not read nonexistent targets after a Dry Run. Day 3 should retain 12 distinct movement IDs in each target, but Append All has 32 rows and Append New Only has 12 rows.

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Choose the processing strategy

Choose extraction scope and target behavior independently.

</div>
</div>

| Combination | Choose it when | Cost or responsibility |
| --- | --- | --- |
| Incremental Read + Append All | Large sources have reliable watermarks or change tracking and append-only events. | Reads newly eligible records and avoids repeated complete processing scans; requires correct checkpoints and replay handling. Replaying consumed records as new work can duplicate them. |
| Full Read + Append New Only | Duplicate prevention matters, or reliable incremental extraction is unavailable. | Reads the complete source each time and inserts only unseen `_row_hash` values; pays for full scanning and distributed hash comparison. |
| Incremental Read + Append New Only | Reliable incremental extraction can limit scope and hash comparison should also prevent replay duplicates. | Compares only eligible records; cannot recover late or changed rows excluded by the watermark. |

??? info "Watermarks and hash boundaries"
    Incremental extraction requires a target-specific identity and a reliable advancing watermark. Use `read_mode="incremental"`, `target_table_id=resolve_table_id(...)` and `read_parameters={"watermark_column": "modified_datetime"}`; see the [reference example](../reference/read-and-load-strategies.md#incremental). This is an alternative experiment, not the configuration used for the count comparison. Due profiling or Full Source Observation may still scan the full source.

    Hashes describe final values and logical types after transformation and Sensitive Data treatment. Source Job IDs and timestamps participate; FabricOps audit and SCD lifecycle fields are excluded. Adding a volatile input field can make unchanged business rows hash differently. Existing targets must have valid historical hashes. See the [hash contract](../reference/read-and-load-strategies.md#mandatory-row-hashes).

    Append New Only inserts changed hashes as **new records**, even for the same business key. It does not update existing business keys, infer deletions or remove pre-existing duplicates. Use [SCD1 or SCD2](02C-build-and-run-scd-etl.md) for business-key-based state management.

### Expected result

Bronze ends at 12 movements; Silver Target A has 32 rows and Target B has 12. You can explain why Full Read + Append All repeats rows and why Full Read + Append New Only retains only unseen row hashes.

### Metadata saved by FabricOps

Persistent executions use the Metadata Lakehouse configured by `00_env_config`. Dry Run keeps its summary in session only.

| Table | Purpose in this demo |
| --- | --- |
| `METADATA_PIPELINE_RUN` | Finalized execution outcome and operations. |
| `METADATA_DATA_CATALOGUE` | Source and separate target identities, columns and processing definitions. |
| `METADATA_DATA_PROFILED` | Due source/target profile snapshots; a nonpublishing no-op does not profile a newly published target. |
| `METADATA_DATA_PROFILED_FREQUENCY` | Frequency rows linked to applicable profiles. |
| `METADATA_DATA_LINEAGE` | Source and both targets' pipeline participation. |
| `METADATA_PROCESSING_STATE` | Captured source observations, accepted baselines and target-specific publication receipts when applicable; this Full Read comparison does not consume incremental checkpoints. |
| `METADATA_GUARDRAIL_RESULTS` | Results of applicable selected Contract Guardrails when evaluated. |

### Repeat and recover safely

Repeated Day 2 staging keeps Bronze unique, but a new Append All execution repeats its full input. Extra executions change the expected totals. For an independent replay, use a fresh demo environment or separate table identities and approved Contracts. Preserve the target, its markers and scoped Processing State together.

If counts differ, check whether Bronze was staged, whether a Write failed, whether the execution published, and whether extra full executions ran. Inspect the targets and returned publication statuses before retrying. Do not empty checkpoints, delete only a target, or overwrite to hide a mismatch. Reconcile the exact target and receipt history with its owner; this comparison is not a production repair procedure.

**Next:** [Step 2C. Compare SCD1 and SCD2](02C-build-and-run-scd-etl.md)
