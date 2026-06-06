"""Lightweight schema, partition, and profile drift safeguards.

Use :func:`validate_schema`, :func:`monitor_data_changes`, and
:func:`stop_if_failed` in production pipeline notebooks. Users choose
intent-based presets while FabricOps handles profiling, baseline selection,
comparison, and enforcement mechanics internally.
"""

from __future__ import annotations

from datetime import datetime, timezone
import math
import re
import warnings


class SchemaDriftError(Exception):
    """Raised when a schema check is configured to fail on drift.

    Notes
    -----
    This exception is shared by schema-check workflows so notebook callers
    have one failure type to catch when they choose fail-fast behavior.
    """


class UnsupportedDataFrameEngineError(ValueError):
    """Raised when dataframe engine detection cannot resolve pandas or Spark."""


def _detect_dataframe_engine(df) -> str:
    """Detect whether a dataframe is pandas or Spark.

    Parameters
    ----------
    df : Any
        Dataframe-like object to inspect.

    Returns
    -------
    str
        Either ``"pandas"`` or ``"spark"``.

    Raises
    ------
    UnsupportedDataFrameEngineError
        If the object is not recognized as pandas or Spark dataframe.
    """
    mod = str(type(df).__module__)
    if mod.startswith("pandas"):
        return "pandas"
    if mod.startswith("pyspark") or hasattr(df, "schema"):
        return "spark"
    raise UnsupportedDataFrameEngineError(f"Unsupported dataframe type: {type(df)!r}")


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


def _check_schema(
    df,
    expected_columns: dict[str, str],
    *,
    allow_extra_columns: bool = False,
    check_types: bool = True,
    action: str = "fail",
) -> dict:
    """Check dataframe columns and datatypes against local expectations.

    Parameters
    ----------
    df : Any
        Spark, pandas, or dataframe-like object with ``schema`` or ``columns``
        metadata. Spark ``schema.fields`` entries are compared by ``name`` and
        ``dataType``.
    expected_columns : dict[str, str]
        Mapping of expected column names to expected datatype strings, such as
        ``{"customer_id": "bigint", "amount": "decimal(18,2)"}``.
    allow_extra_columns : bool, default=False
        When false, columns not listed in ``expected_columns`` are reported as
        unexpected.
    check_types : bool, default=True
        When true, compare actual and expected datatypes after minimal internal
        normalization of common Spark datatype representations.
    action : {"observe", "warn", "fail"}, default="fail"
        Enforcement behavior when the check does not pass. ``observe`` only
        returns the result, ``warn`` emits a Python warning and returns the
        result, and ``fail`` raises :class:`SchemaDriftError`.

    Returns
    -------
    dict
        Small result dictionary containing pass/fail status, missing columns,
        unexpected columns, datatype mismatches, and a concise summary.

    Raises
    ------
    ValueError
        If ``action`` is not one of ``observe``, ``warn``, or ``fail``.
    SchemaDriftError
        If the schema does not pass and ``action="fail"``.

    Notes
    -----
    This helper intentionally does not check nullability, column ordering,
    schema approvals, contract versions, metadata tables, or evidence
    persistence. Define expected schemas directly in the notebook or caller
    that owns the pipeline-specific expectation.
    """
    normalized_action = str(action).lower()
    if normalized_action not in {"observe", "warn", "fail"}:
        raise ValueError("action must be one of: observe, warn, fail")

    actual_columns, actual_types = _actual_schema(df)
    actual_set = set(actual_columns)
    expected_names = [str(column) for column in expected_columns]
    expected_set = set(expected_names)

    missing_columns = [column for column in expected_names if column not in actual_set]
    unexpected_columns = [] if allow_extra_columns else [column for column in actual_columns if column not in expected_set]

    datatype_mismatches = []
    if check_types:
        for column, expected_type in expected_columns.items():
            column_name = str(column)
            if column_name in actual_set and column_name in actual_types:
                expected = _normalize_datatype(expected_type)
                actual = actual_types[column_name]
                if actual != expected:
                    datatype_mismatches.append({"column": column_name, "expected": expected, "actual": actual})

    passed = not missing_columns and not unexpected_columns and not datatype_mismatches
    result = {
        "passed": passed,
        "status": "passed" if passed else "failed",
        "missing_columns": missing_columns,
        "unexpected_columns": unexpected_columns,
        "datatype_mismatches": datatype_mismatches,
        "summary": (
            "Schema check passed."
            if passed
            else f"Schema check failed: {len(missing_columns)} missing, {len(unexpected_columns)} unexpected, {len(datatype_mismatches)} datatype mismatch(es)."
        ),
    }

    if passed or normalized_action == "observe":
        return result
    if normalized_action == "warn":
        warnings.warn(result["summary"], UserWarning, stacklevel=2)
        return result
    raise SchemaDriftError(result["summary"])


