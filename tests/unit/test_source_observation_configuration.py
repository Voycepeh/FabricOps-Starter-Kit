"""Pipeline-level observation configuration has no Data Contract prerequisites."""
# ruff: noqa: D103
from importlib import import_module
from types import SimpleNamespace

import pytest
from fabricops_kit.pipeline import shared

setup = import_module('fabricops_kit.pipeline.setup_pipeline')


def test_manual_and_interval_settings_are_owned_by_pipeline(monkeypatch):
    session = SimpleNamespace(plan=SimpleNamespace(evidence={}))
    monkeypatch.setattr(shared, 'start_pipeline_session', lambda *a, **kw: session)
    assert setup.setup_pipeline(pipeline_mode='Dry Run', observe_source=True, source_observation_days=7) is session
    assert session.plan.evidence['source_observation_policy'] == {'manual': True, 'days': 7}
    setup.setup_pipeline(pipeline_mode='Dry Run')
    assert session.plan.evidence['source_observation_policy'] == {'manual': False, 'days': None}


@pytest.mark.parametrize('days', [0, -1, True, '7', 1.5])
def test_invalid_intervals_fail_before_session_start(monkeypatch, days):
    monkeypatch.setattr(shared, 'start_pipeline_session', lambda *a, **kw: pytest.fail('session started'))
    with pytest.raises(ValueError, match='positive integer'):
        setup.setup_pipeline(pipeline_mode='Dry Run', source_observation_days=days)


def test_manual_trigger_is_strict_boolean():
    with pytest.raises(ValueError, match='boolean'):
        setup.setup_pipeline(pipeline_mode='Dry Run', observe_source='yes')
