"""Exercise the demo's isolated, read-only metadata boundary and physical reset cells."""
# ruff: noqa: D103
import ast
from pathlib import Path
from types import SimpleNamespace

import nbformat
import pytest

from fabricops_kit.config.metadata_schemas import CANONICAL_METADATA_TABLES, metadata_table_schema_registry

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / 'templates/DemoData/00C_demo_setup.ipynb'
CELLS = {cell.id: cell.source for cell in nbformat.read(NOTEBOOK, as_version=4).cells}
METADATA_ID = '11111111-1111-4111-8111-111111111111'


def _helpers():
    """Load actual notebook logic, leaving only Fabric transport boundaries for tests to supply."""
    tree = ast.parse(CELLS['reset-private-helpers'])
    tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))
                 or (isinstance(node, ast.Import) and node.names[0].name == 'json')
                 or (isinstance(node, ast.ImportFrom) and node.module in {'uuid', 'urllib.error'})]
    namespace = dict(_demo_extra_notebook_ids=set(), _demo_listed_notebook_ids=set(),
                     _demo_notebook_ids={'notebook'}, context=SimpleNamespace(workspace_id='dev'))
    exec(compile(tree, str(NOTEBOOK), 'exec'), namespace)
    return namespace


def _empty():
    return dict.fromkeys(CANONICAL_METADATA_TABLES, 0)


def _preview_namespace():
    ns = _helpers()
    metadata = SimpleNamespace(kind='lakehouse', schema_enabled=True, workspace_id='governance', item_id=METADATA_ID)
    stores = {key: SimpleNamespace(kind='warehouse' if key == 'Gold' else 'lakehouse', schema_enabled=True,
              workspace_id='dev', item_id=key.lower()) for key in ('Bronze', 'Silver', 'Gold')}
    stores['Metadata'] = metadata
    config = SimpleNamespace(path_config=SimpleNamespace(paths={'dev': stores, 'governance': {'Metadata': metadata}}))
    context = SimpleNamespace(workspace_id='dev', readiness_status='ready', paths=stores)
    def request(method, path):
        if path.endswith('/notebooks'):
            return {'value': [{'id': str(index), 'displayName': name} for index, name in enumerate(ns['_DEMO_NAMES'])]}
        return {'displayName': 'configured'}
    ns.update(context=context, resolve_fabric_context=lambda: (config, 'dev', {}),
              EXTRA_DEMO_NOTEBOOK_IDS=[], FabricNotebookClient=lambda: SimpleNamespace(request=request),
              _demo_check_jobs=lambda: None, _demo_metadata_counts=_empty)
    return ns


def test_preview_is_read_only_and_checks_all_installed_metadata_tables():
    ns, counts, reads = _helpers(), _empty(), []
    registry = metadata_table_schema_registry()
    def read(table, **kwargs):
        reads.append((table, kwargs))
        return SimpleNamespace(schema=registry[table], count=lambda: counts[table])
    ns.update(_demo_config=object(), metadata_table_schema_registry=metadata_table_schema_registry,
              metadata_table_physical_schema=lambda *_: 'configured-schema', read_lakehouse_table=read)
    assert ns['_demo_metadata_counts']() == counts
    ns['_demo_require_empty_metadata'](counts)
    assert {t for t, _ in reads} == set(CANONICAL_METADATA_TABLES)
    assert all(kw == {'store': 'Metadata', 'schema': 'configured-schema'} for _, kw in reads)
    assert '_demo_delete_rows' not in ns and '_demo_scope' not in ns


@pytest.mark.parametrize('table', CANONICAL_METADATA_TABLES)
def test_any_existing_metadata_blocks_the_fresh_lifecycle_without_deletion(table):
    ns, counts = _helpers(), _empty()
    counts[table] = 1
    with pytest.raises(RuntimeError, match='create a fresh dedicated demo Metadata Lakehouse'):
        ns['_demo_require_empty_metadata'](counts)
    assert counts[table] == 1


