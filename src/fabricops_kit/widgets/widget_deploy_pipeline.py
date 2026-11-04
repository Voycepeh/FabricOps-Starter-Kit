"""Engineering export and deployment of independently approved notebook packages."""
from __future__ import annotations

import base64
import html
import json

from fabricops_kit.activated_pipeline.shared import (
    authoritative_approval, deploy_approved_submission, export_pipeline_submission,
    export_retained_submission, read_approvals, read_registry,
)
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.widgets import shared


def widget_deploy_pipeline(*, pipeline_id=None, dry_run=None, context=None) -> dict:
    """Export completed Engineering evidence or explicitly deploy an approved package.

    Parameters
    ----------
    pipeline_id : str | None, optional
        Filter approvals and retained versions by logical Pipeline ID.
    dry_run : PipelineSession | None, optional
        Completed Engineering Dry Run to export. Deployment uses persisted
        Governance records and does not depend on this session.
    context : dict | None, optional
        Configured Engineering notebook context for the destination workspace.

    Returns
    -------
    dict
        Widget, state, controls and export/review/deploy actions. Portable JSON
        can be downloaded and imported in a separate Governance session.

    Notes
    -----
    Engineering cannot decide approvals through this workflow. Fabric permissions
    must deny Engineering writes to Governance tables and accepted package copies.
    Rollback exports an earlier implementation for a new approval and version.
    Restoration exports the active implementation for explicit recovery approval.
    Deployment readback verifies the complete definition, including non-code cells.

    Examples
    --------
    >>> ui = widget_deploy_pipeline(dry_run=preview)
    >>> ui = widget_deploy_pipeline(pipeline_id=PIPELINE_ID)

    """
    startup = shared.WidgetStartup("Engineering deployment", tone="engineering", reserved_height="560px")
    config, workspace, runtime = resolve_fabric_context(context=context)
    routed = {**runtime, "config": config, "scope_workspace_id": workspace}
    spark = get_spark_session(context=runtime)
    widgets = shared.require_ipywidgets()
    if pipeline_id is None and dry_run is not None:
        pipeline_id = dry_run.plan.pipeline_id
    destination = widgets.Text(value=workspace, layout=widgets.Layout(width="100%"))
    approval = widgets.Dropdown(options=[], layout=widgets.Layout(width="100%"))
    retained = widgets.Dropdown(options=[], layout=widgets.Layout(width="100%"))
    intent = widgets.Dropdown(options=[("Rollback through a new version", "rollback"), ("Restore the active notebook", "restore")], layout=widgets.Layout(width="100%"))
    export_button = widgets.Button(description="Export Dry Run submission", disabled=dry_run is None)
    retained_button = widgets.Button(description="Export recovery submission")
    review_button = widgets.Button(description="Review approved deployment")
    refresh_button = widgets.Button(description="Refresh approvals")
    deploy_button = widgets.Button(description="Deploy approved notebook", button_style="primary", disabled=True)
    confirm = widgets.Checkbox(description="Deploy this exact approved notebook in this workspace", indent=False)
    report, download = widgets.HTML(), widgets.HTML()
    exported_json = widgets.Textarea(layout=widgets.Layout(width="100%", height="120px"))
    state = {"package": None, "approval_id": None, "result": None}
    def invalidate(_event=None):
        state["approval_id"] = None
        confirm.value = False
        deploy_button.disabled = True
    def refresh():
        rows = read_approvals(context=routed, spark_session=spark)
        options = []
        for row in rows:
            if row["status"] != "approved" or row["execution_workspace_id"] != workspace or pipeline_id and row["pipeline_id"] != pipeline_id:
                continue
            try:
                authoritative_approval(row["approval_id"], context=routed, spark_session=spark)
            except ValueError:
                continue
            options.append((f'{row["pipeline_id"]} / {row["submission_id"]} · {row["decision_kind"]}', row["approval_id"]))
        approval.options = [("Select a Governance approval", None)] + options
        records = [row for row in read_registry(context=routed, spark_session=spark)
            if row["execution_workspace_id"] == workspace and (not pipeline_id or row["pipeline_id"] == pipeline_id)]
        retained.options = [(f'{row["pipeline_id"]} v{row["pipeline_version"]} · {row["status"]}', row["promotion_id"]) for row in records]
        retained_button.disabled = not records
        invalidate()
        return rows
    def show_package(package):
        state["package"] = package
        exported_json.value = json.dumps(package, sort_keys=True, ensure_ascii=False)
        encoded = base64.b64encode(json.dumps(package, sort_keys=True, ensure_ascii=False).encode()).decode()
        download.value = '<a download="fabricops-submission.json" href="data:application/json;base64,' + encoded + '">Download immutable submission package</a><p>Import this file in the Governance workspace. A digest identifies content; it does not certify testing outcomes.</p>'
        return package
    def export():
        return show_package(export_pipeline_submission(dry_run, destination_workspace_id=destination.value.strip(), context=routed, spark_session=spark))
    def export_recovery():
        return show_package(export_retained_submission(retained.value, intent=intent.value, context=routed, spark_session=spark))
    def review():
        result = authoritative_approval(approval.value, context=routed, spark_session=spark)
        if result["execution_workspace_id"] != workspace:
            raise ValueError("Select an approval for this Engineering workspace.")
        state["approval_id"] = result["approval_id"]
        state["result"] = None
        confirm.value = False
        report.value = "<pre style='white-space:pre-wrap;max-height:480px;overflow:auto'>" + html.escape(json.dumps(result, indent=2, default=str)) + "</pre>"
        return result
    def deploy():
        if not confirm.value or state["approval_id"] != approval.value or state["approval_id"] is None:
            raise ValueError("Review and explicitly confirm an authoritative Governance approval first.")
        result = deploy_approved_submission(state["approval_id"], context=routed, spark_session=spark)
        state["result"] = result
        deploy_button.disabled = True
        report.value += "<p>Approved operation completed. Governed execution remains gated pending signed-in Fabric acceptance. Update engineer-owned schedule targets explicitly.</p>"
        return result
    def run(action, button):
        button.disabled = True
        try:
            action()
        except Exception as exc:
            report.value += "<p role='alert'>" + html.escape(str(exc)) + "</p>"
        finally:
            export_button.disabled = dry_run is None
            button.disabled = False
            deploy_button.disabled = not confirm.value or state["approval_id"] is None or state["result"] is not None
    approval.observe(invalidate, names="value")
    confirm.observe(lambda _event: setattr(deploy_button, "disabled", not confirm.value or state["approval_id"] is None or state["result"] is not None), names="value")
    for button, action in ((export_button, export), (retained_button, export_recovery), (review_button, review), (refresh_button, refresh), (deploy_button, deploy)):
        button.on_click(lambda _button, action=action, button=button: run(action, button))
    with startup.phase("metadata_loading", "Loading read-only Governance approvals and retained Engineering deployments…"):
        refresh()
    root = shared.form_page(widgets, title="Engineering deployment", tone="engineering",
        description="Submit completed tests for independent review, then deploy the approved snapshot.", children=[
            widgets.HTML("<label>Submission execution workspace</label>"), destination, export_button, download,
            widgets.HTML("<label>Copy portable submission JSON for Governance import</label>"), exported_json,
            widgets.HTML("<label>Retained implementation</label>"), retained,
            widgets.HTML("<label>Recovery operation to request</label>"), intent, retained_button,
            widgets.HTML("<label>Authoritative Governance approval for this workspace</label>"), approval,
            refresh_button, review_button, report, confirm, deploy_button])
    startup.display(root)
    return {"widget": root, "state": state, "controls": {"destination": destination, "approval": approval, "retained": retained,
        "intent": intent, "package": exported_json, "confirm": confirm, "export": export_button, "deploy": deploy_button},
        "actions": {"export": export, "export_retained": export_recovery, "review": review, "deploy": deploy, "refresh": refresh}}
