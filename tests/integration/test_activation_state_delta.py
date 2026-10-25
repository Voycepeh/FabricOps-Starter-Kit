"""Exercise the activation authority with persisted Delta transactions.

Only Fabric routing and runtime audit discovery are replaced. Reads, MERGE
expressions, serializable conflict handling, and token read-back use real Delta.
"""
# ruff: noqa: F811
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
    initial = service.activation_state_records(__import__("json").loads(service.empty_activation_state()), token="initial", audit=audit)
    spark_session.createDataFrame(initial, metadata_table_schema_registry()[service.ACTIVATION_STATE_TABLE]).write.format("delta").save(path)
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
    service.environment_activation(proposed, "DEV").update(revision="release-one")
    committed = service.commit_activation_state(proposed, expected_token=token, context=runtime.context, spark_session=runtime.spark)
    assert service.read_activation_state(context=runtime.context, spark_session=runtime.spark) == (committed, proposed)
    stale = deepcopy(state)
    service.environment_activation(stale, "DEV")["revision"] = "must-not-publish"
    with pytest.raises(Exception, match="Stale activation revision"):
        service.commit_activation_state(stale, expected_token=token, context=runtime.context, spark_session=runtime.spark)
    assert service.read_activation_state(context=runtime.context, spark_session=runtime.spark) == (committed, proposed)
    assert runtime.spark.read.format("delta").load(runtime.path).count() == 2


def test_persisted_overlapping_commits_cannot_both_publish(authority_delta):
    """Overlapping reservations/releases serialize or fail, never merge stale JSON."""
    runtime = authority_delta
    token, initial = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    ready = Barrier(2)
    proposals = []
    for version in (3, 4):
        state = deepcopy(initial)
        environment = service.environment_activation(state, "DEV")
        environment.update(revision=f"release-{version}")
        proposals.append(state)
    def publish(state):
        ready.wait(timeout=10)
        try:
            return service.commit_activation_state(state, expected_token=token, context=runtime.context, spark_session=runtime.spark)
        except Exception:
            return None  # Metadata/write conflicts and stale tokens all fail closed.
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(publish, proposals))
    assert sum(result is not None for result in results) == 1
    _current_token, current = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    # A transaction may commit and lose its acknowledgement to another metadata
    # conflict; inspect the durable bytes instead of assuming a client outcome.
    assert canonical_candidate_json(current) in {canonical_candidate_json(state) for state in proposals}
    assert runtime.spark.read.format("delta").load(runtime.path).count() == 2


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
    assert runtime.spark.read.format('delta').load(paths['METADATA_PIPELINE_RUN']).count() == 1
    assert runtime.spark.read.format('delta').load(paths['METADATA_GUARDRAIL_RESULTS']).count() == 1
    assert runtime.spark.read.format('delta').load(paths['METADATA_GUARDRAIL_RESULTS']).first().guardrail_result_id == 'stable-result'


def test_stale_in_transaction_rolls_back_unmatched_children(authority_delta, monkeypatch):
    """Force a race after preflight; child inserts and deletes roll back with CAS."""
    from delta.tables import DeltaTable
    runtime = authority_delta
    reader = service.read_activation_state
    token, initial = reader(context=runtime.context, spark_session=runtime.spark)
    latest = deepcopy(initial)
    service.environment_activation(latest, "PROD")["revision"] = "newer"
    committed = service.commit_activation_state(latest, expected_token=token, context=runtime.context, spark_session=runtime.spark)
    version = DeltaTable.forPath(runtime.spark, runtime.path).history(1).first().version
    stale = deepcopy(initial)
    service.environment_activation(stale, "DEV")["runs"]["unmatched-child"] = {
        "pipeline_id": "pipeline", "tables": [], "mode": "rebind"}
    reads = []
    def race(**kwargs):
        reads.append(True)
        return (token, deepcopy(initial)) if len(reads) == 1 else reader(**kwargs)
    monkeypatch.setattr(service, "read_activation_state", race)
    with pytest.raises(Exception, match="Stale activation revision"):
        service.commit_activation_state(stale, expected_token=token, context=runtime.context, spark_session=runtime.spark)
    assert reader(context=runtime.context, spark_session=runtime.spark) == (committed, latest)
    assert DeltaTable.forPath(runtime.spark, runtime.path).history(1).first().version == version
    assert runtime.spark.read.format("delta").load(runtime.path).filter("record_type = 'reservation'").count() == 0


