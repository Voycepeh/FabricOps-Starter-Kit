"""Test FabricOps behavior and reference contracts."""

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
    """Verify dq rule engine supports catalogue rules."""
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
    """Verify legacy or external rule names fail validation."""
    with pytest.raises(ValueError, match="unsupported rule_type"):
        governance._validate_dq_rules([_rule(old_rule_type, columns=["id"])])


def test_not_null_and_non_empty_string_have_distinct_semantics(spark_session):
    """Verify not null and non empty string have distinct semantics."""
    df = spark_session.createDataFrame([(None,), ("",), ("   ",), ("ok",)], "name string")

    not_null = _rule("not_null", columns=["name"])
    non_empty = _rule("non_empty_string", columns=["name"])

    not_null_check = governance._run_dq_guardrail_checks(df, "students", [not_null])[0]
    non_empty_check = governance._run_dq_guardrail_checks(df, "students", [non_empty])[0]

    assert not_null_check["failed_count"] == 1
    assert non_empty_check["failed_count"] == 3


def test_dq_metadata_actions_are_append_only_and_preserve_multicolumns(fake_notebookutils):
    """Verify dq metadata actions are append only and preserve multicolumns."""
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
    for field in ["rule_key", "rule_id", "metadata_column_key", "metadata_table_key", "environment_name", "dataset_name", "table_name", "column_name", "rule_type", "rule_parameters_json", "severity", "description", "is_active", "review_status", "approved_by", "approved_at", "suggestion_json", "action_type", "_committed_at", "_committed_by", "_workspace_name", "_notebook_name", "_metadata_lakehouse_name", "_activity_id"]:
        assert field in rows[0]


