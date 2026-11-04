"""Fabric notebook identity is resolved internally through promotion Registry rows."""
# ruff: noqa: D103
from types import SimpleNamespace
from unittest.mock import ANY, Mock

from fabricops_kit import setup_pipeline
from fabricops_kit.pipeline import shared


def test_pipeline_id_is_not_a_public_setup_argument():
    """Pipeline identity is resolved internally rather than supplied by callers."""
    import inspect
    assert "pipeline_id" not in inspect.signature(setup_pipeline).parameters


def test_setup_delegates_identity_resolution_to_registry(monkeypatch):
    launch = Mock(return_value=SimpleNamespace(plan=SimpleNamespace(evidence={})))
    monkeypatch.setattr(shared, "start_pipeline_session", launch)
    monkeypatch.setattr(shared, "get_default_fabric_context", lambda **kwargs: {
        "config": {}, "scope_workspace_id": "dev", "notebook_id": "00000000-0000-4000-8000-000000000001"})
    activation = __import__("fabricops_kit.activated_pipeline.shared", fromlist=["resolve_pipeline_identity"])
    monkeypatch.setattr(activation, "resolve_pipeline_identity", lambda **kwargs: (
        "00000000-0000-4000-8000-000000000001", {"role": "source", "row": None}))
    setup_pipeline(pipeline_mode="Ungoverned")
    launch.assert_called_once_with("Ungoverned", inspector=ANY)


def test_fabric_notebook_guid_is_valid_identity():
    assert shared.validate_pipeline_id("00000000-0000-4000-8000-000000000001") == "00000000-0000-4000-8000-000000000001"


def test_no_registration_runtime_helpers_remain():
    for name in ("resolve_pipeline_registration", "commit_pipeline_registration", "read_pipeline_registry", "validate_pipeline_registrations"):
        assert not hasattr(shared, name)
