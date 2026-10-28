"""Joint Run, approval, admission and rebind publication proofs."""
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
    finalize_pipeline(pipeline.PipelineSession(plan, r.spark))
    request = {"testing_run_id": plan.plan_id,
        "pipeline_name": "Orders", "pipeline_version": "1", "agreement_id": "agreement", "agreement_version": "1"}
    token, _state = authority.read_pipeline_authority(context=r.context, spark_session=r.spark)
    report = authority.review_pipeline_release([request], context=r.context, spark_session=r.spark)[3]
    approval = authority.approve_pipeline_release([request], expected_token=token, expected_review_digest=report["review_digest"], governance_confirmed=True,
        context=r.context, spark_session=r.spark)
    monkeypatch.setattr(authority, "resolve_pipeline_participants", lambda *a, **kw: json.loads(plan.participants_json))
    monkeypatch.setattr(pipeline, "pipeline_physical_bindings", lambda *a, **kw: plan.runtime_context["_pipeline_bindings"])
    return plan, request, approval


def test_finalized_test_approval_and_live_reference_the_retained_test_run(runs_delta, monkeypatch):
    r = runs_delta
    test, request, approved = approved_runtime(r, monkeypatch)
    live = authority.build_live_pipeline_plan(pipeline_id=test.pipeline_id, context=r.context, spark_session=r.spark)
    assert live.approval_id == approved["pipelines"][test.pipeline_id]["approval_id"]
    rows = r.rows()
    assert len(rows) == 2 and all("definition_id" not in row for row in rows)
    assert all("candidate_json" not in row for row in rows)
    r.complete(live)
    pipeline.finalize_pipeline_run(live, spark_session=r.spark)
    _token, state = authority.read_pipeline_authority(context=r.context, spark_session=r.spark)
    current = authority.workspace_activation(state, "DEV")
    assert not current["runs"] and len(current["history"]) == 1
    # Reapproval is independent decision history over the same retained Test Run.
    request["pipeline_version"] = "2"
    report = authority.review_pipeline_release([request], context=r.context, spark_session=r.spark)[3]
    authority.approve_pipeline_release([request], expected_token=_token, expected_review_digest=report["review_digest"], governance_confirmed=True,
        context=r.context, spark_session=r.spark)
    native = authority.authority_records(context=r.context, spark_session=r.spark)
    assert len(native["approvals"]) == 2 and len({item["testing_run_id"] for item in native["approvals"]}) == 1
    token, state = authority.read_pipeline_authority(context=r.context, spark_session=r.spark)
    current = authority.workspace_activation(state, "DEV")
    current["history"].pop(next(key for key in current["history"] if key != current["pipelines"][test.pipeline_id]["approval_id"]))
    with pytest.raises(ValueError, match="immutable and retained"):
        authority.commit_pipeline_authority(state, expected_token=token, context=r.context, spark_session=r.spark)


@pytest.mark.parametrize("defect", ["missing", "duplicate", "altered", "contract", "agreement", "testing"])
def test_missing_duplicate_or_altered_references_block_live(runs_delta, monkeypatch, defect):
    from delta.tables import DeltaTable
    r = runs_delta
    test, _request, _approved = approved_runtime(r, monkeypatch)
    retained_run = DeltaTable.forPath(r.spark, r.paths["METADATA_PIPELINE_RUN"])
    if defect == "missing":
        retained_run.delete()
    elif defect == "duplicate":
        r.spark.read.format("delta").load(r.paths["METADATA_PIPELINE_RUN"]).write.format("delta").mode("append").save(r.paths["METADATA_PIPELINE_RUN"])
    elif defect == "altered":
        retained_run.update(set={"warnings_json": "'[{\"changed\":true}]'"})
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




@pytest.mark.parametrize("competitor", ["approval", "rebind"])
def test_live_admission_races_share_the_registry_cas(runs_delta, monkeypatch, competitor):
    r = runs_delta
    test, request, _approved = approved_runtime(r, monkeypatch)
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
                expected_review_digest=authority.review_pipeline_release([{**request, "pipeline_version": "2"}], context=r.context, spark_session=r.spark)[3]["review_digest"],
                governance_confirmed=True, context=r.context, spark_session=r.spark)
        if competitor == "rebind":
            return pipeline.resolve_pipeline_registration(test.pipeline_id,
                context={**r.context, "notebook_id": "replacement"}, previous_binding=(r.context["workspace_id"], r.context["notebook_id"]), spark_session=r.spark)
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
    current = authority.workspace_activation(state, "DEV")
    assert len(current["history"]) in {1, 2}
    if outcomes[0] is not None:
        assert len(current["runs"]) == 1
        authority.release_pipeline_lease(outcomes[0], spark_session=r.spark)
    else:
        assert not current["runs"]


def test_exact_content_readback_after_lost_authority_acknowledgement(authority_delta, monkeypatch):
    from delta.tables import DeltaTable
    r = authority_delta
    token, state = authority.read_pipeline_authority(context=r.context, spark_session=r.spark)
    authority.workspace_activation(state, "DEV")["revision"] = "committed"
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

def test_rebound_notebook_requires_a_new_finalized_test_and_decision(runs_delta, monkeypatch):
    r = runs_delta
    test, _request, _approved = approved_runtime(r, monkeypatch)
    replacement = {**r.context, "notebook_id": "replacement"}
    pipeline.resolve_pipeline_registration(test.pipeline_id, context=replacement,
        previous_binding=(r.context["workspace_id"], r.context["notebook_id"]), spark_session=r.spark)
    with pytest.raises(ValueError, match="rerun Test and approve the new binding"):
        authority.build_live_pipeline_plan(pipeline_id=test.pipeline_id, context=replacement, spark_session=r.spark)
    native = authority.authority_records(context=replacement, spark_session=r.spark)
    assert len(native["approvals"]) == 1 and not native["reservations"]
