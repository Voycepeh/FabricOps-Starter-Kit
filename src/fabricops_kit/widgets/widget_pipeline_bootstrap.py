"""Pipeline bootstrap widget for guided pipeline notebook workflows."""

from __future__ import annotations

from typing import Any, Mapping
from uuid import uuid4

from fabricops_kit.config.shared import get_current_audit_timestamp, resolve_fabric_context
from fabricops_kit.metadata import current_notebook_active_registrations, register_current_notebook
from fabricops_kit.widgets.shared import (
    set_selected_agreement,
    PipelineRunContext,
    get_selected_agreement,
    latest_agreement_versions,
    list_data_agreements,
    render_searchable_selector,
    require_ipywidgets,
    set_active_pipeline_context,
)


def widget_pipeline_bootstrap(
    *,
    notebook_type: str = "02_pipeline",
    select_agreement: bool = False,
    register_notebook: bool = False,
    read_only: bool = False,
    run_context: Any = None,
    spark_session: Any = None,
    metadata_schema: str | None = None,
    pipeline_name: str | None = None,
    context: dict[str, Any] | None = None,
) -> Any:
    """Bootstrap a guided pipeline notebook run and store runtime defaults.

    Parameters
    ----------
    notebook_type : str, default="02_pipeline"
        FabricOps notebook type to associate with the active context.
    select_agreement : bool, default=False
        When True, render the agreement selector and capture the selected
        agreement for downstream defaults.
    register_notebook : bool, default=False
        When True, allow the agreement selector to register this notebook
        to the selected agreement. Use ``False`` for read-only exploration.
    read_only : bool, default=False
        Marks the active context as read-only for exploratory notebooks. The
        startup helper itself does not write metadata unless
        ``register_notebook=True`` is explicitly requested.
    run_context : object, optional
        ``RUN_CONTEXT`` from ``00_env_config``. Defaults to the active notebook
        variable named ``RUN_CONTEXT``.
    spark_session : Any, optional
        Spark session. Defaults to the active notebook variable named ``spark``.
    metadata_schema : str, optional
        ``METADATA_SCHEMA`` from ``00_env_config`` when schema routing is used.
    pipeline_name : str, optional
        Friendly pipeline name. Defaults to Fabric runtime notebook metadata.
    context : dict, optional
        Advanced FabricOps context override.

    Returns
    -------
    Any
        Pipeline runtime context object with resolved runtime defaults. Most notebooks
        use it only as ``PIPELINE`` for ``run_id`` and ``pipeline_name`` when
        preparing target configs or lineage. The concrete context class is
        intentionally internal and not part of the primary public API.

    Notes
    -----
    This helper keeps template code concise while preserving explicit lower-level
    parameters on guardrail and summary helpers for advanced notebooks.

    """
    return _widget_pipeline_bootstrap_workflow(
        notebook_type=notebook_type,
        select_agreement=select_agreement,
        register_notebook=register_notebook,
        read_only=read_only,
        run_context=run_context,
        spark_session=spark_session,
        metadata_schema=metadata_schema,
        pipeline_name=pipeline_name,
        context=context,
    )


# ---------------------------------------------------------------------------
# Internal model and run-state resolver layer
# ---------------------------------------------------------------------------


