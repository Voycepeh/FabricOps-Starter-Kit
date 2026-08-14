# Check source-table changes before a full read

`observe_table()` collects and persists compact source facts; the guardrail checks make the judgements.

## Run the pre-read flow

Use the same logical target, schema, and table identity as the eventual pipeline read:

```python
from fabricops_kit import check_changes, check_freshness, check_schema, observe_table

observation_df = observe_table(
    target=SOURCE_TARGET,
    schema=SOURCE_SCHEMA,
    table_name=SOURCE_TABLE_NAME,
    partition_column="business_date",
    change_column="modified_at",
)
metadata_table_key = observation_df.select("metadata_table_key").first()[0]

schema_result = check_schema(
    target=SOURCE_TARGET,
    schema=SOURCE_SCHEMA,
    table_name=SOURCE_TABLE_NAME,
    rules_df=guardrail_rules_df,
    metadata_table_key=metadata_table_key,
)
freshness_result = check_freshness(
    observation_df,
    rules_df=guardrail_rules_df,
    metadata_table_key=metadata_table_key,
)
changes_result = check_changes(
    observation_df,
    rules_df=guardrail_rules_df,
    metadata_table_key=metadata_table_key,
)
```

## Keep evidence and judgement separate

| Stage | Responsibility | Metadata ownership |
| --- | --- | --- |
| `observe_table()` | Aggregate `COUNT`, `MIN`, and `MAX`; persist and return the canonical observation DataFrame. | `METADATA_SOURCE_OBSERVATION` observed facts |
| `check_schema()` | Inspect and judge the physical schema without a full business-row read. | `METADATA_GUARDRAIL` approved rule; `METADATA_GUARDRAIL_RESULTS` judgement |
| `check_freshness(observation_df)` | Judge the observation-wide latest `max_change_value`. | Rule and judgement metadata |
| `check_changes(observation_df)` | Load the previous comparable snapshot, compare partitions, and append removal tombstones. | Observation tombstones and guardrail judgement |

Warehouse observation pushes grouped `COUNT_BIG`, `MIN(change_column)`, and `MAX(change_column)` into the Warehouse SQL engine. Lakehouse observation projects only the partition and change columns before its distributed aggregation.

!!! important "Observation does not judge"
    A successfully collected snapshot is persisted even when a later check fails. `observe_table()` does not load history, classify partitions, decide whether a read is required, or construct a physical read predicate.

A first comparison establishes a baseline. Later comparisons classify a partition as new, changed, removed, or reappeared. Removed partitions are represented by `is_present=false` tombstones written by `check_changes()`; affected partition values remain structured evidence, and the future physical read layer owns predicate construction.

!!! warning "Recreate old Preview metadata tables"
    Existing Preview `METADATA_SOURCE_OBSERVATION` tables created with the old fingerprint-based schema are incompatible. Recreate them through the normal FabricOps metadata/bootstrap setup; no migration or compatibility shim is provided.

## Continue only after cheap checks pass

After all three results allow continuation, perform the full source read, run row-level DQ, and call `profile_and_register_table()`. The observation and catalogue use the same authoritative `metadata_table_key`, so the evidence remains linked to the profiled physical table identity.

## Next step

Review the [`observe_table()` API](../api/reference/observe_table.md) and the generated references for `check_schema`, `check_freshness`, and `check_changes`.
