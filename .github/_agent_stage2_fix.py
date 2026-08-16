from pathlib import Path


def replace(path_str: str, old: str, new: str) -> None:
    path = Path(path_str)
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise SystemExit(f"Expected text not found in {path}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


RENAME_INTERNAL = {
    "build_table_id": "_build_table_id",
    "build_column_id": "_build_column_id",
    "catalogue_table_identity": "_catalogue_table_identity",
    "guardrail_compatibility_observation": "_guardrail_compatibility_observation",
    "is_source_observation": "_is_source_observation",
    "observation_rows": "_observation_rows",
}
for root in (Path("src"), Path("tests"), Path("scripts")):
    for path in root.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        updated = text
        for old, new in RENAME_INTERNAL.items():
            updated = updated.replace(old, new)
        if updated != text:
            path.write_text(updated, encoding="utf-8")

identity = Path("src/fabricops_kit/config/metadata_identity.py")
text = identity.read_text(encoding="utf-8")
text = text.replace('\n\n__all__ = ["_build_column_id", "_build_table_id"]\n', "\n")
identity.write_text(text, encoding="utf-8")

replace(
    "tests/unit/test_config.py",
    '''    assert catalogue_names == [
        "metadata_table_key",
        "metadata_column_key",
        "schema_fingerprint",
        "environment_name",
        "store_type",
        "layer",
        "schema_name",
        "table_name",
        "column_name",
        "data_type",
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ]
    assert profiling_fields.isdisjoint(catalogue_names)
    assert {"metadata_table_key", "metadata_column_key", "schema_fingerprint", "column_name"}.issubset(catalogue_names)
    assert profiling_fields.issubset(profiled_names)
    assert {"metadata_table_key", "metadata_column_key", "schema_fingerprint", "column_name"}.issubset(profiled_names)
''',
    '''    assert catalogue_names == [
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
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ]
    assert profiling_fields.isdisjoint(catalogue_names)
    assert {"metadata_level", "table_id", "column_id", "column_name", "first_profiled_at", "last_profiled_at", "is_active"}.issubset(catalogue_names)
    assert profiling_fields.issubset(profiled_names)
    assert {"profile_id", "profile_snapshot_id", "table_id", "column_id", "environment_name", "data_type"}.issubset(profiled_names)
''',
)
replace("tests/unit/test_config.py", '    assert catalogue["schema_fingerprint"] == "string"\n', '    assert catalogue["first_profiled_at"] == "timestamp"\n    assert catalogue["last_profiled_at"] == "timestamp"\n    assert catalogue["is_active"] == "boolean"\n')
replace("tests/unit/test_config.py", '            assert timestamp_fields == ["_committed_at"]\n', '            assert timestamp_fields == ["first_profiled_at", "last_profiled_at", "_committed_at"]\n')
replace(
    "tests/unit/test_config.py",
    '''    assert schema.fieldNames() == [
        "lineage_event_id",
        "metadata_table_key",
        "schema_fingerprint",
        "profile_role",
        "profiled_at",
        "environment_name",
        *audit_names,
    ]
''',
    '''    assert schema.fieldNames() == [
        "lineage_id",
        "table_id",
        "profile_snapshot_id",
        "environment_name",
        "pipeline_role",
        "recorded_at",
        *audit_names,
    ]
''',
)
replace("tests/unit/test_dq_rules.py", '    assert {"store_type", "metadata_table_key", "metadata_column_key", "schema_fingerprint"}.issubset(catalogue_fields)\n', '    assert {"metadata_level", "store_type", "table_id", "column_id", "first_profiled_at", "last_profiled_at", "is_active"}.issubset(catalogue_fields)\n')
replace(
    "tests/unit/test_dq_rules.py",
    '''    assert {
        "metadata_column_key",
        "value",
        "frequency_count",
        "frequency_percent",
        "frequency_rank",
        "profiled_row_count",
        "profiled_non_null_count",
        "profiled_at",
    }.issubset(frequency_fields)
''',
    '''    assert {
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
    }.issubset(frequency_fields)
''',
)
replace(
    "tests/unit/test_governance_review_migration.py",
    '''    expected_catalogue_fields = [
        "metadata_table_key",
        "metadata_column_key",
        "schema_fingerprint",
        "environment_name",
        "store_type",
        "layer",
        "schema_name",
        "table_name",
        "column_name",
        "data_type",
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ]
''',
    '''    expected_catalogue_fields = [
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
        "_committed_by",
        "_committed_at",
        "_workspace_id",
        "_workspace_name",
        "_notebook_id",
        "_notebook_name",
        "_metadata_lakehouse_name",
        "_activity_id",
    ]
''',
)
replace("tests/unit/test_governance_review_migration.py", '    assert "metadata_table_key" in schemas["METADATA_DATA_PROFILED"].fieldNames()\n', '    assert {"profile_id", "profile_snapshot_id", "table_id", "column_id"}.issubset(schemas["METADATA_DATA_PROFILED"].fieldNames())\n')
