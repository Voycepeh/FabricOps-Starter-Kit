"""Standalone Schema, Freshness, and Changes Guardrail authoring widget."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import html
import json
from typing import Any

from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.data_contract.shared import save_guardrails
from fabricops_kit.pipeline.shared import (
    GUARDRAIL_CHANGE_BEHAVIOURS,
    resolve_guardrail_change_behaviour,
)
from fabricops_kit.widgets import shared as authoring
from fabricops_kit.widgets import shared
from fabricops_kit.widgets import enrichment_shared as enrichment_ai

CHANGE_BEHAVIOURS = GUARDRAIL_CHANGE_BEHAVIOURS
_DURATION_UNITS = ("Minutes", "Hours", "Days")
_FAILURE_ACTIONS = (("Block", "Block"), ("Warn", "Warn"))
_FAILURE_SEVERITIES = {value for _, value in _FAILURE_ACTIONS}


def _guardrail_version(rules: Iterable[Mapping[str, Any]]) -> int:
    """Return the latest explicit Guardrail version."""
    return max((int(row.get("guardrail_version") or 0) for row in rules), default=0)


def _guardrail_records_from_selection(
    state: Mapping[str, Any],
    *,
    required_columns: Iterable[str],
    freshness_column: str,
    maximum_age: int | float,
    maximum_age_unit: str,
    change_behaviour: str,
    schema_action: str = "Block",
    freshness_action: str = "Block",
    change_action: str = "Block",
    partition_column: str = "",
    change_column: str = "",
    guardrail_version: int | None = None,
    config: Any = None,
    sensitive_rules: Iterable[Mapping[str, Any]] = (),
) -> list[dict[str, Any]]:
    """Translate Schema, Freshness, and Changes controls into Stage 4A rows."""
    del config
    columns = [str(value) for value in state.get("columns", [])]
    available = set(columns)
    required = [str(value) for value in required_columns]
    if not required or any(value not in available for value in required):
        raise ValueError("Select at least one required column from the selected table schema.")
    if freshness_column:
        if freshness_column not in available:
            raise ValueError("Freshness column must come from the selected table schema.")
        try:
            age = float(maximum_age)
        except (TypeError, ValueError) as exc:
            raise ValueError("Maximum age must be a positive number.") from exc
        if age <= 0:
            raise ValueError("Maximum age must be a positive number.")
        if maximum_age_unit not in _DURATION_UNITS:
            raise ValueError("Maximum age unit must be Minutes, Hours, or Days.")
    else:
        age = 0.0
    for label, value in (
        ("Partition column", partition_column),
        ("Change / watermark column", change_column),
    ):
        if value and value not in available:
            raise ValueError(f"{label} must come from the selected table schema.")
    expected_change, source_pattern = resolve_guardrail_change_behaviour(change_behaviour)
    actions = {
        "schema": str(schema_action),
        "freshness": str(freshness_action),
        "change": str(change_action),
    }
    if any(value not in _FAILURE_SEVERITIES for value in actions.values()):
        raise ValueError("Failure action must be Block pipeline or Warn only.")

    version = guardrail_version or (
        _guardrail_version(state.get("existing_rules") or ()) + 1
    )
    data_types = {
        str(row.get("column_name") or ""): str(row.get("data_type") or "")
        for row in state.get("catalogue_profile_rows", [])
    }
    records = [
        authoring.build_rule_record(
            state,
            guardrail_type="schema",
            rule_id="schema",
            rule_type="minimum_required",
            parameters={
                "columns": required,
                "data_types": {name: data_types.get(name, "") for name in required},
            },
            action=actions["schema"],
            guardrail_version=version,
        ),
        authoring.build_rule_record(
            state,
            guardrail_type="freshness",
            rule_id="freshness",
            rule_type="max_age" if freshness_column else "skip",
            parameters={
                "freshness_column": freshness_column,
                "maximum_age": age,
                "maximum_age_unit": maximum_age_unit.lower(),
            },
            action=actions["freshness"],
            guardrail_version=version,
        ),
        authoring.build_rule_record(
            state,
            guardrail_type="changes",
            rule_id="changes",
            rule_type=expected_change,
            parameters={
                "change_behaviour": change_behaviour,
                "expected_change": expected_change,
                "source_pattern": source_pattern,
                "partition_column": partition_column,
                "change_column": change_column,
            },
            action=actions["change"],
            guardrail_version=version,
        ),
    ]
    for sensitive_rule in sensitive_rules:
        records.append(
            authoring.sensitive_data_record_from_selection(
                state,
                column_name=str(sensitive_rule.get("column_name") or ""),
                treatment=str(sensitive_rule.get("treatment") or ""),
                action=str(sensitive_rule.get("action") or "Block"),
                guardrail_version=version,
                is_active=bool(sensitive_rule.get("is_active", True)),
                parameters=sensitive_rule.get("parameters"),
            )
        )
    return records


def widget_author_guardrails(
    *,
    spark_session: Any,
    context: dict[str, Any] | None = None,
    commit: bool = False,
) -> dict[str, Any]:
    """Configure table and Sensitive Data Guardrails for a profiled table.

    Parameters
    ----------
    spark_session : Any
        Fabric Spark session used to resolve profiled targets and save rules.
    context : dict[str, Any], optional
        Advanced override for the active ``FABRIC_CONTEXT``.
    commit : bool, default=False
        Save the initial selection immediately. The default renders the widget.

    Returns
    -------
    dict[str, Any]
        Target state, authoring controls, canonical preview, and save action.

    Raises
    ------
    ValueError
        If no profiled target exists or configured values are invalid.

    Notes
    -----
    The widget resolves a Data Contract version for the selected profiled
    Catalogue table and writes ``METADATA_GUARDRAIL`` rows owned by its
    ``contract_id`` and ``contract_version``. Runtime code resolves the
    underlying ``table_id`` through ``METADATA_DATA_CONTRACT``.
    Sensitive Data uses one compact Add/Edit editor plus an authored-rule list;
    it does not create treatment controls for every Catalogue column. When AI
    Enrichment is enabled, suggestions use compact metadata context and populate
    editable drafts only. Governance must review and save them through the same
    normalized Guardrail service.

    Examples
    --------
    >>> form = widget_author_guardrails(spark_session=spark)

    """
    from IPython import display as ip

    config, env, _ = resolve_fabric_context(context=context)
    widgets = shared.require_ipywidgets()
    authoring_box = widgets.VBox()
    current: dict[str, Any] = {}

    def render(state: Mapping[str, Any]) -> None:
        current.clear()
        current.update(
            _render_guardrail_authoring(
                state, spark_session=spark_session, context=context, commit=False
            )
        )
        authoring_box.children = (current["ui"],)

    state, target, target_controls = authoring.load_guardrail_authoring_targets(
        config,
        env,
        spark_session=spark_session,
        widgets=widgets,
        on_change=render,
    )
    if commit:
        current["records"] = current["save"]()
    ui = shared.form_page(
        widgets,
        title="Author Guardrails",
        description=(
            "Select a profiled table, then author table and Sensitive Data expectations."
        ),
        children=[
            shared.form_section(
                widgets,
                title="Target",
                children=[target, target_controls["target_summary"]],
            ),
            authoring_box,
        ],
    )
    ip.display(ui)
    return {
        "state": state,
        "controls": {"target": target, **target_controls},
        "authoring": current,
        "ui": ui,
    }


def _load_sensitive_rules(state: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Return the latest independently authored Sensitive Data rules by column."""
    latest = {}
    names_by_id = {value: name for name, value in (state.get("column_ids") or {}).items()}
    for row in state.get("existing_rules") or ():
        if str(row.get("guardrail_type") or "") != "sensitive_data":
            continue
        column_id = str(row.get("column_id") or "")
        current = latest.get(column_id)
        order = (int(row.get("guardrail_version") or 0), str(row.get("_committed_at") or ""))
        current_order = (
            int(current.get("guardrail_version") or 0), str(current.get("_committed_at") or "")
        ) if current else (-1, "")
        if order > current_order:
            params = authoring.rule_parameters(row)
            latest[column_id] = {
                "column_name": names_by_id.get(column_id, ""),
                "column_id": column_id,
                "treatment": str(params.get("treatment") or "tokenize"),
                "action": str(row.get("action") or "Block"),
                "parameters": {
                    key: value for key, value in params.items()
                    if key not in {"scope", "treatment"}
                },
                "is_active": row.get("is_active", True) is not False,
                "persisted": True,
            }
    return list(latest.values())


