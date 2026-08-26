"""Public owner for committing a successful pipeline watermark checkpoint."""

from __future__ import annotations

from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import configured_lakehouse_schema, get_spark_session, write_lakehouse_table_core


_CHECKPOINT_TABLE = "METADATA_SOURCE_WATERMARK_CHECKPOINT"


def commit_pipeline_checkpoint(read_prep: dict[str, Any]) -> dict[str, Any] | None:
    """Commit a prepared watermark only after target persistence succeeds.

    Parameters
    ----------
    read_prep : dict
        Exact result returned by :func:`read_pipeline_prep`. Call this function
        only after transformation, Guardrails, and the physical target write
        have all succeeded.

    Returns
    -------
    dict or None
        The committed checkpoint record, or ``None`` when the source strategy
        did not produce a watermark candidate.

    Raises
    ------
    ValueError
        If the preparation result contains an invalid watermark candidate or
        inconsistent source identity.
    RuntimeError
        If Fabric configuration, Spark, or metadata persistence is unavailable.

    Notes
    -----
    This is the explicit success boundary for watermark processing.
    ``read_pipeline_prep`` never advances successful state. If a target write
    raises, do not call this function; the previous successful checkpoint then
    remains unchanged and the same bounded range is prepared on retry.

    Metadata and business targets may be separate Fabric items, so the target
    write and checkpoint append cannot form one cross-item transaction. Target
    writes used with watermark retries must therefore be idempotent.

    Examples
    --------
    >>> write_lakehouse_table(
    ...     write_prep["df"], "bookings",
    ...     mode=write_prep["mode"], options=write_prep["options"],
    ... )
    >>> committed = commit_pipeline_checkpoint(read_prep)
    >>> committed is None or committed["watermark_column"] == "modified_datetime"
    True

    See Also
    --------
    read_pipeline_prep, write_pipeline_prep

    """
    if not isinstance(read_prep, dict):
        raise ValueError("read_prep must be the dictionary returned by read_pipeline_prep().")
    candidate = read_prep.get("candidate_checkpoint")
    if candidate is None:
        return None
    if not isinstance(candidate, dict) or candidate.get("status") != "candidate":
        raise ValueError("candidate_checkpoint must be an uncommitted candidate from read_pipeline_prep().")
    source = read_prep.get("source")
    source_processing = read_prep.get("source_processing")
    if not isinstance(source, dict) or not str(source.get("table_id") or "").strip():
        raise ValueError("read_prep must contain the canonical source table identity.")
    if not isinstance(source_processing, dict) or source_processing.get("read_strategy") != "incremental_watermark":
        raise ValueError("A watermark candidate requires incremental_watermark source processing.")
    column = str(candidate.get("column") or "").strip()
    if column != source_processing.get("watermark_column") or candidate.get("value") is None:
        raise ValueError("The watermark candidate does not match the prepared source processing definition.")

    config, env, context = resolve_fabric_context()
    audit = build_runtime_audit_fields(config=config, env=env, runtime_context=context)
    record = {
        "environment_name": env,
        "table_id": source["table_id"],
        "watermark_column": column,
        "watermark_value": str(candidate["value"]),
        **audit,
    }
    spark = get_spark_session()
    frame = spark.createDataFrame(
        [coerce_metadata_row_types(_CHECKPOINT_TABLE, record)],
        schema=metadata_table_schema_registry()[_CHECKPOINT_TABLE],
    )
    write_lakehouse_table_core(
        frame,
        _CHECKPOINT_TABLE,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context=context,
        mode="append",
    )
    return record
