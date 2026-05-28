# Install

This page explains: how to build or download the FabricOps wheel and install it in Microsoft Fabric.
Use this when: you are setting up FabricOps Starter Kit in a new workspace.
Next read: [Templates](notebook-structure.md), [Start](quick-start.md), [Deploy](deployment-and-promotion.md).

## Install path

`Get wheel → Upload to Fabric Environment → Attach to notebook runtime → Verify import`

## Steps

| Step | Action | Result |
| --- | --- | --- |
| 1 | Build the wheel locally with `uv build` (or download a released `.whl`). | You have a versioned `dist/*.whl` package. |
| 2 | Upload the wheel to your Fabric Environment custom libraries. | Wheel is available in Fabric runtime. |
| 3 | Attach the Environment to notebooks or workspace runtime. | Notebooks can import `fabricops_kit`. |
| 4 | Restart session/runtime if prompted by Fabric. | Newly attached library is active. |
| 5 | Verify import in a notebook cell: `import fabricops_kit as fsk`. | Runtime is ready for templates. |

## Build from source (optional)

```bash
uv sync --extra docs
uv run python -m compileall src tests
uv run python -m pytest -q
uv build
```

## After install

- Open template notebooks from [Templates](notebook-structure.md).
- Run the guided sequence on [Start](quick-start.md).
