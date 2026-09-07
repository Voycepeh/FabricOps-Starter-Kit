"""Structural tests for the reusable agreement form layout."""

from __future__ import annotations

from types import SimpleNamespace
import importlib
import sys

import pytest

import fabricops_kit.widgets.shared as shared
import fabricops_kit.widgets.widget_render_data_agreement as agreement_widget
import fabricops_kit.widgets.widget_render_data_steward as steward_widget
import fabricops_kit.widgets as widgets_package
from fabricops_kit.widgets import widget_register_data_contract as contract_callable
contract_widget = importlib.import_module("fabricops_kit.widgets.widget_register_data_contract")
widgets_package.widget_register_data_contract = contract_callable
from tests.helpers import agreement_config, agreement_row, steward_row
from tests.unit.test_agreements import _FakeWidget, _FakeWidgets

pytestmark = pytest.mark.unit


def _render(monkeypatch):
    config = agreement_config()
    monkeypatch.setattr(agreement_widget, "resolve_fabric_context", lambda context=None: (config, "dev", {}))
    monkeypatch.setitem(sys.modules, "IPython", SimpleNamespace(display=SimpleNamespace(display=lambda value: None)))
    monkeypatch.setattr(shared, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(agreement_widget, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(agreement_widget, "list_data_agreements", lambda *args, **kwargs: [])
    monkeypatch.setattr(
        agreement_widget,
        "list_data_stewards",
        lambda *args, **kwargs: [steward_row(), steward_row(steward_id="22222222-2222-4222-8222-222222222222")],
    )
    return agreement_widget.widget_render_data_agreement(spark=object())


def _visible_text(widget):
    values = [str(getattr(widget, "value", "") or ""), str(getattr(widget, "description", "") or "")]
    values.extend(_visible_text(child) for child in getattr(widget, "children", ()))
    return " ".join(values)


def _render_steward(monkeypatch, *, custom_fields=None, stewards=None):
    config = agreement_config()
    if custom_fields is not None:
        config.data_agreement_config.data_steward_widget["custom_fields"] = custom_fields
    steward_rows = [steward_row()] if stewards is None else stewards
    monkeypatch.setattr(steward_widget, "resolve_fabric_context", lambda context=None: (config, "dev", {}))
    monkeypatch.setitem(sys.modules, "IPython", SimpleNamespace(display=SimpleNamespace(display=lambda value: None)))
    monkeypatch.setattr(steward_widget, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(shared, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(steward_widget, "list_data_stewards", lambda *args, **kwargs: steward_rows)
    return steward_widget.widget_render_data_steward(spark=object())


def _render_contract(monkeypatch, *, writer=None):
    class Frame:
        def __init__(self, rows):
            self.rows = list(rows)

        def collect(self):
            return list(self.rows)

    class Spark:
        def createDataFrame(self, rows, schema=None):
            return Frame(rows)

    audit = {"_committed_at": "2026-08-03", "_activity_id": "activity-1"}
    tables = {
        "METADATA_DATA_AGREEMENT": Frame([{
            "agreement_id": "agreement-1", "agreement_version": "1.0.0",
            "agreement_name": "Orders Agreement", "domain": "sales",
            "business_purpose": "Reporting", "provider_steward_id": "provider",
            "recipient_steward_id": "recipient", "approved_usage_json": '["reporting"]', **audit,
        }]),
        "METADATA_DATA_STEWARD": Frame([
            {"steward_id": "provider", "steward_name": "Provider", "is_active": True, **audit},
            {"steward_id": "recipient", "steward_name": "Recipient", "is_active": True, **audit},
        ]),
        "METADATA_DATA_CATALOGUE": Frame([
            {"metadata_level": "table", "table_id": "table-1", "column_id": None,
             "environment_name": "dev", "store_type": "lakehouse", "layer": "curated",
             "schema_name": "sales", "table_name": "orders", "load_strategy": "overwrite",
             "load_strategy_parameters_json": "{}", "is_active": True, **audit},
            {"metadata_level": "column", "table_id": "table-1", "column_id": "column-1",
             "column_name": "example_column", "data_type": "string", "environment_name": "dev",
             "is_active": True, **audit},
        ]),
        "METADATA_ENRICHMENT": Frame([]),
        "METADATA_GUARDRAIL": Frame([]),
        "METADATA_DATA_CONTRACT": Frame([]),
    }
    class SelectMultiple(_FakeWidget):
        def __init__(self, value=(), options=None, **kwargs):
            super().__init__(value=None, options=options, **kwargs)
            self.value = tuple(value)

    _FakeWidgets.SelectMultiple = SelectMultiple
    monkeypatch.setattr(contract_widget, "require_ipywidgets", lambda: _FakeWidgets)
    monkeypatch.setattr(contract_widget, "resolve_fabric_context", lambda **kwargs: ({}, "dev", {}))
    monkeypatch.setattr(contract_widget, "get_spark_session", lambda value=None: Spark())
    monkeypatch.setattr(contract_widget, "read_lakehouse_table_core", lambda name, **kwargs: tables[name])
    monkeypatch.setattr(contract_widget, "write_lakehouse_table_core", writer or (lambda *args, **kwargs: None))
    monkeypatch.setattr(contract_widget, "build_runtime_audit_fields", lambda **kwargs: {
        "_committed_by": "tester", "_committed_at": "2026-08-03",
        "_workspace_id": "workspace", "_workspace_name": "Workspace",
        "_notebook_id": "notebook", "_notebook_name": "Notebook",
        "_metadata_lakehouse_name": "Metadata", "_activity_id": "activity-1",
    })
    monkeypatch.setitem(sys.modules, "IPython", SimpleNamespace(display=SimpleNamespace(display=lambda value: None)))
    return contract_widget.widget_register_data_contract(
        agreement_id="agreement-1", agreement_version="1.0.0", table_id="table-1",
        approved_usages=["reporting"], spark_session=object(),
    )


def test_shared_form_containers_expand_without_scrollbars():
    """Keep reusable page and section containers naturally expanding."""
    section = shared.form_section(_FakeWidgets, title="Details", children=[_FakeWidget()])
    page = shared.form_page(_FakeWidgets, title="Title", description="Description", children=[section])

    for container in (page, section):
        assert container.layout.kwargs["width"] == "100%"
        assert container.layout.kwargs["height"] == "auto"
        assert container.layout.kwargs["overflow"] == "visible"

    css = page.children[0].value
    assert ".fabricops-form .widget-inline-hbox{display:flex;flex-direction:column;align-items:stretch;" in css
    assert ".fabricops-form .widget-inline-hbox>.widget-label{width:100%;margin:0 0 6px;flex:none;}" in css

    common = shared.widget_common(_FakeWidgets, "Example")
    assert common["layout"].kwargs["width"] == "100%"
    assert common["layout"].kwargs["min_width"] == "0"
    assert common["layout"].kwargs["max_width"] == "100%"

    grid = shared.form_grid(_FakeWidgets, [_FakeWidget(), _FakeWidget()])
    assert grid.layout.kwargs["grid_template_columns"] == "repeat(auto-fit, minmax(min(100%, 280px), 1fr))"
    assert grid.layout.kwargs["grid_gap"] == "16px 24px"


def test_long_search_results_are_bounded_without_scrolling_the_form():
    """Bound selector results without adding scrollbars to its container."""
    selector = shared.render_searchable_selector(
        widgets=_FakeWidgets,
        label="Steward",
        rows=[{"id": str(index), "name": f"Steward {index}"} for index in range(50)],
        label_fn=lambda row: row["name"],
        value_fn=lambda row: row["id"],
    )

    assert len(selector["selector"].options) == 25
    assert selector["container"].layout.kwargs["height"] == "auto"
    assert selector["container"].layout.kwargs["overflow"] == "visible"


def test_agreement_form_has_meaningful_groups_and_fabric_safe_status(monkeypatch):
    """Expose meaningful agreement labels and a Fabric-safe result status."""
    controls = _render(monkeypatch)
    text = _visible_text(controls["container"])

    for label in (
        "Approved usages",
        "Provider Data Steward",
        "Recipient Data Steward",
        "Search provider data stewards",
        "Search recipient data stewards",
        "Document name",
        "Document link",
        "Custom columns",
    ):
        assert label in text
    assert "Approved usage</" not in text
    assert {key: (box.description, box.value) for key, box in controls["approved_usage_checkboxes"].items()} == {
        "internal cross domain": ("Internal Cross Domain", False),
        "internal single domain": ("Internal Single Domain", False),
        "research": ("Research", False),
        "external": ("External", False),
    }
    assert controls["save_button"].click_callbacks
    assert controls["existing_record"].callbacks
    assert "execution_output" not in controls
    assert "execution_log_section" not in controls


def test_save_preserves_emitted_lakehouse_output_and_restores_button(monkeypatch, capsys):
    """Keep complete technical output and restore Save after persistence."""
    message = "Writing Lakehouse table to abfss://container@account.dfs.core.windows.net/path"

    def save(**kwargs):
        print(message)
        return agreement_row(agreement_id="33333333-3333-4333-8333-333333333333")

    monkeypatch.setattr(agreement_widget, "_create_or_update_data_agreement", save)
    controls = _render(monkeypatch)
    controls["approved_usage_checkboxes"]["internal cross domain"].value = True
    controls["save_button"].click_callbacks[0](None)

    assert message in capsys.readouterr().out
    assert controls["save_button"].disabled is False


def test_agreement_save_validation_error_stays_in_status_and_later_success_recovers(monkeypatch, capsys):
    """Handle Fabric validation failures without notebook-level output or stale status."""
    attempts = []
    callbacks = []
    refreshes = []

    def save(**kwargs):
        attempts.append(kwargs)
        assert controls["status"].value == ""
        if len(attempts) == 1:
            raise ValueError("expiry_date must be on or after start_date.")
        return agreement_row(agreement_id="33333333-3333-4333-8333-333333333333", agreement_version="1.0.0")

    monkeypatch.setattr(agreement_widget, "_create_or_update_data_agreement", save)
    controls = _render(monkeypatch)
    controls["status"].value = '<span style="color:#107c10">Previous status</span>'
    controls["after_save_callbacks"].append(callbacks.append)
    original_refresh_rows = controls["existing_record"].refresh_rows

    def refresh_rows(rows, selected=None):
        refreshes.append((list(rows), selected))
        original_refresh_rows(rows, selected)

    controls["existing_record"].refresh_rows = refresh_rows
    controls["approved_usage_checkboxes"]["internal cross domain"].value = True

    controls["save_button"].click_callbacks[0](None)

    first_output = capsys.readouterr()
    assert first_output.out == ""
    assert first_output.err == ""
    assert "Error: expiry_date must be on or after start_date." in controls["status"].value
    assert "cannot access local variable 'row'" not in controls["status"].value
    assert callbacks == []
    assert refreshes == []
    assert controls["save_button"].disabled is False

    controls["save_button"].click_callbacks[0](None)

    second_output = capsys.readouterr()
    assert second_output.out == ""
    assert second_output.err == ""
    assert "Saved Orders Agreement (33333333-3333-4333-8333-333333333333 v1.0.0)." in controls["status"].value
    assert "expiry_date must be on or after start_date" not in controls["status"].value
    assert callbacks == [controls["existing_records_by_id"]["33333333-3333-4333-8333-333333333333"]]
    assert refreshes[-1][1] == "33333333-3333-4333-8333-333333333333"
    assert controls["existing_record"].value == "33333333-3333-4333-8333-333333333333"
    assert "Agreement ID: 33333333-3333-4333-8333-333333333333" in controls["identity_context"].value


def test_steward_form_uses_simplified_visible_layout(monkeypatch):
    """Compose steward maintenance with one form flow and hidden technical output."""
    controls = _render_steward(monkeypatch)
    text = _visible_text(controls["container"])

    for label in (
        "Data Steward", "Create or update data stewards", "Steward selection",
        "Steward details", "Additional information", "Search data stewards",
        "Select or create steward", "Save steward",
    ):
        assert label in text
    for removed in (
        "Data Steward Creation Widget", "Existing data steward",
        "Contact or supporting information", "Custom columns", "Save result",
        "Execution log", "Steward name:</b>", "Role:</b>", "Contact:</b>",
        "Steward ID:</b>",
    ):
        assert removed not in text
    assert "Optional" not in text
    assert controls["save_button"].description == "Save steward"
    assert controls["save_button"].click_callbacks
    assert controls["container"].layout.kwargs["height"] == "auto"
    assert "execution_output" not in controls
    assert "execution_log_section" not in controls


def test_steward_additional_information_renders_only_for_custom_fields(monkeypatch):
    """Show the custom field section only when configured."""
    controls = _render_steward(monkeypatch, custom_fields=[])
    text = _visible_text(controls["container"])

    assert "Additional information" not in text
    assert controls["custom_fields"] == {}


def test_steward_selector_search_population_and_save_paths_remain_unchanged(monkeypatch, capsys):
    """Keep selector filtering, form population, custom fields, and create/update saves working."""
    writes = []
    rows = [
        steward_row(custom_fields_json='{"group":"Shared Services"}'),
        steward_row(
            steward_id="22222222-2222-4222-8222-222222222222",
            steward_name="Analytics Steward",
            steward_role="Governance Reviewer",
            contact="analytics@example.com",
            custom_fields_json='{"group":"Analytics"}',
        ),
    ]

    def save(**kwargs):
        values = dict(kwargs["values"])
        row = {
            "steward_id": values.get("steward_id") or "33333333-3333-4333-8333-333333333333",
            "steward_name": values["steward_name"],
            "steward_role": values["steward_role"],
            "contact": values["contact"],
            "custom_fields": kwargs["custom_fields"],
        }
        writes.append(row)
        print("Writing Lakehouse steward row")
        return row

    monkeypatch.setattr(steward_widget, "_create_or_update_data_steward", save)
    controls = _render_steward(monkeypatch, stewards=rows)

    search = controls["existing_record_search"]
    search.value = "Analytics"
    search.callbacks[0]({"name": "value"})
    assert controls["existing_record"].options == [
        ("Create new steward", ""),
        (
            "Analytics Steward | Governance Reviewer | analytics@example.com",
            "22222222-2222-4222-8222-222222222222",
        ),
    ]

    controls["existing_record"].value = "22222222-2222-4222-8222-222222222222"
    controls["existing_record"].callbacks[0]({
        "name": "value",
        "new": "22222222-2222-4222-8222-222222222222",
    })
    assert controls["fields"]["steward_name"].value == "Analytics Steward"
    assert controls["fields"]["steward_role"].value == "Governance Reviewer"
    assert controls["fields"]["contact"].value == "analytics@example.com"
    assert controls["custom_fields"]["group"].value == "Analytics"

    controls["save_button"].click_callbacks[0](None)
    assert writes[-1]["steward_id"] == "22222222-2222-4222-8222-222222222222"
    assert writes[-1]["custom_fields"] == {"group": "Analytics"}
    assert controls["status"].value == "Data steward saved successfully: Analytics Steward"
    assert "22222222-2222-4222-8222-222222222222" not in controls["status"].value
    assert "Writing Lakehouse steward row" in capsys.readouterr().out

    controls["existing_record"].value = ""
    controls["existing_record"].callbacks[0]({"name": "value", "new": ""})
    controls["fields"]["steward_name"].value = "New Steward"
    controls["fields"]["steward_role"].value = "Data Owner"
    controls["fields"]["contact"].value = "new@example.com"
    controls["custom_fields"]["group"].value = "New group"
    controls["save_button"].click_callbacks[0](None)

    assert writes[-1]["steward_id"] == "33333333-3333-4333-8333-333333333333"
    assert writes[-1]["custom_fields"] == {"group": "New group"}
    assert controls["status"].value == "Data steward saved successfully: New Steward"


def test_contract_form_uses_labelled_shared_sections(monkeypatch):
    """Compose one-table contract controls with shared responsive form sections."""
    state = _render_contract(monkeypatch)
    controls = state["_controls"]
    page = controls["page"]
    text = _visible_text(page)

    for label in (
        "Prepare Data Contract", "Data Agreement", "Governed table",
        "Approved usages", "1. Agreement and table", "2. Approved usage",
            "3. Draft contract", "Save draft Data Contract", "Freeze Data Contract",
    ):
        assert label in text
    assert controls["save"].click_callbacks
    assert page.layout.kwargs["width"] == "100%"
    assert page.layout.kwargs["height"] == "auto"
    assert page.layout.kwargs["overflow"] == "visible"
    assert "execution_output" not in controls
    assert "execution_log_section" not in controls


def test_contract_save_preserves_complete_notebook_stdout(monkeypatch, capsys):
    """Leave the technical Lakehouse destination on ordinary notebook stdout."""
    message = "Writing Lakehouse table to abfss://container@account.dfs.core.windows.net/path"

    def write(*args, **kwargs):
        print(message)

    state = _render_contract(monkeypatch, writer=write)
    state["_controls"]["save"].click_callbacks[0](None)

    assert message in capsys.readouterr().out
    assert "Saved draft" in state["_controls"]["status"].value
