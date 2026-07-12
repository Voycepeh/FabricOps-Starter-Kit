---
name: FabricOps Release Maintainer
description: Guide an AI coding agent through preparing a FabricOps release, performing deterministic repository work automatically, and pausing for explicit maintainer decisions where human judgement is required.
---

# FabricOps Maintainer Release Guide

This skill is the operational source of truth for FabricOps release preparation. The published human page at `docs/maintainer/index.md` is synchronised from this file; do not maintain a second independent copy of the release workflow.

End-user setup and notebook walkthrough content stays in the [Guided Demo](../guided-demo.md). Maintainer-only release curation, packaging, publishing, and recovery guidance belongs here.

## Choose the correct execution environment

Use the release workflow in the environment that matches the current phase. Codex Cloud is appropriate for release preparation and release-readiness reporting, but the final tag and publication phase requires Codex Desktop or another authenticated local environment.

### Codex Cloud

Codex Cloud may be used for:

1. Release inventory inspection.
2. Lifecycle curation.
3. Release PR preparation.
4. Generator execution.
5. Tests, linting and documentation validation.
6. Package and wheel builds.
7. Final release preflight.
8. Reporting whether the repository is ready to tag.

Codex Cloud must not be assumed capable of:

1. Creating or pushing the final annotated release tag.
2. Using the maintainer's local Git or GitHub credentials.
3. Accessing a persistent corrected local branch state.
4. Waiting for a GitHub Actions release workflow to complete.
5. Reliably verifying the final GitHub Release and published assets.

When the release-preparation PR has merged and Codex Cloud completes preflight, it must stop and provide the exact tag command for the maintainer to run in an authenticated local environment, for example `git tag -a vX.Y.Z -m "FabricOps Starter Kit vX.Y.Z"`. It must not create or push the tag from Codex Cloud.

### Codex Desktop or authenticated local environment

Run the final tag step in Codex Desktop or another authenticated local environment that has:

- a clean local clone
- the latest `origin/main`
- working GitHub authentication
- permission to push tags
- network access to GitHub
- `git`
- `gh` where workflow and release inspection are required
- `uv` and the repository build dependencies

Codex Desktop or the local environment may:

1. Run the final release preflight.
2. Create the local annotated tag.
3. Pause for explicit maintainer approval.
4. Push only the approved release tag.
5. Inspect the tag-triggered GitHub Actions workflow.
6. Verify the GitHub Release and frozen source links.

!!! warning "Final tag creation requires an authenticated local environment"
    Do not rely on Codex Cloud to push the release tag. Cloud environments may have a stale or temporary checkout, no GitHub write credentials, restricted network access, or no ability to wait for and inspect the completed release workflow.

    Attempting the final release step from such an environment may fail after the release PR has already been merged.

    Use Codex Desktop or a local terminal with confirmed GitHub authentication for the final tag and publication step.

## 1. What a FabricOps release contains

A FabricOps release currently governs only two formal areas: FabricOps public functions and FabricOps metadata schema. Notebook templates, skills, samples, guided demos, DQ assets, and environment resource bundles are manually maintained outside the package release contract. The release manifest is the lifecycle decision file:

```text
docs/releases/manifests/<version>.yml
```

It contains two release asset groups:

- `functions`
- `metadata_tables`

The canonical frozen source reference is the annotated Git release tag, not an
intermediate PR commit SHA. For a release `X.Y.Z`, set the manifest fields to:

```yaml
release_version: X.Y.Z
source_ref: vX.Y.Z
```

For example:

```yaml
release_version: 0.1.0
source_ref: v0.1.0
```

Generated frozen source links must use the tag form:

```text
https://github.com/<owner>/<repo>/blob/vX.Y.Z/<source-path>
```

The release tag is the stable, human-readable release identity. During the
release-preparation PR, frozen source links that use the intended release tag
may return 404 because the tag does not exist yet. This is expected. The links
become valid immediately after the annotated tag is pushed following merge.
Release-preparation validation checks tag/version consistency without requiring
the tag to already exist.

Source registries decide what exists; the manifest decides whether each discovered asset is `preview`, `live`, or `discontinued` for the release.

| Asset group | Authoritative source | Release inventory behaviour |
| --- | --- | --- |
| Functions | [`src/fabricops_kit/public_api.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/public_api.py) `SUPPORTED_PUBLIC_API` | A function enters the release inventory only when it is in the supported public API boundary. |
| Metadata tables | [`src/fabricops_kit/config/metadata_schemas.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py) canonical schema registry | A metadata table enters the inventory when it is registered in the canonical schema registry. |

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

