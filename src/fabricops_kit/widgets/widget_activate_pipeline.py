"""One Governance review for dependency-aware coordinated pipeline activation."""
from __future__ import annotations

import html
import json
from typing import Any

from fabricops_kit.activated_pipeline.shared import (
    metadata_records, manifest_digest, read_activation_state, environment_activation,
    manifest_table_mappings, validate_manifest, review_pipeline_release, approve_pipeline_release,
)
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.widgets import shared


def _eligible_candidate(row, pipeline_id=None):
    """Exclude incomplete, corrupt and ungoverned runs before independent backend review."""
    try:
        candidate = json.loads(row["candidate_json"])
        summary = json.loads(row["operation_summary_json"])
        expected = {f"{role}:{item['participant']}" for item in candidate["participants"] for role in item["roles"]}
        return bool(row.get("execution_mode") == "testing" and row.get("status") == "succeeded"
                    and row.get("completed_at") and (pipeline_id is None or row["pipeline_id"] == pipeline_id)
                    and expected and set(summary["operations"]) == expected and not summary.get("failures")
                    and summary.get("boundary_completed") is True
                    and isinstance(summary.get("physical_bindings"), dict)
                    and summary["physical_bindings"] == candidate.get("physical_bindings")
                    and all(item.get("table_id") for item in summary["frozen_contracts"])
                    and all(item.get("table_id") for item in candidate["participants"])
                    and len(summary["frozen_contracts"]) == len(candidate["participants"])
                    and all(item["contract"] for item in summary["frozen_contracts"])
                    and all(item.get("status") == "succeeded" for item in summary["operations"].values())
                    and row["candidate_fingerprint"] and manifest_digest(candidate) == row["candidate_fingerprint"])
    except (ValueError, KeyError, TypeError):
        return False


def _missing_contracts(row):
    """Describe missing coverage without admitting the run to activation review."""
    if row.get("execution_mode") != "testing" or row.get("status") not in {"succeeded", "ungoverned_completed"} or not row.get("completed_at"):
        return []
    try:
        candidate = json.loads(row["candidate_json"])
        summary = json.loads(row["operation_summary_json"])
        return sorted({item["table_id"] for item in [*candidate["participants"], *summary["frozen_contracts"]]
                       if isinstance(item, dict) and isinstance(item.get("table_id"), str) and item["table_id"] and not item.get("contract")})
    except (ValueError, KeyError, TypeError):
        return []


def _release_view(report, candidates, requests):
    """Render the contract and writer decisions with expandable Testing details."""
    visible = set(report.get("changed_tables", []))
    for candidate in candidates:
        visible.update(item["table_id"] for item in json.loads(candidate["operation_summary_json"])["frozen_contracts"])
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
    result = "<h3>" + text(report.get("environment")) + " · " + status + "</h3>" + table
    result += "<ul>" + "".join("<li>" + text(item) + "</li>" for item in blockers) + "</ul>"
    result += "<p>Affected pipelines: " + text(", ".join(report.get("affected_pipelines", [])) or "None") + "</p>"
    verification = {request["testing_run_id"]: request["testing_verification"] for request in requests}
    for candidate in candidates:
        detail = {"run_id": candidate["run_id"], "status": candidate["status"],
                  "testing_notebook_binding": candidate.get("testing_notebook_binding"),
                  "testing_verification": verification[candidate["run_id"]],
                  "configuration": json.loads(candidate["candidate_json"]),
                  "execution_results": json.loads(candidate["operation_summary_json"])}
        result += "<details><summary>" + text(candidate["pipeline_id"]) + " · Successful Testing</summary><pre>" + html.escape(json.dumps(detail, indent=2, default=str)) + "</pre></details>"
    return result


