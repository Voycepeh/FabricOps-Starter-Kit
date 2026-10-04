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
  - `METADATA_SOURCE_OBSERVATION` stores source-state evidence and history used by incremental execution; successful watermark and partition progress is stored on governed targets.

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

`AGENTS.md` is the repository-wide contract. Load the most specific workflow skill for the requested change:

| Change | Skill |
| --- | --- |
| Public callable or function-level package source | `.agents/skills/fabricops-public-api-change/SKILL.md` |
| Notebook templates under `templates/notebooks/` | `.agents/skills/fabricops-notebook-template/SKILL.md` |
| Documentation cleanup, structure, or presentation | `.agents/skills/fabricops-docs-maintenance/SKILL.md` |
| Release preparation, versioning, tagging, or publishing | `.agents/skills/fabricops-release/SKILL.md` |

Use a secondary skill only when the requested change genuinely crosses that boundary. For example, a package change that directly requires a notebook-template update uses the public-API skill as the primary workflow and the notebook skill for the affected template work.

Skills own task-specific procedure. They may specialize how to perform a task, but they must not override repository-wide contracts in this file. When guidance overlaps, keep the invariant here and the detailed procedure in the owning skill rather than maintaining two copies.

There is intentionally no generic catch-all FabricOps skill. When no specialized skill applies, follow this file and the authoritative repository sources directly.

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
- Public and internal functions must not call unrelated public workflow functions.
- Public and internal functions may call foundational FabricOps I/O functions for ordinary physical reads and writes. This narrow exception does not permit arbitrary public-to-public orchestration.
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

## Fabric I/O routing

- Ordinary reusable Fabric table and file reads/writes that are useful beyond one workflow should use the appropriate foundational function under `src/fabricops_kit/io/` instead of duplicating low-level transport logic.
- A workflow-specific physical read/write that has no credible direct notebook/user use may remain a private helper in its owning domain. Reuse central Fabric store, connector, path, and session helpers rather than promoting a niche operation into a public foundational API.
- Domain-specific mutations such as contract activation, profiling replacement/upsert, Source Observation commits, Catalogue upserts, and SCD processing may remain private to their owning domain and may use native Spark/Delta code when that keeps the domain behaviour clearer.
- Domain-specific mutation code must reuse configured Fabric routing, store, schema, path, and session helpers rather than rebuilding infrastructure rules ad hoc.
- Do not introduce a generic mutation API merely to hide `DeltaTable.merge()`; centralize only genuinely reusable infrastructure.
- Foundational I/O functions own their physical read/write completion output and must not expose ABFSS/OneLake implementation paths in normal user-facing logging.

## Public call-flow architecture contract

`docs/reference/_data/public-function-call-flows.json` is the committed normalized public callable architecture contract and compact lookup index for agents. It stores each callable once in `defined_functions`, public-root metrics and lifecycle in `public_functions`, and each resolved direct caller-to-callee edge once in `relationships`.

Before function-level source changes:

- find the callable by `qualified_name` in `defined_functions` for owner file, source location, classification, inbound callers, source references, and cleanup signals
- inspect `public_functions` when public-root width, scope, depth, files touched, lifecycle, or Live impact matters
- inspect `relationships` where `caller_qualified_name` matches the current callable for direct callees
- follow those relationships recursively only when transitive helper reachability is needed
- keep `inbound_callers` and `inbound_source_references` distinct; a package import or loaded-symbol reference is not a call edge
- use the dashboard when a fully expanded interactive call tree is useful; the dashboard reconstructs that view from the same normalized relationships at runtime

Source code, exports, reference metadata, and generators remain authoritative. Do not manually edit the JSON as a fix, and do not require agents to parse the generated dashboard HTML to understand the graph.

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
- Use `.agents/skills/fabricops-docs-maintenance/SKILL.md` for documentation ownership, readability, Guided Demo, Featured Solutions, and diagram procedure.
- Use `.agents/skills/fabricops-notebook-template/SKILL.md` for all living standard notebook templates. Only `00_env_config.ipynb` and `02_pipeline.ipynb` are currently part of the release snapshot contract.
- Use `.agents/skills/fabricops-release/SKILL.md` for release notes, release snapshots, versioning, tagging, and publishing procedure.
- Use `.agents/skills/fabricops-public-api-change/SKILL.md` for callable documentation and lifecycle-specific API procedure.

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
- no new unrelated public-to-public or internal-to-public calls outside the narrow foundational-I/O exception
- no private helper surfaced as Internal
- no unrelated generated files, dashboard output, release files, or notebook templates
- intentional breaking changes are clearly documented