def test_lost_commit_acknowledgement_confirms_complete_publication(authority_delta, monkeypatch):
    """An exception after real execute is recovered by exact validated read-back."""
    from delta.tables import DeltaMergeBuilder, DeltaTable
    runtime = authority_delta
    original = DeltaMergeBuilder.execute
    executions = []
    def lost_ack(builder):
        original(builder)
        executions.append(True)
        raise OSError("acknowledgement lost after commit")
    monkeypatch.setattr(DeltaMergeBuilder, "execute", lost_ack)
    lease = service.reserve_pipeline_rebind("pipeline", context=runtime.context, spark_session=runtime.spark)
    version = DeltaTable.forPath(runtime.spark, runtime.path).history(1).first().version
    _token, state = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    assert state["environments"]["DEV"]["runs"][lease]["mode"] == "rebind"
    assert executions == [True]
    # Repeating inspection never republishes. A duplicate acquisition fails closed.
    with pytest.raises(ValueError, match="another rebind"):
        service.reserve_pipeline_rebind("pipeline", context=runtime.context, spark_session=runtime.spark)
    assert DeltaTable.forPath(runtime.spark, runtime.path).history(1).first().version == version


def test_profiling_claims_survive_other_authority_changes_and_release(authority_delta):
    """Renewal, expiry identity and release share the same CAS as rebind barriers."""
    from datetime import timedelta
    runtime = authority_delta
    token, state = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    physical = {"workspace_id": "workspace", "item_id": "lakehouse", "kind": "lakehouse", "schema": "demo", "table_name": "orders"}
    claim = {"claim_key": "context:standard", "token": "lease-token", "key": "context", "table_id": "orders",
             "environment": "DEV", "activity": "standard", "trigger": "read", "execution_id": "run",
             "expires_at": (datetime.now(UTC) + timedelta(hours=1)).isoformat(), "physical": physical}
    state["profiling_claims"][claim["claim_key"]] = claim
    service.commit_activation_state(state, expected_token=token, context=runtime.context, spark_session=runtime.spark)
    lease = service.reserve_pipeline_rebind("pipeline", context=runtime.context, spark_session=runtime.spark)
    token, state = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    assert state["profiling_claims"][claim["claim_key"]] == claim
    from fabricops_kit.pipeline import shared
    renewed_at = datetime.now(UTC)
    shared.maintain_table_profile_claim(claim, context=runtime.context, spark_session=runtime.spark, now=renewed_at)
    completed = shared.maintain_table_profile_claim(claim, context=runtime.context, spark_session=runtime.spark,
        complete=True, now=renewed_at + timedelta(seconds=1))
    _, completed_state = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    assert completed_state["profiling_claims"][claim["claim_key"]]["completed_at"] == completed
    with pytest.raises(shared.ProfilingConflict, match="expired or belongs"):
        shared.maintain_table_profile_claim({**claim, "token": "wrong-owner"}, context=runtime.context, spark_session=runtime.spark)
    with pytest.raises(shared.ProfilingConflict, match="expired or belongs"):
        shared.maintain_table_profile_claim(claim, context=runtime.context, spark_session=runtime.spark, now=renewed_at + timedelta(days=1))
    service.release_pipeline_rebind("pipeline", lease, context=runtime.context, spark_session=runtime.spark)
    token, state = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    assert state["profiling_claims"][claim["claim_key"]]["token"] == claim["token"]
    shared.maintain_table_profile_claim(claim, context=runtime.context, spark_session=runtime.spark, complete=False)
    _, state = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    assert state["profiling_claims"] == {} and state["environments"]["DEV"]["runs"] == {}


# Reuse the persisted finalized-Test fixture, not an alternate authority writer.
from tests.integration.test_pipeline_run_delta import runs_delta  # noqa: E402, F401