def test_preview_uses_selected_metadata_and_rejects_business_store_alias():
    ns = _preview_namespace()
    ns['context'].paths['Bronze'] = ns['context'].paths['Metadata']
    with pytest.raises(RuntimeError, match='separate from the business stores'):
        exec(CELLS['reset-preview'], ns)


def test_nonempty_selected_metadata_blocks_before_jobs_or_business_io():
    ns, calls = _preview_namespace(), []
    counts = _empty(); counts['METADATA_DATA_CONTRACT'] = 1
    def unexpected():
        calls.append('fabric notebook API')
        raise AssertionError('No further preparation should start')
    ns.update(_demo_metadata_counts=lambda: counts, FabricNotebookClient=unexpected)
    with pytest.raises(RuntimeError, match='No business reset is permitted'):
        exec(CELLS['reset-preview'], ns)
    assert not calls and not ns['_demo_confirmed']


@pytest.mark.parametrize('table,field,wrong_type', [
    ('METADATA_DATA_CATALOGUE', 'load_strategy_parameters_json', 'struct<watermark_column:string>'),
    ('METADATA_PIPELINE_RUN', 'operations', 'array<struct<table_id:string>>'),
    ('METADATA_PROCESSING_STATE', 'row_count', 'string'),
])
def test_schema_migration_must_precede_business_reset(table, field, wrong_type):
    ns = _helpers(); expected = metadata_table_schema_registry()[table]
    physical = [SimpleNamespace(name=f.name, dataType=f.dataType) for f in expected]
    next(f for f in physical if f.name == field).dataType = SimpleNamespace(simpleString=lambda: wrong_type)
    ns.update(_demo_config=object(), metadata_table_schema_registry=lambda: {table: expected},
              metadata_table_physical_schema=lambda *_: 'engineering',
              read_lakehouse_table=lambda *a, **kw: SimpleNamespace(schema=physical, count=lambda: 0))
    with pytest.raises(RuntimeError, match='missing columns or incompatible types'):
        ns['_demo_metadata_counts']()


def test_missing_metadata_is_a_setup_error_without_business_changes():
    ns = _helpers()
    def missing(*args, **kwargs):
        raise PermissionError('missing or inaccessible')
    ns.update(_demo_config=object(), metadata_table_schema_registry=lambda: {'missing': None},
              metadata_table_physical_schema=lambda *_: 'configured', read_lakehouse_table=missing)
    with pytest.raises(RuntimeError, match='run metadata setup in 00B'):
        ns['_demo_metadata_counts']()


def test_apply_requires_confirmation_stopped_jobs_and_empty_metadata():
    ns, actions = _helpers(), []
    ns.update(RESET_CONFIRMATION='', DEMO_EXECUTIONS_STOPPED=True, _demo_check_jobs=lambda: None,
              _demo_metadata_counts=_empty, _demo_remove_outputs=lambda: actions.append('outputs'))
    with pytest.raises(RuntimeError, match='cancelled'):
        exec(CELLS['reset-apply'], ns)
    ns.update(RESET_CONFIRMATION='RESET DEMO', DEMO_EXECUTIONS_STOPPED=False)
    with pytest.raises(RuntimeError, match='Stop current and earlier'):
        exec(CELLS['reset-apply'], ns)
    counts = _empty(); counts['METADATA_DATA_CONTRACT_ACTIVATION'] = 1
    ns.update(RESET_CONFIRMATION='RESET DEMO', DEMO_EXECUTIONS_STOPPED=True, _demo_metadata_counts=lambda: counts)
    with pytest.raises(RuntimeError, match='No business reset is permitted'):
        exec(CELLS['reset-apply'], ns)
    assert not actions and not ns['_demo_confirmed']


