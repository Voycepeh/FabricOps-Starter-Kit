"""Exercise the actual notebook-local demo ownership and reset cells."""
# ruff: noqa: D103
import ast
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import nbformat
import pytest

from fabricops_kit.config.metadata_schemas import CANONICAL_METADATA_TABLES

ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = ROOT / 'templates/DemoData/00C_demo_setup.ipynb'
CELLS = {cell.id: cell.source for cell in nbformat.read(NOTEBOOK, as_version=4).cells}


def _helpers():
    """Load notebook logic without importing unavailable Fabric/Delta boundaries."""
    tree = ast.parse(CELLS['reset-private-helpers'])
    tree.body = [node for node in tree.body if not isinstance(node, (ast.Import, ast.ImportFrom))
                 or (isinstance(node, ast.Import) and node.names[0].name == 'json')
                 or (isinstance(node, ast.ImportFrom) and node.module == 'collections')]
    namespace = {}
    exec(compile(tree, str(NOTEBOOK), 'exec'), namespace)
    return namespace


def _history():
    """Every disposable table has demo rows, unrelated rows, and identical IDs in another workspace."""
    rows = {table: [] for table in CANONICAL_METADATA_TABLES}
    rows['METADATA_PIPELINE_RUN'] = [dict(run_id='run', workspace_id='dev', pipeline_id='notebook',
        execution_mode='ungoverned', completed_at='yesterday', profiling='[]', operations='[{"table_id":"source"},{"table_id":"target"}]')]
    for table in _helpers()['_DEMO_DELETE_ORDER']:
        if table == 'METADATA_PIPELINE_RUN':
            continue
        row = dict(workspace_id='dev', table_id='target', _notebook_id='notebook')
        if table == 'METADATA_PROCESSING_STATE':
            row = dict(workspace_id='dev', source_table_id='source', target_table_id='target',
                       pipeline_id='notebook', run_id='run', record_id='receipt', publication_id='publication',
                       record_type='publication_receipt', _notebook_id='notebook')
        if table in {'METADATA_DATA_PROFILED', 'METADATA_DATA_PROFILED_FREQUENCY'}:
            row.update(profile_id='profile', profile_snapshot_id='snapshot')
        if table == 'METADATA_GUARDRAIL_RESULTS':
            row['run_id'] = 'run'
        rows[table] = [row]
    for table, records in rows.items():
        if not records:
            records.append(dict(shared='immutable-governance-record'))
        else:
            records.extend([{**records[0], 'workspace_id': 'other-workspace'},
                            dict(workspace_id='dev', table_id='unrelated', _notebook_id='other',
                                 **({'operations': '[]', 'profiling': '[]', 'run_id': 'other-run', 'pipeline_id': 'other'}
                                    if table == 'METADATA_PIPELINE_RUN' else {}))])
    return rows


def _scope(ns, rows, **kwargs):
    return ns['_demo_scope'](rows, 'dev', {'source', 'target'}, {'notebook'}, {'physical'}, **kwargs)


def test_complete_inventory_and_repeat_reset_preserves_unrelated_records():
    ns, rows = _helpers(), _history()
    plan = _scope(ns, rows)
    assert set(plan) == set(CANONICAL_METADATA_TABLES)
    for table, selected in plan.items():
        assert len(selected) == (1 if table in ns['_DEMO_DELETE_ORDER'] else 0)
    retained = {table: [r for r in records if r not in plan[table]] for table, records in rows.items()}
    assert not any(_scope(ns, retained).values())
    assert sum(map(len, retained.values())) == sum(map(len, rows.values())) - 8
    # An interrupted cleanup resumes independently of which earlier children are absent.
    for removed_table in ns['_DEMO_DELETE_ORDER']:
        partial = deepcopy(rows)
        partial[removed_table] = [r for r in partial[removed_table] if r not in plan[removed_table]]
        resumed = _scope(ns, partial)
        assert not resumed[removed_table]
        assert sum(map(len, resumed.values())) == 7


