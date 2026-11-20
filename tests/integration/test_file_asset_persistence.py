"""File metadata snapshots, shared Guardrails and additive Delta migration."""
# ruff: noqa: D103, F811
from dataclasses import replace
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock
import importlib
import json

import pytest

from fabricops_kit.config.metadata_schemas import _require_catalogue_assets, metadata_table_schema_registry
from fabricops_kit.data_contract.shared import file_source_identity
from fabricops_kit.pipeline import shared
from tests.integration.test_catalogue_upgrade_delta import catalogue_delta  # noqa: F401
from tests.unit.test_pipeline_session import runtime  # noqa: F401
from tests.unit.test_unified_file_read import files  # noqa: F401


@pytest.fixture
def profile_runtime(spark_session, monkeypatch):
    config = {}
    identity = {**file_source_identity(workspace_id="physical", item_id="lakehouse", relative_path="input/a.csv", file_format="csv"), "store": "Bronze"}
    audit = {field.name: datetime(2026, 1, 1) if field.name == "_committed_at" else "audit-" + field.name
             for field in metadata_table_schema_registry()["METADATA_DATA_PROFILED"] if field.name.startswith("_")}
    context = {"config": config, "scope_workspace_id": "execution", **{k[1:]: v for k, v in audit.items()}}
    plan = shared.PipelineExecutionPlan("ungoverned", "execution", "notebook", "run", "{}", "{}", "{}", context)
    context["execution_plan"] = plan
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **kw: dict(audit))
    monkeypatch.setattr(shared, "get_spark_session", lambda **kw: spark_session)
    rows = {}
    def capture(*, dataframe, table_name, **kw):
        rows[table_name] = [row.asDict(recursive=True) for row in dataframe.collect()]
    monkeypatch.setattr(shared, "_replace_snapshot_rows", capture)
    monkeypatch.setattr(shared, "_require_catalogue_assets", Mock())
    plan.evidence["profiling_configuration"] = {"frequency_enabled": True, "grain_discovery_enabled": True}
    return SimpleNamespace(spark=spark_session, context=context, plan=plan, identity=identity, rows=rows)


@pytest.mark.parametrize("operation", ["read", "write"])
def test_file_profile_and_frequency_use_common_ids_and_commit_only_after_success(profile_runtime, operation):
    r = profile_runtime
    source = r.identity["table_id"]
    frame = r.spark.createDataFrame([(1, "a"), (2, "a")], "id int, label string")
    result = shared.schedule_file_profiling(frame, source_id=source, context=r.context, presentations=[], operation=operation)
    assert not r.rows and result["results_persisted"] is False
    summary = shared._persist_file_profile(r.identity, operation=operation, context=r.context)
    profiles = r.rows["METADATA_DATA_PROFILED"]
    frequency = r.rows["METADATA_DATA_PROFILED_FREQUENCY"]
    assert len(profiles) == 2 and frequency
    assert all(row["table_id"] == source and row["asset_type"] == "FILE" and row["run_id"] == "run"
               and row["pipeline_role"] == ("source" if operation == "read" else "target")
               and row["column_id"] is not None and "source_id" not in row for row in [*profiles, *frequency])
    assert {row["profile_id"] for row in frequency} <= {row["profile_id"] for row in profiles}
    assert summary["grain_candidates"] and result["results_persisted"] is True
    original_ids = {row["profile_id"] for row in profiles}
    shared._persist_file_profile(r.identity, operation=operation, context=r.context)
    assert {row["profile_id"] for row in r.rows["METADATA_DATA_PROFILED"]} == original_ids
    assert len(r.plan.evidence["profiling"]) == 3


def test_populated_legacy_catalogue_adds_asset_fields_without_losing_processing(catalogue_delta):
    from fabricops_kit.config.shared import build_table_id

    r = catalogue_delta
    row = r.row(table_id=build_table_id("lakehouse", "Silver", "sales", "orders"),
                asset_type=None, metadata_level="table", store_type="lakehouse",
                layer="Silver", schema_name="sales", extension="keep", item_id=r.config.path_config.paths["dev"]["Silver"].item_id)
    r.seed([row], legacy=True)
    before = r.read().first().asDict(recursive=True)
    result = r.run()
    assert result["status"] == "ready", result["table_results"]["METADATA_DATA_CATALOGUE"]
    current = r.read().first().asDict(recursive=True)
    assert all(current[key] == value for key, value in before.items()
               if key not in {"asset_type", "item_id"} and key in current)
    assert current["asset_type"] == "TABLE" and current["columns_json"] is None
    version = r.version()
    assert r.run()["status"] == "ready"
    assert r.version() == version


