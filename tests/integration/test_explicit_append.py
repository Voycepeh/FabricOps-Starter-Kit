"""Distributed content comparison and execution-scoped publication identities."""
# ruff: noqa: D103
from types import SimpleNamespace
from datetime import UTC, datetime

import pytest
from fabricops_kit.pipeline import shared

pytestmark = pytest.mark.spark


@pytest.mark.parametrize('store_type', ['lakehouse', 'warehouse'])
def test_append_new_only_is_distributed_and_preserves_changed_rows(spark_session, monkeypatch, store_type):
    import fabricops_kit.io as io
    incoming = shared.add_row_hash(spark_session.createDataFrame([(1, 'old'), (1, 'old'), (1, 'new'), (2, 'new')], 'id int, value string'))
    target = incoming.where("value = 'old'").limit(1)
    monkeypatch.setattr(shared, 'read_lakehouse_table', lambda *a, **kw: target)
    monkeypatch.setattr(io, 'read_warehouse_table', lambda *a, **kw: target)
    identity = dict(store_type=store_type, store='Silver', schema='dbo', table_name='target')
    result = shared.filter_unpublished_rows(incoming, identity, context={})
    assert sorted((r.id, r.value) for r in result.collect()) == [(1, 'new'), (2, 'new')]
    assert result.columns == incoming.columns
    assert 'LeftAnti' in result._jdf.queryExecution().optimizedPlan().toString()
    snapshot = shared.validate_target_row_hash(identity, context={}, cache_hashes=True)
    try:
        assert snapshot.is_cached
        assert shared.filter_unpublished_rows(incoming, identity, context={}, target_hashes=snapshot).count() == 2
    finally:
        snapshot.unpersist()
    target = incoming.limit(0)
    assert shared.filter_unpublished_rows(incoming, identity, context={}).count() == 3
    target = incoming
    assert shared.filter_unpublished_rows(incoming, identity, context={}).count() == 0


@pytest.mark.parametrize('strategy', ['overwrite', 'append_all', 'append_new_only', 'scd1', 'scd2'])
def test_publication_identity_distinguishes_new_executions(spark_session, monkeypatch, strategy):
    incoming = spark_session.createDataFrame([(1,), (1,)], 'id int')
    monkeypatch.setattr(shared, 'read_lakehouse_table', lambda *a, **kw: [])
    monkeypatch.setattr(shared, '_find_applied_publication', lambda *a, **kw: None)
    monkeypatch.setattr(shared, 'metadata_table_physical_schema', lambda *a: None)
    ids = []
    for run_id in ('first', 'second', 'first'):
        context = dict(config=object(), scope_workspace_id='dev', execution_plan=SimpleNamespace(plan_id=run_id))
        with shared.PublicationBatch(incoming, identity={'table_id': 'target'}, processing={'load_strategy': strategy},
                                     source_table_ids=[], audit={'_activity_id': 'activity', '_committed_at': datetime.now(UTC)}, context=context) as batch:
            assert batch.input_rows == 2
            ids.append(batch.receipt['batch_id'])
    assert ids[0] == ids[2]
    assert (ids[0] != ids[1]) == (strategy in {'overwrite', 'append_all'})


def test_old_append_is_rejected():
    with pytest.raises(ValueError, match='invalid load_strategy'):
        shared.validated_processing({'load_strategy': 'append'})
