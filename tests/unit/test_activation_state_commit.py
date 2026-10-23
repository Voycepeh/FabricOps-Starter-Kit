"""Governance authority stays read-only during engineering reservation commits."""
# ruff: noqa: D103
from copy import deepcopy
import json

import pytest

from fabricops_kit.activated_pipeline import shared as service
from fabricops_kit.config import shared as config


@pytest.fixture
def state_store(monkeypatch):
    state = {'METADATA_ACTIVATION_STATE': ['authority-0', json.loads(service.empty_activation_state())],
             'METADATA_EXECUTION_STATE': ['execution-0', {'format': 'fabricops.execution-state.v1', 'locked': False, 'runs': {}}]}
    writes = []
    def records(table, **kwargs):
        token, snapshot = state[table]
        return [{'authority_id': 'central', 'token': token, 'snapshot_json': json.dumps(snapshot)}]
    def commit(table, snapshot, *, expected_token, **kwargs):
        if state[table][0] != expected_token:
            raise ValueError('stale snapshot')
        token = f'{table}-{len(writes)}'
        state[table] = [token, deepcopy(snapshot)]
        writes.append((table, deepcopy(snapshot)))
        return token
    monkeypatch.setattr(service, 'metadata_records', records)
    monkeypatch.setattr(config, 'commit_metadata_snapshot', commit)
    return state, writes


def test_execution_reservations_do_not_write_governance_authority(state_store):
    state, writes = state_store
    token, proposal = service.read_activation_state(context={})
    service.environment_activation(proposal, 'DEV', {'_registry_workspace_id': 'team-a'})['runs']['run-a'] = {'mode': 'live'}
    committed = service.commit_activation_state(proposal, expected_token=token, context={})
    assert all(table == 'METADATA_EXECUTION_STATE' for table, _ in writes)
    assert state['METADATA_ACTIVATION_STATE'][0] == 'authority-0'
    assert service.read_activation_state(context={}) == (committed, proposal)
    with pytest.raises(ValueError, match='changed'):
        service.commit_activation_state(proposal, expected_token=token, context={})


def test_activation_claims_cutover_lock_before_governance_commit_and_unlocks_after(state_store):
    _state, writes = state_store
    token, proposal = service.read_activation_state(context={})
    service.environment_activation(proposal, 'DEV')['revision'] = 'approved'
    service.commit_activation_state(proposal, expected_token=token, context={})
    assert [table for table, _ in writes] == ['METADATA_EXECUTION_STATE', 'METADATA_ACTIVATION_STATE', 'METADATA_EXECUTION_STATE']
    assert writes[0][1]['locked'] and writes[-1][1]['locked'] is False


def test_interrupted_cutover_cannot_be_read_or_recovered_by_timeout(state_store):
    state, _writes = state_store
    state['METADATA_EXECUTION_STATE'][1]['locked'] = 'interrupted-transaction'
    with pytest.raises(RuntimeError, match='locked'):
        service.read_activation_state(context={})


def test_legacy_reservations_fail_closed_until_jobs_verified_stopped(state_store):
    state, _writes = state_store
    service.environment_activation(state['METADATA_ACTIVATION_STATE'][1], 'DEV')['runs']['old-run'] = {}
    with pytest.raises(RuntimeError, match='Legacy activation reservations'):
        service.read_activation_state(context={})


def test_unconfirmed_authority_write_leaves_cutover_locked(state_store, monkeypatch):
    state, _writes = state_store
    original = config.commit_metadata_snapshot
    def fail(table, *args, **kwargs):
        if table == 'METADATA_ACTIVATION_STATE':
            raise PermissionError('Governance table is read-only')
        return original(table, *args, **kwargs)
    monkeypatch.setattr(config, 'commit_metadata_snapshot', fail)
    token, proposal = service.read_activation_state(context={})
    service.environment_activation(proposal, 'DEV')['revision'] = 'unauthorized'
    with pytest.raises(PermissionError):
        service.commit_activation_state(proposal, expected_token=token, context={})
    assert state['METADATA_ACTIVATION_STATE'][0] == 'authority-0'
    with pytest.raises(RuntimeError, match='locked'):
        service.read_activation_state(context={})
