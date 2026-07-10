# Release Workflow

Use this checklist when preparing a new FabricOps Starter Kit release. The release manifest is the centre of the workflow: source registries decide what exists, the generator synchronises discovered assets, the maintainer decides each asset's lifecycle status, release tooling renders the release contract, and the tag workflow publishes immutable assets.

```text
Source registries decide what exists
        ↓
Generator discovers and synchronises it
        ↓
Maintainer decides Preview / Live / Discontinued
        ↓
Generator compares and renders New / Updated / Unchanged
        ↓
Maintainer approves changelog and release narrative
        ↓
Tag workflow builds and publishes immutable assets
```

## 1. Decide release scope

Decide what the release is meant to ship before editing the release manifest:

- public functions that should enter or leave the supported public API boundary
- metadata tables or schema changes that should be supported
- notebook templates that should be included in the release package
- DQ rules that should be documented and supported
- breaking changes, upgrade instructions, and user-facing release motivation

An LLM may help draft a release summary from maintainer instructions and merged PR summaries, but it must not decide semantic version impact, lifecycle status, or whether a breaking change is acceptable.

## 2. Implement and test changes

Complete the source, notebook, documentation, or generator changes intended for the release. Run checks that match the change scope. For normal source changes, use the repository validation baseline:

```bash
uv run python -m compileall src tests
uv run python -m pytest -q
uv run ruff check .
```

For function-level source changes that affect callable structure, exports, helper relationships, source locations, architecture classification, or public-flow metrics, refresh the committed call-flow contract:

```bash
PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
```

## 3. Set the package version

Choose the smallest semantic version bump that communicates public impact:

| Bump | Use when |
| --- | --- |
| Patch | Backward-compatible fixes, documentation corrections, and non-breaking notebook-template improvements. |
| Minor | Backward-compatible public APIs, new notebook capabilities, new optional configuration, or additive metadata/rule formats. |
| Major | Breaking changes to Python APIs, notebook contracts, configuration structures, metadata schemas, agreement or pipeline contracts, or data-quality rule formats. |

Update the version before synchronising the release inventory:

1. Set `pyproject.toml` `[project].version` to `X.Y.Z`.
2. Set `src/fabricops_kit/__init__.py` `__version__` to `X.Y.Z`.
3. Keep package version, source commit, agreement version, and pipeline version as separate traceability concepts.

The inventory generator reads the target release version from `pyproject.toml`.

## 4. Generate or synchronise the release manifest

The version-specific release manifest is the lifecycle decision file:

```text
docs/releases/manifests/<version>.yml
```

It covers four release asset groups:

- `functions`
- `metadata_tables`
- `templates`
- `dq_rules`

Source registries determine whether an asset exists. The release manifest determines that asset's lifecycle status for the version.

| Asset group | Discovered from | Maintainer implication |
| --- | --- | --- |
| `functions` | `fabricops_kit.public_api.SUPPORTED_PUBLIC_API` | Adding a function to Python source alone does not make it release-facing. It must be included in the supported public API boundary to enter the release inventory. |
| `metadata_tables` | `src/fabricops_kit/config/metadata_schemas.py` canonical metadata schema registry | A metadata table enters the inventory when it is registered in the canonical schema registry. |
| `templates` | `templates/notebooks/*.ipynb` | A notebook file in this directory enters the generated inventory. |
| `dq_rules` | `guardrails_shared.DQ_RULE_TYPES` | A rule implementation that is not registered in `DQ_RULE_TYPES` is not part of the release inventory. |

Synchronise the manifest after setting the package version:

```bash
PYTHONPATH=src python scripts/generate_release_inventory.py
```

The actual CLI supports `--check` for validation only:

```bash
PYTHONPATH=src python scripts/generate_release_inventory.py --check
```

Newly discovered assets default to `preview`. The generator must not automatically promote assets to `live`.

## 5. Review new, updated, unchanged, and discontinued assets

Open the release manifest and review every changed group:

```text
docs/releases/manifests/<version>.yml
```

Use the release inventory and generated release pages to distinguish lifecycle status from release change type:

- lifecycle status: `preview`, `live`, `discontinued`
- release change type: New, Updated, Unchanged, Removed, or Discontinued

