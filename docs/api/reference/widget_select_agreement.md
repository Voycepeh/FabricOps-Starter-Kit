# widget_select_agreement

## Signature

```python
def widget_select_agreement(agreement_rows_or_config: Any, env_name: str | None=None, *, spark_session: Any=None, register_notebook: bool=False, notebook_type: str | None=None, environment_name: str | None=None, dataset_name: str | None=None, table_name: str | None=None, topic: str | None=None, pipeline_name: str | None=None) -> Any
```

## Summary

Render an agreement selector and optionally register the active notebook.

## Usage note

- Use near the start of 02_pipeline or 99_explore before reads, profiling, lineage, or governance evidence need an agreement id.

**Do not use when:**

- Do not use when an agreement has already been programmatically selected and validated, or for catalogue table review selection in 03_governance.

**Additional context:**

Displays an agreement selector and stores the chosen agreement so pipeline and exploration notebooks can bind work to approved business context.

## Parameters

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `agreement_rows_or_config` | `Any` | Yes | Pass ``CONFIG`` in normal notebooks, or provide preloaded agreement rows when the caller already has them available. |
| `env_name` | `str \| None` | No | Environment key used to load agreements when ``CONFIG`` is supplied. |
| `spark_session` | `Any` | No | Fabric Spark session used for configured metadata-table reads. |
| `register_notebook` | `bool` | No | When True, render registration status and a button that links the current notebook to the selected agreement. |
| `notebook_type` | `str \| None` | No | Workflow metadata passed to ``_register_current_notebook`` when ``register_notebook`` is enabled. |
| `environment_name` | `str \| None` | No | Not documented yet |
| `dataset_name` | `str \| None` | No | Not documented yet |
| `table_name` | `str \| None` | No | Not documented yet |
| `topic` | `str \| None` | No | Not documented yet |
| `pipeline_name` | `str \| None` | No | Not documented yet |

## Returns

Interactive widget state; call get_selected_agreement to retrieve the selected agreement record.

### Return interpretation

A visible selection widget does not mean an agreement is selected; call get_selected_agreement after the user chooses a row.

## Raises / Errors

Raises metadata read, widget dependency, or configuration errors when agreement metadata cannot be loaded.

### Common failure causes

- No agreement metadata rows are available.
- The user has not selected an agreement.
- Notebook registration metadata cannot be written.
- The configured metadata lakehouse cannot be read.

## Example

```python
widget_select_agreement(CONFIG, env="Sandbox", spark_session=spark)
agreement = get_selected_agreement()
```

## See also

- [Notebook Templates](../../how-fabricops-works/notebook-templates.md)

**Glossary terms**

- **Notebook template:** A starter notebook that shows where and how FabricOps helpers are used.

See the [full glossary](../../../reference/glossary/) for more FabricOps terms.

## Developer details

- Module: `data_agreement`
- Classification: Callable
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `773`
- Signature:

```python
def widget_select_agreement(agreement_rows_or_config: Any, env_name: str | None=None, *, spark_session: Any=None, register_notebook: bool=False, notebook_type: str | None=None, environment_name: str | None=None, dataset_name: str | None=None, table_name: str | None=None, topic: str | None=None, pipeline_name: str | None=None) -> Any
```

**Used in templates:**

- `02_pipeline`
- `99_explore`

**Side effects:**

Displays an IPython widget and may register the active notebook selection in metadata when requested.

**Notes:**

No additional callable notes are documented.

## Calls

- `fabricops_kit.data_agreement._html_escape`
- `fabricops_kit.data_agreement._latest_agreement_versions`
- `fabricops_kit.data_agreement._list_data_agreements`
- `fabricops_kit.data_agreement._render_searchable_selector`
- `fabricops_kit.data_agreement._require_ipywidgets`
- `fabricops_kit.metadata._current_notebook_active_registrations`
- `fabricops_kit.metadata._register_current_notebook`

