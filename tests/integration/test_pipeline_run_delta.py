"""Pipeline Run atomic publication, conflict fencing and Test approval on real Delta."""
# ruff: noqa: F811
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from dataclasses import replace
from datetime import UTC, datetime
from threading import Barrier
from types import SimpleNamespace
from uuid import uuid4

import pytest
import json

from fabricops_kit import finalize_pipeline
from fabricops_kit.activated_pipeline import shared as activation
from fabricops_kit.config.metadata_schemas import AUDIT_SCHEMA_FIELDS, coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.pipeline import shared

pytestmark = pytest.mark.spark


@pytest.fixture
def runs_delta(monkeypatch, spark_session, tmp_path):
    """Replace Fabric routing and notebook discovery; publish actual canonical Delta records."""
    pytest.importorskip('delta.tables')
    if 'DeltaSparkSessionExtension' not in spark_session.conf.get('spark.sql.extensions', ''):
        pytest.skip('requires Delta Spark extensions')
    tables = ('METADATA_PIPELINE_RUN', 'METADATA_GUARDRAIL_RESULTS', 'METADATA_DATA_CONTRACT', 'METADATA_DATA_AGREEMENT', 'METADATA_PIPELINE_REGISTRY')
    paths = {table: str(tmp_path / table) for table in tables}
    registry = metadata_table_schema_registry()
    for table in tables:
        initial = [{**activation.empty_pipeline_authority(), **{name: datetime.now() if name == '_committed_at' else 'test-runtime' for name, *_ in AUDIT_SCHEMA_FIELDS}}] if table == 'METADATA_PIPELINE_REGISTRY' else []
        spark_session.createDataFrame(initial, registry[table]).write.format('delta').save(paths[table])
    audit = {name: datetime.now() if name == '_committed_at' else 'test-runtime' for name, *_ in AUDIT_SCHEMA_FIELDS}
    audit.update(_workspace_id='workspace', _notebook_id='notebook')
    context = {'config': {}, 'env': 'DEV', 'workspace_id': 'workspace', 'notebook_id': 'notebook'}
    # Explicit plans isolate Delta persistence from Fabric notebook initialization.
    monkeypatch.setattr(shared, 'get_default_fabric_context', lambda **kwargs: context)
    pipeline_id = '4c7ae400-85ab-4023-9427-e8fde20bd596'
    for module in (shared, activation):
        monkeypatch.setattr(module, 'resolve_fabric_context', lambda context=None: (context['config'], context['env'], context))
        monkeypatch.setattr(module, 'build_runtime_audit_fields', lambda **kwargs: dict(audit))
        monkeypatch.setattr(module, 'resolve_configured_lakehouse_table',
            lambda store, table, schema, **kwargs: (store, table, 'engineering', paths[table]))
        monkeypatch.setattr(module, 'read_lakehouse_table', lambda table, **kwargs: spark_session.read.format('delta').load(paths[table]))
    shared.resolve_pipeline_registration(pipeline_id, context=context, spark_session=spark_session)
    def append(table, rows):
        spark_session.createDataFrame([coerce_metadata_row_types(table, {**row, **audit}) for row in rows], registry[table]).write.format('delta').mode('append').save(paths[table])
    agreement = {'agreement_id': 'agreement', 'agreement_version': '1', 'start_date': '2020-01-01',
                 'expiry_date': '2099-01-01', 'agreement_name': 'Agreement'}
    # Agreement's non-null authored fields are irrelevant to exact date/version validation.
    for field in registry['METADATA_DATA_AGREEMENT']:
        if not field.nullable and field.name not in agreement and not field.name.startswith('_'):
            agreement[field.name] = 'test'
    append('METADATA_DATA_AGREEMENT', [agreement])
    retained = set()
    def make(roles=('source', 'target'), mode='testing', run_id=None):
        participants, contracts, bindings = {}, {}, {}
        for index, role in enumerate(roles):
            table = f'table{index}'
            participants[table] = {'table_id': table, 'store': 'Bound', 'table_name': table, 'logical_id': table, 'roles': [role]}
            payload = {'contract': {'contract_id': 'contract-' + table, 'contract_version': 1, 'status': 'frozen'},
                       'table': {'table_id': table, 'columns': [{'column_id': 'id-col', 'column_name': 'id', 'data_type': 'bigint'}]},
                       'guardrails': [{'guardrail_rule_id': 'schema-' + table, 'guardrail_version': 1,
                            'guardrail_type': 'schema', 'rule_type': 'required_columns',
                            'rule_parameters': {'required_columns': ['id-col']}, 'action': 'Block', 'is_active': True}]}
            contracts[table] = {'contract_id': 'contract-' + table, 'contract_version': 1, 'table_id': table,
                'status': 'frozen', 'environment_name': 'DEV', 'contract_payload_json': shared.canonical_pipeline_json(payload)}
            bindings[table] = {'workspace_id': 'workspace', 'item_id': 'lakehouse', 'kind': 'lakehouse', 'schema': 'demo', 'table_name': table}
        for contract in contracts.values():
            key = (contract['contract_id'], contract['contract_version'])
            if key not in retained:
                append('METADATA_DATA_CONTRACT', [contract])
                retained.add(key)
        plan = shared.PipelineExecutionPlan(mode, 'DEV', 'notebook', run_id or str(uuid4()),
            shared.canonical_pipeline_json(participants), '{}', shared.canonical_pipeline_json(contracts),
            {**context, '_pipeline_bindings': bindings}, pipeline_id=pipeline_id,
            approval_id='release' if mode == 'live' else '')
        return plan
    def complete(plan):
        for key, operation in plan.evidence['operations'].items():
            operation.update(status='succeeded', read_mode='full' if key.startswith('source:') else None,
                write_mode='overwrite' if key.startswith('target:') else None, source_table_ids=sorted(
                    table for table, item in json.loads(plan.participants_json).items() if 'source' in item['roles']) if key.startswith('target:') else [],
                stages=[{'stage': 'Read' if key.startswith('source:') else 'Processing', 'status': 'passed'},
                        {'stage': 'Schema', 'status': 'passed'}, {'stage': 'Profile', 'status': 'passed'}])
        plan.evidence['guardrail_history'] = [
            {'guardrail_result_id': str(uuid4()), 'guardrail_rule_id': 'schema-' + table, 'guardrail_version': 1,
             'table_id': table, 'table_name': table, 'contract_id': 'contract-' + table, 'contract_version': 1,
             'execution_type': plan.execution_mode, 'run_id': plan.plan_id, 'environment_name': 'DEV',
             'status': 'passed', 'can_continue': True, 'severity': 'blocking', 'result_payload_json': '{}'}
            for table in json.loads(plan.participants_json)]
        plan.evidence['boundary_completed'] = True
    def rows():
        return [row.asDict(recursive=True) for row in spark_session.read.format('delta').load(paths['METADATA_PIPELINE_RUN']).collect()]
    return SimpleNamespace(spark=spark_session, paths=paths, context=context, make=make, complete=complete,
                           rows=rows, append=append, audit=audit)


