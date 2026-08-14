"""Public widget entrypoint for ``widget_review_guardrail_governance``."""

from __future__ import annotations

import importlib
import json

from fabricops_kit.widgets import shared as _governance_review
from fabricops_kit.config.shared import resolve_fabric_context

from typing import Any, Mapping



def widget_review_guardrail_governance(
    state: Mapping[str, Any],
    *,
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Render governance policy and shared rule-review controls.

    Parameters
    ----------
    state : Mapping[str, Any]
        Guardrail state with existing guardrail rule records to review.
    spark_session : Any, optional
        Fabric Spark session used when saving governance review decisions.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context.

    Returns
    -------
    dict[str, Any]
        Rendered controls and review actions for notebook automation.

    """
    return _guardrail_governance_review_widget_workflow(state, spark_session=spark_session, context=context)


def _guardrail_governance_review_widget_workflow(state: Mapping[str, Any], *, spark_session: Any = None, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render interactive 03 governance policy and shared rule-review controls.

    Parameters
    ----------
    state : mapping
        Selected table state. The state may
        include ``existing_rules`` from ``METADATA_GUARDRAIL``.
    spark_session : Any, optional
        Spark session used for save actions.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    dict[str, Any]
        Widget state with controls and callable guardrail review actions.

    """
    config, env, _context = resolve_fabric_context(context=context)
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    guardrail_rules = [dict(row, _record_kind="guardrail") for row in list(state.get("existing_rules") or [])]
    all_records = guardrail_rules
    reviewable = [row for row in all_records if str(row.get("review_state") or row.get("review_status") or "") in {"pending_governance_review", "active_pending_governance_review", "self_approved", "governance_approved"}]

    def _label(row: Mapping[str, Any], idx: int) -> tuple[str, int]:
        label = f"guardrail · {row.get('review_status')} · {row.get('guardrail_type')} · {row.get('rule_type')} · {row.get('column_name') or '_table'}"
        return label, idx

    record_options = [_label(row, idx) for idx, row in enumerate(reviewable)]
    selected_record = widgets.Dropdown(options=record_options or [("No proposed, bypassed, or active records", -1)], description="Record", layout=widgets.Layout(width="820px"))
    replacement_key = widgets.Text(description="Supersedes/replacement", layout=widgets.Layout(width="620px"))
    history_rows = _governance_review.load_rule_review_history(all_records, metadata_table_key=str(state.get("metadata_table_key") or ""), table_name=str(state.get("table_name") or ""))
    history = widgets.HTML("<pre>" + json.dumps(history_rows, indent=2, default=str) + "</pre>")
    status = widgets.HTML(f"<b>Current governance:</b> {state.get('governance_mode', 'ungoverned')} · <b>Approval policy:</b> {state.get('approval_policy', 'no_approval_required')}")
    message = widgets.HTML()
    records_state: dict[str, Any] = {"last_record": None}

    approve_button = widgets.Button(description="Approve", button_style="success")
    approve_activate_button = widgets.Button(description="Approve and activate", button_style="success")
    reject_button = widgets.Button(description="Reject", button_style="danger")
    replace_button = widgets.Button(description="Replace record", button_style="warning")
    deactivate_button = widgets.Button(description="Deactivate", button_style="warning")

    def _selected_record_row() -> dict[str, Any]:
        if selected_record.value == -1:
            raise ValueError("No reviewable record is selected.")
        return reviewable[int(selected_record.value)]

    def save_record_action(action: str) -> dict[str, Any]:
        selected = _selected_record_row()
        row = _governance_review.apply_governance_rule_action(selected, action, superseded_by_rule_key=replacement_key.value, config=config)
        target_table = _governance_review.GUARDRAIL_TABLE
        rows_to_write = row if isinstance(row, list) else [row]
        for review_row in rows_to_write:
            review_row.pop("_record_kind", None)
        records_state["last_record"] = row
        if spark_session is None or config is None or env is None:
            message.value = "<b>Preview only:</b> FABRIC_CONTEXT/context and spark_session are required to save review action."
            return row
        _governance_review._write_rule_records(rows_to_write, config=config, env=env, spark_session=spark_session)
        message.value = f"<b style='color:green'>Saved {action} review event to {target_table}.</b>"
        return row

    approve_button.on_click(lambda _: save_record_action("approve"))
    approve_activate_button.on_click(lambda _: save_record_action("approve_and_activate"))
    reject_button.on_click(lambda _: save_record_action("reject"))
    replace_button.on_click(lambda _: save_record_action("replace"))
    deactivate_button.on_click(lambda _: save_record_action("deactivate"))

    ui = widgets.VBox([
        widgets.HTML("<h3>Governance policy and guardrail review</h3>"),
        widgets.HTML("<p>01_governance owns the standard governance review workflow. Review guardrail rule intent from METADATA_GUARDRAIL.</p>"),
        widgets.HTML("<p><b>Filters:</b> Guardrail requests · Bypass pending review · Active approved · Rejected · Superseded · View approval logs.</p>"),
        status,
        widgets.HTML("<h4>Proposed, bypassed, and active records requiring governance decisions</h4>"),
        selected_record,
        replacement_key,
        widgets.HBox([approve_activate_button, approve_button, reject_button, replace_button, deactivate_button]),
        widgets.HTML("<h4>Approval logs and record history by table</h4>"),
        history,
        message,
    ])
    ip.display(ui)
    return {"controls": {"selected_record": selected_record, "selected_rule": selected_record, "replacement_key": replacement_key}, "save_record_action": save_record_action, "save_rule_action": save_record_action, "last_record": records_state, "ui": ui}
