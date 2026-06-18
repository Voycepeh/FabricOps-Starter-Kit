"""Contract tests for centralized notebook environment context."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract

ROOT = Path(__file__).parents[2]
NOTEBOOK_DIR = ROOT / "templates" / "notebooks"
DOWNSTREAM_NOTEBOOKS = [
    "01_agreement.ipynb",
    "02_pipeline.ipynb",
    "03_governance.ipynb",
    "99_explore.ipynb",
]


def _notebook_text(name: str) -> str:
    notebook = json.loads((NOTEBOOK_DIR / name).read_text(encoding="utf-8"))
    return "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"])


def test_00_env_config_owns_env_name_definition():
    text = _notebook_text("00_env_config.ipynb")

    assert "ENV_NAME = ENV" in text
    assert "FABRIC_CONTEXT" in text


@pytest.mark.parametrize("name", DOWNSTREAM_NOTEBOOKS)
def test_downstream_templates_do_not_redefine_env_name(name: str):
    text = _notebook_text(name)

    assert 'ENV_NAME = FABRIC_CONTEXT["env_name"]' not in text
    assert "ENV_NAME = ENV" not in text
    assert "get_fabric_context(env_name=" not in text
