"""Governance review of portable submissions, independent of Engineering sessions."""
from __future__ import annotations

import base64
import html
import json

from fabricops_kit.activated_pipeline.shared import (
    FABRIC_VALIDATION_PENDING, decide_pipeline_submission, import_pipeline_submission,
    read_approvals, read_registry, review_submission_policy, validate_submission,
)
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.widgets import shared


def widget_activate_pipeline(*, pipeline_id=None, package=None, context=None) -> dict:
    """Import, review and decide an immutable notebook submission in Governance.

    Parameters
    ----------
    pipeline_id : str | None, optional
        Filter imported candidates and decision history by logical Pipeline ID.
    package : str | bytes | dict | None, optional
        Portable Engineering submission. The import action persists a verified
        immutable copy under Governance's identity; opening the widget does not.
    context : dict | None, optional
        Configured Governance notebook context and central Metadata routing.

    Returns
    -------
    dict
        Widget, controls, state and import/review/decide/refresh actions. Approval
        grants deployment authority; Engineering must separately deploy it.

    Notes
    -----
    This widget never opens Engineering notebooks or creates deployed items.
    Integrity does not attest the truth of engineer-provided test outcomes.
    Review source code, Dry Run claims and independently resolved active policies.
    Rollback and restoration packages require separate explicit decisions here.
    Governance owns the entire Metadata Lakehouse; schema names are routing, not
    restrictions on privileged Governance workspace members.

    Examples
    --------
    >>> ui = widget_activate_pipeline()

    """
    startup = shared.WidgetStartup("Pipeline approval", tone="governance", reserved_height="560px")
    config, workspace, runtime = resolve_fabric_context(context=context)
    routed = {**runtime, "config": config, "scope_workspace_id": workspace}
    spark = get_spark_session(context=runtime)
    widgets = shared.require_ipywidgets()
    workspace_control = widgets.Text(description="", layout=widgets.Layout(width="100%"))
    pipeline_control = widgets.Text(value=pipeline_id or "", layout=widgets.Layout(width="100%"))
    payload = widgets.Textarea(value=json.dumps(package) if isinstance(package, dict) else (package.decode() if isinstance(package, bytes) else package or ""),
        layout=widgets.Layout(width="100%", height="120px"))
    selection = widgets.Dropdown(options=[], layout=widgets.Layout(width="100%"))
    decision = widgets.Dropdown(options=[("Approve", "approved"), ("Reject", "rejected"), ("Revoke", "revoked")], layout=widgets.Layout(width="100%"))
    note = widgets.Textarea(layout=widgets.Layout(width="100%", height="80px"))
    expires = widgets.Text(placeholder="Optional UTC ISO timestamp", layout=widgets.Layout(width="100%"))
    confirm = widgets.Checkbox(description="I independently reviewed this exact submission and policy", indent=False)
    import_button = widgets.Button(description="Import submission")
    refresh_button = widgets.Button(description="Refresh history")
    review_button = widgets.Button(description="Review candidate")
    decide_button = widgets.Button(description="Save Governance decision", button_style="primary", disabled=True)
    report, history = widgets.HTML(), widgets.HTML()
    state = {"review": None, "result": None, "rows": [], "deployments": []}
    def invalidated(_event=None):
        state["review"] = None
        state["result"] = None
        confirm.value = False
        decide_button.disabled = True
    def refresh():
        rows = read_approvals(context=routed, spark_session=spark)
        state["rows"] = rows
        scoped = [row for row in rows if (not pipeline_control.value.strip() or row["pipeline_id"] == pipeline_control.value.strip())
            and (not workspace_control.value.strip() or row["execution_workspace_id"] == workspace_control.value.strip())]
        candidates = {}
        for row in sorted(scoped, key=lambda row: row["revision"]):
            candidates[row["submission_id"]] = row
        selected = selection.value
        selection.options = [(f'{row["execution_workspace_id"]} / {row["pipeline_id"]} / {key} · {row["status"]}', key)
            for key, row in candidates.items()]
        if selected in candidates:
            selection.value = selected
        # Governance owns all metadata, but visibility never implies permission to deploy.
        state["deployments"] = [row for row in read_registry(context=routed, spark_session=spark)
            if (not pipeline_control.value.strip() or row["pipeline_id"] == pipeline_control.value.strip())
            and (not workspace_control.value.strip() or row["execution_workspace_id"] == workspace_control.value.strip())]
        history.value = "<details><summary>Approval history and recorded deployments</summary><pre style='white-space:pre-wrap'>" + html.escape(
            json.dumps({"decisions": [{key: value for key, value in row.items() if key != "package_json"} for row in scoped],
                "deployments": state["deployments"]}, indent=2, default=str)) + "</pre></details>"
        invalidated()
        return scoped
    def import_candidate():
        raw = payload.value
        accepted = import_pipeline_submission(raw, context=routed, spark_session=spark)
        workspace_control.value = accepted["execution_workspace_id"]
        pipeline_control.value = accepted["pipeline_id"]
        refresh()
        selection.value = accepted["submission_id"]
        report.value = "<p>Immutable review copy imported. Test outcomes remain untrusted claims until reviewed.</p>"
        return accepted
    def review():
        rows = read_approvals(context=routed, spark_session=spark)
        matches = [row for row in rows if row["submission_id"] == selection.value]
        if not matches:
            raise ValueError("Import and select a submission first.")
        row = max(matches, key=lambda item: item["revision"])
        package_value = validate_submission(row["package_json"])
        manifest = package_value["manifest"]
        policy = review_submission_policy(package_value, context=routed, spark_session=spark) if decision.value == "approved" else {}
        revision = max(item["revision"] for item in rows if item["pipeline_id"] == row["pipeline_id"]
            and item["execution_workspace_id"] == row["execution_workspace_id"])
        state["review"] = {"submission_id": selection.value, "revision": revision, "policy": policy, "status": decision.value}
        confirm.value = False
        report.value = "<h3>Review exact submission</h3><p>Approval does not deploy a notebook. Recorded Dry Run results are Engineering claims.</p>"
        for title, content in (("Manifest and approved physical bindings", manifest), ("Recorded Dry Run", package_value["dry_run"]),
                ("Recorded Contract evidence", package_value["contracts"]), ("Independently resolved current policy", policy)):
            report.value += "<details open><summary>" + title + "</summary><pre style='white-space:pre-wrap;max-height:360px;overflow:auto'>" + html.escape(json.dumps(content, indent=2, default=str)) + "</pre></details>"
        for key, title in (("executed_notebook_base64", "Complete saved definition captured before testing"), ("source_notebook_base64", "Complete submitted saved source notebook"), ("notebook_base64", "Exact notebook authorized for deployment")):
            report.value += "<details><summary>" + title + "</summary><pre style='white-space:pre-wrap;max-height:360px;overflow:auto'>" + html.escape(base64.b64decode(package_value[key]).decode()) + "</pre></details>"
        return state["review"]
    def decide():
        reviewed = state["review"]
        if not reviewed or not confirm.value or reviewed["status"] != decision.value:
            raise ValueError("Review and explicitly confirm this exact Governance decision first.")
        result = decide_pipeline_submission(reviewed["submission_id"], status=reviewed["status"], expected_revision=reviewed["revision"],
            policy=reviewed["policy"], review_note=note.value, governance_confirmed=True,
            expires_at=expires.value.strip() or None, context=routed, spark_session=spark)
        refresh()
        state["result"] = result
        report.value += "<p>Governance decision saved. Engineering performs any approved deployment separately.</p>"
        return result
    def run(action, button):
        button.disabled = True
        try:
            action()
        except Exception as exc:
            report.value += "<p role='alert'>" + html.escape(str(exc)) + "</p>"
        finally:
            button.disabled = False
            decide_button.disabled = not state["review"] or not confirm.value
    for control in (selection, decision, workspace_control, pipeline_control):
        control.observe(invalidated, names="value")
    confirm.observe(lambda _event: setattr(decide_button, "disabled", not state["review"] or not confirm.value), names="value")
    for button, action in ((import_button, import_candidate), (refresh_button, refresh), (review_button, review), (decide_button, decide)):
        button.on_click(lambda _button, action=action, button=button: run(action, button))
    with startup.phase("metadata_loading", "Loading Governance decisions and recorded deployments…"):
        refresh()
    root = shared.form_page(widgets, title="Pipeline approval", tone="governance",
        description="Import an Engineering package, review it independently and record a decision.", children=[
            widgets.HTML("<p>" + html.escape(FABRIC_VALIDATION_PENDING) + "</p>"),
            widgets.HTML("<label>Execution workspace ID filter</label>"), workspace_control,
            widgets.HTML("<label>Pipeline ID filter</label>"), pipeline_control,
            widgets.HTML("<label>Paste portable submission JSON</label>"), payload, import_button,
            widgets.HTML("<label>Imported submission</label>"), selection, refresh_button,
            widgets.HTML("<label>Decision</label>"), decision, review_button, report,
            widgets.HTML("<label>Independent review note</label>"), note,
            widgets.HTML("<label>Approval expiration</label>"), expires, confirm, decide_button, history])
    startup.display(root)
    return {"widget": root, "state": state, "ready": False, "reason": FABRIC_VALIDATION_PENDING,
        "controls": {"workspace": workspace_control, "pipeline": pipeline_control, "package": payload,
            "submission": selection, "decision": decision, "note": note, "expires": expires, "confirm": confirm,
            "import": import_button, "review": review_button, "decide": decide_button},
        "actions": {"import": import_candidate, "review": review, "decide": decide, "refresh": refresh}}
