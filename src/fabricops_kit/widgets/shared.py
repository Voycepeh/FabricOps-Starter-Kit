"""Shared widget rendering helpers for FabricOps notebook widgets."""

from __future__ import annotations

from fabricops_kit.io import read_lakehouse_table, write_lakehouse_table

from collections import Counter
from collections.abc import Callable
from dataclasses import dataclass, field as dataclass_field
from datetime import date, datetime, timezone
import hashlib
import json
import logging
from contextlib import contextmanager
from time import perf_counter
from typing import Any, Iterable, Mapping
import uuid

from fabricops_kit.config import shared as config_shared
from fabricops_kit.io.shared import (
    configured_lakehouse_schema,
    resolve_configured_lakehouse_table,
)
from fabricops_kit.config.audit import _audit_timestamp_value, _resolve_action_by, build_runtime_audit_fields
from fabricops_kit.config.metadata_keys import _build_dq_rule_key
from fabricops_kit.config.metadata_schemas import (
    CANONICAL_METADATA_TABLES,
    coerce_metadata_row_types,
    metadata_table_physical_schema,
    metadata_table_schema_registry,
)
from fabricops_kit.pipeline.shared import DQ_RULE_TYPES


_WIDGET_LABEL_WIDTH = "150px"
_WIDGET_FIELD_MAX_WIDTH = "100%"
_WIDGET_STYLE = {"description_width": _WIDGET_LABEL_WIDTH}
_WIDGET_FIELD_MIN_WIDTH = "0"
_WIDGET_FIELD_WIDTH = "100%"
_TEXTAREA_HEIGHT = "80px"
_AUTHORING_PANE_HEIGHT = "560px"
_FORM_PAGE_HEIGHT = "720px"
_STATUS_MIN_HEIGHT = "32px"

