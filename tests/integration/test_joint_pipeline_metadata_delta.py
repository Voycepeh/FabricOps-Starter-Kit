"""Joint definition, approval, admission, rebind and profiling publication proofs."""
# ruff: noqa: D103, F811
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime
import json
from threading import Barrier, local

import pytest

from fabricops_kit import finalize_pipeline
from fabricops_kit.activated_pipeline import shared as authority
from fabricops_kit.pipeline import shared as pipeline
from tests.integration.test_activation_state_delta import authority_delta
from tests.integration.test_pipeline_run_delta import runs_delta

pytestmark = pytest.mark.spark


def approved_runtime(r, monkeypatch):
    plan = r.make()
    r.complete(plan)
    result = finalize_pipeline(pipeline.PipelineSession(plan, r.spark))
    request = {"testing_run_id": plan.plan_id, "candidate_fingerprint": result["candidate_fingerprint"],
        "pipeline_name": "Orders", "pipeline_version": "1", "agreement_id": "agreement", "agreement_version": "1"}
    token, _state = authority.read_pipeline_authority(context=r.context, spark_session=r.spark)
    approval = authority.approve_pipeline_release([request], expected_token=token, governance_confirmed=True,
        context=r.context, spark_session=r.spark)
    monkeypatch.setattr(authority, "resolve_pipeline_participants", lambda *a, **kw: json.loads(plan.participants_json))
    monkeypatch.setattr(pipeline, "pipeline_physical_bindings", lambda *a, **kw: plan.runtime_context["_pipeline_bindings"])
    return plan, request, approval


def test_finalized_test_approval_and_live_resolve_one_retained_definition(runs_delta, monkeypatch):
    r = runs_delta
    test, request, approved = approved_runtime(r, monkeypatch)
    before = r.spark.read.format("delta").load(r.paths["METADATA_PIPELINE_DEFINITION"]).count()
    live = authority.build_live_pipeline_plan(pipeline_id=test.pipeline_id, context=r.context, spark_session=r.spark)
    assert live.activated_pipeline_id == approved["pipelines"][test.pipeline_id]["activated_pipeline_id"]
    assert before == r.spark.read.format("delta").load(r.paths["METADATA_PIPELINE_DEFINITION"]).count() == 1
    rows = r.rows()
    assert len({row["definition_id"] for row in rows}) == 1
    assert all("candidate_json" not in row for row in rows)
    r.complete(live)
    pipeline.finalize_pipeline_run(live, spark_session=r.spark)
    _token, state = authority.read_pipeline_authority(context=r.context, spark_session=r.spark)
    current = authority.environment_activation(state, "DEV")
    assert not current["runs"] and len(current["history"]) == 1
    # Reapproval is independent decision history over the same immutable definition.
    request["pipeline_version"] = "2"
    authority.approve_pipeline_release([request], expected_token=_token, governance_confirmed=True,
        context=r.context, spark_session=r.spark)
    native = authority.authority_records(context=r.context, spark_session=r.spark)
    assert len(native["approvals"]) == 2 and len({item["definition_id"] for item in native["approvals"]}) == 1
    token, state = authority.read_pipeline_authority(context=r.context, spark_session=r.spark)
    current = authority.environment_activation(state, "DEV")
    current["history"].pop(next(key for key in current["history"] if key != current["pipelines"][test.pipeline_id]["activated_pipeline_id"]))
    with pytest.raises(ValueError, match="immutable and retained"):
        authority.commit_pipeline_authority(state, expected_token=token, context=r.context, spark_session=r.spark)


@pytest.mark.parametrize("defect", ["missing", "duplicate", "altered", "contract", "agreement", "testing"])
def test_missing_duplicate_or_altered_references_block_live(runs_delta, monkeypatch, defect):
    from delta.tables import DeltaTable
    r = runs_delta
    test, _request, _approved = approved_runtime(r, monkeypatch)
    definition = DeltaTable.forPath(r.spark, r.paths["METADATA_PIPELINE_DEFINITION"])
    if defect == "missing":
        definition.delete()
    elif defect == "duplicate":
        r.spark.read.format("delta").load(r.paths["METADATA_PIPELINE_DEFINITION"]).write.format("delta").mode("append").save(r.paths["METADATA_PIPELINE_DEFINITION"])
    elif defect == "altered":
        definition.update(set={"project_configuration_json": "'{\"changed\":true}'"})
    elif defect == "contract":
        DeltaTable.forPath(r.spark, r.paths["METADATA_DATA_CONTRACT"]).update(set={"contract_payload_json": "'{}'"})
    elif defect == "agreement":
        DeltaTable.forPath(r.spark, r.paths["METADATA_DATA_AGREEMENT"]).update(set={"business_purpose": "'altered'"})
    else:
        DeltaTable.forPath(r.spark, r.paths["METADATA_GUARDRAIL_RESULTS"]).delete()
    with pytest.raises(ValueError):
        authority.build_live_pipeline_plan(pipeline_id=test.pipeline_id, context=r.context, spark_session=r.spark)
    native = authority.authority_records(context=r.context, spark_session=r.spark)
    assert native["reservations"] == []


