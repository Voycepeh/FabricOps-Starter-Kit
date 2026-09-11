"""Notebook-scoped Data Contract selection for Development and Production."""

from __future__ import annotations

import html
from typing import Any

from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
from fabricops_kit.config.shared import (
    get_default_fabric_context,
    is_table_not_found_error,
    resolve_fabric_context,
)
from fabricops_kit.io.shared import get_spark_session, read_lakehouse_table_core
from fabricops_kit.pipeline.shared import resolve_active_data_contract
from fabricops_kit.widgets.shared import (
    form_page,
    form_section,
    parse_data_contract_payload,
    pipeline_active_context,
    require_ipywidgets,
    resolve_notebook_lineage_tables,
    status_message,
    widget_common,
)

CONTRACT_TABLE = "METADATA_DATA_CONTRACT"
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"


def _row_dict(row: Any) -> dict[str, Any]:
    return row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)


def _contract_options(rows: list[dict[str, Any]], table_id: str) -> list[dict[str, Any]]:
    """Return newest-first immutable contract rows for one canonical table."""
    return sorted(
        (
            dict(row) for row in rows
            if str(row.get("table_id") or "") == table_id
            and str(row.get("status") or "").lower() in {"frozen", "active", "superseded"}
        ),
        key=lambda row: int(row.get("contract_version") or 0), reverse=True,
    )


def _contract_review(row: dict[str, Any]) -> dict[str, Any]:
    """Build a compact review solely from an immutable contract payload."""
    payload = parse_data_contract_payload(row)
    table = payload["table"]
    guardrails = payload.get("guardrails") or []
    counts: dict[str, int] = {}
    for rule in guardrails:
        kind = str(rule.get("guardrail_type") or "unspecified")
        counts[kind] = counts.get(kind, 0) + 1
    return {
        "contract_version": int(row["contract_version"]),
        "status": str(row.get("status") or ""),
        "contract_date": row.get("_committed_at"),
        "table": {key: table.get(key) for key in ("table_id", "schema_name", "table_name")},
        "schema_columns": len(table.get("columns") or []),
        "guardrails": counts,
        "guardrail_details": guardrails,
        "processing": table.get("processing"),
    }


def _set_override(context: dict[str, Any], table_id: str, contract: dict[str, Any]) -> None:
    """Set one table's immutable override without changing any other table."""
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
        overrides[table_id] = {
            "contract_id": str(contract["contract_id"]),
            "contract_version": int(contract["contract_version"]),
        }
        target_context["data_contract_overrides"] = overrides


