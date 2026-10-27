"""Persisted Catalogue schema conversion, recovery and Delta conflict tests."""

from tests.helpers import call_with_spark
# ruff: noqa: F811
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from dataclasses import replace
import importlib
import json
from threading import Barrier
from types import SimpleNamespace

import pytest

from fabricops_kit.config.metadata_schemas import CATALOGUE_NESTED_FIELDS, metadata_table_schema_registry
from tests.helpers import framework_config

pytestmark = pytest.mark.spark
setup = importlib.import_module('fabricops_kit.config.setup_metadata_tables')
TABLE = 'METADATA_DATA_CATALOGUE'
CANDIDATE = {'columns': ['tenant', 'id'], 'column_count': 2, 'row_count': 2**34,
             'distinct_count': 2**34, 'uniqueness_percent': 100.0, 'null_count': 0}
SCHEDULE = {'status': 'configured', 'schedules': [
    {'enabled': True, 'frequency': 'daily', 'times': ['23:00', '08:00'], 'timezone': 'Asia/Singapore'},
    {'enabled': False, 'frequency': 'weekly', 'times': [], 'timezone': 'UTC'},
]}


@pytest.fixture
def catalogue_delta(spark_session, monkeypatch, tmp_path):
    """Use real Delta at a routed Catalogue path and empty unrelated tables."""
    from fabricops_kit.io import shared as io
    from pyspark.sql.types import StringType, StructField, StructType
    pytest.importorskip('delta.tables')
    if 'DeltaSparkSessionExtension' not in spark_session.conf.get('spark.sql.extensions', ''):
        pytest.skip('requires Delta Spark extensions')
    path = str(tmp_path / 'configured-metadata' / 'custom_engineering' / TABLE)
    registry = metadata_table_schema_registry()
    schema = registry[TABLE]
    config = replace(framework_config(), engineering_metadata_schema='custom_engineering',
                     governance_metadata_schema='custom_governance')
    def read(name, **kwargs):
        if name not in registry:
            raise RuntimeError('[PATH_NOT_FOUND]')
        assert kwargs['schema'] == ('custom_engineering' if name == TABLE else
            ('custom_governance' if name in {'METADATA_DATA_STEWARD', 'METADATA_DATA_AGREEMENT',
                                           'METADATA_DATA_CONTRACT', 'METADATA_ACTIVATION_STATE'} else 'custom_engineering'))
        if name == TABLE:
            return spark_session.read.format('delta').load(path)
        return spark_session.createDataFrame([], registry[name])
    def write(frame, name, **kwargs):
        assert name == TABLE and kwargs['schema'] == 'custom_engineering'
        frame.write.format('delta').mode(kwargs['mode']).options(**kwargs.get('options', {})).save(path)
    def resolve(store, name, schema_name, **kwargs):
        assert store == 'Metadata' and name == TABLE and schema_name == 'custom_engineering'
        return None, name, schema_name, path
    monkeypatch.setattr(setup, 'read_lakehouse_table', read)
    monkeypatch.setattr(setup, 'write_lakehouse_table', write)
    monkeypatch.setattr(io, 'resolve_configured_lakehouse_table', resolve)
    def row(**values):
        audit = {field.name: datetime(2020, 2, 3, 4, 5, 6, 123456) if field.name == '_committed_at' else 'original-' + field.name
                 for field in schema.fields if not field.nullable}
        return {'metadata_level': 'table', 'table_id': 'table', 'workspace_id': 'dev',
                'table_name': 'orders', 'load_strategy': 'overwrite', 'is_active': True,
                **audit, **values}
    def seed(rows, native=(), extra=True):
        physical = StructType([StructField(f.name, StringType() if f.name in CATALOGUE_NESTED_FIELDS
            and f.name not in native else f.dataType, True, {'comment': 'original ' + f.name})
            for f in schema.fields] + ([StructField('extension', StringType(), True, {'comment': 'keep'})] if extra else []))
        spark_session.createDataFrame(rows, physical).write.format('delta').save(path)
        spark_session.sql(f"ALTER TABLE delta.`{path}` SET TBLPROPERTIES ('owner_note'='retain this')")
    def run():
        return call_with_spark(spark_session, setup.setup_metadata_tables,  config=config, workspace_id='dev', verbose=False)
    def upgrade():
        return setup._upgrade_catalogue(spark=spark_session, table=read(TABLE, schema='custom_engineering'),
            expected_schema=schema, metadata_schema='custom_engineering', context={'config': config, 'scope_workspace_id': 'dev'})
    def version():
        from delta.tables import DeltaTable
        return DeltaTable.forPath(spark_session, path).history(1).first()['version']
    return SimpleNamespace(spark=spark_session, path=path, schema=schema, row=row, seed=seed,
                           run=run, upgrade=upgrade, version=version,
                           read=lambda: spark_session.read.format('delta').load(path))


