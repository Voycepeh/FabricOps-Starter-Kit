"""Physical Warehouse routing at the Fabric connector boundary."""

from tests.helpers import call_with_spark
# ruff: noqa: D103
from dataclasses import asdict
from importlib import import_module
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fabricops_kit import FabricStore, FrameworkConfig, PathConfig
from fabricops_kit import io
from fabricops_kit.config.shared import ResolvedFabricStore, get_store
from fabricops_kit.io import shared
from fabricops_kit.pipeline import shared as pipeline
from tests.integration.test_storage_io import _Frame, _Spark

pytestmark = pytest.mark.integration


@pytest.fixture
def connector(monkeypatch):
    monkeypatch.setattr(shared, '_require_fabric_connector', lambda: SimpleNamespace(
        WorkspaceId='workspace', DatawarehouseId='item', DatabaseName='database'))


def context(alias='Gold', name='wh_ODI_Product', kind='warehouse'):
    return {'config': FrameworkConfig(path_config=PathConfig(paths={'poc': {
        alias: FabricStore('poc', 'workspace-id', 'item-id', kind, name=name),
    }})), 'env': 'poc'}


@pytest.mark.parametrize('alias', ['Gold', 'Product', 'Source', 'Unified', 'Bronze', 'Silver'])
@pytest.mark.parametrize('name', ['wh_ODI_Product', None])
def test_read_write_and_query_use_physical_name_with_legacy_fallback(connector, alias, name):
    runtime = context(alias, name)
    physical = name or alias
    spark, frame = _Spark(), _Frame()
    result = call_with_spark(spark, io.read_warehouse_table, 'dbo', 'orders', store=alias,  context=runtime)
    io.write_warehouse_table(frame, 'dbo', 'orders', store=alias, context=runtime)
    assert result == {'synapsesql': f'{physical}.dbo.orders'}
    assert ('synapsesql', f'{physical}.dbo.orders') in frame.write.calls
    for calls in (spark.read.calls, frame.write.calls):
        assert ('option', 'workspace', 'workspace-id') in calls
        assert ('option', 'item', 'item-id') in calls
    assert ('option', 'database', physical) in spark.read.calls
    spark.read.calls.clear()
    call_with_spark(spark, io.read_warehouse_query, 'SELECT * FROM dbo.orders', store=alias,  context=runtime)
    assert ('option', 'database', physical) in spark.read.calls
    assert get_store(runtime['config'], 'poc', alias).key == alias
    identity = pipeline.resolve_physical_table_identity(runtime['config'], 'poc', store=alias, schema='dbo', table_name='orders')
    assert identity['store'] == alias


def test_legacy_positional_constructors_and_json_round_trip():
    legacy = ResolvedFabricStore('poc', 'workspace-id', 'item-id', 'warehouse', True, 'dbo', 'Product')
    assert legacy.key == 'Product' and legacy.name is None
    configured = FabricStore('poc', 'workspace-id', 'item-id', 'warehouse', True, 'dbo', name=' wh_ODI_Product ')
    decoded = FabricStore(**json.loads(json.dumps(asdict(configured))))
    resolved = get_store(PathConfig(paths={'custom': {'Product': decoded}}), 'custom', 'Product')
    assert resolved.name == 'wh_ODI_Product' and resolved.key == 'Product'
    assert (resolved.workspace_id, resolved.item_id) == ('workspace-id', 'item-id')


@pytest.mark.parametrize('field,value', [('name', ''), ('name', '  '), ('name', 123), ('item_id', ''), ('workspace_id', '')])
def test_invalid_configuration_fails_before_connector_access(field, value):
    values = dict(env='poc', workspace_id='workspace', item_id='item', kind='warehouse')
    values[field] = value
    with pytest.raises(ValueError, match=field):
        FabricStore(**values)


def test_lakehouse_paths_still_use_ids(connector):
    runtime = context(name='Physical Lakehouse', kind='lakehouse')
    spark, frame = _Spark(), _Frame()
    call_with_spark(spark, io.read_lakehouse_table, 'orders', store='Gold',  context=runtime)
    io.write_lakehouse_table(frame, 'orders', store='Gold', context=runtime)
    expected = 'abfss://workspace-id@onelake.dfs.fabric.microsoft.com/item-id/Tables/orders'
    assert ('load', expected) in spark.read.calls
    assert ('save', expected) in frame.write.calls


