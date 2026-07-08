"""Tests for release inventory generation."""

from __future__ import annotations

from pathlib import Path
import tomllib

import pytest

import scripts.release_inventory as ri


def test_release_inventory_reads_version_from_pyproject():
    """Verify release inventory version comes from pyproject.toml."""
    expected = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    assert ri.read_package_version() == expected


def test_release_inventory_discovers_supported_public_api():
    """Verify all supported public API functions are discovered."""
    from fabricops_kit.public_api import SUPPORTED_PUBLIC_API

    assets = ri.discover_functions()
    assert {asset.qualified_name for asset in assets} == set(SUPPORTED_PUBLIC_API)
    assert all(asset.source_path.startswith("src/fabricops_kit/") for asset in assets)


def test_release_inventory_discovers_metadata_tables_and_docs():
    """Verify metadata tables come from the schema registry with conventional docs paths."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    assets = ri.discover_metadata_tables()
    assert {asset.name for asset in assets} == set(metadata_table_schema_registry())
    catalogue = next(asset for asset in assets if asset.name == "METADATA_DATA_CATALOGUE")
    assert catalogue.source_path == "src/fabricops_kit/config/metadata_schemas.py"
    assert catalogue.documentation_path == "docs/reference/metadata/metadata_data_catalogue.md"


def test_release_inventory_discovers_templates_from_files():
    """Verify notebook templates are discovered from actual template files."""
    assets = ri.discover_templates()
    assert {asset.source_path for asset in assets} == {path.as_posix() for path in sorted(Path("templates/notebooks").glob("*.ipynb"))}
    assert next(asset for asset in assets if asset.name == "00_env_config").documentation_path.endswith("environment-config.md")


def test_release_inventory_discovers_dq_rules_from_registry():
    """Verify DQ rules are discovered from the authoritative guardrail registry."""
    from fabricops_kit.pipeline.guardrails_shared import DQ_RULE_TYPES

    assets = ri.discover_dq_rules()
    assert {asset.name for asset in assets} == set(DQ_RULE_TYPES)
    assert next(asset for asset in assets if asset.name == "not_null").documentation_path == "docs/reference/dq-rules/not-null.md"


def test_release_inventory_first_generation_defaults_preview():
    """Verify first-generation manifests mark every asset preview."""
    manifest = ri.synchronize_manifest(None, {"functions": [ri.ReleaseAsset("a", "src/a.py")], "metadata_tables": [], "templates": [], "dq_rules": []}, "1.2.3")
    assert manifest["release_version"] == "1.2.3"
    assert manifest["functions"][0]["status"] == "preview"


def test_release_inventory_regeneration_preserves_status_and_adds_new_preview():
    """Verify regeneration preserves statuses and adds new assets as preview."""
    existing = {"release_version": "1.0.0", "functions": [{"name": "a", "source_path": "old.py", "status": "live", "notes": "keep"}], "metadata_tables": [], "templates": [], "dq_rules": []}
    discovered = {"functions": [ri.ReleaseAsset("a", "new.py"), ri.ReleaseAsset("b", "b.py")], "metadata_tables": [], "templates": [], "dq_rules": []}
    manifest = ri.synchronize_manifest(existing, discovered, "1.0.0")
    assert manifest["functions"][0]["source_path"] == "new.py"
    assert manifest["functions"][0]["status"] == "live"
    assert manifest["functions"][0]["notes"] == "keep"
    assert manifest["functions"][1]["status"] == "preview"


def test_release_inventory_removed_asset_requires_discontinued():
    """Verify removed tracked assets fail until maintainers discontinue them."""
    existing = {"release_version": "1.0.0", "functions": [{"name": "gone", "source_path": "gone.py", "status": "live"}], "metadata_tables": [], "templates": [], "dq_rules": []}
    with pytest.raises(ValueError, match="Mark each removed asset"):
        ri.synchronize_manifest(existing, {"functions": [], "metadata_tables": [], "templates": [], "dq_rules": []}, "1.0.0")


def test_release_inventory_rejects_invalid_status_and_duplicates():
    """Verify invalid lifecycle status values and duplicate names fail."""
    bad_status = {"release_version": "1.0.0", "functions": [{"name": "a", "status": "alpha"}], "metadata_tables": [], "templates": [], "dq_rules": []}
    with pytest.raises(ValueError, match="Invalid lifecycle status"):
        ri.synchronize_manifest(bad_status, {"functions": [], "metadata_tables": [], "templates": [], "dq_rules": []}, "1.0.0")
    duplicate = {"release_version": "1.0.0", "functions": [{"name": "a", "status": "preview"}, {"name": "a", "status": "live"}], "metadata_tables": [], "templates": [], "dq_rules": []}
    with pytest.raises(ValueError, match="Duplicate identifier"):
        ri.synchronize_manifest(duplicate, {"functions": [], "metadata_tables": [], "templates": [], "dq_rules": []}, "1.0.0")


def test_release_inventory_output_order_is_deterministic():
    """Verify manifest rows are sorted deterministically."""
    manifest = ri.synchronize_manifest(None, {"functions": [ri.ReleaseAsset("b", "b.py"), ri.ReleaseAsset("a", "a.py")], "metadata_tables": [], "templates": [], "dq_rules": []}, "1.0.0")
    assert [item["name"] for item in manifest["functions"]] == ["a", "b"]


def test_release_contract_pages_render_status_chips_and_links():
    """Verify rendered release contract tables include status chips and stable links."""
    content = (ri.ROOT / "docs" / "releases" / ri.read_package_version() / "functions.md").read_text(encoding="utf-8")
    assert "| Status | Name | Documentation | Source |" in content
    assert 'fabricops-release-status fabricops-release-status--live">Live</span>' in content
    assert 'fabricops-release-status fabricops-release-status--preview">Preview</span>' in content
    assert "[docs/api/reference/read_lakehouse_table.md](../../api/reference/read_lakehouse_table.md)" in content
    assert "`src/fabricops_kit/io/read_lakehouse_table.py`" in content
    assert "https://" not in content


def test_release_status_chip_supports_all_lifecycle_values():
    """Verify release status chips render all supported lifecycle classes."""
    assert ri.release_status_chip("live") == '<span class="fabricops-release-status fabricops-release-status--live">Live</span>'
    assert ri.release_status_chip("preview") == '<span class="fabricops-release-status fabricops-release-status--preview">Preview</span>'
    assert ri.release_status_chip("discontinued") == '<span class="fabricops-release-status fabricops-release-status--discontinued">Discontinued</span>'


def test_release_status_ordering_is_deterministic():
    """Verify release contract rows sort by lifecycle status before name."""
    rows = [
        {"name": "z_old", "status": "discontinued"},
        {"name": "b_preview", "status": "preview"},
        {"name": "a_live", "status": "live"},
        {"name": "a_preview", "status": "preview"},
    ]
    assert [item["name"] for item in ri.sort_release_items(rows)] == ["a_live", "a_preview", "b_preview", "z_old"]


def test_release_notes_are_sourced_from_changelog():
    """Verify missing release notes are reported rather than invented."""
    assert ri.extract_changelog_notes(ri.read_package_version()) == "Release notes have not yet been prepared."


def test_release_manifest_lifecycle_counts_match_initial_release_baseline():
    """Verify maintainer-owned lifecycle classifications match the initial release baseline."""
    manifest = ri._load_manifest(ri.manifest_path(ri.read_package_version()))
    assert manifest is not None
    assert sum(1 for item in manifest["functions"] if item["status"] == "live") == 9
    assert sum(1 for item in manifest["templates"] if item["status"] == "live") == 3
    assert sum(1 for item in manifest["metadata_tables"] if item["status"] == "live") == 4
    assert all(item["status"] == "preview" for item in manifest["dq_rules"])
