"""Contract-free Testing replaces the removed Bootstrap execution mode."""
# ruff: noqa: D103, F811
import json
from dataclasses import replace

import pytest

from fabricops_kit import setup_pipeline
from fabricops_kit.pipeline import shared
from tests.unit.test_execution_plan import plan_runtime  # noqa: F401
from tests.unit.test_pipeline_run_evidence import runtime  # noqa: F401

SOURCE = {"store": "Bronze", "schema": "demo", "table_name": "source"}
TARGET = {"store": "Silver", "schema": "demo", "table_name": "target"}


def test_headless_exploration_uses_testing_and_never_activates(plan_runtime):
    _, context, _, _ = plan_runtime
    plan = setup_pipeline(sources=[SOURCE], targets=[TARGET], pipeline_id="explore", interactive=False, context=context)
    assert plan.execution_mode == "testing" and not plan.permits_persistence
    assert json.loads(plan.contracts_json) == {"source": None, "target": None}


def test_contract_free_completed_run_is_explicitly_ungoverned(runtime):
    make, operation, saved, _, _ = runtime
    original = make(roles=("source",))
    plan = replace(original, contracts_json=json.dumps({"table0": None}), evidence={})
    with plan:
        operation(plan, 0)
    assert saved[plan.plan_id]["status"] == "ungoverned_completed"


def test_partial_contract_selection_is_rejected(plan_runtime):
    rows, _, make, row = plan_runtime
    rows.append(row())
    with pytest.raises(ValueError, match="Partial contract selection"):
        make(selections={"source": {"contract_id": "contract-source", "contract_version": 1}, "target": {"no_contract": True}})


def test_automatic_boundary_includes_external_transform_failures(runtime):
    make, operation, saved, writes, _ = runtime
    plan = make(roles=("source",))
    with pytest.raises(ArithmeticError):
        with plan:
            operation(plan, 0)
            raise ArithmeticError("private business value")
    assert saved[plan.plan_id]["status"] == "failed"
    assert "private business value" not in json.dumps(saved[plan.plan_id], default=str)
    count = len(writes)
    assert shared.finalize_pipeline_run(plan)["status"] == "failed"
    assert len(writes) == count


def test_read_only_boundary_success_and_abandoned_incomplete(runtime):
    make, operation, saved, _, _ = runtime
    complete = make(roles=("source",))
    with complete:
        operation(complete, 0)
    assert saved[complete.plan_id]["status"] == "succeeded"
    abandoned = make(roles=("source",))
    operation(abandoned, 0)
    assert saved[abandoned.plan_id]["status"] == "incomplete"
    incomplete = make(roles=("source", "source"))
    with incomplete:
        operation(incomplete, 0)
    assert saved[incomplete.plan_id]["status"] == "incomplete"


def test_old_mode_and_missing_stable_identity_are_rejected(plan_runtime):
    _, context, _, _ = plan_runtime
    with pytest.raises(ValueError, match="testing or live"):
        setup_pipeline(sources=[SOURCE], targets=[], pipeline_id="explore", execution_mode="bootstrap", context=context)
    with pytest.raises(ValueError, match="stable pipeline_id"):
        setup_pipeline(sources=[SOURCE], targets=[], interactive=False, context=context)
