"""Structural tests for the reusable agreement form layout."""

from __future__ import annotations

from tests.helpers import call_with_spark

from types import SimpleNamespace
import sys

import pytest

import fabricops_kit.widgets.shared as shared
import fabricops_kit.widgets.widget_render_data_agreement as agreement_widget
import fabricops_kit.widgets.widget_render_data_steward as steward_widget
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
    return call_with_spark(object(), agreement_widget.widget_render_data_agreement, )


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
    return call_with_spark(object(), steward_widget.widget_render_data_steward, )


def test_shared_form_viewport_is_bounded_while_sections_expand_naturally():
    """Bound and scroll the page while keeping its internal sections natural."""
    section = shared.form_section(_FakeWidgets, title="Details", children=[_FakeWidget()])
    page = shared.form_page(_FakeWidgets, title="Title", description="Description", children=[section])

    assert page.layout.kwargs["width"] == "100%"
    assert page.layout.kwargs["min_width"] == "0"
    assert page.layout.kwargs["max_width"] == "100%"
    assert page.layout.kwargs["height"] == "720px"
    assert page.layout.kwargs["overflow"] == "auto"

    assert section.layout.kwargs["width"] == "100%"
    assert section.layout.kwargs["height"] == "auto"
    assert section.layout.kwargs["overflow"] == "visible"

    css = page.children[0].value
    assert '.widget-inline-hbox:not(.widget-checkbox):not(.widget-html)' in css
    assert 'grid-template-columns:minmax(0,1fr)' in css
    assert '.fabricops-form .widget-html.widget-inline-hbox { display:block;' in css
    assert '.fabricops-form .widget-checkbox > .widget-label { display:none; }' in css
    assert 'fabricops-page-header' in css
    assert '--form-tint:#eaf3fb' in css
    assert '--form-tint:#f1edf8' in css

    common = shared.widget_common(_FakeWidgets, "Example")
    assert common["style"]["description_width"] == "150px"
    assert common["layout"].kwargs["width"] == "100%"
    assert common["layout"].kwargs["min_width"] == "0"
    assert common["layout"].kwargs["max_width"] == "100%"

    empty = shared.widget_common(_FakeWidgets, "   ")
    assert empty["description"] == ""
    assert empty["style"]["description_width"] == "0px"

    grid = shared.form_grid(_FakeWidgets, [_FakeWidget(), _FakeWidget()])
    assert grid.layout.kwargs["grid_template_columns"] == "repeat(auto-fit, minmax(min(100%, 280px), 1fr))"
    assert grid.layout.kwargs["grid_gap"] == "16px 24px"


def test_long_search_results_use_one_compact_combobox_without_scrolling_the_form():
    """Keep long dynamic lists searchable without rendering a permanent list box."""
    selector = shared.render_searchable_selector(
        widgets=_FakeWidgets,
        label="Steward",
        rows=[{"id": str(index), "name": f"Steward {index}"} for index in range(50)],
        label_fn=lambda row: row["name"],
        value_fn=lambda row: row["id"],
    )

    assert len(selector["search"].options) == 50
    assert selector["container"].children == [selector["search"]]
    assert selector["search"].placeholder == "Search..."
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
        "Document name",
        "Document link",
        "Custom columns",
    ):
        assert label in text
    assert "Approved usage</" not in text
    assert "Save result" not in text
    assert "Custom columns" in text
    assert {key: (box.description, box.value) for key, box in controls["approved_usage_checkboxes"].items()} == {
        "internal cross domain": ("Internal Cross Domain", False),
        "internal single domain": ("Internal Single Domain", False),
        "research": ("Research", False),
        "external": ("External", False),
    }
    assert controls["save_button"].description == "Save and clear"
    assert controls["discard_button"].description == "Discard and clear"
    assert controls["save_button"].click_callbacks
    assert controls["discard_button"].click_callbacks
    assert controls["save_button"].disabled is True
    assert controls["existing_record"].callbacks
    assert "execution_output" not in controls
    assert "execution_log_section" not in controls


def test_governance_save_sections_share_white_card_layout(monkeypatch):
    """Keep the Steward and Agreement save controls in matching white cards."""
    agreement = _render(monkeypatch)
    steward = _render_steward(monkeypatch)
    for controls, heading in ((agreement, "Save agreement"), (steward, "Save steward")):
        actions = controls["container"].children[-1]
        assert actions.layout.kwargs["border"] == "1px solid #dce4ed"
        assert heading in actions.children[0].value
        assert controls["status"] is actions.children[-1]


