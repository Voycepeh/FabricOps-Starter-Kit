# Release Workflow

Use this checklist when preparing a new FabricOps Starter Kit release. FabricOps uses a GitHub-only release process: a `vMAJOR.MINOR.PATCH` tag identifies the immutable source commit, and the GitHub release publishes the wheel, source distribution, checksums, and release notes.

## Release checklist

1. **Complete source changes**
   - Merge or finish the focused implementation, notebook-template, or documentation changes intended for the release.
   - Keep package version, source commit, agreement version, and pipeline version as separate traceability concepts.

2. **Run targeted tests**
   - Run the checks that match the change scope.
   - For normal source changes, use the repository validation baseline:

     ```bash
     uv run python -m compileall src tests
     uv run python -m pytest -q
     uv run ruff check .
     ```

   - Before release sign-off, also run the release-compatible checks used by automation:

     ```bash
     uv sync --frozen
     uv run ruff check .
     uv run pytest
     uv run mkdocs build --strict
     ```

3. **Regenerate required architecture and reference artifacts**
   - For function-level source changes that affect callable structure, exports, helper relationships, source locations, architecture classification, or public-flow metrics, regenerate the committed call-flow contract:

     ```bash
     PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py
     ```

   - Before tagging a release, refresh the generated function reference pages and release contract pages so the release commit contains the shipped contract evidence:

     ```bash
     PYTHONPATH=src python scripts/generate_individual_function_reference_pages.py
     PYTHONPATH=src python scripts/generate_release_inventory.py --check
     PYTHONPATH=src python scripts/generate_release_contract_pages.py
     ```

   - Do not manually edit generated outputs as source of truth. Update source inputs or generator logic first, then regenerate.

4. **Verify public API changes**
   - Confirm the release-facing callable boundary in `fabricops_kit.public_api.SUPPORTED_PUBLIC_API`.
   - Run the public contract and callable architecture tests.
   - Confirm notebook templates and public guidance use supported root imports rather than internal package paths.
   - Use the [Public API & Architecture](public-api-architecture.md) page for the maintainer review links.

5. **Update version and release notes**
   - Choose the smallest semantic version bump that communicates public impact:

     | Bump | Use when |
     | --- | --- |
     | Patch | Backward-compatible fixes, documentation corrections, and non-breaking notebook-template improvements. |
     | Minor | Backward-compatible public APIs, new notebook capabilities, new optional configuration, or additive metadata/rule formats. |
     | Major | Breaking changes to Python APIs, notebook contracts, configuration structures, metadata schemas, agreement or pipeline contracts, or data-quality rule formats. |

   - Move completed `CHANGELOG.md` entries from `Unreleased` into `## [X.Y.Z] - YYYY-MM-DD`.
   - Update `pyproject.toml` `[project].version` to `X.Y.Z`.
   - Update `src/fabricops_kit/__init__.py` `__version__` to `X.Y.Z`.
   - Refresh or add `docs/releases/<version>/` contract pages when preparing an actual release.

6. **Build the wheel**
   - Build from the repository root:

     ```bash
     uv build
     ```

   - Fabric custom library upload uses the wheel in `dist/`, for example:

     ```text
     dist/fabricops_kit-X.Y.Z-py3-none-any.whl
     ```

   - Do not reuse wheel versions. If a wheel was already uploaded or published, bump the version for changed contents.

7. **Build release assets**
   - Validate distributions:

     ```bash
     uvx twine check dist/*
     ```

   - The tag workflow also creates `dist/SHA256SUMS.txt`, installs the wheel in a clean temporary environment, and tests imports from the package `__all__` surface.

8. **Publish the GitHub release**
   - Create an annotated tag only after version, changelog, generated references, release contracts, and validation are ready:

     ```bash
     git tag -a vX.Y.Z -m "FabricOps Starter Kit vX.Y.Z"
     git push origin vX.Y.Z
     ```

   - The release workflow runs for tags matching `v*.*.*`, verifies the tag matches `pyproject.toml`, builds assets, and creates the GitHub Release with the matching changelog section as release notes.

9. **Verify release artifacts**
   - Confirm the GitHub Release contains the wheel, source distribution, checksums, and release notes.
   - Confirm the root documentation site remains the evolving product documentation and that version-specific contracts are available under [Releases](../releases/index.md).
   - Record which Fabric Environment uses which wheel version after upload.

## Retry and hotfix guidance

If automation fails before the GitHub Release is created, fix the problem and push a new annotated tag for the corrected release commit. Do not rewrite a published release tag.

For a hotfix, branch from the released tag or production release commit, apply the minimal fix, update the changelog and patch version, refresh release contract pages as needed, validate locally, and tag the new patch release.

## Supporting references

- [Public API & Architecture](public-api-architecture.md)
- [Generators](generators.md)
- [Releases](../releases/index.md)
