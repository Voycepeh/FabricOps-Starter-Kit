from __future__ import annotations

import ast
import importlib
import json
from datetime import datetime, timezone

from .metadata import build_metadata_column_key, build_metadata_table_key
from .config import DEFAULT_BUSINESS_CONTEXT_PROMPT_TEMPLATE

COLUMN_BUSINESS_CONTEXT_FROM_WIDGET: list[dict] = []
REJECTED_COLUMN_BUSINESS_CONTEXT_FROM_WIDGET: list[dict] = []
BUSINESS_CONTEXT_PROMPT = DEFAULT_BUSINESS_CONTEXT_PROMPT_TEMPLATE


def _prepare_business_context_profile_input(profile_rows: list[dict], table_name: str, table_context: str = "") -> list[dict]:
    out = []
    for row in profile_rows or []:
        out.append(
            {
                "table_name": table_name,
                "table_context": table_context,
                "column_name": row.get("column_name") or row.get("COLUMN_NAME"),
                "data_type": row.get("data_type") or row.get("DATA_TYPE"),
                "row_count": row.get("row_count") or row.get("ROW_COUNT"),
                "null_count": row.get("null_count") or row.get("NULL_COUNT"),
                "distinct_count": row.get("distinct_count") or row.get("DISTINCT_COUNT"),
                "observed_values_sample": row.get("observed_values_sample") or row.get("OBSERVED_VALUES_SAMPLE") or "",
            }
        )
    return out


def draft_business_context(prepared_profile_df, prompt_template: str = BUSINESS_CONTEXT_PROMPT, output_col: str = "ai_business_context_response"):
    """Run Fabric AI to draft column business context suggestions.

    Parameters
    ----------
    prepared_profile_df : pyspark.sql.DataFrame
        Profile input DataFrame prepared for prompt-template execution.
    prompt_template : str, default=BUSINESS_CONTEXT_PROMPT
        Prompt template used by Fabric AI.
    output_col : str, default=\"ai_business_context_response\"
        Output column containing AI response text.

    Returns
    -------
    pyspark.sql.DataFrame
        Input DataFrame enriched with AI response output.
    """
    ai = getattr(prepared_profile_df, "ai", None)
    if ai is None or not hasattr(ai, "generate_response"):
        raise RuntimeError("draft_business_context requires Fabric DataFrame.ai.generate_response.")
    return prepared_profile_df.ai.generate_response(prompt=prompt_template, is_prompt_template=True, output_col=output_col)


def _parse_ai_dict_response(text: str) -> dict:
    cleaned = str(text or "").strip()
    marker = "BUSINESS_CONTEXT"
    if marker in cleaned and "=" in cleaned:
        cleaned = cleaned.split("=", 1)[1].strip()
    try:
        obj = ast.literal_eval(cleaned)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        try:
            obj = json.loads(cleaned)
            return obj if isinstance(obj, dict) else {}
        except Exception:
            return {}


def _extract_column_business_context_suggestions(response_rows, response_col: str = "ai_business_context_response") -> list[dict]:
    """Parse AI suggestion rows from Spark DataFrames or ``list[dict]`` payloads."""
    out = []
    if hasattr(response_rows, "collect"):
        iterable = [r.asDict(recursive=True) if hasattr(r, "asDict") else dict(r) for r in response_rows.collect()]
    else:
        iterable = response_rows or []
    for row in iterable:
        parsed = _parse_ai_dict_response(row.get(response_col) or row.get("response") or row.get("ai_response") or "")
        if parsed:
            out.append(parsed)
    return out


def prepare_business_context_profile_input(profile_rows: list[dict], table_name: str, table_context: str = "") -> list[dict]:
    """Prepare profile rows for business context prompt drafting."""
    return _prepare_business_context_profile_input(profile_rows=profile_rows, table_name=table_name, table_context=table_context)


def extract_column_business_context_suggestions(response_rows, response_col: str = "ai_business_context_response") -> list[dict]:
    """Extract review-ready business context suggestion rows from AI responses."""
    return _extract_column_business_context_suggestions(response_rows=response_rows, response_col=response_col)


def get_reviewed_business_context_rows(status: str = "approved") -> list[dict]:
    """Return reviewed business context rows from widget state."""
    normalized = str(status or "").strip().lower()
    if normalized == "approved":
        return list(COLUMN_BUSINESS_CONTEXT_FROM_WIDGET)
    if normalized == "rejected":
        return list(REJECTED_COLUMN_BUSINESS_CONTEXT_FROM_WIDGET)
    raise ValueError("status must be 'approved' or 'rejected'.")


def _require_ipywidgets():
    widgets = importlib.import_module("ipywidgets")
    return widgets


