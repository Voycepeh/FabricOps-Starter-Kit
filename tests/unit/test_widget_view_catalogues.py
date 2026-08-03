"""Tests for the scoped catalogue widgets and their shared contract."""

from __future__ import annotations

from datetime import datetime
import inspect
import sys
import types

import pytest

import fabricops_kit
from fabricops_kit.widgets.shared import build_catalogue_widget, dataset_label, schema_version_options

pytestmark = pytest.mark.unit


def test_public_catalogue_widgets_replace_catch_all():
    """The three scoped widgets replace the removed catch-all export."""
    assert callable(fabricops_kit.widget_view_agreement_catalogue)
    assert callable(fabricops_kit.widget_view_pipeline_catalogue)
    assert callable(fabricops_kit.widget_view_data_catalogue)
    assert "widget_view_data_contract" not in fabricops_kit.__all__
    with pytest.raises(AttributeError):
        getattr(fabricops_kit, "widget_view_data_contract")


def test_dataset_labels_are_consistent_and_pipeline_roles_are_explicit():
    """Shared labels are consistent and make lineage roles explicit."""
    row = {"layer": "raw", "schema_name": "sales", "table_name": "orders", "metadata_table_key": "key"}
    assert dataset_label(row) == "raw / sales / orders"
    assert dataset_label(row, "Source") == "[Source] raw / sales / orders"
    assert dataset_label(row, "Target") == "[Target] raw / sales / orders"


def test_schema_versions_are_deduplicated_and_latest_is_deterministic():
    """Schema choices deduplicate column observations and choose the latest."""
    rows = [
        {"metadata_table_key": "key", "schema_fingerprint": "old", "_committed_at": datetime(2026, 1, 1)},
        {"metadata_table_key": "key", "schema_fingerprint": "new", "_committed_at": datetime(2026, 2, 1)},
        {"metadata_table_key": "key", "schema_fingerprint": "new", "_committed_at": datetime(2026, 2, 1)},
    ]
    options = schema_version_options(rows, "key")
    assert [value for _label, value in options] == ["new", "old"]
    assert options[0][0].startswith("Latest")


def test_widgets_do_not_render_spark_dataframes_or_return_ten_table_mapping():
    """Public owners delegate selection and never render Spark frames."""
    for widget in (
        fabricops_kit.widget_view_agreement_catalogue,
        fabricops_kit.widget_view_pipeline_catalogue,
        fabricops_kit.widget_view_data_catalogue,
    ):
        source = inspect.getsource(widget)
        assert "display(catalogue" not in source
        assert "display(profile" not in source
        assert "get_data_contract_views" not in source


@pytest.mark.parametrize(
    ("widget", "title", "subtitle", "empty_message"),
    [
        (
            fabricops_kit.widget_view_agreement_catalogue,
            "Agreement Catalogue Viewer",
            "View data catalogues linked to the selected data agreement",
            "This agreement has no linked catalogue inventory.",
        ),
        (
            fabricops_kit.widget_view_pipeline_catalogue,
            "Pipeline Catalogue Viewer",
            "View data catalogues used by the current pipeline notebook",
            "No lineage catalogue inventory was found for this notebook.",
        ),
        (
            fabricops_kit.widget_view_data_catalogue,
            "Data Catalogue Viewer",
            "Browse data catalogues available in the current environment",
            "The data catalogue has no datasets in the current environment.",
        ),
    ],
)
def test_catalogue_viewers_supply_exact_shared_layout_copy(widget, title, subtitle, empty_message):
    """Each owner supplies its viewer-specific copy to the common builder."""
    source = inspect.getsource(widget)
    assert "return build_catalogue_widget(" in source
    assert f'title="{title}"' in source
    assert f'description="{subtitle}"' in source
    assert f'empty_message="{empty_message}"' in source


def test_internal_selection_context_is_not_rendered(monkeypatch):
    """Technical selection identifiers remain available without appearing in UI context."""
    import fabricops_kit.widgets.shared as shared
    from tests.unit.test_widget_register_data_contract import _FakeWidgets

    _FakeWidgets.Dropdown = _FakeWidgets.Select

    class FakeHTML(_FakeWidgets.HTML):
        """Capture positional HTML content like ipywidgets.HTML."""

        def __init__(self, value="", **kwargs):
            super().__init__(value=value, **kwargs)

    _FakeWidgets.HTML = FakeHTML
    displayed = []
    fake_display = types.ModuleType("IPython.display")
    fake_display.display = displayed.append
    fake_ipython = types.ModuleType("IPython")
    fake_ipython.display = fake_display
    monkeypatch.setitem(sys.modules, "IPython", fake_ipython)
    monkeypatch.setitem(sys.modules, "IPython.display", fake_display)
    monkeypatch.setattr(shared, "require_ipywidgets", lambda: _FakeWidgets)

    state = build_catalogue_widget(
        title="Pipeline Catalogue Viewer",
        description="View data catalogues used by the current pipeline notebook",
        selection_context={"notebook_id": "technical-id", "environment_name": "dev"},
        display_context={"Notebook": "Customer <pipeline>", "Environment": "dev", "Linked datasets": 1},
        inventory_rows=[{
            "metadata_table_key": "dataset-key", "schema_fingerprint": "fingerprint",
            "layer": "raw", "schema_name": "sales", "table_name": "orders",
            "_committed_at": datetime(2026, 7, 31),
        }],
        role_options=[("Source", "dataset-key")], target="metadata", schema=None,
        spark_session=object(), runtime_context={}, empty_message="No inventory.",
    )

    page = displayed[0]
    header, context_section, selection_section, selected_section = page.children
    visible_html = context_section.children[1].value
    assert "Pipeline Catalogue Viewer" in header.value
    assert "View data catalogues used by the current pipeline notebook" in header.value
    assert "background:#0f6cbd" in header.value
    assert [section.children[0].value for section in page.children[1:]] == [
        '<div style="color:#0f548c;font-size:16px;font-weight:600;border-bottom:1px solid #d7e7f5;padding:0 0 6px 0;">Context</div>',
        '<div style="color:#0f548c;font-size:16px;font-weight:600;border-bottom:1px solid #d7e7f5;padding:0 0 6px 0;">Catalogue selection</div>',
        '<div style="color:#0f548c;font-size:16px;font-weight:600;border-bottom:1px solid #d7e7f5;padding:0 0 6px 0;">Selected catalogue</div>',
    ]
    for widget in (page, header, context_section, selection_section, selected_section):
        assert widget.layout.kwargs["width"] == "100%"
        assert widget.layout.kwargs["height"] == "auto"
        assert widget.layout.kwargs["overflow"] == "visible"
    assert state["_controls"]["search"].description == "Search"
    for control in state["_controls"].values():
        assert control.layout.kwargs == {"width": "100%", "height": "auto", "overflow": "visible"}
    assert "Save" not in repr(page.children)
    assert "Execution log" not in repr(page.children)
    assert "<b>Notebook:</b> Customer &lt;pipeline&gt;" in visible_html
    assert "Customer <pipeline>" not in visible_html
    assert "<b>Environment:</b> dev" in visible_html
    assert "<b>Linked datasets:</b> 1" in visible_html
    assert "technical-id" not in visible_html
    assert "notebook_id" not in visible_html
    assert "environment_name" not in visible_html
    assert state["get_selection"]()["notebook_id"] == "technical-id"