def _sensitive_rule_from_controls(controls: Mapping[str, Any], state: Mapping[str, Any]) -> dict[str, Any]:
    """Build and canonically validate one editable Sensitive Data draft."""
    treatment = str(controls["treatment"].value)
    parameters = {}
    if treatment == "mask":
        parameters = {
            "preserve_start": controls["preserve_start"].value,
            "preserve_end": controls["preserve_end"].value,
            "mask_character": controls["mask_character"].value,
        }
    elif treatment == "bucket":
        parameters = {
            "bins": [
                float(value.strip()) for value in str(controls["bins"].value).split(",")
                if value.strip()
            ],
            "labels": [
                value.strip() for value in str(controls["labels"].value).split(",")
            ],
        }
    record = authoring.sensitive_data_record_from_selection(
        state,
        column_name=str(controls["column"].value),
        treatment=treatment,
        action=str(controls["action"].value),
        parameters=parameters,
    )
    return {
        "column_name": str(controls["column"].value),
        "column_id": record["column_id"],
        "treatment": treatment,
        "action": record["action"],
        "parameters": parameters,
        "is_active": True,
        "persisted": False,
    }


def _render_sensitive_data_rule_list(widgets, drafts, container, *, edit_rule, remove_rule) -> None:
    """Render compact authored-rule summaries with Edit and Remove actions."""
    rows = []
    for draft in drafts:
        if not draft.get("is_active", True):
            continue
        edit = widgets.Button(description="Edit")
        remove = widgets.Button(description="Remove", button_style="warning")
        edit.on_click(lambda _, item=draft: edit_rule(item))
        remove.on_click(lambda _, item=draft: remove_rule(item))
        rows.append(widgets.GridBox(
            [widgets.HTML(value=f"<code>{html.escape(draft['column_name'])}</code>"),
             widgets.HTML(value=html.escape(str(draft["treatment"]).title())),
             widgets.HTML(value=html.escape(str(draft["action"]))), edit, remove],
            layout=widgets.Layout(
                width="100%", grid_template_columns="1fr 120px 100px 80px 90px",
                grid_gap="4px 10px", align_items="center",
            ),
        ))
    container.children = tuple(rows) if rows else (
        widgets.HTML(value="<i>No Sensitive Data rules authored.</i>"),
    )


