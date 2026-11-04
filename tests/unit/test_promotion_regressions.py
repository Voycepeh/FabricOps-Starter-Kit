"""Physical routing and retry safety across consumers and Pipeline Promotion."""
from copy import deepcopy
from datetime import date
import hashlib
import json
from types import SimpleNamespace

import pytest

from fabricops_kit.activated_pipeline import shared as authority
from fabricops_kit.pipeline import shared as pipeline
from fabricops_kit.data_agent import shared as agent
from fabricops_kit.config import FabricStore, FrameworkConfig, PathConfig
from tests.unit.test_activated_pipeline import operation, promotion


def _config(dev_schema='demo', prod_schema='demo', item='item-B', physical_workspace='DEV'):
    metadata = FabricStore(workspace_id='CENTRAL', item_id='metadata', kind='lakehouse', schema_enabled=True, schema='engineering')
    return FrameworkConfig(path_config=PathConfig(paths={
        'DEV': {'Gold': FabricStore(workspace_id=physical_workspace, item_id=item, kind='warehouse', schema='demo'),
                'Silver': FabricStore(workspace_id='DEV', item_id='silver-dev', kind='lakehouse', schema_enabled=True, schema=dev_schema), 'Metadata': metadata},
        'PROD': {'Silver': FabricStore(workspace_id='PROD', item_id='silver-prod', kind='lakehouse', schema_enabled=True, schema=prod_schema), 'Metadata': metadata},
    }))


@pytest.fixture
def consumer_metadata(monkeypatch):
    """Keep consumer validation real while supplying registered metadata records."""
    binding = dict(workspace_id='DEV', item_id='item-A', kind='warehouse', schema='demo', table_name='orders')
    payload = json.dumps({'table': {'table_id': 'orders', 'columns': []}, 'enrichment': {}, 'guardrails': []})
    contract = dict(table_id='orders', contract_id='contract', contract_version=1, status='frozen', contract_payload_json=payload)
    activation = dict(workspace_id='DEV', table_id='orders', contract_id='contract', contract_version=1,
        payload_sha256=hashlib.sha256(payload.encode()).hexdigest(), activation_id='activation', revision=1,
        status='active', destination_json=json.dumps(binding), activated_by='reviewer', activated_at=date.today())
    op = operation(); op['destination'] = binding
    row = promotion(); row.update(operations_json=json.dumps([op]), bindings_sha256=authority.manifest_digest([op]))
    agreement = dict(agreement_id='agreement', agreement_version='1', start_date=date(2020,1,1), expiry_date=date(2099,1,1))
    row.update(agreement_id='agreement', agreement_version='1', agreement_sha256=authority.manifest_digest(authority.agreement_definition(agreement)))
    tables = {authority.ACTIVATION_TABLE: [activation], authority.REGISTRY_TABLE: [row],
        'METADATA_DATA_CONTRACT': [contract], 'METADATA_DATA_AGREEMENT': [agreement]}
    monkeypatch.setattr(authority, 'metadata_records', lambda table, **kw: deepcopy(tables[table]))
    monkeypatch.setattr(agent, 'resolve_catalogue_table_identity', lambda *a, **kw: dict(table_id='orders', layer='Gold', store_type='warehouse', schema='demo', table_name='orders'))
    return SimpleNamespace(binding=binding, activation=activation, row=row, op=op)


def test_consumer_rejects_unreviewed_item_binding(consumer_metadata):
    """Identical logical IDs cannot reuse an approval for a different physical item."""
    with pytest.raises(ValueError, match='physical binding differs'):
        agent.consumer_context(_config(item='item-B'), 'orders', workspace_id='DEV')


def test_consumer_accepts_exact_physical_binding(consumer_metadata):
    """The approved datasource and exact frozen Contract remain usable."""
    result = agent.consumer_context(_config(item='item-A'), 'orders', workspace_id='DEV')
    assert result['source']['item_id'] == 'item-A'
    assert result['contract']['agreement_id'] == 'agreement'


def test_consumer_uses_physical_workspace_for_remote_contract(consumer_metadata):
    """Remote store routing selects its physical activation without changing execution scope."""
    fixture = consumer_metadata
    fixture.binding['workspace_id'] = 'REMOTE'
    fixture.activation.update(workspace_id='REMOTE', destination_json=json.dumps(fixture.binding))
    fixture.op['destination'] = dict(fixture.binding)
    fixture.row.update(operations_json=json.dumps([fixture.op]), bindings_sha256=authority.manifest_digest([fixture.op]))
    result = agent.consumer_context(_config(item='item-A', physical_workspace='REMOTE'), 'orders', workspace_id='DEV')
    assert result['source']['workspace_id'] == 'REMOTE'


