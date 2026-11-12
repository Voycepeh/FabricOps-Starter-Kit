"""Unified Read lifecycle exercises real sessions with isolated Fabric boundaries."""
# ruff: noqa: D103
import importlib
import json
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fabricops_kit import orchestrate_read, orchestrate_write, setup_pipeline, finalize_pipeline
from fabricops_kit.pipeline import shared
from fabricops_kit.data_contract.shared import file_source_identity
from tests.unit.test_pipeline_session import runtime  # noqa: F401, F811


@pytest.fixture
def files(runtime, monkeypatch):  # noqa: F811
    io = importlib.import_module('fabricops_kit.io')
    routing = importlib.import_module('fabricops_kit.io.shared')
    configured = SimpleNamespace(workspace_id='physical-workspace', item_id='physical-item', kind='lakehouse')
    monkeypatch.setattr(routing, 'resolve_configured_file_path', lambda store, path, **kw:
        (configured, path, 'abfss://physical-workspace/physical-item/Files/' + path))
    monkeypatch.setattr(shared, 'get_store', lambda *a, **kw: configured)
    # Reuse real binding capture for files and preserve the table test fixture's bindings.
    original = shared.pipeline_physical_bindings
    real = __import__('tests.unit.test_pipeline_session', fromlist=['PHYSICAL_BINDINGS']).PHYSICAL_BINDINGS
    monkeypatch.setattr(shared, 'pipeline_physical_bindings', lambda identities, **kw:
        {**original({k: v for k, v in identities.items() if v.get('source_type') != 'file'}, **kw),
         **real({k: v for k, v in identities.items() if v.get('source_type') == 'file'}, **kw)})
    readers = {}
    for fmt in ('csv', 'json', 'parquet', 'excel'):
        reader = Mock(return_value=runtime.frame, __name__='read_lakehouse_' + fmt)
        monkeypatch.setattr(io, 'read_lakehouse_' + fmt, reader)
        readers[fmt] = reader
    monkeypatch.setattr(runtime.read, 'schedule_file_profiling', lambda *a, **kw:
        {'status': 'completed', 'row_count': 2, 'results_persisted': False})
    return SimpleNamespace(runtime=runtime, readers=readers, configured=configured)


@pytest.mark.parametrize('fmt', ['csv', 'json', 'parquet', 'excel'])
def test_formats_participate_in_read_write_and_finalize(files, fmt):
    session = setup_pipeline(pipeline_mode='Dry Run')
    options = {'sheet_name': 'Orders'} if fmt == 'excel' else {'mode': 'FAILFAST'}
    result = orchestrate_read(store='Bronze', relative_path='demo/orders.' + fmt,
                              file_format=fmt, read_options=options)
    assert result['dataframe'] is files.runtime.frame
    assert result['source_type'] == 'file' and result['source_id'].startswith('file:')
    assert 'table_id' not in result and result['execution_plan_id'] == session.plan.plan_id
    assert [stage['stage'] for stage in result['orchestration_stages']] == ['Read', 'Profile']
    call = files.readers[fmt].call_args
    assert call.kwargs['context']['_spark_session'] is files.runtime.spark
    assert call.kwargs['store'] == 'Bronze'
    assert all(call.kwargs[key] == value for key, value in options.items())
    assert result['source_location']['workspace_id'] == 'physical-workspace'
    write = orchestrate_write(result['dataframe'], store='Gold', schema='demo', table_name='summary', write_mode='overwrite')
    assert write['source_ids'] == [result['source_id']]
    assert write['source_association'] == 'pipeline_participation'
    assert files.runtime.publication.call_args.kwargs['source_table_ids'] == []
    run = finalize_pipeline(session)
    assert run['status'] == 'dry_run_completed'
    source = next(op for op in run['operations'] if op['pipeline_role'] == 'source')
    target = next(op for op in run['operations'] if op['pipeline_role'] == 'target')
    assert source['source_id'] == result['source_id'] and source['table_id'] is None
    assert target['source_ids'] == [result['source_id']] and target['source_table_ids'] == []
    shared.validate_pipeline_run(run)


