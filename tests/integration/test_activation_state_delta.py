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


def test_rebind_barrier_is_persisted_and_released_in_activation_authority(authority_delta):
    """A notebook transfer blocks competing starts through the durable authority."""
    runtime = authority_delta
    pipeline_id = "8f32a471-6c91-4b7e-9d13-2f0c947eab52"
    lease_id = service.reserve_pipeline_rebind(pipeline_id, context=runtime.context, spark_session=runtime.spark)
    _token, state = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    assert service.environment_activation(state, "DEV")["runs"][lease_id]["mode"] == "rebind"
    with pytest.raises(ValueError, match="another rebind"):
        service.reserve_pipeline_rebind(pipeline_id, context=runtime.context, spark_session=runtime.spark)
    service.release_pipeline_rebind(pipeline_id, lease_id, context=runtime.context, spark_session=runtime.spark)
    _token, state = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    assert service.environment_activation(state, "DEV")["runs"] == {}


def test_finalization_commits_complete_test_results_with_real_delta(authority_delta, monkeypatch, tmp_path):
    """Explicit Test finalization commits run and diagnostic rows exactly once."""
    from fabricops_kit import finalize_pipeline
    from fabricops_kit.pipeline import shared
    runtime = authority_delta
    tables = ('METADATA_PIPELINE_RUN', 'METADATA_GUARDRAIL_RESULTS')
    paths = {table: str(tmp_path / table) for table in tables}
    for table in tables:
        runtime.spark.createDataFrame([], metadata_table_schema_registry()[table]).write.format('delta').save(paths[table])
    monkeypatch.setattr(shared, 'build_runtime_audit_fields', service.build_runtime_audit_fields)
    monkeypatch.setattr(shared, 'resolve_configured_lakehouse_table',
        lambda store, table, schema, **kwargs: ('Metadata', table, 'governance', paths[table]))
    monkeypatch.setattr(shared, 'read_lakehouse_table',
        lambda table, **kwargs: runtime.spark.read.format('delta').load(paths[table]))
    plan = shared.PipelineExecutionPlan('testing', 'DEV', 'notebook', 'test-finalization',
        canonical_candidate_json({'orders': {'store': 'Bronze', 'table_name': 'orders', 'roles': ['source']}}),
        '{}', canonical_candidate_json({'orders': None}), runtime.context, pipeline_id='orders')
    plan.evidence['operations']['source:Bronze/orders'].update(status='succeeded',
        configuration_sha256='tested', configuration={}, stages=[{'stage': 'Read', 'status': 'passed'}])
    row = {'guardrail_result_id': 'stable-result', 'guardrail_rule_id': 'rule', 'guardrail_version': 1,
           'table_id': 'orders', 'contract_id': 'contract', 'contract_version': 1,
           'execution_type': 'testing', 'run_id': plan.plan_id, 'environment_name': 'DEV',
           'status': 'passed', 'can_continue': True, 'severity': 'blocking', 'result_payload_json': '{}'}
    plan.evidence['guardrail_history'] = [row]
    session = shared.PipelineSession(plan, runtime.spark)
    assert all(runtime.spark.read.format('delta').load(path).count() == 0 for path in paths.values())
    result = finalize_pipeline(session)
    assert result['status'] == 'ungoverned_completed' and not plan.permits_persistence
    assert finalize_pipeline(session) == result
    assert runtime.spark.read.format('delta').load(paths['METADATA_PIPELINE_RUN']).count() == 2
    assert runtime.spark.read.format('delta').load(paths['METADATA_GUARDRAIL_RESULTS']).count() == 1
    assert runtime.spark.read.format('delta').load(paths['METADATA_GUARDRAIL_RESULTS']).first().guardrail_result_id == 'stable-result'
