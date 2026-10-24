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
    context = {"config": {}, "env": "canary", "notebook_id": "notebook", "notebook_name": "pipeline", "workspace_id": "workspace"}
    monkeypatch.setattr(pipeline, "pipeline_physical_bindings", lambda identities, config, environment: config["bindings"])
    monkeypatch.setattr(service, "resolve_fabric_context", lambda context=None: (context["config"], context["env"], dict(context)))
    monkeypatch.setattr(pipeline, "resolve_fabric_context", service.resolve_fabric_context)
    monkeypatch.setattr(service, "build_runtime_audit_fields", lambda **kw: {})
    contracts, diagnostics, registrations = [], [], []
    monkeypatch.setattr(pipeline, "read_pipeline_registry", lambda **kw: ("registry-token", copy.deepcopy(registrations)))
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
    def candidate(pipeline_id="4c7ae400-85ab-4023-9427-e8fde20bd596", version=3, roles=("target",), env="canary", tables=None, destinations=None):
        plan = make(mode="testing", roles=roles)
        identities = json.loads(plan.participants_json)
        frozen, bindings = {}, {}
        tables = tables or list(identities)
        identities = {table: {**item, "table_id": table, "table_name": table} for table, item in zip(tables, identities.values())}
        for key, item in identities.items():
            selected_version = version[key] if isinstance(version, dict) else version
            payload = {"contract": {"contract_id": "contract-" + key, "contract_version": selected_version, "status": "frozen"},
                       "table": {"table_id": key, "columns": [], "processing": {"load_strategy": "overwrite"}}, "guardrails": [],
                       "profiling": {**pipeline.default_profiling_policy(), "standard": {"frequency": "interval", "days": 7, "trigger": "write"}}}
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
                operation(plan, int(table_id.removeprefix("table")), stages=[{"stage": "Read" if identities[table_id]["roles"] == ["source"] else "Processing", "status": "passed"}])
        run = plan.run_result
        # Results are retained by the test reviewer, never committed by Test.
        saved[plan.plan_id] = run
        run['guardrail_results'] = copy.deepcopy(diagnostics)
        run['testing_notebook_binding'] = {'workspace_id': 'workspace', 'notebook_id': 'notebook', 'activity_id': 'fabric-test-run'}
        registrations[:] = [row for row in registrations if (row['pipeline_id'], row['environment_name']) != (pipeline_id, env)]
        registrations.append({'pipeline_id': pipeline_id, 'environment_name': env, 'registration_status': 'Active',
                              'workspace_id': 'workspace', 'notebook_id': 'notebook'})
        run.update(_workspace_id="workspace", _notebook_id="notebook")
        return plan, run
    def request(run, release=None):
        return {"testing_result": run, "testing_run_id": run["run_id"], "candidate_fingerprint": run["candidate_fingerprint"],
                "pipeline_name": run["pipeline_id"], "pipeline_version": release or run["run_id"],
            "agreement_id": "agreement", "agreement_version": "1",
            "testing_verification": {"verified": True, "reference": "fabric-test-run"}}
    def approve(*runs, env="canary"):
        return service.approve_pipeline_release([request(run) for run in runs], expected_token=central["token"],
            governance_confirmed=True, context={**context, "env": env})
    def current(env="canary"):
        return service.environment_activation(central["state"], env)
    return SimpleNamespace(candidate=candidate, approve=approve, request=request, current=current, central=central,
                           context=context, saved=saved, contracts=contracts, diagnostics=diagnostics,
                           operation=operation, commit=commit, read=read)


def test_single_pipeline_activation_has_no_business_or_deployment_side_effects(authority, tmp_path):
    state = authority
    _, run = state.candidate()
    before = set(tmp_path.iterdir())
    result = state.approve(run)
    assert result["pipelines"]["4c7ae400-85ab-4023-9427-e8fde20bd596"]["testing_run_id"] == run["run_id"]
    assert state.current()["tables"]["table0"]["writer"] == "4c7ae400-85ab-4023-9427-e8fde20bd596"
    assert set(tmp_path.iterdir()) == before


