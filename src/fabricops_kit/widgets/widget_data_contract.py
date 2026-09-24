"""Unified Data Contract governance authoring, review, freeze, and activation widget."""

from __future__ import annotations

import html
import json
import uuid
from typing import Any, Mapping

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.data_contract.scheduled_refresh import discover_scheduled_refresh
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.widgets import shared
from fabricops_kit.widgets.enrichment_shared import (
    PII_LABELS,
    build_ai_dq_context,
    build_ai_enrichment_context,
    build_ai_sensitive_data_context,
    suggest_enrichment,
    suggest_dq_rules,
    suggest_sensitive_data,
)

DATA_CONTRACT_MANIFEST: dict[str, Any] | None = None
DATA_CONTRACT_MANIFEST_JSON: str | None = None
_TABS = ("Table", "Columns", "Review")
_CLASSIFICATIONS = ("", "Public", "Internal", "Confidential", "Restricted")
_COLUMN_DQ_TYPES = ("completeness", "uniqueness", "value_set", "range", "pattern")
_ADVANCED_TYPES = (
    ("Composite uniqueness", "uniqueness"),
    ("Column relationship", "column_relationship"),
    ("Custom expression", "custom_expression"),
)
_DQ_HELP = {
    "completeness": "Limit missing values, with explicit blank-text handling.",
    "uniqueness": "Require one column, or a table-level column combination, to be unique.",
    "value_set": "Allow or block an explicit governed set of values.",
    "range": "Apply independent inclusive or exclusive minimum and maximum bounds.",
    "pattern": "Require populated text to match a governed regular expression.",
    "column_relationship": "Compare two columns row by row with a controlled operator.",
    "custom_expression": "Evaluate a constrained project-authored PySpark boolean Column expression.",
}


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


def _parameters(row: Mapping[str, Any]) -> dict[str, Any]:
    """Return rule parameters from an authoring row or immutable manifest row."""
    value = row.get("rule_parameters", row.get("rule_parameters_json", {}))
    if isinstance(value, str):
        try:
            value = json.loads(value or "{}")
        except json.JSONDecodeError:
            return {}
    return dict(value) if isinstance(value, Mapping) else {}


def _latest(rows: list[dict[str, Any]], *identity: str) -> list[dict[str, Any]]:
    """Resolve append-only authoring rows to their latest logical configurations."""
    selected: dict[tuple[str, ...], dict[str, Any]] = {}
    for row in rows:
        key = tuple(str(row.get(name) or "") for name in identity)
        rank = (
            int(row.get("guardrail_version") or 0),
            str(row.get("_committed_at") or ""),
            str(row.get("_activity_id") or ""),
        )
        previous = selected.get(key)
        previous_rank = (
            int(previous.get("guardrail_version") or 0),
            str(previous.get("_committed_at") or ""),
            str(previous.get("_activity_id") or ""),
        ) if previous else None
        if previous_rank is None or rank >= previous_rank:
            selected[key] = row
    return list(selected.values())


def _manifest_sections(payload: dict[str, Any]) -> dict[str, str]:
    """Build bounded, human-readable manifest review sections."""
    table = payload.get("table", {})
    contract = payload.get("contract", {})
    enrichments = payload.get("enrichment", {})
    guardrails = payload.get("guardrails", [])
    description_by_column = {
        str(row.get("column_id") or ""): str(row.get("value") or "")
        for row in enrichments.get("columns", [])
        if row.get("enrichment_type") == "Description"
    }
    required: set[str] = set()
    for rule in guardrails:
        if str(rule.get("guardrail_type") or "").lower() == "schema" and rule.get("is_active", True):
            required.update(_parameters(rule).get("required_columns", []))
    column_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(str(row.get("column_name") or "")),
            html.escape(str(row.get("data_type") or "")),
            "Yes" if row.get("column_id") in required or row.get("column_name") in required else "No",
            html.escape(description_by_column.get(str(row.get("column_id") or ""), "")),
        )
        for row in table.get("columns", [])
    )
    def rule_list(rows: list[dict[str, Any]]) -> str:
        items = "".join(
            "<li><b>{}</b> · {} · {} · {}</li>".format(
            html.escape(str(row.get("rule_type") or row.get("guardrail_type") or "")),
            html.escape(str(row.get("column_id") or "table")),
            html.escape(str(row.get("action") or "Warn")),
            html.escape(json.dumps(_parameters(row), sort_keys=True, default=str)),
            )
            for row in rows
        ) or "<li>None configured</li>"
        return f"<ul>{items}</ul>"

    active = [row for row in guardrails if row.get("is_active", True)]
    freshness = [row for row in active if str(row.get("guardrail_type") or "").lower() == "freshness"]
    source_drift = [row for row in active if str(row.get("guardrail_type") or "").lower() == "source_drift"]
    table_dq = [
        row for row in active
        if str(row.get("guardrail_type") or "").lower() in {"data_quality", "dq"}
        and not str(row.get("column_id") or "")
    ]
    column_guardrails = [row for row in active if str(row.get("column_id") or "")]
    composite = [row for row in table_dq if str(row.get("rule_type") or "") == "uniqueness"]
    relationships = [row for row in table_dq if str(row.get("rule_type") or "") == "column_relationship"]
    custom = [row for row in table_dq if str(row.get("rule_type") or "") == "custom_expression"]
    return {
        "Identity": (
            f"<h3>Identity</h3><p><b>{html.escape(str(table.get('schema_name') or ''))}."
            f"{html.escape(str(table.get('table_name') or ''))}</b></p>"
            f"<p>Contract v{html.escape(str(contract.get('contract_version') or ''))} · "
            f"{html.escape(str(contract.get('status') or '').upper())}</p>"
        ),
        "Table": (
            "<h3>Table</h3><p><b>Load strategy:</b> "
            f"{html.escape(str(table.get('processing', {}).get('load_strategy') or 'Not configured').upper())}</p>"
            + _scheduled_refresh_html(table.get("scheduled_refresh", {}))
            + f"<h4>Freshness</h4>{rule_list(freshness)}"
            + f"<h4>Source Drift</h4>{rule_list(source_drift)}"
            + f"<h4>Data Quality · Composite Uniqueness</h4>{rule_list(composite)}"
            + f"<h4>Data Quality · Column Relationships</h4>{rule_list(relationships)}"
            + f"<h4>Data Quality · Custom Expressions</h4>{rule_list(custom)}"
        ),
        "Columns": (
            "<h3>Columns</h3><table><thead><tr><th>Column</th><th>Datatype</th>"
            f"<th>Required</th><th>Description</th></tr></thead><tbody>{column_rows}</tbody></table>"
            f"<h4>Column Guardrails</h4>{rule_list(column_guardrails)}"
        ),
        "Lifecycle / Agreement state": (
            "<h3>Lifecycle / Agreement state</h3><p>Status: "
            f"<b>{html.escape(str(contract.get('status') or '').upper())}</b></p>"
        ),
    }


def _manifest_html(payload: dict[str, Any]) -> str:
    """Render the human and exact JSON views from the same canonical dictionary."""
    sections = _manifest_sections(payload)
    exact_json = html.escape(_expose_manifest(payload))
    return "".join(sections.values()) + (
        f"<details><summary>Exact JSON manifest</summary><pre>{exact_json}</pre></details>"
    )


def _profile_html(profile: dict[str, Any]) -> str:
    """Render escaped, read-only profile evidence."""
    if profile.get("kind") == "values":
        rows = "".join(
            f"<tr><td>{html.escape(str(item.get('value')))}</td>"
            f"<td>{html.escape(str(item.get('count')))}</td></tr>"
            for item in profile.get("values", [])
        )
        return f"<h4>Observed values</h4><table>{rows}</table>"
    if profile.get("kind") == "range":
        return (
            "<h4>Observed range</h4><p>Min &nbsp; "
            f"{html.escape(str(profile.get('min')))}<br>Max &nbsp; "
            f"{html.escape(str(profile.get('max')))}</p>"
        )
    return "<p>No profile values available.</p>"


def _scheduled_refresh_html(discovery: Mapping[str, Any]) -> str:
    """Render normalized Scheduled Refresh discovery without exposing API details."""
    status = str(discovery.get("status") or "unavailable")
    schedules = discovery.get("schedules") or []
    if status == "not_configured":
        detail = "<span>No schedule configured</span>"
    elif status != "configured" or not schedules:
        detail = "<span>Schedule discovery unavailable</span>"
    else:
        rows = []
        for schedule in schedules:
            frequency = str(schedule.get("frequency") or "Scheduled").replace("_", " ").title()
            times = ", ".join(str(value) for value in schedule.get("times") or []) or "Time not provided"
            timezone = str(schedule.get("timezone") or "UTC")
            enabled = "" if schedule.get("enabled", True) else " · Disabled"
            rows.append(
                "<li>{} · {} · {}{}</li>".format(
                    html.escape(frequency), html.escape(times), html.escape(timezone), enabled,
                )
            )
        detail = "<ul style=\"margin:4px 0 0 18px;\">" + "".join(rows) + "</ul>"
    return (
        "<div><b>Scheduled refresh</b><br>"
        f"{detail}<br><span style=\"color:#666;font-size:12px;\">Discovered from Fabric · read-only</span></div>"
    )


