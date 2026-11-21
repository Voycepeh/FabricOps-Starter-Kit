"""Direct v0.5.0-to-main metadata upgrades on real Delta tables."""
from datetime import datetime
import importlib
from types import SimpleNamespace

import pytest

from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
from tests.helpers import metadata_schema_050

pytestmark = pytest.mark.spark
setup = importlib.import_module('fabricops_kit.config.setup_metadata_tables')


@pytest.fixture
def release_delta(spark_session, monkeypatch, tmp_path):
    """Seed frozen release schemas and route only their upgrade transactions."""
    pytest.importorskip('delta.tables')
    from delta.tables import DeltaTable
    from fabricops_kit.io import shared as io
    from pyspark.sql.types import StructField, StructType, StringType
    if 'DeltaSparkSessionExtension' not in spark_session.conf.get('spark.sql.extensions', ''):
        pytest.skip('requires Delta Spark extensions')
    paths = {}
    monkeypatch.setattr(io, 'resolve_configured_lakehouse_table',
        lambda store, name, schema, **kw: (store, name, schema, paths[name]))

    def seed(table, values, *, layout=None):
        schema = metadata_schema_050(table)
        row = {field.name: datetime(2020, 1, 2, 3, 4, 5, 123456) if field.dataType.typeName() == 'timestamp'
               else True if field.dataType.typeName() == 'boolean'
               else 1 if field.dataType.typeName() in {'integer', 'long'} else 'original'
               for field in schema if not field.nullable}
        row.update(values)
        if table not in {'METADATA_DATA_CONTRACT_ACTIVATION', 'METADATA_PIPELINE_RUN', 'METADATA_PIPELINE_REGISTRY'}:
            row['consumer_extension'] = ' keep exact bytes \n '
            schema = StructType([*schema.fields, StructField('consumer_extension', StringType(), True, {'comment': 'keep'})])
        path = paths[table] = str(tmp_path / table)
        writer = spark_session.createDataFrame([row], schema).write.format('delta')
        if layout == 'mapping':
            writer = writer.option('delta.columnMapping.mode', 'name')
        if layout == 'partition':
            writer = writer.partitionBy('source_id')
        writer.save(path)
        delta = DeltaTable.forPath(spark_session, path)
        def read():
            return spark_session.read.format('delta').load(path)
        def upgrade():
            return setup._upgrade_metadata_table(spark=spark_session, table=read(), table_name=table,
                expected_schema=metadata_table_schema_registry()[table], metadata_schema='engineering', context={})
        return SimpleNamespace(read=read, upgrade=upgrade, path=path, delta=delta,
            version=lambda: delta.history(1).first()['version'])
    return SimpleNamespace(spark=spark_session, seed=seed)


@pytest.mark.parametrize('table', ['METADATA_DATA_CONTRACT', 'METADATA_DATA_CONTRACT_ACTIVATION', 'METADATA_GUARDRAIL_RESULTS'])
@pytest.mark.parametrize('file_asset', [True, False])
def test_released_identity_upgrade_preserves_rows_json_and_rollback(release_delta, table, file_asset):
    """Only the three released source_id fields are consolidated; frozen bytes stay intact."""
    from fabricops_kit.data_contract.shared import file_source_identity
    import json

    rt = release_delta
    source = file_source_identity(asset_workspace_id='physical', item_id='files', relative_path='orders.csv', file_format='csv')
    old_source = {key: value for key, value in source.items() if key not in {'table_id', 'asset_type', 'asset_workspace_id'}}
    old_source.update(source_id=source['table_id'], source_type='file', workspace_id='physical')
    frozen = json.dumps({'source': old_source, 'table': {'columns': []}}, indent=3)
    destination = json.dumps(old_source if file_asset else {'kind': 'lakehouse', 'workspace_id': 'physical', 'item_id': 'tables'}, indent=2)
    values = {'table_id': None if file_asset else 'table:orders', 'source_id': source['table_id'] if file_asset else None,
        'workspace_id': 'physical', 'contract_payload_json': frozen, 'destination_json': destination,
        'contract_id': 'orders', 'contract_version': 1, 'status': 'frozen', 'activation_id': 'activation', 'revision': 1}
    state = rt.seed(table, values)
    before, version = state.read().first().asDict(), state.version()
    identity = state.delta.detail().first()['id']
    frame, info = state.upgrade()
    after = frame.first().asDict()
    assert info['removed_columns'] == (['source_id', 'workspace_id'] if table != 'METADATA_DATA_CONTRACT' else ['source_id'])
    assert info['converted_columns'] == []
    assert after['table_id'] == (source['table_id'] if file_asset else 'table:orders')
    assert after['asset_type'] == ('FILE' if file_asset else 'TABLE')
    for name, value in before.items():
        if name not in {'source_id', 'table_id', 'workspace_id'}:
            assert after[name] == value
    if 'workspace_id' in before:
        assert after['asset_workspace_id' if table == 'METADATA_DATA_CONTRACT_ACTIVATION' else 'legacy_workspace_id'] == before['workspace_id']
    assert state.delta.detail().first()['id'] == identity
    assert rt.spark.read.format('delta').option('versionAsOf', version).load(state.path).first().asDict() == before
    assert state.upgrade()[1] is None
    assert state.version() == version + 1


