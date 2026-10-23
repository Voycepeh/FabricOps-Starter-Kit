"""Focused contracts for FabricOps metadata schemas."""

from __future__ import annotations

import pytest

from fabricops_kit.config.metadata_schemas import (
    CANONICAL_METADATA_TABLES,
    GOVERNANCE_METADATA_TABLES,
    ENGINEERING_METADATA_TABLES,
    audit_schema_fields,
    metadata_table_owner,
    metadata_table_physical_schema,
    metadata_table_schema_registry,
)

pytestmark = pytest.mark.unit


def test_canonical_tables_have_one_authoritative_writer_class():
    """Every canonical table belongs to exactly one ownership class."""
    expected_owners = {
        "METADATA_DATA_STEWARD": "governance",
        "METADATA_DATA_AGREEMENT": "governance",
        "METADATA_DATA_CONTRACT": "governance",
        "METADATA_ACTIVATION_STATE": "governance",
        "METADATA_WORKSPACE_REGISTRY": "governance",
        "METADATA_EXECUTION_STATE": "engineering",
        "METADATA_TABLE_PROFILING": "engineering",
        "METADATA_DATA_CATALOGUE": "engineering",
        "METADATA_DATA_PROFILED": "engineering",
        "METADATA_DATA_PROFILED_FREQUENCY": "engineering",
        "METADATA_DATA_LINEAGE": "engineering",
        "METADATA_DATA_ACCESS": "engineering",
        "METADATA_GUARDRAIL_RESULTS": "engineering",
        "METADATA_PIPELINE_RUN": "engineering",
        "METADATA_SOURCE_OBSERVATION": "engineering",
    }
    assert set(GOVERNANCE_METADATA_TABLES).isdisjoint(ENGINEERING_METADATA_TABLES)
    assert set(GOVERNANCE_METADATA_TABLES) | set(ENGINEERING_METADATA_TABLES) == set(CANONICAL_METADATA_TABLES)
    assert {table: metadata_table_owner(table) for table in CANONICAL_METADATA_TABLES} == expected_owners


def test_physical_schema_resolution_uses_framework_ownership_config():
    """Callers resolve schemas by canonical table name rather than literals."""
    class Config:
        governance_metadata_schema = "approved"
        engineering_metadata_schema = "observed"

    assert metadata_table_physical_schema(Config(), "METADATA_DATA_CONTRACT") == "approved"
    assert metadata_table_physical_schema(Config(), "METADATA_SOURCE_OBSERVATION") == "observed"


