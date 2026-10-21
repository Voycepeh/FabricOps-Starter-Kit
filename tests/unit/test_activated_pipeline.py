"""Coordinated environment activation using real validation and simulated Delta transport."""
# ruff: noqa: D103, F811
from __future__ import annotations

import copy
import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from threading import Lock
from types import SimpleNamespace

import pytest

from fabricops_kit.activated_pipeline import shared as service
from fabricops_kit.pipeline import shared as pipeline
from tests.unit.test_pipeline_run_evidence import runtime  # noqa: F401


@pytest.fixture
def authority(runtime, monkeypatch, tmp_path):
    """Mock physical Fabric I/O only; keep fingerprints, run validation and dependency logic."""
    make, operation, saved, writes, failure = runtime
    executable = tmp_path / "project.ipynb"
    executable.write_text('{"cells":[{"cell_type":"code","source":["transform()"]}]}')
    digest = pipeline.notebook_executable_fingerprint(executable.read_bytes())
    context = {"config": {}, "env": "canary", "notebook_id": "notebook", "notebook_name": "pipeline", "workspace_id": "workspace"}
    monkeypatch.setattr(pipeline, "deployed_notebook_fingerprint", lambda runtime: digest)
    monkeypatch.setattr(pipeline, "pipeline_physical_bindings", lambda identities, config, environment: config["bindings"])
    monkeypatch.setattr(service, "resolve_fabric_context", lambda context=None: (context["config"], context["env"], dict(context)))
    monkeypatch.setattr(pipeline, "resolve_fabric_context", service.resolve_fabric_context)
    monkeypatch.setattr(service, "build_runtime_audit_fields", lambda **kw: {})
    contracts, diagnostics = [], []
    agreement = {"agreement_id": "agreement", "agreement_version": "1", "start_date": "2020-01-01", "expiry_date": "2099-01-01"}
    central = {"token": "initial", "state": json.loads(service.empty_activation_state()), "fail": False}
    lock = Lock()
    def records(table, **kwargs):
        return {"METADATA_PIPELINE_RUN": list(saved.values()), "METADATA_DATA_CONTRACT": contracts,
                "METADATA_GUARDRAIL_RESULTS": diagnostics, "METADATA_DATA_AGREEMENT": [agreement]}[table]
    monkeypatch.setattr(service, "metadata_records", records)
    def read(**kwargs):
        with lock:
            return central["token"], copy.deepcopy(central["state"])
    def commit(state, *, expected_token, **kwargs):
        with lock:
            if central["fail"]:
                raise OSError("simulated commit failure")
            if expected_token != central["token"]:
                raise ValueError("Stale activation revision")
            central["state"] = copy.deepcopy(state)
            central["token"] = str(int(central["token"]) + 1) if central["token"].isdigit() else "1"
            return central["token"]
    monkeypatch.setattr(service, "read_activation_state", read)
    monkeypatch.setattr(service, "commit_activation_state", commit)
    def candidate(pipeline_id="A", version=3, roles=("target",), env="canary", tables=None, destinations=None):
        plan = make(roles=roles, executable=digest)
        identities = json.loads(plan.participants_json)
        frozen, bindings = {}, {}
        tables = tables or list(identities)
        identities = {table: {**item, "table_id": table, "table_name": table} for table, item in zip(tables, identities.values())}
        for key, item in identities.items():
            selected_version = version[key] if isinstance(version, dict) else version
            payload = {"contract": {"contract_id": "contract-" + key, "contract_version": selected_version, "status": "frozen"},
                       "table": {"table_id": key, "columns": [], "processing": {"load_strategy": "overwrite"}}, "guardrails": []}
            contract = {"contract_id": "contract-" + key, "contract_version": selected_version, "status": "frozen", "table_id": key,
                        "environment_name": "DEV", "contract_payload_json": pipeline.canonical_candidate_json(payload)}
            frozen[key] = contract
            if contract not in contracts:
                contracts.append(contract)
            bindings[key] = (destinations or {}).get(key, {"workspace_id": env, "item_id": "lakehouse", "kind": "lakehouse", "schema": "physical", "table_name": key})
        # The operation fixture resolves physical table names to tableN IDs.
        assert tables == list(identities)
        plan = replace(plan, environment=env, pipeline_id=pipeline_id, contracts_json=pipeline.canonical_candidate_json(frozen),
                       participants_json=pipeline.canonical_candidate_json(identities), evidence={},
                       runtime_context={**context, "config": {"bindings": bindings}, "env": env, "_pipeline_bindings": bindings})
        pipeline.persist_pipeline_run(plan)
        with plan:
            for table_id in identities:
                operation(plan, int(table_id.removeprefix("table")))
        run = saved[plan.plan_id]
        run.update(_workspace_id="workspace", _notebook_id="notebook")
        return plan, run
    def request(run, release=None):
        return {"testing_run_id": run["run_id"], "candidate_fingerprint": run["candidate_fingerprint"],
                "pipeline_name": run["pipeline_id"], "pipeline_version": release or run["run_id"],
                "agreement_id": "agreement", "agreement_version": "1", "executable_path": str(executable)}
    def approve(*runs, env="canary"):
        return service.approve_pipeline_release([request(run) for run in runs], expected_token=central["token"],
            governance_confirmed=True, context={**context, "env": env})
    def current(env="canary"):
        return service.environment_activation(central["state"], env)
    return SimpleNamespace(candidate=candidate, approve=approve, request=request, current=current, central=central,
                           context=context, saved=saved, contracts=contracts, executable=executable, diagnostics=diagnostics,
                           operation=operation, digest=digest, commit=commit, read=read)


