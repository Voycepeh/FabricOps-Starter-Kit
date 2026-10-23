"""Internal config helpers for FabricOps runtime setup."""


from __future__ import annotations

import hashlib
import json

from copy import deepcopy
from dataclasses import asdict, dataclass, field
from contextvars import ContextVar
from datetime import UTC, datetime
from pathlib import Path
import re
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


DEFAULT_AUDIT_TIMEZONE = "UTC"


_ACTIVE_GOVERNED_CONTEXT: ContextVar = ContextVar("fabricops_governed_context", default=None)


def get_default_fabric_context() -> dict[str, Any]:
    """Return the context resolved from the central registry, never notebook globals."""
    active = _ACTIVE_GOVERNED_CONTEXT.get()
    if active is None:
        raise RuntimeError("No governed context. Run setup_pipeline() or setup_governance(); "
                           "00_env_config and FABRIC_CONTEXT globals are no longer supported. "
                           "Independent public IO accepts an explicit context.")
    return dict(active)


def resolve_fabric_context(
    *,
    config: Any = None,
    env: str | None = None,
    context: dict[str, Any] | None = None,
) -> tuple[Any, str, dict[str, Any]]:
    """Resolve explicit or default FabricOps config and environment values."""
    active = _ACTIVE_GOVERNED_CONTEXT.get()
    if active is not None and active.get("_configuration_locked", True):
        proposed = dict(context or {})
        if ((config is not None and config != active["config"])
                or (env is not None and env != active["env"])
                or (proposed.get("config", active["config"]) != active["config"])
                or (proposed.get("env", active["env"]) != active["env"])):
            raise ValueError("Governed workspace configuration cannot be overridden after setup.")
        for key in ("workspace_id", "notebook_id", "_registry_workspace_id", "_registry_revision",
                    "_registry_config", "_registry_registration", "_registry_bootstrap", "_registry_pipeline", "_configuration_locked"):
            if key in proposed and proposed[key] != active.get(key):
                raise ValueError("Governed runtime identity cannot be overridden after setup.")
        context = {**active, **proposed}
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
    value = config.get("audit_timezone") if isinstance(config, dict) else getattr(config, "audit_timezone", None)
    return _validate_audit_timezone(value)


def normalize_audit_datetime(value: Any, config: Any = None) -> datetime:
    """Preserve instants; interpret timezone-free author input in the configured zone.

    Spark TimestampType collection is a separate boundary: its naive Python
    datetimes represent the Python process's local zone, not the audit zone.
    TimestampNTZ and DateType business values must retain their own semantics.
    """
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    zone = ZoneInfo(get_audit_timezone(config))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=zone)
        # Reject nonexistent wall times instead of silently changing the instant.
        if parsed.astimezone(UTC).astimezone(zone).replace(tzinfo=None) != parsed.replace(tzinfo=None):
            raise ValueError("Timestamp falls in a daylight-saving gap; provide an explicit UTC offset.")
        if parsed.replace(fold=0).utcoffset() != parsed.replace(fold=1).utcoffset():
            raise ValueError("Timestamp is ambiguous during daylight-saving overlap; provide an explicit UTC offset.")
    return parsed.astimezone(zone)


def metadata_timestamp_sort_key(value: Any) -> tuple[int, Any]:
    """Order metadata by instant, including Spark-collected local datetimes."""
    try:
        parsed = value.astimezone(UTC) if isinstance(value, datetime) else normalize_audit_datetime(value)
        return 1, parsed.astimezone(UTC)
    except (TypeError, ValueError):
        return 0, str(value or "")


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
    kind: str
    schema_enabled: bool = False
    schema: str | None = None
    item_name: str | None = None

    def __post_init__(self) -> None:
        """Validate and normalize initialized values."""
        for field_name in ("env", "workspace_id", "item_id", "kind"):
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
class ResolvedFabricStore(FabricStore):
    """Configured Fabric store paired with its environment mapping key."""

    key: str = ""

    def __post_init__(self) -> None:
        """Validate the store details and resolved item name."""
        super().__post_init__()
        if not isinstance(self.key, str) or not self.key.strip():
            raise ValueError("key must be a non-empty string.")


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