def test_repeated_apply_and_partial_failure_preserve_metadata_and_revoke_confirmation():
    ns, actions = _helpers(), []
    def failure():
        actions.append('partial output removal')
        raise OSError('permission failure')
    ns.update(RESET_CONFIRMATION='RESET DEMO', DEMO_EXECUTIONS_STOPPED=True, _demo_check_jobs=lambda: None,
              _demo_metadata_counts=_empty, _demo_remove_outputs=failure)
    with pytest.raises(RuntimeError, match='business reset incomplete'):
        exec(CELLS['reset-apply'], ns)
    assert not ns['_demo_confirmed'] and ns['RESET_CONFIRMATION'] == ''
    ns['_demo_remove_outputs'] = lambda: actions.append('outputs missing is OK')
    for _ in range(2):
        ns['RESET_CONFIRMATION'] = 'RESET DEMO'
        exec(CELLS['reset-apply'], ns)
        assert ns['_demo_confirmed'] and ns['RESET_CONFIRMATION'] == ''
    assert actions == ['partial output removal', 'outputs missing is OK', 'outputs missing is OK']


def test_verification_requires_all_metadata_to_remain_empty(capsys):
    ns, counts = _helpers(), _empty()
    ns.update(_demo_confirmed=True, _demo_day1={}, _demo_verify_outputs=lambda: None,
              _demo_check_jobs=lambda: None, _demo_metadata_counts=lambda: counts)
    counts['METADATA_DATA_STEWARD'] = 1
    with pytest.raises(RuntimeError, match='No business reset is permitted'):
        exec(CELLS['reset-verify'], ns)
    assert 'RESET COMPLETE' not in capsys.readouterr().out
    counts['METADATA_DATA_STEWARD'] = 0
    exec(CELLS['reset-verify'], ns)
    assert 'RESET COMPLETE' in capsys.readouterr().out
    assert not ns['_demo_confirmed']


@pytest.mark.parametrize('status', ['NotStarted', 'InProgress', 'Unknown'])
def test_fabric_nonterminal_job_blocks_reset(status):
    ns = _helpers()
    ns.update(_demo_notebook_ids={'notebook'}, context=SimpleNamespace(workspace_id='dev'),
              _demo_client=SimpleNamespace(request=lambda *_: {'value': [{'status': status}]}))
    with pytest.raises(RuntimeError, match='non-terminal Fabric job'):
        ns['_demo_check_jobs']()


def test_job_pagination_checks_all_active_instances():
    ns, calls = _helpers(), []
    def request(method, path):
        calls.append(path)
        return {'value': [{'status': 'Completed'}], 'continuationUri': 'next-page'} if len(calls) == 1 else {
            'value': [{'status': 'InProgress'}]}
    ns.update(_demo_notebook_ids={'notebook'}, context=SimpleNamespace(workspace_id='dev'),
              _demo_client=SimpleNamespace(request=request))
    with pytest.raises(RuntimeError, match='non-terminal'):
        ns['_demo_check_jobs']()
    assert calls[-1] == 'next-page'


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
    ns['_demo_remove_outputs']()
    ns['_demo_remove_outputs']()
    ns['_demo_verify_outputs']()
    assert existing == {'/configured/Silver/demo/unrelated'}
    assert not catalog and len(warehouse) == 2
    assert all('DROP TABLE [demo].[customer_summary]' in call[0][2] for call in warehouse)
    assert all(call[1]['database_name'] == 'physical-gold' for call in warehouse)
    assert sum(q.startswith('DROP TABLE') for q in sql) == (5 if initially_present else 0)


def test_verified_deleted_retired_id_is_not_queried_for_live_jobs():
    import io
    from urllib.error import HTTPError
    ns, calls = _helpers(), []
    def request(method, path):
        calls.append(path)
        if path.endswith('/retired'):
            raise HTTPError(path, 404, 'Not Found', {}, io.BytesIO(b'{"errorCode":"ItemNotFound"}'))
        return {'value': [{'status': 'Completed'}]}
    ns.update(_demo_notebook_ids={'notebook', 'retired'}, _demo_extra_notebook_ids={'retired'},
              _demo_listed_notebook_ids={'notebook'}, _demo_client=SimpleNamespace(request=request))
    ns['_demo_check_jobs']()
    assert '/workspaces/dev/items/notebook/jobs/instances' in calls
    assert '/workspaces/dev/items/retired' in calls
    assert '/workspaces/dev/items/retired/jobs/instances' not in calls


