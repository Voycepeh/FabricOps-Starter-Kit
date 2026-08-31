"""Behavioural tests for versioned one-table Data Contract assembly."""

from __future__ import annotations

import json
import importlib
import sys
from types import ModuleType

import pytest

import fabricops_kit
from fabricops_kit.widgets import widget_register_data_contract as public_widget
from fabricops_kit.widgets.widget_register_data_contract import (
    _assemble_payload,
    _contract_id,
    _selected_usages,
)

pytestmark = pytest.mark.unit


def _sources():
    audit = {"_committed_at": "2026-01-01T00:00:00", "_activity_id": "a"}
    return {
        "METADATA_DATA_STEWARD": [
            {"steward_id": "provider", "steward_name": "Provider", "steward_role": "Owner", "contact": "provider@example.invalid", "is_active": True, **audit},
            {"steward_id": "recipient", "steward_name": "Recipient", "steward_role": "Consumer", "contact": "recipient@example.invalid", "is_active": True, **audit},
            {"steward_id": "other", "steward_name": "Other", "is_active": True, **audit},
        ],
        "METADATA_DATA_CATALOGUE": [
            {"metadata_level": "table", "table_id": "orders", "column_id": None, "environment_name": "dev", "store_type": "lakehouse", "layer": "gold", "schema_name": "sales", "table_name": "orders", "load_strategy": "scd1", "load_strategy_parameters_json": '{"key_columns":["order_id"]}', "is_active": True, **audit},
            {"metadata_level": "column", "table_id": "orders", "column_id": "order_id", "column_name": "order_id", "data_type": "long", "environment_name": "dev", "is_active": True, **audit},
        ],
        "METADATA_ENRICHMENT": [
            {"enrichment_id": "e1", "table_id": "orders", "column_id": None, "environment_name": "dev", "enrichment_level": "table", "enrichment_type": "description", "value": "Orders", **audit},
            {"enrichment_id": "e2", "table_id": "orders", "column_id": "order_id", "environment_name": "dev", "enrichment_level": "column", "enrichment_type": "description", "value": "Identifier", **audit},
        ],
        "METADATA_GUARDRAIL": [
            {"guardrail_rule_id": "g1", "guardrail_version": 2, "table_id": "orders", "column_id": "order_id", "environment_name": "dev", "guardrail_type": "quality", "rule_id": "not_null", "rule_type": "not_null", "rule_parameters_json": '{"threshold":1}', "severity": "error", "is_active": True, **audit},
            {"guardrail_rule_id": "g2", "guardrail_version": 1, "table_id": "orders", "environment_name": "dev", "guardrail_type": "schema", "rule_id": "old", "rule_type": "schema", "rule_parameters_json": "{}", "severity": "warning", "is_active": False, **audit},
        ],
    }


def _agreement():
    return {"agreement_id": "agreement", "agreement_version": "3", "agreement_name": "Order sharing", "domain": "sales", "business_purpose": "Analytics", "provider_steward_id": "provider", "recipient_steward_id": "recipient", "approved_usage_json": '["analytics","reporting"]'}


def test_contract_identity_is_stable_for_agreement_lifecycle_and_table():
    """Use one stable ID across versions while separating table lifecycles."""
    assert _contract_id("agreement", "orders") == _contract_id("agreement", "orders")
    assert _contract_id("agreement", "orders") != _contract_id("agreement", "customers")


def test_usage_must_be_a_parent_agreement_subset():
    """Reject permissions not granted by the exact parent Agreement."""
    assert _selected_usages(["reporting"], ["analytics", "reporting"]) == ["reporting"]
    with pytest.raises(ValueError, match="subset"):
        _selected_usages(["admin"], ["analytics"])


