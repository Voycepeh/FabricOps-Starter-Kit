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
_TABS = ("Table", "Columns", "Advanced", "Manifest & Freeze")
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
    """Build one scannable manifest review page with expandable rule detail."""
    table = payload.get("table", {})
    contract = payload.get("contract", {})
    enrichments = payload.get("enrichment", {})
    guardrails = payload.get("guardrails", [])
    columns = table.get("columns", [])
    description_by_column = {
        str(row.get("column_id") or ""): str(row.get("value") or "")
        for row in enrichments.get("columns", [])
        if row.get("enrichment_type") == "Description"
    }
    required: set[str] = set()
    for rule in guardrails:
        if str(rule.get("guardrail_type") or "").lower() == "schema" and rule.get("is_active", True):
            required.update(_parameters(rule).get("required_columns", []))

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
    advanced = [
        row for row in table_dq
        if str(row.get("rule_type") or "") in {"uniqueness", "column_relationship", "custom_expression"}
    ]
    blocking = [row for row in active if str(row.get("action") or "").lower() == "block"]
    required_count = sum(
        1 for row in columns
        if row.get("column_id") in required or row.get("column_name") in required
    )
    column_rows = "".join(
        "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            html.escape(str(row.get("column_name") or "")),
            html.escape(str(row.get("data_type") or "")),
            "Yes" if row.get("column_id") in required or row.get("column_name") in required else "No",
            html.escape(description_by_column.get(str(row.get("column_id") or ""), "")),
        )
        for row in columns
    )
    summary = (
        "<h3>Contract summary</h3>"
        "<div style='display:grid;grid-template-columns:repeat(4,minmax(120px,1fr));gap:10px;margin:10px 0 16px;'>"
        f"<div><b>{len(columns)}</b><br><span>Columns</span></div>"
        f"<div><b>{required_count}</b><br><span>Required</span></div>"
        f"<div><b>{len(active)}</b><br><span>Active guardrails</span></div>"
        f"<div><b>{len(blocking)}</b><br><span>Blocking rules</span></div></div>"
        "<p><b>Load strategy:</b> "
        f"{html.escape(str(table.get('processing', {}).get('load_strategy') or 'Not configured').upper())}"
        " &nbsp; <b>Status:</b> "
        f"{html.escape(str(contract.get('status') or '').upper())}</p>"
        + _scheduled_refresh_html(table.get("scheduled_refresh", {}))
        + f"<p><b>Freshness:</b> {len(freshness)} configured &nbsp; "
        f"<b>Source drift:</b> {len(source_drift)} configured &nbsp; "
        f"<b>Column rules:</b> {len(column_guardrails)} &nbsp; "
        f"<b>Advanced rules:</b> {len(advanced)}</p>"
    )
    details = (
        "<details><summary><b>Column definitions and rules</b> · "
        f"{len(columns)} columns, {len(column_guardrails)} column rules</summary>"
        "<table><thead><tr><th>Column</th><th>Datatype</th><th>Required</th><th>Description</th>"
        f"</tr></thead><tbody>{column_rows}</tbody></table>"
        f"<h4>Column guardrails</h4>{rule_list(column_guardrails)}</details>"
        "<details><summary><b>Table guardrails</b> · "
        f"{len(freshness) + len(source_drift)} configured</summary>"
        f"<h4>Freshness</h4>{rule_list(freshness)}"
        f"<h4>Source Drift</h4>{rule_list(source_drift)}</details>"
        "<details><summary><b>Advanced rules</b> · "
        f"{len(advanced)} configured</summary>{rule_list(advanced)}</details>"
    )
    return {"Review": summary + details}

def _manifest_html(payload: dict[str, Any]) -> str:
    """Render the human and exact JSON views from the same canonical dictionary."""
    sections = _manifest_sections(payload)
    exact_json = html.escape(_expose_manifest(payload))
    return "".join(sections.values()) + (
        f"<details><summary>Exact JSON manifest</summary><pre>{exact_json}</pre></details>"
    )