@pytest.mark.parametrize('strategy', ['scd1', 'scd2'])
@pytest.mark.parametrize('fail', [False, True])
def test_scd_stage_mutation_schema_checks_and_cleanup_share_physical_database(connector, monkeypatch, strategy, fail):
    # Keep SQL generation and connector routing real; fake the Spark input validation.
    monkeypatch.setattr(pipeline, 'validate_processing_input', lambda *_args: None)
    runtime, frame, spark = context(), _Frame(), _Spark()
    frame.columns = ['customer_id', 'name', 'effective_at', '_effective_from', '_effective_to', '_is_current']
    frame.sparkSession = spark
    statements = []

    def execute(sql):
        statements.append(sql)
        if fail and len(statements) == 1:
            raise RuntimeError('mutation failed')
        return SimpleNamespace(collect=Mock())

    spark.read.synapsesql = execute
    definition = {'load_strategy': strategy, 'key_columns': ['customer_id']}
    if strategy == 'scd2':
        definition['effective_column'] = 'effective_at'
    if fail:
        with pytest.raises(RuntimeError, match='mutation failed'):
            shared.execute_warehouse_processing(frame, store='Gold', schema='dbo', table_name='customers', processing=definition, context=runtime)
    else:
        shared.execute_warehouse_processing(frame, store='Gold', schema='dbo', table_name='customers', processing=definition, context=runtime)
    stage = next(c[1] for c in frame.write.calls if c[0] == 'synapsesql')
    assert stage.startswith('wh_ODI_Product.dbo._fabricops_scd_')
    assert ('option', 'database', 'wh_ODI_Product') in spark.read.calls
    assert not any(c == ('option', 'database', 'Gold') for c in spark.read.calls)
    assert 'sys.columns' in statements[0] and '[dbo].[customers]' in statements[0]
    assert len(statements) == (2 if fail else 1)
    if fail:
        assert 'DROP TABLE' in statements[1]


def test_incremental_query_database_and_schema_probe(connector):
    runtime, spark = context(), _Spark()
    reader = import_module('fabricops_kit.pipeline.pipeline_read')
    query = reader._warehouse_incremental_query({'schema': 'dbo', 'table_name': 'orders'}, {
        'type': 'watermark', 'column': 'sequence', 'after': 1, 'through': 10, 'has_data': True, 'first_run': False,
    })
    call_with_spark(spark, io.read_warehouse_query, query, store='Gold',  context=runtime)
    call_with_spark(spark, io.read_warehouse_query, 'SELECT TOP (0) * FROM [dbo].[orders]', store='Gold',  context=runtime)
    assert spark.read.calls.count(('option', 'database', 'wh_ODI_Product')) == 2
    store = get_store(runtime['config'], 'poc', 'Gold')
    assert shared.resolve_warehouse_table_location(store, 'dbo', 'orders', warehouse_name=store.key)[2] == 'wh_ODI_Product.dbo.orders'


@pytest.mark.parametrize('incremental', [False, True])
def test_pipeline_reader_reaches_real_connector_with_physical_database(connector, monkeypatch, incremental):
    runtime, spark = context(), _Spark()
    reader = import_module('fabricops_kit.pipeline.pipeline_read')
    monkeypatch.setattr(reader, 'resolve_fabric_context', lambda: (runtime['config'], 'poc', runtime))
    monkeypatch.setattr(reader, 'resolve_pipeline_data_contract', lambda *_a, **_k: None)
    monkeypatch.setattr(reader, 'capture_source_observation', lambda **_k: {})
    monkeypatch.setattr(reader, 'resolve_incremental_source_scope', lambda **_k: {
        'type': 'watermark', 'column': 'sequence', 'after': 1, 'through': 10, 'has_data': True, 'first_run': False,
    })
    result = call_with_spark(spark, reader.pipeline_read, store='Gold', schema='dbo', table_name='orders',
                                   verbose=False,
                                  **({'read_mode': 'incremental', 'target_table_id': 'target',
                                      'read_parameters': {'watermark_column': 'sequence'}} if incremental else {}))
    assert result['table_id'] == pipeline.resolve_physical_table_identity(
        runtime['config'], 'poc', store='Gold', schema='dbo', table_name='orders')['table_id']
    assert ('option', 'database', 'wh_ODI_Product') in spark.read.calls
    if not incremental:
        assert ('synapsesql', 'wh_ODI_Product.dbo.orders') in spark.read.calls



