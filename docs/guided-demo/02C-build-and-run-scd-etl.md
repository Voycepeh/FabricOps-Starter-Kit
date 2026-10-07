# Step 2C. SCD Type 1 vs Type 2

This is an **optional processing-mode demo**. It uses tiny inline customer data, so there is nothing extra to upload.

## Story

Customer C001 changes from **Basic** to **Premium**.

Run the same change twice:

- **SCD1** keeps only the latest customer state.
- **SCD2** keeps the previous state as history.

Copy `02_pipeline` in Fabric and name the copy something like `02C_scd_demo`. Keep the original notebook unchanged.

## 1. Create the starting data

```python
from datetime import datetime
from fabricops_kit import pipeline_read, pipeline_write, write_lakehouse_table

batch_1 = spark.createDataFrame([
    ("C001", "Basic", "SG", datetime(2026, 10, 1, 9, 0)),
    ("C002", "Premium", "MY", datetime(2026, 10, 1, 9, 0)),
], ["customer_id", "membership", "country", "modified_datetime"])

write_lakehouse_table(
    batch_1,
    "customers_scd_source",
    store="Bronze",
    schema="demo",
    mode="overwrite",
)

source = pipeline_read(
    store="Bronze",
    schema="demo",
    table_name="customers_scd_source",
    read_mode="full",
    spark_session=spark,
)
```

Publish the same starting state to two separate targets:

```python
pipeline_write(
    source["dataframe"],
    store="Silver",
    schema="demo",
    table_name="customers_scd1",
    load_strategy="scd1",
    load_strategy_parameters={"key_columns": ["customer_id"]},
    source_table_ids=[source["table_id"]],
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

## 2. Apply one customer change

```python
batch_2 = spark.createDataFrame([
    ("C001", "Premium", "SG", datetime(2026, 10, 7, 9, 0)),
    ("C003", "Basic", "AU", datetime(2026, 10, 7, 9, 0)),
], ["customer_id", "membership", "country", "modified_datetime"])

write_lakehouse_table(
    batch_2,
    "customers_scd_source",
    store="Bronze",
    schema="demo",
    mode="overwrite",
)

source = pipeline_read(
    store="Bronze",
    schema="demo",
    table_name="customers_scd_source",
    read_mode="full",
    spark_session=spark,
)
```

Run the same two `pipeline_write()` calls again.

## Expected result

**SCD1**

```text
C001  Premium  SG   ← updated
C002  Premium  MY   ← unchanged
C003  Basic    AU   ← inserted
```

There is still one row per customer.

**SCD2**

C001 now has two versions: the old **Basic** row is closed as history and a new **Premium** row is current. C002 remains current and C003 is inserted.

Inspect `_effective_from`, `_effective_to`, and `_is_current` to see the difference.

**Next:** return to [Step 3. Author and freeze the Data Contract](03-author-and-freeze-data-contract.md).
