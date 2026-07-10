# Public API & Architecture

Use this page as the maintainer technical reference for the supported public API boundary, callable architecture, and call-flow artifacts. The [Release Guide](index.md) owns the release checklist; this page owns the architecture review details used during release validation and implementation cleanup.

## Supported public API boundary

`fabricops_kit.public_api.SUPPORTED_PUBLIC_API` is the canonical machine-readable release boundary for notebook-facing public callables.

Maintainers should verify that:

1. release-facing functions are listed in `SUPPORTED_PUBLIC_API`;
2. adding a function to Python source alone does not make it release-facing;
3. notebook templates and public guidance import supported functions from the root package where appropriate;
4. public exports are intentional in package `__init__.py` files and in `src/fabricops_kit/__init__.py` when the root API should expose them; and
5. generated references are review aids, not the source of truth for the public boundary.

## Public function architecture

FabricOps uses a small, predictable package pattern for public callable functions:

- one public owner file named after the function
- one package `shared.py` for helpers, support classes, dataclasses, constants, and value objects
- one package `__init__.py` for exports
- root exports only for notebook-facing supported public API

Avoid catch-all files such as `public.py`, `models.py`, `classes.py`, `adapter.py`, `adapters.py`, `resolver.py`, or `resolvers.py` unless explicitly approved.

Architecture review should confirm that release changes do not introduce public-to-public calls, internal-to-public calls, cross-file private helper dependencies, or private helpers surfaced as public/internal architecture layers.

## Callable architecture contract

`docs/reference/_data/public-function-call-flows.json` is the committed callable architecture contract. Use it to inspect public callable scopes, direct and transitive callees, helper reachability, source locations, architecture violations, cleanup/refactor signals, and defined-but-not-used functions.

Source code remains authoritative. If the JSON disagrees with source, fix the source inputs or generator and regenerate the contract instead of hand-editing the JSON.

Run the call-flow JSON generator when function-level source changes affect callable structure, source locations, public exports, helper relationships, architecture classification, or public function flow metrics:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
```

Commit the regenerated `docs/reference/_data/public-function-call-flows.json` only when the committed architecture contract is intentionally affected.

## Function references and dashboard

Use these generated review surfaces when validating public API and architecture changes:

- [Function Reference](../reference/index.md): generated public callable catalogue from source metadata and docstrings.
- [Call Graph Dashboard](../assets/public-function-call-flows-dashboard.html): interactive view of callable flow, architecture signals, selected callable review, and AI cleanup packet export.
- [Function Call Graph](../function-call-graph.md): maintainer guide for the call-flow review workflow.
- [Call-flow JSON contract](../reference/_data/public-function-call-flows.json): compact committed architecture contract for agent planning and review.

Run individual function references before an actual release preparation or an explicit generated-reference refresh:

```bash
PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
```

Run the dashboard generator only when intentionally refreshing the published dashboard:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_dashboard.py
```

Do not manually edit generated function pages, dashboard HTML, or call-flow JSON as source of truth. Update source inputs or generator logic first, then regenerate the owned artifact.
