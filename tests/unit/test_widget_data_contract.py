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
        "table_id": "orders", "workspace_id": "dev", "metadata_level": "table",
        "schema_name": "sales", "table_name": "orders", "store_type": "Lakehouse",
        "layer": "Silver", "load_strategy": "append",
        "load_strategy_parameters_json": {}, "is_active": True,
        "_workspace_id": "workspace-id", "_workspace_name": "Development",
        "_notebook_id": "writer-notebook-id",
    }]
    for index in range(count):
        rows.append({
            "table_id": "orders", "workspace_id": "dev", "metadata_level": "column",
            "column_id": f"col-{index}", "column_name": f"column_{index}",
            "data_type": (
                "long" if index == 0 else "timestamp" if index == 1 else "string"
            ), "is_active": True,
        })
    return rows


def _use_text_identifier(runtime):
    """Use a categorical identifier when exercising mask-specific controls."""
    runtime["catalogue"][1]["data_type"] = "string"
    payload = json.loads(runtime["contract"]["contract_payload_json"])
    payload["table"]["columns"][0]["data_type"] = "string"
    runtime["contract"]["contract_payload_json"] = json.dumps(payload)
    sensitive = next(row for row in runtime["guardrails"] if row.get("guardrail_type") == "sensitive_data")
    sensitive.update({"rule_type": "mask", "rule_parameters_json": json.dumps({
        "scope": "column", "treatment": "mask", "preserve_start": 0, "preserve_end": 0, "mask_character": "*",
    })})


def _capture_fixture_columns(runtime):
    """Simulate creating a draft after the test's Engineering schema change."""
    payload = json.loads(runtime["contract"]["contract_payload_json"])
    payload["table"]["columns"] = [{**row, "presence": "required"} for row in runtime["catalogue"][1:]]
    runtime["contract"]["contract_payload_json"] = json.dumps(payload)


