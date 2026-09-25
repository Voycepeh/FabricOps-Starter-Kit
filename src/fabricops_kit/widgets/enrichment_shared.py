"""Focused helpers for environment-aware metadata enrichment."""

from __future__ import annotations

from datetime import datetime, timezone
import importlib
import json
from typing import Any

from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
from fabricops_kit.data_contract.shared import (
    normalize_guardrail_action,
    validate_sensitive_data_parameters,
)

CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
ENRICHMENT_TABLE = "METADATA_ENRICHMENT"
_PROFILE_CONTEXT_FIELDS = (
    "row_count", "non_null_count", "null_count", "null_percent",
    "distinct_count", "distinct_percent", "mean_value", "stddev_value",
        "min_value", "percentile_25_value", "median_value",
        "percentile_75_value", "max_value",
)
PII_TYPES = frozenset({"direct", "indirect", "none"})
PII_LABELS = {"direct": "Direct PII", "indirect": "Indirect PII", "none": "Not PII"}
STANDARD_DQ_TYPES = frozenset({"completeness", "uniqueness", "value_set", "range", "pattern"})


def build_ai_enrichment_context(
    catalogue_row: dict[str, Any],
    *,
    metadata_level: str,
    existing_description: str,
    profile_rows: Any = (),
) -> dict[str, Any]:
    """Build compact technical context for an Enrichment suggestion."""
    column_id = str(catalogue_row.get("column_id") or "")
    profiles = [
        {name: row.get(name) for name in _PROFILE_CONTEXT_FIELDS if row.get(name) is not None}
        for row in _rows(profile_rows)
        if not column_id or str(row.get("column_id") or "") == column_id
    ]
    return {
        "metadata_level": str(metadata_level),
        "table_name": str(catalogue_row.get("table_name") or ""),
        "column_name": str(catalogue_row.get("column_name") or ""),
        "data_type": str(catalogue_row.get("data_type") or ""),
        "existing_description": str(existing_description or ""),
        "profile_evidence": profiles[:3],
    }


def _invoke_fabric_ai(prompt: str) -> str:
    """Invoke the Microsoft Fabric AI Functions pandas extension."""
    importlib.import_module("synapse.ml.aifunc")
    pandas = importlib.import_module("pandas")
    frame = pandas.DataFrame([{"fabricops_prompt": prompt}])
    ai = getattr(frame, "ai", None)
    if ai is None or not hasattr(ai, "generate_response"):
        raise RuntimeError(
            "Microsoft Fabric AI Functions are unavailable. Run in an enabled Fabric runtime or disable AI Enrichment."
        )
    result = ai.generate_response("{fabricops_prompt}")
    return str(result.iloc[0]).strip()


def suggest_enrichment(
    context: dict[str, Any],
    *,
    description_prompt: str,
    invoke: Any = None,
) -> dict[str, str]:
    """Return one transient AI Description suggestion."""
    if not str(description_prompt).strip():
        raise ValueError("An AI Enrichment description prompt is required.")
    call = invoke or _invoke_fabric_ai
    context_json = json.dumps(context, sort_keys=True, default=str)
    description = str(call(f"{description_prompt.strip()}\n\nContext:\n{context_json}")).strip()
    return {"Description": description}


def build_ai_sensitive_data_context(state: dict[str, Any]) -> dict[str, Any]:
    """Build compact metadata-only evidence for Sensitive Data suggestions."""
    fields = (
        "row_count", "non_null_count", "null_count", "null_percent",
        "distinct_count", "distinct_percent", "mean_value", "stddev_value",
        "min_value", "percentile_25_value", "median_value",
        "percentile_75_value", "max_value",
    )
    columns = []
    for row in state.get("catalogue_profile_rows", []):
        columns.append({
            "column_id": str(row.get("column_id") or ""),
            "column_name": str(row.get("column_name") or ""),
            "data_type": str(row.get("data_type") or ""),
            "description": str(row.get("description") or ""),
            "classification": str(row.get("classification") or ""),
            "profile_evidence": {
                name: row.get(name) for name in fields if row.get(name) is not None
            },
            "frequency_evidence": list(row.get("frequency_evidence") or [])[:3],
        })
    return {
        "table_id": str(state.get("table_id") or ""),
        "table_name": str(state.get("table_name") or ""),
        "schema_name": str(state.get("schema_name") or ""),
        "layer": str(state.get("layer") or ""),
        "table_description": str(state.get("table_description") or ""),
        "table_classification": str(state.get("table_classification") or ""),
        "contract_id": str(state.get("contract_id") or ""),
        "contract_version": int(state.get("contract_version") or 0),
        "columns": columns,
    }


