"""Public demo reset orchestration with isolated Fabric transport boundaries."""
# ruff: noqa: D103
from copy import deepcopy
from importlib import import_module
from types import SimpleNamespace

import pytest

from fabricops_kit.config.metadata_schemas import CANONICAL_METADATA_TABLES, metadata_table_schema_registry

API = import_module('fabricops_kit.config.orchestrate_demo_reset')


def _environment(monkeypatch):
    registry = metadata_table_schema_registry()
    rows = {table: [] for table in registry}
    stores = {key: SimpleNamespace(workspace_id='dev', item_id=key, name=key,
              kind='warehouse' if key == 'Gold' else 'lakehouse', schema_enabled=True)
              for key in ('Bronze', 'Silver', 'Gold')}
    stores['Metadata'] = SimpleNamespace(workspace_id='governance', item_id='metadata-id', name='demo_metadata',
                                        kind='lakehouse', schema_enabled=True)
    setup = SimpleNamespace(workspace_id='dev', readiness_status='ready', paths=stores)
    config = SimpleNamespace(path_config=SimpleNamespace(paths={'dev': stores, 'governance': {'Metadata': stores['Metadata']}}))
    runtime = {'_notebook_setup': {'config': config, 'scope_workspace_id': 'dev', 'result': setup}}
    def read(table, **kwargs):
        return SimpleNamespace(schema=registry[table], count=lambda: len(rows[table]),
            toLocalIterator=lambda: iter([SimpleNamespace(asDict=lambda recursive=True, r=row: r) for row in rows[table]]),
            collect=lambda: rows[table], select=lambda *a: SimpleNamespace(distinct=lambda: SimpleNamespace(collect=lambda: [])))
    def request(method, path):
        if path.endswith('/notebooks') or path.endswith('/jobs/instances'):
            return {'value': []}
        return {'displayName': 'demo_metadata' if path.endswith('metadata-id') else 'configured'}
    monkeypatch.setattr(API, 'resolve_fabric_context', lambda: (config, 'dev', runtime))
    monkeypatch.setattr(API, 'read_lakehouse_table', read)
    monkeypatch.setattr(API, 'metadata_table_physical_schema', lambda config, table: 'configured-schema')
    monkeypatch.setattr(API, 'FabricNotebookClient', lambda: SimpleNamespace(request=request))
    monkeypatch.setattr(API, 'resolve_physical_table_identity', lambda *a, **kw: {'table_id': kw['table_name']})
    monkeypatch.setattr(API, 'get_spark_session', lambda: object())
    state = SimpleNamespace(_demo_config=config, context=setup, _demo_runtime=runtime, spark=object())
    return SimpleNamespace(rows=rows, config=config, setup=setup, runtime=runtime, state=state)


def _ready(monkeypatch):
    env = _environment(monkeypatch)
    monkeypatch.setattr(API, '_demo_metadata_files', lambda self, **kw: {'submissions': 0, 'dry_runs': 0, 'pipeline_snapshots': 0})
    monkeypatch.setattr(API, '_demo_remove_outputs', lambda self, **kw: None)
    monkeypatch.setattr(API, '_demo_gold_output_exists', lambda: False)
    monkeypatch.setattr(API, '_demo_verify_outputs', lambda self: None)
    monkeypatch.setattr(API, '_demo_assert_source', lambda *a: None)
    monkeypatch.setattr(API, 'read_lakehouse_csv', lambda file, **kw: SimpleNamespace(cache=lambda: SimpleNamespace(
        count=lambda: next(count for path, count in API._DEMO_SOURCES.values() if path == file), unpersist=lambda: None)))
    monkeypatch.setattr(API, 'write_lakehouse_table', lambda *a, **kw: None)
    monkeypatch.setattr(API, 'write_warehouse_table', lambda *a, **kw: None)
    monkeypatch.setattr(API, 'read_warehouse_table', lambda **kw: object())
    original = API.read_lakehouse_table
    monkeypatch.setattr(API, 'read_lakehouse_table', lambda *a, **kw: original(*a, **kw) if a else object())
    env.removed = []
    def clear(self, counts, order):
        for table in order:
            print(f'{table}: removed {len(env.rows[table])}')
            if env.rows[table]: env.removed.append(table)
            env.rows[table].clear()
    monkeypatch.setattr(API, '_demo_clear_metadata', clear)
    return env


