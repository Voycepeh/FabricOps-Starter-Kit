<!-- Generated file. Edit docs/releases/manifests/0.2.0.yml or the authoritative source metadata and regenerate. -->

# `setup_notebook`

<span class="fabricops-release-status fabricops-release-status--live">Live</span>

Package version: `0.2.0`

Qualified callable: `fabricops_kit.config.setup_notebook.setup_notebook`

Source path: `src/fabricops_kit/config/setup_notebook.py`

Frozen source ref: `v0.2.0`

[View frozen source](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.2.0/src/fabricops_kit/config/setup_notebook.py)

Signature: `setup_notebook(config: 'FrameworkConfig | dict[str, Any]', env: 'str' = 'Sandbox', required_targets: 'list[str] | None' = None, notebook_name: 'str | None' = None, run_id_prefix: 'str' = 'run', local_fallback_name: 'str | None' = None) -> 'NotebookSetupContext'`

## Description

Validate notebook startup configuration and resolve required Fabric targets.

## Parameters

config : FrameworkConfig | dict[str, Any]
    Full FabricOps framework configuration used to resolve environments and
    target stores.
env : str, default="Sandbox"
    Environment section selected for target resolution.
required_targets : list[str] | None, optional
    Logical Fabric target names the notebook requires before execution can
    proceed. Defaults to ``["Source", "Unified"]``.
notebook_name : str | None, optional
    Explicit notebook name override used for runtime metadata and naming
    validation.
run_id_prefix : str, default="run"
    Prefix used only when no Fabric runtime run identifier is available.
local_fallback_name : str | None, optional
    Notebook name used only when neither ``notebook_name`` nor Fabric
    runtime notebook context provides one.

## Return value

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

## Usage notes

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
``01_agreement`` and suffixed variants, ``02_pipeline`` and suffixed
variants, ``03_governance`` and suffixed variants, and ``99_explore`` and
suffixed variants.

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

[Back to release overview](../index.md)
