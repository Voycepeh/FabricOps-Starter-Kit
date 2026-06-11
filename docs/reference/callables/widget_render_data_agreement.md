# widget_render_data_agreement

Render the standalone data-agreement intake widget.

## What this is for and when to use it

Render the standalone data-agreement intake widget.

- Render the standalone data-agreement intake widget.

## When not to use it

- Not documented yet

## Example

```python
Not documented yet
```

## Inputs

<div class="module-table-scroll reference-input-table">
<table class="reference-function-table">
  <thead>
    <tr>
      <th>Parameter</th>
      <th>Required</th>
      <th>Meaning</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td data-label="Parameter"><code>config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Configuration containing agreement widget fields and metadata routing.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key configured by ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Fabric Spark session used for metadata reads and append-only writes.</td>
    </tr>
  </tbody>
</table>
</div>

## Output

dict[str, Any]
    Rendered controls, including read-only generated-identifier context.

## Errors and side effects

**Errors:** Not documented yet

**Side effects:** Not documented yet

## Related functions

Not documented yet

<details class="reference-implementation-details">
<summary>Implementation details</summary>

### Call flow

```text
widget_render_data_agreement(...)
└── _render_maintenance_widget(...)
    ├── _agreement_identity_text(...)
    │   └── _next_minor_version(...)
    │       └── _parse_contract_version(...)
    ├── _collect_custom_fields(...)
    │   └── _to_iso_date(...)
    ├── _config_value(...)
    ├── _create_or_update_data_agreement(...)
    │   ├── _build_runtime_audit_fields(...)
    │   │   ├── _context_get(...)
    │   │   ├── _current_audit_timestamp(...)
    │   │   │   └── _get_audit_timezone(...)
    │   │   │       └── _validate_audit_timezone(...)
    │   │   ├── _runtime_context(...)
    │   │   │   └── _context_get(...)
    │   │   └── _safe_str(...)
    │   ├── _business_agreement_snapshot(...)
    │   │   ├── _deserialize_custom_fields(...)
    │   │   └── _serialize_custom_fields(...)
    │   ├── _config_value(...)
    │   ├── _generate_agreement_id(...)
    │   ├── _list_all_data_agreement_rows(...)
    │   │   ├── _coerce_row_dicts(...)
    │   │   ├── _config_value(...)
    │   │   └── read_lakehouse_table(...)
    │   │       ├── _current_database_matches(...)
    │   │       ├── _get_spark(...)
    │   │       ├── _get_store(...)
    │   │       ├── _normalize_table_name(...)
    │   │       ├── _registered_table_identifier(...)
    │   │       │   ├── _normalize_table_name(...)
    │   │       │   └── _quote_identifier(...)
    │   │       └── _uses_registered_metadata_table(...)
    │   ├── _list_data_stewards(...)
    │   │   ├── _active_steward(...)
    │   │   │   └── _to_bool(...)
    │   │   ├── _config_value(...)
    │   │   ├── _latest_by_key(...)
    │   │   │   └── _coerce_row_dicts(...)
    │   │   └── read_lakehouse_table(...)
    │   │       ├── _current_database_matches(...)
    │   │       ├── _get_spark(...)
    │   │       ├── _get_store(...)
    │   │       ├── _normalize_table_name(...)
    │   │       ├── _registered_table_identifier(...)
    │   │       │   ├── _normalize_table_name(...)
    │   │       │   └── _quote_identifier(...)
    │   │       └── _uses_registered_metadata_table(...)
    │   ├── _next_minor_version(...)
    │   │   └── _parse_contract_version(...)
    │   ├── _parse_contract_version(...)
    │   ├── _parse_iso_date(...)
    │   ├── _serialize_custom_fields(...)
    │   └── _write_row(...)
    │       └── write_lakehouse_table(...)
    │           ├── _get_store(...)
    │           ├── _normalize_table_name(...)
    │           ├── _registered_table_identifier(...)
    │           │   ├── _normalize_table_name(...)
    │           │   └── _quote_identifier(...)
    │           └── _uses_registered_metadata_table(...)
    ├── _create_or_update_data_steward(...)
    │   ├── _active_steward(...)
    │   │   └── _to_bool(...)
    │   ├── _build_runtime_audit_fields(...)
    │   │   ├── _context_get(...)
    │   │   ├── _current_audit_timestamp(...)
    │   │   │   └── _get_audit_timezone(...)
    │   │   │       └── _validate_audit_timezone(...)
    │   │   ├── _runtime_context(...)
    │   │   │   └── _context_get(...)
    │   │   └── _safe_str(...)
    │   ├── _config_value(...)
    │   ├── _generate_steward_id(...)
    │   ├── _parse_iso_date(...)
    │   ├── _serialize_custom_fields(...)
    │   ├── _to_bool(...)
    │   └── _write_row(...)
    │       └── write_lakehouse_table(...)
    │           ├── _get_store(...)
    │           ├── _normalize_table_name(...)
    │           ├── _registered_table_identifier(...)
    │           │   ├── _normalize_table_name(...)
    │           │   └── _quote_identifier(...)
    │           └── _uses_registered_metadata_table(...)
    ├── _deserialize_custom_fields(...)
    ├── _get_widget_visible_fields(...)
    │   └── _config_value(...)
    ├── _list_data_agreements(...)
    │   ├── _latest_agreement_versions(...)
    │   │   ├── _coerce_row_dicts(...)
    │   │   └── _parse_contract_version(...)
    │   └── _list_all_data_agreement_rows(...)
    │       ├── _coerce_row_dicts(...)
    │       ├── _config_value(...)
    │       └── read_lakehouse_table(...)
    │           ├── _current_database_matches(...)
    │           ├── _get_spark(...)
    │           ├── _get_store(...)
    │           ├── _normalize_table_name(...)
    │           ├── _registered_table_identifier(...)
    │           │   ├── _normalize_table_name(...)
    │           │   └── _quote_identifier(...)
    │           └── _uses_registered_metadata_table(...)
    ├── _list_data_stewards(...)
    │   ├── _active_steward(...)
    │   │   └── _to_bool(...)
    │   ├── _config_value(...)
    │   ├── _latest_by_key(...)
    │   │   └── _coerce_row_dicts(...)
    │   └── read_lakehouse_table(...)
    │       ├── _current_database_matches(...)
    │       ├── _get_spark(...)
    │       ├── _get_store(...)
    │       ├── _normalize_table_name(...)
    │       ├── _registered_table_identifier(...)
    │       │   ├── _normalize_table_name(...)
    │       │   └── _quote_identifier(...)
    │       └── _uses_registered_metadata_table(...)
    ├── _render_custom_fields(...)
    │   ├── _require_ipywidgets(...)
    │   ├── _to_bool(...)
    │   └── _widget_common(...)
    ├── _render_searchable_selector(...)
    │   ├── _html_escape(...)
    │   └── _widget_common(...)
    ├── _require_ipywidgets(...)
    ├── _standard_widget(...)
    │   ├── _require_ipywidgets(...)
    │   ├── _to_bool(...)
    │   └── _widget_common(...)
    ├── _to_bool(...)
    └── _to_iso_date(...)
```

### Internal helpers used by this callable

### `def _render_maintenance_widget(*, spark: Any, config: Any, env_name: str, kind: str, display_widget: bool=True) -> dict[str, Any]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L1130-L1338">View `_render_maintenance_widget` on GitHub</a>

**Code:**

```python
def _render_maintenance_widget(*, spark: Any, config: Any, env_name: str, kind: str, display_widget: bool = True) -> dict[str, Any]:
    widgets = _require_ipywidgets()
    from IPython import display as ip

    is_steward = kind == "data_steward_widget"
    prompt = "Create new steward" if is_steward else "Create new agreement"
    widget_config = {**_WIDGET_CONFIG_DEFAULTS[kind], **dict(_config_value(config, kind, {}) or {})}
    fields = _get_widget_visible_fields(config, kind)
    after_save_callbacks: list[Any] = []
    row_lookup: dict[str, dict[str, Any]] = {}

    def _row_id(row: dict[str, Any]) -> str:
        return str(row.get("steward_id" if is_steward else "agreement_id") or "").strip()

    def _existing_rows() -> list[dict[str, Any]]:
        return _list_data_stewards(config, env_name, spark_session=spark, active_only=False, missing_ok=True) if is_steward else _list_data_agreements(config, env_name, spark_session=spark, missing_ok=True)

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
    identity_context = None if is_steward else widgets.HTML(value=_agreement_identity_text(None))

    roles = [str(option).strip() for option in (_config_value(config, "steward_role_options", DEFAULT_STEWARD_ROLE_OPTIONS) or []) if str(option).strip()]
    steward_role_options = [(role, role) for role in roles] if is_steward else None
    form = {}
    steward_field_selector = None
    for field in fields:
        if field == "steward_id" and not is_steward:
            steward_rows = _list_data_stewards(config, env_name, spark_session=spark, active_only=True, missing_ok=True)
            steward_field_selector = _render_searchable_selector(
                widgets=widgets,
                label=FIELD_LABELS.get(field, field.replace("_", " ").title()),
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
            rows = _list_data_stewards(config, env_name, spark_session=spark, active_only=True, missing_ok=True)
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
            widget.value = _to_bool(value)
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
        stored = _deserialize_custom_fields(row.get("custom_fields_json", ""))
        for key, widget in custom.items():
            _apply_widget_value(widget, stored.get(key, widget.value))
        if identity_context is not None:
            identity_context.value = _agreement_identity_text(row if row else None)

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
                    key: _to_iso_date(widget.value) if key in {"effective_from", "effective_to", "start_date", "expiry_date"} else widget.value
                    for key, widget in form.items()
                }
                extras = _collect_custom_fields(widget_config, custom)
                if is_steward:
                    if selected.value:
                        values["steward_id"] = selected.value
                        values["_existing_steward_role"] = row_lookup.get(selected.value, {}).get("steward_role", "")
                    row = _create_or_update_data_steward(spark=spark, config=config, env_name=env_name, values=values, custom_fields=extras)
                    _refresh_existing_options(row["steward_id"])
                    for callback in after_save_callbacks:
                        callback(row)
                    print(f"Saved data steward: {row.get('steward_name', '')} ({row['steward_id']})")
                else:
                    selected_row = row_lookup.get(selected.value) if selected.value else None
                    row = _create_or_update_data_agreement(spark=spark, config=config, env_name=env_name, values=values, selected_agreement=selected_row, custom_fields=extras)
                    if row.get("_fabricops_no_change"):
                        print(row.get("_fabricops_message", "No changes detected. Nothing was appended."))
                    else:
                        print(f"Saved data agreement: {row.get('agreement_name', '')} ({row['agreement_id']} v{row['contract_version']})")
                    _refresh_existing_options(row["agreement_id"])
                    if not row.get("_fabricops_no_change"):
                        for callback in after_save_callbacks:
                            callback(row)
                    if identity_context is not None:
                        identity_context.value = _agreement_identity_text(row)
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
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_render_maintenance_widget`.

### `def _agreement_identity_text(row: dict[str, Any] | None) -> str`

**What it does:**

Return read-only agreement version context for the notebook form.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L1117-L1127">View `_agreement_identity_text` on GitHub</a>

**Code:**

```python
def _agreement_identity_text(row: dict[str, Any] | None) -> str:
    """Return read-only agreement version context for the notebook form."""
    if not row:
        return "Agreement ID and version are generated when saved."
    current_version = str(row.get("contract_version") or "")
    return (
        f"Agreement ID: {row.get('agreement_id', '')}<br>"
        f"Current version: {current_version}<br>"
        f"Next version on save: {_next_minor_version(current_version)}<br>"
        "Saving this change will append a new version. Existing rows will not be overwritten."
    )
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_agreement_identity_text`.

### `def _next_minor_version(version: Any) -> str`

**What it does:**

