"""Private widget workflow for selecting a data agreement."""

from __future__ import annotations

from typing import Any

from fabricops_kit.agreement_selection_state import set_selected_agreement
from fabricops_kit.config.shared import get_current_audit_timestamp, resolve_fabric_context
from fabricops_kit.metadata import current_notebook_active_registrations, register_current_notebook
from fabricops_kit.widgets.shared import latest_agreement_versions, list_data_agreements, render_searchable_selector, require_ipywidgets




def _html_escape(value: Any) -> str:
    """Return display-safe HTML text for notebook status snippets."""
    import html

    return html.escape(str(value or ""))




def _select_agreement_widget_workflow(agreement_rows: Any = None, *, context: dict[str, Any] | None = None, spark_session: Any = None, metadata_schema: str | None = None, register_notebook: bool = False, notebook_type: str | None = None, environment_name: str | None = None, dataset_name: str | None = None, table_name: str | None = None, topic: str | None = None, pipeline_name: str | None = None) -> Any:
    """Render the downstream agreement selector workflow and retain the selected row.

    Parameters
    ----------
    agreement_rows : iterable, optional
        Preloaded agreement rows. When omitted, agreements are loaded from the
        active ``FABRIC_CONTEXT`` initialized by ``00_env_config``.
    context : dict, optional
        Advanced override context. Defaults to the active ``FABRIC_CONTEXT``.
    spark_session : pyspark.sql.SparkSession, optional
        Fabric Spark session used for configured metadata-table reads.
    metadata_schema : str, optional
        Explicit metadata Lakehouse schema override. Pass ``METADATA_SCHEMA``
        from ``00_env_config`` in schema-enabled Lakehouses so agreement reads
        and notebook registration use the same metadata route.
    register_notebook : bool, default=False
        When True, render registration status and a button that links the
        current notebook to the selected agreement.
    notebook_type, environment_name, dataset_name, table_name, topic, pipeline_name : str, optional
        Workflow metadata passed to ``register_current_notebook`` when
        ``register_notebook`` is enabled.

    Returns
    -------
    ipywidgets.Select
        Displayed searchable latest-version agreement selector control. Its
        ``value`` remains the stable ``agreement_id`` for existing callers.
        When registration is enabled, registration widgets are attached as
        attributes on the selector for advanced notebook automation.

    """
    widgets = require_ipywidgets()
    from IPython import display as ip

    config = None
    env = None
    if agreement_rows is None:
        config, env, _context = resolve_fabric_context(context=context)
        try:
            rows = list_data_agreements(config, env, spark_session=spark_session, metadata_schema=metadata_schema)
        except Exception as exc:
            raise RuntimeError("No agreements found. Run 01_agreement first.") from exc
    else:
        rows = agreement_rows
        if register_notebook:
            config, env, _context = resolve_fabric_context(context=context)
    latest_rows = latest_agreement_versions(rows)
    if not latest_rows:
        raise ValueError("No agreements found. Save a data agreement in notebook 01_agreement first.")
    rows_by_id = {str(row.get("agreement_id") or "").strip(): row for row in latest_rows if str(row.get("agreement_id") or "").strip()}

    def _agreement_label(row: dict[str, Any]) -> str:
        agreement_id = str(row.get("agreement_id") or "").strip()
        return f"{row.get('agreement_name', '') or agreement_id} ({agreement_id} / v{row.get('contract_version', '')})"

    selector_parts = render_searchable_selector(
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
        if change.get("name") == "value" and change.get("new") is not None:
            selected_row = rows_by_id.get(str(change["new"]))
            if selected_row is not None:
                set_selected_agreement(selected_row)

    selector.observe(_on_change, names="value")
    if selector.value in rows_by_id:
        set_selected_agreement(rows_by_id[str(selector.value)])
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
        if config is None or env is None or spark_session is None:
            raise ValueError("widget_select_agreement(..., register_notebook=True) requires an active FABRIC_CONTEXT or context override plus spark_session.")
        active_rows = current_notebook_active_registrations(
            spark_session,
            config=config,
            env=env,
            metadata_schema=metadata_schema,
            notebook_type=notebook_type,
            environment_name=environment_name or env,
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

            new_row = register_current_notebook(
                spark_session,
                config=config,
                env=env,
                agreement_id=selected_id,
                contract_version=selected_version,
                registration_role=role,
                registration_status="active",
                metadata_schema=metadata_schema,
                notebook_type=notebook_type,
                environment_name=environment_name or env,
                dataset_name=dataset_name,
                table_name=table_name,
                topic=topic,
                pipeline_name=pipeline_name,
            )
            if other and role == "primary":
                superseded_at = get_current_audit_timestamp(config=config, drop_microseconds=False)
                for previous in other:
                    register_current_notebook(
                        spark_session,
                        config=config,
                        env=env,
                        agreement_id=previous.get("agreement_id"),
                        contract_version=previous.get("agreement_contract_version"),
                        registration_role=previous.get("registration_role") or "primary",
                        registration_status="superseded",
                        metadata_schema=metadata_schema,
                        registration_id=previous.get("registration_id"),
                        superseded_at=superseded_at,
                        superseded_by_registration_id=new_row.get("registration_id"),
                        notebook_type=previous.get("notebook_type") or notebook_type,
                        environment_name=previous.get("environment_name") or environment_name or env,
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

