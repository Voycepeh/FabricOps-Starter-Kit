"""Public widget for linking and activating a table's Production Data Contract."""

from __future__ import annotations

import html
import json
from typing import Any

from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session, read_lakehouse_table_core
from fabricops_kit.widgets.shared import (
    activate_contract_version,
    action_row,
    form_page,
    form_section,
    parse_data_contract_payload,
    require_ipywidgets,
    status_message,
    widget_common,
)

CONTRACT_TABLE = "METADATA_DATA_CONTRACT"
AGREEMENT_TABLE = "METADATA_DATA_AGREEMENT"


def _row_dict(row: Any) -> dict[str, Any]:
    return row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)


def _payload(row: dict[str, Any]) -> dict[str, Any]:
    return parse_data_contract_payload(row)


def _selected_contract(
    rows: list[dict[str, Any]], table_id: str, contract_id: str, contract_version: int
) -> dict[str, Any]:
    matches = [
        row for row in rows
        if str(row.get("contract_id") or "") == contract_id
        and int(row.get("contract_version") or 0) == contract_version
    ]
    if not matches:
        raise ValueError("Selected Data Contract version does not exist.")
    row = matches[0]
    if str(row.get("table_id") or "") != table_id:
        raise ValueError("Selected Data Contract version does not belong to the selected table_id.")
    if str(row.get("status") or "").lower() not in {"frozen", "active", "superseded"}:
        raise ValueError("Only a frozen Data Contract version can be activated.")
    _payload(row)
    return row


def _compact_review(payload: dict[str, Any]) -> dict[str, Any]:
    table = payload["table"]
    guardrails = payload.get("guardrails") or []
    counts: dict[str, int] = {}
    for rule in guardrails:
        kind = str(rule.get("guardrail_type") or "unspecified")
        counts[kind] = counts.get(kind, 0) + 1
    enrichment = payload.get("enrichment") or {}
    return {
        "table": {key: table.get(key) for key in ("table_id", "table_name", "schema_name", "layer", "store_type")},
        "schema_columns": len(table.get("columns") or []),
        "enrichment": {
            "table_values": len(enrichment.get("table") or []),
            "column_values": len(enrichment.get("columns") or []),
        },
        "guardrails": counts,
        "processing": table.get("processing"),
    }


