# Setup: Create Wheel

This page explains: how to build a FabricOps Starter Kit wheel for Fabric installation.
Use this when: you need packaging and versioning steps before runtime setup.
Next read: [Setup / Run in Fabric](run-in-fabric.md), [Start](../quick-start.md), [Workspace Operating Model](../how-fabricops-works/workspace-operating-model.md).

## Prerequisites

- VS Code or another editor
- Git
- Python `>=3.11`
- `uv`
- Repository cloned locally
- Microsoft Fabric workspace / Environment access for upload

## Prepare local repo

From the repository root:

```bash
git checkout main
git pull
uv sync --extra docs
```

## Validate before build

Run local validation before packaging:

```bash
uv run python -m compileall src tests
uv run python -m pytest -q
```

## Build wheel

```bash
uv build
```

## Find wheel artifact

Build artifacts are written to `dist/`:

- `dist/*.whl`
- `dist/*.tar.gz`

For Fabric custom libraries, upload the `.whl` artifact.

## Versioning before rebuild

Every wheel should have a clear version number. This makes it easier to track which
Fabric Environment is running which framework version.

The package version should stay aligned in two places:

```toml
# pyproject.toml
[project]
name = "fabricops-kit"
version = "0.1.1"
```

```python
# src/fabricops_kit/__init__.py
__version__ = "0.1.1"
```

### When to bump the version

Use a **patch** bump for bug fixes, docs-compatible packaging fixes, or small internal
fixes:

```text
0.1.0 -> 0.1.1
```

Use a **minor** bump for new functions, workflow behavior changes, or new framework
capabilities:

```text
0.1.1 -> 0.2.0
```

Use a **major** bump for breaking changes, or when the framework is stable enough for a
formal release:

```text
0.2.0 -> 1.0.0
```

!!! warning "Do not reuse wheel versions"
    Do not upload different wheel contents using the same version number.
    Fabric Environments may cache or retain package versions, so reusing a version can
    make it unclear which code is actually installed.

### Manual version bump steps

1. Open `pyproject.toml` and update `[project].version`:

   ```toml
   [project]
   name = "fabricops-kit"
   version = "0.1.1"
   ```

2. Open `src/fabricops_kit/__init__.py` and update:

   ```python
   __version__ = "0.1.1"
   ```

3. Save both files.

4. Validate the repository:

   ```bash
   uv run python -m compileall src tests
   uv run python -m pytest -q
   ```

5. Build:

   ```bash
   uv build
   ```

6. Confirm `dist/` contains the updated wheel:

   ```text
   dist/fabricops_kit-0.1.1-py3-none-any.whl
   ```

### Recommended release checklist

Before uploading a new wheel to Fabric:

1. Pull latest `main`.
2. Decide the version bump type (patch, minor, or major).
3. Update `pyproject.toml`.
4. Update `src/fabricops_kit/__init__.py`.
5. Run compile validation.
6. Run tests.
7. Run `uv build`.
8. Upload the `.whl` from `dist/` to the Fabric Environment.
9. Record which Fabric Environment uses which wheel version.
10. Commit and tag the release.

```bash
git add pyproject.toml src/fabricops_kit/__init__.py
git commit -m "Release fabricops-kit 0.1.1"
git tag v0.1.1
git push
git push origin v0.1.1
```

### Example release flow (0.1.1)

If the current version is `0.1.0` and you fixed a packaging issue:

1. Bump both version values to `0.1.1`.
2. Run local validation commands.
3. Build with `uv build`.
4. Upload `dist/fabricops_kit-0.1.1-py3-none-any.whl` to Fabric.
5. Commit and create tag `v0.1.1`.

Manual versioning is recommended for now because the framework is still evolving.
Git-tag-based automated versioning can be considered later.

## Next step

[Run in Fabric →](run-in-fabric.md)


## Release checklist (merged)

- Verify package version and changelog intent before build.
- Build wheel in a clean environment and confirm artifacts are produced once.
- Install the built wheel locally and run import smoke tests.
- Run project validation (`pytest`, `compileall`, `mkdocs build --strict`) before publishing.
- Record release notes and promotion intent before Fabric deployment.
