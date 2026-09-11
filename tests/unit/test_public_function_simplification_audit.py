"""Tests for repository-wide public-function simplification audit generation."""

from __future__ import annotations

from scripts import generate_public_function_simplification_audit as audit


def _payload() -> dict:
    public_functions = []
    for name in ("public_a", "public_b", "public_c"):
        public_functions.append(
            {
                "qualified_name": f"fabricops_kit.example.{name}",
                "function_name": name,
                "source_path": f"src/fabricops_kit/example/{name}.py",
                "lifecycle_status": "preview",
                "width": 1,
                "scope": 4,
                "depth": 2,
                "files_touched": [f"src/fabricops_kit/example/{name}.py"],
                "architecture_violation_count": 0,
                "has_architecture_violation": False,
                "has_large_width_or_depth": False,
            }
        )
    public_functions[2]["has_architecture_violation"] = True
    public_functions[2]["architecture_violation_count"] = 1

    relationships = []

    def edge(caller: str, callee: str) -> None:
        relationships.append(
            {
                "caller_qualified_name": caller,
                "callee_qualified_name": callee,
                "call_count": 1,
                "architecture_violations": [],
                "violation_types": [],
                "violation_details": [],
            }
        )

    root_a = "fabricops_kit.example.public_a"
    root_b = "fabricops_kit.example.public_b"
    root_c = "fabricops_kit.example.public_c"
    helpers_a = ["helper_1", "helper_2", "helper_3", "helper_a"]
    helpers_b = ["helper_1", "helper_2", "helper_3", "helper_b"]
    helpers_c = ["helper_1", "helper_c"]
    for helper in helpers_a:
        edge(root_a, f"fabricops_kit.example.{helper}")
    for helper in helpers_b:
        edge(root_b, f"fabricops_kit.example.{helper}")
    for helper in helpers_c:
        edge(root_c, f"fabricops_kit.example.{helper}")

    inbound: dict[str, list[str]] = {
        "helper_1": [root_a, root_b, root_c],
        "helper_2": [root_a, root_b],
        "helper_3": [root_a, root_b],
        "helper_a": [root_a],
        "helper_b": [root_b],
        "helper_c": [root_c],
    }
    defined_functions = [
        {
            "qualified_name": item["qualified_name"],
            "function_name": item["function_name"],
            "function_type": "public_function",
            "source_path": item["source_path"],
            "inbound_callers": [],
        }
        for item in public_functions
    ]
    for helper, callers in inbound.items():
        defined_functions.append(
            {
                "qualified_name": f"fabricops_kit.example.{helper}",
                "function_name": helper,
                "function_type": "shared_function",
                "source_path": "src/fabricops_kit/example/shared.py",
                "inbound_callers": callers,
                "supports_live_contract": False,
                "live_impact_level": "preview_only",
            }
        )

    return {
        "metadata": {"schema": "fabricops_public_function_call_flows_v3"},
        "public_functions": public_functions,
        "defined_functions": defined_functions,
        "relationships": relationships,
    }


def test_clusters_public_functions_by_shared_downstream_helpers() -> None:
    result = audit.build_simplification_audit(_payload())

    assert result["summary"]["public_function_count"] == 3
    assert result["summary"]["family_cluster_count"] == 1
    assert result["summary"]["individual_review_count"] == 1
    family = next(batch for batch in result["review_batches"] if batch["review_mode"] == "family")
    assert family["public_functions"] == [
        "fabricops_kit.example.public_a",
        "fabricops_kit.example.public_b",
    ]
    assert family["shared_by_all_helpers"] == [
        "fabricops_kit.example.helper_1",
        "fabricops_kit.example.helper_2",
        "fabricops_kit.example.helper_3",
    ]


def test_reports_global_helper_usage_and_safe_inline_candidates() -> None:
    result = audit.build_simplification_audit(_payload())
    helpers = {item["function_name"]: item for item in result["helper_usage"]}

    assert helpers["helper_1"]["public_root_count"] == 3
    assert helpers["helper_1"]["repository_inline_candidate"] is False
    assert helpers["helper_a"]["public_root_count"] == 1
    assert helpers["helper_a"]["inbound_caller_count"] == 1
    assert helpers["helper_a"]["repository_inline_candidate"] is True


def test_high_risk_signal_wins_over_family_or_standard_review_tier() -> None:
    result = audit.build_simplification_audit(_payload())
    public = {item["function_name"]: item for item in result["public_functions"]}

    assert public["public_a"]["review_tier"] == "family"
    assert public["public_b"]["review_tier"] == "family"
    assert public["public_c"]["review_tier"] == "high"
    assert public["public_a"]["strongest_overlap_peer"] == "fabricops_kit.example.public_b"
    assert public["public_a"]["strongest_overlap_ratio"] == 0.75


def test_thresholds_are_configurable_without_changing_graph_evidence() -> None:
    result = audit.build_simplification_audit(
        _payload(),
        min_shared_helpers=4,
        min_overlap_ratio=0.5,
    )

    assert result["summary"]["family_cluster_count"] == 0
    assert result["summary"]["individual_review_count"] == 3
    assert result["summary"]["qualifying_overlap_pair_count"] == 0
    assert any(item["shared_helper_count"] == 3 for item in result["overlaps"])
