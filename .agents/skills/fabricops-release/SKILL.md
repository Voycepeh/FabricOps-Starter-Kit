---
name: FabricOps Release Maintainer
description: Guide an AI coding agent through preparing a FabricOps release, performing deterministic repository work automatically, and pausing for explicit maintainer decisions where human judgement is required.
---

# FabricOps Maintainer Release Guide

This skill is the operational source of truth for FabricOps release preparation. The published human page at `docs/maintainer/index.md` is synchronised from this file; do not maintain a second independent copy of the release workflow.

End-user setup and notebook walkthrough content stays in the [Guided Demo](../guided-demo.md). Maintainer-only release curation, packaging, publishing, and recovery guidance belongs here.

## 1. What a FabricOps release contains

A FabricOps release contains a tagged source commit, package artifacts, release notes, release lifecycle evidence, and generated release contract pages. The release manifest is the lifecycle decision file:

```text
docs/releases/manifests/<version>.yml
```

It contains four release asset groups:

- `functions`
- `metadata_tables`
- `templates`
- `dq_rules`

Source registries decide what exists; the manifest decides whether each discovered asset is `preview`, `live`, or `discontinued` for the release.

| Asset group | Authoritative source | Release inventory behaviour |
| --- | --- | --- |
| Functions | [`src/fabricops_kit/public_api.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/public_api.py) `SUPPORTED_PUBLIC_API` | A function enters the release inventory only when it is in the supported public API boundary. |
| Metadata tables | [`src/fabricops_kit/config/metadata_schemas.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py) canonical schema registry | A metadata table enters the inventory when it is registered in the canonical schema registry. |
| Notebook templates | [`templates/notebooks/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/) | A committed notebook in this directory enters the inventory. |
| DQ rules | [`src/fabricops_kit/pipeline/guardrails_shared.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/guardrails_shared.py) `DQ_RULE_TYPES` | A DQ rule enters the inventory only when registered in `DQ_RULE_TYPES`. |

## 2. Before you start

When invoked with language such as “start a release”, “prepare the next FabricOps release”, “release FabricOps”, or “start release preparation”, the AI agent must inspect before mutating.

Run these inspection commands first:

```bash
git status --short
git branch --show-current
git fetch origin main
git log --oneline -5 origin/main
```

Purpose: confirm the working tree, branch, and latest `main` state. These commands read Git metadata and do not write repository files. If unrelated changes exist, stop and ask whether to preserve, commit, or move them before release work continues.

Read these files and directories before proposing changes:

