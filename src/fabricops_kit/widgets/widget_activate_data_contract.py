"""Review and activate a frozen Contract in its physical table workspace."""
from __future__ import annotations

import html
import hashlib
import json
from uuid import uuid4

from fabricops_kit.activated_pipeline.shared import read_activations, set_table_contract_activation
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.widgets import shared


def widget_activate_data_contract(table_id: str, contract_id: str, contract_version: int, *,
                                  workspace_id: str | None = None, context=None) -> dict:
    """Review the frozen definition and explicitly activate it independently of pipelines.

    Parameters
    ----------
    table_id, contract_id : str
        Exact logical table and frozen Contract identity.
    contract_version : int
        Exact positive frozen version.
    workspace_id : str | None, optional
        Physical table workspace to review; defaults to the configured scope.
        Use this when reviewing Engineering tables from the Governance notebook.
    context : dict | None, optional
        Configured notebook context; central Metadata routing is preserved.

    Returns
    -------
    dict
        Widget, state, confirmation control and activation action. Opening the
        widget changes no metadata. Stale review is rejected atomically.

    Raises
    ------
    ValueError
        If the exact frozen Contract, workspace or activation is ambiguous.
    RuntimeError
        If configured metadata, Spark or widgets are unavailable.

    Notes
    -----
    Actual storage permissions authorize activation. The confirmation checkbox
    grants no access. Ungoverned writes to the physical table and aliases become
    protected; Pipeline Promotion remains a separate decision.

    Examples
    --------
    >>> ui = widget_activate_data_contract(TABLE_ID, CONTRACT_ID, 1)

    """
    from fabricops_kit.activated_pipeline.shared import metadata_records, exact_record
    from fabricops_kit.pipeline.shared import resolve_catalogue_table_identity, pipeline_physical_bindings
    startup = shared.WidgetStartup("Data Contract Activation", tone="governance", reserved_height="560px")
    config, workspace, runtime = resolve_fabric_context(context=context)
    metadata_workspace = runtime.get("metadata_workspace_id") or workspace
    workspace = workspace if workspace_id is None else str(workspace_id).strip()
    if not workspace:
        raise ValueError("workspace_id must be nonblank.")
    routed = {**runtime, "config": config, "scope_workspace_id": workspace, "metadata_workspace_id": metadata_workspace}
    spark = get_spark_session(context=runtime)
    with startup.phase("metadata_loading", "Loading the frozen Contract and exact physical table binding…"):
        current = [row for row in read_activations(context=routed, spark_session=spark)
            if row["workspace_id"] == workspace and row["table_id"] == table_id]
        expected = current[0]["activation_id"] if current else None
        contract = exact_record(metadata_records("METADATA_DATA_CONTRACT", context=routed, spark_session=spark),
            table_id=table_id, contract_id=contract_id, contract_version=contract_version, status="frozen")
        identity = resolve_catalogue_table_identity(config, workspace, table_id, context=routed, spark_session=spark)
        destination = pipeline_physical_bindings({table_id: identity}, config=config, workspace_id=workspace)[table_id]
        if str(destination["workspace_id"]).casefold() != workspace.casefold():
            raise ValueError("Select the physical table workspace before reviewing Contract Activation.")
        payload_sha256 = hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest()
    widgets = shared.require_ipywidgets()
    confirm = widgets.Checkbox(description="I reviewed the exact frozen Contract and physical workspace", indent=False)
    button = widgets.Button(description="Activate Contract", button_style="primary", disabled=True)
    report = widgets.HTML()
    state = {"activation_id": str(uuid4()), "result": None}
    def activate():
        if not confirm.value:
            raise ValueError("Review and confirm the exact frozen Contract first.")
        state["result"] = set_table_contract_activation(table_id, contract_id, contract_version,
            expected_activation_id=expected, activation_id=state["activation_id"], governance_confirmed=True,
            context=routed, spark_session=spark, expected_destination=destination,
            expected_payload_sha256=payload_sha256)
        button.disabled = True
        report.value = "<p>Contract activated for the physical workspace and Table ID.</p>"
        return state["result"]
    def click(_button):
        button.disabled = True
        try:
            activate()
        except Exception as exc:
            report.value = "<p role='alert'>" + html.escape(str(exc)) + "</p>"
            button.disabled = not confirm.value
    confirm.observe(lambda _event: setattr(button, "disabled", not confirm.value or state["result"] is not None), names="value")
    button.on_click(click)
    root = shared.form_page(widgets, title="Data Contract Activation", tone="governance",
        description="Protect one physical workspace/Table ID with an exact frozen Contract.", children=[
            widgets.HTML("<pre style='white-space:pre-wrap'>" + html.escape(json.dumps(
                {"workspace_id": workspace, "destination": destination, "previous_activation_id": expected, "contract": contract}, indent=2, default=str)) + "</pre>"),
            confirm, button, report])
    startup.display(root)
    return {"widget": root, "destination": destination, "state": state, "controls": {"confirm": confirm, "activate": button}, "actions": {"activate": activate}}
