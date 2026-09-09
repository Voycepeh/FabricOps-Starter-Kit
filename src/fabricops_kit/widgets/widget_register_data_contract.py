"""Public widget entrypoint for versioned, one-table Data Contracts."""

from __future__ import annotations

import html
import json
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.data_contract.shared import contract_lifecycle_id, freeze_contract, parse_approved_usages, select_approved_usages
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session, read_lakehouse_table_core, write_lakehouse_table_core
from fabricops_kit.widgets.shared import action_row, form_page, form_section, require_ipywidgets, status_message, widget_common

CONTRACT_TABLE = "METADATA_DATA_CONTRACT"
_SOURCE_TABLES = (
    "METADATA_DATA_AGREEMENT", "METADATA_DATA_STEWARD", "METADATA_DATA_CATALOGUE",
    "METADATA_ENRICHMENT", "METADATA_GUARDRAIL",
)


def _rows(frame: Any) -> list[dict[str, Any]]:
    """Collect Spark rows as independent dictionaries."""
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in frame.collect()]


def _latest(rows: list[dict[str, Any]], identity: tuple[str, ...]) -> list[dict[str, Any]]:
    """Select the latest audit row for each logical identity."""
    selected: dict[tuple[str, ...], dict[str, Any]] = {}
    for row in rows:
        key = tuple(str(row.get(field) or "") for field in identity)
        rank = (str(row.get("_committed_at") or ""), str(row.get("_activity_id") or ""))
        current = selected.get(key)
        current_rank = (str(current.get("_committed_at") or ""), str(current.get("_activity_id") or "")) if current else None
        if current_rank is None or rank > current_rank:
            selected[key] = row
    return [selected[key] for key in sorted(selected)]


def _contract_id(environment_name: str, table_id: str) -> str:
    """Build the stable business identity for one environment/table lifecycle."""
    return contract_lifecycle_id(table_id, environment_name)


def _agreement_version_key(value: Any) -> tuple[int, int, int]:
    """Return the canonical numeric Data Agreement version ordering key."""
    try:
        parts = str(value or "").strip().split(".")
        return tuple(int(parts[index]) if index < len(parts) else 0 for index in range(3))  # type: ignore[return-value]
    except (TypeError, ValueError):
        return (0, 0, 0)