@pytest.mark.parametrize('changes', [
    {'table_name': 'orders'}, {'schema': 'demo'}, {'query': 'select 1'},
    {'relative_path': None}, {'file_format': None}, {'file_format': 'xml'},
    {'relative_path': '../escape'}, {'relative_path': '/absolute'}, {'relative_path': 'a/../../b'},
    {'relative_path': 'abfss://elsewhere'}, {'read_mode': 'incremental'},
    {'relative_path': '{../outside.csv,safe/*.csv}'}, {'relative_path': '{../,safe/}*.csv'},
    {'read_options': {'path': 'another.csv'}}, {'read_options': {'context': {}}},
    {'read_options': []},
])
def test_invalid_file_declarations_fail_closed(files, changes):
    session = setup_pipeline(pipeline_mode='Dry Run')
    args = dict(store='Bronze', relative_path='demo/orders.csv', file_format='csv')
    args.update(changes)
    with pytest.raises((ValueError, TypeError)):
        orchestrate_read(**args)
    assert session.closed
    for reader in files.readers.values():
        reader.assert_not_called()


def test_file_failure_records_failed_operation_and_closes_session(files):
    session = setup_pipeline(pipeline_mode='Dry Run')
    files.readers['csv'].side_effect = OSError('unreadable file')
    with pytest.raises(RuntimeError, match='unreadable file'):
        orchestrate_read(store='Bronze', relative_path='demo/orders.csv', file_format='csv')
    assert session.closed and session.plan.run_result['status'] == 'failed'
    assert next(iter(session.plan.evidence['operations'].values()))['status'] == 'failed'


def test_frozen_file_contract_compares_reader_options(files, monkeypatch):
    session = setup_pipeline(pipeline_mode='Dry Run')
    descriptor = file_source_identity(workspace_id='physical-workspace', item_id='physical-item',
        relative_path='demo/orders.csv', file_format='csv', reader_options={'header': True})
    payload = {'source': descriptor, 'table': {'columns': []}, 'enrichment': {'table': [], 'columns': []}, 'guardrails': []}
    contract = {'source_id': descriptor['source_id'], 'table_id': None, 'contract_id': 'orders-file', 'contract_version': 1,
        'status': 'frozen', 'contract_payload': payload, 'contract_payload_json': json.dumps(payload)}
    monkeypatch.setattr(shared, 'resolve_data_contract_version', lambda *a, **kw: contract)
    session.select_contract(descriptor['source_id'], 'orders-file', 1)
    with pytest.raises(ValueError, match='reader options differ'):
        orchestrate_read(store='Bronze', relative_path='demo/orders.csv', file_format='csv', read_options={'header': False})
    files.readers['csv'].assert_not_called()


def test_approved_file_boundary_binds_exact_plan_and_options():
    from fabricops_kit.activated_pipeline import shared as activation
    source = file_source_identity(workspace_id='w', item_id='i', relative_path='demo/orders.csv', file_format='csv', reader_options={'header': True})
    content = json.dumps({'source': source})
    binding = {**{k: v for k, v in source.items() if k != 'reader_options'}, 'reader_options_json': json.dumps(source['reader_options'])}
    contract = {'contract_id': 'c', 'contract_version': 1, 'contract_payload_json': content}
    package = {'contracts': {source['source_id']: contract}, 'manifest': {
        'operations': [{'source_type': 'file', 'source_id': source['source_id'], 'table_id': None,
            'destination': binding, 'pipeline_role': 'source', 'read_mode': 'full', 'operation_key': 'source:Bronze/Files/demo/orders.csv'}],
        'file_authorizations': [{'source': source, 'store': 'Bronze', 'contract_id': 'c', 'contract_version': 1,
            'payload_sha256': activation.hashlib.sha256(content.encode()).hexdigest()}]}}
    activation.validate_file_execution_authorizations(package)
    for key, value in [('relative_path', 'demo/other.csv'), ('reader_options_json', '{"header":false}'), ('item_id', 'other')]:
        changed = deepcopy(package)
        changed['manifest']['operations'][0]['destination'][key] = value
        with pytest.raises(ValueError, match='exact approved pipeline plan'):
            activation.validate_file_execution_authorizations(changed)
    changed = deepcopy(package)
    changed['manifest']['file_authorizations'] = []
    with pytest.raises(RuntimeError, match='exact approved'):
        activation.validate_file_execution_authorizations(changed)
    assert activation.FABRIC_GOVERNED_VALIDATED is False


