# `setup_notebook`

<p class="reference-catalogue-item-meta reference-catalogue-item-badges reference-lifecycle-badges">
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live</span>
<span class="reference-chip reference-lifecycle-chip reference-lifecycle-live reference-lifecycle-chip-prominent">Live since 0.1.0</span>
</p>

> This function is part of the supported FabricOps public contract. Changes to its signature, behaviour, public export, or Live-critical dependencies require Live-contract review.

Shared environment setup and runtime validation for notebook templates.

<p class="reference-catalogue-item-meta reference-catalogue-item-badges">
<span class="reference-chip">01_governance</span>
</p>

## Usage notes

Use at the start of a Governance notebook to load and validate FabricOps configuration, resolve required targets, and capture runtime context before other helpers run.


## Example usage

<div class="reference-example-usage" markdown="1">

```python
CONTEXT = setup_notebook()
```

</div>

<details class="reference-signature-details" markdown="1">
<summary>Signature</summary>

## Signature

<div class="reference-api-definition" markdown="1">

```python
def setup_notebook(
    config: FrameworkConfig | dict[str, Any] | None=None,
    env: str='Sandbox',
    required_targets: list[str] | None=None,
    notebook_name: str | None=None,
    run_id_prefix: str='run',
    local_fallback_name: str | None=None,
    *,
    config_workspace_id: str | None=None,
) -> NotebookSetupContext:
```

</div>

</details>

## Parameters

Required describes the Python signature. An optional parameter may still be needed for the selected mode or identity form; see its description. `—` means no signature default.

<div class="reference-input-table" markdown="1">

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `config` | `FrameworkConfig \| dict[str, Any] \| None` | No | `None` | Explicit configuration for local or advanced use. When omitted, run 00_env_config in config_workspace_id (or the caller workspace when omitted), passing Fabric currentWorkspaceId. The notebook rejects unregistered workspaces and returns the environment and FrameworkConfig as JSON. This automatic path initializes the shared Fabric context and applies the configured Spark audit timezone. |
| `env` | `str` | No | `'Sandbox'` | Environment section for explicit config only; automatic setup resolves it from the workspace. |
| `required_targets` | `list[str] \| None` | No | `None` | Logical Fabric target names the notebook requires before execution can proceed. When omitted, all stores configured for the selected environment are required. |
| `notebook_name` | `str \| None` | No | `None` | Explicit notebook name override used for runtime metadata and naming validation. |
| `run_id_prefix` | `str` | No | `'run'` | Prefix used only when no Fabric runtime run identifier is available. |
| `local_fallback_name` | `str \| None` | No | `None` | Notebook name used only when neither ``notebook_name`` nor Fabric runtime notebook context provides one. |
| `config_workspace_id` | `str \| None` | No | `None` | Workspace hosting 00_env_config for automatic loading. Defaults to the caller workspace. Supply a workspace ID only for cross-workspace setup. Ignored when config is supplied explicitly. |

</div>

## Returns

NotebookSetupContext
    A ``NotebookSetupContext`` containing the selected environment,
    resolved Fabric stores, runtime and user identity, startup validation
    results, generated or detected run ID, and overall readiness status.
    Returned fields are ``run_id`` (generated or detected run identifier),
    ``notebook_name`` (resolved notebook name), ``workspace_name``
    (resolved workspace name when available), ``user_name`` (resolved user
    identity), ``environment`` (selected environment key), ``paths``
    (requested target names mapped to resolved Fabric store objects),
    ``validation_results`` (startup check results), ``runtime_metadata``
    (best-effort runtime metadata), and ``readiness_status`` (overall
    readiness outcome).

### Return interpretation

A ready context means required targets resolved and startup checks did not fail. Review validation_results when readiness_status is not ready before running downstream notebook cells.

## Raises / Errors

RuntimeError
    Automatic setup requires notebookutils, an available Fabric runtime
    context, and currentWorkspaceId. Unexpected runtime access or
    configuration notebook execution failures are reported separately.
ValueError
    Raised for unregistered workspaces, mismatched configuration responses,
    or when config sections are invalid or required targets cannot be
    resolved for the selected environment.

### Common failure causes

- Missing required configuration sections or target names.
- No active Spark session, which is reported as a warning for local fallback mode.
- Fabric notebook runtime utilities are unavailable outside Fabric.
- Workspace, lakehouse, warehouse, or notebook context cannot be resolved.
- Invalid target names or required store identity fields.
- Explicit notebook_name or local_fallback_name is needed when automatic Fabric context is not available.

## Notes