def test_agreement_selector_shows_parties_and_dates_without_identity_details():
    """Present business context in the latest agreement label."""
    row = agreement_row(
        agreement_id="33333333-3333-4333-8333-333333333333",
        agreement_version="1.2.0",
        provider_steward_name="Provider",
        recipient_steward_name="Recipient",
    )
    label = agreement_widget._agreement_label(row)
    assert label == "Orders Agreement — between Provider and Recipient — 2026-01-01 to 2026-12-31"
    assert row["agreement_id"] not in label
    assert row["agreement_version"] not in label


def test_agreement_save_enables_only_after_required_inputs(monkeypatch):
    """Require a complete agreement draft before enabling Save."""
    controls = _render(monkeypatch)
    assert controls["save_button"].disabled
    for field, value in agreement_row().items():
        if field in controls["fields"]:
            controls["fields"][field].value = value
    controls["approved_usage_checkboxes"]["internal cross domain"].value = True
    controls["fields"]["agreement_name"].callbacks[-1]({"new": "Orders Agreement"})
    assert not controls["save_button"].disabled
    controls["fields"]["agreement_name"].value = ""
    controls["fields"]["agreement_name"].callbacks[-1]({"new": ""})
    assert controls["save_button"].disabled


def test_agreement_discard_and_clear_does_not_save(monkeypatch):
    """Discard agreement edits without appending an agreement version."""
    writes = []
    monkeypatch.setattr(
        agreement_widget,
        "_create_or_update_data_agreement",
        lambda **kwargs: writes.append(kwargs),
    )
    controls = _render(monkeypatch)
    controls["fields"]["agreement_name"].value = "Unsaved agreement"
    controls["custom_fields"]["consumer_group"].value = "ODI"
    controls["approved_usage_checkboxes"]["research"].value = True

    controls["discard_button"].click_callbacks[0](None)

    assert writes == []
    assert controls["fields"]["agreement_name"].value == ""
    assert controls["custom_fields"]["consumer_group"].value == ""
    assert not any(box.value for box in controls["approved_usage_checkboxes"].values())
    assert len(controls["supporting_documents"]) == 1
    assert "discarded" in controls["status"].value.lower()


def test_save_preserves_emitted_lakehouse_output_and_restores_button(monkeypatch, capsys):
    """Keep complete technical output and restore Save after persistence."""
    message = "Writing Lakehouse table to abfss://container@account.dfs.core.windows.net/path"

    def save(**kwargs):
        print(message)
        return agreement_row(agreement_id="33333333-3333-4333-8333-333333333333", agreement_version="1.0.0")

    monkeypatch.setattr(agreement_widget, "_create_or_update_data_agreement", save)
    controls = _render(monkeypatch)
    controls["approved_usage_checkboxes"]["internal cross domain"].value = True
    controls["save_button"].click_callbacks[0](None)

    assert message in capsys.readouterr().out
    assert controls["save_button"].disabled is True  # The form was cleared after saving.


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
    assert controls["save_button"].disabled is True  # Required fields remain blank.

    controls["save_button"].click_callbacks[0](None)

    second_output = capsys.readouterr()
    assert second_output.out == ""
    assert second_output.err == ""
    assert "Saved Orders Agreement." in controls["status"].value
    assert "expiry_date must be on or after start_date" not in controls["status"].value
    assert callbacks == [controls["existing_records_by_id"]["33333333-3333-4333-8333-333333333333"]]
    assert refreshes[-1][1] == "33333333-3333-4333-8333-333333333333"
    assert controls["existing_record"].value == ""
    assert "identity_context" not in controls


def test_agreement_callback_failure_after_write_still_clears_form(monkeypatch):
    """A failed observer must not make a persisted agreement appear unsaved."""
    writes = []

    def save(**kwargs):
        writes.append(kwargs)
        return agreement_row(agreement_id="33333333-3333-4333-8333-333333333333", agreement_version="1.0.0")

    def failed_callback(_row):
        raise RuntimeError("downstream view unavailable")

    monkeypatch.setattr(agreement_widget, "_create_or_update_data_agreement", save)
    controls = _render(monkeypatch)
    controls["fields"]["agreement_name"].value = "Orders Agreement"
    controls["after_save_callbacks"].append(failed_callback)

    controls["save_button"].click_callbacks[0](None)

    assert len(writes) == 1
    assert "Saved Orders Agreement" in controls["status"].value
    assert "post-save callback failed" in controls["status"].value
    assert "Form cleared" in controls["status"].value
    assert controls["fields"]["agreement_name"].value == ""
    assert controls["existing_record"].value == ""


