# `setup_notebook`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview reference-lifecycle-chip-prominent">Preview</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is available for evaluation but is not part of the supported Live release contract. It may change without backward-compatibility guarantees.

## Call-flow summary

- Downstream callables: 8
- Shared helpers: 4
- Private helpers: 4

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=setup_notebook">Open Preview call flow</a>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-preview">Preview</span> |
| Live since | — |
| Discontinued in | — |
| Contract classification | Preview |
| Live-critical dependencies | 0 |
| Direct Live dependents | 0 |
| Transitive Live dependents | 0 |


Shared environment setup and runtime validation for notebook templates.

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/setup_notebook.py:20`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_notebook.py#L20-L145">View on GitHub</a>
</div>

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">Public Starter Kit function</span>
<span class="reference-chip">00_env_config</span>
</p>

**Used in notebooks:** `00_env_config`

## Usage notes

Use this in the setup notebook to capture and render the key runtime information required by downstream Starter Kit notebooks.

This helps confirm the active environment, configured stores, notebook context, and runtime values before later notebooks depend on them.


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

## Example usage

<div class="reference-example-usage" markdown="1">

```python
context = setup_notebook(CONFIG, env="Sandbox", required_targets=["Source", "Unified"], notebook_name="00_env_config")
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

NotebookSetupContext with resolved configuration paths, runtime metadata, smoke-check results, and readiness status.

### Return interpretation

A ready context means required targets resolved and runtime checks passed. Review validation messages before running downstream cells when readiness is not successful.

## Raises / Errors

ValueError for invalid configuration sections, missing required paths, or unresolved required targets.

### Common failure causes

- The environment name is not present in CONFIG.
- Required targets are missing from path configuration.
- Fabric runtime metadata is unavailable and no local fallback was provided.
- Configured lakehouse or warehouse targets cannot be resolved.

## See also

- [Notebook Templates Implementation Guide](../../notebook-templates-implementation-guide/index.md)
- [Metadata Tables](../../reference/metadata.md)


!!! info "Generated reference freshness"
    Reference pages generated: 08 Jul 2026, 1:08 PM SGT
    Call-flow data generated: 09 Jul 2026, 8:52 PM SGT
