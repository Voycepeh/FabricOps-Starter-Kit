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

from fabricops_kit.config.metadata_schemas import CATALOGUE_NESTED_FIELDS, metadata_table_schema_registry, decode_metadata_row, encode_metadata_row
from tests.helpers import framework_config
from fabricops_kit.config import shared as config_shared
from fabricops_kit.data_contract.shared import file_source_identity

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
    logical_schema = metadata_table_schema_registry(logical=True)[TABLE]
    config = replace(framework_config(), engineering_metadata_schema='custom_engineering',
                     governance_metadata_schema='custom_governance')
    config.path_config.paths["prod"] = {
        "Silver": replace(config.path_config.paths["dev"]["Silver"], workspace_id="prod-physical"),
    }
    def resolve_name(workspace, **kwargs):
        return {"dev": "Development", "prod-physical": "Production", "files": "Files"}.get(workspace, workspace)
    monkeypatch.setattr(config_shared, 'resolve_asset_workspace_name', resolve_name)
    from fabricops_kit.pipeline import shared as pipeline
    monkeypatch.setattr(pipeline, 'resolve_asset_workspace_name', resolve_name)

    def read(name, **kwargs):
        if name not in registry:
            raise RuntimeError('[PATH_NOT_FOUND]')
        if name == TABLE:
            assert kwargs['schema'] == 'custom_engineering'
        if name == TABLE:
            return spark_session.read.format('delta').load(path)
        if name == 'METADATA_PROCESSING_STATE':
            return SimpleNamespace(schema=registry[name])
        return spark_session.createDataFrame([], registry[name])
    def write(frame, name, **kwargs):
        assert name == TABLE and kwargs['schema'] == 'custom_engineering'
        frame.write.format('delta').mode(kwargs['mode']).options(**(kwargs.get('options') or {})).save(path)
    def resolve(store, name, schema_name, **kwargs):
        assert store == 'Metadata' and name == TABLE and schema_name == 'custom_engineering'
        return None, name, schema_name, path
    monkeypatch.setattr(setup, 'read_lakehouse_table', read)
    monkeypatch.setattr(setup, 'write_lakehouse_table', write)
    monkeypatch.setattr(io, 'resolve_configured_lakehouse_table', resolve)
    def row(**values):
        audit = {field.name: datetime(2020, 2, 3, 4, 5, 6, 123456) if field.name == '_committed_at' else 'original-' + field.name
                 for field in schema.fields if not field.nullable}
        return {'asset_type': 'TABLE', 'table_id': 'table', 'asset_workspace_id': 'dev', 'asset_workspace_name': 'Development',
                'table_name': 'orders', 'load_strategy': 'overwrite', 'is_active': True,
                **audit, **values}
    def seed(rows, native=(), extra=True, retired=False, legacy=False, old_workspace=False):
        physical = StructType([StructField(f.name, logical_schema[f.name].dataType if f.name in native else f.dataType, True, {'comment': 'original ' + f.name})
            for f in schema.fields] + ([StructField('extension', StringType(), True, {'comment': 'keep'})] if extra else []))
        if legacy or old_workspace:
            aliases = {"asset_workspace_id": "workspace_id", "asset_workspace_name": "workspace_name"}
            physical = StructType([StructField(aliases.get(field.name, field.name), field.dataType, field.nullable, field.metadata)
                                   for field in physical if not legacy or field.name not in {"columns_json", "asset_workspace_name"}])
            rows = [{**{old: row.get(new) for new, old in aliases.items()}, **row} for row in rows]
        if legacy:
            for name in ("metadata_level", "column_id", "column_name", "data_type"):
                physical.add(StructField(name, StringType(), True))
        if retired:
            physical.add(StructField('metadata_key', StringType(), True))
        spark_session.createDataFrame(rows, physical).write.format('delta').save(path)
        spark_session.sql(f"ALTER TABLE delta.`{path}` SET TBLPROPERTIES ('owner_note'='retain this')")
    def run():
        return call_with_spark(spark_session, setup.setup_metadata_tables,  config=config, workspace_id='dev', verbose=False)
    def upgrade():
        return setup._upgrade_metadata_table(spark=spark_session, table=read(TABLE, schema='custom_engineering'), table_name=TABLE,
            expected_schema=schema, metadata_schema='custom_engineering', context={'config': config, 'scope_workspace_id': 'dev'})
    def version():
        from delta.tables import DeltaTable
        return DeltaTable.forPath(spark_session, path).history(1).first()['version']
    return SimpleNamespace(spark=spark_session, path=path, schema=schema, row=row, seed=seed,
                           run=run, upgrade=upgrade, version=version, config=config,
                           read=lambda: spark_session.read.format('delta').load(path))


