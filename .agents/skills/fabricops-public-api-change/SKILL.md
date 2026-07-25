---
name: FabricOps Public API Change
description: Use when adding, changing, promoting, deprecating, removing, refactoring, or reviewing callable-level source under src/fabricops_kit.
---

# FabricOps Public API Change Skill

## Purpose

Guide focused callable-level source changes while applying the repository contracts in `AGENTS.md`.

Do not use this skill for docs-only wording, release-only presentation, or notebook template edits unless function-level package source also changes.

## Context to inspect

Inspect only the sources relevant to the task:

- `AGENTS.md`
- the target entry in `docs/reference/_data/public-function-call-flows.json`
- `src/fabricops_kit/public_api.py`
- the callable owner file and package `shared.py`
- package exports
- relevant tests
- `scripts/reference_docs_metadata.py` only when reference categorisation, usage notes, or examples change

## Workflow

1. Classify the callable as Live, Preview, Discontinued, Internal, or Private.
2. Identify the smallest valid owner-file seam and reuse existing shared helpers.
3. Inspect the observable contract and current call flow.
4. Implement only the required source change.
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

Use checks proportional to the change:

- Run targeted tests for the changed callable or domain first.
- Run broader tests only when shared behaviour or architecture requires them.
- Run Ruff on affected files or the relevant scope when practical.
- Run `compileall`, an import check, or another focused syntax check.
- Regenerate `public-function-call-flows.json` only when its architecture contract changes.
- Regenerate individual reference artifacts when a source, docstring, export, call-flow, reference-metadata, or generator change affects their generated content.
- When individual reference artifacts are regenerated, run `PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py` a second time and confirm that it produces no diff.
- For docstring-only changes, use the smallest syntax or import check, do not regenerate architecture unless its contract changes, and regenerate individual reference artifacts when the docstring affects their content.

Review the final diff before completion.

## Completion report

State:

- lifecycle and public contract impact
- files changed
- whether affected individual reference artifacts were regenerated and committed, or were not affected
- whether call-flow JSON was regenerated
- whether the timestamp manifest was committed alongside an intentional contract refresh, restored as timestamp-only noise, or refreshed by explicit request
- verification commands and results