Return the next minor contract version, defaulting to ``1.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L647-L650">View `_next_minor_version` on GitHub</a>

**Code:**

```python
def _next_minor_version(version: Any) -> str:
    """Return the next minor contract version, defaulting to ``1.0.0``."""
    major, minor, _ = _parse_contract_version(version)
    return "1.0.0" if major == 0 else f"{major}.{minor + 1}.0"
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_next_minor_version`.

### `def _parse_contract_version(version: Any) -> tuple[int, int, int]`

**What it does:**

Parse a semantic contract version into a comparable tuple.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L638-L644">View `_parse_contract_version` on GitHub</a>

**Code:**

```python
def _parse_contract_version(version: Any) -> tuple[int, int, int]:
    """Parse a semantic contract version into a comparable tuple."""
    try:
        parts = str(version or "").strip().split(".")
        return tuple(int(parts[index]) if index < len(parts) else 0 for index in range(3))  # type: ignore[return-value]
    except (TypeError, ValueError):
        return (0, 0, 0)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_parse_contract_version`.

### `def _collect_custom_fields(config: list[dict[str, Any]] | dict[str, Any], widgets_by_key: dict[str, Any]) -> dict[str, Any]`

**What it does:**

Collect and validate configured custom-field widget values.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L362-L394">View `_collect_custom_fields` on GitHub</a>

**Code:**

```python
def _collect_custom_fields(config: list[dict[str, Any]] | dict[str, Any], widgets_by_key: dict[str, Any]) -> dict[str, Any]:
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
            value = _to_iso_date(value)
        if definition.get("required") and value in (None, "", []):
            raise ValueError(f"{definition.get('label', key)} is required.")
        values[key] = value
    return values
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_collect_custom_fields`.

### `def _to_iso_date(value: Any) -> str`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L698-L701">View `_to_iso_date` on GitHub</a>

**Code:**

```python
def _to_iso_date(value: Any) -> str:
    if value is None:
        return ""
    return value.date().isoformat() if isinstance(value, datetime) else value.isoformat() if isinstance(value, date) else str(value)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_to_iso_date`.

### `def _config_value(config: Any, name: str, default: Any) -> Any`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L149-L153">View `_config_value` on GitHub</a>

**Code:**

```python
def _config_value(config: Any, name: str, default: Any) -> Any:
    agreement_config = getattr(config, "data_agreement_config", config)
    if isinstance(agreement_config, dict):
        return agreement_config.get(name, default)
    return getattr(agreement_config, name, default)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_config_value`.

### `def _create_or_update_data_agreement(*, spark: Any, config: Any, env_name: str, values: dict[str, Any], selected_agreement: dict[str, Any] | None=None, custom_fields: dict[str, Any] | None=None, committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> dict[str, Any]`

**What it does:**

Append a new agreement or a new semantic version of an existing one.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L711-L755">View `_create_or_update_data_agreement` on GitHub</a>

**Code:**

```python
def _create_or_update_data_agreement(*, spark: Any, config: Any, env_name: str, values: dict[str, Any], selected_agreement: dict[str, Any] | None = None, custom_fields: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append a new agreement or a new semantic version of an existing one.

    Reusing ``selected_agreement`` preserves its stable ``agreement_id`` and
    increments from the latest stored version. Runtime audit fields remain
    backend-managed.
    """
    row = {field: values.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS}
    existing_rows = _list_all_data_agreement_rows(config, env_name, spark_session=spark, missing_ok=True)
    selected_id = str((selected_agreement or {}).get("agreement_id") or "").strip()
    if selected_id:
        same_agreement = [item for item in existing_rows if str(item.get("agreement_id") or "").strip() == selected_id]
        latest = max(same_agreement, key=lambda item: _parse_contract_version(item.get("contract_version")), default=selected_agreement)
        row["agreement_id"] = selected_id
        row["contract_version"] = _next_minor_version(latest.get("contract_version"))
    else:
        latest = None
        row["agreement_id"] = str(row.get("agreement_id") or "").strip() or _generate_agreement_id()
        row["contract_version"] = str(row.get("contract_version") or "1.0.0").strip()
    required = ["agreement_id", "contract_version", "agreement_name", "domain", "steward_id", "recipient", "start_date", "expiry_date", "business_purpose"]
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError("Missing required agreement field(s): " + ", ".join(missing))
    usage_fields = ["approved_usage_internal", "approved_usage_external", "approved_usage_research"]
    if not any(str(row.get(field) or "").strip() for field in usage_fields):
        raise ValueError("At least one approved usage field is required: internal, external, or research.")
    row["start_date"] = _parse_iso_date(row.get("start_date"), "start_date", required=True)
    row["expiry_date"] = _parse_iso_date(row.get("expiry_date"), "expiry_date", required=True)
    if row["expiry_date"] < row["start_date"]:
        raise ValueError("expiry_date must be on or after start_date.")
    active_steward_ids = {str(item["steward_id"]) for item in _list_data_stewards(config, env_name, spark_session=spark, active_only=True)}
    if str(row["steward_id"]) not in active_steward_ids:
        raise ValueError("steward_id must reference an active data steward.")
    row["custom_fields_json"] = _serialize_custom_fields(custom_fields)
    if latest is not None:
        new_snapshot = _business_agreement_snapshot(row)
        latest_snapshot = _business_agreement_snapshot(latest)
        if new_snapshot == latest_snapshot:
            return {**latest, "_fabricops_no_change": True, "_fabricops_message": "No changes detected. Nothing was appended."}
    if any(str(item.get("agreement_id") or "").strip() == row["agreement_id"] and str(item.get("contract_version") or "").strip() == row["contract_version"] for item in existing_rows):
        raise ValueError(f"Agreement {row['agreement_id']} version {row['contract_version']} already exists. Select the existing agreement to create the next version, or create a new agreement.")
    row.update(_build_runtime_audit_fields(config=config, env=env_name, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    _write_row(spark=spark, config=config, env_name=env_name, table=str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), row=row)
    return row
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_create_or_update_data_agreement`.

### `def _business_agreement_snapshot(row: dict[str, Any]) -> dict[str, Any]`

**What it does:**

Return user-facing agreement values used to detect business changes.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L704-L708">View `_business_agreement_snapshot` on GitHub</a>

**Code:**

```python
def _business_agreement_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    """Return user-facing agreement values used to detect business changes."""
    snapshot = {field: row.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS}
    snapshot["custom_fields_json"] = _serialize_custom_fields(_deserialize_custom_fields(row.get("custom_fields_json", "")))
    return snapshot
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_business_agreement_snapshot`.

### `def _deserialize_custom_fields(custom_fields_json: Any) -> dict[str, Any]`

**What it does:**

Deserialize stored custom-field JSON for widget display.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L118-L146">View `_deserialize_custom_fields` on GitHub</a>

**Code:**

```python
def _deserialize_custom_fields(custom_fields_json: Any) -> dict[str, Any]:
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
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_deserialize_custom_fields`.

### `def _serialize_custom_fields(values: dict[str, Any] | None) -> str`

**What it does:**

Serialize organization-specific intake values to deterministic JSON.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L102-L115">View `_serialize_custom_fields` on GitHub</a>

**Code:**

```python
def _serialize_custom_fields(values: dict[str, Any] | None) -> str:
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
    return json.dumps(values or {}, sort_keys=True, default=_to_iso_date)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_serialize_custom_fields`.

### `def _generate_agreement_id() -> str`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L694-L695">View `_generate_agreement_id` on GitHub</a>

**Code:**

```python
def _generate_agreement_id() -> str:
    return "DA-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_generate_agreement_id`.

### `def _list_all_data_agreement_rows(config: Any, env_name: str, *, spark_session: Any=None, missing_ok: bool=False) -> list[dict[str, Any]]`

**What it does:**

List all append-only agreement rows from the metadata lakehouse.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L672-L681">View `_list_all_data_agreement_rows` on GitHub</a>

**Code:**

```python
def _list_all_data_agreement_rows(config: Any, env_name: str, *, spark_session: Any = None, missing_ok: bool = False) -> list[dict[str, Any]]:
    """List all append-only agreement rows from the metadata lakehouse."""
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    try:
        rows = read_lakehouse_table(config, env_name, "metadata", str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), spark_session=spark_session)
    except Exception:
        if missing_ok:
            return []
        raise
    return _coerce_row_dicts(rows)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_list_all_data_agreement_rows`.

### `def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L397-L402">View `_coerce_row_dicts` on GitHub</a>

**Code:**

```python
def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
    if rows is None:
        return []
    if hasattr(rows, "collect"):
        rows = rows.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_coerce_row_dicts`.

### `def _list_data_stewards(config: Any, env_name: str, *, spark_session: Any=None, active_only: bool=True, missing_ok: bool=False) -> list[dict[str, Any]]`

**What it does:**

List latest append-only steward rows from the metadata lakehouse.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L536-L565">View `_list_data_stewards` on GitHub</a>

**Code:**

```python
def _list_data_stewards(config: Any, env_name: str, *, spark_session: Any = None, active_only: bool = True, missing_ok: bool = False) -> list[dict[str, Any]]:
    """List latest append-only steward rows from the metadata lakehouse.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Metadata lakehouse configuration.
    env_name : str
        Configured environment key.
    spark_session : pyspark.sql.SparkSession, optional
        Fabric Spark session.
    active_only : bool, default=True
        Return only currently effective active steward assignments.
    missing_ok : bool, default=False
        Return an empty list when the table is not available.

    Returns
    -------
    list[dict[str, Any]]
        Latest steward rows sorted by stable ID.
    """
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    try:
        rows = read_lakehouse_table(config, env_name, "metadata", str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), spark_session=spark_session)
    except Exception:
        if missing_ok:
            return []
        raise
    latest = _latest_by_key(rows, "steward_id")
    return [row for row in latest if _active_steward(row)] if active_only else latest
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_list_data_stewards`.

### `def _active_steward(row: dict[str, Any]) -> bool`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L516-L526">View `_active_steward` on GitHub</a>

**Code:**

```python
def _active_steward(row: dict[str, Any]) -> bool:
    is_active = row.get("is_active")
    if is_active not in (None, "") and not _to_bool(is_active):
        return False
    today = datetime.now(timezone.utc).date()
    try:
        starts_before_today = not row.get("effective_from") or date.fromisoformat(str(row["effective_from"])[:10]) <= today
        ends_after_today = not row.get("effective_to") or date.fromisoformat(str(row["effective_to"])[:10]) >= today
        return starts_before_today and ends_after_today
    except ValueError as exc:
        raise ValueError(f"{DATA_STEWARD_TABLE} row '{row.get('steward_id', '')}' has an invalid effective date. Use ISO dates.") from exc
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_active_steward`.

### `def _to_bool(value: Any) -> bool`

**What it does:**

Normalize common notebook and metadata boolean representations.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L497-L513">View `_to_bool` on GitHub</a>

**Code:**

```python
def _to_bool(value: Any) -> bool:
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
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_to_bool`.

### `def _latest_by_key(rows: Any, key: str) -> list[dict[str, Any]]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L488-L494">View `_latest_by_key` on GitHub</a>

**Code:**

```python
def _latest_by_key(rows: Any, key: str) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in _coerce_row_dicts(rows):
        value = str(row.get(key) or "").strip()
        if value and (value not in latest or str(row.get("_committed_at") or "") >= str(latest[value].get("_committed_at") or "")):
            latest[value] = row
    return sorted(latest.values(), key=lambda row: str(row.get(key) or "").lower())
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_latest_by_key`.

### `def _parse_iso_date(value: Any, field_name: str, *, required: bool=False) -> str`

**What it does:**

Return an ISO date string or raise a clear intake validation error.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L572-L582">View `_parse_iso_date` on GitHub</a>

**Code:**