def widget_activate_data_contract(
    *, table_id: str | None = None, contract_id: str | None = None,
    contract_version: int | None = None, agreement_id: str | None = None,
    agreement_version: str | None = None, target: str = "metadata",
    schema: str | None = None, spark_session=None, context=None,
):
    """Link an exact Data Agreement version and activate a frozen Data Contract.

    Parameters
    ----------
    table_id : str, optional
        Initial governed table identity.
    contract_id : str, optional
        Initial frozen Data Contract lifecycle identity.
    contract_version : int, optional
        Initial exact immutable Data Contract version.
    agreement_id : str, optional
        Initial Data Agreement lifecycle identity selected at activation time.
    agreement_version : str, optional
        Initial exact Data Agreement version selected at activation time.
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
        Selection state, immutable review, controls, and an ``activate`` callable.

    Raises
    ------
    ValueError
        If the contract or exact Agreement version is missing, mismatched, or ineligible.
    RuntimeError
        If active-contract metadata is ambiguous or the atomic Delta update fails.

    Notes
    -----
    Activation writes Agreement linkage only to the selected contract version,
    atomically activates it, and supersedes the prior active version for the same
    ``table_id``. It never changes the frozen payload and does not deploy notebooks.
    Repeating the same activation is idempotent; conflicting relink requests fail.

    Examples
    --------
    >>> state = widget_activate_data_contract(
    ...     table_id="orders", contract_version=2,
    ...     agreement_id="agreement-orders", agreement_version="1.0.0",
    ... )
    >>> state["activate"]()

    See Also
    --------
    widget_author_data_contract, widget_select_data_contract

    """
    config, env, resolved = resolve_fabric_context(context=context)
    spark = get_spark_session(spark_session)
    runtime_context = {"config": config, "env": env, **(resolved or {})}
    contracts = [_row_dict(row) for row in read_lakehouse_table_core(
        CONTRACT_TABLE, target=target, schema=schema, spark_session=spark,
        context=runtime_context,
    ).collect()]
    agreements = [_row_dict(row) for row in read_lakehouse_table_core(
        AGREEMENT_TABLE, target=target,
        schema=metadata_table_physical_schema(config, AGREEMENT_TABLE),
        spark_session=spark, context=runtime_context,
    ).collect()]
    tables = sorted({str(row.get("table_id") or "") for row in contracts if row.get("table_id")})
    state: dict[str, Any] = {
        "available_table_ids": tables, "table_id": table_id,
        "contract_id": contract_id, "contract_version": contract_version,
        "agreement_id": agreement_id, "agreement_version": agreement_version,
        "versions": [], "agreements": agreements, "current_active_version": None,
        "review": None, "message": "", "_controls": {},
    }

    def refresh() -> dict[str, Any] | None:
        selected_table = str(state.get("table_id") or "")
        versions = sorted(
            [row for row in contracts if str(row.get("table_id") or "") == selected_table
             and str(row.get("status") or "").lower() in {"frozen", "active", "superseded"}],
            key=lambda row: int(row.get("contract_version") or 0), reverse=True,
        )
        active = [row for row in versions if row.get("is_active") is True]
        if len(active) > 1:
            raise RuntimeError(f"Data Contract integrity error: {selected_table!r} has multiple active versions.")
        state["versions"] = versions
        state["current_active_version"] = active[0].get("contract_version") if active else None
        if not versions:
            state["review"] = None
            return None
        version = int(state.get("contract_version") or versions[0]["contract_version"])
        cid = str(state.get("contract_id") or next(
            (row["contract_id"] for row in versions if int(row["contract_version"]) == version), ""
        ))
        selected = _selected_contract(contracts, selected_table, cid, version)
        state.update(contract_id=cid, contract_version=version, review=_compact_review(_payload(selected)))
        return selected

    def activate() -> dict[str, Any]:
        selected = refresh()
        if selected is None:
            raise ValueError("Select a table and frozen Data Contract version.")
        aid = str(state.get("agreement_id") or "").strip()
        aversion = str(state.get("agreement_version") or "").strip()
        if not aid or not aversion:
            raise ValueError("Select an exact Data Agreement version before activation.")
        result = activate_contract_version(
            config=config, env=env, table_id=str(selected["table_id"]),
            contract_id=str(selected["contract_id"]),
            contract_version=int(selected["contract_version"]),
            agreement_id=aid, agreement_version=aversion,
            target=target, schema=schema, spark_session=spark, context=runtime_context,
        )
        if not result["changed"]:
            state["message"] = f"Data Contract v{selected['contract_version']} is already active with this Data Agreement."
            return result
        by_key = {(row["contract_id"], int(row["contract_version"])): row for row in contracts}
        for change in result["changes"]:
            by_key[(change["contract_id"], change["contract_version"])].update(change)
        state["message"] = f"Data Contract v{selected['contract_version']} is linked and active for Production."
        refresh()
        return result

    state["refresh"], state["activate"] = refresh, activate
    refresh()
    try:
        widgets = require_ipywidgets()
    except ModuleNotFoundError:
        return state
    table_control = widgets.Dropdown(
        options=[("Select one table", ""), *[(value, value) for value in tables]],
        value=state.get("table_id") or "", **widget_common(widgets, "Governed table"),
    )
    version_control = widgets.Dropdown(description="Frozen version")
    agreement_control = widgets.Dropdown(
        options=[("Select one Agreement version", ""), *[
            (f"{row.get('agreement_name') or row['agreement_id']} · v{row['agreement_version']}",
             f"{row['agreement_id']}\n{row['agreement_version']}") for row in agreements
        ]], **widget_common(widgets, "Data Agreement version"),
    )
    review_html, active_html, status = widgets.HTML(), widgets.HTML(), status_message(widgets)
    button = widgets.Button(description="Link Agreement and Activate", button_style="primary")

    def render(*_args: Any) -> None:
        state["table_id"] = table_control.value or None
        versions = sorted(
            [row for row in contracts if str(row.get("table_id") or "") == str(state.get("table_id") or "")
             and str(row.get("status") or "").lower() in {"frozen", "active", "superseded"}],
            key=lambda row: int(row.get("contract_version") or 0), reverse=True,
        )
        version_control.options = [
            (f"v{row['contract_version']} · {row.get('status')}", f"{row['contract_id']}\n{row['contract_version']}")
            for row in versions
        ]
        if version_control.value:
            state["contract_id"], value = version_control.value.split("\n", 1)
            state["contract_version"] = int(value)
        if agreement_control.value:
            state["agreement_id"], state["agreement_version"] = agreement_control.value.split("\n", 1)
        try:
            refresh()
            review = {**(state.get("review") or {}), "agreement_linkage": {
                "agreement_id": state.get("agreement_id"), "agreement_version": state.get("agreement_version"),
            }}
            review_html.value = "<pre>" + html.escape(json.dumps(review, indent=2)) + "</pre>"
            active_html.value = f"<b>Current Production contract:</b> {('v' + str(state['current_active_version'])) if state['current_active_version'] else 'None'}"
            status.value = ""
        except (ValueError, RuntimeError) as exc:
            status.value = html.escape(str(exc))

    table_control.observe(render, names="value")
    version_control.observe(render, names="value")
    agreement_control.observe(render, names="value")

    def on_activate(_button: Any) -> None:
        try:
            activate()
            status.value = html.escape(state["message"])
            render()
        except (ValueError, RuntimeError) as exc:
            status.value = html.escape(str(exc))

    button.on_click(on_activate)
    render()
    page = form_page(
        widgets, title="Link and Activate Data Contract",
        description="Review one frozen table contract and explicitly link an exact Data Agreement version.",
        children=[
            form_section(widgets, title="1. Governed table and frozen version", children=[table_control, version_control, active_html]),
            form_section(widgets, title="2. Data Agreement version", children=[agreement_control]),
            form_section(widgets, title="3. Confirm immutable definition and linkage", children=[review_html]),
            action_row(widgets, [button]), status,
        ],
    )
    state["_controls"] = {
        "table": table_control, "version": version_control, "agreement": agreement_control,
        "review": review_html, "active": active_html, "activate": button, "status": status, "page": page,
    }
    from IPython import display as ip
    ip.display(page)
    return state
