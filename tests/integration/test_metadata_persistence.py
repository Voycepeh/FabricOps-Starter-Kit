"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import pytest

from fabricops_kit.config import setup_metadata_tables
from tests.helpers import framework_config

pytestmark = pytest.mark.integration


def test_central_metadata_setup_preserves_existing_valid_tables(monkeypatch):
    """Verify central metadata setup preserves existing valid tables."""
    import fabricops_kit.config as config_module

    class Schema:
        def __init__(self, fields):
            self._fields = list(fields)

        def fieldNames(self):  # noqa: N802 - mirrors Spark API
            return list(self._fields)

    schemas = {
        "METADATA_DATA_STEWARD": Schema(["steward_id", "is_active"]),
        "METADATA_DATA_AGREEMENT": Schema(["agreement_id"]),
        "METADATA_DATA_AGREEMENT_EVIDENCE": Schema(["agreement_id", "file_path"]),
        "METADATA_NOTEBOOK_REGISTRY": Schema(["agreement_id", "registration_id"]),
        "METADATA_GUARDRAIL_RULES": Schema(["rule_id"]),
    }
    checked_paths = []
    writes = []

    monkeypatch.setattr(config_module, "_metadata_table_definitions", lambda config: schemas)
    monkeypatch.setattr(config_module, "_existing_table_columns", lambda spark, path: checked_paths.append(path) or schemas[path.rsplit('/', 1)[-1]].fieldNames())
    monkeypatch.setattr(config_module, "_write_bootstrap_table", lambda **kwargs: writes.append(kwargs))
    monkeypatch.setattr(config_module, "_active_steward_count", lambda spark, path: 1)

    result = setup_metadata_tables(spark=object(), config=framework_config(), env="dev")

    assert result["status"] == "ready"
    assert result["tables"] == list(schemas)
    assert result["created_tables"] == []
    assert result["skipped_tables"] == list(schemas)
    assert result["warnings"] == []
    assert result["active_metadata_tables"] == list(schemas)
    assert result["created_or_checked_tables"] == list(schemas)
    assert writes == []
    assert [path.rsplit('/', 1)[-1] for path in checked_paths] == list(schemas)


def test_central_metadata_setup_rejects_existing_tables_missing_columns(monkeypatch):
    """Verify central metadata setup rejects existing tables missing columns."""
    import fabricops_kit.config as config_module

    class Schema:
        def __init__(self, fields):
            self._fields = list(fields)

        def fieldNames(self):  # noqa: N802 - mirrors Spark API
            return list(self._fields)

    schemas = {
        "METADATA_DATA_STEWARD": Schema(["steward_id", "is_active"]),
        "METADATA_GUARDRAIL_RULES": Schema(["rule_id"]),
    }

    monkeypatch.setattr(config_module, "_metadata_table_definitions", lambda config: schemas)
    monkeypatch.setattr(config_module, "_existing_table_columns", lambda spark, path: ["steward_id"])
    monkeypatch.setattr(config_module, "_write_bootstrap_table", lambda **kwargs: pytest.fail("invalid existing schema should not be overwritten"))

    with pytest.raises(ValueError, match=r"METADATA_DATA_STEWARD is missing required column\(s\): is_active"):
        setup_metadata_tables(spark=object(), config=framework_config(), env="dev")
