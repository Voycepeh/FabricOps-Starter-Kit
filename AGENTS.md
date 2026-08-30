# AGENTS.md

## Purpose

Canonical operating guide for Codex and agent contributions in this repository. Keep changes focused, reusable, public-safe, and easy to hand over.

## Core operating rules

- Pull requests must target `main`.
- Treat GitHub and repository source as the source of truth.
- Treat Microsoft Fabric as the execution runtime.
- Prefer small, focused PRs and update existing owner files before adding new abstractions.
- Do not add compatibility aliases, legacy parameter names, wrappers, adapters, resolver layers, or transitional shims unless migration support is explicitly requested.
- Keep examples generic and public-safe. Never include real data, secrets, tenant or workspace identifiers, internal URLs, or production screenshots.
- Public brand name: **FabricOps Starter Kit**.
- Preferred positioning: **governed, quality-checked, Microsoft Fabric notebook workflows**.
- Keep metadata responsibilities separated and name the implemented tables precisely:
  - `METADATA_DATA_CATALOGUE` stores canonical table and column identity, physical location, data type, and processing-definition fields.
  - `METADATA_DATA_PROFILED` stores profile metrics for registered table and column snapshots.
  - `METADATA_DATA_PROFILED_FREQUENCY` stores frequency-distribution rows linked to profile snapshots where applicable.
  - `METADATA_DATA_LINEAGE` stores registered source/target pipeline participation.
  - `METADATA_ENRICHMENT` stores authored business and governance enrichment.
  - `METADATA_GUARDRAIL` stores authored executable Guardrail rules.
  - `METADATA_GUARDRAIL_RESULTS` stores Guardrail evaluation results and continuation decisions.
  - `METADATA_GUARDRAIL_ROW_RESULTS` stores row-level failures linked to Guardrail Results where applicable.
  - `METADATA_SOURCE_OBSERVATION`, `METADATA_SOURCE_WATERMARK_CHECKPOINT`, and `METADATA_SOURCE_PARTITION_CHECKPOINT` store implemented source-state and successful-processing records used by incremental execution.

## Canonical terminology and glossary

`docs/reference/_data/glossary.json` is the canonical source for FabricOps terminology used across documentation, code-facing descriptions, examples, tests, generated metadata text, diagrams, and agent-authored content.

Before introducing, renaming, redefining, or broadly replacing a term:

- check the glossary first and use the canonical term, category, meaning, aliases, and preferred usage
- preserve the three public glossary categories: **FabricOps concepts**, **Governance concepts**, and **Engineering concepts**; **Data Quality** is a Governance concept even when Engineering executes DQ checks
- prefer the specific FabricOps table, record, field, strategy, rule, or result name when one exists instead of vague alternatives such as `evidence`, `context`, `processing metadata`, or `data products`
- when documenting persisted metadata, hand-offs, diagrams, or lifecycle steps, name the actual implemented `METADATA_*` tables or record types when they are known; do not replace them with vague labels such as `observed evidence`, `observed metadata`, `runtime outcomes`, or `governance intent`
- generic category wording is acceptable only when the exact implementation is not relevant; when a section explains what FabricOps actually reads or writes, anchor it to the concrete table or record names
- verify metadata names and schemas against `src/fabricops_kit/config/metadata_schemas.py` before documenting them; do not invent near-miss names such as `METADATA_GUARDRAIL_RULES`
- preserve real implemented concepts such as Source Observation when they are the canonical concept or table; the rule is to remove vague substitutes, not valid domain terminology
- treat aliases as search and comprehension aids, not additional canonical concepts; for example, **policy as code** is an alias of **governance as code**
- update the glossary in the same focused PR when an intentional product or implementation change creates, removes, or materially changes a canonical concept
- do not preserve obsolete glossary terms merely for backwards compatibility unless migration support is explicitly requested
- if implementation and glossary disagree, verify the authoritative implementation first, then update the glossary rather than documenting stale behaviour

