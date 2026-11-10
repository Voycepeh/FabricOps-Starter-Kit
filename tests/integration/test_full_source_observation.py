"""Read scope never narrows the complete physical frame offered to Source Drift."""
# ruff: noqa: D103
from importlib import import_module
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.spark


@pytest.mark.parametrize('store_type', ['lakehouse', 'warehouse'])
@pytest.mark.parametrize('scope', ['full', 'query', 'incremental', 'empty_incremental'])
def test_source_drift_receives_complete_source_independent_of_read_scope(spark_session, monkeypatch, store_type, scope):
    read = import_module('fabricops_kit.pipeline.pipeline_read')
    source = spark_session.createDataFrame([(1, 'a'), (2, 'b')], 'id int, value string')
    identity = dict(table_id='source', table_name='source', store='Bronze', store_type=store_type, schema='dbo')
    context = {'config': object(), 'scope_workspace_id': 'dev',
        'execution_plan': SimpleNamespace(plan_id='run', evidence={}), '_spark_session': spark_session}
    monkeypatch.setattr(read, 'resolve_physical_table_identity', lambda *a, **kw: identity)
    monkeypatch.setattr(read, 'resolve_pipeline_data_contract', lambda *a, **kw: None)
    monkeypatch.setattr(read, 'capture_source_observation', lambda **kw: [])
    monkeypatch.setattr(read, 'resolve_incremental_source_scope', lambda **kw:
        dict(type='incremental', column='id', after=1, through=2, has_data=scope != 'empty_incremental', first_run=False))
    calls = []
    monkeypatch.setattr(read, 'read_lakehouse_table', lambda *a, **kw: calls.append(('table', kw)) or source)
    monkeypatch.setattr(read, 'read_warehouse_table', lambda *a, **kw: calls.append(('table', kw)) or source)
    monkeypatch.setattr(read, 'read_warehouse_query', lambda query, **kw:
        calls.append(('query', query)) or (source.limit(0) if scope == 'empty_incremental' else source.where('id > 1')))
    observed = []
    def observe(identity, *, dataframe=None, context):
        observed.append(dataframe)
        if dataframe is not None:
            assert dataframe.count() == 2
        return {'status': 'baseline_pending', 'row_count': 2}
    monkeypatch.setattr(read, 'observe_full_source', observe)
    result = read.pipeline_read(store='Bronze', schema='dbo', table_name='source',
        read_mode='incremental' if 'incremental' in scope else 'full',
        read_parameters={'watermark_column': 'id'} if 'incremental' in scope else None,
        query='SELECT * FROM dbo.source WHERE id > 1' if scope == 'query' else None,
        target_table_id='target' if 'incremental' in scope else None, context=context,
        verbose=False)
    assert result['dataframe'].count() == (2 if scope == 'full' else 0 if scope == 'empty_incremental' else 1)
    assert len(observed) == 1
    # Warehouse filtered/empty reads require a separate complete physical scan;
    # full reads and Lakehouse materializations may reuse the complete frame.
    assert (observed[0] is None) == (scope == 'query' or (store_type == 'warehouse' and scope != 'full'))
    assert result['full_source_observation']['row_count'] == 2
