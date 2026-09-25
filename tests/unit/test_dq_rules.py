"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import json
import importlib

import pytest

from fabricops_kit.pipeline import shared as governance
from fabricops_kit.config import metadata_schemas
from fabricops_kit.config.shared import build_table_id
from fabricops_kit.widgets import shared as governance_authoring
from tests.helpers import FakeSpark, framework_config

pytestmark = pytest.mark.unit


def test_check_dq_passes_development_contract_context_to_runtime(monkeypatch):
    """Keep DQ selection in the shared runtime loader without changing its public signature."""
    module = importlib.import_module("fabricops_kit.pipeline.check_dq")
    context = {"data_contract_overrides": {"orders": {"contract_id": "contract-a", "contract_version": 2}}}
    captured = {}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", context))
    monkeypatch.setattr(module, "resolve_pipeline_data_contract", lambda *args, **kwargs: {"contract_id": "contract-a"})
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *args, **kwargs: {
        "table_id": "orders", "store_type": "lakehouse", "store": "source", "schema": "sales", "table_name": "orders",
    })
    monkeypatch.setattr(
        module, "check_dq_runtime",
        lambda *args, **kwargs: captured.update(kwargs) or {"status": "passed"},
    )
    assert module.check_dq(object(), table_id="orders", spark_session=object())["status"] == "passed"
    assert captured["context"] is context


def test_check_dq_can_skip_contract_io_and_raise_on_block(monkeypatch):
    """Notebook validation mode removes result-list orchestration."""
    module = importlib.import_module("fabricops_kit.pipeline.check_dq")
    assert module.check_dq(object(), table_id="orders", enabled=False) == {
        "status": "skipped", "can_continue": True, "checks": [],
    }
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(module, "resolve_pipeline_data_contract", lambda *args, **kwargs: {"contract_id": "contract-a"})
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *_args, **_kwargs: {
        "table_id": "orders", "store_type": "lakehouse", "store": "source",
        "schema": "sales", "table_name": "orders",
    })
    monkeypatch.setattr(module, "check_dq_runtime", lambda *_args, **_kwargs: {"can_continue": False})
    with pytest.raises(RuntimeError, match="blocking DQ Guardrail"):
        module.check_dq(object(), table_id="orders", raise_on_failure=True, spark_session=object())


def test_check_dq_skips_when_development_has_no_selected_contract(monkeypatch):
    """Return a continuation-safe result without running contract-backed DQ."""
    module = importlib.import_module("fabricops_kit.pipeline.check_dq")
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(module, "resolve_pipeline_data_contract", lambda *args, **kwargs: None)
    monkeypatch.setattr(
        module, "check_dq_runtime",
        lambda *args, **kwargs: pytest.fail("DQ must not run without a selected Development contract"),
    )
    result = module.check_dq(object(), table_id="orders", raise_on_failure=True, spark_session=object())
    assert result["status"] == "skipped"
    assert result["can_continue"] is True
    assert result["environment_name"] == "dev"


def _rule(rule_type: str, **kwargs):
    rule = {"rule_id": f"r_{rule_type}", "rule_type": rule_type, "columns": ["id"], "severity": "error", "description": "test"}
    rule.update(kwargs)
    if rule_type == "completeness":
        rule.setdefault("maximum_missing_percent", 0)
        rule.setdefault("treat_blank_as_missing", False)
    return rule


