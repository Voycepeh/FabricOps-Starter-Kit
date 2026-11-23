# Run column lineage

FabricOps captures source-to-output dependencies for each prepared Write in `METADATA_PIPELINE_RUN.operations[].lineage`. The parent `run_id` and operation identity own the graph. Read/Write participation remains in the existing operation fields and `source_assets`.

## Physical storage for reporting

**Power BI reads `METADATA_DATA_LINEAGE` directly.** Persistent finalization materializes one scalar row per Run × Write × output column × source column × dependency type. A source with both VALUE and FILTER roles produces separate facts. Constants/generated outputs, source row-set dependencies and unknown/omitted outputs have explicit record types, so an absent source is never confused with a participating Read.

| Consumer | Storage |
| --- | --- |
| Power BI and cross-run impact queries | `METADATA_DATA_LINEAGE`, filtered to `lineage_version = 1`; no JSON expansion required |
| Detailed expression/operator drill-through | The owning Run's `operations[].lineage` graph, linked by run_id + operation_key, then target/source column IDs |
| Run participation | Existing operations and `source_assets`, independently of detected dependencies |

The physical projection contains **18 dependency fields and eight standard audit fields**:

| Fields | Purpose |
| --- | --- |
| `lineage_id`, `lineage_version`, `record_type` | Stable fact identity, reporting-version filter and dependency/constant/gap distinction |
| `run_id`, `operation_key` | Link to the finalized Run and owning Write |
| `publication_status`, `coverage` | Distinguish published input and incomplete capture |
| Source and target `asset_workspace_id`, `table_id`, `asset_type` | Separate physical Catalogue identities, including cross-workspace and file assets |
| Source and target `column_id`, `column_name` | Graph nodes and readable labels |
| `dependency_type` | Distinguish value dependencies from filters, joins and other influences |

Pipeline identity, execution workspace, Run/operation status, write mode, detector/scope, gap diagnostics, omitted counts, transformation summaries, graph node IDs and the snapshot hash are not repeated on dependency rows. Obtain Run attributes through `run_id`; use `operation_key` and column IDs to drill into the detailed graph. The publication result still returns a snapshot hash for retry tracking, without storing it on every fact. Facts can be rebuilt from the retained Run without executing business code.

### Power BI model

Import the physical table through the Lakehouse SQL endpoint or supported Delta connection, filter `lineage_version = 1`, and keep `record_type` in the model. Relate `run_id` to `METADATA_PIPELINE_RUN`. Use separate source and target Catalogue dimensions; join each role on physical `asset_workspace_id + table_id + asset_type` (create a composite model key when required). Column IDs/names already exist in the fact table. If current Catalogue columns are needed as dimensions, flatten its `columns_json` once; lineage reports themselves need no JSON parsing.

Use distinct output-column counts when counting impacted columns: multiple source columns and dependency types intentionally create multiple facts. Filter `publication_status = published` when reporting confirmed publication, and retain coverage and record-type filters. A published Write can belong to a later failed Run. Row-set dependencies have no source column ID; OUTPUT/GAP/CAPTURE_GAP rows do not assert source-column dependencies.

### Publication and recovery

The Run commits first. Finalization then publishes the entire projection in one idempotent Delta append, using a permanent per-Run transaction identity, metadata-conflict retry and exact read-back verification. The Run and projection are separate Delta commits; facts become available at finalization, including failed or incomplete Run boundaries. A hard interruption can leave a committed Run awaiting projection. A normal projection failure is explicit and never changes business publication or rewrites the finalized Run.

Retry `finalize_pipeline(pipeline)` with the retained session to retry projection only, even if that session already closed. An internal maintainer repair can call `publish_column_lineage(run_record, context=runtime, spark_session=spark)` after reading the finalized Run from configured Metadata. The publisher verifies the exact committed snapshot and rejects fabricated or incomplete inputs. Retry handles a lost append acknowledgement by reading back the complete expected facts. Do not replay business Writes to repair reporting. Delta transaction identity retention must remain unbounded; unsupported finite retention fails explicitly.

### Upgrade and rollback boundary

`setup_metadata_tables` creates the new canonical table for fresh installations. For an existing historical activity layout, it adds the nullable fact columns without rewriting rows or dropping original/extension columns. Repeat setup is safe. Historical activity rows keep `lineage_version`, `run_id` and `record_type` null; no Run or column dependencies are inferred from participation. Dependency reports must filter `lineage_version = 1`. Old Runs without graphs are not backfilled with invented dependencies.

