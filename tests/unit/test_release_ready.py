"""Tests for release readiness validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts import check_release_ready as ready


def test_manifest_release_alignment_accepts_matching_tag(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify manifest release_version and source_ref may match the pushed tag."""
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    (manifests / "0.1.0.yml").write_text("release_version: 0.1.0\nsource_ref: v0.1.0\n", encoding="utf-8")
    monkeypatch.setattr(ready, "MANIFESTS_DIR", manifests)

    ready.validate_manifest_release_alignment("0.1.0", "v0.1.0")


def test_manifest_release_alignment_rejects_mismatched_source_ref(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify release readiness fails when manifest source_ref and tag disagree."""
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    (manifests / "0.1.0.yml").write_text("release_version: 0.1.0\nsource_ref: v0.2.0\n", encoding="utf-8")
    monkeypatch.setattr(ready, "MANIFESTS_DIR", manifests)

    with pytest.raises(ValueError, match="source_ref='v0.2.0' != release tag='v0.1.0'"):
        ready.validate_manifest_release_alignment("0.1.0", "v0.1.0")


def test_manifest_release_alignment_rejects_mismatched_manifest_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify release readiness fails when manifest version and tag version disagree."""
    manifests = tmp_path / "manifests"
    manifests.mkdir()
    (manifests / "0.1.0.yml").write_text("release_version: 0.2.0\nsource_ref: v0.1.0\n", encoding="utf-8")
    monkeypatch.setattr(ready, "MANIFESTS_DIR", manifests)

    with pytest.raises(ValueError, match="release_version='0.2.0' != package/tag version='0.1.0'"):
        ready.validate_manifest_release_alignment("0.1.0", "v0.1.0")
