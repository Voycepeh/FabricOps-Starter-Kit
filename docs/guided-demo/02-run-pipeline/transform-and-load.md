# Unit 4: Transform and load

**Keep business transformation logic visible, then let the template handle the standard FabricOps load boundary.**

## Add project-specific transformation

Use the **User defined transformation** section in `02_pipeline` for joins, filters, derivations, aggregations, enrichment, and reshaping.

![Transform DataFrame](../../assets/02/Transform_DF.png)

FabricOps standardises the governed boundary around ETL. It does not replace the transformation logic that belongs to the project.

The `02_pipeline` template deliberately stays lightweight. It shows where project transformation belongs without carrying a full PySpark tutorial into every new pipeline. This Guided Demo teaches the common patterns; use the [FabricOps Engineering Guide](../../reference/engineering-cheat-sheet.md) when you want the deeper engineering explanation or a syntax reminder.

## Core PySpark patterns

Most project-specific transformation in `02_pipeline` should remain in PySpark once the source has been read into a Spark DataFrame.

!!! info "New to PySpark in Microsoft Fabric?"

    FabricOps intentionally uses PySpark as the normal transformation path inside `02_pipeline`. This demo only teaches the patterns needed to understand the FabricOps workflow; it is not intended to replace the official Spark learning material.

    Use Microsoft Learn when you want to go deeper into Fabric notebooks and Spark:

    [Microsoft Learn: Fabric Data Engineering](https://learn.microsoft.com/en-us/fabric/data-engineering/) · [Author and execute Fabric notebooks](https://learn.microsoft.com/en-us/fabric/data-engineering/author-execute-notebook) · [Use Python for Apache Spark in Fabric](https://learn.microsoft.com/en-us/fabric/data-science/python-guide/python-overview)

    Fabric notebooks also support Spark SQL, Scala, and SparkR. PySpark is the **FabricOps recommendation** for project transformation consistency, not a Microsoft Fabric platform restriction.

### Select only what you need

Use `select()` to make the intended output columns explicit and avoid carrying unnecessary data through later transformations.

```python
transformed_df = source_1_df.select(
    "student_id",
    "programme_code",
    "status",
    "modified_datetime",
)
```

### Filter rows

Use `filter()` to keep only rows that should continue through the pipeline.

```python
transformed_df = transformed_df.filter(
    (F.col("status") == "ACTIVE")
    & (F.col("student_id").isNotNull())
)
```

### Create or change columns

Use `withColumn()` for derived fields and casting.

```python
transformed_df = transformed_df.withColumn(
    "modified_date",
    F.to_date("modified_datetime"),
)
```

```python
transformed_df = transformed_df.withColumn(
    "student_id",
    F.col("student_id").cast("string"),
)
```

### Conditional logic

Use `when()` / `otherwise()` when a derived value depends on row conditions.

```python
transformed_df = transformed_df.withColumn(
    "status_group",
    F.when(F.col("status") == "ACTIVE", "Current")
     .when(F.col("status") == "COMPLETED", "Completed")
     .otherwise("Other"),
)
```

### Handle missing values

Use null handling deliberately rather than letting missing values flow unnoticed through the transformation.

```python
transformed_df = transformed_df.fillna({"status": "UNKNOWN"})
```

Use `coalesce()` when you want the first available value from several columns:

```python
transformed_df = transformed_df.withColumn(
    "contact",
    F.coalesce("mobile", "email", F.lit("no_contact")),
)
```

### Remove duplicates

Use `dropDuplicates()` when any surviving row is acceptable for a duplicate key.

```python
transformed_df = transformed_df.dropDuplicates(["student_id"])
```

When the surviving row matters, use a window so the choice is explicit. A common example is keeping the most recently modified row.

```python
from pyspark.sql.window import Window

latest_window = (
    Window
    .partitionBy("student_id")
    .orderBy(F.col("modified_datetime").desc())
)

transformed_df = (
    transformed_df
    .withColumn("row_number", F.row_number().over(latest_window))
    .filter(F.col("row_number") == 1)
    .drop("row_number")
)
```

The same window pattern extends to ranking, previous/next values with `lag()` and `lead()`, and running totals. Those patterns are included in the [FabricOps Engineering Guide](../../reference/engineering-cheat-sheet.md).

### Join another source

If the pipeline has multiple upstream sources, join their DataFrames in the transformation section.

```python
transformed_df = (
    source_1_df.alias("e")
    .join(
        source_2_df.alias("p"),
        F.col("e.programme_code") == F.col("p.programme_code"),
        "left",
    )
)
```

Use `left_anti` when you need rows with no match and `left_semi` when you only need rows that have a match without adding columns from the right side.

```python
unmatched_df = source_1_df.join(source_2_df, "student_id", "left_anti")
```

Multiple sources may fan into this transformation, but the governed pipeline still publishes one target table.

### Aggregate

Use `groupBy()` and `agg()` when the target represents a summarised grain.

```python
transformed_df = (
    source_1_df
    .groupBy("programme_code", "status")
    .agg(
        F.count("*").alias("student_count"),
        F.countDistinct("student_id").alias("distinct_students"),
        F.max("modified_datetime").alias("latest_modified_datetime"),
    )
)
```

The important engineering decision is not the syntax itself. Confirm that the resulting grain and business meaning are correct for the governed target you selected.

### Reshape or flatten when the data requires it

Other common project patterns include `pivot()` for reshaping values into columns, `explode()` for arrays, struct access for nested JSON, and `unionByName()` for combining compatible datasets with different column order. These are useful, but they are not part of every pipeline, so the full examples stay in the [FabricOps Engineering Guide](../../reference/engineering-cheat-sheet.md).

## When SQL appears in `02_pipeline`

FabricOps does not treat Spark SQL as a second default transformation language beside PySpark. SQL is most useful when reading a Fabric Warehouse and the Warehouse can reduce the data before it reaches Spark.

!!! info "New to SQL in Fabric Warehouse?"

    FabricOps mainly uses SQL for Warehouse-side filtering, projection, joins, aggregation, CTEs, window calculations, and row limits through `read_warehouse_query()`.

    Use Microsoft Learn for the full Warehouse SQL surface rather than treating the examples below as a complete SQL tutorial:

    [Microsoft Learn: T-SQL surface area in Fabric Data Warehouse](https://learn.microsoft.com/en-us/fabric/data-warehouse/tsql-surface-area) · [Spark connector for Fabric Data Warehouse](https://learn.microsoft.com/en-us/fabric/data-engineering/spark-data-warehouse-connector)

    Fabric Warehouse supports a broad T-SQL surface, but support is not identical to SQL Server. Check the Fabric T-SQL surface-area page when you need syntax beyond the common read/query patterns shown here.

Use `read_warehouse_query()` for engineer-authored Warehouse projection, filtering, joins, aggregation, CTEs, window calculations, or row limits that should be pushed down to the Warehouse engine.

```python
source_1_df = read_warehouse_query(
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
    target=SOURCE_TARGET,
    spark_session=spark,
)
```

Here:

- `WHERE` filters source rows before aggregation,
- `GROUP BY` defines the groups being summarised,
- `HAVING` filters those groups after the aggregate has been calculated,
- `ORDER BY` sorts the query result.

After the Warehouse query returns, continue the project-specific engineering work using the returned PySpark DataFrame.

!!! tip "Why push SQL down to the Warehouse?"

    If the Warehouse can return only the rows and columns the pipeline needs, less data has to move into Spark. This is especially useful for narrow filters, projections, aggregations, and joins that the Warehouse engine can perform efficiently.

## A few Spark habits that matter

Keep these in mind when transformations become larger:

- select only the columns you need,
- filter unnecessary rows early,
- prefer Spark built-in functions over Python UDFs where possible,
- avoid unnecessary `collect()` calls,
- expect large joins and repartitioning to cause shuffle,
- consider broadcasting only genuinely small lookup DataFrames,
- cache only when an expensive DataFrame will be reused,
- choose physical partitions carefully to avoid unnecessary small files,
- use `df.explain(mode="formatted")` when diagnosing a slow transformation.

These are project-level engineering choices, so FabricOps keeps them visible instead of trying to hide them behind the starter kit.

For the deeper engineering explanation and the full syntax reference, including windows, string/date functions, nested data, `unionByName`, repartitioning, caching, and full versus incremental processing, use the [FabricOps Engineering Guide](../../reference/engineering-cheat-sheet.md).

## Choose the target

The template supports managed Lakehouse and Warehouse targets, but each governed pipeline publishes exactly one target table.

### Lakehouse target

![Write Lakehouse](../../assets/02/Write_LH.png)

After persistence, read the complete physical target back and profile/register it so the catalogue represents the stored result rather than only an intermediate DataFrame.

![Read written Lakehouse table](../../assets/02/Read_Written_LH.png)

### Warehouse target

Create the target schema first when required:

```sql
CREATE SCHEMA demo
```

![Create Warehouse schema](../../assets/02/create_schema.png)

Then execute the Warehouse target section.

![Write Warehouse](../../assets/02/Write_WH.png)

## Why the guided pattern uses one target

It is technically possible to clone the write block and publish multiple targets from one notebook. FabricOps does not stop you from doing that.

The gap is that those physical writes are independent. For example, Target A can be written successfully and Target B can then fail because of permissions, a connector issue, a timeout, locking, or another Fabric runtime error. There is no notebook-level transaction that automatically rolls Target A back, so the pipeline can finish in a partial-success state.

Because of that, the governed `02_pipeline` pattern deliberately uses **fan-in**: one or many upstream sources may feed the transformation, but each pipeline publishes one governed target table.

## Need another persisted output?

Create a separate downstream pipeline rather than adding another governed target write to the same pipeline.

This keeps each pipeline responsible for one publication boundary. The output of the first pipeline can become an upstream source for the next pipeline when another persisted stage is needed.

Do not use a pipeline's own target as an engineer-authored source inside the same pipeline. Persisted intermediate tables should form explicit stages between separate pipelines.

## Partitioning and parallelism

`partition_by` controls physical Lakehouse storage layout. `repartition_by` can change Spark write parallelism. Use either only when it fits the real data shape because poor partition choices can create small files or unnecessary shuffle overhead.

![Write Lakehouse in parallel](../../assets/02/Write_LH_Parallel.png)

These physical write choices are separate from FabricOps incremental processing strategy, which determines which logical source data should be processed during a run.

## Function details

Use the [Function Reference](../../reference/index.md) for exact parameters for `write_lakehouse_table()`, `write_warehouse_table()`, `profile_dataframe()`, `profile_frequency_distribution()`, and `profile_and_register_table()`.

**Previous:** [Unit 3: Configure sources](configure-sources.md)  
**Next:** [Unit 5: Choose processing behaviour and review results](processing-and-results.md)