def test_setup_migrates_existing_physical_workspace_columns(catalogue_delta, monkeypatch):
    """Upgrade the existing physical Catalogue and mixed history without guessing."""
    from delta.tables import DeltaTable
    from fabricops_kit.io import shared as io
    from pyspark.sql.types import StructField, StructType

    rt = catalogue_delta
    original_catalogue = rt.row(columns_json='[{"column_id":"stored-id","column_name":"id","data_type":"int"}]')
    rt.seed([original_catalogue], old_workspace=True)
    original_version = rt.version()
    paths = {}
    registry = metadata_table_schema_registry()
    audit = {key: value for key, value in original_catalogue.items() if key.startswith("_")}
    sources = {
        "METADATA_DATA_PROFILED": [
            {"asset_type": "TABLE", "table_id": "table", "profile_id": "table-profile", "workspace_id": "executor"},
            {"asset_type": "FILE", "table_id": "file:old", "profile_id": "file-profile", "workspace_id": "physical-file"}],
        "METADATA_DATA_ACCESS": [
            {"table_id": "table", "access_id": "legacy-access", "workspace_id": "executor"},
            {"asset_type": "TABLE", "table_id": "table", "access_id": "new-access", "workspace_id": "dev"}],
        "METADATA_DATA_CONTRACT_ACTIVATION": [
            {"table_id": "table", "activation_id": "activation", "workspace_id": "dev",
             "destination_json": '{"workspace_id":"dev"}'}],
    }
    for name, rows in sources.items():
        paths[name] = rt.path + "-" + name
        schema = StructType([StructField("workspace_id" if field.name == "asset_workspace_id" else field.name,
                                         field.dataType, True)
                             for field in registry[name] if field.name != "legacy_workspace_id"])
        rt.spark.createDataFrame([{**audit, **row} for row in rows], schema).write.format("delta").save(paths[name])

    read = setup.read_lakehouse_table
    resolve = io.resolve_configured_lakehouse_table
    monkeypatch.setattr(setup, "read_lakehouse_table",
        lambda name, **kwargs: rt.spark.read.format("delta").load(paths[name]) if name in paths else read(name, **kwargs))
    monkeypatch.setattr(io, "resolve_configured_lakehouse_table",
        lambda store, name, schema, **kwargs: (None, name, schema, paths[name]) if name in paths
        else resolve(store, name, schema, **kwargs))

    result = rt.run()
    assert result["status"] == "ready", result["failed_tables"]
    assert result["table_results"][TABLE]["pre_upgrade_version"] == original_version
    assert {key: rt.read().first()[key] for key in original_catalogue} == original_catalogue
    for name, original in sources.items():
        upgrade = result["table_results"][name]
        assert upgrade["pre_upgrade_version"] == 0
        assert "VERSION AS OF 0" in upgrade["recovery_guidance"]
        records = rt.spark.read.format("delta").load(paths[name]).collect()
        assert all({key: row[key] for key in audit} == audit for row in records)
        assert sorted(row["workspace_id"] for row in rt.spark.read.format("delta").option("versionAsOf", 0).load(paths[name]).collect()) == sorted(row["workspace_id"] for row in original)
        if name == "METADATA_DATA_CONTRACT_ACTIVATION":
            assert records[0]["asset_workspace_id"] == "dev"
            assert records[0]["destination_json"] == original[0]["destination_json"]
        else:
            assert {row["asset_workspace_id"] for row in records} == {None, original[1]["workspace_id"]}
            assert {row["legacy_workspace_id"] for row in records} == {None, original[0]["workspace_id"]}

    assert rt.run()["status"] == "ready"
    assert rt.version() == original_version + 1
    assert all(DeltaTable.forPath(rt.spark, path).history(1).first()["version"] == 1 for path in paths.values())