def test_fresh_setup_uses_structs_and_repeated_setup_is_noop(catalogue_delta):
    """Normal setup creates native columns immediately and never resets data."""
    rt = catalogue_delta
    first = rt.run()
    assert first['status'] == 'ready' and TABLE in first['created_tables']
    assert rt.read().schema.simpleString() == rt.schema.simpleString()
    rt.spark.createDataFrame([rt.row(load_strategy_parameters_json={'watermark_column': 'modified'})],
                             rt.schema).write.format('delta').mode('append').save(rt.path)
    version = rt.version()
    assert rt.run()['status'] == 'ready'
    assert rt.version() == version


def test_populated_v025_setup_preserves_all_rows_fields_order_and_properties(catalogue_delta):
    """Historical producer fields retain exact values, including inactive assets."""
    rt = catalogue_delta
    processing = [({}, 'overwrite'), ({'watermark_column': 'modified'}, 'append'),
                  ({'key_columns': ['tenant', 'id']}, 'scd1'),
                  ({'key_columns': ['id'], 'watermark_column': 'm'}, 'scd1'),
                  ({'key_columns': ['tenant', 'id'], 'effective_column': 'start'}, 'scd2'),
                  ({'key_columns': ['id'], 'effective_column': 'start', 'tracked_columns': ['name', 'amount'],
                    'watermark_column': 'modified'}, 'scd2')]
    rows = [rt.row(table_id=f't{index}', load_strategy=strategy, extension=f'ext-{index}',
        load_strategy_parameters_json=json.dumps(params), scheduled_refresh_json=json.dumps(SCHEDULE),
        profile_key_candidates_json=json.dumps({'status': 'resolved', 'max_combination_width': 3,
                                               'candidates': [CANDIDATE, {**CANDIDATE, 'columns': ['id', 'tenant']}] }))
        for index, (params, strategy) in enumerate(processing)]
    rows += [rt.row(table_id='inactive', metadata_level='column', column_id='col', column_name='retired',
                    data_type='decimal(18,2)', is_active=False, extension='unrelated')]
    rt.seed(rows)
    original = {r['table_id']: r.asDict(recursive=True) for r in rt.read().collect()}
    from delta.tables import DeltaTable
    detail = DeltaTable.forPath(rt.spark, rt.path).detail().first().asDict()
    version = rt.version()
    result = rt.run()
    assert result['status'] == 'ready', result['table_results'][TABLE]
    upgrade = result['table_results'][TABLE]
    assert upgrade['status'] == 'evolved' and upgrade['pre_upgrade_version'] == version
    assert rt.version() == version + 1
    current = {r['table_id']: r.asDict(recursive=True) for r in rt.read().collect()}
    assert original.keys() == current.keys()
    for key, before in original.items():
        for name, value in before.items():
            if name not in CATALOGUE_NESTED_FIELDS:
                assert current[key][name] == value
    for index, (params, _) in enumerate(processing):
        after = current[f't{index}']
        assert after['load_strategy_parameters_json'] == {name: params.get(name) for name in
            ('watermark_column', 'key_columns', 'effective_column', 'tracked_columns')}
        assert after['scheduled_refresh_json'] == SCHEDULE
        assert after['profile_key_candidates_json'] == json.loads(rows[index]['profile_key_candidates_json'])
    new_detail = DeltaTable.forPath(rt.spark, rt.path).detail().first().asDict()
    assert new_detail['id'] == detail['id'] and new_detail['properties'] == detail['properties']
    assert rt.read().schema['extension'].metadata == {'comment': 'keep'}
    assert json.loads(DeltaTable.forPath(rt.spark, rt.path).history(1).first()['userMetadata'])['pre_upgrade_version'] == version
    assert rt.run()['status'] == 'ready' and rt.version() == version + 1
    # Native processing strips only absent optional fields, preserving its logical contract.
    from fabricops_kit.pipeline.shared import catalogue_authored_processing, validated_processing
    for index, (params, strategy) in enumerate(processing):
        assert validated_processing(catalogue_authored_processing(current[f't{index}'])) == {'load_strategy': strategy, **params}


