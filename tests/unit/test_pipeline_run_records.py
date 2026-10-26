"""One-row Pipeline Run storage with native typed operations and stages."""
# ruff: noqa: F811
import copy
import json

import pytest

from fabricops_kit.pipeline import shared
from tests.unit.test_pipeline_run_evidence import runtime  # noqa: F401


@pytest.mark.parametrize('roles', [('source',), ('source', 'target'), ('source', 'source', 'target', 'target')])
def test_native_operations_expose_table_and_contract_versions(runtime, roles):
    """One run row contains the exact uniquely keyed Read/Write set."""
    make, operation, _, _, _ = runtime
    plan = make(mode='testing', roles=roles)
    for index in range(len(roles)):
        operation(plan, index)
    plan.evidence['boundary_completed'] = True
    logical = shared.finalize_pipeline_run(plan)
    record = shared.validate_pipeline_run(logical)
    assert len(record['operations']) == len(roles)
    assert len({item['operation_key'] for item in record['operations']}) == len(roles)
    assert 'candidate_json' not in record and 'definition_id' not in record
    assert all(item['contract_id'] and 'configuration_json' not in item for item in record['operations'])
    assert all(item['started_at'] and item['completed_at'] for item in record['operations'])



@pytest.mark.parametrize('defect', ['missing', 'duplicate', 'contract_reference', 'failed', 'empty_stages',
                                   'duplicate_stage', 'unresolved_stage', 'missing_boundary'])
def test_incomplete_or_mismatched_operation_array_fails_closed(runtime, defect):
    """A typed but incomplete or foreign operation cannot support parent success."""
    make, operation, _, _, _ = runtime
    plan = make(mode='testing', roles=('source',))
    operation(plan, 0)
    plan.evidence['boundary_completed'] = True
    record = shared.finalize_pipeline_run(plan)
    item = record['operations'][0]
    if defect == 'missing':
        record['operations'].clear()
    elif defect == 'duplicate':
        record['operations'].append(copy.deepcopy(item))
    elif defect == 'contract_reference':
        item['contract_version'] = None
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
        shared.validate_pipeline_run(record)


def test_native_run_preserves_profiling_without_configuration_join(runtime):
    """Profile results remain Run facts alongside the operation array."""
    make, operation, _, _, _ = runtime
    plan = make(mode='testing', roles=('source',))
    operation(plan, 0)
    plan.evidence['profiling'] = [{'activity': 'grain', 'status': 'passed', 'context_key': 'physical'}]
    logical = shared.finalize_pipeline_run(plan)
    assert logical['profiling'][0]['activity'] == 'grain'
    assert 'definition_id' not in logical
