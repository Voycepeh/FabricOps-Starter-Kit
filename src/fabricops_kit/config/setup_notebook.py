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
    """Run consolidated FabricOps startup for delivery and optional support notebooks.

    Parameters
    ----------
    config : FrameworkConfig | dict[str, Any]
        Framework configuration object or compatible mapping. The setup flow
        validates required sections and configured Fabric targets before
        running readiness checks.
    env : str, default="Sandbox"
        Environment key used to resolve target paths.
    required_targets : list[str] | None, optional
        Target names that must resolve for ``env``. Defaults to
        ``["Source", "Unified"]``.
    notebook_name : str | None, optional
        Explicit notebook name used for runtime metadata and naming checks.
    run_id_prefix : str, default="run"
        Prefix used when a Fabric runtime run identifier is unavailable.
    local_fallback_name : str | None, optional
        Notebook name used when neither ``notebook_name`` nor Fabric runtime
        context provides one.

    Returns
    -------
    NotebookSetupContext
        Validated runtime context with resolved paths, smoke-check results,
        runtime metadata, and overall readiness status.

    Raises
    ------
    ValueError
        Raised when config sections are invalid or required targets cannot be
        resolved for the selected environment.

    Notes
    -----
    Validation and smoke checks are local to notebook startup. This helper does
    not provision Fabric resources or persist metadata.

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
