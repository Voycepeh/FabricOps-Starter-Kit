# Source package guide (`src/fabricops_kit`)

This package keeps runtime logic in `src/fabricops_kit/` and publishes user-facing callables through `fabricops_kit.__all__` in `src/fabricops_kit/__init__.py`.

## Public callable catalogue sources

- **Public callable source of truth:** `__all__` in `src/fabricops_kit/__init__.py`.
- **Generated docs outputs:**
  - Step-first reference: `docs/reference/index.md`

## Spark session discovery

Notebook-facing APIs resolve Spark automatically. Remove the former `spark` and
`spark_session` arguments from metadata setup, readers, Governance widgets,
profiling, access scanning, and Data Agent calls. This is a breaking API cleanup;
there are no compatibility aliases.

FabricOps prefers an existing DataFrame's session, then an internally supplied
operation session, then PySpark's active session. If PySpark does not expose the
Fabric session, FabricOps checks `spark` in the IPython notebook namespace. It
never creates a session. Spark-dependent operations raise a clear error when
none is available. `setup_notebook()` still validates explicit local configuration
without Spark and reports that Spark-dependent operations are unavailable. Setup
uses the same detected session for readiness and the configured audit timezone.
Tests inject sessions at internal discovery boundaries or through private runtime
context; notebook code does not need session plumbing.

## Dedicated Guided Demo reset

After `setup_notebook()`, call the public Preview API `orchestrate_demo_reset()`
to inspect the reset scope. `orchestrate_demo_reset(reset=True)` opts into clearing
all metadata and saved lifecycle artifacts in the dedicated `demo_metadata`
Lakehouse, restoring five Day 1 sources and removing six demo outputs. Stop all
demo writers first; never use shared or production Metadata. The orchestrator
owns preflight and verification, so 00C imports no internal reset foundations.
See the [Guided Demo](../docs/guided-demo/00C-prepare-demo-data-with-fabricops-io.md).