@pytest.mark.parametrize('roles', [('source',), ('source', 'target'), ('source', 'source', 'target', 'target')])
def test_finalized_test_is_atomic_and_activation_reads_all_typed_operations(runs_delta, roles):
    """Finalized Test is durable and eligible only with a complete verified row set."""
    r = runs_delta
    plan = r.make(roles)
    shared.persist_pipeline_run(plan, spark_session=r.spark)
    assert r.rows() == []  # Unfinalized Test has no persisted run evidence.
    r.complete(plan)
    finalize_pipeline(shared.PipelineSession(plan, r.spark))
    records = r.rows()
    assert len(records) == 1
    assert len(records[0]['operations']) == len(roles)
    assert shared.validate_pipeline_run(records[0])['status'] == 'succeeded'
    manifest = activation.tested_pipeline_run(testing_run_id=plan.plan_id,
        pipeline_name='Orders', pipeline_version='1',
        agreement_id='agreement', agreement_version='1', context=r.context, spark_session=r.spark)
    assert manifest['testing_run_id'] == plan.plan_id
    from delta.tables import DeltaTable
    removed = plan.evidence['guardrail_history'][0]
    DeltaTable.forPath(r.spark, r.paths['METADATA_GUARDRAIL_RESULTS']).delete(
        "guardrail_result_id = '" + removed['guardrail_result_id'] + "'")
    with pytest.raises(ValueError, match='Guardrail evidence is missing'):
        activation.tested_pipeline_run(testing_run_id=plan.plan_id,
            pipeline_name='Orders', pipeline_version='1',
            agreement_id='agreement', agreement_version='1', context=r.context, spark_session=r.spark)
    r.append('METADATA_GUARDRAIL_RESULTS', [removed])
    DeltaTable.forPath(r.spark, r.paths['METADATA_PIPELINE_RUN']).update(
        set={'operations': "filter(operations, item -> item.operation_key <> 'source:table0')"})
    with pytest.raises(ValueError, match='whole-run|source outside|Guardrail evidence'):
        activation.tested_pipeline_run(testing_run_id=plan.plan_id,
            pipeline_name='Orders', pipeline_version='1',
            agreement_id='agreement', agreement_version='1', context=r.context, spark_session=r.spark)