def widget_register_data_contract(*, agreement_id: str | None = None, agreement_version: str | None = None, table_id: str | None = None, approved_usages: list[str] | None = None, target: str = "metadata", schema: str | None = None, spark_session=None, context=None):
    """Create, author, and freeze one versioned governed-table Data Contract.

    Parameters
    ----------
    agreement_id : str, optional
        Saved parent Data Agreement lifecycle identity.
    agreement_version : str, optional
        Exact saved Data Agreement version. When omitted, the widget initially
        selects the latest saved version of ``agreement_id``.
    table_id : str, optional
        Initial active logical Catalogue table identity.
    approved_usages : list of str, optional
        Initial usage subset. Every value must be approved by the Agreement.
    target : str, default="metadata"
        Configured FabricStore target containing FabricOps metadata.
    schema : str, optional
        Metadata Lakehouse schema override.
    spark_session : object, optional
        Spark session override.
    context : object, optional
        FabricOps context, normally established by ``00_env_config``.

    Returns
    -------
    dict
        Mutable state with structured ``review`` and ``warnings`` values,
        ``refresh``, ``save``, and ``freeze`` callables, saved and frozen
        identity/version values, and notebook controls under ``_controls``.

    Raises
    ------
    ValueError
        If a selected Agreement version, table, usage, or metadata JSON value
        is invalid.

    Notes
    -----
    Rendering does not write metadata. ``save`` creates or reopens exactly one
    payload-free ``draft`` row containing the deterministic contract identity,
    version, Agreement identity, and ``table_id``. Enrichment and Guardrail
    authoring can then target that exact draft version. ``freeze`` reads those
    exact-version definitions, assembles the canonical immutable payload, and
    changes the version status to ``frozen``. Runtime Guardrail result tables
    are neither read nor embedded. Historical frozen versions are never
    modified. This workflow requires a configured Microsoft Fabric metadata
    Lakehouse.

    Examples
    --------
    >>> state = widget_register_data_contract(
    ...     agreement_id="agreement-123",
    ...     agreement_version="2",
    ...     table_id="orders",
    ...     approved_usages=["analytics"],
    ...     target="metadata",
    ...     spark_session=spark,
    ... )
    >>> state["save"]()
    >>> state["freeze"]()

    See Also
    --------
    widget_render_data_agreement
    widget_view_catalogue
    widget_enrich_table_metadata

    """
    config, env, resolved = resolve_fabric_context(context=context)
    spark_session = get_spark_session(spark_session)
    runtime_context = {"config": config, "env": env, **(resolved or {})}
    source = {name: _rows(read_lakehouse_table_core(name, target=target, schema=schema, spark_session=spark_session, context=runtime_context)) for name in _SOURCE_TABLES}
    contract_frame = read_lakehouse_table_core(CONTRACT_TABLE, target=target, schema=schema, spark_session=spark_session, context=runtime_context)
    contract_rows = _rows(contract_frame)
    agreements = _latest(source["METADATA_DATA_AGREEMENT"], ("agreement_id", "agreement_version"))
    agreement_options = sorted(
        agreements,
        key=lambda r: (str(r.get("agreement_id") or ""), _agreement_version_key(r.get("agreement_version"))),
    )
    active_table_rows = _latest([r for r in source["METADATA_DATA_CATALOGUE"] if str(r.get("environment_name") or "") == env and r.get("is_active") is not False and (str(r.get("metadata_level") or "").lower() == "table" or not r.get("column_id"))], ("table_id",))
    table_options = sorted({str(r.get("table_id") or "") for r in active_table_rows if r.get("table_id")})
    state: dict[str, Any] = {"environment_name": env, "available_agreements": agreement_options, "available_table_ids": table_options, "agreement_id": agreement_id, "agreement_version": agreement_version, "table_id": table_id, "approved_usages": approved_usages, "review": None, "warnings": [], "saved_contract_id": None, "saved_contract_version": None, "frozen_contract_id": None, "frozen_contract_version": None, "_controls": {}}

    def refresh() -> dict[str, Any] | None:
        selected_table = str(state.get("table_id") or "")
        if not selected_table:
            state["review"], state["warnings"] = None, ["Select one governed table."]
            return None
        if selected_table not in table_options:
            raise ValueError("Select one valid active METADATA_DATA_CATALOGUE table_id.")
        chosen: list[str] = []
        lifecycle_id = _contract_id(env, selected_table)
        versions = [int(r.get("contract_version") or 0) for r in contract_rows if str(r.get("contract_id") or "") == lifecycle_id]
        open_drafts = [
            row for row in contract_rows
            if str(row.get("contract_id") or "") == lifecycle_id
            and str(row.get("status") or "").lower() == "draft"
        ]
        if len(open_drafts) > 1:
            raise RuntimeError(f"Data Contract integrity error: {lifecycle_id!r} has multiple open draft versions.")
        version = int(open_drafts[0]["contract_version"]) if open_drafts else max(versions, default=0) + 1
        review = {
            "contract": {"contract_id": lifecycle_id, "contract_version": version, "status": "draft"},
            "table": {"table_id": selected_table},
        }
        state.update({"approved_usages": chosen, "parent_approved_usages": [], "agreement_id": None, "agreement_version": None, "contract_id": lifecycle_id, "next_contract_version": version, "review": review, "warnings": []})
        return review

    def save() -> dict[str, Any]:
        review = refresh()
        if review is None:
            raise ValueError("Select one active Catalogue table before saving.")
        existing = [
            row for row in contract_rows
            if str(row.get("contract_id") or "") == state["contract_id"]
            and int(row.get("contract_version") or 0) == int(state["next_contract_version"])
        ]
        if existing:
            if str(existing[0].get("status") or "").lower() == "draft":
                state.update(saved_contract_id=existing[0]["contract_id"], saved_contract_version=existing[0]["contract_version"])
                return existing[0]
            raise ValueError("The selected Data Contract version is no longer an open draft.")
        audit = build_runtime_audit_fields(config=config, env=env, runtime_context=runtime_context)
        row = {"contract_id": state["contract_id"], "contract_version": state["next_contract_version"], "agreement_id": None, "agreement_version": None, "table_id": state["table_id"], "environment_name": env, "contract_payload_json": None, "status": "draft", "is_active": False, **audit}
        row = coerce_metadata_row_types(CONTRACT_TABLE, row)
        frame = spark_session.createDataFrame([row], schema=metadata_table_schema_registry()[CONTRACT_TABLE])
        write_lakehouse_table_core(frame, CONTRACT_TABLE, target=target, schema=schema, mode="append", context=runtime_context)
        contract_rows.append(row)
        state.update({"saved_contract_id": row["contract_id"], "saved_contract_version": row["contract_version"]})
        refresh()
        return row

    def freeze() -> dict[str, Any]:
        draft = save()
        if str(draft.get("status") or "").lower() != "draft":
            raise ValueError("Only an open draft Data Contract version can be frozen.")
        result = freeze_contract(
            draft=draft,
            config=config, env=env, spark_session=spark_session,
            context=runtime_context, target=target, schema=schema,
        )
        frozen = result["contract"]
        payload = result["payload"]
        warnings = result["warnings"]
        contract_rows[contract_rows.index(draft)] = frozen
        state.update(review=payload, warnings=warnings, frozen_contract_id=frozen["contract_id"], frozen_contract_version=frozen["contract_version"])
        return frozen

    state["refresh"], state["save"], state["freeze"] = refresh, save, freeze
    refresh()
    try:
        widgets = require_ipywidgets()
    except ModuleNotFoundError:
        return state
    agreement_choices = [
        (f"{r.get('agreement_name') or r['agreement_id']} · v{r['agreement_version']}", f"{r['agreement_id']}\n{r['agreement_version']}")
        for r in agreement_options
    ]
    selected_agreement = (
        f"{state['agreement_id']}\n{state['agreement_version']}"
        if state.get("agreement_id") and state.get("agreement_version")
        else None
    )
    agreement_control = widgets.Dropdown(
        options=agreement_choices,
        value=selected_agreement if selected_agreement in {value for _label, value in agreement_choices} else None,
        **widget_common(widgets, "Data Agreement"),
    )
    table_control = widgets.Dropdown(options=[("Select one table", ""), *[(value, value) for value in table_options]], value=state.get("table_id") or "", **widget_common(widgets, "Governed table"))
    usage_box = widgets.SelectMultiple(options=state.get("parent_approved_usages", []), value=tuple(state.get("approved_usages") or []), **widget_common(widgets, "Approved usages"))
    review_html, warning_html, status = widgets.HTML(), widgets.HTML(), status_message(widgets)
    save_button = widgets.Button(description="Save draft Data Contract", button_style="primary")
    freeze_button = widgets.Button(description="Freeze Data Contract", button_style="success")
    synchronizing = False

    def render(*_args: Any) -> None:
        nonlocal synchronizing
        if synchronizing:
            return
        if agreement_control.value:
            state["agreement_id"], state["agreement_version"] = agreement_control.value.split("\n", 1)
        visible_usages = list(usage_box.value)
        selected_agreement_row = next(
            (
                row for row in agreement_options
                if str(row.get("agreement_id") or "") == str(state.get("agreement_id") or "")
                and str(row.get("agreement_version") or "") == str(state.get("agreement_version") or "")
            ),
            None,
        )
        allowed_before_refresh = (
            parse_approved_usages(selected_agreement_row.get("approved_usage_json"))
            if selected_agreement_row else []
        )
        state["table_id"] = table_control.value or None
        state["approved_usages"] = [value for value in visible_usages if value in allowed_before_refresh]
        try:
            refresh()
            allowed = list(state.get("parent_approved_usages") or [])
            selected = tuple(value for value in state.get("approved_usages") or [] if value in allowed)
            synchronizing = True
            usage_box.options = allowed
            usage_box.value = selected
            synchronizing = False
            review_html.value = "<pre>" + html.escape(json.dumps(state["review"], indent=2, default=str)) + "</pre>" if state["review"] else "<i>Select an Agreement and table to review governance context.</i>"
            warning_html.value = "<br>".join(html.escape(v) for v in state["warnings"])
        except ValueError as exc:
            synchronizing = False
            status.value = html.escape(str(exc))
    agreement_control.observe(render, names="value"); table_control.observe(render, names="value"); usage_box.observe(render, names="value")
    render()
    def on_save(_button: Any) -> None:
        try:
            saved = save(); status.value = f"Saved draft {html.escape(saved['contract_id'])} version {saved['contract_version']}."
        except ValueError as exc:
            status.value = html.escape(str(exc))
    save_button.on_click(on_save)
    def on_freeze(_button: Any) -> None:
        try:
            frozen = freeze(); status.value = f"Frozen {html.escape(frozen['contract_id'])} version {frozen['contract_version']}."
        except (ValueError, RuntimeError) as exc:
            status.value = html.escape(str(exc))
    freeze_button.on_click(on_freeze)
    page = form_page(widgets, title="Prepare Data Contract", description="Create a draft, author its governance definition, then freeze it for testing and activation.", children=[form_section(widgets, title="1. Agreement and table", children=[agreement_control, table_control]), form_section(widgets, title="2. Approved usage", children=[usage_box]), form_section(widgets, title="3. Draft contract", children=[warning_html, review_html]), action_row(widgets, [save_button, freeze_button]), status])
    state["_controls"] = {"agreement": agreement_control, "table": table_control, "approved_usages": usage_box, "save": save_button, "freeze": freeze_button, "review": review_html, "warnings": warning_html, "status": status, "page": page}
    from IPython import display as ip
    ip.display(page)
    return state