def suggest_sensitive_data(
    context: dict[str, Any], *, prompt: str, invoke: Any = None
) -> list[dict[str, Any]]:
    """Return validated transient Sensitive Data rule suggestions."""
    if not str(prompt).strip():
        raise ValueError("An AI Sensitive Data prompt is required.")
    allowed_columns = {
        str(row.get("column_name") or ""): str(row.get("column_id") or "")
        for row in context.get("columns", [])
        if str(row.get("column_name") or "") and str(row.get("column_id") or "")
    }
    instruction = (
        f"{prompt.strip()}\n\nSuggest advisory Sensitive Data rules using only this metadata context. "
        "Assess every supplied column as Direct PII, Indirect PII, or Not PII. "
        "Return JSON only as a list of objects with column, pii_type, reason, treatment, action, and parameters. "
        "Use pii_type values direct, indirect, or none. For none, treatment must be null, action must be null, "
        "and parameters must be an empty object. "
        "Allowed treatments: tokenize, mask, bucket, remove. Allowed actions: Warn, Block. "
        "Classification is only an input signal, not an automatic rule. Do not include raw values.\n\n"
        f"Context:\n{json.dumps(context, sort_keys=True, default=str)}"
    )
    raw = str((invoke or _invoke_fabric_ai)(instruction)).strip()
    if raw.startswith("```"):
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        candidates = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("AI Sensitive Data suggestion was not valid JSON.") from exc
    if not isinstance(candidates, list):
        raise ValueError("AI Sensitive Data suggestion must be a JSON list.")
    suggestions = []
    seen = set()
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("Each AI Sensitive Data suggestion must be a JSON object.")
        column_name = str(candidate.get("column") or "").strip()
        if column_name not in allowed_columns:
            raise ValueError(f"AI Sensitive Data suggestion referenced unknown column {column_name!r}.")
        if column_name in seen:
            continue
        pii_type = str(candidate.get("pii_type") or "").strip().lower()
        if pii_type not in PII_TYPES:
            raise ValueError(f"AI Sensitive Data suggestion for {column_name!r} has an invalid pii_type.")
        reason = str(candidate.get("reason") or "").strip()
        if not reason:
            raise ValueError(f"AI Sensitive Data suggestion for {column_name!r} requires a reason.")
        if pii_type == "none":
            if candidate.get("treatment") not in (None, "") or candidate.get("action") not in (None, ""):
                raise ValueError("Not PII suggestions cannot include a treatment or action.")
            if candidate.get("parameters") not in (None, {}):
                raise ValueError("Not PII suggestions cannot include treatment parameters.")
            suggestions.append({
                "column_name": column_name,
                "column_id": allowed_columns[column_name],
                "pii_type": pii_type,
                "pii_label": PII_LABELS[pii_type],
                "reason": reason,
                "treatment": None,
                "action": None,
                "parameters": {},
                "is_active": False,
            })
            seen.add(column_name)
            continue
        try:
            parameters = validate_sensitive_data_parameters({
                "scope": "column",
                "treatment": candidate.get("treatment"),
                **dict(candidate.get("parameters") or {}),
            })
            action = normalize_guardrail_action(candidate.get("action"))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                f"AI Sensitive Data suggestion for {column_name!r} is invalid: {exc}"
            ) from exc
        suggestions.append({
            "column_name": column_name,
            "column_id": allowed_columns[column_name],
            "pii_type": pii_type,
            "pii_label": PII_LABELS[pii_type],
            "reason": reason,
            "treatment": parameters.pop("treatment"),
            "action": action,
            "parameters": {key: value for key, value in parameters.items() if key != "scope"},
            "is_active": True,
        })
        seen.add(column_name)
    return suggestions


def build_ai_dq_context(state: dict[str, Any]) -> dict[str, Any]:
    """Build governed metadata/profile context without raw rows or internal identifiers."""
    fields = (
        "row_count", "non_null_count", "null_count", "null_percent",
        "distinct_count", "distinct_percent", "mean_value", "stddev_value",
        "min_value", "percentile_25_value", "median_value",
        "percentile_75_value", "max_value",
    )
    return {
        "table_name": str(state.get("table_name") or ""),
        "schema_name": str(state.get("schema_name") or ""),
        "layer": str(state.get("layer") or ""),
        "table_description": str(state.get("table_description") or ""),
        "table_classification": str(state.get("table_classification") or ""),
        "columns": [
            {
                "column_name": str(row.get("column_name") or ""),
                "data_type": str(row.get("data_type") or ""),
                "description": str(row.get("description") or ""),
                "classification": str(row.get("classification") or ""),
                "profile_evidence": {name: row.get(name) for name in fields if row.get(name) is not None},
                "frequency_evidence": list(row.get("frequency_evidence") or [])[:10],
            }
            for row in state.get("catalogue_profile_rows", [])
        ],
    }


