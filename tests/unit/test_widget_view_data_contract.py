"""Tests for data-contract view selection helpers."""

from __future__ import annotations

import pytest

import fabricops_kit
from fabricops_kit.widgets import widget_view_data_contract as public_widget
from fabricops_kit.widgets.widget_view_data_contract import _options
from fabricops_kit.widgets.shared import format_full_value, render_expandable_dataframe

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
    assert "additional records are not loaded" in viewer["container"].children[1].value
    assert "…" in viewer["container"].children[3].value
    assert viewer["field_selector"].options[0] == "payload"
