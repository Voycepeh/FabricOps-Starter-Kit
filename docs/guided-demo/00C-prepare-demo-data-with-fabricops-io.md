# 0C. Prepare the demo data with FabricOps I/O

### Before you begin

Complete [Step 0B](00B-configure-environment-and-load-assets.md), import all three demo notebooks, and read [Reset, rerun and validate a package](#reset-rerun-and-validate-a-package) before executing 00C.

!!! warning "Dedicated demo environment only"

    Running 00C resets demo sources, all six outputs and applicable previous demo metadata. Stop schedules and interactive demo runs, review its preview and confirm `RESET DEMO`. Never run against unrelated production assets. Wait for `RESET COMPLETE` before starting Day 1.

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

### Load the shared 00_env_config notebook that is in the same workspace via our helper function (Or if you did want to point to a notebook in another workpace just pass the workpace id into the helper funciton)

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

## Read and Write Order History to the Gold Warehouse

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

## Prepare Day 1 for Append and SCD Demos

Initialize the Day 1 Bronze source tables for the Incremental Append vs Full Hash Append (02B) and SCD1/SCD2 (02C) demos.

</div>
</div>

This step prepares two dedicated Bronze tables using the sample CSV files:

| Source file | Bronze table | Used by |
|---|---|---|
| `Demo/inventory_day1.csv` | `demo.inventory_movements` | 02B incremental/full append comparison |
| `Demo/products_day1.csv` | `demo.product_master_updates` | 02C SCD1/SCD2 |

### Run the complete `00C_demo_setup` notebook, including confirmation and verification.

![Step 5: Prepare Day 1 for append and SCD demos](../assets/00C/step5.png)

The notebook reads each CSV file using `read_lakehouse_csv()` and writes it to the Bronze Lakehouse using `write_lakehouse_table()` with `mode="overwrite"`.

This initializes the Day 1 source tables before the first execution of the 02B and 02C notebooks.


### Expected result

After the notebook finishes, Engineering Development should contain the starting tables for all three Step 2 demos:

```text
bronze Lakehouse
  demo.orders
  demo.products
  demo.inventory_movements      # 02B append Day 1 baseline
  demo.product_master_updates   # 02C SCD Day 1 baseline

gold Warehouse
  demo.order_history
```

<div class="fabricops-section-banner" markdown="1">
<img src="/FabricOps-Starter-Kit/assets/mascots/robot-scanning.png" alt="" loading="lazy">
<div class="fabricops-section-content" markdown="1">

## Reset, rerun and validate a package

Use 00C as the single reset entrypoint for the dedicated Ungoverned engineering demo.

</div>
</div>

!!! warning "Destructive demo reset"

    00C overwrites five demo sources, removes all six demo outputs and deletes applicable demo metadata, including previous Run history. Use it only in the dedicated demo environment. Never point it at unrelated production assets. It preserves shared Governance and immutable deployment history and blocks ambiguous ownership.

### Preview and confirm

1. Install or upgrade the wheel being validated in the Fabric Environments, publish the Environments and start new notebook sessions as described in [00B](00B-configure-environment-and-load-assets.md). Record the installed version displayed by `setup_notebook()`; the regression target is v0.4.2 Ungoverned, while the notebook always runs the package actually installed.
2. Import 02A, 02B and 02C into Engineering Development **before running 00C**, keeping the names `02A_full_refresh_demo`, `02B_incremental_append_demo` and `02C_scd_demo`. 00C resolves their exact Fabric Notebook IDs; both paths in 02B use the same Pipeline ID and separate Run IDs.
3. Check the existing Bronze, Silver, Gold and Metadata mappings. Bronze, Silver and Metadata must be separate schema-enabled Lakehouses; Gold is a separate Warehouse. Run the installed package’s metadata setup/migration using 00B to provision or upgrade all current metadata tables, and create the Gold `demo` schema shown above before running 00C. Use the configured Metadata Lakehouse, never the attached/default Lakehouse as a substitute.
4. Stop demo schedules, jobs and interactive executions. Keep them stopped through verification. Set `DEMO_EXECUTIONS_STOPPED = True` in 00C. Run from the top through **reset-preview** and inspect the workspace/item identities, all five restores, six removals and remove/preserve counts for every metadata table.
5. After reviewing the preview, set `RESET_CONFIRMATION = "RESET DEMO"` in **reset-confirmation** and execute that cell, then **reset-apply**. The application consumes this confirmation. Unrelated pipelines may continue writing to the shared Metadata Lakehouse; only demo executions and metadata schema migrations must remain stopped during the reset. Continue through all the existing I/O examples and source writes, ending with **reset-verify**. Accept the reset only when it prints **`RESET COMPLETE`** and actual removal counts, including zeros. An exception means the reset is incomplete.

The restored sources are Bronze `demo.orders` (120), `demo.products` (8), `demo.inventory_movements` (8), `demo.product_master_updates` (8), and Gold `demo.order_history` (180). 00C compares their full row content with the Day 1 fixtures. Source files remain untouched.

| Demo | Output absent after reset |
| --- | --- |
| 02A | Silver `demo.curated_orders`; Gold `demo.customer_summary` |
| 02B | Silver `demo.inventory_movements_append_all`; `demo.inventory_movements_append_new_only` |
| 02C | Silver `demo.product_master_scd1`; `demo.product_master_scd2` |

??? info "Metadata reset coverage and ownership"

    All reads use the Metadata store and the configured Engineering/Governance schemas. Table identities come from `resolve_table_id()` with exact configured store/schema/table coordinates. Workspace scope is mandatory because Table IDs alone do not distinguish workspaces. Run operations must match the configured physical destinations as well.

    | Existing metadata table | Demo records and reset policy | State after reset |
    | --- | --- | --- |
    | `METADATA_PIPELINE_RUN` | Remove exact demo Notebook/Pipeline IDs in the execution workspace, including failed/terminated incomplete Ungoverned runs. Reject mixed participants, changed physical bindings or governed history. | No previous demo Runs; unrelated history retained. |
    | `METADATA_PROCESSING_STATE` | Remove demo-owned source observations, incremental checkpoints, drift baselines, full-source baselines and publication receipts using exact source/target, workspace, pipeline, Run and publication identifiers. Block links to unrelated owners. | No stale progress or receipts for the demo. |
    | `METADATA_DATA_LINEAGE` | Remove exact demo table/workspace participation with verified Notebook ownership. | No previous demo participation. |
    | `METADATA_DATA_CATALOGUE` | Remove table and column records for the 11 exact source/output identities in the execution workspace, only with verified demo Notebook ownership. This also clears processing definitions, profile candidates and profile timing fields. | No stale demo Catalogue entries. |
    | `METADATA_DATA_PROFILED` | Remove exact demo table/workspace profile snapshots with verified Notebook ownership. | No previous demo profiles. |
    | `METADATA_DATA_PROFILED_FREQUENCY` | Remove exact demo frequency records before profiles; check retained records do not reference removed profile/snapshot identifiers. | No previous demo frequencies or orphaned demo profile references. |
    | `METADATA_GUARDRAIL_RESULTS` | Ungoverned normally writes none. Remove applicable demo-owned results by exact Run/table/workspace/Notebook identifiers; block unrelated references. | Zero applicable demo results. |
    | `METADATA_DATA_ACCESS` | These notebooks do not scan access. Remove only demonstrably demo-owned records with exact table/workspace/Notebook scope if present. A separately owned scan blocks reset rather than losing its records. | Normally zero deletions; unrelated scans retained. |
    | `METADATA_PIPELINE_REGISTRY` | Ungoverned does not create promotion versions. Preserve immutable history; a demo binding or exact demo table use in this workspace blocks reset. | Unchanged; normally zero demo rows. |
    | `METADATA_PIPELINE_ACTIVATION` | These Ungoverned demos do not submit Governance decisions. Preserve history; a demo binding or exact demo table use in this workspace blocks reset. | Unchanged. |
    | `METADATA_DATA_CONTRACT` | These demos do not author Contracts. Preserve all versions; a Contract using demo evidence from this workspace blocks reset. | Unchanged. |
    | `METADATA_DATA_CONTRACT_ACTIVATION` | Preserve retained selections and Agreement associations. A demo Table ID in a configured physical demo workspace blocks reset. | Unchanged. |
    | `METADATA_DATA_AGREEMENT` | No writes from 00C or 02A–02C. Shared Governance records are never deleted. | Unchanged. |
    | `METADATA_DATA_STEWARD` | No writes from 00C or 02A–02C. Shared Governance records are never deleted. | Unchanged. |

    The reset deletes children before parents and Run history last. Native Delta deletion matches complete reviewed rows, including supported extension columns; it does not truncate, replace metadata tables, change schemas or delete by name substring.

    Confirmation rechecks demo ownership and the exact selected records, allowing unrelated metadata inserts and updates. Each deletion uses an isolated Delta commit tag: its metrics must report exactly the reviewed number of deleted demo rows and zero inserted/updated rows. This verifies the reset’s own changes without requiring unrelated workspaces to remain frozen. Final output reports actual deletions and the current remaining row count, which can differ from the preview because unrelated pipelines remain active.

    Processing State and profile links are checked before cleanup, and no selected demo records may remain afterward. Catalogue fields retain profile timing and candidates. Profiling policies live in preserved Contract payloads (Ungoverned uses fixed defaults), and outcomes live in Run `profiling`; there is no separate profiling schedule table.

??? info "After a metadata schema migration"

    Metadata migration remains owned by `setup_metadata_tables()` in 00B. Supported additive changes and known format upgrades preserve existing rows. After installing a package, run that setup before 00C. The reset reads schemas from the installed package and validates required column names and types across every current metadata table before any deletion; it does not perform migrations itself.

    A missing column or old native collection where JSON STRING is now required blocks the preview. A compatible addition already applied by metadata setup is picked up from the package registry without duplicating its schema in 00C. A new or retired table blocks reset until its ownership policy and coverage matrix are reviewed. Identity/relationship changes also require review; they must never be inferred by a demo reset. Keep schema migrations stopped until reset verification finishes. Map-valued extensions on a table with selected demo rows block cleanup because native Delta equality cannot safely match them.

### Execute the engineering regression

Keep `PIPELINE_MODE = "Ungoverned"` in all three demos. Run each notebook from its top through Finalize; 02B finalizes both independent paths. Do not run 00C between days.

| Day | Execute in order | Physical results |
| --- | --- | --- |
| 1 | 00C → [02A](02A-full-refresh-demo.md) → [02B](02B-build-and-run-incremental-append-etl.md) with `DEMO_DAY = 1` → [02C](02C-build-and-run-scd-etl.md) with `DEMO_DAY = 1` | 02A: 120 curated orders, 30 customers. 02B: 8 rows in each target. 02C: 8 SCD1 rows and 8 SCD2 versions. |
| 2 | 02B with `DEMO_DAY = 2` → 02C with `DEMO_DAY = 2` | 02B: 12 source rows and 12 in each target. 02C: 8 SCD1 rows and 9 SCD2 versions. |
| 3 | 02B with `DEMO_DAY = 3` → 02C with `DEMO_DAY = 3` | 02B: no new movements; both targets remain 12. 02C: 8 SCD1 rows and 10 SCD2 versions, with 8 current products. |

Day 3 is implemented: 02B deliberately stages no new file, while 02C stages `products_day3.csv`. Run the staging cells, not just the parameter cell. The individual demo pages include content checks as well as counts.

### Validate outputs and metadata

- [ ] Inspect persisted targets using the optional public read cells in 02A–02C. Write previews are prepared input, not proof of the persisted target content.
- [ ] Verify each demo's expected values, keys, row hashes and history using the checks on its page. Ensure business sources retain the expected content for that day; the orchestrators must not mutate them.
- [ ] Inspect `pipeline_result` after each Finalize. In the clean sequence without replays there are **10 new `METADATA_PIPELINE_RUN` rows**: one 02A, six 02B, three 02C. All should have `execution_mode = ungoverned`, `status = ungoverned_completed`, `boundary_completed = true`, and a completion time. Replays add new Runs; they must not duplicate business content.
- [ ] Filter metadata by exact execution workspace, Table IDs and the three Pipeline IDs printed by the notebooks. Run operations must reference the correct source/target IDs and physical destinations; 02B's incremental target is the Append All target. Check both 02B Runs on each day, not only the last `pipeline_result` displayed.
- [ ] Check Catalogue source/target identities and processing definitions, applicable profile snapshots/frequencies, and Lineage source/target roles with the exact `_notebook_id` and `_activity_id`. Lineage is pipeline participation, not exact DataFrame derivation, and its activity can be shared by interactive executions; do not expect one Lineage row per Run.
- [ ] Check committed Processing State publication receipts match the exact physical target markers. Checkpoint/baseline members must reference their receipt's `publication_id` and exact source/target/workspace. No accepted checkpoint may move past an unpublished batch. Day 3 no-op Writes need not create another publication receipt. Profiles are policy-driven; do not require an arbitrary fixed number of snapshots.
- [ ] Ungoverned must not create Contracts, activations or promotion Registry versions. Guardrail Results are conditional, not a required row count. A missing required Run, mismatched receipt, broken reference, duplicate key, wrong value or changed source is a failed acceptance even if all cells completed.

??? tip "Inspect the configured Metadata Lakehouse"

    Open its SQL endpoint or notebook and select the configured Engineering schema (default `engineering`). Replace placeholders with the exact IDs printed by setup and the demo notebooks. For example:

    ```sql
    SELECT run_id, pipeline_id, execution_mode, status, boundary_completed,
           started_at, completed_at, operations, profiling
    FROM engineering.METADATA_PIPELINE_RUN
    WHERE workspace_id = '<execution-workspace-id>'
      AND pipeline_id IN ('<02A-notebook-id>', '<02B-notebook-id>', '<02C-notebook-id>');

    SELECT record_type, status, run_id, pipeline_id, source_table_id,
           target_table_id, publication_id, publication_batch_id, max_change_value
    FROM engineering.METADATA_PROCESSING_STATE
    WHERE workspace_id = '<execution-workspace-id>'
      AND pipeline_id IN ('<02A-notebook-id>', '<02B-notebook-id>', '<02C-notebook-id>');
    ```

    `operations` and `profiling` are JSON STRING columns. Expand the actual JSON to inspect each operation, its `source_table_ids`, `incremental_target_table_id`, destination, metrics and status. Use the exact `profile_id`/`profile_snapshot_id` and `publication_id` links when checking children; table-name similarity is not ownership.

### Replay, failures and package changes

Repeat 02A before advancing days: overwrite must preserve 120/30 business results. Repeat 02B on the current day: the incremental path must return no already-accepted movements, and Append New Only must admit no seen hashes. Repeat 02C on the current day: it must keep eight current products and add no unchanged SCD2 version. Audit timestamps and Run identities can change.

After recording results, stop the demo again and run **all of 00C twice**. Both executions must finish with `RESET COMPLETE`; the second must remove zero metadata rows and tolerate absent targets. For a partial reset failure, fix the reported permission, configuration or ownership blocker and restart 00C from the top. Never manually delete just a checkpoint or parent metadata row. A missing metadata table is a blocker; provision/check it through 00B rather than silently skipping it.

An incomplete Run without a completion time blocks reset. Check Fabric Monitor and stop the execution first. Only then add its exact Run ID to `STOPPED_DEMO_RUN_IDS`. For a verified retired demo notebook copy, add its exact ID to `EXTRA_DEMO_NOTEBOOK_IDS`; unrelated/mixed-table Runs still block. If that ID is absent from the complete notebook listing, 00C checks the item itself. Only an explicit Fabric `ItemNotFound` response confirms deletion and skips its live-job query. Permission errors, service failures and ambiguous 404 responses block reset. Historical incomplete Runs still require explicit stopped-Run confirmation even when their notebook has been deleted. Retained governed history is not disposable: use a separate Ungoverned demo environment instead.

For each package change, publish the new wheel, start fresh sessions, rerun 00C and repeat this sequence. Record version, date, tester, reset summaries, Run IDs, output/value checks and any failures. **Local automated tests do not establish Fabric acceptance**: cross-workspace routing, Fabric job visibility, Lakehouse catalog removal and Warehouse SQL/connector behavior require this maintainer run in Fabric. Live Fabric is not added to PR CI.


**Next:** [Step 1. Establish Governance context](01-establish-governance-context.md)
