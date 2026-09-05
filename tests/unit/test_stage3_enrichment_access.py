"""Focused Stage 3 contracts for Enrichment and Data Access."""

from __future__ import annotations

from fabricops_kit.widgets import enrichment_shared


def test_latest_enrichment_is_environment_specific():
    """Keep Development and Production enrichment values independent."""
    rows = [
        {"enrichment_id": "dev-old", "contract_id": "contract-1", "contract_version": 1, "column_id": "column-1", "environment_name": "dev", "enrichment_level": "column", "enrichment_type": "Description", "value": "Old", "_committed_at": "2026-01-01", "_activity_id": "a"},
        {"enrichment_id": "dev-new", "contract_id": "contract-1", "contract_version": 1, "column_id": "column-1", "environment_name": "dev", "enrichment_level": "column", "enrichment_type": "Description", "value": "Development", "_committed_at": "2026-02-01", "_activity_id": "b"},
        {"enrichment_id": "prod", "contract_id": "contract-1", "contract_version": 1, "column_id": "column-1", "environment_name": "prod", "enrichment_level": "column", "enrichment_type": "Description", "value": "Production", "_committed_at": "2026-03-01", "_activity_id": "c"},
    ]
    latest = enrichment_shared.latest_enrichment_values(rows, environment_name="dev")
    assert latest[("column", "contract-1", 1, "column-1", "Description")]["value"] == "Development"


def test_catalogue_table_options_are_environment_specific():
    """Keep environment rows separate while retaining the shared logical table ID."""
    rows = [
        {"metadata_level": "table", "table_id": "shared-id", "column_id": "", "environment_name": "dev", "table_name": "Orders", "layer": "Development", "schema_name": "dbo", "is_active": True, "last_profiled_at": "2026-01-01"},
        {"metadata_level": "table", "table_id": "shared-id", "column_id": "", "environment_name": "prod", "table_name": "Orders", "layer": "Production", "schema_name": "dbo", "is_active": True, "last_profiled_at": "2026-01-01"},
    ]
    dev = enrichment_shared.catalogue_table_options(rows, environment_name="dev")
    prod = enrichment_shared.catalogue_table_options(rows, environment_name="prod")
    assert [row["table_id"] for row in dev] == ["shared-id"]
    assert [row["table_id"] for row in prod] == ["shared-id"]
    assert dev[0]["label"] != prod[0]["label"]