DEFAULT_AI_ENRICHMENT = {
    "enabled": False,
    "table_description_prompt": (
        "Write a concise business description of what the selected table represents and supports using only "
        "the supplied FabricOps context. Use the table name, grain, classification, and meaningful business "
        "columns as context. Do not list or paraphrase columns, mention datatypes, summarize the schema, or use "
        "phrasing such as 'contains fields' or 'contains columns'. Treat metadata as evidence rather than business "
        "truth, do not invent unsupported meaning, and return only the proposed description."
    ),
    "column_description_prompt": (
        "Write a concise business description for the selected column using only the supplied FabricOps "
        "column name, datatype, existing description, table context, and profile summary. Treat profile "
        "statistics as observed evidence rather than business truth, do not invent unsupported meaning, "
        "and return only the proposed description."
    ),
    "sensitive_data_prompt": (
        "Assess the selected active canonical column as Direct PII, Indirect PII, or Not PII using only "
        "the supplied table context, column metadata, Enrichment, and profile evidence. Explain the "
        "assessment briefly. For Direct or Indirect PII, suggest only tokenize, mask, bucket, or remove, "
        "explicit parameters, and a Block action. Use Mask for text or categorical columns and Bucket for "
        "numeric values using approved fixed boundaries. Tokenize can protect numeric or categorical "
        "identifiers; Remove supports either. Prefer full masking when Mask applies. The manually selected information "
        "classification is context only, not a PII decision. Profile summaries, min/max, and the top three "
        "frequent values are approved input evidence. Never request full source rows or return raw values. Return "
        "structured JSON only; final review belongs to Governance."
    ),
    "grain_prompt": (
        "Suggest the table row grain and the smallest defensible single or composite row-key candidate using "
        "only governed table metadata, column descriptions, and profile evidence. Prefer a single column when "
        "it is 100% distinct with no missing values. Per-column distinctness cannot prove composite uniqueness, "
        "so describe composite keys as candidates that the table-level uniqueness guardrail must validate. "
        "Return structured JSON only; final review belongs to Governance."
    ),
    "business_rule_prompt": (
        "Resolve Governance-authored business intent into the smallest set of independent deterministic FabricOps "
        "Data Quality rules that preserves the stated requirement. Decompose compound requirements when separate "
        "conditions can fail independently. Resolve referenced columns from the supplied governed table name, "
        "description, column metadata, classifications, profile evidence, and existing DQ rules; an optional column "
        "selection is a constraint, not a requirement. Supported rule types are completeness, uniqueness, value_set, "
        "range, pattern, column_relationship, conditional_completeness, conditional_values, and custom_expression. "
        "Treat a business-language whitelist as value_set mode=allow and a blacklist as value_set mode=block; if both "
        "are explicitly required, return two independent value_set rules. Resolve text-format requirements as Pattern "
        "rules here and generate the deterministic regular expression as an implementation detail for Governance review. "
        "Prefer supported structured patterns before custom_expression; use custom_expression only when none of those "
        "structured patterns can preserve the atomic requirement without changing its meaning. Never invent columns or "
        "business meaning, and do not propose obvious duplicates of existing DQ rules. Observed profile or frequency "
        "values are evidence, not contractual whitelist, blacklist, mappings, patterns, or thresholds unless Governance "
        "explicitly states them as such. Return structured JSON only; final review belongs to Governance."
    ),
}


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
    classification_levels : list[str]
        Controlled information-classification labels rendered by table and
        column metadata enrichment widgets.
    ai_enrichment : dict[str, Any]
        Optional AI Enrichment authoring settings. ``enabled`` controls the
        assistant and the prompt fields provide project instructions.
    sensitive_data_token_mapping : dict[str, Any], optional
        Engineering-managed token vault target with ``store``, ``schema`` and
        ``table_name``. Provision a restricted Delta table before use. The store
        must be separate from Metadata because mappings contain original values.
        Enforce inserts missing assignments; Validate reads without persisting.
        Empty keeps explicit caller-owned mapping management.
    enrichment_context_widget, enrichment_classification_widget : dict[str, Any]
        Widget definitions for organization-specific enrichment fields. Each
        widget uses ``custom_fields`` entries keyed by ``key``.

    """

    required_classification: bool = True
    sensitivity_rules: dict[str, str] = field(default_factory=dict)
    classification_levels: list[str] = field(default_factory=lambda: ["Public", "Restricted", "Confidential", "Highly Sensitive"])
    ai_enrichment: dict[str, Any] = field(default_factory=lambda: dict(DEFAULT_AI_ENRICHMENT))
    enrichment_context_widget: dict[str, Any] = field(default_factory=lambda: {"custom_fields": []})
    enrichment_classification_widget: dict[str, Any] = field(default_factory=lambda: {"custom_fields": []})

    sensitive_data_token_mapping: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and normalize initialized values."""
        target = dict(self.sensitive_data_token_mapping or {})
        if target:
            if set(target) - {"store", "schema", "table_name"} or not all(
                isinstance(target.get(key), str) and target[key].strip() for key in ("store", "table_name")
            ):
                raise ValueError("sensitive_data_token_mapping requires store and table_name; schema is optional.")
            if target["store"].strip().lower() == "metadata":
                raise ValueError("Token mappings contain original values; use a separately restricted store, not Metadata.")
            if target.get("schema") is not None and not isinstance(target["schema"], str):
                raise ValueError("Token mapping schema must be a string or None.")
            target = {key: value.strip() if isinstance(value, str) else value for key, value in target.items()}
        object.__setattr__(self, "sensitive_data_token_mapping", target)
        object.__setattr__(self, "required_classification", bool(self.required_classification))
        object.__setattr__(self, "sensitivity_rules", dict(self.sensitivity_rules or {}))
        labels = [str(option).strip() for option in (self.classification_levels or []) if str(option).strip()]
        labels = labels or ["Public", "Restricted", "Confidential", "Highly Sensitive"]
        if len(labels) != len(set(labels)):
            raise ValueError("classification_levels must contain unique ranked values.")
        object.__setattr__(self, "classification_levels", labels)
        ai_enrichment = {**DEFAULT_AI_ENRICHMENT, **dict(self.ai_enrichment or {})}
        object.__setattr__(self, "ai_enrichment", {
            "enabled": bool(ai_enrichment.get("enabled", False)),
            "table_description_prompt": str(
                ai_enrichment.get("table_description_prompt") or ""
            ).strip(),
            "column_description_prompt": str(
                ai_enrichment.get("column_description_prompt") or ""
            ).strip(),
            "sensitive_data_prompt": str(
                ai_enrichment.get("sensitive_data_prompt") or ""
            ).strip(),
            "grain_prompt": str(ai_enrichment.get("grain_prompt") or "").strip(),
            "business_rule_prompt": str(
                ai_enrichment.get("business_rule_prompt") or ""
            ).strip(),
        })
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
        Lightweight metadata table names provisioned centrally by Governance.
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
    governance_metadata_schema : str, default="governance"
        Physical schema for governance-authored metadata definitions.
    engineering_metadata_schema : str, default="engineering"
        Physical schema for engineering-written metadata.

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
    governance_metadata_schema: str = "governance"
    engineering_metadata_schema: str = "engineering"
    execution_workspace_id: str | None = None

    def __post_init__(self) -> None:
        """Validate and normalize initialized values."""
        object.__setattr__(self, "audit_timezone", _validate_audit_timezone(self.audit_timezone))
        for field_name in ("governance_metadata_schema", "engineering_metadata_schema"):
            value = str(getattr(self, field_name) or "").strip()
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
                raise ValueError(f"{field_name} must be a simple non-empty schema name.")
            object.__setattr__(self, field_name, value)
        if self.governance_metadata_schema == self.engineering_metadata_schema:
            raise ValueError("governance_metadata_schema and engineering_metadata_schema must be different.")


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

    metadata_targets: dict[tuple[str, str], list[str]] = {}
    for env, targets in normalized.path_config.paths.items():
        if not isinstance(targets, dict) or not targets:
            raise ValueError(f"Environment '{env}' must contain at least one target.")
        for target_name, housepath in targets.items():
            required = ("workspace_id", "item_id", "kind")
            if not all(hasattr(housepath, attr) for attr in required):
                raise ValueError(f"Target '{env}/{target_name}' must provide FabricStore fields: {required}.")
        metadata_store = targets.get("Metadata")
        if metadata_store is not None:
            identity = (
                str(getattr(metadata_store, "workspace_id", "")),
                str(getattr(metadata_store, "item_id", "")),
            )
            metadata_targets.setdefault(identity, []).append(str(env))

    if len(metadata_targets) > 1:
        configured = "; ".join(
            f"{', '.join(sorted(envs))} -> {workspace_id}/{item_id}"
            for (workspace_id, item_id), envs in sorted(metadata_targets.items())
        )
        raise ValueError(
            "All configured environments must use the same physical FabricOps Metadata Lakehouse "
            f"(workspace_id + item_id). Configured targets: {configured}."
        )

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


