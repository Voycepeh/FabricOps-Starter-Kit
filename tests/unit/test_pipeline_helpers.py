from __future__ import annotations

import json

import pytest

import fabricops_kit
from fabricops_kit import pipeline

pytestmark = pytest.mark.unit


class FakeSpark:
    def __init__(self):
        self.created = []

    def createDataFrame(self, rows, schema=None):
        self.created.append((rows, schema))
        return {"rows": rows, "schema": schema}


def test_new_pipeline_helpers_are_exported():
    expected = {
        "read_pipeline_sources",
        "profile_pipeline_datasets",
        "run_schema_guardrails",
        "run_data_drift_guardrails",
        "run_dq_guardrails",
        "write_catalogue_evidence",
        "add_runtime_audit_columns",
        "write_pipeline_targets",
        "write_pipeline_lineage",
        "write_pipeline_run_summary",
    }
    assert expected <= set(fabricops_kit.__all__)
    for name in expected:
        assert callable(getattr(fabricops_kit, name))


def test_read_pipeline_sources_supports_many_source_kinds(monkeypatch):
    calls = []
    monkeypatch.setattr(pipeline, "read_lakehouse_table", lambda config, env, layer, table, spark_session=None: calls.append(("lakehouse", layer, table)) or f"df_{table}")
    monkeypatch.setattr(pipeline, "read_lakehouse_csv", lambda config, env, layer, path, spark_session=None, header=True: calls.append(("csv", layer, path, header)) or f"df_{path}")

    sources = pipeline.read_pipeline_sources(
        {
            "orders": {"kind": "lakehouse", "layer": "source", "table_name": "orders"},
            "customers": {"kind": "csv", "layer": "source", "path": "Files/customers.csv", "header": True},
        },
        config={},
        env="dev",
        spark_session=object(),
    )

    assert set(sources) == {"orders", "customers"}
    assert calls == [("lakehouse", "source", "orders"), ("csv", "source", "Files/customers.csv", True)]


def test_write_pipeline_lineage_supports_many_to_many_relationships(monkeypatch):
    writes = []
    monkeypatch.setattr(pipeline, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((df, env, target, table, kwargs)))

    result = pipeline.write_pipeline_lineage(
        spark=FakeSpark(),
        config={},
        env="dev",
        run_id="run-1",
        source_definitions={"s1": {"table_name": "source_one"}, "s2": {"table_name": "source_two"}},
        target_definitions={"t1": {"table_name": "target_one"}, "t2": {"table_name": "target_two"}},
        relationships=[{"sources": ["s1", "s2"], "targets": ["t1", "t2"], "operation": "join"}],
        dataset_name="sales",
    )

    assert result["row_count"] == 4
    assert writes[0][2:4] == ("metadata", "METADATA_DATA_LINEAGE_TABLE")
    payload = json.loads(result["rows"][0]["transformation_steps_json"])
    assert payload["operation"] == "join"


def test_write_pipeline_run_summary_writes_metadata_table(monkeypatch):
    writes = []
    fake_spark = FakeSpark()
    monkeypatch.setattr(pipeline, "write_lakehouse_table", lambda df, config, env, target, table, **kwargs: writes.append((df, env, target, table, kwargs)))

    row = pipeline.write_pipeline_run_summary(
        spark=fake_spark,
        config={},
        env="dev",
        run_id="run-1",
        source_definitions={"s1": {"table_name": "source_one"}, "s2": {"table_name": "source_two"}},
        target_definitions={"t1": {"table_name": "target_one"}, "t2": {"table_name": "target_two"}},
        source_schema_results={"s1": {"status": "passed"}},
        target_schema_results={"t1": {"status": "passed"}},
        source_dq_results={"s1": {"status": "passed"}},
        target_dq_results={"t1": {"status": "warning"}},
    )

    assert row["source_count"] == 2
    assert row["target_count"] == 2
    assert row["dq_status"] == "warning"
    assert writes[0][2:4] == ("metadata", "METADATA_PIPELINE_RUNS")
    assert writes[0][4]["mode"] == "append"
