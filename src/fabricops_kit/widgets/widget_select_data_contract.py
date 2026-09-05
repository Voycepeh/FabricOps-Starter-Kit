"""Public widget for selecting one whole Development Data Contract."""

from __future__ import annotations

import html
from typing import Any

from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
from fabricops_kit.config.shared import get_default_fabric_context, resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session, read_lakehouse_table_core
from fabricops_kit.pipeline.shared import resolve_active_data_contract
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
        "processing": table.get("processing"),
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
    table_id: str,
    *,
    spark_session=None,
    context=None,
):
    """Choose one whole Data Contract for a table's Development testing.

    Parameters
    ----------
    table_id : str
        Canonical table identity already stored in FabricOps metadata.
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
        current authoring removes only that table's entry.

    Raises
    ------
    ValueError
        If ``table_id`` is empty, a version belongs to another table, or a rejected contract is selected.

    Notes
    -----
    This is a read-only Development testing tool and never activates or changes
    Data Contract metadata. Current authoring is the default.
    Production ignores manual selection and uses its active Data Contract
    automatically. Frozen previews are read only from ``contract_payload_json``.

    Examples
    --------
    >>> selection = widget_select_data_contract(table_id="table-orders")
    >>> selection["select"]()  # current authoring

    See Also
    --------
    widget_activate_data_contract, check_schema, check_freshness, check_changes, check_dq

    """
    table_id = str(table_id or "").strip()
    if not table_id:
        raise ValueError("table_id must be a non-empty canonical FabricOps table identity.")
    config, env, resolved = resolve_fabric_context(context=context)
    spark = get_spark_session(spark_session)
    runtime_context = {"config": config, "env": env, **(resolved or {})}
    metadata_schema = metadata_table_physical_schema(config, CONTRACT_TABLE)
    if env == "prod":
        versions = []
    else:
        frame = read_lakehouse_table_core(
            CONTRACT_TABLE, target="metadata", schema=metadata_schema,
            spark_session=spark, context=runtime_context,
        )
        versions = _contract_options([_row_dict(row) for row in frame.collect()], table_id)
    state: dict[str, Any] = {"table_id": table_id, "versions": versions, "data_contract_id": None, "data_contract_version": None, "review": None, "message": "", "_controls": {}}
    selection_context = context if isinstance(context, dict) else resolved

    def select(contract_id: str | None = None, contract_version: int | None = None) -> dict[str, Any]:
        if env == "prod":
            state.update(data_contract_id=None, data_contract_version=None, review=None)
            return state
        if not contract_id and contract_version is None:
            _set_override(selection_context, table_id, None)
            state.update(data_contract_id=None, data_contract_version=None, review=None, message="Current authoring")
            return state
        matches = [row for row in versions if str(row.get("contract_id") or "") == str(contract_id or "") and int(row.get("contract_version") or 0) == int(contract_version or 0)]
        if not matches:
            raise ValueError("Selected Data Contract version is not available for this table.")
        selected = matches[0]
        if str(selected.get("status") or "").lower() == "rejected":
            raise ValueError("Rejected Data Contracts cannot be used for Development testing.")
        review = _contract_review(selected)
        _set_override(selection_context, table_id, selected)
        state.update(data_contract_id=str(selected["contract_id"]), data_contract_version=int(selected["contract_version"]), review=review, message=f"Using Data Contract v{selected['contract_version']}")
        return state

    state["select"] = select
    if env == "prod":
        try:
            active_contract = resolve_active_data_contract(config, env, table_id, spark_session=spark, required=True)
        except ValueError as exc:
            raise ValueError(f"Production requires an active Data Contract for table_id {table_id!r}.") from exc
        state["message"] = f"Using active Data Contract v{active_contract['contract_version']}"
    else:
        select()
    try:
        widgets = require_ipywidgets()
    except ModuleNotFoundError:
        return state
    status = status_message(widgets)
    if env == "prod":
        page = form_page(widgets, title="Data Contract", description="Production automatically uses the active Data Contract.", children=[form_section(widgets, title="Production Data Contract", children=[widgets.HTML(value=html.escape(state["message"]))])])
        state["_controls"] = {"status": status, "page": page}
    else:
        options = [("Current authoring", AUTHORING)] + [
            (f"Data Contract v{row['contract_version']} — {row.get('status')}" + (" — active" if row.get("is_active") else ""), f"{row['contract_id']}\n{row['contract_version']}")
            for row in versions
        ]
        control = widgets.RadioButtons(options=options, value=AUTHORING, **widget_common(widgets, "Data Contract"))
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
                    f"Table ID: {html.escape(review['table']['table_id'])}<br>Schema: {review['schema_columns']} columns<br>"
                    f"Guardrails: {html.escape(', '.join(f'{key}: {value}' for key, value in review['guardrails'].items()) or 'None')}<br>"
                    f"Processing: {html.escape(', '.join(f'{key}: {value}' for key, value in (review['processing'] or {}).items()) or 'Missing')}"
                )
                status.value = ""
            except ValueError as exc:
                control.value = AUTHORING
                status.value = html.escape(str(exc))

        control.observe(render, names="value")
        render()
        page = form_page(widgets, title="Data Contract", description="Choose current authoring or one exact frozen Data Contract for Development testing.", children=[form_section(widgets, title="Development Data Contract", children=[control, preview]), status])
        state["_controls"] = {"selection": control, "preview": preview, "status": status, "page": page}
    from IPython import display as ip
    ip.display(page)
    return state
