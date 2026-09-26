"""Focused helpers for environment-aware metadata enrichment."""

from __future__ import annotations

import ast
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from io import StringIO
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
STANDARD_DQ_TYPES = frozenset({"completeness", "value_set", "range", "pattern"})
BUSINESS_RULE_TYPES = frozenset({
    "completeness", "uniqueness", "value_set", "range", "pattern",
    "column_relationship", "conditional_completeness", "conditional_values",
    "custom_expression",
})
BUSINESS_RULE_OPERATORS = frozenset({"=", "!=", ">", ">=", "<", "<="})


def build_ai_enrichment_context(
    catalogue_row: dict[str, Any],
    *,
    metadata_level: str,
    existing_description: str,
    profile_rows: Any = (),
    column_rows: Any = (),
) -> dict[str, Any]:
    """Build compact technical context for an Enrichment suggestion."""
    column_id = str(catalogue_row.get("column_id") or "")
    profiles = [
        {name: row.get(name) for name in _PROFILE_CONTEXT_FIELDS if row.get(name) is not None}
        for row in _rows(profile_rows)
        if not column_id or str(row.get("column_id") or "") == column_id
    ]
    columns = [
        {
            "column_name": str(row.get("column_name") or ""),
            "data_type": str(row.get("data_type") or ""),
        }
        for row in _rows(column_rows)
        if str(row.get("column_name") or "")
    ]
    return {
        "metadata_level": str(metadata_level),
        "table_name": str(catalogue_row.get("table_name") or ""),
        "column_name": str(catalogue_row.get("column_name") or ""),
        "data_type": str(catalogue_row.get("data_type") or ""),
        "existing_description": str(existing_description or ""),
        "table_columns": columns,
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
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
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
    guidance = ""
    if str(context.get("metadata_level") or "") == "table":
        guidance = (
            "\n\nWrite a concise business description of what the dataset represents and what it supports. "
            "Use grain and classification as context. Do not list or paraphrase columns. "
            "Do not mention technical or operational metadata. Do not repeat the grain verbatim. "
            "Do not explain the classification itself."
        )
    description = str(
        call(f"{description_prompt.strip()}{guidance}\n\nContext:\n{context_json}")
    ).strip()
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


def _normalize_ai_column_reference(
    value: Any, allowed_columns: dict[str, str]
) -> str:
    """Return a canonical known column name from tolerant AI output."""
    by_id = {column_id: column_name for column_name, column_id in allowed_columns.items()}

    def from_mapping(mapping: dict[str, Any]) -> str:
        name = str(mapping.get("column_name") or mapping.get("name") or "").strip()
        if name in allowed_columns:
            return name
        column_id = str(mapping.get("column_id") or "").strip()
        return by_id.get(column_id, "")

    if isinstance(value, dict):
        return from_mapping(value)

    text = str(value or "").strip()
    if text in allowed_columns:
        return text
    if text in by_id:
        return by_id[text]
    if text.startswith("{") and text.endswith("}"):
        parsed: Any = None
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(text)
            except (SyntaxError, ValueError):
                parsed = None
        if isinstance(parsed, dict):
            return from_mapping(parsed)
    return ""


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
        "The column field must be the supplied column_name string, not a column object. "
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
        column_ref = candidate.get("column")
        column_name = _normalize_ai_column_reference(column_ref, allowed_columns)
        if not column_name:
            continue
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


def suggest_grain_key(context: dict[str, Any], *, prompt: str, invoke: Any = None) -> dict[str, Any]:
    """Return one transient grain wording suggestion grounded by profiled key evidence."""
    if not str(prompt).strip():
        raise ValueError("An AI Grain prompt is required.")
    allowed_columns = {
        str(row.get("column_name") or "") for row in context.get("columns", [])
        if str(row.get("column_name") or "")
    }
    candidates = [
        candidate for candidate in context.get("profile_key_candidates", [])
        if isinstance(candidate, dict)
    ]
    key_columns: list[str] = []
    for candidate in candidates:
        columns = [str(name) for name in candidate.get("columns", [])]
        if columns and all(name in allowed_columns for name in columns):
            key_columns = columns
            break
    if not key_columns:
        single_candidates = [
            str(row.get("column_name") or "")
            for row in context.get("columns", [])
            if str(row.get("column_name") or "") in allowed_columns
            and float(row.get("distinct_percent") or 0) >= 100.0
            and float(row.get("null_percent") or 0) <= 0.0
        ]
        if single_candidates:
            key_columns = [single_candidates[0]]

    instruction = f"""{prompt.strip()}

The row-key candidate has already been determined deterministically from Engineering profiling evidence.
Do not choose, replace, expand, or reinterpret the key columns.
Your task is only to describe what one row represents in concise business language.
Do not enumerate the table schema, repeat technical metadata, or describe operational FabricOps fields.
Use the supplied key only as structural evidence for the row grain.
Return JSON only with grain and rationale.

Profiled row-key candidate:
{json.dumps(key_columns, default=str)}

Context:
{json.dumps(context, sort_keys=True, default=str)}"""
    raw = str((invoke or _invoke_fabric_ai)(instruction)).strip()
    if raw.startswith("```"):
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        candidate = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("AI Grain suggestion was not valid JSON.") from exc
    if not isinstance(candidate, dict):
        raise ValueError("AI Grain suggestion must be a JSON object.")
    return {
        "grain": str(candidate.get("grain") or "").strip(),
        "key_columns": key_columns,
        "rationale": str(candidate.get("rationale") or "").strip(),
    }

def suggest_dq_rules(context: dict[str, Any], *, prompt: str, invoke: Any = None) -> list[dict[str, Any]]:
    """Return validated, transient suggestions for the four column-level DQ families."""
    if not str(prompt).strip():
        raise ValueError("An AI Data Quality prompt is required.")
    allowed_columns = {
        str(row.get("column_name") or "") for row in context.get("columns", [])
        if str(row.get("column_name") or "")
    }
    instruction = f"""{prompt.strip()}

Return JSON only: a list of objects with rule_type, columns, parameters, rationale, and selected.
Allowed rule_type values: completeness, value_set, range, pattern.
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
        parameters = _normalize_ai_dq_parameters(
            rule_type, dict(candidate.get("parameters") or {})
        )
        _validate_ai_dq_parameters(rule_type, parameters)
        suggestions.append({
            "rule_type": rule_type, "columns": list(columns), "parameters": parameters,
            "rationale": str(candidate.get("rationale") or "").strip(),
            "selected": bool(candidate.get("selected", True)),
        })
    return suggestions


def _normalize_ai_dq_parameters(
    rule_type: str, parameters: dict[str, Any]
) -> dict[str, Any]:
    """Keep only canonical parameters supported by the selected DQ family."""
    expected = {
        "completeness": {"maximum_missing_percent", "treat_blank_as_missing"},
        "value_set": {"mode", "values"},
        "range": {"minimum", "maximum", "minimum_inclusive", "maximum_inclusive"},
        "pattern": {"pattern"},
    }[rule_type]
    return {key: value for key, value in parameters.items() if key in expected}


def _validate_ai_dq_parameters(rule_type: str, parameters: dict[str, Any]) -> None:
    """Reject malformed or executable AI-authored standard-rule parameters."""
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


def build_ai_business_rule_context(state: dict[str, Any]) -> dict[str, Any]:
    """Build governed metadata and DQ context for natural-language rule authoring."""
    columns = []
    for row in state.get("columns", []):
        column_name = str(row.get("column_name") or "").strip()
        if not column_name:
            continue
        profile = dict(row.get("profile") or {})
        profile_evidence = {
            name: profile.get(name)
            for name in _PROFILE_CONTEXT_FIELDS
            if profile.get(name) is not None
        }
        examples = [
            value for value in profile.get("example_values", [])
            if value not in (None, "")
        ][:3]
        if examples:
            profile_evidence["example_values"] = examples
        column = {
            "column_name": column_name,
            "data_type": str(row.get("data_type") or ""),
            "description": str(row.get("description") or ""),
            "classification": str(row.get("classification") or ""),
        }
        if profile_evidence:
            column["profile"] = profile_evidence
        columns.append(column)

    existing_dq_rules = []
    for row in state.get("existing_dq_rules", []):
        rule_type = str(row.get("rule_type") or "").strip()
        rule_columns = [
            str(name).strip()
            for name in row.get("columns", [])
            if str(name).strip()
        ]
        if not rule_type or not rule_columns:
            continue
        existing_dq_rules.append({
            "rule_type": rule_type,
            "columns": rule_columns,
            "parameters": dict(row.get("parameters") or {}),
        })

    return {
        "table_name": str(state.get("table_name") or ""),
        "schema_name": str(state.get("schema_name") or ""),
        "layer": str(state.get("layer") or ""),
        "table_description": str(state.get("table_description") or ""),
        "table_classification": str(state.get("table_classification") or ""),
        "columns": columns,
        "existing_dq_rules": existing_dq_rules,
    }


def suggest_business_rule(
    context: dict[str, Any],
    *,
    requirement: str,
    relevant_columns: list[str] | tuple[str, ...] = (),
    prompt: str,
    invoke: Any = None,
) -> list[dict[str, Any]]:
    """Resolve natural-language business intent into one or more atomic Guardrails."""
    business_requirement = str(requirement or "").strip()
    if not business_requirement:
        raise ValueError("Describe what must be true before generating DQ Rules.")
    if not str(prompt).strip():
        raise ValueError("An AI Business Rule prompt is required.")

    allowed_columns = {
        str(row.get("column_name") or "").strip()
        for row in context.get("columns", [])
        if str(row.get("column_name") or "").strip()
    }
    selected_columns = [
        str(name).strip() for name in relevant_columns if str(name).strip()
    ]
    unknown_selected = sorted(set(selected_columns).difference(allowed_columns))
    if unknown_selected:
        raise ValueError(
            "DQ Rule column constraint contains unknown columns: "
            + ", ".join(unknown_selected)
        )

    instruction = f"""{prompt.strip()}

Business requirement:
{business_requirement}

Optional column constraint selected by Governance:
{json.dumps(selected_columns)}

Return JSON only as an array containing one or more atomic rule objects.
Each object must contain requirement, rule_type, columns, parameters, and rationale.
Decompose compound requirements into the smallest independent enforceable rules. One condition that can fail independently should be one rule.
Resolve business-language column references against the governed table and column context. If the optional column constraint is empty, infer the required columns from the full governed context. If it is populated, use only those columns.
Do not invent columns. Do not return a rule that is already represented in existing_dq_rules.
Allowed rule_type values: completeness, uniqueness, value_set, range, pattern, column_relationship, conditional_completeness, conditional_values, custom_expression.
Resolve against every canonical FabricOps DQ pattern before using custom_expression. Use custom_expression if and only if none of the canonical patterns can faithfully represent that atomic requirement without changing its meaning.
Completeness: exactly one column; parameters maximum_missing_percent and treat_blank_as_missing.
Uniqueness: one or more columns; no rule-specific parameters. This is a repeatable uniqueness constraint, not the table Grain & Row Key. Do not infer or replace Grain & Row Key from a DQ Rule. Grain is a separate singular table definition authored in the Table workspace.
Value Set: exactly one column; parameters mode (allow or block) and non-empty values.
Range: exactly one column; parameters minimum and/or maximum plus minimum_inclusive and maximum_inclusive booleans.
Pattern: exactly one column; parameter pattern containing the governed regular expression.
Column Relationship: exactly two different columns; parameter operator using =, !=, >, >=, <, or <=.
Conditional Completeness: exactly two columns, condition column then required target column; parameters condition_operator (= or !=), condition_value, and treat_blank_as_missing.
Conditional Values: exactly two columns, condition column then target column; parameters condition_operator (= or !=), condition_value, mode (allow or block), and non-empty values.
Custom Expression: only when no pattern above is sufficient; parameters expression_language="pyspark" and expression.
A custom expression must be one safe PySpark boolean Column expression using only F.col("known_column"), F.lit(...), literals, comparisons, &, |, ~, arithmetic (+, -, *, /, %), and approved null/text methods already supported by FabricOps. Do not return imports, assignments, SQL, UDFs, eval/exec, file/network access, arbitrary Python calls, exponentiation, floor division, or matrix multiplication.
Observed profile and frequency values are evidence, not automatic contractual requirements. Never turn observed values into allowed values, mappings, or thresholds unless the business requirement explicitly states them.
Do not force a known pattern when it would weaken, broaden, or otherwise change the atomic requirement.

Context:
{json.dumps(context, sort_keys=True, default=str)}"""
    raw = str((invoke or _invoke_fabric_ai)(instruction)).strip()
    if raw.startswith("```"):
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        candidates = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("AI DQ Rule proposal was not valid JSON.") from exc
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("AI DQ Rule proposal must be a non-empty JSON array.")

    resolved: list[dict[str, Any]] = []
    for candidate in candidates:
        if not isinstance(candidate, dict):
            raise ValueError("Every AI DQ Rule proposal must be one JSON object.")

        atomic_requirement = str(
            candidate.get("requirement") or business_requirement
        ).strip()
        rule_type = str(candidate.get("rule_type") or "").strip()
        if rule_type not in BUSINESS_RULE_TYPES:
            raise ValueError(
                f"AI DQ Rule proposal used unsupported rule_type {rule_type!r}."
            )

        columns = candidate.get("columns")
        if not isinstance(columns, list) or not columns:
            raise ValueError(
                "AI DQ Rule proposal must reference at least one known column."
            )
        normalized_columns = [str(name).strip() for name in columns]
        if len(set(normalized_columns)) != len(normalized_columns):
            raise ValueError("AI DQ Rule proposal cannot repeat the same column.")
        if any(name not in allowed_columns for name in normalized_columns):
            raise ValueError("AI DQ Rule proposal referenced an unknown column.")
        if selected_columns and any(
            name not in selected_columns for name in normalized_columns
        ):
            raise ValueError(
                "AI DQ Rule proposal used a column outside the selected constraint."
            )

        parameters = dict(candidate.get("parameters") or {})
        if rule_type in STANDARD_DQ_TYPES:
            if len(normalized_columns) != 1:
                raise ValueError(f"{rule_type} requires exactly one known column.")
            canonical_parameters = _normalize_ai_dq_parameters(rule_type, parameters)
            _validate_ai_dq_parameters(rule_type, canonical_parameters)
            canonical_parameters.update({
                "columns": normalized_columns,
                "business_requirement": atomic_requirement,
            })
        elif rule_type == "uniqueness":
            if parameters:
                raise ValueError(
                    "Uniqueness proposal does not accept rule-specific parameters."
                )
            canonical_parameters = {
                "columns": normalized_columns,
                "business_requirement": atomic_requirement,
            }
        elif rule_type == "column_relationship":
            if len(normalized_columns) != 2:
                raise ValueError(
                    "Column Relationship requires exactly two known columns."
                )
            if normalized_columns[0] == normalized_columns[1]:
                raise ValueError(
                    "Column Relationship requires two different columns."
                )
            operator = str(parameters.get("operator") or "").strip()
            if operator not in BUSINESS_RULE_OPERATORS:
                raise ValueError(
                    "Column Relationship proposal used an unsupported operator."
                )
            canonical_parameters = {
                "columns": normalized_columns,
                "operator": operator,
                "business_requirement": atomic_requirement,
            }
        elif rule_type in {"conditional_completeness", "conditional_values"}:
            if (
                len(normalized_columns) != 2
                or normalized_columns[0] == normalized_columns[1]
            ):
                raise ValueError(
                    f"{rule_type} requires exactly two different known columns."
                )
            condition_operator = str(
                parameters.get("condition_operator") or ""
            ).strip()
            if condition_operator not in {"=", "!="}:
                raise ValueError(
                    f"{rule_type} condition_operator must be '=' or '!='."
                )
            if "condition_value" not in parameters:
                raise ValueError(f"{rule_type} requires condition_value.")
            canonical_parameters = {
                "columns": normalized_columns,
                "condition_operator": condition_operator,
                "condition_value": parameters["condition_value"],
                "business_requirement": atomic_requirement,
            }
            if rule_type == "conditional_completeness":
                if not isinstance(parameters.get("treat_blank_as_missing"), bool):
                    raise ValueError(
                        "conditional_completeness requires boolean "
                        "treat_blank_as_missing."
                    )
                canonical_parameters["treat_blank_as_missing"] = parameters[
                    "treat_blank_as_missing"
                ]
            else:
                if parameters.get("mode") not in {"allow", "block"}:
                    raise ValueError(
                        "conditional_values mode must be 'allow' or 'block'."
                    )
                if (
                    not isinstance(parameters.get("values"), list)
                    or not parameters["values"]
                ):
                    raise ValueError(
                        "conditional_values requires a non-empty values list."
                    )
                canonical_parameters.update({
                    "mode": parameters["mode"],
                    "values": list(parameters["values"]),
                })
        else:
            expression_language = str(
                parameters.get("expression_language") or ""
            ).strip().lower()
            expression = str(parameters.get("expression") or "").strip()
            if expression_language != "pyspark":
                raise ValueError(
                    "Custom Expression proposal must use "
                    "expression_language='pyspark'."
                )
            if not expression:
                raise ValueError(
                    "Custom Expression proposal requires a PySpark boolean expression."
                )
            lowered = expression.lower()
            forbidden = (
                "import ", "exec(", "eval(", "__", "spark.sql", "udf(", "open(",
                "subprocess", "requests.", "urllib", "os.", "sys.",
            )
            if any(token in lowered for token in forbidden):
                raise ValueError(
                    "Custom Expression proposal contains unsupported executable content."
                )
            canonical_parameters = {
                "expression_language": "pyspark",
                "expression": expression,
                "business_requirement": atomic_requirement,
                "columns": normalized_columns,
                "engineering_review_required": True,
            }

        resolved.append({
            "rule_type": rule_type,
            "columns": normalized_columns,
            "parameters": canonical_parameters,
            "business_requirement": atomic_requirement,
            "rationale": str(candidate.get("rationale") or "").strip(),
            "engineering_review_required": rule_type == "custom_expression",
        })

    return resolved

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
    "build_ai_business_rule_context",
    "latest_enrichment_values",
    "suggest_enrichment",
    "suggest_dq_rules",
    "suggest_business_rule",
    "build_ai_sensitive_data_context",
    "suggest_sensitive_data",
    "PII_LABELS",
    "PII_TYPES",
]
