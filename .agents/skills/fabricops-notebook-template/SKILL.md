---
name: FabricOps Notebook Template
description: Use when creating, updating, or reviewing FabricOps notebook templates under templates/notebooks.
---

# FabricOps Notebook Template Skill

## Purpose

Guide notebook template work so templates remain public-safe, understandable, Microsoft Fabric aware, and clearly separated from the formal FabricOps package release contract.

## When to use this skill

Use this skill for creating, editing, reviewing, or validating notebooks under `templates/notebooks/` or documentation that directly instructs maintainers how to manage notebook templates.

Do not use this skill for package implementation changes unless the notebook task also requires a public FabricOps API change.

## Context to inspect

- `AGENTS.md`, especially "Notebook template change", "Metadata lakehouse routing", "Public safety and positioning", and generated-artifact rules.
- Existing notebooks in `templates/notebooks/`.
- User-facing template guidance in `docs/notebook-templates.md` and relevant guided demo pages in `docs/guided-demo/`.
- Public API reference pages under `docs/api/reference/` before using a FabricOps callable in a template.
- `src/fabricops_kit/__init__.py` and public package exports when checking that a template uses public APIs only.
- Existing notebook template tests under `tests/templates/`.

## Implementation workflow

1. Define Context, Task, Constraints, Expected output, and Verification.
2. Treat templates as applications of FabricOps, not release-frozen package artifacts.
3. Use public FabricOps APIs only; avoid internal package imports, private helpers, generated metadata internals, or test-only helpers.
4. Keep notebooks executable block by block in Microsoft Fabric and understandable for junior engineers.
5. Reuse canonical defaults and public helpers from `src/fabricops_kit/` instead of duplicating constants or metadata-routing logic inline.
6. Avoid duplicating long explanations already maintained in guided demos or the template implementation guide; link to canonical docs when useful.
7. Include or preserve a concise "Tested with FabricOps" record when the task touches template validation status. It should contain version, date, and tester.
8. Claim Microsoft Fabric runtime success only after actual Fabric execution by the named tester. Local Python checks may support compatibility claims but cannot prove Fabric execution.
9. Preserve sample assets only when they are public-safe and genuinely required by the template.

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

## Expected output

Notebook template changes should be limited to `templates/notebooks/`, directly related template tests under `tests/templates/`, and `docs/notebook-templates.md` when needed.

## Verification

Use existing repository checks relevant to template changes:

```bash
uv run pytest tests/templates
uv run python -m compileall src tests
uv run python -m pytest -q
uv run ruff check .
```

When Fabric runtime validation is required, report the Fabric workspace execution as a manual or maintainer-confirmed step with version, date, tester, notebook name, and outcome. Do not fabricate this record.

## Completion report

Report changed notebooks, public APIs used, validation type achieved, FabricOps version compatibility statement, whether actual Fabric runtime testing occurred, and exact commands or manual Fabric evidence used.
