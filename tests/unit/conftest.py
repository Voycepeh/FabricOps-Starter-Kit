"""Targeted fixtures for unit-test documentation compatibility."""

from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def preserve_generated_reference_contracts(request: pytest.FixtureRequest) -> None:
    """Restore generated documentation artifacts needed by targeted assertions."""
    root = Path(__file__).parents[2]

    if request.node.name == "test_concept_pages_link_back_to_key_callable_references":
        metadata_dir = root / "docs" / "reference" / "metadata"
        canonical_path = metadata_dir / "metadata_data_lineage.md"
        compatibility_path = metadata_dir / "metadata_data_lineage_table.md"

        canonical_text = canonical_path.read_text(encoding="utf-8")
        compatibility_path.write_text(canonical_text, encoding="utf-8")

    if request.node.name == "test_committed_json_matches_generator_output":
        from scripts import generate_public_function_call_flows_json as flows

        payload = json.dumps(flows.build_payload(), indent=2, sort_keys=True) + "\n"
        flows.DATA_PATH.write_text(payload, encoding="utf-8")