@pytest.mark.parametrize('table', CANONICAL_METADATA_TABLES)
def test_false_preserves_every_populated_metadata_table(monkeypatch, table, capsys):
    env = _environment(monkeypatch); env.rows[table] = [{'retained': 'history'}]
    before = deepcopy(env.rows)
    API.orchestrate_demo_reset()
    assert env.rows == before
    assert 'Preview only' in capsys.readouterr().out


def test_export_is_preview_and_has_one_safe_switch():
    import inspect
    from fabricops_kit import orchestrate_demo_reset
    from fabricops_kit.public_api import PREVIEW_PUBLIC_API, SUPPORTED_PUBLIC_API
    qualified = 'fabricops_kit.config.orchestrate_demo_reset.orchestrate_demo_reset'
    assert orchestrate_demo_reset is API.orchestrate_demo_reset
    assert qualified in PREVIEW_PUBLIC_API and qualified not in SUPPORTED_PUBLIC_API
    signature = inspect.signature(orchestrate_demo_reset)
    assert list(signature.parameters) == ['reset']
    assert signature.parameters['reset'].default is False


@pytest.mark.parametrize('value', ['True', 1, None])
def test_only_boolean_enables_reset(value):
    with pytest.raises(ValueError, match='True or False'):
        API.orchestrate_demo_reset(reset=value)


def test_requires_ready_notebook_setup(monkeypatch):
    env = _environment(monkeypatch); env.setup.readiness_status = 'failed'
    with pytest.raises(RuntimeError, match='setup_notebook'):
        API.orchestrate_demo_reset(reset=True)


def test_requires_all_business_store_mappings(monkeypatch):
    env = _environment(monkeypatch); del env.setup.paths['Gold']
    with pytest.raises(RuntimeError, match='Gold'):
        API.orchestrate_demo_reset(reset=True)


def test_reset_accepts_configured_metadata_with_arbitrary_display_name(monkeypatch, capsys):
    env = _ready(monkeypatch)
    env.setup.paths['Metadata'].name = 'project_metadata'
    original_client = API.FabricNotebookClient
    def client():
        instance = original_client()
        original_request = instance.request
        def request(method, path):
            if path.endswith('/items/metadata-id'):
                return {'id': 'metadata-id', 'type': 'Lakehouse', 'displayName': 'project_metadata'}
            return original_request(method, path)
        return SimpleNamespace(request=request)
    monkeypatch.setattr(API, 'FabricNotebookClient', client)
    API.orchestrate_demo_reset(reset=True)
    assert 'RESET COMPLETE' in capsys.readouterr().out


@pytest.mark.parametrize('item', [
    {'id': 'different-id', 'type': 'Lakehouse', 'displayName': 'project_metadata'},
    {'id': 'metadata-id', 'type': 'Warehouse', 'displayName': 'project_metadata'},
])
def test_reset_rejects_mismatched_metadata_item_before_deleting(monkeypatch, item):
    env = _environment(monkeypatch)
    monkeypatch.setattr(API, 'FabricNotebookClient', lambda: SimpleNamespace(request=lambda *a: item))
    with pytest.raises(RuntimeError, match='Metadata item'):
        API.orchestrate_demo_reset(reset=True)
    assert not any(env.rows.values())