@pytest.fixture
def widget_runtime(monkeypatch):
    """Provide mutable canonical service state behind the real ipywidgets controls."""
    models = {}
    class Layout(types.SimpleNamespace):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            models[id(self)] = self
            self.closed = False

        def close(self):
            self.closed = True
            models.pop(id(self), None)

    class Widget:
        def __init__(self, value=None, options=(), description="", disabled=False, layout=None, **kwargs):
            models[id(self)] = self
            self.closed = False
            self._observers = []
            self._dom_classes = []
            self.description = description
            self.placeholder = kwargs.get("placeholder", "")
            self.tooltip = kwargs.get("tooltip", "")
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

        def remove_class(self, name):
            if name in self._dom_classes:
                self._dom_classes.remove(name)

        def close(self):
            self.closed = True
            models.pop(id(self), None)

    class Dropdown(Widget):
        @Widget.value.setter
        def value(self, value):
            values = self._option_values(self._options)
            if value is not None and value not in values:
                raise ValueError("Invalid selection: value not found")
            old = self._value
            self._value = value
            if old != value:
                for callback in list(self._observers):
                    callback({"old": old, "new": value, "name": "value"})

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
        Layout=lambda **kwargs: Layout(**kwargs), HTML=Widget, Text=Widget, Textarea=Widget, IntText=Widget,
        Dropdown=Dropdown, Combobox=Widget, Checkbox=Widget, Select=Widget, SelectMultiple=Widget,
        ToggleButtons=Widget, ToggleButton=Widget,
        Button=Button, VBox=Box, HBox=Box, GridBox=Box, Tab=Tab,
    )
    catalogue = _catalogue_rows()
    catalogue[0]["scheduled_refresh_json"] = {
        "status": "configured",
        "schedules": [{
            "enabled": True, "frequency": "daily", "times": ["08:00"],
            "timezone": "Asia/Singapore",
        }],
    }
    contract_payload = {
        "contract": {
            "contract_id": "contract-orders", "contract_version": 1, "status": "draft",
        },
        "table": {
            **catalogue[0],
            "processing": {"load_strategy": "append"},
            "processing_source": "catalogue",
            "columns": [{**row, "presence": "required" if index == 0 else "optional"} for index, row in enumerate(catalogue[1:])],
        },
        "enrichment": {"table": [], "columns": []},
        "guardrails": [],
    }
    contract = {
        "contract_id": "contract-orders", "contract_version": 1, "table_id": "orders",
        "workspace_id": "dev",
        "contract_payload_json": json.dumps(contract_payload, sort_keys=True, separators=(",", ":")),
        "status": "draft", "is_active": False,
    }
    enrichment = [
        {"enrichment_id": "table-description", "contract_id": "contract-orders", "contract_version": 1, "workspace_id": "dev", "enrichment_level": "table", "column_id": "", "enrichment_type": "Description", "value": "Orders table"},
        {"enrichment_id": "table-classification", "contract_id": "contract-orders", "contract_version": 1, "workspace_id": "dev", "enrichment_level": "table", "column_id": "", "enrichment_type": "Classification", "value": "Restricted"},
        {"enrichment_id": "column-description", "contract_id": "contract-orders", "contract_version": 1, "workspace_id": "dev", "enrichment_level": "column", "column_id": "col-0", "enrichment_type": "Description", "value": "Order identifier"},
        {"enrichment_id": "column-classification", "contract_id": "contract-orders", "contract_version": 1, "workspace_id": "dev", "enrichment_level": "column", "column_id": "col-0", "enrichment_type": "Classification", "value": "Confidential"},
    ]
    guardrails = [
        {"guardrail_rule_id": "schema", "guardrail_version": 1, "guardrail_type": "schema", "rule_type": "required_columns", "rule_parameters_json": '{"required_columns":["col-0"]}', "action": "Block", "is_active": True},
        {"guardrail_rule_id": "fresh", "guardrail_version": 1, "guardrail_type": "freshness", "rule_type": "freshness", "rule_parameters_json": '{"freshness_column":"column_1","expected_refresh_frequency":1,"expected_refresh_unit":"days","maximum_age":2,"maximum_age_unit":"days"}', "action": "Block", "is_active": True},
        {"guardrail_rule_id": "drift", "guardrail_version": 1, "guardrail_type": "source_drift", "rule_type": "source_drift", "rule_parameters_json": '{"partition_column":"column_0","change_column":"column_1"}', "action": "Warn", "is_active": True},
        {"guardrail_rule_id": "sensitive", "guardrail_version": 1, "guardrail_type": "sensitive_data", "column_id": "col-0", "rule_type": "tokenize", "rule_parameters_json": '{"scope":"column","treatment":"tokenize"}', "action": "Block", "is_active": True},
        {"guardrail_rule_id": "dq", "guardrail_version": 1, "guardrail_type": "data_quality", "column_id": "col-0", "rule_type": "completeness", "rule_parameters_json": '{"columns":["column_0"],"maximum_missing_percent":0,"treat_blank_as_missing":false}', "action": "Block", "is_active": True},
        {"guardrail_rule_id": "dq-pattern", "guardrail_version": 1, "guardrail_type": "data_quality", "column_id": "col-0", "rule_type": "pattern", "rule_parameters_json": '{"columns":["column_0"],"pattern":"^ORD-[0-9]+$"}', "action": "Warn", "is_active": True},
        {"guardrail_rule_id": "advanced", "guardrail_version": 1, "guardrail_type": "data_quality", "column_id": "", "rule_type": "column_relationship", "rule_parameters_json": '{"columns":["column_1","column_0"],"operator":">"}', "action": "Warn", "is_active": True},
    ]
    for row in guardrails:
        row.update({
            "contract_id": "contract-orders",
            "contract_version": 1,
            "workspace_id": "dev",
        })
    calls = {"draft": [], "enrichment": [], "guardrails": [], "freeze": 0, "activate": 0, "profiles": []}
    class ScheduleState(dict):
        def update(self, *args, **kwargs):
            super().update(*args, **kwargs)
            catalogue[0]["scheduled_refresh_json"] = dict(self)

    schedule = ScheduleState(catalogue[0]["scheduled_refresh_json"])
    ai_enrichment = {
        "enabled": False,
        "table_description_prompt": "configured table description prompt",
        "column_description_prompt": "configured column description prompt",
        "sensitive_data_prompt": "configured sensitive prompt",
        "grain_prompt": "configured grain prompt",
        "business_rule_prompt": "configured business rule prompt",
    }

    def review(**_kwargs):
        if contract["status"] == "draft":
            return {
                "contract": dict(contract), "contract_id": contract["contract_id"],
                "contract_version": 1, "table_id": "orders", "workspace_id": "dev",
                "catalogue_rows": [dict(row) for row in catalogue],
                "available_columns": json.loads(contract["contract_payload_json"])["table"]["columns"],
                "enrichment": [dict(row) for row in enrichment],
                "guardrails": [dict(row) for row in guardrails],
            }
        return {
            "contract": dict(contract), "contract_id": contract["contract_id"],
            "contract_version": 1, "table_id": "orders", "workspace_id": "dev",
            "catalogue_rows": [], "available_columns": json.loads(contract["contract_payload_json"])["table"]["columns"],
            "enrichment": [dict(row) for row in enrichment], "guardrails": [dict(row) for row in guardrails],
            "payload": manifest(),
        }

    def manifest():
        saved = json.loads(contract["contract_payload_json"])
        return {
            "contract": {"contract_id": "contract-orders", "contract_version": 1, "status": contract["status"]},
            "table": {
                **catalogue[0],
                "processing": dict(saved.get("table", {}).get("processing") or {}),
                "processing_source": str(saved.get("table", {}).get("processing_source") or "default"),
                "columns": [dict(row) for row in catalogue[1:]],
            },
            "enrichment": {
                "table": [dict(row) for row in enrichment if not row.get("column_id")],
                "columns": [dict(row) for row in enrichment if row.get("column_id")],
            },
            "guardrails": [{**row, "rule_parameters": module._parameters(row)} for row in guardrails if row.get("is_active", True)],
        }

    def save_contract_draft(*, draft, payload, **_kwargs):
        saved_payload = json.loads(json.dumps(payload))
        calls["draft"].append(saved_payload)
        contract["contract_payload_json"] = json.dumps(
            saved_payload, sort_keys=True, separators=(",", ":")
        )
        enrichment[:] = [
            dict(row)
            for row in [
                *saved_payload.get("enrichment", {}).get("table", []),
                *saved_payload.get("enrichment", {}).get("columns", []),
            ]
        ]
        calls["enrichment"].append([dict(row) for row in enrichment])
        guardrails[:] = []
        for item in saved_payload.get("guardrails", []):
            row = dict(item)
            row["rule_parameters_json"] = json.dumps(
                row.pop("rule_parameters", {}), sort_keys=True, separators=(",", ":")
            )
            row["is_active"] = bool(item.get("is_active", True))
            guardrails.append(row)
        calls["guardrails"].append([dict(row) for row in guardrails])
        return dict(contract)

    def freeze_contract(**_kwargs):
        calls["freeze"] += 1
        contract["status"] = "frozen"
        payload = json.loads(contract["contract_payload_json"])
        payload["contract"]["status"] = "frozen"
        contract["contract_payload_json"] = json.dumps(
            payload, sort_keys=True, separators=(",", ":")
        )
        return {"payload": payload}

    config = types.SimpleNamespace(
        path_config=types.SimpleNamespace(paths={
            "dev": {
                "Bronze": types.SimpleNamespace(kind="lakehouse", name="Raw Lakehouse"),
                "Silver": types.SimpleNamespace(kind="lakehouse", name="Curated Lakehouse"),
                "Gold": types.SimpleNamespace(kind="warehouse", name="Serving Warehouse"),
                "Metadata": types.SimpleNamespace(kind="lakehouse", name="Metadata Lakehouse"),
            }
        }),
        governance_config=types.SimpleNamespace(
            ai_enrichment=ai_enrichment,
            classification_levels=["Public", "Restricted", "Confidential", "Highly Sensitive"],
        ),
    )
    monkeypatch.setattr(module, "resolve_fabric_context", lambda **_kwargs: (config, "dev", {}))
    monkeypatch.setattr(module, "get_spark_session", lambda _session=None, *_args, **_kwargs: object())
    monkeypatch.setattr(module.shared, "require_ipywidgets", lambda: ipywidgets)
    monkeypatch.setattr(module.contracts, "list_contract_governance_state", lambda **_kwargs: {"tables": [catalogue[0]], "contracts": [contract]})
    monkeypatch.setattr(module.contracts, "get_contract_review_state", review)
    monkeypatch.setattr(module.contracts, "save_contract_draft", save_contract_draft)
    monkeypatch.setattr(module.contracts, "freeze_contract", freeze_contract)
    monkeypatch.setattr(module.contracts, "get_table_runtime_context", lambda **_kwargs: {
        "latest_profile": {
            "profile_snapshot_id": "snapshot-prod",
            "workspace_id": "PROD",
            "pipeline_name": "02_pipeline",
            "committed_by": "voyce@example.com",
            "committed_at": "2026-09-26T02:45:00",
        },
        "writer_count": 1,
        "reader_count": 2,
        "lineage": [
            {
                "workspace_id": "DEV", "relationship": "Writer",
                "pipeline_name": "02_pipeline", "last_seen": "2026-09-26T03:00:00",
            },
            {
                "workspace_id": "PROD", "relationship": "Reader",
                "pipeline_name": "04_reporting", "last_seen": "2026-09-26T02:30:00",
            },
        ],
    })
    monkeypatch.setattr(module.contracts, "get_column_profile_context", lambda column_id, **_kwargs: calls["profiles"].append(column_id) or {
        "kind": "profile",
        "profile": {
            "data_type": "long",
            "row_count": 10, "non_null_count": 9, "null_count": 1,
            "null_percent": 10.0, "distinct_count": 8, "distinct_percent": 80.0,
            "mean_value": 5.0, "stddev_value": 2.5,
            "min_value": "1", "percentile_25_value": 3.0, "median_value": 5.0,
            "percentile_75_value": 7.0, "max_value": "9",
        },
        "values": [{"value": column_id, "count": 2, "percent": 20.0}],
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
        state["_controls"]["workspace_select"].value = "dev"
        state["_controls"]["open"].click()
        return state

    return {
        "start": start, "open": open_widget, "models": models,
        "calls": calls, "contract": contract, "catalogue": catalogue,
        "enrichment": enrichment, "guardrails": guardrails, "schedule": schedule,
        "ai_enrichment": ai_enrichment,
    }


def test_manifest_review_shows_business_rule_lifecycle_state():
    """Keep Business Rule intent and Engineering review visible outside raw JSON."""
    payload = {
        "table": {"columns": []},
        "enrichment": {"columns": []},
        "guardrails": [
            {
                "guardrail_type": "data_quality",
                "rule_type": "custom_expression",
                "action": "Block",
                "is_active": True,
                "rule_parameters": {
                    "business_requirement": "Total amount must equal the calculated amount",
                    "columns": ["TOTAL_AMOUNT", "QUANTITY", "UNIT_PRICE"],
                    "expression": "F.col('TOTAL_AMOUNT') == F.col('QUANTITY') * F.col('UNIT_PRICE')",
                    "engineering_review_required": True,
                    "engineering_review_status": "approved",
                    "engineering_reviewed_by": "engineer@example.com",
                },
            },
            {
                "guardrail_type": "data_quality",
                "rule_type": "column_relationship",
                "action": "Warn",
                "is_active": True,
                "rule_parameters": {
                    "business_requirement": "End date must be after start date",
                    "columns": ["END_DATE", "START_DATE"],
                    "operator": ">=",
                },
            },
        ],
    }

    review = module._manifest_sections(payload)["Review"]

    assert "Total amount must equal the calculated amount" in review
    assert "Expression:" in review
    assert "Engineering review: Approved by engineer@example.com" in review
    assert "End date must be after start date" in review
    assert "Engineering review: Not required" in review


def test_select_rejects_missing_explicit_contract_version(widget_runtime):
    """An explicit contract version never silently falls back to another version."""
    state = widget_runtime["start"]()

    with pytest.raises(ValueError, match="Data Contract v99 was not found"):
        state["select"]("orders", 99)

    assert state["current"] is None


def test_selector_is_explicit_and_pending_selection_cannot_change_active_contract(widget_runtime):
    """The editor stays inactive until Open and Change table deactivates the current contract."""
    state = widget_runtime["start"]()
    controls = state["_controls"]

    assert state["current"] is None
    assert state["table_id"] is None
    assert state["pending_table_id"] == "orders"
    assert controls["workspace_select"].value == ""
    assert controls["table"].value == "orders"
    assert controls["contract"].value == "1"
    assert controls["table_search"].options == [
        "Select governed table",
        "Development · Lakehouse: Curated Lakehouse · Schema: sales · Table: orders",
    ]
    assert controls["contract_search"].options == ["Select contract", "v1 · Draft", "New Draft"]
    selector = controls["selector_panel"].children[0]
    assert [field.children[0].value for field in selector.children] == [
        "<b>Workspace</b>",
        "<b>Table</b>",
        "<b>Contract</b>",
    ]
    assert all(field.children[1].layout.width == "100%" for field in selector.children)
    assert controls["selector_panel"].layout.display != "none"
    assert controls["editor_shell"].layout.display == "none"

    controls["open"].click()
    assert state["current"]["table_id"] == "orders"
    assert state["table_id"] == "orders"
    assert controls["selector_panel"].layout.display == "none", state["message"]
    assert controls["editor_shell"].layout.display == ""

    controls["table_description"].value = "Unsaved edit"
    assert state["dirty"] is True
    assert controls["change_table"].description == "Exit"
    assert controls["table_exit_row"].layout.justify_content == "center"

    controls["change_table"].click()
    assert state["current"] is not None
    assert state["dirty"] is True
    assert controls["table_exit_confirm"].layout.display != "none"

    controls["cancel_exit"].click()
    assert controls["table_exit_confirm"].layout.display == "none"
    assert state["current"] is not None
    assert state["dirty"] is True

    controls["change_table"].click()
    controls["confirm_exit_discard"].click()
    assert state["current"] is None
    assert state["table_id"] is None
    assert state["dirty"] is False
    assert controls["selector_panel"].layout.display == ""
    assert controls["editor_shell"].layout.display == "none"
    assert "Unsaved changes discarded" in state["message"]


@pytest.mark.parametrize("versions, expected", [([], "new"), ([3, 2, 1], "3")])
def test_contract_selector_defaults_to_latest_version_or_new_draft(
    widget_runtime, monkeypatch, versions, expected
):
    """Tables without versions start a draft; versioned tables default to the latest."""
    monkeypatch.setattr(
        module.contracts,
        "list_contract_governance_state",
        lambda **_kwargs: {
            "tables": [widget_runtime["catalogue"][0]],
            "contracts": [
                {**widget_runtime["contract"], "contract_version": version}
                for version in versions
            ],
        },
    )
    state = module.widget_data_contract()
    controls = state["_controls"]
    table_option = next(
        option for option in controls["table_search"].options if "Table: orders" in option
    )
    controls["table_search"].value = table_option

    assert controls["contract"].value == expected
    assert state["pending_contract_version"] == (None if expected == "new" else int(expected))
    assert [value for _label, value in controls["contract"].options] == [
        "", *map(str, versions), "new"
    ]
    assert controls["contract_search"].options[-1] == "New Draft"


def test_initial_table_search_does_not_filter_by_selection_prompt(widget_runtime):
    """An unselected table field leaves all registered table suggestions visible."""
    widget_runtime["catalogue"][0].update(layer="Bronze", schema_name="demo")
    state = module.widget_data_contract()
    controls = state["_controls"]

    assert controls["workspace_select"].value == ""
    assert controls["table"].value == ""
    assert controls["table_search"].value == ""
    assert any("Table: orders" in option for option in controls["table_search"].options)
    assert state["pending_table_id"] is None

    table_option = next(
        option for option in controls["table_search"].options if "Table: orders" in option
    )
    controls["table_search"].value = table_option
    assert controls["table"].value == "orders"
    assert state["pending_table_id"] == "orders"


def test_selector_refresh_is_atomic_after_observers_are_registered(widget_runtime, monkeypatch):
    """Table and Workspace filtering clears stale selections in either direction."""
    rows = [dict(widget_runtime["catalogue"][0]),
            {**widget_runtime["catalogue"][0], "table_id": "inventory", "table_name": "inventory", "workspace_id": "other"},
            {**widget_runtime["catalogue"][0], "workspace_id": "other"}]
    monkeypatch.setattr(module.contracts, "list_contract_governance_state", lambda **kw: {"tables": rows, "contracts": [widget_runtime["contract"]]})
    state = module.widget_data_contract()
    controls = state["_controls"]
    assert controls["table"].value == controls["workspace_select"].value == ""
    controls["workspace_select"].value = "dev"
    assert [value for label, value in controls["table"].options] == ["", "orders"]
    controls["table"].value = "orders"
    assert [value for label, value in controls["workspace_select"].options] == ["", "dev", "other"]
    assert controls["contract"].value == "1"
    controls["workspace_select"].value = "other"
    assert controls["table"].value == "orders"
    controls["table"].value = "inventory"
    assert [value for label, value in controls["workspace_select"].options] == ["", "other"]
    assert state["_selector_refreshing"] is False
    assert controls["contract"].value == "new"
    assert state["pending_contract_version"] is None
    controls["table"].value = "orders"
    assert controls["contract"].value == "1"
    assert state["pending_contract_version"] == 1


def test_table_identity_labels_distinguish_same_named_tables(widget_runtime, monkeypatch):
    """Search results expose physical identity while selection keeps the central Table ID."""
    rows = [
        dict(widget_runtime["catalogue"][0]),
        {
            **widget_runtime["catalogue"][0],
            "table_id": "audit-orders",
            "store_type": "Warehouse",
            "layer": "Gold",
            "schema_name": "audit",
        },
    ]
    monkeypatch.setattr(
        module.contracts,
        "list_contract_governance_state",
        lambda **_kwargs: {"tables": rows, "contracts": [widget_runtime["contract"]]},
    )

    state = module.widget_data_contract()
    controls = state["_controls"]
    labels_by_value = {value: label for label, value in controls["table"].options}

    assert labels_by_value["orders"] == (
        "Development · Lakehouse: Curated Lakehouse · Schema: sales · Table: orders"
    )
    assert labels_by_value["audit-orders"] == (
        "Development · Warehouse: Serving Warehouse · Schema: audit · Table: orders"
    )
    controls["table"].value = "audit-orders"
    assert state["pending_table_id"] == "audit-orders"


def test_inherited_processing_is_editable_and_persists_on_contract_save(widget_runtime):
    """Fallback processing stays editable and is saved inside the exact draft JSON."""
    payload = json.loads(widget_runtime["contract"]["contract_payload_json"])
    payload["table"]["processing"] = {"load_strategy": "overwrite"}
    payload["table"]["processing_source"] = "previous_contract"
    widget_runtime["contract"]["contract_payload_json"] = json.dumps(payload)

    state = widget_runtime["open"]()
    controls = state["_controls"]

    assert controls["load_strategy"].disabled is False
    controls["load_strategy"].value = "append"
    controls["top_nav"].value = "Review"
    controls["save_data_contract"].click()

    saved = widget_runtime["calls"]["draft"][-1]
    assert saved["table"]["processing"] == {"load_strategy": "append"}
    assert saved["table"]["processing_source"] == "manual"
    persisted = json.loads(widget_runtime["contract"]["contract_payload_json"])
    assert persisted["table"]["processing"] == {"load_strategy": "append"}
    assert persisted["table"]["processing_source"] == "manual"


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


def test_profile_context_renders_compact_datatype_aware_evidence():
    """Profile statistics and optional frequencies render as compact escaped text."""
    numeric = module._profile_html({
        "kind": "profile",
        "profile": {
            "data_type": "double", "row_count": 120, "null_count": 0,
            "null_percent": 0.0, "distinct_count": 100, "distinct_percent": 83.333,
            "mean_value": 237.42, "stddev_value": 281.16,
            "min_value": "29.9", "percentile_25_value": 89.0,
            "median_value": 149.0, "percentile_75_value": 399.0, "max_value": "1299.0",
        },
        "values": [{"value": "<Ready>", "count": 15, "percent": 12.5}],
    })
    assert "Row count: <b>120</b>" in numeric
    assert "Distinct count: <b>100</b>" in numeric
    assert "Distinct percent: <b>83.333%</b>" in numeric
    assert "Null count: <b>0</b>" in numeric
    assert "Null percent: <b>0%</b>" in numeric
    assert "Min value: <b>29.9</b>" in numeric
    assert "Max value: <b>1299.0</b>" in numeric
    assert "Median value: <b>149</b>" in numeric
    assert "Percentile 25 value: <b>89</b>" in numeric
    assert "Percentile 75 value: <b>399</b>" in numeric
    assert "Mean value: <b>237.42</b>" in numeric
    assert "Stddev value: <b>281.16</b>" in numeric
    assert "Value: <b>&lt;Ready&gt;</b>" in numeric
    assert "Count: <b>15</b>" in numeric
    assert "Percent: <b>12.5%</b>" in numeric
    assert "<b>Row count</b>" not in numeric

    high_cardinality = module._profile_html({
        "kind": "profile",
        "profile": {
            "data_type": "string", "row_count": 120, "null_percent": 0.0,
            "distinct_count": 120, "distinct_percent": 100.0,
        },
        "values": [],
    })
    assert "highly unique" in high_cardinality
    assert "value frequency profiling was skipped" in high_cardinality
    assert "Not yet profiled" in module._profile_html({"kind": "unavailable"})


def test_shared_layout_and_existing_state_hydrate(widget_runtime):
    """The unified page uses shared layout primitives and hydrates all main editors."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    assert "fabricops-form" in controls["page"]._dom_classes
    assert tuple(controls["top_nav"].options) == ("Table", "Column", "Review")
    assert controls["workspace"].layout.grid_template_columns == "minmax(250px, 27fr) minmax(0, 73fr)"
    assert len(controls["workspace"].children) == 2
    assert controls["table"].value == "orders"
    assert controls["contract"].value == "1"
    assert controls["table_description"].value == "Orders table"
    assert controls["table_classification"].value == "Confidential"
    assert controls["column_description"].value == "Order identifier"
    assert controls["column_classification"].value == "Confidential"
    assert controls["required"].value is True
    assert controls["table_guardrails"]["freshness"]["enabled"].value is True
    assert controls["table_guardrails"]["source_drift"]["enabled"].value is True
    assert len(controls["table_guardrails"]["source_drift"]["parameters"]) == 2
    assert controls["load_strategy"].value == "append"
    assert controls["load_strategy"].disabled is True
    assert controls["sensitive_enabled"].value is True
    assert controls["business_saved"].value == ""
    assert controls["row_key_columns"].value == ()
    assert controls["business_enabled"].description == "Enabled"
    assert controls["business_block"].description == "On failure"
    table_summary = controls["left_pane"].children[0].value
    assert "Scheduled refresh" in table_summary
    assert "Daily · 08:00 · Asia/Singapore" in table_summary


def test_existing_grain_hydrates_row_key(widget_runtime):
    """Grain owns its selected key and policy independently of DQ."""
    widget_runtime["guardrails"].append({
        "guardrail_rule_id": "grain", "guardrail_version": 1, "guardrail_type": "grain",
        "column_id": "", "rule_type": "uniqueness", "rule_parameters_json": '{"columns":["column_0","column_1"]}',
        "action": "Warn", "is_active": True, "contract_id": "contract-orders", "contract_version": 1, "workspace_id": "dev",
    })
    controls = widget_runtime["open"]()["_controls"]
    assert tuple(controls["row_key_columns"].value) == ("column_0", "column_1")
    assert controls["grain_enabled"].value is True
    assert controls["grain_policy"].value == "Warn"


def test_grain_changes_reuse_one_rule_and_never_enable_implicitly(widget_runtime):
    """Description and key edits retain inactive metadata until explicit enablement."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["table_grain"].value = "One row per key combination"
    assert not any(r.get("guardrail_type") == "grain" for r in state["current"]["guardrails"])
    controls["row_key_columns"].value = ("column_0",)
    def grains():
        return [r for r in state["current"]["guardrails"] if r.get("guardrail_type") == "grain"]
    assert len(grains()) == 1
    rule_id = grains()[0]["guardrail_rule_id"]
    assert grains()[0]["is_active"] is False
    controls["grain_enabled"].value = True
    assert controls["grain_policy"].value == "Block"
    controls["grain_policy"].value = "Warn"
    controls["row_key_columns"].value = ("column_0", "column_1")
    controls["grain_enabled"].value = False
    assert len(grains()) == 1
    assert grains()[0]["guardrail_rule_id"] == rule_id
    assert json.loads(grains()[0]["rule_parameters_json"]) == {"columns": ["column_0", "column_1"]}
    controls["save_data_contract"].click()
    reopened_state = widget_runtime["open"]()
    reopened = reopened_state["_controls"]
    assert reopened["grain_enabled"].value is False
    assert reopened["grain_policy"].value == "Warn"
    assert reopened["row_key_columns"].value == ("column_0", "column_1")
    assert reopened["table_grain"].value == "One row per key combination"
    reopened["grain_enabled"].value = True
    assert reopened["grain_policy"].value == "Block"
    assert not any(r.get("guardrail_type") == "data_quality" and r.get("rule_type") == "uniqueness" for r in reopened_state["current"]["guardrails"])


def test_general_table_uniqueness_is_not_reinterpreted_as_grain(widget_runtime):
    """Existing DQ rules retain their ownership; no compatibility migration is inferred."""
    for rule_id, columns in (("dq-key-a", ["column_0"]), ("dq-key-b", ["column_1"])):
        widget_runtime["guardrails"].append({
            "guardrail_rule_id": rule_id, "guardrail_version": 1, "guardrail_type": "data_quality",
            "column_id": "", "rule_type": "uniqueness", "rule_parameters_json": json.dumps({"columns": columns}),
            "action": "Block", "is_active": True, "contract_id": "contract-orders", "contract_version": 1, "workspace_id": "dev",
        })
    state = widget_runtime["open"]()
    controls = state["_controls"]
    assert controls["row_key_columns"].value == ()
    assert controls["grain_enabled"].value is False
    controls["row_key_columns"].value = ("column_0", "column_1")
    assert len([r for r in state["current"]["guardrails"] if r.get("rule_type") == "uniqueness" and r.get("guardrail_type") == "data_quality"]) == 2


def test_reviewed_fields_round_trip_after_save_and_reopen(widget_runtime):
    """Saved governance choices hydrate without relying on the old widget instance."""
    _use_text_identifier(widget_runtime)
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["table_description"].value = "Persisted orders"
    controls["table_classification"].value = "Restricted"
    controls["table_grain"].value = "One row per order"
    controls["row_key_columns"].value = ("column_0",)
    controls["grain_enabled"].value = True

    freshness = controls["table_guardrails"]["freshness"]
    freshness["enabled"].value = True
    freshness["block"].value = False
    freshness["parameters"][0].value = "recurring"
    freshness["parameters"][1].value = "column_1"
    freshness["parameters"][2].value = "2"
    freshness["parameters"][3].value = "days"
    freshness["parameters"][4].value = "3"
    freshness["parameters"][5].value = "days"

    drift = controls["table_guardrails"]["source_drift"]
    drift["enabled"].value = True
    drift["block"].value = True
    drift["parameters"][0].value = "column_0"
    drift["parameters"][1].value = "column_1"

    controls["column_select"].value = "col-0"
    controls["column_description"].value = "Persisted identifier"
    controls["column_classification"].value = "Restricted"
    controls["required"].value = True
    controls["pii_type"].value = "direct"
    controls["pii_reason"].value = "Identifies an order"
    controls["sensitive_treatment"].value = "mask"
    controls["mask_start"].value = "1"
    controls["mask_end"].value = "2"
    controls["mask_character"].value = "#"
    controls["sensitive_enabled"].value = True

    completeness = controls["dq_family_controls"]["completeness"]
    completeness["enabled"].value = True
    completeness["block"].value = True
    completeness["parameters"][0].value = "5"
    completeness["parameters"][1].value = True

    controls["save_data_contract"].click()
    assert widget_runtime["calls"]["draft"]

    reopened = widget_runtime["open"]()
    hydrated = reopened["_controls"]
    assert hydrated["table_description"].value == "Persisted orders"
    assert hydrated["table_classification"].value == "Restricted"
    assert hydrated["table_grain"].value == "One row per order"
    assert tuple(hydrated["row_key_columns"].value) == ("column_0",)
    assert hydrated["grain_enabled"].value is True

    reopened_freshness = hydrated["table_guardrails"]["freshness"]
    assert reopened_freshness["enabled"].value is True
    assert reopened_freshness["block"].value is False
    assert reopened_freshness["parameters"][1].value == "column_1"
    assert reopened_freshness["parameters"][2].value == "2.0"
    assert reopened_freshness["parameters"][4].value == "3.0"

    reopened_drift = hydrated["table_guardrails"]["source_drift"]
    assert reopened_drift["enabled"].value is True
    assert reopened_drift["block"].value is True
    assert reopened_drift["parameters"][0].value == "column_0"
    assert reopened_drift["parameters"][1].value == "column_1"

    hydrated["column_select"].value = "col-0"
    assert hydrated["column_description"].value == "Persisted identifier"
    assert hydrated["column_classification"].value == "Restricted"
    assert hydrated["required"].value is True
    assert hydrated["pii_type"].value == "direct"
    assert hydrated["pii_reason"].value == "Identifies an order"
    assert hydrated["sensitive_treatment"].value == "mask"
    assert hydrated["mask_start"].value == "1"
    assert hydrated["mask_end"].value == "2"
    assert hydrated["mask_character"].value == "#"
    assert hydrated["sensitive_enabled"].value is True
    assert "sensitive_block" not in hydrated

    reopened_completeness = hydrated["dq_family_controls"]["completeness"]
    assert reopened_completeness["enabled"].value is True
    assert reopened_completeness["block"].value is True
    assert reopened_completeness["parameters"][0].value == "5.0"
    assert reopened_completeness["parameters"][1].value is True


def test_v38_top_navigation_switches_one_two_pane_workspace(widget_runtime):
    """Use the prototype contract: top nav plus one 27/73 left/right workspace."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    for label in ("Table", "Column", "Review"):
        controls["top_nav"].value = label
        assert len(controls["left_pane"].children) > 0
        assert len(controls["right_pane"].children) > 0

    controls["top_nav"].value = "Table"
    table_context = controls["left_pane"].children[0]
    table_summary = table_context.value
    assert "v1 · DRAFT" in table_summary
    assert "Latest profile" in table_summary
    assert "PROD · 02_pipeline" in table_summary
    assert "voyce@example.com · 26 Sep 2026, 02:45" in table_summary
    assert "Pipeline usage" in table_summary
    assert "1 write · 2 reads" in table_summary
    assert "View lineage" in table_summary
    assert ">Env</th>" in table_summary
    assert ">Pipeline</th>" in table_summary
    assert ">Role</th>" in table_summary
    assert ">Write</td>" in table_summary
    assert ">Read</td>" in table_summary
    assert "04_reporting" in table_summary
    assert "Classification" in table_summary
    assert "Grain" in table_summary
    assert "Row Key" in table_summary
    assert "Load strategy" in table_summary
    assert "Scheduled refresh" in table_summary
    assert "Guardrails" in table_summary
    assert table_summary.index("Grain") < table_summary.index("Classification")
    assert table_summary.index("Classification") < table_summary.index("Row Key")
    assert table_summary.index("Row Key") < table_summary.index("Load strategy")
    assert table_summary.index("Load strategy") < table_summary.index("Scheduled refresh")
    assert table_summary.index("Scheduled refresh") < table_summary.index("Guardrails")
    assert "table_save" not in controls
    table_sections = controls["right_pane"].children
    assert [section.children[0].value for section in table_sections[:6]] == [
        "<div class=\"fabricops-section-heading\">Grain &amp; Row Key</div>",
        "<div class=\"fabricops-section-heading\">Table definition</div>",
        "<div class=\"fabricops-section-heading\">Profiling</div>",
        "<div class=\"fabricops-section-heading\">Processing</div>",
        "<div class=\"fabricops-section-heading\">Freshness</div>",
        "<div class=\"fabricops-section-heading\">Source Drift</div>",
    ]

    grain_section = controls["right_pane"].children[0]
    assert grain_section.children[1].children == (controls["grain_enabled"], controls["grain_policy"])
    assert len(grain_section.children[3].children) == 1
    assert controls["table_grain"].layout.max_width == "560px"

    controls["top_nav"].value = "Column"
    assert controls["column_search"] in controls["left_pane"].children
    assert controls["dq_panel"].children[1].children[2] is controls["dq_primary"]
    assert list(controls["dq_family_controls"]) == [
        "completeness", "uniqueness", "value_set", "range",
    ]
    assert "pattern" not in controls["dq_family_controls"]
    assert any(
        label == "Pattern · column_0"
        for label, _value in controls["business_saved"].options
    )
    assert "save_column" not in controls
    assert "save_dq" not in controls

    assert "Business Rules" not in tuple(controls["top_nav"].options)
    controls["top_nav"].value = "Review"
    assert controls["left_pane"].children[0] is table_context
    assert "Column definitions" in controls["manifest_preview"].value
    assert "Guardrails" in controls["manifest_preview"].value
    assert "<b>Table</b>" in controls["manifest_preview"].value
    assert "<b>Columns</b>" in controls["manifest_preview"].value
    assert "<b>DQ Rules</b>" in controls["manifest_preview"].value


def test_scheduled_refresh_renders_captured_frequency_in_table_summary(widget_runtime):
    """Operational context shows the writer-captured schedule in the table summary."""
    widget_runtime["catalogue"][0]["scheduled_refresh_json"] = {
        "status": "configured",
        "schedules": [
            {"enabled": True, "frequency": "daily", "times": ["08:00"], "timezone": "Asia/Singapore"},
            {"enabled": False, "frequency": "weekly", "times": ["09:30"], "timezone": "UTC"},
        ],
    }

    state = widget_runtime["open"]()
    rendered = state["_controls"]["left_pane"].children[0].value

    assert "Scheduled refresh" in rendered
    assert "Daily · 08:00 · Asia/Singapore" in rendered
    assert "Weekly · 09:30 · UTC · Disabled" in rendered
    assert rendered.index("Daily · 08:00 · Asia/Singapore") < rendered.index("Weekly · 09:30 · UTC · Disabled")
    assert "pipeline_refresh" not in state["_controls"]


def test_no_scheduled_refresh_is_calm_and_does_not_affect_persistence(widget_runtime):
    """No Fabric schedule remains non-fatal and canonical save records stay unchanged."""
    widget_runtime["catalogue"][0]["scheduled_refresh_json"] = {"status": "not_configured", "schedules": []}
    state = widget_runtime["open"]()
    rendered = state["_controls"]["left_pane"].children[0].value
    assert "Scheduled refresh" in rendered
    assert "Not configured" in rendered

    state["_controls"]["table_description"].value = "Still governed"
    assert widget_runtime["calls"]["enrichment"] == []

    state["_controls"]["save_data_contract"].click()
    saved = widget_runtime["calls"]["enrichment"][-1]
    assert all("scheduled_refresh" not in record for record in saved)


def test_profile_context_is_lazy_and_cached_per_table_and_column(widget_runtime):
    """Profile evidence loads only when Columns is opened, then reuses the per-column cache."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    assert widget_runtime["calls"]["profiles"] == []

    controls["top_nav"].value = "Column"
    assert widget_runtime["calls"]["profiles"].count("col-0") == 1

    controls["column_select"].value = "col-1"
    assert widget_runtime["calls"]["profiles"].count("col-1") == 1

    controls["column_select"].value = "col-0"
    assert widget_runtime["calls"]["profiles"].count("col-0") == 1

    state["load_profile_context"]("col-0")
    assert widget_runtime["calls"]["profiles"].count("col-0") == 1
    assert ("orders", "col-0") in state["_profile_cache"]


def test_column_selection_reuses_one_editor_and_refreshes_profile(widget_runtime):
    """Large schemas scroll inside the list only and rehydrate a single editor."""
    widget_runtime["catalogue"][:] = _catalogue_rows(250)
    _capture_fixture_columns(widget_runtime)
    state = widget_runtime["open"]()
    controls = state["_controls"]
    editor_identity = id(controls["column_description"])
    controls["column_select"].value = "col-249"
    assert id(controls["column_description"]) == editor_identity
    assert "column_249" in controls["column_context"].value
    assert widget_runtime["calls"]["profiles"] == []
    controls["top_nav"].value = "Column"
    assert "col-249" in controls["profile_context"].value
    assert widget_runtime["calls"]["profiles"][-1] == "col-249"
    assert controls["left_pane"].children[-1] is controls["column_select"]
    assert controls["column_search"] in controls["left_pane"].children
    assert controls["workspace"].layout.grid_template_columns == "minmax(250px, 27fr) minmax(0, 73fr)"
    assert controls["column_select"].layout.height == "220px"
    assert controls["column_select"].layout.max_height == "280px"
    assert "fabricops-contract-list" in controls["column_select"]._dom_classes


def test_column_without_dq_rule_resets_editor_instead_of_leaking_prior_rule(widget_runtime):
    """Selecting an unconfigured column must not retain another column's DQ values."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    families = controls["dq_family_controls"]
    assert controls["dq_completeness_failure"].value == "0"
    assert families["completeness"]["block"].value is True

    controls["column_select"].value = "col-1"

    assert controls["dq_completeness_failure"].value == "0"
    assert families["completeness"]["block"].value is False


def test_unsaved_column_edits_survive_an_unrelated_save_rerender(widget_runtime):
    """Per-column drafts live in widget state rather than one disposable render closure."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["column_select"].value = "col-1"
    controls["column_description"].value = "Unsaved local description"
    controls["column_select"].value = "col-0"

    controls["table_description"].value = "Saved table description"
    state["_controls"]["column_select"].value = "col-1"

    assert state["_controls"]["column_description"].value == "Unsaved local description"


def test_final_save_returns_to_selector_after_persisting_canonical_draft(widget_runtime):
    """Save and exit persists staged state and returns to the table selector."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["column_description"].value = "Older local draft"
    controls["column_select"].value = "col-1"
    controls["column_select"].value = "col-0"
    controls["column_description"].value = "Canonical saved description"
    controls["pii_reason"].value = "Existing sensitive policy remains reviewed."

    assert widget_runtime["calls"]["enrichment"] == []
    assert state["dirty"] is True

    state["_controls"]["save_data_contract"].click()
    assert widget_runtime["calls"]["enrichment"]
    assert state["dirty"] is False
    assert state["current"] is None
    assert state["_controls"]["selector_panel"].layout.display != "none"
    assert state["_controls"]["editor_shell"].layout.display == "none"
    assert "draft saved" in state["message"]


def test_freeze_dirty_draft_prompts_save_and_freeze(widget_runtime):
    """Freeze stays clickable with edits and saves the draft only after confirmation."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["table_description"].value = "Ready to freeze"
    assert state["dirty"] is True
    assert controls["freeze"].disabled is False

    controls["freeze"].click()
    assert controls["freeze_confirm"].description == "Save & Freeze v1"

    controls["freeze_confirm"].click()

    assert len(widget_runtime["calls"]["draft"]) == 1
    assert widget_runtime["calls"]["freeze"] == 1
    assert widget_runtime["contract"]["status"] == "frozen"
    assert "FROZEN" in state["message"]


def test_live_edits_stage_without_writes_until_final_save(widget_runtime):
    """Table and column edits stage locally; Review save persists once."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["table_description"].value = "Governed orders"
    controls["column_description"].value = "Canonical ID"
    controls["required"].value = False

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
    assert "draft saved" in state["message"]


def test_table_and_column_edits_stage_without_intermediate_actions(widget_runtime):
    """Table and column edits update session state without partial persistence."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["table_description"].value = "Unified table save"
    controls["column_description"].value = "Unified column save"
    controls["pii_reason"].value = "Direct identifier for a person."

    assert widget_runtime["calls"]["enrichment"] == []
    assert widget_runtime["calls"]["guardrails"] == []
    assert state["_pending_enrichment"]
    assert state["_pending_guardrails"]

    controls["save_data_contract"].click()
    assert len(widget_runtime["calls"]["enrichment"]) == 1
    assert len(widget_runtime["calls"]["guardrails"]) == 1


def test_discard_changes_restores_canonical_state_without_writes(widget_runtime):
    """Discard confirmation can be cancelled before clearing staged changes."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["table_description"].value = "Unsaved table change"
    assert state["dirty"] is True
    assert widget_runtime["calls"]["enrichment"] == []

    controls["discard_data_contract"].click()
    assert controls["discard_data_contract_confirm"].layout.display == ""
    assert state["dirty"] is True

    controls["cancel_discard_data_contract"].click()
    assert controls["discard_data_contract_confirm"].layout.display == "none"
    assert state["dirty"] is True
    assert controls["table_description"].value == "Unsaved table change"
    assert "Discard cancelled" in state["message"]

    controls["discard_data_contract"].click()
    controls["confirm_discard_data_contract"].click()
    assert state["dirty"] is False
    assert widget_runtime["calls"]["enrichment"] == []
    assert widget_runtime["calls"]["guardrails"] == []
    assert state["current"] is None
    assert controls["selector_panel"].layout.display == ""
    assert controls["editor_shell"].layout.display == "none"
    assert "discarded" in state["message"]


@pytest.mark.parametrize("tab", ["Table", "Column", "Business Rules", "Review"])
def test_shared_footer_saves_and_clears_from_every_tab(
    widget_runtime, monkeypatch, tab
):
    """One footer persists the complete staged draft from every authoring tab."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    controls["top_nav"].value = tab
    controls["table_description"].value = f"Saved from {tab}"

    assert controls["editor_shell"].children[-1] is controls["authoring_footer"]
    assert controls["authoring_footer"].layout.display == ""
    controls["save_data_contract"].click()

    saved_description = next(
        item for item in widget_runtime["calls"]["draft"][-1]["enrichment"]["table"]
        if item["enrichment_type"] == "Description"
    )
    assert saved_description["value"] == f"Saved from {tab}"
    assert state["current"] is None
    assert controls["selector_panel"].layout.display == ""
    assert controls["editor_shell"].layout.display == "none"


@pytest.mark.parametrize("tab", ["Table", "Column", "Business Rules", "Review"])
def test_shared_footer_preserves_state_when_save_fails(
    widget_runtime, monkeypatch, tab
):
    """A failed save remains in the editor with all staged changes intact."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    controls["top_nav"].value = tab
    controls["table_description"].value = f"Unsaved from {tab}"

    def fail_save(**_kwargs):
        raise RuntimeError("Metadata store unavailable; retry the save.")

    monkeypatch.setattr(module.contracts, "save_contract_draft", fail_save)
    controls["save_data_contract"].click()

    assert state["current"] is not None
    assert state["dirty"] is True
    assert controls["table_description"].value == f"Unsaved from {tab}"
    assert controls["selector_panel"].layout.display == "none"
    assert controls["editor_shell"].layout.display == ""
    assert "Metadata store unavailable; retry the save." in state["message"]


@pytest.mark.parametrize("tab", ["Table", "Column", "Business Rules", "Review"])
def test_shared_footer_discards_and_clears_from_every_tab(
    widget_runtime, monkeypatch, tab
):
    """Confirmed discard clears only staged state from every authoring tab."""
    persisted = widget_runtime["contract"]["contract_payload_json"]
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    controls["top_nav"].value = tab
    controls["table_description"].value = f"Discarded from {tab}"

    controls["discard_data_contract"].click()
    assert controls["discard_data_contract_confirm"].layout.display == ""
    controls["cancel_discard_data_contract"].click()
    assert state["dirty"] is True
    assert controls["table_description"].value == f"Discarded from {tab}"

    controls["discard_data_contract"].click()
    controls["confirm_discard_data_contract"].click()

    assert widget_runtime["contract"]["contract_payload_json"] == persisted
    assert widget_runtime["calls"]["draft"] == []
    assert state["current"] is None
    assert controls["selector_panel"].layout.display == ""
    assert controls["editor_shell"].layout.display == "none"


def test_guardrail_edits_stage_then_final_save_persists(widget_runtime):
    """Guardrail editors stage normalized records and persist them only at final save."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["table_guardrails"]["freshness"]["block"].value = False

    controls["sensitive_enabled"].value = True
    controls["sensitive_treatment"].value = "tokenize"
    controls["pii_reason"].value = "The identifier directly associates an order with a person."

    controls["dq_blank_missing"].value = True

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

def _enable_ai(widget_runtime, monkeypatch, *, captures=None):
    """Enable deterministic AI responses for widget interaction tests."""
    widget_runtime["ai_enrichment"]["enabled"] = True
    captures = captures if captures is not None else {"enrichment": [], "sensitive": [], "grain": []}

    def enrichment(context, **_kwargs):
        captures["enrichment"].append(context)
        level = context["metadata_level"]
        return {"Description": f"Suggested {level} description"}

    def grain(context, **_kwargs):
        captures["grain"].append(context)
        candidates = context.get("profile_key_candidates") or []
        key_columns = list(candidates[0].get("columns", [])) if candidates else ["column_0"]
        return {
            "grain": "One row represents a single order line.",
            "key_columns": key_columns,
            "rationale": "Grounded in Engineering profile evidence.",
        }

    def sensitive(context, **_kwargs):
        captures["sensitive"].append(context)
        column = context["columns"][0]
        return [{
            "column_name": column["column_name"], "column_id": column["column_id"],
            "pii_type": "direct", "pii_label": "Direct PII",
            "reason": "Can uniquely associate a person.", "treatment": "mask" if column["data_type"] == "string" else "tokenize",
            "action": "Block",
            "parameters": {"preserve_start": 1, "preserve_end": 0, "mask_character": "*"} if column["data_type"] == "string" else {},
            "is_active": True,
        }]

    monkeypatch.setattr(module, "suggest_enrichment", enrichment)
    monkeypatch.setattr(module, "suggest_grain_key", grain)
    monkeypatch.setattr(module, "suggest_sensitive_data", sensitive)
    return captures


def _open_with_ai(widget_runtime, monkeypatch, *, captures=None):
    """Open one contract and explicitly opt in to scoped AI suggestions."""
    captures = _enable_ai(widget_runtime, monkeypatch, captures=captures)
    state = widget_runtime["start"]()
    state["_controls"]["open_with_ai"].click()
    return state, captures


def test_sensitive_ai_is_disabled_by_configuration(widget_runtime):
    """AI-disabled authoring keeps every manual editor available."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    assert controls["rerun_sensitive"].disabled is True
    assert controls["column_description"].disabled is False
    assert "save_column_enrichment" not in controls
    assert all(not drafts for drafts in state["_column_drafts"].values())


def test_ai_startup_is_explicit_and_scoped_to_current_table_and_column(widget_runtime, monkeypatch):
    """Choose AI before opening; the editor then renders the complete contract."""
    captures = _enable_ai(widget_runtime, monkeypatch)
    state = widget_runtime["start"]()
    controls = state["_controls"]

    assert captures["enrichment"] == []
    assert captures["sensitive"] == []
    assert controls["selector_panel"].layout.display != "none"

    controls["open_with_ai"].click()
    controls = state["_controls"]
    assert len(captures["enrichment"]) == 1  # existing table Description is reused; current column is suggested
    assert captures["enrichment"][0]["metadata_level"] == "column"
    assert len(captures["sensitive"]) == 1
    assert captures["sensitive"][0]["table_description"] == "Orders table"
    assert captures["sensitive"][0]["columns"][0]["description"] == "Suggested column description"
    assert all(not drafts for drafts in state["_column_drafts"].values())
    assert state["_ai_suggestions"]
    assert captures["grain"]
    assert "Suggested column description" in controls["column_description_ai"].value
    assert "Direct PII" in controls["sensitive_ai"].value
    assert controls["selector_panel"].layout.display == "none"
    assert controls["editor_shell"].layout.display == ""
    grain_section = controls["right_pane"].children[0]
    assert grain_section.children[1].children == (controls["grain_enabled"], controls["grain_policy"])
    assert grain_section.children[3].layout.grid_template_columns == (
        "minmax(0, 68fr) minmax(240px, 32fr)"
    )
    assert len(grain_section.children[3].children) == 2
    grain_primary = grain_section.children[3].children[0]
    assert controls["grain_profile_evidence"] in grain_primary.children
    controls["top_nav"].value = "Column"
    assert controls["dq_panel"].children[1].children[2] is controls["dq_primary"]
    assert "dq_ai_panel" not in controls
    assert "Business Rules" in tuple(controls["top_nav"].options)
    controls["top_nav"].value = "Business Rules"
    assert controls["business_requirement"] in controls["business_ai_panel"].children
    assert controls["business_requirement"].description == ""
    assert controls["business_columns"].description == ""
    assert controls["business_rule_controls"].layout.display == "none"
    assert controls["workspace"].layout.grid_template_columns == "minmax(0, 1fr) minmax(0, 1fr)"
    assert "Author DQ Rules" in controls["left_pane"].children[0].children[0].value
    assert "Review &amp; Add DQ Rules" in controls["right_pane"].children[0].children[0].value
    for label in ("Table", "Column", "Business Rules", "Review"):
        controls["top_nav"].value = label
        assert len(controls["left_pane"].children) > 0
        assert len(controls["right_pane"].children) > 0
    assert widget_runtime["calls"]["enrichment"] == []
    assert widget_runtime["calls"]["guardrails"] == []


def test_data_contract_uses_notebook_scroll_and_natural_panel_heights(
    widget_runtime, monkeypatch
):
    """Main tab panels expand naturally while genuine lists retain bounded scrolling."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    style = controls["page"].children[0].value

    assert controls["page"].layout.height == "auto"
    assert controls["page"].layout.overflow == "visible"
    assert "height:500px" not in style
    assert "max-height:500px" not in style
    assert ".fabricops-business-body {\n    flex:0 1 auto" in style
    assert "max-height:none; overflow:visible" in style
    assert "overflow-x:hidden; overflow-y:auto" in style

    controls["top_nav"].value = "Business Rules"
    author_panel = controls["left_pane"].children[0]
    review_panel = controls["right_pane"].children[0]
    assert author_panel.layout.height == "auto"
    assert author_panel.layout.overflow == "visible"
    assert review_panel.layout.height == "auto"
    assert review_panel.layout.overflow == "visible"
    assert getattr(controls["business_saved"].layout, "height", None) is None
    assert getattr(controls["business_proposal_select"].layout, "height", None) is None
    assert controls["resolve_business_rule"] in author_panel.children[-1].children
    assert controls["apply_business_rule"] in review_panel.children[-1].children[1].children

    for control_name in (
        "row_key_columns", "key_columns", "tracked_columns",
        "column_select", "business_columns",
    ):
        assert "fabricops-contract-list" in controls[control_name]._dom_classes
    assert controls["row_key_columns"].layout.max_height == "252px"
    assert controls["key_columns"].layout.max_height == "220px"
    assert controls["tracked_columns"].layout.max_height == "220px"
    assert controls["business_columns"].layout.max_height == "220px"
    assert controls["profile_context"].layout.height == "auto"
    assert controls["profile_context"].layout.overflow == "visible"

    controls["top_nav"].value = "Review"
    exact_json = controls["right_pane"].children[1].children[1]
    assert exact_json.layout.height == "auto"
    assert exact_json.layout.overflow == "visible"


def test_shared_draft_footer_stays_outside_tabs_and_freeze_stays_on_review(
    widget_runtime, monkeypatch
):
    """Draft actions remain global while the lifecycle freeze action remains review-only."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    def contains(root, target):
        return root is target or any(
            contains(child, target) for child in getattr(root, "children", ())
        )

    for tab in ("Table", "Column", "Business Rules"):
        controls["top_nav"].value = tab
        assert not contains(controls["workspace"], controls["save_data_contract"])
        assert not contains(controls["workspace"], controls["discard_data_contract"])
        assert not contains(controls["workspace"], controls["freeze"])

    controls["top_nav"].value = "Review"
    assert contains(controls["right_pane"], controls["freeze"])
    assert not contains(controls["workspace"], controls["save_data_contract"])
    assert not contains(controls["workspace"], controls["discard_data_contract"])
    assert contains(controls["authoring_footer"], controls["save_data_contract"])
    assert contains(controls["authoring_footer"], controls["discard_data_contract"])



def test_missing_profiled_key_candidate_shows_no_suggestion_without_profile_fallback(
    widget_runtime,
):
    """Missing Engineering key evidence stays explicit and does not infer a fallback key."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    assert tuple(controls["row_key_columns"].value) == ()
    assert "No row key suggestion available from the latest profile" in (
        controls["grain_profile_evidence"].value
    )
    assert widget_runtime["calls"]["profiles"] == []


def test_profiled_key_candidate_preselects_row_key_and_feeds_grain_ai(widget_runtime, monkeypatch):
    """Consume Engineering key evidence without asking AI to choose the key."""
    widget_runtime["catalogue"][0]["profile_key_candidates_json"] = {
        "status": "resolved",
        "max_combination_width": 3,
        "candidates": [{
            "columns": ["column_0", "column_1"],
            "column_count": 2,
            "row_count": 120,
            "distinct_count": 120,
            "uniqueness_percent": 100.0,
            "null_count": 0,
        }],
    }
    state, captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    assert tuple(controls["row_key_columns"].value) == ("column_0", "column_1")
    assert captures["grain"][0]["profile_key_candidates"][0]["columns"] == [
        "column_0", "column_1"
    ]
    assert "Profile evidence" in controls["grain_profile_evidence"].value
    assert "Profiled row key" in controls["grain_ai"].value
    assert "<details" in controls["grain_ai"].value
    assert "Why this suggestion?" in controls["grain_ai"].value
    assert widget_runtime["calls"]["guardrails"] == []

    controls["save_data_contract"].click()
    saved_uniqueness = next(
        record for record in widget_runtime["calls"]["guardrails"][-1]
        if record.get("rule_type") == "uniqueness"
    )
    assert module._parameters(saved_uniqueness)["columns"] == ["column_0", "column_1"]


def test_grain_ai_updates_wording_without_overwriting_manual_row_key(widget_runtime, monkeypatch):
    """AI can suggest Grain wording, but Engineering/manual evidence owns the row key."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    controls["row_key_columns"].value = ("column_1",)
    table_summary = controls["left_pane"].children[0].value
    assert "Row Key" in table_summary
    assert "column_1" in table_summary

    controls["accept_grain"].click()
    assert controls["table_grain"].value == "One row represents a single order line."
    assert tuple(controls["row_key_columns"].value) == ("column_1",)
    table_summary = controls["left_pane"].children[0].value
    assert "One row represents a single order line." in table_summary
    assert "column_1" in table_summary


def test_processing_and_business_rule_changes_refresh_left_table_summary(widget_runtime, monkeypatch):
    """Hydrate left-side Table values changed from Processing and Business Rules editors."""
    widget_runtime["guardrails"][:] = [
        rule for rule in widget_runtime["guardrails"]
        if str(rule.get("guardrail_type") or "").lower() not in {"data_quality", "dq"}
    ]
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    controls["load_strategy"].value = "scd1"
    table_summary = controls["left_pane"].children[0].value
    assert "Load strategy" in table_summary
    assert "SCD1" in table_summary
    assert "data_quality" not in controls["sidebar_rule_buttons"]

    monkeypatch.setattr(
        module,
        "suggest_business_rule",
        lambda *_args, **_kwargs: [{
            "rule_type": "column_relationship",
            "columns": ["column_0", "column_1"],
            "parameters": {
                "columns": ["column_0", "column_1"],
                "operator": "=",
                "business_requirement": "Columns must match.",
            },
            "rationale": "Deterministic relationship.",
        }],
    )
    controls["top_nav"].value = "Business Rules"
    controls["business_requirement"].value = "Columns must match."
    controls["business_columns"].value = ("column_0", "column_1")
    controls["resolve_business_rule"].click()
    controls["apply_business_rule"].click()

    controls["top_nav"].value = "Table"
    table_summary = controls["left_pane"].children[0].value
    assert "data_quality" in controls["sidebar_rule_buttons"]


def test_business_rule_delete_requires_confirmation_and_stages_removal(
    widget_runtime, monkeypatch
):
    """Delete removes only the selected draft Business Rule after explicit confirmation."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    controls["top_nav"].value = "Business Rules"

    controls["business_saved"].value = "advanced"
    assert controls["delete_business_rule"].disabled is False
    assert controls["delete_business_rule_confirm"].layout.display == "none"

    controls["delete_business_rule"].click()
    assert controls["delete_business_rule_confirm"].layout.display == ""
    assert any(
        row.get("guardrail_rule_id") == "advanced"
        for row in state["current"]["guardrails"]
    )

    controls["confirm_delete_business_rule"].click()

    assert controls["business_saved"].value == ""
    assert controls["delete_business_rule"].disabled is True
    assert not any(
        row.get("guardrail_rule_id") == "advanced"
        for row in state["current"]["guardrails"]
    )
    assert state["dirty"] is True
    assert "DQ Rule deletion staged" in state["message"]

    controls["save_data_contract"].click()
    assert not any(
        row.get("guardrail_rule_id") == "advanced"
        for row in widget_runtime["calls"]["draft"][-1]["guardrails"]
    )


def test_table_description_ai_uses_grain_and_manual_classification(widget_runtime, monkeypatch):
    """Generate Description after Grain and use manual Classification as context."""
    widget_runtime["enrichment"][:] = [
        row for row in widget_runtime["enrichment"]
        if not (
            not row.get("column_id")
            and row.get("enrichment_type") in {"Description", "Grain"}
        )
    ]
    _state, captures = _open_with_ai(widget_runtime, monkeypatch)

    table_context = captures["enrichment"][0]
    assert table_context["grain"] == "One row represents a single order line."
    assert table_context["classification"] == "Confidential"
    assert captures["grain"]


def test_ai_open_reports_granular_progress(widget_runtime, monkeypatch):
    """Slow AI startup reports the real stage before each blocking suggestion call."""
    widget_runtime["ai_enrichment"]["enabled"] = True
    widget_runtime["enrichment"][:] = [
        row for row in widget_runtime["enrichment"]
        if not (
            not row.get("column_id")
            and row.get("enrichment_type") in {"Description", "Grain"}
        )
    ]
    progress = []
    state = widget_runtime["start"]()

    def enrichment(context, **_kwargs):
        progress.append(state["_controls"]["open_progress"].value)
        level = context["metadata_level"]
        return {"Description": f"Suggested {level} description"}

    def sensitive(context, **_kwargs):
        progress.append(state["_controls"]["open_progress"].value)
        column = context["columns"][0]
        return [{
            "column_name": column["column_name"], "column_id": column["column_id"],
            "pii_type": "none", "pii_label": "Not PII",
            "reason": "No sensitive evidence.", "treatment": "mask",
            "action": "Warn", "parameters": {}, "is_active": False,
        }]

    monkeypatch.setattr(module, "suggest_enrichment", enrichment)
    monkeypatch.setattr(
        module,
        "suggest_grain_key",
        lambda *_args, **_kwargs: {
            "grain": "One row represents a single order line.",
            "key_columns": ["column_0"],
            "rationale": "Profile grounded.",
        },
    )
    monkeypatch.setattr(module, "suggest_sensitive_data", sensitive)

    state["_controls"]["open_with_ai"].click()

    assert "Generating table description" in progress[0]
    assert "Generating first-column description" in progress[1]
    assert "Assessing first column for sensitive data" in progress[2]
    assert state["_controls"]["open_progress"].value == ""


def test_accept_actions_modify_only_their_owned_controls(widget_runtime, monkeypatch):
    """Description and Sensitive Data acceptance stay isolated from manual Classification."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    controls["required"].value = False
    controls["dq_whitelist_values"].value = "keep-me"

    original_classification = controls["column_classification"].value
    controls["accept_column_description"].click()
    assert controls["column_description"].value == "Suggested column description"
    assert controls["column_classification"].value == original_classification
    assert controls["required"].value is False
    assert controls["dq_whitelist_values"].value == "keep-me"

    description = controls["column_description"].value
    controls["accept_sensitive"].click()
    assert controls["pii_type"].value == "direct"
    assert controls["sensitive_treatment"].value == "tokenize"
    assert "sensitive_block" not in controls
    assert controls["column_description"].value == description
    assert controls["column_classification"].value == "Confidential"
    assert controls["required"].value is False
    assert controls["dq_whitelist_values"].value == "keep-me"
    assert widget_runtime["calls"]["guardrails"] == []

    assert widget_runtime["calls"]["guardrails"] == []
    controls["save_data_contract"].click()
    assert widget_runtime["calls"]["draft"], (state.get("message"), state.get("_validation_errors"))
    saved_sensitive = next(
        record for record in widget_runtime["calls"]["guardrails"][-1]
        if record.get("guardrail_type") == "sensitive_data"
    )
    saved_parameters = module._parameters(saved_sensitive)
    assert saved_parameters["pii_type"] == "direct"
    assert saved_parameters["pii_reason"] == "Can uniquely associate a person."


def test_manual_description_change_marks_dependent_ai_stale_and_requests_rerun(
    widget_runtime, monkeypatch
):
    """Changing Description invalidates dependent AI advice without changing manual controls."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    scope = next(iter(state["_ai_suggestions"]))
    column_id = str(controls["column_select"].value)

    controls["column_description"].value = "Edited business description"

    suggestions = state["_ai_suggestions"][scope]["columns"][column_id]
    assert suggestions["description"]["stale"] is True
    assert suggestions["sensitive_data"]["stale"] is True
    assert "Needs refresh" in controls["sensitive_ai"].value


def test_accepting_description_does_not_invalidate_matching_ai_context(
    widget_runtime, monkeypatch
):
    """Accepting the exact AI Description keeps dependent advice current."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    scope = next(iter(state["_ai_suggestions"]))
    column_id = str(controls["column_select"].value)

    controls["accept_column_description"].click()

    suggestions = state["_ai_suggestions"][scope]["columns"][column_id]
    assert suggestions["description"]["stale"] is False
    assert suggestions["sensitive_data"]["stale"] is False


def test_table_context_change_marks_loaded_sensitive_ai_stale(widget_runtime, monkeypatch):
    """Table Description and Classification changes invalidate column-level dependent advice."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    scope = next(iter(state["_ai_suggestions"]))
    column_id = str(controls["column_select"].value)

    controls["table_classification"].value = "Restricted"

    assert state["_ai_suggestions"][scope]["columns"][column_id]["sensitive_data"]["stale"] is True
    assert "Needs refresh" in controls["sensitive_ai"].value


def test_description_rerun_failure_replaces_stale_success(widget_runtime, monkeypatch):
    """A failed Description re-run must surface the error instead of an old suggestion."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    monkeypatch.setattr(
        module,
        "suggest_enrichment",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("AI Functions unavailable")),
    )

    controls["rerun_column_description"].click()

    assert "AI suggestions unavailable" in controls["column_description_ai"].value
    assert state["_ai_failure"] == "AI Functions unavailable"
    assert controls["accept_column_description"].disabled is True
    assert controls["rerun_column_description"].disabled is True


@pytest.mark.parametrize("button, service, pane", [
    ("rerun_table_description", "suggest_enrichment", "table_description_ai"),
    ("rerun_column_description", "suggest_enrichment", "column_description_ai"),
    ("rerun_sensitive", "suggest_sensitive_data", "sensitive_ai"),
    ("suggest_grain", "suggest_grain_key", "grain_ai"),
    ("resolve_business_rule", "suggest_business_rule", "business_proposal"),
])
@pytest.mark.parametrize("failure", [
    RuntimeError("This event loop is already running"),
    ModuleNotFoundError("No module named 'synapse.ml.aifunc'"),
])
def test_unavailable_ai_disables_actions_and_keeps_manual_authoring(
    widget_runtime, monkeypatch, button, service, pane, failure
):
    """Runtime failures disable AI throughout the session without showing internals."""
    state, captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    attempts = []

    def unavailable(*_args, **_kwargs):
        attempts.append(service)
        raise failure

    monkeypatch.setattr(module, service, unavailable)
    controls[button].click()

    assert attempts == [service]
    assert state["_ai_failure"] == str(failure)
    assert "AI suggestions unavailable" in controls[pane].value
    assert str(failure) not in controls[pane].value
    for name in (
        "open_with_ai", "rerun_table_description", "rerun_column_description",
        "rerun_sensitive", "suggest_grain", "resolve_business_rule",
    ):
        assert controls[name].disabled, name
        controls[name].click()
    assert attempts == [service]
    assert controls["column_description"].disabled is False
    controls["column_description"].value = "Manual description"
    assert not state["_validation_errors"]

    successful_calls = {name: len(values) for name, values in captures.items()}
    controls["column_select"].value = "col-1"
    assert attempts == [service]
    assert {name: len(values) for name, values in captures.items()} == successful_calls
    assert controls["rerun_column_description"].disabled
    assert controls["rerun_sensitive"].disabled
    assert "AI suggestions unavailable" in controls["column_description_ai"].value


@pytest.mark.parametrize("failure_action", ["resolve_business_rule", "rerun_column_description"])
def test_unavailable_ai_clears_previous_business_generation_validation(
    widget_runtime, monkeypatch, failure_action
):
    """An earlier AI response error must not block manual saves after AI becomes unavailable."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    failures = iter([ValueError("Invalid AI response"), RuntimeError("This event loop is already running")])

    def unavailable(*_args, **_kwargs):
        raise next(failures)

    monkeypatch.setattr(module, "suggest_business_rule", unavailable)
    controls["resolve_business_rule"].click()
    assert "business_rule_ai" in state["_validation_errors"]
    assert controls["resolve_business_rule"].disabled is False

    monkeypatch.setattr(module, "suggest_enrichment", unavailable)
    state["_validation_errors"]["business_rule"] = "Authored rule needs correction"
    controls[failure_action].click()
    assert controls["resolve_business_rule"].disabled
    assert "business_rule_ai" not in state["_validation_errors"]
    assert state["_validation_errors"]["business_rule"] == "Authored rule needs correction"
    state["_validation_errors"].pop("business_rule")
    controls["column_description"].value = "Manually authored description"
    controls["save_data_contract"].click()
    assert widget_runtime["calls"]["draft"]


def test_unavailable_ai_during_open_stops_further_calls(widget_runtime, monkeypatch):
    """The first runtime failure disables automatic AI work and the Open with AI action."""
    captures = _enable_ai(widget_runtime, monkeypatch)
    attempts = []

    def unavailable(*_args, **_kwargs):
        attempts.append("grain")
        raise RuntimeError("This event loop is already running")

    monkeypatch.setattr(module, "suggest_grain_key", unavailable)
    state = widget_runtime["start"]()
    state["_controls"]["open_with_ai"].click()
    controls = state["_controls"]

    assert attempts == ["grain"]
    assert captures == {"enrichment": [], "sensitive": [], "grain": []}
    assert state["current"] is not None
    assert "AI suggestions unavailable" in state["message"]
    assert "event loop" not in state["message"]
    assert controls["open_with_ai"].disabled
    assert controls["rerun_table_description"].disabled
    assert controls["rerun_column_description"].disabled
    assert controls["rerun_sensitive"].disabled
    assert controls["resolve_business_rule"].disabled
    assert controls["column_description"].disabled is False

    controls["change_table"].click()
    controls["open_without_ai"].click()
    controls = state["_controls"]
    assert state["current"] is not None
    assert controls["open_with_ai"].disabled
    assert controls["rerun_table_description"].disabled
    assert controls["rerun_column_description"].disabled
    assert controls["rerun_sensitive"].disabled
    assert controls["column_description"].disabled is False
    assert attempts == ["grain"]
    assert captures == {"enrichment": [], "sensitive": [], "grain": []}


def test_sensitive_pii_assessment_requires_reason_before_save(widget_runtime):
    """Do not silently discard a reviewed Direct or Indirect PII assessment."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["pii_type"].value = "indirect"
    controls["pii_reason"].value = ""
    before = len(widget_runtime["calls"]["guardrails"])


    assert len(widget_runtime["calls"]["guardrails"]) == before
    assert any(
        "Explain why this column is Direct or Indirect PII." in message
        for message in state["_validation_errors"].values()
    )
    controls["save_data_contract"].click()
    assert "Complete the current draft configuration before saving" in state["message"]


def test_sensitive_generation_preserves_existing_unsaved_column_draft(widget_runtime, monkeypatch):
    """Regress PR 1375: PII generation never overwrites unrelated draft fields."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    controls["column_description"].value = "Unsaved description"
    controls["column_classification"].value = "Restricted"
    controls["dq_whitelist_values"].value = "keep-me"
    controls["column_select"].value = "col-1"
    controls["column_select"].value = "col-0"

    controls["rerun_sensitive"].click()

    assert controls["column_description"].value == "Unsaved description"
    assert controls["column_classification"].value == "Restricted"
    assert controls["dq_whitelist_values"].value == "keep-me"


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
    controls["table_description"].value = "Current unsaved table description"
    controls["column_description"].value = "Current unsaved description"
    controls["column_classification"].value = "Restricted"
    controls["rerun_column_description"].click()
    controls["rerun_sensitive"].click()

    assert captures["enrichment"][-1]["existing_description"] == "Current unsaved description"
    assert captures["sensitive"][-1]["table_description"] == "Current unsaved table description"
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
        module, "suggest_grain_key",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("AI Functions unavailable")),
    )
    monkeypatch.setattr(
        module, "suggest_sensitive_data",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("malformed AI response")),
    )
    state = widget_runtime["start"]()
    assert all(not errors for errors in state["_ai_errors"].values())
    state["_controls"]["open_with_ai"].click()
    controls = state["_controls"]
    assert controls["column_description"].disabled is False
    controls["column_description"].value = "Manual still works"
    assert widget_runtime["calls"]["enrichment"] == []
    assert state["_pending_enrichment"]
    controls["save_data_contract"].click()
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


