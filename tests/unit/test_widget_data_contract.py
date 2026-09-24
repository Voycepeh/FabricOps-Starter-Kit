"""Focused interaction tests for the unified Data Contract widget."""

from __future__ import annotations

import importlib
import json
import sys
import types

import pytest

module = importlib.import_module("fabricops_kit.widgets.widget_data_contract")


def _catalogue_rows(count: int = 2) -> list[dict]:
    rows = [{
        "table_id": "orders", "environment_name": "dev", "metadata_level": "table",
        "schema_name": "sales", "table_name": "orders", "store_type": "Lakehouse",
        "layer": "Silver", "is_active": True,
        "_workspace_id": "workspace-id", "_notebook_id": "writer-notebook-id",
    }]
    for index in range(count):
        rows.append({
            "table_id": "orders", "environment_name": "dev", "metadata_level": "column",
            "column_id": f"col-{index}", "column_name": f"column_{index}",
            "data_type": "string" if index else "long", "is_active": True,
        })
    return rows


@pytest.fixture
def widget_runtime(monkeypatch):
    """Provide mutable canonical service state behind the real ipywidgets controls."""
    class Layout(types.SimpleNamespace):
        pass

    class Widget:
        def __init__(self, value=None, options=(), description="", disabled=False, layout=None, **kwargs):
            self._observers = []
            self._dom_classes = []
            self.description = description
            self.disabled = disabled
            self.layout = layout or Layout()
            self.style = kwargs.get("style", {})
            self._options = options
            values = self._option_values(options)
            self._value = value if value is not None else (values[0] if values else None)

        @staticmethod
        def _option_values(options):
            return [item[1] if isinstance(item, tuple) else item for item in options]

        @property
        def options(self):
            return self._options

        @options.setter
        def options(self, options):
            self._options = options
            values = self._option_values(options)
            if self._value not in values:
                self.value = values[0] if values else None

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            old = self._value
            self._value = value
            if old != value:
                for callback in list(self._observers):
                    callback({"old": old, "new": value, "name": "value"})

        def observe(self, callback, names="value"):
            self._observers.append(callback)

        def add_class(self, name):
            self._dom_classes.append(name)

    class Box(Widget):
        def __init__(self, children=(), **kwargs):
            super().__init__(**kwargs)
            self.children = tuple(children)

    class Button(Widget):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self._click_handlers = []

        def on_click(self, callback):
            self._click_handlers.append(callback)

        def click(self):
            if not self.disabled:
                for callback in list(self._click_handlers):
                    callback(self)

    class Tab(Box):
        def set_title(self, index, title):
            pass

    ipywidgets = types.SimpleNamespace(
        Layout=lambda **kwargs: Layout(**kwargs), HTML=Widget, Text=Widget, Textarea=Widget,
        Dropdown=Widget, Checkbox=Widget, Select=Widget, SelectMultiple=Widget,
        ToggleButtons=Widget,
        Button=Button, VBox=Box, HBox=Box, GridBox=Box, Tab=Tab,
    )
    catalogue = _catalogue_rows()
    contract = {
        "contract_id": "contract-orders", "contract_version": 1, "table_id": "orders",
        "environment_name": "dev", "status": "draft", "is_active": False,
    }
    enrichment = [
        {"enrichment_id": "table-description", "contract_id": "contract-orders", "contract_version": 1, "environment_name": "dev", "enrichment_level": "table", "column_id": "", "enrichment_type": "Description", "value": "Orders table"},
        {"enrichment_id": "table-classification", "contract_id": "contract-orders", "contract_version": 1, "environment_name": "dev", "enrichment_level": "table", "column_id": "", "enrichment_type": "Classification", "value": "Internal"},
        {"enrichment_id": "column-description", "contract_id": "contract-orders", "contract_version": 1, "environment_name": "dev", "enrichment_level": "column", "column_id": "col-0", "enrichment_type": "Description", "value": "Order identifier"},
        {"enrichment_id": "column-classification", "contract_id": "contract-orders", "contract_version": 1, "environment_name": "dev", "enrichment_level": "column", "column_id": "col-0", "enrichment_type": "Classification", "value": "Confidential"},
    ]
    guardrails = [
        {"guardrail_rule_id": "schema", "guardrail_version": 1, "guardrail_type": "schema", "rule_type": "required_columns", "rule_parameters_json": '{"required_columns":["col-0"]}', "action": "Warn", "is_active": True},
        {"guardrail_rule_id": "fresh", "guardrail_version": 1, "guardrail_type": "freshness", "rule_type": "freshness", "rule_parameters_json": '{"freshness_column":"column_1","maximum_age":2,"maximum_age_unit":"days"}', "action": "Block", "is_active": True},
        {"guardrail_rule_id": "drift", "guardrail_version": 1, "guardrail_type": "source_drift", "rule_type": "source_drift", "rule_parameters_json": '{"partition_column":"column_0","change_column":"column_1","load_strategy":"append"}', "action": "Warn", "is_active": True},
        {"guardrail_rule_id": "sensitive", "guardrail_version": 1, "guardrail_type": "sensitive_data", "column_id": "col-0", "rule_type": "mask", "rule_parameters_json": '{"scope":"column","treatment":"mask","preserve_start":0,"preserve_end":0,"mask_character":"*"}', "action": "Block", "is_active": True},
        {"guardrail_rule_id": "dq", "guardrail_version": 1, "guardrail_type": "data_quality", "column_id": "col-0", "rule_type": "completeness", "rule_parameters_json": '{"columns":["column_0"],"maximum_missing_percent":0,"treat_blank_as_missing":false}', "action": "Block", "is_active": True},
        {"guardrail_rule_id": "dq-pattern", "guardrail_version": 1, "guardrail_type": "data_quality", "column_id": "col-0", "rule_type": "pattern", "rule_parameters_json": '{"columns":["column_0"],"pattern":"^ORD-[0-9]+$"}', "action": "Warn", "is_active": True},
        {"guardrail_rule_id": "advanced", "guardrail_version": 1, "guardrail_type": "data_quality", "column_id": "", "rule_type": "column_relationship", "rule_parameters_json": '{"columns":["column_1","column_0"],"operator":">"}', "action": "Warn", "is_active": True},
    ]
    calls = {"enrichment": [], "guardrails": [], "freeze": 0, "activate": 0, "profiles": []}
    schedule = {
        "status": "unavailable", "schedules": [],
        "message": "Scheduled Refresh discovery is unavailable for this notebook.",
    }
    ai_enrichment = {
        "enabled": False,
        "description_prompt": "configured description prompt",
        "sensitive_data_prompt": "configured sensitive prompt",
        "dq_prompt": "configured DQ prompt",
    }

    def review(**_kwargs):
        if contract["status"] == "draft":
            return {
                "contract": dict(contract), "contract_id": contract["contract_id"],
                "contract_version": 1, "table_id": "orders", "environment_name": "dev",
                "catalogue_rows": [dict(row) for row in catalogue],
                "available_columns": [dict(row) for row in catalogue[1:]],
                "enrichment": [dict(row) for row in enrichment],
                "guardrails": [dict(row) for row in guardrails],
            }
        return {
            "contract": dict(contract), "contract_id": contract["contract_id"],
            "contract_version": 1, "table_id": "orders", "environment_name": "dev",
            "catalogue_rows": [], "available_columns": [dict(row) for row in catalogue[1:]],
            "enrichment": [dict(row) for row in enrichment], "guardrails": [dict(row) for row in guardrails],
            "payload": manifest(),
        }

    def manifest():
        return {
            "contract": {"contract_id": "contract-orders", "contract_version": 1, "status": contract["status"]},
            "table": {**catalogue[0], "processing": {}, "columns": [dict(row) for row in catalogue[1:]]},
            "enrichment": {
                "table": [dict(row) for row in enrichment if not row.get("column_id")],
                "columns": [dict(row) for row in enrichment if row.get("column_id")],
            },
            "guardrails": [{**row, "rule_parameters": module._parameters(row)} for row in guardrails if row.get("is_active", True)],
        }

    def save_enrichment(records, **_kwargs):
        calls["enrichment"].append(records)
        for record in records:
            enrichment[:] = [row for row in enrichment if row.get("enrichment_id") != record.get("enrichment_id")]
            if str(record.get("value") or "").strip():
                enrichment.append(dict(record))
        return records

    def save_guardrails(records, **_kwargs):
        calls["guardrails"].append(records)
        for record in records:
            guardrails[:] = [row for row in guardrails if row.get("guardrail_rule_id") != record.get("guardrail_rule_id")]
            guardrails.append(dict(record))
        return records

    def freeze_contract(**_kwargs):
        calls["freeze"] += 1
        contract["status"] = "frozen"
        return {"payload": manifest()}

    def activate_contract_version(**_kwargs):
        calls["activate"] += 1
        contract["status"] = "active"
        return {"changed": True}

    config = types.SimpleNamespace(
        path_config=types.SimpleNamespace(paths={
            "dev": {
                "Bronze": types.SimpleNamespace(kind="lakehouse"),
                "Silver": types.SimpleNamespace(kind="lakehouse"),
                "Gold": types.SimpleNamespace(kind="warehouse"),
                "Metadata": types.SimpleNamespace(kind="lakehouse"),
            }
        }),
        governance_config=types.SimpleNamespace(
            ai_enrichment=ai_enrichment,
            sensitivity_labels=["Public", "Internal", "Confidential", "Restricted"],
        ),
    )
    monkeypatch.setattr(module, "resolve_fabric_context", lambda **_kwargs: (config, "dev", {}))
    monkeypatch.setattr(module, "get_spark_session", lambda _session: object())
    monkeypatch.setattr(module, "discover_scheduled_refresh", lambda **_kwargs: schedule)
    monkeypatch.setattr(module.shared, "require_ipywidgets", lambda: ipywidgets)
    monkeypatch.setattr(module.contracts, "list_contract_governance_state", lambda **_kwargs: {"tables": [catalogue[0]], "contracts": [contract]})
    monkeypatch.setattr(module.contracts, "get_contract_review_state", review)
    monkeypatch.setattr(module.contracts, "build_contract_manifest", lambda **_kwargs: (manifest(), []))
    monkeypatch.setattr(module.contracts, "assemble_contract_payload", lambda **_kwargs: (manifest(), []))
    monkeypatch.setattr(module.contracts, "save_enrichment", save_enrichment)
    monkeypatch.setattr(module.contracts, "save_guardrails", save_guardrails)
    monkeypatch.setattr(module.contracts, "freeze_contract", freeze_contract)
    monkeypatch.setattr(module.contracts, "activate_contract_version", activate_contract_version)
    monkeypatch.setattr(module.contracts, "get_column_profile_context", lambda column_id, **_kwargs: calls["profiles"].append(column_id) or {
        "kind": "values",
        "profile": {
            "row_count": 10, "non_null_count": 9, "null_count": 1,
            "null_percent": 10.0, "distinct_count": 8, "distinct_percent": 80.0,
            "min_value": "ORD-1", "max_value": "ORD-9",
        },
        "values": [{"value": column_id, "count": 2}],
    })
    display_module = types.SimpleNamespace(display=lambda *_args, **_kwargs: None)
    monkeypatch.setitem(
        sys.modules, "IPython",
        types.SimpleNamespace(display=display_module, get_ipython=lambda: None),
    )
    def start():
        return module.widget_data_contract(table_id="orders", contract_version=1)

    def open_widget():
        state = start()
        state["_controls"]["open"].click()
        return state

    return {
        "start": start, "open": open_widget,
        "calls": calls, "contract": contract, "catalogue": catalogue,
        "guardrails": guardrails, "schedule": schedule,
        "ai_enrichment": ai_enrichment,
    }