def widget_select_data_contract(*, spark_session=None, context=None):
    """Select immutable Data Contracts for every table linked to this notebook.

    Parameters
    ----------
    spark_session : object, optional
        Spark session override.
    context : dict, optional
        FabricOps context normally established by ``00_env_config``. The current
        ``notebook_id``, optional ``workspace_id``, and environment scope Lineage.

    Returns
    -------
    dict
        Notebook scope, role-preserving table states, table-scoped resolved
        contracts, controls, and a Development ``select`` callable.

    Raises
    ------
    ValueError
        If notebook identity is missing, a requested version is unavailable,
        or Production has no active contract for a Lineage-linked table.
    RuntimeError
        If Production has multiple active versions for a lineage-linked table.

    Notes
    -----
    Development may independently select a frozen, active, or superseded
    immutable version for each Lineage-linked ``table_id`` and stores it in
    ``data_contract_overrides``. Draft and rejected versions are excluded.
    An unselected Development table runs without contract-backed enforcement.
    Production ignores overrides, exposes no picker, and resolves exactly one
    active version per linked table. This widget never activates metadata.

    Examples
    --------
    >>> selection = widget_select_data_contract()
    >>> selection["select"]("table-orders", "orders-contract", 3)

    See Also
    --------
    widget_author_data_contract, widget_activate_data_contract

    """
    config, env, resolved = resolve_fabric_context(context=context)
    spark = get_spark_session(spark_session)
    runtime_context = {"config": config, "env": env, **(resolved or {})}
    lineage_schema = metadata_table_physical_schema(config, LINEAGE_TABLE)
    pairs, notebook_scope = resolve_notebook_lineage_tables(
        environment_name=env, target="metadata", schema=lineage_schema,
        spark_session=spark, context=runtime_context, runtime_context=runtime_context,
        required=env == "prod",
    )
    table_ids = list(dict.fromkeys(table_id for _role, table_id in pairs))
    selection_context = context if isinstance(context, dict) else (resolved or runtime_context)
    state: dict[str, Any] = {
        "notebook": notebook_scope,
        "lineage_tables": [{"pipeline_role": role, "table_id": table_id} for role, table_id in pairs],
        "environment": env, "tables": {}, "resolved_contracts": {}, "message": "", "_controls": {},
    }

    # Initialization always starts Development unselected and Production ignores overrides.
    selection_context["data_contract_overrides"] = {}
    if env == "prod":
        for table_id in table_ids:
            try:
                contract = resolve_active_data_contract(
                    config, env, table_id, spark_session=spark, required=True,
                )
            except ValueError as exc:
                raise ValueError(
                    f"Production environment {env!r} requires exactly one active Data Contract for "
                    f"lineage-linked table {table_id!r} (table_id={table_id!r})."
                ) from exc
            except RuntimeError as exc:
                raise RuntimeError(
                    f"Production environment {env!r} cannot resolve Data Contract for lineage-linked "
                    f"table {table_id!r} (table_id={table_id!r}): {exc}"
                ) from exc
            state["tables"][table_id] = {"versions": [], "selected": contract, "review": _contract_review(contract)}
            state["resolved_contracts"][table_id] = {
                "contract_id": str(contract["contract_id"]),
                "contract_version": int(contract["contract_version"]),
            }
        state["message"] = f"Resolved {len(table_ids)} active Production Data Contract(s)."
    else:
        try:
            contracts = [_row_dict(row) for row in read_lakehouse_table_core(
                CONTRACT_TABLE, target="metadata",
                schema=metadata_table_physical_schema(config, CONTRACT_TABLE),
                spark_session=spark, context=runtime_context,
            ).collect()]
        except Exception as exc:
            if not is_table_not_found_error(exc):
                raise
            contracts = []
        for table_id in table_ids:
            versions = _contract_options(contracts, table_id)
            state["tables"][table_id] = {"versions": versions, "selected": None, "review": None}
        state["message"] = (
            "Development only · running unvalidated until immutable Data Contract versions are explicitly selected."
        )

    def select(table_id: str, contract_id: str, contract_version: int) -> dict[str, Any]:
        if env == "prod":
            raise ValueError("Production Data Contracts are resolved automatically and cannot be selected manually.")
        if table_id not in state["tables"]:
            raise ValueError("The selected table_id is not linked to the current notebook in METADATA_DATA_LINEAGE.")
        matches = [
            row for row in state["tables"][table_id]["versions"]
            if str(row.get("contract_id") or "") == str(contract_id or "")
            and int(row.get("contract_version") or 0) == int(contract_version or 0)
        ]
        if not matches:
            raise ValueError("Selected immutable Data Contract version is not available for this table.")
        selected = matches[0]
        review = _contract_review(selected)
        _set_override(selection_context, table_id, selected)
        state["tables"][table_id].update(selected=selected, review=review)
        state["resolved_contracts"][table_id] = {
            "contract_id": str(selected["contract_id"]),
            "contract_version": int(selected["contract_version"]),
        }
        state["message"] = f"Using Data Contract v{selected['contract_version']} for {table_id}."
        return state

    state["select"] = select
    try:
        widgets = require_ipywidgets()
    except ModuleNotFoundError:
        return state
    status = status_message(widgets)
    sections = []
    if env == "prod":
        for role, table_id in pairs:
            resolved_contract = state["resolved_contracts"][table_id]
            review = state["tables"][table_id]["review"]
            table_name = review["table"].get("table_name") or table_id
            sections.append(widgets.HTML(value=html.escape(
                f"{'Read' if role.lower() == 'source' else 'Write'}  {table_name} · table_id {table_id} · "
                f"Data Contract v{resolved_contract['contract_version']} · Active · "
                f"{review['contract_date'] or 'date unavailable'}"
            )))
        page = form_page(
            widgets, title="Production Data Contracts",
            description="Active immutable versions resolved from current-notebook Lineage.",
            children=[form_section(widgets, title="Resolved contracts", children=sections), status],
        )
        state["_controls"] = {"status": status, "page": page}
    else:
        controls: dict[str, Any] = {}
        for role, table_id in pairs:
            if table_id in controls:
                continue
            versions = state["tables"][table_id]["versions"]
            control = widgets.Dropdown(
                options=[("No Data Contract · Development only", ""), *[
                    (f"Data Contract v{row['contract_version']} · {row.get('status')}",
                     f"{row['contract_id']}\n{row['contract_version']}") for row in versions
                ]], **widget_common(widgets, f"{role} · {table_id}"),
            )
            preview = widgets.HTML(value="")

            def render(change: Any, *, current_table: str = table_id, current_control: Any = control, current_preview: Any = preview) -> None:
                if not change.get("new"):
                    return
                try:
                    contract_id, version = current_control.value.split("\n", 1)
                    select(current_table, contract_id, int(version))
                    review = state["tables"][current_table]["review"]
                    current_preview.value = (
                        f"<b>v{review['contract_version']}</b> · {html.escape(review['status'].title())} · "
                        f"{html.escape(str(review['contract_date'] or 'date unavailable'))} · "
                        f"{review['schema_columns']} columns · "
                        f"{html.escape(str(review['processing'] or 'Missing processing'))}"
                    )
                    status.value = ""
                except ValueError as exc:
                    status.value = html.escape(str(exc))

            control.observe(render, names="value")
            controls[table_id] = control
            role_label = "Read" if role.lower() == "source" else "Write"
            table_name = table_id
            if versions:
                table_name = str(parse_data_contract_payload(versions[0])["table"].get("table_name") or table_id)
            sections.extend([
                widgets.HTML(value=html.escape(f"{role_label}  {table_name} · table_id {table_id}")),
                control, preview,
            ])
        page = form_page(
            widgets, title="Development Data Contracts",
            description=(f"Environment: {env} · Notebook: {notebook_scope.get('notebook_name') or notebook_scope.get('notebook_id')} · "
                         "Unselected tables run unvalidated in Development only."),
            children=[form_section(widgets, title="Lineage-linked tables", children=sections), status],
        )
        state["_controls"] = {"selections": controls, "status": status, "page": page}
    from IPython import display as ip
    ip.display(page)
    return state
