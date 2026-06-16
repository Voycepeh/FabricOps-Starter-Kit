"""Tests for 02_pipeline guardrail display modes."""

from fabricops_kit.pipeline import build_guardrail_detail_rows, build_guardrail_summary_rows, display_guardrail_results


def _bundle(**overrides):
    bundle = {
        "schema_results": {},
        "freshness_results": {},
        "stability_results": {},
        "dq_results": {},
        "catalogue_status": {},
        "summary": {"raw": True},
        "can_continue": True,
        "failed_tables": [],
    }
    bundle.update(overrides)
    return bundle


def test_summary_mode_happy_path():
    """Verify summary mode returns compact passing rows."""
    rows = build_guardrail_summary_rows(
        _bundle(
            schema_results={"orders": {"status": "passed", "can_continue": True}},
            freshness_results={"orders": {"status": "passed", "can_continue": True}},
            stability_results={"orders": {"status": "passed", "can_continue": True}},
            dq_results={"orders": {"status": "passed", "can_continue": True}},
            catalogue_status={"orders": "written"},
        )
    )

    assert rows == [
        {
            "table": "orders",
            "status": "passed",
            "failed_guardrail": "none",
            "can_continue": "yes",
            "main_reason": "All blocking guardrails passed.",
            "next_action": "Continue.",
            "schema": "passed",
            "freshness": "passed",
            "profile_behavior": "passed",
            "dq": "passed",
            "catalogue": "written",
        }
    ]


def test_summary_mode_schema_failure_reason():
    """Verify schema failure gets concise summary wording."""
    rows = build_guardrail_summary_rows(_bundle(schema_results={"orders": {"status": "failed", "can_continue": False, "missing_columns": ["order_amount"], "unexpected_columns": ["promo_code"]}}))

    assert rows[0]["status"] == "failed"
    assert rows[0]["failed_guardrail"] == "schema"
    assert rows[0]["main_reason"] == "Schema failed: missing column order_amount; unexpected column promo_code."


def test_summary_mode_freshness_failure_reason():
    """Verify freshness failure gets concise summary wording."""
    rows = build_guardrail_summary_rows(_bundle(freshness_results={"orders": {"status": "failed", "can_continue": False, "freshness_column": "order_date"}}))

    assert rows[0]["failed_guardrail"] == "freshness"
    assert rows[0]["main_reason"] == "Freshness failed: latest order_date is older than allowed lag."


def test_summary_mode_profile_baseline_created():
    """Verify profile baseline creation gets plain wording."""
    rows = build_guardrail_summary_rows(_bundle(stability_results={"customers": {"status": "baseline_created", "can_continue": True}}))

    assert rows[0]["status"] == "passed"
    assert rows[0]["main_reason"] == "Profile behavior baseline created."


def test_summary_mode_profile_static_changed():
    """Verify static profile changes hide raw hashes in summary mode."""
    rows = build_guardrail_summary_rows(_bundle(stability_results={"orders": {"status": "failed", "can_continue": False, "differences": [{"difference_type": "profile_changed", "watermark_value": "__FULL_TABLE__", "expected_profile_hash": "abc", "actual_profile_hash": "def"}]}}))

    assert rows[0]["failed_guardrail"] == "profile_behavior"
    assert rows[0]["main_reason"] == "Profile behavior failed: static data changed from accepted baseline."
    assert "abc" not in rows[0]["main_reason"]
    assert "def" not in rows[0]["main_reason"]


def test_summary_mode_profile_watermark_changed():
    """Verify changed watermark groups get plain wording."""
    rows = build_guardrail_summary_rows(_bundle(stability_results={"orders": {"status": "failed", "can_continue": False, "differences": [{"difference_type": "profile_changed", "watermark_value": "2026-06-13"}]}}))

    assert rows[0]["main_reason"] == "Profile behavior failed: previous watermark group 2026-06-13 changed."


