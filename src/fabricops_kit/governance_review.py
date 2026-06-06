"""Table-scoped governance review helpers for ``04_gov`` notebooks."""

from __future__ import annotations

import importlib
import json
from dataclasses import dataclass
from typing import Any, Iterable

from .fabric_input_output import read_lakehouse_table, write_lakehouse_table
from .metadata import _now_utc_iso, _resolve_action_by, build_metadata_column_key, build_metadata_table_key, build_runtime_audit_fields, build_dq_rule_key

CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
COLUMN_CONTEXT_TABLE = "METADATA_COLUMN_CONTEXT"
DQ_RULES_TABLE = "METADATA_DQ_RULES"
COLUMN_CLASSIFICATION_TABLE = "METADATA_COLUMN_CLASSIFICATION"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE_TABLE"
SUCCESS_STATUSES = {"success", "succeeded", "passed", "complete", "completed", "ok"}
DQ_RULE_TYPES = ["not_null", "unique", "accepted_values", "value_range", "regex", "datatype", "referential_integrity", "custom_expression"]
SENSITIVITY_LABELS = ["public", "internal", "confidential", "restricted"]
PERSONAL_DATA_CLASSIFICATIONS = ["not_personal_data", "direct_identifier", "indirect_identifier", "sensitive_personal_data", "unknown"]

_SELECTED_CATALOGUE_TABLE: dict[str, Any] | None = None


@dataclass(frozen=True)
class CatalogueTableSelection:
    """Stable identity for a profiled table selected from the data catalogue.

    Parameters
    ----------
    environment_name, dataset_name, table_name : str
        Logical table identity selected from ``METADATA_DATA_CATALOGUE``.
    metadata_table_key : str
        Stable table key preserved from catalogue rows or derived from the logical identity.
    profile_run_id : str
        Latest successful profile run selected for governance review.
    profile_stage : str
        Profile stage such as ``source`` or ``target``.
    layer, asset_kind : str
        Display context from the catalogue.
    profiled_at : str, optional
        Profile timestamp for the selected run.
    """

    environment_name: str
    dataset_name: str
    table_name: str
    metadata_table_key: str
    profile_run_id: str
    profile_stage: str
    layer: str = ""
    asset_kind: str = ""
    profiled_at: str = ""

    def as_dict(self) -> dict[str, Any]:
        """Return the selection as a plain dictionary."""
        return dict(self.__dict__)


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


def get_governance_metadata_schemas() -> dict[str, Any]:
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


def _row_metadata_table_key(row: dict[str, Any]) -> str:
    explicit = _value(row, "metadata_table_key")
    if explicit:
        return str(explicit)
    return build_metadata_table_key(_value(row, "environment_name"), _value(row, "dataset_name"), _value(row, "table_name"))


def setup_governance_metadata_tables(*, spark: Any, config: Any, env: str) -> dict[str, Any]:
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
    schemas = get_governance_metadata_schemas()
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
            raise ValueError(f"{table_name} is missing required column(s): {', '.join(missing)}. Migrate the table before running 04_gov.")
    return {"status": "ready", "tables": list(schemas), "created_tables": created}


