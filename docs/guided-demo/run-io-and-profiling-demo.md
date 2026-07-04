# Run IO and Profiling Demo

This step proves that FabricOps can read, write, and profile data across configured Lakehouse and Warehouse targets after environment setup.

## Why this exists

Fabric notebooks are easy to start with, but the native notebook attachment model encourages users to think in terms of the currently attached Lakehouse or Warehouse. That makes demos simple, but it can make team notebooks harder to reuse when data lives across multiple Fabric items.

FabricOps standardizes the access pattern so notebooks can use the configured target names from `00_env_config` instead of hardcoding paths, workspace IDs, item IDs, or manually switching attachments. The helpers use Spark as the runtime and resolve the configured Lakehouse or Warehouse target from the active `CONFIG`, `ENV`, and `FABRIC_CONTEXT` values.

The result is a plug-and-play pattern: define targets once in `00_env_config`, then call the same IO helpers from each notebook regardless of which Fabric item is attached to the notebook.

## Key idea

Run `00_env_config` once. Then IO helpers resolve the correct Lakehouse or Warehouse target from `CONFIG` and `FABRIC_CONTEXT`. Users call the same helper functions every time, regardless of which Fabric item is attached to the notebook.

## Conceptual mapping

| Helper | What it demonstrates |
| --- | --- |
| `read_lakehouse_csv`, `read_lakehouse_excel`, `read_lakehouse_parquet` | Read raw files from configured Lakehouse Files. |
| `write_lakehouse_table`, `read_lakehouse_table` | Write and read Delta tables through configured Lakehouse Tables. |
| `write_warehouse_table`, `read_warehouse_table`, `read_warehouse_query` | Write and read Warehouse tables through configured Warehouse targets. |
| `profile_dataframe` | Profile a Spark dataframe returned from either Lakehouse or Warehouse reads. |

## What you will do

1. Open `templates/notebooks/guided_demo_io_and_profiling.ipynb` in Microsoft Fabric.
2. Run `%run 00_env_config` first so `CONFIG`, `ENV`, and `FABRIC_CONTEXT` exist.
3. Load or generate CSV, Excel, and Parquet samples.
4. Write to Lakehouse.
5. Read from Lakehouse and profile it.
6. Write to Warehouse.
7. Read from Warehouse and profile it.
8. Run the larger Spark test to see parallel processing.

## Why Spark

Spark lets the same pattern work for small files and larger datasets. The demo starts with simple CSV, Excel, and Parquet files, then uses `spark.range` and repartitioning to show that the same IO pattern can scale to larger parallel processing workloads.

The notebook defaults are intentionally modest. Increase `ROW_COUNT` only after the basic run passes in your Fabric capacity.

## Expected evidence

You should see:

1. CSV, Excel, and Parquet dataframes displayed.
2. A Lakehouse table created and read back.
3. A Warehouse table created and read back.
4. Profile rows generated from the Lakehouse read dataframe.
5. Profile rows generated from the Warehouse read dataframe.
6. A final PASS summary table.

## Notes

This smoke test intentionally does not call metadata setup. It is designed to run after `00_env_config` and before agreement registration so teams can confirm configured IO targets and profiling behavior independently from metadata table creation.
