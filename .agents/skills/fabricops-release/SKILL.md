---
name: FabricOps Release Maintainer
description: Guide an AI coding agent through preparing a FabricOps release, performing deterministic repository work automatically, and pausing for explicit maintainer decisions where human judgement is required.
---

# FabricOps Maintainer Release Guide

This skill is the operational source of truth for FabricOps release preparation. The published human page at `docs/maintainer/index.md` is synchronised from this file; do not maintain a second independent copy of the release workflow.

End-user setup and notebook walkthrough content stays in the Guided Demo. Maintainer-only release curation, packaging, publishing, and recovery guidance belongs here.

## Workflow ownership

FabricOps has one canonical repository validation path.

1. `.github/workflows/ci.yml` owns Ruff, pytest, generated-artifact validation, strict MkDocs build, package build/check, and installed-wheel smoke testing.
2. The same CI workflow uploads the already-built `site/` artifact on successful pushes to `main` and deploys that artifact to GitHub Pages. Pages must not rebuild documentation independently.
3. `.github/workflows/release.yml` owns only tag and release-specific work: release identity checks, release inventory validation, final publication artifact build/check, checksums, release-note extraction, and GitHub Release publication.
4. This release skill must not maintain a second copy of generic CI commands. Before tagging, verify that the candidate `main` commit has passed the canonical CI workflow, then run only release-specific readiness checks documented here.

If generic repository validation needs to change, update CI rather than duplicating the change in Pages, Release, or this skill.

## Agent task structure

Before editing release files or reporting release readiness, resolve:

1. **Context**: target version, candidate commit, release manifest, changelog section, release pages, and current public callable inventory.
2. **Task**: prepare a release PR, validate release-specific readiness, or perform an authenticated local tag/publish step.
3. **Constraints**: package releases cover public functions and metadata schemas; notebook templates, samples, skills, and demos are maintained independently unless explicitly scoped.
4. **Expected output**: updated release files, a release-specific readiness report, or an authenticated-local tag command; never an unverified tag.
5. **Verification**: successful canonical CI for the candidate commit plus release-specific consistency checks and a clean working tree.

## Minimum maintainer workflow

1. Identify the target version from `pyproject.toml`, the intended manifest under `docs/releases/manifests/`, and the candidate commit with `git rev-parse HEAD`.
2. Inspect the release-specific public callable inventory generated from `src/fabricops_kit/public_api.py`; verify all intended Live public functions are represented.
3. Keep package release assets separate from independently maintained notebook templates. Do not copy, freeze, version, package, or stamp templates during package release preparation.
4. Verify release notes in `CHANGELOG.md`, package metadata in `pyproject.toml`, release pages under `docs/releases/`, dashboard data where intentionally refreshed, and standalone function pages where applicable to the release scope.
5. Repair release presentation by fixing the proper source file, manifest, changelog, metadata, or generator. Do not change function implementations merely to repair release presentation.
6. Verify generated outputs originate from their documented generator; do not hand-edit generated pages or inventories as source of truth.
7. Confirm the candidate commit has passed `.github/workflows/ci.yml`.
8. Run `PYTHONPATH=src python scripts/check_release_ready.py vX.Y.Z` and `PYTHONPATH=src python scripts/generate_release_inventory.py --check`.
9. Stop and report blockers instead of tagging an unverified release. Final reports must say either **READY TO TAG** or **NOT READY TO TAG** with supporting evidence.

## What a FabricOps release contains

A FabricOps release currently governs only two formal areas: FabricOps public functions and FabricOps metadata schema. Notebook templates, skills, samples, guided demos, DQ assets, and environment resource bundles are maintained outside the package release contract.

The release manifest is:

```text
docs/releases/manifests/<version>.yml
```

It contains two formal release asset groups:

1. `functions`
2. `metadata_tables`

The canonical frozen source reference is the annotated Git release tag. For release `X.Y.Z`:

```yaml
release_version: X.Y.Z
source_ref: vX.Y.Z
```

Generated frozen source links must use `blob/vX.Y.Z/`. During release preparation those links may return 404 until the tag exists; that is expected.

Source registries decide what exists. The manifest decides whether discovered assets are `preview`, `live`, or `discontinued`.

## Before release preparation

Inspect the latest `main` before mutating:

```bash
git status --short
git branch --show-current
git fetch origin main
git log --oneline -5 origin/main
```

Read at minimum:

1. `pyproject.toml`
2. `CHANGELOG.md`
3. `docs/releases/manifests/`
4. `src/fabricops_kit/public_api.py`
5. `src/fabricops_kit/config/metadata_schemas.py`
6. `.github/workflows/ci.yml`
7. `.github/workflows/release.yml`

Never assume the next version or lifecycle decision.

## Release preparation

The release preparation PR targets `main` and should contain only release-preparation changes.

1. Curate and approve the release inventory and lifecycle decisions.
2. Update `pyproject.toml` only after the maintainer approves the semantic version.
3. Set manifest `release_version` and `source_ref` to the intended release tag.
4. Finalise the changelog.
5. Run only generators required by the release scope.
6. Commit only generated outputs directly owned by those changes.
7. Confirm the release PR passes canonical CI.
8. After merge, confirm the resulting `main` commit also passes canonical CI before creating the release tag.

Formal lifecycle decisions apply only to public functions and metadata tables. Do not classify notebook templates, DQ rules, skills, samples, guided demos, function packets, refactor packets, documentation examples, or environment resource bundles as package release assets.

