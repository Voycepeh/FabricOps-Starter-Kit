"""Print a scoped callable architecture lookup from the committed call-flow contract.

This is an agent retrieval interface, not a new architecture data source.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTRACT = ROOT / "docs/reference/_data/public-function-call-flows.json"


def lookup(data: dict, name: str, *, depth: int = 1, include_callers: bool = False) -> dict:
    """Return one callable and the requested bounded neighborhood."""
    functions = {row["qualified_name"]: row for row in data.get("defined_functions", [])}
    public = {row["qualified_name"]: row for row in data.get("public_functions", [])}
    matches = [qn for qn in functions if qn == name or qn.rsplit(".", 1)[-1] == name]
    if not matches:
        raise ValueError(f"Unknown callable: {name}")
    if len(matches) > 1:
        raise ValueError(f"Ambiguous callable {name!r}; use qualified_name: {', '.join(sorted(matches))}")

    root = matches[0]
    downstream: dict[str, list[dict]] = defaultdict(list)
    upstream: dict[str, list[dict]] = defaultdict(list)
    for edge in data.get("relationships", []):
        caller, callee = edge["caller_qualified_name"], edge["callee_qualified_name"]
        downstream[caller].append(edge)
        upstream[callee].append(edge)

    def explore(edges_by_node: dict[str, list[dict]], next_key: str) -> tuple[list[dict], set[str]]:
        seen = {root}
        found: list[dict] = []
        queue = deque([(root, 0)])
        while queue:
            node, level = queue.popleft()
            if level >= depth:
                continue
            for edge in sorted(edges_by_node.get(node, []), key=lambda e: (e["caller_qualified_name"], e["callee_qualified_name"])):
                other = edge[next_key]
                found.append({"depth": level + 1, **edge})
                if other not in seen:
                    seen.add(other)
                    queue.append((other, level + 1))
        return found, seen

    callees, downstream_nodes = explore(downstream, "callee_qualified_name")
    callers, upstream_nodes = explore(upstream, "caller_qualified_name") if include_callers else ([], set())
    details = {qn: functions[qn] for qn in sorted(downstream_nodes | upstream_nodes) if qn in functions and qn != root}
    return {
        "callable": functions[root],
        "public_root": public.get(root),
        "direct_and_transitive_callees": callees,
        "callers": callers if include_callers else None,
        "related_functions": details,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("callable", help="Qualified name or unambiguous simple function name")
    parser.add_argument("--depth", type=int, default=1, help="Maximum edge distance, default: 1")
    parser.add_argument("--callers", action="store_true", help="Include inbound edges as well as outgoing edges")
    parser.add_argument("--contract", type=Path, default=DEFAULT_CONTRACT, help="JSON contract path")
    args = parser.parse_args()
    if args.depth < 0 or args.depth > 10:
        parser.error("--depth must be between 0 and 10")
    data = json.loads(args.contract.read_text(encoding="utf-8"))
    try:
        result = lookup(data, args.callable, depth=args.depth, include_callers=args.callers)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