## Regenerate the function reference

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
```

Run the generator whenever public exports change (add/remove/rename) so GitHub Pages stays aligned with the package surface.

## Governed pipeline execution

Use `orchestrate_read()` and `orchestrate_write()` for governed pipeline execution. The orchestrators own the Read/Write stages, Guardrail evaluation, Sensitive Data treatment, result persistence, and failure decisions.

The standalone `pipeline_read()`, `resolve_table_id()`, `pipeline_write()`, `check_schema()`, `check_freshness()`, `check_source_drift()`, `check_dq()`, `check_sensitive_data()` entrypoints have been removed from the public API. Current owner modules contain internal implementation stages; the obsolete Contract Source Drift evaluator has been removed. These names are not supported notebook imports.

Use the orchestrator calls in `templates/notebooks/02_pipeline.ipynb`. Keep transformations between Read and Write. Read check results come back under `freshness_result`, `schema_result`, `grain_result`, and `dq_result`; Write also returns `sensitive_result`, `source_drift_results` and `source_guardrail_results`. Governed execution stops on Block before publication. Dry Run returns blocking outcomes for inspection without publishing, while Ungoverned skips contract-dependent checks and refuses writes to governed targets.

`orchestrate_write()` returns the final prepared Write input as `result["dataframe"]`, including Sensitive Data treatment, `_row_hash`, target audit columns and applicable SCD2 lifecycle columns. Preview it with `display(result["dataframe"].limit(10))`. Append New Only returns only rows submitted for insertion; SCD1/SCD2 show processing input rather than a reconstructed post-merge destination. Dry Run returns the prepared input available at that stage without publication.

`write_metrics["rows_committed"]` (Rows loaded) measures commits in the current attempt. Native Delta metrics take priority; Warehouse overwrite/append use the PublicationBatch receipt count only after successful publication and confirmation. Already loaded reports zero new commits. SCD change counts stay unavailable unless reliably measured. `input_rows` describes the incoming batch; `total_target_rows` describes the destination total where profiling provides it. These metrics require no extra reporting counts.

For token mapping reuse, pass the persisted mapping as `orchestrate_write(existing_mapping=...)` and retain `result["sensitive_result"]["support_mapping"]` for later runs. Persisting modes can reuse and insert assignments in a separately configured restricted token vault. Dry Run never inserts mapping assignments.

Schema presence/datatype violations and configured Sensitive Data treatment failures block. Grain, Freshness, Source Drift, and DQ retain their authored Warn/Block policies. Each configured Guardrail owns its continuation decision; intentionally disabled checks do not impose additional requirements. Foundational physical I/O and `profile_table()` remain public standalone utilities.

`Ungoverned` is the default execution mode. FabricOps derives the logical Pipeline ID from the current Fabric Notebook ID and resolves promoted copies through `METADATA_PIPELINE_REGISTRY`. Dry Run supports optional frozen Contract selection for preview validation. Governed resolves its exact activated configuration from authority.

Call `setup_notebook()` first, then `setup_pipeline(pipeline_mode=...)`. Run Read → Transform → Write → `finalize_pipeline(pipeline)`. FabricOps resolves notebook identity internally; notebook-level Pipeline ID declarations are not required. Dry Run previews business changes and persists available saved-definition/test claims in Engineering Files; Governed enforces activated Data Contracts. Runtime authority, source participation and reporting remain internal. See the [execution modes and completion limits](../templates/notebooks/README.md#pipeline-execution-mode).

Until immutable mapping-dependency identity is supported, caller-owned/configured token-mapping candidates remain diagnostic-only and cannot be activated. For internal caller-owned mapping management, after consuming the prepared DataFrame and persisting a returned mapping, release its cache with `result["sensitive_result"]["support_mapping"].unpersist()`. Failed orchestration releases token caches automatically.

### Contract-driven Guardrails

Data Contract → Configured Guardrails → Governed execution → Results.

`orchestrate_write()` no longer returns `coverage_result` or runs a separate Coverage Gate stage. Read and Write use the context-local execution established by setup. Source Read rules must produce exact-plan, exact-contract results before a Governed Write can consume them. Empty rule lists and `is_active=False` optional definitions are valid; they do not require a minimum number of checks. Existing Schema and Sensitive Data Block policies and all Warn/Block actions are unchanged.

Frozen Contracts contain canonical executable Guardrails and descriptive Enrichment. Unsupported Coverage Gate keys fail validation instead of being silently ignored. Frozen payloads are immutable. Dry Run writes no business data, checkpoints or published operational tables. Explicit finalization returns its summary and saves available saved-definition/test claims in Engineering Files. For a completed captured Dry Run, `finalize_pipeline()` automatically saves the submission and displays its status, approval refresh, explicit deployment and recovery controls; `widget_activate_pipeline()` lists saved submissions directly and lets Governance review and decide them. No file download, upload or JSON paste is required. No Python session crosses that boundary.

Expand the Data Contract selector's sections to inspect columns/types, Grain keys, individual DQ rules and all saved policies and states. After running its plan, call `CONTRACTS["refresh"]()` to inspect available exact-version results. Saved definitions alone are not execution results.

### Pipeline profiling configuration

`setup_pipeline(profiling_enabled=True, profiling_interval_days=1, profiling_max_rows=None, grain_discovery_enabled=False, frequency_enabled=False)` owns profiling for every Read and Write in the session. Standard runs first when eligible and then on its configured interval; opt-in Grain discovery and Frequency each complete once per physical table with sufficient scope. Bounded completions cannot suppress later full-table work; full completions satisfy bounded requests, and larger bounded completions satisfy equal or smaller bounds. Completion history is shared across pipelines by workspace/item/table, and failed or nonpublishing Writes and Dry Run do not advance it. These settings are part of the approved saved notebook identity.

`profiling_max_rows` selects at most that many rows before profiling computation (Spark limit; Warehouse TOP plus Spark). Physical reads may exceed this bound. Saved snapshots and Data Contract Authoring identify bounded results as sampled; counts and uniqueness are selection-only facts. Full-table row metrics stay unknown when only a sample is measured. Guardrails, Source Observation, publication and checkpoints use their own required inputs. Contracts no longer own profiling schedules and need no saved profiles to freeze or activate. Standalone `profile_table()` defaults Grain discovery and Frequency to False; explicit opt-in parameters remain available.

### Pipeline-owned Source Drift

`setup_pipeline(source_drift_enabled=False, source_drift_interval_days=1, source_drift_block=True)` controls automatic complete-source observation, independently of every profiling setting. Read all sources before any Write; the first Write closes the Read set and consolidates source decisions. Source hashes and duplicate multiplicities remain distributed. Validated authored keys permit exact modified-row counts; unkeyed comparisons report content additions/removals with modifications unknown. Additions alone never block normal incremental ETL; configured blocking applies to removals, modifications, typed-schema changes and unavailable observations. The first successful observation establishes history without invented prior changes.

Confirmed acceptance history is shared by execution workspace and exact physical workspace/item/table. Successful finalization and all required verified publications precede an atomic conditional head update; failed, blocked, incomplete or nonpublishing work cannot advance it. Nonblocking mode retains warnings and the same acceptance boundary. Dry Run persists neither baselines nor publication state. `finalize_pipeline()` adds a `source_drift` diagnostic summary when enabled, separately from immutable Run content. Acceptance failures require investigation/new execution. If acknowledgement and read-back both fail, `acceptance_unknown` requires inspecting immutable acceptance history before retrying; do not assume rollback. Engineering settings are retained in saved approval/promotion identity; new Contracts omit Source Drift rules while historical frozen records remain unchanged. The former `observe_source` and `source_observation_days` parameters have no aliases.

## Lakehouse Files output

Use `write_lakehouse_file()` (Preview) for standalone CSV, Parquet or newline-delimited
JSON output without profiling or metadata persistence:

```python
write_lakehouse_file(
    dataframe=final_df,
    relative_path="Exports/orders.csv",
    store="Silver",
    file_format="csv",
    write_options={"header": True},
)
```

For pipeline participation, use `orchestrate_write()` after `setup_pipeline()`:

```python
result = orchestrate_write(
    dataframe=final_df,
    store="Silver",
    relative_path="Exports/orders.parquet",
    file_format="parquet",
    write_mode="overwrite",
)
```

Supply either table coordinates (`store`, `schema`, `table_name`) or file coordinates
(`store`, `relative_path`, `file_format`). File modes are `errorifexists`, `overwrite`,
`append` and `ignore`; the foundational default is `errorifexists`. Orchestration
requires an explicit `write_mode`. Files do not support `append_all`, Append New Only,
SCD1 or SCD2. A suffix does not select output layout: `orders.csv` is a **dataset
folder** by default. Set `single_file=True` for one artifact with a matching extension;
append is then rejected. Dataset output preserves distributed Spark parallelism and
supports the same `repartition_by` conventions as foundational table writing.

Single-file output uses one executor, stages one part and renames it into place. It
checks up to `max_single_file_rows + 1` rows before staging (default limit 1,000,000)
and checks encoded output size before publication (default 128 MiB). These limits
do not bound executor working memory, especially for wide rows. No business rows
are collected on the driver. Use a stable input during the count and write actions.
Single CSV/JSON artifacts are uncompressed; dataset folders support compression
options, and single Parquet supports internal compression. Temporary paths are
removed after staging. Overwrite and rename are not transactional; serialize writers
to each destination and validate recovery behavior in Fabric.

The result includes the actual `resolved_path`, publication status and available
filesystem metrics. `file_count` and `output_bytes` describe the resulting target,
including prior dataset parts after append. `rows_committed` remains unknown.
`ignore` returns `published=False` when a destination exists. Paths must be exact,
nested paths beneath the configured `Files/` root; absolute paths, traversal, reader
wildcards and destination/layout overrides in `write_options` are rejected.

File writes support Dry Run and Ungoverned. Dry Run validates arguments and profiles
the supplied DataFrame when due, but never stages or publishes files and cannot verify
permissions, collisions or output-size limits. Governed file targets fail closed:
the current Pipeline Promotion authorization supports file Reads only. Ungoverned
still rejects protected file destinations and overlapping folders. File targets use
the existing physical file `source_id`, never a `table_id`, and do not use table
contracts, table audit columns, row hashes or table lineage. Full Read sources can
participate; incremental checkpoint publication remains table-only.

Pipeline profiling honors `setup_pipeline()` settings and profiles the supplied
DataFrame, with session-local file history and no persisted table profile snapshots.
It does not reread the published destination. `METADATA_PIPELINE_RUN` operations retain
source participation, destination, options/layout limits, mode, output path,
publication status and available metrics. Call `finalize_pipeline()` at the normal
notebook boundary; successful publication does not finalize the pipeline.

Configured paths may traverse shortcuts. Fabric must support the underlying write,
delete and rename operations; read-only or unsupported shortcuts raise an error.
SharePoint shortcuts are not assumed writable. There is no Graph upload or redirected
publication. Test permissions, rename behavior and cleanup against the real Fabric
Lakehouse before relying on single-file publication.
