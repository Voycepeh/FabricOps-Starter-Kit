"""Governance selection and conditional activation of exact physical Contracts."""
from __future__ import annotations

import hashlib
import html
import json
from uuid import uuid4

from fabricops_kit.activated_pipeline.shared import (
    agreement_definition, exact_record, manifest_digest, metadata_records,
    read_activation_history, set_table_contract_activation, validate_agreement,
)
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.widgets import shared


def widget_activate_data_contract(table_id: str | None = None, contract_id: str | None = None,
                                  contract_version: int | None = None, *,
                                  workspace_id: str | None = None, context=None) -> dict:
    """Select and review a table or file dataset, frozen Contract and applicable Agreement.

    The existing selector lists readable table and file names with physical
    context. File Activation uses its exact frozen Source ID and reader settings,
    without a Table ID. Opening and reviewing never activate a dataset.

    Parameters
    ----------
    table_id, contract_id : str | None, optional
        Preselect an exact logical table and frozen Contract. With no arguments,
        select from named physical tables/files and exact frozen versions.
    contract_version : int | None, optional
        Exact positive frozen version to preselect; never a latest fallback.
    workspace_id : str | None, optional
        Physical table workspace. With a supplied table, defaults to the current
        configured scope. Governance metadata stays in its central Lakehouse.
    context : dict | None, optional
        Configured Governance notebook context.

    Returns
    -------
    dict
        Widget, selection/review state, controls and review/activate/refresh actions.
        Opening changes no metadata. Backend mutation independently revalidates
        exact bindings, policy hashes and the reviewed current activation ID.

    Notes
    -----
    Governance owns all central metadata, so selection uses Catalogue records
    without opening Engineering workspaces. Actual Fabric permissions authorize
    writes. Each physical activation selects one frozen Contract and at most one
    Agreement; cross-workspace execution requires effective associated terms.
    Retained revisions provide history independently of notebook promotion.

    Examples
    --------
    >>> ui = widget_activate_data_contract()
    >>> ui = widget_activate_data_contract(TABLE_ID, CONTRACT_ID, 1,
    ...     workspace_id=PHYSICAL_WORKSPACE_ID)

    """
    from fabricops_kit.pipeline.shared import resolve_catalogue_table_identity, pipeline_physical_bindings, participant_id
    from fabricops_kit.data_contract.shared import contract_file_datasets, dataset_display_name
    startup = shared.WidgetStartup("Data Contract Activation", tone="governance", reserved_height="560px")
    config, current_workspace, runtime = resolve_fabric_context(context=context)
    metadata_workspace = runtime.get("metadata_workspace_id") or current_workspace
    base = {**runtime, "config": config, "scope_workspace_id": current_workspace, "metadata_workspace_id": metadata_workspace}
    spark = get_spark_session(context=runtime)
    selected_workspace = workspace_id or (current_workspace if table_id is not None else None)
    with startup.phase("metadata_loading", "Loading datasets, frozen Contracts and Governance history…"):
        catalogue = metadata_records("METADATA_DATA_CATALOGUE", context=base, spark_session=spark)
        contracts = metadata_records("METADATA_DATA_CONTRACT", context=base, spark_session=spark)
        agreements = metadata_records("METADATA_DATA_AGREEMENT", context=base, spark_session=spark)
        initial_context = {**base, "scope_workspace_id": selected_workspace or current_workspace}
        history_rows = read_activation_history(context=initial_context, spark_session=spark)
    tables = [row for row in catalogue if row.get("metadata_level") == "table" and row.get("is_active") is not False]
    files = contract_file_datasets(contracts, config=config, workspace_id=current_workspace)
    datasets = [*tables, *files]
    frozen = [row for row in contracts if row.get("status") == "frozen"]
    widgets = shared.require_ipywidgets()
    workspaces = sorted({row["workspace_id"] for row in datasets} | ({selected_workspace} if selected_workspace else set()))
    workspace = widgets.Dropdown(options=[("Select physical workspace", None)] + [(value, value) for value in workspaces],
        value=selected_workspace, layout=widgets.Layout(width="100%"))
    table = widgets.Dropdown(options=[], layout=widgets.Layout(width="100%"))
    contract = widgets.Dropdown(options=[], layout=widgets.Layout(width="100%"))
    agreement = widgets.Dropdown(options=[("No Agreement association", None)] + [
        (str(row["agreement_id"]) + " / " + str(row["agreement_version"]), (row["agreement_id"], row["agreement_version"]))
        for row in agreements], layout=widgets.Layout(width="100%"))
    confirm = widgets.Checkbox(description="I reviewed this exact physical Contract and Agreement selection", indent=False)
    review_button = widgets.Button(description="Review selection")
    activate_button = widgets.Button(description="Activate Contract", button_style="primary", disabled=True)
    refresh_button = widgets.Button(description="Refresh history")
    report, history = widgets.HTML(), widgets.HTML()
    state = {"review": None, "result": None, "destination": None, "history": history_rows, "changing": False}
    result = {}
    def routed():
        if not workspace.value:
            raise ValueError("Select the physical table workspace.")
        return {**base, "scope_workspace_id": workspace.value}
    def invalidate(_event=None):
        state["review"] = None
        state["result"] = None
        confirm.value = False
        activate_button.disabled = True
    def contract_choices(_event=None):
        if state["changing"]:
            return
        invalidate()
        options = [(f'{row["contract_id"]} / v{row["contract_version"]}', (row["contract_id"], row["contract_version"]))
            for row in frozen if participant_id(row) == table.value]
        contract.options = [("Select frozen Contract/version", None)] + options
        wanted = (contract_id, contract_version)
        if wanted in [value for _label, value in options]:
            contract.value = wanted
    def table_choices(_event=None):
        state["changing"] = True
        try:
            values = {participant_id(row) for row in datasets if row["workspace_id"] == workspace.value}
            if table_id is not None and workspace.value == selected_workspace:
                values.add(table_id)
            labels = {participant_id(row): dataset_display_name(row) for row in datasets}
            table.options = [("Select dataset", None)] + [(labels.get(value, value), value) for value in sorted(values)]
            if table_id in values:
                table.value = table_id
        finally:
            state["changing"] = False
        contract_choices()
    def refresh():
        state["history"] = read_activation_history(context=routed() if workspace.value else base, spark_session=spark)
        return render_history()
    def render_history():
        scoped = [row for row in state["history"] if (not workspace.value or row["workspace_id"] == workspace.value)
            and (not table.value or (row.get("source_id") or row.get("table_id")) == table.value)]
        history.value = "<details><summary>Contract Activation history and current state</summary><pre style='white-space:pre-wrap'>" + html.escape(json.dumps(scoped, indent=2, default=str)) + "</pre></details>"
        return scoped
    def selection_binding():
        if not table.value or not contract.value:
            raise ValueError("Select an exact dataset and frozen Contract/version.")
        row = exact_record(metadata_records("METADATA_DATA_CONTRACT", context=routed(), spark_session=spark),
            **({"source_id": table.value} if str(table.value).startswith("file:") else {"table_id": table.value}),
            contract_id=contract.value[0], contract_version=contract.value[1], status="frozen")
        if row.get("source_id"):
            destination = json.loads(row["contract_payload_json"])["source"]
        else:
            identity = resolve_catalogue_table_identity(config, workspace.value, table.value, context=routed(), spark_session=spark)
            destination = pipeline_physical_bindings({table.value: identity}, config=config, workspace_id=workspace.value)[table.value]
        if str(destination["workspace_id"]).casefold() != workspace.value.casefold():
            raise ValueError("Select the physical table workspace before review.")
        state["destination"] = destination
        result["destination"] = destination
        return row, destination
    def review():
        invalidate()
        row, destination = selection_binding()
        history_values = refresh()
        current = [item for item in history_values if item["status"] == "active"]
        reference = agreement.value
        terms = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=routed(), spark_session=spark),
            agreement_id=reference[0], agreement_version=reference[1]) if reference else None
        if terms:
            validate_agreement(terms)
        state["review"] = {"workspace_id": workspace.value, "dataset_id": table.value,
            "table_id": row.get("table_id"), "source_id": row.get("source_id"), "contract": contract.value,
            "reference": reference, "agreement_sha256": manifest_digest(agreement_definition(terms)) if terms else None,
            "destination": destination, "payload_sha256": hashlib.sha256(row["contract_payload_json"].encode()).hexdigest(),
            "expected_activation_id": current[0]["activation_id"] if current else None, "activation_id": str(uuid4())}
        report.value = "<pre style='white-space:pre-wrap;max-height:360px;overflow:auto'>" + html.escape(json.dumps(
            {"destination": destination, "contract": row, "agreement": terms, "previous_activation_id": state["review"]["expected_activation_id"]}, indent=2, default=str)) + "</pre>"
        return state["review"]
    def activate():
        reviewed = state["review"]
        if not reviewed or not confirm.value:
            raise ValueError("Review and explicitly confirm the exact frozen Contract first.")
        terms = reviewed["reference"]
        is_file = reviewed["destination"].get("source_type") == "file"
        file_dataset = next((item for item in files if item["source_id"] == reviewed["source_id"]), {}) if is_file else {}
        file_store = file_dataset.get("store")
        state["result"] = set_table_contract_activation(None if is_file else reviewed["table_id"], *reviewed["contract"],
            **({"file_source": reviewed["destination"], "file_store": file_store,
                "file_configuration_workspace_id": file_dataset.get("configuration_workspace_id", reviewed["workspace_id"])} if is_file else {}),
            expected_activation_id=reviewed["expected_activation_id"], activation_id=reviewed["activation_id"], governance_confirmed=True,
            context=routed(), spark_session=spark, expected_destination=reviewed["destination"],
            expected_payload_sha256=reviewed["payload_sha256"], agreement_id=terms[0] if terms else None,
            agreement_version=terms[1] if terms else None, expected_agreement_sha256=reviewed["agreement_sha256"])
        activate_button.disabled = True
        report.value += "<p>Contract selection saved independently of notebook promotion.</p>"
        refresh()
        return state["result"]
    def run(action, button):
        button.disabled = True
        try:
            action()
        except Exception as exc:
            report.value += "<p role='alert'>" + html.escape(str(exc)) + "</p>"
        finally:
            button.disabled = False
            activate_button.disabled = not confirm.value or state["review"] is None or state["result"] is not None
    workspace.observe(table_choices, names="value")
    table.observe(contract_choices, names="value")
    contract.observe(invalidate, names="value")
    agreement.observe(invalidate, names="value")
    confirm.observe(lambda _event: setattr(activate_button, "disabled", not confirm.value or state["review"] is None or state["result"] is not None), names="value")
    for button, action in ((review_button, review), (activate_button, activate), (refresh_button, refresh)):
        button.on_click(lambda _button, action=action, button=button: run(action, button))
    table_choices()
    if table.value and contract.value:
        selection_binding()
    render_history()
    root = shared.form_page(widgets, title="Data Contract Activation", tone="governance",
        description="Select an exact frozen Contract and applicable Agreement for a physical table.", children=[
            widgets.HTML("<label>Physical table workspace</label>"), workspace,
            widgets.HTML("<label>Physical Table ID</label>"), table,
            widgets.HTML("<label>Frozen Contract and version</label>"), contract,
            widgets.HTML("<label>Agreement governing this physical Contract selection</label>"), agreement,
            review_button, report, confirm, activate_button, refresh_button, history])
    startup.display(root)
    result.update(widget=root, state=state, destination=state["destination"], controls={"workspace": workspace, "table": table,
        "contract": contract, "agreement": agreement, "review": review_button, "confirm": confirm, "activate": activate_button},
        actions={"review": review, "activate": activate, "refresh": refresh})
    return result