def test_latest_active_rule_resolution_and_inactive_not_enforced(spark_session):
    """Verify latest active rule resolution and inactive not enforced."""
    metadata = spark_session.createDataFrame(
        [
            {"rule_key": "k1", "rule_id": "r1", "environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "id", "rule_type": "not_null", "rule_parameters_json": json.dumps({"columns": ["id"]}), "severity": "error", "description": "old", "is_active": True, "review_status": "governance_approved", "action_type": "created", "approved_at": "2026-01-01T00:00:00Z", "_committed_at": "2026-01-01T00:00:00Z"},
            {"rule_key": "k1", "rule_id": "r1", "environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "id", "rule_type": "not_null", "rule_parameters_json": json.dumps({"columns": ["id"]}), "severity": "error", "description": "off", "is_active": False, "review_status": "governance_approved", "action_type": "deactivated", "approved_at": "2026-01-02T00:00:00Z", "_committed_at": "2026-01-02T00:00:00Z"},
            {"rule_key": "k2", "rule_id": "r2", "environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "status", "rule_type": "accepted_values", "rule_parameters_json": json.dumps({"columns": ["status"], "allowed_values": ["A"]}), "severity": "warning", "description": "status", "is_active": True, "review_status": "governance_approved", "action_type": "created", "approved_at": "2026-01-01T00:00:00Z", "_committed_at": "2026-01-01T00:00:00Z"},
        ]
    )
    rules = governance._load_active_dq_rules(metadata, "orders", env_name="dev", dataset_name="sales")
    assert [r["rule_id"] for r in rules] == ["r2"]



def test_governance_metadata_schemas_use_catalogue_for_profile_history():
    """Verify guardrail schemas keep rules/results and use catalogue profile evidence."""
    schemas = governance._get_governance_metadata_schemas()

    assert governance.GUARDRAIL_RULES_TABLE in schemas
    assert governance.GUARDRAIL_RESULTS_TABLE in schemas
    assert "METADATA_GUARDRAIL_PROFILES" not in schemas
    assert "METADATA_GUARDRAIL_BASELINE_EVENTS" not in schemas
    assert not hasattr(governance, "GUARDRAIL_BASELINE_EVENT_TYPES")
    assert governance.GUARDRAIL_TYPES == ["schema", "freshness", "profile_behavior", "dq"]
    assert "governance_approved" in governance.GUARDRAIL_REVIEW_STATUSES
    assert {"guardrail_type", "review_status", "source_notebook_type", "superseded_by_rule_key"}.issubset(
        set(schemas[governance.GUARDRAIL_RULES_TABLE].fieldNames())
    )
    catalogue_fields = set(schemas[governance.CATALOGUE_TABLE].fieldNames())
    assert {
        "watermark_column",
        "watermark_value",
        "profile_hash",
        "profile_payload_json",
        "row_count",
        "null_percent",
    }.issubset(catalogue_fields)
    assert {
        "baseline_status",
        "source_schema_check",
        "target_schema_check",
        "dq_status",
        "dq_rule_count",
        "dq_failed_rule_count",
        "dq_failed_row_count",
        "load_behavior",
        "source_data_change_check",
        "target_data_change_check",
        "source_change_signal_json",
    }.isdisjoint(catalogue_fields)
    assert {"status", "can_continue", "expected_value_json", "actual_value_json"}.issubset(
        set(schemas[governance.GUARDRAIL_RESULTS_TABLE].fieldNames())
    )

def test_widget_display_rows_include_active_and_inactive_rules():
    """Verify widget display rows include active and inactive rules."""
    rows = governance._dq_rule_display_rows([
        {"rule_id": "r1", "rule_type": "not_null", "column_name": "id", "is_active": True},
        {"rule_id": "r2", "rule_type": "unique", "column_name": "id", "is_active": False},
    ])
    assert [r["Status"] for r in rows] == ["active", "inactive"]


def test_dq_tagged_dataframe_uses_row_level_warning_and_error_status(spark_session):
    """Verify dq tagged dataframe uses row level warning and error status."""
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
    """Verify value when uses null safe expected value comparison."""
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
    """Verify cross column rules use consistent null behavior."""
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
    """Verify enforce dq rules loads only active guardrail metadata rules."""
    df = spark_session.createDataFrame([(1, "ok"), (None, "ok")], "id int, status string")
    metadata = spark_session.createDataFrame(
        [
            {
                "rule_key": "governance-approved-active",
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
                "review_status": "governance_approved",
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
                "rule_key": "governance-approved-inactive",
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
                "review_status": "governance_approved",
                "action_type": "deactivated",
                "approved_at": "2026-06-14T00:00:00Z",
                "_committed_at": "2026-06-15T00:00:00Z",
            },
        ]
    )

    reads = []

    def fake_read(table, *, target, context, **kwargs):
        reads.append((context["env_name"], target, table, kwargs))
        return metadata

    monkeypatch.setattr(governance, "read_lakehouse_table", fake_read)

    result = governance.enforce_dq_rules(df, framework_config(), "dev", "sales", "orders", spark_session=spark_session)

    assert reads == [("dev", "metadata", governance.GUARDRAIL_RULES_TABLE, {"schema": None, "spark_session": spark_session})]
    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert len(result["checks"]) == 1
    assert result["checks"][0]["rule_id"] == "id_required"
    assert result["checks"][0]["failed_count"] == 1
    assert "_dq_check_status" in result["dataframe"].columns


def test_enforce_dq_rules_returns_passed_when_no_approved_active_rules(monkeypatch, spark_session):
    """Verify enforce dq rules returns passed when no active guardrail rules."""
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
    assert "_dq_check_status" in result["dataframe"].columns


def test_load_active_dq_rules_handles_lifecycle_column_shapes(spark_session):
    """Verify DQ loading only references lifecycle columns that exist."""

    def row(**overrides):
        base = {
            "rule_key": overrides.get("rule_key", overrides.get("rule_id", "rule")),
            "rule_id": overrides.get("rule_id", "rule"),
            "environment_name": "dev",
            "dataset_name": "sales",
            "table_name": "orders",
            "column_name": "order_id",
            "rule_type": "not_null",
            "rule_parameters_json": json.dumps({"columns": ["order_id"]}),
            "severity": "error",
            "description": "required",
            "action_type": "created",
            "approved_at": "2026-01-01T00:00:00Z",
            "_committed_at": "2026-01-01T00:00:00Z",
        }
        base.update(overrides)
        return base

    both = spark_session.createDataFrame([
        row(rule_key="both", rule_id="both", activation_state="active", review_state="governance_approved"),
    ])
    transitional = spark_session.createDataFrame([
        row(rule_key="transitional", rule_id="transitional", activation_state="active", review_status="governance_approved"),
    ])
    legacy = spark_session.createDataFrame([
        row(rule_key="legacy", rule_id="legacy", is_active=True, review_status="self_approved"),
    ])
    missing_review = spark_session.createDataFrame([
        row(rule_key="missing_review", rule_id="missing_review", activation_state="active"),
    ])
    lifecycle_rows = [
        row(rule_key="active_pending", rule_id="active_pending", activation_state="active", review_state="active_pending_governance_review"),
        row(rule_key="draft", rule_id="draft", activation_state="inactive", review_state="draft"),
        row(rule_key="pending", rule_id="pending", activation_state="pending", review_state="pending_governance_review"),
        row(rule_key="rejected", rule_id="rejected", activation_state="inactive", review_state="rejected_by_governance"),
        row(rule_key="inactive", rule_id="inactive", activation_state="inactive", review_state="inactive"),
        row(rule_key="superseded", rule_id="superseded", activation_state="inactive", review_state="superseded"),
    ]
    lifecycle = spark_session.createDataFrame(lifecycle_rows)

    assert [rule["rule_id"] for rule in governance._load_active_dq_rules(both, "orders", env_name="dev", dataset_name="sales")] == ["both"]
    assert [rule["rule_id"] for rule in governance._load_active_dq_rules(transitional, "orders", env_name="dev", dataset_name="sales")] == ["transitional"]
    assert [rule["rule_id"] for rule in governance._load_active_dq_rules(legacy, "orders", env_name="dev", dataset_name="sales")] == ["legacy"]
    assert governance._load_active_dq_rules(missing_review, "orders", env_name="dev", dataset_name="sales") == []
    assert [rule["rule_id"] for rule in governance._load_active_dq_rules(lifecycle, "orders", env_name="dev", dataset_name="sales")] == ["active_pending"]
