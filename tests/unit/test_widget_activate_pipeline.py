"""Activation inspection cannot revive the removed approval workflow."""
import importlib
from copy import deepcopy
import pytest

from fabricops_kit.activated_pipeline import shared as service
from tests.unit.test_activated_pipeline import contract_candidate

module = importlib.import_module("fabricops_kit.widgets.widget_activate_pipeline")


def test_widget_is_read_only_and_explicitly_blocks_deployment_assurance(monkeypatch):
    """Opening Governance UI neither authorizes a SHA nor mutates candidates."""
    rows = [service.empty_pipeline_authority(), contract_candidate()]
    before = deepcopy(rows)
    context = {"config": {}, "scope_workspace_id": "DEV"}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: ({}, "DEV", context or {}))
    monkeypatch.setattr(module, "get_spark_session", lambda **kw: object())
    monkeypatch.setattr(module, "read_registry", lambda **kw: rows)
    from IPython import display as ip
    monkeypatch.setattr(ip, "display", lambda *args, **kwargs: None)
    rendered = module.widget_activate_pipeline(context=context)
    assert rendered["ready"] is False and "trusted deployment verification" in rendered["reason"]
    assert rendered["token"] == rows[0]["token"] and rendered["records"] == rows[1:]
    assert rows == before
    assert "perform_activation" not in rendered
