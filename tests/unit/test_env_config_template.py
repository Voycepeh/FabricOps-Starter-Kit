"""Regression tests for the shared 00_env_config notebook template."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def _env_config_source() -> str:
    notebook = json.loads(Path("templates/notebooks/00_env_config.ipynb").read_text(encoding="utf-8"))
    return "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])


def test_env_config_derives_runtime_setup_from_declared_paths() -> None:
    """Changing logical store names should not require edits later in the notebook."""
    source = _env_config_source()

    assert "REQUIRED_TARGETS =" not in source
    assert 'CONFIG.path_config.paths[ENV]["source"]' not in source
    assert "ACTIVE_STORE" not in source
    assert "required_targets=list(CONFIG.path_config.paths[ENV])" in source


def test_env_config_leaves_metadata_schema_routing_to_framework() -> None:
    """Canonical metadata writers should own governance versus engineering schema routing."""
    source = _env_config_source()

    assert "metadata_schema=" not in source
    assert "VALIDATION_MODE" not in source
    assert '"notebook_context"' not in source
    assert '"runtime_metadata": RUN_CONTEXT.runtime_metadata' in source
    assert "governance_metadata_schema" in source
    assert "engineering_metadata_schema" in source
