"""Governance activation gate for one validated frozen Data Contract version."""

from __future__ import annotations

import html
from typing import Any, Mapping

from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema
from fabricops_kit.config.shared import resolve_fabric_context
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


def _latest_validation(
    rows: list[dict[str, Any]], *, contract_id: str, contract_version: int, environment_name: str
) -> dict[str, Any]:
    """Summarize the latest exact-version Engineering validation run."""
    matches = [
        row for row in rows
        if str(row.get("contract_id") or "") == contract_id
        and int(row.get("contract_version") or 0) == int(contract_version)
        and str(row.get("environment_name") or "") == environment_name
        and str(row.get("execution_type") or "").casefold() == "validate"
    ]
    if not matches:
        return {"validated": False, "run_id": "", "rows": [], "blocked": 0, "warnings": 0}

    run_rank: dict[str, tuple[str, str]] = {}
    for row in matches:
        run_id = str(row.get("run_id") or "")
        rank = (str(row.get("_committed_at") or ""), str(row.get("_activity_id") or ""))
        run_rank[run_id] = max(run_rank.get(run_id, ("", "")), rank)
    latest_run = max(run_rank, key=run_rank.get)
    latest_rows = [row for row in matches if str(row.get("run_id") or "") == latest_run]

    def blocking(row: Mapping[str, Any]) -> bool:
        status = str(row.get("status") or "").casefold()
        severity = str(row.get("severity") or "").casefold()
        return row.get("can_continue") is False or (
            severity == "blocking" and status in {"fail", "failed", "block", "blocked"}
        )

    blocked = sum(blocking(row) for row in latest_rows)
    warnings = sum(
        str(row.get("status") or "").casefold() in {"warn", "warning"}
        for row in latest_rows
    )
    return {
        "validated": bool(latest_rows) and blocked == 0,
        "run_id": latest_run,
        "rows": latest_rows,
        "blocked": blocked,
        "warnings": warnings,
    }


def widget_activate_data_contract(
    *, table_id: str | None = None, contract_version: int | None = None,
    spark_session: Any = None, context: Any = None,
) -> dict[str, Any]:
    """Link a Data Agreement and activate one validated frozen Data Contract.

    Only frozen versions are selectable. The exact selected version must have a
    successful latest Engineering validation run in METADATA_GUARDRAIL_RESULTS
    with execution_type='validate' before activation is enabled. Activation
    links one exact Data Agreement version and updates the active Production
    contract pointer; it never edits the immutable contract payload or deploys
    the Engineering pipeline.
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
    results = _rows(read_lakehouse_table(
        "METADATA_GUARDRAIL_RESULTS",
        store="Metadata",
        schema=metadata_table_physical_schema(config, "METADATA_GUARDRAIL_RESULTS"),
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
    agreement_select = widgets.Dropdown(
        description="Agreement",
        style=field_style,
        layout=field_layout,
    )
    validation_view = widgets.HTML()
    review_view = widgets.HTML()
    status = shared.status_message(widgets)
    activate = widgets.Button(
        description="Activate for Production",
        button_style="primary",
        disabled=True,
        icon="check",
    )
    confirmation_text = widgets.HTML()
    cancel_confirmation = widgets.Button(description="Cancel")
    confirm_activation = widgets.Button(
        description="Activate for Production",
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
        "validation": None,
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
        agreement = agreement_select.value
        if not selected:
            state.update(contract_id=None, contract_version=None, validation=None)
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
        validation = _latest_validation(
            results,
            contract_id=contract_id_value,
            contract_version=version,
            environment_name=env,
        )
        state.update(
            table_id=table_select.value,
            contract_id=contract_id_value,
            contract_version=version,
            validation=validation,
        )
        if agreement:
            state["agreement_id"], state["agreement_version"] = agreement
        else:
            state["agreement_id"], state["agreement_version"] = None, None

        if validation["validated"]:
            validation_view.value = (
                "<div style='font-size:12px;line-height:1.45;'>"
                "<span style='color:#107c10;font-weight:700;'>✓ Validated</span> · "
                f"{html.escape(validation['run_id'])} · "
                f"{validation['warnings']} warning(s)</div>"
            )
        else:
            validation_view.value = (
                "<div style='font-size:12px;line-height:1.45;'>"
                "<span style='color:#a4262c;font-weight:700;'>Activation blocked</span> · "
                + (
                    f"{validation['blocked']} blocking failure(s)"
                    if validation["run_id"]
                    else "no exact-version validation"
                )
                + "</div>"
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
        activate.disabled = not (validation["validated"] and agreement)

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
        if activate.disabled or not contract_select.value or not agreement_select.value:
            return
        _, version = contract_select.value
        agreement_id_value, agreement_version_value = agreement_select.value
        confirmation_text.value = (
            "<div style='font-size:13px;line-height:1.5;'>"
            "<b>Activate Data Contract?</b><br>"
            f"Make <b>{html.escape(table_labels.get(str(table_select.value), str(table_select.value)))}</b> "
            f"contract v{version} the governed Production definition linked to "
            f"<b>{html.escape(str(agreement_id_value))} · v{html.escape(str(agreement_version_value))}</b>."
            "</div>"
        )
        confirmation_prompt.layout.display = "flex"

    def cancel_activation(_: Any) -> None:
        confirmation_prompt.layout.display = "none"

    def perform_activation(_: Any) -> None:
        if activate.disabled or not contract_select.value or not agreement_select.value:
            confirmation_prompt.layout.display = "none"
            return
        contract_id_value, version = contract_select.value
        agreement_id_value, agreement_version_value = agreement_select.value
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
                f"Data Contract v{version} is now the governed Production definition."
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
    activate.on_click(on_activate)
    cancel_confirmation.on_click(cancel_activation)
    confirm_activation.on_click(perform_activation)
    agreement_select.options = agreement_options()
    agreement_select.value = None
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
                children=[review_view, activation_actions, status],
            ),
        ],
        layout=widgets.Layout(
            width="100%",
            min_width="0",
            grid_template_columns="repeat(3, minmax(0, 1fr))",
            grid_gap="12px",
            align_items="start",
        ),
    )

    page = shared.form_page(
        widgets,
        title="Activate Data Contract",
        description=(
            "Link an exact Data Agreement version and activate a validated frozen "
            "contract for Production."
        ),
        children=[activation_flow, confirmation_prompt],
    )
    ip.display(page)
    state["widget"] = page
    state["refresh"] = refresh_contracts
    return state