def get_store(config: Any | dict[str, Any] | None, env: str, store: str) -> ResolvedFabricStore:
    """Resolve a configured FabricStore for an environment and logical store key.

    Parameters
    ----------
    env : str
        Environment key such as ``Sandbox``, ``DE``, or ``Prod``.
    store : str
        Configured store key and physical Fabric item name, such as ``Bronze`` or ``Gold``.
    config : FrameworkConfig | PathConfig | None
        Configuration that contains environment-to-store mappings.

    Returns
    -------
    ResolvedFabricStore
        Resolved store with connection details and the configured item ``key``.

    Raises
    ------
    ValueError
        If config is missing, or if the environment/store mapping does not exist.

    Examples
    --------
    >>> get_store(CONFIG, "dev", "Gold").key
    'Gold'

    """
    paths = _normalize_path_config(config).paths
    if env not in paths:
        available_envs = ", ".join(sorted(paths.keys())) or "<none>"
        raise ValueError(
            f"Environment '{env}' was not found in Fabric config. Available environments: {available_envs}."
        )
    if store not in paths[env]:
        available_targets = ", ".join(sorted(paths[env].keys(), key=str.casefold)) or "<none>"
        raise ValueError(
            f"Store '{store}' was not found under environment '{env}'. Available stores: {available_targets}."
        )
    configured_store = paths[env][store]
    if not isinstance(configured_store, FabricStore):
        raise ValueError(f"Store '{env}/{store}' must be configured as a FabricStore.")
    return ResolvedFabricStore(
        env=configured_store.env,
        workspace_id=configured_store.workspace_id,
        item_id=configured_store.item_id,
        kind=configured_store.kind,
        schema_enabled=configured_store.schema_enabled,
        schema=configured_store.schema,
        key=store,
        item_name=configured_store.item_name,
    )


