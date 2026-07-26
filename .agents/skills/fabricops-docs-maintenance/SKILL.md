---
name: FabricOps Docs Maintenance
description: Use when cleaning up, reorganizing, or updating FabricOps documentation without changing package runtime behavior or generated API reference outputs.
---

# FabricOps Documentation Maintenance Skill

## Purpose

Guide documentation cleanup and restructuring so FabricOps keeps one canonical home for each topic and avoids duplicating generated or maintained content.

## When to use this skill

Use this skill for docs-only edits under `README.md`, `docs/`, and related MkDocs configuration when the task is cleanup, consolidation, restructuring, or user/maintainer guidance.

Do not use this skill to manually maintain generated callable reference pages, release contract pages, or dashboard output. Use the source metadata or generator that owns those artifacts instead.

## Content classification

Classify the requested content before creating or moving files:

1. Repository landing/navigation: `README.md` or `docs/index.md`.
2. User implementation guidance: `docs/how-fabricops-works.md` or `docs/notebook-templates.md`.
3. Guided demonstration: `docs/guided-demo.md` or `docs/guided-demo/`.
4. Maintainer procedure: `docs/maintainer/`.
5. Generated API reference: source docstrings, `scripts/reference_docs_metadata.py`, and generated files under `docs/api/reference/` or `docs/reference/`.
6. Release-specific reference: `docs/releases/`, `docs/releases/manifests/`, and release generators.

Update the canonical destination for the classification instead of creating another overlapping page.

## Context to inspect

- `AGENTS.md`, especially "Documentation and API reference rules", "Generated reference artifacts and Codex runs", and "What to update when changing X".
- `README.md` for concise repository navigation.
- `mkdocs.yml` for current navigation, redirects if present, hooks, and docs plugins.
- Existing pages in `docs/`, especially `docs/how-fabricops-works.md`, `docs/guided-demo.md`, `docs/guided-demo/`, `docs/notebook-templates.md`, `docs/maintainer/`, and `docs/releases/`.
- Source docstrings in `src/fabricops_kit/` and `scripts/reference_docs_metadata.py` before changing generated callable documentation.
- `src/fabricops_kit/config/metadata_schemas.py` and `scripts/generate_individual_function_reference_pages.py` before changing generated metadata table documentation.
- Existing images under `docs/assets/` before deleting or replacing them.

## Implementation workflow

1. Define Context, Task, Constraints, Expected output, and Verification.
2. Search for the existing canonical page or section before adding a new page.
3. Move or consolidate content into the canonical destination; remove duplicate explanations rather than maintaining two copies.
4. Keep the root `README.md` concise and navigation-focused.
5. Treat guided demos as user-facing operating guides where appropriate.
6. Put maintainer-only procedures in `docs/maintainer/`.
7. Preserve useful existing images when restructuring pages; remove only assets that are unused, public-safe to remove, and not referenced.
8. Do not touch the homepage or documentation navigation unless the task explicitly requires it or a moved page would break navigation.
9. Update `mkdocs.yml` only when navigation, page paths, or included docs files actually change.
10. For generated callable documentation, update source docstrings or metadata instead of editing generated pages directly.
11. For metadata reference work, inspect `metadata_schemas.py` and the generator first, update schema/ownership source metadata, regenerate, and never manually fix an individual metadata page.
12. Metadata schema pages must not document Spark nullability and must use exact column-level writer ownership rather than generic component labels.
13. Run the metadata-page freshness validation for explicitly scoped metadata generator/reference work and commit only `docs/reference/metadata.md` plus `docs/reference/metadata/*.md`.

## Constraints

- Do not duplicate explanations across the homepage, implementation guide, guided demos, function pages, and maintainer reference.
- Do not manually edit generated callable reference pages under `docs/api/reference/`, `docs/reference/index.md`, or dashboard HTML in `docs/assets/public-function-call-flows-dashboard.html` for a docs cleanup PR.
- Do not change FabricOps package behavior, public APIs, notebook templates, release versions, or generated release contracts unless explicitly requested.
- Keep examples public-safe: no real tenant IDs, workspace IDs, production data, secrets, internal URLs, or production screenshots.

## Expected output

A docs maintenance change should contain only the focused Markdown, image reference, or `mkdocs.yml` edits needed for the task. It should not include generated API reference or dashboard diffs unless the PR is explicitly a generated-reference refresh.

## Verification

Run deterministic checks that apply to the change:

```bash
uv run mkdocs build --strict
```

Also review:

- internal links in changed Markdown files
- `git diff -- docs/api/reference docs/reference/index.md docs/assets/public-function-call-flows-dashboard.html` to confirm generated API pages and dashboard output were not unintentionally modified
- `git diff -- README.md docs mkdocs.yml` for duplicated explanations or unintended navigation changes

## Completion report

Report the content classification, canonical pages changed, whether navigation changed, whether generated files were avoided, and the exact validation commands and results.
