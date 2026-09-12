# Unit 5: Choose target processing and review results

**Keep source reads simple, choose the governed target strategy, then review what the completed run produced.**

## Read each source normally

`pipeline_read()` resolves the source `table_id`, physical location, and source Lineage context. FabricOps then delegates to the configured foundational Lakehouse or Warehouse reader. Read preparation does not inspect a downstream target, calculate watermark or partition progress, skip the pipeline, or return a processing scope.

This keeps each Read block independent of its eventual Write destination:

```text
Identify source
      ↓
Resolve table_id and source Lineage
      ↓
Physically read the source
```

Use an explicit Warehouse query when the project needs source-side filtering, projection, joins, or aggregation. That query is project-owned read logic rather than hidden incremental state in Read preparation.

## Choose target processing

Target processing remains configured at the Write boundary. `pipeline_write()` resolves the target's governed `load_strategy` and applies the corresponding Lakehouse or Warehouse publication behaviour. The foundational writers perform physical I/O only.

In the contract-free Step 2 run, Development identifies the physical target and proposes its processing settings directly in the template. After Governance freezes a Data Contract, Step 4 validates that proposal against the selected version; in Production, the active frozen version is authoritative.

| Target strategy | Typical use |
| --- | --- |
| `overwrite` | Replace a target from a complete prepared result. |
| `append` | Add prepared rows to an append-only target. |
| `scd1` | Upsert current values by governed key columns. |
| `scd2` | Preserve governed history using effective dates and tracked columns. |

Keep merge, upsert, append, partitioning, and other target-side decisions in target configuration and the Write block. A Read block should not need to know where its DataFrame will later be written.

!!! warning "One governed target, one writer"

    One governed target `table_id` should have one owning pipeline/notebook writer. Independent writers can race, duplicate appends, overwrite each other's state, break SCD history, or apply inconsistent assumptions. FabricOps freezes the owner's logical notebook name with the Data Contract and rejects a contract-backed write from a conflicting notebook name. The physical notebook ID remains diagnostic metadata because it can differ after promotion to another workspace.

## Keep Source Stability separate from processing

Freshness asks whether the source is recent enough. Source Stability asks whether data already processed by the pipeline changed unexpectedly. For example, today's arrival can pass Freshness while a value processed yesterday changing from `$20` to `$25` is still detected as historical mutation. New data is compatible with append; changed, removed, or reappeared historical data violates append stability, while overwrite, SCD1, and SCD2 can reconcile it. Source Stability reports the evidence and validates compatibility without selecting or executing the load strategy.

`METADATA_SOURCE_OBSERVATION` stores both states in one append-only table. Source evidence is first written with `observation_status="observed"`, scoped by logical notebook name, source `table_id`, and target `table_id`. Only a successful physical target write appends the corresponding `committed` state, making it eligible as the next baseline. A failed write leaves the raw observed rows intact but commits neither an accepted baseline nor successful target Lineage.

## Keep canonical profiles complete

A normal complete-table source read can refresh the canonical registered source Profile. A filtered, joined, or aggregated Warehouse query should not replace the Profile of the complete physical source. The current `02_pipeline` treats that query result as derived data and uses `profile_table(dataframe=df)` for diagnostic profiling instead of registering it as the canonical physical-table profile.

## Review the completed run

After the baseline pipeline succeeds, confirm that the target exists and that `METADATA_DATA_CATALOGUE`, `METADATA_DATA_PROFILED`, `METADATA_DATA_PROFILED_FREQUENCY` where applicable, and `METADATA_DATA_LINEAGE` records were written.

Those concrete metadata records are the handoff to Governance in Step 3.

!!! important "What happens next"

    Do not add Guardrail checks manually to this module. Step 3 reads `METADATA_DATA_CATALOGUE` and `METADATA_DATA_PROFILED`, then uses the unified editor to author `METADATA_ENRICHMENT` and `METADATA_GUARDRAIL` for one `table_id` and freeze the Data Contract version. Step 4 selects that exact version in `02_pipeline`, writes summaries to `METADATA_GUARDRAIL_RESULTS`, and returns DQ failed values to the caller without persisting them automatically. Step 5 explicitly links the tested version to its Data Agreement and activates it. Step 6 promotes and runs the pipeline against the active contract.

For exact APIs such as `pipeline_read()` and `pipeline_write()`, use the [Function Reference](../../reference/index.md). The template is the normal learning-path entry point.

**Previous:** [Unit 4: Transform and write](transform-and-load.md)  
**Next:** [Step 3: Author and freeze the Data Contract](../03-enrich-guardrails.md)
