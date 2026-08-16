"""Logical relationship contract checks for the normalized metadata model."""

from fabricops_kit.config.metadata_schemas import (
    AUDIT_SCHEMA_FIELDS,
    CANONICAL_METADATA_TABLES,
    METADATA_RELATIONSHIPS,
    metadata_table_schema_registry,
)


def test_all_metadata_tables_share_standard_audit_columns_and_types():
    """All canonical tables retain the shared audit field contract."""
    registry = metadata_table_schema_registry()
    expected = [(name, kind) for name, kind, _nullable in AUDIT_SCHEMA_FIELDS]
    assert len(CANONICAL_METADATA_TABLES) == 13
    for table in CANONICAL_METADATA_TABLES:
        fields = registry[table].fields[-8:]
        actual = [(field.name, type(field.dataType).__name__.replace("Type", "").lower()) for field in fields]
        assert actual == expected


def test_catalogue_is_stable_asset_identity_hub():
    """Catalogue owns one stable identity row per logical asset."""
    fields = metadata_table_schema_registry()["METADATA_DATA_CATALOGUE"].fieldNames()
    assert fields[:12] == [
        "metadata_key", "metadata_level", "metadata_table_key", "metadata_column_key",
        "store_type", "layer", "schema_name", "table_name", "column_name",
        "first_profiled_at", "last_profiled_at", "is_active",
    ]
    assert "schema_fingerprint" not in fields
    assert "environment_name" not in fields
    assert METADATA_RELATIONSHIPS["METADATA_DATA_CATALOGUE"]["primary_key"] == "metadata_key"


def test_downstream_identity_aliases_are_removed():
    """Event and governance tables retain keys instead of physical aliases."""
    registry = metadata_table_schema_registry()
    for table in ("METADATA_DATA_PROFILED", "METADATA_GUARDRAIL_RESULTS"):
        assert not {"dataset_name", "table_name", "column_name"} & set(registry[table].fieldNames())
    observation = set(registry["METADATA_SOURCE_OBSERVATION"].fieldNames())
    assert not {"source_target", "source_schema", "source_table", "partition_column", "change_column"} & observation
    assert {"observation_id", "guardrail_rule_version_id", "metadata_table_key"} <= observation
