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

Migrate notebooks to the orchestrator calls in `templates/notebooks/02_pipeline.ipynb`. Keep transformations between Read and Write. Read check results come back under `freshness_result`, `schema_result`, and `dq_result`; Write also returns `sensitive_result`, `source_drift_results`, and `coverage_result`. Blocking stages stop later stages before publication. Development without a selected contract retains its existing baseline behavior.

For token mapping reuse, pass the persisted mapping as `orchestrate_write(existing_mapping=...)` and retain `result["sensitive_result"]["support_mapping"]` for later runs. FabricOps never persists raw token mappings automatically.

Schema presence/datatype violations and configured Sensitive Data treatment failures block. Freshness, Source Drift, and DQ retain their authored Warn/Block policies. Guardrail Coverage remains a mandatory publication-readiness gate. Foundational physical I/O and `profile_table()` remain public standalone utilities.

Each orchestration call resolves its contracts and active rules once. Only applicable Guardrails execute or print stage output. A contract-free Development run prints one decision and proceeds to Read or Write; skipped result fields remain available for inspection. Validate evaluates the exact selected frozen candidate and records `execution_type="validate"` outcomes for activation.

After consuming the prepared DataFrame and persisting a returned token mapping, release its cache with `result["sensitive_result"]["support_mapping"].unpersist()`. Failed orchestration releases token caches automatically.