# ---------------------------------------------------------------------------
# Resolver and utility layer: metadata table setup
# ---------------------------------------------------------------------------


def is_table_not_found_error(exc: Exception) -> bool:
    """Return whether an exception indicates a missing metadata table."""
    text = str(exc).lower()
    return any(token in text for token in ("table or view not found", "table not found", "not found", "does not exist", "delta table doesn't exist"))


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


REGISTRY_TABLE = "METADATA_WORKSPACE_REGISTRY"


def fabric_runtime_identity() -> dict[str, Any]:
    """Read executing identity directly from Fabric, ignoring notebook-supplied context."""
    try:
        import notebookutils
        live = notebookutils.runtime.context
    except (ImportError, AttributeError) as exc:
        raise RuntimeError("Governed execution requires the Fabric runtime workspace identity.") from exc
    identity = resolve_runtime_context(context={"runtime_metadata": live}, active_context={})
    from uuid import UUID
    for key in ("workspace_id", "notebook_id"):
        try:
            identity[key] = str(UUID(str(identity[key])))
        except (ValueError, TypeError, AttributeError) as exc:
            raise RuntimeError(f"Fabric runtime did not provide a valid {key}.") from exc
    # Names are audit labels, never configuration or execution requirements.
    identity["workspace_name"] = identity.get("workspace_name") or identity["workspace_id"]
    identity["notebook_name"] = identity.get("notebook_name") or identity["notebook_id"]
    identity["activity_id"] = identity.get("activity_id") or str(__import__("uuid").uuid4())
    return identity


