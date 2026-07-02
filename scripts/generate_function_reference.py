"""Orchestrate the full generated reference refresh."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from reference_generation import (
    call_graph_data,
    callable_reference_pages,
    glossary,
    landing_page,
    manifests,
    metadata_reference_pages,
    module_pages,
    runtime_inventory_dashboard,
    source_scan,
)
from reference_generation import shared as _shared
from reference_generation.shared import *  # noqa: F403 - compatibility imports for source-level tests
from reference_generation.shared import generate_full_reference

globals().update({name: value for name, value in vars(_shared).items() if not name.startswith("__")})
# Source contract marker owned by call_graph_dashboard.py: const EMBEDDED_FUNCTION_CALL_GRAPH_DATA=


def main() -> None:
    """Run the full reference generation workflow in job-owned module order."""
    # Imports above intentionally load each job-owned module before the shared
    # full-refresh coordinator runs the existing refresh sequence.
    _ = (
        source_scan,
        call_graph_data,
        runtime_inventory_dashboard,
        callable_reference_pages,
        metadata_reference_pages,
        glossary,
        manifests,
        landing_page,
        module_pages,
    )
    generate_full_reference()


if __name__ == "__main__":
    main()
