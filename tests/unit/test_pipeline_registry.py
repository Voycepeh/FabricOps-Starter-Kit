"""Permanent identity recovery and serialized Engineering registration."""
# ruff: noqa: D103
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from threading import Barrier, Lock
from uuid import UUID, uuid4
from unittest.mock import Mock

import pytest

from fabricops_kit.pipeline import shared


@pytest.fixture
def registry(monkeypatch):
    rows, token, lock = [], ["initial"], Lock()
    context = {"config": {}, "env": "Development", "workspace_id": "workspace-dev",
               "notebook_id": "notebook-one", "notebook_name": "Supplier Ingestion"}
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda context: (context["config"], context["env"], context))
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **kwargs: {"_committed_by": "engineer"})
    from fabricops_kit.activated_pipeline import shared as activation
    monkeypatch.setattr(activation, "reserve_pipeline_rebind", lambda *args, **kwargs: "rebind-lease")
    monkeypatch.setattr(activation, "release_pipeline_rebind", lambda *args, **kwargs: None)

    def read(**kwargs):
        with lock:
            return token[0], deepcopy(rows)

    def commit(row, *, expected_token, **kwargs):
        with lock:
            if token[0] != expected_token:
                raise RuntimeError("Stale Pipeline Registry")
            token[0] = str(uuid4())
            rows[:] = [old for old in rows if (old['pipeline_id'], old['environment_name']) != (row['pipeline_id'], row['environment_name'])]
            rows.append(deepcopy(row))

    monkeypatch.setattr(shared, "read_pipeline_registry", read)
    monkeypatch.setattr(shared, "commit_pipeline_registration", commit)
    return context, rows, read, commit


def test_new_uuid_recovers_even_when_execution_stops_before_saving(registry):
    context, rows, *_ = registry
    first = shared.resolve_pipeline_registration(context=context)
    assert UUID(first['pipeline_id']).version == 4 and first['resolution'] == 'New'
    recovered = shared.resolve_pipeline_registration(context=context)
    assert recovered['pipeline_id'] == first['pipeline_id'] and len(rows) == 1
    assert 'activated_pipeline_id' not in rows[0]


def test_supplied_uuid_and_rename_preserve_identity(registry):
    context, rows, *_ = registry
    identity = str(uuid4())
    original = shared.resolve_pipeline_registration(identity, context=context)
    row = shared.resolve_pipeline_registration(identity, context={**context, 'notebook_name': 'Any new name'})
    assert row['pipeline_id'] == identity and rows[0]['notebook_name'] == 'Any new name'
    assert rows[0]['registered_at'] == original['registered_at']
    assert rows[0]['registered_by'] == original['registered_by']
    assert 'updated_at' not in rows[0]


@pytest.mark.parametrize('identity', ['orders', '', None, 'not-a-uuid', '00000000-0000-1000-8000-000000000000'])
def test_invalid_uuid_fails(identity):
    with pytest.raises(ValueError, match='UUIDv4'):
        shared.validate_pipeline_id(identity)


def test_reupload_requires_explicit_expected_binding(registry):
    context, rows, *_ = registry
    original = shared.resolve_pipeline_registration(context=context)
    identity = original['pipeline_id']
    uploaded = {**context, 'notebook_id': 'reuploaded'}
    with pytest.raises(ValueError, match='previous_workspace_id'):
        shared.resolve_pipeline_registration(identity, context=uploaded)
    assert rows[0]['notebook_id'] == context['notebook_id']
    with pytest.raises(ValueError, match='previous_workspace_id'):
        shared.resolve_pipeline_registration(identity, context=uploaded, previous_binding=('wrong', 'old'))
    rebound = shared.resolve_pipeline_registration(identity, context=uploaded,
        previous_binding=(context['workspace_id'], context['notebook_id']))
    assert rebound['pipeline_id'] == identity and rebound['resolution'] == 'Rebound'
    assert rows[0]['registered_at'] == original['registered_at']
    assert rows[0]['registered_by'] == original['registered_by']
    assert 'updated_at' not in rows[0]
    assert shared.resolve_pipeline_registration(context=uploaded)['pipeline_id'] == identity


def test_failed_atomic_rebind_preserves_binding(registry, monkeypatch):
    context, rows, *_ = registry
    identity = shared.resolve_pipeline_registration(context=context)['pipeline_id']
    from fabricops_kit.activated_pipeline import shared as activation
    released = []
    monkeypatch.setattr(activation, 'release_pipeline_rebind',
        lambda pipeline_id, lease_id, **kwargs: released.append((pipeline_id, lease_id)))
    monkeypatch.setattr(shared, 'commit_pipeline_registration',
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError('registry write failed')))
    with pytest.raises(RuntimeError, match='registry write failed'):
        shared.resolve_pipeline_registration(identity, context={**context, 'notebook_id': 'reuploaded'},
            previous_binding=(context['workspace_id'], context['notebook_id']))
    assert released == []
    assert rows[0]['notebook_id'] == context['notebook_id']


