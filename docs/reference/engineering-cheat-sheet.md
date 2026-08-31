# FabricOps Engineering Guide

Use this page when you want the deeper engineering reasoning behind the FabricOps `02_pipeline` workflow.

The Guided Demo stays practical and the How FabricOps Works page stays high-level. This guide explains the engineering choices behind those pages, then keeps the practical PySpark, Spark optimisation, and T-SQL references collapsed at the bottom for quick lookup.

## Engineering concepts behind FabricOps

??? info "Lakehouse Files vs Tables"

    A Fabric Lakehouse has two useful storage experiences: **Files** and **Tables**. FabricOps supports both, but they serve different purposes.

    | | Files | Tables |
    | --- | --- | --- |
    | Best fit | Raw, file-oriented, semi-structured, unstructured, or externally supplied data | Managed structured datasets |
    | Typical access | File or folder path | Registered table name |
    | Common formats | CSV, JSON, Parquet, Excel, text, and other files | Delta tables |
    | Schema | Usually interpreted when read | Managed as part of the table |
    | Table transactions | Not provided by a plain file | Delta table capabilities |
    | FabricOps use | Raw/source landing and file ingestion | Governed reusable engineering sources and targets |

    **FabricOps recommendation:** keep naturally file-based inputs as Files when that preserves the source cleanly. Once data becomes a reusable governed dataset, prefer a managed Table rather than treating it as an anonymous file forever.

    This keeps the distinction between **source representation** and **governed analytical dataset** clear. A CSV arriving from a source system can remain a file; the cleaned, typed, reusable result can become a Delta table.

    **Microsoft Learn:** [What is a lakehouse in Microsoft Fabric?](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview)

