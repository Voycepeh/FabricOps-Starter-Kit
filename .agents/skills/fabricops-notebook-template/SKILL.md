---
name: FabricOps Notebook Template
description: Use when creating, updating, or reviewing FabricOps notebook templates under templates/notebooks.
---

# FabricOps Notebook Template Skill

## Purpose

Guide all living standard notebook template work so templates remain public-safe, understandable, Microsoft Fabric aware, and clearly separated from the formal FabricOps package release contract.

This skill owns the current standard templates under `templates/notebooks/`, including `00_env_config`, `01_governance`, `02_pipeline`, and `99_explore`. The release workflow has a narrower responsibility: it freezes and publishes only the notebook templates explicitly included in the release snapshot contract.

## When to use this skill

Use this skill for creating, editing, reviewing, or validating notebooks under `templates/notebooks/` or documentation that directly instructs maintainers how to manage notebook templates.

Do not use this skill for package implementation changes unless the notebook task also requires a public FabricOps API change.

## Context to inspect

- `AGENTS.md`, especially "Notebook template change", "Metadata lakehouse routing", "Public safety and positioning", and generated-artifact rules.
- Existing notebooks in `templates/notebooks/`.
- User-facing template guidance in `templates/notebooks/README.md` and relevant guided demo pages in `docs/guided-demo/`.
- Public API reference pages under `docs/api/reference/` before using a FabricOps callable in a template.
- `src/fabricops_kit/__init__.py` and public package exports when checking that a template uses public APIs only.
- Existing notebook template tests under `tests/templates/`.

## Implementation workflow

1. Define Context, Task, Constraints, Expected output, and Verification.
2. Treat all notebooks under `templates/notebooks/` as evolving latest templates. Preserve each notebook's existing responsibility: `00_env_config` for environment/runtime configuration, `01_governance` for governance authoring and review, `02_pipeline` for governed pipeline execution, and `99_explore` for consumer exploration. Do not assume that release snapshot eligibility defines notebook-template ownership.
3. At each FabricOps release, the release skill freezes only `00_env_config.ipynb` and `02_pipeline.ipynb` under `templates/releases/vX.Y.Z/` unless the release snapshot contract is explicitly changed.
4. Use public FabricOps APIs only; avoid internal package imports, private helpers, generated metadata internals, or test-only helpers. For ordinary Fabric table/file reads and writes, use the public foundational I/O functions instead of raw Spark/connector/path persistence when FabricOps provides the operation.
5. Keep notebooks executable block by block in Microsoft Fabric and understandable for junior engineers.
6. Reuse canonical defaults and public helpers from `src/fabricops_kit/` instead of duplicating constants or metadata-routing logic inline.
7. Avoid duplicating long explanations already maintained in guided demos or the template implementation guide; link to canonical docs when useful.
8. Include or preserve a concise "Tested with FabricOps" record when the task touches template validation status. It should contain version, date, and tester.
9. Claim Microsoft Fabric runtime success only after actual Fabric execution by the named tester. Local Python checks may support compatibility claims but cannot prove Fabric execution.
10. Preserve sample assets only when they are public-safe and genuinely required by the template.

## Standard 02 pipeline migration contract

Treat `02_pipeline.ipynb` as a cloneable bootstrap that users own after copying it. FabricOps owns the scaffold and package behaviour; projects own the configuration values and transformation logic they place into the scaffold.

Preserve these migration surfaces across routine template changes:

- Keep the top-level flow ordered as Environment → Data Contract → Read → Transform → Write.
- Use each `orchestrate_read()` call itself as the source configuration surface. Keep source choices explicit as call arguments rather than duplicating them into `READ_*` passthrough variables.
- Use each `orchestrate_write()` call itself as the target configuration surface. Keep target choices explicit as call arguments rather than duplicating them into `WRITE_*` passthrough variables.
- Treat read strategy as a per-source decision and write strategy as a per-target decision. One pipeline may mix full and incremental sources and publish targets with different supported load strategies.
- Keep project transformation logic isolated in the dedicated `transform` cell between Read and Write. Do not bury project transformation logic inside FabricOps-owned read/write scaffolding.
- Keep FabricOps-owned engine behaviour behind public `fabricops_kit` APIs. Do not grow private framework implementations inline in the notebook when the behaviour belongs in the package.
- Preserve stable cell IDs for the standard migration surfaces unless a deliberate migration-contract change requires otherwise.

- Keep optional `display()` calls outside orchestration and keep the Transform cell free of orchestration calls.
- Do not reconstruct the standard Read or Write stage sequence inline; the canonical standard template calls `orchestrate_read()` and `orchestrate_write()`.

The goal is not to freeze notebook presentation or exact cell contents. Maintainers may improve explanations, examples, public API calls, and scaffold implementation. The invariant is that a user or coding assistant can migrate an existing pipeline to a newer template by identifying the orchestrator configuration calls and dedicated transformation cell, then reviewing the resulting pipeline before execution.

A change that moves or mixes these user-owned surfaces is a migration-contract change. Keep it explicit, justify it in the PR, and update the structural contract tests intentionally rather than weakening them.

## Validation types

Distinguish three validation levels in reports and notebook wording:

- Local structural validation: parsing notebooks, checking cells, linting extracted code where applicable, and running repository tests that do not require Fabric.
- Package/API compatibility validation: confirming the template imports supported public APIs and matches the intended FabricOps version or version range.
- Actual Microsoft Fabric runtime validation: executing the notebook in Microsoft Fabric with configured workspace, lakehouse/warehouse, environment, and metadata targets.

Do not describe local structural validation or package/API compatibility validation as actual Microsoft Fabric testing.

## Constraints

- Do not change FabricOps public API behavior to make a template easier unless the PR is explicitly scoped for a package change.
- Do not import from private modules or underscore-prefixed helpers in templates.
- Do not hardcode tenant IDs, workspace IDs, lakehouse IDs, production paths, secrets, or internal URLs.
- Do not stamp templates as tested for a FabricOps version without actual Fabric execution evidence.
- Do not modify release manifests, release pages, generated function pages, dashboard HTML, or package metadata for a template-only task.
- Never modernize or edit a frozen template snapshot after it is copied from its release tag. The release tag is the authoritative source for that snapshot.

## Expected output

Notebook template changes should be limited to `templates/notebooks/`, directly related template tests under `tests/templates/`, and `templates/notebooks/README.md` when needed.

## Verification

Use checks proportional to the notebook change. Start with the directly affected template tests and structural checks:

```bash
uv run pytest tests/templates
```

Run broader `compileall`, repository-wide pytest, or Ruff only when shared package behaviour, extracted Python, or the scope of the change makes those checks relevant. Do not turn a notebook wording or layout change into an unrelated full-suite requirement.

When Fabric runtime validation is required, report the Fabric workspace execution as a manual or maintainer-confirmed step with version, date, tester, notebook name, and outcome. Do not fabricate this record.

## Completion report

Report changed notebooks, public APIs used, validation type achieved, FabricOps version compatibility statement, whether actual Fabric runtime testing occurred, and exact commands or manual Fabric evidence used.