def registry_bootstrap() -> dict[str, Any]:
    """Load the administrator-built wheel's pinned locator; no runtime overrides."""
    from importlib.resources import files
    from uuid import UUID
    locator = json.loads(files("fabricops_kit.config").joinpath("registry_bootstrap.json").read_text())
    if set(locator) != {"governance_workspace_id", "metadata_item_id", "governance_schema", "engineering_schema"}:
        raise RuntimeError("Install the centrally published FabricOps wheel with a pinned registry bootstrap.")
    try:
        for key in ("governance_workspace_id", "metadata_item_id"):
            locator[key] = str(UUID(locator[key]))
        for key in ("governance_schema", "engineering_schema"):
            if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", locator[key]):
                raise ValueError("Invalid metadata schema.")
        if locator["governance_schema"] == locator["engineering_schema"]:
            raise ValueError("Governance and execution schemas must be distinct.")
    except (ValueError, TypeError, AttributeError) as exc:
        raise RuntimeError("Invalid centrally published registry bootstrap.") from exc
    return locator


def bootstrap_context(locator, identity):
    """Construct only the pinned Metadata route, before workspace registration is resolved."""
    env = "GOVERNANCE"
    store = FabricStore(env, locator["governance_workspace_id"], locator["metadata_item_id"],
                        "lakehouse", True, locator["governance_schema"])
    config = FrameworkConfig(PathConfig({env: {"Metadata": store}}), GovernanceConfig(), DataAgreementConfig(),
                             governance_metadata_schema=locator["governance_schema"],
                             engineering_metadata_schema=locator["engineering_schema"])
    return {**identity, "config": config, "env": env}


def read_workspace_registry(*, locator, identity, spark_session=None):
    """Read exactly one central registry snapshot using the pinned physical route."""
    from fabricops_kit.io import read_lakehouse_table
    context = bootstrap_context(locator, identity)
    # Administrative/bootstrap reads must not inherit a different active workspace context.
    saved = _ACTIVE_GOVERNED_CONTEXT.set(None)
    try:
        rows = read_lakehouse_table(REGISTRY_TABLE, store="Metadata", schema=locator["governance_schema"],
                                   context=context, spark_session=spark_session).collect()
    finally:
        _ACTIVE_GOVERNED_CONTEXT.reset(saved)
    if len(rows) != 1:
        raise RuntimeError("Initialize exactly one central Workspace Registry before governed execution.")
    row = rows[0].asDict(recursive=True) if hasattr(rows[0], "asDict") else dict(rows[0])
    snapshot = json.loads(row["snapshot_json"])
    if row.get("authority_id") != "central" or snapshot.get("format") != "fabricops.workspace-registry.v1":
        raise RuntimeError("Unsupported Workspace Registry snapshot.")
    return row["token"], snapshot