## Internal implementation summary

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in the internal implementation summary.

    ```text
    widget_select_agreement(...)
    ├── _current_notebook_active_registrations(...)
    │   ├── _context_get(...)
    │   ├── _load_notebook_registry(...)
    │   │   └── …
    │   ├── _runtime_context(...)
    │   │   └── …
    │   └── _safe_str(...)
    ├── _html_escape(...)
    ├── _latest_agreement_versions(...)
    │   ├── _coerce_row_dicts(...)
    │   └── _parse_contract_version(...)
    ├── _list_data_agreements(...)
    │   ├── _latest_agreement_versions(...)
    │   │   └── …
    │   └── _list_all_data_agreement_rows(...)
    │       └── …
    ├── _register_current_notebook(...)
    │   ├── _context_get(...)
    │   ├── _current_audit_timestamp(...)
    │   │   └── …
    │   ├── _notebook_registration_key(...)
    │   ├── _rows_for_spark(...)
    │   ├── _runtime_context(...)
    │   │   └── …
    │   ├── _safe_str(...)
    │   └── write_lakehouse_table(...)
    │       └── …
    ├── _render_searchable_selector(...)
    │   ├── _html_escape(...)
    │   └── _widget_common(...)
    └── _require_ipywidgets(...)
    ```

??? info "Internal helpers used: 22"

    This callable uses 22 internal helpers for audit timestamp, metadata loading, rule parsing, fabric or spark access, and other.

    <div class="module-table-scroll reference-input-table">
    <table class="reference-function-table">
      <thead>
        <tr>
          <th>Area</th>
          <th>Helpers</th>
          <th>What they do</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td data-label="Area">Audit timestamp</td>
          <td data-label="Helpers"><code>_current_audit_timestamp</code>, <code>_get_audit_timezone</code>, <code>_validate_audit_timezone</code></td>
          <td data-label="What they do">Resolve and stamp audit time consistently.</td>
        </tr>
        <tr>
          <td data-label="Area">Metadata loading</td>
          <td data-label="Helpers"><code>_latest_agreement_versions</code>, <code>_list_all_data_agreement_rows</code>, <code>_list_data_agreements</code>, <code>_load_notebook_registry</code>, <code>_render_searchable_selector</code></td>
          <td data-label="What they do">Load and identify the metadata or table context needed by the callable.</td>
        </tr>
        <tr>
          <td data-label="Area">Rule parsing</td>
          <td data-label="Helpers"><code>_parse_contract_version</code></td>
          <td data-label="What they do">Normalize stored or user-provided values before applying rules.</td>
        </tr>
        <tr>
          <td data-label="Area">Fabric or Spark access</td>
          <td data-label="Helpers"><code>_rows_for_spark</code></td>
          <td data-label="What they do">Access Fabric or Spark runtime services used by the implementation.</td>
        </tr>
        <tr>
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_coerce_row_dicts</code>, <code>_coerce_row_dicts</code>, <code>_config_value</code>, <code>_context_get</code>, <code>_current_notebook_active_registrations</code>, <code>_html_escape</code>, <code>_notebook_registration_key</code>, <code>_register_current_notebook</code>, <code>_require_ipywidgets</code>, <code>_runtime_context</code>, <code>_safe_str</code>, <code>_widget_common</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Audit timestamp helpers"

            **`def _current_audit_timestamp(config: Any=None, timezone_name: str | None=None, *, drop_microseconds: bool=True) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/config.py#L69-L75)

            ```python
            def _current_audit_timestamp(config: Any = None, timezone_name: str | None = None, *, drop_microseconds: bool = True) -> str:
                """Return the current audit timestamp in the configured audit timezone."""
                tz_name = _get_audit_timezone(config, timezone_name)
                value = datetime.now(ZoneInfo(tz_name))
                if drop_microseconds:
                    value = value.replace(microsecond=0)
                return value.isoformat()
            ```

            **`def _get_audit_timezone(config: Any=None, timezone_name: str | None=None) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/config.py#L61-L66)

            ```python
            def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
                """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
                if timezone_name is not None:
                    return _validate_audit_timezone(timezone_name)
                value = getattr(config, "audit_timezone", None) if config is not None else None
                return _validate_audit_timezone(value)
            ```

            **`def _validate_audit_timezone(timezone_name: str | None) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/config.py#L27-L58)

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

        ??? example "Metadata loading helpers"

            **`def _latest_agreement_versions(rows: Any) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/data_agreement.py#L570-L586)

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

            **`def _list_all_data_agreement_rows(config: Any, env_name: str, *, spark_session: Any=None, missing_ok: bool=False) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/data_agreement.py#L589-L598)

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

            **`def _list_data_agreements(config: Any, env_name: str, *, spark_session: Any=None, active_only: bool=False, missing_ok: bool=False) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/data_agreement.py#L601-L608)

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

            **`def _load_notebook_registry(spark, agreement_id=None, metadata_table=NOTEBOOK_REGISTRY_TABLE, notebook_type=None, environment_name=None, missing_ok: bool=True, *, config: Any=None, env: str | None=None, active_only: bool=False, notebook_id: str | None=None, notebook_name: str | None=None, registration_role: str | None=None) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L336-L387)

            ```python
            def _load_notebook_registry(
                spark,
                agreement_id=None,
                metadata_table=NOTEBOOK_REGISTRY_TABLE,
                notebook_type=None,
                environment_name=None,
                missing_ok: bool = True,
                *,
                config: Any = None,
                env: str | None = None,
                active_only: bool = False,
                notebook_id: str | None = None,
                notebook_name: str | None = None,
                registration_role: str | None = None,
            ) -> list[dict[str, Any]]:
                try:
                    table = (
                        read_lakehouse_table(config, env, "metadata", metadata_table, spark_session=spark)
                        if config is not None and env is not None
                        else spark.table(metadata_table)
                    )
                    rows = _coerce_row_dicts(table)
                except Exception:
                    if missing_ok:
                        return []
                    raise
                if active_only:
                    latest: dict[str, dict[str, Any]] = {}
                    for row in rows:
                        key = row.get("registration_id") or _notebook_registration_key(row)
                        previous = latest.get(key)
                        if previous is None or str(row.get("registered_at") or "") >= str(previous.get("registered_at") or ""):
                            latest[key] = row
                    rows = list(latest.values())
                out = []
                for row in rows:
                    if agreement_id is not None and str(row.get("agreement_id") or "") != str(agreement_id):
                        continue
                    if notebook_type and str(row.get("notebook_type") or "") != str(notebook_type):
                        continue
                    if environment_name and str(row.get("environment_name") or "") != str(environment_name):
                        continue
                    if notebook_id and str(row.get("notebook_id") or "") != str(notebook_id):
                        continue
                    if notebook_name and str(row.get("notebook_name") or "") != str(notebook_name):
                        continue
                    if registration_role and str(row.get("registration_role") or "") != str(registration_role):
                        continue
                    if active_only and str(row.get("registration_status") or "active") != "active":
                        continue
                    out.append(row)
                return out
            ```

            **`def _render_searchable_selector(*, widgets: Any, label: str, rows: list[dict[str, Any]], label_fn: Callable[[dict[str, Any]], str], value_fn: Callable[[dict[str, Any]], str], placeholder: str='Search...', max_results: int=25, search_fields: list[str] | None=None, context_fields: list[tuple[str, str]] | None=None, empty_label: str | None=None, selected_value: str | None=None) -> dict[str, Any]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/data_agreement.py#L198-L308)

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

        ??? example "Rule parsing helpers"

            **`def _parse_contract_version(version: Any) -> tuple[int, int, int]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/data_agreement.py#L555-L561)

            ```python
            def _parse_contract_version(version: Any) -> tuple[int, int, int]:
                """Parse a semantic contract version into a comparable tuple."""
                try:
                    parts = str(version or "").strip().split(".")
                    return tuple(int(parts[index]) if index < len(parts) else 0 for index in range(3))  # type: ignore[return-value]
                except (TypeError, ValueError):
                    return (0, 0, 0)
            ```

        ??? example "Fabric or Spark access helpers"

            **`def _rows_for_spark(rows: list[dict[str, Any]]) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L89-L98)

            ```python
            def _rows_for_spark(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
                out = []
                for row in rows or []:
                    item = dict(row)
                    if isinstance(item.get("approved_at"), datetime):
                        item["approved_at"] = item["approved_at"].isoformat()
                    if isinstance(item.get("ai_suggestion_json"), (dict, list)):
                        item["ai_suggestion_json"] = json.dumps(item["ai_suggestion_json"], sort_keys=True)
                    out.append(item)
                return out
            ```

        ??? example "Other helpers"

            **`def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/data_agreement.py#L397-L402)

            ```python
            def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
                if rows is None:
                    return []
                if hasattr(rows, "collect"):
                    rows = rows.collect()
                return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]
            ```

            **`def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L53-L58)

            ```python
            def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
                if rows is None:
                    return []
                if hasattr(rows, "collect"):
                    rows = rows.collect()
                return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]
            ```

            **`def _config_value(config: Any, name: str, default: Any) -> Any`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/data_agreement.py#L149-L153)

            ```python
            def _config_value(config: Any, name: str, default: Any) -> Any:
                agreement_config = getattr(config, "data_agreement_config", config)
                if isinstance(agreement_config, dict):
                    return agreement_config.get(name, default)
                return getattr(agreement_config, name, default)
            ```

            **`def _context_get(context: Any, *keys: str) -> Any`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L101-L113)

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

            **`def _current_notebook_active_registrations(spark, *, config: Any, env: str, metadata_table: str=NOTEBOOK_REGISTRY_TABLE, notebook_type: str | None=None, environment_name: str | None=None, registration_role: str | None=None, missing_ok: bool=True) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L390-L440)

            ```python
            def _current_notebook_active_registrations(
                spark,
                *,
                config: Any,
                env: str,
                metadata_table: str = NOTEBOOK_REGISTRY_TABLE,
                notebook_type: str | None = None,
                environment_name: str | None = None,
                registration_role: str | None = None,
                missing_ok: bool = True,
            ) -> list[dict[str, Any]]:
                """Return active agreement registrations for the running notebook.

                Parameters
                ----------
                spark : pyspark.sql.SparkSession
                    Fabric Spark session used to read the metadata table.
                config : FrameworkConfig or dict
                    Metadata route configuration from ``00_env_config``.
                env : str
                    Environment key paired with ``config``.
                metadata_table : str, default=NOTEBOOK_REGISTRY_TABLE
                    Physical notebook registry table name.
                notebook_type, environment_name, registration_role : str, optional
                    Optional filters for notebook phase, environment, and primary versus
                    additional registration role.
                missing_ok : bool, default=True
                    Return an empty list when the registry cannot be read.

                Returns
                -------
                list[dict[str, Any]]
                    Active latest registration rows for the current notebook runtime.
                """
                ctx = _runtime_context()
                notebook_id = _safe_str(_context_get(ctx, "currentNotebookId", "notebookId"))
                notebook_name = _safe_str(_context_get(ctx, "currentNotebookName", "notebookName") or "unknown_notebook")
                rows = _load_notebook_registry(
                    spark,
                    metadata_table=metadata_table,
                    notebook_type=notebook_type,
                    environment_name=environment_name,
                    missing_ok=missing_ok,
                    config=config,
                    env=env,
                    active_only=True,
                    notebook_id=notebook_id or None,
                    notebook_name=None if notebook_id else notebook_name,
                    registration_role=registration_role,
                )
                return rows
            ```

            **`def _html_escape(value: Any) -> str`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/data_agreement.py#L192-L195)

            ```python
            def _html_escape(value: Any) -> str:
                """Return display-safe HTML text for notebook context snippets."""
                import html
                return html.escape(str(value or ""))
            ```

            **`def _notebook_registration_key(row: dict[str, Any]) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L41-L50)

            ```python
            def _notebook_registration_key(row: dict[str, Any]) -> str:
                parts = [
                    str(row.get("workspace_id") or ""),
                    str(row.get("notebook_id") or ""),
                    str(row.get("notebook_name") or ""),
                    str(row.get("agreement_id") or ""),
                    str(row.get("agreement_contract_version") or ""),
                    str(row.get("registration_role") or ""),
                ]
                return hashlib.sha256("||".join(parts).encode("utf-8")).hexdigest()[:24]
            ```

            **`def _register_current_notebook(spark, agreement_id=None, notebook_type=None, environment_name=None, dataset_name=None, table_name=None, topic=None, pipeline_name=None, contract_version=None, registration_role='primary', registration_status='active', registration_id=None, superseded_at=None, superseded_by_registration_id=None, metadata_table=NOTEBOOK_REGISTRY_TABLE, *, config: Any=None, env: str | None=None)`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L220-L333)

            ```python
            def _register_current_notebook(
                spark,
                agreement_id=None,
                notebook_type=None,
                environment_name=None,
                dataset_name=None,
                table_name=None,
                topic=None,
                pipeline_name=None,
                contract_version=None,
                registration_role="primary",
                registration_status="active",
                registration_id=None,
                superseded_at=None,
                superseded_by_registration_id=None,
                metadata_table=NOTEBOOK_REGISTRY_TABLE,
                *,
                config: Any = None,
                env: str | None = None,
            ):
                """Append a runtime notebook registration row.

                Parameters
                ----------
                spark : pyspark.sql.SparkSession
                    Fabric Spark session used to append the registration row.
                config : FrameworkConfig or dict, optional
                    Recommended metadata route configuration from ``00_env_config``. When
                    paired with ``env``, the row is written through
                    ``write_lakehouse_table(df, config, env, "metadata", metadata_table)``.
                env : str, optional
                    Environment key paired with ``config`` for metadata lakehouse routing.
                agreement_id : str
                    Agreement identifier this notebook supports.
                notebook_type : str
                    Notebook family or workflow phase. When blank, the value is inferred
                    from the current notebook name prefix.
                environment_name, dataset_name, table_name, topic, pipeline_name : str, optional
                    Optional workflow context recorded with the notebook registration.
                contract_version : str, optional
                    Agreement contract version selected when the notebook was registered.
                registration_role : {"primary", "additional"}, default="primary"
                    Whether the row represents the notebook's user-facing active agreement
                    or an additional audit link.
                registration_status : {"active", "superseded"}, default="active"
                    Current registration event state. Superseded rows are retained for audit
                    and ignored by active-registration helpers.
                registration_id : str, optional
                    Stable registration identifier. When omitted, a deterministic identifier
                    is generated from the notebook and agreement identity.
                superseded_at, superseded_by_registration_id : str, optional
                    Audit values populated when a prior registration is superseded.
                metadata_table : str, default=NOTEBOOK_REGISTRY_TABLE
                    Physical notebook registry table name.

                Returns
                -------
                dict[str, str]
                    Registration row matching :data:`NOTEBOOK_REGISTRY_FIELDS`.

                Raises
                ------
                ValueError
                    If the recommended ``config``/``env`` route is not provided.

                Notes
                -----
                ``00_env_config`` prepares the notebook registry as part of
                :func:`fabricops_kit.config.setup_metadata_tables`. New notebooks should
                pass ``config=CONFIG`` and ``env=ENV`` so metadata writes use the
                configured ``metadata`` target from ``00_env_config``.
                """
                if config is None or env is None:
                    raise ValueError("_register_current_notebook requires config and env for metadata routing.")

                ctx = _runtime_context()
                workspace_id = _context_get(ctx, "currentWorkspaceId", "workspaceId")
                workspace_name = _context_get(ctx, "currentWorkspaceName", "workspaceName")
                notebook_id = _context_get(ctx, "currentNotebookId", "notebookId")
                notebook_name = _context_get(ctx, "currentNotebookName", "notebookName") or "unknown_notebook"
                user_id = _context_get(ctx, "userId")
                user_name = _context_get(ctx, "userName")
                inferred_type = notebook_type or str(notebook_name).split("_", 1)[0]
                row = {
                    "agreement_id": _safe_str(agreement_id),
                    "environment_name": _safe_str(environment_name),
                    "dataset_name": _safe_str(dataset_name),
                    "table_name": _safe_str(table_name),
                    "topic": _safe_str(topic),
                    "pipeline_name": _safe_str(pipeline_name),
                    "notebook_type": _safe_str(inferred_type),
                    "workspace_id": _safe_str(workspace_id),
                    "workspace_name": _safe_str(workspace_name),
                    "notebook_id": _safe_str(notebook_id),
                    "notebook_name": _safe_str(notebook_name),
                    "notebook_url": _safe_str(
                        f"https://app.fabric.microsoft.com/groups/{workspace_id}/notebooks/{notebook_id}"
                        if workspace_id and notebook_id
                        else ""
                    ),
                    "user_name": _safe_str(user_name),
                    "user_id": _safe_str(user_id),
                    "registered_at": _current_audit_timestamp(config=config, drop_microseconds=False),
                    "agreement_contract_version": _safe_str(contract_version),
                    "registration_role": _safe_str(registration_role or "primary"),
                    "registration_status": _safe_str(registration_status or "active"),
                    "superseded_at": _safe_str(superseded_at),
                    "superseded_by_registration_id": _safe_str(superseded_by_registration_id),
                }
                row["registration_id"] = _safe_str(registration_id or _notebook_registration_key(row))
                row = {field: row.get(field, "") for field in NOTEBOOK_REGISTRY_FIELDS}
                df = spark.createDataFrame(_rows_for_spark([row]))
                write_lakehouse_table(df, config, env, "metadata", metadata_table, mode="append")
                return row
            ```

            **`def _require_ipywidgets()`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/data_agreement.py#L63-L72)

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

            **`def _runtime_context() -> dict[str, Any]`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L120-L144)

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

            **`def _safe_str(value: Any) -> str`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/metadata.py#L116-L117)

            ```python
            def _safe_str(value: Any) -> str:
                return "" if value is None else str(value)
            ```

            **`def _widget_common(widgets_module: Any, description: str, *, textarea: bool=False) -> dict[str, Any]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/data_agreement.py#L180-L189)

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


## Source link

- Source file path: `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/data_agreement.py#L773-L997">View widget_select_agreement on GitHub</a>

