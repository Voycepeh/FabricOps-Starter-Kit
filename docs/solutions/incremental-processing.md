# Incremental processing

Use observed source changes to limit recurring ETL work while keeping the target's maintenance semantics explicit.

```text
observe_table()
→ check_schema() → check_freshness() → check_changes()
→ plan_incremental_processing()
→ scoped read → transformation → validation
→ write_incremental_lakehouse_table()
```

## Problem

**Large recurring pipelines should not reread and rewrite every row when only a small source scope changed.** They also need a safe first run and predictable behavior when an existing source partition changes, reappears, or disappears.

## How FabricOps solves it

**Detection, planning, reading, transformation, and writing remain separate steps.** [`observe_table()`](../api/reference/observe_table.md) records compact evidence. [`check_changes()`](../api/reference/check_changes.md) compares observations and applies the Change Guardrail; it never reads business rows or chooses a target operation.

[`plan_incremental_processing()`](../api/reference/plan_incremental_processing.md) combines that structured result with explicit target configuration. The notebook then performs a normal lazy [`read_lakehouse_table()`](../api/reference/read_lakehouse_table.md) and, for an incremental plan, filters the partition column with `where(...isin(...))`. Transformation and DQ remain visible before [`write_incremental_lakehouse_table()`](../api/reference/write_incremental_lakehouse_table.md) applies the plan.

| Target strategy | Intended target | Changed-source action |
| --- | --- | --- |
| **Overwrite** | Current-state or full-refresh table | Overwrite affected partitions when an explicit compatible target partition is configured; otherwise reread and overwrite the full target. |
| **Append** | Immutable fact or event table | Append new partitions only. Reject changed, reappeared, or removed partitions rather than duplicate data. |
| **Merge / SCD Type 1** | Current-state upsert table | Merge affected rows by explicit business keys: update matches and insert new keys. |
| **SCD Type 2** | History-preserving dimension | Expire changed current rows and add new current versions using `valid_from`, `valid_to`, and `is_current`. |

## Keep source behavior and target maintenance separate

**`source_pattern` describes the source; `write_strategy` describes the target.** An append-only source can feed a merge target, for example. The Change Guardrail judges whether observed behavior fits its declared source pattern, while the processing plan independently selects target maintenance.

!!! important "Safe boundaries"

    The first observation creates a baseline and uses a full read. An unchanged source skips processing. Removed source partitions never imply automatic target deletion: overwrite falls back to an explicit full refresh, while append, merge, and SCD2 fail until a safe deletion policy is designed.

## Notebook pattern

Configure the target near its identity, then inspect the returned plain dictionary before reading rows:

```python
processing_plan = plan_incremental_processing(
    changes_result,
    "merge",
    key_columns=["order_id"],
)

if processing_plan["read_strategy"] != "skip":
    source_df = read_lakehouse_table("orders", target="source", schema="dbo")
    if processing_plan["read_strategy"] == "incremental":
        source_df = source_df.where(
            F.col(processing_plan["partition_column"]).isin(processing_plan["partition_values"])
        )
    transformed_df = source_df.select("*")
    write_incremental_lakehouse_table(transformed_df, "orders_current", processing_plan, target="curated")
```

## Next

Start with the complete [`02_pipeline` notebook template](../notebook-templates.md), then choose the target strategy that matches the target's business purpose.
