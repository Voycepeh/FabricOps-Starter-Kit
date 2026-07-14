"""Public owner file for FabricOps notebook setup."""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any
from uuid import uuid4

from .shared import (
    ConfigSmokeCheckResult,
    FrameworkConfig,
    NotebookSetupContext,
    get_current_audit_timestamp,
    get_store,
    validate_framework_config,
)


def setup_notebook(
    config: FrameworkConfig | dict[str, Any],
    env: str = "Sandbox",
    required_targets: list[str] | None = None,
    notebook_name: str | None = None,
    run_id_prefix: str = "run",
    local_fallback_name: str | None = None,
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
    information in a reusable ``NotebookSetupContext``. It does not
    automatically inject configuration into every downstream function.

    Parameters
    ----------
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
    ValueError
        Raised when config sections are invalid or required targets cannot be
        resolved for the selected environment.

    Notes
    -----
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

    """
    normalized = validate_framework_config(config)
    targets = required_targets or ["Source", "Unified"]
    resolved_paths = {target: get_store(config=normalized, env=env, target=target) for target in targets}

    runtime_meta = _get_fabric_runtime_metadata(notebook_name=notebook_name, local_fallback_name=local_fallback_name)
    resolved_notebook_name = runtime_meta.get("notebook_name")
    user_name = runtime_meta.get("user_name") or runtime_meta.get("user_id") or "unknown"
    run_id = runtime_meta.get("current_run_id") or (
        f"{run_id_prefix}_"
        f"{datetime.fromisoformat(get_current_audit_timestamp(config=normalized)).strftime('%Y%m%dT%H%M%S')}_"
        f"{uuid4().hex[:8]}"
    )

    checks: list[ConfigSmokeCheckResult] = []
    spark_obj = globals().get("spark")
    checks.append(
        ConfigSmokeCheckResult(
            "spark_session",
            "pass" if spark_obj is not None else "warn",
            "Spark session is available." if spark_obj is not None else "Spark session not found; local fallback mode.",
        )
    )
    checks.append(
        ConfigSmokeCheckResult(
            "fabric_runtime_context",
            "pass" if runtime_meta.get("runtime_available") else "skipped",
            "Fabric runtime context is readable."
            if runtime_meta.get("runtime_available")
            else "notebookutils.runtime unavailable outside Fabric runtime.",
        )
    )
    for target, store in resolved_paths.items():
        missing = [attr for attr in ("workspace_id", "item_id", "name", "kind") if not getattr(store, attr, None)]
        if missing:
            checks.append(ConfigSmokeCheckResult(f"path:{target}", "fail", f"Missing required fields: {missing}"))
        elif store.kind == "lakehouse" and str(store.root).startswith("abfss://"):
            checks.append(
                ConfigSmokeCheckResult(
                    f"path:{target}", "pass", "Lakehouse store is populated and ABFSS root is derivable."
                )
            )
        else:
            checks.append(ConfigSmokeCheckResult(f"path:{target}", "pass", "Store is populated."))

    if resolved_notebook_name:
        normalized_name = "_".join(str(resolved_notebook_name).strip().lower().split())
        patterns = [
            r"^00_env_config$",
            r"^01_agreement(?:_[a-z0-9_]+)?$",
            r"^02_pipeline(?:_[a-z0-9_]+)?$",
            r"^03_governance(?:_[a-z0-9_]+)?$",
            r"^99_explore(?:_[a-z0-9_]+)?$",
        ]
        naming_errors = [] if any(re.match(pattern, normalized_name) for pattern in patterns) else [
            "Notebook name does not match accepted FabricOps naming patterns."
        ]
        checks.append(
            ConfigSmokeCheckResult(
                "notebook_naming",
                "pass" if not naming_errors else "fail",
                "; ".join(naming_errors) or "Notebook name is valid.",
            )
        )
    else:
        checks.append(ConfigSmokeCheckResult("notebook_naming", "skipped", "Notebook name check skipped."))

    readiness_status = "ready" if all(r.status in {"pass", "warn", "skipped"} for r in checks) else "not_ready"

    return NotebookSetupContext(
        run_id=str(run_id),
        notebook_name=resolved_notebook_name,
        workspace_name=runtime_meta.get("workspace_name"),
        user_name=str(user_name),
        environment=env,
        paths=resolved_paths,
        validation_results=checks,
        runtime_metadata=runtime_meta,
        readiness_status=readiness_status,
    )


def _get_fabric_runtime_metadata(*, notebook_name: str | None, local_fallback_name: str | None) -> dict[str, Any]:
    """Collect best-effort runtime metadata for setup_notebook."""
    context = None
    try:
        import notebookutils.runtime as nb_runtime  # type: ignore

        context = getattr(nb_runtime, "context", None)
    except Exception:
        context = None

    def ctx(key: str) -> Any:
        if context is None:
            return None
        if isinstance(context, dict):
            return context.get(key)
        get_method = getattr(context, "get", None)
        if callable(get_method):
            try:
                return get_method(key)
            except Exception:
                return None
        return getattr(context, key, None)

    return {
        "notebook_name": notebook_name or ctx("currentNotebookName") or local_fallback_name,
        "workspace_name": ctx("currentWorkspaceName"),
        "workspace_id": ctx("currentWorkspaceId"),
        "user_name": ctx("userName") or ctx("userId") or "unknown",
        "user_id": ctx("userId"),
        "current_run_id": ctx("currentRunId"),
        "is_for_pipeline": ctx("isForPipeline"),
        "is_for_interactive": ctx("isForInteractive"),
        "is_reference_run": ctx("isReferenceRun"),
        "runtime_available": context is not None,
    }


__all__ = ["setup_notebook"]