@pytest.mark.parametrize('table,added', [
    ('METADATA_DATA_PROFILED', {'asset_type', 'run_id', 'pipeline_role'}),
    ('METADATA_DATA_PROFILED_FREQUENCY', {'asset_type', 'run_id', 'pipeline_role'}),
])
def test_additive_file_schema_upgrade_preserves_populated_rows_and_extensions(catalogue_delta, monkeypatch, table, added):
    from pyspark.sql.types import StructType, StructField, StringType
    r = catalogue_delta
    setup = importlib.import_module('fabricops_kit.config.setup_metadata_tables')
    expected = metadata_table_schema_registry()[table]
    legacy = StructType([field for field in expected if field.name not in added] + [StructField('extension', StringType())])
    row = {field.name: datetime(2026, 1, 1) if field.name == '_committed_at' else 'original-' + field.name
           for field in legacy if not field.nullable}
    row.update(table_id='retained', extension='keep', lineage_id='released-lineage' if table.endswith('LINEAGE') else None)
    path = r.path + '-legacy-' + table
    r.spark.createDataFrame([row], legacy).write.format('delta').save(path)
    def read():
        return r.spark.read.format('delta').load(path)
    before = read().first().asDict(recursive=True)
    monkeypatch.setattr(setup, 'write_lakehouse_table', lambda frame, *a, **kw:
        frame.write.format('delta').mode('append').options(**kw['options']).save(path))
    missing = setup._validate_existing_metadata_schema(table, read().schema, expected, allow_missing=True)
    assert set(missing) == added
    setup._add_missing_metadata_columns(spark=r.spark, table_name=table, metadata_schema='engineering',
        expected_schema=expected, missing_columns=missing, context={})
    after = read().first().asDict(recursive=True)
    assert all(after[key] == value for key, value in before.items())
    assert all(after[key] is None for key in added)
    assert setup._validate_existing_metadata_schema(table, read().schema, expected, allow_missing=True) == []


def test_real_delta_file_catalogue_merges_are_idempotent(catalogue_delta, monkeypatch):
    from delta.tables import DeltaTable
    from pyspark.sql.types import StructType, StructField, StringType
    r = catalogue_delta
    registry = metadata_table_schema_registry()
    tables = ('METADATA_DATA_CATALOGUE',)
    paths = {name: r.path + '-' + name for name in tables}
    audit = {field.name: datetime(2026, 1, 1) if field.name == '_committed_at' else 'audit-' + field.name
             for field in registry[tables[0]] if field.name.startswith('_')}
    for table in tables:
        schema = StructType([*registry[table], StructField('extension', StringType())])
        r.spark.createDataFrame([], schema).write.format('delta').save(paths[table])
    monkeypatch.setattr(shared, 'get_spark_session', lambda **kw: r.spark)
    monkeypatch.setattr(shared, 'resolve_fabric_context', lambda context=None: ({}, 'execution', {'config': {}, **(context or {})}))
    monkeypatch.setattr(shared, 'build_pipeline_audit_fields', lambda **kw: dict(audit))
    monkeypatch.setattr(shared, 'metadata_table_physical_schema', lambda *a: 'engineering')
    monkeypatch.setattr(shared, 'resolve_configured_lakehouse_table', lambda store, table, schema, **kw:
        (store, table, schema, paths[table]))
    reader = importlib.import_module("fabricops_kit.io.read_lakehouse_table")
    monkeypatch.setattr(reader, "resolve_configured_lakehouse_table", shared.resolve_configured_lakehouse_table)
    identity = {**file_source_identity(workspace_id='physical', item_id='item', relative_path='a.csv', file_format='csv'), 'store': 'Bronze'}
    for _attempt in range(3):
        shared.persist_file_catalogue(identity, context={})
    catalogue = r.spark.read.format('delta').load(paths[tables[0]])
    assert catalogue.count() == 1
    first = catalogue.first().asDict()
    DeltaTable.forPath(r.spark, paths[tables[0]]).update(set={'extension': "'keep'"})
    audit['_committed_at'] = datetime(2026, 2, 1)
    shared.persist_file_catalogue(identity, context={})
    latest = r.spark.read.format('delta').load(paths[tables[0]]).first().asDict()
    assert latest['first_observed_at'] == first['first_observed_at']
    assert latest['last_observed_at'] > first['last_observed_at'] and latest['extension'] == 'keep'


