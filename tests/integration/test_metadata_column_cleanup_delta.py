"""Automatic explicit column retirement preserves real Delta rows and identity."""

from datetime import datetime
import importlib
import json
from types import SimpleNamespace

import pytest

from fabricops_kit.config.metadata_schemas import (
    AUDIT_SCHEMA_FIELDS, RETIRED_METADATA_COLUMNS, metadata_table_schema_registry,
)
from tests.helpers import call_with_spark, framework_config

pytestmark = pytest.mark.spark
setup = importlib.import_module('fabricops_kit.config.setup_metadata_tables')
TABLES = [table for table, columns in RETIRED_METADATA_COLUMNS.items() if columns]


@pytest.fixture
def cleanup_delta(spark_session, monkeypatch, tmp_path):
    """Route the setup migration to actual Delta and isolate unrelated tables."""
    from fabricops_kit.io import shared as io
    pytest.importorskip('delta.tables')
    from delta.tables import DeltaTable
    from pyspark.sql.types import StructField, StructType, StringType
    if 'DeltaSparkSessionExtension' not in spark_session.conf.get('spark.sql.extensions', ''):
        pytest.skip('requires Delta Spark extensions')
    registry = metadata_table_schema_registry()
    paths = {}

    class Unrelated:
        def __init__(self, schema):
            self.schema = schema

        def toLocalIterator(self):  # noqa: N802
            return iter(())

    def read(name, **kwargs):
        if name not in registry:
            raise RuntimeError('[PATH_NOT_FOUND]')
        if name in paths:
            return spark_session.read.format('delta').load(paths[name])
        return Unrelated(registry[name])

    monkeypatch.setattr(setup, 'read_lakehouse_table', read)
    monkeypatch.setattr(io, 'resolve_configured_lakehouse_table',
                        lambda store, name, schema, **kw: (store, name, schema, paths[name]))
    monkeypatch.setattr(setup, 'write_lakehouse_table', lambda *a, **kw: pytest.fail('migration must commit atomically'))

    def seed(table, bad=None, missing=None, empty=False, layout=None):
        path = paths[table] = str(tmp_path / table)
        canonical = registry[table]
        fields = [StructField(f.name, f.dataType, True, {'comment': f.name}) for f in canonical if f.name != missing]
        for name, replacement in RETIRED_METADATA_COLUMNS[table].items():
            fields.append(StructField(name, canonical[replacement].dataType if replacement else StringType(), True))
        fields.append(StructField('consumer_extension', StringType(), True, {'comment': 'preserve'}))
        row = {f.name: None for f in fields}
        row.update({name: datetime(2020, 1, 2, 3, 4, 5, 123456) if kind == 'timestamp' else 'original'
                    for name, kind, _ in AUDIT_SCHEMA_FIELDS})
        row['consumer_extension'] = ' keep exact bytes \n '
        for name, replacement in RETIRED_METADATA_COLUMNS[table].items():
            row[name] = row[replacement] if replacement else None
        if bad:
            row[bad] = datetime(2021, 1, 1) if RETIRED_METADATA_COLUMNS[table][bad] else 'unique historical data'
        writer = spark_session.createDataFrame([] if empty else [row, row], StructType(fields)).write.format('delta')
        if layout == 'partition':
            writer = writer.partitionBy('lineage_event_id')
        if layout == 'mapping':
            writer = writer.option('delta.columnMapping.mode', 'name')
        writer.save(path)
        delta = DeltaTable.forPath(spark_session, path)
        spark_session.sql(f"ALTER TABLE delta.`{path}` SET TBLPROPERTIES ('owner_note'='retain')")
        return SimpleNamespace(path=path, delta=delta, read=lambda: read(table),
                               version=lambda: delta.history(1).first()['version'])

    def run():
        return call_with_spark(spark_session, setup.setup_metadata_tables,
                              config=framework_config(), workspace_id='dev', verbose=False)

    return SimpleNamespace(spark=spark_session, seed=seed, run=run)


@pytest.mark.parametrize('table', TABLES)
@pytest.mark.parametrize('empty', [False, True])
def test_setup_removes_only_declared_redundant_columns(cleanup_delta, table, empty):
    """Duplicate rows, audit, extensions, properties and table ID survive cleanup."""
    rt = cleanup_delta
    missing = 'profile_scope' if 'PROFILED' in table else ('is_active' if 'CATALOGUE' in table else None)
    state = rt.seed(table, missing=missing, empty=empty)
    retired = set(RETIRED_METADATA_COLUMNS[table])
    before = state.read()
    kept = [name for name in before.columns if name not in retired]
    expected = before.select(*kept).collect()
    historical_rows = before.collect()
    detail = state.delta.detail().first().asDict()
    version = state.version()
    result = rt.run()
    assert result['status'] == 'ready', result['table_results']
    info = result['table_results'][table]
    assert info['status'] == 'evolved'
    assert info['removed_columns'] == sorted(retired)
    assert info['pre_upgrade_version'] == version and info['upgrade_version'] == version + 1
    recovery = json.loads(state.delta.history(1).first()['userMetadata'])
    assert recovery['pre_upgrade_version'] == version
    assert recovery['removed_columns'] == sorted(retired)
    if missing:
        assert info['added_columns'] == [missing]
        assert all(row[missing] is None for row in state.read().collect())
    assert not (set(state.read().columns) & retired)
    assert state.read().select(*kept).collect() == expected
    current = state.delta.detail().first().asDict()
    assert current['id'] == detail['id'] and current['properties'] == detail['properties']
    assert state.read().schema['consumer_extension'].metadata == {'comment': 'preserve'}
    # The old version remains available as the rollback boundary, including retired values.
    assert rt.spark.read.format('delta').option('versionAsOf', version).load(state.path).collect() == historical_rows
    again = rt.run()
    assert again['table_results'][table]['status'] == 'validated'
    assert state.version() == version + 1


@pytest.mark.parametrize('table,bad', [(table, column) for table in TABLES
                                     for column in RETIRED_METADATA_COLUMNS[table]])
def test_unique_retired_values_fail_before_mutation(cleanup_delta, table, bad):
    """Every retirement is checked; no useful populated legacy value disappears."""
    rt = cleanup_delta
    state = rt.seed(table, bad=bad)
    before, version = state.read().collect(), state.version()
    result = rt.run()
    assert result['failed_tables'] == [table]
    assert bad in result['table_results'][table]['message']
    assert 'not provably redundant' in result['table_results'][table]['message']
    assert state.version() == version and state.read().collect() == before


@pytest.mark.parametrize('layout', ['constraint', 'partition', 'mapping'])
def test_unsupported_layout_fails_without_modifying_metadata(cleanup_delta, layout):
    """Complex physical layouts require a separately reviewed migration."""
    rt = cleanup_delta
    table = 'METADATA_DATA_LINEAGE'
    state = rt.seed(table, layout=layout)
    if layout == 'constraint':
        rt.spark.sql(f"ALTER TABLE delta.`{state.path}` ADD CONSTRAINT keep_extension CHECK (consumer_extension IS NOT NULL)")
    before, version = state.read().collect(), state.version()
    result = rt.run()
    assert result['failed_tables'] == [table]
    assert 'constraint migration' in result['table_results'][table]['message']
    assert state.version() == version and state.read().collect() == before
