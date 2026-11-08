"""Single-cell demo reset: preview, explicit boolean authorization and metadata scope checks."""
# ruff: noqa: D103
import ast
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import nbformat
import pytest

from fabricops_kit.config.metadata_schemas import CANONICAL_METADATA_TABLES, metadata_table_schema_registry

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / 'templates/DemoData/00C_demo_setup.ipynb'
CELLS = {cell.id: cell.source for cell in nbformat.read(NOTEBOOK, as_version=4).cells}


def _helpers():
    tree = ast.parse(CELLS['reset'])
    tree.body = [node for node in tree.body if isinstance(node, ast.FunctionDef)
                 or isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id.startswith('_DEMO_') for t in node.targets)
                 or isinstance(node, ast.Import) and node.names[0].name == 'json'
                 or isinstance(node, ast.ImportFrom) and node.module == 'urllib.error']
    ns = {}
    exec(compile(tree, str(NOTEBOOK), 'exec'), ns)
    return ns


def _run_reset(ns):
    """Execute the real cell with only Fabric transport/physical boundaries supplied by a test."""
    tree = ast.parse(CELLS['reset'])
    tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef))
                 and not (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'RESET_DEMO' for t in node.targets))]
    exec(compile(tree, str(NOTEBOOK), 'exec'), ns)


def _namespace():
    ns = _helpers()
    registry = metadata_table_schema_registry()
    rows = {table: [] for table in registry}
    stores = {key: SimpleNamespace(workspace_id='dev', item_id=key, name=key,
              kind='warehouse' if key == 'Gold' else 'lakehouse', schema_enabled=True)
              for key in ('Bronze', 'Silver', 'Gold')}
    stores['Metadata'] = SimpleNamespace(workspace_id='governance', item_id='metadata-id', name='demo_metadata',
                                        kind='lakehouse', schema_enabled=True)
    context = SimpleNamespace(workspace_id='dev', readiness_status='ready', paths=stores)
    config = SimpleNamespace(path_config=SimpleNamespace(paths={'dev': stores, 'governance': {'Metadata': stores['Metadata']}}))
    def read(table, **kwargs):
        return SimpleNamespace(schema=registry[table], count=lambda: len(rows[table]),
            toLocalIterator=lambda: iter([SimpleNamespace(asDict=lambda recursive=True, r=row: r) for row in rows[table]]),
            collect=lambda: rows[table], select=lambda *a: SimpleNamespace(distinct=lambda: SimpleNamespace(collect=lambda: [])))
    def request(method, path):
        if path.endswith('/notebooks') or path.endswith('/jobs/instances'):
            return {'value': []}
        return {'displayName': 'demo_metadata' if path.endswith('metadata-id') else 'configured'}
    ns.update(RESET_DEMO=False, context=context, _demo_config=config, _demo_runtime={},
              resolve_fabric_context=lambda: (config, 'dev', {}), read_lakehouse_table=read,
              metadata_table_schema_registry=metadata_table_schema_registry,
              metadata_table_physical_schema=lambda config, table: 'configured-schema',
              FabricNotebookClient=lambda: SimpleNamespace(request=request),
              resolve_table_id=lambda **kw: kw['table_name'])
    return ns, rows


@pytest.mark.parametrize('table', CANONICAL_METADATA_TABLES)
def test_false_previews_and_preserves_every_populated_metadata_table(table, capsys):
    ns, rows = _namespace(); rows[table] = [{'retained': 'history'}]
    before = deepcopy(rows)
    _run_reset(ns)
    assert rows == before
    assert 'Preview only' in capsys.readouterr().out


def test_true_requires_the_actual_dedicated_item_name_before_deleting():
    ns, rows = _namespace(); ns['RESET_DEMO'] = True
    ns['FabricNotebookClient'] = lambda: SimpleNamespace(request=lambda *a: {'displayName': 'production_metadata'})
    with pytest.raises(RuntimeError, match='dedicated demo_metadata'):
        _run_reset(ns)
    assert not any(rows.values())


