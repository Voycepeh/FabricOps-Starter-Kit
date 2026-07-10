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


def test_maintainer_navigation_contains_only_two_pages() -> None:
    """Verify MkDocs exposes only the two intended maintainer pages."""
    mkdocs = MKDOCS.read_text(encoding="utf-8")
    assert "FabricOps Maintainer:" in mkdocs
    assert "Release Guide: maintainer/index.md" in mkdocs
    assert "Public API & Architecture: maintainer/public-api-architecture.md" in mkdocs
    assert "maintainer/overview.md" not in mkdocs
    assert "maintainer/release-workflow.md" not in mkdocs
    assert "maintainer/generators.md" not in mkdocs


def test_removed_maintainer_pages_are_not_referenced() -> None:
    """Verify stale maintainer page references are absent from maintained docs."""
    haystack = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [README, LLMS, GUIDE, ARCHITECTURE, MKDOCS]
    )
    for removed_path in REMOVED_MAINTAINER_PATHS:
        assert removed_path not in haystack


def test_release_guide_links_to_existing_source_paths() -> None:
    """Verify repository source links in the maintainer guide resolve."""
    guide = GUIDE.read_text(encoding="utf-8")
    links = re.findall(r"\[[^\]]+\]\((\.\./\.\./[^)#]+)", guide)
    assert links
    for link in links:
        assert (GUIDE.parent / link).resolve().exists(), link


def test_documented_release_generators_exist() -> None:
    """Verify every documented release generator source path exists."""
    guide = GUIDE.read_text(encoding="utf-8")
    for path in REQUIRED_GENERATOR_PATHS:
        assert (ROOT / path).exists()
        assert path in guide


def test_release_skill_starts_with_inspection_and_has_approval_gates() -> None:
    """Verify the skill describes inspection-first operation and human approval gates."""
    skill = SKILL.read_text(encoding="utf-8")
    assert "the AI agent must inspect before mutating" in skill
    assert "Never assume the next version" in skill
    assert "Before setting lifecycle statuses" in skill
    assert "The AI must ask the maintainer to decide" in skill
    assert "Pause for maintainer approval before selecting or writing the final version" in skill
    assert "Ask for explicit approval" in skill
    assert "Never add a lifecycle status named `updated`" in skill