<div class="reference-docstring-notes" markdown="1">

With no arguments, load workspace configuration before the startup flow.
By default, use 00_env_config in the current workspace. Advanced callers
may supply config_workspace_id to load a shared deployment in another
workspace. The caller identity comes from
``notebookutils.runtime.context["currentWorkspaceId"]`` through the top-level
``notebookutils`` package; ``environmentWorkspaceId`` and
``config_workspace_id`` never replace it. No configuration load provisions
metadata tables.

Print a startup summary in the calling notebook with the installed FabricOps
version, documentation link, configuration source, caller workspace, notebook
and run identity, resolved environment, audit timezone, metadata schemas,
requested targets, readiness status, and any warning, skipped, or failed
checks. This output is visible even when Fabric keeps the configuration
notebook output in a separate execution snapshot. Explicit configuration
also prints the summary.

Startup flow:

1. Validate the supplied FabricOps framework configuration.
2. Resolve the selected environment.
3. Resolve every target listed in ``required_targets``.
4. Default ``required_targets`` to all stores configured for the selected
   environment when omitted.
5. Collect Fabric notebook runtime information when available.
6. Generate a fallback run ID when the Fabric runtime does not provide one.
7. Check whether a Spark session is available.
8. Check whether Fabric runtime context is readable.
9. Validate that each required target contains the necessary store
   identity fields.
10. Validate the notebook name against supported FabricOps notebook naming
    patterns.
11. Return an overall readiness status.

Current standard templates use ``00_env_config``, ``01_governance``,
and ``02_pipeline``. Governance and pipeline names can include suffixes
for project-specific workflows.

Each resolved target contains the configured Fabric store identity needed
by downstream functions, such as workspace identity, Fabric item identity,
store name, store kind, and derived path information where applicable.
``setup.paths`` maps each requested target name to its resolved Fabric
store configuration. Conceptual example:

``setup = setup_notebook(CONFIG, env="Development", required_targets=["Bronze", "Silver", "Gold", "Metadata"])``

``bronze_store = setup.paths["Bronze"]``

``gold_store = setup.paths["Gold"]``

``readiness_status`` is ``"ready"`` when every check is ``pass``,
``warn``, or ``skipped``, and ``"not_ready"`` when any check fails. The
function returns this status to the caller and does not automatically stop
notebook execution merely because readiness is ``"not_ready"``. Caller-side
enforcement is optional but recommended for delivery notebooks. Conceptual
pattern:

``setup = setup_notebook(CONFIG, env="Development", required_targets=["Bronze", "Silver"])``

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
mutate the supplied configuration, or automatically stop notebook execution on failed
readiness checks.

</div>

## Behavior and scope

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
information in a reusable ``NotebookSetupContext``. It
initializes the shared context when configuration is loaded automatically.

</div>

## See also

- [Templates](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks)
- [Metadata Tables](../../reference/metadata.md)

<div class="reference-source-card" markdown="1">
**Source**

`fabricops_kit/config/setup_notebook.py:10`

<a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config/setup_notebook.py#L10-L174">View on GitHub</a>
</div>


<details class="reference-implementation-details" markdown="1">
<summary>Maintainer architecture details</summary>

## Contract impact

| Property | Value |
| --- | --- |
| Lifecycle | <span class="reference-chip reference-lifecycle-chip reference-lifecycle-live">Live</span> |
| Live since | 0.1.0 |
| Discontinued in | — |
| Contract classification | Live public function |
| Contract risk | Live |
| Live-critical dependencies | 11 |

### Release history

| Status | Version |
| --- | --- |
| Live | 0.1.0 |
| Live | 0.2.0 |
| Live | 0.2.5 |

### Live-critical dependencies

<ul class="reference-compact-list">
<li><code>fabricops_kit.config.shared._get_fabric_runtime_context</code></li>
<li><code>fabricops_kit.config.shared._get_fabric_runtime_metadata</code></li>
<li><code>fabricops_kit.config.shared._normalize_path_config</code></li>
<li><code>fabricops_kit.config.shared._print_notebook_setup_summary</code></li>
<li><code>fabricops_kit.config.shared._validate_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_audit_timezone</code></li>
<li><code>fabricops_kit.config.shared.get_current_audit_timestamp</code></li>
<li><code>fabricops_kit.config.shared.get_store</code></li>
<li><code>fabricops_kit.config.shared.initialize_notebook</code></li>
<li><code>fabricops_kit.config.shared.validate_framework_config</code></li>
<li><code>fabricops_kit.io.shared.get_spark_session</code></li>
</ul>


</details>
