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

    public_b = next(item for item in payload["public_functions"] if item["function_name"] == "public_b")
    assert public_b["has_large_width_or_depth"] is False
    assert public_b["has_architecture_violation"] is False
    assert public_b["signals"] == []

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
    assert "<th>Chip</th>" in html
    assert "<th>Relevant section</th>" in html
    assert "<th>Color</th>" not in html
    assert "<th>Where shown</th>" not in html
    assert '<span class="badge warn">Large width/depth</span>' in html
    assert '<span class="badge danger">Architecture violation</span>' in html
    assert '<span class="badge muted">Inline candidate</span>' in html
    assert '<span class="badge muted">Promote to shared</span>' in html
    for violation_type in range(1, 7):
        assert f'<span class="badge danger">Type {violation_type}</span>' in html
    assert '<span class="badge muted">Public function summary cards</span>' in html
    assert '<span class="badge muted">Public function table</span>' in html
    assert '<span class="badge muted">Selected call tree</span>' in html
    assert '<span class="badge muted">Selected callable inventory</span>' in html
    assert '<span class="badge muted">Inventory violation chips</span>' in html
    assert "Width means number of direct package-local calls" in html
    assert "Depth means the deepest nested call path" in html
    assert "Scope means total downstream functions" in html
    assert 'type="button">Width</button>' in html
    assert 'type="button">Scope</button>' in html
    assert 'type="button">Depth</button>' in html
    assert 'type="button">Direct calls</button>' not in html
    assert 'data-sort="suggested_refactor_action"' not in html
    assert "Suggested refactor action" not in html
    assert "Inline candidate" in html
    assert "Promote to shared" in html
    assert "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/" in html
    assert "voycepeh.github.io/src" not in html
    assert "functionLink(f)}</td><td>${esc(f.derived_width)}</td>" in html
    assert "<td>${badges(publicSignalsForFunction(f))}</td><td>${esc(f.source_path)}</td>" in html
    assert '<th class="col-select">Select</th><th class="col-small"><button class="sort-button" data-inventory-sort="call_depth" type="button" title="Distance from the selected public callable root.">Call depth</button></th><th class="col-function"><button class="sort-button" data-inventory-sort="function_name" type="button">Function</button></th><th class="col-type"><button class="sort-button" data-inventory-sort="function_type" type="button">Type</button></th><th class="col-small"><button class="sort-button" data-inventory-sort="function_width" type="button" title="Number of direct package-local calls made by this function.">Width</button></th><th class="col-small"><button class="sort-button" data-inventory-sort="function_scope" type="button" title="Total downstream functions reached from this function.">Scope</button></th><th class="col-small"><button class="sort-button" data-inventory-sort="function_downstream_depth" type="button" title="Deepest downstream call path from this function.">Depth</button></th><th>Violation</th><th>Inline candidate</th><th>Promote to shared</th><th class="col-file"><button class="sort-button" data-inventory-sort="source_path" type="button">File</button></th>' in html
    assert "function inventoryDownstreamMetrics(flow,qualifiedName)" in html
    assert "function enrichInventoryRows(rows,flow)" in html
    assert "<td>${esc(n.call_depth)}</td><td>${functionLink(n)}</td><td>${esc(n.function_type)}</td><td>${esc(n.function_width)}</td><td>${esc(n.function_scope)}</td><td>${esc(n.function_downstream_depth)}</td><td>${violationBadges(n)}" in html
    assert "<td>${n.promote_to_shared_candidate?'Yes':'No'}</td><td>${esc(n.source_path)}</td>" in html
    assert ">Parent</button>" not in html
    assert "large_width_or_depth" in html
    assert "Architecture violation" in html
    assert "Public functions with architecture violation" in html
    assert "Public functions with large width/depth" in html
    assert "Supported by" in html
    assert "Shared helper functions" in html
    assert "Nested private functions" in html
    assert '<article class="architecture-summary-card"><strong id="card-public">0</strong><div class="card-title">Public functions</div><div class="card-kicker">Main review</div></article>' in html
    assert '<article class="architecture-summary-card risk"><strong id="card-warnings">0</strong><div class="card-title">Public functions with architecture violation</div><div class="card-kicker">Main review</div></article>' in html
    assert '<article class="architecture-summary-card review"><strong id="card-large">0</strong><div class="card-title">Public functions with large width/depth</div><div class="card-kicker">Main review</div></article>' in html
    assert '<article class="architecture-summary-card"><strong id="card-shared-helpers">0</strong><div class="card-title">Shared helper functions</div><div class="card-kicker">Supported by</div></article>' in html
    assert '<article class="architecture-summary-card"><strong id="card-private-functions">0</strong><div class="card-title">Nested private functions</div><div class="card-kicker">Supported by</div></article>' in html
    assert '<article class="architecture-summary-card info"><div class="card-kicker">Main review</div><div class="card-title">Public functions</div>' not in html
    assert '<article class="architecture-summary-card good"><div class="card-kicker">Supported by</div><div class="card-title">Shared helper functions</div>' not in html
    assert "Main reviewPublic functions" not in html
    assert "card-shared-helpers" in html
    assert "card-private-functions" in html
    assert "uniqueFlowCount('shared_function')" in html
    assert "uniqueFlowCount('private_function')" in html
    assert "DATA.public_functions.filter(f=>hasPublicSignal(f,'architecture_violation')).length" in html
    assert "DATA.public_functions.filter(f=>hasPublicSignal(f,'large_width_or_depth')).length" in html
    assert "function publicSignalsForFunction(f)" in html
    assert "function normalizePublicFunction(f)" in html
    assert "function derivePublicMetrics(f)" in html
    assert "function deriveFlowEdges(flow)" in html
    assert "function deriveArchitectureViolations(flow)" in html
    assert "function deriveInventorySignals(flow)" in html
    assert "(f.derived_width??0)>10||(f.derived_depth??0)>5" in html
    assert "return publicSignalsForFunction(f).includes(signal)" in html
    assert "publicSignalsForFunction(f)" in html
    assert "DATA.public_functions.flatMap(publicSignalsForFunction)" in html
    assert "${esc(signalLabel(v))}" in html
    assert "publicSignalsForFunction(f).map(signalLabel).join(' ')" in html
    assert "f.signals" not in html
    assert 'id="card-used"' not in html
    assert 'id="card-defined"' not in html
    assert "fabricops_public_function_call_flow_refactor_packet_v2" in html
    assert "signal_rules" in html
    assert "architecture_violation_rules" in html
    assert "inventory_suggestion_rules" in html
    assert "cleanup_mode" in html
    assert "export_scope" in html
    assert "export_scope_reason" in html
    assert "omitted_inventory_assets" in html
    assert "violation_types" in html
    assert "violation_details" in html
    assert "inline_candidate" in html
    assert "promote_to_shared_candidate" in html
    assert 'id="selected-call-tree-heading"' in html
    assert 'id="selected-callable-inventory-heading"' in html
    assert 'href="#selected-callable-inventory-heading"' in html
    assert 'href="#selected-call-tree-heading"' in html
    assert 'data-tree-depth="1"' in html
    assert 'data-tree-depth="2"' in html
    assert 'data-tree-depth="3"' in html
    assert 'data-tree-depth="4"' in html
    assert 'data-tree-depth="all"' in html
    assert 'data-tree-depth="0"' in html
    assert 'data-tree-node-toggle' in html
    assert 'aria-expanded' in html
    assert 'function hiddenTreeStats(node)' in html
    assert 'function treeSummaryChips(node)' in html
    assert 'children ${stats.children}' in html
    assert 'downstream ${stats.downstream}' in html
    assert 'max depth ${stats.maxDepth}' in html
    assert 'violations ${stats.violations}' in html
    assert '+ ${stats.downstream} hidden' in html
    assert 'function setTreeDepth(depth)' in html
    assert 'function initializeTreeExpansion(flow)' in html
    assert "selected_flow_functions" in html
    assert "selected_inventory_assets" in html
    assert "derived_width" in html
    assert "derived_scope" in html
    assert "derived_depth" in html
    assert "derived_public_signals" in html
    assert "deterministic_signal_rules" in html
    assert "derived_architecture_violations" in html
    assert "public_calls_public" not in html
    assert "cross_file_private_dependency" not in html
    assert "large_depth" not in html
    assert ">large_width<" not in html
    assert ">large_width</span>" not in html


