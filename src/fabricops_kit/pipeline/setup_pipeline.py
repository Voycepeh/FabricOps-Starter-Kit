"""Set up interactive or scheduled pipeline execution with one immutable plan."""

from __future__ import annotations

import html
import json
from typing import Any

from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
from fabricops_kit.config.shared import is_table_not_found_error, resolve_fabric_context
from fabricops_kit.io import read_lakehouse_table
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.shared import build_pipeline_execution_plan, resolve_pipeline_participants


def _value(value):
    if value is None:
        return "Not stored"
    if isinstance(value, dict):
        return "<br>".join(f"<b>{html.escape(str(key))}</b>: {_value(item)}" for key, item in value.items()) or "{}"
    if isinstance(value, list):
        return "[" + ", ".join(_value(item) for item in value) + "]"
    return html.escape(str(value))


def _table(rows, columns):
    if not rows:
        return "<p>No saved definitions.</p>"
    headings = "".join(f"<th>{html.escape(label)}</th>" for _key, label in columns)
    body = ""
    for row in rows:
        cells = "".join(f"<td>{_value(row.get(key))}</td>" for key, _label in columns)
        if row.get("is_active") is False:
            cells = cells.replace("<td>", "<td><span>Inactive · </span>", 1)
        body += f'<tr class="{"inactive" if row.get("is_active") is False else "active"}">{cells}</tr>'
    return f'<div class="contract-scroll"><table><thead><tr>{headings}</tr></thead><tbody>{body}</tbody></table></div>'


def _applicability(kind, roles):
    boundaries = {
        "schema": "Read and Write", "grain": "Read and Write", "data_quality": "Read and Write",
        "freshness": "Read", "source_drift": "Write (source/target relationship; Read captures observation)",
        "sensitive_data": "Write",
    }
    boundary = boundaries.get(kind, "Unsupported by current evaluator; retained for review")
    applicable = (kind in {"schema", "grain", "data_quality"}
                  or (kind in {"freshness", "source_drift"} and "source" in roles)
                  or (kind == "sensitive_data" and "target" in roles))
    return boundary + ("" if applicable else " · Will not run at this participant's boundary")


def _contract_review(row, roles=("source", "target")):
    """Return every saved column and rule, without runtime defaults or filtering."""
    from fabricops_kit.widgets.shared import parse_data_contract_payload

    payload = parse_data_contract_payload(row)
    columns = payload["table"].get("columns")
    rules = payload.get("guardrails")
    if not isinstance(columns, list) or not isinstance(rules, list):
        raise ValueError("Selected frozen payload requires table.columns and guardrails lists.")
    names = {column.get("column_id"): column.get("column_name") for column in columns}
    groups = {kind: [] for kind in ("schema", "grain", "data_quality", "freshness", "source_drift", "sensitive_data")}
    for rule in rules:
        if not isinstance(rule, dict):
            raise ValueError("Invalid saved Guardrail definition.")
        kind = str(rule.get("guardrail_type") or "unspecified")
        params = rule.get("rule_parameters")
        groups.setdefault(kind, []).append({
            **rule,
            "column": names.get(rule.get("column_id"), rule.get("column_id")),
            "parameters": params,
            "classification": [entry.get("value") for entry in
                (payload.get("enrichment") or {}).get("columns", [])
                if entry.get("column_id") == rule.get("column_id") and entry.get("enrichment_type") == "Classification"],
            "applicability": _applicability(kind, roles),
            "other": {key: value for key, value in rule.items() if key not in {
                "guardrail_type", "rule_type", "column_id", "rule_parameters", "is_active", "action",
            }},
        })
    return {"payload": payload, "columns": columns, "categories": groups,
            "counts": {key: len(value) for key, value in groups.items()}}


def _inspector(row, roles, results=()):
    review = _contract_review(row, roles)
    labels = {"schema": "Schema", "grain": "Grain", "data_quality": "Data Quality", "freshness": "Freshness",
              "source_drift": "Source Drift", "sensitive_data": "Sensitive Data"}
    sections = []
    for kind, rules in review["categories"].items():
        content = ""
        if kind == "schema":
            columns = [{**column, "constraints": {key: value for key, value in column.items() if key not in {
                "column_id", "column_name", "data_type", "precision", "scale", "is_nullable", "nullable", "is_active",
            }}} for column in review["columns"]]
            for column in columns:
                column["required_rules"] = [
                    {"required": column.get("column_id") in rule["parameters"]["required_columns"]
                                 or column.get("column_name") in rule["parameters"]["required_columns"],
                     "active": rule.get("is_active"), "action": rule.get("action")}
                    for rule in rules if isinstance(rule.get("parameters"), dict)
                    and "required_columns" in rule["parameters"]
                ]
            # Exact authored keys are retained. No implied nullable/action/active defaults.
            content += f'<p>{len(columns)} saved columns. Rule action and state are shown separately below.</p>'
            content += _table(columns, [("column_name", "Column"), ("data_type", "Exact type"),
                                      ("precision", "Precision"), ("scale", "Scale"),
                                      ("is_nullable", "is_nullable"), ("nullable", "nullable"),
                                      ("is_active", "Active"), ("required_rules", "Required by saved Schema rules (state/action)"), ("constraints", "Other saved column fields")])
        content += _table(rules, [("column", "Column"), ("rule_type", "Rule"),
                                  ("parameters", "Saved condition, thresholds and parameters"),
                                  ("classification", "Saved classification"),
                                  ("action", "Action"), ("is_active", "Active"),
                                  ("applicability", "Boundary"), ("other", "Other saved fields")])
        title = labels.get(kind, f"Other / {kind}")
        inactive = sum(rule.get("is_active") is False for rule in rules)
        sections.append(f'<details><summary>{html.escape(title)} · {len(rules)} checks · {inactive} inactive</summary>{content}</details>')
    sections.append("<details><summary>Processing and ownership</summary>" + _value({key: review["payload"]["table"][key] for key in ("processing", "writer") if key in review["payload"]["table"]}) + "</details>")
    actual = [result for result in results if result.get("contract_id") == row.get("contract_id")
              and result.get("contract_version") == row.get("contract_version")
              and result.get("table_id") == row.get("table_id")]
    sections.append("<details><summary>Execution results · " + str(len(actual)) + "</summary>" +
                    (_table(actual, [("guardrail_type", "Guardrail"), ("guardrail_rule_id", "Rule"),
                                     ("execution_type", "Mode"), ("status", "Result"), ("can_continue", "Can continue"),
                                     ("result_payload_json", "Evaluation details")]) if actual else
                     "<p>Not executed in this plan. Saved definitions are configuration only.</p>") + "</details>")
    raw = html.escape(json.dumps(review["payload"], indent=2, ensure_ascii=False))
    return "".join(sections) + f'<details><summary>Raw frozen definition</summary><pre>{raw}</pre></details>'


