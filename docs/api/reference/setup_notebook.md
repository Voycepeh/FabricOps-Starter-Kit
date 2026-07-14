# `setup_notebook`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

## Call-flow summary

- Downstream callables: 8
- Shared helpers: 4
- Private helpers: 4

<a class="reference-source-link" href="../../../assets/public-function-call-flows-dashboard.html?function=setup_notebook">Open Live contract call flow</a>

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

- [Templates](../../notebook-templates-implementation-guide/index.md)
- [Metadata Tables](../../reference/metadata.md)


<details>
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.1.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 7 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.1.0 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.setup_notebook._get_fabric_runtime_metadata</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared._validate_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_current_audit_timestamp</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.validate_framework_config</code></li>
</ul>


</details>

!!! info "Generated reference freshness"
    Reference pages generated: 14 Jul 2026, 1:33 PM SGT
    Call-flow data generated: 13 Jul 2026, 11:33 PM SGT
