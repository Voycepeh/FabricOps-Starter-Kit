# Step 2C. SCD Type 1 vs Type 2

This is an **optional processing-mode demo** using three tiny inline snapshots of a simple food product table. There is nothing extra to upload.

## Story

A source system sends the current **food product table of truth** each day.

The question is simple: for the same `product_id`, did any tracked value such as `category` or `price` change?

If nothing changed, both SCD1 and SCD2 keep the same business state. If something changed, SCD1 replaces the old state while SCD2 preserves the old version and starts a new one.

## 1. Day 1 product snapshot

```python
from datetime import datetime
from fabricops_kit import orchestrate_write

day_1 = spark.createDataFrame([
    ("P001", "Snack", 2.50, datetime(2026, 10, 6, 9, 0)),
    ("P002", "Drink", 1.80, datetime(2026, 10, 6, 9, 0)),
    ("P003", "Fruit", 1.20, datetime(2026, 10, 6, 9, 0)),
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

On Day 2, P001 is unchanged, P002 changes price, and P004 is new.

```python
day_2 = spark.createDataFrame([
    ("P001", "Snack", 2.50, datetime(2026, 10, 7, 9, 0)),
    ("P002", "Drink", 2.00, datetime(2026, 10, 7, 9, 0)),
    ("P003", "Fruit", 1.20, datetime(2026, 10, 7, 9, 0)),
    ("P004", "Snack", 3.20, datetime(2026, 10, 7, 9, 0)),
], ["product_id", "category", "price", "modified_datetime"])
```

Run the same two `orchestrate_write()` calls again using `day_2`.

### What happens to P001?

Day 1 and Day 2 both contain:

```text
P001  Snack  2.50
```

Nothing tracked changed.

**SCD1** still has one row:

```text
P001  Snack  2.50
```

**SCD2** also still has one version:

```text
P001  Snack  2.50  Day 1 → current
```

It does **not** create another history row just because another daily snapshot arrived. The newer `modified_datetime` is not a tracked business attribute; only `category` and `price` are compared for SCD2 change detection.

P002 is different: its price changed from 1.80 to 2.00, so SCD1 updates the row and SCD2 creates a new version. P004 is inserted as a new product in both targets.

## 3. Day 3 product snapshot

Now P001 changes category from **Snack** to **Healthy Snack**.

```python
day_3 = spark.createDataFrame([
    ("P001", "Healthy Snack", 2.50, datetime(2026, 10, 8, 9, 0)),
    ("P002", "Drink", 2.00, datetime(2026, 10, 8, 9, 0)),
    ("P003", "Fruit", 1.20, datetime(2026, 10, 8, 9, 0)),
    ("P004", "Snack", 3.20, datetime(2026, 10, 8, 9, 0)),
], ["product_id", "category", "price", "modified_datetime"])
```

Run the same two `orchestrate_write()` calls again using `day_3`.

### SCD1 after Day 3

SCD1 keeps only the latest truth:

```text
P001  Healthy Snack  2.50
```

The old `P001 | Snack | 2.50` state is replaced.

### SCD2 after Day 3

SCD2 preserves both versions:

```text
P001  Snack          2.50  Day 1 → Day 3  historical
P001  Healthy Snack  2.50  Day 3 → current
```

Day 2 did not create another P001 version because nothing tracked changed that day.

## The comparison is simple

1. Match the incoming row to the current row by `product_id`.
2. Compare the tracked columns, here `category` and `price`.
3. If none of those values changed, keep the current business state.
4. If any tracked value changed:
   - **SCD1** replaces the existing row.
   - **SCD2** closes the existing version and inserts a new current version.

So SCD tracking is **not limited to one column**. Any configured tracked column can trigger a change.

> **Note:** seeing P001 unchanged on Day 1 and Day 2 is not a duplicate-key problem. It is the same business key arriving again in a later snapshot. Two P001 rows inside the **same** snapshot would be a different issue and should normally be rejected or resolved before the SCD write.

## The mental model

**SCD1:** “What is true now?”

**SCD2:** “What was true, when was it true, and what is true now?”

**Next:** return to [Step 3. Author and freeze the Data Contract](03-author-and-freeze-data-contract.md).