Migration support follows released versions. Release `0.5.0` shipped the 13-column participation layout; the intermediate 40-column projection was unreleased and has no migration path. Fresh installations use the 26-column schema, and released participation layouts receive the additive upgrade described above.

Legacy reports must select null `lineage_version` before treating rows as activity. Keep the evolved data intact when rolling back; do not drop/rebuild a supported released table. The demo data reset preserves both version 1 dependency facts and historical activity rows.

## Automatic capture

Successful `orchestrate_read` calls register trusted physical Read plan leaves in the active session. At each Write, the detector walks the analyzed Catalyst plan, binds attributes by Spark expression ID, and records operator/expression edges. Semantic plan equality identifies registered Reads, including cloned attributes in self-joins; ambiguous physical matches remain unknown. Only ancestors of actual Write outputs enter the persisted graph. An unused participating Read does not become a dependency.

Table Writes capture the prepared input, including supported Sensitive Data expressions, row hash, audit and SCD2 lifecycle columns, before the publication framework's local checkpoint truncates the plan. A session-only bridge preserves the captured graph if a later Write uses that framework-owned snapshot. File Writes capture their supplied input before profiling/publication. Dry Run retains graphs in memory and never commits them.

Capture inspects plan/schema metadata without collecting or counting business rows. It does not install global listeners, patch pandas, replay notebook code or execute an extra Write. JVM references stay in session memory and are cleared on session close.

Each graph contains:

- `version`, `detector`, `scope="write_input"` and `write_mode`.
- `outputs`: final column names/IDs, root source references, transformation node IDs, gaps and coverage.
- `nodes` and `edges`: source assets/columns, intermediate columns, aliases, operators, expressions, generated values and unknown boundaries.
- Dependency roles: `VALUE`, `JOIN`, `FILTER`, `GROUP`, `ORDER`, `CONDITION`, `PARTITION`, `ROW_SET` and internal `TRANSFORM` links. Root summaries retain multiple roles when appropriate.
- `output_count`, `omitted_output_count` and graph-level `gaps`, so bounded fallback is visible.

Literal expression payloads, row samples, raw SQL strings and UDF bodies are excluded. Column and alias names remain verbatim metadata, including any expression text Spark uses for an automatically named column. Operation classes, names and types explain structure, such as a Multiply followed by Sum, without storing the exact calculation constants. Python variable assignment names are unavailable in Catalyst; aliases and Spark plan stages provide the intermediate structure.

## Coverage and publication

**Coverage is a dependency claim, not a successful-publication claim.** `complete` means all traversed dependencies are understood within the Write-input scope; `partial` retains known roots alongside gaps; `unknown` cannot establish the origins. Constants can be complete with no source columns. Source-asset `ROW_SET` roots represent row membership/cardinality, including `count(*)` and cross joins.

Always examine the operation's `status` and `publication_status` as well as the parent Run status. An attempted Write can have a graph before publication fails. Conversely a published Write can survive a later failed notebook or metadata stage. Missing historical publication status is unknown. For an empty/no-op publication, the graph still describes the attempted input, not newly committed rows.

`scope="write_input"` deliberately excludes target rows retained by append or SCD merges and does not model target-side merge execution or row-level provenance. Existing-target filtering can add an unknown target-read boundary. This graph cannot claim that every row currently in the target was created by this Run.

| Boundary | Behaviour |
| --- | --- |
| Projects, renames, arithmetic, casts, common SQL functions, joins, filters, grouping/aggregates, unions, windows and generators | Trace supported analyzed expressions and plan operators automatically |
| Functions returning Spark DataFrames, aliases and caches | Preserve Catalyst dependencies without requiring annotations |
| Python UDF | Keep declared input argument dependencies; mark the opaque implementation as a gap |
| `toPandas()` then `createDataFrame()` | Record unknown origins; matching names or values never restores attribution. Run participation remains available |
| `mapInPandas`, RDD reconstruction, user checkpoint, unsupported plan/expression | Explicit unsupported/severed boundary; no inferred source attribution |
| Warehouse pushed-down custom query | Unknown column origins; SQL projection aliases are not assumed to be physical columns |
| Native Spark SQL over registered Lakehouse sources/views | Traverse its analyzed plan |
| Spark Connect, inaccessible JVM plans or changed Catalyst APIs | Record `plan_access_unavailable`; business publication can continue |