def catalogue_table_options(catalogue_rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
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
        raise ValueError("METADATA_DATA_CATALOGUE has no rows. Run 03_pc profiling before 04_gov.")
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
        table_key = str(_value(row, "metadata_table_key") or build_metadata_table_key(env, dataset, table))
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


def get_selected_catalogue_table() -> dict[str, Any]:
    """Return the current catalogue table selection from widget state."""
    if _SELECTED_CATALOGUE_TABLE is None:
        raise ValueError("No catalogue table has been selected. Run widget_select_catalogue_table first.")
    return dict(_SELECTED_CATALOGUE_TABLE)


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
    options = catalogue_table_options(rows)
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
    filtered = [
        r for r in rows
        if _is_success(r)
        and str(_value(r, "environment_name")) == str(selection["environment_name"])
        and str(_value(r, "dataset_name")) == str(selection["dataset_name"])
        and str(_value(r, "table_name")) == str(selection["table_name"])
        and str(_value(r, "profile_run_id")) == str(selection["profile_run_id"])
        and str(_value(r, "profile_stage")) == str(selection["profile_stage"])
        and _row_metadata_table_key(r) == str(selection["metadata_table_key"])
    ]
    if not filtered:
        raise ValueError("The selected successful profile has no column rows in METADATA_DATA_CATALOGUE.")
    return filtered


def build_profile_summary(profile_rows: list[dict[str, Any]], selection: dict[str, Any]) -> dict[str, Any]:
    """Build a concise table summary for display before governance review."""
    if not profile_rows:
        raise ValueError("Cannot summarize an empty selected profile.")
    first = profile_rows[0]
    return {
        "environment_name": selection.get("environment_name"), "dataset_name": selection.get("dataset_name"), "table_name": selection.get("table_name"),
        "layer": selection.get("layer") or _value(first, "layer"), "asset_kind": selection.get("asset_kind") or _value(first, "asset_kind"),
        "profile_stage": selection.get("profile_stage") or _value(first, "profile_stage"), "profile_run_id": selection.get("profile_run_id"),
        "profiled_at": max(str(_value(r, "profiled_at")) for r in profile_rows), "row_count": max(int(_value(r, "row_count", 0) or 0) for r in profile_rows),
        "column_count": len({str(_value(r, "column_name")) for r in profile_rows if _value(r, "column_name")}),
    }


def latest_by_column(rows: Any, *, approved_status: str = "approved") -> dict[str, dict[str, Any]]:
    """Return latest approved metadata row by ``metadata_column_key``."""
    filtered = [r for r in _coerce_rows(rows) if str(r.get("review_status") or r.get("status") or "").lower() == approved_status]
    out: dict[str, dict[str, Any]] = {}
    for row in sorted(filtered, key=lambda r: str(r.get("approved_at") or r.get("_committed_at") or "")):
        key = str(row.get("metadata_column_key") or "")
        if key:
            out[key] = row
    return out


def optional_ai_generate_response(prepared_df: Any, *, prompt: str, output_col: str = "ai_suggestion") -> Any | None:
    """Run Fabric AI when available and return ``None`` when unavailable."""
    ai = getattr(prepared_df, "ai", None)
    if ai is None or not hasattr(ai, "generate_response"):
        return None
    return ai.generate_response(prompt=prompt, is_prompt_template=True, output_col=output_col)


def _audit(config: Any, env: str, approved_by: str | None) -> dict[str, str]:
    return build_runtime_audit_fields(config=config, env=env, committed_by=approved_by)


def build_column_context_records(profile_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
    """Build append-only approved business-context records from explicit reviews."""
    profile = {str(_value(r, "column_name")): r for r in profile_rows}
    actor = _resolve_action_by(approved_by)
    now = _now_utc_iso()
    audit = _audit(config, env or "", actor) if config is not None and env is not None else {}
    rows = []
    for review in reviewed_rows or []:
        if str(review.get("review_status", "approved")).lower() != "approved" or not review.get("commit"):
            continue
        col = str(review.get("column_name"))
        p = profile.get(col, {})
        env_name = str(_value(p, "environment_name") or review.get("environment_name") or env or "")
        dataset = str(_value(p, "dataset_name") or review.get("dataset_name") or "")
        table = str(_value(p, "table_name") or review.get("table_name") or "")
        rows.append({
            "metadata_column_key": str(_value(p, "metadata_column_key") or review.get("metadata_column_key") or build_metadata_column_key(env_name, dataset, table, col)),
            "metadata_table_key": str(_value(p, "metadata_table_key") or review.get("metadata_table_key") or build_metadata_table_key(env_name, dataset, table)),
            "environment_name": env_name, "dataset_name": dataset, "table_name": table, "column_name": col,
            "business_context": str(review.get("business_context") or ""), "notes": str(review.get("notes") or ""), "review_status": "approved",
            "approved_by": actor, "approved_at": now, "ai_suggestion_json": _json(review.get("ai_suggestion_json") or review.get("ai_suggestion")), **audit,
        })
    return rows


def build_dq_rule_records(profile_rows: list[dict[str, Any]], reviewed_rules: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
    """Build append-only approved DQ-rule records without enforcing them."""
    actor = _resolve_action_by(approved_by)
    now = _now_utc_iso()
    audit = _audit(config, env or "", actor) if config is not None and env is not None else {}
    profile = {str(_value(r, "column_name")): r for r in profile_rows}
    rows = []
    for rule in reviewed_rules or []:
        if str(rule.get("review_status", "approved")).lower() != "approved" or not rule.get("commit"):
            continue
        rule_type = str(rule.get("rule_type") or "")
        if rule_type not in DQ_RULE_TYPES:
            raise ValueError(f"Unsupported rule_type: {rule_type}")
        col = str(rule.get("column_name") or "")
        p = profile.get(col, {})
        env_name = str(_value(p, "environment_name") or rule.get("environment_name") or env or "")
        dataset = str(_value(p, "dataset_name") or rule.get("dataset_name") or "")
        table = str(_value(p, "table_name") or rule.get("table_name") or "")
        rule_id = str(rule.get("rule_id") or f"{table}.{col}.{rule_type}")
        rows.append({
            "rule_key": build_dq_rule_key(env_name, dataset, table, rule_id), "rule_id": rule_id,
            "metadata_column_key": str(_value(p, "metadata_column_key") or rule.get("metadata_column_key") or build_metadata_column_key(env_name, dataset, table, col)),
            "metadata_table_key": str(_value(p, "metadata_table_key") or rule.get("metadata_table_key") or build_metadata_table_key(env_name, dataset, table)),
            "environment_name": env_name, "dataset_name": dataset, "table_name": table, "column_name": col,
            "rule_type": rule_type, "rule_parameters_json": _json(rule.get("rule_parameters") or rule.get("rule_parameters_json") or {}),
            "severity": str(rule.get("severity") or "warning"), "description": str(rule.get("description") or ""), "is_active": bool(rule.get("is_active", True)),
            "review_status": "approved", "approved_by": actor, "approved_at": now, "ai_suggestion_json": _json(rule.get("ai_suggestion_json") or rule.get("ai_suggestion")), "action_type": "approved", **audit,
        })
    return rows


def build_classification_records(profile_rows: list[dict[str, Any]], reviewed_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
    """Build append-only approved sensitivity and PII classification records."""
    actor = _resolve_action_by(approved_by)
    now = _now_utc_iso()
    audit = _audit(config, env or "", actor) if config is not None and env is not None else {}
    profile = {str(_value(r, "column_name")): r for r in profile_rows}
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
        col = str(review.get("column_name"))
        p = profile.get(col, {})
        env_name = str(_value(p, "environment_name") or review.get("environment_name") or env or "")
        dataset = str(_value(p, "dataset_name") or review.get("dataset_name") or "")
        table = str(_value(p, "table_name") or review.get("table_name") or "")
        rows.append({
            "metadata_column_key": str(_value(p, "metadata_column_key") or review.get("metadata_column_key") or build_metadata_column_key(env_name, dataset, table, col)),
            "metadata_table_key": str(_value(p, "metadata_table_key") or review.get("metadata_table_key") or build_metadata_table_key(env_name, dataset, table)),
            "environment_name": env_name, "dataset_name": dataset, "table_name": table, "column_name": col,
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


def commit_column_context(config: Any, env: str, rows: list[dict[str, Any]], *, spark_session: Any, mode: str = "append") -> list[dict[str, Any]]:
    """Persist approved business context rows after explicit human commit."""
    if rows:
        write_lakehouse_table(spark_session.createDataFrame(rows), config, env, "metadata", COLUMN_CONTEXT_TABLE, mode=mode)
    return rows


def commit_dq_rules(config: Any, env: str, rows: list[dict[str, Any]], *, spark_session: Any, mode: str = "append") -> list[dict[str, Any]]:
    """Persist approved DQ rules after explicit human commit."""
    if rows:
        write_lakehouse_table(spark_session.createDataFrame(rows), config, env, "metadata", DQ_RULES_TABLE, mode=mode)
    return rows


def commit_column_classification(config: Any, env: str, rows: list[dict[str, Any]], *, spark_session: Any, mode: str = "append") -> list[dict[str, Any]]:
    """Persist approved classification rows after explicit human commit."""
    if rows:
        write_lakehouse_table(spark_session.createDataFrame(rows), config, env, "metadata", COLUMN_CLASSIFICATION_TABLE, mode=mode)
    return rows


def widget_review_table_governance(profile_rows: list[dict[str, Any]], *, existing_context: dict[str, dict[str, Any]] | None = None, existing_rules: dict[str, dict[str, Any]] | None = None, existing_classification: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """Render lightweight copy-ready review guidance for three governance stages.

    Parameters
    ----------
    profile_rows : list of dict
        Selected column profile evidence.
    existing_context, existing_rules, existing_classification : dict, optional
        Latest approved state keyed by column key.

    Returns
    -------
    dict[str, Any]
        Review state scaffold. Users explicitly pass edited rows to build and
        commit helpers; rendering this widget never writes metadata.
    """
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    state = {"context": existing_context or {}, "rules": existing_rules or {}, "classification": existing_classification or {}}
    columns = [str(_value(row, "column_name")) for row in profile_rows]
    html = widgets.HTML(
        "<h3>04_gov human review stages</h3>"
        "<ol><li>Business context: edit rows and call commit_column_context only after approval.</li>"
        "<li>DQ rules: author rules and call commit_dq_rules only after approval.</li>"
        "<li>Sensitivity/PII: review labels and call commit_column_classification only after approval.</li></ol>"
        f"<p><b>Columns loaded:</b> {', '.join(columns)}</p>"
        "<p>AI suggestions are advisory and are never written by this widget.</p>"
    )
    ip.display(html)
    return state
