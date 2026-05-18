"""Technical/audit column helpers for traceable FabricOps datasets.

Use these functions before output writes to stamp run IDs, timestamps, and
derived partition buckets that support lineage, replayability, and handover.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
from typing import Any
import uuid

import pandas as pd



def _default_technical_columns() -> list[str]:
    """Return framework-generated and legacy technical column names to ignore.

    The returned list is intended for downstream profiling and hash generation logic
    that needs a shared source of truth for framework-managed columns.

    Returns
    -------
    list[str]
        Technical column names including current standard names and legacy names
        retained only for backward-compatible ignore behavior.

    Examples
    --------
    >>> cols = _default_technical_columns()
    >>> "_pipeline_run_id" in cols
    True
    """
    return [
        "_pipeline_run_id",
        "_pipeline_name",
        "_pipeline_environment",
        "_source_system",
        "_source_table",
        "_source_extract_timestamp",
        "_record_loaded_timestamp",
        "_notebook_name",
        "_loaded_by",
        "_watermark_value",
        "_partition_bucket",
        "_sample_bucket",
        "_row_ingest_id",
        "_business_key_hash",
        "_row_hash",
        "pipeline_ts",
        "notebook_name",
        "loaded_by",
        "p_bucket",
        "sample_bucket",
        "row_ingest_id",
        "ingest_run_id",
        "pipeline_run_id",
        "loaded_at",
        "run_ingest_id",
    ]


def _assert_columns_exist(df: Any, columns: list[str]) -> None:
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _non_technical_columns(df: Any) -> list[str]:
    technical = set(_default_technical_columns())
    return [c for c in df.columns if c not in technical]


def _safe_string(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)) or pd.isna(value):
        return "<NULL>"
    return str(value)


def _hash_row(values: list[Any]) -> str:
    joined = "||".join(_safe_string(v) for v in values)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()


def _get_fabric_runtime_context() -> dict[str, Any]:
    try:
        from notebookutils import runtime  # type: ignore

        return getattr(runtime, "context", None) or {}
    except Exception:
        return {}


def _bucket_values_pandas(series: pd.Series, bucket_size: int) -> tuple[pd.Series, pd.Series]:
    hashes = series.apply(lambda v: int(hashlib.sha256(_safe_string(v).encode("utf-8")).hexdigest(), 16))
    return hashes % bucket_size, hashes % 1_000_000


def _add_datetime_features(
    df,
    datetime_column: str,
    *,
    prefix: str | None = None,
    timezone: str = "Asia/Singapore",
    include_datetime: bool = True,
    include_date: bool = True,
    include_time: bool = True,
    include_hour: bool = True,
    include_30_min_block: bool = True,
    engine: str = "auto",
):
    """Add localized datetime feature columns derived from a UTC datetime column.

    Parameters
    ----------
    df : Any
        Input PySpark DataFrame.
    datetime_column : str
        Source UTC datetime column.
    prefix : str | None, optional
        Prefix used for output columns. When omitted, `datetime_column` is used.
    timezone : str, default="Asia/Singapore"
        IANA timezone used for localization.
    include_datetime : bool, default=True
        Whether to add ``{PREFIX}_DTM_UTC8``.
    include_date : bool, default=True
        Whether to add ``{PREFIX}_DATE_UTC8``.
    include_time : bool, default=True
        Whether to add ``{PREFIX}_TIME_UTC8``.
    include_hour : bool, default=True
        Whether to add ``{PREFIX}_HOUR_UTC8``.
    include_30_min_block : bool, default=True
        Whether to add ``{PREFIX}_TIME_BLOCK_30_MIN``.
    engine : str, default="auto"
        Execution mode placeholder retained for compatibility; PySpark DataFrame is expected.

    Returns
    -------
    Any
        DataFrame with requested datetime features.

    Raises
    ------
    ValueError
        If `datetime_column` does not exist.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({"event_ts": ["2026-01-01T00:45:00Z"]})
    >>> _add_datetime_features(df, "event_ts", prefix="EVENT")["EVENT_TIME_UTC8"].iloc[0]
    '08:45:00'
    """
    _assert_columns_exist(df, [datetime_column])
    col_prefix = prefix or datetime_column

    from pyspark.sql import functions as F

    localized = F.from_utc_timestamp(F.col(datetime_column), timezone)
    out = df
    if include_datetime:
        out = out.withColumn(f"{col_prefix}_DTM_UTC8", localized)
    if include_date:
        out = out.withColumn(f"{col_prefix}_DATE_UTC8", F.to_date(localized))
    if include_time:
        out = out.withColumn(f"{col_prefix}_TIME_UTC8", F.date_format(localized, "HH:mm:ss"))
    if include_hour:
        out = out.withColumn(f"{col_prefix}_HOUR_UTC8", F.hour(localized))
    if include_30_min_block:
        out = out.withColumn(
            f"{col_prefix}_TIME_BLOCK_30_MIN",
            F.when(F.minute(localized) < 30, F.concat(F.date_format(localized, "HH:"), F.lit("00"))).otherwise(
                F.concat(F.date_format(localized, "HH:"), F.lit("30"))
            ),
        )
    return out


def _add_audit_columns(
    df,
    *,
    run_id: str | None = None,
    pipeline_name: str | None = None,
    environment: str | None = None,
    source_system: str | None = None,
    source_table: str | None = None,
    source_extract_timestamp: str | None = None,
    notebook_name: str | None = None,
    loaded_by: str | None = None,
    watermark_column: str | None = None,
    bucket_column: str | None = None,
    bucket_size: int = 512,
    include_row_ingest_id: bool = True,
    engine: str = "auto",
):
    """Add run tracking and audit columns for ingestion workflows.

    Parameters
    ----------
    df : Any
        Input PySpark DataFrame.
    run_id : str | None, optional
        Pipeline run identifier. If omitted, a UUID is generated.
    pipeline_name : str | None, optional
        Pipeline or notebook workflow name.
    environment : str | None, optional
        Environment label such as ``Sandbox`` or ``Production``.
    source_system : str | None, optional
        Upstream source system name.
    source_table : str | None, optional
        Upstream table or dataset name.
    source_extract_timestamp : str | None, optional
        Timestamp string representing source extract time.
    notebook_name : str | None, optional
        Notebook name override. Uses Fabric runtime context when available.
    loaded_by : str | None, optional
        User override. Uses Fabric runtime context when available.
    watermark_column : str | None, optional
        Source column copied into ``_watermark_value``.
    bucket_column : str | None, optional
        Source column used to derive ``_partition_bucket`` and ``_sample_bucket``.
    bucket_size : int, default=512
        Partition bucket modulus. Must be one of ``128``, ``256``, ``512``, ``1024``.
    include_row_ingest_id : bool, default=True
        Whether to add ``_row_ingest_id``.
    engine : str, default="auto"
        Execution mode placeholder retained for compatibility; PySpark DataFrame is expected.

    Returns
    -------
    Any
        DataFrame with requested audit columns.

    Raises
    ------
    ValueError
        If `watermark_column` or `bucket_column` does not exist, or `bucket_size` is invalid.

    Notes
    -----
    Fabric notebook runtime is optional. This function imports locally without Fabric.
    In Fabric notebooks it reads ``notebookutils.runtime.context`` when available;
    otherwise it falls back to ``local_notebook`` and ``local_user``.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({"BUSINESS_KEY": ["A1"], "updated_at": ["2026-01-01T00:00:00Z"]})
    >>> out = _add_audit_columns(
    ...     df,
    ...     pipeline_name="orders_pipeline",
    ...     environment="Sandbox",
    ...     source_table="orders",
    ...     watermark_column="updated_at",
    ...     bucket_column="BUSINESS_KEY",
    ...     engine="pandas",
    ... )
    >>> "_pipeline_run_id" in out.columns
    True
    """
    selected_engine = _resolve_engine(df, engine)
    resolved_run_id = run_id or str(uuid.uuid4())
    context = _get_fabric_runtime_context()
    resolved_notebook_name = notebook_name or context.get("currentNotebookName", "local_notebook")
    resolved_loaded_by = loaded_by or context.get("userName", "local_user")

    if watermark_column is not None:
        _assert_columns_exist(df, [watermark_column])
    if bucket_column is not None:
        _assert_columns_exist(df, [bucket_column])
        if bucket_size not in {128, 256, 512, 1024}:
            raise ValueError("bucket_size must be one of 128, 256, 512, or 1024.")

    if selected_engine == "pandas":
        out = df.copy()
        out["_pipeline_run_id"] = resolved_run_id
        if pipeline_name is not None:
            out["_pipeline_name"] = pipeline_name
        if environment is not None:
            out["_pipeline_environment"] = environment
        if source_system is not None:
            out["_source_system"] = source_system
        if source_table is not None:
            out["_source_table"] = source_table
        if source_extract_timestamp is not None:
            out["_source_extract_timestamp"] = source_extract_timestamp
        out["_record_loaded_timestamp"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        out["_notebook_name"] = resolved_notebook_name
        out["_loaded_by"] = resolved_loaded_by
        if watermark_column is not None:
            out["_watermark_value"] = out[watermark_column]
        if bucket_column is not None:
            p_bucket, s_bucket = _bucket_values_pandas(out[bucket_column], bucket_size)
            out["_partition_bucket"] = p_bucket
            out["_sample_bucket"] = s_bucket
        if include_row_ingest_id:
            out["_row_ingest_id"] = [str(uuid.uuid4()) for _ in range(len(out))]
        return out

    from pyspark.sql import functions as F

    out = df.withColumn("_pipeline_run_id", F.lit(resolved_run_id))
    for name, value in [
        ("_pipeline_name", pipeline_name),
        ("_pipeline_environment", environment),
        ("_source_system", source_system),
        ("_source_table", source_table),
        ("_source_extract_timestamp", source_extract_timestamp),
    ]:
        if value is not None:
            out = out.withColumn(name, F.lit(value))
    out = out.withColumn("_record_loaded_timestamp", F.current_timestamp())
    out = out.withColumn("_notebook_name", F.lit(resolved_notebook_name))
    out = out.withColumn("_loaded_by", F.lit(resolved_loaded_by))
    if watermark_column is not None:
        out = out.withColumn("_watermark_value", F.col(watermark_column))
    if bucket_column is not None:
        value = F.abs(F.hash(F.col(bucket_column)))
        out = out.withColumn("_partition_bucket", F.pmod(value, F.lit(bucket_size))).withColumn("_sample_bucket", F.pmod(value, F.lit(1_000_000)))
    if include_row_ingest_id:
        out = out.withColumn("_row_ingest_id", F.expr("uuid()"))
    return out


def _add_hash_columns(
    df,
    *,
    business_keys: list[str] | None = None,
    row_hash_columns: list[str] | None = None,
    include_business_key_hash: bool = True,
    include_row_hash: bool = True,
    engine: str = "auto",
):
    """Add business key and row-level SHA256 hash columns.

    Parameters
    ----------
    df : Any
        Input PySpark DataFrame.
    business_keys : list[str] | None, optional
        Business key columns used to build ``_business_key_hash``.
    row_hash_columns : list[str] | None, optional
        Columns used to build ``_row_hash``. When omitted, all non-technical columns are used.
    include_business_key_hash : bool, default=True
        Whether to add ``_business_key_hash``.
    include_row_hash : bool, default=True
        Whether to add ``_row_hash``.
    engine : str, default="auto"
        Execution mode placeholder retained for compatibility; PySpark DataFrame is expected.

    Returns
    -------
    Any
        DataFrame with hash columns added.

    Raises
    ------
    ValueError
        If business key hashing is enabled without `business_keys`, or if required columns are missing.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({"BUSINESS_KEY": ["A1"], "amount": [10.5]})
    >>> out = _add_hash_columns(df, business_keys=["BUSINESS_KEY"], engine="pandas")
    >>> "_row_hash" in out.columns
    True
    """
    selected_engine = _resolve_engine(df, engine)

    if include_business_key_hash:
        if not business_keys:
            raise ValueError("business_keys must be provided when include_business_key_hash=True.")
        _assert_columns_exist(df, business_keys)

    if include_row_hash:
        row_hash_columns = row_hash_columns or _non_technical_columns(df)
        _assert_columns_exist(df, row_hash_columns)

    if selected_engine == "pandas":
        out = df.copy()
        if include_business_key_hash:
            out["_business_key_hash"] = out[business_keys].apply(lambda row: _hash_row(row.tolist()), axis=1)
        if include_row_hash:
            out["_row_hash"] = out[row_hash_columns].apply(lambda row: _hash_row(row.tolist()), axis=1)
        return out

    from pyspark.sql import functions as F

    out = df
    if include_business_key_hash:
        business_exprs = [F.coalesce(F.col(c).cast("string"), F.lit("<NULL>")) for c in business_keys]
        out = out.withColumn("_business_key_hash", F.sha2(F.concat_ws("||", *business_exprs), 256))
    if include_row_hash:
        row_exprs = [F.coalesce(F.col(c).cast("string"), F.lit("<NULL>")) for c in row_hash_columns]
        out = out.withColumn("_row_hash", F.sha2(F.concat_ws("||", *row_exprs), 256))
    return out


def standardize_columns(df, run_id=None, pipeline_name=None, environment=None, source_table=None, datetime_columns=None, business_keys=None, bucket_column=None, engine="spark"):
    """Apply canonical technical/audit enrichment in one notebook-facing wrapper."""
    out = df
    if datetime_columns:
        for col, prefix in datetime_columns.items():
            out = _add_datetime_features(out, col, prefix=prefix, engine=engine)
    out = _add_audit_columns(out, run_id=run_id, pipeline_name=pipeline_name, environment=environment, source_table=source_table, bucket_column=bucket_column, engine=engine)
    if business_keys:
        out = _add_hash_columns(out, business_keys=business_keys, engine=engine)
    return out