_SCHEMA_PRESETS = {
    "strict": {"allow_extra_columns": False, "action": "observe"},
    "allow_new_columns": {"allow_extra_columns": True, "action": "observe"},
    "monitor_only": {"allow_extra_columns": False, "action": "observe"},
}


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

    low_level = _check_schema(
        dataframe,
        expected_schema,
        allow_extra_columns=_SCHEMA_PRESETS[normalized_preset]["allow_extra_columns"],
        check_types=True,
        action="observe",
    )
    checks = []
    for column in low_level.get("missing_columns", []):
        checks.append({"check": "missing_column", "column": column, "status": "failed", "passed": False})
    for mismatch in low_level.get("datatype_mismatches", []):
        checks.append({"check": "datatype_mismatch", **mismatch, "status": "failed", "passed": False})
    actual_unexpected = [column for column in _actual_schema(dataframe)[0] if str(column) not in {str(c) for c in expected_schema}]
    for column in actual_unexpected:
        checks.append({"check": "unexpected_column", "column": column, "status": "warning" if normalized_preset == "allow_new_columns" else "failed", "passed": normalized_preset == "allow_new_columns"})

    blocking = bool(low_level.get("missing_columns") or low_level.get("datatype_mismatches"))
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
        else f"Schema validation {status}: {len(low_level.get('missing_columns', []))} missing, {len(actual_unexpected)} unexpected, {len(low_level.get('datatype_mismatches', []))} datatype mismatch(es)."
    )
    return {
        "status": status,
        "can_continue": can_continue,
        "checks": checks,
        "message": message,
        "missing_columns": low_level.get("missing_columns", []),
        "unexpected_columns": actual_unexpected,
        "datatype_mismatches": low_level.get("datatype_mismatches", []),
        "preset": normalized_preset,
    }


# --- merged from drift_checkers.py ---


import json

from fabricops_kit._utils import _to_jsonable


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_spark_collect(df):
    if df is None:
        return []
    if hasattr(df, "collect"):
        return df.collect()
    return []

def _is_missing_table_error(exc: Exception) -> bool:
    text = str(exc).lower()
    patterns = ["not found", "table or view not found", "no such table", "cannot resolve", "missing"]
    return any(p in text for p in patterns)


def _json_dumps(value) -> str:
    return json.dumps(_to_jsonable(value), sort_keys=True)


def _write_metadata_rows(spark, metadata_table: str, records: list[dict], mode: str = "append") -> bool:
    if not records:
        return False
    metadata_df = spark.createDataFrame(records)
    metadata_df.write.mode(mode).saveAsTable(metadata_table)
    return True


def _check_partition_drift(df, dataset_name: str, table_name: str, partition_column: str, business_keys: list[str] | None = None, watermark_column: str | None = None, baseline_snapshot: list[dict] | dict | None = None, policy: dict | None = None, run_id: str | None = None, engine: str = "spark") -> dict:
    """Check partition-level drift using keys, partitions, and optional watermark baselines.
    
        Parameters
        ----------
        df : Any
            Value used by this callable.
        dataset_name : Any
            Value used by this callable.
        table_name : Any
            Value used by this callable.
        partition_column : Any
            Value used by this callable.
        business_keys : Any
            Value used by this callable.
        watermark_column : Any
            Value used by this callable.
        baseline_snapshot : Any
            Value used by this callable.
        policy : Any
            Value used by this callable.
        run_id : Any
            Value used by this callable.
        engine : Any
            Value used by this callable.
    
        Returns
        -------
        dict
            Structured output produced by this callable.
    """
    keys = business_keys or []
    if not keys:
        raise ValueError("business_keys must contain at least one column for partition drift checks.")
    current_snapshot = _build_partition_snapshot(
        df,
        dataset_name=dataset_name,
        table_name=table_name,
        partition_column=partition_column,
        business_keys=keys,
        watermark_column=watermark_column,
        run_id=run_id,
        engine=engine,
    )
    if baseline_snapshot is None:
        return {
            "dataset_name": dataset_name,
            "table_name": table_name,
            "status": "no_baseline",
            "can_continue": True,
            "current_snapshot": current_snapshot,
            "baseline_snapshot": None,
            "comparison": None,
            "message": "No baseline partition snapshot found; current snapshot captured as first observation.",
        }

    baseline_rows = baseline_snapshot if isinstance(baseline_snapshot, list) else [baseline_snapshot]
    comparison = _compare_partition_snapshots(baseline_rows, current_snapshot, policy=policy or _default_incremental_safety_policy())
    status = str(comparison.get("status", "passed"))
    return {
        "dataset_name": dataset_name,
        "table_name": table_name,
        "status": status,
        "can_continue": bool(comparison.get("can_continue", True)),
        "current_snapshot": current_snapshot,
        "baseline_snapshot": baseline_rows,
        "comparison": comparison,
        "message": "Partition drift check completed.",
    }