@pytest.mark.parametrize('table_name', ['METADATA_DATA_ACCESS', 'METADATA_GUARDRAIL_RESULTS'])
def test_workspace_upgrade_relaxes_only_legacy_workspace_nullability(catalogue_delta, monkeypatch, table_name):
    """Migrate NOT NULL workspace columns, retain audit constraints and accept new rows."""
    from delta.tables import DeltaTable
    from fabricops_kit.io import shared as io
    from pyspark.sql.types import StructField, StructType

    rt = catalogue_delta
    expected = metadata_table_schema_registry()[table_name]
    path = rt.path + '-' + table_name
    fields = [StructField('workspace_id' if field.name == 'asset_workspace_id' else field.name,
        field.dataType, field.name not in {'asset_workspace_id', '_committed_at'}, field.metadata)
        for field in expected if field.name not in {'legacy_workspace_id', 'execution_workspace_id'}]
    old_schema = StructType(fields)
    columns = ', '.join(f'`{field.name}` {field.dataType.simpleString()}'
        + ('' if field.nullable else ' NOT NULL') for field in fields)
    rt.spark.sql(f'CREATE TABLE delta.`{path}` ({columns}) USING DELTA')
    original = {'workspace_id': 'dev', 'table_id': 'orders', 'asset_type': 'TABLE',
        '_committed_at': datetime(2020, 2, 3, 4, 5, 6, 123456)}
    if table_name == 'METADATA_GUARDRAIL_RESULTS':
        original['result_payload_json'] = '{}'
    rt.spark.createDataFrame([original], old_schema).write.format('delta').mode('append').save(path)
    monkeypatch.setattr(io, 'resolve_configured_lakehouse_table', lambda *a, **kw: (None, table_name, 'engineering', path))

    def upgrade():
        return setup._upgrade_metadata_table(spark=rt.spark, table=rt.spark.read.format('delta').load(path),
            table_name=table_name, expected_schema=expected, metadata_schema='engineering', context={})

    frame, result = upgrade()
    assert result['pre_upgrade_version'] == 1
    assert frame.schema['legacy_workspace_id'].nullable
    assert not frame.schema['_committed_at'].nullable
    migrated = frame.first().asDict()
    physical_access = table_name == 'METADATA_DATA_ACCESS'
    assert migrated['asset_workspace_id'] == ('dev' if physical_access else None)
    assert migrated['legacy_workspace_id'] == (None if physical_access else 'dev')
    assert migrated['_committed_at'] == original['_committed_at']
    # Match the current writer: it emits no legacy workspace value.
    current = {**migrated, 'asset_workspace_id': 'dev', 'legacy_workspace_id': None}
    rt.spark.createDataFrame([current], frame.schema).write.format('delta').mode('append').save(path)
    version = DeltaTable.forPath(rt.spark, path).history(1).first()['version']
    assert upgrade()[1] is None
    assert DeltaTable.forPath(rt.spark, path).history(1).first()['version'] == version


def test_migrate_catalogue_to_one_row_per_physical_asset(catalogue_delta):
    """Migrate TABLE and FILE assets with exact IDs, scoped schemas and intact audit."""
    rt = catalogue_delta
    table_id = config_shared.build_table_id("lakehouse", "Silver", "sales", "orders")
    file = file_source_identity(workspace_id="files", item_id="item", relative_path="orders.csv", file_format="csv")
    dev = rt.row(table_id=table_id, asset_type=None, metadata_level="table", layer="Silver", store_type="lakehouse",
                 schema_name="sales", item_id=rt.config.path_config.paths["dev"]["Silver"].item_id, writer_workspace_id="writing-notebook-workspace", extension="keep",
                 load_strategy_parameters_json='{"key_columns":["id"]}')
    prod = {**dev, "workspace_id": "prod"}
    file_row = rt.row(table_id=file["source_id"], asset_type="FILE", metadata_level="file", workspace_id="FILES",
                      item_id="item", relative_path="orders.csv", file_format="csv")
    def child(parent, id_, name, dtype, **values):
        return {**parent, "metadata_level": "column", "column_id": id_, "column_name": name, "data_type": dtype, **values}
    rt.seed([dev, prod, file_row,
             child(dev, "exact-table-column-id", "id", "int"),
             child(dev, "historical-id", "retired", "long", is_active=False),
             child(prod, "exact-other-workspace-id", "name", "string"),
             child(file_row, "exact-file-column-id", "id", "double")], legacy=True)
    version = rt.version()
    result = rt.run()
    upgrade = result["table_results"][TABLE]
    assert result["status"] == "ready", upgrade
    assert upgrade["pre_upgrade_version"] == version
    assert f"VERSION AS OF {version}" in upgrade["recovery_guidance"]
    assert {"metadata_level", "column_id", "column_name", "data_type"}.isdisjoint(rt.read().columns)
    rows = {row["asset_workspace_id"]: row.asDict() for row in rt.read().collect()}
    assert len(rows) == 3
    assert rows["dev"]["table_id"] == rows["prod-physical"]["table_id"] == table_id
    assert rows["prod-physical"]["asset_workspace_name"] == "Production"
    assert rows["prod-physical"]["_workspace_name"] == dev["_workspace_name"]
    assert rows["prod-physical"]["writer_workspace_id"] == dev["writer_workspace_id"]
    assert rows["prod-physical"]["load_strategy_parameters_json"] == dev["load_strategy_parameters_json"]
    assert rows["prod-physical"]["extension"] == "keep"
    assert rows["files"]["relative_path"] == "orders.csv"
    for workspace, column_id, name, dtype in (
            ("dev", "exact-table-column-id", "id", "int"),
            ("prod-physical", "exact-other-workspace-id", "name", "string"),
            ("files", "exact-file-column-id", "id", "double")):
        assert json.loads(rows[workspace]["columns_json"]) == [
            {"column_id": column_id, "column_name": name, "data_type": dtype}]
    assert rt.spark.read.format("delta").option("versionAsOf", version).load(rt.path).count() == 7
    assert rt.run()["status"] == "ready"
    assert rt.version() == version + 1


