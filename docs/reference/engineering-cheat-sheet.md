# Fabric Engineering Cheat Sheet

Use this page when you know the transformation you need and want a quick reminder of the syntax. The Guided Demo explains these patterns in context; the `02_pipeline` template stays intentionally lightweight and only provides the place for project-specific transformation code.

FabricOps standardises the governed workflow around engineering. Your project still owns the transformation logic.

## Key concepts and when to use what

Use these expandable comparisons when you need the decision first and the syntax second. The **Fabric concepts** below align to Microsoft Fabric terminology and link to the relevant Microsoft Learn article. The **FabricOps recommendations** describe how this starter kit chooses to use those capabilities.

??? info "Lakehouse Files vs Tables"

    | | Files | Tables |
    | --- | --- | --- |
    | Best fit | Raw, file-oriented, unstructured, or non-Delta data | Managed structured data |
    | Typical access | File or folder path | Registered table name |
    | Common formats | CSV, JSON, Parquet, Excel, and other files | Delta tables |
    | Fabric behaviour | Flexible file area | Managed table area with Delta capabilities |
    | FabricOps use | Raw/file source and staging paths | Governed reusable Lakehouse tables |

    **Rule of thumb:** use Files when the source is naturally file-oriented; use Tables when the data should behave like a managed, queryable dataset.

    **Microsoft Learn:** [What is a lakehouse in Microsoft Fabric?](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview)

