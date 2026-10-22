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


def setup_pipeline(*, sources, targets, execution_mode="testing", selections=None, interactive=None,
                   spark_session=None, context=None, pipeline_id=None, configuration=None, testing_writes=False):
    """Prepare Author → Test → Activate → Live execution without running guardrails.

    Testing is interactive by default. Set interactive=False for automation and
    provide exact contract_id/contract_version choices keyed by global table_id,
    or omit selections for contract-free exploration. Select every participant's
    frozen contract or No Contract for all; partial governance is rejected.
    Stable pipeline_id is required and independent of notebook name or path.

    testing_writes=True explicitly permits real Testing writes to the declared
    target destinations, provided no Live pipeline owns them. Such writes have
    real side effects, including target metadata, mappings and checkpoints.
    False evaluates without publication. Guardrail diagnostics and run records
    always persist to the central configured Metadata store.

    Live is headless and resolves the environment's approved configuration
    automatically. It rejects manual contract choices and pins one activation
    revision. Transformation configuration, table
    identity, destinations and ownership must match approval. Operational
    differences allowed by the orchestrators warn and persist in the run record.

    Returns an immutable PipelineExecutionPlan, or Testing widget state with
    select_contract, build_plan and refresh. Call finalize_pipeline(plan) after all
    Reads, transformations and Writes, including read-only pipelines. Stopped runs
    remain incomplete. Reuse the setup context without repeating configuration.
    Engineering and Microsoft Fabric own code integrity, source control, CI/CD
    and deployment. No executable export or checksum is required.

    Raises ValueError for unsafe configuration or partial contract selection,
    RuntimeError for metadata failures, stale authority or a reused run boundary.
    Approval neither deploys notebooks nor writes business data.

    Examples
    --------
    >>> plan = setup_pipeline(sources=SOURCES, targets=TARGETS, pipeline_id="hr-employees",
    ...     interactive=False, selections=SELECTIONS, configuration={})
    >>> source = orchestrate_read(execution_plan=plan, **READ_CONFIG)
    >>> transformed = transform(source["dataframe"])
    >>> result = orchestrate_write(transformed, execution_plan=plan, sources=[source], **WRITE_CONFIG)
    >>> pipeline_result = finalize_pipeline(plan)

    """
    if not str(pipeline_id or "").strip():
        raise ValueError("setup_pipeline requires a stable pipeline_id.")
    if execution_mode not in {"testing", "live"}:
        raise ValueError("execution_mode must be testing or live.")
    if interactive is None:
        interactive = execution_mode == "testing"
    if execution_mode == "live":
        if selections is not None:
            raise ValueError("Live rejects manual contract selections; contracts come exclusively from the Activated Pipeline manifest.")
        if interactive or testing_writes:
            raise ValueError("Live is headless; Testing write authorization is not a Live option.")
        from fabricops_kit.activated_pipeline.shared import build_live_pipeline_plan
        return build_live_pipeline_plan(pipeline_id=pipeline_id, sources=list(sources), targets=list(targets),
            configuration=configuration, context=context, spark_session=spark_session)
    if not interactive:
        mode = execution_mode
        return build_pipeline_execution_plan(
            execution_mode=mode, sources=sources, targets=targets,
            selections=selections, context=context, spark_session=spark_session,
            pipeline_id=pipeline_id, configuration=configuration, testing_writes=testing_writes,
        )
    if execution_mode is not None and execution_mode != "testing":
        raise ValueError("Interactive contract selection is only available for Testing.")
    config, env, resolved = resolve_fabric_context(context=context)
    runtime = {**resolved, "config": config, "env": env}
    if not str(runtime.get("notebook_id") or "").strip():
        raise ValueError("Configure notebook_id before selecting Pipeline Data Contracts.")
    spark = get_spark_session(spark_session)
    sources, targets = list(sources), list(targets)
    identities = resolve_pipeline_participants(
        config, env, sources=sources, targets=targets, context=runtime, spark_session=spark,
    )
    try:
        rows = [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
                for row in read_lakehouse_table("METADATA_DATA_CONTRACT", store="Metadata",
                    schema=metadata_table_physical_schema(config, "METADATA_DATA_CONTRACT"),
                    spark_session=spark, context=runtime).collect()]
    except Exception as exc:
        if is_table_not_found_error(exc):
            raise RuntimeError("Initialize METADATA_DATA_CONTRACT in the configured metadata store before selection.") from exc
        raise
    state: dict[str, Any] = {"execution_mode": "testing", "environment": env, "tables": {}, "_controls": {}}
    for table_id, identity in identities.items():
        matching = [row for row in rows if row.get("table_id") == table_id]
        versions = sorted([row for row in matching if str(row.get("status") or "").lower() == "frozen"],
                          key=lambda row: int(row["contract_version"]), reverse=True)
        keys = [(row["contract_id"], row["contract_version"]) for row in versions]
        if len(keys) != len(set(keys)):
            raise RuntimeError("Duplicate frozen contract version rows.")
        for row in versions:
            _contract_review(row, identity["roles"])
        state["tables"][table_id] = {"identity": identity, "versions": versions,
                                    "selected": None, "choice": None, "review": None}

    def require_unbuilt_plan():
        if state.get("execution_plan") is not None:
            raise RuntimeError("Cannot change selection during an active execution plan; create a new widget for a new run.")

    def select_contract(table_id, contract_id=None, contract_version=None, *, no_contract=False):
        require_unbuilt_plan()
        if table_id not in state["tables"]:
            raise ValueError("Only configured pipeline participants may select contracts.")
        table = state["tables"][table_id]
        if no_contract:
            if contract_id is not None or contract_version is not None:
                raise ValueError("No Contract cannot be combined with a contract identity.")
            selected, choice = None, {"no_contract": True}
        else:
            matches = [row for row in table["versions"] if row["contract_id"] == contract_id and row["contract_version"] == contract_version]
            if len(matches) != 1:
                raise ValueError("Select an available exact frozen version.")
            selected = matches[0]
            choice = {"contract_id": contract_id, "contract_version": contract_version}
        table.update(selected=selected, choice=choice,
                     review=_contract_review(selected, table["identity"]["roles"]) if selected else None)
        refresh()
        return state

    def set_mode(mode):
        require_unbuilt_plan()
        if mode != "testing":
            raise ValueError("Contract selection supports Testing only; use saved Activated Pipeline selection for Live.")
        state["execution_mode"] = mode
        refresh()
        return state

    def build_plan():
        if state.get("execution_plan") is None and not state.get("writes_confirmed", False):
            if testing_writes:
                raise ValueError("Confirm real Testing writes and their destinations before building the plan.")
        if state.get("execution_plan") is not None:
            return state["execution_plan"]
        plan = build_pipeline_execution_plan(
            execution_mode=state["execution_mode"], sources=sources, targets=targets,
            selections={key: table["choice"] for key, table in state["tables"].items() if table["choice"] is not None},
            context=runtime, spark_session=spark,
            pipeline_id=pipeline_id, configuration=configuration, testing_writes=testing_writes,
        )

        state["execution_plan"] = plan
        refresh()
        return plan

    state.update(select_contract=select_contract, set_mode=set_mode, build_plan=build_plan)
    root = header = mode_control = None
    refreshing = False

    def refresh():
        nonlocal refreshing
        if root is None or refreshing:
            return
        refreshing = True
        try:
            root.add_class("pipeline-testing")
            mode_control.disabled = state.get("execution_plan") is not None
            write_authorized.disabled = not testing_writes or state.get("execution_plan") is not None
            mode_control.value = state["execution_mode"]
            header.value = '<h3>Pipeline Data Contracts · Testing</h3><p>Choose contract mappings and explicitly authorize any real Testing writes. Run records and Guardrail diagnostics persist.</p>'
            for table_id, controls in state["_controls"].items():
                table = state["tables"][table_id]
                versions = table["versions"]
                options = [("Choose explicitly…", ""), ("No Contract", "none")]
                options += [(f'{row.get("contract_name") or row["contract_id"]} · v{row["contract_version"]} · Frozen'
                             ,
                             f'{row["contract_id"]}\n{row["contract_version"]}') for row in versions]
                controls["version"].disabled = state.get("execution_plan") is not None
                controls["version"].options = options
                selected = table["selected"]
                controls["version"].value = (f'{selected["contract_id"]}\n{selected["contract_version"]}' if selected else
                                             ("none" if table["choice"] else ""))
                controls["inspector"].value = (_inspector(selected, table["identity"]["roles"],
                    state["execution_plan"].results if state.get("execution_plan") else ()) if selected else
                                                ("<p>Explicit No Contract: no saved Guardrails selected.</p>" if table["choice"] else "<p>Select a frozen contract to inspect its saved definitions.</p>"))
        finally:
            refreshing = False

    state["refresh"] = refresh
    if execution_mode is not None:
        set_mode(execution_mode)
    if selections is not None:
        if set(selections) != set(identities):
            raise ValueError("Supply an explicit choice for every participating table only.")
        for table_id, choice in selections.items():
            if not isinstance(choice, dict) or set(choice) not in ({"no_contract"}, {"contract_id", "contract_version"}):
                raise ValueError("Select exact contract_id/contract_version or explicit no_contract=True.")
            if "no_contract" in choice and choice["no_contract"] is not True:
                raise ValueError("No Contract must explicitly be True.")
            select_contract(table_id, **choice)
    try:
        from fabricops_kit.widgets.shared import form_page, form_section, require_ipywidgets

        widgets = require_ipywidgets()
        from IPython import display as ip
    except ModuleNotFoundError:
        return state
    destinations = [item for item in identities.values() if "target" in item["roles"]]
    write_authorized = widgets.Checkbox(value=False, indent=False,
        description="I authorize real Testing writes to the displayed destinations", disabled=not testing_writes)
    write_authorized.observe(lambda change: state.update(writes_confirmed=change["new"]), names="value")
    state["write_authorized"] = write_authorized
    style = widgets.HTML('''<style>
.pipeline-contracts { --mode:#0f6cbd; }
.pipeline-testing { --mode:#6750a4; }
.pipeline-contracts h3 { font-size:15px; color:var(--mode); margin:0; }
.pipeline-contracts .inactive { background:#f2f5f8; color:#526477; }
.pipeline-contracts .contract-scroll { overflow-x:auto; }
</style>''')
    header = widgets.HTML()
    mode_control = widgets.ToggleButtons(options=[("Testing", "testing")], value="testing", description="Pipeline mode")
    mode_control.observe(lambda change: set_mode(change["new"]) if not refreshing else None, names="value")
    sections = []
    for table_id, table in state["tables"].items():
        identity = table["identity"]
        label = " / ".join(str(identity.get(key)) for key in ("store", "schema", "table_name") if identity.get(key))
        roles = " / ".join("Read" if role == "source" else "Write" for role in identity["roles"])
        title = widgets.HTML(f'<small>{html.escape(table_id)}</small>')
        version = widgets.Dropdown(description="Contract", layout=widgets.Layout(width="100%"), style={"description_width": "70px"})
        inspector = widgets.HTML()
        def changed(change, key=table_id):
            if refreshing:
                return
            require_unbuilt_plan()
            if not change["new"]:
                state["tables"][key].update(selected=None, choice=None, review=None)
                refresh()
                return
            if change["new"] == "none":
                select_contract(key, no_contract=True)
            else:
                contract_id, version_number = change["new"].split("\n")
                select_contract(key, contract_id, int(version_number))
        version.observe(changed, names="value")
        state["_controls"][table_id] = {"version": version, "inspector": inspector}
        sections.append(form_section(widgets, title=f"{roles} · {label}", children=[title, version, inspector]))
    root = form_page(
        widgets, title="Pipeline setup", tone="engineering",
        description="Select exact frozen Data Contract versions for Testing.",
        children=[style, header, mode_control,
                  widgets.HTML("<p>Testing writes: " + ("REAL writes with side effects" if testing_writes else "Evaluation only") + "</p><pre>" + html.escape(json.dumps(destinations, indent=2)) + "</pre>"),
                  write_authorized, *sections],
    )
    root.add_class("pipeline-contracts")
    state["widget"], state["mode_control"] = root, mode_control
    refresh()
    ip.display(root)
    return state
