---
name: FabricOps Docs Maintenance
description: Use when cleaning up, reorganizing, or updating FabricOps documentation without changing package runtime behavior or generated API reference outputs.
---

# FabricOps Documentation Maintenance Skill

## Purpose

Guide documentation cleanup and restructuring so FabricOps keeps one canonical home for each topic, avoids duplicated content, and stays easy to scan on desktop and mobile.

## When to use this skill

Use this skill for docs-only edits under `README.md`, `docs/`, and related MkDocs configuration when the task is cleanup, consolidation, restructuring, readability improvement, or user/maintainer guidance.

Do not use this skill to manually maintain generated callable reference pages, release contract pages, or dashboard output. Use the source metadata or generator that owns those artifacts instead.

## Content classification

Classify the requested content before creating or moving files:

1. Repository landing/navigation: `README.md` or `docs/index.md`.
2. Product definition: `docs/maintainer/product-definition.md` for what FabricOps is, its original product intent, audience, positioning, scope, and product-level boundaries.
3. High-level workflow explanation: `docs/how-fabricops-works.md` for how the complete FabricOps workflow fits together without implementation-level detail.
4. Guided implementation: `docs/guided-demo.md` and `docs/guided-demo/` for what users do, run, configure, and observe when applying FabricOps. Put contextual rationale, design choices, trade-offs, caveats, and edge cases beside the relevant implementation step in focused collapsible blocks when they help users understand why the workflow is designed that way.
5. User implementation guidance not owned by the Guided Demo: `docs/notebook-templates.md` or another existing canonical implementation page.
6. Maintainer procedure: `docs/maintainer/`, except where a more specific ownership rule applies.
7. Generated API reference: source docstrings, `scripts/reference_docs_metadata.py`, and generated files under `docs/api/reference/` or `docs/reference/`.
8. Release-specific reference: `docs/releases/`, `docs/releases/manifests/`, and release generators.

Update the canonical destination for the classification instead of creating another overlapping page.

## Documentation ownership model

Use the reader's question to determine where content belongs:

- **Product Definition — “What is FabricOps?”** Preserve the original product intent, scope, audience, positioning, and boundaries. Do not turn this into an implementation guide.
- **How FabricOps Works — “How does the workflow fit together?”** Explain the complete operating flow at a high level so a reader can understand the system without implementation detail.
- **Guided Demo — “How do I implement and run it, and why does this step work this way?”** Show the practical sequence, user actions, configuration, notebook steps, and expected results. Keep optional rationale, design trade-offs, caveats, and edge cases in collapsible `???` blocks beside the step where the reader encounters them.
- **Function Reference — “What exactly does this callable do?”** Keep exact parameters, return contracts, side effects, failure behaviour, examples, and callable-specific guidance in generated reference documentation.

Cross-link between these layers instead of repeating the same explanation. Overview pages should stay high level, implementation pages should stay actionable while carrying optional contextual rationale, and reference pages should remain exact.

Before creating a new page, confirm that the topic cannot be added cleanly to one of these existing owners. Prefer strengthening an existing canonical page over adding another conceptual layer.

## Documentation readability pattern

Human-facing documentation should be easy to scan before it is read in detail. Prefer a consistent page rhythm:

1. Page title.
2. One short lead sentence that explains the purpose or outcome.
3. A diagram, table, or compact summary where it genuinely helps.
4. Short sections with descriptive `##` and `###` headings.
5. Focused callouts for important rules, warnings, or notes.
6. Collapsible secondary detail when useful but not required for the main flow.
7. A clear next action or related page near the end.

Use these patterns deliberately:

- Start major sections with a short **bold summary sentence** when it helps readers understand the point before reading details.
- Keep paragraphs compact. If a paragraph contains multiple responsibilities, stages, or decisions, split it into subsections, bullets, or a table.
- Prefer descriptive headings such as `## Engineering Production` over unlabeled transitions buried inside prose.
- Use Material admonitions such as `!!! note`, `!!! important`, and `!!! warning` for information that should stand out. Keep them focused and avoid turning every paragraph into a box.
- Use `??? info` or another collapsible detail block for background explanation, rationale, trade-offs, exceptions, troubleshooting, or optional detail that would otherwise interrupt the main reading flow.
- Use tables for comparisons and ownership matrices, not for long narrative content.
- Use numbered steps for actions that must be performed in order.
- Use code blocks for code, commands, paths, and compact flow notation. Do not use code blocks as generic prose callouts.
- Preserve useful diagrams and screenshots, but do not repeat the diagram's full meaning in several paragraphs directly below it.
- End user-facing procedure pages with an `Expected result` or equivalent outcome and a clear `Next` link where appropriate.
- Keep terminology exactly aligned with FabricOps canonical terms such as Governance, Engineering Development, Engineering Production, Project-Specific Consumer, Data Catalogue, Data Profiled, Data Profiled Frequency, Data Lineage, Enrichment, Guardrails, Guardrail Results, Data Agreement, and Data Contract.

### Guided Demo page pattern

Guided Demo action pages should normally follow this structure where applicable:

```text
# Step X: Action

Short purpose or outcome.

## Before you begin
## What to do
## Expected result

Previous / Next
```

Use additional sections only where the step genuinely needs them. Long technical explanation should sit under a descriptive subsection or collapsible block rather than forming a wall of text. Prefer putting design rationale and trade-offs next to the action they explain instead of creating a separate standalone rationale page.

### Maintainer page pattern

