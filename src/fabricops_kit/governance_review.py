"""Table-scoped governance review helpers for ``03_review`` notebooks."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from datetime import datetime, timezone
import importlib
import json
import re
import uuid
from typing import Any, Iterable

from .config import DEFAULT_BUSINESS_CONTEXT_PROMPT_TEMPLATE, DEFAULT_GOVERNANCE_PERSONAL_IDENTIFIER_PROMPT_TEMPLATE
from .fabric_input_output import read_lakehouse_table, write_lakehouse_table
from .data_profiling import profile_dataframe
from .metadata import _now_utc_iso, _resolve_action_by, _build_metadata_column_key, _build_metadata_table_key, _build_runtime_audit_fields, _build_dq_rule_key

CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
COLUMN_CONTEXT_TABLE = "METADATA_COLUMN_CONTEXT"
DQ_RULES_TABLE = "METADATA_DQ_RULES"
COLUMN_CLASSIFICATION_TABLE = "METADATA_COLUMN_CLASSIFICATION"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE_TABLE"
PIPELINE_RUNS_TABLE = "METADATA_PIPELINE_RUNS"
SUCCESS_STATUSES = {"success", "succeeded", "passed", "complete", "completed", "ok"}
DQ_RULE_TYPES = ["not_null", "unique_key", "accepted_values", "value_range", "regex_format", "datatype", "referential_integrity", "custom_expression"]
DQ_RULE_TYPE_ALIASES = {"unique": "unique_key", "regex": "regex_format"}
SENSITIVITY_LABELS = ["public", "internal", "confidential", "restricted"]
PERSONAL_DATA_CLASSIFICATIONS = ["not_personal_data", "direct_identifier", "indirect_identifier", "sensitive_personal_data", "unknown"]
BUSINESS_CONTEXT_PROMPT = DEFAULT_BUSINESS_CONTEXT_PROMPT_TEMPLATE
PDPA_PERSONAL_IDENTIFIER_PROMPT = DEFAULT_GOVERNANCE_PERSONAL_IDENTIFIER_PROMPT_TEMPLATE
AI_SUGGESTABLE_DQ_RULE_TYPES = {"not_null", "unique_key", "accepted_values", "value_range", "regex_format"}


@dataclass
class DQEnforcementResult:
    """Structured DQ enforcement outputs produced by internal DQ helpers."""

    rules: list[dict[str, Any]]
    rule_results: Any
    valid_rows: Any
    quarantine_rows: Any
    failure_rows: Any

_SELECTED_CATALOGUE_TABLE: dict[str, Any] | None = None


def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
    if rows_or_df is None:
        return []
    if hasattr(rows_or_df, "collect"):
        rows_or_df = rows_or_df.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]


def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
    return row.get(name, row.get(name.upper(), default))


def _is_success(row: dict[str, Any]) -> bool:
    return str(_value(row, "profile_status", "")).strip().lower() in SUCCESS_STATUSES


def _canonical_dq_rule_type(rule_type: Any) -> str:
    return DQ_RULE_TYPE_ALIASES.get(str(rule_type or "").strip(), str(rule_type or "").strip())


def _approved_review_context(profile_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> tuple[dict[str, dict[str, Any]], str, str, dict[str, Any]]:
    actor = _resolve_action_by(approved_by)
    audit = _build_runtime_audit_fields(config=config, env=env or "", committed_by=actor) if config is not None and env is not None else {}
    return {str(_value(r, "column_name")): r for r in profile_rows}, actor, _now_utc_iso(), audit


def _approved_column_identity(profile_row: dict[str, Any], review_row: dict[str, Any], *, env: str | None = None) -> dict[str, str]:
    col = str(review_row.get("column_name") or _value(profile_row, "column_name") or ((review_row.get("columns") or [""])[0]))
    env_name = str(_value(profile_row, "environment_name") or review_row.get("environment_name") or env or "")
    dataset = str(_value(profile_row, "dataset_name") or review_row.get("dataset_name") or "")
    table = str(_value(profile_row, "table_name") or review_row.get("table_name") or "")
    return {
        "metadata_column_key": str(_value(profile_row, "metadata_column_key") or review_row.get("metadata_column_key") or _build_metadata_column_key(env_name, dataset, table, col)),
        "metadata_table_key": str(_value(profile_row, "metadata_table_key") or review_row.get("metadata_table_key") or _build_metadata_table_key(env_name, dataset, table)),
        "environment_name": env_name,
        "dataset_name": dataset,
        "table_name": table,
        "column_name": col,
    }


def _spark_types():
    """Return Spark SQL type classes lazily so package import stays lightweight."""
    try:
        from pyspark.sql.types import BooleanType, DoubleType, LongType, StringType, StructField, StructType, TimestampType
    except Exception as exc:  # pragma: no cover - Fabric/runtime dependency guard
        raise RuntimeError("governance metadata schemas require pyspark.sql.types in the active runtime.") from exc
    return BooleanType, DoubleType, LongType, StringType, StructField, StructType, TimestampType


def _schema(fields: list[tuple[str, Any]]):
    _, _, _, _, StructField, StructType, _ = _spark_types()
    return StructType([StructField(name, data_type, True) for name, data_type in fields])


def _schema_field_names(schema: Any) -> list[str]:
    if hasattr(schema, "fieldNames"):
        return list(schema.fieldNames())
    return [field.name for field in getattr(schema, "fields", [])]


def _get_governance_metadata_schemas() -> dict[str, Any]:
    """Return typed Spark schemas prepared by ``00_env_config`` for governance.

    Returns
    -------
    dict[str, pyspark.sql.types.StructType]
        Physical metadata table names mapped to explicit nullable Spark schemas.

    Notes
    -----
    The bootstrap creates empty Delta tables with these explicit schemas instead
    of inferring all columns from empty strings. It does not seed data,
    duplicate pipeline configuration, or create a data-contract table.
    """
    BooleanType, DoubleType, LongType, StringType, _, _, TimestampType = _spark_types()
    string = StringType()
    long = LongType()
    double = DoubleType()
    boolean = BooleanType()
    timestamp = TimestampType()
    audit = [("_committed_at", string), ("_committed_by", string), ("_workspace_name", string), ("_notebook_name", string), ("_metadata_lakehouse_name", string), ("_activity_id", string)]
    catalogue = [
        ("metadata_table_key", string), ("metadata_column_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string),
        ("layer", string), ("asset_kind", string), ("pipeline_name", string), ("profile_run_id", string), ("profile_stage", string), ("profile_status", string), ("baseline_status", string),
        ("source_data_change_check", string), ("profile_baseline_mode", string), ("data_type", string), ("row_count", long), ("null_count", long), ("distinct_count", long),
        ("distribution_type", string), ("distribution_json", string), ("profiled_at", string), ("null_percent", double), ("distinct_percent", double), ("min_value", string), ("max_value", string),
        ("agreement_id", string), ("contract_version", string),
        ("DQ_STATUS", string), ("DQ_RULE_COUNT", long), ("DQ_FAILED_RULE_COUNT", long), ("DQ_WARNING_RULE_COUNT", long), ("DQ_ERROR_RULE_COUNT", long), ("DQ_FAILED_ROW_COUNT", long), ("DQ_FAILED_ROW_PERCENT", double), ("DQ_CHECKED_AT", string),
        ("TABLE_NAME", string), ("RUN_TIMESTAMP", timestamp), ("COLUMN_NAME", string), ("DATA_TYPE", string), ("ROW_COUNT", long), ("NULL_COUNT", long), ("NULL_PERCENT", double), ("DISTINCT_COUNT", long), ("DISTINCT_PERCENT", double), ("MIN_VALUE", string), ("MAX_VALUE", string), ("DISTRIBUTION_TYPE", string), ("DISTRIBUTION_JSON", string),
        ("AGREEMENT_ID", string), ("AGREEMENT_CONTRACT_VERSION", string), ("NOTEBOOK_REGISTRY_ID", string), ("NOTEBOOK_ID", string), ("PROFILE_RUN_ID", string), ("ENVIRONMENT_NAME", string), ("DATASET_NAME", string), ("PIPELINE_NAME", string), ("EVIDENCE_ROLE", string), ("PROFILE_STAGE", string), ("PROFILE_STATUS", string), ("BASELINE_STATUS", string), ("SOURCE_SCHEMA_CHECK", string), ("TARGET_SCHEMA_CHECK", string), ("SOURCE_DATA_CHANGE_CHECK", string), ("TARGET_DATA_CHANGE_CHECK", string), ("SOURCE_CHANGE_SIGNAL_JSON", string), ("LAYER", string), ("ASSET_KIND", string), ("PROFILED_TABLE_NAME", string), ("PROFILED_ROW_COUNT", long),
        *audit,
    ]
    return {
        CATALOGUE_TABLE: _schema(catalogue),
        COLUMN_CONTEXT_TABLE: _schema([("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("business_context", string), ("notes", string), ("review_status", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), *audit]),
        DQ_RULES_TABLE: _schema([("rule_key", string), ("rule_id", string), ("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("rule_type", string), ("rule_parameters_json", string), ("severity", string), ("description", string), ("is_active", boolean), ("review_status", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), ("action_type", string), *audit]),
        COLUMN_CLASSIFICATION_TABLE: _schema([("metadata_column_key", string), ("metadata_table_key", string), ("environment_name", string), ("dataset_name", string), ("table_name", string), ("column_name", string), ("sensitivity_label", string), ("personal_data_classification", string), ("pii_identifier_type", string), ("handling_requirement", string), ("reasoning", string), ("review_status", string), ("approved_by", string), ("approved_at", string), ("ai_suggestion_json", string), *audit]),
        LINEAGE_TABLE: _schema([("lineage_id", string), ("dataset_name", string), ("run_id", string), ("source_table", string), ("target_table", string), ("source_table_key", string), ("target_table_key", string), ("transformation_steps_json", string), ("created_at", string), *audit]),
        PIPELINE_RUNS_TABLE: _schema([("run_id", string), ("agreement_id", string), ("agreement_contract_version", string), ("notebook_registry_id", string), ("notebook_id", string), ("notebook_type", string), ("pipeline_name", string), ("environment_name", string), ("started_at", string), ("completed_at", string), ("status", string), ("source_count", long), ("target_count", long), ("source_guardrail_status", string), ("target_guardrail_status", string), ("dq_status", string), ("lineage_status", string), ("catalogue_status", string), ("message", string), ("run_summary_json", string), ("created_at", string)]),
    }


def _is_table_not_found_error(exc: Exception) -> bool:
    """Return whether a Spark/read exception clearly means the table is absent."""
    error_class_getter = getattr(exc, "getErrorClass", None)
    try:
        error_class = str(error_class_getter() or "") if callable(error_class_getter) else ""
    except Exception:
        error_class = ""
    if error_class.upper() in {"PATH_NOT_FOUND", "TABLE_OR_VIEW_NOT_FOUND", "DELTA_TABLE_NOT_FOUND"}:
        return True
    message = str(exc).lower()
    not_found_markers = (
        "path does not exist",
        "path_not_found",
        "table_or_view_not_found",
        "table not found",
        "no such file or directory",
        "doesn't exist",
        "does not exist",
    )
    non_not_found_markers = ("permission", "access denied", "unauthorized", "forbidden", "authentication", "credential", "malformed", "invalid configuration")
    return any(marker in message for marker in not_found_markers) and not any(marker in message for marker in non_not_found_markers)


def _setup_governance_metadata_tables(*, spark: Any, config: Any, env: str) -> dict[str, Any]:
    """Create or validate governance metadata tables via the configured route.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Spark session used to create empty metadata tables when missing.
    config : FrameworkConfig or dict
        ``00_env_config`` configuration that contains the ``metadata`` target.
    env : str
        Environment key to prepare.

    Returns
    -------
    dict[str, Any]
        Setup status, checked tables, and newly created tables.
    """
    created: list[str] = []
    schemas = _get_governance_metadata_schemas()
    for table_name, schema in schemas.items():
        try:
            table = read_lakehouse_table(config, env, "metadata", table_name, spark_session=spark)
        except Exception as exc:
            if not _is_table_not_found_error(exc):
                raise RuntimeError(f"Unable to read governance metadata table {table_name!r}; not attempting creation because the error was not a confirmed table-not-found condition.") from exc
            empty_df = spark.createDataFrame([], schema=schema)
            write_lakehouse_table(empty_df, config, env, "metadata", table_name, mode="ignore", overwrite_schema=True)
            table = read_lakehouse_table(config, env, "metadata", table_name, spark_session=spark)
            created.append(table_name)
        columns = list(getattr(table, "columns", [])) or (list(_coerce_rows(table)[0]) if _coerce_rows(table) else [])
        fields = _schema_field_names(schema)
        missing = [field for field in fields if field not in columns]
        if missing:
            raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}. Migrate the table before running 03_review.")
    return {"status": "ready", "tables": list(schemas), "created_tables": created}


def _catalogue_table_options(catalogue_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return one option per logical table using its latest successful profile.

    Parameters
    ----------
    catalogue_rows : iterable of dict
        Rows from ``METADATA_DATA_CATALOGUE``.

    Returns
    -------
    list[dict[str, Any]]
        Stable table selections sorted by display label.

    Raises
    ------
    ValueError
        If there are no catalogue rows or no successful profile rows.
    """
    rows = [dict(r) for r in catalogue_rows or []]
    if not rows:
        raise ValueError("METADATA_DATA_CATALOGUE has no rows. Run 02_pipeline profiling before 03_review.")
    successes = [r for r in rows if _is_success(r)]
    if not successes:
        raise ValueError("METADATA_DATA_CATALOGUE has no successful profile evidence for governance review.")
    latest: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in successes:
        env = str(_value(row, "environment_name"))
        dataset = str(_value(row, "dataset_name"))
        table = str(_value(row, "table_name"))
        key = (env, dataset, table)
        current = latest.get(key)
        sort_key = (str(_value(row, "profiled_at")), str(_value(row, "profile_run_id")), str(_value(row, "profile_stage")))
        if current is None or sort_key > current["_sort_key"]:
            latest[key] = {"row": row, "_sort_key": sort_key}
    options = []
    for (env, dataset, table), item in latest.items():
        row = item["row"]
        table_key = str(_value(row, "metadata_table_key") or _build_metadata_table_key(env, dataset, table))
        profile_run_id = str(_value(row, "profile_run_id"))
        profile_stage = str(_value(row, "profile_stage"))
        layer = str(_value(row, "layer"))
        asset_kind = str(_value(row, "asset_kind"))
        label = f"{env} / {dataset} / {layer or '-'} / {asset_kind or '-'} / {table} / {profile_stage or '-'} / {profile_run_id}"
        options.append({
            "label": label,
            "value": json.dumps({"environment_name": env, "dataset_name": dataset, "table_name": table, "metadata_table_key": table_key, "profile_run_id": profile_run_id, "profile_stage": profile_stage, "layer": layer, "asset_kind": asset_kind, "profiled_at": str(_value(row, "profiled_at"))}, sort_keys=True),
            "environment_name": env, "dataset_name": dataset, "table_name": table, "metadata_table_key": table_key,
            "profile_run_id": profile_run_id, "profile_stage": profile_stage, "layer": layer, "asset_kind": asset_kind, "profiled_at": str(_value(row, "profiled_at")),
        })
    return sorted(options, key=lambda r: r["label"])


