"""Regression coverage for configured-source SQL routing and validation."""
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from tests.helpers import call_with_spark
from tests.unit.test_pipeline_prep import _identity, _patch_read

reader = import_module('fabricops_kit.pipeline.pipeline_read')


@pytest.fixture
def lakehouse(monkeypatch):
    """Supply a configured source without using the attached Spark catalog."""
    identity = _identity(table_id='lakehouse:source:dbo:orders', store_type='lakehouse')
    _patch_read(monkeypatch, identity)
    frame = Mock(columns=['id'])
    result = SimpleNamespace(columns=['id'])
    spark = SimpleNamespace(sql=Mock(return_value=result), catalog=SimpleNamespace(dropTempView=Mock()))
    physical = Mock(return_value=frame)
    monkeypatch.setattr(reader, 'read_lakehouse_table', physical)
    return SimpleNamespace(identity=identity, frame=frame, spark=spark, physical=physical, result=result)


@pytest.mark.parametrize('query', [
    'SELECT id FROM dbo.orders WHERE id > 3 LIMIT 100',
    'SELECT TOP (100) id FROM dbo.orders WHERE id > 3 ORDER BY id',
    'SELECT TOP 100 [id] FROM [dbo].[orders]',
    'SELECT `id` FROM `dbo`.`orders` LIMIT 100',
    'WITH recent AS (SELECT id FROM dbo.orders WHERE id > 3) SELECT * FROM recent LIMIT 100',
    'SELECT a.id FROM orders a JOIN orders b ON a.id = b.id LIMIT 100',
    "SELECT 'DROP; TOP' AS label, id FROM orders LIMIT 100",
])
def test_lakehouse_query_binds_configured_source_and_cleans_view(lakehouse, query):
    """Physical source routing survives SQL projection, aliases, CTEs and TOP."""
    result = call_with_spark(lakehouse.spark, reader.pipeline_read,
                             table_id=lakehouse.identity['table_id'], query=query, verbose=False)
    assert result['dataframe'] is lakehouse.result
    assert result['is_query'] is True
    assert result['read_metrics']['rows_read'] is None
    lakehouse.physical.assert_called_once()
    assert lakehouse.physical.call_args.kwargs['store'] == 'source'
    assert lakehouse.physical.call_args.kwargs['schema'] == 'dbo'
    view = lakehouse.frame.createOrReplaceTempView.call_args.args[0]
    assert view in lakehouse.spark.sql.call_args.args[0]
    assert 'LIMIT 100' in lakehouse.spark.sql.call_args.args[0]
    lakehouse.spark.catalog.dropTempView.assert_called_once_with(view)


@pytest.mark.parametrize('query', [
    '', 'SELECT [id] FROM orders', 'SELECT * FROM [dbo].[orders]', 'DELETE FROM orders', 'SELECT * INTO other FROM orders',
    'SELECT * FROM orders; DROP TABLE orders',
    'WITH c AS (DELETE FROM orders RETURNING *) SELECT * FROM c',
    'SELECT * FROM other', 'SELECT * FROM otherdb.dbo.orders',
    'SELECT * FROM delta.`/tmp/unconfigured`', 'SELECT * FROM read_files("/tmp")',
    'SELECT * FROM orders JOIN other ON orders.id = other.id',
    'SELECT 1', 'SELECT * FROM orders, UNNEST(ARRAY(1,2))',
    'SELECT TOP 10 PERCENT * FROM orders',
    'SELECT TOP 10 WITH TIES * FROM orders ORDER BY id',
    'SELECT TOP 10 ISNULL(id, 0) FROM orders',
    'SELECT TOP 10 id FROM orders UNION ALL SELECT id FROM orders',
    'SELECT TOP 10 a.id FROM orders a JOIN orders b ON a.id=b.id',
])
def test_unsupported_lakehouse_sql_fails_before_source_io(lakehouse, query):
    """No guessed conversion or unconfigured relation reaches Spark execution."""
    with pytest.raises(ValueError, match='Lakehouse source'):
        call_with_spark(lakehouse.spark, reader.pipeline_read,
                        table_id=lakehouse.identity['table_id'], query=query, verbose=False)
    lakehouse.physical.assert_not_called()
    lakehouse.spark.sql.assert_not_called()


def test_query_observation_never_uses_partial_result(lakehouse, monkeypatch):
    """Mandatory physical observations remain separate from a restricted query."""
    monkeypatch.setattr(reader, 'resolve_pipeline_data_contract', lambda *a, **k: {'contract_id': 'contract'})
    observe = Mock(return_value={'status': 'skipped'})
    capture = Mock(return_value=None)
    monkeypatch.setattr(reader, 'observe_full_source', observe)
    monkeypatch.setattr(reader, 'capture_source_observation', capture)
    call_with_spark(lakehouse.spark, reader.pipeline_read, table_id=lakehouse.identity['table_id'],
                    query='SELECT id FROM orders LIMIT 100', verbose=False)
    assert observe.call_args.kwargs['dataframe'] is None
    assert capture.call_args.kwargs['dataframe'] is None


def test_query_analysis_failure_releases_private_view(lakehouse):
    """A Spark binding failure cannot leave a session view behind."""
    lakehouse.spark.sql.side_effect = RuntimeError('analysis failure')
    with pytest.raises(ValueError, match='Lakehouse source.*analysis failure'):
        call_with_spark(lakehouse.spark, reader.pipeline_read, table_id=lakehouse.identity['table_id'],
                        query='SELECT id FROM orders LIMIT 100', verbose=False)
    lakehouse.spark.catalog.dropTempView.assert_called_once()


def test_warehouse_invalid_sql_identifies_source(monkeypatch):
    """Warehouse validation fails at the routing boundary before connector I/O."""
    identity = _identity()
    _patch_read(monkeypatch, identity)
    physical = Mock()
    monkeypatch.setattr(reader, 'read_warehouse_query', physical)
    with pytest.raises(ValueError, match='Warehouse source'):
        call_with_spark(object(), reader.pipeline_read, table_id=identity['table_id'],
                        query='SELECT * INTO new_table FROM orders', verbose=False)
    physical.assert_not_called()


def test_warehouse_query_observation_reads_physical_source(monkeypatch):
    """Warehouse filtering cannot narrow required Freshness or Source Drift state."""
    identity = _identity()
    _patch_read(monkeypatch, identity)
    monkeypatch.setattr(reader, 'resolve_pipeline_data_contract', lambda *a, **k: {'contract_id': 'contract'})
    monkeypatch.setattr(reader, 'read_warehouse_query', Mock(return_value=SimpleNamespace(columns=['id'])))
    capture = Mock(return_value=None)
    monkeypatch.setattr(reader, 'capture_source_observation', capture)
    call_with_spark(object(), reader.pipeline_read, table_id=identity['table_id'],
                    query='SELECT TOP 100 id FROM dbo.orders', verbose=False)
    assert capture.call_args.kwargs['dataframe'] is None


def test_warehouse_query_failure_keeps_permissions_and_source_context(monkeypatch):
    """Connector failures retain their exception identity and gain source information."""
    identity = _identity()
    _patch_read(monkeypatch, identity)
    denied = PermissionError('access denied')
    query = Mock(side_effect=denied)
    monkeypatch.setattr(reader, 'read_warehouse_query', query)
    with pytest.raises(PermissionError) as result:
        call_with_spark(object(), reader.pipeline_read, table_id=identity['table_id'],
                        query='SELECT TOP 100 id FROM dbo.orders', verbose=False)
    assert result.value is denied
    assert 'Warehouse source' in denied.__notes__[0]
    query.assert_called_once()