def test_payload_is_complete_deterministic_and_excludes_runtime_results():
    """Freeze governed definitions, not volatile Guardrail evidence."""
    kwargs = {"contract_id": _contract_id("agreement", "orders"), "contract_version": 1, "agreement": _agreement(), "table_id": "orders", "usages": ["analytics"], "tables": _sources(), "environment_name": "dev"}
    first, warnings = _assemble_payload(**kwargs)
    second, _ = _assemble_payload(**kwargs)
    assert json.dumps(first, sort_keys=True, separators=(",", ":")) == json.dumps(second, sort_keys=True, separators=(",", ":"))
    assert first["agreement"]["agreement_version"] == "3"
    assert first["table"]["table_id"] == "orders"
    assert first["table"]["processing"] == {"load_strategy": "scd1", "key_columns": ["order_id"]}
    assert first["table"]["columns"] == [{"column_id": "order_id", "column_name": "order_id", "data_type": "long"}]
    assert {row["steward_id"] for row in first["stewards"]} == {"provider", "recipient"}
    assert first["enrichment"]["table"][0]["value"] == "Orders"
    assert [row["guardrail_rule_id"] for row in first["guardrails"]] == ["g1"]
    assert first["guardrails"][0]["rule_parameters"] == {"threshold": 1}
    assert "results" not in json.dumps(first).lower()
    assert warnings == []


def test_contract_versions_freeze_catalogue_processing_independently():
    """Keep earlier payloads unchanged when current Catalogue processing changes."""
    sources = _sources()
    kwargs = {
        "contract_id": _contract_id("agreement", "orders"),
        "agreement": _agreement(),
        "table_id": "orders",
        "usages": ["analytics"],
        "tables": sources,
        "environment_name": "dev",
    }
    sources["METADATA_DATA_CATALOGUE"][0].update(
        load_strategy="overwrite", load_strategy_parameters_json="{}"
    )
    version_one, _ = _assemble_payload(contract_version=1, **kwargs)

    sources["METADATA_DATA_CATALOGUE"][0].update(
        load_strategy="scd1",
        load_strategy_parameters_json='{"key_columns":["order_id"]}',
    )
    version_two, _ = _assemble_payload(contract_version=2, **kwargs)

    assert version_one["table"]["processing"] == {"load_strategy": "overwrite"}
    assert version_two["table"]["processing"] == {
        "load_strategy": "scd1",
        "key_columns": ["order_id"],
    }


def test_payload_rejects_inactive_or_unknown_table():
    """Contract only current active logical Catalogue tables."""
    sources = _sources()
    sources["METADATA_DATA_CATALOGUE"][0]["is_active"] = False
    with pytest.raises(ValueError, match="valid active"):
        _assemble_payload(contract_id="c", contract_version=1, agreement=_agreement(), table_id="orders", usages=[], tables=sources, environment_name="dev")


def test_public_export_remains_the_owner_entrypoint():
    """Keep the entrypoint while deleting obsolete inventory helpers."""
    module = importlib.import_module("fabricops_kit.widgets.widget_register_data_contract")
    assert fabricops_kit.widget_register_data_contract is public_widget
    assert module.widget_register_data_contract is public_widget
    assert not hasattr(module, "_latest_inventory")
    assert not hasattr(module, "_compare_schemas")


class _Widget:
    """Observable ipywidget double with trait-style options and values."""

    def __init__(self, *children, value=None, options=None, **kwargs):
        self.children = tuple(children[0]) if children and isinstance(children[0], (list, tuple)) else children
        self.layout = kwargs.get("layout")
        self._observers = []
        self._clicks = []
        self._options = []
        self._value = value
        if options is not None:
            self.options = options

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, values):
        self._options = list(values or [])
        allowed = [item[1] if isinstance(item, tuple) else item for item in self._options]
        if isinstance(self._value, tuple):
            self.value = tuple(item for item in self._value if item in allowed)
        elif self._value not in allowed:
            self.value = allowed[0] if allowed else None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        old = self._value
        self._value = value
        if old != value:
            for callback in list(self._observers):
                callback({"name": "value", "old": old, "new": value})

    def observe(self, callback, names=None):
        self._observers.append(callback)

    def on_click(self, callback):
        self._clicks.append(callback)

    def click(self):
        for callback in self._clicks:
            callback(self)

    def add_class(self, _name):
        return None