def get_selected_catalogue_table(table_selector: Any | None = None) -> dict[str, Any]:
    """Return the catalogue table selected by ``widget_select_catalogue_table``.

    Parameters
    ----------
    table_selector : ipywidgets.Combobox, optional
        Selector returned by ``widget_select_catalogue_table``. Passing it is
        optional because the widget also maintains module-level selection state.

    Returns
    -------
    dict[str, Any]
        Stable table identity used by ``load_catalogue_profile_rows``.
    """
    if _SELECTED_CATALOGUE_TABLE is not None:
        return dict(_SELECTED_CATALOGUE_TABLE)
    raw_value = getattr(table_selector, "value", None) if table_selector is not None else None
    if raw_value:
        try:
            parsed = json.loads(str(raw_value))
            if isinstance(parsed, dict):
                return dict(parsed)
        except json.JSONDecodeError:
            pass
    raise ValueError("No catalogue table has been selected. Run widget_select_catalogue_table first.")


def widget_select_catalogue_table(config: Any, env: str, *, spark_session: Any):
    """Render a searchable selector for latest successful catalogue tables.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Runtime config containing the metadata lakehouse route.
    env : str
        Environment used to read ``METADATA_DATA_CATALOGUE``.
    spark_session : pyspark.sql.SparkSession
        Spark session used for the catalogue read.

    Returns
    -------
    ipywidgets.Combobox
        Searchable selector whose value stores stable JSON identity.
    """
    global _SELECTED_CATALOGUE_TABLE
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    rows = _coerce_rows(read_lakehouse_table(config, env, "metadata", CATALOGUE_TABLE, spark_session=spark_session))
    options = _catalogue_table_options(rows)
    by_label = {o["label"]: o for o in options}
    combo = widgets.Combobox(placeholder="Search profiled tables", options=[o["label"] for o in options], description="Table", ensure_option=True, layout=widgets.Layout(width="980px"))
    context = widgets.HTML()

    def select(label: str) -> None:
        global _SELECTED_CATALOGUE_TABLE
        option = by_label.get(label) or options[0]
        _SELECTED_CATALOGUE_TABLE = {k: option[k] for k in ["environment_name", "dataset_name", "table_name", "metadata_table_key", "profile_run_id", "profile_stage", "layer", "asset_kind", "profiled_at"]}
        context.value = f"<b>Selected table:</b> {_SELECTED_CATALOGUE_TABLE['environment_name']} / {_SELECTED_CATALOGUE_TABLE['dataset_name']} / {_SELECTED_CATALOGUE_TABLE['table_name']}<br/><b>Profile run:</b> {_SELECTED_CATALOGUE_TABLE['profile_run_id']} ({_SELECTED_CATALOGUE_TABLE['profile_stage']})"

    def on_change(change: dict[str, Any]) -> None:
        if change.get("name") == "value" and change.get("new") in by_label:
            select(change["new"])

    combo.observe(on_change, names="value")
    combo.value = options[0]["label"]
    select(combo.value)
    ip.display(widgets.VBox([combo, context]))
    return combo


