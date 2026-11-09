"""Demo reset and retail transforms on real Spark/Delta, with only Fabric transport isolated."""
# ruff: noqa: D103
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from importlib import import_module
from pathlib import Path
import shutil
from types import SimpleNamespace

import nbformat
import pytest
from pyspark.sql import functions as F

from fabricops_kit import orchestrate_demo_reset, read_lakehouse_csv, read_lakehouse_table, write_lakehouse_table
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
from tests.unit.test_orchestrate_demo_reset import API, _environment

ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.spark


@pytest.fixture
def demo_csv(spark_session, monkeypatch):
    """Route the public CSV reader to committed fixtures without requiring Delta."""
    monkeypatch.setattr(import_module('fabricops_kit.io.read_lakehouse_csv'), 'resolve_configured_file_path',
        lambda store, path, **_: (store, path, str(ROOT / 'templates/DemoData' / Path(path).name)))
    return spark_session


@pytest.fixture
def demo_delta(demo_csv, monkeypatch, tmp_path):
    spark_session = demo_csv
    delta = pytest.importorskip('delta.tables')
    if 'DeltaSparkSessionExtension' not in spark_session.conf.get('spark.sql.extensions', ''):
        pytest.skip('requires Delta Spark extensions, as do the existing publication regressions')
    spark_session.conf.set('spark.databricks.delta.snapshotPartitions', '2')
    # Route existing public IO to local files, preserving the actual Spark/Delta implementations.
    for module in ('read_lakehouse_table', 'write_lakehouse_table'):
        monkeypatch.setattr(import_module('fabricops_kit.io.' + module), 'resolve_configured_lakehouse_table',
            lambda store, table, schema, **_: (store, table, schema, str(tmp_path / store / table)))
    return SimpleNamespace(spark=spark_session, root=tmp_path, DeltaTable=delta.DeltaTable)


def test_public_reset_clears_metadata_restores_sources_and_retries_partial_failure(demo_delta, monkeypatch, capsys):
    run = demo_delta
    env = _environment(monkeypatch)
    registry = metadata_table_schema_registry()
    def read(table_name, *, store, schema):
        return read_lakehouse_table(table_name, store=store, schema=schema)
    def write(frame, *, table_name, store, schema, mode):
        write_lakehouse_table(frame, table_name, store=store, schema=schema, mode=mode)
    # Real canonical Delta schemas and rows, including frozen Contracts and retained activations.
    for table, schema in registry.items():
        record = {f.name: None if f.nullable else datetime(2026, 1, 1)
                  if f.dataType.simpleString() == 'timestamp' else datetime(2026, 1, 1).date()
                  if f.dataType.simpleString() == 'date' else False
                  if f.dataType.simpleString() == 'boolean' else 1
                  if f.dataType.simpleString() in {'int', 'bigint'} else 'demo' for f in schema}
        for key in record:
            if key in {'table_id', 'source_table_id', 'target_table_id'}: record[key] = 'orders'
            if key.endswith('workspace_id'): record[key] = 'dev'
            if key in {'operations', 'profiling', 'operations_json'}: record[key] = '[]'
            if key in {'package_json', 'contract_payload_json', 'destination_json'}: record[key] = '{}'
        if table == 'METADATA_DATA_CONTRACT': record['status'] = 'frozen'
        if table in {'METADATA_DATA_CONTRACT_ACTIVATION', 'METADATA_PIPELINE_REGISTRY'}: record['status'] = 'active'
        write(run.spark.createDataFrame([record], schema), table_name=table, store='Metadata', schema='metadata', mode='overwrite')
    sentinel = run.spark.createDataFrame([(77,)], 'id int')
    write(sentinel, table_name='unrelated', store='Silver', schema='other', mode='overwrite')
    for store, table in API._DEMO_OUTPUTS:
        write(sentinel, table_name=table, store=store, schema='demo', mode='overwrite')
    # Only remote Fabric catalog/warehouse removal is replaced by equivalent local filesystem IO.
    def remove(self, *, preview=False):
        if preview: return
        for store, table in API._DEMO_OUTPUTS:
            shutil.rmtree(run.root / store / table, ignore_errors=True)
    def verify(self=None):
        assert all(not (run.root / store / table).exists() for store, table in API._DEMO_OUTPUTS)
    env.setup.paths['Metadata'].root = str(run.root / 'Metadata')
    env.state._metadata = env.setup.paths['Metadata']
    env.state.spark = run.spark
    env.state._demo_table_ids = {table for store, table in [*API._DEMO_SOURCES, *API._DEMO_OUTPUTS]}
    env.state._demo_workspaces = {'dev', 'governance'}
    monkeypatch.setattr(API, 'get_spark_session', lambda: run.spark)
    for name, function in {'read_lakehouse_table': read, 'read_warehouse_table': read,
            'write_lakehouse_table': write, 'write_warehouse_table': write, 'read_lakehouse_csv': read_lakehouse_csv}.items():
        monkeypatch.setattr(API, name, function)
    monkeypatch.setattr(API._DemoReset, '_demo_remove_outputs', remove)
    monkeypatch.setattr(API._DemoReset, '_demo_verify_outputs', verify)
    monkeypatch.setattr(API, 'resolve_configured_lakehouse_table',
        lambda store, table, schema: (store, table, schema, str(run.root / store / table)))
    artifacts = run.root / 'Metadata/Files/fabricops/engineering'
    (artifacts / 'submissions').mkdir(parents=True)
    (artifacts / 'submissions/demo.json').write_text('{"manifest":{"operations":[{"table_id":"orders"}]}}')
    orchestrate_demo_reset()  # False previews populated state without changing it.
    assert all(count == 1 for count in env.state._demo_metadata_counts().values())
    # Fail after metadata deletion to prove the same cell can recover without a new configuration.
    def fail(self, **kw):
        if not kw.get('preview'): raise RuntimeError('simulated Fabric transport failure')
    monkeypatch.setattr(API._DemoReset, '_demo_remove_outputs', fail)
    with pytest.raises(RuntimeError, match='simulated Fabric transport'):
        orchestrate_demo_reset(reset=True)
    assert 'RESET COMPLETE' not in capsys.readouterr().out
    monkeypatch.setattr(API._DemoReset, '_demo_remove_outputs', remove)
    for _ in range(2):
        orchestrate_demo_reset(reset=True)
        assert env.state._demo_metadata_counts() == dict.fromkeys(registry, 0)
        assert env.state._demo_metadata_files() == dict.fromkeys(('submissions', 'dry_runs', 'pipeline_snapshots'), 0)
        for (store, table), (file, count) in API._DEMO_SOURCES.items():
            expected = read_lakehouse_csv(file, store='Bronze', header=True, inferSchema=True)
            actual = read(table, store=store, schema='demo')
            assert actual.count() == count
            env.state._demo_assert_source(actual, expected)
        verify()
        assert read('unrelated', store='Silver', schema='other').collect() == sentinel.collect()
        assert all(read(table, store='Metadata', schema='metadata').schema.simpleString() == schema.simpleString() for table, schema in registry.items())
    assert capsys.readouterr().out.count('RESET COMPLETE') == 2
    # Equal counts cannot hide a missing row and a duplicate.
    expected = run.spark.createDataFrame([(1,), (2,)], 'id int')
    wrong = run.spark.createDataFrame([(1,), (1,)], 'id int')
    with pytest.raises(RuntimeError, match='content differs'):
        env.state._demo_assert_source(wrong, expected)