```python
def _parse_iso_date(value: Any, field_name: str, *, required: bool = False) -> str:
    """Return an ISO date string or raise a clear intake validation error."""
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{field_name} is required.")
        return ""
    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO date (YYYY-MM-DD).") from exc
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_parse_iso_date`.

### `def _write_row(*, spark: Any, config: Any, env_name: str, table: str, row: dict[str, Any]) -> None`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L568-L569">View `_write_row` on GitHub</a>

**Code:**

```python
def _write_row(*, spark: Any, config: Any, env_name: str, table: str, row: dict[str, Any]) -> None:
    write_lakehouse_table(spark.createDataFrame([row]), config, env_name, "metadata", table, mode="append")
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_write_row`.

### `def _build_runtime_audit_fields(*, config: Any=None, env: str | None=None, timestamp_field: str='_committed_at', user_field: str='_committed_by', workspace_field: str='_workspace_name', notebook_field: str='_notebook_name', metadata_lakehouse_field: str='_metadata_lakehouse_name', activity_field: str='_activity_id', committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> dict[str, str]`

**What it does:**

Build reusable framework-managed audit fields for metadata-table rows.

**Source:**

- `src/fabricops_kit/metadata.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/metadata.py#L219-L289">View `_build_runtime_audit_fields` on GitHub</a>

**Code:**

```python
def _build_runtime_audit_fields(
    *,
    config: Any = None,
    env: str | None = None,
    timestamp_field: str = "_committed_at",
    user_field: str = "_committed_by",
    workspace_field: str = "_workspace_name",
    notebook_field: str = "_notebook_name",
    metadata_lakehouse_field: str = "_metadata_lakehouse_name",
    activity_field: str = "_activity_id",
    committed_by: str | None = None,
    committed_at: str | None = None,
    runtime_context: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Build reusable framework-managed audit fields for metadata-table rows.

    Parameters
    ----------
    config : FrameworkConfig | dict, optional
        Framework config containing ``path_config.paths[env]["metadata"]``.
    env : str, optional
        Environment key paired with ``config``.
    timestamp_field, user_field, workspace_field, notebook_field : str
        Output keys for timestamp, user, workspace, and notebook audit values.
    metadata_lakehouse_field, activity_field : str
        Output keys for metadata lakehouse and Fabric activity audit values.
    committed_by, committed_at : str, optional
        Deterministic audit overrides. When omitted, values resolve from Fabric
        runtime context and the configured audit timezone timestamp.
    runtime_context : dict[str, Any], optional
        Values merged over :func:`_runtime_context`, primarily for tests or
        controlled notebook overrides.

    Returns
    -------
    dict[str, str]
        Framework-managed metadata audit values keyed by the supplied field
        names.

    Notes
    -----
    DataFrame runtime audit columns and metadata-table audit fields both use
    underscore-prefixed names. This helper centralizes the metadata-table
    convention so notebooks can reuse runtime context when adding dataframe
    audit columns inline.
    """
    context = {**_runtime_context(), **(runtime_context or {})}

    def _first_non_blank(*keys: str) -> Any:
        for key in keys:
            value = _context_get(context, key)
            if value is not None and str(value).strip():
                return value
        return None

    metadata_lakehouse_name = ""
    if config is not None and env is not None:
        paths = config.path_config.paths if hasattr(config, "path_config") else config.paths
        metadata_lakehouse_name = _safe_str(paths[env]["metadata"].name)
    return {
        user_field: _safe_str(committed_by).strip()
        if committed_by and _safe_str(committed_by).strip()
        else _safe_str(_first_non_blank("userName", "userId") or "unknown"),
        timestamp_field: _safe_str(committed_at)
        if committed_at
        else _current_audit_timestamp(config=config),
        workspace_field: _safe_str(_first_non_blank("currentWorkspaceName", "workspaceName") or ""),
        notebook_field: _safe_str(_first_non_blank("currentNotebookName", "notebookName") or ""),
        metadata_lakehouse_field: metadata_lakehouse_name,
        activity_field: _safe_str(_first_non_blank("activityId") or ""),
    }
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_build_runtime_audit_fields`.

### `def _current_audit_timestamp(config: Any=None, timezone_name: str | None=None, *, drop_microseconds: bool=True) -> str`

**What it does:**

Return the current audit timestamp in the configured audit timezone.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/config.py#L69-L75">View `_current_audit_timestamp` on GitHub</a>

**Code:**

```python
def _current_audit_timestamp(config: Any = None, timezone_name: str | None = None, *, drop_microseconds: bool = True) -> str:
    """Return the current audit timestamp in the configured audit timezone."""
    tz_name = _get_audit_timezone(config, timezone_name)
    value = datetime.now(ZoneInfo(tz_name))
    if drop_microseconds:
        value = value.replace(microsecond=0)
    return value.isoformat()
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_current_audit_timestamp`.

### `def _get_audit_timezone(config: Any=None, timezone_name: str | None=None) -> str`

**What it does:**

Resolve the configured FabricOps audit timezone, defaulting to UTC.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/config.py#L61-L66">View `_get_audit_timezone` on GitHub</a>

**Code:**

```python
def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
    """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
    if timezone_name is not None:
        return _validate_audit_timezone(timezone_name)
    value = getattr(config, "audit_timezone", None) if config is not None else None
    return _validate_audit_timezone(value)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_get_audit_timezone`.

### `def _validate_audit_timezone(timezone_name: str | None) -> str`

**What it does:**

Return a valid IANA audit timezone name.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/config.py#L27-L58">View `_validate_audit_timezone` on GitHub</a>

**Code:**

```python
def _validate_audit_timezone(timezone_name: str | None) -> str:
    """Return a valid IANA audit timezone name.

    Parameters
    ----------
    timezone_name : str or None
        IANA timezone name to validate. Blank values default to ``"UTC"``.

    Returns
    -------
    str
        Validated timezone name.

    Raises
    ------
    ValueError
        If a non-blank value is not a valid IANA timezone name.
    """
    value = str(timezone_name or DEFAULT_AUDIT_TIMEZONE).strip() or DEFAULT_AUDIT_TIMEZONE
    if value != DEFAULT_AUDIT_TIMEZONE and "/" not in value:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        )
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        ) from exc
    return value
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_validate_audit_timezone`.

### `def _context_get(context: Any, *keys: str) -> Any`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/metadata.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/metadata.py#L173-L185">View `_context_get` on GitHub</a>

**Code:**

```python
def _context_get(context: Any, *keys: str) -> Any:
    for key in keys:
        try:
            if isinstance(context, dict):
                value = context.get(key)
            else:
                getter = getattr(context, "get", None)
                value = getter(key) if callable(getter) else None
        except Exception:
            value = None
        if value is not None:
            return value
    return None
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_context_get`.

### `def _runtime_context() -> dict[str, Any]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/metadata.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/metadata.py#L192-L216">View `_runtime_context` on GitHub</a>

**Code:**

```python
def _runtime_context() -> dict[str, Any]:
    try:
        import notebookutils  # type: ignore
    except Exception:
        return {}

    runtime = getattr(notebookutils, "runtime", None)
    context = getattr(runtime, "context", None)
    if context is None:
        return {}

    keys = [
        "currentWorkspaceId",
        "currentWorkspaceName",
        "currentNotebookId",
        "currentNotebookName",
        "workspaceId",
        "workspaceName",
        "notebookId",
        "notebookName",
        "userId",
        "userName",
        "activityId",
    ]
    return {key: _context_get(context, key) for key in keys}
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_runtime_context`.

### `def _safe_str(value: Any) -> str`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/metadata.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/metadata.py#L188-L189">View `_safe_str` on GitHub</a>

**Code:**

```python
def _safe_str(value: Any) -> str:
    return "" if value is None else str(value)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_safe_str`.

### `def _create_or_update_data_steward(*, spark: Any, config: Any, env_name: str, values: dict[str, Any], custom_fields: dict[str, Any] | None=None, committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> dict[str, Any]`

**What it does:**

Append a created or updated steward assignment with runtime audit fields.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L585-L635">View `_create_or_update_data_steward` on GitHub</a>

**Code:**

```python
def _create_or_update_data_steward(*, spark: Any, config: Any, env_name: str, values: dict[str, Any], custom_fields: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append a created or updated steward assignment with runtime audit fields.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session.
    config : FrameworkConfig or dict
        Metadata configuration.
    env_name : str
        Configured environment key.
    values : dict[str, Any]
        User-facing steward values. Reusing ``steward_id`` appends an update;
        omitting it creates a backend-generated stable steward identifier.
    custom_fields : dict[str, Any], optional
        Organization-specific configured values.

    Returns
    -------
    dict[str, Any]
        Appended steward row.
    """
    row = {field: values.get(field, "") for field in DATA_STEWARD_VISIBLE_FIELDS}
    required = ["steward_name", "steward_role", "contact"]
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError("Missing required steward field(s): " + ", ".join(missing))
    configured_roles = {
        str(option).strip()
        for option in (_config_value(config, "steward_role_options", DEFAULT_STEWARD_ROLE_OPTIONS) or [])
        if str(option).strip()
    }
    existing_role = str(values.get("_existing_steward_role") or "").strip()
    selected_steward_id = str(values.get("steward_id") or "").strip()
    if str(row["steward_role"]).strip() not in configured_roles and not (selected_steward_id and existing_role and str(row["steward_role"]).strip() == existing_role):
        raise ValueError("steward_role must be one of the configured steward role options.")
    row["effective_from"] = _parse_iso_date(row.get("effective_from"), "effective_from")
    row["effective_to"] = _parse_iso_date(row.get("effective_to"), "effective_to")
    if row["effective_to"] and row["effective_from"] and row["effective_to"] < row["effective_from"]:
        raise ValueError("effective_to must be on or after effective_from.")
    row["steward_id"] = str(values.get("steward_id") or "").strip() or _generate_steward_id(row)
    explicit_active = values.get("is_active")
    if explicit_active not in (None, "") and not _to_bool(explicit_active):
        row["is_active"] = "false"
    else:
        row["is_active"] = "true" if _active_steward({**row, "is_active": row.get("is_active", "")}) else "false"
    row["custom_fields_json"] = _serialize_custom_fields(custom_fields)
    row.update(_build_runtime_audit_fields(config=config, env=env_name, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    _write_row(spark=spark, config=config, env_name=env_name, table=str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), row=row)
    return row
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_create_or_update_data_steward`.

### `def _generate_steward_id(values: dict[str, Any]) -> str`

**What it does:**

Generate a stable public-safe steward identifier from business fields.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L529-L533">View `_generate_steward_id` on GitHub</a>

**Code:**

```python
def _generate_steward_id(values: dict[str, Any]) -> str:
    """Generate a stable public-safe steward identifier from business fields."""
    basis = "|".join(str(values.get(field, "")).strip().lower() for field in ("steward_name", "contact", "effective_from"))
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:10]
    return f"STEW-{digest}"
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_generate_steward_id`.

### `def _get_widget_visible_fields(config: Any, kind: str) -> list[str]`

**What it does:**

Return configured editable columns without backend audit fields.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L156-L177">View `_get_widget_visible_fields` on GitHub</a>

**Code:**

```python
def _get_widget_visible_fields(config: Any, kind: str) -> list[str]:
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
    configured = {**_WIDGET_CONFIG_DEFAULTS[kind], **dict(_config_value(config, kind, {}) or {})}.get("visible_columns", [])
    hidden = set(STANDARD_RUNTIME_AUDIT_COLUMNS) | {"custom_fields_json"}
    if kind == "data_steward_widget":
        hidden.update({"steward_id", "is_active"})
    if kind == "data_agreement_widget":
        hidden.update(DATA_AGREEMENT_GENERATED_FIELDS)
    return [field for field in configured if field not in hidden]
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_get_widget_visible_fields`.

### `def _list_data_agreements(config: Any, env_name: str, *, spark_session: Any=None, active_only: bool=False, missing_ok: bool=False) -> list[dict[str, Any]]`

