# Detect changed source-table partitions

`observe_table()` cheaply identifies which source table partitions changed before FabricOps performs a more expensive read, profiling run, or deeper change check.

## Observe a configured table

Use the same logical target, schema, and table variables as the pipeline read. The configured `source` target may resolve to either a Warehouse or Lakehouse:

```python
from fabricops_kit import observe_table

SOURCE_TARGET = "source"
SOURCE_SCHEMA = "dbo"
SOURCE_TABLE_NAME = "student_enrolment"

observation = observe_table(
    target=SOURCE_TARGET,
    schema=SOURCE_SCHEMA,
    table_name=SOURCE_TABLE_NAME,
    partition_column="business_date",
    change_column="modified_at",
)
```

For a Lakehouse without schemas, omit the schema while retaining the same logical target:

```python
observation = observe_table(
    table_name=SOURCE_TABLE_NAME,
    target=SOURCE_TARGET,
    partition_column="business_date",
    change_column="modified_at",
)
```

## Understand the evidence

For each partition, FabricOps stores only:

- the partition value
- its row count
- its earliest change value
- its latest change value

A partition requires a follow-up read when it is new, its row count changes, its earliest or latest change value changes, or it reappears after removal. Missing current partitions are reported as removed, and compact tombstones preserve that absence for later comparisons.

Warehouse observation runs `COUNT(*)`, `MIN(change_column)`, and `MAX(change_column)` grouped by the partition column in the Warehouse SQL engine. Spark receives only the aggregate result. Lakehouse observation selects only the partition and change columns before performing the distributed aggregation.

!!! important "Choose a trustworthy change column"
    `change_column` must advance when rows in the partition are inserted or updated. Typical values are `modified_at`, `updated_at`, or `last_changed_at`. Observation is a lightweight signal, not proof that every individual cell is unchanged; a middle value can change while count, minimum, and maximum remain identical. Use deeper change detection when the source does not maintain a reliable change column.

## Place observation before the full read

The source workflow is **observe cheaply → schema, freshness, and change checks → full source read → row-level data-quality checks → profile/register**. `observe_table()` produces evidence; it is not itself a guardrail. Its `MIN(change_column)` and `MAX(change_column)` evidence can support freshness and change decisions without a second source scan.

The current standalone `check_schema()`, `check_freshness()`, and `check_changes()` callables still accept DataFrames or row-like observations. Connecting all three directly to stored table-observation evidence requires a separate focused consolidation; this PR does not broaden their contracts. Row-level null, value, domain, and uniqueness checks remain after the full read.

## Plan the restricted follow-up read

The result preserves `first_observation`, `new_partitions`, `changed_partitions`, `removed_partitions`, `requires_read`, and a restricted `read_predicate`. Use that plan to avoid an expensive source read when no likely change exists, or to restrict deeper processing to affected partitions.

`observe_table()` never mutates the source. It appends compact observation history to FabricOps-owned metadata routed through the metadata target configured by `00_env_config`.

## Next step

Review the [`observe_table()` API](../api/reference/observe_table.md), then use [`check_changes()`](../reference/index.md) when an affected slice needs deeper DataFrame-level comparison.
