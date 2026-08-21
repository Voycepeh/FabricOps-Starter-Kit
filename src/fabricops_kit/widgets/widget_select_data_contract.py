"""Public widget for selecting a Development Data Contract validation source."""

from __future__ import annotations

import html
from typing import Any

from fabricops_kit.config.shared import get_default_fabric_context, get_store, resolve_fabric_context
from fabricops_kit.io.shared import configured_lakehouse_schema, get_spark_session, read_lakehouse_table_core, resolve_lakehouse_table_location, resolve_warehouse_table_location
from fabricops_kit.pipeline.shared import resolve_active_data_contract, resolve_catalogue_table_id
from fabricops_kit.widgets.shared import form_page, form_section, parse_data_contract_payload, pipeline_active_context, require_ipywidgets, status_message, widget_common

CONTRACT_TABLE = "METADATA_DATA_CONTRACT"
AUTHORING = ""


def _row_dict(row: Any) -> dict[str, Any]:
    return row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)


def _contract_options(rows: list[dict[str, Any]], table_id: str) -> list[dict[str, Any]]:
    """Return newest-first selectable contract rows for one canonical table."""
    return sorted(
        (dict(row) for row in rows if str(row.get("table_id") or "") == table_id),
        key=lambda row: int(row.get("contract_version") or 0),
        reverse=True,
    )


def _contract_review(row: dict[str, Any]) -> dict[str, Any]:
    """Build a compact review solely from an immutable contract payload."""
    payload = parse_data_contract_payload(row)
    table, agreement = payload["table"], payload.get("agreement") or {}
    guardrails = payload.get("guardrails") or []
    counts: dict[str, int] = {}
    for rule in guardrails:
        kind = str(rule.get("guardrail_type") or "unspecified")
        counts[kind] = counts.get(kind, 0) + 1
    return {
        "contract_version": int(row["contract_version"]),
        "status": str(row.get("status") or ""),
        "agreement": {key: agreement.get(key) for key in ("agreement_name", "agreement_id", "agreement_version")},
        "table": {key: table.get(key) for key in ("table_id", "schema_name", "table_name")},
        "schema_columns": len(table.get("columns") or []),
        "guardrails": counts,
        "guardrail_details": guardrails,
        "approved_usages": payload.get("approved_usages") or [],
    }


def _set_override(context: dict[str, Any], table_id: str, contract: dict[str, Any] | None) -> None:
    """Set or clear one table's override in established Fabric contexts."""
    contexts = [context]
    active = pipeline_active_context()
    if active is not None:
        if active.context is None:
            active.context = {}
        contexts.append(active.context)
    try:
        contexts.append(get_default_fabric_context())
    except RuntimeError:
        pass
    for target_context in contexts:
        overrides = dict(target_context.get("data_contract_overrides") or {})
        if contract is None:
            overrides.pop(table_id, None)
        else:
            overrides[table_id] = {
                "contract_id": str(contract["contract_id"]),
                "contract_version": int(contract["contract_version"]),
            }
        target_context["data_contract_overrides"] = overrides


