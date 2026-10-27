"""One Governance review for dependency-aware coordinated pipeline activation."""
from __future__ import annotations

from fabricops_kit.io.shared import get_spark_session

import html
import json
from typing import Any

from fabricops_kit.activated_pipeline.shared import (
    metadata_records, manifest_digest, read_pipeline_authority, workspace_activation,
    pipeline_table_mappings, review_pipeline_release, approve_pipeline_release,
)
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.widgets import shared


def _eligible_candidate(row, pipeline_id=None):
    """Exclude incomplete, corrupt and ungoverned runs before independent backend review."""
    try:
        from fabricops_kit.pipeline.shared import validate_pipeline_run
        validate_pipeline_run(row)
        return bool(row["execution_mode"] == "testing" and row["status"] == "succeeded"
                    and (pipeline_id is None or row["pipeline_id"] == pipeline_id)
                    and all(item.get("contract_id") for item in row["operations"]))
    except (ValueError, KeyError, TypeError):
        return False


def _missing_contracts(row):
    """List completed Test tables lacking a frozen contract selection."""
    if row.get("execution_mode") != "testing" or row.get("status") not in {"succeeded", "ungoverned_completed"} or not row.get("completed_at"):
        return []
    try:
        return sorted({item["table_id"] for item in row["operations"] if isinstance(item.get("table_id"), str)
                       and item["table_id"] and not item.get("contract_id")})
    except (KeyError, TypeError, AttributeError):
        return []


def _release_view(report, candidates):
    """Render the contract and writer decisions with expandable Testing details."""
    visible = set(report.get("changed_tables", []))
    for candidate in candidates:
        visible.update(item["table_id"] for item in candidate["operations"])
    rows = []
    def text(value):
        return html.escape(str(value if value is not None else "None"))
    for table_id in sorted(visible):
        old = report.get("current_tables", {}).get(table_id, {})
        new = report.get("tables", {}).get(table_id, {})
        values = [table_id, old.get("contract_version"), new.get("contract_version"), old.get("writer"), new.get("writer"), ", ".join(new.get("readers", [])) or "None"]
        rows.append("<tr>" + "".join("<td>" + text(value) + "</td>" for value in values) + "</tr>")
    table = "<div style='overflow-x:auto'><table><thead><tr><th>Table</th><th>Current version</th><th>Proposed version</th><th>Current writer</th><th>Proposed writer</th><th>Readers</th></tr></thead><tbody>" + "".join(rows) + "</tbody></table></div>"
    blockers = report.get("blocking_conflicts", [])
    status = "Ready for approval" if report.get("ready") else "Release requires attention"
    result = "<h3>" + text(report.get("workspace_id")) + " · " + status + "</h3>" + table
    result += "<ul>" + "".join("<li>" + text(item) + "</li>" for item in blockers) + "</ul>"
    result += "<p>Affected pipelines: " + text(", ".join(report.get("affected_pipelines", [])) or "None") + "</p>"
    for candidate in candidates:
        detail = {"run_id": candidate["run_id"], "status": candidate["status"],
                  "operations": candidate["operations"]}
        result += "<details><summary>" + text(candidate["pipeline_id"]) + " · Successful Testing</summary><pre>" + html.escape(json.dumps(detail, indent=2, default=str)) + "</pre></details>"
    return result