def load_catalogue_profile_rows(config: Any, env: str, selection: dict[str, Any], *, spark_session: Any) -> list[dict[str, Any]]:
    """Load column rows for the selected latest successful profile run."""
    rows = _coerce_rows(read_lakehouse_table(config, env, "metadata", CATALOGUE_TABLE, spark_session=spark_session))
    filtered = []
    for row in rows:
        table_key = str(
            _value(row, "metadata_table_key")
            or _build_metadata_table_key(
                _value(row, "environment_name"),
                _value(row, "dataset_name"),
                _value(row, "table_name"),
            )
        )
        if (
            _is_success(row)
            and str(_value(row, "environment_name")) == str(selection["environment_name"])
            and str(_value(row, "dataset_name")) == str(selection["dataset_name"])
            and str(_value(row, "table_name")) == str(selection["table_name"])
            and str(_value(row, "profile_run_id")) == str(selection["profile_run_id"])
            and str(_value(row, "profile_stage")) == str(selection["profile_stage"])
            and table_key == str(selection["metadata_table_key"])
        ):
            filtered.append(row)
    if not filtered:
        raise ValueError("The selected successful profile has no column rows in METADATA_DATA_CATALOGUE.")
    return filtered


def _build_column_context_records(profile_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
    """Build append-only approved business-context records from explicit reviews."""
    profile, actor, now, audit = _approved_review_context(profile_rows, config=config, env=env, approved_by=approved_by)
    rows = []
    for review in reviewed_rows or []:
        if str(review.get("review_status", "approved")).lower() != "approved" or not review.get("commit"):
            continue
        identity = _approved_column_identity(profile.get(str(review.get("column_name")), {}), review, env=env)
        rows.append({
            **identity,
            "business_context": str(review.get("business_context") or ""), "notes": str(review.get("notes") or ""), "review_status": "approved",
            "approved_by": actor, "approved_at": now, "ai_suggestion_json": _json(review.get("ai_suggestion_json") or review.get("ai_suggestion")), **audit,
        })
    return rows


def _build_dq_rule_records(profile_rows: list[dict[str, Any]], reviewed_rules: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
    """Build append-only approved DQ-rule records without enforcing them."""
    profile, actor, now, audit = _approved_review_context(profile_rows, config=config, env=env, approved_by=approved_by)
    rows = []
    for rule in reviewed_rules or []:
        if str(rule.get("review_status", "approved")).lower() != "approved" or not rule.get("commit"):
            continue
        rule_type = _canonical_dq_rule_type(rule.get("rule_type"))
        if rule_type not in DQ_RULE_TYPES:
            raise ValueError(f"Unsupported rule_type: {rule_type}")
        identity = _approved_column_identity(profile.get(str(rule.get("column_name") or (rule.get("columns") or [""])[0]), {}), rule, env=env)
        rule_id = str(rule.get("rule_id") or f"{identity['table_name']}.{identity['column_name']}.{rule_type}")
        rows.append({
            "rule_key": _build_dq_rule_key(identity["environment_name"], identity["dataset_name"], identity["table_name"], rule_id), "rule_id": rule_id,
            **identity,
            "rule_type": rule_type, "rule_parameters_json": _json(rule.get("rule_parameters") or rule.get("rule_parameters_json") or {}),
            "severity": str(rule.get("severity") or "warning"), "description": str(rule.get("description") or ""), "is_active": bool(rule.get("is_active", True)),
            "review_status": "approved", "approved_by": actor, "approved_at": now, "ai_suggestion_json": _json(rule.get("ai_suggestion_json") or rule.get("ai_suggestion")), "action_type": "approved", **audit,
        })
    return rows


def _build_classification_records(profile_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
    """Build append-only approved sensitivity and PII classification records."""
    profile, actor, now, audit = _approved_review_context(profile_rows, config=config, env=env, approved_by=approved_by)
    rows = []
    for review in reviewed_rows or []:
        if str(review.get("review_status", "approved")).lower() != "approved" or not review.get("commit"):
            continue
        sensitivity = str(review.get("sensitivity_label") or "internal")
        classification = str(review.get("personal_data_classification") or "unknown")
        if sensitivity not in SENSITIVITY_LABELS:
            raise ValueError(f"Unsupported sensitivity_label: {sensitivity}")
        if classification not in PERSONAL_DATA_CLASSIFICATIONS:
            raise ValueError(f"Unsupported personal_data_classification: {classification}")
        identity = _approved_column_identity(profile.get(str(review.get("column_name")), {}), review, env=env)
        rows.append({
            **identity,
            "sensitivity_label": sensitivity, "personal_data_classification": classification,
            "pii_identifier_type": str(review.get("pii_identifier_type") or ""), "handling_requirement": str(review.get("handling_requirement") or ""),
            "reasoning": str(review.get("reasoning") or ""), "review_status": "approved", "approved_by": actor, "approved_at": now,
            "ai_suggestion_json": _json(review.get("ai_suggestion_json") or review.get("ai_suggestion")), **audit,
        })
    return rows

def _json(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)


def _display_review_guidance(title: str, profile_rows: list[dict[str, Any]], instructions: str) -> list[dict[str, Any]]:
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    columns = [str(_value(row, "column_name")) for row in profile_rows]
    html = widgets.HTML(
        f"<h3>{title}</h3>"
        f"<p>{instructions}</p>"
        f"<p><b>Columns loaded:</b> {', '.join(columns)}</p>"
        "<p>Return value is an editable list scaffold. Add reviewed dictionaries, set "
        "<code>review_status='approved'</code> and <code>commit=True</code>, then pass the list to "
        "<code>record_table_governance</code>.</p>"
    )
    ip.display(html)
    return []


def widget_review_column_context(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Render standalone business-context review guidance for ``03_review``.

    Parameters
    ----------
    profile_rows : list of dict
        Selected column profile evidence from ``load_catalogue_profile_rows``.

    Returns
    -------
    list[dict[str, Any]]
        Empty editable review list. Add approved context rows before calling
        ``record_table_governance``.
    """
    return _display_review_guidance(
        "Business context review",
        profile_rows,
        "Describe human-approved business meaning for each column. AI suggestions, if used, are advisory only.",
    )


def widget_review_dq_rules(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Render standalone DQ-rule review guidance for ``03_review``.

    Parameters
    ----------
    profile_rows : list of dict
        Selected column profile evidence from ``load_catalogue_profile_rows``.

    Returns
    -------
    list[dict[str, Any]]
        Empty editable review list. Add approved rule dictionaries before
        calling ``record_table_governance``.
    """
    return _display_review_guidance(
        "DQ rule review",
        profile_rows,
        "Author human-approved DQ rules for selected columns. These records are governance evidence and are not automatically enforced by 02_pipeline.",
    )


def widget_review_column_classification(profile_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Render standalone sensitivity and PII classification review guidance.

    Parameters
    ----------
    profile_rows : list of dict
        Selected column profile evidence from ``load_catalogue_profile_rows``.

    Returns
    -------
    list[dict[str, Any]]
        Empty editable review list. Add approved classification dictionaries
        before calling ``record_table_governance``.
    """
    return _display_review_guidance(
        "Sensitivity and PII classification review",
        profile_rows,
        "Review sensitivity labels, personal-data classifications, identifier types, and handling requirements.",
    )


def record_table_governance(
    config: Any,
    env: str,
    profile_rows: list[dict[str, Any]],
    *,
    spark_session: Any,
    context_reviews: list[dict[str, Any]] | None = None,
    dq_rule_reviews: list[dict[str, Any]] | None = None,
    classification_reviews: list[dict[str, Any]] | None = None,
    approved_by: str | None = None,
    mode: str = "append",
) -> dict[str, list[dict[str, Any]]]:
    """Persist approved table-governance review evidence.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration that routes metadata writes to
        the configured metadata lakehouse target.
    env : str
        Environment key in ``config``.
    profile_rows : list of dict
        Column-profile rows loaded for the selected catalogue table.
    spark_session : pyspark.sql.SparkSession
        Spark session used to create DataFrames for metadata writes.
    context_reviews, dq_rule_reviews, classification_reviews : list of dict, optional
        Human-approved rows from the governance review workflow. Only rows with
        ``review_status="approved"`` and ``commit=True`` are written.
    approved_by : str, optional
        Reviewer identity to stamp on records. When omitted, runtime defaults
        are used.
    mode : str, default "append"
        Write mode for metadata table commits.

    Returns
    -------
    dict[str, list[dict[str, Any]]]
        Records written for ``column_context``, ``dq_rules``, and
        ``column_classification``.

    Notes
    -----
    This is the v1 governance commit action for ``03_review`` notebooks. It merges
    the previous row-builder and per-table commit helpers into one explicit
    human approval step while preserving configured metadata lakehouse routing.
    """
    context_records = _build_column_context_records(
        profile_rows,
        context_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    dq_rule_records = _build_dq_rule_records(
        profile_rows,
        dq_rule_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    classification_records = _build_classification_records(
        profile_rows,
        classification_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    writes = {
        COLUMN_CONTEXT_TABLE: context_records,
        DQ_RULES_TABLE: dq_rule_records,
        COLUMN_CLASSIFICATION_TABLE: classification_records,
    }
    for table_name, records in writes.items():
        if records:
            write_lakehouse_table(spark_session.createDataFrame(records), config, env, "metadata", table_name, mode=mode)

    return {
        "column_context": context_records,
        "dq_rules": dq_rule_records,
        "column_classification": classification_records,
    }


def _spark_sql_helpers():
    """Return Spark SQL helper modules lazily for DQ runtime helpers."""
    try:
        from pyspark.sql import SparkSession, functions as F
        from pyspark.sql.window import Window
    except Exception as exc:  # pragma: no cover - Fabric/runtime dependency guard
        raise RuntimeError("DQ enforcement helpers require pyspark in the active runtime.") from exc
    return SparkSession, F, Window


def _run_fabric_ai_drafting(prepared_profile_df, *, prompt: str, output_col: str):
    """Run Fabric AI prompt drafting against prepared profile rows."""
    ai = getattr(prepared_profile_df, "ai", None)
    if ai is None or not hasattr(ai, "generate_response"):
        raise RuntimeError("AI drafting requires Fabric DataFrame.ai.generate_response.")
    return prepared_profile_df.ai.generate_response(prompt=prompt, is_prompt_template=True, output_col=output_col)


def _draft_business_context(prepared_profile_df, prompt_template: str = BUSINESS_CONTEXT_PROMPT, output_col: str = "ai_business_context_response"):
    """Draft column business-context suggestions with Fabric AI."""
    return _run_fabric_ai_drafting(prepared_profile_df, prompt=prompt_template, output_col=output_col)


def _draft_governance(prepared_profile_df, prompt: str | None = None, output_col: str = "ai_governance_response"):
    """Draft sensitivity and PII classification suggestions with Fabric AI."""
    return _run_fabric_ai_drafting(prepared_profile_df, prompt=prompt or PDPA_PERSONAL_IDENTIFIER_PROMPT, output_col=output_col)


def _parse_ai_dict_response(text: str) -> dict[str, Any]:
    """Parse JSON/Python-dict AI response text into a dictionary."""
    cleaned = str(text or "").strip()
    match = re.search(r"^[A-Z_]+\s*=\s*(\{.*\})\s*$", cleaned, flags=re.DOTALL)
    if match:
        cleaned = match.group(1)
    if not cleaned:
        return {}
    for loader in (json.loads, ast.literal_eval):
        try:
            obj = loader(cleaned)
        except Exception:
            continue
        if isinstance(obj, dict):
            return obj
    return {}


def _extract_assignment_payload(response_rows, *, response_col: str, assignment_key: str | None = None, table_name: str | None = None) -> list[dict[str, Any]]:
    """Extract dictionary payloads from AI response rows with optional table-key narrowing."""
    out: list[dict[str, Any]] = []
    for row in _coerce_rows(response_rows):
        parsed = _parse_ai_dict_response(row.get(response_col) or row.get("response") or row.get("ai_response") or "")
        if not parsed:
            continue
        payload = parsed.get(assignment_key, parsed) if assignment_key else parsed
        if table_name is not None:
            payload = payload.get(table_name, []) if isinstance(payload, dict) else []
        if isinstance(payload, list):
            out.extend(dict(item) for item in payload if isinstance(item, dict))
        elif isinstance(payload, dict):
            out.append(payload)
    return out


def _validate_dq_rules(rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Validate canonical DQ rules before loading or enforcement."""
    if not isinstance(rules, list):
        raise ValueError("DQ rules must be a list of dictionaries.")
    required = {"rule_id", "rule_type", "columns", "severity", "description"}
    for i, rule in enumerate(rules):
        if not isinstance(rule, dict):
            raise ValueError(f"DQ rule at index {i} must be a dictionary.")
        missing = required.difference(rule)
        if missing:
            raise ValueError(f"DQ rule '{rule.get('rule_id', i)}' is missing fields: {sorted(missing)}")
        rule["rule_type"] = _canonical_dq_rule_type(rule["rule_type"])
        if rule["rule_type"] not in AI_SUGGESTABLE_DQ_RULE_TYPES:
            raise ValueError(f"DQ rule '{rule['rule_id']}' has unsupported rule_type '{rule['rule_type']}'.")
        if str(rule["severity"]).lower() not in {"warning", "error"}:
            raise ValueError(f"DQ rule '{rule['rule_id']}' severity must be warning or error.")
        cols = rule.get("columns")
        if not isinstance(cols, list) or not cols:
            raise ValueError(f"DQ rule '{rule['rule_id']}' columns must be a non-empty list.")
        if rule["rule_type"] in {"not_null", "accepted_values", "value_range", "regex_format"} and len(cols) != 1:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires exactly one column.")
        if rule["rule_type"] == "accepted_values" and "allowed_values" not in rule:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires allowed_values.")
        if rule["rule_type"] == "value_range" and "lower_bound" not in rule and "upper_bound" not in rule:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires lower_bound or upper_bound.")
        if rule["rule_type"] == "regex_format" and "regex_pattern" not in rule:
            raise ValueError(f"DQ rule '{rule['rule_id']}' requires regex_pattern.")
    return rules


def _latest_dq_rule_versions(metadata_df, table_name: str, env_name: str | None = None, dataset_name: str | None = None):
    """Resolve latest DQ metadata rows using the current v1 metadata shape."""
    _, F, Window = _spark_sql_helpers()
    columns = set(getattr(metadata_df, "columns", []))
    partition_cols = [name for name in ("rule_key", "rule_id", "column_name", "rule_type") if name in columns]
    order_cols = [name for name in ("approved_at", "_committed_at", "action_type", "approved_by", "_committed_by") if name in columns]
    if not partition_cols:
        raise ValueError("DQ metadata must include rule_key or rule identity columns.")
    scoped = metadata_df.filter(F.col("table_name") == table_name) if "table_name" in columns else metadata_df
    if env_name is not None and "environment_name" in columns:
        scoped = scoped.filter(F.col("environment_name") == env_name)
    if dataset_name is not None and "dataset_name" in columns:
        scoped = scoped.filter(F.col("dataset_name") == dataset_name)
    if not order_cols:
        return scoped
    w = Window.partitionBy(*[F.col(name) for name in partition_cols]).orderBy(*[F.col(name).desc_nulls_last() for name in order_cols])
    return scoped.withColumn("_rn", F.row_number().over(w)).filter(F.col("_rn") == 1).drop("_rn")


def _load_active_dq_rules(metadata_df, table_name: str, env_name: str | None = None, dataset_name: str | None = None) -> list[dict[str, Any]]:
    """Load active DQ rules from current v1 metadata rows."""
    _, F, _ = _spark_sql_helpers()
    columns = set(getattr(metadata_df, "columns", []))
    latest = _latest_dq_rule_versions(metadata_df, table_name, env_name=env_name, dataset_name=dataset_name)
    if "is_active" in columns:
        latest = latest.filter(F.col("is_active") == True)
    if "action_type" in columns:
        latest = latest.filter(F.lower(F.coalesce(F.col("action_type"), F.lit("approved"))) != "deactivated")
    if "review_status" in columns:
        latest = latest.filter(F.lower(F.coalesce(F.col("review_status"), F.lit("approved"))) == "approved")

    rules: list[dict[str, Any]] = []
    for row in _coerce_rows(latest.collect()):
        params_raw = row.get("rule_parameters_json") or "{}"
        try:
            params = json.loads(params_raw) if isinstance(params_raw, str) else dict(params_raw)
        except Exception:
            params = {}
        columns_value = params.pop("columns", None) or row.get("columns") or row.get("column_name")
        if isinstance(columns_value, str):
            rule_columns = [c.strip() for c in columns_value.split(",") if c.strip()]
        else:
            rule_columns = list(columns_value or [])
        rules.append(
            {
                "rule_id": str(row.get("rule_id") or ""),
                "rule_type": _canonical_dq_rule_type(row.get("rule_type")),
                "columns": rule_columns,
                "severity": str(row.get("severity") or "warning"),
                "description": str(row.get("description") or ""),
                **params,
            }
        )
    return _validate_dq_rules(rules)


def _dq_failed_expression(df, rule: dict[str, Any]):
    """Build a Spark boolean expression identifying rows that fail one DQ rule."""
    _, F, Window = _spark_sql_helpers()
    rtype = str(rule["rule_type"])
    cols = [str(column) for column in rule.get("columns", [])]
    missing_columns = [column for column in cols if column not in set(getattr(df, "columns", []))]
    if missing_columns:
        return F.lit(True)
    col_name = cols[0] if cols else None
    if rtype == "not_null":
        failed = F.col(col_name).isNull() | (F.trim(F.col(col_name).cast("string")) == "")
    elif rtype == "unique_key":
        failed = F.count(F.lit(1)).over(Window.partitionBy(*[F.col(c) for c in cols])) > F.lit(1)
    elif rtype == "accepted_values":
        failed = F.col(col_name).isNotNull() & ~F.col(col_name).isin(rule["allowed_values"])
    elif rtype == "value_range":
        cond = F.lit(False)
        if rule.get("lower_bound") is not None:
            cond = cond | (F.col(col_name).cast("double") < F.lit(float(rule["lower_bound"])))
        if rule.get("upper_bound") is not None:
            cond = cond | (F.col(col_name).cast("double") > F.lit(float(rule["upper_bound"])))
        failed = F.col(col_name).isNotNull() & cond
    elif rtype == "regex_format":
        failed = F.col(col_name).isNotNull() & ~F.col(col_name).rlike(rule["regex_pattern"])
    else:
        failed = F.lit(False)
    return F.coalesce(failed, F.lit(False))


def _dq_check_status(severity: str, failed_count: int) -> str:
    if failed_count <= 0:
        return "passed"
    return "failed" if str(severity).strip().lower() == "error" else "warning"


def _run_dq_guardrail_checks(df, table_name: str, rules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Run DQ rules and return notebook guardrail check dictionaries."""
    _, F, _ = _spark_sql_helpers()
    _validate_dq_rules(rules)
    total = int(df.count())
    checks: list[dict[str, Any]] = []
    dataframe_columns = set(getattr(df, "columns", []))
    for rule in rules:
        failed_rows = df.select(
            F.when(_dq_failed_expression(df, rule), F.lit(1)).otherwise(F.lit(0)).alias("failed")
        )
        failed_count = int(
            failed_rows.agg(F.sum("failed").alias("failed_count")).collect()[0]["failed_count"] or 0
        )
        severity = str(rule.get("severity", "warning")).strip().lower()
        columns = [str(column) for column in rule.get("columns", [])]
        check_status = _dq_check_status(severity, failed_count)
        check = {
            "check": "dq_rule",
            "table_name": table_name,
            "rule_id": str(rule.get("rule_id") or ""),
            "rule_type": str(rule.get("rule_type") or ""),
            "columns": columns,
            "severity": severity,
            "status": check_status,
            "passed": failed_count == 0,
            "failed_count": failed_count,
            "total_count": total,
            "failed_percent": float(round((failed_count / total) * 100, 4)) if total else 0.0,
            "description": str(rule.get("description") or ""),
        }
        missing_columns = [column for column in columns if column not in dataframe_columns]
        if missing_columns:
            check["missing_columns"] = missing_columns
        checks.append(check)
    return checks


def _dq_tagged_dataframe(df, rules: list[dict[str, Any]]):
    """Return the full DataFrame tagged with warning-rule DQ columns."""
    _, F, _ = _spark_sql_helpers()
    warning_rules = sorted(
        (rule for rule in rules if str(rule.get("severity", "warning")).strip().lower() == "warning"),
        key=lambda rule: str(rule.get("rule_id") or ""),
    )
    failed_rule_columns = [
        F.when(_dq_failed_expression(df, rule), F.lit(str(rule.get("rule_id") or "")))
        for rule in warning_rules
    ]
    failed_rules = F.concat_ws(",", *failed_rule_columns) if failed_rule_columns else F.lit("")
    return (
        df.withColumn("_dq_failed_rules", failed_rules)
        .withColumn(
            "_dq_check_status",
            F.when(F.col("_dq_failed_rules") == F.lit(""), F.lit("passed")).otherwise(F.lit("warning")),
        )
    )


def _dq_failed_row_count(df, rules: list[dict[str, Any]]) -> int:
    """Return the count of rows that failed at least one DQ rule."""
    _, F, _ = _spark_sql_helpers()
    if not rules:
        return 0
    failed_columns = [F.when(_dq_failed_expression(df, rule), F.lit(1)).otherwise(F.lit(0)) for rule in rules]
    failed_row = failed_columns[0]
    for column in failed_columns[1:]:
        failed_row = failed_row + column
    failed_rows = df.select(F.when(failed_row > F.lit(0), F.lit(1)).otherwise(F.lit(0)).alias("failed"))
    return int(failed_rows.agg(F.sum("failed").alias("failed_count")).collect()[0]["failed_count"] or 0)


def _dq_summary(checks: list[dict[str, Any]], total_count: int, failed_row_count: int) -> dict[str, Any]:
    """Build aggregate DQ fields for catalogue/profile evidence."""
    failed_checks = [check for check in checks if not bool(check.get("passed", False))]
    warning_checks = [check for check in failed_checks if check.get("severity") == "warning"]
    error_checks = [check for check in failed_checks if check.get("severity") == "error"]
    status = _summarize_dq_guardrail(checks)["status"]
    return {
        "DQ_STATUS": status,
        "DQ_RULE_COUNT": len(checks),
        "DQ_FAILED_RULE_COUNT": len(failed_checks),
        "DQ_WARNING_RULE_COUNT": len(warning_checks),
        "DQ_ERROR_RULE_COUNT": len(error_checks),
        "DQ_FAILED_ROW_COUNT": failed_row_count,
        "DQ_FAILED_ROW_PERCENT": float(round((failed_row_count / total_count) * 100, 4)) if total_count else 0.0,
        "DQ_CHECKED_AT": datetime.now(timezone.utc).isoformat(),
    }


def _summarize_dq_guardrail(checks: list[dict[str, Any]]) -> dict[str, Any]:
    if any(check.get("status") == "failed" for check in checks):
        status = "failed"
        can_continue = False
    elif any(check.get("status") == "warning" for check in checks):
        status = "warning"
        can_continue = True
    else:
        status = "passed"
        can_continue = True
    failed_checks = [check for check in checks if check.get("status") in {"warning", "failed"}]
    if not checks:
        message = "No active approved DQ rules found."
    elif failed_checks:
        message = f"DQ guardrail found {len(failed_checks)} rule failure(s): {status}."
    else:
        message = f"DQ guardrail passed {len(checks)} active approved rule(s)."
    return {"status": status, "can_continue": can_continue, "checks": checks, "message": message}


def enforce_dq_rules(
    dataframe,
    config,
    env,
    dataset_name,
    table_name,
    *,
    spark_session=None,
) -> dict:
    """Enforce active approved DQ rules as a simple pipeline guardrail.

    Parameters
    ----------
    dataframe : Any
        Spark DataFrame to evaluate before the target write. The full DataFrame
        is never filtered or split by this helper.
    config : FrameworkConfig or dict
        Runtime configuration containing the configured metadata lakehouse
        route from ``00_env_config``.
    env : str
        Environment name used to read ``METADATA_DQ_RULES`` from the configured
        metadata target.
    dataset_name : str
        Dataset identifier used with ``table_name`` to scope approved DQ rules
        when those columns exist in the metadata table.
    table_name : str
        Target table name whose approved active DQ rules should be enforced.
    spark_session : pyspark.sql.SparkSession, optional
        Spark session used to read metadata when required by the configured
        storage helper.

    Returns
    -------
    dict
        Guardrail result with ``status``, ``can_continue``, ``checks``, and
        ``message``. The result also carries the full tagged ``dataframe`` and
        aggregate ``summary`` fields for the existing catalogue evidence path.
        Error-severity rule failures return ``status='failed'`` and
        ``can_continue=False``. Warning-severity failures return
        ``status='warning'`` and ``can_continue=True``. Passing or absent rules
        return ``status='passed'`` and ``can_continue=True``.

    Notes
    -----
    This v1 guardrail reads approved active rules from ``METADATA_DQ_RULES`` via
    the configured metadata route. It records aggregate rule outcomes only; it
    does not quarantine rows, write row-level failure metadata, filter invalid
    rows, send alerts, or partially write targets.
    """
    metadata_df = read_lakehouse_table(config, env, "metadata", DQ_RULES_TABLE, spark_session=spark_session)
    rules = _load_active_dq_rules(metadata_df, table_name=table_name, env_name=env, dataset_name=dataset_name)
    checks = _run_dq_guardrail_checks(dataframe, table_name=table_name, rules=rules) if rules else []
    total_count = int(dataframe.count())
    failed_row_count = _dq_failed_row_count(dataframe, rules) if rules else 0
    result = _summarize_dq_guardrail(checks)
    result["dataframe"] = _dq_tagged_dataframe(dataframe, rules)
    result["summary"] = _dq_summary(checks, total_count, failed_row_count)
    return result

def _split_dq_rows(df, rules: list[dict[str, Any]], dq_run_id: str | None = None, row_id_columns: list[str] | None = None):
    """Split source rows into valid rows, quarantine rows, and failure evidence."""
    _, F, Window = _spark_sql_helpers()
    _validate_dq_rules(rules)
    dq_run_id = dq_run_id or str(uuid.uuid4())
    run_ts = datetime.now(timezone.utc).isoformat()
    if row_id_columns:
        df_with_ids = df.withColumn("dq_row_id", F.sha2(F.concat_ws("||", *[F.coalesce(F.col(c).cast("string"), F.lit("<NULL>")) for c in row_id_columns]), 256))
    else:
        df_with_ids = df.withColumn("dq_row_id", F.sha2(F.concat_ws("||", *[F.coalesce(F.col(c).cast("string"), F.lit("<NULL>")) for c in df.columns], F.monotonically_increasing_id().cast("string")), 256))
    working = df_with_ids.withColumn("dq_run_id", F.lit(dq_run_id))
    failure_dfs = []
    for rule in rules:
        rid, rtype, cols = str(rule["rule_id"]), str(rule["rule_type"]), rule["columns"]
        col_name = cols[0] if cols else None
        if rtype == "not_null":
            failed = F.col(col_name).isNull() | (F.trim(F.col(col_name).cast("string")) == "")
        elif rtype == "unique_key":
            dup_col = f"__dq_duplicate_count_{rid}"
            working = working.withColumn(dup_col, F.count(F.lit(1)).over(Window.partitionBy(*[F.col(c) for c in cols])))
            failed = F.col(dup_col) > F.lit(1)
        elif rtype == "accepted_values":
            failed = F.col(col_name).isNotNull() & ~F.col(col_name).isin(rule["allowed_values"])
        elif rtype == "value_range":
            cond = F.lit(False)
            if rule.get("lower_bound") is not None:
                cond = cond | (F.col(col_name).cast("double") < F.lit(float(rule["lower_bound"])))
            if rule.get("upper_bound") is not None:
                cond = cond | (F.col(col_name).cast("double") > F.lit(float(rule["upper_bound"])))
            failed = F.col(col_name).isNotNull() & cond
        elif rtype == "regex_format":
            failed = F.col(col_name).isNotNull() & ~F.col(col_name).rlike(rule["regex_pattern"])
        else:
            continue
        failure_dfs.append(working.filter(F.coalesce(failed, F.lit(False))).select(F.col("dq_run_id"), F.col("dq_row_id"), F.lit(rid).alias("rule_id"), F.lit(rtype).alias("rule_type"), F.lit(",".join(cols)).alias("failed_columns"), F.lit(str(rule.get("severity", "warning"))).alias("severity"), F.lit(str(rule.get("description", ""))).alias("description"), F.lit(run_ts).alias("dq_failed_ts")))
        if rtype == "unique_key":
            working = working.drop(dup_col)
    if not failure_dfs:
        empty = df.sparkSession.createDataFrame([], "dq_run_id string, dq_row_id string, dq_quarantine_id string, rule_id string, rule_type string, failed_columns string, severity string, description string, dq_failed_ts string")
        return working, working.limit(0), empty
    failures = failure_dfs[0]
    for failure_df in failure_dfs[1:]:
        failures = failures.unionByName(failure_df)
    quarantine_ids = failures.select("dq_run_id", "dq_row_id").distinct().withColumn("dq_quarantine_id", F.sha2(F.concat_ws("||", F.col("dq_run_id"), F.col("dq_row_id")), 256))
    failures = failures.join(quarantine_ids, on=["dq_run_id", "dq_row_id"], how="left").select("dq_run_id", "dq_row_id", "dq_quarantine_id", "rule_id", "rule_type", "failed_columns", "severity", "description", "dq_failed_ts")
    quarantine_rows = working.join(quarantine_ids, on=["dq_run_id", "dq_row_id"], how="inner").withColumn("dq_quarantine_ts", F.lit(run_ts))
    valid_rows = working.join(quarantine_ids.select("dq_run_id", "dq_row_id"), on=["dq_run_id", "dq_row_id"], how="left_anti")
    return valid_rows, quarantine_rows, failures


def _run_dq_rules(df, table_name: str, rules: list[dict[str, Any]]):
    """Run DQ rules and return rule-level PASS/FAIL evidence."""
    _, F, _ = _spark_sql_helpers()
    _validate_dq_rules(rules)
    _, _, failures = _split_dq_rows(df, rules)
    total = df.count()
    failure_counts = {r["rule_id"]: int(r["failed_count"]) for r in failures.groupBy("rule_id").agg(F.count(F.lit(1)).alias("failed_count")).collect()}
    rows = []
    for rule in rules:
        failed_count = failure_counts.get(rule["rule_id"], 0)
        rows.append({"table_name": table_name, "rule_id": rule["rule_id"], "rule_type": rule["rule_type"], "columns": ",".join(rule["columns"]), "severity": str(rule["severity"]).lower(), "status": "PASS" if failed_count == 0 else "FAIL", "failed_count": int(failed_count), "total_count": int(total), "failed_percent": float(round((failed_count / total) * 100, 4)) if total else 0.0, "description": rule.get("description", ""), "run_timestamp": datetime.now(timezone.utc).isoformat()})
    return df.sparkSession.createDataFrame(rows)


def _prepare_dq_profile_input_rows(*, profile_df=None, df=None, table_name: str, business_context: str = ""):
    """Prepare DQ prompt profile rows from a profile DataFrame or raw DataFrame."""
    if (profile_df is None) == (df is None):
        raise ValueError("Provide exactly one of profile_df or df.")
    if profile_df is None:
        profile_df = profile_dataframe(df, table_name=table_name)
    cols = set(profile_df.columns)
    if {"column_name", "data_type", "row_count", "null_count", "distinct_count"}.issubset(cols):
        return profile_df
    _, F, _ = _spark_sql_helpers()
    return profile_df.select(
        F.col("TABLE_NAME").alias("table_name"),
        F.col("COLUMN_NAME").alias("column_name"),
        F.col("DATA_TYPE").alias("data_type"),
        F.col("ROW_COUNT").alias("row_count"),
        F.col("NULL_COUNT").alias("null_count"),
        F.col("NULL_PERCENT").alias("null_percent"),
        F.col("DISTINCT_COUNT").alias("distinct_count"),
        F.col("DISTINCT_PERCENT").alias("distinct_percent"),
        F.col("MIN_VALUE").alias("min_value"),
        F.col("MAX_VALUE").alias("max_value"),
        F.lit("").alias("observed_values_sample"),
        F.lit(business_context).alias("business_context"),
        F.lit(datetime.now(timezone.utc).isoformat()).alias("profile_timestamp"),
    )


def _draft_dq_rules(*, profile_df=None, df=None, table_name: str, business_context: str = "", prompt_template: str | None = None, output_col: str = "response") -> list[dict[str, Any]]:
    """Draft candidate DQ rules from metadata profiles or a raw DataFrame fallback."""
    prepared = _prepare_dq_profile_input_rows(profile_df=profile_df, df=df, table_name=table_name, business_context=business_context)
    responses = _run_fabric_ai_drafting(prepared, prompt=prompt_template or "", output_col=output_col)
    candidates = _extract_assignment_payload(responses, response_col=output_col, assignment_key="DQ_RULES", table_name=table_name)
    by_id = {r.get("rule_id"): {**r, "rule_type": _canonical_dq_rule_type(r.get("rule_type"))} for r in candidates if r.get("rule_id")}
    return list(by_id.values())


def _enforce_dq(df, *, table_name: str, rules=None, metadata_df=None, row_id_columns: list[str] | None = None, dq_run_id: str | None = None) -> DQEnforcementResult:
    """Enforce approved DQ rules and return structured deterministic outputs."""
    if rules is None and metadata_df is None:
        raise ValueError("Provide rules or metadata_df.")
    active_rules = rules or _load_active_dq_rules(metadata_df, table_name=table_name)
    _validate_dq_rules(active_rules)
    rule_results = _run_dq_rules(df, table_name=table_name, rules=active_rules)
    valid_rows, quarantine_rows, failure_rows = _split_dq_rows(df, active_rules, dq_run_id=dq_run_id, row_id_columns=row_id_columns)
    return DQEnforcementResult(active_rules, rule_results, valid_rows, quarantine_rows, failure_rows)
