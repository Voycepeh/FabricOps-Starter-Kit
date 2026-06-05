from __future__ import annotations

import importlib
import json
import ast
from typing import Any

from fabricops_kit.metadata import _now_utc_iso, _resolve_action_by, build_metadata_column_key, build_metadata_table_key
from fabricops_kit.config import DEFAULT_GOVERNANCE_PERSONAL_IDENTIFIER_PROMPT_TEMPLATE

_DEFAULT_WIDGET_CONFIG = {
    "confidentiality_labels": ["public", "confidential", "restricted"],
    "personal_identifier_options": ["not_personal_data", "direct_identifier", "indirect_identifier", "unknown"],
}

_WIDGET_APPROVED_ROWS: list[dict[str, Any]] = []
_WIDGET_REJECTED_ROWS: list[dict[str, Any]] = []
PDPA_PERSONAL_IDENTIFIER_PROMPT = DEFAULT_GOVERNANCE_PERSONAL_IDENTIFIER_PROMPT_TEMPLATE


def _build_governance_context(
    business_context: str,
    approved_usage: str,
    dataset_context: str,
    profile_context: str = "",
    glossary_context: str = "",
    steward_notes: str = "",
) -> dict[str, str]:
    """Build governance prompt context fields for notebook workflows."""
    return {
        "business_context": business_context or "",
        "approved_usage": approved_usage or "",
        "dataset_context": dataset_context or "",
        "profile_context": profile_context or "",
        "glossary_context": glossary_context or "",
        "steward_notes": steward_notes or "",
    }


def _prepare_governance_input(profile_rows: list[dict], table_name: str, column_contexts: list[dict]) -> list[dict]:
    """Join approved business context into profile rows for governance AI suggestions."""
    context_lookup = {r["column_name"]: r for r in column_contexts or [] if r.get("column_name")}
    out = []
    for row in profile_rows or []:
        col = row.get("column_name") or row.get("COLUMN_NAME")
        approved = (context_lookup.get(col) or {}).get("approved_business_context")
        if approved:
            out.append({**row, "table_name": table_name, "column_name": col, "approved_business_context": approved})
    return out


def prepare_governance_input(profile_rows: list[dict], table_name: str, column_contexts: list[dict]) -> list[dict]:
    """Prepare governance prompt input rows from profile evidence and approved context."""
    return _prepare_governance_input(profile_rows=profile_rows, table_name=table_name, column_contexts=column_contexts)


def draft_governance(prepared_profile_df, prompt: str | None = None, output_col: str = "ai_governance_response"):
    """Run Fabric AI personal-identifier suggestion prompt on prepared governance rows."""
    ai = getattr(prepared_profile_df, "ai", None)
    if ai is None or not hasattr(ai, "generate_response"):
        raise RuntimeError("draft_governance requires Fabric DataFrame.ai.generate_response.")
    return prepared_profile_df.ai.generate_response(prompt=prompt, is_prompt_template=True, output_col=output_col)


def _extract_pii_suggestions(response_rows, response_col: str = "ai_governance_response") -> list[dict]:
    """Extract governance suggestions from Spark/list response payloads."""
    def _parse_payload(value: Any) -> dict[str, Any]:
        if isinstance(value, dict):
            return value
        text = str(value or "").strip()
        if not text:
            return {}
        # Prefer JSON payloads from template prompts.
        try:
            obj = json.loads(text)
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
        # Fallback: tolerate simple Python dict assignment text.
        if "=" in text:
            text = text.split("=", 1)[1].strip()
        try:
            obj = ast.literal_eval(text)
            if isinstance(obj, dict):
                return obj
        except Exception:
            return {}
        return {}

    if hasattr(response_rows, "collect"):
        iterable = [r.asDict(recursive=True) if hasattr(r, "asDict") else dict(r) for r in response_rows.collect()]
    else:
        iterable = response_rows or []
    out = []
    for row in iterable:
        parsed = _parse_payload(row.get(response_col))
        if isinstance(parsed, dict) and parsed:
            out.append(parsed)
        else:
            out.append(
                {
                    "column_name": row.get("column_name"),
                    "ai_suggested_personal_identifier_classification": row.get("ai_suggested_personal_identifier_classification", "unknown"),
                    "confidentiality_label": row.get("confidentiality_label", "confidential"),
                    "approved_business_context": row.get("approved_business_context", ""),
                }
            )
    return [r for r in out if r]