def test_data_contract_uses_versioned_one_table_schema():
    """Contract rows freeze one table definition under one Agreement version."""
    registry = metadata_table_schema_registry()
    audit_names = [name for name, _kind, _nullable in audit_schema_fields()]
    schema = registry["METADATA_DATA_CONTRACT"]

    assert "METADATA_DATA_CONTRACT_SNAPSHOT" not in CANONICAL_METADATA_TABLES
    assert schema.fieldNames() == [
        "contract_id", "contract_version",
        "table_id", "table_name", "environment_name", "contract_payload_json", "status", *audit_names,
    ]
    assert "provider_steward_name" in metadata_table_schema_registry()["METADATA_DATA_AGREEMENT"].fieldNames()
    assert "recipient_steward_name" in metadata_table_schema_registry()["METADATA_DATA_AGREEMENT"].fieldNames()
    assert {"metadata_table_key", "schema_fingerprint", "approved_usage_json"}.isdisjoint(schema.fieldNames())
    assert [(field.name, type(field.dataType).__name__, field.nullable) for field in schema.fields[:7]] == [
        ("contract_id", "StringType", False), ("contract_version", "IntegerType", False),
        ("table_id", "StringType", False), ("table_name", "StringType", True),
        ("environment_name", "StringType", False),
        ("contract_payload_json", "StringType", True),
        ("status", "StringType", False),
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
        "data_type",
        "load_strategy",
        "load_strategy_parameters_json",
        "writer_workspace_id",
        "writer_notebook_id",
        "writer_notebook_name",
        "scheduled_refresh_json",
        "profile_key_candidates_json",
        "first_profiled_at",
        "last_profiled_at",
        "is_active",
        "execution_workspace_id", "_legacy_environment_name",
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert {"metadata_id", "metadata_key", "metadata_table_key", "metadata_column_key"}.isdisjoint(fields)


def test_stage2_profile_schema_is_normalized():
    """Profile stores snapshot metrics and asset IDs without a duplicate event timestamp."""
    fields = metadata_table_schema_registry()["METADATA_DATA_PROFILED"].fieldNames()
    assert fields[:21] == [
        "profile_id",
        "profile_snapshot_id",
        "table_id",
        "column_id",
        "environment_name",
        "data_type",
        "table_name",
        "column_name",
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
        "table_id",
        "column_id",
        "table_name",
        "column_name",
        "data_type",
        "environment_name",
        "value",
        "frequency_count",
        "frequency_percent",
        "frequency_rank",
        "profiled_row_count",
        "profiled_non_null_count",
        "execution_workspace_id", "_legacy_environment_name",
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert {"metadata_column_key", "profiled_at"}.isdisjoint(fields)


def test_stage2_lineage_schema_uses_pipeline_language():
    """Lineage describes pipeline participation and uses the standard commit timestamp."""
    fields = metadata_table_schema_registry()["METADATA_DATA_LINEAGE"].fieldNames()
    assert fields == [
        "lineage_id",
        "table_id",
        "table_name",
        "environment_name",
        "pipeline_role",
        "execution_workspace_id", "_legacy_environment_name",
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert {"lineage_event_id", "profile_role", "profiled_at", "recorded_at"}.isdisjoint(fields)
    assert "_committed_at" in fields


def test_stage2_source_observation_schema_is_guardrail_independent():
    """Persist reusable source evidence with the standard commit timestamp only."""
    fields = metadata_table_schema_registry()["METADATA_SOURCE_OBSERVATION"].fieldNames()
    assert fields == [
        "observation_id",
        "run_id",
        "source_table_id",
        "source_table_name",
        "target_table_id",
        "target_table_name",
        "environment_name",
        "partition_value",
        "row_count",
        "min_change_value",
        "max_change_value",
        "content_fingerprint",
        "is_present",
        "observation_status",
        "publication_payload_json",
        "execution_workspace_id", "_legacy_environment_name",
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    assert {
        "observed_at",
        "metadata_table_key",
        "guardrail_rule_version_id",
        "partition_column",
        "change_column",
    }.isdisjoint(fields)


def test_source_consumption_is_not_a_separate_metadata_table():
    """Source Observation owns both observed and committed states."""
    assert "METADATA_SOURCE_CONSUMPTION" not in metadata_table_schema_registry()






def test_stage3_data_access_schema_records_observed_sql_permissions():
    """Data Access stores one observed SQL permission for a registered table snapshot."""
    schema = metadata_table_schema_registry()["METADATA_DATA_ACCESS"]
    fields = schema.fieldNames()
    assert fields == [
        "access_id",
        "user_principal",
        "table_id",
        "table_name",
        "environment_name",
        "access_level",
        "access_value",
        "access_state",
        "access_snapshot_id",
        "user_type",
        "role_name",
        "permission_source",
        "database_name",
        "schema_name",
        "object_name",
        "object_type",
        "execution_workspace_id", "_legacy_environment_name",
        *[name for name, _kind, _nullable in audit_schema_fields()],
    ]
    field_by_name = {field.name: field for field in schema.fields}
    assert all(
        not field_by_name[name].nullable
        for name in {
            "access_id",
            "user_principal",
            "table_id",
            "environment_name",
            "access_level",
            "access_value",
            "access_state",
            "access_snapshot_id",
            "user_type",
            "permission_source",
            "database_name",
        }
    )
    assert all(field_by_name[name].nullable for name in {"role_name", "schema_name", "object_name", "object_type"})
    assert {
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


def test_definition_tables_are_retired_but_results_remain():
    """Setup owns contract payloads and execution results, with no side definitions."""
    registry = metadata_table_schema_registry()
    for table in ("METADATA_ENRICHMENT", "METADATA_GUARDRAIL"):
        assert table not in registry
        assert table not in CANONICAL_METADATA_TABLES
        with pytest.raises(ValueError, match="Unknown canonical"):
            metadata_table_owner(table)
    results = registry["METADATA_GUARDRAIL_RESULTS"].fieldNames()
    assert results[:3] == ["guardrail_result_id", "guardrail_rule_id", "guardrail_version"]
    assert {"contract_id", "contract_version", "result_payload_json"} <= set(results)
