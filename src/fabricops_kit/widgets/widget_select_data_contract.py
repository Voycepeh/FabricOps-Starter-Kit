"""Compact pipeline-wide execution selection and immutable contract inspection."""

from __future__ import annotations

import html
import json
from typing import Any

from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
from fabricops_kit.config.shared import is_table_not_found_error, resolve_fabric_context
from fabricops_kit.io import read_lakehouse_table
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.pipeline.create_pipeline_execution_plan import create_pipeline_execution_plan
from fabricops_kit.pipeline.shared import resolve_catalogue_table_identity, resolve_physical_table_identity
from fabricops_kit.widgets.shared import parse_data_contract_payload, require_ipywidgets


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


def widget_select_data_contract(*, sources, targets, spark_session=None, context=None):
    """Select one pipeline mode and independently inspect each participant's contract.

    Parameters
    ----------
    sources : list of dict
        Explicit source participants: store/schema/table_name or registered table_id.
        Historical Lineage is optional and cannot introduce additional participants.
    targets : list of dict
        Explicit target participants with the same coordinate or table_id shape.
    spark_session : object, optional
        Spark session for metadata reads.
    context : dict, optional
        Configured environment routing and notebook identity.

    Returns
    -------
    dict
        Interactive state with execution_mode (initially testing), tables, controls,
        select_contract, set_mode, build_plan and refresh. Each table starts unselected.
        After executing the built plan, refresh shows its exact-version results
        in expandable sections alongside saved definitions and disabled states.
        Explicitly select No Contract for bootstrap; build_plan validates every
        choice and freezes the plan to pass to all Read and Write calls.
        UI edits after build_plan require a new plan and a new run of Read/Transform/Write.
        The widget never changes notebook globals, edits or activates contracts.

    Raises
    ------
    ValueError
        For missing notebook identity, invalid payloads, unavailable selections or
        Live choices bypassing an active contract.
    RuntimeError
        For ambiguous active versions or a metadata-read failure.

    Examples
    --------
    >>> selection = widget_select_data_contract(sources=PIPELINE_SOURCES, targets=PIPELINE_TARGETS)
    >>> plan = selection["build_plan"]()

    """
    config, env, resolved = resolve_fabric_context(context=context)
    runtime = {**resolved, "config": config, "env": env}
    if not str(runtime.get("notebook_id") or "").strip():
        raise ValueError("Configure notebook_id before selecting Pipeline Data Contracts.")
    spark = get_spark_session(spark_session)
    sources, targets = list(sources), list(targets)
    identities = {}
    for role, participants in (("source", sources), ("target", targets)):
        for participant in participants:
            identity = (resolve_physical_table_identity(config, env, **{
                key: participant[key] for key in ("store", "schema", "table_name")
            }) if "store" in participant else resolve_catalogue_table_identity(
                config, env, participant["table_id"], context=runtime, spark_session=spark,
            ))
            table_id = identity["table_id"]
            roles = identities.get(table_id, {}).get("roles", [])
            if role in roles:
                raise ValueError(f"Duplicate {role} participant {table_id!r}.")
            identities[table_id] = {**identity, "roles": [*roles, role]}
    if not identities:
        raise ValueError("Configure at least one actual source or target.")
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
        matching = [row for row in rows if row.get("table_id") == table_id and row.get("environment_name") == env]
        active = [row for row in matching if row.get("is_active") is True]
        if len(active) > 1:
            raise RuntimeError(f"Multiple active Data Contract versions for {table_id!r}.")
        if active and str(active[0].get("status") or "").lower() != "frozen":
            raise ValueError("Active Data Contract must be frozen.")
        versions = sorted([row for row in matching if str(row.get("status") or "").lower() == "frozen"],
                          key=lambda row: int(row["contract_version"]), reverse=True)
        keys = [(row["contract_id"], row["contract_version"]) for row in versions]
        if len(keys) != len(set(keys)):
            raise RuntimeError("Duplicate frozen contract version rows.")
        for row in versions:
            _contract_review(row, identity["roles"])
        state["tables"][table_id] = {"identity": identity, "versions": versions, "active": active[0] if active else None,
                                    "selected": None, "choice": None, "review": None}

    def select_contract(table_id, contract_id=None, contract_version=None, *, no_contract=False):
        if table_id not in state["tables"]:
            raise ValueError("Only configured pipeline participants may select contracts.")
        table = state["tables"][table_id]
        if no_contract:
            if contract_id is not None or contract_version is not None:
                raise ValueError("No Contract cannot be combined with a contract identity.")
            if table["active"]:
                raise ValueError("Live cannot bypass the active contract with No Contract.")
            selected, choice = None, {"no_contract": True}
        else:
            matches = [row for row in table["versions"] if row["contract_id"] == contract_id and row["contract_version"] == contract_version]
            if len(matches) != 1:
                raise ValueError("Select an available exact frozen version.")
            selected = matches[0]
            if state["execution_mode"] == "live" and selected is not table["active"]:
                raise ValueError("Live requires the active frozen version.")
            choice = {"contract_id": contract_id, "contract_version": contract_version}
        state.pop("execution_plan", None)
        table.update(selected=selected, choice=choice,
                     review=_contract_review(selected, table["identity"]["roles"]) if selected else None)
        refresh()
        return state

    def set_mode(mode):
        if mode not in {"testing", "live"}:
            raise ValueError("Mode must be testing or live.")
        state.pop("execution_plan", None)
        state["execution_mode"] = mode
        if mode == "live":
            for table in state["tables"].values():
                active = table["active"]
                # A visible mode change selects the only eligible Live version.
                if active:
                    table.update(selected=active, choice={"contract_id": active["contract_id"],
                                 "contract_version": active["contract_version"]},
                                 review=_contract_review(active, table["identity"]["roles"]))
                elif table["selected"]:
                    table.update(selected=None, choice=None, review=None)
        refresh()
        return state

    def build_plan():
        plan = create_pipeline_execution_plan(
            execution_mode=state["execution_mode"], sources=sources, targets=targets,
            selections={key: table["choice"] for key, table in state["tables"].items() if table["choice"] is not None},
            context=runtime, spark_session=spark,
        )

        state["execution_plan"] = plan
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
            testing = state["execution_mode"] == "testing"
            root.remove_class("pipeline-testing" if not testing else "pipeline-live")
            root.add_class("pipeline-testing" if testing else "pipeline-live")
            mode_control.value = state["execution_mode"]
            header.value = f'<h3>Pipeline Data Contracts · {"Testing" if testing else "Live"}</h3><p>' + (
                "No data or metadata persistence. Checks return diagnostics in memory." if testing else
                "Successful publication and operational metadata commits are permitted.") + '</p>'
            for table_id, controls in state["_controls"].items():
                table = state["tables"][table_id]
                active = table["active"]
                versions = table["versions"] if testing else ([active] if active else [])
                options = [("Choose explicitly…", ""), *([("No Contract", "none")] if not active else [])]
                options += [(f'{row.get("contract_name") or row["contract_id"]} · v{row["contract_version"]} · Frozen'
                             + (" · Active" if row.get("is_active") else ""),
                             f'{row["contract_id"]}\n{row["contract_version"]}') for row in versions]
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
    try:
        widgets = require_ipywidgets()
        from IPython import display as ip
    except ModuleNotFoundError:
        return state
    style = widgets.HTML('''<style>
.pipeline-contracts{max-width:1000px;padding:12px;border:2px solid var(--mode);border-radius:6px;color:#17212b;background:var(--surface)}
.pipeline-testing{--mode:#a21920;--surface:#fff5f5}.pipeline-live{--mode:#176536;--surface:#f1fbf4}
.pipeline-contracts h3{background:var(--mode);color:white;padding:9px;margin:0;border-radius:4px}
.pipeline-contracts summary{cursor:pointer;color:var(--mode);font-weight:600;padding:5px}
.pipeline-contracts table{border-collapse:collapse;width:100%;background:white;font-size:12px}
.pipeline-contracts th,.pipeline-contracts td{border:1px solid #bbc0c5;padding:5px;text-align:left;vertical-align:top;overflow-wrap:anywhere}
.pipeline-contracts .inactive{background:#eceff1;color:#454c53}
.pipeline-contracts .contract-scroll{overflow-x:auto}.pipeline-contracts pre{white-space:pre-wrap}
.pipeline-contracts .widget-toggle-buttons .mod-active{background:var(--mode);color:white}
</style>''')
    header = widgets.HTML()
    mode_control = widgets.ToggleButtons(options=[("Testing", "testing"), ("Live", "live")], value="testing", description="Pipeline mode")
    mode_control.observe(lambda change: set_mode(change["new"]) if not refreshing else None, names="value")
    sections = []
    for table_id, table in state["tables"].items():
        identity = table["identity"]
        label = " / ".join(str(identity.get(key)) for key in ("store", "schema", "table_name") if identity.get(key))
        roles = " / ".join("Read" if role == "source" else "Write" for role in identity["roles"])
        title = widgets.HTML(f'<h4>{html.escape(roles)} · {html.escape(label)}</h4><small>{html.escape(table_id)}</small>')
        version = widgets.Dropdown(description="Contract", layout=widgets.Layout(width="100%"), style={"description_width": "70px"})
        inspector = widgets.HTML()
        def changed(change, key=table_id):
            if refreshing:
                return
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
        sections.append(widgets.VBox([title, version, inspector]))
    root = widgets.VBox([style, header, mode_control, *sections])
    root.add_class("pipeline-contracts")
    state["widget"], state["mode_control"] = root, mode_control
    refresh()
    ip.display(root)
    return state
