"""Environment-neutral explicit plan validation and frozen contract authority."""

import importlib
import json

import pytest

from fabricops_kit.pipeline import shared
from tests.unit.test_contract_orchestration import frozen
from tests.unit.test_data_contract_resolution import RecordingFrame

module = importlib.import_module("fabricops_kit.pipeline.shared")


@pytest.fixture
def plan_runtime(monkeypatch):
    """Supply only metadata read and configured identity boundaries."""
    rows = []
    runtime = {"config": object(), "env": "canary-east", "notebook_id": "notebook"}
    def resolve(context=None):
        return runtime["config"], runtime["env"], dict(context or runtime)
    monkeypatch.setattr(module, "resolve_fabric_context", resolve)
    monkeypatch.setattr(shared, "resolve_fabric_context", resolve)
    monkeypatch.setattr(module, "resolve_physical_table_identity", lambda c, e, **kw: {
        **kw, "table_id": kw["table_name"], "store_kind": "lakehouse"})
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda *a, **kw: RecordingFrame(rows))
    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda *a: "metadata")
    def make(mode="testing", selections=None):
        return module.build_pipeline_execution_plan(execution_mode=mode,
            sources=[{"store": "Bronze", "schema": "demo", "table_name": "source"}],
            targets=[{"store": "Silver", "schema": "demo", "table_name": "target"}],
            selections=selections if selections is not None else {"source": {"no_contract": True}, "target": {"no_contract": True}},
            context=runtime)
    def row(table_id="source", version=1, active=False):
        result = frozen(table_id, version=version, active=active)
        result["environment_name"] = runtime["env"]
        return result
    return rows, runtime, make, row


@pytest.mark.parametrize("environment", ["dev", "test", "uat", "prod", "production", "canary-east", "sandbox42"])
@pytest.mark.parametrize("mode", ["testing", "live"])
def test_arbitrary_environment_has_identical_explicit_bootstrap_policy(plan_runtime, environment, mode):
    """Environment identity routes execution and never decides persistence or contracts."""
    _, runtime, make, _ = plan_runtime
    runtime["env"] = environment
    plan = make(mode)
    assert plan.environment == environment
    assert plan.permits_persistence is (mode == "live")
    assert json.loads(plan.selections_json)["target"] == {"no_contract": True}


def test_testing_can_select_inactive_candidate_but_live_cannot(plan_runtime):
    """Exact frozen version choices are independent by participant."""
    rows, _, make, row = plan_runtime
    rows.extend([row(active=True), row(version=2)])
    selections = {"source": {"contract_id": "contract-source", "contract_version": 2}, "target": {"no_contract": True}}
    plan = make(selections=selections)
    assert json.loads(plan.contracts_json)["source"]["contract_version"] == 2
    with pytest.raises(ValueError, match="active frozen"):
        make("live", selections)
    selections["source"]["contract_version"] = 1
    assert make("live", selections).execution_mode == "live"
    assert json.loads(plan.contracts_json)["source"]["contract_version"] == 2


@pytest.mark.parametrize("mode", ["testing", "live"])
def test_no_contract_cannot_bypass_active(plan_runtime, mode):
    """Explicit bootstrap never bypasses an existing active contract."""
    rows, _, make, row = plan_runtime
    rows.append(row(active=True))
    with pytest.raises(ValueError, match="bypass"):
        make(mode)


@pytest.mark.parametrize("corruption", ["json", "contract_id", "version", "table", "columns", "duplicate", "multiple_active"])
def test_corrupt_and_ambiguous_contracts_are_errors(plan_runtime, corruption):
    """No failed resolution is converted into an uncontracted plan."""
    rows, _, make, row = plan_runtime
    candidate = row()
    payload = json.loads(candidate["contract_payload_json"])
    if corruption == "contract_id": payload["contract"]["contract_id"] = "wrong"
    if corruption == "version": payload["contract"]["contract_version"] = 99
    if corruption == "table": payload["table"]["table_id"] = "unrelated"
    if corruption == "columns": payload["table"]["columns"][0].pop("data_type")
    candidate["contract_payload_json"] = "{bad" if corruption == "json" else json.dumps(payload)
    rows.append(candidate)
    if corruption == "duplicate": rows.append(dict(candidate))
    if corruption == "multiple_active": rows[:] = [row(active=True), row(version=2, active=True)]
    with pytest.raises((ValueError, RuntimeError)):
        make(selections={"source": {"contract_id": "contract-source", "contract_version": 1}, "target": {"no_contract": True}})


def test_metadata_scope_filters_other_environment_versions(plan_runtime):
    """A shared metadata store cannot leak another environment's active contracts."""
    rows, _, make, row = plan_runtime
    other = row(active=True)
    other["environment_name"] = "elsewhere"
    rows.append(other)
    assert json.loads(make("live").contracts_json)["source"] is None


def test_missing_and_unrelated_choices_rejected(plan_runtime):
    """Every configured participant needs an explicit choice; extra tables are rejected."""
    _, _, make, _ = plan_runtime
    with pytest.raises(ValueError, match="every participating"):
        make(selections={"source": {"no_contract": True}})
    with pytest.raises(ValueError, match="every participating"):
        make(selections={"source": {"no_contract": True}, "target": {"no_contract": True}, "unrelated": {"no_contract": True}})


def test_live_plan_rejects_active_version_changes_after_creation(plan_runtime):
    """All calls revalidate Live authority before evaluating or publishing."""
    rows, _, make, row = plan_runtime
    rows.append(row(active=True))
    plan = make("live", {"source": {"contract_id": "contract-source", "contract_version": 1}, "target": {"no_contract": True}})
    rows[:] = [row(version=2, active=True)]
    with pytest.raises(ValueError, match="changed after plan creation"):
        shared.prepare_pipeline_execution(["source"], execution_plan=plan)


def test_missing_contract_store_is_not_an_explicit_no_contract_state(plan_runtime, monkeypatch):
    """Unreadable metadata cannot authorize bootstrap by hiding active contracts."""
    _, _, make, _ = plan_runtime
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("Table not found")))
    with pytest.raises(RuntimeError, match="missing metadata table"):
        make("live")


@pytest.mark.parametrize("mode", ["testing", "live"])
def test_read_only_headless_plan_needs_no_target(plan_runtime, mode):
    """Read-only participants use the same immutable plan without a business target."""
    from fabricops_kit import setup_pipeline

    _, runtime, _, _ = plan_runtime
    plan = setup_pipeline(interactive=False, execution_mode=mode,
        sources=[{"store": "Bronze", "schema": "demo", "table_name": "source"}], targets=[],
        selections={"source": {"no_contract": True}}, context=runtime)
    assert json.loads(plan.participants_json)["source"]["roles"] == ["source"]
    assert set(json.loads(plan.contracts_json)) == {"source"}
