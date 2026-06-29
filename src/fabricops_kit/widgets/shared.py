"""Shared widget rendering helpers for FabricOps notebook widgets."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

_WIDGET_STYLE = {"description_width": "150px"}
_WIDGET_LAYOUT_WIDTH = "600px"
_TEXTAREA_HEIGHT = "80px"


def _require_ipywidgets():
    """Return ipywidgets or raise an actionable optional-dependency error."""
    try:
        import ipywidgets as widgets
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The FabricOps widget feature requires the 'dq-review' extra. "
            'Install with: pip install "fabricops-kit[dq-review]"'
        ) from exc
    return widgets


def _widget_common(widgets_module: Any, description: str, *, textarea: bool = False) -> dict[str, Any]:
    """Return common style and layout keyword arguments for form controls."""
    common: dict[str, Any] = {"description": description, "style": dict(_WIDGET_STYLE)}
    layout_class = getattr(widgets_module, "Layout", None)
    if layout_class is not None:
        kwargs = {"width": _WIDGET_LAYOUT_WIDTH}
        if textarea:
            kwargs["height"] = _TEXTAREA_HEIGHT
        common["layout"] = layout_class(**kwargs)
    return common


def _html_escape(value: Any) -> str:
    """Return display-safe HTML text for notebook context snippets."""
    import html

    return html.escape(str(value or ""))


def _render_searchable_selector(
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
) -> dict[str, Any]:
    """Render a table-backed selector with search and stable-value tracking."""
    search = widgets.Text(value="", placeholder=placeholder, **_widget_common(widgets, f"Search {label}"))
    selector = widgets.Select(options=[], **_widget_common(widgets, label))
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
    container = widgets.VBox([search, selector, context])
    return {"container": container, "search": search, "selector": selector, "context": context, "rows_by_value": lookup}


def _render_custom_fields(config: list[dict[str, Any]] | dict[str, Any], *, values: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render organization-specific custom fields from normalized config."""
    widgets = _require_ipywidgets()
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
        common = _widget_common(widgets, label, textarea=field_type == "textarea")
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


def _standard_widget(field: str, value: Any = "", *, options: list[Any] | None = None) -> Any:
    """Render a standard widget control for a configured field name."""
    widgets = _require_ipywidgets()
    description = field.replace("_", " ").title()
    if options is not None:
        default_value = value if value in options else (options[0] if options else None)
        return widgets.Dropdown(options=options, value=default_value, **_widget_common(widgets, description))
    if field.endswith("_date") or field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
        return widgets.DatePicker(value=date.fromisoformat(str(value)[:10]) if value else None, **_widget_common(widgets, description))
    if field.startswith("approved_usage_") or field == "is_active":
        return widgets.Checkbox(value=True if value == "" else str(value).strip().lower() in {"1", "true", "yes", "y"}, **_widget_common(widgets, description))
    if field in {"business_purpose"}:
        return widgets.Textarea(value=str(value or ""), **_widget_common(widgets, description, textarea=True))
    return widgets.Text(value=str(value or ""), **_widget_common(widgets, description))
