"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations
import pytest

from fabricops_kit.guardrails import enforce_profile_behavior, stop_if_failed, validate_schema

pytestmark = pytest.mark.unit


def test_validate_schema_supports_strict_allow_new_and_monitor_modes():
    """Verify validate schema supports strict allow new and monitor modes."""
    class FakeFrame:
        def __init__(self, dtypes):
            self.dtypes = dtypes
            self.columns = [name for name, _dtype in dtypes]

    df = FakeFrame([("id", "bigint"), ("amount", "double"), ("new_col", "string")])
    expected = {"id": "bigint", "amount": "double"}

    strict = validate_schema(df, expected, preset="strict")
    allow_new = validate_schema(df, expected, preset="allow_new_columns")
    monitor = validate_schema(FakeFrame([("id", "bigint")]), expected, preset="monitor_only")

    assert strict["status"] == "failed"
    assert strict["can_continue"] is False
    assert allow_new["status"] == "warning"
    assert allow_new["can_continue"] is True
    assert monitor["status"] == "warning"
    assert monitor["can_continue"] is True
    with pytest.raises(ValueError, match="preset"):
        validate_schema(df, expected, preset="unknown")


def _profile_rows(row_count: int, minimum: str = "2026-01-01", maximum: str = "2026-01-31") -> list[dict[str, object]]:
    return [
        {
            "table_name": "orders",
            "column_name": "business_date",
            "data_type": "date",
            "row_count": row_count,
            "min_value": minimum,
            "max_value": maximum,
        }
    ]


def _catalogue_row(row_count: int, minimum: str = "2026-01-01", maximum: str = "2026-01-31") -> dict[str, object]:
    return {
        "dataset_name": "sales",
        "table_name": "orders",
        "profile_stage": "source",
        "profile_status": "success",
        "stability_status": "passed",
        "load_behavior": "append",
        "profile_run_id": "previous-run",
        "profiled_at": "2026-01-01T00:00:00+00:00",
        "column_name": "business_date",
        "row_count": row_count,
        "min_value": minimum,
        "max_value": maximum,
    }


def test_enforce_profile_behavior_append_passes_when_row_count_grows(monkeypatch):
    """Verify enforce profile behavior append passes when row count grows."""
    from fabricops_kit import data_profiling

    monkeypatch.setattr(data_profiling, "profile_dataframe", lambda *args, **kwargs: _profile_rows(12))

    result = enforce_profile_behavior(
        None,
        object(),
        "METADATA_DATA_CATALOGUE",
        "sales",
        "orders",
        stage="source",
        run_id="current-run",
        load_behavior="append",
        watermark_column="business_date",
        catalogue_df=[_catalogue_row(10)],
    )

    assert result["status"] == "passed"
    assert result["can_continue"] is True


def test_enforce_profile_behavior_append_fails_when_row_count_drops(monkeypatch):
    """Verify enforce profile behavior append fails when row count drops."""
    from fabricops_kit import data_profiling

    monkeypatch.setattr(data_profiling, "profile_dataframe", lambda *args, **kwargs: _profile_rows(9))

    result = enforce_profile_behavior(
        None,
        object(),
        "METADATA_DATA_CATALOGUE",
        "sales",
        "orders",
        stage="source",
        run_id="current-run",
        load_behavior="append",
        watermark_column="business_date",
        catalogue_df=[_catalogue_row(10)],
    )

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert "row_count" in result["stability_difference_summary"]


def test_enforce_profile_behavior_append_fails_when_watermark_min_moves_forward(monkeypatch):
    """Verify enforce profile behavior append fails when watermark min moves forward."""
    from fabricops_kit import data_profiling

    monkeypatch.setattr(data_profiling, "profile_dataframe", lambda *args, **kwargs: _profile_rows(12, minimum="2026-01-02"))

    result = enforce_profile_behavior(
        None,
        object(),
        "METADATA_DATA_CATALOGUE",
        "sales",
        "orders",
        stage="source",
        run_id="current-run",
        load_behavior="append",
        watermark_column="business_date",
        catalogue_df=[_catalogue_row(10, minimum="2026-01-01")],
    )

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert "watermark_min" in result["stability_difference_summary"]



def test_enforce_profile_behavior_does_not_use_non_watermark_row_for_watermark_comparison(monkeypatch):
    """Verify enforce profile behavior does not use non watermark row for watermark comparison."""
    from fabricops_kit import data_profiling

    monkeypatch.setattr(data_profiling, "profile_dataframe", lambda *args, **kwargs: _profile_rows(12, minimum="2026-01-02", maximum="2026-01-31"))
    non_watermark_previous = {
        **_catalogue_row(10, minimum="2026-01-01", maximum="2026-01-31"),
        "column_name": "customer_id",
    }

    result = enforce_profile_behavior(
        None,
        object(),
        "METADATA_DATA_CATALOGUE",
        "sales",
        "orders",
        stage="source",
        run_id="current-run",
        load_behavior="append",
        watermark_column="business_date",
        catalogue_df=[non_watermark_previous],
    )

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert result["baseline_row_count"] == 10
    assert result["baseline_watermark_min_value"] == ""
    assert "watermark_comparison" in result["stability_difference_summary"]
    assert "No previous accepted profile row" in result["stability_difference_summary"]


