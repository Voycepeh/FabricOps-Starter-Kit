# Step 2: Run the v0.2 pipeline

Use `02_pipeline` for one clear, governed pipeline sequence:

```text
run environment configuration
→ read and profile source tables
→ apply source guardrails
→ transform the data
→ apply target guardrails
→ write, read, and profile target tables
→ view the resulting data contract
```

The notebook is optimized for Lakehouse-to-Lakehouse movement with PySpark so processing can use distributed and parallel execution. Complete Warehouse table reads, complete-table Warehouse SQL reads, and Warehouse targets remain supported alternatives.

## Resolve and reuse physical table identity

Run `00_env_config` first. For every source or target, define the configured target, schema, and table name once, then reuse those variables for reading or writing and profiling. `profile_and_register_table()` resolves the active environment, configured store type, and normalized target layer internally. The complete physical identity remains `environment_name + store_type + layer + schema_name + table_name`.

### Lakehouse source

```python
SOURCE_TARGET = "unified"
SOURCE_SCHEMA = UNIFIED_SCHEMA
SOURCE_TABLE_NAME = "smoke_test_source_df"

source_df = read_lakehouse_table(
    target=SOURCE_TARGET,
    schema=SOURCE_SCHEMA,
    table_name=SOURCE_TABLE_NAME,
    spark_session=spark,
)

source_profile_df = profile_and_register_table(
    source_df,
    profile_role="source",
    target=SOURCE_TARGET,
    schema=SOURCE_SCHEMA,
    table_name=SOURCE_TABLE_NAME,
)
```

A complete Warehouse source can use `read_warehouse_table()` with the same profiling call. `read_warehouse_query()` is also supported when `SELECT * FROM schema.table` genuinely returns the complete physical table. A filtered, joined, sampled, or aggregated query result must not be registered as the complete profile of a single physical source table.

## Guardrails and transformation

Source and target guardrail execution is planned for v0.3.0. The v0.2 notebook reserves clear stages for those checks without introducing placeholder APIs. Put user-defined PySpark transformation logic between those stages.

## Lakehouse target

Write the transformed DataFrame first, read the persisted target, and only then profile and register that physical table:

```python
TARGET_TARGET = "unified"
TARGET_SCHEMA = UNIFIED_SCHEMA
TARGET_TABLE_NAME = "smoke_test_target_df"

write_lakehouse_table(
    transformed_df,
    target=TARGET_TARGET,
    schema=TARGET_SCHEMA,
    table_name=TARGET_TABLE_NAME,
)

target_df = read_lakehouse_table(
    target=TARGET_TARGET,
    schema=TARGET_SCHEMA,
    table_name=TARGET_TABLE_NAME,
    spark_session=spark,
)

target_profile_df = profile_and_register_table(
    target_df,
    profile_role="target",
    target=TARGET_TARGET,
    schema=TARGET_SCHEMA,
    table_name=TARGET_TABLE_NAME,
)
```

The notebook also provides an optional Warehouse target using `write_warehouse_table()`, followed by `read_warehouse_table()` and the identical `profile_and_register_table()` call.

## Resulting evidence

Each successful profile registration appends observed statistical evidence to `METADATA_DATA_PROFILED`, upserts the canonical table and column identities in `METADATA_DATA_CATALOGUE`, and records source or target participation in `METADATA_DATA_LINEAGE`. All metadata writes continue to use the metadata Lakehouse configured by `00_env_config`, not the business source or target store.

Finish the notebook with `widget_view_data_contract(spark_session=spark)` to review the registered source and target evidence.
