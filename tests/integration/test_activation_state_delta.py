"""Prove the consolidated native Registry authority using persisted Delta commits."""
# ruff: noqa: D103
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import datetime
from threading import Barrier
from types import SimpleNamespace

import pytest

from fabricops_kit.activated_pipeline import shared as service
from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, metadata_table_schema_registry
from fabricops_kit.pipeline import shared as pipeline

pytestmark = pytest.mark.spark


@pytest.fixture
def authority_delta(monkeypatch, spark_session, tmp_path):
    """Replace only Fabric routing; production codecs, CAS and reads use real Delta."""
    pytest.importorskip("delta.tables")
    if "DeltaSparkSessionExtension" not in spark_session.conf.get("spark.sql.extensions", ""):
        pytest.skip("requires Delta Spark extensions")
    schemas = metadata_table_schema_registry()
    context = {"config": {}, "scope_workspace_id": "DEV", "workspace_id": "DEV", "notebook_id": "notebook"}
    audit = {name: datetime.now() if name == "_committed_at" else "test-runtime" for name, *_ in AUDIT_SCHEMA_FIELDS}
    audit.update(_workspace_id="DEV", _notebook_id="notebook")
    paths = {}
    def ensure(table):
        if table not in paths:
            path = str(tmp_path / table)
            initial = [{**service.empty_pipeline_authority(), **audit}] if table == service.PIPELINE_AUTHORITY_TABLE else []
            spark_session.createDataFrame(initial, schemas[table]).write.format("delta").save(path)
            paths[table] = path
        return paths[table]
    path = ensure(service.PIPELINE_AUTHORITY_TABLE)
    for module in (service, pipeline):
        monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: (context["config"], context["scope_workspace_id"], context))
        monkeypatch.setattr(module, "build_runtime_audit_fields", lambda **kw: dict(audit))
        monkeypatch.setattr(module, "resolve_configured_lakehouse_table", lambda store, table, schema, **kw: (store, table, schema, ensure(table)))
        monkeypatch.setattr(module, "read_lakehouse_table", lambda table, **kw: spark_session.read.format("delta").load(ensure(table)))
    return SimpleNamespace(context=context, spark=spark_session, path=path, ensure=ensure, paths=paths, audit=audit)


def test_persisted_stale_commit_cannot_partially_update_the_authority(authority_delta):
    r = authority_delta
    token, state = service.read_pipeline_authority(context=r.context, spark_session=r.spark)
    proposed = deepcopy(state)
    service.workspace_activation(proposed, "DEV")["revision"] = "release-one"
    committed = service.commit_pipeline_authority(proposed, expected_token=token, context=r.context, spark_session=r.spark)
    assert service.read_pipeline_authority(context=r.context, spark_session=r.spark) == (committed, proposed)
    stale = deepcopy(state)
    service.workspace_activation(stale, "OTHER")["revision"] = "must-not-publish"
    with pytest.raises(Exception, match="Stale Pipeline Registry authority"):
        service.commit_pipeline_authority(stale, expected_token=token, context=r.context, spark_session=r.spark)
    assert service.read_pipeline_authority(context=r.context, spark_session=r.spark) == (committed, proposed)
    assert r.spark.read.format("delta").load(r.path).count() == 1


def test_persisted_overlapping_commits_cannot_both_publish(authority_delta):
    r = authority_delta
    token, initial = service.read_pipeline_authority(context=r.context, spark_session=r.spark)
    ready = Barrier(2)
    proposals = []
    for workspace_id in ("DEV", "OTHER"):
        state = deepcopy(initial)
        service.workspace_activation(state, workspace_id)["revision"] = workspace_id
        proposals.append(state)
    def publish(state):
        ready.wait(timeout=30)
        try:
            return service.commit_pipeline_authority(state, expected_token=token, context=r.context, spark_session=r.spark)
        except Exception:
            return None
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(publish, proposals))
    assert sum(result is not None for result in results) == 1
    _token, current = service.read_pipeline_authority(context=r.context, spark_session=r.spark)
    assert current in proposals
    assert r.spark.read.format("delta").load(r.path).count() == 1


def test_rebind_barrier_is_persisted_and_released_in_registry(authority_delta):
    r = authority_delta
    identity = "8f32a471-6c91-4b7e-9d13-2f0c947eab52"
    lease = service.reserve_pipeline_rebind(identity, context=r.context, spark_session=r.spark)
    _token, state = service.read_pipeline_authority(context=r.context, spark_session=r.spark)
    assert service.workspace_activation(state, "DEV")["runs"][lease]["mode"] == "rebind"
    with pytest.raises(ValueError, match="another rebind"):
        service.reserve_pipeline_rebind(identity, context=r.context, spark_session=r.spark)
    service.release_pipeline_rebind(identity, lease, context=r.context, spark_session=r.spark)
    _token, state = service.read_pipeline_authority(context=r.context, spark_session=r.spark)
    assert service.workspace_activation(state, "DEV")["runs"] == {}


def test_missing_singleton_is_never_inserted_by_mutation(authority_delta):
    from delta.tables import DeltaTable
    r = authority_delta
    token, state = service.read_pipeline_authority(context=r.context, spark_session=r.spark)
    DeltaTable.forPath(r.spark, r.path).delete()
    with pytest.raises(ValueError, match="missing or duplicated"):
        service.commit_pipeline_authority(state, expected_token=token, context=r.context, spark_session=r.spark)
    assert r.spark.read.format("delta").load(r.path).count() == 0


def test_failure_in_any_native_collection_rolls_back_token_and_all_fields(authority_delta):
    """An invalid typed value cannot leave a new revision, token or reservation behind."""
    r = authority_delta
    token, state = service.read_pipeline_authority(context=r.context, spark_session=r.spark)
    proposed = deepcopy(state)
    service.workspace_activation(proposed, "DEV")["runs"]["bad"] = {"pipeline_id": None, "tables": [], "mode": "live"}
    with pytest.raises(Exception):
        service.commit_pipeline_authority(proposed, expected_token=token, context=r.context, spark_session=r.spark)
    assert service.read_pipeline_authority(context=r.context, spark_session=r.spark) == (token, state)