def test_promotion_adds_binding_without_activation(registry):
    context, rows, *_ = registry
    identity = shared.resolve_pipeline_registration(context=context)['pipeline_id']
    prod = {**context, 'env': 'Production', 'workspace_id': 'workspace-prod', 'notebook_id': 'promoted'}
    assert shared.resolve_pipeline_registration(identity, context=prod)['resolution'] == 'Promoted'
    assert len(rows) == 2 and {row['pipeline_id'] for row in rows} == {identity}
    assert all('manifest_json' not in row for row in rows)


def test_independent_copy_gets_uuid_only_through_explicit_operation(registry):
    context, rows, *_ = registry
    identity = shared.resolve_pipeline_registration(context=context)['pipeline_id']
    copy = {**context, 'notebook_id': 'copy'}
    with pytest.raises(ValueError, match='another notebook'):
        shared.resolve_pipeline_registration(identity, context=copy)
    other = shared.resolve_pipeline_registration(context=copy, new_pipeline=True)
    assert other['pipeline_id'] != identity and len(rows) == 2
    with pytest.raises(ValueError, match='already owns'):
        shared.resolve_pipeline_registration(context=context, new_pipeline=True)


def test_concurrent_first_registration_cannot_commit_two_identities(registry, monkeypatch):
    context, rows, read, _commit = registry
    barrier = Barrier(2)
    def racing_read(**kwargs):
        value = read(**kwargs)
        barrier.wait()
        return value
    monkeypatch.setattr(shared, 'read_pipeline_registry', racing_read)
    def register():
        try:
            return shared.resolve_pipeline_registration(context=context)['pipeline_id']
        except RuntimeError:
            return None
    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(lambda _: register(), range(2)))
    assert len(rows) == 1 and results.count(None) == 1
    monkeypatch.setattr(shared, 'read_pipeline_registry', read)
    assert shared.resolve_pipeline_registration(context=context)['pipeline_id'] == rows[0]['pipeline_id']


@pytest.mark.parametrize('conflict', ['logical', 'notebook'])
def test_duplicate_bindings_fail_closed(monkeypatch, conflict):
    identity = str(uuid4())
    rows = [{'pipeline_id': 'central', 'environment_name': '*', 'registration_status': 'Authority', 'registry_token': 'one'},
            {'pipeline_id': identity, 'environment_name': 'Development', 'workspace_id': 'w', 'notebook_id': 'n', 'registration_status': 'Active'},
            {'pipeline_id': identity if conflict == 'logical' else str(uuid4()), 'environment_name': 'Development',
             'workspace_id': 'w', 'notebook_id': 'n', 'registration_status': 'Active'}]
    monkeypatch.setattr(shared, 'resolve_fabric_context', lambda **kwargs: ({}, 'Development', {}))
    from fabricops_kit.activated_pipeline import shared as authority
    monkeypatch.setattr(authority, 'authority_records', lambda **kw: {'token': 'one', 'registrations': rows[1:]})
    with pytest.raises(ValueError, match='Ambiguous'):
        shared.read_pipeline_registry(context={})


def test_live_cannot_allocate_an_unbound_identity(registry, monkeypatch):
    context, rows, *_ = registry
    create_uuid = Mock(side_effect=AssertionError('Live must not generate a UUID'))
    monkeypatch.setattr(shared, 'uuid4', create_uuid)
    with pytest.raises(ValueError, match='Live requires an existing'):
        shared.resolve_pipeline_registration(context=context, allow_new_identity=False)
    assert rows == []
    create_uuid.assert_not_called()


def test_live_recovers_registered_identity_without_mutation(registry, monkeypatch):
    context, rows, *_ = registry
    identity = shared.resolve_pipeline_registration(context=context)['pipeline_id']
    before = deepcopy(rows)
    monkeypatch.setattr(shared, 'uuid4', Mock(side_effect=AssertionError('unexpected UUID')))
    recovered = shared.resolve_pipeline_registration(context=context, allow_new_identity=False)
    assert recovered['pipeline_id'] == identity and recovered['resolution'] == 'Recovered'
    assert rows == before



def test_explicit_promotion_preserves_registration_semantics_without_new_identity(registry, monkeypatch):
    context, rows, *_ = registry
    identity = shared.resolve_pipeline_registration(context=context)['pipeline_id']
    prod = {**context, 'env': 'Production', 'workspace_id': 'workspace-prod', 'notebook_id': 'promoted'}
    monkeypatch.setattr(shared, 'uuid4', Mock(side_effect=AssertionError('unexpected UUID')))
    promoted = shared.resolve_pipeline_registration(identity, context=prod, allow_new_identity=False)
    assert promoted['pipeline_id'] == identity and promoted['resolution'] == 'Promoted'
    assert len(rows) == 2 and {row['pipeline_id'] for row in rows} == {identity}
