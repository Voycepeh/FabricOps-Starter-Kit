"""Tests for governed guardrail authoring state helpers."""

import json

from fabricops_kit.governance_review import (
    CATALOGUE_TABLE,
    GOVERNANCE_REVIEWS_TABLE,
    GUARDRAIL_RESULTS_TABLE,
    GUARDRAIL_RULES_TABLE,
    _get_governance_metadata_schemas,
    apply_governance_rule_action,
    guardrail_authoring_status,
    resolve_table_governance_policy,
    widget_author_dq_rules,
    widget_author_schema_freshness_profile_rules,
)


def test_metadata_ownership_schema_separates_catalogue_rules_and_results():
    """Verify catalogue, rule, result, and governance policy fields stay separated."""
    schemas = _get_governance_metadata_schemas()
    catalogue_fields = set(schemas[CATALOGUE_TABLE].fieldNames())
    rule_fields = set(schemas[GUARDRAIL_RULES_TABLE].fieldNames())
    result_fields = set(schemas[GUARDRAIL_RESULTS_TABLE].fieldNames())
    review_fields = set(schemas[GOVERNANCE_REVIEWS_TABLE].fieldNames())

    removed_catalogue_fields = {
        "load_behavior",
        "source_data_change_check",
        "target_data_change_check",
        "source_schema_check",
        "target_schema_check",
        "dq_status",
        "dq_rule_count",
        "dq_failed_rule_count",
        "dq_failed_row_count",
        "source_change_signal_json",
    }
    assert not removed_catalogue_fields & catalogue_fields
    assert {"approval_required", "approval_bypassed", "requires_post_review", "governance_mode", "approval_policy"}.issubset(rule_fields)
    assert {"result_id", "result_payload_json", "actual_value_json"}.issubset(result_fields)
    assert {"governance_mode", "approval_policy", "approval_bypass_allowed", "effective_from", "effective_to"}.issubset(review_fields)


def test_table_policy_defaults_to_ungoverned_no_approval():
    """Verify missing policy rows make a table ungoverned by default."""
    policy = resolve_table_governance_policy([], environment_name="dev", dataset_name="sales", table_name="orders")
    assert policy["governance_mode"] == "ungoverned"
    assert policy["approval_policy"] == "no_approval_required"


def test_authoring_status_matches_ungoverned_governed_and_bypass_paths():
    """Verify authoring lifecycle fields for all table governance paths."""
    ungoverned = guardrail_authoring_status({"governance_mode": "ungoverned"})
    governed = guardrail_authoring_status({"governance_mode": "governed", "approval_policy": "approval_required"})
    bypassed = guardrail_authoring_status({"governance_mode": "governed", "approval_policy": "approval_required_with_bypass"}, bypass_reason="urgent fix", actor="engineer@example.com")

    assert ungoverned["is_active"] is True
    assert ungoverned["review_status"] == "self_approved"
    assert governed["is_active"] is False
    assert governed["review_status"] == "proposed"
    assert bypassed["is_active"] is True
    assert bypassed["review_status"] == "bypass_active_pending_review"
    assert bypassed["requires_post_review"] is True
    assert bypassed["bypass_reason"] == "urgent fix"


def test_governance_rule_actions_approve_reject_and_supersede():
    """Verify governance can approve, reject, and supersede append-only rule rows."""
    rule = {"rule_key": "old", "review_status": "proposed", "is_active": False}
    assert apply_governance_rule_action(rule, "approve", actor="steward@example.com")["review_status"] == "governance_approved"
    assert apply_governance_rule_action(rule, "reject")["is_active"] is False
    superseded = apply_governance_rule_action(rule, "supersede", superseded_by_rule_key="new")
    assert superseded["review_status"] == "superseded"
    assert superseded["superseded_by_rule_key"] == "new"


