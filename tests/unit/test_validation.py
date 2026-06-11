from __future__ import annotations
import pytest

from fabricops_kit.guardrails import enforce_profile_behavior, stop_if_failed, validate_schema

pytestmark = pytest.mark.unit


def test_validate_schema_supports_strict_allow_new_and_monitor_modes():
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


def test_enforce_profile_behavior_overwrite_accepts_profile_differences(monkeypatch):
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


def test_enforce_freshness_passes_when_latest_value_within_lag():
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
    from fabricops_kit.guardrails import enforce_freshness

    result = enforce_freshness([], None, None)

    assert result["status"] == "skipped"
    assert result["can_continue"] is True
