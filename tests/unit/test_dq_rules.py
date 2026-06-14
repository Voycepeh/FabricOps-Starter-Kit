from __future__ import annotations

import json

import pytest

import fabricops_kit.governance_review as governance
from tests.helpers import FakeSpark, framework_config

pytestmark = pytest.mark.unit


def _rule(rule_type: str, **kwargs):
    rule = {"rule_id": f"r_{rule_type}", "rule_type": rule_type, "columns": ["id"], "severity": "error", "description": "test"}
    rule.update(kwargs)
    return rule


@pytest.mark.parametrize(
    ("rule", "failed"),
    [
        (_rule("not_null", columns=["id"]), 1),
        (_rule("null_rate_below", columns=["email"], max_null_percent=10), 1),
        (_rule("non_empty_string", columns=["name"]), 2),
        (_rule("unique", columns=["id"]), 2),
        (_rule("unique_combination", columns=["id", "semester"]), 2),
        (_rule("accepted_values", columns=["status"], allowed_values=["Active", "Inactive"]), 1),
        (_rule("not_in_values", columns=["country"], blocked_values=["UNKNOWN", "N/A"]), 2),
        (_rule("between", columns=["score"], min_value=0, max_value=100), 1),
        (_rule("greater_than", columns=["amount"], value=0), 1),
        (_rule("greater_than_or_equal", columns=["credit_units"], value=0), 1),
        (_rule("less_than", columns=["risk_score"], value=1), 1),
        (_rule("less_than_or_equal", columns=["response_rate"], value=100), 1),
        (_rule("regex_match", columns=["email"], regex_pattern=r"^[^@]+@[^@]+\.[^@]+$"), 1),
        (_rule("date_not_future", columns=["birth_date"]), 1),
        (_rule("date_between", columns=["event_date"], min_value="2020-01-01", max_value="2026-12-31"), 1),
        (_rule("freshness", columns=["updated_at"], max_age_days=1000), 1),
        (_rule("max_age_days", columns=["snapshot_date"], max_age_days=1000), 1),
        (_rule("column_pair_equal", columns=["source_id", "target_id"]), 1),
        (_rule("column_a_gte_column_b", columns=["end_date", "start_date"]), 1),
        (_rule("column_a_gt_column_b", columns=["expiry_date", "start_date"]), 1),
        (_rule("required_when", columns=["approved_date"], condition="country = 'UNKNOWN'"), 1),
        (_rule("value_when", columns=["is_active"], condition="student_status = 'Graduated'", expected_value=False), 1),
        (_rule("expression_true", columns=[], expression="credits_attempted >= credits_earned"), 1),
    ],
)
def test_dq_rule_engine_supports_catalogue_rules(spark_session, rule, failed):
    df = spark_session.createDataFrame(
        [
            ("1", "2026A", "good@example.com", "Alice", "Active", "US", 50, 10, 0, 0.5, 99, "2000-01-01", "2025-01-01", "2099-01-01", "2099-01-01", "A", "A", "2026-01-02", "2026-01-01", "2026-01-02", "2026-01-01", "2026-01-01", "Graduated", False, 10, 9),
            ("1", "2026A", "bad-email", "", "Pending", "UNKNOWN", 101, 0, -1, 1.5, 101, "2999-01-01", "2019-12-31", "2000-01-01", "2000-01-01", "B", "C", "2026-01-01", "2026-01-02", "2026-01-01", "2026-01-01", None, "Graduated", True, 4, 5),
            (None, "2026B", None, None, "Inactive", "N/A", 0, 1, 1, 0.1, 100, "2001-01-01", "2026-01-01", "2026-01-01", "2026-01-01", "D", "D", "2026-01-02", "2026-01-01", "2026-01-02", "2026-01-01", None, "Active", True, 1, 1),
        ],
        "id string, semester string, email string, name string, status string, country string, score int, amount int, credit_units int, risk_score double, response_rate int, birth_date string, event_date string, updated_at string, snapshot_date string, source_id string, target_id string, end_date string, start_date string, expiry_date string, other_start_date string, approved_date string, student_status string, is_active boolean, credits_attempted int, credits_earned int",
    )
    checks = governance._run_dq_guardrail_checks(df, "students", [rule])
    assert checks[0]["failed_count"] == failed