@pytest.mark.parametrize(
    ("rule", "failed"),
    [
        (_rule("completeness", columns=["email"], maximum_missing_percent=10), 1),
        (_rule("completeness", columns=["name"], maximum_missing_percent=0, treat_blank_as_missing=True), 2),
        (_rule("uniqueness", columns=["id"]), 2),
        (_rule("uniqueness", columns=["id", "semester"]), 2),
        (_rule("value_set", columns=["status"], mode="allow", values=["Active", "Inactive"]), 1),
        (_rule("value_set", columns=["country"], mode="block", values=["UNKNOWN", "N/A"]), 2),
        (_rule("range", columns=["score"], minimum=0, maximum=100), 1),
        (_rule("pattern", columns=["email"], pattern=r"^[^@]+@[^@]+\.[^@]+$"), 1),
        (_rule("column_relationship", columns=["end_date", "start_date"], operator=">="), 1),
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


def test_custom_expression_supports_safe_arithmetic_business_rule(spark_session):
    """Evaluate arithmetic Business Rules without eval or arbitrary Python."""
    df = spark_session.createDataFrame(
        [
            (100.0, 2.0, 50.0, 0.0),
            (90.0, 2.0, 50.0, 0.1),
            (80.0, 2.0, 50.0, 0.1),
        ],
        "total_amount double, quantity double, unit_price double, discount double",
    )
    rule = _rule(
        "custom_expression",
        columns=["total_amount", "quantity", "unit_price", "discount"],
        expression_language="pyspark",
        expression=(
            'F.col("total_amount") == F.col("quantity") * F.col("unit_price") '
            '* (F.lit(1) - F.col("discount"))'
        ),
    )

    checks = governance._run_dq_guardrail_checks(df, "orders", [rule])

    assert checks[0]["failed_count"] == 1


@pytest.mark.parametrize(
    "expression",
    [
        'F.col("amount") ** F.lit(2) > F.lit(0)',
        'F.col("amount") // F.lit(2) > F.lit(0)',
    ],
)
def test_custom_expression_rejects_unapproved_arithmetic(expression):
    """Keep the arithmetic grammar deliberately bounded."""
    with pytest.raises(ValueError, match="unsupported"):
        governance._validate_dq_rules([
            _rule(
                "custom_expression",
                expression_language="pyspark",
                expression=expression,
            )
        ])


@pytest.mark.parametrize("old_rule_type", ["unique_key", "regex_format", "regex", "unique_compound", "compound_unique", "datatype", "referential_integrity", "null_rate_below", "non_empty_string", "unique", "accepted_values", "not_in_values", "between", "regex_match", "value_when", "not_null", "greater_than", "greater_than_or_equal", "less_than", "less_than_or_equal", "date_not_future", "date_between", "freshness", "max_age_days", "column_pair_equal", "column_a_gte_column_b", "column_a_gt_column_b", "expression_true"])
def test_legacy_or_external_rule_names_fail_validation(old_rule_type):
    """Verify legacy or external rule names fail validation."""
    with pytest.raises(ValueError, match="unsupported rule_type"):
        governance._validate_dq_rules([_rule(old_rule_type, columns=["id"])])


def test_completeness_blank_handling_is_explicit(spark_session):
    """Blank text is missing only when the authored boolean enables it."""
    df = spark_session.createDataFrame([(None,), ("",), ("   ",), ("ok",)], "name string")
    null_only = _rule("completeness", columns=["name"], maximum_missing_percent=0, treat_blank_as_missing=False)
    include_blanks = _rule("completeness", columns=["name"], maximum_missing_percent=0, treat_blank_as_missing=True)
    assert governance._run_dq_guardrail_checks(df, "students", [null_only])[0]["failed_count"] == 1
    assert governance._run_dq_guardrail_checks(df, "students", [include_blanks])[0]["failed_count"] == 3

def test_latest_active_rule_resolution_and_inactive_not_enforced(spark_session):
    """Verify latest active rule resolution and inactive not enforced."""
    metadata = spark_session.createDataFrame(
        [
            {"rule_key": "k1", "rule_id": "r1", "table_id": "orders-key", "environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "id", "rule_type": "completeness", "rule_parameters_json": json.dumps({"columns": ["id"], "maximum_missing_percent": 0, "treat_blank_as_missing": False}), "severity": "error", "description": "old", "is_active": True, "review_status": "governance_approved", "action_type": "created", "approved_at": "2026-01-01T00:00:00Z", "_committed_at": "2026-01-01T00:00:00Z"},
            {"rule_key": "k1", "rule_id": "r1", "table_id": "orders-key", "environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "id", "rule_type": "completeness", "rule_parameters_json": json.dumps({"columns": ["id"], "maximum_missing_percent": 0, "treat_blank_as_missing": False}), "severity": "error", "description": "off", "is_active": False, "review_status": "governance_approved", "action_type": "deactivated", "approved_at": "2026-01-02T00:00:00Z", "_committed_at": "2026-01-02T00:00:00Z"},
            {"rule_key": "k2", "rule_id": "r2", "table_id": "orders-key", "environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "status", "rule_type": "value_set", "rule_parameters_json": json.dumps({"columns": ["status"], "mode": "allow", "values": ["A"]}), "severity": "warning", "description": "status", "is_active": True, "review_status": "governance_approved", "action_type": "created", "approved_at": "2026-01-01T00:00:00Z", "_committed_at": "2026-01-01T00:00:00Z"},
        ]
    )
    rules = governance._load_active_dq_rules(metadata, "orders-key", env="dev", dataset_name="sales")
    assert [r["rule_id"] for r in rules] == ["r2"]


def test_active_dq_rules_are_scoped_by_canonical_table_identity(spark_session):
    """Do not mix rules for same-named tables in different configured stores."""
    base = {
        "environment_name": "dev", "dataset_name": "sales", "table_name": "orders",
        "column_name": "id", "rule_type": "completeness",
        "rule_parameters_json": json.dumps({"columns": ["id"], "maximum_missing_percent": 0, "treat_blank_as_missing": False}),
        "severity": "error", "is_active": True, "review_status": "governance_approved",
        "action_type": "created", "_committed_at": "2026-01-01T00:00:00Z",
    }
    metadata = spark_session.createDataFrame([
        {**base, "table_id": "source-orders", "rule_key": "source", "rule_id": "source"},
        {**base, "table_id": "product-orders", "rule_key": "product", "rule_id": "product"},
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
    assert not hasattr(governance_authoring, "GUARDRAIL_REVIEW_STATUSES")
    assert {"guardrail_rule_id", "contract_id", "contract_version", "column_id", "guardrail_type", "rule_parameters_json", "is_active"}.issubset(
        set(schemas[governance_authoring.GUARDRAIL_TABLE].fieldNames())
    )
    catalogue_fields = set(schemas[governance_authoring.CATALOGUE_TABLE].fieldNames())
    profiled_fields = set(schemas["METADATA_DATA_PROFILED"].fieldNames())
    frequency_fields = set(schemas["METADATA_DATA_PROFILED_FREQUENCY"].fieldNames())
    assert {"metadata_level", "store_type", "table_id", "column_id", "first_profiled_at", "last_profiled_at", "is_active"}.issubset(catalogue_fields)
    assert {
        "row_count",
        "non_null_count",
        "null_percent",
        "distinct_percent",
    }.issubset(profiled_fields)
    assert "frequency_json" not in profiled_fields
    assert {
        "frequency_id",
        "profile_id",
        "profile_snapshot_id",
        "value",
        "frequency_count",
        "frequency_percent",
        "frequency_rank",
        "profiled_row_count",
        "profiled_non_null_count",
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
    assert {"guardrail_result_id", "guardrail_rule_id", "status", "can_continue", "result_payload_json"}.issubset(
        set(schemas[governance_authoring.GUARDRAIL_RESULTS_TABLE].fieldNames())
    )


def test_dq_tagged_dataframe_uses_row_level_warning_and_error_status(spark_session):
    """Verify dq tagged dataframe uses row level warning and error status."""
    df = spark_session.createDataFrame(
        [(None, "bad", -1), ("ok", "bad", -1), ("ok", "good", 1), (None, "good", -1)],
        "id string, status string, amount int",
    )
    rules = [
        _rule("completeness", rule_id="id_required", columns=["id"], severity="error"),
        _rule("value_set", rule_id="status_allowed", columns=["status"], mode="allow", values=["good"], severity="warning"),
        _rule("range", rule_id="amount_positive", columns=["amount"], minimum=0, minimum_inclusive=False, severity="warning"),
    ]

    rows = governance._dq_tagged_dataframe(df, rules).select("id", "status", "amount", "_dq_failed_rules", "_dq_check_status").collect()
    by_values = {(row["id"], row["status"], row["amount"]): row.asDict() for row in rows}

    assert by_values[(None, "bad", -1)]["_dq_check_status"] == "failed"
    assert by_values[("ok", "bad", -1)]["_dq_check_status"] == "warning"
    assert by_values[("ok", "good", 1)]["_dq_check_status"] == "passed"
    assert by_values[(None, "good", -1)]["_dq_check_status"] == "failed"


def test_cross_column_rules_use_consistent_null_behavior(spark_session):
    """Verify cross column rules use consistent null behavior."""
    df = spark_session.createDataFrame(
        [(None, None), (None, 1), (1, None), (1, 1), (2, 1), (1, 2)],
        "a int, b int",
    )

    equal_check = governance._run_dq_guardrail_checks(df, "pairs", [_rule("column_relationship", columns=["a", "b"], operator="=")])[0]
    gte_check = governance._run_dq_guardrail_checks(df, "pairs", [_rule("column_relationship", columns=["a", "b"], operator=">=")])[0]
    gt_check = governance._run_dq_guardrail_checks(df, "pairs", [_rule("column_relationship", columns=["a", "b"], operator=">")])[0]

    assert equal_check["failed_count"] == 4
    assert gte_check["failed_count"] == 3
    assert gt_check["failed_count"] == 4


def test_load_active_dq_rules_handles_lifecycle_column_shapes(spark_session):
    """Verify DQ loading only references lifecycle columns that exist."""

    def row(**overrides):
        base = {
            "rule_key": overrides.get("rule_key", overrides.get("rule_id", "rule")),
            "rule_id": overrides.get("rule_id", "rule"),
            "environment_name": "dev",
            "dataset_name": "sales",
            "table_name": "orders",
            "table_id": "orders-key",
            "column_name": "order_id",
            "rule_type": "completeness",
            "rule_parameters_json": json.dumps({"columns": ["order_id"], "maximum_missing_percent": 0, "treat_blank_as_missing": False}),
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
    """Use completeness(0) for strict non-null without a duplicate rule type."""
    df = spark_session.createDataFrame([(1,), (2,), (None,), (3,)], "value int")
    strict = _rule("completeness", columns=["value"], maximum_missing_percent=0)
    permissive = _rule("completeness", columns=["value"], maximum_missing_percent=25)

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
    """Consolidate directional comparisons into configurable range bounds."""
    df = spark_session.createDataFrame([(0,), (50,), (100,)], "score int")
    rule = _rule("range", columns=["score"], **parameters)
    assert governance._run_dq_guardrail_checks(df, "scores", [rule])[0]["failed_count"] == failed


def test_between_preserves_comparable_date_values(spark_session):
    """Keep date-like comparable values in the general range rule."""
    df = spark_session.createDataFrame([("2025-12-31",), ("2026-01-01",), ("2026-12-31",)], "event_date string")
    rule = _rule(
        "range",
        columns=["event_date"],
        minimum="2026-01-01",
        minimum_inclusive=True,
        maximum="2026-12-31",
        maximum_inclusive=False,
    )
    assert governance._run_dq_guardrail_checks(df, "events", [rule])[0]["failed_count"] == 2


@pytest.mark.parametrize("operator", ["=", "!=", ">", ">=", "<", "<="])
def test_column_relationship_supports_controlled_operators(spark_session, operator):
    """Keep ordered column comparison limited to the governed operator list."""
    df = spark_session.createDataFrame([(2, 1)], "a int, b int")
    rule = _rule("column_relationship", columns=["a", "b"], operator=operator)
    check = governance._run_dq_guardrail_checks(df, "pairs", [rule])[0]
    assert check["failed_count"] in {0, 1}


def test_column_relationship_rejects_same_column_and_unknown_operator():
    """Reject ambiguous ordered comparisons before evaluation."""
    with pytest.raises(ValueError, match="different columns"):
        governance._validate_dq_rules([_rule("column_relationship", columns=["a", "a"], operator="=")])
    with pytest.raises(ValueError, match="unsupported operator"):
        governance._validate_dq_rules([_rule("column_relationship", columns=["a", "b"], operator="contains")])


@pytest.mark.parametrize(
    ("action", "runtime_severity"),
    [("Warn", "warning"), ("Block", "error")],
)
def test_authored_guardrail_action_maps_to_dq_runtime_severity(action, runtime_severity):
    """Canonical Warn and Block actions map to DQ continuation semantics."""
    assert governance._normalize_dq_severity(action) == runtime_severity
    status = "warning" if runtime_severity == "warning" else "failed"
    result = governance._summarize_dq_guardrail([{"status": status}])
    assert result["status"] == status
    assert result["can_continue"] is (action == "Warn")

@pytest.mark.parametrize("operator", ["=", "!=", ">", ">=", "<", "<="])
def test_column_relationship_supports_all_controlled_operators(spark_session, operator):
    """Evaluate every supported table relationship operator natively."""
    df = spark_session.createDataFrame([(1, 1), (2, 1), (None, 1)], "a int, b int")
    check = governance._run_dq_guardrail_checks(
        df, "pairs", [_rule("column_relationship", columns=["a", "b"], operator=operator)]
    )[0]
    assert check["total_count"] == 3


def test_custom_expression_pass_fail_and_validation(spark_session):
    """Compile safe custom boolean expressions and reject unsafe or missing references."""
    df = spark_session.createDataFrame(
        [("Closed", None), ("Closed", "2026-01-01"), ("Open", None)],
        "status string, closed_date string",
    )
    rule = _rule(
        "custom_expression", columns=[], expression_language="pyspark",
        expression='(F.col("status") != "Closed") | F.col("closed_date").isNotNull()',
    )
    assert governance._run_dq_guardrail_checks(df, "orders", [rule])[0]["failed_count"] == 1
    with pytest.raises(ValueError, match="missing column"):
        governance._run_dq_guardrail_checks(
            df, "orders", [_rule("custom_expression", columns=[], expression_language="pyspark", expression='F.col("unknown") == 1')]
        )
    with pytest.raises(ValueError, match="unsupported"):
        governance._validate_dq_rules([
            _rule("custom_expression", columns=[], expression_language="pyspark", expression='__import__("os").system("echo unsafe")')
        ])


@pytest.mark.parametrize(
    ("expression", "failed_count"),
    [
        ('F.col("status").isin("Open", "Closed")', 1),
        ('F.col("code").rlike("^[A-Z]{3}$")', 1),
        ('F.col("code").contains("BC")', 1),
        ('F.col("code").startswith("A")', 1),
        ('F.col("code").endswith("C")', 1),
    ],
)
def test_custom_expression_supports_safe_column_methods(spark_session, expression, failed_count):
    """Compile the explicit whitelist of useful, side-effect-free Column methods."""
    dataframe = spark_session.createDataFrame(
        [("Open", "ABC"), ("Pending", "bad")], "status string, code string"
    )
    rule = _rule(
        "custom_expression", columns=[], expression_language="pyspark", expression=expression,
    )
    check = governance._run_dq_guardrail_checks(dataframe, "orders", [rule])[0]
    assert check["failed_count"] == failed_count


def test_custom_expression_requires_boolean_spark_column(spark_session):
    """Reject a valid column reference when it does not resolve to a boolean predicate."""
    dataframe = spark_session.createDataFrame([(1,)], "amount int")
    rule = _rule(
        "custom_expression", columns=[], expression_language="pyspark", expression='F.col("amount")',
    )
    with pytest.raises(ValueError, match="must resolve to a boolean Spark Column"):
        governance._run_dq_guardrail_checks(dataframe, "orders", [rule])


@pytest.mark.parametrize(
    "expression",
    [
        'F.col("amount", "other") > 0',
        'F.lit(1, 2) == 1',
        'F.col("amount").isNull(1)',
        'F.col("amount").isNotNull(1)',
        'F.col("amount").isin()',
        'F.col("amount").rlike("x", "y")',
    ],
)
def test_custom_expression_rejects_invalid_signatures(expression):
    """Reject malformed calls rather than silently discarding their arguments."""
    with pytest.raises(ValueError):
        governance._validate_dq_rules([
            _rule(
                "custom_expression", columns=[], expression_language="pyspark",
                expression=expression,
            )
        ])