def _build_and_write_partition_snapshot(spark, df, dataset_name: str, table_name: str, metadata_table: str, partition_column: str, business_keys: list[str] | None = None, watermark_column: str | None = None, run_id: str | None = None, mode: str = "append", engine: str = "spark") -> dict:
    """Build a partition snapshot and persist it to the metadata table.

    Parameters
    ----------
    spark : Any
        Spark session used for metadata writes.
    df : Any
        Source dataframe used to derive partition statistics.
    dataset_name : str
        Dataset identifier recorded in metadata.
    table_name : str
        Table identifier recorded in metadata.
    metadata_table : str
        Destination table for partition snapshot records.
    partition_column : str
        Partition column used to group snapshot rows.
    business_keys : list[str] | None, default=None
        Optional business-key columns used for key-level metrics.
    watermark_column : str | None, default=None
        Optional watermark column captured in the snapshot.
    run_id : str | None, default=None
        Optional run identifier attached to metadata rows.
    mode : str, default=\"append\"
        Spark write mode.
    engine : str, default=\"spark\"
        Engine used when building the partition snapshot.

    Returns
    -------
    dict
        Partition snapshot payload that was converted and written as metadata records.
    """
    keys = business_keys or []
    if not keys:
        raise ValueError("business_keys must contain at least one column for partition snapshots.")
    snapshot = _build_partition_snapshot(
        df,
        dataset_name=dataset_name,
        table_name=table_name,
        partition_column=partition_column,
        business_keys=keys,
        watermark_column=watermark_column,
        run_id=run_id,
        engine=engine,
    )
    records = [
        {
            "run_id": run_id,
            "dataset_name": dataset_name,
            "table_name": table_name,
            "snapshot_type": "partition",
            "partition_column": partition_column,
            "business_keys_json": _json_dumps(keys),
            "watermark_column": watermark_column,
            "partition_snapshot_json": _json_dumps(snapshot),
            "created_at": _utc_now_iso(),
        }
    ]
    written = _write_metadata_rows(spark, metadata_table=metadata_table, records=records, mode=mode)
    return {"snapshot": snapshot, "records": records, "metadata_table": metadata_table, "written": written}


def _load_latest_partition_snapshot(spark, metadata_table: str, dataset_name: str, table_name: str) -> list[dict] | dict | None:
    """Load the most recent partition snapshot for a dataset/table pair.

    Parameters
    ----------
    spark : Any
        Spark session used to query metadata.
    metadata_table : str
        Metadata table containing partition snapshot rows.
    dataset_name : str
        Dataset identifier to filter.
    table_name : str
        Table identifier to filter.

    Returns
    -------
    list[dict] | dict | None
        Latest partition snapshot payload, or ``None`` when no baseline is available.
    """
    try:
        df = spark.table(metadata_table)
        if hasattr(df, "filter") and hasattr(df, "orderBy") and hasattr(df, "limit"):
            from pyspark.sql import functions as F

            df = (
                df.filter(
                    (F.col("dataset_name") == dataset_name)
                    & (F.col("table_name") == table_name)
                    & (F.col("snapshot_type") == "partition")
                )
                .orderBy(F.col("created_at").desc(), F.col("run_id").desc())
                .limit(1)
            )
            rows = _safe_spark_collect(df)
        else:
            rows = _safe_spark_collect(df)
    except Exception as exc:
        if _is_missing_table_error(exc):
            return None
        raise
    matched = [r.asDict() if hasattr(r, "asDict") else dict(r) for r in rows if (r["dataset_name"] == dataset_name and r["table_name"] == table_name and r.get("snapshot_type") == "partition")]
    if not matched:
        return None
    matched.sort(key=lambda x: (str(x.get("created_at", "")), str(x.get("run_id", ""))), reverse=True)
    raw = matched[0].get("partition_snapshot_json")
    if not raw:
        return None
    return json.loads(raw)


def _default_profile_drift_policy() -> dict:
    """Return the lightweight default profile drift policy.

    Returns
    -------
    dict
        Thresholds used by :func:`monitor_data_changes` for row-count,
        null-percent, distinct-percent, numeric PSI, categorical distance, and
        missing-column enforcement.
    """
    return {
        "max_row_count_change_percent": 50,
        "max_null_percent_change_points": 20,
        "max_distinct_percent_change_points": 30,
        "warn_numeric_psi": 0.10,
        "block_numeric_psi": 0.25,
        "warn_categorical_distance": 0.10,
        "block_categorical_distance": 0.25,
        "fail_on_missing_column": True,
    }


def _row_get(row, *names):
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


def _parse_distribution(value):
    if value in (None, ""):
        return None
    if isinstance(value, dict):
        return value
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return None


def _normalize_profile(profile) -> dict | None:
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
        row_count = _row_get(first, "row_count", "ROW_COUNT", "PROFILED_ROW_COUNT")
        table_name = _row_get(first, "table_name", "TABLE_NAME", "PROFILED_TABLE_NAME")
        dataset_name = _row_get(first, "dataset_name", "DATASET_NAME")
        profile_stage = _row_get(first, "profile_stage", "PROFILE_STAGE", "EVIDENCE_ROLE")
        columns = []
        for row in rows:
            distribution_type = _row_get(row, "distribution_type", "DISTRIBUTION_TYPE")
            distribution = _parse_distribution(_row_get(row, "distribution", "DISTRIBUTION", "distribution_json", "DISTRIBUTION_JSON"))
            column = {
                "column_name": _row_get(row, "column_name", "COLUMN_NAME"),
                "data_type": _row_get(row, "data_type", "DATA_TYPE"),
                "row_count": _row_get(row, "row_count", "ROW_COUNT", "PROFILED_ROW_COUNT"),
                "null_count": _row_get(row, "null_count", "NULL_COUNT"),
                "null_pct": _row_get(row, "null_pct", "NULL_PCT", "null_percent", "NULL_PERCENT"),
                "distinct_count": _row_get(row, "distinct_count", "DISTINCT_COUNT"),
                "distinct_pct": _row_get(row, "distinct_pct", "DISTINCT_PCT", "distinct_percent", "DISTINCT_PERCENT"),
                "min_value": _row_get(row, "min_value", "MIN_VALUE"),
                "max_value": _row_get(row, "max_value", "MAX_VALUE"),
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
            "profile_status": _row_get(first, "profile_status", "PROFILE_STATUS"),
            "baseline_status": _row_get(first, "baseline_status", "BASELINE_STATUS"),
            "source_change_signal": _parse_distribution(_row_get(first, "source_change_signal", "SOURCE_CHANGE_SIGNAL_JSON")),
        }
    return profile


