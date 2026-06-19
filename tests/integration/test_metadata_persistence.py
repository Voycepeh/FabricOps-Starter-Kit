"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import pytest

from fabricops_kit.config import setup_metadata_tables
from tests.helpers import framework_config

pytestmark = pytest.mark.integration


def test_central_metadata_setup_preserves_existing_valid_tables(monkeypatch):
    """Verify central metadata setup preserves existing valid tables."""
    import fabricops_kit.config as config_module
    import fabricops_kit.fabric_input_output as io
    import fabricops_kit.governance_review as governance

    class Schema:
        def __init__(self, fields):
            self._fields = list(fields)

        def fieldNames(self):  # noqa: N802 - mirrors Spark API
            return list(self._fields)

    class Table:
        def __init__(self, fields):
            self.columns = list(fields)

    schemas = {
        "METADATA_DATA_STEWARD": Schema(["steward_id", "is_active"]),
        "METADATA_DATA_AGREEMENT": Schema(["agreement_id"]),
        "METADATA_DATA_AGREEMENT_EVIDENCE": Schema(["agreement_id", "file_path"]),
        "METADATA_NOTEBOOK_REGISTRY": Schema(["agreement_id", "registration_id"]),
        "METADATA_GUARDRAIL_RULES": Schema(["rule_id"]),
    }
    reads = []
    writes = []

    def read_table(table, *, target, context, spark_session=None, **kwargs):
        assert context["env"] == "dev"
        assert target == "metadata"
        reads.append((context["env"], target, table))
        return Table(schemas[table].fieldNames())

    class Spark:
        def sql(self, statement):
            raise AssertionError(f"metadata setup must not call spark.sql: {statement}")

    monkeypatch.setattr(config_module, "_get_metadata_table_schema_registry", lambda config: schemas)
    monkeypatch.setattr(governance, "_get_governance_metadata_schemas", lambda: {"METADATA_GUARDRAIL_RULES": schemas["METADATA_GUARDRAIL_RULES"]})
    monkeypatch.setattr(io, "read_lakehouse_table", read_table)
    monkeypatch.setattr(io, "write_lakehouse_table", lambda *args, **kwargs: writes.append((args, kwargs)))
    monkeypatch.setattr("fabricops_kit.data_agreement._list_data_stewards", lambda *args, **kwargs: [{"steward_id": "s1"}])

    result = setup_metadata_tables(spark=Spark(), config=framework_config(), env="dev")

    assert result["status"] == "ready"
    assert result["tables"] == list(schemas)
    assert result["created_tables"] == []
    assert result["warnings"] == []
    assert result["active_metadata_tables"] == list(schemas)
    assert result["created_or_checked_tables"] == list(schemas)
    assert writes == []
    assert reads == [("dev", "metadata", table) for table in list(schemas) + list(schemas)]


def test_central_metadata_setup_rejects_existing_tables_missing_columns(monkeypatch):
    """Verify central metadata setup rejects existing tables missing columns."""
    import fabricops_kit.config as config_module
    import fabricops_kit.fabric_input_output as io
    import fabricops_kit.governance_review as governance

    class Schema:
        def __init__(self, fields):
            self._fields = list(fields)

        def fieldNames(self):  # noqa: N802 - mirrors Spark API
            return list(self._fields)

    schemas = {
        "METADATA_DATA_STEWARD": Schema(["steward_id", "is_active"]),
        "METADATA_GUARDRAIL_RULES": Schema(["rule_id"]),
    }

    class BadTable:
        columns = ["steward_id"]

    monkeypatch.setattr(config_module, "_get_metadata_table_schema_registry", lambda config: schemas)
    monkeypatch.setattr(governance, "_get_governance_metadata_schemas", lambda: {"METADATA_GUARDRAIL_RULES": schemas["METADATA_GUARDRAIL_RULES"]})
    monkeypatch.setattr(io, "read_lakehouse_table", lambda *args, **kwargs: BadTable())
    monkeypatch.setattr(io, "write_lakehouse_table", lambda *args, **kwargs: pytest.fail("invalid existing schema should not be overwritten"))

    with pytest.raises(ValueError, match=r"METADATA_DATA_STEWARD is missing required column\(s\): is_active"):
        setup_metadata_tables(spark=object(), config=framework_config(), env="dev")
