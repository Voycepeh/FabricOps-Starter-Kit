# Step 2: Run the Common Pipeline Patterns

**Use `02_pipeline` in Engineering Development to demonstrate FabricOps file, Lakehouse, Warehouse, profiling, and metadata-registration patterns.**

```text
Files → Lakehouse and Warehouse
Lakehouse → transformation → Warehouse
Warehouse → SQL query → Lakehouse
```

## Before you begin

Complete [Step 0B: Set up the operating environment](00B-run-environment-setup.md).

Confirm that `00_env_config` defines these stores:

| Layer | Item type | Purpose |
| --- | --- | --- |
| `source` | Lakehouse | Stores the source files and receives the final Demo 3 output. |
| `unified` | Lakehouse | Receives the Lakehouse table created in Demo 1. |
| `product` | Warehouse | Receives the Warehouse tables created in Demo 1 and Demo 2. |

For simplicity, the demo uses the `demo` schema for managed Lakehouse and Warehouse tables.

## 1. Upload the demo files

Upload the demo files to the Source Lakehouse under:

```text
Files/DemoData/
├── excel_file_demo.xlsx
├── lakehouse_data_demo.csv
├── parquet_file.parquet
└── warehouse_data_demo.csv
```

The files are available from [`templates/DemoData/`](../../templates/DemoData/).

![Upload demo files](../assets/02/Upload_Files.png)

## 2. Open and configure `02_pipeline`

Open `02_pipeline` in Engineering Development.

Attach the same Fabric Environment used by `00_env_config`, restart the notebook session if required, then run the setup and FabricOps import cells.

![Config](../assets/02/Config.png)

## 3. Read the Excel file

Use `read_lakehouse_excel()` for an Excel workbook stored in the Source Lakehouse `Files` area.

![Read Excel](../assets/02/Read_Excel.png)

![Profile Excel](../assets/02/Read_Excel_Profile.png)

The helper reads the worksheet into a Spark DataFrame that can then be profiled or transformed.

## 4. Read the Parquet file

Use `read_lakehouse_parquet()` for the Parquet file stored in the Source Lakehouse `Files` area.

![Read Parquet](../assets/02/Read_Parquet.png)

## 5. Read CSV, transform, and write to a Lakehouse

Use `read_lakehouse_csv()` to read the CSV intended for the Lakehouse demo.

![Read CSV for Lakehouse](../assets/02/Read_CSV_LH_DEMO.png)

### Apply transformation logic

Use the **User defined transformation** section in `02_pipeline` for visible project-specific transformations.

![Transform DataFrame](../assets/02/Transform_DF.png)

### Write and profile the target

Run the Lakehouse target write section to write into the Unified Lakehouse and register the target evidence.

![Write Lakehouse](../assets/02/Write_LH.png)

!!! tip "Partitioning"

    `partition_by` and `repartition_by` can help with large workloads, but they should be used only when they fit the data shape. A poor partition key can create many small files and make reads and writes slower.

You can then inspect the written table and compact profile summary.

![Read written Lakehouse table](../assets/02/Read_Written_LH.png)

!!! note "Frequency profiling"

    Frequency rows for eligible columns are created and persisted by the profiling workflow. Displaying `target_profile_df` shows the compact profile summary, not the full frequency table.

## 6. Read CSV and write to a Warehouse

Use `read_lakehouse_csv()` to read the CSV intended for the Warehouse demo.

![Read CSV for Warehouse](../assets/02/Read_CSV_WH_DEMO.png)

Create the target Warehouse schema first:

```sql
CREATE SCHEMA demo
```

![Create Warehouse schema](../assets/02/create_schema.png)

Then run the Warehouse target write section. For the demo, the source DataFrame can be written directly without an additional transformation.

![Write Warehouse](../assets/02/Write_WH.png)

## 7. Read from Warehouse and write back to Lakehouse

Use `read_warehouse_query()` or `read_warehouse_table()` to read the Warehouse table created earlier.

![Read Warehouse](../assets/02/Read_WH.png)

For Spark-heavy processing, Lakehouse data is often more natural because the data is already available to Spark without an additional Warehouse query path.

??? info "Why the demo also shows parallel processing"

    This step also demonstrates repartitioning before a Lakehouse write. Parallel processing can help on larger datasets, but it adds overhead on small datasets. Test the pattern against the real workload instead of assuming more partitions are always faster.

![Write Lakehouse in parallel](../assets/02/Write_LH_Parallel.png)

## Functions demonstrated

| Function | Available since | Demonstrated purpose |
| --- | --- | --- |
| `read_lakehouse_csv()` | FabricOps v0.1.0 | Read CSV files from a configured Lakehouse `Files` area. |
| `read_lakehouse_excel()` | FabricOps v0.1.0 | Read an Excel worksheet from a configured Lakehouse `Files` area. |
| `read_lakehouse_parquet()` | FabricOps v0.1.0 | Read Parquet files from a configured Lakehouse `Files` area. |
| `read_lakehouse_table()` | FabricOps v0.1.0 | Read a managed Lakehouse table. |
| `write_lakehouse_table()` | FabricOps v0.1.0 | Write a Spark DataFrame as a managed Lakehouse table. |
| `read_warehouse_table()` | FabricOps v0.1.0 | Read a complete named Warehouse table. |
| `read_warehouse_query()` | FabricOps v0.1.0 | Execute caller-provided SQL against a Warehouse. |
| `write_warehouse_table()` | FabricOps v0.1.0 | Write a Spark DataFrame to a Warehouse table. |
| `profile_dataframe()` | FabricOps v0.2.0 | Generate column-level profiling statistics for a DataFrame. |
| `profile_frequency_distribution()` | FabricOps v0.2.0 | Generate value-frequency distributions for selected DataFrame columns. |
| `profile_and_register_table()` | FabricOps v0.2.0 | Profile a table and register the resulting profile metadata in the FabricOps metadata model. |

## Expected result

You should now have demonstrated the standard FabricOps IO and profiling patterns across files, Lakehouse, and Warehouse targets, with Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and Data Lineage evidence written by the pipeline workflow.

**Next:** [Step 3: Enrich the Data Catalogue and define Guardrails](03-enrich-guardrails.md)
