"""Tests for coordinated function reference bundle generation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import generate_function_reference_bundle as bundle
from scripts import generate_individual_function_reference_pages as pages
from scripts import generate_public_function_call_flows_json as flows
from tests.unit.test_public_function_call_flows import write_manifest, write_project


def test_release_payload_filters_live_roots_and_keeps_frozen_fields(tmp_path: Path) -> None:
    """Verify release JSON freezes only Live public roots from generated source data."""
    root, pkg, init_path = write_project(tmp_path)
    manifests = write_manifest(root)

    current = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path, manifests_dir=manifests)
    frozen = flows.freeze_release_payload(current, release_version="0.1.0", source_ref="release-ref")

    assert [row["function_name"] for row in frozen["public_functions"]] == ["public_a"]
    public_a = frozen["public_functions"][0]
    assert public_a["lifecycle_status"] == "live"
    assert public_a["source_ref"] == "release-ref"
    assert public_a["signature"].startswith("def public_a(")
    assert frozen["metadata"]["contract_kind"] == "frozen_release_live_only"
    assert frozen["release_contract"]["source_ref"] == "release-ref"
    retained = {row["qualified_name"] for row in frozen["defined_functions"]}
    flow_qns = {row["qualified_name"] for public_row in frozen["public_functions"] for row in public_row["flow"]}
    assert retained <= flow_qns
    assert frozen["summary"]["defined_function_count"] == len(frozen["defined_functions"])


def test_release_pages_render_from_exact_frozen_json(tmp_path: Path) -> None:
    """Verify release pages consume the exact records written to frozen JSON."""
    contract = tmp_path / "public-function-call-flows.json"
    contract.write_text(
        json.dumps(
            {
                "public_functions": [
                    {
                        "function_name": "old_live",
                        "qualified_name": "fabricops_kit.old.old_live",
                        "source_path": "src/fabricops_kit/old.py",
                        "source_start_line": 10,
                        "source_end_line": 20,
                        "source_ref": "release-ref",
                        "lifecycle_status": "live",
                        "signature": "def old_live(value: str) -> str",
                        "summary": "Frozen summary from JSON.",
                        "parameters": [{"name": "value", "type": "str", "required": "Yes", "description": "Frozen parameter."}],
                        "returns_documentation": "Frozen returns.",
                        "raises_documentation": "Frozen raises.",
                        "examples": "old_live(value='x')",
                        "flow": [],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    generated = pages.generate_release_function_reference_pages(
        contract_path=contract,
        output_dir=tmp_path / "functions",
        release_version="0.1.0",
    )

    page_text = (tmp_path / "functions" / "old_live.md").read_text(encoding="utf-8")
    assert generated[0].name == "index.md"
    assert "This page documents `old_live` as released in version `0.1.0`." in page_text
    assert "Frozen summary from JSON." in page_text
    assert "def old_live(value: str) -> str" in page_text
    assert "release-ref/src/fabricops_kit/old.py#L10-L20" in page_text
    assert "[Current function page](../../../api/reference/old_live.md)" in page_text
    assert "[Release function index](index.md)" in page_text
    assert (tmp_path / "functions" / "index.md").exists()
    assert "<summary>Maintainer architecture details</summary>" in page_text


def test_release_bundle_refuses_existing_snapshot_without_overwrite(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify frozen release snapshots cannot be silently overwritten."""
    release_dir = tmp_path / "docs" / "releases" / "0.1.0" / "_data"
    release_dir.mkdir(parents=True)
    (release_dir / "public-function-call-flows.json").write_text("{}\n", encoding="utf-8")
    monkeypatch.setattr(bundle, "RELEASES_DIR", tmp_path / "docs" / "releases")
    monkeypatch.setattr(bundle, "_manifest_for_release", lambda version: {"release_version": version, "source_ref": "abc123"})
    monkeypatch.setattr(bundle, "_release_source_ref", lambda manifest: "abc123")

    with pytest.raises(RuntimeError, match="Use --overwrite-release"):
        bundle.generate_release_bundle("0.1.0")


def test_release_source_ref_accepts_matching_manifest_tag() -> None:
    """Verify matching release tag source refs are accepted before the tag exists."""
    manifest = {"release_version": "0.1.0", "source_ref": "v0.1.0"}

    assert bundle._release_source_ref(manifest) == "v0.1.0"


def test_release_source_ref_rejects_mismatched_manifest_tag() -> None:
    """Verify tag source refs must match the manifest release version."""
    manifest = {"release_version": "0.1.0", "source_ref": "v0.2.0"}

    with pytest.raises(RuntimeError, match="must match release_version"):
        bundle._release_source_ref(manifest)


def test_release_source_ref_uses_current_tree_when_matching_tag_is_not_created(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify release prep can freeze with a future tag source ref before tag creation."""
    monkeypatch.setattr(bundle, "_source_ref_exists", lambda source_ref: False)
    monkeypatch.setattr(bundle.flows, "build_payload", lambda: {"public_functions": [], "defined_functions": [], "metadata": {}, "summary": {}})

    payload = bundle._build_release_payload("0.1.0", "v0.1.0")

    assert payload["metadata"]["source_ref"] == "v0.1.0"
    assert payload["release_contract"]["source_ref"] == "v0.1.0"