# Keep the real writers available while the orchestration fixture isolates Fabric IO.
FILE_CATALOGUE_WRITER = shared.persist_file_catalogue
RUN_WRITER = shared._merge_pipeline_run_row


def test_orchestrated_file_read_commits_run_participation_before_finalization(catalogue_delta, files, monkeypatch):
    from fabricops_kit import setup_pipeline, orchestrate_read, finalize_pipeline
    r = catalogue_delta
    registry = metadata_table_schema_registry()
    paths = {table: r.path + '-orchestrated-' + table for table in
             ('METADATA_DATA_CATALOGUE', 'METADATA_PIPELINE_RUN')}
    for table, path in paths.items():
        r.spark.createDataFrame([], registry[table]).write.format('delta').save(path)
    audit = {field.name: datetime(2026, 1, 1) if field.name == '_committed_at' else 'audit-' + field.name
             for field in registry['METADATA_PIPELINE_RUN'] if field.name.startswith('_')}
    monkeypatch.setattr(shared, 'get_spark_session', lambda *a, **kw: r.spark)
    monkeypatch.setattr(shared, 'build_runtime_audit_fields', lambda **kw: dict(audit))
    monkeypatch.setattr(shared, 'resolve_configured_lakehouse_table', lambda store, table, schema, **kw:
        (store, table, schema, paths[table]))
    reader = importlib.import_module("fabricops_kit.io.read_lakehouse_table")
    monkeypatch.setattr(reader, "resolve_configured_lakehouse_table", shared.resolve_configured_lakehouse_table)
    monkeypatch.setattr(shared, 'persist_file_catalogue', FILE_CATALOGUE_WRITER)
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', RUN_WRITER)
    monkeypatch.setattr(shared, 'read_lakehouse_table', lambda table, **kw: r.spark.read.format('delta').load(paths[table]))
    files.readers['csv'].return_value = r.spark.createDataFrame([], 'id long, name string')
    session = setup_pipeline(pipeline_mode='Ungoverned', profiling_enabled=False)
    result = orchestrate_read(store='Bronze', relative_path='inventory/inventory.csv', file_format='csv')
    runs = r.spark.read.format('delta').load(paths['METADATA_PIPELINE_RUN'])
    participant = shared.pipeline_participation(runs).first().asDict()
    assert participant['table_id'] == result['table_id'] and participant['pipeline_role'] == 'source'
    assert participant['run_id'] == session.plan.plan_id and participant['asset_type'] == 'FILE'
    assert participant['_activity_id'] == audit['_activity_id']
    rows = r.spark.read.format('delta').load(paths['METADATA_DATA_CATALOGUE']).collect()
    assert len(rows) == 1
    assert [column["column_name"] for column in json.loads(rows[0]["columns_json"])] == ["id", "name"]
    finalize_pipeline(session)
    finalize_pipeline(session)
    assert r.spark.read.format('delta').load(paths['METADATA_PIPELINE_RUN']).count() == 1


REPLACE_SNAPSHOT_WRITER = shared._replace_snapshot_rows