def test_stale_writer_cannot_replace_a_newer_run_or_operation_array(runs_delta):
    """Whole-row CAS rejects stale configuration, stages and parent outcomes together."""
    r = runs_delta
    plan = r.make(mode='live')
    shared.persist_pipeline_run(plan, spark_session=r.spark)
    stale = replace(plan, evidence=deepcopy(plan.evidence))
    r.complete(plan)
    shared.persist_pipeline_run(plan, spark_session=r.spark)
    before = r.rows()
    stale.evidence['failures'].append({'code': 'stale_writer_failure'})
    with pytest.raises(RuntimeError, match='persistence failed'):
        shared.persist_pipeline_run(stale, spark_session=r.spark)
    assert r.rows() == before


def test_lost_acknowledgement_recovers_complete_snapshot_and_final_is_immutable(runs_delta, monkeypatch):
    """Physical commit followed by transport failure is confirmed without replay."""
    r = runs_delta
    plan = r.make(mode='live')
    shared.persist_pipeline_run(plan, spark_session=r.spark)
    r.complete(plan)
    plan.evidence['profiling'] = [{'context_key': 'physical-profile', 'activity': 'standard', 'status': 'passed',
        'results_persisted': True, 'empty_result': False, 'profile_snapshot_id': 'snapshot',
        'completed_at': datetime.now(UTC).isoformat(), 'table_id': 'table0', 'environment': 'DEV',
        'physical': plan.runtime_context['_pipeline_bindings']['table0'], 'row_count': None}]
    from delta.tables import DeltaMergeBuilder
    execute = DeltaMergeBuilder.execute
    def lost_ack(builder):
        execute(builder)
        raise OSError('acknowledgement lost after physical Delta commit')
    monkeypatch.setattr(DeltaMergeBuilder, 'execute', lost_ack)
    result = shared.finalize_pipeline_run(plan, spark_session=r.spark)
    assert result['status'] == 'succeeded'
    assert r.rows()[0]['profiling'][0]['row_count'] is None
    assert shared.finalize_pipeline_run(plan, spark_session=r.spark) == result
    monkeypatch.setattr(DeltaMergeBuilder, 'execute', execute)
    with pytest.raises(RuntimeError, match='persistence failed'):
        shared.persist_pipeline_run(plan, spark_session=r.spark)
    assert shared.validate_pipeline_run(r.rows()[0])['status'] == 'succeeded'


def test_competing_first_publications_cannot_duplicate_a_run(runs_delta):
    """SetTransaction fences simultaneous first publication of the same run ID."""
    r = runs_delta
    plan = r.make(mode='live')
    other = replace(plan, evidence=deepcopy(plan.evidence))
    ready = Barrier(2)
    def write(item):
        ready.wait(timeout=30)
        try:
            shared.persist_pipeline_run(item, spark_session=r.spark)
            return True
        except RuntimeError:
            return False
    with ThreadPoolExecutor(2) as pool:
        outcomes = list(pool.map(write, (plan, other)))
    assert any(outcomes)
    assert len(r.rows()) == 1
    assert shared.validate_pipeline_run(r.rows()[0])['status'] == 'incomplete'



def test_simultaneous_updates_accept_one_complete_run(runs_delta):
    """Whole-row CAS rejects a stale writer when two attempts change the same run."""
    r = runs_delta
    plan = r.make(mode='live')
    shared.persist_pipeline_run(plan, spark_session=r.spark)
    other = replace(plan, evidence=deepcopy(plan.evidence))
    plan.evidence.setdefault('warnings', []).append({'code': 'first_writer'})
    other.evidence['failures'].append({'code': 'competing_writer_failure'})
    ready = Barrier(2)
    def update(item):
        ready.wait(timeout=30)
        try:
            shared.persist_pipeline_run(item, spark_session=r.spark)
            return True
        except RuntimeError:
            return False
    with ThreadPoolExecutor(2) as pool:
        outcomes = list(pool.map(update, (plan, other)))
    assert sum(outcomes) == 1
    assert len(r.rows()) == 1
    assert shared.validate_pipeline_run(r.rows()[0])['run_id'] == plan.plan_id


