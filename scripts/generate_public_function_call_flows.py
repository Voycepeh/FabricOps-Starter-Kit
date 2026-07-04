"""Compatibility wrapper for public-function call-flow artifact generation.

Prefer running ``generate_public_function_call_flows_json.py`` and
``generate_public_function_call_flows_dashboard.py`` directly.
"""

from __future__ import annotations

from scripts.generate_public_function_call_flows_json import *  # noqa: F403
from scripts.generate_public_function_call_flows_dashboard import render_dashboard
from scripts.generate_public_function_call_flows_dashboard import write_dashboard


def write_outputs(payload, data_path=DATA_PATH, dashboard_path=None):  # type: ignore[name-defined] # noqa: F405, ANN001, ANN201
    """Write both legacy outputs for compatibility callers."""
    write_json(payload, data_path)  # type: ignore[name-defined] # noqa: F405
    if dashboard_path is None:
        write_dashboard()
    else:
        write_dashboard(dashboard_path)


def main() -> None:
    """Generate both legacy public function call-flow artifacts."""
    write_json(build_payload())  # type: ignore[name-defined] # noqa: F405
    write_dashboard()


if __name__ == "__main__":
    main()
