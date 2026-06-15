"""Lightweight schema and profile behavior guardrails for pipeline notebooks.

Use :func:`validate_schema`, :func:`enforce_freshness`,
:func:`enforce_profile_behavior`, and :func:`stop_if_failed` in production
pipeline notebooks. FabricOps enforces technical data-contract expectations
with simple freshness and profile behavior choices.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4


_DEFAULT_STABILITY_EXCLUDE_COLUMNS = {
    "_fabricops_run_id",
    "_fabricops_pipeline_name",
    "_fabricops_created_at",
    "_dq_check_status",
    "_dq_failed_rules",
}
_DEFAULT_STABILITY_EXCLUDE_PREFIXES = ("_fabricops_", "_dq_")


class SchemaDriftError(Exception):
    """Raised when a guardrail check is configured to stop execution.

    Notes
    -----
    This exception is shared by schema-check workflows so notebook callers
    have one failure type to catch when they choose fail-fast behavior.

    """


def _normalize_datatype(data_type) -> str:
    raw = str(data_type).strip().lower()
    raw = re.sub(r"\s+", "", raw)

    decimal_match = re.search(r"decimaltype\((\d+),(\d+)\)|decimal\((\d+),(\d+)\)", raw)
    if decimal_match:
        precision = decimal_match.group(1) or decimal_match.group(3)
        scale = decimal_match.group(2) or decimal_match.group(4)
        return f"decimal({precision},{scale})"

    aliases = {
        "integertype()": "int",
        "integertype": "int",
        "integer": "int",
        "int32": "int",
        "int": "int",
        "longtype()": "bigint",
        "longtype": "bigint",
        "long": "bigint",
        "int64": "bigint",
        "bigint": "bigint",
        "stringtype()": "string",
        "stringtype": "string",
        "str": "string",
        "object": "string",
        "string": "string",
        "datetype()": "date",
        "datetype": "date",
        "date": "date",
        "timestamptype()": "timestamp",
        "timestamptype": "timestamp",
        "timestamp": "timestamp",
        "datetime64[ns]": "timestamp",
        "doubletype()": "double",
        "doubletype": "double",
        "double": "double",
        "float64": "double",
        "floattype()": "float",
        "floattype": "float",
        "float32": "float",
        "float": "float",
        "booleantype()": "boolean",
        "booleantype": "boolean",
        "bool": "boolean",
        "boolean": "boolean",
    }
    return aliases.get(raw, raw)


def _actual_schema(df) -> tuple[list[str], dict[str, str]]:
    schema = getattr(df, "schema", None)
    if schema is not None and hasattr(schema, "fields"):
        columns = [str(field.name) for field in schema.fields]
        types = {str(field.name): _normalize_datatype(getattr(field, "dataType", "")) for field in schema.fields}
        return columns, types

    dtypes = getattr(df, "dtypes", None)
    if dtypes is not None:
        dtype_items = dtypes.items() if hasattr(dtypes, "items") else dtypes
        types = {str(name): _normalize_datatype(dtype) for name, dtype in dtype_items}
        columns = [str(column) for column in getattr(df, "columns", list(types))]
        return columns, types

    columns = [str(column) for column in getattr(df, "columns", [])]
    return columns, {}



def _json_dumps_stable(value) -> str:
    return json.dumps(value, default=str, sort_keys=True, separators=(",", ":"))


def _profile_hash(payload: dict) -> str:
    return hashlib.sha256(_json_dumps_stable(payload).encode("utf-8")).hexdigest()


def _schema_signature(dataframe) -> list[dict[str, str]]:
    columns, types = _actual_schema(dataframe)
    return [{"column_name": column, "data_type": types.get(column, "")} for column in columns]


def _profile_payload_from_profile(profile, *, dataframe=None, watermark_column: str = "", watermark_value: str = "") -> dict:
    normalized = _normalize_profile(profile) or {}
    columns = []
    for column in normalized.get("columns", []) or []:
        if not isinstance(column, dict):
            continue
        columns.append({
            "column_name": _string_value(column.get("column_name")),
            "data_type": _string_value(column.get("data_type")),
            "null_count": _string_value(column.get("null_count")),
            "distinct_count": _string_value(column.get("distinct_count")),
            "min_value": _string_value(column.get("min_value")),
            "max_value": _string_value(column.get("max_value")),
        })
    columns.sort(key=lambda item: item["column_name"])
    return {
        "row_count": _profile_row_count(profile),
        "schema_signature": _schema_signature(dataframe) if dataframe is not None else [],
        "columns": columns,
        "watermark_column": watermark_column or "",
        "watermark_value": watermark_value or "",
    }



def _select_profile_behavior_rule(rules_df, *, dataset_name: str, table_name: str) -> dict | None:
    if rules_df is None:
        return None
    rows = rules_df.collect() if hasattr(rules_df, "collect") else ([rules_df] if isinstance(rules_df, dict) else rules_df)
    candidates = []
    for raw in rows or []:
        row = _row_to_dict(raw)
        if _string_value(_catalogue_value(row, "guardrail_type")).lower() != "profile_behavior":
            continue
        if _string_value(_catalogue_value(row, "dataset_name")) not in {"", dataset_name}:
            continue
        if _string_value(_catalogue_value(row, "table_name")) != table_name:
            continue
        if _string_value(_catalogue_value(row, "is_active")).lower() in {"false", "0", "no"}:
            continue
        review_status = _string_value(_catalogue_value(row, "review_status")).lower()
        if review_status and review_status not in {"approved", "governance_approved", "engineer_approved", "active"}:
            continue
        candidates.append(row)
    if not candidates:
        return None
    candidates.sort(key=lambda row: _string_value(_catalogue_value(row, "approved_at", "created_at", "_committed_at")), reverse=True)
    return candidates[0]

def _accepted_profile_rows(catalogue_df, *, environment_name: str, dataset_name: str, table_name: str, watermark_column: str, exclude_run_id: str | None = None) -> list[dict]:
    if catalogue_df is None:
        return []
    rows = catalogue_df.collect() if hasattr(catalogue_df, "collect") else ([catalogue_df] if isinstance(catalogue_df, dict) else catalogue_df)
    candidates = []
    for raw in rows or []:
        row = _row_to_dict(raw)
        if environment_name and _string_value(_catalogue_value(row, "environment_name")) not in {"", environment_name}:
            continue
        if _string_value(_catalogue_value(row, "dataset_name")) != dataset_name:
            continue
        if _string_value(_catalogue_value(row, "table_name", "profiled_table_name")) != table_name:
            continue
        if _string_value(_catalogue_value(row, "guardrail_type", "profile_guardrail_type")) not in {"", "profile_behavior"}:
            continue
        if _string_value(_catalogue_value(row, "watermark_column")) != _string_value(watermark_column):
            continue
        if exclude_run_id and _string_value(_catalogue_value(row, "profile_run_id", "run_id")) == str(exclude_run_id):
            continue
        if _string_value(_catalogue_value(row, "profile_status")).lower() not in {"", "success", "successful", "passed", "accepted"}:
            continue
        status = _string_value(_catalogue_value(row, "stability_status", "profile_behavior_status", "baseline_status")).lower()
        if status not in {"passed", "baseline_created", "accepted", "approved"}:
            continue
        candidates.append(row)
    candidates.sort(key=lambda row: (_string_value(_catalogue_value(row, "watermark_value")), _string_value(_catalogue_value(row, "profiled_at", "created_at")), _string_value(_catalogue_value(row, "profile_run_id", "run_id"))))
    latest = {}
    for row in candidates:
        latest[_string_value(_catalogue_value(row, "watermark_value"))] = row
    return list(latest.values())


_SCHEMA_PRESETS = {"strict", "allow_new_columns", "monitor_only"}


def validate_schema(dataframe, expected_schema: dict[str, str], *, preset: str = "strict") -> dict:
    """Validate a dataframe schema using an intent-based preset.

    Parameters
    ----------
    dataframe : Any
        Spark, pandas, or dataframe-like object with schema metadata.
    expected_schema : dict[str, str]
        Mapping of required column names to expected datatype strings.
    preset : {"strict", "allow_new_columns", "monitor_only"}, default="strict"
        Schema validation intent. ``strict`` blocks missing columns, datatype
        changes, and unexpected columns. ``allow_new_columns`` blocks missing
        columns and datatype changes while reporting additional columns as a
        warning. ``monitor_only`` reports all differences without blocking.

    Returns
    -------
    dict
        Standard guardrail result with ``status``, ``can_continue``,
        ``checks``, and ``message`` plus detailed schema difference fields.

    Raises
    ------
    ValueError
        If ``preset`` is not one of the supported schema presets.

    Examples
    --------
    >>> validate_schema(df, {"id": "int"}, preset="allow_new_columns")
    {'status': 'passed', 'can_continue': True, ...}

    """
    normalized_preset = str(preset).lower()
    if normalized_preset not in _SCHEMA_PRESETS:
        raise ValueError("preset must be one of: strict, allow_new_columns, monitor_only")

    actual_columns, actual_types = _actual_schema(dataframe)
    actual_set = set(actual_columns)
    expected_names = [str(column) for column in expected_schema]
    expected_set = set(expected_names)

    missing_columns = [column for column in expected_names if column not in actual_set]
    datatype_mismatches = []
    for column, expected_type in expected_schema.items():
        column_name = str(column)
        if column_name in actual_set and column_name in actual_types:
            expected = _normalize_datatype(expected_type)
            actual = actual_types[column_name]
            if actual != expected:
                datatype_mismatches.append({"column": column_name, "expected": expected, "actual": actual})

    checks = []
    for column in missing_columns:
        checks.append({"check": "missing_column", "column": column, "status": "failed", "passed": False})
    for mismatch in datatype_mismatches:
        checks.append({"check": "datatype_mismatch", **mismatch, "status": "failed", "passed": False})
    actual_unexpected = [column for column in actual_columns if str(column) not in expected_set]
    for column in actual_unexpected:
        checks.append({"check": "unexpected_column", "column": column, "status": "warning" if normalized_preset == "allow_new_columns" else "failed", "passed": normalized_preset == "allow_new_columns"})

    blocking = bool(missing_columns or datatype_mismatches)
    if normalized_preset == "strict":
        blocking = blocking or bool(actual_unexpected)
    if normalized_preset == "monitor_only":
        status = "warning" if checks else "passed"
        can_continue = True
    elif blocking:
        status = "failed"
        can_continue = False
    elif normalized_preset == "allow_new_columns" and actual_unexpected:
        status = "warning"
        can_continue = True
    else:
        status = "passed"
        can_continue = True

    message = (
        "Schema validation passed."
        if status == "passed"
        else f"Schema validation {status}: {len(missing_columns)} missing, {len(actual_unexpected)} unexpected, {len(datatype_mismatches)} datatype mismatch(es)."
    )
    return {
        "status": status,
        "can_continue": can_continue,
        "checks": checks,
        "message": message,
        "missing_columns": missing_columns,
        "unexpected_columns": actual_unexpected,
        "datatype_mismatches": datatype_mismatches,
        "preset": normalized_preset,
    }


def _normalize_profile(profile) -> dict | None:
    def row_value(row, *names):
        for name in names:
            if isinstance(row, dict) and name in row:
                return row.get(name)
            if hasattr(row, "asDict"):
                data = row.asDict(recursive=True)
                if name in data:
                    return data.get(name)
            if hasattr(row, name):
                return getattr(row, name)
        return None

    def distribution_payload(value):
        if value in (None, ""):
            return None
        if isinstance(value, dict):
            return value
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError):
            return None

    if profile is None:
        return None
    if isinstance(profile, dict) and "columns" in profile:
        return profile
    if hasattr(profile, "collect"):
        return _normalize_profile(profile.collect())
    if isinstance(profile, (list, tuple)):
        rows = list(profile)
        if not rows:
            return None
        first = rows[0]
        row_count = row_value(first, "row_count", "ROW_COUNT", "PROFILED_ROW_COUNT")
        table_name = row_value(first, "table_name", "TABLE_NAME", "PROFILED_TABLE_NAME")
        dataset_name = row_value(first, "dataset_name", "DATASET_NAME")
        profile_stage = row_value(first, "profile_stage", "PROFILE_STAGE", "EVIDENCE_ROLE")
        columns = []
        for row in rows:
            distribution_type = row_value(row, "distribution_type", "DISTRIBUTION_TYPE")
            distribution = distribution_payload(row_value(row, "distribution", "DISTRIBUTION", "distribution_json", "DISTRIBUTION_JSON"))
            column = {
                "column_name": row_value(row, "column_name", "COLUMN_NAME"),
                "data_type": row_value(row, "data_type", "DATA_TYPE"),
                "row_count": row_value(row, "row_count", "ROW_COUNT", "PROFILED_ROW_COUNT"),
                "null_count": row_value(row, "null_count", "NULL_COUNT"),
                "null_pct": row_value(row, "null_pct", "NULL_PCT", "null_percent", "NULL_PERCENT"),
                "distinct_count": row_value(row, "distinct_count", "DISTINCT_COUNT"),
                "distinct_pct": row_value(row, "distinct_pct", "DISTINCT_PCT", "distinct_percent", "DISTINCT_PERCENT"),
                "min_value": row_value(row, "min_value", "MIN_VALUE"),
                "max_value": row_value(row, "max_value", "MAX_VALUE"),
            }
            if distribution_type:
                column["distribution_type"] = distribution_type
            if distribution is not None:
                column["distribution"] = distribution
            columns.append(column)
        return {
            "dataset_name": dataset_name,
            "table_name": table_name,
            "profile_stage": profile_stage,
            "row_count": row_count,
            "columns": columns,
            "profile_status": row_value(first, "profile_status", "PROFILE_STATUS"),
            "baseline_status": row_value(first, "baseline_status", "BASELINE_STATUS"),
            "source_change_signal": distribution_payload(row_value(first, "source_change_signal", "SOURCE_CHANGE_SIGNAL_JSON")),
        }
    return profile


def _row_to_dict(row) -> dict:
    if row is None:
        return {}
    if isinstance(row, dict):
        return dict(row)
    if hasattr(row, "asDict"):
        return row.asDict(recursive=True)
    return {name: getattr(row, name) for name in dir(row) if not name.startswith("_")}


def _guardrail_exclude_columns(exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None) -> set[str]:
    excluded = set(_DEFAULT_STABILITY_EXCLUDE_COLUMNS)
    if exclude_columns:
        excluded.update(str(column) for column in exclude_columns)
    return excluded


def _is_guardrail_excluded_column(column: str, exclude_columns: set[str]) -> bool:
    name = str(column)
    return name in exclude_columns or any(name.startswith(prefix) for prefix in _DEFAULT_STABILITY_EXCLUDE_PREFIXES)


def _profile_row_count(profile) -> int | None:
    normalized = _normalize_profile(profile) or {}
    value = normalized.get("row_count")
    if value in (None, ""):
        columns = normalized.get("columns") or []
        if columns:
            first_column = columns[0] or {}
            if isinstance(first_column, dict):
                value = first_column.get("row_count")
    try:
        return int(value) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _max_column_value(dataframe, column_name: str):
    if dataframe is None or not column_name:
        return None
    if hasattr(dataframe, "agg"):
        from pyspark.sql import functions as F

        rows = dataframe.agg(F.max(F.col(column_name)).alias("latest_value")).collect()
        if not rows:
            return None
        row = rows[0]
        if isinstance(row, dict):
            return row.get("latest_value")
        if hasattr(row, "asDict"):
            return row.asDict().get("latest_value")
        try:
            return row["latest_value"]
        except Exception:
            return getattr(row, "latest_value", None)
    if isinstance(dataframe, dict):
        values = [dataframe.get(column_name)]
    else:
        values = []
        for row in dataframe or []:
            if isinstance(row, dict):
                values.append(row.get(column_name))
            elif hasattr(row, "asDict"):
                values.append(row.asDict().get(column_name))
            else:
                values.append(getattr(row, column_name, None))
    values = [value for value in values if value not in (None, "")]
    return max(values) if values else None


def _coerce_date(value) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _iso_date_value(value) -> str:
    parsed = _coerce_date(value)
    return parsed.isoformat() if parsed is not None else ("" if value is None else str(value))


def enforce_freshness(
    dataframe,
    freshness_column: str | None,
    max_lag_days: int | str | None,
    severity: str = "blocking",
    *,
    reference_date: date | datetime | str | None = None,
) -> dict:
    """Enforce that a DataFrame contains recent enough data.

    Parameters
    ----------
    dataframe : Any
        Spark DataFrame or iterable of row-like mappings to check.
    freshness_column : str or None
        Column whose maximum value represents the latest available data date.
        When omitted, the freshness guardrail is skipped.
    max_lag_days : int or str or None
        Maximum allowed lag, in days, between ``reference_date`` and the latest
        value in ``freshness_column``. Required when ``freshness_column`` is set.
    severity : {"blocking", "warning"}, default="blocking"
        Whether stale data blocks continuation or returns a non-blocking warning.
    reference_date : date, datetime, str, optional
        Date used as "today" for comparison. Defaults to the current local date.

    Returns
    -------
    dict
        Standard guardrail result with ``status``, ``can_continue``,
        ``check_type``, latest value, required minimum value, and message.

    Notes
    -----
    Freshness is separate from profile behavior. ``profile_mode="skip"`` only
    skips profile behavior enforcement; freshness still runs when configured.

    """
    column = str(freshness_column or "").strip()
    normalized_severity = str(severity or "blocking").lower().strip()
    if normalized_severity not in {"blocking", "warning"}:
        raise ValueError("severity must be one of: blocking, warning")

    base_result = {
        "status": "skipped",
        "can_continue": True,
        "check_type": "freshness",
        "freshness_column": column,
        "freshness_max_lag_days": "" if max_lag_days in (None, "") else max_lag_days,
        "freshness_severity": normalized_severity,
        "latest_value": "",
        "required_min_value": "",
        "freshness_status": "skipped",
        "freshness_can_continue": True,
        "freshness_message": "Freshness check skipped because no freshness column is configured.",
        "message": "Freshness check skipped because no freshness column is configured.",
    }
    if not column:
        return base_result
    if max_lag_days is None or str(max_lag_days).strip() == "":
        raise ValueError("max_lag_days is required when freshness_column is set")
    lag_days = int(max_lag_days)
    if lag_days < 0:
        raise ValueError("max_lag_days must be greater than or equal to zero")
    base_result["freshness_max_lag_days"] = lag_days

    today = _coerce_date(reference_date) if reference_date is not None else date.today()
    if today is None:
        raise ValueError("reference_date must be a date, datetime, or ISO date string")
    required_min = today - timedelta(days=lag_days)
    latest_raw = _max_column_value(dataframe, column)
    latest_date = _coerce_date(latest_raw)
    latest_display = _iso_date_value(latest_raw)
    required_display = required_min.isoformat()
    base_result.update(latest_value=latest_display, required_min_value=required_display)

    if latest_date is not None and latest_date >= required_min:
        message = "Freshness check passed."
        base_result.update(
            status="passed",
            can_continue=True,
            freshness_status="passed",
            freshness_can_continue=True,
            freshness_message=message,
            message=message,
        )
        return base_result

    message = f"Freshness check failed: latest {column} is older than allowed lag."
    status = "failed" if normalized_severity == "blocking" else "warning"
    can_continue = normalized_severity == "warning"
    base_result.update(
        status=status,
        can_continue=can_continue,
        freshness_status=status,
        freshness_can_continue=can_continue,
        freshness_message=message,
        message=message,
    )
    return base_result


def _catalogue_value(row: dict, *names: str):
    for name in names:
        if name in row:
            return row.get(name)
        upper = name.upper()
        if upper in row:
            return row.get(upper)
        lower = name.lower()
        for key, value in row.items():
            if str(key).lower() == lower:
                return value
    return None


def _string_value(value) -> str:
    return "" if value is None else str(value)


def _comparable_value(value):
    if value in (None, ""):
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    text = str(value)
    try:
        return Decimal(text)
    except Exception:
        return text


def _is_less_than(left, right) -> bool:
    left_value = _comparable_value(left)
    right_value = _comparable_value(right)
    if left_value is None or right_value is None:
        return False
    if isinstance(left_value, Decimal) and isinstance(right_value, Decimal):
        return left_value < right_value
    return str(left_value) < str(right_value)


def _is_greater_than(left, right) -> bool:
    left_value = _comparable_value(left)
    right_value = _comparable_value(right)
    if left_value is None or right_value is None:
        return False
    if isinstance(left_value, Decimal) and isinstance(right_value, Decimal):
        return left_value > right_value
    return str(left_value) > str(right_value)


def enforce_profile_behavior(
    spark,
    dataframe,
    metadata_table: str,
    dataset_name: str,
    table_name: str,
    *,
    stage: str,
    run_id: str,
    profile_mode: str | None = None,
    watermark_column: str | None = None,
    severity: str = "blocking",
    rule_key: str = "profile_behavior_default",
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    exclude_run_id: str | None = None,
    config=None,
    env: str | None = None,
    catalogue_df=None,
    current_profile=None,
    write_results: bool = True,
    rules_table: str = "METADATA_GUARDRAIL_RULES",
    rules_df=None,
) -> dict:
    """Enforce profile behavior guardrails using catalogue evidence as baseline.

    Parameters
    ----------
    spark : Any
        Spark session used to read metadata when ``catalogue_df`` is not supplied.
    dataframe : Any
        Spark DataFrame being checked.
    metadata_table : str
        Metadata catalogue table, normally ``METADATA_DATA_CATALOGUE``.
    dataset_name : str
        Dataset identifier used for rule and baseline lookup.
    table_name : str
        Table identifier used for rule and baseline lookup.
    stage : str
        Pipeline stage used in returned evidence.
    run_id : str
        Current pipeline run identifier.
    profile_mode : {"static_data", "changing_data", "skip"}, optional
        Profile behavior mode. Defaults to ``"static_data"`` when no approved
        rule supplies a mode.
    watermark_column : str, optional
        Required for ``changing_data``. Values define independent profile groups.
    severity : {"blocking", "warning"}, default="blocking"
        Blocking failures stop continuation; warning failures report but allow continuation.
    rule_key : str, default="profile_behavior_default"
        Rule identifier written to guardrail result evidence when no approved
        rule row supplies one.
    exclude_columns : list-like, optional
        Business or technical columns to exclude from generated profile
        evidence.
    exclude_run_id : str, optional
        Run identifier to exclude from previous catalogue baseline lookup.
        Defaults to ``run_id``.
    config : object, optional
        Runtime configuration from ``00_env_config`` used to read metadata and
        write result evidence when paired with ``env``.
    env : str, optional
        Environment key used with ``config`` for configured metadata routing.
    catalogue_df : DataFrame or iterable of mappings, optional
        Preloaded ``METADATA_DATA_CATALOGUE`` evidence.
    current_profile : DataFrame or iterable of mappings, optional
        Current profile evidence for static mode.
    write_results : bool, default=True
        Whether to append runtime outcome rows to
        ``METADATA_GUARDRAIL_RESULTS`` when ``config`` and ``env`` are
        supplied.
    rules_table : str, default="METADATA_GUARDRAIL_RULES"
        Metadata table used to load approved profile behavior rules when
        ``rules_df`` is not supplied.
    rules_df : DataFrame or iterable of mappings, optional
        Preloaded guardrail rules. When supplied, no rules-table read is
        performed.

    Returns
    -------
    dict
        Standard guardrail result plus catalogue profile evidence and comparison
        details suitable for ``METADATA_DATA_CATALOGUE`` and
        ``METADATA_GUARDRAIL_RESULTS``.

    Notes
    -----
    Baselines are never reset here. Current profile evidence is compared to the
    previous accepted or passed catalogue evidence. Intentional blocked changes
    should be reviewed in governance or handled by superseding/resetting the
    relevant guardrail rule.


    """
    if rules_df is None and config is not None and env is not None:
        from fabricops_kit.fabric_input_output import _configured_lakehouse_schema, read_lakehouse_table
        try:
            rules_df = read_lakehouse_table(config, env, "metadata", rules_table, schema=_configured_lakehouse_schema(config, env, "metadata"), spark_session=spark)
        except Exception as exc:
            if not _is_missing_table_error(exc):
                raise

    selected_rule = _select_profile_behavior_rule(rules_df, dataset_name=dataset_name, table_name=table_name)
    if selected_rule:
        rule_key = _string_value(_catalogue_value(selected_rule, "rule_key", "rule_id")) or rule_key
        severity = _catalogue_value(selected_rule, "severity") or severity
        profile_mode = profile_mode or _catalogue_value(selected_rule, "rule_type", "profile_mode")
        rule_parameters = _catalogue_value(selected_rule, "rule_parameters_json") or "{}"
        try:
            rule_parameters = json.loads(rule_parameters) if isinstance(rule_parameters, str) else dict(rule_parameters or {})
        except Exception:
            rule_parameters = {}
        watermark_column = watermark_column or rule_parameters.get("watermark_column") or _catalogue_value(selected_rule, "watermark_column", "column_name")

    mode = str(profile_mode or "static_data").lower().strip()
    normalized_severity = str(severity or "blocking").lower().strip()
    if normalized_severity not in {"blocking", "warning"}:
        raise ValueError("severity must be one of: blocking, warning")
    if mode not in {"static_data", "changing_data", "skip"}:
        raise ValueError("profile_mode must be one of: static_data, changing_data, skip")

    if catalogue_df is None and config is not None and env is not None:
        from fabricops_kit.fabric_input_output import _configured_lakehouse_schema, read_lakehouse_table
        try:
            catalogue_df = read_lakehouse_table(config, env, "metadata", metadata_table, schema=_configured_lakehouse_schema(config, env, "metadata"), spark_session=spark)
        except Exception as exc:
            if _is_missing_table_error(exc):
                catalogue_df = None
            else:
                raise

    environment_name = env or ""
    evidence_rows: list[dict] = []
    if mode == "skip":
        message = "Profile behavior guardrail skipped; other guardrails still apply."
        return {"status": "skipped", "can_continue": True, "check_type": "profile_behavior", "guardrail_type": "profile_behavior", "rule_type": "skip", "stability_check_enabled": False, "profile_mode": "skip", "watermark_column": watermark_column or "", "stability_status": "skipped", "stability_can_continue": True, "stability_message": message, "message": message, "profile_evidence_rows": []}

    effective_exclude_columns = _guardrail_exclude_columns(exclude_columns)
    if mode == "static_data":
        if current_profile is None:
            from fabricops_kit.data_profiling import profile_dataframe
            current_profile = profile_dataframe(dataframe, table_name, exclude_columns=effective_exclude_columns, config=config)
        payload = _profile_payload_from_profile(current_profile, dataframe=dataframe, watermark_column="", watermark_value="__FULL_TABLE__")
        evidence_rows.append({"watermark_column": "", "watermark_value": "__FULL_TABLE__", "row_count": payload.get("row_count"), "profile_payload_json": _json_dumps_stable(payload), "profile_hash": _profile_hash(payload)})
    else:
        if not watermark_column:
            raise ValueError("watermark_column is required for changing_data profile behavior")
        if not hasattr(dataframe, "filter") or not hasattr(dataframe, "select"):
            raise ValueError("changing_data profile behavior requires a Spark-like DataFrame")
        values = [row[0] for row in dataframe.select(watermark_column).distinct().collect()]
        from fabricops_kit.data_profiling import profile_dataframe
        for value in sorted(values, key=lambda item: str(item)):
            group_df = dataframe.filter(dataframe[watermark_column] == value)
            group_profile = profile_dataframe(group_df, table_name, exclude_columns=effective_exclude_columns, config=config)
            payload = _profile_payload_from_profile(group_profile, dataframe=group_df, watermark_column=watermark_column, watermark_value=_string_value(value))
            evidence_rows.append({"watermark_column": watermark_column, "watermark_value": _string_value(value), "row_count": payload.get("row_count"), "profile_payload_json": _json_dumps_stable(payload), "profile_hash": _profile_hash(payload)})

    previous = _accepted_profile_rows(catalogue_df, environment_name=environment_name, dataset_name=dataset_name, table_name=table_name, watermark_column=("" if mode == "static_data" else watermark_column or ""), exclude_run_id=exclude_run_id or run_id)
    previous_by_wm = {_string_value(_catalogue_value(row, "watermark_value")): row for row in previous}
    current_by_wm = {row["watermark_value"]: row for row in evidence_rows}
    differences = []
    for wm, baseline in previous_by_wm.items():
        if wm not in current_by_wm:
            differences.append({"difference_type": "missing_watermark_value", "watermark_value": wm})
            continue
        old_hash = _string_value(_catalogue_value(baseline, "profile_hash"))
        new_hash = current_by_wm[wm]["profile_hash"]
        if old_hash and old_hash != new_hash:
            differences.append({"difference_type": "profile_changed", "watermark_value": wm, "expected_profile_hash": old_hash, "actual_profile_hash": new_hash})
    new_groups = [wm for wm in current_by_wm if wm not in previous_by_wm]

    if not previous:
        status = "baseline_created"
        can_continue = True
        message = "No previous accepted profile_behavior evidence was available; current profile establishes the catalogue baseline."
    elif differences:
        status = "failed" if normalized_severity == "blocking" else "warning"
        can_continue = normalized_severity == "warning"
        message = "Profile behavior changed versus previous accepted catalogue evidence. Review and approve the change in governance, or supersede/reset the relevant guardrail rule if intentional."
    else:
        status = "passed"
        can_continue = True
        message = "Profile behavior guardrail passed."

    result_payload = {"profile_mode": mode, "differences": differences, "new_watermark_values": new_groups, "profile_evidence_rows": evidence_rows}
    result = {
        "status": status,
        "can_continue": can_continue,
        "check_type": "profile_behavior",
        "guardrail_type": "profile_behavior",
        "rule_type": mode,
        "severity": normalized_severity,
        "rule_key": rule_key,
        "stability_check_enabled": True,
        "profile_mode": mode,
        "watermark_column": watermark_column or "",
        "watermark_value": "__FULL_TABLE__" if mode == "static_data" else "",
        "row_count": sum(int(row.get("row_count") or 0) for row in evidence_rows),
        "profile_hash": evidence_rows[0]["profile_hash"] if len(evidence_rows) == 1 else _profile_hash({"groups": evidence_rows}),
        "profile_payload_json": _json_dumps_stable(result_payload),
        "baseline_run_id": _string_value(_catalogue_value(previous[0], "profile_run_id", "run_id")) if previous else "",
        "baseline_row_count": _catalogue_value(previous[0], "row_count") if len(previous) == 1 else None,
        "baseline_watermark_min_value": "",
        "baseline_watermark_max_value": "",
        "stability_status": status,
        "stability_can_continue": can_continue,
        "stability_message": message,
        "stability_difference_summary": json.dumps(differences, default=str, sort_keys=True) if differences else "",
        "message": message,
        "profile_evidence_rows": evidence_rows,
        "expected_value_json": json.dumps({"previous": previous_by_wm}, default=str, sort_keys=True),
        "actual_value_json": json.dumps({"current": current_by_wm}, default=str, sort_keys=True),
        "result_payload_json": json.dumps(result_payload, default=str, sort_keys=True),
    }

    if write_results and config is not None and env is not None:
        try:
            from fabricops_kit.fabric_input_output import _configured_lakehouse_schema, write_lakehouse_table
            from pyspark.sql import Row
            result_row = Row(result_id=str(uuid4()), run_id=run_id, rule_key=rule_key, environment_name=environment_name, dataset_name=dataset_name, table_name=table_name, column_name="", guardrail_type="profile_behavior", rule_type=mode, status=status, can_continue=can_continue, severity=normalized_severity, reason=message, expected_value_json=result["expected_value_json"], actual_value_json=result["actual_value_json"], result_payload_json=result["result_payload_json"], created_at=datetime.utcnow().isoformat() + "Z")
            write_lakehouse_table(spark.createDataFrame([result_row]), config, env, "metadata", "METADATA_GUARDRAIL_RESULTS", schema=_configured_lakehouse_schema(config, env, "metadata"), mode="append")
        except Exception as exc:
            if not _is_missing_table_error(exc):
                raise
    return result

def _is_missing_table_error(exc: Exception) -> bool:
    text = str(exc).lower()
    patterns = ["not found", "table or view not found", "no such table", "cannot resolve", "missing"]
    return any(pattern in text for pattern in patterns)


def stop_if_failed(result) -> None:
    """Stop notebook execution when a guardrail result is blocking.

    Parameters
    ----------
    result : dict
        Direct schema, freshness, profile behavior, or DQ guardrail result.

    Raises
    ------
    SchemaDriftError
        If the resolved result has ``can_continue=False``.

    """
    resolved = (result or {}).get("result") if isinstance(result, dict) and "result" in result else result
    resolved = resolved or {}
    if bool(resolved.get("can_continue", True)):
        return
    status = resolved.get("status", "failed")
    detail = resolved.get("message") or resolved.get("summary") or "Guardrail blocked execution."
    raise SchemaDriftError(f"Guardrail blocked execution with status: {status}. {detail}")
