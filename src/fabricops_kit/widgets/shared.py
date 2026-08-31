"""Shared widget rendering helpers for FabricOps notebook widgets."""

from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field as dataclass_field
from datetime import date, datetime, timezone
import hashlib
import json
from typing import Any, Iterable, Mapping
import uuid

from fabricops_kit.config import shared as config_shared
from fabricops_kit.io.shared import (
    configured_lakehouse_schema,
    read_lakehouse_table_core,
    resolve_configured_lakehouse_table,
    write_lakehouse_table_core,
)
from fabricops_kit.config.audit import _audit_timestamp_value, _resolve_action_by, build_runtime_audit_fields
from fabricops_kit.config.metadata_keys import _build_dq_rule_key
from fabricops_kit.config.metadata_schemas import (
    CANONICAL_METADATA_TABLES,
    coerce_metadata_row_types,
    metadata_table_schema_registry,
)
from fabricops_kit.pipeline.shared import DQ_RULE_TYPES


_WIDGET_STYLE = {"description_width": "initial"}
_WIDGET_FIELD_MIN_WIDTH = "0"
_WIDGET_FIELD_WIDTH = "100%"
_TEXTAREA_HEIGHT = "80px"
_AUTHORING_PANE_HEIGHT = "560px"
_STATUS_MIN_HEIGHT = "32px"

DATA_CONTRACT_TABLE = "METADATA_DATA_CONTRACT"


def parse_data_contract_payload(row: Mapping[str, Any]) -> dict[str, Any]:
    """Parse and validate the immutable identity in one contract payload."""
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


def _contract_activation_changes(rows: list[dict[str, Any]], selected: dict[str, Any]) -> list[dict[str, Any]]:
    """Return lifecycle-only mutations for one selected contract version."""
    changes = [
        {"contract_id": prior["contract_id"], "contract_version": int(prior["contract_version"]), "status": "superseded", "is_active": False}
        for prior in rows
        if str(prior.get("table_id") or "") == str(selected.get("table_id") or "")
        and prior.get("is_active") is True
        and not (
            str(prior.get("contract_id") or "") == str(selected.get("contract_id") or "")
            and int(prior.get("contract_version") or 0) == int(selected.get("contract_version") or 0)
        )
    ]
    if selected.get("is_active") is not True or str(selected.get("status") or "").lower() != "active":
        changes.append({"contract_id": selected["contract_id"], "contract_version": int(selected["contract_version"]), "status": "active", "is_active": True})
    return changes


def activate_contract_version(
    *,
    config,
    env: str,
    table_id: str,
    contract_id: str,
    contract_version: int,
    target: str = "metadata",
    schema: str | None = None,
    spark_session=None,
    context=None,
) -> dict[str, Any]:
    """Activate one frozen version and supersede the prior active version."""
    frame = read_lakehouse_table_core(
        DATA_CONTRACT_TABLE, target=target, schema=schema,
        spark_session=spark_session, context=context,
    )
    rows = [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in frame.collect()]
    selected = [
        row for row in rows
        if str(row.get("contract_id") or "") == contract_id
        and int(row.get("contract_version") or 0) == int(contract_version)
    ]
    if not selected:
        raise ValueError("Selected Data Contract version does not exist.")
    row = selected[0]
    if str(row.get("table_id") or "") != table_id:
        raise ValueError("Selected Data Contract version does not belong to the selected table_id.")
    if str(row.get("status") or "").lower() == "rejected":
        raise ValueError("Rejected Data Contracts cannot be manually activated. Register a corrected version first.")
    parse_data_contract_payload(row)
    active = [
        candidate for candidate in rows
        if str(candidate.get("table_id") or "") == table_id
        and candidate.get("is_active") is True
    ]
    if len(active) > 1:
        raise RuntimeError(f"Data Contract integrity error: {table_id!r} has multiple active versions.")
    changes = _contract_activation_changes(rows, row)
    if not changes:
        return {"changed": False, "contract_id": contract_id, "contract_version": int(contract_version), "changes": []}
    try:
        from delta.tables import DeltaTable
    except Exception as exc:  # pragma: no cover - Fabric runtime dependency
        raise RuntimeError("Delta Lake support is required to activate a Data Contract.") from exc
    source = spark_session.createDataFrame(changes)
    _store, _table, _schema, path = resolve_configured_lakehouse_table(
        target, DATA_CONTRACT_TABLE,
        schema or configured_lakehouse_schema(config, env, target), context=context,
    )
    (
        DeltaTable.forPath(spark_session, path).alias("target")
        .merge(source.alias("source"), "target.contract_id = source.contract_id AND target.contract_version = source.contract_version")
        .whenMatchedUpdate(set={"status": "source.status", "is_active": "source.is_active"})
        .execute()
    )
    return {"changed": True, "contract_id": contract_id, "contract_version": int(contract_version), "changes": changes}


def require_ipywidgets():
    """Return ipywidgets or raise an actionable optional-dependency error."""
    try:
        import ipywidgets as widgets
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The FabricOps widget feature requires the 'dq-review' extra. "
            'Install with: pip install "fabricops-kit[dq-review]"'
        ) from exc
    return widgets


def widget_common(widgets_module: Any, description: str, *, textarea: bool = False) -> dict[str, Any]:
    """Return common style and layout keyword arguments for form controls."""
    common: dict[str, Any] = {"description": description, "style": dict(_WIDGET_STYLE)}
    layout_class = getattr(widgets_module, "Layout", None)
    if layout_class is not None:
        kwargs = {"width": _WIDGET_FIELD_WIDTH, "min_width": _WIDGET_FIELD_MIN_WIDTH, "max_width": "100%"}
        if textarea:
            kwargs["height"] = _TEXTAREA_HEIGHT
        common["layout"] = layout_class(**kwargs)
    return common