def test_pipeline_writer_preserves_logical_alias_at_real_connector(connector, monkeypatch):
    from tests.unit.test_pipeline_prep import _patch_write

    runtime, frame = context(), _Frame()
    identity, _ = _patch_write(monkeypatch, store_type='warehouse', context=runtime)
    identity['store'] = 'Gold'
    writer = import_module('fabricops_kit.pipeline.pipeline_write')
    committed = Mock()
    monkeypatch.setattr(pipeline, 'commit_pipeline_write_success', committed)
    result = call_with_spark(_Spark(), writer.pipeline_write, frame, store='Gold', schema='dbo', table_name='students',
                                    context=runtime, verbose=False, source_table_ids=['source'])
    assert ('synapsesql', 'wh_ODI_Product.dbo.students') in frame.write.calls
    assert result['table_id'] == identity['table_id']
    assert committed.call_args.args[0]['target_table_id'] == identity['table_id']


def test_schema_validation_probes_physical_database_and_keeps_logical_metadata(connector, monkeypatch):
    runtime, spark = context(), _Spark()
    checker = import_module('fabricops_kit.pipeline.check_schema')
    identity = pipeline.resolve_physical_table_identity(runtime['config'], 'poc', store='Gold', schema='dbo', table_name='orders')
    identity['store_type'] = 'warehouse'
    monkeypatch.setattr(checker, 'resolve_pipeline_data_contract', lambda *_a, **_k: {'contract_id': 'contract', 'contract_version': 1})
    monkeypatch.setattr(checker, 'resolve_catalogue_table_identity', lambda *_a, **_k: identity)
    monkeypatch.setattr(checker, 'load_table_guardrail_rules', lambda *_a, **_k: [])
    monkeypatch.setattr(checker, 'select_table_guardrail_rule', lambda *_a, **_k: {'guardrail_rule_id': 'rule'})
    monkeypatch.setattr(checker, 'schema_check_core', lambda *_a, **_k: {'status': 'passed', 'can_continue': True})
    monkeypatch.setattr(checker, 'print_guardrail_result', lambda *_a, **_k: None)
    persisted = Mock()
    monkeypatch.setattr(checker, 'write_guardrail_result_row', persisted)
    call_with_spark(spark, checker.check_schema, table_id=identity['table_id'],  context=runtime, verbose=False)
    assert ('option', 'database', 'wh_ODI_Product') in spark.read.calls
    assert ('synapsesql', 'SELECT TOP (0) * FROM [dbo].[orders]') in spark.read.calls
    assert persisted.call_args.kwargs['layer'] == 'Gold'


def test_failed_staging_cleans_up_in_physical_database(connector, monkeypatch):
    monkeypatch.setattr(pipeline, 'validate_processing_input', lambda *_args: None)
    runtime, frame, spark = context(), _Frame(), _Spark()
    frame.columns = ['customer_id', 'name']
    frame.sparkSession = spark
    attempted = Mock(side_effect=RuntimeError('staging failed'))
    frame.write.synapsesql = attempted
    cleanup = Mock(return_value=SimpleNamespace(collect=Mock()))
    spark.read.synapsesql = cleanup
    with pytest.raises(RuntimeError, match='staging failed'):
        shared.execute_warehouse_processing(frame, store='Gold', schema='dbo', table_name='customers',
                                            processing={'load_strategy': 'scd1', 'key_columns': ['customer_id']}, context=runtime)
    assert attempted.call_args.args[0].startswith('wh_ODI_Product.dbo._fabricops_scd_')
    assert ('option', 'database', 'wh_ODI_Product') in spark.read.calls
    assert 'DROP TABLE [dbo].[_fabricops_scd_' in cleanup.call_args.args[0]