Identify the latest released version from `docs/releases/manifests/*.yml`, the current development version from `pyproject.toml`, and the requested release scope from the maintainer or merged PR history. Never assume the next version.

## 3. Start the AI-assisted workflow

The AI should perform safe deterministic work itself and pause only for explicit maintainer decisions.

Default release workflow:

1. Inspect the latest `main`.
2. Curate and approve the release inventory and lifecycle decisions.
3. Prepare the final release PR from a focused release-preparation branch.
4. Set the manifest to Live with the release date.
5. Set `source_ref` to the intended annotated release tag, such as `v0.1.0`.
6. Finalise the changelog.
7. Generate and commit frozen release documentation using the tag reference.
8. Validate package version, manifest version, source tag, generated function/metadata release pages, tests, documentation, and wheel artifacts.
9. Merge the release PR into `main`. The release PR may be squash-merged or rebased because frozen source documentation depends on the release tag, not an intermediate PR commit.
10. Stage A: run release preflight in Codex Cloud, Codex Desktop, or another supported environment and report whether the release is ready to tag. Codex Cloud must stop here and provide the exact local tag command.
11. Stage B: in Codex Desktop or another authenticated local environment, refresh `main`, create the local annotated tag, pause for explicit maintainer approval, and push only the approved tag.
12. Allow the tag-triggered GitHub Actions workflow to build and publish the GitHub Release.
13. Verify the workflow result, GitHub Release assets, and frozen source links from the authenticated local environment.

Do not require any PR branch commit as the frozen source identity. Normal PR history cleanup must not invalidate frozen release links.

Release-required generated artifacts may include the release manifest, release contract pages, individual function reference pages, and `docs/reference/_data/public-function-call-flows.json` when function-level source changes affect the architecture contract. Do not include unrelated dashboard output unless the dashboard is intentionally refreshed.

Required release consistency checks must agree before merge and again in the
tag workflow:

- Git tag: `vX.Y.Z`
- Package version: `X.Y.Z`
- Manifest `release_version`: `X.Y.Z`
- Manifest `source_ref`: `vX.Y.Z`
- Changelog release heading: `X.Y.Z`
- Frozen release directory: `docs/releases/X.Y.Z/`

A mismatch blocks the release. The release workflow may also record the resolved
commit SHA for audit evidence, for example `Release tag: v0.1.0` and
`Resolved commit: <merged-main-sha>`, but that SHA is resolved release metadata
rather than the canonical source URL stored in the manifest. Generated
documentation should link to the release tag, not the resolved SHA.

## 4. Inspect current release state

Run non-mutating validation where supported:

```bash
PYTHONPATH=src python scripts/generate_release_inventory.py --check
```

Entry point: [`scripts/generate_release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_release_inventory.py). Implementation: [`scripts/release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/release_inventory.py).

This reads `pyproject.toml`, source registries, and `docs/releases/manifests/<version>.yml`. It writes nothing in `--check` mode. Success prints `Release inventory validated: docs/releases/manifests/<version>.yml`. If it fails because the target manifest is missing or stale, prepare the target manifest as described below instead of weakening validation.

## 5. Review all available release assets

Before setting lifecycle statuses or drafting the changelog, discover and present the formal release assets grouped as Functions and Metadata tables only.

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

Formal lifecycle decisions apply only to public functions and metadata tables. Do not classify notebook templates, DQ rules, skills, samples, guided demos, function packets, refactor packets, documentation examples, or environment resource bundles as package release assets.

Notebook templates are manually maintained living applications of the package. They are not promoted, frozen, copied, renamed by package version, packaged, automatically stamped, or release-blocked by this workflow. Maintainers may run separate manual validation for templates, and each template should keep a manually maintained `Tested with FabricOps` table that Voyce Peh updates only after testing in Microsoft Fabric.

DQ logic may remain available in the repository, but DQ validation, DQ rules, DQ widgets, and DQ release notes are not part of the formal release contract for now. Do not add DQ versioning, migration, compatibility, schema, or release requirements during package release preparation.

## 7. Decide Patch, Minor or Major

`pyproject.toml` is the authoritative package version. `fabricops_kit.__version__` is loaded from installed package metadata with a local fallback to `pyproject.toml`; it is not a second committed version authority.

