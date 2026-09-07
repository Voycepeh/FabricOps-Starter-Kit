"""Record-builder contracts for Stage 3 Enrichment."""

from __future__ import annotations

import types

from fabricops_kit.widgets import enrichment_shared


def _audit_fields():
    """Return deterministic audit values for record-building tests."""
    return {
        "_committed_by": "user",
        "_committed_at": "2026-08-17T00:00:00",
        "_workspace_id": "workspace-id",
        "_workspace_name": "workspace",
        "_notebook_id": "notebook-id",
        "_notebook_name": "notebook",
        "_metadata_lakehouse_name": "metadata",
        "_activity_id": "activity",
    }


def test_build_enrichment_records_uses_ids_and_environment(monkeypatch):
    """Build column enrichment with Stage 3 asset IDs and environment."""
    monkeypatch.setattr(enrichment_shared, "build_runtime_audit_fields", lambda **kwargs: _audit_fields())
    rows = enrichment_shared.build_enrichment_records(
        [
            {
                "enrichment_level": "column",
                "contract_id": "contract-id",
                "contract_version": 2,
                "column_id": "column-id",
                "environment_name": "dev",
                "enrichment_type": "Description",
                "value": "Student identifier",
            }
        ],
        config=types.SimpleNamespace(),
        env="dev",
    )
    assert len(rows) == 1
    row = rows[0]
    assert row["contract_id"] == "contract-id"
    assert row["contract_version"] == 2
    assert "table_id" not in row
    assert row["column_id"] == "column-id"
    assert row["environment_name"] == "dev"
    assert "metadata_key" not in row


def test_table_enrichment_clears_column_id(monkeypatch):
    """Keep table enrichment attached to the table without a column ID."""
    monkeypatch.setattr(enrichment_shared, "build_runtime_audit_fields", lambda **kwargs: _audit_fields())
    row = enrichment_shared.build_enrichment_records(
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
        env="dev",
    )[0]
    assert row["column_id"] == ""


def test_column_enrichment_requires_column_id(monkeypatch):
    """Reject column enrichment when the selected Catalogue column ID is missing."""
    monkeypatch.setattr(enrichment_shared, "build_runtime_audit_fields", lambda **kwargs: _audit_fields())
    try:
        enrichment_shared.build_enrichment_records(
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
            env="dev",
        )
    except ValueError as exc:
        assert "column_id" in str(exc)
    else:
        raise AssertionError("Expected missing column_id to raise ValueError")
