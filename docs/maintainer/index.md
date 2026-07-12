# FabricOps Maintainer Release Guide

This page publishes the same operational workflow used by the `FabricOps Release Maintainer` AI skill. The canonical workflow source is [`.agents/skills/fabricops-release/SKILL.md`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/.agents/skills/fabricops-release/SKILL.md); run [`scripts/sync_maintainer_release_guide.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/sync_maintainer_release_guide.py) after editing the skill.

<!-- FABRICOPS-RELEASE-SKILL-CONTENT:START -->

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
6. Package and notebook-pack builds.
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

A FabricOps release contains a tagged source commit, package artifacts, release notes, release lifecycle evidence, and generated release contract pages. The release manifest is the lifecycle decision file:

```text
docs/releases/manifests/<version>.yml
```

It contains four release asset groups:

- `functions`
- `metadata_tables`
- `templates`
- `dq_rules`

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

Default release workflow:

1. Inspect the latest `main`.
2. Curate and approve the release inventory and lifecycle decisions.
3. Prepare the final release PR from a focused release-preparation branch.
4. Set the manifest to Live with the release date.
5. Set `source_ref` to the intended annotated release tag, such as `v0.1.0`.
6. Finalise the changelog.
7. Generate and commit frozen release documentation using the tag reference.
8. Validate package version, manifest version, source tag, generated artifacts, tests, documentation, wheel, and notebook pack.
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

Template lifecycle decisions have an additional dependency gate, but the gate
applies to the required minimum execution path rather than every cell in the
notebook. Template lifecycle and section maturity are separate: a Preview
template may contain Live sections, and a Live template may contain isolated
Preview sections when those Preview sections are optional and excluded from the
supported path. Do not exclude a notebook from a release merely because the
notebook's overall template lifecycle is Preview.

A template is a versioned workflow container with three release maturity layers:

| Layer | Purpose |
| --- | --- |
| Template lifecycle | Whether the notebook as a whole is `preview` or `live`. |
| Template revision metadata | When the notebook was introduced, promoted, materially updated, and tested. |
| Cell or section maturity | Whether each block is required, optional supported content, or experimental Preview content. |

Use stable logical notebook filenames such as `00_env_config.ipynb`; do not add
package-version suffixes such as `00_env_config_v0_4_0.ipynb`. The exact
notebook file included in a release is frozen by the release tag, release asset,
template metadata, and release manifest. Later releases may update the same
stable notebook filename while Git records the exact released copy. Add an
independent `template_revision` only when a separate per-template revision
identity is genuinely needed.

Template inclusion and promotion are separate concepts:

| Concept | Meaning |
| --- | --- |
| Included in release | The exact notebook file is packaged and pinned to the release tag. |
| Template lifecycle Preview | The notebook as a whole may still evolve materially. |
| Live section | This section forms part of the supported path for the release. |
| Preview section | This section is experimental and may change or be removed. |
| Live template | The complete required execution path and all required dependencies are stable and supported. |

Each template should expose visible top-level metadata in the notebook header,
mirrored where practical in machine-readable notebook metadata. These fields
describe the current repository copy and should be updated only when the
template materially changes:

```yaml
template_id: 00_env_config
template_lifecycle: preview
introduced_in: 0.1.0
live_since: null
last_updated_in: 0.1.0
tested_with: 0.1.0
contains_live_sections: true
contains_preview_sections: true
```

Use the corresponding `template_id` value for `99_explore.ipynb` and update the
version fields to match the release where that template copy was introduced,
materially changed, or tested.

Template sections should be visibly labelled, versioned, and tagged for
automation:

| Section maturity | Meaning | Required tags |
| --- | --- | --- |
| Required | Supported minimum execution path. Must run in order, use only Live dependencies, be covered by notebook validation, require configuration values rather than source-code edits during normal use, and remain compatible within the stated release line. | `fabricops-required`, `fabricops-live` |
| Optional | Supported feature block that may be skipped without breaking the basic workflow. | `fabricops-optional`, `fabricops-live` |
| Preview | Experimental block that may change between releases, depend on Preview functions, require extra setup, be removed later, and be excluded from standard validation. | `fabricops-optional`, `fabricops-preview` |

Each major notebook section should visibly state `Section maturity`, `Required
for normal execution`, `Introduced in`, and `Last updated in`. For example:

```markdown
## Configure Fabric stores

Section maturity: Live
Required for normal execution: Yes
Introduced in: 0.1.0
Last updated in: 0.1.0
```

```markdown
## Agreement and governance configuration

Section maturity: Preview
Required for normal execution: No
Introduced in: 0.1.0
May change without backward compatibility.
```

A Live section is part of the supported release path. A Preview section may
change without backward compatibility or be removed. A Live template may contain
Preview sections only when those sections are optional, isolated, visually
marked, excluded from standard template validation, do not run automatically, do
not affect downstream required cells, and can be removed without breaking the
notebook. The template's required execution path must contain only Live
dependencies.

For `v0.1.0`, include `00_env_config.ipynb` and `99_explore.ipynb` as
version-pinned Preview template artifacts. Their required Fabric I/O path may
contain explicitly marked Live sections, while all other experimental or
incomplete capabilities remain clearly marked Preview.

Expected `v0.1.0` notebook state:

| Template | Template lifecycle | Included since | Contains Live sections | Contains Preview sections |
| --- | --- | --- | --- | --- |
| `00_env_config.ipynb` | Preview | `0.1.0` | Yes | Yes |
| `99_explore.ipynb` | Preview | `0.1.0` | Yes | Yes |

The `v0.1.0` Live section boundary is limited to the stable Fabric I/O path
backed by these Live public functions:

- `read_lakehouse_csv`
- `read_lakehouse_excel`
- `read_lakehouse_parquet`
- `read_lakehouse_table`
- `read_warehouse_query`
- `read_warehouse_table`
- `write_lakehouse_table`
- `write_warehouse_table`

Sections that depend on profiling, agreement workflows, metadata registration,
widgets, DQ rules, notebook registry, governance automation, or other Preview
functions must remain Preview.

Before promoting any template to `live`, the AI must prepare and show a template
dependency report with these fields:

| Field | Required content |
| --- | --- |
| Template | Template ID, source path, lifecycle, `introduced_in`, `live_since`, `last_updated_in`, `tested_with`, and whether it contains Live or Preview sections. |
| Functions | Public functions required for normal required-path execution and each lifecycle status. |
| Config contracts | Configuration contracts or required configuration structures used by the required path and each lifecycle status. |
| Metadata | Metadata tables or schemas read or written by the required path and each lifecycle status. |
| Widgets | Interactive widgets required for normal required-path execution and each lifecycle status. |
| Preview dependencies | Any required-path dependency that is still `preview`, grouped by dependency type. |

A template can become Live only when every required section is classified, every
required-path dependency is Live, required cells run from a clean environment,
required cells need configuration values rather than source-code editing, Preview
sections are isolated, the notebook records `introduced_in`, `live_since`, and
`last_updated_in`, the complete required path is tested against the package
release, and the release pack contains the exact tested notebook. Any required
Preview dependency blocks template promotion. If the dependency report contains
one or more required-path Preview dependencies, keep the template as `preview`,
promote the dependencies first where approved, or defer the template to a later
release.

Templates should generally be among the last release surfaces stabilised, after
the underlying package, metadata, configuration, and widget contracts are stable.
This makes future promotion evidence-based rather than subjective.

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

The preflight must:

1. Validate package, manifest, changelog, and tag alignment.
2. Run targeted tests.
3. Run full validation where supported.
4. Build distributions.
5. Validate the notebook pack.
6. Confirm no tracked files changed.
7. Report whether the release is ready.

Recommended checks include:

```bash
PYTHONPATH=src python scripts/check_release_ready.py vX.Y.Z
uv run ruff check .
uv run pytest
uv run mkdocs build --strict
uv build
uvx twine check dist/*
uv run python scripts/build_release_notebook_pack.py "X.Y.Z" --output-dir dist
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
- notebook-pack contents

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
8. Build the approved Live notebook pack.
9. Generate checksums.
10. Create the GitHub Release and attach its assets.

After the tag workflow completes, verify the GitHub Release contains:

- wheel
- source distribution
- checksums
- release notes
- notebook pack when configured by the release manifest

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
- DQ rule registry: [`src/fabricops_kit/pipeline/guardrails_shared.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/guardrails_shared.py)
- Notebook template directory: [`templates/notebooks/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/)
- Release manifests: [`docs/releases/manifests/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/docs/releases/manifests/)
- Release workflow automation: [`.github/workflows/`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/.github/workflows/)
- Release inventory entry point: [`scripts/generate_release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/generate_release_inventory.py)
- Release inventory implementation: [`scripts/release_inventory.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/release_inventory.py)

<!-- FABRICOPS-RELEASE-SKILL-CONTENT:END -->
