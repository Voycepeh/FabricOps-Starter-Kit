"""Governance activation gate for one validated frozen Data Contract version."""

from __future__ import annotations

import html
import hashlib
from typing import Any

from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
from fabricops_kit.config.shared import metadata_timestamp_sort_key, resolve_fabric_context
from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.io import read_lakehouse_table
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.widgets import shared


def _rows(value: Any) -> list[dict[str, Any]]:
    """Return Spark or row-like values as plain dictionaries."""
    source = value.collect() if hasattr(value, "collect") else value
    return [
        row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row)
        for row in (source or [])
    ]


def _diagnostic_review(reports, contract, environment):
    """Match a complete in-memory Testing report to an exact frozen definition."""
    expected = {"contract_id": contract["contract_id"], "contract_version": int(contract["contract_version"]),
                "payload_sha256": hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest()}
    matches = [report for report in reports or []
               if report.get("execution_mode") == "testing" and report.get("execution_environment") == environment
               and report.get("tested_contracts", {}).get(contract["table_id"]) == expected]
    if not matches:
        return {"available": False, "plan_id": ""}
    latest = max(metadata_timestamp_sort_key(report.get("testing_completed_at")) for report in matches)
    current = [report for report in matches if metadata_timestamp_sort_key(report.get("testing_completed_at")) == latest]
    available = all(report.get("validation_passed") is True and report.get("published") is False
                    and report.get("persistence_status") == "disabled" and report.get("execution_plan_id")
                    for report in current)
    return {"available": bool(available), "plan_id": current[-1].get("execution_plan_id", "") if available else ""}


