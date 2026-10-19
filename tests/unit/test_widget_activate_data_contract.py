"""Focused contracts for the Data Contract activation gate."""

import inspect
import json

from fabricops_kit.widgets.widget_activate_data_contract import (
    _latest_validation,
    widget_activate_data_contract,
)


def _row(*, run_id: str, status: str, can_continue: bool, severity: str, committed_at: str):
    return {
        "contract_id": "contract-a",
        "contract_version": 2,
        "environment_name": "dev",
        "execution_type": "validate",
        "guardrail_type": "guardrail_coverage", "rule_type": "contract_validation",
        "result_payload_json": '{"validation_complete":true}',
        "run_id": run_id,
        "status": status,
        "can_continue": can_continue,
        "severity": severity,
        "_committed_at": committed_at,
        "_activity_id": run_id,
    }


def test_latest_validation_requires_exact_version_evidence():
    """Reject activation when the exact frozen version has no validation evidence."""
    result = _latest_validation(
        [], contract_id="contract-a", contract_version=2, environment_name="dev"
    )
    assert result["validated"] is False
    assert result["run_id"] == ""


def test_latest_validation_uses_latest_run_and_blocks_failed_guardrails():
    """Use the latest validation run and allow warnings that can continue."""
    rows = [
        _row(run_id="old", status="failed", can_continue=False, severity="blocking", committed_at="2026-09-25T10:00:00"),
        _row(run_id="new", status="passed", can_continue=True, severity="blocking", committed_at="2026-09-26T10:00:00"),
        _row(run_id="new", status="warning", can_continue=True, severity="warning", committed_at="2026-09-26T10:00:01"),
        _row(run_id="new", status="passed", can_continue=True, severity="blocking", committed_at="2026-09-26T10:00:02"),
    ]
    result = _latest_validation(
        rows, contract_id="contract-a", contract_version=2, environment_name="dev"
    )
    assert result["validated"] is True
    assert result["run_id"] == "new"
    assert result["blocked"] == 0
    assert result["warnings"] == 1


def test_latest_validation_blocks_latest_failed_run():
    """Block activation when the latest validation run has a blocking failure."""
    rows = [
        _row(run_id="old", status="passed", can_continue=True, severity="blocking", committed_at="2026-09-25T10:00:00"),
        _row(run_id="new", status="failed", can_continue=False, severity="blocking", committed_at="2026-09-26T10:00:00"),
    ]
    result = _latest_validation(
        rows, contract_id="contract-a", contract_version=2, environment_name="dev"
    )
    assert result["validated"] is False
    assert result["blocked"] == 1


def test_activation_widget_uses_compact_three_step_confirmation_flow():
    """Keep activation compact and require an explicit confirmation prompt."""
    source = inspect.getsource(widget_activate_data_contract)

    assert 'grid_template_columns="repeat(3, minmax(0, 1fr))"' in source
    assert 'title="1 · Contract"' in source
    assert 'title="2 · Data Agreement"' in source
    assert 'title="3 · Review & activate"' in source
    assert "widgets.Combobox(" in source
    assert 'placeholder="Search Data Agreements..."' in source
    assert "ensure_option=True" in source
    assert "widgets.Checkbox(" not in source
    assert "confirmation_prompt.layout.display = \"flex\"" in source
    assert "confirm_activation.on_click(perform_activation)" in source
    assert "activate.on_click(on_activate)" in source



def test_partial_successful_checks_do_not_enable_activation():
    """A passing check without the full validation completion record is insufficient."""
    row = _row(run_id="partial", status="passed", can_continue=True, severity="blocking", committed_at="2026-10-19T10:00:00")
    row.update(guardrail_type="schema", rule_type="required_columns", result_payload_json="{}")
    assert not _latest_validation([row], contract_id="contract-a", contract_version=2, environment_name="dev")["validated"]


def test_latest_partial_run_supersedes_an_earlier_completed_run():
    """A later incomplete attempt cannot reuse an old completion record."""
    complete = _row(run_id="complete", status="passed", can_continue=True, severity="blocking", committed_at="2026-10-19T09:00:00")
    partial = _row(run_id="partial", status="passed", can_continue=True, severity="blocking", committed_at="2026-10-19T10:00:00")
    partial.update(guardrail_type="schema", rule_type="required_columns", result_payload_json="{}")
    assert not _latest_validation([complete, partial], contract_id="contract-a", contract_version=2, environment_name="dev")["validated"]



def test_new_partial_checks_in_same_activity_do_not_reuse_old_completion():
    """Interactive retries sharing a run ID need a completion after their latest check."""
    complete = _row(run_id="same", status="passed", can_continue=True, severity="blocking", committed_at="2026-10-19T09:00:00")
    later = _row(run_id="same", status="passed", can_continue=True, severity="blocking", committed_at="2026-10-19T10:00:00")
    later.update(guardrail_type="schema", rule_type="required_columns", result_payload_json="{}")
    assert not _latest_validation([complete, later], contract_id="contract-a", contract_version=2, environment_name="dev")["validated"]
