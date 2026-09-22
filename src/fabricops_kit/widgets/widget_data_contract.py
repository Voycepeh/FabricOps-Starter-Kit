"""Unified Data Contract governance authoring, review, freeze, and activation widget."""

from __future__ import annotations

import html
import json
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.widgets import shared

DATA_CONTRACT_MANIFEST: dict[str, Any] | None = None
DATA_CONTRACT_MANIFEST_JSON: str | None = None
_TABS = ("Table", "Columns", "Advanced", "Manifest & Freeze")
_ADVANCED_TYPES = (
    "Composite uniqueness", "Compare columns", "Required when",
    "Conditional value", "Referential columns",
)


def _expose_manifest(payload: dict[str, Any]) -> str:
    """Expose one canonical payload to both module and active notebook namespaces."""
    global DATA_CONTRACT_MANIFEST, DATA_CONTRACT_MANIFEST_JSON
    DATA_CONTRACT_MANIFEST = payload
    DATA_CONTRACT_MANIFEST_JSON = json.dumps(payload, indent=2, ensure_ascii=False, default=str)
    try:
        from IPython import get_ipython
        shell = get_ipython()
        if shell is not None:
            shell.user_ns["DATA_CONTRACT_MANIFEST"] = payload
            shell.user_ns["DATA_CONTRACT_MANIFEST_JSON"] = DATA_CONTRACT_MANIFEST_JSON
    except (ImportError, AttributeError):
        pass
    return DATA_CONTRACT_MANIFEST_JSON


def _manifest_html(payload: dict[str, Any]) -> str:
    """Render the human and exact JSON views from the same canonical dictionary."""
    table = payload.get("table", {})
    enrichment = payload.get("enrichment", {})
    descriptions = {
        str(row.get("column_id") or ""): row.get("value")
        for row in enrichment.get("columns", []) if row.get("enrichment_type") == "Description"
    }
    required = set()
    for rule in payload.get("guardrails", []):
        if rule.get("guardrail_type") == "schema":
            params = rule.get("rule_parameters", {})
            required.update(params.get("required_columns") or params.get("columns") or [])
    column_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(str(row.get("column_name") or "")),
            html.escape(str(row.get("data_type") or "")),
            "Yes" if row.get("column_name") in required or row.get("column_id") in required else "No",
            html.escape(str(descriptions.get(str(row.get("column_id") or ""), ""))),
        ) for row in table.get("columns", [])
    )
    guardrails = "".join(
        "<li><b>{}</b> · {} · {} · <code>{}</code> · {}</li>".format(
            html.escape(str(rule.get("guardrail_type") or "")),
            html.escape(str(rule.get("rule_type") or "")),
            html.escape(str(rule.get("column_id") or "table")),
            html.escape(json.dumps(rule.get("rule_parameters", {}), default=str, sort_keys=True)),
            "Block" if str(rule.get("action") or "Warn") == "Block" else "Warn",
        ) for rule in payload.get("guardrails", [])
    ) or "<li>None configured</li>"
    exact_json = html.escape(_expose_manifest(payload))
    return f"""
    <h3>Identity</h3><p><b>{html.escape(str(table.get('schema_name') or ''))}.{html.escape(str(table.get('table_name') or ''))}</b></p>
    <h3>Table &amp; processing</h3><pre>{html.escape(json.dumps(table.get('processing', {}), indent=2, default=str))}</pre>
    <h3>Columns</h3><table><thead><tr><th>Column</th><th>Datatype</th><th>Required</th><th>Description</th></tr></thead><tbody>{column_rows}</tbody></table>
    <h3>Guardrails &amp; advanced rules</h3><ul>{guardrails}</ul>
    <details><summary>JSON manifest</summary><pre>{exact_json}</pre></details>"""


def _profile_html(profile: dict[str, Any]) -> str:
    if profile.get("kind") == "values":
        rows = "".join(f"<tr><td>{html.escape(str(item.get('value')))}</td><td>{html.escape(str(item.get('count')))}</td></tr>" for item in profile["values"])
        return f"<h4>Observed values</h4><table>{rows}</table>"
    if profile.get("kind") == "range":
        return f"<h4>Observed range</h4><p>Min &nbsp; {html.escape(str(profile.get('min')))}<br>Max &nbsp; {html.escape(str(profile.get('max')))}</p>"
    return "<p>No profile values available.</p>"


