"""Governance review uses exact diagnostic reports without Testing persistence."""

import hashlib
import inspect

import pytest

from fabricops_kit.widgets.widget_activate_data_contract import _diagnostic_review, widget_activate_data_contract


def report_and_contract():
    """Return a passing in-memory Testing report for one exact immutable payload."""
    contract = {"contract_id": "contract", "contract_version": 2, "table_id": "table", "contract_payload_json": '{"frozen":true}'}
    report = {"execution_mode": "testing", "execution_environment": "canary-east", "execution_plan_id": "plan",
              "validation_passed": True, "published": False, "persistence_status": "disabled",
              "tested_contracts": {"table": {"contract_id": "contract", "contract_version": 2,
                  "payload_sha256": hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest()}}}
    return report, contract


def test_successful_report_only_qualifies_for_explicit_review():
    """Testing provides diagnostics in memory, not registered activation evidence."""
    report, contract = report_and_contract()
    assert _diagnostic_review([report], contract, "canary-east") == {"available": True, "plan_id": "plan"}
    assert not _diagnostic_review([], contract, "canary-east")["available"]


@pytest.mark.parametrize("field,value", [("validation_passed", False), ("published", True),
    ("execution_mode", "live"), ("execution_environment", "elsewhere"), ("persistence_status", "committed")])
def test_incomplete_or_unrelated_report_never_qualifies(field, value):
    """The review requires a complete exact Testing result in this metadata scope."""
    report, contract = report_and_contract()
    report[field] = value
    assert not _diagnostic_review([report], contract, "canary-east")["available"]


@pytest.mark.parametrize("field,value", [("contract_id", "other"), ("contract_version", 3), ("payload_sha256", "wrong")])
def test_report_cannot_authorize_another_version_or_payload(field, value):
    """A report for one immutable payload cannot qualify another one."""
    report, contract = report_and_contract()
    report["tested_contracts"]["table"][field] = value
    assert not _diagnostic_review([report], contract, "canary-east")["available"]


def test_activation_requires_review_agreement_and_confirmation():
    """Keep a separate explicit Governance approval and two-step activation."""
    source = inspect.getsource(widget_activate_data_contract)
    assert "widgets.Checkbox(" in source
    assert 'validation["available"] and reviewed.value and agreement' in source
    assert "reviewed.value = False" in source
    assert "approval_scope" in source
    assert 'confirmation_prompt.layout.display = "flex"' in source
    assert "confirm_activation.on_click(perform_activation)" in source
    assert "METADATA_GUARDRAIL_RESULTS" not in source


def test_latest_failed_report_cannot_reuse_older_passing_diagnostics():
    """Later failure and equal-time ambiguity both prevent approval eligibility."""
    report, contract = report_and_contract()
    report["testing_completed_at"] = "2026-10-20T02:00:00Z"
    failed = {**report, "validation_passed": False, "testing_completed_at": "2026-10-20T10:30:00+08:00"}
    assert not _diagnostic_review([report, failed], contract, "canary-east")["available"]
    failed["testing_completed_at"] = report["testing_completed_at"]
    assert not _diagnostic_review([report, failed], contract, "canary-east")["available"]