def test_orphaned_sealed_definition_cannot_authorize_execution(runs_delta):
    r = runs_delta
    test = r.make()
    r.complete(test)
    candidate, fingerprint, _bindings = pipeline.pipeline_candidate(test)
    identity = pipeline.seal_pipeline_definition(candidate, environment="DEV", fingerprint=fingerprint,
        context=r.context, spark_session=r.spark)
    assert pipeline.seal_pipeline_definition(candidate, environment="DEV", fingerprint=fingerprint,
        context=r.context, spark_session=r.spark) == identity
    assert r.rows() == []
    with pytest.raises(ValueError, match="No approved pipeline"):
        authority.build_live_pipeline_plan(pipeline_id=test.pipeline_id, context=r.context, spark_session=r.spark)


@pytest.mark.parametrize("competitor", ["approval", "rebind", "profiling"])
def test_live_admission_races_share_the_registry_cas(runs_delta, monkeypatch, competitor):
    r = runs_delta
    test, request, _approved = approved_runtime(r, monkeypatch)
    from types import SimpleNamespace
    physical = test.runtime_context["_pipeline_bindings"]["table0"]
    monkeypatch.setattr(pipeline, "profiling_context_key", lambda *a, **kw: ("profile-key", {"table_id": "table0", "environment": "DEV", "physical": physical}))
    monkeypatch.setattr(pipeline, "profiling_completion_history", lambda *a, **kw: {})
    commit = authority.commit_pipeline_authority
    barrier, thread = Barrier(2), local()
    def guarded(state, **kwargs):
        if not getattr(thread, "arrived", False):
            thread.arrived = True
            barrier.wait(timeout=60)
        return commit(state, **kwargs)
    monkeypatch.setattr(authority, "commit_pipeline_authority", guarded)
    def start():
        return authority.build_live_pipeline_plan(pipeline_id=test.pipeline_id, context=r.context, spark_session=r.spark)
    def competing():
        if competitor == "approval":
            token, _state = authority.read_pipeline_authority(context=r.context, spark_session=r.spark)
            return authority.approve_pipeline_release([{**request, "pipeline_version": "2"}], expected_token=token,
                governance_confirmed=True, context=r.context, spark_session=r.spark)
        if competitor == "rebind":
            return pipeline.resolve_pipeline_registration(test.pipeline_id,
                context={**r.context, "notebook_id": "replacement"}, previous_binding=("workspace", "notebook"), spark_session=r.spark)
        claim = pipeline.claim_table_profile("table0", "standard", "read", context={**r.context,
            "execution_plan": SimpleNamespace(plan_id="profile-owner", permits_persistence=True)}, spark_session=r.spark)
        return None if claim.get("status") == "skipped" else claim
    def attempt(function):
        try:
            return function()
        except Exception:
            return None
    with ThreadPoolExecutor(2) as pool:
        outcomes = list(pool.map(attempt, (start, competing)))
    assert sum(item is not None for item in outcomes) == 1
    monkeypatch.setattr(authority, "commit_pipeline_authority", commit)
    token, state = authority.read_pipeline_authority(context=r.context, spark_session=r.spark)
    current = authority.environment_activation(state, "DEV")
    assert len(current["history"]) in {1, 2}
    if outcomes[0] is not None:
        assert len(current["runs"]) == 1
        authority.release_pipeline_lease(outcomes[0], spark_session=r.spark)
    else:
        assert not current["runs"]
        if competitor == "profiling":
            assert state["profiling_claims"]["profile-key:standard"]["execution_id"] == "profile-owner"