def widget_data_contract(
    *, table_id: str | None = None, contract_version: int | None = None,
    spark_session: Any = None, context: Any = None,
) -> dict[str, Any]:
    """Open the single governance experience for a governed table's Data Contracts.

    Parameters
    ----------
    table_id : str, optional
        Initial canonical governed table identity. If omitted, select it in the widget.
    contract_version : int, optional
        Initial exact lifecycle version. If omitted, the newest version is selected.
    spark_session : object, optional
        Active Microsoft Fabric Spark session. The configured session is used when omitted.
    context : object, optional
        FabricOps runtime context normally established by ``00_env_config``.

    Returns
    -------
    dict
        Current selector and lifecycle state, controls, and callable ``select``,
        ``new_draft``, ``refresh_manifest``, ``freeze``, and ``activate`` actions.

    Raises
    ------
    ValueError
        If an initial identity is invalid or an authored lifecycle action is ineligible.
    RuntimeError
        If configured metadata routing or an atomic lifecycle mutation fails.

    Notes
    -----
    The Environment and configured FabricStore are inherited from ``00_env_config``.
    Profile context is read from ``METADATA_DATA_PROFILED`` and
    ``METADATA_DATA_PROFILED_FREQUENCY`` and is never included in the canonical payload.
    Refresh frequency is intentionally omitted because it is not a canonical persisted
    Data Contract field. Immutable versions are review-only. Activation requires an exact
    Data Agreement version and delegates its atomic mutation to the Data Contract service.

    Examples
    --------
    >>> state = widget_data_contract(table_id="table-orders", spark_session=spark)
    >>> state["refresh_manifest"]()

    See Also
    --------
    widget_select_data_contract

    """
    from IPython import display as ip

    config, env, resolved = resolve_fabric_context(context=context)
    spark = shared.get_spark_session(spark_session)
    catalogue = contracts.list_contract_governance_state(config=config, env=env, spark_session=spark)
    table_rows = catalogue["tables"]
    if table_id is not None and str(table_id) not in {str(row.get("table_id")) for row in table_rows}:
        raise ValueError("table_id has no active table-level Catalogue row in the authoring environment.")
    state: dict[str, Any] = {
        "environment_name": env, "table_id": table_id, "contract_version": contract_version,
        "contracts": catalogue["contracts"], "tables": table_rows, "current": None,
        "manifest": None, "profile_context": None, "message": "", "_controls": {},
    }

    def select(selected_table: str, version: int | None = None) -> dict[str, Any] | None:
        state["table_id"] = str(selected_table or "").strip() or None
        matches = [row for row in state["contracts"] if str(row.get("table_id") or "") == str(state["table_id"] or "")]
        if not matches:
            state["current"] = None
            return None
        chosen = next((row for row in matches if int(row.get("contract_version") or 0) == int(version or 0)), matches[0])
        state["contract_version"] = int(chosen["contract_version"])
        state["current"] = contracts.get_contract_review_state(
            config=config, env=env, spark_session=spark,
            contract_id=str(chosen["contract_id"]), contract_version=state["contract_version"],
        )
        refresh_manifest()
        return state["current"]

    def new_draft() -> dict[str, Any]:
        if not state.get("table_id"):
            raise ValueError("Select one governed table before creating a draft.")
        draft = contracts.create_contract_draft(
            table_id=str(state["table_id"]), config=config, env=env,
            spark_session=spark, context=resolved,
        )
        state["contracts"] = [draft, *[row for row in state["contracts"]
            if not (row.get("contract_id") == draft.get("contract_id") and row.get("contract_version") == draft.get("contract_version"))]]
        select(str(state["table_id"]), int(draft["contract_version"]))
        return draft

    def refresh_manifest() -> dict[str, Any] | None:
        current = state.get("current")
        if not current:
            return None
        if str(current["contract"].get("status") or "").lower() == "draft":
            payload, warnings = contracts.build_contract_manifest(
                draft=current["contract"], config=config, env=env, spark_session=spark,
            )
            state["manifest_warnings"] = warnings
        else:
            payload = current["payload"]
            state["manifest_warnings"] = []
        state["manifest"] = payload
        _expose_manifest(payload)
        return payload

    def freeze() -> dict[str, Any]:
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be frozen.")
        result = contracts.freeze_contract(
            draft=current["contract"], config=config, env=env, spark_session=spark, context=resolved,
        )
        state["manifest"] = result["payload"]
        _expose_manifest(result["payload"])
        state["current"] = contracts.get_contract_review_state(
            config=config, env=env, spark_session=spark,
            contract_id=str(current["contract_id"]), contract_version=int(current["contract_version"]),
        )
        return result

    def activate(agreement_id: str, agreement_version: str) -> dict[str, Any]:
        current = state.get("current")
        if not current:
            raise ValueError("Select an exact frozen Data Contract version before activation.")
        row = current["contract"]
        return contracts.activate_contract_version(
            config=config, env=env, table_id=str(row["table_id"]), contract_id=str(row["contract_id"]),
            contract_version=int(row["contract_version"]), agreement_id=agreement_id,
            agreement_version=agreement_version, spark_session=spark,
            context={"config": config, "env": env, **dict(resolved or {})},
        )

    def save_enrichment(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Persist table or column Enrichment only for the selected draft."""
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be edited.")
        saved = contracts.save_enrichment(records, config=config, env=env, spark_session=spark)
        select(str(state["table_id"]), int(state["contract_version"]))
        return saved

    def save_guardrails(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Persist canonical table, column, or advanced Guardrails for the selected draft."""
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be edited.")
        saved = contracts.save_guardrails(records, config=config, env=env, spark_session=spark)
        select(str(state["table_id"]), int(state["contract_version"]))
        return saved

    def load_profile_context(column_id: str) -> dict[str, Any]:
        """Load persisted authoring context without changing the contract manifest."""
        profile = contracts.get_column_profile_context(
            config=config, env=env, spark_session=spark, table_id=str(state.get("table_id") or ""),
            column_id=str(column_id or ""),
        )
        state["profile_context"] = profile
        return profile

    state.update(
        select=select, new_draft=new_draft, refresh_manifest=refresh_manifest,
        freeze=freeze, activate=activate, save_enrichment=save_enrichment,
        save_guardrails=save_guardrails, load_profile_context=load_profile_context,
    )
    if table_id:
        select(str(table_id), contract_version)

    widgets = shared.require_ipywidgets()
    table_options = [(f"{row.get('schema_name') or ''}.{row.get('table_name') or row.get('table_id')}", str(row["table_id"])) for row in table_rows]
    table_control = widgets.Dropdown(options=[("Select governed table", ""), *table_options], value=state.get("table_id") or "", description="Table")
    contract_control = widgets.Dropdown(description="Contract")
    selector = widgets.HBox([
        widgets.Text(value=env, description="Environment", disabled=True),
        widgets.Text(value="Metadata", description="Fabric store", disabled=True), table_control, contract_control,
    ], layout=widgets.Layout(width="100%", flex_flow="row wrap"))
    status = widgets.HTML()
    panes = [widgets.VBox() for _ in _TABS]
    tabs = widgets.Tab(children=panes)
    for index, title in enumerate(_TABS):
        tabs.set_title(index, title)

    def render() -> None:
        current = state.get("current")
        if not current:
            for pane in panes: pane.children = (widgets.HTML("<p>Select a governed table and contract.</p>"),)
            return
        row, editable = current["contract"], str(current["contract"].get("status") or "").lower() == "draft"
        table = next((item for item in current.get("catalogue_rows", []) if not item.get("column_id")), {})
        classification = widgets.Dropdown(options=("Public", "Internal", "Confidential", "Restricted"), description="Classification", disabled=not editable)
        description = widgets.Textarea(description="Description", disabled=not editable, layout=widgets.Layout(width="100%"))
        freshness = widgets.VBox([widgets.HTML("<h4>Freshness Check</h4>"), widgets.Checkbox(description="Enabled", disabled=not editable), widgets.Checkbox(description="Block on failure", disabled=not editable)])
        drift = widgets.VBox([widgets.HTML("<h4>Source Drift Check</h4>"), widgets.Checkbox(description="Enabled", disabled=not editable), widgets.Checkbox(description="Block on failure", disabled=not editable)])
        context_html = widgets.HTML(f"<h3>{html.escape(str(table.get('schema_name') or ''))}.{html.escape(str(table.get('table_name') or state['table_id']))}</h3><p>{html.escape(env)} · Metadata · {html.escape(str(table.get('store_type') or ''))}</p><h4>Contract</h4><b>v{row['contract_version']} · {html.escape(str(row.get('status') or '').upper())}</b>")
        panes[0].children = (widgets.HBox([context_html, widgets.VBox([classification, description, freshness, drift])], layout=widgets.Layout(width="100%", flex_flow="row wrap")),)
        columns = current.get("available_columns", [])
        column_select = widgets.Select(options=[(f"{item.get('column_name')} · {item.get('data_type')}", item.get('column_id')) for item in columns], description="Columns")
        column_editor = widgets.VBox([widgets.HTML("<h4>Schema / Required</h4>"), widgets.Checkbox(description="Required", disabled=not editable), widgets.Dropdown(options=("Public", "Internal", "Confidential", "Restricted"), description="Classification", disabled=not editable), widgets.Textarea(description="Description", disabled=not editable), widgets.HTML("<h4>Observed profile context</h4><p>Select a column to load persisted profile context.</p>"), widgets.HTML("<h4>Sensitive Data</h4>"), widgets.Checkbox(description="Enabled", disabled=not editable), widgets.Checkbox(description="Block on failure", disabled=not editable), widgets.Dropdown(options=("tokenize", "mask", "bucket", "remove"), description="Treatment", disabled=not editable), widgets.HTML("<h4>Column Data Quality</h4>"), widgets.Button(description="Suggest rules", disabled=True)])
        def column_changed(change: dict[str, Any]) -> None:
            if change.get("new"):
                try:
                    column_editor.children[4].value = _profile_html(load_profile_context(str(change["new"])))
                except (ValueError, RuntimeError) as exc:
                    column_editor.children[4].value = f"<p>{html.escape(str(exc))}</p>"
        column_select.observe(column_changed, names="value")
        panes[1].children = (widgets.HBox([column_select, column_editor], layout=widgets.Layout(width="100%", flex_flow="row wrap")),)
        advanced_list = widgets.Select(options=_ADVANCED_TYPES, description="Rule type")
        panes[2].children = (widgets.HBox([widgets.VBox([widgets.HTML("<h3>Advanced rules</h3>"), widgets.Button(description="Suggest rules", disabled=True), advanced_list, widgets.HTML("<b>Saved configurations</b>"), widgets.Select(options=[]), widgets.Button(description="+ New configuration", disabled=not editable)]), widgets.VBox([widgets.HTML("<h3>New configuration</h3>"), widgets.Checkbox(description="Block on failure", disabled=not editable), widgets.Button(description="Save configuration", button_style="primary", disabled=not editable)])], layout=widgets.Layout(width="100%", flex_flow="row wrap")),)
        payload = state.get("manifest") or {}
        actions = []
        if editable:
            freeze_button = widgets.Button(description=f"Freeze v{row['contract_version']}", button_style="primary")
            def freeze_clicked(_button: Any) -> None:
                try:
                    freeze(); state["message"] = f"Data Contract v{row['contract_version']} is FROZEN."; render()
                except (ValueError, RuntimeError) as exc:
                    status.value = html.escape(str(exc))
            freeze_button.on_click(freeze_clicked)
            actions.append(freeze_button)
        elif str(row.get("status") or "").lower() in {"frozen", "active", "superseded"}:
            agreement_id = widgets.Text(description="Data Agreement ID")
            agreement_version = widgets.Text(description="Agreement version")
            activate_button = widgets.Button(description="Activate for Production", disabled=str(row.get("status") or "").lower() == "active")
            def activate_clicked(_button: Any) -> None:
                try:
                    activate(agreement_id.value, agreement_version.value)
                    state["message"] = f"Data Contract v{row['contract_version']} is ACTIVE for Production."
                    status.value = html.escape(state["message"])
                except (ValueError, RuntimeError) as exc:
                    status.value = html.escape(str(exc))
            activate_button.on_click(activate_clicked)
            actions.extend([agreement_id, agreement_version, activate_button])
        panes[3].children = (widgets.HBox([widgets.HTML(f"<h3>Manifest</h3><p>v{row['contract_version']} · {str(row.get('status') or '').upper()}</p><b>Sections</b><p>Identity<br>Table &amp; processing<br>Columns<br>Guardrails &amp; advanced rules<br>JSON manifest</p><b>Notebook variable</b><p>DATA_CONTRACT_MANIFEST</p>"), widgets.VBox([widgets.HTML(_manifest_html(payload)), *actions])], layout=widgets.Layout(width="100%", flex_flow="row wrap")),)

    def table_changed(change: dict[str, Any]) -> None:
        selected = change["new"]
        state["table_id"] = selected or None
        matches = [row for row in state["contracts"] if str(row.get("table_id") or "") == selected]
        contract_control.options = [("New draft", "new"), *[(f"v{row['contract_version']} · {str(row.get('status') or '').title()}", str(row["contract_version"])) for row in matches]]
        if matches: contract_control.value = str(matches[0]["contract_version"])
        else: render()

    def contract_changed(change: dict[str, Any]) -> None:
        if not state.get("table_id") or not change["new"]: return
        if change["new"] == "new": new_draft()
        else: select(str(state["table_id"]), int(change["new"]))
        render()

    table_control.observe(table_changed, names="value")
    contract_control.observe(contract_changed, names="value")
    state["_controls"] = {"table": table_control, "contract": contract_control, "tabs": tabs, "status": status}
    if table_control.value: table_changed({"new": table_control.value})
    render()
    page = shared.form_page(
        widgets, title="Data Contract",
        description="Select, author, review, freeze, and activate one governed table contract.",
        children=[selector, tabs, status],
    )
    ip.display(page)
    return state
