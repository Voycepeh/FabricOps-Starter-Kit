"""Persist Test observations and final Run facts using the real Delta boundaries."""
# ruff: noqa: F811
import json
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from fabricops_kit import finalize_pipeline
from fabricops_kit.pipeline import shared
from tests.integration.test_activation_state_delta import authority_delta  # noqa: F401

pytestmark = pytest.mark.spark


def test_test_profiles_publish_once_with_table_and_run_identity(authority_delta, monkeypatch):
    """Prepared target aggregates support Governance without a physical target or reread."""
    r = authority_delta
    frame = r.spark.createDataFrame([(10, 'masked'), (20, 'masked')], ['id', 'category'])
    identity = {'table_id': 'target', 'store': 'Silver', 'schema': 'demo', 'table_name': 'target',
                'store_kind': 'lakehouse', 'roles': ['target'], 'logical_id': 'target'}
    binding = {'workspace_id': 'DEV', 'item_id': 'business-item', 'kind': 'lakehouse', 'schema': 'demo', 'table_name': 'target'}
    plan = shared.PipelineExecutionPlan('testing', 'DEV', 'notebook', str(uuid4()), json.dumps({'target': identity}),
        json.dumps({'target': {'no_contract': True}}), json.dumps({'target': None}),
        {**r.context, '_pipeline_bindings': {'target': binding}}, pipeline_id=str(uuid4()))
    context = {**r.context, 'execution_plan': plan, '_pipeline_identities': {'target': identity}, '_pipeline_contracts': {'target': None}}
    monkeypatch.setattr(shared, 'build_runtime_audit_fields', lambda **kw: {
        **r.audit, '_activity_id': kw['runtime_context'].get('activity_id', r.audit['_activity_id'])})
    monkeypatch.setattr(shared, 'get_default_fabric_context', lambda **kw: plan.runtime_context)
    monkeypatch.setattr(shared, 'resolve_catalogue_table_identity', lambda *a, **kw: dict(identity))
    monkeypatch.setattr(shared, 'profiling_completion_history', lambda *a, **kw: {})
    monkeypatch.setattr(shared, 'pipeline_physical_bindings', lambda *a, **kw: {'target': binding})
    calculate = SimpleNamespace(calls=0)
    original = shared.build_profile_dataframe

    def profile(dataframe, **kwargs):
        calculate.calls += 1
        assert dataframe is frame
        return original(dataframe, **kwargs)

    monkeypatch.setattr(shared, 'build_profile_dataframe', profile)
    result = shared.schedule_table_profiling('target', 'write', dataframe=frame, context=context, spark_session=r.spark)
    assert result['row_count'] == 2 and calculate.calls == 1
    assert 'METADATA_DATA_CATALOGUE' not in r.paths and 'METADATA_DATA_PROFILED' not in r.paths
    for operation in plan.evidence['operations'].values():
        operation.update(status='succeeded', started_at=datetime.now(UTC).isoformat(), completed_at=datetime.now(UTC).isoformat(), write_mode='overwrite', source_table_ids=[],
            stages=[{'stage': 'Processing', 'status': 'passed'}, {'stage': 'Profile', 'status': 'passed'}])
    token = shared._ACTIVE_PIPELINE.set(None)
    session = shared.PipelineSession(plan, r.spark)
    try:
        final = finalize_pipeline(session)
        assert final['status'] == 'ungoverned_completed' and calculate.calls == 1
        profiles = r.spark.read.format('delta').load(r.ensure('METADATA_DATA_PROFILED')).collect()
        assert {row.table_id for row in profiles} == {'target'}
        assert all(row.workspace_id == 'DEV' and row.row_count == 2 for row in profiles)
        assert {row._activity_id for row in profiles} == {plan.plan_id}
        columns = {row.column_name: row for row in profiles}
        assert columns['id'].min_value == '10' and columns['id'].max_value == '20'
        catalogue = r.spark.read.format('delta').load(r.ensure('METADATA_DATA_CATALOGUE')).collect()
        assert {row.metadata_level for row in catalogue} == {'table', 'column'}
        assert all(row.table_id == 'target' and row.last_profiled_at is not None for row in catalogue)
        frequency = r.spark.read.format('delta').load(r.ensure('METADATA_DATA_PROFILED_FREQUENCY')).collect()
        assert frequency and {row.value for row in frequency} == {'masked'}
        stored = r.spark.read.format('delta').load(r.ensure('METADATA_PIPELINE_RUN')).first()
        assert stored.run_id == plan.plan_id and stored.status == 'ungoverned_completed'
        assert all(event.results_persisted and event.reason == 'test_observation' for event in stored.profiling)
        assert 'METADATA_PROCESSING_STATE' not in r.paths
        assert set(r.paths) <= {'METADATA_PIPELINE_REGISTRY', 'METADATA_PIPELINE_RUN', 'METADATA_DATA_CATALOGUE', 'METADATA_DATA_PROFILED', 'METADATA_DATA_PROFILED_FREQUENCY'}
        finalize_pipeline(session)
        assert calculate.calls == 1
        assert r.spark.read.format('delta').load(r.ensure('METADATA_DATA_PROFILED')).count() == len(profiles)
    finally:
        if not session.closed:
            session.close(failed=True)
        shared._ACTIVE_PIPELINE.reset(token)