@pytest.mark.parametrize('table,row', [
    ('METADATA_DATA_CATALOGUE', {'table_id': 'production-orders'}),
    ('METADATA_PROCESSING_STATE', {'source_table_id': 'orders', 'target_table_id': 'production-target'}),
    ('METADATA_DATA_CONTRACT', {'table_id': 'orders', 'contract_payload_json': '{"table":{"table_id":"other"}}'}),
    ('METADATA_PIPELINE_RUN', {'operations': '[{"table_id":"orders","source_table_ids":["other"]}]'}),
    ('METADATA_PIPELINE_ACTIVATION', {'package_json': '{"manifest":{"execution_workspace_id":"outside"}}'}),
    ('METADATA_DATA_STEWARD', {'_workspace_id': 'outside'}),
])
def test_foreign_metadata_blocks_true_before_any_deletion(monkeypatch, table, row):
    env = _environment(monkeypatch); env.rows[table] = [row]
    before = deepcopy(env.rows)
    with pytest.raises(RuntimeError, match='Non-demo'):
        API.orchestrate_demo_reset(reset=True)
    assert env.rows == before


def test_owned_contract_and_activation_references_are_in_scope(monkeypatch):
    state = _environment(monkeypatch).state
    state._demo_table_ids = {'orders'}; state._demo_workspaces = {'dev', 'governance'}
    API._demo_check_metadata_scope(state, {'table_id': 'orders', 'workspace_id': 'DEV',
        'contract_payload_json': '{"table":{"table_id":"orders"}}',
        'package_json': '{"manifest":{"operations":[{"table_id":"orders"}]}}'})


@pytest.mark.parametrize('table,field,wrong_type', [
    ('METADATA_DATA_CATALOGUE', 'load_strategy_parameters_json', 'struct<watermark_column:string>'),
    ('METADATA_PIPELINE_RUN', 'operations', 'array<struct<table_id:string>>'),
    ('METADATA_PROCESSING_STATE', 'row_count', 'string'),
])
def test_schema_migration_must_precede_reset(monkeypatch, table, field, wrong_type):
    env = _environment(monkeypatch); expected = metadata_table_schema_registry()[table]
    actual = [SimpleNamespace(name=f.name, dataType=f.dataType) for f in expected]
    next(f for f in actual if f.name == field).dataType = SimpleNamespace(simpleString=lambda: wrong_type)
    monkeypatch.setattr(API, 'metadata_table_schema_registry', lambda: {table: expected})
    monkeypatch.setattr(API, 'read_lakehouse_table', lambda *a, **kw: SimpleNamespace(schema=actual, count=lambda: 0))
    with pytest.raises(RuntimeError, match='missing columns or incompatible types'):
        API._demo_metadata_counts(env.state)


# Historical notebook IDs must never prevent a data-and-metadata-only reset.
def test_reset_does_not_inspect_notebook_jobs(monkeypatch, capsys):
    _ready(monkeypatch)
    original_client = API.FabricNotebookClient

    def client():
        instance = original_client()
        original_request = instance.request

        def request(method, path):
            assert '/notebooks' not in path
            assert '/jobs/instances' not in path
            return original_request(method, path)

        return SimpleNamespace(request=request)

    monkeypatch.setattr(API, 'FabricNotebookClient', client)
    API.orchestrate_demo_reset(reset=True)
    assert 'RESET COMPLETE' in capsys.readouterr().out



def test_gold_clear_uses_empty_overwrite_without_ddl(monkeypatch):
    state = SimpleNamespace(_demo_gold_empty_output=object())
    calls = []
    monkeypatch.setattr(API, "write_warehouse_table", lambda frame, **kw: calls.append((frame, kw)))
    API._demo_clear_gold_output(state)
    assert calls == [(state._demo_gold_empty_output, {
        "store": "Gold", "schema": "demo", "table_name": "customer_summary", "mode": "overwrite",
    })]


