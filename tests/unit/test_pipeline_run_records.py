"""One-row Pipeline Run storage with native typed operations and stages."""
# ruff: noqa: F811
import copy
import json

import pytest

from fabricops_kit.pipeline import shared
from scripts.migrate_pipeline_runs import convert_run
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
    record = shared.pipeline_run_row(logical)
    assert len(record['operations']) == len(roles)
    assert len({item['operation_key'] for item in record['operations']}) == len(roles)
    assert [item['table_id'] for item in record['operations']] == [f'table{i}' for i in range(len(roles))]
    assert all(item['started_at'] and item['completed_at'] for item in record['operations'])
    restored = shared.pipeline_run_result(record)
    assert all(value == logical[key] for key, value in restored.items())
    assert shared.pipeline_run_result(convert_run(restored)) == restored


@pytest.mark.parametrize('defect', ['missing', 'duplicate', 'table', 'contract', 'configuration', 'failed', 'empty_stages',
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
    elif defect == 'table':
        item['table_id'] = 'foreign-table'
    elif defect == 'contract':
        item['contract_version'] = 999
    elif defect == 'configuration':
        item['configuration_json'] = '{}'
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
    with pytest.raises(ValueError):
        shared.pipeline_run_result(record)


def test_history_conversion_preserves_profiling_and_rejects_unknown_fields(runtime):
    """Offline conversion retains all historical details or stops explicitly."""
    make, operation, _, _, _ = runtime
    plan = make(mode='testing', roles=('source',))
    operation(plan, 0)
    plan.evidence['profiling'] = [{'activity': 'grain', 'status': 'passed', 'context_key': 'physical'}]
    logical = shared.pipeline_run_result(shared.pipeline_run_row(shared.finalize_pipeline_run(plan)))
    converted = convert_run(logical)
    assert json.loads(shared.pipeline_run_result(converted)['operation_summary_json'])['profiling'] == plan.evidence['profiling']
    summary = json.loads(logical['operation_summary_json'])
    next(iter(summary['operations'].values()))['unknown_historical_field'] = 'preserve-or-reject'
    logical['operation_summary_json'] = json.dumps(summary)
    with pytest.raises(ValueError, match='Unknown'):
        convert_run(logical)
