"""Configuration bootstrap for FabricOps notebook pipelines.

This module is the workflow entrypoint for establishing the ``00_env_config``
contract, standard environment path definitions, notebook prefix policies,
and smoke-check validation before data movement starts.
Use it early in a Fabric run so downstream IO, quality, lineage, and review
steps execute with explicit, validated runtime context.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


DEFAULT_AUDIT_TIMEZONE = "UTC"


_DEFAULT_CONTEXT_ERROR = "No active Fabric context found. Please run 00_env_config before running this notebook."


def get_default_fabric_context() -> dict[str, Any]:
    """Return the active Fabric context created by ``00_env_config``.

    Returns
    -------
    dict[str, Any]
        Active FabricOps runtime context containing at least ``config`` and
        ``env``.

    Raises
    ------
    RuntimeError
        If ``00_env_config`` has not initialized ``FABRIC_CONTEXT`` in the
        active notebook session.

    Notes
    -----
    The helper first checks the IPython notebook namespace, then ``builtins``.
    When ``00_env_config`` is still constructing the active context, it can
    also assemble the minimal context from ``CONFIG`` and ``ENV`` in the
    notebook namespace. This keeps common notebooks simple while still
    allowing tests and advanced workflows to inject an explicit context.

    """
    context = None
    shell_user_ns = None
    try:
        from IPython import get_ipython  # type: ignore

        shell = get_ipython()
        if shell is not None:
            shell_user_ns = shell.user_ns
            context = shell_user_ns.get("FABRIC_CONTEXT")
    except Exception:
        context = None

    if context is None:
        try:
            import builtins

            context = getattr(builtins, "FABRIC_CONTEXT", None)
        except Exception:
            context = None

    if context is None and shell_user_ns is not None:
        shell_config = shell_user_ns.get("CONFIG")
        shell_env = shell_user_ns.get("ENV")
        if shell_config is not None and shell_env is not None:
            context = {"config": shell_config, "env": shell_env}
            run_context = shell_user_ns.get("RUN_CONTEXT")
            if run_context is not None:
                context["workspace_name"] = getattr(run_context, "workspace_name", None)
                context["runtime_metadata"] = getattr(run_context, "runtime_metadata", None)

    has_environment = isinstance(context, dict) and context.get("env")
    if not isinstance(context, dict) or not context.get("config") or not has_environment:
        raise RuntimeError(_DEFAULT_CONTEXT_ERROR)
    return context


def get_fabric_context(
    *,
    env: str | None = None,
    config: Any = None,
    workspace_id: str | None = None,
    lakehouse_id: str | None = None,
    workspace_name: str | None = None,
    lakehouse_name: str | None = None,
    **values: Any,
) -> dict[str, Any]:
    """Build a Fabric context from explicit values or the active default.

    Parameters
    ----------
    env : str, optional
        Environment key to use. Defaults to the active ``00_env_config`` value.
    config : Any, optional
        FrameworkConfig or compatible config object. Defaults to the active
        ``00_env_config`` value.
    workspace_id : str, optional
        Workspace ID override for advanced cross-workspace usage.
    lakehouse_id : str, optional
        Lakehouse item ID override for advanced usage.
    workspace_name : str, optional
        Workspace name override.
    lakehouse_name : str, optional
        Lakehouse name override.
    **values
        Additional context values to merge into the returned dictionary.

    Returns
    -------
    dict[str, Any]
        Fabric context dictionary suitable for helper ``context=`` overrides.

    """
    base: dict[str, Any] = {} if config is not None and env is not None else dict(get_default_fabric_context())
    if config is not None:
        base["config"] = config
    if env is not None:
        base["env"] = env
    for key, value in {
        "workspace_id": workspace_id,
        "lakehouse_id": lakehouse_id,
        "workspace_name": workspace_name,
        "lakehouse_name": lakehouse_name,
    }.items():
        if value is not None:
            base[key] = value
    base.update(values)
    if not base.get("config") or not base.get("env"):
        raise RuntimeError(_DEFAULT_CONTEXT_ERROR)
    return base


def resolve_fabric_context(
    *,
    config: Any = None,
    env: str | None = None,
    context: dict[str, Any] | None = None,
) -> tuple[Any, str, dict[str, Any]]:
    """Resolve explicit or default FabricOps config and environment values."""
    resolved = dict(context or {})
    if config is None:
        config = resolved.get("config")
    resolved_env = env or resolved.get("env")
    if config is None or resolved_env is None:
        active = get_default_fabric_context()
        if config is None:
            config = active["config"]
        if resolved_env is None:
            resolved_env = active["env"]
        resolved = {**active, **resolved}
    resolved["config"] = config
    resolved["env"] = str(resolved_env)
    return config, str(resolved_env), resolved


def _validate_audit_timezone(timezone_name: str | None) -> str:
    """Return a valid IANA audit timezone name.

    Parameters
    ----------
    timezone_name : str or None
        IANA timezone name to validate. Blank values default to ``"UTC"``.

    Returns
    -------
    str
        Validated timezone name.

    Raises
    ------
    ValueError
        If a non-blank value is not a valid IANA timezone name.

    """
    value = str(timezone_name or DEFAULT_AUDIT_TIMEZONE).strip() or DEFAULT_AUDIT_TIMEZONE
    if value != DEFAULT_AUDIT_TIMEZONE and "/" not in value:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        )
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        ) from exc
    return value


def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
    """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
    if timezone_name is not None:
        return _validate_audit_timezone(timezone_name)
    value = getattr(config, "audit_timezone", None) if config is not None else None
    return _validate_audit_timezone(value)


def _current_audit_timestamp(
    config: Any = None, timezone_name: str | None = None, *, drop_microseconds: bool = True
) -> str:
    """Return the current audit timestamp in the configured audit timezone."""
    tz_name = _get_audit_timezone(config, timezone_name)
    value = datetime.now(ZoneInfo(tz_name))
    if drop_microseconds:
        value = value.replace(microsecond=0)
    return value.isoformat()


