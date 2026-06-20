# Create Wheel

Build the local FabricOps wheel before setting up Fabric artifacts so the Microsoft Fabric Environment can install the same package version you will use in the guided demo.

This page covers only the local build portion of setup. Do not upload anything to Fabric from this page; after the wheel exists, continue to [Setup Fabric Artifacts](setup-fabric-artifacts.md) for the Fabric Environment upload and runtime setup steps.

## Prerequisites

Install or confirm access to the following before you start:

- **Git**, with **Git Bash** available for the commands below on Windows.
- **VS Code**, or another editor you are comfortable using.
- **Python 3.11 or newer**, matching the repository requirement of `requires-python = ">=3.11"`.
- **uv**, the Python package and project manager used by this repository.
- A local clone or opened copy of the `Voycepeh/FabricOps-Starter-Kit` repository.

If `uv` is not installed yet, one simple option is:

```bash
pip install uv
```

For other installers, see the official uv documentation. Then confirm it is available:

```bash
uv --version
```

## 1. Clone or open the repository locally

If you do not have the repository yet, open **Git Bash** and clone it:

```bash
git clone https://github.com/Voycepeh/FabricOps-Starter-Kit.git
cd FabricOps-Starter-Kit
code .
```

If you already have the repository, open it in VS Code or your preferred editor and make sure your terminal is running from the repository root.

Run the remaining local commands from the VS Code terminal or from Git Bash while your current folder is `FabricOps-Starter-Kit`.

## 2. Sync the local environment

From the repository root, update your local branch and synchronize the project environment from `pyproject.toml` and `uv.lock`:

```bash
git checkout main
git pull
uv sync --extra docs
```

Why this command:

- `uv sync` creates or updates the local virtual environment.
- The repository lock file keeps dependency resolution reproducible.
- `--extra docs` installs the documentation dependencies used by `mkdocs build`.

## 3. Validate before build

Run local validation before packaging:

```bash
uv run python -m compileall src tests
uv run python -m pytest -q
```

These checks confirm the package still imports, compiles, and passes its test suite before you package it for Fabric. If validation fails, fix the local issue before building and uploading a wheel.

## 4. Build the wheel

Build the package from the repository root:

```bash
uv build
```

The build writes artifacts under `dist/`. For this project, the Fabric custom library upload should use the wheel file:

```text
dist/fabricops_kit-0.1.0-py3-none-any.whl
```

The exact version number may differ if the project version has changed.

## 5. Confirm the wheel appears in `dist/`

Build artifacts are written to `dist/`:

- `dist/*.whl`
- `dist/*.tar.gz`

For Fabric custom libraries, keep the `.whl` artifact ready for upload to the Microsoft Fabric Environment in [Setup Fabric Artifacts](setup-fabric-artifacts.md).

!!! tip "What file am I uploading later?"
    - **Upload:** `dist/*.whl`
    - **Do not upload:** the repository folder, a `.zip`, the `.tar.gz` source distribution, or `uv.lock`.
    - **If `dist/` does not exist:** run `uv build` from the repository root.
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

### Recommended build checklist

Before uploading a new wheel to Fabric:

1. Pull latest `main`.
2. Decide whether the package version needs to change before rebuilding.
3. Update `pyproject.toml` when a version bump is needed.
4. Update `src/fabricops_kit/__init__.py` when a version bump is needed.
5. Run compile validation.
6. Run tests.
7. Run `uv build`.
8. Confirm the `.whl` from `dist/` is the artifact you will upload in [Setup Fabric Artifacts](setup-fabric-artifacts.md).
9. Record which Fabric Environment uses which wheel version after upload.
10. Commit and tag the release when preparing an actual package release.

## Common issues

### I do not see a `dist/` folder

`dist/` is created by the build step. From the repository root, run:

```bash
uv build
```

If the command fails, read the build error first. A common fix is to refresh the local environment and rerun validation:

```bash
uv sync --extra docs
uv run python -m compileall src tests
uv run python -m pytest -q
uv build
```

### Multiple wheels exist in `dist/`

Use the latest version/date, or clean `dist/` and rebuild so there is only one wheel to choose from:

```bash
rm -rf dist
uv build
```

## Expected result

You have a FabricOps `.whl` file in `dist/` ready to upload to a Microsoft Fabric Environment.

Next, continue to [Setup Fabric Artifacts](setup-fabric-artifacts.md).
