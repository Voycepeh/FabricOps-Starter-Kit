"""Tests for the public function call-flow v2 generator."""

from __future__ import annotations

import ast
from pathlib import Path

from scripts import generate_public_function_call_flows as flows


def write_project(tmp_path: Path) -> tuple[Path, Path, Path]:
    """Create a tiny package fixture for call-flow tests."""
    root = tmp_path
    pkg = root / "src" / "fabricops_kit"
    pkg.mkdir(parents=True)
    init_path = pkg / "__init__.py"
    init_path.write_text(
        "from .public_a import public_a\n"
        "from .public_b import public_b\n"
        "__all__ = ['public_a', 'public_b']\n",
        encoding="utf-8",
    )
    (pkg / "public_a.py").write_text(
        "from .shared import helper as imported_helper\n"
        "from . import shared as shared_alias\n\n"
        "DISPATCH = {'x': same_file_helper}\n\n"
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
        "def depth_1():\n    depth_2()\n\n"
        "def depth_2():\n    depth_3()\n\n"
        "def depth_3():\n    depth_4()\n\n"
        "def depth_4():\n    depth_5()\n\n"
        "def depth_5():\n    depth_6()\n\n"
        "def depth_6():\n    return None\n\n"
        + "".join(f"def width_{i}():\n    return None\n\n" for i in range(11))
        + "def unused_local():\n    return None\n\n"
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


def info(name: str, path: str) -> flows.FunctionInfo:
    """Build minimal function metadata for violation classifier tests."""
    node = ast.parse(f"def {name}():\n    pass\n").body[0]
    assert isinstance(node, ast.FunctionDef)
    return flows.FunctionInfo(name, f"fabricops_kit.{path.replace('/', '.').removesuffix('.py')}.{name}", path, 1, 2, node)


def test_public_function_call_flow_payload_rules(tmp_path: Path) -> None:
    """Validate deterministic signal fields, thresholds, candidates, and unused calculation."""
    root, pkg, init_path = write_project(tmp_path)

    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    public_a = next(item for item in payload["public_functions"] if item["function_name"] == "public_a")
    reached = {item["function_name"] for item in public_a["flow"]}
    assert {"same_file_helper", "helper", "_private_shared", "recursive_helper", "public_b"} <= reached
    assert public_a["width"] > 10
    assert public_a["depth"] > 5
    assert public_a["has_large_width_or_depth"] is True
    assert public_a["has_architecture_violation"] is True
    assert public_a["signals"] == ["large_width_or_depth", "architecture_violation"]
    assert public_a["public_signals"] == ["large_width_or_depth", "architecture_violation"]
    assert public_a["architecture_violation_count"] >= 1

    public_b_row = next(item for item in public_a["flow"] if item["function_name"] == "public_b")
    assert public_b_row["violation_types"] == ["Type 1"]
    assert public_b_row["violation_details"] == ["Public function calls another public function directly."]
    assert public_b_row["inline_candidate"] is True
    assert public_b_row["promote_to_shared_candidate"] is False
    assert public_b_row["distinct_caller_count"] == 1

    unused_records = payload["defined_but_not_used"]
    assert {item["function_name"] for item in unused_records} == {"unused_local"}
    assert payload["metadata"]["generated_at_sgt"].endswith(" SGT")
    assert payload["metadata"]["source_json_url"] == flows.SOURCE_JSON_URL


def test_large_width_or_depth_thresholds_are_strict() -> None:
    """Validate deterministic large width/depth thresholds."""
    root = info("public_root", "src/fabricops_kit/root.py")
    assert flows.calculate_refactor_signals(root, [], 10, 5) == []
    assert flows.calculate_refactor_signals(root, [], 11, 5)[0]["signal"] == "large_width_or_depth"
    assert flows.calculate_refactor_signals(root, [], 10, 6)[0]["signal"] == "large_width_or_depth"


def test_architecture_violation_type_classification() -> None:
    """Validate all deterministic architecture violation edge types."""
    public = info("public_a", "src/fabricops_kit/public_a.py")
    other_public = info("public_b", "src/fabricops_kit/public_b.py")
    shared = info("helper", "src/fabricops_kit/shared.py")
    private = info("_private", "src/fabricops_kit/private.py")
    other_private = info("_other_private", "src/fabricops_kit/other.py")

    assert flows.classify_architecture_violation(public, other_public, "public_function", "public_dependency")["type"] == "Type 1"
    assert flows.classify_architecture_violation(shared, public, "shared_function", "public_dependency")["type"] == "Type 2"
    assert flows.classify_architecture_violation(private, public, "private_function", "public_dependency")["type"] == "Type 3"
    assert flows.classify_architecture_violation(shared, other_private, "shared_function", "private_function")["type"] == "Type 4"
    assert flows.classify_architecture_violation(private, other_private, "private_function", "private_function")["type"] == "Type 5"
    assert flows.classify_architecture_violation(private, shared, "private_function", "shared_function")["type"] == "Type 6"
    assert flows.classify_architecture_violation(shared, info("_same", "src/fabricops_kit/shared.py"), "shared_function", "private_function") is None


def test_dashboard_signal_wording_columns_and_links(tmp_path: Path) -> None:
    """Validate focused dashboard wording, deterministic columns, and GitHub blob links."""
    root, pkg, init_path = write_project(tmp_path)
    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    html = flows.render_dashboard(payload)

    assert "Width &gt; 10 or Depth &gt; 5" in html

    assert "Signal rules and calculations" in html
    assert '<details class="flow-details signal-rules">' in html
    for violation_type in ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5", "Type 6"]:
        assert violation_type in html
    assert "Public function calls another public function directly." in html
    assert "Shared function calls a public function directly." in html
    assert "Private function calls a public function directly." in html
    assert "Shared function calls a private function from another file." in html
    assert "Private function calls a private function from another file." in html
    assert "Private function calls a shared function directly." in html
    assert "Yes when called by exactly one parent function" in html
    assert "Yes when function_type is private_function" in html
    assert "Width means number of direct package-local calls" in html
    assert "Depth means the deepest nested call path" in html
    assert "Scope means total downstream functions" in html
    assert 'type="button">Width</button>' in html
    assert 'type="button">Scope</button>' in html
    assert 'type="button">Depth</button>' in html
    assert 'type="button">Direct calls</button>' not in html
    assert 'data-sort="suggested_refactor_action"' not in html
    assert "Suggested refactor action" not in html
    assert "Violation detail" in html
    assert "Inline candidate" in html
    assert "Promote to shared" in html
    assert "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/" in html
    assert "voycepeh.github.io/src" not in html
    assert "functionLink(f)}</td><td>${esc(f.source_path)}</td>" in html
    assert "functionLink(n)}</td><td>${esc(n.source_path)}</td>" in html
    assert "large_width_or_depth" in html
    assert "Architecture violation" in html
    assert "With architecture violation" in html
    assert "With large width/depth" in html
    assert "Supported by" in html
    assert "Shared helper functions" in html
    assert "Nested private functions" in html
    assert "card-shared-helpers" in html
    assert "card-private-functions" in html
    assert "uniqueFlowCount('shared_function')" in html
    assert "uniqueFlowCount('private_function')" in html
    assert 'id="card-used"' not in html
    assert 'id="card-defined"' not in html
    assert "fabricops_public_function_call_flow_refactor_packet_v2" in html
    assert "signal_rules" in html
    assert "per_function_violation_details" in html


def test_dashboard_fetches_json_without_embedding_payload_by_default(tmp_path: Path) -> None:
    """Validate the default dashboard fetches JSON and keeps selected-flow wiring."""
    root, pkg, init_path = write_project(tmp_path)
    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    html = flows.render_dashboard(payload)

    assert "loadDashboardData('../reference/_data/public-function-call-flows.json')" in html
    assert "public-function-call-flows-json" not in html
    assert "fabricops_public_function_call_flows_v2" not in html
    assert "selected-public-function-panel" in html
    assert "selected-call-tree" in html
    assert "function treeNode(root,node)" in html
    assert "selectedCallableInventoryTable" in html
    assert "definedButNotUsedTable" in html
    assert "Download architecture refactor packet" in html
    assert "Download orphan cleanup packet" in html
    assert "Export selected packet as YAML" not in html
    assert "Copy AI refactor prompt" not in html
    assert "showWorkflow" in html
    assert "if(e.target.closest('a'))return" in html


def test_dashboard_can_embed_json_for_debug_mode(tmp_path: Path) -> None:
    """Validate optional standalone/debug mode can still embed JSON."""
    root, pkg, init_path = write_project(tmp_path)
    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    html = flows.render_dashboard(payload, embed_json=True)

    assert "public-function-call-flows-json" in html
    assert "fabricops_public_function_call_flows_v2" in html


def test_callable_flow_docs_page_uses_deterministic_signal_rules() -> None:
    """Validate callable flow docs describe the deterministic V2 signal model."""
    docs = Path("docs/reference/function-call-graph.md").read_text(encoding="utf-8")

    assert "#### Public-flow signals" in docs
    assert "Large width/depth | Yellow | Width > 10 or Depth > 5" in docs
    assert "Architecture violation | Red | Any Type 1-6 architecture violation" in docs
    assert "#### Architecture violation types" in docs
    for violation_type in ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5", "Type 6"]:
        assert violation_type in docs
    assert "#### Inventory suggestions" in docs
    assert "Inline candidate | Called by exactly one parent" in docs
    assert "Promote to shared | Private function called by more than one distinct caller" in docs
    assert "#### Metric definitions" in docs
    assert "Width | Direct package-local calls from the selected public function." in docs
    assert "Depth | Deepest nested call path." in docs
    assert "Scope | Total downstream functions reached by the selected public function flow." in docs
    assert "Broken rule | An architecture rule is broken" not in docs
    assert "Too many steps" not in docs
    assert "Too many helpers" not in docs
    assert "Shared helper | The helper is used by more than one public function" not in docs
    assert "Maybe combine" not in docs