def widget_activate_pipeline(*, pipeline_id=None, context=None) -> dict[str, Any]:
    """Review one successful Testing run and coordinate all affected pipeline candidates.

    Spark is resolved automatically from the existing execution session.
    No session is created; Spark-dependent work raises
    ``RuntimeError`` when no session is available.

    Displays workspace_id, current/proposed table contracts, writer ownership,
    affected pipelines, missing tests, conflicts and complete release readiness.
    Completed Testing runs missing contracts are listed by table ID and excluded
    from review. Extra candidate controls appear for shared-table dependencies.
    Supply an immutable release version for
    every selected pipeline. The backend revalidates complete Testing, exact
    contracts, Agreement, locations and operation modes at review and again at approval.

    One explicit approval publishes the entire workspace_id revision atomically.
    Stale review, missing tests, competing writers, contract conflicts or affected
    running executions block approval. Approval never deploys or writes business
    data. Failed commits cannot expose a partial release. Returns widget state,
    refresh, review_release and perform_activation. Metadata errors raise or are
    displayed by button actions; opening the widget changes no approval.
    """
    spark_session = get_spark_session(context=context)
    import ipywidgets as widgets

    startup = shared.WidgetStartup("Pipeline Activation")
    with startup.phase("initialization", "Resolving FabricOps configuration…"):
        _config, active_workspace_id, _runtime = resolve_fabric_context(context=context)
    with startup.phase("metadata_loading", "Loading configured metadata…"):
        all_runs = json.loads(json.dumps(metadata_records("METADATA_PIPELINE_RUN", context=context,
            spark_session=spark_session, all_workspaces=True), default=str))
    runs = [row for row in all_runs if _eligible_candidate(row)]
    excluded = [(row, _missing_contracts(row)) for row in all_runs
                if pipeline_id is None or row["pipeline_id"] == pipeline_id]
    coverage_notice = widgets.HTML(layout=widgets.Layout(width="100%", min_width="0"))
    missing_rows = ["<li>" + html.escape(str(row["pipeline_id"])) + " · " + html.escape(str(row["run_id"]))
                    + ": missing frozen Data Contracts for table IDs: " + html.escape(", ".join(missing)) + "</li>"
                    for row, missing in excluded if missing]
    if missing_rows:
        coverage_notice.value = ('<div style="overflow-wrap:anywhere"><p><b>Testing completed, but these runs cannot activate.</b></p><ul>'
            + "".join(missing_rows) + "</ul><p>Select a valid frozen Data Contract for every listed table and rerun complete Testing. "
            "All existing Guardrail, operation and Data Agreement checks must also pass.</p></div>")
    with startup.phase("metadata_loading", "Loading Data Agreements…"):
        agreements = metadata_records("METADATA_DATA_AGREEMENT", context=context, spark_session=spark_session)
    pipeline_select = widgets.Dropdown(description="Pipeline", options=[("Select pipeline", ""), *[(value, value) for value in sorted({row["pipeline_id"] for row in runs})]], value=pipeline_id if pipeline_id in {row["pipeline_id"] for row in runs} else "", layout=widgets.Layout(width="100%", min_width="0"))
    workspace_select = widgets.Dropdown(description="Workspace", options=[("Select workspace", ""), *[(value, value) for value in sorted({row["workspace_id"] for row in runs})]], value="", layout=widgets.Layout(width="100%", min_width="0"))
    run_select = widgets.Dropdown(description="Testing run", options=[("Select Testing run", "")], value="", layout=widgets.Layout(width="100%", min_width="0"))
    additions = widgets.SelectMultiple(description="Include tests", options=[(f"{r['pipeline_id']} · {r['run_id']}", r["run_id"]) for r in runs], layout=widgets.Layout(width="100%"))
    agreement = widgets.Dropdown(description="Agreement", options=[(f"{r.get('agreement_name', r['agreement_id'])} · {r['agreement_version']}", (r['agreement_id'], r['agreement_version'])) for r in agreements], layout=widgets.Layout(width="100%"))
    details = widgets.HTML()
    fields = widgets.VBox()
    review_button = widgets.Button(description="Review complete release", button_style="primary")
    confirm = widgets.Checkbox(description="I approve the complete reviewed release", indent=False)
    activate = widgets.Button(description="Activate release", button_style="primary", disabled=True)
    status = shared.status_message(widgets)
    state = {"eligible_runs": runs, "pipeline_select": pipeline_select, "workspace_select": workspace_select,
             "filtering": False, "run_select": run_select, "additional_runs": additions,
             "agreement_select": agreement, "details": details, "confirmed": confirm,
             "activate": activate, "candidate_controls": {}, "activation_result": None}

    def invalidate(*_):
        state.pop("review_token", None)
        activate.disabled = True
        confirm.value = False

    def selected_context():
        if not workspace_select.value:
            raise ValueError("Select the Engineering workspace to review and activate.")
        return {**_runtime, "config": _config, "scope_workspace_id": workspace_select.value}

    def requests():
        if not run_select.value or not workspace_select.value:
            raise ValueError("No eligible Testing run selected. Activation requires complete successful Testing with frozen Data Contracts for every table. Resolve any missing table contracts shown above and rerun Testing.")
        if not agreement.value:
            raise ValueError("Select an exact effective Data Agreement.")
        result = []
        for run_id in dict.fromkeys([run_select.value, *additions.value]):
            row = next(row for row in runs if row["run_id"] == run_id)
            controls = state["candidate_controls"][run_id]
            result.append({"testing_run_id": run_id,
                "pipeline_name": row["pipeline_id"], "pipeline_version": controls["version"].value.strip(),
                "agreement_id": agreement.value[0], "agreement_version": agreement.value[1]})
        return result

    def refresh(*_):
        if state["filtering"]:
            return
        invalidate()
        review_button.disabled = not run_select.value or not workspace_select.value
        token, snapshot = read_pipeline_authority(context=context, spark_session=spark_session)
        current = workspace_activation(snapshot, workspace_select.value or active_workspace_id)
        selected = [r for r in runs if r["run_id"] in {run_select.value, *additions.value}]
        children = []
        changed_tables = set()
        for row in selected:
            controls = state["candidate_controls"].get(row["run_id"])
            if controls is None:
                controls = {"version": widgets.Text(description="Version", layout=widgets.Layout(width="100%"))}
                for control in controls.values():
                    control.observe(invalidate, names="value")
                state["candidate_controls"][row["run_id"]] = controls
            children.append(shared.form_section(widgets, title=row["pipeline_id"] + " · " + row["run_id"], children=list(controls.values())))
            mappings = pipeline_table_mappings(row)
            for table_id, item in mappings.items():
                previous = current["tables"].get(table_id, {})
                if any(previous.get(key) != item[key] for key in ("contract_id", "contract_version", "payload_sha256", "destination")) or (
                    "target" in item["roles"] and previous.get("writer") != row["pipeline_id"]):
                    changed_tables.add(table_id)
            previous_pipeline = current["pipelines"].get(row["pipeline_id"])
            if previous_pipeline:
                old_refs = pipeline_table_mappings(previous_pipeline)
                new_writes = {key for key, item in mappings.items() if "target" in item["roles"]}
                changed_tables.update(table_id for table_id, ref in old_refs.items()
                                      if "target" in ref["roles"] and table_id not in new_writes)
        fields.children = children
        dependencies = {key: sorted(changed_tables.intersection(pipeline_table_mappings(row)))
                        for key, row in current["pipelines"].items()
                        if changed_tables.intersection(pipeline_table_mappings(row))}
        additions.layout.display = "" if set(dependencies) - {r["pipeline_id"] for r in selected} or additions.value else "none"
        summary = {"workspace_id": workspace_select.value or None, "current_revision": current["revision"], "current_contracts_and_writers": current["tables"],
                   "selected_testing_candidates": [{"pipeline_id": r["pipeline_id"], "run_id": r["run_id"],
                       "proposed_contracts": r["operations"]} for r in selected],
                   "dependencies": dependencies,
                   "testing_status": {key: [{"run_id": r["run_id"], "status": r["status"]} for r in all_runs if r["pipeline_id"] == key] for key in dependencies}}
        details.value = ("<p>Select a workspace and pipeline to review eligible Testing evidence.</p>"
                         if not workspace_select.value else
                         "<pre>" + html.escape(json.dumps(summary, indent=2, default=str)) + "</pre>")
        state["summary"] = summary

    def review_release(_=None):
        invalidate()
        token, _snapshot, _proposed, report = review_pipeline_release(requests(), context=selected_context(), spark_session=spark_session)
        state["report"] = report
        selected = [row for row in runs if row["run_id"] in {run_select.value, *additions.value}]
        details.value = _release_view(report, selected)
        if report["ready"]:
            state["review_token"] = token
            state["review_digest"] = report["review_digest"]
            state["reviewed_requests"] = json.loads(json.dumps(requests()))
        return report

    def perform_activation(_=None):
        if not confirm.value or not state.get("review_token") or requests() != state["reviewed_requests"]:
            raise ValueError("Review and explicitly approve the complete current release first.")
        result = approve_pipeline_release(requests(), expected_token=state["review_token"], expected_review_digest=state["review_digest"], governance_confirmed=True,
                                          context=selected_context(), spark_session=spark_session)
        state["activation_result"] = result
        invalidate()
        status.value = "<p>Release activated. New Live runs resolve this revision. Deployment remains separate.</p>"
        return result

    def safe(action):
        def click(_):
            try:
                action()
            except Exception as exc:
                invalidate()
                status.value = "<p>" + html.escape(str(exc)) + "</p>"
        return click

    def filter_choices(change=None, *, source=None):
        if state["filtering"]:
            return
        state["filtering"] = True
        try:
            selected_pipeline, selected_workspace = pipeline_select.value, workspace_select.value
            if source == "workspace" and not any(row["pipeline_id"] == selected_pipeline and row["workspace_id"] == selected_workspace for row in runs):
                selected_pipeline = ""
            if source == "pipeline" and not any(row["pipeline_id"] == selected_pipeline and row["workspace_id"] == selected_workspace for row in runs):
                selected_workspace = ""
            pipelines = sorted({row["pipeline_id"] for row in runs if not selected_workspace or row["workspace_id"] == selected_workspace})
            workspaces = sorted({row["workspace_id"] for row in runs if not selected_pipeline or row["pipeline_id"] == selected_pipeline})
            labels = {row["workspace_id"]: row.get("_workspace_name") or row["workspace_id"] for row in runs}
            pipeline_select.options = [("Select pipeline", ""), *[(value, value) for value in pipelines]]
            pipeline_select.value = selected_pipeline if selected_pipeline in pipelines else ""
            workspace_select.options = [("Select workspace", ""), *[(f"{labels[value]} ({value})", value) for value in workspaces]]
            workspace_select.value = selected_workspace if selected_workspace in workspaces else ""
            scoped = [row for row in runs if row["workspace_id"] == workspace_select.value]
            candidates = [row for row in scoped if row["pipeline_id"] == pipeline_select.value]
            previous = run_select.value
            run_select.options = [("Select Testing run", ""), *[(row["run_id"], row["run_id"]) for row in candidates]]
            run_select.value = previous if previous in {row["run_id"] for row in candidates} else ""
            valid_ids = {row["run_id"] for row in scoped}
            retained = tuple(value for value in additions.value if value in valid_ids)
            additions.options = [(f"{row['pipeline_id']} · {row['run_id']}", row["run_id"]) for row in scoped]
            additions.value = retained
        finally:
            state["filtering"] = False
        refresh()

    pipeline_select.observe(lambda change: filter_choices(change, source="pipeline"), names="value")
    workspace_select.observe(lambda change: filter_choices(change, source="workspace"), names="value")
    for control in (run_select, additions):
        control.observe(refresh, names="value")
    agreement.observe(invalidate, names="value")
    confirm.observe(lambda _: setattr(activate, "disabled", not (confirm.value and state.get("review_token"))), names="value")
    review_button.on_click(safe(review_release))
    activate.on_click(safe(perform_activation))
    selector = widgets.GridBox([pipeline_select, run_select, workspace_select],
        layout=widgets.Layout(width="100%", grid_template_columns="repeat(3, minmax(0, 1fr))", grid_gap="16px"))
    selector.add_class("fabricops-activation-selector")
    root = shared.form_page(widgets, title="Activate a tested pipeline", tone="governance",
        description="Select an Engineering workspace, review shared tables and approve its complete release.",
        children=[coverage_notice, selector, additions, fields, agreement, details, review_button, confirm,
                  shared.action_row(widgets, [activate]), status])
    root.add_class("fabricops-pipeline-activation")
    root.children[0].value += "<style>@container (max-width:650px){.fabricops-pipeline-activation .fabricops-activation-selector{grid-template-columns:minmax(0,1fr)!important;}}</style>"
    state.update(widget=root, refresh=refresh, review_release=review_release, perform_activation=perform_activation)
    with startup.phase("metadata_loading", "Loading activation state…"):
        filter_choices()
    startup.display(root)
    return state