def _normalize_baseline_mode(baseline_mode: str) -> str:
    value = str(baseline_mode or "latest_successful").lower()
    if value not in {"latest_successful", "approved"}:
        raise ValueError("baseline_mode must be one of: latest_successful, approved")
    return value


def _extract_numeric_distribution_bin_edges(profile) -> dict[str, list[float]]:
    """Return numeric distribution bin edges from a profile payload.

    Parameters
    ----------
    profile : dict or Spark DataFrame or list[dict]
        Profile payload produced by :func:`fabricops_kit.profile_dataframe` or
        loaded from profile metadata.

    Returns
    -------
    dict[str, list[float]]
        Mapping of column names to numeric bin edges that can be passed back to
        ``profile_dataframe(..., distribution_bin_edges=...)`` for comparable
        current-run distributions.
    """
    normalized = _normalize_profile(profile) or {}
    edges: dict[str, list[float]] = {}
    for column in normalized.get("columns", []):
        distribution = column.get("distribution") or {}
        if column.get("distribution_type") == "numeric" and distribution.get("bin_edges"):
            edges[str(column.get("column_name"))] = [float(value) for value in distribution.get("bin_edges", [])]
    return edges


def _extract_categorical_distribution_categories(profile) -> dict[str, list[str]]:
    """Return categorical baseline vocabularies from a profile payload.

    Parameters
    ----------
    profile : dict or Spark DataFrame or list[dict]
        Profile payload produced by :func:`fabricops_kit.profile_dataframe` or
        loaded from profile metadata.

    Returns
    -------
    dict[str, list[str]]
        Mapping of column names to baseline category values that can be passed
        to ``profile_dataframe(..., categorical_categories=...)``.
    """
    normalized = _normalize_profile(profile) or {}
    categories: dict[str, list[str]] = {}
    for column in normalized.get("columns", []):
        distribution = column.get("distribution") or {}
        if column.get("distribution_type") == "categorical" and distribution.get("category_counts") is not None:
            categories[str(column.get("column_name"))] = [str(value) for value in distribution.get("category_counts", {}).keys()]
    return categories


def _profile_check_status(value: float, warning_threshold: float, blocking_threshold: float) -> tuple[str, bool, bool]:
    if value >= blocking_threshold:
        return "failed", False, True
    if value >= warning_threshold:
        return "warning", True, False
    return "passed", True, False


def _proportions(counts: list[int | float], epsilon: float = 1e-9) -> list[float]:
    total = float(sum(float(count or 0) for count in counts))
    if total <= 0:
        return [epsilon for _ in counts]
    return [max(float(count or 0) / total, epsilon) for count in counts]


def _numeric_psi(current_distribution: dict, baseline_distribution: dict) -> float | None:
    current_edges = [float(value) for value in current_distribution.get("bin_edges", [])]
    baseline_edges = [float(value) for value in baseline_distribution.get("bin_edges", [])]
    if current_edges != baseline_edges:
        return None
    current_counts = [float(value or 0) for value in current_distribution.get("bin_counts", [])]
    baseline_counts = [float(value or 0) for value in baseline_distribution.get("bin_counts", [])]
    if len(current_counts) != len(baseline_counts) or not current_counts:
        return None
    current_props = _proportions(current_counts)
    baseline_props = _proportions(baseline_counts)
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
    active = {**_default_profile_drift_policy(), **(policy or {})}
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
                status, passed, blocks = _profile_check_status(value, float(active["warn_numeric_psi"]), float(active["block_numeric_psi"]))
                checks.append({"check": "numeric_psi", "column": col, "value": value, "warning_threshold": active["warn_numeric_psi"], "blocking_threshold": active["block_numeric_psi"], "status": status, "passed": passed})
                warning = warning or status == "warning"
                blocking = blocking or blocks
        if b.get("distribution_type") == "categorical" and c.get("distribution_type") == "categorical" and b_distribution and c_distribution:
            value, new_categories = _categorical_distance(c_distribution, b_distribution)
            status, passed, blocks = _profile_check_status(value, float(active["warn_categorical_distance"]), float(active["block_categorical_distance"]))
            checks.append({"check": "categorical_distance", "column": col, "value": value, "warning_threshold": active["warn_categorical_distance"], "blocking_threshold": active["block_categorical_distance"], "status": status, "passed": passed, "new_categories": new_categories})
            warning = warning or status == "warning"
            blocking = blocking or blocks

    status = "failed" if blocking else "warning" if warning else "passed"
    return {"status": status, "can_continue": not blocking, "checks": checks, "message": "Profile drift check completed."}


