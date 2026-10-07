# Step 2C. SCD Type 1 vs Type 2

This is an **optional processing-mode demo** using two tiny inline snapshots of a mapping table. There is nothing extra to upload.

## Story

A source system provides the current **product-category mapping table of truth**.

On Day 2, product P001 moves from **Laptop** to **Computing**, while P003 appears for the first time.

The same Day 2 snapshot is written using SCD1 and SCD2 so you can see the difference immediately.

## 1. Day 1 mapping snapshot

```python
from datetime import datetime
from fabricops_kit import orchestrate_write

day_1 = spark.createDataFrame([
    ("P001", "Laptop", "Alice", datetime(2026, 10, 6, 9, 0)),
    ("P002", "Monitor", "Bob", datetime(2026, 10, 6, 9, 0)),
], ["product_id", "category", "product_owner", "modified_datetime"])
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
        "tracked_columns": ["category", "product_owner"],
    },
    spark_session=spark,
)
```

## 2. Day 2 mapping snapshot

```python
day_2 = spark.createDataFrame([
    ("P001", "Computing", "Alice", datetime(2026, 10, 7, 9, 0)),
    ("P002", "Monitor", "Carol", datetime(2026, 10, 7, 9, 0)),
    ("P003", "Accessories", "Dan", datetime(2026, 10, 7, 9, 0)),
], ["product_id", "category", "product_owner", "modified_datetime"])
```

Run the same two `orchestrate_write()` calls again, this time using `day_2`.

## What changes?

### SCD1

SCD1 keeps the mapping table as the latest truth.

```text
P001  Computing    Alice  ← category updated
P002  Monitor      Carol  ← owner updated
P003  Accessories  Dan    ← inserted
```

There is still one row per product.

### SCD2

SCD2 keeps the mapping history.

P001 now has two versions because `category` changed:

```text
P001  Laptop     Alice  ← historical
P001  Computing  Alice  ← current
```

P002 also gets a new version because `product_owner` changed from Bob to Carol. P003 is inserted as a new current row.

Inspect `_effective_from`, `_effective_to`, and `_is_current` to see when each mapping was valid.

## The mental model

**SCD1:** keep the latest mapping as the current truth.

**SCD2:** keep the current mapping and preserve previous versions when any tracked column changes.

**Next:** return to [Step 3. Author and freeze the Data Contract](03-author-and-freeze-data-contract.md).
