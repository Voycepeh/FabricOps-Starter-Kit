"""Shared widget rendering helpers for FabricOps notebook widgets."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date
from typing import Any

from fabricops_kit.config.shared import DEFAULT_STEWARD_ROLE_OPTIONS

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


# Widget workflow implementations migrated from data_agreement.py.
def _render_maintenance_widget_shared_workflow(*, spark: Any, config: Any, env: str, kind: str, display_widget: bool = True) -> dict[str, Any]:
    from fabricops_kit import data_agreement_shared as _data_agreement

    widgets = _require_ipywidgets()
    from IPython import display as ip

    is_steward = kind == "data_steward_widget"
    prompt = "Create new steward" if is_steward else "Create new agreement"
    widget_config = {**_data_agreement._WIDGET_CONFIG_DEFAULTS[kind], **dict(_data_agreement._config_value(config, kind, {}) or {})}
    fields = _data_agreement._get_widget_visible_fields(config, kind)
    after_save_callbacks: list[Any] = []
    row_lookup: dict[str, dict[str, Any]] = {}

    def _row_id(row: dict[str, Any]) -> str:
        return str(row.get("steward_id" if is_steward else "agreement_id") or "").strip()

    def _existing_rows() -> list[dict[str, Any]]:
        return _data_agreement._list_data_stewards(config, env, spark_session=spark, active_only=False, missing_ok=True) if is_steward else _data_agreement._list_data_agreements(config, env, spark_session=spark, missing_ok=True)

    def _existing_rows_for_selector() -> list[dict[str, Any]]:
        rows = _existing_rows()
        return [row for row in rows if _row_id(row)]

    def _refresh_lookup(rows: list[dict[str, Any]]) -> None:
        row_lookup.clear()
        row_lookup.update({_row_id(row): row for row in rows if _row_id(row)})

    def _steward_label(row: dict[str, Any]) -> str:
        parts = [str(row.get(field) or "").strip() for field in ("steward_name", "steward_role", "contact")]
        return " | ".join(part for part in parts if part) or str(row.get("steward_id") or "Unnamed steward")

    def _agreement_label(row: dict[str, Any]) -> str:
        row_id = _row_id(row)
        return f"{row.get('agreement_name', '') or row_id} ({row_id} / v{row.get('contract_version', '')})"

    existing_rows = _existing_rows_for_selector()
    _refresh_lookup(existing_rows)
    selected_selector = _render_searchable_selector(
        widgets=widgets,
        label="Create / update",
        rows=existing_rows,
        label_fn=_steward_label if is_steward else _agreement_label,
        value_fn=_row_id,
        placeholder="Search stewards..." if is_steward else "Search agreements...",
        search_fields=["steward_name", "steward_role", "contact", "steward_id"] if is_steward else ["agreement_name", "agreement_id", "contract_version", "domain", "recipient"],
        context_fields=[
            ("steward_name", "Steward name"), ("steward_role", "Role"), ("contact", "Contact"), ("steward_id", "Steward ID"),
        ] if is_steward else [
            ("agreement_name", "Agreement name"), ("agreement_id", "Agreement ID"), ("contract_version", "Current version"), ("recipient", "Recipient"),
        ],
        empty_label=prompt,
    )
    selected = selected_selector["selector"]
    identity_context = None if is_steward else widgets.HTML(value=_data_agreement._agreement_identity_text(None))

    roles = [str(option).strip() for option in (_data_agreement._config_value(config, "steward_role_options", DEFAULT_STEWARD_ROLE_OPTIONS) or []) if str(option).strip()]
    steward_role_options = [(role, role) for role in roles] if is_steward else None
    form = {}
    steward_field_selector = None
    for field in fields:
        if field == "steward_id" and not is_steward:
            steward_rows = _data_agreement._list_data_stewards(config, env, spark_session=spark, active_only=True, missing_ok=True)
            steward_field_selector = _render_searchable_selector(
                widgets=widgets,
                label=_data_agreement.FIELD_LABELS.get(field, field.replace("_", " ").title()),
                rows=steward_rows,
                label_fn=_steward_label,
                value_fn=lambda row: str(row.get("steward_id") or "").strip(),
                placeholder="Search stewards...",
                search_fields=["steward_name", "steward_role", "contact", "steward_id"],
                context_fields=[("steward_name", "Steward name"), ("steward_role", "Role"), ("contact", "Contact"), ("steward_id", "Steward ID")],
            )
            form[field] = steward_field_selector["selector"]
        else:
            form[field] = _standard_widget(
                field,
                options=steward_role_options if field == "steward_role" else None,
            )
    custom = _render_custom_fields(widget_config)

    def _refresh_existing_options(selected_id: str | None = None) -> None:
        rows = _existing_rows_for_selector()
        _refresh_lookup(rows)
        selected.refresh_rows(rows, selected_id if selected_id in row_lookup else "")

    def _refresh_steward_dropdown(selected_id: str | None = None) -> None:
        if "steward_id" in form:
            current = selected_id or form["steward_id"].value
            rows = _data_agreement._list_data_stewards(config, env, spark_session=spark, active_only=True, missing_ok=True)
            form["steward_id"].refresh_rows(rows, str(current or ""))

    refresh_stewards = None if is_steward else widgets.Button(description="Refresh active stewards")
    if refresh_stewards is not None:
        refresh_stewards.on_click(lambda _: _refresh_steward_dropdown())
    save = widgets.Button(description="Save")
    output = widgets.Output()

    def _apply_widget_value(widget: Any, value: Any) -> None:
        select_value = getattr(widget, "select_value", None)
        if callable(select_value):
            select_value(str(value or ""))
            return
        current = getattr(widget, "value", None)
        if isinstance(current, tuple):
            widget.value = tuple(value or ())
        elif isinstance(current, bool):
            widget.value = _data_agreement._to_bool(value)
        else:
            options = list(getattr(widget, "options", []) or [])
            option_values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
            widget.value = value if not option_values or value in option_values else option_values[0]

    def _populate(change: dict[str, Any]) -> None:
        row_id = change.get("new")
        row = row_lookup.get(row_id, {}) if row_id else {}
        for field, widget in form.items():
            value = row.get(field, "")
            if field == "steward_role" and value:
                option_values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in list(getattr(widget, "options", []))]
                if value not in option_values:
                    widget.options = [*list(getattr(widget, "options", [])), (str(value), str(value))]
            if field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
                value = date.fromisoformat(str(value)[:10]) if value else None
            _apply_widget_value(widget, value)
        stored = _data_agreement._deserialize_custom_fields(row.get("custom_fields_json", ""))
        for key, widget in custom.items():
            _apply_widget_value(widget, stored.get(key, widget.value))
        if identity_context is not None:
            identity_context.value = _data_agreement._agreement_identity_text(row if row else None)

    selected.observe(_populate, names="value")
    # Keep lightweight test stubs and custom notebooks that call the first
    # registered callback exercising the population path; real ipywidgets still
    # receives the same observers.
    callbacks = getattr(selected, "callbacks", None)
    if isinstance(callbacks, list) and callbacks:
        callbacks.insert(0, callbacks.pop())

    def _clear_output() -> None:
        clear = getattr(output, "clear_output", None)
        if clear is not None:
            clear(wait=True)

    def _save(_: Any) -> None:
        save.disabled = True
        _clear_output()
        with output:
            try:
                values = {
                    key: _data_agreement._to_iso_date(widget.value) if key in {"effective_from", "effective_to", "start_date", "expiry_date"} else widget.value
                    for key, widget in form.items()
                }
                extras = _data_agreement._collect_custom_fields(widget_config, custom)
                if is_steward:
                    if selected.value:
                        values["steward_id"] = selected.value
                        values["_existing_steward_role"] = row_lookup.get(selected.value, {}).get("steward_role", "")
                    row = _data_agreement._create_or_update_data_steward(spark=spark, config=config, env=env, values=values, custom_fields=extras)
                    _refresh_existing_options(row["steward_id"])
                    for callback in after_save_callbacks:
                        callback(row)
                    print(f"Saved data steward: {row.get('steward_name', '')} ({row['steward_id']})")
                else:
                    selected_row = row_lookup.get(selected.value) if selected.value else None
                    row = _data_agreement._create_or_update_data_agreement(spark=spark, config=config, env=env, values=values, selected_agreement=selected_row, custom_fields=extras)
                    if row.get("_fabricops_no_change"):
                        print(row.get("_fabricops_message", "No changes detected. Nothing was appended."))
                    else:
                        print(f"Saved data agreement: {row.get('agreement_name', '')} ({row['agreement_id']} v{row['contract_version']})")
                    _refresh_existing_options(row["agreement_id"])
                    if not row.get("_fabricops_no_change"):
                        for callback in after_save_callbacks:
                            callback(row)
                    if identity_context is not None:
                        identity_context.value = _data_agreement._agreement_identity_text(row)
            except Exception as exc:
                print(f"Error: {exc}")
            finally:
                save.disabled = False

    save.on_click(_save)
    controls = [selected_selector["container"]]
    if identity_context is not None:
        controls.append(identity_context)
    for field in fields:
        if field == "steward_id" and steward_field_selector is not None:
            controls.append(steward_field_selector["container"])
        else:
            controls.append(form[field])
    controls.extend([*custom.values()])
    if refresh_stewards is not None:
        controls.append(refresh_stewards)
    container = widgets.VBox([*controls, save, output])
    if display_widget:
        ip.display(container)
    return {
        "container": container,
        "existing_record": selected,
        "existing_record_search": selected_selector["search"],
        "existing_record_context": selected_selector["context"],
        "existing_records_by_id": row_lookup,
        "identity_context": identity_context,
        "fields": form,
        "custom_fields": custom,
        "refresh_stewards_button": refresh_stewards,
        "refresh_existing_options": _refresh_existing_options,
        "refresh_steward_options": _refresh_steward_dropdown,
        "after_save_callbacks": after_save_callbacks,
        "save_button": save,
        "output": output,
    }

def _render_agreement_evidence_widget_workflow(*, spark: Any, config: Any, env: str, display_widget: bool = True) -> dict[str, Any]:
    """Render optional agreement evidence upload controls."""
    from fabricops_kit import data_agreement_shared as _data_agreement

    widgets = _require_ipywidgets()
    from IPython import display as ip

    row_lookup: dict[str, dict[str, Any]] = {}

    def _agreement_rows() -> list[dict[str, Any]]:
        return _data_agreement._list_all_data_agreement_rows(config, env, spark_session=spark, missing_ok=True)

    def _version_key(row: dict[str, Any]) -> str:
        agreement_id = str(row.get("agreement_id") or "").strip()
        contract_version = str(row.get("contract_version") or "").strip()
        return f"{agreement_id}||{contract_version}" if agreement_id and contract_version else ""

    def _version_label(row: dict[str, Any]) -> str:
        key = _version_key(row)
        return f"{row.get('agreement_name', '') or row.get('agreement_id', '')} ({row.get('agreement_id', '')} / v{row.get('contract_version', '')})" if key else ""

    def _selector_rows() -> list[dict[str, Any]]:
        row_lookup.clear()
        rows = [row for row in _agreement_rows() if _version_key(row)]
        row_lookup.update({_version_key(row): row for row in rows})
        return rows

    message = widgets.HTML(value="")
    version_selector = _render_searchable_selector(
        widgets=widgets,
        label="Agreement Version",
        rows=_selector_rows(),
        label_fn=_version_label,
        value_fn=_version_key,
        placeholder="Search agreement versions...",
        search_fields=["agreement_name", "agreement_id", "contract_version", "domain", "recipient"],
        context_fields=[("agreement_name", "Agreement name"), ("agreement_id", "Agreement ID"), ("contract_version", "Contract version"), ("recipient", "Recipient")],
        empty_label="Select an agreement version...",
    )
    selected = version_selector["selector"]
    evidence_type = widgets.Dropdown(options=[(item, item) for item in _data_agreement.AGREEMENT_EVIDENCE_TYPES], **_widget_common(widgets, "Evidence Type"))
    evidence_file_paths = widgets.Textarea(
        placeholder=(
            "Files/fabricops/agreement_evidence/<agreement_id>/<contract_version>/signed_agreement.pdf\n"
            "Files/fabricops/agreement_evidence/<agreement_id>/<contract_version>/email_approval.pdf"
        ),
        **_widget_common(widgets, "Evidence File Paths"),
    )
    instructions = widgets.HTML(
        value=(
            "Upload evidence files manually to the metadata lakehouse Files area, "
            "then paste one Files/... path per line."
        )
    )
    refresh = widgets.Button(description="Refresh agreements")
    save = widgets.Button(description="Save evidence")
    output = widgets.Output()

    def _set_empty_state() -> None:
        has_agreement = any(value for _, value in selected.options)
        message.value = "" if has_agreement else "<b>No data agreements found.</b> Save a Data Agreement first, then return here to upload optional evidence."
        evidence_file_paths.disabled = not has_agreement
        save.disabled = not has_agreement

    def _refresh(_: Any = None) -> None:
        current = str(selected.value or "")
        rows = _selector_rows()
        selected.refresh_rows(rows, current if current in row_lookup else "")
        _set_empty_state()

    def _clear_output() -> None:
        clear = getattr(output, "clear_output", None)
        if clear is not None:
            clear(wait=True)

    def _save(_: Any) -> None:
        save.disabled = True
        _clear_output()
        with output:
            try:
                selected_row = row_lookup.get(selected.value or "")
                if not selected_row:
                    raise ValueError("Select an agreement version before saving evidence.")
                rows = _data_agreement._save_agreement_evidence_records(
                    spark=spark,
                    config=config,
                    env=env,
                    agreement_id=str(selected_row.get("agreement_id") or ""),
                    contract_version=str(selected_row.get("contract_version") or ""),
                    evidence_type=str(evidence_type.value or "Other"),
                    evidence_file_paths=evidence_file_paths.value,
                )
                print(f"Saved {len(rows)} agreement evidence file reference row(s).")
            except Exception as exc:
                print(f"Error: {exc}")
            finally:
                _set_empty_state()
                if any(value for _, value in selected.options):
                    save.disabled = False

    refresh.on_click(_refresh)
    save.on_click(_save)
    _set_empty_state()
    container = widgets.VBox([message, version_selector["container"], evidence_type, instructions, evidence_file_paths, refresh, save, output])
    if display_widget:
        ip.display(container)
    return {
        "container": container,
        "message": message,
        "agreement_version": selected,
        "agreement_version_search": version_selector["search"],
        "agreement_version_context": version_selector["context"],
        "agreement_versions_by_key": row_lookup,
        "evidence_type": evidence_type,
        "evidence_file_paths": evidence_file_paths,
        "instructions": instructions,
        "refresh_agreements_button": refresh,
        "refresh_agreements": _refresh,
        "save_button": save,
        "output": output,
    }
