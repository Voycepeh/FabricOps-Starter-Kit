"""Tests for activation-state and formal governance-review transitions."""

import pytest

from fabricops_kit.governance_review import (
    _assert_governance_review_context,
    apply_governance_enrichment_action,
    apply_governance_rule_action,
    build_enrichment_rule_records,
    guardrail_authoring_status,
)


def test_authoring_actions_map_to_activation_and_review_states():
    """Verify 02 authoring actions cannot create formal review decisions."""
    draft = guardrail_authoring_status({}, authoring_action="save_draft")
    pending = guardrail_authoring_status({}, authoring_action="submit_for_governance_review")
    applied = guardrail_authoring_status({}, authoring_action="apply_now")

    assert draft["activation_state"] == "inactive"
    assert draft["is_active"] is False
    assert draft["review_state"] == "draft"
    assert draft["requires_governance_review"] is False
    assert pending["activation_state"] == "pending"
    assert pending["is_active"] is False
    assert pending["review_state"] == "pending_governance_review"
    assert pending["requires_governance_review"] is True
    assert applied["activation_state"] == "active"
    assert applied["is_active"] is True
    assert applied["review_state"] == "active_pending_governance_review"
    assert applied["requires_governance_review"] is True
    assert applied["activation_reason"] == "engineering_apply_now"
    assert {draft["review_state"], pending["review_state"], applied["review_state"]}.isdisjoint({"governance_approved", "rejected_by_governance"})


def test_formal_review_actions_are_blocked_outside_03_governance():
    """Verify direct formal review helpers require 03_governance context."""
    with pytest.raises(PermissionError, match="only allowed from 03_governance"):
        _assert_governance_review_context("02_pipeline")
    with pytest.raises(PermissionError, match="only allowed from 03_governance"):
        apply_governance_rule_action({"rule_id": "r1"}, "approve", source_notebook_type="02_pipeline")


def test_rule_review_transitions_cover_approve_reject_replace_and_deactivate():
    """Verify formal guardrail transitions preserve append-only replacement history."""
    pending = {"rule_id": "r1", "rule_key": "k1", "activation_state": "pending", "is_active": False, "review_state": "pending_governance_review", "source_notebook_type": "02_pipeline"}
    active_pending = {**pending, "activation_state": "active", "is_active": True, "review_state": "active_pending_governance_review"}
    approved = apply_governance_rule_action(active_pending, "approve")
    activated = apply_governance_rule_action(pending, "approve_and_activate")
    rejected = apply_governance_rule_action(pending, "reject")
    deactivated = apply_governance_rule_action(approved, "deactivate")
    old, new = apply_governance_rule_action(approved, "replace", superseded_by_rule_key="r2")

    assert approved["activation_state"] == "active"
    assert approved["review_state"] == "governance_approved"
    assert activated["activation_state"] == "active"
    assert rejected["activation_state"] == "inactive"
    assert rejected["review_state"] == "rejected_by_governance"
    assert deactivated["activation_state"] == "inactive"
    assert deactivated["review_state"] == "inactive"
    assert old["review_state"] == "superseded"
    assert old["superseded_by_record_id"] == "r2"
    assert new["activation_state"] == "active"
    assert new["review_state"] == "governance_approved"
    assert new["supersedes_record_id"] == "r1"


def test_enrichment_authoring_and_review_states_are_standardized():
    """Verify enrichment records use the same lifecycle and review actions."""
    profile_rows = [{"environment_name": "dev", "dataset_name": "sales", "table_name": "orders", "column_name": "id", "metadata_table_key": "dev.sales.orders", "metadata_column_key": "dev.sales.orders.id"}]
    records = build_enrichment_rule_records(profile_rows, [{"column_name": "id", "business_description": "Order identifier", "commit": True}], authoring_action="apply_now")
    record = records[0]
    rejected = apply_governance_enrichment_action(record, "reject")

    assert record["activation_state"] == "active"
    assert record["review_state"] == "active_pending_governance_review"
    assert record["source_notebook_type"] == "02_pipeline"
    assert rejected["activation_state"] == "inactive"
    assert rejected["review_state"] == "rejected_by_governance"
