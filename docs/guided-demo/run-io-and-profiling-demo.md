# Run IO and Profiling Demo

This step proves that FabricOps can read, write, and profile data across configured Lakehouse and Warehouse targets after environment setup.

## Why this exists

Fabric notebooks make it easy to attach a Lakehouse or Warehouse and quickly read files or tables through the native UI. That is great for exploration and simple demos.

The problem starts when a pipeline needs to work across more than one Lakehouse or Warehouse, or when users do not have broad item-level access but are expected to work through approved table, schema, or configured target access.

FabricOps standardizes that access pattern. Instead of relying on whichever item is attached to the notebook, the IO helpers resolve the configured Lakehouse or Warehouse target from `00_env_config`. Users call the same functions every time, and the notebook can read or write through the approved target without hardcoding paths, switching attachments, or rethinking the access pattern.

## Key idea

Run `00_env_config` once. Then IO helpers resolve the correct Lakehouse or Warehouse target from `CONFIG` and `FABRIC_CONTEXT`. Users call the same helper functions every time, using the configured targets prepared in `00_env_config`.

## Conceptual mapping

| Helper | What it demonstrates |
| --- | --- |
| `read_lakehouse_csv`, `read_lakehouse_excel`, `read_lakehouse_parquet` | Read raw files from configured Lakehouse Files. |
| `write_lakehouse_table`, `read_lakehouse_table` | Write and read Delta tables through configured Lakehouse Tables. |
| `write_warehouse_table`, `read_warehouse_table`, `read_warehouse_query` | Write and read Warehouse tables through configured Warehouse targets. |
| `profile_dataframe` | Profile a Spark dataframe returned from either Lakehouse or Warehouse reads. |

## Starter dataset

Prepare the starter files and upload them into this configured Lakehouse Files folder before running the notebook:

```text
Files/fabricops_demo/io_profile/
```

The starter dataset includes:

| File | Used for |
| --- | --- |
| [`orders.csv`](../assets/demo-data/io-profile/orders.csv) | CSV file-read smoke test with simple order facts. |
| [`products.xlsx`](../assets/demo-data/io-profile/products.xlsx) | Excel file-read smoke test with product reference data. |
| [`customers.parquet`](../assets/demo-data/io-profile/customers.parquet) | Parquet file-read smoke test with customer attributes. |

The repo includes the small `orders.csv`, `products.xlsx`, and `customers.parquet` starter samples. Upload these files to the configured Lakehouse Files path, or set `USE_UPLOADED_STARTER_FILES = False` so the notebook regenerates the same tiny samples in the configured Lakehouse Files path.

## What you will do

1. Open [`guided_demo_io_and_profiling.ipynb`](../assets/demo-data/io-profile/guided_demo_io_and_profiling.ipynb) in Microsoft Fabric.
2. Run `%run 00_env_config` first so `CONFIG`, `ENV`, and `FABRIC_CONTEXT` exist.
3. Download the bundled starter CSV, Excel, and Parquet files.
4. Upload them to `Files/fabricops_demo/io_profile/` in the configured Lakehouse Files area. All three starter files are bundled with the guided demo asset.
5. Run the notebook to read those files through the FabricOps IO helpers.
6. Write to Lakehouse, read from Lakehouse, and profile the Lakehouse read dataframe.
7. Write to Warehouse, read from Warehouse, and profile the Warehouse read dataframe.
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
