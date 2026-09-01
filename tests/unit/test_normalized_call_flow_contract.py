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

    assert normalized["metadata"]["schema"] == "fabricops_public_function_call_flows_v3"
    assert "flow" not in normalized["public_functions"][0]
    assert len(normalized["defined_functions"]) == 2
    assert normalized["relationships"] == [
        {
            "caller_qualified_name": "fabricops_kit.example.public_a",
            "callee_qualified_name": "fabricops_kit.example.helper",
            "call_count": 2,
            "architecture_violations": [],
            "violation_types": [],
            "violation_details": [],
        }
    ]
    assert normalized["summary"]["relationship_count"] == 1


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
    """Keep the interactive dashboard wired to the normalized relationship graph."""
    html = dashboard.render_dashboard(payload=flows.normalize_payload(_payload()), embed_json=True)

    assert "hydrateNormalizedFlows" in html
    assert "Public Function Call Flows V3" in html
    assert "children.get(qn)" in html
    assert "const next=new Set(stack)" in html
