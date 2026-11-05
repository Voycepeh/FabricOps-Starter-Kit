"""Many workspace identities share one Governance Metadata Lakehouse on real Delta."""
# ruff: noqa: F811
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime
from threading import Barrier
from uuid import uuid4

import pytest

from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
from fabricops_kit.pipeline import shared
from tests.integration.test_pipeline_run_delta import runs_delta

pytestmark = pytest.mark.spark


@pytest.mark.parametrize('parallelism', [5, 10, 20])
def test_parallel_workspaces_keep_runs_profiles_catalogue_and_processing_state(runs_delta, monkeypatch, parallelism):
    """Real owner functions retain every workspace's metadata despite shared Delta files."""
    r = runs_delta
    schemas = metadata_table_schema_registry()
    extra = ['METADATA_GUARDRAIL_RESULTS', 'METADATA_DATA_PROFILED', 'METADATA_DATA_PROFILED_FREQUENCY',
             'METADATA_DATA_CATALOGUE', 'METADATA_PROCESSING_STATE', 'METADATA_DATA_LINEAGE']
    for table in extra:
        r.paths[table] = r.paths['METADATA_PIPELINE_RUN'] + '-' + table
        r.spark.createDataFrame([], schemas[table]).write.format('delta').save(r.paths[table])
    import importlib
    writer = importlib.import_module('fabricops_kit.io.write_lakehouse_table')
    monkeypatch.setattr(writer, 'resolve_configured_lakehouse_table',
        lambda store, table, schema, **kw: (store, table, schema, r.paths[table]))
    monkeypatch.setattr(shared, 'get_spark_session', lambda *a, **kw: r.spark)
    monkeypatch.setattr(shared, 'resolve_catalogue_table_identity', lambda *a, **kw: {'table_name': 'orders'})
    # Route all workspaces to the same paths while preserving their logical scope.
    monkeypatch.setattr(shared, 'persistence_permitted', lambda context: True)
    monkeypatch.setattr(shared, 'build_runtime_audit_fields', lambda **kw: {**r.audit,
        '_workspace_id': kw['active_workspace_id'], '_committed_by': kw['runtime_context']['user_id']})
    plans = []
    for index in range(parallelism):
        plan = r.make(mode='ungoverned')
        workspace = f'workspace-{index}'
        plan = replace(plan, workspace_id=workspace, runtime_context={**plan.runtime_context,
            'scope_workspace_id': workspace, 'user_id': f'engineer-{index}',
            '_pipeline_bindings': {key: {**binding, 'workspace_id': workspace}
                for key, binding in plan.runtime_context['_pipeline_bindings'].items()}})
        plans.append(plan)
    ready = Barrier(parallelism)
    def execute(plan):
        workspace = plan.workspace_id
        audit = {**r.audit, '_workspace_id': workspace, '_committed_by': plan.runtime_context['user_id']}
        def frame(table, row):
            return r.spark.createDataFrame([{**row, **audit}], schemas[table])
        ready.wait(timeout=60)
        shared.persist_pipeline_run(plan, spark_session=r.spark)
        profile = {'profile_id': workspace, 'profile_snapshot_id': workspace, 'table_id': 'orders',
                   'workspace_id': workspace, 'row_count': 7}
        for table, identity in [('METADATA_DATA_PROFILED', 'profile_id'), ('METADATA_DATA_PROFILED_FREQUENCY', 'frequency_id')]:
            shared._replace_snapshot_rows(dataframe=frame(table, {**profile, identity: workspace}),
                table_name=table, row_id=identity, config={}, active_workspace_id=workspace, spark_session=r.spark)
        catalogue = {'workspace_id': workspace, 'table_id': 'orders', 'metadata_level': 'table',
                     'table_name': 'orders', 'is_active': True, 'last_profiled_at': datetime(2026, 1, 1)}
        shared._upsert_catalogue_identities(catalogue_df=frame('METADATA_DATA_CATALOGUE', catalogue),
            config={}, active_workspace_id=workspace, spark_session=r.spark)
        record = {**audit, 'record_id': workspace, 'record_type': 'source_observation', 'status': 'observed',
                  'workspace_id': workspace, 'run_id': plan.plan_id, 'source_table_id': 'orders'}
        shared._merge_source_observation_records([record], config={}, context=plan.runtime_context)
        shared.persist_lineage_participation(table_id='orders', pipeline_role='source',
            activity_id=workspace, context=plan.runtime_context)
        guardrail = {'guardrail_result_id': workspace, 'guardrail_rule_id': 'rule', 'guardrail_version': 1,
            'table_id': 'orders', 'contract_id': 'contract', 'contract_version': 1,
            'execution_type': 'ungoverned', 'run_id': plan.plan_id, 'workspace_id': workspace,
            'status': 'passed', 'can_continue': True, 'severity': 'warning', 'result_payload_json': '{}'}
        writer.write_lakehouse_table(frame('METADATA_GUARDRAIL_RESULTS', guardrail),
            'METADATA_GUARDRAIL_RESULTS', store='Metadata', schema='engineering',
            mode='append', verbose=False, context=plan.runtime_context)
        r.complete(plan)
        shared.persist_pipeline_run(plan, spark_session=r.spark, status='succeeded', completed_at=datetime(2026, 1, 1))
    with ThreadPoolExecutor(parallelism) as pool:
        list(pool.map(execute, plans))
    rows = r.rows()
    assert len(rows) == parallelism
    assert {row['workspace_id'] for row in rows} == {plan.workspace_id for plan in plans}
    assert all(row['status'] == 'succeeded' and len(row['operations']) == 2 for row in rows)
    for table in extra:
        retained = r.spark.read.format('delta').load(r.paths[table])
        assert retained.count() == parallelism, table
        assert retained.select('workspace_id').distinct().count() == parallelism, table


