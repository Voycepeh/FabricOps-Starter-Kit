"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import html
import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
REFERENCE_INDEX = ROOT / "docs" / "reference" / "index.md"
CALLABLE_FINDER_JS = ROOT / "docs" / "javascripts" / "callable-finder.js"


def _reference_index() -> str:
    return REFERENCE_INDEX.read_text(encoding="utf-8")


def _finder_js() -> str:
    return CALLABLE_FINDER_JS.read_text(encoding="utf-8")


def test_function_catalogue_uses_public_starter_kit_finder() -> None:
    """Verify function catalogue searches public functions and classes."""
    page = _reference_index()

    assert "## Find a function" in page
    assert "Use the finder below to search 26 public functions and 7 public classes." in page
    assert "Search public functions and classes" in page
    assert 'placeholder="Search public functions and classes"' in page
    assert "Function taxonomy filters" not in page
    assert 'data-function-type-filter=' not in page
    assert "Workflow" not in page
    assert "Composable" not in page


def test_function_catalogue_removes_essential_optional_filter_labels() -> None:
    """Verify function catalogue removes essential optional filter labels."""
    page = _reference_index()

    assert "> Essential<" not in page
    assert "> Optional<" not in page
    assert ">Essential</strong>" not in page
    assert ">Optional</strong>" not in page
    assert "data-role-filter" not in page
    assert "data-role=" not in page
    assert "Search callable functions" not in page
    assert "Find a callable" not in page


def test_public_starter_kit_rows_are_rendered_without_taxonomy_filters() -> None:
    """Verify the catalogue has public rows without taxonomy filters."""
    page = _reference_index()

    assert 'data-function-type="public-starter-kit"' in page
    assert 'data-function-type-filter=' not in page
    assert 'data-function-type="example-only"' not in page
    assert 'data-function-type="internal"' not in page


def test_internal_functions_are_not_indexed_for_normal_catalogue_search() -> None:
    """Verify internal functions are not indexed for normal catalogue search."""
    page = _reference_index()

    assert 'data-function-type="public-starter-kit"' in page
    assert 'data-function-type="internal"' not in page
    assert 'class="reference-chip reference-chip-type reference-chip-internal">Internal</span>' not in page
    assert "reference/internal/" not in page


def test_finder_searches_public_catalogue_fields_without_type_filters() -> None:
    """Verify finder searches public catalogue fields without taxonomy filters."""
    script = _finder_js()

    assert "[data-function-type-filter]" not in script
    assert "dataset.functionTypeFilter" not in script
    assert "types.has(entry.functionType)" not in script
    assert "[data-role-filter]" not in script

    for field in (
        "row.dataset.callableName",
        "row.dataset.callableModule",
        "row.dataset.callableStarterPath",
        "row.dataset.callableUsageSource",
        "row.dataset.callablePurpose",
    ):
        assert field in script

    assert "entry.module.includes(query)" in script
    assert "entry.starterPath.includes(query)" in script
    assert "queryMatchesEntry(queryTokens, entry.tokens)" in script


def test_homepage_template_called_function_kpi_matches_reference_count() -> None:
    """Verify homepage template-called function KPI matches the reference count."""
    homepage = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")
    token_match = re.search(
        r"<!-- FABRICOPS_PUBLIC_FUNCTION_COUNT -->(.*?)<!-- /FABRICOPS_PUBLIC_FUNCTION_COUNT -->",
        homepage,
    )

    assert token_match is not None
    token_body = token_match.group(1).strip()
    token_text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", token_body)).split())

    assert token_text == "26 public callable functions"
    assert "<strong>" in token_body
    assert "<span> public callable functions</span>" in token_body
    assert 'href="reference/"' in homepage


def test_reference_defines_used_in_as_direct_code_cell_invocation() -> None:
    """Verify reference usage wording excludes imports, markdown, metadata, and internals."""
    page = _reference_index()

    assert "“Used in” means direct starter notebook code-cell invocation" in page
    assert "not import-only, markdown-only, generated metadata, example usage, or implementation helper usage" in page


def test_removed_schema_helpers_are_not_public_catalogue_entries() -> None:
    """Verify removed schema helpers are not public reference catalogue entries."""
    page = _reference_index()

    assert 'data-callable-name="validate_schema"' not in page
    assert 'data-callable-name="validate_schema_rule"' not in page


def _audit_rows() -> list[dict[str, object]]:
    """Return generated callable surface audit rows."""
    import json

    return json.loads((ROOT / "docs" / "reference" / "_data" / "callable-surface-audit.json").read_text(encoding="utf-8"))


def _core_template_called_public() -> set[str]:
    """Return exported functions classified as core template-called public functions."""
    return {str(row["function"]) for row in _audit_rows() if row["decision"] == "template_called_public"}


def _direct_template_call_set() -> set[str]:
    """Return public function names directly called by all template code cells."""
    from scripts.generate_function_reference import (
        _direct_public_template_symbols,
        parse_public_exports,
        parse_template_flow_docs,
    )

    public_symbols = set(parse_public_exports())
    called: set[str] = set()
    for flow in parse_template_flow_docs():
        called.update(_direct_public_template_symbols(flow.get("template_path", ""), public_symbols))
    return called


