from __future__ import annotations

import pytest

import fabricops_kit.data_agreement as agreement
import fabricops_kit.governance_review as governance
import fabricops_kit.metadata as metadata

from tests.helpers import FakeSpark, agreement_config, framework_config

pytestmark = pytest.mark.integration


def test_agreement_metadata_table_setup_creates_missing_tables_only(monkeypatch):
    writes = []
    attempts = {table: 0 for table in (agreement.DATA_STEWARD_TABLE, agreement.DATA_AGREEMENT_TABLE, agreement.DATA_AGREEMENT_EVIDENCE_TABLE)}

    def read_table(config, env, target, table, **kwargs):
        attempts[table] += 1
        if attempts[table] == 1:
            raise RuntimeError("missing")
        if table == agreement.DATA_STEWARD_TABLE:
            return [dict.fromkeys(agreement._get_data_steward_schema(), "")]
        if table == agreement.DATA_AGREEMENT_TABLE:
            return [dict.fromkeys(agreement._get_data_agreement_schema(), "")]
        return [dict.fromkeys(agreement._get_data_agreement_evidence_schema(), "")]

    monkeypatch.setattr(agreement, "read_lakehouse_table", read_table)
    monkeypatch.setattr(agreement, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((env, target, table, kwargs)))

    first = agreement._setup_data_agreement_tables(spark=FakeSpark(), config=agreement_config(), env="dev")
    second = agreement._setup_data_agreement_tables(spark=FakeSpark(), config=agreement_config(), env="dev")

    assert first["created_tables"] == [agreement.DATA_STEWARD_TABLE, agreement.DATA_AGREEMENT_TABLE, agreement.DATA_AGREEMENT_EVIDENCE_TABLE]
    assert second["created_tables"] == []
    assert all((env, target) == ("dev", "metadata") for env, target, _, _ in writes)
    assert {kwargs["mode"] for _, _, _, kwargs in writes} == {"ignore"}


def test_governance_metadata_setup_validates_spark_schemas(monkeypatch):
    class FakeTable:
        def __init__(self, schema):
            self.schema = schema
            self.columns = schema.fieldNames()

    class Spark:
        def __init__(self):
            self.created_schemas = []

        def createDataFrame(self, rows, schema=None):  # noqa: N802
            self.created_schemas.append(schema)
            return FakeTable(schema)

    reads = {table: 0 for table in governance._get_governance_metadata_schemas()}
    writes = []

    def read_table(config, env, target, table, spark_session=None):
        reads[table] += 1
        if reads[table] == 1:
            raise RuntimeError("[PATH_NOT_FOUND] missing")
        return FakeTable(governance._get_governance_metadata_schemas()[table])

    monkeypatch.setattr(governance, "read_lakehouse_table", read_table)
    monkeypatch.setattr(governance, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((table, kwargs)))

    result = governance._setup_governance_metadata_tables(spark=Spark(), config=framework_config(), env="dev")

    assert result["status"] == "ready"
    assert set(result["created_tables"]) == set(governance._get_governance_metadata_schemas())
    assert all(kwargs["mode"] == "ignore" for _, kwargs in writes)


def test_notebook_registry_rejects_existing_tables_missing_required_schema(monkeypatch):
    monkeypatch.setattr(metadata, "read_lakehouse_table", lambda *args, **kwargs: [{"agreement_id": "DA-1", "workspace": "legacy"}])
    monkeypatch.setattr(metadata, "write_lakehouse_table", lambda *args, **kwargs: pytest.fail("invalid existing schema should not be overwritten"))

    with pytest.raises(ValueError, match="workspace_name"):
        metadata._setup_notebook_registry_table(spark=FakeSpark(), config=framework_config(), env="dev")
