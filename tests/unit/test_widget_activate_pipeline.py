"""Native widgets keep Governance decisions and Engineering deployment separate."""
# ruff: noqa: F811 -- shared pytest fixture imported for collection
import importlib
from unittest.mock import Mock

import pytest

from tests.unit.test_pipeline_handoff import authority, approved, package_candidate


def render(monkeypatch, module, context):
    """Render actual ipywidgets while replacing only runtime services."""
    from IPython import display as ip
    monkeypatch.setattr(ip, "display", lambda *a, **kw: None)
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: ({}, context_value["scope_workspace_id"], context_value))
    context_value = context
    monkeypatch.setattr(module, "get_spark_session", lambda **kw: object())


def test_governance_reviews_imported_json_without_engineering_session(authority, monkeypatch):
    """Opening and reviewing the actual widget never calls Engineering notebook APIs."""
    module = importlib.import_module("fabricops_kit.widgets.widget_activate_pipeline")
    render(monkeypatch, module, authority.gov)
    monkeypatch.setattr(module, "review_submission_policy", lambda *a, **kw: {"policy": "independently reviewed"})
    ui = module.widget_activate_pipeline(package=package_candidate())
    assert authority.tables[module.read_registry.__globals__["REGISTRY_TABLE"]] == []
    assert ui["ready"] is False
    assert ui["controls"]["decide"].disabled
    ui["actions"]["import"]()
    with pytest.raises(ValueError, match="Review"):
        ui["actions"]["decide"]()
    ui["actions"]["review"]()
    ui["controls"]["note"].value = "Reviewed code and test claims independently"
    ui["controls"]["confirm"].value = True
    result = ui["actions"]["decide"]()
    assert result["status"] == "approved" and result["decided_by"] == "reviewer"
    assert authority.tables["METADATA_PIPELINE_REGISTRY"] == []
    assert not any(name in ui["actions"] for name in ("promote", "deploy"))


def test_governance_decision_change_invalidates_review(authority, monkeypatch):
    """A different candidate, decision or filter requires another review."""
    module = importlib.import_module("fabricops_kit.widgets.widget_activate_pipeline")
    render(monkeypatch, module, authority.gov)
    monkeypatch.setattr(module, "review_submission_policy", lambda *a, **kw: {"policy": "independently reviewed"})
    ui = module.widget_activate_pipeline(package=package_candidate())
    ui["actions"]["import"]()
    ui["actions"]["review"]()
    ui["controls"]["confirm"].value = True
    assert not ui["controls"]["decide"].disabled
    ui["controls"]["decision"].value = "rejected"
    assert ui["state"]["review"] is None and ui["controls"]["decide"].disabled


def test_engineering_deployment_is_explicit_and_cannot_decide(authority, monkeypatch):
    """Engineering reviews persisted Governance authority in an independent widget session."""
    module = importlib.import_module("fabricops_kit.widgets.widget_deploy_pipeline")
    decision = approved(authority)
    render(monkeypatch, module, authority.eng)
    deploy = Mock(return_value={"status": "active"})
    monkeypatch.setattr(module, "deploy_approved_submission", deploy)
    ui = module.widget_deploy_pipeline(pipeline_id=decision["pipeline_id"])
    assert ui["controls"]["export"].disabled
    assert ui["controls"]["deploy"].disabled
    with pytest.raises(ValueError, match="Review"):
        ui["actions"]["deploy"]()
    ui["controls"]["approval"].value = decision["approval_id"]
    ui["actions"]["review"]()
    ui["controls"]["confirm"].value = True
    assert ui["actions"]["deploy"]()["status"] == "active"
    assert deploy.call_args.args == (decision["approval_id"],)
    assert "decide" not in ui["actions"]