@pytest.mark.parametrize('value', ['True', 1, None])
def test_only_a_boolean_enables_reset(value):
    ns, _ = _namespace(); ns['RESET_DEMO'] = value
    with pytest.raises(ValueError, match='True or False'):
        _run_reset(ns)


@pytest.mark.parametrize('table,row', [
    ('METADATA_DATA_CATALOGUE', {'table_id': 'production-orders'}),
    ('METADATA_PROCESSING_STATE', {'source_table_id': 'orders', 'target_table_id': 'production-target'}),
    ('METADATA_DATA_CONTRACT', {'table_id': 'orders', 'contract_payload_json': '{"table":{"table_id":"other"}}'}),
    ('METADATA_PIPELINE_RUN', {'operations': '[{"table_id":"orders","source_table_ids":["other"]}]'}),
    ('METADATA_PIPELINE_ACTIVATION', {'package_json': '{"manifest":{"execution_workspace_id":"outside"}}'}),
    ('METADATA_DATA_STEWARD', {'_workspace_id': 'outside'}),
])
def test_foreign_metadata_blocks_true_before_any_deletion(table, row):
    ns, rows = _namespace(); ns['RESET_DEMO'] = True; rows[table] = [row]
    before = deepcopy(rows)
    with pytest.raises(RuntimeError, match='Non-demo'):
        _run_reset(ns)
    assert rows == before


def test_owned_contract_and_activation_references_are_in_scope():
    ns = _helpers(); ns.update(_demo_table_ids={'orders'}, _demo_workspaces={'dev', 'governance'})
    ns['_demo_check_metadata_scope']({'table_id': 'orders', 'workspace_id': 'DEV',
        'contract_payload_json': '{"table":{"table_id":"orders"}}',
        'package_json': '{"manifest":{"operations":[{"table_id":"orders"}]}}'})


@pytest.mark.parametrize('table,field,wrong_type', [
    ('METADATA_DATA_CATALOGUE', 'load_strategy_parameters_json', 'struct<watermark_column:string>'),
    ('METADATA_PIPELINE_RUN', 'operations', 'array<struct<table_id:string>>'),
    ('METADATA_PROCESSING_STATE', 'row_count', 'string'),
])
def test_schema_migration_must_precede_reset(table, field, wrong_type):
    ns = _helpers(); expected = metadata_table_schema_registry()[table]
    actual = [SimpleNamespace(name=f.name, dataType=f.dataType) for f in expected]
    next(f for f in actual if f.name == field).dataType = SimpleNamespace(simpleString=lambda: wrong_type)
    ns.update(_demo_config=object(), metadata_table_schema_registry=lambda: {table: expected},
              metadata_table_physical_schema=lambda *_: 'engineering',
              read_lakehouse_table=lambda *a, **kw: SimpleNamespace(schema=actual, count=lambda: 0))
    with pytest.raises(RuntimeError, match='missing columns or incompatible types'):
        ns['_demo_metadata_counts']()


@pytest.mark.parametrize('status', ['NotStarted', 'InProgress', 'Unknown'])
def test_active_demo_job_blocks_reset(status):
    ns, _ = _namespace()
    def request(method, path):
        if path.endswith('/notebooks'):
            return {'value': [{'id': 'notebook', 'displayName': '02A_full_refresh_demo'}]}
        return {'value': [{'status': status}]}
    ns['_demo_client'] = SimpleNamespace(request=request)
    with pytest.raises(RuntimeError, match='job is active'):
        ns['_demo_check_jobs']()