def test_two_readers_are_allowed_and_competing_writers_rejected(authority):
    state = authority
    _, a = state.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596", roles=("source",))
    _, b = state.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031", roles=("source",))
    state.approve(a); state.approve(b)
    assert set(state.current()["tables"]["table0"]["readers"]) == {"4c7ae400-85ab-4023-9427-e8fde20bd596", "f5ee4669-5b76-4baf-9875-6cfecba2e031"}
    _, writer = state.candidate("e6a217ed-7303-41ff-9764-c6a1c9840723")
    # Writer ownership change requires replacing directly affected readers too.
    state.approve(writer, a, b)
    _, competing = state.candidate("c7c4db41-dada-4574-8cfd-df096eaf7c33")
    before = copy.deepcopy(state.central)
    with pytest.raises(ValueError, match="Competing writer"):
        state.approve(competing, a, b, writer)
    assert state.central == before


def test_v3_to_v4_requires_complete_coordinated_testing(authority):
    state = authority
    _, a3 = state.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596")
    _, b3 = state.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031", roles=("source",))
    state.approve(a3); state.approve(b3)
    _, a4 = state.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596", version=4)
    before = copy.deepcopy(state.central)
    with pytest.raises(ValueError, match="Missing replacement Testing candidate:"):
        state.approve(a4)
    assert state.central == before
    _, b4 = state.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031", version=4, roles=("source",))
    state.approve(a4, b4)
    assert state.current()["tables"]["table0"]["contract_version"] == 4
    assert set(state.current()["pipelines"]) == {"4c7ae400-85ab-4023-9427-e8fde20bd596", "f5ee4669-5b76-4baf-9875-6cfecba2e031"}
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


def test_unverified_handoff_and_previous_notebook_test_cannot_activate(authority):
    state = authority
    _, run = state.candidate()
    request = state.request(run)
    request["testing_verification"] = {"verified": False, "reference": "fabric-test-run"}
    with pytest.raises(ValueError, match="independently verify"):
        service.review_pipeline_release([request], context=state.context)
    request["testing_verification"] = {"verified": True, "reference": ""}
    with pytest.raises(ValueError, match="run reference"):
        service.review_pipeline_release([request], context=state.context)
    request = state.request(run)
    run["testing_notebook_binding"]["notebook_id"] = "previous-notebook"
    with pytest.raises(ValueError, match="current registered notebook"):
        service.review_pipeline_release([request], context=state.context)


def test_affected_failed_evidence_blocks_entire_release(authority):
    state = authority
    _, a = state.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596"); _, b = state.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031", roles=("source",))
    state.approve(a); state.approve(b)
    _, a4 = state.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596", version=4); _, b4 = state.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031", version=4, roles=("source",))
    b4["status"] = "failed"
    before = copy.deepcopy(state.central)
    with pytest.raises(ValueError, match="complete successful"):
        state.approve(a4, b4)
    assert state.central == before


def test_environment_isolation_shares_global_frozen_versions(authority):
    state = authority
    _, prod = state.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596", version=3)
    _, dev = state.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596", version=4, env="DEV")
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
    _, a = state.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596"); _, b = state.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031")
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
    live = service.build_live_pipeline_plan(pipeline_id="4c7ae400-85ab-4023-9427-e8fde20bd596", context=state.context)
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


def test_rebind_reservation_drains_live_and_blocks_new_live(authority, monkeypatch):
    state = authority
    plan, run = state.candidate()
    state.approve(run)
    identities = json.loads(plan.participants_json)
    monkeypatch.setattr(service, "resolve_pipeline_participants", lambda *a, **kw: identities)
    monkeypatch.setattr(pipeline, "pipeline_physical_bindings", lambda *a, **kw: plan.runtime_context["_pipeline_bindings"])
    identity = run["pipeline_id"]
    live = service.build_live_pipeline_plan(pipeline_id=identity, context=state.context)
    with pytest.raises(ValueError, match="Drain active Live runs"):
        service.reserve_pipeline_rebind(identity, context=state.context)
    live.evidence["boundary_completed"] = True
    pipeline.finalize_pipeline_run(live)
    lease_id = service.reserve_pipeline_rebind(identity, context=state.context)
    with pytest.raises(ValueError, match="rebinding is in progress"):
        service.build_live_pipeline_plan(pipeline_id=identity, context=state.context)
    service.release_pipeline_rebind(identity, lease_id, context=state.context)
    assert not state.current()["runs"]






