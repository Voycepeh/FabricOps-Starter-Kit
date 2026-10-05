# PySpark Transformation Reference

FabricOps deliberately leaves project-specific transformation as ordinary PySpark between the governed Read and Write boundaries.

Use this page as a quick reference when building the transformation section of `02_pipeline`. These are standard PySpark patterns rather than FabricOps-specific APIs.

The examples assume:

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window
```

## Inspect and select

Use these operations to understand the DataFrame you received from [`orchestrate_read()`](../api/reference/orchestrate_read.md) and keep only the columns needed by the transformation. `select()` creates a DataFrame with the chosen columns; `drop()` removes columns; `withColumnRenamed()` changes a column name without changing its values.

```python
display(df)
df.show(20, truncate=False)
df.printSchema()
df.count()

df = df.select("student_id", "programme", "status", "modified_datetime")
df = df.withColumnRenamed("old_name", "new_name")
df = df.drop("temporary_column")
```

## Filter, derive, and cast

Filtering removes rows that do not meet a condition. Deriving creates a new column from existing values. Casting changes a column to the data type expected by later transformation or the target schema.

For example, if the source contains active and inactive students, `filter()` can retain only active rows. `to_date()` can then derive a date-only value from a timestamp.

```python
df = df.filter(
    (F.col("status") == "ACTIVE")
    & F.col("student_id").isNotNull()
)

df = df.withColumn("modified_date", F.to_date("modified_datetime"))
df = df.withColumn("student_id", F.col("student_id").cast("string"))
```

## Conditional logic and nulls

Use conditional expressions when a new value depends on existing data. `when(...).otherwise(...)` is the PySpark equivalent of CASE logic. Null-handling functions let you replace defaults, reject incomplete rows, or choose the first available value.

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

## Deduplication

Deduplication is useful when more than one source row represents the same business record. `dropDuplicates()` keeps one row but does not give you precise control over which duplicate survives. When the newest or highest-priority record must win, use a window and `row_number()` instead.

For example, partitioning by `student_id` and sorting by `modified_datetime` descending lets you retain the latest record for each student.

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

## Joins

Joins combine DataFrames using a shared key. A `left` join keeps every row from the main DataFrame and adds matching lookup values. `left_anti` returns rows with no match and is useful for finding exceptions. `left_semi` returns rows that have a match without bringing columns from the second DataFrame into the result.

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

## Group, aggregate, pivot, and sort

Aggregation changes the grain of the data. `groupBy()` defines the grouping columns and `agg()` calculates measures such as counts, totals, or averages for each group. `pivot()` turns values from one column into separate output columns.

For example, order-level rows can be grouped by customer to produce one customer-level summary row.

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

## Window functions

Window functions calculate values across related rows **without collapsing those rows into one aggregate row**. They are useful for ranking, latest-record selection, previous/next comparisons, and running totals.

A window normally defines a partition—such as one customer—and an ordering—such as transaction time. Spark then evaluates the window expression within that ordered group.

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

## Strings, dates, nested data, and unions

These are common reshaping operations when source data does not yet match the structure needed by the target. String functions clean text, date functions derive reporting periods, `explode()` turns array elements into rows, nested fields can be flattened with `select()`, and `unionByName()` stacks compatible DataFrames.

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

## Spark optimization reminders

Correct transformation logic comes first. Once the result is correct, these habits help avoid unnecessary Spark work. They are guidelines rather than rules—the right choice depends on data volume, partitioning, skew, and how often a DataFrame is reused.

1. Select only the columns you need.
2. Filter rows as early as practical.
3. Prefer built-in Spark functions over Python UDFs.
4. Avoid unnecessary `collect()` calls that move data to the driver.
5. Expect wide joins, `groupBy`, `distinct`, and repartitioning to create shuffle.
6. Broadcast only genuinely small lookup DataFrames.
7. Cache only expensive DataFrames that are reused.
8. Watch for skewed keys and uneven partitions.
9. Avoid excessive small output files.
10. Inspect the execution plan before guessing at a performance fix.

### Repartition versus coalesce

Both change the number of Spark partitions, but they solve different problems. `repartition()` redistributes data and can increase or decrease parallelism; because it shuffles data, it is relatively expensive. `coalesce()` is mainly useful for reducing partitions with less movement, often near the end of processing.

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

### Join and shuffle habits

Joins and aggregations are common shuffle boundaries, so reduce the amount of data reaching them before tuning partition counts. Select only required columns and filter rows as early as practical. When a large join is repeatedly expensive, inspect whether the data is distributed sensibly for the join key rather than adding `repartition()` automatically.

```python
filtered_df = (
    source_df
    .select("student_id", "programme_code", "status")
    .filter(F.col("status") == "ACTIVE")
)

prepared_df = filtered_df.repartition("programme_code")
joined_df = prepared_df.join(programme_df, "programme_code", "left")
```

Repartitioning by a join key can help in some workloads, but it also creates a shuffle itself. Use the execution plan and Spark UI to confirm that the extra redistribution is worthwhile. In the Spark UI, large shuffle read/write volumes, uneven task sizes, and long-running straggler tasks are useful signals for shuffle or skew problems.

### Partition sizing and partitioned writes

Avoid both a very small number of oversized partitions and a very large number of tiny partitions. A target around **128 MB per partition** can be a useful starting heuristic for some workloads, but it is not a FabricOps requirement or a universal Spark optimum. Data shape, executor resources, skew, compression, and the operation being performed all affect the right size.

Storage partitioning is a separate decision. Partitioning a large output by a column commonly used for filtering, such as a date, can enable partition pruning and reduce the amount of data scanned. Avoid high-cardinality partition columns that create excessive directories or small files.

```python
(
    df.write
    .mode("overwrite")
    .partitionBy("event_date")
    .format("delta")
    .save(output_path)
)
```

When using FabricOps write helpers, prefer the supported write configuration rather than bypassing the helper solely to control physical partitioning.

### Cache only reused work

Caching can help when the same expensive intermediate DataFrame is evaluated multiple times. It can waste memory when the DataFrame is used only once, so do not cache every transformation by default.

```python
df.cache()
# multiple actions that reuse df
df.unpersist()
```

### Inspect the execution plan

When a transformation is unexpectedly slow, inspect Spark's plan before changing partition counts or adding caches. The plan shows how Spark intends to scan, join, shuffle, and aggregate the data.

```python
df.explain(mode="formatted")
```

Look for expensive exchanges or shuffles, large joins, repeated scans, and whether filters or projections happen early enough.

!!! note "Spark partitioning is not incremental processing"
    **Incremental processing** decides which logical source data this run should process.

    **Spark partitioning** decides how Spark distributes a DataFrame for compute or write.

## Related FabricOps documentation

- [Step 2: Build and run the ETL](../guided-demo/02-build-and-run-etl.md)
- [Plug-and-Play Data Pipelines with Data Contract Enforcement](../solutions/plug-and-play-data-pipelines.md)
- [Read & Write Modes](read-and-load-strategies.md)
