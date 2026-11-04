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


def test_02b_notebook_three_day_comparison_uses_same_dataframe(spark_session, monkeypatch):
    """Execute demo cells with real CSVs, transforms and hash filtering, without Fabric I/O."""
    import inspect
    import json
    from pathlib import Path
    from pyspark.sql import functions as F
    from fabricops_kit import orchestrate_read, orchestrate_write

    root = Path(__file__).resolve().parents[2]
    data = root / 'templates/DemoData'
    notebook = json.loads((data / '02B_incremental_append_demo.ipynb').read_text())
    cells = {cell['id']: ''.join(cell['source']) for cell in notebook['cells']}
    bronze = spark_session.read.csv(str(data / 'inventory_day1.csv'), header=True, inferSchema=True)
    targets, submitted, reads = {}, [], []

    def read_csv(path, **kwargs):
        return spark_session.read.csv(str(data / Path(path).name), header=True, inferSchema=True)

    def read_table(*, table_name, store, schema):
        assert (store, schema, table_name) == ('Bronze', 'demo', 'inventory_movements')
        return bronze

    def stage(frame, *, table_name, store, schema, mode):
        nonlocal bronze
        assert (store, schema, table_name, mode) == ('Bronze', 'demo', 'inventory_movements', 'overwrite')
        bronze = frame

    def read(**kwargs):
        inspect.signature(orchestrate_read).bind(**kwargs)
        assert kwargs['read_mode'] == 'full'
        reads.append(bronze)
        return {'dataframe': bronze}

    def write(frame, **kwargs):
        inspect.signature(orchestrate_write).bind(frame, **kwargs)
        assert kwargs['store'] == 'Silver' and kwargs['schema'] == 'demo'
        submitted.append(frame)
        name = kwargs['table_name']
        incoming = shared.add_row_hash(frame)
        if kwargs['write_mode'] == 'append_new_only':
            identity = dict(store_type='lakehouse', store='Silver', schema='demo', table_name=name)
            existing = targets.get(name, incoming.limit(0))
            monkeypatch.setattr(shared, 'read_lakehouse_table', lambda *a, **kw: existing)
            incoming = shared.filter_unpublished_rows(incoming, identity, context={})
        else:
            assert kwargs['write_mode'] == 'append_all'
        targets[name] = targets[name].unionByName(incoming) if name in targets else incoming
        return {'dataframe': frame}

    namespace = dict(F=F, read_lakehouse_csv=read_csv, read_lakehouse_table=read_table,
                     write_lakehouse_table=stage, orchestrate_read=read, orchestrate_write=write,
                     display=lambda frame: None)
    for day, source_count, all_count, new_count in ((1, 8, 8, 8), (2, 12, 20, 12), (3, 12, 32, 12)):
        namespace['DEMO_DAY'] = day
        for cell_id in ('read-csv', 'read-setup', 'read-1', 'transform', 'write-setup', 'write-1', 'write-2'):
            exec(compile(cells[cell_id], f'02B:{cell_id}', 'exec'), namespace)
        assert reads[-1].count() == source_count
        assert submitted[-2] is submitted[-1] is namespace['transformed_df']
        assert targets['inventory_movements_append_all'].count() == all_count
        assert targets['inventory_movements_append_new_only'].count() == new_count
    assert len(reads) == 3 and len(submitted) == 6
