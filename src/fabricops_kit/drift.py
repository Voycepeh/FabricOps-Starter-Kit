"""Lightweight schema and catalogue profile stability safeguards.

Use :func:`validate_schema`, :func:`enforce_catalogue_stability`, and :func:`stop_if_failed` in production
pipeline notebooks. FabricOps compares
append-only catalogue profile evidence to catch silent upstream source changes
before governed outputs are promoted.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
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



def _schema_guardrail_rows(
    dataframe,
    *,
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    sort_columns: bool = False,
) -> list[dict[str, str | bool | None]]:
    """Return schema rows used by the public schema guardrail generator."""
    excluded = {str(column) for column in (exclude_columns or [])}
    columns, types = _actual_schema(dataframe)
    nullable_by_column: dict[str, bool | None] = {}
    raw_type_by_column: dict[str, str] = {}
    schema = getattr(dataframe, "schema", None)
    if schema is not None and hasattr(schema, "fields"):
        for field in schema.fields:
            nullable_by_column[str(field.name)] = getattr(field, "nullable", None)
            raw_type_by_column[str(field.name)] = str(getattr(field, "dataType", ""))
    dtypes = getattr(dataframe, "dtypes", None)
    if dtypes is not None:
        dtype_items = dtypes.items() if hasattr(dtypes, "items") else dtypes
        for name, dtype in dtype_items:
            raw_type_by_column.setdefault(str(name), str(dtype))
    selected_columns = [column for column in columns if column not in excluded]
    if sort_columns:
        selected_columns = sorted(selected_columns)
    return [
        {
            "column_name": column,
            "spark_data_type": raw_type_by_column.get(column, str(types.get(column, ""))),
            "nullable": nullable_by_column.get(column),
            "guardrail_data_type": _normalize_datatype(raw_type_by_column.get(column, types.get(column, ""))),
        }
        for column in selected_columns
    ]


def _generate_schema_guardrail_config(
    dataframe,
    *,
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    sort_columns: bool = False,
    output_format: str = "dict",
):
    """Generate internal starter schema guardrail config from a DataFrame schema.

    Parameters
    ----------
    dataframe : Any
        Spark, pandas, or dataframe-like object with schema metadata.
    exclude_columns : list-like, optional
        Columns to omit from the starter expectation, such as runtime audit or
        technical annotation columns.
    sort_columns : bool, default=False
        When ``True``, sort output columns alphabetically. When ``False``,
        preserve DataFrame schema order.
    output_format : {"dict", "python", "rows"}, default="dict"
        Return shape. ``"dict"`` returns a mapping suitable for review before
        passing to :func:`validate_schema`. ``"python"`` returns copy-paste-ready
        Python code defining ``expected_schema``. ``"rows"`` returns row
        dictionaries with column name, Spark datatype, nullable flag, and
        proposed guardrail datatype.

    Returns
    -------
    dict[str, str] or str or list[dict]
        Starter schema guardrail in the requested output format.

    Raises
    ------
    ValueError
        If ``output_format`` is not one of ``"dict"``, ``"python"``, or
        ``"rows"``.

    Notes
    -----
    This helper captures the current observed schema only. Review and approve
    the returned expectation before using it as a pipeline guardrail. Common
    normalized types include ``string``, ``int``, ``bigint``, ``double``,
    ``decimal(p,s)``, ``date``, ``timestamp``, and ``boolean``.
    """
    rows = _schema_guardrail_rows(dataframe, exclude_columns=exclude_columns, sort_columns=sort_columns)
    config = {str(row["column_name"]): str(row["guardrail_data_type"]) for row in rows}
    normalized_format = str(output_format or "dict").lower()
    if normalized_format == "dict":
        return config
    if normalized_format == "rows":
        return rows
    if normalized_format == "python":
        lines = ["expected_schema = {"]
        for column, data_type in config.items():
            lines.append(f"    {column!r}: {data_type!r},")
        lines.append("}")
        return "\n".join(lines)
    raise ValueError("output_format must be one of: dict, python, rows")



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


def _canonical_hash_value(value):
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value
    if isinstance(value, (float, Decimal)):
        numeric = float(value)
        if math.isnan(numeric) or math.isinf(numeric):
            return str(numeric)
        return round(numeric, 12)
    if isinstance(value, dict):
        return {str(key): _canonical_hash_value(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple, set)):
        return [_canonical_hash_value(item) for item in value]
    return str(value)


def _canonical_json_hash(payload: dict) -> str:
    canonical = _canonical_hash_value(payload)
    encoded = json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _stable_profile_payload(profile) -> dict:
    normalized = _normalize_profile(profile) or {}
    columns = []
    for column in normalized.get("columns", []) or []:
        column_payload = {
            "column_name": column.get("column_name"),
            "data_type": _normalize_datatype(column.get("data_type")),
            "row_count": column.get("row_count"),
            "null_count": column.get("null_count"),
            "null_pct": column.get("null_pct"),
            "distinct_count": column.get("distinct_count"),
            "distinct_pct": column.get("distinct_pct"),
            "min_value": column.get("min_value"),
            "max_value": column.get("max_value"),
        }
        if column.get("distribution_type"):
            column_payload["distribution_type"] = column.get("distribution_type")
        if column.get("distribution") is not None:
            column_payload["distribution"] = column.get("distribution")
        columns.append(column_payload)
    columns.sort(key=lambda item: str(item.get("column_name") or ""))
    row_count = normalized.get("row_count")
    if row_count is None and columns:
        row_count = columns[0].get("row_count")
    return {"row_count": row_count, "columns": columns}


def _profile_hash(profile) -> str:
    return _canonical_json_hash(_stable_profile_payload(profile))


def _stability_exclude_columns(exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None) -> set[str]:
    excluded = set(_DEFAULT_STABILITY_EXCLUDE_COLUMNS)
    if exclude_columns:
        excluded.update(str(column) for column in exclude_columns)
    return excluded


def _is_stability_excluded_column(column: str, exclude_columns: set[str]) -> bool:
    name = str(column)
    return name in exclude_columns or any(name.startswith(prefix) for prefix in _DEFAULT_STABILITY_EXCLUDE_PREFIXES)


def _schema_hash_from_dataframe(dataframe, exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None) -> str:
    excluded = _stability_exclude_columns(exclude_columns)
    columns, types = _actual_schema(dataframe)
    payload = {column: types.get(column, "") for column in columns if not _is_stability_excluded_column(column, excluded)}
    return _canonical_json_hash(payload)


def _profile_row_count(profile) -> int | None:
    payload = _stable_profile_payload(profile)
    value = payload.get("row_count")
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _filter_watermark_slice(dataframe, watermark_column: str, watermark_value):
    from pyspark.sql import functions as F

    return dataframe.where(F.col(watermark_column) <= F.lit(watermark_value))


def _max_watermark_value(dataframe, watermark_column: str):
    from pyspark.sql import functions as F

    rows = dataframe.agg(F.max(F.col(watermark_column)).alias("watermark_value")).collect()
    if not rows:
        return None
    return rows[0]["watermark_value"]


def _latest_catalogue_stability_row(
    catalogue_df,
    *,
    dataset_name: str,
    table_name: str,
    profile_stage: str,
    stability_check_type: str,
    data_behavior: str,
    profile_scope: str,
    watermark_column: str | None = None,
    exclude_run_id: str | None = None,
) -> dict | None:
    if catalogue_df is None:
        return None

    try:
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

        def required_col(*names: str) -> str | None:
            return catalogue_col(*names)

        stage = str(profile_stage).lower()
        stage_roles = [stage, f"{stage}_profile"]
        if stage == "target":
            stage_roles.append("output_profile")

        dataset_col = required_col("dataset_name", "DATASET_NAME")
        table_col = required_col("table_name", "PROFILED_TABLE_NAME", "TABLE_NAME")
        stage_col = required_col("profile_stage", "PROFILE_STAGE", "evidence_role", "EVIDENCE_ROLE")
        profile_status_col = catalogue_col("profile_status", "PROFILE_STATUS")
        run_col = catalogue_col("profile_run_id", "PROFILE_RUN_ID", "run_id", "RUN_ID")
        time_col = catalogue_col("profiled_at", "run_timestamp", "RUN_TIMESTAMP", "created_at")
        enabled_col = required_col("stability_check_enabled", "STABILITY_CHECK_ENABLED")
        stability_status_col = required_col("stability_status", "STABILITY_STATUS")
        check_type_col = required_col("stability_check_type", "STABILITY_CHECK_TYPE")
        behavior_col = required_col("data_behavior", "DATA_BEHAVIOR")
        scope_col = required_col("profile_scope", "PROFILE_SCOPE")
        watermark_col = required_col("watermark_column", "WATERMARK_COLUMN")
        comparable_hash_col = required_col("comparable_profile_hash", "COMPARABLE_PROFILE_HASH")
        profile_hash_col = required_col("profile_hash", "PROFILE_HASH")
        watermark_value_col = required_col("watermark_value", "WATERMARK_VALUE")

        required = [
            dataset_col,
            table_col,
            stage_col,
            enabled_col,
            stability_status_col,
            check_type_col,
            behavior_col,
            scope_col,
            profile_hash_col,
        ]
        if str(stability_check_type).lower() == "watermark_slice_hash":
            required.extend([watermark_col, comparable_hash_col, watermark_value_col])
        if any(column is None for column in required):
            return None

        filters = [
            F.col(dataset_col) == dataset_name,
            F.col(table_col) == table_name,
            F.lower(F.col(stage_col)).isin(stage_roles),
            F.lower(F.col(stability_status_col)).isin("passed", "baseline_created"),
            F.lower(F.col(check_type_col)) == str(stability_check_type).lower(),
            F.lower(F.col(behavior_col)) == str(data_behavior).lower(),
            F.lower(F.col(scope_col)) == str(profile_scope).lower(),
            F.lower(F.col(enabled_col).cast("string")).isin("true", "1", "yes"),
        ]
        if profile_status_col:
            filters.append(F.lower(F.col(profile_status_col)).isin("success", "successful"))
        if exclude_run_id and run_col:
            filters.append(F.col(run_col) != exclude_run_id)
        if str(stability_check_type).lower() == "watermark_slice_hash":
            filters.append(F.col(watermark_col) == (watermark_column or ""))
            filters.append(F.col(comparable_hash_col).isNotNull() & (F.length(F.trim(F.col(comparable_hash_col).cast("string"))) > 0))
            filters.append(F.col(watermark_value_col).isNotNull() & (F.length(F.trim(F.col(watermark_value_col).cast("string"))) > 0))
        else:
            filters.append(F.col(profile_hash_col).isNotNull() & (F.length(F.trim(F.col(profile_hash_col).cast("string"))) > 0))

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
    except Exception as exc:
        if _is_missing_table_error(exc):
            return None
        raise


def enforce_catalogue_stability(
    spark,
    dataframe,
    metadata_table: str,
    dataset_name: str,
    table_name: str,
    *,
    stage: str,
    run_id: str,
    data_behavior: str,
    stability_check_type: str,
    watermark_column: str | None = None,
    watermark_value=None,
    exclude_columns: list[str] | set[str] | tuple[str, ...] | None = None,
    exclude_run_id: str | None = None,
    config=None,
    env: str | None = None,
    catalogue_df=None,
) -> dict:
    """Compare the current DataFrame profile with append-only catalogue evidence.

    Parameters
    ----------
    spark : Any
        Spark session used to read ``METADATA_DATA_CATALOGUE`` baselines.
    dataframe : Any
        Spark DataFrame being checked.
    metadata_table : str
        Existing catalogue metadata table that stores profile evidence rows.
    dataset_name : str
        Governed dataset identifier used for baseline lookup.
    table_name : str
        Governed source or target table name used for baseline lookup.
    stage : {"source", "target"}
        Pipeline stage used to keep source and target baselines independent.
    run_id : str
        Current pipeline run identifier.
    data_behavior : {"fixed", "changing"}
        Whether the dataset is expected to be stable in full or only stable for
        the previously loaded watermark slice.
    stability_check_type : {"full_profile_hash", "watermark_slice_hash", "skip"}
        Comparison strategy. ``skip`` records a non-blocking skipped result.
    watermark_column : str, optional
        Comparable watermark column required for ``watermark_slice_hash``.
    watermark_value : Any, optional
        Current run watermark. When omitted for changing data, the maximum
        value in ``watermark_column`` is used.
    exclude_columns : list-like, optional
        Business or technical columns to exclude from deterministic profiles.
    exclude_run_id : str, optional
        Run identifier to exclude from baseline lookup. Defaults to ``run_id``.
    config, env : object, str, optional
        Metadata route from ``00_env_config`` used to read the catalogue table
        via ``read_lakehouse_table`` when ``catalogue_df`` is not supplied.
    catalogue_df : DataFrame, optional
        Preloaded ``METADATA_DATA_CATALOGUE`` DataFrame. When provided, no
        metadata read is performed.

    Returns
    -------
    dict
        Standard guardrail result compatible with ``stop_if_failed``.

    Notes
    -----
    The function does not create a separate history table. It reads the latest
    previous row from the existing append-only catalogue and returns stability
    metadata for ``write_catalogue_evidence`` to append with today's profile.
    """
    from fabricops_kit.data_profiling import profile_dataframe

    behavior = str(data_behavior or "").lower()
    check_type = str(stability_check_type or "").lower()
    if behavior not in {"fixed", "changing"}:
        raise ValueError("data_behavior must be one of: fixed, changing")
    if check_type not in {"full_profile_hash", "watermark_slice_hash", "skip"}:
        raise ValueError("stability_check_type must be one of: full_profile_hash, watermark_slice_hash, skip")
    if check_type == "watermark_slice_hash" and not watermark_column:
        raise ValueError("watermark_column is required for watermark_slice_hash")

    effective_exclude_columns = _stability_exclude_columns(exclude_columns)
    current_profile_df = profile_dataframe(dataframe, table_name, exclude_columns=effective_exclude_columns)
    current_profile_hash = _profile_hash(current_profile_df)
    current_row_count = _profile_row_count(current_profile_df)
    schema_hash = _schema_hash_from_dataframe(dataframe, exclude_columns=effective_exclude_columns)
    effective_watermark = watermark_value
    if check_type == "watermark_slice_hash" and effective_watermark is None:
        effective_watermark = _max_watermark_value(dataframe, str(watermark_column))

    comparable_profile_hash = current_profile_hash
    profile_scope = "full_table"
    profile_filter_expression = ""
    if check_type == "watermark_slice_hash":
        profile_scope = "watermark_slice"
        profile_filter_expression = f"{watermark_column} <= {effective_watermark}"
        comparable_df = _filter_watermark_slice(dataframe, str(watermark_column), effective_watermark)
        comparable_profile_hash = _profile_hash(profile_dataframe(comparable_df, table_name, exclude_columns=effective_exclude_columns))

    if catalogue_df is None and config is not None and env is not None:
        from fabricops_kit.fabric_input_output import read_lakehouse_table

        try:
            catalogue_df = read_lakehouse_table(config, env, "metadata", metadata_table, spark_session=spark)
        except Exception as exc:
            if _is_missing_table_error(exc):
                catalogue_df = None
            else:
                raise

    baseline = _latest_catalogue_stability_row(
        catalogue_df,
        dataset_name=dataset_name,
        table_name=table_name,
        profile_stage=stage,
        stability_check_type=check_type,
        data_behavior=behavior,
        profile_scope=profile_scope,
        watermark_column=watermark_column,
        exclude_run_id=exclude_run_id or run_id,
    )
    baseline_run_id = str((baseline or {}).get("profile_run_id") or (baseline or {}).get("PROFILE_RUN_ID") or "")
    baseline_watermark_value = (baseline or {}).get("watermark_value", (baseline or {}).get("WATERMARK_VALUE"))
    baseline_profile_hash = (baseline or {}).get("profile_hash", (baseline or {}).get("PROFILE_HASH"))
    if check_type == "watermark_slice_hash":
        baseline_profile_hash = (baseline or {}).get("comparable_profile_hash", (baseline or {}).get("COMPARABLE_PROFILE_HASH"))
        if baseline_watermark_value is not None:
            profile_filter_expression = f"{watermark_column} <= {baseline_watermark_value}"
            comparable_df = _filter_watermark_slice(dataframe, str(watermark_column), baseline_watermark_value)
            comparable_profile_hash = _profile_hash(profile_dataframe(comparable_df, table_name, exclude_columns=effective_exclude_columns))

    result = {
        "status": "passed",
        "can_continue": True,
        "check_type": "catalogue_profile_stability",
        "stability_check_enabled": check_type != "skip",
        "stability_check_type": check_type,
        "data_behavior": behavior,
        "profile_scope": profile_scope,
        "watermark_column": watermark_column or "",
        "watermark_value": str(effective_watermark) if effective_watermark is not None else "",
        "profile_filter_expression": profile_filter_expression,
        "row_count": current_row_count,
        "schema_hash": schema_hash,
        "profile_hash": current_profile_hash,
        "comparable_profile_hash": comparable_profile_hash,
        "baseline_run_id": baseline_run_id,
        "baseline_profile_hash": str(baseline_profile_hash or ""),
        "baseline_watermark_value": str(baseline_watermark_value) if baseline_watermark_value is not None else "",
        "stability_status": "passed",
        "stability_can_continue": True,
        "stability_message": "Current profile matches the previous catalogue profile.",
        "stability_difference_summary": "",
    }
    if check_type == "skip":
        result.update(status="skipped", stability_status="skipped", stability_message="Catalogue profile stability check skipped.", message="Catalogue profile stability check skipped.")
        return result
    if not baseline or not baseline_profile_hash:
        result.update(status="baseline_created", stability_status="baseline_created", baseline_profile_hash="", stability_message="No previous catalogue stability profile was available; current profile establishes the baseline.", message="No previous catalogue stability profile was available; current profile establishes the baseline.")
        return result
    if comparable_profile_hash != str(baseline_profile_hash):
        message = "Previously loaded data changed compared with the prior catalogue profile." if check_type == "watermark_slice_hash" else "Current full profile differs from the previous catalogue profile."
        result.update(
            status="failed",
            can_continue=False,
            stability_status="failed",
            stability_can_continue=False,
            stability_message=message,
            stability_difference_summary=json.dumps({"current_hash": comparable_profile_hash, "baseline_hash": str(baseline_profile_hash)}, sort_keys=True),
            message=message,
        )
        return result
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
        Direct schema, catalogue stability, or DQ guardrail result.

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
