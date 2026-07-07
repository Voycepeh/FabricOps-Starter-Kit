"""Public widget entrypoint for ``widget_render_data_steward``."""

from __future__ import annotations

from datetime import date
import hashlib
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
    get_widget_visible_fields,
    list_data_stewards,
    parse_iso_date,
    render_custom_fields,
    serialize_custom_fields,
    standard_widget,
    to_bool,
    to_iso_date,
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
        label="Create / update",
        rows=existing_rows,
        label_fn=_steward_label,
        value_fn=_row_id,
        placeholder="Search stewards...",
        search_fields=["steward_name", "steward_role", "contact", "steward_id"],
        context_fields=[("steward_name", "Steward name"), ("steward_role", "Role"), ("contact", "Contact"), ("steward_id", "Steward ID")],
        empty_label="Create new steward",
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
            if field in {"effective_from", "effective_to"}:
                value = date.fromisoformat(str(value)[:10]) if value else None
            _apply_widget_value(widget, value)
        stored = deserialize_custom_fields(row.get("custom_fields_json", ""))
        for key, widget in custom.items():
            _apply_widget_value(widget, stored.get(key, widget.value))

    selected.observe(_populate, names="value")
    callbacks = getattr(selected, "callbacks", None)
    if isinstance(callbacks, list) and callbacks:
        callbacks.insert(0, callbacks.pop())

    save = widgets.Button(description="Save")
    output = widgets.Output()

    def _save(_: Any) -> None:
        save.disabled = True
        clear = getattr(output, "clear_output", None)
        if clear is not None:
            clear(wait=True)
        with output:
            try:
                values = {key: to_iso_date(widget.value) if key in {"effective_from", "effective_to"} else widget.value for key, widget in form.items()}
                extras = collect_custom_fields(widget_config, custom)
                if selected.value:
                    values["steward_id"] = selected.value
                    values["_existing_steward_role"] = row_lookup.get(selected.value, {}).get("steward_role", "")
                row = _create_or_update_data_steward(spark=spark, config=config, env=env, values=values, custom_fields=extras)
                _refresh_existing_options(row["steward_id"])
                for callback in after_save_callbacks:
                    callback(row)
                print(f"Saved data steward: {row.get('steward_name', '')} ({row['steward_id']})")
            except Exception as exc:
                print(f"Error: {exc}")
            finally:
                save.disabled = False

    save.on_click(_save)
    controls = [selected_selector["container"], *[form[field] for field in fields], *custom.values()]
    container = widgets.VBox([*controls, save, output])
    ip.display(container)
    return {"container": container, "existing_record": selected, "existing_record_search": selected_selector["search"], "existing_record_context": selected_selector["context"], "existing_records_by_id": row_lookup, "identity_context": None, "fields": form, "custom_fields": custom, "refresh_stewards_button": None, "refresh_existing_options": _refresh_existing_options, "refresh_steward_options": None, "after_save_callbacks": after_save_callbacks, "save_button": save, "output": output}


def _generate_steward_id(values: dict[str, Any]) -> str:
    basis = "|".join(str(values.get(field, "")).strip().lower() for field in ("steward_name", "contact", "effective_from"))
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:10]
    return f"STEW-{digest}"


def _steward_label(row: dict[str, Any]) -> str:
    parts = [str(row.get(field) or "").strip() for field in ("steward_name", "steward_role", "contact")]
    return " | ".join(part for part in parts if part) or str(row.get("steward_id") or "Unnamed steward")


def _create_or_update_data_steward(*, spark: Any, config: Any, env: str, values: dict[str, Any], custom_fields: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {field: values.get(field, "") for field in DATA_STEWARD_VISIBLE_FIELDS}
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
    row["effective_from"] = parse_iso_date(row.get("effective_from"), "effective_from")
    row["effective_to"] = parse_iso_date(row.get("effective_to"), "effective_to")
    if row["effective_to"] and row["effective_from"] and row["effective_to"] < row["effective_from"]:
        raise ValueError("effective_to must be on or after effective_from.")
    row["steward_id"] = selected_steward_id or _generate_steward_id(row)
    explicit_active = values.get("is_active")
    row["is_active"] = False if explicit_active not in (None, "") and not to_bool(explicit_active) else bool(active_steward({**row, "is_active": row.get("is_active", "")}, config))
    row["custom_fields_json"] = serialize_custom_fields(custom_fields)
    row.update(build_runtime_audit_fields(config=config, env=env, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    write_widget_metadata_row(spark=spark, config=config, env=env, table=str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), row=row)
    return row
