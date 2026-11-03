"""Stable explicit logical pipeline identities without permanent registrations."""
from uuid import uuid4
from unittest.mock import Mock
import pytest

from fabricops_kit import setup_pipeline
from fabricops_kit.pipeline import shared


@pytest.mark.parametrize("mode", ["Ungoverned", "Governed"])
def test_persistent_setup_requires_saved_pipeline_id(mode):
    """Persistent identity is not automatically recovered from a notebook."""
    with pytest.raises(ValueError, match="explicit stable pipeline_id"):
        setup_pipeline(pipeline_mode=mode)


def test_saved_pipeline_id_is_independent_of_deployment(monkeypatch):
    """Identical Pipeline IDs pass unchanged across notebook/environment promotion."""
    launch = Mock(return_value=object())
    monkeypatch.setattr(shared, "start_pipeline_session", launch)
    identity = str(uuid4())
    setup_pipeline(pipeline_id=identity, pipeline_mode="Ungoverned")
    assert launch.call_args.args == (identity, "Ungoverned")
    setup_pipeline(pipeline_mode="Dry Run")
    assert launch.call_args.args == (None, "Dry Run")


@pytest.mark.parametrize("removed", ["new_pipeline", "previous_workspace_id", "previous_notebook_id"])
def test_registration_arguments_are_removed(removed):
    """Removed lifecycle inputs are not compatibility aliases."""
    with pytest.raises(TypeError):
        setup_pipeline(**{removed: True})


def test_no_registration_runtime_helpers_remain():
    """Registration persists only in retained migration evidence."""
    for name in ("resolve_pipeline_registration", "commit_pipeline_registration", "read_pipeline_registry", "validate_pipeline_registrations"):
        assert not hasattr(shared, name)
