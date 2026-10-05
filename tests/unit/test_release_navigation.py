"""Tests for manifest-driven release navigation."""

from __future__ import annotations

from pathlib import Path

import pytest

import scripts.release_navigation as rn


def _write_manifest(directory: Path, version: str, status: str) -> None:
    (directory / f"{version}.yml").write_text(
        f"release_version: {version}\n"
        f"release_status: {status}\n"
        "release_date: 2026-08-01\n"
        "functions:\n"
        "metadata_tables:\n",
        encoding="utf-8",
    )


def test_release_navigation_uses_single_landing_page(tmp_path: Path) -> None:
    """Verify release history stays behind one sidebar landing page."""
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    _write_manifest(manifests, "0.1.0", "live")
    _write_manifest(manifests, "0.10.0", "live")

    assert rn.render_release_navigation(manifests) == (
        "      - Releases (Python package): releases/index.md\n"
    )


def test_release_navigation_preserves_landing_page_navigation(tmp_path: Path) -> None:
    """Verify synchronization leaves the landing-page navigation unchanged."""
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    _write_manifest(manifests, "0.2.0", "live")
    mkdocs = tmp_path / "mkdocs.yml"
    expected = (
        "nav:\n"
        "  - Home: index.md\n"
        "  - Download FabricOps:\n"
        "      - Releases (Python package): releases/index.md\n"
        "      - Notebook Templates: https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks\n"
        "  - Reference: reference/index.md\n"
    )
    mkdocs.write_text(expected, encoding="utf-8")

    rn.sync_release_navigation(mkdocs_path=mkdocs, manifests_dir=manifests)

    assert mkdocs.read_text(encoding="utf-8") == expected


def test_release_navigation_check_fails_when_landing_page_is_missing(tmp_path: Path) -> None:
    """Verify CI rejects navigation that does not expose the release landing page."""
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    _write_manifest(manifests, "0.2.0", "live")
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(
        "nav:\n"
        "  - Download FabricOps:\n"
        "      - Notebook Templates: templates/notebooks\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Releases landing-page entry"):
        rn.sync_release_navigation(check=True, mkdocs_path=mkdocs, manifests_dir=manifests)


def test_repository_release_navigation_is_current() -> None:
    """Verify committed MkDocs navigation matches all current Live manifests."""
    rn.sync_release_navigation(check=True)