@pytest.fixture
def approved_authority(runs_delta):
    """Approve a real finalized Test run into the canonical physical authority."""
    import json
    from fabricops_kit import finalize_pipeline
    from fabricops_kit.pipeline import shared
    runtime = runs_delta
    runtime.paths[service.ACTIVATION_STATE_TABLE] = runtime.paths['METADATA_PIPELINE_RUN'] + '-authority'
    initial = service.activation_state_records(json.loads(service.empty_activation_state()), token='initial', audit=runtime.audit)
    runtime.spark.createDataFrame(initial, metadata_table_schema_registry()[service.ACTIVATION_STATE_TABLE]).write.format('delta').save(runtime.paths[service.ACTIVATION_STATE_TABLE])
    def tested():
        plan = runtime.make()
        runtime.complete(plan)
        # The exact frozen definitions and committed diagnostics remain separate authorities.
        if not runtime.spark.read.format('delta').load(runtime.paths['METADATA_DATA_CONTRACT']).count():
            runtime.append('METADATA_DATA_CONTRACT', list(json.loads(plan.contracts_json).values()))
        result = finalize_pipeline(shared.PipelineSession(plan, runtime.spark))
        return {'testing_run_id': plan.plan_id, 'candidate_fingerprint': result['candidate_fingerprint'],
                'pipeline_name': 'Orders', 'pipeline_version': plan.plan_id,
                'agreement_id': 'agreement', 'agreement_version': '1'}
    runtime.tested = tested
    runtime.request = tested()
    runtime.release = service.approve_pipeline_release([runtime.request], expected_token='initial', governance_confirmed=True,
        context=runtime.context, spark_session=runtime.spark)
    return runtime


def test_atomic_approval_participants_native_queries_and_immutable_history(approved_authority):
    """Approval, active link and every participant commit at one Delta version."""
    from delta.tables import DeltaTable
    from pyspark.sql import functions as F
    runtime = approved_authority
    frame = runtime.spark.read.format('delta').load(runtime.paths[service.ACTIVATION_STATE_TABLE])
    participants = frame.filter("record_type = 'participant'")
    assert {row.table_id for row in participants.select('participant.table_id').collect()} == {'table0', 'table1'}
    assert participants.filter(F.col('participant.contract_version') == 1).count() == 2
    assert frame.filter("record_type = 'approval'").count() == 1
    assert frame.select('token').distinct().count() == 1
    history = DeltaTable.forPath(runtime.spark, runtime.paths[service.ACTIVATION_STATE_TABLE]).history().collect()
    assert len(history) == 2  # Initial seed plus one approval transaction, no runtime DDL.
    token, original = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    bad = deepcopy(original)
    approval = next(iter(bad['environments']['DEV']['history'].values()))
    approval['pipeline_name'] = 'changed'
    with pytest.raises(ValueError, match='Immutable approval'):
        service.commit_activation_state(bad, expected_token=token, context=runtime.context, spark_session=runtime.spark)
    bad = deepcopy(original)
    bad['environments']['DEV']['history'].clear()
    with pytest.raises(ValueError, match='Immutable approval'):
        service.commit_activation_state(bad, expected_token=token, context=runtime.context, spark_session=runtime.spark)
    assert service.read_activation_state(context=runtime.context, spark_session=runtime.spark) == (token, original)
    from datetime import timedelta
    runtime.audit['_committed_at'] += timedelta(minutes=1)
    service.approve_pipeline_release([runtime.request], expected_token=token, governance_confirmed=True,
        context=runtime.context, spark_session=runtime.spark)
    _, repeated = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    assert repeated['environments']['DEV']['history'] == original['environments']['DEV']['history']