Do not encode `updated` as a lifecycle status. Updated labels should come from deterministic comparison with prior release contracts, fingerprints, source metadata, or other release-tooling evidence.

### Classify each release change

| Case | Manifest treatment | Expected release contract result |
| --- | --- | --- |
| New Preview asset | `status: preview` and `introduced_in: X.Y.Z` | New and Preview. |
| New Live asset | `status: live`, `introduced_in: X.Y.Z`, and `live_since: X.Y.Z` | New and Live. |
| Updated Live asset | Preserve `status: live` and `live_since: <original version>`. | Updated and Live when deterministic comparison identifies a change. |
| Updated Preview asset | Keep `status: preview`. | Updated and Preview when deterministic comparison identifies a change. |
| Unchanged asset | Preserve prior lifecycle fields. | Unchanged unless maintainer metadata or notes changed. |
| Discontinued asset | `status: discontinued`, `discontinued_in: X.Y.Z`, and `rationale: <human explanation>`. | Discontinued. |

An asset removed from source is not sufficiently managed by deletion alone. The inventory synchroniser rejects previously tracked assets that disappear from source unless they were explicitly marked `discontinued` in the manifest first.

## 6. Promote Preview assets to Live

Promotion is an intentional maintainer decision.

1. Set the target release version in `pyproject.toml`.
2. Create or synchronise `docs/releases/manifests/<version>.yml`:

   ```bash
   PYTHONPATH=src python scripts/generate_release_inventory.py
   ```

3. Open `docs/releases/manifests/<version>.yml`.
4. Find the relevant item under one of:

   ```yaml
   functions:
   metadata_tables:
   templates:
   dq_rules:
   ```

5. Change:

   ```yaml
   status: preview
   ```

   to:

   ```yaml
   status: live
   live_since: X.Y.Z
   ```

6. Add or update human-owned fields where useful:

   ```yaml
   notes:
   rationale:
   introduced_in:
   description:
   purpose:
   managed_by:
   ```

7. Regenerate the release inventory and release contract pages.
8. Review the generated release pages before tagging.

`live_since` should identify the first release where the asset became Live. Do not reset `live_since` during ordinary updates.

## 7. Write and approve the changelog

`CHANGELOG.md` is not a purely generated file. The maintainer owns the final wording. The changelog records why users should care, not merely which files changed.

Recommended process:

1. Review merged PRs and the generated release inventory comparison.
2. Draft entries under `Unreleased`.
3. Classify entries under `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, and `Security`.
4. Include upgrade instructions and breaking changes where applicable.
5. Move approved entries to `## [X.Y.Z] - YYYY-MM-DD`.

The generator may provide deterministic inventory evidence, but it cannot infer release intent, upgrade impact, breaking-change severity, or user-facing explanation reliably.

An LLM may draft changelog language from human release instructions, merged PR summaries, release inventory differences, and test or migration notes. The maintainer must review and approve it. The LLM must not invent changes, decide semantic version impact, promote Preview assets to Live, or determine whether a breaking change is acceptable.

## 8. Generate release contract pages and references

Use generators for deterministic artifacts; do not manually edit generated contract pages as source of truth.

| Purpose | Command | Expected during release preparation |
| --- | --- | --- |
| Callable architecture contract | `PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py` | Run when function-level source changes affect the committed architecture contract. |
| Individual function reference pages | `PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py` | Run before tagging so the release commit contains current function reference pages. |
| Release inventory | `PYTHONPATH=src python scripts/generate_release_inventory.py` | Run after version and source registries are ready; edit lifecycle fields in the manifest, then rerun. |
| Release contract pages | `PYTHONPATH=src python scripts/generate_release_contract_pages.py` | Run after manifest lifecycle decisions and changelog wording are ready. |
| Call graph dashboard | `PYTHONPATH=src python scripts/generate_public_function_call_flows_dashboard.py` | Run only when intentionally refreshing the published dashboard. |

For validation, use:

```bash
PYTHONPATH=src python scripts/generate_release_inventory.py --check
```

If `--check` reports a missing or stale manifest after a version bump, synchronise the manifest for that version, make the human lifecycle decisions, regenerate release contract pages, then rerun `--check`.