def test_freshness_filters_to_temporal_columns_and_explains_live_rule(widget_runtime):
    """Freshness authoring only offers temporal columns and translates controls into a rule."""
    state = widget_runtime["open"]()
    freshness = state["_controls"]["table_guardrails"]["freshness"]

    freshness_grid = freshness["display"][1]
    assert [row.children[0].value for row in freshness_grid.children] == [
        "<div style='padding-top:7px;'>Refresh expectation</div>",
        "<div style='padding-top:7px;'>Timestamp column</div>",
        "<div style='padding-top:7px;'>Expected refresh</div>",
        "<div style='padding-top:7px;'>Maximum age</div>",
    ]
    options = [
        item[1] if isinstance(item, tuple) else item
        for item in freshness["parameters"][1].options
    ]
    assert options == ["", "column_1"]

    freshness["enabled"].value = True
    freshness["parameters"][0].value = "recurring"
    freshness["parameters"][1].value = "column_1"
    freshness["parameters"][2].value = "6"
    freshness["parameters"][3].value = "hours"
    freshness["parameters"][4].value = "24"
    freshness["parameters"][5].value = "hours"

    preview = freshness["display"][-1].value
    assert "Expected source refresh: <b>6 hours</b>." in preview
    assert "The latest <code>column_1</code> must be within <b>24 hours</b> of the pipeline run." in preview
    assert "<code>MAX(column_1)</code> must be on or after 1 Jan 2026 23:00." in preview

    freshness_section = state["_controls"]["right_pane"].children[4]
    assert freshness_section.children[1].children[0] is freshness["enabled"]
    assert freshness_section.children[1].children[1] is freshness["block"]
    freshness_primary = freshness_section.children[2]
    assert "Applies when this table is used as a source in a downstream pipeline." in freshness_primary.children[0].value
    assert "not when this table itself is written" in freshness_primary.children[0].value


