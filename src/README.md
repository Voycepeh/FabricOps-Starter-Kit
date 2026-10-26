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

The standalone `pipeline_read()`, `pipeline_write()`, `check_schema()`, `check_freshness()`, `check_source_drift()`, `check_dq()`, `check_sensitive_data()` entrypoints have been removed from the public API. Their owner modules contain internal implementation stages; they are not supported notebook imports. This intentionally removes the former Live `pipeline_read()` and `pipeline_write()` API contracts without compatibility aliases.

Migrate notebooks to the orchestrator calls in `templates/notebooks/02_pipeline.ipynb`. Keep transformations between Read and Write. Read check results come back under `freshness_result`, `schema_result`, `grain_result`, and `dq_result`; Write also returns `sensitive_result`, `source_drift_results` and `source_guardrail_results`. Live stops on Block before publication; Testing returns blocking outcomes for inspection. Default Bootstrap permits initial publication only before any participant has frozen or active contracts; Live rejects No Contract.

For token mapping reuse, pass the persisted mapping as `orchestrate_write(existing_mapping=...)` and retain `result["sensitive_result"]["support_mapping"]` for later runs. Live can reuse and insert assignments in a separately configured restricted token vault. Testing never inserts mapping assignments.

Schema presence/datatype violations and configured Sensitive Data treatment failures block. Grain, Freshness, Source Drift, and DQ retain their authored Warn/Block policies. Each configured Guardrail owns its continuation decision; intentionally disabled checks do not impose additional requirements. Foundational physical I/O and `profile_table()` remain public standalone utilities.

By default, `setup_pipeline(sources=..., targets=...)` returns a noninteractive Bootstrap plan. Bootstrap permits initial publication/profiling while no participating frozen or active contract exists, and rechecks that condition before every Read/Write. To test authored contracts, explicitly set `interactive=True` or supply exact headless Testing configuration.

Configure only `pipeline_id` and `pipeline_mode` (`Test` or `Live`) through `setup_pipeline()`, then Read → Transform → Write → `finalize_pipeline()`. Finalize publishes Test run and Guardrail results for activation review and releases Live reservations. Runtime authority, source participation and reporting are internal. See the [execution modes and completion limits](../templates/notebooks/README.md#pipeline-execution-mode).

Until immutable mapping-dependency identity is supported, caller-owned/configured token-mapping candidates remain diagnostic-only and cannot be activated. For internal caller-owned mapping management, after consuming the prepared DataFrame and persisting a returned mapping, release its cache with `result["sensitive_result"]["support_mapping"].unpersist()`. Failed orchestration releases token caches automatically.

### Contract-driven Guardrails migration

Data Contract → Configured Guardrails → Testing/Live Execution → Results.

`orchestrate_write()` no longer returns `coverage_result` or runs a separate Coverage Gate stage. Read and Write use the context-local execution established by setup. Source Read rules must produce exact-plan, exact-contract results before a Live Write can consume them. Empty rule lists and `is_active=False` optional definitions are valid; they do not require a minimum number of checks. Existing Schema and Sensitive Data Block policies and all Warn/Block actions are unchanged.

Canonical existing Data Contracts need no rewrite. Payloads containing legacy `coverage_gate`, `coverage_policy`, `coverage_gate_policy` or `guardrail_coverage` settings are rejected with migration guidance rather than silently ignored. Create a new draft, express every required protection as an enabled Guardrail, remove obsolete settings, then freeze, test and activate the new version. Never edit a frozen payload. A legacy coverage Guardrail entry is unsupported and must likewise be replaced in a new version. Testing continues to write neither data nor metadata.

Expand the Data Contract selector's sections to inspect columns/types, Grain keys, individual DQ rules and all saved policies and states. After running its plan, call `CONTRACTS["refresh"]()` to inspect available exact-version results. Saved definitions alone are not execution results.