def _audit_timestamp_expr(config: Any = None, timezone_name: str | None = None):
    """Return a Spark expression for the current audit timestamp timezone."""
    from pyspark.sql import functions as F

    tz_name = _get_audit_timezone(config, timezone_name)
    return F.current_timestamp() if tz_name == "UTC" else F.from_utc_timestamp(F.current_timestamp(), tz_name)


@dataclass(frozen=True)
class PathConfig:
    """Environment-to-target mapping used for lakehouse/warehouse routing.

    Parameters
    ----------
    paths : dict[str, dict[str, Any]]
        Mapping from environment name (for example ``"dev"``) to one or more
        target names and their configured Housepath-like objects.

    Examples
    --------
    >>> PathConfig(paths={"dev": {"source": object()}}).paths["dev"] is not None
    True

    """

    paths: dict[str, dict[str, Any]]

    def __post_init__(self) -> None:
        """Validate and normalize initialized values."""
        if not isinstance(self.paths, dict) or not self.paths:
            raise ValueError("paths must be a non-empty mapping of environments to targets.")


@dataclass(frozen=True)
class NotebookRuntimeConfig:
    """Runtime options used by notebook-oriented helpers."""

    allowed_notebook_prefixes: tuple[str, ...] = (
        "00_env_config",
        "01_agreement",
        "02_pipeline",
        "03_governance",
        "99_explore",
    )

    def __post_init__(self) -> None:
        """Validate and normalize initialized values."""
        prefixes = tuple(prefix.strip() for prefix in self.allowed_notebook_prefixes if str(prefix).strip())
        if not prefixes:
            raise ValueError("allowed_notebook_prefixes must contain at least one non-empty prefix.")
        object.__setattr__(self, "allowed_notebook_prefixes", prefixes)


@dataclass(frozen=True)
class QualityConfig:
    """Default quality-policy options for FabricOps validation stages.

    Parameters
    ----------
    default_severity : str, default="warning"
        Baseline severity label applied when rule-level severity is not set.
    fail_on_critical : bool, default=True
        Whether critical findings should mark the run as failed in downstream
        orchestration decisions.
    quarantine_on_failure : bool, default=False
        Whether failed records should be routed to a quarantine path when that
        workflow is enabled by runtime helpers.

    """

    default_severity: str = "warning"
    fail_on_critical: bool = True
    quarantine_on_failure: bool = False

    def __post_init__(self) -> None:
        """Validate and normalize initialized values."""
        severity = str(self.default_severity).strip().lower()
        if severity not in {"info", "warning", "critical"}:
            raise ValueError("default_severity must be one of: info, warning, critical.")
        object.__setattr__(self, "default_severity", severity)
        object.__setattr__(self, "fail_on_critical", bool(self.fail_on_critical))
        object.__setattr__(self, "quarantine_on_failure", bool(self.quarantine_on_failure))


def _normalize_widget_config(widget: dict[str, Any] | None) -> dict[str, Any]:
    """Return a widget config with validated custom-field dictionaries."""
    normalized = deepcopy(dict(widget or {}))
    custom_fields = []
    for field_definition in normalized.get("custom_fields", []) or []:
        field_config = deepcopy(dict(field_definition))
        key = str(field_config.get("key") or "").strip()
        if not key:
            raise ValueError("Governance custom fields require a key.")
        field_config["key"] = key
        custom_fields.append(field_config)
    normalized["custom_fields"] = custom_fields
    return normalized


@dataclass(frozen=True)
class GovernanceConfig:
    """Default governance-policy options for metadata/classification checks.

    Parameters
    ----------
    required_classification : bool, default=True
        Whether governed datasets are expected to carry classification metadata.
    sensitivity_rules : dict[str, str]
        Mapping of rule keys to expected sensitivity labels used by governance
        notebook checks and reporting summaries.
    sensitivity_labels : list[str]
        Controlled labels rendered by column metadata enrichment widgets.
    pii_classifications : list[str]
        Controlled PII classifications rendered by column metadata enrichment widgets.
    enrichment_context_widget, enrichment_classification_widget : dict[str, Any]
        Widget definitions for organization-specific enrichment fields. Each
        widget uses ``custom_fields`` entries keyed by ``key``.

    """

    required_classification: bool = True
    sensitivity_rules: dict[str, str] = field(default_factory=dict)
    sensitivity_labels: list[str] = field(default_factory=lambda: ["classified", "restricted", "public"])
    pii_classifications: list[str] = field(default_factory=lambda: ["direct PII", "indirect PII", "none"])
    enrichment_context_widget: dict[str, Any] = field(default_factory=lambda: {"custom_fields": []})
    enrichment_classification_widget: dict[str, Any] = field(default_factory=lambda: {"custom_fields": []})

    def __post_init__(self) -> None:
        """Validate and normalize initialized values."""
        object.__setattr__(self, "required_classification", bool(self.required_classification))
        object.__setattr__(self, "sensitivity_rules", dict(self.sensitivity_rules or {}))
        labels = [str(option).strip() for option in (self.sensitivity_labels or []) if str(option).strip()]
        pii = [str(option).strip() for option in (self.pii_classifications or []) if str(option).strip()]
        object.__setattr__(self, "sensitivity_labels", labels or ["classified", "restricted", "public"])
        object.__setattr__(self, "pii_classifications", pii or ["direct PII", "indirect PII", "none"])
        object.__setattr__(
            self,
            "enrichment_context_widget",
            _normalize_widget_config(self.enrichment_context_widget),
        )
        object.__setattr__(
            self,
            "enrichment_classification_widget",
            _normalize_widget_config(self.enrichment_classification_widget),
        )


DEFAULT_STEWARD_ROLE_OPTIONS = [
    "Data Owner",
    "Data Steward",
    "Data Custodian",
    "Governance Reviewer",
    "Business Approver",
]


