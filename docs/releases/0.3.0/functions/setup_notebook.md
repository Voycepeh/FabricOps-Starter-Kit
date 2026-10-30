<!-- Generated file. Edit docs/releases/manifests/0.3.0.yml or the authoritative source metadata and regenerate. -->

# `setup_notebook`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.3.0`

Qualified callable: `fabricops_kit.config.setup_notebook.setup_notebook`

Source path: `src/fabricops_kit/config/setup_notebook.py`

Frozen source ref: `v0.3.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.3.0/src/fabricops_kit/config/setup_notebook.py)

Signature: `setup_notebook(config: 'FrameworkConfig | dict[str, Any] | None' = None, workspace_id: 'str | None' = None, required_targets: 'list[str] | None' = None, notebook_name: 'str | None' = None, run_id_prefix: 'str' = 'run', local_fallback_name: 'str | None' = None, *, config_workspace_id: 'str | None' = None) -> 'NotebookSetupContext'`

## Description

Validate notebook startup configuration and resolve required Fabric targets.

## Parameters

config : FrameworkConfig | dict[str, Any] | None, optional
    Explicit configuration for local or advanced use. When omitted, run
    00_env_config in config_workspace_id (or the caller workspace
    when omitted), passing Fabric currentWorkspaceId. The notebook rejects
    unregistered workspaces and returns the workspace_id and FrameworkConfig
    as JSON. Both configuration paths initialize the shared Fabric context
    and apply the configured Spark audit timezone.
workspace_id : str, optional
    Workspace ID for explicit local configuration; Fabric setup derives the caller workspace.
required_targets : list[str] | None, optional
    Logical Fabric target names the notebook requires before execution can
    proceed. When omitted, all stores configured for the selected
    workspace_id are required.
notebook_name : str | None, optional
    Explicit notebook name override used for display and runtime metadata.
run_id_prefix : str, default="run"
    Prefix used only when no Fabric runtime run identifier is available.
local_fallback_name : str | None, optional
    Notebook name used only when neither ``notebook_name`` nor Fabric
    runtime notebook context provides one.

config_workspace_id : str | None, optional
    Workspace hosting 00_env_config for automatic loading. Defaults to the
    caller workspace. Supply a workspace ID only for cross-workspace setup.
    Ignored when config is supplied explicitly.

## Return value

NotebookSetupContext
    A ``NotebookSetupContext`` containing the selected workspace_id,
    resolved Fabric stores, runtime and user identity, startup validation
    results, generated or detected run ID, and overall readiness status.
    Returned fields are ``run_id`` (generated or detected run identifier),
    ``notebook_name`` (resolved notebook name), ``workspace_name``
    (resolved workspace name when available), ``user_name`` (resolved user
    identity), ``workspace_id`` (selected workspace_id key), ``paths``
    (requested target names mapped to resolved Fabric store objects),
    ``validation_results`` (startup check results), ``runtime_metadata``
    (best-effort runtime metadata), and ``readiness_status`` (overall
    readiness outcome).

## Usage notes

With no arguments, load workspace configuration before the startup flow.
By default, use 00_env_config in the current workspace. Advanced callers
may supply config_workspace_id to load a shared deployment in another
workspace. The caller identity comes from
``notebookutils.runtime.context["currentWorkspaceId"]`` through the top-level
``notebookutils`` package; ``environmentWorkspaceId`` and
``config_workspace_id`` never replace it. No configuration load provisions
metadata tables.

Print a startup summary in the calling notebook with the installed FabricOps
version, documentation link, configuration source, and configuration workspace (name when available, ID),
caller workspace, notebook and run identity, resolved workspace_id, audit timezone, metadata schemas,
requested targets, readiness status, and any warning, skipped, or failed
checks. This output is visible even when Fabric keeps the configuration
notebook output in a separate execution snapshot. Explicit configuration
also prints the summary. Both paths publish configuration for setup_pipeline()
and downstream IO. Rerunning notebook setup closes the current pipeline and
invalidates the previous setup before loading configuration, including when
initialization fails. Default I/O also rejects the invalidated configuration;
explicit per-call configuration remains supported. Call setup_pipeline()
again after successful setup.

Startup flow:

1. Validate the supplied FabricOps framework configuration.
2. Resolve the selected workspace_id.
3. Resolve every target listed in ``required_targets``.
4. Default ``required_targets`` to all stores configured for the selected
   workspace_id when omitted.
5. Collect Fabric notebook runtime information when available.
6. Generate a fallback run ID when the Fabric runtime does not provide one.
7. Check whether a Spark session is available.
8. Check whether Fabric runtime context is readable.
9. Validate that each required target contains the necessary store
   identity fields.
10. Retain the notebook name for informational display and audit metadata.
11. Return an overall readiness status.

Current standard templates use ``00_env_config``, ``01_governance``,
and ``02_pipeline``. Notebook names are informational and never determine
pipeline identity or execution eligibility.

Each resolved target contains the configured Fabric store identity needed
by downstream functions, such as workspace identity, Fabric item identity,
store name, store kind, and derived path information where applicable.
``setup.paths`` maps each requested target name to its resolved Fabric
store configuration. Conceptual example:

``setup = setup_notebook(CONFIG, workspace_id="<workspace-id>", required_targets=["Bronze", "Silver", "Gold", "Metadata"])``

``bronze_store = setup.paths["Bronze"]``

``gold_store = setup.paths["Gold"]``

``readiness_status`` is ``"ready"`` when every check is ``pass``,
``warn``, or ``skipped``, and ``"not_ready"`` when any check fails. The
function returns this status to the caller and does not automatically stop
notebook execution merely because readiness is ``"not_ready"``. Caller-side
enforcement is optional but recommended for delivery notebooks. Conceptual
pattern:

``setup = setup_notebook(CONFIG, workspace_id="<workspace-id>", required_targets=["Bronze", "Silver"])``

``if setup.readiness_status != "ready": raise RuntimeError("FabricOps notebook setup is not ready.")``

Runtime metadata is collected on a best-effort basis and includes notebook
name, workspace name and ID, user name and ID, current run ID, whether the
execution is pipeline-driven, whether the execution is interactive, whether
the execution is a reference run, and whether Fabric runtime context is
available. Local or non-Fabric execution may produce warnings or skipped
checks rather than failing automatically.

Validation and smoke checks are local to notebook startup. Startup validation does
not read business data, write business data, persist metadata, provision
workspaces, lakehouses, or warehouses, create missing Fabric resources,
mutate the supplied configuration, or automatically stop notebook execution on failed
readiness checks.

[Back to release overview](../index.md)
