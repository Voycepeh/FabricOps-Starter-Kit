"""Generate only the Function Call Graph JSON and dashboard artifacts.

This focused entrypoint refreshes `docs/reference/_data/function-call-graph.json`
and `docs/assets/function-call-graph-dashboard.html` without running the complete
reference generator. Use `scripts/generate_function_reference.py` when a full
reference refresh is required.
"""

from __future__ import annotations

from generate_function_reference import generate_function_call_graph_artifacts


def main() -> None:
    """Run the focused Function Call Graph generation workflow."""
    generate_function_call_graph_artifacts()


if __name__ == "__main__":
    main()
