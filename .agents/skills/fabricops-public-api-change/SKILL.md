---
name: FabricOps Public API Change
description: Use when adding, changing, promoting, refactoring, or reviewing a FabricOps callable or function-level implementation in src/fabricops_kit.
---

# FabricOps Public API Change Skill

## Purpose

Guide focused changes to FabricOps callable source code while preserving the repository architecture contract in `AGENTS.md` and the committed public call-flow data in `docs/reference/_data/public-function-call-flows.json`.

## When to use this skill

Use this skill for work that adds, changes, promotes, deprecates, removes, or refactors a callable in `src/fabricops_kit/`, including public notebook-facing APIs, architecture-visible internal helpers, private helpers, package exports, public API metadata, and generated call-flow contract inputs.

Do not use this skill for docs-only wording, release-only presentation, or notebook template edits unless those tasks also change function-level package source.

## Context to inspect

Before editing, inspect the relevant repository sources instead of relying on memory:

- `AGENTS.md`, especially "Backward compatibility and public contracts", "Function architecture rules", "Agent public call flow architecture contract", "Public callable package file pattern", and "Public API docstring requirements".
- `docs/reference/_data/public-function-call-flows.json` for the callable scope, owner file, direct and transitive callees, architecture violations, cleanup signals, and defined-but-not-used functions.
- `src/fabricops_kit/public_api.py` for release-facing public API lifecycle status.
- `src/fabricops_kit/__init__.py` and the package `__init__.py` files for exported names.
- The current owner file in `src/fabricops_kit/` and any existing `shared.py` in the same domain before creating a new helper path.
- `scripts/reference_docs_metadata.py` when public callable reference metadata or categorisation changes.
- Existing tests under `tests/` that cover the callable, domain, public API contract, or architecture guardrails.

## Implementation workflow

1. Classify the callable as Live, Preview, Discontinued, Internal, or Private using `src/fabricops_kit/public_api.py`, exports, docstrings, tests, and the call-flow JSON.
2. Define the five task items: Context, Task, Constraints, Expected output, and Verification.
3. Identify the owner file and reuse existing shared helpers before creating a new file or abstraction.
4. Preserve the observable contract of Live callables unless the task explicitly authorizes a breaking change. Observable contract includes import path, exported name, parameters, accepted inputs, return shape, side effects, persisted outputs, exceptions, and documented behavior.
5. For new public callables, follow the owner-file pattern from `AGENTS.md`: one public owner file named after the function, one package `shared.py` for reusable implementation objects, and `__init__.py` for exports.
6. Keep architecture layers clean: public functions must not call public functions, and internal functions must not call public functions.
7. Avoid compatibility wrappers, aliases, adapter layers, legacy parameter names, or transitional shims unless migration support is explicitly requested.
8. Update source, exports, docstrings, tests, and `scripts/reference_docs_metadata.py` together when the public contract, source location, or reference metadata changes.
9. Regenerate `docs/reference/_data/public-function-call-flows.json` when required by `AGENTS.md`.
10. Do not commit generated individual function pages in `docs/api/reference/` or dashboard HTML in `docs/assets/public-function-call-flows-dashboard.html` for an ordinary source PR.

## Constraints

- Do not manually edit generated reference outputs as source of truth.
- Do not add public-to-public or internal-to-public calls.
- Do not surface private underscore helpers as Internal functions.
- Do not include private helpers in Public API Surface KPI counts.
- Do not change notebook-facing behavior accidentally; document intentional breaking changes clearly.
- Do not create duplicate helper modules or resolver layers when an owner file or domain `shared.py` already exists.

## Expected output

A completed public API change includes only the files required by the task, usually one or more of:

- `src/fabricops_kit/**/*.py`
- `src/fabricops_kit/__init__.py`
- `scripts/reference_docs_metadata.py`
- targeted tests under `tests/`
- `docs/reference/_data/public-function-call-flows.json` when the committed call-flow contract changes

## Verification

Run checks appropriate to the change. For normal source PRs, the repository minimum is:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
uv run python -m compileall src tests
uv run python -m pytest -q
uv run ruff check .
```

Also run targeted tests for the changed callable or domain when available. Review the final diff to confirm generated individual function pages, dashboard HTML, release pages, and notebook templates were not changed unless explicitly in scope.

## Completion report

In the PR summary, state:

- callable lifecycle classification and whether any public contract changed
- owner files and tests updated
- whether `docs/reference/_data/public-function-call-flows.json` was regenerated
- any generated docs refresh that should happen later rather than in this PR
- exact verification commands and results