def test_steward_form_uses_simplified_visible_layout(monkeypatch):
    """Compose steward maintenance with one form flow and hidden technical output."""
    controls = _render_steward(monkeypatch)
    text = _visible_text(controls["container"])

    for label in (
        "Data Steward", "Create or update data stewards", "Steward selection",
        "Steward details", "Custom columns",
        "Select or create steward", "Save and clear", "Discard and clear",
    ):
        assert label in text
    for removed in (
        "Data Steward Creation Widget", "Existing data steward",
        "Contact or supporting information", "Save result",
        "Execution log", "Steward name:</b>", "Role:</b>", "Contact:</b>",
        "Steward ID:</b>",
    ):
        assert removed not in text
    assert "Optional" not in text
    assert controls["existing_record_search"].placeholder == "Search stewards..."
    assert controls["save_button"].description == "Save and clear"
    assert controls["discard_button"].description == "Discard and clear"
    assert controls["save_button"].click_callbacks
    assert controls["discard_button"].click_callbacks
    assert controls["container"].layout.kwargs["height"] == "720px"
    assert controls["container"].layout.kwargs["overflow"] == "auto"
    assert "execution_output" not in controls
    assert "execution_log_section" not in controls


def test_steward_discard_and_clear_does_not_write(monkeypatch):
    """Discarding form edits clears them without persisting a steward."""
    writes = []
    monkeypatch.setattr(
        steward_widget,
        "_create_or_update_data_steward",
        lambda **kwargs: writes.append(kwargs),
    )
    controls = _render_steward(monkeypatch)
    controls["fields"]["steward_name"].value = "Unsaved steward"
    controls["fields"]["contact"].value = "unsaved@example.com"
    controls["custom_fields"]["group"].value = "Unsaved group"
    controls["existing_record"].value = "11111111-1111-4111-8111-111111111111"

    controls["discard_button"].click_callbacks[0](None)

    assert writes == []
    assert controls["existing_record"].value == ""
    assert controls["fields"]["steward_name"].value == ""
    assert controls["fields"]["contact"].value == ""
    assert controls["custom_fields"]["group"].value == ""
    assert "discarded" in controls["status"].value.lower()


def test_steward_refresh_failure_after_write_still_clears_form(monkeypatch):
    """A failed list reload must report a saved steward without inviting a duplicate."""
    writes = []

    def save(**kwargs):
        writes.append(kwargs)
        return {"steward_id": "33333333-3333-4333-8333-333333333333", "steward_name": "New Steward"}

    monkeypatch.setattr(steward_widget, "_create_or_update_data_steward", save)
    controls = _render_steward(monkeypatch)
    controls["fields"]["steward_name"].value = "New Steward"
    controls["fields"]["contact"].value = "new@example.com"
    monkeypatch.setattr(
        steward_widget, "list_data_stewards", lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("refresh unavailable"))
    )

    controls["save_button"].click_callbacks[0](None)

    assert len(writes) == 1
    assert "Data steward saved successfully: New Steward" in controls["status"].value
    assert "steward list refresh failed" in controls["status"].value
    assert "Form cleared" in controls["status"].value
    assert controls["fields"]["steward_name"].value == ""
    assert controls["save_button"].disabled is True


def test_steward_additional_information_renders_only_for_custom_fields(monkeypatch):
    """Show the custom field section only when configured."""
    controls = _render_steward(monkeypatch, custom_fields=[])
    text = _visible_text(controls["container"])

    assert "Custom columns" not in text
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
    analytics_label = "Analytics Steward | Governance Reviewer | analytics@example.com"
    assert search.options == [
        "Create new steward",
        "Configured Steward | Data Steward | steward@example.com",
        analytics_label,
    ]
    search.value = analytics_label
    search.callbacks[0]({"name": "value", "new": analytics_label})
    assert controls["existing_record"].value == "22222222-2222-4222-8222-222222222222"

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
    assert "Data steward saved successfully: Analytics Steward. Form cleared." in controls["status"].value
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
    assert "Data steward saved successfully: New Steward. Form cleared." in controls["status"].value
