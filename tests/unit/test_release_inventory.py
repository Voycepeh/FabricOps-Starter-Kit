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


def test_load_release_manifests_reads_default_manifest_directory():
    """Verify the no-argument loader preserves release-page default discovery."""
    manifests = ri.load_release_manifests()

    assert [manifest["release_version"] for manifest in manifests] == [ri.read_package_version()]


def test_load_release_manifests_reads_only_supplied_directory(tmp_path):
    """Verify custom manifest directories are isolated from repository manifests."""
    manifests_dir = tmp_path / "manifests"
    manifests_dir.mkdir()
    (manifests_dir / "0.2.0.yml").write_text(
        "release_version: 0.2.0\n"
        "release_status: live\n"
        "release_date: 2026-08-01\n"
        "functions:\n"
        "metadata_tables:\n"
        "templates:\n"
        "dq_rules:\n",
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
        "templates": [],
        "dq_rules": [],
    }

    ri._validate_manifest(manifest, "1.0.0")


def test_malformed_live_release_dates_fail_clearly():
    """Verify Live release dates reject prose, malformed dates, and timestamps."""
    for release_date in [None, "yesterday", "2026-7-8", "2026-07-08T00:00:00"]:
        manifest = {
            "release_version": "1.0.0",
            "release_status": "live",
            "release_date": release_date,
            "functions": [],
            "metadata_tables": [],
            "templates": [],
            "dq_rules": [],
        }
        with pytest.raises(ValueError, match="must include release_date in YYYY-MM-DD format"):
            ri._validate_manifest(manifest, "1.0.0")


def test_release_contract_pages_render_live_only_local_inventory():
    """Verify release overview inventory contains only Live local detail links."""
    ri.render_release_pages()
    version = ri.read_package_version()
    content = (ri.ROOT / "docs" / "releases" / version / "index.md").read_text(encoding="utf-8")
    assert "| Function | Description |" in content
    assert "[`read_lakehouse_table`](functions/read_lakehouse_table.md)" in content
    assert "docs/api/reference" not in content
    assert "| Status | Name | Documentation | Source |" not in content
    assert "src/fabricops_kit/io/read_lakehouse_table.py" not in content
    assert 'fabricops-release-status fabricops-release-status--live">Live</span>' in content
    assert 'fabricops-release-status fabricops-release-status--preview">Preview</span>' not in content


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
    """Verify release notes come from the matching changelog section."""
    assert "first supported FabricOps Starter Kit release" in ri.extract_changelog_notes(ri.read_package_version())


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
    assert sum(1 for item in manifest["templates"] if item["status"] == "live") == 3
    assert sum(1 for item in manifest["metadata_tables"] if item["status"] == "live") == 4
    assert any(item["status"] == "preview" for item in manifest["functions"])
    assert any(item["status"] == "preview" for item in manifest["templates"])
    assert all(item["status"] == "preview" for item in manifest["dq_rules"])


def test_release_generates_exact_live_detail_pages_and_no_preview_pages():
    """Verify frozen details exist only where release-specific details are useful."""
    ri.render_release_pages()
    base = ri.ROOT / "docs" / "releases" / ri.read_package_version()
    assert len(list((base / "functions").glob("*.md"))) == 9
    assert len(list((base / "metadata").glob("*.md"))) == 4
    assert not (base / "templates").exists()
    assert not (base / "dq-rules").exists()
    assert not (base / "functions" / "index.md").exists()
    assert not (base / "metadata" / "index.md").exists()
    assert not (base / "functions" / "setup_notebook.md").exists()


def test_release_overview_lists_live_inventory_in_collapsible_sections():
    """Verify release overview sections include counts and direct asset links."""
    ri.render_release_pages()
    content = (ri.ROOT / "docs" / "releases" / ri.read_package_version() / "index.md").read_text(encoding="utf-8")

    assert '<details class="fabricops-release-inventory" markdown>' in content
    assert "<summary>9 Live functions</summary>" in content
    assert "<summary>4 Live metadata tables</summary>" in content
    assert "<summary>3 Live notebook templates</summary>" in content
    assert "Live dq rules" not in content
    assert "| Function | Description |" in content
    assert "| Metadata table | Purpose |" in content
    assert "| Notebook template | Purpose |" in content
    assert "[`profile_dataframe`](functions/profile_dataframe.md)" in content
    assert "[`METADATA_DATA_CATALOGUE`](metadata/metadata_data_catalogue.md)" in content
    assert "[`00_env_config`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/v0.1.0/templates/notebooks/00_env_config.ipynb)" in content
    assert "/blob/main/" not in content
    assert "| Status |" not in content
    assert "Details" not in content
    assert "[Open]" not in content


