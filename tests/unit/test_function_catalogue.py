"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
REFERENCE_INDEX = ROOT / "docs" / "reference" / "index.md"
CALLABLE_FINDER_JS = ROOT / "docs" / "javascripts" / "callable-finder.js"


def _reference_index() -> str:
    return REFERENCE_INDEX.read_text(encoding="utf-8")


def _finder_js() -> str:
    return CALLABLE_FINDER_JS.read_text(encoding="utf-8")


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


def test_removed_schema_helpers_are_not_public_catalogue_entries() -> None:
    """Verify removed schema helpers are not public reference catalogue entries."""
    page = _reference_index()

    assert 'data-callable-name="validate_schema"' not in page
    assert 'data-callable-name="validate_schema_rule"' not in page


def _public_inventory_function_names() -> set[str]:
    """Return dashboard public function names used by generated references."""
    data = json.loads((ROOT / "docs" / "reference" / "_data" / "public-function-call-flows.json").read_text(encoding="utf-8"))
    return {str(row["function_name"]) for row in data["public_functions"]}


def _catalogue_row_names() -> set[str]:
    """Return function names rendered as Function Reference catalogue rows."""
    return set(re.findall(r'data-callable-name="([^"]+)"', _reference_index()))


def test_reference_catalogue_rows_include_only_public_inventory_functions() -> None:
    """Verify catalogue rows expose only public notebook-facing inventory functions."""
    assert _catalogue_row_names() == _public_inventory_function_names()


def test_public_inventory_functions_have_standalone_pages() -> None:
    """Verify public inventory functions have standalone pages."""
    api_reference_dir = ROOT / "docs" / "api" / "reference"

    for name in sorted(_public_inventory_function_names()):
        assert (api_reference_dir / f"{name}.md").exists(), name


def test_public_inventory_has_no_extra_or_missing_standalone_pages() -> None:
    """Verify standalone pages exactly match the current public inventory."""
    api_reference_dir = ROOT / "docs" / "api" / "reference"
    page_names = {path.stem for path in api_reference_dir.glob("*.md")}
    assert page_names == _public_inventory_function_names()
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


def test_root_function_exports_match_public_call_flow_inventory() -> None:
    """Verify package-root function exports match the current call-flow inventory."""
    import inspect

    import fabricops_kit

    root_function_exports = {
        name for name in fabricops_kit.__all__ if inspect.isfunction(getattr(fabricops_kit, name))
    }
    assert root_function_exports == _public_inventory_function_names()


def test_format_specific_io_and_internal_guardrails_are_not_root_exported() -> None:
    """Verify low-level IO and internal guardrail helpers are absent from root exports."""
    import fabricops_kit

    root_exports = set(fabricops_kit.__all__)
    assert {"read_lakehouse_table", "write_lakehouse_table"} <= root_exports
    assert {"stop_if_failed", "write_catalogue_evidence"}.isdisjoint(root_exports)


def test_retired_function_taxonomy_audit_is_removed() -> None:
    """Verify the old taxonomy audit artifact is no longer generated."""
    assert not (ROOT / "docs" / "reference" / "_data" / "function-taxonomy-audit.json").exists()


def test_retired_callable_surface_audit_is_removed() -> None:
    """Verify the obsolete parallel callable inventory remains retired."""
    assert not (ROOT / "docs" / "reference" / "_data" / "callable-surface-audit.json").exists()
