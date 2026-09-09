"""Tests for preparing release documentation state."""

from __future__ import annotations

import scripts.release_inventory as ri


def test_preparing_release_omits_frozen_pages_and_stays_in_overview():
    """Verify a preparing current release has no frozen detail directory."""
    version = ri.read_package_version()
    manifest = ri._load_manifest(ri.manifest_path(version))
    assert manifest is not None
    assert manifest["release_status"] == "preparing"

    paths = ri.render_release_pages()
    release_dir = ri.ROOT / "docs" / "releases" / version
    overview = (ri.ROOT / "docs" / "releases" / "index.md").read_text(encoding="utf-8")

    assert ri.ROOT / "docs" / "releases" / "index.md" in paths
    assert ri.ROOT / "docs" / "releases" / version / "index.md" not in paths
    assert not release_dir.exists()
    assert "## Release history" in overview
    assert "## In preparation" in overview
    assert f"| FabricOps Starter Kit {version} | Preparing |" in overview
    assert "[FabricOps Starter Kit 0.1.0](0.1.0/)" in overview
