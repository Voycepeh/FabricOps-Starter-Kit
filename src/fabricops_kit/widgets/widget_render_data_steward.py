"""Public widget entrypoint for ``widget_render_data_steward``."""

from __future__ import annotations

import uuid
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import DEFAULT_STEWARD_ROLE_OPTIONS, resolve_fabric_context
from fabricops_kit.widgets.shared import (
    DATA_STEWARD_TABLE,
    DATA_STEWARD_VISIBLE_FIELDS,
    WIDGET_CONFIG_DEFAULTS,
    active_steward,
    collect_custom_fields,
    deserialize_custom_fields,
    action_row,
    execution_log_section,
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
    write_widget_metadata_row,
)


def widget_render_data_steward(*, spark: Any, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render append-only data steward create/update maintenance.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for metadata reads and append-only writes.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    dict[str, Any]
        Rendered widget controls keyed for notebook customization.

    """
    config, env, _context = resolve_fabric_context(context=context)
    widgets = require_ipywidgets()
    from IPython import display as ip

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

    existing_rows = [row for row in list_data_stewards(config, env, spark_session=spark, active_only=False, missing_ok=True) if _row_id(row)]
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
        rows = [row for row in list_data_stewards(config, env, spark_session=spark, active_only=False, missing_ok=True) if _row_id(row)]
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

    save = widgets.Button(description="Save steward")
    output = widgets.Output()
    status = widgets.HTML(value="")
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

    for widget in form.values():
        widget.observe(_sync_save_state, names="value")
    _sync_save_state()

    def _save(_: Any) -> None:
        save.disabled = True
        status.value = ""
        clear = getattr(output, "clear_output", None)
        if clear is not None:
            clear(wait=True)
        try:
            values = {
                key: widget.value.strip() if isinstance(widget.value, str) else widget.value
                for key, widget in form.items()
            }
            missing = _missing_required(values)
            if missing:
                status.value = "Data steward was not saved. Complete the required fields."
                return
            extras = collect_custom_fields(widget_config, custom)
            if selected.value:
                values["steward_id"] = selected.value
                values["_existing_steward_role"] = row_lookup.get(selected.value, {}).get("steward_role", "")
            row = _create_or_update_data_steward(spark=spark, config=config, env=env, values=values, custom_fields=extras)
            _refresh_existing_options(row["steward_id"])
            for callback in after_save_callbacks:
                callback(row)
            status.value = f"Data steward saved successfully: {row.get('steward_name', '')}"
            print(f"Saved data steward: {row.get('steward_name', '')} ({row['steward_id']})")
        except Exception as exc:
            status.value = f"Data steward was not saved: {exc}"
        finally:
            _sync_save_state()

    save.on_click(_save)
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
                title="Additional information",
                children=[form_grid(widgets, custom.values())],
            )
        )
    actions = action_row(widgets, [save])
    log_section = execution_log_section(widgets, output)
    container = form_page(
        widgets,
        title="Data Steward",
        description="Create or update data stewards",
        children=[selection_section, details_section, *supporting_sections, actions, status],
    )
    ip.display(container)
    return {"container": container, "existing_record": selected, "existing_record_search": selected_selector["search"], "existing_record_context": selected_selector["context"], "existing_records_by_id": row_lookup, "identity_context": None, "fields": form, "custom_fields": custom, "refresh_stewards_button": None, "refresh_existing_options": _refresh_existing_options, "refresh_steward_options": None, "after_save_callbacks": after_save_callbacks, "save_button": save, "status": status, "output": output, "execution_output": output, "execution_log_section": log_section}


def _generate_steward_id() -> str:
    steward_id = str(uuid.uuid4())
    uuid.UUID(steward_id)
    return steward_id


def _steward_label(row: dict[str, Any]) -> str:
    parts = [str(row.get(field) or "").strip() for field in ("steward_name", "steward_role", "contact")]
    return " | ".join(part for part in parts if part) or str(row.get("steward_id") or "Unnamed steward")


def _create_or_update_data_steward(*, spark: Any, config: Any, env: str, values: dict[str, Any], custom_fields: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> dict[str, Any]:
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
    row.update(build_runtime_audit_fields(config=config, env=env, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    write_widget_metadata_row(spark=spark, config=config, env=env, table=str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), row=row)
    return row