def test_static_source_does_not_require_temporal_columns(widget_runtime):
    """A static source can explicitly declare that no refresh is expected."""
    widget_runtime["catalogue"][2]["data_type"] = "string"

    state = widget_runtime["open"]()
    freshness = state["_controls"]["table_guardrails"]["freshness"]

    freshness["enabled"].value = True
    freshness["parameters"][0].value = "static"

    assert freshness["parameters"][0].disabled is False
    assert freshness["parameters"][1].disabled is True
    assert freshness["block"].disabled is True
    assert "No refresh is expected for this source" in freshness["display"][-1].value
    assert "Source Drift" in freshness["display"][-1].value


def test_static_freshness_stages_skip_rule(widget_runtime):
    """Static source expectation persists as an explicit skip Freshness rule."""
    widget_runtime["guardrails"][:] = [
        rule for rule in widget_runtime["guardrails"]
        if rule["guardrail_type"] != "freshness"
    ]
    state = widget_runtime["open"]()
    freshness = state["_controls"]["table_guardrails"]["freshness"]

    freshness["enabled"].value = True
    freshness["parameters"][0].value = "static"

    staged = next(
        record for records in state["_pending_guardrails"].values()
        for record in records.values()
        if record.get("guardrail_type") == "freshness"
    )
    assert staged["rule_type"] == "skip"
    assert module._parameters(staged) == {"refresh_expectation": "static"}
    assert "Expected source refresh" in state["_controls"]["left_pane"].children[0].value
    assert "No refresh expected" in state["_controls"]["left_pane"].children[0].value


