"""Focused contracts for unified Data Contract authoring."""

from __future__ import annotations

import importlib
import inspect
import sys
import types

import pytest


module = importlib.import_module("fabricops_kit.widgets.widget_author_data_contract")


def _install_widgets(monkeypatch):
    """Install small observable notebook widget fakes."""
    class Widget:
        def __init__(self, *args, **kwargs):
            del args
            self.options = kwargs.get("options", ())
            self.description = kwargs.get("description", "")
            self.disabled = kwargs.get("disabled", False)
            self._observers = []
            self._value = kwargs.get("value", None)
            if self._value is None and self.options:
                first = self.options[0]
                self._value = first[1] if isinstance(first, tuple) else first
        @property
        def value(self):
            return self._value
        @value.setter
        def value(self, value):
            old = self._value; self._value = value
            if old != value:
                for callback in self._observers:
                    callback({"old": old, "new": value})
        def observe(self, callback, names=None):
            del names
            self._observers.append(callback)
        def on_click(self, callback):
            self._click = callback
        def click(self):
            self._click(self)
        def add_class(self, _name):
            return None
    class Box(Widget):
        def __init__(self, children=(), *args, **kwargs):
            super().__init__(*args, **kwargs); self.children = tuple(children)
    class HTML(Widget):
        pass
    class SelectMultiple(Widget):
        pass
    fake = types.SimpleNamespace(
        Combobox=Widget, Textarea=Widget, Button=Widget, HTML=HTML, ToggleButtons=Widget,
        Dropdown=Widget, SelectMultiple=SelectMultiple, FloatText=Widget, VBox=Box, GridBox=type("GridBox", (Box,), {}),
        Layout=lambda **kwargs: types.SimpleNamespace(**kwargs),
    )
    monkeypatch.setattr(module.shared, "require_ipywidgets", lambda: fake)
    monkeypatch.setitem(sys.modules, "IPython", types.SimpleNamespace(display=types.SimpleNamespace(display=lambda *_args: None)))
    return fake


def _state(column_count: int = 3):
    columns = [
        {
            "table_id": "table-orders", "column_id": f"column-{index}",
            "column_name": f"column_{index}", "data_type": "string",
            "metadata_level": "column", "environment_name": "dev", "is_active": True,
        }
        for index in range(column_count)
    ]
    table = {
        "table_id": "table-orders", "table_name": "Orders", "metadata_level": "table",
        "environment_name": "dev", "load_strategy": "SCD2",
    }
    return {
        "contract": {
            "contract_id": "contract-orders", "contract_version": 3,
            "table_id": "table-orders", "agreement_id": "finance", "agreement_version": "1",
            "environment_name": "dev", "status": "draft", "contract_payload_json": None,
        },
        "contract_id": "contract-orders", "contract_version": 3,
        "table_id": "table-orders", "environment_name": "dev",
        "catalogue_rows": [table, *columns], "available_columns": columns,
        "enrichment": [{
            "contract_id": "contract-orders", "contract_version": 3,
            "environment_name": "dev", "column_id": "column-0",
            "enrichment_level": "column", "enrichment_type": "Description", "value": "Order key",
        }],
        "guardrails": [{
            "guardrail_rule_id": "existing", "guardrail_version": 1,
            "contract_id": "contract-orders", "contract_version": 3,
            "environment_name": "dev", "guardrail_type": "schema", "rule_id": "schema",
            "rule_type": "minimum_required", "rule_parameters_json": '{"columns":["column_0"]}',
            "action": "Block", "is_active": True, "column_id": "",
        }],
    }


@pytest.fixture
def widget(monkeypatch):
    """Build a service-isolated unified authoring widget."""
    state = _state()
    _install_widgets(monkeypatch)
    calls = {"loads": [], "enrichment": [], "guardrails": [], "validate": [], "freeze": []}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda **_kwargs: (object(), "dev", {}))
    monkeypatch.setattr(module.contract_authoring, "validate_contract_identity", lambda cid, version: (cid, int(version)))
    def load(**kwargs):
        calls["loads"].append((kwargs["contract_id"], kwargs["contract_version"]))
        return {key: (list(value) if isinstance(value, list) else dict(value) if isinstance(value, dict) else value) for key, value in state.items()}
    monkeypatch.setattr(module.contract_authoring, "get_contract_authoring_state", load)
    monkeypatch.setattr(module.contract_authoring, "save_enrichment", lambda records, **_kwargs: calls["enrichment"].append(records) or records)
    monkeypatch.setattr(module.contract_authoring, "save_guardrails", lambda records, **_kwargs: calls["guardrails"].append(records) or records)
    monkeypatch.setattr(module.contract_authoring, "validate_contract_draft", lambda *args, **kwargs: calls["validate"].append((args, kwargs)) or {
        "contract": state["contract"], "enrichment": state["enrichment"], "guardrails": state["guardrails"],
    })
    monkeypatch.setattr(module.contract_authoring, "freeze_contract", lambda **kwargs: calls["freeze"].append(kwargs) or {
        "contract": {**kwargs["draft"], "status": "frozen"},
        "payload": {"contract": {"contract_id": kwargs["draft"]["contract_id"]}},
        "warnings": [],
    })
    result = module.widget_author_data_contract(
        contract_id="contract-orders", contract_version=3,
        spark_session=object(), context={"config": object(), "env": "dev"},
    )
    return result, calls


