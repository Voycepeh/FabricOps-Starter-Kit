"""Test documentation notebook links for MkDocs strict compatibility."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
NOTEBOOK_TEMPLATES_PAGE = ROOT / "docs" / "how-fabricops-works" / "notebook-templates.md"
GITHUB_NOTEBOOK_BASE_URL = (
    "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/"
)

NOTEBOOK_LINKS = (
    "00_env_config.ipynb",
    "01_agreement.ipynb",
    "02_pipeline.ipynb",
    "03_governance.ipynb",
    "99_explore.ipynb",
    "example_pipeline_demo.ipynb",
    "example_dq_rule_smoke_test.ipynb",
)


def test_template_notebook_links_use_github_urls() -> None:
    """Keep notebook links out of MkDocs local markdown validation."""
    text = NOTEBOOK_TEMPLATES_PAGE.read_text(encoding="utf-8")

    assert "../../templates/notebooks/" not in text
    for notebook in NOTEBOOK_LINKS:
        assert f"{GITHUB_NOTEBOOK_BASE_URL}{notebook}" in text


def test_template_notebook_page_has_no_relative_ipynb_links() -> None:
    """Prevent MkDocs strict mode from treating template notebooks as missing docs pages."""
    text = NOTEBOOK_TEMPLATES_PAGE.read_text(encoding="utf-8")
    markdown_links = re.findall(r"\[[^\]]+\]\(([^)]+\.ipynb)\)", text)

    assert markdown_links
    assert all(link.startswith("https://github.com/") for link in markdown_links)
