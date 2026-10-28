"""Dry Run and Ungoverned replace the removed Bootstrap execution mode."""
# ruff: noqa: D103, F811
import json
from dataclasses import replace

import pytest

from fabricops_kit.pipeline.shared import build_pipeline_execution_plan
from fabricops_kit.pipeline import shared
from tests.unit.test_execution_plan import plan_runtime  # noqa: F401
from tests.unit.test_pipeline_run_evidence import runtime  # noqa: F401

SOURCE = {"store": "Bronze", "schema": "demo", "table_name": "source"}
TARGET = {"store": "Silver", "schema": "demo", "table_name": "target"}


def test_headless_exploration_uses_dry_run_and_never_activates(plan_runtime):
    _, context, _, _ = plan_runtime
    plan = build_pipeline_execution_plan(execution_mode="dry_run", sources=[SOURCE], targets=[TARGET], pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", context=context)
    assert plan.execution_mode == "dry_run" and not plan.permits_persistence
    assert json.loads(plan.contracts_json) == {"source": None, "target": None}


def test_contract_free_completed_run_is_explicitly_ungoverned(runtime):
    make, operation, saved, _, _ = runtime
    original = make(roles=("source",))
    plan = replace(original, execution_mode="ungoverned", contracts_json=json.dumps({"table0": None}), evidence={})
    with plan:
        operation(plan, 0)
    assert saved[plan.plan_id]["status"] == "ungoverned_completed"


def test_partial_contract_selection_is_valid_testing(plan_runtime):
    rows, _, make, row = plan_runtime
    rows.append(row())
    plan = make(selections={"source": {"contract_id": "contract-source", "contract_version": 1}, "target": {"no_contract": True}})
    assert json.loads(plan.contracts_json)["source"]["contract_version"] == 1
    assert json.loads(plan.contracts_json)["target"] is None


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
    with pytest.raises(ValueError, match="dry_run, ungoverned or governed"):
        build_pipeline_execution_plan(sources=[SOURCE], targets=[], pipeline_id="8f32a471-6c91-4b7e-9d13-2f0c947eab52", execution_mode="bootstrap", context=context)
    with pytest.raises(ValueError, match="UUIDv4"):
        build_pipeline_execution_plan(execution_mode="dry_run", sources=[SOURCE], targets=[], context=context)
