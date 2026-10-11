"""Generate the canonical v4 public-function call-flow JSON contract.

The analysis module intentionally keeps its expanded in-memory payload because release
snapshots freeze public-root flows. This module owns the compact current contract used
by the dashboard, reference generator, tests, and agent query utility.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

try:
    from scripts import public_function_call_flows_analysis as _analysis
except (ImportError, ModuleNotFoundError):  # Direct ``python scripts/...`` execution.
    import public_function_call_flows_analysis as _analysis


for _name in dir(_analysis):
    if not _name.startswith("__"):
        globals()[_name] = getattr(_analysis, _name)


_PUBLIC_DOCUMENTATION_FIELDS = (
    "signature",
    "summary",
    "parameters",
    "returns_documentation",
    "raises_documentation",
    "examples",
    "usage_notes",
    "public_import_path",
    "contract_risk",
)
_FUNCTION_COUNT_FIELDS = {
    "direct_live_dependent_count",
    "transitive_live_dependent_count",
}
_RELATIONSHIP_EVIDENCE_FIELDS = (
    "architecture_signals",
    "architecture_violations",
)


def _function_record(
    record: dict[str, Any],
    public_record: dict[str, Any] | None,
    *,
    runtime_hooks: set[str],
    unused_by_qn: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return one authoritative callable record with no edge-derived callers."""
    compact = {
        key: copy.deepcopy(value)
        for key, value in record.items()
        if key not in _FUNCTION_COUNT_FIELDS | {"inbound_callers"}
    }
    qn = str(record["qualified_name"])
    compact["usage"] = (
        "public_flow_reachable"
        if record.get("public_flow_reachable")
        else "detached"
        if record.get("inbound_source_references") or qn in runtime_hooks
        else "unused"
    )
    if qn in runtime_hooks:
        compact["implicit_runtime_hook"] = True
    for empty_field in (
        "inbound_source_references",
        "direct_live_dependents",
        "transitive_live_dependents",
        "release_history",
        "release_versions",
    ):
        if not compact.get(empty_field):
            compact.pop(empty_field, None)
    compact.pop("public_flow_reachable", None)
    compact.pop("contract_display", None)
    compact.pop("release_versions", None)
    if not compact.get("supports_live_contract"):
        compact.pop("supports_live_contract", None)
    for optional_field in ("live_since", "discontinued_in"):
        if compact.get(optional_field) is None:
            compact.pop(optional_field, None)

    if public_record:
        for field in _PUBLIC_DOCUMENTATION_FIELDS:
            if field in public_record and public_record[field] not in (None, "", []):
                compact[field] = copy.deepcopy(public_record[field])
    if qn in unused_by_qn:
        compact["cleanup"] = {
            "reason": unused_by_qn[qn]["reason"],
            "suggested_action": unused_by_qn[qn]["suggested_action"],
        }
    return compact


def _public_analysis_record(record: dict[str, Any]) -> dict[str, Any]:
    """Return analysis that exists only in the context of a public root."""
    result: dict[str, Any] = {
        "qualified_name": record["qualified_name"],
        "metrics": {
            "width": record.get("width", record.get("direct_call_count", 0)),
            "scope": record.get("scope", record.get("transitive_function_count", 0)),
            "depth": record.get("depth", record.get("max_depth", 0)),
        },
        "files_touched": copy.deepcopy(record.get("files_touched", [])),
    }
    if record.get("architecture_violation_count"):
        result["architecture_violation_count"] = record["architecture_violation_count"]
    if record.get("refactor_signals"):
        result["refactor_signals"] = copy.deepcopy(record["refactor_signals"])
    if record.get("live_critical_dependencies"):
        result["live_critical_dependencies"] = copy.deepcopy(record["live_critical_dependencies"])
    return result


def _empty_relationship(caller: str, callee: str) -> dict[str, Any]:
    return {"caller_qualified_name": caller, "callee_qualified_name": callee}


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the canonical v4 contract from the expanded analysis payload."""
    public_by_qn = {
        str(row["qualified_name"]): row
        for row in payload.get("public_functions", [])
    }
    runtime_hooks = {str(qn) for qn in payload.get("implicit_runtime_hook_functions", [])}
    unused_by_qn = {
        str(row["qualified_name"]): row
        for row in payload.get("defined_but_not_used", [])
    }
    functions = [
        _function_record(
            row,
            public_by_qn.get(str(row["qualified_name"])),
            runtime_hooks=runtime_hooks,
            unused_by_qn=unused_by_qn,
        )
        for row in payload.get("defined_functions", [])
    ]

    relationship_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for public_function in payload.get("public_functions", []):
        for row in public_function.get("flow", []):
            caller = row.get("parent_qualified_name")
            callee = row.get("qualified_name")
            if not caller or not callee:
                continue
            key = (str(caller), str(callee))
            edge = relationship_by_key.setdefault(key, _empty_relationship(*key))
            call_count = int(row.get("call_count_from_parent") or 1)
            if call_count > 1:
                edge["call_count"] = max(int(edge.get("call_count", 1)), call_count)
            for field in _RELATIONSHIP_EVIDENCE_FIELDS:
                if row.get(field):
                    edge[field] = copy.deepcopy(row[field])

    # Retain resolved calls outside public reachability without duplicating them as
    # inbound caller arrays on function records.
    for callee_record in payload.get("defined_functions", []):
        callee = callee_record.get("qualified_name")
        if not callee:
            continue
        for caller in callee_record.get("inbound_callers", []):
            key = (str(caller), str(callee))
            relationship_by_key.setdefault(key, _empty_relationship(*key))

    metadata = {
        key: copy.deepcopy(value)
        for key, value in payload.get("metadata", {}).items()
        if key
        not in {
            "architecture_violation_signal",
            "detached_function_definition",
            "inbound_call_definition",
            "source_reference_definition",
            "unused_function_definition",
        }
    }
    metadata.update(
        {
            "schema": "fabricops_public_function_call_flows_v4",
            "graph_storage": "canonical_functions_direct_relationships_public_analysis",
        }
    )
    release_versions = copy.deepcopy(payload.get("release_contract", {}).get("release_versions", []))
    result: dict[str, Any] = {
        "metadata": metadata,
        "functions": sorted(functions, key=lambda row: str(row["qualified_name"])),
        "relationships": [relationship_by_key[key] for key in sorted(relationship_by_key)],
        "public_analysis": [
            _public_analysis_record(row)
            for row in sorted(
                payload.get("public_functions", []),
                key=lambda item: (str(item.get("function_name", "")), str(item["qualified_name"])),
            )
        ],
    }
    if release_versions:
        result["release_versions"] = release_versions
    return result


def write_json(payload: dict[str, Any], data_path: Path = DATA_PATH) -> None:
    """Write v4 only for the current contract; preserve expanded release payloads."""
    output = normalize_payload(payload) if data_path == DATA_PATH else payload
    _analysis.write_json(output, data_path)


def main() -> None:
    """Generate the canonical current public-function call-flow contract."""
    write_json(build_payload())


if __name__ == "__main__":
    main()