@pytest.mark.parametrize("old_rule_type", ["unique_key", "regex_format", "value_range", "regex", "unique_compound", "compound_unique", "datatype", "referential_integrity", "custom_expression"])
def test_legacy_or_external_rule_names_fail_validation(old_rule_type):
    with pytest.raises(ValueError, match="unsupported rule_type"):
        governance._validate_dq_rules([_rule(old_rule_type, columns=["id"])])


def test_not_null_and_non_empty_string_have_distinct_semantics(spark_session):
    df = spark_session.createDataFrame([(None,), ("",), ("   ",), ("ok",)], "name string")

    not_null = _rule("not_null", columns=["name"])
    non_empty = _rule("non_empty_string", columns=["name"])

    not_null_check = governance._run_dq_guardrail_checks(df, "students", [not_null])[0]
    non_empty_check = governance._run_dq_guardrail_checks(df, "students", [non_empty])[0]

    assert not_null_check["failed_count"] == 1
    assert non_empty_check["failed_count"] == 3


def test_dq_metadata_actions_are_append_only_and_preserve_multicolumns(fake_notebookutils):
    profile_rows = [{"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "student_id"}]
    base = {"rule_id": "grain", "rule_type": "unique_combination", "columns": ["student_id", "semester"], "severity": "error", "description": "grain", "commit": True}
    rows = governance._build_dq_rule_records(
        profile_rows,
        [
            {**base, "action_type": "created"},
            {**base, "action_type": "updated", "description": "new grain"},
            {**base, "action_type": "deactivated"},
            {**base, "action_type": "reactivated"},
        ],
        config=framework_config(),
        env="dev",
        approved_by="reviewer@example.com",
    )
    assert [r["action_type"] for r in rows] == ["created", "updated", "deactivated", "reactivated"]
    assert [r["is_active"] for r in rows] == [True, True, False, True]
    assert json.loads(rows[0]["rule_parameters_json"])["columns"] == ["student_id", "semester"]
    for field in ["rule_key", "rule_id", "metadata_column_key", "metadata_table_key", "environment_name", "dataset_name", "table_name", "column_name", "rule_type", "rule_parameters_json", "severity", "description", "is_active", "review_status", "approved_by", "approved_at", "ai_suggestion_json", "action_type", "_committed_at", "_committed_by", "_workspace_name", "_notebook_name", "_metadata_lakehouse_name", "_activity_id"]:
        assert field in rows[0]


def test_latest_active_rule_resolution_and_inactive_not_enforced(spark_session):
    metadata = spark_session.createDataFrame(
        [
            {"rule_key": "k1", "rule_id": "r1", "environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "id", "rule_type": "not_null", "rule_parameters_json": json.dumps({"columns": ["id"]}), "severity": "error", "description": "old", "is_active": True, "review_status": "approved", "action_type": "created", "approved_at": "2026-01-01T00:00:00Z", "_committed_at": "2026-01-01T00:00:00Z"},
            {"rule_key": "k1", "rule_id": "r1", "environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "id", "rule_type": "not_null", "rule_parameters_json": json.dumps({"columns": ["id"]}), "severity": "error", "description": "off", "is_active": False, "review_status": "approved", "action_type": "deactivated", "approved_at": "2026-01-02T00:00:00Z", "_committed_at": "2026-01-02T00:00:00Z"},
            {"rule_key": "k2", "rule_id": "r2", "environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "status", "rule_type": "accepted_values", "rule_parameters_json": json.dumps({"columns": ["status"], "allowed_values": ["A"]}), "severity": "warning", "description": "status", "is_active": True, "review_status": "approved", "action_type": "created", "approved_at": "2026-01-01T00:00:00Z", "_committed_at": "2026-01-01T00:00:00Z"},
        ]
    )
    rules = governance._load_active_dq_rules(metadata, "orders", env_name="dev", dataset_name="sales")
    assert [r["rule_id"] for r in rules] == ["r2"]


def test_widget_display_rows_include_active_and_inactive_rules():
    rows = governance._dq_rule_display_rows([
        {"rule_id": "r1", "rule_type": "not_null", "column_name": "id", "is_active": True},
        {"rule_id": "r2", "rule_type": "unique", "column_name": "id", "is_active": False},
    ])
    assert [r["Status"] for r in rows] == ["active", "inactive"]


def test_ai_suggestion_parser_rejects_unsupported_and_keeps_drafts():
    payload = {"DQ_RULES": {"orders": [{"rule_id": "r1", "rule_type": "not_null", "columns": ["id"], "severity": "warning", "description": "draft"}]}}
    drafts = governance._parse_dq_ai_suggestions([{"response": json.dumps(payload)}], table_name="orders")
    assert drafts[0]["review_status"] == "draft"
    assert drafts[0]["is_active"] is False
    bad = {"DQ_RULES": {"orders": [{"rule_id": "bad", "rule_type": "required_columns", "columns": ["id"], "severity": "warning", "description": "bad"}]}}
    with pytest.raises(ValueError):
        governance._parse_dq_ai_suggestions([{"response": json.dumps(bad)}], table_name="orders")


def test_dq_tagged_dataframe_uses_row_level_warning_and_error_status(spark_session):
    df = spark_session.createDataFrame(
        [(None, "bad", -1), ("ok", "bad", -1), ("ok", "good", 1), (None, "good", -1)],
        "id string, status string, amount int",
    )
    rules = [
        _rule("not_null", rule_id="id_required", columns=["id"], severity="error"),
        _rule("accepted_values", rule_id="status_allowed", columns=["status"], allowed_values=["good"], severity="warning"),
        _rule("greater_than", rule_id="amount_positive", columns=["amount"], value=0, severity="warning"),
    ]

    rows = governance._dq_tagged_dataframe(df, rules).select("id", "status", "amount", "_dq_failed_rules", "_dq_check_status").collect()
    by_values = {(row["id"], row["status"], row["amount"]): row.asDict() for row in rows}

    assert by_values[(None, "bad", -1)]["_dq_check_status"] == "failed"
    assert by_values[("ok", "bad", -1)]["_dq_check_status"] == "warning"
    assert by_values[("ok", "good", 1)]["_dq_check_status"] == "passed"
    assert by_values[(None, "good", -1)]["_dq_check_status"] == "failed"


def test_value_when_uses_null_safe_expected_value_comparison(spark_session):
    df = spark_session.createDataFrame(
        [
            ("Graduated", True, None, None, None),
            ("Graduated", False, None, None, None),
            ("Graduated", False, None, "x", None),
            ("Graduated", False, None, None, "x"),
            ("Active", True, "x", "y", None),
        ],
        "student_status string, is_active boolean, expected_null string, actual_non_null string, actual_null string",
    )
    rules = [
        _rule("value_when", rule_id="graduated_inactive", columns=["is_active"], condition="student_status = 'Graduated'", expected_value=False),
        _rule("value_when", rule_id="null_expected", columns=["expected_null"], condition="student_status = 'Graduated'", expected_value=None),
        _rule("value_when", rule_id="nonnull_expected", columns=["actual_null"], condition="student_status = 'Graduated'", expected_value="x"),
    ]

    checks = {check["rule_id"]: check for check in governance._run_dq_guardrail_checks(df, "students", rules)}

    assert checks["graduated_inactive"]["failed_count"] == 1
    assert checks["null_expected"]["failed_count"] == 0
    assert checks["nonnull_expected"]["failed_count"] == 3

    null_mismatch = _rule("value_when", rule_id="null_mismatch", columns=["actual_non_null"], condition="student_status = 'Graduated'", expected_value=None)
    assert governance._run_dq_guardrail_checks(df, "students", [null_mismatch])[0]["failed_count"] == 1


def test_cross_column_rules_use_consistent_null_behavior(spark_session):
    df = spark_session.createDataFrame(
        [(None, None), (None, 1), (1, None), (1, 1), (2, 1), (1, 2)],
        "a int, b int",
    )

    equal_check = governance._run_dq_guardrail_checks(df, "pairs", [_rule("column_pair_equal", columns=["a", "b"])])[0]
    gte_check = governance._run_dq_guardrail_checks(df, "pairs", [_rule("column_a_gte_column_b", columns=["a", "b"])])[0]
    gt_check = governance._run_dq_guardrail_checks(df, "pairs", [_rule("column_a_gt_column_b", columns=["a", "b"])])[0]

    assert equal_check["failed_count"] == 4
    assert gte_check["failed_count"] == 3
    assert gt_check["failed_count"] == 4


def test_enforce_dq_rules_loads_only_approved_active_metadata_rules(monkeypatch, spark_session):
    df = spark_session.createDataFrame([(1, "ok"), (None, "ok")], "id int, status string")
    metadata = spark_session.createDataFrame(
        [
            {
                "rule_key": "approved-active",
                "rule_id": "id_required",
                "environment_name": "dev",
                "dataset_name": "sales",
                "table_name": "orders",
                "column_name": "id",
                "rule_type": "not_null",
                "rule_parameters_json": json.dumps({"columns": ["id"]}),
                "severity": "error",
                "description": "id required",
                "is_active": True,
                "review_status": "approved",
                "action_type": "created",
                "approved_at": "2026-06-14T00:00:00Z",
                "_committed_at": "2026-06-14T00:00:00Z",
            },
            {
                "rule_key": "draft-active",
                "rule_id": "draft_rule",
                "environment_name": "dev",
                "dataset_name": "sales",
                "table_name": "orders",
                "column_name": "status",
                "rule_type": "accepted_values",
                "rule_parameters_json": json.dumps({"columns": ["status"], "allowed_values": ["ok"]}),
                "severity": "error",
                "description": "draft should not run",
                "is_active": True,
                "review_status": "draft",
                "action_type": "created",
                "approved_at": "2026-06-14T00:00:00Z",
                "_committed_at": "2026-06-14T00:00:00Z",
            },
            {
                "rule_key": "approved-inactive",
                "rule_id": "inactive_rule",
                "environment_name": "dev",
                "dataset_name": "sales",
                "table_name": "orders",
                "column_name": "status",
                "rule_type": "accepted_values",
                "rule_parameters_json": json.dumps({"columns": ["status"], "allowed_values": ["bad"]}),
                "severity": "error",
                "description": "inactive should not run",
                "is_active": False,
                "review_status": "approved",
                "action_type": "deactivated",
                "approved_at": "2026-06-14T00:00:00Z",
                "_committed_at": "2026-06-15T00:00:00Z",
            },
        ]
    )

    reads = []

    def fake_read(config, env, target, table, **kwargs):
        reads.append((env, target, table, kwargs))
        return metadata

    monkeypatch.setattr(governance, "read_lakehouse_table", fake_read)

    result = governance.enforce_dq_rules(df, framework_config(), "dev", "sales", "orders", spark_session=spark_session)

    assert reads[0][0:3] == ("dev", "metadata", governance.DQ_RULES_TABLE)
    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert [check["rule_id"] for check in result["checks"]] == ["id_required"]
    assert result["checks"][0]["failed_count"] == 1
    assert result["summary"]["rule_count"] == 1
    assert result["summary"]["failed_rule_count"] == 1
    assert "_dq_check_status" in result["dataframe"].columns


def test_enforce_dq_rules_returns_passed_when_no_approved_active_rules(monkeypatch, spark_session):
    df = spark_session.createDataFrame([(1, "ok")], "id int, status string")
    metadata = spark_session.createDataFrame(
        [
            {
                "rule_key": "draft-only",
                "rule_id": "draft_rule",
                "environment_name": "dev",
                "dataset_name": "sales",
                "table_name": "orders",
                "column_name": "id",
                "rule_type": "not_null",
                "rule_parameters_json": json.dumps({"columns": ["id"]}),
                "severity": "error",
                "description": "draft",
                "is_active": True,
                "review_status": "draft",
                "action_type": "created",
                "approved_at": "2026-06-14T00:00:00Z",
                "_committed_at": "2026-06-14T00:00:00Z",
            }
        ]
    )
    monkeypatch.setattr(governance, "read_lakehouse_table", lambda *args, **kwargs: metadata)

    result = governance.enforce_dq_rules(df, framework_config(), "dev", "sales", "orders", spark_session=spark_session)

    assert result["status"] == "passed"
    assert result["can_continue"] is True
    assert result["checks"] == []
    assert result["summary"]["rule_count"] == 0
    assert "_dq_check_status" in result["dataframe"].columns
