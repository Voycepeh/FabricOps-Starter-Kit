"""Configuration bootstrap and contract validation for FabricOps notebook pipelines.

This module is the workflow entrypoint for establishing the ``00_env_config``
contract, standard environment path definitions, notebook prefix policies, AI
prompt templates, and smoke-check validation before data movement starts.
Use it early in a Fabric run so downstream IO, quality, lineage, and review
steps execute with explicit, validated runtime context.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from importlib.resources import files
from pathlib import Path
import re
from typing import Any

import yaml
from jsonschema import Draft202012Validator


class DatasetContractValidationError(Exception):
    """Raised when dataset-contract validation fails."""


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
        prefixes = tuple(prefix.strip() for prefix in self.allowed_notebook_prefixes if str(prefix).strip())
        if not prefixes:
            raise ValueError("allowed_notebook_prefixes must contain at least one non-empty prefix.")
        object.__setattr__(self, "allowed_notebook_prefixes", prefixes)


@dataclass(frozen=True)
class AIPromptConfig:
    """Prompt templates used by AI-assisted framework workflows."""

    business_context_prompt_template: str = ""
    dq_rule_suggestion_prompt_template: str = ""
    governance_personal_identifier_prompt_template: str = ""
    governance_candidate_prompt_template: str = ""
    governance_review_prompt_template: str = ""

    def __post_init__(self) -> None:
        for label, value in {
            "business_context_prompt_template": self.business_context_prompt_template,
            "dq_rule_suggestion_prompt_template": self.dq_rule_suggestion_prompt_template,
            "governance_personal_identifier_prompt_template": self.governance_personal_identifier_prompt_template,
            "governance_candidate_prompt_template": self.governance_candidate_prompt_template,
            "governance_review_prompt_template": self.governance_review_prompt_template,
        }.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{label} must be a non-empty string.")


DEFAULT_BUSINESS_CONTEXT_PROMPT_TEMPLATE = """
Infer business meaning only for one column. Do not classify personal data.
Use table_name={table_name}, table_context={table_context}, column_name={column_name}, data_type={data_type},
row_count={row_count}, null_count={null_count}, distinct_count={distinct_count}, observed_values_sample={observed_values_sample}.
Return only Python dict:
BUSINESS_CONTEXT = {"column_name": "name", "business_context": "clear business meaning", "notes": "optional reviewer note"}
""".strip()

DEFAULT_GOVERNANCE_PERSONAL_IDENTIFIER_PROMPT_TEMPLATE = """
Use approved_business_context as evidence. Classify personal identifier status separately from business context.
Allowed personal identifier values: not_personal_data, direct_identifier, indirect_identifier, unknown.
Allowed confidentiality labels: public, confidential, restricted.
Return only JSON dict with keys:
column_name, ai_suggested_personal_identifier_classification, confidentiality_label, evidence, reasoning.
""".strip()


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
        severity = str(self.default_severity).strip().lower()
        if severity not in {"info", "warning", "critical"}:
            raise ValueError("default_severity must be one of: info, warning, critical.")
        object.__setattr__(self, "default_severity", severity)
        object.__setattr__(self, "fail_on_critical", bool(self.fail_on_critical))
        object.__setattr__(self, "quarantine_on_failure", bool(self.quarantine_on_failure))


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
    """

    required_classification: bool = True
    sensitivity_rules: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "required_classification", bool(self.required_classification))
        object.__setattr__(self, "sensitivity_rules", dict(self.sensitivity_rules or {}))


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
        object.__setattr__(self, "metadata_tables", deepcopy(dict(self.metadata_tables or {})))
        object.__setattr__(self, "data_steward_widget", deepcopy(dict(self.data_steward_widget or {})))
        object.__setattr__(self, "data_agreement_widget", deepcopy(dict(self.data_agreement_widget or {})))
        options = [str(option).strip() for option in (self.steward_role_options or []) if str(option).strip()]
        object.__setattr__(self, "steward_role_options", options or list(DEFAULT_STEWARD_ROLE_OPTIONS))


@dataclass(frozen=True)
class ReviewWorkflowConfig:
    """Notebook-table review settings for DQ and governance suggestion approval."""

    business_context: str = ""
    approved_usage: str = ""
    profile_table: str = "metadata.profile_rows"
    business_context_review_table: str = "metadata.business_context_review"
    business_context_approved_table: str = "metadata.business_context_approved"
    dq_review_table: str = "metadata.dq_review"
    dq_approved_table: str = "metadata.dq_approved"
    governance_review_table: str = "metadata.governance_review"
    governance_approved_table: str = "metadata.governance_approved"
    default_approval_status: str = "pending"


