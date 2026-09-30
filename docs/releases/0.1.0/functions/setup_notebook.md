# `setup_notebook`

This page documents `setup_notebook` as released in version `0.1.0`.

Release version: `0.1.0`

<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>

[Current function page](../../../api/reference/setup_notebook.md) · [Release function index](index.md)

Run consolidated FabricOps startup for delivery and optional support notebooks.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/setup_notebook.py:20`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.1.0/src/fabricops_kit/config/setup_notebook.py#L20-L145">View on GitHub</a>
</div>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_notebook(
    config: FrameworkConfig | dict[str, Any],
    env: str='Sandbox',
    required_targets: list[str] | None=None,
    notebook_name: str | None=None,
    run_id_prefix: str='run',
    local_fallback_name: str | None=None,
) -> NotebookSetupContext:
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict[str, Any]` | Yes | Framework configuration object or compatible mapping. The setup flow validates required sections and configured Fabric targets before running readiness checks. |
| `env` | `str` | No | Environment key used to resolve target paths. |
| `required_targets` | `list[str] \| None` | No | Target names that must resolve for ``env``. Defaults to ``["Source", "Unified"]``. |
| `notebook_name` | `str \| None` | No | Explicit notebook name used for runtime metadata and naming checks. |
| `run_id_prefix` | `str` | No | Prefix used when a Fabric runtime run identifier is unavailable. |
| `local_fallback_name` | `str \| None` | No | Notebook name used when neither ``notebook_name`` nor Fabric runtime context provides one. |

## Returns

NotebookSetupContext
    Validated runtime context with resolved paths, smoke-check results,
    runtime metadata, and overall readiness status.

## Raises / Errors

ValueError
    Raised when config sections are invalid or required targets cannot be
    resolved for the selected environment.

<details>
<summary>Maintainer architecture details</summary>

- Downstream callables: 8
- Frozen source ref: `v0.1.0`

</details>
