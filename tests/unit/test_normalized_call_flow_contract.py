"""Focused tests for the normalized current call-flow contract."""

from __future__ import annotations

from scripts import generate_public_function_call_flows_dashboard as dashboard
from scripts import generate_public_function_call_flows_json as flows


def _payload():
    return {
        "metadata": {"schema": "fabricops_public_function_call_flows_v2"},
        "summary": {},
        "defined_functions": [
            {
                "qualified_name": "fabricops_kit.example.public_a",
                "function_name": "public_a",
                "function_type": "public_function",
                "inbound_callers": [],
            },
            {
                "qualified_name": "fabricops_kit.example.helper",
                "function_name": "helper",
                "function_type": "shared_function",
                "inbound_callers": ["fabricops_kit.example.public_a"],
            },
        ],
        "public_functions": [
            {
                "qualified_name": "fabricops_kit.example.public_a",
                "function_name": "public_a",
                "flow": [
                    {
                        "qualified_name": "fabricops_kit.example.public_a",
                        "parent_qualified_name": None,
                    },
                    {
                        "qualified_name": "fabricops_kit.example.helper",
                        "parent_qualified_name": "fabricops_kit.example.public_a",
                        "call_count_from_parent": 2,
                        "architecture_violations": [],
                        "violation_types": [],
                        "violation_details": [],
                    },
                    {
                        "qualified_name": "fabricops_kit.example.helper",
                        "parent_qualified_name": "fabricops_kit.example.public_a",
                        "call_count_from_parent": 2,
                        "architecture_violations": [],
                        "violation_types": [],
                        "violation_details": [],
                    },
                ],
            }
        ],
    }


def test_normalize_payload_stores_functions_and_relationships_once():
    """Persist one callable inventory and one record for each direct edge."""
    normalized = flows.normalize_payload(_payload())

    assert normalized["metadata"]["schema"] == "fabricops_public_function_call_flows_v4"
    assert set(normalized) == {"functions", "metadata", "public_analysis", "relationships"}
    assert len(normalized["functions"]) == 2
    assert normalized["public_analysis"] == [{
        "qualified_name": "fabricops_kit.example.public_a",
        "metrics": {"width": 0, "scope": 0, "depth": 0},
        "files_touched": [],
    }]
    assert all("inbound_callers" not in row for row in normalized["functions"])
    assert normalized["relationships"] == [
        {
            "caller_qualified_name": "fabricops_kit.example.public_a",
            "callee_qualified_name": "fabricops_kit.example.helper",
            "call_count": 2,
        }
    ]
    assert "summary" not in normalized


def test_normalize_payload_keeps_resolved_edges_outside_public_reachability():
    """Retain resolved package call edges even when no public root reaches them."""
    payload = _payload()
    payload["defined_functions"].append(
        {
            "qualified_name": "fabricops_kit.example.detached",
            "function_name": "detached",
            "function_type": "shared_function",
            "inbound_callers": ["fabricops_kit.example.helper"],
        }
    )

    normalized = flows.normalize_payload(payload)
    edges = {
        (row["caller_qualified_name"], row["callee_qualified_name"])
        for row in normalized["relationships"]
    }
    assert ("fabricops_kit.example.helper", "fabricops_kit.example.detached") in edges


def test_dashboard_hydrates_expanded_flows_from_normalized_relationships():
    """Hydrate normalized edges and default omitted optional evidence to empty arrays."""
    html = dashboard.render_dashboard(payload=flows.normalize_payload(_payload()), embed_json=True)

    assert "hydrateNormalizedFlows" not in html
    assert "Public Function Call Flows V4" in html
    assert "function normalizeDashboardData(data)" in html
    assert "Object.defineProperty(record,'flow'" in html
    assert "children.get(qn)" in html
    assert "const next=new Set(stack)" in html
    assert "qn!==rootQn&&fn.architecture_classification==='foundational_io'" in html
    assert "edge?.architecture_violations||[]" in html
    assert "edge?.architecture_signals||[]" in html
    assert "architecture_signal_types:signals.map(item=>item.type)" in html
    assert "violation_types:violations.map(item=>item.type)" in html


def test_normalize_payload_keeps_nonempty_architecture_evidence():
    """Omit empty edge evidence while retaining nonempty violations and signals."""
    payload = _payload()
    edge = payload["public_functions"][0]["flow"][1]
    expected = {
        "architecture_violations": [{"type": "Type 1"}],
        "architecture_signals": [{"type": "Type 0"}],
    }
    edge.update(expected)
    result = flows.normalize_payload(payload)["relationships"][0]

    for field, value in expected.items():
        assert result[field] == value
    assert "architecture_signal_types" not in result
    assert "architecture_signal_details" not in result
    assert "violation_types" not in result
    assert "violation_details" not in result