class _Layout:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class _Widgets:
    Dropdown = SelectMultiple = HTML = Button = VBox = HBox = _Widget
    Layout = _Layout


class _Frame:
    def __init__(self, rows):
        self.rows = list(rows)

    def collect(self):
        return list(self.rows)


class _Spark:
    def createDataFrame(self, rows, schema=None):
        return _Frame(rows)


def _widget_sources():
    sources = _sources()
    sources["METADATA_DATA_AGREEMENT"] = [
        {**_agreement(), "agreement_id": "agreement-a", "agreement_version": "1.0.0", "agreement_name": "Agreement A", "approved_usage_json": '["analytics","research"]'},
        {**_agreement(), "agreement_id": "agreement-b", "agreement_version": "3.0.0", "agreement_name": "Agreement B", "approved_usage_json": '["internal"]'},
        {**_agreement(), "agreement_id": "agreement-b", "agreement_version": "10.0.0", "agreement_name": "Agreement B", "approved_usage_json": '["internal","reporting"]'},
    ]
    return sources


def _run_widget(monkeypatch, *, agreement_id="agreement-b", agreement_version="10.0.0", approved_usages=None):
    """Run the public widget against deterministic metadata and UI doubles."""
    module = importlib.import_module("fabricops_kit.widgets.widget_register_data_contract")
    tables = {name: _Frame(rows) for name, rows in _widget_sources().items()}
    tables["METADATA_DATA_CONTRACT"] = _Frame([])
    writes = []
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: ({}, "dev", {}))
    monkeypatch.setattr(module, "get_spark_session", lambda spark_session=None: _Spark())
    monkeypatch.setattr(module, "read_lakehouse_table_core", lambda name, **kwargs: tables[name])
    monkeypatch.setattr(module, "write_lakehouse_table_core", lambda frame, name, **kwargs: writes.extend(frame.rows))
    monkeypatch.setattr(module, "build_runtime_audit_fields", lambda **kwargs: {
        "_committed_by": "tester", "_committed_at": "2026-01-01T00:00:00",
        "_workspace_id": "workspace", "_workspace_name": "Workspace",
        "_notebook_id": "notebook", "_notebook_name": "Notebook",
        "_metadata_lakehouse_name": "Metadata", "_activity_id": "activity",
    })
    monkeypatch.setattr(module, "require_ipywidgets", lambda: _Widgets)
    ipython = ModuleType("IPython")
    display_module = ModuleType("IPython.display")
    display_module.display = lambda _value: None
    ipython.display = display_module
    monkeypatch.setitem(sys.modules, "IPython", ipython)
    monkeypatch.setitem(sys.modules, "IPython.display", display_module)
    state = module.widget_register_data_contract(
        agreement_id=agreement_id,
        agreement_version=agreement_version,
        table_id="orders",
        approved_usages=approved_usages,
    )
    return state, writes


def test_widget_initializes_visible_controls_from_supplied_selection(monkeypatch):
    """Keep displayed Agreement, table, usages, and review in one initial state."""
    state, writes = _run_widget(monkeypatch, approved_usages=["reporting"])
    controls = state["_controls"]
    assert controls["agreement"].value == "agreement-b\n10.0.0"
    assert controls["table"].value == "orders"
    assert controls["approved_usages"].options == ["internal", "reporting"]
    assert controls["approved_usages"].value == ("reporting",)
    assert state["review"]["agreement"]["agreement_version"] == "10.0.0"
    assert writes == []


def test_widget_agreement_change_refreshes_and_intersects_usages(monkeypatch):
    """Replace stale usage options and remove permissions absent from the new Agreement."""
    state, _writes = _run_widget(monkeypatch, approved_usages=["reporting"])
    controls = state["_controls"]
    controls["agreement"].value = "agreement-a\n1.0.0"
    assert controls["approved_usages"].options == ["analytics", "research"]
    assert controls["approved_usages"].value == ()
    assert state["approved_usages"] == []
    assert state["review"]["agreement"]["agreement_id"] == "agreement-a"


