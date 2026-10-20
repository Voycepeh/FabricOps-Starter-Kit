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
            {"column_id": "postal-id", "column_name": "POSTAL_CODE", "data_type": "long"},
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
    ],
)
def test_invalid_suggestion_fields_are_rejected(field, value, message):
    """Reject unsupported assessment, treatment, and action values."""
    candidate = {"column": "EMAIL", "pii_type": "direct", "reason": "Identifying.",
                 "treatment": "mask", "action": "Block",
                 "parameters": {"preserve_start": 0, "preserve_end": 0, "mask_character": "*"}}
    candidate[field] = value
    with pytest.raises(ValueError, match=message):
        module.suggest_sensitive_data(_context(), prompt="configured", invoke=_invoke([candidate]))


def test_unknown_column_suggestion_is_ignored():
    """Ignore model output that does not reference a governed column."""
    candidate = {
        "column": "MISSING",
        "pii_type": "direct",
        "reason": "Invented column.",
        "treatment": "mask",
        "action": "Block",
        "parameters": {"preserve_start": 0, "preserve_end": 0, "mask_character": "*"},
    }

    result = module.suggest_sensitive_data(
        _context(), prompt="configured", invoke=_invoke([candidate])
    )

    assert result == []


def test_nested_column_context_is_normalized_to_known_column():
    """Accept a known column when the model echoes the supplied column object."""
    candidate = {
        "column": {
            "column_id": "email-id",
            "column_name": "EMAIL",
            "data_type": "string",
            "description": "Email address",
            "profile_evidence": {"row_count": 120},
        },
        "pii_type": "direct",
        "reason": "Can contact a person.",
        "treatment": "mask",
        "action": "Block",
        "parameters": {"preserve_start": 0, "preserve_end": 0, "mask_character": "*"},
    }

    result = module.suggest_sensitive_data(
        _context(), prompt="configured", invoke=_invoke([candidate])
    )

    assert result[0]["column_name"] == "EMAIL"


def test_stringified_column_context_is_normalized_to_known_column():
    """Accept Fabric AI output that stringifies the supplied column object."""
    column = {
        "classification": "",
        "column_id": "email-id",
        "column_name": "EMAIL",
        "data_type": "string",
        "description": "Email address",
        "profile_evidence": {"row_count": 120},
    }
    candidate = {
        "column": str(column),
        "pii_type": "direct",
        "reason": "Can contact a person.",
        "treatment": "mask",
        "action": "Block",
        "parameters": {"preserve_start": 0, "preserve_end": 0, "mask_character": "*"},
    }

    result = module.suggest_sensitive_data(
        _context(), prompt="configured", invoke=_invoke([candidate])
    )

    assert result[0]["column_name"] == "EMAIL"


def test_invalid_treatment_parameters_are_rejected():
    """Apply canonical Sensitive Data parameter validation to AI output."""
    candidate = {"column": "POSTAL_CODE", "pii_type": "indirect", "reason": "Location.",
                 "treatment": "bucket", "action": "Warn", "parameters": {"bins": [1]}}
    with pytest.raises(ValueError, match="invalid"):
        module.suggest_sensitive_data(_context(), prompt="configured", invoke=_invoke([candidate]))


def test_assessment_metadata_uses_canonical_sensitive_data_validation():
    """Retain only validated review rationale in Sensitive Data parameters."""
    validated = module.validate_sensitive_data_parameters({
        "scope": "column", "treatment": "remove", "pii_type": "indirect",
        "pii_reason": "A quasi-identifier when combined with other attributes.",
    })
    assert validated["pii_type"] == "indirect"
    assert validated["pii_reason"].startswith("A quasi-identifier")
    with pytest.raises(ValueError, match="pii_type"):
        module.validate_sensitive_data_parameters({
            "scope": "column", "treatment": "remove", "pii_type": "none",
            "pii_reason": "Not identifying.",
        })


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


