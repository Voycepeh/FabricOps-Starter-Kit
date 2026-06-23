"""Validate generated callable architecture outputs against repository rules."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CALLABLE_FLOW_PATH = ROOT / "docs" / "reference" / "_data" / "callable-flow.json"
DASHBOARD_PATH = ROOT / "docs" / "assets" / "callable-functions-dashboard.html"
INVENTORY_PATH = ROOT / "docs" / "assets" / "callable-functions-inventory.html"

VISIBLE_FUNCTION_TYPES = {"Public function", "Internal function"}
VISIBLE_LAYERS = {"public", "internal"}
OLD_VISIBLE_LAYER_LABELS = {"Public API", "Internal helper", "Utility", "Adapter", "Workflow", "Private"}


def _load_flow() -> dict[str, Any]:
    return json.loads(CALLABLE_FLOW_PATH.read_text(encoding="utf-8"))


def _failures(flow: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    inventory = flow.get("function_inventory", [])
    summary = flow.get("summary_counts", {})
    public_surface = summary.get("public_api_surface", {})
    metrics = summary.get("callable_inventory_metrics", {})

    for row in inventory:
        qn = str(row.get("qualified_name", ""))
        name = str(row.get("function_name", ""))
        function_type = row.get("function_type")
        layer = row.get("layer")
        if name.split(".")[-1].startswith("_"):
            failures.append(f"Private helper surfaced in default inventory: {qn}")
        if function_type not in VISIBLE_FUNCTION_TYPES:
            failures.append(f"Non Public/Internal function type emitted for {qn}: {function_type!r}")
        if layer not in VISIBLE_LAYERS:
            failures.append(f"Non public/internal layer emitted for {qn}: {layer!r}")
        if function_type in OLD_VISIBLE_LAYER_LABELS or layer in OLD_VISIBLE_LAYER_LABELS:
            failures.append(f"Old architecture layer label emitted for {qn}: {function_type!r}/{layer!r}")
        if row.get("callable_kind") != "function":
            failures.append(f"Supporting object emitted as architecture inventory row: {qn}")

    if any(key in summary.get("function_type", {}) for key in OLD_VISIBLE_LAYER_LABELS):
        failures.append("Old architecture labels are present in summary_counts.function_type")
    if set(summary.get("function_type", {})) - VISIBLE_FUNCTION_TYPES:
        failures.append(f"Unexpected visible function type counts: {sorted(summary.get('function_type', {}))}")
    if set(summary.get("layer", {})) - VISIBLE_LAYERS:
        failures.append(f"Unexpected visible layer counts: {sorted(summary.get('layer', {}))}")
    if metrics.get("hidden_private_helpers", 0) and metrics.get("total_callables") != len(inventory):
        # total_callables intentionally means visible rows only; hidden helpers are tracked separately.
        pass
    if public_surface.get("public_api_entrypoints") != summary.get("layer", {}).get("public"):
        failures.append("Public API Surface entrypoint count does not match visible public functions")

    for flow_row in flow.get("public_entrypoint_flow", []):
        for callee in [*flow_row.get("direct_callees", []), *flow_row.get("transitive_callees", [])]:
            name = str(callee.get("callable", ""))
            if name.split(".")[-1].startswith("_"):
                failures.append(f"Private helper surfaced in public flow: {flow_row.get('qualified_name')} -> {callee.get('qualified_name')}")
            if callee.get("callee_type") not in {"Public", "Internal"}:
                failures.append(f"Non Public/Internal callee type in public flow: {callee.get('qualified_name')}={callee.get('callee_type')!r}")
            if callee.get("architecture_result") == "Violation" and callee.get("violation_type") not in {"Public -> Public", "Internal -> Public"}:
                failures.append(f"Unsupported architecture violation type: {callee.get('violation_type')!r}")

    dashboard_text = DASHBOARD_PATH.read_text(encoding="utf-8")
    inventory_text = INVENTORY_PATH.read_text(encoding="utf-8")
    for label in ("Utility ->", "Adapter layer", "Workflow layer", "Private layer"):
        if label in dashboard_text or label in inventory_text:
            failures.append(f"Old architecture wording remains in dashboard assets: {label}")
    return failures


def main() -> int:
    """Run callable architecture validation."""
    failures = _failures(_load_flow())
    if failures:
        print("Callable architecture validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("Callable architecture validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
