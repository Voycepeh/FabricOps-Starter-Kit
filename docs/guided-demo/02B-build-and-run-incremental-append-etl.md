# Step 2B. Incremental → Append

This is an **optional processing-mode demo**. Keep the main `02_pipeline` and Step 2 Guided Demo unchanged.

Use the Orders table prepared in 0C. No additional file upload is required.

## Story

New orders arrive after the first successful load. FabricOps should read only the unconsumed Orders rows and append them to a separate target.

## Before you run it

Copy `02_pipeline` in Fabric and name the copy something like `02B_incremental_append_demo`.

For the Orders source, the governed processing definition must use:

```text
watermark_column = modified_datetime
```

Incremental progress is source → target specific, so resolve the new target before the Read.

## Change only the scenario

Use a separate target such as `demo.orders_incremental`.

```python
target_table_id = resolve_table_id(
    store="Silver",
    schema="demo",
    table_name="orders_incremental",
)

orders = orchestrate_read(
    name="orders",
    store="Bronze",
    schema="demo",
    table_name="orders",
    read_mode="incremental",
    target_table_id=target_table_id,
    spark_session=spark,
)
```

Publish the returned scope with Append:

```python
if orders["should_process"]:
    result = pipeline_write(
        orders["dataframe"],
        store="Silver",
        schema="demo",
        table_name="orders_incremental",
        load_strategy="append",
        source_table_ids=[orders["table_id"]],
        spark_session=spark,
    )
```

## Validate it

1. First run: the missing baseline bootstraps from the available Orders source.
2. Add a few new Orders rows with later `modified_datetime` values.
3. Run again: only those new rows should be returned and appended.
4. Run once more without adding data: `should_process` should be false.

The original `02_pipeline` and its targets remain untouched.

**Next optional mode:** [Step 2C. SCD Type 1 vs Type 2](02C-build-and-run-scd1-etl.md)