## 9. Validate and build locally

Before release sign-off, run release-compatible checks locally when dependencies are available:

```bash
uv sync --frozen
uv run ruff check .
uv run pytest
uv run mkdocs build --strict
uv build
uvx twine check dist/*
```

For a local wheel import smoke test, install the generated wheel into a clean temporary environment and import the public package surface exposed by `fabricops_kit.__all__`.

## 10. Tag and publish

Create an annotated tag only after the version, release manifest, lifecycle statuses, changelog, generated references, release contracts, and validation are ready:

```bash
git tag -a vX.Y.Z -m "FabricOps Starter Kit vX.Y.Z"
git push origin vX.Y.Z
```

The release workflow runs for tags matching `v*.*.*`. It verifies the tag version matches `pyproject.toml`, runs validation, builds assets, and creates the GitHub Release with the matching changelog section as release notes.

## 11. Verify published assets

After automation completes, confirm the GitHub Release contains:

- wheel
- source distribution
- checksums
- release notes
- notebook pack when configured by the release manifest

Confirm the root documentation site remains the evolving product documentation and that version-specific contracts are available under [Releases](../releases/index.md). Record which Fabric Environment uses which wheel version after upload.

## Ownership summary

| Item | Source of truth | Deterministic or human-owned | Maintainer action |
| --- | --- | --- | --- |
| Package version | `pyproject.toml` | Human-owned | Select semantic version. |
| Function existence | `SUPPORTED_PUBLIC_API` | Human-owned source decision, generator-discovered | Export or remove supported callable. |
| Metadata table existence and schema | canonical schema registry | Human-owned source definition, generator-discovered | Add or update registered schema. |
| Template existence | `templates/notebooks/*.ipynb` | Human-authored, generator-discovered | Add or update committed notebook. |
| DQ rule existence | `DQ_RULE_TYPES` | Human-owned source registry, generator-discovered | Register or remove supported rule type. |
| Lifecycle status | release manifest | Human-owned | Set Preview, Live, or Discontinued. |
| `live_since` | release manifest | Human-owned, generator-preserved | Set once on first Live release. |
| Metadata schema fingerprint | generated release inventory | Deterministic | Never edit manually. |
| Source paths and documentation paths | generated release inventory | Deterministic | Fix source or generator when wrong. |
| New or Updated labels | comparison with prior release | Deterministic where supported | Review the result, do not hand-maintain duplicate flags. |
| Changelog wording | `CHANGELOG.md` | Human-approved | Write or approve release-facing explanation. |
| Release contract pages | release contract generator | Deterministic rendering | Regenerate, review, do not hand-edit. |
| Wheel, sdist, checksums | tag workflow | Deterministic build | Verify published assets. |

## Human, generator, LLM, and automation boundaries

**Human-defined**

- release scope
- semantic version
- Preview, Live, or Discontinued decisions
- public API inclusion
- approval of schemas, templates, and rules
- release motivation
- changelog wording
- breaking-change and upgrade guidance

**Deterministically generated**

- discovered asset lists
- source paths
- documentation paths
- qualified names
- metadata schema fingerprints
- release inventory rendering
- release contract pages
- individual function reference pages
- call-flow architecture JSON
- dashboard HTML where its generator is intentionally run
- wheel, source distribution, and checksums from the tagged commit

**LLM-assisted but human-approved**

- draft changelog entries
- draft release summaries
- draft migration notes
- draft rationale and descriptions
- suggested New or Updated explanations based on deterministic diffs

**Automated after tagging**

- version/tag validation
- test and documentation validation
- package build
- distribution validation
- clean-environment import smoke test
- checksum creation
- GitHub Release creation
- asset attachment

## Retry and hotfix guidance

If automation fails before the GitHub Release is created, fix the problem and push a new annotated tag for the corrected release commit. Do not rewrite a published release tag.

For a hotfix, branch from the released tag or production release commit, apply the minimal fix, update the changelog and patch version, refresh release contract pages as needed, validate locally, and tag the new patch release.

## Supporting references

- [Public API & Architecture](public-api-architecture.md)
- [Generators](generators.md)
- [Releases](../releases/index.md)