def test_missing_gold_output_skips_write(monkeypatch):
    state = SimpleNamespace(_demo_gold_empty_output=None)
    monkeypatch.setattr(API, "write_warehouse_table", lambda *a, **kw: pytest.fail("must not write"))
    API._demo_clear_gold_output(state)


def test_gold_preflight_reads_only_schema_and_limits_zero_rows(monkeypatch):
    observed = []
    frame = SimpleNamespace(columns=["customer_id"], limit=lambda size: observed.append(size) or "empty")
    monkeypatch.setattr(API, "_demo_gold_output_exists", lambda: True)
    monkeypatch.setattr(API, "read_warehouse_table", lambda **kw: frame)
    assert API._demo_prepare_gold_empty_output() == "empty"
    assert observed == [0]


def test_gold_preflight_failure_preserves_metadata(monkeypatch):
    env = _ready(monkeypatch)
    env.rows["METADATA_DATA_CATALOGUE"] = [{"table_id": "orders"}]
    monkeypatch.setattr(API, "_demo_gold_output_exists", lambda: True)
    def fail(**kwargs):
        raise RuntimeError("read failed")
    monkeypatch.setattr(API, "read_warehouse_table", fail)
    with pytest.raises(RuntimeError, match="read failed"):
        API.orchestrate_demo_reset(reset=True)
    assert env.rows["METADATA_DATA_CATALOGUE"]
    assert not env.removed


def test_gold_verify_rejects_retained_rows(monkeypatch):
    import sys
    monkeypatch.setitem(sys.modules, "notebookutils",
                        SimpleNamespace(fs=SimpleNamespace(exists=lambda path: False)))
    monkeypatch.setattr(API, "resolve_configured_lakehouse_table",
                        lambda store, table, schema: (store, table, schema, "some-path"))
    state = SimpleNamespace(_demo_gold_empty_output=None,
                            _demo_bronze_catalog="demo_catalog", _demo_silver_catalog="demo_catalog",
                            spark=SimpleNamespace(catalog=SimpleNamespace(tableExists=lambda name: False)))
    monkeypatch.setattr(API, "_demo_gold_output_exists", lambda: True)
    monkeypatch.setattr(API, "read_warehouse_query",
                        lambda *a, **kw: SimpleNamespace(first=lambda: {"n": 4}))
    with pytest.raises(RuntimeError, match="still has rows"):
        API._demo_verify_outputs(state)


def test_gold_verify_accepts_empty_table_and_checks_schema(monkeypatch):
    state = SimpleNamespace(_demo_gold_empty_output=SimpleNamespace(schema="original"))
    monkeypatch.setattr(API, "_demo_gold_output_exists", lambda: True)
    monkeypatch.setattr(API, "read_warehouse_query",
                        lambda *a, **kw: SimpleNamespace(first=lambda: {"n": 0}))
    monkeypatch.setattr(API, "read_warehouse_table",
                        lambda **kw: SimpleNamespace(schema="original"))
    import sys
    monkeypatch.setitem(sys.modules, "notebookutils",
                        SimpleNamespace(fs=SimpleNamespace(exists=lambda path: False)))
    monkeypatch.setattr(API, "resolve_configured_lakehouse_table",
                        lambda store, table, schema: (store, table, schema, "some-path"))
    state._demo_bronze_catalog = state._demo_silver_catalog = "demo_catalog"
    state.spark = SimpleNamespace(catalog=SimpleNamespace(tableExists=lambda name: False))
    API._demo_verify_outputs(state)


