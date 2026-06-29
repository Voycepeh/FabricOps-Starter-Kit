"""Public widget entrypoint for ``widget_author_dq_rules``."""

from __future__ import annotations

import importlib
import json

from fabricops_kit import governance_review as _governance_review
from fabricops_kit.config.shared import resolve_fabric_context

from typing import Any, Iterable, Mapping



def widget_author_dq_rules(
    state: Mapping[str, Any],
    *,
    dq_authoring_mode: str = "manual",
    rule_type: str = "not_null",
    selected_columns: Iterable[str] | None = None,
    parameters: Mapping[str, Any] | None = None,
    severity: str = "warning",
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
    bypass_reason: str = "",
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
    commit: bool = False,
) -> dict[str, Any]:
    """Render interactive manual DQ rule authoring UI.

    Parameters
    ----------
    state : Mapping[str, Any]
        Guardrail target state returned by the target selector or prepared by a
        notebook workflow.
    dq_authoring_mode : str, default="manual"
        Authoring mode for the widget. The public widget supports manual rule
        authoring.
    rule_type : str, default="not_null"
        Initial DQ rule type selected in the widget.
    selected_columns : Iterable[str], optional
        Initial columns selected for the rule.
    parameters : Mapping[str, Any], optional
        Initial rule parameters.
    severity : str, default="warning"
        Initial rule severity.
    spark_session : Any, optional
        Fabric Spark session used when committing metadata rows.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context.
    bypass_reason : str, default=""
        Governance-bypass reason used when applying rules immediately.
    source_notebook_type : str, default="02_pipeline"
        Notebook role recorded on authored metadata rows.
    created_by_role : str, default="engineering"
        Actor role recorded on authored metadata rows.
    commit : bool, default=False
        When True, commit the selected rule instead of preview-only behavior.

    Returns
    -------
    dict[str, Any]
        Rendered controls and save actions for notebook automation.

    """
    return _dq_rule_authoring_widget_workflow(
        state,
        dq_authoring_mode=dq_authoring_mode,
        rule_type=rule_type,
        selected_columns=selected_columns,
        parameters=parameters,
        severity=severity,
        spark_session=spark_session,
        context=context,
        bypass_reason=bypass_reason,
        source_notebook_type=source_notebook_type,
        created_by_role=created_by_role,
        commit=commit,
    )


