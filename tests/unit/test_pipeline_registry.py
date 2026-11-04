"""Fabric notebook identity is resolved internally through promotion Registry rows."""
from types import SimpleNamespace
from unittest.mock import ANY, Mock
import pytest

from fabricops_kit import setup_pipeline
from fabricops_kit.pipeline import shared


def test_persistent_setup_does_not_accept_pipeline_id():
    with pytest.raises(TypeError):
        setup_pipeline(pipeline_id="00000000-0000-4000-8000-000000000001")


def test_setup_delegates_identity_resolution_to_registry(monkeypatch):
    launch = Mock(return_value=SimpleNamespace(plan=SimpleNamespace(evidence={})))
    monkeypatch.setattr(shared, "start_pipeline_session", launch)
    setup_pipeline(pipeline_mode="Ungoverned")
    launch.assert_called_once_with("Ungoverned", inspector=ANY)


def test_fabric_notebook_guid_is_valid_identity():
    assert shared.validate_pipeline_id("00000000-0000-4000-8000-000000000001") == "00000000-0000-4000-8000-000000000001"


def test_no_registration_runtime_helpers_remain():
    for name in ("resolve_pipeline_registration", "commit_pipeline_registration", "read_pipeline_registry", "validate_pipeline_registrations"):
        assert not hasattr(shared, name)