def _profile_html(context: dict[str, Any]) -> str:
    """Render a compact datatype-aware summary of governed profile evidence."""
    if context.get("kind") == "unavailable":
        return "<p>No profile values available.</p>"

    profile = dict(context.get("profile") or {})
    values = list(context.get("values") or [])
    if not profile:
        return "<p>No profile values available.</p>"

    def shown(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, float):
            return f"{value:,.3f}".rstrip("0").rstrip(".")
        return str(value)

    def escaped(value: Any) -> str:
        return html.escape(shown(value))

    row_count = profile.get("row_count")
    distinct_count = profile.get("distinct_count")
    distinct_percent = profile.get("distinct_percent")
    null_percent = profile.get("null_percent")
    data_type = str(profile.get("data_type") or "").lower()
    numeric = any(
        marker in data_type
        for marker in ("byte", "short", "int", "long", "float", "double", "decimal")
    )
    temporal = "date" in data_type or "timestamp" in data_type
    boolean = "bool" in data_type

    facts = []
    if row_count is not None:
        facts.append(f"{escaped(row_count)} rows")
    if distinct_count is not None:
        distinct = f"{escaped(distinct_count)} distinct"
        if distinct_percent is not None:
            distinct += f" ({escaped(distinct_percent)}%)"
        facts.append(distinct)
    if null_percent is not None:
        facts.append(f"{escaped(null_percent)}% missing")

    lines = []
    if facts:
        lines.append(" · ".join(facts))

    if temporal:
        if profile.get("min_value") is not None or profile.get("max_value") is not None:
            lines.append(
                f"Observed: {escaped(profile.get('min_value'))} to "
                f"{escaped(profile.get('max_value'))}"
            )
    elif numeric:
        if profile.get("min_value") is not None or profile.get("max_value") is not None:
            lines.append(
                f"Range: {escaped(profile.get('min_value'))} to "
                f"{escaped(profile.get('max_value'))}"
            )
        distribution = []
        if profile.get("median_value") is not None:
            distribution.append(f"Median {escaped(profile.get('median_value'))}")
        if (
            profile.get("percentile_25_value") is not None
            and profile.get("percentile_75_value") is not None
        ):
            distribution.append(
                "Middle 50% "
                f"{escaped(profile.get('percentile_25_value'))} to "
                f"{escaped(profile.get('percentile_75_value'))}"
            )
        if profile.get("mean_value") is not None:
            distribution.append(f"Mean {escaped(profile.get('mean_value'))}")
        if profile.get("stddev_value") is not None:
            distribution.append(f"Std dev {escaped(profile.get('stddev_value'))}")
        if distribution:
            lines.append(" · ".join(distribution))

    if values:
        common = []
        for item in values[:3]:
            label = escaped(item.get("value"))
            count = item.get("count")
            percent = item.get("percent")
            detail = []
            if count is not None:
                detail.append(escaped(count))
            if percent is not None:
                detail.append(f"{escaped(percent)}%")
            common.append(f"{label} ({', '.join(detail)})" if detail else label)
        prefix = "Values" if boolean else "Common values"
        lines.append(f"{prefix}: " + ", ".join(common))
    elif (
        distinct_percent is not None
        and float(distinct_percent) >= 80.0
        and not temporal
    ):
        lines.append("Values are highly unique, so common value profiling was skipped.")

    return "<p>" + "<br>".join(lines) + "</p>"

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
    Save overwrites the complete canonical JSON for the selected draft version, then reloads
    that exact version. A new draft is seeded from the previous frozen version when one exists.
    Processing prefers the current Engineering Catalogue scan, otherwise the previous contract,
    then defaults to overwrite. Catalogue-resolved processing is read-only; inherited, defaulted,
    or manually saved processing remains editable until the draft is frozen.
    Profile context remains read-only and is never added
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
        "environment_name": env, "table_id": None, "contract_version": None,
        "pending_table_id": table_id, "pending_contract_version": contract_version,
        "contracts": catalogue["contracts"], "tables": table_rows, "current": None,
        "manifest": None, "profile_context": None, "message": "", "_controls": {},
        "_column_drafts": {}, "_profile_cache": {},
        "_ai_suggestions": {}, "_ai_errors": {}, "_ai_mode": {},
        "_pending_enrichment": {}, "_pending_guardrails": {}, "dirty": False,
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
    top_nav = widgets.ToggleButtons(
        options=_TABS,
        value="Table",
        layout=widgets.Layout(width="720px"),
    )
    left = widgets.VBox(
        layout=widgets.Layout(
            width="100%", min_width="0", max_width="100%",
            border="1px solid #e1e6eb", padding="16px", gap="8px",
            align_items="stretch",
        )
    )
    right = widgets.VBox(
        layout=widgets.Layout(
            width="100%", min_width="0", max_width="100%",
            border="1px solid #e1e6eb", padding="20px 24px", gap="10px",
            align_items="stretch",
        )
    )
    workspace = widgets.GridBox(
        [left, right],
        layout=widgets.Layout(
            width="100%", min_width="0", max_width="100%",
            grid_template_columns="minmax(250px, 27fr) minmax(0, 73fr)",
            grid_gap="12px", align_items="flex-start", overflow="visible",
        ),
    )
    view_content: dict[str, tuple[tuple[Any, ...], tuple[Any, ...]]] = {}

    def apply_view(*_args: Any) -> None:
        left_children, right_children = view_content.get(str(top_nav.value), ((), ()))
        left.children = tuple(left_children)
        right.children = tuple(right_children)
        if str(top_nav.value) == "Columns":
            load_selected_profile = state.get("_load_selected_profile")
            if callable(load_selected_profile):
                load_selected_profile()
        elif str(top_nav.value) == "Manifest & Freeze":
            refresh_review = state.get("_refresh_review")
            if callable(refresh_review):
                refresh_review()

    top_nav.observe(apply_view, names="value")

    def set_status(message: str, *, error: bool = False, warning: bool = False) -> None:
        state["message"] = message
        colour = "#a4262c" if error else "#8a6d1d" if warning else "#107c10"
        status.value = f'<div style="color:{colour};font-weight:600;">{html.escape(message)}</div>'

    def refresh_manifest() -> dict[str, Any] | None:
        current = state.get("current")
        if not current:
            return None
        if str(current["contract"].get("status") or "").lower() == "draft":
            payload, warnings = contracts.assemble_contract_payload(
                draft=current["contract"],
                tables={
                    "METADATA_DATA_CATALOGUE": current.get("catalogue_rows", []),
                    contracts.ENRICHMENT_TABLE: current.get("enrichment", []),
                    contracts.GUARDRAIL_TABLE: current.get("guardrails", []),
                },
                environment_name=env,
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
        state["_saved_payload"] = json.loads(
            str(state["current"]["contract"].get("contract_payload_json") or "{}")
        )
        scope = (str(chosen["contract_id"]), state["contract_version"])
        state["dirty"] = bool(
            state["_pending_enrichment"].get(scope)
            or state["_pending_guardrails"].get(scope)
            or state["_column_drafts"].get(scope)
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

    def stage_enrichment(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Stage Enrichment in widget session state without writing Metadata."""
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be edited.")
        scope = (str(current["contract_id"]), int(current["contract_version"]))
        pending: dict[str, dict[str, Any]] = state["_pending_enrichment"].setdefault(scope, {})
        current_rows = list(current.get("enrichment", []))
        for record in records:
            key = str(record.get("enrichment_id") or "")
            pending[key] = dict(record)
            current_rows = [
                row for row in current_rows
                if str(row.get("enrichment_id") or "") != key
            ]
            current_rows.append(dict(record))
        current["enrichment"] = current_rows
        state["dirty"] = True
        refresh_manifest()
        return records

    def stage_guardrails(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Stage Guardrails in widget session state without writing Metadata."""
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be edited.")
        scope = (str(current["contract_id"]), int(current["contract_version"]))
        pending: dict[str, dict[str, Any]] = state["_pending_guardrails"].setdefault(scope, {})
        current_rows = list(current.get("guardrails", []))
        for record in records:
            key = str(record.get("guardrail_rule_id") or "")
            pending[key] = dict(record)
            current_rows = [
                row for row in current_rows
                if str(row.get("guardrail_rule_id") or "") != key
            ]
            current_rows.append(dict(record))
        current["guardrails"] = current_rows
        state["dirty"] = True
        refresh_manifest()
        return records

    def stage_processing(processing: dict[str, Any]) -> dict[str, Any]:
        """Stage processing inside the mutable draft JSON."""
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can edit processing.")
        normalized = contracts.validated_processing(dict(processing))
        payload = json.loads(
            str(current["contract"].get("contract_payload_json") or "{}")
        )
        table_payload = payload.setdefault("table", {})
        source = str(table_payload.get("processing_source") or "default")
        if source == "catalogue" and normalized != contracts.contract_processing(current["contract"]):
            raise ValueError("Catalogue-resolved processing is read-only in this Data Contract.")
        if normalized != contracts.contract_processing(current["contract"]):
            source = "manual"
        table_payload["processing"] = normalized
        table_payload["processing_source"] = source
        current["contract"]["contract_payload_json"] = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        )
        state["dirty"] = True
        refresh_manifest()
        return normalized

    def save_data_contract_session() -> None:
        """Overwrite the selected draft JSON once, then reload canonical state once."""
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be saved.")
        scope = (str(current["contract_id"]), int(current["contract_version"]))
        payload = refresh_manifest()
        if payload is None:
            raise ValueError("Data Contract draft has no payload to save.")
        saved = contracts.save_contract_draft(
            draft=current["contract"],
            payload=payload,
            config=config,
            env=env,
            spark_session=spark,
            context=resolved,
        )
        current["contract"] = saved
        state["_pending_enrichment"].pop(scope, None)
        state["_pending_guardrails"].pop(scope, None)
        state["_column_drafts"].pop(scope, None)
        state["dirty"] = False
        select(str(state["table_id"]), int(state["contract_version"]))
        render()
        set_status("Data Contract draft saved.")

    def discard_data_contract_session() -> None:
        """Discard staged changes for the selected contract and reload canonical state."""
        current = state.get("current")
        if not current:
            return
        scope = (str(current["contract_id"]), int(current["contract_version"]))
        state["_pending_enrichment"].pop(scope, None)
        state["_pending_guardrails"].pop(scope, None)
        state["_column_drafts"].pop(scope, None)
        state["dirty"] = False
        select(str(state["table_id"]), int(state["contract_version"]))
        render()
        set_status("Unsaved Data Contract changes discarded.")

    def load_profile_context(column_id: str) -> dict[str, Any]:
        """Load one column profile once per governed table and reuse it within the widget."""
        selected_table = str(state.get("table_id") or "").strip()
        selected_column = str(column_id or "").strip()
        if not selected_table or not selected_column:
            raise ValueError("Select a governed table and column before loading profile context.")
        cache_key = (selected_table, selected_column)
        profile_cache: dict[tuple[str, str], dict[str, Any]] = state["_profile_cache"]
        if cache_key not in profile_cache:
            profile_cache[cache_key] = contracts.get_column_profile_context(
                config=config, env=env, spark_session=spark,
                table_id=selected_table, column_id=selected_column,
            )
        profile = profile_cache[cache_key]
        state["profile_context"] = profile
        return profile

    def freeze() -> dict[str, Any]:
        current = state.get("current")
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be frozen.")
        if state.get("dirty"):
            raise ValueError("Save the Data Contract before freezing this version.")
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
        freeze=freeze, activate=activate, stage_enrichment=stage_enrichment,
        stage_guardrails=stage_guardrails, save_data_contract=save_data_contract_session,
        discard_data_contract=discard_data_contract_session,
        load_profile_context=load_profile_context,
    )
    configured_stores = dict(getattr(getattr(config, "path_config", None), "paths", {}).get(env, {}))
    store_options = [
        (
            f"{name} · {str(getattr(store, 'kind', '') or '').title()}" if getattr(store, "kind", None) else str(name),
            str(name),
        )
        for name, store in configured_stores.items()
    ]
    store_control = widgets.Dropdown(
        options=store_options, **shared.widget_common(widgets, "Fabric store"),
    )
    schema_control = widgets.Dropdown(
        options=[], **shared.widget_common(widgets, "Schema"),
    )
    table_control = widgets.Dropdown(
        options=[("Select governed table", "")],
        **shared.widget_common(widgets, "Table"),
    )
    contract_control = widgets.Dropdown(**shared.widget_common(widgets, "Contract"))
    selector = shared.form_grid(widgets, [
        store_control, schema_control, table_control, contract_control,
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
        view_content.clear()
        state["_controls"].update({
            "table": table_control, "contract": contract_control,
            "top_nav": top_nav, "workspace": workspace, "left_pane": left,
            "right_pane": right, "status": status,
        })
        if not current:
            prompt = widgets.HTML("<p>Select a governed table and contract.</p>")
            left.children = (prompt,)
            right.children = ()
            return
        row = current["contract"]
        editable = str(row.get("status") or "").lower() == "draft"
        enrichments, guardrails = current_rows()

        def session_guardrails() -> list[dict[str, Any]]:
            return _latest(list(current.get("guardrails", [])), "guardrail_rule_id")

        columns = sorted(
            list(current.get("available_columns", [])),
            key=lambda column: (
                str(column.get("column_name") or "").startswith("_"),
                str(column.get("column_name") or "").casefold(),
            ),
        )
        table = next((item for item in current.get("catalogue_rows", []) if not item.get("column_id")), {})
        if not table:
            table = (state.get("manifest") or {}).get("table", {})
        suggestion_scope = (str(current["contract_id"]), int(current["contract_version"]))
        ai_state = state["_ai_suggestions"].setdefault(
            suggestion_scope, {"table": {}, "columns": {}}
        )
        ai_errors = state["_ai_errors"].setdefault(suggestion_scope, {})
        ai_mode = state["_ai_mode"].get(suggestion_scope)
        column_names = [str(column.get("column_name") or "") for column in columns]
        field_layout = widgets.Layout(width="100%", max_width="560px", min_width="0")
        compact_field_layout = widgets.Layout(width="360px", max_width="100%", min_width="0")
        selector_layout = widgets.Layout(width="100%", max_width="560px", min_width="0", height="150px")
        checkbox_row_layout = widgets.Layout(gap="20px", align_items="center", flex_flow="row wrap")

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
        accept_table_description = widgets.Button(description="Accept", disabled=not editable)
        rerun_table_description = widgets.Button(description="Re-run", disabled=not editable)
        table_save = widgets.Button(description="Apply Table Changes", button_style="primary", disabled=not editable)

        processing = contracts.contract_processing(row)
        processing_source = contracts.contract_processing_source(row)
        processing_locked = processing_source == "catalogue"
        load_strategy_control = widgets.Dropdown(
            options=("overwrite", "append", "scd1", "scd2"),
            value=str(processing.get("load_strategy") or "overwrite"),
            disabled=not editable or processing_locked,
            **shared.widget_common(widgets, "Load strategy"),
        )
        load_strategy_control.layout = compact_field_layout
        processing_source_labels = {
            "catalogue": "Resolved from Engineering Catalogue · read-only",
            "previous_contract": "Inherited from the previous Data Contract version",
            "default": "No scan or prior contract value found · defaulted to overwrite",
            "manual": "Saved on this Data Contract draft",
        }
        processing_source_hint = widgets.HTML(
            "<span style='color:#666;font-size:12px;'>"
            + html.escape(processing_source_labels.get(processing_source, "Saved on this Data Contract"))
            + "</span>"
        )
        partition_column_control = widgets.Dropdown(
            options=["", *column_names],
            value=str(processing.get("partition_column") or ""),
            disabled=not editable or processing_locked,
            **shared.widget_common(widgets, "Partition column"),
        )
        watermark_column_control = widgets.Dropdown(
            options=["", *column_names],
            value=str(processing.get("watermark_column") or ""),
            disabled=not editable or processing_locked,
            **shared.widget_common(widgets, "Watermark column"),
        )
        key_columns_control = widgets.SelectMultiple(
            options=column_names,
            value=tuple(value for value in processing.get("key_columns", []) if value in column_names),
            disabled=not editable or processing_locked,
            **shared.widget_common(widgets, "Key columns"),
        )
        effective_column_control = widgets.Dropdown(
            options=["", *column_names],
            value=str(processing.get("effective_column") or ""),
            disabled=not editable or processing_locked,
            **shared.widget_common(widgets, "Effective column"),
        )
        tracked_columns_control = widgets.SelectMultiple(
            options=column_names,
            value=tuple(value for value in processing.get("tracked_columns", []) if value in column_names),
            disabled=not editable or processing_locked,
            **shared.widget_common(widgets, "Tracked columns"),
        )
        processing_parameter_controls = (
            partition_column_control, watermark_column_control, key_columns_control,
            effective_column_control, tracked_columns_control,
        )

        def update_processing_controls(_change: dict[str, Any] | None = None) -> None:
            strategy = str(load_strategy_control.value or "overwrite")
            partition_column_control.layout.display = "" if strategy == "append" else "none"
            watermark_column_control.layout.display = "" if strategy in {"append", "scd1", "scd2"} else "none"
            key_columns_control.layout.display = "" if strategy in {"scd1", "scd2"} else "none"
            effective_column_control.layout.display = "" if strategy == "scd2" else "none"
            tracked_columns_control.layout.display = "" if strategy == "scd2" else "none"

        def build_processing() -> dict[str, Any]:
            strategy = str(load_strategy_control.value or "").strip()
            value: dict[str, Any] = {"load_strategy": strategy}
            if strategy in {"append", "scd1", "scd2"}:
                watermark = str(watermark_column_control.value or "").strip()
                if watermark:
                    value["watermark_column"] = watermark
            if strategy == "append":
                partition = str(partition_column_control.value or "").strip()
                if partition:
                    value["partition_column"] = partition
            if strategy in {"scd1", "scd2"}:
                value["key_columns"] = [str(item) for item in key_columns_control.value]
            if strategy == "scd2":
                value["effective_column"] = str(effective_column_control.value or "").strip()
                if tracked_columns_control.value:
                    value["tracked_columns"] = [str(item) for item in tracked_columns_control.value]
            return contracts.validated_processing(value)

        load_strategy_control.observe(update_processing_controls, names="value")
        update_processing_controls()

        def render_table_ai() -> None:
            if not ai_enrichment.get("enabled"):
                table_description_ai.value = "<p><b>AI suggestion</b><br>Disabled in 00_env_config.</p>"
            elif not editable:
                table_description_ai.value = "<p><b>AI suggestion</b><br>Not run for review-only versions.</p>"
            elif ai_mode != "with_ai":
                message = (
                    "Skipped for this contract session."
                    if ai_mode == "without_ai"
                    else "Choose Run with AI suggestions above."
                )
                table_description_ai.value = f"<p><b>AI suggestion</b><br>{message}</p>"
            else:
                table_description_ai.value = _suggestion_html(
                    "Description", ai_state["table"].get("description")
                )
            available = (
                editable and bool(ai_enrichment.get("enabled")) and ai_mode == "with_ai"
            )
            accept_table_description.disabled = not (
                available and ai_state["table"].get("description")
                and not ai_state["table"]["description"].get("error")
            )
            rerun_table_description.disabled = not available

        def run_table_ai(*, force: bool = False) -> None:
            if (
                not editable
                or not ai_enrichment.get("enabled")
                or ai_mode != "with_ai"
            ):
                render_table_ai()
                return
            if not force and ai_state["table"].get("description"):
                render_table_ai()
                return
            try:
                if state.get("_opening_with_ai"):
                    set_open_progress("Generating table description…", 50)
                result = suggest_enrichment(
                    build_ai_enrichment_context(
                        table,
                        metadata_level="table",
                        existing_description=str(table_description.value or ""),
                    ),
                    description_prompt=str(ai_enrichment.get("description_prompt") or ""),
                )
                previous_value = str(ai_state["table"].get("description", {}).get("value") or "")
                new_value = str(result["Description"])
                ai_state["table"]["description"] = {"value": new_value, "stale": False}
                if previous_value and new_value != previous_value:
                    mark_all_sensitive_stale()
                    invalidate_dq_suggestions("Table Description suggestion changed.")
                ai_errors.pop("table_enrichment", None)
            except (TypeError, ValueError, RuntimeError) as exc:
                message = str(exc)
                ai_state["table"]["description"] = {"error": message, "stale": False}
                ai_errors["table_enrichment"] = message
                set_status(f"Table AI suggestions unavailable: {message}", warning=True)
            render_table_ai()

        accept_table_description.on_click(
            lambda _button: setattr(
                table_description, "value",
                str(ai_state["table"].get("description", {}).get("value") or ""),
            )
        )
        rerun_table_description.on_click(lambda _button: run_table_ai(force=True))

        table_rules: dict[str, Any] = {}
        for kind, title in (("freshness", "Freshness"), ("source_drift", "Source Drift")):
            existing = next((r for r in guardrails if str(r.get("guardrail_type") or "").lower() == kind), {})
            existing_parameters = _parameters(existing)
            enabled = widgets.Checkbox(value=bool(existing and existing.get("is_active", True)), description="Enabled", disabled=not editable)
            block = widgets.Checkbox(value=str(existing.get("action") or "Warn") == "Block", description="Block on failure", disabled=not editable)
            parameter_controls: list[Any] = []
            if kind == "freshness":
                freshness_column = widgets.Dropdown(
                    options=column_names,
                    value=str(existing_parameters.get("freshness_column") or "") or None,
                    disabled=not editable,
                    **shared.widget_common(widgets, "Freshness column"),
                )
                freshness_column.layout = field_layout
                maximum_age = widgets.Text(
                    value=str(existing_parameters.get("maximum_age") or ""), disabled=not editable,
                    **shared.widget_common(widgets, "Maximum age"),
                )
                maximum_age.layout = field_layout
                maximum_age_unit = widgets.Dropdown(
                    options=("minutes", "hours", "days"),
                    value=str(existing_parameters.get("maximum_age_unit") or "days"), disabled=not editable,
                    **shared.widget_common(widgets, "Age unit"),
                )
                maximum_age_unit.layout = field_layout
                parameter_controls = [freshness_column, maximum_age, maximum_age_unit]
            else:
                partition_column = widgets.Dropdown(
                    options=column_names,
                    value=str(existing_parameters.get("partition_column") or "") or None,
                    disabled=not editable,
                    **shared.widget_common(widgets, "Partition column"),
                )
                partition_column.layout = field_layout
                change_column = widgets.Dropdown(
                    options=column_names,
                    value=str(existing_parameters.get("change_column") or "") or None,
                    disabled=not editable,
                    **shared.widget_common(widgets, "Change column"),
                )
                change_column.layout = field_layout
                parameter_controls = [partition_column, change_column]
            save = widgets.Button(description=f"Apply {title}", disabled=not editable)

            def build_table_rule_record(
                *, rule_kind: str = kind,
                enabled_control: Any = enabled, block_control: Any = block,
                controls: list[Any] = parameter_controls, rule_title: str = title,
            ) -> dict[str, Any] | None:
                old = next((
                    rule for rule in session_guardrails()
                    if str(rule.get("guardrail_type") or "").lower() == rule_kind
                    and not str(rule.get("column_id") or "")
                ), {})
                if not enabled_control.value and not old:
                    return None
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
                if enabled_control.value and any(value in {"", None} for value in parameters.values()):
                    raise ValueError(f"{rule_title} requires all governed configuration fields.")
                return guardrail_record(
                    rule_kind, rule_kind, parameters, existing=old,
                    action="Block" if block_control.value else "Warn", active=enabled_control.value,
                )

            def save_table_rule(
                _button: Any, builder: Any = build_table_rule_record, rule_title: str = title,
            ) -> None:
                try:
                    record = builder()
                    if record is not None:
                        stage_guardrails([record])
                        set_status(f"{rule_title} changes staged locally.")
                except (TypeError, ValueError, RuntimeError) as exc:
                    set_status(str(exc), error=True)

            save.on_click(save_table_rule)
            table_rules[kind] = {
                "enabled": enabled, "parameters": parameter_controls,
                "block": block, "save": save, "build_record": build_table_rule_record,
            }
        def save_table(_button: Any) -> None:
            try:
                enrichment_records = [
                    enrichment_record("table", "Description", table_description.value),
                    enrichment_record("table", "Classification", table_classification.value),
                ]
                guardrail_records = [
                    record for record in (
                        table_rules["freshness"]["build_record"](),
                        table_rules["source_drift"]["build_record"](),
                    )
                    if record is not None
                ]
                stage_processing(build_processing())
                stage_enrichment(enrichment_records)
                if guardrail_records:
                    stage_guardrails(guardrail_records)
                set_status("Table changes staged locally. Save the Data Contract from Review to persist.")
            except (TypeError, ValueError, RuntimeError) as exc:
                set_status(str(exc), error=True)

        table_save.on_click(save_table)

        active_guardrails = [rule for rule in guardrails if rule.get("is_active", True)]
        guardrail_status = {
            "Schema": any(
                str(rule.get("guardrail_type") or "").lower() == "schema"
                for rule in active_guardrails
            ),
            "Freshness": bool(table_rules["freshness"]["enabled"].value),
            "Sensitive Data": any(
                str(rule.get("guardrail_type") or "").lower() == "sensitive_data"
                for rule in active_guardrails
            ),
            "Source Drift": bool(table_rules["source_drift"]["enabled"].value),
            "Data Quality": any(
                str(rule.get("guardrail_type") or "").lower() in {"data_quality", "dq"}
                for rule in active_guardrails
            ),
        }
        guardrail_status_html = "".join(
            "<div style='display:flex;justify-content:space-between;gap:12px;padding:3px 0'>"
            f"<span style='color:#666'>{html.escape(name)}</span>"
            f"<span style='font-size:12px'>{'Enabled' if enabled else 'Disabled'}</span></div>"
            for name, enabled in guardrail_status.items()
        )
        schedule_status = str(scheduled_refresh.get("status") or "unavailable")
        if schedule_status == "configured" and scheduled_refresh.get("schedules"):
            first_schedule = scheduled_refresh["schedules"][0]
            refresh_frequency = str(first_schedule.get("frequency") or "Scheduled").replace("_", " ").title()
            schedule_times = ", ".join(str(value) for value in first_schedule.get("times") or [])
            if schedule_times:
                refresh_frequency = f"{refresh_frequency} · {schedule_times}"
        elif schedule_status == "not_configured":
            refresh_frequency = "Not configured"
        else:
            refresh_frequency = "Unavailable"

        identity = widgets.HTML(
            "<p><b>{}</b><br>Contract v{} · {}<br>Environment: {}<br>Store: {} · {}</p>".format(
                html.escape(f"{table.get('schema_name') or ''}.{table.get('table_name') or state['table_id']}"),
                html.escape(str(row.get("contract_version") or "")), html.escape(str(row.get("status") or "").upper()),
                html.escape(env), html.escape(str(table.get("store_type") or "Metadata")),
                html.escape(str(table.get("layer") or "")),
            )
        )
        processing = contracts.contract_processing(row)
        load_strategy = str(processing.get("load_strategy") or "overwrite").upper()
        pipeline_refresh = widgets.HTML(
            "<div><b>Load strategy</b><br>"
            f"{html.escape(load_strategy)}</div><br>"
            + _scheduled_refresh_html(scheduled_refresh)
        )
        table_summary = widgets.HTML(
                "<div style='background:#e7f5ef;border-left:4px solid #107c41;"
                "border-radius:4px;padding:10px 11px;margin-bottom:12px;'>"
                "<div style='color:#0b5d35;font-size:10px;font-weight:800;"
                "text-transform:uppercase;letter-spacing:.07em;'>Governed table</div>"
                + identity.value
                + "</div>"
                + "<div style='color:#667085;font-size:10px;font-weight:800;"
                "text-transform:uppercase;letter-spacing:.07em;'>Contract</div>"
                + "<div style='color:#172b4d;font-weight:600;margin-top:3px;'>"
                + f"v{row['contract_version']} · {html.escape(str(row.get('status') or '').upper())}</div>"
                + "<div style='border-top:1px solid #e6eaef;margin:14px 0;'></div>"
                + "<div style='color:#667085;font-size:10px;font-weight:800;"
                "text-transform:uppercase;letter-spacing:.07em;'>Loading Strategy</div>"
                + f"<div style='color:#172b4d;font-weight:600;margin-top:3px;'>{html.escape(load_strategy)}</div>"
                + "<div style='color:#667085;font-size:10px;font-weight:800;"
                "text-transform:uppercase;letter-spacing:.07em;margin-top:13px;'>Refresh Frequency</div>"
                + f"<div style='color:#172b4d;font-weight:600;margin-top:3px;'>{html.escape(refresh_frequency)}</div>"
                + "<div style='color:#667085;font-size:10px;font-weight:800;"
                "text-transform:uppercase;letter-spacing:.07em;margin-top:13px;'>Classification</div>"
                + "<div style='color:#172b4d;font-weight:600;margin-top:3px;'>"
                + f"{html.escape(str(table_classification.value or 'Not classified'))}</div>"
                + "<div style='border-top:1px solid #e6eaef;margin:14px 0;'></div>"
                + "<div style='color:#667085;font-size:10px;font-weight:800;"
                "text-transform:uppercase;letter-spacing:.07em;'>Guardrails</div>"
                + "<div style='margin-top:6px;'>" + guardrail_status_html + "</div>"
        )
        table_left = (table_summary, change_table_button)

        def render_table_summary(_change: dict[str, Any] | None = None) -> None:
            active = [rule for rule in session_guardrails() if rule.get("is_active", True)]
            selected_sensitive = bool(
                state.get("_working_sensitive_enabled", False)
            )
            selected_dq = bool(state.get("_working_dq_enabled", False))
            statuses = {
                "Schema": bool(required_columns),
                "Freshness": bool(table_rules["freshness"]["enabled"].value),
                "Sensitive Data": selected_sensitive or any(
                    str(rule.get("guardrail_type") or "").lower() == "sensitive_data"
                    for rule in active
                ),
                "Source Drift": bool(table_rules["source_drift"]["enabled"].value),
                "Data Quality": selected_dq or any(
                    str(rule.get("guardrail_type") or "").lower() in {"data_quality", "dq"}
                    for rule in active
                ),
            }
            guardrail_html = "".join(
                "<div style='display:flex;justify-content:space-between;gap:12px;padding:3px 0'>"
                f"<span style='color:#666'>{html.escape(name)}</span>"
                f"<span style='font-size:12px'>{'Enabled' if enabled else 'Disabled'}</span></div>"
                for name, enabled in statuses.items()
            )
            table_summary.value = (
                "<div style='color:#0f6cbd;font-size:11px;font-weight:800;"
                "text-transform:uppercase;letter-spacing:.07em;'>Table</div>"
                f"<div style='color:#172b4d;font-size:18px;font-weight:700;margin-top:6px;'>{html.escape(str(table.get('table_name') or state.get('table_id') or ''))}</div>"
                f"<div style='color:#667085;font-size:12px;margin-top:2px;'>{html.escape(str(table.get('schema_name') or ''))}</div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Loading Strategy</div>"
                f"<div style='font-weight:600;'>{html.escape(str(load_strategy_control.value or 'Not configured').upper())}</div></div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Refresh Frequency</div>"
                f"<div style='font-weight:600;'>{html.escape(refresh_frequency)}</div></div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Classification</div>"
                f"<div style='font-weight:600;'>{html.escape(str(table_classification.value or 'Not classified'))}</div></div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Guardrails</div>"
                + guardrail_html + "</div>"
            )

        table_classification.observe(render_table_summary, names="value")
        for rule_controls in table_rules.values():
            rule_controls["enabled"].observe(render_table_summary, names="value")
        processing_hint_row = widgets.HBox(
            [
                widgets.HTML("", layout=widgets.Layout(width="150px", min_width="150px")),
                processing_source_hint,
            ],
            layout=widgets.Layout(width="100%", gap="12px", align_items="flex-start"),
        )
        table_ai_row = widgets.HBox(
            [
                widgets.HTML("", layout=widgets.Layout(width="150px", min_width="150px")),
                widgets.VBox(
                    [
                        table_description_ai,
                        shared.action_row(
                            widgets, [accept_table_description, rerun_table_description]
                        ),
                    ],
                    layout=widgets.Layout(width="560px", max_width="100%", gap="6px"),
                ),
            ],
            layout=widgets.Layout(width="100%", gap="12px", align_items="flex-start"),
        )
        table_right = (
            shared.form_section(
                widgets,
                title="Table metadata",
                children=[
                    table_classification,
                    table_description,
                    table_ai_row,
                ],
            ),
            shared.form_section(
                widgets,
                title="Processing",
                children=[
                    load_strategy_control,
                    processing_hint_row,
                    *processing_parameter_controls,
                ],
            ),
            shared.form_section(
                widgets,
                title="Freshness",
                children=[
                    widgets.HTML(
                        "<div style='color:#667085;font-size:12px;line-height:1.5;'>"
                        "Expected source-data arrival SLA. This is independent of when Fabric "
                        "schedules the notebook to run.</div>"
                    ),
                    widgets.HBox(
                        [table_rules["freshness"]["enabled"], table_rules["freshness"]["block"]],
                        layout=checkbox_row_layout,
                    ),
                    *table_rules["freshness"]["parameters"],
                ],
            ),
            shared.form_section(
                widgets,
                title="Source Drift",
                children=[
                    widgets.HTML(
                        "<div style='color:#667085;font-size:12px;line-height:1.5;'>"
                        "Detect changes in source partitions and the selected change column "
                        "before governed publication.</div>"
                    ),
                    widgets.HBox(
                        [table_rules["source_drift"]["enabled"], table_rules["source_drift"]["block"]],
                        layout=checkbox_row_layout,
                    ),
                    *table_rules["source_drift"]["parameters"],
                ],
            ),
            shared.action_row(widgets, [table_save]),
        )
        view_content["Table"] = (table_left, table_right)


        # Columns: one editor, hydrated on selection, with profile evidence isolated from payload.
        required_rule = next(
            (r for r in guardrails if str(r.get("guardrail_type") or "").lower() == "schema"), {}
        )
        required_columns = set(_parameters(required_rule).get("required_columns", []))
        render_table_summary()
        saved_payload = json.loads(
            str(current["contract"].get("contract_payload_json") or "{}")
        )
        contracted_columns = {
            str(item.get("column_id") or ""): dict(item)
            for item in (saved_payload.get("table", {}).get("columns", []) or [])
            if item.get("column_id")
        }
        observed_types = {
            str(item.get("column_id") or ""): str(item.get("data_type") or "")
            for item in columns
        }
        contracted_types = {
            cid: str(contracted_columns.get(cid, {}).get("data_type") or observed_type)
            for cid, observed_type in observed_types.items()
        }
        column_options: list[tuple[str, str]] = []
        column_option_style = widgets.HTML()
        column_search = widgets.Text(
            placeholder="Search columns",
            layout=widgets.Layout(width="100%"),
        )
        column_select = widgets.Select(
            options=(),
            rows=8,
            layout=widgets.Layout(width="100%", height="250px"),
        )
        column_select.add_class("fabricops-contract-columns")
        column_context = widgets.HTML()
        profile_context = shared.preview_region(widgets, widgets.HTML("<p>No column selected.</p>"), height="160px")
        column_description = widgets.Textarea(disabled=not editable, **shared.widget_common(widgets, "Description", textarea=True))
        column_classification = widgets.Dropdown(options=_CLASSIFICATIONS, disabled=not editable, **shared.widget_common(widgets, "Classification"))
        column_description_ai = widgets.HTML()
        accept_column_description = widgets.Button(description="Accept", disabled=not editable)
        rerun_column_description = widgets.Button(description="Re-run", disabled=not editable)
        required = widgets.Checkbox(description="Required", disabled=not editable)
        datatype_choice = widgets.Dropdown(
            options=(), disabled=not editable,
            **shared.widget_common(widgets, "Contract datatype"),
        )
        datatype_choice.layout.display = "none"
        sensitive_enabled = widgets.Checkbox(description="Enabled", disabled=not editable)
        pii_type = widgets.Dropdown(
            options=[(label, value) for value, label in PII_LABELS.items()],
            value="none", disabled=not editable, **shared.widget_common(widgets, "PII assessment"),
        )
        pii_reason = widgets.Textarea(
            disabled=not editable, **shared.widget_common(widgets, "Reason", textarea=True)
        )
        sensitive_treatment = widgets.Dropdown(options=("tokenize", "mask", "bucket", "remove"), disabled=not editable, **shared.widget_common(widgets, "Treatment"))
        sensitive_block = widgets.Checkbox(description="Block on failure", disabled=not editable)
        mask_start = widgets.Text(value="0", disabled=not editable, **shared.widget_common(widgets, "Mask: preserve start"))
        mask_end = widgets.Text(value="0", disabled=not editable, **shared.widget_common(widgets, "Mask: preserve end"))
        mask_character = widgets.Text(value="*", disabled=not editable, **shared.widget_common(widgets, "Mask character"))
        bucket_bins = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Bucket boundaries (comma-separated)"))
        bucket_labels = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Bucket labels (comma-separated)"))
        dq_type = widgets.Select(
            options=[
                ("Completeness", "completeness"),
                ("Uniqueness", "uniqueness"),
                ("Value Set", "value_set"),
                ("Range", "range"),
                ("Pattern", "pattern"),
            ],
            rows=5,
            disabled=not editable,
            layout=selector_layout,
        )
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
        dq_enabled = widgets.Checkbox(description="Enabled", disabled=not editable)
        dq_block = widgets.Checkbox(description="Block on failure", disabled=not editable)
        dq_usage = widgets.HTML()
        save_column_enrichment = widgets.Button(description="Apply enrichment", button_style="primary", disabled=not editable)
        save_column = widgets.Button(
            description="Apply Column Changes", button_style="primary", disabled=not editable,
            layout=widgets.Layout(width="130px", height="34px"),
        )
        save_required = widgets.Button(description="Apply required state", disabled=not editable)
        save_sensitive = widgets.Button(description="Apply Sensitive Data", disabled=not editable)
        sensitive_ai = widgets.HTML()
        accept_sensitive = widgets.Button(description="Accept suggestion", disabled=not editable)
        rerun_sensitive = widgets.Button(description="Re-run", disabled=not editable)
        save_dq = widgets.Button(description="Apply Data Quality rule", disabled=not editable)
        suggest_dq = widgets.Button(
            description="Suggest rules",
            disabled=(
                not editable
                or not ai_enrichment.get("enabled")
                or ai_mode != "with_ai"
            ),
        )
        dq_suggestion = widgets.Select(options=(), disabled=True, **shared.widget_common(widgets, "AI suggestions"))
        accept_dq_suggestion = widgets.Button(description="Apply selected suggestion", disabled=True)
        dq_ai = widgets.HTML()
        for control in (
            table_description, table_classification,
            column_description, column_classification, datatype_choice,
            pii_type, pii_reason, sensitive_treatment,
            mask_start, mask_end, mask_character, bucket_bins, bucket_labels,
            dq_max_missing, dq_value_mode, dq_values, dq_minimum, dq_maximum, dq_pattern,
        ):
            control.layout.width = "100%"
            control.layout.max_width = "560px"
            control.layout.min_width = "0"
        draft_scope = (str(current["contract_id"]), int(current["contract_version"]))
        unsaved_columns: dict[str, dict[str, Any]] = state["_column_drafts"].setdefault(
            draft_scope, {}
        )

        def selected_column() -> dict[str, Any]:
            return next((c for c in columns if str(c.get("column_id") or "") == str(column_select.value or "")), {})

        hydrating = {"active": False}
        hydrated_column_snapshots: dict[str, dict[str, Any]] = {}

        def column_editor_snapshot() -> dict[str, Any]:
            return {
                "description": column_description.value,
                "classification": column_classification.value,
                "required": required.value,
                "sensitive_enabled": sensitive_enabled.value,
                "pii_type": pii_type.value,
                "pii_reason": pii_reason.value,
                "sensitive_treatment": sensitive_treatment.value,
                "sensitive_block": sensitive_block.value,
                "mask_start": mask_start.value,
                "mask_end": mask_end.value,
                "mask_character": mask_character.value,
                "bucket_bins": bucket_bins.value,
                "bucket_labels": bucket_labels.value,
                "dq_type": dq_type.value,
                "dq_parameters": [control.value for control in dq_parameter_controls],
                "dq_enabled": dq_enabled.value,
                "dq_block": dq_block.value,
            }

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
            dq_enabled.value = False
            dq_block.value = False
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
            dq_enabled.value = bool(rule and rule.get("is_active", True))
            dq_block.value = str(rule.get("action") or "Warn") == "Block"

        def hydrate_column(column_id: str) -> None:
            hydrating["active"] = True
            selected = next((c for c in columns if str(c.get("column_id") or "") == column_id), {})
            observed_type = str(selected.get("data_type") or "")
            contract_type = str(contracted_types.get(column_id) or observed_type)
            mismatch = bool(contract_type and observed_type and contract_type != observed_type)
            if mismatch:
                column_context.value = (
                    f"<h4>{html.escape(str(selected.get('column_name') or ''))}</h4>"
                    "<p><span style='color:#a4262c;font-weight:700;'>Datatype drift detected</span><br>"
                    f"Contract: <b>{html.escape(contract_type)}</b> · "
                    f"Observed: <b style='color:#a4262c'>{html.escape(observed_type)}</b><br>"
                    "Choose which datatype this draft should govern before saving.</p>"
                )
                datatype_choice.options = (
                    (f"Keep contract · {contract_type}", contract_type),
                    (f"Accept observed · {observed_type}", observed_type),
                )
                datatype_choice.value = contract_type
                datatype_choice.layout.display = ""
            else:
                column_context.value = (
                    f"<h4>{html.escape(str(selected.get('column_name') or ''))}</h4>"
                    f"<p>Datatype: <b>{html.escape(contract_type or observed_type)}</b><br>"
                    f"Required: <b>{'Yes' if column_id in required_columns or selected.get('column_name') in required_columns else 'No'}</b></p>"
                )
                datatype_choice.options = ((contract_type or observed_type, contract_type or observed_type),)
                datatype_choice.value = contract_type or observed_type
                datatype_choice.layout.display = "none"
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
            sensitive_block.value = str(sensitive.get("action") or "Warn") == "Block"
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
            hydrated_column_snapshots[column_id] = column_editor_snapshot()
            pending = unsaved_columns.get(column_id)
            if pending:
                column_description.value = pending["description"]
                column_classification.value = pending["classification"]
                required.value = pending["required"]
                sensitive_enabled.value = pending["sensitive_enabled"]
                pii_type.value = pending["pii_type"]
                pii_reason.value = pending["pii_reason"]
                sensitive_treatment.value = pending["sensitive_treatment"]
                sensitive_block.value = pending["sensitive_block"]
                mask_start.value = pending["mask_start"]
                mask_end.value = pending["mask_end"]
                mask_character.value = pending["mask_character"]
                bucket_bins.value = pending["bucket_bins"]
                bucket_labels.value = pending["bucket_labels"]
                dq_type.value = pending["dq_type"]
                for control, value in zip(dq_parameter_controls, pending["dq_parameters"], strict=True):
                    control.value = value
                dq_enabled.value = pending["dq_enabled"]
                dq_block.value = pending["dq_block"]
            profile_context.value = "<p>Open the Columns tab to load profile evidence.</p>"
            hydrating["active"] = False

        def load_selected_profile() -> None:
            column_id = str(column_select.value or "")
            if not column_id:
                profile_context.value = "<p>No column selected.</p>"
                return
            try:
                profile_context.value = _profile_html(load_profile_context(column_id))
            except (ValueError, RuntimeError) as exc:
                profile_context.value = f"<p>{html.escape(str(exc))}</p>"

        state["_load_selected_profile"] = load_selected_profile

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
        def working_sensitive_changed(_change: dict[str, Any]) -> None:
            if hydrating["active"]:
                return
            state["_working_sensitive_enabled"] = bool(sensitive_enabled.value)
            render_table_summary()

        def working_dq_changed(_change: dict[str, Any]) -> None:
            if hydrating["active"]:
                return
            state["_working_dq_enabled"] = bool(dq_enabled.value)
            render_table_summary()

        sensitive_enabled.observe(working_sensitive_changed, names="value")
        dq_enabled.observe(working_dq_changed, names="value")
        update_sensitive_fields()

        def update_pii_fields(change: dict[str, Any] | None = None) -> None:
            is_pii = str(pii_type.value or "none") != "none"
            if not is_pii:
                sensitive_enabled.value = False
            sensitive_treatment.disabled = not editable or not is_pii
            sensitive_block.disabled = not editable or not is_pii
            update_sensitive_fields()

        pii_type.observe(update_pii_fields, names="value")
        update_pii_fields()

        def column_changed(change: dict[str, Any]) -> None:
            old = str(change.get("old") or "")
            if old:
                snapshot = column_editor_snapshot()
                if snapshot != hydrated_column_snapshots.get(old, snapshot):
                    unsaved_columns[old] = snapshot
                    set_status(
                        "Column edits were retained locally; use Apply Column Changes before the final save."
                    )
                else:
                    unsaved_columns.pop(old, None)
            if change.get("new"):
                selected_id = str(change["new"])
                hydrate_column(selected_id)
                if str(top_nav.value) == "Columns":
                    load_selected_profile()
                if not state.get("_opening_with_ai"):
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

        def _effective_ai_description(column_id: str) -> str:
            """Return the freshest Description context for dependent AI suggestions."""
            description, _classification = _column_editable_values(column_id)
            suggestion = ai_state["columns"].get(column_id, {}).get("description", {})
            if suggestion and not suggestion.get("error") and not suggestion.get("stale"):
                return str(suggestion.get("value") or description)
            return description

        def _effective_table_ai_description() -> str:
            """Return the freshest table Description context for dependent AI suggestions."""
            suggestion = ai_state["table"].get("description", {})
            if suggestion and not suggestion.get("error") and not suggestion.get("stale"):
                return str(suggestion.get("value") or table_description.value or "")
            return str(table_description.value or "")

        def render_column_ai(column_id: str) -> None:
            suggestions = ai_state["columns"].get(column_id, {})
            if not ai_enrichment.get("enabled"):
                disabled_message = "<p><b>AI suggestion</b><br>Disabled in 00_env_config.</p>"
                column_description_ai.value = disabled_message
                sensitive_ai.value = disabled_message
            elif not editable:
                review_message = "<p><b>AI suggestion</b><br>Not run for review-only versions.</p>"
                column_description_ai.value = review_message
                sensitive_ai.value = review_message
            elif ai_mode != "with_ai":
                message = (
                    "Skipped for this contract session."
                    if ai_mode == "without_ai"
                    else "Choose Run with AI suggestions on the Table tab."
                )
                column_description_ai.value = f"<p><b>AI suggestion</b><br>{message}</p>"
                sensitive_ai.value = f"<p><b>AI suggestion</b><br>{message}</p>"
            else:
                column_description_ai.value = _suggestion_html(
                    "Description", suggestions.get("description")
                )
                sensitive_ai.value = _suggestion_html(
                    "Sensitive Data", suggestions.get("sensitive_data")
                )
            available = (
                editable and bool(ai_enrichment.get("enabled")) and ai_mode == "with_ai"
            )
            accept_column_description.disabled = not (
                available and suggestions.get("description") and not suggestions["description"].get("error")
            )
            accept_sensitive.disabled = not (
                available and suggestions.get("sensitive_data") and not suggestions["sensitive_data"].get("error")
            )
            rerun_column_description.disabled = not available
            rerun_sensitive.disabled = not available

        def invalidate_dq_suggestions(message: str) -> None:
            """Clear DQ advice when any of its governed inputs change."""
            if state["_ai_suggestions"][suggestion_scope].pop("dq", None) is not None:
                dq_suggestion.options = ()
                dq_suggestion.disabled = True
                accept_dq_suggestion.disabled = True
                dq_ai.value = (
                    "<p><b>AI suggestions</b><br>"
                    f"{html.escape(message)} Re-run suggestions to refresh them.</p>"
                )

        def mark_sensitive_stale(column_id: str) -> None:
            """Mark one column's dependent Sensitive Data advice stale."""
            suggestion = ai_state["columns"].get(column_id, {}).get("sensitive_data")
            if suggestion:
                suggestion["stale"] = True

        def mark_all_sensitive_stale() -> None:
            """Mark all loaded column Sensitive Data suggestions stale."""
            for column_suggestions in ai_state["columns"].values():
                suggestion = column_suggestions.get("sensitive_data")
                if suggestion:
                    suggestion["stale"] = True

        def run_column_enrichment_ai(column_id: str, *, force: bool = False) -> None:
            suggestions = ai_state["columns"].setdefault(column_id, {})
            if not force and suggestions.get("description"):
                render_column_ai(column_id)
                return
            selected = next(
                (column for column in columns if str(column.get("column_id") or "") == column_id), {}
            )
            description, _ = _column_editable_values(column_id)
            try:
                if state.get("_opening_with_ai"):
                    set_open_progress("Loading first-column profile…", 65)
                profile_value = load_profile_context(column_id)
                if state.get("_opening_with_ai"):
                    set_open_progress("Generating first-column description…", 75)
                result = suggest_enrichment(
                    build_ai_enrichment_context(
                        selected,
                        metadata_level="column",
                        existing_description=description,
                        profile_rows=[dict(profile_value.get("profile") or {})],
                    ),
                    description_prompt=str(ai_enrichment.get("description_prompt") or ""),
                )
                previous_value = str(suggestions.get("description", {}).get("value") or "")
                new_value = str(result["Description"])
                suggestions["description"] = {"value": new_value, "stale": False}
                if previous_value and new_value != previous_value:
                    mark_sensitive_stale(column_id)
                    invalidate_dq_suggestions("Description suggestion changed.")
                ai_errors.pop((column_id, "enrichment"), None)
            except (TypeError, ValueError, RuntimeError) as exc:
                message = str(exc)
                suggestions["description"] = {"error": message, "stale": False}
                ai_errors[(column_id, "enrichment")] = message
                set_status(f"AI suggestions unavailable for this column: {message}", warning=True)
            render_column_ai(column_id)

        def run_sensitive_ai(
            column_id: str, *, force: bool = False, use_description_suggestion: bool = False
        ) -> None:
            suggestions = ai_state["columns"].setdefault(column_id, {})
            if not force and suggestions.get("sensitive_data"):
                render_column_ai(column_id)
                return
            selected = next(
                (column for column in columns if str(column.get("column_id") or "") == column_id), {}
            )
            description, classification = _column_editable_values(column_id)
            if use_description_suggestion:
                description = _effective_ai_description(column_id)
            try:
                if state.get("_opening_with_ai"):
                    set_open_progress("Assessing first column for sensitive data…", 88)
                profile_value = load_profile_context(column_id)
                profile = dict(profile_value.get("profile") or {})
                context_value = build_ai_sensitive_data_context({
                    "table_id": state.get("table_id"),
                    "table_name": table.get("table_name"),
                    "schema_name": table.get("schema_name"),
                    "layer": table.get("layer"),
                    "contract_id": current.get("contract_id"),
                    "contract_version": current.get("contract_version"),
                    "table_description": (
                        _effective_table_ai_description()
                        if use_description_suggestion
                        else str(table_description.value or "")
                    ),
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
            if (
                not editable
                or not ai_enrichment.get("enabled")
                or ai_mode != "with_ai"
                or not column_id
            ):
                render_column_ai(column_id)
                return
            run_column_enrichment_ai(column_id)
            run_sensitive_ai(column_id, use_description_suggestion=True)

        def accept_description_clicked(_button: Any) -> None:
            suggestion = ai_state["columns"].get(str(column_select.value or ""), {}).get("description", {})
            if not suggestion.get("error"):
                column_description.value = str(suggestion.get("value") or "")

        def accept_sensitive_clicked(_button: Any) -> None:
            suggestion = ai_state["columns"].get(str(column_select.value or ""), {}).get("sensitive_data", {})
            if not suggestion or suggestion.get("error"):
                return
            pii_type.value = str(suggestion["pii_type"])
            pii_reason.value = str(suggestion["reason"])
            sensitive_enabled.value = suggestion["pii_type"] != "none"
            sensitive_treatment.value = str(suggestion.get("treatment") or "mask")
            sensitive_block.value = str(suggestion.get("action") or "Warn") == "Block"
            parameters = suggestion.get("parameters", {})
            mask_start.value = str(parameters.get("preserve_start", 0))
            mask_end.value = str(parameters.get("preserve_end", 0))
            mask_character.value = str(parameters.get("mask_character", "*"))
            bucket_bins.value = ", ".join(map(str, parameters.get("bins", [])))
            bucket_labels.value = ", ".join(map(str, parameters.get("labels", [])))

        accept_column_description.on_click(accept_description_clicked)
        accept_sensitive.on_click(accept_sensitive_clicked)
        rerun_column_description.on_click(
            lambda _button: run_column_enrichment_ai(str(column_select.value or ""), force=True)
        )
        rerun_sensitive.on_click(
            lambda _button: run_sensitive_ai(str(column_select.value or ""), force=True)
        )

        def description_changed(change: dict[str, Any]) -> None:
            if hydrating["active"]:
                return
            column_id = str(column_select.value or "")
            suggestions = ai_state["columns"].get(column_id, {})
            description_suggestion = suggestions.get("description")
            new_value = str(change.get("new") or "")
            if (
                description_suggestion
                and not description_suggestion.get("error")
                and new_value == str(description_suggestion.get("value") or "")
            ):
                render_column_ai(column_id)
                return
            if description_suggestion:
                description_suggestion["stale"] = True
            mark_sensitive_stale(column_id)
            invalidate_dq_suggestions("Description changed.")
            render_column_ai(column_id)

        def classification_changed(_change: dict[str, Any]) -> None:
            if hydrating["active"]:
                return
            column_id = str(column_select.value or "")
            mark_sensitive_stale(column_id)
            invalidate_dq_suggestions("Classification changed.")
            render_column_ai(column_id)

        def table_description_changed(change: dict[str, Any]) -> None:
            suggestion = ai_state["table"].get("description")
            new_value = str(change.get("new") or "")
            if (
                suggestion
                and not suggestion.get("error")
                and new_value == str(suggestion.get("value") or "")
            ):
                return
            if suggestion:
                suggestion["stale"] = True
            mark_all_sensitive_stale()
            invalidate_dq_suggestions("Table Description changed.")
            render_table_ai()
            selected_id = str(column_select.value or "")
            if selected_id:
                render_column_ai(selected_id)

        def table_classification_changed(_change: dict[str, Any]) -> None:
            mark_all_sensitive_stale()
            invalidate_dq_suggestions("Table Classification changed.")
            selected_id = str(column_select.value or "")
            if selected_id:
                render_column_ai(selected_id)

        column_description.observe(description_changed, names="value")
        column_classification.observe(classification_changed, names="value")
        table_description.observe(table_description_changed, names="value")
        table_classification.observe(table_classification_changed, names="value")

        def save_column_enrichment_clicked(_button: Any) -> None:
            try:
                cid = str(column_select.value or "")
                stage_enrichment([
                    enrichment_record("column", "Description", column_description.value, cid),
                    enrichment_record("column", "Classification", column_classification.value, cid),
                ])
                set_status("Column enrichment staged locally.")
            except (ValueError, RuntimeError) as exc:
                set_status(str(exc), error=True)

        def build_required_record() -> dict[str, Any]:
            selected = selected_column()
            cid = str(selected.get("column_id") or "")
            current_rule = next((
                rule for rule in session_guardrails()
                if str(rule.get("guardrail_type") or "").lower() == "schema"
            ), required_rule)
            updated = set(_parameters(current_rule).get("required_columns", []))
            identifier = cid or str(selected.get("column_name") or "")
            (updated.add if required.value else updated.discard)(identifier)
            return guardrail_record(
                "schema", "required_columns", {"required_columns": sorted(updated)},
                existing=current_rule,
            )

        def save_required_clicked(_button: Any) -> None:
            try:
                stage_guardrails([build_required_record()])
                set_status("Required-column change staged locally.")
            except (ValueError, RuntimeError) as exc:
                set_status(str(exc), error=True)

        def build_sensitive_record() -> dict[str, Any] | None:
            cid = str(column_select.value or "")
            existing = next((
                r for r in session_guardrails()
                if str(r.get("guardrail_type") or "").lower() == "sensitive_data"
                and str(r.get("column_id") or "") == cid
            ), {})
            if (
                not existing
                and not sensitive_enabled.value
                and str(pii_type.value or "none") == "none"
            ):
                return None
            if str(pii_type.value or "none") == "none" and sensitive_enabled.value:
                raise ValueError("Enable a Sensitive Data rule only for Direct or Indirect PII.")
            parameters: dict[str, Any] = {
                "scope": "column", "treatment": sensitive_treatment.value,
            }
            if str(pii_type.value or "none") != "none":
                if not str(pii_reason.value or "").strip():
                    raise ValueError("Explain why this column is Direct or Indirect PII.")
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
                    "bins": [
                        float(value.strip()) for value in bucket_bins.value.split(",")
                        if value.strip()
                    ],
                    "labels": [
                        value.strip() for value in bucket_labels.value.split(",")
                        if value.strip()
                    ],
                })
            return guardrail_record(
                "sensitive_data", str(sensitive_treatment.value), parameters, column_id=cid,
                action="Block" if sensitive_block.value else "Warn",
                existing=existing, active=sensitive_enabled.value,
            )

        def save_sensitive_clicked(_button: Any) -> None:
            try:
                record = build_sensitive_record()
                if record is not None:
                    stage_guardrails([record])
                    set_status("Sensitive Data change staged locally.")
            except (TypeError, ValueError, RuntimeError) as exc:
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
                existing = next((r for r in session_guardrails() if str(r.get("guardrail_type") or "").lower() in {"data_quality", "dq"} and str(r.get("column_id") or "") == cid and str(r.get("rule_type") or "") == kind), {})
                stage_guardrails([guardrail_record(
                    "data_quality", kind, params, column_id=cid,
                    action="Block" if dq_block.value else "Warn",
                    existing=existing, active=dq_enabled.value,
                )])
                set_status("Data Quality rule staged locally.")
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
                    "layer": table.get("layer"), "table_description": _effective_table_ai_description(),
                    "table_classification": table_classification.value,
                    "catalogue_profile_rows": [{
                        **selected, "description": _effective_ai_description(
                            str(selected.get("column_id") or "")
                        ),
                        "classification": column_classification.value,
                        **{name: profile.get(name) for name in (
                            "row_count", "non_null_count", "null_count", "null_percent",
                            "distinct_count", "distinct_percent", "mean_value", "stddev_value",
                            "min_value", "percentile_25_value", "median_value",
                            "percentile_75_value", "max_value",
                        ) if profile.get(name) is not None},
                        "frequency_evidence": [
                            {
                                "value": item.get("value"),
                                "count": item.get("count"),
                                "percent": item.get("percent"),
                            }
                            for item in profile_value.get("values", [])[:10]
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
                ) + "</ul><p>Select and edit a rule before the final Data Contract save; suggestions are never persisted automatically.</p>"
            except (TypeError, ValueError, RuntimeError) as exc:
                state["_ai_suggestions"][suggestion_scope].pop("dq", None)
                dq_suggestion.options = ()
                dq_suggestion.disabled = True
                accept_dq_suggestion.disabled = True
                dq_ai.value = f"<p style='color:#a4262c'>{html.escape(str(exc))}</p>"

        def accept_dq_clicked(_button: Any) -> None:
            suggestions = state["_ai_suggestions"][suggestion_scope].get("dq", [])
            if dq_suggestion.value in (None, ""):
                return
            suggestion = suggestions[int(dq_suggestion.value)]
            dq_type.value = suggestion["rule_type"]
            dq_enabled.value = True
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

        def save_column_clicked(_button: Any) -> None:
            try:
                cid = str(column_select.value or "")
                enrichment_records = [
                    enrichment_record("column", "Description", column_description.value, cid),
                    enrichment_record("column", "Classification", column_classification.value, cid),
                ]
                guardrail_records = [
                    record for record in (build_required_record(), build_sensitive_record())
                    if record is not None
                ]
                stage_enrichment(enrichment_records)
                if guardrail_records:
                    stage_guardrails(guardrail_records)
                unsaved_columns.pop(cid, None)
                hydrated_column_snapshots[cid] = column_editor_snapshot()
                set_status("Column changes staged locally. Save the Data Contract from Review to persist.")
            except (TypeError, ValueError, RuntimeError) as exc:
                set_status(str(exc), error=True)

        save_column_enrichment.on_click(save_column_enrichment_clicked)
        save_required.on_click(save_required_clicked)
        save_sensitive.on_click(save_sensitive_clicked)
        save_column.on_click(save_column_clicked)
        save_dq.on_click(save_dq_clicked)
        suggest_dq.on_click(suggest_dq_clicked)
        accept_dq_suggestion.on_click(accept_dq_clicked)
        def rebuild_column_options() -> None:
            nonlocal column_options
            column_options = []
            required_indexes = []
            for index, column in enumerate(columns, start=1):
                cid = str(column.get("column_id") or "")
                name = str(column.get("column_name") or "")
                contract_type = str(contracted_types.get(cid) or column.get("data_type") or "")
                observed_type = str(observed_types.get(cid) or "")
                is_required = cid in required_columns or name in required_columns
                drift = contract_type != observed_type
                marker = " *" if is_required else ""
                drift_marker = f"  → {observed_type}" if drift else ""
                column_options.append(
                    (f"{name}    {contract_type}{drift_marker}{marker}", cid)
                )
                if is_required:
                    required_indexes.append(index)
            rules = "".join(
                f".fabricops-contract-columns option:nth-child({index}):not(:checked)"
                "{color:#0f6cbd;font-weight:600;}"
                for index in required_indexes
            )
            column_option_style.value = (
                "<style>"
                + rules
                + ".fabricops-contract-columns option:checked{"
                "color:CanvasText !important;font-weight:600;}"
                + "</style>"
            )

        def refresh_column_options(*_args: Any) -> None:
            rebuild_column_options()
            query = str(column_search.value or "").strip().casefold()
            current_value = str(column_select.value or "")
            filtered = [
                option for option in column_options
                if not query or query in str(option[0]).casefold()
            ]
            column_select.options = filtered
            values = [str(value) for _label, value in filtered]
            if current_value in values:
                column_select.value = current_value
            elif values:
                column_select.value = values[0]
            else:
                column_select.value = None

        def required_feedback(change: dict[str, Any]) -> None:
            if hydrating["active"]:
                return
            cid = str(column_select.value or "")
            selected = selected_column()
            name = str(selected.get("column_name") or "")
            if bool(change.get("new")):
                required_columns.add(cid)
            else:
                required_columns.discard(cid)
                required_columns.discard(name)
            refresh_column_options()
            render_table_summary()

        def datatype_feedback(change: dict[str, Any]) -> None:
            if hydrating["active"] or not change.get("new"):
                return
            cid = str(column_select.value or "")
            contracted_types[cid] = str(change["new"])
            payload = json.loads(str(current["contract"].get("contract_payload_json") or "{}"))
            for item in payload.get("table", {}).get("columns", []):
                if str(item.get("column_id") or "") == cid:
                    item["data_type"] = contracted_types[cid]
                    break
            current["contract"]["contract_payload_json"] = json.dumps(
                payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
            )
            state["dirty"] = True
            refresh_manifest()
            refresh_column_options()
            hydrate_column(cid)
            set_status("Contract datatype choice staged locally. Save the Data Contract to persist.")

        required.observe(required_feedback, names="value")
        datatype_choice.observe(datatype_feedback, names="value")
        column_search.observe(refresh_column_options, names="value")
        rebuild_column_options()
        refresh_column_options()

        column_left = (
            widgets.HTML(
                "<div style='color:#0f6cbd;font-size:11px;font-weight:800;"
                "text-transform:uppercase;letter-spacing:.07em;'>Columns</div>"
                "<div style='color:#667085;font-size:12px;line-height:1.45;margin-top:4px;'>"
                "Select one column to review metadata, profile evidence, Sensitive Data, "
                "and Data Quality rules.</div>"
            ),
            column_search,
            column_option_style,
            column_select,
        )
        dq_editor = widgets.VBox(
            [
                dq_help,
                dq_usage,
                widgets.HBox(
                    [dq_enabled, dq_block],
                    layout=checkbox_row_layout,
                ),
                *dq_parameter_controls,
                dq_suggestion,
                dq_ai,
                shared.action_row(widgets, [suggest_dq, accept_dq_suggestion, save_dq]),
            ],
            layout=widgets.Layout(width="100%", gap="8px", padding="2px 0 0 0"),
        )
        dq_panel = shared.form_section(
            widgets,
            title="Column data quality",
            children=[
                widgets.GridBox(
                    [dq_type, dq_editor],
                    layout=widgets.Layout(
                        width="100%",
                        grid_template_columns="minmax(190px, 32fr) minmax(0, 68fr)",
                        grid_gap="16px",
                        align_items="flex-start",
                    ),
                ),
            ],
        )
        column_schema_row = widgets.HBox(
            [
                widgets.HTML(
                    "<div style='color:#253858;font-size:13px;font-weight:600;'>Schema</div>",
                    layout=widgets.Layout(width="150px", min_width="150px"),
                ),
                widgets.VBox(
                    [required, datatype_choice],
                    layout=widgets.Layout(width="560px", max_width="100%", gap="6px"),
                ),
            ],
            layout=widgets.Layout(width="100%", gap="12px", align_items="center"),
        )
        column_ai_row = widgets.HBox(
            [
                widgets.HTML("", layout=widgets.Layout(width="150px", min_width="150px")),
                widgets.VBox(
                    [
                        column_description_ai,
                        shared.action_row(
                            widgets, [accept_column_description, rerun_column_description]
                        ),
                    ],
                    layout=widgets.Layout(width="560px", max_width="100%", gap="6px"),
                ),
            ],
            layout=widgets.Layout(width="100%", gap="12px", align_items="flex-start"),
        )
        column_right = (
            column_context,
            shared.form_section(
                widgets,
                title="Column definition",
                children=[
                    column_schema_row,
                    column_classification,
                    column_description,
                    column_ai_row,
                ],
            ),
            shared.form_section(
                widgets,
                title="Profile evidence",
                children=[profile_context],
            ),
            shared.form_section(
                widgets,
                title="Sensitive Data",
                children=[
                    widgets.HBox(
                        [sensitive_enabled, sensitive_block],
                        layout=checkbox_row_layout,
                    ),
                    sensitive_ai,
                    shared.action_row(widgets, [accept_sensitive, rerun_sensitive]),
                    pii_type,
                    pii_reason,
                    sensitive_treatment,
                    mask_start,
                    mask_end,
                    mask_character,
                    bucket_bins,
                    bucket_labels,
                ],
            ),
            dq_panel,
            shared.action_row(widgets, [save_column]),
        )
        view_content["Columns"] = (column_left, column_right)

        if ai_mode == "with_ai":
            run_table_ai()
        else:
            render_table_ai()
        if column_options:
            column_select.value = column_options[0][1]
            hydrate_column(str(column_select.value))
            render_column_ai(str(column_select.value))
            if ai_mode == "with_ai":
                prepare_column_ai(str(column_select.value))

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
        advanced_enabled = widgets.Checkbox(description="Enabled", disabled=not editable)
        advanced_block = widgets.Checkbox(description="Block on failure", disabled=not editable)
        advanced_help = widgets.HTML()
        advanced_save = widgets.Button(description="Apply configuration", button_style="primary", disabled=not editable)
        advanced_lookup: dict[str, dict[str, Any]] = {}
        for control in (
            advanced_type, advanced_saved, advanced_columns, advanced_operator,
            custom_expression, custom_description,
        ):
            control.layout.width = "100%"
            control.layout.max_width = "560px"
            control.layout.min_width = "0"
        advanced_type.layout.height = "120px"
        advanced_saved.layout.height = "120px"
        advanced_columns.layout.height = "150px"

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
            advanced_enabled.value = bool(rule and rule.get("is_active", True))
            advanced_block.value = str(rule.get("action") or "Warn") == "Block"

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
                stage_guardrails([guardrail_record(
                    "data_quality", kind, params,
                    action="Block" if advanced_block.value else "Warn",
                    existing=existing, active=advanced_enabled.value,
                )])
                set_status("Advanced Data Quality configuration staged locally.")
            except (ValueError, RuntimeError) as exc:
                set_status(str(exc), error=True)

        advanced_type.observe(hydrate_advanced_type, names="value")
        advanced_saved.observe(hydrate_advanced_saved, names="value")
        advanced_save.on_click(save_advanced_clicked)
        hydrate_advanced_type()
        advanced_left = (
            widgets.HTML(
                "<div style='color:#0f6cbd;font-size:11px;font-weight:800;"
                "text-transform:uppercase;letter-spacing:.07em;'>Advanced rules</div>"
                "<div style='color:#667085;font-size:12px;line-height:1.45;margin-top:4px;'>"
                "Multi-column and custom Data Quality configurations.</div>"
            ),
            advanced_type,
            widgets.HTML(
                "<div style='color:#253858;font-size:13px;font-weight:700;margin-top:8px;'>"
                "Saved configurations</div>"
            ),
            advanced_saved,
        )
        advanced_right = (
            shared.form_section(
                widgets,
                title="Configuration",
                children=[
                    advanced_help,
                    widgets.HBox(
                        [advanced_enabled, advanced_block],
                        layout=checkbox_row_layout,
                    ),
                    advanced_columns,
                    advanced_operator,
                    custom_expression,
                    custom_description,
                    shared.action_row(widgets, [advanced_save]),
                ],
            ),
        )
        view_content["Advanced"] = (advanced_left, advanced_right)


        # Manifest: current working contract plus changes since the last persisted draft.
        payload = refresh_manifest() or {}
        saved_payload = state.get("_saved_payload") or {}
        sections = _manifest_sections(payload)

        def review_change_html() -> str:
            changes: list[str] = []
            old_table = dict(saved_payload.get("table") or {})
            new_table = dict(payload.get("table") or {})
            old_processing = old_table.get("processing") or {}
            new_processing = new_table.get("processing") or {}
            if old_processing != new_processing:
                changes.append(
                    "<li><b>Processing</b> changed from "
                    f"<code>{html.escape(json.dumps(old_processing, sort_keys=True))}</code> to "
                    f"<code>{html.escape(json.dumps(new_processing, sort_keys=True))}</code></li>"
                )

            def enrichment_map(doc: dict[str, Any]) -> dict[tuple[str, str], str]:
                result: dict[tuple[str, str], str] = {}
                enrichment = doc.get("enrichment") or {}
                for item in [*(enrichment.get("table") or []), *(enrichment.get("columns") or [])]:
                    result[(str(item.get("column_id") or ""), str(item.get("enrichment_type") or ""))] = str(item.get("value") or "")
                return result

            old_enrichment, new_enrichment = enrichment_map(saved_payload), enrichment_map(payload)
            for key in sorted(set(old_enrichment) | set(new_enrichment)):
                before, after = old_enrichment.get(key, ""), new_enrichment.get(key, "")
                if before != after:
                    target = key[0] or "Table"
                    changes.append(
                        f"<li><b>{html.escape(target)} · {html.escape(key[1])}</b>: "
                        f"{html.escape(before or 'Not set')} → {html.escape(after or 'Not set')}</li>"
                    )

            old_columns = {
                str(item.get("column_id") or ""): item
                for item in old_table.get("columns", []) if item.get("column_id")
            }
            for item in new_table.get("columns", []):
                cid = str(item.get("column_id") or "")
                before = str(old_columns.get(cid, {}).get("data_type") or "")
                after = str(item.get("data_type") or "")
                if before and after and before != after:
                    changes.append(
                        f"<li><b>{html.escape(str(item.get('column_name') or cid))} datatype</b>: "
                        f"{html.escape(before)} → {html.escape(after)}</li>"
                    )

            def active_rules(doc: dict[str, Any]) -> dict[str, dict[str, Any]]:
                return {
                    str(item.get("guardrail_rule_id") or item.get("rule_id") or ""): item
                    for item in doc.get("guardrails", []) if item.get("is_active", True)
                }
            old_rules, new_rules = active_rules(saved_payload), active_rules(payload)
            added = [rule for key, rule in new_rules.items() if key not in old_rules]
            removed = [rule for key, rule in old_rules.items() if key not in new_rules]
            changed = [
                rule for key, rule in new_rules.items()
                if key in old_rules and rule != old_rules[key]
            ]
            if added:
                changes.append(f"<li><b>Guardrails</b>: +{len(added)} enabled configuration(s)</li>")
            if removed:
                changes.append(f"<li><b>Guardrails</b>: -{len(removed)} configuration(s)</li>")
            if changed:
                changes.append(f"<li><b>Guardrails</b>: {len(changed)} configuration(s) changed</li>")
            if not changes:
                return "<p style='color:#667085;'>No unsaved changes. Current draft matches the last save.</p>"
            return (
                "<div style='border-left:4px solid #0f6cbd;padding:10px 12px;background:#f5f9fd;'>"
                "<b>Changes since last save</b><ul style='margin-bottom:0;'>"
                + "".join(changes) + "</ul></div>"
            )

        current_summary = widgets.HTML(
            "<div style='font-size:16px;font-weight:700;color:#172b4d;'>Current draft</div>"
            "<div style='color:#667085;font-size:12px;margin-top:3px;'>"
            "This is the complete contract that will replace the saved draft JSON.</div>"
        )
        change_preview = widgets.HTML(review_change_html())
        manifest_preview = widgets.HTML(
            value=sections["Review"],
            layout=widgets.Layout(width="100%", height="auto", overflow="visible"),
        )

        def refresh_review() -> None:
            nonlocal payload
            payload = refresh_manifest() or {}
            refreshed_sections = _manifest_sections(payload)
            manifest_preview.value = refreshed_sections["Review"]
            change_preview.value = review_change_html()
        state["_refresh_review"] = refresh_review
        exact_json_content = widgets.HTML(
            f"<details><summary>Exact JSON manifest</summary><pre>{html.escape(_expose_manifest(payload))}</pre></details>"
        )
        exact_json = shared.preview_region(widgets, exact_json_content, height="240px")
        refresh_review_base = refresh_review

        def refresh_review() -> None:
            refresh_review_base()
            exact_json_content.value = (
                "<details><summary>Exact JSON manifest</summary><pre>"
                + html.escape(_expose_manifest(payload))
                + "</pre></details>"
            )

        state["_refresh_review"] = refresh_review
        actions: list[Any] = []
        save_contract_button = None
        discard_contract_button = None
        if editable:
            save_contract_button = widgets.Button(
                description="Save Data Contract",
                button_style="primary",
            )
            discard_contract_button = widgets.Button(description="Discard changes")
            freeze_button = widgets.Button(
                description=f"Freeze v{row['contract_version']}…",
                disabled=bool(state.get("dirty")),
            )
            freeze_confirm = widgets.VBox(layout=widgets.Layout(display="none"))
            freeze_cancel = widgets.Button(description="Cancel")
            freeze_confirm_button = widgets.Button(
                description=f"Freeze v{row['contract_version']}",
                button_style="danger",
            )
            freeze_confirm.children = (
                widgets.HTML(
                    f"<b>Freeze Data Contract v{row['contract_version']}?</b><br>"
                    "This version will become immutable. Further changes require a new contract version."
                ),
                widgets.HBox(
                    [freeze_cancel, freeze_confirm_button],
                    layout=widgets.Layout(gap="8px"),
                ),
            )

            def save_contract_clicked(_button: Any) -> None:
                try:
                    scope = (str(current["contract_id"]), int(current["contract_version"]))
                    unapplied_columns = state["_column_drafts"].get(scope, {})
                    if unapplied_columns:
                        raise ValueError(
                            "Apply retained Column changes before saving the Data Contract."
                        )
                    save_data_contract_session()
                except (TypeError, ValueError, RuntimeError) as exc:
                    set_status(str(exc), error=True)

            def freeze_clicked(_button: Any) -> None:
                if state.get("dirty"):
                    set_status("Save the Data Contract before freezing this version.", error=True)
                    return
                freeze_confirm.layout.display = ""

            def freeze_cancel_clicked(_button: Any) -> None:
                freeze_confirm.layout.display = "none"

            def freeze_confirm_clicked(_button: Any) -> None:
                try:
                    freeze_confirm_button.disabled = True
                    freeze()
                    render()
                    set_status(f"Data Contract v{row['contract_version']} is FROZEN.")
                except (ValueError, RuntimeError) as exc:
                    freeze_confirm_button.disabled = False
                    set_status(str(exc), error=True)

            def discard_contract_clicked(_button: Any) -> None:
                try:
                    discard_data_contract_session()
                except (ValueError, RuntimeError) as exc:
                    set_status(str(exc), error=True)

            save_contract_button.on_click(save_contract_clicked)
            discard_contract_button.on_click(discard_contract_clicked)
            freeze_button.on_click(freeze_clicked)
            freeze_cancel.on_click(freeze_cancel_clicked)
            freeze_confirm_button.on_click(freeze_confirm_clicked)
            actions.extend([
                widgets.HBox(
                    [save_contract_button, discard_contract_button, freeze_button],
                    layout=widgets.Layout(gap="8px", align_items="center"),
                ),
                freeze_confirm,
            ])
        else:
            agreement_id = widgets.Text(**shared.widget_common(widgets, "Data Agreement ID"))
            agreement_version = widgets.Text(**shared.widget_common(widgets, "Agreement version"))
            activate_button = widgets.Button(
                description="Activate for Production",
                disabled=str(row.get("status") or "").lower() != "frozen" or row.get("is_active") is True,
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
        review_left = (
            widgets.HTML(
                "<div style='color:#0f6cbd;font-size:11px;font-weight:800;"
                "text-transform:uppercase;letter-spacing:.07em;'>Manifest</div>"
                + "<div style='color:#172b4d;font-size:18px;font-weight:700;margin-top:6px;'>"
                + html.escape(
                    f"{str(table.get('schema_name') or '')}.{str(table.get('table_name') or state.get('table_id') or '')}"
                )
                + "</div>"
                + "<div style='color:#667085;font-size:12px;margin-top:5px;'>"
                + f"v{row['contract_version']} · {html.escape(str(row.get('status') or '').upper())}</div>"
            ),
            widgets.HTML(
                "<div style='color:#667085;font-size:12px;line-height:1.5;margin-top:8px;'>"
                "Notebook variable<br><b style='color:#172b4d;'>DATA_CONTRACT_MANIFEST</b></div>"
            ),
        )
        review_right = (
            shared.form_section(
                widgets,
                title="Current contract",
                children=[current_summary, change_preview, manifest_preview],
            ),
            shared.form_section(
                widgets,
                title="Exact JSON",
                children=[exact_json],
            ),
            *actions,
        )
        view_content["Manifest & Freeze"] = (review_left, review_right)
        apply_view()


        state["_controls"].update({
            "table_description": table_description, "table_classification": table_classification,
            "table_save": table_save, "table_guardrails": table_rules,
            "load_strategy": load_strategy_control,
            "processing_source": processing_source_hint,
            "processing_parameters": processing_parameter_controls,
            "partition_column": partition_column_control,
            "watermark_column": watermark_column_control,
            "key_columns": key_columns_control,
            "effective_column": effective_column_control,
            "tracked_columns": tracked_columns_control,
            "pipeline_refresh": pipeline_refresh,
            "table_description_ai": table_description_ai,
            "accept_table_description": accept_table_description,
            "rerun_table_description": rerun_table_description,
            "column_search": column_search,
            "column_select": column_select, "column_context": column_context,
            "profile_context": profile_context, "column_description": column_description,
            "column_classification": column_classification, "required": required,
            "datatype_choice": datatype_choice, "column_option_style": column_option_style,
            "save_column_enrichment": save_column_enrichment, "save_required": save_required,
            "save_column": save_column, "dq_panel": dq_panel, "dq_editor": dq_editor,
            "sensitive_enabled": sensitive_enabled, "sensitive_treatment": sensitive_treatment,
            "column_description_ai": column_description_ai,
            "accept_column_description": accept_column_description,
            "rerun_column_description": rerun_column_description,
            "pii_type": pii_type, "pii_reason": pii_reason,
            "sensitive_ai": sensitive_ai, "accept_sensitive": accept_sensitive,
            "rerun_sensitive": rerun_sensitive,
            "sensitive_block": sensitive_block, "mask_start": mask_start,
            "mask_end": mask_end, "mask_character": mask_character,
            "bucket_bins": bucket_bins, "bucket_labels": bucket_labels,
            "save_sensitive": save_sensitive,
            "dq_type": dq_type, "dq_parameter_controls": dq_parameter_controls,
            "dq_max_missing": dq_max_missing, "dq_blank_missing": dq_blank_missing,
            "dq_value_mode": dq_value_mode, "dq_values": dq_values,
            "dq_minimum": dq_minimum, "dq_minimum_inclusive": dq_minimum_inclusive,
            "dq_maximum": dq_maximum, "dq_maximum_inclusive": dq_maximum_inclusive,
            "dq_pattern": dq_pattern, "dq_enabled": dq_enabled, "dq_block": dq_block,
            "suggest_dq": suggest_dq, "dq_ai": dq_ai,
            "dq_suggestion": dq_suggestion, "accept_dq_suggestion": accept_dq_suggestion,
            "save_dq": save_dq,
            "advanced_type": advanced_type, "advanced_saved": advanced_saved,
            "advanced_columns": advanced_columns, "advanced_enabled": advanced_enabled,
            "advanced_block": advanced_block, "advanced_save": advanced_save,
            "advanced_operator": advanced_operator, "custom_expression": custom_expression,
            "custom_description": custom_description,
            "manifest_preview": manifest_preview,
            "save_data_contract": save_contract_button,
            "discard_data_contract": discard_contract_button,
            "freeze": freeze_button if editable else None,
            "freeze_confirm": freeze_confirm_button if editable else None,
            "activate": next((control for control in actions if getattr(control, "description", "").startswith("Activate")), None),
        })

    open_with_ai_button = widgets.Button(
        description="Open with AI suggestions",
        button_style="info",
        disabled=not bool(ai_enrichment.get("enabled")),
        layout=widgets.Layout(width="220px"),
    )
    open_without_ai_button = widgets.Button(
        description="Open without AI",
        button_style="primary",
        layout=widgets.Layout(width="220px"),
    )
    open_progress = widgets.HTML()

    def set_open_progress(label: str, percent: int) -> None:
        """Show real opening stages so slow AI calls still feel visibly active."""
        bounded = max(0, min(100, int(percent)))
        open_progress.value = (
            "<div style='width:440px;max-width:100%;'>"
            f"<div style='font-size:12px;margin-bottom:4px;'>{html.escape(label)}</div>"
            "<div style='height:6px;background:#e1e6eb;border-radius:3px;overflow:hidden;'>"
            f"<div style='width:{bounded}%;height:100%;background:#2b88d8;"
            "transition:width .25s ease;'></div></div></div>"
        )

    ai_availability = widgets.HTML(
        "" if ai_enrichment.get("enabled") else
        "<span style='color:#666;font-size:12px;'>AI suggestions unavailable: disabled in 00_env_config.</span>"
    )
    change_table_button = widgets.Button(description="Change table")
    selector_actions = widgets.VBox(
        [
            widgets.HBox(
                [open_with_ai_button, open_without_ai_button],
                layout=widgets.Layout(width="100%", justify_content="center", gap="12px"),
            ),
            ai_availability,
            open_progress,
        ],
        layout=widgets.Layout(width="100%", align_items="center", gap="8px", margin="16px 0 0 0"),
    )
    selector_panel = widgets.VBox(
        [selector, selector_actions],
        layout=widgets.Layout(width="100%", height="auto", overflow="visible", display=""),
    )
    editor_shell = widgets.VBox(
        [
            widgets.HBox(
                [top_nav],
                layout=widgets.Layout(
                    width="100%", justify_content="center", margin="4px 0 6px 0",
                ),
            ),
            workspace,
        ],
        layout=widgets.Layout(width="100%", height="auto", overflow="visible", display="none", gap="7px"),
    )

    def refresh_table_options(*_args: Any) -> None:
        selected_store = str(store_control.value or "")
        selected_schema = str(schema_control.value or "")
        rows = [
            row for row in table_rows
            if str(row.get("layer") or "") == selected_store
            and str(row.get("schema_name") or "") == selected_schema
        ]
        table_control.options = [
            ("Select governed table", ""),
            *[
                (str(row.get("table_name") or row.get("table_id")), str(row["table_id"]))
                for row in rows
            ],
        ]
        pending = str(state.get("pending_table_id") or "")
        values = [item[1] if isinstance(item, tuple) else item for item in table_control.options]
        table_control.value = pending if pending in values else ""

    def refresh_schema_options(*_args: Any) -> None:
        selected_store = str(store_control.value or "")
        schemas = list(dict.fromkeys(
            str(row.get("schema_name") or "")
            for row in table_rows
            if str(row.get("layer") or "") == selected_store
        ))
        schema_control.options = schemas
        pending_row = next(
            (row for row in table_rows if str(row.get("table_id") or "") == str(state.get("pending_table_id") or "")),
            None,
        )
        preferred = str((pending_row or {}).get("schema_name") or "")
        schema_control.value = preferred if preferred in schemas else (schemas[0] if schemas else None)
        refresh_table_options()

    def table_changed(change: dict[str, Any]) -> None:
        selected = str(change.get("new") or "")
        state["pending_table_id"] = selected or None
        matches = [row for row in state["contracts"] if str(row.get("table_id") or "") == selected]
        contract_control.options = [
            *[(f"v{row['contract_version']} · {str(row.get('status') or '').title()}", str(row["contract_version"])) for row in matches],
            ("New draft", "new"),
        ]
        preferred = state.get("pending_contract_version")
        preferred_value = str(preferred) if preferred is not None else None
        available = [str(row["contract_version"]) for row in matches]
        if preferred_value in available:
            contract_control.value = preferred_value
        elif matches:
            contract_control.value = str(matches[0]["contract_version"])
        else:
            contract_control.value = "new"

    def contract_changed(change: dict[str, Any]) -> None:
        value = change.get("new")
        state["pending_contract_version"] = None if value in (None, "", "new") else int(value)

    def open_selected(*, with_ai: bool) -> None:
        selected_table = str(state.get("pending_table_id") or "")
        selected_contract = contract_control.value
        if not selected_table or not selected_contract:
            set_status("Select a governed table and contract before opening.", error=True)
            return
        open_with_ai_button.disabled = True
        open_without_ai_button.disabled = True
        state["_opening_with_ai"] = bool(with_ai)
        set_open_progress("Opening contract…", 20)
        try:
            if selected_contract == "new":
                state["table_id"] = selected_table
                new_draft()
            else:
                select(selected_table, int(selected_contract))
            scope = (
                str(state["current"]["contract_id"]),
                int(state["current"]["contract_version"]),
            )
            state["_ai_mode"][scope] = "with_ai" if with_ai else "without_ai"
            set_open_progress(
                "Preparing AI context…" if with_ai else "Loading editor…",
                35 if with_ai else 70,
            )
            render()
            set_open_progress("Building editor…", 96)
            selector_panel.layout.display = "none"
            editor_shell.layout.display = ""
            open_progress.value = ""
            set_status(
                f"Opened Data Contract v{state['contract_version']} for {state['table_id']}"
                + (" with AI suggestions." if with_ai else " without AI.")
            )
        except Exception as exc:
            open_progress.value = ""
            set_status(str(exc), error=True)
        finally:
            state["_opening_with_ai"] = False
            open_with_ai_button.disabled = not bool(ai_enrichment.get("enabled"))
            open_without_ai_button.disabled = False

    def change_table(_button: Any) -> None:
        state["current"] = None
        state["manifest"] = None
        state["table_id"] = None
        state["contract_version"] = None
        editor_shell.layout.display = "none"
        selector_panel.layout.display = ""
        set_status("Select a governed table and contract.")

    open_with_ai_button.on_click(lambda _button: open_selected(with_ai=True))
    open_without_ai_button.on_click(lambda _button: open_selected(with_ai=False))
    change_table_button.on_click(change_table)
    store_control.observe(refresh_schema_options, names="value")
    schema_control.observe(refresh_table_options, names="value")
    table_control.observe(table_changed, names="value")
    contract_control.observe(contract_changed, names="value")

    pending_row = next(
        (row for row in table_rows if str(row.get("table_id") or "") == str(state.get("pending_table_id") or "")),
        None,
    )
    preferred_store = str((pending_row or {}).get("layer") or "")
    store_values = [item[1] if isinstance(item, tuple) else item for item in store_control.options]
    if preferred_store in store_values:
        store_control.value = preferred_store
    elif store_values:
        store_control.value = store_values[0]
    refresh_schema_options()
    if table_control.value:
        table_changed({"new": table_control.value})
    render()
    page = shared.form_page(
        widgets, title="Data Contract",
        description="Select, author, review, freeze, and activate one governed table contract.",
        children=[selector_panel, editor_shell, status],
    )
    state["_controls"].update({
        "page": page, "selector_panel": selector_panel, "editor_shell": editor_shell,
        "store": store_control, "schema": schema_control,
        "open_with_ai": open_with_ai_button, "open_without_ai": open_without_ai_button,
        "open": open_without_ai_button, "open_progress": open_progress,
        "change_table": change_table_button,
    })
    ip.display(page)
    return state