@dataclass(frozen=True)
class DataAgreementConfig:
    """Editable ``01_agreement`` table names and widget definitions.

    Parameters
    ----------
    metadata_tables : dict[str, str]
        Lightweight metadata table names prepared by ``00_env_config``.
    data_steward_widget, data_agreement_widget : dict[str, Any]
        Visible standard columns and organization-specific ``custom_fields``.
        Custom fields are rendered dynamically and persisted in
        ``custom_fields_json`` instead of becoming physical table columns.
    steward_role_options : list[str]
        Controlled Data Steward role labels rendered by ``01_agreement`` as the
        ``steward_role`` dropdown.

    """

    metadata_tables: dict[str, str] = field(
        default_factory=lambda: {
            "data_steward": "METADATA_DATA_STEWARD",
            "data_agreement": "METADATA_DATA_AGREEMENT",
            "data_agreement_evidence": "METADATA_DATA_AGREEMENT_EVIDENCE",
        }
    )
    data_steward_widget: dict[str, Any] = field(
        default_factory=lambda: {
            "visible_columns": [
                "steward_name",
                "steward_role",
                "contact",
                "effective_from",
                "effective_to",
            ],
            "custom_fields": [],
        }
    )
    data_agreement_widget: dict[str, Any] = field(
        default_factory=lambda: {
            "visible_columns": [
                "agreement_name",
                "domain",
                "steward_id",
                "recipient",
                "start_date",
                "expiry_date",
                "business_purpose",
                "approved_usage_internal",
                "approved_usage_external",
                "approved_usage_research",
            ],
            "custom_fields": [],
        }
    )
    steward_role_options: list[str] = field(default_factory=lambda: list(DEFAULT_STEWARD_ROLE_OPTIONS))

    def __post_init__(self) -> None:
        """Validate and normalize initialized values."""
        object.__setattr__(self, "metadata_tables", deepcopy(dict(self.metadata_tables or {})))
        object.__setattr__(self, "data_steward_widget", _normalize_widget_config(self.data_steward_widget))
        object.__setattr__(self, "data_agreement_widget", _normalize_widget_config(self.data_agreement_widget))
        options = [str(option).strip() for option in (self.steward_role_options or []) if str(option).strip()]
        object.__setattr__(self, "steward_role_options", options or list(DEFAULT_STEWARD_ROLE_OPTIONS))


@dataclass(frozen=True)
class ReviewWorkflowConfig:
    """Notebook-local review settings for suggestion staging and approval."""

    business_context: str = ""
    approved_usage: str = ""
    profile_table: str = "metadata.profile_rows"
    business_context_review_table: str = "metadata.business_context_review"
    business_context_approved_table: str = "metadata.business_context_approved"
    dq_review_table: str = "metadata.dq_review"
    dq_approved_table: str = "metadata.dq_approved"
    default_approval_status: str = "pending"


@dataclass(frozen=True)
class LineageConfig:
    """Default lineage-capture behavior for pipeline traceability.

    Parameters
    ----------
    capture_transformation_steps : bool, default=True
        Whether transformation-level steps should be included in lineage
        capture payloads.

    """

    capture_transformation_steps: bool = True

    def __post_init__(self) -> None:
        """Validate and normalize initialized values."""
        object.__setattr__(self, "capture_transformation_steps", bool(self.capture_transformation_steps))


@dataclass(frozen=True)
class FrameworkConfig:
    """Top-level framework configuration object.

    Parameters
    ----------
    path_config : PathConfig
        Environment and target routing definitions.
    notebook_runtime_config : NotebookRuntimeConfig
        Notebook naming policy and runtime validation options.
    quality_config : QualityConfig, optional
        Default quality-policy settings. Uses package defaults when omitted.
    governance_config : GovernanceConfig, optional
        Default governance-policy settings. Uses package defaults when omitted.
    review_workflow_config : ReviewWorkflowConfig, optional
        Notebook-native review, approval, and metadata destination settings. Uses package defaults when omitted.
    lineage_config : LineageConfig, optional
        Default lineage capture behavior. Uses package defaults when omitted.
    audit_timezone : str, default="UTC"
        IANA timezone used for FabricOps-generated audit and technical timestamps.

    Examples
    --------
    >>> cfg = FrameworkConfig(
    ...     path_config=PathConfig(paths={"dev": {"source": object()}}),
    ...     notebook_runtime_config=NotebookRuntimeConfig(("00_",)),
    ... )
    >>> isinstance(cfg, FrameworkConfig)
    True

    """

    path_config: PathConfig
    notebook_runtime_config: NotebookRuntimeConfig
    quality_config: QualityConfig = field(default_factory=QualityConfig)
    governance_config: GovernanceConfig = field(default_factory=GovernanceConfig)
    review_workflow_config: ReviewWorkflowConfig = field(default_factory=ReviewWorkflowConfig)
    lineage_config: LineageConfig = field(default_factory=LineageConfig)
    data_agreement_config: DataAgreementConfig = field(default_factory=DataAgreementConfig)
    audit_timezone: str = DEFAULT_AUDIT_TIMEZONE

    def __post_init__(self) -> None:
        """Validate and normalize initialized values."""
        object.__setattr__(self, "audit_timezone", _validate_audit_timezone(self.audit_timezone))


@dataclass(frozen=True)
class ConfigSmokeCheckResult:
    """Represent one readiness or smoke-test check."""

    name: str
    status: str
    message: str


@dataclass(frozen=True)
class NotebookSetupContext:
    """Consolidated startup context returned by :func:`setup_notebook`.

    Parameters
    ----------
    run_id : str
        Unique run identifier generated for this notebook startup.
    notebook_name : str | None
        Notebook name resolved from runtime context or caller input.
    workspace_name : str | None
        Fabric workspace name when runtime context is available.
    user_name : str | None
        Active Fabric user name when runtime context is available.
    environment : str
        Selected environment key used for path resolution.
    paths : dict[str, Any]
        Resolved environment target mappings keyed by target name.
    validation_results : list[ConfigSmokeCheckResult]
        Startup validation checks executed during setup.
    runtime_metadata : dict[str, Any]
        Raw runtime metadata for troubleshooting and logging.
    readiness_status : str
        Overall readiness status derived from validation checks.

    """

    run_id: str
    notebook_name: str | None
    workspace_name: str | None
    user_name: str | None
    environment: str
    paths: dict[str, Any]
    validation_results: list[ConfigSmokeCheckResult]
    runtime_metadata: dict[str, Any]
    readiness_status: str


