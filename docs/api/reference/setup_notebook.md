# `setup_notebook`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
<span class="reference-chip reference-chip-muted">Public function</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Shared environment setup and runtime validation for notebook templates.

<div class="reference-docstring-intro" markdown="1">

Validate the selected FabricOps environment and resolve the Fabric targets
required by the notebook before downstream IO, profiling, and metadata
functions run. The returned context contains resolved stores, runtime
identity, startup checks, and an overall readiness status.

The main value of ``setup_notebook`` is to provide an early startup
checkpoint for the configuration and Fabric target information that
downstream FabricOps functions rely on, including
``read_lakehouse_table``, ``write_lakehouse_table``,
``read_warehouse_table``, ``read_warehouse_query``, and profiling or
metadata registration functions that resolve Fabric targets or runtime
context. It validates and resolves the same configuration and Fabric
targets used by downstream FabricOps functions, then returns that
information in a reusable ``NotebookSetupContext``. It does not
automatically inject configuration into every downstream function.

</div>

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/setup_notebook.py:20`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_notebook.py#L20-L224">View on GitHub</a>
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
CONTEXT = setup_notebook(CONFIG, env=ENVIRONMENT_NAME, required_targets=["Source", "Unified", "metadata"])
```

</div>

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict[str, Any]` | Yes | Full FabricOps framework configuration used to resolve environments and target stores. |
| `env` | `str` | No | Environment section selected for target resolution. |
| `required_targets` | `list[str] \| None` | No | Logical Fabric target names the notebook requires before execution can proceed. Defaults to ``["Source", "Unified"]``. |
| `notebook_name` | `str \| None` | No | Explicit notebook name override used for runtime metadata and naming validation. |
| `run_id_prefix` | `str` | No | Prefix used only when no Fabric runtime run identifier is available. |
| `local_fallback_name` | `str \| None` | No | Notebook name used only when neither ``notebook_name`` nor Fabric runtime notebook context provides one. |

## Returns

NotebookSetupContext with run_id, notebook_name, workspace_name, user_name, environment, paths, validation_results, runtime_metadata, and readiness_status.

### Return interpretation

A ready context means required targets resolved and startup checks did not fail. Review validation_results when readiness_status is not ready before running downstream notebook cells.

## Raises / Errors

ValueError for invalid configuration sections, missing required paths, or unresolved required targets.

### Common failure causes

- Missing required configuration sections or target names.
- No active Spark session, which is reported as a warning for local fallback mode.
- Fabric notebook runtime utilities are unavailable outside Fabric.
- Workspace, lakehouse, warehouse, or notebook context cannot be resolved.
- Invalid target names or required store identity fields.
- Explicit notebook_name or local_fallback_name is needed when automatic Fabric context is not available.

## Notes

<div class="reference-docstring-notes" markdown="1">

Startup flow:

1. Validate the supplied FabricOps framework configuration.
2. Resolve the selected environment.
3. Resolve every target listed in ``required_targets``.
4. Default ``required_targets`` to ``["Source", "Unified"]`` when
   omitted.
5. Collect Fabric notebook runtime information when available.
6. Generate a fallback run ID when the Fabric runtime does not provide one.
7. Check whether a Spark session is available.
8. Check whether Fabric runtime context is readable.
9. Validate that each required target contains the necessary store
   identity fields.
10. Validate the notebook name against supported FabricOps notebook naming
    patterns.
11. Return an overall readiness status.

Supported notebook naming patterns currently include ``00_env_config``,
``01_governance`` and suffixed variants, ``02_pipeline`` and suffixed
variants, and ``99_explore`` and suffixed variants.

Each resolved target contains the configured Fabric store identity needed
by downstream functions, such as workspace identity, Fabric item identity,
store name, store kind, and derived path information where applicable.
``setup.paths`` maps each requested target name to its resolved Fabric
store configuration. Conceptual example:

``setup = setup_notebook(CONFIG, env="Development", required_targets=["Source", "Unified", "Warehouse"])``

``source_store = setup.paths["Source"]``

``warehouse_store = setup.paths["Warehouse"]``

``readiness_status`` is ``"ready"`` when every check is ``pass``,
``warn``, or ``skipped``, and ``"not_ready"`` when any check fails. The
function returns this status to the caller and does not automatically stop
notebook execution merely because readiness is ``"not_ready"``. Caller-side
enforcement is optional but recommended for delivery notebooks. Conceptual
pattern:

``setup = setup_notebook(CONFIG, env="Development", required_targets=["Source", "Unified"])``

``if setup.readiness_status != "ready": raise RuntimeError("FabricOps notebook setup is not ready.")``

Runtime metadata is collected on a best-effort basis and includes notebook
name, workspace name and ID, user name and ID, current run ID, whether the
execution is pipeline-driven, whether the execution is interactive, whether
the execution is a reference run, and whether Fabric runtime context is
available. Local or non-Fabric execution may produce warnings or skipped
checks rather than failing automatically.

Validation and smoke checks are local to notebook startup. This helper does
not read business data, write business data, persist metadata, provision
workspaces, lakehouses, or warehouses, create missing Fabric resources,
mutate the supplied configuration, globally attach setup context to all
downstream calls, or automatically stop notebook execution on failed
readiness checks.

</div>

## See also

- [Templates](../../notebook-templates.md)
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
| Live | 0.2.0 |

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
