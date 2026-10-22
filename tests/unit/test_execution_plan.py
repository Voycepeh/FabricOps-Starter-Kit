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
    monkeypatch.setattr(shared, "persist_pipeline_run", lambda *a, **kw: None)
    monkeypatch.setattr(shared, "pipeline_physical_bindings", lambda identities, **kw: {key: {"workspace_id": "test", "item_id": "lakehouse", "kind": "lakehouse", "schema": item.get("schema"), "table_name": item["table_name"]} for key, item in identities.items()})
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
            context=runtime, pipeline_id="example")
    def row(table_id="source", version=1, active=False):
        result = frozen(table_id, version=version, active=active)
        result["environment_name"] = runtime["env"]
        return result
    return rows, runtime, make, row


@pytest.mark.parametrize("environment", ["dev", "test", "uat", "prod", "production", "canary-east", "sandbox42"])
@pytest.mark.parametrize("mode", ["testing"])
def test_arbitrary_environment_has_identical_explicit_bootstrap_policy(plan_runtime, environment, mode):
    """Environment identity routes execution and never decides persistence or contracts."""
    _, runtime, make, _ = plan_runtime
    runtime["env"] = environment
    plan = make(mode)
    assert plan.environment == environment
    assert plan.permits_persistence is False
    assert json.loads(plan.selections_json)["target"] == {"no_contract": True}


def test_testing_can_select_inactive_candidate_but_live_cannot(plan_runtime):
    """Exact frozen version choices are independent by participant."""
    rows, _, make, row = plan_runtime
    rows.extend([row(active=True), row(version=2), row(table_id="target", active=True)])
    selections = {"source": {"contract_id": "contract-source", "contract_version": 2}, "target": {"contract_id": "contract-target", "contract_version": 1}}
    plan = make(selections=selections)
    assert json.loads(plan.contracts_json)["source"]["contract_version"] == 2
    with pytest.raises(ValueError, match="Activated Pipeline"):
        make("live", selections)
    selections["source"]["contract_version"] = 1
    with pytest.raises(ValueError, match="Activated Pipeline"):
        make("live", selections)
    assert json.loads(plan.contracts_json)["source"]["contract_version"] == 2


def test_testing_no_contract_is_diagnostic_only_even_when_legacy_active_flag_exists(plan_runtime):
    """Legacy active contract columns grant no Live authority and do not choose Testing contracts."""
    rows, _, make, row = plan_runtime
    rows.append(row(active=True))
    assert json.loads(make().contracts_json)["source"] is None
    with pytest.raises(ValueError, match="Activated Pipeline"):
        make("live")


@pytest.mark.parametrize("corruption", ["json", "contract_id", "version", "table", "columns", "duplicate"])
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


def test_global_contracts_are_available_across_environments(plan_runtime):
    """A frozen contract is shared globally rather than copied per environment."""
    rows, runtime, make, row = plan_runtime
    rows.extend([{**row(), "environment_name": "DEV"}, {**row(table_id="target"), "environment_name": "DEV"}])
    runtime["env"] = "PROD"
    plan = make(selections={key: {"contract_id": "contract-" + key, "contract_version": 1} for key in ("source", "target")})
    assert json.loads(plan.contracts_json)["source"]["environment_name"] == "DEV"


def test_missing_and_unrelated_choices_rejected(plan_runtime):
    """Every configured participant needs an explicit choice; extra tables are rejected."""
    _, _, make, _ = plan_runtime
    with pytest.raises(ValueError, match="every participating"):
        make(selections={"source": {"no_contract": True}})
    with pytest.raises(ValueError, match="every participating"):
        make(selections={"source": {"no_contract": True}, "target": {"no_contract": True}, "unrelated": {"no_contract": True}})


def test_live_builder_rejects_individual_contract_authority(plan_runtime):
    """Even matching legacy active flags cannot construct a Live execution plan."""
    rows, _, make, row = plan_runtime
    rows.extend([row(active=True), row(table_id="target", active=True)])
    with pytest.raises(ValueError, match="Activated Pipeline"):
        make("live", {"source": {"contract_id": "contract-source", "contract_version": 1}, "target": {"contract_id": "contract-target", "contract_version": 1}})


def test_removed_bootstrap_mode_is_rejected(plan_runtime):
    """Contract-free exploration uses Testing with explicit write authorization."""
    _, _, make, _ = plan_runtime
    with pytest.raises(ValueError, match="testing or live"):
        make("bootstrap")


@pytest.mark.parametrize("mode", ["testing"])
def test_read_only_headless_plan_needs_no_target(plan_runtime, mode):
    """Read-only participants use the same immutable plan without a business target."""
    from fabricops_kit.pipeline.shared import build_pipeline_execution_plan

    rows, runtime, _, row = plan_runtime
    if mode == "live":
        rows.append(row(active=True))
    plan = build_pipeline_execution_plan(execution_mode=mode,
        sources=[{"store": "Bronze", "schema": "demo", "table_name": "source"}], targets=[],
        selections={"source": {"contract_id": "contract-source", "contract_version": 1} if mode == "live" else {"no_contract": True}}, context=runtime, pipeline_id="example")
    assert json.loads(plan.participants_json)["source"]["roles"] == ["source"]
    assert set(json.loads(plan.contracts_json)) == {"source"}


def test_testing_attempts_preserve_activity_and_isolate_transient_engine_state(plan_runtime):
    """Separate attempts within one Fabric activity keep independent observation caches."""
    _, context, make, _ = plan_runtime
    context["activity_id"] = "actual-fabric-activity"
    first, second = make(), make()
    assert first.runtime_context["activity_id"] == second.runtime_context["activity_id"] == "actual-fabric-activity"
    first_engine = shared.prepare_pipeline_execution(["source"], execution_plan=first)
    second_engine = shared.prepare_pipeline_execution(["source"], execution_plan=second)
    assert first_engine["activity_id"] == first.plan_id
    assert second_engine["activity_id"] == second.plan_id
    assert first_engine["activity_id"] != second_engine["activity_id"]
