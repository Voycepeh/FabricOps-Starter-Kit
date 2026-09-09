"""Unified, contract-centric Data Contract authoring widget."""

from __future__ import annotations

import html
import json
from typing import Any, Mapping

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.data_contract import shared as contract_authoring
from fabricops_kit.pipeline.shared import (
    GUARDRAIL_CHANGE_BEHAVIOURS,
    resolve_guardrail_change_behaviour,
)
from fabricops_kit.widgets import shared

_SECTIONS = ("Overview", "Enrichment", "Guardrails", "Review")
_GUARDRAIL_TYPES = ("Schema", "Freshness", "Changes", "Data Quality", "Sensitive Data")
_ACTIONS = ("Warn", "Block")


def _escape(value: Any) -> str:
    """Escape one dynamic value for safe passive HTML rendering."""
    return html.escape(str(value if value not in (None, "") else "—"), quote=True)


def _table_html(headers: tuple[str, ...], rows: list[tuple[Any, ...]], *, empty: str) -> str:
    """Render a complete passive table as one escaped HTML block."""
    heading = "".join(f"<th>{_escape(value)}</th>" for value in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{_escape(value)}</td>" for value in row) + "</tr>"
        for row in rows
    )
    if not body:
        body = f'<tr><td colspan="{len(headers)}"><em>{_escape(empty)}</em></td></tr>'
    return (
        '<table class="fabricops-contract-table"><thead><tr>' + heading
        + "</tr></thead><tbody>" + body + "</tbody></table>"
    )


def _column_maps(state: Mapping[str, Any]) -> tuple[list[str], dict[str, str]]:
    rows = state.get("available_columns") or []
    names = [str(row.get("column_name") or "") for row in rows if row.get("column_name")]
    return names, {str(row.get("column_name")): str(row.get("column_id") or "") for row in rows}


def _guardrail_summary(row: Mapping[str, Any], column_names: Mapping[str, str]) -> tuple[str, str, str, str]:
    kind = str(row.get("guardrail_type") or "unspecified").replace("_", " ").title()
    rule = str(row.get("rule_type") or row.get("rule_id") or "—")
    scope = column_names.get(str(row.get("column_id") or ""), "table")
    try:
        parameters = json.loads(str(row.get("rule_parameters_json") or "{}"))
    except json.JSONDecodeError:
        parameters = {}
    if kind == "Schema" and parameters.get("columns"):
        rule = "Required: " + ", ".join(map(str, parameters["columns"]))
    elif kind == "Freshness" and parameters.get("maximum_age"):
        rule = f"Max age {parameters['maximum_age']} {parameters.get('maximum_age_unit', '')}".strip()
        scope = str(parameters.get("freshness_column") or scope)
    elif kind == "Data Quality":
        scope = ", ".join(map(str, parameters.get("columns") or [])) or scope
    return kind, rule, scope, str(row.get("action") or "Warn")


def _authoring_rule_state(state: Mapping[str, Any]) -> dict[str, Any]:
    names, ids = _column_maps(state)
    return {
        "table_id": state["table_id"], "contract_id": state["contract_id"],
        "contract_version": state["contract_version"], "environment_name": state["environment_name"],
        "columns": names, "column_ids": ids, "catalogue_profile_rows": state.get("available_columns") or [],
        "existing_rules": state.get("guardrails") or [],
    }


