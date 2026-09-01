---
name: fabricops
description: Guides automation tools working on the FabricOps Starter Kit. Use when authoring or reviewing Fabric notebooks, package helpers, metadata and contract workflows, generated function references, DQ rule review or enforcement, or repo changes that must preserve FabricOps governance, 00_env_config routing, and metadata-backed evidence.
---

Use this skill when authoring notebooks, changing package helpers, or reviewing generated references for the FabricOps Starter Kit.

## What this skill is for

This skill guides automation tools working on the FabricOps Starter Kit repository. It is not public user documentation and should not become a replacement for the docs, generated references, source code, or notebook templates. Point agents to the source of truth instead of duplicating full documentation, generated manifests, or rule pages here.

## Reference sources

Start with the existing generated function reference system. Do not replace it with a separate documentation or manifest system.

- `docs/reference/_data/public-function-call-flows.json` — committed normalized public callable architecture contract. `public_functions` contains public-root metrics and lifecycle, `defined_functions` contains one record per callable, and `relationships` contains direct caller-to-callee edges used for helper reachability and graph traversal.
- `docs/assets/public-function-call-flows-dashboard.html` — published dashboard frontend generated from the public call-flow contract for reviewer exploration and AI cleanup packet export. It reconstructs expanded call trees from the normalized relationships at runtime.
- `docs/api/reference/` — generated individual public callable pages for notebook authors and maintainers.
- Public callable pages under `docs/api/reference/` embed internal helper implementation details for package maintenance. Standalone `docs/reference/internal/` pages are generated only when explicitly enabled for maintainer diagnostics.
- `docs/reference/dq-rules/` — generated DQ rule reference pages for supported rule types, parameters, and examples.

## Core operating principles

- Respect `00_env_config`; it owns environment setup and configured runtime targets.
- Use configured metadata targets rather than assuming an attached/default lakehouse.
- Prefer existing helpers before creating wrappers or new workflow steps.
- Do not hardcode Fabric workspace IDs or item IDs unless explicitly provided by the user.
- Do not bypass governed metadata evidence when agreement, review, enforcement, lineage, or handover workflows require it.
- Do not invent unsupported workflow steps, notebook responsibilities, DQ rule types, parameters, or enforcement behavior.
- Do not create a separate documentation or manifest system for FabricOps guidance.
- Keep examples public-safe and generic; do not include production values, tenant or workspace identifiers, internal URLs, secrets, or screenshots.
- Check side effects before using a function.
- Treat `Not documented yet` as incomplete guidance; inspect source code, docstrings, generated manifests, and generated reference pages before generating code.
- Update docs and tests together when changing public APIs, generated reference behavior, or notebook-facing guidance.

## Notebook workflow ownership

- `00_env_config` owns environment selection, runtime setup, and metadata target configuration.
- `01_governance` owns agreement and steward context.
- Profiling or review notebooks own discovery, suggested metadata, and review evidence.
- Pipeline notebooks own executable validation, enforcement, lineage, and run evidence.
- Handover outputs should be assembled from approved metadata and runtime evidence rather than ad hoc notebook-only state.

### Data quality rules

DQ rules are governed evidence, not ad hoc notebook checks. They should flow through contract, profiling, review, approval, metadata, and enforcement workflows so downstream notebooks can explain which approved expectations were evaluated and why.

- Use `docs/reference/dq-rules/` for generated DQ rule guidance, and inspect individual generated rule pages before recommending syntax or parameters.
- Use `widget_review_dq_rules` for DQ review and approval workflows.
- Use `enforce_dq_rules` for executable pipeline enforcement before target writes.
- Do not bypass approved metadata when pipeline enforcement requires reviewed rules; enforcement should read approved active rules from the configured metadata target.
- Do not invent unsupported DQ rule types, syntax, parameters, or enforcement semantics.
- Summarize the relevant generated DQ rule page instead of duplicating full generated rule content.

