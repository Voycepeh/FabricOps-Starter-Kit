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
        "layer": "Silver", "load_strategy": "append",
        "load_strategy_parameters_json": "{}", "is_active": True,
        "_workspace_id": "workspace-id", "_notebook_id": "writer-notebook-id",
    }]
    for index in range(count):
        rows.append({
            "table_id": "orders", "environment_name": "dev", "metadata_level": "column",
            "column_id": f"col-{index}", "column_name": f"column_{index}",
            "data_type": (
                "long" if index == 0 else "timestamp" if index == 1 else "string"
            ), "is_active": True,
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
    contract_payload = {
        "contract": {
            "contract_id": "contract-orders", "contract_version": 1, "status": "draft",
        },
        "table": {
            **catalogue[0],
            "processing": {"load_strategy": "append"},
            "processing_source": "catalogue",
            "columns": [dict(row) for row in catalogue[1:]],
        },
        "enrichment": {"table": [], "columns": []},
        "guardrails": [],
    }
    contract = {
        "contract_id": "contract-orders", "contract_version": 1, "table_id": "orders",
        "environment_name": "dev",
        "contract_payload_json": json.dumps(contract_payload, sort_keys=True, separators=(",", ":")),
        "status": "draft", "is_active": False,
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
        {"guardrail_rule_id": "drift", "guardrail_version": 1, "guardrail_type": "source_drift", "rule_type": "source_drift", "rule_parameters_json": '{"partition_column":"column_0","change_column":"column_1"}', "action": "Warn", "is_active": True},
        {"guardrail_rule_id": "sensitive", "guardrail_version": 1, "guardrail_type": "sensitive_data", "column_id": "col-0", "rule_type": "mask", "rule_parameters_json": '{"scope":"column","treatment":"mask","preserve_start":0,"preserve_end":0,"mask_character":"*"}', "action": "Block", "is_active": True},
        {"guardrail_rule_id": "dq", "guardrail_version": 1, "guardrail_type": "data_quality", "column_id": "col-0", "rule_type": "completeness", "rule_parameters_json": '{"columns":["column_0"],"maximum_missing_percent":0,"treat_blank_as_missing":false}', "action": "Block", "is_active": True},
        {"guardrail_rule_id": "dq-pattern", "guardrail_version": 1, "guardrail_type": "data_quality", "column_id": "col-0", "rule_type": "pattern", "rule_parameters_json": '{"columns":["column_0"],"pattern":"^ORD-[0-9]+$"}', "action": "Warn", "is_active": True},
        {"guardrail_rule_id": "advanced", "guardrail_version": 1, "guardrail_type": "data_quality", "column_id": "", "rule_type": "column_relationship", "rule_parameters_json": '{"columns":["column_1","column_0"],"operator":">"}', "action": "Warn", "is_active": True},
    ]
    for row in guardrails:
        row.update({
            "contract_id": "contract-orders",
            "contract_version": 1,
            "environment_name": "dev",
        })
    calls = {"draft": [], "enrichment": [], "guardrails": [], "freeze": 0, "activate": 0, "profiles": []}
    schedule = {
        "status": "unavailable", "schedules": [],
        "message": "Scheduled Refresh discovery is unavailable for this notebook.",
    }
    ai_enrichment = {
        "enabled": False,
        "table_description_prompt": "configured table description prompt",
        "column_description_prompt": "configured column description prompt",
        "sensitive_data_prompt": "configured sensitive prompt",
        "grain_prompt": "configured grain prompt",
        "pattern_prompt": "configured pattern prompt",
        "business_rule_prompt": "configured business rule prompt",
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

    def activate_contract_version(**_kwargs):
        calls["activate"] += 1
        contract["is_active"] = True
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
    monkeypatch.setattr(module.contracts, "save_enrichment", save_enrichment)
    monkeypatch.setattr(module.contracts, "save_guardrails", save_guardrails)
    monkeypatch.setattr(module.contracts, "save_contract_draft", save_contract_draft)
    monkeypatch.setattr(module.contracts, "freeze_contract", freeze_contract)
    monkeypatch.setattr(module.contracts, "activate_contract_version", activate_contract_version)
    monkeypatch.setattr(module.contracts, "get_table_runtime_context", lambda **_kwargs: {
        "latest_profile": {
            "profile_snapshot_id": "snapshot-prod",
            "environment_name": "PROD",
            "pipeline_name": "02_pipeline",
            "committed_by": "voyce@example.com",
            "committed_at": "2026-09-26T02:45:00",
        },
        "writer_count": 1,
        "reader_count": 2,
        "lineage": [
            {
                "environment_name": "DEV", "relationship": "Writer",
                "pipeline_name": "02_pipeline", "last_seen": "2026-09-26T03:00:00",
            },
            {
                "environment_name": "PROD", "relationship": "Reader",
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
        state["_controls"]["open"].click()
        return state

    return {
        "start": start, "open": open_widget,
        "calls": calls, "contract": contract, "catalogue": catalogue,
        "guardrails": guardrails, "schedule": schedule,
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


def test_selector_is_explicit_and_pending_selection_cannot_change_active_contract(widget_runtime):
    """The editor stays inactive until Open and Change table deactivates the current contract."""
    state = widget_runtime["start"]()
    controls = state["_controls"]

    assert state["current"] is None
    assert state["table_id"] is None
    assert state["pending_table_id"] == "orders"
    assert controls["store"].value == "Silver"
    store_labels = [label for label, _value in controls["store"].options]
    assert "Silver · Lakehouse" in store_labels
    assert "Metadata · Lakehouse" not in store_labels
    assert controls["schema"].value == "sales"
    selector = controls["selector_panel"].children[0]
    assert [child.description for child in selector.children] == [
        "Fabric store", "Schema", "Table", "Contract",
    ]
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
    controls["top_nav"].value = "Manifest & Freeze"
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
    assert "No profile values available" in module._profile_html({"kind": "unavailable"})


def test_shared_layout_and_existing_state_hydrate(widget_runtime):
    """The unified page uses shared layout primitives and hydrates all main editors."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    assert "fabricops-form" in controls["page"]._dom_classes
    assert tuple(controls["top_nav"].options) == ("Table", "Columns", "Business Rules", "Manifest & Freeze")
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
    assert len(controls["table_guardrails"]["source_drift"]["parameters"]) == 2
    assert controls["load_strategy"].value == "append"
    assert controls["load_strategy"].disabled is True
    assert controls["sensitive_enabled"].value is True
    assert controls["dq_type"].value == "completeness"
    assert controls["business_saved"].value == ""
    assert controls["row_key_columns"].value == ()
    assert controls["business_enabled"].description == "Enabled"
    assert controls["business_block"].description == "Block on failure"
    assert "Schedule discovery unavailable" in controls["pipeline_refresh"].value
    assert "read-only" in controls["pipeline_refresh"].value


def test_existing_table_uniqueness_hydrates_row_key(widget_runtime):
    """Hydrate an existing table-level uniqueness rule into Grain & Row Key."""
    widget_runtime["guardrails"].append({
        "guardrail_rule_id": "row-key",
        "guardrail_version": 1,
        "guardrail_type": "data_quality",
        "column_id": "",
        "rule_type": "uniqueness",
        "rule_parameters_json": '{"columns":["column_0","column_1"]}',
        "action": "Block",
        "is_active": True,
        "contract_id": "contract-orders",
        "contract_version": 1,
        "environment_name": "dev",
    })

    state = widget_runtime["open"]()
    controls = state["_controls"]

    assert tuple(controls["row_key_columns"].value) == ("column_0", "column_1")
    assert controls["row_key_block"].value is True


def test_v38_top_navigation_switches_one_two_pane_workspace(widget_runtime):
    """Use the prototype contract: top nav plus one 27/73 left/right workspace."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    for label in ("Table", "Columns", "Business Rules", "Manifest & Freeze"):
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
    assert "1 writer · 2 readers" in table_summary
    assert "View lineage" in table_summary
    assert "04_reporting" in table_summary
    assert "Loading Strategy" in table_summary
    assert "Refresh Frequency" in table_summary
    assert "Classification" in table_summary
    assert "Guardrails" in table_summary
    assert "table_save" not in controls
    table_sections = controls["right_pane"].children
    assert [section.children[0].value for section in table_sections[:5]] == [
        "<div style=\"color:#253858;font-size:14px;font-weight:700;line-height:1.25;\">Table definition</div>",
        "<div style=\"color:#253858;font-size:14px;font-weight:700;line-height:1.25;\">Grain &amp; Row Key</div>",
        "<div style=\"color:#253858;font-size:14px;font-weight:700;line-height:1.25;\">Processing</div>",
        "<div style=\"color:#253858;font-size:14px;font-weight:700;line-height:1.25;\">Freshness</div>",
        "<div style=\"color:#253858;font-size:14px;font-weight:700;line-height:1.25;\">Source Drift</div>",
    ]

    controls["top_nav"].value = "Columns"
    assert controls["column_search"] in controls["left_pane"].children
    assert controls["dq_panel"].children[1].layout.grid_template_columns == (
        "minmax(0, 68fr) minmax(240px, 32fr)"
    )
    assert [label for label, _value in controls["dq_type"].options] == [
        "Completeness", "Allowed Values", "Value Rules", "Pattern",
    ]
    assert "save_column" not in controls
    assert "save_dq" not in controls

    controls["top_nav"].value = "Business Rules"
    assert controls["business_saved"] in controls["left_pane"].children
    assert controls["business_requirement"].layout.max_width == "760px"
    assert controls["business_columns"].layout.height == "130px"
    assert controls["business_enabled"].description == "Enabled"
    assert controls["business_block"].description == "Block on failure"
    controls["top_nav"].value = "Manifest & Freeze"
    assert controls["left_pane"].children[0] is table_context
    assert "Table guardrails" in controls["manifest_preview"].value
    assert "Column definitions and rules" in controls["manifest_preview"].value
    assert "Business Rules" in controls["manifest_preview"].value


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
    assert controls["dq_block"].value is True

    controls["column_select"].value = "col-1"

    assert controls["dq_type"].value == "completeness"
    assert controls["dq_max_missing"].value == "0"
    assert controls["dq_block"].value is False


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
    """Final Data Contract save persists staged state and completes the authoring cycle."""
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
    """Discard clears staged session changes and reloads canonical state without persistence."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["table_description"].value = "Unsaved table change"
    assert state["dirty"] is True
    assert widget_runtime["calls"]["enrichment"] == []

    controls["discard_data_contract"].click()

    assert state["dirty"] is False
    assert widget_runtime["calls"]["enrichment"] == []
    assert widget_runtime["calls"]["guardrails"] == []
    assert state["_controls"]["table_description"].value == "Orders table"
    assert "discarded" in state["message"]


def test_guardrail_edits_stage_then_final_save_persists(widget_runtime):
    """Guardrail editors stage normalized records and persist them only at final save."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    controls["table_guardrails"]["freshness"]["block"].value = False

    controls["sensitive_enabled"].value = True
    controls["sensitive_treatment"].value = "tokenize"
    controls["pii_reason"].value = "The identifier directly associates an order with a person."

    controls["dq_type"].value = "completeness"
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
    assert len(captures["enrichment"]) == 2  # selected table plus currently opened column
    assert captures["enrichment"][0]["table_columns"] == [
        {"column_name": "column_0", "data_type": "long"},
        {"column_name": "column_1", "data_type": "timestamp"},
    ]
    assert len(captures["sensitive"]) == 1
    assert captures["sensitive"][0]["table_description"] == "Suggested table description"
    assert captures["sensitive"][0]["columns"][0]["description"] == "Suggested column description"
    assert all(not drafts for drafts in state["_column_drafts"].values())
    assert state["_ai_suggestions"]
    assert "Suggested column description" in controls["column_description_ai"].value
    assert "Direct PII" in controls["sensitive_ai"].value
    assert controls["selector_panel"].layout.display == "none"
    assert controls["editor_shell"].layout.display == ""
    for label in ("Table", "Columns", "Business Rules", "Manifest & Freeze"):
        controls["top_nav"].value = label
        assert len(controls["left_pane"].children) > 0
        assert len(controls["right_pane"].children) > 0
    assert widget_runtime["calls"]["enrichment"] == []
    assert widget_runtime["calls"]["guardrails"] == []


def test_ai_open_reports_granular_progress(widget_runtime, monkeypatch):
    """Slow AI startup reports the real stage before each blocking suggestion call."""
    widget_runtime["ai_enrichment"]["enabled"] = True
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
    assert controls["sensitive_block"].value is True
    assert controls["column_description"].value == description
    assert controls["column_classification"].value == "Confidential"
    assert controls["required"].value is False
    assert controls["dq_type"].value == "pattern"
    assert controls["dq_pattern"].value == "manual-pattern"
    assert widget_runtime["calls"]["guardrails"] == []

    assert widget_runtime["calls"]["guardrails"] == []
    controls["save_data_contract"].click()
    saved_sensitive = next(
        record for record in widget_runtime["calls"]["guardrails"][-1]
        if record.get("guardrail_type") == "sensitive_data"
    )
    saved_parameters = module._parameters(saved_sensitive)
    assert saved_parameters["pii_type"] == "direct"
    assert saved_parameters["pii_reason"] == "Can uniquely associate a person."


def test_dq_ai_is_scoped_to_pattern_and_forwards_instruction(
    widget_runtime, monkeypatch
):
    """Only Pattern exposes AI assistance and user intent augments the prompt."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    captured: dict[str, object] = {}

    def dq(_context, **kwargs):
        captured.update(kwargs)
        return [{
            "rule_type": "pattern",
            "columns": ["column_0"],
            "parameters": {"pattern": "^P[0-9]{3}$"},
            "rationale": "Matches the requested product ID shape.",
            "selected": True,
        }]

    monkeypatch.setattr(module, "suggest_dq_rules", dq)

    assert controls["dq_type"].value == "completeness"
    assert controls["suggest_dq"].disabled is True
    assert controls["dq_ai_instruction"].disabled is True

    controls["dq_type"].value = "pattern"
    assert controls["suggest_dq"].disabled is False
    assert controls["dq_ai_instruction"].disabled is False

    controls["dq_ai_instruction"].value = "Product IDs start with P followed by three digits."
    controls["suggest_dq"].click()

    assert "Product IDs start with P followed by three digits." in str(captured["prompt"])
    controls["accept_dq_suggestion"].click()
    assert controls["dq_pattern"].value == "^P[0-9]{3}$"

    controls["dq_type"].value = "value_set"
    assert controls["suggest_dq"].disabled is True
    assert controls["dq_suggestion"].options == ()


def test_dq_ai_uses_fresh_description_suggestions_before_acceptance(widget_runtime, monkeypatch):
    """Dependent DQ advice sees fresh AI Description context without auto-accepting it."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    captured: list[dict[str, object]] = []

    def dq(context, **_kwargs):
        captured.append(context)
        return []

    monkeypatch.setattr(module, "suggest_dq_rules", dq)

    assert controls["column_description"].value == "Order identifier"
    controls["dq_type"].value = "pattern"
    controls["suggest_dq"].click()

    assert captured
    assert captured[0]["table_description"] == "Suggested table description"
    assert captured[0]["columns"][0]["description"] == "Suggested column description"
    assert controls["column_description"].value == "Order identifier"


def test_manual_description_change_marks_dependent_ai_stale_and_requests_rerun(
    widget_runtime, monkeypatch
):
    """Changing Description invalidates dependent AI advice without changing manual controls."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]
    scope = next(iter(state["_ai_suggestions"]))
    column_id = str(controls["column_select"].value)

    state["_ai_suggestions"][scope]["dq"] = [{
        "rule_type": "completeness",
        "columns": ["column_0"],
        "parameters": {},
        "rationale": "old",
        "selected": True,
    }]
    controls["dq_suggestion"].options = [("old", "0")]
    controls["dq_suggestion"].disabled = False
    controls["accept_dq_suggestion"].disabled = False

    controls["column_description"].value = "Edited business description"

    suggestions = state["_ai_suggestions"][scope]["columns"][column_id]
    assert suggestions["description"]["stale"] is True
    assert suggestions["sensitive_data"]["stale"] is True
    assert "dq" not in state["_ai_suggestions"][scope]
    assert controls["dq_suggestion"].options == ()
    assert "Re-run suggestions" in controls["dq_ai"].value
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

    assert "AI Functions unavailable" in controls["column_description_ai"].value
    assert controls["accept_column_description"].disabled is True


def test_dq_failure_clears_previous_suggestions(widget_runtime, monkeypatch):
    """A failed DQ re-run must not leave old AI suggestions selectable."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    monkeypatch.setattr(
        module,
        "suggest_dq_rules",
        lambda *_args, **_kwargs: [{
            "rule_type": "pattern",
            "columns": ["column_0"],
            "parameters": {"pattern": "^ORD-[0-9]+$"},
            "rationale": "Structured identifier.",
            "selected": True,
        }],
    )
    controls["dq_type"].value = "pattern"
    controls["suggest_dq"].click()
    assert controls["dq_suggestion"].options

    monkeypatch.setattr(
        module,
        "suggest_dq_rules",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("DQ AI unavailable")),
    )
    controls["suggest_dq"].click()

    assert controls["dq_suggestion"].options == ()
    assert controls["dq_suggestion"].disabled is True
    assert controls["accept_dq_suggestion"].disabled is True
    assert "DQ AI unavailable" in controls["dq_ai"].value


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

    options = [item[1] if isinstance(item, tuple) else item for item in freshness["parameters"][0].options]
    assert options == ["", "column_1"]
    assert freshness["parameters"][0].description == "Timestamp column"

    freshness["enabled"].value = True
    freshness["parameters"][0].value = "column_1"
    freshness["parameters"][1].value = "24"
    freshness["parameters"][2].value = "hours"

    preview = freshness["display"][-1].value
    assert "The latest <code>column_1</code> must be within <b>24 hours</b> of the pipeline run." in preview
    assert "<code>MAX(column_1)</code> must be on or after 1 Jan 2026 23:00." in preview

    freshness_section = state["_controls"]["right_pane"].children[3]
    assert "Applies when this table is used as a source in a downstream pipeline." in freshness_section.children[1].value
    assert "not when this table itself is written" in freshness_section.children[1].value


def test_freshness_is_unavailable_without_temporal_columns(widget_runtime):
    """Tables without date or timestamp columns cannot author a Freshness rule."""
    widget_runtime["catalogue"][2]["data_type"] = "string"

    state = widget_runtime["open"]()
    freshness = state["_controls"]["table_guardrails"]["freshness"]

    assert freshness["enabled"].disabled is True
    assert freshness["block"].disabled is True
    assert freshness["parameters"][0].disabled is True
    assert "No date or datetime columns are available" in freshness["display"][0].value


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

    freshness["parameters"][0].value = "column_1"
    freshness["parameters"][1].value = "6"
    freshness["parameters"][2].value = "hours"
    assert widget_runtime["calls"]["guardrails"] == []
    staged = next(
        record for records in state["_pending_guardrails"].values()
        for record in records.values()
        if record.get("guardrail_type") == "freshness"
    )
    assert module._parameters(staged) == {
        "freshness_column": "column_1", "maximum_age": 6.0, "maximum_age_unit": "hours",
    }

    drift = state["_controls"]["table_guardrails"]["source_drift"]
    drift["enabled"].value = True
    assert drift["parameters"][1].description == "Change tracking column"
    drift["parameters"][0].value = "column_0"
    drift["parameters"][1].value = "column_1"
    drift_preview = drift["display"][-1].value
    assert "last successfully consumed state for that downstream target" in drift_preview
    assert "row count, <code>column_1</code> values, and a content fingerprint" in drift_preview

    drift_section = state["_controls"]["right_pane"].children[4]
    assert "Applies when this table is used as a source in a downstream pipeline." in drift_section.children[1].value
    assert "previously consumed from this table has changed" in drift_section.children[1].value

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
    controls["dq_type"].value = "completeness"
    controls["dq_max_missing"].value = "not-a-number"


    assert len(widget_runtime["calls"]["guardrails"]) == before
    assert any(
        "could not convert string to float" in message
        for message in state["_validation_errors"].values()
    )


def test_column_dq_family_change_hydrates_its_own_saved_configuration(widget_runtime):
    """Keep multiple rules on one column independently editable and update the matching record."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    assert controls["dq_type"].value == "completeness"
    assert controls["dq_max_missing"].value == "0"

    controls["dq_type"].value = "pattern"

    assert controls["dq_pattern"].value == "^ORD-[0-9]+$"
    assert controls["dq_block"].value is False
    controls["dq_pattern"].value = "^ORDER-[0-9]+$"
    assert widget_runtime["calls"]["guardrails"] == []
    state["_controls"]["save_data_contract"].click()
    saved = next(
        record for record in widget_runtime["calls"]["guardrails"][-1]
        if record.get("guardrail_rule_id") == "dq-pattern"
    )
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
    state["_controls"]["dq_type"].value = "pattern"
    state["_controls"]["suggest_dq"].click()

    column = captured["columns"][0]
    assert column["profile_evidence"] == {
        "row_count": 10, "non_null_count": 9, "null_count": 1,
        "null_percent": 10.0, "distinct_count": 8, "distinct_percent": 80.0,
        "mean_value": 5.0, "stddev_value": 2.5,
        "min_value": "1", "percentile_25_value": 3.0, "median_value": 5.0,
        "percentile_75_value": 7.0, "max_value": "9",
    }
    assert column["frequency_evidence"] == [
        {"value": "col-0", "count": 2, "percent": 20.0}
    ]


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
        },
    }

    sections = module._manifest_sections(payload, column_profiles=profiles)

    assert set(sections) == {"Review"}
    review = sections["Review"]
    assert review.index("<b>Table guardrails</b>") < review.index("<b>Column definitions and rules</b>")
    assert review.index("<b>Column definitions and rules</b>") < review.index("<b>Business Rules</b>")
    assert "<b>Business Rules</b> · 2 configured" in review
    assert "<b>Column definitions and rules</b> · 1 columns, 2 column guardrails" in review
    assert "Profile evidence" in review
    assert "Min value: <b>CUS-001</b>" in review
    assert "Max value: <b>CUS-120</b>" in review
    assert "Distinct count: <b>120</b> (<b>100.0%</b>)" in review
    assert "Null count: <b>0</b> (<b>0.0%</b>)" in review
    assert "Customer identifier" in review
    assert "Confidential" in review
    assert "Direct PII · Mask" in review
    assert "Required" in review and ">Yes<" in review
    assert review.count("<b>Pattern</b>") == 1


def test_business_rule_resolve_apply_stages_existing_guardrail_model(
    widget_runtime, monkeypatch
):
    """Resolve natural-language intent and Apply it into normal staged Guardrail state."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    def resolve(_context, **kwargs):
        assert kwargs["requirement"] == "End date must be on or after start date."
        assert kwargs["relevant_columns"] == ["column_0", "column_1"]
        return {
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
        }

    monkeypatch.setattr(module, "suggest_business_rule", resolve)
    controls["top_nav"].value = "Business Rules"
    controls["business_saved"].value = ""
    controls["business_requirement"].value = "End date must be on or after start date."
    controls["business_columns"].value = ("column_0", "column_1")
    controls["resolve_business_rule"].click()

    assert "Known FabricOps pattern: Column Relationship" in controls["business_proposal"].value
    assert "No Engineering review required" in controls["business_proposal"].value
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


def test_custom_business_rule_requires_engineering_review_before_freeze(
    widget_runtime, monkeypatch
):
    """Custom Expressions stage pending review and require an explicit engineer approval."""
    state, _captures = _open_with_ai(widget_runtime, monkeypatch)
    controls = state["_controls"]

    def resolve(_context, **kwargs):
        return {
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
        }

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


def test_range_is_directly_authored_and_saves_without_ai(widget_runtime):
    """Range stays deterministic: edit bounds directly and persist them on contract save."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    before = len(widget_runtime["calls"]["guardrails"])

    controls["dq_type"].value = "range"
    assert controls["suggest_dq"].disabled is True

    controls["dq_enabled"].value = True
    controls["dq_minimum"].value = "1"
    controls["dq_minimum_inclusive"].value = True
    controls["dq_maximum"].value = "100"
    controls["dq_maximum_inclusive"].value = False

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
    }


def test_freeze_activation_manifest_refresh_and_immutable_controls(widget_runtime):
    """Lifecycle actions reload exact state, refresh manifest, and close immutable editors."""
    state = widget_runtime["open"]()
    before = module.DATA_CONTRACT_MANIFEST
    state["_controls"]["freeze"].click()
    assert widget_runtime["calls"]["freeze"] == 0
    state["_controls"]["freeze_confirm"].click()
    assert widget_runtime["calls"]["freeze"] == 1
    assert state["current"]["contract"]["status"] == "frozen"
    assert state["_controls"]["table_description"].disabled is True
    assert module.DATA_CONTRACT_MANIFEST is not before
    state["_controls"]["activate"].click()
    assert widget_runtime["calls"]["activate"] == 1
    assert state["current"]["contract"]["status"] == "frozen"
    assert state["current"]["contract"]["is_active"] is True
    assert "ACTIVE" in state["message"]


def test_column_selector_stays_name_only_when_required_changes(widget_runtime):
    """Required state belongs in the fixed column header, not the navigation list."""
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
    assert label == "column_1"
    assert controls["column_header"].layout.grid_template_columns == "minmax(0, 1fr) 110px"
    assert widget_runtime["calls"]["guardrails"] == []


def test_table_and_column_definitions_share_compact_layout(widget_runtime):
    """Table and column definitions use the same compact aligned editor grid."""
    state = widget_runtime["open"]()
    controls = state["_controls"]

    expected = "120px minmax(240px, 1fr) minmax(240px, 1fr)"
    assert controls["table_definition"].children[1].layout.grid_template_columns == expected
    assert controls["column_definition"].children[1].layout.grid_template_columns == expected
    assert controls["table_classification"].layout.width == "250px"
    assert controls["column_classification"].layout.width == "250px"
    assert controls["column_search"].layout.width == "100%"
    assert controls["column_select"].layout.width == "100%"
    assert all(
        label == f"column_{index}"
        for index, (label, _value) in enumerate(controls["column_select"].options)
    )
    assert "color:#0f6cbd;font-size:20px" in controls["column_context"].value
    assert "Required:" not in controls["column_context"].value


def test_table_classification_updates_left_summary_immediately(widget_runtime):
    """Table classification feedback follows the staged editor value without a save."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    summary = controls["left_pane"].children[0]

    assert "Internal" in summary.value
    controls["table_classification"].value = "Restricted"
    assert "Restricted" in summary.value
    assert "Internal</div>" not in summary.value
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
    summary = controls["left_pane"].children[0]

    assert "Freshness" in summary.value
    controls["table_guardrails"]["freshness"]["enabled"].value = False
    assert "Freshness" in summary.value
    assert "Disabled" in summary.value
    assert widget_runtime["calls"]["guardrails"] == []


def test_review_shows_changes_since_last_save(widget_runtime):
    """Review compares the working contract with the persisted draft baseline."""
    state = widget_runtime["open"]()
    controls = state["_controls"]
    controls["table_classification"].value = "Restricted"
    controls["top_nav"].value = "Manifest & Freeze"

    assert "Changes since last save" in controls["manifest_preview"].value or state["dirty"]
    assert "Restricted" in json.dumps(state["manifest"])
    assert widget_runtime["calls"]["draft"] == []
