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
    write_lakehouse_table_core,
)
from fabricops_kit.config.audit import _audit_timestamp_value, _resolve_action_by, build_runtime_audit_fields
from fabricops_kit.config.metadata_keys import _build_dq_rule_key
from fabricops_kit.config.metadata_schemas import (
    CANONICAL_METADATA_TABLES,
    coerce_metadata_row_types,
    metadata_table_schema_registry,
)
from fabricops_kit.pipeline.guardrails_shared import DQ_RULE_TYPES


_WIDGET_STYLE = {"description_width": "initial"}
_WIDGET_FIELD_MIN_WIDTH = "0"
_WIDGET_FIELD_WIDTH = "100%"
_TEXTAREA_HEIGHT = "80px"


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


def execution_log_section(widgets: Any, output: Any) -> Any:
    """Present unfiltered technical output beneath a visible execution-log heading."""
    output.layout = widgets.Layout(width="100%", height="auto", overflow="visible")
    return widgets.VBox(
        [widgets.HTML(value="<b>Execution log</b>"), output],
        layout=widgets.Layout(
            width="100%",
            height="auto",
            overflow="visible",
            border="1px solid #d7e7f5",
            padding="10px",
            font_family="monospace",
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
GUARDRAIL_REVIEW_STATUSES = ["draft", "pending_governance_review", "active_pending_governance_review", "self_approved", "governance_approved", "rejected_by_governance", "superseded", "inactive"]
ACTIVATION_STATES = ["active", "pending", "inactive"]
REVIEW_STATES = ["draft", "pending_governance_review", "active_pending_governance_review", "governance_approved", "rejected_by_governance", "superseded", "inactive"]
SOURCE_NOTEBOOK_TYPES = ["02_pipeline", "01_governance"]
CREATED_BY_ROLES = ["engineering", "governance", "system"]
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"
DATA_ACCESS_TABLE = "METADATA_DATA_ACCESS"
SENSITIVITY_LABELS = ["classified", "restricted", "public"]
PERSONAL_DATA_CLASSIFICATIONS = ["direct PII", "indirect PII", "none"]


def get_current_notebook_lineage_scope(
    *,
    target: str = "metadata",
    schema: str | None = None,
    spark_session=None,
    context=None,
) -> list[tuple[str, str]]:
    """Return historical dataset roles and IDs for the active pipeline notebook."""
    from pyspark.sql import functions as F

    config, env, resolved = config_shared.resolve_fabric_context(context=context)
    runtime = resolved.get("runtime_metadata") or {}
    workspace_id = str(resolved.get("workspace_id") or runtime.get("workspace_id") or "").strip()
    notebook_id = str(resolved.get("notebook_id") or runtime.get("notebook_id") or "").strip()
    if not workspace_id or not notebook_id:
        raise ValueError(
            "pipeline_scope='current_notebook' requires current workspace and notebook IDs from the Fabric runtime context."
        )
    lineage = read_lakehouse_table_core(
        LINEAGE_TABLE, target=target, schema=schema,
        spark_session=spark_session, context={"config": config, "env": env, **resolved},
    )
    scoped = lineage.filter(
        (F.col("environment_name") == env)
        & (F.col("workspace_id") == workspace_id)
        & (F.col("notebook_id") == notebook_id)
    )
    rows = (
        scoped.groupBy("metadata_table_key")
        .agg(
            F.max("profiled_at").alias("latest_profiled_at"),
            F.sort_array(F.collect_set("profile_role")).alias("historical_roles"),
        )
        .orderBy(F.col("latest_profiled_at").desc_nulls_last(), F.col("metadata_table_key"))
        .collect()
    )
    return [
        (
            " / ".join(str(role).strip().title() for role in row["historical_roles"] if str(role or "").strip())
            or "Pipeline",
            str(row["metadata_table_key"]),
        )
        for row in rows
        if str(row["metadata_table_key"] or "").strip()
    ]


def get_data_contract_views(
    metadata_table_key: str,
    *,
    agreement_id: str | None = None,
    environment_name: str | None = None,
    target: str = "metadata",
    schema: str | None = None,
    spark_session=None,
    context=None,
) -> dict[str, Any]:
    """Return the canonical raw metadata traces related to a registered dataset."""
    from pyspark.sql import functions as F

    def read(name: str):
        return read_lakehouse_table_core(
            name, target=target, schema=schema, spark_session=spark_session, context=context,
        )

    raw_tables = {name: read(name) for name in CANONICAL_METADATA_TABLES}
    contracts = raw_tables["METADATA_DATA_CONTRACT"].filter(
        F.col("metadata_table_key") == metadata_table_key
    )
    if agreement_id:
        contracts = contracts.filter(F.col("agreement_id") == agreement_id)
        agreement_ids = [agreement_id]
    else:
        agreement_ids = [
            row["agreement_id"]
            for row in contracts.select("agreement_id").distinct().collect()
            if row["agreement_id"]
        ]

    agreement = raw_tables["METADATA_DATA_AGREEMENT"]
    agreement = agreement.filter(F.col("agreement_id").isin(agreement_ids)) if agreement_ids else agreement.limit(0)
    agreement_rows = agreement.select("provider_steward_id", "recipient_steward_id").distinct().collect()
    provider_steward_ids = [row["provider_steward_id"] for row in agreement_rows if row["provider_steward_id"]]
    recipient_steward_ids = [row["recipient_steward_id"] for row in agreement_rows if row["recipient_steward_id"]]
    steward_ids = list(dict.fromkeys([*provider_steward_ids, *recipient_steward_ids]))

    tables: dict[str, Any] = {}
    for name, frame in raw_tables.items():
        if name == "METADATA_DATA_STEWARD":
            frame = frame.filter(F.col("steward_id").isin(steward_ids)) if steward_ids else frame.limit(0)
        elif name == "METADATA_DATA_AGREEMENT":
            frame = agreement
        elif name == "METADATA_DATA_CONTRACT":
            frame = contracts
        else:
            frame = frame.filter(F.col("metadata_table_key") == metadata_table_key)
        if environment_name and "environment_name" in frame.columns:
            frame = frame.filter(F.col("environment_name") == environment_name)
        tables[name] = frame.orderBy(F.col("_committed_at").desc_nulls_last())

    return {
        "selection": {
            "environment_name": environment_name,
            "metadata_table_key": metadata_table_key,
            "agreement_id": agreement_id,
            "provider_steward_id": provider_steward_ids[0] if len(provider_steward_ids) == 1 else None,
            "recipient_steward_id": recipient_steward_ids[0] if len(recipient_steward_ids) == 1 else None,
        },
        "tables": tables,
        "error": None,
    }


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


def set_active_pipeline_context(context: PipelineRunContext) -> None:
    """Store the active pipeline runtime context for downstream helpers."""
    global _ACTIVE_PIPELINE_CONTEXT
    _ACTIVE_PIPELINE_CONTEXT = context


def pipeline_active_context() -> PipelineRunContext | None:
    """Return the active pipeline context when one has been started."""
    return _ACTIVE_PIPELINE_CONTEXT


_SELECTED_AGREEMENT: dict[str, Any] | None = None


def set_selected_agreement(row: dict[str, Any]) -> None:
    """Store the selected agreement row for private widget workflows."""
    global _SELECTED_AGREEMENT
    _SELECTED_AGREEMENT = dict(row)


def _get_selected_agreement_state() -> dict[str, Any] | None:
    """Return the selected agreement row for private widget workflows."""
    return dict(_SELECTED_AGREEMENT) if _SELECTED_AGREEMENT else None


def get_selected_agreement() -> dict[str, Any]:
    """Return the agreement selected by the active agreement-selection state."""
    selected = _get_selected_agreement_state()
    if not selected:
        raise RuntimeError("No agreement selected. Run the agreement selection workflow first.")
    return selected


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

def _next_minor_version(version: Any) -> str:
    """Return the next minor contract version, defaulting to ``1.0.0``."""
    major, minor, _ = _parse_agreement_version(version)
    return "1.0.0" if major == 0 else f"{major}.{minor + 1}.0"

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

def _approved_review_context(profile_rows: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> tuple[dict[str, dict[str, Any]], str, str, dict[str, Any]]:
    actor = _resolve_action_by(approved_by)
    audit = build_runtime_audit_fields(config=config, env=env or "", committed_by=actor) if config is not None and env is not None else {}
    return {str(_value(r, "column_name")): r for r in profile_rows}, actor, _audit_timestamp_value(config), audit

def _approved_column_identity(profile_row: dict[str, Any], review_row: dict[str, Any], *, env: str | None = None) -> dict[str, str]:
    col = str(review_row.get("column_name") or _value(profile_row, "column_name") or ((review_row.get("columns") or [""])[0]))
    environment = str(_value(profile_row, "environment_name") or review_row.get("environment_name") or env or "")
    dataset = str(_value(profile_row, "dataset_name") or review_row.get("dataset_name") or "")
    table = str(_value(profile_row, "table_name") or review_row.get("table_name") or "")
    store_type = str(_value(profile_row, "store_type") or review_row.get("store_type") or "lakehouse")
    layer = str(_value(profile_row, "layer") or review_row.get("layer") or review_row.get("fabric_store_target") or "")
    schema_name = _value(profile_row, "schema_name", review_row.get("schema_name"))
    table_key = str(
        _value(profile_row, "metadata_table_key")
        or review_row.get("metadata_table_key")
        or config_shared.build_metadata_table_key(store_type, layer, schema_name, table)
    )
    return {
        "metadata_column_key": str(_value(profile_row, "metadata_column_key") or review_row.get("metadata_column_key") or config_shared.build_metadata_column_key(table_key, col)),
        "metadata_table_key": table_key,
        "environment_name": environment,
        "dataset_name": dataset,
        "table_name": table,
        "column_name": col,
    }

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

def _json(value: Any) -> str:
    if value in (None, ""):
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, sort_keys=True)

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

def _render_enrichment_extra_fields(widgets: Any, definitions: list[dict[str, Any]]) -> dict[str, Any]:
    """Render configured enrichment extra fields keyed by field key."""
    controls: dict[str, Any] = {}
    for definition in definitions:
        key = str(definition.get("key") or "").strip()
        if not key:
            raise ValueError("Custom enrichment fields require a key.")
        label = str(definition.get("label") or key.replace("_", " ").title())
        field_type = str(definition.get("type") or "text").lower()
        common = {"description": label, "layout": widgets.Layout(width="420px")}
        if field_type == "textarea":
            control = widgets.Textarea(value="", rows=int(definition.get("rows", 2)), **common)
        elif field_type in {"dropdown", "select"}:
            options = list(definition.get("options", []))
            control = widgets.Dropdown(options=options, value=options[0] if options else None, **common)
        else:
            control = widgets.Text(value="", **common)
        controls[key] = control
    return controls

def _collect_enrichment_extra_fields(controls: dict[str, Any]) -> dict[str, Any]:
    """Collect configured enrichment extra-field values."""
    return {name: control.value for name, control in controls.items()}

def _selected_catalogue_rows_for_enrichment(guardrail_state: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return selected column evidence from the guardrail target handover state."""
    rows = [dict(row) for row in guardrail_state.get("catalogue_profile_rows", []) if row.get("column_name")]
    profile_run_id = str(guardrail_state.get("profile_run_id") or "")
    profile_stage = str(guardrail_state.get("profile_stage") or "")
    if profile_run_id:
        rows = [row for row in rows if str(_value(row, "profile_run_id")) == profile_run_id]
    if profile_stage:
        rows = [row for row in rows if str(_value(row, "profile_stage")) == profile_stage]
    deduped: dict[str, dict[str, Any]] = {}

    def profile_sort_key(row: dict[str, Any]) -> tuple[str, str, str, str]:
        return (
            str(_value(row, "profiled_at")),
            str(_value(row, "profile_run_id")),
            str(_value(row, "run_id") or _value(row, "pipeline_run_id")),
            str(_value(row, "profile_stage")),
        )

    for row in sorted(rows, key=profile_sort_key, reverse=True):
        deduped.setdefault(str(_value(row, "column_name")), row)
    return [deduped[name] for name in sorted(deduped)]

def build_enrichment_records(
    records: Iterable[Mapping[str, Any]],
    *,
    config: Any = None,
    env: str | None = None,
    actor: str | None = None,
) -> list[dict[str, Any]]:
    """Build canonical append-only ``METADATA_ENRICHMENT`` rows.

    Each input must provide ``enrichment_level``, ``metadata_key``,
    ``enrichment_type``, and a non-empty string ``value``. Appending a newer row
    replaces the current value; clearing is intentionally deferred because empty
    values are rejected.
    """
    audit = (
        build_runtime_audit_fields(config=config, env=env, committed_by=actor)
        if config is not None and env is not None
        else {}
    )
    built = []
    for raw in records:
        level = str(raw.get("enrichment_level") or "").strip().lower()
        if level not in {"table", "column"}:
            raise ValueError("enrichment_level must be 'table' or 'column'.")
        metadata_key = str(raw.get("metadata_key") or "").strip()
        if not metadata_key:
            raise ValueError("metadata_key must be non-empty.")
        enrichment_type = str(raw.get("enrichment_type") or "").strip()
        if not enrichment_type:
            raise ValueError("enrichment_type must be non-empty.")
        value = raw.get("value")
        if not isinstance(value, str) or not value.strip():
            raise ValueError("value must be a non-empty string.")
        row_audit = {name: raw.get(name, audit.get(name, "")) for name in STANDARD_RUNTIME_AUDIT_COLUMNS}
        built.append({
            "enrichment_id": str(raw.get("enrichment_id") or uuid.uuid4()),
            "enrichment_level": level,
            "metadata_key": metadata_key,
            "enrichment_type": enrichment_type,
            "value": value,
            **row_audit,
        })
    return built


def latest_enrichment_values(rows: Any) -> dict[tuple[str, str, str], dict[str, Any]]:
    """Return current enrichment rows keyed by level, metadata key, and type.

    Rows are ordered deterministically by ``_committed_at``, ``_activity_id``,
    and ``enrichment_id``. The lexicographically latest tuple wins.
    """
    source = rows.collect() if hasattr(rows, "collect") else rows
    latest: dict[tuple[str, str, str], dict[str, Any]] = {}
    for raw in source or []:
        row = raw.asDict(recursive=True) if hasattr(raw, "asDict") else dict(raw)
        key = (str(row.get("enrichment_level") or ""), str(row.get("metadata_key") or ""), str(row.get("enrichment_type") or ""))
        committed_at = row.get("_committed_at")
        committed_text = str(committed_at or "").strip().replace("Z", "+00:00")
        try:
            committed_value = committed_at if isinstance(committed_at, datetime) else datetime.fromisoformat(committed_text)
            if committed_value.tzinfo is None:
                committed_value = committed_value.replace(tzinfo=timezone.utc)
            committed_order = (1, committed_value.timestamp())
        except ValueError:
            committed_order = (0, committed_text)
        order = (committed_order, str(row.get("_activity_id") or ""), str(row.get("enrichment_id") or ""))
        current = latest.get(key)
        if current is None or order > current["_enrichment_sort_key"]:
            row["_enrichment_sort_key"] = order
            latest[key] = row
    for row in latest.values():
        row.pop("_enrichment_sort_key", None)
    return latest


def write_enrichment_records(records: list[dict[str, Any]], *, config: Any, env: str, spark_session: Any) -> None:
    """Append canonical enrichment records to the configured metadata target."""
    if not records:
        return
    schema = metadata_table_schema_registry()[ENRICHMENT_TABLE]
    coerced = [coerce_metadata_row_types(ENRICHMENT_TABLE, record) for record in records]
    write_lakehouse_table_core(
        spark_session.createDataFrame(coerced, schema=schema),
        ENRICHMENT_TABLE,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
        mode="append",
    )


def read_enrichment_records(config: Any, env: str, *, spark_session: Any) -> list[dict[str, Any]]:
    """Read enrichment append events from the configured metadata target."""
    return _read_metadata_table_or_empty(config, env, ENRICHMENT_TABLE, spark_session=spark_session)

def resolve_table_governance_policy(governance_rows: Any, *, environment_name: str = "", dataset_name: str = "", table_name: str = "", metadata_table_key: str = "") -> dict[str, Any]:
    """Return the latest active table-level governance policy.

    Parameters
    ----------
    governance_rows : Any
        Catalogue rows or selected target state rows containing table governance policy fields.
    environment_name, dataset_name, table_name, metadata_table_key : str, optional
        Table identity used to filter policy rows.

    Returns
    -------
    dict[str, Any]
        Effective policy. Tables default to ungoverned with no approval
        required unless the latest active policy row marks them governed.

    """
    default = {"governance_mode": "ungoverned", "approval_policy": "no_approval_required", "governance_status": "active", "approval_bypass_allowed": False, "requires_post_review": False}
    rows = []
    for row in _coerce_rows(governance_rows):
        if metadata_table_key and str(row.get("metadata_table_key") or "") not in {"", metadata_table_key}:
            continue
        if environment_name and str(row.get("environment_name") or "") not in {"", environment_name}:
            continue
        if dataset_name and str(row.get("dataset_name") or "") not in {"", dataset_name}:
            continue
        if table_name and str(row.get("table_name") or "") != table_name:
            continue
        if str(row.get("governance_status") or "active").lower() != "active":
            continue
        rows.append(row)
    if not rows:
        return default
    rows.sort(key=lambda row: str(row.get("effective_from") or row.get("reviewed_at") or row.get("_committed_at") or ""), reverse=True)
    latest = rows[0]
    mode = str(latest.get("governance_mode") or "ungoverned").lower()
    policy = str(latest.get("approval_policy") or ("approval_required" if mode == "governed" else "no_approval_required")).lower()
    bypass_allowed = bool(latest.get("approval_bypass_allowed", latest.get("bypass_allowed", policy == "approval_required_with_bypass")))
    return {**default, **latest, "governance_mode": mode, "approval_policy": policy, "approval_bypass_allowed": bypass_allowed, "bypass_allowed": bypass_allowed}

def _is_no_approval_required(policy: Mapping[str, Any]) -> bool:
    """Return whether policy allows active records without formal review."""
    return str(policy.get("governance_mode") or "ungoverned").lower() == "ungoverned" or str(policy.get("approval_policy") or "").lower() == "no_approval_required"

def _assert_governance_review_context(source_notebook_type: str) -> None:
    """Block formal review outside the ``01_governance`` notebook context."""
    if source_notebook_type != "01_governance":
        raise PermissionError("Formal governance review actions are only allowed from 01_governance.")

def _lifecycle_fields(*, activation_state: str, review_state: str, actor: str, now: str, created_by_role: str = "engineering", source_notebook_type: str = "02_pipeline", activation_reason: str = "", requires_governance_review: bool = False, requires_post_review: bool = False) -> dict[str, Any]:
    """Build standardized lifecycle fields for enrichment and guardrail rows."""
    active = activation_state == "active"
    fields = {
        "activation_state": activation_state,
        "is_active": active,
        "review_state": review_state,
        "review_status": review_state,
        "created_by_role": created_by_role,
        "source_notebook_type": source_notebook_type,
        "activation_reason": activation_reason,
        "requires_governance_review": requires_governance_review,
        "requires_post_review": requires_post_review,
    }
    if active:
        fields.update({"activated_by": actor, "activated_at": now, "effective_from": now})
    return fields

def _authoring_lifecycle(policy: Mapping[str, Any], *, action: str = "save", actor: str | None = None, bypass_reason: str = "", source_notebook_type: str = "02_pipeline", created_by_role: str = "engineering", config: Any = None) -> dict[str, Any]:
    """Return lifecycle fields for authoring save, draft, submit, and apply-now actions."""
    now = _audit_timestamp_value(config)
    resolved = _resolve_action_by(actor)
    if action == "draft":
        return _lifecycle_fields(activation_state="inactive", review_state="draft", actor=resolved, now=now, created_by_role=created_by_role, source_notebook_type=source_notebook_type)
    if _is_no_approval_required(policy):
        return _lifecycle_fields(activation_state="active", review_state="self_approved", actor=resolved, now=now, created_by_role=created_by_role, source_notebook_type=source_notebook_type)
    if action in {"apply_now", "bypass"} or bypass_reason:
        fields = _lifecycle_fields(activation_state="active", review_state="active_pending_governance_review", actor=resolved, now=now, created_by_role=created_by_role, source_notebook_type=source_notebook_type, activation_reason="engineering_apply_now", requires_governance_review=True, requires_post_review=True)
        fields.update({"bypass_reason": bypass_reason, "approval_bypassed": True, "bypassed_by": resolved, "bypassed_at": now})
        return fields
    return _lifecycle_fields(activation_state="pending", review_state="pending_governance_review", actor=resolved, now=now, created_by_role=created_by_role, source_notebook_type=source_notebook_type, requires_governance_review=True)

def guardrail_authoring_status(policy: Mapping[str, Any], *, bypass_reason: str = "", actor: str | None = None, config: Any = None, action: str = "save", source_notebook_type: str = "02_pipeline", created_by_role: str = "engineering") -> dict[str, Any]:
    """Return lifecycle fields for authored guardrail and enrichment records.

    Parameters
    ----------
    policy : mapping
        Effective table governance policy.
    bypass_reason : str, optional
        Justification for immediate application when review is still required.
    actor : str, optional
        Current user identifier.
    config : Any, optional
        Runtime configuration used for timestamp formatting.
    action : {"save", "draft", "submit", "apply_now"}, default="save"
        Authoring action selected by the notebook user.
    source_notebook_type : {"02_pipeline", "01_governance"}, default="02_pipeline"
        Notebook type that created the record.
    created_by_role : {"engineering", "governance", "system"}, default="engineering"
        Role that created the record.

    Returns
    -------
    dict[str, Any]
        Lifecycle fields for metadata rows.

    """
    lifecycle = _authoring_lifecycle(policy, action=action, actor=actor, bypass_reason=bypass_reason, source_notebook_type=source_notebook_type, created_by_role=created_by_role, config=config)
    lifecycle.setdefault("approval_required", bool(lifecycle.get("requires_governance_review")))
    lifecycle.setdefault("approval_bypassed", bool(lifecycle.get("activation_reason") == "engineering_apply_now"))
    lifecycle.setdefault("author_role", created_by_role)
    lifecycle.setdefault("governance_mode", str(policy.get("governance_mode") or "ungoverned"))
    lifecycle.setdefault("approval_policy", str(policy.get("approval_policy") or ("no_approval_required" if _is_no_approval_required(policy) else "approval_required")))
    return lifecycle

def _record_identity(row: Mapping[str, Any]) -> str:
    """Return the stable lifecycle record identity for rule or enrichment rows."""
    return str(row.get("rule_id") or row.get("rule_key") or "")

def apply_governance_rule_action(rule: Mapping[str, Any], action: str, *, actor: str | None = None, superseded_by_rule_key: str = "", replacement: Mapping[str, Any] | None = None, source_notebook_type: str = "01_governance", config: Any = None) -> dict[str, Any] | list[dict[str, Any]]:
    """Return append-only governance action row(s) for a guardrail rule.

    Parameters
    ----------
    rule : mapping
        Existing rule row from ``METADATA_GUARDRAIL``.
    action : str
        One of ``approve``, ``approve_and_activate``, ``reject``, ``replace``,
        ``deactivate``, or legacy ``supersede``.
    actor : str, optional
        Reviewer identity.
    superseded_by_rule_key : str, optional
        Replacement rule key for supersede/replace actions.
    replacement : mapping, optional
        Replacement rule values when action is ``replace``.
    source_notebook_type : str, default="01_governance"
        Must be ``01_governance`` for formal review decisions.
    config : Any, optional
        Runtime configuration used for timestamps.

    Returns
    -------
    dict or list of dict
        One review row, or old/new rows for ``replace``.

    """
    _assert_governance_review_context(source_notebook_type)
    row = dict(rule)
    now = _audit_timestamp_value(config)
    reviewer = _resolve_action_by(actor)
    legacy_supersede = action == "supersede"
    action = "replace" if legacy_supersede else action
    common = {"source_notebook_type": "01_governance", "created_by_role": "governance", "reviewed_by": reviewer, "reviewed_at": now, "review_comment": str(row.get("review_comment") or ""), "requires_governance_review": False, "requires_post_review": False}
    if action in {"approve", "approve_and_activate"}:
        row.update(common | {"activation_state": "active", "is_active": True, "review_state": "governance_approved", "review_status": "governance_approved", "approved_by": reviewer, "approved_at": now, "review_decision": "approved", "activated_by": row.get("activated_by") or reviewer, "activated_at": row.get("activated_at") or now, "effective_from": row.get("effective_from") or now})
    elif action == "reject":
        row.update(common | {"activation_state": "inactive", "is_active": False, "review_state": "rejected_by_governance", "review_status": "rejected_by_governance", "review_decision": "rejected", "effective_to": now})
    elif action == "deactivate":
        row.update(common | {"activation_state": "inactive", "is_active": False, "review_state": "inactive", "review_status": "inactive", "review_decision": "deactivated", "effective_to": now})
    elif action == "replace":
        new = dict(row)
        new.update(dict(replacement or {}))
        new_id = str((replacement or {}).get("rule_id") or superseded_by_rule_key or f"{_record_identity(row)}.replacement.{uuid.uuid4().hex[:8]}")
        new_key = str(superseded_by_rule_key or (replacement or {}).get("rule_key") or f"{row.get('rule_key') or _record_identity(row)}:{uuid.uuid4().hex[:8]}")
        old = dict(row)
        old.update(common | {"activation_state": "inactive", "is_active": False, "review_state": "superseded", "review_status": "superseded", "review_decision": "superseded", "superseded_by_record_id": new_id, "superseded_by_rule_key": new_key, "effective_to": now})
        new.update(common | {"rule_id": new_id, "rule_key": new_key, "activation_state": "active", "is_active": True, "review_state": "governance_approved", "review_status": "governance_approved", "approved_by": reviewer, "approved_at": now, "review_decision": "approved", "activated_by": reviewer, "activated_at": now, "effective_from": now, "effective_to": "", "supersedes_record_id": _record_identity(row), "supersedes_rule_id": str(row.get("rule_id") or "")})
        return old if legacy_supersede else [old, new]
    else:
        raise ValueError("action must be one of approve, approve_and_activate, reject, replace, deactivate, or supersede")
    return row

def load_rule_review_history(rows: Iterable[Mapping[str, Any]], *, metadata_table_key: str = "", metadata_column_key: str = "", table_name: str = "", column_name: str = "") -> list[dict[str, Any]]:
    """Return approval history derived from append-only rule rows.

    Parameters
    ----------
    rows : iterable of mapping
        Rows from ``METADATA_GUARDRAIL``.
    metadata_table_key, metadata_column_key, table_name, column_name : str, optional
        Optional filters for the selected table or column.

    Returns
    -------
    list of dict
        History rows ordered by submitted or created timestamp.

    """
    history: list[dict[str, Any]] = []
    for raw in rows or []:
        row = dict(raw)
        if metadata_table_key and str(row.get("metadata_table_key") or row.get("table_key") or "") not in {"", metadata_table_key}:
            continue
        if metadata_column_key and str(row.get("metadata_column_key") or row.get("column_key") or "") not in {"", metadata_column_key}:
            continue
        if table_name and str(row.get("table_name") or "") != table_name:
            continue
        if column_name and str(row.get("column_name") or "") not in {"", column_name}:
            continue
        history.append({
            "rule_id": str(row.get("rule_id") or ""),
            "rule_version": str(row.get("rule_version") or row.get("_committed_at") or ""),
            "record_type": "guardrail",
            "rule_type": str(row.get("enrichment_type") or row.get("guardrail_type") or row.get("rule_type") or ""),
            "review_status": str(row.get("review_status") or ""),
            "is_active": bool(row.get("is_active")),
            "submitted_by": str(row.get("submitted_by") or row.get("_committed_by") or ""),
            "submitted_at": str(row.get("submitted_at") or row.get("_committed_at") or ""),
            "reviewed_by": str(row.get("reviewed_by") or row.get("approved_by") or ""),
            "reviewed_at": str(row.get("reviewed_at") or row.get("approved_at") or ""),
            "decision": str(row.get("review_decision") or row.get("review_status") or ""),
            "comment": str(row.get("review_comment") or row.get("notes") or ""),
            "bypass_reason": str(row.get("bypass_reason") or ""),
            "requires_post_review": bool(row.get("requires_post_review")),
            "superseded_reference": str(row.get("supersedes_rule_id") or row.get("superseded_by_rule_key") or ""),
        })
    history.sort(key=lambda item: (item["submitted_at"], item["rule_id"]))
    return history

def _write_enrichment_records(records: list[dict[str, Any]], *, config: Any, env: str, spark_session: Any) -> None:
    """Append records to ``METADATA_ENRICHMENT``."""
    write_enrichment_records(records, config=config, env=env, spark_session=spark_session)

def _base_guardrail_rule_record(state: Mapping[str, Any], *, guardrail_type: str, rule_type: str, column_name: str = "", parameters: Mapping[str, Any] | None = None, severity: str = "warning", description: str = "", policy: Mapping[str, Any] | None = None, bypass_reason: str = "", actor: str | None = None, action: str = "submit", source_notebook_type: str = "02_pipeline", created_by_role: str = "engineering", config: Any = None) -> dict[str, Any]:
    """Build one ``METADATA_GUARDRAIL`` record for widget save actions."""
    env = str(state.get("environment_name") or "")
    dataset = str(state.get("dataset_name") or "")
    table = str(state.get("table_name") or "")
    table_key = str(state.get("metadata_table_key") or config_shared.build_metadata_table_key(
        state.get("store_type", "lakehouse"), state.get("layer", state.get("fabric_store_target", "")),
        state.get("schema_name"), table,
    ))
    rule_id = f"{table}.{column_name or '_table'}.{guardrail_type}.{rule_type}"
    lifecycle = guardrail_authoring_status(
        policy or state,
        bypass_reason=bypass_reason,
        actor=actor,
        config=config,
        action=action,
        source_notebook_type=source_notebook_type,
        created_by_role=created_by_role,
    )
    committed_at = _audit_timestamp_value(config)
    actor_value = _resolve_action_by(actor)
    pending = lifecycle.get("review_state") == "pending_governance_review"
    return {"guardrail_rule_id": rule_id, "rule_key": _build_dq_rule_key(env, dataset, table, rule_id), "rule_id": rule_id, "metadata_column_key": config_shared.build_metadata_column_key(table_key, column_name) if column_name else "", "metadata_table_key": table_key, "environment_name": env, "dataset_name": dataset, "table_name": table, "column_name": column_name, "guardrail_type": guardrail_type, "rule_type": rule_type, "rule_parameters_json": json.dumps(parameters or {}, sort_keys=True, default=str), "severity": severity, "description": description, "submitted_by": actor_value if pending else "", "submitted_at": committed_at if pending else "", "reviewed_by": actor_value if lifecycle.get("review_status") == "self_approved" else "", "reviewed_at": committed_at if lifecycle.get("review_status") == "self_approved" else "", "review_decision": lifecycle.get("review_status", ""), "review_comment": "", "supersedes_rule_id": "", "effective_from": committed_at if lifecycle.get("is_active") else "", "effective_to": "", "action_type": "created", "source_notebook_type": source_notebook_type, **lifecycle}

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

def _filter_table_rows(rows: Iterable[Mapping[str, Any]], *, environment_name: str, dataset_name: str, table_name: str, metadata_table_key: str = "") -> list[dict[str, Any]]:
    """Return rows matching a selected table identity."""
    filtered = []
    for row in rows:
        item = dict(row)
        if metadata_table_key and str(item.get("metadata_table_key") or "") not in {"", metadata_table_key}:
            continue
        if environment_name and str(item.get("environment_name") or "") not in {"", environment_name}:
            continue
        if dataset_name and str(item.get("dataset_name") or "") not in {"", dataset_name}:
            continue
        if table_name and str(item.get("table_name") or "") != table_name:
            continue
        filtered.append(item)
    return filtered

def _load_guardrail_authoring_targets(
    config: Any,
    env: str,
    *,
    spark_session: Any,
    widgets: Any,
    on_change: Any | None = None,
) -> tuple[dict[str, Any], Any, dict[str, Any]]:
    """Load profiled targets and keep a canonical selected-table state current."""
    catalogue = _read_metadata_table_or_empty(config, env, PROFILED_TABLE, spark_session=spark_session)
    rules = _read_metadata_table_or_empty(config, env, GUARDRAIL_TABLE, spark_session=spark_session)
    if not catalogue:
        raise ValueError("METADATA_DATA_PROFILED has no guardrail targets.")

    targets: dict[str, tuple[str, str, str, str]] = {}
    for row in catalogue:
        environment_name = str(row.get("environment_name") or env)
        dataset_name = str(row.get("dataset_name") or "")
        table_name = str(row.get("table_name") or "")
        if not table_name:
            continue
        metadata_table_key = str(
            row.get("metadata_table_key")
            or config_shared.build_metadata_table_key(
                row.get("store_type", "lakehouse"),
                row.get("layer", row.get("fabric_store_target", "")),
                row.get("schema_name"),
                table_name,
            )
        )
        label = f"{environment_name} / {dataset_name or '(no dataset)'} / {table_name}"
        targets[label] = (environment_name, dataset_name, table_name, metadata_table_key)
    if not targets:
        raise ValueError("METADATA_DATA_PROFILED has no table-level guardrail targets.")

    target = widgets.Dropdown(
        options=[(label, value) for label, value in sorted(targets.items())],
        description="Target",
        layout=widgets.Layout(width="760px"),
    )
    summary = widgets.HTML()
    state: dict[str, Any] = {}

    def refresh(*_: Any) -> None:
        environment_name, dataset_name, table_name, metadata_table_key = target.value
        table_rows = _filter_table_rows(
            catalogue,
            environment_name=environment_name,
            dataset_name=dataset_name,
            table_name=table_name,
            metadata_table_key=metadata_table_key,
        )
        table_rules = _filter_table_rows(
            rules,
            environment_name=environment_name,
            dataset_name=dataset_name,
            table_name=table_name,
            metadata_table_key=metadata_table_key,
        )
        latest = max(
            table_rows,
            key=lambda row: str(row.get("profiled_at") or row.get("run_timestamp") or row.get("profile_run_id") or ""),
        )
        columns = sorted({str(row.get("column_name")) for row in table_rows if row.get("column_name")})
        policy = resolve_table_governance_policy(
            table_rows,
            environment_name=environment_name,
            dataset_name=dataset_name,
            table_name=table_name,
            metadata_table_key=metadata_table_key,
        )
        state.clear()
        state.update(
            environment_name=environment_name,
            dataset_name=dataset_name,
            table_name=table_name,
            metadata_table_key=metadata_table_key,
            profile_run_id=str(latest.get("profile_run_id") or ""),
            profile_stage=str(latest.get("profile_stage") or ""),
            columns=columns,
            catalogue_profile_rows=table_rows,
            existing_rules=table_rules,
            **policy,
        )
        summary.value = (
            f"<b>Columns:</b> {len(columns)} · <b>Existing rules:</b> {len(table_rules)} · "
            f"<b>Governance:</b> {state['governance_mode']}"
        )
        if on_change is not None:
            on_change(state)

    target.observe(refresh, names="value")
    refresh()
    return state, target, {"target_summary": summary, "refresh_target": refresh}

def _latest_rule(existing_rules: Iterable[Mapping[str, Any]], guardrail_type: str, rule_type: str | None = None, column_name: str | None = None) -> dict[str, Any]:
    """Return the newest matching rule row for widget prepopulation."""
    matches = []
    for row in existing_rules or []:
        item = dict(row)
        if str(item.get("guardrail_type") or "") != guardrail_type:
            continue
        if rule_type is not None and str(item.get("rule_type") or "") != rule_type:
            continue
        if column_name is not None and str(item.get("column_name") or "") != column_name:
            continue
        matches.append(item)
    matches.sort(key=lambda row: (int(row.get("configuration_version") or 0), str(row.get("_committed_at") or "")), reverse=True)
    return matches[0] if matches else {}

def _rule_params(rule: Mapping[str, Any]) -> dict[str, Any]:
    """Return parsed rule parameters for widget prepopulation."""
    raw = rule.get("rule_parameters_json") or "{}"
    try:
        return json.loads(raw) if isinstance(raw, str) else dict(raw or {})
    except Exception:
        return {}

def _write_rule_records(records: list[dict[str, Any]], *, config: Any, env: str, spark_session: Any) -> None:
    """Append rule records to ``METADATA_GUARDRAIL``."""
    if not records:
        return
    write_lakehouse_table_core(
        spark_session.createDataFrame([coerce_metadata_row_types(GUARDRAIL_TABLE, record) for record in records]),
        GUARDRAIL_TABLE,
        target="metadata",
        schema=configured_lakehouse_schema(config, env, "metadata"),
        context={"config": config, "env": env},
        mode="append",
    )

def _schema_freshness_profile_records_from_selection(
    state: Mapping[str, Any],
    *,
    selected_columns: Iterable[str],
    schema_mode: str,
    freshness_mode: str,
    freshness_column: str,
    max_lag_days: int | str,
    profile_mode: str,
    watermark_column: str,
    partition_column: str = "",
    change_column: str = "",
    expected_change: str = "monitor_only",
    change_mode: str = "skip",
    bypass_reason: str = "",
    action: str = "submit",
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
    config: Any = None,
) -> list[dict[str, Any]]:
    """Build separate schema, freshness, change, and profile rule rows."""
    if str(profile_mode) == "changing_data" and not str(watermark_column or "").strip():
        raise ValueError("watermark_column is required when profile_mode is changing_data")
    if str(freshness_mode) == "enforce":
        try:
            lag_days = int(max_lag_days)
        except (TypeError, ValueError) as exc:
            raise ValueError("max_lag_days must be a non-negative integer") from exc
        if lag_days < 0:
            raise ValueError("max_lag_days must be a non-negative integer")
    else:
        lag_days = 0
    columns = [str(column) for column in selected_columns]
    change_mode = str(change_mode).strip().lower()
    if change_mode not in {"enforce", "monitor", "skip"}:
        raise ValueError("change_mode must be one of: enforce, monitor, skip")
    expected_change = "monitor_only" if change_mode == "monitor" else str(expected_change).strip().lower()
    if expected_change not in {"change_required", "no_change_required", "monitor_only"}:
        raise ValueError("expected_change must be one of: change_required, no_change_required, monitor_only")
    if change_mode != "skip" and (not str(partition_column).strip() or not str(change_column).strip()):
        raise ValueError("partition_column and change_column are required for the source-change rule")
    available_columns = {str(column) for column in state.get("columns", [])}
    if change_mode != "skip" and (partition_column not in available_columns or change_column not in available_columns):
        raise ValueError("partition_column and change_column must come from the selected table catalogue evidence")
    data_types = {str(row.get("column_name") or ""): str(row.get("data_type") or "") for row in state.get("catalogue_profile_rows", [])}
    records = []
    if change_mode != "skip":
        records.append(_base_guardrail_rule_record(
            state,
            guardrail_type="change",
            rule_type=expected_change,
            parameters={
                "partition_column": partition_column,
                "change_column": change_column,
                "expected_change": expected_change,
            },
            description="Source-change observation and expectation guardrail",
            bypass_reason=bypass_reason,
            action=action,
            source_notebook_type=source_notebook_type,
            created_by_role=created_by_role,
            config=config,
        ))
    records.extend([
        _base_guardrail_rule_record(
            state,
            guardrail_type="schema",
            rule_type=str(schema_mode),
            parameters={"columns": columns, "data_types": {column: data_types.get(column, "") for column in columns}},
            description="Selected-table schema guardrail",
            bypass_reason=bypass_reason,
            action=action,
            source_notebook_type=source_notebook_type,
            created_by_role=created_by_role,
            config=config,
        ),
        _base_guardrail_rule_record(
            state,
            guardrail_type="freshness",
            rule_type="max_lag_days" if str(freshness_mode) == "enforce" else "skip",
            parameters={"freshness_column": freshness_column if str(freshness_mode) == "enforce" else "", "max_lag_days": lag_days},
            description="Freshness guardrail",
            bypass_reason=bypass_reason,
            action=action,
            source_notebook_type=source_notebook_type,
            created_by_role=created_by_role,
            config=config,
        ),
        _base_guardrail_rule_record(
            state,
            guardrail_type="profile_behavior",
            rule_type=str(profile_mode),
            parameters={"watermark_column": watermark_column if str(profile_mode) == "changing_data" else ""},
            description="Profile behavior guardrail",
            bypass_reason=bypass_reason,
            action=action,
            source_notebook_type=source_notebook_type,
            created_by_role=created_by_role,
            config=config,
        ),
    ])
    return records

def _dq_records_from_selection(
    state: Mapping[str, Any],
    *,
    rule_type: str,
    selected_columns: Iterable[str],
    parameters: Mapping[str, Any] | None = None,
    severity: str = "warning",
    bypass_reason: str = "",
    action_type: str = "created",
    action: str = "submit",
    source_notebook_type: str = "02_pipeline",
    created_by_role: str = "engineering",
    config: Any = None,
    column_selection: str = "independent",
) -> list[dict[str, Any]]:
    """Build DQ rule records from selected columns."""
    columns = [str(column) for column in selected_columns]
    if column_selection != "independent":
        identity_payload = {"columns": columns, **dict(parameters or {})}
        record = _base_guardrail_rule_record(
            state,
            guardrail_type="dq",
            rule_type=rule_type,
            parameters=identity_payload,
            severity=severity,
            description=f"{rule_type} DQ guardrail",
            bypass_reason=bypass_reason,
            action=action,
            source_notebook_type=source_notebook_type,
            created_by_role=created_by_role,
            config=config,
        )
        identity_hash = hashlib.sha256(
            json.dumps(identity_payload, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()[:12]
        rule_id = f"{record['table_name']}._table.dq.{rule_type}.{identity_hash}"
        record.update(
            guardrail_rule_id=rule_id,
            rule_id=rule_id,
            rule_key=_build_dq_rule_key(
                record["environment_name"], record["dataset_name"], record["table_name"], rule_id
            ),
        )
        record["action_type"] = action_type
        if action_type in {"deactivated", "superseded"}:
            record["is_active"] = False
            record["review_status"] = "superseded" if action_type == "superseded" else "rejected"
        return [record]
    records = []
    for column in columns:
        record = _base_guardrail_rule_record(
            state,
            guardrail_type="dq",
            rule_type=rule_type,
            column_name=str(column),
            parameters={"columns": [str(column)], **dict(parameters or {})},
            severity=severity,
            description=f"{rule_type} DQ guardrail",
            bypass_reason=bypass_reason,
            action=action,
            source_notebook_type=source_notebook_type,
            created_by_role=created_by_role,
            config=config,
        )
        record["action_type"] = action_type
        if action_type in {"deactivated", "superseded"}:
            record["is_active"] = False
            record["review_status"] = "superseded" if action_type == "superseded" else "rejected"
        records.append(record)
    return records




# Governance readiness and policy helpers migrated from the retired mixed governance module.



def _is_success(row: dict[str, Any]) -> bool:
    return str(_value(row, "profile_status", "")).strip().lower() in {"success", "succeeded", "passed", "complete", "completed", "ok"}

def _first_present(row: dict[str, Any], names: Iterable[str], default: Any = "") -> Any:
    """Return the first present catalogue value from a list of candidate names."""
    for name in names:
        value = _value(row, name, None)
        if value not in (None, ""):
            return value
    return default

def _catalogue_physical_identity(row: dict[str, Any]) -> dict[str, str]:
    """Return stable physical table identity without profile stage or pipeline identity."""
    env = str(_first_present(row, ["environment_name", "env"]))
    asset_kind = str(_first_present(row, ["asset_kind", "asset_type"]))
    asset_name = str(_first_present(row, ["asset_name", "dataset_name", "lakehouse_name", "warehouse_name"]))
    schema_or_layer = str(_first_present(row, ["schema_name", "layer"]))
    table = str(_value(row, "table_name"))
    table_key = str(_first_present(row, ["physical_asset_id", "metadata_table_key"], ""))
    if not table_key:
        table_key = config_shared.build_metadata_table_key(asset_kind or "lakehouse", schema_or_layer, _value(row, "schema_name", None), table)
    return {
        "environment_name": env,
        "asset_kind": asset_kind,
        "asset_name": asset_name,
        "dataset_name": str(_value(row, "dataset_name") or asset_name),
        "schema_or_layer": schema_or_layer,
        "layer": str(_value(row, "layer") or schema_or_layer),
        "schema_name": str(_value(row, "schema_name") or schema_or_layer),
        "table_name": table,
        "metadata_table_key": table_key,
    }

def load_catalogue_profile_rows(config: Any, env: str, selection: dict[str, Any], *, spark_session: Any) -> list[dict[str, Any]]:
    """Load column rows for the selected latest successful profile run."""
    rows = _coerce_rows(read_lakehouse_table_core(PROFILED_TABLE, target="metadata", schema=configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, spark_session=spark_session))
    selection_identity = _catalogue_physical_identity(selection)
    filtered = []
    for row in rows:
        row_identity = _catalogue_physical_identity(row)
        if (
            _is_success(row)
            and row_identity == selection_identity
            and str(_value(row, "profile_run_id")) == str(selection["profile_run_id"])
            and str(_value(row, "profile_stage")) == str(selection["profile_stage"])
        ):
            filtered.append(row)
    if not filtered:
        raise ValueError("The selected successful profile has no column rows in METADATA_DATA_PROFILED.")
    return filtered

def _latest_row(rows: list[dict[str, Any]], *order_fields: str) -> dict[str, Any] | None:
    """Return the latest row using lexicographic string timestamps/ids."""
    if not rows:
        return None
    return max(rows, key=lambda row: tuple(str(_value(row, field)) for field in order_fields))

def _status_is_failed(value: Any) -> bool:
    return str(value or "").strip().lower() in {"failed", "fail", "error", "errors", "rejected"}

def _status_is_warning(value: Any) -> bool:
    return str(value or "").strip().lower() in {"warning", "warnings", "needs_remediation", "drift"}

def _read_metadata_rows(config: Any, env: str, table: str, *, spark_session: Any) -> list[dict[str, Any]]:
    return _coerce_rows(read_lakehouse_table_core(table, target="metadata", schema=configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, spark_session=spark_session))

def _evaluate_governance_readiness(
    config: Any,
    env: str,
    selection: dict[str, Any],
    *,
    spark_session: Any,
    reviewed_by: str | None = None,
) -> dict[str, Any]:
    """Evaluate persisted evidence readiness without writing a metadata table.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration used for metadata lakehouse routing.
    env : str
        Environment key in ``config``.
    selection : dict[str, Any]
        Catalogue-table selection returned by ``get_selected_catalogue_table``.
    spark_session : pyspark.sql.SparkSession
        Spark session used to read metadata tables.
    reviewed_by : str, optional
        Reviewer identity. Runtime user metadata is used when omitted.

    Returns
    -------
    dict[str, Any]
        Readiness summary row plus blocker, warning, and evidence details.

    Notes
    -----
    The function intentionally re-reads agreement, catalogue, pipeline-run, and
    evidence metadata from the configured ``metadata`` target so review notebooks can run in a separate session after ``02_pipeline``.

    """
    profile_rows = load_catalogue_profile_rows(config, env, selection, spark_session=spark_session)
    first_profile = profile_rows[0]
    dataset_name = str(_value(first_profile, "dataset_name") or selection.get("dataset_name") or "")
    table_name = str(_value(first_profile, "table_name") or selection.get("table_name") or "")
    table_key = str(_value(first_profile, "metadata_table_key") or selection.get("metadata_table_key") or config_shared.build_metadata_table_key(
        _value(first_profile, "store_type", selection.get("store_type", "lakehouse")),
        _value(first_profile, "layer", selection.get("layer", selection.get("fabric_store_target", ""))),
        _value(first_profile, "schema_name", selection.get("schema_name")), table_name,
    ))
    profile_run_id = str(_value(first_profile, "profile_run_id") or selection.get("profile_run_id") or "")
    profile_stage = str(_value(first_profile, "profile_stage") or selection.get("profile_stage") or "")
    agreement_id = str(_value(first_profile, "agreement_id") or _value(first_profile, "AGREEMENT_ID") or "")
    agreement_version = str(_value(first_profile, "agreement_version") or _value(first_profile, "AGREEMENT_CONTRACT_VERSION") or "")

    pipeline_rows: list[dict[str, Any]] = []
    related_pipeline_rows: list[dict[str, Any]] = []
    latest_pipeline = None

    agreement_rows = [
        row for row in _read_metadata_rows(config, env, DATA_AGREEMENT_TABLE, spark_session=spark_session)
        if agreement_id and str(_value(row, "agreement_id")) == agreement_id
        and (not agreement_version or str(_value(row, "agreement_version")) == agreement_version)
    ]
    blockers: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    def _append_once(items: list[dict[str, str]], *, code: str, message: str) -> None:
        if not any(item.get("code") == code for item in items):
            items.append({"code": code, "message": message})

    if not agreement_id:
        _append_once(blockers, code="missing_agreement_id", message="Catalogue evidence is not linked to an agreement.")
    elif not agreement_rows:
        _append_once(blockers, code="missing_agreement_metadata", message="No matching agreement metadata row was found.")
    dq_statuses = {str(_value(row, "dq_status") or "").lower() for row in profile_rows}
    dq_error_count = sum(int(_value(row, "dq_error_rule_count", 0) or 0) for row in profile_rows)
    dq_failed_count = sum(int(_value(row, "dq_failed_rule_count", 0) or 0) for row in profile_rows)
    if "failed" in dq_statuses or dq_error_count > 0:
        _append_once(blockers, code="dq_failed", message="Failed DQ evidence blocks approval.")
    elif "warning" in dq_statuses or dq_failed_count > 0:
        _append_once(warnings, code="dq_warning", message="DQ warning evidence requires remediation review.")

    if latest_pipeline is not None:
        pipeline_dq_status = _value(latest_pipeline, "dq_status")
        if _status_is_failed(pipeline_dq_status):
            _append_once(blockers, code="dq_failed", message="Pipeline DQ status blocks approval.")
        elif _status_is_warning(pipeline_dq_status):
            _append_once(warnings, code="dq_warning", message="Pipeline DQ status requires remediation review.")

        for field in ("source_guardrail_status", "target_guardrail_status"):
            status = _value(latest_pipeline, field)
            if _status_is_failed(status):
                blockers.append({"code": f"{field}_failed", "message": f"{field} is {status}; schema drift or guardrail failure is present."})
            elif _status_is_warning(status):
                warnings.append({"code": f"{field}_warning", "message": f"{field} is {status}; schema drift is surfaced for review."})

    outcome = "rejected" if blockers else ("needs_remediation" if warnings else "approved")
    reviewed_at = _audit_timestamp_value(config)
    actor = _resolve_action_by(reviewed_by)
    audit = build_runtime_audit_fields(config=config, env=env, committed_by=actor, committed_at=reviewed_at)
    evidence_summary = {
        "agreement_row_count": len(agreement_rows),
        "profile_column_count": len(profile_rows),
        "pipeline_run_count": len(pipeline_rows),
        "related_pipeline_run_count": len(related_pipeline_rows),
        "prior_pipeline_run_ids": [str(_value(row, "run_id")) for row in related_pipeline_rows if str(_value(row, "run_id")) != profile_run_id],
        "latest_pipeline_run": latest_pipeline or {},
    }
    row = {
        "review_id": f"{profile_run_id or 'profile'}-{uuid.uuid4().hex[:12]}",
        "environment_name": env,
        "dataset_name": dataset_name,
        "table_name": table_name,
        "metadata_table_key": table_key,
        "profile_run_id": profile_run_id,
        "profile_stage": profile_stage,
        "pipeline_run_id": str(_value(latest_pipeline or {}, "run_id")),
        "agreement_id": agreement_id,
        "agreement_version": agreement_version,
        "outcome": outcome,
        "blocker_count": len(blockers),
        "warning_count": len(warnings),
        "blockers_json": json.dumps(blockers, sort_keys=True),
        "warnings_json": json.dumps(warnings, sort_keys=True),
        "evidence_summary_json": json.dumps(evidence_summary, default=str, sort_keys=True),
        "reviewed_at": reviewed_at,
        "reviewed_by": actor,
        **audit,
    }
    return {"review": row, "outcome": outcome, "blockers": blockers, "warnings": warnings, "evidence_summary": evidence_summary}

def record_table_governance(
    config: Any,
    env: str,
    profile_rows: list[dict[str, Any]],
    *,
    spark_session: Any,
    guardrail_rule_reviews: list[dict[str, Any]] | None = None,
    approved_by: str | None = None,
    readiness_selection: dict[str, Any] | None = None,
    evaluate_readiness: bool = False,
    mode: str = "append",
) -> dict[str, Any]:
    """Persist governed guardrail rule intent.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Shared ``00_env_config`` configuration that routes metadata writes to
        the configured metadata lakehouse target.
    env : str
        Environment key in ``config``.
    profile_rows : list of dict
        Column-profile rows loaded for the selected catalogue table.
    spark_session : pyspark.sql.SparkSession
        Spark session used to create DataFrames for metadata writes.
    guardrail_rule_reviews : list of dict, optional
        Human-reviewed guardrail rule rows. DQ rows use
        ``review_status="governance_approved"`` and are written only to
        ``METADATA_GUARDRAIL``.
    approved_by : str, optional
        Reviewer identity to stamp on records. When omitted, runtime defaults
        are used.
    readiness_selection : dict, optional
        Catalogue selection used to evaluate non-persistent readiness evidence.
    evaluate_readiness : bool, default=False
        Whether to return a readiness summary after checking agreement,
        pipeline, schema/profile, and DQ evidence. No metadata table is written.
    mode : str, default "append"
        Write mode for metadata table commits.

    Returns
    -------
    dict[str, Any]
        Records written for ``guardrail_rules`` plus an optional non-persistent
        ``readiness_summary``.

    """
    guardrail_records = _build_dq_rule_records(
        profile_rows,
        guardrail_rule_reviews or [],
        config=config,
        env=env,
        approved_by=approved_by,
    )
    writes = {GUARDRAIL_TABLE: [dict(record, guardrail_type=record.get("guardrail_type") or "dq") for record in guardrail_records]}
    for table_name, records in writes.items():
        if records:
            write_lakehouse_table_core(spark_session.createDataFrame([coerce_metadata_row_types(table_name, record) for record in records]), table_name, target="metadata", schema=configured_lakehouse_schema(config, env, "metadata"), context={"config": config, "env": env}, mode=mode)

    readiness_summary = None
    if evaluate_readiness:
        if readiness_selection is None:
            raise ValueError("readiness_selection is required when evaluate_readiness=True.")
        readiness_summary = _evaluate_governance_readiness(
            config,
            env,
            readiness_selection,
            spark_session=spark_session,
            reviewed_by=approved_by,
        )

    return {
        "guardrail_rules": guardrail_records,
        "readiness_summary": readiness_summary,
    }

def build_table_governance_policy_record(state: Mapping[str, Any], *, governance_mode: str, approval_policy: str | None = None, actor: str | None = None, reason: str = "", config: Any = None) -> dict[str, Any]:
    """Build a table-level governance policy row.

    Parameters
    ----------
    state : mapping
        Table identity state containing environment, dataset, table, and table key.
    governance_mode : {"governed", "ungoverned"}
        Desired table governance mode.
    approval_policy : str, optional
        Approval policy. Defaults to approval-required with bypass for governed
        tables and no approval required for ungoverned tables.
    actor : str, optional
        Reviewer identity.
    reason : str, optional
        Human-readable policy reason.
    config : Any, optional
        Runtime configuration used for timestamps.

    Returns
    -------
    dict[str, Any]
        table governance policy dictionary for catalogue-backed selected state.

    """
    mode = str(governance_mode or "ungoverned").lower()
    if mode not in {"governed", "ungoverned"}:
        raise ValueError("governance_mode must be governed or ungoverned")
    policy = str(approval_policy or ("approval_required_with_bypass" if mode == "governed" else "no_approval_required"))
    now = _audit_timestamp_value(config)
    return {
        "review_id": str(uuid.uuid4()),
        "environment_name": str(state.get("environment_name") or ""),
        "dataset_name": str(state.get("dataset_name") or ""),
        "table_name": str(state.get("table_name") or ""),
        "metadata_table_key": str(state.get("metadata_table_key") or ""),
        "profile_run_id": str(state.get("profile_run_id") or ""),
        "profile_stage": str(state.get("profile_stage") or ""),
        "outcome": "policy_updated",
        "blocker_count": 0,
        "warning_count": 0,
        "blockers_json": "[]",
        "warnings_json": "[]",
        "evidence_summary_json": json.dumps({"policy_reason": reason}, sort_keys=True),
        "reviewed_at": now,
        "reviewed_by": _resolve_action_by(actor),
        "governance_mode": mode,
        "approval_policy": policy,
        "governance_status": "active",
        "approval_bypass_allowed": policy == "approval_required_with_bypass",
        "requires_post_review": False,
        "policy_reason": reason,
        "effective_from": now,
        "effective_to": "",
    }

def mark_table_governed(state: Mapping[str, Any], *, actor: str | None = None, reason: str = "", approval_policy: str = "approval_required_with_bypass", config: Any = None) -> dict[str, Any]:
    """Return an active governed table policy row."""
    return build_table_governance_policy_record(state, governance_mode="governed", approval_policy=approval_policy, actor=actor, reason=reason, config=config)

def mark_table_ungoverned(state: Mapping[str, Any], *, actor: str | None = None, reason: str = "", config: Any = None) -> dict[str, Any]:
    """Return an active ungoverned table policy row."""
    return build_table_governance_policy_record(state, governance_mode="ungoverned", approval_policy="no_approval_required", actor=actor, reason=reason, config=config)


# DQ authoring record helpers migrated to widget ownership.

def _canonical_dq_rule_type(rule_type: Any) -> str:
    return str(rule_type or "").strip()


def _normalize_dq_severity(severity: Any) -> str:
    value = str(severity or "warning").strip().lower()
    return "error" if value in {"blocking", "error"} else "warning"


def _dq_rule_parameter_payload(rule: dict[str, Any], columns: list[str]) -> dict[str, Any]:
    """Return rule parameters stored inside ``rule_parameters_json``."""
    metadata_fields = {
        "rule_key", "rule_id", "metadata_column_key", "metadata_table_key", "environment_name", "dataset_name",
        "table_name", "column_name", "rule_type", "rule_parameters", "rule_parameters_json", "severity",
        "description", "is_active", "review_status", "approved_by", "approved_at", "suggestion_json",
        "suggestion", "action_type", "commit", "_committed_at", "_committed_by", "_workspace_id", "_workspace_name",
        "_notebook_id", "_notebook_name", "_metadata_lakehouse_name", "_activity_id",
    }
    payload: dict[str, Any] = {"columns": columns}
    raw = rule.get("rule_parameters") or rule.get("rule_parameters_json") or {}
    if isinstance(raw, str) and raw.strip():
        try:
            raw = json.loads(raw)
        except Exception:
            raw = {}
    if isinstance(raw, dict):
        payload.update(raw)
    for key, value in rule.items():
        if key not in metadata_fields and value is not None:
            payload[key] = value
    payload["columns"] = columns
    return payload

def _build_dq_rule_records(profile_rows: list[dict[str, Any]], reviewed_rules: list[dict[str, Any]], *, config: Any = None, env: str | None = None, approved_by: str | None = None) -> list[dict[str, Any]]:
    """Build append-only governance-approved DQ-rule records without enforcing them."""
    profile, actor, now, audit = _approved_review_context(profile_rows, config=config, env=env, approved_by=approved_by)
    rows = []
    for rule in reviewed_rules or []:
        if not rule.get("commit"):
            continue
        review_status = str(rule.get("review_status", "governance_approved")).lower()
        action_type = str(rule.get("action_type") or ("created" if rule.get("is_active", True) else "deactivated")).lower()
        if action_type == "delete":
            action_type = "deactivated"
        if action_type not in {"created", "updated", "deactivated", "reactivated"}:
            raise ValueError(f"Unsupported DQ action_type: {action_type}")
        is_active = bool(rule.get("is_active", action_type != "deactivated"))
        if action_type == "deactivated":
            is_active = False
        if action_type == "reactivated":
            is_active = True
        if review_status != "governance_approved":
            continue
        draft = dict(rule)
        draft["rule_type"] = _canonical_dq_rule_type(draft.get("rule_type"))
        columns = draft.get("columns") or ([draft.get("column_name")] if draft.get("column_name") else [])
        if isinstance(columns, str):
            columns = [c.strip() for c in columns.split(",") if c.strip()]
        draft["columns"] = list(columns or [])
        from fabricops_kit.pipeline.guardrails_shared import _validate_dq_rules
        _validate_dq_rules([draft])
        columns = [str(c) for c in draft.get("columns", [])]
        display_column = str(rule.get("column_name") or ", ".join(columns) or "")
        primary_column = columns[0] if columns else display_column
        identity = _approved_column_identity(profile.get(primary_column, {}), {**rule, "column_name": display_column, "columns": columns}, env=env)
        identity["column_name"] = display_column
        params = _dq_rule_parameter_payload(draft, columns)
        identity_hash = hashlib.sha256(_json(params).encode("utf-8")).hexdigest()[:12]
        rule_id = str(
            rule.get("rule_id")
            or f"{identity['table_name']}.{display_column or 'table'}.{draft['rule_type']}.{identity_hash}"
        )
        rows.append({
            "rule_key": str(rule.get("rule_key") or _build_dq_rule_key(identity["environment_name"], identity["dataset_name"], identity["table_name"], rule_id)),
            "rule_id": rule_id,
            **identity,
            "guardrail_type": str(rule.get("guardrail_type") or "dq"),
            "rule_type": draft["rule_type"],
            "rule_parameters_json": _json(params),
            "severity": _normalize_dq_severity(draft.get("severity")),
            "description": str(rule.get("description") or ""),
            "is_active": is_active,
            "review_status": str(rule.get("target_review_status") or "governance_approved"),
            "author_role": str(rule.get("author_role") or "governance_reviewer"),
                                    "approved_by": str(rule.get("approved_by") or actor),
            "approved_at": str(rule.get("approved_at") or now),
            "suggestion_json": _json(rule.get("suggestion_json") or rule.get("suggestion")),
            "action_type": action_type,
            "source_notebook_type": str(rule.get("source_notebook_type") or "01_governance"),
            "source_notebook_id": str(rule.get("source_notebook_id") or ""),
            "source_workspace_id": str(rule.get("source_workspace_id") or ""),
            "superseded_by_rule_key": str(rule.get("superseded_by_rule_key") or ""),
            "notes": str(rule.get("notes") or ""),
            **audit,
        })
    return rows


# Shared catalogue-selection widget implementation.
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
PROFILE_TABLE = "METADATA_DATA_PROFILED"
PROFILE_FREQUENCY_TABLE = "METADATA_DATA_PROFILED_FREQUENCY"


def collect_catalogue_inventory(catalogue: Any, environment_name: str) -> list[dict[str, Any]]:
    """Collect distinct dataset-version observations in the active environment."""
    from pyspark.sql import functions as F

    fields = [
        "metadata_table_key", "schema_fingerprint", "environment_name", "store_type",
        "layer", "schema_name", "table_name", "_committed_at",
    ]
    return [
        row.asDict(recursive=True)
        for row in catalogue.filter(F.col("environment_name") == environment_name)
        .select(*fields).distinct().collect()
        if str(row["metadata_table_key"] or "").strip()
    ]


def dataset_label(row: dict[str, Any], role: str | None = None) -> str:
    """Build the consistent physical dataset label, optionally tagged by role."""
    location = " / ".join(
        str(row.get(field) or "").strip()
        for field in ("layer", "schema_name", "table_name")
        if str(row.get(field) or "").strip()
    ) or str(row.get("metadata_table_key") or "")
    return f"[{role}] {location}" if role else location


def schema_version_options(rows: list[dict[str, Any]], metadata_table_key: str) -> list[tuple[str, str]]:
    """Return deterministic newest-first schema choices for one dataset."""
    versions: dict[str, Any] = {}
    for row in rows:
        if str(row.get("metadata_table_key") or "") != metadata_table_key:
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


def build_catalogue_widget(
    *, title: str, description: str, selection_context: dict[str, Any], display_context: dict[str, Any],
    inventory_rows: list[dict[str, Any]],
    role_options: list[tuple[str | None, str]] | None, target: str, schema: str | None,
    spark_session: Any, runtime_context: dict[str, Any], empty_message: str,
) -> dict[str, Any]:
    """Build common controls and snapshot-scoped catalogue/profile readers."""
    widgets = require_ipywidgets()
    rows_by_key: dict[str, list[dict[str, Any]]] = {}
    for row in inventory_rows:
        rows_by_key.setdefault(str(row["metadata_table_key"]), []).append(row)
    roles = role_options or [(None, key) for key in sorted(rows_by_key)]
    options: list[tuple[str, str]] = []
    option_context: dict[str, tuple[str | None, str]] = {}
    for role, key in roles:
        if key not in rows_by_key:
            continue
        latest = max(rows_by_key[key], key=lambda row: (str(row.get("_committed_at") or ""), str(row.get("schema_fingerprint") or "")))
        value = f"{role or ''}\x1f{key}"
        options.append((dataset_label(latest, role), value))
        option_context[value] = (role, key)
    options.sort(key=lambda item: (item[0].casefold(), item[1]))
    search = widgets.Text(value="", placeholder="Search catalogues", **widget_common(widgets, "Search"))
    dataset = widgets.Dropdown(options=options, **widget_common(widgets, "Dataset"))
    version = widgets.Dropdown(options=[], **widget_common(widgets, "Schema version"))
    profile_column = widgets.Dropdown(options=[], **widget_common(widgets, "Profile column"))
    for control in (search, dataset, version, profile_column):
        control.layout = widgets.Layout(width="100%", height="auto", overflow="visible")
    selection_details = widgets.HTML(value="")
    status = widgets.HTML(value="")
    controls = {
        "search": search,
        "dataset": dataset,
        "schema_fingerprint": version,
        "metadata_column_key": profile_column,
    }
    state: dict[str, Any] = {"get_selection": None, "get_views": None, "refresh": None, "_controls": controls, "error": None}
    source_frames: dict[str, Any] = {}
    current_frames: dict[str, Any] = {}
    selected_profiled_at: Any = None
    last_dataset_value = str(dataset.value or "")
    filtering_options = False

    def get_selection() -> dict[str, Any]:
        """Return current control values and entry-point context."""
        role, key = option_context.get(str(dataset.value or ""), (None, ""))
        selected_rows = rows_by_key.get(key, [])
        latest = max(selected_rows, key=lambda row: (str(row.get("_committed_at") or ""), str(row.get("schema_fingerprint") or "")), default={})
        return {
            **selection_context, "metadata_table_key": key or None,
            "schema_fingerprint": version.value, "dataset_label": dataset_label(latest, role) if latest else None,
            "profiled_at": selected_profiled_at, "metadata_column_key": profile_column.value,
            "profile_role": role, "store_type": latest.get("store_type"), "layer": latest.get("layer"),
            "schema_name": latest.get("schema_name"), "table_name": latest.get("table_name"),
        }

    def get_views():
        """Return the selected catalogue, compact profile, and frequency frames."""
        selection = get_selection()
        key = selection["metadata_table_key"]
        fingerprint = selection["schema_fingerprint"]
        if not key or not fingerprint:
            raise ValueError(empty_message)
        if not source_frames:
            source_frames.update({
                "catalogue": read_lakehouse_table_core(
                    CATALOGUE_TABLE, target=target, schema=schema,
                    spark_session=spark_session, context=runtime_context,
                ),
                "profile": read_lakehouse_table_core(
                    PROFILE_TABLE, target=target, schema=schema,
                    spark_session=spark_session, context=runtime_context,
                ),
                "frequency": read_lakehouse_table_core(
                    PROFILE_FREQUENCY_TABLE, target=target, schema=schema,
                    spark_session=spark_session, context=runtime_context,
                ),
            })
            refresh_loaded_views()
        catalogue = current_frames["catalogue"]
        profile = current_frames["profile"]
        frequency = current_frames["frequency"]
        catalogue_order = [name for name in ("column_name", "metadata_column_key", "_committed_at") if name in catalogue.columns]
        profile_order = [name for name in ("column_name", "metadata_column_key", "profiled_at", "_committed_at") if name in profile.columns]
        frequency_order = [name for name in ("frequency_rank", "value", "_committed_at") if name in frequency.columns]
        return {
            "catalogue": catalogue.orderBy(*catalogue_order),
            "profile": profile.orderBy(*profile_order),
            "frequency": frequency.orderBy(*frequency_order),
        }

    def refresh_loaded_views() -> None:
        """Filter cached source frames for the active dataset and snapshot."""
        nonlocal selected_profiled_at
        from pyspark.sql import functions as F

        _role, key = option_context.get(str(dataset.value or ""), (None, ""))
        fingerprint = version.value
        catalogue = source_frames["catalogue"].filter(
            (F.col("metadata_table_key") == key) & (F.col("schema_fingerprint") == fingerprint)
        )
        profile_for_dataset = source_frames["profile"].filter(
            (F.col("metadata_table_key") == key) & (F.col("schema_fingerprint") == fingerprint)
        )
        latest_rows = (
            profile_for_dataset.filter(F.col("profiled_at").isNotNull())
            .select("profiled_at").distinct().orderBy(F.col("profiled_at").desc()).limit(1).collect()
        )
        selected_profiled_at = latest_rows[0]["profiled_at"] if latest_rows else None
        if selected_profiled_at is None:
            profile_snapshot = profile_for_dataset.limit(0)
            frequency_snapshot = source_frames["frequency"].filter(F.lit(False))
            column_options: list[tuple[str, str]] = []
            frequency_keys: set[str] = set()
        else:
            profile_snapshot = profile_for_dataset.filter(F.col("profiled_at") == selected_profiled_at)
            column_rows = profile_snapshot.select("metadata_column_key", "column_name").distinct().collect()
            column_options = sorted(
                ((str(row["column_name"] or row["metadata_column_key"]), str(row["metadata_column_key"])) for row in column_rows),
                key=lambda option: (option[0].casefold(), option[1]),
            )
            profile_keys = [value for _label, value in column_options]
            frequency_snapshot = source_frames["frequency"].filter(
                (F.col("profiled_at") == selected_profiled_at)
                & F.col("metadata_column_key").isin(profile_keys)
            )
            frequency_keys = {
                str(row["metadata_column_key"])
                for row in frequency_snapshot.select("metadata_column_key").distinct().collect()
            }
        previous_column = str(profile_column.value or "")
        profile_column.options = column_options
        column_values = [value for _label, value in column_options]
        preferred_column = next((value for value in column_values if value in frequency_keys), None)
        profile_column.value = (
            previous_column if previous_column in column_values
            else preferred_column or (column_values[0] if column_values else None)
        )
        selected_key = profile_column.value
        selected_frequency = frequency_snapshot.filter(
            (F.col("metadata_column_key") == selected_key)
            & (F.col("profiled_at") == selected_profiled_at)
        ) if selected_key and selected_profiled_at is not None else frequency_snapshot.limit(0)
        current_frames.update({
            "catalogue": catalogue,
            "profile": profile_snapshot,
            "frequency_snapshot": frequency_snapshot,
            "frequency": selected_frequency,
        })
        state.update(get_selection())
        state["error"] = None if key else empty_message
        selection = get_selection()
        selection_details.value = (
            f"<b>Dataset:</b> {_html_escape(selection['dataset_label'])}<br>"
            f"<b>Schema version:</b> {_html_escape(selection['schema_fingerprint'])}<br>"
            f"<b>Profile snapshot:</b> {_html_escape(selection['profiled_at'])}<br>"
            f"<b>Profile column:</b> {_html_escape(selection['metadata_column_key'])}"
            if key else ""
        )
        status.value = (
            "No compact profile snapshot is available for this dataset."
            if key and selected_profiled_at is None
            else "Selection ready. Run get_views() in the next cell to load native Spark DataFrames."
            if key
            else empty_message
        )

    def refresh(*_args: Any) -> None:
        """Synchronize lightweight selection state and filter loaded frames."""
        nonlocal selected_profiled_at
        _role, key = option_context.get(str(dataset.value or ""), (None, ""))
        choices = schema_version_options(inventory_rows, key)
        current = str(version.value or "")
        version.options = choices
        values = [value for _label, value in choices]
        version.value = current if current in values else (values[0] if values else None)
        if source_frames:
            refresh_loaded_views()
            return
        selected_profiled_at = None
        profile_column.options = []
        state.update(get_selection())
        state["error"] = None if key else empty_message
        selection = get_selection()
        selection_details.value = (
            f"<b>Dataset:</b> {_html_escape(selection['dataset_label'])}<br>"
            f"<b>Schema version:</b> {_html_escape(selection['schema_fingerprint'])}<br>"
            "<b>Profile snapshot:</b> Load views to resolve<br>"
            "<b>Profile column:</b> Load views to resolve"
            if key else ""
        )
        status.value = (
            "Selection ready. Run get_views() in the next cell to load native Spark DataFrames."
            if key else empty_message
        )

    def refresh_frequency(*_args: Any) -> None:
        """Restrict normalized frequencies to the selected snapshot column."""
        from pyspark.sql import functions as F

        frequency = current_frames.get("frequency_snapshot")
        if frequency is None:
            return
        selected_key = profile_column.value
        current_frames["frequency"] = frequency.filter(
            (F.col("metadata_column_key") == selected_key)
            & (F.col("profiled_at") == selected_profiled_at)
        ) if selected_key and selected_profiled_at is not None else frequency.limit(0)
        state.update(get_selection())

    def select_dataset(change: dict[str, Any]) -> None:
        """Remember valid selections and refresh after direct dataset changes."""
        nonlocal last_dataset_value
        selected = str(change.get("new") or "")
        if selected:
            last_dataset_value = selected
        if not filtering_options:
            refresh()

    def filter_options(*_args: Any) -> None:
        """Filter datasets and restore a valid selection automatically."""
        nonlocal filtering_options, last_dataset_value
        query = str(search.value or "").strip().casefold()
        filtered = [option for option in options if query in option[0].casefold()]
        filtered_values = [value for _label, value in filtered]
        filtering_options = True
        try:
            dataset.options = filtered
            dataset.value = (
                last_dataset_value if last_dataset_value in filtered_values
                else filtered_values[0] if filtered_values
                else None
            )
        finally:
            filtering_options = False
        if dataset.value:
            last_dataset_value = str(dataset.value)
        refresh()

    state.update({"get_selection": get_selection, "get_views": get_views, "refresh": refresh})
    refresh()
    dataset.observe(lambda change: select_dataset(change) if change.get("name") == "value" else None, names="value")
    version.observe(lambda change: refresh() if change.get("name") == "value" else None, names="value")
    profile_column.observe(lambda change: refresh_frequency() if change.get("name") == "value" else None, names="value")
    search.observe(lambda change: filter_options() if change.get("name") == "value" else None, names="value")
    context_html = "<br>".join(
        f"<b>{_html_escape(name)}:</b> {_html_escape(value)}"
        for name, value in display_context.items()
        if value not in (None, "")
    )
    from IPython import display as ip
    context_section = form_section(widgets, title="Context", children=[widgets.HTML(value=context_html)])
    selection_section = form_section(
        widgets,
        title="Catalogue selection",
        children=[form_grid(widgets, [search, dataset, version, profile_column])],
    )
    selected_section = form_section(
        widgets,
        title="Selected catalogue",
        children=[selection_details, status],
    )
    ip.display(
        form_page(
            widgets,
            title=title,
            description=description,
            children=[context_section, selection_section, selected_section],
        )
    )
    return state


def catalogue_table_options(rows: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Return deterministic, uniquely labelled logical catalogue tables.

    Canonical ``metadata_table_key`` values remain the option values.  Labels
    use the physical catalogue coordinates and add the environment and a short
    key only when the readable coordinates are not unique.
    """
    latest: dict[str, dict[str, Any]] = {}
    for raw in rows:
        row = dict(raw)
        key = str(row.get("metadata_table_key") or "").strip()
        if not key:
            continue
        rank = tuple(
            str(row.get(field) or "")
            for field in ("_committed_at", "_activity_id", "schema_fingerprint", "metadata_column_key")
        )
        current = latest.get(key)
        if current is None or rank > current["_browser_rank"]:
            row["_browser_rank"] = rank
            latest[key] = row

    def base_label(row: Mapping[str, Any]) -> str:
        table = str(row.get("table_name") or "(unnamed table)")
        location = " / ".join(
            value for value in (
                str(row.get("layer") or "").strip(),
                str(row.get("schema_name") or "").strip(),
            ) if value
        )
        return f"{table} — {location}" if location else table

    counts = Counter(base_label(row) for row in latest.values())
    options = []
    for key, raw in latest.items():
        row = {name: value for name, value in raw.items() if name != "_browser_rank"}
        label = base_label(row)
        if counts[label] > 1:
            environment = str(row.get("environment_name") or "").strip()
            store = str(row.get("store_type") or "").strip()
            context = " / ".join(value for value in (environment, store) if value)
            label = f"{label} ({context or key})"
        options.append({**row, "metadata_table_key": key, "label": label})
    return sorted(options, key=lambda row: (str(row["label"]).casefold(), str(row["metadata_table_key"])))


def catalogue_table_browser_state(
    catalogue_rows: Iterable[Mapping[str, Any]],
    metadata_table_key: str,
    current_enrichment: Mapping[tuple[str, str, str], Mapping[str, Any]],
) -> dict[str, Any]:
    """Resolve the latest complete schema and historical columns for a table."""
    key = str(metadata_table_key or "").strip()
    if not key:
        raise ValueError("The selected logical table is missing metadata_table_key.")
    rows = [dict(row) for row in catalogue_rows if str(row.get("metadata_table_key") or "") == key]
    if not rows:
        raise ValueError("The selected logical table has no catalogue schema rows.")

    def rank(row: Mapping[str, Any]) -> tuple[str, ...]:
        return tuple(
            str(row.get(field) or "")
            for field in ("_committed_at", "_activity_id", "schema_fingerprint", "metadata_column_key")
        )

    latest_event = max(rows, key=rank)
    fingerprint = str(latest_event.get("schema_fingerprint") or "").strip()
    if not fingerprint:
        raise ValueError("The selected logical table has no latest schema fingerprint.")
    latest_rows = [row for row in rows if str(row.get("schema_fingerprint") or "") == fingerprint]
    current_keys = {str(row.get("metadata_column_key") or "").strip() for row in latest_rows}
    observations: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        column_key = str(row.get("metadata_column_key") or "").strip()
        if column_key:
            observations.setdefault(column_key, []).append(row)
    columns = []
    for column_key, history in observations.items():
        recent = max(history, key=rank)
        first = min(history, key=rank)
        level_values = {
            enrichment_type: str(current_enrichment.get(("column", column_key, enrichment_type), {}).get("value") or "")
            for enrichment_type in ("Description", "Classification", "Personal_identifier")
        }
        columns.append({
            "column_name": str(recent.get("column_name") or ""),
            "metadata_column_key": column_key,
            "data_type": str(recent.get("data_type") or ""),
            "status": "current" if column_key in current_keys else "removed",
            "first_observed_at": first.get("_committed_at"),
            "last_observed_at": recent.get("_committed_at"),
            "latest_schema_membership": column_key in current_keys,
            "enrichment_values": level_values,
        })
    columns.sort(key=lambda row: (row["status"] != "current", row["column_name"].casefold(), row["metadata_column_key"]))
    identity = dict(max(rows, key=rank))
    table_values = {
        enrichment_type: str(current_enrichment.get(("table", key, enrichment_type), {}).get("value") or "")
        for enrichment_type in ("Description", "Classification")
    }
    return {
        "table_identity": identity,
        "metadata_table_key": key,
        "table_name": str(identity.get("table_name") or ""),
        "latest_schema_fingerprint": fingerprint,
        "latest_schema_timestamp": latest_event.get("_committed_at"),
        "latest_schema_rows": sorted(latest_rows, key=lambda row: (str(row.get("column_name") or "").casefold(), str(row.get("metadata_column_key") or ""))),
        "all_historical_columns": columns,
        "current_columns": [row for row in columns if row["status"] == "current"],
        "removed_columns": [row for row in columns if row["status"] == "removed"],
        "current_enrichment_values": {"table": table_values, "columns": {row["metadata_column_key"]: row["enrichment_values"] for row in columns}},
    }


def render_read_only_catalogue_detail(state: Mapping[str, Any]) -> str:
    """Render schema history and enrichment context without authoring controls."""
    def shown(value: Any) -> str:
        return (
            _html_escape(value) if str(value or "").strip()
            else "<span style='color:#6b7280'>Not provided</span>"
        )

    table_values = state.get("current_enrichment_values", {}).get("table", {})
    table_context = "".join(
        f"<div><b>{_html_escape(name)}:</b> {shown(table_values.get(name))}</div>"
        for name in ("Description", "Classification")
    )

    def column_rows(rows: Iterable[Mapping[str, Any]], *, removed: bool) -> str:
        body = []
        for row in rows:
            enrichment = row.get("enrichment_values", {})
            removed_detail = (
                f"<br><span style='color:#6b7280'><b>Removed</b> · Last observed: "
                f"{shown(row.get('last_observed_at'))}</span>" if removed else ""
            )
            body.append(
                "<tr style='color:#6b7280' >" if removed else "<tr>"
            )
            body.append(
                f"<td>{shown(row.get('column_name'))}{removed_detail}</td>"
                f"<td>{shown(row.get('data_type'))}</td>"
                f"<td>{shown(enrichment.get('Description'))}</td>"
                f"<td>{shown(enrichment.get('Classification'))}</td>"
                f"<td>{shown(enrichment.get('Personal_identifier'))}</td></tr>"
            )
        return "".join(body) or "<tr><td colspan='5'><i>None</i></td></tr>"

    header = (
        "<thead><tr><th>Column</th><th>Type</th><th>Description</th>"
        "<th>Classification</th><th>Personal identifier</th></tr></thead>"
    )
    return (
        f"<h4>{shown(state.get('table_name'))}</h4>"
        "<div><b>metadata_table_key:</b> <code>"
        f"{shown(state.get('metadata_table_key'))}</code></div>"
        "<div><b>Latest fingerprint:</b> <code>"
        f"{shown(state.get('latest_schema_fingerprint'))}</code></div>"
        f"<div><b>Latest schema timestamp:</b> {shown(state.get('latest_schema_timestamp'))}</div>"
        f"<h5>Table enrichment (read-only)</h5>{table_context}"
        "<h5>Current columns</h5><div style='overflow:auto'>"
        f"<table style='width:100%;font-size:12px'>{header}<tbody>"
        f"{column_rows(state.get('current_columns', []), removed=False)}</tbody></table></div>"
        "<h5>Removed columns</h5><div style='overflow:auto'>"
        f"<table style='width:100%;font-size:12px'>{header}<tbody>"
        f"{column_rows(state.get('removed_columns', []), removed=True)}</tbody></table></div>"
    )