def _validate_framework_config(config: FrameworkConfig | dict[str, Any]) -> FrameworkConfig:
    """Validate and normalize framework configuration input.

    Parameters
    ----------
    config : FrameworkConfig | dict[str, Any]
        Existing framework config object or compatible mapping containing the
        required user-facing component configs. Framework-only sections may be
        omitted and will use package defaults.

    Returns
    -------
    FrameworkConfig
        Normalized, validated framework config object.

    Raises
    ------
    ValueError
        Raised when required sections are missing, component types are invalid,
        or configured path targets are incomplete.

    Notes
    -----
    Validation checks configuration shape and required FabricStore fields.
    It does not perform external IO or provision Fabric resources.

    Examples
    --------
    >>> normalized = _validate_framework_config(framework_config)
    >>> isinstance(normalized, FrameworkConfig)
    True

    """
    if isinstance(config, FrameworkConfig):
        normalized = config
    elif isinstance(config, dict):
        required_keys = {
            "path_config",
            "notebook_runtime_config",
        }
        missing_keys = sorted(required_keys.difference(config.keys()))
        if missing_keys:
            raise ValueError(f"Framework config is missing required keys: {', '.join(missing_keys)}.")
        normalized = FrameworkConfig(**config)
    else:
        raise ValueError("config must be a FrameworkConfig object or compatible mapping.")

    if not isinstance(normalized.path_config, PathConfig):
        raise ValueError("path_config must be a PathConfig object.")
    if not isinstance(normalized.notebook_runtime_config, NotebookRuntimeConfig):
        raise ValueError("notebook_runtime_config must be a NotebookRuntimeConfig object.")
    if not isinstance(normalized.quality_config, QualityConfig):
        raise ValueError("quality_config must be a QualityConfig object.")
    if not isinstance(normalized.governance_config, GovernanceConfig):
        raise ValueError("governance_config must be a GovernanceConfig object.")
    if not isinstance(normalized.review_workflow_config, ReviewWorkflowConfig):
        raise ValueError("review_workflow_config must be a ReviewWorkflowConfig object.")
    if not isinstance(normalized.lineage_config, LineageConfig):
        raise ValueError("lineage_config must be a LineageConfig object.")
    if not isinstance(normalized.data_agreement_config, DataAgreementConfig):
        raise ValueError("data_agreement_config must be a DataAgreementConfig object.")
    _validate_audit_timezone(normalized.audit_timezone)

    for env, targets in normalized.path_config.paths.items():
        if not isinstance(targets, dict) or not targets:
            raise ValueError(f"Environment '{env}' must contain at least one target.")
        for target_name, housepath in targets.items():
            required = ("workspace_id", "item_id", "name", "kind")
            if not all(hasattr(housepath, attr) for attr in required):
                raise ValueError(f"Target '{env}/{target_name}' must provide FabricStore fields: {required}.")

    return normalized


def _normalize_path_config(config: Any | None, *, require_paths: bool = True) -> PathConfig:
    """Return the shared runtime path configuration for accepted config shapes."""
    if config is None:
        if require_paths:
            raise ValueError("No Fabric config was provided. Pass a FrameworkConfig, PathConfig, or compatible object.")
        return PathConfig(paths={"__missing__": {}})

    candidate = config
    if isinstance(candidate, FrameworkConfig):
        return candidate.path_config
    if isinstance(candidate, PathConfig):
        return candidate
    if isinstance(candidate, dict):
        if "path_config" in candidate:
            candidate = candidate.get("path_config")
        elif "paths" in candidate:
            candidate = candidate.get("paths")
        else:
            if require_paths:
                raise ValueError("config mapping must contain 'path_config' or 'paths'.")
            return PathConfig(paths={"__missing__": {}})
    elif hasattr(candidate, "path_config"):
        candidate = getattr(candidate, "path_config")
    elif not hasattr(candidate, "paths"):
        if require_paths:
            raise ValueError("config must provide path_config or paths for Fabric target routing.")
        return PathConfig(paths={"__missing__": {}})

    if isinstance(candidate, PathConfig):
        return candidate
    if isinstance(candidate, dict):
        if "paths" in candidate and isinstance(candidate.get("paths"), dict):
            return PathConfig(paths=candidate["paths"])
        return PathConfig(paths=candidate)
    if hasattr(candidate, "paths"):
        paths = getattr(candidate, "paths")
        if isinstance(paths, dict):
            return PathConfig(paths=paths)
    if require_paths:
        raise ValueError("path_config must provide a non-empty paths mapping.")
    return PathConfig(paths={"__missing__": {}})


def _get_store(config: FrameworkConfig | PathConfig | dict[str, Any] | Any | None, env: str, target: str) -> Any:
    """Resolve a configured Fabric path for an environment and target.

    Parameters
    ----------
    env : str
        Environment key such as ``Sandbox``, ``DE``, or ``Prod``.
    target : str
        Target key such as ``Source``, ``Unified``, ``Product``, or ``Warehouse``.
    config : FrameworkConfig | PathConfig | None
        Configuration that contains environment-to-target path mappings.

    Returns
    -------
    Any
        FabricStore object with ``workspace_id``, ``house_id``, ``house_name``, and ``root``.

    Raises
    ------
    ValueError
        If config is missing, or if the environment/target mapping does not exist.

    Examples
    --------
    >>> get_path("Sandbox", "Source", config=CONFIG)
    Housepath(...)

    """
    paths = _normalize_path_config(config).paths
    if env not in paths:
        available_envs = ", ".join(sorted(paths.keys())) or "<none>"
        raise ValueError(
            f"Environment '{env}' was not found in Fabric config. Available environments: {available_envs}."
        )
    if target not in paths[env]:
        available_targets = ", ".join(sorted(paths[env].keys())) or "<none>"
        raise ValueError(
            f"Target '{target}' was not found under environment '{env}'. Available targets: {available_targets}."
        )
    return paths[env][target]