**What it does:**

List latest versioned agreements from the configured metadata lakehouse.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L684-L691">View `_list_data_agreements` on GitHub</a>

**Code:**

```python
def _list_data_agreements(config: Any, env_name: str, *, spark_session: Any = None, active_only: bool = False, missing_ok: bool = False) -> list[dict[str, Any]]:
    """List latest versioned agreements from the configured metadata lakehouse."""
    rows = _list_all_data_agreement_rows(config, env_name, spark_session=spark_session, missing_ok=missing_ok)
    agreements = _latest_agreement_versions(rows)
    if not active_only:
        return agreements
    today = datetime.now(timezone.utc).date()
    return [row for row in agreements if (not row.get("start_date") or date.fromisoformat(str(row["start_date"])[:10]) <= today) and (not row.get("expiry_date") or date.fromisoformat(str(row["expiry_date"])[:10]) >= today)]
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_list_data_agreements`.

### `def _latest_agreement_versions(rows: Any) -> list[dict[str, Any]]`

**What it does:**

Return the latest semantic version for each stable agreement ID.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L653-L669">View `_latest_agreement_versions` on GitHub</a>

**Code:**

```python
def _latest_agreement_versions(rows: Any) -> list[dict[str, Any]]:
    """Return the latest semantic version for each stable agreement ID."""

    def _agreement_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
        return (
            _parse_contract_version(row.get("contract_version")),
            str(row.get("_committed_at") or row.get("updated_at") or row.get("uploaded_at") or ""),
            str(row.get("agreement_name") or ""),
            str(row.get("agreement_id") or ""),
        )

    latest: dict[str, dict[str, Any]] = {}
    for row in _coerce_row_dicts(rows):
        key = str(row.get("agreement_id") or "").strip()
        if key and (key not in latest or _agreement_sort_key(row) > _agreement_sort_key(latest[key])):
            latest[key] = row
    return sorted(latest.values(), key=lambda row: (str(row.get("agreement_name") or "").lower(), str(row.get("agreement_id") or "")))
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_latest_agreement_versions`.

### `def _render_custom_fields(config: list[dict[str, Any]] | dict[str, Any], *, values: dict[str, Any] | None=None) -> dict[str, Any]`

**What it does:**

Create widgets for configured organization-specific fields.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L310-L359">View `_render_custom_fields` on GitHub</a>

**Code:**

```python
def _render_custom_fields(config: list[dict[str, Any]] | dict[str, Any], *, values: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create widgets for configured organization-specific fields.

    Parameters
    ----------
    config : list[dict[str, Any]] or dict[str, Any]
        Custom-field definitions or a widget config containing ``custom_fields``.
    values : dict[str, Any], optional
        Previously stored values used to prefill update forms.

    Returns
    -------
    dict[str, ipywidgets.Widget]
        Widgets keyed by custom-field key.

    Notes
    -----
    Supported field types are ``text``, ``textarea``, ``select``,
    ``multiselect``, ``date``, and ``boolean``.
    """
    widgets = _require_ipywidgets()

    definitions = config.get("custom_fields", []) if isinstance(config, dict) else config
    current = values or {}
    rendered: dict[str, Any] = {}
    for definition in definitions:
        key = str(definition["key"])
        field_type = str(definition.get("type", "text")).lower()
        label = str(definition.get("label", FIELD_LABELS.get(key, key.replace("_", " ").title())))
        common = _widget_common(widgets, label, textarea=field_type == "textarea")
        value = current.get(key)
        if field_type == "textarea":
            widget = widgets.Textarea(value=str(value or ""), **common)
        elif field_type == "select":
            options = list(definition.get("options", []))
            option_values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
            default_value = value if value in option_values else option_values[0] if option_values else None
            widget = widgets.Dropdown(options=options, value=default_value, **common)
        elif field_type == "multiselect":
            widget = widgets.SelectMultiple(options=list(definition.get("options", [])), value=tuple(value or ()), **common)
        elif field_type == "date":
            widget = widgets.DatePicker(value=date.fromisoformat(str(value)[:10]) if value else None, **common)
        elif field_type == "boolean":
            widget = widgets.Checkbox(value=_to_bool(value), **common)
        elif field_type == "text":
            widget = widgets.Text(value=str(value or ""), **common)
        else:
            raise ValueError(f"Unsupported custom field type: {field_type}")
        rendered[key] = widget
    return rendered
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_render_custom_fields`.

### `def _require_ipywidgets()`

**What it does:**

Return ipywidgets or raise an actionable optional-dependency error.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L63-L72">View `_require_ipywidgets` on GitHub</a>

**Code:**

```python
def _require_ipywidgets():
    """Return ipywidgets or raise an actionable optional-dependency error."""
    try:
        import ipywidgets as widgets
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The data agreement widget feature requires the 'dq-review' extra. "
            'Install with: pip install "fabricops-kit[dq-review]"'
        ) from exc
    return widgets
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_require_ipywidgets`.

### `def _widget_common(widgets_module: Any, description: str, *, textarea: bool=False) -> dict[str, Any]`

**What it does:**

Return common style and layout keyword arguments for form controls.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L180-L189">View `_widget_common` on GitHub</a>

**Code:**

```python
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
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_widget_common`.

### `def _render_searchable_selector(*, widgets: Any, label: str, rows: list[dict[str, Any]], label_fn: Callable[[dict[str, Any]], str], value_fn: Callable[[dict[str, Any]], str], placeholder: str='Search...', max_results: int=25, search_fields: list[str] | None=None, context_fields: list[tuple[str, str]] | None=None, empty_label: str | None=None, selected_value: str | None=None) -> dict[str, Any]`

**What it does:**

Render a table-backed selector with search and stable-value tracking.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L198-L308">View `_render_searchable_selector` on GitHub</a>

**Code:**

```python
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
    """Render a table-backed selector with search and stable-value tracking.

    The visible label may be friendly and long, while the selection value remains
    the stable key produced by ``value_fn``. The returned ``selector`` is the
    select control used by persistence code, and its ``value`` is never replaced
    with the display label.
    """
    search = widgets.Text(value="", placeholder=placeholder, **_widget_common(widgets, f"Search {label}"))
    selector = widgets.Select(options=[], **_widget_common(widgets, label))
    context = widgets.HTML(value="")
    lookup: dict[str, dict[str, Any]] = {}
    indexed_rows: list[dict[str, Any]] = []

    def _set_rows(new_rows: list[dict[str, Any]]) -> None:
        lookup.clear()
        indexed_rows.clear()
        for row in new_rows:
            value = str(value_fn(row) or "").strip()
            if not value:
                continue
            display_label = str(label_fn(row) or value)
            lookup[value] = row
            indexed_rows.append({
                "row": row,
                "label": display_label,
                "value": value,
                "search": " ".join(
                    [display_label, value, *(str(row.get(field) or "") for field in (search_fields or sorted(str(key) for key in row)))]
                ).casefold(),
            })

    def _matching_options(query: str) -> list[tuple[str, str]]:
        needle = str(query or "").casefold().strip()
        matches = [item for item in indexed_rows if not needle or needle in item["search"]]
        return [(item["label"], item["value"]) for item in matches[:max_results]]

    def _render_context(value: Any) -> None:
        row = lookup.get(str(value or ""))
        context.value = "<br>".join(
            f"<b>{_html_escape(field_label)}:</b> {_html_escape(row.get(field, ''))}"
            for field, field_label in context_fields
        ) if row and context_fields else ("<em>No record selected.</em>" if context_fields else "")

    def _apply_filter(preferred_value: Any = None) -> None:
        current = str(preferred_value if preferred_value is not None else selector.value or "")
        options = _matching_options(search.value)
        if empty_label is not None:
            options = [(empty_label, ""), *options]
        selector.options = options
        values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
        if current and current in lookup and current not in values and not str(search.value or "").strip():
            row = lookup[current]
            options = [(str(label_fn(row) or current), current), *options]
            values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
        non_empty_values = [value for value in values if value]
        if current in values and (current or not str(search.value or "").strip()):
            selector.value = current
        elif non_empty_values:
            selector.value = non_empty_values[0]
        elif values:
            selector.value = values[0]
        else:
            selector.value = None
        _render_context(selector.value)

    def _on_search(change: dict[str, Any]) -> None:
        if change.get("name") == "value":
            _apply_filter(selector.value)

    def _on_select(change: dict[str, Any]) -> None:
        if change.get("name") == "value":
            _render_context(change.get("new"))

    def _refresh_rows(new_rows: list[dict[str, Any]], selected: str | None = None) -> None:
        _set_rows(new_rows)
        _apply_filter(selected)

    def _select_value(value: str | None) -> None:
        _apply_filter(str(value or ""))

    search.observe(_on_search, names="value")
    selector.observe(_on_select, names="value")
    _refresh_rows(rows, selected_value)
    container = widgets.VBox([search, selector, context])
    selector.search_box = search
    selector.context_html = context
    selector.refresh_rows = _refresh_rows
    selector.select_value = _select_value
    selector.rows_by_value = lookup
    return {
        "container": container,
        "search": search,
        "selector": selector,
        "context": context,
        "rows_by_value": lookup,
        "refresh_rows": _refresh_rows,
    }
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_render_searchable_selector`.

### `def _html_escape(value: Any) -> str`

**What it does:**

Return display-safe HTML text for notebook context snippets.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L192-L195">View `_html_escape` on GitHub</a>

**Code:**

```python
def _html_escape(value: Any) -> str:
    """Return display-safe HTML text for notebook context snippets."""
    import html
    return html.escape(str(value or ""))
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_html_escape`.

### `def _standard_widget(field: str, value: Any='', *, options: list[Any] | None=None) -> Any`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L1101-L1114">View `_standard_widget` on GitHub</a>

**Code:**

```python
def _standard_widget(field: str, value: Any = "", *, options: list[Any] | None = None) -> Any:
    widgets = _require_ipywidgets()
    description = FIELD_LABELS.get(field, field.replace("_", " ").title())
    if options is not None:
        option_values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
        default_value = value if value in option_values else option_values[0] if option_values else None
        return widgets.Dropdown(options=options, value=default_value, **_widget_common(widgets, description))
    if field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
        return widgets.DatePicker(value=date.fromisoformat(str(value)[:10]) if value else None, **_widget_common(widgets, description))
    if field == "is_active":
        return widgets.Checkbox(value=True if value == "" else _to_bool(value), **_widget_common(widgets, description))
    if field in {"business_purpose", "approved_usage_internal", "approved_usage_external", "approved_usage_research"}:
        return widgets.Textarea(value=str(value or ""), **_widget_common(widgets, description, textarea=True))
    return widgets.Text(value=str(value or ""), **_widget_common(widgets, description))
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_standard_widget`.


</details>

## Source

- Source file path: `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L1518-L1535">View widget_render_data_agreement on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

```python
def widget_render_data_agreement(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]:
    """Render append-only agreement create/update maintenance using active stewards.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Configuration containing agreement widget fields and metadata routing.
    env_name : str
        Environment key configured by ``00_env_config``.
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for metadata reads and append-only writes.

    Returns
    -------
    dict[str, Any]
        Rendered controls, including read-only generated-identifier context.
    """
    return _render_maintenance_widget(spark=spark, config=config, env_name=env_name, kind="data_agreement_widget")
```

</details>

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.widget_render_data_agreement`
- Short name: `widget_render_data_agreement`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `1518`
- Inbound references count: 0
- Outbound references count: 1

### AI implementation contract

- **required_context:** Starter template: `01_agreement`; segment: `Agreement intake`.
- **inputs:** config : FrameworkConfig or dict
    Configuration containing agreement widget fields and metadata routing.
env_name : str
    Environment key configured by ``00_env_config``.
spark : pyspark.sql.SparkSession
    Fabric Spark session used for metadata reads and append-only writes.