def _assert_no_blocking_profile_drift(result: dict) -> None:
    """Raise when a profile drift result should block notebook execution.

    Parameters
    ----------
    result : dict
        Result returned by :func:`monitor_data_changes`.

    Raises
    ------
    SchemaDriftError
        If ``result["can_continue"]`` is false.
    """
    if not bool((result or {}).get("can_continue", True)):
        status = (result or {}).get("status", "failed")
        detail = (result or {}).get("message") or "Configured profile drift thresholds were exceeded."
        raise SchemaDriftError(f"Profile drift guardrail blocked execution with status: {status}. {detail}")


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
    mode = _normalize_baseline_mode(baseline_mode)
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
        filters = []
        if "DATASET_NAME" in df.columns:
            filters.append(F.col("DATASET_NAME") == dataset_name)
        if "PROFILED_TABLE_NAME" in df.columns:
            filters.append(F.col("PROFILED_TABLE_NAME") == table_name)
        elif "TABLE_NAME" in df.columns:
            filters.append(F.col("TABLE_NAME") == table_name)
        if "PROFILE_STAGE" in df.columns:
            filters.append(F.lower(F.col("PROFILE_STAGE")).isin(stage_roles))
        elif "EVIDENCE_ROLE" in df.columns:
            filters.append(F.lower(F.col("EVIDENCE_ROLE")).isin(stage_roles))
        if mode == "approved":
            if "BASELINE_STATUS" not in df.columns:
                return None
            filters.append(F.lower(F.col("BASELINE_STATUS")) == "approved")
        elif "PROFILE_STATUS" in df.columns:
            filters.append(F.lower(F.col("PROFILE_STATUS")) == "successful")
        if exclude_run_id and "PROFILE_RUN_ID" in df.columns:
            filters.append(F.col("PROFILE_RUN_ID") != exclude_run_id)
        for condition in filters:
            df = df.filter(condition)
        if "PROFILE_RUN_ID" not in df.columns:
            rows = _safe_spark_collect(df)
            return _normalize_profile(rows)
        order_columns = []
        if "RUN_TIMESTAMP" in df.columns:
            order_columns.append(F.col("RUN_TIMESTAMP").desc())
        order_columns.append(F.col("PROFILE_RUN_ID").desc())
        latest_runs = df.orderBy(*order_columns).select("PROFILE_RUN_ID").limit(1).collect()
        if not latest_runs:
            return None
        latest_run_id = latest_runs[0]["PROFILE_RUN_ID"]
        rows = df.filter(F.col("PROFILE_RUN_ID") == latest_run_id).collect()
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


def _as_monitor_only_result(result: dict) -> dict:
    if bool(result.get("can_continue", True)):
        return result
    converted = {**result, "can_continue": True, "status": "warning"}
    converted["message"] = f"Monitor-only data-change check observed blocking drift without stopping execution. {result.get('message', '')}".strip()
    converted["monitor_only"] = True
    converted["original_status"] = result.get("status")
    return converted


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
    current_profile_df = profile_dataframe(
        dataframe,
        table_name,
        include_distributions=True,
        distribution_columns=distribution_columns,
        distribution_bin_edges=_extract_numeric_distribution_bin_edges(baseline_profile),
        categorical_categories=_extract_categorical_distribution_categories(baseline_profile),
    )
    current_profile = _normalize_profile(current_profile_df)
    result = _check_profile_drift(current_profile, baseline_profile, policy=config["policy"])
    if config["monitor_only"]:
        result = _as_monitor_only_result(result)
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


def _summarize_drift_results(schema_drift_result: dict | None = None, partition_drift_result: dict | None = None, profile_drift_result: dict | None = None) -> dict:
    """Summarize schema, partition, and profile drift outcomes into one decision.
    
        Parameters
        ----------
        schema_drift_result : Any
            Value used by this callable.
        partition_drift_result : Any
            Value used by this callable.
        profile_drift_result : Any
            Value used by this callable.
    
        Returns
        -------
        dict
            Structured output produced by this callable.
    """
    results = {"schema": schema_drift_result, "partition": partition_drift_result, "profile": profile_drift_result}
    statuses = {k: (v or {}).get("status") for k, v in results.items()}
    failed = [k for k, v in results.items() if v and (v.get("status") == "failed" or not v.get("can_continue", True))]
    warnings = [k for k, v in results.items() if v and v.get("status") in {"warning", "no_baseline"}]
    if failed:
        overall = "failed"
    elif warnings and all((v or {}).get("status") == "no_baseline" for v in results.values() if v):
        overall = "no_baseline"
    elif warnings:
        overall = "warning"
    else:
        overall = "passed"
    can_continue = len(failed) == 0
    return {
        "status": overall,
        "can_continue": can_continue,
        "schema_status": statuses["schema"],
        "partition_status": statuses["partition"],
        "profile_status": statuses["profile"],
        "blocking_checks": failed,
        "warnings": warnings,
    }


def _build_drift_evidence_record(*, dataset_name: str, table_name: str, run_id: str | None, drift_type: str, result: dict, workspace_id: str | None = None, workspace_name: str | None = None, notebook_id: str | None = None, notebook_name: str | None = None) -> dict:
    """Build a metadata-ready drift evidence record for schema/profile/partition checks."""
    return {
        "dataset_name": dataset_name,
        "table_name": table_name,
        "run_id": run_id,
        "workspace_id": workspace_id,
        "workspace_name": workspace_name,
        "notebook_id": notebook_id,
        "notebook_name": notebook_name,
        "drift_type": drift_type,
        "status": str(result.get("status", "unknown")),
        "can_continue": bool(result.get("can_continue", True)),
        "summary_json": _json_dumps(result.get("summary", {})),
        "result_json": _json_dumps(result),
        "created_at": _utc_now_iso(),
    }


