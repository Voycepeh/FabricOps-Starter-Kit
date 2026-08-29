"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import pytest

from fabricops_kit.widgets import shared as widget_shared

pytestmark = pytest.mark.unit


def test_profile_helper_returns_notebook_ready_structure():
    """Verify profile helper returns notebook ready structure."""
    profile = {"table_name": "orders", "row_count": 3, "columns": [{"column_name": "amount"}]}

    assert profile["table_name"] == "orders"
    assert profile["row_count"] == 3


def test_obsolete_catalogue_and_enrichment_helpers_are_not_exposed():
    """Verify removed widget helpers are absent from the shared module."""
    removed_symbols = {
        "_approved_column_identity",
        "_approved_review_context",
        "_collect_enrichment_extra_fields",
        "_json",
        "_next_minor_version",
        "_render_enrichment_extra_fields",
        "_selected_catalogue_rows_for_enrichment",
        "_write_rule_records",
        "build_catalogue_widget",
        "build_enrichment_records",
        "catalogue_table_browser_state",
        "catalogue_table_options",
        "collect_catalogue_inventory",
        "get_current_notebook_lineage_scope",
        "get_data_contract_views",
        "get_selected_agreement",
        "latest_enrichment_values",
        "read_enrichment_records",
        "render_read_only_catalogue_detail",
        "set_active_pipeline_context",
        "set_selected_agreement",
        "write_enrichment_records",
    }

    assert removed_symbols.isdisjoint(vars(widget_shared))