def test_single_pipeline_activation_has_no_business_or_deployment_side_effects(authority, tmp_path):
    state = authority
    _, run = state.candidate()
    before = set(tmp_path.iterdir())
    result = state.approve(run)
    assert result["pipelines"]["A"]["testing_run_id"] == run["run_id"]
    assert state.current()["tables"]["table0"]["writer"] == "A"
    assert set(tmp_path.iterdir()) == before


def test_two_readers_are_allowed_and_competing_writers_rejected(authority):
    state = authority
    _, a = state.candidate("A", roles=("source",))
    _, b = state.candidate("B", roles=("source",))
    state.approve(a); state.approve(b)
    assert set(state.current()["tables"]["table0"]["readers"]) == {"A", "B"}
    _, writer = state.candidate("Writer")
    # Writer ownership change requires replacing directly affected readers too.
    state.approve(writer, a, b)
    _, competing = state.candidate("OtherWriter")
    before = copy.deepcopy(state.central)
    with pytest.raises(ValueError, match="Competing writer"):
        state.approve(competing, a, b, writer)
    assert state.central == before


def test_v3_to_v4_requires_complete_coordinated_testing(authority):
    state = authority
    _, a3 = state.candidate("A")
    _, b3 = state.candidate("B", roles=("source",))
    state.approve(a3); state.approve(b3)
    _, a4 = state.candidate("A", version=4)
    before = copy.deepcopy(state.central)
    with pytest.raises(ValueError, match="Missing replacement Testing candidate: B"):
        state.approve(a4)
    assert state.central == before
    _, b4 = state.candidate("B", version=4, roles=("source",))
    state.approve(a4, b4)
    assert state.current()["tables"]["table0"]["contract_version"] == 4
    assert set(state.current()["pipelines"]) == {"A", "B"}
    assert all(service.manifest_table_mappings(service.validate_manifest(row))["table0"]["contract_version"] == 4
               for row in state.current()["pipelines"].values())


@pytest.mark.parametrize("field,value", [("status", "failed"), ("status", "incomplete"), ("status", "ungoverned_completed"),
                                         ("completed_at", None), ("candidate_fingerprint", "corrupt")])
def test_invalid_evidence_never_activates(authority, field, value):
    state = authority
    _, run = state.candidate()
    run[field] = value
    with pytest.raises((ValueError, TypeError)):
        state.approve(run)
    assert not state.current()["pipelines"]


def test_affected_failed_evidence_blocks_entire_release(authority):
    state = authority
    _, a = state.candidate("A"); _, b = state.candidate("B", roles=("source",))
    state.approve(a); state.approve(b)
    _, a4 = state.candidate("A", version=4); _, b4 = state.candidate("B", version=4, roles=("source",))
    b4["status"] = "failed"
    before = copy.deepcopy(state.central)
    with pytest.raises(ValueError, match="complete successful"):
        state.approve(a4, b4)
    assert state.central == before