@pytest.mark.parametrize('kind', ['source_observation', 'incremental_checkpoint', 'drift_baseline',
                                  'full_source_baseline', 'publication_receipt'])
def test_every_processing_state_type_is_removed(kind):
    ns, rows = _helpers(), _history()
    rows['METADATA_PROCESSING_STATE'][0]['record_type'] = kind
    assert _scope(ns, rows)['METADATA_PROCESSING_STATE'][0]['record_type'] == kind


@pytest.mark.parametrize('table,row', [
    ('METADATA_DATA_CONTRACT', dict(evidence_workspace_id='dev', table_id='source')),
    ('METADATA_DATA_CONTRACT_ACTIVATION', dict(workspace_id='physical', table_id='target')),
    ('METADATA_PIPELINE_REGISTRY', dict(execution_workspace_id='dev', pipeline_id='notebook')),
    ('METADATA_PIPELINE_ACTIVATION', dict(execution_workspace_id='dev', pipeline_id='notebook')),
])
def test_governance_and_immutable_history_block_without_modification(table, row):
    ns, rows = _helpers(), _history()
    rows[table].append(row)
    before = deepcopy(rows)
    with pytest.raises(RuntimeError, match='history|preserved'):
        _scope(ns, rows)
    assert rows == before


@pytest.mark.parametrize('change,error', [
    ({'pipeline_id': 'another-pipeline'}, 'ambiguous'),
    ({'operations': '[{"table_id":"target"},{"table_id":"unrelated"}]'}, 'ambiguous'),
    ({'operations': 'null'}, 'Invalid operations'),
    ({'execution_mode': 'governed'}, 'Governed'),
    ({'completed_at': None}, 'may still be active'),
])
def test_ambiguous_or_active_runs_block(change, error):
    ns, rows = _helpers(), _history()
    rows['METADATA_PIPELINE_RUN'][0].update(change)
    with pytest.raises(RuntimeError, match=error):
        _scope(ns, rows)


def test_confirmed_terminated_incomplete_run_can_be_reset():
    ns, rows = _helpers(), _history()
    rows['METADATA_PIPELINE_RUN'][0]['completed_at'] = None
    assert len(_scope(ns, rows, stopped_runs={'run'})['METADATA_PIPELINE_RUN']) == 1


@pytest.mark.parametrize('table,change', [
    ('METADATA_PROCESSING_STATE', {'target_table_id': 'unrelated'}),
    ('METADATA_PROCESSING_STATE', {'pipeline_id': 'unrelated'}),
    ('METADATA_DATA_LINEAGE', {'_notebook_id': 'unrelated'}),
    ('METADATA_DATA_CATALOGUE', {'_notebook_id': 'unrelated'}),
    ('METADATA_DATA_PROFILED', {'_notebook_id': 'unrelated'}),
    ('METADATA_DATA_ACCESS', {'_notebook_id': 'unrelated'}),
])
def test_shared_asset_ownership_blocks(table, change):
    ns, rows = _helpers(), _history()
    rows[table][0].update(change)
    with pytest.raises(RuntimeError, match='unrelated|another|unknown'):
        _scope(ns, rows)


@pytest.mark.parametrize('child,fields', [
    ('METADATA_DATA_PROFILED_FREQUENCY', {'profile_id': 'profile', 'profile_snapshot_id': 'snapshot'}),
    ('METADATA_PROCESSING_STATE', {'publication_id': 'publication'}),
    ('METADATA_GUARDRAIL_RESULTS', {'run_id': 'run'}),
])
def test_retained_child_cannot_reference_removed_demo_parent(child, fields):
    ns, rows = _helpers(), _history()
    rows[child].append(dict(workspace_id='dev', table_id='unrelated', **fields))
    with pytest.raises(RuntimeError, match='links demo|references demo'):
        _scope(ns, rows)