def test_dashboard_derives_signals_from_old_shape_payload() -> None:
    """Validate dashboard JavaScript derives V2 signals from old-shape JSON."""
    html = flows.render_dashboard({
        "public_functions": [{
            "function_name": "public_root",
            "qualified_name": "pkg.public_root",
            "source_path": "src/pkg/root.py",
            "flow": [
                {"function_name": "public_root", "qualified_name": "pkg.public_root", "function_type": "public_function", "source_path": "src/pkg/root.py", "parent_qualified_name": None, "depth": 0},
                {"function_name": "public_child", "qualified_name": "pkg.public_child", "function_type": "public_dependency", "source_path": "src/pkg/child.py", "parent_qualified_name": "pkg.public_root", "depth": 1},
                {"function_name": "shared_parent", "qualified_name": "pkg.shared_parent", "function_type": "shared_function", "source_path": "src/pkg/shared.py", "parent_qualified_name": "pkg.public_root", "depth": 1},
                {"function_name": "public_from_shared", "qualified_name": "pkg.public_from_shared", "function_type": "public_dependency", "source_path": "src/pkg/pub.py", "parent_qualified_name": "pkg.shared_parent", "depth": 2},
                {"function_name": "private_parent", "qualified_name": "pkg.private_parent", "function_type": "private_function", "source_path": "src/pkg/private.py", "parent_qualified_name": "pkg.public_root", "depth": 1},
                {"function_name": "public_from_private", "qualified_name": "pkg.public_from_private", "function_type": "public_dependency", "source_path": "src/pkg/pub2.py", "parent_qualified_name": "pkg.private_parent", "depth": 2},
                {"function_name": "cross_private", "qualified_name": "pkg.cross_private", "function_type": "private_function", "source_path": "src/pkg/other.py", "parent_qualified_name": "pkg.shared_parent", "depth": 2},
                {"function_name": "other_private", "qualified_name": "pkg.other_private", "function_type": "private_function", "source_path": "src/pkg/other2.py", "parent_qualified_name": "pkg.private_parent", "depth": 2},
                {"function_name": "shared_from_private", "qualified_name": "pkg.shared_from_private", "function_type": "shared_function", "source_path": "src/pkg/shared2.py", "parent_qualified_name": "pkg.private_parent", "depth": 2},
                {"function_name": "deep_helper", "qualified_name": "pkg.deep_helper", "function_type": "private_function", "source_path": "src/pkg/deep.py", "parent_qualified_name": "pkg.shared_from_private", "depth": 6},
                {"function_name": "inline_helper", "qualified_name": "pkg.inline_helper", "function_type": "private_function", "source_path": "src/pkg/inline.py", "parent_qualified_name": "pkg.public_root", "depth": 1},
                {"function_name": "promote_helper", "qualified_name": "pkg.promote_helper", "function_type": "private_function", "source_path": "src/pkg/promote.py", "parent_qualified_name": "pkg.shared_parent", "depth": 2},
                {"function_name": "promote_helper", "qualified_name": "pkg.promote_helper", "function_type": "private_function", "source_path": "src/pkg/promote.py", "parent_qualified_name": "pkg.private_parent", "depth": 2},
            ] + [
                {"function_name": f"wide_{i}", "qualified_name": f"pkg.wide_{i}", "function_type": "private_function", "source_path": f"src/pkg/wide_{i}.py", "parent_qualified_name": "pkg.public_root", "depth": 1}
                for i in range(11)
            ],
        }]
    })

    assert "normalizeDashboardData(data)" in html
    assert "derived_width:width||f.direct_call_count||f.width||0" in html
    assert "derived_scope:scope||f.transitive_function_count||f.scope||0" in html
    assert "derived_depth:depths.length?Math.max(...depths):f.max_depth||f.depth||0" in html
    assert "pt==='public_function'||pt==='public_dependency'" in html
    assert "return 'Type 1'" in html
    assert "return 'Type 2'" in html
    assert "return 'Type 3'" in html
    assert "return 'Type 4'" in html
    assert "return 'Type 5'" in html
    assert "return 'Type 6'" in html
    assert "row.promote_to_shared_candidate=row.function_type==='private_function'&&row.distinct_caller_count>1" in html
    assert "row.inline_candidate=row.depth!==0&&row.incoming_edge_count===1" in html
    assert "!row.called_multiple_times_by_same_parent" in html
    assert "badges(publicSignalsForFunction(f))" in html
    assert "DATA.public_functions.filter(f=>hasPublicSignal(f,'architecture_violation')).length" in html
    assert "DATA.public_functions.filter(f=>hasPublicSignal(f,'large_width_or_depth')).length" in html
    assert "treeNode(root,node)" in html
    assert "violationBadges(n)" in html
    assert "packetFields(n)" in html
    assert "large_depth" not in html
    assert ">large_width<" not in html


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
    assert "<th>Select</th><th>Function</th><th>Reason</th><th>Suggested action</th><th>File</th>" in html
    assert "functionLink(n)}</td><td>${esc(n.reason)}</td><td>${esc(n.suggested_action)}</td><td>${esc(n.source_path)}</td>" in html
    assert "Download architecture refactor packet" in html
    assert html.count("Download architecture refactor packet") == 1
    assert "Download orphan cleanup packet" in html
    assert "Export scope" in html
    assert "Full selected flow" in html
    assert "Checked functions only" in html
    assert "Inline candidates only" in html
    assert "Architecture violations only" in html
    assert "Promote-to-shared candidates only" in html
    assert "Cleanup mode" in html
    assert "Breaking cleanup" in html
    assert "Preserve compatibility" in html
    assert "Default:</strong> the packet includes the full selected flow." in html
    assert "All functions in this selected flow will be included." in html
    assert "Only checked rows will be included." in html
    assert "Only deterministic inline candidates will be included." in html
    assert "Only rows with Type 1–Type 6 architecture violations will be included." in html
    assert "Only private helpers called by more than one distinct caller will be included." in html
    assert "functions will be exported" in html
    assert "Included by full flow" in html
    assert "checkEnabled=exportScope()==='checked_functions_only'" in html
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