def test_02a_real_transform_and_public_overwrite_preserve_source_content(demo_delta):
    ns = {'F': F, 'sources': {}}
    for key, table in [('orders', 'orders'), ('products', 'products'), ('history', 'order_history')]:
        ns['sources'][key] = {'dataframe': read_lakehouse_csv(f'demo/{table}.csv', inferSchema=True)}
    before = {key: frame['dataframe'].collect() for key, frame in ns['sources'].items()}
    notebook = nbformat.read(ROOT / 'templates/DemoData/02A_full_refresh_demo.ipynb', as_version=4)
    exec(next(c.source for c in notebook.cells if c.id == 'transform'), ns)
    detailed = ns['transformed_df'].collect()
    customers = ns['customer_summary_df'].collect()
    assert len(detailed) == 120 and len(customers) == 30
    assert len({row.order_id for row in detailed}) == 120
    total = Decimal('0')
    for row in detailed:
        expected = (Decimal(str(row.quantity)) * Decimal(str(row.unit_price))
                    * (1 - Decimal(str(row.discount)))).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        assert Decimal(str(row.order_net_amount)) == expected
        assert row.product_name and row.historical_order_count == 6
        total += expected
    assert total == Decimal('28539.15')
    assert sum(row.order_count for row in customers) == 120
    assert sum(Decimal(str(row.total_order_net_amount)).quantize(Decimal('.01')) for row in customers) == total
    for name, frame in [('curated_orders', ns['transformed_df']), ('customer_summary', ns['customer_summary_df'])]:
        write_lakehouse_table(frame.unionByName(frame), name, store='Silver', schema='demo', mode='overwrite')
        write_lakehouse_table(frame, name, store='Silver', schema='demo', mode='overwrite')
        check = read_lakehouse_table(name, store='Silver', schema='demo')
        assert check.exceptAll(frame).count() == frame.exceptAll(check).count() == 0
    for key, frame in ns['sources'].items():
        assert frame['dataframe'].collect() == before[key]