def test_enforce_profile_behavior_reuses_current_profile_when_supplied(monkeypatch):
    """Verify enforce profile behavior reuses current profile when supplied."""
    from fabricops_kit import data_profiling

    def fail_profile(*args, **kwargs):
        raise AssertionError("profile_dataframe should not be called when current_profile is provided")

    monkeypatch.setattr(data_profiling, "profile_dataframe", fail_profile)

    result = enforce_profile_behavior(
        None,
        object(),
        "METADATA_DATA_CATALOGUE",
        "sales",
        "orders",
        stage="source",
        run_id="current-run",
        load_behavior="append",
        watermark_column="business_date",
        catalogue_df=[_catalogue_row(10)],
        current_profile=_profile_rows(12),
    )

    assert result["status"] == "passed"
    assert result["row_count"] == 12

def test_enforce_profile_behavior_overwrite_accepts_profile_differences(monkeypatch):
    """Verify enforce profile behavior overwrite accepts profile differences."""
    from fabricops_kit import data_profiling

    monkeypatch.setattr(data_profiling, "profile_dataframe", lambda *args, **kwargs: _profile_rows(1, minimum="2026-02-01", maximum="2026-02-02"))

    result = enforce_profile_behavior(
        None,
        object(),
        "METADATA_DATA_CATALOGUE",
        "sales",
        "orders",
        stage="target",
        run_id="current-run",
        load_behavior="overwrite",
        watermark_column="business_date",
        catalogue_df=[{**_catalogue_row(100), "profile_stage": "target", "load_behavior": "overwrite"}],
    )

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert result["stability_difference_summary"] == ""


def test_enforce_profile_behavior_skip_returns_skipped_and_can_continue(monkeypatch):
    """Verify enforce profile behavior skip returns skipped and can continue."""
    from fabricops_kit import data_profiling

    monkeypatch.setattr(data_profiling, "profile_dataframe", lambda *args, **kwargs: _profile_rows(1))

    result = enforce_profile_behavior(
        None,
        object(),
        "METADATA_DATA_CATALOGUE",
        "sales",
        "orders",
        stage="source",
        run_id="current-run",
        load_behavior="skip",
        watermark_column="business_date",
        catalogue_df=[_catalogue_row(10)],
    )

    assert result["status"] == "skipped"
    assert result["can_continue"] is True
    assert result["stability_check_enabled"] is False



def test_profile_row_count_falls_back_to_first_normalized_column_row_count():
    """Verify profile row count falls back to first normalized column row count."""
    from fabricops_kit.guardrails import _profile_row_count

    result = _profile_row_count({"columns": [{"column_name": "business_date", "row_count": "42"}]})

    assert result == 42


def test_profile_row_count_returns_none_for_invalid_row_count():
    """Verify profile row count returns none for invalid row count."""
    from fabricops_kit.guardrails import _profile_row_count

    result = _profile_row_count({"row_count": "not-a-number", "columns": [{"row_count": "also-invalid"}]})

    assert result is None

def test_enforce_freshness_passes_when_latest_value_within_lag():
    """Verify enforce freshness passes when latest value within lag."""
    from fabricops_kit.guardrails import enforce_freshness

    result = enforce_freshness(
        [{"business_date": "2026-06-10"}],
        "business_date",
        1,
        severity="blocking",
        reference_date="2026-06-11",
    )

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert result["latest_value"] == "2026-06-10"
    assert result["required_min_value"] == "2026-06-10"


def test_enforce_freshness_blocks_when_latest_value_is_stale():
    """Verify enforce freshness blocks when latest value is stale."""
    from fabricops_kit.guardrails import enforce_freshness

    result = enforce_freshness(
        [{"business_date": "2026-06-09"}],
        "business_date",
        1,
        severity="blocking",
        reference_date="2026-06-11",
    )

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert result["freshness_status"] == "failed"
    assert "older than allowed lag" in result["message"]


def test_enforce_freshness_warns_when_stale_warning_severity():
    """Verify enforce freshness warns when stale warning severity."""
    from fabricops_kit.guardrails import enforce_freshness

    result = enforce_freshness(
        [{"business_date": "2026-06-09"}],
        "business_date",
        1,
        severity="warning",
        reference_date="2026-06-11",
    )

    assert result["status"] == "warning"
    assert result["can_continue"] is True


