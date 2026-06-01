# Install

This page explains the full local-to-Fabric installation workflow for the
FabricOps Starter Kit helper wheel.
Use this when: you want to build the package from this repository and install it
as a Microsoft Fabric Environment custom library.
Next read: [Workspace and Notebook Flow](how-fabricops-works/workspace-and-notebook-flow.md), [Start](quick-start.md),
[Production and Handover](how-fabricops-works/production-and-handover.md).

The flow is:

```text
Local machine → build wheel → upload to Fabric Environment → attach environment → verify import
```

!!! note "Build the wheel locally"
    This project does not require a prebuilt wheel from GitHub Releases. The
    normal workflow is to clone the repository, build `dist/*.whl` locally, and
    upload that wheel to Microsoft Fabric.

## 1. Prerequisites

Install or confirm access to the following before you start:

- **Git**, with **Git Bash** available for the commands below.
- **VS Code**, or another editor you are comfortable using.
- **Python 3.11 or newer**, matching the repository requirement of
  `requires-python = ">=3.11"`.
- **uv**, the Python package and project manager used by this repository.
- Access to a **Microsoft Fabric workspace**.
- Permission to **create or edit a Microsoft Fabric Environment** in that
  workspace.

If `uv` is not installed yet, one simple option is:

```bash
pip install uv
```

For other installers, see the official uv documentation. Then confirm it is
available:

```bash
uv --version
```

## 2. Clone the repository locally

Open **Git Bash** and clone the repository:

```bash
git clone https://github.com/Voycepeh/FabricOps-Starter-Kit.git
cd FabricOps-Starter-Kit
code .
```

This opens the repository in VS Code. Run the remaining local commands from the
VS Code terminal or from Git Bash while your current folder is
`FabricOps-Starter-Kit`.

## 3. Set up the local environment with uv

Synchronize the project environment from `pyproject.toml` and `uv.lock`:

```bash
uv sync --extra docs
```

Why this command:

- `uv sync` creates or updates the local virtual environment.
- The repository lock file keeps dependency resolution reproducible.
- `--extra docs` installs the documentation dependencies used by
  `mkdocs build`.

## 4. Run validation locally

Before building a wheel, run the same lightweight checks used for repository
hygiene:

```bash
uv run python -m compileall src tests
uv run python -m pytest -q
```

These checks confirm the package still imports, compiles, and passes its test
suite before you package it for Fabric. If tests fail, fix the local issue before
building and uploading a wheel.

## 5. Build the wheel

Build the package from the repository root:

```bash
uv build
```

The build writes artifacts under `dist/`. For this project, the Fabric custom
library upload should use the wheel file:

```text
dist/fabricops_kit-0.1.0-py3-none-any.whl
```

The exact version number may differ if the project version has changed.

!!! tip "What file am I uploading?"
    - **Upload:** `dist/*.whl`
    - **Do not upload:** the repository folder, a `.zip`, the `.tar.gz` source
      distribution, or `uv.lock`.
    - **If multiple wheels exist:** use the latest version/date, or clean `dist/`
      and rebuild so there is only one wheel to choose from.

For more detail on versioning and rebuilding wheels, see
[Setup: Create Wheel](setup/create-wheel.md).

## 6. Install the wheel in a Microsoft Fabric Environment

In Microsoft Fabric:

1. Open the target **Fabric workspace**.
2. Create a new **Environment**, or open the Environment that should run your
   FabricOps notebooks.
3. Go to **Libraries** / **Custom libraries**.
4. Upload the generated wheel from your local `dist/` folder, for example
   `dist/fabricops_kit-0.1.0-py3-none-any.whl`.
5. Save or publish the Environment so Fabric applies the library change.
6. Attach the Environment to the notebook or workspace item that will run the
   FabricOps Starter Kit notebook templates.
7. Restart the notebook session if Fabric prompts you, or if the session was
   already running before the Environment was attached.

For first-run runtime checks after the wheel is installed, see
[Setup: Run in Fabric](setup/run-in-fabric.md).

## 7. Verify in a Fabric notebook

After the Environment is published and attached, open a Fabric notebook that uses
that Environment and run:

```python
import fabricops_kit as fsk

print(f"FabricOps Starter Kit version: {fsk.__version__}")
print(f"Available helper count: {len(fsk.__all__)}")
```

If the import works, the helper wheel is available to the notebook runtime. You
can then continue with [Workspace and Notebook Flow](how-fabricops-works/workspace-and-notebook-flow.md) and
[Start](quick-start.md).

If the import fails, the most common cause is that the Environment was uploaded
but not published, not attached to the notebook, or the notebook session has not
been restarted since the attachment changed.

## 8. Common issues

### I do not see a `dist/` folder

`dist/` is created by the build step. From the repository root, run:

```bash
uv build
```

If the command fails, read the build error first. A common fix is to refresh the
local environment and rerun validation:

```bash
uv sync --extra docs
uv run python -m compileall src tests
uv run python -m pytest -q
uv build
```

### Fabric notebook cannot import the package

Check the Fabric setup in this order:

1. The uploaded file is the generated `.whl` from `dist/`.
2. The Environment has been saved or published after the upload.
3. The notebook is attached to that Environment.
4. The notebook session was restarted after attaching or updating the
   Environment.
5. The notebook import uses the module name `fabricops_kit`, not the package
   distribution name `fabricops-kit`.

Use this import check:

```python
import fabricops_kit as fsk
print(fsk.__version__)
```

### I uploaded the wrong file

Remove the incorrect custom library from the Fabric Environment, upload the
correct `dist/*.whl` file, then save or publish the Environment again. Do not
upload the repository folder, a `.zip` of the source, or the `.tar.gz` source
distribution.

### I rebuilt the wheel but Fabric still uses the old version

Fabric Environments can keep using the already published package until the
Environment is updated and the notebook runtime restarts.

Recommended steps:

1. Bump the project version before rebuilding if the wheel contents changed.
2. Run `uv build` again.
3. Upload the new `dist/*.whl` file.
4. Save or publish the Environment.
5. Restart the attached notebook session.
6. Verify `fsk.__version__` in the notebook.

Do not reuse the same version number for different wheel contents; it makes it
hard to know which package Fabric is running.

### Tests fail locally

Do not build and upload a wheel from a failing local checkout. First make sure
you are on the latest `main`, refresh dependencies, and rerun the checks:

```bash
git checkout main
git pull
uv sync --extra docs
uv run python -m compileall src tests
uv run python -m pytest -q
```

If tests still fail, inspect the pytest output and fix the failing code, test,
or local environment issue before running `uv build`.
