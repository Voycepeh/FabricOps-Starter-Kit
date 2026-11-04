"""Native Contract Activation review pins exact physical binding and frozen payload."""
import importlib
import hashlib
from unittest.mock import Mock

from tests.unit.test_activated_pipeline import operation


def test_reviewed_contract_binding_and_payload_are_passed_to_atomic_action(monkeypatch):
    """The checkbox authorizes only the exact displayed physical binding and frozen content."""
    module = importlib.import_module('fabricops_kit.widgets.widget_activate_data_contract')
    pipeline = importlib.import_module('fabricops_kit.pipeline.shared')
    from IPython import display as ip
    monkeypatch.setattr(ip, 'display', lambda *a, **kw: None)
    monkeypatch.setattr(module, 'resolve_fabric_context', lambda **kw: ({}, 'DEV', {}))
    monkeypatch.setattr(module, 'get_spark_session', lambda **kw: object())
    monkeypatch.setattr(module, 'read_activation_history', lambda **kw: [])
    contract = dict(table_id='orders', contract_id='contract', contract_version=1, status='frozen', contract_payload_json='{}')
    monkeypatch.setattr(module, 'metadata_records', lambda table, **kw: [contract] if table == 'METADATA_DATA_CONTRACT' else [])
    monkeypatch.setattr(pipeline, 'resolve_catalogue_table_identity', lambda *a, **kw: {'table_id': 'orders'})
    binding = operation()['destination']
    monkeypatch.setattr(pipeline, 'pipeline_physical_bindings', lambda *a, **kw: {'orders': binding})
    action = Mock(return_value={'status': 'active'})
    monkeypatch.setattr(module, 'set_table_contract_activation', action)
    ui = module.widget_activate_data_contract('orders', 'contract', 1)
    assert ui['destination'] == binding
    assert ui['controls']['activate'].disabled
    ui['actions']['review']()
    ui['controls']['confirm'].value = True
    assert ui['actions']['activate']()['status'] == 'active'
    assert action.call_args.kwargs['expected_destination'] == binding
    assert action.call_args.kwargs['expected_payload_sha256'] == hashlib.sha256(b'{}').hexdigest()


def test_explicit_physical_workspace_keeps_governance_metadata_routing(monkeypatch):
    """Governance can review a remote physical table without rerouting the central Metadata store."""
    module = importlib.import_module('fabricops_kit.widgets.widget_activate_data_contract')
    pipeline = importlib.import_module('fabricops_kit.pipeline.shared')
    from IPython import display as ip
    monkeypatch.setattr(ip, 'display', lambda *a, **kw: None)
    monkeypatch.setattr(module, 'resolve_fabric_context', lambda **kw: ({}, 'GOVERNANCE', {'metadata_workspace_id': 'CENTRAL'}))
    monkeypatch.setattr(module, 'get_spark_session', lambda **kw: object())
    observed = []
    def activations(**kwargs):
        observed.append(kwargs['context'])
        return []
    monkeypatch.setattr(module, 'read_activation_history', lambda **kw: [])
    monkeypatch.setattr(module, 'read_activation_history', activations)
    monkeypatch.setattr(module, 'metadata_records', lambda table, **kw: [dict(table_id='orders', contract_id='contract', contract_version=1, status='frozen', contract_payload_json='{}')] if table == 'METADATA_DATA_CONTRACT' else [])
    monkeypatch.setattr(pipeline, 'resolve_catalogue_table_identity', lambda *a, **kw: {'table_id': 'orders'})
    monkeypatch.setattr(pipeline, 'pipeline_physical_bindings', lambda *a, **kw: {'orders': operation(workspace=kw['workspace_id'])['destination']})
    ui = module.widget_activate_data_contract('orders', 'contract', 1, workspace_id='PROD')
    assert ui['destination']['workspace_id'] == 'PROD'
    assert observed[0]['scope_workspace_id'] == 'PROD'
    assert observed[0]['metadata_workspace_id'] == 'CENTRAL'


def test_no_argument_widget_selects_physical_table_and_frozen_version(monkeypatch):
    """The complete Governance workflow is available through the zero-argument interface."""
    module = importlib.import_module('fabricops_kit.widgets.widget_activate_data_contract')
    pipeline = importlib.import_module('fabricops_kit.pipeline.shared')
    from IPython import display as ip
    monkeypatch.setattr(ip, 'display', lambda *a, **kw: None)
    monkeypatch.setattr(module, 'resolve_fabric_context', lambda **kw: ({}, 'GOV', {'metadata_workspace_id': 'CENTRAL'}))
    monkeypatch.setattr(module, 'get_spark_session', lambda **kw: object())
    monkeypatch.setattr(module, 'read_activation_history', lambda **kw: [])
    data = {
        'METADATA_DATA_CATALOGUE': [dict(table_id='orders', workspace_id='DEV', metadata_level='table', is_active=True)],
        'METADATA_DATA_CONTRACT': [dict(table_id='orders', contract_id='contract', contract_version=2, status='frozen', contract_payload_json='{}')],
        'METADATA_DATA_AGREEMENT': [],
    }
    monkeypatch.setattr(module, 'metadata_records', lambda table, **kw: data[table])
    monkeypatch.setattr(pipeline, 'resolve_catalogue_table_identity', lambda *a, **kw: {'table_id': 'orders'})
    monkeypatch.setattr(pipeline, 'pipeline_physical_bindings', lambda *a, **kw: {'orders': operation()['destination']})
    action = Mock(return_value={'status': 'active'})
    monkeypatch.setattr(module, 'set_table_contract_activation', action)
    ui = module.widget_activate_data_contract()
    assert ui['controls']['workspace'].value is None
    ui['controls']['workspace'].value = 'DEV'
    ui['controls']['table'].value = 'orders'
    assert ui['controls']['contract'].value is None  # no latest-version fallback
    ui['controls']['contract'].value = ('contract', 2)
    ui['actions']['review']()
    ui['controls']['confirm'].value = True
    assert ui['actions']['activate']()['status'] == 'active'
    assert action.call_args.args == ('orders', 'contract', 2)
    ui['controls']['contract'].value = None
    assert ui['state']['review'] is None and ui['controls']['activate'].disabled