def test_reset_is_one_code_cell_and_false_cannot_write_later_cells():
    notebook = nbformat.read(NOTEBOOK, as_version=4); nbformat.validate(notebook)
    assert [c.id for c in notebook.cells if c.id.startswith('reset') and c.cell_type == 'code'] == ['reset']
    assert CELLS['reset'].startswith('RESET_DEMO = False')
    for cell in notebook.cells:
        if cell.cell_type != 'code': continue
        compile(cell.source, str(NOTEBOOK), 'exec')
        assert all(node.name.startswith('_demo_') for node in ast.walk(ast.parse(cell.source)) if isinstance(node, ast.FunctionDef))
        if cell.id != 'reset':
            assert 'write_lakehouse_table(' not in cell.source and 'write_warehouse_table(' not in cell.source


def test_demo_file_paths_are_lowercase():
    for path in (ROOT / 'templates/DemoData').glob('*.ipynb'):
        assert 'Demo/' not in path.read_text()


@pytest.mark.parametrize('initially_present', [False, True])
def test_output_cleanup_is_exact_and_repeatable(monkeypatch, initially_present):
    import sys
    ns = _helpers()
    paths = {f'/configured/{store}/demo/{table}' for store, table in ns['_DEMO_OUTPUTS'] if store == 'Silver'}
    existing = set(paths) if initially_present else set()
    existing.add('/configured/Silver/demo/unrelated')
    catalog = {f'catalog.`{table}`' for store, table in ns['_DEMO_OUTPUTS'] if store == 'Silver'} if initially_present else set()
    sql, warehouse = [], []
    def spark_sql(query):
        sql.append(query)
        qualified = query.split(' ', 3)[-1] if query.startswith('DESCRIBE') else query.removeprefix('DROP TABLE ')
        if query.startswith('DESCRIBE'):
            table = qualified.split('`')[1]
            return SimpleNamespace(where=lambda _: SimpleNamespace(collect=lambda: [
                {'data_type': f'/configured/Silver/demo/{table}'}]))
        catalog.remove(qualified)
    def remove(path, recursive):
        assert path in paths and recursive is True
        existing.remove(path)
        return True
    monkeypatch.setitem(sys.modules, 'notebookutils', SimpleNamespace(fs=SimpleNamespace(
        exists=lambda path: path in existing, rm=remove)))
    ns.update(_demo_silver_catalog='catalog', spark=SimpleNamespace(catalog=SimpleNamespace(
        tableExists=lambda qualified: qualified in catalog), sql=spark_sql),
        context=SimpleNamespace(paths={'Gold': object()}), resolve_warehouse_name=lambda *_: 'physical-gold',
        execute_warehouse_sql=lambda *a, **kw: warehouse.append((a, kw)),
        resolve_configured_lakehouse_table=lambda store, table, schema: (store, table, schema, f'/configured/{store}/demo/{table}'),
        read_warehouse_query=lambda *a, **kw: SimpleNamespace(first=lambda: {'n': 0}))
    before = existing.copy()
    ns['_demo_remove_outputs'](preview=True)
    assert existing == before and not warehouse
    ns['_demo_remove_outputs']()
    ns['_demo_remove_outputs']()
    ns['_demo_verify_outputs']()
    assert existing == {'/configured/Silver/demo/unrelated'}
    assert not catalog and len(warehouse) == 2
    assert all('DROP TABLE [demo].[customer_summary]' in call[0][2] for call in warehouse)
    assert all(call[1]['database_name'] == 'physical-gold' for call in warehouse)
    assert sum(q.startswith('DROP TABLE') for q in sql) == (5 if initially_present else 0)



