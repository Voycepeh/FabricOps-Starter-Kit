from __future__ import annotations

import pandas as pd
import pytest

from fabricops_kit.governance_review import _validate_dq_rules
from fabricops_kit.drift import _generate_schema_guardrail_config, enforce_catalogue_stability, stop_if_failed, validate_schema

pytestmark = pytest.mark.unit


def test_validate_schema_supports_strict_allow_new_and_monitor_modes():
    df = pd.DataFrame({"id": [1, 2], "amount": [10.0, 20.0], "new_col": ["x", "y"]})
    expected = {"id": "bigint", "amount": "double"}

    strict = validate_schema(df, expected, preset="strict")
    allow_new = validate_schema(df, expected, preset="allow_new_columns")
    monitor = validate_schema(df[["id"]], expected, preset="monitor_only")

    assert strict["status"] == "failed"
    assert strict["can_continue"] is False
    assert allow_new["status"] == "warning"
    assert allow_new["can_continue"] is True
    assert monitor["status"] == "warning"
    assert monitor["can_continue"] is True
    with pytest.raises(ValueError, match="preset"):
        validate_schema(df, expected, preset="unknown")


def test_internal_generate_schema_guardrail_config_returns_dict_rows_and_python_code():
    df = pd.DataFrame({"id": [1], "status": ["open"], "_runtime": ["skip"]})

    config = _generate_schema_guardrail_config(df, exclude_columns=["_runtime"], output_format="dict")
    rows = _generate_schema_guardrail_config(df, exclude_columns=["_runtime"], output_format="rows")
    python_code = _generate_schema_guardrail_config(df, exclude_columns=["_runtime"], output_format="python")

    assert config == {"id": "bigint", "status": "string"}
    assert rows == [
        {"column_name": "id", "spark_data_type": "int64", "nullable": None, "guardrail_data_type": "bigint"},
        {"column_name": "status", "spark_data_type": "object", "nullable": None, "guardrail_data_type": "string"},
    ]
    assert "expected_schema = {" in python_code
    assert "'id': 'bigint'" in python_code
    with pytest.raises(ValueError, match="output_format"):
        _generate_schema_guardrail_config(df, output_format="html")


def test__validate_dq_rules_accepts_canonical_rules_and_rejects_invalid_shapes():
    valid_rules = [
        {"rule_id": "id_required", "rule_type": "not_null", "columns": ["id"], "severity": "error", "description": "ID required"},
        {
            "rule_id": "status_values",
            "rule_type": "accepted_values",
            "columns": ["status"],
            "allowed_values": ["active", "inactive"],
            "severity": "warning",
            "description": "Known status",
        },
    ]

    assert _validate_dq_rules(valid_rules) == valid_rules
    for invalid in (
        None,
        [{"rule_id": "missing", "rule_type": "not_null", "columns": ["id"]}],
        [{"rule_id": "bad_type", "rule_type": "custom", "columns": ["id"], "severity": "error", "description": "x"}],
        [{"rule_id": "no_cols", "rule_type": "not_null", "columns": [], "severity": "error", "description": "x"}],
    ):
        with pytest.raises(ValueError):
            _validate_dq_rules(invalid)


def test_enforce_catalogue_stability_reads_catalogue_through_metadata_route(spark_session, monkeypatch):
    import fabricops_kit.fabric_input_output as io

    df = spark_session.createDataFrame([(1, "open")], "id int, status string")
    first = enforce_catalogue_stability(spark_session, df, "missing_catalogue", "sales", "orders", stage="source", run_id="run-1", data_behavior="fixed", stability_check_type="full_profile_hash")
    catalogue_df = spark_session.createDataFrame([{**first, "dataset_name": "sales", "table_name": "orders", "profile_stage": "source", "profile_run_id": "run-1", "profile_status": "success", "profiled_at": "2026-01-01T00:00:00Z"}])
    calls = []

    def fake_read(config, env, target, table, *, spark_session=None):
        calls.append((config, env, target, table, spark_session))
        return catalogue_df

    monkeypatch.setattr(io, "read_lakehouse_table", fake_read)
    result = enforce_catalogue_stability(spark_session, df, "METADATA_DATA_CATALOGUE", "sales", "orders", stage="source", run_id="run-2", data_behavior="fixed", stability_check_type="full_profile_hash", config={"cfg": True}, env="dev")

    assert result["status"] == "passed"
    assert calls == [({"cfg": True}, "dev", "metadata", "METADATA_DATA_CATALOGUE", spark_session)]


