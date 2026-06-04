"""Runtime audit column helpers for traceable FabricOps outputs.

Use these helpers immediately before output writes to stamp lightweight runtime
audit context onto produced rows. Hash columns, datetime feature columns,
bucket columns, sample buckets, and row ingest IDs are intentionally outside the
default audit path.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
import warnings

import pandas as pd

RUNTIME_AUDIT_COLUMNS = [
    "_pipeline_run_id",
    "_pipeline_name",
    "_pipeline_environment",
    "_source_table",
    "_record_loaded_timestamp",
    "_notebook_name",
    "_loaded_by",
]

_LEGACY_TECHNICAL_COLUMNS = [
    "_source_system",
    "_source_extract_timestamp",
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


def _default_technical_columns() -> list[str]:
    """Return framework-generated audit and legacy technical columns to ignore.

    Returns
    -------
    list[str]
        Runtime audit columns plus legacy technical columns retained only so
        profiling helpers can continue to exclude columns produced by older
        notebook templates.
    """
    return [*RUNTIME_AUDIT_COLUMNS, *_LEGACY_TECHNICAL_COLUMNS]


def _get_fabric_runtime_context() -> dict[str, Any]:
    """Return the Microsoft Fabric notebook runtime context when available."""
    try:
        from notebookutils import runtime  # type: ignore

        return getattr(runtime, "context", None) or {}
    except Exception:
        return {}


def _context_value(context: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = context.get(key)
        if value not in (None, ""):
            return str(value)
    return None


def add_runtime_audit_columns(
    df: Any,
    *,
    run_id: str | None = None,
    pipeline_name: str | None = None,
    environment: str | None = None,
    source_table: str | None = None,
    notebook_name: str | None = None,
    loaded_by: str | None = None,
    engine: str = "auto",
):
    """Add lightweight runtime audit columns to a dataframe.

    Parameters
    ----------
    df : pyspark.sql.DataFrame or pandas.DataFrame
        DataFrame to enrich before writing a pipeline target table.
    run_id : str, optional
        Identifier for the pipeline run that produced the row.
    pipeline_name : str, optional
        Name of the pipeline that produced the row.
    environment : str, optional
        Runtime environment name, such as ``"dev"`` or ``"prod"``.
    source_table : str, optional
        Source table or source asset used by the pipeline run.
    notebook_name : str, optional
        Notebook name to stamp. When omitted, the Fabric runtime context is
        used when available.
    loaded_by : str, optional
        User or service principal to stamp. When omitted, the Fabric runtime
        context is used when available.
    engine : {"auto", "spark", "pandas"}, default="auto"
        DataFrame engine. ``"auto"`` detects pandas DataFrames and otherwise
        uses the Spark ``withColumn`` API.

    Returns
    -------
    pyspark.sql.DataFrame or pandas.DataFrame
        DataFrame containing only the standard runtime audit columns added by
        this helper: ``_pipeline_run_id``, ``_pipeline_name``,
        ``_pipeline_environment``, ``_source_table``,
        ``_record_loaded_timestamp``, ``_notebook_name``, and ``_loaded_by``.

    Notes
    -----
    Hash columns are useful for deduplication, masked key comparison, slowly
    changing dimensions, or change detection, but they are not audit fields.
    Datetime feature columns are analytics features. Bucket columns are for
    advanced large-table layout or skew handling. For simple parallel writes,
    use ``repartition_by`` in the write helper instead.

    Examples
    --------
    >>> import pandas as pd
    >>> df = pd.DataFrame({"customer_id": [1001]})
    >>> out = add_runtime_audit_columns(df, run_id="run-1", pipeline_name="pipe", environment="dev", source_table="customers")
    >>> [column for column in out.columns if column.startswith("_pipeline")]
    ['_pipeline_run_id', '_pipeline_name', '_pipeline_environment']
    """
    selected_engine = engine
    if selected_engine == "auto":
        selected_engine = "pandas" if isinstance(df, pd.DataFrame) else "spark"
    if selected_engine not in {"pandas", "spark"}:
        raise ValueError("engine must be one of auto, pandas, or spark.")

    context = _get_fabric_runtime_context()
    resolved_notebook_name = notebook_name or _context_value(context, "currentNotebookName", "notebookName") or "unknown_notebook"
    resolved_loaded_by = loaded_by or _context_value(context, "userName", "userId") or "unknown_user"
    resolved_run_id = run_id or datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%SZ")

    if selected_engine == "pandas":
        out = df.copy()
        out["_pipeline_run_id"] = resolved_run_id
        out["_pipeline_name"] = pipeline_name
        out["_pipeline_environment"] = environment
        out["_source_table"] = source_table
        out["_record_loaded_timestamp"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        out["_notebook_name"] = resolved_notebook_name
        out["_loaded_by"] = resolved_loaded_by
        return out

    from pyspark.sql import functions as F

    return (
        df.withColumn("_pipeline_run_id", F.lit(resolved_run_id))
        .withColumn("_pipeline_name", F.lit(pipeline_name))
        .withColumn("_pipeline_environment", F.lit(environment))
        .withColumn("_source_table", F.lit(source_table))
        .withColumn("_record_loaded_timestamp", F.current_timestamp())
        .withColumn("_notebook_name", F.lit(resolved_notebook_name))
        .withColumn("_loaded_by", F.lit(resolved_loaded_by))
    )


def standardize_columns(
    df: Any,
    run_id: str | None = None,
    pipeline_name: str | None = None,
    environment: str | None = None,
    source_table: str | None = None,
    datetime_columns: dict[str, str] | None = None,
    business_keys: list[str] | None = None,
    bucket_column: str | None = None,
    engine: str = "auto",
):
    """Deprecated wrapper for :func:`add_runtime_audit_columns`.

    Parameters
    ----------
    df : pyspark.sql.DataFrame or pandas.DataFrame
        DataFrame to enrich.
    run_id, pipeline_name, environment, source_table : str, optional
        Runtime audit values passed through to
        :func:`add_runtime_audit_columns`.
    datetime_columns, business_keys, bucket_column : optional
        Deprecated compatibility parameters. They are ignored by this wrapper
        because datetime features, hashes, and buckets are no longer part of
        the default pipeline-standard column path.
    engine : {"auto", "spark", "pandas"}, default="auto"
        DataFrame engine.

    Returns
    -------
    pyspark.sql.DataFrame or pandas.DataFrame
        DataFrame enriched with runtime audit columns only.

    Warns
    -----
    DeprecationWarning
        Always emitted to guide callers to :func:`add_runtime_audit_columns`.
    """
    if datetime_columns or business_keys or bucket_column:
        warnings.warn(
            "standardize_columns no longer adds datetime, hash, or bucket columns; "
            "use add_runtime_audit_columns for the standard audit path and add specialized columns explicitly where needed.",
            DeprecationWarning,
            stacklevel=2,
        )
    else:
        warnings.warn(
            "standardize_columns is deprecated; use add_runtime_audit_columns instead.",
            DeprecationWarning,
            stacklevel=2,
        )
    return add_runtime_audit_columns(
        df,
        run_id=run_id,
        pipeline_name=pipeline_name,
        environment=environment,
        source_table=source_table,
        engine=engine,
    )
