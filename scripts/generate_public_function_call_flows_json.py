"""Generate normalized public-function call-flow JSON data.

The detailed analysis implementation lives in ``public_function_call_flows_analysis``
so tests and release tooling can keep using the existing in-memory expanded flow.
Only the committed current JSON is normalized to functions + relationships.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

try:
    from scripts import public_function_call_flows_analysis as _analysis
except ModuleNotFoundError:  # Direct ``python scripts/...`` execution.
    import public_function_call_flows_analysis as _analysis


# Re-export the existing analysis surface so repository tests and release tooling keep
# using the same implementation. The committed v3 JSON is normalized only when it is
# written to DATA_PATH below; dashboard and agent consumers traverse the same graph.
for _name in dir(_analysis):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_analysis, _name)


def _empty_relationship(caller: str, callee: str) -> dict[str, Any]:
    """Return a canonical direct relationship record."""
    return {
        "caller_qualified_name": caller,
        "callee_qualified_name": callee,
        "call_count": 1,
        "architecture_violations": [],
        "violation_types": [],
        "violation_details": [],
    }


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a compact v3 graph contract without duplicated expanded public flows."""
    normalized = copy.deepcopy(payload)
    relationship_by_key: dict[tuple[str, str], dict[str, Any]] = {}

    # Preserve the richer edge evidence already calculated for public-root flows.
    for public_function in payload.get("public_functions", []):
        for row in public_function.get("flow", []):
            caller = row.get("parent_qualified_name")
            callee = row.get("qualified_name")
            if not caller or not callee:
                continue
            key = (str(caller), str(callee))
            edge = relationship_by_key.setdefault(key, _empty_relationship(*key))
            edge["call_count"] = max(edge["call_count"], int(row.get("call_count_from_parent") or 1))
            if row.get("architecture_violations"):
                edge["architecture_violations"] = copy.deepcopy(row["architecture_violations"])
                edge["violation_types"] = list(row.get("violation_types", []))
                edge["violation_details"] = list(row.get("violation_details", []))

    # Include resolved calls outside public-root reachability as well. These edges are
    # already represented by each function's canonical inbound_callers list.
    for callee_record in payload.get("defined_functions", []):
        callee = callee_record.get("qualified_name")
        if not callee:
            continue
        for caller in callee_record.get("inbound_callers", []):
            key = (str(caller), str(callee))
            relationship_by_key.setdefault(key, _empty_relationship(*key))

    for public_function in normalized.get("public_functions", []):
        public_function.pop("flow", None)

    relationships = [relationship_by_key[key] for key in sorted(relationship_by_key)]
    normalized["relationships"] = relationships
    metadata = dict(normalized.get("metadata", {}))
    metadata.update(
        {
            "schema": "fabricops_public_function_call_flows_v3",
            "graph_storage": "normalized_functions_and_direct_relationships",
            "relationship_definition": "Each resolved direct package-local caller to callee relationship is stored once. Consumers reconstruct downstream trees by traversing relationships from a public root.",
        }
    )
    normalized["metadata"] = metadata
    summary = dict(normalized.get("summary", {}))
    summary["relationship_count"] = len(relationships)
    normalized["summary"] = summary
    return normalized


def write_json(payload: dict[str, Any], data_path: Path = DATA_PATH) -> None:
    """Write call-flow JSON, normalizing only the current committed architecture contract."""
    output = normalize_payload(payload) if data_path == DATA_PATH else payload
    _analysis.write_json(output, data_path)


def main() -> None:
    """Generate only the normalized current public function call-flow JSON artifact."""
    write_json(build_payload())


if __name__ == "__main__":
    main()