def test_enforce_catalogue_stability_ignores_incompatible_skipped_and_failed_baselines(spark_session):
    df = spark_session.createDataFrame([(1, "open")], "id int, status string")
    first = enforce_catalogue_stability(spark_session, df, "missing_catalogue", "sales", "orders", stage="source", run_id="run-good", data_behavior="fixed", stability_check_type="full_profile_hash")
    rows = [
        {**first, "dataset_name": "sales", "table_name": "orders", "profile_stage": "source", "profile_run_id": "run-skipped", "profile_status": "success", "profiled_at": "2026-01-03T00:00:00Z", "stability_status": "skipped", "stability_check_enabled": False},
        {**first, "dataset_name": "sales", "table_name": "orders", "profile_stage": "source", "profile_run_id": "run-failed", "profile_status": "success", "profiled_at": "2026-01-02T00:00:00Z", "stability_status": "failed"},
        {**first, "dataset_name": "sales", "table_name": "orders", "profile_stage": "source", "profile_run_id": "run-changing", "profile_status": "success", "profiled_at": "2026-01-01T12:00:00Z", "data_behavior": "changing"},
        {**first, "dataset_name": "sales", "table_name": "orders", "profile_stage": "source", "profile_run_id": "run-good", "profile_status": "success", "profiled_at": "2026-01-01T00:00:00Z"},
    ]
    catalogue_df = spark_session.createDataFrame(rows)

    result = enforce_catalogue_stability(spark_session, df, "METADATA_DATA_CATALOGUE", "sales", "orders", stage="source", run_id="run-current", data_behavior="fixed", stability_check_type="full_profile_hash", catalogue_df=catalogue_df)

    assert result["status"] == "passed"
    assert result["baseline_run_id"] == "run-good"


def test_enforce_catalogue_stability_watermark_requires_usable_baseline_hash_and_watermark(spark_session):
    df = spark_session.createDataFrame([(1, "2026-01-01", 10)], "id int, business_date string, amount int")
    first = enforce_catalogue_stability(spark_session, df, "missing_catalogue", "sales", "orders", stage="source", run_id="run-1", data_behavior="changing", stability_check_type="watermark_slice_hash", watermark_column="business_date", watermark_value="2026-01-01")
    bad = {**first, "dataset_name": "sales", "table_name": "orders", "profile_stage": "source", "profile_run_id": "run-1", "profile_status": "success", "profiled_at": "2026-01-01T00:00:00Z", "watermark_value": "", "comparable_profile_hash": ""}
    catalogue_df = spark_session.createDataFrame([bad])

    result = enforce_catalogue_stability(spark_session, df, "METADATA_DATA_CATALOGUE", "sales", "orders", stage="source", run_id="run-2", data_behavior="changing", stability_check_type="watermark_slice_hash", watermark_column="business_date", watermark_value="2026-01-01", catalogue_df=catalogue_df)

    assert result["status"] == "baseline_created"
    assert result["can_continue"] is True


def test_enforce_catalogue_stability_technical_columns_do_not_change_hashes(spark_session):
    baseline_df = spark_session.createDataFrame([(1, "2026-01-01", 10)], "id int, business_date string, amount int")
    tagged_df = spark_session.createDataFrame(
        [(1, "2026-01-01", 10, "warning", "amount_positive", "run-2", "pipe", "2026-01-02")],
        "id int, business_date string, amount int, _dq_check_status string, _dq_failed_rules string, _fabricops_run_id string, _fabricops_pipeline_name string, _fabricops_created_at string",
    )
    first = enforce_catalogue_stability(spark_session, baseline_df, "missing_catalogue", "sales", "orders", stage="target", run_id="run-1", data_behavior="changing", stability_check_type="watermark_slice_hash", watermark_column="business_date", watermark_value="2026-01-01")
    catalogue_df = spark_session.createDataFrame([{**first, "dataset_name": "sales", "table_name": "orders", "profile_stage": "target", "profile_run_id": "run-1", "profile_status": "success", "profiled_at": "2026-01-01T00:00:00Z"}])

    result = enforce_catalogue_stability(spark_session, tagged_df, "METADATA_DATA_CATALOGUE", "sales", "orders", stage="target", run_id="run-2", data_behavior="changing", stability_check_type="watermark_slice_hash", watermark_column="business_date", watermark_value="2026-01-01", catalogue_df=catalogue_df)

    assert result["status"] == "passed"
    assert result["profile_hash"] == first["profile_hash"]
    assert result["comparable_profile_hash"] == first["comparable_profile_hash"]
    assert result["schema_hash"] == first["schema_hash"]


def test_stop_if_failed_blocks_only_failed_guardrail_results():
    stop_if_failed({"can_continue": True, "status": "warning", "message": "observed"})
    stop_if_failed({"result": {"can_continue": True, "status": "passed"}})

    with pytest.raises(Exception):
        stop_if_failed({"can_continue": False, "status": "failed", "message": "blocked"})


def test_drift_public_surface_keeps_removed_exceptions_unexported():
    import fabricops_kit
    import fabricops_kit.drift as drift

    public_drift_callables = {"validate_schema", "enforce_catalogue_stability", "stop_if_failed"}
    exported_from_drift = {
        name
        for name in fabricops_kit.__all__
        if getattr(fabricops_kit, name).__module__ == "fabricops_kit.drift"
    }

    assert exported_from_drift == public_drift_callables
    assert not hasattr(drift, "_check_partition_drift")
    assert not hasattr(drift, "_build_partition_snapshot")


