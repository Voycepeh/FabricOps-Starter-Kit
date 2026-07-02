"""Tests for the public function call-flow v2 generator."""

from __future__ import annotations

import json
from pathlib import Path

from scripts import generate_public_function_call_flows as flows


def write_project(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create a tiny package fixture for call-flow tests."""
    root = tmp_path
    pkg = root / "src" / "fabricops_kit"
    pkg.mkdir(parents=True)
    init_path = pkg / "__init__.py"
    init_path.write_text(
        "from .public_a import PublicClass, public_a\n"
        "from .public_b import public_b\n"
        "EXPORTS = ('public_a', 'public_b', 'PublicClass')\n"
        "__all__ = [*EXPORTS]\n",
        encoding="utf-8",
    )
    (pkg / "public_a.py").write_text(
        "from .shared import helper as imported_helper\n"
        "from . import shared as shared_alias\n\n"
        "DISPATCH = {'x': same_file_helper}\n\n"
        "class PublicClass:\n"
        "    def method(self):\n"
        "        return same_file_helper()\n\n"
        "def public_a():\n"
        "    same_file_helper()\n"
        "    imported_helper()\n"
        "    shared_alias._private_shared()\n"
        "    DISPATCH['x']()\n"
        "    public_b()\n\n"
        "def same_file_helper():\n"
        "    recursive_helper()\n\n"
        "def recursive_helper():\n"
        "    recursive_helper()\n\n"
        "def unused_local():\n"
        "    return None\n\n"
        "from .public_b import public_b\n",
        encoding="utf-8",
    )
    (pkg / "public_b.py").write_text("def public_b():\n    return 'b'\n", encoding="utf-8")
    (pkg / "shared.py").write_text(
        "def helper():\n"
        "    return _private_shared()\n\n"
        "def _private_shared():\n"
        "    return None\n",
        encoding="utf-8",
    )
    return root, pkg, init_path


def test_public_function_call_flow_payload_rules(tmp_path: Path) -> None:
    """Validate discovery, resolution, recursion safety, signals, and unused calculation."""
    root, pkg, init_path = write_project(tmp_path)

    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    assert {item["function_name"] for item in payload["public_functions"]} == {"public_a", "public_b"}
    assert "PublicClass" not in {item["function_name"] for item in payload["defined_functions"]}
    assert "method" not in {item["function_name"] for item in payload["defined_functions"]}

    public_a = next(item for item in payload["public_functions"] if item["function_name"] == "public_a")
    reached = {item["function_name"] for item in public_a["flow"]}
    assert {"same_file_helper", "helper", "_private_shared", "recursive_helper", "public_b"} <= reached
    assert public_a["flow"]
    assert public_a["max_depth"] < 10
    assert "public_calls_public" in public_a["signals"]
    assert "cross_file_private_dependency" in public_a["signals"]

    unused = {item["function_name"] for item in payload["defined_but_not_used"]}
    assert unused == {"unused_local"}
    assert {"public_functions", "defined_functions", "used_functions", "defined_but_not_used", "summary"} <= set(payload)


def test_dashboard_contains_embedded_json_and_selected_flow_wiring(tmp_path: Path) -> None:
    """Validate dashboard renders the embedded data and click-driven selected-flow panel."""
    root, pkg, init_path = write_project(tmp_path)
    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    html = flows.render_dashboard(payload)

    assert "public-function-call-flows-json" in html
    assert "selected-flow-panel" in html
    assert "renderSelected" in html
    assert "addEventListener('click'" in html
    embedded = html.split('type="application/json">', 1)[1].split("</script>", 1)[0]
    assert json.loads(embedded.replace("&quot;", '"'))["metadata"]["schema"] == "fabricops_public_function_call_flows_v2"
