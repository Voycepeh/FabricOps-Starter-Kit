---
name: FabricOps Public API Change
description: Use when adding, changing, promoting, deprecating, removing, refactoring, or reviewing callable-level source under src/fabricops_kit.
---

# FabricOps Public API Change Skill

## Purpose

Guide focused callable-level source changes while applying the repository contracts in `AGENTS.md`.

Lifecycle determines compatibility. Live public callables are backward-compatible by default and their observable contracts must be preserved unless the task explicitly authorizes a breaking change. Preview callables may change cleanly without compatibility wrappers or transitional shims unless migration support is explicitly requested. Discontinued callables do not imply current compatibility support.

Do not use this skill for docs-only wording, release-only presentation, or notebook template edits unless function-level package source also changes.

## Context to inspect

Start with `AGENTS.md`, the owner source file, and targeted tests. Retrieve callable context without reading the entire generated contract:

```bash
python scripts/query_public_function_call_flow.py <qualified_name>
python scripts/query_public_function_call_flow.py <qualified_name> --depth 2 --callers
```

Add `src/fabricops_kit/public_api.py`, exports, shared helpers, and `scripts/reference_docs_metadata.py` only when the requested change affects those boundaries. Use deeper graph traversal only when necessary. Source and exports, not generated JSON, determine actual behavior.

## Workflow

1. Classify the callable as Live, Preview, Discontinued, Internal, or Private before deciding compatibility requirements. For Live callables, identify the existing observable contract before editing. For Preview, Internal, or Private callables, do not preserve obsolete structure merely for backwards compatibility.
2. Identify the smallest valid owner-file seam and reuse existing shared helpers.
3. Inspect the observable contract and current call flow. Use the targeted callable lookup and expand its depth only when the downstream scope is relevant. Check whether a physical read/write is genuinely reusable/user-facing or only workflow-specific.
4. Implement only the required source change. Route genuinely reusable physical reads/writes through foundational I/O owner functions; keep niche workflow-specific I/O and domain-specific mutations with their owning domain when that is the clearer implementation.
5. Update exports, docstrings, reference metadata, and tests only when affected.
6. For a new or modified Live callable, compare the docstring with the implementation and cover behaviour, side effects, return interpretation, failure behaviour, runtime assumptions, and a valid example. Preview callable documentation may remain lighter unless the callable is being promoted.
7. Regenerate `docs/reference/_data/public-function-call-flows.json` only when the committed architecture contract changes. If the contract changes, retain both the changed call-flow JSON and the corresponding `public_function_call_flows_json` timestamp entry in `docs/reference/_data/generated-artifacts.json`. If the contract does not change, restore timestamp-only noise unless the task explicitly requests a timestamp refresh.
8. Run `PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py` and commit meaningful changes to `docs/api/reference/*.md`, `docs/reference/index.md`, and `docs/reference/function-call-graph.md` when the source, docstring, export, call flow, reference metadata, or generator change affects them. Do not regenerate them when the change cannot affect their content, and never edit them manually.
9. When individual reference artifacts are regenerated, run the generator a second time and confirm that it produces no diff.
10. Review the diff for unrelated generated artifacts, dashboard output, architecture violations, compatibility shims, or timestamp-only noise.
11. Report lifecycle, contract impact, changed files, verification, whether affected individual reference artifacts were committed, and whether the timestamp manifest was committed alongside an intentional contract refresh.

Follow the architecture, compatibility, generated-artifact, and public-safety rules in `AGENTS.md`; do not restate or override them here.

## Expected output

Change only files required by the task, typically:

- callable owner or package `shared.py`
- package exports when the public surface changes
- `scripts/reference_docs_metadata.py` when reference metadata changes
- targeted tests
- affected `docs/api/reference/*.md` pages when individual reference generation produces meaningful changes
- `docs/reference/index.md` and `docs/reference/function-call-graph.md` when individual reference generation produces meaningful changes
- `docs/reference/_data/public-function-call-flows.json` only when its contract changes
- `docs/reference/_data/generated-artifacts.json` only for the corresponding `public_function_call_flows_json` timestamp when the call-flow contract intentionally changes or the task explicitly requests a timestamp refresh

Affected generated individual reference artifacts are normal outputs of the source PR that changes their authoritative inputs. The dashboard HTML remains separately owned and must not be regenerated or committed in an ordinary backend or source PR unless that PR directly changes the dashboard frontend or its published output contract.

## Verification

Run targeted tests, Ruff and an appropriate syntax check. Regenerate only artifacts affected by the source change as directed by `AGENTS.md`, and run the individual reference generator twice whenever those pages change. Review the diff before opening the PR.

## Completion report

Report the lifecycle and public-contract impact, changed source and generated files, validation results, and whether the architecture JSON and matching timestamp changed.
