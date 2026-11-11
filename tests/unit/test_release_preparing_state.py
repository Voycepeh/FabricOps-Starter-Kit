"""Tests for live release documentation state."""

from __future__ import annotations

import scripts.release_inventory as ri


def test_live_release_keeps_frozen_pages_and_release_history():
    """Check released snapshots without re-rendering them from current public APIs."""
    version = ri.read_package_version()
    manifest = ri._load_manifest(ri.manifest_path(version))
    assert manifest is not None
    assert manifest["release_status"] == "live"

    release_dir = ri.ROOT / "docs" / "releases" / version
    release_index = release_dir / "index.md"
    overview = (ri.ROOT / "docs" / "releases" / "index.md").read_text(encoding="utf-8")

    assert release_dir.exists()
    assert release_index.exists()
    assert "## Release history" in overview
    assert f"[FabricOps Starter Kit {version}]({version}/index.md)" in overview

    # The published manifest owns historical names even after a breaking rename.
    # Importing current callables to rewrite those pages would change history.
    for item in manifest["functions"]:
        if item["status"] == "live":
            assert (release_dir / "functions" / f"{item['name']}.md").exists()