def setup_pipeline(
    *, pipeline_id: str | None = None, pipeline_mode: str = "Ungoverned",
    new_pipeline: bool = False, previous_workspace_id: str | None = None,
    previous_notebook_id: str | None = None,
):
    """Start an isolated pipeline in Dry Run, Ungoverned or Governed mode.

    Dry Run evaluates real reads, transformations, profiling and optionally
    selected contract Guardrails without persisting target data or operational
    state. Ungoverned executes without Data Contracts while retaining operational
    checks and blocks writes to tables already governed in the workspace.
    Governed resolves only activated workspace authority and enforces its exact
    contract versions, destinations and ownership throughout the run.
    Spark and supported Fabric runtime identity are resolved internally. The caller workspace and notebook IDs are required for registration.

    Parameters
    ----------
    pipeline_id : str | None, optional
        Permanent UUIDv4. Omit to recover the exact notebook binding or register
        a new UUID in Ungoverned mode. Dry Run may use a session-only UUID and
        never registers it. Governed never allocates a new UUID.
        A changed same-workspace_id binding requires both previous notebook IDs.
    pipeline_mode : {"Dry Run", "Ungoverned", "Governed"}, default="Ungoverned"
        Preview without writing, execute without contracts, or execute with
        activated contracts enforced.
    new_pipeline : bool, default=False
        Explicitly create a new identity for an independent notebook copy. Omit
        pipeline_id when set. An already registered notebook is rejected.
    previous_workspace_id, previous_notebook_id : str | None, optional
        Supply both old binding IDs to explicitly rebind a reuploaded notebook.
        Rebinding requires Ungoverned mode and no active Governed runs.

    Returns
    -------
    PipelineSession
        Contract selection, pipeline_id containing the permanent UUID, registration
        details and the automatically refreshed execution report. Read and
        Write calls use this execution through a context-local binding.

    Notes
    -----
    Call setup_notebook() first to initialize configuration and display notebook
    readiness. This function reuses that configuration without rerunning
    00_env_config or displaying the workspace_id summary. Cross-workspace
    configuration is selected only through setup_notebook(config_workspace_id=...).
    Repeated pipeline setup closes the preceding execution owned by this task.
    Repeated notebook setup closes its pipeline and invalidates prior configuration,
    including when the new setup fails. Changed runtime identity requires fresh
    notebook setup.

    Fabric cell events identify failures, not successful notebook completion.
    Call finalize_pipeline after all Reads, transformations and Writes.
    Neither a successful Write nor interpreter shutdown proves completion. Dry
    Run finalization returns only a session summary and does not persist it.

    Raises
    ------
    ValueError
        For an invalid UUIDv4, conflicting notebook binding, unsupported mode or
        missing Governed activation.
    RuntimeError
        If setup_notebook() has not completed successfully for the current
        execution, or a Spark session is unavailable.

    Examples
    --------
    >>> context = setup_notebook()
    >>> pipeline = setup_pipeline(pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", pipeline_mode="Ungoverned")
    >>> orders = orchestrate_read(store="Bronze", schema="demo", table_name="orders")
    >>> independent_copy = setup_pipeline(pipeline_mode="Ungoverned", new_pipeline=True)
    >>> reuploaded = setup_pipeline(pipeline_id=PIPELINE_ID, pipeline_mode="Ungoverned",
    ...     previous_workspace_id=old_workspace_id, previous_notebook_id=old_notebook_id)

    """
    from fabricops_kit.pipeline.shared import start_pipeline_session

    if pipeline_id is not None:
        from fabricops_kit.pipeline.shared import validate_pipeline_id
        pipeline_id = validate_pipeline_id(pipeline_id)
    if pipeline_mode not in {"Dry Run", "Ungoverned", "Governed"}:
        raise ValueError("pipeline_mode must be exactly Dry Run, Ungoverned or Governed.")
    if not isinstance(new_pipeline, bool) or (new_pipeline and pipeline_id is not None):
        raise ValueError("new_pipeline=True requires an omitted pipeline_id.")
    if (previous_workspace_id is None) != (previous_notebook_id is None):
        raise ValueError("Supply both previous_workspace_id and previous_notebook_id for rebinding.")
    if previous_workspace_id is not None and (pipeline_id is None or new_pipeline or pipeline_mode != "Ungoverned"):
        raise ValueError("Rebinding requires a saved pipeline_id and pipeline_mode='Ungoverned'.")
    return start_pipeline_session(
        pipeline_id, pipeline_mode,
        inspector=_inspector,
        new_pipeline=new_pipeline,
        previous_binding=(previous_workspace_id, previous_notebook_id) if previous_workspace_id is not None else None,
    )