`docs/reference/dq-rules/index.md` is the source of truth for currently supported DQ rule pages; the list below is an orientation aid and must not become a separate permanent source of truth:

- `docs/reference/dq-rules/accepted-values.md`
- `docs/reference/dq-rules/between.md`
- `docs/reference/dq-rules/column-a-gt-column-b.md`
- `docs/reference/dq-rules/column-a-gte-column-b.md`
- `docs/reference/dq-rules/column-pair-equal.md`
- `docs/reference/dq-rules/date-between.md`
- `docs/reference/dq-rules/date-not-future.md`
- `docs/reference/dq-rules/expression-true.md`
- `docs/reference/dq-rules/freshness.md`
- `docs/reference/dq-rules/greater-than.md`
- `docs/reference/dq-rules/greater-than-or-equal.md`
- `docs/reference/dq-rules/less-than.md`
- `docs/reference/dq-rules/less-than-or-equal.md`
- `docs/reference/dq-rules/max-age-days.md`
- `docs/reference/dq-rules/non-empty-string.md`
- `docs/reference/dq-rules/not-in-values.md`
- `docs/reference/dq-rules/not-null.md`
- `docs/reference/dq-rules/null-rate-below.md`
- `docs/reference/dq-rules/regex-match.md`
- `docs/reference/dq-rules/required-when.md`
- `docs/reference/dq-rules/unique.md`
- `docs/reference/dq-rules/unique-combination.md`
- `docs/reference/dq-rules/value-when.md`

## Generated reference discipline

- Use `docs/reference/_data/public-function-call-flows.json` as a normalized graph. Find a public root in `public_functions`, inspect its canonical function row in `defined_functions`, then use `relationships` where `caller_qualified_name` matches the current function to find direct callees. Recurse through those relationships only when transitive helper reachability or scope is needed. Use `inbound_callers` and `inbound_source_references` on `defined_functions` as separate signals; an import/reference is not a call edge.
- Use `docs/assets/public-function-call-flows-dashboard.html` when reviewer exploration, an expanded call tree, or an AI cleanup packet is needed. The dashboard reconstructs the tree from the same normalized JSON rather than relying on a stored expanded `flow` array.
- Use pages in `docs/api/reference/` for notebook authoring guidance.
- Use the embedded Internal implementation summary on public callable pages for package maintenance; standalone `docs/reference/internal/` pages are disabled by default and should only be used when explicitly generated for maintainer diagnostics.
- Never edit generated reference files manually. Update the authoritative source inputs, reference metadata, or generator and regenerate them.
- If function-level source changes affect callable structure, source locations, public exports, helper relationships, architecture classification, or public function flow metrics, regenerate the committed architecture contract with `PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py`. When a source, docstring, export, call-flow, reference-metadata, or generator change affects generated individual function reference content, regenerate the affected committed pages in the same source PR with `PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py`; do not regenerate them when the change cannot affect their content.

## Workflow

1. Identify whether the task is agreement, profiling or review, pipeline enforcement, governance review, handover, notebook authoring, or package maintenance.
2. Check the notebook workflow ownership above and current `How FabricOps Works` guide for the relevant starter flow.
3. Read the matching page in `docs/api/reference/` before calling or recommending a public helper.
4. For DQ work, read `docs/reference/dq-rules/index.md`, each relevant generated DQ rule page, and the callable page before generating notebook code.
5. Inspect `docs/reference/_data/public-function-call-flows.json` when you need callable architecture. Use `public_functions` for root metrics/lifecycle, `defined_functions` for individual callable metadata, and `relationships` for direct edges; follow edges recursively only for the downstream scope you actually need.
6. Use the embedded Internal implementation summary on callable pages when maintaining package implementation details; only use `docs/reference/internal/` if standalone internal pages were explicitly generated for maintainer diagnostics.
7. Preserve `00_env_config` metadata routing for reads and writes, especially governed evidence tables such as `METADATA_DQ_RULES`.
