"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import importlib
import json
from pathlib import Path

import pytest

import fabricops_kit
import fabricops_kit.pipeline as pipeline
from fabricops_kit.pipeline import shared as pipeline_shared
widgets_shared_module = importlib.import_module("fabricops_kit.widgets.shared")
from tests.helpers import framework_config

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _canonical_audit(monkeypatch):
    """Provide deterministic canonical audit fields for pipeline helper tests."""
    audit = {
        "_workspace_id": "workspace-id",
        "_workspace_name": "workspace",
        "_notebook_id": "notebook-id",
        "_notebook_name": "02_pipeline",
        "_activity_id": "activity-id",
        "_committed_by": "user",
        "_committed_at": "2026-01-01T00:00:00+00:00",
        "_metadata_lakehouse_name": "lh_metadata_dev",
    }
    monkeypatch.setattr(pipeline_shared, "_runtime_audit_fields", lambda *args, **kwargs: dict(audit))



class FakeSpark:
    """Fakespark test double."""

    def __init__(self):
        """Initialize the test helper."""
        self.created = []

    def createDataFrame(self, rows, schema=None):
        """Return createDataFrame."""
        self.created.append((rows, schema))
        return {"rows": rows, "schema": schema}


def test_public_pipeline_helpers_are_exported_without_wrapper_bloat():
    """Verify public pipeline helpers are exported without wrapper bloat."""
    assert "prepare_pipeline_table_configs" not in fabricops_kit.__all__
    assert not hasattr(fabricops_kit, "prepare_pipeline_table_configs")
    assert not hasattr(pipeline, "prepare_pipeline_table_configs")
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("fabricops_kit.pipeline.prepare_pipeline_table_configs")
    assert "run_table_guardrails" not in fabricops_kit.__all__
    assert not hasattr(fabricops_kit, "run_table_guardrails")
    assert "write_catalogue_evidence" not in fabricops_kit.__all__
    assert "write_pipeline_lineage" not in fabricops_kit.__all__
    assert "write_pipeline_run_summary" not in fabricops_kit.__all__
    for removed_name in {
        "prepare_source_table_configs",
        "prepare_target_table_configs",
        "write_target_tables",
        "build_guardrail_evidence_definitions",
        "guardrail_summary",
        "stop_if_any_guardrail_failed",
        "read_pipeline_sources",
        "profile_pipeline_datasets",
        "run_schema_guardrails",
        "run_source_stability_guardrails",
        "run_dq_guardrails",
        "add_runtime_audit_columns",
        "write_pipeline_targets",
    }:
        assert removed_name not in fabricops_kit.__all__
        assert not hasattr(fabricops_kit, removed_name)

    for private_source_reader in {"_load_source_dataframe", "_read_source_dataframe", "_source_read_type"}:
        assert not hasattr(fabricops_kit, private_source_reader)


class FakeDataFrame:
    """Fakedataframe test double."""

    def __init__(self, name="df"):
        """Initialize the test helper."""
        self.name = name
        self.with_columns = []

    def withColumn(self, name, value):
        """Return withColumn."""
        self.with_columns.append((name, value))
        return self


def test_pipeline_module_does_not_expose_source_read_routing_wrappers():
    """Verify pipeline module does not expose source read routing wrappers."""
    assert not hasattr(pipeline, "_load_source_dataframe")
    assert not hasattr(pipeline, "_read_source_dataframe")
    assert not hasattr(pipeline, "_source_read_type")




def test_summary_status_treats_baseline_created_as_passed_and_skipped_as_nonblocking():
    """Verify summary status treats baseline created as passed and skipped as nonblocking."""
    assert pipeline_shared._summary_status({"s1": {"status": "baseline_created"}}) == "passed"
    assert pipeline_shared._summary_status({"s1": {"status": "skipped"}}) == "skipped"
    assert pipeline_shared._summary_status({"s1": {"status": "passed"}, "s2": {"status": "skipped"}}) == "passed"


def test_normalize_catalogue_evidence_types_casts_numeric_percent_timestamp_and_boolean_columns(spark_session):
    """Verify normalize catalogue evidence types casts only catalogue-owned fields."""
    evidence = spark_session.createDataFrame(
        [
            {
                "row_count": 3,
                "null_count": 0,
                "distinct_count": 3,
                "null_percent": 0,
                "distinct_percent": 100,
                "run_timestamp": "2026-01-01T00:00:00",
                "dataset_name": "orders",
            }
        ]
    )

    normalized = pipeline_shared._normalize_catalogue_evidence_types(evidence)
    dtypes = dict(normalized.dtypes)

    for column_name in ["row_count", "null_count", "distinct_count"]:
        assert dtypes[column_name] == "bigint"
    for column_name in ["null_percent", "distinct_percent"]:
        assert dtypes[column_name] == "double"
    assert dtypes["run_timestamp"] == "timestamp"
    assert dtypes["dataset_name"] == "string"



