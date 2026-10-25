"""One-row Pipeline Run storage with native typed operations and stages."""
# ruff: noqa: F811
import copy
import json

import pytest

from fabricops_kit.pipeline import shared
from tests.unit.test_pipeline_run_evidence import runtime  # noqa: F401


@pytest.mark.parametrize('roles', [('source',), ('source', 'target'), ('source', 'source', 'target', 'target')])
def test_typed_operations_roundtrip_and_query_fields(runtime, roles):
    """One run row contains the exact uniquely keyed Read/Write set."""
    make, operation, _, _, _ = runtime
    plan = make(mode='testing', roles=roles)
    for index in range(len(roles)):
        operation(plan, index)
    plan.evidence['boundary_completed'] = True
    logical = shared.finalize_pipeline_run(plan)
    shared.seal_pipeline_definition(json.loads(logical['candidate_json']), environment=plan.environment,
        fingerprint=logical['candidate_fingerprint'])
    record = shared.pipeline_run_row(logical)
    assert len(record['operations']) == len(roles)
    assert len({item['operation_key'] for item in record['operations']}) == len(roles)
    assert 'candidate_json' not in record
    assert all('configuration_json' not in item and 'contract_id' not in item for item in record['operations'])
    assert all(item['started_at'] and item['completed_at'] for item in record['operations'])
    restored = shared.pipeline_run_result(record)
    assert all(value == logical[key] for key, value in restored.items())


@pytest.mark.parametrize('defect', ['missing', 'duplicate', 'foreign_definition', 'failed', 'empty_stages',
                                   'duplicate_stage', 'unresolved_stage', 'missing_boundary'])
def test_incomplete_or_mismatched_operation_array_fails_closed(runtime, defect):
    """A typed but incomplete or foreign operation cannot support parent success."""
    make, operation, _, _, _ = runtime
    plan = make(mode='testing', roles=('source',))
    operation(plan, 0)
    plan.evidence['boundary_completed'] = True
    record = shared.pipeline_run_row(shared.finalize_pipeline_run(plan))
    item = record['operations'][0]
    if defect == 'missing':
        record['operations'].clear()
    elif defect == 'duplicate':
        record['operations'].append(copy.deepcopy(item))
    elif defect == 'foreign_definition':
        record['definition_id'] = 'missing-definition'
    elif defect == 'failed':
        item['status'] = 'failed'
    elif defect == 'empty_stages':
        item['stages'] = []
    elif defect == 'duplicate_stage':
        item['stages'].append(dict(item['stages'][0]))
    elif defect == 'unresolved_stage':
        item['stages'][0]['status'] = 'pending'
    else:
        record['boundary_completed'] = False
    with pytest.raises((ValueError, KeyError)):
        shared.pipeline_run_result(record)


def test_typed_storage_preserves_profiling_and_rejects_unknown_fields(runtime):
    """Offline conversion retains all historical details or stops explicitly."""
    make, operation, _, _, _ = runtime
    plan = make(mode='testing', roles=('source',))
    operation(plan, 0)
    plan.evidence['profiling'] = [{'activity': 'grain', 'status': 'passed', 'context_key': 'physical'}]
    logical = shared.finalize_pipeline_run(plan)
    shared.seal_pipeline_definition(json.loads(logical['candidate_json']), environment=plan.environment, fingerprint=logical['candidate_fingerprint'])
    logical = shared.pipeline_run_result(shared.pipeline_run_row(logical))
    assert json.loads(logical['operation_summary_json'])['profiling'] == plan.evidence['profiling']
    summary = json.loads(logical['operation_summary_json'])
    next(iter(summary['operations'].values()))['unknown_historical_field'] = 'preserve-or-reject'
    logical['operation_summary_json'] = json.dumps(summary)
    with pytest.raises(ValueError, match='Unknown'):
        shared.pipeline_run_row(logical)
