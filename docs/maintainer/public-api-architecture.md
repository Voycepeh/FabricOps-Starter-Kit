# Public API & Architecture

**Use this page to review the supported public API boundary, callable architecture, and generated call-flow artifacts.**

The [Release Guide](index.md) owns release procedure. This page owns architecture review details used during implementation cleanup and release validation.

## Supported public API boundary

`fabricops_kit.public_api.SUPPORTED_PUBLIC_API` is the canonical machine-readable boundary for notebook-facing supported public callables.

Maintainers should verify that:

1. release-facing functions are listed in `SUPPORTED_PUBLIC_API`
2. adding a function to Python source alone does not make it release-facing
3. notebook templates and public guidance import supported functions from the root package where appropriate
4. public exports are intentional in package `__init__.py` files and in `src/fabricops_kit/__init__.py` when the root API should expose them
5. generated references are review surfaces rather than the source of truth for the public boundary

!!! important "Public boundary rule"

    A callable is not part of the supported release boundary merely because it exists in source. The supported registry and intentional exports define what is public-facing.

## Public function architecture

**Keep public callable structure small and predictable.**

FabricOps uses this package pattern:

- one public owner file named after the function
- one package `shared.py` for reusable helpers and supporting objects
- one package `__init__.py` for exports
- root exports only for notebook-facing supported public API

Avoid catch-all files such as `public.py`, `models.py`, `classes.py`, adapter files, or resolver files unless explicitly approved.

### Architecture checks

Architecture review should confirm that changes do not introduce:

- public-to-public calls
- internal-to-public calls
- cross-file private helper dependencies
- private helpers surfaced as Public or Internal architecture layers

## Callable architecture contract

`docs/reference/_data/public-function-call-flows.json` is the committed callable architecture contract.

Use it to inspect:

- public callable scope and owner file
- direct and transitive callees
- helper reachability
- source locations
- architecture violations
- cleanup and refactor signals
- defined-but-not-used functions

!!! note "Source remains authoritative"

    If the JSON disagrees with source, fix the source inputs or generator and regenerate the contract. Do not hand-edit the JSON as the fix.

Run the call-flow generator when a source change affects callable structure, source locations, public exports, helper relationships, architecture classification, or public function flow metrics:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
```

Commit the regenerated JSON only when the architecture contract is intentionally affected.

## Review surfaces

| Surface | Purpose |
| --- | --- |
| [Function Reference](../reference/index.md) | Generated public callable catalogue from source metadata and docstrings. |
| [Call Graph Dashboard](../assets/public-function-call-flows-dashboard.html) | Interactive callable flow and architecture review. |
| [Function Call Graph](../function-call-graph.md) | Maintainer guide for the call-flow review workflow. |
| [Call-flow JSON contract](../reference/_data/public-function-call-flows.json) | Compact committed architecture contract for agent planning and review. |

## Regeneration commands

### Individual function references

Run before an actual release preparation or explicit generated-reference refresh:

```bash
PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
```

### Dashboard

Run only when intentionally refreshing the published dashboard:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_dashboard.py
```

!!! warning "Do not repair generated artifacts by hand"

    Do not manually edit generated function pages, dashboard HTML, or call-flow JSON as source of truth. Update source inputs or generator logic first, then regenerate the owned artifact.