def test_fabric_ai_invocation_registers_accessor_and_returns_first_response(monkeypatch, capsys):
    """Register Fabric AI Functions and suppress its notebook console chatter."""
    calls = []
    response = type("Response", (), {"iloc": [" generated response "]})()

    class AI:
        def generate_response(self, *args, **kwargs):
            print("Calling getAccessToken from PyTridentTokenLibrary")
            print("ai.generate_response: 100%", file=__import__("sys").stderr)
            calls.append(("generate_response", args, kwargs))
            return response

    class Frame:
        ai = AI()

    class Pandas:
        @staticmethod
        def DataFrame(rows):
            calls.append(("DataFrame", rows))
            return Frame()

    def fake_import(name):
        calls.append(("import", name))
        if name == "synapse.ml.aifunc":
            return object()
        if name == "pandas":
            return Pandas()
        raise AssertionError(name)

    monkeypatch.setattr(module.importlib, "import_module", fake_import)

    assert module._invoke_fabric_ai("prompt text") == "generated response"
    assert calls[0] == ("import", "synapse.ml.aifunc")
    assert calls[1] == ("import", "pandas")
    assert calls[2] == ("DataFrame", [{"fabricops_prompt": "prompt text"}])
    assert calls[3] == ("generate_response", ("{fabricops_prompt}",), {})
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_fabric_ai_unavailable_has_clear_failure(monkeypatch):
    """Report an actionable error outside an AI-enabled Fabric runtime."""
    class Frame:
        ai = None

    class Pandas:
        @staticmethod
        def DataFrame(*_args, **_kwargs):
            return Frame()

    def fake_import(name):
        if name == "synapse.ml.aifunc":
            return object()
        if name == "pandas":
            return Pandas()
        raise AssertionError(name)

    monkeypatch.setattr(module.importlib, "import_module", fake_import)
    with pytest.raises(RuntimeError, match="AI Functions are unavailable"):
        module._invoke_fabric_ai("prompt")


def test_sensitive_context_and_prompt_include_approved_profile_samples():
    """Share summaries and only the three most frequent values, not full rows."""
    evidence = {**_context()['columns'][0], 'min_value': 'min@example.test',
                'max_value': 'max@example.test', 'sample': 'unapproved-source-row',
                'frequency_evidence': [
                    {'value': 'fourth', 'count': 1},
                    {'value': 'second', 'count': 20, 'percent': 20.0, 'extra': 'unapproved-extra'},
                    {'value': 'first', 'count': 30},
                    {'value': 'third', 'count': 10},
                ],
                'profile_evidence': {'row_count': 100, 'null_count': 2}}
    built = module.build_ai_sensitive_data_context({'catalogue_profile_rows': [evidence]})
    column = built['columns'][0]
    assert column['profile_evidence'] == {'row_count': 100, 'null_count': 2,
                                        'min_value': 'min@example.test', 'max_value': 'max@example.test'}
    assert [item['value'] for item in column['frequency_evidence']] == ['first', 'second', 'third']
    assert column['frequency_evidence'][1]['percent'] == 20.0
    prompts = []
    module.suggest_sensitive_data(built, prompt='Policy', invoke=lambda prompt: prompts.append(prompt) or '[]')
    assert 'min@example.test' in prompts[0] and 'max@example.test' in prompts[0]
    assert all(value in prompts[0] for value in ('first', 'second', 'third'))
    assert 'fourth' not in prompts[0] and 'unapproved-' not in prompts[0]


def test_nested_profile_extrema_survive_context_rebuilding():
    """The invocation boundary preserves approved metadata already normalized by the widget."""
    built = module.build_ai_sensitive_data_context({'catalogue_profile_rows': [
        {**_context()['columns'][0], 'profile_evidence': {'min_value': 'A', 'max_value': 'Z'}}
    ]})
    rebuilt = module.build_ai_sensitive_data_context({'catalogue_profile_rows': built['columns']})
    assert rebuilt['columns'][0]['profile_evidence'] == {'min_value': 'A', 'max_value': 'Z'}


def test_sensitive_suggestions_always_use_block():
    """Older model output cannot reintroduce a Warn policy into the editor."""
    result = module.suggest_sensitive_data(_context(), prompt='Policy', invoke=_invoke([{
        'column': 'EMAIL', 'pii_type': 'direct', 'reason': 'Identifies a person',
        'treatment': 'remove', 'action': 'Warn', 'parameters': {},
    }]))
    assert result[0]['action'] == 'Block'


@pytest.mark.parametrize('column,treatment,parameters', [
    ('EMAIL', 'bucket', {'bins': [0, 10], 'labels': ['low', 'high']}),
    ('POSTAL_CODE', 'mask', {'preserve_start': 0, 'preserve_end': 0, 'mask_character': '*'}),
])
def test_ai_rejects_treatments_incompatible_with_datatype(column, treatment, parameters):
    """Reject unusable suggestions before the editor can offer acceptance."""
    with pytest.raises(ValueError, match='datatype'):
        module.suggest_sensitive_data(_context(), prompt='Policy', invoke=_invoke([{
            'column': column, 'pii_type': 'direct', 'reason': 'Identifies an entity',
            'treatment': treatment, 'action': 'Block', 'parameters': parameters,
        }]))
