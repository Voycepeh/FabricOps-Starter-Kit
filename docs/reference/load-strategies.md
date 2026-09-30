# Load Strategies

FabricOps supports four governed target Load Strategies through `orchestrate_write()` and `pipeline_write()`: **Overwrite, Append, SCD1, and SCD2**. Each target chooses its strategy independently.

| Load Strategy | Setting | Runtime behaviour | Key configuration |
| --- | --- | --- | --- |
| **Overwrite** | `load_strategy="overwrite"` | Replaces the governed target state, or governed Lakehouse partitions when a partition column is configured. | Optional `partition_column` |
| **Append** | `load_strategy="append"` | Adds the prepared batch to the existing target. | No business key required |
| **SCD1** | `load_strategy="scd1"` | Updates matching business keys in place and inserts new keys. | `key_columns` required |
| **SCD2** | `load_strategy="scd2"` | Preserves historical versions and maintains the current version as governed values change. | `key_columns` and `effective_column` required; `tracked_columns` optional |

The applicable Data Contract is authoritative. Development can propose processing settings, while selected/frozen contract validation governs Development and the active approved contract governs Production.

## Overwrite

Whole-table Overwrite publishes the prepared DataFrame as the complete target state.

When a governed `partition_column` is configured for a Lakehouse target, FabricOps performs partition-scoped overwrite instead. It derives the affected partition values and uses the governed scope to replace only those partitions, including removal of stale partitions when the incremental observation reports that a source partition disappeared.

A partial Incremental input cannot use whole-table Overwrite. FabricOps rejects that combination because replacing a complete target with a partial source scope would lose unaffected data.

## Append

Append adds the prepared rows to the existing target.

It is naturally suited to immutable/new-event batches, but reruns require care because repeatedly appending the same logical rows can duplicate them. FabricOps uses activity metadata to make same-activity retries safe when a row-producing publication has already succeeded.

For the first Incremental → Append run, no committed baseline means the Read side bootstraps with the complete source. FabricOps permits that bootstrap only when the target is new or empty; a populated target without a committed source-to-target baseline is rejected rather than silently duplicating the full source.

## SCD1

SCD1 requires `key_columns`.

Rows with an existing governed business key are updated to the latest prepared values; new keys are inserted. It is the keyed, idempotent choice when only the current state should remain visible and history is not required.

## SCD2

SCD2 requires `key_columns` and an `effective_column`. `tracked_columns` can optionally define which business attributes drive version changes.

FabricOps maintains technical history fields:

- `_effective_from`
- `_effective_to`
- `_is_current`

Changed business records close their previous current version and insert a replacement current version. Lakehouse SCD2 applies the history mutation through one Delta merge path; Warehouse SCD2 uses its governed SQL transaction path.

## Read mode and Load Strategy are different controls

The Read mode answers **how much source data should this run process?**

The Load Strategy answers **how should the prepared result change the target?**

That separation allows combinations such as:

| Pattern | Use |
| --- | --- |
| Full → Overwrite | Complete rebuild |
| Incremental → Append | New immutable rows |
| Full or Incremental → SCD1 | Current-state keyed merge |
| Full or Incremental → SCD2 | Keyed history maintenance |
| Incremental → partition-scoped Overwrite | Rebuild only affected Lakehouse partitions |

See [Read Modes](read-modes.md) for bootstrap, watermark/partition scope, and source-to-target progress semantics.

## Contract and metadata lifecycle

The resolved Load Strategy and its parameters are persisted on the table-level Data Catalogue record. The selected or active Data Contract remains authoritative for governed processing.

Only after physical publication and Catalogue persistence succeed does FabricOps commit target Lineage and accepted Source Observation/write-success metadata. This keeps incremental progress aligned with successfully published target state.

## Multiple targets

Each `orchestrate_write()` publishes independently. Multiple Write blocks in one notebook are not one atomic transaction. If an earlier target succeeds and a later target fails, the earlier publication remains successful.

## Related documentation

- [Plug-and-Play Data Pipelines with Data Contract Enforcement](../solutions/plug-and-play-data-pipelines.md)
- [Read Modes](read-modes.md)
- [`orchestrate_write()`](../api/reference/orchestrate_write.md)
- [`pipeline_write()`](../api/reference/pipeline_write.md)
- [Guided Demo: Full Read Pipeline](../guided-demo/02-build-and-run-etl.md)