Use the smallest semantic version bump that communicates public impact:

| Bump | Use when |
| --- | --- |
| Patch | Backward-compatible fixes and documentation corrections for public functions or metadata schemas. |
| Minor | Backward-compatible public function additions or additive metadata schema changes. |
| Major | Breaking changes to public Python functions or metadata schemas. |

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
| Release inventory | `PYTHONPATH=src python scripts/generate_release_inventory.py` | `pyproject.toml`, public function and metadata schema registries, version manifest | `docs/releases/manifests/<version>.yml` | Edit human-owned lifecycle fields only. |
| Release contract pages | `PYTHONPATH=src python scripts/generate_release_contract_pages.py` | release manifest, changelog, source registries | `docs/releases/<version>/`, `docs/releases/index.md` | No. Fix manifest, changelog, source, or generator. |
| Dashboard | `PYTHONPATH=src python scripts/generate_public_function_call_flows_dashboard.py` | call-flow JSON | `docs/assets/public-function-call-flows-dashboard.html` | No. Run only for intentional dashboard refreshes. |

Generator source links:

- [`scripts/generate_public_function_call_flows_json.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_public_function_call_flows_json.py)
- [`scripts/generate_individual_function_reference_pages.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_individual_function_reference_pages.py)
- [`scripts/generate_release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_release_inventory.py)
- [`scripts/release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/release_inventory.py)
- [`scripts/generate_release_contract_pages.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_release_contract_pages.py)
- [`scripts/generate_public_function_call_flows_dashboard.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_public_function_call_flows_dashboard.py)

When freezing release function references, the generator reads `source_ref` from
the release manifest. For release-preparation PRs, `source_ref: vX.Y.Z` is valid
even before the tag exists. Do not hardcode a release tag into generated pages;
fix the manifest if the generated links use the wrong tag.

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


A release may validly contain zero Live metadata contracts. Notebook templates are living applications of the FabricOps package; do not copy, freeze, version, package, or stamp them during package release preparation. Their `Tested with FabricOps` table is manually maintained only after Voyce Peh tests the notebook in Microsoft Fabric.

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

## 14. Stage A: release preflight

Stage A may run in Codex Cloud, Codex Desktop, or another environment with the required dependencies. It is a release-readiness check only. It must not create or push a tag when running in Codex Cloud.

The preflight has only two blocking groups: public function checks and metadata schema checks. Public function checks may validate package version consistency, public exports, function signatures, function compatibility classification, function documentation, wheel/build outputs, and public-function release notes. Metadata schema checks may validate required metadata tables, columns, data types, nullability, schema compatibility, breaking-change classification, and metadata release notes.

The preflight must:

1. Validate package, manifest, changelog, and tag alignment for the formal release scope.
2. Run targeted public function and metadata schema tests.
3. Run full validation where supported.
4. Build distributions.
5. Confirm no tracked files changed.
6. Report whether the release is ready.

Notebook templates, template snapshots, skills, DQ validation, sample generation, environment resource bundles, and notebook packs must not block package release preflight.

Recommended checks include:

```bash
PYTHONPATH=src python scripts/check_release_ready.py vX.Y.Z
uv run ruff check .
uv run pytest
uv run mkdocs build --strict
uv build
uvx twine check dist/*
git status --short
```

`git status --short` must be clean after validation and builds. If validation fails before tag creation, create a focused fix PR against `main`; do not tag a failing release.

## 15. Stage B: tag and publish

Stage B must run in Codex Desktop or another authenticated local environment. It must refresh `main`, repeat the critical release-readiness check, confirm the tag does not already exist, create the annotated tag locally, show the tag target to the maintainer, pause for explicit approval, push only the tag, inspect the tag-triggered workflow, verify the GitHub Release and assets, and verify frozen `blob/vX.Y.Z/` source links.

Before creating the tag, run these mandatory environment checks:

```bash
git status --short
git fetch origin --tags
git checkout main
git pull --ff-only origin main
git rev-parse HEAD
git ls-remote origin
gh auth status
```

Requirements:

1. `git status --short` must be clean.
2. `git pull --ff-only` must succeed.
3. `git ls-remote origin` must succeed.
4. `gh auth status` must show an authenticated account when `gh` is used for workflow and release inspection.
5. The authenticated account must have permission to push tags to the repository.

