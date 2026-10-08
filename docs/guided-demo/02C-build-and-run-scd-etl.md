# Step 2C. SCD Type 1 vs Type 2

This optional Guided Demo reuses the **02 Pipeline** notebook from Step 2. You will change a copy, not the original full-refresh notebook.

**Goal:** Send the same three product snapshots to two separate Silver targets so you can see the difference between SCD1 and SCD2.

| | SCD1 target | SCD2 target |
| --- | --- | --- |
| Store | `Silver` Lakehouse | `Silver` Lakehouse |
| Table | `demo.product_mapping_scd1` | `demo.product_mapping_scd2` |
| Business key | `product_id` | `product_id` |
| Change tracking | Keep latest row | Preserve history when `category` or `price` changes |
| Effective time | Not required | `modified_datetime` |

There is nothing extra to upload. The demo creates three tiny product snapshots directly in the copied notebook.

## 1. Duplicate the notebook in Fabric

1. Open `02_pipeline` in your **Engineering Development** workspace.
2. Make a copy named `02C_scd_demo`.
3. Use the copy for all the edits below.
4. Keep the same attached Fabric Environment and the `00_env_config` notebook from Step 2.

The original `02_pipeline`, `demo.curated_orders`, and `demo.customer_summary` remain unchanged.

## 2. Keep the Environment and Data Contract cells

Keep this setup cell:

```python
%run 00_env_config
```

Replace the import cell with:

```python
from datetime import datetime

from fabricops_kit import (
    orchestrate_write,
    read_lakehouse_table,
    widget_select_data_contract,
)
```

Keep the Data Contract selector:

```python
CONTRACTS = widget_select_data_contract(spark_session=spark)
```

For this optional processing-mode demo, leave both new targets without a selected contract unless you have intentionally authored contracts for them. If a target is selected in **Validate** mode, FabricOps validates but does not publish it; use **Enforce** when you want the SCD write to occur.

## 3. Replace the Read and Transform sections with Day 1

Delete or skip the three original Read blocks and the Step 2 transformation. This demo uses a tiny inline product snapshot so the SCD behavior is easy to inspect.

In the **Transform** section, create Day 1:

```python
day_1 = spark.createDataFrame([
    ("P001", "Snack", 2.50, datetime(2026, 10, 6, 9, 0)),
    ("P002", "Drink", 1.80, datetime(2026, 10, 6, 9, 0)),
    ("P003", "Fruit", 1.20, datetime(2026, 10, 6, 9, 0)),
], ["product_id", "category", "price", "modified_datetime"])

display(day_1)
```

This is the starting business state for both targets.

## 4. Replace WRITE 1 with the SCD1 target

Keep `writes = {}` once.

Replace **WRITE 1** with:

```python
scd1_result = orchestrate_write(
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
    contracts=CONTRACTS,
    repartition_by=None,
    spark_session=spark,
)

writes["product_mapping_scd1"] = scd1_result
```

For SCD1, `product_id` identifies the business row. When that product arrives again, the target keeps the latest row for that key.

## 5. Replace WRITE 2 with the SCD2 target

Replace **WRITE 2** with:

```python
scd2_result = orchestrate_write(
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
    contracts=CONTRACTS,
    repartition_by=None,
    spark_session=spark,
)

writes["product_mapping_scd2"] = scd2_result
```

For SCD2:

* `product_id` identifies the business entity.
* `category` and `price` are the tracked business attributes.
* `modified_datetime` tells FabricOps when a new version becomes effective.
* FabricOps maintains `_effective_from`, `_effective_to`, and `_is_current`.

A newer `modified_datetime` by itself does **not** create history when the tracked business values are unchanged.

## 6. First run: create both targets

Run the copied notebook from the top through both Write cells.

Verify the targets:

```python
scd1 = read_lakehouse_table(
    "product_mapping_scd1",
    store="Silver",
    schema="demo",
    spark_session=spark,
)

scd2 = read_lakehouse_table(
    "product_mapping_scd2",
    store="Silver",
    schema="demo",
    spark_session=spark,
)

print("SCD1 rows:", scd1.count())
print("SCD2 rows:", scd2.count())

display(scd1.orderBy("product_id"))
display(scd2.orderBy("product_id", "_effective_from"))
```

