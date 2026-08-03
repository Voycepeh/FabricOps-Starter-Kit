"""Focused contracts for immutable Data Contract metadata schemas."""

from __future__ import annotations

import pytest

from fabricops_kit.config.metadata_schemas import (
    CANONICAL_METADATA_TABLES,
    audit_schema_fields,
    metadata_table_schema_registry,
)

pytestmark = pytest.mark.unit


def test_data_contract_uses_one_snapshot_membership_schema():
    """One snapshot table contains timestamped memberships without lifecycle columns."""
    registry = metadata_table_schema_registry()
    audit_names = [name for name, _kind, _nullable in audit_schema_fields()]
    membership_names = registry["METADATA_DATA_CONTRACT"].fieldNames()

    assert "METADATA_DATA_CONTRACT_SNAPSHOT" not in CANONICAL_METADATA_TABLES
    assert "METADATA_DATA_CONTRACT_SNAPSHOT" not in registry
    assert membership_names == [
        "agreement_id", "metadata_table_key", "schema_fingerprint", *audit_names,
    ]
    abandoned = {
        "contract_id", "contract_version", "contract_status", "effective_from",
        "effective_to", "contract_payload_json", "contract_snapshot_id",
        "snapshot_saved_at",
    }
    assert abandoned.isdisjoint(membership_names)


def test_profiled_frequency_schema_is_normalized_and_ordered():
    """Verify the breaking normalized profile frequency metadata contract."""
    from fabricops_kit.config.metadata_schemas import (
        AUDIT_SCHEMA_FIELDS,
        CANONICAL_METADATA_TABLES,
        metadata_table_schema_registry,
    )

    registry = metadata_table_schema_registry()
    profiled_index = CANONICAL_METADATA_TABLES.index("METADATA_DATA_PROFILED")
    assert CANONICAL_METADATA_TABLES[profiled_index + 1] == "METADATA_DATA_PROFILED_FREQUENCY"
    assert "frequency_json" not in registry["METADATA_DATA_PROFILED"].fieldNames()
    schema = registry["METADATA_DATA_PROFILED_FREQUENCY"]
    expected = [
        ("metadata_column_key", "StringType", False),
        ("value", "StringType", True),
        ("frequency_count", "LongType", False),
        ("frequency_percent", "DoubleType", False),
        ("frequency_rank", "IntegerType", False),
        ("profiled_row_count", "LongType", False),
        ("profiled_non_null_count", "LongType", False),
        ("profiled_at", "TimestampType", False),
        *[(name, f"{kind.title()}Type" if kind != "integer" else "IntegerType", nullable) for name, kind, nullable in AUDIT_SCHEMA_FIELDS],
    ]
    assert [(field.name, type(field.dataType).__name__, field.nullable) for field in schema.fields] == expected