- **output:** dict[str, Any]
    Rendered controls, including read-only generated-identifier context.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.data_agreement._render_maintenance_widget`

### Raw source metadata

- Source file path: `src/fabricops_kit/data_agreement.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L1518-L1535">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L1518-L1535</a>
- Start line: `1518`
- End line: `1535`
- Signature:

```python
def widget_render_data_agreement(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation helpers

### Call flow

```text
widget_render_data_agreement(...)
└── _render_maintenance_widget(...)
    ├── _agreement_identity_text(...)
    │   └── _next_minor_version(...)
    │       └── _parse_contract_version(...)
    ├── _collect_custom_fields(...)
    │   └── _to_iso_date(...)
    ├── _config_value(...)
    ├── _create_or_update_data_agreement(...)
    │   ├── _build_runtime_audit_fields(...)
    │   │   ├── _context_get(...)
    │   │   ├── _current_audit_timestamp(...)
    │   │   │   └── _get_audit_timezone(...)
    │   │   │       └── _validate_audit_timezone(...)
    │   │   ├── _runtime_context(...)
    │   │   │   └── _context_get(...)
    │   │   └── _safe_str(...)
    │   ├── _business_agreement_snapshot(...)
    │   │   ├── _deserialize_custom_fields(...)
    │   │   └── _serialize_custom_fields(...)
    │   ├── _config_value(...)
    │   ├── _generate_agreement_id(...)
    │   ├── _list_all_data_agreement_rows(...)
    │   │   ├── _coerce_row_dicts(...)
    │   │   ├── _config_value(...)
    │   │   └── read_lakehouse_table(...)
    │   │       ├── _current_database_matches(...)
    │   │       ├── _get_spark(...)
    │   │       ├── _get_store(...)
    │   │       ├── _normalize_table_name(...)
    │   │       ├── _registered_table_identifier(...)
    │   │       │   ├── _normalize_table_name(...)
    │   │       │   └── _quote_identifier(...)
    │   │       └── _uses_registered_metadata_table(...)
    │   ├── _list_data_stewards(...)
    │   │   ├── _active_steward(...)
    │   │   │   └── _to_bool(...)
    │   │   ├── _config_value(...)
    │   │   ├── _latest_by_key(...)
    │   │   │   └── _coerce_row_dicts(...)
    │   │   └── read_lakehouse_table(...)
    │   │       ├── _current_database_matches(...)
    │   │       ├── _get_spark(...)
    │   │       ├── _get_store(...)
    │   │       ├── _normalize_table_name(...)
    │   │       ├── _registered_table_identifier(...)
    │   │       │   ├── _normalize_table_name(...)
    │   │       │   └── _quote_identifier(...)
    │   │       └── _uses_registered_metadata_table(...)
    │   ├── _next_minor_version(...)
    │   │   └── _parse_contract_version(...)
    │   ├── _parse_contract_version(...)
    │   ├── _parse_iso_date(...)
    │   ├── _serialize_custom_fields(...)
    │   └── _write_row(...)
    │       └── write_lakehouse_table(...)
    │           ├── _get_store(...)
    │           ├── _normalize_table_name(...)
    │           ├── _registered_table_identifier(...)
    │           │   ├── _normalize_table_name(...)
    │           │   └── _quote_identifier(...)
    │           └── _uses_registered_metadata_table(...)
    ├── _create_or_update_data_steward(...)
    │   ├── _active_steward(...)
    │   │   └── _to_bool(...)
    │   ├── _build_runtime_audit_fields(...)
    │   │   ├── _context_get(...)
    │   │   ├── _current_audit_timestamp(...)
    │   │   │   └── _get_audit_timezone(...)
    │   │   │       └── _validate_audit_timezone(...)
    │   │   ├── _runtime_context(...)
    │   │   │   └── _context_get(...)
    │   │   └── _safe_str(...)
    │   ├── _config_value(...)
    │   ├── _generate_steward_id(...)
    │   ├── _parse_iso_date(...)
    │   ├── _serialize_custom_fields(...)
    │   ├── _to_bool(...)
    │   └── _write_row(...)
    │       └── write_lakehouse_table(...)
    │           ├── _get_store(...)
    │           ├── _normalize_table_name(...)
    │           ├── _registered_table_identifier(...)
    │           │   ├── _normalize_table_name(...)
    │           │   └── _quote_identifier(...)
    │           └── _uses_registered_metadata_table(...)
    ├── _deserialize_custom_fields(...)
    ├── _get_widget_visible_fields(...)
    │   └── _config_value(...)
    ├── _list_data_agreements(...)
    │   ├── _latest_agreement_versions(...)
    │   │   ├── _coerce_row_dicts(...)
    │   │   └── _parse_contract_version(...)
    │   └── _list_all_data_agreement_rows(...)
    │       ├── _coerce_row_dicts(...)
    │       ├── _config_value(...)
    │       └── read_lakehouse_table(...)
    │           ├── _current_database_matches(...)
    │           ├── _get_spark(...)
    │           ├── _get_store(...)
    │           ├── _normalize_table_name(...)
    │           ├── _registered_table_identifier(...)
    │           │   ├── _normalize_table_name(...)
    │           │   └── _quote_identifier(...)
    │           └── _uses_registered_metadata_table(...)
    ├── _list_data_stewards(...)
    │   ├── _active_steward(...)
    │   │   └── _to_bool(...)
    │   ├── _config_value(...)
    │   ├── _latest_by_key(...)
    │   │   └── _coerce_row_dicts(...)
    │   └── read_lakehouse_table(...)
    │       ├── _current_database_matches(...)
    │       ├── _get_spark(...)
    │       ├── _get_store(...)
    │       ├── _normalize_table_name(...)
    │       ├── _registered_table_identifier(...)
    │       │   ├── _normalize_table_name(...)
    │       │   └── _quote_identifier(...)
    │       └── _uses_registered_metadata_table(...)
    ├── _render_custom_fields(...)
    │   ├── _require_ipywidgets(...)
    │   ├── _to_bool(...)
    │   └── _widget_common(...)
    ├── _render_searchable_selector(...)
    │   ├── _html_escape(...)
    │   └── _widget_common(...)
    ├── _require_ipywidgets(...)
    ├── _standard_widget(...)
    │   ├── _require_ipywidgets(...)
    │   ├── _to_bool(...)
    │   └── _widget_common(...)
    ├── _to_bool(...)
    └── _to_iso_date(...)
```

### Internal helpers used by this callable

### `def _render_maintenance_widget(*, spark: Any, config: Any, env_name: str, kind: str, display_widget: bool=True) -> dict[str, Any]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L1130-L1338">View `_render_maintenance_widget` on GitHub</a>

**Code:**

```python
def _render_maintenance_widget(*, spark: Any, config: Any, env_name: str, kind: str, display_widget: bool = True) -> dict[str, Any]:
    widgets = _require_ipywidgets()
    from IPython import display as ip

    is_steward = kind == "data_steward_widget"
    prompt = "Create new steward" if is_steward else "Create new agreement"
    widget_config = {**_WIDGET_CONFIG_DEFAULTS[kind], **dict(_config_value(config, kind, {}) or {})}
    fields = _get_widget_visible_fields(config, kind)
    after_save_callbacks: list[Any] = []
    row_lookup: dict[str, dict[str, Any]] = {}

    def _row_id(row: dict[str, Any]) -> str:
        return str(row.get("steward_id" if is_steward else "agreement_id") or "").strip()

    def _existing_rows() -> list[dict[str, Any]]:
        return _list_data_stewards(config, env_name, spark_session=spark, active_only=False, missing_ok=True) if is_steward else _list_data_agreements(config, env_name, spark_session=spark, missing_ok=True)

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
    identity_context = None if is_steward else widgets.HTML(value=_agreement_identity_text(None))

    roles = [str(option).strip() for option in (_config_value(config, "steward_role_options", DEFAULT_STEWARD_ROLE_OPTIONS) or []) if str(option).strip()]
    steward_role_options = [(role, role) for role in roles] if is_steward else None
    form = {}
    steward_field_selector = None
    for field in fields:
        if field == "steward_id" and not is_steward:
            steward_rows = _list_data_stewards(config, env_name, spark_session=spark, active_only=True, missing_ok=True)
            steward_field_selector = _render_searchable_selector(
                widgets=widgets,
                label=FIELD_LABELS.get(field, field.replace("_", " ").title()),
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
            rows = _list_data_stewards(config, env_name, spark_session=spark, active_only=True, missing_ok=True)
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
            widget.value = _to_bool(value)
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
        stored = _deserialize_custom_fields(row.get("custom_fields_json", ""))
        for key, widget in custom.items():
            _apply_widget_value(widget, stored.get(key, widget.value))
        if identity_context is not None:
            identity_context.value = _agreement_identity_text(row if row else None)

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
                    key: _to_iso_date(widget.value) if key in {"effective_from", "effective_to", "start_date", "expiry_date"} else widget.value
                    for key, widget in form.items()
                }
                extras = _collect_custom_fields(widget_config, custom)
                if is_steward:
                    if selected.value:
                        values["steward_id"] = selected.value
                        values["_existing_steward_role"] = row_lookup.get(selected.value, {}).get("steward_role", "")
                    row = _create_or_update_data_steward(spark=spark, config=config, env_name=env_name, values=values, custom_fields=extras)
                    _refresh_existing_options(row["steward_id"])
                    for callback in after_save_callbacks:
                        callback(row)
                    print(f"Saved data steward: {row.get('steward_name', '')} ({row['steward_id']})")
                else:
                    selected_row = row_lookup.get(selected.value) if selected.value else None
                    row = _create_or_update_data_agreement(spark=spark, config=config, env_name=env_name, values=values, selected_agreement=selected_row, custom_fields=extras)
                    if row.get("_fabricops_no_change"):
                        print(row.get("_fabricops_message", "No changes detected. Nothing was appended."))
                    else:
                        print(f"Saved data agreement: {row.get('agreement_name', '')} ({row['agreement_id']} v{row['contract_version']})")
                    _refresh_existing_options(row["agreement_id"])
                    if not row.get("_fabricops_no_change"):
                        for callback in after_save_callbacks:
                            callback(row)
                    if identity_context is not None:
                        identity_context.value = _agreement_identity_text(row)
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
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_render_maintenance_widget`.

### `def _agreement_identity_text(row: dict[str, Any] | None) -> str`

**What it does:**

Return read-only agreement version context for the notebook form.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L1117-L1127">View `_agreement_identity_text` on GitHub</a>

**Code:**

```python
def _agreement_identity_text(row: dict[str, Any] | None) -> str:
    """Return read-only agreement version context for the notebook form."""
    if not row:
        return "Agreement ID and version are generated when saved."
    current_version = str(row.get("contract_version") or "")
    return (
        f"Agreement ID: {row.get('agreement_id', '')}<br>"
        f"Current version: {current_version}<br>"
        f"Next version on save: {_next_minor_version(current_version)}<br>"
        "Saving this change will append a new version. Existing rows will not be overwritten."
    )
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_agreement_identity_text`.

### `def _next_minor_version(version: Any) -> str`

**What it does:**

Return the next minor contract version, defaulting to ``1.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L647-L650">View `_next_minor_version` on GitHub</a>

**Code:**

```python
def _next_minor_version(version: Any) -> str:
    """Return the next minor contract version, defaulting to ``1.0.0``."""
    major, minor, _ = _parse_contract_version(version)
    return "1.0.0" if major == 0 else f"{major}.{minor + 1}.0"
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_next_minor_version`.

### `def _parse_contract_version(version: Any) -> tuple[int, int, int]`

**What it does:**

Parse a semantic contract version into a comparable tuple.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L638-L644">View `_parse_contract_version` on GitHub</a>

**Code:**

