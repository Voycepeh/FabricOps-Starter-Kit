"""Tests for 02_pipeline guardrail display modes."""

from datetime import datetime

import pytest

from fabricops_kit.pipeline import display_guardrail_results
from fabricops_kit.pipeline.shared import build_guardrail_detail_rows, build_guardrail_summary_rows


pytestmark = pytest.mark.unit


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


def _persisted_tables(spark_session):
    results = spark_session.createDataFrame(
        [
            ("result-old", "rule-old", "key-a", "orders", "old-run", "dq", "not_null", "failed", "error", "id", False, "old", '{"failed_count": 1, "failed_percent": 25.0, "total_count": 4}', datetime(2026, 8, 1)),
            ("result-pass", "rule-pass", "key-a", "orders", "new-run", "dq", "not_null", "passed", "error", "id", True, "Rule passed.", '{"failed_count": 0, "failed_percent": 0.0, "total_count": 4}', datetime(2026, 8, 2)),
            ("result-one", "rule-one", "key-a", "orders", "new-run", "dq", "required_when", "failed", "error", "required_value,status", False, "1 row failed", '{"failed_count": 1, "failed_percent": 25.0, "total_count": 4}', datetime(2026, 8, 2)),
            ("result-other", "rule-other", "key-b", "orders", "other-run", "dq", "not_null", "failed", "error", "id", False, "different canonical table", '{"failed_count": 9, "failed_percent": 90.0, "total_count": 10}', datetime(2026, 8, 3)),
        ],
        "guardrail_result_id string, guardrail_rule_id string, metadata_table_key string, table_name string, "
        "run_id string, guardrail_type string, rule_type string, status string, severity string, column_name string, "
        "can_continue boolean, reason string, actual_value_json string, _committed_at timestamp",
    )
    evidence = spark_session.createDataFrame(
        [
            ("row-result-one", "result-one", "rule-one", "key-a", "new-run", "required_when", '{"id":1}', '["required_value","status"]', '{"required_value":null,"status":"open"}', "required value was null"),
            ("row-result-two", "result-pass", "rule-pass", "key-a", "new-run", "not_null", '{"id":1}', '["id"]', '{"id":null}', "id was null"),
            ("row-result-old", "result-old", "rule-old", "key-a", "old-run", "not_null", '{"id":2}', '["id"]', '{"id":null}', "old failure"),
            ("row-result-other", "result-other", "rule-other", "key-b", "other-run", "not_null", '{"id":3}', '["id"]', '{"id":null}', "other table"),
        ],
        "guardrail_row_result_id string, guardrail_result_id string, guardrail_rule_id string, metadata_table_key string, "
        "run_id string, rule_type string, row_identity string, involved_columns_json string, failed_values_json string, failure_reason string",
    )
    return {
        "METADATA_GUARDRAIL_RESULTS": results,
        "METADATA_GUARDRAIL_ROW_RESULTS": evidence,
    }


def test_persisted_results_choose_one_latest_canonical_run(monkeypatch, spark_session):
    """Latest lookup scopes by canonical identity and never combines runs."""
    import fabricops_kit.pipeline.shared as shared

    tables = _persisted_tables(spark_session)
    monkeypatch.setattr(shared, "read_lakehouse_table_core", lambda table, **_kwargs: tables[table])

    views = display_guardrail_results(metadata_table_key="key-a", spark_session=spark_session)

    assert views["run_id"] == "new-run"
    summary = views["summary"].collect()
    assert {row.run_id for row in summary} == {"new-run"}
    assert {row.guardrail_result_id for row in summary} == {"result-pass", "result-one"}
    assert summary[0].status == "failed"
    failed = next(row for row in summary if row.guardrail_result_id == "result-one")
    assert (failed.failed_rows, failed.failed_percent, failed.total_count) == (1, 25.0, 4)


def test_persisted_results_explicit_run_preserves_failed_rule_grain_and_nulls(monkeypatch, spark_session):
    """Explicit execution returns every failed-row/rule pair and keeps JSON nulls."""
    import fabricops_kit.pipeline.shared as shared

    tables = _persisted_tables(spark_session)
    monkeypatch.setattr(shared, "read_lakehouse_table_core", lambda table, **_kwargs: tables[table])

    views = display_guardrail_results(
        metadata_table_key="key-a", run_id="new-run", spark_session=spark_session
    )

    rows = views["row_evidence"].collect()
    assert len(rows) == 2
    assert {row.row_identity for row in rows} == {'{"id":1}'}
    assert {row.rule_type for row in rows} == {"required_when", "not_null"}
    required = next(row for row in rows if row.rule_type == "required_when")
    assert '"required_value":null' in required.failed_values
    assert '"status":"open"' in required.failed_values


def test_persisted_results_return_clean_empty_views(monkeypatch, spark_session):
    """No result and passing runs retain stable empty evidence schemas."""
    import fabricops_kit.pipeline.shared as shared

    tables = _persisted_tables(spark_session)
    monkeypatch.setattr(shared, "read_lakehouse_table_core", lambda table, **_kwargs: tables[table])

    missing = display_guardrail_results(metadata_table_key="missing", spark_session=spark_session)
    assert missing["summary"].count() == 0
    assert missing["row_evidence"].count() == 0
    assert missing["run_id"] is None
    assert "No Guardrail Results" in missing["message"]

    passing_evidence = tables["METADATA_GUARDRAIL_ROW_RESULTS"].limit(0)
    monkeypatch.setitem(tables, "METADATA_GUARDRAIL_ROW_RESULTS", passing_evidence)
    passing = display_guardrail_results(
        metadata_table_key="key-a", run_id="new-run", spark_session=spark_session
    )
    assert passing["summary"].count() == 2
    assert passing["row_evidence"].count() == 0
    assert passing["row_evidence"].columns == [
        "rule_type", "row_identity", "involved_columns", "failed_values",
        "failure_reason", "run_id", "guardrail_result_id", "guardrail_rule_id",
    ]
