"""Public widget entrypoint for ``widget_render_data_agreement``."""

from __future__ import annotations

from datetime import date
import json
from typing import Any
import uuid

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.widgets.shared import (
    DATA_AGREEMENT_TABLE,
    DATA_AGREEMENT_VISIBLE_FIELDS,
    FIELD_LABELS,
    WIDGET_CONFIG_DEFAULTS,
    collect_custom_fields,
    deserialize_custom_fields,
    get_widget_visible_fields,
    list_data_stewards,
    parse_iso_date,
    serialize_custom_fields,
    standard_widget,
    to_bool,
    to_iso_date,
    config_value,
    list_all_data_agreement_rows,
    list_data_agreements,
    render_searchable_selector,
    require_ipywidgets,
    write_widget_metadata_row,
    render_custom_fields,
)


def widget_render_data_agreement(*, spark: Any, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render append-only agreement create/update maintenance using active stewards.

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
        Rendered controls, including read-only generated-identifier context.

    """
    config, env, _context = resolve_fabric_context(context=context)
    widgets = require_ipywidgets()
    from IPython import display as ip

    kind = "data_agreement_widget"
    widget_config = {**WIDGET_CONFIG_DEFAULTS[kind], **dict(config_value(config, kind, {}) or {})}
    fields = get_widget_visible_fields(config, kind)
    after_save_callbacks: list[Any] = []
    row_lookup: dict[str, dict[str, Any]] = {}

    def _row_id(row: dict[str, Any]) -> str:
        return str(row.get("agreement_id") or "").strip()

    def _refresh_lookup(rows: list[dict[str, Any]]) -> None:
        row_lookup.clear()
        row_lookup.update({_row_id(row): row for row in rows if _row_id(row)})

    existing_rows = [row for row in list_data_agreements(config, env, spark_session=spark, missing_ok=True) if _row_id(row)]
    _refresh_lookup(existing_rows)
    selected_selector = render_searchable_selector(
        widgets=widgets,
        label="Create / update",
        rows=existing_rows,
        label_fn=_agreement_label,
        value_fn=_row_id,
        placeholder="Search agreements...",
        search_fields=["agreement_name", "agreement_id", "agreement_version", "domain", "recipient"],
        context_fields=[("agreement_name", "Agreement name"), ("agreement_id", "Agreement ID"), ("agreement_version", "Current version"), ("recipient", "Recipient")],
        empty_label="Create new agreement",
    )
    selected = selected_selector["selector"]
    identity_context = widgets.HTML(value=_agreement_identity_text(None))
    form: dict[str, Any] = {}
    steward_field_selectors: dict[str, dict[str, Any]] = {}
    for field in fields:
        if field in {"provider_steward_id", "recipient_steward_id"}:
            steward_rows = list_data_stewards(config, env, spark_session=spark, active_only=True, missing_ok=True)
            steward_field_selectors[field] = render_searchable_selector(
                widgets=widgets,
                label=FIELD_LABELS.get(field, field.replace("_", " ").title()),
                rows=steward_rows,
                label_fn=_steward_label,
                value_fn=lambda row: str(row.get("steward_id") or "").strip(),
                placeholder="Search stewards...",
                search_fields=["steward_name", "steward_role", "contact", "steward_id"],
                context_fields=[("steward_name", "Steward name"), ("steward_role", "Role"), ("contact", "Contact"), ("steward_id", "Steward ID")],
            )
            form[field] = steward_field_selectors[field]["selector"]
        else:
            form[field] = standard_widget(field)
    custom = render_custom_fields(widget_config)
    usage_options = [str(option) for option in widget_config.get("approved_usage_options", [])]
    if not usage_options or len(set(usage_options)) != len(usage_options) or any(not option.strip() for option in usage_options):
        raise ValueError("approved_usage_options must contain unique, non-empty values.")
    approved_usage_checkboxes = {
        option: widgets.Checkbox(value=False, description=option.replace("_", " ").title()) for option in usage_options
    }
    supporting_document_rows: list[dict[str, Any]] = []
    supporting_documents = widgets.VBox([])

    def _render_document_rows() -> None:
        supporting_documents.children = tuple(row["container"] for row in supporting_document_rows)

    def _add_document_row(label: str = "", location: str = "") -> None:
        label_widget = widgets.Text(value=label, description="Document label")
        location_widget = widgets.Text(value=location, description="Document location")
        remove = widgets.Button(description="Remove document")
        record = {"label": label_widget, "location": location_widget, "remove": remove}
        record["container"] = widgets.VBox([label_widget, location_widget, remove])

        def _remove(_: Any) -> None:
            supporting_document_rows.remove(record)
            _render_document_rows()

        remove.on_click(_remove)
        supporting_document_rows.append(record)
        _render_document_rows()

    add_supporting_document_button = widgets.Button(description="+ Add document")
    add_supporting_document_button.on_click(lambda _: _add_document_row())
    _add_document_row()

    def _refresh_existing_options(selected_id: str | None = None) -> None:
        rows = [row for row in list_data_agreements(config, env, spark_session=spark, missing_ok=True) if _row_id(row)]
        _refresh_lookup(rows)
        selected.refresh_rows(rows, selected_id if selected_id in row_lookup else "")

    def _refresh_steward_dropdowns() -> None:
        rows = list_data_stewards(config, env, spark_session=spark, active_only=True, missing_ok=True)
        for field in ("provider_steward_id", "recipient_steward_id"):
            current = str(form[field].value or "")
            valid_ids = {str(row.get("steward_id") or "") for row in rows}
            form[field].refresh_rows(rows, current if current in valid_ids else "")

    refresh_stewards = widgets.Button(description="Refresh active stewards")
    refresh_stewards.on_click(lambda _: _refresh_steward_dropdowns())
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
            if field in {"start_date", "expiry_date"}:
                value = date.fromisoformat(str(value)[:10]) if value else None
            _apply_widget_value(widget, value)
        stored = deserialize_custom_fields(row.get("custom_fields_json", ""))
        for key, widget in custom.items():
            _apply_widget_value(widget, stored.get(key, widget.value))
        documents = _deserialize_supporting_documents(row.get("supporting_documents_json", "[]")) if row else []
        supporting_document_rows.clear()
        for document in documents:
            _add_document_row(document["label"], document["location"])
        if not documents:
            _add_document_row()
        selected_usage = _deserialize_approved_usage(row.get("approved_usage_json"), usage_options) if row else []
        for option, checkbox in approved_usage_checkboxes.items():
            checkbox.value = option in selected_usage
        identity_context.value = _agreement_identity_text(row if row else None)

    selected.observe(_populate, names="value")
    callbacks = getattr(selected, "callbacks", None)
    if isinstance(callbacks, list) and callbacks:
        callbacks.insert(0, callbacks.pop())

    def _save(_: Any) -> None:
        save.disabled = True
        clear = getattr(output, "clear_output", None)
        if clear is not None:
            clear(wait=True)
        with output:
            try:
                values = {key: to_iso_date(widget.value) if key in {"start_date", "expiry_date"} else widget.value for key, widget in form.items()}
                values["supporting_documents"] = [
                    {"label": row["label"].value, "location": row["location"].value} for row in supporting_document_rows
                ]
                values["approved_usage"] = [option for option, checkbox in approved_usage_checkboxes.items() if checkbox.value]
                extras = collect_custom_fields(widget_config, custom)
                selected_row = row_lookup.get(selected.value) if selected.value else None
                row = _create_or_update_data_agreement(spark=spark, config=config, env=env, values=values, selected_agreement=selected_row, custom_fields=extras)
                if row.get("_fabricops_no_change"):
                    print(row.get("_fabricops_message", "No changes detected. Nothing was appended."))
                else:
                    print(f"Saved data agreement: {row.get('agreement_name', '')} ({row['agreement_id']} v{row['agreement_version']})")
                    for callback in after_save_callbacks:
                        callback(row)
                _refresh_existing_options(row["agreement_id"])
                identity_context.value = _agreement_identity_text(row)
            except Exception as exc:
                print(f"Error: {exc}")
            finally:
                save.disabled = False

    save.on_click(_save)
    controls = [selected_selector["container"], identity_context]
    for field in fields:
        controls.append(steward_field_selectors[field]["container"] if field in steward_field_selectors else form[field])
    controls.extend([supporting_documents, add_supporting_document_button, *approved_usage_checkboxes.values(), *custom.values(), refresh_stewards])
    container = widgets.VBox([*controls, save, output])
    ip.display(container)
    return {"container": container, "existing_record": selected, "existing_record_search": selected_selector["search"], "existing_record_context": selected_selector["context"], "existing_records_by_id": row_lookup, "identity_context": identity_context, "fields": form, "provider_steward_selector": form["provider_steward_id"], "recipient_steward_selector": form["recipient_steward_id"], "supporting_documents": supporting_document_rows, "add_supporting_document_button": add_supporting_document_button, "approved_usage_checkboxes": approved_usage_checkboxes, "custom_fields": custom, "refresh_stewards_button": refresh_stewards, "refresh_existing_options": _refresh_existing_options, "refresh_steward_options": _refresh_steward_dropdowns, "after_save_callbacks": after_save_callbacks, "save_button": save, "output": output}


def _parse_agreement_version(version: Any) -> tuple[int, int, int]:
    try:
        parts = str(version or "").strip().split(".")
        return tuple(int(parts[index]) if index < len(parts) else 0 for index in range(3))  # type: ignore[return-value]
    except (TypeError, ValueError):
        return (0, 0, 0)


def _next_minor_version(version: Any) -> str:
    major, minor, _ = _parse_agreement_version(version)
    return "1.0.0" if major == 0 else f"{major}.{minor + 1}.0"


def _generate_agreement_id() -> str:
    agreement_id = str(uuid.uuid4())
    uuid.UUID(agreement_id)
    return agreement_id


def _serialize_supporting_documents(rows: list[dict[str, Any]]) -> str:
    documents = []
    for row in rows:
        label = str(row.get("label") or "").strip()
        location = str(row.get("location") or "").strip()
        if not label and not location:
            continue
        if not label or not location:
            raise ValueError("Each supporting document requires both a label and a location.")
        documents.append({"label": label, "location": location})
    return json.dumps(documents, separators=(",", ":"), ensure_ascii=False)


def _deserialize_supporting_documents(value: Any) -> list[dict[str, str]]:
    try:
        documents = json.loads(str(value or "[]"))
    except json.JSONDecodeError as exc:
        raise ValueError("supporting_documents_json must be a JSON list.") from exc
    if not isinstance(documents, list) or any(not isinstance(item, dict) for item in documents):
        raise ValueError("supporting_documents_json must be a JSON list of document objects.")
    # Apply the same strict shape validation used when saving.
    canonical = _serialize_supporting_documents(documents)
    return json.loads(canonical)


def _serialize_approved_usage(selected: Any, options: list[str]) -> str:
    selected_values = {str(value) for value in (selected or [])}
    unknown = selected_values.difference(options)
    if unknown:
        raise ValueError("approved_usage_json contains unconfigured value(s): " + ", ".join(sorted(unknown)))
    ordered = [option for option in options if option in selected_values]
    if not ordered:
        raise ValueError("At least one approved usage is required.")
    return json.dumps(ordered, separators=(",", ":"), ensure_ascii=False)


def _deserialize_approved_usage(value: Any, options: list[str]) -> list[str]:
    try:
        selected = json.loads(str(value or "[]"))
    except json.JSONDecodeError as exc:
        raise ValueError("approved_usage_json must be a JSON list.") from exc
    if not isinstance(selected, list) or any(not isinstance(item, str) for item in selected):
        raise ValueError("approved_usage_json must be a JSON list of configured values.")
    return json.loads(_serialize_approved_usage(selected, options))


def _business_agreement_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    snapshot = {field: row.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS}
    snapshot["supporting_documents_json"] = _serialize_supporting_documents(
        _deserialize_supporting_documents(row.get("supporting_documents_json", "[]"))
    )
    snapshot["approved_usage_json"] = str(row.get("approved_usage_json") or "")
    snapshot["custom_fields_json"] = serialize_custom_fields(deserialize_custom_fields(row.get("custom_fields_json", "")))
    return snapshot


def _agreement_identity_text(row: dict[str, Any] | None) -> str:
    if not row:
        return "Agreement ID and version are generated when saved."
    current_version = str(row.get("agreement_version") or "")
    return (
        f"Agreement ID: {row.get('agreement_id', '')}<br>"
        f"Current version: {current_version}<br>"
        f"Next version on save: {_next_minor_version(current_version)}<br>"
        "Saving this change will append a new version. Existing rows will not be overwritten."
    )


def _steward_label(row: dict[str, Any]) -> str:
    parts = [str(row.get(field) or "").strip() for field in ("steward_name", "steward_role", "contact")]
    return " | ".join(part for part in parts if part) or str(row.get("steward_id") or "Unnamed steward")


def _agreement_label(row: dict[str, Any]) -> str:
    row_id = str(row.get("agreement_id") or "").strip()
    name = str(row.get("agreement_name") or row_id)
    version = str(row.get("agreement_version") or "")
    return f"{name} ({row_id} / v{version})"


def _create_or_update_data_agreement(*, spark: Any, config: Any, env: str, values: dict[str, Any], selected_agreement: dict[str, Any] | None = None, custom_fields: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> dict[str, Any]:
    row = {field: values.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS}
    existing_rows = list_all_data_agreement_rows(config, env, spark_session=spark, missing_ok=True)
    selected_id = str((selected_agreement or {}).get("agreement_id") or "").strip()
    if selected_id:
        same_agreement = [item for item in existing_rows if str(item.get("agreement_id") or "").strip() == selected_id]
        latest = max(same_agreement, key=lambda item: _parse_agreement_version(item.get("agreement_version")), default=selected_agreement)
        row["agreement_id"] = selected_id
        row["agreement_version"] = _next_minor_version(latest.get("agreement_version"))
    else:
        latest = None
        row["agreement_id"] = _generate_agreement_id()
        row["agreement_version"] = "1.0.0"
    uuid.UUID(row["agreement_id"])
    row["supporting_documents_json"] = _serialize_supporting_documents(values.get("supporting_documents", []))
    usage_options = [str(option) for option in (dict(config_value(config, "data_agreement_widget", {}) or {}).get("approved_usage_options", WIDGET_CONFIG_DEFAULTS["data_agreement_widget"]["approved_usage_options"]) or [])]
    row["approved_usage_json"] = _serialize_approved_usage(values.get("approved_usage", []), usage_options)
    required = ["agreement_id", "agreement_version", "agreement_name", "domain", "provider_steward_id", "recipient_steward_id", "recipient", "start_date", "expiry_date", "business_purpose"]
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError("Missing required agreement field(s): " + ", ".join(missing))
    row["start_date"] = parse_iso_date(row.get("start_date"), "start_date", required=True)
    row["expiry_date"] = parse_iso_date(row.get("expiry_date"), "expiry_date", required=True)
    if row["expiry_date"] < row["start_date"]:
        raise ValueError("expiry_date must be on or after start_date.")
    active_steward_ids = {str(item["steward_id"]) for item in list_data_stewards(config, env, spark_session=spark, active_only=True)}
    provider_id = str(row["provider_steward_id"])
    recipient_id = str(row["recipient_steward_id"])
    if provider_id == recipient_id:
        raise ValueError("Provider and recipient data stewards must be different.")
    if provider_id not in active_steward_ids:
        raise ValueError("provider_steward_id must reference an active data steward.")
    if recipient_id not in active_steward_ids:
        raise ValueError("recipient_steward_id must reference an active data steward.")
    row["custom_fields_json"] = serialize_custom_fields(custom_fields)
    if latest is not None:
        if _business_agreement_snapshot(row) == _business_agreement_snapshot(latest):
            return {**latest, "_fabricops_no_change": True, "_fabricops_message": "No changes detected. Nothing was appended."}
    if any(str(item.get("agreement_id") or "").strip() == row["agreement_id"] and str(item.get("agreement_version") or "").strip() == row["agreement_version"] for item in existing_rows):
        raise ValueError(f"Agreement {row['agreement_id']} version {row['agreement_version']} already exists. Select the existing agreement to create the next version, or create a new agreement.")
    row.update(build_runtime_audit_fields(config=config, env=env, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    write_widget_metadata_row(spark=spark, config=config, env=env, table=str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), row=row)
    return row
