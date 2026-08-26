# Step 2: Run the Development pipeline

**Use `02_pipeline` in Engineering Development to execute the canonical FabricOps pipeline shape while demonstrating the currently validated IO, transformation, profiling, and metadata-registration patterns.**

The notebook follows one lifecycle even when some newer governed components are still Preview:

```text
0. Environment → E. Extract → T. Transform → L. Load
```

!!! info "Key concepts for this step"

    [**Pipeline**](../glossary.md#pipeline) — a repeatable sequence that reads, transforms, checks, and writes data.  
    [**Profile**](../glossary.md#profile) — a point-in-time summary of the data and its structure.  
    [**Schema**](../glossary.md#schema) — the expected columns and data types of a table or DataFrame.  
    [**Data Quality**](../glossary.md#data-quality) — the governed expectations the data must meet for its intended use.

    These concepts are enough for the baseline run. Open the [Glossary](../glossary.md) only when another term becomes relevant.

The Live blocks below are the currently validated Step 2 path. Preview blocks show where the newer governed runtime fits without requiring those components for this baseline run.

## Before you begin

Complete [Step 0B: Set up the operating environment](00B-run-environment-setup.md).

Confirm that `00_env_config` defines these stores:

| Layer | Item type | Purpose |
| --- | --- | --- |
| `source` | Lakehouse | Stores the source files and receives the final demo output where required. |
| `unified` | Lakehouse | Receives the Lakehouse table created in the Lakehouse example. |
| `product` | Warehouse | Receives the Warehouse examples. |

For simplicity, the demo uses the `demo` schema for managed Lakehouse and Warehouse tables.

???+ success "Live — 0. Environment: open and configure `02_pipeline`"

    Upload the demo files to the Source Lakehouse under `Files/DemoData/` and open `02_pipeline` in Engineering Development.

    Attach the same Fabric Environment used by `00_env_config`, restart the notebook session if required, then run the setup and FabricOps import cells.

    ![Config](../assets/02/Config.png)

    FabricOps keeps environment-specific routing in `00_env_config` so the same notebook can resolve configured source, unified, product, and metadata stores without hardcoding Fabric item paths throughout the pipeline.

## E. Extract

???+ success "Live — Read Excel from the Source Lakehouse"

    Use `read_lakehouse_excel()` for an Excel workbook stored in the Source Lakehouse `Files` area.

    ![Read Excel](../assets/02/Read_Excel.png)

    ![Profile Excel](../assets/02/Read_Excel_Profile.png)

    The helper reads the worksheet into a Spark DataFrame that can then be profiled or transformed.

???+ success "Live — Read Parquet from the Source Lakehouse"

    Use `read_lakehouse_parquet()` for the Parquet file stored in the Source Lakehouse `Files` area.

    ![Read Parquet](../assets/02/Read_Parquet.png)

???+ success "Live — Read CSV for a Lakehouse target"

    Use `read_lakehouse_csv()` to read the CSV intended for the Lakehouse demo.

    ![Read CSV for Lakehouse](../assets/02/Read_CSV_LH_DEMO.png)

???+ success "Live — Read CSV for a Warehouse target"

    Use `read_lakehouse_csv()` to read the CSV intended for the Warehouse demo.

    ![Read CSV for Warehouse](../assets/02/Read_CSV_WH_DEMO.png)

???+ success "Live — Read a Warehouse table or SQL query"

    Use `read_warehouse_table()` for a complete named Warehouse table or `read_warehouse_query()` when the pipeline should execute caller-provided SQL.

    ![Read Warehouse](../assets/02/Read_WH.png)

    A filtered, joined, or aggregated query result should not be registered as the complete profile of one physical source table. For Spark-heavy processing, Lakehouse data is normally more direct because Delta data is already available to Spark while Warehouse reads use an additional SQL/TDS path.

??? info "Preview — Governed source preparation and incremental read"

    **Answer three separate questions: how to identify source data, what to read now, and how to apply the result.**

    ### Choose how the source should be read

    The engineer configures one explicit source strategy:

    | Source strategy | What it means | Typical example |
    | --- | --- | --- |
    | `full_dataset` | Read the complete source every run. | Small CSV or reference table. |
    | `incremental_watermark` | Read rows newer than the last successfully committed checkpoint. | Warehouse table with `modified_datetime`. |
    | `incremental_partition` | Read whole logical data buckets that are new or changed. | Lakehouse snapshots by `snapshot_date`. |

    `incremental_watermark` and `incremental_partition` are both incremental strategies. They differ in how FabricOps identifies affected source data: **which rows changed since the last successful checkpoint** versus **which whole data buckets changed**.

    ```python
    SOURCE_READ_STRATEGY = "full_dataset"

    SOURCE_READ_STRATEGY = "incremental_watermark"
    SOURCE_WATERMARK_COLUMN = "modified_datetime"

    SOURCE_READ_STRATEGY = "incremental_partition"
    SOURCE_PARTITION_COLUMN = "snapshot_date"
    ```

    ### Understand the runtime read mode

    FabricOps then resolves what this execution needs:

    | Runtime mode | Meaning |
    | --- | --- |
    | `skip` | Nothing needs processing this run. |
    | `full_dataset` | Read the complete physical source. |
    | `incremental_subset` | Read only the affected part of the source. |

    For example, a watermark with no newer value resolves to `skip`; the first partition observation resolves to `full_dataset`; and changed or new partitions resolve to `incremental_subset`. The source strategy is not the runtime read mode. Target strategies (`overwrite`, `append`, `scd1`, and `scd2`) answer the separate third question: how should the processed DataFrame be applied?

    ### Watermark example: changed rows

    Consider Fabric Warehouse `dbo.Bookings`, configured with `incremental_watermark` on `modified_datetime`. If the previous successful watermark is `2026-08-26 10:00` and FabricOps captures `2026-08-26 12:00` as the current upper watermark, the bounded subset is:

    ```text
    modified_datetime > 2026-08-26 10:00
    AND modified_datetime <= 2026-08-26 12:00
    ```

    The interval is `(lower_bound, upper_bound]`. Rows arriving after 12:00 belong to the next execution. On a first run, FabricOps reads the full dataset and retains the captured upper value only as a candidate. After the target write succeeds, call `commit_pipeline_checkpoint(read_prep)` to advance the successful watermark. If transformation, Guardrails, or target persistence fails, do not call it: the successful watermark remains unchanged and a retry starts from the last successful checkpoint. Source observation describes what a source looked like, while the successful watermark records how far a completed pipeline processed.

    !!! warning "Watermarks must be unique as well as increasing"

        A watermark value must be non-null and globally unique for every source row. FabricOps validates this before preparing the range. A timestamp shared by two rows is unsafe: another row could arrive later with the already committed timestamp and fall outside the next `(lower, upper]` interval. Use a source-provided increasing sequence or another column that is both strictly increasing and unique; otherwise choose `incremental_partition`. Target writes used with checkpoint retries must also be idempotent because business and metadata targets cannot share one cross-item transaction.

    ### Partition example: affected buckets

    Consider Lakehouse `student_snapshot`, configured with `incremental_partition` on `snapshot_date`:

    ```text
    25 Aug → unchanged
    26 Aug → changed
    27 Aug → new
    ```

    FabricOps prepares the complete 26 Aug and 27 Aug buckets. This model suits daily or monthly snapshots, historical corrections, late-arriving records, and independent processing by date or month because an older affected bucket can be reopened.

    | | `incremental_watermark` | `incremental_partition` |
    | --- | --- | --- |
    | Unit | Rows in a watermark range | Whole affected data buckets |
    | Typical column | `modified_datetime` | `snapshot_date` |
    | Retry | Start at the last successful checkpoint | Reprocess affected partitions |
    | Late arrivals | Requires a reliable modified value | Strong fit when old buckets can reopen |
    | Historical correction | Must update the watermark value | Reprocess the old partition |
    | Parallel date processing | Possible | Natural |

    Prefer a watermark for a transactional Warehouse, SQL, or API source with a non-null, strictly increasing, globally unique value and row-level changes. A modified timestamp is suitable only when the source guarantees those properties. Prefer partitions when deliveries naturally arrive as days, months, or snapshots and whole periods are expected to be reprocessed. Neither is universally better.

    A late row with `business_date = 25 Aug` and `modified_datetime = 27 Aug` is found by a watermark on `modified_datetime`. A strict watermark can miss it if the source assigns an old value behind the successful checkpoint. Partition processing can reopen 25 Aug when FabricOps actually detects that bucket as affected; it does not imply that every old bucket is always reread.

    !!! important "Keep source profiles complete"

        A complete `full_dataset` DataFrame may refresh the canonical registered source profile. An `incremental_subset` may be profiled diagnostically, but it must not replace the complete physical source profile.

## T. Transform

???+ success "Live — Apply user-defined transformation"

    Use the **User defined transformation** section in `02_pipeline` for visible project-specific transformations.

    ![Transform DataFrame](../assets/02/Transform_DF.png)

    FabricOps governs the boundaries around ETL rather than replacing business transformation logic. Joins, filters, derivations, aggregations, enrichment, and reshaping remain visible and project-owned in the notebook.

## L. Load

???+ success "Live — Write, read back, and profile a Lakehouse target"

    Run the Lakehouse target write section to write into the Unified Lakehouse.

    ![Write Lakehouse](../assets/02/Write_LH.png)

    Read the persisted target back and profile/register the complete physical target.

    ![Read written Lakehouse table](../assets/02/Read_Written_LH.png)

    `profile_and_register_table()` records Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and basic table-level Data Lineage records alongside the pipeline activity.

    !!! tip "Partitioning"

        `partition_by` and `repartition_by` can help with large workloads, but they should be used only when they fit the data shape. A poor partition key can create many small files and make reads and writes slower.

        `partition_by` controls physical Lakehouse storage layout. `incremental_partition` controls which logical source data buckets FabricOps processes. A table can be physically partitioned by `event_date` while using `incremental_watermark` on `modified_datetime`.

    !!! note "Frequency profiling"

        Frequency rows for eligible columns are created and persisted by the profiling workflow. Displaying `target_profile_df` shows the compact profile summary, not the full frequency table.

???+ success "Live — Write, read back, and profile a Warehouse target"

    Create the target Warehouse schema first when required:

    ```sql
    CREATE SCHEMA demo
    ```

    ![Create Warehouse schema](../assets/02/create_schema.png)

    Then run the Warehouse target write section. For the baseline demo, the source DataFrame can be written directly without an additional transformation.

    ![Write Warehouse](../assets/02/Write_WH.png)

???+ success "Live — Read from Warehouse and write back to Lakehouse"

    Use `read_warehouse_query()` or `read_warehouse_table()` to read the Warehouse table and continue the result through Spark processing into a Lakehouse target.

    This example also demonstrates optional repartitioning before a Lakehouse write. Parallel processing can help on larger datasets but adds overhead on small datasets, so test it against the real workload.

    ![Write Lakehouse in parallel](../assets/02/Write_LH_Parallel.png)

??? info "Preview — Target Guardrails and governed load preparation"

    In the newer governed lifecycle, target Schema and DQ checks run on the transformed target DataFrame before persistence. `write_pipeline_prep()` then reuses the same processing definition resolved by `read_pipeline_prep()`, adds the governed audit/lifecycle fields, and prepares the explicit physical writer settings.

    The target is still written with the normal FabricOps Lakehouse or Warehouse writer. After persistence, the complete target is read back and profiled/registered. This keeps the physical IO visible while Governance controls the processing boundary.

## Functions demonstrated in the Live Step 2 path

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
| `profile_and_register_table()` | FabricOps v0.2.0 | Profile a complete physical table and register its metadata. |

## Expected result

You should now have executed the validated baseline through the same canonical `Environment → Extract → Transform → Load` structure used by the newer governed lifecycle, with Data Catalogue, Data Profiled, Data Profiled Frequency where applicable, and Data Lineage records written by the pipeline workflow.

The collapsed Preview blocks show the exact places where incremental preparation, Guardrails, contract selection, and governed load preparation extend this flow in later steps.

**Previous:** [Step 1: Create Data Stewards and Data Agreements](01-create-agreement.md)  
**Next:** [Step 3: Enrich the Data Catalogue and define Guardrails](03-enrich-guardrails.md)