def _ready_namespace():
    ns, rows = _namespace()
    original_read = ns['read_lakehouse_table']
    ns.update(RESET_DEMO=True, spark=object(), _demo_check_jobs=lambda: None,
              _demo_metadata_files=lambda **kw: {'submissions': 0, 'dry_runs': 0, 'pipeline_snapshots': 0},
              _demo_remove_outputs=lambda **kw: None, _demo_verify_outputs=lambda: None,
              _demo_assert_source=lambda *a: None,
              resolve_configured_lakehouse_table=lambda store, table, schema: (store, table, schema, table),
              read_lakehouse_csv=lambda file, **kw: SimpleNamespace(cache=lambda: SimpleNamespace(
                  count=lambda: next(count for path, count in ns['_DEMO_SOURCES'].values() if path == file), unpersist=lambda: None)),
              write_lakehouse_table=lambda *a, **kw: None, write_warehouse_table=lambda *a, **kw: None,
              read_warehouse_table=lambda **kw: object())
    ns['read_lakehouse_table'] = lambda *a, **kw: original_read(*a, **kw) if a else object()
    removed = []
    def delta(spark, path):
        def delete():
            removed.append(path); rows[path].clear()
        return SimpleNamespace(delete=delete, history=lambda _: SimpleNamespace(
            first=lambda: {'operationMetrics': {'numDeletedRows': 1}}))
    ns['DeltaTable'] = SimpleNamespace(forPath=delta)
    return ns, rows, removed


def test_true_clears_all_tables_children_first_and_repeated_reset_is_safe(capsys):
    ns, rows, removed = _ready_namespace()
    for table in rows: rows[table] = [{'table_id': 'orders'}]
    _run_reset(ns)
    assert not any(rows.values())
    assert set(removed) == set(CANONICAL_METADATA_TABLES)
    assert removed.index('METADATA_DATA_PROFILED_FREQUENCY') < removed.index('METADATA_DATA_PROFILED')
    assert removed.index('METADATA_DATA_CONTRACT_ACTIVATION') < removed.index('METADATA_DATA_CONTRACT')
    _run_reset(ns)
    assert len(removed) == len(CANONICAL_METADATA_TABLES)
    output = capsys.readouterr().out
    assert output.count('RESET COMPLETE') == 2
    assert all(f'{table}: removed 0' in output for table in rows)


def test_fixture_failure_occurs_before_metadata_or_output_deletion():
    ns, rows, removed = _ready_namespace(); rows['METADATA_DATA_CATALOGUE'] = [{'table_id': 'orders'}]
    ns['read_lakehouse_csv'] = lambda *a, **kw: SimpleNamespace(cache=lambda: SimpleNamespace(count=lambda: -1))
    with pytest.raises(RuntimeError, match='Restore the fixture before resetting'):
        _run_reset(ns)
    assert not removed and rows['METADATA_DATA_CATALOGUE']


def test_incomplete_metadata_deletion_cannot_report_success(capsys):
    ns, rows, _ = _ready_namespace(); rows['METADATA_PROCESSING_STATE'] = [{'source_table_id': 'orders'}]
    ns['DeltaTable'] = SimpleNamespace(forPath=lambda *a: SimpleNamespace(delete=lambda: None,
        history=lambda _: SimpleNamespace(first=lambda: {'operationMetrics': {'numDeletedRows': 0}})))
    with pytest.raises(RuntimeError, match='Metadata reset incomplete'):
        _run_reset(ns)
    assert 'RESET COMPLETE' not in capsys.readouterr().out


def test_output_verification_failure_cannot_report_success(capsys):
    ns, _, _ = _ready_namespace()
    ns['_demo_verify_outputs'] = lambda: (_ for _ in ()).throw(RuntimeError('output remains'))
    with pytest.raises(RuntimeError, match='output remains'):
        _run_reset(ns)
    assert 'RESET COMPLETE' not in capsys.readouterr().out


def test_guided_demo_puts_the_single_boolean_reset_before_io_examples():
    page = (ROOT / 'docs/guided-demo/00C-prepare-demo-data-with-fabricops-io.md').read_text()
    assert page.index('## Reset, rerun and validate a package') < page.index('## Read the same Orders')
    assert 'RESET_DEMO = False' in page and 'RESET COMPLETE' in page
    assert 'RESET_CONFIRMATION' not in page and 'EXTRA_DEMO_NOTEBOOK_IDS' not in page
    assert 'all rows in the 14 metadata tables' in page
    assert 'saved submissions' in page and 'manually created' in page