```python
def _parse_contract_version(version: Any) -> tuple[int, int, int]:
    """Parse a semantic contract version into a comparable tuple."""
    try:
        parts = str(version or "").strip().split(".")
        return tuple(int(parts[index]) if index < len(parts) else 0 for index in range(3))  # type: ignore[return-value]
    except (TypeError, ValueError):
        return (0, 0, 0)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_parse_contract_version`.

### `def _collect_custom_fields(config: list[dict[str, Any]] | dict[str, Any], widgets_by_key: dict[str, Any]) -> dict[str, Any]`

**What it does:**

Collect and validate configured custom-field widget values.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L362-L394">View `_collect_custom_fields` on GitHub</a>

**Code:**

```python
def _collect_custom_fields(config: list[dict[str, Any]] | dict[str, Any], widgets_by_key: dict[str, Any]) -> dict[str, Any]:
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
            value = _to_iso_date(value)
        if definition.get("required") and value in (None, "", []):
            raise ValueError(f"{definition.get('label', key)} is required.")
        values[key] = value
    return values
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_collect_custom_fields`.

### `def _to_iso_date(value: Any) -> str`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L698-L701">View `_to_iso_date` on GitHub</a>

**Code:**

```python
def _to_iso_date(value: Any) -> str:
    if value is None:
        return ""
    return value.date().isoformat() if isinstance(value, datetime) else value.isoformat() if isinstance(value, date) else str(value)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_to_iso_date`.

### `def _config_value(config: Any, name: str, default: Any) -> Any`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L149-L153">View `_config_value` on GitHub</a>

**Code:**

```python
def _config_value(config: Any, name: str, default: Any) -> Any:
    agreement_config = getattr(config, "data_agreement_config", config)
    if isinstance(agreement_config, dict):
        return agreement_config.get(name, default)
    return getattr(agreement_config, name, default)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_config_value`.

### `def _create_or_update_data_agreement(*, spark: Any, config: Any, env_name: str, values: dict[str, Any], selected_agreement: dict[str, Any] | None=None, custom_fields: dict[str, Any] | None=None, committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> dict[str, Any]`

**What it does:**

Append a new agreement or a new semantic version of an existing one.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L711-L755">View `_create_or_update_data_agreement` on GitHub</a>

**Code:**

```python
def _create_or_update_data_agreement(*, spark: Any, config: Any, env_name: str, values: dict[str, Any], selected_agreement: dict[str, Any] | None = None, custom_fields: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append a new agreement or a new semantic version of an existing one.

    Reusing ``selected_agreement`` preserves its stable ``agreement_id`` and
    increments from the latest stored version. Runtime audit fields remain
    backend-managed.
    """
    row = {field: values.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS}
    existing_rows = _list_all_data_agreement_rows(config, env_name, spark_session=spark, missing_ok=True)
    selected_id = str((selected_agreement or {}).get("agreement_id") or "").strip()
    if selected_id:
        same_agreement = [item for item in existing_rows if str(item.get("agreement_id") or "").strip() == selected_id]
        latest = max(same_agreement, key=lambda item: _parse_contract_version(item.get("contract_version")), default=selected_agreement)
        row["agreement_id"] = selected_id
        row["contract_version"] = _next_minor_version(latest.get("contract_version"))
    else:
        latest = None
        row["agreement_id"] = str(row.get("agreement_id") or "").strip() or _generate_agreement_id()
        row["contract_version"] = str(row.get("contract_version") or "1.0.0").strip()
    required = ["agreement_id", "contract_version", "agreement_name", "domain", "steward_id", "recipient", "start_date", "expiry_date", "business_purpose"]
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError("Missing required agreement field(s): " + ", ".join(missing))
    usage_fields = ["approved_usage_internal", "approved_usage_external", "approved_usage_research"]
    if not any(str(row.get(field) or "").strip() for field in usage_fields):
        raise ValueError("At least one approved usage field is required: internal, external, or research.")
    row["start_date"] = _parse_iso_date(row.get("start_date"), "start_date", required=True)
    row["expiry_date"] = _parse_iso_date(row.get("expiry_date"), "expiry_date", required=True)
    if row["expiry_date"] < row["start_date"]:
        raise ValueError("expiry_date must be on or after start_date.")
    active_steward_ids = {str(item["steward_id"]) for item in _list_data_stewards(config, env_name, spark_session=spark, active_only=True)}
    if str(row["steward_id"]) not in active_steward_ids:
        raise ValueError("steward_id must reference an active data steward.")
    row["custom_fields_json"] = _serialize_custom_fields(custom_fields)
    if latest is not None:
        new_snapshot = _business_agreement_snapshot(row)
        latest_snapshot = _business_agreement_snapshot(latest)
        if new_snapshot == latest_snapshot:
            return {**latest, "_fabricops_no_change": True, "_fabricops_message": "No changes detected. Nothing was appended."}
    if any(str(item.get("agreement_id") or "").strip() == row["agreement_id"] and str(item.get("contract_version") or "").strip() == row["contract_version"] for item in existing_rows):
        raise ValueError(f"Agreement {row['agreement_id']} version {row['contract_version']} already exists. Select the existing agreement to create the next version, or create a new agreement.")
    row.update(_build_runtime_audit_fields(config=config, env=env_name, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    _write_row(spark=spark, config=config, env_name=env_name, table=str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), row=row)
    return row
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_create_or_update_data_agreement`.

### `def _business_agreement_snapshot(row: dict[str, Any]) -> dict[str, Any]`

**What it does:**

Return user-facing agreement values used to detect business changes.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L704-L708">View `_business_agreement_snapshot` on GitHub</a>

**Code:**

```python
def _business_agreement_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    """Return user-facing agreement values used to detect business changes."""
    snapshot = {field: row.get(field, "") for field in DATA_AGREEMENT_VISIBLE_FIELDS}
    snapshot["custom_fields_json"] = _serialize_custom_fields(_deserialize_custom_fields(row.get("custom_fields_json", "")))
    return snapshot
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_business_agreement_snapshot`.

### `def _deserialize_custom_fields(custom_fields_json: Any) -> dict[str, Any]`

**What it does:**

Deserialize stored custom-field JSON for widget display.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L118-L146">View `_deserialize_custom_fields` on GitHub</a>

**Code:**

```python
def _deserialize_custom_fields(custom_fields_json: Any) -> dict[str, Any]:
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
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_deserialize_custom_fields`.

### `def _serialize_custom_fields(values: dict[str, Any] | None) -> str`

**What it does:**

Serialize organization-specific intake values to deterministic JSON.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L102-L115">View `_serialize_custom_fields` on GitHub</a>

**Code:**

```python
def _serialize_custom_fields(values: dict[str, Any] | None) -> str:
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
    return json.dumps(values or {}, sort_keys=True, default=_to_iso_date)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_serialize_custom_fields`.

### `def _generate_agreement_id() -> str`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L694-L695">View `_generate_agreement_id` on GitHub</a>

**Code:**

```python
def _generate_agreement_id() -> str:
    return "DA-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_generate_agreement_id`.

### `def _list_all_data_agreement_rows(config: Any, env_name: str, *, spark_session: Any=None, missing_ok: bool=False) -> list[dict[str, Any]]`

**What it does:**

List all append-only agreement rows from the metadata lakehouse.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L672-L681">View `_list_all_data_agreement_rows` on GitHub</a>

**Code:**

```python
def _list_all_data_agreement_rows(config: Any, env_name: str, *, spark_session: Any = None, missing_ok: bool = False) -> list[dict[str, Any]]:
    """List all append-only agreement rows from the metadata lakehouse."""
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    try:
        rows = read_lakehouse_table(config, env_name, "metadata", str(metadata_tables.get("data_agreement", DATA_AGREEMENT_TABLE)), spark_session=spark_session)
    except Exception:
        if missing_ok:
            return []
        raise
    return _coerce_row_dicts(rows)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_list_all_data_agreement_rows`.

### `def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L397-L402">View `_coerce_row_dicts` on GitHub</a>

**Code:**

```python
def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
    if rows is None:
        return []
    if hasattr(rows, "collect"):
        rows = rows.collect()
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_coerce_row_dicts`.

### `def _list_data_stewards(config: Any, env_name: str, *, spark_session: Any=None, active_only: bool=True, missing_ok: bool=False) -> list[dict[str, Any]]`

**What it does:**

List latest append-only steward rows from the metadata lakehouse.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L536-L565">View `_list_data_stewards` on GitHub</a>

**Code:**

```python
def _list_data_stewards(config: Any, env_name: str, *, spark_session: Any = None, active_only: bool = True, missing_ok: bool = False) -> list[dict[str, Any]]:
    """List latest append-only steward rows from the metadata lakehouse.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Metadata lakehouse configuration.
    env_name : str
        Configured environment key.
    spark_session : pyspark.sql.SparkSession, optional
        Fabric Spark session.
    active_only : bool, default=True
        Return only currently effective active steward assignments.
    missing_ok : bool, default=False
        Return an empty list when the table is not available.

    Returns
    -------
    list[dict[str, Any]]
        Latest steward rows sorted by stable ID.
    """
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    try:
        rows = read_lakehouse_table(config, env_name, "metadata", str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), spark_session=spark_session)
    except Exception:
        if missing_ok:
            return []
        raise
    latest = _latest_by_key(rows, "steward_id")
    return [row for row in latest if _active_steward(row)] if active_only else latest
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_list_data_stewards`.

### `def _active_steward(row: dict[str, Any]) -> bool`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L516-L526">View `_active_steward` on GitHub</a>

**Code:**

```python
def _active_steward(row: dict[str, Any]) -> bool:
    is_active = row.get("is_active")
    if is_active not in (None, "") and not _to_bool(is_active):
        return False
    today = datetime.now(timezone.utc).date()
    try:
        starts_before_today = not row.get("effective_from") or date.fromisoformat(str(row["effective_from"])[:10]) <= today
        ends_after_today = not row.get("effective_to") or date.fromisoformat(str(row["effective_to"])[:10]) >= today
        return starts_before_today and ends_after_today
    except ValueError as exc:
        raise ValueError(f"{DATA_STEWARD_TABLE} row '{row.get('steward_id', '')}' has an invalid effective date. Use ISO dates.") from exc
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_active_steward`.

### `def _to_bool(value: Any) -> bool`

**What it does:**

Normalize common notebook and metadata boolean representations.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L497-L513">View `_to_bool` on GitHub</a>

**Code:**

```python
def _to_bool(value: Any) -> bool:
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
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_to_bool`.

### `def _latest_by_key(rows: Any, key: str) -> list[dict[str, Any]]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L488-L494">View `_latest_by_key` on GitHub</a>

**Code:**

```python
def _latest_by_key(rows: Any, key: str) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in _coerce_row_dicts(rows):
        value = str(row.get(key) or "").strip()
        if value and (value not in latest or str(row.get("_committed_at") or "") >= str(latest[value].get("_committed_at") or "")):
            latest[value] = row
    return sorted(latest.values(), key=lambda row: str(row.get(key) or "").lower())
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_latest_by_key`.

### `def _parse_iso_date(value: Any, field_name: str, *, required: bool=False) -> str`

**What it does:**

Return an ISO date string or raise a clear intake validation error.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L572-L582">View `_parse_iso_date` on GitHub</a>

**Code:**

```python
def _parse_iso_date(value: Any, field_name: str, *, required: bool = False) -> str:
    """Return an ISO date string or raise a clear intake validation error."""
    text = str(value or "").strip()
    if not text:
        if required:
            raise ValueError(f"{field_name} is required.")
        return ""
    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError as exc:
        raise ValueError(f"{field_name} must be a valid ISO date (YYYY-MM-DD).") from exc
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_parse_iso_date`.

### `def _write_row(*, spark: Any, config: Any, env_name: str, table: str, row: dict[str, Any]) -> None`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L568-L569">View `_write_row` on GitHub</a>