def test_csv_types_and_retail_transform_without_orders_table(files, monkeypatch, spark_session):
    from pathlib import Path
    from pyspark.sql import functions as F
    root = Path(__file__).resolve().parents[2] / 'templates/DemoData'
    csv_module = importlib.import_module('fabricops_kit.io.read_lakehouse_csv')
    io = importlib.import_module('fabricops_kit.io')
    monkeypatch.setattr(io, 'read_lakehouse_csv', csv_module.read_lakehouse_csv)
    monkeypatch.setattr(csv_module, 'get_spark_session', lambda **kw: spark_session)
    monkeypatch.setattr(csv_module, 'resolve_configured_file_path', lambda store, path, **kw:
                        (files.configured, path, str(root / Path(path).name)))
    session = setup_pipeline(pipeline_mode='Dry Run')
    notebook = json.loads((root / '02A_full_refresh_demo.ipynb').read_text())
    source_code = next(''.join(cell['source']) for cell in notebook['cells']
                       if cell['cell_type'] == 'code' and 'relative_path="demo/orders.csv"' in ''.join(cell['source']))
    ns = {'orchestrate_read': orchestrate_read, 'sources': {}, 'display': lambda frame: None, 'F': F}
    exec(compile(source_code, '02A-read-orders', 'exec'), ns)
    orders = ns['sources']['orders']['dataframe']
    types = dict(orders.dtypes)
    assert types['order_datetime'] == types['modified_datetime'] == 'timestamp'
    assert types['quantity'] == 'int' and types['unit_price'] == types['discount'] == 'double'
    for label, filename in [('products', 'products.csv'), ('history', 'order_history.csv')]:
        ns['sources'][label] = {'dataframe': spark_session.read.csv(str(root / filename), header=True, inferSchema=True)}
    transform = next(''.join(cell['source']) for cell in notebook['cells'] if cell.get('id') == 'transform')
    exec(compile(transform, '02A-transform', 'exec'), ns)
    assert ns['transformed_df'].count() == 120
    assert ns['customer_summary_df'].count() == 30
    total = ns['transformed_df'].agg(F.sum('order_net_amount')).first()[0]
    assert total == pytest.approx(28539.15)
    assert not any(identity.get('table_name') == 'orders' for identity in json.loads(session.plan.participants_json).values())
    finalize_pipeline(session)


def test_file_profile_respects_explicit_bound_and_stays_in_memory(files, spark_session):
    session = setup_pipeline(pipeline_mode='Dry Run', profiling_max_rows=2)
    context = {'execution_plan': session.plan}
    frame = spark_session.createDataFrame([(1,), (2,), (3,)], 'id int')
    presentations = []
    result = shared.schedule_file_profiling(frame, source_id='file:test', context=context, presentations=presentations)
    assert result['row_count'] == 2 and result['profiling_max_rows'] == 2
    assert result['profile_scope'] == 'bounded_selection' and result['results_persisted'] is False
    assert presentations and 'Bounded selection' in presentations[0]['title']
    assert shared.schedule_file_profiling(frame, source_id='file:test', context=context, presentations=[])['status'] == 'not_due'
    files.runtime.writes.assert_not_called()


