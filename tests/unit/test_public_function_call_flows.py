"""Tests for the public function call-flow v2 generator."""

from __future__ import annotations

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
        "    public_b()\n"
        "    depth_1()\n"
        "    width_0()\n"
        "    width_1()\n"
        "    width_2()\n"
        "    width_3()\n"
        "    width_4()\n"
        "    width_5()\n"
        "    width_6()\n"
        "    width_7()\n"
        "    width_8()\n"
        "    width_9()\n"
        "    width_10()\n\n"
        "def same_file_helper():\n"
        "    recursive_helper()\n\n"
        "def recursive_helper():\n"
        "    recursive_helper()\n\n"
        "def depth_1():\n"
        "    depth_2()\n\n"
        "def depth_2():\n"
        "    depth_3()\n\n"
        "def depth_3():\n"
        "    depth_4()\n\n"
        "def depth_4():\n"
        "    depth_5()\n\n"
        "def depth_5():\n"
        "    return None\n\n"
        "def width_0():\n"
        "    return None\n\n"
        "def width_1():\n"
        "    return None\n\n"
        "def width_2():\n"
        "    return None\n\n"
        "def width_3():\n"
        "    return None\n\n"
        "def width_4():\n"
        "    return None\n\n"
        "def width_5():\n"
        "    return None\n\n"
        "def width_6():\n"
        "    return None\n\n"
        "def width_7():\n"
        "    return None\n\n"
        "def width_8():\n"
        "    return None\n\n"
        "def width_9():\n"
        "    return None\n\n"
        "def width_10():\n"
        "    return None\n\n"
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
    assert "large_depth" in public_a["signals"]
    assert "large_width" in public_a["signals"]
    assert {"refactor_signals", "refactor_summary", "suggested_refactor_action"} <= set(public_a)
    assert public_a["suggested_refactor_action"] == "review_public_calls_public"

    refactor_by_signal = {item["signal"]: item for item in public_a["refactor_signals"]}
    assert refactor_by_signal["public_calls_public"]["severity"] == "warning"
    assert refactor_by_signal["public_calls_public"]["evidence"][0]["function_name"] == "public_b"
    assert refactor_by_signal["cross_file_private_dependency"]["evidence"]
    assert refactor_by_signal["large_depth"]["evidence"][0]["max_depth"] == public_a["max_depth"]
    assert len(refactor_by_signal["large_width"]["evidence"]) == public_a["direct_call_count"]

    unused_records = payload["defined_but_not_used"]
    unused = {item["function_name"] for item in unused_records}
    assert unused == {"unused_local"}
    assert unused_records[0]["suggested_action"] == "review_for_deletion_or_connection"
    assert {"public_functions", "defined_functions", "used_functions", "defined_but_not_used", "summary"} <= set(payload)


def test_dashboard_fetches_json_without_embedding_payload_by_default(tmp_path: Path) -> None:
    """Validate the default dashboard fetches JSON and keeps selected-flow wiring."""
    root, pkg, init_path = write_project(tmp_path)
    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    html = flows.render_dashboard(payload)

    assert "../reference/_data/public-function-call-flows.json" in html
    assert "public-function-call-flows-json" not in html
    assert "fabricops_public_function_call_flows_v2" not in html
    assert "Public functions" in html
    assert "Architecture violations / refactor warnings" in html
    assert "Large depth / width" in html
    assert "Defined but not used" in html
    assert "Used functions" in html
    assert "Defined functions" in html
    assert "searchBox" in html
    assert "signalFilter" in html
    assert "actionFilter" in html
    assert "selected-public-function-panel" in html
    assert "selected-call-tree" in html
    assert "selectedCallableInventoryTable" in html
    assert "definedButNotUsedTable" in html
    assert "selectVisibleInventory" in html
    assert "selectVisibleCleanup" in html
    assert "compatibilityMode" in html
    assert "Export selected packet as JSON" in html
    assert "Export selected packet as YAML" in html
    assert "fabricops_public_function_call_flow_refactor_packet_v2" in html
    assert "renderSelected" in html
    assert "if(e.target.closest('a'))return" in html


def test_dashboard_can_embed_json_for_debug_mode(tmp_path: Path) -> None:
    """Validate optional standalone/debug mode can still embed JSON."""
    root, pkg, init_path = write_project(tmp_path)
    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    html = flows.render_dashboard(payload, embed_json=True)

    assert "public-function-call-flows-json" in html
    assert "fabricops_public_function_call_flows_v2" in html
