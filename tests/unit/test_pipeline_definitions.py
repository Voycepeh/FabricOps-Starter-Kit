"""Content-addressed immutable definitions and exact retained reference validation."""
# ruff: noqa: F811
from copy import deepcopy
import json

import pytest

from fabricops_kit.pipeline import shared
from tests.unit.test_pipeline_run_evidence import runtime


@pytest.mark.parametrize('defect', ['participant', 'operation', 'configuration', 'binding', 'contract', 'environment', 'hash'])
def test_altered_definition_fails_closed(runtime, defect):
    """No foreign member or changed retained configuration can reuse a sealed ID."""
    make, operation, *_ = runtime
    plan = make(mode='testing', roles=('source', 'target'))
    for index in range(2):
        operation(plan, index)
    candidate, fingerprint, _bindings = shared.pipeline_candidate(plan)
    row = shared.pipeline_definition_row(candidate, environment=plan.environment, fingerprint=fingerprint)
    assert shared.pipeline_definition_candidate(row) == candidate
    changed = deepcopy(row)
    if defect == 'participant':
        changed['participants'].append(deepcopy(changed['participants'][0]))
    elif defect == 'operation':
        changed['operation_configurations'].pop()
    elif defect == 'configuration':
        changed['operation_configurations'][0]['configuration_json'] = '{"changed":true}'
    elif defect == 'binding':
        changed['physical_bindings'][0]['item_id'] = 'another-item'
    elif defect == 'contract':
        changed['participants'][0]['payload_sha256'] = 'altered'
    elif defect == 'environment':
        changed['environment_name'] = 'OTHER'
    else:
        changed['definition_id'] = 'forged'
    with pytest.raises(ValueError):
        shared.pipeline_definition_candidate(changed)


def test_run_parent_and_environment_cannot_reference_a_foreign_definition(runtime):
    """Repeated scalar parents provide a checked filtering identity, not a second definition."""
    make, operation, *_ = runtime
    plan = make(mode='testing', roles=('source',))
    operation(plan, 0)
    plan.evidence['boundary_completed'] = True
    logical = shared.finalize_pipeline_run(plan)
    row = shared.pipeline_run_row(logical)
    definition = shared.pipeline_definition_row(json.loads(logical['candidate_json']), environment=plan.environment,
        fingerprint=logical['candidate_fingerprint'])
    for field in ('pipeline_id', 'environment_name'):
        with pytest.raises(ValueError, match='foreign immutable definition'):
            shared.pipeline_run_result({**row, field: 'foreign'}, definition=definition)
