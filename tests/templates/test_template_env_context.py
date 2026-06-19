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


LEGACY_ENV_VARIABLE = "ENV" + "_NAME"
LEGACY_ENV_CONTEXT_KEY = "env" + "_name"
LEGACY_CONTEXT_FIELDS = ("enrichment_context_extra" + "_fields", "enrichment_classification_extra" + "_fields")
REMOVED_CONTEXT_ALIAS = "NOTEBOOK" + "_CONTEXT"


def test_template_notebooks_do_not_define_legacy_environment_variable():  # noqa: D103
    for path in NOTEBOOK_DIR.glob("*.ipynb"):
        text = _notebook_text(path.name)

        assert LEGACY_ENV_VARIABLE not in text


def test_00_env_config_owns_env_context_definition():  # noqa: D103
    text = _notebook_text("00_env_config.ipynb")

    assert 'ENV = "dev"' in text
    assert "FABRIC_CONTEXT" in text
    assert '"env": ENV' in text
    assert f'"{LEGACY_ENV_CONTEXT_KEY}": ENV' not in text
    assert REMOVED_CONTEXT_ALIAS not in text
    assert "notebook_context" in text
    assert "RUN_CONTEXT.runtime_metadata" in text


def test_00_env_config_uses_governance_widget_custom_fields():  # noqa: D103
    text = _notebook_text("00_env_config.ipynb")

    assert "GOVERNANCE_CONFIG = GovernanceConfig(" in text
    assert "enrichment_context_widget=" in text
    assert "enrichment_classification_widget=" in text
    assert '"custom_fields"' in text
    assert '"key": "business_owner_notes"' in text
    assert '"key": "retention_class"' in text
    assert all(field_name not in text for field_name in LEGACY_CONTEXT_FIELDS)


@pytest.mark.parametrize("name", DOWNSTREAM_NOTEBOOKS)
def test_downstream_templates_do_not_reference_legacy_environment_context(name: str):  # noqa: D103
    text = _notebook_text(name)

    assert f'{LEGACY_ENV_VARIABLE} = FABRIC_CONTEXT["{LEGACY_ENV_CONTEXT_KEY}"]' not in text
    assert f'FABRIC_CONTEXT["{LEGACY_ENV_CONTEXT_KEY}"]' not in text
    assert f'FABRIC_CONTEXT.get("{LEGACY_ENV_CONTEXT_KEY}")' not in text
    assert f"{LEGACY_ENV_VARIABLE} = ENV" not in text