def _prepare_drift_baselines(
    *,
    current_profile: dict | None = None,
    baseline_profile: dict | None = None,
    baseline_schema_snapshot: dict | None = None,
    baseline_partition_snapshot: list[dict] | dict | None = None,
) -> dict:
    """Prepare baseline payloads for drift checks in notebook workflows.

    When baseline inputs are omitted, this helper safely falls back to
    ``None`` for schema/partition baselines and to ``current_profile`` for
    profile drift baselines. This keeps optional drift sections run-all safe
    while still enabling strict comparisons once persisted baselines exist.
    """
    return {
        "schema": baseline_schema_snapshot,
        "partition": baseline_partition_snapshot,
        "profile": baseline_profile if baseline_profile is not None else current_profile,
    }


# --- merged from incremental.py ---
"""Incremental partition safety snapshot and comparison helpers."""


from datetime import date, timedelta
from typing import Any


class IncrementalSafetyError(Exception):
    """Incrementalsafetyerror.

    Public class used by the framework API for `IncrementalSafetyError`.

    Examples
    --------
    >>> IncrementalSafetyError(... )
    """


def _default_incremental_safety_policy() -> dict:
    """Execute the `_default_incremental_safety_policy` workflow step in FabricOps.
    
        Use this callable at its corresponding stage of the pipeline contract
        (configuration, IO, profiling, quality, drift, lineage, or handover)
        to produce deterministic artifacts and validation evidence.
    
        Parameters
        ----------
        None
            This function does not require explicit parameters.
    
        Returns
        -------
        Any
            Function output used by downstream FabricOps workflow steps.
    
        Raises
        ------
        Exception
            Propagates validation, runtime, or storage errors from underlying
            operations when execution cannot continue safely.
    
        Notes
        -----
        Side effects may include metadata writes, quality evidence generation,
        or persisted drift/lineage/handover artifacts depending on the function.
    
        Examples
        --------
        >>> _default_incremental_safety_policy()
        """
    return {
        "block_on_historical_partition_change": True,
        "closed_partition_grace_days": 1,
        "allow_late_arriving_records": False,
        "lookback_partitions": 3,
        "allow_historical_changes": False,
        "require_approval_for_historical_changes": True,
        "approval_reference": None,
        "run_mode": "incremental",
    }


def _hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _build_partition_hash(partition_value: Any, row_count: int, business_key_count: int, max_watermark: Any, min_watermark: Any, business_key_hash: str) -> str:
    payload = "|".join(
        [
            str(partition_value),
            str(row_count),
            str(business_key_count),
            str(max_watermark),
            str(min_watermark),
            str(business_key_hash),
        ]
    )
    return _hash(payload)


def _build_pandas_partition_snapshot(df, *, dataset_name: str, table_name: str, partition_column: str, business_keys: list[str], watermark_column: str | None, run_id: str | None) -> list[dict]:
    generated_at = datetime.now(timezone.utc).isoformat()
    rows: list[dict] = []
    grouped = df.groupby(partition_column, dropna=False)
    for partition_value, group in grouped:
        row_count = int(group.shape[0])
        key_rows = group[business_keys].astype(str).drop_duplicates().apply(lambda r: "||".join(r.values.tolist()), axis=1)
        sorted_key_rows = sorted(key_rows.tolist())
        business_key_hash = _hash("##".join(sorted_key_rows))
        business_key_count = int(len(sorted_key_rows))

        max_watermark = min_watermark = None
        if watermark_column:
            max_watermark = _to_jsonable(group[watermark_column].max())
            min_watermark = _to_jsonable(group[watermark_column].min())

        partition_hash = _build_partition_hash(partition_value, row_count, business_key_count, max_watermark, min_watermark, business_key_hash)
        rows.append(
            {
                "dataset_name": str(dataset_name),
                "table_name": str(table_name),
                "run_id": run_id,
                "engine": "pandas",
                "generated_at": generated_at,
                "partition_column": str(partition_column),
                "partition_value": _to_jsonable(partition_value),
                "row_count": row_count,
                "business_key_count": business_key_count,
                "max_watermark": max_watermark,
                "min_watermark": min_watermark,
                "partition_hash": partition_hash,
                "business_key_hash": business_key_hash,
            }
        )

    return sorted(rows, key=lambda r: str(r["partition_value"]))