def widget_activate_pipeline(*, testing_results, pipeline_id=None, spark_session=None, context=None) -> dict[str, Any]:
    """Review one successful Testing run and coordinate all affected pipeline candidates.

    Pass finalized in-memory Test results using testing_results=[pipeline_result].
    For each candidate, independently check its Fabric notebook execution,
    enter the Fabric run reference and attest that the Test actually ran.
    No execution metadata is committed by Test; approval freezes the reviewed
    evidence in METADATA_ACTIVATION_STATE.

    Displays environment, current/proposed table contracts, writer ownership,
    affected pipelines, missing tests, conflicts and complete release readiness.
    Completed Testing runs missing contracts are listed by table ID and excluded
    from review. Extra candidate controls appear for shared-table dependencies.
    Supply an immutable release version for
    every selected pipeline. The backend checks the supplied Test result,
    current registered notebook binding, exact contracts, Agreement and
    processing configuration at review and again at approval. Because Test
    commits no execution record, Governance must verify the Fabric run itself.

    One explicit approval publishes the entire environment revision atomically.
    Stale review, missing tests, competing writers, contract conflicts or affected
    running executions block approval. Approval never deploys or writes business
    data. Failed commits cannot expose a partial release. Returns widget state,
    refresh, review_release and perform_activation. Metadata errors raise or are
    displayed by button actions; opening the widget changes no approval.
    """
    import ipywidgets as widgets

    startup = shared.WidgetStartup("Pipeline Activation")
    with startup.phase("initialization", "Resolving FabricOps configuration…"):
        _config, env, _runtime = resolve_fabric_context(context=context)
    with startup.phase("metadata_loading", "Loading configured metadata…"):
        all_runs = json.loads(json.dumps(list(testing_results), default=str))
        if any(row.get("environment_name") != env for row in all_runs):
            raise ValueError("Testing results must belong to the activation environment.")
        if len({row["run_id"] for row in all_runs}) != len(all_runs):
            raise ValueError("Select each Testing result only once.")
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
    primary = [row for row in runs if pipeline_id is None or row["pipeline_id"] == pipeline_id]
    run_select = widgets.Dropdown(description="Testing run", options=[(f"{r['pipeline_id']} · {r['run_id']}", r["run_id"]) for r in primary], layout=widgets.Layout(width="100%"))
    additions = widgets.SelectMultiple(description="Include tests", options=[(f"{r['pipeline_id']} · {r['run_id']}", r["run_id"]) for r in runs], layout=widgets.Layout(width="100%"))
    agreement = widgets.Dropdown(description="Agreement", options=[(f"{r.get('agreement_name', r['agreement_id'])} · {r['agreement_version']}", (r['agreement_id'], r['agreement_version'])) for r in agreements], layout=widgets.Layout(width="100%"))
    details = widgets.HTML()
    fields = widgets.VBox()
    review_button = widgets.Button(description="Review complete release", button_style="primary")
    confirm = widgets.Checkbox(description="I approve the complete reviewed release", indent=False)
    activate = widgets.Button(description="Activate release", button_style="primary", disabled=True)
    status = shared.status_message(widgets)
    state = {"eligible_runs": runs, "run_select": run_select, "additional_runs": additions,
             "agreement_select": agreement, "details": details, "confirmed": confirm,
             "activate": activate, "candidate_controls": {}, "activation_result": None}

    def invalidate(*_):
        state.pop("review_token", None)
        activate.disabled = True
        confirm.value = False

    def requests():
        if run_select.value is None:
            raise ValueError("No eligible Testing run selected. Activation requires complete successful Testing with frozen Data Contracts for every table. Resolve any missing table contracts shown above and rerun Testing.")
        if not agreement.value:
            raise ValueError("Select an exact effective Data Agreement.")
        result = []
        for run_id in dict.fromkeys([run_select.value, *additions.value]):
            row = next(row for row in runs if row["run_id"] == run_id)
            controls = state["candidate_controls"][run_id]
            result.append({"testing_result": row, "testing_run_id": run_id, "candidate_fingerprint": row["candidate_fingerprint"],
                "pipeline_name": row["pipeline_id"], "pipeline_version": controls["version"].value.strip(),
                "agreement_id": agreement.value[0], "agreement_version": agreement.value[1],
                "testing_verification": {"verified": controls["verified"].value,
                                         "reference": controls["run_reference"].value.strip()}})
        return result

    def refresh(*_):
        invalidate()
        review_button.disabled = run_select.value is None
        token, snapshot = read_activation_state(context=context, spark_session=spark_session)
        current = environment_activation(snapshot, env)
        selected = [r for r in runs if r["run_id"] in {run_select.value, *additions.value}]
        children = []
        changed_tables = set()
        for row in selected:
            controls = state["candidate_controls"].get(row["run_id"])
            if controls is None:
                controls = {
                    "version": widgets.Text(description="Version", layout=widgets.Layout(width="100%")),
                    "run_reference": widgets.Text(description="Fabric run", placeholder="Verified Fabric notebook run reference",
                        layout=widgets.Layout(width="100%")),
                    "verified": widgets.Checkbox(description="I independently verified this Fabric Test execution", indent=False),
                }
                for control in controls.values():
                    control.observe(invalidate, names="value")
                state["candidate_controls"][row["run_id"]] = controls
            children.append(shared.form_section(widgets, title=row["pipeline_id"] + " · " + row["run_id"], children=list(controls.values())))
            candidate = json.loads(row["candidate_json"])
            summary = json.loads(row["operation_summary_json"])
            roles = {item["participant"]: item["roles"] for item in candidate["participants"]}
            for item in summary["frozen_contracts"]:
                table_id = item["table_id"]
                previous = current["tables"].get(table_id, {})
                if any(previous.get(key) != value for key, value in item["contract"].items()) or (
                    "target" in roles[item["participant"]] and previous.get("writer") != row["pipeline_id"]
                ) or previous.get("destination") != summary["physical_bindings"].get(table_id):
                    changed_tables.add(table_id)
            previous_pipeline = current["pipelines"].get(row["pipeline_id"])
            if previous_pipeline:
                old_refs = manifest_table_mappings(validate_manifest(previous_pipeline))
                new_writes = {item["table_id"] for item in candidate["participants"] if "target" in item["roles"]}
                changed_tables.update(table_id for table_id, ref in old_refs.items()
                                      if "target" in ref["roles"] and table_id not in new_writes)
        fields.children = children
        dependencies = {key: sorted(changed_tables.intersection(manifest_table_mappings(validate_manifest(row))))
                        for key, row in current["pipelines"].items()
                        if changed_tables.intersection(manifest_table_mappings(validate_manifest(row)))}
        additions.layout.display = "" if set(dependencies) - {r["pipeline_id"] for r in selected} or additions.value else "none"
        summary = {"environment": env, "current_revision": current["revision"], "current_contracts_and_writers": current["tables"],
                   "selected_testing_candidates": [{"pipeline_id": r["pipeline_id"], "run_id": r["run_id"],
                       "proposed_contracts": json.loads(r["operation_summary_json"])["frozen_contracts"]} for r in selected],
                   "dependencies": dependencies,
                   "testing_status": {key: [{"run_id": r["run_id"], "status": r["status"]} for r in all_runs if r["pipeline_id"] == key] for key in dependencies}}
        details.value = "<pre>" + html.escape(json.dumps(summary, indent=2, default=str)) + "</pre>"
        state["summary"] = summary

    def review_release(_=None):
        invalidate()
        selected_requests = requests()
        token, _snapshot, _proposed, report = review_pipeline_release(selected_requests, context=context, spark_session=spark_session)
        state["report"] = report
        selected = [row for row in runs if row["run_id"] in {run_select.value, *additions.value}]
        details.value = _release_view(report, selected, selected_requests)
        if report["ready"]:
            state["review_token"] = token
            state["reviewed_requests"] = json.loads(json.dumps(selected_requests))
        return report

    def perform_activation(_=None):
        if not confirm.value or not state.get("review_token") or requests() != state["reviewed_requests"]:
            raise ValueError("Review and explicitly approve the complete current release first.")
        result = approve_pipeline_release(requests(), expected_token=state["review_token"], governance_confirmed=True,
                                          context=context, spark_session=spark_session)
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

    for control in (run_select, additions):
        control.observe(refresh, names="value")
    agreement.observe(invalidate, names="value")
    confirm.observe(lambda _: setattr(activate, "disabled", not (confirm.value and state.get("review_token"))), names="value")
    review_button.on_click(safe(review_release))
    activate.on_click(safe(perform_activation))
    root = shared.form_page(widgets, title="Activate a tested pipeline", tone="governance",
        description=f"Environment: {env}. Review shared tables and approve a complete release.",
        children=[coverage_notice, run_select, additions, fields, agreement, details, review_button, confirm,
                  shared.action_row(widgets, [activate]), status])
    state.update(widget=root, refresh=refresh, review_release=review_release, perform_activation=perform_activation)
    with startup.phase("metadata_loading", "Loading activation state…"):
        refresh()
    startup.display(root)
    return state