def extract_governance_suggestions(response_rows, response_col: str = "ai_governance_response") -> list[dict]:
    """Extract review-ready governance suggestions from AI responses."""
    return _extract_pii_suggestions(response_rows=response_rows, response_col=response_col)


def widget_review_governance(suggestions: list[dict], environment_name: str, dataset_name: str, table_name: str) -> None:
    """Display governance review widget and capture approve/reject decisions in module state."""
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    _WIDGET_APPROVED_ROWS.clear()
    _WIDGET_REJECTED_ROWS.clear()

    idx = {"i": 0}
    action_history: list[str] = []
    summary = widgets.HTML()
    pid = widgets.Dropdown(options=_DEFAULT_WIDGET_CONFIG["personal_identifier_options"], description="Identifier")
    conf = widgets.Dropdown(options=_DEFAULT_WIDGET_CONFIG["confidentiality_labels"], description="Confidentiality")
    notes = widgets.Textarea(description="Reviewer notes", layout=widgets.Layout(width="900px", height="80px"))
    b1, b2, b3 = widgets.Button(description="Approve", button_style="success"), widgets.Button(description="Reject", button_style="danger"), widgets.Button(description="Undo", button_style="warning")

    def cur():
        return suggestions[idx["i"]] if idx["i"] < len(suggestions) else None

    def load():
        r = cur()
        if r is None:
            summary.value = f"<b>Done</b> approved={len(_WIDGET_APPROVED_ROWS)} rejected={len(_WIDGET_REJECTED_ROWS)}"
            return
        summary.value = f"{idx['i']+1}/{len(suggestions)} col={r.get('column_name')}<br/>Business context: {r.get('approved_business_context','')}"
        pid.value = r.get("ai_suggested_personal_identifier_classification", "unknown")
        conf.value = r.get("confidentiality_label", "confidential")
        notes.value = ""

    def on_approve(_):
        r = cur()
        _WIDGET_APPROVED_ROWS.append({
            "environment_name": environment_name,
            "dataset_name": dataset_name,
            "table_name": table_name,
            "column_name": r.get("column_name"),
            "metadata_table_key": build_metadata_table_key(environment_name, dataset_name, table_name),
            "metadata_column_key": build_metadata_column_key(environment_name, dataset_name, table_name, r.get("column_name")),
            "approved_business_context": r.get("approved_business_context", ""),
            "ai_suggested_personal_identifier_classification": r.get("ai_suggested_personal_identifier_classification", "unknown"),
            "approved_personal_identifier_classification": pid.value,
            "confidentiality_label": conf.value,
            "reviewer_notes": notes.value,
            "approved_at": _now_utc_iso(),
        })
        action_history.append("approve")
        idx["i"] += 1
        load()

    def on_reject(_):
        r = cur()
        _WIDGET_REJECTED_ROWS.append(dict(r))
        action_history.append("reject")
        idx["i"] += 1
        load()

    def on_undo(_):
        if _undo_last_action(action_history, _WIDGET_APPROVED_ROWS, _WIDGET_REJECTED_ROWS):
            idx["i"] = max(0, idx["i"] - 1)
            load()

    b1.on_click(on_approve)
    b2.on_click(on_reject)
    b3.on_click(on_undo)
    load()
    ip.display(widgets.VBox([summary, pid, conf, notes, widgets.HBox([b1, b2, b3])]))


