---
name: fabricops
description: Repository guidance for AI agents working on governed, quality-checked, AI-ready notebooks in Microsoft Fabric.
---

# FabricOps agent skill

Use this skill when changing FabricOps Starter Kit notebooks, package helpers, metadata workflows, generated reference guidance, or DQ rule behavior.

## Source of truth

- Treat `00_env_config` as the owner of environment setup and configured metadata/lakehouse targets.
- Use `docs/reference/agent-manifest.json`, `docs/reference/function-manifest.json`, `docs/reference/callables/`, and `docs/reference/internal/` before changing or recommending helpers.
- Use `docs/reference/dq-rules/` for supported DQ rule names, parameters, and examples.
- Do not duplicate generated callable lists or generated DQ catalogue content in hand-written docs.

## Operating rules

- Keep examples generic and public-safe: no secrets, tenant IDs, workspace IDs, internal URLs, real data, or production screenshots.
- Route metadata reads and writes through the configured `metadata` target from `00_env_config`; do not assume an attached/default lakehouse.
- Preserve governance review as a metadata control panel over profiled catalogue output; do not move the DQ catalogue back into `docs/how-fabricops-works/governance-review.md`.
- Prefer existing public helpers and notebook workflows before adding wrappers or new steps.
- Do not invent unsupported DQ rule types, parameters, notebook responsibilities, or enforcement behavior.

## Governance and DQ guidance

- Treat `03_governance` as the metadata control panel that augments catalogue/profile output after `02_pipeline` has written and profiled real tables.
- Keep detailed DQ rule guidance in `docs/reference/dq-rules/index.md`; do not duplicate the full catalogue in workflow pages.
- Remember that approved DQ rules live in `METADATA_DQ_RULES` and are enforced by later `02_pipeline` runs through `enforce_dq_rules`.

## Workflow

For repo-wide or reference-affecting changes, run relevant tests and a strict docs build, typically:

```bash
uv run pytest
uv run mkdocs build --strict
```