def test_authoring_widgets_write_rule_intent_records_only():
    """Verify authoring widgets return guardrail-rule rows instead of catalogue or result rows."""
    state = {
        "environment_name": "dev",
        "dataset_name": "sales",
        "table_name": "orders",
        "metadata_table_key": "table-key",
        "columns": ["order_id"],
        "catalogue_profile_rows": [{"column_name": "order_id", "data_type": "string"}],
        "governance_mode": "ungoverned",
        "approval_policy": "no_approval_required",
    }
    records = widget_author_schema_freshness_profile_rules(state) + widget_author_dq_rules(state, selected_columns=["order_id"])
    assert {record["guardrail_type"] for record in records} == {"schema", "freshness", "profile_behavior", "dq"}
    assert all("rule_parameters_json" in record for record in records)
    assert all(json.loads(record["rule_parameters_json"]) is not None for record in records)
    assert all("result_id" not in record for record in records)
    assert all("profile_payload_json" not in record for record in records)


def _rule(**overrides):
    base = {
        "rule_key": "rule-key",
        "rule_id": "rule-id",
        "environment_name": "dev",
        "dataset_name": "sales",
        "table_name": "orders",
        "column_name": "",
        "guardrail_type": "schema",
        "rule_type": "relaxed",
        "rule_parameters_json": "{}",
        "severity": "blocking",
        "is_active": True,
        "review_status": "self_approved",
        "created_at": "2026-01-01T00:00:00Z",
    }
    base.update(overrides)
    return base


def test_schema_rules_from_guardrail_metadata_are_enforced(spark_session):
    """Verify schema rule rows are loaded and enforced."""
    from fabricops_kit.guardrails import validate_schema_rule

    df = spark_session.createDataFrame([(1, "ok", "extra")], "order_id int, status string, extra string")
    rules = [_rule(rule_parameters_json=json.dumps({"columns": ["order_id", "status"], "data_types": {"order_id": "int", "status": "string"}}))]

    result = validate_schema_rule(df, rules, dataset_name="sales", table_name="orders")

    assert result["status"] == "warning"
    assert result["can_continue"] is True
    assert result["guardrail_type"] == "schema"


def test_freshness_rules_from_guardrail_metadata_are_enforced(spark_session):
    """Verify freshness rule rows are loaded and enforced."""
    from fabricops_kit.guardrails import enforce_freshness_rule

    df = spark_session.createDataFrame([("2026-06-14",)], "business_date string")
    rules = [
        _rule(
            guardrail_type="freshness",
            rule_type="max_lag_days",
            rule_parameters_json=json.dumps({"freshness_column": "business_date", "max_lag_days": 2}),
        )
    ]

    result = enforce_freshness_rule(df, rules, dataset_name="sales", table_name="orders", reference_date="2026-06-15")

    assert result["status"] == "passed"
    assert result["guardrail_type"] == "freshness"


def test_profile_behavior_rules_from_guardrail_metadata_are_enforced(spark_session):
    """Verify profile behavior rule rows are loaded and enforced."""
    from fabricops_kit.guardrails import enforce_profile_behavior

    df = spark_session.createDataFrame([(1, "2026-06-14")], "order_id int, business_date string")
    rules = [
        _rule(
            guardrail_type="profile_behavior",
            rule_type="static_data",
            rule_parameters_json=json.dumps({}),
        )
    ]

    result = enforce_profile_behavior(
        spark_session,
        df,
        "METADATA_DATA_CATALOGUE",
        "sales",
        "orders",
        stage="target",
        run_id="run-1",
        rules_df=rules,
        catalogue_df=[],
        write_results=False,
    )

    assert result["status"] == "baseline_created"
    assert result["guardrail_type"] == "profile_behavior"
    assert result["rule_type"] == "static_data"


def test_dq_rules_from_guardrail_metadata_are_loaded_and_enforced(spark_session, monkeypatch):
    """Verify DQ rule rows are loaded and enforced."""
    from fabricops_kit import governance_review

    df = spark_session.createDataFrame([(1,), (None,)], "order_id int")
    rules_df = spark_session.createDataFrame([
        _rule(
            rule_key="dq-rule",
            rule_id="orders.order_id.not_null",
            guardrail_type="dq",
            rule_type="not_null",
            column_name="order_id",
            rule_parameters_json=json.dumps({"columns": ["order_id"]}),
            severity="error",
        )
    ])
    monkeypatch.setattr(governance_review, "_read_guardrail_rule_metadata", lambda *args, **kwargs: rules_df)

    result = governance_review.enforce_dq_rules(df, object(), "dev", "sales", "orders", spark_session=spark_session, write_results=False)

    assert result["status"] == "failed"
    assert result["can_continue"] is False
    assert result["checks"][0]["rule_id"] == "orders.order_id.not_null"


