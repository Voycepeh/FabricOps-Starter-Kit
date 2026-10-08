# Step 2B. Incremental → Append

This optional Guided Demo reuses the **02 Pipeline** notebook from Step 2. You will change a copy, not the original full-refresh notebook.

**Goal:** Read only unconsumed Orders from the Bronze Lakehouse, then append them to a separate Silver Lakehouse target. Run the notebook three times to see the bootstrap, new-row, and no-change cases.

| | Source | Target |
| --- | --- | --- |
| Store | `Bronze` Lakehouse | `Silver` Lakehouse |
| Table | `demo.orders` | `demo.orders_incremental` |
| Processing | Incremental on `modified_datetime` | Append |

The Orders source was created in [Step 00C](00C-prepare-demo-data-with-fabricops-io.md); no new file upload is needed. Keep the original `02_pipeline`, `demo.curated_orders`, and `demo.customer_summary` unchanged.

## 1. Duplicate the notebook in Fabric

1. Open `02_pipeline` in your **Engineering Development** workspace.
2. Make a copy named `02B_incremental_append_demo`.
3. Use the copy for **all** the edits below. Keep the same attached Fabric Environment and the `00_env_config` notebook from Step 2.

## 2. Configure the incremental watermark in the Read

The sample Bronze Orders source already contains `modified_datetime`. Specify that column in the copied notebook's `orchestrate_read()` call using `read_parameters`; you do **not** need to edit the Data Catalogue manually.

FabricOps manages the accepted watermark for each source-to-target relationship, only committing progress after a successful target publication. If a selected or active Data Contract sets a different watermark, FabricOps rejects the mismatch rather than silently overriding it.

See [Read and Load Strategies](../reference/read-and-load-strategies.md) for the state lifecycle.

## 3. Keep the Environment and Data Contract cells

Keep this setup cell:

```python
%run 00_env_config
```

Replace the **import** cell with:

```python
from pyspark.sql import functions as F

from fabricops_kit import (
    orchestrate_read,
    orchestrate_write,
    resolve_table_id,
    widget_select_data_contract,
    read_lakehouse_table,
    write_lakehouse_table,
)
```

Keep the Data Contract selector cell:

```python
CONTRACTS = widget_select_data_contract(spark_session=spark)
```

In Development, you can leave the target without a selected contract. If you select **Validate** for the target, it will not publish; use **Enforce** to exercise the Append write.

## 4. Replace READ 1 — Orders

Keep the existing `sources = {}` initialization once. Replace the **READ 1 — Orders** cell with:

```python
target_table_id = resolve_table_id(
    store="Silver",
    schema="demo",
    table_name="orders_incremental",
)

source = orchestrate_read(
    name="orders",
    store="Bronze",
    schema="demo",
    table_name="orders",
    read_mode="incremental",
    read_parameters={"watermark_column": "modified_datetime"},
    target_table_id=target_table_id,
    spark_session=spark,
)
sources["orders"] = source

print("Scope:", source["scope"])
print("Should process:", source["should_process"])
display(source["dataframe"])
```

**Why resolve the target first?** Incremental progress belongs to one exact **source → target** relationship. Another target consuming Bronze Orders may have a different last-processed watermark.

**Important:** Do not provide custom SQL in `query` for an incremental read; FabricOps builds its own filtering predicate. Leave `query` omitted.

Delete or skip **READ 2 — Products** and **READ 3 — Order History**. Leave the optional Read inspection cell commented out; incremental reads intentionally skip full-table profiling.

## 5. Replace the Transform cell

Replace the existing joins and customer summary aggregation under **3. Transform** with:

```python
# Preserve the Orders schema and its modified_datetime watermark.
transformed_df = sources["orders"]["dataframe"]
display(transformed_df)
```

This deliberately performs no transformation, so you can inspect the exact rows that will be appended.

## 6. Replace WRITE 1 — Lakehouse Curated Orders

Keep `writes = {}` once. Replace **WRITE 1** with:

```python
if sources["orders"]["should_process"]:
    write_result = orchestrate_write(
        transformed_df,
        name="orders_incremental",
        sources=[sources["orders"]],
        store="Silver",
        schema="demo",
        table_name="orders_incremental",
        write_mode="append",
        contracts=CONTRACTS,
        repartition_by=None,
        spark_session=spark,
    )

    writes["orders_incremental"] = write_result
    print("Published:", write_result["published"])
else:
    print("No new Orders to process; skipping append.")
```

