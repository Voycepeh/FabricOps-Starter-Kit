"""Behavioural tests for versioned one-table Data Contract assembly."""

from __future__ import annotations

import json
import importlib

import pytest

import fabricops_kit
from fabricops_kit.widgets import widget_register_data_contract as public_widget
from fabricops_kit.widgets.widget_register_data_contract import (
    _assemble_payload,
    _contract_id,
    _selected_usages,
)

pytestmark = pytest.mark.unit


def _sources():
    audit = {"_committed_at": "2026-01-01T00:00:00", "_activity_id": "a"}
    return {
        "METADATA_DATA_STEWARD": [
            {"steward_id": "provider", "steward_name": "Provider", "steward_role": "Owner", "contact": "provider@example.invalid", "is_active": True, **audit},
            {"steward_id": "recipient", "steward_name": "Recipient", "steward_role": "Consumer", "contact": "recipient@example.invalid", "is_active": True, **audit},
            {"steward_id": "other", "steward_name": "Other", "is_active": True, **audit},
        ],
        "METADATA_DATA_CATALOGUE": [
            {"metadata_level": "table", "table_id": "orders", "column_id": None, "environment_name": "dev", "store_type": "lakehouse", "layer": "gold", "schema_name": "sales", "table_name": "orders", "is_active": True, **audit},
            {"metadata_level": "column", "table_id": "orders", "column_id": "order_id", "column_name": "order_id", "environment_name": "dev", "is_active": True, **audit},
        ],
        "METADATA_DATA_PROFILED": [{"table_id": "orders", "column_id": "order_id", "data_type": "long", **audit}],
        "METADATA_ENRICHMENT": [
            {"enrichment_id": "e1", "table_id": "orders", "column_id": None, "environment_name": "dev", "enrichment_level": "table", "enrichment_type": "description", "value": "Orders", **audit},
            {"enrichment_id": "e2", "table_id": "orders", "column_id": "order_id", "environment_name": "dev", "enrichment_level": "column", "enrichment_type": "description", "value": "Identifier", **audit},
        ],
        "METADATA_GUARDRAIL": [
            {"guardrail_rule_id": "g1", "guardrail_version": 2, "table_id": "orders", "column_id": "order_id", "environment_name": "dev", "guardrail_type": "quality", "rule_id": "not_null", "rule_type": "not_null", "rule_parameters_json": '{"threshold":1}', "severity": "error", "is_active": True, **audit},
            {"guardrail_rule_id": "g2", "guardrail_version": 1, "table_id": "orders", "environment_name": "dev", "guardrail_type": "schema", "rule_id": "old", "rule_type": "schema", "rule_parameters_json": "{}", "severity": "warning", "is_active": False, **audit},
        ],
    }


def _agreement():
    return {"agreement_id": "agreement", "agreement_version": "3", "agreement_name": "Order sharing", "domain": "sales", "business_purpose": "Analytics", "provider_steward_id": "provider", "recipient_steward_id": "recipient", "approved_usage_json": '["analytics","reporting"]'}


def test_contract_identity_is_stable_for_agreement_lifecycle_and_table():
    """Use one stable ID across versions while separating table lifecycles."""
    assert _contract_id("agreement", "orders") == _contract_id("agreement", "orders")
    assert _contract_id("agreement", "orders") != _contract_id("agreement", "customers")


def test_usage_must_be_a_parent_agreement_subset():
    """Reject permissions not granted by the exact parent Agreement."""
    assert _selected_usages(["reporting"], ["analytics", "reporting"]) == ["reporting"]
    with pytest.raises(ValueError, match="subset"):
        _selected_usages(["admin"], ["analytics"])


def test_payload_is_complete_deterministic_and_excludes_runtime_results():
    """Freeze governed definitions, not volatile Guardrail evidence."""
    kwargs = {"contract_id": _contract_id("agreement", "orders"), "contract_version": 1, "agreement": _agreement(), "table_id": "orders", "usages": ["analytics"], "tables": _sources(), "environment_name": "dev"}
    first, warnings = _assemble_payload(**kwargs)
    second, _ = _assemble_payload(**kwargs)
    assert json.dumps(first, sort_keys=True, separators=(",", ":")) == json.dumps(second, sort_keys=True, separators=(",", ":"))
    assert first["agreement"]["agreement_version"] == "3"
    assert first["table"]["table_id"] == "orders"
    assert first["table"]["columns"] == [{"column_id": "order_id", "column_name": "order_id", "data_type": "long"}]
    assert {row["steward_id"] for row in first["stewards"]} == {"provider", "recipient"}
    assert first["enrichment"]["table"][0]["value"] == "Orders"
    assert [row["guardrail_rule_id"] for row in first["guardrails"]] == ["g1"]
    assert first["guardrails"][0]["rule_parameters"] == {"threshold": 1}
    assert "results" not in json.dumps(first).lower()
    assert warnings == []


def test_payload_rejects_inactive_or_unknown_table():
    """Contract only current active logical Catalogue tables."""
    sources = _sources()
    sources["METADATA_DATA_CATALOGUE"][0]["is_active"] = False
    with pytest.raises(ValueError, match="valid active"):
        _assemble_payload(contract_id="c", contract_version=1, agreement=_agreement(), table_id="orders", usages=[], tables=sources, environment_name="dev")


def test_public_export_remains_the_owner_entrypoint():
    """Keep the entrypoint while deleting obsolete inventory helpers."""
    module = importlib.import_module("fabricops_kit.widgets.widget_register_data_contract")
    assert fabricops_kit.widget_register_data_contract is public_widget
    assert module.widget_register_data_contract is public_widget
    assert not hasattr(module, "_latest_inventory")
    assert not hasattr(module, "_compare_schemas")
