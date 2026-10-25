"""Typed Pipeline Run completeness, identity and lossless history conversion."""
# ruff: noqa: F811
import copy
import json

import pytest

from fabricops_kit.pipeline import shared
from scripts.migrate_pipeline_runs import convert_run
from tests.unit.test_pipeline_run_evidence import runtime  # noqa: F401


@pytest.mark.parametrize('roles', [('source',), ('source', 'target'), ('source', 'source', 'target', 'target')])
def test_typed_record_identity_and_roundtrip(runtime, roles):
    """Every logical Read/Write has one typed, queryable, stable operation."""
    make, operation, _, _, _ = runtime
    plan = make(mode='testing', roles=roles)
    for index in range(len(roles)):
        operation(plan, index)
    plan.evidence['boundary_completed'] = True
    logical = shared.finalize_pipeline_run(plan)
    records = shared.pipeline_run_records(logical, snapshot_token='snapshot')
    assert len(records) == 1 + len(roles)
    assert len({row['record_id'] for row in records}) == len(records)
    assert [row['table_id'] for row in records[1:]] == [f'table{i}' for i in range(len(roles))]
    assert all(row['operation_started_at'] and row['operation_completed_at'] for row in records[1:])
    restored = shared.pipeline_run_snapshots(list(reversed(records)))[0]
    for key, value in restored.items():
        assert value == logical[key]
    migrated = convert_run(restored)
    assert shared.pipeline_run_snapshots(migrated) == [restored]


@pytest.mark.parametrize('corruption', ['missing', 'duplicate', 'foreign', 'token', 'status', 'table', 'stage', 'identity', 'parent'])
def test_corrupt_snapshots_fail_closed(runtime, corruption):
    """Partial, foreign and tampered child rows cannot produce approval evidence."""
    make, operation, _, _, _ = runtime
    plan = make(mode='testing', roles=('source',))
    operation(plan, 0)
    plan.evidence['boundary_completed'] = True
    records = shared.pipeline_run_records(shared.finalize_pipeline_run(plan), snapshot_token='snapshot')
    if corruption == 'missing':
        records.pop()
    elif corruption == 'duplicate':
        records.append(copy.deepcopy(records[-1]))
    elif corruption == 'parent':
        records.pop(0)
    else:
        field, value = {'foreign': ('environment_name', 'other'), 'token': ('snapshot_token', 'other'),
            'status': ('status', 'failed'), 'table': ('table_id', 'foreign-table'),
            'stage': ('stages_json', '[]'), 'identity': ('operation_id', 'forged')}[corruption]
        records[-1][field] = value
        # Even a self-consistent digest cannot replace candidate table identity.
        if corruption in {'table', 'identity'}:
            records[0]['operations_digest'] = shared._pipeline_operations_digest(records[1:])
    with pytest.raises(ValueError):
        shared.pipeline_run_snapshots(records)


def test_history_conversion_rejects_ambiguous_operations_and_retains_profiling(runtime):
    """Do not discard unknown history or synthesize successful operation facts."""
    make, operation, _, _, _ = runtime
    plan = make(mode='testing', roles=('source',))
    operation(plan, 0)
    plan.evidence['profiling'] = [{'activity': 'grain', 'status': 'passed', 'context_key': 'physical'}]
    logical = shared.pipeline_run_snapshots(shared.pipeline_run_records(
        shared.finalize_pipeline_run(plan), snapshot_token='snapshot'))[0]
    assert json.loads(shared.pipeline_run_snapshots(convert_run(logical))[0]['operation_summary_json'])['profiling'] == plan.evidence['profiling']
    summary = json.loads(logical['operation_summary_json'])
    summary['operations'].clear()
    logical['operation_summary_json'] = json.dumps(summary)
    with pytest.raises(ValueError, match='membership'):
        convert_run(logical)


@pytest.mark.parametrize('defect', ['duplicate_stage', 'unresolved_stage', 'missing_configuration', 'missing_boundary'])
def test_self_consistent_but_incomplete_success_is_rejected(runtime, defect):
    """A recomputed digest cannot turn incomplete operation facts into run success."""
    make, operation, _, _, _ = runtime
    plan = make(mode='testing', roles=('source',))
    operation(plan, 0)
    plan.evidence['boundary_completed'] = True
    logical = shared.finalize_pipeline_run(plan)
    summary = json.loads(logical['operation_summary_json'])
    item = next(iter(summary['operations'].values()))
    if defect == 'duplicate_stage':
        item['stages'].append(dict(item['stages'][0]))
    elif defect == 'unresolved_stage':
        item['stages'][0]['status'] = 'pending'
    elif defect == 'missing_configuration':
        item.pop('configuration')
    else:
        summary['boundary_completed'] = False
    logical['operation_summary_json'] = json.dumps(summary)
    with pytest.raises(ValueError, match='successful authority'):
        shared.pipeline_run_snapshots(shared.pipeline_run_records(logical, snapshot_token='snapshot'))