def test_summary_mode_profile_watermark_disappeared():
    """Verify missing watermark groups get plain wording."""
    rows = build_guardrail_summary_rows(_bundle(stability_results={"orders": {"status": "failed", "can_continue": False, "differences": [{"difference_type": "missing_watermark_value", "watermark_value": "2026-06-13"}]}}))

    assert rows[0]["main_reason"] == "Profile behavior failed: previous watermark group 2026-06-13 disappeared."


def test_summary_mode_dq_failure_reason():
    """Verify DQ failure counts blocking failed rules."""
    rows = build_guardrail_summary_rows(_bundle(dq_results={"orders": {"status": "failed", "can_continue": False, "checks": [{"status": "failed", "severity": "error"}, {"status": "passed", "severity": "error"}]}}))

    assert rows[0]["failed_guardrail"] == "dq"
    assert rows[0]["main_reason"] == "DQ failed: 1 blocking DQ rule(s) failed."


def test_summary_mode_dq_warning_reason():
    """Verify DQ warning-only failures get non-blocking warning wording."""
    rows = build_guardrail_summary_rows(_bundle(dq_results={"orders": {"status": "warning", "can_continue": True, "checks": [{"status": "warning", "severity": "warning"}, {"status": "passed", "severity": "error"}]}}))

    assert rows[0]["status"] == "warning"
    assert rows[0]["failed_guardrail"] == "dq"
    assert rows[0]["main_reason"] == "DQ warning: 1 warning DQ rule(s) failed."
    details = build_guardrail_detail_rows(_bundle(dq_results={"orders": {"status": "warning", "can_continue": True, "checks": [{"status": "warning", "severity": "warning"}]}}))
    assert details[0]["reason"] == "DQ warning: 1 warning DQ rule(s) failed."


def test_detailed_mode_returns_per_guardrail_rows_with_expected_actual_reason():
    """Verify detailed rows include diagnostic fields."""
    rows = build_guardrail_detail_rows(
        _bundle(
            schema_results={"orders": {"status": "failed", "can_continue": False, "missing_columns": ["order_amount"], "unexpected_columns": ["promo_code"]}},
            freshness_results={"orders": {"status": "passed", "can_continue": True, "freshness_column": "order_date", "required_min_value": "2026-06-13", "latest_value": "2026-06-15"}},
        )
    )

    assert {row["guardrail"] for row in rows} == {"schema", "freshness"}
    schema = next(row for row in rows if row["guardrail"] == "schema")
    assert schema["reason"] == "Schema failed: missing column order_amount; unexpected column promo_code."
    assert "order_amount" in schema["expected"]
    assert "promo_code" in schema["actual"]


def test_display_modes_return_summary_detail_and_debug_without_mutation():
    """Verify display helper chooses modes and keeps raw bundle intact."""
    bundle = _bundle(schema_results={"orders": {"status": "passed", "can_continue": True}})
    original_summary = bundle["summary"]

    assert display_guardrail_results(bundle, mode="summary") == build_guardrail_summary_rows(bundle)
    assert display_guardrail_results(bundle, mode="detailed") == build_guardrail_detail_rows(bundle)
    assert display_guardrail_results(bundle, mode="debug") is original_summary
    assert bundle["summary"] is original_summary


def test_display_modes_return_spark_dataframe_when_session_supplied():
    """Verify summary and detailed modes return display-friendly Spark tables."""
    bundle = _bundle(schema_results={"orders": {"status": "passed", "can_continue": True}})

    class Spark:
        def __init__(self):
            self.rows = None

        def createDataFrame(self, rows):
            self.rows = rows
            return {"spark_rows": rows}

    spark = Spark()

    rendered = display_guardrail_results(bundle, mode="summary", spark_session=spark)

    assert rendered == {"spark_rows": build_guardrail_summary_rows(bundle)}
    assert spark.rows == build_guardrail_summary_rows(bundle)
    assert display_guardrail_results(_bundle(), mode="summary", spark_session=spark) == []
