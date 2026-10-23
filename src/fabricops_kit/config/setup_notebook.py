"""Public owner file for FabricOps notebook setup."""

from __future__ import annotations

from typing import Any

from .shared import FrameworkConfig, NotebookSetupContext, initialize_notebook


def setup_notebook(
    config: FrameworkConfig | dict[str, Any] | None = None,
    env: str = "Sandbox",
    required_targets: list[str] | None = None,
    notebook_name: str | None = None,
    run_id_prefix: str = "run",
    local_fallback_name: str | None = None,
    *,
    config_workspace_id: str | None = None,
) -> NotebookSetupContext:
    """Validate notebook startup configuration and resolve required Fabric targets.

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

    Parameters
    ----------
    config : FrameworkConfig | dict[str, Any] | None, optional
        Explicit configuration for local or advanced use. When omitted, run
        00_env_config in config_workspace_id (or the caller workspace
        when omitted), passing Fabric currentWorkspaceId. The notebook rejects
        unregistered workspaces and returns the environment and FrameworkConfig
        as JSON. This automatic path initializes the shared Fabric context and
        applies the configured Spark audit timezone.
    env : str, default="Sandbox"
        Environment section for explicit config only; automatic setup resolves it from the workspace.
    required_targets : list[str] | None, optional
        Logical Fabric target names the notebook requires before execution can
        proceed. When omitted, all stores configured for the selected
        environment are required.
    notebook_name : str | None, optional
        Explicit notebook name override used for runtime metadata and naming
        validation.
    run_id_prefix : str, default="run"
        Prefix used only when no Fabric runtime run identifier is available.
    local_fallback_name : str | None, optional
        Notebook name used only when neither ``notebook_name`` nor Fabric
        runtime notebook context provides one.

    config_workspace_id : str | None, optional
        Workspace hosting 00_env_config for automatic loading. Defaults to the
        caller workspace. Supply a workspace ID only for cross-workspace setup.
        Ignored when config is supplied explicitly.

    Returns
    -------
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

    Raises
    ------
    RuntimeError
        Automatic setup requires a readable Fabric workspace ID.
    ValueError
        Raised for unregistered workspaces, mismatched configuration responses,
        or when config sections are invalid or required targets cannot be
        resolved for the selected environment.

    Notes
    -----
    With no arguments, load workspace configuration before the startup flow.
    By default, use 00_env_config in the current workspace. Advanced callers
    may supply config_workspace_id to load a shared deployment in another
    workspace. No configuration load provisions metadata tables.

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

    """
    return initialize_notebook(
        config=config, env=env, required_targets=required_targets,
        notebook_name=notebook_name, run_id_prefix=run_id_prefix,
        local_fallback_name=local_fallback_name, config_workspace_id=config_workspace_id,
    )


__all__ = ["setup_notebook"]
