# Source change detection and incremental reads

Use a compact source observation to decide whether an expensive business-data read is necessary and, when possible, restrict that read to the partitions that need attention.

!!! important "Observation makes the decision cheaper"

    `observe_source()` is not meant to replace reading the source. It is meant to make the decision to perform the expensive read much cheaper.

```text
Source
  ↓
observe_source()
  ↓
Compare with METADATA_SOURCE_OBSERVATION
  ↓
No change ───────────────→ Skip the business-data read
  ↓
Changed or new partition → Restricted source read
  ↓
check_changes() when deeper comparison is needed
  ↓
Continue pipeline
```

## Decide whether this pattern fits

**Source observation is most useful when repeated full reads cost much more than a compact aggregate.**

| Use this when | Be careful when |
| --- | --- |
| The source is large. | The table has no useful partition column. |
| Pipelines run repeatedly. | Every observation still scans the entire source. |
| Most partitions normally do not change. | Fingerprint columns are volatile and mark most partitions as changed. |
| The follow-up read can filter by date, batch, or partition. | The partition predicate changes between runs. |
| Full source reads are expensive. | The table is small enough that a normal read is already cheap. |

For an unpartitioned table, or one whose aggregation must scan nearly every row on every run, observation can still reduce data transferred to Spark but may not reduce work in the source engine. Measure both source-engine work and Spark transfer before adopting the pattern.

## Understand the lightweight observation

**FabricOps stores compact evidence, not a copy of the business dataset.**

For each observed partition, the evidence includes:

- source identity and an observation-definition identity
- partition value and whether that partition is currently present
- row count
- observed minimum and maximum for the configured range column
- a deterministic compact fingerprint
- observation time and standard FabricOps audit fields

The history belongs to FabricOps and is appended to `METADATA_SOURCE_OBSERVATION` in the configured metadata Lakehouse. FabricOps does not write fingerprints or state back to the source Warehouse or Lakehouse.

The `observation_definition_id` separates histories produced with different partition columns, range columns, fingerprint columns, or partition predicates. Changing any of those settings begins a distinct comparison history instead of comparing incompatible evidence.

!!! note "A fingerprint is a first-tier signal"

    The compact aggregate is designed to identify partitions that may need attention. It is not a collision-proof row-level change record. Use [`check_changes()`](../reference/index.md) on the affected data when the pipeline needs inserted, updated, or deleted row classification.

## Warehouse pattern: aggregate before Spark

**Warehouse observation pushes grouping and aggregate work into the SQL serving engine.**

FabricOps uses the existing read-only [`read_warehouse_query()`](../api/reference/read_warehouse_query.md) connectivity path rather than creating another Warehouse connector. The generated observation query follows this shape:

```sql
SELECT
    business_date,
    COUNT_BIG(*) AS row_count,
    MIN(order_id) AS observed_min,
    MAX(order_id) AS observed_max,
    CHECKSUM_AGG(BINARY_CHECKSUM(order_id, modified_at)) AS aggregate_checksum
FROM dbo.orders
GROUP BY business_date
```

Only the grouped observation rows reach Spark. A subsequent business-data read can use the returned `read_predicate` in a filtered Warehouse query so unchanged partitions are not transferred.

This is cheap when the Warehouse can aggregate efficiently and the result has far fewer rows than the source. It can still be expensive when the query scans a very large unpartitioned table, the predicate cannot prune data, or almost every partition changes on every run.

## Lakehouse pattern: keep aggregation distributed

**Lakehouse observation reads only the columns required to build evidence.**

The Lakehouse path uses the existing configured table resolution and Delta reader, then applies:

1. projection of the partition, range, and fingerprint columns
2. the configured partition predicate, when supplied
3. distributed grouping and aggregation in Spark
4. collection of only the compact per-partition result

Choose a predicate that Spark and Delta can use for partition pruning. A string filter does not guarantee pruning by itself; its columns and values must align with the table's physical partition layout.

## Choose observation columns deliberately

### Partition column

**Choose a stable column that also supports the restricted follow-up read.**