- [`pyproject.toml`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/pyproject.toml): authoritative package version and package configuration.
- [`src/fabricops_kit/__init__.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/__init__.py): package exports and runtime `__version__` loader.
- `CHANGELOG.md`: human-approved release narrative.
- [`docs/releases/manifests/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/docs/releases/manifests/): version-specific lifecycle manifests.
- [`.github/workflows/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/.github/workflows/): release and documentation automation.
- [`src/fabricops_kit/public_api.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/public_api.py): supported public API registry.
- [`src/fabricops_kit/config/metadata_schemas.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py): canonical metadata schema registry.
- [`src/fabricops_kit/pipeline/guardrails_shared.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/guardrails_shared.py): DQ rule registry.
- [`templates/notebooks/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/): release template source directory.

Identify the latest released version from `docs/releases/manifests/*.yml`, the current development version from `pyproject.toml`, and the requested release scope from the maintainer or merged PR history. Never assume the next version.

## 3. Start the AI-assisted workflow

The AI should perform safe deterministic work itself and pause only for explicit maintainer decisions.

Default release PR workflow:

1. Work from latest `main`.
2. Create a focused release-preparation branch.
3. Make only release-preparation changes.
4. Keep unrelated source work out of the release PR.
5. Run release checks and generators.
6. Show selected version, lifecycle changes, New/Updated evidence, generated artifacts, changelog draft, tests run, and unresolved manual steps.
7. Ask for final approval before opening or finalising the release PR when approval is required.

Release-required generated artifacts may include the release manifest, release contract pages, individual function reference pages, and `docs/reference/_data/public-function-call-flows.json` when function-level source changes affect the architecture contract. Do not include unrelated dashboard output unless the dashboard is intentionally refreshed.

## 4. Inspect current release state

Run non-mutating validation where supported:

```bash
PYTHONPATH=src python scripts/generate_release_inventory.py --check
```

Entry point: [`scripts/generate_release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_release_inventory.py). Implementation: [`scripts/release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/release_inventory.py).

This reads `pyproject.toml`, source registries, and `docs/releases/manifests/<version>.yml`. It writes nothing in `--check` mode. Success prints `Release inventory validated: docs/releases/manifests/<version>.yml`. If it fails because the target manifest is missing or stale, prepare the target manifest as described below instead of weakening validation.

## 5. Review all available release assets

Before setting lifecycle statuses or drafting the changelog, discover and present all release assets grouped as Functions, Metadata tables, Notebook templates, and DQ rules.

For each asset, show where available:

- name
- source path
- documentation path
- current lifecycle status
- `introduced_in`
- `live_since`
- `schema_since` for metadata tables
- prior release presence
- whether it appears new
- whether it appears changed where deterministic evidence exists
- whether it is missing from current source

Use a concise decision table like this:

| Asset | Type | Previous status | Detected change | Proposed action |
| --- | --- | --- | --- | --- |
| `widget_pipeline_bootstrap` | Function | Preview | Source changed or maintainer-scoped | Ask whether to keep Preview or promote to Live. |
| `METADATA_PIPELINE_RUNS` | Metadata table | Live | Schema fingerprint changed | Keep Live; confirm release notes and compatibility. |
| `accepted_values` | DQ rule | Not present | New | Ask Preview or Live. |
| `03_governance` | Template | Live | Changed where detectable | Keep Live; confirm update wording. |

Lifecycle status is not change classification:

- lifecycle status: `preview`, `live`, `discontinued`
- release change classification: New, Updated, Unchanged, Discontinued, Removed or missing

New or Updated classification should be derived deterministically only where current tooling supports it. Where deterministic detection is not available, the AI may identify a likely change from Git history or diffs, but must label it as a proposed interpretation requiring maintainer confirmation. Never add a lifecycle status named `updated`.

## 6. Decide Preview, Live and Discontinued statuses

The AI must ask the maintainer to decide before editing lifecycle fields:

1. Which newly discovered assets should remain Preview?
2. Which newly discovered assets should become Live?
3. Which existing Preview assets should now become Live?
4. Which assets should become Discontinued?
5. Which removals are intentional?
6. Which updates require upgrade guidance?
7. What is the user-facing release motivation?
8. Is the intended release Patch, Minor, or Major?

New assets default to `preview`. The generator must not automatically promote assets to `live`.

## 7. Decide Patch, Minor or Major

`pyproject.toml` is the authoritative package version. `fabricops_kit.__version__` is loaded from installed package metadata with a local fallback to `pyproject.toml`; it is not a second committed version authority.

Use the smallest semantic version bump that communicates public impact:

| Bump | Use when |
| --- | --- |
| Patch | Backward-compatible fixes, documentation corrections, and non-breaking notebook-template improvements. |
| Minor | Backward-compatible public APIs, new notebook capabilities, new optional configuration, or additive metadata/rule formats. |
| Major | Breaking changes to Python APIs, notebook contracts, configuration structures, metadata schemas, agreement or pipeline contracts, or DQ rule formats. |

Pause for maintainer approval before selecting or writing the final version.

## 8. Update version and manifest

When the target version is approved, update [`pyproject.toml`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/pyproject.toml). The release inventory command reads that version.

For a follow-up release, copy the latest prior manifest first so lifecycle decisions carry forward:

```bash
cp docs/releases/manifests/0.1.0.yml docs/releases/manifests/0.2.0.yml
```

Then update the copied file:

```yaml
release_version: 0.2.0
```

Synchronise generated fields:

```bash
PYTHONPATH=src python scripts/generate_release_inventory.py
```

The generator reads the current `pyproject.toml` version and `docs/releases/manifests/<version>.yml`. If the target manifest does not exist, it creates a fresh manifest and current discovered assets start as `preview`; it does not automatically carry prior lifecycle decisions forward.

Human-owned and generator-preserved fields include `status`, `introduced_in`, `live_since`, `schema_since`, `discontinued_in`, `notes`, `rationale`, `description`, `purpose`, and `managed_by`.

Generated fields that must not be hand-maintained include discovered names, qualified names, source paths, documentation paths, schema fingerprints, and other computed fields. If they are wrong, fix source metadata or generator logic and rerun the generator.

## 9. Draft and approve changelog

`CHANGELOG.md` is human-approved release narrative, not a purely generated file. It records why users should care.

Recommended process:

1. Review merged PRs and release inventory evidence.
2. Draft entries under `Unreleased`.
3. Classify entries under `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, and `Security`.
4. Include upgrade instructions and breaking changes where applicable.
5. Move approved entries to `## [X.Y.Z] - YYYY-MM-DD`.

An LLM may draft changelog entries, release summaries, migration notes, rationale, descriptions, and likely New/Updated explanations from deterministic diffs. The maintainer must approve final wording. The LLM must not invent changes, decide semantic version impact, promote Preview assets to Live, or accept a breaking change.

## 10. Run generators

Run only the generators required for the release scope. Do not manually edit generated contract pages.

| Purpose | Command | Reads | Writes | May edit output manually? |
| --- | --- | --- | --- | --- |
| Public call-flow JSON | `PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py` | Python source, public API registry, release manifests | `docs/reference/_data/public-function-call-flows.json` | No. Fix source or generator. |
| Individual function references | `PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py` | Source docstrings and reference metadata | `docs/api/reference/*.md`, `docs/reference/index.md` | No. Fix source docstrings or metadata. |
| Release inventory | `PYTHONPATH=src python scripts/generate_release_inventory.py` | `pyproject.toml`, source registries, version manifest | `docs/releases/manifests/<version>.yml` | Edit human-owned lifecycle fields only. |
| Release contract pages | `PYTHONPATH=src python scripts/generate_release_contract_pages.py` | release manifest, changelog, source registries | `docs/releases/<version>/`, `docs/releases/index.md` | No. Fix manifest, changelog, source, or generator. |
| Dashboard | `PYTHONPATH=src python scripts/generate_public_function_call_flows_dashboard.py` | call-flow JSON | `docs/assets/public-function-call-flows-dashboard.html` | No. Run only for intentional dashboard refreshes. |

Generator source links:

- [`scripts/generate_public_function_call_flows_json.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_public_function_call_flows_json.py)
- [`scripts/generate_individual_function_reference_pages.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_individual_function_reference_pages.py)
- [`scripts/generate_release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_release_inventory.py)
- [`scripts/release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/release_inventory.py)
- [`scripts/generate_release_contract_pages.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_release_contract_pages.py)
- [`scripts/generate_public_function_call_flows_dashboard.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_public_function_call_flows_dashboard.py)

## 11. Review generated evidence

Review generated diffs before testing:

```bash
git diff -- docs/releases/manifests docs/releases docs/api/reference docs/reference/_data/public-function-call-flows.json
```

Success means generated changes match the approved release decisions and no unrelated generated dashboard or reference output is included. If unexpected generated artifacts appear, revert them or explain why they are intentionally part of the release PR.

## 12. Test and build

Run release-compatible checks when dependencies are available:

```bash
uv sync --frozen
uv run ruff check .
uv run pytest
uv run mkdocs build --strict
uv build
uvx twine check dist/*
```

If the AI cannot run a command because of credentials, missing dependencies, unavailable network, or Fabric access, it must explain why, provide the exact manual action, state the expected result, wait for confirmation, and continue from the next verifiable step.

## 13. Prepare and merge release PR

The release PR targets `main` and should contain only release-preparation changes. Before finalising the PR, show the maintainer:

- selected version
- asset lifecycle changes
- New and Updated assets where evidence exists
- generated artifacts included
- changelog draft
- tests run
- unresolved manual steps

Ask for final approval before opening or finalising the PR when required.

## 14. Create release tag

Tagging is a separate explicit phase after the release PR is merged.

1. Confirm the release PR is merged into `main`.
2. Fetch and inspect the merged commit.
3. Confirm package version, changelog, and manifest match.
4. Confirm required CI checks passed.
5. Show the exact tag to create.
6. Ask for explicit approval.
7. Create and push the annotated tag only when authorised and technically available.

```bash
git tag -a vX.Y.Z -m "FabricOps Starter Kit vX.Y.Z"
git push origin vX.Y.Z
```

Do not rewrite or move an already published release tag.

## 15. Verify GitHub Release

After the tag workflow completes, verify the GitHub Release contains:

- wheel
- source distribution
- checksums
- release notes
- notebook pack when configured by the release manifest

Release workflow source lives under [`.github/workflows/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/.github/workflows/). If the workflow fails, report the exact failing step and recovery path.

## 16. Retry, hotfix and rollback guidance

If automation fails before the GitHub Release is created, fix the problem and push a new annotated tag for the corrected release commit. Do not rewrite a published release tag.

For a hotfix, branch from the released tag or production release commit, apply the minimal fix, update the changelog and patch version, refresh release contract pages as needed, validate locally, and tag the new patch release.

GitHub Releases and tags are immutable release evidence. Prefer deprecating a bad release with a clear GitHub Release note and a follow-up patch release instead of deleting or rewriting history.

## 17. Human, AI, generator and automation ownership table

| Item | Owner | Maintainer or AI action |
| --- | --- | --- |
| Release scope and motivation | Human-defined | Maintainer approves release intent and user-facing narrative. |
| Semantic version | Human-defined | AI may propose; maintainer selects Patch, Minor, or Major. |
| Public API inclusion | Human-owned source decision | AI edits only after approval. |
| Preview, Live, Discontinued | Human-owned manifest decision | AI asks, then edits lifecycle fields. |
| Source registries | Human-owned source definitions | AI may update source when requested and tested. |
| Asset discovery | Deterministic generator | AI runs discovery and summarises results. |
| Schema fingerprints | Deterministic generator | Never edit manually. |
| New/Updated labels | Deterministic where supported | AI labels uncertain updates as proposed interpretations. |
| Changelog wording | Human-approved | AI drafts; maintainer approves. |
| Generated release pages | Deterministic rendering | AI regenerates and reviews; do not hand-edit. |
| Build artifacts and checksums | Tag workflow | AI verifies published assets. |
| Tag creation | Human-approved automation | AI pauses before creating or pushing tags. |

## 18. Exact source-code links

- Package configuration: [`pyproject.toml`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/pyproject.toml)
- Package root and exports: [`src/fabricops_kit/__init__.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/__init__.py)
- Public API registry: [`src/fabricops_kit/public_api.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/public_api.py)
- Metadata schema registry: [`src/fabricops_kit/config/metadata_schemas.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py)
- DQ rule registry: [`src/fabricops_kit/pipeline/guardrails_shared.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/guardrails_shared.py)
- Notebook template directory: [`templates/notebooks/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/)
- Release manifests: [`docs/releases/manifests/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/docs/releases/manifests/)
- Release workflow automation: [`.github/workflows/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/.github/workflows/)
- Release inventory entry point: [`scripts/generate_release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_release_inventory.py)
- Release inventory implementation: [`scripts/release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/release_inventory.py)