def test_selector_is_explicit_and_pending_selection_cannot_change_active_contract(widget_runtime):
    """The editor stays inactive until Open and Change table deactivates the current contract."""
    state = widget_runtime["start"]()
    controls = state["_controls"]

    assert state["current"] is None
    assert state["table_id"] is None
    assert state["pending_table_id"] == "orders"
    assert controls["store"].value == "Silver"
    assert "Silver · Lakehouse" in [label for label, _value in controls["store"].options]
    assert controls["schema"].value == "sales"
    assert controls["selector_panel"].layout.display != "none"
    assert controls["editor_shell"].layout.display == "none"

    controls["open"].click()
    assert state["current"]["table_id"] == "orders"
    assert state["table_id"] == "orders"
    assert controls["selector_panel"].layout.display == "none"
    assert controls["editor_shell"].layout.display == ""

    controls["change_table"].click()
    assert state["current"] is None
    assert state["table_id"] is None
    assert controls["selector_panel"].layout.display == ""
    assert controls["editor_shell"].layout.display == "none"


def test_manifest_view_exposes_exact_canonical_dictionary_and_escapes_html():
    """Human review and notebook variables share an escaped canonical object."""
    payload = {
        "contract": {"contract_id": "contract-1", "contract_version": 2, "status": "frozen"},
        "table": {"schema_name": "<demo>", "table_name": "orders", "columns": [], "processing": {}},
        "enrichment": {"table": [], "columns": []}, "guardrails": [],
    }
    rendered = module._manifest_html(payload)
    assert module.DATA_CONTRACT_MANIFEST is payload
    assert json.loads(module.DATA_CONTRACT_MANIFEST_JSON) == payload
    assert "Exact JSON manifest" in rendered
    assert "&lt;demo&gt;" in rendered
    assert "<demo>" not in rendered


