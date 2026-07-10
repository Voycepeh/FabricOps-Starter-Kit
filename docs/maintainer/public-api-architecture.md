# Public API & Architecture

Use this page to review the public API boundary and callable architecture before shipping a FabricOps release. Keep the source code, public API metadata, and generated call-flow contract as the source inputs; use generated pages and dashboards as review aids.

## Public API Contract

`fabricops_kit.public_api.SUPPORTED_PUBLIC_API` is the canonical machine-readable release boundary for notebook-facing public callables.

Before release sign-off:

1. Inspect `fabricops_kit.public_api.SUPPORTED_PUBLIC_API` for the supported callable inventory.
2. Run the contract tests that import and validate that inventory.
3. Confirm notebook templates and public guidance depend only on supported public functions.
4. Use generated callable pages for details, but do not treat generated pages as the source of truth for the release boundary.

## Public Function Architecture

FabricOps uses a small, predictable package pattern for new public callable functions:

- one public owner file named after the function
- one package `shared.py` for helpers, support classes, dataclasses, constants, and value objects
- one package `__init__.py` for exports
- root exports only for notebook-facing supported public API

Avoid catch-all files such as `public.py`, `models.py`, `classes.py`, `adapter.py`, `adapters.py`, `resolver.py`, or `resolvers.py` unless explicitly approved.

## Review links

- [Function Reference](../reference/index.md): generated public callable catalogue.
- [Call Graph Dashboard](../assets/public-function-call-flows-dashboard.html): callable flow, architecture signals, selected callable review, and AI cleanup packet export.
- [Function Call Graph](../function-call-graph.md): maintainer guide for the call-flow review workflow.
- [Call-flow JSON contract](../reference/_data/public-function-call-flows.json): committed architecture contract used by the dashboard.

## Architecture checks

Use the call-flow dashboard and tests to check that release changes do not introduce public-to-public calls, internal-to-public calls, cross-file private helper dependencies, or private helpers surfaced as public/internal architecture layers.
