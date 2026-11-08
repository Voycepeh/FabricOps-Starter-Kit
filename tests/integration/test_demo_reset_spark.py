"""Demo reset and retail transforms on real Spark/Delta, with only Fabric transport isolated."""
# ruff: noqa: D103
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

import nbformat
import pytest
from pyspark.sql import functions as F

from fabricops_kit import read_lakehouse_csv, read_lakehouse_table, write_lakehouse_table
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
from fabricops_kit.io.shared import retry_delta_metadata
from tests.templates.test_demo_reset import CELLS, ROOT, _helpers, _history, _scope

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


def test_real_delta_exact_metadata_deletion_repeats_without_replacing_tables(demo_delta):
    run, ns = demo_delta, _helpers()
    schema_registry = metadata_table_schema_registry()
    rows = _history()
    now = datetime(2026, 1, 1)
    # Populate the real physical schemas, including all required audit columns.
    for table in ns['_DEMO_DELETE_ORDER']:
        schema = schema_registry[table]
        records = []
        for row in rows[table]:
            record = {f.name: None if f.nullable else False if f.dataType.simpleString() == 'boolean'
                      else 1 if f.dataType.simpleString() in {'int', 'bigint'}
                      else now if f.dataType.simpleString() == 'timestamp' else 'test' for f in schema}
            record.update(row)
            for f in schema:
                if f.dataType.simpleString() == 'timestamp' and record[f.name] is not None:
                    record[f.name] = now
            records.append(record)
        path = str(run.root / table)
        run.spark.createDataFrame(records, schema).write.format('delta').save(path)
        rows[table] = [r.asDict(recursive=True) for r in run.spark.read.format('delta').load(path).collect()]
    plan = _scope(ns, rows)
    ns.update(spark=run.spark, DeltaTable=run.DeltaTable, retry_delta_metadata=retry_delta_metadata,
              _demo_config=object(), metadata_table_schema_registry=metadata_table_schema_registry,
              metadata_table_physical_schema=lambda *_: 'configured-schema',
              resolve_configured_lakehouse_table=lambda store, table, schema: (store, table, schema, str(run.root / table)))
    for table in ns['_DEMO_DELETE_ORDER']:
        path = str(run.root / table)
        identity = run.DeltaTable.forPath(run.spark, path).detail().first()['id']
        original_schema = run.spark.read.format('delta').load(path).schema
        expected = ns['_demo_row_counts'](rows[table]) - ns['_demo_row_counts'](plan[table])
        ns['_demo_delete_rows'](table, plan[table])
        ns['_demo_delete_rows'](table, plan[table])  # Retry after an uncertain acknowledgement.
        actual = [r.asDict(recursive=True) for r in run.spark.read.format('delta').load(path).collect()]
        assert ns['_demo_row_counts'](actual) == expected
        assert run.DeltaTable.forPath(run.spark, path).detail().first()['id'] == identity
        assert run.spark.read.format('delta').load(path).schema == original_schema


def test_day1_notebook_source_restoration_is_repeatable_and_content_verified(demo_delta):
    run, ns = demo_delta, _helpers()
    day1 = {(store, table): read_lakehouse_csv(file, store='Bronze', inferSchema=True)
            for (store, table), (file, count) in ns['_DEMO_SOURCES'].items()}
    def read(*, table_name, store, schema):
        # The Warehouse transport boundary is represented by a local Delta table.
        return read_lakehouse_table(table_name, store=store, schema=schema)
    def write(frame, *, table_name, store, schema, mode):
        write_lakehouse_table(frame, table_name, store=store, schema=schema, mode=mode)
    ns.update(F=F, _demo_confirmed=True, _demo_day1=day1,
              read_lakehouse_csv=read_lakehouse_csv, read_lakehouse_table=read, read_warehouse_table=read,
              write_lakehouse_table=write, write_warehouse_table=write, read_warehouse_query=lambda *a, **kw: None)
    cells = ('412da4dc-8cdd-478e-9c25-cd16d8ab97ad', '7c5f1da6-05e4-4a47-b366-44bd98f7efaa',
             '66cfd20c-2601-4b53-8abf-b32fd2b0b8ea', 'stage-day1-scenarios')
    for repeat in range(2):
        ns['orders_csv_df'] = day1[('Bronze', 'orders')]
        for cell in cells:
            exec(CELLS[cell], ns)
        for (store, table), expected in day1.items():
            persisted = read(table_name=table, store=store, schema='demo')
            assert persisted.count() == ns['_DEMO_SOURCES'][(store, table)][1]
            ns['_demo_assert_source'](persisted, expected)
    wrong = day1[('Bronze', 'orders')].withColumn('quantity', F.lit(-1))
    with pytest.raises(RuntimeError, match='content differs'):
        ns['_demo_assert_source'](wrong, day1[('Bronze', 'orders')])
    # Multisets matter: equal row counts cannot hide a missing row and a duplicate.
    expected = run.spark.createDataFrame([(1,), (2,)], 'id int')
    wrong = run.spark.createDataFrame([(1,), (1,)], 'id int')
    with pytest.raises(RuntimeError, match='content differs'):
        ns['_demo_assert_source'](wrong, expected)


def test_02a_real_transform_and_public_overwrite_preserve_source_content(demo_delta):
    ns = {'F': F, 'sources': {}}
    for key, table in [('orders', 'orders'), ('products', 'products'), ('history', 'order_history')]:
        ns['sources'][key] = {'dataframe': read_lakehouse_csv(f'Demo/{table}.csv', inferSchema=True)}
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
    ns = {'F': F, 'sources': {key: {'dataframe': read_lakehouse_csv(f'Demo/{table}.csv', inferSchema=True)}
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