def test_profile_context_rendering_priority_and_escaping():
    """Persisted frequencies, ranges, and unavailable states render distinctly."""
    rendered = module._profile_html({"kind": "values", "values": [{"value": "<Ready>", "count": 3}]})
    assert "Observed values" in rendered and "&lt;Ready&gt;" in rendered
    assert "Observed range" in module._profile_html({"kind": "range", "min": 1, "max": 4})
    assert "No profile values available" in module._profile_html({"kind": "unavailable"})


def test_shared_layout_and_existing_state_hydrate(widget_runtime):
    """The unified page uses shared layout primitives and hydrates all main editors."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    assert "fabricops-form" in controls["page"]._dom_classes
    assert tuple(controls["top_nav"].options) == ("Table", "Columns", "Advanced", "Review")
    assert controls["workspace"].layout.grid_template_columns == "minmax(250px, 27fr) minmax(0, 73fr)"
    assert len(controls["workspace"].children) == 2
    assert controls["table"].value == "orders"
    assert controls["contract"].value == "1"
    assert controls["table_description"].value == "Orders table"
    assert controls["table_classification"].value == "Internal"
    assert controls["column_description"].value == "Order identifier"
    assert controls["column_classification"].value == "Confidential"
    assert controls["required"].value is True
    assert controls["table_guardrails"]["freshness"]["enabled"].value is True
    assert controls["table_guardrails"]["source_drift"]["enabled"].value is True
    assert controls["table_guardrails"]["source_drift"]["parameters"][2].value == "append"
    assert controls["sensitive_enabled"].value is True
    assert controls["dq_type"].value == "completeness"
    assert controls["advanced_type"].value == "uniqueness"
    assert "Schedule discovery unavailable" in controls["pipeline_refresh"].value
    assert "read-only" in controls["pipeline_refresh"].value


def test_v38_top_navigation_switches_one_two_pane_workspace(widget_runtime):
    """Use the prototype contract: top nav plus one 27/73 left/right workspace."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    for label in ("Table", "Columns", "Advanced", "Review"):
        controls["top_nav"].value = label
        assert len(controls["left_pane"].children) > 0
        assert len(controls["right_pane"].children) > 0

    controls["top_nav"].value = "Table"
    table_summary = controls["left_pane"].children[0].value
    assert "Loading Strategy" in table_summary
    assert "Refresh Frequency" in table_summary
    assert "Classification" in table_summary
    assert "Guardrails" in table_summary
    assert controls["table_save"].description == "Apply Table Changes"

    controls["top_nav"].value = "Columns"
    assert controls["column_search"] in controls["left_pane"].children
    assert controls["dq_panel"].children[1].layout.grid_template_columns == (
        "minmax(190px, 32fr) minmax(0, 68fr)"
    )
    assert controls["save_column"].description == "Apply Column Changes"

    controls["top_nav"].value = "Advanced"
    assert controls["advanced_type"] in controls["left_pane"].children
    controls["top_nav"].value = "Review"
    assert controls["manifest_nav"] in controls["left_pane"].children