def test_mixed_types_null_blank_empty_and_historical_lists(catalogue_delta):
    """Missing discovery metadata stays unknown; empty collections keep ordering."""
    rt = catalogue_delta
    values = [None, '', ' \n ', 'null', '{}', '[]', json.dumps([CANDIDATE]),
              json.dumps({'status': 'not_evaluated', 'max_combination_width': 0, 'candidates': []}),
              json.dumps({'status': 'unresolved', 'max_combination_width': 3, 'candidates': []})]
    rt.seed([rt.row(table_id=str(i), load_strategy_parameters_json={'key_columns': []},
        scheduled_refresh_json='{}' if i == 4 else json.dumps({'status': '', 'schedules': []}),
        profile_key_candidates_json=value) for i, value in enumerate(values)], native={'load_strategy_parameters_json'})
    frame, info = rt.upgrade()
    rows = {r['table_id']: r.asDict(recursive=True) for r in frame.collect()}
    for i in range(4):
        assert rows[str(i)]['profile_key_candidates_json'] is None
    assert rows['4']['profile_key_candidates_json'] == {'status': None, 'max_combination_width': None, 'candidates': None}
    assert rows['5']['profile_key_candidates_json'] == {'status': None, 'max_combination_width': None, 'candidates': []}
    assert rows['6']['profile_key_candidates_json'] == {'status': None, 'max_combination_width': None, 'candidates': [CANDIDATE]}
    assert rows['7']['profile_key_candidates_json']['status'] == 'not_evaluated'
    assert rows['8']['profile_key_candidates_json']['status'] == 'unresolved'
    assert all(r['load_strategy_parameters_json']['key_columns'] == [] for r in rows.values())
    assert info['converted_columns'] == ['profile_key_candidates_json', 'scheduled_refresh_json']


@pytest.mark.parametrize(('field', 'value'), [
    ('load_strategy_parameters_json', '{broken'),
    ('load_strategy_parameters_json', '{"partition_column":"date"}'),
    ('load_strategy_parameters_json', '{"key_columns":[1]}'),
    ('load_strategy_parameters_json', '{"key_columns":[null]}'),
    ('scheduled_refresh_json', '{"schedules":[{"enabled":"true"}]}'),
    ('scheduled_refresh_json', '{"schedules":[{"times":[10]}]}'),
    ('scheduled_refresh_json', '{"schedules":[{"extra":true}]}'),
    ('profile_key_candidates_json', '{"candidates":[{"row_count":1.5}]}'),
    ('profile_key_candidates_json', '{"candidates":[{"column_count":true}]}'),
    ('profile_key_candidates_json', '{"max_combination_width":2147483648}'),
    ('profile_key_candidates_json', '["id"]'),
    ('profile_key_candidates_json', '{"status":"resolved","status":"unresolved"}'),
])
def test_invalid_values_abort_without_catalogue_mutation(catalogue_delta, field, value):
    """Neither schema nor data nor properties change when validation fails."""
    rt = catalogue_delta
    rt.seed([rt.row(**{field: value})])
    version, schema, rows = rt.version(), rt.read().schema, rt.read().collect()
    result = rt.run()
    assert TABLE in result['failed_tables']
    assert rt.version() == version and rt.read().schema == schema and rt.read().collect() == rows