@pytest.mark.parametrize('table', ['METADATA_DATA_PROFILED', 'METADATA_DATA_PROFILED_FREQUENCY', 'METADATA_DATA_ACCESS'])
def test_released_workspace_history_is_preserved_without_inference(release_delta, table):
    """Release observations have execution-scoped workspaces; do not reinterpret them as physical."""
    state = release_delta.seed(table, {'table_id': 'orders', 'workspace_id': 'execution', 'column_id': 'exact-column',
        'profile_id': 'profile', 'profile_snapshot_id': 'snapshot', 'frequency_id': 'frequency', 'value': 'original'})
    before = state.read().first().asDict()
    frame, info = state.upgrade()
    after = frame.first().asDict()
    assert info['removed_columns'] == ['workspace_id']
    assert after['legacy_workspace_id'] == 'execution' and after['asset_workspace_id'] is None
    if table != 'METADATA_DATA_ACCESS':
        assert after['asset_type'] == 'TABLE'
    assert all(after[key] == value for key, value in before.items() if key != 'workspace_id')
    assert state.upgrade()[1] is None


@pytest.mark.parametrize('layout', ['partition', 'mapping'])
def test_unsupported_released_layout_is_unchanged(release_delta, layout):
    """Reject an unsupported physical rewrite before touching the released data."""
    state = release_delta.seed('METADATA_GUARDRAIL_RESULTS', {'source_id': None, 'table_id': 'orders'}, layout=layout)
    before, version = state.read().collect(), state.version()
    with pytest.raises(ValueError, match='unsupported partition, mapping or constraint migration'):
        state.upgrade()
    assert state.version() == version and state.read().collect() == before


@pytest.mark.parametrize('table', ['METADATA_DATA_CONTRACT', 'METADATA_DATA_CONTRACT_ACTIVATION', 'METADATA_GUARDRAIL_RESULTS'])
def test_released_conflicting_ids_abort_without_modification(release_delta, table):
    """A release-backed migration cannot guess which populated identity to retain."""
    state = release_delta.seed(table, {'table_id': 'existing', 'source_id': 'file:conflicting',
        'workspace_id': 'physical', 'destination_json': '{"workspace_id":"physical","kind":"lakehouse","item_id":"files"}'})
    before, version = state.read().collect(), state.version()
    with pytest.raises(ValueError, match='not provably redundant'):
        state.upgrade()
    assert state.version() == version and state.read().collect() == before


def test_released_run_json_and_provenance_require_no_rewrite(release_delta):
    """v0.5.0 already stores JSON strings and provenance; retain their exact bytes."""
    state = release_delta.seed('METADATA_PIPELINE_RUN', {'run_id': 'released-run', 'pipeline_id': 'pipeline',
        'execution_mode': 'ungoverned', 'status': 'incomplete', 'boundary_completed': False,
        'run_schema_version': 3, 'pipeline_version': 1, 'operations': '[ ]', 'profiling': '[\n]',
        'failures': '[  ]', 'warnings_json': '[ ]'})
    before, version = state.read().collect(), state.version()
    frame, info = state.upgrade()
    assert info is None and frame.collect() == before
    assert state.version() == version