def _render_sensitive_data_editor(
    state: Mapping[str, Any], *, widgets: Any, ai_config: Mapping[str, Any]
) -> dict[str, Any]:
    """Render one compact Sensitive Data rule editor and transient rule list."""
    drafts = _load_sensitive_rules(state)
    column = widgets.Dropdown(
        options=list(state.get("columns") or ()),
        **shared.widget_common(widgets, "Column"),
    )
    treatment = widgets.Dropdown(
        options=[("Tokenize", "tokenize"), ("Mask", "mask"),
                 ("Bucket", "bucket"), ("Remove", "remove")],
        value="tokenize", **shared.widget_common(widgets, "Treatment"),
    )
    action = widgets.Dropdown(options=_FAILURE_ACTIONS, value="Block", **shared.widget_common(widgets, "Action"))
    preserve_start = widgets.BoundedIntText(value=0, min=0, **shared.widget_common(widgets, "Preserve start"))
    preserve_end = widgets.BoundedIntText(value=0, min=0, **shared.widget_common(widgets, "Preserve end"))
    mask_character = widgets.Text(value="*", **shared.widget_common(widgets, "Mask character"))
    bins = widgets.Text(**shared.widget_common(widgets, "Numeric bins"))
    labels = widgets.Text(**shared.widget_common(widgets, "Labels"))
    mask_options = widgets.HBox([preserve_start, preserve_end, mask_character])
    bucket_options = widgets.HBox([bins, labels])
    add_update = widgets.Button(description="Add / Update rule", button_style="primary")
    suggest_button = widgets.Button(description="✨ Suggest Sensitive Data")
    suggest_button.disabled = not (
        bool(ai_config.get("enabled", False))
        and str(ai_config.get("sensitive_data_prompt") or "").strip()
    )
    status = widgets.HTML()
    current_rules = widgets.VBox()
    editing = {"column_id": ""}
    change_callback = {"value": None}
    controls = {
        "column": column, "treatment": treatment, "action": action,
        "preserve_start": preserve_start, "preserve_end": preserve_end,
        "mask_character": mask_character, "bins": bins, "labels": labels,
    }

    def update_options(*_: Any) -> None:
        mask_options.layout.display = "" if treatment.value == "mask" else "none"
        bucket_options.layout.display = "" if treatment.value == "bucket" else "none"

    def edit_rule(draft) -> None:
        editing["column_id"] = draft["column_id"]
        column.value = draft["column_name"]
        treatment.value = draft["treatment"]
        action.value = draft["action"]
        params = draft.get("parameters") or {}
        preserve_start.value = int(params.get("preserve_start", 0))
        preserve_end.value = int(params.get("preserve_end", 0))
        mask_character.value = str(params.get("mask_character") or "*")
        bins.value = ", ".join(str(value) for value in params.get("bins", []))
        labels.value = ", ".join(str(value) for value in params.get("labels", []))
        update_options()

    def remove_rule(draft) -> None:
        if draft.get("persisted"):
            draft["is_active"] = False
        else:
            drafts.remove(draft)
        if editing["column_id"] == draft["column_id"]:
            editing["column_id"] = ""
        _render_sensitive_data_rule_list(
            widgets, drafts, current_rules, edit_rule=edit_rule, remove_rule=remove_rule
        )
        if change_callback["value"]:
            change_callback["value"]()

    def add_or_update(*_: Any) -> dict[str, Any]:
        try:
            draft = _sensitive_rule_from_controls(controls, state)
        except (TypeError, ValueError) as exc:
            status.value = f"<b style='color:#b00020'>Validation error:</b> {html.escape(str(exc))}"
            return {}
        current = next((item for item in drafts if item["column_id"] == draft["column_id"]), None)
        if current:
            persisted = current.get("persisted", False)
            current.update(draft)
            current["persisted"] = persisted
        else:
            drafts.append(draft)
        editing["column_id"] = draft["column_id"]
        status.value = "Draft rule updated. Use Save Guardrails to persist it."
        _render_sensitive_data_rule_list(
            widgets, drafts, current_rules, edit_rule=edit_rule, remove_rule=remove_rule
        )
        if change_callback["value"]:
            change_callback["value"]()
        return draft

    def suggest() -> list[dict[str, Any]]:
        if not bool(ai_config.get("enabled", False)):
            status.value = "AI Enrichment is disabled in 00_env_config. Manual authoring remains available."
            return []
        sensitive_prompt = str(ai_config.get("sensitive_data_prompt") or "").strip()
        if not sensitive_prompt:
            status.value = "Sensitive Data AI prompt is not configured. Manual authoring remains available."
            return []
        try:
            suggestions = enrichment_ai.suggest_sensitive_data(
                enrichment_ai.build_ai_sensitive_data_context(dict(state)),
                prompt=sensitive_prompt,
            )
        except Exception as exc:
            status.value = f"AI suggestion unavailable: {html.escape(str(exc))} Manual authoring remains available."
            return []
        if not suggestions:
            status.value = "AI returned no valid Sensitive Data rules. Manual authoring remains available."
            return []
        for suggestion in suggestions:
            current = next((item for item in drafts if item["column_id"] == suggestion["column_id"]), None)
            if current:
                persisted = current.get("persisted", False)
                current.update(suggestion)
                current["persisted"] = persisted
            else:
                drafts.append({**suggestion, "persisted": False})
        _render_sensitive_data_rule_list(
            widgets, drafts, current_rules, edit_rule=edit_rule, remove_rule=remove_rule
        )
        status.value = "AI suggestions added to draft rules. Review or edit them before saving."
        if change_callback["value"]:
            change_callback["value"]()
        return suggestions

    def set_on_change(callback) -> None:
        change_callback["value"] = callback

    treatment.observe(update_options, names="value")
    add_update.on_click(add_or_update)
    suggest_button.on_click(lambda _: suggest())
    update_options()
    _render_sensitive_data_rule_list(
        widgets, drafts, current_rules, edit_rule=edit_rule, remove_rule=remove_rule
    )
    ui = widgets.VBox([
        shared.action_row(widgets, [suggest_button]),
        widgets.HTML(value="<b>Add / Edit rule</b>"),
        shared.form_grid(widgets, [column, treatment, action]),
        mask_options, bucket_options,
        shared.action_row(widgets, [add_update]), status,
        widgets.HTML(value="<b>Current rules</b>"), current_rules,
    ])
    return {
        "ui": ui, "controls": controls, "draft_rules": drafts,
        "add_or_update": add_or_update, "edit_rule": edit_rule,
        "remove_rule": remove_rule, "suggest": suggest,
        "suggest_button": suggest_button, "status": status,
        "mask_options": mask_options, "bucket_options": bucket_options,
        "current_rules": current_rules, "update_options": update_options,
        "set_on_change": set_on_change,
    }


