"""Tests for live release documentation state."""

from __future__ import annotations

import scripts.release_inventory as ri


def test_live_release_renders_frozen_pages_and_release_history():
    """Verify a Live current release has frozen detail pages and appears in release history."""
    version = ri.read_package_version()
    manifest = ri._load_manifest(ri.manifest_path(version))
    assert manifest is not None
    assert manifest["release_status"] == "live"

    paths = ri.render_release_pages()
    release_dir = ri.ROOT / "docs" / "releases" / version
    release_index = release_dir / "index.md"
    overview = (ri.ROOT / "docs" / "releases" / "index.md").read_text(encoding="utf-8")

    assert ri.ROOT / "docs" / "releases" / "index.md" in paths
    assert release_index in paths
    assert release_dir.exists()
    assert release_index.exists()
    assert "## Release history" in overview
    assert f"[FabricOps Starter Kit {version}]({version}/)" in overview