def test_file_contract_shared_schema_dq_grain_and_metadata_freshness(files, spark_session, monkeypatch):
    from datetime import datetime, UTC
    from fabricops_kit.pipeline.check_schema import check_schema
    from fabricops_kit.pipeline.check_dq import check_dq
    from fabricops_kit.pipeline.check_freshness import check_freshness
    session = setup_pipeline(pipeline_mode='Dry Run')
    identity = shared.resolve_file_participant(store='Bronze', relative_path='demo/orders.csv', file_format='csv', context=session.plan.runtime_context)
    source_id = identity['source_id']
    columns = [{'column_id': name, 'column_name': name, 'data_type': typ} for name, typ in [('id', 'int'), ('modified', 'timestamp')]]
    payload = {'source': shared.file_participant_source(identity), 'table': {'columns': columns},
        'enrichment': {'table': [], 'columns': []}, 'guardrails': [
            {'guardrail_rule_id': 'grain', 'guardrail_type': 'grain', 'rule_type': 'uniqueness', 'action': 'Block',
             'rule_parameters': {'columns': ['id']}, 'is_active': True},
            {'guardrail_rule_id': 'fresh', 'guardrail_type': 'freshness', 'rule_type': 'freshness', 'action': 'Warn',
             'rule_parameters': {'evidence_method': 'metadata', 'evaluation_scope': 'full_dataset',
                                 'maximum_age': 2, 'maximum_age_unit': 'hours'}, 'is_active': True}]}
    contract = {'source_id': source_id, 'table_id': None, 'contract_id': 'c', 'contract_version': 1,
                'contract_payload_json': json.dumps(payload), 'contract_payload': payload}
    rules = shared.contract_guardrail_rows(contract, workspace_id='dev', table_id=source_id)
    # Same shared engines and result writer; only runtime/audit access is isolated.
    context = {'config': {}, 'scope_workspace_id': 'dev', '_spark_session': spark_session, 'execution_plan': session.plan,
        '_pipeline_identities': {source_id: identity}, '_pipeline_contracts': {source_id: contract}, '_pipeline_rules': {source_id: rules}}
    monkeypatch.setattr(shared, 'build_pipeline_audit_fields', lambda **kw: {'_activity_id': 'test'})
    monkeypatch.setattr(shared, 'get_current_audit_timestamp', lambda **kw: datetime.now(UTC))
    monkeypatch.setattr(importlib.import_module('fabricops_kit.pipeline.check_schema'), 'get_store', lambda *a: files.configured)
    freshness_module = importlib.import_module('fabricops_kit.pipeline.check_freshness')
    monkeypatch.setattr(freshness_module, 'build_runtime_audit_fields', lambda **kw: {'_activity_id': 'test'})
    def metadata_evidence(params, **kwargs):
        return {'evidence_method': 'metadata', 'evaluation_scope': 'full_dataset',
                'outcome': 'available', 'latest_value': datetime.now(UTC).isoformat(),
                'scan_required': False}
    monkeypatch.setattr(freshness_module, 'collect_freshness_evidence', metadata_evidence)
    monkeypatch.setattr(shared, 'load_table_guardrail_rules', lambda *a, **kw: rules)
    frame = spark_session.createDataFrame([(1, datetime.now(UTC)), (1, datetime.now(UTC))], 'id int, modified timestamp')
    schema = check_schema(frame, table_id=source_id, verbose=False, context=context)
    dq = check_dq(frame, table_id=source_id, verbose=False, context=context, diagnostics='none')
    fresh = check_freshness(source_id, dataframe=frame, verbose=False, context=context)
    assert schema['can_continue'] is True
    assert dq['can_continue'] is False and len(dq['checks']) == 1
    assert fresh['can_continue'] is True and fresh['evidence_outcome'] == 'available'
    assert session.plan.results and all(row.get('table_id') is None and row['source_id'] == source_id for row in session.plan.results)
    assert any(row['guardrail_type'] == 'data_quality' for row in session.plan.results)


def test_warehouse_file_route_rejected_before_reader(files):
    session = setup_pipeline(pipeline_mode='Dry Run')
    files.configured.kind = 'warehouse'
    with pytest.raises(ValueError, match='Warehouse file routing'):
        orchestrate_read(store='Gold', relative_path='demo/orders.csv', file_format='csv')
    assert session.closed
    files.readers['csv'].assert_not_called()


