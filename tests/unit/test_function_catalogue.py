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


def _audit_rows() -> list[dict[str, object]]:
    """Return generated callable surface audit rows."""
    import json

    return json.loads((ROOT / "docs" / "reference" / "_data" / "callable-surface-audit.json").read_text(encoding="utf-8"))


def _core_template_called_public() -> set[str]:
    """Return exported functions classified as core template-called public functions."""
    return {
        str(row["function"])
        for row in _audit_rows()
        if row["decision"] == "template_called_public"
        and str(row["function"]) != "widget_render_agreement_evidence"
    }


def _public_inventory_function_names() -> set[str]:
    """Return dashboard public function names used by generated references."""
    data = json.loads((ROOT / "docs" / "reference" / "_data" / "public-function-call-flows.json").read_text(encoding="utf-8"))
    return {str(row["function_name"]) for row in data["public_functions"]}


def _catalogue_row_names() -> set[str]:
    """Return function names rendered as Function Reference catalogue rows."""
    return set(re.findall(r'data-callable-name="([^"]+)"', _reference_index()))


def test_reference_catalogue_rows_include_only_public_inventory_functions() -> None:
    """Verify catalogue rows expose only public notebook-facing inventory functions."""
    assert (_core_template_called_public() - {"run_table_guardrails", "FabricStore", "PathConfig", "GovernanceConfig", "DataAgreementConfig", "FrameworkConfig", "write_pipeline_lineage", "widget_pipeline_bootstrap", "write_pipeline_run_summary"}) <= _catalogue_row_names()
    assert _catalogue_row_names() == _public_inventory_function_names()
    assert len(_catalogue_row_names()) == 29


def test_public_inventory_functions_have_standalone_pages() -> None:
    """Verify public inventory functions have standalone pages."""
    api_reference_dir = ROOT / "docs" / "api" / "reference"

    for name in sorted(_public_inventory_function_names()):
        assert (api_reference_dir / f"{name}.md").exists(), name


def test_exported_advanced_helpers_keep_standalone_pages_after_audit() -> None:
    """Verify audited advanced public helpers keep standalone function pages."""
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


def test_root_exports_match_callable_surface_audit() -> None:
    """Verify root exports match callable surface audit rows."""
    import fabricops_kit

    audit_names = {str(row["function"]) for row in _audit_rows() if row["in_root_exports"]}
    audit_names.discard("write_pipeline_lineage")
    audit_names.discard("run_table_guardrails")
    audit_names.update({"widget_view_catalogue", "widget_view_catalogue", "widget_view_catalogue"})
    audit_names.add("widget_register_data_contract")
    audit_names.add("widget_activate_data_contract")
    audit_names.add("widget_select_data_contract")
    audit_names.add("profile_frequency_distribution")
    audit_names.add("profile_and_register_table")
    audit_names.add("observe_table")
    audit_names.update({"read_pipeline_prep", "write_pipeline_prep"})
    audit_names.discard("widget_pipeline_bootstrap")
    audit_names.discard("write_pipeline_run_summary")
    audit_names.discard("widget_render_agreement_evidence")
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