If any check fails, stop before creating the tag. Do not bypass authentication, disable protections, or force-push.

Use this concise authenticated-local command sequence after the release PR has merged and required CI has passed:

```bash
git fetch origin --tags
git checkout main
git pull --ff-only origin main
git status --short

PYTHONPATH=src python scripts/check_release_ready.py vX.Y.Z

git tag --list vX.Y.Z
git ls-remote --tags origin refs/tags/vX.Y.Z refs/tags/vX.Y.Z^{}

git tag -a vX.Y.Z -m "FabricOps Starter Kit vX.Y.Z"

git show --no-patch --decorate vX.Y.Z
git rev-list -n 1 vX.Y.Z
```

Stop immediately before pushing the tag. Ask for explicit approval and show the maintainer:

- current `main` SHA
- local annotated tag
- resolved tag target
- release-readiness result
- test result
- built artifact names

Push the tag only after explicit maintainer approval:

```bash
git push origin vX.Y.Z
```

Do not use `--force`. Do not create or push the tag from within the release-preparation PR. Do not rewrite, move, recreate, delete, or force-push an already published release tag.

## 16. Verify GitHub Release

The maintainer or Codex Desktop pushes the annotated tag. The tag-triggered GitHub Actions workflow builds and publishes the release. The local agent verifies the resulting workflow and GitHub Release. The local agent should not manually upload substitute assets unless the documented recovery process explicitly requires it.

The tag workflow must:

1. Verify the pushed tag matches the package version.
2. Verify the manifest version matches the tag.
3. Verify `source_ref` equals the pushed tag.
4. Run lint, tests, and strict documentation validation.
5. Build wheel and source distribution.
6. Validate distributions.
7. Smoke-test the installed wheel.
9. Generate checksums.
10. Create the GitHub Release and attach its assets.

After the tag workflow completes, verify the GitHub Release contains:

- wheel
- source distribution
- checksums
- release notes

Verify frozen source links now resolve through `blob/vX.Y.Z/`. If frozen source links return 404 before the release tag is pushed, confirm the manifest uses the intended tag; this is expected because the tag does not exist yet. If the links still return 404 after the tag is pushed, verify that the tag exists remotely in GitHub and points to the merged release commit.

Release workflow source lives under [`.github/workflows/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/.github/workflows/). If the workflow fails, report the exact failing step and recovery path.

## 17. Retry, hotfix and rollback guidance

No GitHub authentication: stop and ask the maintainer to authenticate locally. Do not create or push the tag.

Remote access fails: stop before tag creation. Do not assume the remote state.

Tag already exists: do not recreate, delete, move, or force-push it. Inspect the existing tag and release instead.

Validation fails before tag creation: create a focused fix PR against `main`. Do not tag a failing release.

Tag workflow fails after the tag is pushed: do not move or recreate the tag. Inspect the failing workflow step and prepare a focused hotfix PR. Follow the repository's existing release recovery policy.

Frozen source links return 404 before tagging: this is expected because the tag does not exist yet.

Frozen source links return 404 after tagging: verify the tag exists remotely and points to the merged release commit.

For a hotfix, branch from the released tag or production release commit, apply the minimal fix, update the changelog and patch version, refresh release contract pages as needed, validate locally, and tag the new patch release.

GitHub Releases and tags are immutable release evidence. Prefer deprecating a bad release with a clear GitHub Release note and a follow-up patch release instead of deleting or rewriting history.

## 18. Human, AI, generator and automation ownership table

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
| Canonical frozen source reference | Human-approved manifest field | Use `source_ref: vX.Y.Z`; resolved commit SHA is audit metadata only. |
| Tag creation | Human-approved automation | AI pauses before creating or pushing tags. |

## 19. Exact source-code links

- Package configuration: [`pyproject.toml`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/pyproject.toml)
- Package root and exports: [`src/fabricops_kit/__init__.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/__init__.py)
- Public API registry: [`src/fabricops_kit/public_api.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/public_api.py)
- Metadata schema registry: [`src/fabricops_kit/config/metadata_schemas.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/metadata_schemas.py)
- Release manifests: [`docs/releases/manifests/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/docs/releases/manifests/)
- Release workflow automation: [`.github/workflows/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/.github/workflows/)
- Release inventory entry point: [`scripts/generate_release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_release_inventory.py)
- Release inventory implementation: [`scripts/release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/release_inventory.py)