_FORM_STYLE = """<style>
.fabricops-form {
    --form-accent:#0f6cbd; --form-tint:#eaf3fb; --form-text:#243449; --form-border:#dce4ed;
    font:13px/1.5 'Segoe UI',Arial,sans-serif; color:var(--form-text);
    background:#f6f8fb; border:1px solid var(--form-border); border-radius:10px;
    padding:20px; gap:16px; container-type:inline-size; scrollbar-gutter:stable;
}
.fabricops-form.fabricops-governance { --form-accent:#6750a4; --form-tint:#f1edf8; }
.fabricops-form, .fabricops-form *, .fabricops-form *::before, .fabricops-form *::after { box-sizing:border-box; }
.fabricops-form > *, .fabricops-form .widget-box > * { flex-shrink:0; }
.fabricops-form .widget-box, .fabricops-form .widget-gridbox { min-width:0; max-width:100%; }
.fabricops-form .widget-vbox { gap:12px; }
.fabricops-form .widget-hbox { gap:12px; flex-wrap:wrap; align-items:center; }
.fabricops-form .widget-inline-hbox:not(.widget-checkbox):not(.widget-html) {
    display:grid; grid-template-columns:minmax(0,1fr); align-items:start; gap:6px;
    width:100% !important; min-width:0 !important; max-width:100% !important; height:auto !important; margin:0;
}
.fabricops-form .widget-inline-hbox > .widget-label {
    width:100% !important; min-width:0 !important; max-width:100% !important;
    height:auto; min-height:0; margin:0; text-align:left; justify-self:start;
    white-space:normal; overflow-wrap:anywhere; font-size:13px; font-weight:600; line-height:1.5;
}
.fabricops-form .widget-label:empty { display:none; }
.fabricops-form .widget-html.widget-inline-hbox { display:block; width:100% !important; max-width:100% !important; margin:0; padding:0; }
.fabricops-form .widget-html-content { width:100%; max-width:none; padding:0; overflow-wrap:anywhere; line-height:1.5; }
.fabricops-form .widget-html:not(.fabricops-status):has(> .widget-html-content:empty),
.fabricops-form .widget-html:has(> .widget-html-content > style:only-child) { display:none; }
.fabricops-form .fabricops-page-header {
    background:var(--form-tint); border-left:4px solid var(--form-accent); border-radius:6px;
    padding:16px 20px; color:var(--form-text);
}
.fabricops-form .fabricops-page-title { font-size:21px; font-weight:650; line-height:1.3; }
.fabricops-form.fabricops-started .fabricops-page-title { display:none; }
.fabricops-form.fabricops-started .fabricops-page-header { display:none; }
.fabricops-form .fabricops-page-description { color:#526477; margin-top:5px; max-width:80ch; }
.fabricops-form .fabricops-section {
    background:#fff; border:1px solid var(--form-border) !important; border-radius:8px;
    padding:20px !important; gap:16px;
}
.fabricops-form .fabricops-section-heading { font-size:14px; font-weight:650; line-height:1.4; color:var(--form-text); }
.fabricops-form .fabricops-authoring-pane { background:#fff; border:1px solid var(--form-border); border-radius:8px; padding:16px; }
.fabricops-form input:not([type=checkbox]), .fabricops-form select, .fabricops-form textarea {
    width:100%; min-width:0; max-width:100%; min-height:36px; border:1px solid #b8c5d3;
    border-radius:5px; padding:7px 10px; background:#fff; color:var(--form-text);
    font:13px/1.5 'Segoe UI',Arial,sans-serif;
}
.fabricops-form .widget-textarea textarea { height:110px; min-height:96px; resize:vertical; }
.fabricops-form .widget-select select { height:130px; padding:5px; }
.fabricops-form .widget-select-multiple select { height:96px; }
.fabricops-form option { padding:6px 8px; }
.fabricops-form input:disabled, .fabricops-form select:disabled,
.fabricops-form textarea:disabled { background:#f2f5f8; color:#657587; }
.fabricops-form .widget-checkbox { display:flex; align-items:center; min-height:36px; min-width:0 !important; width:auto !important; max-width:100% !important; margin:0; }
.fabricops-form .widget-checkbox > .widget-label { display:none; }
.fabricops-form .widget-checkbox .widget-label-basic { display:flex; gap:8px; align-items:center; white-space:normal; margin:0; max-width:100%; }
.fabricops-form .widget-checkbox .widget-label-basic > span { min-width:0; white-space:normal; overflow-wrap:anywhere; }
.fabricops-form .widget-checkbox input { flex:0 0 14px; }
.fabricops-form input[type=checkbox] { width:14px; min-width:14px; height:14px; accent-color:var(--form-accent); }
.fabricops-form .widget-button, .fabricops-form .widget-toggle-button {
    min-height:36px; height:auto; border-radius:5px; padding:7px 14px; margin:0;
    font:600 13px/1.5 'Segoe UI',Arial,sans-serif; box-shadow:none; white-space:normal;
}
.fabricops-form .widget-button {
    width:auto; min-width:120px; max-width:100%; background:#fff; color:#34465b;
    border:1px solid #b8c5d3;
}
.fabricops-form .widget-button.mod-primary { background:var(--form-accent); border-color:var(--form-accent); color:#fff; }
.fabricops-form .widget-button.mod-info { background:#fff; border-color:var(--form-accent); color:var(--form-accent); }
.fabricops-form .widget-button.mod-danger { background:#fff; border-color:#c58a92; color:#a4262c; }
.fabricops-form .widget-button.fabricops-confirm-danger { background:#a4262c; border-color:#a4262c; color:#fff; }
.fabricops-form .widget-button.mod-warning { background:#fff6df; border-color:#9b7415; color:#735600; }
.fabricops-form .widget-button:disabled {
    background:#edf0f4; border-color:#d4dce5; color:#68788a; opacity:1; cursor:not-allowed;
}
.fabricops-form .widget-button:not(:disabled):hover { filter:brightness(.95); }
.fabricops-form :is(input,select,textarea,button,summary):focus-visible { outline:2px solid var(--form-accent); outline-offset:2px; }
.fabricops-form .widget-toggle-buttons > div { display:flex; flex-wrap:wrap; gap:4px; }
.fabricops-form .widget-toggle-buttons .mod-active { background:var(--form-tint); color:var(--form-accent); }
.fabricops-form .fabricops-actions { gap:10px; flex-wrap:wrap; }
.fabricops-form summary { cursor:pointer; padding:7px 0; font-weight:600; color:var(--form-accent); }
.fabricops-form details { min-width:0; max-width:100%; }
.fabricops-form table { width:100%; border-collapse:collapse; font-size:12px; }
.fabricops-form th { background:#f2f5f9; color:#526477; text-align:left; }
.fabricops-form td, .fabricops-form th { padding:10px 12px; border-bottom:1px solid #e8edf3; overflow-wrap:anywhere; }
.fabricops-form pre { white-space:pre-wrap; overflow-wrap:anywhere; }
.fabricops-form .fabricops-document-row { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,2fr) auto; gap:12px; align-items:end; }
@container (max-width:800px) {
    .fabricops-form .fabricops-authoring-workspace, .fabricops-form .fabricops-activation-flow,
    .fabricops-form .fabricops-document-row { grid-template-columns:minmax(0,1fr) !important; }
    .fabricops-form .fabricops-steward-panels { display:grid; grid-template-columns:minmax(0,1fr); }
    .fabricops-form .fabricops-steward-panels > .widget-vbox { width:100% !important; min-width:0 !important; }
}
@media (prefers-reduced-motion:reduce) { .fabricops-form * { scroll-behavior:auto !important; } }
</style>"""


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
    label = str(description or "").strip()
    common: dict[str, Any] = {
        "description": label,
        "style": {
            **_WIDGET_STYLE,
            "description_width": _WIDGET_LABEL_WIDTH if label else "0px",
        },
    }
    layout_class = getattr(widgets_module, "Layout", None)
    if layout_class is not None:
        kwargs = {
            "width": _WIDGET_FIELD_WIDTH,
            "min_width": _WIDGET_FIELD_MIN_WIDTH,
            "max_width": _WIDGET_FIELD_MAX_WIDTH,
        }
        if textarea:
            kwargs["height"] = _TEXTAREA_HEIGHT
        common["layout"] = layout_class(**kwargs)
    return common