```python
def widget_select_agreement(agreement_rows_or_config: Any, env_name: str | None = None, *, spark_session: Any = None, register_notebook: bool = False, notebook_type: str | None = None, environment_name: str | None = None, dataset_name: str | None = None, table_name: str | None = None, topic: str | None = None, pipeline_name: str | None = None) -> Any:
    """Render a downstream agreement selector and retain the selected row.

    Parameters
    ----------
    agreement_rows_or_config : FrameworkConfig or iterable
        Pass ``CONFIG`` in normal notebooks, or provide preloaded agreement
        rows when the caller already has them available.
    env_name : str, optional
        Environment key used to load agreements when ``CONFIG`` is supplied.
    spark_session : pyspark.sql.SparkSession, optional
        Fabric Spark session used for configured metadata-table reads.
    register_notebook : bool, default=False
        When True, render registration status and a button that links the
        current notebook to the selected agreement.
    notebook_type, environment_name, dataset_name, table_name, topic, pipeline_name : str, optional
        Workflow metadata passed to ``_register_current_notebook`` when
        ``register_notebook`` is enabled.

    Returns
    -------
    ipywidgets.Select
        Displayed searchable latest-version agreement selector control. Its
        ``value`` remains the stable ``agreement_id`` for existing callers.
        When registration is enabled, registration widgets are attached as
        attributes on the selector for advanced notebook automation.
    """
    widgets = _require_ipywidgets()
    from IPython import display as ip

    global _SELECTED_AGREEMENT
    if env_name is not None:
        try:
            rows = _list_data_agreements(agreement_rows_or_config, env_name, spark_session=spark_session)
        except Exception as exc:
            raise RuntimeError("No agreements found. Run 01_agreement first.") from exc
    else:
        rows = agreement_rows_or_config
    latest_rows = _latest_agreement_versions(rows)
    if not latest_rows:
        raise ValueError("No agreements found. Save a data agreement in notebook 01_agreement first.")
    rows_by_id = {str(row.get("agreement_id") or "").strip(): row for row in latest_rows if str(row.get("agreement_id") or "").strip()}

    def _agreement_label(row: dict[str, Any]) -> str:
        agreement_id = str(row.get("agreement_id") or "").strip()
        return f"{row.get('agreement_name', '') or agreement_id} ({agreement_id} / v{row.get('contract_version', '')})"

    selector_parts = _render_searchable_selector(
        widgets=widgets,
        label="Agreement",
        rows=latest_rows,
        label_fn=_agreement_label,
        value_fn=lambda row: str(row.get("agreement_id") or "").strip(),
        placeholder="Search agreements...",
        search_fields=["agreement_name", "agreement_id", "contract_version", "domain", "recipient"],
        context_fields=[("agreement_name", "Agreement name"), ("agreement_id", "Agreement ID"), ("contract_version", "Current version"), ("recipient", "Recipient")],
    )
    selector = selector_parts["selector"]

    def _on_change(change: dict[str, Any]) -> None:
        global _SELECTED_AGREEMENT
        if change.get("name") == "value" and change.get("new") is not None:
            selected_row = rows_by_id.get(str(change["new"]))
            if selected_row is not None:
                _SELECTED_AGREEMENT = dict(selected_row)

    selector.observe(_on_change, names="value")
    if selector.value in rows_by_id:
        _SELECTED_AGREEMENT = dict(rows_by_id[str(selector.value)])
    selector.search_box = selector_parts["search"]
    selector.context_html = selector_parts["context"]

    registration_status = None
    registration_action = None
    register_button = None
    registration_output = None
    active_rows: list[dict[str, Any]] = []
    active_primary_rows: list[dict[str, Any]] = []

    def _selected_row() -> dict[str, Any] | None:
        return rows_by_id.get(str(selector.value or ""))

    def _status_message() -> str:
        selected = _selected_row()
        if not selected:
            return "Select an agreement before registering this notebook."
        selected_id = str(selected.get("agreement_id") or "")
        selected_version = str(selected.get("contract_version") or "")
        same_active = [row for row in active_rows if str(row.get("agreement_id") or "") == selected_id and str(row.get("agreement_contract_version") or "") == selected_version]
        same_primary = [row for row in same_active if str(row.get("registration_role") or "primary") == "primary"]
        other = [row for row in active_primary_rows if row not in same_primary]
        if same_primary:
            return f"Registration status: already registered to {selected_id} version {selected_version} as the primary active agreement."
        if same_active:
            role = str(same_active[0].get("registration_role") or "additional")
            return f"Registration status: already registered to {selected_id} version {selected_version} as an active {role} agreement link."
        if other:
            current = other[0]
            current_version = str(current.get("agreement_contract_version") or "unknown version")
            return f"Registration status: this notebook is already registered to {current.get('agreement_id', '')} version {current_version}. Choose how to handle the selected agreement."
        return "Registration status: not registered to an active agreement."

    def _refresh_registration_status(*_: Any) -> None:
        if registration_status is None:
            return
        registration_status.value = _html_escape(_status_message())

    if register_notebook:
        if env_name is None or spark_session is None:
            raise ValueError("widget_select_agreement(..., register_notebook=True) requires CONFIG, env_name, and spark_session.")
        config = agreement_rows_or_config
        active_rows = _current_notebook_active_registrations(
            spark_session,
            config=config,
            env=env_name,
            notebook_type=notebook_type,
            environment_name=environment_name or env_name,
        )
        active_primary_rows = [row for row in active_rows if str(row.get("registration_role") or "primary") == "primary"]
        registration_status = widgets.HTML(value="")
        registration_action = widgets.ToggleButtons(
            options=["Cancel", "Replace active registration", "Add another agreement link"],
            value="Cancel",
            description="If already linked",
        )
        register_button = widgets.Button(description="Register notebook", button_style="primary")
        registration_output = widgets.Output()

        def _register(_: Any = None) -> None:
            selected = _selected_row()
            if registration_output is not None:
                registration_output.clear_output()
            if not selected:
                if registration_status is not None:
                    registration_status.value = "Select an agreement before registering this notebook."
                return
            selected_id = str(selected.get("agreement_id") or "")
            selected_version = str(selected.get("contract_version") or "")
            same_active = [row for row in active_rows if str(row.get("agreement_id") or "") == selected_id and str(row.get("agreement_contract_version") or "") == selected_version]
            same_primary = [row for row in same_active if str(row.get("registration_role") or "primary") == "primary"]
            other = [row for row in active_primary_rows if row not in same_primary]
            if same_active:
                role = str(same_active[0].get("registration_role") or "primary")
                if registration_status is not None:
                    registration_status.value = _html_escape(f"Notebook is already registered to {selected_id} version {selected_version} as an active {role} agreement link; no duplicate was created.")
                return

            role = "primary"
            if other:
                choice = getattr(registration_action, "value", "Cancel")
                if choice == "Cancel":
                    if registration_status is not None:
                        registration_status.value = "Registration canceled. Existing active registration was not changed."
                    return
                if choice == "Add another agreement link":
                    role = "additional"
                elif choice == "Replace active registration":
                    role = "primary"
                else:
                    return

            new_row = _register_current_notebook(
                spark_session,
                config=config,
                env=env_name,
                agreement_id=selected_id,
                contract_version=selected_version,
                registration_role=role,
                registration_status="active",
                notebook_type=notebook_type,
                environment_name=environment_name or env_name,
                dataset_name=dataset_name,
                table_name=table_name,
                topic=topic,
                pipeline_name=pipeline_name,
            )
            if other and role == "primary":
                superseded_at = _current_audit_timestamp(config=config, drop_microseconds=False)
                for previous in other:
                    _register_current_notebook(
                        spark_session,
                        config=config,
                        env=env_name,
                        agreement_id=previous.get("agreement_id"),
                        contract_version=previous.get("agreement_contract_version"),
                        registration_role=previous.get("registration_role") or "primary",
                        registration_status="superseded",
                        registration_id=previous.get("registration_id"),
                        superseded_at=superseded_at,
                        superseded_by_registration_id=new_row.get("registration_id"),
                        notebook_type=previous.get("notebook_type") or notebook_type,
                        environment_name=previous.get("environment_name") or environment_name or env_name,
                        dataset_name=previous.get("dataset_name") or dataset_name,
                        table_name=previous.get("table_name") or table_name,
                        topic=previous.get("topic") or topic,
                        pipeline_name=previous.get("pipeline_name") or pipeline_name,
                    )
                for previous in other:
                    if previous in active_rows:
                        active_rows.remove(previous)
                active_rows.append(new_row)
                active_primary_rows[:] = [new_row]
                message = f"Replaced active registration with {selected_id} version {selected_version}. Previous registration history remains in the audit trail."
            elif role == "additional":
                active_rows.append(new_row)
                message = f"Added additional agreement link to {selected_id} version {selected_version}. Existing primary registration remains active."
            else:
                active_rows.append(new_row)
                active_primary_rows[:] = [new_row]
                message = f"Registered notebook to {selected_id} version {selected_version}."
            if registration_status is not None:
                registration_status.value = _html_escape(message)

        register_button.on_click(_register)
        selector.observe(lambda change: _refresh_registration_status() if change.get("name") == "value" else None, names="value")
        _refresh_registration_status()
        selector.registration_status = registration_status
        selector.registration_action = registration_action
        selector.register_button = register_button
        selector.registration_output = registration_output
        selector.container = widgets.VBox([selector_parts["container"], registration_status, registration_action, register_button, registration_output])
    else:
        selector.container = selector_parts["container"]
    ip.display(selector.container)
    return selector
```

