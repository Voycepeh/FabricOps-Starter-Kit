"""Tests for data-contract view selection helpers."""

from __future__ import annotations

import pytest

import fabricops_kit
from fabricops_kit.widgets import widget_view_data_contract as public_widget
from fabricops_kit.widgets.widget_view_data_contract import (
    _agreement_id_from_context,
    _options,
)
from fabricops_kit.widgets.shared import (
    format_full_value,
    render_expandable_dataframe,
    write_dataframe_download,
)

pytestmark = pytest.mark.unit


ROWS = [
    {"store_type": "lakehouse", "layer": "curated", "schema_name": "sales", "table_name": "orders", "metadata_table_key": "one"},
    {"store_type": "lakehouse", "layer": "raw", "schema_name": "sales", "table_name": "orders", "metadata_table_key": "two"},
    {"store_type": "warehouse", "layer": "curated", "schema_name": "dbo", "table_name": "orders", "metadata_table_key": "three"},
]


def test_dependent_options_follow_canonical_location_hierarchy():
    """Each hierarchy choice constrains the next selector."""
    assert _options(ROWS, "layer", {"store_type": "lakehouse"}) == ["curated", "raw"]
    assert _options(ROWS, "schema_name", {"store_type": "warehouse", "layer": "curated"}) == ["dbo"]


def test_duplicate_table_names_resolve_exact_metadata_identity():
    """A table name alone never determines the registered dataset."""
    assert _options(ROWS, "metadata_table_key", {"store_type": "lakehouse", "layer": "raw", "schema_name": "sales", "table_name": "orders"}) == ["two"]
    assert len(_options(ROWS, "metadata_table_key", {"table_name": "orders"})) == 3


def test_widget_is_publicly_importable_and_old_export_is_removed():
    """Only the intentional Preview rename is exported."""
    assert fabricops_kit.widget_view_data_contract is public_widget
    assert "widget_browse_metadata_catalogue" not in fabricops_kit.__all__
    with pytest.raises(AttributeError):
        getattr(fabricops_kit, "widget_browse_metadata_catalogue")


def test_agreement_context_resolves_records_and_widget_state():
    """Agreement records and agreement-widget selections resolve the same ID."""
    assert _agreement_id_from_context({"agreement_id": "agreement-1"}) == "agreement-1"

    class Selected:
        value = "agreement-2"

    state = {
        "existing_record": Selected(),
        "existing_records_by_id": {"agreement-2": {"agreement_id": "agreement-2"}},
    }
    assert _agreement_id_from_context(state) == "agreement-2"
    assert _agreement_id_from_context(None) == ""


def test_missing_optional_widgets_returns_clear_non_breaking_state(monkeypatch, capsys):
    """Role notebooks remain executable when the optional widget extra is absent."""
    import importlib

    module = importlib.import_module("fabricops_kit.widgets.widget_view_data_contract")
    monkeypatch.setattr(
        module,
        "require_ipywidgets",
        lambda: (_ for _ in ()).throw(ModuleNotFoundError("Install the widget extra.")),
    )
    state = public_widget(metadata_id="dataset-1", schema_version="schema-2")

    assert state["metadata_table_key"] == "dataset-1"
    assert state["schema_fingerprint"] == "schema-2"
    assert "Install the widget extra" in state["error"]
    assert "Data contract viewer unavailable" in capsys.readouterr().out


def test_full_value_formatter_pretty_prints_json_and_preserves_invalid_text():
    """JSON detail is readable while malformed JSON remains inspectable."""
    assert format_full_value('{"values":["Active","Completed"]}') == (  # noqa: S105
        '{\n  "values": [\n    "Active",\n    "Completed"\n  ]\n}'
    )
    assert format_full_value("{invalid json") == "{invalid json"
    assert format_full_value(None) == ""


def test_expandable_viewer_collects_only_bounded_rows_and_retains_full_values(spark_session):
    """The compact preview truncates display only and reports bounded history."""
    pytest.importorskip("ipywidgets")
    long_json = '{"description":"' + ("x" * 100) + '"}'
    dataframe = spark_session.createDataFrame(
        [(1, long_json), (2, '{"status":"ok"}'), (3, "plain text")],
        "record_id int, payload string",
    ).orderBy("record_id")

    viewer = render_expandable_dataframe(
        dataframe, title="History", max_rows=2,
        preview_columns=["record_id", "payload"], expanded_columns=["payload"],
    )

    assert viewer["limited"] is True
    assert len(viewer["rows"]) == 2
    assert viewer["rows"][0]["payload"] == long_json
    assert "additional records are not loaded" in viewer["status"].value
    assert "…" in viewer["preview"].value
    assert viewer["field_selector"].options[0] == "payload"


def test_dataframe_download_writes_complete_source_with_configured_path(monkeypatch):
    """Exports write the source DataFrame rather than the bounded preview rows."""
    calls = []

    class Writer:
        def mode(self, value):
            calls.append(("mode", value))
            return self

        def option(self, key, value):
            calls.append(("option", key, value))
            return self

        def csv(self, path):
            calls.append(("csv", path))

    class DataFrame:
        write = Writer()

        def limit(self, _count):
            raise AssertionError("downloads must not inherit the preview limit")

    monkeypatch.setattr(
        "fabricops_kit.widgets.shared.resolve_configured_file_path",
        lambda target, relative_path, context: (object(), relative_path, f"abfss://metadata/Files/{relative_path}"),
    )

    exported = write_dataframe_download(
        DataFrame(), filename="data contract/id", file_format="csv",
        target="metadata", context={"env": "dev"},
    )

    assert exported["filename"] == "data-contract-id.csv"
    assert exported["relative_path"].startswith("Files/fabricops_exports/")
    assert calls[:2] == [("mode", "overwrite"), ("option", "header", True)]
    assert calls[2][0] == "csv"