Terminology changes do not authorize unrelated code, schema, generated-reference, or dashboard changes. Keep the PR scoped to directly affected artifacts.

## Default task approach

For substantial tasks, resolve:

1. **Context**: repository area, source files, current behaviour, and existing workflows.
2. **Task**: the smallest complete change.
3. **Constraints**: public contracts, generated-artifact boundaries, and explicit exclusions.
4. **Expected output**: files that should and should not change.
5. **Verification**: targeted tests, scripts, builds, diffs, or manual checks.

Inspect and reuse current implementations before creating parallel paths. Avoid abstractions for hypothetical future use. Keep generated content generated.

## Task-specific skills

Use the relevant workflow skill:

- Public callable or function-level source changes:
  `.agents/skills/fabricops-public-api-change/SKILL.md`
- Release preparation:
  `.agents/skills/fabricops-release/SKILL.md`
- Documentation cleanup:
  `.agents/skills/fabricops-docs-maintenance/SKILL.md`
- Notebook template work:
  `.agents/skills/fabricops-notebook-template/SKILL.md`

`AGENTS.md` is the repository-wide contract. Skills provide focused procedures and must not override it.

## Backward compatibility and public contracts

Backward compatibility applies to supported public callables and externally consumed data contracts. It does not require preserving private or shared implementation structure.

For a Live public callable, preserve its observable contract unless the task explicitly authorizes a breaking change:

- public import path and exported name
- parameter names, order, defaults, and accepted inputs
- return type, schema, shape, and documented meaning
- side effects and persisted outputs
- exceptions and normal failure behaviour

The internal implementation may be replaced completely. Private helpers, non-exported shared helpers, helper filenames, helper call chains, internal imports, and internal algorithms may be renamed, moved, merged, split, inlined, rewritten, deleted, or otherwise replaced without changing the supported public contract.

Do not preserve obsolete internal wrappers, aliases, adapters, resolver layers, or transitional shims unless the task explicitly requests migration support.

An unchanged function signature alone does not prove backward compatibility. Verify observable behaviour, accepted inputs, return contracts, side effects, persisted outputs, and failure behaviour.

Preview callables are not covered by Live backward-compatibility guarantees. Preserve only behaviour required by the task and relevant tests unless the callable is being promoted or frozen.

Discontinued callables do not imply current support. Preserve historical behaviour only when explicitly required.

When breaking cleanup is authorized, do not add compatibility layers unless requested. Clearly identify every changed public contract in the PR summary.

## Function architecture

- Public functions use non-underscore names and are notebook-facing or user-facing entrypoints.
- Internal functions use non-underscore names and are architecture-visible implementation units.
- Private helpers use leading underscores and remain hidden implementation details.
- New architecture-visible internal functions must not use leading underscores.
- Public functions must not call other public functions.
- Internal functions must not call public functions.
- Public and internal functions may call their own private helpers.
- Cross-file imports or calls of underscore-prefixed private helpers are architecture violations.
- Classes, dataclasses, enums, constants, protocols, config objects, and external libraries are supporting objects, not architecture layers.
- Private helpers must not be counted in Public or Internal API metrics.
- Update relevant tests and snapshots when architecture classification or dashboard outputs intentionally change.

## Public callable package pattern

For a new public callable:

- use one public owner file named after the function
- use the package `shared.py` for reusable implementation objects
- use `__init__.py` for exports

Do not add `public.py`, `models.py`, `classes.py`, adapter or resolver files, or compatibility shims unless explicitly approved.

### Fabric IO callable file pattern

For Fabric IO, public owner files live under `src/fabricops_kit/io/`, and reusable IO helpers live in `src/fabricops_kit/io/shared.py`. Avoid wrapper-on-wrapper layers and remove obsolete compatibility code after migration.

## Public call-flow architecture contract

`docs/reference/_data/public-function-call-flows.json` is the committed public callable architecture contract and compact lookup index for agents.

Before function-level source changes, inspect the relevant entry for:

