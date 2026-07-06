# Release management

FabricOps Starter Kit uses a GitHub-only release process. A Git tag named `vMAJOR.MINOR.PATCH` identifies one immutable FabricOps release made up of the GitHub source tag, Python wheel, Python source distribution, GitHub Release, matching changelog section, and versioned Mike documentation snapshot.

## Release authority and scope

- Keep the package version explicit in `pyproject.toml` under `[project].version`.
- Do not use `setuptools-scm`, dynamic Git-derived package versions, PyPI publishing, Azure Artifacts, or an alternate build tool in this release flow.
- Build distributions from the tagged commit with `uv build`.
- Use semantic versioning across the public FabricOps surface, including Python APIs, notebook contracts, configuration structures, metadata schemas, agreement and pipeline contract structures, and data-quality rule formats.
- Keep package version, documentation version, Git commit SHA, agreement version, and pipeline version as separate traceability concepts.

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

## Refresh generated references

Before tagging a release, refresh generated individual function references so the published API reference matches the release commit:

```bash
PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
```

Commit any resulting generated individual function reference page updates with the release-prep changes. Routine implementation-only PRs do not need this refresh unless they intentionally change the public API contract or reference catalogue.

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

Create an annotated tag only after the changelog, version, generated docs, and local validation are ready:

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
5. Run Ruff, tests, and `mkdocs build --strict`.
6. Build the wheel and source distribution with `uv build`.
7. Validate distributions with `uvx twine check dist/*`.
8. Require a matching `CHANGELOG.md` release section for the package version.
9. Install the wheel in a clean temporary environment.
10. Test stable public imports from the package `__all__` surface.
11. Generate `dist/SHA256SUMS.txt`.
12. Create a GitHub Release and attach the wheel, source distribution, and checksums.
13. Use the matching changelog section for release notes.
14. Deploy the versioned documentation with Mike only after package and documentation checks pass.

## Mike documentation versioning

Python package releases and Mike documentation snapshots both retain the full semantic version, such as `0.8.1`. This keeps each documentation snapshot aligned to the exact released wheel.

| Git tag | Package version | Mike version |
| --- | --- | --- |
| `v0.8.0` | `0.8.0` | `0.8.0` |
| `v0.8.1` | `0.8.1` | `0.8.1` |
| `v0.9.0` | `0.9.0` | `0.9.0` |
| `v1.0.0` | `1.0.0` | `1.0.0` |

The release workflow derives `DOC_VERSION` from the full package version and deploys with Mike after validation succeeds:

```bash
uv run mike deploy \
  --push \
  --update-aliases \
  "${DOC_VERSION}" \
  latest \
  stable
uv run mike set-default --push latest
```

`latest` points to the newest released documentation. `stable` points to the recommended production documentation. For the initial GitHub-only release implementation, `latest` and `stable` move together unless maintainers document a deliberate distinction. The optional `dev` alias may be updated from `main` for preview documentation, but `main` is never promoted automatically to `latest`.

## Retrying failed documentation deployment

If the workflow fails before the GitHub Release is created, fix the problem and push a new annotated tag for the corrected release commit. Do not rewrite a published release tag.

If package validation and GitHub Release creation succeeded but the Mike deployment failed, rerun the failed workflow job from GitHub Actions after fixing the documentation deployment issue. The Mike commands are idempotent for the same documentation version and aliases because they use `--update-aliases`.

## Hotfix releases

For a hotfix, branch from the released tag or the commit that contains the production release, apply the minimal fix, update `CHANGELOG.md`, bump the patch version in `pyproject.toml`, validate locally, and tag the new patch release. Patch hotfix documentation publishes a new full-version Mike snapshot and updates the title and aliases to the new full package version.

## Rollback, deprecation, and follow-up guidance

GitHub Releases and tags are immutable release evidence. Prefer deprecating a bad release with a clear GitHub Release note and a follow-up patch release instead of deleting or rewriting history. Move `stable` back to the recommended documentation version only when maintainers explicitly decide that the newest release should not be the production recommendation.

Runtime traceability should continue to record FabricOps package version, notebook or repository commit SHA where available, agreement version, and pipeline version as separate concepts. Do not introduce metadata migrations as part of release administration; add schema migrations in focused follow-up PRs when persistent metadata columns are required.

## Supporting release references

- [Public API contract](../reference/public-api-contract.md): canonical release boundary guidance for the supported notebook-facing functions in `fabricops_kit.public_api.SUPPORTED_PUBLIC_API`.
- [Release traceability](../release-info.md): published release traceability and release evidence.
- [Documentation versioning](docs-versioning.md): docs versioning expectations for release preparation.
