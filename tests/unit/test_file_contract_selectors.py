"""File authoring uses readable dataset selection without Catalogue table aliases."""
# ruff: noqa: D103
import json
from types import SimpleNamespace
from unittest.mock import Mock

from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.pipeline import shared as pipeline
from tests.unit.test_widget_data_contract import widget_runtime  # noqa: F401


def test_unobserved_file_discovered_from_successful_pipeline_without_reading(widget_runtime, monkeypatch):  # noqa: F811
    source = contracts.file_source_identity(workspace_id="dev", item_id="item",
        relative_path="demo/orders.csv", file_format="csv",
        reader_options={"header": True, "inferSchema": True})
    run = {"completed_at": "2026-11-12T10:00:00Z", "operations": json.dumps([{
        "pipeline_role": "source", "source_type": "file", "source_id": source["source_id"],
        "status": "succeeded", "destination": {
            **{key: source[key] for key in ("workspace_id", "item_id", "relative_path", "file_format")},
            "reader_options_json": json.dumps(source["reader_options"])},
        "observed_columns_json": json.dumps([{"column_name": "id", "data_type": "int"}])
    }])}
    from tests.unit.test_widget_data_contract import module
    import fabricops_kit.config.shared as config_shared
    monkeypatch.setattr(config_shared, "get_store", lambda config, route, key: SimpleNamespace(workspace_id="dev", item_id="item"))
    monkeypatch.setattr(module.contracts, "list_contract_governance_state",
        lambda **kwargs: {"tables": [], "contracts": [], "pipeline_runs": [run]})
    state = module.widget_data_contract()
    labels = {value: label for label, value in state["_controls"]["table"].options}
    assert source["source_id"] in labels
    assert "demo/orders.csv" in labels[source["source_id"]]
    assert "select_file" not in state["_controls"]
    assert "file_path" not in state["_controls"]


def test_file_and_table_names_are_distinct_and_filter_by_physical_workspace():
    table = {'table_id': 'table-orders', 'workspace_id': 'w', 'table_name': 'orders', 'metadata_level': 'table', 'layer': 'Bronze', 'schema_name': 'demo'}
    source = contracts.file_source_identity(workspace_id='w', item_id='i', relative_path='demo/orders.csv', file_format='csv')
    source['store'] = 'Bronze'
    options = contracts.dataset_selector_options([table], [source], workspace_id='w')
    assert set(options['tables']) == {'table-orders', source['source_id']}
    assert contracts.dataset_selector_options([table], [source], workspace_id='other')['tables'] == []
    assert 'Table' in contracts.dataset_display_name(table)
    assert 'demo/orders.csv' in contracts.dataset_display_name(source)


def test_authored_file_keeps_physical_identity_and_separate_configuration_route(monkeypatch):
    import fabricops_kit.config.shared as config_shared
    source = contracts.file_source_identity(workspace_id='physical-source', item_id='item', relative_path='demo/orders.csv', file_format='csv')
    stores = {'gov': {'Metadata': SimpleNamespace(workspace_id='gov', item_id='meta')},
              'engineering': {'Bronze': SimpleNamespace(workspace_id='physical-source', item_id='item')}}
    monkeypatch.setattr(config_shared, 'get_store', lambda config, route, key: stores[route][key])
    rows = [{'source_id': source['source_id'], 'contract_version': 1,
             'contract_payload_json': json.dumps({'source': source, 'table': {'columns': []}})}]
    datasets = contracts.contract_file_datasets(rows, config={'path_config': {'paths': stores}}, workspace_id='gov')
    assert len(datasets) == 1
    assert datasets[0]['configuration_workspace_id'] == 'engineering'
    assert datasets[0]['workspace_id'] == 'physical-source'
    assert datasets[0]['source_id'] == source['source_id']
    assert 'table_id' not in datasets[0]
