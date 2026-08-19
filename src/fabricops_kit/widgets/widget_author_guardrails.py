"""Lightweight table guardrail authoring widget."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import html
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.pipeline.guardrail_metadata import canonical_guardrail_rule_record
from fabricops_kit.pipeline.guardrails_shared import (
    GUARDRAIL_CHANGE_BEHAVIOURS,
    resolve_guardrail_change_behaviour,
)
from fabricops_kit.widgets import shared

CHANGE_BEHAVIOURS = GUARDRAIL_CHANGE_BEHAVIOURS
_DURATION_UNITS = ("Minutes", "Hours", "Days")
_FAILURE_ACTIONS = (("Block pipeline", "blocking"), ("Warn only", "warning"))
_FAILURE_SEVERITIES = {value for _, value in _FAILURE_ACTIONS}


def _configuration_version(rules: Iterable[Mapping[str, Any]]) -> int:
    """Return the latest explicit guardrail configuration version."""
    return max((int(row.get("configuration_version") or 0) for row in rules), default=0)


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
    configuration_version: int | None = None,
    config: Any = None,
) -> list[dict[str, Any]]:
    """Translate the form vocabulary into canonical guardrail rows."""
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
    for label, value in (("Partition column", partition_column), ("Change / watermark column", change_column)):
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
    existing = list(state.get("existing_rules") or [])
    version = configuration_version or (_configuration_version(existing) + 1)
    data_types = {
        str(row.get("column_name") or ""): str(row.get("data_type") or "")
        for row in state.get("catalogue_profile_rows", [])
    }
    specifications = [
        (
            "schema",
            "minimum_required",
            "",
            {"columns": required, "data_types": {name: data_types.get(name, "") for name in required}},
        ),
        (
            "freshness",
            "max_age" if freshness_column else "skip",
            freshness_column,
            {"freshness_column": freshness_column, "maximum_age": age, "maximum_age_unit": maximum_age_unit.lower()},
        ),
        (
            "change",
            expected_change,
            "",
            {
                "change_behaviour": change_behaviour,
                "expected_change": expected_change,
                "source_pattern": source_pattern,
                "partition_column": partition_column,
                "change_column": change_column,
            },
        ),
    ]
    records = []
    for guardrail_type, rule_type, column_name, parameters in specifications:
        record = shared._base_guardrail_rule_record(
            state,
            guardrail_type=guardrail_type,
            rule_type=rule_type,
            column_name=column_name,
            parameters=parameters,
            severity=severities[guardrail_type],
            description=f"Table {guardrail_type} guardrail",
            action="apply_now",
            source_notebook_type="01_governance",
            created_by_role="governance",
            config=config,
        )
        record.update(
            configuration_version=version,
            guardrail_rule_id=f"{record['guardrail_rule_id']}.v{version}",
            rule_id=f"{record['rule_id']}.v{version}",
            activation_state="active",
            is_active=True,
            review_status="authored",
            review_state="authored",
            approval_required=False,
            approval_bypassed=False,
            requires_governance_review=False,
            requires_post_review=False,
            bypass_reason="",
            action_type="created",
        )
        records.append(record)
    return records


def widget_author_guardrails(
    *,
    spark_session: Any,
    context: dict[str, Any] | None = None,
    commit: bool = False,
) -> dict[str, Any]:
    """Render standalone Schema, Freshness, and Changes guardrail authoring.

    Parameters
    ----------
    spark_session : Any
        Fabric Spark session used to read profiled targets and save rules.
    context : dict[str, Any], optional
        Advanced override for the active ``FABRIC_CONTEXT``.
    commit : bool, default=False
        Save the initial selection immediately. The default renders the widget.

    Returns
    -------
    dict[str, Any]
        Target and authoring controls plus testable build and save actions.

    Raises
    ------
    ValueError
        If no profiled target exists or configured values are invalid.

    Notes
    -----
    Run after ``00_env_config`` in Microsoft Fabric. The widget reads
    ``METADATA_DATA_PROFILED`` and existing ``METADATA_GUARDRAIL`` rows, then
    writes new versions through the canonical guardrail metadata writer.

    Examples
    --------
    >>> form = widget_author_guardrails(spark_session=spark)

    """
    from IPython import display as ip

    config, env, _ = resolve_fabric_context(context=context)
    widgets = shared.require_ipywidgets()
    authoring = widgets.VBox()
    current: dict[str, Any] = {}

    def render(state: Mapping[str, Any]) -> None:
        current.clear()
        current.update(_render_guardrail_authoring(state, spark_session=spark_session, context=context, commit=False))
        authoring.children = (current["ui"],)

    state, target, target_controls = shared._load_guardrail_authoring_targets(
        config, env, spark_session=spark_session, widgets=widgets, on_change=render
    )
    if commit:
        current["records"] = current["save"]()
    ui = shared.form_page(
        widgets,
        title="Author Guardrails",
        description="Select a profiled target, then author table-level guardrails.",
        children=[
            shared.form_section(widgets, title="Target", children=[target, target_controls["target_summary"]]),
            authoring,
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
    """Render guardrail controls for one resolved target state."""
    if not str(state.get("table_name") or "").strip() or not str(state.get("metadata_table_key") or "").strip():
        raise ValueError("A selected table with a canonical metadata_table_key is required.")
    config, env, _ = resolve_fabric_context(context=context)
    widgets = shared.require_ipywidgets()
    columns = [str(value) for value in state.get("columns", [])]
    existing = list(state.get("existing_rules") or [])
    version_state = {"persisted": _configuration_version(existing)}
    schema_rule = shared._latest_rule(existing, "schema")
    freshness_rule = shared._latest_rule(existing, "freshness")
    change_rule = shared._latest_rule(existing, "change")
    schema_params = shared._rule_params(schema_rule)
    freshness_params = shared._rule_params(freshness_rule)
    change_params = shared._rule_params(change_rule)
    selected_required = set(schema_params.get("columns") or columns)
    schema_data_types = {
        str(row.get("column_name") or ""): str(row.get("data_type") or "")
        for row in state.get("catalogue_profile_rows", [])
    }
    schema_checkboxes = {
        name: widgets.Checkbox(value=name in selected_required, description="", indent=False) for name in columns
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
                widgets.HTML(value=f"<code>{html.escape(schema_data_types.get(name, ''))}</code>"),
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
        layout=widgets.Layout(width="100%", height="auto", overflow="visible", gap="4px"),
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
        value=float(freshness_params.get("maximum_age") or 1), **shared.widget_common(widgets, "Maximum age")
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
    partition_column = widgets.Dropdown(
        options=["", *columns],
        value=str(change_params.get("partition_column") or ""),
        **shared.widget_common(widgets, "Partition column"),
    )
    change_column = widgets.Dropdown(
        options=["", *columns],
        value=str(change_params.get("change_column") or ""),
        **shared.widget_common(widgets, "Change / watermark column"),
    )
    change_failure_action = widgets.Dropdown(
        options=_FAILURE_ACTIONS,
        value=str(change_rule.get("severity") or "blocking"),
        **shared.widget_common(widgets, "On failure"),
    )
    message = widgets.HTML()
    save_button = widgets.Button(description="Save Guardrails", button_style="primary")
    version_display = widgets.HTML(value=f"<b>Next save version</b><br>{version_state['persisted'] + 1}")

    def build_records() -> list[dict[str, Any]]:
        return _guardrail_records_from_selection(
            state,
            required_columns=[name for name, control in schema_checkboxes.items() if control.value],
            freshness_column=freshness_column.value,
            maximum_age=maximum_age.value,
            maximum_age_unit=maximum_age_unit.value,
            change_behaviour=change_behaviour.value,
            schema_severity=schema_failure_action.value,
            freshness_severity=freshness_failure_action.value,
            change_severity=change_failure_action.value,
            partition_column=partition_column.value,
            change_column=change_column.value,
            configuration_version=version_state["persisted"] + 1,
            config=config,
        )

    def save(*_: Any) -> list[dict[str, Any]]:
        records = build_records()
        if spark_session is None or config is None or env is None:
            message.value = "<b>Preview only:</b> FABRIC_CONTEXT and spark_session are required to save."
            return records
        canonical_records = [canonical_guardrail_rule_record(record, config=config, env=env) for record in records]
        shared._write_rule_records(canonical_records, config=config, env=env, spark_session=spark_session)
        version_state["persisted"] = records[0]["configuration_version"]
        version_display.value = f"<b>Next save version</b><br>{version_state['persisted'] + 1}"
        message.value = f"<b style='color:green'>Saved guardrail version {records[0]['configuration_version']}.</b>"
        return canonical_records

    save_button.on_click(save)
    version = version_state["persisted"] + 1
    identity = shared.form_grid(
        widgets,
        [
            widgets.HTML(value=f"<b>Environment</b><br>{state.get('environment_name', '')}"),
            widgets.HTML(value=f"<b>Target</b><br>{state.get('fabric_store_target') or state.get('layer', '')}"),
            widgets.HTML(value=f"<b>Schema</b><br>{state.get('schema_name', '')}"),
            widgets.HTML(value=f"<b>Table</b><br>{state.get('table_name', '')}"),
            version_display,
        ],
    )
    ui = shared.form_page(
        widgets,
        title="Author Guardrails",
        description="Version table-level Schema, Freshness, and Changes guardrails.",
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
                    shared.form_grid(widgets, [freshness_column, maximum_age, maximum_age_unit, freshness_failure_action])
                ],
            ),
            shared.form_section(
                widgets,
                title="3. Changes",
                children=[
                    shared.form_grid(widgets, [change_behaviour, partition_column, change_column, change_failure_action])
                ],
            ),
            shared.action_row(widgets, [save_button]),
            message,
        ],
    )
    result = {
        "version": version,
        "next_version": version,
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
        },
        "build_records": build_records,
        "save": save,
        "save_button": save_button,
        "ui": ui,
    }
    if commit:
        result["records"] = save()
    return result