def test_apply_requires_confirmation_and_propagates_partial_failure():
    ns, rows = _helpers(), _history()
    original = deepcopy(rows)
    selected = _scope(ns, rows)
    actions = []
    def remove(table, selected_rows):
        if table == 'METADATA_DATA_PROFILED':
            raise OSError('injected storage failure')
        actions.append(table)
        rows[table] = [r for r in rows[table] if r not in selected_rows]
    ns.update(_demo_before=deepcopy(rows), _demo_metadata_rows=lambda: deepcopy(rows),
              _demo_selected=selected, _demo_check_jobs=lambda: None, _demo_delete_rows=remove,
              _demo_remove_outputs=lambda: actions.append('outputs'), DEMO_EXECUTIONS_STOPPED=True,
              RESET_CONFIRMATION='cancel')
    with pytest.raises(RuntimeError, match='cancelled'):
        exec(CELLS['reset-apply'], ns)
    assert rows == original and not actions
    ns['RESET_CONFIRMATION'] = 'RESET DEMO'
    with pytest.raises(RuntimeError, match='incomplete while cleaning METADATA_DATA_PROFILED') as error:
        exec(CELLS['reset-apply'], ns)
    assert isinstance(error.value.__cause__, OSError)
    assert not ns['_demo_confirmed']
    assert actions == ['METADATA_GUARDRAIL_RESULTS', 'METADATA_PROCESSING_STATE', 'METADATA_DATA_PROFILED_FREQUENCY']
    assert rows['METADATA_PIPELINE_RUN'] == original['METADATA_PIPELINE_RUN']
    resumed = _scope(ns, rows)
    assert not resumed['METADATA_PROCESSING_STATE'] and resumed['METADATA_PIPELINE_RUN']


def test_apply_rechecks_concurrent_changes_and_stopped_executions():
    ns, rows = _helpers(), _history()
    ns.update(_demo_before=deepcopy(rows), _demo_metadata_rows=lambda: deepcopy(rows),
              _demo_check_jobs=lambda: None, RESET_CONFIRMATION='RESET DEMO', DEMO_EXECUTIONS_STOPPED=False)
    with pytest.raises(RuntimeError, match='Stop all'):
        exec(CELLS['reset-apply'], ns)
    ns['DEMO_EXECUTIONS_STOPPED'] = True
    ns['RESET_CONFIRMATION'] = 'RESET DEMO'
    rows['METADATA_DATA_STEWARD'].append({'shared': 'new'})
    with pytest.raises(RuntimeError, match='changed since preview'):
        exec(CELLS['reset-apply'], ns)
    assert not ns['_demo_confirmed']


def test_missing_metadata_is_never_silently_skipped():
    ns = _helpers()
    ns.update(_demo_config=object(), metadata_table_schema_registry=lambda: {'missing': None},
              metadata_table_physical_schema=lambda *_: 'configured-engineering')
    def missing(*args, **kwargs):
        assert kwargs == {'store': 'Metadata', 'schema': 'configured-engineering'}
        raise RuntimeError('missing table or access denied')
    ns['read_lakehouse_table'] = missing
    with pytest.raises(RuntimeError, match='Check the Metadata mapping'):
        ns['_demo_metadata_rows']()


def test_verification_requires_exact_metadata_preservation(capsys):
    ns, rows = _helpers(), _history()
    selected = _scope(ns, rows)
    remaining = {t: [r for r in records if r not in selected[t]] for t, records in rows.items()}
    ns.update(_demo_confirmed=True, _demo_day1={}, _demo_verify_outputs=lambda: None,
              _demo_check_jobs=lambda: None, _demo_metadata_rows=lambda: remaining,
              _demo_before=rows, _demo_selected=selected, _demo_table_ids={'source', 'target'},
              _demo_notebook_ids={'notebook'}, _demo_physical_workspaces={'physical'}, _demo_bindings=None, STOPPED_DEMO_RUN_IDS=[],
              context=SimpleNamespace(workspace_id='dev'))
    remaining['METADATA_DATA_STEWARD'].clear()
    with pytest.raises(RuntimeError, match='changed unexpectedly'):
        exec(CELLS['reset-verify'], ns)
    assert 'RESET COMPLETE' not in capsys.readouterr().out
    remaining['METADATA_DATA_STEWARD'] = rows['METADATA_DATA_STEWARD']
    exec(CELLS['reset-verify'], ns)
    assert 'RESET COMPLETE' in capsys.readouterr().out
    assert not ns['_demo_confirmed']