??? info "Lakehouse vs Warehouse"

    | | Lakehouse | Warehouse |
    | --- | --- | --- |
    | Primary development experience | Apache Spark: Python, Scala, Spark SQL, R | T-SQL |
    | Data | Structured and unstructured | Structured relational data |
    | Storage | Delta on OneLake | Delta on OneLake |
    | SQL access | SQL analytics endpoint for read/query scenarios | Full Warehouse T-SQL experience |
    | Best fit | Data engineering, data science, flexible transformation | BI, dimensional modelling, SQL-first analytics |
    | FabricOps position | Supported source/target | Supported source/target |

    **Important:** Lakehouse does support SQL. The distinction is the primary engineering experience and workload, not “Spark only” versus “SQL only.”

    **Microsoft Learn:** [What is a lakehouse in Microsoft Fabric? — Lakehouse vs. warehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview#lakehouse-vs-warehouse)

??? info "Notebook vs Pipeline vs Dataflow Gen2"

    | Fabric item | Use it for |
    | --- | --- |
    | Notebook | Code-first ingestion, preparation, complex transformation, and Spark engineering |
    | Pipeline | Orchestration, dependencies, scheduling, automation, and scalable data movement |
    | Dataflow Gen2 | Low-code Power Query ingestion, preparation, and transformation |

    **FabricOps recommendation:** keep project engineering logic visible in `02_pipeline`, then use native Fabric orchestration when the notebook needs to run as part of a scheduled or dependent workflow.

    **Microsoft Learn:** [Data ingestion options for a lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/load-data-lakehouse) · [Pipeline overview](https://learn.microsoft.com/en-us/fabric/data-factory/pipeline-overview) · [What is Dataflow Gen2?](https://learn.microsoft.com/en-us/fabric/data-factory/dataflows-gen2-overview)

??? info "Delta vs Parquet"

    | | Parquet | Delta Lake |
    | --- | --- | --- |
    | Core idea | Columnar file format | Parquet files plus a transaction log |
    | ACID transactions | Not provided by the file format itself | Supported |
    | Time travel / table history | Not provided by the file format itself | Supported |
    | Schema evolution | File-level capability only | Managed as part of the Delta table |
    | FabricOps use | File source/interchange where appropriate | Governed Lakehouse tables |

    **Rule of thumb:** Parquet is a file format; Delta is a table/storage layer built on Parquet plus transaction state.

    **Microsoft Learn:** [Delta Lake overview](https://learn.microsoft.com/en-us/fabric/fundamentals/delta-lake-overview)

??? info "PySpark vs Warehouse SQL — FabricOps recommendation"

    | Need | Prefer |
    | --- | --- |
    | Project-specific transformation after data is already in Spark | PySpark |
    | Filter or project Warehouse rows before they reach Spark | Warehouse SQL via `read_warehouse_query()` |
    | Aggregate a Warehouse source before transfer | Warehouse SQL via `read_warehouse_query()` |
    | Join DataFrames already in Spark | PySpark |
    | Window, cleansing, reshaping, and engineering logic in `02_pipeline` | PySpark |

    Spark SQL is valid in Fabric notebooks, but FabricOps does not teach it as a second default transformation language beside PySpark. SQL is shown mainly where pushing work into the Warehouse engine reduces what Spark needs to receive.

    **Microsoft Learn:** [What is Microsoft Fabric Data Engineering?](https://learn.microsoft.com/en-us/fabric/data-engineering/data-engineering-overview) · [What is a lakehouse in Microsoft Fabric?](https://learn.microsoft.com/en-us/fabric/data-engineering/lakehouse-overview)

??? info "Full vs incremental processing"

    | Strategy | Use when |
    | --- | --- |
    | Full dataset | The source is small/simple enough to reprocess, or there is no reliable incremental key |
    | Incremental watermark | A timestamp or increasing sequence identifies new or changed rows |
    | Incremental partition | A date/snapshot partition is the correct unit of change and processing |

    **FabricOps rule:** checkpoint/watermark state represents successful processing. Do not advance it until the governed target write succeeds.

    **Microsoft Learn:** [Incrementally load data from Data Warehouse to Lakehouse](https://learn.microsoft.com/en-us/fabric/data-factory/tutorial-incremental-copy-data-warehouse-lakehouse) · [Incremental copy in Copy job](https://learn.microsoft.com/en-us/fabric/data-factory/incremental-copy-job)

??? info "WHERE vs HAVING"

    | Clause | Filters |
    | --- | --- |
    | `WHERE` | Source rows before aggregation |
    | `HAVING` | Groups after `GROUP BY` has calculated aggregates |

    ```sql
    SELECT
        programme_code,
        COUNT(*) AS student_count
    FROM dbo.student_enrolment
    WHERE status = 'ACTIVE'
    GROUP BY programme_code
    HAVING COUNT(*) > 100;
    ```

    **FabricOps use:** this commonly appears inside `read_warehouse_query()` when aggregation should be pushed down to the Warehouse.

??? info "Join types"

    | Join | Use when |
    | --- | --- |
    | `inner` | Keep only matching rows from both sides |
    | `left` | Keep every row from the main/left dataset and add matches where available |
    | `full` | Keep rows from both sides, matched or unmatched |
    | `left_semi` | Keep left rows that have a match without adding right-side columns |
    | `left_anti` | Keep left rows that have no match |

    `left_semi` and `left_anti` are especially useful for existence checks, reconciliation, and identifying missing reference matches.

    **Microsoft Learn:** [Data ingestion options for a lakehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/load-data-lakehouse) for the broader notebook/Spark engineering context.

??? info "Deduplication choices"

    | Pattern | Use when |
    | --- | --- |
    | `distinct()` | Entire duplicate rows should be removed |
    | `dropDuplicates(keys)` | Any one row per key is acceptable |
    | Window + `row_number()` | Business logic determines exactly which row survives |

    **FabricOps recommendation:** when the surviving record matters, make the rule explicit with a window such as “latest `modified_datetime` per business key.”

??? info "Repartition vs coalesce"

    | Function | What it does | Typical use |
    | --- | --- | --- |
    | `repartition()` | Redistributes data and performs a shuffle | Increase/decrease parallelism or repartition by a known key |
    | `coalesce()` | Usually reduces partitions with less movement | Reduce partition/file count after the main transformation |

    Neither is a default performance fix. Choose them only when the real data shape and write behaviour justify the cost.

    **Microsoft Learn:** [What is Microsoft Fabric Data Engineering?](https://learn.microsoft.com/en-us/fabric/data-engineering/data-engineering-overview) for the broader Spark/notebook engineering context.

??? info "What FabricOps standardises vs what the project owns"

    | FabricOps standardises | Project owns |
    | --- | --- |
    | Environment-aware Fabric routing | Business transformation logic |
    | Governed source and target identity | Join logic and reference enrichment |
    | Processing/load strategy resolution | Derived columns and cleansing |
    | Profiling and Catalogue metadata | Business aggregations and target grain |
    | Guardrails | Domain-specific validation intent |
    | Data Contracts | Workload-specific Spark tuning |
    | Governed publication boundary | Business meaning of the resulting dataset |

    This is a **FabricOps design choice**, not a Microsoft Fabric platform restriction. Fabric provides the underlying capabilities; FabricOps standardises the repeatable governed workflow around them.

## PySpark transformation patterns

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
```

Combine conditions with `&` and `|`:

```python
df = df.filter(
    (F.col("status") == "ACTIVE")
    & (F.col("student_id").isNotNull())
)
```

### Add or replace a column

```python
df = df.withColumn(
    "modified_date",
    F.to_date("modified_datetime"),
)
```

### Cast a data type

```python
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
```

Use `coalesce()` when you want the first available value:

```python
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

Use a window when you need to control which duplicate survives:

```python
latest_window = (
    Window
    .partitionBy("student_id")
    .orderBy(F.col("modified_datetime").desc())
)

latest_df = (
    df
    .withColumn("row_number", F.row_number().over(latest_window))
    .filter(F.col("row_number") == 1)
    .drop("row_number")
)
```

### Join DataFrames

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

Common join types include `inner`, `left`, `right`, `full`, `left_semi`, and `left_anti`.

Use `left_anti` to keep rows with no match:

```python
unmatched_df = source_df.join(reference_df, "student_id", "left_anti")
```

Use `left_semi` when you only need to know whether a match exists:

```python
matched_df = source_df.join(reference_df, "student_id", "left_semi")
```

Broadcast a genuinely small lookup table when appropriate:

```python
enriched_df = source_df.join(F.broadcast(small_lookup_df), "programme_code", "left")
```

### Group and aggregate

```python
summary_df = (
    df
    .groupBy("programme", "status")
    .agg(
        F.count("*").alias("student_count"),
        F.countDistinct("student_id").alias("distinct_students"),
        F.avg("amount").alias("avg_amount"),
        F.max("modified_datetime").alias("latest_modified_datetime"),
    )
)
```

Useful aggregations include `count`, `countDistinct`, `sum`, `avg`, `min`, and `max`.

### Pivot

```python
pivoted_df = (
    df
    .groupBy("programme")
    .pivot("status")
    .agg(F.count("*"))
)
```

### Sort rows

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

### String functions

```python
df = df.withColumn("name_upper", F.upper("name"))
df = df.withColumn("name_clean", F.trim("name"))
df = df.withColumn("full_name", F.concat_ws(" ", "first_name", "last_name"))
df = df.withColumn("clean_phone", F.regexp_replace("phone", "-", ""))
df = df.withColumn("prefix", F.substring("programme_code", 1, 3))
```

### Date functions

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

### Combine datasets by column name

```python
combined_df = df1.unionByName(df2, allowMissingColumns=True)
```

Use this when compatible datasets may not have identical column order or when some columns may be absent.

## Built-ins before UDFs

Prefer Spark built-in functions whenever possible because Spark can optimise them. A normal Python UDF processes values through Python row by row and usually prevents some Spark optimisations.

Use a UDF only when the required logic cannot reasonably be expressed with built-in functions. For vectorisable custom numerical logic, a Pandas UDF may be more appropriate than a row-at-a-time UDF.

## Practical Spark performance habits

For normal FabricOps engineering work:

1. Select only the columns you need.
2. Filter unnecessary rows early.
3. Prefer built-in Spark functions over UDFs.
4. Avoid unnecessary `collect()` calls that move data to the driver.
5. Use joins deliberately; large joins can cause expensive shuffles.
6. Broadcast a small join input only when it is genuinely small enough.
7. Repartition only for a known reason.
8. Cache only when the same expensive DataFrame is reused.
9. Watch for skewed join keys and small-file problems.
10. Use `df.explain(mode="formatted")` when diagnosing a slow transformation.

### Repartition and coalesce

```python
df = df.repartition(200, "student_id")
df = df.coalesce(10)
```

`repartition()` performs a shuffle and can increase or decrease partitions. `coalesce()` is normally used to reduce partitions with less movement.

### Cache only when reused

```python
df.cache()
# ...reuse df in multiple actions...
df.unpersist()
```

These are project-level engineering choices. FabricOps does not hide them because their correct use depends on the data and workload.

## Warehouse SQL pushdown

In FabricOps, SQL is primarily useful when reading from a Fabric Warehouse. Use `read_warehouse_query()` when filtering, projection, joins, aggregation, CTEs, window calculations, or row limits should happen in the Warehouse before the result reaches Spark.

```python
source_df = read_warehouse_query(
    """
    SELECT
        programme_code,
        status,
        COUNT(*) AS student_count
    FROM dbo.student_enrolment
    WHERE modified_datetime >= '2026-01-01'
    GROUP BY
        programme_code,
        status
    HAVING COUNT(*) > 100
    ORDER BY student_count DESC
    """,
    target="product",
)
```

### SQL clauses to remember

```sql
SELECT ...
FROM ...
JOIN ... ON ...
WHERE ...
GROUP BY ...
HAVING ...
ORDER BY ...
```

`WHERE` filters source rows before aggregation. `HAVING` filters groups after `GROUP BY` has calculated the aggregates.

### CTE

```sql
WITH latest AS (
    SELECT
        student_id,
        modified_datetime,
        ROW_NUMBER() OVER (
            PARTITION BY student_id
            ORDER BY modified_datetime DESC
        ) AS rn
    FROM dbo.student_enrolment
)
SELECT *
FROM latest
WHERE rn = 1;
```

Use SQL pushdown when the Warehouse can reduce the amount of data that Spark needs to receive. Continue the project-specific transformation in PySpark after the query returns a Spark DataFrame.

## Full vs incremental processing

### Full dataset

Use a full load when the source is small enough to reprocess safely and simply, or when the source does not provide a reliable incremental key.

```text
Read all source rows → Transform → Write complete target
```

### Incremental watermark

Use a watermark when a monotonically increasing timestamp or sequence can identify new or changed rows.

```text
Last successful watermark
        ↓
Read newer rows
        ↓
Transform and write
        ↓
Commit the new watermark only after success
```

The important rule is that the watermark represents successful processing state. Do not advance it before the governed target write succeeds.

### Incremental partition

Use partition-based processing when the source exposes meaningful partitions such as a snapshot or business date and those partitions are the correct unit of change detection and processing.

## MERGE / upsert

A merge pattern is useful when an incremental load needs to update existing keys and insert new keys rather than replacing the complete target.

Treat MERGE as a load pattern, not a default transformation step. In FabricOps, the actual write behaviour should follow the governed load strategy for the selected target.

## SCD patterns

Use SCD Type 1 when the latest value should replace the previous value. Use SCD Type 2 when historical versions must remain queryable.

These are target load strategies, not generic transformations to add automatically to every pipeline.

## Quick decision guide

| Need | Prefer |
| --- | --- |
| Project-specific transformation after data is in Spark | PySpark |
| Reduce/filter/aggregate a Fabric Warehouse source before Spark | `read_warehouse_query()` + SQL |
| Find rows with no lookup match | `left_anti` join |
| Keep rows that have a lookup match without adding lookup columns | `left_semi` join |
| Small lookup joined to a much larger DataFrame | Broadcast join when appropriate |
| Keep one controlled record per duplicate business key | Window + `row_number()` |
| Rank or compare rows within a group | Window functions |
| Summarise rows | `groupBy(...).agg(...)` |
| Reshape values into columns | `pivot()` |
| Flatten arrays or nested structures | `explode()` / struct column access |
| Combine compatible datasets with different column order | `unionByName()` |
| Simple complete reprocessing | Full dataset |
| Process only records newer than a reliable state value | Incremental watermark |
| Process changed date/snapshot partitions | Incremental partition |
| Update existing keys and insert new ones | Governed MERGE/upsert load strategy |

For FabricOps-specific function parameters and contracts, use the [Function Reference](index.md). For the worked learning path, return to [Module 2: Engineer and run a data pipeline](../guided-demo/02-run-pipeline.md).
