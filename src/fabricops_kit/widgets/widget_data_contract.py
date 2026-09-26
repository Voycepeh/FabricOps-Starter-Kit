"""Unified Data Contract governance authoring, review, and freeze widget."""

from __future__ import annotations

import html
import json
import uuid
from datetime import datetime, timedelta
from typing import Any, Mapping

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.io.shared import get_spark_session
from fabricops_kit.widgets import shared
from fabricops_kit.widgets.enrichment_shared import (
    PII_LABELS,
    build_ai_business_rule_context,
    build_ai_dq_context,
    build_ai_enrichment_context,
    build_ai_sensitive_data_context,
    suggest_enrichment,
    suggest_grain_key,
    suggest_dq_rules,
    suggest_business_rule,
    suggest_sensitive_data,
)

DATA_CONTRACT_MANIFEST: dict[str, Any] | None = None
DATA_CONTRACT_MANIFEST_JSON: str | None = None
_TABS = ("Table", "Columns", "Business Rules", "Manifest & Freeze")
_CLASSIFICATIONS = ("", "Public", "Internal", "Confidential", "Restricted")
_COLUMN_DQ_TYPES = ("completeness", "value_set", "range", "pattern")
_DQ_HELP = {
    "completeness": "Limit missing values, with explicit blank-text handling.",
    "uniqueness": "Require one column, or a table-level column combination, to be unique.",
    "value_set": "Allowed Values checks whether a column value belongs to an approved governed set.",
    "range": "Value Rules apply numeric or date conditions such as below, above, between, or outside bounds.",
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


def _manifest_sections(
    payload: dict[str, Any],
    *,
    column_profiles: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, str]:
    """Build one scannable review page from table, column, and cross-column contract rules."""
    table = payload.get("table", {})
    enrichments = payload.get("enrichment", {})
    guardrails = payload.get("guardrails", [])
    columns = table.get("columns", [])
    profiles = dict(column_profiles or {})

    column_enrichment: dict[tuple[str, str], str] = {
        (str(row.get("column_id") or ""), str(row.get("enrichment_type") or "")): str(
            row.get("value") or ""
        )
        for row in enrichments.get("columns", [])
    }
    required: set[str] = set()
    for rule in guardrails:
        if str(rule.get("guardrail_type") or "").lower() == "schema" and rule.get("is_active", True):
            required.update(_parameters(rule).get("required_columns", []))

    def parameter_text(row: Mapping[str, Any]) -> str:
        parts = []
        for name, value in _parameters(row).items():
            if value in (None, "", [], {}):
                continue
            if isinstance(value, list):
                shown = ", ".join(str(item) for item in value)
            elif isinstance(value, bool):
                shown = "Yes" if value else "No"
            else:
                shown = str(value)
            parts.append(f"{name.replace('_', ' ')}: {shown}")
        return " · ".join(parts)

    def rule_label(row: Mapping[str, Any]) -> str:
        return str(row.get("rule_type") or row.get("guardrail_type") or "").replace("_", " ").title()

    def rule_list(rows: list[dict[str, Any]]) -> str:
        items = "".join(
            "<li><b>{}</b> · {}{}</li>".format(
                html.escape(rule_label(row)),
                html.escape(str(row.get("action") or "Warn")),
                (
                    " · " + html.escape(parameter_text(row))
                    if parameter_text(row) else ""
                ),
            )
            for row in rows
        ) or "<li>None configured</li>"
        return f"<ul>{items}</ul>"

    def business_rule_list(rows: list[dict[str, Any]]) -> str:
        if not rows:
            return "<ul><li>None configured</li></ul>"
        items = []
        for row in rows:
            params = _parameters(row)
            requirement = str(
                params.get("business_requirement") or params.get("description") or ""
            ).strip()
            columns = [str(value) for value in params.get("columns") or []]
            kind = str(row.get("rule_type") or "")
            review_required = (
                kind == "custom_expression"
                and bool(params.get("engineering_review_required", True))
            )
            review_status = str(
                params.get("engineering_review_status") or "pending"
            ).replace("_", " ").title()
            details = [
                f"<b>{html.escape(requirement or rule_label(row))}</b>",
                html.escape(rule_label(row)),
                html.escape(str(row.get("action") or "Warn")),
            ]
            if columns:
                details.append("Columns: " + html.escape(", ".join(columns)))
            if kind == "custom_expression" and params.get("expression"):
                details.append(
                    "Expression: <code>"
                    + html.escape(str(params["expression"]))
                    + "</code>"
                )
            if review_required:
                reviewer = str(params.get("engineering_reviewed_by") or "").strip()
                review = "Engineering review: " + html.escape(review_status)
                if reviewer and review_status.lower() == "approved":
                    review += " by " + html.escape(reviewer)
                details.append(review)
            else:
                details.append("Engineering review: Not required")
            items.append("<li>" + "<br>".join(details) + "</li>")
        return "<ul>" + "".join(items) + "</ul>"

    def example_values(column_id: str) -> str:
        profile = dict(profiles.get(column_id) or {})
        values = [
            value for value in list(profile.get("example_values") or [])
            if value not in (None, "")
        ][:3]
        if not values:
            fallback = []
            for name in ("min_value", "max_value"):
                value = profile.get(name)
                if value not in (None, "") and value not in fallback:
                    fallback.append(value)
            values = fallback[:2]
        if not values:
            return "<span style='color:#667085;'>—</span>"
        return "<br>".join(html.escape(str(value)) for value in values)

    active = [row for row in guardrails if row.get("is_active", True)]
    business_rules = [
        row for row in active
        if not str(row.get("column_id") or "")
        and str(row.get("guardrail_type") or "").lower() in {"data_quality", "dq"}
        and str(row.get("rule_type") or "") in {
            "column_relationship", "custom_expression"
        }
    ]
    business_rule_ids = {id(row) for row in business_rules}
    table_guardrails = [
        row for row in active
        if not str(row.get("column_id") or "") and id(row) not in business_rule_ids
    ]
    column_guardrails = [row for row in active if str(row.get("column_id") or "")]
    sensitive_by_column = {
        str(row.get("column_id") or ""): row
        for row in column_guardrails
        if str(row.get("guardrail_type") or "").lower() == "sensitive_data"
    }
    rules_by_column: dict[str, list[dict[str, Any]]] = {}
    for rule in column_guardrails:
        if str(rule.get("guardrail_type") or "").lower() == "sensitive_data":
            continue
        rules_by_column.setdefault(str(rule.get("column_id") or ""), []).append(rule)

    def sensitive_text(column_id: str) -> str:
        rule = sensitive_by_column.get(column_id)
        if not rule:
            return "Not PII"
        parameters = _parameters(rule)
        pii_type = str(parameters.get("pii_type") or "direct").lower()
        label = PII_LABELS.get(pii_type, pii_type.replace("_", " ").title())
        treatment = str(parameters.get("treatment") or rule.get("rule_type") or "").replace("_", " ").title()
        action = str(rule.get("action") or "Warn")
        detail = f"{label} · {treatment}" if treatment else label
        return f"{html.escape(detail)}<br><span style='color:#667085;'>{html.escape(action)}</span>"

    def column_rule_list() -> str:
        if not rules_by_column and not sensitive_by_column:
            return "<ul><li>None configured</li></ul>"
        items = []
        column_names = {
            str(row.get("column_id") or ""): str(row.get("column_name") or "")
            for row in columns
        }
        for column_id in sorted(set(rules_by_column) | set(sensitive_by_column)):
            name = column_names.get(column_id, column_id or "Unknown column")
            rules = []
            sensitive = sensitive_by_column.get(column_id)
            if sensitive:
                rules.append(
                    "<div><b>Sensitive Data</b> · "
                    + sensitive_text(column_id)
                    + "</div>"
                )
            rules.extend(
                "<div><b>{}</b> · {}{}</div>".format(
                    html.escape(rule_label(rule)),
                    html.escape(str(rule.get("action") or "Warn")),
                    (
                        "<br><span style='color:#667085;'>"
                        + html.escape(parameter_text(rule))
                        + "</span>"
                        if parameter_text(rule) else ""
                    ),
                )
                for rule in rules_by_column.get(column_id, [])
            )
            items.append(
                "<li><b>" + html.escape(name) + "</b><div style='margin-top:4px;'>"
                + "".join(rules) + "</div></li>"
            )
        return "<ul>" + "".join(items) + "</ul>"

    column_rows = "".join(
        "<tr>"
        "<td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td>"
        "</tr>".format(
            html.escape(str(row.get("column_name") or "")),
            example_values(str(row.get("column_id") or "")),
            html.escape(str(row.get("data_type") or "")),
            "Yes" if row.get("column_id") in required or row.get("column_name") in required else "No",
            sensitive_text(str(row.get("column_id") or "")),
            html.escape(column_enrichment.get(
                (str(row.get("column_id") or ""), "Classification"), ""
            )) or "<span style='color:#667085;'>—</span>",
            html.escape(column_enrichment.get(
                (str(row.get("column_id") or ""), "Description"), ""
            )) or "<span style='color:#667085;'>—</span>",
        )
        for row in columns
    )
    guardrail_count = len(table_guardrails) + len(column_guardrails) + len(business_rules)
    guardrail_sections = (
        "<div style='margin-top:8px;'><b>Table</b>"
        + rule_list(table_guardrails)
        + "</div>"
        "<div style='margin-top:8px;'><b>Columns</b>"
        + column_rule_list()
        + "</div>"
        "<div style='margin-top:8px;'><b>Business Rules</b>"
        + business_rule_list(business_rules)
        + "</div>"
    )
    details = (
        "<details open><summary><b>Column definitions</b> · "
        f"{len(columns)} columns</summary>"
        "<div style='overflow-x:auto;'>"
        "<table style='width:100%;font-size:12px;'><thead><tr>"
        "<th>Column</th><th>Examples</th><th>Datatype</th><th>Required</th>"
        "<th>Sensitive</th><th>Classification</th><th>Description</th>"
        f"</tr></thead><tbody>{column_rows}</tbody></table></div></details>"
        "<details><summary><b>Guardrails</b> · "
        f"{guardrail_count} configured</summary>{guardrail_sections}</details>"
    )
    return {"Review": details}

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

    def bold_value(value: Any, suffix: str = "") -> str:
        return f"<b>{html.escape(shown(value))}{suffix}</b>"

    facts = []
    for key, label, suffix in (
        ("row_count", "Row count", ""),
        ("distinct_count", "Distinct count", ""),
        ("distinct_percent", "Distinct percent", "%"),
        ("null_count", "Null count", ""),
        ("null_percent", "Null percent", "%"),
    ):
        if profile.get(key) is not None:
            facts.append(f"{label}: {bold_value(profile.get(key), suffix)}")

    lines = []
    if facts:
        lines.append(" · ".join(facts))

    range_facts = []
    if profile.get("min_value") is not None:
        range_facts.append(f"Min value: {bold_value(profile.get('min_value'))}")
    if profile.get("max_value") is not None:
        range_facts.append(f"Max value: {bold_value(profile.get('max_value'))}")
    if range_facts:
        lines.append(" · ".join(range_facts))

    distribution = []
    for key, label in (
        ("median_value", "Median value"),
        ("percentile_25_value", "Percentile 25 value"),
        ("percentile_75_value", "Percentile 75 value"),
        ("mean_value", "Mean value"),
        ("stddev_value", "Stddev value"),
    ):
        if profile.get(key) is not None:
            distribution.append(f"{label}: {bold_value(profile.get(key))}")
    if distribution:
        lines.append(" · ".join(distribution))

    if values:
        frequencies = []
        for item in values[:3]:
            parts = []
            if item.get("value") is not None:
                parts.append(f"Value: {bold_value(item.get('value'))}")
            if item.get("count") is not None:
                parts.append(f"Count: {bold_value(item.get('count'))}")
            if item.get("percent") is not None:
                parts.append(f"Percent: {bold_value(item.get('percent'), '%')}")
            if parts:
                frequencies.append(" · ".join(parts))
        lines.extend(frequencies)
    elif (
        profile.get("distinct_percent") is not None
        and float(profile["distinct_percent"]) >= 80.0
        and "date" not in str(profile.get("data_type") or "").lower()
        and "timestamp" not in str(profile.get("data_type") or "").lower()
    ):
        lines.append("Values are highly unique, so value frequency profiling was skipped.")

    return "<p style='margin:0;line-height:1.65;'>" + "<br>".join(lines) + "</p>"

def _scheduled_refresh_html(discovery: Mapping[str, Any]) -> str:
    """Render normalized writer Scheduled Refresh metadata from Catalogue."""
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
        f"{detail}<br><span style=\"color:#666;font-size:12px;\">Captured by writer pipeline · read-only</span></div>"
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
        "_pending_enrichment": {}, "_pending_guardrails": {}, "_validation_errors": {},
        "_column_dq_selection": {}, "_selector_refreshing": False, "dirty": False,
    }
    scheduled_refresh: dict[str, Any] = {"status": "uncaptured", "schedules": []}
    state["scheduled_refresh"] = scheduled_refresh
    contract_schedule = {"status": "unavailable", "schedules": []}

    def refresh_scheduled_refresh(selected_table: str) -> None:
        table_row = next(
            (item for item in table_rows if str(item.get("table_id") or "") == selected_table), {}
        )
        raw_value = str(table_row.get("scheduled_refresh_json") or "").strip()
        try:
            captured = json.loads(raw_value) if raw_value else {"status": "uncaptured", "schedules": []}
        except json.JSONDecodeError as exc:
            raise ValueError("Catalogue scheduled_refresh_json is invalid.") from exc
        if not isinstance(captured, Mapping):
            raise ValueError("Catalogue scheduled_refresh_json must contain an object.")
        status_value = str(captured.get("status") or "").strip().lower()
        if status_value not in {"configured", "not_configured", "uncaptured"}:
            raise ValueError(
                "Catalogue Scheduled Refresh status must be configured, not_configured, or uncaptured."
            )
        normalized = {
            "status": status_value,
            "schedules": list(captured.get("schedules") or []),
        }
        scheduled_refresh.clear()
        scheduled_refresh.update(normalized)
        contract_schedule.clear()
        contract_schedule.update(
            normalized if status_value != "uncaptured"
            else {"status": "unavailable", "schedules": []}
        )

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
        state["_validation_errors"].clear()
        state["table_id"] = str(selected_table or "").strip() or None
        matches = [
            row for row in state["contracts"]
            if str(row.get("table_id") or "") == str(state["table_id"] or "")
        ]
        if not matches:
            state["current"] = None
            return None
        if version is None:
            chosen = matches[0]
        else:
            chosen = next(
                (
                    row for row in matches
                    if int(row.get("contract_version") or 0) == int(version)
                ),
                None,
            )
            if chosen is None:
                raise ValueError(
                    f"Data Contract v{int(version)} was not found for table {state['table_id']}."
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
        prepare_save = state.get("_prepare_data_contract_save")
        if callable(prepare_save):
            prepare_save()
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
        state["_column_dq_selection"].pop(scope, None)
        state["dirty"] = False
        return_to_selector = state.get("_return_to_selector")
        if callable(return_to_selector):
            return_to_selector("Data Contract draft saved. Select a governed table and contract.")
        else:
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
        state["_column_dq_selection"].pop(scope, None)
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
        if str(scheduled_refresh.get("status") or "") == "uncaptured":
            raise ValueError(
                "Scheduled Refresh has not been captured by the writer pipeline. "
                "Run the writer pipeline before freezing this Data Contract."
            )
        if not current or str(current["contract"].get("status") or "").lower() != "draft":
            raise ValueError("Only a draft Data Contract version can be frozen.")
        if state.get("dirty"):
            raise ValueError("Save the Data Contract before freezing this version.")
        result = contracts.freeze_contract(
            draft=current["contract"], config=config, env=env,
            spark_session=spark, context=resolved, scheduled_refresh=contract_schedule,
        )
        latest = contracts.list_contract_governance_state(
            config=config, env=env, spark_session=spark,
        )
        state["contracts"] = latest["contracts"]
        select(str(state["table_id"]), int(state["contract_version"]))
        return result

    state.update(
        select=select, new_draft=new_draft, refresh_manifest=refresh_manifest,
        freeze=freeze, stage_enrichment=stage_enrichment,
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
        if str(name).strip().lower() != "metadata"
    ]
    selector_dropdown_layout = widgets.Layout(
        width="100%", min_width="0", max_width="100%",
    )
    store_control = widgets.Dropdown(options=store_options, layout=selector_dropdown_layout)
    schema_control = widgets.Dropdown(options=[], layout=selector_dropdown_layout)
    table_control = widgets.Dropdown(
        options=[("Select governed table", "")], layout=selector_dropdown_layout,
    )
    contract_control = widgets.Dropdown(layout=selector_dropdown_layout)

    def selector_field(label: str, control: Any) -> Any:
        return widgets.VBox(
            [
                widgets.HTML(f"<b>{html.escape(label)}</b>"),
                control,
            ],
            layout=widgets.Layout(
                width="100%", min_width="0", align_items="stretch", gap="4px",
            ),
        )

    selector = widgets.GridBox(
        [
            selector_field("Fabric store", store_control),
            selector_field("Schema", schema_control),
            selector_field("Table", table_control),
            selector_field("Contract", contract_control),
        ],
        layout=widgets.Layout(
            width="100%",
            grid_template_columns="repeat(4, minmax(0, 1fr))",
            grid_gap="16px 24px",
            overflow="visible",
        ),
    )

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
        scope = (str(current["contract_id"]), int(current["contract_version"]))
        old_id = str(old.get("guardrail_rule_id") or "")
        pending = state["_pending_guardrails"].get(scope, {})
        version = int(old.get("guardrail_version") or 0)
        if not old_id or old_id not in pending:
            version += 1
        return {
            "guardrail_rule_id": old.get("guardrail_rule_id") or str(uuid.uuid4()),
            "guardrail_version": version,
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

        def set_validation_error(key: str, error: Exception | str | None = None) -> None:
            errors: dict[str, str] = state["_validation_errors"]
            if error is None:
                errors.pop(key, None)
            else:
                errors[key] = str(error)

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
        raw_profile_key_candidates = table.get("profile_key_candidates_json") or "[]"
        if isinstance(raw_profile_key_candidates, str):
            try:
                raw_profile_key_candidates = json.loads(raw_profile_key_candidates or "[]")
            except json.JSONDecodeError:
                raw_profile_key_candidates = []
        profile_key_candidates = [
            dict(candidate)
            for candidate in raw_profile_key_candidates
            if isinstance(candidate, Mapping)
            and candidate.get("columns")
            and all(str(name) in column_names for name in candidate.get("columns", []))
        ] if isinstance(raw_profile_key_candidates, list) else []
        profiled_key_columns = (
            [str(name) for name in profile_key_candidates[0].get("columns", [])]
            if profile_key_candidates else []
        )
        temporal_column_names = [
            str(column.get("column_name") or "")
            for column in columns
            if any(
                marker in str(column.get("data_type") or "").lower()
                for marker in ("date", "timestamp", "datetime")
            )
        ]
        field_layout = widgets.Layout(width="100%", max_width="560px", min_width="0")
        compact_field_layout = widgets.Layout(width="360px", max_width="100%", min_width="0")
        checkbox_row_layout = widgets.Layout(gap="20px", align_items="center", flex_flow="row wrap")
        ai_visible = bool(ai_enrichment.get("enabled") and ai_mode == "with_ai")
        visible_tabs = _TABS if ai_visible else tuple(
            tab for tab in _TABS if tab != "Business Rules"
        )
        top_nav.options = visible_tabs
        if str(top_nav.value) not in visible_tabs:
            top_nav.value = "Table"

        # Table: passive identity plus explicitly saved Enrichment and table Guardrails.
        table_description = widgets.Textarea(
            value=enrichment_value(enrichments, "table", "Description"), disabled=not editable,
            **shared.widget_common(widgets, "Description", textarea=True),
        )
        table_classification = widgets.Dropdown(
            options=_CLASSIFICATIONS, value=enrichment_value(enrichments, "table", "Classification"),
            disabled=not editable, **shared.widget_common(widgets, "Classification"),
        )
        table_description.description = ""
        table_description.layout = widgets.Layout(width="100%", min_width="0", height="110px")
        table_classification.description = ""
        table_classification.layout = widgets.Layout(width="250px", max_width="100%", min_width="0")
        table_description_ai = widgets.HTML()
        accept_table_description = widgets.Button(description="Apply", disabled=not editable)
        rerun_table_description = widgets.Button(description="Re-run", disabled=not editable)

        # Table grain and row key: grain is descriptive Enrichment; selected key columns
        # create one table-level uniqueness guardrail.
        table_grain = widgets.Text(
            value=enrichment_value(enrichments, "table", "Grain"), disabled=not editable,
            placeholder="Example: One row per order line",
            **shared.widget_common(widgets, "Row grain"),
        )
        table_grain.layout = widgets.Layout(
            width="100%", max_width="560px", min_width="0"
        )
        existing_row_key = next((
            rule for rule in guardrails
            if str(rule.get("guardrail_type") or "").lower() in {"data_quality", "dq"}
            and str(rule.get("rule_type") or "") == "uniqueness"
            and not str(rule.get("column_id") or "")
        ), {})
        existing_row_key_columns = [
            str(name) for name in _parameters(existing_row_key).get("columns", [])
            if str(name) in column_names
        ]
        row_key_columns = widgets.SelectMultiple(
            options=column_names,
            value=tuple(existing_row_key_columns or profiled_key_columns),
            disabled=not editable,
            **shared.widget_common(widgets, "Row key columns"),
        )
        row_key_columns.layout = widgets.Layout(
            width="100%", max_width="560px", min_width="0", height="120px"
        )
        row_key_block = widgets.Checkbox(
            value=str(existing_row_key.get("action") or "Block") == "Block",
            description="Block on duplicate row keys",
            disabled=not editable,
        )
        grain_profile_evidence = widgets.HTML()
        grain_ai = widgets.HTML()
        suggest_grain = widgets.Button(
            description="Suggest grain",
            disabled=(
                not editable or not ai_enrichment.get("enabled") or ai_mode != "with_ai"
            ),
        )
        accept_grain = widgets.Button(description="Apply", disabled=True)

        def render_grain_profile_evidence() -> None:
            if profile_key_candidates:
                rows = "".join(
                    "<li><code>{}</code> · <b>{}%</b> unique · no missing key values</li>".format(
                        html.escape(" + ".join(str(name) for name in candidate.get("columns", []))),
                        html.escape(str(candidate.get("uniqueness_percent") or 100)),
                    )
                    for candidate in profile_key_candidates[:8]
                )
                grain_profile_evidence.value = (
                    "<div style='color:#667085;font-size:12px;line-height:1.5;'>"
                    "<b>Profile evidence</b><ul style='margin:5px 0 0 18px;'>"
                    + rows
                    + "</ul><span>The smallest proven candidate is preselected as the row key. "
                    "Governance defines the business grain; the frozen contract later enforces the selected key.</span></div>"
                )
                return
            grain_profile_evidence.value = (
                "<div style='color:#667085;font-size:12px;line-height:1.5;'>"
                "<b>Profile evidence</b><br>"
                "No row key suggestion available from the latest profile. "
                "Select a row key manually if this table has one.</div>"
            )

        def run_grain_ai(*_args: Any) -> None:
            if suggest_grain.disabled:
                return
            try:
                render_grain_profile_evidence()
                profile_rows = []
                for column in columns:
                    cid = str(column.get("column_id") or "")
                    profile_value = load_profile_context(cid)
                    profile = dict(profile_value.get("profile") or {})
                    profile_rows.append({
                        "column_name": str(column.get("column_name") or ""),
                        "data_type": str(column.get("data_type") or ""),
                        "description": enrichment_value(
                            enrichments, "column", "Description", cid
                        ),
                        **{
                            name: profile.get(name)
                            for name in (
                                "row_count", "non_null_count", "null_count", "null_percent",
                                "distinct_count", "distinct_percent",
                            )
                            if profile.get(name) is not None
                        },
                    })
                suggestion = suggest_grain_key(
                    {
                        "table_name": str(table.get("table_name") or ""),
                        "schema_name": str(table.get("schema_name") or ""),
                        "table_description": str(table_description.value or ""),
                        "table_classification": str(table_classification.value or ""),
                        "profile_key_candidates": profile_key_candidates,
                        "columns": profile_rows,
                    },
                    prompt=str(ai_enrichment.get("grain_prompt") or ""),
                )
                ai_state["table"]["grain_key"] = suggestion
                key_text = (
                    ", ".join(profiled_key_columns)
                    if profiled_key_columns else "No row key suggestion available"
                )
                grain_ai.value = (
                    "<div style='background:#f6f8fa;border-left:3px solid #0f6cbd;"
                    "padding:9px 11px;font-size:12px;line-height:1.5;'>"
                    f"<b>Suggested grain:</b> {html.escape(suggestion['grain'] or 'Not inferred')}<br>"
                    f"<b>Profiled row key:</b> {html.escape(key_text)}"
                    "<details style='margin-top:5px;color:#667085;'>"
                    "<summary style='cursor:pointer;'>Why this suggestion?</summary>"
                    f"<div style='margin-top:4px;'>{html.escape(suggestion['rationale'])}</div>"
                    "</details></div>"
                )
                accept_grain.disabled = False
            except (TypeError, ValueError, RuntimeError) as exc:
                ai_state["table"].pop("grain_key", None)
                accept_grain.disabled = True
                grain_ai.value = f"<p style='color:#a4262c'>{html.escape(str(exc))}</p>"

        def accept_grain_ai(_button: Any) -> None:
            suggestion = ai_state["table"].get("grain_key") or {}
            table_grain.value = str(suggestion.get("grain") or "")
            render_table_summary()

        suggest_grain.on_click(run_grain_ai)
        accept_grain.on_click(accept_grain_ai)
        render_grain_profile_evidence()

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
                table_description_ai.value = "<p>Disabled in 00_env_config.</p>"
            elif not editable:
                table_description_ai.value = "<p>Not run for review-only versions.</p>"
            elif ai_mode != "with_ai":
                message = (
                    "Skipped for this contract session."
                    if ai_mode == "without_ai"
                    else "Choose Run with AI suggestions above."
                )
                table_description_ai.value = f"<p>{message}</p>"
            else:
                table_description_ai.value = _suggestion_html(
                    "Description", ai_state["table"].get("description"), show_heading=False
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
                description_context = build_ai_enrichment_context(
                    table,
                    metadata_level="table",
                    existing_description=str(table_description.value or ""),
                    column_rows=columns,
                )
                grain_suggestion = ai_state["table"].get("grain_key") or {}
                description_context["grain"] = str(
                    table_grain.value or grain_suggestion.get("grain") or ""
                )
                description_context["classification"] = str(table_classification.value or "")
                result = suggest_enrichment(
                    description_context,
                    description_prompt=str(ai_enrichment.get("table_description_prompt") or ""),
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
            display_controls: list[Any] = []
            if kind == "freshness":
                refresh_expectation = widgets.Dropdown(
                    options=[
                        ("Recurring", "recurring"),
                        ("No refresh expected", "static"),
                    ],
                    value=(
                        "static"
                        if str(existing.get("rule_type") or "").lower() == "skip"
                        or str(existing_parameters.get("refresh_expectation") or "").lower() == "static"
                        else "recurring"
                    ),
                    disabled=not editable,
                    **shared.widget_common(widgets, "Refresh expectation"),
                )
                refresh_expectation.layout = field_layout
                configured_freshness_column = str(
                    existing_parameters.get("freshness_column") or ""
                )
                freshness_column = widgets.Dropdown(
                    options=[("Select timestamp column", ""), *temporal_column_names],
                    value=(
                        configured_freshness_column
                        if configured_freshness_column in temporal_column_names
                        else ""
                    ),
                    disabled=not editable or not temporal_column_names,
                    **shared.widget_common(widgets, "Timestamp column"),
                )
                freshness_column.layout = field_layout
                expected_refresh_frequency = widgets.Text(
                    value=str(existing_parameters.get("expected_refresh_frequency") or ""),
                    disabled=not editable or not temporal_column_names,
                    layout=widgets.Layout(width="150px", min_width="100px"),
                )
                expected_refresh_unit = widgets.Dropdown(
                    options=("minutes", "hours", "days"),
                    value=str(existing_parameters.get("expected_refresh_unit") or "days"),
                    disabled=not editable or not temporal_column_names,
                    layout=widgets.Layout(width="150px", min_width="120px"),
                )
                maximum_age = widgets.Text(
                    value=str(existing_parameters.get("maximum_age") or ""),
                    disabled=not editable or not temporal_column_names,
                    layout=widgets.Layout(width="150px", min_width="100px"),
                )
                maximum_age_unit = widgets.Dropdown(
                    options=("minutes", "hours", "days"),
                    value=str(existing_parameters.get("maximum_age_unit") or "days"),
                    disabled=not editable or not temporal_column_names,
                    layout=widgets.Layout(width="150px", min_width="120px"),
                )
                freshness_grid = widgets.GridBox(
                    [
                        widgets.HTML("<div style='padding-top:7px;'>Refresh expectation</div>"),
                        refresh_expectation,
                        widgets.HTML(""),
                        widgets.HTML("<div style='padding-top:7px;'>Timestamp column</div>"),
                        freshness_column,
                        widgets.HTML(""),
                        widgets.HTML("<div style='padding-top:7px;'>Expected refresh</div>"),
                        expected_refresh_frequency,
                        expected_refresh_unit,
                        widgets.HTML("<div style='padding-top:7px;'>Maximum age</div>"),
                        maximum_age,
                        maximum_age_unit,
                    ],
                    layout=widgets.Layout(
                        width="100%",
                        grid_template_columns="180px minmax(180px, 1fr) 180px",
                        grid_gap="8px 10px",
                        align_items="flex-start",
                    ),
                )
                freshness_rule_preview = widgets.HTML()
                freshness_unavailable = widgets.HTML()

                def refresh_freshness_rule_preview(
                    _change: dict[str, Any] | None = None,
                    *,
                    enabled_control: Any = enabled,
                    block_control: Any = block,
                ) -> None:
                    static_source = str(refresh_expectation.value or "") == "static"
                    freshness_column.disabled = not editable or static_source or not temporal_column_names
                    expected_refresh_frequency.disabled = not editable or static_source or not temporal_column_names
                    expected_refresh_unit.disabled = not editable or static_source or not temporal_column_names
                    maximum_age.disabled = not editable or static_source or not temporal_column_names
                    maximum_age_unit.disabled = not editable or static_source or not temporal_column_names
                    enabled_control.disabled = not editable
                    block_control.disabled = not editable or static_source
                    if static_source:
                        freshness_unavailable.value = ""
                        freshness_rule_preview.value = (
                            "<div style='background:#f6f8fa;border-left:3px solid #0f6cbd;"
                            "padding:9px 11px;margin-top:8px;font-size:12px;line-height:1.5;'>"
                            "<b>ⓘ Source expectation</b><br>"
                            "No refresh is expected for this source. Freshness age checks are skipped."
                            "<br><span style='color:#667085;'>Use Source Drift separately if an unexpected "
                            "change to this static source should be detected.</span></div>"
                        )
                        return
                    if not temporal_column_names:
                        freshness_unavailable.value = (
                            "<div style='color:#b42318;font-size:12px;font-weight:600;"
                            "margin:4px 0 8px;'>No date or datetime columns are available. "
                            "Recurring freshness cannot be configured for this table.</div>"
                        )
                        freshness_rule_preview.value = ""
                        return
                    freshness_unavailable.value = ""
                    selected = str(freshness_column.value or "").strip()
                    raw_expected = str(expected_refresh_frequency.value or "").strip()
                    expected_unit = str(expected_refresh_unit.value or "days")
                    raw_age = str(maximum_age.value or "").strip()
                    unit = str(maximum_age_unit.value or "days")
                    if not enabled.value or not selected or not raw_expected or not raw_age:
                        freshness_rule_preview.value = ""
                        return
                    try:
                        expected = float(raw_expected)
                        age = float(raw_age)
                    except ValueError:
                        freshness_rule_preview.value = ""
                        return
                    if expected <= 0 or age <= 0:
                        freshness_rule_preview.value = ""
                        return
                    shown_age = str(int(age)) if age.is_integer() else str(age)
                    sample_run = datetime(2026, 1, 2, 23, 0)
                    if unit == "minutes":
                        cutoff = sample_run - timedelta(minutes=age)
                    elif unit == "hours":
                        cutoff = sample_run - timedelta(hours=age)
                    else:
                        cutoff = sample_run - timedelta(days=age)
                    freshness_rule_preview.value = (
                        "<div style='background:#f6f8fa;border-left:3px solid #0f6cbd;"
                        "padding:9px 11px;margin-top:8px;font-size:12px;line-height:1.5;'>"
                        "<b>ⓘ Rule</b><br>"
                        f"Expected source refresh: <b>{html.escape(str(int(expected)) if expected.is_integer() else str(expected))} "
                        f"{html.escape(expected_unit)}</b>.<br>"
                        f"The latest <code>{html.escape(selected)}</code> must be within "
                        f"<b>{html.escape(shown_age)} {html.escape(unit)}</b> of the pipeline run."
                        "<br><span style='color:#667085;'>Example: if the pipeline runs at "
                        "2 Jan 2026 23:00, "
                        f"<code>MAX({html.escape(selected)})</code> must be on or after "
                        f"{cutoff.day} {cutoff.strftime('%b %Y %H:%M')}.</span></div>"
                    )

                for freshness_control in (
                    enabled, refresh_expectation, freshness_column,
                    expected_refresh_frequency, expected_refresh_unit,
                    maximum_age, maximum_age_unit
                ):
                    freshness_control.observe(refresh_freshness_rule_preview, names="value")
                refresh_freshness_rule_preview()
                parameter_controls = [
                    refresh_expectation,
                    freshness_column,
                    expected_refresh_frequency,
                    expected_refresh_unit,
                    maximum_age,
                    maximum_age_unit,
                ]
                display_controls = [
                    freshness_unavailable,
                    freshness_grid,
                    freshness_rule_preview,
                ]
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
                    **shared.widget_common(widgets, "Change tracking column"),
                )
                change_column.layout = field_layout
                source_drift_rule_preview = widgets.HTML()

                def refresh_source_drift_rule_preview(
                    _change: dict[str, Any] | None = None,
                    *,
                    enabled_control: Any = enabled,
                ) -> None:
                    partition = str(partition_column.value or "").strip()
                    change = str(change_column.value or "").strip()
                    if not enabled_control.value or not partition or not change:
                        source_drift_rule_preview.value = ""
                        return
                    source_drift_rule_preview.value = (
                        "<div style='background:#f6f8fa;border-left:3px solid #0f6cbd;"
                        "padding:9px 11px;margin-top:8px;font-size:12px;line-height:1.5;'>"
                        "<b>ⓘ Rule</b><br>"
                        "When this table is consumed as a source, FabricOps compares each "
                        f"<code>{html.escape(partition)}</code> partition with the last "
                        "successfully consumed state for that downstream target. "
                        "Changes are detected from row count, "
                        f"<code>{html.escape(change)}</code> values, and a content fingerprint."
                        "<br><span style='color:#667085;'>Example: if a previously consumed "
                        f"<code>{html.escape(partition)}</code> partition is different when read "
                        "again today, Source Drift is detected.</span></div>"
                    )

                for source_drift_control in (enabled, partition_column, change_column):
                    source_drift_control.observe(
                        refresh_source_drift_rule_preview, names="value"
                    )
                refresh_source_drift_rule_preview()
                source_drift_grid = widgets.GridBox(
                    [
                        widgets.HTML("<div style='padding-top:7px;'>Partition column</div>"),
                        partition_column,
                        widgets.HTML("<div style='padding-top:7px;'>Change tracking column</div>"),
                        change_column,
                    ],
                    layout=widgets.Layout(
                        width="100%",
                        grid_template_columns="180px minmax(180px, 1fr)",
                        grid_gap="8px 10px",
                        align_items="flex-start",
                    ),
                )
                parameter_controls = [partition_column, change_column]
                display_controls = [
                    source_drift_grid,
                    source_drift_rule_preview,
                ]

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
                    expectation = str(controls[0].value or "recurring")
                    if expectation == "static":
                        parameters = {"refresh_expectation": "static"}
                    else:
                        if not temporal_column_names:
                            raise ValueError(
                                "Recurring Freshness requires at least one date or datetime column."
                            )
                        raw_expected = str(controls[2].value or "").strip()
                        raw_age = str(controls[4].value or "").strip()
                        parameters = {
                            "refresh_expectation": "recurring",
                            "freshness_column": str(controls[1].value or "").strip(),
                            "expected_refresh_frequency": float(raw_expected),
                            "expected_refresh_unit": str(controls[3].value or "days"),
                            "maximum_age": float(raw_age),
                            "maximum_age_unit": str(controls[5].value or "days"),
                        }
                else:
                    parameters = {
                        "partition_column": str(controls[0].value or "").strip(),
                        "change_column": str(controls[1].value or "").strip(),
                    }
                if enabled_control.value and any(value in {"", None} for value in parameters.values()):
                    raise ValueError(f"{rule_title} requires all governed configuration fields.")
                return guardrail_record(
                    rule_kind,
                    "skip" if rule_kind == "freshness" and parameters.get("refresh_expectation") == "static"
                    else rule_kind,
                    parameters,
                    existing=old,
                    action="Block" if block_control.value else "Warn",
                    active=enabled_control.value,
                )

            table_rules[kind] = {
                "enabled": enabled, "parameters": parameter_controls,
                "display": display_controls,
                "block": block, "build_record": build_table_rule_record,
            }
        def sync_table_enrichment(_change: dict[str, Any] | None = None) -> None:
            if not editable:
                return
            try:
                stage_enrichment([
                    enrichment_record("table", "Description", table_description.value),
                    enrichment_record("table", "Classification", table_classification.value),
                    enrichment_record("table", "Grain", table_grain.value),
                ])
                set_validation_error("table.enrichment")
                render_table_summary()
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error("table.enrichment", exc)

        def sync_row_key(_change: dict[str, Any] | None = None) -> None:
            if not editable:
                return
            try:
                selected_keys = [str(name) for name in row_key_columns.value]
                if existing_row_key or selected_keys:
                    stage_guardrails([guardrail_record(
                        "data_quality", "uniqueness",
                        {"columns": selected_keys or existing_row_key_columns},
                        existing=existing_row_key,
                        action="Block" if row_key_block.value else "Warn",
                        active=bool(selected_keys),
                    )])
                set_validation_error("table.row_key")
                render_table_summary()
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error("table.row_key", exc)

        def sync_table_processing(_change: dict[str, Any] | None = None) -> None:
            if not editable:
                return
            try:
                stage_processing(build_processing())
                set_validation_error("table.processing")
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error("table.processing", exc)

        def sync_table_rule(
            rule_kind: str, _change: dict[str, Any] | None = None,
        ) -> None:
            if not editable:
                return
            try:
                record = table_rules[rule_kind]["build_record"]()
                if record is not None:
                    stage_guardrails([record])
                set_validation_error(f"table.{rule_kind}")
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error(f"table.{rule_kind}", exc)

        for control in (table_description, table_classification, table_grain):
            control.observe(sync_table_enrichment, names="value")
        row_key_columns.observe(sync_row_key, names="value")

        def prepare_data_contract_save() -> None:
            """Persist the currently displayed row-key choice when final Save is deliberate."""
            sync_row_key()

        state["_prepare_data_contract_save"] = prepare_data_contract_save
        row_key_block.observe(sync_row_key, names="value")
        for control in (load_strategy_control, *processing_parameter_controls):
            control.observe(sync_table_processing, names="value")
        for rule_kind, rule_controls in table_rules.items():
            rule_controls["enabled"].observe(
                lambda change, kind=rule_kind: sync_table_rule(kind, change), names="value"
            )
            rule_controls["block"].observe(
                lambda change, kind=rule_kind: sync_table_rule(kind, change), names="value"
            )
            for control in rule_controls["parameters"]:
                control.observe(
                    lambda change, kind=rule_kind: sync_table_rule(kind, change), names="value"
                )

        schedule_status = str(scheduled_refresh.get("status") or "unavailable")
        if schedule_status == "configured" and scheduled_refresh.get("schedules"):
            refresh_lines = []
            for schedule in scheduled_refresh["schedules"]:
                frequency = str(schedule.get("frequency") or "Scheduled").replace("_", " ").title()
                times = ", ".join(str(value) for value in schedule.get("times") or [])
                timezone = str(schedule.get("timezone") or "UTC")
                schedule_state = "" if schedule.get("enabled", True) else " · Disabled"
                parts = [frequency]
                if times:
                    parts.append(times)
                parts.append(timezone)
                refresh_lines.append(" · ".join(parts) + schedule_state)
            refresh_frequency = "<br>".join(html.escape(line) for line in refresh_lines)
        elif schedule_status == "not_configured":
            refresh_frequency = "Not configured"
        elif schedule_status == "uncaptured":
            refresh_frequency = "Not captured"
        else:
            refresh_frequency = "Unavailable"

        runtime_context = contracts.get_table_runtime_context(
            config=config, env=env, spark_session=spark,
            table_id=str(state.get("table_id") or ""),
        )

        def context_timestamp(value: Any) -> str:
            if isinstance(value, datetime):
                return value.strftime("%d %b %Y, %H:%M")
            text = str(value or "").strip()
            if not text:
                return "Unknown"
            try:
                parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
                return parsed.strftime("%d %b %Y, %H:%M")
            except ValueError:
                return text

        def runtime_context_html() -> str:
            profile = runtime_context.get("latest_profile")
            if profile:
                environment_name = str(profile.get("environment_name") or "Unknown environment")
                pipeline_name = str(profile.get("pipeline_name") or "Unknown pipeline")
                committed_by = str(profile.get("committed_by") or "Unknown")
                profile_html = (
                    "<div style='margin-top:14px;'>"
                    "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Latest profile</div>"
                    f"<div style='font-weight:600;margin-top:3px;'>{html.escape(environment_name)} · "
                    f"{html.escape(pipeline_name)}</div>"
                    f"<div style='color:#667085;font-size:12px;margin-top:2px;'>{html.escape(committed_by)} · "
                    f"{html.escape(context_timestamp(profile.get('committed_at')))}</div></div>"
                )
            else:
                profile_html = (
                    "<div style='margin-top:14px;'>"
                    "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Latest profile</div>"
                    "<div style='color:#667085;font-size:12px;margin-top:3px;'>No profile available</div></div>"
                )

            writer_count = int(runtime_context.get("writer_count") or 0)
            reader_count = int(runtime_context.get("reader_count") or 0)
            writer_label = "write" if writer_count == 1 else "writes"
            reader_label = "read" if reader_count == 1 else "reads"
            lineage_rows = list(runtime_context.get("lineage") or [])
            if lineage_rows:
                rows_html = "".join(
                    "<tr>"
                    f"<td style='padding:5px 8px;'>{html.escape(str(item.get('environment_name') or ''))}</td>"
                    f"<td style='padding:5px 8px;'>{html.escape(str(item.get('pipeline_name') or ''))}</td>"
                    f"<td style='padding:5px 8px;'>{html.escape(('Read' if str(item.get('relationship') or '').lower() in {'reader', 'read'} else 'Write' if str(item.get('relationship') or '').lower() in {'writer', 'write'} else str(item.get('relationship') or '')))}</td>"
                    f"<td style='padding:5px 8px;white-space:nowrap;'>{html.escape(context_timestamp(item.get('last_seen')))}</td>"
                    "</tr>"
                    for item in lineage_rows
                )
                detail_html = (
                    "<details style='margin-top:5px;'>"
                    "<summary style='cursor:pointer;color:#0f6cbd;font-size:12px;'>View lineage</summary>"
                    "<div style='overflow-x:auto;margin-top:6px;'>"
                    "<table style='border-collapse:collapse;width:100%;font-size:11px;'>"
                    "<thead><tr><th style='text-align:left;padding:5px 8px;'>Env</th>"
                    "<th style='text-align:left;padding:5px 8px;'>Pipeline</th>"
                    "<th style='text-align:left;padding:5px 8px;'>Role</th>"
                    "<th style='text-align:left;padding:5px 8px;'>Last seen</th></tr></thead>"
                    f"<tbody>{rows_html}</tbody></table></div></details>"
                )
            else:
                detail_html = "<div style='color:#667085;font-size:12px;margin-top:3px;'>No lineage recorded</div>"
            return (
                profile_html
                + "<div style='margin-top:14px;'>"
                "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Pipeline usage</div>"
                f"<div style='font-weight:600;margin-top:3px;'>{writer_count} {writer_label} · "
                f"{reader_count} {reader_label}</div>"
                + detail_html
                + "</div>"
            )

        table_summary = widgets.HTML()
        table_left = (table_summary, table_exit_row, table_exit_confirm)

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
            freshness_controls = table_rules["freshness"]
            source_refresh_expectation = "Not defined"
            if freshness_controls["enabled"].value:
                freshness_parameters = freshness_controls["parameters"]
                expectation_mode = str(freshness_parameters[0].value or "recurring")
                if expectation_mode == "static":
                    source_refresh_expectation = "No refresh expected"
                else:
                    frequency = str(freshness_parameters[2].value or "").strip()
                    unit = str(freshness_parameters[3].value or "").strip()
                    if frequency and unit:
                        try:
                            numeric_frequency = float(frequency)
                            shown_frequency = (
                                str(int(numeric_frequency))
                                if numeric_frequency.is_integer()
                                else str(numeric_frequency)
                            )
                        except ValueError:
                            shown_frequency = frequency
                        source_refresh_expectation = f"{shown_frequency} {unit}"

            guardrail_html = "".join(
                "<div style='display:flex;justify-content:space-between;gap:12px;padding:3px 0'>"
                f"<span style='color:#666'>{html.escape(name)}</span>"
                f"<span style='font-size:12px;{'color:#0f6cbd;' if enabled else ''}'>{'Enabled' if enabled else 'Disabled'}</span></div>"
                for name, enabled in statuses.items()
            )
            table_summary.value = (
                "<div style='color:#0f6cbd;font-size:11px;font-weight:800;"
                "text-transform:uppercase;letter-spacing:.07em;'>Table</div>"
                f"<div style='color:#172b4d;font-size:18px;font-weight:700;margin-top:6px;'>"
                f"{html.escape(str(table.get('table_name') or state.get('table_id') or ''))}</div>"
                f"<div style='color:#667085;font-size:12px;margin-top:2px;'>"
                f"{html.escape(str(table.get('schema_name') or ''))}</div>"
                f"<div style='color:#667085;font-size:12px;margin-top:5px;'>v{row['contract_version']} · "
                f"{html.escape(str(row.get('status') or '').upper())}</div>"
                + runtime_context_html()
                + "<div style='border-top:1px solid #e6eaef;margin:14px 0;'></div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Grain</div>"
                f"<div style='font-weight:600;'>{html.escape(str(table_grain.value or 'Not defined'))}</div></div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Classification</div>"
                f"<div style='font-weight:600;'>{html.escape(str(table_classification.value or 'Not classified'))}</div></div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Row Key</div>"
                f"<div style='font-weight:600;'>{html.escape(', '.join(row_key_columns.value) or 'Not defined')}</div></div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Load strategy</div>"
                f"<div style='font-weight:600;'>{html.escape(str(load_strategy_control.value or 'Not configured').upper())}</div></div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Scheduled refresh</div>"
                f"<div style='font-weight:600;line-height:1.5;'>{refresh_frequency}</div></div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Expected source refresh</div>"
                f"<div style='font-weight:600;'>{html.escape(source_refresh_expectation)}</div></div>"
                "<div style='margin-top:12px;'>"
                "<div style='color:#667085;font-size:11px;text-transform:uppercase;'>Guardrails</div>"
                + guardrail_html + "</div>"
            )

        table_grain.observe(render_table_summary, names="value")
        row_key_columns.observe(render_table_summary, names="value")
        table_classification.observe(render_table_summary, names="value")
        load_strategy_control.observe(render_table_summary, names="value")
        for rule_controls in table_rules.values():
            rule_controls["enabled"].observe(render_table_summary, names="value")
        for freshness_control in table_rules["freshness"]["parameters"]:
            freshness_control.observe(render_table_summary, names="value")
        processing_hint_row = widgets.HBox(
            [
                widgets.HTML("", layout=widgets.Layout(width="150px", min_width="150px")),
                processing_source_hint,
            ],
            layout=widgets.Layout(width="100%", gap="12px", align_items="flex-start"),
        )
        def definition_section(
            title: str,
            classification: Any,
            description: Any,
            suggestion: Any,
            accept_button: Any,
            rerun_button: Any,
        ) -> Any:
            primary = widgets.VBox(
                [
                    widgets.HTML("<b>Classification</b>"),
                    classification,
                    widgets.HTML("<b>Description</b>"),
                    description,
                ],
                layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
            )
            if ai_visible:
                assistant = widgets.VBox(
                    [
                        widgets.HTML("<b>AI suggestion</b>"),
                        suggestion,
                        shared.action_row(widgets, [accept_button, rerun_button]),
                    ],
                    layout=widgets.Layout(
                        width="100%", min_width="0", gap="8px",
                        padding="0 0 0 16px",
                        border_left="1px solid #e1e6eb",
                    ),
                )
                content = widgets.GridBox(
                    [primary, assistant],
                    layout=widgets.Layout(
                        width="100%",
                        grid_template_columns="minmax(0, 68fr) minmax(240px, 32fr)",
                        grid_gap="16px",
                        align_items="flex-start",
                    ),
                )
            else:
                content = primary
            return shared.form_section(widgets, title=title, children=[content])

        def guardrail_section(
            title: str,
            *,
            banner_title: str,
            banner_detail: str,
            description: str,
            primary_children: list[Any],
            ai_children: list[Any] | None = None,
        ) -> Any:
            """Render every Guardrail with one consistent primary/assistant layout."""
            banner = widgets.HTML(
                "<div style='background:#f6f8fa;border-left:3px solid #0f6cbd;"
                "padding:8px 10px;margin-bottom:8px;font-size:12px;line-height:1.5;'>"
                f"<b>{html.escape(banner_title)}</b>"
                f"<br><span style='color:#667085;'>{html.escape(banner_detail)}</span></div>"
            )
            primary = widgets.VBox(
                [
                    banner,
                    widgets.HTML(
                        "<div style='color:#667085;font-size:12px;line-height:1.5;"
                        "margin-bottom:4px;'>"
                        + html.escape(description)
                        + "</div>"
                    ),
                    *primary_children,
                ],
                layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
            )
            if ai_visible:
                assistant = widgets.VBox(
                    list(ai_children or []),
                    layout=widgets.Layout(
                        width="100%", min_width="0", gap="8px",
                        padding="0 0 0 16px",
                        border_left="1px solid #e1e6eb",
                    ),
                )
                content = widgets.GridBox(
                    [primary, assistant],
                    layout=widgets.Layout(
                        width="100%",
                        grid_template_columns="minmax(0, 68fr) minmax(240px, 32fr)",
                        grid_gap="16px",
                        align_items="flex-start",
                    ),
                )
            else:
                content = primary
            return shared.form_section(widgets, title=title, children=[content])

        table_definition = definition_section(
            "Table definition", table_classification, table_description,
            table_description_ai, accept_table_description, rerun_table_description,
        )
        grain_definition = shared.form_section(
            widgets,
            title="Grain & Row Key",
                children=[
                    widgets.GridBox(
                        [
                            widgets.VBox(
                                [
                                    widgets.HTML(
                                        "<div style='color:#667085;font-size:12px;line-height:1.5;"
                                        "margin-bottom:4px;'>Define what one row represents, then "
                                        "select the column or smallest column combination that should "
                                        "uniquely identify that row. The selected key automatically "
                                        "becomes the table-level uniqueness guardrail.</div>"
                                    ),
                                    table_grain,
                                    row_key_columns,
                                    grain_profile_evidence,
                                    row_key_block,
                                ],
                                layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
                            ),
                            *(
                                [
                                    widgets.VBox(
                                        [
                                            widgets.HTML("<b>AI suggestion</b>"),
                                            grain_ai,
                                            shared.action_row(
                                                widgets, [suggest_grain, accept_grain]
                                            ),
                                        ],
                                        layout=widgets.Layout(
                                            width="100%", min_width="0", gap="8px",
                                            padding="0 0 0 16px",
                                            border_left="1px solid #e1e6eb",
                                        ),
                                    )
                                ]
                                if ai_visible else []
                            ),
                        ],
                        layout=widgets.Layout(
                            width="100%",
                            grid_template_columns=(
                                "minmax(0, 68fr) minmax(240px, 32fr)"
                                if ai_visible else "minmax(0, 1fr)"
                            ),
                            grid_gap="16px",
                            align_items="flex-start",
                        ),
                    ),
                ],
            )
        table_right = (
            grain_definition,
            table_definition,
            shared.form_section(
                widgets,
                title="Processing",
                children=[
                    load_strategy_control,
                    processing_hint_row,
                    *processing_parameter_controls,
                ],
            ),
            guardrail_section(
                "Freshness",
                banner_title="Applies when this table is used as a source in a downstream pipeline.",
                banner_detail=(
                    "This rule is checked when the table is consumed as an input, "
                    "not when this table itself is written."
                ),
                description=(
                    "Check whether the source has received sufficiently recent data. "
                    "Freshness uses the latest value in the selected timestamp column "
                    "relative to the pipeline run time."
                ),
                primary_children=[
                    widgets.GridBox(
                        [table_rules["freshness"]["enabled"], table_rules["freshness"]["block"]],
                        layout=widgets.Layout(
                            width="100%",
                            grid_template_columns="repeat(2, minmax(160px, max-content))",
                            grid_gap="8px 20px",
                            align_items="center",
                        ),
                    ),
                    *table_rules["freshness"]["display"],
                ],
            ),
            guardrail_section(
                "Source Drift",
                banner_title="Applies when this table is used as a source in a downstream pipeline.",
                banner_detail=(
                    "This rule is checked when the table is consumed as an input, "
                    "not when this table itself is written."
                ),
                description=(
                    "Check whether data that was previously consumed from this table has "
                    "changed when the same source data is read again."
                ),
                primary_children=[
                    widgets.GridBox(
                        [table_rules["source_drift"]["enabled"], table_rules["source_drift"]["block"]],
                        layout=widgets.Layout(
                            width="100%",
                            grid_template_columns="repeat(2, minmax(160px, max-content))",
                            grid_gap="8px 20px",
                            align_items="center",
                        ),
                    ),
                    *table_rules["source_drift"]["display"],
                ],
            ),
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
            layout=widgets.Layout(width="100%", min_width="0", max_width="100%"),
        )
        column_select = widgets.Select(
            options=(),
            rows=8,
            layout=widgets.Layout(width="100%", min_width="0", max_width="100%", height="250px"),
        )
        column_select.add_class("fabricops-contract-columns")
        column_context = widgets.HTML()
        profile_context = shared.preview_region(widgets, widgets.HTML("<p>No column selected.</p>"), height="160px")
        column_description = widgets.Textarea(disabled=not editable, **shared.widget_common(widgets, "Description", textarea=True))
        column_classification = widgets.Dropdown(options=_CLASSIFICATIONS, disabled=not editable, **shared.widget_common(widgets, "Classification"))
        column_description.description = ""
        column_description.layout = widgets.Layout(width="100%", min_width="0", height="110px")
        column_classification.description = ""
        column_classification.layout = widgets.Layout(width="250px", max_width="100%", min_width="0")
        column_description_ai = widgets.HTML()
        accept_column_description = widgets.Button(description="Apply", disabled=not editable)
        rerun_column_description = widgets.Button(description="Re-run", disabled=not editable)
        required = widgets.Checkbox(description="Required", disabled=not editable)
        column_header = widgets.VBox(
            [column_context, required],
            layout=widgets.Layout(
                width="100%", min_width="0", gap="4px", align_items="flex-start",
            ),
        )
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
        sensitive_rule_preview = widgets.HTML()
        mask_start = widgets.Text(value="0", disabled=not editable, **shared.widget_common(widgets, "Mask: preserve start"))
        mask_end = widgets.Text(value="0", disabled=not editable, **shared.widget_common(widgets, "Mask: preserve end"))
        mask_character = widgets.Text(value="*", disabled=not editable, **shared.widget_common(widgets, "Mask character"))
        bucket_bins = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Bucket boundaries (comma-separated)"))
        bucket_labels = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Bucket labels (comma-separated)"))
        dq_type = widgets.ToggleButtons(
            options=[
                ("Completeness", "completeness"),
                ("Allowed Values", "value_set"),
                ("Value Rules", "range"),
                ("Pattern", "pattern"),
            ],
            disabled=not editable,
            layout=widgets.Layout(width="100%"),
        )
        dq_catalogue = widgets.HTML(
            "<div style='display:grid;grid-template-columns:repeat(4,minmax(135px,1fr));"
            "gap:8px;margin-bottom:10px;'>"
            "<div style='border:1px solid #dfe3e8;border-radius:6px;padding:9px 10px;'>"
            "<b>Completeness</b><br><span style='color:#667085;font-size:12px;'>"
            "How much of the column must be populated.</span></div>"
            "<div style='border:1px solid #dfe3e8;border-radius:6px;padding:9px 10px;'>"
            "<b>Allowed Values</b><br><span style='color:#667085;font-size:12px;'>"
            "Which values are accepted or blocked.</span></div>"
            "<div style='border:1px solid #dfe3e8;border-radius:6px;padding:9px 10px;'>"
            "<b>Value Rules</b><br><span style='color:#667085;font-size:12px;'>"
            "Numeric or date conditions such as above, below, or between.</span></div>"
            "<div style='border:1px solid #dfe3e8;border-radius:6px;padding:9px 10px;'>"
            "<b>Pattern</b><br><span style='color:#667085;font-size:12px;'>"
            "Text structure enforced with a regular expression.</span></div>"
            "</div>"
        )
        dq_help = widgets.HTML()
        dq_max_missing = widgets.Text(value="0", disabled=not editable, **shared.widget_common(widgets, "Maximum missing %"))
        dq_blank_missing = widgets.Checkbox(value=False, description="Treat blank/whitespace text as missing", disabled=not editable)
        dq_value_mode = widgets.Dropdown(options=("allow", "block"), disabled=not editable, **shared.widget_common(widgets, "Mode"))
        dq_values = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Allowed values (comma-separated)"))
        dq_minimum = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Lower bound"))
        dq_minimum_inclusive = widgets.Checkbox(value=True, description="Include lower bound", disabled=not editable)
        dq_maximum = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Upper bound"))
        dq_maximum_inclusive = widgets.Checkbox(value=True, description="Include upper bound", disabled=not editable)
        dq_pattern = widgets.Text(disabled=not editable, **shared.widget_common(widgets, "Regular expression"))
        dq_parameter_controls = (
            dq_max_missing, dq_blank_missing, dq_value_mode, dq_values, dq_minimum,
            dq_minimum_inclusive, dq_maximum, dq_maximum_inclusive, dq_pattern,
        )
        dq_enabled = widgets.Checkbox(description="Enabled", disabled=not editable)
        dq_block = widgets.Checkbox(description="Block on failure", disabled=not editable)
        dq_usage = widgets.HTML()
        sensitive_ai = widgets.HTML()
        accept_sensitive = widgets.Button(description="Apply", disabled=not editable)
        rerun_sensitive = widgets.Button(description="Re-run", disabled=not editable)
        sensitive_ai_actions = shared.action_row(
            widgets, [accept_sensitive, rerun_sensitive]
        )
        dq_ai_instruction = widgets.Text(
            value="",
            disabled=True,
            placeholder="Example: Product IDs start with P followed by three digits",
            **shared.widget_common(widgets, "Pattern instruction"),
        )
        dq_ai_instruction.layout = widgets.Layout(width="100%", min_width="0")
        suggest_dq = widgets.Button(description="Suggest", disabled=True)
        dq_suggestion = widgets.Select(
            options=(), disabled=True, **shared.widget_common(widgets, "AI suggestions")
        )
        accept_dq_suggestion = widgets.Button(description="Apply", disabled=True)
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
        for classification in (table_classification, column_classification):
            classification.layout.width = "250px"
            classification.layout.max_width = "100%"
        draft_scope = (str(current["contract_id"]), int(current["contract_version"]))
        unsaved_columns: dict[str, dict[str, Any]] = state["_column_drafts"].setdefault(
            draft_scope, {}
        )
        selected_dq_by_column: dict[str, str] = state["_column_dq_selection"].setdefault(
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
                row for row in session_guardrails()
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
            try:
                live_enrichments, live_guardrails = current_rows()
                selected = next((c for c in columns if str(c.get("column_id") or "") == column_id), {})
                observed_type = str(selected.get("data_type") or "")
                contract_type = str(contracted_types.get(column_id) or observed_type)
                mismatch = bool(contract_type and observed_type and contract_type != observed_type)
                column_name = html.escape(str(selected.get("column_name") or ""))
                if mismatch:
                    column_context.value = (
                        "<div style='min-height:54px;'>"
                        f"<div style='color:#0f6cbd;font-size:20px;font-weight:700;'>{column_name}</div>"
                        "<div style='color:#a4262c;font-size:12px;font-weight:700;margin-top:3px;'>"
                        "Datatype drift detected</div>"
                        f"<div style='color:#667085;font-size:12px;margin-top:2px;'>"
                        f"Contract: <b>{html.escape(contract_type)}</b> · "
                        f"Observed: <b style='color:#a4262c'>{html.escape(observed_type)}</b></div>"
                        "</div>"
                    )
                    datatype_choice.options = (
                        (f"Keep contract · {contract_type}", contract_type),
                        (f"Accept observed · {observed_type}", observed_type),
                    )
                    datatype_choice.value = contract_type
                    datatype_choice.layout.display = ""
                else:
                    column_context.value = (
                        "<div style='min-height:54px;'>"
                        f"<div style='color:#0f6cbd;font-size:20px;font-weight:700;'>{column_name}</div>"
                        f"<div style='color:#667085;font-size:12px;margin-top:3px;'>"
                        f"{html.escape(contract_type or observed_type)}</div></div>"
                    )
                    datatype_choice.options = ((contract_type or observed_type, contract_type or observed_type),)
                    datatype_choice.value = contract_type or observed_type
                    datatype_choice.layout.display = "none"
                column_description.value = enrichment_value(live_enrichments, "column", "Description", column_id)
                column_classification.value = enrichment_value(live_enrichments, "column", "Classification", column_id)
                required.value = column_id in required_columns or selected.get("column_name") in required_columns
                sensitive = next((r for r in live_guardrails if str(r.get("guardrail_type") or "").lower() == "sensitive_data" and str(r.get("column_id") or "") == column_id), {})
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
                    str(rule.get("rule_type") or "") for rule in live_guardrails
                    if str(rule.get("guardrail_type") or "").lower() in {"data_quality", "dq"}
                    and str(rule.get("column_id") or "") == column_id
                    and str(rule.get("rule_type") or "") in _COLUMN_DQ_TYPES
                    and rule.get("is_active", True)
                ]
                preferred_dq = selected_dq_by_column.get(column_id)
                dq_type.value = (
                    preferred_dq
                    if preferred_dq in _COLUMN_DQ_TYPES
                    else configured[0] if configured else _COLUMN_DQ_TYPES[0]
                )
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
            finally:
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
            selected_id = str(column_select.value or "")
            if selected_id and not hydrating["active"]:
                selected_dq_by_column[selected_id] = kind
            count = sum(
                1 for rule in session_guardrails()
                if str(rule.get("rule_type") or "") == kind and rule.get("is_active", True)
            )
            dq_help.value = f"<p>{html.escape(_DQ_HELP[kind])}</p>"
            dq_usage.value = f"<p>{count} current configuration(s) use this rule type.</p>"
            visible = {
                "completeness": {dq_max_missing, dq_blank_missing},
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

        def refresh_sensitive_rule_preview(
            _change: dict[str, Any] | None = None,
        ) -> None:
            pii_value = str(pii_type.value or "none")
            if not sensitive_enabled.value or pii_value == "none":
                sensitive_rule_preview.value = ""
                return
            pii_label = PII_LABELS.get(pii_value, pii_value)
            treatment = str(sensitive_treatment.value or "")
            action = (
                "Block the pipeline run on failure."
                if sensitive_block.value
                else "Do not block the pipeline run on failure."
            )
            detail = ""
            if treatment == "mask":
                detail = (
                    f" Preserve {html.escape(str(mask_start.value or '0'))} character(s) at the start "
                    f"and {html.escape(str(mask_end.value or '0'))} at the end."
                )
            elif treatment == "bucket":
                bins = str(bucket_bins.value or "").strip()
                labels = str(bucket_labels.value or "").strip()
                if bins:
                    detail = f" Bucket boundaries: <code>{html.escape(bins)}</code>."
                if labels:
                    detail += f" Labels: <code>{html.escape(labels)}</code>."
            reason = str(pii_reason.value or "").strip()
            reason_line = (
                f"<br><span style='color:#667085;'>Reason: {html.escape(reason)}</span>"
                if reason else ""
            )
            sensitive_rule_preview.value = (
                "<div style='background:#f6f8fa;border-left:3px solid #0f6cbd;"
                "padding:9px 11px;margin-top:8px;font-size:12px;line-height:1.5;'>"
                "<b>ⓘ Rule</b><br>"
                f"This column is assessed as <b>{html.escape(pii_label)}</b>. "
                f"Treatment: <b>{html.escape(treatment)}</b>.{detail} {action}"
                f"{reason_line}</div>"
            )

        for sensitive_control in (
            sensitive_enabled, pii_type, pii_reason, sensitive_treatment, sensitive_block,
            mask_start, mask_end, mask_character, bucket_bins, bucket_labels,
        ):
            sensitive_control.observe(refresh_sensitive_rule_preview, names="value")

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
        refresh_sensitive_rule_preview()

        def column_changed(change: dict[str, Any]) -> None:
            old = str(change.get("old") or "")
            if old:
                snapshot = column_editor_snapshot()
                if snapshot != hydrated_column_snapshots.get(old, snapshot):
                    unsaved_columns[old] = snapshot
                    set_status("Column edits were retained in the current draft session.")
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

        def _suggestion_html(
            label: str, suggestion: dict[str, Any] | None, *, show_heading: bool = True
        ) -> str:
            heading = "<b>AI suggestion</b><br>" if show_heading else ""
            if not suggestion:
                return f"<p>{heading}<span style=\"color:#666\">Preparing…</span></p>"
            stale = " · <b>Needs refresh</b>" if suggestion.get("stale") else ""
            error = suggestion.get("error")
            if error:
                return (
                    f"<p>{heading}<span style=\"color:#a4262c\">"
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
            stale_text = stale if show_heading else ("<b>Needs refresh</b><br>" if stale else "")
            return f"<p>{heading}{stale_text}{value}</p>"

        def _column_editable_values(column_id: str) -> tuple[str, str]:
            if str(column_select.value or "") == column_id:
                return str(column_description.value or ""), str(column_classification.value or "")
            live_enrichments, _live_guardrails = current_rows()
            pending = unsaved_columns.get(column_id, {})
            return (
                str(pending.get("description", enrichment_value(
                    live_enrichments, "column", "Description", column_id
                )) or ""),
                str(pending.get("classification", enrichment_value(
                    live_enrichments, "column", "Classification", column_id
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
                column_description_ai.value = "<p>Disabled in 00_env_config.</p>"
                sensitive_ai.value = "<p><b>AI suggestion</b><br>Disabled in 00_env_config.</p>"
            elif not editable:
                column_description_ai.value = "<p>Not run for review-only versions.</p>"
                sensitive_ai.value = "<p><b>AI suggestion</b><br>Not run for review-only versions.</p>"
            elif ai_mode != "with_ai":
                message = (
                    "Skipped for this contract session."
                    if ai_mode == "without_ai"
                    else "Choose Run with AI suggestions on the Table tab."
                )
                column_description_ai.value = f"<p>{message}</p>"
                sensitive_ai.value = f"<p><b>AI suggestion</b><br>{message}</p>"
            else:
                column_description_ai.value = _suggestion_html(
                    "Description", suggestions.get("description"), show_heading=False
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
                    description_prompt=str(ai_enrichment.get("column_description_prompt") or ""),
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
                    selected_name = str(selected.get("column_name") or column_id)
                    raise ValueError(
                        f"No Sensitive Data assessment matched {selected_name!r}."
                    )
                suggestions["sensitive_data"] = {**result[0], "stale": False}
                ai_errors.pop((column_id, "sensitive_data"), None)
            except (TypeError, ValueError, RuntimeError) as exc:
                message = str(exc)
                suggestions["sensitive_data"] = {"error": message, "stale": False}
                ai_errors[(column_id, "sensitive_data")] = message
                selected_name = str(selected.get("column_name") or column_id)
                set_status(
                    f"Sensitive Data AI suggestion skipped for {selected_name}: {message}",
                    warning=True,
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

        def mark_column_hydrated(*keys: str) -> None:
            cid = str(column_select.value or "")
            if not cid:
                return
            current_snapshot = column_editor_snapshot()
            baseline = hydrated_column_snapshots.setdefault(cid, dict(current_snapshot))
            for key in keys:
                baseline[key] = current_snapshot[key]
            if baseline == current_snapshot:
                unsaved_columns.pop(cid, None)
            else:
                unsaved_columns[cid] = current_snapshot

        def sync_column_enrichment(_change: dict[str, Any] | None = None) -> None:
            if hydrating["active"] or not editable:
                return
            cid = str(column_select.value or "")
            if not cid:
                return
            key = f"column.{cid}.enrichment"
            try:
                stage_enrichment([
                    enrichment_record("column", "Description", column_description.value, cid),
                    enrichment_record("column", "Classification", column_classification.value, cid),
                ])
                set_validation_error(key)
                mark_column_hydrated("description", "classification")
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error(key, exc)

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

        def sync_required(_change: dict[str, Any] | None = None) -> None:
            if hydrating["active"] or not editable:
                return
            cid = str(column_select.value or "")
            if not cid:
                return
            key = f"column.{cid}.required"
            try:
                stage_guardrails([build_required_record()])
                set_validation_error(key)
                mark_column_hydrated("required")
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error(key, exc)

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

        def sync_sensitive(_change: dict[str, Any] | None = None) -> None:
            if hydrating["active"] or not editable:
                return
            cid = str(column_select.value or "")
            if not cid:
                return
            key = f"column.{cid}.sensitive"
            try:
                record = build_sensitive_record()
                if record is not None:
                    stage_guardrails([record])
                set_validation_error(key)
                mark_column_hydrated(
                    "sensitive_enabled", "pii_type", "pii_reason", "sensitive_treatment",
                    "sensitive_block", "mask_start", "mask_end", "mask_character",
                    "bucket_bins", "bucket_labels",
                )
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error(key, exc)

        def sync_dq(_change: dict[str, Any] | None = None) -> None:
            if hydrating["active"] or not editable:
                return
            cid = str(column_select.value or "")
            if not cid:
                return
            kind = str(dq_type.value)
            key = f"column.{cid}.dq.{kind}"
            try:
                selected = selected_column()
                existing = next((
                    r for r in session_guardrails()
                    if str(r.get("guardrail_type") or "").lower() in {"data_quality", "dq"}
                    and str(r.get("column_id") or "") == cid
                    and str(r.get("rule_type") or "") == kind
                ), {})
                if not existing and not dq_enabled.value:
                    set_validation_error(key)
                    mark_column_hydrated("dq_type", "dq_parameters", "dq_enabled", "dq_block")
                    return
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
                stage_guardrails([guardrail_record(
                    "data_quality", kind, params, column_id=cid,
                    action="Block" if dq_block.value else "Warn",
                    existing=existing, active=dq_enabled.value,
                )])
                set_validation_error(key)
                mark_column_hydrated("dq_type", "dq_parameters", "dq_enabled", "dq_block")
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error(key, exc)

        def suggest_dq_clicked(_button: Any) -> None:
            """Generate Pattern advice and hydrate controls only on apply."""
            try:
                requested_type = str(dq_type.value or "")
                if requested_type != "pattern":
                    raise ValueError("AI assistance is available only for Pattern.")
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
                user_instruction = str(dq_ai_instruction.value or "").strip()
                family_instruction = (
                    f"Suggest only one {requested_type} rule for the selected column. "
                    "Do not return any other Data Quality rule family."
                )
                if user_instruction:
                    family_instruction += (
                        "\nAdditional author instruction:\n" + user_instruction
                    )
                prompt_value = (
                    str(ai_enrichment.get("pattern_prompt") or "").strip()
                    + "\n\n"
                    + family_instruction
                )
                suggestions = [
                    item for item in suggest_dq_rules(
                        context_payload, prompt=prompt_value,
                    )
                    if str(item.get("rule_type") or "") == requested_type
                ]
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
                ) + "</ul><p>Select a suggestion and choose <b>Apply</b>. FabricOps copies only the canonical supported fields into the editor; you can still edit them before the final Data Contract save.</p>"
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

        for control in (column_description, column_classification):
            control.observe(sync_column_enrichment, names="value")
        required.observe(sync_required, names="value")
        for control in (
            sensitive_enabled, pii_type, pii_reason, sensitive_treatment, sensitive_block,
            mask_start, mask_end, mask_character, bucket_bins, bucket_labels,
        ):
            control.observe(sync_sensitive, names="value")
        for control in (dq_type, *dq_parameter_controls, dq_enabled, dq_block):
            control.observe(sync_dq, names="value")

        def refresh_dq_ai_controls(_change: dict[str, Any] | None = None) -> None:
            if _change and _change.get("old") != _change.get("new"):
                state["_ai_suggestions"][suggestion_scope].pop("dq", None)
                dq_suggestion.options = ()
                dq_suggestion.disabled = True
                accept_dq_suggestion.disabled = True
            supported = str(dq_type.value or "") == "pattern"
            available = bool(
                editable and ai_enrichment.get("enabled") and ai_mode == "with_ai"
            )
            enabled = supported and available
            dq_ai_instruction.disabled = not enabled
            suggest_dq.disabled = not enabled
            if supported:
                dq_ai_instruction.placeholder = (
                    "Optional: describe the text pattern you want FabricOps to translate "
                    "into a regular expression."
                )
                if not state["_ai_suggestions"][suggestion_scope].get("dq"):
                    dq_ai.value = (
                        "<p>Use AI to translate a human description into a Pattern rule, "
                        "then choose <b>Apply</b> and edit the regular expression if needed.</p>"
                    )
            else:
                state["_ai_suggestions"][suggestion_scope].pop("dq", None)
                dq_suggestion.options = ()
                dq_suggestion.disabled = True
                accept_dq_suggestion.disabled = True
                dq_ai.value = (
                    "<p>Completeness, Allowed Values, and Value Rules are configured directly; "
                    "AI assistance is reserved for Pattern.</p>"
                )

        suggest_dq.on_click(suggest_dq_clicked)
        accept_dq_suggestion.on_click(accept_dq_clicked)
        dq_type.observe(refresh_dq_ai_controls, names="value")
        refresh_dq_ai_controls()
        def rebuild_column_options() -> None:
            nonlocal column_options
            column_options = [
                (str(column.get("column_name") or ""), str(column.get("column_id") or ""))
                for column in columns
            ]
            column_option_style.value = (
                "<style>.fabricops-contract-columns option:checked{font-weight:600;}</style>"
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
                "Select a column to review its details and rules.</div>"
            ),
            column_search,
            column_option_style,
            column_select,
        )
        dq_primary = widgets.VBox(
            [
                dq_catalogue,
                dq_type,
                dq_help,
                widgets.HBox(
                    [dq_enabled, dq_block],
                    layout=checkbox_row_layout,
                ),
                *dq_parameter_controls,
            ],
            layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
        )
        dq_ai_panel = widgets.VBox(
            [
                widgets.HTML("<b>AI assistant</b>"),
                dq_ai_instruction,
                dq_suggestion,
                dq_ai,
                shared.action_row(widgets, [suggest_dq, accept_dq_suggestion]),
            ],
            layout=widgets.Layout(
                width="100%", min_width="0", gap="8px",
                padding="0 0 0 16px",
                border_left="1px solid #e1e6eb",
            ),
        )
        dq_panel = guardrail_section(
            "Column data quality",
            banner_title="Applies when this governed column is validated or enforced in a pipeline.",
            banner_detail=(
                "FabricOps evaluates active deterministic Data Quality rules before a governed "
                "write is allowed to continue."
            ),
            description=(
                "Choose the rule family that describes the column expectation, configure it, "
                "and review the resulting deterministic rule."
            ),
            primary_children=[dq_primary],
            ai_children=list(dq_ai_panel.children),
        )
        column_definition = definition_section(
            "Column definition", column_classification, column_description,
            column_description_ai, accept_column_description, rerun_column_description,
        )
        sensitive_primary = widgets.VBox(
            [
                pii_type,
                sensitive_treatment,
                mask_start,
                mask_end,
                mask_character,
                bucket_bins,
                bucket_labels,
                pii_reason,
                sensitive_rule_preview,
            ],
            layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
        )
        sensitive_ai_panel = widgets.VBox(
            [sensitive_ai, sensitive_ai_actions],
            layout=widgets.Layout(
                width="100%", min_width="0", gap="8px",
                padding="0 0 0 16px",
                border_left="1px solid #e1e6eb",
            ),
        )
        column_right = (
            column_header,
            datatype_choice,
            column_definition,
            shared.form_section(
                widgets,
                title="Profile evidence",
                children=[profile_context],
            ),
            guardrail_section(
                "Sensitive Data",
                banner_title="Applies before this governed table is written.",
                banner_detail=(
                    "FabricOps applies the selected deterministic treatment to this column "
                    "before the governed write proceeds."
                ),
                description=(
                    "Classify whether this column contains PII, record the reason, and choose "
                    "how the pipeline should treat the sensitive value."
                ),
                primary_children=[
                    widgets.HBox(
                        [sensitive_enabled, sensitive_block],
                        layout=checkbox_row_layout,
                    ),
                    sensitive_primary,
                ],
                ai_children=list(sensitive_ai_panel.children),
            ),
            dq_panel,
        )
        view_content["Columns"] = (column_left, column_right)

        if ai_mode == "with_ai":
            if not str(table_grain.value or "").strip():
                run_grain_ai()
            if not str(table_description.value or "").strip():
                run_table_ai()
            else:
                render_table_ai()
        else:
            render_table_ai()
        if column_options:
            column_select.value = column_options[0][1]
            hydrate_column(str(column_select.value))
            render_column_ai(str(column_select.value))
            if ai_mode == "with_ai":
                prepare_column_ai(str(column_select.value))

        # Business Rules: Governance states intent; FabricOps resolves deterministic Guardrails.
        business_saved = widgets.Select(
            **shared.widget_common(widgets, "Saved Business Rules")
        )
        business_requirement = widgets.Text(
            disabled=not editable,
            placeholder="Example: End date must be after start date",
            **shared.widget_common(widgets, "Business requirement"),
        )
        business_requirement.description = ""
        business_columns = widgets.SelectMultiple(
            options=[
                (str(column.get("column_name") or ""), str(column.get("column_name") or ""))
                for column in columns
            ],
            disabled=not editable,
            **shared.widget_common(widgets, "Relevant columns (optional)"),
        )
        business_columns.description = ""
        business_enabled = widgets.Checkbox(
            value=True, description="Enabled", disabled=not editable
        )
        business_block = widgets.Checkbox(
            description="Block on failure", disabled=not editable
        )
        business_rule_controls = widgets.HBox(
            [business_enabled, business_block],
            layout=checkbox_row_layout,
        )
        business_rule_controls.layout.display = "none"
        business_examples = widgets.HTML(
            "<div style='color:#667085;font-size:12px;line-height:1.6;'>"
            "<b>Examples</b><br>"
            "• End date must be after start date<br>"
            "• When status is Approved, approved date is required<br>"
            "• Total amount must equal quantity × unit price × (1 - discount)<br>"
            "• Either email or mobile number must be present"
            "</div>"
        )
        business_proposal = widgets.HTML(
            "<p style='color:#667085;'>Describe a rule, optionally select the relevant columns, "
            "then choose <b>Resolve rule</b>.</p>"
        )
        resolve_business_rule = widgets.Button(
            description="Resolve rule",
            disabled=not (
                editable and ai_enrichment.get("enabled") and ai_mode == "with_ai"
            ),
        )
        apply_business_rule = widgets.Button(description="Apply", disabled=True)
        engineering_reviewer = widgets.Text(
            disabled=not editable,
            placeholder="Engineer name or identifier",
            **shared.widget_common(widgets, "Engineering reviewer"),
        )
        engineering_review_note = widgets.Textarea(
            disabled=not editable,
            placeholder="Optional review note",
            **shared.widget_common(widgets, "Review note", textarea=True),
        )
        approve_engineering_review = widgets.Button(
            description="Approve engineering review", disabled=True
        )
        engineering_review_status = widgets.HTML()
        engineering_review_panel = widgets.VBox(
            [
                engineering_review_status,
                engineering_reviewer,
                engineering_review_note,
                approve_engineering_review,
            ],
            layout=widgets.Layout(
                width="100%", gap="8px", padding="10px 12px",
                border="1px solid #e1e6eb",
            ),
        )
        engineering_review_panel.layout.display = "none"
        business_lookup: dict[str, dict[str, Any]] = {}
        business_resolved: dict[str, Any] = {}
        business_hydrating = {"active": False}

        business_saved.layout.width = "100%"
        business_saved.layout.max_width = "760px"
        business_saved.layout.min_width = "0"
        business_saved.layout.height = "160px"
        business_requirement.layout.width = "100%"
        business_requirement.layout.min_width = "0"
        business_columns.layout.width = "100%"
        business_columns.layout.min_width = "0"
        business_columns.layout.height = "130px"
        engineering_review_note.layout.height = "80px"

        def business_rule_label(rule: Mapping[str, Any]) -> str:
            params = _parameters(rule)
            requirement = str(
                params.get("business_requirement")
                or params.get("description")
                or ""
            ).strip()
            if requirement:
                return requirement
            kind = str(rule.get("rule_type") or "")
            if kind == "column_relationship":
                names = list(params.get("columns") or [])
                if len(names) == 2:
                    return f"{names[0]} {params.get('operator') or '='} {names[1]}"
            return kind.replace("_", " ").title() or "Business Rule"

        def refresh_business_saved_options(selected: str | None = None) -> None:
            business_lookup.clear()
            options: list[tuple[str, str]] = [("New Business Rule", "")]
            for rule in session_guardrails():
                if str(rule.get("guardrail_type") or "").lower() not in {"data_quality", "dq"}:
                    continue
                if str(rule.get("column_id") or ""):
                    continue
                if str(rule.get("rule_type") or "") not in {
                    "completeness", "uniqueness", "value_set", "range", "pattern",
                    "column_relationship", "conditional_completeness",
                    "conditional_values", "custom_expression",
                }:
                    continue
                key = str(rule.get("guardrail_rule_id") or "")
                if not key:
                    continue
                business_lookup[key] = rule
                options.append((business_rule_label(rule), key))
            business_saved.options = options
            option_values = {str(value) for _label, value in options}
            business_saved.value = selected if selected in option_values else ""

        def engineering_review_state(rule: Mapping[str, Any]) -> tuple[bool, str]:
            if str(rule.get("rule_type") or "") != "custom_expression":
                return False, "not_required"
            params = _parameters(rule)
            required = bool(params.get("engineering_review_required", True))
            status = str(params.get("engineering_review_status") or "pending").lower()
            return required, status

        def render_engineering_review(rule: Mapping[str, Any] | None = None) -> None:
            current_rule = dict(rule or {})
            required, status = engineering_review_state(current_rule)
            engineering_review_panel.layout.display = "" if required else "none"
            if not required:
                engineering_review_status.value = ""
                approve_engineering_review.disabled = True
                return
            params = _parameters(current_rule)
            approved = status == "approved"
            reviewer = str(params.get("engineering_reviewed_by") or "")
            note = str(params.get("engineering_review_note") or "")
            engineering_reviewer.value = reviewer
            engineering_review_note.value = note
            if approved:
                engineering_review_status.value = (
                    "<div style='color:#107c10;font-weight:600;'>Engineering review approved"
                    + (f" by {html.escape(reviewer)}" if reviewer else "")
                    + ".</div>"
                )
            else:
                engineering_review_status.value = (
                    "<div style='color:#8a6d1d;font-weight:600;'>Engineering review pending.</div>"
                    "<div style='color:#667085;font-size:12px;margin-top:3px;'>"
                    "Review the resolved Custom Expression before approving it for freeze.</div>"
                )
            approve_engineering_review.disabled = not editable or approved

        def render_business_proposal(proposal: Mapping[str, Any] | None = None) -> None:
            if not proposal:
                business_rule_controls.layout.display = "none"
                business_proposal.value = (
                    "<p style='color:#667085;'>No Data Quality rule has been resolved yet.</p>"
                )
                return
            business_rule_controls.layout.display = ""
            rule_type = str(proposal.get("rule_type") or "")
            params = dict(proposal.get("parameters") or {})
            rationale = str(proposal.get("rationale") or "").strip()
            if rule_type == "custom_expression":
                expression = str(params.get("expression") or "")
                heading = "Custom Expression"
                review = (
                    "<span style='color:#8a6d1d;font-weight:600;'>"
                    "Engineering review required</span>"
                )
            else:
                names = list(params.get("columns") or [])
                if rule_type == "column_relationship" and len(names) == 2:
                    expression = (
                        f"{names[0]} {params.get('operator') or '='} {names[1]}"
                    )
                else:
                    expression = ", ".join(str(name) for name in names)
                heading = (
                    "Known FabricOps pattern: "
                    + rule_type.replace("_", " ").title()
                )
                review = (
                    "<span style='color:#107c10;font-weight:600;'>"
                    "No Engineering review required</span>"
                )
            rationale_html = (
                "<br><span style='color:#667085;'>" + html.escape(rationale) + "</span>"
                if rationale else ""
            )
            business_proposal.value = (
                "<div style='background:#f6f8fa;border-left:3px solid #0f6cbd;"
                "padding:10px 12px;font-size:12px;line-height:1.6;'>"
                f"<b>{html.escape(heading)}</b><br>"
                f"<code>{html.escape(expression)}</code><br>"
                f"{review}{rationale_html}</div>"
            )

        def hydrate_business_saved(change: dict[str, Any] | None = None) -> None:
            business_hydrating["active"] = True
            try:
                business_resolved.clear()
                apply_business_rule.disabled = True
                rule = business_lookup.get(str(business_saved.value or ""), {})
                params = _parameters(rule)
                requirement = str(
                    params.get("business_requirement")
                    or params.get("description")
                    or ""
                ).strip()
                if not requirement and rule:
                    requirement = business_rule_label(rule)
                business_requirement.value = requirement
                valid_columns = {value for _label, value in business_columns.options}
                selected_columns = [
                    str(name) for name in params.get("columns", [])
                    if str(name) in valid_columns
                ]
                business_columns.value = tuple(selected_columns)
                business_enabled.value = bool(
                    not rule or rule.get("is_active", True)
                )
                business_block.value = str(rule.get("action") or "Warn") == "Block"
                if rule:
                    render_business_proposal({
                        "rule_type": str(rule.get("rule_type") or ""),
                        "parameters": params,
                        "rationale": "Saved deterministic Guardrail.",
                    })
                    render_engineering_review(rule)
                else:
                    render_business_proposal()
                    render_engineering_review()
            finally:
                business_hydrating["active"] = False

        def invalidate_business_proposal(_change: dict[str, Any] | None = None) -> None:
            if business_hydrating["active"]:
                return
            business_resolved.clear()
            apply_business_rule.disabled = True
            render_business_proposal()

        def resolve_business_rule_clicked(_button: Any) -> None:
            try:
                context_payload = build_ai_business_rule_context({
                    "table_name": table.get("table_name"),
                    "schema_name": table.get("schema_name"),
                    "layer": table.get("layer"),
                    "table_description": _effective_table_ai_description(),
                    "table_classification": table_classification.value,
                    "columns": [
                        {
                            **column,
                            "description": _column_editable_values(
                                str(column.get("column_id") or "")
                            )[0],
                            "classification": _column_editable_values(
                                str(column.get("column_id") or "")
                            )[1],
                        }
                        for column in columns
                    ],
                })
                proposal = suggest_business_rule(
                    context_payload,
                    requirement=str(business_requirement.value or ""),
                    relevant_columns=list(business_columns.value),
                    prompt=str(ai_enrichment.get("business_rule_prompt") or ""),
                )
                business_resolved.clear()
                business_resolved.update(proposal)
                render_business_proposal(proposal)
                apply_business_rule.disabled = False
                set_validation_error("business_rule")
            except (TypeError, ValueError, RuntimeError) as exc:
                business_resolved.clear()
                apply_business_rule.disabled = True
                business_proposal.value = (
                    f"<p style='color:#a4262c'>{html.escape(str(exc))}</p>"
                )
                set_validation_error("business_rule", exc)

        def apply_business_rule_clicked(_button: Any) -> None:
            if not business_resolved:
                return
            try:
                existing = business_lookup.get(str(business_saved.value or ""), {})
                params = dict(business_resolved.get("parameters") or {})
                if str(business_resolved.get("rule_type") or "") == "custom_expression":
                    params.update({
                        "engineering_review_required": True,
                        "engineering_review_status": "pending",
                    })
                    params.pop("engineering_reviewed_by", None)
                    params.pop("engineering_review_note", None)
                resolved_type = str(business_resolved["rule_type"])
                resolved_columns = [str(value) for value in params.get("columns") or []]
                column_rule_id = ""
                if resolved_type == "uniqueness":
                    # Uniqueness is repeatable. Grain & Row Key is a separate, singular
                    # semantic declaration authored on the Table tab.
                    existing = {}
                elif resolved_type in _COLUMN_DQ_TYPES and len(resolved_columns) == 1:
                    column_rule_id = next((
                        str(column.get("column_id") or "")
                        for column in columns
                        if str(column.get("column_name") or "") == resolved_columns[0]
                    ), "")
                    if not column_rule_id:
                        raise ValueError(
                            "Resolved single-column Business Rule does not match a governed column."
                        )
                    existing = next((
                        rule for rule in session_guardrails()
                        if str(rule.get("guardrail_type") or "").lower() in {"data_quality", "dq"}
                        and str(rule.get("column_id") or "") == column_rule_id
                        and str(rule.get("rule_type") or "") == resolved_type
                    ), {})
                record = guardrail_record(
                    "data_quality",
                    resolved_type,
                    params,
                    column_id=column_rule_id,
                    action="Block" if business_block.value else "Warn",
                    existing=existing,
                    active=bool(business_enabled.value),
                )
                stage_guardrails([record])
                render_table_summary()
                if column_rule_id:
                    selected_dq_by_column[column_rule_id] = resolved_type
                    refresh_business_saved_options()
                    set_status(
                        "Business Rule resolved to a Column Rule and staged on "
                        f"{resolved_columns[0]}. Open Columns to review it before saving."
                    )
                else:
                    refresh_business_saved_options(str(record["guardrail_rule_id"]))
                business_resolved.clear()
                apply_business_rule.disabled = True
                set_validation_error("business_rule")
                render_engineering_review(record)
                if not column_rule_id:
                    set_status(
                        "Business Rule staged in the Data Contract. Save Data Contract to persist."
                    )
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error("business_rule", exc)
                set_status(str(exc), error=True)

        def approve_engineering_review_clicked(_button: Any) -> None:
            try:
                rule = business_lookup.get(str(business_saved.value or ""), {})
                required, status = engineering_review_state(rule)
                if not required:
                    raise ValueError("The selected Business Rule does not require Engineering review.")
                if status == "approved":
                    return
                reviewer = str(engineering_reviewer.value or "").strip()
                if not reviewer:
                    raise ValueError("Engineering reviewer is required before approval.")
                params = _parameters(rule)
                params.update({
                    "engineering_review_required": True,
                    "engineering_review_status": "approved",
                    "engineering_reviewed_by": reviewer,
                    "engineering_review_note": str(engineering_review_note.value or "").strip(),
                })
                record = guardrail_record(
                    "data_quality", "custom_expression", params,
                    action=str(rule.get("action") or "Warn"),
                    existing=rule,
                    active=bool(rule.get("is_active", True)),
                )
                stage_guardrails([record])
                refresh_business_saved_options(str(record["guardrail_rule_id"]))
                render_engineering_review(record)
                set_validation_error("business_rule.engineering_review")
                set_status(
                    "Engineering review approved and staged. Save Data Contract to persist."
                )
            except (TypeError, ValueError, RuntimeError) as exc:
                set_validation_error("business_rule.engineering_review", exc)
                set_status(str(exc), error=True)

        business_saved.observe(hydrate_business_saved, names="value")
        business_requirement.observe(invalidate_business_proposal, names="value")
        business_columns.observe(invalidate_business_proposal, names="value")
        resolve_business_rule.on_click(resolve_business_rule_clicked)
        apply_business_rule.on_click(apply_business_rule_clicked)
        approve_engineering_review.on_click(approve_engineering_review_clicked)
        refresh_business_saved_options()
        hydrate_business_saved()

        business_left = (
            widgets.HTML(
                "<div style='color:#0f6cbd;font-size:11px;font-weight:800;"
                "text-transform:uppercase;letter-spacing:.07em;'>Business Rules</div>"
                "<div style='color:#667085;font-size:12px;line-height:1.45;margin-top:4px;'>"
                "Generate enforceable Data Quality rules from plain-language business rules."
                "</div>"
            ),
            business_saved,
        )
        business_primary = widgets.VBox(
            [
                widgets.HTML(
                    "<div style='color:#667085;font-size:12px;line-height:1.5;'>"
                    "Review the resolved deterministic rule and choose whether it is active "
                    "and whether failure should block the pipeline.</div>"
                ),
                business_rule_controls,
                business_proposal,
                engineering_review_panel,
            ],
            layout=widgets.Layout(width="100%", min_width="0", gap="8px"),
        )
        if ai_visible:
            business_ai_panel = widgets.VBox(
                [
                    widgets.HTML("<b>AI assistant</b>"),
                    widgets.HTML(
                        "<div style='color:#667085;font-size:12px;line-height:1.5;'>"
                        "Write a business rule in plain language. FabricOps translates it into "
                        "a reviewable, enforceable Data Quality rule.</div>"
                    ),
                    widgets.HTML("<b>Business rule</b>"),
                    business_requirement,
                    widgets.HTML("<b>Relevant columns (optional)</b>"),
                    business_columns,
                    business_examples,
                    shared.action_row(
                        widgets, [resolve_business_rule, apply_business_rule]
                    ),
                ],
                layout=widgets.Layout(
                    width="100%", min_width="0", gap="8px",
                    padding="0 0 0 16px",
                    border_left="1px solid #e1e6eb",
                ),
            )
            business_content = widgets.GridBox(
                [business_primary, business_ai_panel],
                layout=widgets.Layout(
                    width="100%",
                    grid_template_columns="minmax(0, 68fr) minmax(240px, 32fr)",
                    grid_gap="16px",
                    align_items="flex-start",
                ),
            )
        else:
            business_ai_panel = widgets.VBox(
                layout=widgets.Layout(display="none")
            )
            business_content = business_primary
        business_right = (
            shared.form_section(
                widgets,
                title="Generate Enforceable Data Quality Rules from Business Rules",
                children=[
                    widgets.HTML(
                        "<div style='color:#667085;font-size:12px;line-height:1.5;"
                        "margin-bottom:8px;'>This page showcases one FabricOps capability. "
                        "For the end-to-end Governance and Engineering lifecycle it fits into, "
                        "see <a href='https://voycepeh.github.io/FabricOps-Starter-Kit/"
                        "how-fabricops-works/' target='_blank'>How FabricOps Works</a>.</div>"
                    ),
                    business_content,
                ],
            ),
        )
        view_content["Business Rules"] = (business_left, business_right)


        # Manifest: current working contract plus changes since the last persisted draft.
        payload = refresh_manifest() or {}
        saved_payload = state.get("_saved_payload") or {}
        sections = _manifest_sections(
            payload, column_profiles=runtime_context.get("column_profiles", {})
        )

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
            refreshed_sections = _manifest_sections(
                payload, column_profiles=runtime_context.get("column_profiles", {})
            )
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
            pending_engineering_review = any(
                str(rule.get("rule_type") or "") == "custom_expression"
                and rule.get("is_active", True)
                and bool(_parameters(rule).get("engineering_review_required", True))
                and str(_parameters(rule).get("engineering_review_status") or "pending").lower()
                != "approved"
                for rule in session_guardrails()
            )
            freeze_button = widgets.Button(
                description=f"Freeze v{row['contract_version']}…",
                disabled=bool(state.get("dirty")) or pending_engineering_review,
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
                    errors = state["_validation_errors"]
                    if errors:
                        first_error = next(iter(errors.values()))
                        raise ValueError(
                            "Complete the current draft configuration before saving: "
                            f"{first_error}"
                        )
                    scope = (str(current["contract_id"]), int(current["contract_version"]))
                    retained_columns = state["_column_drafts"].get(scope, {})
                    if retained_columns:
                        raise ValueError(
                            "Complete the retained Column edits before saving the Data Contract."
                        )
                    save_data_contract_session()
                except (TypeError, ValueError, RuntimeError) as exc:
                    set_status(str(exc), error=True)

            def freeze_clicked(_button: Any) -> None:
                if state.get("dirty"):
                    set_status("Save the Data Contract before freezing this version.", error=True)
                    return
                pending_review = any(
                    str(rule.get("rule_type") or "") == "custom_expression"
                    and rule.get("is_active", True)
                    and bool(_parameters(rule).get("engineering_review_required", True))
                    and str(_parameters(rule).get("engineering_review_status") or "pending").lower()
                    != "approved"
                    for rule in session_guardrails()
                )
                if pending_review:
                    set_status(
                        "Complete Engineering review for all active Custom Expression Business Rules before freezing.",
                        error=True,
                    )
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
            actions.append(widgets.HTML(
                "<div style='color:#667085;font-size:12px;'>"
                "Frozen contracts are review-only here. Complete exact-version validation, "
                "Data Agreement selection, and Production activation in the Activation widget."
                "</div>"
            ))
        review_left = table_left

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
            "table_grain": table_grain, "row_key_columns": row_key_columns,
            "row_key_block": row_key_block, "grain_profile_evidence": grain_profile_evidence,
            "grain_ai": grain_ai, "suggest_grain": suggest_grain, "accept_grain": accept_grain,
            "table_definition": table_definition,
            "table_guardrails": table_rules,
            "load_strategy": load_strategy_control,
            "processing_source": processing_source_hint,
            "processing_parameters": processing_parameter_controls,
            "partition_column": partition_column_control,
            "watermark_column": watermark_column_control,
            "key_columns": key_columns_control,
            "effective_column": effective_column_control,
            "tracked_columns": tracked_columns_control,
            "table_description_ai": table_description_ai,
            "accept_table_description": accept_table_description,
            "rerun_table_description": rerun_table_description,
            "column_search": column_search,
            "column_select": column_select, "column_context": column_context,
            "column_header": column_header, "column_definition": column_definition,
            "profile_context": profile_context, "column_description": column_description,
            "column_classification": column_classification, "required": required,
            "datatype_choice": datatype_choice, "column_option_style": column_option_style,
            "dq_panel": dq_panel, "dq_primary": dq_primary, "dq_ai_panel": dq_ai_panel,
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
            "dq_type": dq_type, "dq_parameter_controls": dq_parameter_controls,
            "dq_max_missing": dq_max_missing, "dq_blank_missing": dq_blank_missing,
            "dq_value_mode": dq_value_mode, "dq_values": dq_values,
            "dq_minimum": dq_minimum, "dq_minimum_inclusive": dq_minimum_inclusive,
            "dq_maximum": dq_maximum, "dq_maximum_inclusive": dq_maximum_inclusive,
            "dq_pattern": dq_pattern, "dq_enabled": dq_enabled, "dq_block": dq_block,
            "suggest_dq": suggest_dq, "dq_ai": dq_ai,
            "dq_ai_instruction": dq_ai_instruction,
            "dq_suggestion": dq_suggestion, "accept_dq_suggestion": accept_dq_suggestion,
            "business_saved": business_saved,
            "business_requirement": business_requirement,
            "business_columns": business_columns,
            "business_ai_panel": business_ai_panel,
            "business_primary": business_primary,
            "business_enabled": business_enabled,
            "business_block": business_block,
            "business_rule_controls": business_rule_controls,
            "business_proposal": business_proposal,
            "resolve_business_rule": resolve_business_rule,
            "apply_business_rule": apply_business_rule,
            "engineering_review_panel": engineering_review_panel,
            "engineering_review_status": engineering_review_status,
            "engineering_reviewer": engineering_reviewer,
            "engineering_review_note": engineering_review_note,
            "approve_engineering_review": approve_engineering_review,
            "manifest_preview": manifest_preview,
            "save_data_contract": save_contract_button,
            "discard_data_contract": discard_contract_button,
            "freeze": freeze_button if editable else None,
            "freeze_confirm": freeze_confirm_button if editable else None,
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
    change_table_button = widgets.Button(
        description="Exit",
        layout=widgets.Layout(width="120px"),
    )
    confirm_exit_discard = widgets.Button(
        description="Discard & exit",
        button_style="danger",
    )
    cancel_exit = widgets.Button(description="Cancel")
    table_exit_confirm = widgets.VBox(
        [
            widgets.HTML(
                "<div style='font-size:12px;line-height:1.5;text-align:center;'>"
                "<b>Discard unsaved changes?</b><br>"
                "<span style='color:#667085;'>Your staged Data Contract changes will be lost.</span>"
                "</div>"
            ),
            widgets.HBox(
                [cancel_exit, confirm_exit_discard],
                layout=widgets.Layout(width="100%", justify_content="center", gap="8px"),
            ),
        ],
        layout=widgets.Layout(
            width="100%", display="none", gap="8px", margin="8px 0 0 0"
        ),
    )
    table_exit_row = widgets.HBox(
        [change_table_button],
        layout=widgets.Layout(width="100%", justify_content="center"),
    )
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
        if state["_selector_refreshing"]:
            return
        selected_store = str(store_control.value or "")
        selected_schema = str(schema_control.value or "")
        rows = [
            row for row in table_rows
            if str(row.get("layer") or "") == selected_store
            and str(row.get("schema_name") or "") == selected_schema
        ]
        pending = str(state.get("pending_table_id") or "")
        options = [
            ("Select governed table", ""),
            *[
                (str(row.get("table_name") or row.get("table_id")), str(row["table_id"]))
                for row in rows
            ],
        ]
        values = [item[1] if isinstance(item, tuple) else item for item in options]
        state["_selector_refreshing"] = True
        try:
            table_control.value = None
            table_control.options = options
            table_control.value = pending if pending in values else ""
        finally:
            state["_selector_refreshing"] = False
        table_changed({"new": table_control.value})

    def refresh_schema_options(*_args: Any) -> None:
        if state["_selector_refreshing"]:
            return
        selected_store = str(store_control.value or "")
        schemas = list(dict.fromkeys(
            str(row.get("schema_name") or "")
            for row in table_rows
            if str(row.get("layer") or "") == selected_store
        ))
        pending_row = next(
            (row for row in table_rows if str(row.get("table_id") or "") == str(state.get("pending_table_id") or "")),
            None,
        )
        preferred = str((pending_row or {}).get("schema_name") or "")
        state["_selector_refreshing"] = True
        try:
            schema_control.value = None
            schema_control.options = schemas
            schema_control.value = preferred if preferred in schemas else (schemas[0] if schemas else None)
        finally:
            state["_selector_refreshing"] = False
        refresh_table_options()

    def table_changed(change: dict[str, Any]) -> None:
        if state["_selector_refreshing"]:
            return
        selected = str(change.get("new") or "")
        state["pending_table_id"] = selected or None
        matches = [row for row in state["contracts"] if str(row.get("table_id") or "") == selected]
        options = [
            *[(f"v{row['contract_version']} · {str(row.get('status') or '').title()}", str(row["contract_version"])) for row in matches],
            ("New draft", "new"),
        ]
        preferred = state.get("pending_contract_version")
        preferred_value = str(preferred) if preferred is not None else None
        available = [str(row["contract_version"]) for row in matches]
        state["_selector_refreshing"] = True
        try:
            contract_control.value = None
            contract_control.options = options
            if preferred_value in available:
                contract_control.value = preferred_value
            elif matches:
                contract_control.value = str(matches[0]["contract_version"])
            else:
                contract_control.value = "new"
        finally:
            state["_selector_refreshing"] = False
        contract_changed({"new": contract_control.value})

    def contract_changed(change: dict[str, Any]) -> None:
        if state["_selector_refreshing"]:
            return
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

    def return_to_selector(message: str) -> None:
        state["current"] = None
        state["manifest"] = None
        state["table_id"] = None
        state["contract_version"] = None
        editor_shell.layout.display = "none"
        selector_panel.layout.display = ""
        set_status(message)

    state["_return_to_selector"] = return_to_selector

    def change_table(_button: Any) -> None:
        if state.get("dirty"):
            table_exit_confirm.layout.display = ""
            return
        return_to_selector("Select a governed table and contract.")

    def cancel_exit_clicked(_button: Any) -> None:
        table_exit_confirm.layout.display = "none"

    def confirm_exit_clicked(_button: Any) -> None:
        table_exit_confirm.layout.display = "none"
        if state.get("current"):
            discard_data_contract_session()
        return_to_selector("Unsaved changes discarded. Select a governed table and contract.")

    open_with_ai_button.on_click(lambda _button: open_selected(with_ai=True))
    open_without_ai_button.on_click(lambda _button: open_selected(with_ai=False))
    change_table_button.on_click(change_table)
    cancel_exit.on_click(cancel_exit_clicked)
    confirm_exit_discard.on_click(confirm_exit_clicked)

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

    store_control.observe(refresh_schema_options, names="value")
    schema_control.observe(refresh_table_options, names="value")
    table_control.observe(table_changed, names="value")
    contract_control.observe(contract_changed, names="value")
    render()
    page = shared.form_page(
        widgets, title="Data Contract",
        description="Select, author, review, and freeze one governed table contract.",
        children=[selector_panel, editor_shell, status],
    )
    state["_controls"].update({
        "page": page, "selector_panel": selector_panel, "editor_shell": editor_shell,
        "store": store_control, "schema": schema_control,
        "table": table_control, "contract": contract_control,
        "open_with_ai": open_with_ai_button, "open_without_ai": open_without_ai_button,
        "open": open_without_ai_button, "open_progress": open_progress,
        "change_table": change_table_button,
        "table_exit_row": table_exit_row,
        "table_exit_confirm": table_exit_confirm,
        "confirm_exit_discard": confirm_exit_discard,
        "cancel_exit": cancel_exit,
    })
    ip.display(page)
    return state
