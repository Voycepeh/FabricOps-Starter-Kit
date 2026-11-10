"""Pipeline-owned profiling validation and immutable promotion parameters."""
# ruff: noqa: D103
import importlib
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from fabricops_kit.pipeline.shared import validate_pipeline_profiling

setup = importlib.import_module('fabricops_kit.pipeline.setup_pipeline')
shared = importlib.import_module('fabricops_kit.pipeline.shared')
activation = importlib.import_module('fabricops_kit.activated_pipeline.shared')


@pytest.mark.parametrize('overrides', [{}, {'profiling_enabled': False, 'grain_discovery_enabled': True,
    'frequency_enabled': True, 'profiling_interval_days': 7, 'profiling_max_rows': 500}])
def test_setup_stores_pipeline_configuration(monkeypatch, overrides):
    session = SimpleNamespace(plan=SimpleNamespace(evidence={}))
    monkeypatch.setattr(shared, 'start_pipeline_session', lambda *a, **kw: session)
    assert setup.setup_pipeline(**overrides) is session
    assert session.plan.evidence['profiling_configuration'] == validate_pipeline_profiling(overrides)


@pytest.mark.parametrize('name,values', [
    ('profiling_enabled', [None, 0, 1, 'true']),
    ('grain_discovery_enabled', [None, 0, 1, 'true']),
    ('frequency_enabled', [None, 0, 1, 'true']),
    ('profiling_interval_days', [None, True, False, 0, -1, 1.5, '1']),
    ('profiling_max_rows', [True, False, 0, -1, 1.5, '1']),
])
def test_invalid_setup_rejected_before_start(monkeypatch, name, values):
    start = Mock()
    monkeypatch.setattr(shared, 'start_pipeline_session', start)
    for value in values:
        with pytest.raises(ValueError, match=name):
            setup.setup_pipeline(**{name: value})
    start.assert_not_called()


def test_governed_configuration_cannot_override_approved_settings(monkeypatch):
    approved = {'manual': False, 'days': None, **validate_pipeline_profiling({'profiling_max_rows': 100})}
    session = SimpleNamespace(plan=SimpleNamespace(evidence={'approved_parameters': approved}), close=Mock())
    monkeypatch.setattr(shared, 'start_pipeline_session', lambda *a, **kw: session)
    with pytest.raises(RuntimeError, match='parameter overrides'):
        setup.setup_pipeline(pipeline_mode='Governed', profiling_max_rows=200)
    session.close.assert_called_once_with(failed=True)
    setup.setup_pipeline(pipeline_mode='Governed', profiling_max_rows=100)
    assert session.plan.evidence['profiling_configuration']['profiling_max_rows'] == 100


def test_promotion_freezes_all_profiling_parameters():
    # promoted_notebook performs the same saved-literal extraction used for approval.
    notebook = {'cells': [{'cell_type': 'code', 'source': 'pipeline = setup_pipeline(pipeline_mode="Dry Run", profiling_enabled=False, grain_discovery_enabled=True, frequency_enabled=True, profiling_interval_days=3, profiling_max_rows=17)'}]}
    cloned, parameters = activation.promoted_notebook(json.dumps(notebook))
    assert parameters == {'manual': False, 'days': None, **validate_pipeline_profiling({
        'profiling_enabled': False, 'grain_discovery_enabled': True, 'frequency_enabled': True,
        'profiling_interval_days': 3, 'profiling_max_rows': 17})}
    assert b'Governed' in cloned


def test_authoring_labels_sampled_column_counts():
    widget = importlib.import_module('fabricops_kit.widgets.widget_data_contract')
    rendered = widget._profile_html({'kind': 'profile', 'profile': {'profile_scope': 'bounded_selection',
        'profiling_max_rows': 10, 'row_count': 10, 'distinct_count': 10, 'distinct_percent': 100}})
    assert 'Sampled evidence' in rendered and 'full-table facts are unknown' in rendered
