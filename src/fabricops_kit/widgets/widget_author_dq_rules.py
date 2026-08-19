"""Standalone DQ guardrail authoring widget."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import html
import json
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.guardrail_metadata import canonical_guardrail_rule_record
from fabricops_kit.pipeline.guardrails_shared import DQ_COMPARISON_OPERATORS
from fabricops_kit.widgets import shared


DQ_RULE_DEFINITIONS: dict[str, dict[str, Any]] = {
    "missing_values": {
        "label": "Missing values",
        "column_selection": "independent",
        "parameters": {
            "maximum_null_percent": {
                "label": "Maximum null percent",
                "type": "number",
                "required": True,
                "default": 0,
            }
        },
    },
    "blank_text": {"label": "Blank text", "column_selection": "independent", "parameters": {}},
    "unique_values": {"label": "Unique values", "column_selection": "independent", "parameters": {}},
    "unique_combination": {
        "label": "Unique combination",
        "column_selection": "group",
        "minimum_columns": 2,
        "parameters": {},
    },
    "allowed_values": {
        "label": "Allowed values",
        "column_selection": "independent",
        "parameters": {"allowed_values": {"label": "Allowed values", "type": "list", "required": True}},
    },
    "blocked_values": {
        "label": "Blocked values",
        "column_selection": "independent",
        "parameters": {"blocked_values": {"label": "Blocked values", "type": "list", "required": True}},
    },
    "value_range": {
        "label": "Value range",
        "column_selection": "independent",
        "at_least_one_of": ("minimum", "maximum"),
        "parameters": {
            "minimum": {"label": "Minimum", "type": "optional_scalar"},
            "minimum_inclusive": {"label": "Include minimum", "type": "boolean", "default": True},
            "maximum": {"label": "Maximum", "type": "optional_scalar"},
            "maximum_inclusive": {"label": "Include maximum", "type": "boolean", "default": True},
        },
    },
    "text_pattern": {
        "label": "Text pattern",
        "column_selection": "independent",
        "parameters": {"pattern": {"label": "Pattern", "type": "text", "required": True}},
    },
    "required_when": {
        "label": "Required when",
        "column_selection": "conditional",
        "minimum_columns": 1,
        "parameters": {
            "condition_column": {"label": "Condition column", "type": "column", "required": True},
            "condition_operator": {"label": "Condition operator", "type": "operator", "required": True},
            "condition_value": {"label": "Condition value", "type": "scalar", "required": True},
        },
    },
    "conditional_value": {
        "label": "Conditional value",
        "column_selection": "conditional",
        "minimum_columns": 1,
        "maximum_columns": 1,
        "parameters": {
            "condition_column": {"label": "Condition column", "type": "column", "required": True},
            "condition_operator": {"label": "Condition operator", "type": "operator", "required": True},
            "condition_value": {"label": "Condition value", "type": "scalar", "required": True},
            "expected_value": {"label": "Expected value", "type": "scalar", "required": True},
        },
    },
    "compare_columns": {
        "label": "Compare columns",
        "column_selection": "ordered_pair",
        "parameters": {"operator": {"label": "Operator", "type": "operator", "required": True}},
    },
}


def _parameter_control(widgets: Any, definition: Mapping[str, Any], value: Any, *, columns: Iterable[str] = ()) -> Any:
    kind = definition.get("type")
    common = shared.widget_common(widgets, str(definition.get("label") or "Parameter"))
    if kind == "number":
        return widgets.Text(value="" if value is None else str(value), **common)
    if kind in {"optional_scalar", "scalar"}:
        return widgets.Text(value="" if value is None else str(value), **common)
    if kind == "boolean":
        return widgets.Checkbox(value=bool(value), **common)
    if kind == "column":
        options = list(columns)
        selected = value if value in options else (options[0] if options else None)
        return widgets.Dropdown(options=options, value=selected, **common)
    if kind == "operator":
        selected = value if value in DQ_COMPARISON_OPERATORS else "="
        return widgets.Dropdown(options=DQ_COMPARISON_OPERATORS, value=selected, **common)
    if kind == "list":
        text = ", ".join(str(item) for item in value) if isinstance(value, (list, tuple)) else str(value or "")
        return widgets.Text(value=text, **common)
    return widgets.Text(value=str(definition.get("default", "") if value is None else value), **common)


def _collect_parameters(definition: Mapping[str, Any], controls: Mapping[str, Any]) -> dict[str, Any]:
    values: dict[str, Any] = {}
    for name, parameter in definition.get("parameters", {}).items():
        value = controls[name].value
        if parameter.get("type") == "list":
            value = [item.strip() for item in str(value).split(",") if item.strip()]
        elif parameter.get("type") == "number":
            try:
                value = None if str(value).strip() == "" else float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"{parameter['label']} must be a number.") from exc
        elif parameter.get("type") in {"optional_scalar", "scalar"}:
            text = str(value).strip()
            if text == "" and parameter.get("type") == "optional_scalar":
                value = None
            else:
                try:
                    value = json.loads(text)
                except json.JSONDecodeError:
                    value = text
        if parameter.get("required") and (value is None or value == "" or value == []):
            raise ValueError(f"{parameter['label']} is required.")
        values[name] = value
    alternatives = definition.get("at_least_one_of", ())
    if alternatives and all(values.get(name) in {None, ""} for name in alternatives):
        labels = " or ".join(str(definition["parameters"][name]["label"]) for name in alternatives)
        raise ValueError(f"Provide at least one of {labels}.")
    return values


def widget_author_dq_rules(
    *,
    spark_session: Any,
    context: dict[str, Any] | None = None,
    rule_type: str = "missing_values",
    selected_columns: Iterable[str] | None = None,
    parameters: Mapping[str, Any] | None = None,
    severity: str = "warning",
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
    rule_type : str, default="missing_values"
        Initially selected canonical DQ rule type.
    selected_columns : Iterable[str], optional
        Columns initially selected on each resolved target.
    parameters : Mapping[str, Any], optional
        Initial structured values for the selected rule's controls.
    severity : str, default="warning"
        Initial failure severity.
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
    Run after ``00_env_config`` in Microsoft Fabric. Independent rules produce one ``METADATA_GUARDRAIL`` row per selected
    column. Grouped, conditional, and ordered-pair rules remain one logical
    row, with all participating columns and structured values serialized in
    ``rule_parameters_json``.

    Examples
    --------
    >>> form = widget_author_dq_rules(spark_session=spark)

    """
    from IPython import display as ip

    config, env, _ = resolve_fabric_context(context=context)
    widgets = shared.require_ipywidgets()
    state: dict[str, Any] = {}
    initial_parameters = dict(parameters or {})
    rule = widgets.Dropdown(
        options=[(definition["label"], name) for name, definition in DQ_RULE_DEFINITIONS.items()],
        value=rule_type if rule_type in DQ_RULE_DEFINITIONS else "missing_values",
        **shared.widget_common(widgets, "DQ rule"),
    )
    parameter_box = widgets.VBox()
    parameter_controls: dict[str, Any] = {}
    column_box = widgets.VBox()
    column_controls: dict[str, Any] = {}
    severity_control = widgets.ToggleButtons(
        options=["warning", "error"],
        value=severity if severity in {"warning", "error"} else "warning",
        description="Severity",
    )
    preview = widgets.Textarea(
        description="Preview", disabled=True, layout=widgets.Layout(width="100%", height="220px")
    )
    message = widgets.HTML()
    records_state: dict[str, list[dict[str, Any]]] = {"records": []}

    def render_parameters(selected_state: Mapping[str, Any], *_: Any) -> None:
        parameter_controls.clear()
        definition = DQ_RULE_DEFINITIONS[rule.value]
        for name, spec in definition["parameters"].items():
            control = _parameter_control(
                widgets,
                spec,
                initial_parameters.get(name, spec.get("default")),
                columns=selected_state.get("columns", []),
            )
            control.observe(refresh_preview, names="value")
            parameter_controls[name] = control
        parameter_box.children = tuple(parameter_controls.values()) or (
            widgets.HTML("<i>This rule has no parameters.</i>"),
        )
        refresh_preview()

    def render_columns(selected_state: Mapping[str, Any]) -> None:
        column_controls.clear()
        definition = DQ_RULE_DEFINITIONS[rule.value]
        selection_mode = definition["column_selection"]
        columns = list(selected_state.get("columns", []))
        if selection_mode == "none":
            column_box.children = (widgets.HTML("<i>This table-level rule does not select columns.</i>"),)
            refresh_preview()
            return
        if selection_mode == "ordered_pair":
            if len(columns) < 2:
                column_box.children = (widgets.HTML("<b>At least two profiled columns are required.</b>"),)
                refresh_preview()
                return
            initial = [column for column in (selected_columns or ()) if column in columns]
            column_a_value = initial[0] if initial else columns[0]
            column_b_value = initial[1] if len(initial) > 1 else next(
                column for column in columns if column != column_a_value
            )
            column_a = widgets.Dropdown(
                options=columns,
                value=column_a_value,
                **shared.widget_common(widgets, "Column A"),
            )
            column_b = widgets.Dropdown(
                options=columns,
                value=column_b_value,
                **shared.widget_common(widgets, "Column B"),
            )
            column_a.observe(refresh_preview, names="value")
            column_b.observe(refresh_preview, names="value")
            column_controls.update(column_a=column_a, column_b=column_b)
            column_box.children = (column_a, column_b)
            refresh_preview()
            return
        if selection_mode == "conditional" and definition.get("maximum_columns") == 1:
            initial = [column for column in (selected_columns or ()) if column in columns]
            target_column = widgets.Dropdown(
                options=columns,
                value=initial[0] if initial else (columns[0] if columns else None),
                **shared.widget_common(widgets, "Target column"),
            )
            target_column.observe(refresh_preview, names="value")
            column_controls["target_column"] = target_column
            column_box.children = (target_column,)
            refresh_preview()
            return
        selected = set(selected_columns) if selected_columns is not None else set()
        rows = [
            widgets.GridBox(
                [widgets.HTML("<b>Apply</b>"), widgets.HTML("<b>Column name</b>"), widgets.HTML("<b>Data type</b>")],
                layout=widgets.Layout(grid_template_columns="70px 1fr 1fr", width="100%"),
            )
        ]
        types = {
            str(row.get("column_name")): str(row.get("data_type") or "")
            for row in selected_state.get("catalogue_profile_rows", [])
        }
        for name in selected_state.get("columns", []):
            control = widgets.Checkbox(value=name in selected, description="", indent=False)
            control.observe(refresh_preview, names="value")
            column_controls[name] = control
            rows.append(
                widgets.GridBox(
                    [
                        control,
                        widgets.HTML(f"<code>{html.escape(name)}</code>"),
                        widgets.HTML(f"<code>{html.escape(types.get(name, ''))}</code>"),
                    ],
                    layout=widgets.Layout(grid_template_columns="70px 1fr 1fr", width="100%"),
                )
            )
        column_box.children = tuple(rows)
        refresh_preview()

    def build_records() -> list[dict[str, Any]]:
        definition = DQ_RULE_DEFINITIONS[rule.value]
        selection_mode = definition["column_selection"]
        if selection_mode == "none":
            columns = []
        elif selection_mode == "ordered_pair":
            if set(column_controls) != {"column_a", "column_b"}:
                raise ValueError("This rule requires two profiled columns.")
            columns = [column_controls["column_a"].value, column_controls["column_b"].value]
            if columns[0] == columns[1]:
                raise ValueError("Column A and Column B must be different columns.")
        elif selection_mode == "conditional" and definition.get("maximum_columns") == 1:
            if "target_column" not in column_controls or not column_controls["target_column"].value:
                raise ValueError("Select a target column.")
            columns = [column_controls["target_column"].value]
        else:
            columns = [name for name, control in column_controls.items() if control.value]
            minimum = int(definition.get("minimum_columns", 1))
            if len(columns) < minimum:
                raise ValueError(f"Select at least {minimum} column(s).")
        return shared._dq_records_from_selection(
            state,
            rule_type=rule.value,
            selected_columns=columns,
            parameters=_collect_parameters(definition, parameter_controls),
            severity=severity_control.value,
            action="submit",
            source_notebook_type=source_notebook_type,
            created_by_role=created_by_role,
            config=config,
            column_selection=selection_mode,
        )

    def refresh_preview(*_: Any) -> None:
        if not state:
            return
        try:
            records_state["records"] = build_records()
            preview.value = json.dumps(records_state["records"], indent=2, default=str)
            message.value = ""
        except ValueError as exc:
            records_state["records"] = []
            preview.value = ""
            message.value = f"<b style='color:#b00020'>Validation error:</b> {html.escape(str(exc))}"

    def save() -> list[dict[str, Any]]:
        records = build_records()
        canonical_records = [canonical_guardrail_rule_record(record, config=config, env=env) for record in records]
        records_state["records"] = canonical_records
        shared._write_rule_records(canonical_records, config=config, env=env, spark_session=spark_session)
        message.value = f"<b style='color:green'>Saved {len(canonical_records)} DQ rule row(s) to METADATA_GUARDRAIL.</b>"
        return canonical_records

    def render_target(selected_state: Mapping[str, Any]) -> None:
        if selected_state is not state:
            state.clear()
            state.update(selected_state)
        render_parameters(selected_state)
        render_columns(selected_state)

    state, target, target_controls = shared._load_guardrail_authoring_targets(
        config, env, spark_session=spark_session, widgets=widgets, on_change=render_target
    )

    def render_rule(*_: Any) -> None:
        render_parameters(state)
        render_columns(state)

    rule.observe(render_rule, names="value")
    severity_control.observe(refresh_preview, names="value")
    save_button = widgets.Button(description="Save DQ rules", button_style="primary")
    save_button.on_click(lambda _: save())
    ui = shared.form_page(
        widgets,
        title="Author DQ Rules",
        description="Select a profiled target and configure canonical DQ rules.",
        children=[
            shared.form_section(widgets, title="Target", children=[target, target_controls["target_summary"]]),
            shared.form_section(widgets, title="Choose DQ rule", children=[rule, parameter_box]),
            shared.form_section(widgets, title="Applicable columns", children=[column_box]),
            shared.form_section(widgets, title="Failure behaviour", children=[severity_control]),
            shared.form_section(widgets, title="Preview", children=[preview]),
            shared.action_row(widgets, [save_button]),
            message,
        ],
    )
    ip.display(ui)
    result = {
        "state": state,
        "records": records_state["records"],
        "controls": {
            "target": target,
            "rule_type": rule,
            "parameters": parameter_box,
            "parameter_controls": parameter_controls,
            "columns": column_controls,
            "severity": severity_control,
            **target_controls,
        },
        "build_records": build_records,
        "build_batch_records": build_records,
        "save": save,
        "save_button": save_button,
        "ui": ui,
    }
    if commit:
        result["records"] = save()
    return result
