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
7. Regenerate `docs/reference/_data/public-function-call-flows.json` only when the committed architecture contract changes.
8. Review the diff for unrelated generated artifacts, architecture violations, or compatibility shims.
9. Report lifecycle, contract impact, changed files, verification, and any separate generated refresh still required.

Follow the architecture, compatibility, generated-artifact, and public-safety rules in `AGENTS.md`; do not restate or override them here.

## Expected output

Change only files required by the task, typically:

- callable owner or package `shared.py`
- package exports when the public surface changes
- `scripts/reference_docs_metadata.py` when reference metadata changes
- targeted tests
- `docs/reference/_data/public-function-call-flows.json` only when its contract changes

Generated individual function pages and dashboard HTML are not normal source-PR outputs.

## Verification

Use checks proportional to the change:

- Run targeted tests for the changed callable or domain first.
- Run broader tests only when shared behaviour or architecture requires them.
- Run Ruff on affected files or the relevant scope when practical.
- Run `compileall`, an import check, or another focused syntax check.
- Regenerate `public-function-call-flows.json` only when its architecture contract changes.
- For docstring-only changes, use the smallest syntax or import check and do not regenerate architecture or individual reference artifacts.

Review the final diff before completion.

## Completion report

State:

- lifecycle and public contract impact
- files changed
- whether call-flow JSON was regenerated
- verification commands and results
- any separate generated refresh still required
