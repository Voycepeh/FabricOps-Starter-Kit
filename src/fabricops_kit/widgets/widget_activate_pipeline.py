"""Governance review of saved submissions from the central Metadata Lakehouse."""
from __future__ import annotations

import base64
import html
import json

from fabricops_kit.activated_pipeline.shared import (
    FABRIC_VALIDATION_PENDING, decide_pipeline_submission, import_pipeline_submission,
    list_pipeline_submissions, read_pipeline_submission, read_approvals, read_registry, review_submission_policy, validate_submission,
)
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.widgets import shared


def widget_activate_pipeline(*, pipeline_id=None, context=None) -> dict:
    """Select, review and decide a saved Engineering submission in Governance.

    Parameters
    ----------
    pipeline_id : str | None, optional
        Filter saved submissions and decision history by logical Pipeline ID.
    context : dict | None, optional
        Configured Governance notebook context and central Metadata routing.

    Returns
    -------
    dict
        Widget, controls, state and review/decide/refresh actions. Approval
        grants deployment authority; Engineering must separately deploy it.

    Notes
    -----
    Finalize saves packages in the configured Metadata Lakehouse. This widget
    lists them directly; no file download, upload or JSON paste is needed.
    Opening the widget only reads storage. Review re-reads the selected package,
    rejects changes since refresh and persists an immutable Governance-owned copy
    before policy review. Decisions use that copy, never mutable Engineering Files.
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
    selection = widgets.Dropdown(options=[], layout=widgets.Layout(width="100%"))
    decision = widgets.Dropdown(options=[("Approve", "approved"), ("Reject", "rejected"), ("Revoke", "revoked")], layout=widgets.Layout(width="100%"))
    note = widgets.Textarea(layout=widgets.Layout(width="100%", height="80px"))
    expires = widgets.Text(placeholder="Optional UTC ISO timestamp", layout=widgets.Layout(width="100%"))
    confirm = widgets.Checkbox(description="I independently reviewed this exact submission and policy", indent=False)
    refresh_button = widgets.Button(description="Refresh submissions")
    review_button = widgets.Button(description="Review submission")
    decide_button = widgets.Button(description="Save Governance decision", button_style="primary", disabled=True)
    report, history = widgets.HTML(), widgets.HTML()
    state = {"review": None, "result": None, "rows": [], "deployments": [], "pending": {}, "submission_errors": []}
    def invalidated(_event=None):
        state["review"] = None
        state["result"] = None
        confirm.value = False
        decide_button.disabled = True
    def refresh():
        invalidated()
        rows = read_approvals(context=routed, spark_session=spark)
        state["rows"] = rows
        scoped = [row for row in rows if (not pipeline_control.value.strip() or row["pipeline_id"] == pipeline_control.value.strip())
            and (not workspace_control.value.strip() or row["execution_workspace_id"] == workspace_control.value.strip())]
        discovery = list_pipeline_submissions(context=routed, spark_session=spark)
        state["pending"] = {package["manifest"]["submission_id"]: package for package in discovery["submissions"]
            if (not pipeline_control.value.strip() or package["manifest"]["pipeline_id"] == pipeline_control.value.strip())
            and (not workspace_control.value.strip() or package["manifest"]["execution_workspace_id"] == workspace_control.value.strip())}
        state["submission_errors"] = discovery["errors"]
        candidates = {identity: {**package["manifest"], "status": "pending review"} for identity, package in state["pending"].items()}
        for row in sorted(scoped, key=lambda row: row["revision"]):
            candidates[row["submission_id"]] = row
        selected = selection.value
        selection.options = [("Select a saved submission", None)] + [(f'{row["execution_workspace_id"]} / {row["pipeline_id"]} / {key} · {row["status"]}', key)
            for key, row in candidates.items()]
        if selected in candidates:
            selection.value = selected
        # Governance owns all metadata, but visibility never implies permission to deploy.
        state["deployments"] = [row for row in read_registry(context=routed, spark_session=spark)
            if (not pipeline_control.value.strip() or row["pipeline_id"] == pipeline_control.value.strip())
            and (not workspace_control.value.strip() or row["execution_workspace_id"] == workspace_control.value.strip())]
        history.value = "<details><summary>Approval history and recorded deployments</summary><pre style='white-space:pre-wrap'>" + html.escape(
            json.dumps({"decisions": [{key: value for key, value in row.items() if key != "package_json"} for row in scoped],
                "deployments": state["deployments"], "unavailable_submissions": state["submission_errors"]}, indent=2, default=str)) + "</pre></details>"
        if state["submission_errors"]:
            report.value = "<p role='alert'>Some saved submissions could not be loaded. See unavailable submissions in the history below.</p>"
        return scoped
    def review():
        invalidated()
        rows = read_approvals(context=routed, spark_session=spark)
        matches = [row for row in rows if row["submission_id"] == selection.value]
        if not matches:
            listed = state["pending"].get(selection.value)
            if listed is None:
                raise ValueError("Refresh and select a saved submission first.")
            package = read_pipeline_submission(selection.value, expected_sha256=listed["submission_sha256"], context=routed, spark_session=spark)
            accepted = import_pipeline_submission(package, context=routed, spark_session=spark)
            rows = read_approvals(context=routed, spark_session=spark)
            matches = [accepted]
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
    for button, action in ((refresh_button, refresh), (review_button, review), (decide_button, decide)):
        button.on_click(lambda _button, action=action, button=button: run(action, button))
    with startup.phase("metadata_loading", "Loading Governance decisions and recorded deployments…"):
        refresh()
    root = shared.form_page(widgets, title="Pipeline approval", tone="governance",
        description="Select a saved Engineering submission, review it independently and record a decision.", children=[
            widgets.HTML("<p>" + html.escape(FABRIC_VALIDATION_PENDING) + "</p>"),
            widgets.HTML("<label>Execution workspace ID filter</label>"), workspace_control,
            widgets.HTML("<label>Pipeline ID filter</label>"), pipeline_control,
            widgets.HTML("<label>Saved pipeline submission</label>"), selection, refresh_button,
            widgets.HTML("<label>Decision</label>"), decision, review_button, report,
            widgets.HTML("<label>Independent review note</label>"), note,
            widgets.HTML("<label>Approval expiration</label>"), expires, confirm, decide_button, history])
    startup.display(root)
    return {"widget": root, "state": state, "ready": False, "reason": FABRIC_VALIDATION_PENDING,
        "controls": {"workspace": workspace_control, "pipeline": pipeline_control,
            "submission": selection, "decision": decision, "note": note, "expires": expires, "confirm": confirm,
            "review": review_button, "decide": decide_button},
        "actions": {"review": review, "decide": decide, "refresh": refresh}}