def test_exact_version_overview_and_existing_guardrails(widget):
    """Selection remains exact and passive views expose the contract state."""
    result, calls = widget
    assert calls["loads"] == [("contract-orders", 3)]
    assert result["state"]["table_id"] == "table-orders"
    assert "Orders" in result["ui"].children[0].value
    assert "table-orders" in result["ui"].children[0].value
    assert "SCD2" in result["render_section"]("Overview").value
    guardrail = result["render_section"]("Guardrails")
    assert "Required: column_0" in guardrail.children[0].value
    assert ("Data Quality", "Data Quality") in result["controls"]["guardrail_type"].options


def test_one_selected_enrichment_column_uses_service(widget):
    """The one-column editor submits descriptive Enrichment to the service."""
    result, calls = widget
    result["render_section"]("Enrichment")
    controls = result["controls"]
    controls["enrichment_column"].value = "column_1"
    controls["enrichment_description"].value = "Customer-facing order label"
    controls["enrichment_save"].click()
    record = calls["enrichment"][0][0]
    assert record["column_id"] == "column-1"
    assert record["enrichment_type"] == "Description"
    assert record["contract_id"] == "contract-orders"
    assert record["contract_version"] == 3


@pytest.mark.parametrize("kind", ["Schema", "Freshness", "Changes", "Data Quality", "Sensitive Data"])
def test_each_guardrail_subtype_is_lazy_and_uses_normalized_service(widget, kind):
    """Only the selected subtype mounts controls and every subtype saves centrally."""
    result, calls = widget
    result["render_section"]("Guardrails")
    editor = result["controls"]["guardrail_editor"]
    assert editor.children == ()
    result["controls"]["guardrail_type"].value = kind
    subtype = result["controls"]["guardrail_subtype_controls"]
    fields = subtype["fields"]
    if kind == "Schema":
        fields[0].value = ("column_0",)
    elif kind == "Data Quality":
        fields[1].value = ("column_0",)
    elif kind == "Changes":
        fields[0].value = "Incremental append"
    subtype["save"].click()
    assert calls["guardrails"]
    expected = {"Schema": "schema", "Freshness": "freshness", "Changes": "changes", "Data Quality": "data_quality", "Sensitive Data": "sensitive_data"}[kind]
    assert calls["guardrails"][0][0]["guardrail_type"] == expected


def test_review_validates_and_freezes_through_authoritative_services(widget):
    """Review and freeze delegate governance rules and persistence to services."""
    result, calls = widget
    result["render_section"]("Review")
    assert calls["validate"]
    result["controls"]["freeze"].click()
    assert calls["freeze"][0]["draft"]["contract_version"] == 3
    assert calls["freeze"][0]["draft"]["contract_id"] == "contract-orders"
    assert "payload" not in calls["freeze"][0]
    source = inspect.getsource(module.widget_author_data_contract)
    assert '"agreement"' not in source
    assert '"stewards"' not in source
    assert '"approved_usages"' not in source
    registration = importlib.import_module("fabricops_kit.widgets.widget_register_data_contract")
    registration_source = inspect.getsource(registration.widget_register_data_contract)
    assert "freeze_contract(" in source
    assert "freeze_contract(" in registration_source
    assert "assemble_contract_payload(" not in source
    assert "assemble_contract_payload(" not in registration_source


def test_html_escaping_and_large_schema_widget_model_regression(monkeypatch):
    """A 100-column schema stays aggregated and unsafe text is escaped."""
    widgets = _install_widgets(monkeypatch)
    state = _state(100)
    state["catalogue_rows"][0]["table_name"] = '<script>alert("x")</script>'
    monkeypatch.setattr(module, "resolve_fabric_context", lambda **_kwargs: (object(), "dev", {}))
    monkeypatch.setattr(module.contract_authoring, "validate_contract_identity", lambda cid, version: (cid, int(version)))
    monkeypatch.setattr(module.contract_authoring, "get_contract_authoring_state", lambda **_kwargs: state)
    result = module.widget_author_data_contract(contract_id="contract-orders", contract_version=3, spark_session=object())
    overview = result["ui"].children[0]
    assert "&lt;script&gt;" in overview.value and "<script>" not in overview.value
    enrichment = result["render_section"]("Enrichment")
    assert sum(isinstance(child, widgets.HTML) for child in enrichment.children) == 1
    result["render_section"]("Guardrails")
    result["controls"]["guardrail_type"].value = "Schema"
    assert len(result["controls"]["guardrail_subtype_controls"]["fields"]) == 1
    assert isinstance(result["controls"]["guardrail_subtype_controls"]["fields"][0], widgets.SelectMultiple)
    assert not any(isinstance(child, widgets.GridBox) for child in result["ui"].children)


def test_passive_table_helper_escapes_every_dynamic_cell():
    """Aggregated table rendering never exposes an arbitrary HTML path."""
    rendered = module._table_html(("<header>",), [("<img src=x onerror=1>",)], empty="<empty>")
    assert "<header>" not in rendered
    assert "<img" not in rendered
    assert "&lt;img src=x onerror=1&gt;" in rendered
