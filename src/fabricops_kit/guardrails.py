"""Lightweight schema and profile behavior guardrails for pipeline notebooks.

Use :func:`validate_schema`, :func:`enforce_freshness`,
:func:`enforce_profile_behavior`, and :func:`stop_if_failed` in production
pipeline notebooks. FabricOps enforces technical data-contract expectations
with simple freshness and load behavior choices.
"""

from __future__ import annotations

import json
import re
from datetime import date, datetime, timedelta
from decimal import Decimal


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
    Freshness is separate from profile behavior. ``load_behavior="skip"`` only
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


def _profile_watermark_bounds(profile, watermark_column: str | None) -> tuple[str, str]:
    normalized = _normalize_profile(profile) or {}
    if not watermark_column:
        return "", ""
    for column in normalized.get("columns", []) or []:
        if str(column.get("column_name") or "").lower() == str(watermark_column).lower():
            return _string_value(column.get("min_value")), _string_value(column.get("max_value"))
    return "", ""


def _latest_catalogue_behavior_profile_row(
    catalogue_df,
    *,
    dataset_name: str,
    table_name: str,
    profile_stage: str,
    load_behavior: str,
    watermark_column: str | None = None,
    exclude_run_id: str | None = None,
) -> dict | None:
    if catalogue_df is None:
        return None

    try:
        if hasattr(catalogue_df, "collect") and hasattr(catalogue_df, "columns"):
            from pyspark.sql import functions as F

            df = catalogue_df
            columns_by_lower = {str(column).lower(): column for column in df.columns}

            def catalogue_col(*names: str) -> str | None:
                for name in names:
                    if name in df.columns:
                        return name
                    if name.lower() in columns_by_lower:
                        return columns_by_lower[name.lower()]
                return None

            stage = str(profile_stage).lower()
            stage_roles = [stage, f"{stage}_profile"]
            if stage == "target":
                stage_roles.append("output_profile")

            dataset_col = catalogue_col("dataset_name")
            table_col = catalogue_col("table_name", "profiled_table_name")
            stage_col = catalogue_col("profile_stage", "evidence_role")
            behavior_col = catalogue_col("load_behavior")
            stability_status_col = catalogue_col("stability_status")
            profile_status_col = catalogue_col("profile_status")
            run_col = catalogue_col("profile_run_id", "run_id")
            time_col = catalogue_col("profiled_at", "run_timestamp", "created_at")
            column_col = catalogue_col("column_name")
            required = [dataset_col, table_col, stage_col, behavior_col, stability_status_col]
            if watermark_column:
                required.append(column_col)
            if any(column is None for column in required):
                return None

            filters = [
                F.col(dataset_col) == dataset_name,
                F.col(table_col) == table_name,
                F.lower(F.col(stage_col)).isin(stage_roles),
                F.lower(F.col(behavior_col)) == str(load_behavior).lower(),
                F.lower(F.col(stability_status_col)).isin("passed", "baseline_created"),
            ]
            if profile_status_col:
                filters.append(F.lower(F.col(profile_status_col)).isin("success", "successful"))
            if exclude_run_id and run_col:
                filters.append(F.col(run_col) != exclude_run_id)
            if watermark_column and column_col:
                filters.append(F.lower(F.col(column_col)) == str(watermark_column).lower())

            for condition in filters:
                df = df.filter(condition)
            order_columns = []
            if time_col:
                order_columns.append(F.col(time_col).desc())
            if run_col:
                order_columns.append(F.col(run_col).desc())
            if order_columns:
                df = df.orderBy(*order_columns)
            rows = df.limit(1).collect()
            return _row_to_dict(rows[0]) if rows else None

        rows = catalogue_df
        if isinstance(catalogue_df, dict):
            rows = [catalogue_df]
        candidates = []
        stage = str(profile_stage).lower()
        stage_roles = {stage, f"{stage}_profile"}
        if stage == "target":
            stage_roles.add("output_profile")
        for raw_row in rows or []:
            row = _row_to_dict(raw_row)
            if str(_catalogue_value(row, "dataset_name")) != dataset_name:
                continue
            if str(_catalogue_value(row, "table_name", "profiled_table_name")) != table_name:
                continue
            if str(_catalogue_value(row, "profile_stage", "evidence_role")).lower() not in stage_roles:
                continue
            if str(_catalogue_value(row, "load_behavior")).lower() != str(load_behavior).lower():
                continue
            if str(_catalogue_value(row, "stability_status")).lower() not in {"passed", "baseline_created"}:
                continue
            profile_status = _catalogue_value(row, "profile_status")
            if profile_status and str(profile_status).lower() not in {"success", "successful"}:
                continue
            if exclude_run_id and str(_catalogue_value(row, "profile_run_id", "run_id")) == str(exclude_run_id):
                continue
            if watermark_column and str(_catalogue_value(row, "column_name")).lower() != str(watermark_column).lower():
                continue
            candidates.append(row)
        if not candidates:
            return None
        candidates.sort(key=lambda row: (_string_value(_catalogue_value(row, "profiled_at", "run_timestamp", "created_at")), _string_value(_catalogue_value(row, "profile_run_id", "run_id"))), reverse=True)
        return candidates[0]
    except Exception as exc:
        if _is_missing_table_error(exc):
            return None
        raise


