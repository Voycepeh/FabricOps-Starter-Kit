"""Validate the FabricOps release maintainer skill and human guide sync."""

from __future__ import annotations

import re
from pathlib import Path

from scripts import sync_maintainer_release_guide

ROOT = Path(__file__).parents[2]
SKILL = ROOT / ".agents" / "skills" / "fabricops-release" / "SKILL.md"
GUIDE = ROOT / "docs" / "maintainer" / "index.md"
ARCHITECTURE = ROOT / "docs" / "maintainer" / "public-api-architecture.md"
MKDOCS = ROOT / "mkdocs.yml"
README = ROOT / "README.md"
LLMS = ROOT / "docs" / "llms.txt"

REMOVED_MAINTAINER_PATHS = (
    "docs/maintainer/overview.md",
    "docs/maintainer/release-workflow.md",
    "docs/maintainer/generators.md",
    "maintainer/overview",
    "maintainer/release-workflow",
    "maintainer/generators",
    "docs/maintainer/product-narrative.md",
    "maintainer/product-narrative",
)

REQUIRED_GENERATOR_PATHS = (
    "scripts/generate_public_function_call_flows_json.py",
    "scripts/generate_individual_function_reference_pages.py",
    "scripts/generate_release_inventory.py",
    "scripts/release_inventory.py",
    "scripts/generate_release_contract_pages.py",
    "scripts/generate_public_function_call_flows_dashboard.py",
)


def test_release_skill_exists_and_is_canonical_source() -> None:
    """Verify the release skill exists and the docs guide is synchronized from it."""
    assert SKILL.exists()
    assert GUIDE.exists()
    assert "name: FabricOps Release Maintainer" in SKILL.read_text(encoding="utf-8")
    assert GUIDE.read_text(encoding="utf-8") == sync_maintainer_release_guide.rendered_doc()


def test_release_guide_uses_canonical_github_source_links() -> None:
    """Verify repository source links use GitHub URLs and resolve locally."""
    guide = GUIDE.read_text(encoding="utf-8")
    assert not re.search(r"\]\(\.\./\.\./(?:scripts|src|\.agents|pyproject\.toml|templates|docs/releases|\.github)", guide)
    links = re.findall(
        r"https://github\.com/Voycepeh/FabricOps-Starter-Kit/blob/main/([^\s)]+)",
        guide,
    )
    assert links
    for link in links:
        assert (ROOT / link).exists(), link


def test_documented_release_generators_exist() -> None:
    """Verify every documented release generator source path exists."""
    guide = GUIDE.read_text(encoding="utf-8")
    for path in REQUIRED_GENERATOR_PATHS:
        assert (ROOT / path).exists()
        assert path in guide