??? info "Lakehouse first — and when Warehouse fits"

    FabricOps supports both Lakehouse and Warehouse, but its engineering path is intentionally **Lakehouse first** when substantial transformation is required.

    Microsoft’s own decision guide draws a similar boundary: Lakehouse is the stronger fit when Spark, large-scale data engineering, or mixed data types are central, while Warehouse is the stronger fit for T-SQL-first relational analytics, dimensional modelling, enterprise warehousing, and BI-oriented consumption.

    | | Lakehouse | Warehouse |
    | --- | --- | --- |
    | Primary engineering experience | Spark / notebooks | T-SQL |
    | Strong fit | Large-scale data engineering, mixed structures, repeated PySpark transformation | Structured relational analytics, dimensional models, SQL consumption, BI serving |
    | Processing style | Distributed Spark processing over Delta / OneLake | SQL engine over structured relational tables |
    | FabricOps source | Preferred working layer for heavy or repeated engineering | Supported source; often useful as an ingestion/query boundary |
    | FabricOps target | Preferred for intermediate engineered layers | Strong option for curated Product / Gold outputs |

    **Why Lakehouse first?** FabricOps is PySpark-first. Spark is designed to distribute work across partitions and process large datasets in parallel, and Lakehouse Delta tables are the native fit for that engineering path.

    A Warehouse can still be read from a notebook, including with `read_warehouse_query()`. That is useful when SQL can filter, project, join, or aggregate before Spark receives the data. But when the same large Warehouse dataset will be processed repeatedly in PySpark, repeatedly crossing from the Warehouse SQL engine into Spark adds an unnecessary processing boundary.

    For heavy or repeated engineering, FabricOps therefore recommends landing the required Warehouse data **1:1 into a Lakehouse Delta table first**, using either a full or incremental ingestion pattern, then carrying out the main transformation in PySpark.

    ```text
    Source Warehouse
          ↓
    focused full / incremental extract
          ↓
    Lakehouse Delta landing
          ↓
    parallel PySpark engineering
          ↓
    reusable engineered layers
          ↓
    curated Product / Gold
    ```

    This does not mean every Warehouse source must be copied. If the query is small, selective, or used once, direct Warehouse pushdown can be simpler and more efficient.

    ### Why Warehouse is often strong at Product / Gold

    The final curated layer has different priorities from the engineering layers. At Product / Gold, the data is normally structured, stable, and designed for consumption rather than heavy transformation.

    A Fabric Warehouse can be a strong serving layer when the product benefits from relational schemas, T-SQL access, SQL permissions, auditing, dimensional modelling, Power BI, Data Agents, or other SQL-oriented consumers.

    FabricOps therefore separates the two questions:

    ```text
    Where should heavy engineering happen?
    → usually Lakehouse + PySpark

    Where should curated relational data be served?
    → Lakehouse or Warehouse, with Warehouse preferred when relational serving and control are useful
    ```

    Warehouse is a recommendation for those serving characteristics, not a requirement. Power BI, Data Agents, and other Fabric consumers can also work with Lakehouse data where that is the better fit.

    **Microsoft Learn:** [Choose between Warehouse and Lakehouse](https://learn.microsoft.com/en-us/fabric/fundamentals/decision-guide-lakehouse-warehouse)

??? info "Medallion architecture"

    Medallion is a common way to organise data into progressively more refined layers.

    | Layer | Typical meaning | Example |
    | --- | --- | --- |
    | Bronze | Raw / landed data | Source extracts, raw files, minimally changed ingestion |
    | Silver | Cleaned, validated, standardised, reusable data | Typed, deduplicated, conformed engineering tables |
    | Gold | Curated data for consumption | Business-ready tables, aggregates, dimensional models |

    The useful idea is **progressive refinement**: preserve the source, create trusted reusable data, then publish data shaped for consumption.

    **FabricOps position:** medallion is compatible with FabricOps but is not mandatory. FabricOps standardises governance, metadata, processing, and publication boundaries; it does not require every project to create Bronze, Silver, and Gold layers just to conform to the terminology.

    Use separate persisted layers when they have a real purpose such as reuse, isolation, auditability, different grains, expensive transformations, or different consumer needs. Do not create extra copies only because the layer names exist.

    ```text
    Raw source / Files
            ↓
    reusable engineered table
            ↓
    governed Production table
            ↓
    consumer model / BI / AI
    ```

    That may resemble Bronze → Silver → Gold, but the actual number of persisted stages should follow the project architecture.

    **Microsoft Learn:** [Medallion architecture in Fabric](https://learn.microsoft.com/en-us/fabric/onelake/onelake-medallion-lakehouse-architecture)

??? info "Notebook first — vs Pipeline vs Dataflow Gen2"

    FabricOps deliberately makes the **Notebook** the visible engineering unit for governed transformation.

    | Fabric item | Strong fit | FabricOps position |
    | --- | --- | --- |
    | Notebook | Code-first engineering, PySpark, custom transformation, reusable engineering logic | Primary governed engineering implementation in `02_pipeline` |
    | Pipeline | Orchestration, schedules, dependencies, retries, data movement, calling notebooks | Use around FabricOps notebooks when orchestration is required |
    | Dataflow Gen2 | Low-code Power Query ingestion and transformation | Valid Fabric capability, but not the canonical FabricOps engineering path |

    **Why notebook first?** FabricOps wants project-specific engineering logic to stay explicit, reviewable, and versionable beside the metadata-driven workflow. PySpark also gives a consistent DataFrame transformation path across Lakehouse and Warehouse reads.

    Pipelines still matter. They are the natural place to schedule or orchestrate notebooks, chain dependencies, run activities, and monitor execution. FabricOps does not try to recreate those native platform capabilities inside its own metadata model.

    Dataflow Gen2 can still be useful for teams that prefer Power Query or low-code preparation. It simply is not the default implementation path taught by the starter kit.

    **Microsoft Learn:** [Data ingestion options for a Lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/load-data-lakehouse)

??? info "Config-driven engineering and why FabricOps has I/O functions"

    A Fabric notebook can work naturally with its attached/default Fabric item, but real engineering projects often need to read and write across **multiple Lakehouses, Warehouses, workspaces, and environments**.

    Native Spark access can do this, but the physical location has to be supplied somehow. Without a shared resolution layer, notebook code can end up carrying explicit OneLake ABFS paths, workspace IDs, item IDs, or connection details.

    ```text
    abfss://<workspace-id>@onelake.dfs.fabric.microsoft.com/<item-id>/Tables/...
    ```

    That works technically, but it creates an engineering maintenance problem when the same `02_pipeline` moves from Development to Production or when a Fabric item is replaced, renamed, or added.

    | Hard-coded in each pipeline | FabricOps approach |
    | --- | --- |
    | Physical workspace/item identity appears inside transformation notebooks | Physical identity is centralised in `00_env_config` |
    | Dev → Prod may require editing every promoted notebook | The promoted `02_pipeline` keeps the same logical target names |
    | Adding or replacing a Lakehouse/Warehouse can require changes across many notebooks | Update the environment configuration once |
    | A Production notebook can accidentally retain a Development path or ID | Environment-specific resolution happens through the active config |
    | Cross-item access logic is repeated beside business transformation | FabricOps I/O functions keep item resolution and access logic reusable |

    The intended separation is:

    ```text
    02_pipeline
        │
        │ asks for a logical store / target
        ▼
    00_env_config
        │
        │ defines the environment-specific Fabric items
        ▼
    FabricOps I/O functions
        │
        ▼
    Correct Lakehouse / Warehouse / workspace
    ```

    In other words, **`02_pipeline` describes what the pipeline needs; `00_env_config` describes where those resources exist in the current environment; the FabricOps I/O layer resolves the two.**

    This is why the I/O functions are not just wrappers around native PySpark reads and writes. They provide a consistent boundary for multi-item access, environment portability, logical target resolution, and shared behaviour around Fabric reads and writes.

    A project notebook can therefore use a logical target such as `source`, `unified`, `product`, or another project-defined key instead of embedding the physical Fabric identity everywhere.

    ```python
    source_df = read_lakehouse_table(
        "student_enrolment",
        target="source",
    )
    ```

    The same `02_pipeline` can then be promoted while the Development and Production versions of `00_env_config` resolve `source` to the correct environment-specific Fabric item.

    ### Why `00_env_config` is a notebook instead of YAML

    A YAML file would also be a valid generic configuration pattern. FabricOps intentionally keeps environment configuration in `00_env_config` because Fabric notebooks already work naturally with notebook-to-notebook `%run` execution.

    ```python
    %run 00_env_config
    ```

    This makes the configured context available directly to the notebook session without adding a separate file-loading and parsing mechanism. It also keeps the setup visible to Fabric users in the same notebook experience as the rest of the starter kit.

    The important architectural choice is not the file format. It is the **separation of environment-specific physical identity from reusable pipeline logic**.

??? info "PySpark first — and where T-SQL fits"

    Once source data is in Spark, FabricOps uses **PySpark DataFrames as the normal transformation path**.

    | Need | FabricOps preference |
    | --- | --- |
    | Heavy or repeated project transformation | Lakehouse + PySpark |
    | Filtering or projection on a Warehouse source before Spark | T-SQL via `read_warehouse_query()` |
    | Aggregation or join that can substantially reduce Warehouse data before transfer | T-SQL via `read_warehouse_query()` |
    | Joining DataFrames already in Spark | PySpark |
    | Cleansing, derivation, deduplication, windows, reshaping | PySpark |

    PySpark fits the main FabricOps engineering path because Spark distributes processing across partitions and is well suited to large-scale transformation. Keeping the working data in Lakehouse Delta avoids repeatedly crossing between a Warehouse SQL engine and Spark when the workload is primarily PySpark.

    ```text
    Lakehouse / Files
          ↓
        READ
          ↓
    PySpark DataFrame
          ↓
    parallel project transformation
          ↓
    governed target write
    ```

    For Warehouse sources, T-SQL can sit inside the read boundary:

    ```text
    Warehouse
        ↓
    T-SQL pushdown
        ↓
    read_warehouse_query(...)
        ↓
    PySpark DataFrame
        ↓
    PySpark transformation
    ```

    For a large Warehouse source that will be transformed repeatedly, prefer landing it into Lakehouse Delta first rather than making the Warehouse-to-Spark boundary part of every processing step.

    **Microsoft Learn:** [Microsoft Fabric Data Engineering](https://learn.microsoft.com/en-us/fabric/data-engineering/data-engineering-overview)

??? info "Full vs incremental: full, watermark, and partition"

    FabricOps makes the processing strategy explicit rather than hiding it inside ad-hoc notebook code.

    | Strategy | Use when | Main trade-off |
    | --- | --- | --- |
    | Full dataset | The source is small enough to reprocess safely, or there is no trustworthy incremental key | Simplest and easiest to reason about, but repeatedly processes everything |
    | Incremental watermark | A timestamp or monotonically increasing value identifies new or changed rows | Efficient, but depends on reliable change state and ordering |
    | Incremental partition | A date, snapshot, or other partition is the correct unit of change | Efficient and easy to reconcile by partition, but depends on meaningful source partitioning |

    ### Full dataset

    ```text
    Read all source rows
            ↓
       Transform
            ↓
    Write governed target
    ```

    Prefer full processing when simplicity is worth more than incremental complexity. It is often the safest choice for small reference tables, modest datasets, or sources without a reliable change indicator.

    ### Incremental watermark

    ```text
    Last successful watermark
             ↓
    Read rows newer than state
             ↓
          Transform
             ↓
    Write governed target
             ↓
    Commit new watermark
    ```

    A watermark normally uses a timestamp, sequence, or another increasing value that reliably identifies new or changed source records.

    **Critical FabricOps rule:** the watermark represents **successfully processed state**. Do not advance it before the governed target write succeeds. Otherwise a failed run can move the checkpoint forward and silently skip data on the next run.

    Consider late-arriving records when designing the watermark. Depending on the source, a small lookback or reprocessing window may be safer than assuming every record arrives strictly in order.

    ### Incremental partition

    ```text
    Identify changed/new partition
             ↓
    Read that logical partition
             ↓
          Transform
             ↓
    Write/reconcile that partition
             ↓
      Commit completion state
    ```

    Partition-based processing works well when the source naturally exposes a meaningful processing unit such as `snapshot_date`, business date, or another stable partition identifier.

    Do not confuse **logical incremental partitions** with Spark physical partition tuning. Incremental processing decides **which business/source data belongs in the run**. Spark repartitioning decides **how the DataFrame is physically distributed for compute/write**.

    **Microsoft Learn:** [Incrementally load data from Data Warehouse to Lakehouse](https://learn.microsoft.com/en-us/fabric/data-factory/tutorial-incremental-copy-data-warehouse-lakehouse)

## Practical cheat sheets

Use these when you already know what you want to do and only need a quick syntax or tuning reminder. The [Guided Demo](../guided-demo/02-run-pipeline.md) explains how the patterns fit into the FabricOps workflow.

??? example "PySpark transformation cheat sheet"

    The examples assume:

    ```python
    from pyspark.sql import functions as F
    from pyspark.sql.window import Window
    ```

    ### Inspect and select

    ```python
    display(df)
    df.show(20, truncate=False)
    df.printSchema()
    df.count()

    df = df.select("student_id", "programme", "status", "modified_datetime")
    df = df.withColumnRenamed("old_name", "new_name")
    df = df.drop("temporary_column")
    ```

    ### Filter, derive, and cast

    ```python
    df = df.filter(
        (F.col("status") == "ACTIVE")
        & (F.col("student_id").isNotNull())
    )

    df = df.withColumn("modified_date", F.to_date("modified_datetime"))
    df = df.withColumn("student_id", F.col("student_id").cast("string"))
    ```

    ### Conditional logic and nulls

    ```python
    df = df.withColumn(
        "status_group",
        F.when(F.col("status") == "ACTIVE", "Current")
         .when(F.col("status") == "COMPLETED", "Completed")
         .otherwise("Other"),
    )

    df = df.fillna({"amount": 0, "region": "UNKNOWN"})
    df = df.dropna(subset=["student_id"])
    df = df.withColumn("contact", F.coalesce("mobile", "email", F.lit("no_contact")))
    ```

    ### Deduplication

    ```python
    df = df.dropDuplicates(["student_id"])

    latest_window = (
        Window
        .partitionBy("student_id")
        .orderBy(F.col("modified_datetime").desc())
    )

    latest_df = (
        df
        .withColumn("rn", F.row_number().over(latest_window))
        .filter(F.col("rn") == 1)
        .drop("rn")
    )
    ```

    ### Joins

    ```python
    enriched_df = (
        enrolment_df.alias("e")
        .join(
            programme_df.alias("p"),
            F.col("e.programme_code") == F.col("p.programme_code"),
            "left",
        )
    )

    unmatched_df = source_df.join(reference_df, "student_id", "left_anti")
    exists_df = source_df.join(reference_df, "student_id", "left_semi")
    ```

    Broadcast a genuinely small lookup when appropriate:

    ```python
    enriched_df = source_df.join(
        F.broadcast(small_lookup_df),
        "programme_code",
        "left",
    )
    ```

    ### Group, aggregate, pivot, and sort

    ```python
    summary_df = (
        df
        .groupBy("programme", "status")
        .agg(
            F.count("*").alias("student_count"),
            F.countDistinct("student_id").alias("distinct_students"),
            F.sum("amount").alias("total_amount"),
            F.avg("amount").alias("avg_amount"),
        )
    )

    pivoted_df = (
        df
        .groupBy("programme")
        .pivot("status")
        .agg(F.count("*"))
    )

    df = df.orderBy(F.col("modified_datetime").desc())
    ```

    ### Window functions

    ```python
    w = Window.partitionBy("student_id").orderBy(F.col("modified_datetime").desc())

    df = df.withColumn("rank", F.rank().over(w))
    df = df.withColumn("dense_rank", F.dense_rank().over(w))
    df = df.withColumn("previous_amount", F.lag("amount", 1).over(w))
    df = df.withColumn("next_amount", F.lead("amount", 1).over(w))
    ```

    Running total:

    ```python
    running_window = (
        Window
        .partitionBy("student_id")
        .orderBy("modified_datetime")
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )

    df = df.withColumn("running_total", F.sum("amount").over(running_window))
    ```

    ### Common string, date, and nested-data patterns

    ```python
    df = df.withColumn("name_clean", F.trim("name"))
    df = df.withColumn("full_name", F.concat_ws(" ", "first_name", "last_name"))
    df = df.withColumn("modified_date", F.to_date("modified_datetime"))
    df = df.withColumn("month_start", F.date_trunc("month", "modified_datetime"))

    exploded_df = df.withColumn("tag", F.explode("tags"))

    flat_df = df.select(
        "event_id",
        F.col("customer.customer_id").alias("customer_id"),
        F.col("customer.email").alias("email"),
    )

    combined_df = df1.unionByName(df2, allowMissingColumns=True)
    ```

??? tip "Spark optimisation cheat sheet"

    FabricOps deliberately leaves project-specific Spark tuning visible because the correct choice depends on the real workload.

    ### High-value habits

    1. Select only the columns you need.
    2. Filter rows as early as practical.
    3. Prefer built-in Spark functions over Python UDFs.
    4. Avoid unnecessary `collect()` calls that move data to the driver.
    5. Expect wide joins, `groupBy`, `distinct`, and repartitioning to create shuffle.
    6. Broadcast only genuinely small lookup DataFrames.
    7. Cache only expensive DataFrames that are reused.
    8. Watch for skewed keys and very uneven partitions.
    9. Avoid creating excessive small output files.
    10. Inspect the execution plan before guessing at a fix.

    ### Built-ins before UDFs

    ```python
    clean_df = df.withColumn("name", F.upper(F.trim("name")))
    ```

    Prefer Spark built-ins when possible because Spark can optimise them as part of the query plan. Use a Python UDF only when the required logic cannot reasonably be expressed using built-in functions.

    ### Broadcast a small lookup

    ```python
    enriched_df = large_df.join(
        F.broadcast(small_lookup_df),
        "key",
        "left",
    )
    ```

    ### Repartition vs coalesce

    ```python
    df = df.repartition(200, "student_id")
    df = df.coalesce(10)
    ```

    | | `repartition()` | `coalesce()` |
    | --- | --- | --- |
    | Can increase partitions | Yes | Normally no |
    | Can decrease partitions | Yes | Yes |
    | Shuffle | Yes | Usually less movement |
    | Typical use | Change parallelism or redistribute by key | Reduce partitions/file count after the main work |

    Do not use either as a default performance fix.

    ### Cache only reused work

    ```python
    df.cache()
    # multiple actions that reuse df
    df.unpersist()
    ```

    ### Inspect the plan

    ```python
    df.explain(mode="formatted")
    ```

    Look for expensive exchanges or shuffles, large joins, repeated scans, and whether filters or projections are happening early enough.

    ### Physical partitioning is not incremental processing

    ```text
    Incremental processing
    = which logical source data should this run process?

    Spark partitioning
    = how should Spark distribute the DataFrame for compute/write?
    ```

??? example "T-SQL cheat sheet"

    T-SQL in FabricOps is primarily used for **Warehouse pushdown** through `read_warehouse_query()` when the Warehouse can reduce the data before Spark receives it.

    ### Select and filter

    ```sql
    SELECT
        student_id,
        programme_code,
        status,
        modified_datetime
    FROM dbo.student_enrolment
    WHERE status = 'ACTIVE';
    ```

    ### Join

    ```sql
    SELECT
        e.student_id,
        e.programme_code,
        p.programme_name
    FROM dbo.student_enrolment AS e
    LEFT JOIN dbo.programme AS p
        ON e.programme_code = p.programme_code;
    ```

    ### Aggregate, WHERE, and HAVING

    ```sql
    SELECT
        programme_code,
        COUNT(*) AS student_count
    FROM dbo.student_enrolment
    WHERE status = 'ACTIVE'
    GROUP BY programme_code
    HAVING COUNT(*) > 100
    ORDER BY student_count DESC;
    ```

    `WHERE` filters source rows **before** aggregation. `HAVING` filters groups **after** `GROUP BY` has calculated the aggregates.

    ### CTE + window

    ```sql
    WITH latest AS (
        SELECT
            student_id,
            programme_code,
            modified_datetime,
            ROW_NUMBER() OVER (
                PARTITION BY student_id
                ORDER BY modified_datetime DESC
            ) AS rn
        FROM dbo.student_enrolment
    )
    SELECT
        student_id,
        programme_code,
        modified_datetime
    FROM latest
    WHERE rn = 1;
    ```

    ### FabricOps Warehouse read pattern

    ```python
    source_df = read_warehouse_query(
        """
        SELECT
            programme_code,
            status,
            COUNT(*) AS student_count
        FROM dbo.student_enrolment
        WHERE modified_datetime >= '2026-01-01'
        GROUP BY programme_code, status
        HAVING COUNT(*) > 100
        """,
        target="product",
    )
    ```

    After the query returns, continue project-specific transformation using the returned PySpark DataFrame.

For exact FabricOps function contracts, use the [Function Reference](index.md). For the worked learning path, return to [Module 2: Engineer and run a data pipeline](../guided-demo/02-run-pipeline.md).