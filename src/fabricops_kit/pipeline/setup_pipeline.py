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
        "freshness": "Read", "source_drift": "Historical definition only; setup_pipeline controls Source Drift",
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
              "source_drift": "Historical Source Drift (pipeline-owned)", "sensitive_data": "Sensitive Data"}
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


def setup_pipeline(*, pipeline_mode: str = "Ungoverned",
                   profiling_enabled: bool = True, profiling_interval_days: int = 1,
                   profiling_max_rows: int | None = None, grain_discovery_enabled: bool = False,
                   frequency_enabled: bool = False, source_drift_enabled: bool = False,
                   source_drift_interval_days: int = 1, source_drift_block: bool = True):
    """Start a pipeline using the current Fabric notebook identity and one execution mode.

    Dry Run previews transformations, optional Contract checks and profiling without
    durable mutations. Ungoverned publishes without activated Contracts, but cannot
    write protected Table IDs or physical destination aliases. Governed requires
    a promoted notebook and independently activated Contracts for all sources
    and targets. It remains fail closed pending signed-in Fabric validation.

    Parameters
    ----------
    pipeline_mode : {"Dry Run", "Ungoverned", "Governed"}, default="Ungoverned"
        Preview, publish without governance, or enforce activated governance.

    profiling_enabled : bool, default=True
        Enable Standard profiling independently of Grain discovery and Frequency.
    profiling_interval_days : int, default=1
        Positive integer interval since the latest confirmed physical-table
        Standard completion with sufficient scope, shared across pipelines.
        Full-table requests ignore bounded completions; bounded requests may reuse
        full completions or completions with an equal or larger requested bound.
    profiling_max_rows : int or None, default=None
        None profiles the complete physical table (the prepared DataFrame for
        Dry Run Writes). A positive integer bounds each
        enabled activity using an arbitrary row selection; statistics describe only
        that selection. This does not guarantee a physical read of only that many
        rows. Saved results carry their scope. Guardrails and Source Observation
        always use their own required input, independently of this limit.
    grain_discovery_enabled : bool, default=False
        Discover candidate Grain keys once per physical table and sufficient scope.
        Does not control mandatory Grain Guardrails.
    frequency_enabled : bool, default=False
        Profile value frequencies once per physical table and sufficient scope.

    source_drift_enabled : bool, default=False
        Observe complete physical sources automatically during Read, independently
        of profiling limits and incremental checkpoints. Read every source before
        any Write; the first Write closes the participating Read set.
    source_drift_interval_days : int, default=1
        Positive interval since the latest confirmed successful acceptance for the
        physical source, shared across pipelines. Failed or incomplete runs and
        nonpublishing Writes do not advance observation history.
    source_drift_block : bool, default=True
        Block publication on confirmed additions, removals, modifications, schema
        changes or unavailable observations. False permits warnings; new baselines
        still require successful finalization and verified required publications.
        The first exact snapshot does not invent historical changes.

    Returns
    -------
    PipelineSession
        Context-local Read/Write execution and in-memory report. Call
        finalize_pipeline after every Read, transformation and Write completes.

    Notes
    -----
    Call setup_notebook first. Spark and Fabric identity come from that setup.
    The current Fabric Notebook ID establishes the logical Pipeline ID. The
    Pipeline Registry maps promoted physical notebook IDs back to the original
    identity; no identity is declared in notebook source. Repeated setup closes
    the previous execution. Dry Run never writes Registry, Run,
    profiling results or Processing State. Completed captured Dry Runs retain
    serializable saved-definition/test claims in Engineering Files for submission.
    Finalize displays the package download and explicit deployment/recovery controls.
    Governed setup validates the active deployed notebook and approved executable
    code/configuration; outputs, counts and Markdown may change. Setup never
    deploys, freezes an edited source, or repairs a notebook automatically.
    Persistent runs record final outcomes;
    a successful Write does not imply successful whole-notebook completion.

    Raises
    ------
    ValueError
        If the mode, Source Drift or profiling configuration is invalid.
    RuntimeError
        If notebook setup or Spark is unavailable, or signed-in Fabric validation
        remains pending. Governed fails before admission and publication.

    Examples
    --------
    >>> context = setup_notebook()
    >>> pipeline = setup_pipeline(pipeline_mode="Ungoverned")
    >>> preview = setup_pipeline(pipeline_mode="Dry Run")

    """
    from fabricops_kit.pipeline.shared import start_pipeline_session

    if pipeline_mode not in {"Dry Run", "Ungoverned", "Governed"}:
        raise ValueError("pipeline_mode must be exactly Dry Run, Ungoverned or Governed.")
    profiling = {
        "profiling_enabled": profiling_enabled, "profiling_interval_days": profiling_interval_days,
        "profiling_max_rows": profiling_max_rows, "grain_discovery_enabled": grain_discovery_enabled,
        "frequency_enabled": frequency_enabled,
    }
    from fabricops_kit.pipeline.shared import validate_pipeline_profiling, validate_source_drift_configuration

    profiling = validate_pipeline_profiling(profiling)
    policy = validate_source_drift_configuration({"source_drift_enabled": source_drift_enabled,
        "source_drift_interval_days": source_drift_interval_days, "source_drift_block": source_drift_block})
    session = start_pipeline_session(pipeline_mode, inspector=_inspector)
    if pipeline_mode == "Governed" and session.plan.evidence.get("approved_parameters") != {**policy, **profiling}:
        session.close(failed=True)
        raise RuntimeError("Governed parameter overrides differ from the frozen notebook; Dry Run and promote a new version.")
    session.plan.evidence["pipeline_parameters"] = {**policy, **profiling}
    session.plan.evidence["profiling_configuration"] = profiling
    session.plan.evidence["source_drift_policy"] = policy
    return session
