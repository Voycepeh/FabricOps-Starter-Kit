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

## Regenerate the function reference

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
```

Run the generator whenever public exports change (add/remove/rename) so GitHub Pages stays aligned with the package surface.

## Governed pipeline execution

Use `orchestrate_read()` and `orchestrate_write()` for governed pipeline execution. The orchestrators own the Read/Write stages, Guardrail evaluation, Sensitive Data treatment, result persistence, and failure decisions.

The standalone `pipeline_read()`, `pipeline_write()`, `check_schema()`, `check_freshness()`, `check_source_drift()`, `check_dq()`, `check_sensitive_data()` entrypoints have been removed from the public API. Their owner modules contain internal implementation stages; they are not supported notebook imports.

Use the orchestrator calls in `templates/notebooks/02_pipeline.ipynb`. Keep transformations between Read and Write. Read check results come back under `freshness_result`, `schema_result`, `grain_result`, and `dq_result`; Write also returns `sensitive_result`, `source_drift_results` and `source_guardrail_results`. Governed execution stops on Block before publication. Dry Run returns blocking outcomes for inspection without publishing, while Ungoverned skips contract-dependent checks and refuses writes to governed targets.

For token mapping reuse, pass the persisted mapping as `orchestrate_write(existing_mapping=...)` and retain `result["sensitive_result"]["support_mapping"]` for later runs. Persisting modes can reuse and insert assignments in a separately configured restricted token vault. Dry Run never inserts mapping assignments.

Schema presence/datatype violations and configured Sensitive Data treatment failures block. Grain, Freshness, Source Drift, and DQ retain their authored Warn/Block policies. Each configured Guardrail owns its continuation decision; intentionally disabled checks do not impose additional requirements. Foundational physical I/O and `profile_table()` remain public standalone utilities.

`Ungoverned` is the default execution mode, but persistent Ungoverned and Governed executions require an explicit stable `pipeline_id`. Dry Run may omit it for a session-only identity and provides optional frozen Contract selection for preview validation. Governed resolves its exact activated configuration from authority.

Call `setup_notebook()` first, define and retain a literal UUIDv4 `PIPELINE_ID` in version-controlled notebook source, then call `setup_pipeline(pipeline_id=PIPELINE_ID, pipeline_mode=...)`. Run Read → Transform → Write → `finalize_pipeline(pipeline)`. Persistent modes require the explicit stable ID; Dry Run may omit it for a session-only identity. Dry Run previews business changes and persists available saved-definition/test claims in Engineering Files; Governed enforces activated Data Contracts. Runtime authority, source participation and reporting remain internal. See the [execution modes and completion limits](../templates/notebooks/README.md#pipeline-execution-mode).

Until immutable mapping-dependency identity is supported, caller-owned/configured token-mapping candidates remain diagnostic-only and cannot be activated. For internal caller-owned mapping management, after consuming the prepared DataFrame and persisting a returned mapping, release its cache with `result["sensitive_result"]["support_mapping"].unpersist()`. Failed orchestration releases token caches automatically.

### Contract-driven Guardrails

Data Contract → Configured Guardrails → Governed execution → Results.

`orchestrate_write()` no longer returns `coverage_result` or runs a separate Coverage Gate stage. Read and Write use the context-local execution established by setup. Source Read rules must produce exact-plan, exact-contract results before a Governed Write can consume them. Empty rule lists and `is_active=False` optional definitions are valid; they do not require a minimum number of checks. Existing Schema and Sensitive Data Block policies and all Warn/Block actions are unchanged.

Frozen Contracts contain canonical executable Guardrails and descriptive Enrichment. Unsupported Coverage Gate keys fail validation instead of being silently ignored. Frozen payloads are immutable. Dry Run writes no business data, checkpoints or published operational tables. Explicit finalization returns its summary and saves available saved-definition/test claims in Engineering Files. For a completed captured Dry Run, `finalize_pipeline()` automatically saves the submission and displays its status, approval refresh, explicit deployment and recovery controls; `widget_activate_pipeline()` lists saved submissions directly and lets Governance review and decide them. No file download, upload or JSON paste is required. No Python session crosses that boundary.

Expand the Data Contract selector's sections to inspect columns/types, Grain keys, individual DQ rules and all saved policies and states. After running its plan, call `CONTRACTS["refresh"]()` to inspect available exact-version results. Saved definitions alone are not execution results.
