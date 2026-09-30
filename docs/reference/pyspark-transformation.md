# PySpark Transformation Reference

FabricOps deliberately leaves project-specific transformation as ordinary PySpark between the governed Read and Write boundaries.

Use this page as a quick reference when building the transformation section of `02_pipeline`. These are standard PySpark patterns rather than FabricOps-specific APIs.

The examples assume:

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window
```

## Inspect and select

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

```python
df = df.filter(
    (F.col("status") == "ACTIVE")
    & F.col("student_id").isNotNull()
)

df = df.withColumn("modified_date", F.to_date("modified_datetime"))
df = df.withColumn("student_id", F.col("student_id").cast("string"))
```

## Conditional logic and nulls

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

### Inspect the execution plan

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