def test_real_delta_file_profiles_and_frequencies_commit_idempotently(catalogue_delta, profile_runtime, monkeypatch):
    r = profile_runtime
    registry = metadata_table_schema_registry()
    paths = {table: catalogue_delta.path + '-profiles-' + table for table in
             ('METADATA_DATA_CATALOGUE', 'METADATA_DATA_PROFILED', 'METADATA_DATA_PROFILED_FREQUENCY')}
    for table, path in paths.items():
        r.spark.createDataFrame([], registry[table]).write.format('delta').save(path)
    monkeypatch.setattr(shared, '_replace_snapshot_rows', REPLACE_SNAPSHOT_WRITER)
    monkeypatch.setattr(shared, 'metadata_table_physical_schema', lambda *a: 'engineering')
    monkeypatch.setattr(shared, 'resolve_configured_lakehouse_table', lambda store, table, schema, **kw:
        (store, table, schema, paths[table]))
    frame = r.spark.createDataFrame([(1, 'a'), (2, 'a')], 'id int, label string')
    result = shared.schedule_file_profiling(frame, source_id=r.identity['table_id'],
        context=r.context, presentations=[])
    reader = importlib.import_module("fabricops_kit.io.read_lakehouse_table")
    monkeypatch.setattr(reader, "resolve_configured_lakehouse_table", shared.resolve_configured_lakehouse_table)
    monkeypatch.setattr(shared, "_require_catalogue_assets", _require_catalogue_assets)
    with pytest.raises(ValueError, match="requires exactly one active Catalogue asset"):
        shared._persist_file_profile(r.identity, operation='read', context=r.context)
    shared.persist_file_catalogue(r.identity, context=r.context)
    for _attempt in range(2):
        shared._persist_file_profile(r.identity, operation='read', context=r.context)
    profiles = r.spark.read.format('delta').load(paths['METADATA_DATA_PROFILED']).collect()
    frequency = r.spark.read.format('delta').load(paths['METADATA_DATA_PROFILED_FREQUENCY']).collect()
    assert len(profiles) == 2 and len(frequency) == 1
    assert all(row.table_id == r.identity['table_id'] and row.asset_type == 'FILE'
               and row.column_id is not None for row in [*profiles, *frequency])
    assert {row.profile_id for row in frequency} <= {row.profile_id for row in profiles}
    assert result['results_persisted'] is True


@pytest.mark.parametrize('table', [
    'METADATA_DATA_PROFILED', 'METADATA_DATA_PROFILED_FREQUENCY', 'METADATA_GUARDRAIL_RESULTS'])
def test_legacy_file_identity_consolidates_atomically_with_history_preserved(catalogue_delta, monkeypatch, table):
    from pyspark.sql.types import StructType, StructField, StringType
    from delta.tables import DeltaTable
    from fabricops_kit.config.shared import build_column_id
    setup = importlib.import_module('fabricops_kit.config.setup_metadata_tables')
    r = catalogue_delta
    expected = metadata_table_schema_registry()[table]
    legacy = StructType([f for f in expected if f.name not in
                         {'asset_type', 'asset_workspace_id', 'legacy_workspace_id', 'execution_workspace_id'}] +
                        [StructField(name, StringType()) for name in ('workspace_id', 'source_id', 'extension')])
    row = {f.name: datetime(2026, 1, 1) if f.name == '_committed_at' else
           True if f.name == 'can_continue' else 1 if f.name in {'contract_version', 'guardrail_version'} else 'original'
           for f in legacy if not f.nullable}
    row.update(table_id=None, source_id='file:retained', extension='keep', column_name='id',
               metadata_level='file', lineage_id='released-lineage', profile_id='released-profile',
               profile_snapshot_id='released-snapshot', frequency_id='released-frequency', workspace_id='physical')
    path = r.path + '-identity-' + table
    r.spark.createDataFrame([row], legacy).write.format('delta').save(path)
    before = r.spark.read.format('delta').load(path).first().asDict()
    monkeypatch.setattr(importlib.import_module('fabricops_kit.io.shared'), 'resolve_configured_lakehouse_table',
        lambda *a, **kw: (None, table, 'engineering', path))
    def upgrade():
        return setup._upgrade_metadata_table(spark=r.spark, table=r.spark.read.format('delta').load(path),
            table_name=table, expected_schema=expected, metadata_schema='engineering', context={})
    upgraded, result = upgrade()
    assert result and 'source_id' in result['removed_columns']
    after = upgraded.first().asDict()
    assert 'source_id' not in after and after['table_id'] == 'file:retained' and after['asset_type'] == 'FILE'
    for name, value in before.items():
        if name not in {'source_id', 'table_id', 'column_id', 'workspace_id'}:
            assert after[name] == value
    if table in {'METADATA_DATA_PROFILED', 'METADATA_DATA_PROFILED_FREQUENCY'}:
        assert after['column_id'] == build_column_id('file:retained', 'id')
        assert after['asset_workspace_id'] == 'physical'
    else:
        assert after['legacy_workspace_id'] == 'physical'
    version = DeltaTable.forPath(r.spark, path).history(1).first()['version']
    assert upgrade()[1] is None
    assert DeltaTable.forPath(r.spark, path).history(1).first()['version'] == version