def _widget_pipeline_bootstrap_workflow(
    *,
    notebook_type: str = "02_pipeline",
    select_agreement: bool = False,
    register_notebook: bool = False,
    read_only: bool = False,
    run_context: Any = None,
    spark_session: Any = None,
    metadata_schema: str | None = None,
    pipeline_name: str | None = None,
    context: dict[str, Any] | None = None,
) -> Any:
    """Start a guided notebook run and store runtime defaults.

    Parameters
    ----------
    notebook_type : str, default="02_pipeline"
        FabricOps notebook type to associate with the active context.
    select_agreement : bool, default=False
        When True, render the agreement selector and capture the selected
        agreement for downstream defaults.
    register_notebook : bool, default=False
        When True, allow the agreement selector to register this notebook
        to the selected agreement. Use ``False`` for read-only exploration.
    read_only : bool, default=False
        Marks the active context as read-only for exploratory notebooks. The
        startup helper itself does not write metadata unless
        ``register_notebook=True`` is explicitly requested.
    run_context : object, optional
        ``RUN_CONTEXT`` from ``00_env_config``. Defaults to the active notebook
        variable named ``RUN_CONTEXT``.
    spark_session : Any, optional
        Spark session. Defaults to the active notebook variable named ``spark``.
    metadata_schema : str, optional
        ``METADATA_SCHEMA`` from ``00_env_config`` when schema routing is used.
    pipeline_name : str, optional
        Friendly pipeline name. Defaults to Fabric runtime notebook metadata.
    context : dict, optional
        Advanced FabricOps context override.

    Returns
    -------
    Any
        Internal context object with resolved runtime defaults. Most notebooks
        use it only as ``PIPELINE`` for ``run_id`` and ``pipeline_name`` when
        preparing target configs or lineage. The concrete context class is
        intentionally internal and not part of the primary public API.

    Notes
    -----
    This helper keeps template code concise while preserving explicit lower-level
    parameters on guardrail and summary helpers for advanced notebooks.

    """
    if run_context is None or spark_session is None or metadata_schema is None:
        try:
            ip = get_ipython()  # type: ignore[name-defined]
        except Exception:
            user_ns = {}
        else:
            user_ns = getattr(ip, "user_ns", {}) if ip is not None else {}
        run_context = run_context if run_context is not None else user_ns.get("RUN_CONTEXT")
        spark_session = spark_session if spark_session is not None else user_ns.get("spark")
        schema = metadata_schema if metadata_schema is not None else user_ns.get("METADATA_SCHEMA", "")
    else:
        schema = metadata_schema
    runtime_metadata = getattr(run_context, "runtime_metadata", {}) or {}
    if not isinstance(runtime_metadata, Mapping):
        runtime_metadata = {}
    resolved_pipeline_name = str(pipeline_name or runtime_metadata.get("currentNotebookName") or notebook_type)
    active = PipelineRunContext(
        run_id=str(getattr(run_context, "run_id", "") or uuid4()),
        pipeline_started_at=get_current_audit_timestamp(),
        pipeline_name=resolved_pipeline_name,
        spark_session=spark_session,
        metadata_schema=str(schema or ""),
        notebook_type=str(notebook_type or "02_pipeline"),
        notebook_id=str(runtime_metadata.get("currentNotebookId") or ""),
        context=context,
        read_only=bool(read_only),
    )
    set_active_pipeline_context(active)

    if select_agreement:
        _render_bootstrap_agreement_selector(
            spark_session=active.spark_session,
            metadata_schema=active.metadata_schema or None,
            register_notebook=register_notebook,
            notebook_type=active.notebook_type,
            pipeline_name=active.pipeline_name,
            context=active.context,
        )
        agreement = get_selected_agreement()
        active.agreement = dict(agreement)
        active.agreement_id = str(agreement.get("agreement_id", ""))
        active.agreement_contract_version = str(
            agreement.get("agreement_contract_version", agreement.get("contract_version", ""))
        )
        active.notebook_registry_id = str(agreement.get("notebook_registry_id", agreement.get("registration_id", "")))
        active.notebook_id = str(agreement.get("notebook_id", active.notebook_id))

    return active



def _html_escape(value: Any) -> str:
    """Return display-safe HTML text for notebook status snippets."""
    import html

    return html.escape(str(value or ""))




def _render_bootstrap_agreement_selector(agreement_rows: Any = None, *, context: dict[str, Any] | None = None, spark_session: Any = None, metadata_schema: str | None = None, register_notebook: bool = False, notebook_type: str | None = None, environment_name: str | None = None, dataset_name: str | None = None, table_name: str | None = None, topic: str | None = None, pipeline_name: str | None = None) -> Any:
    """Render the bootstrap-owned agreement selector workflow and retain the selected row.

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
            raise ValueError("widget_pipeline_bootstrap(..., register_notebook=True) requires an active FABRIC_CONTEXT or context override plus spark_session.")
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