def test_governed_operation_matches_approved_source_before_read(files, monkeypatch):
    from dataclasses import replace
    activation = importlib.import_module('fabricops_kit.activated_pipeline.shared')
    session = setup_pipeline(pipeline_mode='Dry Run')
    orchestrate_read(store='Bronze', relative_path='demo/orders.csv', file_format='csv', read_options={'header': True})
    run = shared.pipeline_run_row(session.plan, status='incomplete')
    operation = run['operations'][0]
    approved = {**activation.operation_configuration(operation), 'requested_schema': None}
    # Exercise managed operation enforcement independently of signed-in admission.
    # The production release gate remains closed; no fixture changes its value.
    verifier = Mock()
    monkeypatch.setattr(activation, 'verify_governed_plan', verifier)
    monkeypatch.setattr(shared, 'persist_pipeline_run', lambda *a, **kw: None)
    session.plan = replace(session.plan, execution_mode='governed', promotion_id='reviewed-promotion',
        activated_operations_json=json.dumps([approved]), evidence={})
    session.plan.evidence['session'] = session
    files.readers['csv'].reset_mock()
    with pytest.raises(ValueError, match='frozen binding'):
        orchestrate_read(store='Bronze', relative_path='demo/orders.csv', file_format='csv', read_options={'header': False})
    files.readers['csv'].assert_not_called()
    assert session.closed
    assert activation.FABRIC_GOVERNED_VALIDATED is False


def test_file_pipeline_submission_round_trips_typed_operation_and_write_association():
    from fabricops_kit.activated_pipeline import shared as activation
    from tests.unit.test_pipeline_handoff import package_candidate, resign
    from tests.unit.test_activated_pipeline import operation
    package = package_candidate()
    source = file_source_identity(workspace_id='w', item_id='i', relative_path='demo/orders.csv', file_format='csv', reader_options={'header': True})
    content = json.dumps({'source': source, 'table': {'columns': []}, 'enrichment': {'table': [], 'columns': []}, 'guardrails': []})
    source_op = operation(role='source')
    source_op.update(operation_key='source:Bronze/Files/demo/orders.csv', source_type='file', source_id=source['source_id'],
        table_id=None, requested_schema=None, destination={**{k: v for k, v in source.items() if k != 'reader_options'},
                                                          'reader_options_json': json.dumps(source['reader_options'])})
    for field in ['operations', 'tested_operations']:
        package['manifest'][field].append(deepcopy(source_op))
        package['manifest'][field][0]['source_ids'] = [source['source_id']]
    run_op = {key: value for key, value in source_op.items() if key != 'requested_schema'}
    run_op.update(contract_id='file-contract', contract_version=1, payload_sha256=activation.hashlib.sha256(content.encode()).hexdigest(),
        status='succeeded', stages=[{'stage': 'Read', 'status': 'passed'}])
    package['dry_run']['operations'].append(run_op)
    package['dry_run']['operations'][0]['source_ids'] = [source['source_id']]
    package['contracts'][source['source_id']] = {'contract_id': 'file-contract', 'contract_version': 1,
        'status': 'frozen', 'source_id': source['source_id'], 'table_id': None, 'contract_payload_json': content}
    package['manifest']['file_authorizations'] = [{'source': source, 'store': 'Bronze', 'contract_id': 'file-contract',
        'contract_version': 1, 'payload_sha256': run_op['payload_sha256']}]
    validated = activation.validate_submission(resign(package))
    activation.validate_file_execution_authorizations(validated)
    assert validated['manifest']['operations'][0]['source_table_ids'] == []
    changed = deepcopy(package)
    changed['manifest']['operations'][0]['source_ids'] = []
    with pytest.raises(ValueError, match='associations differ|inconsistent operation evidence'):
        activation.validate_submission(resign(changed))


def test_explicit_file_participant_plan_uses_same_source_identity(files):
    identity = shared.resolve_file_participant(store='Bronze', relative_path='demo/orders.csv', file_format='csv',
                                              context={'config': {}, 'scope_workspace_id': 'dev'})
    plan = shared.build_pipeline_execution_plan(execution_mode='dry_run',
        sources=[{'store': 'Bronze', 'relative_path': 'demo/orders.csv', 'file_format': 'csv'}], targets=[],
        pipeline_id='00000000-0000-4000-8000-000000000001',
        context={'config': {}, 'scope_workspace_id': 'dev', 'notebook_id': ''}, spark_session=files.runtime.spark)
    participants = json.loads(plan.participants_json)
    assert list(participants) == [identity['source_id']]
    assert 'table_id' not in participants[identity['source_id']]
    run = shared.pipeline_run_row(plan, status='incomplete')
    assert run['operations'][0]['status'] == 'not_started'
    assert shared.validate_pipeline_run(run)['operations'][0]['source_id'] == identity['source_id']


