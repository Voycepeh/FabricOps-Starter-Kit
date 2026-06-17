"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
REFERENCE_INDEX = ROOT / "docs" / "reference" / "index.md"
CALLABLE_FINDER_JS = ROOT / "docs" / "javascripts" / "callable-finder.js"


def _reference_index() -> str:
    return REFERENCE_INDEX.read_text(encoding="utf-8")


def _finder_js() -> str:
    return CALLABLE_FINDER_JS.read_text(encoding="utf-8")


def test_function_catalogue_uses_template_called_filter() -> None:
    """Verify function catalogue uses template-called function filter."""
    page = _reference_index()

    assert "## Find a function" in page
    assert "Use the finder below to look up template-called public functions from active v1 modules." in page
    assert "Search functions" in page
    assert 'placeholder="Search functions"' in page
    assert "Function type filters" in page
    assert 'data-function-type-filter="callable" checked' in page
    assert 'data-function-type-filter="internal"> Internal' not in page
    assert "Template-called public functions used by starter notebook code cells." in page
    assert "For internal helper behavior, open the public function page and expand the Internal implementation summary." in page


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


def test_callable_is_default_and_internal_is_opt_in() -> None:
    """Verify callable is default and internal is opt in."""
    page = _reference_index()

    assert re.search(r'data-function-type-filter="callable"\s+checked', page)
    assert not re.search(r'data-function-type-filter="internal"\s+checked', page)


def test_internal_functions_are_not_indexed_for_normal_catalogue_search() -> None:
    """Verify internal functions are not indexed for normal catalogue search."""
    page = _reference_index()

    assert 'data-function-type="callable"' in page
    assert 'data-function-type="internal"' not in page
    assert 'class="reference-chip reference-chip-type reference-chip-internal">Internal</span>' not in page
    assert "reference/internal/" not in page


def test_finder_filters_by_function_type_and_searches_all_catalogue_fields() -> None:
    """Verify finder filters by function type and searches all catalogue fields."""
    script = _finder_js()

    assert "[data-function-type-filter]" in script
    assert "dataset.functionTypeFilter" in script
    assert "types.has(entry.functionType)" in script
    assert "[data-role-filter]" not in script

    for field in (
        "row.dataset.callableName",
        "row.dataset.callableModule",
        "row.dataset.callableStarterPath",
        "row.dataset.functionType",
        "row.dataset.callablePurpose",
    ):
        assert field in script

    assert "entry.module.includes(query)" in script
    assert "entry.functionType.includes(query)" in script
    assert "entry.starterPath.includes(query)" in script
    assert "queryMatchesEntry(queryTokens, entry.tokens)" in script


def test_homepage_template_called_function_kpi_matches_reference_count() -> None:
    """Verify homepage template-called function KPI matches the reference count."""
    homepage = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")

    assert f'<div class="fabricops-kpi-number">{len(_direct_template_call_set())}</div>' in homepage
    assert '<div class="fabricops-kpi-label">template-called functions</div>' in homepage
    assert "without counting import-only or lower-level helpers" in homepage


def test_reference_defines_used_in_as_direct_code_cell_invocation() -> None:
    """Verify reference usage wording excludes imports, markdown, metadata, and internals."""
    page = _reference_index()

    assert "“Used in” means direct starter notebook code-cell invocation" in page
    assert "not import-only, markdown-only, generated metadata, or internal helper usage" in page


def test_removed_schema_helpers_are_not_public_catalogue_entries() -> None:
    """Verify removed schema helpers are not public reference catalogue entries."""
    page = _reference_index()

    assert 'data-callable-name="validate_schema"' not in page
    assert 'data-callable-name="validate_schema_rule"' not in page


def _direct_template_call_set() -> set[str]:
    """Return public function names directly called by starter template code cells."""
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


def _catalogue_row_names() -> set[str]:
    """Return function names rendered as Function Reference catalogue rows."""
    return set(re.findall(r'data-callable-name="([^"]+)"', _reference_index()))


def test_template_code_cell_direct_call_extractor_finds_expected_surface() -> None:
    """Verify starter template code-cell calls drive the reference surface."""
    called = _direct_template_call_set()

    assert len(called) == 24
    assert "setup_notebook" in called
    assert "write_pipeline_run_summary" in called
    assert "validate_schema" not in called
    assert "validate_schema_rule" not in called
    assert "read_lakehouse_csv" not in called
    assert "read_warehouse_table" not in called
    assert "write_warehouse_table" not in called


def test_reference_catalogue_rows_match_direct_template_calls() -> None:
    """Verify catalogue rows exactly match direct starter template calls."""
    assert _catalogue_row_names() == _direct_template_call_set()


def test_every_counted_function_has_standalone_page() -> None:
    """Verify every counted template-called function has a standalone page."""
    api_reference_dir = ROOT / "docs" / "api" / "reference"

    for name in sorted(_catalogue_row_names()):
        assert (api_reference_dir / f"{name}.md").exists(), name


def test_no_uncalled_function_has_standalone_page() -> None:
    """Verify uncalled public helpers do not have standalone function pages."""
    api_reference_dir = ROOT / "docs" / "api" / "reference"
    page_names = {path.stem for path in api_reference_dir.glob("*.md")}

    assert page_names == _direct_template_call_set()


def test_functions_with_blank_starter_path_are_not_counted() -> None:
    """Verify catalogue excludes functions with no direct starter path."""
    page = _reference_index()

    assert 'data-callable-starter-path="—"' not in page