def test_checkpoint_and_receipt_packages_remain_atomic_across_workspaces(runs_delta, monkeypatch):
    """Concurrent checkpoint progress never separates from its matching publication receipt."""
    r = runs_delta
    table = 'METADATA_PROCESSING_STATE'
    r.paths[table] = r.paths['METADATA_PIPELINE_RUN'] + '-progress'
    r.spark.createDataFrame([], metadata_table_schema_registry()[table]).write.format('delta').save(r.paths[table])
    monkeypatch.setattr(shared, 'get_spark_session', lambda *a, **kw: r.spark)
    monkeypatch.setattr(shared, 'persistence_permitted', lambda context: True)
    ready = Barrier(2)
    def commit(workspace):
        common = {**r.audit, 'workspace_id': workspace, 'run_id': workspace, 'publication_id': workspace,
            'target_table_id': 'target-' + workspace, 'status': 'committed'}
        receipt = {**common, 'record_id': workspace + '-receipt', 'record_type': 'publication_receipt',
            'publication_batch_id': workspace, 'publication_activity_id': workspace,
            'publication_at': datetime(2026, 1, 1), 'publication_input_rows': 7, 'publication_strategy': 'append_all'}
        checkpoint = {**common, 'record_id': workspace + '-checkpoint', 'record_type': 'incremental_checkpoint',
            'source_table_id': 'shared-source', 'max_change_value': '7', 'watermark_type': 'long'}
        baseline = {**common, 'record_id': workspace + '-baseline', 'record_type': 'drift_baseline',
            'source_table_id': 'shared-source'}
        ready.wait(timeout=60)
        shared._merge_source_observation_records([receipt, checkpoint, baseline], config={},
            context={**r.context, 'scope_workspace_id': workspace})
    with ThreadPoolExecutor(2) as pool:
        list(pool.map(commit, ['one', 'two']))
    rows = [row.asDict() for row in r.spark.read.format('delta').load(r.paths[table]).collect()]
    assert len(rows) == 6
    for workspace in ['one', 'two']:
        package = [row for row in rows if row['workspace_id'] == workspace]
        assert {row['record_type'] for row in package} == {'publication_receipt', 'incremental_checkpoint', 'drift_baseline'}
        assert all(shared._publication_receipt(row, package)['input_rows'] == 7 for row in package)
