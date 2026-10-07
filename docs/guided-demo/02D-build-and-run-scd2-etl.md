# Step 2D. SCD Type 2

This is an **optional processing-mode demo**. It uses tiny inline data, so there is nothing extra to upload.

## Story

A customer changes from **Basic** to **Premium**, but this time the previous value must remain available as history.

Copy `02_pipeline` in Fabric and name the copy something like `02D_scd2_demo`. Keep the original notebook unchanged.

## 1. Create the first customer state

```python
from datetime import datetime
from fabricops_kit import pipeline_read, pipeline_write, write_lakehouse_table

batch_1 = spark.createDataFrame([
    ("C001", "Basic", "SG", datetime(2026, 10, 1, 9, 0)),
    ("C002", "Premium", "MY", datetime(2026, 10, 1, 9, 0)),
], ["customer_id", "membership", "country", "modified_datetime"])

write_lakehouse_table(
    batch_1,
    "customers_scd2_source",
    store="Bronze",
    schema="demo",
    mode="overwrite",
)

source = pipeline_read(
    store="Bronze",
    schema="demo",
    table_name="customers_scd2_source",
    read_mode="full",
    spark_session=spark,
)

pipeline_write(
    source["dataframe"],
    store="Silver",
    schema="demo",
    table_name="customers_scd2",
    load_strategy="scd2",
    load_strategy_parameters={
        "key_columns": ["customer_id"],
        "effective_column": "modified_datetime",
        "tracked_columns": ["membership", "country"],
    },
    source_table_ids=[source["table_id"]],
    spark_session=spark,
)
```

## 2. Apply a change

```python
batch_2 = spark.createDataFrame([
    ("C001", "Premium", "SG", datetime(2026, 10, 7, 9, 0)),
    ("C003", "Basic", "AU", datetime(2026, 10, 7, 9, 0)),
], ["customer_id", "membership", "country", "modified_datetime"])

write_lakehouse_table(
    batch_2,
    "customers_scd2_source",
    store="Bronze",
    schema="demo",
    mode="overwrite",
)

source = pipeline_read(
    store="Bronze",
    schema="demo",
    table_name="customers_scd2_source",
    read_mode="full",
    spark_session=spark,
)

pipeline_write(
    source["dataframe"],
    store="Silver",
    schema="demo",
    table_name="customers_scd2",
    load_strategy="scd2",
    load_strategy_parameters={
        "key_columns": ["customer_id"],
        "effective_column": "modified_datetime",
        "tracked_columns": ["membership", "country"],
    },
    source_table_ids=[source["table_id"]],
    spark_session=spark,
)
```

## Expected result

C001 should now have two versions: the old **Basic** row closed as history and a new **Premium** row marked current. C002 remains current and C003 is inserted as a new current row.

Inspect `_effective_from`, `_effective_to`, and `_is_current` to verify the history.

**Next:** return to [Step 3. Author and freeze the Data Contract](03-author-and-freeze-data-contract.md).