def test_new_table_guardrails_require_and_save_canonical_parameters(widget_runtime):
    """New Freshness and Source Drift rules stage live and block final save while incomplete."""
    widget_runtime["guardrails"][:] = [
        rule for rule in widget_runtime["guardrails"]
        if rule["guardrail_type"] not in {"freshness", "source_drift"}
    ]
    state = widget_runtime["open"]()
    freshness = state["_controls"]["table_guardrails"]["freshness"]
    freshness["enabled"].value = True
    before = len(widget_runtime["calls"]["guardrails"])
    assert len(widget_runtime["calls"]["guardrails"]) == before
    assert any(
        "could not convert string to float" in message
        for message in state["_validation_errors"].values()
    )

    freshness["parameters"][0].value = "recurring"
    freshness["parameters"][1].value = "column_1"
    freshness["parameters"][2].value = "1"
    freshness["parameters"][3].value = "days"
    freshness["parameters"][4].value = "6"
    freshness["parameters"][5].value = "hours"
    assert widget_runtime["calls"]["guardrails"] == []
    staged = next(
        record for records in state["_pending_guardrails"].values()
        for record in records.values()
        if record.get("guardrail_type") == "freshness"
    )
    assert module._parameters(staged) == {
        "refresh_expectation": "recurring",
        "freshness_column": "column_1",
        "expected_refresh_frequency": 1.0,
        "expected_refresh_unit": "days",
        "maximum_age": 6.0,
        "maximum_age_unit": "hours",
    }

    drift = state["_controls"]["table_guardrails"]["source_drift"]
    drift["enabled"].value = True
    drift_grid = drift["display"][0]
    assert [drift_grid.children[index].value for index in (0, 2)] == [
        "<div style='padding-top:7px;'>Partition column</div>",
        "<div style='padding-top:7px;'>Change tracking column</div>",
    ]
    drift["parameters"][0].value = "column_0"
    drift["parameters"][1].value = "column_1"
    drift_preview = drift["display"][-1].value
    assert "last successfully consumed state for that downstream target" in drift_preview
    assert "row count, <code>column_1</code> values, and a content fingerprint" in drift_preview

    drift_section = state["_controls"]["right_pane"].children[5]
    assert drift_section.children[1].children[0] is drift["enabled"]
    assert drift_section.children[1].children[1] is drift["block"]
    drift_primary = drift_section.children[2]
    assert "Applies when this table is used as a source in a downstream pipeline." in drift_primary.children[0].value
    assert "previously consumed from this table has changed" in drift_primary.children[1].value

    staged_drift = next(
        record for records in state["_pending_guardrails"].values()
        for record in records.values()
        if record.get("guardrail_type") == "source_drift"
    )
    assert module._parameters(staged_drift) == {
        "partition_column": "column_0", "change_column": "column_1",
    }
    state["_controls"]["save_data_contract"].click()
    assert widget_runtime["calls"]["guardrails"]


def test_disabled_guardrail_is_preserved_in_draft_json(widget_runtime):
    """Disabled Guardrails stay in the draft JSON so they can be re-enabled later."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    freshness = controls["table_guardrails"]["freshness"]

    freshness["enabled"].value = False
    controls["save_data_contract"].click()

    saved = widget_runtime["calls"]["draft"][-1]
    rule = next(
        item for item in saved["guardrails"]
        if item.get("guardrail_rule_id") == "fresh"
    )
    assert rule["is_active"] is False
    assert state["_controls"]["table_guardrails"]["freshness"]["enabled"].value is False


def test_invalid_dq_input_is_reported_in_status_without_persisting(widget_runtime):
    """Parameter conversion failures remain inside the widget error boundary."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    before = len(widget_runtime["calls"]["guardrails"])
    controls["dq_completeness_failure"].value = "not-a-number"


    assert len(widget_runtime["calls"]["guardrails"]) == before
    assert any(
        "could not convert string to float" in message
        for message in state["_validation_errors"].values()
    )


def test_pattern_is_owned_by_dq_rules_not_columns(widget_runtime):
    """Pattern remains a supported DQ Rule without exposing regex authoring in Columns."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    assert "pattern" not in controls["dq_family_controls"]
    assert "dq_pattern" not in controls
    pattern_options = [
        (label, value)
        for label, value in controls["business_saved"].options
        if label == "Pattern · column_0"
    ]
    assert pattern_options == [("Pattern · column_0", "dq-pattern")]


def test_review_sections_render_column_contract_table_with_profile_and_governance():
    """Render table guardrails, rich column rows, then Business Rules."""
    payload = {
        "table": {
            "table_name": "orders", "schema_name": "sales",
            "columns": [
                {
                    "column_id": "col-1", "column_name": "customer_id",
                    "data_type": "string",
                },
            ],
        },
        "contract": {"contract_version": 1, "status": "draft"},
        "enrichment": {
            "columns": [
                {
                    "column_id": "col-1", "enrichment_type": "Description",
                    "value": "Customer identifier",
                },
                {
                    "column_id": "col-1", "enrichment_type": "Classification",
                    "value": "Confidential",
                },
            ],
        },
        "guardrails": [
            {
                "guardrail_type": "schema", "rule_type": "required_columns", "column_id": "",
                "rule_parameters": {"required_columns": ["col-1"]},
            },
            {"guardrail_type": "freshness", "rule_type": "freshness", "column_id": ""},
            {
                "guardrail_type": "sensitive_data", "rule_type": "mask", "column_id": "col-1",
                "action": "Block",
                "rule_parameters": {"pii_type": "direct", "treatment": "mask"},
            },
            {
                "guardrail_type": "data_quality", "rule_type": "pattern", "column_id": "col-1",
                "action": "Warn", "rule_parameters": {"pattern": "^CUS-[0-9]+$"},
            },
            {"guardrail_type": "data_quality", "rule_type": "uniqueness", "column_id": ""},
            {"guardrail_type": "data_quality", "rule_type": "column_relationship", "column_id": ""},
            {"guardrail_type": "data_quality", "rule_type": "custom_expression", "column_id": ""},
        ],
    }
    profiles = {
        "col-1": {
            "row_count": 120, "null_count": 0, "null_percent": 0.0,
            "distinct_count": 120, "distinct_percent": 100.0,
            "min_value": "CUS-001", "max_value": "CUS-120",
            "example_values": ["CUS-042", "CUS-017"],
        },
    }

    sections = module._manifest_sections(payload, column_profiles=profiles)

    assert set(sections) == {"Review"}
    review = sections["Review"]
    assert review.index("<b>Column definitions</b>") < review.index("<b>Guardrails</b>")
    assert "<b>Column definitions</b> · 1 columns" in review
    assert "<b>Guardrails</b> · 7 configured" in review
    assert ">Column</th>" in review
    assert ">Examples</th>" in review
    assert ">Datatype</th>" in review
    assert ">Required</th>" in review
    assert ">Sensitive</th>" in review
    assert ">Classification</th>" in review
    assert ">Description</th>" in review
    assert "CUS-042<br>CUS-017" in review
    assert "<th>Profile</th>" not in review
    assert "<th>Rules</th>" not in review
    assert "<b>Table</b>" in review
    assert "<b>Columns</b>" in review
    assert "<b>DQ Rules</b>" in review
    assert "Customer identifier" in review
    assert "Confidential" in review
    assert "Direct PII · Mask" in review
    assert "Required" in review and ">Yes<" in review
    assert "required columns: customer_id" in review
    assert "required columns: col-1" not in review
    assert review.count("<b>Pattern</b>") == 1

    fallback = module._manifest_sections(
        payload,
        column_profiles={
            "col-1": {"min_value": "CUS-001", "max_value": "CUS-120"},
        },
    )["Review"]
    assert "CUS-001<br>CUS-120" in fallback


def test_column_authored_dq_rule_appears_in_shared_dq_rules_list(
    widget_runtime, monkeypatch
):
    """Column DQ edits hydrate the Business Rules page from the same staged draft state."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    controls["top_nav"].value = "Column"
    controls["dq_family_controls"]["completeness"]["enabled"].value = True

    controls["top_nav"].value = "Business Rules"
    labels = [label for label, _value in controls["business_saved"].options]

    assert any("Completeness" in label and "column_0" in label for label in labels)


def test_business_rule_resolve_apply_stages_existing_guardrail_model(
    widget_runtime, monkeypatch
):
    """Resolve natural-language intent and Apply it into normal staged Guardrail state."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    def resolve(_context, **kwargs):
        assert kwargs["requirement"] == "End date must be on or after start date."
        assert kwargs["relevant_columns"] == ["column_0", "column_1"]
        return [{
            "rule_type": "column_relationship",
            "columns": ["column_1", "column_0"],
            "parameters": {
                "columns": ["column_1", "column_0"],
                "operator": ">=",
                "business_requirement": kwargs["requirement"],
            },
            "business_requirement": kwargs["requirement"],
            "rationale": "Direct two-column comparison.",
            "engineering_review_required": False,
        }]

    monkeypatch.setattr(module, "suggest_business_rule", resolve)
    controls["top_nav"].value = "Business Rules"
    controls["business_saved"].value = ""
    controls["business_requirement"].value = "End date must be on or after start date."
    controls["business_columns"].value = ("column_0", "column_1")
    controls["resolve_business_rule"].click()

    assert "Column Relationship" in controls["business_proposal"].value
    assert "column_1, column_0" in controls["business_proposal"].value
    assert controls["apply_business_rule"].disabled is False

    controls["apply_business_rule"].click()

    staged = next(
        record for records in state["_pending_guardrails"].values()
        for record in records.values()
        if record.get("rule_type") == "column_relationship"
        and module._parameters(record).get("business_requirement")
        == "End date must be on or after start date."
    )
    assert staged["guardrail_type"] == "data_quality"
    assert module._parameters(staged)["operator"] == ">="
    assert widget_runtime["calls"]["guardrails"] == []
    assert "Save Data Contract to persist" in state["message"]


def test_multiple_business_rules_remain_independent(widget_runtime, monkeypatch):
    """Applying a new Business Rule must append rather than replace another rule."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    requirements = [
        "End date must be on or after start date.",
        "Start date must be on or before end date.",
    ]

    def resolve(_context, **kwargs):
        requirement = kwargs["requirement"]
        return [{
            "rule_type": "column_relationship",
            "parameters": {
                "columns": ["column_1", "column_0"],
                "operator": ">=" if requirement == requirements[0] else "<=",
                "business_requirement": requirement,
            },
            "business_requirement": requirement,
            "engineering_review_required": False,
        }]

    monkeypatch.setattr(module, "suggest_business_rule", resolve)
    controls["top_nav"].value = "Business Rules"
    for requirement in requirements:
        controls["business_saved"].value = ""
        controls["business_requirement"].value = requirement
        controls["business_columns"].value = ("column_0", "column_1")
        controls["resolve_business_rule"].click()
        controls["apply_business_rule"].click()

    staged = [
        record for records in state["_pending_guardrails"].values()
        for record in records.values()
        if record.get("rule_type") == "column_relationship"
    ]
    assert len(staged) == 2
    assert {
        module._parameters(record)["business_requirement"] for record in staged
    } == set(requirements)