def _dq_rule_authoring_widget_workflow(
    state: Mapping[str, Any],
    *,
    dq_authoring_mode: str = "manual",
    rule_type: str = "not_null",
    selected_columns: Iterable[str] | None = None,
    parameters: Mapping[str, Any] | None = None,
    severity: str = "warning",
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
    bypass_reason: str = "",
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
    commit: bool = False,
) -> dict[str, Any]:
    """Render interactive manual DQ rule authoring UI.

    Parameters
    ----------
    state : mapping
        Handover state from :func:`widget_select_guardrail_target`.
    dq_authoring_mode : {"manual"}, default="manual"
        Manual DQ authoring mode.
    rule_type : str, default="not_null"
        Initial DQ rule type for manual mode.
    selected_columns : iterable of str, optional
        Initial batch-selected columns. Defaults to all selected table columns.
    parameters : mapping, optional
        Initial JSON rule parameters.
    severity : str, default="warning"
        Initial rule severity.
    spark_session : Any, optional
        Spark session used for saves.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.
    bypass_reason : str, optional
        Initial approval-bypass reason.
    source_notebook_type : {"02_pipeline", "03_governance"}, default="02_pipeline"
        Notebook type stamped on authored records.
    created_by_role : {"engineering", "governance", "system"}, default="engineering"
        Role stamped on authored records.
    commit : bool, default=False
        Whether to save the initial generated records immediately.

    Returns
    -------
    dict[str, Any]
        Widget state containing controls, generated records, and callable
        helpers for tests and notebook automation.

    """
    config, env, _context = resolve_fabric_context(context=context)
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    columns = list(state.get("columns") or [])
    initial_columns = tuple(column for column in (selected_columns or columns) if column in columns)
    existing_rules = list(state.get("existing_rules") or [])
    existing_dq = [row for row in existing_rules if str(row.get("guardrail_type") or "") == "dq"]
    mode = "manual"

    batch_rule_type = widgets.Dropdown(options=_governance_review.DQ_RULE_TYPES, value=rule_type if rule_type in _governance_review.DQ_RULE_TYPES else "not_null", description="Rule type")
    batch_columns = widgets.SelectMultiple(options=columns, value=initial_columns or tuple(columns), description="Columns", rows=min(max(len(columns), 4), 12), layout=widgets.Layout(width="420px"))
    batch_params = widgets.Textarea(value=json.dumps(parameters or {}, indent=2), description="Parameters", layout=widgets.Layout(width="760px", height="90px"))
    batch_severity = widgets.ToggleButtons(options=["warning", "error"], value=severity if severity in {"warning", "error"} else "warning", description="Severity")

    search_column = widgets.Combobox(options=columns, value=columns[0] if columns else "", description="Column")
    individual_rule_type = widgets.Dropdown(options=_governance_review.DQ_RULE_TYPES, value=rule_type if rule_type in _governance_review.DQ_RULE_TYPES else "not_null", description="Rule")
    individual_params = widgets.Textarea(value="{}", description="Parameters", layout=widgets.Layout(width="760px", height="90px"))
    bypass_box = widgets.Textarea(value=bypass_reason, description="Bypass reason", layout=widgets.Layout(width="760px", height="70px"))
    preview = widgets.Textarea(description="Preview", disabled=True, layout=widgets.Layout(width="900px", height="220px"))
    history = widgets.HTML("<pre>" + json.dumps(existing_dq, indent=2, default=str) + "</pre>")
    message = widgets.HTML()
    records_state: dict[str, Any] = {"records": []}

    save_draft_button = widgets.Button(description="Save draft", button_style="")
    submit_button = widgets.Button(description="Submit for governance review", button_style="success")
    apply_now_button = widgets.Button(description="Apply now", button_style="warning")
    save_one_draft_button = widgets.Button(description="Save selected rule as draft", button_style="")
    submit_one_button = widgets.Button(description="Submit selected rule for governance review", button_style="success")
    apply_one_button = widgets.Button(description="Apply selected rule now", button_style="warning")

    def _batch_parameters() -> dict[str, Any]:
        try:
            return json.loads(batch_params.value or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError("Parameters must be valid JSON") from exc

    def _individual_parameters() -> dict[str, Any]:
        try:
            return json.loads(individual_params.value or "{}")
        except json.JSONDecodeError as exc:
            raise ValueError("Individual parameters must be valid JSON") from exc

    def load_existing_individual(*_: Any) -> None:
        rule = _governance_review._latest_rule(existing_dq, "dq", individual_rule_type.value, search_column.value)
        params = _governance_review._rule_params(rule)
        params.pop("columns", None)
        individual_params.value = json.dumps(params, indent=2, default=str)

    def build_batch_records(*, action: str = "submit", use_bypass: bool = False) -> list[dict[str, Any]]:
        selected_action = "apply_now" if use_bypass else action
        reason = bypass_box.value.strip() if selected_action == "apply_now" else ""
        return _governance_review._dq_records_from_selection(state, rule_type=batch_rule_type.value, selected_columns=list(batch_columns.value), parameters=_batch_parameters(), severity=batch_severity.value, bypass_reason=reason, action=selected_action, source_notebook_type=source_notebook_type, created_by_role=created_by_role, config=config)

    def build_individual_record(*, action_type: str = "created", action: str = "submit", use_bypass: bool = False) -> list[dict[str, Any]]:
        selected_action = "apply_now" if use_bypass else action
        reason = bypass_box.value.strip() if selected_action == "apply_now" else ""
        return _governance_review._dq_records_from_selection(state, rule_type=individual_rule_type.value, selected_columns=[search_column.value], parameters=_individual_parameters(), severity=batch_severity.value, bypass_reason=reason, action_type=action_type, action=selected_action, source_notebook_type=source_notebook_type, created_by_role=created_by_role, config=config)

    def refresh_preview(*_: Any) -> None:
        try:
            records_state["records"] = build_batch_records(action="submit")
            preview.value = json.dumps(records_state["records"], indent=2, default=str)
            message.value = ""
        except Exception as exc:
            preview.value = ""
            message.value = f"<b style='color:#b00020'>Validation error:</b> {exc}"

    def save_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        records_state["records"] = records
        if spark_session is None or config is None or env is None:
            message.value = "<b>Preview only:</b> FABRIC_CONTEXT/context and spark_session are required to save."
            return records
        _governance_review._write_rule_records(records, config=config, env=env, spark_session=spark_session)
        message.value = f"<b style='color:green'>Saved {len(records)} DQ rule row(s) to METADATA_GUARDRAIL_RULES.</b>"
        return records

    def save_batch(*, action: str = "submit", use_bypass: bool = False) -> list[dict[str, Any]]:
        return save_records(build_batch_records(action="apply_now" if use_bypass else action))

    def save_individual(*, action_type: str = "created", action: str = "submit", use_bypass: bool = False) -> list[dict[str, Any]]:
        return save_records(build_individual_record(action_type=action_type, action="apply_now" if use_bypass else action))

    for control in (batch_rule_type, batch_columns, batch_params, batch_severity, bypass_box):
        control.observe(lambda change: refresh_preview(), names="value")
    for control in (search_column, individual_rule_type):
        control.observe(lambda change: load_existing_individual(), names="value")
    save_draft_button.on_click(lambda _: save_batch(action="draft"))
    submit_button.on_click(lambda _: save_batch(action="submit"))
    apply_now_button.on_click(lambda _: save_batch(action="apply_now"))
    save_one_draft_button.on_click(lambda _: save_individual(action_type="created", action="draft"))
    submit_one_button.on_click(lambda _: save_individual(action_type="created", action="submit"))
    apply_one_button.on_click(lambda _: save_individual(action_type="created", action="apply_now"))
    load_existing_individual()
    refresh_preview()
    if commit:
        save_batch(action="apply_now" if bypass_reason else "submit")

    ui = widgets.VBox([
        widgets.HTML("<h3>Author DQ rules</h3>"),
        widgets.HTML(f"<b>Mode:</b> {mode} · <b>Table:</b> {state.get('dataset_name', '')}.{state.get('table_name', '')} · <b>Governance:</b> {state.get('governance_mode', 'ungoverned')}"),
        widgets.HTML("<h4>Batch by rule type</h4>"),
        widgets.HBox([batch_rule_type, batch_columns, batch_severity]),
        batch_params,
        widgets.HTML("<h4>Individual rule editing</h4>"),
        widgets.HBox([search_column, individual_rule_type]),
        individual_params,
        widgets.HTML("<h4>Existing rule history</h4>"),
        history,
        bypass_box,
        preview,
        widgets.HBox([save_draft_button, submit_button, apply_now_button]),
        widgets.HBox([save_one_draft_button, submit_one_button, apply_one_button]),
        message,
    ])
    ip.display(ui)
    return {"records": records_state["records"], "controls": {"batch_rule_type": batch_rule_type, "batch_columns": batch_columns, "batch_params": batch_params, "search_column": search_column, "individual_rule_type": individual_rule_type, "individual_params": individual_params, "apply_now_reason": bypass_box, "bypass_reason": bypass_box}, "build_batch_records": build_batch_records, "build_individual_record": build_individual_record, "save_batch": save_batch, "save_individual": save_individual, "save_draft_button": save_draft_button, "submit_button": submit_button, "apply_now_button": apply_now_button, "save_one_draft_button": save_one_draft_button, "submit_one_button": submit_one_button, "apply_one_button": apply_one_button, "ui": ui}