- callable scope and owner file
- direct and transitive callees
- helper reachability
- source locations
- architecture violations
- cleanup signals
- defined-but-not-used functions

Source code, exports, reference metadata, and generators remain authoritative. Do not manually edit the JSON as a fix.

Regenerate and commit the call-flow outputs only when a change affects:

- callable structure
- source locations
- public exports
- helper relationships
- architecture classification
- public function flow metrics

When an intentional source change produces a content change in `docs/reference/_data/public-function-call-flows.json`, retain and commit the corresponding `public_function_call_flows_json` timestamp update in `docs/reference/_data/generated-artifacts.json`. This timestamp manifest change is a directly owned output of the call-flow generator, not an unrelated generated artifact. When the call-flow JSON has no content change, do not commit a timestamp-only change unless the task explicitly requests a timestamp refresh. CI determinism checks may preserve or restore timestamps to avoid meaningless validation diffs.

Command:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
```

## Generated artifact policy

Keep dashboard builds and unrelated docs wording changes separate from source changes by default. Generated individual function reference artifacts are validated, committed outputs and belong in the same source PR when that change affects their content.

Source inputs include:

- `src/fabricops_kit/**/*.py`
- package exports
- `scripts/reference_docs_metadata.py`
- generator source

Ordinary source PRs must regenerate and commit the affected generated individual function reference artifacts when their source change affects generated content:

- `docs/api/reference/*.md`
- `docs/reference/index.md`
- `docs/reference/function-call-graph.md`

Typical changes that require regeneration include public callable source changes; docstring changes that affect generated documentation; callable source-location, public export, callable relationship, or call-flow changes; lifecycle, category, usage-note, or example changes in `scripts/reference_docs_metadata.py`; and generator changes that alter these outputs. Do not regenerate or commit the individual reference artifacts when a change cannot affect generated content.

Generate the individual reference artifacts with:

```bash
PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
```

Never edit generated pages manually. Update the authoritative source, metadata, or generator and regenerate. After regeneration, run the generator a second time and confirm that it produces no diff.

The dashboard artifact remains separately owned:

- `docs/assets/public-function-call-flows-dashboard.html`

Do not regenerate or commit the dashboard in ordinary backend or source PRs unless the PR directly changes the dashboard frontend or its published output contract.

Metadata schema or column ownership changes must update the canonical schema source first and regenerate only the metadata reference artifacts required by the repository contract.

Official generator commands:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
PYTHONPATH=src python scripts/generate_public_function_call_flows_dashboard.py
```

Validation builds do not make generated files on `main` current unless those files are intentionally committed in a scoped PR.

## Documentation and API reference

- Keep root `README.md` concise and navigation-focused.
- Put lifecycle and operating guidance in `docs/`.
- Put callable API guidance in `src/README.md`.
- Do not maintain duplicate manual callable lists.
- Public callable pages are sourced from `src/fabricops_kit/` docstrings and source metadata.
- Do not manually edit generated reference pages as source of truth.
- `src/fabricops_kit/config/metadata_schemas.py` is the canonical implemented metadata schema source.
- `Managed by` entries should identify exact source functions when traceable.

### Documentation ownership

Give each topic one canonical home based on what the reader is trying to learn. Before adding a page or expanding an existing one, classify the content and update the canonical owner instead of creating overlapping explanations.

- **Product Definition** owns what FabricOps is: the original product intent, scope, audience, positioning, operating decisions, and product-level boundaries.
- **Glossary** owns canonical user-facing term definitions and the **FabricOps concepts / Governance concepts / Engineering concepts** grouping.
- **How FabricOps Works** owns the high-level explanation of how the complete FabricOps workflow fits together. It should be understandable without implementation-level detail.
- **Guided Demo** owns practical implementation: what users do, run, configure, and observe when applying the FabricOps workflow. Put useful technical rationale, trade-offs, caveats, and edge cases beside the relevant step in focused collapsible blocks instead of creating a separate rationale layer. Each action page should surface only the glossary concepts needed for that step rather than requiring users to read the full glossary first.
- **Function Reference** owns exact callable contracts: parameters, returns, side effects, failure behaviour, and callable-specific usage guidance.

Cross-link between these layers instead of copying the same explanation into several pages. Keep overview pages high level, Guided Demo pages actionable with optional contextual rationale, and reference pages exact.

### Human-facing documentation readability

Human-facing pages should be scannable before they are read in detail. Use the documentation-maintenance skill for the full pattern, and apply these repository-wide defaults:

- Prefer **page title → short lead sentence → visual/table → short sections → focused callout → next action**.
- Start major sections with a short bold summary sentence when it helps readers understand the point quickly.
- Break long prose into descriptive `##` and `###` sections, bullets, numbered steps, or compact tables.
- Use Material admonitions only for important notes, warnings, and rules. Avoid excessive boxes.
- Use collapsible `???` detail blocks for optional background, exceptions, troubleshooting, rationale, trade-offs, and long secondary explanations.
- Do not repeat a diagram's full meaning in several paragraphs directly below it.
- Procedure pages should normally end with an expected result and a clear next step.
- Prefer existing Markdown and MkDocs Material patterns before adding custom HTML or decorative components.
- Preserve exact FabricOps terminology and do not replace canonical repo terms with generic alternatives.
- Keep layouts readable on mobile as well as desktop.

The Maintainer Release Guide has a separate source-of-truth rule: `.agents/skills/fabricops-release/SKILL.md` owns the workflow and `docs/maintainer/index.md` is synchronised from it. Change the skill first rather than independently editing the published guide.

### Public API docstrings

For new or modified public APIs:

- use complete NumPy-style docstrings
- document every signature parameter
- describe actual behaviour without placeholder text
- document return meaning, relevant side effects, failure behaviour, and Fabric runtime assumptions
- include relevant `Parameters`, `Returns`, `Raises`, `Notes`, `Examples`, and `See Also` sections
- use valid examples that match the real signature
- do not mix Google-style and NumPy-style headers

Live callables must document actual behaviour, meaningful side effects, return interpretation, failure behaviour, runtime assumptions, and at least one valid example. Preview callables may use lighter documentation while unstable, but must meet the Live standard before promotion.

The active Ruff configuration enforces docstring rules. Use correct section spacing and document every parameter when a `Parameters` section is present.

## Interactive widgets

- Public widget functions use `widget_<verb>_<object>`.
- Import IPython display with `from IPython import display as ip`.
- Use `ip.display(...)` for widgets.
- Preserve unqualified `display(...)` for Fabric-native DataFrame rendering.
- Do not create duplicate wrappers for an existing widget workflow.

## Metadata lakehouse routing

Do not assume the attached or default Lakehouse for metadata tables. Route all `METADATA_*` reads and writes through the metadata target configured by `00_env_config`.

Use the current public IO signatures and configured metadata store or path. Do not introduce default-Lakehouse shortcuts.

## Verification before PR

Choose verification proportional to the change:

- Run targeted tests for the changed callable, domain, generator, or documentation contract first.
- Run broader tests only when shared behaviour or architecture requires them.
- Run Ruff on the affected files or relevant scope when practical.
- Use `compileall`, an import check, or another focused syntax check appropriate to the change.
- Regenerate `public-function-call-flows.json` only when its architecture contract changes.
- For docstring-only changes, use the smallest syntax or import verification, do not regenerate the architecture contract unless it changes, and regenerate the individual reference artifacts when the docstring affects their generated content.
- When individual reference artifacts are regenerated, run their generator a second time and confirm that it produces no diff.
- Run dashboard or generator snapshot tests only when those outputs intentionally change.

Before opening a PR, review the diff and confirm:

- no unintended public contract change
- no new public-to-public or internal-to-public calls
- no private helper surfaced as Internal
- no unrelated generated files, dashboard output, release files, or notebook templates
- intentional breaking changes are clearly documented