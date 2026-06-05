import pytest

from fabricops_kit import profile_dataframe
from fabricops_kit.drift import (
    assert_no_blocking_profile_drift,
    check_profile_drift,
    extract_categorical_distribution_categories,
    extract_numeric_distribution_bin_edges,
    load_latest_profile,
)


def _profile(row_count=100, amount_counts=None, status_counts=None, null_pct=0.0):
    amount_counts = amount_counts if amount_counts is not None else [50, 50]
    status_counts = status_counts if status_counts is not None else {"A": 50, "B": 50}
    return {
        "dataset_name": "dataset",
        "table_name": "orders",
        "profile_stage": "source",
        "row_count": row_count,
        "columns": [
            {
                "column_name": "amount",
                "data_type": "double",
                "null_pct": null_pct,
                "distinct_pct": 10.0,
                "min_value": "0",
                "max_value": "100",
                "distribution_type": "numeric",
                "distribution": {"bin_edges": [0.0, 50.0, 100.0], "bin_counts": amount_counts},
            },
            {
                "column_name": "status",
                "data_type": "string",
                "null_pct": 0.0,
                "distinct_pct": 2.0,
                "distribution_type": "categorical",
                "distribution": {"category_counts": status_counts, "other_count": 0},
            },
        ],
    }


def test_missing_baseline_returns_no_baseline():
    result = check_profile_drift(_profile(), None)

    assert result == {"status": "no_baseline", "can_continue": True, "checks": [], "message": "No baseline profile provided."}


def test_stable_numeric_and_categorical_profile_passes():
    result = check_profile_drift(_profile(), _profile())

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert next(check for check in result["checks"] if check["check"] == "numeric_psi")["status"] == "passed"
    assert next(check for check in result["checks"] if check["check"] == "categorical_distance")["status"] == "passed"


def test_moderate_numeric_shift_warns_without_blocking():
    result = check_profile_drift(_profile(amount_counts=[70, 30]), _profile())
    numeric = next(check for check in result["checks"] if check["check"] == "numeric_psi")

    assert result["status"] == "warning"
    assert result["can_continue"] is True
    assert numeric["status"] == "warning"
    assert numeric["passed"] is True


def test_major_numeric_shift_blocks():
    result = check_profile_drift(_profile(amount_counts=[90, 10]), _profile())
    numeric = next(check for check in result["checks"] if check["check"] == "numeric_psi")

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert numeric["status"] == "failed"
    assert numeric["passed"] is False


def _numeric_status_for_counts(counts, *, warn=0.10, block=0.25):
    result = check_profile_drift(_profile(amount_counts=counts), _profile(), policy={"warn_numeric_psi": warn, "block_numeric_psi": block})
    return next(check for check in result["checks"] if check["check"] == "numeric_psi"), result


def test_numeric_psi_threshold_boundaries():
    check, result = _numeric_status_for_counts([60, 40])
    assert check["status"] == "passed"
    assert result["can_continue"] is True

    check, _ = _numeric_status_for_counts([70, 30], warn=0.16945957207744072, block=1.0)
    assert check["status"] == "warning"

    check, result = _numeric_status_for_counts([70, 30], warn=0.10, block=0.25)
    assert check["status"] == "warning"
    assert result["can_continue"] is True

    check, result = _numeric_status_for_counts([80, 20], warn=0.10, block=0.41588830833596724)
    assert check["status"] == "failed"
    assert result["can_continue"] is False

    check, result = _numeric_status_for_counts([90, 10])
    assert check["status"] == "failed"
    assert result["can_continue"] is False


def test_major_categorical_shift_blocks_and_reports_new_categories():
    result = check_profile_drift(_profile(status_counts={"A": 10, "C": 90}), _profile())
    categorical = next(check for check in result["checks"] if check["check"] == "categorical_distance")

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert categorical["status"] == "failed"
    assert categorical["new_categories"] == ["C"]


def test_increased_null_percentage_is_still_detected():
    result = check_profile_drift(_profile(null_pct=25.0), _profile(null_pct=0.0))
    null_check = next(check for check in result["checks"] if check["check"] == "null_percent_change_points" and check["column"] == "amount")

    assert result["status"] == "failed"
    assert null_check["passed"] is False


def test_assert_no_blocking_profile_drift_only_raises_for_failed_result():
    assert_no_blocking_profile_drift({"status": "warning", "can_continue": True})

    with pytest.raises(Exception, match="blocked"):
        assert_no_blocking_profile_drift({"status": "failed", "can_continue": False})


def test_extract_numeric_distribution_bin_edges_returns_baseline_edges():
    assert extract_numeric_distribution_bin_edges(_profile()) == {"amount": [0.0, 50.0, 100.0]}


def test_extract_categorical_distribution_categories_returns_baseline_vocabulary():
    assert extract_categorical_distribution_categories(_profile()) == {"status": ["A", "B"]}