def widget_data_contract(
    *, table_id: str | None = None, contract_version: int | None = None,
    spark_session: Any = None, context: Any = None,
) -> dict[str, Any]:
    """Open the unified governance authoring and lifecycle experience for Data Contracts.

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
        Current selector, editor, lifecycle state, and callable authoring actions.

    Raises
    ------
    ValueError
        If an identity, authored record, or lifecycle action is invalid.
    RuntimeError
        If configured metadata routing or a lifecycle mutation fails.

    Notes
    -----
    Saves delegate to canonical Enrichment and Guardrail services, then reload the exact
    contract version and manifest. Profile context remains read-only and is never added
    to the canonical payload. Scheduled Refresh is discovered read-only from Microsoft
    Fabric and remains independent of the authored Freshness expectation. Immutable
    versions are review-only.
    When enabled through ``GOVERNANCE_CONFIG.ai_enrichment`` in ``00_env_config``,
    Sensitive Data AI assesses canonical columns as Direct PII, Indirect PII, or
    Not PII from governed metadata and profile evidence. Editable draft state remains
    separate until Governance accepts a suggestion. Manual Description or Classification
    edits mark dependent advice stale for explicit re-run. AI never saves, freezes,
    activates, or enforces a contract; runtime Sensitive Data enforcement remains deterministic.

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
    governance_config = getattr(config, "governance_config", None)
    ai_enrichment = dict(getattr(governance_config, "ai_enrichment", {}) or {})
    spark = get_spark_session(spark_session)
    catalogue = contracts.list_contract_governance_state(config=config, env=env, spark_session=spark)
    table_rows = catalogue["tables"]
    if table_id is not None and str(table_id) not in {str(row.get("table_id")) for row in table_rows}:
        raise ValueError("table_id has no active table-level Catalogue row in the authoring environment.")
    state: dict[str, Any] = {
        "environment_name": env, "table_id": table_id, "contract_version": contract_version,
        "contracts": catalogue["contracts"], "tables": table_rows, "current": None,
        "manifest": None, "profile_context": None, "message": "", "_controls": {},
        "_column_drafts": {},
        "_ai_suggestions": {}, "_ai_errors": {},
    }
    scheduled_refresh: dict[str, Any] = {
        "status": "unavailable", "schedules": [],
        "message": "Scheduled Refresh discovery requires a governed writer notebook identity.",
    }
    state["scheduled_refresh"] = scheduled_refresh
    contract_schedule = {
        "status": str(scheduled_refresh.get("status") or "unavailable"),
        "schedules": list(scheduled_refresh.get("schedules") or []),
    }

    def refresh_scheduled_refresh(selected_table: str) -> None:
        table_row = next(
            (item for item in table_rows if str(item.get("table_id") or "") == selected_table), {}
        )
        writer_item_id = str(table_row.get("_notebook_id") or "").strip()
        if writer_item_id:
            discovered = discover_scheduled_refresh(
                context=dict(resolved or {}),
                workspace_id=str(table_row.get("_workspace_id") or "") or None,
                item_id=writer_item_id,
            )
        else:
            discovered = {
                "status": "unavailable", "schedules": [],
                "message": "The governed writer notebook identity is unavailable.",
            }
        scheduled_refresh.clear()
        scheduled_refresh.update(discovered)
        contract_schedule.clear()
        contract_schedule.update({
            "status": str(discovered.get("status") or "unavailable"),
            "schedules": list(discovered.get("schedules") or []),
        })

    widgets = shared.require_ipywidgets()
    status = shared.status_message(widgets)
    panes = [widgets.VBox() for _ in _TABS]
    tabs = widgets.Tab(children=panes)
    for index, title in enumerate(_TABS):
        tabs.set_title(index, title)

    def set_status(message: str, *, error: bool = False, warning: bool = False) -> None:
        state["message"] = message
        colour = "#a4262c" if error else "#8a6d1d" if warning else "#107c10"
        status.value = f'<div style="color:{colour};font-weight:600;">{html.escape(message)}</div>'

    def refresh_manifest() -> dict[str, Any] | None:
        current = state.get("current")
        if not current:
            return None
        if str(current["contract"].get("status") or "").lower() == "draft":
            payload, warnings = contracts.build_contract_manifest(
                draft=current["contract"], config=config, env=env, spark_session=spark,
                scheduled_refresh=contract_schedule,
            )
            state["manifest_warnings"] = warnings
        else:
            payload = current["payload"]
            state["manifest_warnings"] = []
        state["manifest"] = payload
        _expose_manifest(payload)
        return payload

    def select(selected_table: str, version: int | None = None) -> dict[str, Any] | None:
        state["table_id"] = str(selected_table or "").strip() or None
        matches = [
            row for row in state["contracts"]
            if str(row.get("table_id") or "") == str(state["table_id"] or "")
        ]
        if not matches:
            state["current"] = None
            return None
        chosen = next(
            (row for row in matches if int(row.get("contract_version") or 0) == int(version or 0)),
            matches[0],
        )
        state["contract_version"] = int(chosen["contract_version"])
        state["current"] = contracts.get_contract_review_state(
            config=config, env=env, spark_session=spark,
            contract_id=str(chosen["contract_id"]), contract_version=state["contract_version"],
        )
        refresh_scheduled_refresh(str(state["table_id"] or ""))
        refresh_manifest()
        return state["current"]

    def new_draft() -> dict[str, Any]:
        if not state.get("table_id"):
            raise ValueError("Select one governed table before creating a draft.")
        draft = contracts.create_contract_draft(
            table_id=str(state["table_id"]), config=config, env=env,
            spark_session=spark, context=resolved,
        )
        state["contracts"] = [draft, *[
            row for row in state["contracts"]
            if not (
                row.get("contract_id") == draft.get("contract_id")
                and row.get("contract_version") == draft.get("contract_version")
            )
        ]]
        select(str(state["table_id"]), int(draft["contract_version"]))
        return draft

    def reload_after_save(message: str) -> None:
        select(str(state["table_id"]), int(state["contract_version"]))
        render()
        set_status(message)

    def save_enrichment(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be edited.")
        saved = contracts.save_enrichment(records, config=config, env=env, spark_session=spark)
        reload_after_save("Enrichment saved and the canonical contract state was refreshed.")
        return saved

    def save_guardrails(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be edited.")
        saved = contracts.save_guardrails(records, config=config, env=env, spark_session=spark)
        reload_after_save("Guardrails saved and the canonical contract state was refreshed.")
        return saved

    def load_profile_context(column_id: str) -> dict[str, Any]:
        profile = contracts.get_column_profile_context(
            config=config, env=env, spark_session=spark,
            table_id=str(state.get("table_id") or ""), column_id=str(column_id or ""),
        )
        state["profile_context"] = profile
        return profile

    def freeze() -> dict[str, Any]:
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be frozen.")
        result = contracts.freeze_contract(
            draft=current["contract"], config=config, env=env,
            spark_session=spark, context=resolved, scheduled_refresh=contract_schedule,
        )
        select(str(state["table_id"]), int(state["contract_version"]))
        return result

    def activate(agreement_id: str, agreement_version: str) -> dict[str, Any]:
        current = state.get("current")
        if not current:
            raise ValueError("Select an exact frozen Data Contract version before activation.")
        row = current["contract"]
        result = contracts.activate_contract_version(
            config=config, env=env, table_id=str(row["table_id"]),
            contract_id=str(row["contract_id"]), contract_version=int(row["contract_version"]),
            agreement_id=agreement_id, agreement_version=agreement_version,
            spark_session=spark, context={"config": config, "env": env, **dict(resolved or {})},
        )
        select(str(state["table_id"]), int(state["contract_version"]))
        return result

    state.update(
        select=select, new_draft=new_draft, refresh_manifest=refresh_manifest,
        freeze=freeze, activate=activate, save_enrichment=save_enrichment,
        save_guardrails=save_guardrails, load_profile_context=load_profile_context,
    )
    if table_id:
        select(str(table_id), contract_version)

    table_options = [
        (f"{row.get('schema_name') or ''}.{row.get('table_name') or row.get('table_id')}", str(row["table_id"]))
        for row in table_rows
    ]
    table_control = widgets.Dropdown(
        options=[("Select governed table", ""), *table_options], value=state.get("table_id") or "",
        **shared.widget_common(widgets, "Table"),
    )
    contract_control = widgets.Dropdown(**shared.widget_common(widgets, "Contract"))
    selector = shared.form_grid(widgets, [
        widgets.Text(value=env, disabled=True, **shared.widget_common(widgets, "Environment")),
        widgets.Text(value="Metadata", disabled=True, **shared.widget_common(widgets, "Fabric store")),
        table_control, contract_control,
    ])

    def current_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        current = state["current"]
        return (
            _latest(list(current.get("enrichment", [])), "enrichment_level", "column_id", "enrichment_type"),
            _latest(list(current.get("guardrails", [])), "guardrail_rule_id"),
        )

    def enrichment_value(rows: list[dict[str, Any]], level: str, kind: str, column_id: str = "") -> str:
        return str(next((
            row.get("value") or "" for row in reversed(rows)
            if str(row.get("enrichment_level") or "").lower() == level
            and str(row.get("column_id") or "") == column_id
            and str(row.get("enrichment_type") or "") == kind
        ), ""))

    def enrichment_record(level: str, kind: str, value: str, column_id: str = "") -> dict[str, Any]:
        current = state["current"]
        rows, _ = current_rows()
        previous = next((row for row in reversed(rows) if
            str(row.get("enrichment_level") or "").lower() == level
            and str(row.get("column_id") or "") == column_id
            and str(row.get("enrichment_type") or "") == kind), {})
        return {
            "enrichment_id": previous.get("enrichment_id") or str(uuid.uuid4()),
            "contract_id": current["contract_id"], "contract_version": current["contract_version"],
            "environment_name": env, "enrichment_level": level,
            "column_id": column_id, "enrichment_type": kind, "value": value,
        }

    def guardrail_record(
        guardrail_type: str, rule_type: str, parameters: dict[str, Any], *,
        column_id: str = "", action: str = "Warn", existing: Mapping[str, Any] | None = None,
        active: bool = True,
    ) -> dict[str, Any]:
        current = state["current"]
        old = dict(existing or {})
        return {
            "guardrail_rule_id": old.get("guardrail_rule_id") or str(uuid.uuid4()),
            "guardrail_version": int(old.get("guardrail_version") or 0) + 1,
            "contract_id": current["contract_id"], "contract_version": current["contract_version"],
            "environment_name": env, "column_id": column_id,
            "guardrail_type": guardrail_type, "rule_id": old.get("rule_id") or rule_type,
            "rule_type": rule_type, "rule_parameters_json": json.dumps(parameters),
            "action": action, "is_active": active,
        }

    def render() -> None:
        current = state.get("current")
        state["_controls"].update({"table": table_control, "contract": contract_control, "tabs": tabs, "status": status})
        if not current:
            prompt = widgets.HTML("<p>Select a governed table and contract.</p>")
            for pane in panes:
                pane.children = (prompt,)
            return
        row = current["contract"]
        editable = str(row.get("status") or "").lower() == "draft"
        enrichments, guardrails = current_rows()
        columns = list(current.get("available_columns", []))
        table = next((item for item in current.get("catalogue_rows", []) if not item.get("column_id")), {})
        if not table:
            table = (state.get("manifest") or {}).get("table", {})
        suggestion_scope = (str(current["contract_id"]), int(current["contract_version"]))
        ai_state = state["_ai_suggestions"].setdefault(
            suggestion_scope, {"table": {}, "columns": {}}
        )
        ai_errors = state["_ai_errors"].setdefault(suggestion_scope, {})
        classification_labels = list(
            getattr(governance_config, "sensitivity_labels", None) or _CLASSIFICATIONS[1:]
        )

        # Table: passive identity plus explicitly saved Enrichment and table Guardrails.
        table_description = widgets.Textarea(
            value=enrichment_value(enrichments, "table", "Description"), disabled=not editable,
            **shared.widget_common(widgets, "Description", textarea=True),
        )
        table_classification = widgets.Dropdown(
            options=_CLASSIFICATIONS, value=enrichment_value(enrichments, "table", "Classification"),
            disabled=not editable, **shared.widget_common(widgets, "Classification"),
        )
        table_description_ai = widgets.HTML()
        table_classification_ai = widgets.HTML()
        accept_table_description = widgets.Button(description="Accept", disabled=not editable)
        rerun_table_description = widgets.Button(description="Re-run", disabled=not editable)
        accept_table_classification = widgets.Button(description="Accept", disabled=not editable)
        rerun_table_classification = widgets.Button(description="Re-run", disabled=not editable)
        table_save = widgets.Button(description="Save table enrichment", button_style="primary", disabled=not editable)

        def save_table(_button: Any) -> None:
            try:
                save_enrichment([
                    enrichment_record("table", "Description", table_description.value),
                    enrichment_record("table", "Classification", table_classification.value),
                ])
            except (ValueError, RuntimeError) as exc:
                set_status(str(exc), error=True)

        table_save.on_click(save_table)

        def render_table_ai() -> None:
            if not ai_enrichment.get("enabled"):
                message = "<p><b>AI suggestion</b><br>Disabled in 00_env_config.</p>"
                table_description_ai.value = message
                table_classification_ai.value = message
            elif not editable:
                message = "<p><b>AI suggestion</b><br>Not run for review-only versions.</p>"
                table_description_ai.value = message
                table_classification_ai.value = message
            else:
                table_description_ai.value = _suggestion_html(
                    "Description", ai_state["table"].get("description")
                )
                table_classification_ai.value = _suggestion_html(
                    "Classification", ai_state["table"].get("classification")
                )
            available = editable and bool(ai_enrichment.get("enabled"))
            accept_table_description.disabled = not (
                available and ai_state["table"].get("description")
                and not ai_state["table"]["description"].get("error")
            )
            accept_table_classification.disabled = not (
                available and ai_state["table"].get("classification")
                and not ai_state["table"]["classification"].get("error")
            )
            rerun_table_description.disabled = not available
            rerun_table_classification.disabled = not available

        def run_table_ai(*, force: bool = False) -> None:
            if not editable or not ai_enrichment.get("enabled"):
                render_table_ai()
                return
            if (
                not force
                and ai_state["table"].get("description")
                and ai_state["table"].get("classification")
            ):
                render_table_ai()
                return
            try:
                result = suggest_enrichment(
                    build_ai_enrichment_context(
                        table,
                        metadata_level="table",
                        existing_description=str(table_description.value or ""),
                        classification_labels=classification_labels,
                    ),
                    description_prompt=str(ai_enrichment.get("description_prompt") or ""),
                    classification_prompt=str(ai_enrichment.get("classification_prompt") or ""),
                    classification_labels=classification_labels,
                )
                ai_state["table"]["description"] = {
                    "value": result["Description"], "stale": False
                }
                ai_state["table"]["classification"] = {
                    "value": result["Classification"], "stale": False
                }
                ai_errors.pop("table_enrichment", None)
            except (TypeError, ValueError, RuntimeError) as exc:
                message = str(exc)
                ai_state["table"].setdefault(
                    "description", {"error": message, "stale": False}
                )
                ai_state["table"].setdefault(
                    "classification", {"error": message, "stale": False}
                )
                ai_errors["table_enrichment"] = message
                set_status(f"Table AI suggestions unavailable: {message}", warning=True)
            render_table_ai()

        accept_table_description.on_click(
            lambda _button: setattr(
                table_description, "value",
                str(ai_state["table"].get("description", {}).get("value") or ""),
            )
        )
        accept_table_classification.on_click(
            lambda _button: setattr(
                table_classification, "value",
                str(ai_state["table"].get("classification", {}).get("value") or ""),
            )
        )
        rerun_table_description.on_click(lambda _button: run_table_ai(force=True))
        rerun_table_classification.on_click(lambda _button: run_table_ai(force=True))

        def table_description_changed(_change: dict[str, Any]) -> None:
            suggestion = ai_state["table"].get("classification")
            if suggestion:
                suggestion["stale"] = True
            render_table_ai()

        table_description.observe(table_description_changed, names="value")
        table_rules: dict[str, Any] = {}
        for kind, title in (("freshness", "Freshness"), ("source_drift", "Source Drift")):
            existing = next((r for r in guardrails if str(r.get("guardrail_type") or "").lower() == kind), {})
            existing_parameters = _parameters(existing)
            enabled = widgets.Checkbox(value=bool(existing and existing.get("is_active", True)), description="Enabled", disabled=not editable)
            block = widgets.Checkbox(value=str(existing.get("action") or "Warn") == "Block", description="Block on failure", disabled=not editable)
            column_names = [str(column.get("column_name") or "") for column in columns]
            parameter_controls: list[Any] = []
            if kind == "freshness":
                freshness_column = widgets.Dropdown(
                    options=column_names,
                    value=str(existing_parameters.get("freshness_column") or "") or None,
                    disabled=not editable,
                    **shared.widget_common(widgets, "Freshness column"),
                )
                maximum_age = widgets.Text(
                    value=str(existing_parameters.get("maximum_age") or ""), disabled=not editable,
                    **shared.widget_common(widgets, "Maximum age"),
                )
                maximum_age_unit = widgets.Dropdown(
                    options=("minutes", "hours", "days"),
                    value=str(existing_parameters.get("maximum_age_unit") or "days"), disabled=not editable,
                    **shared.widget_common(widgets, "Age unit"),
                )
                parameter_controls = [freshness_column, maximum_age, maximum_age_unit]
            else:
                partition_column = widgets.Dropdown(
                    options=column_names,
                    value=str(existing_parameters.get("partition_column") or "") or None,
                    disabled=not editable,
                    **shared.widget_common(widgets, "Partition column"),
                )
                change_column = widgets.Dropdown(
                    options=column_names,
                    value=str(existing_parameters.get("change_column") or "") or None,
                    disabled=not editable,
                    **shared.widget_common(widgets, "Change column"),
                )
                parameter_controls = [partition_column, change_column]
                if not str(table.get("load_strategy") or "").strip():
                    source_load_strategy = widgets.Dropdown(
                        options=("overwrite", "append", "scd1", "scd2"),
                        value=str(existing_parameters.get("load_strategy") or "") or None,
                        disabled=not editable,
                        **shared.widget_common(widgets, "Source load strategy"),
                    )
                    parameter_controls.append(source_load_strategy)
            save = widgets.Button(description=f"Save {title}", disabled=not editable)

            def save_table_rule(_button: Any, *, rule_kind: str = kind, old: dict[str, Any] = existing,
                                enabled_control: Any = enabled, block_control: Any = block,
                                controls: list[Any] = parameter_controls, rule_title: str = title) -> None:
                try:
                    if not enabled_control.value:
                        parameters = _parameters(old)
                    elif rule_kind == "freshness":
                        raw_age = str(controls[1].value or "").strip()
                        parameters = {
                            "freshness_column": str(controls[0].value or "").strip(),
                            "maximum_age": float(raw_age),
                            "maximum_age_unit": str(controls[2].value or "days"),
                        }
                    else:
                        parameters = {
                            "partition_column": str(controls[0].value or "").strip(),
                            "change_column": str(controls[1].value or "").strip(),
                        }
                        if len(controls) > 2:
                            parameters["load_strategy"] = str(controls[2].value or "").strip()
                    if enabled_control.value and any(value in {"", None} for value in parameters.values()):
                        raise ValueError(f"{rule_title} requires all governed configuration fields.")
                    save_guardrails([guardrail_record(
                        rule_kind, rule_kind, parameters, existing=old,
                        action="Block" if block_control.value else "Warn", active=enabled_control.value,
                    )])
                except (TypeError, ValueError, RuntimeError) as exc:
                    set_status(str(exc), error=True)

            save.on_click(save_table_rule)
            table_rules[kind] = {
                "enabled": enabled, "parameters": parameter_controls,
                "block": block, "save": save,
            }
        identity = widgets.HTML(
            "<p><b>{}</b><br>Contract v{} · {}<br>Environment: {}<br>Store: {} · {}</p>".format(
                html.escape(f"{table.get('schema_name') or ''}.{table.get('table_name') or state['table_id']}"),
                html.escape(str(row.get("contract_version") or "")), html.escape(str(row.get("status") or "").upper()),
                html.escape(env), html.escape(str(table.get("store_type") or "Metadata")),
                html.escape(str(table.get("layer") or "")),
            )
        )
        processing = (state.get("manifest") or {}).get("table", {}).get("processing", {})
        load_strategy = str(processing.get("load_strategy") or table.get("load_strategy") or "Not configured").upper()
        pipeline_refresh = widgets.HTML(
            "<div><b>Load strategy</b><br>"
            f"{html.escape(load_strategy)}</div><br>"
            + _scheduled_refresh_html(scheduled_refresh)
        )
        panes[0].children = (
            shared.form_section(widgets, title="Table identity & context", children=[identity]),
            shared.form_section(widgets, title="Pipeline / Refresh", children=[pipeline_refresh]),
            shared.form_section(widgets, title="Table Enrichment", children=[
                table_description, table_description_ai,
                shared.form_grid(widgets, [accept_table_description, rerun_table_description]),
                table_classification, table_classification_ai,
                shared.form_grid(widgets, [accept_table_classification, rerun_table_classification]),
                table_save,
            ]),
            shared.form_section(widgets, title="Table Guardrails", children=[
                shared.form_grid(widgets, [
                    shared.form_section(widgets, title="Freshness", children=[
                        widgets.HTML(
                            "<p>Freshness is the expected source-data arrival SLA; it is independent "
                            "of when Fabric schedules this notebook to run.</p>"
                        ),
                        table_rules["freshness"]["enabled"],
                        *table_rules["freshness"]["parameters"],
                        table_rules["freshness"]["block"], table_rules["freshness"]["save"],
                    ]),
                    shared.form_section(widgets, title="Source Drift", children=[
                        table_rules["source_drift"]["enabled"],
                        *table_rules["source_drift"]["parameters"],
                        table_rules["source_drift"]["block"], table_rules["source_drift"]["save"],
                    ]),
                ])
            ]),
        )

        # Columns: one editor, hydrated on selection, with profile evidence isolated from payload.
        required_rule = next((r for r in guardrails if str(r.get("guardrail_type") or "").lower() == "schema"), {})
        required_columns = set(_parameters(required_rule).get("required_columns", []))
        column_options = [
            (f"{c.get('column_name')}    {c.get('data_type')}    {'*' if c.get('column_id') in required_columns or c.get('column_name') in required_columns else ''}", str(c.get("column_id") or ""))
            for c in columns
        ]
        column_select = widgets.Select(options=column_options, **shared.widget_common(widgets, "Columns"))
        column_context = widgets.HTML()
        profile_context = shared.preview_region(widgets, widgets.HTML("<p>No column selected.</p>"), height="220px")
        column_description = widgets.Textarea(disabled=not editable, **shared.widget_common(widgets, "Description", textarea=True))
        column_classification = widgets.Dropdown(options=_CLASSIFICATIONS, disabled=not editable, **shared.widget_common(widgets, "Classification"))
        column_description_ai = widgets.HTML()
        column_classification_ai = widgets.HTML()
        accept_column_description = widgets.Button(description="Accept", disabled=not editable)
        rerun_column_description = widgets.Button(description="Re-run", disabled=not editable)
        accept_column_classification = widgets.Button(description="Accept", disabled=not editable)
        rerun_column_classification = widgets.Button(description="Re-run", disabled=not editable)
        required = widgets.Checkbox(description="Required", disabled=not editable)
        sensitive_enabled = widgets.Checkbox(description="Enabled", disabled=not editable)
        pii_type = widgets.Dropdown(
            options=[(label, value) for value, label in PII_LABELS.items()],
            value="none", disabled=not editable, **shared.widget_common(widgets, "PII assessment"),
        )
        pii_reason = widgets.Textarea(
            disabled=not editable, **shared.widget_common(widgets, "Reason", textarea=True)
        )
        sensitive_treatment = widgets.Dropdown(options=("tokenize", "mask", "bucket", "remove"), disabled=not editable, **shared.widget_common(widgets, "Treatment"))
        sensitive_action = widgets.Dropdown(options=("Warn", "Block"), disabled=not editable, **shared.widget_common(widgets, "On failure"))
        mask_start = widgets.Text(value="0", disabled=not editable, **shared.widget_common(widgets, "Mask: preserve start"))
        mask_end = widgets.Text(value="0", disabled=not editable, **shared.widget_common(widgets, "Mask: preserve end"))
        mask_character = widgets.Text(value="*", disabled=not editable, **shared.widget_common(widgets, "Mask character"))
        bucket_bins = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Bucket boundaries (comma-separated)"))
        bucket_labels = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Bucket labels (comma-separated)"))
        dq_type = widgets.Dropdown(options=_COLUMN_DQ_TYPES, disabled=not editable, **shared.widget_common(widgets, "Rule type"))
        dq_help = widgets.HTML()
        dq_max_missing = widgets.Text(value="0", disabled=not editable, **shared.widget_common(widgets, "Maximum missing %"))
        dq_blank_missing = widgets.Checkbox(value=False, description="Treat blank/whitespace text as missing", disabled=not editable)
        dq_value_mode = widgets.Dropdown(options=("allow", "block"), disabled=not editable, **shared.widget_common(widgets, "Mode"))
        dq_values = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Values (comma-separated)"))
        dq_minimum = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Minimum"))
        dq_minimum_inclusive = widgets.Checkbox(value=True, description="Minimum inclusive", disabled=not editable)
        dq_maximum = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Maximum"))
        dq_maximum_inclusive = widgets.Checkbox(value=True, description="Maximum inclusive", disabled=not editable)
        dq_pattern = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Pattern"))
        dq_parameter_controls = (
            dq_max_missing, dq_blank_missing, dq_value_mode, dq_values, dq_minimum,
            dq_minimum_inclusive, dq_maximum, dq_maximum_inclusive, dq_pattern,
        )
        dq_action = widgets.Dropdown(options=("Warn", "Block"), disabled=not editable, **shared.widget_common(widgets, "On failure"))
        dq_usage = widgets.HTML()
        save_column_enrichment = widgets.Button(description="Save enrichment", button_style="primary", disabled=not editable)
        save_required = widgets.Button(description="Save required state", disabled=not editable)
        save_sensitive = widgets.Button(description="Save Sensitive Data", disabled=not editable)
        sensitive_ai = widgets.HTML()
        accept_sensitive = widgets.Button(description="Accept suggestion", disabled=not editable)
        rerun_sensitive = widgets.Button(description="Re-run", disabled=not editable)
        save_dq = widgets.Button(description="Save Data Quality rule", disabled=not editable)
        suggest_dq = widgets.Button(description="Suggest rules", disabled=not editable or not ai_enrichment.get("enabled"))
        dq_suggestion = widgets.Select(options=(), disabled=True, **shared.widget_common(widgets, "AI suggestions"))
        accept_dq_suggestion = widgets.Button(description="Apply selected suggestion", disabled=True)
        dq_ai = widgets.HTML()
        draft_scope = (str(current["contract_id"]), int(current["contract_version"]))
        unsaved_columns: dict[str, dict[str, Any]] = state["_column_drafts"].setdefault(
            draft_scope, {}
        )

        def selected_column() -> dict[str, Any]:
            return next((c for c in columns if str(c.get("column_id") or "") == str(column_select.value or "")), {})

        hydrating = {"active": False}

        def hydrate_dq_family(column_id: str, kind: str) -> None:
            """Hydrate one column/family pair without borrowing another rule's parameters."""
            dq_max_missing.value = "0"
            dq_blank_missing.value = False
            dq_value_mode.value = "allow"
            dq_values.value = ""
            dq_minimum.value = ""
            dq_minimum_inclusive.value = True
            dq_maximum.value = ""
            dq_maximum_inclusive.value = True
            dq_pattern.value = ""
            dq_action.value = "Warn"
            rule = next((
                row for row in guardrails
                if str(row.get("guardrail_type") or "").lower() in {"data_quality", "dq"}
                and str(row.get("column_id") or "") == column_id
                and str(row.get("rule_type") or "") == kind
            ), {})
            if not rule:
                return
            params = _parameters(rule)
            dq_max_missing.value = str(params.get("maximum_missing_percent", 0))
            dq_blank_missing.value = bool(params.get("treat_blank_as_missing", False))
            dq_value_mode.value = str(params.get("mode") or "allow")
            dq_values.value = ", ".join(map(str, params.get("values", [])))
            dq_minimum.value = "" if params.get("minimum") is None else str(params["minimum"])
            dq_minimum_inclusive.value = bool(params.get("minimum_inclusive", True))
            dq_maximum.value = "" if params.get("maximum") is None else str(params["maximum"])
            dq_maximum_inclusive.value = bool(params.get("maximum_inclusive", True))
            dq_pattern.value = str(params.get("pattern") or "")
            dq_action.value = str(rule.get("action") or "Warn")

        def hydrate_column(column_id: str) -> None:
            hydrating["active"] = True
            selected = next((c for c in columns if str(c.get("column_id") or "") == column_id), {})
            column_context.value = (
                f"<h4>{html.escape(str(selected.get('column_name') or ''))}</h4>"
                f"<p>Datatype: <b>{html.escape(str(selected.get('data_type') or ''))}</b><br>"
                f"Required: <b>{'Yes' if column_id in required_columns or selected.get('column_name') in required_columns else 'No'}</b></p>"
            )
            column_description.value = enrichment_value(enrichments, "column", "Description", column_id)
            column_classification.value = enrichment_value(enrichments, "column", "Classification", column_id)
            required.value = column_id in required_columns or selected.get("column_name") in required_columns
            sensitive = next((r for r in guardrails if str(r.get("guardrail_type") or "").lower() == "sensitive_data" and str(r.get("column_id") or "") == column_id), {})
            sensitive_parameters = _parameters(sensitive)
            pii_type.value = str(sensitive_parameters.get("pii_type") or (
                "direct" if sensitive else "none"
            ))
            pii_reason.value = str(sensitive_parameters.get("pii_reason") or "")
            sensitive_enabled.value = bool(sensitive and sensitive.get("is_active", True))
            sensitive_treatment.value = str(sensitive_parameters.get("treatment") or "tokenize")
            sensitive_action.value = str(sensitive.get("action") or "Warn")
            mask_start.value = str(sensitive_parameters.get("preserve_start", 0))
            mask_end.value = str(sensitive_parameters.get("preserve_end", 0))
            mask_character.value = str(sensitive_parameters.get("mask_character") or "*")
            bucket_bins.value = ", ".join(map(str, sensitive_parameters.get("bins", [])))
            bucket_labels.value = ", ".join(map(str, sensitive_parameters.get("labels", [])))
            configured = [
                str(rule.get("rule_type") or "") for rule in guardrails
                if str(rule.get("guardrail_type") or "").lower() in {"data_quality", "dq"}
                and str(rule.get("column_id") or "") == column_id
                and str(rule.get("rule_type") or "") in _COLUMN_DQ_TYPES
                and rule.get("is_active", True)
            ]
            dq_type.value = configured[0] if configured else _COLUMN_DQ_TYPES[0]
            hydrate_dq_family(column_id, str(dq_type.value))
            pending = unsaved_columns.get(column_id)
            if pending:
                column_description.value = pending["description"]
                column_classification.value = pending["classification"]
                required.value = pending["required"]
                sensitive_enabled.value = pending["sensitive_enabled"]
                pii_type.value = pending["pii_type"]
                pii_reason.value = pending["pii_reason"]
                sensitive_treatment.value = pending["sensitive_treatment"]
                sensitive_action.value = pending["sensitive_action"]
                mask_start.value = pending["mask_start"]
                mask_end.value = pending["mask_end"]
                mask_character.value = pending["mask_character"]
                bucket_bins.value = pending["bucket_bins"]
                bucket_labels.value = pending["bucket_labels"]
                dq_type.value = pending["dq_type"]
                for control, value in zip(dq_parameter_controls, pending["dq_parameters"], strict=True):
                    control.value = value
                dq_action.value = pending["dq_action"]
            try:
                profile_context.value = _profile_html(load_profile_context(column_id))
            except (ValueError, RuntimeError) as exc:
                profile_context.value = f"<p>{html.escape(str(exc))}</p>"
            finally:
                hydrating["active"] = False

        def update_dq_help(change: dict[str, Any] | None = None) -> None:
            kind = str(dq_type.value or "")
            count = sum(1 for rule in guardrails if str(rule.get("rule_type") or "") == kind and rule.get("is_active", True))
            dq_help.value = f"<p>{html.escape(_DQ_HELP[kind])}</p>"
            dq_usage.value = f"<p>{count} current configuration(s) use this rule type.</p>"
            visible = {
                "completeness": {dq_max_missing, dq_blank_missing},
                "uniqueness": set(),
                "value_set": {dq_value_mode, dq_values},
                "range": {dq_minimum, dq_minimum_inclusive, dq_maximum, dq_maximum_inclusive},
                "pattern": {dq_pattern},
            }[kind]
            for control in dq_parameter_controls:
                control.layout.display = "" if control in visible else "none"
            selected_id = str(column_select.value or "")
            if selected_id and not hydrating["active"]:
                hydrating["active"] = True
                try:
                    hydrate_dq_family(selected_id, kind)
                finally:
                    hydrating["active"] = False

        dq_type.observe(update_dq_help, names="value")
        update_dq_help()

        def update_sensitive_fields(change: dict[str, Any] | None = None) -> None:
            treatment = str(sensitive_treatment.value or "")
            for control in (mask_start, mask_end, mask_character):
                control.layout.display = "" if treatment == "mask" else "none"
            for control in (bucket_bins, bucket_labels):
                control.layout.display = "" if treatment == "bucket" else "none"

        sensitive_treatment.observe(update_sensitive_fields, names="value")
        update_sensitive_fields()

        def update_pii_fields(change: dict[str, Any] | None = None) -> None:
            is_pii = str(pii_type.value or "none") != "none"
            if not is_pii:
                sensitive_enabled.value = False
            sensitive_treatment.disabled = not editable or not is_pii
            sensitive_action.disabled = not editable or not is_pii
            update_sensitive_fields()

        pii_type.observe(update_pii_fields, names="value")
        update_pii_fields()

        def column_changed(change: dict[str, Any]) -> None:
            old = str(change.get("old") or "")
            if old:
                unsaved_columns[old] = {
                    "description": column_description.value,
                    "classification": column_classification.value,
                    "required": required.value,
                    "sensitive_enabled": sensitive_enabled.value,
                    "pii_type": pii_type.value,
                    "pii_reason": pii_reason.value,
                    "sensitive_treatment": sensitive_treatment.value,
                    "sensitive_action": sensitive_action.value,
                    "mask_start": mask_start.value,
                    "mask_end": mask_end.value,
                    "mask_character": mask_character.value,
                    "bucket_bins": bucket_bins.value,
                    "bucket_labels": bucket_labels.value,
                    "dq_type": dq_type.value,
                    "dq_parameters": [control.value for control in dq_parameter_controls],
                    "dq_action": dq_action.value,
                }
                set_status("Unsaved column edits were retained locally; use the section Save action to persist them.")
            if change.get("new"):
                selected_id = str(change["new"])
                hydrate_column(selected_id)
                prepare_column_ai(selected_id)

        column_select.observe(column_changed, names="value")

        def _suggestion_html(label: str, suggestion: dict[str, Any] | None) -> str:
            if not suggestion:
                return "<p><b>AI suggestion</b><br><span style=\"color:#666\">Preparing…</span></p>"
            stale = " · <b>Needs refresh</b>" if suggestion.get("stale") else ""
            error = suggestion.get("error")
            if error:
                return (
                    "<p><b>AI suggestion</b><br><span style=\"color:#a4262c\">"
                    f"{html.escape(str(error))}</span></p>"
                )
            value = suggestion.get("value")
            if label == "Sensitive Data":
                value = (
                    f"<b>{html.escape(str(suggestion.get('pii_label') or ''))}</b><br>"
                    f"{html.escape(str(suggestion.get('reason') or ''))}<br>"
                    f"Treatment: {html.escape(str(suggestion.get('treatment') or 'None'))} · "
                    f"Action: {html.escape(str(suggestion.get('action') or 'None'))}"
                )
            else:
                value = html.escape(str(value or ""))
            return f"<p><b>AI suggestion</b>{stale}<br>{value}</p>"

        def _column_editable_values(column_id: str) -> tuple[str, str]:
            if str(column_select.value or "") == column_id:
                return str(column_description.value or ""), str(column_classification.value or "")
            pending = unsaved_columns.get(column_id, {})
            return (
                str(pending.get("description", enrichment_value(
                    enrichments, "column", "Description", column_id
                )) or ""),
                str(pending.get("classification", enrichment_value(
                    enrichments, "column", "Classification", column_id
                )) or ""),
            )

        def render_column_ai(column_id: str) -> None:
            suggestions = ai_state["columns"].get(column_id, {})
            if not ai_enrichment.get("enabled"):
                disabled_message = "<p><b>AI suggestion</b><br>Disabled in 00_env_config.</p>"
                column_description_ai.value = disabled_message
                column_classification_ai.value = disabled_message
                sensitive_ai.value = disabled_message
            elif not editable:
                review_message = "<p><b>AI suggestion</b><br>Not run for review-only versions.</p>"
                column_description_ai.value = review_message
                column_classification_ai.value = review_message
                sensitive_ai.value = review_message
            else:
                column_description_ai.value = _suggestion_html(
                    "Description", suggestions.get("description")
                )
                column_classification_ai.value = _suggestion_html(
                    "Classification", suggestions.get("classification")
                )
                sensitive_ai.value = _suggestion_html(
                    "Sensitive Data", suggestions.get("sensitive_data")
                )
            available = editable and bool(ai_enrichment.get("enabled"))
            accept_column_description.disabled = not (
                available and suggestions.get("description") and not suggestions["description"].get("error")
            )
            accept_column_classification.disabled = not (
                available and suggestions.get("classification") and not suggestions["classification"].get("error")
            )
            accept_sensitive.disabled = not (
                available and suggestions.get("sensitive_data") and not suggestions["sensitive_data"].get("error")
            )
            rerun_column_description.disabled = not available
            rerun_column_classification.disabled = not available
            rerun_sensitive.disabled = not available

        def run_column_enrichment_ai(column_id: str, *, force: bool = False) -> None:
            suggestions = ai_state["columns"].setdefault(column_id, {})
            if not force and suggestions.get("description") and suggestions.get("classification"):
                render_column_ai(column_id)
                return
            selected = next(
                (column for column in columns if str(column.get("column_id") or "") == column_id), {}
            )
            description, _classification = _column_editable_values(column_id)
            try:
                profile_value = load_profile_context(column_id)
                result = suggest_enrichment(
                    build_ai_enrichment_context(
                        selected,
                        metadata_level="column",
                        existing_description=description,
                        classification_labels=classification_labels,
                        profile_rows=[dict(profile_value.get("profile") or {})],
                    ),
                    description_prompt=str(ai_enrichment.get("description_prompt") or ""),
                    classification_prompt=str(ai_enrichment.get("classification_prompt") or ""),
                    classification_labels=classification_labels,
                )
                suggestions["description"] = {"value": result["Description"], "stale": False}
                suggestions["classification"] = {
                    "value": result["Classification"], "stale": False
                }
                ai_errors.pop((column_id, "enrichment"), None)
            except (TypeError, ValueError, RuntimeError) as exc:
                message = str(exc)
                suggestions.setdefault("description", {"error": message, "stale": False})
                suggestions.setdefault("classification", {"error": message, "stale": False})
                ai_errors[(column_id, "enrichment")] = message
                set_status(f"AI suggestions unavailable for this column: {message}", warning=True)
            render_column_ai(column_id)

        def run_sensitive_ai(column_id: str, *, force: bool = False) -> None:
            suggestions = ai_state["columns"].setdefault(column_id, {})
            if not force and suggestions.get("sensitive_data"):
                render_column_ai(column_id)
                return
            selected = next(
                (column for column in columns if str(column.get("column_id") or "") == column_id), {}
            )
            description, classification = _column_editable_values(column_id)
            try:
                profile_value = load_profile_context(column_id)
                profile = dict(profile_value.get("profile") or {})
                context_value = build_ai_sensitive_data_context({
                    "table_id": state.get("table_id"),
                    "table_name": table.get("table_name"),
                    "schema_name": table.get("schema_name"),
                    "layer": table.get("layer"),
                    "contract_id": current.get("contract_id"),
                    "contract_version": current.get("contract_version"),
                    "table_description": table_description.value,
                    "table_classification": table_classification.value,
                    "catalogue_profile_rows": [{
                        **dict(selected), "description": description,
                        "classification": classification,
                        **{name: profile.get(name) for name in (
                            "row_count", "non_null_count", "null_count", "null_percent",
                            "distinct_count", "distinct_percent", "min_value", "max_value",
                        ) if profile.get(name) is not None},
                        "frequency_evidence": [
                            {"count": item.get("count")} for item in profile_value.get("values", [])
                        ],
                    }],
                })
                result = suggest_sensitive_data(
                    context_value, prompt=str(ai_enrichment.get("sensitive_data_prompt") or "")
                )
                if len(result) != 1:
                    raise ValueError("AI Sensitive Data response must assess the selected column once.")
                suggestions["sensitive_data"] = {**result[0], "stale": False}
                ai_errors.pop((column_id, "sensitive_data"), None)
            except (TypeError, ValueError, RuntimeError) as exc:
                message = str(exc)
                suggestions["sensitive_data"] = {"error": message, "stale": False}
                ai_errors[(column_id, "sensitive_data")] = message
                set_status(
                    f"Sensitive Data AI unavailable for this column: {message}", warning=True
                )
            render_column_ai(column_id)

        def prepare_column_ai(column_id: str) -> None:
            if not editable or not ai_enrichment.get("enabled") or not column_id:
                render_column_ai(column_id)
                return
            run_column_enrichment_ai(column_id)
            run_sensitive_ai(column_id)

        def accept_description_clicked(_button: Any) -> None:
            suggestion = ai_state["columns"].get(str(column_select.value or ""), {}).get("description", {})
            if not suggestion.get("error"):
                column_description.value = str(suggestion.get("value") or "")

        def accept_classification_clicked(_button: Any) -> None:
            suggestion = ai_state["columns"].get(str(column_select.value or ""), {}).get("classification", {})
            if not suggestion.get("error"):
                column_classification.value = str(suggestion.get("value") or "")

        def accept_sensitive_clicked(_button: Any) -> None:
            suggestion = ai_state["columns"].get(str(column_select.value or ""), {}).get("sensitive_data", {})
            if not suggestion or suggestion.get("error"):
                return
            pii_type.value = str(suggestion["pii_type"])
            pii_reason.value = str(suggestion["reason"])
            sensitive_enabled.value = suggestion["pii_type"] != "none"
            sensitive_treatment.value = str(suggestion.get("treatment") or "mask")
            sensitive_action.value = str(suggestion.get("action") or "Warn")
            parameters = suggestion.get("parameters", {})
            mask_start.value = str(parameters.get("preserve_start", 0))
            mask_end.value = str(parameters.get("preserve_end", 0))
            mask_character.value = str(parameters.get("mask_character", "*"))
            bucket_bins.value = ", ".join(map(str, parameters.get("bins", [])))
            bucket_labels.value = ", ".join(map(str, parameters.get("labels", [])))

        accept_column_description.on_click(accept_description_clicked)
        accept_column_classification.on_click(accept_classification_clicked)
        accept_sensitive.on_click(accept_sensitive_clicked)
        rerun_column_description.on_click(
            lambda _button: run_column_enrichment_ai(str(column_select.value or ""), force=True)
        )
        rerun_column_classification.on_click(
            lambda _button: run_column_enrichment_ai(str(column_select.value or ""), force=True)
        )
        rerun_sensitive.on_click(
            lambda _button: run_sensitive_ai(str(column_select.value or ""), force=True)
        )

        def description_changed(_change: dict[str, Any]) -> None:
            if hydrating["active"]:
                return
            column_id = str(column_select.value or "")
            suggestions = ai_state["columns"].get(column_id, {})
            for name in ("classification", "sensitive_data"):
                if suggestions.get(name):
                    suggestions[name]["stale"] = True
            render_column_ai(column_id)

        def classification_changed(_change: dict[str, Any]) -> None:
            if hydrating["active"]:
                return
            column_id = str(column_select.value or "")
            suggestion = ai_state["columns"].get(column_id, {}).get("sensitive_data")
            if suggestion:
                suggestion["stale"] = True
            render_column_ai(column_id)

        column_description.observe(description_changed, names="value")
        column_classification.observe(classification_changed, names="value")

        def save_column_enrichment_clicked(_button: Any) -> None:
            try:
                cid = str(column_select.value or "")
                save_enrichment([
                    enrichment_record("column", "Description", column_description.value, cid),
                    enrichment_record("column", "Classification", column_classification.value, cid),
                ])
            except (ValueError, RuntimeError) as exc:
                set_status(str(exc), error=True)

        def save_required_clicked(_button: Any) -> None:
            selected = selected_column()
            cid = str(selected.get("column_id") or "")
            updated = set(required_columns)
            identifier = cid or str(selected.get("column_name") or "")
            (updated.add if required.value else updated.discard)(identifier)
            try:
                save_guardrails([guardrail_record(
                    "schema", "required_columns", {"required_columns": sorted(updated)}, existing=required_rule,
                )])
            except (ValueError, RuntimeError) as exc:
                set_status(str(exc), error=True)

        def save_sensitive_clicked(_button: Any) -> None:
            try:
                cid = str(column_select.value or "")
                existing = next((r for r in guardrails if str(r.get("guardrail_type") or "").lower() == "sensitive_data" and str(r.get("column_id") or "") == cid), {})
                if str(pii_type.value or "none") == "none" and sensitive_enabled.value:
                    raise ValueError("Enable a Sensitive Data rule only for Direct or Indirect PII.")
                parameters: dict[str, Any] = {
                    "scope": "column", "treatment": sensitive_treatment.value,
                }
                if str(pii_type.value or "none") != "none":
                    if not str(pii_reason.value or "").strip():
                        raise ValueError(
                            "Explain why this column is Direct or Indirect PII."
                        )
                    parameters.update({
                        "pii_type": str(pii_type.value),
                        "pii_reason": str(pii_reason.value or "").strip(),
                    })
                if sensitive_treatment.value == "mask":
                    parameters.update({
                        "preserve_start": int(mask_start.value),
                        "preserve_end": int(mask_end.value),
                        "mask_character": mask_character.value,
                    })
                elif sensitive_treatment.value == "bucket":
                    parameters.update({
                        "bins": [float(value.strip()) for value in bucket_bins.value.split(",") if value.strip()],
                        "labels": [value.strip() for value in bucket_labels.value.split(",") if value.strip()],
                    })
                save_guardrails([guardrail_record(
                    "sensitive_data", str(sensitive_treatment.value), parameters, column_id=cid,
                    action=str(sensitive_action.value), existing=existing, active=sensitive_enabled.value,
                )])
            except (ValueError, RuntimeError) as exc:
                set_status(str(exc), error=True)

        def save_dq_clicked(_button: Any) -> None:
            try:
                cid = str(column_select.value or "")
                selected = selected_column()
                kind = str(dq_type.value)
                params: dict[str, Any] = {"columns": [str(selected.get("column_name") or cid)]}
                if kind == "completeness":
                    params.update({
                        "maximum_missing_percent": float(dq_max_missing.value),
                        "treat_blank_as_missing": bool(dq_blank_missing.value),
                    })
                elif kind == "value_set":
                    values = [item.strip() for item in dq_values.value.split(",") if item.strip()]
                    if not values:
                        raise ValueError("value_set requires at least one configured value.")
                    params.update({"mode": str(dq_value_mode.value), "values": values})
                elif kind == "range":
                    if not dq_minimum.value.strip() and not dq_maximum.value.strip():
                        raise ValueError("range requires a minimum or maximum.")
                    params.update({
                        "minimum": dq_minimum.value.strip() or None,
                        "minimum_inclusive": bool(dq_minimum_inclusive.value),
                        "maximum": dq_maximum.value.strip() or None,
                        "maximum_inclusive": bool(dq_maximum_inclusive.value),
                    })
                elif kind == "pattern":
                    if not dq_pattern.value.strip():
                        raise ValueError("pattern requires a regular expression.")
                    params["pattern"] = dq_pattern.value
                existing = next((r for r in guardrails if str(r.get("guardrail_type") or "").lower() in {"data_quality", "dq"} and str(r.get("column_id") or "") == cid and str(r.get("rule_type") or "") == kind), {})
                save_guardrails([guardrail_record(
                    "data_quality", kind, params, column_id=cid,
                    action=str(dq_action.value), existing=existing,
                )])
            except (TypeError, ValueError, RuntimeError) as exc:
                set_status(str(exc), error=True)

        def suggest_dq_clicked(_button: Any) -> None:
            """Generate transient standard-rule advice and hydrate controls only on acceptance."""
            try:
                selected = selected_column()
                profile_value = load_profile_context(str(selected.get("column_id") or ""))
                profile = dict(profile_value.get("profile") or {})
                context_payload = build_ai_dq_context({
                    "table_name": table.get("table_name"), "schema_name": table.get("schema_name"),
                    "layer": table.get("layer"), "table_description": table_description.value,
                    "table_classification": table_classification.value,
                    "catalogue_profile_rows": [{
                        **selected, "description": column_description.value,
                        "classification": column_classification.value,
                        **{name: profile.get(name) for name in (
                            "row_count", "non_null_count", "null_count", "null_percent",
                            "distinct_count", "distinct_percent", "min_value", "max_value",
                        ) if profile.get(name) is not None},
                        "frequency_evidence": [
                            {"count": item.get("count")} for item in profile_value.get("values", [])
                        ],
                    }],
                })
                suggestions = suggest_dq_rules(
                    context_payload, prompt=str(ai_enrichment.get("dq_prompt") or ""),
                )
                state["_ai_suggestions"][suggestion_scope]["dq"] = suggestions
                dq_suggestion.options = [
                    (f"{item['rule_type']} · {item['columns'][0]}", str(index))
                    for index, item in enumerate(suggestions) if item["selected"]
                ]
                dq_suggestion.disabled = not bool(dq_suggestion.options)
                accept_dq_suggestion.disabled = not bool(dq_suggestion.options)
                dq_ai.value = "<p><b>Transient suggestions</b></p><ul>" + "".join(
                    f"<li>{html.escape(item['rule_type'])}: {html.escape(item['rationale'])}</li>"
                    for item in suggestions
                ) + "</ul><p>Select and edit a rule before saving; suggestions are never persisted automatically.</p>"
            except (TypeError, ValueError, RuntimeError) as exc:
                dq_ai.value = f"<p style='color:#a4262c'>{html.escape(str(exc))}</p>"

        def accept_dq_clicked(_button: Any) -> None:
            suggestions = state["_ai_suggestions"][suggestion_scope].get("dq", [])
            if dq_suggestion.value in (None, ""):
                return
            suggestion = suggestions[int(dq_suggestion.value)]
            dq_type.value = suggestion["rule_type"]
            params = suggestion["parameters"]
            dq_max_missing.value = str(params.get("maximum_missing_percent", 0))
            dq_blank_missing.value = bool(params.get("treat_blank_as_missing", False))
            dq_value_mode.value = str(params.get("mode") or "allow")
            dq_values.value = ", ".join(map(str, params.get("values", [])))
            dq_minimum.value = "" if params.get("minimum") is None else str(params["minimum"])
            dq_minimum_inclusive.value = bool(params.get("minimum_inclusive", True))
            dq_maximum.value = "" if params.get("maximum") is None else str(params["maximum"])
            dq_maximum_inclusive.value = bool(params.get("maximum_inclusive", True))
            dq_pattern.value = str(params.get("pattern") or "")

        save_column_enrichment.on_click(save_column_enrichment_clicked)
        save_required.on_click(save_required_clicked)
        save_sensitive.on_click(save_sensitive_clicked)
        save_dq.on_click(save_dq_clicked)
        suggest_dq.on_click(suggest_dq_clicked)
        accept_dq_suggestion.on_click(accept_dq_clicked)
        panes[1].children = (shared.authoring_workspace(
            widgets,
            target=[column_select],
            selection=[column_context, widgets.HTML("<b>Profile evidence</b>"), profile_context],
            configuration=[
                shared.form_section(widgets, title="Enrichment", children=[
                    column_description, column_description_ai,
                    shared.form_grid(widgets, [accept_column_description, rerun_column_description]),
                    column_classification, column_classification_ai,
                    shared.form_grid(widgets, [accept_column_classification, rerun_column_classification]),
                    save_column_enrichment,
                ]),
                shared.form_section(widgets, title="Schema", children=[required, save_required]),
                shared.form_section(widgets, title="Sensitive Data", children=[sensitive_ai, accept_sensitive, rerun_sensitive, pii_type, pii_reason, sensitive_enabled, sensitive_treatment, mask_start, mask_end, mask_character, bucket_bins, bucket_labels, sensitive_action, save_sensitive]),
                shared.form_section(widgets, title="Data Quality", children=[
                    dq_type, dq_help, dq_usage, *dq_parameter_controls, dq_action,
                    suggest_dq, dq_suggestion, accept_dq_suggestion, dq_ai, save_dq,
                ]),
            ], titles=("Columns", "Selected column context", "Configuration"),
        ),)
        if column_options:
            column_select.value = column_options[0][1]
            hydrate_column(str(column_select.value))
            prepare_column_ai(str(column_select.value))
        run_table_ai()

        # Advanced: controlled multi-column rule types, saved configurations, no raw JSON editor.
        advanced_type = widgets.Select(options=_ADVANCED_TYPES, **shared.widget_common(widgets, "Rule type"))
        advanced_saved = widgets.Select(**shared.widget_common(widgets, "Saved configurations"))
        advanced_columns = widgets.SelectMultiple(
            options=[(str(c.get("column_name") or ""), str(c.get("column_name") or "")) for c in columns],
            disabled=not editable, **shared.widget_common(widgets, "Columns"),
        )
        advanced_operator = widgets.Dropdown(options=("=", "!=", ">", ">=", "<", "<="), disabled=not editable, **shared.widget_common(widgets, "Operator"))
        custom_expression = widgets.Textarea(disabled=not editable, **shared.widget_common(widgets, "PySpark boolean Column expression", textarea=True))
        custom_description = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Description"))
        advanced_action = widgets.Dropdown(options=("Warn", "Block"), disabled=not editable, **shared.widget_common(widgets, "On failure"))
        advanced_help = widgets.HTML()
        advanced_save = widgets.Button(description="Save configuration", button_style="primary", disabled=not editable)
        advanced_lookup: dict[str, dict[str, Any]] = {}

        def hydrate_advanced_type(change: dict[str, Any] | None = None) -> None:
            kind = str(advanced_type.value or "")
            advanced_help.value = f"<p>{html.escape(_DQ_HELP[kind])}</p>"
            advanced_save.disabled = not editable
            advanced_columns.layout.display = "none" if kind == "custom_expression" else ""
            advanced_operator.layout.display = "" if kind == "column_relationship" else "none"
            custom_expression.layout.display = "" if kind == "custom_expression" else "none"
            custom_description.layout.display = "" if kind == "custom_expression" else "none"
            matching = [r for r in guardrails if str(r.get("rule_type") or "") == kind]
            advanced_lookup.clear()
            options = []
            for rule in matching:
                label = ", ".join(map(str, _parameters(rule).get("columns", []))) or str(rule.get("rule_id") or "Configuration")
                key = str(rule.get("guardrail_rule_id") or rule.get("rule_id") or label)
                advanced_lookup[key] = rule
                options.append((label, key))
            advanced_saved.options = options

        def hydrate_advanced_saved(change: dict[str, Any]) -> None:
            rule = advanced_lookup.get(str(change.get("new") or ""), {})
            params = _parameters(rule)
            advanced_columns.value = tuple(name for name in params.get("columns", []) if name in {value for _label, value in advanced_columns.options})
            advanced_operator.value = str(params.get("operator") or params.get("condition_operator") or "=")
            custom_expression.value = str(params.get("expression") or "")
            custom_description.value = str(params.get("description") or "")
            advanced_action.value = str(rule.get("action") or "Warn")

        def save_advanced_clicked(_button: Any) -> None:
            kind = str(advanced_type.value or "")
            params: dict[str, Any] = {"columns": list(advanced_columns.value)}
            if kind == "uniqueness" and len(params["columns"]) < 2:
                set_status("Composite uniqueness requires at least two columns.", error=True)
                return
            if kind == "column_relationship":
                if len(params["columns"]) != 2:
                    set_status("Column relationship requires exactly two columns.", error=True)
                    return
                params["operator"] = advanced_operator.value
            elif kind == "custom_expression":
                params = {
                    "expression_language": "pyspark", "expression": custom_expression.value.strip(),
                    "description": custom_description.value.strip(),
                }
            existing = advanced_lookup.get(str(advanced_saved.value or ""), {})
            try:
                save_guardrails([guardrail_record(
                    "data_quality", kind, params, action=str(advanced_action.value), existing=existing,
                )])
            except (ValueError, RuntimeError) as exc:
                set_status(str(exc), error=True)

        advanced_type.observe(hydrate_advanced_type, names="value")
        advanced_saved.observe(hydrate_advanced_saved, names="value")
        advanced_save.on_click(save_advanced_clicked)
        hydrate_advanced_type()
        panes[0].children = (*panes[0].children, shared.form_section(
            widgets, title="Table Data Quality", children=[shared.authoring_workspace(
            widgets, target=[advanced_type], selection=[advanced_saved], configuration=[
                advanced_help, advanced_columns, advanced_operator, custom_expression,
                custom_description, advanced_action, advanced_save,
            ], titles=("Rule type", "Saved configurations / affected columns", "Selected / new configuration"),
        )]),)

        # Manifest: compact navigation and bounded selected-section review.
        payload = state.get("manifest") or {}
        sections = _manifest_sections(payload)
        manifest_nav = widgets.Select(options=list(sections), **shared.widget_common(widgets, "Section"))
        manifest_preview = shared.preview_region(widgets, widgets.HTML(), height="500px")

        def manifest_section_changed(change: dict[str, Any]) -> None:
            manifest_preview.value = sections.get(str(change.get("new") or ""), "")

        manifest_nav.observe(manifest_section_changed, names="value")
        manifest_preview.value = sections.get(str(manifest_nav.value or ""), "")
        exact_json = shared.preview_region(
            widgets, widgets.HTML(
                f"<details><summary>Exact JSON manifest</summary><pre>{html.escape(_expose_manifest(payload))}</pre></details>"
            ), height="240px",
        )
        actions: list[Any] = []
        if editable:
            freeze_button = widgets.Button(description=f"Freeze v{row['contract_version']}", button_style="primary")

            def freeze_clicked(_button: Any) -> None:
                try:
                    freeze()
                    render()
                    set_status(f"Data Contract v{row['contract_version']} is FROZEN.")
                except (ValueError, RuntimeError) as exc:
                    set_status(str(exc), error=True)

            freeze_button.on_click(freeze_clicked)
            actions.append(freeze_button)
        else:
            agreement_id = widgets.Text(**shared.widget_common(widgets, "Data Agreement ID"))
            agreement_version = widgets.Text(**shared.widget_common(widgets, "Agreement version"))
            activate_button = widgets.Button(
                description="Activate for Production",
                disabled=str(row.get("status") or "").lower() not in {"frozen", "superseded"},
            )

            def activate_clicked(_button: Any) -> None:
                try:
                    activate(agreement_id.value, agreement_version.value)
                    render()
                    set_status(f"Data Contract v{row['contract_version']} is ACTIVE for Production.")
                except (ValueError, RuntimeError) as exc:
                    set_status(str(exc), error=True)

            activate_button.on_click(activate_clicked)
            actions.extend([agreement_id, agreement_version, activate_button])
        panes[2].children = (shared.authoring_workspace(
            widgets, target=[manifest_nav, widgets.HTML("<p><b>Notebook variable</b><br>DATA_CONTRACT_MANIFEST</p>")],
            selection=[manifest_preview], configuration=[exact_json, *actions],
            titles=("Section summary", "Human-readable review", "Exact manifest & lifecycle"),
        ),)

        state["_controls"].update({
            "table_description": table_description, "table_classification": table_classification,
            "table_save": table_save, "table_guardrails": table_rules,
            "pipeline_refresh": pipeline_refresh,
            "table_description_ai": table_description_ai,
            "table_classification_ai": table_classification_ai,
            "accept_table_description": accept_table_description,
            "rerun_table_description": rerun_table_description,
            "accept_table_classification": accept_table_classification,
            "rerun_table_classification": rerun_table_classification,
            "column_select": column_select, "column_context": column_context,
            "profile_context": profile_context, "column_description": column_description,
            "column_classification": column_classification, "required": required,
            "save_column_enrichment": save_column_enrichment, "save_required": save_required,
            "sensitive_enabled": sensitive_enabled, "sensitive_treatment": sensitive_treatment,
            "column_description_ai": column_description_ai,
            "column_classification_ai": column_classification_ai,
            "accept_column_description": accept_column_description,
            "rerun_column_description": rerun_column_description,
            "accept_column_classification": accept_column_classification,
            "rerun_column_classification": rerun_column_classification,
            "pii_type": pii_type, "pii_reason": pii_reason,
            "sensitive_ai": sensitive_ai, "accept_sensitive": accept_sensitive,
            "rerun_sensitive": rerun_sensitive,
            "sensitive_action": sensitive_action, "mask_start": mask_start,
            "mask_end": mask_end, "mask_character": mask_character,
            "bucket_bins": bucket_bins, "bucket_labels": bucket_labels,
            "save_sensitive": save_sensitive,
            "dq_type": dq_type, "dq_parameter_controls": dq_parameter_controls,
            "dq_max_missing": dq_max_missing, "dq_blank_missing": dq_blank_missing,
            "dq_value_mode": dq_value_mode, "dq_values": dq_values,
            "dq_minimum": dq_minimum, "dq_minimum_inclusive": dq_minimum_inclusive,
            "dq_maximum": dq_maximum, "dq_maximum_inclusive": dq_maximum_inclusive,
            "dq_pattern": dq_pattern, "suggest_dq": suggest_dq, "dq_ai": dq_ai,
            "dq_suggestion": dq_suggestion, "accept_dq_suggestion": accept_dq_suggestion,
            "dq_action": dq_action, "save_dq": save_dq,
            "advanced_type": advanced_type, "advanced_saved": advanced_saved,
            "advanced_columns": advanced_columns, "advanced_save": advanced_save,
            "advanced_operator": advanced_operator, "custom_expression": custom_expression,
            "custom_description": custom_description,
            "manifest_nav": manifest_nav, "manifest_preview": manifest_preview,
            "freeze": next((control for control in actions if getattr(control, "description", "").startswith("Freeze")), None),
            "activate": next((control for control in actions if getattr(control, "description", "").startswith("Activate")), None),
        })

    def table_changed(change: dict[str, Any]) -> None:
        selected = str(change.get("new") or "")
        state["table_id"] = selected or None
        matches = [row for row in state["contracts"] if str(row.get("table_id") or "") == selected]
        contract_control.options = [
            *[(f"v{row['contract_version']} · {str(row.get('status') or '').title()}", str(row["contract_version"])) for row in matches],
            ("New draft", "new"),
        ]
        if matches:
            contract_control.value = str(matches[0]["contract_version"])
        else:
            render()

    def contract_changed(change: dict[str, Any]) -> None:
        value = change.get("new")
        if not state.get("table_id") or not value:
            return
        try:
            if value == "new":
                new_draft()
            else:
                select(str(state["table_id"]), int(value))
            render()
        except (ValueError, RuntimeError) as exc:
            set_status(str(exc), error=True)

    table_control.observe(table_changed, names="value")
    contract_control.observe(contract_changed, names="value")
    if table_control.value:
        table_changed({"new": table_control.value})
    render()
    page = shared.form_page(
        widgets, title="Data Contract",
        description="Select, author, review, freeze, and activate one governed table contract.",
        children=[selector, tabs, status],
    )
    state["_controls"]["page"] = page
    ip.display(page)
    return state