Good starting points include a business date, ingestion date, batch identifier, or another bounded source partition. Partitions should be large enough to avoid excessive metadata rows but small enough that rereading one changed partition is materially cheaper than reading the whole source.

The Preview API requires exactly one partition column. This keeps partition identity unambiguous and ensures changed and new partitions can produce a usable SQL predicate. If a source needs a composite partition, derive a single stable partition key upstream or use a normal source read until composite planning is supported.

### Range column

**Use a sortable value whose minimum and maximum provide useful boundary evidence.**

An increasing numeric ID, event timestamp, or source sequence is usually useful. Avoid a range column whose minimum and maximum remain meaningless or unstable for the way data arrives.

### Fingerprint columns

**Use the smallest set of columns that reliably signals a meaningful source change.**

Common choices include a stable key plus a source modification timestamp or a small set of business-state columns. Too few columns can miss relevant changes; too many volatile or wide columns can make every run look changed and increase source aggregation cost.

Changing the fingerprint column list changes the observation definition. The next run is therefore treated as the first observation under that new definition.

## Example: daily incremental Warehouse flow

**Observe first, then apply the returned predicate to the expensive read.**

```python
from fabricops_kit import observe_source, read_warehouse_query

plan = observe_source(
    {
        "source_type": "warehouse",
        "target": "warehouse",
        "schema": "dbo",
        "table_name": "orders",
    },
    partition_columns=["business_date"],
    range_column="order_id",
    fingerprint_columns=["order_id", "modified_at"],
    config=CONFIG,
    env=ENV,
)

if not plan["requires_read"]:
    source_df = None
elif plan["read_predicate"]:
    source_df = read_warehouse_query(
        f"""
        SELECT order_id, business_date, modified_at, status
        FROM dbo.orders
        WHERE {plan['read_predicate']}
        """,
        target="warehouse",
    )
```

On the first observation, all observed partitions are new and `requires_read` is `True`. On an identical later observation, it is `False`. Changed and new partitions appear in `read_predicate`; unchanged historical partitions do not.

If deeper row evidence is required, compare the restricted result with the corresponding previously loaded data:

```python
from fabricops_kit.pipeline import check_changes

change_result = check_changes(
    source_df,
    previous_df,
    key_columns=["order_id"],
    partition_columns=["business_date"],
)
```

`observe_source()` decides whether and where to read. `check_changes()` classifies changes in DataFrames that are already available. Neither function decides target merge or write policy.

## Handle edge cases explicitly

| Situation | FabricOps behavior or pipeline action |
| --- | --- |
| First observation | Marks observed partitions as new, persists compact evidence, and requires a read without manufacturing historical row classifications. |
| Removed partition | Returns it in `removed_partitions`, requires pipeline attention, and stores an absence tombstone. There are no source rows to include in `read_predicate`; deletion or reconciliation policy belongs to the pipeline. |
| Partition later reappears | Detects the change by comparing it with the stored absence tombstone. |
| Observation definition changes | Uses a new `observation_definition_id`; old evidence is not mixed with the new definition. |
| Metadata history table is absent | Treats the run as a first observation. |
| Metadata read fails for another reason | Raises an error rather than silently resetting source history. |
| Huge source has no useful partition | The aggregate may remain expensive; benchmark against a normal read or redesign the source layout. |
| Fingerprint definition is weak | Relevant changes may not trigger a deeper read; include stable columns that reflect meaningful source state. |

!!! warning "Removed partitions need separate handling"

    `read_predicate` identifies source rows that still exist. A removed partition has no source rows to fetch, so use `removed_partitions` to trigger the pipeline's reconciliation, rebuild, warning, or stop policy.

## Expected result

Repeated pipelines can skip unchanged business-data reads, transfer only changed or new partitions when a read is required, and retain compact comparison history without modifying the external source.

## Next

Review the [`observe_source()` API](../api/reference/observe_source.md), then use [`check_changes()`](../reference/index.md) when an affected slice needs deeper DataFrame-level comparison. For schema and freshness checks around the same pipeline, see [Validate a data source before ETL](validate-a-data-source-before-etl.md).
