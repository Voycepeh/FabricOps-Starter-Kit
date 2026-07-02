"""Generate only the Function Call Graph JSON and dashboard artifacts.

This focused entrypoint refreshes `docs/reference/_data/function-call-graph.json`
and `docs/assets/function-call-graph-dashboard.html` without running the complete
reference generator. Use the full reference generator when a complete reference refresh is required.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reference_generation.call_graph_data import generate_function_call_graph_artifacts


def main() -> None:
    """Run the focused Function Call Graph generation workflow."""
    generate_function_call_graph_artifacts()


if __name__ == "__main__":
    main()