def test_environment_isolation_shares_global_frozen_versions(authority):
    state = authority
    _, prod = state.candidate("A", version=3)
    _, dev = state.candidate("A", version=4, env="DEV")
    state.approve(prod); state.approve(dev, env="DEV")
    assert state.current()["tables"]["table0"]["contract_version"] == 3
    assert state.current("DEV")["tables"]["table0"]["contract_version"] == 4
    assert {row["environment_name"] for row in state.contracts} == {"DEV"}
    with pytest.raises(ValueError, match="activation environment"):
        state.approve(dev)


def test_failed_commit_and_stale_review_expose_no_partial_state(authority):
    state = authority
    _, run = state.candidate()
    before = copy.deepcopy(state.central["state"])
    state.central["fail"] = True
    with pytest.raises(OSError): state.approve(run)
    assert state.central["state"] == before
    state.central["fail"] = False
    token, snapshot = state.read()
    state.commit(snapshot, expected_token=token)
    with pytest.raises(ValueError, match="changed"):
        service.approve_pipeline_release([state.request(run)], expected_token=token, governance_confirmed=True, context=state.context)
    assert state.central["state"] == before


def test_concurrent_reviews_cannot_bypass_writer_consistency(authority):
    state = authority
    _, a = state.candidate("A"); _, b = state.candidate("B")
    token = state.central["token"]
    def approve(run):
        try:
            return service.approve_pipeline_release([state.request(run)], expected_token=token,
                governance_confirmed=True, context=state.context)
        except ValueError:
            return None
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(approve, [a, b]))
    assert sum(item is not None for item in results) == 1
    assert len(state.current()["pipelines"]) == 1


def test_live_run_pins_revision_and_drains_before_switch(authority, monkeypatch):
    state = authority
    plan, run = state.candidate()
    state.approve(run)
    identities = json.loads(plan.participants_json)
    monkeypatch.setattr(service, "resolve_pipeline_participants", lambda *a, **kw: identities)
    monkeypatch.setattr(pipeline, "pipeline_physical_bindings", lambda *a, **kw: plan.runtime_context["_pipeline_bindings"])
    live = service.build_live_pipeline_plan(pipeline_id="A", sources=[], targets=[], configuration={}, context=state.context)
    pinned = live.activation_revision
    _, next_run = state.candidate(version=4)
    with pytest.raises(ValueError, match="Drain running execution"):
        state.approve(next_run)
    assert live.activation_revision == pinned
    # Complete the running pipeline; no cutover may occur before the boundary exits.
    with live:
        state.operation(live, 0)
    state.approve(next_run)
    assert live.activation_revision == pinned != state.current()["revision"]


def test_testing_writes_reserve_separate_destinations_and_respect_live(authority):
    state = authority
    plan, run = state.candidate()
    state.approve(run)
    testing = replace(plan, plan_id="testing-write", evidence={}, testing_writes=True)
    with pytest.raises(ValueError, match="Live-owned"):
        service.reserve_testing_destinations(testing)
    bindings = copy.deepcopy(plan.runtime_context["_pipeline_bindings"])
    bindings["table0"]["item_id"] = "separate-testing-lakehouse"
    testing = replace(testing, runtime_context={**testing.runtime_context, "config": {"bindings": bindings}, "_pipeline_bindings": bindings}, evidence={})
    service.reserve_testing_destinations(testing)
    assert testing.permits_persistence and testing.plan_id in state.current()["runs"]
    service.release_pipeline_lease(testing)
    assert testing.plan_id not in state.current()["runs"]


def test_same_environment_activation_respects_testing_reservation_under_another_table_identity(authority):
    state = authority
    plan, _ = state.candidate("TestingA")
    testing = replace(plan, plan_id="running-testing", evidence={}, testing_writes=True)
    service.reserve_testing_destinations(testing)
    physical = plan.runtime_context["_pipeline_bindings"]["table0"]
    _, run = state.candidate("LiveB", tables=["table1"], destinations={"table1": physical})
    before = copy.deepcopy(state.central)
    _, _, _, report = service.review_pipeline_release([state.request(run)], context=state.context)
    assert not report["ready"]
    assert any("running-testing" in conflict for conflict in report["blocking_conflicts"])
    with pytest.raises(ValueError, match="Drain Testing execution"):
        state.approve(run)
    assert state.central == before
    service.release_pipeline_lease(testing)
    state.approve(run)
    assert state.current()["tables"]["table1"]["destination"] == physical


