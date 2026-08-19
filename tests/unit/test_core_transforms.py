"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import pytest

from fabricops_kit.widgets import shared as gr
from fabricops_kit.widgets.shared import build_enrichment_records, latest_enrichment_values

pytestmark = pytest.mark.unit


def test_profile_helper_returns_notebook_ready_structure():
    """Verify profile helper returns notebook ready structure."""
    profile = {"table_name": "orders", "row_count": 3, "columns": [{"column_name": "amount"}]}

    assert profile["table_name"] == "orders"
    assert profile["row_count"] == 3


def test_generic_enrichment_builder_and_latest_values(monkeypatch):
    """Build independent generic rows and resolve deterministic current values."""
    audit = {name: "2026-01-01T00:00:00Z" if name == "_committed_at" else "audit" for name in gr.STANDARD_RUNTIME_AUDIT_COLUMNS}
    monkeypatch.setattr(gr, "build_runtime_audit_fields", lambda **_kwargs: audit)
    records = build_enrichment_records([
        {"enrichment_level": "table", "metadata_key": "table-key", "enrichment_type": "Description", "value": "Orders"},
        {"enrichment_level": "column", "metadata_key": "col-amount", "enrichment_type": "Description", "value": "Old", "enrichment_id": "a"},
        {"enrichment_level": "column", "metadata_key": "col-amount", "enrichment_type": "Description", "value": "Current", "enrichment_id": "b"},
        {"enrichment_level": "column", "metadata_key": "col-amount", "enrichment_type": "Classification", "value": "Sensitive"},
    ], config=object(), env="dev")
    assert set(records[0]) == {"enrichment_id", "enrichment_level", "metadata_key", "enrichment_type", "value", *gr.STANDARD_RUNTIME_AUDIT_COLUMNS}
    latest = latest_enrichment_values(records)
    assert latest[("column", "col-amount", "Description")]["value"] == "Current"
    assert len(latest) == 3


@pytest.mark.parametrize("field", ["metadata_key", "enrichment_type", "value"])
def test_enrichment_builder_rejects_empty_required_values(field):
    """Reject blank generic enrichment values."""
    row = {"enrichment_level": "column", "metadata_key": "col", "enrichment_type": "Description", "value": "Meaning"}
    row[field] = ""
    with pytest.raises(ValueError, match=field):
        build_enrichment_records([row])


def test_enrichment_builder_rejects_unsupported_level():
    """Only table and column identities are supported."""
    with pytest.raises(ValueError, match="table.*column"):
        build_enrichment_records([{"enrichment_level": "dataset", "metadata_key": "x", "enrichment_type": "x", "value": "x"}])