**Code:**

```python
def _write_row(*, spark: Any, config: Any, env_name: str, table: str, row: dict[str, Any]) -> None:
    write_lakehouse_table(spark.createDataFrame([row]), config, env_name, "metadata", table, mode="append")
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_write_row`.

### `def _build_runtime_audit_fields(*, config: Any=None, env: str | None=None, timestamp_field: str='_committed_at', user_field: str='_committed_by', workspace_field: str='_workspace_name', notebook_field: str='_notebook_name', metadata_lakehouse_field: str='_metadata_lakehouse_name', activity_field: str='_activity_id', committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> dict[str, str]`

**What it does:**

Build reusable framework-managed audit fields for metadata-table rows.

**Source:**

- `src/fabricops_kit/metadata.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/metadata.py#L219-L289">View `_build_runtime_audit_fields` on GitHub</a>

**Code:**

```python
def _build_runtime_audit_fields(
    *,
    config: Any = None,
    env: str | None = None,
    timestamp_field: str = "_committed_at",
    user_field: str = "_committed_by",
    workspace_field: str = "_workspace_name",
    notebook_field: str = "_notebook_name",
    metadata_lakehouse_field: str = "_metadata_lakehouse_name",
    activity_field: str = "_activity_id",
    committed_by: str | None = None,
    committed_at: str | None = None,
    runtime_context: dict[str, Any] | None = None,
) -> dict[str, str]:
    """Build reusable framework-managed audit fields for metadata-table rows.

    Parameters
    ----------
    config : FrameworkConfig | dict, optional
        Framework config containing ``path_config.paths[env]["metadata"]``.
    env : str, optional
        Environment key paired with ``config``.
    timestamp_field, user_field, workspace_field, notebook_field : str
        Output keys for timestamp, user, workspace, and notebook audit values.
    metadata_lakehouse_field, activity_field : str
        Output keys for metadata lakehouse and Fabric activity audit values.
    committed_by, committed_at : str, optional
        Deterministic audit overrides. When omitted, values resolve from Fabric
        runtime context and the configured audit timezone timestamp.
    runtime_context : dict[str, Any], optional
        Values merged over :func:`_runtime_context`, primarily for tests or
        controlled notebook overrides.

    Returns
    -------
    dict[str, str]
        Framework-managed metadata audit values keyed by the supplied field
        names.

    Notes
    -----
    DataFrame runtime audit columns and metadata-table audit fields both use
    underscore-prefixed names. This helper centralizes the metadata-table
    convention so notebooks can reuse runtime context when adding dataframe
    audit columns inline.
    """
    context = {**_runtime_context(), **(runtime_context or {})}

    def _first_non_blank(*keys: str) -> Any:
        for key in keys:
            value = _context_get(context, key)
            if value is not None and str(value).strip():
                return value
        return None

    metadata_lakehouse_name = ""
    if config is not None and env is not None:
        paths = config.path_config.paths if hasattr(config, "path_config") else config.paths
        metadata_lakehouse_name = _safe_str(paths[env]["metadata"].name)
    return {
        user_field: _safe_str(committed_by).strip()
        if committed_by and _safe_str(committed_by).strip()
        else _safe_str(_first_non_blank("userName", "userId") or "unknown"),
        timestamp_field: _safe_str(committed_at)
        if committed_at
        else _current_audit_timestamp(config=config),
        workspace_field: _safe_str(_first_non_blank("currentWorkspaceName", "workspaceName") or ""),
        notebook_field: _safe_str(_first_non_blank("currentNotebookName", "notebookName") or ""),
        metadata_lakehouse_field: metadata_lakehouse_name,
        activity_field: _safe_str(_first_non_blank("activityId") or ""),
    }
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_build_runtime_audit_fields`.

### `def _current_audit_timestamp(config: Any=None, timezone_name: str | None=None, *, drop_microseconds: bool=True) -> str`

**What it does:**

Return the current audit timestamp in the configured audit timezone.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/config.py#L69-L75">View `_current_audit_timestamp` on GitHub</a>

**Code:**

```python
def _current_audit_timestamp(config: Any = None, timezone_name: str | None = None, *, drop_microseconds: bool = True) -> str:
    """Return the current audit timestamp in the configured audit timezone."""
    tz_name = _get_audit_timezone(config, timezone_name)
    value = datetime.now(ZoneInfo(tz_name))
    if drop_microseconds:
        value = value.replace(microsecond=0)
    return value.isoformat()
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_current_audit_timestamp`.

### `def _get_audit_timezone(config: Any=None, timezone_name: str | None=None) -> str`

**What it does:**

Resolve the configured FabricOps audit timezone, defaulting to UTC.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/config.py#L61-L66">View `_get_audit_timezone` on GitHub</a>

**Code:**

```python
def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
    """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
    if timezone_name is not None:
        return _validate_audit_timezone(timezone_name)
    value = getattr(config, "audit_timezone", None) if config is not None else None
    return _validate_audit_timezone(value)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_get_audit_timezone`.

### `def _validate_audit_timezone(timezone_name: str | None) -> str`

**What it does:**

Return a valid IANA audit timezone name.

**Source:**

- `src/fabricops_kit/config.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/config.py#L27-L58">View `_validate_audit_timezone` on GitHub</a>

**Code:**

```python
def _validate_audit_timezone(timezone_name: str | None) -> str:
    """Return a valid IANA audit timezone name.

    Parameters
    ----------
    timezone_name : str or None
        IANA timezone name to validate. Blank values default to ``"UTC"``.

    Returns
    -------
    str
        Validated timezone name.

    Raises
    ------
    ValueError
        If a non-blank value is not a valid IANA timezone name.
    """
    value = str(timezone_name or DEFAULT_AUDIT_TIMEZONE).strip() or DEFAULT_AUDIT_TIMEZONE
    if value != DEFAULT_AUDIT_TIMEZONE and "/" not in value:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        )
    try:
        ZoneInfo(value)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(
            f'Invalid FABRICOPS_AUDIT_TIMEZONE: "{value}". '
            'Use a valid IANA timezone name such as "Asia/Singapore" or keep the default "UTC".'
        ) from exc
    return value
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_validate_audit_timezone`.

### `def _context_get(context: Any, *keys: str) -> Any`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/metadata.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/metadata.py#L173-L185">View `_context_get` on GitHub</a>

**Code:**

```python
def _context_get(context: Any, *keys: str) -> Any:
    for key in keys:
        try:
            if isinstance(context, dict):
                value = context.get(key)
            else:
                getter = getattr(context, "get", None)
                value = getter(key) if callable(getter) else None
        except Exception:
            value = None
        if value is not None:
            return value
    return None
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_context_get`.

### `def _runtime_context() -> dict[str, Any]`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/metadata.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/metadata.py#L192-L216">View `_runtime_context` on GitHub</a>

**Code:**

```python
def _runtime_context() -> dict[str, Any]:
    try:
        import notebookutils  # type: ignore
    except Exception:
        return {}

    runtime = getattr(notebookutils, "runtime", None)
    context = getattr(runtime, "context", None)
    if context is None:
        return {}

    keys = [
        "currentWorkspaceId",
        "currentWorkspaceName",
        "currentNotebookId",
        "currentNotebookName",
        "workspaceId",
        "workspaceName",
        "notebookId",
        "notebookName",
        "userId",
        "userName",
        "activityId",
    ]
    return {key: _context_get(context, key) for key in keys}
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_runtime_context`.

### `def _safe_str(value: Any) -> str`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/metadata.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/metadata.py#L188-L189">View `_safe_str` on GitHub</a>

**Code:**

```python
def _safe_str(value: Any) -> str:
    return "" if value is None else str(value)
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_safe_str`.

### `def _create_or_update_data_steward(*, spark: Any, config: Any, env_name: str, values: dict[str, Any], custom_fields: dict[str, Any] | None=None, committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> dict[str, Any]`

**What it does:**

Append a created or updated steward assignment with runtime audit fields.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L585-L635">View `_create_or_update_data_steward` on GitHub</a>

**Code:**

```python
def _create_or_update_data_steward(*, spark: Any, config: Any, env_name: str, values: dict[str, Any], custom_fields: dict[str, Any] | None = None, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append a created or updated steward assignment with runtime audit fields.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Fabric Spark session.
    config : FrameworkConfig or dict
        Metadata configuration.
    env_name : str
        Configured environment key.
    values : dict[str, Any]
        User-facing steward values. Reusing ``steward_id`` appends an update;
        omitting it creates a backend-generated stable steward identifier.
    custom_fields : dict[str, Any], optional
        Organization-specific configured values.

    Returns
    -------
    dict[str, Any]
        Appended steward row.
    """
    row = {field: values.get(field, "") for field in DATA_STEWARD_VISIBLE_FIELDS}
    required = ["steward_name", "steward_role", "contact"]
    missing = [field for field in required if not str(row.get(field) or "").strip()]
    if missing:
        raise ValueError("Missing required steward field(s): " + ", ".join(missing))
    configured_roles = {
        str(option).strip()
        for option in (_config_value(config, "steward_role_options", DEFAULT_STEWARD_ROLE_OPTIONS) or [])
        if str(option).strip()
    }
    existing_role = str(values.get("_existing_steward_role") or "").strip()
    selected_steward_id = str(values.get("steward_id") or "").strip()
    if str(row["steward_role"]).strip() not in configured_roles and not (selected_steward_id and existing_role and str(row["steward_role"]).strip() == existing_role):
        raise ValueError("steward_role must be one of the configured steward role options.")
    row["effective_from"] = _parse_iso_date(row.get("effective_from"), "effective_from")
    row["effective_to"] = _parse_iso_date(row.get("effective_to"), "effective_to")
    if row["effective_to"] and row["effective_from"] and row["effective_to"] < row["effective_from"]:
        raise ValueError("effective_to must be on or after effective_from.")
    row["steward_id"] = str(values.get("steward_id") or "").strip() or _generate_steward_id(row)
    explicit_active = values.get("is_active")
    if explicit_active not in (None, "") and not _to_bool(explicit_active):
        row["is_active"] = "false"
    else:
        row["is_active"] = "true" if _active_steward({**row, "is_active": row.get("is_active", "")}) else "false"
    row["custom_fields_json"] = _serialize_custom_fields(custom_fields)
    row.update(_build_runtime_audit_fields(config=config, env=env_name, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context))
    metadata_tables = _config_value(config, "metadata_tables", {}) or {}
    _write_row(spark=spark, config=config, env_name=env_name, table=str(metadata_tables.get("data_steward", DATA_STEWARD_TABLE)), row=row)
    return row
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_create_or_update_data_steward`.

### `def _generate_steward_id(values: dict[str, Any]) -> str`

**What it does:**

Generate a stable public-safe steward identifier from business fields.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L529-L533">View `_generate_steward_id` on GitHub</a>

**Code:**

```python
def _generate_steward_id(values: dict[str, Any]) -> str:
    """Generate a stable public-safe steward identifier from business fields."""
    basis = "|".join(str(values.get(field, "")).strip().lower() for field in ("steward_name", "contact", "effective_from"))
    digest = hashlib.sha1(basis.encode("utf-8")).hexdigest()[:10]
    return f"STEW-{digest}"
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_generate_steward_id`.

### `def _get_widget_visible_fields(config: Any, kind: str) -> list[str]`

**What it does:**

Return configured editable columns without backend audit fields.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L156-L177">View `_get_widget_visible_fields` on GitHub</a>

**Code:**

```python
def _get_widget_visible_fields(config: Any, kind: str) -> list[str]:
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
    configured = {**_WIDGET_CONFIG_DEFAULTS[kind], **dict(_config_value(config, kind, {}) or {})}.get("visible_columns", [])
    hidden = set(STANDARD_RUNTIME_AUDIT_COLUMNS) | {"custom_fields_json"}
    if kind == "data_steward_widget":
        hidden.update({"steward_id", "is_active"})
    if kind == "data_agreement_widget":
        hidden.update(DATA_AGREEMENT_GENERATED_FIELDS)
    return [field for field in configured if field not in hidden]
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_get_widget_visible_fields`.

### `def _list_data_agreements(config: Any, env_name: str, *, spark_session: Any=None, active_only: bool=False, missing_ok: bool=False) -> list[dict[str, Any]]`

**What it does:**

List latest versioned agreements from the configured metadata lakehouse.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L684-L691">View `_list_data_agreements` on GitHub</a>

**Code:**

```python
def _list_data_agreements(config: Any, env_name: str, *, spark_session: Any = None, active_only: bool = False, missing_ok: bool = False) -> list[dict[str, Any]]:
    """List latest versioned agreements from the configured metadata lakehouse."""
    rows = _list_all_data_agreement_rows(config, env_name, spark_session=spark_session, missing_ok=missing_ok)
    agreements = _latest_agreement_versions(rows)
    if not active_only:
        return agreements
    today = datetime.now(timezone.utc).date()
    return [row for row in agreements if (not row.get("start_date") or date.fromisoformat(str(row["start_date"])[:10]) <= today) and (not row.get("expiry_date") or date.fromisoformat(str(row["expiry_date"])[:10]) >= today)]
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_list_data_agreements`.

### `def _latest_agreement_versions(rows: Any) -> list[dict[str, Any]]`

**What it does:**

Return the latest semantic version for each stable agreement ID.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L653-L669">View `_latest_agreement_versions` on GitHub</a>

**Code:**

```python
def _latest_agreement_versions(rows: Any) -> list[dict[str, Any]]:
    """Return the latest semantic version for each stable agreement ID."""

    def _agreement_sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
        return (
            _parse_contract_version(row.get("contract_version")),
            str(row.get("_committed_at") or row.get("updated_at") or row.get("uploaded_at") or ""),
            str(row.get("agreement_name") or ""),
            str(row.get("agreement_id") or ""),
        )

    latest: dict[str, dict[str, Any]] = {}
    for row in _coerce_row_dicts(rows):
        key = str(row.get("agreement_id") or "").strip()
        if key and (key not in latest or _agreement_sort_key(row) > _agreement_sort_key(latest[key])):
            latest[key] = row
    return sorted(latest.values(), key=lambda row: (str(row.get("agreement_name") or "").lower(), str(row.get("agreement_id") or "")))
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_latest_agreement_versions`.

### `def _render_custom_fields(config: list[dict[str, Any]] | dict[str, Any], *, values: dict[str, Any] | None=None) -> dict[str, Any]`

**What it does:**

Create widgets for configured organization-specific fields.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L310-L359">View `_render_custom_fields` on GitHub</a>

**Code:**

```python
def _render_custom_fields(config: list[dict[str, Any]] | dict[str, Any], *, values: dict[str, Any] | None = None) -> dict[str, Any]:
    """Create widgets for configured organization-specific fields.

    Parameters
    ----------
    config : list[dict[str, Any]] or dict[str, Any]
        Custom-field definitions or a widget config containing ``custom_fields``.
    values : dict[str, Any], optional
        Previously stored values used to prefill update forms.

    Returns
    -------
    dict[str, ipywidgets.Widget]
        Widgets keyed by custom-field key.

    Notes
    -----
    Supported field types are ``text``, ``textarea``, ``select``,
    ``multiselect``, ``date``, and ``boolean``.
    """
    widgets = _require_ipywidgets()

    definitions = config.get("custom_fields", []) if isinstance(config, dict) else config
    current = values or {}
    rendered: dict[str, Any] = {}
    for definition in definitions:
        key = str(definition["key"])
        field_type = str(definition.get("type", "text")).lower()
        label = str(definition.get("label", FIELD_LABELS.get(key, key.replace("_", " ").title())))
        common = _widget_common(widgets, label, textarea=field_type == "textarea")
        value = current.get(key)
        if field_type == "textarea":
            widget = widgets.Textarea(value=str(value or ""), **common)
        elif field_type == "select":
            options = list(definition.get("options", []))
            option_values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
            default_value = value if value in option_values else option_values[0] if option_values else None
            widget = widgets.Dropdown(options=options, value=default_value, **common)
        elif field_type == "multiselect":
            widget = widgets.SelectMultiple(options=list(definition.get("options", [])), value=tuple(value or ()), **common)
        elif field_type == "date":
            widget = widgets.DatePicker(value=date.fromisoformat(str(value)[:10]) if value else None, **common)
        elif field_type == "boolean":
            widget = widgets.Checkbox(value=_to_bool(value), **common)
        elif field_type == "text":
            widget = widgets.Text(value=str(value or ""), **common)
        else:
            raise ValueError(f"Unsupported custom field type: {field_type}")
        rendered[key] = widget
    return rendered
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_render_custom_fields`.

### `def _require_ipywidgets()`

**What it does:**

Return ipywidgets or raise an actionable optional-dependency error.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L63-L72">View `_require_ipywidgets` on GitHub</a>

**Code:**

```python
def _require_ipywidgets():
    """Return ipywidgets or raise an actionable optional-dependency error."""
    try:
        import ipywidgets as widgets
    except ModuleNotFoundError as exc:
        raise ModuleNotFoundError(
            "The data agreement widget feature requires the 'dq-review' extra. "
            'Install with: pip install "fabricops-kit[dq-review]"'
        ) from exc
    return widgets
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_require_ipywidgets`.

### `def _widget_common(widgets_module: Any, description: str, *, textarea: bool=False) -> dict[str, Any]`

**What it does:**

Return common style and layout keyword arguments for form controls.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L180-L189">View `_widget_common` on GitHub</a>

**Code:**

```python
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
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_widget_common`.

### `def _render_searchable_selector(*, widgets: Any, label: str, rows: list[dict[str, Any]], label_fn: Callable[[dict[str, Any]], str], value_fn: Callable[[dict[str, Any]], str], placeholder: str='Search...', max_results: int=25, search_fields: list[str] | None=None, context_fields: list[tuple[str, str]] | None=None, empty_label: str | None=None, selected_value: str | None=None) -> dict[str, Any]`

**What it does:**

Render a table-backed selector with search and stable-value tracking.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L198-L308">View `_render_searchable_selector` on GitHub</a>

**Code:**

```python
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
    """Render a table-backed selector with search and stable-value tracking.

    The visible label may be friendly and long, while the selection value remains
    the stable key produced by ``value_fn``. The returned ``selector`` is the
    select control used by persistence code, and its ``value`` is never replaced
    with the display label.
    """
    search = widgets.Text(value="", placeholder=placeholder, **_widget_common(widgets, f"Search {label}"))
    selector = widgets.Select(options=[], **_widget_common(widgets, label))
    context = widgets.HTML(value="")
    lookup: dict[str, dict[str, Any]] = {}
    indexed_rows: list[dict[str, Any]] = []

    def _set_rows(new_rows: list[dict[str, Any]]) -> None:
        lookup.clear()
        indexed_rows.clear()
        for row in new_rows:
            value = str(value_fn(row) or "").strip()
            if not value:
                continue
            display_label = str(label_fn(row) or value)
            lookup[value] = row
            indexed_rows.append({
                "row": row,
                "label": display_label,
                "value": value,
                "search": " ".join(
                    [display_label, value, *(str(row.get(field) or "") for field in (search_fields or sorted(str(key) for key in row)))]
                ).casefold(),
            })

    def _matching_options(query: str) -> list[tuple[str, str]]:
        needle = str(query or "").casefold().strip()
        matches = [item for item in indexed_rows if not needle or needle in item["search"]]
        return [(item["label"], item["value"]) for item in matches[:max_results]]

    def _render_context(value: Any) -> None:
        row = lookup.get(str(value or ""))
        context.value = "<br>".join(
            f"<b>{_html_escape(field_label)}:</b> {_html_escape(row.get(field, ''))}"
            for field, field_label in context_fields
        ) if row and context_fields else ("<em>No record selected.</em>" if context_fields else "")

    def _apply_filter(preferred_value: Any = None) -> None:
        current = str(preferred_value if preferred_value is not None else selector.value or "")
        options = _matching_options(search.value)
        if empty_label is not None:
            options = [(empty_label, ""), *options]
        selector.options = options
        values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
        if current and current in lookup and current not in values and not str(search.value or "").strip():
            row = lookup[current]
            options = [(str(label_fn(row) or current), current), *options]
            values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
        non_empty_values = [value for value in values if value]
        if current in values and (current or not str(search.value or "").strip()):
            selector.value = current
        elif non_empty_values:
            selector.value = non_empty_values[0]
        elif values:
            selector.value = values[0]
        else:
            selector.value = None
        _render_context(selector.value)

    def _on_search(change: dict[str, Any]) -> None:
        if change.get("name") == "value":
            _apply_filter(selector.value)

    def _on_select(change: dict[str, Any]) -> None:
        if change.get("name") == "value":
            _render_context(change.get("new"))

    def _refresh_rows(new_rows: list[dict[str, Any]], selected: str | None = None) -> None:
        _set_rows(new_rows)
        _apply_filter(selected)

    def _select_value(value: str | None) -> None:
        _apply_filter(str(value or ""))

    search.observe(_on_search, names="value")
    selector.observe(_on_select, names="value")
    _refresh_rows(rows, selected_value)
    container = widgets.VBox([search, selector, context])
    selector.search_box = search
    selector.context_html = context
    selector.refresh_rows = _refresh_rows
    selector.select_value = _select_value
    selector.rows_by_value = lookup
    return {
        "container": container,
        "search": search,
        "selector": selector,
        "context": context,
        "rows_by_value": lookup,
        "refresh_rows": _refresh_rows,
    }
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_render_searchable_selector`.

### `def _html_escape(value: Any) -> str`

**What it does:**

Return display-safe HTML text for notebook context snippets.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L192-L195">View `_html_escape` on GitHub</a>

**Code:**

```python
def _html_escape(value: Any) -> str:
    """Return display-safe HTML text for notebook context snippets."""
    import html
    return html.escape(str(value or ""))
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_html_escape`.

### `def _standard_widget(field: str, value: Any='', *, options: list[Any] | None=None) -> Any`

**What it does:**

Internal helper used by the package implementation.

**Source:**

- `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/4effb3776a2bd42fe144261564c324aeb0e0d9c8/src/fabricops_kit/data_agreement.py#L1101-L1114">View `_standard_widget` on GitHub</a>

