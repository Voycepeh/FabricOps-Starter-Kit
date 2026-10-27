"""Public widget entrypoint for ``widget_render_data_steward``."""

from __future__ import annotations

from fabricops_kit.io.shared import get_spark_session

from html import escape
import uuid
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import DEFAULT_STEWARD_ROLE_OPTIONS, resolve_fabric_context
from fabricops_kit.widgets.shared import (
    WidgetStartup,
    DATA_STEWARD_TABLE,
    DATA_STEWARD_VISIBLE_FIELDS,
    WIDGET_CONFIG_DEFAULTS,
    active_steward,
    collect_custom_fields,
    deserialize_custom_fields,
    action_row,
    form_grid,
    form_page,
    form_section,
    get_widget_visible_fields,
    list_data_stewards,
    render_custom_fields,
    serialize_custom_fields,
    standard_widget,
    to_bool,
    config_value,
    render_searchable_selector,
    require_ipywidgets,
    status_message,
    write_widget_metadata_row,
)


def widget_render_data_steward(*, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render append-only data steward create/update maintenance.

    Spark is resolved automatically from the existing execution session.
    No session is created; Spark-dependent work raises
    ``RuntimeError`` when no session is available.

    Parameters
    ----------
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    dict[str, Any]
        Rendered widget controls keyed for notebook customization.

    Raises
    ------
    ValueError
        If required authored fields are invalid. Complete the highlighted fields
        before saving. Widget callbacks display validation failures.
    RuntimeError
        If configured metadata routing or persistence fails; check the Metadata
        store configuration and write permissions.

    Examples
    --------
    >>> state = widget_render_data_steward()

    """
    spark = get_spark_session(context=context)
    startup = WidgetStartup("Data Steward")
    with startup.phase("initialization", "Resolving FabricOps configuration…"):
        config, active_workspace_id, _context = resolve_fabric_context(context=context)
    widgets = require_ipywidgets()

    kind = "data_steward_widget"
    widget_config = {**WIDGET_CONFIG_DEFAULTS[kind], **dict(config_value(config, kind, {}) or {})}
    fields = get_widget_visible_fields(config, kind)
    after_save_callbacks: list[Any] = []
    row_lookup: dict[str, dict[str, Any]] = {}

    def _row_id(row: dict[str, Any]) -> str:
        return str(row.get("steward_id") or "").strip()

    def _refresh_lookup(rows: list[dict[str, Any]]) -> None:
        row_lookup.clear()
        row_lookup.update({_row_id(row): row for row in rows if _row_id(row)})

    with startup.phase("metadata_loading", "Loading configured metadata…"):
        existing_rows = [row for row in list_data_stewards(config, active_workspace_id, spark_session=spark, active_only=False, missing_ok=True) if _row_id(row)]
    _refresh_lookup(existing_rows)
    selected_selector = render_searchable_selector(
        widgets=widgets,
        label="Select or create steward",
        rows=existing_rows,
        label_fn=_steward_label,
        value_fn=_row_id,
        placeholder="Search stewards...",
        search_fields=["steward_name", "steward_role", "contact", "steward_id"],
        context_fields=None,
        empty_label="Create new steward",
        search_label="Search data stewards",
    )
    selected = selected_selector["selector"]
    roles = [str(option).strip() for option in (config_value(config, "steward_role_options", DEFAULT_STEWARD_ROLE_OPTIONS) or []) if str(option).strip()]
    steward_role_options = [(role, role) for role in roles]
    form = {field: standard_widget(field, options=steward_role_options if field == "steward_role" else None) for field in fields}
    custom = render_custom_fields(widget_config)

    def _refresh_existing_options(selected_id: str | None = None) -> None:
        rows = [row for row in list_data_stewards(config, active_workspace_id, spark_session=spark, active_only=False, missing_ok=True) if _row_id(row)]
        _refresh_lookup(rows)
        selected.refresh_rows(rows, selected_id if selected_id in row_lookup else "")

    def _apply_widget_value(widget: Any, value: Any) -> None:
        select_value = getattr(widget, "select_value", None)
        if callable(select_value):
            select_value(str(value or ""))
            return
        current = getattr(widget, "value", None)
        if isinstance(current, tuple):
            widget.value = tuple(value or ())
        elif isinstance(current, bool):
            widget.value = to_bool(value)
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
            _apply_widget_value(widget, value)
        stored = deserialize_custom_fields(row.get("custom_fields_json", ""))
        for key, widget in custom.items():
            _apply_widget_value(widget, stored.get(key, widget.value))

    selected.observe(_populate, names="value")
    callbacks = getattr(selected, "callbacks", None)
    if isinstance(callbacks, list) and callbacks:
        callbacks.insert(0, callbacks.pop())

    save = widgets.Button(description="Save and clear", button_style="primary")
    discard = widgets.Button(description="Discard and clear", button_style="danger")
    status = status_message(widgets)

    def _set_status(message: str, *, error: bool = False) -> None:
        colour = "#a4262c" if error else "#107c10"
        status.value = f'<span style="color:{colour}">{escape(message)}</span>'

    required_labels = {
        "steward_name": "Steward name",
        "steward_role": "Steward role",
        "contact": "Contact",
    }

    def _missing_required(values: dict[str, Any]) -> list[str]:
        return [
            label
            for field, label in required_labels.items()
            if not str(values.get(field) or "").strip()
        ]

    def _sync_save_state(*_: Any) -> None:
        save.disabled = bool(_missing_required({key: widget.value for key, widget in form.items()}))

    def _reset_form_fields() -> None:
        selected.value = ""
        for key, widget in form.items():
            _apply_widget_value(widget, None if key in {"effective_from", "effective_to"} else "")
        for widget in custom.values():
            _apply_widget_value(widget, False if isinstance(widget.value, bool) else "")

    for widget in form.values():
        widget.observe(_sync_save_state, names="value")
    _sync_save_state()

    def _save(_: Any) -> None:
        save.disabled = True
        try:
            values = {
                key: widget.value.strip() if isinstance(widget.value, str) else widget.value
                for key, widget in form.items()
            }
            missing = _missing_required(values)
            if missing:
                _set_status("Data steward was not saved. Complete the required fields.", error=True)
                print("Cannot save data steward.\n\nComplete the following required fields:")
                for label in missing:
                    print(f"• {label}")
                return
            extras = collect_custom_fields(widget_config, custom)
            if selected.value:
                values["steward_id"] = selected.value
                values["_existing_steward_role"] = row_lookup.get(selected.value, {}).get("steward_role", "")
            row = _create_or_update_data_steward(spark=spark, config=config, active_workspace_id=active_workspace_id, values=values, custom_fields=extras)
        except Exception as exc:
            _set_status(f"Data steward was not saved: {exc}", error=True)
            print(f"Error: {exc}")
        else:
            warnings: list[str] = []
            try:
                _refresh_existing_options(row["steward_id"])
            except Exception as exc:
                warnings.append(f"steward list refresh failed: {exc}")
            for callback in after_save_callbacks:
                try:
                    callback(row)
                except Exception as exc:
                    warnings.append(f"post-save callback failed: {exc}")
            form_cleared = True
            try:
                _reset_form_fields()
            except Exception as exc:
                form_cleared = False
                warnings.append(f"form could not be cleared: {exc}")
            saved_name = row.get("steward_name", "")
            message = f"Data steward saved successfully: {saved_name}."
            if form_cleared:
                message += " Form cleared."
            if warnings:
                message += f" Post-save warning: {'; '.join(warnings)}."
            _set_status(message)
            print(f"Saved data steward: {saved_name} ({row['steward_id']})")
        finally:
            _sync_save_state()

    save.on_click(_save)

    def _discard_and_clear(_: Any) -> None:
        _reset_form_fields()
        _set_status("Unsaved steward changes discarded. Form cleared.")
        _sync_save_state()

    discard.on_click(_discard_and_clear)
    detail_fields = [form[field] for field in fields]
    selection_section = form_section(
        widgets, title="Steward selection", children=[selected_selector["container"]]
    )
    details_section = form_section(
        widgets, title="Steward details", children=[form_grid(widgets, detail_fields)]
    )
    supporting_sections = []
    if custom:
        supporting_sections.append(
            form_section(
                widgets,
                title="Custom columns",
                children=[form_grid(widgets, custom.values())],
            )
        )
    actions = form_section(
        widgets, title="Save steward", children=[action_row(widgets, [discard, save]), status]
    )
    container = form_page(
        widgets,
        title="Data Steward", tone="governance",
        description="Create or update data stewards",
        children=[selection_section, details_section, *supporting_sections, actions],
    )
    startup.display(container)
    return {"container": container, "existing_record": selected, "existing_record_search": selected_selector["search"], "existing_record_context": selected_selector["context"], "existing_records_by_id": row_lookup, "identity_context": None, "fields": form, "custom_fields": custom, "refresh_stewards_button": None, "refresh_existing_options": _refresh_existing_options, "refresh_steward_options": None, "after_save_callbacks": after_save_callbacks, "save_button": save, "discard_button": discard, "status": status}


def _generate_steward_id() -> str:
    steward_id = str(uuid.uuid4())
    uuid.UUID(steward_id)
    return steward_id


def _steward_label(row: dict[str, Any]) -> str:
    parts = [str(row.get(field) or "").strip() for field in ("steward_name", "steward_role", "contact")]
    return " | ".join(part for part in parts if part) or str(row.get("steward_id") or "Unnamed steward")


def _create_or_update_data_steward(*, spark: Any, config: Any, active_workspace_id: str, values: dict[str, Any], custom_fields: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {
        field: value.strip() if isinstance(value := values.get(field), str) else value
        for field in DATA_STEWARD_VISIBLE_FIELDS
    }
    required = ["steward_name", "steward_role", "contact"]
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError("Missing required steward field(s): " + ", ".join(missing))
    configured_roles = {str(option).strip() for option in (config_value(config, "steward_role_options", DEFAULT_STEWARD_ROLE_OPTIONS) or []) if str(option).strip()}
    existing_role = str(values.get("_existing_steward_role") or "").strip()
    selected_steward_id = str(values.get("steward_id") or "").strip()
    role = str(row["steward_role"]).strip()
    if role not in configured_roles and not (selected_steward_id and existing_role and role == existing_role):
        raise ValueError("steward_role must be one of the configured steward role options.")
    if selected_steward_id:
        uuid.UUID(selected_steward_id)
    row["steward_id"] = selected_steward_id or _generate_steward_id()
    explicit_active = values.get("is_active")
    row["is_active"] = False if explicit_active not in (None, "") and not to_bool(explicit_active) else bool(active_steward({**row, "is_active": row.get("is_active", "")}, config))
    row["custom_fields_json"] = serialize_custom_fields(custom_fields)
    row.update(build_runtime_audit_fields(config=config, active_workspace_id=active_workspace_id, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    write_widget_metadata_row(spark=spark, config=config, active_workspace_id=active_workspace_id, table=str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), row=row)
    return row
