"""Internal config helpers for FabricOps runtime setup."""


from __future__ import annotations

import hashlib
import json

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


DEFAULT_AUDIT_TIMEZONE = "UTC"


_DEFAULT_CONTEXT_ERROR = "No active Fabric context found. Please run 00_env_config before running this notebook."


# ---------------------------------------------------------------------------
# Resolver layer: Fabric runtime context
# ---------------------------------------------------------------------------


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


def resolve_runtime_context(
    *,
    context: dict[str, Any] | None = None,
    active_context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve canonical identity values from FabricOps and Fabric runtime contexts."""

    def _valid(value: Any) -> bool:
        if value is None:
            return False
        text = str(value).strip()
        return bool(text) and text.lower() not in {"none", "unknown", "unknown_notebook"}

    def _get(source: Any, key: str) -> Any:
        try:
            if isinstance(source, dict):
                return source.get(key)
            getter = getattr(source, "get", None)
            return getter(key) if callable(getter) else getattr(source, key, None)
        except Exception:
            return None

    def _canonicalize(source: Any) -> dict[str, Any]:
        runtime_metadata = _get(source, "runtime_metadata") or {}
        aliases = {
            "workspace_id": ("workspace_id", "currentWorkspaceId", "workspaceId"),
            "workspace_name": ("workspace_name", "currentWorkspaceName", "workspaceName"),
            "notebook_id": ("notebook_id", "currentNotebookId", "notebookId"),
            "notebook_name": ("notebook_name", "currentNotebookName", "notebookName"),
            "user_name": ("user_name", "userName"),
            "user_id": ("user_id", "userId"),
            "activity_id": ("activity_id", "activityId"),
        }
        values = {}
        for canonical, keys in aliases.items():
            candidates = (*(_get(source, key) for key in keys), *(_get(runtime_metadata, key) for key in keys))
            values[canonical] = next((value for value in candidates if _valid(value)), None)
        return values

    if active_context is None:
        try:
            active_context = get_default_fabric_context()
        except RuntimeError:
            active_context = {}

    try:
        import notebookutils  # type: ignore

        live_context = getattr(getattr(notebookutils, "runtime", None), "context", None) or {}
    except Exception:
        live_context = {}

    sources = (_canonicalize(context or {}), _canonicalize(active_context or {}), _canonicalize(live_context))
    return {
        key: next((source[key] for source in sources if _valid(source.get(key))), None)
        for key in sources[0]
    }


# ---------------------------------------------------------------------------
# Validator layer: audit and framework validation
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Utility and resolver layer: audit timestamps
# ---------------------------------------------------------------------------


def get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
    """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
    if timezone_name is not None:
        return _validate_audit_timezone(timezone_name)
    value = getattr(config, "audit_timezone", None) if config is not None else None
    return _validate_audit_timezone(value)


def get_current_audit_timestamp(
    config: Any = None, timezone_name: str | None = None, *, drop_microseconds: bool = True
) -> str:
    """Return the current audit timestamp in the configured audit timezone."""
    tz_name = get_audit_timezone(config, timezone_name)
    value = datetime.now(ZoneInfo(tz_name))
    if drop_microseconds:
        value = value.replace(microsecond=0)
    return value.isoformat()


# ---------------------------------------------------------------------------
# Model layer: config dataclasses and setup result dataclasses
# ---------------------------------------------------------------------------




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



DEFAULT_STEWARD_ROLE_OPTIONS = [
    "Data Owner",
    "Data Steward",
    "Data Custodian",
    "Governance Reviewer",
    "Business Approver",
]


@dataclass(frozen=True)
class FabricStore:
    """Configured Fabric lakehouse or warehouse connection details."""

    env: str
    workspace_id: str
    item_id: str
    name: str
    kind: str
    schema_enabled: bool = False
    schema: str | None = None

    def __post_init__(self) -> None:
        """Validate and normalize initialized values."""
        for field_name in ("env", "workspace_id", "item_id", "name", "kind"):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field_name} must be a non-empty string.")
        normalized_kind = self.kind.strip().lower()
        if normalized_kind not in {"lakehouse", "warehouse"}:
            raise ValueError("kind must be one of: lakehouse, warehouse.")
        object.__setattr__(self, "kind", normalized_kind)
        object.__setattr__(self, "schema_enabled", bool(self.schema_enabled))
        schema_value = None if self.schema is None else str(self.schema).strip()
        if self.schema_enabled and normalized_kind == "lakehouse":
            if not schema_value:
                raise ValueError("schema is required when schema_enabled is True for a lakehouse store.")
            if any(separator in schema_value for separator in ("/", "\\", ".")):
                raise ValueError("schema must be a simple schema name; do not use paths or dots.")
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", schema_value):
                raise ValueError("schema must contain only letters, numbers, and underscores, and must not start with a number.")
        object.__setattr__(self, "schema", schema_value or None)

    @property
    def root(self) -> str:
        """Return the OneLake ABFSS root for lakehouse stores."""
        if self.kind != "lakehouse":
            raise ValueError("root is only available for lakehouse stores.")
        return f"abfss://{self.workspace_id}@onelake.dfs.fabric.microsoft.com/{self.item_id}"


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


