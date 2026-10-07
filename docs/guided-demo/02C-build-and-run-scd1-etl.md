# Step 2C. SCD Type 1

This is an **optional processing-mode demo**. It uses tiny inline data, so there is nothing extra to upload.

## Story

A customer changes from **Basic** to **Premium**. With SCD1, the latest value replaces the previous value.

Copy `02_pipeline` in Fabric and name the copy something like `02C_scd1_demo`. Keep the original notebook unchanged.

## 1. Create the first customer state

```python
from fabricops_kit import pipeline_read, pipeline_write, write_lakehouse_table

batch_1 = spark.createDataFrame([
    ("C001", "Basic", "SG"),
    ("C002", "Premium", "MY"),
], ["customer_id", "membership", "country"])

write_lakehouse_table(
    batch_1,
    "customers_scd1_source",
    store="Bronze",
    schema="demo",
    mode="overwrite",
)

source = pipeline_read(
    store="Bronze",
    schema="demo",
    table_name="customers_scd1_source",
    read_mode="full",
    spark_session=spark,
)

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
```

## 2. Apply a change

```python
batch_2 = spark.createDataFrame([
    ("C001", "Premium", "SG"),
    ("C003", "Basic", "AU"),
], ["customer_id", "membership", "country"])

write_lakehouse_table(
    batch_2,
    "customers_scd1_source",
    store="Bronze",
    schema="demo",
    mode="overwrite",
)

source = pipeline_read(
    store="Bronze",
    schema="demo",
    table_name="customers_scd1_source",
    read_mode="full",
    spark_session=spark,
)

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
```

## Expected result

```text
C001  Premium  SG   ← updated
C002  Premium  MY   ← unchanged
C003  Basic    AU   ← inserted
```

There should still be **one row per customer**.

**Next optional mode:** [Step 2D. SCD Type 2](02D-build-and-run-scd2-etl.md)
