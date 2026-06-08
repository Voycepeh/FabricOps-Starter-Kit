# widget_select_agreement

Render an agreement selector and optionally register the active notebook.

## What this is for and when to use it

Render an agreement selector and optionally register the active notebook.

- Use in 02_pipeline or 99_explore notebooks to let a user select an approved data agreement before reading, profiling, or writing governed data.

## When not to use it

- Do not use when an agreement has already been programmatically selected and validated, or for catalogue table review selection in 03_governance.

## Example

```python
widget_select_agreement(CONFIG, env="Sandbox", spark_session=spark)
agreement = get_selected_agreement()
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
      <td data-label="Parameter"><code>agreement_rows_or_config</code></td>
      <td data-label="Required">Yes</td>
      <td data-label="Meaning">Pass ``CONFIG`` in normal notebooks, or provide preloaded agreement rows when the caller already has them available.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>env_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Environment key used to load agreements when ``CONFIG`` is supplied.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>spark_session</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Fabric Spark session used for configured metadata-table reads.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>register_notebook</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">When True, render registration status and a button that links the current notebook to the selected agreement.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>notebook_type</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Workflow metadata passed to ``_register_current_notebook`` when ``register_notebook`` is enabled.</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>environment_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>dataset_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>table_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>topic</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
    <tr>
      <td data-label="Parameter"><code>pipeline_name</code></td>
      <td data-label="Required">No</td>
      <td data-label="Meaning">Not documented yet</td>
    </tr>
  </tbody>
</table>
</div>

## Output

Interactive widget state; call get_selected_agreement to retrieve the selected agreement record.

## Errors and side effects

**Errors:** Raises metadata read, widget dependency, or configuration errors when agreement metadata cannot be loaded.

**Side effects:** Displays an IPython widget and may register the active notebook selection in metadata when requested.

## Related functions

- <a href="../get_selected_agreement/"><code>fabricops_kit.data_agreement.get_selected_agreement</code></a>
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

<details class="reference-implementation-details">
<summary>Implementation details</summary>

- <a href="../internal/data_agreement__html_escape/"><code>fabricops_kit.data_agreement._html_escape</code></a>
- <a href="../internal/data_agreement__latest_agreement_versions/"><code>fabricops_kit.data_agreement._latest_agreement_versions</code></a>
- <a href="../internal/data_agreement__list_data_agreements/"><code>fabricops_kit.data_agreement._list_data_agreements</code></a>
- <a href="../internal/data_agreement__render_searchable_selector/"><code>fabricops_kit.data_agreement._render_searchable_selector</code></a>
- <a href="../internal/data_agreement__require_ipywidgets/"><code>fabricops_kit.data_agreement._require_ipywidgets</code></a>
- <a href="../internal/metadata__current_notebook_active_registrations/"><code>fabricops_kit.metadata._current_notebook_active_registrations</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>

</details>

## Source

- Source file path: `src/fabricops_kit/data_agreement.py`
- <a class="reference-source-link" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c7049e78d915b93903574ea792043a66ebe62cee/src/fabricops_kit/data_agreement.py#L856-L1080">View widget_select_agreement on GitHub</a>

<details class="reference-source-details">
<summary>Show source code</summary>

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
                superseded_at = datetime.now(timezone.utc).isoformat()
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

</details>

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
- Source line: `856`
- Inbound references count: 0
- Outbound references count: 7

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

- <a href="../internal/data_agreement__html_escape/"><code>fabricops_kit.data_agreement._html_escape</code></a>
- <a href="../internal/data_agreement__latest_agreement_versions/"><code>fabricops_kit.data_agreement._latest_agreement_versions</code></a>
- <a href="../internal/data_agreement__list_data_agreements/"><code>fabricops_kit.data_agreement._list_data_agreements</code></a>
- <a href="../internal/data_agreement__render_searchable_selector/"><code>fabricops_kit.data_agreement._render_searchable_selector</code></a>
- <a href="../internal/data_agreement__require_ipywidgets/"><code>fabricops_kit.data_agreement._require_ipywidgets</code></a>
- <a href="../internal/metadata__current_notebook_active_registrations/"><code>fabricops_kit.metadata._current_notebook_active_registrations</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>

### Raw source metadata

- Source file path: `src/fabricops_kit/data_agreement.py`
- GitHub source URL: <a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c7049e78d915b93903574ea792043a66ebe62cee/src/fabricops_kit/data_agreement.py#L856-L1080">https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/c7049e78d915b93903574ea792043a66ebe62cee/src/fabricops_kit/data_agreement.py#L856-L1080</a>
- Start line: `856`
- End line: `1080`
- Signature:

```python
def widget_select_agreement(agreement_rows_or_config: Any, env_name: str | None=None, *, spark_session: Any=None, register_notebook: bool=False, notebook_type: str | None=None, environment_name: str | None=None, dataset_name: str | None=None, table_name: str | None=None, topic: str | None=None, pipeline_name: str | None=None) -> Any
```

### Internal relationship graph

### Public related functions

- <a href="../get_selected_agreement/"><code>fabricops_kit.data_agreement.get_selected_agreement</code></a>
- <a href="../setup_metadata_tables/"><code>fabricops_kit.config.setup_metadata_tables</code></a>

### Internal implementation helpers

- <a href="../internal/data_agreement__html_escape/"><code>fabricops_kit.data_agreement._html_escape</code></a>
- <a href="../internal/data_agreement__latest_agreement_versions/"><code>fabricops_kit.data_agreement._latest_agreement_versions</code></a>
- <a href="../internal/data_agreement__list_data_agreements/"><code>fabricops_kit.data_agreement._list_data_agreements</code></a>
- <a href="../internal/data_agreement__render_searchable_selector/"><code>fabricops_kit.data_agreement._render_searchable_selector</code></a>
- <a href="../internal/data_agreement__require_ipywidgets/"><code>fabricops_kit.data_agreement._require_ipywidgets</code></a>
- <a href="../internal/metadata__current_notebook_active_registrations/"><code>fabricops_kit.metadata._current_notebook_active_registrations</code></a>
- <a href="../internal/metadata__register_current_notebook/"><code>fabricops_kit.metadata._register_current_notebook</code></a>

</details>
