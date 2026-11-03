"""Review and promote manually tested notebooks into separate Governed items."""
from __future__ import annotations

import html
import json
from typing import Any

from fabricops_kit.activated_pipeline.shared import (
    FABRIC_VALIDATION_PENDING, prepare_pipeline_promotion, read_registry, stage_pipeline_promotion,
)
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.widgets import shared


def widget_activate_pipeline(*, pipeline_id=None, dry_run=None, context=None) -> dict[str, Any]:
    """Review destination bindings and explicitly promote a completed manual Dry Run.

    Parameters
    ----------
    pipeline_id : str | None, optional
        Stable Pipeline ID used to filter retained immutable version records.
    dry_run : PipelineSession | None, optional
        Completed and finalized manual Dry Run session. Without it the widget
        displays retained promotions without enabling the promotion action.
    context : dict | None, optional
        Configured notebook context; central Metadata routing is preserved.

    Returns
    -------
    dict
        Widget, scoped version records, controls, review action and promotion
        action. Review creates no artifacts; promotion archives and clones before
        conditionally switching the active version.

    Raises
    ------
    ValueError
        If pipeline identity or Registry records are ambiguous or invalid.
    RuntimeError
        If metadata, widgets or Fabric APIs are unavailable. Action errors remain
        visible without erasing the review or previous active version.

    Notes
    -----
    Only notebook code is frozen; dependencies are not. Saved-definition checks
    have TOCTOU limits. Governed remains blocked pending signed-in Fabric validation.
    Engineers manage schedules; this widget never migrates schedules. A Governed
    folder organizes same-workspace copies and confers no permissions.

    Examples
    --------
    >>> ui = widget_activate_pipeline(dry_run=preview)
    >>> review = ui["actions"]["review"]()

    """
    startup = shared.WidgetStartup("Pipeline Promotion", tone="governance", reserved_height="360px")
    config, workspace, runtime = resolve_fabric_context(context=context)
    if pipeline_id is None and dry_run is not None:
        pipeline_id = dry_run.plan.pipeline_id
    if pipeline_id is not None:
        from fabricops_kit.pipeline.shared import validate_pipeline_id
        pipeline_id = validate_pipeline_id(pipeline_id)
    routed = {**runtime, "config": config, "scope_workspace_id": workspace}
    spark = get_spark_session(context=runtime)
    with startup.phase("metadata_loading", "Loading retained Pipeline Promotion versions…"):
        rows = read_registry(context=routed, spark_session=spark)
    scoped = [row for row in rows if pipeline_id is None or row["pipeline_id"] == pipeline_id]
    widgets = shared.require_ipywidgets()
    destination = widgets.Text(value=workspace, layout=widgets.Layout(width="100%"))
    agreement = widgets.Text(layout=widgets.Layout(width="100%"))
    agreement_version = widgets.Text(layout=widgets.Layout(width="100%"))
    confirm = widgets.Checkbox(value=False, description="I reviewed this notebook, destination bindings and Contracts", indent=False)
    review_button = widgets.Button(description="Review promotion", disabled=dry_run is None)
    promote_button = widgets.Button(description="Promote notebook", disabled=True, button_style="primary")
    report = widgets.HTML()
    state = {"review": None, "result": None}
    def invalidate(_event):
        state["review"] = None
        confirm.value = False
        promote_button.disabled = True
    for control in (destination, agreement, agreement_version):
        control.observe(invalidate, names="value")
    def review():
        target = destination.value.strip()
        fresh = read_registry(context=routed, spark_session=spark)
        active = [row for row in fresh if row["execution_workspace_id"] == target and row["pipeline_id"] == pipeline_id and row["status"] == "active"]
        candidate = prepare_pipeline_promotion(dry_run, destination_workspace_id=target,
            expected_active_version=active[0]["pipeline_version"] if active else None,
            agreement_id=agreement.value.strip() or None, agreement_version=agreement_version.value.strip() or None,
            context=routed, spark_session=spark)
        state["review"] = candidate
        confirm.value = False
        report.value = "<h3>Review frozen implementation and physical bindings</h3><pre style='white-space:pre-wrap'>" + html.escape(
            json.dumps({"promotion": candidate["candidate"], "contracts": candidate["contracts"]}, indent=2, default=str)) + "</pre>" + (
            "<details><summary>Complete promoted notebook</summary><pre style='white-space:pre-wrap'>" + html.escape(candidate["snapshot"].decode()) + "</pre></details>")
        return candidate
    def promote():
        if state["review"] is None or not confirm.value:
            raise ValueError("Review and confirm the exact promotion first.")
        result = stage_pipeline_promotion(state["review"], governance_confirmed=True, spark_session=spark)
        state["result"] = result
        report.value += "<p>Promotion saved. Governed execution remains blocked pending signed-in Fabric validation. Update engineer-owned schedule targets explicitly.</p>"
        promote_button.disabled = True
        return result
    def run(action, button):
        button.disabled = True
        try:
            action()
        except Exception as exc:
            report.value += "<p role='alert'>" + html.escape(str(exc)) + "</p>"
        finally:
            review_button.disabled = dry_run is None
            promote_button.disabled = state["result"] is not None or state["review"] is None or not confirm.value
    review_button.on_click(lambda _button: run(review, review_button))
    promote_button.on_click(lambda _button: run(promote, promote_button))
    confirm.observe(lambda _event: setattr(promote_button, "disabled", state["result"] is not None or state["review"] is None or not confirm.value), names="value")
    records = widgets.HTML("<details><summary>Retained versions</summary><pre style='white-space:pre-wrap'>" + html.escape(json.dumps(scoped, indent=2, default=str)) + "</pre></details>")
    root = shared.form_page(widgets, title="Pipeline Promotion", tone="governance",
        description="Freeze a manually tested notebook and create a separate Governed copy.", children=[
            widgets.HTML("<p>" + html.escape(FABRIC_VALIDATION_PENDING) + "</p>"),
            widgets.HTML("<p>Only the notebook is frozen; imported dependencies are not. Saved-definition checks have TOCTOU limits. Folders confer no permissions.</p>"),
            widgets.HTML("<label>Destination execution workspace</label>"), destination,
            widgets.HTML("<label>Data Agreement ID (where required)</label>"), agreement,
            widgets.HTML("<label>Exact Agreement version</label>"), agreement_version,
            review_button, report, confirm, promote_button, records])
    startup.display(root)
    return {"widget": root, "records": scoped, "state": state, "ready": False, "reason": FABRIC_VALIDATION_PENDING,
        "controls": {"destination": destination, "agreement": agreement, "agreement_version": agreement_version,
            "confirm": confirm, "review": review_button, "promote": promote_button}, "actions": {"review": review, "promote": promote}}