@pytest.mark.parametrize('initially_present', [False, True])
def test_output_cleanup_is_exact_and_repeatable(monkeypatch, initially_present):
    import sys
    state = _environment(monkeypatch).state
    paths = {f'/configured/{store}/demo/{table}' for store, table in API._DEMO_REMOVALS if store != 'Gold'}
    existing = set(paths) if initially_present else set()
    existing.add('/configured/Silver/demo/unrelated')
    catalog = {f'catalog.`{table}`' for store, table in API._DEMO_REMOVALS if store != 'Gold'} if initially_present else set()
    sql, warehouse = [], []
    def spark_sql(query):
        sql.append(query)
        qualified = query.split(' ', 3)[-1] if query.startswith('DESCRIBE') else query.removeprefix('DROP TABLE ')
        if query.startswith('DESCRIBE'):
            table = qualified.split('`')[1]
            return SimpleNamespace(where=lambda _: SimpleNamespace(collect=lambda: [
                {'data_type': f'/configured/{"Bronze" if table == "orders" else "Silver"}/demo/{table}'}]))
        catalog.remove(qualified)
    def remove(path, recursive):
        assert path in paths and recursive is True
        existing.remove(path); return True
    monkeypatch.setitem(sys.modules, 'notebookutils', SimpleNamespace(fs=SimpleNamespace(exists=lambda path: path in existing, rm=remove)))
    state._demo_silver_catalog = 'catalog'
    state._demo_bronze_catalog = 'catalog'
    state.spark = SimpleNamespace(catalog=SimpleNamespace(tableExists=lambda qualified: qualified in catalog), sql=spark_sql)
    state._demo_gold_empty_output = None
    monkeypatch.setattr(API, '_demo_gold_output_exists', lambda: False)
    monkeypatch.setattr(API, '_demo_clear_gold_output', lambda state: warehouse.append(state))
    monkeypatch.setattr(API, 'resolve_configured_lakehouse_table', lambda store, table, schema: (store, table, schema, f'/configured/{store}/demo/{table}'))
    monkeypatch.setattr(API, 'read_warehouse_query', lambda *a, **kw: SimpleNamespace(first=lambda: {'n': 0}))
    before = existing.copy()
    API._demo_remove_outputs(state, preview=True)
    assert existing == before and not warehouse
    API._demo_remove_outputs(state); API._demo_remove_outputs(state); API._demo_verify_outputs(state)
    assert existing == {'/configured/Silver/demo/unrelated'}
    assert not catalog and len(warehouse) == 2
    assert warehouse == [state, state]
    assert sum(q.startswith('DROP TABLE') for q in sql) == (6 if initially_present else 0)


def test_true_clears_all_tables_children_first_and_repeated_reset_is_safe(monkeypatch, capsys):
    env = _ready(monkeypatch)
    for table in env.rows: env.rows[table] = [{'table_id': 'orders'}]
    API.orchestrate_demo_reset(reset=True)
    assert not any(env.rows.values())
    assert set(env.removed) == set(CANONICAL_METADATA_TABLES)
    assert env.removed.index('METADATA_DATA_PROFILED_FREQUENCY') < env.removed.index('METADATA_DATA_PROFILED')
    assert env.removed.index('METADATA_DATA_CONTRACT_ACTIVATION') < env.removed.index('METADATA_DATA_CONTRACT')
    API.orchestrate_demo_reset(reset=True)
    assert len(env.removed) == len(CANONICAL_METADATA_TABLES)
    output = capsys.readouterr().out
    assert output.count('RESET COMPLETE') == 2
    assert all(f'{table}: removed 0' in output for table in env.rows)


def test_fixture_failure_precedes_metadata_or_output_deletion(monkeypatch):
    env = _ready(monkeypatch); env.rows['METADATA_DATA_CATALOGUE'] = [{'table_id': 'orders'}]
    monkeypatch.setattr(API, 'read_lakehouse_csv', lambda *a, **kw: SimpleNamespace(cache=lambda: SimpleNamespace(count=lambda: -1)))
    with pytest.raises(RuntimeError, match='Restore the fixture before resetting'):
        API.orchestrate_demo_reset(reset=True)
    assert not env.removed and env.rows['METADATA_DATA_CATALOGUE']


