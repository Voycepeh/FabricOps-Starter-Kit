"""Generate a repository-wide public-function simplification audit.

The audit consumes the committed normalized public-function call-flow contract and
turns it into review batches based on shared downstream implementation. It is an
analysis aid only; it does not modify the authoritative call-flow JSON.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "docs" / "reference" / "_data" / "public-function-call-flows.json"
DEFAULT_MIN_SHARED_HELPERS = 3
DEFAULT_MIN_OVERLAP_RATIO = 0.5


def _children_by_caller(payload: dict[str, Any]) -> dict[str, set[str]]:
    children: dict[str, set[str]] = defaultdict(set)
    for relationship in payload.get("relationships", []):
        caller = relationship.get("caller_qualified_name")
        callee = relationship.get("callee_qualified_name")
        if caller and callee:
            children[str(caller)].add(str(callee))
    return children


def _reachable_helpers(
    root: str,
    children: dict[str, set[str]],
    public_qns: set[str],
) -> set[str]:
    """Return non-public downstream functions reachable from one public root."""
    helpers: set[str] = set()
    stack = list(children.get(root, set()))
    seen = {root}
    while stack:
        qualified_name = stack.pop()
        if qualified_name in seen:
            continue
        seen.add(qualified_name)
        if qualified_name not in public_qns:
            helpers.add(qualified_name)
        stack.extend(children.get(qualified_name, set()))
    return helpers


def _connected_components(nodes: list[str], edges: set[tuple[str, str]]) -> list[list[str]]:
    adjacency: dict[str, set[str]] = {node: set() for node in nodes}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)

    components: list[list[str]] = []
    seen: set[str] = set()
    for node in sorted(nodes):
        if node in seen:
            continue
        stack = [node]
        component: list[str] = []
        while stack:
            current = stack.pop()
            if current in seen:
                continue
            seen.add(current)
            component.append(current)
            stack.extend(sorted(adjacency[current] - seen, reverse=True))
        components.append(sorted(component))
    return components


def build_simplification_audit(
    payload: dict[str, Any],
    *,
    min_shared_helpers: int = DEFAULT_MIN_SHARED_HELPERS,
    min_overlap_ratio: float = DEFAULT_MIN_OVERLAP_RATIO,
) -> dict[str, Any]:
    """Build deterministic repository-wide simplification review evidence."""
    public_functions = payload.get("public_functions", [])
    defined_functions = payload.get("defined_functions", [])
    public_qns = {
        str(item["qualified_name"])
        for item in public_functions
        if item.get("qualified_name")
    }
    public_by_qn = {
        str(item["qualified_name"]): item
        for item in public_functions
        if item.get("qualified_name")
    }
    defined_by_qn = {
        str(item["qualified_name"]): item
        for item in defined_functions
        if item.get("qualified_name")
    }
    children = _children_by_caller(payload)
    helper_sets = {
        root: _reachable_helpers(root, children, public_qns)
        for root in sorted(public_qns)
    }

    roots_by_helper: dict[str, set[str]] = defaultdict(set)
    for root, helpers in helper_sets.items():
        for helper in helpers:
            roots_by_helper[helper].add(root)

    overlaps: list[dict[str, Any]] = []
    cluster_edges: set[tuple[str, str]] = set()
    roots = sorted(public_qns)
    for index, left in enumerate(roots):
        for right in roots[index + 1 :]:
            shared = sorted(helper_sets[left] & helper_sets[right])
            if not shared:
                continue
            smaller_scope = min(len(helper_sets[left]), len(helper_sets[right]))
            union_size = len(helper_sets[left] | helper_sets[right])
            overlap_ratio = len(shared) / smaller_scope if smaller_scope else 0.0
            jaccard = len(shared) / union_size if union_size else 0.0
            qualifies = len(shared) >= min_shared_helpers and overlap_ratio >= min_overlap_ratio
            if qualifies:
                cluster_edges.add((left, right))
            overlaps.append(
                {
                    "left_qualified_name": left,
                    "right_qualified_name": right,
                    "shared_helper_count": len(shared),
                    "overlap_ratio_of_smaller_flow": round(overlap_ratio, 4),
                    "jaccard_similarity": round(jaccard, 4),
                    "qualifies_for_same_review_batch": qualifies,
                    "shared_helpers": shared,
                }
            )

    components = _connected_components(roots, cluster_edges)
    clusters: list[dict[str, Any]] = []
    cluster_by_root: dict[str, str] = {}
    for index, component in enumerate(components, start=1):
        cluster_id = f"cluster-{index:02d}"
        for root in component:
            cluster_by_root[root] = cluster_id
        common_helpers = sorted(
            set.intersection(*(helper_sets[root] for root in component))
            if len(component) > 1
            else helper_sets[component[0]]
        )
        union_helpers = sorted(set().union(*(helper_sets[root] for root in component)))
        clusters.append(
            {
                "cluster_id": cluster_id,
                "public_function_count": len(component),
                "public_functions": component,
                "shared_by_all_helper_count": len(common_helpers),
                "shared_by_all_helpers": common_helpers,
                "combined_helper_count": len(union_helpers),
                "combined_helpers": union_helpers,
                "review_mode": "family" if len(component) > 1 else "individual",
            }
        )

    helper_usage: list[dict[str, Any]] = []
    for helper in sorted(roots_by_helper):
        record = defined_by_qn.get(helper, {})
        inbound_callers = sorted(str(item) for item in record.get("inbound_callers", []))
        public_roots = sorted(roots_by_helper[helper])
        helper_usage.append(
            {
                "qualified_name": helper,
                "function_name": record.get("function_name", helper.rsplit(".", 1)[-1]),
                "function_type": record.get("function_type"),
                "source_path": record.get("source_path"),
                "public_root_count": len(public_roots),
                "public_roots": public_roots,
                "inbound_caller_count": len(inbound_callers),
                "inbound_callers": inbound_callers,
                "repository_inline_candidate": len(public_roots) == 1 and len(inbound_callers) == 1,
                "supports_live_contract": bool(record.get("supports_live_contract", False)),
                "live_impact_level": record.get("live_impact_level", "none"),
            }
        )

    max_overlap_by_root: dict[str, float] = defaultdict(float)
    strongest_peer_by_root: dict[str, str | None] = {root: None for root in roots}
    for overlap in overlaps:
        ratio = float(overlap["overlap_ratio_of_smaller_flow"])
        left = overlap["left_qualified_name"]
        right = overlap["right_qualified_name"]
        if ratio > max_overlap_by_root[left]:
            max_overlap_by_root[left] = ratio
            strongest_peer_by_root[left] = right
        if ratio > max_overlap_by_root[right]:
            max_overlap_by_root[right] = ratio
            strongest_peer_by_root[right] = left

    public_review: list[dict[str, Any]] = []
    for root in roots:
        item = public_by_qn[root]
        shared_helpers = sorted(
            helper for helper in helper_sets[root] if len(roots_by_helper[helper]) > 1
        )
        high_risk = bool(item.get("has_architecture_violation") or item.get("has_large_width_or_depth"))
        clustered = len(next(cluster["public_functions"] for cluster in clusters if cluster["cluster_id"] == cluster_by_root[root])) > 1
        review_tier = "high" if high_risk else "family" if clustered else "standard"
        public_review.append(
            {
                "qualified_name": root,
                "function_name": item.get("function_name"),
                "source_path": item.get("source_path"),
                "lifecycle_status": item.get("lifecycle_status"),
                "width": item.get("width", 0),
                "scope": item.get("scope", 0),
                "depth": item.get("depth", 0),
                "files_touched": item.get("files_touched", []),
                "architecture_violation_count": item.get("architecture_violation_count", 0),
                "has_architecture_violation": bool(item.get("has_architecture_violation", False)),
                "has_large_width_or_depth": bool(item.get("has_large_width_or_depth", False)),
                "helper_count": len(helper_sets[root]),
                "shared_helper_count": len(shared_helpers),
                "shared_helpers": shared_helpers,
                "strongest_overlap_ratio": round(max_overlap_by_root[root], 4),
                "strongest_overlap_peer": strongest_peer_by_root[root],
                "cluster_id": cluster_by_root[root],
                "review_tier": review_tier,
            }
        )

    qualifying_overlap_count = sum(1 for item in overlaps if item["qualifies_for_same_review_batch"])
    family_cluster_count = sum(1 for item in clusters if item["review_mode"] == "family")
    return {
        "schema": "fabricops_public_function_simplification_audit_v1",
        "source_schema": payload.get("metadata", {}).get("schema"),
        "rules": {
            "cluster_min_shared_helpers": min_shared_helpers,
            "cluster_min_overlap_ratio_of_smaller_flow": min_overlap_ratio,
            "repository_inline_candidate": "Exactly one public root reaches the helper and the helper has exactly one resolved inbound package caller.",
            "review_tier_high": "Architecture violation or large width/depth signal.",
            "review_tier_family": "No high-risk signal, but function belongs to a multi-function implementation cluster.",
        },
        "summary": {
            "public_function_count": len(roots),
            "review_cluster_count": len(clusters),
            "family_cluster_count": family_cluster_count,
            "individual_review_count": len(clusters) - family_cluster_count,
            "qualifying_overlap_pair_count": qualifying_overlap_count,
            "shared_helper_count": sum(1 for roots_for_helper in roots_by_helper.values() if len(roots_for_helper) > 1),
            "repository_inline_candidate_count": sum(1 for item in helper_usage if item["repository_inline_candidate"]),
        },
        "review_batches": clusters,
        "public_functions": public_review,
        "overlaps": overlaps,
        "helper_usage": helper_usage,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Normalized public-function call-flow JSON.")
    parser.add_argument("--output", type=Path, help="Write audit JSON to this path instead of stdout.")
    parser.add_argument("--min-shared-helpers", type=int, default=DEFAULT_MIN_SHARED_HELPERS)
    parser.add_argument("--min-overlap-ratio", type=float, default=DEFAULT_MIN_OVERLAP_RATIO)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    audit = build_simplification_audit(
        payload,
        min_shared_helpers=args.min_shared_helpers,
        min_overlap_ratio=args.min_overlap_ratio,
    )
    rendered = json.dumps(audit, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
