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


def test_public_pipeline_helpers_are_exported_without_wrapper_bloat():
    assert "write_catalogue_evidence" in fabricops_kit.__all__
    assert "write_pipeline_lineage" in fabricops_kit.__all__
    assert "write_pipeline_run_summary" in fabricops_kit.__all__
    for removed_name in {
        "read_pipeline_sources",
        "profile_pipeline_datasets",
        "run_schema_guardrails",
        "run_data_drift_guardrails",
        "run_dq_guardrails",
        "add_runtime_audit_columns",
        "write_pipeline_targets",
    }:
        assert removed_name not in fabricops_kit.__all__
        assert not hasattr(fabricops_kit, removed_name)


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
