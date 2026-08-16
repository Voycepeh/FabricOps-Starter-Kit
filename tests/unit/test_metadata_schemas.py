"""Focused contracts for FabricOps metadata schemas."""

from __future__ import annotations

import pytest

from fabricops_kit.config.metadata_schemas import (
    CANONICAL_METADATA_TABLES,
    audit_schema_fields,
    metadata_table_schema_registry,
)

pytestmark = pytest.mark.unit


def test_data_contract_uses_one_snapshot_membership_schema():
    """Keep the current Data Contract contract unchanged until Stage 5."""
    registry = metadata_table_schema_registry()
    audit_names = [name for name, _kind, _nullable in audit_schema_fields()]
    membership_names = registry["METADATA_DATA_CONTRACT"].fieldNames()

    assert "METADATA_DATA_CONTRACT_SNAPSHOT" not in CANONICAL_METADATA_TABLES
    assert "METADATA_DATA_CONTRACT_SNAPSHOT" not in registry
    assert membership_names == [
        "agreement_id", "metadata_table_key", "schema_fingerprint", "approved_usage_json", *audit_names,
    ]


def test_stage2_catalogue_schema_uses_environment_aware_asset_ids():
    """Catalogue owns the physical table/column identity for one environment."""
    fields = metadata_table_schema_registry()["METADATA_DATA_CATALOGUE"].fieldNames()
    assert fields == [
        "metadata_level",
        "table_id",
        "column_id",
        "environment_name",
        "store_type",
        "layer",
        "schema_name",
        "table_name",
        "column_name",
        "first_profiled_at",
        "last_profiled_at",
        "is_active",
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert {"metadata_id", "metadata_key", "metadata_table_key", "metadata_column_key"}.isdisjoint(fields)


def test_stage2_profile_schema_is_normalized():
    """Profile stores snapshot metrics and asset IDs without repeated physical names."""
    fields = metadata_table_schema_registry()["METADATA_DATA_PROFILED"].fieldNames()
    assert fields[:20] == [
        "profile_id",
        "profile_snapshot_id",
        "table_id",
        "column_id",
        "environment_name",
        "data_type",
        "row_count",
        "non_null_count",
        "null_count",
        "null_percent",
        "distinct_count",
        "distinct_percent",
        "mean_value",
        "stddev_value",
        "min_value",
        "percentile_25_value",
        "median_value",
        "percentile_75_value",
        "max_value",
        "profiled_at",
    ]
    assert {
        "metadata_table_key",
        "metadata_column_key",
        "store_type",
        "layer",
        "schema_name",
        "table_name",
        "column_name",
        "schema_fingerprint",
    }.isdisjoint(fields)


def test_profiled_frequency_schema_is_flattened_detail_for_profile():
    """Frequency stores flattened distribution rows linked through profile_id."""
    registry = metadata_table_schema_registry()
    profiled_index = CANONICAL_METADATA_TABLES.index("METADATA_DATA_PROFILED")
    assert CANONICAL_METADATA_TABLES[profiled_index + 1] == "METADATA_DATA_PROFILED_FREQUENCY"
    assert "frequency_json" not in registry["METADATA_DATA_PROFILED"].fieldNames()
    fields = registry["METADATA_DATA_PROFILED_FREQUENCY"].fieldNames()
    assert fields == [
        "frequency_id",
        "profile_id",
        "profile_snapshot_id",
        "value",
        "frequency_count",
        "frequency_percent",
        "frequency_rank",
        "profiled_row_count",
        "profiled_non_null_count",
        "profiled_at",
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert {"table_id", "column_id", "environment_name", "metadata_column_key"}.isdisjoint(fields)


def test_stage2_lineage_schema_uses_pipeline_language():
    """Lineage describes pipeline participation rather than a profiling role."""
    fields = metadata_table_schema_registry()["METADATA_DATA_LINEAGE"].fieldNames()
    assert fields == [
        "lineage_id",
        "table_id",
        "profile_snapshot_id",
        "environment_name",
        "pipeline_role",
        "recorded_at",
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert {"lineage_event_id", "profile_role", "profiled_at"}.isdisjoint(fields)


def test_stage2_source_observation_schema_is_guardrail_independent():
    """Persist reusable source evidence without Guardrail-owned identity."""
    fields = metadata_table_schema_registry()["METADATA_SOURCE_OBSERVATION"].fieldNames()
    assert fields == [
        "observation_id",
        "table_id",
        "environment_name",
        "partition_value",
        "row_count",
        "min_change_value",
        "max_change_value",
        "is_present",
        "observed_at",
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert {"metadata_table_key", "guardrail_rule_version_id", "partition_column", "change_column"}.isdisjoint(fields)


def test_enrichment_schema_is_unchanged_until_stage3():
    """Do not pull the Enrichment migration into Stage 2."""
    schema = metadata_table_schema_registry()["METADATA_ENRICHMENT"]
    expected_names = [
        "enrichment_id", "enrichment_level", "metadata_key", "enrichment_type", "value",
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert schema.fieldNames() == expected_names