@dataclass(frozen=True)
class LineageConfig:
    """Default lineage-capture behavior for pipeline traceability.

    Parameters
    ----------
    capture_ai_summaries : bool, default=True
        Whether AI-generated summaries should be stored in lineage artifacts.
    capture_transformation_steps : bool, default=True
        Whether transformation-level steps should be included in lineage
        capture payloads.
    """

    capture_ai_summaries: bool = True
    capture_transformation_steps: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "capture_ai_summaries", bool(self.capture_ai_summaries))
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
    ai_prompt_config : AIPromptConfig
        AI prompt templates used across framework workflows.
    quality_config : QualityConfig
        Default quality-policy settings.
    governance_config : GovernanceConfig
        Default governance-policy settings.
    review_workflow_config : ReviewWorkflowConfig
        Notebook-native review, approval, and metadata destination settings.
    lineage_config : LineageConfig
        Default lineage capture behavior.

    Examples
    --------
    >>> cfg = FrameworkConfig(
    ...     path_config=PathConfig(paths={"dev": {"source": object()}}),
    ...     notebook_runtime_config=NotebookRuntimeConfig(("00_",)),
    ...     ai_prompt_config=AIPromptConfig("context", "dq", "personal", "candidate", "review"),
    ...     quality_config=QualityConfig(),
    ...     governance_config=GovernanceConfig(),
    ...     lineage_config=LineageConfig(),
    ... )
    >>> isinstance(cfg, FrameworkConfig)
    True
    """

    path_config: PathConfig
    notebook_runtime_config: NotebookRuntimeConfig
    ai_prompt_config: AIPromptConfig
    quality_config: QualityConfig
    governance_config: GovernanceConfig
    review_workflow_config: ReviewWorkflowConfig
    lineage_config: LineageConfig
    data_agreement_config: DataAgreementConfig = field(default_factory=DataAgreementConfig)


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
        Existing framework config object or compatible mapping containing all
        required component configs.

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
            "ai_prompt_config",
            "quality_config",
            "governance_config",
            "review_workflow_config",
            "lineage_config",
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
    if not isinstance(normalized.ai_prompt_config, AIPromptConfig):
        raise ValueError("ai_prompt_config must be an AIPromptConfig object.")
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

    for env_name, targets in normalized.path_config.paths.items():
        if not isinstance(targets, dict) or not targets:
            raise ValueError(f"Environment '{env_name}' must contain at least one target.")
        for target_name, housepath in targets.items():
            required = ("workspace_id", "item_id", "name", "kind")
            if not all(hasattr(housepath, attr) for attr in required):
                raise ValueError(f"Target '{env_name}/{target_name}' must provide FabricStore fields: {required}.")

    return normalized


def _get_store(config: FrameworkConfig | PathConfig | None, env: str, target: str) -> Any:
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
    if config is None:
        raise ValueError("No Fabric config was provided. Pass a FrameworkConfig or PathConfig instance.")
    paths = config.path_config.paths if isinstance(config, FrameworkConfig) else config.paths
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


def setup_metadata_tables(
    *,
    spark: Any,
    config: FrameworkConfig | dict[str, Any],
    env: str,
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
    require_active_steward : bool, default=False
        Forwarded to the agreement metadata setup to optionally require an
        active steward before returning success.

    Returns
    -------
    dict[str, Any]
        Combined setup summary keyed by ``data_agreement``,
        ``notebook_registry``, and ``governance``.

    Notes
    -----
    This is the v1 notebook setup action for metadata provisioning. It keeps
    ``00_env_config`` simple while delegating to internal helpers that route all
    metadata reads and writes through the configured metadata lakehouse target.
    """
    from fabricops_kit.data_agreement import _setup_data_agreement_tables
    from fabricops_kit.governance_review import _setup_governance_metadata_tables
    from fabricops_kit.metadata import _setup_notebook_registry_table

    data_agreement = _setup_data_agreement_tables(
        spark=spark,
        config=config,
        env=env,
        require_active_steward=require_active_steward,
    )
    notebook_registry = _setup_notebook_registry_table(spark=spark, config=config, env=env)
    governance = _setup_governance_metadata_tables(spark=spark, config=config, env=env)
    statuses = [data_agreement.get("status"), notebook_registry.get("status"), governance.get("status")]
    return {
        "status": "ready" if all(status == "ready" for status in statuses) else "not_ready",
        "data_agreement": data_agreement,
        "notebook_registry": notebook_registry,
        "governance": governance,
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


def _default_schema_text() -> str:
    return files("fabricops_kit.schemas").joinpath("dataset_contract.schema.json").read_text(encoding="utf-8")


# dataset-contract helpers unchanged


def _format_error_path(error_path: list[object], message: str, validator: str) -> str:
    parts = [str(part) for part in error_path]
    base_path = ".".join(parts)
    if validator == "required":
        match = re.search(r"'([^']+)' is a required property", message)
        if match:
            missing_property = match.group(1)
            return f"{base_path}.{missing_property}" if base_path else missing_property
    return base_path or "$"


def _load_dataset_contract(path: str | Path) -> dict:
    """Load a dataset contract YAML file into a dictionary.

    Parameters
    ----------
    path : str or Path
        Path to a dataset-contract file, typically versioned beside pipeline
        notebooks or in a shared config folder.

    Returns
    -------
    dict
        Parsed contract content. Empty files return ``{}``; non-mapping YAML
        values are wrapped as ``{"value": <loaded_value>}`` for safer handling.

    Examples
    --------
    >>> contract = _load_dataset_contract("configs/sales_contract.yml")
    >>> isinstance(contract, dict)
    True
    """
    contract_path = Path(path)
    with contract_path.open("r", encoding="utf-8") as handle:
        loaded = yaml.safe_load(handle)
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        return {"value": loaded}
    return loaded


def _load_schema(schema_path: str | Path | None = None) -> dict:
    if schema_path is None:
        return yaml.safe_load(_default_schema_text())
    with Path(schema_path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _validate_dataset_contract(contract: dict, schema_path: str | Path | None = None) -> list[str]:
    """Validate a loaded dataset contract against the JSON schema.

    Parameters
    ----------
    contract : dict
        Dataset contract content produced by :func:`_load_dataset_contract`.
    schema_path : str or Path or None, default=None
        Optional custom schema location. When omitted, the packaged FabricOps
        dataset-contract schema is used.

    Returns
    -------
    list of str
        Validation error messages using normalized property paths that are
        suitable for notebook run summaries and review logs.

    Notes
    -----
    This function does not raise by default, allowing notebook orchestration to
    collect all schema issues before deciding whether to fail fast.
    """
    schema = _load_schema(schema_path=schema_path)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(contract), key=lambda error: (list(error.path), error.message))
    return [
        f"{_format_error_path(list(error.path), error.message, error.validator)}: {error.message}" for error in errors
    ]


def _assert_valid_dataset_contract(contract: dict, schema_path: str | Path | None = None) -> None:
    """Raise when a dataset contract violates the expected schema.

    Parameters
    ----------
    contract : dict
        Contract content to validate before executing ingestion, quality, and
        metadata stages.
    schema_path : str or Path or None, default=None
        Optional custom schema location. The built-in schema is used when this
        value is ``None``.

    Raises
    ------
    DatasetContractValidationError
        Raised when one or more validation issues are found.
    """
    errors = _validate_dataset_contract(contract, schema_path=schema_path)
    if errors:
        raise DatasetContractValidationError(
            "Dataset contract validation failed:\n" + "\n".join(f"- {e}" for e in errors)
        )


def _load_and_validate_dataset_contract(
    path: str | Path, schema_path: str | Path | None = None
) -> tuple[dict, list[str]]:
    """Load a dataset contract file and return schema validation findings.

    Parameters
    ----------
    path : str or Path
        Contract YAML path used by a Fabric notebook or pipeline run.
    schema_path : str or Path or None, default=None
        Optional schema override for custom contract extensions.

    Returns
    -------
    tuple of (dict, list of str)
        Loaded contract payload and a list of validation errors.

    Examples
    --------
    >>> contract, errors = _load_and_validate_dataset_contract("configs/orders.yml")
    >>> len(errors) >= 0
    True
    """
    contract = _load_dataset_contract(path)
    return contract, _validate_dataset_contract(contract, schema_path=schema_path)
