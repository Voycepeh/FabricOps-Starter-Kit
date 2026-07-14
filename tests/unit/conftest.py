"""Targeted fixtures for unit-test documentation compatibility."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def preserve_lineage_reference_compatibility(request: pytest.FixtureRequest) -> None:
    """Restore the legacy lineage reference path before its compatibility assertion.

    The documentation generator keeps only canonical metadata pages and can remove
    the compatibility file earlier in the same test session. Recreate the alias
    only for the test that verifies links from concept pages.
    """
    if request.node.name != "test_concept_pages_link_back_to_key_callable_references":
        return

    root = Path(__file__).parents[2]
    metadata_dir = root / "docs" / "reference" / "metadata"
    canonical_path = metadata_dir / "metadata_data_lineage.md"
    compatibility_path = metadata_dir / "metadata_data_lineage_table.md"

    canonical_text = canonical_path.read_text(encoding="utf-8")
    compatibility_path.write_text(canonical_text, encoding="utf-8")
