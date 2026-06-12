# widget_render_agreement_evidence

Render the standalone agreement-evidence widget.

## Purpose

Render the standalone agreement-evidence widget.

## At a glance

### Used in templates

- `01_agreement`

**Use when:**

- Render the standalone agreement-evidence widget.

**Do not use when:**

- Not documented yet

**Example:**

```python
Not documented yet
```

**Errors:**

Not documented yet

**Side effects:**

Not documented yet

## Used by

Not documented yet

## Calls

- `fabricops_kit.data_agreement._render_agreement_evidence_widget`

## Callable implementation

### Function details

- Module: `data_agreement`
- Classification: Callable
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `1379`
- Signature:

```python
def widget_render_agreement_evidence(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]
```

### Parameters

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
      <td data-label="Meaning">Configuration containing agreement metadata routing and evidence table settings.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env_name</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Environment key configured by ``00_env_config``.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Fabric Spark session used for metadata reads, file writes, and append-only evidence metadata writes.</td>
    </tr>
  </tbody>
</table>
</div>

### Returns

dict[str, Any]
    Rendered controls for selecting an agreement version, pasting
    metadata lakehouse evidence file paths, refreshing agreement options,
    and saving evidence metadata rows.

### Notes

This public wrapper is intended for the separate-widget ``01_agreement`` layout.
Evidence files must be uploaded manually to the metadata lakehouse
``Files`` area first. The widget appends one file-reference row per
pasted ``Files/...`` path to ``METADATA_DATA_AGREEMENT_EVIDENCE`` and
does not read or write binary file content.

### Public callable source code

- Source file path: `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L1379-L1412">View widget_render_agreement_evidence on GitHub</a>

```python
def widget_render_agreement_evidence(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]:
    """Render standalone agreement evidence upload controls.

    Parameters
    ----------
    config : FrameworkConfig or dict
        Configuration containing agreement metadata routing and evidence table
        settings.
    env_name : str
        Environment key configured by ``00_env_config``.
    spark : pyspark.sql.SparkSession
        Fabric Spark session used for metadata reads, file writes, and
        append-only evidence metadata writes.

    Returns
    -------
    dict[str, Any]
        Rendered controls for selecting an agreement version, pasting
        metadata lakehouse evidence file paths, refreshing agreement options,
        and saving evidence metadata rows.

    Notes
    -----
    This public wrapper is intended for the separate-widget ``01_agreement`` layout.
    Evidence files must be uploaded manually to the metadata lakehouse
    ``Files`` area first. The widget appends one file-reference row per
    pasted ``Files/...`` path to ``METADATA_DATA_AGREEMENT_EVIDENCE`` and
    does not read or write binary file content.
    """
    return _render_agreement_evidence_widget(
        spark=spark,
        config=config,
        env_name=env_name,
    )
