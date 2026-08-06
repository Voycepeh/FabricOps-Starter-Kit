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


def _widget_with_value_containing(widget, text):
    """Find a visible descendant whose value contains the requested text."""
    if text in str(getattr(widget, "value", "") or ""):
        return widget
    for child in getattr(widget, "children", ()):
        match = _widget_with_value_containing(child, text)
        if match is not None:
            return match
    return None


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


def test_widgets_document_named_normalized_frequency_views():
    """Public owners document the intentional named three-view contract."""
    for widget in (
        fabricops_kit.widget_view_agreement_catalogue,
        fabricops_kit.widget_view_pipeline_catalogue,
        fabricops_kit.widget_view_data_catalogue,
    ):
        source = inspect.getsource(widget)
        assert "display(catalogue" not in source
        assert "display(profile" not in source
        assert 'views["frequency"]' in source
        assert "metadata_column_key`` and ``profiled_at" in source
        assert "get_data_contract_views" not in source


def test_catalogue_views_select_one_snapshot_and_one_frequency_column(monkeypatch, spark_session):
    """Views keep compact parents and normalized children on one exact snapshot."""
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

    old_snapshot = datetime(2026, 7, 30)
    latest_snapshot = datetime(2026, 7, 31)
    later_snapshot = datetime(2026, 8, 1)
    tables = {
        "METADATA_DATA_CATALOGUE": spark_session.createDataFrame(
            [
                ("dataset-key", "fingerprint", "id", "column-id", latest_snapshot),
                ("dataset-key", "previous-fingerprint", "id", "column-id", old_snapshot),
                ("unprofiled-key", "fingerprint-2", "id", "column-id-2", latest_snapshot),
            ],
            "metadata_table_key string, schema_fingerprint string, column_name string, "
            "metadata_column_key string, _committed_at timestamp",
        ),
        "METADATA_DATA_PROFILED": spark_session.createDataFrame(
            [
                ("dataset-key", "fingerprint", "column-a", "Country", old_snapshot, old_snapshot),
                ("dataset-key", "fingerprint", "column-a", "Country", latest_snapshot, latest_snapshot),
                ("dataset-key", "fingerprint", "column-b", "Comment", latest_snapshot, latest_snapshot),
                ("dataset-key", "previous-fingerprint", "column-a", "Country", old_snapshot, old_snapshot),
            ],
            "metadata_table_key string, schema_fingerprint string, metadata_column_key string, "
            "column_name string, profiled_at timestamp, _committed_at timestamp",
        ),
        "METADATA_DATA_PROFILED_FREQUENCY": spark_session.createDataFrame(
            [
                ("column-a", "old", 1, 1, old_snapshot),
                ("column-a", None, 2, 1, latest_snapshot),
                ("column-a", "current", 3, 2, latest_snapshot),
                ("column-a", "future", 4, 1, later_snapshot),
                ("unrelated-column", "other", 5, 1, latest_snapshot),
            ],
            "metadata_column_key string, value string, frequency_count long, "
            "frequency_rank integer, profiled_at timestamp",
        ),
    }
    read_calls = []

    def read_table(table, **_kwargs):
        read_calls.append(table)
        return tables[table]

    monkeypatch.setattr(shared, "read_lakehouse_table_core", read_table)

    state = build_catalogue_widget(
        title="Pipeline Catalogue Viewer",
        description="View data catalogues used by the current pipeline notebook",
        selection_context={"notebook_id": "technical-id", "environment_name": "dev"},
        display_context={"Notebook": "Customer <pipeline>", "Environment": "dev", "Linked datasets": 1},
        inventory_rows=[
            {
                "metadata_table_key": "dataset-key", "schema_fingerprint": "fingerprint",
                "layer": "raw", "schema_name": "sales", "table_name": "orders",
                "_committed_at": latest_snapshot,
            },
            {
                "metadata_table_key": "dataset-key", "schema_fingerprint": "previous-fingerprint",
                "layer": "raw", "schema_name": "sales", "table_name": "orders",
                "_committed_at": old_snapshot,
            },
            {
                "metadata_table_key": "unprofiled-key", "schema_fingerprint": "fingerprint-2",
                "layer": "z_curated", "schema_name": "sales", "table_name": "customers",
                "_committed_at": latest_snapshot,
            },
        ],
        role_options=None, target="metadata", schema=None,
        spark_session=object(), runtime_context={}, empty_message="No inventory.",
    )

    page = displayed[0]
    context_widget = _widget_with_value_containing(page, "<b>Notebook:</b>")
    assert context_widget is not None
    visible_html = context_widget.value
    assert "<b>Notebook:</b> Customer &lt;pipeline&gt;" in visible_html
    assert "Customer <pipeline>" not in visible_html
    assert "<b>Environment:</b> dev" in visible_html
    assert "<b>Linked datasets:</b> 1" in visible_html
    assert "technical-id" not in visible_html
    assert "notebook_id" not in visible_html
    assert "environment_name" not in visible_html
    selection = state["get_selection"]()
    assert selection["notebook_id"] == "technical-id"
    assert selection["metadata_table_key"] == "dataset-key"
    assert selection["profiled_at"] is None
    assert selection["metadata_column_key"] is None
    assert read_calls == []

    views = state["get_views"]()
    assert read_calls == [
        "METADATA_DATA_CATALOGUE",
        "METADATA_DATA_PROFILED",
        "METADATA_DATA_PROFILED_FREQUENCY",
    ]
    assert state["get_selection"]()["profiled_at"] == latest_snapshot
    assert state["get_selection"]()["metadata_column_key"] == "column-a"
    assert set(views) == {"catalogue", "profile", "frequency"}
    assert {row.profiled_at for row in views["profile"].collect()} == {latest_snapshot}
    frequency_rows = views["frequency"].collect()
    assert {row.profiled_at for row in frequency_rows} == {latest_snapshot}
    assert {row.metadata_column_key for row in frequency_rows} == {"column-a"}
    assert {row.value for row in frequency_rows} == {None, "current"}

    state["_controls"]["search"].value = "does not exist"
    assert state["_controls"]["dataset"].value is None
    state["_controls"]["search"].value = ""
    assert state["_controls"]["dataset"].value == "\x1fdataset-key"
    assert len(read_calls) == 3

    selected_details = _widget_with_value_containing(page, "<b>Schema version:</b>")
    assert selected_details is not None
    state["_controls"]["schema_fingerprint"].value = "previous-fingerprint"
    assert "<b>Schema version:</b> previous-fingerprint" in selected_details.value
    state["_controls"]["schema_fingerprint"].value = "fingerprint"
    assert len(read_calls) == 3

    state["_controls"]["metadata_column_key"].value = "column-b"
    assert state["get_selection"]()["metadata_column_key"] == "column-b"
    assert state["get_views"]()["frequency"].count() == 0
    assert len(read_calls) == 3

    state["_controls"]["dataset"].value = "\x1funprofiled-key"
    unprofiled = state["get_views"]()
    assert len(read_calls) == 3
    assert state["get_selection"]()["profiled_at"] is None
    assert unprofiled["profile"].count() == 0
    assert unprofiled["frequency"].count() == 0
    assert unprofiled["profile"].schema == tables["METADATA_DATA_PROFILED"].schema
    assert unprofiled["frequency"].schema == tables["METADATA_DATA_PROFILED_FREQUENCY"].schema
