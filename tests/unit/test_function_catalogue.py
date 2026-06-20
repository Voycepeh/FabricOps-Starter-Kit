"""Test FabricOps function reference public-surface contracts."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
REFERENCE_INDEX = ROOT / "docs" / "reference" / "index.md"
CALLABLE_FINDER_JS = ROOT / "docs" / "javascripts" / "callable-finder.js"
API_REFERENCE_DIR = ROOT / "docs" / "api" / "reference"
PUBLIC_WORDING = (
    "Workflow",
    "Composable",
    "Orchestrator",
    "Utility",
    "Advanced public",
    "Template-called",
    "Example-only",
)


def _reference_index() -> str:
    """Return the generated function reference page text."""
    return REFERENCE_INDEX.read_text(encoding="utf-8")


def _finder_js() -> str:
    """Return the callable finder JavaScript."""
    return CALLABLE_FINDER_JS.read_text(encoding="utf-8")


def _audit_rows() -> list[dict[str, object]]:
    """Return generated callable surface audit rows."""
    return json.loads((ROOT / "docs" / "reference" / "_data" / "callable-surface-audit.json").read_text(encoding="utf-8"))


def _function_manifest() -> list[dict[str, object]]:
    """Return generated function manifest entries."""
    return json.loads((ROOT / "docs" / "reference" / "_data" / "function-manifest.json").read_text(encoding="utf-8"))


def _public_names() -> set[str]:
    """Return public Starter Kit function names from generated audit metadata."""
    return {str(row["function"]) for row in _audit_rows() if row["in_root_exports"]}


def _catalogue_row_names() -> set[str]:
    """Return function names rendered as Function Reference catalogue rows."""
    return set(re.findall(r'data-callable-name="([^"]+)"', _reference_index()))


def test_public_starter_kit_catalogue_has_no_taxonomy_filters() -> None:
    """Verify the reference catalogue only searches public Starter Kit functions."""
    page = _reference_index()

    assert "## Find a function" in page
    assert "20 public Starter Kit functions" in page
    assert "252 supporting internal functions" in page
    assert "Search functions" in page
    assert 'placeholder="Search functions"' in page
    assert "Search by function name, module, starter path, usage source, or description." in page
    assert "Function taxonomy filters" not in page
    assert "data-function-type-filter" not in page
    assert "data-function-type=" not in page
    for wording in PUBLIC_WORDING:
        assert wording not in page


def test_finder_keeps_search_and_removes_taxonomy_filter_logic() -> None:
    """Verify finder JavaScript searches public rows without category filters."""
    script = _finder_js()

    assert "[data-function-type-filter]" not in script
    assert "dataset.functionTypeFilter" not in script
    assert "types.has(entry.functionType)" not in script
    assert "row.dataset.callableName" in script
    assert "row.dataset.callableModule" in script
    assert "row.dataset.callableStarterPath" in script
    assert "row.dataset.callableUsageSource" in script
    assert "row.dataset.callablePurpose" in script
    assert "entry.module.includes(query)" in script
    assert "entry.starterPath.includes(query)" in script
    assert "queryMatchesEntry(queryTokens, entry.tokens)" in script


def test_public_count_and_catalogue_rows_match_generated_metadata() -> None:
    """Verify generated metadata drives the 20-function public surface."""
    public_names = _public_names()
    manifest = _function_manifest()
    public_manifest = {str(row["name"]) for row in manifest if row["classification"] == "Callable"}
    internal_manifest = [row for row in manifest if row["classification"] != "Callable"]

    assert len(public_names) == 20
    assert public_manifest == public_names
    assert _catalogue_row_names() == public_names
    assert len(internal_manifest) == 252


def test_only_public_starter_kit_functions_have_standalone_pages() -> None:
    """Verify support functions do not get standalone public callable pages."""
    page_names = {path.stem for path in API_REFERENCE_DIR.glob("*.md")}
    public_names = _public_names()

    assert page_names == public_names
    assert "read_data" in page_names
    assert "write_data" in page_names
    for internal_name in (
        "get_selected_agreement",
        "widget_select_agreement",
        "read_lakehouse_csv",
        "read_lakehouse_table",
        "write_lakehouse_table",
        "read_warehouse_table",
        "write_warehouse_table",
        "_get_store",
    ):
        assert internal_name not in page_names
        assert f'data-callable-name="{internal_name}"' not in _reference_index()


def test_homepage_counts_align_with_generated_metadata() -> None:
    """Verify the landing page count matches generated metadata."""
    homepage = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")
    public_count = len(_public_names())
    internal_count = sum(1 for row in _function_manifest() if row["classification"] != "Callable")

    assert f"{public_count} public Starter Kit functions" in homepage
    assert f"{internal_count} supporting internal functions" in homepage
    assert 'href="reference/"' in homepage


def test_refactor_signals_remain_available_for_maintainer_review() -> None:
    """Verify refactor signals are still generated after removing taxonomy output."""
    signals_path = ROOT / "docs" / "reference" / "_data" / "refactor-signals.json"
    signals = json.loads(signals_path.read_text(encoding="utf-8"))

    assert signals
    assert set(signals) == _public_names()
    assert "run_table_guardrails" in signals
    assert signals["run_table_guardrails"]["qualified_name"].endswith(".run_table_guardrails")


def test_underscore_prefixed_functions_remain_internal() -> None:
    """Verify underscore-prefixed functions are never public catalogue entries."""
    manifest = _function_manifest()
    underscore_rows = [row for row in manifest if str(row["name"]).startswith("_")]

    assert underscore_rows
    assert all(row["classification"] != "Callable" for row in underscore_rows)
    assert all(str(row["name"]) not in _catalogue_row_names() for row in underscore_rows)


def test_removed_taxonomy_audit_file_is_not_generated() -> None:
    """Verify taxonomy audit data was removed from generated data files."""
    assert not (ROOT / "docs" / "reference" / "_data" / "function-taxonomy-audit.json").exists()