<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.widget_select_agreement`
- Short name: `widget_select_agreement`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `773`
- Inbound references count: 0
- Outbound references count: 7
- Used in templates: 02_pipeline, 99_explore
- Glossary terms: notebook template

### AI implementation contract

- **required_context:** Requires agreement metadata created through 01_agreement and metadata routing from 00_env_config.
- **inputs:** config, env, optional spark_session, and notebook registration options for loading agreement choices from metadata.
- **output:** Interactive widget state; call get_selected_agreement to retrieve the selected agreement record.
- **side_effects:** Displays an IPython widget and may register the active notebook selection in metadata when requested.
- **failure_modes:** Raises metadata read, widget dependency, or configuration errors when agreement metadata cannot be loaded.
- **verification:** Verify the user selected an agreement and call get_selected_agreement before generating pipeline code that depends on agreement context.

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.data_agreement._html_escape`
- `fabricops_kit.data_agreement._latest_agreement_versions`
- `fabricops_kit.data_agreement._list_data_agreements`
- `fabricops_kit.data_agreement._render_searchable_selector`
- `fabricops_kit.data_agreement._require_ipywidgets`
- `fabricops_kit.metadata._current_notebook_active_registrations`
- `fabricops_kit.metadata._register_current_notebook`

### Raw source metadata

- Source file path: `src/fabricops_kit/data_agreement.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/data_agreement.py#L773-L997">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/1dc3c45d105de76dbe2c564d1e04e78d550eac95/src/fabricops_kit/data_agreement.py#L773-L997</a>
- Start line: `773`
- End line: `997`
- Signature:

```python
def widget_select_agreement(agreement_rows_or_config: Any, env_name: str | None=None, *, spark_session: Any=None, register_notebook: bool=False, notebook_type: str | None=None, environment_name: str | None=None, dataset_name: str | None=None, table_name: str | None=None, topic: str | None=None, pipeline_name: str | None=None) -> Any
```

### Internal relationship graph

### Public related functions

- <a href="../get_selected_agreement/"><code>fabricops_kit.data_agreement.get_selected_agreement</code></a>
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

### Internal implementation summary

- Internal helper count: 22
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
