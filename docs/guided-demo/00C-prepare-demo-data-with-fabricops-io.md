# 0C. Prepare the demo data with FabricOps I/O

### Before you begin

Complete [Step 0B](00B-configure-environment-and-load-assets.md) with an empty, dedicated demo Metadata Lakehouse, import all three demo notebooks, and read [Reset, rerun and validate a package](#reset-rerun-and-validate-a-package) before executing 00C.

!!! warning "Dedicated demo environment only"

    Running 00C resets the five sources and six outputs in the reserved `demo` schemas. Metadata must already be empty and exclusively for this walkthrough; 00C never deletes existing metadata. Stop current and earlier demo executions, review the preview and confirm `RESET DEMO`. Wait for `RESET COMPLETE` before beginning Step 1.

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
| `demo/inventory_day1.csv` | `demo.inventory_movements` | 02B incremental/full append comparison |
| `demo/products_day1.csv` | `demo.product_master_updates` | 02C SCD1/SCD2 |

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

Start the seven-step lifecycle with isolated, empty metadata and known Day 1 business data.

</div>
</div>

!!! warning "Business reset and dedicated metadata"

    00C overwrites the five named sources and removes the six named outputs in the existing `demo` schemas. Reserve those eleven tables for this walkthrough. Other schemas, tables and source files are untouched. Never use production Metadata for this demo. 00C does not delete metadata: any existing Contract, activation, Run or other metadata row blocks preparation.

### Create the isolation boundary

1. Create a schema-enabled Lakehouse such as `demo_metadata` in the demo Governance workspace. It is exclusively for this seven-step walkthrough. All participating demo workspaces use that **same** lakehouse through the existing logical `Metadata` store.
2. Set `GOVERNANCE_METADATA_LAKEHOUSE_ID` and `GOVERNANCE_METADATA_LAKEHOUSE_NAME` in the demo `00_env_config` to that item's exact ID and physical name. Keep the existing Governance/Engineering metadata schemas. Update every demo config copy, including demo Production and Consumer when used. Use demo-specific workspaces/configuration, or the existing shared `config_workspace_id` option, so unrelated projects keep their original configuration.
3. Run metadata setup in [00B](00B-configure-environment-and-load-assets.md): set `INITIALIZE_METADATA = True`, run the config directly once, then restore `False`. Setup creates or upgrades tables; **it does not clear existing rows**. Do not run Step 1 yet: 00C must see empty metadata tables.
4. Upload the fixtures into Bronze **`Files/demo`**, with lowercase `demo`. The repository folder remains `templates/DemoData`; that download location is different from the case-sensitive Fabric Files folder.

Business stores can already contain the `demo` schemas and may contain unrelated schemas. 00C uses the configured Bronze/Silver/Gold stores and touches only the eleven listed demo tables. Metadata isolation does not authorize other pipelines to share those eleven tables or permit resetting production-governed assets.

### Preview and confirm 00C

1. Install/publish the wheel being validated and start fresh notebook sessions. Confirm the installed version in `setup_notebook()` output. The regression target is v0.4.2 Ungoverned; the notebook uses the package actually installed.
2. Import `02A_full_refresh_demo`, `02B_incremental_append_demo` and `02C_scd_demo` with those names. Stop schedules and interactive executions, including earlier demo/promoted copies that share the demo tables. Add their exact IDs to `EXTRA_DEMO_NOTEBOOK_IDS` for additional job checks. Do not reuse an old promoted copy after changing Metadata.
3. Confirm that the existing `Metadata` store in the demo `00_env_config` points at your manually created `demo_metadata` lakehouse. Set `DEMO_EXECUTIONS_STOPPED = True` only after stopping demo work. Run from the top through **reset-preview**.
4. Review the configured workspace/item identities, five restores, six removals and counts for **every installed metadata table**. 00C checks the Metadata item selected by `00_env_config`; it must be separate from the business stores. Every metadata count must be zero.
5. Set `RESET_CONFIRMATION = "RESET DEMO"` in **reset-confirmation**, execute it and then **reset-apply**. The application consumes the confirmation and rechecks empty metadata before changing business data. Continue through every source-write cell and **reset-verify**. Accept preparation only when it prints **`RESET COMPLETE`**.

The restored sources are Bronze `demo.orders` (120), `demo.products` (8), `demo.inventory_movements` (8), `demo.product_master_updates` (8), and Gold `demo.order_history` (180). Verification compares their full row content with the Day 1 fixtures.

| Demo | Output absent after 00C |
| --- | --- |
| 02A | Silver `demo.curated_orders`; Gold `demo.customer_summary` |
| 02B | Silver `demo.inventory_movements_append_all`; `demo.inventory_movements_append_new_only` |
| 02C | Silver `demo.product_master_scd1`; `demo.product_master_scd2` |

??? info "All metadata tables are checked; none is deleted"

    Counts and schemas come from the installed package's canonical registry and configured Metadata store. Missing tables or incompatible column types require metadata setup before any business reset. New canonical tables are checked automatically. Existing rows in any table block preparation, regardless of their workspace or table ownership. There is no selective metadata deletion, truncation, Contract removal or activation bypass.

    | Current metadata table | Required state before and after 00C |
    | --- | --- |
    | `METADATA_DATA_STEWARD` | Empty; Step 1 creates the demo stewards afterward. |
    | `METADATA_DATA_AGREEMENT` | Empty; Step 1 creates the demo agreement afterward. |
    | `METADATA_DATA_CONTRACT` | Empty; old drafts and frozen versions stay in the previous lakehouse. |
    | `METADATA_DATA_CONTRACT_ACTIVATION` | Empty; old selections and Agreement associations stay in the previous lakehouse. |
    | `METADATA_PIPELINE_ACTIVATION` | Empty; old submissions and Governance decisions stay in the previous lakehouse. |
    | `METADATA_PIPELINE_REGISTRY` | Empty; old promotion history stays in the previous lakehouse. |
    | `METADATA_PIPELINE_RUN` | Empty; previous execution history remains available in the previous lakehouse. |
    | `METADATA_PROCESSING_STATE` | Empty; no old observations, checkpoints, baselines or receipts can affect Day 1. |
    | `METADATA_DATA_CATALOGUE` | Empty; new pipeline observations register the current demo tables/columns. |
    | `METADATA_DATA_PROFILED` | Empty; the new package creates fresh profile metrics. |
    | `METADATA_DATA_PROFILED_FREQUENCY` | Empty; the new package creates applicable frequency distributions. |
    | `METADATA_DATA_LINEAGE` | Empty; previous demo pipeline participation cannot appear in new Contract authoring. |
    | `METADATA_GUARDRAIL_RESULTS` | Empty; subsequent evaluations create applicable results. |
    | `METADATA_DATA_ACCESS` | Empty; subsequent scans create applicable access snapshots. |

    Every summary reports `removed 0; remaining 0`. A populated lakehouse is preserved and rejected, including immutable Governance/deployment history. Pointing every demo notebook at the fresh lakehouse and starting fresh sessions prevents old Contracts, profiles, lineage and Run-based profiling schedules from leaking into the new walkthrough.

### Execute the engineering regression

After `RESET COMPLETE`, continue with [Step 1](01-establish-governance-context.md), then the existing Steps 2–7. Run the engineering scenarios below in Ungoverned mode before Contract authoring. Do not run 00C between days or after Step 1 has populated Metadata.

| Day | Execute in order | Physical results |
| --- | --- | --- |
| 1 | 02A → 02B with `DEMO_DAY = 1` → 02C with `DEMO_DAY = 1` | 02A: 120 curated orders and 30 customers. 02B: 8 rows in each target. 02C: 8 SCD1 rows and 8 SCD2 versions. |
| 2 | 02B with `DEMO_DAY = 2` → 02C with `DEMO_DAY = 2` | 02B: 12 source rows and 12 in each target. 02C: 8 SCD1 rows and 9 SCD2 versions. |
| 3 | 02B with `DEMO_DAY = 3` → 02C with `DEMO_DAY = 3` | 02B: no new movements; both targets remain 12. 02C: 8 SCD1 rows and 10 SCD2 versions, including 8 current products. |

Day 3 is implemented: 02B stages no new file, while 02C stages `demo/products_day3.csv`. Run each notebook from its top through Finalize, including its staging cells. 02B finalizes two separate executions. The existing governed admission restrictions in Steps 5–6 remain unchanged; metadata isolation does not bypass them.

### Validate outputs and metadata

- [ ] Inspect persisted targets with the public read cells. Write previews show prepared input, rather than proof of persisted content.
- [ ] Check the keys, values, hashes and history on the [02A](02A-full-refresh-demo.md), [02B](02B-build-and-run-incremental-append-etl.md) and [02C](02C-build-and-run-scd-etl.md) pages. Orchestrators must preserve the current day's source content.
- [ ] Expect 10 finalized `METADATA_PIPELINE_RUN` records before extra replays: one 02A, six 02B, three 02C. Check `execution_mode = ungoverned`, `status = ungoverned_completed`, `boundary_completed = true` and completion times. Both 02B paths share a Notebook/Pipeline ID but have distinct Run IDs.
- [ ] Check Run operation source/target IDs, physical destinations and 02B's incremental target. Check Catalogue processing definitions, applicable profiles/frequencies and Lineage roles. Profiling is policy-driven; there is no fixed required snapshot count.
- [ ] Check that committed Processing State receipts match physical publication markers and that checkpoint/baseline members reference the exact source, target, workspace and `publication_id`. Failed or skipped publication must not advance progress. No-op Writes need not create another receipt.
- [ ] Before Step 3, confirm the authoring notebook uses the same new Metadata item and reload it in a fresh session. Its Catalogue, profiles and lineage must come from this walkthrough. New Contracts and activations are created through the existing Governance steps.

??? tip "Inspect the configured demo Metadata Lakehouse"

    Use its SQL endpoint or a notebook with the configured Engineering schema (default `engineering`). Replace placeholders with exact IDs printed by the notebooks.

    ```sql
    SELECT run_id, pipeline_id, status, operations, profiling
    FROM engineering.METADATA_PIPELINE_RUN
    WHERE workspace_id = '<demo-execution-workspace-id>';

    SELECT record_type, status, run_id, source_table_id, target_table_id, publication_id
    FROM engineering.METADATA_PROCESSING_STATE
    WHERE workspace_id = '<demo-execution-workspace-id>';
    ```

    Expand the actual JSON STRING `operations` and `profiling` fields. Use exact `profile_id`/`profile_snapshot_id` and `publication_id` links when checking child records. Lineage is pipeline participation and may share activity identities across interactive Runs.

### Replay, failures and a complete restart

Repeat 02A before advancing days: overwrite must preserve 120/30 business results. Repeat 02B on the current day: no already-accepted movements or seen hashes should be added. Repeat 02C on the current day: keep eight current products without duplicate unchanged SCD2 versions. Finalize each execution and inspect its actual results.

00C is safe to run twice **before Step 1 or any pipeline has written metadata**. Both preparations must finish with `RESET COMPLETE`, preserve all source files and other business tables, and tolerate missing outputs. For a partial physical failure, fix its cause and restart 00C from the top; no metadata rollback or selective checkpoint deletion is needed.

For a complete seven-step restart or another package baseline:

1. Stop all current and earlier demo schedules, jobs and interactive executions sharing the eleven business tables. Retire old promoted copies from this walkthrough's schedules; 00C does not delete external notebooks, deployment snapshots, schedules or apps.
2. Create another fresh dedicated Metadata Lakehouse, such as `demo_metadata_02`. Keep the previous one if you need its immutable Contracts, activations, approvals or Run history; 00C never deletes it.
3. Update the exact Metadata item ID/name in every demo configuration copy, run 00B metadata setup once, and restart notebook sessions. Existing production/project configuration remains unchanged.
4. Run 00C against the newly selected Metadata item, prepare Day 1 and repeat Steps 1–7. Business stores and the reserved `demo` schemas can be reused.

Record package version, date, tester, metadata item ID, preparation summary, Run IDs and result checks. **Local tests do not establish Fabric acceptance.** Configured cross-workspace routing, Fabric job visibility, Lakehouse catalog removal, Warehouse connector behavior and the documented Governance gates still require the maintainer workflow in Fabric. Live Fabric execution is not added to PR CI.


**Next:** [Step 1. Establish Governance context](01-establish-governance-context.md)