def form_page(widgets: Any, *, title: str, description: str, children: Iterable[Any]) -> Any:
    """Compose a full-width widget form with a consistent page header."""
    field_style = (
        "<style>"
        ".fabricops-form .widget-inline-hbox{display:flex;flex-direction:column;align-items:stretch;"
        "min-width:0;max-width:100%;}"
        ".fabricops-form .widget-inline-hbox>.widget-label{width:100%;margin:0 0 6px;flex:none;}"
        ".fabricops-form .widget-label{display:block;width:100%;max-width:100%;}"
        ".fabricops-form .widget-text input,.fabricops-form .widget-dropdown select,"
        ".fabricops-form .widget-textarea textarea{width:100%;min-width:0;max-width:100%;box-sizing:border-box;}"
        ".fabricops-form .widget-hbox{min-width:0;max-width:100%;}"
        "</style>"
    )
    header = widgets.HTML(
        value=(
            field_style
            + '<div style="background:#0f6cbd;color:#fff;padding:16px 20px;'
            'border-radius:8px;">'
            f'<div style="font-size:21px;font-weight:600;line-height:1.3;">{_html_escape(title)}</div>'
            f'<div style="font-size:13px;line-height:1.4;margin-top:3px;opacity:.9;">{_html_escape(description)}</div>'
            "</div>"
        ),
        layout=widgets.Layout(width="100%", height="auto", overflow="visible"),
    )
    page = widgets.VBox(
        [header, *children],
        layout=widgets.Layout(width="100%", height="auto", overflow="visible", gap="12px"),
    )
    add_class = getattr(page, "add_class", None)
    if callable(add_class):
        add_class("fabricops-form")
    return page


def status_message(widgets: Any) -> Any:
    """Create a full-width message region that reserves space as text changes."""
    message = widgets.HTML(value="")
    message.layout = widgets.Layout(
        width="100%",
        min_width="0",
        max_width="100%",
        min_height=_STATUS_MIN_HEIGHT,
        height="auto",
        overflow="visible",
    )
    return message


def bounded_region(widgets: Any, children: Iterable[Any], *, height: str = _AUTHORING_PANE_HEIGHT) -> Any:
    """Contain long authoring content in a stable, internally scrolling region."""
    return widgets.VBox(
        list(children),
        layout=widgets.Layout(
            width="100%",
            min_width="0",
            max_width="100%",
            height=height,
            overflow="auto",
            gap="8px",
        ),
    )


def authoring_pane(widgets: Any, *, title: str, children: Iterable[Any]) -> Any:
    """Compose one named, bounded pane in a landscape authoring workspace."""
    heading = widgets.HTML(
        value=(
            '<div style="color:#0f548c;font-size:15px;font-weight:600;'
            f'border-bottom:1px solid #d7e7f5;padding-bottom:6px;">{_html_escape(title)}</div>'
        )
    )
    return bounded_region(widgets, [heading, *children])


def authoring_workspace(
    widgets: Any,
    *,
    target: Iterable[Any],
    selection: Iterable[Any],
    configuration: Iterable[Any],
    titles: tuple[str, str, str] = ("Target", "Selection", "Configuration"),
) -> Any:
    """Compose a stable full-width 25/30/45 landscape authoring workspace."""
    panes = [
        authoring_pane(widgets, title=title, children=children)
        for title, children in zip(titles, (target, selection, configuration), strict=True)
    ]
    workspace = widgets.GridBox(
        panes,
        layout=widgets.Layout(
            width="100%",
            min_width="0",
            max_width="100%",
            grid_template_columns="minmax(0, 25fr) minmax(0, 30fr) minmax(0, 45fr)",
            grid_gap="12px",
            align_items="stretch",
            overflow="visible",
        ),
    )
    add_class = getattr(workspace, "add_class", None)
    if callable(add_class):
        add_class("fabricops-authoring-workspace")
    return workspace


def preview_region(widgets: Any, preview: Any, *, height: str = "180px") -> Any:
    """Apply a bounded, readable layout to a canonical preview control."""
    preview.layout = widgets.Layout(
        width="100%", min_width="0", max_width="100%", height=height, overflow="auto"
    )
    return preview


def form_section(widgets: Any, *, title: str, children: Iterable[Any]) -> Any:
    """Group naturally expanding form content under a visible heading."""
    heading = widgets.HTML(
        value=(
            '<div style="color:#0f548c;font-size:16px;font-weight:600;'
            f'border-bottom:1px solid #d7e7f5;padding:0 0 6px 0;">{_html_escape(title)}</div>'
        ),
        layout=widgets.Layout(width="100%", height="auto", overflow="visible"),
    )
    return widgets.VBox(
        [heading, *children],
        layout=widgets.Layout(
            width="100%", height="auto", overflow="visible", border="1px solid #d7e7f5", padding="12px", gap="8px"
        ),
    )


def form_grid(widgets: Any, children: Iterable[Any]) -> Any:
    """Lay out form controls in responsive, wrapping columns."""
    return widgets.GridBox(
        list(children),
        layout=widgets.Layout(
            width="100%",
            height="auto",
            overflow="visible",
            grid_template_columns="repeat(auto-fit, minmax(min(100%, 280px), 1fr))",
            grid_gap="16px 24px",
        ),
    )


def checkbox_group(widgets: Any, *, label: str, checkboxes: Iterable[Any]) -> Any:
    """Render a labelled, naturally expanding checkbox option group."""
    label_widget = widgets.HTML(value=f"<b>{_html_escape(label)}</b>")
    options = widgets.GridBox(
        list(checkboxes),
        layout=widgets.Layout(
            width="100%",
            height="auto",
            overflow="visible",
            grid_template_columns="repeat(auto-fit, minmax(140px, 1fr))",
            grid_gap="6px 12px",
        ),
    )
    return widgets.VBox(
        [label_widget, options], layout=widgets.Layout(width="100%", height="auto", overflow="visible", gap="4px")
    )


def action_row(widgets: Any, controls: Iterable[Any], *, consequence: Any | None = None) -> Any:
    """Position form actions and an optional consequence summary in a footer row."""
    children = ([consequence] if consequence is not None else []) + list(controls)
    return widgets.HBox(
        children,
        layout=widgets.Layout(
            width="100%",
            height="auto",
            overflow="visible",
            justify_content="flex-end",
            align_items="center",
            gap="10px",
        ),
    )


def resolve_agreement_details(agreement: dict[str, Any] | None) -> tuple[str, str]:
    """Resolve a canonical agreement ID and label from agreement widget state."""
    supplied = agreement or {}
    row: dict[str, Any] = supplied
    resolved = str(supplied.get("agreement_id") or "").strip()
    if not resolved:
        selected = supplied.get("existing_record")
        selected_id = str(getattr(selected, "value", "") or "").strip()
        row = (supplied.get("existing_records_by_id") or {}).get(selected_id, {})
        resolved = str(row.get("agreement_id") or selected_id).strip()
    label = str(row.get("agreement_name") or supplied.get("agreement_name") or resolved).strip()
    return resolved, label