def _build_spark_partition_snapshot(df, *, dataset_name: str, table_name: str, partition_column: str, business_keys: list[str], watermark_column: str | None, run_id: str | None) -> list[dict]:
    from pyspark.sql import functions as F

    generated_at = datetime.now(timezone.utc).isoformat()
    key_cols = [F.coalesce(F.col(c).cast("string"), F.lit("")) for c in business_keys]
    with_key = df.withColumn("_business_key_row_hash", F.sha2(F.concat_ws("||", *key_cols), 256))
    agg_exprs = [
        F.count(F.lit(1)).alias("row_count"),
        F.countDistinct(*[F.col(c) for c in business_keys]).alias("business_key_count"),
        F.sha2(F.concat_ws("##", F.sort_array(F.collect_set(F.col("_business_key_row_hash")))), 256).alias("business_key_hash"),
    ]
    if watermark_column:
        agg_exprs.extend([F.max(F.col(watermark_column)).alias("max_watermark"), F.min(F.col(watermark_column)).alias("min_watermark")])
    else:
        agg_exprs.extend([F.lit(None).alias("max_watermark"), F.lit(None).alias("min_watermark")])

    snapshot_df = with_key.groupBy(F.col(partition_column)).agg(*agg_exprs)
    collected = snapshot_df.collect()
    rows = []
    for row in collected:
        part_val = row[partition_column]
        max_w = _to_jsonable(row["max_watermark"])
        min_w = _to_jsonable(row["min_watermark"])
        bkh = str(row["business_key_hash"])
        rows.append(
            {
                "dataset_name": str(dataset_name),
                "table_name": str(table_name),
                "run_id": run_id,
                "engine": "spark",
                "generated_at": generated_at,
                "partition_column": str(partition_column),
                "partition_value": _to_jsonable(part_val),
                "row_count": int(row["row_count"]),
                "business_key_count": int(row["business_key_count"]),
                "max_watermark": max_w,
                "min_watermark": min_w,
                "partition_hash": _build_partition_hash(part_val, int(row["row_count"]), int(row["business_key_count"]), max_w, min_w, bkh),
                "business_key_hash": bkh,
            }
        )
    return sorted(rows, key=lambda r: str(r["partition_value"]))


def _build_partition_snapshot(df, *, dataset_name: str = "unknown", table_name: str = "unknown", partition_column: str, business_keys: list[str], watermark_column: str | None = None, run_id: str | None = None, engine: str = "auto") -> list[dict]:
    """Execute the `_build_partition_snapshot` workflow step in FabricOps.
    
        Use this callable at its corresponding stage of the pipeline contract
        (configuration, IO, profiling, quality, drift, lineage, or handover)
        to produce deterministic artifacts and validation evidence.
    
        Parameters
        ----------
        df : Any
            Input parameter `df`.
    
        Returns
        -------
        Any
            Function output used by downstream FabricOps workflow steps.
    
        Raises
        ------
        Exception
            Propagates validation, runtime, or storage errors from underlying
            operations when execution cannot continue safely.
    
        Notes
        -----
        Side effects may include metadata writes, quality evidence generation,
        or persisted drift/lineage/handover artifacts depending on the function.
    
        Examples
        --------
        >>> _build_partition_snapshot(...)
        """
    selected_engine = _detect_dataframe_engine(df) if engine == "auto" else engine

    columns = set(getattr(df, "columns", []))
    if partition_column not in columns:
        raise ValueError(f"Missing partition column '{partition_column}'.")
    missing_keys = [c for c in business_keys if c not in columns]
    if missing_keys:
        raise ValueError(f"Missing business key columns: {missing_keys}")
    if watermark_column and watermark_column not in columns:
        raise ValueError(f"Missing watermark column '{watermark_column}'.")

    if selected_engine == "pandas":
        return _build_pandas_partition_snapshot(df, dataset_name=dataset_name, table_name=table_name, partition_column=partition_column, business_keys=business_keys, watermark_column=watermark_column, run_id=run_id)
    if selected_engine == "spark":
        return _build_spark_partition_snapshot(df, dataset_name=dataset_name, table_name=table_name, partition_column=partition_column, business_keys=business_keys, watermark_column=watermark_column, run_id=run_id)
    raise ValueError(f"Unsupported engine '{selected_engine}'.")


def _is_closed_partition(partition_value: Any, grace_days: int) -> bool:
    if grace_days == 0:
        return True
    try:
        parsed = datetime.fromisoformat(str(partition_value)).date()
    except ValueError:
        try:
            parsed = date.fromisoformat(str(partition_value))
        except ValueError:
            return True
    cutoff = datetime.now(timezone.utc).date() - timedelta(days=grace_days)
    return parsed < cutoff


