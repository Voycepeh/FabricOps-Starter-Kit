"""Standalone DQ guardrail authoring widget."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import html
import json
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.widgets import shared


DQ_RULE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "not_null": {"label": "Not null", "parameters": {}},
    "null_rate_below": {"label": "Null rate below", "parameters": {"max_null_percent": {"label": "Maximum null percent", "type": "number", "required": True}}},
    "non_empty_string": {"label": "Non-empty string", "parameters": {}},
    "unique": {"label": "Unique", "parameters": {}},
    "accepted_values": {"label": "Accepted values", "parameters": {"allowed_values": {"label": "Accepted values", "type": "list", "required": True}}},
    "not_in_values": {"label": "Excluded values", "parameters": {"blocked_values": {"label": "Excluded values", "type": "list", "required": True}}},
    "between": {"label": "Between", "parameters": {"min_value": {"label": "Minimum", "type": "number", "required": True}, "max_value": {"label": "Maximum", "type": "number", "required": True}}},
    "greater_than": {"label": "Greater than", "parameters": {"value": {"label": "Value", "type": "number", "required": True}}},
    "greater_than_or_equal": {"label": "Greater than or equal", "parameters": {"value": {"label": "Value", "type": "number", "required": True}}},
    "less_than": {"label": "Less than", "parameters": {"value": {"label": "Value", "type": "number", "required": True}}},
    "less_than_or_equal": {"label": "Less than or equal", "parameters": {"value": {"label": "Value", "type": "number", "required": True}}},
    "regex_match": {"label": "Matches pattern", "parameters": {"regex_pattern": {"label": "Pattern", "type": "text", "required": True}}},
    "date_not_future": {"label": "Date is not in the future", "parameters": {}},
    "date_between": {"label": "Date between", "parameters": {"min_value": {"label": "Earliest date", "type": "text", "required": True}, "max_value": {"label": "Latest date", "type": "text", "required": True}}},
    "freshness": {"label": "Freshness", "parameters": {"max_age_days": {"label": "Maximum age (days)", "type": "integer", "required": True, "default": 1}}},
    "max_age_days": {"label": "Maximum age in days", "parameters": {"max_age_days": {"label": "Maximum age (days)", "type": "integer", "required": True, "default": 1}}},
}


def _parameter_control(widgets: Any, definition: Mapping[str, Any], value: Any) -> Any:
    kind = definition.get("type")
    common = shared.widget_common(widgets, str(definition.get("label") or "Parameter"))
    if kind == "number":
        return widgets.FloatText(value=float(value or 0), **common)
    if kind == "integer":
        return widgets.IntText(value=int(value if value is not None else definition.get("default", 0)), **common)
    if kind == "list":
        text = ", ".join(str(item) for item in value) if isinstance(value, (list, tuple)) else str(value or "")
        return widgets.Text(value=text, **common)
    return widgets.Text(value=str(value or definition.get("default", "")), **common)


def _collect_parameters(definition: Mapping[str, Any], controls: Mapping[str, Any]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for name, parameter in definition.get("parameters", {}).items():
        value = controls[name].value
        if parameter.get("type") == "list":
            value = [item.strip() for item in str(value).split(",") if item.strip()]
        if parameter.get("required") and (value is None or value == "" or value == []):
            raise ValueError(f"{parameter['label']} is required.")
        values[name] = value
    return values


def widget_author_dq_rules(
    *,
    spark_session: Any,
    context: dict[str, Any] | None = None,
    rule_type: str = "not_null",
    selected_columns: Iterable[str] | None = None,
    parameters: Mapping[str, Any] | None = None,
    severity: str = "warning",
    bypass_reason: str = "",
    source_notebook_type: str = "01_governance",
    created_by_role: str = "governance",
    commit: bool = False,
) -> dict[str, Any]:
    """Render standalone, rule-driven DQ guardrail authoring controls.

    Parameters
    ----------
    spark_session : Any
        Fabric Spark session used to read profiled targets and save DQ rules.
    context : dict[str, Any], optional
        Advanced override for the active ``FABRIC_CONTEXT``.
    rule_type : str, default="not_null"
        Initially selected canonical DQ rule type.
    selected_columns : Iterable[str], optional
        Columns initially selected on each resolved target.
    parameters : Mapping[str, Any], optional
        Initial structured values for the selected rule's controls.
    severity : str, default="warning"
        Initial failure severity.
    bypass_reason : str, default=""
        Reason used only when applying a rule immediately.
    source_notebook_type : str, default="01_governance"
        Notebook role recorded on authored metadata rows.
    created_by_role : str, default="governance"
        Actor role recorded on authored metadata rows.
    commit : bool, default=False
        Save the initial selection immediately.

    Returns
    -------
    dict[str, Any]
        Mutable selected-target state, controls, preview, and save actions.

    Raises
    ------
    ValueError
        If no profiled target exists, no column is selected, or a required rule
        parameter is missing.

    Notes
    -----
    Run after ``00_env_config`` in Microsoft Fabric. One canonical
    ``METADATA_GUARDRAIL`` DQ row is produced per selected column, with
    structured values serialized in ``rule_parameters_json``.

    Examples
    --------
    >>> form = widget_author_dq_rules(spark_session=spark)
    >>> form["controls"]["rule_type"].value
    'not_null'

    """
    from IPython import display as ip

    config, env, _ = resolve_fabric_context(context=context)
    widgets = shared.require_ipywidgets()
    state: dict[str, Any] = {}
    initial_parameters = dict(parameters or {})
    rule = widgets.Dropdown(
        options=[(definition["label"], name) for name, definition in DQ_RULE_DEFINITIONS.items()],
        value=rule_type if rule_type in DQ_RULE_DEFINITIONS else "not_null",
        **shared.widget_common(widgets, "DQ rule"),
    )
    parameter_box = widgets.VBox()
    parameter_controls: dict[str, Any] = {}
    column_box = widgets.VBox()
    column_controls: dict[str, Any] = {}
    severity_control = widgets.ToggleButtons(options=["warning", "error"], value=severity if severity in {"warning", "error"} else "warning", description="Severity")
    bypass = widgets.Textarea(value=bypass_reason, **shared.widget_common(widgets, "Apply-now reason", textarea=True))
    preview = widgets.Textarea(description="Preview", disabled=True, layout=widgets.Layout(width="100%", height="220px"))
    message = widgets.HTML()
    records_state: dict[str, list[dict[str, Any]]] = {"records": []}

    def render_parameters(*_: Any) -> None:
        parameter_controls.clear()
        definition = DQ_RULE_DEFINITIONS[rule.value]
        for name, spec in definition["parameters"].items():
            control = _parameter_control(widgets, spec, initial_parameters.get(name, spec.get("default")))
            control.observe(refresh_preview, names="value")
            parameter_controls[name] = control
        parameter_box.children = tuple(parameter_controls.values()) or (widgets.HTML("<i>This rule has no parameters.</i>"),)
        refresh_preview()

    def render_columns(selected_state: Mapping[str, Any]) -> None:
        column_controls.clear()
        selected = set(selected_columns or selected_state.get("columns", []))
        rows = [widgets.GridBox([widgets.HTML("<b>Apply</b>"), widgets.HTML("<b>Column name</b>"), widgets.HTML("<b>Data type</b>")], layout=widgets.Layout(grid_template_columns="70px 1fr 1fr", width="100%"))]
        types = {str(row.get("column_name")): str(row.get("data_type") or "") for row in selected_state.get("catalogue_profile_rows", [])}
        for name in selected_state.get("columns", []):
            control = widgets.Checkbox(value=name in selected, description="", indent=False)
            control.observe(refresh_preview, names="value")
            column_controls[name] = control
            rows.append(widgets.GridBox([control, widgets.HTML(f"<code>{html.escape(name)}</code>"), widgets.HTML(f"<code>{html.escape(types.get(name, ''))}</code>")], layout=widgets.Layout(grid_template_columns="70px 1fr 1fr", width="100%")))
        column_box.children = tuple(rows)
        refresh_preview()

    def build_records(*, action: str = "submit") -> list[dict[str, Any]]:
        columns = [name for name, control in column_controls.items() if control.value]
        if not columns:
            raise ValueError("Select at least one column.")
        return shared._dq_records_from_selection(state, rule_type=rule.value, selected_columns=columns, parameters=_collect_parameters(DQ_RULE_DEFINITIONS[rule.value], parameter_controls), severity=severity_control.value, bypass_reason=bypass.value.strip() if action == "apply_now" else "", action=action, source_notebook_type=source_notebook_type, created_by_role=created_by_role, config=config)

    def refresh_preview(*_: Any) -> None:
        if not state or not column_controls:
            return
        try:
            records_state["records"] = build_records()
            preview.value = json.dumps(records_state["records"], indent=2, default=str)
            message.value = ""
        except ValueError as exc:
            records_state["records"] = []
            preview.value = ""
            message.value = f"<b style='color:#b00020'>Validation error:</b> {html.escape(str(exc))}"

    def save(*, action: str = "submit") -> list[dict[str, Any]]:
        records = build_records(action=action)
        records_state["records"] = records
        shared._write_rule_records(records, config=config, env=env, spark_session=spark_session)
        message.value = f"<b style='color:green'>Saved {len(records)} DQ rule row(s) to METADATA_GUARDRAIL.</b>"
        return records

    state, target, target_controls = shared._load_guardrail_authoring_targets(config, env, spark_session=spark_session, widgets=widgets, on_change=render_columns)
    rule.observe(render_parameters, names="value")
    severity_control.observe(refresh_preview, names="value")
    bypass.observe(refresh_preview, names="value")
    render_parameters()
    save_button = widgets.Button(description="Save DQ rules", button_style="primary")
    save_button.on_click(lambda _: save())
    ui = shared.form_page(widgets, title="Author DQ Rules", description="Select a profiled target and configure canonical DQ rules.", children=[shared.form_section(widgets, title="Target", children=[target, target_controls["target_summary"]]), shared.form_section(widgets, title="Choose DQ rule", children=[rule, parameter_box]), shared.form_section(widgets, title="Applicable columns", children=[column_box]), shared.form_section(widgets, title="Failure behaviour", children=[severity_control, bypass]), shared.form_section(widgets, title="Preview", children=[preview]), shared.action_row(widgets, [save_button]), message])
    ip.display(ui)
    result = {"state": state, "records": records_state["records"], "controls": {"target": target, "rule_type": rule, "parameters": parameter_box, "parameter_controls": parameter_controls, "columns": column_controls, "severity": severity_control, "bypass_reason": bypass, **target_controls}, "build_records": build_records, "build_batch_records": build_records, "save": save, "save_button": save_button, "ui": ui}
    if commit:
        result["records"] = save(action="apply_now" if bypass_reason else "submit")
    return result
