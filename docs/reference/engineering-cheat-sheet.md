# Fabric Engineering Cheat Sheet

Use this page as the quick engineering reference around the FabricOps `02_pipeline` workflow.

FabricOps intentionally makes a few opinionated engineering choices: keep notebook transformation code visible, use PySpark as the default transformation language once data is in Spark, use Warehouse SQL mainly for pushdown before Spark, and make full vs incremental processing an explicit governed choice.

The expandable sections below explain those choices. The rest of the page is a practical PySpark, Spark optimisation, and Warehouse SQL cheat sheet.

## FabricOps engineering choices

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

    This also keeps the distinction between **source representation** and **governed analytical dataset** clear. A CSV arriving from a source system can remain a file; the cleaned, typed, reusable result can become a Delta table.

    **Microsoft Learn:** [What is a lakehouse in Microsoft Fabric?](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview)

??? info "Lakehouse vs Warehouse"

    FabricOps supports both Lakehouse and Warehouse. It does not force every project into one storage engine.

    | | Lakehouse | Warehouse |
    | --- | --- | --- |
    | Primary engineering experience | Spark / notebooks | T-SQL |
    | Data shape | Structured, semi-structured, unstructured, and files | Structured relational data |
    | OneLake storage | Delta-based | Delta-based |
    | SQL access | SQL analytics endpoint for query scenarios | Full Warehouse T-SQL experience |
    | Strong fit | Data engineering, Spark transformation, file-heavy ingestion, flexible processing | SQL-first analytics, relational modelling, dimensional models, BI-oriented workloads |
    | FabricOps source | Supported | Supported |
    | FabricOps target | Supported | Supported |

    **FabricOps recommendation:** choose based on the workload, not because one is universally “better.”

    A Lakehouse is a strong default when the engineering path is already PySpark-heavy or the source estate includes files and mixed structures. A Warehouse is a strong fit when the target is relational, the team is SQL-first, or downstream consumption benefits from a Warehouse-native relational model.

    In FabricOps, a Warehouse source can still feed a PySpark transformation. `read_warehouse_query()` lets the Warehouse perform useful filtering, projection, joins, or aggregation first, and Spark receives the result as a DataFrame.

    **Microsoft Learn:** [What is a lakehouse in Microsoft Fabric? — Lakehouse vs. warehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview#lakehouse-vs-warehouse)

??? info "Medallion architecture"

    Medallion is a common way to organise data into progressively more refined layers.

    | Layer | Typical meaning | Example |
    | --- | --- | --- |
    | Bronze | Raw / landed data | Source extracts, raw files, minimally changed ingestion |
    | Silver | Cleaned, validated, standardised, reusable data | Typed, deduplicated, conformed engineering tables |
    | Gold | Curated data for consumption | Business-ready tables, aggregates, dimensional models |

    The useful idea is **progressive refinement**: preserve the source, create trusted reusable data, then publish data shaped for consumption.

    **FabricOps position:** medallion is compatible with FabricOps but is not mandatory. FabricOps standardises governance, metadata, processing and publication boundaries; it does not require every project to create Bronze, Silver and Gold layers just to conform to the terminology.

    Use separate persisted layers when they have a real purpose: reuse, isolation, auditability, different grains, expensive transformations, or different consumer needs. Do not create extra copies only because the layer names exist.

    A practical FabricOps mapping could be:

    ```text
    Raw source / Files
            ↓
    reusable engineered table
            ↓
    governed Production table
            ↓
    consumer model / BI / AI
    ```

    That may resemble Bronze → Silver → Gold, but the actual number of stages should follow the project architecture.

    **Microsoft Learn:** [Understand medallion architecture for Fabric with OneLake](https://learn.microsoft.com/en-us/fabric/onelake/onelake-medallion-lakehouse-architecture) · [Organize a Fabric lakehouse using medallion architecture design](https://learn.microsoft.com/en-us/training/modules/describe-medallion-architecture/)

??? info "Notebook first — vs Pipeline vs Dataflow Gen2"

    Fabric has several ways to move and transform data. FabricOps deliberately makes the **Notebook** the visible engineering unit for governed transformation.

    | Fabric item | Strong fit | FabricOps position |
    | --- | --- | --- |
    | Notebook | Code-first engineering, PySpark, custom transformation, reusable engineering logic | Primary governed engineering implementation in `02_pipeline` |
    | Pipeline | Orchestration, schedules, dependencies, retries, data movement, calling notebooks | Use around FabricOps notebooks when orchestration is required |
    | Dataflow Gen2 | Low-code Power Query ingestion and transformation | Valid Fabric capability, but not the canonical FabricOps engineering path |

    **Why notebook first?** FabricOps wants the project-specific engineering logic to stay explicit, reviewable and versionable beside the metadata-driven workflow. PySpark also gives a consistent DataFrame transformation path across Lakehouse and Warehouse reads.

    Pipelines still matter. They are the natural place to schedule or orchestrate notebooks, chain dependencies, run activities, and monitor execution. FabricOps does not try to recreate those native platform capabilities inside its own metadata model.

    Dataflow Gen2 can still be useful for teams that prefer Power Query or low-code preparation. It simply is not the default implementation path taught by the starter kit.

    **Microsoft Learn:** [Data ingestion options for a lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/load-data-lakehouse) · [Pipeline overview](https://learn.microsoft.com/en-us/fabric/data-factory/pipeline-overview) · [What is Dataflow Gen2?](https://learn.microsoft.com/en-us/fabric/data-factory/dataflows-gen2-overview)

??? info "PySpark first — and where SQL fits"

    Once source data is in Spark, FabricOps uses **PySpark DataFrames as the normal transformation path**.

    | Need | FabricOps preference |
    | --- | --- |
    | Project-specific transformation after read | PySpark |
    | Filtering or projection on a Warehouse source before Spark | Warehouse SQL via `read_warehouse_query()` |
    | Aggregation or join that can reduce Warehouse data before transfer | Warehouse SQL via `read_warehouse_query()` |
    | Joining DataFrames already in Spark | PySpark |
    | Cleansing, derivation, deduplication, windows, reshaping | PySpark |

    Spark SQL is supported by Fabric and is technically valid. FabricOps simply avoids teaching two equal transformation styles inside `02_pipeline`. That keeps the expected engineering path easier to read and easier to review.

    The normal mental model is:

    ```text
    Lakehouse / Warehouse / Files
              ↓
            READ
              ↓
       PySpark DataFrame
              ↓
    project transformation
              ↓
     governed target write
    ```

    For Warehouse sources, SQL can sit inside the read boundary:

    ```text
    Warehouse
        ↓
    SQL pushdown
        ↓
    read_warehouse_query(...)
        ↓
    PySpark DataFrame
        ↓
    PySpark transformation
    ```

    **Microsoft Learn:** [What is Microsoft Fabric Data Engineering?](https://learn.microsoft.com/en-us/fabric/data-engineering/data-engineering-overview)

??? info "Full vs incremental processing"

    FabricOps makes the processing strategy explicit rather than hiding it inside ad-hoc notebook code.

    | Strategy | Use when | Main trade-off |
    | --- | --- | --- |
    | Full dataset | The source is small/simple enough to reprocess, or there is no trustworthy incremental key | Simple and easy to reason about, but repeatedly processes everything |
    | Incremental watermark | A timestamp or monotonically increasing value identifies new or changed rows | Efficient, but depends on reliable ordering/change state |
    | Incremental partition | A date, snapshot, or partition is the correct unit of change | Efficient and easy to reconcile by partition, but depends on meaningful source partitioning |

    ### Full dataset

    ```text
    Read all source rows
            ↓
       Transform
            ↓
    Write governed target
    ```

    Prefer full processing when simplicity is worth more than incremental complexity. A full load is often the safest choice for small reference tables, modest datasets, or sources without a reliable change indicator.

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

    A watermark normally uses a timestamp, sequence, or other increasing value. The key requirement is that it reliably represents new or changed source records.

    **Critical FabricOps rule:** the watermark represents **successfully processed state**. Do not advance it before the governed target write succeeds. Otherwise a failed run can move the checkpoint forward and silently skip data on the next run.

    Consider late-arriving records when designing the watermark. Depending on the source, a small lookback/reprocessing window may be safer than assuming every record arrives strictly in order.

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

    **Microsoft Learn:** [Incrementally load data from Data Warehouse to Lakehouse](https://learn.microsoft.com/en-us/fabric/data-factory/tutorial-incremental-copy-data-warehouse-lakehouse) · [Incremental copy in Copy job](https://learn.microsoft.com/en-us/fabric/data-factory/incremental-copy-job)

## PySpark cheat sheet

The examples below assume:

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window
```

### Inspect a DataFrame

```python
display(df)
df.show(20, truncate=False)
df.printSchema()
df.count()
df.columns
df.dtypes
```

### Select, rename, drop, and limit

```python
df = df.select(
    "student_id",
    "programme",
    "status",
    "modified_datetime",
)

df = df.select(
    F.col("programme").alias("programme_code"),
    "status",
)

df = df.withColumnRenamed("old_name", "new_name")
df = df.drop("temporary_column")
df = df.limit(10)
```

### Filter rows

```python
df = df.filter(F.col("status") == "ACTIVE")

df = df.filter(
    (F.col("status") == "ACTIVE")
    & (F.col("student_id").isNotNull())
)
```

### Add, derive, and cast columns

```python
df = df.withColumn(
    "modified_date",
    F.to_date("modified_datetime"),
)

df = df.withColumn(
    "student_id",
    F.col("student_id").cast("string"),
)
```

### Conditional logic

```python
df = df.withColumn(
    "status_group",
    F.when(F.col("status") == "ACTIVE", "Current")
     .when(F.col("status") == "COMPLETED", "Completed")
     .otherwise("Other"),
)
```

### Null handling

```python
df = df.fillna({"amount": 0, "region": "UNKNOWN"})
df = df.dropna(subset=["student_id"])
df = df.filter(F.col("amount").isNotNull())

df = df.withColumn(
    "contact",
    F.coalesce("mobile", "email", F.lit("no_contact")),
)
```

### Distinct and deduplication

```python
df = df.distinct()
df = df.dropDuplicates(["student_id"])
```

When the surviving row matters, make the rule explicit:

```python
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
```

Useful join types:

```python
matched_df = source_df.join(reference_df, "student_id", "inner")
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

### Group and aggregate

```python
summary_df = (
    df
    .groupBy("programme", "status")
    .agg(
        F.count("*").alias("student_count"),
        F.countDistinct("student_id").alias("distinct_students"),
        F.sum("amount").alias("total_amount"),
        F.avg("amount").alias("avg_amount"),
        F.min("modified_datetime").alias("first_modified_datetime"),
        F.max("modified_datetime").alias("latest_modified_datetime"),
    )
)
```

### Pivot

```python
pivoted_df = (
    df
    .groupBy("programme")
    .pivot("status")
    .agg(F.count("*"))
)
```

### Sort

```python
df = df.orderBy(
    F.col("programme").asc(),
    F.col("modified_datetime").desc(),
)
```

### Window functions

Latest row per key:

```python
w = Window.partitionBy("student_id").orderBy(F.col("modified_datetime").desc())
latest_df = df.withColumn("rn", F.row_number().over(w)).filter(F.col("rn") == 1)
```

Rank within a group:

```python
df = df.withColumn("rank", F.rank().over(w))
df = df.withColumn("dense_rank", F.dense_rank().over(w))
```

Previous and next values:

```python
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

### Common string functions

```python
df = df.withColumn("name_upper", F.upper("name"))
df = df.withColumn("name_clean", F.trim("name"))
df = df.withColumn("full_name", F.concat_ws(" ", "first_name", "last_name"))
df = df.withColumn("clean_phone", F.regexp_replace("phone", "-", ""))
df = df.withColumn("prefix", F.substring("programme_code", 1, 3))
```

### Common date functions

```python
df = df.withColumn("today", F.current_date())
df = df.withColumn("loaded_at", F.current_timestamp())
df = df.withColumn("modified_date", F.to_date("modified_datetime"))
df = df.withColumn("month_start", F.date_trunc("month", "modified_datetime"))
df = df.withColumn("days_since", F.datediff(F.current_date(), "modified_date"))
df = df.withColumn("year", F.year("modified_date"))
```

### Nested and array data

```python
exploded_df = df.withColumn("tag", F.explode("tags"))

flat_df = df.select(
    "event_id",
    F.col("customer.customer_id").alias("customer_id"),
    F.col("customer.email").alias("email"),
)
```

Aggregate values into arrays:

```python
summary_df = (
    df
    .groupBy("student_id")
    .agg(
        F.collect_list("module_code").alias("modules"),
        F.collect_set("module_code").alias("distinct_modules"),
    )
)
```

### Combine compatible datasets

```python
combined_df = df1.unionByName(
    df2,
    allowMissingColumns=True,
)
```

## Spark optimisation cheat sheet

FabricOps deliberately leaves project-specific Spark tuning visible because the correct choice depends on the real workload.

### Start with the high-value habits

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

Prefer Spark built-in functions when possible because Spark can optimise them as part of the query plan.

```python
# Prefer
clean_df = df.withColumn("name", F.upper(F.trim("name")))
```

A normal Python UDF crosses the Spark/Python boundary row by row and can prevent some Spark optimisation. Use one when the logic cannot reasonably be expressed using built-in functions.

### Broadcast a small lookup

```python
enriched_df = large_df.join(
    F.broadcast(small_lookup_df),
    "key",
    "left",
)
```

Broadcasting can avoid a large shuffle when one side is small enough. Do not force it on a DataFrame that is not genuinely small.

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

Caching costs memory. It is useful when the same expensive result feeds multiple actions in the same Spark session; it is wasteful when the DataFrame is only used once.

### Inspect the plan

```python
df.explain(mode="formatted")
```

Look for expensive exchanges/shuffles, large joins, repeated scans, and whether filters/projections are happening early enough.

### Physical partitioning is not incremental processing

Keep these ideas separate:

```text
Incremental processing
= which logical source data should this run process?

Spark partitioning
= how should Spark distribute the DataFrame for compute/write?
```

A pipeline can use incremental watermark processing and still need no explicit `repartition()` at all.

## Warehouse SQL cheat sheet

SQL in FabricOps is primarily used for **Warehouse pushdown** through `read_warehouse_query()`.

Use it when the Warehouse can reduce the amount of data before Spark receives it.

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

**Microsoft Learn:** [Warehouse in Microsoft Fabric](https://learn.microsoft.com/en-us/fabric/data-warehouse/data-warehousing) · [T-SQL surface area in Fabric Data Warehouse](https://learn.microsoft.com/en-us/fabric/data-warehouse/tsql-surface-area)

## Quick FabricOps decision guide

| Need | Prefer |
| --- | --- |
| Raw or naturally file-oriented source | Lakehouse Files |
| Governed reusable Lakehouse dataset | Lakehouse Table |
| Spark-heavy / file-heavy engineering workload | Lakehouse |
| SQL-first relational / dimensional workload | Warehouse |
| Project transformation after read | PySpark |
| Reduce Warehouse data before Spark | `read_warehouse_query()` + SQL |
| Simple safe reprocessing | Full dataset |
| Timestamp/sequence identifies change | Incremental watermark |
| Snapshot/date is the natural processing unit | Incremental partition |
| Schedule/dependency/orchestration | Native Fabric Pipeline around the notebook |
| Low-code Power Query transformation | Dataflow Gen2 where appropriate, outside the canonical FabricOps notebook path |
| Extra Bronze/Silver/Gold stage | Only when that persisted layer has a real architectural purpose |

For exact FabricOps function contracts, use the [Function Reference](index.md). For the worked learning path, return to [Module 2: Engineer and run a data pipeline](../guided-demo/02-run-pipeline.md).

**Additional PySpark reference:** [Databricks / PySpark / SQL Server / Spark SQL Cheat Sheet — Srihari S.](https://lnkd.in/p/gAEsCbeR). FabricOps adapts only the engineering patterns relevant to Microsoft Fabric and does not treat Databricks-specific features as Fabric capabilities.