def _validate_notebook_name(notebook_name: str, config: FrameworkConfig | None = None) -> list[str]:
    name = "_".join(str(notebook_name or "").strip().lower().split())
    patterns = [
        r"^00_env_config$",
        r"^01_agreement(?:_[a-z0-9_]+)?$",
        r"^02_pipeline(?:_[a-z0-9_]+)?$",
        r"^03_governance(?:_[a-z0-9_]+)?$",
        r"^99_explore(?:_[a-z0-9_]+)?$",
    ]
    if any(__import__("re").match(p, name) for p in patterns):
        return []
    return ["Notebook name does not match accepted FabricOps naming patterns."]


def _run_config_smoke_tests(
    config: FrameworkConfig,
    env: str = "Sandbox",
    required_targets: list[str] | None = None,
    check_io_import: bool = False,
    notebook_name: str | None = None,
) -> list[ConfigSmokeCheckResult]:
    """Run 00_env_config readiness smoke checks for configuration bootstrap.

    Use this during environment bootstrap to verify Spark availability, Fabric
    runtime context access, required path mappings, notebook naming policy, and
    optional IO import readiness before executing downstream notebook steps.

    Parameters
    ----------
    config : FrameworkConfig
        Validated framework configuration to evaluate.
    env : str, default="Sandbox"
        Environment key used when resolving required target paths.
    required_targets : list[str] | None, optional
        Required targets expected in ``config.path_config``. Defaults to
        ``["Source", "Unified"]`` when not provided.
    check_io_import : bool, default=False
        Whether to test importability of ``fabric_input_output`` helpers.
    notebook_name : str | None, optional
        Notebook name to validate against configured naming prefixes.

    Returns
    -------
    list[ConfigSmokeCheckResult]
        Ordered check results with ``pass``, ``warn``, ``fail``, or ``skipped``
        statuses for each readiness dimension.

    Raises
    ------
    ValueError
        Propagated from config/path validation helpers when required targets or
        configured environments are invalid.

    Notes
    -----
    This helper performs validation and lightweight import/runtime checks only.
    It does not create or mutate Fabric resources.

    Examples
    --------
    >>> checks = _run_config_smoke_tests(config=my_config, env="Sandbox", notebook_name="00_env_config")
    >>> any(c.status == "fail" for c in checks)
    False

    """
    results: list[ConfigSmokeCheckResult] = []
    required_targets = required_targets or ["Source", "Unified"]
    spark_ready, spark_message = _check_spark_session()
    results.append(ConfigSmokeCheckResult("spark_session", "pass" if spark_ready else "warn", spark_message))

    runtime_meta = _get_fabric_runtime_metadata(notebook_name=notebook_name)
    runtime_status = "pass" if runtime_meta.get("runtime_available") else "skipped"
    runtime_message = (
        "Fabric runtime context is readable."
        if runtime_meta.get("runtime_available")
        else "notebookutils.runtime unavailable outside Fabric runtime."
    )
    results.append(ConfigSmokeCheckResult("fabric_runtime_context", runtime_status, runtime_message))
    try:
        for target in required_targets:
            p = _get_store(config=config, env=env, target=target)
            missing = [attr for attr in ("workspace_id", "item_id", "name", "kind") if not getattr(p, attr, None)]
            if missing:
                results.append(ConfigSmokeCheckResult(f"path:{target}", "fail", f"Missing required fields: {missing}"))
            elif p.kind == "lakehouse" and str(p.root).startswith("abfss://"):
                results.append(
                    ConfigSmokeCheckResult(
                        f"path:{target}", "pass", "Lakehouse store is populated and ABFSS root is derivable."
                    )
                )
            else:
                results.append(ConfigSmokeCheckResult(f"path:{target}", "pass", "Store is populated."))
    except Exception as exc:
        results.append(ConfigSmokeCheckResult("path_resolution", "fail", str(exc)))

    if notebook_name:
        errors = _validate_notebook_name(notebook_name, config=config)
        results.append(
            ConfigSmokeCheckResult(
                "notebook_naming", "pass" if not errors else "fail", "; ".join(errors) or "Notebook name is valid."
            )
        )
    else:
        results.append(ConfigSmokeCheckResult("notebook_naming", "skipped", "Notebook name check skipped."))

    if check_io_import:
        try:
            from .fabric_input_output import read_lakehouse_table  # noqa: F401

            results.append(ConfigSmokeCheckResult("fabric_io_import", "pass", "fabric_io helpers are importable."))
        except Exception as exc:
            results.append(ConfigSmokeCheckResult("fabric_io_import", "fail", str(exc)))
    else:
        results.append(ConfigSmokeCheckResult("fabric_io_import", "skipped", "IO import check disabled."))
    return results


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
    from uuid import uuid4
    from datetime import datetime, timezone

    normalized = _validate_framework_config(config)
    required_targets = required_targets or ["Source", "Unified"]
    resolved_paths = {target: _get_store(config=normalized, env=env, target=target) for target in required_targets}

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

    resolved_notebook_name = notebook_name or ctx("currentNotebookName") or local_fallback_name
    user_name = ctx("userName") or ctx("userId") or "unknown"
    run_id = (
        ctx("currentRunId")
        or f"{run_id_prefix}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}_{uuid4().hex[:8]}"
    )

    runtime_meta = {
        "notebook_name": resolved_notebook_name,
        "workspace_name": ctx("currentWorkspaceName"),
        "workspace_id": ctx("currentWorkspaceId"),
        "user_name": user_name,
        "user_id": ctx("userId"),
        "current_run_id": ctx("currentRunId"),
        "is_for_pipeline": ctx("isForPipeline"),
        "is_for_interactive": ctx("isForInteractive"),
        "is_reference_run": ctx("isReferenceRun"),
        "runtime_available": context is not None,
    }

    checks = _run_config_smoke_tests(
        config=normalized, env=env, required_targets=required_targets, notebook_name=resolved_notebook_name
    )
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