def widget_review_business_context(suggestions: list[dict], environment_name: str, dataset_name: str, table_name: str, default_approval_status: str = "pending") -> list[dict]:
    """Display interactive approval widget.

    Notes
    -----
    Final approved/rejected rows are produced asynchronously via button callbacks
    and stored in module globals.
    """
    global COLUMN_BUSINESS_CONTEXT_FROM_WIDGET, REJECTED_COLUMN_BUSINESS_CONTEXT_FROM_WIDGET
    widgets = _require_ipywidgets()
    from IPython import display as ip

    approved, rejected = [], []
    action_history: list[str] = []
    state = {"i": 0}

    COLUMN_BUSINESS_CONTEXT_FROM_WIDGET.clear()
    REJECTED_COLUMN_BUSINESS_CONTEXT_FROM_WIDGET.clear()

    title = widgets.HTML("<h4>Review column business context</h4>")
    summary = widgets.HTML()
    approved_box = widgets.Textarea(description="Approved context", layout=widgets.Layout(width="900px", height="80px"))
    notes_box = widgets.Textarea(description="Notes", layout=widgets.Layout(width="900px", height="80px"))
    reviewer_box = widgets.Text(description="Reviewer notes", layout=widgets.Layout(width="900px"))
    status = widgets.HTML()
    btn_approve = widgets.Button(description="Approve", button_style="success")
    btn_reject = widgets.Button(description="Reject", button_style="danger")
    btn_undo = widgets.Button(description="Undo", button_style="warning")

    def curr():
        return suggestions[state["i"]] if state["i"] < len(suggestions) else None

    def load():
        row = curr()
        if row is None:
            summary.value = f"<b>Done.</b> Approved={len(approved)}, Rejected={len(rejected)}"
            approved_box.disabled = notes_box.disabled = reviewer_box.disabled = True
            return
        summary.value = f"<b>{state['i']+1}/{len(suggestions)}</b> column={row.get('column_name')}<br/>AI: {row.get('business_context','')}"
        approved_box.value = row.get("business_context", "")
        notes_box.value = row.get("notes", "")
        reviewer_box.value = ""

    def build_row(row, status_value):
        return {
            "environment_name": environment_name,
            "dataset_name": dataset_name,
            "table_name": table_name,
            "column_name": row.get("column_name"),
            "metadata_table_key": build_metadata_table_key(environment_name, dataset_name, table_name),
            "metadata_column_key": build_metadata_column_key(environment_name, dataset_name, table_name, row.get("column_name")),
            "ai_suggested_business_context": row.get("business_context", ""),
            "approved_business_context": approved_box.value.strip(),
            "business_context_notes": notes_box.value.strip(),
            "approval_status": status_value,
            "reviewer_notes": reviewer_box.value.strip(),
            "approved_by": None,
            "approved_at": datetime.now(timezone.utc).isoformat() if status_value == "approved" else None,
        }

    def _sync_globals():
        COLUMN_BUSINESS_CONTEXT_FROM_WIDGET.clear()
        COLUMN_BUSINESS_CONTEXT_FROM_WIDGET.extend(approved)
        REJECTED_COLUMN_BUSINESS_CONTEXT_FROM_WIDGET.clear()
        REJECTED_COLUMN_BUSINESS_CONTEXT_FROM_WIDGET.extend(rejected)

    def on_approve(_):
        row = curr()
        if row is None:
            return
        approved.append(build_row(row, "approved"))
        action_history.append("approve")
        _sync_globals()
        state["i"] += 1
        load()

    def on_reject(_):
        row = curr()
        if row is None:
            return
        rejected.append(build_row(row, "rejected"))
        action_history.append("reject")
        _sync_globals()
        state["i"] += 1
        load()

    def on_undo(_):
        if not action_history:
            return
        last = action_history.pop()
        if last == "reject" and rejected:
            rejected.pop()
        elif last == "approve" and approved:
            approved.pop()
        _sync_globals()
        state["i"] = max(0, state["i"] - 1)
        load()

    btn_approve.on_click(on_approve)
    btn_reject.on_click(on_reject)
    btn_undo.on_click(on_undo)
    load()
    ip.display(widgets.VBox([title, summary, approved_box, notes_box, reviewer_box, widgets.HBox([btn_approve, btn_reject, btn_undo]), status]))
    return None



def write_business_context(spark, *, rows: list[dict], metadata_path, table_name: str = "METADATA_COLUMN_BUSINESS_CONTEXT", mode: str = "append"):
    """Persist approved business context rows via metadata writer."""
    from .metadata import write_column_business_context
    return write_column_business_context(spark=spark, rows=rows, metadata_path=metadata_path, table_name=table_name, mode=mode)