def validate_workspace_registration(registration, *, locator):
    """Validate a complete admin-owned workspace mapping without selecting an environment."""
    from uuid import UUID
    row = deepcopy(registration)
    required = {"workspace_id", "display_name", "environment", "status", "resources", "notebooks", "settings"}
    if set(row) != required:
        raise ValueError(f"Workspace registration requires exactly {sorted(required)}.")
    row["workspace_id"] = str(UUID(row["workspace_id"]))
    if not str(row["display_name"]).strip() or row["environment"] not in {"DEV", "TEST", "PROD"}:
        raise ValueError("A workspace display name and explicit DEV, TEST or PROD environment are required.")
    if row["status"] not in {"active", "inactive"}:
        raise ValueError("Registration status must be active or inactive.")
    if not {"Bronze", "Silver", "Gold", "Metadata"} <= set(row["resources"]):
        raise ValueError("Register approved Bronze, Silver, Gold and Metadata resources.")
    for key, resource in row["resources"].items():
        resource = dict(resource)
        for field_name in ("workspace_id", "item_id"):
            resource[field_name] = str(UUID(resource[field_name]))
        store = FabricStore(env=row["environment"], **resource)
        if store.kind == "warehouse" and not store.item_name:
            raise ValueError("Warehouse mappings require the physical item_name as well as item_id.")
        row["resources"][key] = resource
    metadata = row["resources"]["Metadata"]
    if (metadata["workspace_id"], metadata["item_id"], metadata["kind"], metadata.get("schema_enabled")) != (
            locator["governance_workspace_id"], locator["metadata_item_id"], "lakehouse", True):
        raise ValueError("Every workspace must use the pinned central Metadata Lakehouse.")
    for notebook_id, binding in row["notebooks"].items():
        if str(UUID(notebook_id)) != notebook_id or set(binding) != {"pipeline_id", "mode"}:
            raise ValueError("Register notebook UUIDs with pipeline_id and mode.")
        if not str(binding["pipeline_id"]).strip() or binding["mode"] not in {"Test", "Live"}:
            raise ValueError("Notebook bindings require a pipeline_id and exactly Test or Live.")
    registration_context(row, locator=locator, identity={})
    return row


def registration_context(registration, *, locator, identity):
    """Materialize the existing FrameworkConfig from one approved workspace registration."""
    row = registration
    settings = deepcopy(row["settings"])
    allowed = {"governance_config", "data_agreement_config", "audit_timezone"}
    if set(settings) - allowed:
        raise ValueError("Registry settings cannot override resource routing or metadata schemas.")
    config = FrameworkConfig(
        path_config=PathConfig({row["environment"]: {key: FabricStore(env=row["environment"], **resource)
                                                   for key, resource in row["resources"].items()}}),
        governance_config=GovernanceConfig(**settings.get("governance_config", {})),
        data_agreement_config=DataAgreementConfig(**settings.get("data_agreement_config", {})),
        audit_timezone=settings.get("audit_timezone", "UTC"),
        governance_metadata_schema=locator["governance_schema"], engineering_metadata_schema=locator["engineering_schema"],
        execution_workspace_id=row["workspace_id"])
    validate_framework_config(config)
    return {**identity, "config": config, "env": row["environment"], "_registry_workspace_id": row["workspace_id"]}


def resolve_governed_workspace(*, target_workspace_id=None, require_pipeline=False, spark_session=None, bind=True):
    """Resolve trusted runtime and central registration, then pin the complete execution configuration."""
    identity = fabric_runtime_identity()
    locator = registry_bootstrap()
    if target_workspace_id is not None and identity["workspace_id"] != locator["governance_workspace_id"]:
        raise PermissionError("Only Governance Workspace operations may select a registered target workspace.")
    workspace_id = target_workspace_id or identity["workspace_id"]
    token, snapshot = read_workspace_registry(locator=locator, identity=identity, spark_session=spark_session)
    row = snapshot["workspaces"].get(workspace_id)
    if row is None or row.get("status") != "active":
        raise PermissionError("Executing or selected workspace is unknown or inactive in the central registry.")
    row = validate_workspace_registration(row, locator=locator)
    if row["workspace_id"] != workspace_id:
        raise RuntimeError("Workspace Registry key does not match its authoritative workspace ID.")
    context = registration_context(row, locator=locator, identity=identity)
    context.update(_configuration_locked=True, _registry_bootstrap=json.dumps(locator, sort_keys=True),
                   _registry_revision=token, _registry_registration=json.dumps(row, sort_keys=True),
                   _registry_config=json.dumps(asdict(context["config"]), sort_keys=True))
    binding = row["notebooks"].get(identity["notebook_id"])
    if require_pipeline:
        if binding is None or target_workspace_id is not None:
            raise PermissionError("Executing notebook ID has no approved pipeline binding in this workspace.")
        context["_registry_pipeline"] = dict(binding)
    from fabricops_kit.io.shared import get_spark_session
    spark = get_spark_session(spark_session)
    # Syntactic resource validation is eager. Metadata readability is verified by the registry
    # read above; target permissions are enforced by Fabric at the actual IO boundary.
    for key in row["resources"]:
        get_store(context["config"], context["env"], key)
    with suspend_governed_context():
        check_governed_readiness(context, spark_session=spark)
    freeze_governed_configuration(context["config"])
    if "_registry_pipeline" in context:
        context["_registry_pipeline"] = FrozenConfigDict(context["_registry_pipeline"])
    if bind:
        bind_governed_context(context, spark_session=spark)
    return dict(context)


