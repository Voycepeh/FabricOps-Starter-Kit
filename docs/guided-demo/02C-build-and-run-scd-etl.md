# Step 2C. SCD Type 1 vs Type 2

This is an **optional processing-mode demo** using two tiny inline snapshots of a simple food product table. There is nothing extra to upload.

## Story

A source system provides the current **food product table of truth**.

On Day 2, P001 moves from **Snack** to **Healthy Snack**, P002 changes price, and P003 appears for the first time.

The same Day 2 snapshot is written using SCD1 and SCD2 so you can see the difference immediately.

## 1. Day 1 product snapshot

```python
from datetime import datetime
from fabricops_kit import orchestrate_write

day_1 = spark.createDataFrame([
    ("P001", "Snack", 2.50, datetime(2026, 10, 6, 9, 0)),
    ("P002", "Drink", 1.80, datetime(2026, 10, 6, 9, 0)),
], ["product_id", "category", "price", "modified_datetime"])
```

Write the same starting snapshot to two separate targets:

```python
orchestrate_write(
    day_1,
    name="product_mapping_scd1",
    sources=[],
    store="Silver",
    schema="demo",
    table_name="product_mapping_scd1",
    write_mode="scd1",
    write_parameters={
        "key_columns": ["product_id"],
    },
    spark_session=spark,
)

orchestrate_write(
    day_1,
    name="product_mapping_scd2",
    sources=[],
    store="Silver",
    schema="demo",
    table_name="product_mapping_scd2",
    write_mode="scd2",
    write_parameters={
        "key_columns": ["product_id"],
        "effective_column": "modified_datetime",
        "tracked_columns": ["category", "price"],
    },
    spark_session=spark,
)
```

## 2. Day 2 product snapshot

```python
day_2 = spark.createDataFrame([
    ("P001", "Healthy Snack", 2.50, datetime(2026, 10, 7, 9, 0)),
    ("P002", "Drink", 2.00, datetime(2026, 10, 7, 9, 0)),
    ("P003", "Snack", 3.20, datetime(2026, 10, 7, 9, 0)),
], ["product_id", "category", "price", "modified_datetime"])
```

Run the same two `orchestrate_write()` calls again, this time using `day_2`.

## What changes?

The comparison is simple:

1. Match the incoming row to the existing row by `product_id`.
2. Compare the tracked business columns, here `category` and `price`.
3. If none of those values changed, keep the existing current record.
4. If any tracked value changed, apply the selected SCD behavior.

So this is **not limited to one column**. FabricOps can track multiple attributes for the same business key.

### SCD1

SCD1 keeps the mapping table as the latest truth.

```text
P001  Healthy Snack  2.50  ← category updated
P002  Drink          2.00  ← price updated
P003  Snack          3.20  ← inserted
```

There is still one row per product.

### SCD2

SCD2 keeps the mapping history.

P001 now has two versions because `category` changed:

```text
P001  Snack          2.50  ← historical
P001  Healthy Snack  2.50  ← current
```

P002 also gets a new version because `price` changed from 1.80 to 2.00. P003 is inserted as a new current row.

Inspect `_effective_from`, `_effective_to`, and `_is_current` to see when each mapping was valid.

## The mental model

**SCD1:** keep the latest mapping as the current truth.

**SCD2:** keep the current mapping and preserve previous versions when any tracked column changes.

**Next:** return to [Step 3. Author and freeze the Data Contract](03-author-and-freeze-data-contract.md).