def test_native_values_are_validated_and_not_rewritten(catalogue_delta):
    """Already native data gets the same strict validation, including null elements."""
    rt = catalogue_delta
    rt.seed([rt.row(load_strategy_parameters_json={'key_columns': ['id']})], native=set(CATALOGUE_NESTED_FIELDS))
    version = rt.version()
    assert rt.run()['status'] == 'ready' and rt.version() == version
    from delta.tables import DeltaTable
    DeltaTable.forPath(rt.spark, rt.path).update(set={'load_strategy_parameters_json.key_columns': "array('id', cast(null as string))"})
    version = rt.version()
    assert TABLE in rt.run()['failed_tables'] and rt.version() == version


@pytest.mark.parametrize('failure', ['interrupted', 'lost_ack'])
def test_interruption_and_lost_commit_acknowledgement_recover(catalogue_delta, monkeypatch, failure):
    """Rerunning setup follows physical Delta state and never converts twice."""
    from py4j.java_gateway import JavaMember
    from pyspark.sql.readwriter import DataFrameWriter
    rt = catalogue_delta
    rt.seed([rt.row(load_strategy_parameters_json='{"key_columns":["id"]}', extension='preserved')])
    version = rt.version()
    if failure == 'interrupted':
        original = DataFrameWriter.parquet
        def interrupt(writer, path, *args, **kwargs):
            original(writer, path, *args, **kwargs)
            if '_catalogue_upgrade_staging/' in path:
                raise RuntimeError('interrupted after durable staging')
        monkeypatch.setattr(DataFrameWriter, 'parquet', interrupt)
    else:
        original = JavaMember.__call__
        def lose_ack(member, *args):
            result = original(member, *args)
            if member.name == 'commit':
                raise RuntimeError('lost commit acknowledgement')
            return result
        monkeypatch.setattr(JavaMember, '__call__', lose_ack)
    assert TABLE in rt.run()['failed_tables']
    assert rt.version() == version + (failure == 'lost_ack')
    monkeypatch.undo()
    # Restore fixture routing after undoing just the failure injection.
    # Direct helper uses the already captured fixture read, but needs path routing.
    from fabricops_kit.io import shared as io
    monkeypatch.setattr(io, 'resolve_configured_lakehouse_table', lambda *a, **kw: (None, TABLE, 'custom_engineering', rt.path))
    expected_extension = 'preserved'
    expected_version = version + 1
    if failure == 'lost_ack':
        from delta.tables import DeltaTable
        DeltaTable.forPath(rt.spark, rt.path).update(set={'extension': "'subsequent valid write'"})
        expected_extension, expected_version = 'subsequent valid write', version + 2
    frame, info = rt.upgrade()
    assert (info is None) == (failure == 'lost_ack')
    assert frame.first()['extension'] == expected_extension and rt.version() == expected_version
    rt.upgrade()
    assert rt.version() == expected_version


@pytest.mark.parametrize('conflict', ['append', 'update', 'setup'])
def test_concurrent_writer_or_setup_cannot_be_overwritten(catalogue_delta, monkeypatch, conflict):
    """Race after staging, while the pinned whole-table transaction is open."""
    from pyspark.sql.readwriter import DataFrameWriter
    from delta.tables import DeltaTable
    rt = catalogue_delta
    rt.seed([rt.row(load_strategy_parameters_json='{}', extension='original')])
    original = DataFrameWriter.parquet
    barrier = Barrier(2)
    def stage(writer, path, *args, **kwargs):
        result = original(writer, path, *args, **kwargs)
        if '_catalogue_upgrade_staging/' in path:
            if conflict == 'setup':
                barrier.wait(timeout=60)
            elif conflict == 'append':
                rt.spark.createDataFrame([rt.row(table_id='newer', extension='new')], rt.read().schema).write.format('delta').mode('append').save(rt.path)
            else:
                DeltaTable.forPath(rt.spark, rt.path).update(set={'extension': "'newer'"})
        return result
    monkeypatch.setattr(DataFrameWriter, 'parquet', stage)
    if conflict == 'setup':
        def attempt(_):
            try:
                return rt.run()['table_results'][TABLE]['status']
            except Exception:
                return 'failed'
        with ThreadPoolExecutor(2) as pool:
            outcomes = list(pool.map(attempt, range(2)))
        assert sorted(outcomes) == ['evolved', 'failed']
        assert rt.read().first()['extension'] == 'original'
    else:
        with pytest.raises(Exception, match='concurrent|Concurrent'):
            rt.upgrade()
        rows = {r['table_id']: r['extension'] for r in rt.read().collect()}
        assert rows == ({'table': 'original', 'newer': 'new'} if conflict == 'append' else {'table': 'newer'})
        assert rt.read().schema['load_strategy_parameters_json'].dataType.simpleString() == 'string'