def test_bypass_warning_is_added_for_schema_freshness_profile_and_dq(spark_session, monkeypatch):
    """Verify bypass-active rules are enforced with post-review warning metadata."""
    from fabricops_kit import governance_review
    from fabricops_kit.guardrails import enforce_freshness_rule, enforce_profile_behavior, validate_schema_rule

    warning = "Rule is active through approval bypass and requires governance post-review."
    schema_df = spark_session.createDataFrame([(1,)], "order_id int")
    bypass_base = {"review_status": "bypass_active_pending_review"}

    schema = validate_schema_rule(
        schema_df,
        [_rule(**bypass_base, rule_parameters_json=json.dumps({"columns": ["order_id"], "data_types": {"order_id": "int"}}))],
        dataset_name="sales",
        table_name="orders",
    )
    freshness = enforce_freshness_rule(
        spark_session.createDataFrame([("2026-06-14",)], "business_date string"),
        [_rule(**bypass_base, guardrail_type="freshness", rule_type="max_lag_days", rule_parameters_json=json.dumps({"freshness_column": "business_date", "max_lag_days": 2}))],
        dataset_name="sales",
        table_name="orders",
        reference_date="2026-06-15",
    )
    profile = enforce_profile_behavior(
        spark_session,
        schema_df,
        "METADATA_DATA_CATALOGUE",
        "sales",
        "orders",
        stage="target",
        run_id="run-1",
        rules_df=[_rule(**bypass_base, guardrail_type="profile_behavior", rule_type="static_data")],
        catalogue_df=[],
        write_results=False,
    )

    dq_rules_df = spark_session.createDataFrame([
        _rule(**bypass_base, rule_key="dq-bypass", rule_id="orders.order_id.not_null", guardrail_type="dq", rule_type="not_null", column_name="order_id", rule_parameters_json=json.dumps({"columns": ["order_id"]}))
    ])
    monkeypatch.setattr(governance_review, "_read_guardrail_rule_metadata", lambda *args, **kwargs: dq_rules_df)
    dq = governance_review.enforce_dq_rules(schema_df, object(), "dev", "sales", "orders", spark_session=spark_session, write_results=False)

    for result in (schema, freshness, profile, dq):
        assert result["can_continue"] is True
        assert warning in result.get("reason", result.get("message", "")) or result.get("bypass_warning") == warning


def test_table_governance_policy_records_mark_governed_and_ungoverned():
    """Verify 03 governance helper records can mark table policy state."""
    from fabricops_kit.governance_review import mark_table_governed, mark_table_ungoverned

    state = {"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "metadata_table_key": "table-key"}
    governed = mark_table_governed(state, actor="steward@example.com", reason="critical table")
    ungoverned = mark_table_ungoverned(state, actor="steward@example.com", reason="sandbox table")

    assert governed["governance_mode"] == "governed"
    assert governed["approval_policy"] == "approval_required_with_bypass"
    assert governed["approval_bypass_allowed"] is True
    assert ungoverned["governance_mode"] == "ungoverned"
    assert ungoverned["approval_policy"] == "no_approval_required"


def test_governance_can_approve_or_reject_bypassed_active_rule():
    """Verify 03 governance can approve or reject bypass-active rules."""
    bypassed = {"rule_key": "rule", "review_status": "bypass_active_pending_review", "is_active": True, "requires_post_review": True}

    approved = apply_governance_rule_action(bypassed, "approve", actor="steward@example.com")
    rejected = apply_governance_rule_action(bypassed, "reject", actor="steward@example.com")

    assert approved["review_status"] == "governance_approved"
    assert approved["requires_post_review"] is False
    assert rejected["review_status"] == "rejected"
    assert rejected["is_active"] is False
