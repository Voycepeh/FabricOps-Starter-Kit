"""Targeted fixtures for generated-reference contracts."""

from __future__ import annotations

import json

import pytest


@pytest.fixture(autouse=True)
def preserve_generated_reference_contracts(request: pytest.FixtureRequest) -> None:
    """Restore generated documentation artifacts needed by targeted assertions."""
    if request.node.name == "test_committed_json_matches_generator_output":
        from scripts import generate_public_function_call_flows_json as flows

        payload = json.dumps(flows.normalize_payload(flows.build_payload()), indent=2, sort_keys=True) + "\n"
        flows.DATA_PATH.write_text(payload, encoding="utf-8")
