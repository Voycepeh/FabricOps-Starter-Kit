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
    """Profile stores snapshot metrics and asset IDs without a duplicate event timestamp."""
    fields = metadata_table_schema_registry()["METADATA_DATA_PROFILED"].fieldNames()
    assert fields[:19] == [
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
    ]
    assert {
        "profiled_at",
        "metadata_table_key",
        "metadata_column_key",
        "store_type",
        "layer",
        "schema_name",
        "table_name",
        "column_name",
        "schema_fingerprint",
    }.isdisjoint(fields)
    assert "_committed_at" in fields


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
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert {"table_id", "column_id", "environment_name", "metadata_column_key", "profiled_at"}.isdisjoint(fields)


def test_stage2_lineage_schema_uses_pipeline_language():
    """Lineage describes pipeline participation and uses the standard commit timestamp."""
    fields = metadata_table_schema_registry()["METADATA_DATA_LINEAGE"].fieldNames()
    assert fields == [
        "lineage_id",
        "table_id",
        "profile_snapshot_id",
        "environment_name",
        "pipeline_role",
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert {"lineage_event_id", "profile_role", "profiled_at", "recorded_at"}.isdisjoint(fields)
    assert "_committed_at" in fields


def test_stage2_source_observation_schema_is_guardrail_independent():
    """Persist reusable source evidence with the standard commit timestamp only."""
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
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert {
        "observed_at",
        "metadata_table_key",
        "guardrail_rule_version_id",
        "partition_column",
        "change_column",
    }.isdisjoint(fields)
    assert "_committed_at" in fields


def test_guardrail_schema_uses_entity_version_and_results_capture_exact_revision():
    """One Guardrail revision is identified by rule ID plus guardrail_version."""
    registry = metadata_table_schema_registry()
    guardrail = registry["METADATA_GUARDRAIL"].fieldNames()
    results = registry["METADATA_GUARDRAIL_RESULTS"].fieldNames()

    assert guardrail[:2] == ["guardrail_rule_id", "guardrail_version"]
    assert "configuration_version" not in guardrail
    assert results[:3] == ["guardrail_result_id", "guardrail_rule_id", "guardrail_version"]


def test_stage3_enrichment_schema_uses_asset_ids_and_environment():
    """Enrichment stores one table/column value against the Stage 2 asset IDs."""
    fields = metadata_table_schema_registry()["METADATA_ENRICHMENT"].fieldNames()
    assert fields == [
        "enrichment_id",
        "table_id",
        "column_id",
        "environment_name",
        "enrichment_level",
        "enrichment_type",
        "value",
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert {"metadata_id", "metadata_key", "metadata_table_key", "metadata_column_key", "enrichment_name"}.isdisjoint(fields)


def test_stage3_data_access_schema_is_minimal_rls_contract():
    """Data Access stores only the RLS assignment needed for one table/environment."""
    fields = metadata_table_schema_registry()["METADATA_DATA_ACCESS"].fieldNames()
    assert fields == [
        "access_id",
        "user_principal",
        "table_id",
        "environment_name",
        "access_level",
        "access_value",
        "access_state",
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert {
        "role_name",
        "permission",
        "access_purpose",
        "approval_status",
        "access_scope",
        "metadata_table_key",
        "metadata_column_key",
        "granted_date",
        "expires_at",
        "approved_by",
        "approved_at",
        "notes",
    }.isdisjoint(fields)
