"""File authoring uses readable dataset selection without Catalogue table aliases."""
# ruff: noqa: D103
import json
from types import SimpleNamespace
from unittest.mock import Mock

from fabricops_kit.data_contract import shared as contracts
from fabricops_kit.pipeline import shared as pipeline
from tests.unit.test_widget_data_contract import widget_runtime  # noqa: F401


def test_unobserved_file_selection_observes_schema_and_offers_existing_editor(widget_runtime, monkeypatch):  # noqa: F811
    source = contracts.file_source_identity(workspace_id='dev', item_id='item', relative_path='demo/orders.csv',
                                            file_format='csv', reader_options={'header': True, 'inferSchema': True})
    monkeypatch.setattr(pipeline, 'resolve_file_participant', lambda **kw: {**source, 'store': 'Bronze'})
    field = SimpleNamespace(name='id', dataType=SimpleNamespace(simpleString=lambda: 'int'))
    reader = Mock(return_value={'dataframe': SimpleNamespace(schema=SimpleNamespace(fields=[field]))})
    monkeypatch.setattr(pipeline, 'read_file_participant', reader)
    state = widget_runtime['start']()
    controls = state['_controls']
    controls['file_path'].value = 'demo/orders.csv'
    controls['select_file'].click()
    assert state['pending_source_id'] == source['source_id']
    assert state['pending_table_id'] is None
    assert state['workspace_id'] == 'dev'
    labels = dict((value, label) for label, value in controls['table'].options)
    assert 'demo/orders.csv' in labels[source['source_id']] and 'File' in labels[source['source_id']]
    assert source['source_id'] not in labels[source['source_id']]
    assert controls['contract'].value == 'new'
    assert all(row.get('table_id') != source['source_id'] for row in state['tables'])
    reader.assert_called_once()


def test_file_and_table_names_are_distinct_and_filter_by_physical_workspace():
    table = {'table_id': 'table-orders', 'workspace_id': 'w', 'table_name': 'orders', 'metadata_level': 'table', 'layer': 'Bronze', 'schema_name': 'demo'}
    source = contracts.file_source_identity(workspace_id='w', item_id='i', relative_path='demo/orders.csv', file_format='csv')
    source['store'] = 'Bronze'
    options = contracts.dataset_selector_options([table], [source], workspace_id='w')
    assert set(options['tables']) == {'table-orders', source['source_id']}
    assert contracts.dataset_selector_options([table], [source], workspace_id='other')['tables'] == []
    assert 'Table' in contracts.dataset_display_name(table)
    assert 'demo/orders.csv' in contracts.dataset_display_name(source)