def test_late_empty_boundary_cannot_authorize_previously_executed_operations(authority):
    state = authority
    original, _ = state.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596")
    plan = replace(original, plan_id="outside-boundary", evidence={})
    pipeline.persist_pipeline_run(plan)
    state.operation(plan, 0)
    with pytest.raises(RuntimeError, match="Transformation"):
        raise RuntimeError("Transformation in a subsequent notebook cell failed")
    with pytest.raises(RuntimeError, match="before executing any operation"):
        with plan:
            pass
    run = pipeline.persist_pipeline_run(plan)
    assert plan.plan_id not in state.saved
    assert run["status"] == "incomplete"
    assert json.loads(run["operation_summary_json"])["boundary_completed"] is False
    with pytest.raises(ValueError, match="complete successful"):
        state.approve(run)
    assert not state.current()["pipelines"]


def test_mutated_contract_cannot_authorize_activation(authority):
    state = authority
    _, run = state.candidate()
    state.contracts[0]["contract_payload_json"] += " "
    with pytest.raises(ValueError, match="Frozen contract changed"):
        state.approve(run)
    state.contracts[0]["contract_payload_json"] = state.contracts[0]["contract_payload_json"].rstrip()


def test_notebook_rename_preserves_pipeline_and_candidate_identity(authority):
    state = authority
    plan, _run = state.candidate()
    renamed = replace(plan, notebook_id="renamed-notebook", runtime_context={**plan.runtime_context, "notebook_name": "new-name"})
    assert pipeline.pipeline_candidate(renamed)[1] == pipeline.pipeline_candidate(plan)[1]
    assert renamed.pipeline_id == "4c7ae400-85ab-4023-9427-e8fde20bd596"


def test_downstream_retesting_follows_changed_output_expectations_only(authority):
    state = authority
    _, a3 = state.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596")
    _, b3 = state.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031", roles=("source", "target"))
    _, c3 = state.candidate("967adc28-d152-4c40-8f4b-44934515a312", roles=("source",), tables=["table1"])
    state.approve(a3); state.approve(b3); state.approve(c3)
    _, a4 = state.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596", version=4)
    _, b4 = state.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031", version={"table0": 4, "table1": 3}, roles=("source", "target"))
    state.approve(a4, b4)
    c_before = state.current()["pipelines"]["967adc28-d152-4c40-8f4b-44934515a312"]["activated_pipeline_id"]
    _, changed_output = state.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031", version=4, roles=("source", "target"))
    with pytest.raises(ValueError, match="Missing replacement Testing candidate:"):
        state.approve(changed_output)
    assert state.current()["pipelines"]["967adc28-d152-4c40-8f4b-44934515a312"]["activated_pipeline_id"] == c_before
    _, c4 = state.candidate("967adc28-d152-4c40-8f4b-44934515a312", version=4, roles=("source",), tables=["table1"])
    state.approve(changed_output, c4)
    assert state.current()["tables"]["table1"]["contract_version"] == 4




def test_live_operational_differences_warn_and_unsafe_changes_fail(authority, monkeypatch):
    state = authority
    plan, run = state.candidate()
    state.approve(run)
    monkeypatch.setattr(service, "resolve_pipeline_participants", lambda *a, **kw: json.loads(plan.participants_json))
    monkeypatch.setattr(pipeline, "pipeline_physical_bindings", lambda *a, **kw: plan.runtime_context["_pipeline_bindings"])
    live = service.build_live_pipeline_plan(pipeline_id="4c7ae400-85ab-4023-9427-e8fde20bd596", context=state.context)
    with pytest.warns(UserWarning, match="frequency_top_n"):
        with live:
            state.operation(live, 0, frequency_top_n=2)
    summary = json.loads(live.run_result["operation_summary_json"])
    assert summary["warnings"][0]["operational_parameters"] == ["frequency_top_n"]
    live = service.build_live_pipeline_plan(pipeline_id="4c7ae400-85ab-4023-9427-e8fde20bd596", context=state.context)
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