def test_foreign_guardrail_provenance_cannot_approve(runs_delta):
    """Matching run/rule IDs from a different environment never count as Test proof."""
    r = runs_delta
    plan = r.make(roles=('source',))
    r.complete(plan)
    finalize_pipeline(shared.PipelineSession(plan, r.spark))
    from delta.tables import DeltaTable
    DeltaTable.forPath(r.spark, r.paths['METADATA_GUARDRAIL_RESULTS']).update(set={'environment_name': "'FOREIGN'"})
    with pytest.raises(ValueError, match='provenance'):
        activation.tested_pipeline_run(testing_run_id=plan.plan_id,
            pipeline_name='Orders', pipeline_version='1',
            agreement_id='agreement', agreement_version='1', context=r.context, spark_session=r.spark)


def test_guardrail_commit_without_run_authority_cannot_approve(runs_delta, monkeypatch):
    """A failure between diagnostic and run commits leaves no approving snapshot."""
    r = runs_delta
    plan = r.make(roles=('source',))
    r.complete(plan)
    def fail_before_run(*args, **kwargs):
        raise OSError('run transaction unavailable')
    monkeypatch.setattr(shared, '_merge_pipeline_run_row', fail_before_run)
    with pytest.raises(RuntimeError, match='persistence failed'):
        finalize_pipeline(shared.PipelineSession(plan, r.spark))
    assert r.rows() == []
    assert r.spark.read.format('delta').load(r.paths['METADATA_GUARDRAIL_RESULTS']).count() == 1
    with pytest.raises(ValueError, match='missing or duplicated'):
        activation.tested_pipeline_run(testing_run_id=plan.plan_id,
            pipeline_name='Orders', pipeline_version='1',
            agreement_id='agreement', agreement_version='1', context=r.context, spark_session=r.spark)


def test_independent_runs_update_concurrently_without_metadata_conflicts(runs_delta):
    """Unrelated runs sharing a data file both progress, without per-update DDL."""
    r = runs_delta
    plans = [r.make(mode='live') for _ in range(2)]
    for plan in plans:
        shared.persist_pipeline_run(plan, spark_session=r.spark)
    # Force normal file-level contention so the bounded OCC retry is exercised.
    r.spark.createDataFrame(r.rows(), metadata_table_schema_registry()['METADATA_PIPELINE_RUN']).coalesce(1).write.format('delta').mode('overwrite').save(r.paths['METADATA_PIPELINE_RUN'])
    for iteration in range(3):
        ready = Barrier(2)
        for plan in plans:
            plan.evidence.setdefault('warnings', []).append({'iteration': iteration})
        def update(plan):
            ready.wait(timeout=30)
            return shared.persist_pipeline_run(plan, spark_session=r.spark)
        with ThreadPoolExecutor(2) as pool:
            outcomes = list(pool.map(update, plans))
        assert len(outcomes) == 2
        assert all(not plan.evidence['persistence_failed'] for plan in plans)
    rows = r.rows()
    assert {row['run_id'] for row in rows} == {plan.plan_id for plan in plans}
    from delta.tables import DeltaTable
    assert all(row['operation'] != 'SET TBLPROPERTIES' for row in
        DeltaTable.forPath(r.spark, r.paths['METADATA_PIPELINE_RUN']).history().select('operation').collect())


def test_sql_explodes_native_operation_and_stage_fields(runs_delta):
    """Read statuses and exact contracts through typed fields without JSON parsing."""
    r = runs_delta
    plan = r.make()
    r.complete(plan)
    finalize_pipeline(shared.PipelineSession(plan, r.spark))
    from pyspark.sql import functions as F
    runs = r.spark.read.format('delta').load(r.paths['METADATA_PIPELINE_RUN'])
    operations = runs.select(F.explode('operations').alias('op'))
    assert {row.table_id for row in operations.select('op.table_id').collect()} == {'table0', 'table1'}
    assert operations.filter(F.col('op.contract_version') == 1).count() == 2
    stages = operations.select(F.explode('op.stages').alias('stage'))
    assert stages.filter(F.col('stage.status') == 'passed').count() == 6