Maintainer pages may be more detailed, but should still use strong hierarchy. Keep mandatory rules visible in normal page flow and move optional rationale, examples, or recovery detail into collapsible sections when that makes the procedure easier to follow.

The Release Guide is special: `.agents/skills/fabricops-release/SKILL.md` is the operational source of truth and `docs/maintainer/index.md` is synchronised from it. Do not independently beautify or rewrite `docs/maintainer/index.md`. Update the release skill first and use the repository's synchronisation path so the two do not drift.

## Context to inspect

- `AGENTS.md`, especially documentation, generated-artifact, and verification rules.
- `README.md` for concise repository navigation.
- `mkdocs.yml` for current navigation, redirects if present, hooks, and docs plugins.
- Existing pages in `docs/`, especially `docs/how-fabricops-works.md`, `docs/guided-demo.md`, `docs/guided-demo/`, `docs/notebook-templates.md`, `docs/maintainer/`, and `docs/releases/`.
- `docs/maintainer/product-definition.md` before changing product positioning, scope, audience, or product-level intent.
- Source docstrings in `src/fabricops_kit/` and `scripts/reference_docs_metadata.py` before changing generated callable documentation.
- `src/fabricops_kit/config/metadata_schemas.py` and `scripts/generate_individual_function_reference_pages.py` before changing generated metadata table documentation.
- Existing images under `docs/assets/` before deleting or replacing them.
- `.agents/skills/fabricops-release/SKILL.md` before changing the published Maintainer Release Guide.

## Implementation workflow

1. Define Context, Task, Constraints, Expected output, and Verification.
2. Classify the content by reader intent and identify its canonical owner before editing.
3. Search for the existing canonical page or section before adding a new page.
4. Move or consolidate content into the canonical destination; remove duplicate explanations rather than maintaining two copies.
5. Cross-link to implementation or reference detail instead of copying content across documentation layers.
6. Keep the root `README.md` concise and navigation-focused.
7. Treat guided demos as user-facing operating guides and place useful optional rationale beside the relevant action in collapsible detail blocks.
8. Put maintainer-only procedures in `docs/maintainer/` unless a more specific ownership rule applies.
9. Improve scanning with headings, bold lead sentences, compact paragraphs, tables, focused admonitions, and collapsible secondary detail before introducing new custom HTML components.
10. Preserve useful existing images when restructuring pages; remove only assets that are unused, public-safe to remove, and not referenced.
11. Do not touch the homepage or documentation navigation unless the task explicitly requires it or a moved page would break navigation.
12. Update `mkdocs.yml` only when navigation, page paths, or included docs files actually change.
13. For generated callable documentation, update source docstrings or metadata instead of editing generated pages directly.
14. For metadata reference work, inspect `metadata_schemas.py` and the generator first, update schema/ownership source metadata, regenerate, and never manually fix an individual metadata page.
15. Metadata schema pages must not document Spark nullability and must use exact column-level writer ownership rather than generic component labels.
16. Run the metadata-page freshness validation for explicitly scoped metadata generator/reference work and commit only `docs/reference/metadata.md` plus `docs/reference/metadata/*.md`.
17. For the Maintainer Release Guide, update `.agents/skills/fabricops-release/SKILL.md` first and keep the published guide synchronised from that source.

## Constraints

- Do not duplicate explanations across the homepage, Product Definition, How FabricOps Works, Guided Demo, function pages, and maintainer reference.
- Do not create a new conceptual page when an existing documentation owner can hold the topic cleanly.
- Prefer contextual collapsible rationale inside the Guided Demo over a separate standalone solution/rationale page when the design choice is best understood at a specific workflow step.
- Do not create visual noise with excessive cards, admonitions, emojis, or decorative components. FabricOps remains a lightweight starter kit and the documentation should feel lightweight too.
- Do not manually edit generated callable reference pages under `docs/api/reference/`, `docs/reference/index.md`, or dashboard HTML in `docs/assets/public-function-call-flows-dashboard.html` for a docs cleanup PR.
- Do not independently edit `docs/maintainer/index.md` when the intended change belongs to the release workflow source skill.
- Do not change FabricOps package behavior, public APIs, notebook templates, release versions, or generated release contracts unless explicitly requested.
- Keep examples public-safe: no real tenant IDs, workspace IDs, production data, secrets, internal URLs, or production screenshots.

## Expected output

A docs maintenance change should contain only the focused Markdown, image reference, CSS, skill, `AGENTS.md`, or `mkdocs.yml` edits needed for the task. It should not include generated API reference or dashboard diffs unless the PR is explicitly a generated-reference refresh.

## Verification

Run deterministic checks that apply to the change:

```bash
uv run mkdocs build --strict
```

Also review:

- desktop and mobile readability of changed human-facing pages when practical
- internal links in changed Markdown files
- heading hierarchy and table-of-contents usefulness
- documentation ownership: each changed topic has one canonical owner and other layers link instead of duplicating it
- `git diff -- docs/api/reference docs/reference/index.md docs/assets/public-function-call-flows-dashboard.html` to confirm generated API pages and dashboard output were not unintentionally modified
- `git diff -- README.md docs mkdocs.yml AGENTS.md .agents/skills/fabricops-docs-maintenance/SKILL.md` for duplicated explanations or unintended navigation changes
- release-skill and published-release-guide synchronisation when the release guide is in scope

## Completion report

Report the content classification, canonical pages changed, readability patterns applied, whether navigation changed, whether generated files were avoided, whether release-guide synchronisation was involved, and the exact validation commands and results.