def test_private_guardrail_evidence_definitions_excludes_dataframes_and_resolves_target_fields():
    """Verify private guardrail evidence definitions excludes dataframes and resolves target fields."""
    definitions = pipeline_shared._build_guardrail_evidence_definitions(
        [
            {
                "key": "target_01",
                "df": object(),
                "table_name": "orders_curated",
                "stage": "target",
                "target_layer": "product",
                "target_kind": "warehouse",
                "write_mode": "overwrite",
                "fabric_store_target": "product",
            }
        ]
    )

    assert definitions == {
        "target_01": {
            "key": "target_01",
            "table_name": "orders_curated",
            "stage": "target",
            "target_layer": "product",
            "target_kind": "warehouse",
            "write_mode": "overwrite",
            "fabric_store_target": "product",
            "layer": "product",
            "kind": "warehouse",
            "mode": "overwrite",
        }
    }


def test_private_guardrail_evidence_definitions_defaults_fabric_store_target():
    """Verify missing FabricStore target defaults to source for evidence."""
    definitions = pipeline_shared._build_guardrail_evidence_definitions([{"key": "source_01", "table_name": "orders"}])
    assert definitions["source_01"]["fabric_store_target"] == "source"











def test_schema_guardrail_strict_and_allow_new_columns_behavior(spark_session):
    """Verify schema guardrail strict and allow new columns behavior."""
    from fabricops_kit.pipeline.shared import schema_check_core

    happy_df = spark_session.createDataFrame([(1, "new")], "id int, status string")
    additive_df = spark_session.createDataFrame([(1, "new", "extra")], "id int, status string, source_file string")
    incompatible_df = spark_session.createDataFrame([("1", "new")], "id string, status string")
    missing_df = spark_session.createDataFrame([(1,)], "id int")
    expected_schema = {"id": "int", "status": "string"}

    happy = schema_check_core(happy_df, expected_schema, preset="strict")
    assert happy["status"] == "passed"
    assert happy["can_continue"] is True

    strict_additive = schema_check_core(additive_df, expected_schema, preset="strict")
    assert strict_additive["status"] == "failed"
    assert strict_additive["can_continue"] is False
    assert strict_additive["unexpected_columns"] == ["source_file"]

    allowed_additive = schema_check_core(additive_df, expected_schema, preset="allow_new_columns")
    assert allowed_additive["status"] == "warning"
    assert allowed_additive["can_continue"] is True
    assert allowed_additive["unexpected_columns"] == ["source_file"]

    incompatible = schema_check_core(incompatible_df, expected_schema, preset="strict")
    assert incompatible["status"] == "failed"
    assert incompatible["can_continue"] is False
    assert incompatible["datatype_mismatches"] == [{"column": "id", "expected": "int", "actual": "string"}]

    incompatible_allow_new = schema_check_core(incompatible_df, expected_schema, preset="allow_new_columns")
    assert incompatible_allow_new["status"] == "failed"
    assert incompatible_allow_new["can_continue"] is False

    missing = schema_check_core(missing_df, expected_schema, preset="strict")
    assert missing["status"] == "failed"
    assert missing["can_continue"] is False
    assert missing["missing_columns"] == ["status"]


def test_freshness_guardrail_blocks_or_warns_by_severity(spark_session):
    """Verify freshness guardrail blocks or warns by severity."""
    from fabricops_kit.pipeline.shared import enforce_freshness

    current_df = spark_session.createDataFrame([("2026-06-14",), ("2026-06-13",)], "business_date string")
    stale_df = spark_session.createDataFrame([("2026-06-01",), ("2026-06-02",)], "business_date string")

    current = enforce_freshness(current_df, "business_date", 1, severity="blocking", reference_date="2026-06-14")
    assert current["status"] == "passed"
    assert current["can_continue"] is True
    assert current["latest_value"] == "2026-06-14"

    stale_blocking = enforce_freshness(stale_df, "business_date", 1, severity="blocking", reference_date="2026-06-14")
    assert stale_blocking["status"] == "failed"
    assert stale_blocking["can_continue"] is False
    assert stale_blocking["required_min_value"] == "2026-06-13"

    stale_warning = enforce_freshness(stale_df, "business_date", 1, severity="warning", reference_date="2026-06-14")
    assert stale_warning["status"] == "warning"
    assert stale_warning["can_continue"] is True