def test_scheduled_refresh_renders_all_discovered_times_and_timezone(widget_runtime):
    """Operational context shows every read-only schedule without adding an editor."""
    widget_runtime["schedule"].update({
        "status": "configured",
        "schedules": [
            {"enabled": True, "frequency": "daily", "times": ["08:00"], "timezone": "Asia/Singapore"},
            {"enabled": False, "frequency": "weekly", "times": ["09:30"], "timezone": "UTC"},
        ],
    })

    state = widget_runtime["open"]()
    rendered = state["_controls"]["pipeline_refresh"].value

    assert "Daily · 08:00 · Asia/Singapore" in rendered
    assert "Weekly · 09:30 · UTC · Disabled" in rendered
    assert "Discovered from Fabric · read-only" in rendered
    assert not hasattr(state["_controls"]["pipeline_refresh"], "on_submit")


def test_no_scheduled_refresh_is_calm_and_does_not_affect_persistence(widget_runtime):
    """No Fabric schedule remains non-fatal and canonical save records stay unchanged."""
    widget_runtime["schedule"].update({"status": "not_configured", "schedules": []})
    state = widget_runtime["open"]()
    assert "No schedule configured" in state["_controls"]["pipeline_refresh"].value

    state["_controls"]["table_description"].value = "Still governed"
    state["_controls"]["table_save"].click()
    assert widget_runtime["calls"]["enrichment"] == []

    state["_controls"]["save_data_contract"].click()
    saved = widget_runtime["calls"]["enrichment"][-1]
    assert all("scheduled_refresh" not in record for record in saved)


def test_profile_context_is_lazy_and_cached_per_table_and_column(widget_runtime):
    """Profile evidence loads only when Columns is opened, then reuses the per-column cache."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    assert widget_runtime["calls"]["profiles"] == []

    controls["top_nav"].value = "Columns"
    assert widget_runtime["calls"]["profiles"].count("col-0") == 1

    controls["column_select"].value = "col-1"
    assert widget_runtime["calls"]["profiles"].count("col-1") == 1

    controls["column_select"].value = "col-0"
    assert widget_runtime["calls"]["profiles"].count("col-0") == 1

    state["load_profile_context"]("col-0")
    assert widget_runtime["calls"]["profiles"].count("col-0") == 1
    assert ("orders", "col-0") in state["_profile_cache"]


def test_column_selection_reuses_one_editor_and_refreshes_profile(widget_runtime):
    """Large schemas remain bounded and column selection rehydrates a single editor."""
    widget_runtime["catalogue"][:] = _catalogue_rows(250)
    state = widget_runtime["open"]()
    controls = state["_controls"]
    editor_identity = id(controls["column_description"])
    controls["column_select"].value = "col-249"
    assert id(controls["column_description"]) == editor_identity
    assert "column_249" in controls["column_context"].value
    assert widget_runtime["calls"]["profiles"] == []
    controls["top_nav"].value = "Columns"
    assert "col-249" in controls["profile_context"].value
    assert widget_runtime["calls"]["profiles"][-1] == "col-249"
    assert controls["left_pane"].children[-1] is controls["column_select"]
    assert controls["column_search"] in controls["left_pane"].children
    assert controls["workspace"].layout.grid_template_columns == "minmax(250px, 27fr) minmax(0, 73fr)"


def test_column_without_dq_rule_resets_editor_instead_of_leaking_prior_rule(widget_runtime):
    """Selecting an unconfigured column must not retain another column's DQ values."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    assert controls["dq_type"].value == "completeness"
    assert controls["dq_max_missing"].value == "0"
    assert controls["dq_action"].value == "Block"

    controls["column_select"].value = "col-1"

    assert controls["dq_type"].value == "completeness"
    assert controls["dq_max_missing"].value == "0"
    assert controls["dq_action"].value == "Warn"