def suggest_dq_rules(context: dict[str, Any], *, prompt: str, invoke: Any = None) -> list[dict[str, Any]]:
    """Return validated, transient suggestions for the five standard DQ families."""
    if not str(prompt).strip():
        raise ValueError("An AI Data Quality prompt is required.")
    allowed_columns = {
        str(row.get("column_name") or "") for row in context.get("columns", [])
        if str(row.get("column_name") or "")
    }
    instruction = f"""{prompt.strip()}

Return JSON only: a list of objects with rule_type, columns, parameters, rationale, and selected.
Allowed rule_type values: completeness, uniqueness, value_set, range, pattern.
Suggest only single-column rules. Never suggest relationships, conditional logic, SQL, Python, or executable code.
Completeness requires maximum_missing_percent and treat_blank_as_missing. Zero observed nulls alone is not requiredness evidence.
Uniqueness requires semantic ID/key evidence; current 100% distinctness alone is insufficient.
Value Set requires mode allow or block and a values list, only for stable categorical domains.
Range requires minimum and/or maximum plus both inclusivity booleans; observed extrema are evidence, not contract limits.
Pattern requires a regex only for clearly structured text. Use governed evidence only.

Context:
{json.dumps(context, sort_keys=True, default=str)}"""
    raw = str((invoke or _invoke_fabric_ai)(instruction)).strip()
    if raw.startswith("```"):
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        candidates = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("AI Data Quality suggestion was not valid JSON.") from exc
    if not isinstance(candidates, list):
        raise ValueError("AI Data Quality suggestion must be a JSON list.")
    suggestions = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("Each AI Data Quality suggestion must be a JSON object.")
        rule_type = str(candidate.get("rule_type") or "")
        if rule_type not in STANDARD_DQ_TYPES:
            raise ValueError(f"AI Data Quality suggestion used unsupported rule_type {rule_type!r}.")
        columns = candidate.get("columns")
        if not isinstance(columns, list) or len(columns) != 1 or columns[0] not in allowed_columns:
            raise ValueError("AI standard Data Quality suggestions require exactly one known column.")
        parameters = dict(candidate.get("parameters") or {})
        _validate_ai_dq_parameters(rule_type, parameters)
        suggestions.append({
            "rule_type": rule_type, "columns": list(columns), "parameters": parameters,
            "rationale": str(candidate.get("rationale") or "").strip(),
            "selected": bool(candidate.get("selected", True)),
        })
    return suggestions


def _validate_ai_dq_parameters(rule_type: str, parameters: dict[str, Any]) -> None:
    """Reject malformed or executable AI-authored standard-rule parameters."""
    expected = {
        "completeness": {"maximum_missing_percent", "treat_blank_as_missing"},
        "uniqueness": set(),
        "value_set": {"mode", "values"},
        "range": {"minimum", "maximum", "minimum_inclusive", "maximum_inclusive"},
        "pattern": {"pattern"},
    }[rule_type]
    if set(parameters) - expected:
        raise ValueError(f"AI {rule_type} suggestion contains unsupported parameters.")
    if rule_type == "completeness":
        value = parameters.get("maximum_missing_percent")
        if not isinstance(value, (int, float)) or not 0 <= value <= 100 or not isinstance(parameters.get("treat_blank_as_missing"), bool):
            raise ValueError("AI completeness parameters are invalid.")
    elif rule_type == "value_set":
        if parameters.get("mode") not in {"allow", "block"} or not isinstance(parameters.get("values"), list) or not parameters["values"]:
            raise ValueError("AI value_set parameters are invalid.")
    elif rule_type == "range":
        if parameters.get("minimum") is None and parameters.get("maximum") is None:
            raise ValueError("AI range requires minimum or maximum.")
        if not all(isinstance(parameters.get(name), bool) for name in ("minimum_inclusive", "maximum_inclusive")):
            raise ValueError("AI range inclusivity parameters are required booleans.")
    elif rule_type == "pattern":
        pattern = parameters.get("pattern")
        if not isinstance(pattern, str) or not pattern or "F." in pattern or "SELECT " in pattern.upper():
            raise ValueError("AI pattern parameters are invalid.")


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
                "catalogue_row": dict(row),
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
    "build_ai_enrichment_context",
    "build_ai_dq_context",
    "latest_enrichment_values",
    "suggest_enrichment",
    "suggest_dq_rules",
    "build_ai_sensitive_data_context",
    "suggest_sensitive_data",
    "PII_LABELS",
    "PII_TYPES",
]