```

## Internal implementation summary

??? info "Call flow"

    Large call graph shown to two levels.

    Expanded internal helper tree is available in the internal implementation summary.

    ```text
    widget_render_agreement_evidence(...)
    └── _render_agreement_evidence_widget(...)
        ├── _list_all_data_agreement_rows(...)
        │   └── …
        ├── _render_searchable_selector(...)
        │   └── …
        ├── _require_ipywidgets(...)
        ├── _save_agreement_evidence_records(...)
        │   └── …
        └── _widget_common(...)
    ```

??? info "Internal helpers used: 19"

    This callable uses 19 internal helpers for audit timestamp, metadata loading, validation, fabric or spark access, and other.

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
          <td data-label="Helpers"><code>_build_runtime_audit_fields</code>, <code>_current_audit_timestamp</code>, <code>_get_audit_timezone</code>, <code>_validate_audit_timezone</code></td>
          <td data-label="What they do">Resolve and stamp audit time consistently.</td>
        </tr>
        <tr>
          <td data-label="Area">Metadata loading</td>
          <td data-label="Helpers"><code>_list_all_data_agreement_rows</code>, <code>_render_agreement_evidence_widget</code>, <code>_render_searchable_selector</code>, <code>_save_agreement_evidence_records</code></td>
          <td data-label="What they do">Load and identify the metadata or table context needed by the callable.</td>
        </tr>
        <tr>
          <td data-label="Area">Validation</td>
          <td data-label="Helpers"><code>_prepare_evidence_file_references</code></td>
          <td data-label="What they do">Validate inputs and guard conditions before the workflow continues.</td>
        </tr>
        <tr>
          <td data-label="Area">Fabric or Spark access</td>
          <td data-label="Helpers"><code>_get_notebookutils</code></td>
          <td data-label="What they do">Access Fabric or Spark runtime services used by the implementation.</td>
        </tr>
        <tr>
          <td data-label="Area">Other</td>
          <td data-label="Helpers"><code>_coerce_row_dicts</code>, <code>_config_value</code>, <code>_context_get</code>, <code>_html_escape</code>, <code>_require_ipywidgets</code>, <code>_runtime_context</code>, <code>_safe_str</code>, <code>_widget_common</code>, <code>_write_row</code></td>
          <td data-label="What they do">Support lower-level implementation details that do not fit the main helper areas.</td>
        </tr>
      </tbody>
    </table>
    </div>

    ??? example "View helper source by area"

        ??? example "Audit timestamp helpers"

            **`def _build_runtime_audit_fields(*, config: Any=None, env: str | None=None, timestamp_field: str='_committed_at', user_field: str='_committed_by', workspace_field: str='_workspace_name', notebook_field: str='_notebook_name', metadata_lakehouse_field: str='_metadata_lakehouse_name', activity_field: str='_activity_id', committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> dict[str, str]`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/metadata.py#L147-L217)

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

            **`def _current_audit_timestamp(config: Any=None, timezone_name: str | None=None, *, drop_microseconds: bool=True) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/config.py#L69-L75)

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

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/config.py#L61-L66)

            ```python
            def _get_audit_timezone(config: Any = None, timezone_name: str | None = None) -> str:
                """Resolve the configured FabricOps audit timezone, defaulting to UTC."""
                if timezone_name is not None:
                    return _validate_audit_timezone(timezone_name)
                value = getattr(config, "audit_timezone", None) if config is not None else None
                return _validate_audit_timezone(value)
            ```

            **`def _validate_audit_timezone(timezone_name: str | None) -> str`**

            Source: [`src/fabricops_kit/config.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/config.py#L27-L58)

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

            **`def _list_all_data_agreement_rows(config: Any, env_name: str, *, spark_session: Any=None, missing_ok: bool=False) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L589-L598)

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

            **`def _render_agreement_evidence_widget(*, spark: Any, config: Any, env_name: str, display_widget: bool=True) -> dict[str, Any]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L1258-L1376)

            ```python
            def _render_agreement_evidence_widget(*, spark: Any, config: Any, env_name: str, display_widget: bool = True) -> dict[str, Any]:
                """Render optional agreement evidence upload controls."""
                widgets = _require_ipywidgets()
                from IPython import display as ip

                row_lookup: dict[str, dict[str, Any]] = {}

                def _agreement_rows() -> list[dict[str, Any]]:
                    return _list_all_data_agreement_rows(config, env_name, spark_session=spark, missing_ok=True)

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
                evidence_type = widgets.Dropdown(options=[(item, item) for item in AGREEMENT_EVIDENCE_TYPES], **_widget_common(widgets, "Evidence Type"))
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
                            rows = _save_agreement_evidence_records(
                                spark=spark,
                                config=config,
                                env_name=env_name,
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
            ```

            **`def _render_searchable_selector(*, widgets: Any, label: str, rows: list[dict[str, Any]], label_fn: Callable[[dict[str, Any]], str], value_fn: Callable[[dict[str, Any]], str], placeholder: str='Search...', max_results: int=25, search_fields: list[str] | None=None, context_fields: list[tuple[str, str]] | None=None, empty_label: str | None=None, selected_value: str | None=None) -> dict[str, Any]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L198-L308)

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

            **`def _save_agreement_evidence_records(*, spark: Any, config: Any, env_name: str, agreement_id: str, contract_version: str, evidence_type: str, evidence_file_paths: Any, committed_by: str | None=None, committed_at: str | None=None, runtime_context: dict[str, Any] | None=None) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L739-L770)

            ```python
            def _save_agreement_evidence_records(*, spark: Any, config: Any, env_name: str, agreement_id: str, contract_version: str, evidence_type: str, evidence_file_paths: Any, committed_by: str | None = None, committed_at: str | None = None, runtime_context: dict[str, Any] | None = None) -> list[dict[str, Any]]:
                """Append manually uploaded evidence file-reference metadata rows."""
                agreement_id = str(agreement_id or "").strip()
                contract_version = str(contract_version or "").strip()
                if not agreement_id:
                    raise ValueError("agreement_id is required before saving agreement evidence.")
                if not contract_version:
                    raise ValueError("contract_version is required before saving agreement evidence.")
                evidence_type = str(evidence_type or "Other").strip() or "Other"
                file_references = _prepare_evidence_file_references(evidence_file_paths)
                audit = _build_runtime_audit_fields(config=config, env=env_name, committed_by=committed_by, committed_at=committed_at, runtime_context=runtime_context)
                uploaded_at = audit.get("_committed_at") or _current_audit_timestamp(config=config, drop_microseconds=False)
                uploaded_by = audit.get("_committed_by") or ""

                metadata_tables = _config_value(config, "metadata_tables", {}) or {}
                rows: list[dict[str, Any]] = []
                for reference in file_references:
                    row = {
                        "agreement_id": agreement_id,
                        "contract_version": contract_version,
                        "evidence_type": evidence_type,
                        "file_name": reference["file_name"],
                        "file_path": reference["file_path"],
                        "mime_type": reference["mime_type"],
                        "file_size": reference["file_size"],
                        "uploaded_at": uploaded_at,
                        "uploaded_by": uploaded_by,
                        **audit,
                    }
                    _write_row(spark=spark, config=config, env_name=env_name, table=str(metadata_tables.get("data_agreement_evidence", DATA_AGREEMENT_EVIDENCE_TABLE)), row=row)
                    rows.append(row)
                return rows
            ```

        ??? example "Validation helpers"

            **`def _prepare_evidence_file_references(paths_value: Any) -> list[dict[str, str]]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L687-L737)

            ```python
            def _prepare_evidence_file_references(paths_value: Any) -> list[dict[str, str]]:
                """Parse and validate manually supplied evidence file paths before writes."""
                utils = _get_notebookutils()
                fs = getattr(utils, "fs", None) if utils is not None else None
                exists = getattr(fs, "exists", None) if fs is not None else None
                list_dir = getattr(fs, "ls", None) if fs is not None else None

                references: list[dict[str, str]] = []
                for raw_line in str(paths_value or "").splitlines():
                    path = re.sub(r"^(?:[-*]\s*|\d+\.\s*)", "", raw_line.strip()).strip()
                    if not path:
                        continue
                    if not path.startswith("Files/"):
                        raise ValueError(f"Evidence file path must start with Files/: {path}")

                    file_name = path.replace("\\", "/").rsplit("/", 1)[-1].strip()
                    if not file_name:
                        raise ValueError(f"Evidence file path must include a file name: {path}")
                    suffix = "." + file_name.rsplit(".", 1)[-1].lower() if "." in file_name else ""
                    if suffix not in AGREEMENT_EVIDENCE_ALLOWED_EXTENSIONS:
                        allowed = ", ".join(AGREEMENT_EVIDENCE_ALLOWED_EXTENSIONS)
                        raise ValueError(f"Unsupported evidence file type for {path}. Allowed types: {allowed}.")
                    if callable(exists) and not bool(exists(path)):
                        raise ValueError(f"Evidence file path does not exist: {path}")

                    file_size = ""
                    if callable(list_dir):
                        normalized = path.rstrip("/")
                        parent = normalized.rsplit("/", 1)[0] if "/" in normalized else ""
                        try:
                            items = list_dir(parent)
                        except Exception:
                            items = []
                        for item in items:
                            item_path = str(getattr(item, "path", "") or getattr(item, "name", "") or "")
                            item_name = item_path.rstrip("/").rsplit("/", 1)[-1]
                            if item_path.rstrip("/") == normalized or item_name == file_name:
                                size = getattr(item, "size", "")
                                file_size = "" if size is None else str(size)
                                break

                    references.append({
                        "file_name": file_name,
                        "file_path": path,
                        "mime_type": AGREEMENT_EVIDENCE_MIME_TYPES.get(suffix, ""),
                        "file_size": file_size,
                    })

                if not references:
                    raise ValueError("Paste at least one evidence file path before saving.")
                return references
            ```

        ??? example "Fabric or Spark access helpers"

            **`def _get_notebookutils() -> Any`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L675-L684)

            ```python
            def _get_notebookutils() -> Any:
                """Return a notebookutils-like object when the Fabric runtime exposes one."""
                candidate = globals().get("notebookutils")
                if candidate is not None:
                    return candidate
                for module_name in ("notebookutils", "mssparkutils"):
                    candidate = sys.modules.get(module_name)
                    if candidate is not None:
                        return candidate
                return None
            ```

        ??? example "Other helpers"

            **`def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L397-L402)

            ```python
            def _coerce_row_dicts(rows: Any) -> list[dict[str, Any]]:
                if rows is None:
                    return []
                if hasattr(rows, "collect"):
                    rows = rows.collect()
                return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in rows]
            ```

            **`def _config_value(config: Any, name: str, default: Any) -> Any`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L149-L153)

            ```python
            def _config_value(config: Any, name: str, default: Any) -> Any:
                agreement_config = getattr(config, "data_agreement_config", config)
                if isinstance(agreement_config, dict):
                    return agreement_config.get(name, default)
                return getattr(agreement_config, name, default)
            ```

            **`def _context_get(context: Any, *keys: str) -> Any`**

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/metadata.py#L101-L113)

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

            **`def _html_escape(value: Any) -> str`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L192-L195)

            ```python
            def _html_escape(value: Any) -> str:
                """Return display-safe HTML text for notebook context snippets."""
                import html
                return html.escape(str(value or ""))
            ```

            **`def _require_ipywidgets()`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L63-L72)

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

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/metadata.py#L120-L144)

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

            Source: [`src/fabricops_kit/metadata.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/metadata.py#L116-L117)

            ```python
            def _safe_str(value: Any) -> str:
                return "" if value is None else str(value)
            ```

            **`def _widget_common(widgets_module: Any, description: str, *, textarea: bool=False) -> dict[str, Any]`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L180-L189)

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

            **`def _write_row(*, spark: Any, config: Any, env_name: str, table: str, row: dict[str, Any]) -> None`**

            Source: [`src/fabricops_kit/data_agreement.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L485-L486)

            ```python
            def _write_row(*, spark: Any, config: Any, env_name: str, table: str, row: dict[str, Any]) -> None:
                write_lakehouse_table(spark.createDataFrame([row]), config, env_name, "metadata", table, mode="append")
            ```


<details class="reference-metadata-details">
<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>

These generated fields are for automation, AI agents, maintainers, and doc tooling. Skip this block when reading the docs normally.

### Function manifest

- Fully qualified function name: `fabricops_kit.data_agreement.widget_render_agreement_evidence`
- Short name: `widget_render_agreement_evidence`
- Module: `data_agreement`
- Classification: Callable
- Related module: `data_agreement`
- Source file path: `src/fabricops_kit/data_agreement.py`
- Source line: `1379`
- Inbound references count: 0
- Outbound references count: 1
- Used in templates: 01_agreement

### AI implementation contract

- **required_context:** Starter template: `01_agreement`; segment: `Agreement intake`.
- **inputs:** config : FrameworkConfig or dict
    Configuration containing agreement metadata routing and evidence table
    settings.
env_name : str
    Environment key configured by ``00_env_config``.
spark : pyspark.sql.SparkSession
    Fabric Spark session used for metadata reads, file writes, and
    append-only evidence metadata writes.
- **output:** dict[str, Any]
    Rendered controls for selecting an agreement version, pasting
    metadata lakehouse evidence file paths, refreshing agreement options,
    and saving evidence metadata rows.
- **side_effects:** Not documented yet
- **failure_modes:** Not documented yet
- **verification:** Not documented yet

### Inbound references

Not documented yet

### Outbound references

- `fabricops_kit.data_agreement._render_agreement_evidence_widget`

### Raw source metadata

- Source file path: `src/fabricops_kit/data_agreement.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L1379-L1412">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/f39132033d0795937707ff6bec4d4f7a90c42957/src/fabricops_kit/data_agreement.py#L1379-L1412</a>
- Start line: `1379`
- End line: `1412`
- Signature:

```python
def widget_render_agreement_evidence(config: Any, env_name: str, *, spark: Any) -> dict[str, Any]
```

### Internal relationship graph

### Public related functions

Not documented yet

### Internal implementation summary

- Internal helper count: 19
- Grouped helper summary and optional source snippets are rendered in the page-level Internal implementation summary section.

</details>
