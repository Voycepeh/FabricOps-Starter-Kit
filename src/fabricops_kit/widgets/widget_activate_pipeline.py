"""Governance review and confirmation for an exact tested whole pipeline."""
from __future__ import annotations
import html
import json
from typing import Any

from fabricops_kit.activated_pipeline.shared import metadata_records, manifest_digest
from fabricops_kit.activated_pipeline.activate_pipeline import activate_pipeline
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.widgets import shared


def _eligible_candidate(row, pipeline_id):
    """Filter corrupt, partial and contract-free snapshots before Governance review."""
    try:
        if row.get("execution_mode") != "testing" or row.get("status") != "succeeded" or not row.get("completed_at"):
            return False
        if pipeline_id is not None and row.get("pipeline_id") != pipeline_id:
            return False
        candidate = json.loads(row["candidate_json"])
        summary = json.loads(row["operation_summary_json"])
        return bool(summary["frozen_contracts"] and all(item["contract"] for item in summary["frozen_contracts"])
                    and summary["operations"] and not summary.get("failures")
                    and all(item.get("status") == "succeeded" and isinstance(item.get("configuration"), dict)
                            for item in summary["operations"].values())
                    and manifest_digest(candidate) == row["candidate_fingerprint"])
    except (ValueError, KeyError, TypeError):
        return False


def widget_activate_pipeline(*, pipeline_id=None, executable_path=None, spark_session=None, context=None) -> dict[str, Any]:
    """Review complete persisted Testing candidates and activate an exact pipeline.

    Shows complete successful candidates with their contracts/rules, operation
    configuration, executable/dependency identity, linked diagnostics, warnings,
    Agreement and fingerprint. The underlying activation service independently
    revalidates all requirements. Opening this widget never activates, deploys or
    publishes. Governance must review and explicitly confirm before activation.

    Returns widget controls, eligible runs, refresh and perform_activation actions.
    Invalid or changed evidence fails closed and is shown in the status output.
    """
    from IPython import display as ip
    import ipywidgets as widgets
    _config, _env, _runtime = resolve_fabric_context(context=context)
    runs = metadata_records("METADATA_PIPELINE_RUN", context=context, spark_session=spark_session)
    eligible = [row for row in runs if _eligible_candidate(row, pipeline_id)]
    agreements = metadata_records("METADATA_DATA_AGREEMENT", context=context, spark_session=spark_session)
    layout = widgets.Layout(width="100%", max_width="900px")
    run_select = widgets.Dropdown(description="Testing run", options=[(f"{row['pipeline_id']} · {row['run_id']}", row["run_id"]) for row in eligible], layout=layout)
    agreement_select = widgets.Dropdown(description="Agreement", options=[(f"{row.get('agreement_name', row['agreement_id'])} · {row['agreement_version']}", (row["agreement_id"],row["agreement_version"])) for row in agreements], layout=layout)
    name = widgets.Text(description="Name", value=pipeline_id or "", layout=layout)
    version = widgets.Text(description="Version", layout=layout)
    executable = widgets.Text(description="Executable", value=executable_path or "", layout=layout)
    expected = widgets.Text(description="Switch from", placeholder="Current active version ID; empty for initial activation", layout=layout)
    details = widgets.HTML()
    reviewed = widgets.Checkbox(description="I reviewed the whole pipeline, exact Agreement, evidence and warnings", value=False, indent=False)
    confirm = widgets.Checkbox(description="I confirm Governance approval of this exact pipeline version", value=False, indent=False)
    action = widgets.Button(description="Activate pipeline", button_style="primary", disabled=True, icon="check")
    status = shared.status_message(widgets)
    state = {"eligible_runs": eligible, "run_select": run_select, "agreement_select": agreement_select,
             "pipeline_name": name, "pipeline_version": version, "executable": executable,
             "expected_active_id": expected, "reviewed": reviewed, "confirmed": confirm,
             "activate": action, "details": details, "activation_result": None}

    def refresh(*_):
        selected = next((row for row in eligible if row["run_id"] == run_select.value), None)
        state["selected_run"] = selected
        if selected is None:
            details.value = "<p>No complete successful Testing candidates. Run and finalize the whole pipeline first.</p>"
            action.disabled = True
            return
        candidate = json.loads(selected["candidate_json"])
        sections = [("Candidate fingerprint", selected["candidate_fingerprint"]),
                    ("Code, configuration and dependencies", candidate),
                    ("Complete operation evidence", json.loads(selected["operation_summary_json"])),
                    ("Exact frozen contracts and rules", [item for item in metadata_records("METADATA_DATA_CONTRACT", context=context, spark_session=spark_session)
                        if item.get("environment_name") == selected["environment_name"] and any(ref["contract"] and item["contract_id"] == ref["contract"]["contract_id"] and item["contract_version"] == ref["contract"]["contract_version"]
                               for ref in json.loads(selected["operation_summary_json"])["frozen_contracts"])]),
                    ("Guardrail evidence", [item for item in metadata_records("METADATA_GUARDRAIL_RESULTS", context=context, spark_session=spark_session) if item.get("run_id") == selected["run_id"]]),
                    ("Warnings", ["Testing does not verify deployment permissions, target transactions or concurrent business writes."]),
                    ("Exact Agreement", next((row for row in agreements if agreement_select.value == (row["agreement_id"],row["agreement_version"])), None))]
        details.value = "".join(f"<details><summary>{html.escape(title)}</summary><pre>{html.escape(json.dumps(value, indent=2, default=str))}</pre></details>" for title,value in sections)
        action.disabled = not (reviewed.value and confirm.value and agreement_select.value and version.value.strip() and name.value.strip() and executable.value.strip())

    def changed(_):
        reviewed.value = False
        confirm.value = False
        refresh()

    def perform_activation(_=None):
        if action.disabled:
            raise ValueError("Review and explicit Governance confirmation are required.")
        selected = state["selected_run"]
        agreement_id, agreement_version = agreement_select.value
        result = activate_pipeline(testing_run_id=selected["run_id"], candidate_fingerprint=selected["candidate_fingerprint"],
            pipeline_name=name.value, pipeline_version=version.value, agreement_id=agreement_id, agreement_version=agreement_version,
            executable_path=executable.value, governance_confirmed=reviewed.value and confirm.value,
            expected_active_id=expected.value.strip() or None, spark_session=spark_session, context=context)
        state["activation_result"] = result
        action.disabled = True
        status.value = "<p>Pipeline activated. Deployment and Live selection are separate actions.</p>"
        return result

    def click(button):
        try:
            perform_activation(button)
        except Exception as exc:
            status.value = f"<p>{html.escape(str(exc))}</p>"
    for control in (run_select, agreement_select, name, version, executable, expected):
        control.observe(changed, names="value")
    for control in (reviewed, confirm):
        control.observe(refresh, names="value")
    action.on_click(click)
    root = shared.form_page(widgets, title="Activate a tested pipeline", tone="governance",
        description="Review complete persisted Testing before explicit Governance confirmation.",
        children=[run_select, name, version, executable, agreement_select, expected,
                  details, reviewed, confirm, shared.action_row(widgets, [action]), status])
    root.add_class("fabricops-form")
    state.update(widget=root, refresh=refresh, perform_activation=perform_activation)
    refresh()
    ip.display(root)
    return state