def test_late_empty_boundary_cannot_authorize_previously_executed_operations(authority):
    state = authority
    original, _ = state.candidate("A")
    plan = replace(original, plan_id="outside-boundary", evidence={})
    pipeline.persist_pipeline_run(plan)
    state.operation(plan, 0)
    with pytest.raises(RuntimeError, match="Transformation"):
        raise RuntimeError("Transformation in a subsequent notebook cell failed")
    with pytest.raises(RuntimeError, match="before executing any operation"):
        with plan:
            pass
    run = state.saved[plan.plan_id]
    assert run["status"] == "incomplete"
    assert json.loads(run["operation_summary_json"])["boundary_completed"] is False
    with pytest.raises(ValueError, match="complete successful"):
        state.approve(run)
    assert not state.current()["pipelines"]


def test_mutated_executable_or_contract_cannot_authorize_activation(authority):
    state = authority
    _, run = state.candidate()
    state.contracts[0]["contract_payload_json"] += " "
    with pytest.raises(ValueError, match="Frozen contract changed"):
        state.approve(run)
    state.contracts[0]["contract_payload_json"] = state.contracts[0]["contract_payload_json"].rstrip()
    state.executable.write_text('{"cells":[{"cell_type":"code","source":"changed()"}]}')
    with pytest.raises(ValueError, match="executable changed"):
        state.approve(run)


def test_notebook_rename_preserves_pipeline_and_candidate_identity(authority):
    state = authority
    plan, _run = state.candidate()
    renamed = replace(plan, notebook_id="renamed-notebook", runtime_context={**plan.runtime_context, "notebook_name": "new-name"})
    assert pipeline.pipeline_candidate(renamed)[1] == pipeline.pipeline_candidate(plan)[1]
    assert renamed.pipeline_id == "A"


def test_downstream_retesting_follows_changed_output_expectations_only(authority):
    state = authority
    _, a3 = state.candidate("A")
    _, b3 = state.candidate("B", roles=("source", "target"))
    _, c3 = state.candidate("C", roles=("source",), tables=["table1"])
    state.approve(a3); state.approve(b3); state.approve(c3)
    _, a4 = state.candidate("A", version=4)
    _, b4 = state.candidate("B", version={"table0": 4, "table1": 3}, roles=("source", "target"))
    state.approve(a4, b4)
    c_before = state.current()["pipelines"]["C"]["activated_pipeline_id"]
    _, changed_output = state.candidate("B", version=4, roles=("source", "target"))
    with pytest.raises(ValueError, match="Missing replacement Testing candidate: C"):
        state.approve(changed_output)
    assert state.current()["pipelines"]["C"]["activated_pipeline_id"] == c_before
    _, c4 = state.candidate("C", version=4, roles=("source",), tables=["table1"])
    state.approve(changed_output, c4)
    assert state.current()["tables"]["table1"]["contract_version"] == 4


def test_real_testing_run_in_another_environment_does_not_block_distinct_destinations(authority):
    state = authority
    plan, _run = state.candidate("A", env="DEV")
    testing = replace(plan, plan_id="dev-testing", evidence={}, testing_writes=True)
    service.reserve_testing_destinations(testing)
    _, prod = state.candidate("A", env="canary")
    state.approve(prod)
    assert state.current("DEV")["runs"]["dev-testing"]["mode"] == "testing"
    service.validate_testing_destinations(testing)
    service.release_pipeline_lease(testing)