def test_multiple_uniqueness_business_rules_do_not_replace_table_grain(
    widget_runtime, monkeypatch
):
    """Repeatable uniqueness constraints stay separate from the singular Grain & Row Key."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    controls["row_key_columns"].value = ("column_0",)

    requirements = [
        ("column_0 must be unique.", ["column_0"]),
        ("column_0 and column_1 together must also be unique.", ["column_0", "column_1"]),
    ]

    def resolve(_context, **kwargs):
        columns = next(cols for requirement, cols in requirements if requirement == kwargs["requirement"])
        return [{
            "rule_type": "uniqueness",
            "parameters": {
                "columns": columns,
                "business_requirement": kwargs["requirement"],
            },
            "business_requirement": kwargs["requirement"],
            "engineering_review_required": False,
        }]

    monkeypatch.setattr(module, "suggest_business_rule", resolve)
    controls["top_nav"].value = "Business Rules"
    for requirement, columns in requirements:
        controls["business_saved"].value = ""
        controls["business_requirement"].value = requirement
        controls["business_columns"].value = tuple(columns)
        controls["resolve_business_rule"].click()
        controls["apply_business_rule"].click()

    staged_uniqueness = [
        record for records in state["_pending_guardrails"].values()
        for record in records.values()
        if record.get("rule_type") == "uniqueness"
        and module._parameters(record).get("business_requirement")
    ]
    assert len(staged_uniqueness) == 2
    assert {tuple(module._parameters(record)["columns"]) for record in staged_uniqueness} == {
        ("column_0",), ("column_0", "column_1"),
    }
    assert controls["row_key_columns"].value == ("column_0",)


def test_pattern_business_rule_is_owned_by_dq_rules(widget_runtime, monkeypatch):
    """Create Pattern through the Business Rules workflow without a column regex editor."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    requirement = "Order ID must start with ORD- followed by digits."

    def resolve(_context, **kwargs):
        return [{
            "rule_type": "pattern",
            "columns": ["column_0"],
            "parameters": {
                "columns": ["column_0"],
                "pattern": "^ORD-[0-9]+$",
                "business_requirement": kwargs["requirement"],
            },
            "business_requirement": kwargs["requirement"],
            "engineering_review_required": False,
        }]

    monkeypatch.setattr(module, "suggest_business_rule", resolve)
    controls["top_nav"].value = "Business Rules"
    controls["business_requirement"].value = requirement
    controls["business_columns"].value = ("column_0",)
    controls["resolve_business_rule"].click()
    controls["apply_business_rule"].click()

    staged = next(
        record for records in state["_pending_guardrails"].values()
        for record in records.values()
        if record.get("rule_type") == "pattern"
        and module._parameters(record).get("business_requirement") == requirement
    )
    assert staged["column_id"] == ""
    assert module._parameters(staged)["pattern"] == "^ORD-[0-9]+$"
    assert any(
        label == "Pattern · column_0"
        for label, _value in controls["business_saved"].options
    )


def test_single_column_business_rule_hydrates_column_rule(widget_runtime, monkeypatch):
    """A simple resolved rule belongs to Columns and hydrates its normal DQ editor."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    def resolve(_context, **kwargs):
        return [{
            "rule_type": "completeness",
            "parameters": {
                "columns": ["column_0"],
                "maximum_missing_percent": 0,
                "treat_blank_as_missing": False,
                "business_requirement": kwargs["requirement"],
            },
            "business_requirement": kwargs["requirement"],
            "engineering_review_required": False,
        }]

    monkeypatch.setattr(module, "suggest_business_rule", resolve)
    controls["top_nav"].value = "Business Rules"
    controls["business_requirement"].value = "Order identifier is always required."
    controls["business_columns"].value = ("column_0",)
    controls["resolve_business_rule"].click()
    controls["apply_business_rule"].click()

    staged = next(
        record for records in state["_pending_guardrails"].values()
        for record in records.values()
        if record.get("rule_type") == "completeness"
        and module._parameters(record).get("business_requirement")
        == "Order identifier is always required."
    )
    assert staged["column_id"] == "col-0"
    assert controls["business_saved"].value

    controls["top_nav"].value = "Column"
    assert float(controls["dq_completeness_failure"].value) == 0
    assert controls["dq_family_controls"]["completeness"]["enabled"].value is True
    assert "DQ Rule added to the current draft" in state["message"]


def test_custom_business_rule_requires_engineering_review_before_freeze(
    widget_runtime, monkeypatch
):
    """Custom Expressions stage pending review and require an explicit engineer approval."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    def resolve(_context, **kwargs):
        return [{
            "rule_type": "custom_expression",
            "parameters": {
                "expression_language": "pyspark",
                "expression": '(F.col("status") != "Approved") | F.col("approved_date").isNotNull()',
                "business_requirement": kwargs["requirement"],
                "columns": ["column_0", "column_1"],
                "engineering_review_required": True,
            },
            "business_requirement": kwargs["requirement"],
            "rationale": "Conditional cross-column requirement.",
            "engineering_review_required": True,
        }]

    monkeypatch.setattr(module, "suggest_business_rule", resolve)
    controls["top_nav"].value = "Business Rules"
    controls["business_requirement"].value = "Approved rows require an approved date."
    controls["resolve_business_rule"].click()
    controls["apply_business_rule"].click()

    pending = next(
        record for records in state["_pending_guardrails"].values()
        for record in records.values()
        if record.get("rule_type") == "custom_expression"
    )
    assert module._parameters(pending)["engineering_review_status"] == "pending"
    assert controls["engineering_review_panel"].layout.display == ""
    assert "Engineering review pending" in controls["engineering_review_status"].value

    controls["approve_engineering_review"].click()
    assert any(
        "Engineering reviewer is required" in message
        for message in state["_validation_errors"].values()
    )

    controls["engineering_reviewer"].value = "data.engineer@example.com"
    controls["engineering_review_note"].value = "Expression and referenced columns reviewed."
    controls["approve_engineering_review"].click()

    approved = next(
        record for records in state["_pending_guardrails"].values()
        for record in records.values()
        if record.get("rule_type") == "custom_expression"
    )
    params = module._parameters(approved)
    assert params["engineering_review_status"] == "approved"
    assert params["engineering_reviewed_by"] == "data.engineer@example.com"
    assert params["engineering_review_note"] == "Expression and referenced columns reviewed."
    assert "Engineering review approved" in controls["engineering_review_status"].value


def test_column_uniqueness_failure_rate_round_trips(widget_runtime):
    """Author and hydrate one accepted duplicate-row failure rate."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    families = controls["dq_family_controls"]

    assert "uniqueness" in families
    assert controls["dq_uniqueness_failure"].value == "0"

    families["uniqueness"]["enabled"].value = True
    families["uniqueness"]["block"].value = True
    controls["dq_uniqueness_failure"].value = "5"

    assert widget_runtime["calls"]["guardrails"] == []
    controls["save_data_contract"].click()

    saved = next(
        record for record in widget_runtime["calls"]["guardrails"][-1]
        if record.get("rule_type") == "uniqueness"
        and record.get("column_id") == "col-0"
    )
    assert saved["action"] == "Block"
    assert module._parameters(saved) == {
        "columns": ["column_0"],
        "maximum_failure_percent": 5.0,
    }
    reopened = widget_runtime["open"]()["_controls"]
    assert float(reopened["dq_uniqueness_failure"].value) == 5
    assert reopened["dq_family_controls"]["uniqueness"]["block"].value is True
    reopened["column_select"].value = "col-1"
    assert float(reopened["dq_uniqueness_failure"].value) == 0
    reopened["column_select"].value = "col-0"
    assert float(reopened["dq_uniqueness_failure"].value) == 5
    assert "dq_min_unique" not in reopened and "dq_max_missing" not in reopened
    for family in reopened["dq_family_controls"].values():
        assert tuple(family["block"].options) == (("Warn", False), ("Block", True))


def test_value_lists_create_independent_whitelist_and_blacklist_rules(widget_runtime):
    """Whitelist and Blacklist render as two text lists and persist as separate value-set rules."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    family = controls["dq_family_controls"]["value_set"]

    assert len(family["display"]) == 2
    controls["dq_whitelist_values"].value = "Active, Inactive, Pending"
    controls["dq_whitelist_max_failure"].value = "2"
    controls["dq_blacklist_values"].value = "Unknown, N/A"
    assert "3 values" in controls["dq_whitelist_count"].value
    assert "2 values" in controls["dq_blacklist_count"].value
    assert "comma-separated" in controls["dq_whitelist_count"].value

    family["enabled"].value = True
    family["block"].value = True
    controls["save_data_contract"].click()

    rules = [
        record for record in widget_runtime["calls"]["guardrails"][-1]
        if record.get("rule_type") == "value_set"
        and record.get("column_id") == "col-0"
        and record.get("is_active")
    ]
    assert len(rules) == 2
    by_mode = {
        module._parameters(record)["mode"]: module._parameters(record)
        for record in rules
    }
    assert by_mode["allow"]["values"] == ["Active", "Inactive", "Pending"]
    assert by_mode["allow"]["maximum_failure_percent"] == 2
    assert by_mode["block"]["values"] == ["Unknown", "N/A"]
    assert "maximum_failure_percent" not in by_mode["block"]
    assert all(record["action"] == "Block" for record in rules)


def test_dq_parameter_checkboxes_align_with_the_fields_they_modify(widget_runtime):
    """Completeness and range options stay grouped below their full-width field."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    completeness_row = controls["dq_family_controls"]["completeness"]["display"][0]
    lower_row, upper_row, tolerance = controls["dq_family_controls"]["range"]["display"]
    assert tolerance is controls["dq_range_max_failure"]

    assert completeness_row.children == (
        controls["dq_completeness_failure"], controls["dq_blank_missing"]
    )
    assert lower_row.children == (
        controls["dq_minimum"], controls["dq_minimum_inclusive"]
    )
    assert upper_row.children == (
        controls["dq_maximum"], controls["dq_maximum_inclusive"]
    )
    assert lower_row.layout.align_items == "stretch"
    assert upper_row.layout.align_items == "stretch"


def test_range_is_directly_authored_and_saves_without_ai(widget_runtime):
    """Range stays deterministic: edit bounds directly and persist them on contract save."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    before = len(widget_runtime["calls"]["guardrails"])

    controls["dq_family_controls"]["range"]["enabled"].value = True
    controls["dq_minimum"].value = "1"
    controls["dq_minimum_inclusive"].value = True
    controls["dq_maximum"].value = "100"
    controls["dq_maximum_inclusive"].value = False
    controls["dq_range_max_failure"].value = "1.5"

    assert len(widget_runtime["calls"]["guardrails"]) == before
    controls["save_data_contract"].click()

    saved = next(
        record for record in widget_runtime["calls"]["guardrails"][-1]
        if record.get("rule_type") == "range"
    )
    assert saved["column_id"] == "col-0"
    assert module._parameters(saved) == {
        "columns": ["column_0"],
        "minimum": "1",
        "minimum_inclusive": True,
        "maximum": "100",
        "maximum_inclusive": False,
        "maximum_failure_percent": 1.5,
    }


def test_business_rule_tolerance_control_follows_selected_rule(widget_runtime, monkeypatch):
    """Business Rules expose the applicable percentage and keep prohibited values strict."""
    state, _ = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    monkeypatch.setattr(module, "suggest_business_rule", lambda *_args, **_kwargs: [
        {"rule_type": "pattern", "columns": ["column_0"],
         "parameters": {"columns": ["column_0"], "pattern": "^[0-9]+$", "maximum_failure_percent": 2}},
        {"rule_type": "value_set", "columns": ["column_0"],
         "parameters": {"columns": ["column_0"], "mode": "block", "values": ["forbidden"]}},
    ])
    controls["business_requirement"].value = "Allow 2% format violations; prohibited values are never acceptable."
    controls["resolve_business_rule"].click()
    assert controls["business_tolerance"].layout.display == ""
    assert float(controls["business_tolerance"].value) == 2
    controls["business_tolerance"].value = "3"
    controls["business_proposal_select"].value = 1
    assert controls["business_tolerance"].layout.display == "none"
    controls["business_proposal_select"].value = 0
    assert float(controls["business_tolerance"].value) == 3
    controls["apply_business_rule"].click()
    staged = [row for records in state["_pending_guardrails"].values() for row in records.values()]
    pattern = next(row for row in staged if row.get("rule_type") == "pattern")
    assert module._parameters(pattern)["maximum_failure_percent"] == 3


def test_schedule_is_read_from_catalogue_without_cross_workspace_discovery(widget_runtime):
    """Governance consumes writer-captured Scheduled Refresh from Catalogue."""
    state = widget_runtime["open"]()

    assert state["scheduled_refresh"] == {
        "status": "configured",
        "schedules": [{
            "enabled": True, "frequency": "daily", "times": ["08:00"],
            "timezone": "Asia/Singapore",
        }],
    }
    summary = state["_controls"]["left_pane"].children[0].value
    assert "Scheduled refresh" in summary
    assert "Daily · 08:00 · Asia/Singapore" in summary


def test_uncaptured_schedule_is_not_misreported_and_blocks_freeze(widget_runtime):
    """A profiled-only Catalogue row is not equivalent to no configured schedule."""
    widget_runtime["catalogue"][0]["scheduled_refresh_json"] = None
    state = widget_runtime["open"]()

    assert state["scheduled_refresh"] == {"status": "uncaptured", "schedules": []}
    assert "Not captured" in state["_controls"]["left_pane"].children[0].value
    state["_controls"]["freeze"].click()
    state["_controls"]["freeze_confirm"].click()
    assert widget_runtime["calls"]["freeze"] == 0
    assert "Run the writer pipeline before freezing" in state["message"]


def test_freeze_refreshes_manifest_and_keeps_activation_out_of_authoring(widget_runtime):
    """Freeze reloads lifecycle state while immutable authoring stays review-only."""
    state = widget_runtime["open"]()
    before = module.DATA_CONTRACT_MANIFEST
    state["_controls"]["freeze"].click()
    assert widget_runtime["calls"]["freeze"] == 0
    state["_controls"]["freeze_confirm"].click()
    assert widget_runtime["calls"]["freeze"] == 1
    assert state["current"]["contract"]["status"] == "frozen"
    assert state["contracts"][0]["status"] == "frozen"
    assert state["_controls"]["table_description"].disabled is True
    assert module.DATA_CONTRACT_MANIFEST is not before
    assert "activate" not in state
    assert "activate" not in state["_controls"]
    assert widget_runtime["calls"]["activate"] == 0


def test_column_selector_marks_required_columns_and_aligns_checkbox(widget_runtime):
    """Required state stays visible in navigation and the header checkbox stays compact."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["column_select"].value = "col-1"

    label = next(
        label for label, value in controls["column_select"].options if value == "col-1"
    )
    assert label == "column_1"

    controls["required"].value = True

    label = next(
        label for label, value in controls["column_select"].options if value == "col-1"
    )
    assert label == "column_1 *"
    assert "option:nth-child(2)" in controls["column_option_style"].value
    assert "color:var(--form-accent)" in controls["column_option_style"].value
    assert controls["column_header"].children[1] is controls["required"]
    assert controls["column_header"].layout.align_items == "flex-start"
    assert "fabricops-column-required" in controls["required"]._dom_classes
    assert controls["required"].layout.width == "auto"
    assert widget_runtime["calls"]["guardrails"] == []


@pytest.mark.parametrize("identifiers", [["col-0"], ["column_0"], ["col-0", "column_0"]])
def test_clearing_required_removes_id_and_name_through_save_freeze_runtime(widget_runtime, identifiers):
    """Clearing Required removes either identifier without clearing other selections."""
    from fabricops_kit.pipeline import shared

    rule = next(row for row in widget_runtime["guardrails"] if row["guardrail_type"] == "schema")
    rule["rule_parameters_json"] = json.dumps({"required_columns": [*identifiers, "col-1"]})
    payload = json.loads(widget_runtime["contract"]["contract_payload_json"])
    payload["table"]["columns"][1]["presence"] = "required"
    widget_runtime["contract"]["contract_payload_json"] = json.dumps(payload)
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["column_select"].value = "col-0"
    assert controls["required"].value is True
    controls["required"].value = False
    controls["save_data_contract"].click()

    payload = widget_runtime["calls"]["draft"][-1]
    saved = next(row for row in payload["guardrails"] if row["guardrail_type"] == "schema")
    assert saved["rule_parameters"] == {"required_columns": ["col-1"]}
    state["_controls"]["open"].click()
    controls = state["_controls"]
    controls["column_select"].value = "col-0"
    assert controls["required"].value is False
    controls["column_select"].value = "col-1"
    assert controls["required"].value is True

    frozen = module.contracts.freeze_contract_record(
        draft={
            "contract_id": "contract-orders", "contract_version": 1,
            "table_id": "orders", "status": "draft", "contract_payload_json": json.dumps(payload),
        }, audit={},
    )
    rows = shared.contract_guardrail_rows(frozen, workspace_id="dev", table_id="orders")
    result = shared.schema_check_core(
        types.SimpleNamespace(columns=["column_1"], dtypes=[("column_1", "timestamp")]),
        rules_df=rows, table_id="orders", workspace_id="dev",
    )
    assert result["missing_columns"] == []
    assert result["status"] == "passed"
    assert result["can_continue"] is True


def test_required_schema_authors_block_and_reaches_runtime(widget_runtime):
    """Required selections save as blocking Schema intent and resolve by frozen ID."""
    from fabricops_kit.pipeline import shared

    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["column_select"].value = "col-1"
    controls["required"].value = True
    controls["save_data_contract"].click()
    payload = widget_runtime["calls"]["draft"][-1]
    schema_rule = next(rule for rule in payload["guardrails"] if rule["guardrail_type"] == "schema")
    assert schema_rule["rule_type"] == "strict"
    assert schema_rule["action"] == "Block"
    assert schema_rule["rule_parameters"] == {"required_columns": ["col-0", "col-1"]}
    frozen = module.contracts.freeze_contract_record(
        draft={
            "contract_id": "contract-orders", "contract_version": 1,
            "table_id": "orders", "status": "draft", "contract_payload_json": json.dumps(payload),
        }, audit={},
    )
    rows = shared.contract_guardrail_rows(frozen, workspace_id="dev", table_id="orders")
    result = shared.schema_check_core(
        types.SimpleNamespace(columns=[], dtypes=[]),
        rules_df=rows, table_id="orders", workspace_id="dev",
    )
    assert result["missing_columns"] == ["column_0", "column_1"]
    assert result["status"] == "failed"
    assert result["can_continue"] is False


def test_table_description_matches_grain_ai_layout(widget_runtime, monkeypatch):
    """Table Description uses the same primary/AI split as Grain & Row Key."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    expected_ai_grid = "minmax(0, 68fr) minmax(240px, 32fr)"
    table_content = controls["table_definition"].children[1]
    grain_content = controls["right_pane"].children[0].children[3]
    assert table_content.layout.grid_template_columns == expected_ai_grid
    assert grain_content.layout.grid_template_columns == expected_ai_grid
    assert table_content.children[1].children[0].value == "<b>AI suggestion</b>"

    expected_column_grid = "120px minmax(240px, 1fr) minmax(240px, 1fr)"
    assert controls["column_definition"].children[1].layout.grid_template_columns == expected_column_grid
    assert controls["table_classification"].layout.width == "250px"
    assert controls["column_classification"].layout.width == "100%"
    assert controls["column_classification"].layout.max_width == "722px"
    assert controls["column_search"].layout.width == "100%"
    assert controls["column_select"].layout.width == "100%"
    assert [label for label, _value in controls["column_select"].options] == [
        "column_0 *",
        "column_1",
    ]
    assert "color:var(--form-accent);font-size:20px" in controls["column_context"].value
    assert "Required:" not in controls["column_context"].value


