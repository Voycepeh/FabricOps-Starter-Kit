"""Focused tests for the unified Data Contract widget helpers."""

import json

import importlib

module = importlib.import_module("fabricops_kit.widgets.widget_data_contract")


def test_manifest_view_exposes_exact_canonical_dictionary():
    """The human review and notebook variables share one canonical object."""
    payload = {
        "contract": {"contract_id": "contract-1", "contract_version": 2, "status": "frozen"},
        "table": {"schema_name": "demo", "table_name": "orders", "columns": [], "processing": {}},
        "enrichment": {"table": [], "columns": []},
        "guardrails": [],
    }
    rendered = module._manifest_html(payload)
    assert module.DATA_CONTRACT_MANIFEST is payload
    assert json.loads(module.DATA_CONTRACT_MANIFEST_JSON) == payload
    assert "JSON manifest" in rendered
    assert "Observed values" not in rendered


def test_profile_context_rendering_priority():
    """Persisted frequencies, ranges, and unavailable states render distinctly."""
    assert "Observed values" in module._profile_html({"kind": "values", "values": [{"value": "Ready", "count": 3}]})
    assert "Observed range" in module._profile_html({"kind": "range", "min": 1, "max": 4})
    assert "No profile values available" in module._profile_html({"kind": "unavailable"})