def test_notebook_validity_and_scope_stay_demo_local():
    nbformat.validate(nbformat.read(NOTEBOOK, as_version=4))
    for cell in nbformat.read(NOTEBOOK, as_version=4).cells:
        if cell.cell_type == 'code':
            tree = ast.parse(cell.source)
            assert all(node.name.startswith('_demo_') for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
    assert 'RESET COMPLETE' in CELLS['reset-verify']
    assert "print('RESET COMPLETE')" not in CELLS['reset-apply']
    assert 'METADATA_PIPELINE_RUN' == _helpers()['_DEMO_DELETE_ORDER'][-1]


@pytest.mark.parametrize('table,payload_field', [('METADATA_PIPELINE_REGISTRY', 'operations_json'),
                                              ('METADATA_PIPELINE_ACTIVATION', 'package_json')])
def test_other_governed_pipeline_using_exact_demo_tables_blocks(table, payload_field):
    ns, rows = _helpers(), _history()
    rows[table].append(dict(execution_workspace_id='dev', pipeline_id='another-notebook',
                           **{payload_field: '{"manifest":{"operations":[{"table_id":"source"}]}}'}))
    with pytest.raises(RuntimeError, match='immutable'):
        _scope(ns, rows)


def test_changed_physical_bindings_are_not_treated_as_current_demo_history():
    ns, rows = _helpers(), _history()
    with pytest.raises(RuntimeError, match='different physical store mappings'):
        _scope(ns, rows, bindings={'source': {'item_id': 'new-source'}, 'target': {'item_id': 'new-target'}})


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


def test_guided_demo_includes_complete_reset_and_daily_regression_workflow():
    page = (ROOT / 'docs/guided-demo/00C-prepare-demo-data-with-fabricops-io.md').read_text()
    assert all(table in page for table in CANONICAL_METADATA_TABLES)
    for phrase in ('RESET COMPLETE', 'RESET DEMO', 'DEMO_EXECUTIONS_STOPPED', 'STOPPED_DEMO_RUN_IDS',
                   'EXTRA_DEMO_NOTEBOOK_IDS', 'DEMO_DAY = 1', 'DEMO_DAY = 2', 'DEMO_DAY = 3',
                   'publication_id', 'profile_snapshot_id', 'dedicated demo environment'):
        assert phrase in page
    for name in ('00B-configure-environment-and-load-assets.md', '02A-full-refresh-demo.md',
                 '02B-build-and-run-incremental-append-etl.md', '02C-build-and-run-scd-etl.md'):
        assert '00C-prepare-demo-data-with-fabricops-io.md' in (ROOT / 'docs/guided-demo' / name).read_text()


def test_retained_pipeline_profiling_demo_tables_is_an_ownership_conflict():
    ns, rows = _helpers(), _history()
    rows['METADATA_PIPELINE_RUN'].append(dict(workspace_id='dev', pipeline_id='other', operations='[]',
                                            run_id='other-profile-run', profiling='[{"table_id":"source"}]'))
    with pytest.raises(RuntimeError, match='ambiguous'):
        _scope(ns, rows)


def test_unknown_processing_state_type_requires_ownership_review():
    ns, rows = _helpers(), _history()
    rows['METADATA_PROCESSING_STATE'][0]['record_type'] = 'future-state'
    with pytest.raises(RuntimeError, match='Unknown demo Processing State'):
        _scope(ns, rows)


def test_catalogue_writer_ownership_survives_later_demo_profiling():
    ns, rows = _helpers(), _history()
    rows['METADATA_DATA_CATALOGUE'][0].update(writer_notebook_id='other-writer', writer_workspace_id='dev')
    with pytest.raises(RuntimeError, match='another writer owner'):
        _scope(ns, rows)