def test_layout_avoids_blank_spacers_and_collapsed_columns(widget_runtime):
    """Keep form rows explicit, aligned, and free of empty placeholder widgets."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    freshness_layout = controls["table_guardrails"]["freshness"]["display"][1]
    assert len(freshness_layout.children) == 4
    assert [len(row.children) for row in freshness_layout.children] == [2, 2, 3, 3]
    assert all(
        str(getattr(child, "value", "") or "").strip()
        for row in freshness_layout.children
        for child in row.children[:1]
    )

    processing_hint = controls["processing_source"]
    processing_section = controls["right_pane"].children[3]
    processing_hint_row = processing_section.children[2]
    assert processing_hint_row.children == (processing_hint,)
    assert processing_hint_row.layout.align_items == "flex-start"

    column_definition = controls["column_definition"].children[1]
    assert column_definition.layout.grid_template_columns == "120px minmax(240px, 1fr)"
    assert len(column_definition.children) == 2


def test_table_classification_updates_left_summary_immediately(widget_runtime):
    """Table classification feedback follows the staged editor value without a save."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    summary = controls["left_pane"].children[0]

    assert "Confidential" in summary.value
    controls["table_classification"].value = "Restricted"
    assert "Restricted" in summary.value
    assert "Confidential</div>" not in summary.value
    assert widget_runtime["calls"]["enrichment"] == []


def test_datatype_drift_requires_explicit_contract_choice(widget_runtime):
    """Observed datatype drift stays red and does not silently replace the contract type."""
    widget_runtime["catalogue"][1]["data_type"] = "string"
    state = widget_runtime["open"]()
    controls = state["_controls"]

    assert "Datatype drift detected" in controls["column_context"].value
    assert "Contract: <b>long</b>" in controls["column_context"].value
    assert "Observed: <b style='color:#a4262c'>string</b>" in controls["column_context"].value
    assert controls["datatype_choice"].layout.display == ""
    assert controls["datatype_choice"].value == "long"

    controls["datatype_choice"].value = "string"

    assert state["dirty"] is True
    assert "Datatype drift detected" not in controls["column_context"].value
    assert ">string</div>" in controls["column_context"].value
    assert controls["datatype_choice"].layout.display == "none"
    payload = json.loads(state["current"]["contract"]["contract_payload_json"])
    selected = next(item for item in payload["table"]["columns"] if item["column_id"] == "col-0")
    assert selected["data_type"] == "string"
    assert widget_runtime["calls"]["draft"] == []


def test_guardrail_summary_tracks_working_controls_before_save(widget_runtime):
    """The Table summary reflects working Guardrail state before persistence."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    assert "freshness" in controls["sidebar_rule_buttons"]
    controls["table_guardrails"]["freshness"]["enabled"].value = False
    assert "freshness" in controls["sidebar_rule_buttons"]
    assert "Disabled · intentionally not executed" in _sidebar_text(controls["guardrail_sidebar"])
    assert widget_runtime["calls"]["guardrails"] == []


def test_manifest_description_is_truncated_and_expandable(widget_runtime):
    """Column descriptions stay compact without squeezing the review table."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["top_nav"].value = "Review"

    manifest = controls["manifest_preview"].value
    assert "table-layout:fixed" in manifest
    assert "text-overflow:ellipsis" in manifest
    assert "Click to expand" in manifest


def test_sensitive_data_output_classification_is_labeled(widget_runtime):
    """Sensitive Data keeps the output classification control visibly labelled."""
    state = widget_runtime["open"]()
    assert state["_controls"]["column_classification"].description == "Output classification"


def test_review_shows_changes_since_last_save(widget_runtime):
    """Review compares the working contract with the persisted draft baseline."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["table_classification"].value = "Restricted"
    controls["top_nav"].value = "Review"

    assert "Changes since last save" in controls["manifest_preview"].value or state["dirty"]
    assert "Restricted" in json.dumps(state["manifest"])
    assert widget_runtime["calls"]["draft"] == []


def test_stale_persisted_dropdown_values_do_not_block_widget_open(widget_runtime):
    """Stale metadata must not trigger ipywidgets 'Invalid selection: value not found'."""
    widget_runtime["catalogue"][0]["load_strategy"] = "append"
    widget_runtime["catalogue"][0]["load_strategy_parameters_json"] = {
        "watermark_column": "removed_watermark",
    }
    state = widget_runtime["open"]()

    controls = state["_controls"]
    assert "partition_column" not in controls
    assert controls["watermark_column"].value == ""


def test_stale_classification_value_falls_back_to_valid_dropdown_option():
    """A retired classification label is normalized before ipywidgets sees it."""
    options = ("", "Public", "Restricted", "Confidential", "Highly Sensitive")

    assert module._valid_dropdown_value(
        options, "Retired Classification", fallback=""
    ) == ""
    assert module._valid_dropdown_value(options, "Restricted", fallback="") == "Restricted"


def test_stale_column_dropdown_metadata_does_not_block_widget_open(widget_runtime):
    """Column hydration normalizes stale dropdown-backed metadata before assignment."""
    classification = next(
        row for row in widget_runtime["enrichment"]
        if row["enrichment_level"] == "column"
        and row["enrichment_type"] == "Classification"
        and row["column_id"] == "col-0"
    )
    classification["value"] = "Retired Classification"
    sensitive = next(
        row for row in widget_runtime["guardrails"]
        if row["guardrail_type"] == "sensitive_data"
    )
    sensitive["rule_parameters_json"] = json.dumps({
        "scope": "column",
        "pii_type": "legacy_pii",
        "treatment": "legacy_treatment",
    })

    state = widget_runtime["open"]()
    controls = state["_controls"]

    assert controls["column_classification"].value == ""
    assert controls["pii_type"].value == "none"
    assert controls["sensitive_treatment"].value == "tokenize"


def test_freshness_timestamp_dropdown_uses_consistent_label_value_options(widget_runtime):
    """Timestamp dropdown options stay valid when temporal columns are present."""
    widget_runtime["catalogue"].append({
        "table_id": widget_runtime["catalogue"][0]["table_id"],
        "workspace_id": widget_runtime["catalogue"][0]["workspace_id"],
        "metadata_level": "column",
        "column_id": "col-date",
        "column_name": "snapshot_date",
        "data_type": "date",
        "is_active": True,
    })
    _capture_fixture_columns(widget_runtime)
    state = widget_runtime["open"]()
    freshness = state["_controls"]["table_guardrails"]["freshness"]["parameters"][1]

    assert ("Select timestamp column", "") in freshness.options
    assert ("snapshot_date", "snapshot_date") in freshness.options
    option_values = [
        option[1] if isinstance(option, tuple) else option
        for option in freshness.options
    ]
    assert freshness.value in option_values


def test_selection_diagnostic_names_control_table_column_and_valid_options():
    """Rejected selection values retain enough context to debug Fabric widget failures."""
    class Control:
        options = (("Public", "Public"), ("Restricted", "Restricted"))

        @property
        def value(self):
            return None

        @value.setter
        def value(self, value):
            if value not in {"Public", "Restricted"}:
                raise ValueError("Invalid selection: value not found")

    with pytest.raises(
        ValueError,
        match=(
            "control='column_classification'.*value='Legacy'.*"
            "table='curated_orders'.*column='customer_id'.*"
            "valid_options=\\['Public', 'Restricted'\\]"
        ),
    ):
        module._set_selection_value(
            Control(),
            "Legacy",
            control_name="column_classification",
            table_name="curated_orders",
            column_name="customer_id",
        )


def test_widget_exception_diagnostic_includes_phase_type_and_source_location():
    """Render failures expose the widget source location instead of only the trait error."""

    def fail():
        raise ValueError("Invalid selection: value not found")

    try:
        fail()
    except ValueError as exc:
        message = module._format_widget_exception(exc, phase="editor render")

    assert "Data Contract widget failed during editor render" in message
    assert "ValueError: Invalid selection: value not found" in message
    assert "Location:" in message
    assert "fail() line" in message

def _sidebar_text(widget):
    titles = getattr(widget, "titles", {})
    return str(getattr(widget, "value", "") or "") + str(getattr(widget, "description", "") or "") + " ".join(titles.values()) + " ".join(_sidebar_text(child) for child in getattr(widget, "children", ()))


def test_sidebar_paths_shared_rules_details_and_editor_navigation(widget_runtime):
    """Both paths show one underlying configuration and navigate to the existing editors."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["table_grain"].value = "One row per combination"
    controls["row_key_columns"].value = ("column_0", "column_1")
    controls["grain_enabled"].value = True
    read = _sidebar_text(controls["sidebar_groups"]["read"])
    write = _sidebar_text(controls["sidebar_groups"]["write"])
    assert "When this table is read" in read and "orchestrate_read()" in read
    assert "Before this table is written" in write and "orchestrate_write()" in write
    assert "Freshness" in read and "Freshness" not in write
    assert "Source Drift" not in read and "Source Drift" in write
    assert "Sensitive Data · 1 treatment" not in read and "Sensitive Data · 1 treatment" in write
    assert "orders → consuming target" in write
    for content in (read, write):
        assert "Grain · column_0 + column_1 · Block" in content
        assert "One row per combination" in content
        assert "Schema · 1 required column" in content
        assert "column_0: long" in content and "column_1: timestamp" in content
        assert "extra columns" in content
        assert "Data Quality · 3 rules across 2 columns" in content
        assert "Accepted failure rate %" in content
        assert "Operator" in content
    assert "treatment must succeed" in write
    assert "Passed" not in write and "Skipped" not in write
    sidebar = _sidebar_text(controls["guardrail_sidebar"])
    assert "Guardrail Coverage" not in sidebar
    assert "State:</b> Enabled" in sidebar and "Profile" not in sidebar
    controls["grain_policy"].value = "Warn"
    for group in controls["sidebar_groups"].values():
        assert "Grain · column_0 + column_1 · Warn" in _sidebar_text(group)
    assert len([r for r in state["current"]["guardrails"] if r.get("guardrail_type") == "grain"]) == 1
    controls["sidebar_rule_buttons"]["grain"][0].click()
    assert controls["top_nav"].value == "Table"
    assert controls["right_pane"].children[0].children[1].children[0] is controls["grain_enabled"]
    controls["sidebar_rule_buttons"]["schema"][0].click()
    assert controls["top_nav"].value == "Column"
    assert controls["column_select"].value == "col-0"
    table_rule = next(button for button in controls["sidebar_rule_buttons"]["data_quality"] if "column relationship" in button.description)
    table_rule.click()
    assert controls["top_nav"].value == "Business Rules"
    assert controls["business_saved"].value == "advanced"
    assert widget_runtime["calls"]["draft"] == []


def test_sidebar_unsaved_parameters_types_counts_and_reopen(widget_runtime):
    """Live staging updates details and counts without waiting for Save."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["column_select"].value = "col-0"
    completeness = controls["dq_family_controls"]["completeness"]
    completeness["parameters"][0].value = "17"
    completeness["block"].value = True
    content = _sidebar_text(controls["sidebar_groups"]["write"])
    assert "Accepted failure rate %:</b> 17.0" in content
    assert "Policy:</b> Block" in content
    controls["required"].value = False
    assert "Schema · 0 required columns" in _sidebar_text(controls["sidebar_groups"]["read"])
    controls["grain_enabled"].value = True
    controls["save_data_contract"].click()
    assert "Grain" in state["_validation_errors"]["table.row_key"]
    assert widget_runtime["calls"]["draft"] == []
    controls["row_key_columns"].value = ("column_0",)
    controls["save_data_contract"].click()
    reopened = widget_runtime["open"]()["_controls"]
    assert "Accepted failure rate %:</b> 17.0" in _sidebar_text(reopened["sidebar_groups"]["write"])
    assert "Grain · column_0 · Block" in _sidebar_text(reopened["sidebar_groups"]["read"])


def test_sidebar_state_is_replaced_when_another_table_is_opened(widget_runtime, monkeypatch):
    """Switch tables in one widget without carrying rules or navigation callbacks."""
    other_catalogue = [{**row, "table_id": "inventory", "table_name": "inventory"} for row in widget_runtime["catalogue"]]
    payload = json.loads(widget_runtime["contract"]["contract_payload_json"])
    payload["table"]["table_id"] = "inventory"
    other_contract = {**widget_runtime["contract"], "contract_id": "contract-inventory", "table_id": "inventory", "contract_payload_json": json.dumps(payload)}
    original_review = module.contracts.get_contract_review_state
    def review(**kwargs):
        if kwargs["contract_id"] != "contract-inventory":
            return original_review(**kwargs)
        return {"contract": other_contract, "contract_id": "contract-inventory", "contract_version": 1,
                "table_id": "inventory", "workspace_id": "dev", "catalogue_rows": other_catalogue,
                "available_columns": other_catalogue[1:], "enrichment": [], "guardrails": []}
    monkeypatch.setattr(module.contracts, "get_contract_review_state", review)
    monkeypatch.setattr(module.contracts, "list_contract_governance_state", lambda **_kw: {
        "tables": [widget_runtime["catalogue"][0], other_catalogue[0]],
        "contracts": [widget_runtime["contract"], other_contract],
    })
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["table_grain"].value = "Old grain"
    controls["row_key_columns"].value = ("column_0",)
    controls["grain_enabled"].value = True
    first_sidebar = controls["guardrail_sidebar"]
    controls["change_table"].click()
    controls["confirm_exit_discard"].click()
    controls["table"].value = "inventory"
    controls["open"].click()
    controls = state["_controls"]
    assert state["table_id"] == "inventory", state["message"]
    assert controls["grain_enabled"].value is False
    assert controls["row_key_columns"].value == ()
    assert "Grain ·" not in _sidebar_text(controls["guardrail_sidebar"])
    assert "Old grain" not in _sidebar_text(controls["guardrail_sidebar"])
    assert first_sidebar is not controls["guardrail_sidebar"]
    controls["row_key_columns"].value = ("column_1",)
    controls["grain_enabled"].value = True
    assert "Grain · column_1 · Block" in _sidebar_text(controls["guardrail_sidebar"])
    controls["sidebar_rule_buttons"]["grain"][0].click()
    assert controls["right_pane"].children[0].children[1].children[0] is controls["grain_enabled"]
    assert "inventory" in controls["left_pane"].children[0].value


def test_sidebar_expand_controls_preserve_state_during_live_updates(widget_runtime):
    """Native toggle controls expose named expansion state and retain it across edits."""
    controls = widget_runtime["open"]()["_controls"]
    read = controls["sidebar_groups"]["read"]
    header, body = read.children
    assert header.description == "When this table is read" and header.value is True
    header.value = False
    assert body.layout.display == "none"
    assert header.description == "When this table is read"
    controls["table_classification"].value = "Restricted"
    read = controls["sidebar_groups"]["read"]
    assert read.children[0].value is False
    assert read.children[0].tooltip == "Expand When this table is read"
    read.children[0].value = True
    schema = next(section for section in read.children[1].children[1:] if section.children[0].description.startswith("Schema"))
    schema.children[0].value = True
    assert schema.children[1].layout.display == ""
    assert schema.children[0].tooltip.startswith("Collapse Schema")


def test_sidebar_has_no_duplicate_configuration_buttons(widget_runtime):
    """Configured guardrails retain navigation without the redundant configuration menu."""
    controls = widget_runtime["open"]()["_controls"]
    assert "configure_guardrails" not in controls
    assert "configure_options" not in controls
    assert "configure_guardrail_buttons" not in controls
    assert len(controls["guardrail_sidebar"].children) == 2


def test_sidebar_static_freshness_describes_expectation_without_claiming_execution(widget_runtime):
    """Static Freshness remains configured but does not imply timestamp-age evaluation."""
    controls = widget_runtime["open"]()["_controls"]
    controls["table_guardrails"]["freshness"]["parameters"][0].value = "static"
    read = _sidebar_text(controls["sidebar_groups"]["read"])
    assert "No refresh expected" in read
    assert "no age validation" in read
    assert "latest timestamp relative to run time" not in read
    assert "Passed" not in read and "Skipped" not in read


@pytest.mark.parametrize("finish", ["select_key", "disable_grain"])
def test_correcting_incomplete_grain_clears_only_its_own_errors(widget_runtime, finish):
    """An unfinished Grain key must not attach errors to unrelated valid edits."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["grain_enabled"].value = True
    controls["table_grain"].value = "One row per order"
    controls["table_description"].value = "New description while choosing a key"
    controls["required"].value = False
    assert set(state["_validation_errors"]) == {"table.row_key"}
    assert widget_runtime["calls"]["draft"] == []
    if finish == "select_key":
        controls["row_key_columns"].value = ("column_0",)
    else:
        controls["grain_enabled"].value = False
    assert state["_validation_errors"] == {}
    controls["save_data_contract"].click()
    assert len(widget_runtime["calls"]["draft"]) == 1