def test_unsaved_column_edits_survive_an_unrelated_save_rerender(widget_runtime):
    """Per-column drafts live in widget state rather than one disposable render closure."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["column_select"].value = "col-1"
    controls["column_description"].value = "Unsaved local description"
    controls["column_select"].value = "col-0"

    controls["table_description"].value = "Saved table description"
    controls["table_save"].click()
    state["_controls"]["column_select"].value = "col-1"

    assert state["_controls"]["column_description"].value == "Unsaved local description"


def test_final_save_clears_stale_local_draft_after_one_canonical_reload(widget_runtime):
    """Final Data Contract save persists staged column state then reloads canonical values once."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["column_description"].value = "Older local draft"
    controls["column_select"].value = "col-1"
    controls["column_select"].value = "col-0"
    controls["column_description"].value = "Canonical saved description"
    controls["save_column"].click()

    assert widget_runtime["calls"]["enrichment"] == []
    assert state["dirty"] is True

    state["_controls"]["save_data_contract"].click()
    assert widget_runtime["calls"]["enrichment"]
    assert state["dirty"] is False
    assert state["_controls"]["column_description"].value == "Canonical saved description"


def test_section_actions_stage_without_writes_until_final_save(widget_runtime):
    """Table and column Apply actions stay local; Review save persists once."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["table_description"].value = "Governed orders"
    controls["table_save"].click()
    controls["column_description"].value = "Canonical ID"
    controls["save_column_enrichment"].click()
    controls["required"].value = False
    controls["save_required"].click()

    assert widget_runtime["calls"]["enrichment"] == []
    assert widget_runtime["calls"]["guardrails"] == []
    assert state["dirty"] is True

    controls["save_data_contract"].click()

    assert len(widget_runtime["calls"]["enrichment"]) == 1
    assert len(widget_runtime["calls"]["guardrails"]) == 1
    assert any(
        record.get("value") == "Governed orders"
        for record in widget_runtime["calls"]["enrichment"][0]
    )
    assert any(
        module._parameters(record).get("required_columns") == []
        for record in widget_runtime["calls"]["guardrails"][0]
        if record.get("guardrail_type") == "schema"
    )
    assert state["dirty"] is False
    assert "canonical state reloaded" in state["message"]


def test_visible_apply_actions_stage_table_and_column_sections(widget_runtime):
    """Visible section actions update session state without partial persistence."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["table_description"].value = "Unified table save"
    controls["table_save"].click()
    controls["column_description"].value = "Unified column save"
    controls["pii_reason"].value = "Direct identifier for a person."
    controls["save_column"].click()

    assert widget_runtime["calls"]["enrichment"] == []
    assert widget_runtime["calls"]["guardrails"] == []
    assert state["_pending_enrichment"]
    assert state["_pending_guardrails"]

    controls["save_data_contract"].click()
    assert len(widget_runtime["calls"]["enrichment"]) == 1
    assert len(widget_runtime["calls"]["guardrails"]) == 1


def test_discard_changes_restores_canonical_state_without_writes(widget_runtime):
    """Discard clears staged session changes and reloads canonical state without persistence."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["table_description"].value = "Unsaved table change"
    controls["table_save"].click()
    assert state["dirty"] is True
    assert widget_runtime["calls"]["enrichment"] == []

    controls["discard_data_contract"].click()

    assert state["dirty"] is False
    assert widget_runtime["calls"]["enrichment"] == []
    assert widget_runtime["calls"]["guardrails"] == []
    assert state["_controls"]["table_description"].value == "Orders table"
    assert "discarded" in state["message"]


def test_guardrail_apply_actions_stage_then_final_save_persists(widget_runtime):
    """Guardrail editors stage normalized records and persist them only at final save."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["table_guardrails"]["freshness"]["block"].value = False
    controls["table_guardrails"]["freshness"]["save"].click()
    controls["table_guardrails"]["source_drift"]["save"].click()

    controls["sensitive_enabled"].value = True
    controls["sensitive_treatment"].value = "tokenize"
    controls["pii_reason"].value = "The identifier directly associates an order with a person."
    controls["save_sensitive"].click()

    controls["dq_type"].value = "completeness"
    controls["dq_blank_missing"].value = True
    controls["save_dq"].click()

    controls["advanced_type"].value = "column_relationship"
    controls["advanced_columns"].value = ("column_0", "column_1")
    controls["advanced_save"].click()

    assert widget_runtime["calls"]["guardrails"] == []
    assert state["_pending_guardrails"]

    controls["save_data_contract"].click()
    saved = widget_runtime["calls"]["guardrails"][-1]

    by_type = {record["guardrail_type"] for record in saved}
    assert {"freshness", "source_drift", "sensitive_data", "data_quality"} <= by_type
    assert any(
        record["rule_type"] == "completeness"
        and module._parameters(record)["treat_blank_as_missing"] is True
        for record in saved
    )
    assert any(
        record["rule_type"] == "column_relationship"
        and module._parameters(record)["columns"] == ["column_0", "column_1"]
        for record in saved
    )


def _enable_ai(widget_runtime, monkeypatch, *, captures=None):
    """Enable deterministic AI responses for widget interaction tests."""
    widget_runtime["ai_enrichment"]["enabled"] = True
    captures = captures if captures is not None else {"enrichment": [], "sensitive": []}

    def enrichment(context, **_kwargs):
        captures["enrichment"].append(context)
        level = context["metadata_level"]
        return {"Description": f"Suggested {level} description"}

    def sensitive(context, **_kwargs):
        captures["sensitive"].append(context)
        column = context["columns"][0]
        return [{
            "column_name": column["column_name"], "column_id": column["column_id"],
            "pii_type": "direct", "pii_label": "Direct PII",
            "reason": "Can uniquely associate a person.", "treatment": "mask",
            "action": "Block",
            "parameters": {"preserve_start": 1, "preserve_end": 0, "mask_character": "*"},
            "is_active": True,
        }]

    monkeypatch.setattr(module, "suggest_enrichment", enrichment)
    monkeypatch.setattr(module, "suggest_sensitive_data", sensitive)
    return captures


