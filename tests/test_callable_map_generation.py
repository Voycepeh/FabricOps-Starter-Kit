from __future__ import annotations

from pathlib import Path

from scripts.generate_function_reference import main as generate_reference

ROOT = Path(__file__).resolve().parents[1]
CALLABLE_MAP_FILE = ROOT / "docs" / "reference" / "callable-map.md"
DEPENDENCY_METADATA_FILE = ROOT / "docs" / "reference" / "dependency-metadata.json"


def test_public_callable_map_page_is_not_generated() -> None:
    generate_reference()
    assert not CALLABLE_MAP_FILE.exists()


def test_dependency_metadata_still_generated_for_reference_surfaces() -> None:
    generate_reference()
    assert DEPENDENCY_METADATA_FILE.exists()