The detector bounds each traversal to 10,000 nodes, 30,000 edges, plan depth 160, 1,000 outputs and a serialized graph of 1,000,000 bytes. It keeps at most 128 registered source leaves and 32 framework snapshot bridges per session. Exceeding the source registry budget makes subsequent captures unknown, preserving ambiguity rather than evicting conflicting identities. Evicted snapshot bridges become unknown. Exceeding traversal/serialization limits produces an unknown graph with `lineage_limit`; any omitted output count is explicit. These are implementation budgets, not Spark or Fabric limits.

## Query a retained Run

The internal query helper accepts a logical Run dictionary or a physical metadata row dictionary whose operations are JSON:

```python
from fabricops_kit.pipeline.shared import column_lineage_rows

rows = column_lineage_rows(run_record)
value_links = [row for row in rows
               if row["target_column_name"] == "revenue"
               and row["dependency_type"] == "VALUE"]
```

Each projected row includes Run/operation references, physical target/source identities, column IDs/names, one dependency type, coverage and publication status. Diagnostic details remain in the Run graph. Constants and unknown outputs produce rows with null source fields. Retained Runs without captured lineage return no projected rows; absence is not proof of no dependencies. The helper is an internal maintainer interface, not a supported public export. Power BI consumers use the physical scalar table. Maintainers exploring detailed graphs can obtain the operations type from `metadata_json_schema("METADATA_PIPELINE_RUN")["operations"]` and resolve node IDs within the owning Write graph.

## Research and detector choice

[OpenLineage's Spark column detector](https://openlineage.io/docs/integrations/spark/spark_column_lineage/) derives dependencies from logical plans and expression IDs, distinguishing value construction from indirect influences. [Spline's Spark agent](https://github.com/AbsaOSS/spline-spark-agent) collects runtime plans through a driver agent and has Spark/Scala compatibility requirements. Spark's [QueryExecutionListener](https://spark.apache.org/docs/latest/api/java/org/apache/spark/sql/util/QueryExecutionListener.html) exposes success/failure callbacks and query plans; callbacks can arrive on multiple threads. Spark also documents that [checkpointing truncates logical plans](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.checkpoint.html).

FabricOps follows the plan/expression approach while capturing at its existing Read/Write boundaries. This choice gives exact Run ownership and avoids recording profiling or metadata queries as business dependencies. It requires no extra JVM agent deployment. The cost is a deliberately limited Catalyst visitor that must be verified against each intended Fabric runtime; it does not provide OpenLineage/Spline's full operator coverage or event ecosystem.

## Verification and Fabric acceptance

`tests/unit/test_column_lineage.py` uses real Spark plans for multi-Read/multi-Write transformations, self-joins, union-by-name with different orders, windows, CASE, casts, SQL views, explode, cache, checkpoints, opaque UDFs, an actual pandas round trip, generated constants, bounds and inaccessible plans. It independently asserts expected source columns and roles, excludes unused Reads, and checks Run finalization/projection after failure. `tests/integration/test_write_publication_input.py` verifies capture before actual writer checkpointing, including hash/audit columns, for persistent and Dry Run modes. `tests/unit/test_file_asset_metadata.py` verifies real Spark FILE-to-FILE lineage through orchestration and finalization. Those detector/orchestration tests simulate Fabric transport. Delta-enabled integration cases in `test_pipeline_run_delta.py` verify physical fact publication, rebuilding from physical Run JSON, idempotent retries, a denied projection after Run commit and lost append acknowledgements. `test_column_lineage_upgrade.py` verifies additive upgrade from the released participation layout and repeat setup with retained legacy bytes and extension columns.

Local Spark tests do not establish signed-in Microsoft Fabric acceptance. Before claiming a runtime is validated, run table and file cases in an isolated Fabric workspace using its intended Spark version, including Lakehouse/Delta and Warehouse connector plans, an opaque Warehouse query, cross-workspace Catalogue joins, SCD/append scope, a later notebook failure, and a pandas boundary. Inspect persisted operations and publication status after reopening the Run. No runtime compatibility claim should be inferred from a green local Spark suite.
