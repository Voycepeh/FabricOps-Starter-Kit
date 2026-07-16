# Run IO and Profiling Demo

Use `99_explore` to confirm that FabricOps can read, write, and profile data through the Fabric targets configured by `00_env_config`.

This smoke test runs before agreement registration. It proves that the shared environment, Fabric Environment, Lakehouse and Warehouse routes, and public IO helpers are working before the governed workflow begins writing project evidence.

## Why this step exists

Microsoft Fabric makes it easy to attach a data item and insert quick read code through the notebook interface. A reusable project workflow still needs consistent access when notebooks work across several configured Lakehouse and Warehouse targets or when users should work only through approved routes.

FabricOps standardizes that access pattern. IO helpers resolve the named target from `CONFIG` and `FABRIC_CONTEXT`, so notebook code uses the same function pattern without hardcoded workspace paths or assumptions about the attached default item.

## Functions demonstrated

| Helper | What it demonstrates |
| --- | --- |
| `read_lakehouse_csv`, `read_lakehouse_excel`, `read_lakehouse_parquet` | Read raw files from configured Lakehouse Files. |
| `write_lakehouse_table`, `read_lakehouse_table` | Write and read Delta tables through a configured Lakehouse target. |
| `write_warehouse_table`, `read_warehouse_table`, `read_warehouse_query` | Write and read through a configured Warehouse target. |
| `profile_dataframe` | Produce one structural and statistical profile row per eligible input column. |

## 1. Download the demo files

| File | Used for |
| --- | --- |
| [`orders.csv`](../assets/demo-data/io-profile/orders.csv) | CSV file-read smoke test with simple order facts. |
| [`products.xlsx`](../assets/demo-data/io-profile/products.xlsx) | Excel file-read smoke test with product reference data. |
| [`customers.parquet`](../assets/demo-data/io-profile/customers.parquet) | Parquet file-read smoke test with customer attributes. |

## 2. Upload the files to the source Lakehouse

Upload all three files to the root of the **Files** section in the source Lakehouse configured by `00_env_config`.

![Upload demo files to the Fabric Lakehouse](../assets/fabric-example-99_upload_files.png)

![Confirm the uploaded demo files](../assets/fabric-example-99_upload_files(2).png)

## 3. Open `99_explore`

Open the copied `99_explore` notebook and attach the same Fabric Environment used by `00_env_config`.

Confirm that the notebook imports `fabricops_kit` and receives the active `CONFIG` and `FABRIC_CONTEXT` values before running the IO cells.

![Start the 99_explore smoke test](../assets/fabric-example-99_start.png)

## 4. Run the smoke test

Run the notebook sections in order:

1. Read the CSV, Excel, and Parquet files from the configured source Lakehouse.
2. Write and read back the demonstration Lakehouse table.
3. Write and read back the demonstration Warehouse table when a Warehouse target is configured.
4. Run `profile_dataframe` on the returned Spark DataFrames.
5. Review the final PASS summary.

Keep the default row-count and repartition settings for the first run. Increase them only after the basic smoke test passes within your Fabric capacity.

## Why Spark is used

The same helper pattern can support small files and larger datasets. The demonstration starts with compact public-safe files, then uses Spark and repartitioning examples to show how the pattern can scale to parallel processing workloads.

## Expected result

You should see:

1. CSV, Excel, and Parquet DataFrames displayed.
2. A Lakehouse table created and read back.
3. A Warehouse table created and read back when that target is configured.
4. Profile rows generated from the returned Spark DataFrames.
5. A final PASS summary confirming the configured routes and helpers worked.

This smoke test does not write required governed workflow state. Its purpose is to validate configuration and helper behavior before agreement registration.

Next, continue to [Register Agreement](create-agreement.md).

See also: [Function Reference](../reference/index.md) for the IO and profiling callable details.