def widget_activate_data_contract(
    *, table_id: str | None = None, contract_version: int | None = None,
    testing_results: list[dict[str, Any]] | None = None,
    spark_session: Any = None, context: Any = None,
) -> dict[str, Any]:
    """Link a Data Agreement and activate one validated frozen Data Contract.

    This separate Governance action requires a successful in-memory Testing
    report matching the exact frozen payload, explicit review approval, an exact
    Data Agreement version and confirmation. Testing does not register activation
    evidence or authorize activation. The approval is a deliberate Governance
    decision after reviewing diagnostics and the checks that were not exercised.
    Activation never edits the immutable payload or deploys the pipeline.

    Parameters
    ----------
    table_id : str, optional
        Initial governed table selection; omitted or unavailable IDs select the
        first table with a frozen contract.
    contract_version : int, optional
        Initial frozen version selection. Choose an available version in the UI.
    testing_results : list of dict, optional
        Complete Write diagnostics returned by Testing. Only exact payload matches
        with validation_passed=True qualify for explicit Governance review.
        Reports remain in memory; opening this widget performs no persistence.
    spark_session : object, optional
        Active Fabric Spark session override.
    context : object, optional
        FabricOps runtime context established by 00_env_config.

    Returns
    -------
    dict[str, Any]
        Rendered widget, selectors, validation state, activation action, and
        ``refresh`` callback. Opening the widget does not activate a version.

    Raises
    ------
    ValueError
        If an activation request fails validation. Select a frozen version with
        successful Testing diagnostics, explicit review and an eligible Data Agreement.
    RuntimeError
        If metadata routing, reads, or activation persistence fail. Check the
        configured metadata target and permissions. UI callbacks display failures.

    Examples
    --------
    >>> state = widget_activate_data_contract(spark_session=spark)

    """
    from IPython import display as ip
    import ipywidgets as widgets
    config, env, runtime_context = resolve_fabric_context(context=context)
    spark = get_spark_session(spark_session)
    quiet_context = {
        **dict(runtime_context or {}),
        "config": config,
        "env": env,
        "_fabricops_suppress_io_log": True,
    }
    governance = contracts.list_contract_governance_state(
        config=config, env=env, spark_session=spark
    )
    frozen = [
        dict(row) for row in governance["contracts"]
        if str(row.get("status") or "").casefold() == "frozen"
    ]
    table_rows = [
        dict(row) for row in governance["tables"]
        if any(str(contract.get("table_id") or "") == str(row.get("table_id") or "") for contract in frozen)
    ]
    agreements = _rows(read_lakehouse_table(
        "METADATA_DATA_AGREEMENT",
        store="Metadata",
        schema=metadata_table_physical_schema(config, "METADATA_DATA_AGREEMENT"),
        spark_session=spark,
        context=quiet_context,
    ))
    table_labels = {
        str(row.get("table_id") or ""): (
            f"{row.get('layer') or ''} · {row.get('schema_name') or ''}.{row.get('table_name') or ''}"
        ).strip(" ·")
        for row in table_rows
    }
    initial_table = str(table_id or "")
    if initial_table not in table_labels:
        initial_table = next(iter(table_labels), "")
    field_layout = widgets.Layout(width="100%", min_width="0", max_width="100%")
    field_style = {"description_width": "96px"}
    table_select = widgets.Dropdown(
        description="Table",
        options=[(label, identity) for identity, label in table_labels.items()],
        value=initial_table or None,
        style=field_style,
        layout=field_layout,
    )
    contract_select = widgets.Dropdown(
        description="Version",
        style=field_style,
        layout=field_layout,
    )
    agreement_select = widgets.Combobox(
        description="Agreement",
        placeholder="Search Data Agreements...",
        ensure_option=True,
        style=field_style,
        layout=field_layout,
    )
    validation_view = widgets.HTML()
    reviewed = widgets.Checkbox(value=False, description="I reviewed these Testing diagnostics and approve this frozen version for Live", indent=False)
    review_view = widgets.HTML()
    status = shared.status_message(widgets)
    activate = widgets.Button(
        description="Activate for Live",
        button_style="primary",
        disabled=True,
        icon="check",
    )
    confirmation_text = widgets.HTML()
    cancel_confirmation = widgets.Button(description="Cancel")
    confirm_activation = widgets.Button(
        description="Activate for Live",
        button_style="primary",
        icon="check",
    )
    confirmation_prompt = widgets.VBox(
        [
            confirmation_text,
            shared.action_row(widgets, [cancel_confirmation, confirm_activation]),
        ],
        layout=widgets.Layout(
            width="100%",
            min_width="0",
            max_width="560px",
            display="none",
            border="1px solid #c7d2e0",
            padding="14px",
            gap="10px",
        ),
    )
    state: dict[str, Any] = {
        "environment_name": env,
        "table_id": initial_table or None,
        "contract_id": None,
        "contract_version": None,
        "agreement_id": None,
        "agreement_version": None,
        "diagnostic_review": None,
        "review_approval": reviewed,
        "activation_result": None,
    }

    def contract_options(selected_table: str) -> list[tuple[str, tuple[str, int]]]:
        candidates = [
            row for row in frozen if str(row.get("table_id") or "") == selected_table
        ]
        candidates.sort(key=lambda row: int(row.get("contract_version") or 0), reverse=True)
        return [
            (
                f"v{int(row.get('contract_version') or 0)}"
                + (" · Active" if row.get("is_active") is True else ""),
                (str(row.get("contract_id") or ""), int(row.get("contract_version") or 0)),
            )
            for row in candidates
        ]

    agreement_lookup: dict[str, tuple[str, str]] = {}

    def agreement_options() -> list[tuple[str, tuple[str, str]]]:
        ordered = sorted(
            agreements,
            key=lambda row: (
                str(row.get("agreement_name") or ""),
                str(row.get("agreement_version") or ""),
            ),
        )
        return [
            (
                f"{row.get('agreement_name') or row.get('agreement_id')} · v{row.get('agreement_version')}",
                (str(row.get("agreement_id") or ""), str(row.get("agreement_version") or "")),
            )
            for row in ordered
        ]

    def refresh_review(*_: Any) -> None:
        selected = contract_select.value
        agreement = agreement_lookup.get(str(agreement_select.value or ""))
        if not selected:
            state.update(contract_id=None, contract_version=None, diagnostic_review=None)
            validation_view.value = (
                "<div style='color:#667085;font-size:12px;line-height:1.45;'>"
                "Select a frozen version to load validation.</div>"
            )
            review_view.value = (
                "<div style='color:#667085;font-size:12px;line-height:1.45;'>"
                "Select a frozen contract and Data Agreement.</div>"
            )
            confirmation_prompt.layout.display = "none"
            activate.disabled = True
            return

        contract_id_value, version = selected
        selected_row = next(row for row in frozen if row["contract_id"] == contract_id_value
                            and int(row["contract_version"]) == version and row["table_id"] == table_select.value)
        validation = _diagnostic_review(testing_results, selected_row, env)
        approval_scope = (table_select.value, contract_id_value, version, agreement)
        if state.get("approval_scope") != approval_scope:
            reviewed.value = False
        state["approval_scope"] = approval_scope
        state.update(
            table_id=table_select.value,
            contract_id=contract_id_value,
            contract_version=version,
            diagnostic_review=validation,
        )
        if agreement:
            state["agreement_id"], state["agreement_version"] = agreement
        else:
            state["agreement_id"], state["agreement_version"] = None, None
        validation_view.value = (
            "<p>Exact Testing diagnostics available for Governance review. "
            "Publication permissions, transactions and finalization remain unverified.</p>"
            if validation["available"] else "<p>Supply successful Testing diagnostics for this exact frozen payload before review.</p>"
        )
        agreement_text = (
            f"{html.escape(str(agreement[0]))} · v{html.escape(str(agreement[1]))}"
            if agreement else "Not selected"
        )
        review_view.value = (
            "<div style='font-size:12px;line-height:1.55;'>"
            f"<b>{html.escape(table_labels.get(str(table_select.value), str(table_select.value)))}</b><br>"
            f"Contract v{version} · Frozen<br>"
            f"{agreement_text}"
            "</div>"
        )
        confirmation_prompt.layout.display = "none"
        activate.disabled = not (validation["available"] and reviewed.value and agreement)

    def refresh_contracts(change: Any = None) -> None:
        selected_table = str(table_select.value or "")
        state["table_id"] = selected_table or None
        options = contract_options(selected_table)
        contract_select.options = options
        preferred = next(
            (value for _, value in options if contract_version is not None and value[1] == int(contract_version)),
            None,
        )
        contract_select.value = preferred or (options[0][1] if options else None)
        refresh_review()

    def on_activate(_: Any) -> None:
        agreement = agreement_lookup.get(str(agreement_select.value or ""))
        if activate.disabled or not contract_select.value or not agreement:
            return
        _, version = contract_select.value
        agreement_id_value, agreement_version_value = agreement
        confirmation_text.value = (
            "<div style='font-size:13px;line-height:1.5;'>"
            "<b>Activate Data Contract?</b><br>"
            f"Make <b>{html.escape(table_labels.get(str(table_select.value), str(table_select.value)))}</b> "
            f"contract v{version} the active Live definition linked to "
            f"<b>{html.escape(str(agreement_id_value))} · v{html.escape(str(agreement_version_value))}</b>."
            "</div>"
        )
        confirmation_prompt.layout.display = "flex"

    def cancel_activation(_: Any) -> None:
        confirmation_prompt.layout.display = "none"

    def perform_activation(_: Any) -> None:
        agreement = agreement_lookup.get(str(agreement_select.value or ""))
        if activate.disabled or not contract_select.value or not agreement:
            confirmation_prompt.layout.display = "none"
            return
        contract_id_value, version = contract_select.value
        agreement_id_value, agreement_version_value = agreement
        try:
            result = contracts.activate_contract_version(
                config=config,
                env=env,
                table_id=str(table_select.value),
                contract_id=contract_id_value,
                contract_version=version,
                agreement_id=agreement_id_value,
                agreement_version=agreement_version_value,
                spark_session=spark,
                context=quiet_context,
                schema=metadata_table_physical_schema(config, "METADATA_DATA_CONTRACT"),
            )
            state["activation_result"] = result
            status.value = (
                "<span style='color:#107c10;font-weight:600;'>Activated ✓</span> "
                f"Data Contract v{version} is now the active Live definition."
            )
            activate.disabled = True
            confirmation_prompt.layout.display = "none"
        except Exception as exc:
            status.value = (
                "<span style='color:#a4262c;font-weight:600;'>Activation failed:</span> "
                + html.escape(str(exc))
            )

    table_select.observe(refresh_contracts, names="value")
    contract_select.observe(refresh_review, names="value")
    agreement_select.observe(refresh_review, names="value")
    reviewed.observe(refresh_review, names="value")
    activate.on_click(on_activate)
    cancel_confirmation.on_click(cancel_activation)
    confirm_activation.on_click(perform_activation)
    agreement_choices = agreement_options()
    agreement_lookup.update(agreement_choices)
    agreement_select.options = [label for label, _ in agreement_choices]
    agreement_select.value = ""
    refresh_contracts()
    activation_actions = shared.action_row(widgets, [activate])
    activation_flow = widgets.GridBox(
        [
            shared.form_section(
                widgets,
                title="1 · Contract",
                children=[table_select, contract_select, validation_view],
            ),
            shared.form_section(
                widgets,
                title="2 · Data Agreement",
                children=[agreement_select],
            ),
            shared.form_section(
                widgets,
                title="3 · Review & activate",
                children=[review_view, reviewed, activation_actions, status],
            ),
        ],
        layout=widgets.Layout(
            width="100%",
            min_width="0",
            grid_template_columns="repeat(3, minmax(0, 1fr))",
            grid_gap="12px",
            align_items="flex-start",
        ),
    )

    page = shared.form_page(
        widgets,
        title="Activate Data Contract",
        description=(
            "Review exact Testing diagnostics, approve the frozen version, and link an exact Data Agreement for Live."
        ),
        children=[activation_flow, confirmation_prompt],
    )
    ip.display(page)
    state["widget"] = page
    state["refresh"] = refresh_contracts
    return state