@pytest.mark.parametrize('status,payload', [
    (403, b'{"errorCode":"InsufficientPrivileges"}'),
    (500, b'{"errorCode":"InternalError"}'),
    (404, b'{"errorCode":"UnknownEndpoint"}'),
    (404, b'not-json'),
])
def test_retired_id_permissions_and_unconfirmed_absence_fail_closed(status, payload):
    import io
    from urllib.error import HTTPError
    ns = _helpers()
    def request(method, path):
        raise HTTPError(path, status, 'unavailable', {}, io.BytesIO(payload))
    ns.update(_demo_notebook_ids={'retired'}, _demo_extra_notebook_ids={'retired'},
              _demo_client=SimpleNamespace(request=request))
    with pytest.raises(RuntimeError, match='Check workspace/item permissions and Fabric availability'):
        ns['_demo_check_jobs']()


def test_retired_notebook_that_still_exists_must_pass_live_job_checks():
    ns = _helpers()
    def request(method, path):
        return {'id': 'retired'} if not path.endswith('/jobs/instances') else {'value': [{'status': 'InProgress'}]}
    ns.update(_demo_notebook_ids={'retired'}, _demo_extra_notebook_ids={'retired'},
              _demo_client=SimpleNamespace(request=request))
    with pytest.raises(RuntimeError, match='non-terminal'):
        ns['_demo_check_jobs']()



def test_notebook_is_valid_private_and_has_no_metadata_deletion_path():
    notebook = nbformat.read(NOTEBOOK, as_version=4); nbformat.validate(notebook)
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            tree = ast.parse(cell.source); compile(tree, str(NOTEBOOK), 'exec')
            assert all(node.name.startswith('_demo_') for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
    assert 'whenMatchedDelete' not in CELLS['reset-private-helpers']
    assert 'TRUNCATE' not in CELLS['reset-private-helpers']
    assert "print('RESET COMPLETE')" in CELLS['reset-verify']


def test_demo_file_paths_are_lowercase_and_repository_asset_paths_stay_valid():
    for path in (ROOT / 'templates/DemoData').glob('*.ipynb'):
        notebook = nbformat.read(path, as_version=4)
        assert 'Demo/' not in path.read_text()
        for cell in notebook.cells:
            if cell.cell_type == 'code':
                compile(cell.source, str(path), 'exec')
    ns = _helpers()
    assert all(file.startswith('demo/') for file, count in ns['_DEMO_SOURCES'].values())
    for path in [ROOT / 'docs/guided-demo.md', *(ROOT / 'docs/guided-demo').glob('*.md')]:
        assert 'Files/Demo' not in path.read_text()
        assert 'subfolder named `Demo`' not in path.read_text()


def test_guided_demo_documents_isolated_metadata_and_the_full_restart():
    page = (ROOT / 'docs/guided-demo/00C-prepare-demo-data-with-fabricops-io.md').read_text()
    assert all(table in page for table in CANONICAL_METADATA_TABLES)
    for phrase in ('dedicated Metadata Lakehouse', 'Metadata item selected by `00_env_config`', 'removed 0; remaining 0',
                   'previous lakehouse', 'before Step 1', 'never deletes', 'Files/demo'):
        assert phrase in page
    setup = (ROOT / 'docs/guided-demo/00A-prepare-fabric-artifacts.md').read_text()
    config = (ROOT / 'docs/guided-demo/00B-configure-environment-and-load-assets.md').read_text()
    assert 'Lakehouse named **demo_metadata**' in setup
    assert 'GOVERNANCE_METADATA_LAKEHOUSE_NAME = "demo_metadata"' in config
    assert 'create' in config and 'yourself in Fabric' in config
    assert 'INITIALIZE_METADATA = True' in config
    assert 'Step 1' in config and 'fresh' in config
