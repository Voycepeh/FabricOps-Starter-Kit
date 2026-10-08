"""Measure generated call-flow JSON size and safely removable empty relationship fields.

This audits the committed file without changing generated artifacts or the schema.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parents[1] / "docs/reference/_data/public-function-call-flows.json"
EVIDENCE_FIELDS = (
    "architecture_violations",
    "architecture_signals",
    "architecture_signal_types",
    "architecture_signal_details",
    "violation_types",
    "violation_details",
)


def serialized_bytes(data: dict) -> int:
    """Measure JSON using the canonical generator's formatting."""
    return len((json.dumps(data, indent=2, sort_keys=True) + "\n").encode("utf-8"))


def audit(data: dict) -> dict:
    """Report exact hypothetical savings, without changing the supplied contract."""
    edges = data.get("relationships", [])
    field_counts = Counter()
    empty_counts = Counter()
    for edge in edges:
        for key, value in edge.items():
            field_counts[key] += 1
            if value == []:
                empty_counts[key] += 1

    # Use the same indent/sort settings as the canonical generator so savings
    # include punctuation, indentation and trailing commas, not estimates.
    compacted = {
        **data,
        "relationships": [
            {key: value for key, value in edge.items() if not (key in EVIDENCE_FIELDS and value == [])}
            for edge in edges
        ],
    }
    original_bytes = serialized_bytes(data)
    projected_bytes = serialized_bytes(compacted)
    return {
        "canonical_serialized_bytes": original_bytes,
        "relationship_count": len(edges),
        "field_occurrences": dict(sorted(field_counts.items())),
        "empty_array_occurrences": dict(sorted(empty_counts.items())),
        "candidate": "omit_empty_relationship_evidence_arrays",
        "candidate_serialized_bytes": projected_bytes,
        "potential_bytes_saved": original_bytes - projected_bytes,
        "potential_percent_saved": round(
            100 * (original_bytes - projected_bytes) / original_bytes, 2
        ) if original_bytes else 0,
        "nonempty_evidence_preserved": True,
    }


def main() -> None:
    """Print a deterministic size audit for the committed architecture contract."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contract", type=Path, default=DEFAULT_PATH)
    args = parser.parse_args()
    data = json.loads(args.contract.read_text(encoding="utf-8"))
    result = audit(data)
    result["on_disk_bytes"] = args.contract.stat().st_size
    result["matches_canonical_format"] = result["on_disk_bytes"] == result["canonical_serialized_bytes"]
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
