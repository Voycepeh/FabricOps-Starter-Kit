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

The standalone `pipeline_read()`, `pipeline_write()`, `check_schema()`, `check_freshness()`, `check_source_drift()`, `check_dq()`, `check_sensitive_data()` entrypoints have been removed from the public API. Current owner modules contain internal implementation stages; the obsolete Contract Source Drift evaluator has been removed. These names are not supported notebook imports.

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

`setup_pipeline(source_drift_enabled=False, source_drift_interval_days=1, source_drift_block=True)` controls automatic complete-source observation, independently of every profiling setting. Read all sources before any Write; the first Write closes the Read set and consolidates source decisions. Source hashes and duplicate multiplicities remain distributed. Validated authored keys permit exact modified-row counts; unkeyed comparisons report content additions/removals with modifications unknown. The first successful observation establishes history without invented prior changes.

Confirmed acceptance history is shared by execution workspace and exact physical workspace/item/table. Successful finalization and all required verified publications precede an atomic conditional head update; failed, blocked, incomplete or nonpublishing work cannot advance it. Nonblocking mode retains warnings and the same acceptance boundary. Dry Run persists neither baselines nor publication state. `finalize_pipeline()` adds a `source_drift` diagnostic summary when enabled, separately from immutable Run content. Acceptance failures leave prior baselines authoritative and require investigation/new execution. Engineering settings are retained in saved approval/promotion identity; new Contracts omit Source Drift rules while historical frozen records remain unchanged. The former `observe_source` and `source_observation_days` parameters have no aliases.
