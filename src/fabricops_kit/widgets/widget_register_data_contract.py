"""Public widget entrypoint for versioned, one-table Data Contracts."""

from __future__ import annotations

from datetime import date, datetime
import html
import json
from typing import Any
import uuid

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session, read_lakehouse_table_core, write_lakehouse_table_core
from fabricops_kit.pipeline.shared import validated_processing
from fabricops_kit.widgets.shared import action_row, form_page, form_section, require_ipywidgets, status_message, widget_common

CONTRACT_TABLE = "METADATA_DATA_CONTRACT"
_SOURCE_TABLES = (
    "METADATA_DATA_AGREEMENT", "METADATA_DATA_STEWARD", "METADATA_DATA_CATALOGUE",
    "METADATA_ENRICHMENT", "METADATA_GUARDRAIL",
)
_CONTRACT_NAMESPACE = uuid.UUID("8383c7ec-23f5-4ad8-92ea-0871045c310c")


def _rows(frame: Any) -> list[dict[str, Any]]:
    """Collect Spark rows as independent dictionaries."""
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in frame.collect()]


def _json_value(value: Any, *, field: str, default: Any) -> Any:
    """Parse a JSON metadata value with an actionable field error."""
    if value in (None, ""):
        return default
    try:
        return json.loads(str(value))
    except (TypeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{field} must contain valid JSON.") from exc


def _approved_usages(value: Any) -> list[str]:
    """Return a normalized approved-usage list."""
    parsed = _json_value(value, field="approved_usage_json", default=[])
    if not isinstance(parsed, list) or any(not isinstance(item, str) for item in parsed):
        raise ValueError("approved_usage_json must be a JSON list of strings.")
    return list(dict.fromkeys(item.strip() for item in parsed if item.strip()))


def _selected_usages(selected: Any, parent: list[str]) -> list[str]:
    """Validate and order the contract usage subset by its parent Agreement."""
    values = list(dict.fromkeys(str(item).strip() for item in (selected or []) if str(item).strip()))
    invalid = sorted(set(values) - set(parent))
    if invalid:
        raise ValueError("Data Contract approved usages must be a subset of the parent Data Agreement approved usages. Invalid value(s): " + ", ".join(invalid))
    return [item for item in parent if item in values]


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


def _json_safe(value: Any) -> Any:
    """Convert Spark-compatible scalar values into JSON-compatible values."""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _fields(row: dict[str, Any], names: tuple[str, ...]) -> dict[str, Any]:
    return {name: _json_safe(row.get(name)) for name in names}


def _contract_id(agreement_id: str, table_id: str) -> str:
    """Build the stable business identity for one Agreement lifecycle/table."""
    return str(uuid.uuid5(_CONTRACT_NAMESPACE, f"{agreement_id.strip()}\n{table_id.strip()}"))


def _agreement_version_key(value: Any) -> tuple[int, int, int]:
    """Return the canonical numeric Data Agreement version ordering key."""
    try:
        parts = str(value or "").strip().split(".")
        return tuple(int(parts[index]) if index < len(parts) else 0 for index in range(3))  # type: ignore[return-value]
    except (TypeError, ValueError):
        return (0, 0, 0)


def _assemble_payload(*, contract_id: str, contract_version: int, agreement: dict[str, Any], table_id: str, usages: list[str], tables: dict[str, list[dict[str, Any]]], environment_name: str) -> tuple[dict[str, Any], list[str]]:
    """Assemble a deterministic, self-contained FabricOps contract document."""
    catalogue = [r for r in tables["METADATA_DATA_CATALOGUE"] if str(r.get("table_id") or "") == table_id and str(r.get("environment_name") or "") == environment_name and r.get("is_active") is not False]
    current = _latest(catalogue, ("table_id", "column_id"))
    table_rows = [r for r in current if str(r.get("metadata_level") or "").lower() == "table" or not r.get("column_id")]
    if not table_rows:
        raise ValueError("Select one valid active METADATA_DATA_CATALOGUE table_id.")
    table = table_rows[-1]
    columns = [r for r in current if r.get("column_id")]
    column_docs = [_fields(r, ("column_id", "column_name", "data_type")) for r in columns]
    incomplete_columns = [
        str(row.get("column_name") or row.get("column_id") or "<blank>")
        for row in column_docs
        if any(not str(row.get(name) or "").strip() for name in ("column_id", "column_name", "data_type"))
    ]
    if incomplete_columns:
        raise ValueError(
            "Active METADATA_DATA_CATALOGUE columns must define column_id, column_name, and data_type before a Data Contract can be assembled: "
            + ", ".join(incomplete_columns)
        )
    column_names = [str(row["column_name"]).strip() for row in column_docs]
    duplicate_names = sorted({name for name in column_names if column_names.count(name) > 1})
    if duplicate_names:
        raise ValueError("Active METADATA_DATA_CATALOGUE columns contain duplicate column_name values: " + ", ".join(duplicate_names))
    enrichment = _latest([r for r in tables["METADATA_ENRICHMENT"] if str(r.get("table_id") or "") == table_id and str(r.get("environment_name") or "") == environment_name], ("enrichment_id",))
    enrichment_docs = [_fields(r, ("enrichment_id", "table_id", "column_id", "enrichment_level", "enrichment_type", "value")) for r in enrichment]
    guardrails = _latest([r for r in tables["METADATA_GUARDRAIL"] if str(r.get("table_id") or "") == table_id and str(r.get("environment_name") or "") == environment_name], ("guardrail_rule_id",))
    guardrail_docs = []
    for row in guardrails:
        if row.get("is_active") is not True:
            continue
        item = _fields(row, ("guardrail_rule_id", "guardrail_version", "table_id", "column_id", "guardrail_type", "rule_id", "rule_type", "severity"))
        rule_parameters = _json_value(row.get("rule_parameters_json"), field="rule_parameters_json", default={})
        if not isinstance(rule_parameters, dict):
            raise ValueError("rule_parameters_json must contain a JSON object.")
        if str(row.get("guardrail_type") or "").strip().lower() == "schema":
            rule_parameters = {
                name: value for name, value in rule_parameters.items()
                if name not in {"columns", "data_types", "selected_columns", "expected_data_types"}
            }
        item["rule_parameters"] = rule_parameters
        guardrail_docs.append(item)
    steward_ids = {str(agreement.get("provider_steward_id") or ""), str(agreement.get("recipient_steward_id") or "")}
    stewards = _latest([r for r in tables["METADATA_DATA_STEWARD"] if str(r.get("steward_id") or "") in steward_ids and r.get("is_active") is not False], ("steward_id",))
    steward_docs = [_fields(r, ("steward_id", "steward_name", "steward_role", "contact")) for r in stewards]
    agreement_doc = _fields(agreement, ("agreement_id", "agreement_version", "agreement_name", "domain", "business_purpose", "provider_steward_id", "recipient_steward_id", "start_date", "expiry_date"))
    agreement_doc["approved_usages"] = _approved_usages(agreement.get("approved_usage_json"))
    parameters = _json_value(
        table.get("load_strategy_parameters_json"), field="load_strategy_parameters_json", default={},
    )
    if not isinstance(parameters, dict):
        raise ValueError("Catalogue load_strategy_parameters_json must contain a JSON object.")
    try:
        processing = validated_processing({**parameters, "load_strategy": table.get("load_strategy")})
    except ValueError as exc:
        raise ValueError(f"Catalogue processing for table_id {table_id!r} is incomplete or invalid: {exc}") from exc
    payload = {
        "contract": {"contract_id": contract_id, "contract_version": contract_version, "status": "draft"},
        "agreement": agreement_doc,
        "stewards": steward_docs,
        "table": {
            **_fields(table, ("table_id", "environment_name", "store_type", "layer", "schema_name", "table_name")),
            "columns": column_docs,
            "processing": processing,
        },
        "enrichment": {"table": [r for r in enrichment_docs if not r.get("column_id")], "columns": [r for r in enrichment_docs if r.get("column_id")]},
        "guardrails": guardrail_docs,
        "approved_usages": usages,
    }
    warnings = []
    if not any(r.get("enrichment_type") == "description" and not r.get("column_id") for r in enrichment_docs):
        warnings.append("Table description is missing.")
    described = {str(r.get("column_id")) for r in enrichment_docs if r.get("enrichment_type") == "description"}
    if any(str(r.get("column_id")) not in described for r in column_docs):
        warnings.append("One or more column descriptions are missing.")
    if not guardrail_docs:
        warnings.append("No active Guardrails are configured.")
    return payload, warnings


def widget_register_data_contract(*, agreement_id: str | None = None, agreement_version: str | None = None, table_id: str | None = None, approved_usages: list[str] | None = None, target: str = "metadata", schema: str | None = None, spark_session=None, context=None):
    """Review and save one immutable, versioned governed-table Data Contract.

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
        ``refresh`` and ``save`` callables, saved identity/version values, and
        notebook controls under ``_controls``.

    Raises
    ------
    ValueError
        If a selected Agreement version, table, usage, or metadata JSON value
        is invalid.

    Notes
    -----
    Rendering does not write metadata. Each explicit save appends exactly one
    ``draft`` row with ``is_active=False`` and the next version of a stable
    contract identity derived from the Agreement lifecycle and ``table_id``.
    The canonical payload freezes Agreement and steward context, current active
    Catalogue structure and processing, current enrichment, active Guardrail expectations,
    and the selected approved-usage subset. Runtime Guardrail result tables are
    neither read nor embedded. Historical contract versions are never updated.
    This workflow does not submit, approve, promote, export, or enforce a
    contract and requires a configured Microsoft Fabric metadata Lakehouse.

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
    state: dict[str, Any] = {"environment_name": env, "available_agreements": agreement_options, "available_table_ids": table_options, "agreement_id": agreement_id, "agreement_version": agreement_version, "table_id": table_id, "approved_usages": approved_usages, "review": None, "warnings": [], "saved_contract_id": None, "saved_contract_version": None, "_controls": {}}

    def refresh() -> dict[str, Any] | None:
        matches = [r for r in agreement_options if str(r.get("agreement_id") or "") == str(state.get("agreement_id") or "")]
        if not matches:
            state["review"], state["warnings"] = None, ["Select a saved Data Agreement."]
            return None
        selected_version = str(state.get("agreement_version") or "")
        agreement = next(
            (r for r in matches if str(r.get("agreement_version") or "") == selected_version),
            max(matches, key=lambda r: _agreement_version_key(r.get("agreement_version"))) if not selected_version else None,
        )
        if agreement is None:
            raise ValueError("Select an exact saved Data Agreement version.")
        state["agreement_version"] = str(agreement["agreement_version"])
        selected_table = str(state.get("table_id") or "")
        if not selected_table:
            state["review"], state["warnings"] = None, ["Select one governed table."]
            return None
        if selected_table not in table_options:
            raise ValueError("Select one valid active METADATA_DATA_CATALOGUE table_id.")
        parent = _approved_usages(agreement.get("approved_usage_json"))
        chosen = _selected_usages(state.get("approved_usages") if state.get("approved_usages") is not None else parent, parent)
        lifecycle_id = _contract_id(str(agreement["agreement_id"]), selected_table)
        versions = [int(r.get("contract_version") or 0) for r in contract_rows if str(r.get("contract_id") or "") == lifecycle_id]
        payload, warnings = _assemble_payload(contract_id=lifecycle_id, contract_version=max(versions, default=0) + 1, agreement=agreement, table_id=selected_table, usages=chosen, tables=source, environment_name=env)
        state.update({"approved_usages": chosen, "parent_approved_usages": parent, "contract_id": lifecycle_id, "next_contract_version": payload["contract"]["contract_version"], "review": payload, "warnings": warnings})
        return payload

    def save() -> dict[str, Any]:
        payload = refresh()
        if payload is None:
            raise ValueError("Select a saved Data Agreement version and one active Catalogue table before saving.")
        audit = build_runtime_audit_fields(config=config, env=env, runtime_context=runtime_context)
        row = {"contract_id": state["contract_id"], "contract_version": state["next_contract_version"], "agreement_id": state["agreement_id"], "agreement_version": state["agreement_version"], "table_id": state["table_id"], "contract_payload_json": json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False), "status": "draft", "is_active": False, **audit}
        row = coerce_metadata_row_types(CONTRACT_TABLE, row)
        frame = spark_session.createDataFrame([row], schema=metadata_table_schema_registry()[CONTRACT_TABLE])
        write_lakehouse_table_core(frame, CONTRACT_TABLE, target=target, schema=schema, mode="append", context=runtime_context)
        contract_rows.append(row)
        state.update({"saved_contract_id": row["contract_id"], "saved_contract_version": row["contract_version"]})
        refresh()
        return row

    state["refresh"], state["save"] = refresh, save
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
            _approved_usages(selected_agreement_row.get("approved_usage_json"))
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
    page = form_page(widgets, title="Prepare Data Contract", description="Review and freeze one governed table definition.", children=[form_section(widgets, title="1. Agreement and table", children=[agreement_control, table_control]), form_section(widgets, title="2. Approved usage", children=[usage_box]), form_section(widgets, title="3. Governance review", children=[warning_html, review_html]), action_row(widgets, [save_button]), status])
    state["_controls"] = {"agreement": agreement_control, "table": table_control, "approved_usages": usage_box, "save": save_button, "review": review_html, "warnings": warning_html, "status": status, "page": page}
    from IPython import display as ip
    ip.display(page)
    return state
