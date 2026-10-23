# Source package guide (`src/fabricops_kit`)

This package keeps runtime logic in `src/fabricops_kit/` and publishes user-facing callables through `fabricops_kit.__all__` in `src/fabricops_kit/__init__.py`.

## Public callable catalogue sources

- **Public callable source of truth:** `__all__` in `src/fabricops_kit/__init__.py`.
- **Generated docs outputs:**
  - Step-first reference: `docs/reference/index.md`

## Regenerate the function reference

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
```

Run the generator whenever public exports change (add/remove/rename) so GitHub Pages stays aligned with the package surface.

## Governed pipeline execution

Use `pipeline = setup_pipeline()`, `orchestrate_read()`, project-owned PySpark
transformations, `orchestrate_write()`, then `finalize_pipeline()` for governed
execution. Setup resolves the actual Fabric workspace and notebook IDs through
the central Workspace Registry. Deployment environment, physical resources,
metadata routing and Test/Live mode come from approved registrations; environment
labels never infer activation or execution mode. Live requires the workspace's
approved manifest and exact activated contracts. Test retains interactive frozen
contract selection and publishes run/Guardrail results only at finalization.

The orchestrators own the Read/Write stages, Guardrail evaluation, Sensitive Data
treatment and failure decisions. Read check results come back under
`freshness_result`, `schema_result`, `grain_result` and `dq_result`; Write also
returns `sensitive_result`, `source_drift_results` and `source_guardrail_results`.
Live stops on Block before publication; Test returns blocking outcomes for inspection.
The standard notebook accepts no environment/resource override. The existing
`pipeline_read()` API and foundational public Fabric IO remain available for
independent use with explicit contexts; `profile_table()` remains a standalone
metadata authoring capability. See generated references for the current public inventory.

Governance uses `setup_governance(target_workspace_id=...)` in the pinned
Governance Workspace. Engineers need only `02_pipeline`; the current template no
longer imports a local configuration notebook. The legacy `setup_notebook()`
helper is deprecated. See the [central setup and migration guide](../docs/guided-demo/00B-configure-environment-and-load-assets.md).

For token mapping reuse, pass the persisted mapping as `orchestrate_write(existing_mapping=...)` and retain `result["sensitive_result"]["support_mapping"]` for later runs. Live can reuse and insert assignments in a separately configured restricted token vault. Testing never inserts mapping assignments.

Schema presence/datatype violations and configured Sensitive Data treatment failures block. Grain, Freshness, Source Drift, and DQ retain their authored Warn/Block policies. Each configured Guardrail owns its continuation decision; intentionally disabled checks do not impose additional requirements. Foundational physical I/O and `profile_table()` remain public standalone utilities.

Configuration stays immutable during a pipeline. Orchestrators validate the
registered mapping before execution and finalization rechecks identity and
registration consistency. After finalization, approved defaults remain available
for independent profiling/IO; explicit independent contexts are also accepted.
See the [execution modes and completion limits](../templates/notebooks/README.md#pipeline-execution-mode).

Until immutable mapping-dependency identity is supported, caller-owned/configured token-mapping candidates remain diagnostic-only and cannot be activated. For internal caller-owned mapping management, after consuming the prepared DataFrame and persisting a returned mapping, release its cache with `result["sensitive_result"]["support_mapping"].unpersist()`. Failed orchestration releases token caches automatically.

### Contract-driven Guardrails migration

Data Contract → Configured Guardrails → Testing/Live Execution → Results.

`orchestrate_write()` no longer returns `coverage_result` or runs a separate Coverage Gate stage. Read and Write use the context-local execution established by setup. Source Read rules must produce exact-plan, exact-contract results before a Live Write can consume them. Empty rule lists and `is_active=False` optional definitions are valid; they do not require a minimum number of checks. Existing Schema and Sensitive Data Block policies and all Warn/Block actions are unchanged.

Canonical existing Data Contracts need no rewrite. Payloads containing legacy `coverage_gate`, `coverage_policy`, `coverage_gate_policy` or `guardrail_coverage` settings are rejected with migration guidance rather than silently ignored. Create a new draft, express every required protection as an enabled Guardrail, remove obsolete settings, then freeze, test and activate the new version. Never edit a frozen payload. A legacy coverage Guardrail entry is unsupported and must likewise be replaced in a new version. Test Read and Write do not commit data or operational metadata; explicit finalization publishes run and Guardrail results.

Expand the Data Contract selector's sections to inspect columns/types, Grain keys, individual DQ rules and all saved policies and states. The execution report refreshes automatically as the session runs. Saved definitions alone are not execution results.
