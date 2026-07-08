# Release management

FabricOps Starter Kit uses a GitHub-only release process. A Git tag named `vMAJOR.MINOR.PATCH` identifies one immutable FabricOps release made up of the GitHub source tag, Python wheel, Python source distribution, checksums, GitHub Release, matching changelog section, and frozen release contract pages under `docs/releases/<version>/`.

## Release authority and scope

- Keep the package version explicit in `pyproject.toml` under `[project].version`.
- Do not use `setuptools-scm`, dynamic Git-derived package versions, PyPI publishing, Azure Artifacts, or an alternate build tool in this release flow.
- Build distributions from the tagged commit with `uv build`.
- Use semantic versioning across the public FabricOps surface, including Python APIs, notebook contracts, configuration structures, metadata schemas, agreement and pipeline contract structures, and data-quality rule formats.
- Keep package version, source commit, agreement version, and pipeline version as separate traceability concepts.

## Documentation publishing model

FabricOps publishes one evolving MkDocs product documentation site at the repository GitHub Pages root. The main-branch Pages workflow rebuilds the site and deploys it cleanly to that root location so stale whole-site version directories are not preserved.

Version-specific documentation is limited to frozen release contracts under `docs/releases/<version>/`. Those pages are committed with the release-preparation changes and remain the historical entry point for released package contracts, supported functions, metadata tables, templates, and DQ rules. Tagged releases publish package assets through GitHub Releases, including the wheel, source distribution, checksums, and release notes. A release-pack ZIP may be added there later.

FabricOps does not maintain full-site documentation aliases. Do not publish or document `dev`, `latest`, or `stable` documentation sites, and do not add another parallel documentation traceability abstraction. Use the Releases navigation entry for historical, version-specific contracts.

## Selecting the next semantic version

Use the smallest version bump that communicates the public impact:

| Bump | Use when |
| --- | --- |
| Patch | Backward-compatible fixes, documentation corrections, and non-breaking notebook-template improvements. |
| Minor | Backward-compatible public APIs, new notebook capabilities, new optional configuration, or additive metadata/rule formats. |
| Major | Breaking changes to Python APIs, notebook contracts, configuration structures, metadata schemas, agreement or pipeline contracts, or data-quality rule formats. |

Fabric-specific runtime-only changes should still be evaluated by their effect on the public notebook and metadata contracts.

## Update release files

1. Move completed entries from `CHANGELOG.md` `Unreleased` into a new released section named `## [X.Y.Z] - YYYY-MM-DD`.
2. Use the standard Keep a Changelog categories (`Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, `Security`).
3. Add FabricOps-specific subsections where relevant: `Python package`, `Notebook templates`, `Metadata model`, `Documentation`, `Breaking changes`, and `Upgrade instructions`.
4. Preserve useful existing history and do not invent entries that are not supported by repository history.
5. Update `pyproject.toml` `[project].version` to the exact `X.Y.Z` value.
6. Refresh the release inventory and release contract pages for the version under `docs/releases/<version>/`.

## Refresh generated references and release contracts

Before tagging a release, refresh generated individual function references so the published API reference matches the release commit:

```bash
PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
```

Refresh the release inventory and contract pages:

```bash
PYTHONPATH=src python scripts/generate_release_inventory.py --check
PYTHONPATH=src python scripts/generate_release_contract_pages.py
```

Commit any resulting generated individual function reference page updates and release-contract page updates with the release-prep changes. Routine implementation-only PRs do not need this refresh unless they intentionally change the public API contract, release inventory, release contract pages, or reference catalogue.

## Local validation

Run the same repository-compatible checks that CI and the release workflow run:

```bash
uv sync --frozen
uv run ruff check .
uv run pytest
uv run mkdocs build --strict
uv build
uvx twine check dist/*
```

For a local wheel import smoke test, install the generated wheel into a clean temporary environment and import the public package surface exposed by `fabricops_kit.__all__`.

## Tagging and release trigger

Create an annotated tag only after the changelog, version, generated docs, release contracts, and local validation are ready:

```bash
git tag -a vX.Y.Z -m "FabricOps Starter Kit vX.Y.Z"
git push origin vX.Y.Z
```

The release workflow runs only for tags matching `v*.*.*`. It removes the leading `v`, reads `[project].version` from `pyproject.toml`, and fails if the tag version and package version do not match exactly.

## Final GitHub release sequence

The tag workflow performs the release in this order:

1. Check out full Git history for the tagged commit.
2. Install `uv` and the repository-supported Python version.
3. Install locked project, development, and documentation dependencies.
4. Verify the tag version matches `pyproject.toml`.
5. Run Ruff and tests.
6. Regenerate required reference artifacts.
7. Build strict documentation as validation.
8. Build the wheel and source distribution with `uv build`.
9. Validate distributions with `uvx twine check dist/*`.
10. Install the wheel in a clean temporary environment.
11. Test public imports from the package `__all__` surface.
12. Generate `dist/SHA256SUMS.txt`.
13. Require a matching `CHANGELOG.md` release section for the package version.
14. Create a GitHub Release and attach the wheel, source distribution, and checksums.
15. Use the matching changelog section for release notes.

The release workflow does not deploy a separate full documentation site. The evolving product documentation is deployed from `main`, and release-specific contracts are committed under `docs/releases/<version>/`.

## Retrying failed release automation

If the workflow fails before the GitHub Release is created, fix the problem and push a new annotated tag for the corrected release commit. Do not rewrite a published release tag.

If package validation and GitHub Release creation succeeded but a release asset is missing, prefer publishing a follow-up patch release with corrected evidence instead of rewriting release history.

## Hotfix releases

For a hotfix, branch from the released tag or the commit that contains the production release, apply the minimal fix, update `CHANGELOG.md`, bump the patch version in `pyproject.toml`, refresh the release contract pages as needed, validate locally, and tag the new patch release. Hotfix documentation updates the root product site through the normal main-branch Pages deployment and records version-specific contract changes under the new `docs/releases/<version>/` directory.

## Rollback, deprecation, and follow-up guidance

GitHub Releases and tags are immutable release evidence. Prefer deprecating a bad release with a clear GitHub Release note and a follow-up patch release instead of deleting or rewriting history.

Runtime traceability should continue to record FabricOps package version, notebook or repository commit SHA where available, agreement version, and pipeline version as separate concepts. Do not introduce metadata migrations as part of release administration; add schema migrations in focused follow-up PRs when persistent metadata columns are required.

## Supporting release references

- [Public API contract](../reference/public-api-contract.md): canonical release boundary guidance for the supported notebook-facing functions in `fabricops_kit.public_api.SUPPORTED_PUBLIC_API`.
- [Releases](../releases/index.md): historical, version-specific release contracts and package evidence.
