"""Standalone Schema, Freshness, and Changes Guardrail authoring widget."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import html
import json
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.guardrails_shared import (
    GUARDRAIL_CHANGE_BEHAVIOURS,
    resolve_guardrail_change_behaviour,
)
from fabricops_kit.widgets import guardrail_authoring_shared as authoring
from fabricops_kit.widgets import shared

CHANGE_BEHAVIOURS = GUARDRAIL_CHANGE_BEHAVIOURS
_DURATION_UNITS = ("Minutes", "Hours", "Days")
_FAILURE_ACTIONS = (("Block pipeline", "blocking"), ("Warn only", "warning"))
_FAILURE_SEVERITIES = {value for _, value in _FAILURE_ACTIONS}


def _guardrail_version(rules: Iterable[Mapping[str, Any]]) -> int:
    """Return the latest explicit Guardrail version."""
    return max((int(row.get("guardrail_version") or 0) for row in rules), default=0)


def _guardrail_records_from_selection(
    state: Mapping[str, Any],
    *,
    required_columns: Iterable[str],
    freshness_column: str,
    maximum_age: int | float,
    maximum_age_unit: str,
    change_behaviour: str,
    schema_severity: str = "blocking",
    freshness_severity: str = "blocking",
    change_severity: str = "blocking",
    partition_column: str = "",
    change_column: str = "",
    guardrail_version: int | None = None,
    config: Any = None,
) -> list[dict[str, Any]]:
    """Translate Schema, Freshness, and Changes controls into Stage 4A rows."""
    del config
    columns = [str(value) for value in state.get("columns", [])]
    available = set(columns)
    required = [str(value) for value in required_columns]
    if not required or any(value not in available for value in required):
        raise ValueError("Select at least one required column from the selected table schema.")
    if freshness_column:
        if freshness_column not in available:
            raise ValueError("Freshness column must come from the selected table schema.")
        try:
            age = float(maximum_age)
        except (TypeError, ValueError) as exc:
            raise ValueError("Maximum age must be a positive number.") from exc
        if age <= 0:
            raise ValueError("Maximum age must be a positive number.")
        if maximum_age_unit not in _DURATION_UNITS:
            raise ValueError("Maximum age unit must be Minutes, Hours, or Days.")
    else:
        age = 0.0
    for label, value in (
        ("Partition column", partition_column),
        ("Change / watermark column", change_column),
    ):
        if value and value not in available:
            raise ValueError(f"{label} must come from the selected table schema.")
    expected_change, source_pattern = resolve_guardrail_change_behaviour(change_behaviour)
    severities = {
        "schema": str(schema_severity),
        "freshness": str(freshness_severity),
        "change": str(change_severity),
    }
    if any(value not in _FAILURE_SEVERITIES for value in severities.values()):
        raise ValueError("Failure action must be Block pipeline or Warn only.")

    version = guardrail_version or (
        _guardrail_version(state.get("existing_rules") or ()) + 1
    )
    data_types = {
        str(row.get("column_name") or ""): str(row.get("data_type") or "")
        for row in state.get("catalogue_profile_rows", [])
    }
    return [
        authoring.build_rule_record(
            state,
            guardrail_type="schema",
            rule_id="schema",
            rule_type="minimum_required",
            parameters={
                "columns": required,
                "data_types": {name: data_types.get(name, "") for name in required},
            },
            severity=severities["schema"],
            guardrail_version=version,
        ),
        authoring.build_rule_record(
            state,
            guardrail_type="freshness",
            rule_id="freshness",
            rule_type="max_age" if freshness_column else "skip",
            parameters={
                "freshness_column": freshness_column,
                "maximum_age": age,
                "maximum_age_unit": maximum_age_unit.lower(),
            },
            severity=severities["freshness"],
            guardrail_version=version,
        ),
        authoring.build_rule_record(
            state,
            guardrail_type="change",
            rule_id="changes",
            rule_type=expected_change,
            parameters={
                "change_behaviour": change_behaviour,
                "expected_change": expected_change,
                "source_pattern": source_pattern,
                "partition_column": partition_column,
                "change_column": change_column,
            },
            severity=severities["change"],
            guardrail_version=version,
        ),
    ]


def widget_author_guardrails(
    *,
    spark_session: Any,
    context: dict[str, Any] | None = None,
    commit: bool = False,
) -> dict[str, Any]:
    """Configure Schema, Freshness, and Change expectations for a profiled table.

    Parameters
    ----------
    spark_session : Any
        Fabric Spark session used to resolve profiled targets and save rules.
    context : dict[str, Any], optional
        Advanced override for the active ``FABRIC_CONTEXT``.
    commit : bool, default=False
        Save the initial selection immediately. The default renders the widget.

    Returns
    -------
    dict[str, Any]
        Target state, authoring controls, canonical preview, and save action.

    Raises
    ------
    ValueError
        If no profiled target exists or configured values are invalid.

    Notes
    -----
    The widget resolves ``table_id`` and ``column_id`` through the normalized
    Catalogue and Profile metadata and writes only the Stage 4A
    ``METADATA_GUARDRAIL`` contract.

    Examples
    --------
    >>> form = widget_author_guardrails(spark_session=spark)

    """
    from IPython import display as ip

    config, env, _ = resolve_fabric_context(context=context)
    widgets = shared.require_ipywidgets()
    authoring_box = widgets.VBox()
    current: dict[str, Any] = {}

    def render(state: Mapping[str, Any]) -> None:
        current.clear()
        current.update(
            _render_guardrail_authoring(
                state, spark_session=spark_session, context=context, commit=False
            )
        )
        authoring_box.children = (current["ui"],)

    state, target, target_controls = authoring.load_guardrail_authoring_targets(
        config,
        env,
        spark_session=spark_session,
        widgets=widgets,
        on_change=render,
    )
    if commit:
        current["records"] = current["save"]()
    ui = shared.form_page(
        widgets,
        title="Author Guardrails",
        description=(
            "Select a profiled table, then author Schema, Freshness, and Changes expectations."
        ),
        children=[
            shared.form_section(
                widgets,
                title="Target",
                children=[target, target_controls["target_summary"]],
            ),
            authoring_box,
        ],
    )
    ip.display(ui)
    return {
        "state": state,
        "controls": {"target": target, **target_controls},
        "authoring": current,
        "ui": ui,
    }


def _render_guardrail_authoring(
    state: Mapping[str, Any],
    *,
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
    commit: bool = False,
) -> dict[str, Any]:
    """Render Guardrail controls for one resolved normalized target state."""
    if not str(state.get("table_id") or "").strip():
        raise ValueError("A selected profiled table with a canonical table_id is required.")
    config, env, _ = resolve_fabric_context(context=context)
    widgets = shared.require_ipywidgets()
    columns = [str(value) for value in state.get("columns", [])]
    existing = list(state.get("existing_rules") or [])
    version_state = {"persisted": _guardrail_version(existing)}
    schema_rule = authoring.latest_rule(existing, "schema")
    freshness_rule = authoring.latest_rule(existing, "freshness")
    change_rule = authoring.latest_rule(existing, "change")
    schema_params = authoring.rule_parameters(schema_rule)
    freshness_params = authoring.rule_parameters(freshness_rule)
    change_params = authoring.rule_parameters(change_rule)
    selected_required = set(schema_params.get("columns") or columns)
    schema_data_types = {
        str(row.get("column_name") or ""): str(row.get("data_type") or "")
        for row in state.get("catalogue_profile_rows", [])
    }
    schema_checkboxes = {
        name: widgets.Checkbox(
            value=name in selected_required, description="", indent=False
        )
        for name in columns
    }
    schema_header = widgets.GridBox(
        [
            widgets.HTML(value="<b>Required</b>"),
            widgets.HTML(value="<b>Column name</b>"),
            widgets.HTML(value="<b>Data type</b>"),
        ],
        layout=widgets.Layout(
            width="100%",
            grid_template_columns="90px minmax(160px, 1fr) minmax(130px, 1fr)",
            grid_gap="4px 12px",
        ),
    )
    schema_rows = {
        name: widgets.GridBox(
            [
                schema_checkboxes[name],
                widgets.HTML(value=f"<code>{html.escape(name)}</code>"),
                widgets.HTML(
                    value=f"<code>{html.escape(schema_data_types.get(name, ''))}</code>"
                ),
            ],
            layout=widgets.Layout(
                width="100%",
                grid_template_columns="90px minmax(160px, 1fr) minmax(130px, 1fr)",
                grid_gap="4px 12px",
                align_items="center",
            ),
        )
        for name in columns
    }
    required_schema = widgets.VBox(
        [
            widgets.HTML(
                value=(
                    "<b>Required schema</b><br>"
                    "<span style='font-size:12px'>Checked columns must exist with the shown data type.</span>"
                )
            ),
            schema_header,
            *schema_rows.values(),
        ],
        layout=widgets.Layout(
            width="100%", height="auto", overflow="visible", gap="4px"
        ),
    )
    schema_failure_action = widgets.Dropdown(
        options=_FAILURE_ACTIONS,
        value=str(schema_rule.get("severity") or "blocking"),
        **shared.widget_common(widgets, "On failure"),
    )
    freshness_value = str(freshness_params.get("freshness_column") or "")
    freshness_column = widgets.Dropdown(
        options=["", *columns],
        value=freshness_value if freshness_value in columns else "",
        **shared.widget_common(widgets, "Freshness date/time column"),
    )
    maximum_age = widgets.FloatText(
        value=float(freshness_params.get("maximum_age") or 1),
        **shared.widget_common(widgets, "Maximum age"),
    )
    unit_value = str(freshness_params.get("maximum_age_unit") or "days").title()
    maximum_age_unit = widgets.Dropdown(
        options=_DURATION_UNITS,
        value=unit_value if unit_value in _DURATION_UNITS else "Days",
        **shared.widget_common(widgets, "Unit"),
    )
    freshness_failure_action = widgets.Dropdown(
        options=_FAILURE_ACTIONS,
        value=str(freshness_rule.get("severity") or "blocking"),
        **shared.widget_common(widgets, "On failure"),
    )
    behaviour = str(change_params.get("change_behaviour") or "Incremental append")
    change_behaviour = widgets.Dropdown(
        options=CHANGE_BEHAVIOURS,
        value=behaviour if behaviour in CHANGE_BEHAVIOURS else "Incremental append",
        **shared.widget_common(widgets, "Change behaviour"),
    )
    partition_value = str(change_params.get("partition_column") or "")
    partition_column = widgets.Dropdown(
        options=["", *columns],
        value=partition_value if partition_value in columns else "",
        **shared.widget_common(widgets, "Partition column"),
    )
    change_value = str(change_params.get("change_column") or "")
    change_column = widgets.Dropdown(
        options=["", *columns],
        value=change_value if change_value in columns else "",
        **shared.widget_common(widgets, "Change / watermark column"),
    )
    change_failure_action = widgets.Dropdown(
        options=_FAILURE_ACTIONS,
        value=str(change_rule.get("severity") or "blocking"),
        **shared.widget_common(widgets, "On failure"),
    )
    preview = widgets.Textarea(
        description="Canonical preview",
        disabled=True,
        layout=widgets.Layout(width="100%", height="260px"),
    )
    message = widgets.HTML()
    save_button = widgets.Button(description="Save Guardrails", button_style="primary")
    version_display = widgets.HTML(
        value=f"<b>Next save version</b><br>{version_state['persisted'] + 1}"
    )

    def build_records() -> list[dict[str, Any]]:
        return _guardrail_records_from_selection(
            state,
            required_columns=[
                name for name, control in schema_checkboxes.items() if control.value
            ],
            freshness_column=freshness_column.value,
            maximum_age=maximum_age.value,
            maximum_age_unit=maximum_age_unit.value,
            change_behaviour=change_behaviour.value,
            schema_severity=schema_failure_action.value,
            freshness_severity=freshness_failure_action.value,
            change_severity=change_failure_action.value,
            partition_column=partition_column.value,
            change_column=change_column.value,
            guardrail_version=version_state["persisted"] + 1,
        )

    def refresh_preview(*_: Any) -> None:
        try:
            preview.value = json.dumps(
                build_records(), indent=2, sort_keys=True, default=str
            )
            message.value = ""
        except ValueError as exc:
            preview.value = ""
            message.value = (
                f"<b style='color:#b00020'>Validation error:</b> {html.escape(str(exc))}"
            )

    def save(*_: Any) -> list[dict[str, Any]]:
        records = build_records()
        if spark_session is None or config is None or env is None:
            message.value = (
                "<b>Preview only:</b> FABRIC_CONTEXT and spark_session are required to save."
            )
            return records
        canonical_records = authoring.canonicalize_records(
            records,
            config=config,
            env=env,
        )
        authoring.write_rule_records(
            canonical_records,
            config=config,
            env=env,
            spark_session=spark_session,
        )
        state_existing = state.get("existing_rules")
        if isinstance(state_existing, list):
            state_existing.extend(canonical_records)
        version_state["persisted"] = records[0]["guardrail_version"]
        version_display.value = (
            f"<b>Next save version</b><br>{version_state['persisted'] + 1}"
        )
        message.value = (
            f"<b style='color:green'>Saved Guardrail version "
            f"{records[0]['guardrail_version']}.</b>"
        )
        refresh_preview()
        return canonical_records

    for control in (
        *schema_checkboxes.values(),
        schema_failure_action,
        freshness_column,
        maximum_age,
        maximum_age_unit,
        freshness_failure_action,
        change_behaviour,
        partition_column,
        change_column,
        change_failure_action,
    ):
        control.observe(refresh_preview, names="value")
    save_button.on_click(save)

    identity = shared.form_grid(
        widgets,
        [
            widgets.HTML(
                value=f"<b>Environment</b><br>{html.escape(str(state.get('environment_name', '')))}"
            ),
            widgets.HTML(
                value=f"<b>Store</b><br>{html.escape(str(state.get('store_type', '')))}"
            ),
            widgets.HTML(
                value=f"<b>Schema</b><br>{html.escape(str(state.get('schema_name', '')))}"
            ),
            widgets.HTML(
                value=f"<b>Table</b><br>{html.escape(str(state.get('table_name', '')))}"
            ),
            version_display,
        ],
    )
    ui = shared.form_page(
        widgets,
        title="Author Guardrails",
        description=(
            "Version Schema, Freshness, and Changes expectations for this profiled table."
        ),
        children=[
            identity,
            shared.form_section(
                widgets,
                title="1. Schema",
                children=[required_schema, schema_failure_action],
            ),
            shared.form_section(
                widgets,
                title="2. Freshness",
                children=[
                    shared.form_grid(
                        widgets,
                        [
                            freshness_column,
                            maximum_age,
                            maximum_age_unit,
                            freshness_failure_action,
                        ],
                    )
                ],
            ),
            shared.form_section(
                widgets,
                title="3. Changes",
                children=[
                    shared.form_grid(
                        widgets,
                        [
                            change_behaviour,
                            partition_column,
                            change_column,
                            change_failure_action,
                        ],
                    )
                ],
            ),
            shared.form_section(widgets, title="Preview", children=[preview]),
            shared.action_row(widgets, [save_button]),
            message,
        ],
    )
    result = {
        "version": version_state["persisted"] + 1,
        "next_version": version_state["persisted"] + 1,
        "version_state": version_state,
        "controls": {
            "schema_columns": schema_checkboxes,
            "schema_data_types": schema_data_types,
            "schema_rows": schema_rows,
            "schema_failure_action": schema_failure_action,
            "freshness_column": freshness_column,
            "maximum_age": maximum_age,
            "maximum_age_unit": maximum_age_unit,
            "freshness_failure_action": freshness_failure_action,
            "change_behaviour": change_behaviour,
            "partition_column": partition_column,
            "change_column": change_column,
            "change_failure_action": change_failure_action,
            "preview": preview,
        },
        "build_records": build_records,
        "refresh_preview": refresh_preview,
        "save": save,
        "save_button": save_button,
        "ui": ui,
    }
    refresh_preview()
    if commit:
        result["records"] = save()
    return result
