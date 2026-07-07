# Public API contract

`fabricops_kit.public_api.SUPPORTED_PUBLIC_API` is the canonical machine-readable source of truth for the FabricOps Starter Kit release-facing public API boundary. Release documentation, generated references, notebook templates, and validation checks should derive the supported callable set from that tuple instead of maintaining separate hand-written function inventories.

The supported public API contains the notebook-facing functions in `SUPPORTED_PUBLIC_API`. These functions are the stable API surface for release preparation and should remain available through the internal release refactor. When the supported boundary intentionally changes, update `src/fabricops_kit/public_api.py`, the related contract tests, and any release notes together.

Implementation helpers are not part of this stable contract. Shared helpers, private helpers, classes, methods, validators, resolvers, workflows, adapters, and utilities may be reorganized before release without being treated as supported public API. Public function behavior should remain stable through that refactor, and notebook templates should only use functions listed in `SUPPORTED_PUBLIC_API`.

## Maintainer release checks

Before release sign-off, maintainers should:

1. Inspect `fabricops_kit.public_api.SUPPORTED_PUBLIC_API` for the supported callable inventory.
2. Run the public contract tests that import and validate `SUPPORTED_PUBLIC_API`.
3. Confirm notebook templates and public guidance depend only on supported public functions.
4. Use generated API/reference pages for callable details without treating generated pages as the source of truth for the release boundary.

## Supporting maintainer references

Use these pages after confirming the public API release contract:

- [Generated function catalogue](index.md): review public callable docstrings and notebook-facing usage notes generated from source inputs.
- [Public function call-flow dashboard](../assets/public-function-call-flows-dashboard.html): review public API shape, chain depth, fan-out, source Python files, cross-layer warnings, and flattening recommendations.
- [Selected callable inventory](../assets/public-function-call-flows-dashboard.html#selected-public-function-panel): search/filter callable-flow functions, select rows, and export AI refactor packets.
- [Public function architecture](public-function-architecture.md): confirm public, internal, and private helper boundaries before refactoring.
- [Function call graph](../function-call-graph.md): inspect generated callable relationships when reviewing architecture changes.
- [Release management](../development/release-management.md): follow the GitHub-only release process, validation checks, and tagging sequence.
