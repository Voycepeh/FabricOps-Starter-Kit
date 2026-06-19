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
    assert "Use the finder below to look up exported public functions from active v1 modules." in page
    assert "Search functions" in page
    assert 'placeholder="Search functions"' in page
    assert "Function type filters" in page
    assert 'data-function-type-filter="template-called" checked' in page
    assert 'data-function-type-filter="advanced-public" checked' in page
    assert 'data-function-type-filter="example-only" checked' in page
    assert 'data-function-type-filter="internal"> Internal' not in page
    assert "Advanced public" in page
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

    assert re.search(r'data-function-type-filter="template-called"\s+checked', page)
    assert re.search(r'data-function-type-filter="advanced-public"\s+checked', page)
    assert re.search(r'data-function-type-filter="example-only"\s+checked', page)
    assert not re.search(r'data-function-type-filter="internal"\s+checked', page)


def test_internal_functions_are_not_indexed_for_normal_catalogue_search() -> None:
    """Verify internal functions are not indexed for normal catalogue search."""
    page = _reference_index()

    assert 'data-function-type="template-called"' in page
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

    assert f'<div class="fabricops-kpi-number">{len(_core_template_called_public())}</div>' in homepage
    assert '<div class="fabricops-kpi-label">starter-kit-functions</div>' in homepage
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


def _catalogue_row_names() -> set[str]:
    """Return function names rendered as Function Reference catalogue rows."""
    return set(re.findall(r'data-callable-name="([^"]+)"', _reference_index()))


def test_template_code_cell_direct_call_extractor_finds_expected_surface() -> None:
    """Verify starter template code-cell calls drive the reference surface."""
    called = _direct_template_call_set()

    assert len(called) == 23
    assert "setup_notebook" in called
    assert "write_pipeline_run_summary" in called
    assert "get_latest_metadata_catalogue" in called
    assert "start_pipeline_run" in called
    assert "validate_schema" not in called
    assert "validate_schema_rule" not in called
    assert "read_lakehouse_csv" not in called
    assert "read_warehouse_table" not in called
    assert "write_warehouse_table" not in called


def test_reference_catalogue_rows_include_all_exported_public_functions() -> None:
    """Verify catalogue rows keep all exported functions while classifying template use."""
    exported_names = {str(row["function"]) for row in _audit_rows() if row["in_root_exports"]}

    assert _core_template_called_public() <= _catalogue_row_names()
    assert _catalogue_row_names() == exported_names


def test_every_counted_function_has_standalone_page() -> None:
    """Verify every counted template-called function has a standalone page."""
    api_reference_dir = ROOT / "docs" / "api" / "reference"

    for name in sorted(_catalogue_row_names()):
        assert (api_reference_dir / f"{name}.md").exists(), name


def test_exported_advanced_helpers_keep_standalone_pages_after_audit() -> None:
    """Verify audited advanced public helpers keep standalone function pages."""
    api_reference_dir = ROOT / "docs" / "api" / "reference"
    page_names = {path.stem for path in api_reference_dir.glob("*.md")}
    exported_names = {str(row["function"]) for row in _audit_rows() if row["in_root_exports"]}

    assert page_names == exported_names
    assert "read_data" in page_names
    assert "write_data" in page_names
    assert "read_lakehouse_csv" not in page_names
    assert "write_warehouse_table" not in page_names


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


def test_example_only_helpers_do_not_inflate_core_count() -> None:
    """Verify example-only helpers are tracked outside the core count."""
    example_only = {
        str(row["function"])
        for row in _audit_rows()
        if row["directly_called_in_example_templates"] and not row["directly_called_in_core_templates"]
    }

    assert "enforce_dq_rules" in example_only
    assert example_only.isdisjoint(_core_template_called_public())
    assert example_only <= _catalogue_row_names()
    page = _reference_index()
    for name in example_only:
        assert f'data-callable-name="{name}"' in page
        assert 'data-function-type="example-only"' in page


def test_format_specific_io_and_internal_guardrails_are_not_root_exported() -> None:
    """Verify low-level IO and internal guardrail helpers are absent from root exports."""
    import fabricops_kit

    root_exports = set(fabricops_kit.__all__)
    assert {"read_data", "write_data"} <= root_exports
    assert {
        "read_lakehouse_csv",
        "read_lakehouse_excel",
        "read_lakehouse_parquet",
        "read_lakehouse_table",
        "read_warehouse_table",
        "write_lakehouse_table",
        "write_warehouse_table",
        "stop_if_failed",
        "write_catalogue_evidence",
    }.isdisjoint(root_exports)