def test_profile_dataframe_distribution_options(spark_session):
    rows = [(1, 10.0, "A"), (2, 20.0, "A"), (3, 30.0, "B"), (4, 40.0, "C")]
    df = spark_session.createDataFrame(rows, "id int, amount double, status string")

    lightweight = profile_dataframe(df, "orders")
    assert "DISTRIBUTION_JSON" not in lightweight.columns

    profiled = profile_dataframe(df, "orders", include_distributions=True)
    by_column = {row["COLUMN_NAME"]: row.asDict() for row in profiled.collect()}
    assert by_column["amount"]["DISTRIBUTION_TYPE"] == "numeric"
    assert "bin_edges" in by_column["amount"]["DISTRIBUTION_JSON"]
    assert by_column["status"]["DISTRIBUTION_TYPE"] == "categorical"
    assert "category_counts" in by_column["status"]["DISTRIBUTION_JSON"]

    limited = profile_dataframe(df, "orders", include_distributions=True, distribution_columns=["status"])
    limited_by_column = {row["COLUMN_NAME"]: row.asDict() for row in limited.collect()}
    assert limited_by_column["amount"]["DISTRIBUTION_JSON"] is None
    assert limited_by_column["status"]["DISTRIBUTION_TYPE"] == "categorical"

    baseline_vocab = profile_dataframe(df, "orders", include_distributions=True, distribution_columns=["status"], categorical_categories={"status": ["A", "B"]})
    status_payload = next(row for row in baseline_vocab.collect() if row["COLUMN_NAME"] == "status")["DISTRIBUTION_JSON"]
    assert '"A"' in status_payload and '"B"' in status_payload
    assert '"new_categories"' in status_payload


def test_load_latest_profile_filters_stage_and_excludes_current_run(spark_session):
    rows = [
        ("dataset", "orders", "source", "run-1", "successful", "observed", "amount", "double", 100, 0.0, 10.0, "numeric", '{"bin_edges": [0, 1], "bin_counts": [100]}'),
        ("dataset", "orders", "target", "run-2", "successful", "observed", "amount", "double", 200, 0.0, 10.0, "numeric", '{"bin_edges": [0, 1], "bin_counts": [200]}'),
        ("dataset", "orders", "source", "run-3", "successful", "observed", "amount", "double", 300, 0.0, 10.0, "numeric", '{"bin_edges": [0, 1], "bin_counts": [300]}'),
    ]
    df = spark_session.createDataFrame(
        rows,
        "DATASET_NAME string, PROFILED_TABLE_NAME string, PROFILE_STAGE string, PROFILE_RUN_ID string, PROFILE_STATUS string, BASELINE_STATUS string, COLUMN_NAME string, DATA_TYPE string, ROW_COUNT int, NULL_PERCENT double, DISTINCT_PERCENT double, DISTRIBUTION_TYPE string, DISTRIBUTION_JSON string",
    )
    df.createOrReplaceTempView("profile_metadata_test")

    baseline = load_latest_profile(spark_session, "profile_metadata_test", "dataset", "orders", "source", exclude_run_id="run-3", baseline_mode="latest_successful")

    assert baseline["profile_stage"] == "source"
    assert baseline["row_count"] == 100


def test_load_latest_profile_selects_approved_and_does_not_fallback(spark_session):
    rows = [
        ("dataset", "orders", "source", "run-1", "successful", "approved", "amount", "double", 100, 0.0, 10.0, "numeric", '{"bin_edges": [0, 1], "bin_counts": [100]}'),
        ("dataset", "orders", "source", "run-2", "successful", "observed", "amount", "double", 200, 0.0, 10.0, "numeric", '{"bin_edges": [0, 1], "bin_counts": [200]}'),
    ]
    df = spark_session.createDataFrame(
        rows,
        "DATASET_NAME string, PROFILED_TABLE_NAME string, PROFILE_STAGE string, PROFILE_RUN_ID string, PROFILE_STATUS string, BASELINE_STATUS string, COLUMN_NAME string, DATA_TYPE string, ROW_COUNT int, NULL_PERCENT double, DISTINCT_PERCENT double, DISTRIBUTION_TYPE string, DISTRIBUTION_JSON string",
    )
    df.createOrReplaceTempView("approved_profile_metadata_test")

    approved = load_latest_profile(spark_session, "approved_profile_metadata_test", "dataset", "orders", "source", baseline_mode="approved")
    assert approved["row_count"] == 100

    none = load_latest_profile(spark_session, "approved_profile_metadata_test", "dataset", "missing", "source", baseline_mode="approved")
    assert none is None


def test_load_latest_profile_rejects_invalid_baseline_mode(spark_session):
    with pytest.raises(ValueError, match="baseline_mode"):
        load_latest_profile(spark_session, "profile_metadata_test", "dataset", "orders", "source", baseline_mode="rolling")