def test_02a_fixture_content_with_the_actual_notebook_transform(demo_csv):
    """Keep the business regression active in ordinary Spark CI without Delta jars."""
    ns = {'F': F, 'sources': {key: {'dataframe': read_lakehouse_csv(f'demo/{table}.csv', inferSchema=True)}
        for key, table in [('orders', 'orders'), ('products', 'products'), ('history', 'order_history')]}}
    notebook = nbformat.read(ROOT / 'templates/DemoData/02A_full_refresh_demo.ipynb', as_version=4)
    exec(next(c.source for c in notebook.cells if c.id == 'transform'), ns)
    orders = ns['transformed_df'].collect()
    customers = ns['customer_summary_df'].collect()
    assert len(orders) == len({r.order_id for r in orders}) == 120
    assert len(customers) == len({r.customer_id for r in customers}) == 30
    assert all(r.historical_order_count == 6 and r.product_name for r in orders)
    assert sum(r.order_count for r in customers) == 120
    assert sum(Decimal(str(r.order_net_amount)) for r in orders) == Decimal('28539.15')
    assert sum(Decimal(str(r.total_order_net_amount)).quantize(Decimal('.01')) for r in customers) == Decimal('28539.15')


def test_unmigrated_native_catalogue_schema_is_rejected_without_changes(demo_delta, monkeypatch):
    """The supported native-to-JSON migration belongs to metadata setup, before demo cleanup."""
    run, state = demo_delta, _environment(monkeypatch).state
    table = 'METADATA_DATA_CATALOGUE'
    expected = metadata_table_schema_registry()[table]
    native = metadata_table_schema_registry(logical=True)[table]
    now = datetime(2026, 1, 1)
    record = {f.name: None if f.nullable else now if f.dataType.simpleString() == 'timestamp' else 'demo'
              for f in native}
    record.update(metadata_level='table', table_id='target', workspace_id='dev', _notebook_id='notebook',
                  load_strategy_parameters_json={'watermark_column': 'modified_datetime'})
    path = str(run.root / table)
    run.spark.createDataFrame([record], native).write.format('delta').save(path)
    delta = run.DeltaTable.forPath(run.spark, path)
    version = delta.history(1).first()['version']
    before = run.spark.read.format('delta').load(path).collect()
    monkeypatch.setattr(API, 'metadata_table_schema_registry', lambda: {table: expected})
    monkeypatch.setattr(API, 'read_lakehouse_table', lambda *a, **kw: run.spark.read.format('delta').load(path))
    with pytest.raises(RuntimeError, match='Run the installed package metadata setup'):
        state._demo_metadata_counts()
    assert delta.history(1).first()['version'] == version
    assert run.spark.read.format('delta').load(path).collect() == before


def test_additive_registry_column_uses_the_installed_package_schema(demo_delta, monkeypatch):
    """An already-applied compatible addition needs no notebook schema copy or new reset API."""
    run, state = demo_delta, _environment(monkeypatch).state
    table = 'METADATA_DATA_CATALOGUE'
    current = metadata_table_schema_registry()[table]
    upgraded = metadata_table_schema_registry()[table].add('new_package_field', 'string')
    frame = run.spark.createDataFrame([], current)
    monkeypatch.setattr(API, 'metadata_table_schema_registry', lambda: {table: upgraded})
    monkeypatch.setattr(API, 'read_lakehouse_table', lambda *a, **kw: frame)
    with pytest.raises(RuntimeError, match='new_package_field'):
        state._demo_metadata_counts()
    # Represent the physical result of the package's additive migration.
    frame = frame.withColumn('new_package_field', F.lit('migrated'))
    counts = state._demo_metadata_counts()
    assert counts == {table: 0}



def test_artifact_scope_is_checked_before_deletion(demo_csv, tmp_path):
    state = API._DemoReset(object(), object(), {}, demo_csv)
    state._metadata = SimpleNamespace(root=str(tmp_path))
    state._demo_table_ids = {'orders'}
    state._demo_workspaces = {'dev'}
    folder = tmp_path / 'Files/fabricops/engineering/submissions'
    folder.mkdir(parents=True)
    file = folder / 'foreign.json'
    file.write_text('{"manifest":{"operations":[{"table_id":"production-table"}]}}')
    with pytest.raises(RuntimeError, match='Non-demo'):
        state._demo_metadata_files()
    assert file.exists()
    file.write_text('{"manifest":{"operations":[{"table_id":"orders"}]}}')
    assert state._demo_metadata_files()['submissions'] == 1
    assert state._demo_metadata_files(delete=True)['submissions'] == 1
    assert not folder.exists()
