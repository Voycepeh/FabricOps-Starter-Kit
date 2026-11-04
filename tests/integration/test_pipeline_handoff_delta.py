"""Real Delta acceptance-copy, decision concurrency and Engineering Files boundaries.

These tests exercise local Delta/Hadoop, not Fabric workspace permission enforcement.
"""
# ruff: noqa: F811
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Barrier

import pytest

from fabricops_kit.activated_pipeline import shared as service
from tests.integration.test_activation_state_delta import authority_delta
from tests.unit.test_pipeline_handoff import package_candidate, resign, authorized_row

pytestmark = pytest.mark.spark
VERIFY_REGISTRY_APPROVAL = service.verify_registry_approval
VERIFY_PROMOTION_INTEGRITY = service.verify_promotion_integrity


@pytest.fixture
def handoff_delta(authority_delta, monkeypatch):
    """Use actual Governance/Engineering Delta paths with local identity/audit fixtures."""
    runtime = authority_delta
    runtime.ensure(service.APPROVAL_TABLE)
    monkeypatch.setattr(service, "verify_registry_approval", VERIFY_REGISTRY_APPROVAL)
    monkeypatch.setattr(service, "verify_promotion_integrity", VERIFY_PROMOTION_INTEGRITY)
    monkeypatch.setattr(service, "review_submission_policy", lambda *a, **kw: {"current": "reviewed policy"})
    return runtime


def decide(runtime, imported, expected):
    """Append one independently confirmed decision against an exact prior revision."""
    return service.decide_pipeline_submission(imported["submission_id"], status="approved", expected_revision=expected,
        policy={"current": "reviewed policy"}, review_note="Independent Governance review of code and recorded claims",
        governance_confirmed=True, context=runtime.context, spark_session=runtime.spark)


def test_import_decision_revocation_and_registry_authority_are_distinct(handoff_delta):
    """Actual persisted decisions never activate Registry; Registry cannot manufacture authority."""
    r = handoff_delta
    package = package_candidate()
    imported = service.import_pipeline_submission(package, context=r.context, spark_session=r.spark)
    approval = decide(r, imported, 1)
    assert service.read_registry(context=r.context, spark_session=r.spark) == []
    assert len(service.read_approvals(context=r.context, spark_session=r.spark)) == 2
    row = authorized_row(approval)
    assert VERIFY_REGISTRY_APPROVAL(row, context=r.context, spark_session=r.spark)[0]["approval_id"] == approval["approval_id"]
    row["snapshot_sha256"] = "f" * 64
    with pytest.raises(ValueError, match="differs"):
        VERIFY_REGISTRY_APPROVAL(row, context=r.context, spark_session=r.spark)
    service.decide_pipeline_submission(imported["submission_id"], status="revoked", expected_revision=2,
        policy={}, review_note="Revoked by Governance", governance_confirmed=True, context=r.context, spark_session=r.spark)
    with pytest.raises(ValueError, match="revoked"):
        service.authoritative_approval(approval["approval_id"], context=r.context, spark_session=r.spark)
    assert len(service.read_approvals(context=r.context, spark_session=r.spark)) == 3


def test_accepted_package_cannot_be_changed_and_engineering_export_is_write_once(handoff_delta):
    """Canonical accepted content and the complete operational export survive independent reads."""
    r = handoff_delta
    package = package_candidate()
    service.import_pipeline_submission(package, context=r.context, spark_session=r.spark)
    uri = service.persist_engineering_submission(package, context=r.context, spark_session=r.spark)
    assert service.persist_engineering_submission(package, context=r.context, spark_session=r.spark) == uri
    retained = service.validate_submission(service.snapshot_file(uri, spark_session=r.spark))
    assert retained == package
    changed = deepcopy(package)
    changed["manifest"]["created_by"] = "changed"
    resign(changed)
    with pytest.raises(ValueError, match="immutable"):
        service.import_pipeline_submission(changed, context=r.context, spark_session=r.spark)
    with pytest.raises(ValueError, match="immutable"):
        service.persist_engineering_submission(changed, context=r.context, spark_session=r.spark)


def test_simultaneous_governance_decisions_have_one_winner(handoff_delta, monkeypatch):
    """Actual Serializable read tracking rejects two approvals from one stale review."""
    r = handoff_delta
    imported = service.import_pipeline_submission(package_candidate(), context=r.context, spark_session=r.spark)
    barrier, original = Barrier(2), service.replace_metadata_transaction
    def synchronized(*args, **kwargs):
        barrier.wait(timeout=60)
        return original(*args, **kwargs)
    monkeypatch.setattr(service, "replace_metadata_transaction", synchronized)
    def save(_index):
        try:
            decide(r, imported, 1)
            return True
        except Exception:
            return False
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sum(pool.map(save, (1, 2))) == 1
    history = service.read_approvals(context=r.context, spark_session=r.spark)
    assert [(row["revision"], row["status"]) for row in sorted(history, key=lambda row: row["revision"])] == [(1, "imported"), (2, "approved")]
