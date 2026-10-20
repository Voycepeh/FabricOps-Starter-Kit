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

Use `orchestrate_read()` and `orchestrate_write()` for governed pipeline execution. The orchestrators own the Read/Write stages, Guardrail evaluation, Sensitive Data treatment, result persistence, and failure decisions.

The standalone `pipeline_read()`, `pipeline_write()`, `check_schema()`, `check_freshness()`, `check_source_drift()`, `check_dq()`, `check_sensitive_data()`, and `check_guardrail_coverage()` entrypoints have been removed from the public API. Their owner modules contain internal implementation stages; they are not supported notebook imports. This intentionally removes the former Live `pipeline_read()` and `pipeline_write()` API contracts without compatibility aliases.

Migrate notebooks to the orchestrator calls in `templates/notebooks/02_pipeline.ipynb`. Keep transformations between Read and Write. Read check results come back under `freshness_result`, `schema_result`, `grain_result`, and `dq_result`; Write also returns `sensitive_result`, `source_drift_results`, and `coverage_result`. Live stops on Block before publication; Testing returns blocking outcomes for inspection. Explicit No Contract permits bootstrap when no active contract is bypassed.

For token mapping reuse, pass the persisted mapping as `orchestrate_write(existing_mapping=...)` and retain `result["sensitive_result"]["support_mapping"]` for later runs. Live can reuse and insert assignments in a separately configured restricted token vault. Testing never inserts mapping assignments.

Schema presence/datatype violations and configured Sensitive Data treatment failures block. Grain, Freshness, Source Drift, and DQ retain their authored Warn/Block policies. Guardrail Coverage remains a mandatory publication-readiness gate. Foundational physical I/O and `profile_table()` remain public standalone utilities.

Create one explicit execution plan with `create_pipeline_execution_plan(execution_mode="testing" or "live", sources=..., targets=..., selections=...)`, or call the widget's `build_plan()`. Pass that same plan to every Read and Write. Environment names only route work. Testing evaluates eligible frozen versions and returns diagnostics with zero durable mutations across every stage. Live enforces active frozen versions and commits approved publication and operational metadata. Testing never registers activation evidence; Governance separately reviews exact in-memory diagnostics and confirms activation.

For Live caller-owned mapping management, after consuming the prepared DataFrame and persisting a returned mapping, release its cache with `result["sensitive_result"]["support_mapping"].unpersist()`. Failed orchestration releases token caches automatically.
