"""Public widget for manually selecting a table's Production Data Contract."""

from __future__ import annotations

import html
import json
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import configured_lakehouse_schema, get_spark_session, read_lakehouse_table_core, resolve_configured_lakehouse_table
from fabricops_kit.widgets.shared import action_row, form_page, form_section, require_ipywidgets, status_message, widget_common

CONTRACT_TABLE = "METADATA_DATA_CONTRACT"


def _row_dict(row: Any) -> dict[str, Any]:
    return row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)


def _payload(row: dict[str, Any]) -> dict[str, Any]:
    try:
        payload = json.loads(str(row.get("contract_payload_json") or ""))
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Selected contract_payload_json is invalid JSON.") from exc
    if not isinstance(payload, dict) or not isinstance(payload.get("contract"), dict) or not isinstance(payload.get("table"), dict):
        raise ValueError("Selected Data Contract payload must identify its contract and table.")
    if str(payload["contract"].get("contract_id") or "") != str(row.get("contract_id") or ""):
        raise ValueError("Selected Data Contract payload contract_id does not match its version row.")
    if int(payload["contract"].get("contract_version") or 0) != int(row.get("contract_version") or 0):
        raise ValueError("Selected Data Contract payload contract_version does not match its version row.")
    if str(payload["table"].get("table_id") or "") != str(row.get("table_id") or ""):
        raise ValueError("Selected Data Contract payload table_id does not match its version row.")
    return payload


def _selected_contract(rows: list[dict[str, Any]], table_id: str, contract_id: str, contract_version: int) -> dict[str, Any]:
    matches = [row for row in rows if str(row.get("contract_id") or "") == contract_id and int(row.get("contract_version") or 0) == contract_version]
    if not matches:
        raise ValueError("Selected Data Contract version does not exist.")
    row = matches[0]
    if str(row.get("table_id") or "") != table_id:
        raise ValueError("Selected Data Contract version does not belong to the selected table_id.")
    if str(row.get("status") or "").lower() == "rejected":
        raise ValueError("Rejected Data Contracts cannot be manually activated. Register a corrected version first.")
    _payload(row)
    return row


def _activation_states(rows: list[dict[str, Any]], selected: dict[str, Any]) -> list[dict[str, Any]]:
    """Return lifecycle-only changes while preserving every frozen definition."""
    table_id = str(selected["table_id"])
    changes = []
    for row in rows:
        if str(row.get("table_id") or "") != table_id:
            continue
        is_selected = row is selected or (
            str(row.get("contract_id")) == str(selected.get("contract_id"))
            and int(row.get("contract_version") or 0) == int(selected.get("contract_version") or 0)
        )
        was_active = row.get("is_active") is True or str(row.get("status") or "").lower() == "active"
        if not is_selected and not was_active:
            continue
        desired_status = "active" if is_selected else "superseded"
        desired_active = is_selected
        if row.get("status") != desired_status or row.get("is_active") is not desired_active:
            changes.append({"contract_id": row["contract_id"], "contract_version": int(row["contract_version"]), "status": desired_status, "is_active": desired_active})
    return changes


def _compact_review(payload: dict[str, Any]) -> dict[str, Any]:
    table, agreement = payload["table"], payload.get("agreement") or {}
    guardrails = payload.get("guardrails") or []
    counts: dict[str, int] = {}
    for rule in guardrails:
        kind = str(rule.get("guardrail_type") or "unspecified")
        counts[kind] = counts.get(kind, 0) + 1
    enrichment = payload.get("enrichment") or {}
    return {
        "table": {key: table.get(key) for key in ("table_id", "table_name", "schema_name", "layer", "store_type")},
        "agreement": {key: agreement.get(key) for key in ("agreement_name", "agreement_id", "agreement_version")},
        "schema_columns": len(table.get("columns") or []),
        "enrichment": {"table_values": len(enrichment.get("table") or []), "column_values": len(enrichment.get("columns") or [])},
        "guardrails": counts,
        "approved_usages": payload.get("approved_usages") or [],
    }


