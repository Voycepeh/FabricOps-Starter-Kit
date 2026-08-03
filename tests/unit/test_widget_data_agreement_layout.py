"""Structural tests for the reusable agreement form layout."""

from __future__ import annotations

from types import SimpleNamespace
import sys

import pytest

import fabricops_kit.widgets.shared as shared
import fabricops_kit.widgets.widget_render_data_agreement as agreement_widget
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


def test_shared_form_containers_expand_without_scrollbars():
    """Keep reusable page and section containers naturally expanding."""
    section = shared.form_section(_FakeWidgets, title="Details", children=[_FakeWidget()])
    page = shared.form_page(_FakeWidgets, title="Title", description="Description", children=[section])

    for container in (page, section):
        assert container.layout.kwargs["width"] == "100%"
        assert container.layout.kwargs["height"] == "auto"
        assert container.layout.kwargs["overflow"] == "visible"

    grid = shared.form_grid(_FakeWidgets, [_FakeWidget(), _FakeWidget()])
    assert grid.layout.kwargs["grid_template_columns"] == "repeat(auto-fit, minmax(260px, 1fr))"


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


def test_agreement_form_has_meaningful_groups_and_unclipped_output(monkeypatch):
    """Expose meaningful agreement labels and naturally expanding output."""
    controls = _render(monkeypatch)
    text = _visible_text(controls["container"])

    for label in (
        "Approved usage",
        "Provider Data Steward",
        "Recipient Data Steward",
        "Search provider data stewards",
        "Search recipient data stewards",
        "Document name",
        "Document link",
        "Execution log",
    ):
        assert label in text
    assert "Optional" not in text
    assert {key: (box.description, box.value) for key, box in controls["approved_usage_checkboxes"].items()} == {
        "internal": ("Internal", False),
        "research": ("Research", False),
        "external": ("External", False),
    }
    assert controls["save_button"].click_callbacks
    assert controls["existing_record"].callbacks
    assert controls["execution_output"].layout.kwargs["overflow"] == "visible"


def test_save_preserves_emitted_lakehouse_output_and_restores_button(monkeypatch, capsys):
    """Keep complete technical output and restore Save after persistence."""
    message = "Writing Lakehouse table to abfss://container@account.dfs.core.windows.net/path"

    def save(**kwargs):
        print(message)
        return agreement_row(agreement_id="33333333-3333-4333-8333-333333333333")

    monkeypatch.setattr(agreement_widget, "_create_or_update_data_agreement", save)
    controls = _render(monkeypatch)
    controls["approved_usage_checkboxes"]["internal"].value = True
    controls["save_button"].click_callbacks[0](None)

    assert message in capsys.readouterr().out
    assert controls["save_button"].disabled is False