def enforce_profile_behavior(
    spark,
    dataframe,
    metadata_table: str,
    dataset_name: str,
    table_name: str,
    *,
    stage: str,
    run_id: str,
    load_behavior: str,
    watermark_column: str | None = None,
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    exclude_run_id: str | None = None,
    config=None,
    env: str | None = None,
    catalogue_df=None,
    current_profile=None,
) -> dict:
    """Enforce profile behavior guardrails for append, overwrite, or skip loads.

    Parameters
    ----------
    spark : Any
        Spark session used to read ``METADATA_DATA_CATALOGUE`` when
        ``catalogue_df`` is not supplied.
    dataframe : Any
        Spark DataFrame being checked.
    metadata_table : str
        Catalogue metadata table that stores profile evidence rows.
    dataset_name : str
        Governed dataset identifier used for previous-profile lookup.
    table_name : str
        Governed source or target table name used for previous-profile lookup.
    stage : str
        Pipeline stage used to keep source and target profiles independent.
    run_id : str
        Current pipeline run identifier.
    load_behavior : {"append", "overwrite", "skip"}
        Expected load behavior. ``append`` protects history, ``overwrite`` accepts
        rebuilt outputs as the new state, and ``skip`` disables only this
        guardrail.
    watermark_column : str, optional
        Business watermark column used by append behavior to compare current and
        previous minimum and maximum profile evidence.
    exclude_columns : list-like, optional
        Business or technical columns to exclude from the current profile.
    exclude_run_id : str, optional
        Run identifier to exclude from previous-profile lookup. Defaults to
        ``run_id``.
    config, env : object, str, optional
        Metadata route from ``00_env_config`` used to read the catalogue table via
        ``read_lakehouse_table`` when ``catalogue_df`` is not supplied.
    catalogue_df : DataFrame or iterable of mappings, optional
        Preloaded ``METADATA_DATA_CATALOGUE`` evidence. When provided, no
        metadata read is performed.
    current_profile : DataFrame or iterable of mappings, optional
        Current profile evidence that has already been computed for this table.
        When supplied, this function reuses it instead of profiling
        ``dataframe`` again.

    Returns
    -------
    dict
        Standard guardrail result with profile behavior status, continuation
        decision, and catalogue evidence fields for ``write_catalogue_evidence``.

    Notes
    -----
    This guardrail uses existing profile evidence: row count plus the configured
    watermark column's ``min_value`` and ``max_value``. Schema and DQ checks are
    enforced by their own guardrails.
    """
    behavior = str(load_behavior or "").lower().strip()
    if behavior not in {"append", "overwrite", "skip"}:
        raise ValueError("load_behavior must be one of: append, overwrite, skip")

    effective_exclude_columns = _guardrail_exclude_columns(exclude_columns)
    current_profile_df = current_profile
    if current_profile_df is None:
        from fabricops_kit.data_profiling import profile_dataframe

        current_profile_df = profile_dataframe(dataframe, table_name, exclude_columns=effective_exclude_columns, config=config)
    current_row_count = _profile_row_count(current_profile_df)
    current_min, current_max = _profile_watermark_bounds(current_profile_df, watermark_column)

    if catalogue_df is None and config is not None and env is not None:
        from fabricops_kit.fabric_input_output import _configured_lakehouse_schema, read_lakehouse_table

        try:
            catalogue_df = read_lakehouse_table(config, env, "metadata", metadata_table, schema=_configured_lakehouse_schema(config, env, "metadata"), spark_session=spark)
        except Exception as exc:
            if _is_missing_table_error(exc):
                catalogue_df = None
            else:
                raise

    baseline = None
    watermark_baseline = None
    if behavior == "append":
        baseline = _latest_catalogue_behavior_profile_row(
            catalogue_df,
            dataset_name=dataset_name,
            table_name=table_name,
            profile_stage=stage,
            load_behavior=behavior,
            exclude_run_id=exclude_run_id or run_id,
        )
        if watermark_column:
            watermark_baseline = _latest_catalogue_behavior_profile_row(
                catalogue_df,
                dataset_name=dataset_name,
                table_name=table_name,
                profile_stage=stage,
                load_behavior=behavior,
                watermark_column=watermark_column,
                exclude_run_id=exclude_run_id or run_id,
            )

    baseline_run_id = _string_value(_catalogue_value(baseline or {}, "profile_run_id", "run_id"))
    baseline_row_count_raw = _catalogue_value(baseline or {}, "row_count", "profiled_row_count")
    baseline_min = _string_value(_catalogue_value(watermark_baseline or {}, "min_value"))
    baseline_max = _string_value(_catalogue_value(watermark_baseline or {}, "max_value"))
    try:
        baseline_row_count = int(baseline_row_count_raw) if baseline_row_count_raw is not None else None
    except (TypeError, ValueError):
        baseline_row_count = None

    result = {
        "status": "passed",
        "can_continue": True,
        "check_type": "profile_behavior_guardrail",
        "stability_check_enabled": behavior != "skip",
        "load_behavior": behavior,
        "watermark_column": watermark_column or "",
        "row_count": current_row_count,
        "baseline_run_id": baseline_run_id,
        "baseline_row_count": baseline_row_count,
        "baseline_watermark_min_value": baseline_min,
        "baseline_watermark_max_value": baseline_max,
        "stability_status": "passed",
        "stability_can_continue": True,
        "stability_message": "Profile behavior guardrail passed.",
        "stability_difference_summary": "",
    }

    if behavior == "skip":
        message = "Profile behavior guardrail skipped; other guardrails still apply."
        result.update(status="skipped", stability_status="skipped", stability_message=message, message=message)
        return result

    if behavior == "overwrite":
        message = "Overwrite load behavior accepted current profile as the new state."
        result.update(stability_message=message, message=message)
        return result

    if baseline is None:
        message = "No previous accepted append profile was available; current profile establishes the baseline."
        result.update(status="baseline_created", stability_status="baseline_created", stability_message=message, message=message)
        return result

    differences = {}
    if baseline_row_count is not None and current_row_count is not None and current_row_count < baseline_row_count:
        differences["row_count"] = {"previous": baseline_row_count, "current": current_row_count, "rule": "append_row_count_must_not_decrease"}
    if watermark_column:
        if watermark_baseline is None:
            differences["watermark_comparison"] = {
                "status": "skipped",
                "column": watermark_column,
                "reason": "No previous accepted profile row was found for the configured watermark column.",
            }
        else:
            if baseline_min and current_min and _is_greater_than(current_min, baseline_min):
                differences["watermark_min"] = {"previous": baseline_min, "current": current_min, "column": watermark_column, "rule": "append_watermark_min_must_not_move_forward"}
            if baseline_max and current_max and _is_less_than(current_max, baseline_max):
                differences["watermark_max"] = {"previous": baseline_max, "current": current_max, "column": watermark_column, "rule": "append_watermark_max_must_not_move_backwards"}

    blocking_differences = {key: value for key, value in differences.items() if value.get("status") != "skipped"}
    if blocking_differences:
        message = "Append load behavior failed because existing history appears to have been removed or moved."
        result.update(
            status="failed",
            can_continue=False,
            stability_status="failed",
            stability_can_continue=False,
            stability_message=message,
            stability_difference_summary=json.dumps(differences, default=str, sort_keys=True),
            message=message,
        )
        return result

    if differences:
        result["stability_difference_summary"] = json.dumps(differences, default=str, sort_keys=True)
    result["message"] = result["stability_message"]
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