def widget_activate_data_contract(*, table_id: str | None = None, contract_id: str | None = None, contract_version: int | None = None, target: str = "metadata", schema: str | None = None, spark_session=None, context=None):
    """Select the frozen Data Contract version used by Production.

    Parameters
    ----------
    table_id : str, optional
        Initial governed table identity.
    contract_id : str, optional
        Initial saved contract lifecycle identity.
    contract_version : int, optional
        Initial exact saved version.
    target : str, default="metadata"
        Configured metadata Lakehouse target.
    schema : str, optional
        Metadata Lakehouse schema override.
    spark_session : object, optional
        Spark session override.
    context : object, optional
        FabricOps context normally established by ``00_env_config``.

    Returns
    -------
    dict
        Widget state, frozen contract review, controls, and an ``activate`` callable.

    Raises
    ------
    ValueError
        If the selection is missing, mismatched, rejected, or has an invalid payload.
    RuntimeError
        If active-contract metadata is ambiguous or Delta lifecycle updates fail.

    Notes
    -----
    Manual activation currently permits draft, active, and superseded versions.
    It atomically marks the selected version active and supersedes the previous
    active version without changing any frozen payload or identity field. This
    interim workflow performs no external approval and promotes no Fabric item;
    a later approved promotion workflow can call the same lifecycle operation.

    Examples
    --------
    >>> state = widget_activate_data_contract(table_id="orders", contract_version=2)
    >>> state["activate"]()

    See Also
    --------
    widget_register_data_contract, check_schema, check_freshness, check_changes, check_dq

    """
    config, env, resolved = resolve_fabric_context(context=context)
    spark = get_spark_session(spark_session)
    runtime_context = {"config": config, "env": env, **(resolved or {})}
    frame = read_lakehouse_table_core(CONTRACT_TABLE, target=target, schema=schema, spark_session=spark, context=runtime_context)
    rows = [_row_dict(row) for row in frame.collect()]
    tables = sorted({str(row.get("table_id") or "") for row in rows if row.get("table_id")})
    state: dict[str, Any] = {"available_table_ids": tables, "table_id": table_id, "contract_id": contract_id, "contract_version": contract_version, "versions": [], "current_active_version": None, "review": None, "message": "", "_controls": {}}

    def refresh() -> dict[str, Any] | None:
        selected_table = str(state.get("table_id") or "")
        versions = sorted([row for row in rows if str(row.get("table_id") or "") == selected_table], key=lambda row: int(row.get("contract_version") or 0), reverse=True)
        active = [row for row in versions if row.get("is_active") is True and str(row.get("status") or "").lower() == "active"]
        if len(active) > 1:
            raise RuntimeError(f"Data Contract integrity error: {selected_table!r} has multiple active versions.")
        state["versions"] = versions
        state["current_active_version"] = active[0].get("contract_version") if active else None
        if not versions:
            state["review"] = None
            return None
        version = int(state.get("contract_version") or versions[0]["contract_version"])
        cid = str(state.get("contract_id") or next((r["contract_id"] for r in versions if int(r["contract_version"]) == version), ""))
        selected = _selected_contract(rows, selected_table, cid, version)
        state.update(contract_id=cid, contract_version=version, review=_compact_review(_payload(selected)))
        return selected

    def activate() -> dict[str, Any]:
        selected = refresh()
        if selected is None:
            raise ValueError("Select a table and saved Data Contract version.")
        changes = _activation_states(rows, selected)
        if not changes:
            state["message"] = f"Data Contract v{selected['contract_version']} is already active."
            return {"changed": False, "contract_id": selected["contract_id"], "contract_version": selected["contract_version"]}
        try:
            from delta.tables import DeltaTable
        except Exception as exc:  # pragma: no cover - Fabric runtime dependency
            raise RuntimeError("Delta Lake support is required to activate a Data Contract.") from exc
        source = spark.createDataFrame(changes)
        _store, _table, _schema, path = resolve_configured_lakehouse_table(target, CONTRACT_TABLE, schema or configured_lakehouse_schema(config, env, target), context=runtime_context)
        (DeltaTable.forPath(spark, path).alias("target").merge(source.alias("source"), "target.contract_id = source.contract_id AND target.contract_version = source.contract_version").whenMatchedUpdate(set={"status": "source.status", "is_active": "source.is_active"}).execute())
        by_key = {(row["contract_id"], int(row["contract_version"])): row for row in rows}
        for change in changes:
            by_key[(change["contract_id"], change["contract_version"])].update(status=change["status"], is_active=change["is_active"])
        state["message"] = f"Data Contract v{selected['contract_version']} is now active for Production."
        refresh()
        return {"changed": True, "contract_id": selected["contract_id"], "contract_version": selected["contract_version"]}

    state["refresh"], state["activate"] = refresh, activate
    refresh()
    try:
        widgets = require_ipywidgets()
    except ModuleNotFoundError:
        return state
    table_control = widgets.Dropdown(options=[("Select one table", ""), *[(value, value) for value in tables]], value=state.get("table_id") or "", **widget_common(widgets, "Governed table"))
    version_control = widgets.Dropdown(description="Saved version")
    review_html, active_html, status = widgets.HTML(), widgets.HTML(), status_message(widgets)
    button = widgets.Button(description="Set as Active Data Contract", button_style="primary")

    def render(*_args: Any) -> None:
        state["table_id"] = table_control.value or None
        versions = sorted([row for row in rows if str(row.get("table_id") or "") == str(state.get("table_id") or "")], key=lambda row: int(row.get("contract_version") or 0), reverse=True)
        options = [(f"v{r['contract_version']} · {r.get('status')}" + (" · ACTIVE" if r.get("is_active") else ""), f"{r['contract_id']}\n{r['contract_version']}") for r in versions]
        version_control.options = options
        if version_control.value:
            state["contract_id"], value = version_control.value.split("\n", 1); state["contract_version"] = int(value)
        try:
            refresh()
            review_html.value = "<pre>" + html.escape(json.dumps(state.get("review"), indent=2)) + "</pre>"
            active_html.value = f"<b>Current Production contract:</b> {('v' + str(state['current_active_version'])) if state['current_active_version'] else 'None'}<br><b>Selected:</b> v{state.get('contract_version') or '—'}"
        except (ValueError, RuntimeError) as exc:
            status.value = html.escape(str(exc))
    table_control.observe(render, names="value"); version_control.observe(render, names="value")
    def on_activate(_button: Any) -> None:
        try:
            activate(); status.value = html.escape(state["message"]); render()
        except (ValueError, RuntimeError) as exc:
            status.value = html.escape(str(exc))
    button.on_click(on_activate); render()
    notice = widgets.HTML(value="<b>Manual activation</b><br>Governance explicitly selects the Data Contract version used by Production. External approval and automated Production promotion are planned as a later workflow.")
    page = form_page(widgets, title="Activate Data Contract", description="Select one frozen contract version for Production enforcement.", children=[form_section(widgets, title="1. Governed table and version", children=[table_control, version_control, active_html]), form_section(widgets, title="2. Frozen contract review", children=[review_html]), form_section(widgets, title="3. Manual activation", children=[notice]), action_row(widgets, [button]), status])
    state["_controls"] = {"table": table_control, "version": version_control, "review": review_html, "active": active_html, "activate": button, "status": status, "page": page}
    from IPython import display as ip
    ip.display(page)
    return state