## Release generators

Run only generators required for the release scope. Do not manually edit generated contract pages.

| Purpose | Command | Primary outputs |
| --- | --- | --- |
| Public call-flow JSON | `PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py` | `docs/reference/_data/public-function-call-flows.json` |
| Individual function references | `PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py` | `docs/api/reference/*.md`, `docs/reference/index.md`, `docs/reference/function-call-graph.md` |
| Release inventory | `PYTHONPATH=src python scripts/generate_release_inventory.py` | `docs/releases/manifests/<version>.yml` |
| Release inventory implementation | `scripts/release_inventory.py` | Shared implementation used by the release inventory entry point |
| Release contract pages | `PYTHONPATH=src python scripts/generate_release_contract_pages.py` | `docs/releases/<version>/`, `docs/releases/index.md` |
| Dashboard | `PYTHONPATH=src python scripts/generate_public_function_call_flows_dashboard.py` | `docs/assets/public-function-call-flows-dashboard.html` |

Do not regenerate the dashboard for an ordinary package release unless the dashboard is intentionally in scope.

## Release-specific readiness

Do not rerun the generic CI checklist here. Canonical CI already owns linting, tests, strict documentation build, generated-artifact validation, package build/check, and installed-wheel smoke testing.

After the release PR is merged, release-specific preflight consists of:

```bash
git fetch origin --tags
git checkout main
git pull --ff-only origin main
git status --short

PYTHONPATH=src python scripts/check_release_ready.py vX.Y.Z
PYTHONPATH=src python scripts/generate_release_inventory.py --check
```

Also verify on GitHub that the current `main` commit has a successful FabricOps CI run. A missing, pending, cancelled, or failed CI run blocks tagging.

Release consistency must agree on:

1. Git tag `vX.Y.Z`
2. package version `X.Y.Z`
3. manifest `release_version: X.Y.Z`
4. manifest `source_ref: vX.Y.Z`
5. changelog release heading `X.Y.Z`
6. frozen release directory `docs/releases/X.Y.Z/`

A mismatch blocks the release.

## Tag and publish

Final tag creation requires Codex Desktop or another authenticated local environment with a clean current `main`, GitHub authentication, and permission to push tags.

Before tag creation:

```bash
git status --short
git fetch origin --tags
git checkout main
git pull --ff-only origin main
git rev-parse HEAD
git ls-remote origin
gh auth status

PYTHONPATH=src python scripts/check_release_ready.py vX.Y.Z
PYTHONPATH=src python scripts/generate_release_inventory.py --check

git tag --list vX.Y.Z
git ls-remote --tags origin refs/tags/vX.Y.Z refs/tags/vX.Y.Z^{}
```

Confirm canonical CI is successful for the exact `main` SHA being tagged.

Create the local annotated tag only after readiness is confirmed:

```bash
git tag -a vX.Y.Z -m "FabricOps Starter Kit vX.Y.Z"
git show --no-patch --decorate vX.Y.Z
git rev-list -n 1 vX.Y.Z
```

Stop before pushing and obtain explicit maintainer approval. Push only the approved tag:

```bash
git push origin vX.Y.Z
```

Never force-push, move, recreate, or rewrite a published release tag.

## Tag workflow contract

The tag-triggered release workflow must remain publication-focused. It should:

1. verify the pushed tag against package and manifest release identity
2. validate the release inventory
3. build the final wheel and source distribution from the tagged commit
4. run distribution metadata checks on the artifacts being published
5. generate SHA256 checksums
6. extract the matching changelog section
7. create the GitHub Release and attach the release assets

It must not rerun Ruff, pytest, strict MkDocs, generic generated-artifact validation, individual reference regeneration, or the installed-wheel smoke test. Those checks belong to canonical CI and must have passed before the tag is created.

## Verify the published release

After the tag workflow completes, verify:

1. the workflow succeeded
2. the GitHub Release exists for the expected tag
3. the release contains the wheel, source distribution, checksums, and release notes
4. frozen `blob/vX.Y.Z/` source links resolve

If the tag workflow fails after the tag is pushed, do not move or recreate the tag. Diagnose the publication-specific failure and prepare a focused hotfix PR when code changes are required.

## Recovery rules

1. No GitHub authentication: stop before tag creation.
2. Candidate commit lacks successful CI: stop and fix CI before tagging.
3. Release-specific readiness fails: prepare a focused fix PR against `main`.
4. Tag already exists: inspect it; do not recreate or move it.
5. Publication workflow fails after tag push: do not rewrite the tag; fix forward.
6. Frozen source links return 404 before tagging: expected.
7. Frozen source links return 404 after tagging: verify the remote tag exists and points to the intended merged commit.

## Ownership summary

| Item | Owner |
| --- | --- |
| Ruff, pytest, generated validation, MkDocs strict build, package validation, wheel smoke | `.github/workflows/ci.yml` |
| GitHub Pages artifact and deployment | `.github/workflows/ci.yml` after successful validation on `main` |
| Release scope, lifecycle, semantic version, changelog approval | Maintainer |
| Release inventory and contract rendering | Deterministic generators |
| Release-specific readiness | This skill plus release-specific scripts |
| Final tagged wheel/sdist, checksums, release notes, GitHub Release | `.github/workflows/release.yml` |
| Tag creation and push | Authenticated local maintainer flow with explicit approval |