def test_native_writers_merge_discovery_and_source_drift_after_upgrade(catalogue_delta, monkeypatch):
    """Production writers and processing resolution use persisted structs directly."""
    from fabricops_kit.pipeline import shared
    write = importlib.import_module('fabricops_kit.pipeline.pipeline_write')
    drift = importlib.import_module('fabricops_kit.pipeline.check_source_drift')
    rt = catalogue_delta
    original_row = rt.row(load_strategy_parameters_json='{}', extension='keep')
    rt.seed([original_row])
    rt.upgrade()
    config = replace(framework_config(), engineering_metadata_schema='custom_engineering')
    context = {'config': config, 'scope_workspace_id': 'dev'}
    def resolve(*args, **kwargs):
        return None, TABLE, 'custom_engineering', rt.path
    monkeypatch.setattr(write, 'resolve_configured_lakehouse_table', resolve)
    monkeypatch.setattr(shared, 'resolve_configured_lakehouse_table', resolve)
    audit = {name: value for name, value in original_row.items() if name.startswith('_')}
    monkeypatch.setattr(write, 'build_runtime_audit_fields', lambda **kw: audit)
    monkeypatch.setattr(shared, 'build_runtime_audit_fields', lambda **kw: audit)
    identity = {'table_id': 'table', 'store_type': 'lakehouse', 'store': 'Silver', 'schema': 'sales', 'table_name': 'orders'}
    parameters = {'key_columns': ['tenant', 'id'], 'effective_column': 'start', 'tracked_columns': ['amount']}
    write._persist_target_processing(identity=identity, processing={'load_strategy': 'scd2', **parameters},
        scheduled_refresh=SCHEDULE, audit=audit, config=config, active_workspace_id='dev', dataframe=rt.read(),
        context=context, spark_session=rt.spark)
    shared._persist_grain_candidates(identity, [CANDIDATE], max_columns=3, config=config, active_workspace_id='dev',
                                     context=context, spark_session=rt.spark)
    current = rt.read().first().asDict(recursive=True)
    assert current['scheduled_refresh_json'] == SCHEDULE
    assert current['profile_key_candidates_json']['candidates'] == [CANDIDATE]
    assert shared.catalogue_authored_processing(current) == {'load_strategy': 'scd2', **parameters}
    # Profiling's ordinary merge preserves captured processing/schedules and extra columns.
    from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types
    profile_row = {**original_row, 'load_strategy': None, 'load_strategy_parameters_json': None,
                   'profile_key_candidates_json': {'status': 'unresolved', 'max_combination_width': 2, 'candidates': []}}
    frame = rt.spark.createDataFrame([coerce_metadata_row_types(TABLE, profile_row)], rt.schema)
    shared._upsert_catalogue_identities(catalogue_df=frame, config=config, active_workspace_id='dev', spark_session=rt.spark)
    current = rt.read().first().asDict(recursive=True)
    assert current['extension'] == 'keep' and current['scheduled_refresh_json'] == SCHEDULE
    assert current['profile_key_candidates_json'] == profile_row['profile_key_candidates_json']
    seen = []
    monkeypatch.setattr(drift, 'resolve_pipeline_data_contract', lambda *a, **kw: {'contract_id': 'contract'})
    monkeypatch.setattr(drift, 'resolve_catalogue_table_identity', lambda *a, **kw: rt.read().first().asDict(recursive=True))
    def processing(*args, **kwargs):
        value = shared.validated_processing(kwargs['authored_processing'])
        seen.append(value)
        return value
    monkeypatch.setattr(drift, 'resolve_table_processing_definition', processing)
    monkeypatch.setattr(drift, 'check_source_drift_for_target', lambda **kw: {'can_continue': True})
    assert call_with_spark(rt.spark, drift.check_source_drift, 'table', target_table_id='table',
                                    verbose=False, context=context)['can_continue']
    assert seen == [{'load_strategy': 'scd2', **parameters}]


