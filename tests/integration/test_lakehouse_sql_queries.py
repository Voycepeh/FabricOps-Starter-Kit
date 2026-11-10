"""Exercise Lakehouse query semantics using real Spark logical plans."""
from importlib import import_module
from unittest.mock import Mock

import pytest

reader = import_module('fabricops_kit.pipeline.pipeline_read')


@pytest.mark.parametrize(('query', 'expected'), [
    ('SELECT id FROM demo.orders WHERE id > 1 ORDER BY id LIMIT 2', [(2,), (3,)]),
    ('SELECT TOP (2) id FROM demo.orders WHERE id > 1 ORDER BY id', [(2,), (3,)]),
    ('SELECT TOP (2) [id] FROM [demo].[orders] WHERE [id] > 1 ORDER BY [id]', [(2,), (3,)]),
    ('SELECT demo.orders.id FROM demo.orders ORDER BY id LIMIT 2', [(1,), (2,)]),
    ('WITH orders AS (SELECT id FROM demo.orders WHERE id > 2) SELECT * FROM orders ORDER BY id', [(3,), (4,)]),
    ('SELECT a.id FROM orders a JOIN orders b ON a.id = b.id WHERE a.id > 2 ORDER BY a.id', [(3,), (4,)]),
    ('SELECT COUNT(*) AS n FROM orders WHERE id > 1', [(3,)]),
    ('SELECT items[0] AS first FROM orders WHERE id = 1', [(10,)]),
])
def test_query_result_survives_private_view_cleanup(monkeypatch, spark_session, query, expected):
    """The result binds the configured DataFrame even with a colliding default table."""
    physical = spark_session.createDataFrame([(i, [i * 10, i * 20]) for i in range(1, 5)], ['id', 'items'])
    unrelated = spark_session.createDataFrame([(999,)], ['id'])
    unrelated.createOrReplaceTempView('orders')
    source = Mock(return_value=physical)
    monkeypatch.setattr(reader, 'read_lakehouse_table', source)
    identity = {'store': 'RemoteBronze', 'schema': 'demo', 'table_name': 'orders'}
    try:
        result = reader._lakehouse_query(query, identity, context={'scope_workspace_id': 'dev'}, spark_session=spark_session)
        # Evaluation happens after the operation has removed its temporary view.
        assert [tuple(row) for row in result.collect()] == expected
        assert not any(table.name.startswith('_fabricops_query_') for table in spark_session.catalog.listTables())
        assert spark_session.table('orders').first().id == 999
        source.assert_called_once_with('orders', store='RemoteBronze', schema='demo', context={'scope_workspace_id': 'dev'})
    finally:
        spark_session.catalog.dropTempView('orders')


def test_query_uses_configured_remote_onelake_location(monkeypatch, spark_session):
    """A remote store reaches the foundational reader with its workspace/item IDs."""
    from fabricops_kit import FabricStore, FrameworkConfig, PathConfig

    physical = spark_session.createDataFrame([(1,), (2,)], ['id'])
    owner = import_module('fabricops_kit.io.read_lakehouse_table')
    load = Mock(return_value=physical)
    monkeypatch.setattr(owner, 'read_delta_path', load)
    context = {
        'config': FrameworkConfig(path_config=PathConfig(paths={'dev': {
            'RemoteBronze': FabricStore('remote-workspace', 'remote-item', 'lakehouse', True, 'demo'),
        }})),
        'scope_workspace_id': 'dev', '_spark_session': spark_session,
        '_fabricops_suppress_io_log': True,
    }
    result = reader._lakehouse_query('SELECT id FROM orders WHERE id = 2',
        {'store': 'RemoteBronze', 'schema': 'demo', 'table_name': 'orders'},
        context=context, spark_session=spark_session)
    assert result.first().id == 2
    assert load.call_args.args[1] == (
        'abfss://remote-workspace@onelake.dfs.fabric.microsoft.com/remote-item/Tables/demo/orders')
