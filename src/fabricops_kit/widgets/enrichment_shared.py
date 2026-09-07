"""Focused helpers for environment-aware metadata enrichment."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
from fabricops_kit.io.shared import read_lakehouse_table_core

CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
ENRICHMENT_TABLE = "METADATA_ENRICHMENT"


def _rows(value: Any) -> list[dict[str, Any]]:
    """Return row-like values as dictionaries."""
    source = value.collect() if hasattr(value, "collect") else value
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in (source or [])]


def _sort_timestamp(value: Any) -> tuple[int, Any]:
    """Return a deterministic sort value for metadata timestamps."""
    text = str(value or "").strip().replace("Z", "+00:00")
    try:
        parsed = value if isinstance(value, datetime) else datetime.fromisoformat(text)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return 1, parsed.timestamp()
    except (TypeError, ValueError):
        return 0, text


def catalogue_table_options(catalogue_rows: Any, *, environment_name: str) -> list[dict[str, str]]:
    """Return current table-level Catalogue options for one environment."""
    latest: dict[str, dict[str, Any]] = {}
    for row in _rows(catalogue_rows):
        if str(row.get("environment_name") or "") != str(environment_name):
            continue
        if str(row.get("metadata_level") or "").lower() != "table":
            continue
        table_id = str(row.get("table_id") or "").strip()
        if not table_id:
            continue
        order = (_sort_timestamp(row.get("last_profiled_at")), str(row.get("_activity_id") or ""))
        current = latest.get(table_id)
        if current is None or order > current["_sort_key"]:
            latest[table_id] = {**row, "_sort_key": order}
    options: list[dict[str, str]] = []
    for table_id, row in latest.items():
        if row.get("is_active") is False:
            continue
        schema_name = str(row.get("schema_name") or "").strip()
        layer = str(row.get("layer") or "").strip()
        table_name = str(row.get("table_name") or table_id)
        context = " / ".join(value for value in (layer, schema_name) if value)
        label = f"{table_name} — {context}" if context else table_name
        options.append({"table_id": table_id, "label": label, "table_name": table_name, "layer": layer, "schema_name": schema_name})
    return sorted(options, key=lambda row: (row["label"].casefold(), row["table_id"]))


def latest_enrichment_values(rows: Any, *, environment_name: str) -> dict[tuple[str, str, int, str, str], dict[str, Any]]:
    """Return latest enrichment by level, contract version, column, and type."""
    latest: dict[tuple[str, str, int, str, str], dict[str, Any]] = {}
    for row in _rows(rows):
        if str(row.get("environment_name") or "") != str(environment_name):
            continue
        level = str(row.get("enrichment_level") or "").lower()
        contract_id = str(row.get("contract_id") or "")
        contract_version = int(row.get("contract_version") or 0)
        column_id = str(row.get("column_id") or "")
        enrichment_type = str(row.get("enrichment_type") or "")
        if not level or not contract_id or contract_version < 1 or not enrichment_type:
            continue
        key = (level, contract_id, contract_version, column_id, enrichment_type)
        order = (
            _sort_timestamp(row.get("_committed_at")),
            str(row.get("_activity_id") or ""),
            str(row.get("enrichment_id") or ""),
        )
        current = latest.get(key)
        if current is None or order > current["_sort_key"]:
            latest[key] = {**row, "_sort_key": order}
    for row in latest.values():
        row.pop("_sort_key", None)
    return latest


def _enrichment_values(
    current_values: dict[tuple[str, str, int, str, str], dict[str, Any]],
    *,
    level: str,
    contract_id: str,
    contract_version: int,
    column_id: str = "",
) -> dict[str, str]:
    """Return enrichment values for one Catalogue identity."""
    result: dict[str, str] = {}
    for (stored_level, stored_contract_id, stored_version, stored_column_id, enrichment_type), row in current_values.items():
        if (stored_level, stored_contract_id, stored_version, stored_column_id) != (level, contract_id, contract_version, column_id):
            continue
        result[enrichment_type] = str(row.get("value") or "")
    return result


def catalogue_table_browser_state(
    catalogue_rows: Any,
    table_id: str,
    *,
    environment_name: str,
    contract_id: str,
    contract_version: int,
    current_values: dict[tuple[str, str, int, str, str], dict[str, Any]],
) -> dict[str, Any]:
    """Return one environment-specific Catalogue table and its column history."""
    rows = [
        row
        for row in _rows(catalogue_rows)
        if str(row.get("environment_name") or "") == str(environment_name)
        and str(row.get("table_id") or "") == str(table_id)
    ]
    if not rows:
        raise ValueError(f"No Catalogue rows found for table_id={table_id!r} in environment {environment_name!r}.")
    table_rows = [row for row in rows if str(row.get("metadata_level") or "").lower() == "table"]
    if not table_rows:
        raise ValueError(f"Catalogue table identity {table_id!r} has no table-level row in environment {environment_name!r}.")
    table_row = max(
        table_rows,
        key=lambda row: (_sort_timestamp(row.get("last_profiled_at")), str(row.get("_activity_id") or "")),
    )
    columns: list[dict[str, Any]] = []
    latest_columns: dict[str, dict[str, Any]] = {}
    for row in rows:
        if str(row.get("metadata_level") or "").lower() != "column":
            continue
        column_id = str(row.get("column_id") or "").strip()
        if not column_id:
            continue
        order = (_sort_timestamp(row.get("last_profiled_at")), str(row.get("_activity_id") or ""))
        current = latest_columns.get(column_id)
        if current is None or order > current["_sort_key"]:
            latest_columns[column_id] = {**row, "_sort_key": order}
    for column_id, row in latest_columns.items():
        active = row.get("is_active") is not False
        columns.append(
            {
                "column_id": column_id,
                "column_name": str(row.get("column_name") or column_id),
                "status": "current" if active else "removed",
                "last_observed_at": row.get("last_profiled_at"),
                "enrichment_values": _enrichment_values(
                    current_values,
                    level="column",
                    contract_id=contract_id,
                    contract_version=contract_version,
                    column_id=column_id,
                ),
            }
        )
    columns.sort(key=lambda row: (row["status"] != "current", row["column_name"].casefold(), row["column_id"]))
    return {
        "table_id": table_id,
        "contract_id": contract_id,
        "contract_version": contract_version,
        "environment_name": environment_name,
        "table_name": str(table_row.get("table_name") or table_id),
        "table_row": dict(table_row),
        "current_columns": [row for row in columns if row["status"] == "current"],
        "removed_columns": [row for row in columns if row["status"] == "removed"],
        "all_historical_columns": columns,
        "current_enrichment_values": {
            "table": _enrichment_values(current_values, level="table", contract_id=contract_id, contract_version=contract_version),
        },
    }


__all__ = [
    "CATALOGUE_TABLE",
    "ENRICHMENT_TABLE",
    "catalogue_table_browser_state",
    "catalogue_table_options",
    "latest_enrichment_values",
]