def test_persisted_test_activation_live_pins_contracts_and_blocks_cutover(approved_authority, monkeypatch):
    """Interrupted Live holds its reservation; unrelated barriers preserve history."""
    import json
    from fabricops_kit.pipeline import shared
    runtime = approved_authority
    test_plan = runtime.make()
    identities = json.loads(test_plan.participants_json)
    physical = test_plan.runtime_context['_pipeline_bindings']
    monkeypatch.setattr(service, 'resolve_pipeline_participants', lambda *args, **kwargs: identities)
    monkeypatch.setattr(shared, 'pipeline_physical_bindings', lambda *args, **kwargs: physical)
    plan = service.build_live_pipeline_plan(pipeline_id=test_plan.pipeline_id, context=runtime.context, spark_session=runtime.spark)
    assert plan.activation_revision == runtime.release['revision']
    assert {item['contract_version'] for item in json.loads(plan.contracts_json).values()} == {1}
    service.verify_live_plan(plan, spark_session=runtime.spark)
    with pytest.raises(ValueError, match='Drain active Live'):
        service.reserve_pipeline_rebind(plan.pipeline_id, context=runtime.context, spark_session=runtime.spark)
    next_request = runtime.tested()
    token, before = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    with pytest.raises(ValueError, match='Drain running execution'):
        service.approve_pipeline_release([next_request], expected_token=token, governance_confirmed=True,
            context=runtime.context, spark_session=runtime.spark)
    other = service.reserve_pipeline_rebind('other-pipeline', context={**runtime.context, 'env': 'PROD'}, spark_session=runtime.spark)
    service.verify_live_plan(plan, spark_session=runtime.spark)
    _, during = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    assert during['environments']['DEV'] == before['environments']['DEV']
    assert other in during['environments']['PROD']['runs']
    service.release_pipeline_lease(plan, spark_session=runtime.spark)
    service.release_pipeline_lease(plan, spark_session=runtime.spark)  # idempotent release, no second publication
    with pytest.raises(ValueError, match='no valid pinned'):
        service.verify_live_plan(plan, spark_session=runtime.spark)
    token, _ = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    service.approve_pipeline_release([next_request], expected_token=token, governance_confirmed=True,
        context=runtime.context, spark_session=runtime.spark)
    _, after = service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
    assert len(after['environments']['DEV']['history']) == 2
    for key, value in before['environments']['DEV']['history'].items():
        assert after['environments']['DEV']['history'][key] == value
    assert after['environments']['PROD']['runs'] == during['environments']['PROD']['runs']


@pytest.mark.parametrize('corruption', ['missing', 'mixed', 'orphan', 'duplicate', 'null', 'ownership', 'extra_authority'])
def test_corrupted_persisted_authority_cannot_authorize_live(approved_authority, corruption):
    """Fail closed on physical incompleteness, even with recomputed publication hashes."""
    runtime = approved_authority
    frame = runtime.spark.read.format('delta').load(runtime.paths[service.ACTIVATION_STATE_TABLE])
    rows = [row.asDict(recursive=True) for row in frame.collect()]
    participant = next(row for row in rows if row['record_type'] == 'participant')
    if corruption == 'missing':
        rows.remove(participant)
    elif corruption == 'mixed':
        participant['token'] = 'stale'
    elif corruption == 'orphan':
        participant['parent_id'] = 'missing-approval'
    elif corruption == 'duplicate':
        rows.append(deepcopy(participant))
    elif corruption == 'null':
        participant['participant']['contract_id'] = None
    elif corruption == 'extra_authority':
        extra = deepcopy(next(row for row in rows if row['record_type'] == 'authority'))
        extra['record_id'] = 'second-authority'
        rows.append(extra)
        next(row for row in rows if row['record_id'] == 'central')['authority']['record_count'] += 1
    elif corruption == 'ownership':
        next(row for row in rows if row['record_type'] == 'ownership')['ownership']['writer'] = 'competing-writer'
    # Recompute hash where appropriate to exercise structural checks too.
    central = next(row for row in rows if row['record_type'] == 'authority')
    if corruption in {'orphan', 'ownership'}:
        central['authority']['content_sha256'] = service.manifest_digest(service._json_instants(service._record_content(rows)))
    # Physical schema may report nullable nested fields; the reader still enforces them.
    nullable_schema = frame.schema
    runtime.spark.createDataFrame(rows, nullable_schema).write.format('delta').mode('overwrite').save(runtime.paths[service.ACTIVATION_STATE_TABLE])
    with pytest.raises((ValueError, KeyError), match='.'):
        service.read_activation_state(context=runtime.context, spark_session=runtime.spark)
