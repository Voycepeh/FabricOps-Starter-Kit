"""First-run Bootstrap policy and contract bypass prevention."""

import json

import pytest

from fabricops_kit import setup_pipeline
from fabricops_kit.pipeline import shared
from tests.unit import test_execution_plan

plan_runtime = test_execution_plan.plan_runtime

SOURCE = {"store": "Bronze", "schema": "demo", "table_name": "source"}
TARGET = {"store": "Silver", "schema": "demo", "table_name": "target"}


def test_default_setup_builds_a_publishing_bootstrap_plan_without_choices(plan_runtime):
    """A fresh configured pipeline can Run all without touching contract controls."""
    _, runtime, _, _ = plan_runtime
    plan = setup_pipeline(sources=[SOURCE], targets=[TARGET], context=runtime)
    assert plan.execution_mode == "bootstrap" and plan.permits_persistence
    assert json.loads(plan.contracts_json) == {"source": None, "target": None}
    assert json.loads(plan.selections_json) == {"source": {"no_contract": True}, "target": {"no_contract": True}}
    assert json.loads(plan.participants_json)["target"]["roles"] == ["target"]


@pytest.mark.parametrize("active,status", [(False, "frozen"), (True, "frozen"), (True, "draft")])
def test_bootstrap_cannot_bypass_any_participant_governance(plan_runtime, active, status):
    """Even an unactivated frozen version requires deliberate governed execution."""
    rows, runtime, _, row = plan_runtime
    rows.append({**row(table_id="target", active=active), "status": status})
    with pytest.raises(ValueError, match="Bootstrap cannot bypass"):
        setup_pipeline(sources=[SOURCE], targets=[TARGET], context=runtime)


def test_drafts_unrelated_tables_and_other_environments_do_not_block_first_run(plan_runtime):
    """Bootstrap eligibility is scoped to participating frozen/active versions."""
    rows, runtime, _, row = plan_runtime
    rows.extend([{**row(), "status": "draft"}, row(table_id="unrelated"),
                 {**row(table_id="target"), "environment_name": "other-environment"}])
    assert setup_pipeline(sources=[SOURCE], targets=[TARGET], context=runtime).execution_mode == "bootstrap"


def test_bootstrap_revalidates_governance_before_each_operation(plan_runtime):
    """A contract frozen after setup prevents stale contract-free publication."""
    rows, runtime, _, row = plan_runtime
    plan = setup_pipeline(sources=[SOURCE], targets=[TARGET], context=runtime)
    rows.append(row(table_id="target"))
    with pytest.raises(ValueError, match="Bootstrap cannot bypass"):
        shared.prepare_pipeline_execution(["source"], execution_plan=plan)


@pytest.mark.parametrize("error", [RuntimeError("permission denied"), RuntimeError("Table not found")])
def test_bootstrap_does_not_infer_absent_governance_from_unreadable_metadata(plan_runtime, monkeypatch, error):
    """Only successful metadata reads can authorize the default Bootstrap plan."""
    _, runtime, _, _ = plan_runtime
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda *a, **kw: (_ for _ in ()).throw(error))
    with pytest.raises(RuntimeError):
        setup_pipeline(sources=[SOURCE], targets=[TARGET], context=runtime)


def test_bootstrap_rejects_contract_overrides(plan_runtime):
    """Turning off interaction cannot silently ignore caller-supplied requirements."""
    _, runtime, _, _ = plan_runtime
    with pytest.raises(ValueError, match="Bootstrap does not accept"):
        setup_pipeline(sources=[SOURCE], targets=[TARGET], selections={"source": {"no_contract": True}}, context=runtime)


def test_read_only_bootstrap_requires_no_business_target(plan_runtime):
    """A source-only first run can register its catalogue/profile metadata."""
    _, runtime, _, _ = plan_runtime
    plan = setup_pipeline(sources=[SOURCE], targets=[], context=runtime)
    assert plan.permits_persistence and set(json.loads(plan.participants_json)) == {"source"}


def test_explicit_live_cannot_be_used_as_a_contract_free_bootstrap_override(plan_runtime):
    """The initial publishing exception belongs to Bootstrap, not an ungoverned Live run."""
    _, runtime, _, _ = plan_runtime
    with pytest.raises(ValueError, match="Live requires"):
        setup_pipeline(sources=[SOURCE], targets=[TARGET], execution_mode="live",
            selections={"source": {"no_contract": True}, "target": {"no_contract": True}}, context=runtime)
