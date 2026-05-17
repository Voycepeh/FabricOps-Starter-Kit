# Create Wheel

## Purpose

FabricOps Starter Kit is installed into Microsoft Fabric as a Python wheel.
Use this page to prepare your local repository, validate locally, and build the wheel
you will upload to a Fabric Environment.

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

Before rebuilding and uploading a new wheel:

- Keep `pyproject.toml` `[project].version` and
  `src/fabricops_kit/__init__.py` `__version__` aligned.
- Use a patch bump for fixes.
- Use a minor bump for new capabilities.
- Do not upload different wheel contents using the same version.

## Next step

[Run in Fabric →](run-in-fabric.md)