@pytest.mark.parametrize('table_id,source_id', [('existing', 'file:other'), (None, ''), (None, '   ')])
def test_conflicting_legacy_asset_identities_block_migration_without_changes(catalogue_delta, monkeypatch, table_id, source_id):
    from pyspark.sql.types import StructType, StructField, StringType
    from delta.tables import DeltaTable
    setup = importlib.import_module('fabricops_kit.config.setup_metadata_tables')
    r = catalogue_delta
    table = 'METADATA_DATA_CATALOGUE'
    schema = StructType([*r.schema, StructField('source_id', StringType())])
    path = r.path + '-conflict'
    r.spark.createDataFrame([r.row(table_id=table_id, source_id=source_id)], schema).write.format('delta').save(path)
    monkeypatch.setattr(importlib.import_module('fabricops_kit.io.shared'), 'resolve_configured_lakehouse_table',
        lambda *a, **kw: (None, table, 'engineering', path))
    version = DeltaTable.forPath(r.spark, path).history(1).first()['version']
    with pytest.raises(ValueError, match='conflicting asset|incomplete physical asset identity|not provably redundant'):
        setup._upgrade_metadata_table(spark=r.spark, table=r.spark.read.format('delta').load(path),
            table_name=table, expected_schema=r.schema, metadata_schema='engineering', context={})
    assert DeltaTable.forPath(r.spark, path).history(1).first()['version'] == version
    assert r.spark.read.format('delta').load(path).first()['table_id'] == table_id


def test_file_columns_keep_ids_across_schema_changes_and_reappearance(catalogue_delta, monkeypatch):
    from fabricops_kit.config.shared import build_column_id
    r = catalogue_delta
    r.spark.createDataFrame([], r.schema).write.format('delta').save(r.path)
    identity = {**file_source_identity(workspace_id='physical', item_id='item', relative_path='a.csv', file_format='csv'), 'store': 'Bronze'}
    audit = {f.name: datetime(2026, 1, 1) if f.name == '_committed_at' else 'audit-' + f.name
             for f in r.schema if f.name.startswith('_')}
    monkeypatch.setattr(shared, 'resolve_fabric_context', lambda context=None: ({}, 'execution', {'config': {}, **(context or {})}))
    monkeypatch.setattr(shared, 'build_pipeline_audit_fields', lambda **kw: dict(audit))
    monkeypatch.setattr(shared, 'get_spark_session', lambda **kw: r.spark)
    monkeypatch.setattr(shared, 'metadata_table_physical_schema', lambda *a: 'engineering')
    monkeypatch.setattr(shared, 'resolve_configured_lakehouse_table', lambda *a, **kw: (*a, r.path))
    monkeypatch.setattr(shared, 'resolve_asset_workspace_name', lambda *a, **kw: 'Physical Workspace')
    def observe(columns):
        shared.persist_file_catalogue(identity, context={}, columns=[
            dict(column_name=name, data_type=kind) for name, kind in columns])
        return {column['column_name']: column for column in json.loads(r.read().first()['columns_json'])}
    initial = observe([('id', 'bigint'), ('name', 'string')])
    changed = observe([('ID', 'string')])
    assert changed['ID']['column_id'] == initial['id']['column_id'] == build_column_id(identity['table_id'], 'id')
    assert changed['ID']['data_type'] == 'string'
    assert 'name' not in changed
    restored = observe([('id', 'bigint'), ('name', 'string')])
    assert restored['name']['column_id'] == initial['name']['column_id']
    assert observe([]) == {}
    assert r.read().first()['columns_json'] == '[]'
    assert r.read().count() == 1