def _open_with_ai(widget_runtime, monkeypatch, *, captures=None):
    """Open one contract and explicitly opt in to scoped AI suggestions."""
    captures = _enable_ai(widget_runtime, monkeypatch, captures=captures)
    state = widget_runtime["open"]()
    state["_controls"]["run_with_ai"].click()
    return state, captures


def test_sensitive_ai_is_disabled_by_configuration(widget_runtime):
    """AI-disabled authoring keeps every manual editor available."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    assert controls["rerun_sensitive"].disabled is True
    assert controls["column_description"].disabled is False
    assert controls["save_column_enrichment"].disabled is False
    assert all(not drafts for drafts in state["_column_drafts"].values())


def test_ai_startup_is_explicit_and_scoped_to_current_table_and_column(widget_runtime, monkeypatch):
    """Opening is immediate; AI runs only after explicit opt-in for the selected contract."""
    captures = _enable_ai(widget_runtime, monkeypatch)
    state = widget_runtime["open"]()
    controls = state["_controls"]

    assert captures["enrichment"] == []
    assert captures["sensitive"] == []
    assert "Choose Run with AI suggestions" in controls["column_description_ai"].value

    controls["run_without_ai"].click()
    assert captures["enrichment"] == []
    assert captures["sensitive"] == []
    assert "without AI" in state["message"]

    state["_controls"]["run_with_ai"].click()
    controls = state["_controls"]
    assert len(captures["enrichment"]) == 2  # selected table plus currently opened column
    assert len(captures["sensitive"]) == 1
    assert all(not drafts for drafts in state["_column_drafts"].values())
    assert state["_ai_suggestions"]
    assert "Suggested column description" in controls["column_description_ai"].value
    assert "Direct PII" in controls["sensitive_ai"].value
    assert widget_runtime["calls"]["enrichment"] == []
    assert widget_runtime["calls"]["guardrails"] == []


def test_accept_actions_modify_only_their_owned_controls(widget_runtime, monkeypatch):
    """Description and Sensitive Data acceptance stay isolated from manual Classification."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    controls["required"].value = False
    controls["dq_type"].value = "pattern"
    controls["dq_pattern"].value = "manual-pattern"

    original_classification = controls["column_classification"].value
    controls["accept_column_description"].click()
    assert controls["column_description"].value == "Suggested column description"
    assert controls["column_classification"].value == original_classification
    assert controls["required"].value is False
    assert controls["dq_pattern"].value == "manual-pattern"

    description = controls["column_description"].value
    controls["accept_sensitive"].click()
    assert controls["pii_type"].value == "direct"
    assert controls["sensitive_treatment"].value == "mask"
    assert controls["sensitive_action"].value == "Block"
    assert controls["column_description"].value == description
    assert controls["column_classification"].value == "Confidential"
    assert controls["required"].value is False
    assert controls["dq_type"].value == "pattern"
    assert controls["dq_pattern"].value == "manual-pattern"
    assert widget_runtime["calls"]["guardrails"] == []

    controls["save_sensitive"].click()
    assert widget_runtime["calls"]["guardrails"] == []
    controls["save_data_contract"].click()
    saved_sensitive = next(
        record for record in widget_runtime["calls"]["guardrails"][-1]
        if record.get("guardrail_type") == "sensitive_data"
    )
    saved_parameters = module._parameters(saved_sensitive)
    assert saved_parameters["pii_type"] == "direct"
    assert saved_parameters["pii_reason"] == "Can uniquely associate a person."


def test_sensitive_pii_assessment_requires_reason_before_save(widget_runtime):
    """Do not silently discard a reviewed Direct or Indirect PII assessment."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["pii_type"].value = "indirect"
    controls["pii_reason"].value = ""
    before = len(widget_runtime["calls"]["guardrails"])

    controls["save_sensitive"].click()

    assert len(widget_runtime["calls"]["guardrails"]) == before
    assert "Explain why this column is Direct or Indirect PII." in state["message"]


def test_sensitive_generation_preserves_existing_unsaved_column_draft(widget_runtime, monkeypatch):
    """Regress PR 1375: PII generation never overwrites unrelated draft fields."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    controls["column_description"].value = "Unsaved description"
    controls["column_classification"].value = "Restricted"
    controls["dq_type"].value = "pattern"
    controls["dq_pattern"].value = "keep-me"
    controls["column_select"].value = "col-1"
    controls["column_select"].value = "col-0"

    controls["rerun_sensitive"].click()

    assert controls["column_description"].value == "Unsaved description"
    assert controls["column_classification"].value == "Restricted"
    assert controls["dq_type"].value == "pattern"
    assert controls["dq_pattern"].value == "keep-me"