@pytest.mark.parametrize(("problem", "diagnostic"), [
    ("unmapped", "Cannot establish the physical workspace"),
    ("missing_binding", "neither a retained item ID nor a successful Run binding"),
    ("duplicate_asset", "duplicate or conflicting parent"),
    ("duplicate_column", "duplicate column identities"),
    ("missing_id", "column_id"),
    ("orphan", "no matching parent"),
])
def test_legacy_catalogue_migration_fails_closed(catalogue_delta, problem, diagnostic):
    """Legacy ambiguities leave the source version available for correction."""
    rt = catalogue_delta
    workspace = "unmapped" if problem == "unmapped" else "dev"
    table_id = config_shared.build_table_id("lakehouse", "Silver", "sales", "orders")
    row = rt.row(table_id=table_id, workspace_id=workspace, metadata_level="table",
                 layer="Silver", store_type="lakehouse", schema_name="sales",
                 item_id=None if problem == "missing_binding" else rt.config.path_config.paths["dev"]["Silver"].item_id)
    column = {**row, "metadata_level": "column", "column_id": "legacy",
              "column_name": "customer_id", "data_type": "int"}
    rows = [row, column]
    if problem == "duplicate_asset":
        rows.append(row)
    elif problem == "duplicate_column":
        rows.append(column)
    elif problem == "missing_id":
        column["column_id"] = None
    elif problem == "orphan":
        rows = [column]
    rt.seed(rows, legacy=True)
    version = rt.version()
    result = rt.run()["table_results"][TABLE]
    assert result["status"] == "failed"
    assert diagnostic in result["message"]
    assert rt.version() == version



def test_catalogue_upgrade_keeps_history_versions_unchanged(catalogue_delta, monkeypatch):
    """Existing frozen Contracts, profiling, Lineage and Guardrail records stay intact."""
    from delta.tables import DeltaTable

    rt = catalogue_delta
    table_id = config_shared.build_table_id("lakehouse", "Silver", "sales", "orders")
    parent = rt.row(table_id=table_id, metadata_level="table", layer="Silver", store_type="lakehouse",
                    schema_name="sales", item_id=rt.config.path_config.paths["dev"]["Silver"].item_id)
    column = {**parent, "metadata_level": "column", "column_id": "retired-id",
              "column_name": "retired", "data_type": "int", "is_active": False}
    rt.seed([parent, column], legacy=True)
    frozen_payload = '{"table":{"columns":[{"column_id":"retired-id","column_name":"retired","data_type":"int"}]}}'
    history = {
        "METADATA_DATA_CONTRACT": {"contract_id": "orders", "contract_version": 2, "status": "frozen",
                                   "evidence_workspace_id": "dev", "contract_payload_json": frozen_payload},
        "METADATA_DATA_PROFILED": {"profile_id": "profile", "column_id": "retired-id", "row_count": 20, "legacy_workspace_id": "dev"},
        "METADATA_DATA_PROFILED_FREQUENCY": {"frequency_id": "frequency", "profile_id": "profile",
                                             "column_id": "retired-id", "legacy_workspace_id": "dev"},
        "METADATA_DATA_LINEAGE": {"lineage_id": "lineage", "pipeline_role": "source"},
        "METADATA_GUARDRAIL_RESULTS": {"guardrail_result_id": "result", "guardrail_rule_id": "rule",
            "guardrail_version": 1, "contract_id": "orders", "contract_version": 2,
            "can_continue": True, "status": "passed", "guardrail_type": "schema",
            "execution_type": "ungoverned", "run_id": "run", "severity": "warning", "result_payload_json": "{}",
            "execution_workspace_id": "dev"},
    }
    paths = {}
    original = {}
    audit = {key: value for key, value in parent.items() if key.startswith("_")}
    registry = metadata_table_schema_registry()
    from pyspark.sql.types import StringType, StructField, StructType
    legacy_lineage = StructType([
        *[StructField(name, StringType()) for name in ("workspace_id", "table_id", "lineage_id", "pipeline_role")],
        *[field for field in registry[TABLE] if field.name in audit],
    ])
    for name, values in history.items():
        paths[name] = rt.path + "-" + name
        row = {**audit, "table_id": table_id, "workspace_id": "dev", **values}
        schema = legacy_lineage if name == "METADATA_DATA_LINEAGE" else registry[name]
        rt.spark.createDataFrame([row], schema).write.format("delta").save(paths[name])
        original[name] = rt.spark.read.format("delta").load(paths[name]).collect()
    read = setup.read_lakehouse_table
    monkeypatch.setattr(setup, "read_lakehouse_table",
        lambda name, **kwargs: rt.spark.read.format("delta").load(paths[name]) if name in paths else read(name, **kwargs))

    result = rt.run()
    assert result["status"] == "ready", result["table_results"]
    assert rt.read().first()["columns_json"] == "[]"
    for name, path in paths.items():
        assert DeltaTable.forPath(rt.spark, path).history(1).first()["version"] == 0
        assert rt.spark.read.format("delta").load(path).collect() == original[name]


