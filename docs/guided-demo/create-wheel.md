# Create Wheel

Build the local FabricOps wheel before setting up Fabric artifacts so the Microsoft Fabric Environment can install the same package version you will use in the guided demo.

## Prerequisites

- VS Code or another editor.
- Git.
- Python `>=3.11`.
- `uv`.
- Repository cloned locally.
- Microsoft Fabric workspace and Environment access for upload.

## 1. Prepare the local repo

From the repository root:

```bash
git checkout main
git pull
uv sync --extra docs
```

## 2. Validate before build

Run local validation before packaging:

```bash
uv run python -m compileall src tests
uv run python -m pytest -q
```

## 3. Build the wheel

```bash
uv build
```

## 4. Confirm the wheel appears in `dist/`

Build artifacts are written to `dist/`:

- `dist/*.whl`
- `dist/*.tar.gz`

For Fabric custom libraries, keep the `.whl` artifact ready for upload to the Microsoft Fabric Environment in [Setup Fabric Artifacts](setup-fabric-artifacts.md).

!!! tip "What file am I uploading?"
    - **Upload:** `dist/*.whl`
    - **Do not upload:** the repository folder, a `.zip`, the `.tar.gz` source distribution, or `uv.lock`.
    - **If multiple wheels exist:** use the latest version/date, or clean `dist/` and rebuild so there is only one wheel to choose from.

## Versioning before rebuild

Every wheel should have a clear version number. This makes it easier to track which Fabric Environment is running which framework version.

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

Use a **patch** bump for bug fixes, docs-compatible packaging fixes, or small internal fixes:

```text
0.1.0 -> 0.1.1
```

Use a **minor** bump for new functions, workflow behavior changes, or new framework capabilities:

```text
0.1.1 -> 0.2.0
```

Use a **major** bump for breaking changes, or when the framework is stable enough for a formal release:

```text
0.2.0 -> 1.0.0
```

!!! warning "Do not reuse wheel versions"
    Do not upload different wheel contents using the same version number. Fabric Environments may cache or retain package versions, so reusing a version can make it unclear which code is installed.

### Manual version bump steps

1. Open `pyproject.toml` and update `[project].version`.
2. Open `src/fabricops_kit/__init__.py` and update `__version__`.
3. Save both files.
4. Validate the repository.
5. Build with `uv build`.
6. Confirm `dist/` contains the updated wheel, for example `dist/fabricops_kit-0.1.1-py3-none-any.whl`.

### Recommended release checklist

Before uploading a new wheel to Fabric:

1. Pull latest `main`.
2. Decide the version bump type.
3. Update `pyproject.toml`.
4. Update `src/fabricops_kit/__init__.py`.
5. Run compile validation.
6. Run tests.
7. Run `uv build`.
8. Upload the `.whl` from `dist/` to the Fabric Environment.
9. Record which Fabric Environment uses which wheel version.
10. Commit and tag the release when preparing an actual package release.

## Expected result

You have a FabricOps `.whl` file in `dist/` ready to upload to a Microsoft Fabric Environment.

Next, continue to [Setup Fabric Artifacts](setup-fabric-artifacts.md).