def test_selected_file_contract_is_enforced_before_associated_table_write(files, spark_session, monkeypatch):
    from datetime import datetime, UTC
    from fabricops_kit.pipeline.shared import contract_guardrail_rows
    source = file_source_identity(workspace_id='physical-workspace', item_id='physical-item', relative_path='demo/orders.csv', file_format='csv')
    payload = {'source': source, 'table': {'columns': [{'column_id': 'id', 'column_name': 'id', 'data_type': 'int'}]},
               'enrichment': {'table': [], 'columns': []}, 'guardrails': []}
    contract = {'table_id': None, 'source_id': source['source_id'], 'contract_id': 'selected-file', 'contract_version': 1,
                'status': 'frozen', 'contract_payload': payload, 'contract_payload_json': json.dumps(payload)}
    monkeypatch.setattr(shared, 'resolve_data_contract_version', lambda *a, **kw: contract)
    def load_rules(*a, table_id, context, **kw):
        selected = context['_pipeline_contracts'].get(table_id)
        rules = contract_guardrail_rows(selected, workspace_id='dev', table_id=table_id) if selected else []
        context['_pipeline_rules'][table_id] = rules
        return rules
    monkeypatch.setattr(shared, 'load_table_guardrail_rules', load_rules)
    monkeypatch.setattr(shared, 'build_pipeline_audit_fields', lambda **kw: {'_activity_id': 'test', '_committed_at': datetime.now(UTC)})
    monkeypatch.setattr(importlib.import_module('fabricops_kit.pipeline.check_schema'), 'get_store', lambda *a: files.configured)
    frame = spark_session.createDataFrame([(1,), (2,)], 'id int')
    files.readers['csv'].return_value = frame
    session = setup_pipeline(pipeline_mode='Dry Run')
    session.spark = spark_session
    session.select_contract(source['source_id'], 'selected-file', 1)
    read = orchestrate_read(store='Bronze', relative_path='demo/orders.csv', file_format='csv')
    assert read['selected_contract'] == {'contract_id': 'selected-file', 'contract_version': 1}
    assert read['schema_result']['source_id'] == source['source_id']
    assert read['guardrail_outcomes'][0]['source_id'] == source['source_id']
    write = orchestrate_write(read['dataframe'], store='Silver', schema='demo', table_name='curated_orders', write_mode='overwrite')
    assert write['source_guardrail_results'][0]['can_continue'] is True
    assert source['source_id'] in write['tested_contracts']
    assert write['source_ids'] == [source['source_id']]
    assert finalize_pipeline(session)['status'] == 'dry_run_completed'


def test_persisted_file_guardrail_uses_explicit_nullable_identity_schema(files, spark_session, monkeypatch):
    from datetime import datetime
    from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS
    source = file_source_identity(workspace_id='w', item_id='i', relative_path='demo/orders.csv', file_format='csv')
    audit = {name: datetime(2026, 1, 1) if kind == 'timestamp' else 'test' for name, kind, _nullable in AUDIT_SCHEMA_FIELDS}
    monkeypatch.setattr(shared, 'build_pipeline_audit_fields', lambda **kw: audit)
    written = Mock()
    monkeypatch.setattr(shared, 'write_lakehouse_table', written)
    shared.write_guardrail_result_row(spark_session=spark_session, config={}, active_workspace_id='dev', run_id='run',
        dataset_name='', table_name='demo/orders.csv', store_type='file', layer='Bronze', guardrail_type='schema',
        rule_type='strict', table_id=source['source_id'], contract_id='file-contract', contract_version=1,
        result={'guardrail_rule_id': 'schema', 'guardrail_version': 1, 'status': 'passed', 'can_continue': True},
        context={'config': {}, 'scope_workspace_id': 'dev'})
    frame = written.call_args.args[0]
    assert frame.schema['table_id'].nullable and frame.schema['source_id'].nullable
    row = frame.first()
    assert row['table_id'] is None and row['source_id'] == source['source_id']