def test_widget_uses_numeric_agreement_versions_and_appends_contract_versions(monkeypatch):
    """Resolve semantic versions and append exactly one immutable row per save."""
    state, writes = _run_widget(monkeypatch, agreement_version=None, approved_usages=["internal"])
    assert state["agreement_version"] == "10.0.0"
    displayed_payload = state["review"]
    first = state["save"]()
    second = state["save"]()
    assert len(writes) == 2
    assert first["contract_version"] == 1
    assert second["contract_version"] == 2
    assert first["contract_id"] == second["contract_id"]
    assert json.loads(first["contract_payload_json"]) == displayed_payload
    assert first["status"] == "draft" and first["is_active"] is False


def test_widget_different_agreement_table_lifecycle_has_different_identity(monkeypatch):
    """Separate contract lifecycles when the Agreement lifecycle changes."""
    first, _writes = _run_widget(monkeypatch, agreement_id="agreement-a", agreement_version="1.0.0")
    second, _writes = _run_widget(monkeypatch)
    assert first["contract_id"] != second["contract_id"]


def test_widget_cannot_save_stale_usage_from_another_agreement(monkeypatch):
    """Discard a stale visible permission before building or saving the payload."""
    state, writes = _run_widget(monkeypatch, approved_usages=["internal"])
    controls = state["_controls"]
    controls["agreement"].value = "agreement-a\n1.0.0"
    controls["approved_usages"].value = ("internal",)
    saved = state["save"]()
    assert json.loads(saved["contract_payload_json"])["approved_usages"] == []
    assert len(writes) == 1


def test_payload_blocks_when_catalogue_data_type_is_missing():
    """Require complete structural typing from the active Catalogue definition."""
    sources = _sources()
    sources["METADATA_DATA_CATALOGUE"][1]["data_type"] = None
    with pytest.raises(ValueError, match="must define data_type"):
        _assemble_payload(
            contract_id="contract", contract_version=1, agreement=_agreement(),
            table_id="orders", usages=[], tables=sources, environment_name="dev",
        )


def test_payload_uses_catalogue_type_without_profiled_metadata():
    """Assemble the frozen schema entirely from the current Catalogue registry."""
    sources = _sources()
    assert "METADATA_DATA_PROFILED" not in sources
    payload, _warnings = _assemble_payload(
        contract_id="contract", contract_version=1, agreement=_agreement(),
        table_id="orders", usages=[], tables=sources, environment_name="dev",
    )
    assert payload["table"]["columns"] == [
        {"column_id": "order_id", "column_name": "order_id", "data_type": "long"}
    ]


@pytest.mark.parametrize(("strategy", "parameters", "message"), [(None, "{}", "invalid load_strategy"), ("merge", "{}", "invalid load_strategy"), ("scd1", "{}", "requires key_columns"), ("scd2", '{"key_columns":["order_id"]}', "requires effective_column")])
def test_contract_registration_requires_valid_processing(strategy, parameters, message):
    """Reject every processing definition that runtime would reject."""
    sources = _sources(); sources["METADATA_DATA_CATALOGUE"][0].update(load_strategy=strategy, load_strategy_parameters_json=parameters)
    with pytest.raises(ValueError, match=message):
        _assemble_payload(contract_id="c", contract_version=1, agreement=_agreement(), table_id="orders", usages=[], tables=sources, environment_name="dev")


def test_contract_registration_preserves_processing_parameters():
    """Preserve canonical parameters in the frozen payload."""
    sources = _sources(); sources["METADATA_DATA_CATALOGUE"][0].update(load_strategy="scd2", load_strategy_parameters_json='{"key_columns":["order_id"],"effective_column":"effective_at","tracked_columns":["status"]}')
    payload, _ = _assemble_payload(contract_id="c", contract_version=1, agreement=_agreement(), table_id="orders", usages=[], tables=sources, environment_name="dev")
    assert payload["table"]["processing"] == {"load_strategy": "scd2", "key_columns": ["order_id"], "effective_column": "effective_at", "tracked_columns": ["status"]}