@dataclass(frozen=True)
class DataAgreementConfig:
    """Editable ``01_governance`` table names and widget definitions.

    Parameters
    ----------
    metadata_tables : dict[str, str]
        Lightweight metadata table names prepared by ``00_env_config``.
    data_steward_widget, data_agreement_widget : dict[str, Any]
        Visible standard columns and organization-specific ``custom_fields``.
        Custom fields are rendered dynamically and persisted in
        ``custom_fields_json`` instead of becoming physical table columns.
    steward_role_options : list[str]
        Controlled Data Steward role labels rendered by ``01_governance`` as the
        ``steward_role`` dropdown.

    """

    metadata_tables: dict[str, str] = field(
        default_factory=lambda: {
            "data_steward": "METADATA_DATA_STEWARD",
            "data_agreement": "METADATA_DATA_AGREEMENT",
        }
    )
    data_steward_widget: dict[str, Any] = field(
        default_factory=lambda: {
            "visible_columns": [
                "steward_name",
                "steward_role",
                "contact",
            ],
            "custom_fields": [],
        }
    )
    data_agreement_widget: dict[str, Any] = field(
        default_factory=lambda: {
            "visible_columns": [
                "agreement_name",
                "domain",
                "provider_steward_id",
                "recipient_steward_id",
                "start_date",
                "expiry_date",
                "business_purpose",
            ],
            "approved_usage_options": ["internal cross domain", "internal single domain", "research", "external"],
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
class FrameworkConfig:
    """Top-level framework configuration object.

    Parameters
    ----------
    path_config : PathConfig
        Environment and target routing definitions.
    governance_config : GovernanceConfig, optional
        Default governance-policy settings. Uses package defaults when omitted.
    data_agreement_config : DataAgreementConfig, optional
        Editable agreement table and widget definitions. Uses package defaults when omitted.
    audit_timezone : str, default="UTC"
        IANA timezone used for FabricOps-generated audit and technical timestamps.

    Examples
    --------
    >>> cfg = FrameworkConfig(path_config=PathConfig(paths={"dev": {"source": object()}}))
    >>> isinstance(cfg, FrameworkConfig)
    True

    """

    path_config: PathConfig
    governance_config: GovernanceConfig = field(default_factory=GovernanceConfig)
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





def validate_framework_config(config: Any | dict[str, Any]) -> Any:
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
    >>> normalized = validate_framework_config(framework_config)
    >>> isinstance(normalized, FrameworkConfig)
    True

    """
    if isinstance(config, FrameworkConfig):
        normalized = config
    elif isinstance(config, dict):
        required_keys = {
            "path_config",
        }
        missing_keys = sorted(required_keys.difference(config.keys()))
        if missing_keys:
            raise ValueError(f"Framework config is missing required keys: {', '.join(missing_keys)}.")
        normalized = FrameworkConfig(**config)
    else:
        raise ValueError("config must be a FrameworkConfig object or compatible mapping.")

    if not isinstance(normalized.path_config, PathConfig):
        raise ValueError("path_config must be a PathConfig object.")
    if not isinstance(normalized.governance_config, GovernanceConfig):
        raise ValueError("governance_config must be a GovernanceConfig object.")
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


# ---------------------------------------------------------------------------
# Normalizer and resolver layer: paths and stores
# ---------------------------------------------------------------------------


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


def get_store(config: Any | dict[str, Any] | None, env: str, target: str) -> Any:
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


# ---------------------------------------------------------------------------
# Resolver and utility layer: metadata table setup
# ---------------------------------------------------------------------------


def is_table_not_found_error(exc: Exception) -> bool:
    """Return whether an exception indicates a missing metadata table."""
    text = str(exc).lower()
    return any(token in text for token in ("table or view not found", "table not found", "not found", "does not exist", "delta table doesn't exist"))


def _stable_metadata_key(*parts: Any) -> str:
    import hashlib
    import json

    payload = [
        {"is_null": part is None, "value": None if part is None else str(part).strip().lower()} for part in parts
    ]
    return hashlib.sha256(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")).hexdigest()


def build_metadata_table_key(store_type: Any, layer: Any, schema_name: Any, table_name: Any) -> str:
    """Return the environment-independent logical identity for a table."""
    return _stable_metadata_key(store_type, layer, schema_name, table_name)


def build_metadata_column_key(metadata_table_key: Any, column_name: Any) -> str:
    """Return the environment-independent logical identity for a column."""
    return _stable_metadata_key(metadata_table_key, column_name)


def stable_metadata_id(*parts: Any) -> str:
    """Return a deterministic SHA-256 identity from normalized logical parts."""
    payload = [
        {"is_null": part is None, "value": None if part is None else str(part).strip().lower()}
        for part in parts
    ]
    return hashlib.sha256(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def build_table_id(store_type: Any, layer: Any, schema_name: Any, table_name: Any) -> str:
    """Return the environment-independent logical identity for a table asset."""
    return stable_metadata_id(store_type, layer, schema_name, table_name)


def build_column_id(table_id: Any, column_name: Any) -> str:
    """Return the environment-independent logical identity for a column asset."""
    return stable_metadata_id(table_id, column_name)
