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


def test_release_navigation_lists_only_live_versions_newest_first(tmp_path: Path) -> None:
    """Verify sidebar versions are derived from Live manifests in semantic order."""
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    _write_manifest(manifests, "0.1.0", "live")
    _write_manifest(manifests, "0.10.0", "live")
    _write_manifest(manifests, "0.2.0", "live")
    _write_manifest(manifests, "0.11.0", "preparing")

    assert rn.render_release_navigation(manifests) == (
        "  - Releases:\n"
        "      - Overview: releases/index.md\n"
        "      - 0.10.0: releases/0.10.0/index.md\n"
        "      - 0.2.0: releases/0.2.0/index.md\n"
        "      - 0.1.0: releases/0.1.0/index.md\n"
    )


def test_release_navigation_replaces_only_releases_block(tmp_path: Path) -> None:
    """Verify synchronization preserves navigation before and after Releases."""
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    _write_manifest(manifests, "0.2.0", "live")
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(
        "nav:\n"
        "  - Home: index.md\n"
        "  - Releases:\n"
        "      - Overview: releases/index.md\n"
        "      - 0.1.0: releases/0.1.0/index.md\n"
        "  - Reference: reference/index.md\n",
        encoding="utf-8",
    )

    rn.sync_release_navigation(mkdocs_path=mkdocs, manifests_dir=manifests)

    assert mkdocs.read_text(encoding="utf-8") == (
        "nav:\n"
        "  - Home: index.md\n"
        "  - Releases:\n"
        "      - Overview: releases/index.md\n"
        "      - 0.2.0: releases/0.2.0/index.md\n"
        "  - Reference: reference/index.md\n"
    )


def test_release_navigation_check_fails_when_sidebar_is_stale(tmp_path: Path) -> None:
    """Verify CI can reject a Live release missing from MkDocs navigation."""
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    _write_manifest(manifests, "0.2.0", "live")
    mkdocs = tmp_path / "mkdocs.yml"
    mkdocs.write_text(
        "nav:\n"
        "  - Releases:\n"
        "      - Overview: releases/index.md\n"
        "      - 0.1.0: releases/0.1.0/index.md\n",
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="MkDocs release navigation is stale"):
        rn.sync_release_navigation(check=True, mkdocs_path=mkdocs, manifests_dir=manifests)


def test_repository_release_navigation_is_current() -> None:
    """Verify committed MkDocs navigation matches all current Live manifests."""
    rn.sync_release_navigation(check=True)