def test_switching_columns_preserves_suggestions_and_drafts(widget_runtime, monkeypatch):
    """Lazy suggestions and user drafts survive bounded column navigation."""
    state, captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    controls["column_description"].value = "First draft"
    controls["column_select"].value = "col-1"
    controls["column_description"].value = "Second draft"
    controls["column_select"].value = "col-0"

    assert controls["column_description"].value == "First draft"
    assert set(next(iter(state["_ai_suggestions"].values()))["columns"]) == {"col-0", "col-1"}
    calls_before = len(captures["sensitive"])
    controls["column_select"].value = "col-1"
    assert controls["column_description"].value == "Second draft"
    assert len(captures["sensitive"]) == calls_before


def test_manual_enrichment_changes_mark_dependent_suggestions_stale(widget_runtime, monkeypatch):
    """Manual Description and Classification edits mark Sensitive Data advice stale."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    controls["column_description"].value = "Manual description"
    assert "Needs refresh" in controls["sensitive_ai"].value
    controls["rerun_sensitive"].click()
    assert "Needs refresh" not in controls["sensitive_ai"].value
    controls["column_classification"].value = "Restricted"
    assert "Needs refresh" in controls["sensitive_ai"].value


def test_rerun_uses_current_editable_context_and_never_persists(widget_runtime, monkeypatch):
    """Explicit refresh reads unsaved Enrichment values without invoking save paths."""
    state, captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    controls["column_description"].value = "Current unsaved description"
    controls["column_classification"].value = "Restricted"
    controls["rerun_column_description"].click()
    controls["rerun_sensitive"].click()

    assert captures["enrichment"][-1]["existing_description"] == "Current unsaved description"
    sensitive_column = captures["sensitive"][-1]["columns"][0]
    assert sensitive_column["description"] == "Current unsaved description"
    assert sensitive_column["classification"] == "Restricted"
    assert widget_runtime["calls"]["enrichment"] == []
    assert widget_runtime["calls"]["guardrails"] == []


def test_ai_failure_is_non_blocking(widget_runtime, monkeypatch):
    """Unavailable Fabric AI reports status while preserving manual authoring."""
    widget_runtime["ai_enrichment"]["enabled"] = True
    monkeypatch.setattr(
        module, "suggest_enrichment",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("AI Functions unavailable")),
    )
    monkeypatch.setattr(
        module, "suggest_sensitive_data",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("malformed AI response")),
    )
    state = widget_runtime["open"]()
    assert all(not errors for errors in state["_ai_errors"].values())
    state["_controls"]["run_with_ai"].click()
    controls = state["_controls"]
    assert controls["column_description"].disabled is False
    controls["column_description"].value = "Manual still works"
    controls["save_column_enrichment"].click()
    assert widget_runtime["calls"]["enrichment"]
    assert state["_ai_errors"]


def test_immutable_contract_does_not_run_authoring_ai(widget_runtime, monkeypatch):
    """Frozen review-only versions never invoke authoring AI."""
    widget_runtime["contract"]["status"] = "frozen"
    widget_runtime["ai_enrichment"]["enabled"] = True
    monkeypatch.setattr(
        module, "suggest_enrichment", lambda *_args, **_kwargs: pytest.fail("AI must not run")
    )
    monkeypatch.setattr(
        module, "suggest_sensitive_data", lambda *_args, **_kwargs: pytest.fail("AI must not run")
    )
    state = widget_runtime["open"]()
    assert state["_controls"]["rerun_sensitive"].disabled is True


def test_new_table_guardrails_require_and_save_canonical_parameters(widget_runtime):
    """New Freshness and Source Drift rules cannot be persisted with empty parameters."""
    widget_runtime["guardrails"][:] = [
        rule for rule in widget_runtime["guardrails"]
        if rule["guardrail_type"] not in {"freshness", "source_drift"}
    ]
    state = widget_runtime["open"]()
    freshness = state["_controls"]["table_guardrails"]["freshness"]
    freshness["enabled"].value = True
    before = len(widget_runtime["calls"]["guardrails"])
    freshness["save"].click()
    assert len(widget_runtime["calls"]["guardrails"]) == before
    assert "could not convert string to float" in state["message"]

    freshness["parameters"][0].value = "column_1"
    freshness["parameters"][1].value = "6"
    freshness["parameters"][2].value = "hours"
    freshness["save"].click()
    saved = widget_runtime["calls"]["guardrails"][-1][0]
    assert module._parameters(saved) == {
        "freshness_column": "column_1", "maximum_age": 6.0, "maximum_age_unit": "hours",
    }

    drift = state["_controls"]["table_guardrails"]["source_drift"]
    drift["enabled"].value = True
    drift["parameters"][0].value = "column_0"
    drift["parameters"][1].value = "column_1"
    drift["save"].click()
    assert module._parameters(widget_runtime["calls"]["guardrails"][-1][0]) == {
        "partition_column": "column_0", "change_column": "column_1", "load_strategy": "overwrite",
    }


def test_invalid_dq_input_is_reported_in_status_without_persisting(widget_runtime):
    """Parameter conversion failures remain inside the widget error boundary."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    before = len(widget_runtime["calls"]["guardrails"])
    controls["dq_type"].value = "completeness"
    controls["dq_max_missing"].value = "not-a-number"

    controls["save_dq"].click()

    assert len(widget_runtime["calls"]["guardrails"]) == before
    assert "could not convert string to float" in state["message"]
    assert "#a4262c" in controls["status"].value