def widget_select_data_contract(
    table_name: str,
    *,
    target: str = "source",
    schema: str | None = None,
    spark_session=None,
    context=None,
):
    """Choose the Guardrail source for one table's Development checks.

    Parameters
    ----------
    table_name : str
        Physical table name within the configured target.
    target : str, default="source"
        Logical FabricOps target containing the configured physical table.
    schema : str, optional
        Physical schema containing the configured table.
    spark_session : object, optional
        Spark session override.
    context : dict, optional
        FabricOps context normally established by ``00_env_config``.

    Returns
    -------
    dict
        Read-only selection state, available versions, frozen preview, controls,
        and a ``select`` callable. Each exact selection is stored under its
        canonical table identity in ``data_contract_overrides``; selecting
        current authoring Guardrails removes only that table's entry.

    Raises
    ------
    ValueError
        If the table cannot be resolved, a version belongs to another table,
        or a rejected contract is selected.

    Notes
    -----
    This is a read-only Development testing tool and never activates or changes
    Data Contract metadata. Current authoring Guardrails are the default.
    Production ignores manual selection and uses its active Data Contract
    automatically. Frozen previews are read only from ``contract_payload_json``.

    Examples
    --------
    >>> selection = widget_select_data_contract("orders", target="source", schema="dbo")
    >>> selection["select"]()  # current authoring Guardrails

    See Also
    --------
    widget_activate_data_contract, check_schema, check_freshness, check_changes, check_dq

    """
    config, env, resolved = resolve_fabric_context(context=context)
    spark = get_spark_session(spark_session)
    runtime_context = {"config": config, "env": env, **(resolved or {})}
    store = get_store(config, env, target)
    store_type = str(store.kind).lower()
    if store_type == "warehouse":
        schema_name, resolved_table, _ = resolve_warehouse_table_location(store, schema or getattr(store, "schema", None), table_name)
    elif store_type == "lakehouse":
        resolved_table, schema_name, _ = resolve_lakehouse_table_location(store, table_name, schema)
    else:
        raise ValueError(f"Target {target!r} must resolve to a Lakehouse or Warehouse.")
    table_id = resolve_catalogue_table_id(config, env, store_type=store_type, layer=target, schema_name=schema_name, table_name=resolved_table, spark_session=spark)
    metadata_schema = configured_lakehouse_schema(config, env, "metadata")
    if env == "prod":
        versions = []
    else:
        frame = read_lakehouse_table_core(
            CONTRACT_TABLE, target="metadata", schema=metadata_schema,
            spark_session=spark, context=runtime_context,
        )
        versions = _contract_options([_row_dict(row) for row in frame.collect()], table_id)
    state: dict[str, Any] = {"table_id": table_id, "table_name": resolved_table, "versions": versions, "data_contract_id": None, "data_contract_version": None, "review": None, "message": "", "_controls": {}}
    selection_context = context if isinstance(context, dict) else resolved

    def select(contract_id: str | None = None, contract_version: int | None = None) -> dict[str, Any]:
        if env == "prod":
            state.update(data_contract_id=None, data_contract_version=None, review=None)
            return state
        if not contract_id and contract_version is None:
            _set_override(selection_context, table_id, None)
            state.update(data_contract_id=None, data_contract_version=None, review=None, message="Validation source: Current authoring Guardrails")
            return state
        matches = [row for row in versions if str(row.get("contract_id") or "") == str(contract_id or "") and int(row.get("contract_version") or 0) == int(contract_version or 0)]
        if not matches:
            raise ValueError("Selected Data Contract version is not available for this table.")
        selected = matches[0]
        if str(selected.get("status") or "").lower() == "rejected":
            raise ValueError("Rejected Data Contracts cannot be used for Development testing.")
        review = _contract_review(selected)
        _set_override(selection_context, table_id, selected)
        state.update(data_contract_id=str(selected["contract_id"]), data_contract_version=int(selected["contract_version"]), review=review, message=f"Using frozen Guardrails from Data Contract v{selected['contract_version']}")
        return state

    state["select"] = select
    if env == "prod":
        try:
            active_contract = resolve_active_data_contract(
                config, env, table_id, spark_session=spark, required=False,
            )
        except ValueError:
            active_contract = None
        state["message"] = (
            f"Active Data Contract v{active_contract['contract_version']}"
            if active_contract else "No active Data Contract"
        )
    else:
        select()
    try:
        widgets = require_ipywidgets()
    except ModuleNotFoundError:
        return state
    status = status_message(widgets)
    if env == "prod":
        page = form_page(widgets, title="Validation source", description="Production validation is read only.", children=[form_section(widgets, title="Production Data Contract", children=[widgets.HTML(value=html.escape(state["message"]))])])
        state["_controls"] = {"status": status, "page": page}
    else:
        options = [("Current authoring Guardrails", AUTHORING)] + [
            (f"Data Contract v{row['contract_version']} — {row.get('status')}" + (" — active" if row.get("is_active") else ""), f"{row['contract_id']}\n{row['contract_version']}")
            for row in versions
        ]
        control = widgets.RadioButtons(options=options, value=AUTHORING, **widget_common(widgets, "Validation source"))
        preview = widgets.HTML(value="")

        def render(change=None) -> None:
            try:
                value = control.value
                if value:
                    contract_id, version = value.split("\n", 1)
                    select(contract_id, int(version))
                else:
                    select()
                review = state.get("review")
                preview.value = html.escape(state["message"]) if not review else (
                    f"<b>Data Contract v{review['contract_version']}</b><br>Status: {html.escape(review['status'])}<br>"
                    f"Schema: {review['schema_columns']} columns<br>Guardrails: {html.escape(', '.join(f'{key}: {value}' for key, value in review['guardrails'].items()) or 'None')}"
                )
                status.value = ""
            except ValueError as exc:
                control.value = AUTHORING
                status.value = html.escape(str(exc))

        control.observe(render, names="value")
        render()
        page = form_page(widgets, title="Validation source", description="Choose current authoring Guardrails or one exact frozen Data Contract for Development testing.", children=[form_section(widgets, title="Development Guardrail source", children=[control, preview]), status])
        state["_controls"] = {"selection": control, "preview": preview, "status": status, "page": page}
    from IPython import display as ip
    ip.display(page)
    return state