def test_enforce_freshness_skips_when_column_not_configured():
    """Verify enforce freshness skips when column not configured."""
    from fabricops_kit.guardrails import enforce_freshness

    result = enforce_freshness([], None, None)

    assert result["status"] == "skipped"
    assert result["can_continue"] is True


def test_profile_behavior_static_data_baseline_created_and_unchanged_passes(spark_session):
    """Verify static profile behavior creates and reuses a full-table baseline."""
    df = spark_session.createDataFrame([(1, "a")], "id int, name string")
    first = enforce_profile_behavior(
        spark_session, df, "METADATA_DATA_CATALOGUE", "sales", "customers",
        stage="source", run_id="run-1", load_behavior="static_data", catalogue_df=[]
    )
    assert first["status"] == "baseline_created"
    baseline = {
        "environment_name": "", "dataset_name": "sales", "table_name": "customers",
        "guardrail_type": "profile_behavior", "watermark_column": "", "watermark_value": "__FULL_TABLE__",
        "profile_hash": first["profile_hash"], "profile_status": "success", "stability_status": "passed",
        "profile_run_id": "run-1", "row_count": first["row_count"],
    }
    second = enforce_profile_behavior(
        spark_session, df, "METADATA_DATA_CATALOGUE", "sales", "customers",
        stage="source", run_id="run-2", load_behavior="static_data", catalogue_df=[baseline]
    )
    assert second["status"] == "passed"
    assert second["can_continue"] is True


def test_profile_behavior_static_data_changed_warns_when_warning_severity(spark_session):
    """Verify static profile behavior returns warnings for changed warning rules."""
    df = spark_session.createDataFrame([(1, "a")], "id int, name string")
    baseline_result = enforce_profile_behavior(
        spark_session, df, "METADATA_DATA_CATALOGUE", "sales", "customers",
        stage="source", run_id="run-1", load_behavior="static_data", catalogue_df=[]
    )
    changed = spark_session.createDataFrame([(1, "a"), (2, "b")], "id int, name string")
    result = enforce_profile_behavior(
        spark_session, changed, "METADATA_DATA_CATALOGUE", "sales", "customers",
        stage="source", run_id="run-2", load_behavior="static_data", severity="warning",
        catalogue_df=[{"dataset_name": "sales", "table_name": "customers", "watermark_column": "", "watermark_value": "__FULL_TABLE__", "profile_hash": baseline_result["profile_hash"], "profile_status": "success", "stability_status": "passed"}],
    )
    assert result["status"] == "warning"
    assert result["can_continue"] is True
    assert "Review and approve" in result["message"]


def test_profile_behavior_changing_data_baseline_new_changed_and_missing_groups(spark_session):
    """Verify changing profile behavior handles new, changed, and missing groups."""
    df = spark_session.createDataFrame([(1, "2026-06-14"), (2, "2026-06-15")], "id int, business_date string")
    baseline = enforce_profile_behavior(
        spark_session, df, "METADATA_DATA_CATALOGUE", "sales", "orders",
        stage="source", run_id="run-1", load_behavior="changing_data", watermark_column="business_date", catalogue_df=[]
    )
    assert baseline["status"] == "baseline_created"
    baseline_rows = [
        {"dataset_name": "sales", "table_name": "orders", "guardrail_type": "profile_behavior", "watermark_column": row["watermark_column"], "watermark_value": row["watermark_value"], "profile_hash": row["profile_hash"], "profile_status": "success", "stability_status": "passed", "profile_run_id": "run-1"}
        for row in baseline["profile_evidence_rows"]
    ]
    with_new = spark_session.createDataFrame([(1, "2026-06-14"), (2, "2026-06-15"), (3, "2026-06-16")], "id int, business_date string")
    assert enforce_profile_behavior(spark_session, with_new, "METADATA_DATA_CATALOGUE", "sales", "orders", stage="source", run_id="run-2", load_behavior="changing_data", watermark_column="business_date", catalogue_df=baseline_rows)["status"] == "passed"
    changed_previous = spark_session.createDataFrame([(1, "2026-06-14"), (9, "2026-06-14"), (2, "2026-06-15")], "id int, business_date string")
    failed = enforce_profile_behavior(spark_session, changed_previous, "METADATA_DATA_CATALOGUE", "sales", "orders", stage="source", run_id="run-3", load_behavior="changing_data", watermark_column="business_date", catalogue_df=baseline_rows)
    assert failed["status"] == "failed"
    assert "profile_changed" in failed["stability_difference_summary"]
    missing = spark_session.createDataFrame([(1, "2026-06-14")], "id int, business_date string")
    missing_result = enforce_profile_behavior(spark_session, missing, "METADATA_DATA_CATALOGUE", "sales", "orders", stage="source", run_id="run-4", load_behavior="changing_data", watermark_column="business_date", catalogue_df=baseline_rows)
    assert missing_result["status"] == "failed"
    assert "missing_watermark_value" in missing_result["stability_difference_summary"]