@pytest.mark.parametrize("conflicting", [False, True])
def test_legacy_catalogue_validates_retained_run_binding(catalogue_delta, monkeypatch, conflicting):
    """Resolve a legacy row without an item ID only from a matching successful operation."""
    rt = catalogue_delta
    table_id = config_shared.build_table_id("lakehouse", "Silver", "sales", "orders")
    row = rt.row(table_id=table_id, metadata_level="table", layer="Silver", store_type="lakehouse",
                 schema_name="sales", workspace_id="prod")
    rt.seed([row], legacy=True)
    version = rt.version()
    read = setup.read_lakehouse_table
    store = rt.config.path_config.paths["prod"]["Silver"]
    operations = json.dumps([{"table_id": table_id, "status": "succeeded",
        "destination": {
            "workspace_id": "original-physical" if conflicting else store.workspace_id,
            "item_id": "original-item" if conflicting else store.item_id,
        }}])

    def read_with_run(name, **kwargs):
        if name == "METADATA_PIPELINE_RUN":
            return rt.spark.createDataFrame([("prod", operations)], "workspace_id string, operations string")
        return read(name, **kwargs)

    monkeypatch.setattr(setup, "read_lakehouse_table", read_with_run)
    if conflicting:
        with pytest.raises(ValueError, match="retained Pipeline Run destinations"):
            rt.upgrade()
        assert rt.version() == version
    else:
        rt.upgrade()
        migrated = rt.read().first()
        assert (migrated["asset_workspace_id"], migrated["item_id"]) == (store.workspace_id, store.item_id)
        assert rt.version() == version + 1