def _get_active_metadata_tables(config: FrameworkConfig | dict[str, Any]) -> list[str]:
    """Return the canonical active metadata tables prepared by ``00_env_config``.

    The active registry is intentionally source-driven: agreement tables come
    from ``DataAgreementConfig``, notebook registry from ``metadata.py``, and
    governance/pipeline tables from the governance schema registry.
    ``METADATA_DATA_ACCESS`` is part of the active setup registry for public-safe access context. Governance review history is derived from append-only enrichment and guardrail rule rows, not a separate review table.
    """
    normalized = _validate_framework_config(config)
    from fabricops_kit.data_agreement import DATA_AGREEMENT_EVIDENCE_TABLE, DATA_AGREEMENT_TABLE, DATA_STEWARD_TABLE
    from fabricops_kit.governance_review import _get_governance_metadata_schemas
    from fabricops_kit.metadata import NOTEBOOK_REGISTRY_TABLE

    metadata_tables = normalized.data_agreement_config.metadata_tables or {}
    tables = [
        str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)),
        str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)),
        str(metadata_tables.get("data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE)),
        NOTEBOOK_REGISTRY_TABLE,
        *_get_governance_metadata_schemas().keys(),
    ]
    out: list[str] = []
    for table in tables:
        table_name = str(table or "").strip()
        if table_name and table_name not in out:
            out.append(table_name)
    return out


def _detect_nested_metadata_delta_folders(
    *, config: FrameworkConfig | dict[str, Any], env: str, expected_tables: list[str]
) -> list[str]:
    """Best-effort warning detector for legacy nested metadata Delta folders."""
    try:
        import notebookutils  # type: ignore
    except Exception:
        return []

    fs = getattr(notebookutils, "fs", None)
    exists = getattr(fs, "exists", None)
    if not callable(exists):
        return []
    metadata_store = _get_store(config=config, env=env, target="metadata")
    nested: list[str] = []
    schema = getattr(metadata_store, "schema", None) if getattr(metadata_store, "schema_enabled", False) else None
    for table in expected_tables:
        candidate_paths = [f"{metadata_store.root.rstrip('/')}/Tables/{table}/Unidentified/_delta_log"]
        if schema:
            candidate_paths.append(f"{metadata_store.root.rstrip('/')}/Tables/{schema}/{table}/Unidentified/_delta_log")
        for path in candidate_paths:
            try:
                if exists(path):
                    nested.append(path)
            except Exception:
                continue
    return nested


def _metadata_schema_field_names(schema: Any) -> list[str]:
    """Return field names from a Spark StructType-like schema."""
    if hasattr(schema, "fieldNames"):
        return list(schema.fieldNames())
    return [field.name for field in getattr(schema, "fields", [])]


def _string_metadata_schema(table_name: str, fields: list[str]):
    """Build an explicit all-string Spark schema for lightweight metadata tables."""
    try:
        from pyspark.sql.types import StringType, StructField, StructType
    except Exception as exc:  # pragma: no cover - Fabric/runtime dependency guard
        raise RuntimeError("metadata table setup requires pyspark.sql.types in the active runtime.") from exc

    logical_names: dict[str, list[str]] = {}
    for column_name in fields:
        logical_names.setdefault(str(column_name).lower(), []).append(str(column_name))
    duplicates = {logical: names for logical, names in logical_names.items() if len(names) > 1}
    if duplicates:
        details = "; ".join(f"{logical}: {', '.join(names)}" for logical, names in sorted(duplicates.items()))
        raise ValueError(f"{table_name} schema contains case-insensitive duplicate column names: {details}.")
    string = StringType()
    return StructType([StructField(str(column_name), string, True) for column_name in fields])


def _get_metadata_table_schema_registry(config: FrameworkConfig | dict[str, Any]) -> dict[str, Any]:
    """Return the canonical metadata setup registry as table names mapped to schemas."""
    normalized = _validate_framework_config(config)
    from fabricops_kit.data_agreement import (
        DATA_AGREEMENT_EVIDENCE_FIELDS,
        DATA_AGREEMENT_EVIDENCE_TABLE,
        DATA_AGREEMENT_FIELDS,
        DATA_AGREEMENT_TABLE,
        DATA_STEWARD_FIELDS,
        DATA_STEWARD_TABLE,
    )
    from fabricops_kit.governance_review import _get_governance_metadata_schemas
    from fabricops_kit.metadata import NOTEBOOK_REGISTRY_FIELDS, NOTEBOOK_REGISTRY_TABLE

    metadata_tables = normalized.data_agreement_config.metadata_tables or {}
    registry: dict[str, Any] = {
        str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)): _string_metadata_schema(
            str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), DATA_STEWARD_FIELDS
        ),
        str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)): _string_metadata_schema(
            str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), DATA_AGREEMENT_FIELDS
        ),
        str(metadata_tables.get("data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE)): _string_metadata_schema(
            str(metadata_tables.get("data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE)),
            DATA_AGREEMENT_EVIDENCE_FIELDS,
        ),
        NOTEBOOK_REGISTRY_TABLE: _string_metadata_schema(NOTEBOOK_REGISTRY_TABLE, NOTEBOOK_REGISTRY_FIELDS),
    }
    registry.update(_get_governance_metadata_schemas())
    return registry


def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
    """Return row dictionaries from Spark-like row collections."""
    if rows is None:
        return []
    if hasattr(rows, "collect"):
        rows = rows.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]


def _resolve_metadata_schema(
    config: FrameworkConfig | dict[str, Any], env: str, metadata_schema: str | None = None
) -> str | None:
    """Return explicit metadata schema or configured metadata target schema."""
    if metadata_schema is not None:
        return str(metadata_schema).strip() or None
    store = _get_store(config=config, env=env, target="metadata")
    if getattr(store, "schema_enabled", False):
        return str(getattr(store, "schema", "") or "").strip() or None
    return None


def _setup_metadata_table_registry(
    *,
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    registry: dict[str, Any],
    metadata_schema: str | None = None,
) -> dict[str, Any]:
    """Create missing metadata tables through configured lakehouse IO helpers."""
    from fabricops_kit.fabric_input_output import read_lakehouse_table, write_lakehouse_table
    from fabricops_kit.governance_review import _is_table_not_found_error

    created: list[str] = []
    for table_name, schema in registry.items():
        try:
            read_kwargs = {"spark_session": spark}
            if metadata_schema is not None:
                read_kwargs["schema"] = metadata_schema
            table = read_lakehouse_table(
                table_name, target="metadata", context={"config": config, "env": env}, **read_kwargs
            )
        except Exception as exc:
            if not _is_table_not_found_error(exc):
                raise RuntimeError(
                    f"Unable to read metadata table {table_name!r}; not attempting creation because the error was not a confirmed table-not-found condition."
                ) from exc
            empty_df = spark.createDataFrame([], schema=schema)
            write_lakehouse_table(
                empty_df,
                table_name,
                target="metadata",
                schema=metadata_schema,
                context={"config": config, "env": env},
                mode="overwrite",
                options={"overwriteSchema": "true"},
            )
            read_kwargs = {"spark_session": spark}
            if metadata_schema is not None:
                read_kwargs["schema"] = metadata_schema
            table = read_lakehouse_table(
                table_name, target="metadata", context={"config": config, "env": env}, **read_kwargs
            )
            created.append(table_name)

        table_columns = list(getattr(table, "columns", []) or [])
        if not table_columns:
            rows = _coerce_row_dicts(table)
            table_columns = list(rows[0]) if rows else []
        missing = [field for field in _metadata_schema_field_names(schema) if field not in table_columns]
        if missing:
            raise ValueError(
                f"{table_name} is missing required column(s): {', '.join(missing)}. Recreate or manually migrate the table before running metadata setup."
            )
    return {"status": "ready", "tables": list(registry), "created_tables": created}


def _validate_metadata_table_registration(
    *,
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    expected_tables: list[str] | None = None,
    metadata_schema: str | None = None,
) -> dict[str, Any]:
    """Validate active metadata tables through configured metadata target reads."""
    from fabricops_kit.fabric_input_output import read_lakehouse_table

    normalized = _validate_framework_config(config)
    expected = list(expected_tables or _get_active_metadata_tables(normalized))
    resolved_metadata_schema = _resolve_metadata_schema(normalized, env, metadata_schema)
    missing: list[str] = []
    warnings: list[str] = []
    for table in expected:
        try:
            read_kwargs = {"spark_session": spark}
            if resolved_metadata_schema is not None:
                read_kwargs["schema"] = resolved_metadata_schema
            read_lakehouse_table(table, target="metadata", context={"config": config, "env": env}, **read_kwargs)
        except Exception:
            missing.append(table)
    nested_paths = _detect_nested_metadata_delta_folders(config=normalized, env=env, expected_tables=expected)
    if missing:
        warnings.append("Expected metadata tables could not be read from the configured metadata target.")
    if nested_paths:
        warnings.append(
            "Detected legacy nested metadata Delta folders under Tables/<metadata_table>/Unidentified/_delta_log. "
            "FabricOps will not delete or migrate user data automatically; review and migrate those folders manually if needed. "
            + (
                "When metadata schema routing is configured, new metadata setup uses schema-aware Lakehouse paths. "
                if resolved_metadata_schema
                else "New metadata setup writes directly to configured ABFSS Lakehouse table paths."
            )
        )
    return {
        "status": "ready" if not missing else "not_ready",
        "database": _get_store(config=normalized, env=env, target="metadata").name,
        "expected_tables": expected,
        "expected_table_count": len(expected),
        "registered_tables": [table for table in expected if table not in missing],
        "missing_tables": missing,
        "nested_metadata_delta_paths": nested_paths,
        "warnings": warnings,
        "metadata_schema": resolved_metadata_schema,
        "fully_qualified_tables": [
            f"{resolved_metadata_schema}.{table}" if resolved_metadata_schema else table for table in expected
        ],
        "show_tables_statement": None,
        "optional_documented_tables": [],
    }


def setup_metadata_tables(
    *,
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    metadata_schema: str | None = None,
    require_active_steward: bool = False,
) -> dict[str, Any]:
    """Prepare all FabricOps metadata tables for the configured environment.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used by the table setup helpers.
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration containing the metadata target.
    env : str
        Environment key to prepare.
    metadata_schema : str or None, default=None
        Optional schema name for schema-enabled Fabric Lakehouses. Keep
        ``None`` for classic Lakehouses that store metadata tables under
        ``Tables/<table_name>``. Use a simple schema such as ``"METADATA"``
        to create and validate registered tables such as
        ``METADATA.METADATA_DATA_AGREEMENT``.
    require_active_steward : bool, default=False
        Forwarded to the agreement metadata setup to optionally require an
        active steward before returning success.

    Returns
    -------
    dict[str, Any]
        Combined setup summary keyed by ``data_agreement``,
        ``notebook_registry``, and ``governance``. The payload also includes
        ``metadata_schema`` and ``fully_qualified_tables`` for schema-enabled
        Lakehouse visibility.

    Notes
    -----
    This is the v1 notebook setup action for metadata provisioning. It keeps
    ``00_env_config`` simple while delegating to internal helpers that route all
    metadata reads and writes through the configured metadata target. With
    ``metadata_schema=None``, setup preserves classic path-based Lakehouse
    behavior under ``Tables/<table_name>``. With ``metadata_schema`` set, setup
    uses schema-aware Lakehouse paths such as ``Tables/<schema>/<table>`` and
    does not bake the schema into configured metadata table names. FabricOps may warn about
    legacy nested or unidentified Delta folders, but it does not delete or
    migrate user data automatically.

    """
    from fabricops_kit.data_agreement import (
        DATA_AGREEMENT_EVIDENCE_TABLE,
        DATA_AGREEMENT_TABLE,
        DATA_STEWARD_TABLE,
        _list_data_stewards,
    )
    from fabricops_kit.governance_review import _get_governance_metadata_schemas
    from fabricops_kit.metadata import NOTEBOOK_REGISTRY_TABLE

    normalized = _validate_framework_config(config)
    registry = _get_metadata_table_schema_registry(normalized)
    resolved_metadata_schema = _resolve_metadata_schema(normalized, env, metadata_schema)
    setup_registry = _setup_metadata_table_registry(
        spark=spark, config=normalized, env=env, registry=registry, metadata_schema=resolved_metadata_schema
    )
    expected_tables = list(registry)
    fully_qualified_tables = [
        f"{resolved_metadata_schema}.{table}" if resolved_metadata_schema else table for table in expected_tables
    ]
    created_tables = list(setup_registry["created_tables"])

    metadata_tables = normalized.data_agreement_config.metadata_tables or {}
    data_agreement_tables = [
        str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)),
        str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)),
        str(metadata_tables.get("data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE)),
    ]
    active_stewards = _list_data_stewards(
        normalized,
        env,
        spark_session=spark,
        active_only=True,
        missing_ok=True,
        metadata_schema=resolved_metadata_schema,
    )
    data_agreement = {
        "status": "ready" if active_stewards else "not_ready",
        "tables": data_agreement_tables,
        "created_tables": [table for table in data_agreement_tables if table in created_tables],
        "active_steward_count": len(active_stewards),
        "message": (
            f"{data_agreement_tables[0]} contains active steward rows. 01_agreement can render both intake widgets."
            if active_stewards
            else f"{data_agreement_tables[0]} has no active steward rows yet. Use the 01_agreement Data Steward widget to create one before saving an agreement."
        ),
    }
    if require_active_steward and not active_stewards:
        raise ValueError(data_agreement["message"])

    governance_tables = list(_get_governance_metadata_schemas())
    notebook_schema = registry.get(NOTEBOOK_REGISTRY_TABLE)
    notebook_registry = {
        "status": "ready",
        "table": NOTEBOOK_REGISTRY_TABLE,
        "schema": _metadata_schema_field_names(notebook_schema) if notebook_schema is not None else [],
        "created": NOTEBOOK_REGISTRY_TABLE in created_tables,
        "created_tables": [NOTEBOOK_REGISTRY_TABLE] if NOTEBOOK_REGISTRY_TABLE in created_tables else [],
    }
    governance = {
        "status": "ready",
        "tables": governance_tables,
        "created_tables": [table for table in governance_tables if table in created_tables],
    }
    created_or_checked: list[str] = []
    for summary in (data_agreement, notebook_registry, governance):
        for key in ("tables", "table"):
            value = summary.get(key) if isinstance(summary, dict) else None
            values = value if isinstance(value, list) else [value] if value else []
            for table in values:
                table_name = str(table or "").strip()
                if table_name and table_name not in created_or_checked:
                    created_or_checked.append(table_name)
    registration_validation = _validate_metadata_table_registration(
        spark=spark,
        config=config,
        env=env,
        expected_tables=expected_tables,
        metadata_schema=resolved_metadata_schema,
    )
    setup_statuses = [notebook_registry.get("status"), governance.get("status")]
    if require_active_steward:
        setup_statuses.append(data_agreement.get("status"))
    registration_status = registration_validation.get("status")
    return {
        "status": "ready"
        if all(status == "ready" for status in setup_statuses) and registration_status in {"ready", "skipped"}
        else "not_ready",
        "data_agreement": data_agreement,
        "notebook_registry": notebook_registry,
        "governance": governance,
        "tables": expected_tables,
        "metadata_schema": resolved_metadata_schema,
        "fully_qualified_tables": fully_qualified_tables,
        "created_tables": created_tables,
        "warnings": registration_validation.get("warnings", []),
        "active_metadata_tables": expected_tables,
        "active_metadata_table_count": len(expected_tables),
        "created_or_checked_tables": created_or_checked,
        "registration_validation": registration_validation,
    }


def _check_spark_session() -> tuple[bool, str]:
    """Check whether a Spark session is available."""
    spark_obj = globals().get("spark")
    if spark_obj is not None:
        return True, "Spark session is available."
    return False, "Spark session not found; local fallback mode."


def _get_fabric_runtime_metadata(notebook_name: str | None = None) -> dict[str, Any]:
    """Best-effort retrieval of Fabric runtime metadata."""
    metadata: dict[str, Any] = {
        "notebook_name": notebook_name,
        "workspace_name": None,
        "user_name": None,
        "runtime_available": False,
    }
    try:
        import notebookutils.runtime as nb_runtime  # type: ignore

        metadata["runtime_available"] = True
        context = getattr(nb_runtime, "context", None)
        if context is not None:

            def _ctx_value(*keys: str) -> Any:
                for key in keys:
                    if hasattr(context, key):
                        value = getattr(context, key, None)
                        if value is not None:
                            return value
                    if isinstance(context, dict):
                        value = context.get(key)
                        if value is not None:
                            return value
                    get_method = getattr(context, "get", None)
                    if callable(get_method):
                        value = get_method(key)
                        if value is not None:
                            return value
                return None

            metadata["notebook_name"] = metadata["notebook_name"] or _ctx_value(
                "currentNotebookName", "current_notebook_name"
            )
            metadata["workspace_name"] = _ctx_value("currentWorkspaceName", "workspaceName", "workspace_name")
            metadata["user_name"] = _ctx_value("userName", "user_name")
    except Exception:
        pass
    return metadata