def _expected_direct_public_template_calls() -> set[str]:
    """Return audited exported functions directly called by template code cells."""
    return {
        str(row["function"])
        for row in _audit_rows()
        if row["in_root_exports"]
        and (row["directly_called_in_core_templates"] or row["directly_called_in_example_templates"])
    }


def _catalogue_row_names() -> set[str]:
    """Return function names rendered as Function Reference catalogue rows."""
    return set(re.findall(r'data-callable-name="([^"]+)"', _reference_index()))


def test_template_code_cell_direct_call_extractor_finds_expected_surface() -> None:
    """Verify starter template code-cell calls drive the reference surface."""
    called = _direct_template_call_set()

    assert called == _expected_direct_public_template_calls()
    assert "setup_notebook" in called
    assert "write_pipeline_run_summary" in called
    assert "get_latest_metadata_catalogue" in called
    assert "widget_pipeline_bootstrap" in called
    assert "validate_schema" not in called
    assert "validate_schema_rule" not in called
    assert "read_lakehouse_csv" not in called
    assert "read_warehouse_table" in called
    assert "write_warehouse_table" not in called


def test_reference_catalogue_rows_include_only_public_root_exports() -> None:
    """Verify catalogue rows expose only the public root export functions."""
    exported_names = {str(row["function"]) for row in _audit_rows() if row["in_root_exports"]}

    assert (_core_template_called_public() - {"FabricStore", "PathConfig", "GovernanceConfig", "DataAgreementConfig", "FrameworkConfig"}) <= _catalogue_row_names()
    assert _catalogue_row_names() == exported_names
    assert len(_catalogue_row_names()) == 33


def test_root_exported_catalogue_functions_have_standalone_pages() -> None:
    """Verify root-exported catalogue functions have standalone pages."""
    api_reference_dir = ROOT / "docs" / "api" / "reference"
    exported_names = {str(row["function"]) for row in _audit_rows() if row["in_root_exports"]}

    for name in sorted(exported_names):
        assert (api_reference_dir / f"{name}.md").exists(), name


def test_exported_advanced_helpers_keep_standalone_pages_after_audit() -> None:
    """Verify audited advanced public helpers keep standalone function pages."""
    api_reference_dir = ROOT / "docs" / "api" / "reference"
    page_names = {path.stem for path in api_reference_dir.glob("*.md")}
    exported_names = {str(row["function"]) for row in _audit_rows() if row["in_root_exports"]}

    assert page_names == exported_names
    assert "read_lakehouse_table" in page_names
    assert "write_lakehouse_table" in page_names
    assert "read_lakehouse_csv" in page_names
    assert "write_warehouse_table" in page_names



def test_explicit_io_helpers_are_public_catalogue_functions() -> None:
    """Verify explicit IO helpers are public catalogue functions."""
    page = _reference_index()

    for name in (
        "read_lakehouse_csv",
        "read_lakehouse_excel",
        "read_lakehouse_parquet",
        "read_lakehouse_table",
        "read_warehouse_query",
        "read_warehouse_table",
        "write_lakehouse_table",
        "write_warehouse_table",
    ):
        assert f'data-callable-name="{name}"' in page


def test_functions_with_blank_starter_path_are_not_counted() -> None:
    """Verify catalogue excludes functions with no direct starter path."""
    page = _reference_index()

    assert 'data-callable-starter-path="—"' not in page


def test_root_exports_match_callable_surface_audit() -> None:
    """Verify root exports match callable surface audit rows."""
    import fabricops_kit

    audit_names = {str(row["function"]) for row in _audit_rows() if row["in_root_exports"]}
    assert set(fabricops_kit.__all__) == audit_names


def test_convert_to_internal_audit_rows_are_not_root_exports() -> None:
    """Verify convert-to-internal audit decisions are not root exports."""
    import fabricops_kit

    internal_names = {str(row["function"]) for row in _audit_rows() if row["decision"] == "convert_to_internal"}
    assert internal_names.isdisjoint(set(fabricops_kit.__all__))


def test_example_template_only_helpers_do_not_inflate_public_catalogue() -> None:
    """Verify example-template-only helpers stay out of the public catalogue."""
    example_template_only = {
        str(row["function"])
        for row in _audit_rows()
        if row["directly_called_in_example_templates"] and not row["directly_called_in_core_templates"]
    }

    assert example_template_only.isdisjoint(_core_template_called_public())
    assert example_template_only.isdisjoint(_catalogue_row_names())


def test_format_specific_io_and_internal_guardrails_are_not_root_exported() -> None:
    """Verify low-level IO and internal guardrail helpers are absent from root exports."""
    import fabricops_kit

    root_exports = set(fabricops_kit.__all__)
    assert {"read_lakehouse_table", "write_lakehouse_table"} <= root_exports
    assert {"stop_if_failed", "write_catalogue_evidence"}.isdisjoint(root_exports)


def test_retired_function_taxonomy_audit_is_removed() -> None:
    """Verify the old taxonomy audit artifact is no longer generated."""
    assert not (ROOT / "docs" / "reference" / "_data" / "function-taxonomy-audit.json").exists()