# Reuse the actual widget hydration fixture; only Fabric UI/backend routing is mocked.
from tests.unit.test_widget_data_contract import widget_runtime  # noqa: E402, F401, F811


def test_widget_hydrates_migrated_schedules_and_composite_key(catalogue_delta, widget_runtime):
    """Persisted migrated values hydrate the existing schedule and key controls."""
    rt = catalogue_delta
    table = dict(widget_runtime['catalogue'][0])
    table.update(rt.row(), table_id='orders', load_strategy='append',
                 load_strategy_parameters_json='{}', scheduled_refresh_json=json.dumps(SCHEDULE),
                 profile_key_candidates_json=json.dumps({'status': 'resolved', 'max_combination_width': 3,
                    'candidates': [{**CANDIDATE, 'columns': ['column_0', 'column_1']}]}))
    columns = [rt.row(**row) for row in widget_runtime['catalogue'][1:]]
    rt.seed([table, *columns])
    rt.upgrade()
    rows = [row.asDict(recursive=True) for row in rt.read().collect()]
    widget_runtime['catalogue'][:] = sorted(rows, key=lambda row: row.get('column_id') is not None)
    state = widget_runtime['open']()
    assert state['scheduled_refresh'] == SCHEDULE
    assert tuple(state['_controls']['row_key_columns'].value) == ('column_0', 'column_1')
    assert 'Daily' in state['_controls']['left_pane'].children[0].value


def test_unsupported_physical_type_aborts_without_mutation(catalogue_delta):
    """A column's suffix never determines whether its physical type is supported."""
    from pyspark.sql.types import StructType, StructField, IntegerType
    rt = catalogue_delta
    physical = StructType([StructField(f.name, IntegerType() if f.name == 'scheduled_refresh_json' else f.dataType,
                                      f.nullable) for f in rt.schema.fields])
    rt.spark.createDataFrame([rt.row(scheduled_refresh_json=1)], physical).write.format('delta').save(rt.path)
    version = rt.version()
    assert TABLE in rt.run()['failed_tables'] and rt.version() == version


def test_duplicate_rows_and_unrelated_nested_columns_survive(catalogue_delta):
    """Verification preserves duplicate multiplicity and unrelated nested values."""
    from decimal import Decimal
    from pyspark.sql.types import MapType, StringType, DecimalType, StructType, StructField
    rt = catalogue_delta
    legacy = StructType([StructField(f.name, StringType() if f.name in CATALOGUE_NESTED_FIELDS else f.dataType, True)
                         for f in rt.schema.fields] + [StructField('annotations', MapType(StringType(), StringType())),
                         StructField('precise_value', DecimalType(30, 12))])
    row = rt.row(load_strategy_parameters_json='{}', annotations={'z': 'last', 'a': None},
                 precise_value=Decimal('123456789012345.123456789012'))
    rt.spark.createDataFrame([row, row], legacy).write.format('delta').save(rt.path)
    frame, _info = rt.upgrade()
    values = frame.collect()
    assert len(values) == 2 and values[0] == values[1]
    assert values[0]['annotations'] == row['annotations']
    assert values[0]['precise_value'] == row['precise_value']
    assert values[0]['_committed_at'] == row['_committed_at']


