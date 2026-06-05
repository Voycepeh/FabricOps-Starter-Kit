import pytest

from fabricops_kit import profile_dataframe
from fabricops_kit.drift import (
    assert_no_blocking_profile_drift,
    check_profile_drift,
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
    result = check_profile_drift(_profile(amount_counts=[65, 35]), _profile())
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


def test_load_latest_profile_filters_stage_and_excludes_current_run(spark_session):
    rows = [
        ("dataset", "orders", "source", "run-1", "amount", "double", 100, 0.0, 10.0, "numeric", '{"bin_edges": [0, 1], "bin_counts": [100]}'),
        ("dataset", "orders", "target", "run-2", "amount", "double", 200, 0.0, 10.0, "numeric", '{"bin_edges": [0, 1], "bin_counts": [200]}'),
        ("dataset", "orders", "source", "run-3", "amount", "double", 300, 0.0, 10.0, "numeric", '{"bin_edges": [0, 1], "bin_counts": [300]}'),
    ]
    df = spark_session.createDataFrame(
        rows,
        "DATASET_NAME string, PROFILED_TABLE_NAME string, PROFILE_STAGE string, PROFILE_RUN_ID string, COLUMN_NAME string, DATA_TYPE string, ROW_COUNT int, NULL_PERCENT double, DISTINCT_PERCENT double, DISTRIBUTION_TYPE string, DISTRIBUTION_JSON string",
    )
    df.createOrReplaceTempView("profile_metadata_test")

    baseline = load_latest_profile(spark_session, "profile_metadata_test", "dataset", "orders", "source", exclude_run_id="run-3")

    assert baseline["profile_stage"] == "source"
    assert baseline["row_count"] == 100
