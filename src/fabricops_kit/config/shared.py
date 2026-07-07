"""Internal config helpers for FabricOps runtime setup."""


from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
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


def build_audit_timestamp_expr(config: Any = None, timezone_name: str | None = None):
    """Return a Spark expression for the current audit timestamp timezone."""
    from pyspark.sql import functions as F

    tz_name = get_audit_timezone(config, timezone_name)
    return F.current_timestamp() if tz_name == "UTC" else F.from_utc_timestamp(F.current_timestamp(), tz_name)


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


def _get_active_metadata_tables(config: Any | dict[str, Any]) -> list[str]:
    """Return the canonical active metadata tables prepared by ``00_env_config``.

    The active registry is intentionally source-driven: agreement tables come
    from ``DataAgreementConfig``, notebook registry from ``widgets.notebook_registry``, and
    governance/pipeline tables from the governance schema registry.
    ``METADATA_DATA_ACCESS`` is part of the active setup registry for public-safe access context. Governance review history is derived from append-only enrichment and guardrail rule rows, not a separate review table.
    """
    normalized = validate_framework_config(config)
    from fabricops_kit.widgets.shared import DATA_AGREEMENT_EVIDENCE_TABLE, DATA_AGREEMENT_TABLE, DATA_STEWARD_TABLE
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
    from fabricops_kit.widgets.notebook_registry import NOTEBOOK_REGISTRY_TABLE

    metadata_tables = normalized.data_agreement_config.metadata_tables or {}
    tables = [
        str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)),
        str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)),
        str(metadata_tables.get("data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE)),
        NOTEBOOK_REGISTRY_TABLE,
        *metadata_table_schema_registry().keys(),
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
    metadata_store = get_store(config=config, env=env, target="metadata")
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


def _get_metadata_table_schema_registry(config: Any | dict[str, Any]) -> dict[str, Any]:
    """Return the canonical metadata setup registry as table names mapped to schemas."""
    normalized = validate_framework_config(config)
    from fabricops_kit.widgets.shared import (
        DATA_AGREEMENT_EVIDENCE_FIELDS,
        DATA_AGREEMENT_EVIDENCE_TABLE,
        DATA_AGREEMENT_FIELDS,
        DATA_AGREEMENT_TABLE,
        DATA_STEWARD_FIELDS,
        DATA_STEWARD_TABLE,
    )
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
    from fabricops_kit.widgets.notebook_registry import NOTEBOOK_REGISTRY_FIELDS, NOTEBOOK_REGISTRY_TABLE

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
    registry.update(metadata_table_schema_registry())
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
    store = get_store(config=config, env=env, target="metadata")
    if getattr(store, "schema_enabled", False):
        return str(getattr(store, "schema", "") or "").strip() or None
    return None


def _is_table_not_found_error(exc: Exception) -> bool:
    """Return whether an exception indicates a missing metadata table."""
    text = str(exc).lower()
    return any(token in text for token in ("table or view not found", "table not found", "not found", "does not exist", "delta table doesn't exist"))


def _setup_metadata_table_registry(
    *,
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
    registry: dict[str, Any],
    metadata_schema: str | None = None,
) -> dict[str, Any]:
    """Create missing metadata tables through configured lakehouse IO helpers."""
    from fabricops_kit.io.shared import read_lakehouse_table_core, write_lakehouse_table_core

    created: list[str] = []
    for table_name, schema in registry.items():
        try:
            read_kwargs = {"spark_session": spark}
            if metadata_schema is not None:
                read_kwargs["schema"] = metadata_schema
            table = read_lakehouse_table_core(
                table_name, target="metadata", context={"config": config, "env": env}, **read_kwargs
            )
        except Exception as exc:
            if not _is_table_not_found_error(exc):
                raise RuntimeError(
                    f"Unable to read metadata table {table_name!r}; not attempting creation because the error was not a confirmed table-not-found condition."
                ) from exc
            empty_df = spark.createDataFrame([], schema=schema)
            write_lakehouse_table_core(
                empty_df,
                table_name,
                target="metadata",
                schema=metadata_schema,
                context={"config": config, "env": env},
                mode="overwrite",
            )
            read_kwargs = {"spark_session": spark}
            if metadata_schema is not None:
                read_kwargs["schema"] = metadata_schema
            table = read_lakehouse_table_core(
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
    from fabricops_kit.io.shared import read_lakehouse_table_core

    normalized = validate_framework_config(config)
    expected = list(expected_tables or _get_active_metadata_tables(normalized))
    resolved_metadata_schema = _resolve_metadata_schema(normalized, env, metadata_schema)
    missing: list[str] = []
    warnings: list[str] = []
    for table in expected:
        try:
            read_kwargs = {"spark_session": spark}
            if resolved_metadata_schema is not None:
                read_kwargs["schema"] = resolved_metadata_schema
            read_lakehouse_table_core(table, target="metadata", context={"config": config, "env": env}, **read_kwargs)
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
        "database": get_store(config=normalized, env=env, target="metadata").name,
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


