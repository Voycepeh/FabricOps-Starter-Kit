"""Public widget entrypoint for ``widget_enrich_table_metadata``."""

from __future__ import annotations

import importlib

from fabricops_kit.widgets import shared as _governance_review
from fabricops_kit.config.shared import resolve_fabric_context

from typing import Any, Mapping



def widget_enrich_table_metadata(
    guardrail_state: Mapping[str, Any],
    *,
    spark_session: Any,
    context: dict[str, Any] | None = None,
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
) -> dict[str, Any]:
    """Render governed table metadata enrichment controls.

    Parameters
    ----------
    guardrail_state : Mapping[str, Any]
        Guardrail target state containing table identity and catalogue profile
        rows for enrichment.
    spark_session : Any
        Fabric Spark session used when committing enrichment metadata rows.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context.
    source_notebook_type : str, default="02_pipeline"
        Notebook role recorded on authored metadata rows.
    created_by_role : str, default="engineering"
        Actor role recorded on authored metadata rows.

    Returns
    -------
    dict[str, Any]
        Rendered controls and save actions for notebook automation.

    """
    return _table_metadata_enrichment_widget_workflow(
        guardrail_state,
        spark_session=spark_session,
        context=context,
        source_notebook_type=source_notebook_type,
        created_by_role=created_by_role,
    )


