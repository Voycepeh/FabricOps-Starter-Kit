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
        {"guardrail_rule_id": "dq", "guardrail_version": 1, "guardrail_type": "data_quality", "column_id": "col-0", "rule_type": "missing_values", "rule_parameters_json": '{"columns":["column_0"],"maximum_null_percent":0}', "action": "Block", "is_active": True},
        {"guardrail_rule_id": "advanced", "guardrail_version": 1, "guardrail_type": "data_quality", "column_id": "", "rule_type": "compare_columns", "rule_parameters_json": '{"columns":["column_1","column_0"],"operator":">"}', "action": "Warn", "is_active": True},
    ]
    calls = {"enrichment": [], "guardrails": [], "freeze": 0, "activate": 0, "profiles": []}
    schedule = {
        "status": "unavailable", "schedules": [],
        "message": "Scheduled Refresh discovery is unavailable for this notebook.",
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

    monkeypatch.setattr(module, "resolve_fabric_context", lambda **_kwargs: (object(), "dev", {}))
    monkeypatch.setattr(module, "get_spark_session", lambda _session: object())
    monkeypatch.setattr(module, "discover_scheduled_refresh", lambda **_kwargs: schedule)
    monkeypatch.setattr(module.shared, "require_ipywidgets", lambda: ipywidgets)
    monkeypatch.setattr(module.contracts, "list_contract_governance_state", lambda **_kwargs: {"tables": [catalogue[0]], "contracts": [contract]})
    monkeypatch.setattr(module.contracts, "get_contract_review_state", review)
    monkeypatch.setattr(module.contracts, "build_contract_manifest", lambda **_kwargs: (manifest(), []))
    monkeypatch.setattr(module.contracts, "save_enrichment", save_enrichment)
    monkeypatch.setattr(module.contracts, "save_guardrails", save_guardrails)
    monkeypatch.setattr(module.contracts, "freeze_contract", freeze_contract)
    monkeypatch.setattr(module.contracts, "activate_contract_version", activate_contract_version)
    monkeypatch.setattr(module.contracts, "get_column_profile_context", lambda column_id, **_kwargs: calls["profiles"].append(column_id) or {"kind": "values", "values": [{"value": column_id, "count": 2}]})
    display_module = types.SimpleNamespace(display=lambda *_args, **_kwargs: None)
    monkeypatch.setitem(
        sys.modules, "IPython",
        types.SimpleNamespace(display=display_module, get_ipython=lambda: None),
    )
    return {
        "open": lambda: module.widget_data_contract(table_id="orders", contract_version=1),
        "calls": calls, "contract": contract, "catalogue": catalogue,
        "guardrails": guardrails, "schedule": schedule,
    }


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
    assert "fabricops-authoring-workspace" in controls["tabs"].children[1].children[0]._dom_classes
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
    assert controls["dq_type"].value == "missing_values"
    assert controls["advanced_type"].value == "unique_combination"
    assert "Schedule discovery unavailable" in controls["pipeline_refresh"].value
    assert "read-only" in controls["pipeline_refresh"].value


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

    saved = widget_runtime["calls"]["enrichment"][-1]
    assert all("scheduled_refresh" not in record for record in saved)


def test_column_selection_reuses_one_editor_and_refreshes_profile(widget_runtime):
    """Large schemas remain bounded and column selection rehydrates a single editor."""
    widget_runtime["catalogue"][:] = _catalogue_rows(250)
    state = widget_runtime["open"]()
    controls = state["_controls"]
    editor_identity = id(controls["column_description"])
    controls["column_select"].value = "col-249"
    assert id(controls["column_description"]) == editor_identity
    assert "column_249" in controls["column_context"].value
    assert "col-249" in controls["profile_context"].value
    assert widget_runtime["calls"]["profiles"][-1] == "col-249"
    assert controls["tabs"].children[1].children[0].layout.grid_template_columns


def test_column_without_dq_rule_resets_editor_instead_of_leaking_prior_rule(widget_runtime):
    """Selecting an unconfigured column must not retain another column's DQ values."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    assert controls["dq_type"].value == "missing_values"
    assert controls["dq_parameter"].value == "0"
    assert controls["dq_action"].value == "Block"

    controls["column_select"].value = "col-1"

    assert controls["dq_type"].value == "missing_values"
    assert controls["dq_parameter"].value == ""
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


def test_enrichment_and_schema_saves_reload_canonical_state(widget_runtime):
    """Table, column, and required-state actions persist and refresh their controls."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["table_description"].value = "Governed orders"
    controls["table_save"].click()
    assert widget_runtime["calls"]["enrichment"][-1][0]["value"] == "Governed orders"
    assert state["_controls"]["table_description"].value == "Governed orders"
    state["_controls"]["column_description"].value = "Canonical ID"
    state["_controls"]["save_column_enrichment"].click()
    assert widget_runtime["calls"]["enrichment"][-1][0]["column_id"] == "col-0"
    state["_controls"]["required"].value = False
    state["_controls"]["save_required"].click()
    saved = widget_runtime["calls"]["guardrails"][-1][0]
    assert module._parameters(saved)["required_columns"] == []
    assert state["_controls"]["required"].value is False
    assert "refreshed" in state["message"]


def test_table_sensitive_dq_and_advanced_guardrails_persist(widget_runtime):
    """Every logical rule section saves normalized records through Guardrail services."""
    state = widget_runtime["open"]()
    state["_controls"]["table_guardrails"]["freshness"]["block"].value = False
    state["_controls"]["table_guardrails"]["freshness"]["save"].click()
    freshness = widget_runtime["calls"]["guardrails"][-1][0]
    assert freshness["guardrail_type"] == "freshness"
    assert module._parameters(freshness) == {
        "freshness_column": "column_1", "maximum_age": 2.0, "maximum_age_unit": "days",
    }
    state["_controls"]["table_guardrails"]["source_drift"]["save"].click()
    drift = widget_runtime["calls"]["guardrails"][-1][0]
    assert drift["guardrail_type"] == "source_drift"
    assert module._parameters(drift) == {
        "partition_column": "column_0", "change_column": "column_1",
    }
    state["_controls"]["sensitive_enabled"].value = True
    state["_controls"]["sensitive_treatment"].value = "tokenize"
    state["_controls"]["save_sensitive"].click()
    assert widget_runtime["calls"]["guardrails"][-1][0]["guardrail_type"] == "sensitive_data"
    state["_controls"]["dq_type"].value = "blank_text"
    state["_controls"]["save_dq"].click()
    assert widget_runtime["calls"]["guardrails"][-1][0]["rule_type"] == "blank_text"
    state["_controls"]["advanced_type"].value = "compare_columns"
    state["_controls"]["advanced_columns"].value = ("column_0", "column_1")
    state["_controls"]["advanced_save"].click()
    assert module._parameters(widget_runtime["calls"]["guardrails"][-1][0])["columns"] == ["column_0", "column_1"]


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
        "partition_column": "column_0", "change_column": "column_1",
    }


def test_invalid_dq_input_is_reported_in_status_without_persisting(widget_runtime):
    """Parameter conversion failures remain inside the widget error boundary."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    before = len(widget_runtime["calls"]["guardrails"])
    controls["dq_type"].value = "missing_values"
    controls["dq_parameter"].value = "not-a-number"

    controls["save_dq"].click()

    assert len(widget_runtime["calls"]["guardrails"]) == before
    assert "could not convert string to float" in state["message"]
    assert "#a4262c" in controls["status"].value


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
