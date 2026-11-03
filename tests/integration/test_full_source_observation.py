"""Full physical observations are independent of selected read scope and accepted by publication."""
# ruff: noqa: D103
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import pytest
from fabricops_kit.pipeline import shared

pytestmark = pytest.mark.spark


@pytest.fixture
def observation_runtime(spark_session, monkeypatch):
    history = []
    source = spark_session.createDataFrame([(1, 'a'), (2, 'b')], 'id int, value string')
    plan = SimpleNamespace(plan_id='run', pipeline_id='pipeline', permits_persistence=True,
                           evidence={'source_observation_policy': {'manual': False, 'days': 7}})
    context = dict(execution_plan=plan, scope_workspace_id='dev', config=object())
    identity = dict(table_id='source', table_name='source', store='Bronze', store_type='lakehouse', schema=None)
    monkeypatch.setattr(shared, 'read_lakehouse_table', lambda name, **kw: list(history) if name == shared._PROCESSING_STATE_TABLE else source)
    monkeypatch.setattr(shared, 'metadata_table_physical_schema', lambda *a: None)
    monkeypatch.setattr(shared, 'build_pipeline_audit_fields', lambda **kw: {'_committed_at': datetime.now(UTC)})
    monkeypatch.setattr(shared, '_merge_source_observation_records', lambda rows, **kw: history.extend(rows))
    yield SimpleNamespace(history=history, source=source, plan=plan, context=context, identity=identity)
    for frame in plan.evidence.pop('source_observation_caches', []):
        frame.unpersist()


def test_full_observation_reuses_physical_frame_and_ignores_unaccepted_attempts(observation_runtime, monkeypatch):
    run = observation_runtime
    result = shared.observe_full_source(run.identity, dataframe=run.source, context=run.context)
    assert result['row_count'] == 2 and result['status'] == 'first_observation'
    # An observed capture does not consume the interval after failed publication.
    assert shared.observe_full_source(run.identity, dataframe=run.source, context=run.context)['status'] == 'first_observation'
    row = run.plan.evidence['full_source_observations']['source'][0]
    run.history.append({**row, 'record_type': 'full_source_baseline', 'status': 'committed', 'accepted_at': datetime.now(UTC), 'target_table_id': 'target'})
    assert shared.observe_full_source(run.identity, dataframe=run.source, context=run.context)['status'] == 'skipped'
    run.plan.evidence['source_observation_policy']['manual'] = True
    assert shared.observe_full_source(run.identity, dataframe=run.source, context=run.context)['status'] == 'unchanged'
    assert shared.observe_full_source(run.identity, dataframe=run.source.where('id = 1'), context=run.context)['status'] == 'changed'
    # Capture remains non-destructive: absence changes the fingerprint, never target rows.
    assert all(row['record_type'] in {'source_observation', 'full_source_baseline'} for row in run.history)


def test_scheduled_and_disabled_observations(observation_runtime):
    run = observation_runtime
    shared.observe_full_source(run.identity, dataframe=run.source, context=run.context)
    row = run.plan.evidence['full_source_observations']['source'][0]
    run.history.append({**row, 'record_type': 'full_source_baseline', 'status': 'committed',
                        'observed_at': datetime.now(UTC) - timedelta(days=8), 'accepted_at': datetime.now(UTC), 'target_table_id': 'target'})
    assert shared.observe_full_source(run.identity, dataframe=run.source, context=run.context)['status'] == 'unchanged'
    run.plan.evidence['source_observation_policy']['days'] = None
    assert shared.observe_full_source(run.identity, dataframe=run.source, context=run.context)['status'] == 'skipped'


def test_warehouse_observation_reads_entire_table(observation_runtime, monkeypatch):
    import fabricops_kit.io as io
    run = observation_runtime
    calls = []
    monkeypatch.setattr(io, 'read_warehouse_table', lambda schema, name, **kw: calls.append((schema, name)) or run.source)
    result = shared.observe_full_source({**run.identity, 'store_type': 'warehouse', 'schema': 'dbo'}, context=run.context)
    assert calls == [('dbo', 'source')]
    assert result['row_count'] == 2


def test_full_baseline_is_bound_to_publication_snapshot(observation_runtime):
    run = observation_runtime
    shared.observe_full_source(run.identity, dataframe=run.source, context=run.context)
    shared._CURRENT_TABLE_IDENTITIES['source'] = {'table_name': 'source'}
    snapshot = shared.snapshot_pipeline_write_observations(workspace_id='dev', activity_id='run',
        target_table_id='target', source_table_ids=['source'], context=run.context)
    success = dict(target_table_id='target', target_table_name='target', source_table_ids=['source'], context=run.context,
                   publication=dict(batch_id='batch', activity_id='activity', committed_at=datetime.now(UTC).isoformat(),
                                    input_rows=2, run_id='run', strategy='overwrite'), observation_snapshot=snapshot)
    rows = shared._pipeline_write_state_records(success, audit={}, active_workspace_id='dev', status='staged')
    assert {row['record_type'] for row in rows} == {'publication_receipt', 'full_source_baseline'}
    assert {row['status'] for row in rows} == {'staged'}
    assert len({row['publication_id'] for row in rows}) == 1


@pytest.mark.parametrize('store_type', ['lakehouse', 'warehouse'])
@pytest.mark.parametrize('has_data', [True, False])
def test_full_observation_during_incremental_read_ignores_predicate(observation_runtime, monkeypatch, store_type, has_data):
    from importlib import import_module
    import fabricops_kit.io as io
    read = import_module('fabricops_kit.pipeline.pipeline_read')
    run = observation_runtime
    identity = {**run.identity, 'store_type': store_type, 'schema': 'dbo'}
    monkeypatch.setattr(read, 'resolve_physical_table_identity', lambda *a, **kw: identity)
    monkeypatch.setattr(read, 'resolve_pipeline_data_contract', lambda *a, **kw: None)
    monkeypatch.setattr(read, 'capture_source_observation', lambda **kw: [])
    monkeypatch.setattr(read, 'resolve_incremental_source_scope', lambda **kw:
                        dict(type='incremental', column='id', after=1, through=2, has_data=has_data, first_run=False))
    monkeypatch.setattr(read, 'read_lakehouse_table', lambda *a, **kw: run.source)
    queries = []
    monkeypatch.setattr(read, 'read_warehouse_query', lambda query, **kw: queries.append(query) or (run.source.where('id > 1') if has_data else run.source.limit(0)))
    monkeypatch.setattr(io, 'read_warehouse_table', lambda *a, **kw: run.source)
    result = read.pipeline_read(store='Bronze', schema='dbo', table_name='source', read_mode='incremental',
        read_parameters={'watermark_column': 'id'}, target_table_id='target', context=run.context, verbose=False)
    assert result['dataframe'].count() == (1 if has_data else 0)
    assert result['full_source_observation']['row_count'] == 2
    if store_type == 'warehouse':
        assert 'WHERE' in queries[0]



def test_dry_run_and_empty_source_observation(observation_runtime):
    run = observation_runtime
    run.plan.permits_persistence = False
    result = shared.observe_full_source(run.identity, dataframe=run.source.limit(0), context=run.context)
    assert result['row_count'] == 0 and result['status'] == 'first_observation'
    assert run.history == []
