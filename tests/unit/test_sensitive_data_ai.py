"""Focused validation tests for advisory Sensitive Data AI suggestions."""

from __future__ import annotations

import json

import pytest

from fabricops_kit.widgets import enrichment_shared as module


def _context() -> dict:
    return {
        "table_id": "customers",
        "table_name": "customers",
        "columns": [
            {"column_id": "email-id", "column_name": "EMAIL", "data_type": "string"},
            {"column_id": "postal-id", "column_name": "POSTAL_CODE", "data_type": "string"},
            {"column_id": "total-id", "column_name": "ORDER_TOTAL", "data_type": "decimal"},
        ],
    }


def _invoke(payload):
    return lambda _prompt: json.dumps(payload)


def test_direct_indirect_and_not_pii_suggestions_are_reviewable():
    """Retain all three supported PII assessments for human review."""
    suggestions = module.suggest_sensitive_data(
        _context(), prompt="configured prompt", invoke=_invoke([
            {"column": "EMAIL", "pii_type": "direct", "reason": "Can contact a person.",
             "treatment": "mask", "action": "Block",
             "parameters": {"preserve_start": 0, "preserve_end": 0, "mask_character": "*"}},
            {"column": "POSTAL_CODE", "pii_type": "indirect", "reason": "Narrows location.",
             "treatment": "bucket", "action": "Warn",
             "parameters": {"bins": [0, 10000, 20000], "labels": ["A", "B", "C"]}},
            {"column": "ORDER_TOTAL", "pii_type": "none", "reason": "No identifying basis.",
             "treatment": None, "action": None, "parameters": {}},
        ]),
    )
    assert [item["pii_type"] for item in suggestions] == ["direct", "indirect", "none"]
    assert suggestions[0]["treatment"] == "mask"
    assert suggestions[1]["treatment"] == "bucket"
    assert suggestions[2]["is_active"] is False


@pytest.mark.parametrize("treatment", ["tokenize", "mask", "remove"])
def test_supported_non_bucket_treatments(treatment):
    """Accept each non-bucket treatment through canonical validation."""
    parameters = (
        {"preserve_start": 0, "preserve_end": 0, "mask_character": "*"}
        if treatment == "mask" else {}
    )
    result = module.suggest_sensitive_data(
        _context(), prompt="configured", invoke=_invoke([{
            "column": "EMAIL", "pii_type": "direct", "reason": "Identifying.",
            "treatment": treatment, "action": "Warn", "parameters": parameters,
        }]),
    )
    assert result[0]["treatment"] == treatment


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("pii_type", "possible", "invalid pii_type"),
        ("treatment", "hash", "invalid"),
        ("action", "Approve", "invalid"),
        ("column", "MISSING", "unknown column"),
    ],
)
def test_invalid_suggestion_fields_are_rejected(field, value, message):
    """Reject unsupported assessment, treatment, action, and column values."""
    candidate = {"column": "EMAIL", "pii_type": "direct", "reason": "Identifying.",
                 "treatment": "mask", "action": "Block",
                 "parameters": {"preserve_start": 0, "preserve_end": 0, "mask_character": "*"}}
    candidate[field] = value
    with pytest.raises(ValueError, match=message):
        module.suggest_sensitive_data(_context(), prompt="configured", invoke=_invoke([candidate]))


def test_invalid_treatment_parameters_are_rejected():
    """Apply canonical Sensitive Data parameter validation to AI output."""
    candidate = {"column": "POSTAL_CODE", "pii_type": "indirect", "reason": "Location.",
                 "treatment": "bucket", "action": "Warn", "parameters": {"bins": [1]}}
    with pytest.raises(ValueError, match="invalid"):
        module.suggest_sensitive_data(_context(), prompt="configured", invoke=_invoke([candidate]))


def test_duplicate_columns_use_first_valid_suggestion():
    """Resolve duplicate suggestions deterministically by keeping the first."""
    candidate = {"column": "EMAIL", "pii_type": "direct", "reason": "First.",
                 "treatment": "mask", "action": "Block",
                 "parameters": {"preserve_start": 0, "preserve_end": 0, "mask_character": "*"}}
    duplicate = {**candidate, "reason": "Second.", "treatment": "remove"}
    result = module.suggest_sensitive_data(
        _context(), prompt="configured", invoke=_invoke([candidate, duplicate])
    )
    assert len(result) == 1
    assert result[0]["reason"] == "First."


def test_malformed_json_and_non_list_are_rejected():
    """Reject malformed and incorrectly shaped model responses."""
    with pytest.raises(ValueError, match="not valid JSON"):
        module.suggest_sensitive_data(_context(), prompt="configured", invoke=lambda _prompt: "{")
    with pytest.raises(ValueError, match="JSON list"):
        module.suggest_sensitive_data(_context(), prompt="configured", invoke=_invoke({}))


def test_configured_prompt_and_metadata_only_context_are_sent():
    """Include the editable configured prompt and constrained instructions."""
    prompts = []
    module.suggest_sensitive_data(
        _context(), prompt="MY EDITABLE PROMPT", invoke=lambda prompt: prompts.append(prompt) or "[]"
    )
    assert "MY EDITABLE PROMPT" in prompts[0]
    assert "Direct PII" in prompts[0]
    assert "Do not include raw values" in prompts[0]


def test_fabric_ai_unavailable_has_clear_failure(monkeypatch):
    """Report an actionable error outside an AI-enabled Fabric runtime."""
    class Frame:
        ai = None

    monkeypatch.setattr(module.importlib, "import_module", lambda _name: type("Pandas", (), {"DataFrame": lambda *_args, **_kwargs: Frame()})())
    with pytest.raises(RuntimeError, match="AI Functions are unavailable"):
        module._invoke_fabric_ai("prompt")
