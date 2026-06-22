"""Profiling resolver helpers for dataframe schemas and selected columns."""

from __future__ import annotations


_DEFAULT_PROFILE_EXCLUDE_COLUMNS = {
    "_pipeline_run_id",
    "_pipeline_name",
    "_pipeline_environment",
    "_source_table",
    "_record_loaded_timestamp",
    "_notebook_name",
    "_loaded_by",
    "_dq_check_status",
    "_dq_failed_rules",
    # Technical columns excluded from profile outputs.
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
    "_fabricops_run_id",
    "_fabricops_pipeline_name",
    "_fabricops_created_at",
    "_dq_check_status",
    "_dq_failed_rules",
}
_DEFAULT_PROFILE_EXCLUDE_PREFIXES = ("_fabricops_", "_dq_")


def _get_profiled_columns(df, exclude_columns: list[str] | set[str] | None = None) -> list[str]:
    """Return non-technical column names from a Spark DataFrame.

    Parameters
    ----------
    df : Any
        Spark DataFrame-like object with a ``dtypes`` attribute.
    exclude_columns : list[str] | set[str] | None, optional
        Additional columns to exclude from profiling.

    Returns
    -------
    list[str]
        Eligible business columns to profile.

    """
    excluded = set(_DEFAULT_PROFILE_EXCLUDE_COLUMNS)
    if exclude_columns:
        excluded.update(exclude_columns)
    return [
        name
        for name, _dtype in df.dtypes
        if name not in excluded and not any(str(name).startswith(prefix) for prefix in _DEFAULT_PROFILE_EXCLUDE_PREFIXES)
    ]


def _is_min_max_supported_type(data_type: str) -> bool:
    """Return whether min/max aggregation is safe for a Spark type string."""
    value = (data_type or "").lower()
    unsupported = ("array", "map", "struct", "binary")
    if any(token in value for token in unsupported):
        return False
    supported = (
        "tinyint",
        "smallint",
        "int",
        "bigint",
        "float",
        "double",
        "decimal",
        "date",
        "timestamp",
        "string",
        "char",
        "varchar",
    )
    return any(token in value for token in supported)

