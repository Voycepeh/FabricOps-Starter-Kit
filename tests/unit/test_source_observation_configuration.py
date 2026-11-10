"""Independent Source Drift setup and governed parameter identity."""
# ruff: noqa: D103
from importlib import import_module
from types import SimpleNamespace

import pytest
from fabricops_kit.pipeline import shared

setup = import_module('fabricops_kit.pipeline.setup_pipeline')


def test_source_drift_defaults_and_independent_pipeline_configuration(monkeypatch):
    session = SimpleNamespace(plan=SimpleNamespace(evidence={}))
    monkeypatch.setattr(shared, 'start_pipeline_session', lambda *a, **kw: session)
    setup.setup_pipeline()
    assert session.plan.evidence['source_drift_policy'] == {
        'source_drift_enabled': False, 'source_drift_interval_days': 1, 'source_drift_block': True}
    setup.setup_pipeline(pipeline_mode='Dry Run', profiling_enabled=False, profiling_max_rows=10,
        source_drift_enabled=True, source_drift_interval_days=7, source_drift_block=False)
    assert session.plan.evidence['source_drift_policy'] == {
        'source_drift_enabled': True, 'source_drift_interval_days': 7, 'source_drift_block': False}
    assert session.plan.evidence['pipeline_parameters'] == {
        **session.plan.evidence['profiling_configuration'], **session.plan.evidence['source_drift_policy']}
    assert 'source_observation_policy' not in session.plan.evidence


@pytest.mark.parametrize('name,values', [
    ('source_drift_enabled', [0, 1, 'true', None]), ('source_drift_block', [0, 1, 'true', None]),
    ('source_drift_interval_days', [None, True, False, 0, -1, '7', 1.5])])
def test_invalid_configuration_rejected_before_session_start(monkeypatch, name, values):
    monkeypatch.setattr(shared, 'start_pipeline_session', lambda *a, **kw: pytest.fail('session started'))
    for value in values:
        with pytest.raises(ValueError, match=name):
            setup.setup_pipeline(**{name: value})


@pytest.mark.parametrize('name', ['observe_source', 'source_observation_days'])
def test_obsolete_controls_have_no_aliases(name):
    with pytest.raises(TypeError, match=name):
        setup.setup_pipeline(**{name: True})


def test_historical_append_receipts_remain_verifiable_without_strategy_alias(monkeypatch):
    monkeypatch.setattr(shared, 'read_warehouse_query', lambda *a, **kw:
                        SimpleNamespace(first=lambda: {'fabricops_publication_rows': 1}))
    receipt = dict(strategy='append', activity_id='historical', committed_at='2026-01-01T00:00:00+00:00', input_rows=1)
    assert shared._physical_target_has_publication(dict(store_type='warehouse', store='Silver', schema='dbo', table_name='target'), receipt, context={})
    with pytest.raises(ValueError, match='invalid load_strategy'):
        shared.validated_processing({'load_strategy': 'append'})


@pytest.mark.parametrize('name,value', [('source_drift_enabled', False), ('source_drift_interval_days', 8), ('source_drift_block', True)])
def test_governed_source_drift_overrides_cannot_change_approved_behavior(monkeypatch, name, value):
    from unittest.mock import Mock
    approved = {**shared.validate_pipeline_profiling(), **shared.validate_source_drift_configuration({
        'source_drift_enabled': True, 'source_drift_interval_days': 7, 'source_drift_block': False})}
    session = SimpleNamespace(plan=SimpleNamespace(evidence={'approved_parameters': approved}), close=Mock())
    monkeypatch.setattr(shared, 'start_pipeline_session', lambda *a, **kw: session)
    requested = {key: approved[key] for key in ('source_drift_enabled', 'source_drift_interval_days', 'source_drift_block')}
    setup.setup_pipeline(pipeline_mode='Governed', **requested)
    requested[name] = value
    with pytest.raises(RuntimeError, match='parameter overrides'):
        setup.setup_pipeline(pipeline_mode='Governed', **requested)
    session.close.assert_called_once_with(failed=True)
