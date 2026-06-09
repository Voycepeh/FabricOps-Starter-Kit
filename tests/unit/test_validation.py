from __future__ import annotations

import pandas as pd
import pytest

from fabricops_kit.governance_review import _validate_dq_rules
from fabricops_kit.drift import (
    display_schema_profile,
    enforce_catalogue_stability,
    generate_schema_guardrail_config,
    print_schema_guardrail_config,
    stop_if_failed,
    validate_schema,
)

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


def test_schema_guardrail_helpers_generate_reviewable_config(capsys):
    class FakeField:
        def __init__(self, name, data_type, nullable):
            self.name = name
            self.dataType = data_type
            self.nullable = nullable

    class FakeSchema:
        fields = [
            FakeField("status", "StringType()", True),
            FakeField("id", "IntegerType()", False),
            FakeField("amount", "DecimalType(10,2)", True),
            FakeField("loaded_at", "TimestampType()", True),
        ]

    class FakeDataFrame:
        schema = FakeSchema()
        dtypes = [(field.name, str(field.dataType)) for field in schema.fields]
        columns = [field.name for field in schema.fields]

    config = generate_schema_guardrail_config(FakeDataFrame(), exclude_columns={"loaded_at"}, sort_columns=True)
    rows = display_schema_profile(FakeDataFrame(), exclude_columns={"loaded_at"}, sort_columns=True)
    printed = print_schema_guardrail_config(FakeDataFrame(), exclude_columns={"loaded_at"}, sort_columns=True, variable_name="source_expected_schema")
    output = capsys.readouterr().out

    assert config == {"amount": "decimal(10,2)", "id": "integer", "status": "string"}
    assert printed == config
    assert rows[0] == {"column_name": "amount", "spark_data_type": "DecimalType(10,2)", "nullable": True, "guardrail_data_type": "decimal(10,2)"}
    assert "source_expected_schema = {" in output
    assert "'id': 'integer'" in output


def test_stop_if_failed_blocks_only_failed_guardrail_results():
    stop_if_failed({"can_continue": True, "status": "warning", "message": "observed"})
    stop_if_failed({"result": {"can_continue": True, "status": "passed"}})

    with pytest.raises(Exception):
        stop_if_failed({"can_continue": False, "status": "failed", "message": "blocked"})


def test_drift_public_surface_keeps_removed_exceptions_unexported():
    import fabricops_kit
    import fabricops_kit.drift as drift

    public_drift_callables = {"validate_schema", "generate_schema_guardrail_config", "print_schema_guardrail_config", "display_schema_profile", "enforce_catalogue_stability", "stop_if_failed"}
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

    result = enforce_catalogue_stability(spark_session, df, "catalogue_fixed_pass", "sales", "orders", stage="source", run_id="run-2", data_behavior="fixed", stability_check_type="full_profile_hash")

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert result["baseline_run_id"] == "run-1"


def test_enforce_catalogue_stability_fixed_fails_when_profile_hash_changes(spark_session):
    baseline_df = spark_session.createDataFrame([(1, "open"), (2, "closed")], "id int, status string")
    changed_df = spark_session.createDataFrame([(1, "open"), (2, "closed"), (3, "new")], "id int, status string")
    first = enforce_catalogue_stability(spark_session, baseline_df, "missing_catalogue", "sales", "orders", stage="target", run_id="run-1", data_behavior="fixed", stability_check_type="full_profile_hash")
    spark_session.createDataFrame([{**first, "dataset_name": "sales", "table_name": "orders", "profile_stage": "target", "profile_run_id": "run-1", "profile_status": "success", "profiled_at": "2026-01-01T00:00:00Z"}]).createOrReplaceTempView("catalogue_fixed_fail")

    result = enforce_catalogue_stability(spark_session, changed_df, "catalogue_fixed_fail", "sales", "orders", stage="target", run_id="run-2", data_behavior="fixed", stability_check_type="full_profile_hash")

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert "differs" in result["message"]


def test_enforce_catalogue_stability_changing_watermark_slice_passes_and_fails(spark_session):
    baseline_df = spark_session.createDataFrame([(1, "2026-01-01", 10), (2, "2026-01-02", 20)], "id int, business_date string, amount int")
    unchanged_df = spark_session.createDataFrame([(1, "2026-01-01", 10), (2, "2026-01-02", 20), (3, "2026-01-03", 30)], "id int, business_date string, amount int")
    changed_df = spark_session.createDataFrame([(1, "2026-01-01", 999), (2, "2026-01-02", 20), (3, "2026-01-03", 30)], "id int, business_date string, amount int")
    first = enforce_catalogue_stability(spark_session, baseline_df, "missing_catalogue", "sales", "orders", stage="source", run_id="run-1", data_behavior="changing", stability_check_type="watermark_slice_hash", watermark_column="business_date", watermark_value="2026-01-02")
    spark_session.createDataFrame([{**first, "dataset_name": "sales", "table_name": "orders", "profile_stage": "source", "profile_run_id": "run-1", "profile_status": "success", "profiled_at": "2026-01-01T00:00:00Z"}]).createOrReplaceTempView("catalogue_changing")

    passed = enforce_catalogue_stability(spark_session, unchanged_df, "catalogue_changing", "sales", "orders", stage="source", run_id="run-2", data_behavior="changing", stability_check_type="watermark_slice_hash", watermark_column="business_date", watermark_value="2026-01-03")
    failed = enforce_catalogue_stability(spark_session, changed_df, "catalogue_changing", "sales", "orders", stage="source", run_id="run-2", data_behavior="changing", stability_check_type="watermark_slice_hash", watermark_column="business_date", watermark_value="2026-01-03")

    assert passed["status"] == "passed"
    assert failed["status"] == "failed"
    assert "Previously loaded data changed" in failed["message"]


def test_enforce_catalogue_stability_first_run_and_current_run_exclusion(spark_session):
    df = spark_session.createDataFrame([(1, "open")], "id int, status string")
    current = enforce_catalogue_stability(spark_session, df, "missing_catalogue", "sales", "orders", stage="source", run_id="run-current", data_behavior="fixed", stability_check_type="full_profile_hash")
    spark_session.createDataFrame([{**current, "dataset_name": "sales", "table_name": "orders", "profile_stage": "source", "profile_run_id": "run-current", "profile_status": "success", "profiled_at": "2026-01-02T00:00:00Z"}]).createOrReplaceTempView("catalogue_current_only")

    result = enforce_catalogue_stability(spark_session, df, "catalogue_current_only", "sales", "orders", stage="source", run_id="run-current", data_behavior="fixed", stability_check_type="full_profile_hash")

    assert result["status"] == "baseline_created"
    assert result["can_continue"] is True