def test_standalone_consumer_does_not_choose_an_arbitrary_agreement(authority):
    state = authority
    _, a = state.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596", roles=("source",))
    _, b = state.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031", roles=("source",))
    state.approve(a); state.approve(b)
    assert service.resolve_approved_consumer_contract({}, "canary", "table0")["agreement_id"] == "agreement"
    row = state.current()["pipelines"]["f5ee4669-5b76-4baf-9875-6cfecba2e031"]
    manifest = json.loads(row["manifest_json"])
    manifest["agreement"]["agreement_id"] = "another-approved-agreement"
    row.update(agreement_id="another-approved-agreement", manifest_json=pipeline.canonical_candidate_json(manifest),
               activated_pipeline_id=service.manifest_digest(manifest))
    with pytest.raises(ValueError, match="unambiguous"):
        service.resolve_approved_consumer_contract({}, "canary", "table0")


def test_table_aliases_cannot_bypass_physical_writer_ownership(authority):
    state = authority
    plan, a = state.candidate("4c7ae400-85ab-4023-9427-e8fde20bd596")
    state.approve(a)
    _, alias = state.candidate("f5ee4669-5b76-4baf-9875-6cfecba2e031", tables=["table1"], destinations={"table1": plan.runtime_context["_pipeline_bindings"]["table0"]})
    before = copy.deepcopy(state.central["state"])
    with pytest.raises(ValueError, match="Conflicting table identities share a physical destination"):
        state.approve(alias)
    assert state.central["state"] == before




def test_manual_finalization_qualifies_without_executable_integrity(authority, monkeypatch):
    """Explicit end boundaries preserve coordinated governance without code exports."""
    from pathlib import Path
    from fabricops_kit.pipeline.shared import finalize_pipeline_run as finalize_pipeline
    def forbidden(*args, **kwargs):
        raise AssertionError('Engineering owns executable integrity')
    monkeypatch.setattr(Path, 'rglob', forbidden)
    monkeypatch.setattr('urllib.request.urlopen', forbidden)
    state = authority
    previous, _ = state.candidate()
    plan = replace(previous, plan_id=previous.plan_id + '-manual', evidence={}, results=[])
    pipeline.persist_pipeline_run(plan)
    state.operation(plan, 0, stages=[{"stage": "Processing", "status": "passed"}])
    plan.evidence["boundary_completed"] = True
    run = finalize_pipeline(plan)
    assert run['status'] == 'succeeded'
    state.approve(run)
    assert state.current()['pipelines'][plan.pipeline_id]['testing_run_id'] == plan.plan_id


def test_internal_completion_releases_existing_live_reservation(authority, monkeypatch):
    """Finalization closes the same atomic reservation used for coordinated cutover."""
    from fabricops_kit.pipeline.shared import finalize_pipeline_run as finalize_pipeline
    state = authority
    previous, run = state.candidate()
    state.approve(run)
    monkeypatch.setattr(service, 'resolve_pipeline_participants', lambda *args, **kwargs: json.loads(previous.participants_json))
    plan = service.build_live_pipeline_plan(pipeline_id=previous.pipeline_id, context=previous.runtime_context)
    assert plan.plan_id in state.current()['runs']
    state.operation(plan, 0)
    plan.evidence['boundary_completed'] = True
    assert finalize_pipeline(plan)['status'] == 'succeeded'
    assert plan.plan_id not in state.current()['runs']


@pytest.mark.parametrize("missing", [("table1",), ("table0", "table2"), ("table0", "table1", "table2")])
def test_completed_testing_with_missing_contracts_cannot_activate(authority, missing):
    """Completion under partial coverage never grants activation authority."""
    state = authority
    previous, _ = state.candidate(roles=("source", "source", "target"))
    contracts = json.loads(previous.contracts_json)
    for table_id in missing:
        contracts[table_id] = None
    plan = replace(previous, plan_id=previous.plan_id + "-mixed", contracts_json=json.dumps(contracts), evidence={}, results=[])
    pipeline.persist_pipeline_run(plan)
    for index in range(3):
        state.operation(plan, index)
    plan.evidence["boundary_completed"] = True
    run = pipeline.finalize_pipeline_run(plan)
    assert run["status"] == ("ungoverned_completed" if len(missing) == 3 else "succeeded")
    before = copy.deepcopy(state.central)
    with pytest.raises(ValueError, match="Missing contracts for table IDs: " + ", ".join(sorted(missing))):
        state.approve(run)
    assert state.central == before


