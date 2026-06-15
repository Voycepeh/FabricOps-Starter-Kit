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
    assert guardrail_authoring_status({"governance_mode": "ungoverned"}) | {"created": True}
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