def form_page(widgets: Any, *, title: str, description: str, children: Iterable[Any], tone: str = "engineering") -> Any:
    """Compose a bounded notebook form with shared fields and a pastel workflow header."""
    header = widgets.HTML(
        value=(
            _FORM_STYLE
            + '<div class="fabricops-page-header">'
            f'<div class="fabricops-page-title">{_html_escape(title)}</div>'
            f'<div class="fabricops-page-description">{_html_escape(description)}</div>'
            "</div>"
        ),
        layout=widgets.Layout(width="100%", height="auto", overflow="visible"),
    )
    page = widgets.VBox(
        [header, *children],
        layout=widgets.Layout(
            width="100%", min_width="0", max_width="100%",
            height=_FORM_PAGE_HEIGHT, overflow="auto",
        ),
    )
    page.fabricops_page_title = title
    page.fabricops_page_description = description
    page.fabricops_page_tone = tone
    add_class = getattr(page, "add_class", None)
    if callable(add_class):
        add_class("fabricops-form")
        add_class("fabricops-governance" if tone == "governance" else "fabricops-engineering")
    return page


class WidgetStartup:
    """Publish plain HTML before blocking I/O, independently of widget comms.

    Timings describe kernel milestones, not browser paint. A frontend view-count
    acknowledgement records readiness separately when the widget manager supports it.
    Spark always remains on the calling notebook thread.
    """

    def __init__(self, title: str, *, tone: str = "governance"):
        """Submit the themed banner and initial loading state as ordinary HTML."""
        from IPython import display as ip

        self.ip = ip
        self.title = title
        self.started = perf_counter()
        self.timings: dict[str, float] = {}
        self.phase_elapsed = 0.0
        self.logger = logging.getLogger(__name__)
        self.display_id = "fabricops-startup-" + uuid.uuid4().hex
        self.html_available = callable(getattr(ip, "HTML", None))
        accent, tint = ("#6750a4", "#f1edf8") if tone == "governance" else ("#0f6cbd", "#eaf3fb")
        self.banner = (
            '<div style="font:13px/1.5 Segoe UI,Arial,sans-serif;color:#243449;'
            f'background:{tint};border-left:4px solid {accent};padding:16px 20px;border-radius:6px">'
            f'<div style="font-size:21px;font-weight:650">{_html_escape(title)}</div></div>'
        )
        if self.html_available:
            ip.display(ip.HTML(self.banner), display_id=self.display_id + "-banner")
            ip.display(ip.HTML('<p role="status" aria-live="polite">Initializing FabricOps…</p>'),
                       display_id=self.display_id)
        self.mark("first_display_submitted")

    def mark(self, name: str) -> None:
        """Record an elapsed kernel milestone without claiming frontend paint."""
        self.timings[name] = perf_counter() - self.started
        self.logger.info("FabricOps startup %s: %s=%.3fs", self.title, name, self.timings[name])

    @contextmanager
    def phase(self, name: str, message: str):
        """Time one synchronous stage and retain actionable failure output."""
        began = perf_counter()
        if self.html_available:
            self.ip.update_display(self.ip.HTML(f'<p role="status">{_html_escape(message)}</p>'),
                                   display_id=self.display_id)
        try:
            yield
        except BaseException:
            if self.html_available:
                self.ip.update_display(self.ip.HTML(
                    '<p role="alert">Unable to load ' + _html_escape(self.title)
                    + '. Check the active FabricOps configuration, Metadata store access and Spark session, '
                    'then rerun this cell. The original error is reported below.</p>'), display_id=self.display_id)
            self.mark("failed")
            raise
        finally:
            elapsed = perf_counter() - began
            self.phase_elapsed += elapsed
            self.timings[name] = self.timings.get(name, 0.0) + elapsed
            self.logger.info("FabricOps startup %s: %s=%.3fs", self.title, name, self.timings[name])

    def display(self, root: Any) -> None:
        """Populate the output once; keep the already visible banner in place."""
        self.timings["widget_construction"] = max(0.0, perf_counter() - self.started
            - self.phase_elapsed - self.timings["first_display_submitted"])
        self.mark("controls_constructed")
        if self.html_available:
            # Keep the title and description together in the static banner while
            # hiding the duplicate header embedded in the returned widget tree.
            title = getattr(root, "fabricops_page_title", self.title)
            tone = getattr(root, "fabricops_page_tone", "governance")
            description = getattr(root, "fabricops_page_description", "")
            accent, tint = (("#6750a4", "#f1edf8") if tone == "governance"
                            else ("#0f6cbd", "#eaf3fb"))
            subtitle = (
                f'<div style="color:#526477;margin-top:5px;max-width:80ch">'
                f'{_html_escape(description)}</div>'
                if description else ""
            )
            self.banner = (
                '<div style="font:13px/1.5 Segoe UI,Arial,sans-serif;color:#243449;'
                f'background:{tint};border-left:4px solid {accent};padding:16px 20px;border-radius:6px">'
                f'<div style="font-size:21px;font-weight:650">{_html_escape(title)}</div>'
                f'{subtitle}</div>'
            )
            self.ip.update_display(self.ip.HTML(self.banner), display_id=self.display_id + "-banner")
            root.add_class("fabricops-started")
            if hasattr(root, "_view_count"):
                root._view_count = 0

                def viewed(change):
                    if change["new"] and "interactive_ready" not in self.timings:
                        self.mark("interactive_ready")
                        root.unobserve(viewed, names="_view_count")

                root.observe(viewed, names="_view_count")
            self.ip.update_display(root, display_id=self.display_id)
        else:
            self.ip.display(root)
        root.startup_timings = self.timings
        self.mark("form_display_submitted")


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
    add_class = getattr(message, "add_class", None)
    if callable(add_class):
        add_class("fabricops-status")
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
    pane = bounded_region(widgets, [heading, *children])
    add_class = getattr(pane, "add_class", None)
    if callable(add_class):
        add_class("fabricops-authoring-pane")
    return pane


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
    """Group naturally expanding form content in one consistent FabricOps section."""
    heading = widgets.HTML(
        value=f'<div class="fabricops-section-heading">{_html_escape(title)}</div>',
        layout=widgets.Layout(width="100%", height="auto", overflow="visible"),
    )
    section = widgets.VBox(
        [heading, *children],
        layout=widgets.Layout(
            width="100%", height="auto", overflow="visible",
            border="1px solid #dce4ed", padding="20px",
        ),
    )
    add_class = getattr(section, "add_class", None)
    if callable(add_class):
        add_class("fabricops-section")
    return section


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
    row = widgets.HBox(
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

    add_class = getattr(row, "add_class", None)
    if callable(add_class):
        add_class("fabricops-actions")
    return row


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
    """Render a compact searchable combobox backed by stable row values."""
    del max_results, search_fields, search_label

    combobox = widgets.Combobox(
        value="",
        options=[],
        placeholder=placeholder,
        ensure_option=True,
        **widget_common(widgets, label),
    )
    selector = widgets.Select(options=[])
    context = widgets.HTML(value="")
    lookup: dict[str, dict[str, Any]] = {}
    labels_by_value: dict[str, str] = {}
    values_by_label: dict[str, str] = {}
    indexed_rows: list[dict[str, Any]] = []
    syncing = False

    def _context_html(row: dict[str, Any] | None) -> str:
        if not row or not context_fields:
            return ""
        parts = [
            f"<b>{_html_escape(field_label)}:</b> {_html_escape(row.get(field, ''))}"
            for field, field_label in context_fields
        ]
        return "<br>".join(parts)

    def _unique_label(base_label: str, value: str) -> str:
        candidate = base_label
        if candidate not in values_by_label:
            return candidate
        if values_by_label[candidate] == value:
            return candidate
        suffix = 2
        while f"{base_label} · {suffix}" in values_by_label:
            suffix += 1
        return f"{base_label} · {suffix}"

    def _set_rows(new_rows: list[dict[str, Any]]) -> None:
        lookup.clear()
        labels_by_value.clear()
        values_by_label.clear()
        indexed_rows.clear()
        if empty_label is not None:
            labels_by_value[""] = empty_label
            values_by_label[empty_label] = ""
        for row in new_rows:
            value = str(value_fn(row) or "")
            if not value:
                continue
            base_label = str(label_fn(row) or value)
            display_label = _unique_label(base_label, value)
            lookup[value] = row
            labels_by_value[value] = display_label
            values_by_label[display_label] = value
            indexed_rows.append(row)

    def _sync_visible_value() -> None:
        nonlocal syncing
        value = str(selector.value or "")
        label_value = labels_by_value.get(value, "") if value else ""
        syncing = True
        try:
            combobox.value = label_value
            context.value = _context_html(lookup.get(value))
        finally:
            syncing = False

    def _refresh_options(*_: Any) -> None:
        candidate = selected_value if selected_value is not None else str(selector.value or "")
        options = [(labels_by_value[value], value) for value in labels_by_value]
        values = [value for _, value in options]
        selector.options = options
        combobox.options = [label_value for label_value, _ in options]
        selector.value = candidate if candidate in values else (values[0] if values else None)
        _sync_visible_value()

    def _on_combobox(change: dict[str, Any]) -> None:
        nonlocal syncing
        if syncing or change.get("name") != "value":
            return
        label_value = str(change.get("new") or "")
        if label_value not in values_by_label:
            return
        syncing = True
        try:
            selector.value = values_by_label[label_value]
        finally:
            syncing = False
        context.value = _context_html(lookup.get(str(selector.value or "")))

    def _on_select(change: dict[str, Any]) -> None:
        if change.get("name") == "value" and not syncing:
            _sync_visible_value()

    def _refresh_rows(new_rows: list[dict[str, Any]], selected: str | None = None) -> None:
        nonlocal selected_value
        selected_value = selected
        _set_rows(new_rows)
        _refresh_options()

    combobox.observe(_on_combobox, names="value")
    selector.observe(_on_select, names="value")
    _set_rows(rows)
    _refresh_options()
    selector.refresh_rows = _refresh_rows
    children = [combobox]
    if context_fields:
        children.append(context)
    container = widgets.VBox(
        children,
        layout=widgets.Layout(width="100%", height="auto", overflow="visible", gap="6px"),
    )
    return {
        "container": container,
        "search": combobox,
        "selector": selector,
        "context": context,
        "rows_by_value": lookup,
    }

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
            options = [
                (str(option[0]), option[1]) if isinstance(option, (tuple, list)) and len(option) == 2
                else (str(option), option)
                for option in (field.get("options", []) or [])
            ]
            option_values = [option[1] for option in options]
            if field.get("required"):
                value = default if default in option_values else (option_values[0] if option_values else "")
            else:
                value = default if default in option_values else ""
            options = [("Select an option", ""), *options]
            rendered[key] = widgets.Dropdown(options=options, value=value, **common)
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
DATA_AGREEMENT_FIELDS = DATA_AGREEMENT_GENERATED_FIELDS + DATA_AGREEMENT_VISIBLE_FIELDS + ["provider_steward_name", "recipient_steward_name", "supporting_documents_json", "approved_usage_json", "custom_fields_json"] + STANDARD_RUNTIME_AUDIT_COLUMNS
WIDGET_CONFIG_DEFAULTS = {"data_steward_widget": {"visible_columns": DATA_STEWARD_VISIBLE_FIELDS, "custom_fields": []}, "data_agreement_widget": {"visible_columns": DATA_AGREEMENT_VISIBLE_FIELDS, "approved_usage_options": ["internal cross domain", "internal single domain", "research", "external"], "custom_fields": []}}
FIELD_LABELS = {"steward_id": "Steward ID", "provider_steward_id": "Provider Data Steward", "recipient_steward_id": "Recipient Data Steward", "steward_name": "Steward Name", "steward_role": "Steward Role", "contact": "Contact", "effective_from": "Effective From", "effective_to": "Effective To", "is_active": "Is Active", "agreement_name": "Agreement Name", "domain": "Domain", "start_date": "Start Date", "expiry_date": "Expiry Date", "business_purpose": "Business Purpose"}
CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
PROFILED_TABLE = "METADATA_DATA_PROFILED"
GUARDRAIL_RESULTS_TABLE = "METADATA_GUARDRAIL_RESULTS"
GUARDRAIL_TYPES = ["schema", "freshness", "profile_behavior", "dq"]
LINEAGE_TABLE = "METADATA_DATA_LINEAGE"
DATA_ACCESS_TABLE = "METADATA_DATA_ACCESS"
CLASSIFICATION_LEVELS = ["Public", "Restricted", "Confidential", "Highly Sensitive"]


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
        if value and (value not in latest or config_shared.metadata_timestamp_sort_key(row.get("_committed_at")) >= config_shared.metadata_timestamp_sort_key(latest[value].get("_committed_at"))):
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
        rows = read_lakehouse_table(str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), store="Metadata", schema=metadata_schema, spark_session=spark_session, context={"config": config, "env": env})
    except Exception as exc:
        if missing_ok and _is_table_not_found_error(exc):
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
    write_lakehouse_table(spark.createDataFrame([typed_row], schema=canonical_schema), table, store="Metadata", schema=metadata_table_physical_schema(config, canonical_table), context={"config": config, "env": env}, mode="append")

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
            config_shared.metadata_timestamp_sort_key(row.get("_committed_at")),
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
        rows = read_lakehouse_table(str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), store="Metadata", schema=metadata_table_physical_schema(config, DATA_AGREEMENT_TABLE), context={"config": config, "env": env}, spark_session=spark_session)
    except Exception as exc:
        if missing_ok and _is_table_not_found_error(exc):
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