Use the same high-level `orchestrate_write()` you used in Step 2, not a separate `pipeline_write()` bypass. The successful write commits the source-to-target incremental progress.

Delete or skip **WRITE 2 — Warehouse Customer Summary**. In the optional Write inspection cell, change `inspect_write` to `"orders_incremental"`, or leave that inspection cell commented out.

## 7. First run: bootstrap

Run your modified notebook **from the top**. For a target with no accepted incremental history:

* `source["scope"]["first_run"]` is `True` and the scope type is `full`.
* The Read returns all existing Bronze Orders.
* `orchestrate_write()` publishes that batch to `Silver.demo.orders_incremental`.

The output from READ 1 should resemble:

```text
Scope: {'type': 'full', 'first_run': True, ...}
Should process: True
```

Verify the target using Fabric's Silver Lakehouse table explorer or this helper in a new code cell:

```python
silver_rows = read_lakehouse_table(
    "orders_incremental",
    store="Silver",
    schema="demo",
    spark_session=spark,
)
print("Silver row count:", silver_rows.count())
display(silver_rows)
```

**Do not re-run Step 00C** between the three tests; it resets the demonstration source baseline.

## 8. Insert two new Orders into Bronze

After a successful first publication, run the following **one-time test cell** in the same notebook. It takes two sample Orders, gives them new IDs, and ensures their `modified_datetime` is later than the current source maximum.

```python
bronze_orders = read_lakehouse_table(
    "orders",
    store="Bronze",
    schema="demo",
    spark_session=spark,
)

# Use deterministic demo IDs; check before inserting to avoid duplicate tests.
test_ids = ["DEMO-INC-001", "DEMO-INC-002"]
assert bronze_orders.where(F.col("order_id").isin(test_ids)).limit(1).count() == 0, (
    "Incremental test Orders already exist. Do not insert them twice."
)

latest_modified = bronze_orders.agg(F.max("modified_datetime").alias("latest")).first()["latest"]
assert latest_modified is not None, "Orders has no modified_datetime baseline."

from datetime import timedelta

demo_rows = bronze_orders.orderBy("order_id").limit(2).collect()
assert len(demo_rows) == 2, "At least two source Orders are required."

new_records = []
for index, row in enumerate(demo_rows, start=1):
    record = row.asDict()
    record["order_id"] = test_ids[index - 1]
    record["modified_datetime"] = latest_modified + timedelta(minutes=index)
    new_records.append(record)

new_orders = spark.createDataFrame(new_records, schema=bronze_orders.schema)

write_lakehouse_table(
    new_orders,
    "orders",
    store="Bronze",
    schema="demo",
    mode="append",
)
print("Inserted two new Bronze Orders.")
display(new_orders)
```

This directly changes the **demo Bronze source**, not the Silver target. Only run it once. Use a dedicated demo environment, not a production Orders table. Since Append records new rows rather than reconciling updates to existing orders, the test uses new `order_id` values.

## 9. Second run: append only new rows

Run the modified pipeline again **from the top**, but **do not execute the one-time test insertion cell again**.

Check that:

1. READ 1 reports `first_run = False` and `type = watermark`.
2. The returned DataFrame contains only `DEMO-INC-001` and `DEMO-INC-002`, assuming no other rows were added.
3. WRITE 1 reports `published = True`.
4. The Silver target now has two additional rows.

The scope uses `modified_datetime > last committed watermark`, not `>=`.

## 10. Third run: no new data

Run the pipeline a third time **without inserting any more Bronze rows**.

The expected result is:

```text
Should process: False
No new Orders to process; skipping append.
```

The Silver row count should remain unchanged. This verifies that the target-specific watermark advanced after successful publication and that the no-change run does not append duplicates.

| Run | Bronze source state | Incremental read | Silver write |
| --- | --- | --- | --- |
| 1 | Original Orders | Bootstrap: all original rows | Append first batch |
| 2 | Original Orders + two test Orders | Only the two new rows | Append two rows |
| 3 | No further changes | No rows to process | Skip write |

!!! warning "Append does not reconcile old Orders"
    If an existing order is updated with a later `modified_datetime`, an Append target adds another version instead of replacing the earlier row. For updates to existing business keys, use SCD1 or SCD2 instead. This optional demo only appends **new orders**.

**Next optional mode:** [Step 2C. SCD Type 1 vs Type 2](02C-build-and-run-scd-etl.md)
