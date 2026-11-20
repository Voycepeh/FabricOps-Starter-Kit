# Run column lineage

FabricOps captures source-to-output dependencies for each prepared Write in `METADATA_PIPELINE_RUN.operations[].lineage`. The parent `run_id` and operation identity own the graph. Read/Write participation remains in the existing operation fields and `source_assets`.

## Storage follows the question

**The primary query is: for this Run and output column, which source columns contributed, and through which transformations?** A versioned per-Write graph inside the existing `operations` JSON STRING keeps that answer with its Run, Contract references, target and publication outcome. There is no extra physical table, metadata commit or migration of retained rows. `METADATA_DATA_LINEAGE` remains a historical archive; current workflows never write or delete it.

| Query | Representation |
| --- | --- |
| Inspect a Run's output column and intermediate steps | Read the Write's graph and follow incoming edges from its output node |
| Join contributing assets/columns to the Catalogue | Flatten `outputs[].sources` through `nodes`; join physical `asset_workspace_id + table_id + asset_type`, then `column_id` in Catalogue `columns_json` |
| List the assets participating in a Run | Use operations and `source_assets`; participation makes no claim about column dependencies |
| Search affected outputs across many Runs | Filter Runs first, then project graphs; if this becomes a frequent large scan, materialize a rebuildable edge index keyed by Run/operation/output/source and detector version |

A future impact index should be derived from Run graphs, with the same coverage and publication filters. Maintaining two independent lineage authorities would introduce disagreement and another failure boundary. This implementation adds no such index.

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
               and "VALUE" in row["dependency_types"]]
```

Each projected row includes Run/operation, physical target/source identities, column IDs, dependency roles, coverage, gaps and operation/publication status. Constants and unknown outputs produce rows with null source fields. Retained Runs without captured lineage return no projected rows; absence is not proof of no dependencies. The helper is an internal maintainer interface, not a supported public export. SQL consumers can use the canonical `metadata_json_schema("METADATA_PIPELINE_RUN", "operations")` to parse operations before exploding graph outputs and sources; resolve `node_id` against the graph's nodes.

## Research and detector choice

[OpenLineage's Spark column detector](https://openlineage.io/docs/integrations/spark/spark_column_lineage/) derives dependencies from logical plans and expression IDs, distinguishing value construction from indirect influences. [Spline's Spark agent](https://github.com/AbsaOSS/spline-spark-agent) collects runtime plans through a driver agent and has Spark/Scala compatibility requirements. Spark's [QueryExecutionListener](https://spark.apache.org/docs/latest/api/java/org/apache/spark/sql/util/QueryExecutionListener.html) exposes success/failure callbacks and query plans; callbacks can arrive on multiple threads. Spark also documents that [checkpointing truncates logical plans](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/api/pyspark.sql.DataFrame.checkpoint.html).

FabricOps follows the plan/expression approach while capturing at its existing Read/Write boundaries. This choice gives exact Run ownership and avoids recording profiling or metadata queries as business dependencies. It requires no extra JVM agent deployment. The cost is a deliberately limited Catalyst visitor that must be verified against each intended Fabric runtime; it does not provide OpenLineage/Spline's full operator coverage or event ecosystem.

## Verification and Fabric acceptance

`tests/unit/test_column_lineage.py` uses real Spark plans for multi-Read/multi-Write transformations, self-joins, union-by-name with different orders, windows, CASE, casts, SQL views, explode, cache, checkpoints, opaque UDFs, an actual pandas round trip, generated constants, bounds and inaccessible plans. It independently asserts expected source columns and roles, excludes unused Reads, and checks Run finalization/projection after failure. `tests/integration/test_write_publication_input.py` verifies capture before actual writer checkpointing, including hash/audit columns, for persistent and Dry Run modes. `tests/unit/test_file_asset_metadata.py` verifies real Spark FILE-to-FILE lineage through orchestration and finalization. Metadata transport in these tests is simulated.

Local Spark tests do not establish signed-in Microsoft Fabric acceptance. Before claiming a runtime is validated, run table and file cases in an isolated Fabric workspace using its intended Spark version, including Lakehouse/Delta and Warehouse connector plans, an opaque Warehouse query, cross-workspace Catalogue joins, SCD/append scope, a later notebook failure, and a pandas boundary. Inspect persisted operations and publication status after reopening the Run. No runtime compatibility claim should be inferred from a green local Spark suite.
