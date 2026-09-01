"""Generate normalized public-function call-flow JSON data.

The detailed analysis implementation remains in ``public_function_call_flows_legacy``
so tests and release tooling can keep using the existing in-memory expanded flow.
Only the committed current JSON is normalized to functions + relationships.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from scripts import public_function_call_flows_legacy as _legacy


# Re-export the existing analysis surface so repository tests and release tooling keep
# using the same implementation. The current committed JSON is normalized only when
# it is written to DATA_PATH below.
for _name in dir(_legacy):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_legacy, _name)


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a compact v3 graph contract without duplicated expanded public flows."""
    normalized = copy.deepcopy(payload)
    relationship_by_key: dict[tuple[str, str], dict[str, Any]] = {}

    for public_function in payload.get("public_functions", []):
        for row in public_function.get("flow", []):
            caller = row.get("parent_qualified_name")
            callee = row.get("qualified_name")
            if not caller or not callee:
                continue
            key = (str(caller), str(callee))
            edge = relationship_by_key.setdefault(
                key,
                {
                    "caller_qualified_name": str(caller),
                    "callee_qualified_name": str(callee),
                    "call_count": int(row.get("call_count_from_parent") or 1),
                    "architecture_violations": copy.deepcopy(row.get("architecture_violations", [])),
                    "violation_types": list(row.get("violation_types", [])),
                    "violation_details": list(row.get("violation_details", [])),
                },
            )
            edge["call_count"] = max(edge["call_count"], int(row.get("call_count_from_parent") or 1))

    for public_function in normalized.get("public_functions", []):
        public_function.pop("flow", None)

    relationships = [relationship_by_key[key] for key in sorted(relationship_by_key)]
    normalized["relationships"] = relationships
    metadata = dict(normalized.get("metadata", {}))
    metadata.update(
        {
            "schema": "fabricops_public_function_call_flows_v3",
            "graph_storage": "normalized_functions_and_direct_relationships",
            "relationship_definition": "Each direct package-local caller to callee relationship is stored once. Consumers reconstruct downstream trees by traversing relationships from a public root.",
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
    _legacy.write_json(output, data_path)


def main() -> None:
    """Generate only the normalized current public function call-flow JSON artifact."""
    write_json(build_payload())


if __name__ == "__main__":
    main()
