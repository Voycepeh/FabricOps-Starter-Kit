"""Validate deterministic call-flow JSON size auditing."""
import copy

from scripts.audit_public_function_call_flows_json import audit, serialized_bytes


def test_audit_preserves_input_and_nonempty_evidence():
    """Audit only empty arrays and leave all caller data unchanged."""
    data = {
        "relationships": [
            {
                "caller_qualified_name": "pkg.a",
                "callee_qualified_name": "pkg.b",
                "architecture_violations": [],
                "architecture_signals": [{"type": "warning"}],
                "violation_types": [],
            }
        ],
        "defined_functions": [{"qualified_name": "pkg.a"}],
    }
    before = copy.deepcopy(data)
    result = audit(data)
    assert data == before
    assert result["relationship_count"] == 1
    assert result["empty_array_occurrences"]["architecture_violations"] == 1
    assert result["potential_bytes_saved"] > 0
    assert result["candidate_serialized_bytes"] < serialized_bytes(data)


def test_audit_does_not_drop_unrelated_empty_fields():
    """Keep empty custom fields outside the recognized evidence vocabulary."""
    data = {"relationships": [{"custom": [], "architecture_signals": [1]}]}
    result = audit(data)
    assert result["potential_bytes_saved"] == 0
    assert result["empty_array_occurrences"]["custom"] == 1


def test_audit_handles_empty_graph():
    """Empty graph has no projected savings."""
    result = audit({"relationships": []})
    assert result["relationship_count"] == 0
    assert result["potential_bytes_saved"] == 0
