"""Read-only governance metadata lookup helpers."""

from __future__ import annotations

from typing import Any, Mapping

from .config.shared import resolve_fabric_context
from .io.shared import configured_lakehouse_schema, read_lakehouse_table_core

CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"


def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
    if rows_or_df is None:
        return []
    if hasattr(rows_or_df, "collect"):
        rows_or_df = rows_or_df.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]


def _catalogue_lookup_value(row: Mapping[str, Any], *names: str) -> Any:
    """Return the first non-empty present catalogue lookup value."""
    fallback = ""
    for name in names:
        if name in row:
            value = row[name]
            if value not in (None, ""):
                return value
            fallback = value
        upper = name.upper()
        if upper in row:
            value = row[upper]
            if value not in (None, ""):
                return value
            fallback = value
    return fallback


def _latest_metadata_catalogue_lookup_workflow(
    *,
    table_name: str,
    agreement: Mapping[str, Any] | None = None,
    metadata_schema: str | None = None,
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
) -> Any:
    """Return the latest metadata catalogue rows for an exploratory table lookup.

    Parameters
    ----------
    table_name : str
        Source table name to look up in ``METADATA_DATA_CATALOGUE``.
    agreement : mapping, optional
        Selected agreement context from :func:`get_selected_agreement`. When an
        agreement id or contract version is present, matching catalogue rows are
        preferred.
    metadata_schema : str, optional
        Explicit metadata Lakehouse schema from ``00_env_config``. When omitted,
        the configured metadata schema is resolved from the active context.
    spark_session : Any, optional
        Spark session used to read metadata and return display-friendly rows.
    context : dict, optional
        Advanced FabricOps context override. Defaults to the active
        ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    Any
        A Spark DataFrame when ``spark_session`` can create one; otherwise a
        list of dictionaries. Existing catalogue rows are limited to the latest
        profile group for the table. Missing metadata returns one friendly
        ``not_found`` row instead of raising.

    Notes
    -----
    This helper is read-only. It reads ``METADATA_DATA_CATALOGUE`` from the
    configured metadata target and does not write audit, approval, guardrail, or
    pipeline metadata.

    """
    config, env, resolved_context = resolve_fabric_context(context=context)
    requested_table = str(table_name or "").strip()
    if not requested_table:
        raise ValueError("table_name is required to look up metadata catalogue context.")
    agreement = dict(agreement or {})
    agreement_id = str(agreement.get("agreement_id") or "").strip()
    contract_version = str(agreement.get("agreement_contract_version") or agreement.get("contract_version") or "").strip()

    def _friendly_row(message: str) -> list[dict[str, Any]]:
        return [{"status": "not_found", "table_name": requested_table, "message": message}]

    try:
        catalogue_df = read_lakehouse_table_core(
            CATALOGUE_TABLE,
            target="metadata",
            schema=metadata_schema or configured_lakehouse_schema(config, env, "metadata"),
            context=resolved_context,
            spark_session=spark_session,
        )
        rows = _coerce_rows(catalogue_df)
    except Exception:
        rows = []

    matches = [
        row
        for row in rows
        if str(_catalogue_lookup_value(row, "table_name", "profiled_table_name") or "").strip() == requested_table
    ]
    if agreement_id:
        agreement_matches = [row for row in matches if str(_catalogue_lookup_value(row, "agreement_id") or "").strip() == agreement_id]
        if agreement_matches:
            matches = agreement_matches
    if contract_version:
        version_matches = [
            row
            for row in matches
            if str(_catalogue_lookup_value(row, "agreement_contract_version", "contract_version") or "").strip() == contract_version
        ]
        if version_matches:
            matches = version_matches

    if not matches:
        output_rows = _friendly_row(f"No metadata catalogue rows found for {requested_table}. Run 02_pipeline profiling to create governed catalogue evidence.")
    else:
        latest_key = max(
            str(_catalogue_lookup_value(row, "profiled_at", "run_timestamp", "created_at", "_committed_at", "profile_run_id") or "")
            for row in matches
        )
        output_rows = [
            row
            for row in matches
            if str(_catalogue_lookup_value(row, "profiled_at", "run_timestamp", "created_at", "_committed_at", "profile_run_id") or "") == latest_key
        ]

    if spark_session is not None and hasattr(spark_session, "createDataFrame"):
        return spark_session.createDataFrame(output_rows)
    return output_rows


def get_latest_metadata_catalogue(
    *,
    table_name: str,
    agreement: Mapping[str, Any] | None = None,
    metadata_schema: str | None = None,
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
) -> Any:
    """Return the latest metadata catalogue rows for an exploratory table lookup."""
    return _latest_metadata_catalogue_lookup_workflow(
        table_name=table_name,
        agreement=agreement,
        metadata_schema=metadata_schema,
        spark_session=spark_session,
        context=context,
    )
