"""Exercise the activation authority with persisted Delta transactions.

Only Fabric routing and runtime audit discovery are replaced. Reads, MERGE
expressions, serializable conflict handling, and token read-back use real Delta.
"""
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import UTC, datetime
from threading import Barrier
from types import SimpleNamespace

import pytest

from fabricops_kit.activated_pipeline import shared as service
from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, metadata_table_schema_registry
from fabricops_kit.pipeline.shared import canonical_candidate_json

pytestmark = pytest.mark.spark


@pytest.fixture
def authority_delta(monkeypatch, spark_session, tmp_path):
    """Persist the actual central schema and route production mutations to it."""
    pytest.importorskip("delta.tables")
    if "DeltaSparkSessionExtension" not in spark_session.conf.get("spark.sql.extensions", ""):
        pytest.skip("requires Delta Spark extensions")
    path = str(tmp_path / service.ACTIVATION_STATE_TABLE)
    context = {"config": {}, "env": "DEV"}
    audit = {name: datetime.now(UTC) if name == "_committed_at" else "test-runtime" for name, *_ in AUDIT_SCHEMA_FIELDS}
    initial = {"authority_id": "central", "token": "initial", "snapshot_json": service.empty_activation_state(), **audit}
    spark_session.createDataFrame([initial], metadata_table_schema_registry()[service.ACTIVATION_STATE_TABLE]).write.format("delta").save(path)
    monkeypatch.setattr(service, "resolve_fabric_context", lambda context=None: ({}, "DEV", context))
    monkeypatch.setattr(service, "build_runtime_audit_fields", lambda **kw: audit)
    monkeypatch.setattr(service, "resolve_configured_lakehouse_table", lambda *a, **kw: ("Metadata", service.ACTIVATION_STATE_TABLE, "governance", path))
    monkeypatch.setattr(service, "read_lakehouse_table", lambda *a, **kw: spark_session.read.format("delta").load(path))
    return SimpleNamespace(context=context, spark=spark_session, path=path)


def test_persisted_stale_commit_cannot_partially_update_the_authority(authority_delta):
    """A stale MERGE must roll back its snapshot as well as its guarded token."""
    runtime = authority_delta
    token, state = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    proposed = deepcopy(state)
    service.environment_activation(proposed, "DEV").update(revision="release-one", tables={"employees": {"contract_version": 4}})
    committed = service.commit_activation_state(proposed, expected_token=token, context=runtime.context, spark_session=runtime.spark)
    assert service.read_activation_state(context=runtime.context, spark_session=runtime.spark) == (committed, proposed)
    stale = deepcopy(state)
    service.environment_activation(stale, "DEV")["revision"] = "must-not-publish"
    with pytest.raises(Exception, match="Stale activation revision"):
        service.commit_activation_state(stale, expected_token=token, context=runtime.context, spark_session=runtime.spark)
    assert service.read_activation_state(context=runtime.context, spark_session=runtime.spark) == (committed, proposed)
    assert runtime.spark.read.format("delta").load(runtime.path).count() == 1


def test_persisted_overlapping_commits_cannot_both_publish(authority_delta):
    """Overlapping reservations/releases serialize or fail, never merge stale JSON."""
    runtime = authority_delta
    token, initial = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    ready = Barrier(2)
    proposals = []
    for version in (3, 4):
        state = deepcopy(initial)
        environment = service.environment_activation(state, "DEV")
        environment.update(revision=f"release-{version}", tables={"employees": {"contract_version": version}},
                           pipelines={f"writer-{version}": {"contract_version": version}})
        proposals.append(state)
    def publish(state):
        ready.wait(timeout=10)
        try:
            return service.commit_activation_state(state, expected_token=token, context=runtime.context, spark_session=runtime.spark)
        except Exception:
            return None  # Metadata/write conflicts and stale tokens all fail closed.
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(publish, proposals))
    assert sum(result is not None for result in results) <= 1
    _current_token, current = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    # A transaction may commit and lose its acknowledgement to another metadata
    # conflict; inspect the durable bytes instead of assuming a client outcome.
    assert canonical_candidate_json(current) in {canonical_candidate_json(state) for state in [initial, *proposals]}
    assert runtime.spark.read.format("delta").load(runtime.path).count() == 1
