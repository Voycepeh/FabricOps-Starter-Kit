"""Shared Guardrail authoring helpers for standalone widgets."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import hashlib
import json
from typing import Any

from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types
from fabricops_kit.config.shared import is_table_not_found_error
from fabricops_kit.io.shared import (
    configured_lakehouse_schema,
    read_lakehouse_table_core,
    write_lakehouse_table_core,
)
from fabricops_kit.pipeline.guardrail_shared import canonical_guardrail_rule_record
from fabricops_kit.widgets import shared

CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
PROFILED_TABLE = "METADATA_DATA_PROFILED"
GUARDRAIL_TABLE = "METADATA_GUARDRAIL"


def _stable_json(value: Any) -> str:
    """Serialize authoring parameters deterministically."""
    return json.dumps(value, default=str, sort_keys=True, separators=(",", ":"))


def latest_rule(
    existing_rules: Iterable[Mapping[str, Any]],
    guardrail_type: str,
    *,
    rule_id: str | None = None,
) -> dict[str, Any]:
    """Return the newest matching normalized Guardrail row."""
    matches = []
    for raw in existing_rules or ():
        row = dict(raw)
        if str(row.get("guardrail_type") or "") != guardrail_type:
            continue
        if rule_id is not None and str(row.get("rule_id") or "") != rule_id:
            continue
        matches.append(row)
    matches.sort(
        key=lambda row: (
            int(row.get("guardrail_version") or 0),
            str(row.get("_committed_at") or ""),
        ),
        reverse=True,
    )
    return matches[0] if matches else {}


def rule_parameters(rule: Mapping[str, Any]) -> dict[str, Any]:
    """Parse one normalized Guardrail parameter payload."""
    raw = rule.get("rule_parameters_json") or "{}"
    try:
        return json.loads(raw) if isinstance(raw, str) else dict(raw or {})
    except (TypeError, json.JSONDecodeError):
        return {}


def _column_id_for_name(state: Mapping[str, Any], column_name: str) -> str:
    """Resolve one visible column name to its canonical Catalogue column ID."""
    name = str(column_name or "").strip()
    column_ids = dict(state.get("column_ids") or {})
    column_id = str(column_ids.get(name) or "").strip()
    if not name or not column_id:
        raise ValueError(
            f"Column {name!r} does not resolve to a canonical column_id for the selected table."
        )
    return column_id


def _build_guardrail_rule_id(
    *,
    table_id: str,
    column_id: str,
    guardrail_type: str,
    rule_id: str,
    identity_parameters: Mapping[str, Any] | None = None,
) -> str:
    """Build a stable identity for one logical normalized Guardrail rule."""
    payload = {
        "table_id": str(table_id),
        "column_id": str(column_id or ""),
        "guardrail_type": str(guardrail_type),
        "rule_id": str(rule_id),
        "identity_parameters": dict(identity_parameters or {}),
    }
    return f"guardrail_{hashlib.sha256(_stable_json(payload).encode('utf-8')).hexdigest()}"


def _next_guardrail_version(
    existing_rules: Iterable[Mapping[str, Any]], guardrail_rule_id: str
) -> int:
    """Return the next append-only Guardrail version for one logical rule."""
    versions = [
        int(row.get("guardrail_version") or 0)
        for row in existing_rules or ()
        if str(row.get("guardrail_rule_id") or "") == guardrail_rule_id
    ]
    return max(versions, default=0) + 1


def build_rule_record(
    state: Mapping[str, Any],
    *,
    guardrail_type: str,
    rule_id: str,
    rule_type: str,
    parameters: Mapping[str, Any] | None = None,
    severity: str = "warning",
    column_name: str = "",
    identity_parameters: Mapping[str, Any] | None = None,
    guardrail_version: int | None = None,
    is_active: bool = True,
) -> dict[str, Any]:
    """Build one Stage 4A Guardrail row without obsolete identity or review fields."""
    table_id = str(state.get("table_id") or "").strip()
    environment_name = str(state.get("environment_name") or "").strip()
    if not table_id:
        raise ValueError("A selected profiled table with a canonical table_id is required.")
    if not environment_name:
        raise ValueError("The selected profiled table must have an environment_name.")
    column_id = _column_id_for_name(state, column_name) if column_name else ""
    guardrail_rule_id = _build_guardrail_rule_id(
        table_id=table_id,
        column_id=column_id,
        guardrail_type=guardrail_type,
        rule_id=rule_id,
        identity_parameters=identity_parameters,
    )
    version = guardrail_version or _next_guardrail_version(
        state.get("existing_rules") or (), guardrail_rule_id
    )
    return {
        "guardrail_rule_id": guardrail_rule_id,
        "guardrail_version": int(version),
        "table_id": table_id,
        "column_id": column_id,
        "environment_name": environment_name,
        "guardrail_type": str(guardrail_type),
        "rule_id": str(rule_id),
        "rule_type": str(rule_type),
        "rule_parameters_json": _stable_json(dict(parameters or {})),
        "severity": str(severity),
        "is_active": bool(is_active),
    }


def dq_records_from_selection(
    state: Mapping[str, Any],
    *,
    rule_id: str,
    selected_columns: Iterable[str],
    parameters: Mapping[str, Any] | None = None,
    severity: str = "warning",
    column_selection: str = "independent",
) -> list[dict[str, Any]]:
    """Build canonical DQ authoring rows for the selected rule semantics."""
    columns = [str(column) for column in selected_columns]
    available = set(state.get("columns") or ())
    if any(column not in available for column in columns):
        raise ValueError("Selected DQ columns must come from the selected profiled table.")
    values = dict(parameters or {})
    if column_selection == "independent":
        return [
            build_rule_record(
                state,
                guardrail_type="dq",
                rule_id=rule_id,
                rule_type=rule_id,
                column_name=column,
                parameters={"columns": [column], **values},
                severity=severity,
            )
            for column in columns
        ]

    column_ids = [_column_id_for_name(state, column) for column in columns]
    identity_parameters: dict[str, Any] = {"column_ids": column_ids, **values}
    condition_column = str(values.get("condition_column") or "").strip()
    if condition_column:
        identity_parameters["condition_column_id"] = _column_id_for_name(
            state, condition_column
        )
    return [
        build_rule_record(
            state,
            guardrail_type="dq",
            rule_id=rule_id,
            rule_type=rule_id,
            parameters={"columns": columns, **values},
            severity=severity,
            identity_parameters=identity_parameters,
        )
    ]


def canonicalize_records(
    records: list[dict[str, Any]],
    *,
    config: Any,
    env: str,
) -> list[dict[str, Any]]:
    """Normalize authored Guardrail rows before the widget-owned shared write call."""
    return [
        canonical_guardrail_rule_record(record, config=config, env=env)
        for record in records
    ]


def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
    if rows_or_df is None:
        return []
    if hasattr(rows_or_df, "collect"):
        rows_or_df = rows_or_df.collect()
    return [
        row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        for row in rows_or_df
    ]


def read_metadata_table_or_empty(
    config: Any,
    env: str,
    table_name: str,
    *,
    spark_session: Any,
) -> list[dict[str, Any]]:
    """Read a metadata table and return row dictionaries, or an empty list if absent."""
    try:
        frame = read_lakehouse_table_core(
            table_name,
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            context={"config": config, "env": env},
            spark_session=spark_session,
        )
    except Exception as exc:
        if is_table_not_found_error(exc):
            return []
        raise
    return _coerce_rows(frame)


def write_rule_records(
    records: list[dict[str, Any]],
    *,
    config: Any,
    env: str,
    spark_session: Any,
) -> None:
    """Append canonical rule records to ``METADATA_GUARDRAIL``."""
    if not records:
        return
    write_lakehouse_table_core(
        spark_session.createDataFrame(
            [coerce_metadata_row_types(GUARDRAIL_TABLE, record) for record in records]
        ),
        GUARDRAIL_TABLE,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
        mode="append",
    )


def load_guardrail_authoring_targets(
    config: Any,
    env: str,
    *,
    spark_session: Any,
    widgets: Any,
    on_change: Any | None = None,
) -> tuple[dict[str, Any], Any, dict[str, Any]]:
    """Resolve independently selectable profiled targets through normalized Catalogue IDs."""
    catalogue = read_metadata_table_or_empty(
        config, env, CATALOGUE_TABLE, spark_session=spark_session
    )
    profiles = read_metadata_table_or_empty(
        config, env, PROFILED_TABLE, spark_session=spark_session
    )
    rules = read_metadata_table_or_empty(
        config, env, GUARDRAIL_TABLE, spark_session=spark_session
    )
    if not catalogue or not profiles:
        raise ValueError("No profiled Catalogue table is available for Guardrail authoring.")

    table_rows = {
        str(row.get("table_id") or ""): dict(row)
        for row in catalogue
        if str(row.get("environment_name") or env) == env
        and str(row.get("metadata_level") or "").lower() == "table"
        and str(row.get("table_id") or "").strip()
    }
    profile_table_ids = {
        str(row.get("table_id") or "")
        for row in profiles
        if str(row.get("environment_name") or env) == env
        and str(row.get("table_id") or "").strip()
    }
    selectable_ids = sorted(set(table_rows) & profile_table_ids)
    if not selectable_ids:
        raise ValueError(
            "METADATA_DATA_PROFILED has no table that resolves to METADATA_DATA_CATALOGUE."
        )

    def label(table_id: str) -> str:
        row = table_rows[table_id]
        location = " / ".join(
            value
            for value in (
                str(row.get("store_type") or ""),
                str(row.get("layer") or ""),
                str(row.get("schema_name") or ""),
                str(row.get("table_name") or ""),
            )
            if value
        )
        return location or table_id

    target = widgets.Dropdown(
        options=[(label(table_id), table_id) for table_id in selectable_ids],
        **shared.widget_common(widgets, "Profiled table"),
    )
    summary = widgets.HTML()
    state: dict[str, Any] = {}

    def refresh(*_: Any) -> None:
        table_id = str(target.value or "")
        table = table_rows[table_id]
        table_profiles = [
            dict(row)
            for row in profiles
            if str(row.get("environment_name") or env) == env
            and str(row.get("table_id") or "") == table_id
        ]
        latest = max(
            table_profiles,
            key=lambda row: (
                str(row.get("_committed_at") or ""),
                str(row.get("profile_snapshot_id") or ""),
            ),
        )
        snapshot_id = str(latest.get("profile_snapshot_id") or "")
        if snapshot_id:
            snapshot = [
                row
                for row in table_profiles
                if str(row.get("profile_snapshot_id") or "") == snapshot_id
            ]
        else:
            latest_at = str(latest.get("_committed_at") or "")
            snapshot = [
                row
                for row in table_profiles
                if str(row.get("_committed_at") or "") == latest_at
            ]

        catalogue_columns = {
            str(row.get("column_id") or ""): dict(row)
            for row in catalogue
            if str(row.get("environment_name") or env) == env
            and str(row.get("table_id") or "") == table_id
            and str(row.get("metadata_level") or "").lower() == "column"
            and str(row.get("column_id") or "").strip()
        }
        evidence = []
        for profile in snapshot:
            column_id = str(profile.get("column_id") or "")
            catalogue_column = catalogue_columns.get(column_id)
            if not catalogue_column:
                continue
            column_name = str(catalogue_column.get("column_name") or "").strip()
            if not column_name:
                continue
            evidence.append(
                {
                    "table_id": table_id,
                    "column_id": column_id,
                    "column_name": column_name,
                    "data_type": str(profile.get("data_type") or ""),
                    "profile_id": str(profile.get("profile_id") or ""),
                    "profile_snapshot_id": snapshot_id,
                    "_committed_at": profile.get("_committed_at"),
                }
            )
        evidence.sort(key=lambda row: row["column_name"].casefold())
        if not evidence:
            raise ValueError(
                "The selected profile snapshot has no columns that resolve to Catalogue column IDs."
            )
        existing_rules = [
            dict(row)
            for row in rules
            if str(row.get("environment_name") or env) == env
            and str(row.get("table_id") or "") == table_id
        ]
        state.clear()
        state.update(
            {
                "environment_name": env,
                "table_id": table_id,
                "table_name": str(table.get("table_name") or ""),
                "store_type": str(table.get("store_type") or ""),
                "layer": str(table.get("layer") or ""),
                "schema_name": str(table.get("schema_name") or ""),
                "profile_snapshot_id": snapshot_id,
                "columns": [row["column_name"] for row in evidence],
                "column_ids": {
                    row["column_name"]: row["column_id"] for row in evidence
                },
                "catalogue_profile_rows": evidence,
                "existing_rules": existing_rules,
            }
        )
        summary.value = (
            f"<b>Columns:</b> {len(evidence)} · <b>Existing rules:</b> {len(existing_rules)} · "
            f"<b>table_id:</b> <code>{table_id}</code>"
        )
        if on_change is not None:
            on_change(state)

    target.observe(refresh, names="value")
    refresh()
    return state, target, {"target_summary": summary, "refresh_target": refresh}
