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
    form_section,
    form_page,
    form_grid,
    execution_log_section,
    checkbox_group,
    action_row,
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
    status_message,
    require_ipywidgets,
    write_widget_metadata_row,
    render_custom_fields,
)


def widget_render_data_agreement(*, spark: Any, context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Render a wide, single-flow data-agreement editor.

    The editor caches active data stewards, keeps one in-memory draft, and
    appends one complete agreement row only after final validation.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for initial metadata reads, explicit steward
        refreshes, and the final append-only write.
    context : dict[str, Any], optional
        Advanced override for the active Fabric context. When omitted, the
        helper uses ``FABRIC_CONTEXT`` initialized by ``00_env_config``.

    Returns
    -------
    dict[str, Any]
        Stable root, section, field, document, steward, and save controls.

    """
    config, env, _context = resolve_fabric_context(context=context)
    widgets = require_ipywidgets()
    from IPython import display as ip

    kind = "data_agreement_widget"
    widget_config = {**WIDGET_CONFIG_DEFAULTS[kind], **dict(config_value(config, kind, {}) or {})}
    steward_fields = ("provider_steward_id", "recipient_steward_id")
    fields = [
        field
        for field in get_widget_visible_fields(config, kind)
        if field != "recipient" and field not in steward_fields
    ]
    after_save_callbacks: list[Any] = []
    row_lookup: dict[str, dict[str, Any]] = {}
    draft: dict[str, Any] = {}

    def _row_id(row: dict[str, Any]) -> str:
        return str(row.get("agreement_id") or "").strip()

    def _refresh_lookup(rows: list[dict[str, Any]]) -> None:
        row_lookup.clear()
        row_lookup.update({_row_id(row): row for row in rows if _row_id(row)})

    existing_rows = [
        row for row in list_data_agreements(config, env, spark_session=spark, missing_ok=True) if _row_id(row)
    ]
    _refresh_lookup(existing_rows)
    selected_selector = render_searchable_selector(
        widgets=widgets,
        label="Agreement",
        rows=existing_rows,
        label_fn=_agreement_label,
        value_fn=_row_id,
        placeholder="Search agreements...",
        search_fields=["agreement_name", "agreement_id", "agreement_version", "domain"],
        empty_label="Create new agreement",
        search_label="Search agreements",
    )
    selected = selected_selector["selector"]
    identity_context = widgets.HTML(value=_agreement_identity_text(None))

    active_steward_rows = list_data_stewards(config, env, spark_session=spark, active_only=True, missing_ok=True)
    active_steward_ids = {
        steward_id for row in active_steward_rows if (steward_id := str(row.get("steward_id") or "").strip())
    }
    form = {field: standard_widget(field) for field in fields}
    steward_field_selectors: dict[str, dict[str, Any]] = {}
    for field in steward_fields:
        selector = render_searchable_selector(
            widgets=widgets,
            label=FIELD_LABELS[field],
            rows=active_steward_rows,
            label_fn=_steward_label,
            value_fn=lambda row: str(row.get("steward_id") or "").strip(),
            placeholder="Search active stewards...",
            search_fields=["steward_name", "steward_role", "contact", "steward_id"],
            context_fields=[("steward_name", "Steward name"), ("steward_role", "Role"), ("contact", "Contact")],
            empty_label="Select an active data steward",
            search_label=(
                "Search provider data stewards" if field == "provider_steward_id" else "Search recipient data stewards"
            ),
        )
        steward_field_selectors[field] = selector
        form[field] = selector["selector"]

    custom = render_custom_fields(widget_config)
    usage_options = [str(option) for option in widget_config.get("approved_usage_options", [])]
    if (
        not usage_options
        or len(set(usage_options)) != len(usage_options)
        or any(not option.strip() for option in usage_options)
    ):
        raise ValueError("approved_usage_options must contain unique, non-empty values.")
    approved_usage_checkboxes = {
        option: widgets.Checkbox(value=False, description=option.replace("_", " ").title()) for option in usage_options
    }

    supporting_document_rows: list[dict[str, Any]] = []
    supporting_documents = widgets.VBox([])

    def _render_document_rows() -> None:
        supporting_documents.children = tuple(row["container"] for row in supporting_document_rows)

    def _add_document_row(label: str = "", location: str = "") -> None:
        name_label = widgets.HTML(value="<b>Document name</b>", layout=widgets.Layout(width="115px"))
        label_widget = widgets.Text(value=label, description="", layout=widgets.Layout(width="28%", min_width="180px"))
        link_label = widgets.HTML(value="<b>Document link</b>", layout=widgets.Layout(width="110px"))
        location_widget = widgets.Text(
            value=location, description="", layout=widgets.Layout(width="38%", min_width="240px")
        )
        remove = widgets.Button(description="Remove document")
        record = {"label": label_widget, "location": location_widget, "remove": remove}
        record["container"] = widgets.HBox(
            [name_label, label_widget, link_label, location_widget, remove],
            layout=widgets.Layout(display="flex", flex_flow="row wrap", align_items="center", width="100%", gap="6px"),
        )

        def _remove(_: Any) -> None:
            supporting_document_rows.remove(record)
            _render_document_rows()

        remove.on_click(_remove)
        supporting_document_rows.append(record)
        _render_document_rows()

    add_supporting_document_button = widgets.Button(description="Add another document")
    add_supporting_document_button.on_click(lambda _: _add_document_row())
    _add_document_row()

    steward_prerequisite_message = (
        "At least two distinct active data stewards are required before an agreement can be saved. "
        "Create or reactivate another data steward, then select Refresh active stewards."
    )
    save = widgets.Button(description="Save Agreement")
    status = status_message(widgets)
    execution_output = widgets.Output(layout=widgets.Layout(width="100%", height="auto", overflow="visible"))

    def _set_status(message: str, *, error: bool = False) -> None:
        colour = "#a4262c" if error else "#107c10"
        status.value = f'<span style="color:{colour}">{message}</span>'

    def _update_steward_prerequisite(*, refreshed: bool = False) -> None:
        save.disabled = len(active_steward_ids) < 2
        if save.disabled:
            _set_status(steward_prerequisite_message, error=True)
        elif refreshed:
            _set_status("Active data stewards refreshed.")
        else:
            status.value = ""

    def _refresh_existing_options(selected_id: str | None = None) -> None:
        rows = [row for row in list_data_agreements(config, env, spark_session=spark, missing_ok=True) if _row_id(row)]
        _refresh_lookup(rows)
        selected.refresh_rows(rows, selected_id if selected_id in row_lookup else "")

    def _refresh_steward_dropdowns() -> None:
        nonlocal active_steward_rows, active_steward_ids
        active_steward_rows = list_data_stewards(config, env, spark_session=spark, active_only=True, missing_ok=True)
        active_steward_ids = {
            steward_id for row in active_steward_rows if (steward_id := str(row.get("steward_id") or "").strip())
        }
        for field in steward_fields:
            current = str(form[field].value or "")
            form[field].refresh_rows(active_steward_rows, current if current in active_steward_ids else "")
        _update_steward_prerequisite(refreshed=True)

    refresh_stewards = widgets.Button(description="Refresh active stewards")
    refresh_stewards.on_click(lambda _: _refresh_steward_dropdowns())

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
            option_values = [
                option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options
            ]
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
        identity_context.value = _agreement_identity_text(row or None)
        draft.clear()
        draft.update(row)

    selected.observe(_populate, names="value")
    callbacks = getattr(selected, "callbacks", None)
    if isinstance(callbacks, list) and callbacks:
        callbacks.insert(0, callbacks.pop())

    def _save(_: Any) -> None:
        save.disabled = True
        status.value = ""
        try:
            values = {
                key: to_iso_date(widget.value) if key in {"start_date", "expiry_date"} else widget.value
                for key, widget in form.items()
            }
            values["supporting_documents"] = [
                {"label": row["label"].value, "location": row["location"].value} for row in supporting_document_rows
            ]
            values["approved_usage"] = [
                option for option, checkbox in approved_usage_checkboxes.items() if checkbox.value
            ]
            draft.clear()
            draft.update(values)
            row = _create_or_update_data_agreement(
                spark=spark,
                config=config,
                env=env,
                values=draft,
                selected_agreement=row_lookup.get(selected.value) if selected.value else None,
                custom_fields=collect_custom_fields(widget_config, custom),
                active_steward_ids=active_steward_ids,
            )
            if row.get("_fabricops_no_change"):
                _set_status(str(row.get("_fabricops_message", "No changes detected.")))
            else:
                _set_status(
                    f"Saved {row.get('agreement_name', '')} ({row['agreement_id']} v{row['agreement_version']})."
                )
                for callback in after_save_callbacks:
                    callback(row)
            row_lookup[row["agreement_id"]] = row
            selected.refresh_rows(list(row_lookup.values()), row["agreement_id"])
            identity_context.value = _agreement_identity_text(row)
        except Exception as exc:
            _set_status(f"Error: {exc}", error=True)
        finally:
            save.disabled = len(active_steward_ids) < 2

    save.on_click(_save)
    _update_steward_prerequisite()
    full_width_layout = widgets.Layout(width="100%", height="auto", overflow="visible")
    row_layout = widgets.Layout(
        display="flex",
        flex_flow="row wrap",
        justify_content="space-between",
        align_items="flex-start",
        width="100%",
    )
    if "business_purpose" in form:
        form["business_purpose"].layout = widgets.Layout(width="100%", height="90px")

    detail_controls = [form_grid(widgets, [form[field] for field in ("agreement_name", "domain") if field in form])]
    detail_controls.append(
        form_grid(widgets, [form[field] for field in ("start_date", "expiry_date") if field in form])
    )
    if "business_purpose" in form:
        detail_controls.append(form["business_purpose"])
    details_section = form_section(widgets, title="Agreement details", children=detail_controls)

    steward_panels = []
    for field in steward_fields:
        selector_panel = steward_field_selectors[field]["container"]
        selector_panel.layout = full_width_layout
        steward_panels.append(
            widgets.VBox(
                [
                    widgets.HTML(
                        value=(
                            '<div style="color:#0f548c;font-size:14px;font-weight:600;'
                            f'margin-bottom:4px;">{FIELD_LABELS[field]}</div>'
                        )
                    ),
                    selector_panel,
                ],
                layout=widgets.Layout(
                    width="49%",
                    height="auto",
                    overflow="visible",
                    min_width="280px",
                    flex="1 1 320px",
                    border="1px solid #d7e7f5",
                    padding="10px 12px",
                ),
            )
        )
    steward_section = form_section(
        widgets,
        title="Provider and recipient data stewards",
        children=[
            widgets.HBox(steward_panels, layout=row_layout),
            widgets.HBox([refresh_stewards], layout=widgets.Layout(justify_content="flex-end", width="100%")),
        ],
    )

    supporting_section = form_section(
        widgets,
        title="Supporting documents",
        children=[supporting_documents, add_supporting_document_button],
    )
    scope_section = form_section(
        widgets,
        title="Agreement scope or classification",
        children=[
            checkbox_group(widgets, label="Approved usages", checkboxes=approved_usage_checkboxes.values()),
            widgets.VBox(
                [
                    widgets.HTML(
                        value=(
                            '<div style="color:#0f548c;font-size:14px;font-weight:600;'
                            'margin-bottom:4px;">Custom columns</div>'
                        )
                    ),
                    form_grid(widgets, custom.values()),
                ],
                layout=widgets.Layout(
                    width="100%", height="auto", overflow="visible",
                    border="1px solid #d7e7f5", padding="10px 12px",
                ),
            ) if custom else widgets.VBox([]),
        ],
    )
    selection_section = form_section(
        widgets,
        title="Agreement selection",
        children=[selected_selector["container"], identity_context],
    )
    form_flow = widgets.VBox(
        [selection_section, details_section, steward_section, supporting_section, scope_section],
        layout=full_width_layout,
    )
    actions = form_section(
        widgets,
        title="Save agreement",
        children=[action_row(widgets, [save])],
    )
    result_section = form_section(
        widgets,
        title="Save result",
        children=[status, execution_log_section(widgets, execution_output)],
    )
    container = form_page(
        widgets,
        title="Data Agreement Creation Widget",
        description=(
            "Governance-level agreement: defines who is sharing data, why it may be shared, "
            "and the governing conditions. Specific datasets and technical delivery terms are "
            "defined later through Data Contracts."
        ),
        children=[form_flow, actions, result_section],
    )
    ip.display(container)
    return {
        "container": container,
        "draft": draft,
        "existing_record": selected,
        "existing_record_search": selected_selector["search"],
        "existing_record_context": selected_selector["context"],
        "existing_records_by_id": row_lookup,
        "identity_context": identity_context,
        "fields": form,
        "provider_steward_selector": form["provider_steward_id"],
        "recipient_steward_selector": form["recipient_steward_id"],
        "supporting_documents": supporting_document_rows,
        "supporting_documents_container": supporting_documents,
        "add_supporting_document_button": add_supporting_document_button,
        "approved_usage_checkboxes": approved_usage_checkboxes,
        "custom_fields": custom,
        "refresh_stewards_button": refresh_stewards,
        "refresh_existing_options": _refresh_existing_options,
        "refresh_steward_options": _refresh_steward_dropdowns,
        "after_save_callbacks": after_save_callbacks,
        "save_button": save,
        "status": status,
        "execution_output": execution_output,
        "execution_log_section": result_section.children[2],
    }


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
    snapshot["custom_fields_json"] = serialize_custom_fields(
        deserialize_custom_fields(row.get("custom_fields_json", ""))
    )
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


def _create_or_update_data_agreement(
    *,
    spark: Any,
    config: Any,
    env: str,
    values: dict[str, Any],
    selected_agreement: dict[str, Any] | None = None,
    custom_fields: dict[str, Any] | None = None,
    committed_by: str | None = None,
    committed_at: str | None = None,
    runtime_context: dict[str, Any] | None = None,
    active_steward_ids: set[str] | None = None,
) -> dict[str, Any]:
    row = {field: values.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS}
    existing_rows = list_all_data_agreement_rows(config, env, spark_session=spark, missing_ok=True)
    selected_id = str((selected_agreement or {}).get("agreement_id") or "").strip()
    if selected_id:
        same_agreement = [item for item in existing_rows if str(item.get("agreement_id") or "").strip() == selected_id]
        latest = max(
            same_agreement,
            key=lambda item: _parse_agreement_version(item.get("agreement_version")),
            default=selected_agreement,
        )
        row["agreement_id"] = selected_id
        row["agreement_version"] = _next_minor_version(latest.get("agreement_version"))
    else:
        latest = None
        row["agreement_id"] = _generate_agreement_id()
        row["agreement_version"] = "1.0.0"
    uuid.UUID(row["agreement_id"])
    row["supporting_documents_json"] = _serialize_supporting_documents(values.get("supporting_documents", []))
    usage_options = [
        str(option)
        for option in (
            dict(config_value(config, "data_agreement_widget", {}) or {}).get(
                "approved_usage_options", WIDGET_CONFIG_DEFAULTS["data_agreement_widget"]["approved_usage_options"]
            )
            or []
        )
    ]
    row["approved_usage_json"] = _serialize_approved_usage(values.get("approved_usage", []), usage_options)
    required = [
        "agreement_id",
        "agreement_version",
        "agreement_name",
        "domain",
        "provider_steward_id",
        "recipient_steward_id",
        "start_date",
        "expiry_date",
        "business_purpose",
    ]
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError("Missing required agreement field(s): " + ", ".join(missing))
    row["start_date"] = parse_iso_date(row.get("start_date"), "start_date", required=True)
    row["expiry_date"] = parse_iso_date(row.get("expiry_date"), "expiry_date", required=True)
    if row["expiry_date"] < row["start_date"]:
        raise ValueError("expiry_date must be on or after start_date.")
    if active_steward_ids is None:
        active_steward_ids = {
            str(item["steward_id"]) for item in list_data_stewards(config, env, spark_session=spark, active_only=True)
        }
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
            return {
                **latest,
                "_fabricops_no_change": True,
                "_fabricops_message": "No changes detected. Nothing was appended.",
            }
    if any(
        str(item.get("agreement_id") or "").strip() == row["agreement_id"]
        and str(item.get("agreement_version") or "").strip() == row["agreement_version"]
        for item in existing_rows
    ):
        raise ValueError(
            f"Agreement {row['agreement_id']} version {row['agreement_version']} already exists. Select the existing agreement to create the next version, or create a new agreement."
        )
    row.update(
        build_runtime_audit_fields(
            config=config,
            env=env,
            committed_by=committed_by,
            committed_at=committed_at,
            runtime_context=runtime_context,
        )
    )
    metadata_tables = config_value(config, "metadata_tables", {}) or {}
    write_widget_metadata_row(
        spark=spark,
        config=config,
        env=env,
        table=str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)),
        row=row,
    )
    return row