Expected row counts after Day 1:

| Target | Rows | Meaning |
| --- | ---: | --- |
| SCD1 | 3 | One current row per product |
| SCD2 | 3 | One current version per product |

## 7. Second run: one change and one new product

Replace only the `day_1` DataFrame cell with:

```python
day_2 = spark.createDataFrame([
    ("P001", "Snack", 2.50, datetime(2026, 10, 7, 9, 0)),
    ("P002", "Drink", 2.00, datetime(2026, 10, 7, 9, 0)),
    ("P003", "Fruit", 1.20, datetime(2026, 10, 7, 9, 0)),
    ("P004", "Snack", 3.20, datetime(2026, 10, 7, 9, 0)),
], ["product_id", "category", "price", "modified_datetime"])

display(day_2)
```

Then change the first argument of both `orchestrate_write()` calls from `day_1` to `day_2` and run the two Write cells again.

Day 2 contains three cases:

* `P001` is unchanged.
* `P002` changes price from `1.80` to `2.00`.
* `P004` is new.

Expected result:

| Product | SCD1 | SCD2 |
| --- | --- | --- |
| P001 | Still one current row | Still one version; no tracked value changed |
| P002 | Existing row updated to price `2.00` | Old version closed and new current version inserted |
| P004 | New row inserted | New current version inserted |

Expected total rows:

| Target | Rows after Day 2 |
| --- | ---: |
| SCD1 | 4 |
| SCD2 | 5 |

Re-run the verification cell from Step 6 to inspect the physical targets.

## 8. Third run: change another tracked column

Replace the snapshot cell with:

```python
day_3 = spark.createDataFrame([
    ("P001", "Healthy Snack", 2.50, datetime(2026, 10, 8, 9, 0)),
    ("P002", "Drink", 2.00, datetime(2026, 10, 8, 9, 0)),
    ("P003", "Fruit", 1.20, datetime(2026, 10, 8, 9, 0)),
    ("P004", "Snack", 3.20, datetime(2026, 10, 8, 9, 0)),
], ["product_id", "category", "price", "modified_datetime"])

display(day_3)
```

Change the first argument of both Write calls to `day_3`, then run them again.

Now `P001` changes `category` from **Snack** to **Healthy Snack**.

Expected SCD1 state for P001:

```text
P001  Healthy Snack  2.50
```

The previous `P001 | Snack | 2.50` row is replaced.

Expected SCD2 history for P001:

```text
P001  Snack          2.50  historical
P001  Healthy Snack  2.50  current
```

Day 2 did not create another P001 history row because neither `category` nor `price` changed.

Expected total rows after Day 3:

| Target | Rows |
| --- | ---: |
| SCD1 | 4 |
| SCD2 | 6 |

## 9. Inspect the exact SCD2 history

Run:

```python
scd2 = read_lakehouse_table(
    "product_mapping_scd2",
    store="Silver",
    schema="demo",
    spark_session=spark,
)

display(
    scd2.select(
        "product_id",
        "category",
        "price",
        "modified_datetime",
        "_effective_from",
        "_effective_to",
        "_is_current",
    ).orderBy("product_id", "_effective_from")
)
```

You should see:

* one current row for every product,
* an additional historical P002 row because its price changed on Day 2,
* an additional historical P001 row because its category changed on Day 3.

## The comparison is simple

For every incoming row:

1. Match it to the current target row using `product_id`.
2. Compare the governed business values.
3. If the values did not change, keep the same business state.
4. If a value changed:
   * **SCD1** replaces the existing row.
   * **SCD2** closes the current version and inserts a new current version.

So SCD tracking is not limited to one column. In this demo, either `category` **or** `price` can cause a new SCD2 version.

!!! note "Repeated snapshots are not duplicate business keys"
    P001 appearing on Day 1, Day 2, and Day 3 is the same business key arriving in separate snapshots. Two P001 rows inside the **same** incoming snapshot are a different data-quality problem and should normally be rejected or resolved before the SCD write.

## The mental model

**SCD1:** “What is true now?”

**SCD2:** “What was true, when was it true, and what is true now?”

**Next:** return to [Step 3. Author and freeze the Data Contract](03-author-and-freeze-data-contract.md).