def test_sidebar_releases_replaced_models_and_preserves_configuration_controls(widget_runtime):
    """Live edits keep the number of open sidebar widgets and layouts bounded."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["row_key_columns"].value = ("column_0",)
    controls["grain_enabled"].value = True
    before = len(widget_runtime["models"])
    original_groups = list(controls["sidebar_groups"].values())
    for index in range(20):
        controls["table_grain"].value = "A" * (index + 1)
        assert len(widget_runtime["models"]) == before
    assert all(group.closed and group.layout.closed for group in original_groups)
    assert not controls["sidebar_groups"]["read"].closed


def test_sidebar_skips_rebuilding_unchanged_configuration(widget_runtime):
    """Description edits unrelated to active checks do not recreate the sidebar."""
    controls = widget_runtime["open"]()["_controls"]
    group = controls["sidebar_groups"]["read"]
    controls["table_description"].value = "Only descriptive Enrichment changed"
    assert controls["sidebar_groups"]["read"] is group
    assert not group.closed



def test_removed_column_definitions_are_reviewed_and_explicitly_removed(widget_runtime):
    """Opening a draft preserves unavailable definitions until Governance removes them."""
    widget_runtime["enrichment"].append({
        "enrichment_id": "removed-description", "contract_id": "contract-orders", "contract_version": 1,
        "workspace_id": "dev", "enrichment_level": "column", "column_id": "removed-column",
        "enrichment_type": "Description", "value": "Keep this until reviewed",
    })
    widget_runtime["guardrails"].append({
        "guardrail_rule_id": "removed-sensitive", "guardrail_version": 1,
        "contract_id": "contract-orders", "contract_version": 1, "workspace_id": "dev",
        "guardrail_type": "sensitive_data", "column_id": "removed-column", "rule_type": "remove",
        "rule_parameters_json": '{"scope":"column","treatment":"remove"}', "action": "Block", "is_active": True,
    })
    state = widget_runtime["open"]()
    assert any(item.get("column_id") == "removed-column" for item in state["current"]["guardrails"])
    assert any(item.get("column_id") == "removed-column" for item in state["current"]["enrichment"])
    assert not state["dirty"]
    state["_controls"]["remove_unavailable_definitions"].click()
    assert state["dirty"]
    assert not any(item.get("column_id") == "removed-column" for item in state["current"]["enrichment"])
    state["save_data_contract"]()
    saved = json.loads(widget_runtime["contract"]["contract_payload_json"])
    assert not any(item.get("column_id") == "removed-column" for item in saved["enrichment"]["columns"])
    assert not any(item.get("column_id") == "removed-column" for item in saved["guardrails"])


def test_rejected_save_retains_pending_widget_edits(widget_runtime, monkeypatch):
    """A stale Save never clears edits or reports that the draft was saved."""
    state = widget_runtime["open"]()
    state["_controls"]["table_description"].value = "Unsaved description"
    def reject(**kwargs):
        raise RuntimeError("Data Contract changed in another session. Your pending edits are retained.")
    monkeypatch.setattr(module.contracts, "save_contract_draft", reject)
    with pytest.raises(RuntimeError, match="pending edits are retained"):
        state["save_data_contract"]()
    assert state["dirty"]
    assert state["_pending_enrichment"]
    assert any(item.get("value") == "Unsaved description" for item in state["current"]["enrichment"])


@pytest.mark.parametrize("old_limit,expected", [(100, "0"), (95, "")])
def test_legacy_uniqueness_hydration_requires_explicit_tolerance(widget_runtime, old_limit, expected):
    """Never silently reinterpret a saved distinct-key tolerance."""
    widget_runtime["guardrails"].append({
        "guardrail_rule_id": "legacy-unique", "guardrail_version": 1,
        "guardrail_type": "data_quality", "column_id": "col-0", "rule_type": "uniqueness",
        "rule_parameters_json": json.dumps({"columns": ["column_0"], "minimum_unique_percent": old_limit}),
        "action": "Warn", "is_active": True,
    })
    state = widget_runtime["open"]()
    controls = state["_controls"]
    assert controls["dq_uniqueness_failure"].value == expected
    if not expected:
        controls["dq_family_controls"]["uniqueness"]["block"].value = True
        controls["save_data_contract"].click()
        assert not widget_runtime["calls"]["draft"]
        assert "legacy distinct-key" in str(state["_validation_errors"])
        controls["dq_uniqueness_failure"].value = "5"
        controls["save_data_contract"].click()
        saved = next(rule for rule in widget_runtime["calls"]["guardrails"][-1] if rule.get("guardrail_rule_id") == "legacy-unique")
        assert module._parameters(saved) == {"columns": ["column_0"], "maximum_failure_percent": 5.0}


def test_saved_business_uniqueness_uses_same_failure_rate_editor(widget_runtime):
    """Table rules and column rules hydrate the same accepted failure percentage."""
    widget_runtime["guardrails"].append({
        "guardrail_rule_id": "table-unique", "guardrail_version": 1,
        "guardrail_type": "data_quality", "column_id": None, "rule_type": "uniqueness",
        "rule_parameters_json": json.dumps({"columns": ["column_0", "column_1"], "maximum_failure_percent": 4}),
        "action": "Block", "is_active": True,
    })
    controls = widget_runtime["open"]()["_controls"]
    controls["business_saved"].value = "table-unique"
    assert controls["business_tolerance"].description == "Accepted failure rate %"
    assert float(controls["business_tolerance"].value) == 4
    assert controls["business_block"].value is True
    controls["business_tolerance"].value = "3"
    controls["apply_business_rule"].click()
    controls["save_data_contract"].click()
    reopened = widget_runtime["open"]()["_controls"]
    reopened["business_saved"].value = "table-unique"
    assert float(reopened["business_tolerance"].value) == 3


def test_sensitive_ui_defaults_to_full_mask_and_hides_technical_settings(widget_runtime):
    """The simplest protection exposes no character-count or mask-symbol settings."""
    _use_text_identifier(widget_runtime)
    state = widget_runtime['open']()
    controls = state['_controls']
    controls['column_select'].value = 'col-0'
    controls['pii_type'].value = 'direct'
    controls['pii_reason'].value = 'Identifies the customer'
    controls['sensitive_enabled'].value = True
    assert controls['sensitive_treatment'].value == 'mask'
    assert controls['mask_mode'].value == 'full'
    assert controls['mask_start'].layout.display == 'none'
    assert controls['mask_character'].layout.display == 'none'
    controls['mask_mode'].value = 'partial'
    assert controls['mask_start'].layout.display == ''
    controls['mask_start'].value = '1'
    controls['mask_mode'].value = 'full'
    assert controls['mask_start'].value == '0'
    assert not state['_validation_errors']


def test_sensitive_fixed_width_policy_survives_save_and_reopen(widget_runtime):
    """Persist fixed intervals rather than recomputing groups from observed rows."""
    state = widget_runtime['open']()
    controls = state['_controls']
    controls['column_select'].value = 'col-0'
    controls['pii_type'].value = 'indirect'
    controls['pii_reason'].value = 'Reduce precision'
    controls['sensitive_enabled'].value = True
    controls['sensitive_treatment'].value = 'bucket'
    controls['bucket_mode'].value = 'width'
    controls['bucket_width'].value = '10'
    controls['bucket_origin'].value = '5'
    assert controls['bucket_width'].layout.display == ''
    assert controls['bucket_bins'].layout.display == 'none'
    assert not state['_validation_errors']
    controls['save_data_contract'].click()
    assert widget_runtime['calls']['guardrails']
    reopened = widget_runtime['open']()['_controls']
    reopened['column_select'].value = 'col-0'
    assert reopened['bucket_mode'].value == 'width'
    assert reopened['bucket_width'].value == '10.0'
    assert reopened['bucket_origin'].value == '5.0'


def test_text_columns_do_not_offer_numeric_buckets(widget_runtime):
    """Category mappings belong in the transformation workflow."""
    state = widget_runtime['open']()
    controls = state['_controls']
    controls['column_select'].value = 'col-1'  # timestamp, also non-numeric
    assert 'bucket' not in [value for _label, value in controls['sensitive_treatment'].options]


def test_saved_numeric_bucket_restores_after_viewing_text_column(widget_runtime):
    """Filtering available treatments cannot make a saved numeric rule unopenable."""
    state = widget_runtime['open']()
    controls = state['_controls']
    controls['column_select'].value = 'col-0'
    controls['pii_type'].value = 'indirect'
    controls['pii_reason'].value = 'Reduce precision'
    controls['sensitive_enabled'].value = True
    controls['sensitive_treatment'].value = 'bucket'
    controls['bucket_mode'].value = 'width'
    controls['save_data_contract'].click()
    reopened = widget_runtime['open']()
    controls = reopened['_controls']
    controls['column_select'].value = 'col-1'
    controls['column_select'].value = 'col-0'
    assert controls['sensitive_treatment'].value == 'bucket'
    assert controls['bucket_mode'].value == 'width'
    assert not reopened['_validation_errors']


def test_sensitive_ai_receives_approved_profile_and_frequency_samples(widget_runtime, monkeypatch):
    """The authoring widget passes min/max and frequent values into AI context."""
    _state, captures = _open_with_ai(widget_runtime, monkeypatch)
    column = captures['sensitive'][0]['columns'][0]
    assert column['profile_evidence']['min_value'] == '1'
    assert column['profile_evidence']['max_value'] == '9'
    assert column['profile_evidence']['mean_value'] == 5.0
    assert column['frequency_evidence'] == [{'value': 'col-0', 'count': 2, 'percent': 20.0}]


def test_numeric_columns_offer_bucket_tokenize_remove_without_mask(widget_runtime):
    """Numeric identifiers can be tokenized; numerical measures can be bucketed."""
    controls = widget_runtime['open']()['_controls']
    assert {value for _label, value in controls['sensitive_treatment'].options} == {'bucket', 'tokenize', 'remove'}


def test_categorical_columns_offer_mask_tokenize_remove_without_bucket(widget_runtime):
    """Physical text columns expose no numeric interval configuration."""
    _use_text_identifier(widget_runtime)
    controls = widget_runtime['open']()['_controls']
    assert {value for _label, value in controls['sensitive_treatment'].options} == {'mask', 'tokenize', 'remove'}


def test_invalid_ai_acceptance_leaves_all_authored_fields_unchanged(widget_runtime, monkeypatch):
    """Even malformed advice bypassing the decoder cannot partially mutate the form."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state['_controls']
    controls['column_select'].value = 'col-1'
    def bucket(context, **kwargs):
        column = context['columns'][0]
        return [{'column_name': column['column_name'], 'column_id': column['column_id'],
            'pii_type': 'indirect', 'pii_label': 'Indirect PII', 'reason': 'Coarse detail',
            'treatment': 'bucket', 'action': 'Block', 'parameters': {'bins': [0, 10], 'labels': ['low', 'high']}, 'is_active': True}]
    monkeypatch.setattr(module, 'suggest_sensitive_data', bucket)
    controls['rerun_sensitive'].click()
    fields = ['pii_type', 'pii_reason', 'sensitive_enabled', 'sensitive_treatment', 'column_classification', 'required']
    before = {name: controls[name].value for name in fields}
    controls['accept_sensitive'].click()
    assert {name: controls[name].value for name in fields} == before
    assert 'does not apply' in state['message']


def test_saved_incompatible_treatment_requires_explicit_repair(widget_runtime):
    """Opening a numeric mask does not silently replace the saved governance decision."""
    rule = next(row for row in widget_runtime['guardrails'] if row.get('guardrail_type') == 'sensitive_data')
    rule.update({'rule_type': 'mask', 'rule_parameters_json': json.dumps({
        'scope': 'column', 'treatment': 'mask', 'preserve_start': 0, 'preserve_end': 0, 'mask_character': '*',
    })})
    state = widget_runtime['open']()
    controls = state['_controls']
    assert controls['sensitive_treatment'].value is None
    assert state['_validation_errors']
    controls['save_data_contract'].click()
    assert not widget_runtime['calls']['guardrails']
    controls['sensitive_treatment'].value = 'tokenize'
    controls['pii_reason'].value = 'Numeric customer identifier'
    controls['save_data_contract'].click()
    assert widget_runtime['calls']['guardrails']


def test_business_review_switches_sources_without_persisting_or_losing_candidates(widget_runtime, monkeypatch):
    """Generated proposals and draft rules share one reviewer while settings stay staged."""
    state, _ = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    monkeypatch.setattr(module, "suggest_business_rule", lambda *a, **kw: [{
        "rule_type": "range", "columns": ["column_0"],
        "parameters": {"minimum": 1, "maximum_failure_percent": 0},
        "business_requirement": "Identifiers must be positive.", "executable": True,
    }])
    controls["business_requirement"].value = "Identifiers must be positive."
    controls["resolve_business_rule"].click()
    choices = controls["business_proposal_select"].options
    controls["business_block"].value = True
    controls["business_review_source"].value = "Current draft rules"
    assert controls["business_proposal_select"].layout.display == "none"
    assert controls["business_saved"].layout.display == ""
    controls["business_review_source"].value = "Generated proposals"
    assert controls["business_proposal_select"].options == choices
    assert controls["business_block"].value is True
    assert controls["business_saved"].layout.display == "none"
    controls["apply_business_rule"].click()
    assert controls["business_review_source"].value == "Current draft rules"
    assert controls["apply_business_rule"].description == "Update DQ Rule"
    assert widget_runtime["calls"]["draft"] == []


def test_business_generation_busy_state_and_failure_restore_the_reviewer(widget_runtime, monkeypatch):
    """A failed generation leaves no stale actionable result and restores the Generate CTA."""
    state, _ = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    def fail(*args, **kwargs):
        assert controls["resolve_business_rule"].disabled
        assert controls["resolve_business_rule"].description == "Generating DQ Rules…"
        assert controls["apply_business_rule"].disabled
        assert controls["business_rule_controls"].layout.display == "none"
        raise ValueError("Example generation failure")

    monkeypatch.setattr(module, "suggest_business_rule", fail)
    controls["resolve_business_rule"].click()
    assert controls["resolve_business_rule"].description == "Generate DQ Rules"
    assert not controls["resolve_business_rule"].disabled
    assert controls["apply_business_rule"].disabled
    assert "Example generation failure" in controls["business_proposal"].value
    assert widget_runtime["calls"]["draft"] == []


def test_profiling_edits_use_normal_draft_save_and_preserve_guardrails(widget_runtime):
    """Table policy edits remain draft state until the normal contract Save action."""
    state = widget_runtime['open']()
    before = json.loads(json.dumps(state['manifest']))
    controls = state['_profiling_editor'].profiling_controls
    controls['standard']['days'].value = 7
    controls['grain']['frequency'].value = 'every'
    controls['grain']['trigger'].value = 'write'
    assert state['dirty'] is True
    assert widget_runtime['calls']['draft'] == []
    state['save_data_contract'](return_to_selector_after=False)
    saved = widget_runtime['calls']['draft'][-1]
    assert saved['profiling']['standard']['days'] == 7
    assert saved['profiling']['grain'] == {'frequency': 'every', 'trigger': 'write'}
    assert saved['guardrails'] == before['guardrails']
    reopened = widget_runtime['open']()
    assert reopened['_profiling_editor'].profiling_controls['standard']['days'].value == 7


def test_frozen_profiling_controls_cannot_edit_policy(widget_runtime):
    """An immutable version exposes disabled policy controls and no separate Save."""
    widget_runtime['contract']['status'] = 'frozen'
    state = widget_runtime['open']()
    section = state['_profiling_editor']
    assert all(control.disabled for values in section.profiling_controls.values() for control in values.values())
    assert not hasattr(section, 'profiling_save')


@pytest.mark.parametrize('uniqueness', [None, 0.0, 100.0])
def test_native_candidate_metrics_do_not_invent_missing_or_zero_values(widget_runtime, uniqueness):
    """Migrated list-only candidates can have unknown metrics; zero remains zero."""
    widget_runtime['catalogue'][0]['profile_key_candidates_json'] = {
        'status': None, 'max_combination_width': None,
        'candidates': [{'columns': ['column_0'], 'column_count': None, 'row_count': None,
                        'distinct_count': None, 'uniqueness_percent': uniqueness, 'null_count': None}],
    }
    state = widget_runtime['open']()
    evidence = state['_controls']['grain_profile_evidence'].value
    assert ('Uniqueness not recorded' if uniqueness is None else f'{uniqueness}% unique') in evidence
    assert 'Missing-key count not recorded' in evidence
    assert 'no missing key values' not in evidence
    assert tuple(state['_controls']['row_key_columns'].value) == ('column_0',)


def test_native_schedule_unknown_fields_remain_unknown_in_both_views(widget_runtime):
    """Missing historical flags/timezone must not become disabled or UTC."""
    captured = {'status': 'configured', 'schedules': [
        {'enabled': None, 'frequency': 'daily', 'times': [], 'timezone': None},
    ]}
    widget_runtime['catalogue'][0]['scheduled_refresh_json'] = captured
    state = widget_runtime['open']()
    for rendered in (state['_controls']['left_pane'].children[0].value,
                     module._scheduled_refresh_html(captured)):
        assert 'Enabled state unknown' in rendered
        assert 'Timezone not provided' in rendered
        assert 'Disabled' not in rendered and 'UTC' not in rendered
    assert state['scheduled_refresh'] == captured


@pytest.mark.parametrize(('null_count', 'expected'), [(0, 'no missing key values'), (2, '2 missing key values')])
def test_native_candidate_missing_key_counts_are_displayed_exactly(widget_runtime, null_count, expected):
    """The native metric, rather than a presumed proven-key outcome, owns the label."""
    widget_runtime['catalogue'][0]['profile_key_candidates_json'] = {
        'status': None, 'max_combination_width': None,
        'candidates': [{'columns': ['column_0'], 'uniqueness_percent': 100.0, 'null_count': null_count}],
    }
    state = widget_runtime['open']()
    assert expected in state['_controls']['grain_profile_evidence'].value