**Code:**

```python
def _standard_widget(field: str, value: Any = "", *, options: list[Any] | None = None) -> Any:
    widgets = _require_ipywidgets()
    description = FIELD_LABELS.get(field, field.replace("_", " ").title())
    if options is not None:
        option_values = [option[1] if isinstance(option, tuple) and len(option) == 2 else option for option in options]
        default_value = value if value in option_values else option_values[0] if option_values else None
        return widgets.Dropdown(options=options, value=default_value, **_widget_common(widgets, description))
    if field in {"effective_from", "effective_to", "start_date", "expiry_date"}:
        return widgets.DatePicker(value=date.fromisoformat(str(value)[:10]) if value else None, **_widget_common(widgets, description))
    if field == "is_active":
        return widgets.Checkbox(value=True if value == "" else _to_bool(value), **_widget_common(widgets, description))
    if field in {"business_purpose", "approved_usage_internal", "approved_usage_external", "approved_usage_research"}:
        return widgets.Textarea(value=str(value or ""), **_widget_common(widgets, description, textarea=True))
    return widgets.Text(value=str(value or ""), **_widget_common(widgets, description))
```

**Used here because:**

`widget_render_data_agreement` reaches this helper in its implementation path.

**Modify this if:**

You want to change the implementation behavior summarized above for `widget_render_data_agreement` or another caller that reaches `_standard_widget`.


</details>
