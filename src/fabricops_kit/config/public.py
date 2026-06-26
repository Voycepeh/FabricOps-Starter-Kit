"""Public config models and notebook-facing setup entrypoints."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
import re
from typing import Any

from .shared import (
    DEFAULT_AUDIT_TIMEZONE,
    DEFAULT_STEWARD_ROLE_OPTIONS,
    _normalize_widget_config,
    _setup_metadata_tables_workflow,
    _setup_notebook_workflow,
    _validate_audit_timezone,
    get_default_fabric_context,
)

_DEFAULT_CONTEXT_ERROR = "No active Fabric context found. Please run 00_env_config before running this notebook."


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
    return _setup_notebook_workflow(
        config=config,
        env=env,
        required_targets=required_targets,
        notebook_name=notebook_name,
        run_id_prefix=run_id_prefix,
        local_fallback_name=local_fallback_name,
    )


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
    return _setup_metadata_tables_workflow(
        spark=spark,
        config=config,
        env=env,
        metadata_schema=metadata_schema,
        require_active_steward=require_active_steward,
    )


# ---------------------------------------------------------------------------
# Utility layer: Spark/Fabric runtime probes
# ---------------------------------------------------------------------------



__all__ = [
    "FabricStore",
    "PathConfig",
    "GovernanceConfig",
    "DataAgreementConfig",
    "FrameworkConfig",
    "ConfigSmokeCheckResult",
    "NotebookSetupContext",
    "setup_notebook",
    "setup_metadata_tables",
    "get_fabric_context",
]