def test_live_release_requires_release_date():
    """Verify Live release manifests must include a release date."""
    manifest = {"release_version": "1.0.0", "release_status": "live", "release_date": None, "functions": [], "metadata_tables": [], "templates": [], "dq_rules": []}

    with pytest.raises(ValueError, match="must include release_date"):
        ri._validate_manifest(manifest, "1.0.0")


def test_individual_release_overview_is_concise_record():
    """Verify individual release overview uses the concise release-record layout."""
    ri.render_release_pages()
    version = ri.read_package_version()
    content = (ri.ROOT / "docs" / "releases" / version / "index.md").read_text(encoding="utf-8")

    assert "- Release date: `2026-07-08`" in content
    assert '<a class="md-button md-button--primary" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/releases/tag/v0.1.0">' in content
    assert "View GitHub Release" in content
    assert "## Downloads" not in content
    assert "Download wheel" not in content
    assert "Download source distribution" not in content
    assert "Download notebook pack" not in content
    assert "SHA256SUMS.txt" not in content
    assert "## Get started" not in content
    assert "## Why this release exists" not in content
    assert "\n## Known limitations" not in content
    assert "\n## Upgrade instructions" not in content
    assert content.count("## Changelog") == 1
    assert "### Added" in content
    assert "### Known limitations" in content
    assert "### Upgrade instructions" in content
    assert "<summary>9 Live functions</summary>" in content
    assert "<summary>4 Live metadata tables</summary>" in content
    assert "<summary>3 Live notebook templates</summary>" in content


def test_release_inventory_section_supports_dq_links_and_omits_empty_groups():
    """Verify DQ sections link directly to detail pages and empty groups are omitted."""
    manifest = {"github_owner": "Voycepeh", "github_repo": "FabricOps-Starter-Kit"}
    live = {"functions": [], "metadata_tables": [], "templates": [], "dq_rules": [{"name": "not_null", "purpose": "Values must be present."}]}

    sections = ri._release_inventory_sections(manifest, "1.2.3", live)
    content = "\n".join(sections)

    assert "<summary>1 Live DQ rules</summary>" in content
    assert "| DQ rule | Purpose |" in content
    assert "[`not_null`](dq-rules/not-null.md)" in content
    assert "Live functions" not in content
    assert "Live metadata tables" not in content
    assert "Live notebook templates" not in content


def test_release_detail_back_links_return_to_release_overview():
    """Verify detail page back links return directly to the release overview."""
    ri.render_release_pages()
    base = ri.ROOT / "docs" / "releases" / ri.read_package_version()
    for path in [base / "functions" / "read_lakehouse_excel.md", base / "metadata" / "metadata_data_catalogue.md"]:
        content = path.read_text(encoding="utf-8")
        assert "[Back to release overview](../index.md)" in content
        assert "[Back to 0.1.0" not in content


def test_no_release_table_uses_raw_source_path_columns():
    """Verify public release inventory tables avoid raw source/documentation columns."""
    for path in (ri.ROOT / "docs" / "releases" / ri.read_package_version()).glob("**/*.md"):
        content = path.read_text(encoding="utf-8")
        assert "| Status | Name | Documentation | Source |" not in content
        assert "Documentation | Source" not in content


def test_generated_release_pages_have_required_notice():
    """Verify generated release pages declare their generated ownership."""
    prefix = "<!-- Generated file. Edit docs/releases/manifests/0.1.0.yml or the authoritative source metadata and regenerate. -->"
    for path in (ri.ROOT / "docs" / "releases" / ri.read_package_version()).glob("**/*.md"):
        assert path.read_text(encoding="utf-8").startswith(prefix)