def test_column_dq_family_change_hydrates_its_own_saved_configuration(widget_runtime):
    """Keep multiple rules on one column independently editable and update the matching record."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    assert controls["dq_type"].value == "completeness"
    assert controls["dq_max_missing"].value == "0"

    controls["dq_type"].value = "pattern"

    assert controls["dq_pattern"].value == "^ORD-[0-9]+$"
    assert controls["dq_action"].value == "Warn"
    controls["dq_pattern"].value = "^ORDER-[0-9]+$"
    controls["save_dq"].click()
    saved = widget_runtime["calls"]["guardrails"][-1][0]
    assert saved["guardrail_rule_id"] == "dq-pattern"
    assert module._parameters(saved)["pattern"] == "^ORDER-[0-9]+$"


def test_dq_ai_receives_unpacked_profile_and_frequency_evidence(widget_runtime, monkeypatch):
    """Pass governed profile statistics and bounded frequencies into DQ suggestions."""
    _enable_ai(widget_runtime, monkeypatch)
    captured = {}

    def suggest(context, **_kwargs):
        captured.update(context)
        return []

    monkeypatch.setattr(module, "suggest_dq_rules", suggest)
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    state["_controls"]["suggest_dq"].click()

    column = captured["columns"][0]
    assert column["profile_evidence"] == {
        "row_count": 10, "non_null_count": 9, "null_count": 1,
        "null_percent": 10.0, "distinct_count": 8, "distinct_percent": 80.0,
        "min_value": "ORD-1", "max_value": "ORD-9",
    }
    assert column["frequency_evidence"] == [{"value": "col-0", "count": 2}]


def test_review_sections_separate_table_dq_categories_from_column_rules():
    """Render the Review hierarchy without duplicating every Guardrail in two sections."""
    payload = {
        "table": {"table_name": "orders", "schema_name": "sales", "columns": []},
        "contract": {"contract_version": 1, "status": "draft"},
        "enrichment": {"columns": []},
        "guardrails": [
            {"guardrail_type": "freshness", "rule_type": "freshness", "column_id": ""},
            {"guardrail_type": "source_drift", "rule_type": "source_drift", "column_id": ""},
            {"guardrail_type": "data_quality", "rule_type": "uniqueness", "column_id": ""},
            {"guardrail_type": "data_quality", "rule_type": "column_relationship", "column_id": ""},
            {"guardrail_type": "data_quality", "rule_type": "custom_expression", "column_id": ""},
            {"guardrail_type": "data_quality", "rule_type": "pattern", "column_id": "col-1"},
        ],
    }
    sections = module._manifest_sections(payload)

    assert set(sections) == {"Identity", "Table", "Columns", "Lifecycle / Agreement state"}
    assert "Composite Uniqueness" in sections["Table"]
    assert "Column Relationships" in sections["Table"]
    assert "Custom Expressions" in sections["Table"]
    assert "pattern" not in sections["Table"]
    assert "pattern" in sections["Columns"]


def test_ai_range_suggestion_hydrates_edits_and_saves_without_parameter_loss(widget_runtime, monkeypatch):
    """Carry structured AI parameters through explicit acceptance, editing, and persistence."""
    _enable_ai(widget_runtime, monkeypatch)
    monkeypatch.setattr(module, "suggest_dq_rules", lambda *_args, **_kwargs: [{
        "rule_type": "range", "columns": ["column_0"],
        "parameters": {
            "minimum": 0, "minimum_inclusive": True,
            "maximum": 100, "maximum_inclusive": False,
        },
        "rationale": "A governed scale.", "selected": True,
    }])
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    before = len(widget_runtime["calls"]["guardrails"])

    controls["suggest_dq"].click()
    assert len(widget_runtime["calls"]["guardrails"]) == before
    controls["accept_dq_suggestion"].click()
    assert controls["dq_type"].value == "range"
    assert controls["dq_maximum"].value == "100"
    assert controls["dq_maximum_inclusive"].value is False
    controls["dq_minimum"].value = "1"
    controls["save_dq"].click()

    saved = widget_runtime["calls"]["guardrails"][-1][0]
    assert saved["column_id"] == "col-0"
    assert module._parameters(saved) == {
        "columns": ["column_0"], "minimum": "1", "minimum_inclusive": True,
        "maximum": "100", "maximum_inclusive": False,
    }


def test_freeze_activation_manifest_refresh_and_immutable_controls(widget_runtime):
    """Lifecycle actions reload exact state, refresh manifest, and close immutable editors."""
    state = widget_runtime["open"]()
    before = module.DATA_CONTRACT_MANIFEST
    state["_controls"]["freeze"].click()
    assert widget_runtime["calls"]["freeze"] == 1
    assert state["current"]["contract"]["status"] == "frozen"
    assert state["_controls"]["table_description"].disabled is True
    assert module.DATA_CONTRACT_MANIFEST is not before
    state["_controls"]["activate"].click()
    assert widget_runtime["calls"]["activate"] == 1
    assert state["current"]["contract"]["status"] == "active"
    assert "ACTIVE" in state["message"]