def widget_author_data_contract(
    *,
    table_id: str,
    spark_session: Any,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Open one exact Data Contract version in a unified authoring experience.

    Parameters
    ----------
    table_id : str
        Canonical governed table identity. The widget creates or reopens its one
        agreement-free draft in the active environment.
    spark_session : Any
        Active Microsoft Fabric Spark session used by the authoring services.
    context : dict[str, Any], optional
        Advanced override for the ``FABRIC_CONTEXT`` created by ``00_env_config``.

    Returns
    -------
    dict[str, Any]
        Table-owned exact-version state, compact controls, displayed UI, and callable
        ``render_section``, ``validate``, and ``freeze`` actions.

    Raises
    ------
    ValueError
        If the table has no active Catalogue row or authored input is invalid.
    RuntimeError
        If Fabric context, metadata routing, or freezing is unavailable.

    Notes
    -----
    This is the primary contract-centric authoring UX. Passive headers, summaries,
    tables, badges, and previews are aggregated HTML; ipywidgets are reserved for
    interaction and only the current section/subtype editor is mounted. Governance
    validation and persistence remain in the Data Contract authoring service layer.

    Examples
    --------
    >>> form = widget_author_data_contract(table_id="table-orders", spark_session=spark)
    >>> render_review = form["render_section"]
    >>> render_review("Review")

    See Also
    --------
    widget_activate_data_contract

    """
    from IPython import display as ip

    config, env, _ = resolve_fabric_context(context=context)
    table_id = str(table_id or "").strip()
    if not table_id:
        raise ValueError("table_id must be a non-empty canonical FabricOps table identity.")
    draft = contract_authoring.create_contract_draft(
        table_id=table_id, config=config, env=env, spark_session=spark_session,
        context=context,
    )
    identity, version = contract_authoring.validate_contract_identity(
        draft["contract_id"], draft["contract_version"]
    )
    state = contract_authoring.get_contract_authoring_state(
        config=config, env=env, spark_session=spark_session,
        contract_id=identity, contract_version=version,
    )
    widgets = shared.require_ipywidgets()
    controls: dict[str, Any] = {}
    editor = widgets.VBox()
    status = widgets.HTML(value="")
    section_control = widgets.ToggleButtons(options=_SECTIONS, value="Overview", description="Section")
    controls["section"] = section_control

    def reload() -> None:
        refreshed = contract_authoring.get_contract_authoring_state(
            config=config, env=env, spark_session=spark_session,
            contract_id=identity, contract_version=version,
        )
        state.clear(); state.update(refreshed)

    def overview() -> Any:
        contract = state["contract"]
        table_row = next((row for row in state["catalogue_rows"] if str(row.get("metadata_level", "")).lower() == "table"), {})
        counts: dict[str, int] = {}
        for row in state["guardrails"]:
            kind = str(row.get("guardrail_type") or "unspecified").replace("_", " ").title()
            counts[kind] = counts.get(kind, 0) + 1
        described = {str(row.get("column_id") or "") for row in state["enrichment"] if row.get("value")}
        total = len(state.get("available_columns") or [])
        values = [
            ("Table", table_row.get("table_name") or state["table_id"]), ("table_id", state["table_id"]),
            ("Processing", table_row.get("load_strategy")), ("Contract ID", identity),
            ("Exact version", version), ("Lifecycle", contract.get("status")),
            ("Enrichment", f"{len(described)}/{total} columns"),
            ("Guardrails", len(state["guardrails"])),
            ("Categories", ", ".join(f"{key} ({value})" for key, value in sorted(counts.items())) or "None"),
        ]
        cards = "".join(f'<div class="fabricops-contract-card"><b>{_escape(k)}</b><span>{_escape(v)}</span></div>' for k, v in values)
        return widgets.HTML(value=f'<div class="fabricops-contract-grid">{cards}</div>')

    def enrichment() -> Any:
        names, ids = _column_maps(state)
        by_column = {
            (str(row.get("column_id") or ""), str(row.get("enrichment_type") or "")): str(row.get("value") or "")
            for row in state["enrichment"]
        }
        select = widgets.Combobox(options=names, value=names[0] if names else "", ensure_option=True, description="Column")
        enrichment_type = widgets.Dropdown(options=("Description", "Classification"), description="Descriptive field")
        value = widgets.Textarea(description="Value")
        save = widgets.Button(description="Save Enrichment", button_style="primary")
        summary = widgets.HTML()
        controls.update(enrichment_column=select, enrichment_type=enrichment_type, enrichment_value=value, enrichment_description=value, enrichment_save=save)

        def render_value(*_args: Any) -> None:
            value.value = by_column.get((ids.get(str(select.value), ""), str(enrichment_type.value)), "")

        def render_summary() -> None:
            summary.value = _table_html(
                ("Column", "Description", "Classification"),
                [(name, by_column.get((ids[name], "Description"), ""), by_column.get((ids[name], "Classification"), "")) for name in names],
                empty="No columns",
            )

        def on_save(_button: Any) -> None:
            try:
                records = contract_authoring.save_enrichment([{
                    "contract_id": identity, "contract_version": version, "environment_name": env,
                    "enrichment_level": "column", "column_id": ids.get(str(select.value), ""),
                    "enrichment_type": enrichment_type.value, "value": value.value,
                }], config=config, env=env, spark_session=spark_session)
                if records:
                    by_column[(records[0]["column_id"], records[0]["enrichment_type"])] = records[0]["value"]
                    state["enrichment"].extend(records)
                render_summary(); status.value = "<b>Enrichment saved.</b>"
            except (ValueError, RuntimeError) as exc:
                status.value = f'<span style="color:#a4262c">{_escape(exc)}</span>'
        select.observe(render_value, names="value"); enrichment_type.observe(render_value, names="value"); save.on_click(on_save)
        render_value(); render_summary()
        return widgets.VBox((select, enrichment_type, value, save, summary))

    def guardrails() -> Any:
        names, ids = _column_maps(state)
        id_to_name = {value: key for key, value in ids.items()}
        listing = widgets.HTML(value=_table_html(
            ("Type", "Rule", "Scope", "Action"),
            [_guardrail_summary(row, id_to_name) for row in state["guardrails"] if row.get("is_active") is not False],
            empty="No Guardrails configured",
        ))
        kind = widgets.Dropdown(options=[("+ Add Guardrail", ""), *((value, value) for value in _GUARDRAIL_TYPES)], value="", description="Type")
        subtype = widgets.VBox()
        controls["guardrail_type"] = kind; controls["guardrail_editor"] = subtype

        def mount(*_args: Any) -> None:
            if not kind.value:
                subtype.children = (); return
            action = widgets.Dropdown(options=_ACTIONS, value="Block", description="Action")
            save = widgets.Button(description="Add Guardrail", button_style="primary")
            fields: list[Any] = []
            rule_state = _authoring_rule_state(state)
            if kind.value == "Schema":
                columns = widgets.SelectMultiple(options=names, description="Required columns")
                fields = [columns]
                def build() -> dict[str, Any]:
                    return shared.build_rule_record(rule_state, guardrail_type="schema", rule_id="schema", rule_type="minimum_required", parameters={"columns": list(columns.value)}, action=action.value)
            elif kind.value == "Freshness":
                column = widgets.Dropdown(options=names, description="Date/time column")
                age = widgets.FloatText(value=24, description="Maximum age")
                unit = widgets.Dropdown(options=("Minutes", "Hours", "Days"), value="Hours", description="Unit")
                fields = [column, age, unit]
                def build() -> dict[str, Any]:
                    return shared.build_rule_record(rule_state, guardrail_type="freshness", rule_id="freshness", rule_type="max_age", parameters={"freshness_column": column.value, "maximum_age": age.value, "maximum_age_unit": str(unit.value).lower()}, action=action.value)
            elif kind.value == "Changes":
                behaviour = widgets.Dropdown(options=GUARDRAIL_CHANGE_BEHAVIOURS, description="Change behaviour")
                partition = widgets.Dropdown(options=[("None", ""), *[(name, name) for name in names]], description="Partition column")
                watermark = widgets.Dropdown(options=[("None", ""), *[(name, name) for name in names]], description="Change column")
                fields = [behaviour, partition, watermark]
                def build() -> dict[str, Any]:
                    expected, pattern = resolve_guardrail_change_behaviour(behaviour.value)
                    return shared.build_rule_record(rule_state, guardrail_type="changes", rule_id="changes", rule_type=expected, parameters={"change_behaviour": behaviour.value, "expected_change": expected, "source_pattern": pattern, "partition_column": partition.value, "change_column": watermark.value}, action=action.value)
            elif kind.value == "Data Quality":
                rule = widgets.Dropdown(options=("missing_values", "unique_values", "accepted_values", "value_range", "regex_match"), description="Rule")
                columns = widgets.SelectMultiple(options=names, description="Columns")
                parameters = widgets.Textarea(value="{}", description="Parameters (JSON)")
                fields = [rule, columns, parameters]
                def build() -> list[dict[str, Any]]:
                    return shared.dq_records_from_selection(rule_state, rule_id=rule.value, selected_columns=columns.value, parameters=json.loads(parameters.value or "{}"), action=action.value)
            else:
                column = widgets.Dropdown(options=names, description="Column")
                treatment = widgets.Dropdown(options=("tokenize", "mask", "bucket", "remove"), description="Treatment")
                parameters = widgets.Textarea(value="{}", description="Parameters (JSON)")
                fields = [column, treatment, parameters]
                def build() -> dict[str, Any]:
                    return shared.sensitive_data_record_from_selection(rule_state, column_name=column.value, treatment=treatment.value, action=action.value, parameters=json.loads(parameters.value or "{}"))

            def on_save(_button: Any) -> None:
                try:
                    built = build(); records = built if isinstance(built, list) else [built]
                    saved = contract_authoring.save_guardrails(records, config=config, env=env, spark_session=spark_session)
                    state["guardrails"].extend(saved); status.value = "<b>Guardrail saved.</b>"
                    render_section("Guardrails")
                except (ValueError, RuntimeError, json.JSONDecodeError) as exc:
                    status.value = f'<span style="color:#a4262c">{_escape(exc)}</span>'
            save.on_click(on_save)
            controls["guardrail_subtype_controls"] = {"action": action, "save": save, "fields": fields}
            subtype.children = (*fields, action, save)
        kind.observe(mount, names="value"); mount()
        return widgets.VBox((listing, kind, subtype))

    def validate() -> dict[str, Any]:
        reload()
        return contract_authoring.validate_contract_draft(
            state["contract"], catalogue_rows=state["catalogue_rows"], enrichment_rows=state["enrichment"],
            guardrail_rows=state["guardrails"], environment_name=env,
        )

    def freeze() -> dict[str, Any]:
        validate()
        result = contract_authoring.freeze_contract(
            draft=state["contract"], config=config, env=env,
            spark_session=spark_session, context=context,
        )
        frozen = result["contract"]
        state["contract"] = frozen
        state["review"] = result["payload"]
        state["warnings"] = result["warnings"]
        return frozen

    def review() -> Any:
        issues: list[str] = []
        try:
            validate()
        except (ValueError, RuntimeError) as exc:
            issues.append(str(exc))
        review_html = widgets.HTML(value=_table_html(
            ("Check", "Result"), [
                ("Exact contract version", f"{identity} · v{version}"),
                ("Lifecycle", state["contract"].get("status")),
                ("Enrichment rows", len(state["enrichment"])),
                ("Guardrails", len(state["guardrails"])),
                ("Validation", "; ".join(issues) if issues else "Draft is valid"),
            ], empty="No review state",
        ))
        freeze_button = widgets.Button(description="Freeze exact draft", button_style="primary", disabled=bool(issues))
        controls["freeze"] = freeze_button
        def on_freeze(_button: Any) -> None:
            try:
                frozen = freeze(); status.value = f"<b>Contract v{_escape(frozen['contract_version'])} frozen.</b>"
                render_section("Review")
            except (ValueError, RuntimeError) as exc:
                status.value = f'<span style="color:#a4262c">{_escape(exc)}</span>'
        freeze_button.on_click(on_freeze)
        return widgets.VBox((review_html, freeze_button))

    renderers = {"Overview": overview, "Enrichment": enrichment, "Guardrails": guardrails, "Review": review}
    def render_section(name: str) -> Any:
        if name not in renderers:
            raise ValueError(f"Unknown contract authoring section: {name}")
        section_control.value = name
        current = renderers[name]()
        editor.children = (current,)
        return current
    section_control.observe(lambda change: render_section(change["new"]), names="value")

    contract = state["contract"]
    table_row = next(
        (row for row in state["catalogue_rows"] if str(row.get("metadata_level") or "").lower() == "table"),
        {},
    )
    table_name = table_row.get("table_name") or state["table_id"]
    styles = widgets.HTML(value=(
        '<style>.fabricops-contract-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:8px}'
        '.fabricops-contract-card{border:1px solid #ddd;border-radius:6px;padding:10px;display:flex;flex-direction:column}'
        '.fabricops-contract-table{width:100%;border-collapse:collapse}.fabricops-contract-table th,.fabricops-contract-table td{padding:7px;border-bottom:1px solid #ddd;text-align:left}</style>'
    ))
    ui = shared.form_page(
        widgets,
        title=str(table_name),
        description=(
            f'table_id: {state["table_id"]} · Contract v{version} · '
            f'{str(contract.get("status") or "draft").upper()} · {identity}'
        ),
        children=(styles, section_control, editor, status),
    )
    render_section("Overview")
    ip.display(ui)
    return {"state": state, "controls": controls, "ui": ui, "render_section": render_section, "validate": validate, "freeze": freeze}
