import pytest

from fabricops_kit import monitor_data_changes, profile_dataframe
from fabricops_kit import data_profiling
from fabricops_kit import drift
from fabricops_kit.drift import _check_profile_drift, _extract_categorical_distribution_categories, _extract_numeric_distribution_bin_edges


def _profile(row_count=100, amount_counts=None, status_counts=None, null_pct=0.0, stage="source"):
    amount_counts = amount_counts if amount_counts is not None else [50, 50]
    status_counts = status_counts if status_counts is not None else {"A": 50, "B": 50}
    return {
        "dataset_name": "dataset",
        "table_name": "orders",
        "profile_stage": stage,
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
    result = _check_profile_drift(_profile(), None)

    assert result == {"status": "no_baseline", "can_continue": True, "checks": [], "message": "No baseline profile provided."}


def test_stable_numeric_and_categorical_profile_passes():
    result = _check_profile_drift(_profile(), _profile())

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert next(check for check in result["checks"] if check["check"] == "numeric_psi")["status"] == "passed"
    assert next(check for check in result["checks"] if check["check"] == "categorical_distance")["status"] == "passed"


def test_moderate_numeric_shift_warns_without_blocking():
    result = _check_profile_drift(_profile(amount_counts=[70, 30]), _profile())
    numeric = next(check for check in result["checks"] if check["check"] == "numeric_psi")

    assert result["status"] == "warning"
    assert result["can_continue"] is True
    assert numeric["status"] == "warning"
    assert numeric["passed"] is True


def test_major_numeric_shift_blocks():
    result = _check_profile_drift(_profile(amount_counts=[90, 10]), _profile())
    numeric = next(check for check in result["checks"] if check["check"] == "numeric_psi")

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert numeric["status"] == "failed"
    assert numeric["passed"] is False


def _numeric_status_for_counts(counts, *, warn=0.10, block=0.25):
    result = _check_profile_drift(_profile(amount_counts=counts), _profile(), policy={"warn_numeric_psi": warn, "block_numeric_psi": block})
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
    result = _check_profile_drift(_profile(status_counts={"A": 10, "C": 90}), _profile())
    categorical = next(check for check in result["checks"] if check["check"] == "categorical_distance")

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert categorical["status"] == "failed"
    assert categorical["new_categories"] == ["C"]


def test_increased_null_percentage_is_still_detected():
    result = _check_profile_drift(_profile(null_pct=25.0), _profile(null_pct=0.0))
    null_check = next(check for check in result["checks"] if check["check"] == "null_percent_change_points" and check["column"] == "amount")

    assert result["status"] == "failed"
    assert null_check["passed"] is False


def test_internal_distribution_extractors_return_baseline_comparison_inputs():
    assert _extract_numeric_distribution_bin_edges(_profile()) == {"amount": [0.0, 50.0, 100.0]}
    assert _extract_categorical_distribution_categories(_profile()) == {"status": ["A", "B"]}


def test_monitor_data_changes_changing_data_selects_latest_successful(monkeypatch):
    calls = {}

    def fake_load(*args, **kwargs):
        calls.update(kwargs)
        return _profile()

    monkeypatch.setattr(drift, "_load_latest_profile", fake_load)
    monkeypatch.setattr(data_profiling, "profile_dataframe", lambda *args, **kwargs: _profile(amount_counts=[60, 40]))

    result = monitor_data_changes(object(), object(), "metadata", "dataset", "orders", stage="source", preset="changing_data", exclude_run_id="run-1")

    assert calls["baseline_mode"] == "latest_successful"
    assert calls["profile_stage"] == "source"
    assert result["baseline"] is not None
    assert result["result"]["can_continue"] is True


def test_monitor_data_changes_fixed_data_selects_approved_without_fallback(monkeypatch):
    calls = {}

    def fake_load(*args, **kwargs):
        calls.update(kwargs)
        return None

    monkeypatch.setattr(drift, "_load_latest_profile", fake_load)
    monkeypatch.setattr(data_profiling, "profile_dataframe", lambda *args, **kwargs: _profile())

    result = monitor_data_changes(object(), object(), "metadata", "dataset", "orders", stage="target", preset="fixed_data")

    assert calls["baseline_mode"] == "approved"
    assert calls["profile_stage"] == "target"
    assert result["baseline"] is None
    assert result["result"]["status"] == "no_baseline"
    assert result["result"]["can_continue"] is True


def test_monitor_data_changes_monitor_changing_data_never_blocks(monkeypatch):
    calls = {}

    def fake_load(*args, **kwargs):
        calls.update(kwargs)
        return _profile()

    monkeypatch.setattr(drift, "_load_latest_profile", fake_load)
    monkeypatch.setattr(data_profiling, "profile_dataframe", lambda *args, **kwargs: _profile(amount_counts=[90, 10]))

    result = monitor_data_changes(object(), object(), "metadata", "dataset", "orders", stage="source", preset="monitor_changing_data")

    assert calls["baseline_mode"] == "latest_successful"
    assert result["result"]["status"] == "warning"
    assert result["result"]["can_continue"] is True
    assert result["result"]["monitor_only"] is True


def test_monitor_data_changes_monitor_fixed_data_uses_approved_and_never_blocks(monkeypatch):
    calls = {}

    def fake_load(*args, **kwargs):
        calls.update(kwargs)
        return _profile()

    monkeypatch.setattr(drift, "_load_latest_profile", fake_load)
    monkeypatch.setattr(data_profiling, "profile_dataframe", lambda *args, **kwargs: _profile(amount_counts=[90, 10]))

    result = monitor_data_changes(object(), object(), "metadata", "dataset", "orders", stage="target", preset="monitor_fixed_data")

    assert calls["baseline_mode"] == "approved"
    assert calls["profile_stage"] == "target"
    assert result["result"]["status"] == "warning"
    assert result["result"]["can_continue"] is True
    assert result["result"]["monitor_only"] is True


def test_monitor_data_changes_policy_overrides_merge_with_preset_defaults(monkeypatch):
    monkeypatch.setattr(drift, "_load_latest_profile", lambda *args, **kwargs: _profile())
    monkeypatch.setattr(data_profiling, "profile_dataframe", lambda *args, **kwargs: _profile(amount_counts=[70, 30]))

    result = monitor_data_changes(
        object(),
        object(),
        "metadata",
        "dataset",
        "orders",
        stage="source",
        preset="changing_data",
        policy_overrides={"block_numeric_psi": 0.30},
    )

    assert result["result"]["policy"]["warn_numeric_psi"] == 0.10
    assert result["result"]["policy"]["block_numeric_psi"] == 0.30


def test_monitor_data_changes_rejects_non_threshold_overrides():
    with pytest.raises(ValueError, match="threshold policy keys"):
        monitor_data_changes(
            object(),
            object(),
            "metadata",
            "dataset",
            "orders",
            stage="source",
            preset="changing_data",
            policy_overrides={"baseline_mode": "approved"},
        )


def test_monitor_data_changes_invalid_preset_errors():
    with pytest.raises(ValueError, match="preset must be one of"):
        monitor_data_changes(object(), object(), "metadata", "dataset", "orders", stage="source", preset="unknown")


def test_source_and_target_stages_remain_isolated(monkeypatch):
    stages = []
    monkeypatch.setattr(drift, "_load_latest_profile", lambda *args, **kwargs: stages.append(kwargs["profile_stage"]) or _profile(stage=kwargs["profile_stage"]))
    monkeypatch.setattr(data_profiling, "profile_dataframe", lambda *args, **kwargs: _profile())

    monitor_data_changes(object(), object(), "metadata", "dataset", "orders", stage="source", preset="changing_data")
    monitor_data_changes(object(), object(), "metadata", "dataset", "orders", stage="target", preset="changing_data")

    assert stages == ["source", "target"]


def test_profile_dataframe_distribution_options(spark_session):
    rows = [(1, 10.0, "A"), (2, 20.0, "A"), (3, 30.0, "B"), (4, 40.0, "C")]
    df = spark_session.createDataFrame(rows, "id int, amount double, status string")

    lightweight = profile_dataframe(df, "orders")
    assert "DISTRIBUTION_JSON" not in lightweight.columns

    profiled = profile_dataframe(df, "orders", include_distributions=True)
    by_column = {row["COLUMN_NAME"]: row.asDict() for row in profiled.collect()}
    assert by_column["amount"]["DISTRIBUTION_TYPE"] == "numeric"
    assert by_column["status"]["DISTRIBUTION_TYPE"] == "categorical"

    baseline_vocab = profile_dataframe(df, "orders", include_distributions=True, distribution_columns=["status"], categorical_categories={"status": ["A", "B"]})
    status_row = next(row.asDict() for row in baseline_vocab.collect() if row["COLUMN_NAME"] == "status")
    assert '"new_categories": ["C"]' in status_row["DISTRIBUTION_JSON"]