def test_release_generation_is_deterministic_and_second_run_clean():
    """Verify rendering twice produces identical page content."""
    ri.render_release_pages()
    first = {p.relative_to(ri.ROOT).as_posix(): p.read_text(encoding="utf-8") for p in (ri.ROOT / "docs" / "releases").glob("**/*.md")}
    ri.render_release_pages()
    second = {p.relative_to(ri.ROOT).as_posix(): p.read_text(encoding="utf-8") for p in (ri.ROOT / "docs" / "releases").glob("**/*.md")}
    assert first == second


def test_mkdocs_navigation_links_only_release_overview():
    """Verify 0.1.0 navigation omits removed category summary pages."""
    content = (ri.ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    assert "0.1.0: releases/0.1.0/index.md" in content
    assert "releases/0.1.0/functions/index.md" not in content
    assert "releases/0.1.0/metadata/index.md" not in content
    assert "releases/0.1.0/templates/index.md" not in content
    assert "releases/0.1.0/dq-rules/index.md" not in content


def test_release_renderer_creates_version_directory():
    """Verify release renderer creates the version directory automatically."""
    assert (ri.ROOT / "docs" / "releases" / ri.read_package_version()).is_dir()


def test_release_notebook_pack_uses_live_manifest_templates(tmp_path):
    """Verify the release notebook ZIP is built from Live template manifest entries."""
    path = ri.build_notebook_pack(ri.read_package_version(), tmp_path)
    manifest = ri._load_manifest(ri.manifest_path(ri.read_package_version()))
    assert manifest is not None
    expected = sorted(f"{item['name']}.ipynb" for item in manifest["templates"] if item["status"] == "live")
    import zipfile

    with zipfile.ZipFile(path) as archive:
        assert sorted(archive.namelist()) == expected
    assert "02_pipeline.ipynb" not in expected


def test_metadata_manifest_records_schema_since_and_fingerprint():
    """Verify metadata schemas are tied to package releases by fingerprint."""
    manifest = ri._load_manifest(ri.manifest_path(ri.read_package_version()))
    assert manifest is not None
    agreement = next(item for item in manifest["metadata_tables"] if item["name"] == "METADATA_DATA_AGREEMENT")
    assert agreement["live_since"] == "0.1.0"
    assert agreement["schema_since"] == "0.1.0"
    assert len(agreement["schema_fingerprint"]) == 64


def test_metadata_schema_since_is_preserved_when_fingerprint_unchanged():
    """Verify schema_since does not advance when a schema fingerprint is unchanged."""
    existing = {
        "release_version": "0.1.1",
        "functions": [],
        "templates": [],
        "dq_rules": [],
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
        "templates": [],
        "dq_rules": [],
        "metadata_tables": [ri.ReleaseAsset("METADATA_DATA_AGREEMENT", "new.py", generated_fields={"schema_fingerprint": "same"})],
    }
    manifest = ri.synchronize_manifest(existing, discovered, "0.1.1")
    assert manifest["metadata_tables"][0]["schema_since"] == "0.1.0"


def test_metadata_schema_since_advances_when_fingerprint_changes():
    """Verify schema_since moves to the package version when schema structure changes."""
    existing = {
        "release_version": "0.2.0",
        "functions": [],
        "templates": [],
        "dq_rules": [],
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
        "templates": [],
        "dq_rules": [],
        "metadata_tables": [ri.ReleaseAsset("METADATA_DATA_AGREEMENT", "new.py", generated_fields={"schema_fingerprint": "new"})],
    }
    manifest = ri.synchronize_manifest(existing, discovered, "0.2.0")
    assert manifest["metadata_tables"][0]["schema_since"] == "0.2.0"


def test_release_history_index_renders_all_manifests_as_sorted_table_rows():
    """Verify release manifests render as newest-first release history rows."""
    manifests = [
        {
            "release_version": "0.1.0",
            "release_date": "2026-07-08",
            "release_motivation": "Initial governed Fabric notebook workflows. Extra detail omitted.",
        },
        {
            "release_version": "0.2.0",
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