def _table_metadata_enrichment_widget_workflow(
    guardrail_state: Mapping[str, Any],
    *,
    spark_session: Any,
    context: dict[str, Any] | None = None,
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
) -> dict[str, Any]:
    """Render one consolidated governed table metadata enrichment widget.

    Parameters
    ----------
    guardrail_state : Mapping[str, Any]
        Target handover state returned by :func:`widget_select_guardrail_target`.
    spark_session : Any
        Spark session used to create write DataFrames.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.
    source_notebook_type : {"02_pipeline", "03_governance"}, default="02_pipeline"
        Notebook type stamped on authored records.
    created_by_role : {"engineering", "governance", "system"}, default="engineering"
        Role stamped on authored records.

    Returns
    -------
    dict[str, Any]
        Widget state with rendered row controls, record builders, and save
        callbacks. Saves write reviewable enrichment intent to
        ``METADATA_ENRICHMENT``. The widget does not write to removed
        split enrichment metadata tables and uses the same approval lifecycle as
        guardrail rules.

    """
    config, env, _context = resolve_fabric_context(context=context)
    widgets = importlib.import_module("ipywidgets")
    from IPython import display as ip

    profile_rows = _governance_review._selected_catalogue_rows_for_enrichment(guardrail_state)
    if not profile_rows:
        raise ValueError("Selected guardrail target has no column rows in METADATA_DATA_CATALOGUE.")
    sensitivity_options, pii_options, context_defs, classification_defs = _governance_review._enrichment_options(config)
    row_controls: list[dict[str, Any]] = []
    row_widgets = []
    status = widgets.HTML(value="")
    apply_reason_box = widgets.Textarea(value="", description="Apply now reason", layout=widgets.Layout(width="760px", height="70px"))
    governed = str(guardrail_state.get("governance_mode") or "ungoverned") == "governed"
    bypass_allowed = bool(guardrail_state.get("approval_bypass_allowed"))
    if not governed:
        policy_text = "This table is ungoverned. Submit and apply actions save active non-pending enrichment."
    elif bypass_allowed:
        policy_text = "This table is governed. Save a draft, submit for governance review, or apply now when continuity requires immediate activation."
    else:
        policy_text = "This table is governed. Save a draft, submit for governance review, or apply now when continuity requires immediate activation."

    for row in profile_rows:
        column_name = str(_governance_review._value(row, "column_name"))
        data_type = str(_governance_review._value(row, "data_type"))
        context_extra = _governance_review._render_enrichment_extra_fields(widgets, context_defs)
        classification_extra = _governance_review._render_enrichment_extra_fields(widgets, classification_defs)
        controls = {
            "column_name": column_name,
            "data_type": data_type,
            "business_context": widgets.Textarea(value="", description="Business context", rows=2, layout=widgets.Layout(width="520px")),
            "business_meaning": widgets.Textarea(value="", description="Meaning", rows=2, layout=widgets.Layout(width="520px")),
            "column_description": widgets.Textarea(value="", description="Column description", rows=2, layout=widgets.Layout(width="520px")),
            "sensitivity_label": widgets.Dropdown(options=sensitivity_options, value=sensitivity_options[0], description="Sensitivity", layout=widgets.Layout(width="320px")),
            "pii_classification": widgets.Dropdown(options=pii_options, value=pii_options[-1], description="PII", layout=widgets.Layout(width="320px")),
            "commit": widgets.Checkbox(value=True, description="Commit/save"),
            "context_extra_fields": context_extra,
            "classification_extra_fields": classification_extra,
        }
        row_controls.append(controls)
        row_widgets.append(widgets.VBox([
            widgets.HTML(f"<b>{column_name}</b> <code>{data_type}</code>"),
            controls["business_context"], controls["business_meaning"], controls["column_description"],
            widgets.HBox([controls["sensitivity_label"], controls["pii_classification"], controls["commit"]]),
            *context_extra.values(), *classification_extra.values(),
        ]))

    def _review_rows() -> list[dict[str, Any]]:
        return [{
            "column_name": controls["column_name"],
            "business_description": controls["business_context"].value,
            "business_meaning": controls["business_meaning"].value,
            "column_description": controls["column_description"].value,
            "sensitivity_label": controls["sensitivity_label"].value,
            "pii_classification": controls["pii_classification"].value,
            "custom_fields": {**_governance_review._collect_enrichment_extra_fields(controls["context_extra_fields"]), **_governance_review._collect_enrichment_extra_fields(controls["classification_extra_fields"])},
            "commit": bool(controls["commit"].value),
        } for controls in row_controls]

    def build_records(*, action: str = "submit", use_bypass: bool = False) -> list[dict[str, Any]]:
        selected_action = "apply_now" if use_bypass else action
        reason = apply_reason_box.value.strip() if selected_action == "apply_now" else ""
        return _governance_review.build_enrichment_rule_records(
            profile_rows,
            _review_rows(),
            state=guardrail_state,
            config=config,
            env=env,
            bypass_reason=reason,
            action=selected_action,
            source_notebook_type=source_notebook_type,
            created_by_role=created_by_role,
        )

    def save(*, action: str = "submit", use_bypass: bool = False) -> dict[str, list[dict[str, Any]]]:
        selected_action = "apply_now" if use_bypass else action
        records = build_records(action=selected_action)
        _governance_review._write_table_metadata_enrichment_records(records, config=config, env=env, spark_session=spark_session)
        status.value = f"Saved {len(records)} enrichment rule row(s) to METADATA_ENRICHMENT."
        return {"enrichment_rules": records}

    draft_button = widgets.Button(description="Save draft", button_style="")
    submit_button = widgets.Button(description="Submit for governance review", button_style="success")
    apply_now_button = widgets.Button(description="Apply now", button_style="warning")
    draft_button.on_click(lambda _: save(action="draft"))
    submit_button.on_click(lambda _: save(action="submit"))
    apply_now_button.on_click(lambda _: save(action="apply_now"))
    ip.display(widgets.VBox([
        widgets.HTML("<h3>Enrich table metadata</h3>"), widgets.HTML(f"<p>{policy_text}</p>"),
        widgets.HTML("<p><b>Actions:</b> Save draft · Submit for governance review · Apply now.</p>"),
        *row_widgets, apply_reason_box, widgets.HBox([draft_button, submit_button, apply_now_button]), status,
    ]))
    return {
        "rows": row_controls,
        "build_records": build_records,
        "save": save,
        "save_draft_button": draft_button,
        "submit_button": submit_button,
        "apply_now_button": apply_now_button,
        "status": status,
        "controls": {"apply_now_reason": apply_reason_box},
    }