def test_enforce_catalogue_stability_fixed_passes_when_profile_hash_unchanged(spark_session):
    df = spark_session.createDataFrame([(1, "open"), (2, "closed")], "id int, status string")
    first = enforce_catalogue_stability(spark_session, df, "missing_catalogue", "sales", "orders", stage="source", run_id="run-1", data_behavior="fixed", stability_check_type="full_profile_hash")
    spark_session.createDataFrame([{**first, "dataset_name": "sales", "table_name": "orders", "profile_stage": "source", "profile_run_id": "run-1", "profile_status": "success", "profiled_at": "2026-01-01T00:00:00Z"}]).createOrReplaceTempView("catalogue_fixed_pass")

    result = enforce_catalogue_stability(spark_session, df, "METADATA_DATA_CATALOGUE", "sales", "orders", stage="source", run_id="run-2", data_behavior="fixed", stability_check_type="full_profile_hash", catalogue_df=spark_session.table("catalogue_fixed_pass"))

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert result["baseline_run_id"] == "run-1"


def test_enforce_catalogue_stability_fixed_fails_when_profile_hash_changes(spark_session):
    baseline_df = spark_session.createDataFrame([(1, "open"), (2, "closed")], "id int, status string")
    changed_df = spark_session.createDataFrame([(1, "open"), (2, "closed"), (3, "new")], "id int, status string")
    first = enforce_catalogue_stability(spark_session, baseline_df, "missing_catalogue", "sales", "orders", stage="target", run_id="run-1", data_behavior="fixed", stability_check_type="full_profile_hash")
    spark_session.createDataFrame([{**first, "dataset_name": "sales", "table_name": "orders", "profile_stage": "target", "profile_run_id": "run-1", "profile_status": "success", "profiled_at": "2026-01-01T00:00:00Z"}]).createOrReplaceTempView("catalogue_fixed_fail")

    result = enforce_catalogue_stability(spark_session, changed_df, "METADATA_DATA_CATALOGUE", "sales", "orders", stage="target", run_id="run-2", data_behavior="fixed", stability_check_type="full_profile_hash", catalogue_df=spark_session.table("catalogue_fixed_fail"))

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert "differs" in result["message"]


def test_enforce_catalogue_stability_changing_watermark_slice_passes_and_fails(spark_session):
    baseline_df = spark_session.createDataFrame([(1, "2026-01-01", 10), (2, "2026-01-02", 20)], "id int, business_date string, amount int")
    unchanged_df = spark_session.createDataFrame([(1, "2026-01-01", 10), (2, "2026-01-02", 20), (3, "2026-01-03", 30)], "id int, business_date string, amount int")
    changed_df = spark_session.createDataFrame([(1, "2026-01-01", 999), (2, "2026-01-02", 20), (3, "2026-01-03", 30)], "id int, business_date string, amount int")
    first = enforce_catalogue_stability(spark_session, baseline_df, "missing_catalogue", "sales", "orders", stage="source", run_id="run-1", data_behavior="changing", stability_check_type="watermark_slice_hash", watermark_column="business_date", watermark_value="2026-01-02")
    spark_session.createDataFrame([{**first, "dataset_name": "sales", "table_name": "orders", "profile_stage": "source", "profile_run_id": "run-1", "profile_status": "success", "profiled_at": "2026-01-01T00:00:00Z"}]).createOrReplaceTempView("catalogue_changing")

    passed = enforce_catalogue_stability(spark_session, unchanged_df, "METADATA_DATA_CATALOGUE", "sales", "orders", stage="source", run_id="run-2", data_behavior="changing", stability_check_type="watermark_slice_hash", watermark_column="business_date", watermark_value="2026-01-03", catalogue_df=spark_session.table("catalogue_changing"))
    failed = enforce_catalogue_stability(spark_session, changed_df, "METADATA_DATA_CATALOGUE", "sales", "orders", stage="source", run_id="run-2", data_behavior="changing", stability_check_type="watermark_slice_hash", watermark_column="business_date", watermark_value="2026-01-03", catalogue_df=spark_session.table("catalogue_changing"))

    assert passed["status"] == "passed"
    assert failed["status"] == "failed"
    assert "Previously loaded data changed" in failed["message"]


def test_enforce_catalogue_stability_first_run_and_current_run_exclusion(spark_session):
    df = spark_session.createDataFrame([(1, "open")], "id int, status string")
    current = enforce_catalogue_stability(spark_session, df, "missing_catalogue", "sales", "orders", stage="source", run_id="run-current", data_behavior="fixed", stability_check_type="full_profile_hash")
    spark_session.createDataFrame([{**current, "dataset_name": "sales", "table_name": "orders", "profile_stage": "source", "profile_run_id": "run-current", "profile_status": "success", "profiled_at": "2026-01-02T00:00:00Z"}]).createOrReplaceTempView("catalogue_current_only")

    result = enforce_catalogue_stability(spark_session, df, "METADATA_DATA_CATALOGUE", "sales", "orders", stage="source", run_id="run-current", data_behavior="fixed", stability_check_type="full_profile_hash", catalogue_df=spark_session.table("catalogue_current_only"))

    assert result["status"] == "baseline_created"
    assert result["can_continue"] is True