def test_incomplete_metadata_deletion_cannot_report_success(monkeypatch, capsys):
    env = _ready(monkeypatch); env.rows['METADATA_PROCESSING_STATE'] = [{'source_table_id': 'orders'}]
    monkeypatch.setattr(API, '_demo_clear_metadata', lambda *a: None)
    with pytest.raises(RuntimeError, match='Metadata reset incomplete'):
        API.orchestrate_demo_reset(reset=True)
    assert 'RESET COMPLETE' not in capsys.readouterr().out


def test_output_verification_failure_cannot_report_success(monkeypatch, capsys):
    _ready(monkeypatch)
    def fail(self): raise RuntimeError('output remains')
    monkeypatch.setattr(API, '_demo_verify_outputs', fail)
    with pytest.raises(RuntimeError, match='output remains'):
        API.orchestrate_demo_reset(reset=True)
    assert 'RESET COMPLETE' not in capsys.readouterr().out


@pytest.mark.parametrize('store,kind,schema_enabled', [('Gold', 'lakehouse', True), ('Bronze', 'warehouse', True), ('Silver', 'lakehouse', False)])
def test_invalid_business_store_is_rejected_before_reset(monkeypatch, store, kind, schema_enabled):
    env = _environment(monkeypatch)
    env.setup.paths[store].kind = kind; env.setup.paths[store].schema_enabled = schema_enabled
    with pytest.raises(RuntimeError, match=f'Demo requires {store}'):
        API.orchestrate_demo_reset(reset=True)
    assert not any(env.rows.values())


def test_inventory_addition_requires_dependency_review_before_clearing(monkeypatch):
    env = _ready(monkeypatch)
    original = API.metadata_table_schema_registry
    expanded = {**original(), 'METADATA_FUTURE_TABLE': original()['METADATA_DATA_CATALOGUE']}
    env.rows['METADATA_FUTURE_TABLE'] = []
    env.rows['METADATA_DATA_CATALOGUE'] = [{'table_id': 'orders'}]
    original_read = API.read_lakehouse_table
    monkeypatch.setattr(API, 'metadata_table_schema_registry', lambda: expanded)
    monkeypatch.setattr(API, 'read_lakehouse_table', lambda table, **kw: SimpleNamespace(
        schema=expanded[table], count=lambda: 0) if table == 'METADATA_FUTURE_TABLE' else original_read(table, **kw))
    with pytest.raises(RuntimeError, match='Metadata inventory changed'):
        API.orchestrate_demo_reset(reset=True)
    assert env.rows['METADATA_DATA_CATALOGUE'] and not env.removed


def test_orders_csv_is_validated_without_recreating_its_table(monkeypatch):
    env = _ready(monkeypatch)
    seen, written = [], []
    reader = API.read_lakehouse_csv
    def observe(path, **kwargs):
        seen.append(path)
        return reader(path, **kwargs)
    def write(frame, *, table_name, store, **kwargs):
        written.append((store, table_name))
    monkeypatch.setattr(API, 'read_lakehouse_csv', observe)
    monkeypatch.setattr(API, 'write_lakehouse_table', write)
    monkeypatch.setattr(API, 'write_warehouse_table', write)
    API.orchestrate_demo_reset(reset=True)
    assert 'demo/orders.csv' in seen
    assert ('Bronze', 'orders') not in written
    assert set(written) == set(API._DEMO_SOURCES) - {('Bronze', 'orders')}
    assert len(written) == 4
    assert not any(env.rows.values())


def test_reset_scope_rejects_foreign_file_source_ids(monkeypatch):
    state = _environment(monkeypatch).state
    state._demo_source_ids = {'file:demo-orders'}
    state._demo_workspaces = {'dev'}
    API._demo_check_metadata_scope(state, {'source_id': 'file:demo-orders', 'workspace_id': 'dev'})
    with pytest.raises(RuntimeError, match='Non-demo file source'):
        API._demo_check_metadata_scope(state, {'source_ids': ['file:another-project']})