def test_fresh_setup_uses_json_and_repeated_setup_is_noop(catalogue_delta):
    """Normal setup creates scalar JSON columns immediately and never resets data."""
    rt = catalogue_delta
    first = rt.run()
    assert first['status'] == 'ready' and TABLE in first['created_tables'], first['table_results']
    assert rt.read().schema.simpleString() == rt.schema.simpleString()
    rt.spark.createDataFrame([encode_metadata_row(TABLE, rt.row(load_strategy_parameters_json={'watermark_column': 'modified'}))],
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
    rows += [rt.row(table_id='inactive', is_active=False, extension='unrelated')]
    rt.seed(rows)
    original = {r['table_id']: decode_metadata_row(TABLE, r.asDict(recursive=True)) for r in rt.read().collect()}
    from delta.tables import DeltaTable
    detail = DeltaTable.forPath(rt.spark, rt.path).detail().first().asDict()
    version = rt.version()
    result = rt.run()
    assert result['status'] == 'ready', result['table_results'][TABLE]
    upgrade = result['table_results'][TABLE]
    assert upgrade['status'] == 'validated'
    assert rt.version() == version
    current = {r['table_id']: decode_metadata_row(TABLE, r.asDict(recursive=True)) for r in rt.read().collect()}
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
        assert after['profile_key_candidates_json'] == {**json.loads(rows[index]['profile_key_candidates_json']),
            'profile_scope': None, 'profiling_max_rows': None}
    new_detail = DeltaTable.forPath(rt.spark, rt.path).detail().first().asDict()
    assert new_detail['id'] == detail['id'] and new_detail['properties'] == detail['properties']
    assert rt.read().schema['extension'].metadata == {'comment': 'keep'}
    assert rt.run()['status'] == 'ready' and rt.version() == version
    # Native processing strips only absent optional fields, preserving its logical contract.
    from fabricops_kit.pipeline.shared import catalogue_authored_processing, validated_processing
    for index, (params, strategy) in enumerate(processing):
        authored = catalogue_authored_processing(current[f't{index}'])
        assert authored == {'load_strategy': strategy, **params}
        if strategy == 'append':
            with pytest.raises(ValueError, match='invalid load_strategy'):
                validated_processing(authored)
        else:
            assert validated_processing(authored) == authored


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
    rows = {r['table_id']: decode_metadata_row(TABLE, r.asDict(recursive=True)) for r in frame.collect()}
    for i in range(4):
        assert rows[str(i)]['profile_key_candidates_json'] is None
    assert rows['4']['profile_key_candidates_json'] == {'status': None, 'profile_scope': None, 'profiling_max_rows': None, 'max_combination_width': None, 'candidates': None}
    assert rows['5']['profile_key_candidates_json'] == {'status': None, 'profile_scope': None, 'profiling_max_rows': None, 'max_combination_width': None, 'candidates': []}
    assert rows['6']['profile_key_candidates_json'] == {'status': None, 'profile_scope': None, 'profiling_max_rows': None, 'max_combination_width': None, 'candidates': [CANDIDATE]}
    assert rows['7']['profile_key_candidates_json']['status'] == 'not_evaluated'
    assert rows['8']['profile_key_candidates_json']['status'] == 'unresolved'
    assert all(r['load_strategy_parameters_json']['key_columns'] == [] for r in rows.values())
    assert info['converted_columns'] == ['load_strategy_parameters_json', 'profile_key_candidates_json']


@pytest.mark.parametrize(('field', 'value'), [
    ('columns_json', '{broken'),
    ('columns_json', '[{"column_id":"c","column_name":"","data_type":"int"}]'),
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


def test_native_values_migrate_once_and_json_is_strictly_validated(catalogue_delta):
    """Already native data gets the same strict validation, including null elements."""
    rt = catalogue_delta
    rt.seed([rt.row(load_strategy_parameters_json={'key_columns': ['id']})], native=set(CATALOGUE_NESTED_FIELDS))
    version = rt.version()
    assert rt.run()['status'] == 'ready' and rt.version() == version + 1
    assert rt.run()['status'] == 'ready' and rt.version() == version + 1
    from delta.tables import DeltaTable
    DeltaTable.forPath(rt.spark, rt.path).update(set={'load_strategy_parameters_json': "'" + json.dumps({'key_columns': ['id', None]}) + "'"})
    version = rt.version()
    assert TABLE in rt.run()['failed_tables'] and rt.version() == version


@pytest.mark.parametrize('retired', [False, True])
@pytest.mark.parametrize('failure', ['interrupted', 'lost_ack'])
def test_interruption_and_lost_commit_acknowledgement_recover(catalogue_delta, monkeypatch, failure, retired):
    """Rerunning setup follows physical Delta state and never converts twice."""
    from py4j.java_gateway import JavaMember
    from pyspark.sql.readwriter import DataFrameWriter
    rt = catalogue_delta
    rt.seed([rt.row(load_strategy_parameters_json={'key_columns':['id']}, extension='preserved')], native={'load_strategy_parameters_json'}, retired=retired)
    version = rt.version()
    if failure == 'interrupted':
        original = DataFrameWriter.parquet
        def interrupt(writer, path, *args, **kwargs):
            original(writer, path, *args, **kwargs)
            if '_metadata_upgrade_staging/' in path:
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


@pytest.mark.parametrize('retired', [False, True])
@pytest.mark.parametrize('conflict', ['append', 'update', 'setup'])
def test_concurrent_writer_or_setup_cannot_be_overwritten(catalogue_delta, monkeypatch, conflict, retired):
    """Race after staging, while the pinned whole-table transaction is open."""
    from pyspark.sql.readwriter import DataFrameWriter
    from delta.tables import DeltaTable
    rt = catalogue_delta
    rt.seed([rt.row(load_strategy_parameters_json={}, extension='original')], native={'load_strategy_parameters_json'}, retired=retired)
    original = DataFrameWriter.parquet
    barrier = Barrier(2)
    def stage(writer, path, *args, **kwargs):
        result = original(writer, path, *args, **kwargs)
        if '_metadata_upgrade_staging/' in path:
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
        assert rt.read().schema['load_strategy_parameters_json'].dataType.simpleString().startswith('struct<')


def test_native_writers_preserve_processing_keys_for_source_snapshots_after_upgrade(catalogue_delta, monkeypatch):
    """Production writers and processing resolution use persisted structs directly."""
    from fabricops_kit.pipeline import shared
    write = importlib.import_module('fabricops_kit.pipeline.pipeline_write')
    rt = catalogue_delta
    original_row = rt.row(load_strategy_parameters_json='{}', extension='keep')
    rt.seed([original_row], retired=True)
    rt.upgrade()
    assert 'metadata_key' not in rt.read().columns
    config = replace(framework_config(), engineering_metadata_schema='custom_engineering')
    context = {'config': config, 'scope_workspace_id': 'dev'}
    def resolve(*args, **kwargs):
        return None, TABLE, 'custom_engineering', rt.path
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
    current = decode_metadata_row(TABLE, rt.read().first().asDict(recursive=True))
    assert current['scheduled_refresh_json'] == SCHEDULE
    assert current['profile_key_candidates_json']['candidates'] == [CANDIDATE]
    assert shared.catalogue_authored_processing(current) == {'load_strategy': 'scd2', **parameters}
    # Profiling's ordinary merge preserves captured processing/schedules and extra columns.
    profile_row = {name: original_row[name] for name in ('asset_workspace_id', 'asset_workspace_name', 'table_id', 'asset_type')}
    profile_row.update(audit)
    profile_row['profile_key_candidates_json'] = {'status': 'unresolved', 'max_combination_width': 2, 'candidates': []}
    shared.merge_catalogue_asset(profile_row, context=context, spark_session=rt.spark)
    current = decode_metadata_row(TABLE, rt.read().first().asDict(recursive=True))
    assert current['extension'] == 'keep' and current['scheduled_refresh_json'] == SCHEDULE
    assert current['profile_key_candidates_json'] == decode_metadata_row(TABLE, profile_row)['profile_key_candidates_json']
    from types import SimpleNamespace
    monkeypatch.setattr(shared, 'resolve_catalogue_table_identity', lambda *a, **kw: current)
    plan = SimpleNamespace(contracts_json='{}', workspace_id='dev')
    assert shared._source_snapshot_keys(identity, {**context, 'execution_plan': plan}) == ['tenant', 'id']


# Reuse the actual widget hydration fixture; only Fabric UI/backend routing is mocked.
from tests.unit.test_widget_data_contract import widget_runtime  # noqa: E402, F401, F811


def test_widget_reads_json_candidates_and_preserves_schedule(catalogue_delta, widget_runtime):
    """Persisted migrated values hydrate the existing schedule and key controls."""
    rt = catalogue_delta
    table = dict(widget_runtime['catalogue'][0])
    table.update(rt.row(), table_id='orders', load_strategy='append',
                 load_strategy_parameters_json='{}', scheduled_refresh_json=json.dumps(SCHEDULE),
                 profile_key_candidates_json=json.dumps({'status': 'resolved', 'max_combination_width': 3,
                    'candidates': [{**CANDIDATE, 'columns': ['column_0', 'column_1']}]}))
    table['columns_json'] = json.dumps(table['columns_json'])
    rt.seed([table])
    rt.upgrade()
    rows = [decode_metadata_row(TABLE, row.asDict(recursive=True)) for row in rt.read().collect()]
    widget_runtime['catalogue'][:] = rows
    state = widget_runtime['open']()
    assert 'scheduled_refresh' not in state
    assert decode_metadata_row(TABLE, widget_runtime['catalogue'][0])['scheduled_refresh_json'] == SCHEDULE
    assert tuple(state['_controls']['row_key_columns'].value) == ('column_0', 'column_1')


def test_unsupported_physical_type_aborts_without_mutation(catalogue_delta):
    """A column's suffix never determines whether its physical type is supported."""
    from pyspark.sql.types import StructType, StructField, IntegerType
    rt = catalogue_delta
    physical = StructType([StructField(f.name, IntegerType() if f.name == 'scheduled_refresh_json' else f.dataType,
                                      f.nullable) for f in rt.schema.fields])
    rt.spark.createDataFrame([rt.row(scheduled_refresh_json=1)], physical).write.format('delta').save(rt.path)
    version = rt.version()
    assert TABLE in rt.run()['failed_tables'] and rt.version() == version


def test_unrelated_nested_columns_survive(catalogue_delta):
    """Distinct assets retain exact extension values during verification."""
    from decimal import Decimal
    from pyspark.sql.types import MapType, StringType, DecimalType, StructType, StructField
    rt = catalogue_delta
    legacy = StructType([StructField(f.name, StringType() if f.name in CATALOGUE_NESTED_FIELDS else f.dataType, True)
                         for f in rt.schema.fields] + [StructField('annotations', MapType(StringType(), StringType())),
                         StructField('precise_value', DecimalType(30, 12))])
    row = rt.row(load_strategy_parameters_json='{}', annotations={'z': 'last', 'a': None},
                 precise_value=Decimal('123456789012345.123456789012'))
    rt.spark.createDataFrame([row, {**row, 'table_id': 'other'}], legacy).write.format('delta').save(rt.path)
    frame, _info = rt.upgrade()
    values = frame.collect()
    assert len(values) == 2 and {value['table_id'] for value in values} == {'table', 'other'}
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
    assert rt.run()['status'] == 'ready' and rt.version() == version + 1


def test_delta_column_mapping_identity_is_retained(catalogue_delta):
    """Use raw Delta metadata because Spark deliberately hides column mapping IDs."""
    rt = catalogue_delta
    rt.seed([rt.row(load_strategy_parameters_json={}, extension='preserve')], native={'load_strategy_parameters_json'})
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
    monkeypatch.setattr(shared, 'resolve_configured_lakehouse_table', resolve)
    monkeypatch.setattr(writer, 'build_runtime_audit_fields', lambda **kw: audit)
    monkeypatch.setattr(shared, 'build_runtime_audit_fields', lambda **kw: audit)
    monkeypatch.setattr(shared, 'read_lakehouse_table', lambda *a, **kw: rt.read())
    identity = shared.resolve_catalogue_table_identity(config, 'dev', 'table', spark_session=rt.spark, context=context)
    assert shared.catalogue_authored_processing(identity) == {'load_strategy': 'overwrite'}
    reader = importlib.import_module("fabricops_kit.pipeline.pipeline_read")
    business = rt.spark.createDataFrame([(1, "a")], "id int, name string")
    monkeypatch.setattr(reader, "read_lakehouse_table", lambda *a, **kw: business)
    monkeypatch.setattr(reader, "resolve_pipeline_data_contract", lambda *a, **kw: None)
    monkeypatch.setattr(reader, "observe_full_source", lambda *a, **kw: {"status": "disabled"})
    monkeypatch.setattr(shared, "build_pipeline_audit_fields", lambda **kw: audit)
    monkeypatch.setattr(reader, "persistence_permitted", lambda context: True)
    result = reader.pipeline_read(table_id="table", context={**context, "_spark_session": rt.spark}, verbose=False)
    assert result["dataframe"] is business
    table = decode_metadata_row(TABLE, rt.read().where("table_id='table'").first().asDict())
    assert [column["column_name"] for column in table["columns_json"]] == ["id", "name"]
    assert table["last_profiled_at"] is None
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
    assert decode_metadata_row(TABLE, rt.read().where("table_id='table'").first().asDict(recursive=True))['profile_key_candidates_json'] == {
        'status': 'unresolved', 'max_combination_width': 2, 'candidates': [],
        'profile_scope': None, 'profiling_max_rows': None}
    # Profile and write update the same current schema without changing processing.
    business = rt.spark.createDataFrame([(1, 'a')], ['id', 'name'])
    observed = shared.table_catalogue_observation(inserted, context=context, dataframe=business, audit=audit)
    observed['profile_key_candidates_json'] = {'status': 'resolved', 'max_combination_width': 2,
        'candidates': [{**CANDIDATE, 'columns': ['id'], 'column_count': 1}]}
    shared.merge_catalogue_asset(observed, context=context, spark_session=rt.spark)
    assert rt.read().where("table_id='inserted'").count() == 1
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
    assert 'processing' not in payload['table']
    assert shared.catalogue_authored_processing(resolved) == {'load_strategy': 'scd1', 'key_columns': ['id']}
    assert {column['column_name'] for column in payload['table']['columns']} == {'id', 'name'}
    reopened = contracts.create_contract_draft(table_id='inserted', config=config, active_workspace_id='dev',
        spark_session=rt.spark, context=context, schema='governance')
    assert reopened['contract_payload_json'] == draft['contract_payload_json']
    assert rt.spark.read.format('delta').load(contract_path).count() == 1


def test_same_asset_key_cannot_rebind_to_another_item(catalogue_delta, monkeypatch):
    """Reject a Fabric item collision without changing the current asset."""
    from fabricops_kit.pipeline import shared as pipeline

    rt = catalogue_delta
    monkeypatch.setattr(pipeline, "resolve_configured_lakehouse_table",
                        lambda *args, **kwargs: (None, TABLE, "custom_engineering", rt.path))
    parent = rt.row(item_id="original-item", load_strategy="scd1")
    rt.seed([parent])
    version = rt.version()
    with pytest.raises(Exception, match="already registered to a different Fabric item"):
        pipeline.merge_catalogue_asset({**parent, "item_id": "different-item", "load_strategy": "overwrite"},
            context={"config": rt.config, "scope_workspace_id": "dev"}, spark_session=rt.spark)
    assert rt.version() == version
    row = rt.read().first()
    assert (row["item_id"], row["load_strategy"]) == ("original-item", "scd1")
