# Step 2C. SCD Type 1 vs Type 2

This is an **optional processing-mode demo** using two tiny inline snapshots. There is nothing extra to upload.

## Story

A source system sends a complete customer snapshot each day.

On Day 2, customer C001 changes from **Basic** to **Premium**, while C003 appears for the first time.

The same Day 2 snapshot is written using SCD1 and SCD2 so you can see the difference immediately.

## 1. Day 1 system snapshot

```python
from datetime import datetime
from fabricops_kit import pipeline_write

day_1 = spark.createDataFrame([
    ("C001", "Basic", "SG", datetime(2026, 10, 6, 9, 0)),
    ("C002", "Premium", "MY", datetime(2026, 10, 6, 9, 0)),
], ["customer_id", "membership", "country", "modified_datetime"])
```

Write the same starting snapshot to two separate targets:

```python
pipeline_write(
    day_1,
    store="Silver",
    schema="demo",
    table_name="customers_scd1",
    load_strategy="scd1",
    load_strategy_parameters={
        "key_columns": ["customer_id"],
    },
    spark_session=spark,
)

pipeline_write(
    day_1,
    store="Silver",
    schema="demo",
    table_name="customers_scd2",
    load_strategy="scd2",
    load_strategy_parameters={
        "key_columns": ["customer_id"],
        "effective_column": "modified_datetime",
        "tracked_columns": ["membership", "country"],
    },
    spark_session=spark,
)
```

## 2. Day 2 system snapshot

```python
day_2 = spark.createDataFrame([
    ("C001", "Premium", "SG", datetime(2026, 10, 7, 9, 0)),
    ("C002", "Premium", "MY", datetime(2026, 10, 7, 9, 0)),
    ("C003", "Basic", "AU", datetime(2026, 10, 7, 9, 0)),
], ["customer_id", "membership", "country", "modified_datetime"])
```

Run the same two writes again, this time using `day_2`.

## What changes?

### SCD1

SCD1 keeps only the latest state.

```text
C001  Premium  SG   ← updated
C002  Premium  MY   ← unchanged
C003  Basic    AU   ← inserted
```

There is still one row per customer.

### SCD2

SCD2 keeps history.

C001 now has two versions:

```text
C001  Basic    SG   ← historical
C001  Premium  SG   ← current
```

C002 remains current and C003 is inserted as a new current row.

Inspect `_effective_from`, `_effective_to`, and `_is_current` to see the history.

## The mental model

**SCD1:** keep the latest version.

**SCD2:** keep the latest version and preserve previous versions.

**Next:** return to [Step 3. Author and freeze the Data Contract](03-author-and-freeze-data-contract.md).
