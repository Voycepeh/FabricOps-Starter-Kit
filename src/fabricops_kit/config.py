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
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import yaml
from jsonschema import Draft202012Validator

DEFAULT_AUDIT_TIMEZONE = "UTC"


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


def _current_audit_timestamp(config: Any = None, timezone_name: str | None = None, *, drop_microseconds: bool = True) -> str:
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


DEFAULT_DQ_RULE_SUGGESTION_PROMPT_TEMPLATE = """
You are helping draft candidate FabricOps-native data quality rules for a Microsoft Fabric pipeline.

These suggestions are advisory drafts only. A human reviewer must approve, edit, or reject every rule before enforcement.

Suggest FabricOps-native DQ rules only. FabricOps supports 23 FabricOps-native DQ rule types. Use only supported rule_type values. Do not invent rule types. Prefer simple named rules before expression_true. Treat expression_true as the Custom expression rule and use it only when no smaller named rule can express the requirement; only trusted reviewers should approve expression rules.

Rule selection principles:
- Suggest DQ rules only when the column profile or business context gives enough evidence.
- Prefer the smallest named rule that expresses the requirement.
- Use column profile evidence: data_type, row_count, null_count, null_percent, distinct_count, distinct_percent, min_value, max_value, and observed_values_sample.
- Do not suggest datatype/schema rules; schema validation is separate.
- Do not suggest profile behavior guardrail rules; profile behavior checks are separate.
- Schema guardrails and profile behavior guardrails are separate FabricOps layers.
- Do not suggest row filtering or quarantine behavior; FabricOps v1 reports/tags outcomes and error severity blocks unsafe downstream writes.
- Use expression_true only as the Custom expression escape hatch when no smaller rule fits.

Data type / constraint-shape guidance and required parameters for all 23 rule types:

Rule catalogue guidance:
Completeness:
- not_null: any profiled column where every row must have a non-null value. Required: columns.
- null_rate_below: any profiled column where some nulls are allowed but the null percentage must stay below a threshold. Required: columns, max_null_percent.
- non_empty_string: string columns where blank or whitespace-only values should fail. Required: columns.
- required_when: any target column required only when a condition is true. Required: columns, condition.

Uniqueness:
- unique: one column should uniquely identify rows. Required: columns.
- unique_combination: a composite business key or table grain should be unique. Required: columns.

Allowed / blocked values:
- accepted_values: governed allowed values for string, numeric, boolean, or code columns. Required: columns, allowed_values.
- not_in_values: placeholder, blocked, retired, or invalid values must not appear. Required: columns, blocked_values.

Numeric / comparable ranges:
- between: comparable value must be within min and/or max. Common for numeric, date, timestamp, or consistently formatted strings. Required: columns, at least one of min_value or max_value.
- greater_than: value must be greater than threshold. Required: columns, value.
- greater_than_or_equal: value must be greater than or equal to threshold. Required: columns, value.
- less_than: value must be less than threshold. Required: columns, value.
- less_than_or_equal: value must be less than or equal to threshold. Required: columns, value.

Pattern and date rules:
- regex_match: string column must match a pattern. Required: columns, regex_pattern.
- date_not_future: date or timestamp column must not be in the future. Required: columns.
- date_between: date or timestamp column must be within a date range. Required: columns, min_value, max_value.
- freshness: date or timestamp column must be recent enough. Required: columns, max_age_days.
- max_age_days: date or timestamp value must not be older than max age. Required: columns, max_age_days.

Cross-column logic:
- column_pair_equal: two compatible columns must be equal. Required: exactly two columns.
- column_a_gte_column_b: first comparable column must be greater than or equal to second. Required: exactly two columns.
- column_a_gt_column_b: first comparable column must be greater than second. Required: exactly two columns.
- value_when: target column must equal expected_value when condition is true. Required: one columns value, condition, expected_value.

Advanced:
- expression_true: Custom expression rule. Use only when no named rule can express the business requirement. Required: expression. Prefer not to use it unless there is clear business logic evidence.

Priority guide:
- If checking presence, choose not_null, null_rate_below, non_empty_string, or required_when.
- If checking duplicate grain, choose unique or unique_combination.
- If checking governed categories, choose accepted_values.
- If checking invalid placeholders, choose not_in_values.
- If checking numeric or date bounds, choose between or threshold rules.
- If checking formatted text, choose regex_match.
- If checking recency, choose freshness or max_age_days.
- If checking relationship between columns, choose cross-column rules.
- If checking conditional business logic, choose required_when or value_when.
- Use expression_true only after all named rules are insufficient.

Evidence guidance:
- Use not_null only when business context indicates the column is mandatory or null_count is already zero and the column looks required.
- Use accepted_values only when observed_values_sample or business context shows a stable controlled set.
- Use unique when distinct_count equals or is expected to equal row_count.
- Use unique_combination only when business context indicates a composite key/table grain.
- Use null_rate_below when nulls are expected but should stay within tolerance.
- Use warning severity by default unless the rule protects a key, required business field, financial measure, compliance field, or downstream join/grain integrity.
- Use error severity when bad data would make output unsafe or misleading.

Output guardrails:
- Every suggestion must include rule_id, rule_type, columns, severity, description, and required parameters.
- rule_id must be lower snake case.
- columns must contain actual column names from the profile/context.
- Do not invent columns.
- Do not invent rule types.
- Do not output markdown.
- Do not output comments.
- Return valid JSON only.

What belongs outside DQ:
- Do not suggest schema rules such as required_columns, expected_schema, or datatype checks.
- Do not suggest profile behavior guardrail rules.
- Schema guardrails and profile behavior guardrails are separate FabricOps layers.

Return valid JSON only in this shape:
{"DQ_RULES":{"{table_name}":[{"rule_id":"lower_snake_case_rule_id","rule_type":"not_null","columns":["column_name"],"severity":"warning","description":"Plain business explanation."}]}}

Table name: {table_name}
Business context: {business_context}
Column profile row:
Column name: {column_name}
Data type: {data_type}
Row count: {row_count}
Null count: {null_count}
Null percent: {null_percent}
Distinct count: {distinct_count}
Distinct percent: {distinct_percent}
Minimum value: {min_value}
Maximum value: {max_value}
Observed values sample: {observed_values_sample}
""".strip()


