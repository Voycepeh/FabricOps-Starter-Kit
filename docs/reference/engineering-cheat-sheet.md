# Fabric Engineering Cheat Sheet

Use this page when you know the transformation you need and want a quick reminder of the syntax. The Guided Demo explains these patterns in context; the `02_pipeline` template stays intentionally lightweight and only provides the place for project-specific transformation code.

FabricOps standardises the governed workflow around engineering. Your project still owns the transformation logic.

## PySpark transformation patterns

The examples below assume:

```python
from pyspark.sql import functions as F
from pyspark.sql.window import Window
```

### Select columns

Keep only the columns needed downstream.

```python
df = df.select(
    "student_id",
    "programme",
    "status",
    "modified_datetime",
)
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

### Rename a column

```python
df = df.withColumnRenamed("old_name", "new_name")
```

### Drop columns

```python
df = df.drop("temporary_column")
```

### Handle nulls

```python
df = df.fillna({"status": "UNKNOWN"})
```

```python
df = df.filter(F.col("student_id").isNotNull())
```

### Distinct rows

```python
df = df.distinct()
```

### Deduplicate by key

```python
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

### Group and aggregate

```python
summary_df = (
    df
    .groupBy("programme", "status")
    .agg(
        F.count("*").alias("student_count"),
        F.max("modified_datetime").alias("latest_modified_datetime"),
    )
)
```

Useful aggregations include `count`, `countDistinct`, `sum`, `avg`, `min`, and `max`.

### Sort rows

```python
df = df.orderBy(
    F.col("programme").asc(),
    F.col("modified_datetime").desc(),
)
```

### Window calculations

```python
programme_window = Window.partitionBy("programme")

df = df.withColumn(
    "programme_student_count",
    F.count("*").over(programme_window),
)
```

### Repartition before a large write

Use only when the data shape justifies it. Repartitioning causes a shuffle.

```python
df = df.repartition("snapshot_date")
```

Do not use repartitioning as a default performance fix. Poor partition choices can create unnecessary shuffle or many small files.

### Cache only when reused

```python
df.cache()
```

Cache a DataFrame only when an expensive result will be reused multiple times in the same Spark session.

## Practical Spark habits

For normal FabricOps engineering work:

1. Select only the columns you need.
2. Filter unnecessary rows early.
3. Avoid unnecessary `collect()` calls that move data to the driver.
4. Use joins deliberately; large joins can cause expensive shuffles.
5. Repartition only for a known reason.
6. Cache only when the same expensive DataFrame is reused.
7. Watch for small-file problems when choosing physical partitioning.

These are project-level engineering choices. FabricOps does not hide them because their correct use depends on the data and workload.

## Warehouse SQL pushdown

In FabricOps, SQL is primarily useful when reading from a Fabric Warehouse. Use `read_warehouse_query()` when filtering, projection, joins, aggregation, or row limits should happen in the Warehouse before the result reaches Spark.

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

The exact implementation depends on the target and the FabricOps load strategy in use. Treat MERGE as a load pattern, not a default transformation step.

## Quick decision guide

| Need | Prefer |
| --- | --- |
| Project-specific transformation after data is in Spark | PySpark |
| Reduce/filter/aggregate a Fabric Warehouse source before Spark | `read_warehouse_query()` + SQL |
| Simple complete reprocessing | Full dataset |
| Process only records newer than a reliable state value | Incremental watermark |
| Process changed date/snapshot partitions | Incremental partition |
| Keep one controlled record per duplicate business key | Window + `row_number()` |
| Summarise rows | `groupBy(...).agg(...)` |
| Add reference attributes | Join |
| Create a derived field | `withColumn()` |

For FabricOps-specific function parameters and contracts, use the [Function Reference](index.md). For the worked learning path, return to [Module 2: Engineer and run a data pipeline](../guided-demo/02-run-pipeline.md).
