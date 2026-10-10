# Step 2B. Run the Incremental → Append Demo

**Process inventory movement batches through the normal FabricOps lifecycle and observe a no-change incremental run.**

## Before you begin

Download and import these assets:

- [`02B_incremental_append_demo.ipynb`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/DemoData/02B_incremental_append_demo.ipynb)
- [`inventory_day1.csv`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/DemoData/incremental_inventory/inventory_day1.csv)
- [`inventory_day2.csv`](https://raw.githubusercontent.com/Voycepeh/FabricOps-Starter-Kit/main/templates/DemoData/incremental_inventory/inventory_day2.csv)

Attach the same Fabric Environment used in Steps 00B and 2A. Keep `00_env_config` beside the imported notebook, and keep the CSV files under the Bronze Lakehouse paths `Files/Demo/incremental_inventory/inventory_day1.csv` and `inventory_day2.csv`.

The notebook uses the same governed identities for every run:

| Role | Store | Table | Processing |
| --- | --- | --- | --- |
| Source | `Bronze` | `demo.inventory_movements` | Incremental on `modified_datetime` |
| Target | `Silver` | `demo.inventory_movements_incremental` | Append |

## What to do

### 1. Run Day 1

Leave the day cell unchanged:

```python
DEMO_DAY = 1
```

Run every cell from top to bottom. The notebook:

1. runs `%run 00_env_config` and imports public FabricOps APIs;
2. reads `inventory_day1.csv` with `read_lakehouse_csv()`;
3. creates the Bronze source with eight unique movement rows;
4. runs the Data Contract selector;
5. calls `orchestrate_read()` in `incremental` mode with `read_parameters={"watermark_column": "modified_datetime"}`;
6. performs the PySpark movement transformation;
7. calls `orchestrate_write()` in `append` mode and passes the Read result through `sources` for lineage;
8. displays the Silver rows and calculated inventory balances.

The first governed Incremental Read bootstraps from the complete Bronze source. Expect **8 Silver rows**.

### 2. Run Day 2

Change only the day value:

```python
DEMO_DAY = 2
```

Rerun the complete notebook. It combines the four Day 2 movements with Bronze by `movement_id`, so accidentally rerunning Day 2 does not stage duplicate source rows. FabricOps reads only the unconsumed watermark scope and appends those four transformed records.

Expect **12 Silver rows**.

### 3. Run Day 3

Change only the day value:

```python
DEMO_DAY = 3
```

Rerun the complete notebook. Day 3 deliberately has no CSV because it represents no source change. The notebook still calls both orchestrators; it does not add a notebook-side `should_process` branch. FabricOps returns an empty incremental scope and the Append target stays at **12 rows**.

??? info "Why the target identity is required"

    Incremental progress belongs to the exact governed source-to-target relationship. `resolve_table_id()` supplies the Silver target identity to `orchestrate_read()`, so another target can consume the same Bronze source independently.

    See [`orchestrate_read()`](../api/reference/orchestrate_read.md) and [Read and Load Strategies](../reference/read-and-load-strategies.md).

## Expected result

| Run | New Bronze movements | Incremental scope | Silver rows |
| --- | ---: | --- | ---: |
| Day 1 | 8 | Bootstrap full scope | 8 |
| Day 2 | 4 | Rows after the committed watermark | 12 |
| Day 3 | 0 | Empty/no-change scope | 12 |

### Reset the demo

`METADATA_SOURCE_OBSERVATION` stores the source-state evidence and history used by Incremental execution, while successful watermark progress is stored on the governed target. Deleting only one business table is not a complete reset. For a clean restart, use a fresh Guided Demo environment, or remove both demo business tables and the scoped Source Observation history for `inventory_movements` → `inventory_movements_incremental` through an approved metadata-maintenance process. Then set `DEMO_DAY = 1` and rerun from the top.

**Next optional mode:** [Step 2C. Run the SCD1 and SCD2 Demo](02C-build-and-run-scd-etl.md)