def _coerce_row_dicts(rows) -> list[dict[str, Any]]:
    if rows is None:
        return []
    if hasattr(rows, "collect"):
        rows = rows.collect()
    out = []
    for r in rows:
        if hasattr(r, "asDict"):
            out.append(r.asDict(recursive=True))
        else:
            out.append(dict(r))
    return out


def _approved_widget_rows(agreement_context: dict[str, Any] | None = None, action_by: str | None = None) -> list[dict[str, Any]]:
    context = dict(agreement_context or {})
    approver = _resolve_action_by(action_by)
    rows = []
    for row in _WIDGET_APPROVED_ROWS:
        merged = dict(row)
        merged.update(context)
        merged["status"] = "approved"
        merged["approved_by"] = approver
        rows.append(merged)
    return rows



def _undo_last_action(action_history: list[str], approved_rows: list[dict[str, Any]], rejected_rows: list[dict[str, Any]]) -> bool:
    """Undo the most recent governance review action in widget state."""
    if not action_history:
        return False
    last = action_history.pop()
    if last == "approve" and approved_rows:
        approved_rows.pop()
        return True
    if last == "reject" and rejected_rows:
        rejected_rows.pop()
        return True
    return False

def write_governance(
    spark,
    *,
    metadata_path,
    approved_rows: list[dict[str, Any]] | None = None,
    agreement_context: dict[str, Any] | None = None,
    action_by: str | None = None,
    table_name: str = "METADATA_COLUMN_GOVERNANCE",
    mode: str = "append",
) -> list[dict[str, Any]]:
    """Persist approved governance rows to metadata table."""
    rows = approved_rows if approved_rows is not None else _approved_widget_rows(agreement_context=agreement_context, action_by=action_by)
    if not rows:
        return []
    writer = getattr(importlib.import_module("fabricops_kit.metadata"), "write_column_governance_context")
    writer(spark=spark, rows=rows, metadata_path=metadata_path, table_name=table_name, mode=mode)
    return rows


def load_governance(governance_rows, *, agreement_rows=None, agreement_id: str | None = None, dataset_name: str | None = None, table_name: str | None = None) -> dict[str, Any]:
    """Load approved governance metadata as read-only agreement context."""
    rows = _coerce_row_dicts(governance_rows)
    filtered = [
        r for r in rows
        if str(r.get("status", "")).lower() == "approved"
        and (not agreement_id or str(r.get("agreement_id") or "") == agreement_id)
        and (not dataset_name or str(r.get("dataset_name") or "") == dataset_name)
        and (not table_name or str(r.get("table_name") or "") == table_name)
    ]

    agreement_candidates = _coerce_row_dicts(agreement_rows) if agreement_rows is not None else filtered
    agreement_candidates = [
        r for r in agreement_candidates
        if (not agreement_id or str(r.get("agreement_id") or "") == agreement_id)
        and (not dataset_name or str(r.get("dataset_name") or "") == dataset_name)
        and (not table_name or str(r.get("table_name") or "") == table_name)
    ]

    agreement_payload = {}
    keys = ["agreement_id", "agreement_context", "approved_usage", "business_context", "ownership", "permissions", "restrictions", "classification", "sensitivity", "pii", "related_notebook_links", "approved_by", "approved_at"]
    if agreement_candidates:
        latest = sorted(agreement_candidates, key=lambda r: str(r.get("approved_at") or r.get("updated_at") or ""))[-1]
        agreement_payload = {k: latest.get(k) for k in keys if latest.get(k) is not None}

    columns = [
        {
            "column_name": r.get("column_name"),
            "approved_personal_identifier_classification": r.get("approved_personal_identifier_classification"),
            "confidentiality_label": r.get("confidentiality_label"),
            "approved_business_context": r.get("approved_business_context"),
            "reviewer_notes": r.get("reviewer_notes", ""),
            "metadata_column_key": r.get("metadata_column_key"),
        }
        for r in filtered
    ]
    return {"agreement_context": agreement_payload, "columns": columns}