def test_fresh_setup_race_cannot_reset_a_newly_populated_catalogue(catalogue_delta, monkeypatch):
    """A concurrent first writer wins; missing-table setup must use errorifexists."""
    rt = catalogue_delta
    original = setup.write_lakehouse_table
    def race(frame, name, **kwargs):
        if name == TABLE:
            rt.seed([rt.row(table_id='newly-written', load_strategy_parameters_json={'key_columns': ['id']})],
                    native=set(CATALOGUE_NESTED_FIELDS))
        return original(frame, name, **kwargs)
    with monkeypatch.context() as fault:
        fault.setattr(setup, 'write_lakehouse_table', race)
        assert TABLE in rt.run()['failed_tables']
    version = rt.version()
    assert rt.read().first()['table_id'] == 'newly-written'
    assert rt.run()['status'] == 'ready' and rt.version() == version


def test_delta_column_mapping_identity_is_retained(catalogue_delta):
    """Use raw Delta metadata because Spark deliberately hides column mapping IDs."""
    rt = catalogue_delta
    rt.seed([rt.row(load_strategy_parameters_json='{}', extension='preserve')])
    rt.spark.sql(f"ALTER TABLE delta.`{rt.path}` SET TBLPROPERTIES "
                 "('delta.columnMapping.mode'='name', 'delta.minReaderVersion'='2', 'delta.minWriterVersion'='5')")
    log = rt.spark._jvm.org.apache.spark.sql.delta.DeltaLog.forTable(rt.spark._jsparkSession, rt.path)
    def metadata():
        return json.loads(log.startTransaction().metadata().json())['metaData']
    original = metadata()
    original_fields = json.loads(original['schemaString'])['fields']
    rt.upgrade()
    current = metadata()
    current_fields = json.loads(current['schemaString'])['fields']
    for before, after in zip(original_fields, current_fields):
        assert before['name'] == after['name'] and before['metadata'] == after['metadata']
    # Delta advances its internal allocator for newly introduced nested members;
    # existing user properties, mapping mode, protocol and physical IDs persist.
    for key, value in original['configuration'].items():
        if key != 'delta.columnMapping.maxColumnId':
            assert current['configuration'][key] == value
    assert current['id'] == original['id']
    assert rt.read().first()['extension'] == 'preserve'
    version = rt.version()
    assert rt.upgrade()[1] is None and rt.version() == version


