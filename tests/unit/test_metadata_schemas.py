"""Focused contracts for immutable Data Contract metadata schemas."""

from __future__ import annotations

import pytest

from fabricops_kit.config.metadata_schemas import (
    CANONICAL_METADATA_TABLES,
    audit_schema_fields,
    metadata_table_schema_registry,
)

pytestmark = pytest.mark.unit


def test_data_contract_uses_snapshot_header_and_membership_schemas():
    """Snapshot schemas contain no abandoned lifecycle columns."""
    registry = metadata_table_schema_registry()
    audit_names = [name for name, _kind, _nullable in audit_schema_fields()]
    header_names = registry["METADATA_DATA_CONTRACT_SNAPSHOT"].fieldNames()
    membership_names = registry["METADATA_DATA_CONTRACT"].fieldNames()

    assert "METADATA_DATA_CONTRACT_SNAPSHOT" in CANONICAL_METADATA_TABLES
    assert header_names == [
        "contract_snapshot_id", "agreement_id", "snapshot_saved_at",
        "linked_dataset_count", *audit_names,
    ]
    assert membership_names == [
        "contract_snapshot_id", "agreement_id", "metadata_table_key",
        "schema_fingerprint", *audit_names,
    ]
    abandoned = {
        "contract_id", "contract_version", "contract_status", "effective_from",
        "effective_to", "contract_payload_json",
    }
    assert abandoned.isdisjoint(header_names)
    assert abandoned.isdisjoint(membership_names)