def test_live_operational_differences_warn_and_unsafe_changes_fail(authority, monkeypatch):
    state = authority
    plan, run = state.candidate()
    state.approve(run)
    monkeypatch.setattr(service, "resolve_pipeline_participants", lambda *a, **kw: json.loads(plan.participants_json))
    monkeypatch.setattr(pipeline, "pipeline_physical_bindings", lambda *a, **kw: plan.runtime_context["_pipeline_bindings"])
    live = service.build_live_pipeline_plan(pipeline_id="A", sources=[], targets=[], configuration={}, context=state.context)
    with pytest.warns(UserWarning, match="frequency_top_n"):
        with live:
            state.operation(live, 0, frequency_top_n=2)
    summary = json.loads(live.run_result["operation_summary_json"])
    assert summary["warnings"][0]["operational_parameters"] == ["frequency_top_n"]
    live = service.build_live_pipeline_plan(pipeline_id="A", sources=[], targets=[], configuration={}, context=state.context)
    with pytest.raises(ValueError, match="configuration differs"):
        with live:
            state.operation(live, 0, write_mode="append")
    assert live.run_result["status"] == "failed"


def test_testing_destination_bindings_are_part_of_exact_candidate_identity(authority):
    state = authority
    plan, run = state.candidate()
    summary = json.loads(run["operation_summary_json"])
    summary["physical_bindings"]["table0"]["item_id"] = "different-lakehouse"
    run["operation_summary_json"] = json.dumps(summary)
    with pytest.raises(ValueError, match="destination bindings"):
        state.approve(run)
    bindings = copy.deepcopy(plan.runtime_context["_pipeline_bindings"])
    bindings["table0"]["item_id"] = "different-lakehouse"
    changed = replace(plan, runtime_context={**plan.runtime_context, "_pipeline_bindings": bindings})
    original_candidate, original_fingerprint, _ = pipeline.pipeline_candidate(plan)
    changed_candidate, changed_fingerprint, _ = pipeline.pipeline_candidate(changed)
    assert original_fingerprint != changed_fingerprint
    assert original_candidate["portable_fingerprint"] == changed_candidate["portable_fingerprint"]


def test_testing_write_rejects_a_midrun_destination_configuration_change(authority):
    state = authority
    plan, _ = state.candidate(env="DEV")
    testing = replace(plan, plan_id="testing-change", evidence={}, testing_writes=True)
    service.reserve_testing_destinations(testing)
    changed = copy.deepcopy(testing.runtime_context["_pipeline_bindings"])
    changed["table0"]["item_id"] = "unreviewed-destination"
    rerouted = replace(testing, runtime_context={**testing.runtime_context, "config": {"bindings": changed}})
    with pytest.raises(ValueError, match="physical destinations changed"):
        service.validate_testing_destinations(rerouted)
    service.release_pipeline_lease(testing)


def test_standalone_consumer_does_not_choose_an_arbitrary_agreement(authority):
    state = authority
    _, a = state.candidate("A", roles=("source",))
    _, b = state.candidate("B", roles=("source",))
    state.approve(a); state.approve(b)
    assert service.resolve_approved_consumer_contract({}, "canary", "table0")["agreement_id"] == "agreement"
    row = state.current()["pipelines"]["B"]
    manifest = json.loads(row["manifest_json"])
    manifest["agreement"]["agreement_id"] = "another-approved-agreement"
    row.update(agreement_id="another-approved-agreement", manifest_json=pipeline.canonical_candidate_json(manifest),
               activated_pipeline_id=service.manifest_digest(manifest))
    with pytest.raises(ValueError, match="unambiguous"):
        service.resolve_approved_consumer_contract({}, "canary", "table0")


def test_table_aliases_cannot_bypass_physical_writer_ownership(authority):
    state = authority
    plan, a = state.candidate("A")
    state.approve(a)
    _, alias = state.candidate("B", tables=["table1"], destinations={"table1": plan.runtime_context["_pipeline_bindings"]["table0"]})
    before = copy.deepcopy(state.central["state"])
    with pytest.raises(ValueError, match="Conflicting table identities share a physical destination"):
        state.approve(alias)
    assert state.central["state"] == before


def test_testing_write_cannot_overwrite_an_active_read_only_consumers_input(authority):
    state = authority
    _, reader = state.candidate("Reader", roles=("source",))
    state.approve(reader)
    plan, _ = state.candidate("TestingWriter")
    testing = replace(plan, plan_id="testing-consumer-input", evidence={}, testing_writes=True)
    with pytest.raises(ValueError, match="Live-owned"):
        service.reserve_testing_destinations(testing)