def test_live_resolves_approved_versions_after_mixed_testing(authority, monkeypatch):
    """Later exploratory selections cannot replace the activated contract versions."""
    from fabricops_kit import setup_pipeline

    state = authority
    previous, approved_run = state.candidate(version={"table0": 1, "table1": 2}, roles=("source", "target"))
    state.approve(approved_run)
    contracts = json.loads(previous.contracts_json)
    contracts["table1"] = None
    exploratory = replace(previous, plan_id=previous.plan_id + "-explore", contracts_json=json.dumps(contracts), evidence={}, results=[])
    pipeline.persist_pipeline_run(exploratory)
    state.operation(exploratory, 0)
    state.operation(exploratory, 1)
    exploratory.evidence["boundary_completed"] = True
    run = pipeline.finalize_pipeline_run(exploratory)
    assert run["status"] == "succeeded"
    with pytest.raises(ValueError, match="table1"):
        state.approve(run)
    # Live receives no manual contract choices or participant lists.
    monkeypatch.setattr(service, "resolve_pipeline_participants", lambda *args, **kwargs: json.loads(previous.participants_json))
    live = service.build_live_pipeline_plan(pipeline_id="4c7ae400-85ab-4023-9427-e8fde20bd596", context=previous.runtime_context)
    assert {key: row["contract_version"] for key, row in json.loads(live.contracts_json).items()} == {"table0": 1, "table1": 2}
    assert live.activated_pipeline_id == state.current()["pipelines"]["4c7ae400-85ab-4023-9427-e8fde20bd596"]["activated_pipeline_id"]
    with live:
        state.operation(live, 0)
        state.operation(live, 1)
    assert live.run_result["status"] == "succeeded"


def test_activation_preserves_exact_profiling_and_policy_changes_require_new_testing(authority, monkeypatch):
    state = authority
    tested, run = state.candidate()
    state.approve(run)
    monkeypatch.setattr(service, 'resolve_pipeline_participants', lambda *args, **kwargs: json.loads(tested.participants_json))
    live = service.build_live_pipeline_plan(pipeline_id='4c7ae400-85ab-4023-9427-e8fde20bd596', context=tested.runtime_context)
    expected = json.loads(tested.contracts_json)
    actual = json.loads(live.contracts_json)
    for table_id, contract in actual.items():
        assert contract['contract_payload_json'] == expected[table_id]['contract_payload_json']
        assert pipeline.contract_profiling_policy(table_id, context={'_pipeline_contracts': actual})['standard'] == {
            'frequency': 'interval', 'days': 7, 'trigger': 'write'}
    changed = copy.deepcopy(expected)
    payload = json.loads(changed['table0']['contract_payload_json'])
    payload['profiling']['standard']['days'] = 14
    changed['table0']['contract_payload_json'] = pipeline.canonical_candidate_json(payload)
    revised = replace(tested, contracts_json=pipeline.canonical_candidate_json(changed))
    assert pipeline.pipeline_candidate(revised)[1] != pipeline.pipeline_candidate(tested)[1]
    assert json.loads(live.contracts_json) == actual


def test_registered_pipeline_cannot_run_live_without_environment_approval(authority):
    """An Active Engineering binding and successful Test never grant Live authority."""
    state = authority
    plan, _result = state.candidate()
    before = copy.deepcopy(state.central)
    with pytest.raises(ValueError, match='No approved pipeline configuration'):
        service.build_live_pipeline_plan(pipeline_id=plan.pipeline_id, context=plan.runtime_context)
    assert state.central == before
    assert not state.current()['history'] and not state.current()['runs']