def _html_escape(value: Any) -> str:
    """Return display-safe HTML text for notebook context snippets."""
    import html

    return html.escape(str(value or ""))


def render_searchable_selector(
    *,
    widgets: Any,
    label: str,
    rows: list[dict[str, Any]],
    label_fn: Callable[[dict[str, Any]], str],
    value_fn: Callable[[dict[str, Any]], str],
    placeholder: str = "Search...",
    max_results: int = 25,
    search_fields: list[str] | None = None,
    context_fields: list[tuple[str, str]] | None = None,
    empty_label: str | None = None,
    selected_value: str | None = None,
    search_label: str | None = None,
) -> dict[str, Any]:
    """Render a table-backed selector with search and stable-value tracking."""
    search = widgets.Text(
        value="", placeholder=placeholder, **widget_common(widgets, search_label or f"Search {label}")
    )
    selector = widgets.Select(options=[], **widget_common(widgets, label))
    context = widgets.HTML(value="")
    lookup: dict[str, dict[str, Any]] = {}
    indexed_rows: list[dict[str, Any]] = []

    def _set_rows(new_rows: list[dict[str, Any]]) -> None:
        lookup.clear()
        indexed_rows.clear()
        for row in new_rows:
            value = str(value_fn(row) or "")
            if not value:
                continue
            lookup[value] = row
            indexed_rows.append(row)

    def _matches(row: dict[str, Any], query: str) -> bool:
        if not query:
            return True
        fields = search_fields or list(row)
        haystack = " ".join(str(row.get(field, "")) for field in fields).lower()
        return query.lower() in haystack

    def _context_html(row: dict[str, Any] | None) -> str:
        if not row or not context_fields:
            return ""
        parts = [
            f"<b>{_html_escape(field_label)}:</b> {_html_escape(row.get(field, ''))}"
            for field, field_label in context_fields
        ]
        return "<br>".join(parts)

    def _refresh_options(*_: Any) -> None:
        current = str(selector.value or selected_value or "")
        query = str(search.value or "").strip()
        filtered = [row for row in indexed_rows if _matches(row, query)][:max_results]
        options = [(label_fn(row), str(value_fn(row) or "")) for row in filtered]
        if empty_label is not None:
            options = [(empty_label, ""), *options]
        selector.options = options
        values = [value for _, value in options]
        selector.value = current if current in values else (values[0] if values else None)
        context.value = _context_html(lookup.get(str(selector.value or "")))

    def _on_select(change: dict[str, Any]) -> None:
        if change.get("name") == "value":
            context.value = _context_html(lookup.get(str(change.get("new") or "")))

    def _refresh_rows(new_rows: list[dict[str, Any]], selected: str | None = None) -> None:
        nonlocal selected_value
        selected_value = selected
        _set_rows(new_rows)
        _refresh_options()

    search.observe(lambda change: _refresh_options() if change.get("name") == "value" else None, names="value")
    selector.observe(_on_select, names="value")
    _set_rows(rows)
    _refresh_options()
    selector.refresh_rows = _refresh_rows
    container = widgets.VBox(
        [search, selector, context], layout=widgets.Layout(width="100%", height="auto", overflow="visible", gap="6px")
    )
    return {"container": container, "search": search, "selector": selector, "context": context, "rows_by_value": lookup}


