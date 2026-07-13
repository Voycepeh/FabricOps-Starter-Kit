"""Tests for release inventory generation."""

from __future__ import annotations

from pathlib import Path
import tomllib

from packaging.version import Version
import pytest

import scripts.release_inventory as ri


def test_release_inventory_reads_version_from_pyproject():
    """Verify release inventory version comes from pyproject.toml."""
    expected = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))["project"]["version"]
    assert ri.read_package_version() == expected


def test_release_inventory_discovers_supported_public_api():
    """Verify all supported public API functions are discovered."""
    from fabricops_kit.public_api import RELEASE_PUBLIC_API

    assets = ri.discover_functions()
    assert {asset.qualified_name for asset in assets} == set(RELEASE_PUBLIC_API)
    assert all(asset.source_path.startswith("src/fabricops_kit/") for asset in assets)


def test_release_inventory_discovers_metadata_tables_and_docs():
    """Verify metadata tables come from the schema registry with conventional docs paths."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry

    assets = ri.discover_metadata_tables()
    assert {asset.name for asset in assets} == set(metadata_table_schema_registry())
    catalogue = next(asset for asset in assets if asset.name == "METADATA_DATA_CATALOGUE")
    assert catalogue.source_path == "src/fabricops_kit/config/metadata_schemas.py"
    assert catalogue.documentation_path == "docs/reference/metadata/metadata_data_catalogue.md"


def test_release_inventory_first_generation_defaults_preview():
    """Verify first-generation manifests mark every asset preview."""
    manifest = ri.synchronize_manifest(None, {"functions": [ri.ReleaseAsset("a", "src/a.py")], "metadata_tables": []}, "1.2.3")
    assert manifest["release_version"] == "1.2.3"
    assert manifest["functions"][0]["status"] == "preview"


def test_release_inventory_regeneration_preserves_status_and_adds_new_preview():
    """Verify regeneration preserves statuses and adds new assets as preview."""
    existing = {"release_version": "1.0.0", "functions": [{"name": "a", "source_path": "old.py", "status": "live", "notes": "keep"}], "metadata_tables": []}
    discovered = {"functions": [ri.ReleaseAsset("a", "new.py"), ri.ReleaseAsset("b", "b.py")], "metadata_tables": []}
    manifest = ri.synchronize_manifest(existing, discovered, "1.0.0")
    assert manifest["functions"][0]["source_path"] == "new.py"
    assert manifest["functions"][0]["status"] == "live"
    assert manifest["functions"][0]["notes"] == "keep"
    assert manifest["functions"][1]["status"] == "preview"


def test_release_inventory_preserves_human_owned_fields_for_release_groups():
    """Verify regeneration preserves lifecycle evidence for formal release groups."""
    existing = {
        "release_version": "1.0.0",
        "functions": [
            {
                "name": "function_a",
                "source_path": "old.py",
                "status": "preview",
                "introduced_in": "0.9.0",
                "rationale": "function rationale",
                "notes": "function note",
            }
        ],
        "metadata_tables": [
            {
                "name": "METADATA_A",
                "source_path": "old.py",
                "status": "preview",
                "schema_since": "0.8.0",
                "schema_fingerprint": "same",
                "introduced_in": "0.8.0",
                "rationale": "metadata rationale",
                "managed_by": "schema owner",
            }
        ],
    }
    discovered = {
        "functions": [ri.ReleaseAsset("function_a", "new.py")],
        "metadata_tables": [ri.ReleaseAsset("METADATA_A", "new.py", generated_fields={"schema_fingerprint": "same"})],
    }

    manifest = ri.synchronize_manifest(existing, discovered, "1.0.0")

    assert manifest["functions"][0]["source_path"] == "new.py"
    assert manifest["functions"][0]["introduced_in"] == "0.9.0"
    assert manifest["functions"][0]["rationale"] == "function rationale"
    assert manifest["functions"][0]["notes"] == "function note"
    metadata = manifest["metadata_tables"][0]
    assert metadata["schema_since"] == "0.8.0"
    assert metadata["introduced_in"] == "0.8.0"
    assert metadata["rationale"] == "metadata rationale"
    assert metadata["managed_by"] == "schema owner"


def test_release_inventory_removed_asset_requires_discontinued():
    """Verify removed tracked assets fail until maintainers discontinue them."""
    existing = {"release_version": "1.0.0", "functions": [{"name": "gone", "source_path": "gone.py", "status": "live"}], "metadata_tables": []}
    with pytest.raises(ValueError, match="Mark each removed asset"):
        ri.synchronize_manifest(existing, {"functions": [], "metadata_tables": []}, "1.0.0")


def test_release_inventory_rejects_invalid_status_and_duplicates():
    """Verify invalid lifecycle status values and duplicate names fail."""
    bad_status = {"release_version": "1.0.0", "functions": [{"name": "a", "status": "alpha"}], "metadata_tables": []}
    with pytest.raises(ValueError, match="Invalid lifecycle status"):
        ri.synchronize_manifest(bad_status, {"functions": [], "metadata_tables": []}, "1.0.0")
    duplicate = {"release_version": "1.0.0", "functions": [{"name": "a", "status": "preview"}, {"name": "a", "status": "live"}], "metadata_tables": []}
    with pytest.raises(ValueError, match="Duplicate identifier"):
        ri.synchronize_manifest(duplicate, {"functions": [], "metadata_tables": []}, "1.0.0")


def test_release_inventory_output_order_is_deterministic():
    """Verify manifest rows are sorted deterministically."""
    manifest = ri.synchronize_manifest(None, {"functions": [ri.ReleaseAsset("b", "b.py"), ri.ReleaseAsset("a", "a.py")], "metadata_tables": []}, "1.0.0")
    assert [item["name"] for item in manifest["functions"]] == ["a", "b"]


def test_load_release_manifests_reads_default_manifest_directory():
    """Verify the no-argument loader preserves release-page default discovery."""
    manifests = ri.load_release_manifests()

    versions = [manifest["release_version"] for manifest in manifests]

    assert versions
    assert ri.read_package_version() in versions
    assert versions == sorted(versions, key=Version)


def test_load_release_manifests_reads_only_supplied_directory(tmp_path):
    """Verify custom manifest directories are isolated from repository manifests."""
    manifests_dir = tmp_path / "manifests"
    manifests_dir.mkdir()
    (manifests_dir / "0.2.0.yml").write_text(
        "release_version: 0.2.0\n"
        "release_status: live\n"
        "release_date: 2026-08-01\n"
        "functions:\n"
        "metadata_tables:\n",
        encoding="utf-8",
    )

    manifests = ri.load_release_manifests(manifests_dir)

    assert [manifest["release_version"] for manifest in manifests] == ["0.2.0"]


def test_valid_live_release_date_passes_strict_validation():
    """Verify exact ISO release dates are accepted for Live manifests."""
    manifest = {
        "release_version": "1.0.0",
        "release_status": "live",
        "release_date": "2026-07-08",
        "functions": [],
        "metadata_tables": [],
    }

    ri._validate_manifest(manifest, "1.0.0")


def test_preparing_release_status_allows_null_release_evidence():
    """Verify preparing releases can omit release date and source commit evidence."""
    manifest = {
        "release_version": "1.0.0",
        "release_status": "preparing",
        "release_date": None,
        "source_ref": None,
        "functions": [],
        "metadata_tables": [],
    }

    ri._validate_manifest(manifest, "1.0.0")


def test_invalid_release_status_fails_clearly():
    """Verify release status is distinct from asset lifecycle values."""
    manifest = {
        "release_version": "1.0.0",
        "release_status": "preview",
        "functions": [],
        "metadata_tables": [],
    }

    with pytest.raises(ValueError, match="Invalid release_status"):
        ri._validate_manifest(manifest, "1.0.0")



def test_manifest_accepts_matching_tag_source_ref():
    """Verify release tag source refs may match the manifest version before tag creation."""
    manifest = {
        "release_version": "0.1.0",
        "release_status": "live",
        "release_date": "2026-07-11",
        "source_ref": "v0.1.0",
        "functions": [],
        "metadata_tables": [],
    }

    ri._validate_manifest(manifest, "0.1.0")


def test_manifest_rejects_mismatched_tag_source_ref():
    """Verify release tag source refs must match the manifest version."""
    manifest = {
        "release_version": "0.1.0",
        "release_status": "live",
        "release_date": "2026-07-11",
        "source_ref": "v0.2.0",
        "functions": [],
        "metadata_tables": [],
    }

    with pytest.raises(ValueError, match="source_ref 'v0.2.0' must match v0.1.0"):
        ri._validate_manifest(manifest, "0.1.0")


def test_malformed_live_release_dates_fail_clearly():
    """Verify Live release dates reject prose, malformed dates, and timestamps."""
    for release_date in [None, "yesterday", "2026-7-8", "2026-07-08T00:00:00"]:
        manifest = {
            "release_version": "1.0.0",
            "release_status": "live",
            "release_date": release_date,
            "functions": [],
            "metadata_tables": [],
        }
        with pytest.raises(ValueError, match="must include release_date in YYYY-MM-DD format"):
            ri._validate_manifest(manifest, "1.0.0")


def test_release_contract_pages_render_live_manifest_snapshot():
    """Verify Live manifests render frozen release evidence."""
    paths = ri.render_release_pages()
    version = ri.read_package_version()
    content = (ri.ROOT / "docs" / "releases" / "index.md").read_text(encoding="utf-8")

    assert ri.ROOT / "docs" / "releases" / "index.md" in paths
    assert ri.ROOT / "docs" / "releases" / version / "index.md" in paths
    assert (ri.ROOT / "docs" / "releases" / version).exists()
    assert f"| [FabricOps Starter Kit {version}]({version}/) | 2026-07-11 |" in content
    assert "No completed FabricOps Starter Kit releases have been published yet." not in content


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


def test_release_asset_status_badges_are_manifest_driven():
    """Verify release-local status badges come from manifest metadata."""
    version = "1.2.0"

    assert ri.release_asset_change_status({"name": "new", "live_since": version}, version) == "new"
    assert ri.release_asset_change_status({"name": "updated", "live_since": "1.1.0", "updated_in": version}, version) == "updated"
    assert ri.release_asset_change_status({"name": "schema", "live_since": "1.1.0", "schema_since": version}, version) == "updated"
    assert ri.release_asset_change_status({"name": "same", "live_since": "1.1.0"}, version) == ""
    assert ri.release_asset_status_badge("new") == '<span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span>'
    assert ri.release_asset_status_badge("updated") == '<span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span>'
    assert ri.release_asset_status_badge("") == ""


def test_release_inventory_status_sorting_prioritizes_new_updated_then_name():
    """Verify release inventory rows sort new, updated, then unchanged alphabetically."""
    version = "1.2.0"
    rows = [
        {"name": "z_same", "status": "live", "live_since": "1.0.0"},
        {"name": "b_updated", "status": "live", "live_since": "1.0.0", "updated_in": version},
        {"name": "a_new", "status": "live", "live_since": version},
        {"name": "a_same", "status": "live", "live_since": "1.0.0"},
        {"name": "a_updated", "status": "live", "live_since": "1.0.0", "updated_in": version},
    ]

    sorted_names = [item["name"] for item in ri.sort_release_inventory_items(rows, version)]

    assert sorted_names == ["a_new", "a_updated", "b_updated", "a_same", "z_same"]


def test_release_inventory_section_renders_optional_status_badges():
    """Verify release overview badges and ordering are generated from manifest fields."""
    manifest = {"release_version": "1.2.0", "github_owner": "Voycepeh", "github_repo": "FabricOps-Starter-Kit"}
    items = [
        {"name": "z_same", "status": "live", "live_since": "1.0.0", "description": "Same."},
        {"name": "b_updated", "status": "live", "live_since": "1.0.0", "updated_in": "1.2.0", "description": "Updated."},
        {"name": "a_new", "status": "live", "live_since": "1.2.0", "description": "New."},
        {"name": "a_same", "status": "live", "live_since": "1.0.0", "description": "Same A."},
    ]

    lines = ri._release_inventory_section(manifest, "1.2.0", "functions", items)
    rows = [line for line in lines if line.startswith("| [`")]

    assert rows == [
        '| [`a_new`](functions/a_new.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--new">NEW</span> | New. |',
        '| [`b_updated`](functions/b_updated.md) <span class="fabricops-release-asset-status fabricops-release-asset-status--updated">UPDATED</span> | Updated. |',
        '| [`a_same`](functions/a_same.md) | Same A. |',
        '| [`z_same`](functions/z_same.md) | Same. |',
    ]


def test_release_notes_are_sourced_from_changelog():
    """Verify release notes come from the matching changelog section."""
    notes = ri.extract_changelog_notes(ri.read_package_version())

    assert "Stable Fabric lakehouse and warehouse read/write helpers as the only Live v0.1.0 public API surface." in notes
    assert "first supported FabricOps Starter Kit release" in notes


def test_missing_release_notes_fail_generation_clearly(tmp_path):
    """Verify missing release notes fail instead of rendering placeholders."""
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text("# Changelog\n\n## [Unreleased]\n\n- Pending.\n", encoding="utf-8")
    with pytest.raises(ValueError, match="no release section"):
        ri.extract_changelog_notes("9.9.9", changelog)


def test_release_manifest_lifecycle_counts_match_initial_release_baseline():
    """Verify maintainer-owned lifecycle classifications match the initial release baseline."""
    manifest = ri._load_manifest(ri.manifest_path(ri.read_package_version()))
    assert manifest is not None
    assert sum(1 for item in manifest["functions"] if item["status"] == "live") == 9
    setup = next(item for item in manifest["functions"] if item["name"] == "setup_notebook")
    assert setup["status"] == "live"
    assert setup["live_since"] == "0.1.0"
    assert sum(1 for item in manifest["metadata_tables"] if item["status"] == "live") == 0
    assert "templates" not in manifest
    assert "dq_rules" not in manifest
    assert any(item["status"] == "preview" for item in manifest["functions"])


def test_release_generates_frozen_detail_pages_for_live_manifest():
    """Verify Live releases render frozen detail pages."""
    ri.render_release_pages()
    base = ri.ROOT / "docs" / "releases" / ri.read_package_version()

    assert base.exists()


def test_release_overview_lists_live_release_with_inventory():
    """Verify Live releases are listed with frozen Live inventory links."""
    ri.render_release_pages()
    content = (ri.ROOT / "docs" / "releases" / "index.md").read_text(encoding="utf-8")

    assert "## Release history" in content
    assert "No completed FabricOps Starter Kit releases have been published yet." not in content
    assert "## In preparation" not in content
    assert f"| [FabricOps Starter Kit {ri.read_package_version()}]({ri.read_package_version()}/) | 2026-07-11 |" in content
    assert "functions/read_lakehouse_table.md" not in content


def test_live_release_requires_release_date():
    """Verify Live release manifests must include a release date."""
    manifest = {"release_version": "1.0.0", "release_status": "live", "release_date": None, "functions": [], "metadata_tables": []}

    with pytest.raises(ValueError, match="must include release_date"):
        ri._validate_manifest(manifest, "1.0.0")


def test_individual_release_overview_is_rendered_for_live_release():
    """Verify Live releases render a release overview."""
    ri.render_release_pages()
    version = ri.read_package_version()
    release_dir = ri.ROOT / "docs" / "releases" / version

    assert (release_dir / "index.md").exists()


def test_release_inventory_section_omits_empty_manual_asset_groups():
    """Verify manual asset groups cannot enter formal release sections."""
    manifest = {"github_owner": "Voycepeh", "github_repo": "FabricOps-Starter-Kit"}
    live = {"functions": [], "metadata_tables": []}

    sections = ri._release_inventory_sections(manifest, "1.2.3", live)
    content = "\n".join(sections)

    assert content == ""
    assert "DQ rules" not in content
    assert "notebook templates" not in content


def test_release_detail_pages_are_rendered_for_live_release():
    """Verify Live releases render detail page back-link evidence."""
    ri.render_release_pages()
    base = ri.ROOT / "docs" / "releases" / ri.read_package_version()

    assert (base / "functions" / "read_lakehouse_excel.md").exists()
    assert not (base / "metadata" / "metadata_data_catalogue.md").exists()


def test_no_release_table_uses_raw_source_path_columns():
    """Verify public release inventory tables avoid raw source/documentation columns."""
    for path in (ri.ROOT / "docs" / "releases" / ri.read_package_version()).glob("**/*.md"):
        content = path.read_text(encoding="utf-8")
        assert "| Status | Name | Documentation | Source |" not in content
        assert "Documentation | Source" not in content


def test_generated_release_pages_have_required_notice():
    """Verify generated release pages declare their generated ownership."""
    prefix = "<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->"
    release_root = ri.ROOT / "docs" / "releases" / ri.read_package_version()
    for path in release_root.glob("**/*.md"):
        content = path.read_text(encoding="utf-8")
        if path.is_relative_to(release_root / "functions"):
            assert "Frozen source ref:" in content or "frozen for FabricOps Starter Kit" in content
        else:
            assert content.startswith(prefix)


def test_release_generation_is_deterministic_and_second_run_clean():
    """Verify rendering twice produces identical page content."""
    ri.render_release_pages()
    first = {p.relative_to(ri.ROOT).as_posix(): p.read_text(encoding="utf-8") for p in (ri.ROOT / "docs" / "releases").glob("**/*.md")}
    ri.render_release_pages()
    second = {p.relative_to(ri.ROOT).as_posix(): p.read_text(encoding="utf-8") for p in (ri.ROOT / "docs" / "releases").glob("**/*.md")}
    assert first == second


def test_mkdocs_navigation_links_release_overview_after_release_exists():
    """Verify 0.1.0 navigation links the frozen release overview."""
    content = (ri.ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert "releases/index.md" in content
    assert "0.1.0: releases/0.1.0/index.md" in content
    assert "releases/0.1.0/functions/index.md" not in content


def test_release_renderer_keeps_live_version_directory():
    """Verify release renderer keeps the version directory for Live releases."""
    ri.render_release_pages()

    assert (ri.ROOT / "docs" / "releases" / ri.read_package_version()).exists()


def test_metadata_manifest_records_schema_since_and_fingerprint():
    """Verify metadata schemas are tied to package releases by fingerprint."""
    manifest = ri._load_manifest(ri.manifest_path(ri.read_package_version()))
    assert manifest is not None
    agreement = next(item for item in manifest["metadata_tables"] if item["name"] == "METADATA_DATA_AGREEMENT")
    assert agreement["status"] == "preview"
    assert agreement["schema_since"] == "0.1.0"
    assert len(agreement["schema_fingerprint"]) == 64


def test_metadata_schema_since_is_preserved_when_fingerprint_unchanged():
    """Verify schema_since does not advance when a schema fingerprint is unchanged."""
    existing = {
        "release_version": "0.1.1",
        "functions": [],
        "metadata_tables": [
            {
                "name": "METADATA_DATA_AGREEMENT",
                "source_path": "old.py",
                "status": "live",
                "live_since": "0.1.0",
                "schema_since": "0.1.0",
                "schema_fingerprint": "same",
            }
        ],
    }
    discovered = {
        "functions": [],
        "metadata_tables": [ri.ReleaseAsset("METADATA_DATA_AGREEMENT", "new.py", generated_fields={"schema_fingerprint": "same"})],
    }
    manifest = ri.synchronize_manifest(existing, discovered, "0.1.1")
    assert manifest["metadata_tables"][0]["schema_since"] == "0.1.0"


def test_metadata_schema_since_advances_when_fingerprint_changes():
    """Verify schema_since moves to the package version when schema structure changes."""
    existing = {
        "release_version": "0.2.0",
        "functions": [],
        "metadata_tables": [
            {
                "name": "METADATA_DATA_AGREEMENT",
                "source_path": "old.py",
                "status": "live",
                "live_since": "0.1.0",
                "schema_since": "0.1.0",
                "schema_fingerprint": "old",
            }
        ],
    }
    discovered = {
        "functions": [],
        "metadata_tables": [ri.ReleaseAsset("METADATA_DATA_AGREEMENT", "new.py", generated_fields={"schema_fingerprint": "new"})],
    }
    manifest = ri.synchronize_manifest(existing, discovered, "0.2.0")
    assert manifest["metadata_tables"][0]["schema_since"] == "0.2.0"


def test_release_history_index_renders_all_manifests_as_sorted_table_rows():
    """Verify release manifests render as newest-first release history rows."""
    manifests = [
        {
            "release_version": "0.1.0",
            "release_status": "live",
            "release_date": "2026-07-08",
            "release_motivation": "Initial governed Fabric notebook workflows. Extra detail omitted.",
        },
        {
            "release_version": "0.2.0",
            "release_status": "live",
            "release_date": "2026-08-01",
            "release_motivation": "Expanded release workflow coverage.",
        },
    ]

    content = ri.render_releases_index(manifests, "<!-- Generated file. Test notice. -->")

    assert content.startswith("<!-- Generated file. Test notice. -->")
    assert "## Release history" in content
    assert "## Current release" not in content
    assert "| Release | Release date | Description |" in content
    assert "| [FabricOps Starter Kit 0.2.0](0.2.0/) | 2026-08-01 | Expanded release workflow coverage. |" in content
    assert "| [FabricOps Starter Kit 0.1.0](0.1.0/) | 2026-07-08 | Initial governed Fabric notebook workflows. |" in content
    assert content.index("FabricOps Starter Kit 0.2.0") < content.index("FabricOps Starter Kit 0.1.0")


def test_release_history_semantic_version_fallback_order_is_deterministic():
    """Verify equal or unavailable dates fall back to semantic-version order."""
    manifests = [
        {"release_version": "0.1.9", "release_date": None, "release_motivation": "Patch release."},
        {"release_version": "0.1.10", "release_date": None, "release_motivation": "Later patch release."},
        {"release_version": "0.2.0", "release_date": "2026-08-01", "release_motivation": "Minor release."},
        {"release_version": "0.3.0", "release_date": "2026-08-01", "release_motivation": "Later minor release."},
    ]

    versions = [manifest["release_version"] for manifest in ri.sort_release_manifests(manifests)]

    assert versions == ["0.3.0", "0.2.0", "0.1.10", "0.1.9"]
