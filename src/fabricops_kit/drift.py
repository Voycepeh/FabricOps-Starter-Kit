"""Lightweight schema, partition, and profile drift safeguards.

Use :func:`validate_schema`, :func:`monitor_data_changes`, and
:func:`stop_if_failed` in production pipeline notebooks. Users choose
intent-based presets while FabricOps handles profiling, baseline selection,
comparison, and enforcement mechanics internally.
"""

from __future__ import annotations

import json
import math
import re


class SchemaDriftError(Exception):
    """Raised when a schema check is configured to fail on drift.

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


_DEFAULT_PROFILE_DRIFT_POLICY = {
    "max_row_count_change_percent": 50,
    "max_null_percent_change_points": 20,
    "max_distinct_percent_change_points": 30,
    "warn_numeric_psi": 0.10,
    "block_numeric_psi": 0.25,
    "warn_categorical_distance": 0.10,
    "block_categorical_distance": 0.25,
    "fail_on_missing_column": True,
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


def _baseline_distribution_args(profile) -> dict[str, dict[str, list[float] | list[str]]]:
    normalized = _normalize_profile(profile) or {}
    numeric_edges: dict[str, list[float]] = {}
    categorical_values: dict[str, list[str]] = {}
    for column in normalized.get("columns", []):
        distribution = column.get("distribution") or {}
        column_name = str(column.get("column_name"))
        if column.get("distribution_type") == "numeric" and distribution.get("bin_edges"):
            numeric_edges[column_name] = [float(value) for value in distribution.get("bin_edges", [])]
        elif column.get("distribution_type") == "categorical" and distribution.get("category_counts") is not None:
            categorical_values[column_name] = [str(value) for value in distribution.get("category_counts", {}).keys()]
    return {"numeric_edges": numeric_edges, "categorical_values": categorical_values}

def _numeric_psi(current_distribution: dict, baseline_distribution: dict) -> float | None:
    current_edges = [float(value) for value in current_distribution.get("bin_edges", [])]
    baseline_edges = [float(value) for value in baseline_distribution.get("bin_edges", [])]
    if current_edges != baseline_edges:
        return None
    current_counts = [float(value or 0) for value in current_distribution.get("bin_counts", [])]
    baseline_counts = [float(value or 0) for value in baseline_distribution.get("bin_counts", [])]
    if len(current_counts) != len(baseline_counts) or not current_counts:
        return None
    def proportions(counts: list[float], epsilon: float = 1e-9) -> list[float]:
        total = float(sum(float(count or 0) for count in counts))
        if total <= 0:
            return [epsilon for _ in counts]
        return [max(float(count or 0) / total, epsilon) for count in counts]

    current_props = proportions(current_counts)
    baseline_props = proportions(baseline_counts)
    return float(sum((current - baseline) * math.log(current / baseline) for current, baseline in zip(current_props, baseline_props)))


def _categorical_distance(current_distribution: dict, baseline_distribution: dict) -> tuple[float, list[str]]:
    current_counts = {str(k): float(v or 0) for k, v in (current_distribution.get("category_counts") or {}).items()}
    baseline_counts = {str(k): float(v or 0) for k, v in (baseline_distribution.get("category_counts") or {}).items()}
    current_counts["__other__"] = float(current_distribution.get("other_count") or 0)
    baseline_counts["__other__"] = float(baseline_distribution.get("other_count") or 0)
    current_total = sum(current_counts.values()) or 1.0
    baseline_total = sum(baseline_counts.values()) or 1.0
    categories = sorted(set(current_counts) | set(baseline_counts))
    distance = 0.5 * sum(abs((current_counts.get(category, 0.0) / current_total) - (baseline_counts.get(category, 0.0) / baseline_total)) for category in categories)
    explicit_new = set(current_distribution.get("new_categories") or [])
    compared_new = {category for category in set(current_counts) - set(baseline_counts) if category != "__other__"}
    new_categories = sorted(str(category) for category in explicit_new | compared_new)
    return float(distance), new_categories


def _check_profile_drift(current_profile: dict, baseline_profile: dict | None = None, policy: dict | None = None) -> dict:
    """Compare profile metrics against a baseline profile and drift thresholds.

    Parameters
    ----------
    current_profile : dict or Spark DataFrame or list[dict]
        Current profile payload. Spark profile DataFrames and collected profile
        rows are normalized into the existing dictionary shape.
    baseline_profile : dict or Spark DataFrame or list[dict] or None, optional
        Previous successful profile for the same dataset, table, and source or
        target stage. ``None`` returns a non-blocking ``no_baseline`` result.
    policy : dict, optional
        Threshold overrides. Unspecified values fall back to
        :func:`monitor_data_changes`.

    Returns
    -------
    dict
        Result with ``status``, ``can_continue``, ``checks``, and ``message``.
        Status is ``passed``, ``warning``, ``failed``, or ``no_baseline``.
    """
    active = {**_DEFAULT_PROFILE_DRIFT_POLICY, **(policy or {})}
    current = _normalize_profile(current_profile)
    baseline = _normalize_profile(baseline_profile)
    if baseline is None:
        return {"status": "no_baseline", "can_continue": True, "checks": [], "message": "No baseline profile provided."}
    if current is None:
        raise ValueError("current_profile must contain at least one profile row.")

    checks = []
    blocking = False
    warning = False
    b_row = float(baseline.get("row_count") or 0)
    c_row = float(current.get("row_count") or 0)
    row_delta_pct = 0.0 if b_row == 0 else abs(c_row - b_row) / b_row * 100.0
    row_ok = row_delta_pct <= float(active["max_row_count_change_percent"])
    checks.append({"check": "row_count_change_percent", "passed": row_ok, "value": row_delta_pct, "threshold": active["max_row_count_change_percent"], "status": "passed" if row_ok else "failed"})
    blocking = blocking or (not row_ok)

    b_cols = {c.get("column_name"): c for c in baseline.get("columns", [])}
    c_cols = {c.get("column_name"): c for c in current.get("columns", [])}
    for col in sorted(set(b_cols) - set(c_cols)):
        passed = not bool(active["fail_on_missing_column"])
        status = "passed" if passed else "failed"
        checks.append({"check": "missing_column", "column": col, "passed": passed, "status": status})
        blocking = blocking or (not passed)

    for col in sorted(set(b_cols).intersection(c_cols)):
        b = b_cols[col]
        c = c_cols[col]
        if "null_pct" in b and "null_pct" in c:
            delta = abs(float(c.get("null_pct") or 0) - float(b.get("null_pct") or 0))
            passed = delta <= float(active["max_null_percent_change_points"])
            checks.append({"check": "null_percent_change_points", "column": col, "passed": passed, "value": delta, "threshold": active["max_null_percent_change_points"], "status": "passed" if passed else "failed"})
            blocking = blocking or (not passed)
        if "distinct_pct" in b and "distinct_pct" in c:
            delta = abs(float(c.get("distinct_pct") or 0) - float(b.get("distinct_pct") or 0))
            passed = delta <= float(active["max_distinct_percent_change_points"])
            checks.append({"check": "distinct_percent_change_points", "column": col, "passed": passed, "value": delta, "threshold": active["max_distinct_percent_change_points"], "status": "passed" if passed else "failed"})
            blocking = blocking or (not passed)
        if b.get("min_value") != c.get("min_value"):
            checks.append({"check": "min_changed", "column": col, "passed": True, "status": "passed", "baseline": b.get("min_value"), "current": c.get("min_value")})
        if b.get("max_value") != c.get("max_value"):
            checks.append({"check": "max_changed", "column": col, "passed": True, "status": "passed", "baseline": b.get("max_value"), "current": c.get("max_value")})

        b_distribution = b.get("distribution") or {}
        c_distribution = c.get("distribution") or {}
        if b.get("distribution_type") == "numeric" and c.get("distribution_type") == "numeric" and b_distribution and c_distribution:
            value = _numeric_psi(c_distribution, b_distribution)
            if value is not None:
                status = "failed" if value >= float(active["block_numeric_psi"]) else "warning" if value >= float(active["warn_numeric_psi"]) else "passed"
                checks.append({"check": "numeric_psi", "column": col, "value": value, "warning_threshold": active["warn_numeric_psi"], "blocking_threshold": active["block_numeric_psi"], "status": status, "passed": status != "failed"})
                warning = warning or status == "warning"
                blocking = blocking or status == "failed"
        if b.get("distribution_type") == "categorical" and c.get("distribution_type") == "categorical" and b_distribution and c_distribution:
            value, new_categories = _categorical_distance(c_distribution, b_distribution)
            status = "failed" if value >= float(active["block_categorical_distance"]) else "warning" if value >= float(active["warn_categorical_distance"]) else "passed"
            checks.append({"check": "categorical_distance", "column": col, "value": value, "warning_threshold": active["warn_categorical_distance"], "blocking_threshold": active["block_categorical_distance"], "status": status, "passed": status != "failed", "new_categories": new_categories})
            warning = warning or status == "warning"
            blocking = blocking or status == "failed"

    status = "failed" if blocking else "warning" if warning else "passed"
    return {"status": status, "can_continue": not blocking, "checks": checks, "message": "Profile drift check completed."}


def _is_missing_table_error(exc: Exception) -> bool:
    text = str(exc).lower()
    patterns = ["not found", "table or view not found", "no such table", "cannot resolve", "missing"]
    return any(pattern in text for pattern in patterns)


def _load_latest_profile(spark, metadata_table: str, dataset_name: str, table_name: str, profile_stage: str, exclude_run_id: str | None = None, baseline_mode: str = "latest_successful") -> dict | None:
    """Load an explicit profile-drift baseline from profile metadata rows.

    Parameters
    ----------
    spark : Any
        Spark session used to query the existing profile metadata table.
    metadata_table : str
        Existing profile metadata table, such as
        ``METADATA_DATA_CATALOGUE``.
    dataset_name : str
        Dataset name to match.
    table_name : str
        Profiled source or target table name to match.
    profile_stage : {"source", "target"}
        Profile stage to match. Existing ``EVIDENCE_ROLE`` values such as
        ``source_profile`` and ``output_profile`` are supported.
    exclude_run_id : str, optional
        Current run identifier to exclude from baseline selection.
    baseline_mode : {"latest_successful", "approved"}, default="latest_successful"
        Baseline selection mode. ``latest_successful`` selects the latest
        previous row marked ``PROFILE_STATUS = successful`` when that field is
        present. ``approved`` selects rows marked ``BASELINE_STATUS = approved``
        and never falls back to latest previous evidence.

    Returns
    -------
    dict or None
        Normalized profile dictionary for the latest matching previous profile,
        or ``None`` when no baseline exists.

    Notes
    -----
    This helper reuses the existing profile metadata rows. It does not create a
    separate data-drift table or approval workflow.
    """
    mode = str(baseline_mode or "latest_successful").lower()
    if mode not in {"latest_successful", "approved"}:
        raise ValueError("baseline_mode must be one of: latest_successful, approved")
    try:
        df = spark.table(metadata_table)
    except Exception as exc:
        if _is_missing_table_error(exc):
            return None
        raise

    try:
        from pyspark.sql import functions as F

        stage = str(profile_stage).lower()
        stage_roles = [stage, f"{stage}_profile"]
        if stage == "target":
            stage_roles.append("output_profile")
        columns_by_lower = {str(column).lower(): column for column in df.columns}

        def catalogue_col(*names: str) -> str | None:
            for name in names:
                if name in df.columns:
                    return name
                if name.lower() in columns_by_lower:
                    return columns_by_lower[name.lower()]
            return None

        filters = []
        dataset_col = catalogue_col("dataset_name", "DATASET_NAME")
        table_col = catalogue_col("table_name", "PROFILED_TABLE_NAME", "TABLE_NAME")
        stage_col = catalogue_col("profile_stage", "PROFILE_STAGE", "evidence_role", "EVIDENCE_ROLE")
        baseline_col = catalogue_col("baseline_status", "BASELINE_STATUS")
        profile_status_col = catalogue_col("profile_status", "PROFILE_STATUS")
        profile_run_col = catalogue_col("profile_run_id", "PROFILE_RUN_ID")
        run_timestamp_col = catalogue_col("run_timestamp", "RUN_TIMESTAMP", "profiled_at")
        if dataset_col:
            filters.append(F.col(dataset_col) == dataset_name)
        if table_col:
            filters.append(F.col(table_col) == table_name)
        if stage_col:
            filters.append(F.lower(F.col(stage_col)).isin(stage_roles))
        if mode == "approved":
            if not baseline_col:
                return None
            filters.append(F.lower(F.col(baseline_col)) == "approved")
        elif profile_status_col:
            filters.append(F.lower(F.col(profile_status_col)).isin("success", "successful"))
        if exclude_run_id and profile_run_col:
            filters.append(F.col(profile_run_col) != exclude_run_id)
        for condition in filters:
            df = df.filter(condition)
        if not profile_run_col:
            rows = df.collect() if hasattr(df, "collect") else []
            return _normalize_profile(rows)
        order_columns = []
        if run_timestamp_col:
            order_columns.append(F.col(run_timestamp_col).desc())
        order_columns.append(F.col(profile_run_col).desc())
        latest_runs = df.orderBy(*order_columns).select(profile_run_col).limit(1).collect()
        if not latest_runs:
            return None
        latest_run_id = latest_runs[0][profile_run_col]
        rows = df.filter(F.col(profile_run_col) == latest_run_id).collect()
        return _normalize_profile(rows)
    except Exception as exc:
        if _is_missing_table_error(exc):
            return None
        raise


_DATA_CHANGE_PRESETS = {
    "changing_data": {
        "baseline_mode": "latest_successful",
        "policy": {
            "max_row_count_change_percent": 50,
            "max_null_percent_change_points": 20,
            "max_distinct_percent_change_points": 30,
            "warn_numeric_psi": 0.10,
            "block_numeric_psi": 0.25,
            "warn_categorical_distance": 0.10,
            "block_categorical_distance": 0.25,
            "fail_on_missing_column": True,
        },
        "monitor_only": False,
    },
    "fixed_data": {
        "baseline_mode": "approved",
        "policy": {
            "max_row_count_change_percent": 0,
            "max_null_percent_change_points": 0,
            "max_distinct_percent_change_points": 0,
            "warn_numeric_psi": 0.01,
            "block_numeric_psi": 0.10,
            "warn_categorical_distance": 0.01,
            "block_categorical_distance": 0.10,
            "fail_on_missing_column": True,
        },
        "monitor_only": False,
    },
    "monitor_changing_data": {
        "baseline_mode": "latest_successful",
        "policy": {
            "max_row_count_change_percent": 50,
            "max_null_percent_change_points": 20,
            "max_distinct_percent_change_points": 30,
            "warn_numeric_psi": 0.10,
            "block_numeric_psi": 0.25,
            "warn_categorical_distance": 0.10,
            "block_categorical_distance": 0.25,
            "fail_on_missing_column": True,
        },
        "monitor_only": True,
    },
    "monitor_fixed_data": {
        "baseline_mode": "approved",
        "policy": {
            "max_row_count_change_percent": 0,
            "max_null_percent_change_points": 0,
            "max_distinct_percent_change_points": 0,
            "warn_numeric_psi": 0.01,
            "block_numeric_psi": 0.10,
            "warn_categorical_distance": 0.01,
            "block_categorical_distance": 0.10,
            "fail_on_missing_column": True,
        },
        "monitor_only": True,
    },
}


def _data_change_preset_config(preset: str, policy_overrides: dict | None = None) -> dict:
    normalized_preset = str(preset).lower()
    if normalized_preset not in _DATA_CHANGE_PRESETS:
        raise ValueError("preset must be one of: changing_data, fixed_data, monitor_changing_data, monitor_fixed_data")
    base = _DATA_CHANGE_PRESETS[normalized_preset]
    overrides = policy_overrides or {}
    unsupported = sorted(set(overrides) - set(base["policy"]))
    if unsupported:
        allowed = ", ".join(sorted(base["policy"]))
        invalid = ", ".join(unsupported)
        raise ValueError(f"policy_overrides may only adjust threshold policy keys. Invalid: {invalid}. Allowed: {allowed}")
    return {
        "preset": normalized_preset,
        "baseline_mode": base["baseline_mode"],
        "policy": {**base["policy"], **overrides},
        "monitor_only": bool(base["monitor_only"]),
    }


def monitor_data_changes(
    spark,
    dataframe,
    metadata_table: str,
    dataset_name: str,
    table_name: str,
    *,
    stage: str,
    preset: str = "changing_data",
    exclude_run_id: str | None = None,
    distribution_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    policy_overrides: dict | None = None,
) -> dict:
    """Profile a dataframe and compare it with the baseline selected by a preset.

    Parameters
    ----------
    spark : Any
        Spark session used to load existing profile metadata.
    dataframe : Any
        Spark DataFrame to profile.
    metadata_table : str
        Existing metadata table containing profile evidence rows.
    dataset_name : str
        Dataset identifier used to select matching baseline profiles.
    table_name : str
        Source or target table name used to select matching baseline profiles.
    stage : {"source", "target"}
        Pipeline stage being monitored. Source and target baselines are selected
        independently.
    preset : {"changing_data", "fixed_data", "monitor_changing_data", "monitor_fixed_data"}, default="changing_data"
        Data-change monitoring intent. ``changing_data`` compares with the
        latest successful profile and may block, ``fixed_data`` compares with
        an approved baseline and may block, ``monitor_changing_data`` compares
        with the latest successful profile without blocking, and
        ``monitor_fixed_data`` compares with an approved baseline without
        blocking. Presets determine baseline and enforcement behavior;
        ``policy_overrides`` adjusts thresholds only.
    exclude_run_id : str, optional
        Current run identifier to exclude from baseline lookup.
    distribution_columns : list[str] or set[str] or tuple[str, ...], optional
        Optional allow-list of columns for distribution comparisons.
    policy_overrides : dict, optional
        Threshold policy overrides merged with the selected preset defaults.
        Overrides may adjust thresholds only; presets retain control of
        baseline selection and blocking behaviour.

    Returns
    -------
    dict
        Wrapper containing ``profile`` for the current profile, ``baseline`` for
        the selected baseline profile, and ``result`` for the drift decision.

    Notes
    -----
    Users choose intent through presets. FabricOps handles profiling, baseline
    selection, comparison, and enforcement mechanics internally.
    """
    from fabricops_kit.data_profiling import profile_dataframe

    config = _data_change_preset_config(preset, policy_overrides)
    baseline_profile = _load_latest_profile(
        spark,
        metadata_table=metadata_table,
        dataset_name=dataset_name,
        table_name=table_name,
        profile_stage=stage,
        exclude_run_id=exclude_run_id,
        baseline_mode=config["baseline_mode"],
    )
    baseline_distribution_args = _baseline_distribution_args(baseline_profile)
    current_profile_df = profile_dataframe(
        dataframe,
        table_name,
        include_distributions=True,
        distribution_columns=distribution_columns,
        distribution_bin_edges=baseline_distribution_args["numeric_edges"],
        categorical_categories=baseline_distribution_args["categorical_values"],
    )
    current_profile = _normalize_profile(current_profile_df)
    result = _check_profile_drift(current_profile, baseline_profile, policy=config["policy"])
    if config["monitor_only"] and not bool(result.get("can_continue", True)):
        original_status = result.get("status")
        result = {**result, "can_continue": True, "status": "warning", "monitor_only": True, "original_status": original_status}
        result["message"] = (
            "Monitor-only data-change check observed blocking drift without stopping execution. "
            f"{result.get('message', '')}"
        ).strip()
    result = {**result, "preset": config["preset"], "baseline_mode": config["baseline_mode"], "policy": config["policy"]}
    return {"profile": current_profile_df, "profile_payload": current_profile, "baseline": baseline_profile, "result": result}


def stop_if_failed(result) -> None:
    """Stop notebook execution when a guardrail result is blocking.

    Parameters
    ----------
    result : dict
        Direct schema result, direct data-change result, or the wrapper returned
        by :func:`monitor_data_changes`.

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