def test_claim_cleanup_retries_only_remaining_targets(monkeypatch):
    """A completed target's transferred ownership never blocks releasing another target."""
    destinations = [operation(table='A')['destination'], operation(table='B')['destination']]
    owners, calls = {'A': 'old-run', 'B': 'old-run'}, []
    failed = False
    def claim(owner, destination, **kw):
        nonlocal failed
        table = destination['table_name']; calls.append(table)
        if table == 'B' and not failed:
            failed = True
            raise RuntimeError('Concurrent Delta modification')
        assert owners.get(table) == owner
        owners.pop(table)
    monkeypatch.setattr(authority, 'publication_claim', claim)
    plan = SimpleNamespace(plan_id='old-run', runtime_context={}, evidence=dict(sealed=True, lease_token='old-run', publication_claims=destinations))
    with pytest.raises(RuntimeError, match='Concurrent'):
        authority.release_pipeline_lease(plan)
    assert [binding['table_name'] for binding in plan.evidence['publication_claims']] == ['B']
    owners['A'] = 'new-run'
    authority.release_pipeline_lease(plan)
    assert owners == {'A': 'new-run'} and calls == ['A', 'B', 'B']
    assert 'lease_token' not in plan.evidence


def test_default_schema_and_table_identity_use_destination():
    """A saved None schema uses the destination default rather than the observed source schema."""
    cfg = _config(dev_schema='development', prod_schema='production')
    identity = pipeline.resolve_physical_table_identity(cfg, 'DEV', store='Silver', schema=None, table_name='orders')
    binding = pipeline.pipeline_physical_bindings({identity['table_id']: identity}, config=cfg, workspace_id='DEV')[identity['table_id']]
    op = operation(role='source'); op.update(table_id=identity['table_id'], destination=binding, requested_schema=None)
    resolved = authority.resolve_promoted_operations([op], context={'config':cfg, 'scope_workspace_id':'PROD'})
    expected = pipeline.resolve_physical_table_identity(cfg, 'PROD', store='Silver', schema=None, table_name='orders')
    assert resolved[0]['destination']['schema'] == 'production'
    assert resolved[0]['table_id'] == expected['table_id']
    assert resolved[0]['table_id'] != identity['table_id']
    assert authority.resolve_promoted_operations(resolved, context={'config':cfg, 'scope_workspace_id':'PROD'}) == resolved


def test_explicit_schema_stays_explicit_across_workspaces():
    """Explicit notebook schemas are not replaced by a configured default."""
    cfg = _config(dev_schema='development', prod_schema='production')
    identity = pipeline.resolve_physical_table_identity(cfg, 'DEV', store='Silver', schema='fixed', table_name='orders')
    binding = pipeline.pipeline_physical_bindings({identity['table_id']: identity}, config=cfg, workspace_id='DEV')[identity['table_id']]
    op = operation(role='source'); op.update(table_id=identity['table_id'], destination=binding, requested_schema='fixed')
    resolved = authority.resolve_promoted_operations([op], context={'config':cfg, 'scope_workspace_id':'PROD'})
    assert resolved[0]['destination']['schema'] == 'fixed'
    assert resolved[0]['table_id'] == identity['table_id']


def test_schema_resolution_keeps_source_and_incremental_target_references_consistent():
    """Physical default changes remap operation references as well as participant IDs."""
    cfg = _config(dev_schema='development', prod_schema='production')
    ops = []
    for role, table in [('source','incoming'), ('target','output')]:
        identity = pipeline.resolve_physical_table_identity(cfg, 'DEV', store='Silver', schema=None, table_name=table)
        binding = pipeline.pipeline_physical_bindings({identity['table_id']: identity}, config=cfg, workspace_id='DEV')[identity['table_id']]
        op = operation(role=role, table=table); op.update(table_id=identity['table_id'], destination=binding, requested_schema=None)
        ops.append(op)
    ops[0]['incremental_target_table_id'] = ops[1]['table_id']
    ops[1]['source_table_ids'] = [ops[0]['table_id']]
    resolved = authority.resolve_promoted_operations(ops, context={'config':cfg, 'scope_workspace_id':'PROD'})
    assert resolved[0]['incremental_target_table_id'] == resolved[1]['table_id']
    assert resolved[1]['source_table_ids'] == [resolved[0]['table_id']]


def test_consumer_rejects_agreement_for_a_different_physical_item(consumer_metadata):
    """An exact active Contract cannot borrow an Agreement covering another destination."""
    fixture = consumer_metadata
    fixture.activation['destination_json'] = json.dumps({**fixture.binding, 'item_id': 'item-B'})
    with pytest.raises(ValueError, match='Agreement covers this consumer physical binding'):
        agent.consumer_context(_config(item='item-B'), 'orders', workspace_id='DEV')
