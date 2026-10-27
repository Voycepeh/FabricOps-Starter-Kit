"""Record-builder contracts for Stage 3 Enrichment."""

from __future__ import annotations

import types
import json

from fabricops_kit.data_contract import shared as contract_shared


def _audit_fields():
    """Return deterministic audit values for record-building tests."""
    return {
        "_committed_by": "user",
        "_committed_at": "2026-08-17T00:00:00",
        "_workspace_id": "workspace-id",
        "_workspace_name": "workspace",
        "_notebook_id": "notebook-id",
        "_notebook_name": "notebook",
        "_metadata_lakehouse_name": "Metadata",
        "_activity_id": "activity",
    }


def test_build_enrichment_records_uses_ids_and_environment(monkeypatch):
    """Build column enrichment with Stage 3 asset IDs and workspace_id."""
    monkeypatch.setattr(contract_shared, "build_runtime_audit_fields", lambda **kwargs: _audit_fields())
    monkeypatch.setattr(contract_shared, "read_lakehouse_table", lambda *args, **kwargs: [{
        "contract_id": "contract-id", "contract_version": 2,
        "contract_payload_json": json.dumps({"table": {"table_id": "table-id", "table_name": "orders", "columns": [{"column_id": "column-id", "column_name": "order_id"}]}}),
    }])
    rows = contract_shared.build_enrichment_records(
        [
            {
                "enrichment_level": "column",
                "contract_id": "contract-id",
                "contract_version": 2,
                "column_id": "column-id",
                "workspace_id": "dev",
                "enrichment_type": "Description",
                "value": "Student identifier",
            }
        ],
        config=types.SimpleNamespace(),
        active_workspace_id="dev",
    )
    assert len(rows) == 1
    row = rows[0]
    assert row["contract_id"] == "contract-id"
    assert row["contract_version"] == 2
    assert row["table_id"] == "table-id"
    assert row["table_name"] == "orders"
    assert row["column_id"] == "column-id"
    assert row["column_name"] == "order_id"
    assert row["workspace_id"] == "dev"
    assert "metadata_key" not in row


def test_table_enrichment_clears_column_id(monkeypatch):
    """Keep table enrichment attached to the table without a column ID."""
    monkeypatch.setattr(contract_shared, "build_runtime_audit_fields", lambda **kwargs: _audit_fields())
    monkeypatch.setattr(contract_shared, "read_lakehouse_table", lambda *args, **kwargs: [{
        "contract_id": "contract-id", "contract_version": 2,
        "contract_payload_json": json.dumps({"table": {"table_id": "table-id", "table_name": "students", "columns": []}}),
    }])
    row = contract_shared.build_enrichment_records(
        [
            {
                "enrichment_level": "table",
                "contract_id": "contract-id",
                "contract_version": 2,
                "column_id": "should-not-persist",
                "enrichment_type": "Description",
                "value": "Student table",
            }
        ],
        config=types.SimpleNamespace(),
        active_workspace_id="dev",
    )[0]
    assert row["column_id"] == ""


def test_column_enrichment_requires_column_id(monkeypatch):
    """Reject column enrichment when the selected Catalogue column ID is missing."""
    monkeypatch.setattr(contract_shared, "build_runtime_audit_fields", lambda **kwargs: _audit_fields())
    try:
        contract_shared.build_enrichment_records(
            [
                {
                    "enrichment_level": "column",
                    "contract_id": "contract-id",
                    "contract_version": 2,
                    "enrichment_type": "Description",
                    "value": "Student identifier",
                }
            ],
            config=types.SimpleNamespace(),
            active_workspace_id="dev",
        )
    except ValueError as exc:
        assert "column_id" in str(exc)
    else:
        raise AssertionError("Expected missing column_id to raise ValueError")