def enrichment_control_options(config: Any) -> tuple[list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return configured column metadata enrichment controls."""
    governance = getattr(config, "governance_config", None)
    sensitivity = list(getattr(governance, "classification_levels", None) or CLASSIFICATION_LEVELS)
    context_widget = getattr(governance, "enrichment_context_widget", None) or {}
    classification_widget = getattr(governance, "enrichment_classification_widget", None) or {}
    context_fields = list(context_widget.get("custom_fields", []) or [])
    classification_fields = list(classification_widget.get("custom_fields", []) or [])
    return sensitivity, context_fields, classification_fields


# Governance readiness and policy helpers migrated from the retired mixed governance module.


# DQ authoring record helpers migrated to widget ownership.


CATALOGUE_TABLE = "METADATA_DATA_CATALOGUE"
PROFILE_TABLE = "METADATA_DATA_PROFILED"
PROFILE_FREQUENCY_TABLE = "METADATA_DATA_PROFILED_FREQUENCY"


# ---------------------------------------------------------------------------
# Guardrail authoring shared implementation
# ---------------------------------------------------------------------------

from fabricops_kit.config.shared import is_table_not_found_error

from fabricops_kit.data_contract.shared import (
    canonical_guardrail_rule_record,
    normalize_guardrail_action,
    validate_sensitive_data_parameters,
)

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
            config_shared.metadata_timestamp_sort_key(row.get("_committed_at")),
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
    contract_id: str,
    contract_version: int,
    column_id: str,
    guardrail_type: str,
    rule_id: str,
    identity_parameters: Mapping[str, Any] | None = None,
) -> str:
    """Build a stable identity for one logical normalized Guardrail rule."""
    payload = {
        "contract_id": str(contract_id),
        "contract_version": int(contract_version),
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
    action: str = "Warn",
    column_name: str = "",
    identity_parameters: Mapping[str, Any] | None = None,
    guardrail_version: int | None = None,
    is_active: bool = True,
) -> dict[str, Any]:
    """Build one Stage 4A Guardrail row without obsolete identity or review fields."""
    table_id = str(state.get("table_id") or "").strip()
    contract_id = str(state.get("contract_id") or "").strip()
    contract_version = int(state.get("contract_version") or 0)
    environment_name = str(state.get("environment_name") or "").strip()
    if not table_id:
        raise ValueError("A selected profiled table with a canonical table_id is required.")
    if not environment_name:
        raise ValueError("The selected profiled table must have an environment_name.")
    if not contract_id or contract_version < 1:
        raise ValueError("A selected Data Contract version is required for Guardrail authoring.")
    column_id = _column_id_for_name(state, column_name) if column_name else ""
    guardrail_rule_id = _build_guardrail_rule_id(
        contract_id=contract_id,
        contract_version=contract_version,
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
        "contract_id": contract_id,
        "contract_version": contract_version,
        "column_id": column_id,
        "environment_name": environment_name,
        "guardrail_type": str(guardrail_type),
        "rule_id": str(rule_id),
        "rule_type": str(rule_type),
        "rule_parameters_json": _guardrail_stable_json(dict(parameters or {})),
        "action": normalize_guardrail_action(action),
        "is_active": bool(is_active),
    }

def dq_records_from_selection(
    state: Mapping[str, Any],
    *,
    rule_id: str,
    selected_columns: Iterable[str],
    parameters: Mapping[str, Any] | None = None,
    action: str = "Warn",
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
                guardrail_type="data_quality",
                rule_id=rule_id,
                rule_type=rule_id,
                column_name=column,
                parameters={"columns": [column], **values},
                action=action,
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
            guardrail_type="data_quality",
            rule_id=rule_id,
            rule_type=rule_id,
            parameters={"columns": columns, **values},
            action=action,
            identity_parameters=identity_parameters,
        )
    ]

def sensitive_data_record_from_selection(
    state: Mapping[str, Any],
    *,
    column_name: str,
    treatment: str,
    action: str = "Block",
    guardrail_version: int | None = None,
    is_active: bool = True,
    parameters: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build one canonical column-scoped Sensitive Data Guardrail row."""
    normalized_parameters = validate_sensitive_data_parameters({
        "scope": "column", "treatment": treatment, **dict(parameters or {}),
    })
    normalized_treatment = normalized_parameters["treatment"]
    column_id = _column_id_for_name(state, column_name)
    return build_rule_record(
        state,
        guardrail_type="sensitive_data",
        rule_id=f"sensitive_data_{column_id}",
        rule_type=normalized_treatment,
        parameters=normalized_parameters,
        action=action,
        column_name=column_name,
        guardrail_version=guardrail_version,
        is_active=is_active,
    )