def _compare_partition_snapshots(baseline_snapshots: list[dict], current_snapshots: list[dict], policy: dict | None = None) -> dict:
    """Execute the `_compare_partition_snapshots` workflow step in FabricOps.
    
        Use this callable at its corresponding stage of the pipeline contract
        (configuration, IO, profiling, quality, drift, lineage, or handover)
        to produce deterministic artifacts and validation evidence.
    
        Parameters
        ----------
        baseline_snapshots : Any
            Input parameter `baseline_snapshots`.
        current_snapshots : Any
            Input parameter `current_snapshots`.
        policy : Any
            Input parameter `policy`.
    
        Returns
        -------
        Any
            Function output used by downstream FabricOps workflow steps.
    
        Raises
        ------
        Exception
            Propagates validation, runtime, or storage errors from underlying
            operations when execution cannot continue safely.
    
        Notes
        -----
        Side effects may include metadata writes, quality evidence generation,
        or persisted drift/lineage/handover artifacts depending on the function.
    
        Examples
        --------
        >>> _compare_partition_snapshots(..., ..., ...)
        """
    active_policy = {**_default_incremental_safety_policy(), **(policy or {})}
    baseline = {str(s.get("partition_value")): s for s in baseline_snapshots}
    current = {str(s.get("partition_value")): s for s in current_snapshots}
    changes = []

    def add_change(drift_type: str, partition_value: str, previous_value, current_value, default_message: str) -> None:
        is_closed = _is_closed_partition(partition_value, int(active_policy["closed_partition_grace_days"]))
        run_mode = str(active_policy.get("run_mode", "incremental"))
        block_default = is_closed and bool(active_policy["block_on_historical_partition_change"])
        severity, action = ("warning", "warn") if not block_default else ("critical", "block")

        if run_mode == "backfill":
            severity, action = "warning", "warn"
        elif bool(active_policy.get("allow_historical_changes")):
            approval_required = bool(active_policy.get("require_approval_for_historical_changes"))
            approval_reference = active_policy.get("approval_reference")
            if (not approval_required) or approval_reference:
                severity, action = "warning", "warn"
            else:
                severity, action = "critical", "block"

        if drift_type == "partition_added":
            severity, action = "info", "allow"

        changes.append({"drift_type": drift_type, "partition_value": partition_value, "previous_value": _to_jsonable(previous_value), "current_value": _to_jsonable(current_value), "severity": severity, "action": action, "message": default_message})

    for part in sorted(set(current) - set(baseline)):
        add_change("partition_added", part, None, current[part], f"Partition '{part}' is new in the current snapshot.")
    for part in sorted(set(baseline) - set(current)):
        add_change("partition_removed", part, baseline[part], None, f"Partition '{part}' exists in baseline but is missing in current snapshot.")

    for part in sorted(set(baseline).intersection(current)):
        b, c = baseline[part], current[part]
        for field, drift_type in [("row_count", "row_count_changed"), ("business_key_count", "business_key_count_changed"), ("max_watermark", "max_watermark_changed"), ("min_watermark", "min_watermark_changed"), ("business_key_hash", "business_key_hash_changed"), ("partition_hash", "partition_hash_changed")]:
            if b.get(field) != c.get(field):
                add_change(drift_type, part, b.get(field), c.get(field), f"Partition '{part}' field '{field}' changed.")

    blocking = sum(1 for ch in changes if ch["action"] == "block")
    warning = sum(1 for ch in changes if ch["action"] == "warn")
    status = "failed" if blocking else "warning" if warning else "passed"
    return {"status": status, "can_continue": blocking == 0, "changes": changes, "summary": {"partition_count_baseline": len(baseline), "partition_count_current": len(current), "change_count": len(changes), "blocking_change_count": blocking, "warning_change_count": warning}, "policy": active_policy}


def _assert_incremental_safe(result: dict) -> None:
    """Execute the `_assert_incremental_safe` workflow step in FabricOps.
    
        Use this callable at its corresponding stage of the pipeline contract
        (configuration, IO, profiling, quality, drift, lineage, or handover)
        to produce deterministic artifacts and validation evidence.
    
        Parameters
        ----------
        result : Any
            Input parameter `result`.
    
        Returns
        -------
        Any
            Function output used by downstream FabricOps workflow steps.
    
        Raises
        ------
        Exception
            Propagates validation, runtime, or storage errors from underlying
            operations when execution cannot continue safely.
    
        Notes
        -----
        Side effects may include metadata writes, quality evidence generation,
        or persisted drift/lineage/handover artifacts depending on the function.
    
        Examples
        --------
        >>> _assert_incremental_safe(...)
        """
    if not bool(result.get("can_continue", True)):
        raise IncrementalSafetyError("Blocking incremental partition safety changes detected.")


def _build_incremental_safety_records(result: dict, *, run_id: str, dataset_name: str, table_name: str) -> list[dict]:
    """Execute the `_build_incremental_safety_records` workflow step in FabricOps.
    
        Use this callable at its corresponding stage of the pipeline contract
        (configuration, IO, profiling, quality, drift, lineage, or handover)
        to produce deterministic artifacts and validation evidence.
    
        Parameters
        ----------
        result : Any
            Input parameter `result`.
    
        Returns
        -------
        Any
            Function output used by downstream FabricOps workflow steps.
    
        Raises
        ------
        Exception
            Propagates validation, runtime, or storage errors from underlying
            operations when execution cannot continue safely.
    
        Notes
        -----
        Side effects may include metadata writes, quality evidence generation,
        or persisted drift/lineage/handover artifacts depending on the function.
    
        Examples
        --------
        >>> _build_incremental_safety_records(...)
        """
    changes = result.get("changes", []) or [
        {
            "drift_type": "none",
            "partition_value": None,
            "previous_value": None,
            "current_value": None,
            "severity": "info",
            "action": "allow",
            "message": "No incremental partition changes detected.",
        }
    ]
    rows = []
    for change in changes:
        rows.append(
            _to_jsonable(
                {
                    "run_id": run_id,
                    "dataset_name": dataset_name,
                    "table_name": table_name,
                    "status": result.get("status", "passed"),
                    "can_continue": bool(result.get("can_continue", True)),
                    "drift_type": change.get("drift_type"),
                    "partition_value": change.get("partition_value"),
                    "previous_value": change.get("previous_value"),
                    "current_value": change.get("current_value"),
                    "severity": change.get("severity"),
                    "action": change.get("action"),
                    "message": change.get("message"),
                }
            )
        )
    return rows
