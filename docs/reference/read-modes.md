# Read Modes

FabricOps exposes two governed source Read modes through `orchestrate_read()` and `pipeline_read()`: **Full** and **Incremental**. The choice is made independently for each source table.

| Read mode | Setting | Runtime behaviour |
| --- | --- | --- |
| **Full** | `read_mode="full"` | Reads the complete governed source. |
| **Incremental** | `read_mode="incremental"` | Resolves work not yet committed for the exact source-to-target relationship and reads only that scope. |

## Full

Full is the default. FabricOps resolves the source `table_id`, physical Fabric Store and Lakehouse/Warehouse reader, then returns the complete source DataFrame.

A Full read does not need `target_table_id` to determine scope.

## Incremental

Incremental processing is **target-specific**. The same source may have been consumed to different points by different targets, so `target_table_id` is required.

FabricOps:

1. observes the complete physical source,
2. resolves the last committed Source Observation for that exact source-to-target relationship,
3. derives the unconsumed scope,
4. reads or filters to that scope,
5. captures current-run observation state without advancing accepted progress.

Accepted progress advances only after the corresponding target publication succeeds.

### First run

When no committed source-to-target baseline exists, Incremental deterministically uses a **full bootstrap read**.

The write strategy then determines whether that bootstrap can be published safely. For example, Incremental + Append requires a new or empty target when no committed baseline exists; FabricOps refuses to append a full bootstrap into an already populated target.

### Incremental scope

Depending on the governed processing definition and observations, FabricOps can resolve a watermark or changed-partition scope. The Read result exposes a compact `scope` plus `has_data` / `should_process` so the notebook can see whether there is work to process.

For Lakehouse sources, FabricOps filters the Spark DataFrame. For Warehouse sources, FabricOps generates its own SQL predicate and pushes the incremental scope into the Warehouse read.

Caller-owned Warehouse `query` SQL cannot be combined with Incremental mode because FabricOps owns the incremental predicate.

## Relationship to load strategy

Read mode and target Load Strategy are separate decisions, but some combinations have safety requirements.

| Example | Meaning |
| --- | --- |
| Full → Overwrite | Rebuild and publish the complete target state. |
| Incremental → Append | Process only new scope and append it. |
| Incremental → SCD1 | Process changed scope and merge current values by governed key. |
| Incremental → SCD2 | Process changed scope and maintain governed history. |
| Incremental → whole-table Overwrite | Rejected because a partial input cannot safely replace the complete target. |
| Incremental → partition-scoped Overwrite | Supported when governed partition scope can safely replace the affected Lakehouse partitions. |

See [Load Strategies](load-strategies.md) for the target-side semantics.

## Source observations and retries

Incremental scope is based on **committed** source-to-target progress, not merely on the fact that a source was read. FabricOps stages/observes source state during the run and commits accepted progress only after successful target publication.

That boundary prevents a failed pipeline from silently advancing its watermark or partition baseline and skipping unprocessed data on the next run.

## Related documentation

- [Plug-and-Play Data Pipelines with Data Contract Enforcement](../solutions/plug-and-play-data-pipelines.md)
- [`orchestrate_read()`](../api/reference/orchestrate_read.md)
- [`pipeline_read()`](../api/reference/pipeline_read.md)
- [Guided Demo: Full Read Pipeline](../guided-demo/02-build-and-run-etl.md)
- [Guided Demo: Incremental Append Pipeline](../guided-demo/02B-build-and-run-incremental-append-etl.md)
