"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import json

import pytest

from fabricops_kit.pipeline import guardrails_shared as governance
from fabricops_kit.config import metadata_schemas
from fabricops_kit.config.shared import build_metadata_table_key
from fabricops_kit.widgets import shared as governance_authoring
from tests.helpers import FakeSpark, framework_config

pytestmark = pytest.mark.unit


def _rule(rule_type: str, **kwargs):
    rule = {"rule_id": f"r_{rule_type}", "rule_type": rule_type, "columns": ["id"], "severity": "error", "description": "test"}
    rule.update(kwargs)
    if rule_type == "missing_values":
        rule.setdefault("maximum_null_percent", 0)
    return rule


@pytest.mark.parametrize(
    ("rule", "failed"),
    [
        (_rule("missing_values", columns=["email"], maximum_null_percent=10), 1),
        (_rule("blank_text", columns=["name"]), 2),
        (_rule("unique_values", columns=["id"]), 2),
        (_rule("unique_combination", columns=["id", "semester"]), 2),
        (_rule("allowed_values", columns=["status"], allowed_values=["Active", "Inactive"]), 1),
        (_rule("blocked_values", columns=["country"], blocked_values=["UNKNOWN", "N/A"]), 2),
        (_rule("value_range", columns=["score"], minimum=0, maximum=100), 1),
        (_rule("text_pattern", columns=["email"], pattern=r"^[^@]+@[^@]+\.[^@]+$"), 1),
        (_rule("required_when", columns=["approved_date"], condition_column="country", condition_operator="=", condition_value="UNKNOWN"), 1),
        (_rule("conditional_value", columns=["is_active"], condition_column="student_status", condition_operator="=", condition_value="Graduated", expected_value=False), 1),
        (_rule("compare_columns", columns=["end_date", "start_date"], operator=">="), 1),
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


@pytest.mark.parametrize("old_rule_type", ["unique_key", "regex_format", "regex", "unique_compound", "compound_unique", "datatype", "referential_integrity", "custom_expression", "null_rate_below", "non_empty_string", "unique", "accepted_values", "not_in_values", "between", "regex_match", "value_when", "not_null", "greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal", "date_not_future", "date_between", "freshness", "max_age_days", "column_pair_equal", "column_a_gte_column_b", "column_a_gt_column_b", "expression_true"])
def test_legacy_or_external_rule_names_fail_validation(old_rule_type):
    """Verify legacy or external rule names fail validation."""
    with pytest.raises(ValueError, match="unsupported rule_type"):
        governance._validate_dq_rules([_rule(old_rule_type, columns=["id"])])


def test_strict_null_rate_and_blank_text_have_distinct_semantics(spark_session):
    """Verify strict null-rate and non-empty-string rules have distinct semantics."""
    df = spark_session.createDataFrame([(None,), ("",), ("   ",), ("ok",)], "name string")

    strict_null_rate = _rule("missing_values", columns=["name"], maximum_null_percent=0)
    non_empty = _rule("blank_text", columns=["name"])

    null_rate_check = governance._run_dq_guardrail_checks(df, "students", [strict_null_rate])[0]
    non_empty_check = governance._run_dq_guardrail_checks(df, "students", [non_empty])[0]

    assert null_rate_check["failed_count"] == 1
    assert non_empty_check["failed_count"] == 3


def test_dq_metadata_actions_are_append_only_and_preserve_multicolumns(fake_notebookutils):
    """Verify dq metadata actions are append only and preserve multicolumns."""
    profile_rows = [{"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "student_id"}]
    base = {"rule_id": "grain", "rule_type": "unique_combination", "columns": ["student_id", "semester"], "severity": "error", "description": "grain", "commit": True}
    rows = governance_authoring._build_dq_rule_records(
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
            {"rule_key": "k1", "rule_id": "r1", "metadata_table_key": "orders-key", "environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "id", "rule_type": "missing_values", "rule_parameters_json": json.dumps({"columns": ["id"], "maximum_null_percent": 0}), "severity": "error", "description": "old", "is_active": True, "review_status": "governance_approved", "action_type": "created", "approved_at": "2026-01-01T00:00:00Z", "_committed_at": "2026-01-01T00:00:00Z"},
            {"rule_key": "k1", "rule_id": "r1", "metadata_table_key": "orders-key", "environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "id", "rule_type": "missing_values", "rule_parameters_json": json.dumps({"columns": ["id"], "maximum_null_percent": 0}), "severity": "error", "description": "off", "is_active": False, "review_status": "governance_approved", "action_type": "deactivated", "approved_at": "2026-01-02T00:00:00Z", "_committed_at": "2026-01-02T00:00:00Z"},
            {"rule_key": "k2", "rule_id": "r2", "metadata_table_key": "orders-key", "environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "status", "rule_type": "allowed_values", "rule_parameters_json": json.dumps({"columns": ["status"], "allowed_values": ["A"]}), "severity": "warning", "description": "status", "is_active": True, "review_status": "governance_approved", "action_type": "created", "approved_at": "2026-01-01T00:00:00Z", "_committed_at": "2026-01-01T00:00:00Z"},
        ]
    )
    rules = governance._load_active_dq_rules(metadata, "orders-key", env="dev", dataset_name="sales")
    assert [r["rule_id"] for r in rules] == ["r2"]


def test_active_dq_rules_are_scoped_by_canonical_table_identity(spark_session):
    """Do not mix rules for same-named tables in different configured stores."""
    base = {
        "environment_name": "dev", "dataset_name": "sales", "table_name": "orders",
        "column_name": "id", "rule_type": "missing_values",
        "rule_parameters_json": json.dumps({"columns": ["id"], "maximum_null_percent": 0}),
        "severity": "error", "is_active": True, "review_status": "governance_approved",
        "action_type": "created", "_committed_at": "2026-01-01T00:00:00Z",
    }
    metadata = spark_session.createDataFrame([
        {**base, "metadata_table_key": "source-orders", "rule_key": "source", "rule_id": "source"},
        {**base, "metadata_table_key": "product-orders", "rule_key": "product", "rule_id": "product"},
    ])

    rules = governance._load_active_dq_rules(
        metadata, "product-orders", env="dev", dataset_name="sales",
    )

    assert [rule["rule_id"] for rule in rules] == ["product"]



def test_governance_metadata_schemas_use_catalogue_for_profile_history():
    """Verify guardrail schemas keep rules/results and use catalogue profile evidence."""
    schemas = metadata_schemas.metadata_table_schema_registry()

    assert governance_authoring.GUARDRAIL_TABLE in schemas
    assert governance_authoring.GUARDRAIL_RESULTS_TABLE in schemas
    assert "METADATA_GUARDRAIL_PROFILES" not in schemas
    assert "METADATA_GUARDRAIL_BASELINE_EVENTS" not in schemas
    assert not hasattr(governance, "GUARDRAIL_BASELINE_EVENT_TYPES")
    assert ["schema", "freshness", "profile_behavior", "dq"] == ["schema", "freshness", "profile_behavior", "dq"]
    assert "governance_approved" in governance_authoring.GUARDRAIL_REVIEW_STATUSES
    assert {"guardrail_type", "review_status", "source_notebook_type", "superseded_by_rule_key"}.issubset(
        set(schemas[governance_authoring.GUARDRAIL_TABLE].fieldNames())
    )
    catalogue_fields = set(schemas[governance_authoring.CATALOGUE_TABLE].fieldNames())
    profiled_fields = set(schemas["METADATA_DATA_PROFILED"].fieldNames())
    frequency_fields = set(schemas["METADATA_DATA_PROFILED_FREQUENCY"].fieldNames())
    assert {"store_type", "metadata_table_key", "metadata_column_key", "schema_fingerprint"}.issubset(catalogue_fields)
    assert {
        "row_count",
        "non_null_count",
        "null_percent",
        "distinct_percent",
    }.issubset(profiled_fields)
    assert "frequency_json" not in profiled_fields
    assert {
        "metadata_column_key",
        "value",
        "frequency_count",
        "frequency_percent",
        "frequency_rank",
        "profiled_row_count",
        "profiled_non_null_count",
        "profiled_at",
    }.issubset(frequency_fields)
    assert {"profile_role", "watermark_column", "watermark_value", "profile_hash", "profile_payload_json"}.isdisjoint(catalogue_fields)
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
        set(schemas[governance_authoring.GUARDRAIL_RESULTS_TABLE].fieldNames())
    )


def test_dq_tagged_dataframe_uses_row_level_warning_and_error_status(spark_session):
    """Verify dq tagged dataframe uses row level warning and error status."""
    df = spark_session.createDataFrame(
        [(None, "bad", -1), ("ok", "bad", -1), ("ok", "good", 1), (None, "good", -1)],
        "id string, status string, amount int",
    )
    rules = [
        _rule("missing_values", rule_id="id_required", columns=["id"], severity="error"),
        _rule("allowed_values", rule_id="status_allowed", columns=["status"], allowed_values=["good"], severity="warning"),
        _rule("value_range", rule_id="amount_positive", columns=["amount"], minimum=0, minimum_inclusive=False, severity="warning"),
    ]

    rows = governance._dq_tagged_dataframe(df, rules).select("id", "status", "amount", "_dq_failed_rules", "_dq_check_status").collect()
    by_values = {(row["id"], row["status"], row["amount"]): row.asDict() for row in rows}

    assert by_values[(None, "bad", -1)]["_dq_check_status"] == "failed"
    assert by_values[("ok", "bad", -1)]["_dq_check_status"] == "warning"
    assert by_values[("ok", "good", 1)]["_dq_check_status"] == "passed"
    assert by_values[(None, "good", -1)]["_dq_check_status"] == "failed"


def test_conditional_value_uses_null_safe_expected_value_comparison(spark_session):
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
        _rule("conditional_value", rule_id="graduated_inactive", columns=["is_active"], condition_column="student_status", condition_operator="=", condition_value="Graduated", expected_value=False),
        _rule("conditional_value", rule_id="null_expected", columns=["expected_null"], condition_column="student_status", condition_operator="=", condition_value="Graduated", expected_value=None),
        _rule("conditional_value", rule_id="nonnull_expected", columns=["actual_null"], condition_column="student_status", condition_operator="=", condition_value="Graduated", expected_value="x"),
    ]

    checks = {check["rule_id"]: check for check in governance._run_dq_guardrail_checks(df, "students", rules)}

    assert checks["graduated_inactive"]["failed_count"] == 1
    assert checks["null_expected"]["failed_count"] == 0
    assert checks["nonnull_expected"]["failed_count"] == 3

    null_mismatch = _rule("conditional_value", rule_id="null_mismatch", columns=["actual_non_null"], condition_column="student_status", condition_operator="=", condition_value="Graduated", expected_value=None)
    assert governance._run_dq_guardrail_checks(df, "students", [null_mismatch])[0]["failed_count"] == 1


def test_cross_column_rules_use_consistent_null_behavior(spark_session):
    """Verify cross column rules use consistent null behavior."""
    df = spark_session.createDataFrame(
        [(None, None), (None, 1), (1, None), (1, 1), (2, 1), (1, 2)],
        "a int, b int",
    )

    equal_check = governance._run_dq_guardrail_checks(df, "pairs", [_rule("compare_columns", columns=["a", "b"], operator="=")])[0]
    gte_check = governance._run_dq_guardrail_checks(df, "pairs", [_rule("compare_columns", columns=["a", "b"], operator=">=")])[0]
    gt_check = governance._run_dq_guardrail_checks(df, "pairs", [_rule("compare_columns", columns=["a", "b"], operator=">")])[0]

    assert equal_check["failed_count"] == 4
    assert gte_check["failed_count"] == 3
    assert gt_check["failed_count"] == 4


def test_run_active_dq_guardrail_loads_only_approved_active_metadata_rules(monkeypatch, spark_session):
    """Verify the internal active DQ guardrail loads only active metadata rules."""
    df = spark_session.createDataFrame([(1, "ok"), (None, "ok")], "id int, status string")
    table_key = build_metadata_table_key("lakehouse", "", None, "orders")
    metadata = spark_session.createDataFrame(
        [
            {
                "rule_key": "governance-approved-active",
                "rule_id": "id_required",
                "environment_name": "dev",
                "dataset_name": "sales",
                "table_name": "orders",
                "metadata_table_key": table_key,
                "column_name": "id",
                "rule_type": "missing_values",
                "rule_parameters_json": json.dumps({"columns": ["id"], "maximum_null_percent": 0}),
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
                "metadata_table_key": table_key,
                "column_name": "status",
                "rule_type": "allowed_values",
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
                "metadata_table_key": table_key,
                "column_name": "status",
                "rule_type": "allowed_values",
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
        reads.append((context["env"], target, table, kwargs))
        return metadata

    monkeypatch.setattr(governance, "read_lakehouse_table_core", fake_read)

    result = governance.run_active_dq_guardrail(df, framework_config(), "dev", "sales", "orders", spark_session=spark_session)

    assert reads == [("dev", "metadata", governance.GUARDRAIL_TABLE, {"schema": None, "spark_session": spark_session})]
    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert len(result["checks"]) == 1
    assert result["checks"][0]["rule_id"] == "id_required"
    assert result["checks"][0]["failed_count"] == 1
    assert "_dq_check_status" in result["dataframe"].columns


def test_run_active_dq_guardrail_returns_passed_when_no_approved_active_rules(monkeypatch, spark_session):
    """Verify the internal active DQ guardrail returns passed when no active guardrail rules."""
    df = spark_session.createDataFrame([(1, "ok")], "id int, status string")
    table_key = build_metadata_table_key("lakehouse", "", None, "orders")
    metadata = spark_session.createDataFrame(
        [
            {
                "rule_key": "draft-only",
                "rule_id": "draft_rule",
                "environment_name": "dev",
                "dataset_name": "sales",
                "table_name": "orders",
                "metadata_table_key": table_key,
                "column_name": "id",
                "rule_type": "missing_values",
                "rule_parameters_json": json.dumps({"columns": ["id"], "maximum_null_percent": 0}),
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
    monkeypatch.setattr(governance, "read_lakehouse_table_core", lambda *args, **kwargs: metadata)

    result = governance.run_active_dq_guardrail(df, framework_config(), "dev", "sales", "orders", spark_session=spark_session)

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
            "metadata_table_key": "orders-key",
            "column_name": "order_id",
            "rule_type": "missing_values",
            "rule_parameters_json": json.dumps({"columns": ["order_id"], "maximum_null_percent": 0}),
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

    assert [rule["rule_id"] for rule in governance._load_active_dq_rules(both, "orders-key", env="dev", dataset_name="sales")] == ["both"]
    assert [rule["rule_id"] for rule in governance._load_active_dq_rules(transitional, "orders-key", env="dev", dataset_name="sales")] == ["transitional"]
    assert [rule["rule_id"] for rule in governance._load_active_dq_rules(legacy, "orders-key", env="dev", dataset_name="sales")] == ["legacy"]
    assert governance._load_active_dq_rules(missing_review, "orders-key", env="dev", dataset_name="sales") == []
    assert [rule["rule_id"] for rule in governance._load_active_dq_rules(lifecycle, "orders-key", env="dev", dataset_name="sales")] == ["active_pending"]

def test_null_rate_zero_is_strict_and_positive_threshold_allows_expected_rate(spark_session):
    """Use missing_values(0) for strict non-null without a duplicate rule type."""
    df = spark_session.createDataFrame([(1,), (2,), (None,), (3,)], "value int")
    strict = _rule("missing_values", columns=["value"], maximum_null_percent=0)
    permissive = _rule("missing_values", columns=["value"], maximum_null_percent=25)

    assert governance._run_dq_guardrail_checks(df, "values", [strict])[0]["failed_count"] == 1
    assert governance._run_dq_guardrail_checks(df, "values", [permissive])[0]["failed_count"] == 0


@pytest.mark.parametrize(
    ("parameters", "failed"),
    [
        ({"minimum": 0, "minimum_inclusive": True}, 0),
        ({"minimum": 0, "minimum_inclusive": False}, 1),
        ({"maximum": 100, "maximum_inclusive": True}, 0),
        ({"maximum": 100, "maximum_inclusive": False}, 1),
        ({"minimum": 0, "maximum": 100}, 0),
    ],
)
def test_between_supports_one_or_two_inclusive_or_exclusive_bounds(spark_session, parameters, failed):
    """Consolidate directional comparisons into configurable value_range bounds."""
    df = spark_session.createDataFrame([(0,), (50,), (100,)], "score int")
    rule = _rule("value_range", columns=["score"], **parameters)
    assert governance._run_dq_guardrail_checks(df, "scores", [rule])[0]["failed_count"] == failed


def test_between_preserves_comparable_date_values(spark_session):
    """Keep date-like comparable values in the general value_range rule."""
    df = spark_session.createDataFrame([("2025-12-31",), ("2026-01-01",), ("2026-12-31",)], "event_date string")
    rule = _rule(
        "value_range",
        columns=["event_date"],
        minimum="2026-01-01",
        minimum_inclusive=True,
        maximum="2026-12-31",
        maximum_inclusive=False,
    )
    assert governance._run_dq_guardrail_checks(df, "events", [rule])[0]["failed_count"] == 2


@pytest.mark.parametrize("operator", ["=", "!=", ">", ">=", "<", "<="])
def test_compare_columns_supports_controlled_operators(spark_session, operator):
    """Keep ordered column comparison limited to the governed operator list."""
    df = spark_session.createDataFrame([(2, 1)], "a int, b int")
    rule = _rule("compare_columns", columns=["a", "b"], operator=operator)
    check = governance._run_dq_guardrail_checks(df, "pairs", [rule])[0]
    assert check["failed_count"] in {0, 1}


def test_compare_columns_rejects_same_column_and_unknown_operator():
    """Reject ambiguous ordered comparisons before evaluation."""
    with pytest.raises(ValueError, match="different columns"):
        governance._validate_dq_rules([_rule("compare_columns", columns=["a", "a"], operator="=")])
    with pytest.raises(ValueError, match="unsupported operator"):
        governance._validate_dq_rules([_rule("compare_columns", columns=["a", "b"], operator="contains")])