def test_exact_content_readback_after_lost_authority_acknowledgement(authority_delta, monkeypatch):
    from delta.tables import DeltaTable
    r = authority_delta
    token, state = authority.read_pipeline_authority(context=r.context, spark_session=r.spark)
    authority.environment_activation(state, "DEV")["revision"] = "committed"
    original = DeltaTable.merge
    class LostAck:
        def __init__(self, builder): self.builder = builder
        def whenMatchedUpdate(self, **kwargs):
            self.builder = self.builder.whenMatchedUpdate(**kwargs)
            return self
        def execute(self):
            self.builder.execute()
            raise OSError("acknowledgement lost after physical commit")
    monkeypatch.setattr(DeltaTable, "merge", lambda self, *a, **kw: LostAck(original(self, *a, **kw)))
    committed = authority.commit_pipeline_authority(state, expected_token=token, context=r.context, spark_session=r.spark)
    assert authority.read_pipeline_authority(context=r.context, spark_session=r.spark) == (committed, state)


def test_concurrent_definition_sealing_is_unique_and_idempotent(runs_delta):
    r = runs_delta
    test = r.make()
    r.complete(test)
    candidate, fingerprint, _bindings = pipeline.pipeline_candidate(test)
    ready = Barrier(2)
    def seal(_):
        ready.wait(timeout=30)
        return pipeline.seal_pipeline_definition(candidate, environment="DEV", fingerprint=fingerprint,
            context=r.context, spark_session=r.spark)
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(seal, range(2)))
    assert results[0] == results[1]
    assert r.spark.read.format("delta").load(r.paths["METADATA_PIPELINE_DEFINITION"]).count() == 1


def test_persisted_profile_renewal_completion_and_owner_fencing(authority_delta, monkeypatch):
    from types import SimpleNamespace
    from datetime import timedelta
    r = authority_delta
    physical = {"workspace_id": "workspace", "item_id": "lakehouse", "kind": "lakehouse", "schema": "demo", "table_name": "orders"}
    descriptor = {"table_id": "orders", "environment": "DEV", "physical": physical}
    monkeypatch.setattr(pipeline, "profiling_context_key", lambda *a, **kw: ("profile-key", descriptor))
    monkeypatch.setattr(pipeline, "profiling_completion_history", lambda *a, **kw: {})
    now = datetime.now(UTC)
    context = {**r.context, "execution_plan": SimpleNamespace(plan_id="profile-owner", permits_persistence=True)}
    claim = pipeline.claim_table_profile("orders", "standard", "read", context=context, spark_session=r.spark, now=now)
    pipeline.maintain_table_profile_claim(claim, context=context, spark_session=r.spark, now=now + timedelta(seconds=20))
    with pytest.raises(pipeline.ProfilingConflict):
        pipeline.maintain_table_profile_claim({**claim, "token": "foreign"}, context=context, spark_session=r.spark, now=now)
    completed = pipeline.maintain_table_profile_claim(claim, context=context, spark_session=r.spark, complete=True, now=now + timedelta(seconds=30))
    native = authority.authority_records(context=r.context, spark_session=r.spark)
    assert native["profiling_claims"][0]["completed_at"] == completed
    # An unrelated Engineering registration preserves the owned completion claim.
    pipeline.resolve_pipeline_registration(context=r.context, spark_session=r.spark)
    assert authority.authority_records(context=r.context, spark_session=r.spark)["profiling_claims"] == native["profiling_claims"]
    pipeline.maintain_table_profile_claim(claim, context=context, spark_session=r.spark, complete=False, now=now + timedelta(seconds=31))
    assert not authority.authority_records(context=r.context, spark_session=r.spark)["profiling_claims"]


def test_rebound_notebook_requires_a_new_finalized_test_and_decision(runs_delta, monkeypatch):
    r = runs_delta
    test, _request, _approved = approved_runtime(r, monkeypatch)
    replacement = {**r.context, "notebook_id": "replacement"}
    pipeline.resolve_pipeline_registration(test.pipeline_id, context=replacement,
        previous_binding=("workspace", "notebook"), spark_session=r.spark)
    with pytest.raises(ValueError, match="rerun Test and approve the new binding"):
        authority.build_live_pipeline_plan(pipeline_id=test.pipeline_id, context=replacement, spark_session=r.spark)
    native = authority.authority_records(context=replacement, spark_session=r.spark)
    assert len(native["approvals"]) == 1 and not native["reservations"]
