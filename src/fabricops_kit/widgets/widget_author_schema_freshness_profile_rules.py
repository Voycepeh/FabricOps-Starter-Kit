"""Public widget entrypoint for ``widget_author_schema_freshness_profile_rules``."""

from __future__ import annotations

import importlib
import json

from fabricops_kit.widgets import shared as _governance_review
from fabricops_kit.config.shared import resolve_fabric_context

from typing import Any, Mapping



def widget_author_schema_freshness_profile_rules(
    state: Mapping[str, Any],
    *,
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
    bypass_reason: str = "",
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
    commit: bool = False,
) -> dict[str, Any]:
    """Render schema, freshness, and profile behavior authoring controls.

    Parameters
    ----------
    state : Mapping[str, Any]
        Guardrail target state returned by the target selector or prepared by a
        notebook workflow.
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
    return _schema_freshness_profile_rule_authoring_widget_workflow(
        state,
        spark_session=spark_session,
        context=context,
        bypass_reason=bypass_reason,
        source_notebook_type=source_notebook_type,
        created_by_role=created_by_role,
        commit=commit,
    )


def _schema_freshness_profile_rule_authoring_widget_workflow(
    state: Mapping[str, Any],
    *,
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
    bypass_reason: str = "",
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
    commit: bool = False,
) -> dict[str, Any]:
    """Render interactive schema, freshness, and profile behavior authoring UI.

    Parameters
    ----------
    state : mapping
        Handover state from :func:`widget_select_guardrail_target`.
    spark_session : Any, optional
        Spark session used for save actions.
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
        ``build_records``/``save`` helpers for tests and notebook automation.

    """
    config, env, _context = resolve_fabric_context(context=context)
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    columns = list(state.get("columns") or [])
    existing_rules = list(state.get("existing_rules") or [])
    schema_rule = _governance_review._latest_rule(existing_rules, "schema")
    schema_params = _governance_review._rule_params(schema_rule)
    selected_schema_columns = tuple(column for column in (schema_params.get("columns") or columns) if column in columns)
    freshness_rule = _governance_review._latest_rule(existing_rules, "freshness")
    freshness_params = _governance_review._rule_params(freshness_rule)
    profile_rule = _governance_review._latest_rule(existing_rules, "profile_behavior")
    profile_params = _governance_review._rule_params(profile_rule)

    schema_columns = widgets.SelectMultiple(options=columns, value=selected_schema_columns or tuple(columns), description="Columns", rows=min(max(len(columns), 4), 12), layout=widgets.Layout(width="420px"))
    schema_mode = widgets.Dropdown(options=["strict", "relaxed", "skip"], value=str(schema_rule.get("rule_type") or "relaxed"), description="Schema mode")
    freshness_mode = widgets.Dropdown(options=["enforce", "skip"], value="skip" if str(freshness_rule.get("rule_type") or "skip") == "skip" else "enforce", description="Freshness")
    freshness_column = widgets.Dropdown(options=[""] + columns, value=str(freshness_params.get("freshness_column") or freshness_rule.get("column_name") or ""), description="Column")
    max_lag = widgets.BoundedIntText(value=int(freshness_params.get("max_lag_days") or 0), min=0, description="Max lag days")
    profile_mode = widgets.Dropdown(options=["static_data", "changing_data", "skip"], value=str(profile_rule.get("rule_type") or "static_data"), description="Profile mode")
    watermark_column = widgets.Dropdown(options=[""] + columns, value=str(profile_params.get("watermark_column") or profile_rule.get("column_name") or ""), description="Watermark")
    bypass_box = widgets.Textarea(value=bypass_reason, description="Bypass reason", layout=widgets.Layout(width="760px", height="70px"))
    preview = widgets.Textarea(description="Preview", disabled=True, layout=widgets.Layout(width="900px", height="220px"))
    message = widgets.HTML()
    records_state: dict[str, Any] = {"records": []}

    draft_button = widgets.Button(description="Save draft", button_style="")
    submit_button = widgets.Button(description="Submit for governance review", button_style="success")
    apply_now_button = widgets.Button(description="Apply now", button_style="warning")
    cancel_button = widgets.Button(description="Cancel")

    def build_records(*, action: str = "submit", use_bypass: bool = False) -> list[dict[str, Any]]:
        selected_action = "apply_now" if use_bypass else action
        reason = bypass_box.value.strip() if selected_action == "apply_now" else ""
        return _governance_review._schema_freshness_profile_records_from_selection(
            state,
            selected_columns=list(schema_columns.value),
            schema_mode=schema_mode.value,
            freshness_mode=freshness_mode.value,
            freshness_column=freshness_column.value,
            max_lag_days=max_lag.value,
            profile_mode=profile_mode.value,
            watermark_column=watermark_column.value,
            bypass_reason=reason,
            action=selected_action,
            source_notebook_type=source_notebook_type,
            created_by_role=created_by_role,
            config=config,
        )

    def refresh_preview(*_: Any) -> None:
        try:
            records_state["records"] = build_records(action="submit")
            preview.value = json.dumps(records_state["records"], indent=2, default=str)
            message.value = ""
        except Exception as exc:
            preview.value = ""
            message.value = f"<b style='color:#b00020'>Validation error:</b> {exc}"

    def save(*, action: str = "submit", use_bypass: bool = False) -> list[dict[str, Any]]:
        records = build_records(action="apply_now" if use_bypass else action)
        records_state["records"] = records
        if spark_session is None or config is None or env is None:
            message.value = "<b>Preview only:</b> FABRIC_CONTEXT/context and spark_session are required to save."
            return records
        _governance_review._write_rule_records(records, config=config, env=env, spark_session=spark_session)
        message.value = f"<b style='color:green'>Saved {len(records)} guardrail rule row(s) to METADATA_GUARDRAIL.</b>"
        return records

    def cancel(_: Any = None) -> None:
        records_state["records"] = []
        preview.value = ""
        message.value = "<b>Cancelled.</b>"

    for control in (schema_columns, schema_mode, freshness_mode, freshness_column, max_lag, profile_mode, watermark_column, bypass_box):
        control.observe(lambda change: refresh_preview(), names="value")
    draft_button.on_click(lambda _: save(action="draft"))
    submit_button.on_click(lambda _: save(action="submit"))
    apply_now_button.on_click(lambda _: save(action="apply_now"))
    cancel_button.on_click(cancel)
    refresh_preview()
    if commit:
        save(action="apply_now" if bypass_reason else "submit")

    ui = widgets.VBox([
        widgets.HTML("<h3>Author schema, freshness, and profile behavior rules</h3>"),
        widgets.HTML(f"<b>Table:</b> {state.get('dataset_name', '')}.{state.get('table_name', '')} · <b>Governance:</b> {state.get('governance_mode', 'ungoverned')}"),
        widgets.HTML("<h4>Schema guardrail</h4>"),
        widgets.HBox([schema_mode, schema_columns]),
        widgets.HTML("<h4>Freshness guardrail</h4>"),
        widgets.HBox([freshness_mode, freshness_column, max_lag]),
        widgets.HTML("<h4>Profile behavior guardrail</h4>"),
        widgets.HBox([profile_mode, watermark_column]),
        bypass_box,
        preview,
        widgets.HBox([draft_button, submit_button, apply_now_button, cancel_button]),
        message,
    ])
    ip.display(ui)
    return {
        "records": records_state["records"],
        "controls": {"schema_columns": schema_columns, "schema_mode": schema_mode, "freshness_mode": freshness_mode, "freshness_column": freshness_column, "max_lag": max_lag, "profile_mode": profile_mode, "watermark_column": watermark_column, "apply_now_reason": bypass_box, "bypass_reason": bypass_box},
        "build_records": build_records,
        "save": save,
        "save_draft_button": draft_button,
        "submit_button": submit_button,
        "apply_now_button": apply_now_button,
        "ui": ui,
    }
