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


def test_function_catalogue_uses_public_callable_filter() -> None:
    page = _reference_index()

    assert "## Find a function" in page
    assert "Use the finder below to look up public callables from active v1 modules." in page
    assert "Search functions" in page
    assert 'placeholder="Search functions"' in page
    assert "Function type filters" in page
    assert 'data-function-type-filter="callable" checked' in page
    assert 'data-function-type-filter="internal"> Internal' not in page
    assert "Public functions intended for notebook authors." in page
    assert "For internal helper behavior, open the public callable page and expand Implementation details." in page


def test_function_catalogue_removes_essential_optional_filter_labels() -> None:
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
    page = _reference_index()

    assert re.search(r'data-function-type-filter="callable"\s+checked', page)
    assert not re.search(r'data-function-type-filter="internal"\s+checked', page)


def test_internal_functions_are_not_indexed_for_normal_catalogue_search() -> None:
    page = _reference_index()

    assert 'data-function-type="callable"' in page
    assert 'data-function-type="internal"' not in page
    assert 'class="reference-chip reference-chip-type reference-chip-internal">Internal</span>' not in page
    assert "reference/internal/" not in page


def test_finder_filters_by_function_type_and_searches_all_catalogue_fields() -> None:
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