def test_post_migration_reader_draft_and_all_catalogue_insert_paths(catalogue_delta, monkeypatch, tmp_path):
    """Exercise real identity/draft readers and both producer insert paths after upgrade."""
    from fabricops_kit.pipeline import shared
    from fabricops_kit.data_contract import shared as contracts
    writer = importlib.import_module('fabricops_kit.pipeline.pipeline_write')
    rt = catalogue_delta
    original = rt.row(store_type='lakehouse', layer='Silver', schema_name='sales',
                      load_strategy_parameters_json='{}', extension='keep')
    rt.seed([original])
    rt.upgrade()
    config = replace(framework_config(), engineering_metadata_schema='custom_engineering')
    context = {'config': config, 'scope_workspace_id': 'dev'}
    audit = {name: value for name, value in original.items() if name.startswith('_')}
    def resolve(*args, **kwargs):
        return None, TABLE, 'custom_engineering', rt.path
    monkeypatch.setattr(writer, 'resolve_configured_lakehouse_table', resolve)
    monkeypatch.setattr(shared, 'resolve_configured_lakehouse_table', resolve)
    monkeypatch.setattr(writer, 'build_runtime_audit_fields', lambda **kw: audit)
    monkeypatch.setattr(shared, 'build_runtime_audit_fields', lambda **kw: audit)
    monkeypatch.setattr(shared, 'read_lakehouse_table', lambda *a, **kw: rt.read())
    identity = shared.resolve_catalogue_table_identity(config, 'dev', 'table', spark_session=rt.spark, context=context)
    assert shared.catalogue_authored_processing(identity) == {'load_strategy': 'overwrite'}
    # Insert a new target identity using the actual target-processing merge.
    inserted = {**identity, 'table_id': 'inserted', 'table_name': 'new_orders'}
    writer._persist_target_processing(identity=inserted, processing={'load_strategy': 'scd1', 'key_columns': ['id']},
        scheduled_refresh=SCHEDULE, audit=audit, config=config, active_workspace_id='dev', dataframe=rt.read(),
        context=context, spark_session=rt.spark)
    resolved = shared.resolve_catalogue_table_identity(config, 'dev', 'inserted', spark_session=rt.spark, context=context)
    assert shared.catalogue_authored_processing(resolved) == {'load_strategy': 'scd1', 'key_columns': ['id']}
    assert resolved['scheduled_refresh_json'] == SCHEDULE and resolved['extension'] is None
    # Persist an empty discovery result using the grain-only update's typed literal.
    shared._persist_grain_candidates(identity, [], max_columns=2, config=config, active_workspace_id='dev',
                                     context=context, spark_session=rt.spark)
    assert rt.read().where("table_id='table'").first()['profile_key_candidates_json'].asDict(recursive=True) == {
        'status': 'unresolved', 'max_combination_width': 2, 'candidates': []}
    # Build and insert real profile table/column identities, retaining processing.
    business = rt.spark.createDataFrame([(1, 'a')], ['id', 'name'])
    source = rt.read().where("table_id='inserted'")
    profile_frame = shared._catalogue_dataframe_from_profiled(source, source_df=business,
        store_type='lakehouse', layer='Silver', schema_name='sales', table_name='new_orders',
        profile_key_candidates_json={'status': 'resolved', 'max_combination_width': 2,
                                     'candidates': [{**CANDIDATE, 'columns': ['id'], 'column_count': 1}]})
    shared._upsert_catalogue_identities(catalogue_df=profile_frame, config=config, active_workspace_id='dev', spark_session=rt.spark)
    inserted_rows = [row.asDict(recursive=True) for row in rt.read().where("table_id='inserted'").collect()]
    assert len(inserted_rows) == 3
    assert {row['column_name'] for row in inserted_rows if row['column_id']} == {'id', 'name'}
    resolved = shared.resolve_catalogue_table_identity(config, 'dev', 'inserted', spark_session=rt.spark, context=context)
    assert resolved['scheduled_refresh_json'] == SCHEDULE
    assert resolved['profile_key_candidates_json']['candidates'][0]['columns'] == ['id']
    assert shared.catalogue_authored_processing(resolved) == {'load_strategy': 'scd1', 'key_columns': ['id']}
    # Draft creation must read nullable optional struct fields without treating
    # absent parameters as authored settings, and keep transport payloads JSON.
    contract_path = str(tmp_path / 'contracts')
    contract_schema = metadata_table_schema_registry()['METADATA_DATA_CONTRACT']
    rt.spark.createDataFrame([], contract_schema).write.format('delta').save(contract_path)
    def read(name, **kwargs):
        return rt.read() if name == TABLE else rt.spark.read.format('delta').load(contract_path)
    def write(frame, name, **kwargs):
        assert name == 'METADATA_DATA_CONTRACT' and kwargs['mode'] == 'append'
        frame.write.format('delta').mode('append').save(contract_path)
    monkeypatch.setattr(contracts, 'read_lakehouse_table', read)
    monkeypatch.setattr(contracts, 'write_lakehouse_table', write)
    monkeypatch.setattr(contracts, 'build_runtime_audit_fields', lambda **kw: audit)
    draft = contracts.create_contract_draft(table_id='inserted', config=config, active_workspace_id='dev',
        spark_session=rt.spark, context=context, schema='governance')
    payload = json.loads(draft['contract_payload_json'])
    assert payload['table']['processing'] == {'load_strategy': 'scd1', 'key_columns': ['id']}
    assert {column['column_name'] for column in payload['table']['columns']} == {'id', 'name'}
    reopened = contracts.create_contract_draft(table_id='inserted', config=config, active_workspace_id='dev',
        spark_session=rt.spark, context=context, schema='governance')
    assert reopened['contract_payload_json'] == draft['contract_payload_json']
    assert rt.spark.read.format('delta').load(contract_path).count() == 1