def verify_governed_context(context):
    """Reject runtime, registration or configuration drift before operations and finalization."""
    if not context.get("_registry_revision"):
        return  # Explicit independent IO contexts are outside the governed lifecycle.
    identity = fabric_runtime_identity()
    if any(identity[key] != context[key] for key in ("workspace_id", "notebook_id")):
        raise RuntimeError("Fabric execution identity changed after pipeline setup.")
    if json.dumps(asdict(context["config"]), sort_keys=True) != context["_registry_config"]:
        raise RuntimeError("Governed configuration changed after setup; start a new execution.")
    locator = registry_bootstrap()
    if json.dumps(locator, sort_keys=True) != context["_registry_bootstrap"]:
        raise RuntimeError("Central registry bootstrap changed after setup; start a new execution.")
    _token, snapshot = read_workspace_registry(locator=locator, identity=identity,
                                              spark_session=context.get("_pipeline_spark"))
    row = snapshot["workspaces"].get(context["_registry_workspace_id"])
    if json.dumps(row, sort_keys=True) != context["_registry_registration"]:
        raise RuntimeError("Workspace registration changed after setup; stop and start a new execution.")


def activation_scope(environment, context=None):
    """Scope approvals by executing workspace; historical environment scopes remain read-only history."""
    context = context or {}
    config = context.get("config")
    workspace_id = context.get("_registry_workspace_id") or getattr(config, "execution_workspace_id", None)
    return f"{environment}@{workspace_id}" if workspace_id else environment



def commit_metadata_snapshot(table, snapshot, *, expected_token, context, spark_session=None):
    """Compare-and-swap a preinitialized singleton; confirm lost acknowledgements by exact token."""
    from uuid import uuid4
    from delta.tables import DeltaTable
    from fabricops_kit.io.shared import get_spark_session, resolve_configured_lakehouse_table
    from fabricops_kit.io import read_lakehouse_table
    from fabricops_kit.config.audit import build_runtime_audit_fields
    from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema, metadata_table_schema_registry, coerce_metadata_row_types
    config, env, runtime = resolve_fabric_context(context=context)
    spark = get_spark_session(spark_session)
    schema = metadata_table_physical_schema(config, table)
    _store, _name, _schema, path = resolve_configured_lakehouse_table("Metadata", table, schema, context=context)
    token = str(uuid4())
    row = {"authority_id": "central", "token": token, "snapshot_json": json.dumps(snapshot, sort_keys=True, separators=(",", ":")),
           **build_runtime_audit_fields(config=config, env=env, runtime_context=runtime)}
    frame = spark.createDataFrame([coerce_metadata_row_types(table, row)], schema=metadata_table_schema_registry()[table])
    expected = "'" + expected_token.replace("'", "''") + "'"
    changes = {key: "source." + key for key in row if key != "authority_id"}
    changes["token"] = f"CASE WHEN target.token = {expected} THEN source.token ELSE CAST(raise_error('Stale metadata snapshot; refresh') AS STRING) END"
    failure = None
    try:
        (DeltaTable.forPath(spark, path).alias("target").merge(frame.alias("source"), "target.authority_id = source.authority_id")
         .whenMatchedUpdate(set=changes).execute())
    except Exception as exc:
        failure = exc
    rows = read_lakehouse_table(table, store="Metadata", schema=schema, context=context, spark_session=spark).collect()
    if len(rows) == 1 and rows[0]["token"] == token:
        return token
    raise RuntimeError("Metadata snapshot commit was not confirmed; refresh before retrying.") from failure



