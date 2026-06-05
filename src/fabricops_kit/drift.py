"""Lightweight schema, partition, and profile drift safeguards.

Use :func:`check_schema` in production pipeline notebooks when a local,
pipeline-specific check only needs to confirm expected dataframe columns and
datatypes before execution continues. The remaining helpers support optional
partition and profile drift workflows.
"""

from __future__ import annotations

from datetime import datetime, timezone
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


def detect_dataframe_engine(df) -> str:
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


def check_schema(
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


def check_partition_drift(df, dataset_name: str, table_name: str, partition_column: str, business_keys: list[str] | None = None, watermark_column: str | None = None, baseline_snapshot: list[dict] | dict | None = None, policy: dict | None = None, run_id: str | None = None, engine: str = "spark") -> dict:
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
    current_snapshot = build_partition_snapshot(
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
    comparison = compare_partition_snapshots(baseline_rows, current_snapshot, policy=policy or default_incremental_safety_policy())
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


def build_and_write_partition_snapshot(spark, df, dataset_name: str, table_name: str, metadata_table: str, partition_column: str, business_keys: list[str] | None = None, watermark_column: str | None = None, run_id: str | None = None, mode: str = "append", engine: str = "spark") -> dict:
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
    snapshot = build_partition_snapshot(
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


def load_latest_partition_snapshot(spark, metadata_table: str, dataset_name: str, table_name: str) -> list[dict] | dict | None:
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


def check_profile_drift(current_profile: dict, baseline_profile: dict | None = None, policy: dict | None = None) -> dict:
    """Compare profile metrics against a baseline profile and drift thresholds.
    
        Parameters
        ----------
        current_profile : Any
            Value used by this callable.
        baseline_profile : Any
            Value used by this callable.
        policy : Any
            Value used by this callable.
    
        Returns
        -------
        dict
            Structured output produced by this callable.
    """
    active = {
        "max_row_count_change_percent": 50,
        "max_null_percent_change_points": 20,
        "max_distinct_percent_change_points": 30,
        "fail_on_missing_column": True,
        **(policy or {}),
    }
    if baseline_profile is None:
        return {"status": "no_baseline", "can_continue": True, "checks": [], "message": "No baseline profile provided."}

    checks = []
    blocking = False
    b_row = float(baseline_profile.get("row_count") or 0)
    c_row = float(current_profile.get("row_count") or 0)
    row_delta_pct = 0.0 if b_row == 0 else abs(c_row - b_row) / b_row * 100.0
    row_ok = row_delta_pct <= float(active["max_row_count_change_percent"])
    checks.append({"check": "row_count_change_percent", "passed": row_ok, "value": row_delta_pct, "threshold": active["max_row_count_change_percent"]})
    blocking = blocking or (not row_ok)

    b_cols = {c.get("column_name"): c for c in baseline_profile.get("columns", [])}
    c_cols = {c.get("column_name"): c for c in current_profile.get("columns", [])}
    for col in sorted(set(b_cols) - set(c_cols)):
        passed = not bool(active["fail_on_missing_column"])
        checks.append({"check": "missing_column", "column": col, "passed": passed})
        blocking = blocking or (not passed)

    for col in sorted(set(b_cols).intersection(c_cols)):
        b = b_cols[col]
        c = c_cols[col]
        if "null_pct" in b and "null_pct" in c:
            delta = abs(float(c.get("null_pct") or 0) - float(b.get("null_pct") or 0))
            passed = delta <= float(active["max_null_percent_change_points"])
            checks.append({"check": "null_percent_change_points", "column": col, "passed": passed, "value": delta, "threshold": active["max_null_percent_change_points"]})
            blocking = blocking or (not passed)
        if "distinct_pct" in b and "distinct_pct" in c:
            delta = abs(float(c.get("distinct_pct") or 0) - float(b.get("distinct_pct") or 0))
            passed = delta <= float(active["max_distinct_percent_change_points"])
            checks.append({"check": "distinct_percent_change_points", "column": col, "passed": passed, "value": delta, "threshold": active["max_distinct_percent_change_points"]})
            blocking = blocking or (not passed)
        if b.get("min_value") != c.get("min_value"):
            checks.append({"check": "min_changed", "column": col, "passed": True, "baseline": b.get("min_value"), "current": c.get("min_value")})
        if b.get("max_value") != c.get("max_value"):
            checks.append({"check": "max_changed", "column": col, "passed": True, "baseline": b.get("max_value"), "current": c.get("max_value")})

    return {"status": "failed" if blocking else "passed", "can_continue": not blocking, "checks": checks, "message": "Profile drift check completed."}


def summarize_drift_results(schema_drift_result: dict | None = None, partition_drift_result: dict | None = None, profile_drift_result: dict | None = None) -> dict:
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


def build_drift_evidence_record(*, dataset_name: str, table_name: str, run_id: str | None, drift_type: str, result: dict, workspace_id: str | None = None, workspace_name: str | None = None, notebook_id: str | None = None, notebook_name: str | None = None) -> dict:
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


def prepare_drift_baselines(
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


def default_incremental_safety_policy() -> dict:
    """Execute the `default_incremental_safety_policy` workflow step in FabricOps.
    
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
        >>> default_incremental_safety_policy()
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


def build_partition_snapshot(df, *, dataset_name: str = "unknown", table_name: str = "unknown", partition_column: str, business_keys: list[str], watermark_column: str | None = None, run_id: str | None = None, engine: str = "auto") -> list[dict]:
    """Execute the `build_partition_snapshot` workflow step in FabricOps.
    
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
        >>> build_partition_snapshot(...)
        """
    selected_engine = detect_dataframe_engine(df) if engine == "auto" else engine

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


def compare_partition_snapshots(baseline_snapshots: list[dict], current_snapshots: list[dict], policy: dict | None = None) -> dict:
    """Execute the `compare_partition_snapshots` workflow step in FabricOps.
    
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
        >>> compare_partition_snapshots(..., ..., ...)
        """
    active_policy = {**default_incremental_safety_policy(), **(policy or {})}
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


def assert_incremental_safe(result: dict) -> None:
    """Execute the `assert_incremental_safe` workflow step in FabricOps.
    
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
        >>> assert_incremental_safe(...)
        """
    if not bool(result.get("can_continue", True)):
        raise IncrementalSafetyError("Blocking incremental partition safety changes detected.")


def build_incremental_safety_records(result: dict, *, run_id: str, dataset_name: str, table_name: str) -> list[dict]:
    """Execute the `build_incremental_safety_records` workflow step in FabricOps.
    
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
        >>> build_incremental_safety_records(...)
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