def _render_guardrail_authoring(
    state: Mapping[str, Any],
    *,
    spark_session: Any = None,
    context: dict[str, Any] | None = None,
    commit: bool = False,
) -> dict[str, Any]:
    """Render Guardrail controls for one resolved normalized target state."""
    if not str(state.get("table_id") or "").strip():
        raise ValueError("A selected profiled table with a canonical table_id is required.")
    config, env, _ = resolve_fabric_context(context=context)
    widgets = shared.require_ipywidgets()
    columns = [str(value) for value in state.get("columns", [])]
    existing = list(state.get("existing_rules") or [])
    version_state = {"persisted": _guardrail_version(existing)}
    schema_rule = authoring.latest_rule(existing, "schema")
    freshness_rule = authoring.latest_rule(existing, "freshness")
    change_rule = authoring.latest_rule(existing, "changes")
    schema_params = authoring.rule_parameters(schema_rule)
    freshness_params = authoring.rule_parameters(freshness_rule)
    change_params = authoring.rule_parameters(change_rule)
    selected_required = set(schema_params.get("columns") or columns)
    schema_data_types = {
        str(row.get("column_name") or ""): str(row.get("data_type") or "")
        for row in state.get("catalogue_profile_rows", [])
    }
    schema_checkboxes = {
        name: widgets.Checkbox(
            value=name in selected_required, description="", indent=False
        )
        for name in columns
    }
    schema_header = widgets.GridBox(
        [
            widgets.HTML(value="<b>Required</b>"),
            widgets.HTML(value="<b>Column name</b>"),
            widgets.HTML(value="<b>Data type</b>"),
        ],
        layout=widgets.Layout(
            width="100%",
            grid_template_columns="90px minmax(160px, 1fr) minmax(130px, 1fr)",
            grid_gap="4px 12px",
        ),
    )
    schema_rows = {
        name: widgets.GridBox(
            [
                schema_checkboxes[name],
                widgets.HTML(value=f"<code>{html.escape(name)}</code>"),
                widgets.HTML(
                    value=f"<code>{html.escape(schema_data_types.get(name, ''))}</code>"
                ),
            ],
            layout=widgets.Layout(
                width="100%",
                grid_template_columns="90px minmax(160px, 1fr) minmax(130px, 1fr)",
                grid_gap="4px 12px",
                align_items="center",
            ),
        )
        for name in columns
    }
    required_schema = widgets.VBox(
        [
            widgets.HTML(
                value=(
                    "<b>Required schema</b><br>"
                    "<span style='font-size:12px'>Checked columns must exist with the shown data type.</span>"
                )
            ),
            schema_header,
            *schema_rows.values(),
        ],
        layout=widgets.Layout(
            width="100%", height="auto", overflow="visible", gap="4px"
        ),
    )
    schema_failure_action = widgets.Dropdown(
        options=_FAILURE_ACTIONS,
        value=str(schema_rule.get("action") or "Block"),
        **shared.widget_common(widgets, "On failure"),
    )
    freshness_value = str(freshness_params.get("freshness_column") or "")
    freshness_column = widgets.Dropdown(
        options=["", *columns],
        value=freshness_value if freshness_value in columns else "",
        **shared.widget_common(widgets, "Freshness date/time column"),
    )
    maximum_age = widgets.FloatText(
        value=float(freshness_params.get("maximum_age") or 1),
        **shared.widget_common(widgets, "Maximum age"),
    )
    unit_value = str(freshness_params.get("maximum_age_unit") or "days").title()
    maximum_age_unit = widgets.Dropdown(
        options=_DURATION_UNITS,
        value=unit_value if unit_value in _DURATION_UNITS else "Days",
        **shared.widget_common(widgets, "Unit"),
    )
    freshness_failure_action = widgets.Dropdown(
        options=_FAILURE_ACTIONS,
        value=str(freshness_rule.get("action") or "Block"),
        **shared.widget_common(widgets, "On failure"),
    )
    behaviour = str(change_params.get("change_behaviour") or "Incremental append")
    change_behaviour = widgets.Dropdown(
        options=CHANGE_BEHAVIOURS,
        value=behaviour if behaviour in CHANGE_BEHAVIOURS else "Incremental append",
        **shared.widget_common(widgets, "Change behaviour"),
    )
    partition_value = str(change_params.get("partition_column") or "")
    partition_column = widgets.Dropdown(
        options=["", *columns],
        value=partition_value if partition_value in columns else "",
        **shared.widget_common(widgets, "Partition column"),
    )
    change_value = str(change_params.get("change_column") or "")
    change_column = widgets.Dropdown(
        options=["", *columns],
        value=change_value if change_value in columns else "",
        **shared.widget_common(widgets, "Change / watermark column"),
    )
    change_failure_action = widgets.Dropdown(
        options=_FAILURE_ACTIONS,
        value=str(change_rule.get("action") or "Block"),
        **shared.widget_common(widgets, "On failure"),
    )
    governance_config = getattr(config, "governance_config", None)
    ai_config = dict(getattr(governance_config, "ai_enrichment", None) or {})
    sensitive_editor = _render_sensitive_data_editor(
        state, widgets=widgets, ai_config=ai_config
    )
    preview = shared.preview_region(widgets, widgets.Textarea(
        description="Canonical preview",
        disabled=True,
    ))
    message = shared.status_message(widgets)
    save_button = widgets.Button(description="Save Guardrails", button_style="primary")
    version_display = widgets.HTML(
        value=f"<b>Next save version</b><br>{version_state['persisted'] + 1}"
    )

    def build_records() -> list[dict[str, Any]]:
        return _guardrail_records_from_selection(
            state,
            required_columns=[
                name for name, control in schema_checkboxes.items() if control.value
            ],
            freshness_column=freshness_column.value,
            maximum_age=maximum_age.value,
            maximum_age_unit=maximum_age_unit.value,
            change_behaviour=change_behaviour.value,
            schema_action=schema_failure_action.value,
            freshness_action=freshness_failure_action.value,
            change_action=change_failure_action.value,
            partition_column=partition_column.value,
            change_column=change_column.value,
            guardrail_version=version_state["persisted"] + 1,
            sensitive_rules=sensitive_editor["draft_rules"],
        )

    def refresh_preview(*_: Any) -> None:
        try:
            preview.value = json.dumps(
                build_records(), indent=2, sort_keys=True, default=str
            )
            message.value = ""
        except ValueError as exc:
            preview.value = ""
            message.value = (
                f"<b style='color:#b00020'>Validation error:</b> {html.escape(str(exc))}"
            )

    sensitive_editor["set_on_change"](refresh_preview)

    def save(*_: Any) -> list[dict[str, Any]]:
        records = build_records()
        if spark_session is None or config is None or env is None:
            message.value = (
                "<b>Preview only:</b> FABRIC_CONTEXT and spark_session are required to save."
            )
            return records
        canonical_records = save_guardrails(
            records, config=config, env=env, spark_session=spark_session
        )
        state_existing = state.get("existing_rules")
        if isinstance(state_existing, list):
            state_existing.extend(canonical_records)
        version_state["persisted"] = records[0]["guardrail_version"]
        version_display.value = (
            f"<b>Next save version</b><br>{version_state['persisted'] + 1}"
        )
        message.value = (
            f"<b style='color:green'>Saved Guardrail version "
            f"{records[0]['guardrail_version']}.</b>"
        )
        refresh_preview()
        return canonical_records

    for control in (
        *schema_checkboxes.values(),
        schema_failure_action,
        freshness_column,
        maximum_age,
        maximum_age_unit,
        freshness_failure_action,
        change_behaviour,
        partition_column,
        change_column,
        change_failure_action,
    ):
        control.observe(refresh_preview, names="value")
    save_button.on_click(save)

    identity = shared.form_grid(
        widgets,
        [
            widgets.HTML(
                value=f"<b>Environment</b><br>{html.escape(str(state.get('environment_name', '')))}"
            ),
            widgets.HTML(
                value=f"<b>Store</b><br>{html.escape(str(state.get('store_type', '')))}"
            ),
            widgets.HTML(
                value=f"<b>Schema</b><br>{html.escape(str(state.get('schema_name', '')))}"
            ),
            widgets.HTML(
                value=f"<b>Table</b><br>{html.escape(str(state.get('table_name', '')))}"
            ),
            version_display,
        ],
    )
    ui = shared.authoring_workspace(
        widgets,
        target=[identity],
        selection=[
            shared.form_section(
                widgets,
                title="Schema",
                children=[required_schema, schema_failure_action],
            ),
            shared.form_section(
                widgets,
                title="Sensitive Data",
                children=[sensitive_editor["ui"]],
            ),
        ],
        configuration=[
            shared.form_section(
                widgets,
                title="Freshness",
                children=[
                    shared.form_grid(
                        widgets,
                        [
                            freshness_column,
                            maximum_age,
                            maximum_age_unit,
                            freshness_failure_action,
                        ],
                    )
                ],
            ),
            shared.form_section(
                widgets,
                title="Changes",
                children=[
                    shared.form_grid(
                        widgets,
                        [
                            change_behaviour,
                            partition_column,
                            change_column,
                            change_failure_action,
                        ],
                    )
                ],
            ),
            preview,
            shared.action_row(widgets, [save_button]),
            message,
        ],
        titles=("Target context", "Schema selection", "Freshness, changes, and preview"),
    )
    result = {
        "version": version_state["persisted"] + 1,
        "next_version": version_state["persisted"] + 1,
        "version_state": version_state,
        "controls": {
            "schema_columns": schema_checkboxes,
            "schema_data_types": schema_data_types,
            "schema_rows": schema_rows,
            "schema_failure_action": schema_failure_action,
            "freshness_column": freshness_column,
            "maximum_age": maximum_age,
            "maximum_age_unit": maximum_age_unit,
            "freshness_failure_action": freshness_failure_action,
            "change_behaviour": change_behaviour,
            "partition_column": partition_column,
            "change_column": change_column,
            "change_failure_action": change_failure_action,
            "sensitive_data": sensitive_editor,
            "preview": preview,
        },
        "build_records": build_records,
        "refresh_preview": refresh_preview,
        "save": save,
        "save_button": save_button,
        "workspace": ui,
        "ui": ui,
    }
    refresh_preview()
    if commit:
        result["records"] = save()
    return result