def render_custom_fields(config: list[dict[str, Any]] | dict[str, Any], *, values: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render organization-specific custom fields from normalized config."""
    widgets = require_ipywidgets()
    fields = config.get("custom_fields", []) if isinstance(config, dict) else config
    rendered: dict[str, Any] = {}
    values = values or {}
    for field in fields or []:
        key = str(field.get("key") or "").strip()
        if not key:
            continue
        label = str(field.get("label") or key.replace("_", " ").title())
        field_type = str(field.get("type") or "text").lower()
        default = values.get(key, field.get("default", ""))
        common = widget_common(widgets, label, textarea=field_type == "textarea")
        if field_type == "textarea":
            rendered[key] = widgets.Textarea(value=str(default or ""), **common)
        elif field_type == "dropdown":
            options = field.get("options", []) or []
            rendered[key] = widgets.Dropdown(options=options, value=default if default in options else (options[0] if options else None), **common)
        elif field_type == "checkbox":
            rendered[key] = widgets.Checkbox(value=bool(default), **common)
        else:
            rendered[key] = widgets.Text(value=str(default or ""), **common)
    return rendered


def standard_widget(field: str, value: Any = "", *, options: list[Any] | None = None) -> Any:
    """Render a standard widget control for a configured field name."""
    widgets = require_ipywidgets()
    description = field.replace("_", " ").title()
    if options is not None:
        option_values = [
            option[1] if isinstance(option, tuple) and len(option) == 2 else option
            for option in options
        ]
        default_value = value if value in option_values else (option_values[0] if option_values else None)
        return widgets.Dropdown(options=options, value=default_value, **widget_common(widgets, description))
    if field.endswith("_date") or field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
        return widgets.DatePicker(value=date.fromisoformat(str(value)[:10]) if value else None, **widget_common(widgets, description))
    if field == "is_active":
        return widgets.Checkbox(value=True if value == "" else str(value).strip().lower() in {"1", "true", "yes", "y"}, **widget_common(widgets, description))
    if field in {"business_purpose"}:
        return widgets.Textarea(value=str(value or ""), **widget_common(widgets, description, textarea=True))
    return widgets.Text(value=str(value or ""), **widget_common(widgets, description))


# Widget-owned helper implementations migrated from data_agreement.py.
DATA_AGREEMENT_TABLE = "METADATA_DATA_AGREEMENT"
DATA_STEWARD_TABLE = "METADATA_DATA_STEWARD"
STANDARD_RUNTIME_AUDIT_COLUMNS = ["_committed_by", "_committed_at", "_workspace_id", "_workspace_name", "_notebook_id", "_notebook_name", "_metadata_lakehouse_name", "_activity_id"]
DATA_STEWARD_VISIBLE_FIELDS = ["steward_name", "steward_role", "contact"]
DATA_STEWARD_BACKEND_FIELDS = ["steward_id", *DATA_STEWARD_VISIBLE_FIELDS, "is_active"]
DATA_AGREEMENT_VISIBLE_FIELDS = ["agreement_name", "domain", "provider_steward_id", "recipient_steward_id", "start_date", "expiry_date", "business_purpose"]
DATA_AGREEMENT_GENERATED_FIELDS = ["agreement_id", "agreement_version"]
DATA_STEWARD_FIELDS = DATA_STEWARD_BACKEND_FIELDS + ["custom_fields_json"] + STANDARD_RUNTIME_AUDIT_COLUMNS
DATA_AGREEMENT_FIELDS = DATA_AGREEMENT_GENERATED_FIELDS + DATA_AGREEMENT_VISIBLE_FIELDS + ["supporting_documents_json", "approved_usage_json", "custom_fields_json"] + STANDARD_RUNTIME_AUDIT_COLUMNS
WIDGET_CONFIG_DEFAULTS = {"data_steward_widget": {"visible_columns": DATA_STEWARD_VISIBLE_FIELDS, "custom_fields": []}, "data_agreement_widget": {"visible_columns": DATA_AGREEMENT_VISIBLE_FIELDS, "approved_usage_options": ["internal cross domain", "internal single domain", "research", "external"], "custom_fields": []}}
FIELD_LABELS = {"steward_id": "Steward ID", "provider_steward_id": "Provider Data Steward", "recipient_steward_id": "Recipient Data Steward", "steward_name": "Steward Name", "steward_role": "Steward Role", "contact": "Contact", "effective_from": "Effective From", "effective_to": "Effective To", "is_active": "Is Active", "agreement_name": "Agreement Name", "domain": "Domain", "start_date": "Start Date", "expiry_date": "Expiry Date", "business_purpose": "Business Purpose"}
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
PROFILED_TABLE = "METADATA_DATA_PROFILED"
ENRICHMENT_TABLE = "METADATA_ENRICHMENT"
GUARDRAIL_TABLE = "METADATA_GUARDRAIL"
GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"
GUARDRAIL_TYPES = ["schema", "freshness", "profile_behavior", "dq"]
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"
DATA_ACCESS_TABLE = "METADATA_DATA_ACCESS"
SENSITIVITY_LABELS = ["classified", "restricted", "public"]
PERSONAL_DATA_CLASSIFICATIONS = ["direct PII", "indirect PII", "none"]


@dataclass
class PipelineRunContext:
    """Internal runtime context resolved for guided notebook defaults."""

    run_id: str
    pipeline_started_at: str
    pipeline_name: str
    spark_session: Any = None
    metadata_schema: str = ""
    notebook_type: str = "02_pipeline"
    agreement_id: str = ""
    agreement_version: str = ""
    agreement: dict[str, Any] = dataclass_field(default_factory=dict)
    context: dict[str, Any] | None = None
    read_only: bool = False
    source_definitions: dict[str, dict[str, Any]] = dataclass_field(default_factory=dict)
    target_definitions: dict[str, dict[str, Any]] = dataclass_field(default_factory=dict)


_ACTIVE_PIPELINE_CONTEXT: PipelineRunContext | None = None


def pipeline_active_context() -> PipelineRunContext | None:
    """Return the active pipeline context when one has been started."""
    return _ACTIVE_PIPELINE_CONTEXT


_SELECTED_AGREEMENT: dict[str, Any] | None = None


def _get_selected_agreement_state() -> dict[str, Any] | None:
    """Return the selected agreement row for private widget workflows."""
    return dict(_SELECTED_AGREEMENT) if _SELECTED_AGREEMENT else None


def serialize_custom_fields(values: dict[str, Any] | None) -> str:
    """Serialize organization-specific intake values to deterministic JSON.

    Parameters
    ----------
    values : dict[str, Any] or None
        Extra values collected from configured custom fields.

    Returns
    -------
    str
        JSON object text suitable for ``custom_fields_json``.

    """
    return json.dumps(values or {}, sort_keys=True, default=to_iso_date)

def deserialize_custom_fields(custom_fields_json: Any) -> dict[str, Any]:
    """Deserialize stored custom-field JSON for widget display.

    Parameters
    ----------
    custom_fields_json : Any
        JSON object text, an existing mapping, or a blank value.

    Returns
    -------
    dict[str, Any]
        Parsed custom field values. Blank input produces an empty mapping.

    Raises
    ------
    ValueError
        If non-blank text is not a JSON object.

    """
    if custom_fields_json in (None, ""):
        return {}
    if isinstance(custom_fields_json, dict):
        return dict(custom_fields_json)
    try:
        values = json.loads(str(custom_fields_json))
    except json.JSONDecodeError as exc:
        raise ValueError("custom_fields_json must be a JSON object.") from exc
    if not isinstance(values, dict):
        raise ValueError("custom_fields_json must be a JSON object.")
    return values

def config_value(config: Any, name: str, default: Any) -> Any:
    """Return a data-agreement widget configuration value."""
    agreement_config = getattr(config, "data_agreement_config", config)
    if isinstance(agreement_config, dict):
        return agreement_config.get(name, default)
    return getattr(agreement_config, name, default)

def get_widget_visible_fields(config: Any, kind: str) -> list[str]:
    """Return configured editable columns without backend audit fields.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Environment configuration containing widget settings.
    kind : {"data_steward_widget", "data_agreement_widget"}
        Widget configuration section to inspect.

    Returns
    -------
    list[str]
        Safe editable fields. Technical audit fields are always excluded.

    """
    configured = {**WIDGET_CONFIG_DEFAULTS[kind], **dict(config_value(config, kind, {}) or {})}.get("visible_columns", [])
    hidden = set(STANDARD_RUNTIME_AUDIT_COLUMNS) | {"custom_fields_json"}
    if kind == "data_steward_widget":
        hidden.update({"steward_id", "is_active"})
        hidden.update(set(configured) - set(DATA_STEWARD_VISIBLE_FIELDS))
    if kind == "data_agreement_widget":
        hidden.update(DATA_AGREEMENT_GENERATED_FIELDS)
    return [field for field in configured if field not in hidden]

def collect_custom_fields(config: list[dict[str, Any]] | dict[str, Any], widgets_by_key: dict[str, Any]) -> dict[str, Any]:
    """Collect and validate configured custom-field widget values.

    Parameters
    ----------
    config : list[dict[str, Any]] or dict[str, Any]
        Custom-field definitions or widget config.
    widgets_by_key : dict[str, ipywidgets.Widget]
        Rendered custom widgets keyed by configured field key.

    Returns
    -------
    dict[str, Any]
        JSON-ready custom values.

    Raises
    ------
    ValueError
        If a required configured field is blank.

    """
    definitions = config.get("custom_fields", []) if isinstance(config, dict) else config
    values: dict[str, Any] = {}
    for definition in definitions:
        key = str(definition["key"])
        value = widgets_by_key[key].value
        if isinstance(value, tuple):
            value = list(value)
        if isinstance(value, (date, datetime)):
            value = to_iso_date(value)
        if definition.get("required") and value in (None, "", []):
            raise ValueError(f"{definition.get('label', key)} is required.")
        values[key] = value
    return values

def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
    if rows is None:
        return []
    if hasattr(rows, "collect"):
        rows = rows.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]

def _latest_by_key(rows: Any, key: str) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in _coerce_row_dicts(rows):
        value = str(row.get(key) or "").strip()
        if value and (value not in latest or str(row.get("_committed_at") or "") >= str(latest[value].get("_committed_at") or "")):
            latest[value] = row
    return sorted(latest.values(), key=lambda row: str(row.get(key) or "").lower())

def to_bool(value: Any) -> bool:
    """Normalize common notebook and metadata boolean representations.

    Blank values are treated as false. Any non-blank value outside the
    supported true/false spellings raises a clear validation error instead of
    relying on Python string truthiness.
    """
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    normalized = str(value).strip().lower()
    if normalized in {"true", "1", "yes", "y"}:
        return True
    if normalized in {"", "false", "0", "no", "n"}:
        return False
    raise ValueError(f"Unsupported boolean value: {value!r}. Use true/false, 1/0, yes/no, or y/n.")

def _audit_date(config: Any = None) -> date:
    """Return today in the configured FabricOps audit timezone."""
    return datetime.fromisoformat(config_shared.get_current_audit_timestamp(config=config)).date()

def active_steward(row: dict[str, Any], config: Any = None) -> bool:
    """Return whether a steward person record is active."""
    is_active = row.get("is_active")
    return is_active in (None, "") or to_bool(is_active)


def list_data_stewards(config: Any, env: str, *, spark_session: Any = None, active_only: bool = True, missing_ok: bool = False, metadata_schema: str | None = None) -> list[dict[str, Any]]:
    """List latest append-only steward rows from the metadata lakehouse."""
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    try:
        rows = read_lakehouse_table_core(str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), target="metadata", schema=metadata_schema, spark_session=spark_session, context={"config": config, "env": env})
    except Exception:
        if missing_ok:
            return []
        raise
    latest = _latest_by_key(rows, "steward_id")
    return [row for row in latest if active_steward(row, config)] if active_only else latest

def write_widget_metadata_row(*, spark: Any, config: Any, env: str, table: str, row: dict[str, Any]) -> None:
    """Append one widget metadata row to the configured metadata target."""
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    canonical_table = {
        str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)): DATA_STEWARD_TABLE,
        str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)): DATA_AGREEMENT_TABLE,
    }.get(table, table)
    canonical_schema = metadata_table_schema_registry().get(canonical_table)
    typed_row = coerce_metadata_row_types(canonical_table, row)
    write_lakehouse_table_core(spark.createDataFrame([typed_row], schema=canonical_schema), table, target="metadata", schema=configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, mode="append")

def parse_iso_date(value: Any, field_name: str, *, required: bool = False) -> date | None:
    """Return a date object or raise a clear intake validation error."""
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{field_name} is required.")
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO date (YYYY-MM-DD).") from exc

def _parse_agreement_version(version: Any) -> tuple[int, int, int]:
    """Parse a semantic contract version into a comparable tuple."""
    try:
        parts = str(version or "").strip().split(".")
        return tuple(int(parts[index]) if index < len(parts) else 0 for index in range(3))  # type: ignore[return-value]
    except (TypeError, ValueError):
        return (0, 0, 0)


def latest_agreement_versions(rows: Any) -> list[dict[str, Any]]:
    """Return the latest semantic version for each stable agreement ID."""

    def _agreement_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
        return (
            _parse_agreement_version(row.get("agreement_version")),
            str(row.get("_committed_at") or ""),
            str(row.get("agreement_name") or ""),
            str(row.get("agreement_id") or ""),
        )

    latest: dict[str, dict[str, Any]] = {}
    for row in _coerce_row_dicts(rows):
        key = str(row.get("agreement_id") or "").strip()
        if key and (key not in latest or _agreement_sort_key(row) > _agreement_sort_key(latest[key])):
            latest[key] = row
    return sorted(latest.values(), key=lambda row: (str(row.get("agreement_name") or "").lower(), str(row.get("agreement_id") or "")))

def list_all_data_agreement_rows(config: Any, env: str, *, spark_session: Any = None, missing_ok: bool = False, metadata_schema: str | None = None) -> list[dict[str, Any]]:
    """List all append-only agreement rows from the metadata lakehouse."""
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    try:
        rows = read_lakehouse_table_core(str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), target="metadata", schema=metadata_schema or configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, spark_session=spark_session)
    except Exception:
        if missing_ok:
            return []
        raise
    return _coerce_row_dicts(rows)

def list_data_agreements(config: Any, env: str, *, spark_session: Any = None, active_only: bool = False, missing_ok: bool = False, metadata_schema: str | None = None) -> list[dict[str, Any]]:
    """List latest versioned agreements from the configured metadata lakehouse."""
    rows = list_all_data_agreement_rows(config, env, spark_session=spark_session, missing_ok=missing_ok, metadata_schema=metadata_schema)
    agreements = latest_agreement_versions(rows)
    if not active_only:
        return agreements
    today = _audit_date(config)
    return [row for row in agreements if (not row.get("start_date") or date.fromisoformat(str(row["start_date"])[:10]) <= today) and (not row.get("expiry_date") or date.fromisoformat(str(row["expiry_date"])[:10]) >= today)]

def to_iso_date(value: Any) -> str:
    """Return a date-like widget value as an ISO string."""
    if value is None:
        return ""
    return value.date().isoformat() if isinstance(value, datetime) else value.isoformat() if isinstance(value, date) else str(value)

def _coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
    if rows_or_df is None:
        return []
    if hasattr(rows_or_df, "collect"):
        rows_or_df = rows_or_df.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows_or_df]

def _value(row: dict[str, Any], name: str, default: Any = "") -> Any:
    return row.get(name, row.get(name.upper(), default))


def _is_table_not_found_error(exc: Exception) -> bool:
    """Return whether a Spark/read exception clearly means the table is absent."""
    error_class_getter = getattr(exc, "getErrorClass", None)
    try:
        error_class = str(error_class_getter() or "") if callable(error_class_getter) else ""
    except Exception:
        error_class = ""
    if error_class.upper() in {"PATH_NOT_FOUND", "TABLE_OR_VIEW_NOT_FOUND", "DELTA_TABLE_NOT_FOUND"}:
        return True
    message = str(exc).lower()
    not_found_markers = (
        "path does not exist",
        "path_not_found",
        "table_or_view_not_found",
        "table not found",
        "no such file or directory",
        "doesn't exist",
        "does not exist",
    )
    non_not_found_markers = ("permission", "access denied", "unauthorized", "forbidden", "authentication", "credential", "malformed", "invalid configuration")
    return any(marker in message for marker in not_found_markers) and not any(marker in message for marker in non_not_found_markers)


def enrichment_control_options(config: Any) -> tuple[list[str], list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return configured column metadata enrichment controls."""
    governance = getattr(config, "governance_config", None)
    sensitivity = list(getattr(governance, "sensitivity_labels", None) or SENSITIVITY_LABELS)
    pii = list(getattr(governance, "pii_classifications", None) or PERSONAL_DATA_CLASSIFICATIONS)
    context_widget = getattr(governance, "enrichment_context_widget", None) or {}
    classification_widget = getattr(governance, "enrichment_classification_widget", None) or {}
    context_fields = list(context_widget.get("custom_fields", []) or [])
    classification_fields = list(classification_widget.get("custom_fields", []) or [])
    return sensitivity, pii, context_fields, classification_fields


def _read_metadata_table_or_empty(config: Any, env: str, table_name: str, *, spark_session: Any) -> list[dict[str, Any]]:
    """Read a metadata table and return row dictionaries."""
    try:
        frame = read_lakehouse_table_core(
            table_name,
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            context={"config": config, "env": env},
            spark_session=spark_session,
        )
    except Exception as exc:
        if _is_table_not_found_error(exc):
            return []
        raise
    return _coerce_rows(frame)


# Governance readiness and policy helpers migrated from the retired mixed governance module.


# DQ authoring record helpers migrated to widget ownership.


# Shared catalogue-selection widget implementation.
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
PROFILE_TABLE = "METADATA_DATA_PROFILED"
PROFILE_FREQUENCY_TABLE = "METADATA_DATA_PROFILED_FREQUENCY"


def dataset_label(row: dict[str, Any], role: str | None = None) -> str:
    """Build the consistent physical dataset label, optionally tagged by role."""
    location = " / ".join(
        str(row.get(field) or "").strip()
        for field in ("layer", "schema_name", "table_name")
        if str(row.get(field) or "").strip()
    ) or str(row.get("table_id") or "")
    return f"[{role}] {location}" if role else location


def schema_version_options(rows: list[dict[str, Any]], table_id: str) -> list[tuple[str, str]]:
    """Return deterministic newest-first schema choices for one dataset."""
    versions: dict[str, Any] = {}
    for row in rows:
        if str(row.get("table_id") or "") != table_id:
            continue
        fingerprint = str(row.get("schema_fingerprint") or "").strip()
        committed = row.get("_committed_at")
        if fingerprint and str(committed or "") >= str(versions.get(fingerprint) or ""):
            versions[fingerprint] = committed
    ordered = sorted(
        versions.items(),
        key=lambda item: (isinstance(item[1], datetime), str(item[1] or ""), item[0]),
        reverse=True,
    )
    counts = Counter(str(timestamp or "") for _fingerprint, timestamp in ordered)
    result = []
    for index, (fingerprint, timestamp) in enumerate(ordered):
        name = "Latest" if index == 0 else "Previous"
        detail = timestamp.isoformat(sep=" ", timespec="minutes") if isinstance(timestamp, datetime) else "Timestamp unavailable"
        suffix = f" — {fingerprint[:8]}" if counts[str(timestamp or "")] > 1 or timestamp is None else ""
        result.append((f"{name} — {detail}{suffix}", fingerprint))
    return result


def _prepare_selected_guardrail_views(results, row_results, *, table_id: str) -> dict[str, Any]:
    """Prepare one selected dataset's latest persisted guardrail execution."""
    from pyspark.sql import functions as F

    scoped = results.filter(
        (F.col("table_id") == table_id)
        & F.col("run_id").isNotNull()
        & (F.trim(F.col("run_id")) != "")
    )
    latest = (
        scoped.select("run_id", "_committed_at")
        .distinct()
        .orderBy(F.col("_committed_at").desc_nulls_last(), F.col("run_id").desc())
        .limit(1)
        .collect()
    )
    selected_run_id = str(latest[0]["run_id"]) if latest else None
    selected_results = (
        scoped.filter(F.col("run_id") == selected_run_id)
        if selected_run_id is not None
        else scoped.limit(0)
    )
    actual = F.col("actual_value_json")
    guardrail_results = selected_results.select(
        "rule_type",
        F.col("column_name").alias("columns"),
        "status",
        "severity",
        F.get_json_object(actual, "$.failed_count").cast("long").alias("failed_rows"),
        F.get_json_object(actual, "$.failed_percent").cast("double").alias("failed_percent"),
        F.get_json_object(actual, "$.total_count").cast("long").alias("total_count"),
        "reason",
        "can_continue",
        "run_id",
    ).orderBy(
        F.when(F.lower(F.col("status")) == "failed", 0)
        .when(F.lower(F.col("status")) == "warning", 1)
        .otherwise(2),
        F.col("rule_type"),
        F.col("columns"),
    )
    selected_row_results = (
        row_results.filter(
            (F.col("table_id") == table_id)
            & (F.col("run_id") == selected_run_id)
        )
        if selected_run_id is not None
        else row_results.limit(0)
    )
    guardrail_row_results = selected_row_results.select(
        "rule_type",
        "row_identity",
        F.col("involved_columns_json").alias("involved_columns"),
        F.col("failed_values_json").alias("failed_values"),
        "failure_reason",
        "run_id",
    ).orderBy("row_identity", "rule_type", "failure_reason")
    return {
        "guardrail_results": guardrail_results,
        "guardrail_row_results": guardrail_row_results,
    }


# ---------------------------------------------------------------------------
# Guardrail authoring shared implementation
# ---------------------------------------------------------------------------

from fabricops_kit.config.shared import is_table_not_found_error

from fabricops_kit.pipeline.shared import canonical_guardrail_rule_record

def _guardrail_stable_json(value: Any) -> str:
    """Serialize authoring parameters deterministically."""
    return json.dumps(value, default=str, sort_keys=True, separators=(",", ":"))

def latest_rule(
    existing_rules: Iterable[Mapping[str, Any]],
    guardrail_type: str,
    *,
    rule_id: str | None = None,
) -> dict[str, Any]:
    """Return the newest matching normalized Guardrail row."""
    matches = []
    for raw in existing_rules or ():
        row = dict(raw)
        if str(row.get("guardrail_type") or "") != guardrail_type:
            continue
        if rule_id is not None and str(row.get("rule_id") or "") != rule_id:
            continue
        matches.append(row)
    matches.sort(
        key=lambda row: (
            int(row.get("guardrail_version") or 0),
            str(row.get("_committed_at") or ""),
        ),
        reverse=True,
    )
    return matches[0] if matches else {}

def rule_parameters(rule: Mapping[str, Any]) -> dict[str, Any]:
    """Parse one normalized Guardrail parameter payload."""
    raw = rule.get("rule_parameters_json") or "{}"
    try:
        return json.loads(raw) if isinstance(raw, str) else dict(raw or {})
    except (TypeError, json.JSONDecodeError):
        return {}

def _column_id_for_name(state: Mapping[str, Any], column_name: str) -> str:
    """Resolve one visible column name to its canonical Catalogue column ID."""
    name = str(column_name or "").strip()
    column_ids = dict(state.get("column_ids") or {})
    column_id = str(column_ids.get(name) or "").strip()
    if not name or not column_id:
        raise ValueError(
            f"Column {name!r} does not resolve to a canonical column_id for the selected table."
        )
    return column_id

def _build_guardrail_rule_id(
    *,
    table_id: str,
    column_id: str,
    guardrail_type: str,
    rule_id: str,
    identity_parameters: Mapping[str, Any] | None = None,
) -> str:
    """Build a stable identity for one logical normalized Guardrail rule."""
    payload = {
        "table_id": str(table_id),
        "column_id": str(column_id or ""),
        "guardrail_type": str(guardrail_type),
        "rule_id": str(rule_id),
        "identity_parameters": dict(identity_parameters or {}),
    }
    return f"guardrail_{hashlib.sha256(_guardrail_stable_json(payload).encode('utf-8')).hexdigest()}"

def _next_guardrail_version(
    existing_rules: Iterable[Mapping[str, Any]], guardrail_rule_id: str
) -> int:
    """Return the next append-only Guardrail version for one logical rule."""
    versions = [
        int(row.get("guardrail_version") or 0)
        for row in existing_rules or ()
        if str(row.get("guardrail_rule_id") or "") == guardrail_rule_id
    ]
    return max(versions, default=0) + 1

def build_rule_record(
    state: Mapping[str, Any],
    *,
    guardrail_type: str,
    rule_id: str,
    rule_type: str,
    parameters: Mapping[str, Any] | None = None,
    severity: str = "warning",
    column_name: str = "",
    identity_parameters: Mapping[str, Any] | None = None,
    guardrail_version: int | None = None,
    is_active: bool = True,
) -> dict[str, Any]:
    """Build one Stage 4A Guardrail row without obsolete identity or review fields."""
    table_id = str(state.get("table_id") or "").strip()
    environment_name = str(state.get("environment_name") or "").strip()
    if not table_id:
        raise ValueError("A selected profiled table with a canonical table_id is required.")
    if not environment_name:
        raise ValueError("The selected profiled table must have an environment_name.")
    column_id = _column_id_for_name(state, column_name) if column_name else ""
    guardrail_rule_id = _build_guardrail_rule_id(
        table_id=table_id,
        column_id=column_id,
        guardrail_type=guardrail_type,
        rule_id=rule_id,
        identity_parameters=identity_parameters,
    )
    version = guardrail_version or _next_guardrail_version(
        state.get("existing_rules") or (), guardrail_rule_id
    )
    return {
        "guardrail_rule_id": guardrail_rule_id,
        "guardrail_version": int(version),
        "table_id": table_id,
        "column_id": column_id,
        "environment_name": environment_name,
        "guardrail_type": str(guardrail_type),
        "rule_id": str(rule_id),
        "rule_type": str(rule_type),
        "rule_parameters_json": _guardrail_stable_json(dict(parameters or {})),
        "severity": str(severity),
        "is_active": bool(is_active),
    }

def dq_records_from_selection(
    state: Mapping[str, Any],
    *,
    rule_id: str,
    selected_columns: Iterable[str],
    parameters: Mapping[str, Any] | None = None,
    severity: str = "warning",
    column_selection: str = "independent",
) -> list[dict[str, Any]]:
    """Build canonical DQ authoring rows for the selected rule semantics."""
    columns = [str(column) for column in selected_columns]
    available = set(state.get("columns") or ())
    if any(column not in available for column in columns):
        raise ValueError("Selected DQ columns must come from the selected profiled table.")
    values = dict(parameters or {})
    if column_selection == "independent":
        return [
            build_rule_record(
                state,
                guardrail_type="dq",
                rule_id=rule_id,
                rule_type=rule_id,
                column_name=column,
                parameters={"columns": [column], **values},
                severity=severity,
            )
            for column in columns
        ]

    column_ids = [_column_id_for_name(state, column) for column in columns]
    identity_parameters: dict[str, Any] = {"column_ids": column_ids, **values}
    condition_column = str(values.get("condition_column") or "").strip()
    if condition_column:
        identity_parameters["condition_column_id"] = _column_id_for_name(
            state, condition_column
        )
    return [
        build_rule_record(
            state,
            guardrail_type="dq",
            rule_id=rule_id,
            rule_type=rule_id,
            parameters={"columns": columns, **values},
            severity=severity,
            identity_parameters=identity_parameters,
        )
    ]

def canonicalize_records(
    records: list[dict[str, Any]],
    *,
    config: Any,
    env: str,
) -> list[dict[str, Any]]:
    """Normalize authored Guardrail rows before the widget-owned shared write call."""
    return [
        canonical_guardrail_rule_record(record, config=config, env=env)
        for record in records
    ]

def _guardrail_coerce_rows(rows_or_df: Any) -> list[dict[str, Any]]:
    if rows_or_df is None:
        return []
    if hasattr(rows_or_df, "collect"):
        rows_or_df = rows_or_df.collect()
    return [
        row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        for row in rows_or_df
    ]

def read_metadata_table_or_empty(
    config: Any,
    env: str,
    table_name: str,
    *,
    spark_session: Any,
) -> list[dict[str, Any]]:
    """Read a metadata table and return row dictionaries, or an empty list if absent."""
    try:
        frame = read_lakehouse_table_core(
            table_name,
            target="metadata",
            schema=configured_lakehouse_schema(config, env, "metadata"),
            context={"config": config, "env": env},
            spark_session=spark_session,
        )
    except Exception as exc:
        if is_table_not_found_error(exc):
            return []
        raise
    return _guardrail_coerce_rows(frame)

def write_rule_records(
    records: list[dict[str, Any]],
    *,
    config: Any,
    env: str,
    spark_session: Any,
) -> None:
    """Append canonical rule records to ``METADATA_GUARDRAIL``."""
    if not records:
        return
    write_lakehouse_table_core(
        spark_session.createDataFrame(
            [coerce_metadata_row_types(GUARDRAIL_TABLE, record) for record in records]
        ),
        GUARDRAIL_TABLE,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
        mode="append",
    )

def load_guardrail_authoring_targets(
    config: Any,
    env: str,
    *,
    spark_session: Any,
    widgets: Any,
    on_change: Any | None = None,
) -> tuple[dict[str, Any], Any, dict[str, Any]]:
    """Resolve independently selectable profiled targets through normalized Catalogue IDs."""
    catalogue = read_metadata_table_or_empty(
        config, env, CATALOGUE_TABLE, spark_session=spark_session
    )
    profiles = read_metadata_table_or_empty(
        config, env, PROFILED_TABLE, spark_session=spark_session
    )
    rules = read_metadata_table_or_empty(
        config, env, GUARDRAIL_TABLE, spark_session=spark_session
    )
    if not catalogue or not profiles:
        raise ValueError("No profiled Catalogue table is available for Guardrail authoring.")

    table_rows = {
        str(row.get("table_id") or ""): dict(row)
        for row in catalogue
        if str(row.get("environment_name") or env) == env
        and str(row.get("metadata_level") or "").lower() == "table"
        and str(row.get("table_id") or "").strip()
    }
    profile_table_ids = {
        str(row.get("table_id") or "")
        for row in profiles
        if str(row.get("environment_name") or env) == env
        and str(row.get("table_id") or "").strip()
    }
    selectable_ids = sorted(set(table_rows) & profile_table_ids)
    if not selectable_ids:
        raise ValueError(
            "METADATA_DATA_PROFILED has no table that resolves to METADATA_DATA_CATALOGUE."
        )

    def label(table_id: str) -> str:
        row = table_rows[table_id]
        location = " / ".join(
            value
            for value in (
                str(row.get("store_type") or ""),
                str(row.get("layer") or ""),
                str(row.get("schema_name") or ""),
                str(row.get("table_name") or ""),
            )
            if value
        )
        return location or table_id

    target = widgets.Dropdown(
        options=[(label(table_id), table_id) for table_id in selectable_ids],
        **widget_common(widgets, "Profiled table"),
    )
    summary = widgets.HTML()
    state: dict[str, Any] = {}

    def refresh(*_: Any) -> None:
        table_id = str(target.value or "")
        table = table_rows[table_id]
        table_profiles = [
            dict(row)
            for row in profiles
            if str(row.get("environment_name") or env) == env
            and str(row.get("table_id") or "") == table_id
        ]
        latest = max(
            table_profiles,
            key=lambda row: (
                str(row.get("_committed_at") or ""),
                str(row.get("profile_snapshot_id") or ""),
            ),
        )
        snapshot_id = str(latest.get("profile_snapshot_id") or "")
        if snapshot_id:
            snapshot = [
                row
                for row in table_profiles
                if str(row.get("profile_snapshot_id") or "") == snapshot_id
            ]
        else:
            latest_at = str(latest.get("_committed_at") or "")
            snapshot = [
                row
                for row in table_profiles
                if str(row.get("_committed_at") or "") == latest_at
            ]

        catalogue_columns = {
            str(row.get("column_id") or ""): dict(row)
            for row in catalogue
            if str(row.get("environment_name") or env) == env
            and str(row.get("table_id") or "") == table_id
            and str(row.get("metadata_level") or "").lower() == "column"
            and str(row.get("column_id") or "").strip()
        }
        evidence = []
        for profile in snapshot:
            column_id = str(profile.get("column_id") or "")
            catalogue_column = catalogue_columns.get(column_id)
            if not catalogue_column:
                continue
            column_name = str(catalogue_column.get("column_name") or "").strip()
            if not column_name:
                continue
            evidence.append(
                {
                    "table_id": table_id,
                    "column_id": column_id,
                    "column_name": column_name,
                    "data_type": str(profile.get("data_type") or ""),
                    "profile_id": str(profile.get("profile_id") or ""),
                    "profile_snapshot_id": snapshot_id,
                    "_committed_at": profile.get("_committed_at"),
                }
            )
        evidence.sort(key=lambda row: row["column_name"].casefold())
        if not evidence:
            raise ValueError(
                "The selected profile snapshot has no columns that resolve to Catalogue column IDs."
            )
        existing_rules = [
            dict(row)
            for row in rules
            if str(row.get("environment_name") or env) == env
            and str(row.get("table_id") or "") == table_id
        ]
        state.clear()
        state.update(
            {
                "environment_name": env,
                "table_id": table_id,
                "table_name": str(table.get("table_name") or ""),
                "store_type": str(table.get("store_type") or ""),
                "layer": str(table.get("layer") or ""),
                "schema_name": str(table.get("schema_name") or ""),
                "profile_snapshot_id": snapshot_id,
                "columns": [row["column_name"] for row in evidence],
                "column_ids": {
                    row["column_name"]: row["column_id"] for row in evidence
                },
                "catalogue_profile_rows": evidence,
                "existing_rules": existing_rules,
            }
        )
        summary.value = (
            f"<b>Columns:</b> {len(evidence)} · <b>Existing rules:</b> {len(existing_rules)} · "
            f"<b>table_id:</b> <code>{table_id}</code>"
        )
        if on_change is not None:
            on_change(state)

    target.observe(refresh, names="value")
    refresh()
    return state, target, {"target_summary": summary, "refresh_target": refresh}