@dataclass(frozen=True)
class AIPromptConfig:
    """Prompt templates used by implemented AI-assisted workflows.

    Parameters
    ----------
    business_context_prompt_template : str, optional
        Prompt used for business-context drafting. Blank values use the
        package default.
    dq_rule_suggestion_prompt_template : str, optional
        Prompt used for data-quality rule suggestions. Blank values use the
        package default.
    governance_personal_identifier_prompt_template : str, optional
        Prompt used for personal-identifier classification suggestions. Blank
        values use the package default.
    """

    business_context_prompt_template: str = ""
    dq_rule_suggestion_prompt_template: str = ""
    governance_personal_identifier_prompt_template: str = ""

    def __post_init__(self) -> None:
        defaults = {
            "business_context_prompt_template": DEFAULT_BUSINESS_CONTEXT_PROMPT_TEMPLATE,
            "dq_rule_suggestion_prompt_template": DEFAULT_DQ_RULE_SUGGESTION_PROMPT_TEMPLATE,
            "governance_personal_identifier_prompt_template": DEFAULT_GOVERNANCE_PERSONAL_IDENTIFIER_PROMPT_TEMPLATE,
        }
        for label, default in defaults.items():
            value = getattr(self, label)
            if not isinstance(value, str):
                raise ValueError(f"{label} must be a string.")
            resolved = value.strip() or default
            if not resolved.strip():
                raise ValueError(f"{label} must be a non-empty string.")
            object.__setattr__(self, label, resolved)


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
    ...     ai_prompt_config=AIPromptConfig(),
    ... )
    >>> isinstance(cfg, FrameworkConfig)
    True
    """

    path_config: PathConfig
    notebook_runtime_config: NotebookRuntimeConfig
    ai_prompt_config: AIPromptConfig
    quality_config: QualityConfig = field(default_factory=QualityConfig)
    governance_config: GovernanceConfig = field(default_factory=GovernanceConfig)
    review_workflow_config: ReviewWorkflowConfig = field(default_factory=ReviewWorkflowConfig)
    lineage_config: LineageConfig = field(default_factory=LineageConfig)
    data_agreement_config: DataAgreementConfig = field(default_factory=DataAgreementConfig)
    audit_timezone: str = DEFAULT_AUDIT_TIMEZONE

    def __post_init__(self) -> None:
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
            "ai_prompt_config",
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
    _validate_audit_timezone(normalized.audit_timezone)

    for env_name, targets in normalized.path_config.paths.items():
        if not isinstance(targets, dict) or not targets:
            raise ValueError(f"Environment '{env_name}' must contain at least one target.")
        for target_name, housepath in targets.items():
            required = ("workspace_id", "item_id", "name", "kind")
            if not all(hasattr(housepath, attr) for attr in required):
                raise ValueError(f"Target '{env_name}/{target_name}' must provide FabricStore fields: {required}.")

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
    ``METADATA_DATA_ACCESS`` is documented as optional access-capture metadata
    and is not part of the current active setup registry.
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


def _metadata_tables_from_setup_results(*summaries: dict[str, Any]) -> list[str]:
    """Return ordered metadata table names from setup helper summaries."""
    tables: list[str] = []
    for summary in summaries:
        for key in ("tables", "table"):
            value = summary.get(key) if isinstance(summary, dict) else None
            values = value if isinstance(value, list) else [value] if value else []
            for table in values:
                table_name = str(table or "").strip()
                if table_name and table_name not in tables:
                    tables.append(table_name)
    return tables


def _detect_nested_metadata_delta_folders(*, config: FrameworkConfig | dict[str, Any], env: str, expected_tables: list[str]) -> list[str]:
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


def _metadata_table_columns(table: Any) -> list[str]:
    """Return column names from a Spark DataFrame-like object or row collection."""
    columns = list(getattr(table, "columns", []) or [])
    if columns:
        return columns
    rows = _coerce_row_dicts(table)
    return list(rows[0]) if rows else []


def _create_empty_metadata_dataframe(spark: Any, schema: Any) -> Any:
    """Create an empty Spark DataFrame using an explicit metadata schema."""
    return spark.createDataFrame([], schema=schema)



def _resolve_metadata_schema(config: FrameworkConfig | dict[str, Any], env: str, metadata_schema: str | None = None) -> str | None:
    """Return explicit metadata schema or configured metadata target schema."""
    if metadata_schema is not None:
        return str(metadata_schema).strip() or None
    store = _get_store(config=config, env=env, target="metadata")
    if getattr(store, "schema_enabled", False):
        return str(getattr(store, "schema", "") or "").strip() or None
    return None

def _setup_metadata_table_registry(
    *, spark: Any, config: FrameworkConfig | dict[str, Any], env: str, registry: dict[str, Any], metadata_schema: str | None = None
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
            table = read_lakehouse_table(config, env, "metadata", table_name, **read_kwargs)
        except Exception as exc:
            if not _is_table_not_found_error(exc):
                raise RuntimeError(
                    f"Unable to read metadata table {table_name!r}; not attempting creation because the error was not a confirmed table-not-found condition."
                ) from exc
            empty_df = _create_empty_metadata_dataframe(spark, schema)
            write_lakehouse_table(empty_df, config, env, "metadata", table_name, schema=metadata_schema, mode="overwrite", options={"overwriteSchema": "true"})
            read_kwargs = {"spark_session": spark}
            if metadata_schema is not None:
                read_kwargs["schema"] = metadata_schema
            table = read_lakehouse_table(config, env, "metadata", table_name, **read_kwargs)
            created.append(table_name)

        missing = [field for field in _metadata_schema_field_names(schema) if field not in _metadata_table_columns(table)]
        if missing:
            raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}. Recreate or manually migrate the table before running metadata setup.")
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
            read_lakehouse_table(normalized, env, "metadata", table, **read_kwargs)
        except Exception:
            missing.append(table)
    nested_paths = _detect_nested_metadata_delta_folders(config=normalized, env=env, expected_tables=expected)
    if missing:
        warnings.append("Expected metadata tables could not be read from the configured metadata target.")
    if nested_paths:
        warnings.append(
            "Detected legacy nested metadata Delta folders under Tables/<metadata_table>/Unidentified/_delta_log. "
            "FabricOps will not delete or migrate user data automatically; review and migrate those folders manually if needed. "
            + ("When metadata schema routing is configured, new metadata setup uses schema-aware Lakehouse paths. " if resolved_metadata_schema else "New metadata setup writes directly to configured ABFSS Lakehouse table paths.")
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
        "fully_qualified_tables": [f"{resolved_metadata_schema}.{table}" if resolved_metadata_schema else table for table in expected],
        "show_tables_statement": None,
        "optional_documented_tables": ["METADATA_DATA_ACCESS"],
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
    setup_registry = _setup_metadata_table_registry(spark=spark, config=normalized, env=env, registry=registry, metadata_schema=resolved_metadata_schema)
    expected_tables = list(registry)
    fully_qualified_tables = [f"{resolved_metadata_schema}.{table}" if resolved_metadata_schema else table for table in expected_tables]
    created_tables = list(setup_registry["created_tables"])

    metadata_tables = normalized.data_agreement_config.metadata_tables or {}
    data_agreement_tables = [
        str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)),
        str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)),
        str(metadata_tables.get("data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE)),
    ]
    active_stewards = _list_data_stewards(normalized, env, spark_session=spark, active_only=True, missing_ok=True, metadata_schema=resolved_metadata_schema)
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
    created_or_checked = _metadata_tables_from_setup_results(data_agreement, notebook_registry, governance)
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
        "status": "ready" if all(status == "ready" for status in setup_statuses) and registration_status in {"ready", "skipped"} else "not_ready",
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