def suspend_governed_context():
    """Temporarily suspend default routing for administrative singleton bootstrap only."""
    from contextlib import contextmanager
    @contextmanager
    def suspended():
        token = _ACTIVE_GOVERNED_CONTEXT.set(None)
        try:
            yield
        finally:
            _ACTIVE_GOVERNED_CONTEXT.reset(token)
    return suspended()



class FrozenConfigDict(dict):
    """JSON-compatible mapping that rejects accidental post-setup configuration edits."""

    def _immutable(self, *args, **kwargs):
        raise TypeError("Governed workspace configuration is immutable; update the central registry and rerun setup.")

    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = __ior__ = _immutable

    def __deepcopy__(self, memo):
        """Share immutable configuration safely across plan copies."""
        return self


class FrozenConfigList(list):
    """JSON-compatible immutable sequence for centrally approved policy settings."""

    def _immutable(self, *args, **kwargs):
        raise TypeError("Governed workspace configuration is immutable.")

    __setitem__ = __delitem__ = append = clear = extend = insert = pop = remove = reverse = sort = __iadd__ = __imul__ = _immutable

    def __deepcopy__(self, memo):
        """Share immutable configuration safely across plan copies."""
        return self


def freeze_governed_configuration(value):
    """Freeze nested settings without changing the existing FrameworkConfig and FabricStore types."""
    from dataclasses import fields, is_dataclass
    if is_dataclass(value):
        for item in fields(value):
            object.__setattr__(value, item.name, freeze_governed_configuration(getattr(value, item.name)))
    elif isinstance(value, dict):
        return FrozenConfigDict((key, freeze_governed_configuration(item)) for key, item in value.items())
    elif isinstance(value, list):
        return FrozenConfigList(freeze_governed_configuration(item) for item in value)
    return value



def configure_metadata_transaction(*, spark, config, env, table_name):
    """Provision singleton Serializable isolation using administrator permissions."""
    from fabricops_kit.io.shared import resolve_configured_lakehouse_table
    from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
    _store, _table, _schema, path = resolve_configured_lakehouse_table(
        "Metadata", table_name, metadata_table_physical_schema(config, table_name), context={"config": config, "env": env})
    spark.sql("ALTER TABLE delta.`" + path.replace("`", "``") + "` SET TBLPROPERTIES ('delta.isolationLevel' = 'Serializable')")



def release_governed_context(context):
    """Release the pipeline override lock while retaining approved defaults for independent IO."""
    active = _ACTIVE_GOVERNED_CONTEXT.get()
    if active is not None and context.get("_registry_revision") == active.get("_registry_revision"):
        defaults = dict(active)
        defaults.pop("_registry_pipeline", None)
        defaults["_configuration_locked"] = False
        _ACTIVE_GOVERNED_CONTEXT.set(defaults)


def check_governed_readiness(context, *, spark_session):
    """Verify shared metadata availability and canonical schemas without provisioning as an engineer."""
    from fabricops_kit.io import read_lakehouse_table
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry, metadata_table_physical_schema
    schemas = metadata_table_schema_registry()
    for table in ("METADATA_ACTIVATION_STATE", "METADATA_EXECUTION_STATE", "METADATA_DATA_CATALOGUE",
                  "METADATA_PIPELINE_RUN", "METADATA_GUARDRAIL_RESULTS", "METADATA_SOURCE_OBSERVATION"):
        try:
            frame = read_lakehouse_table(table, store="Metadata",
                schema=metadata_table_physical_schema(context["config"], table), context=context, spark_session=spark_session)
            if set(schemas[table].fieldNames()) - set(frame.schema.fieldNames()):
                raise ValueError("Missing canonical metadata columns.")
            frame.limit(0).collect()
        except Exception as exc:
            raise RuntimeError(f"Shared metadata readiness failed for {table}. Ask Governance to run "
                               "setup_metadata_tables() and verify Fabric read permissions.") from exc



def bind_governed_context(context, *, spark_session=None):
    """Install validated configuration only after the previous pipeline boundary closes."""
    from fabricops_kit.io.shared import get_spark_session
    get_spark_session(spark_session).conf.set("spark.sql.session.timeZone", context["config"].audit_timezone)
    _ACTIVE_GOVERNED_CONTEXT.set(dict(context))
