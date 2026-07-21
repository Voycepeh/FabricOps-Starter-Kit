"""Tests for the public function call-flow v2 generator."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import time

import pytest

from scripts import generate_public_function_call_flows_dashboard as dashboard
from scripts import generate_public_function_call_flows_json as flows


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


def write_manifest(root: Path) -> Path:
    """Create a minimal lifecycle manifest fixture."""
    manifests = root / "docs" / "releases" / "manifests"
    manifests.mkdir(parents=True)
    (manifests / "0.1.0.yml").write_text(
        "release_version: 0.1.0\n"
        "functions:\n"
        "  - name: public_a\n"
        "    qualified_name: fabricops_kit.public_a.public_a\n"
        "    status: live\n"
        "    live_since: 0.1.0\n"
        "  - name: public_b\n"
        "    qualified_name: fabricops_kit.public_b.public_b\n"
        "    status: preview\n"
        "metadata_tables:\n",
        encoding="utf-8",
    )
    return manifests


def write_versioned_manifest(manifests: Path, version: str, status: str = "preview") -> None:
    """Write one minimal release manifest for semantic version tests."""
    manifests.mkdir(parents=True, exist_ok=True)
    (manifests / f"{version}.yml").write_text(
        f"release_version: {version}\n"
        "functions:\n"
        "  - name: public_a\n"
        "    qualified_name: fabricops_kit.public_a.public_a\n"
        f"    status: {status}\n"
        "  - name: public_b\n"
        "    qualified_name: fabricops_kit.public_b.public_b\n"
        "    status: preview\n"
        "metadata_tables:\n",
        encoding="utf-8",
    )


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
    assert "generated_at_sgt" not in payload["metadata"]
    assert "generated_at_utc" not in payload["metadata"]
    assert payload["metadata"]["source_json_url"] == flows.SOURCE_JSON_URL
    assert set(payload["metadata"]["architecture_violation_rules"]) == {
        "Type 1",
        "Type 2",
        "Type 3",
        "Type 4",
        "Type 5",
    }
    assert "Type 6" not in payload["metadata"]["architecture_violation_rules"]
    assert payload["metadata"]["architecture_violation_signal"] == "Any Type 1 to Type 5 edge appears in the public function flow."


def test_release_lifecycle_and_live_impact_contract(tmp_path: Path) -> None:
    """Validate manifest-sourced lifecycle metadata and Live dependency impact."""
    root, pkg, init_path = write_project(tmp_path)
    manifests = write_manifest(root)

    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path, manifests_dir=manifests)

    public_a = next(item for item in payload["public_functions"] if item["function_name"] == "public_a")
    assert public_a["lifecycle_status"] == "live"
    assert public_a["live_since"] == "0.1.0"
    assert public_a["release_history"] == [{"version": "0.1.0", "status": "live"}]
    assert public_a["release_versions"] == ["0.1.0"]
    assert public_a["contract_classification"] == "live_public_function"
    assert public_a["contract_display"] == "Live · Live since 0.1.0"
    assert public_a["contract_risk"] == "live"

    public_b = next(item for item in payload["public_functions"] if item["function_name"] == "public_b")
    assert public_b["lifecycle_status"] == "preview"
    assert public_b["contract_classification"] == "preview_public_function"
    assert public_b["contract_risk"] == "preview"

    assert payload["release_contract"]["release_versions"] == ["0.1.0"]
    assert payload["release_contract"]["latest_release_version"] == "0.1.0"
    assert payload["release_contract"]["live_public_function_count"] == 1
    assert payload["release_contract"]["preview_public_function_count"] == 1

    helper = next(item for item in public_a["flow"] if item["function_name"] == "helper")
    assert helper["lifecycle_status"] == "internal"
    assert helper["direct_live_dependents"] == ["fabricops_kit.public_a.public_a"]
    assert helper["transitive_live_dependents"] == []
    assert helper["supports_live_contract"] is True
    assert helper["live_impact_level"] == "direct_live_dependency"
    assert helper["contract_classification"] == "live_critical_internal"

    private_shared = next(item for item in public_a["flow"] if item["function_name"] == "_private_shared")
    assert private_shared["direct_live_dependents"] == ["fabricops_kit.public_a.public_a"]
    assert private_shared["transitive_live_dependents"] == []
    assert private_shared["direct_live_dependents"] == sorted(set(private_shared["direct_live_dependents"]))
    assert private_shared["transitive_live_dependents"] == sorted(set(private_shared["transitive_live_dependents"]))
    assert private_shared["contract_classification"] == "live_critical_internal"

    public_b_root = next(item for item in public_b["flow"] if item["qualified_name"] == "fabricops_kit.public_b.public_b")
    assert public_b_root["live_impact_level"] == "preview_only"
    assert public_b_root["supports_live_contract"] is False
    assert public_b_root["lifecycle_status"] == "preview"


def test_isolated_fixture_without_manifests_allows_preview_fallback(tmp_path: Path) -> None:
    """Validate isolated fixtures with no manifests can still build as Preview."""
    root, pkg, init_path = write_project(tmp_path)
    manifests = root / "docs" / "releases" / "manifests"
    manifests.mkdir(parents=True)

    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path, manifests_dir=manifests)

    assert {item["lifecycle_status"] for item in payload["public_functions"]} == {"preview"}
    assert all(item["live_since"] is None for item in payload["public_functions"])


def test_missing_manifest_entry_fails_when_manifests_exist(tmp_path: Path) -> None:
    """Validate manifest-backed generation fails when a public callable is omitted."""
    root, pkg, init_path = write_project(tmp_path)
    manifests = root / "docs" / "releases" / "manifests"
    manifests.mkdir(parents=True)
    (manifests / "0.1.0.yml").write_text(
        "release_version: 0.1.0\n"
        "functions:\n"
        "  - name: public_a\n"
        "    qualified_name: fabricops_kit.public_a.public_a\n"
        "    status: live\n"
        "    live_since: 0.1.0\n"
        "metadata_tables:\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Public callable missing from release manifests"):
        flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path, manifests_dir=manifests)


def test_read_function_lifecycle_accepts_custom_manifest_directory(tmp_path: Path) -> None:
    """Validate call-flow lifecycle loading works with explicit manifest directories."""
    manifests = tmp_path / "custom-manifests"
    manifests.mkdir()
    (manifests / "0.1.0.yml").write_text(
        "release_version: 0.1.0\n"
        "functions:\n"
        "  - name: public_a\n"
        "    qualified_name: fabricops_kit.public_a.public_a\n"
        "    status: live\n"
        "    live_since: 0.1.0\n"
        "metadata_tables:\n",
        encoding="utf-8",
    )

    lifecycle_by_qn, release_versions = flows.read_function_lifecycle(manifests)

    assert release_versions == ["0.1.0"]
    assert lifecycle_by_qn["fabricops_kit.public_a.public_a"].lifecycle_status == "live"


def test_release_manifests_use_semantic_version_order(tmp_path: Path) -> None:
    """Validate 0.10.0 sorts after 0.2.0 for release-contract metadata."""
    root, pkg, init_path = write_project(tmp_path)
    manifests = root / "docs" / "releases" / "manifests"
    write_versioned_manifest(manifests, "0.10.0", status="live")
    write_versioned_manifest(manifests, "0.1.0", status="preview")
    write_versioned_manifest(manifests, "0.2.0", status="preview")

    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path, manifests_dir=manifests)

    assert payload["release_contract"]["release_versions"] == ["0.1.0", "0.2.0", "0.10.0"]
    assert payload["release_contract"]["latest_release_version"] == "0.10.0"
    public_a = next(item for item in payload["public_functions"] if item["function_name"] == "public_a")
    assert public_a["lifecycle_status"] == "live"
    assert public_a["release_history"] == [
        {"version": "0.1.0", "status": "preview"},
        {"version": "0.2.0", "status": "preview"},
        {"version": "0.10.0", "status": "live"},
    ]


def test_repository_manifest_lifecycle_authority() -> None:
    """Validate repository release manifest lifecycle fields drive real output."""
    payload = flows.build_payload()

    excel = next(item for item in payload["public_functions"] if item["function_name"] == "read_lakehouse_excel")
    assert excel["lifecycle_status"] == "live"
    assert excel["live_since"] == "0.1.0"
    assert excel["release_history"] == [{"version": "0.1.0", "status": "live"}]

    preview = next(item for item in payload["public_functions"] if item["function_name"] == "display_guardrail_results")
    assert preview["lifecycle_status"] == "preview"
    assert preview["live_since"] is None

    manifest = flows.load_release_manifests()[0]
    expected_live = sum(1 for item in manifest["functions"] if item["status"] == "live")
    assert payload["release_contract"]["live_public_function_count"] == expected_live


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
    assert flows.classify_architecture_violation(private, shared, "private_function", "shared_function") is None
    assert flows.classify_architecture_violation(shared, info("_same", "src/fabricops_kit/shared.py"), "shared_function", "private_function") is None
    widget = info("widget_review", "src/fabricops_kit/widgets/review.py")
    assert flows.classify_architecture_violation(widget, public, "widget_function", "public_dependency") is None
    assert flows.classify_architecture_violation(public, widget, "public_function", "widget_function", callee_is_public=True)["type"] == "Type 1"


def test_widget_function_classification_requires_widget_folder_prefix_and_public_export() -> None:
    """Validate widget classification requires package, naming convention, and public export."""
    public_widget = info("widget_review", "src/fabricops_kit/widgets/review.py")
    internal_widget_helper = info("widget_common", "src/fabricops_kit/widgets/shared.py")
    public_widget_without_prefix = info("review", "src/fabricops_kit/widgets/review.py")
    public_widget_outside_package = info("widget_review", "src/fabricops_kit/review.py")

    public_qns = {
        public_widget.qualified_name,
        public_widget_without_prefix.qualified_name,
        public_widget_outside_package.qualified_name,
    }

    assert flows.function_type(public_widget, public_qns) == "widget_function"
    assert flows.function_type(internal_widget_helper, public_qns) == "shared_function"
    assert flows.function_type(public_widget_without_prefix, public_qns, public_widget_without_prefix.qualified_name) == "public_function"
    assert flows.function_type(public_widget_outside_package, public_qns, public_widget_outside_package.qualified_name) == "public_function"


def test_widget_to_public_edge_is_visible_and_allowed(tmp_path: Path) -> None:
    """Validate widget-to-public composition remains in the flow without Type 1."""
    root = tmp_path
    pkg = root / "src" / "fabricops_kit"
    widgets = pkg / "widgets"
    widgets.mkdir(parents=True)
    init_path = pkg / "__init__.py"
    init_path.write_text(
        "from .widgets.review import widget_review\n"
        "from .public_target import public_target\n"
        "__all__ = ['widget_review', 'public_target']\n",
        encoding="utf-8",
    )
    (widgets / "review.py").write_text(
        "from ..public_target import public_target\n\n"
        "def widget_review():\n"
        "    return public_target()\n",
        encoding="utf-8",
    )
    (pkg / "public_target.py").write_text("def public_target():\n    return None\n", encoding="utf-8")

    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    widget_flow = next(item for item in payload["public_functions"] if item["function_name"] == "widget_review")
    widget_root = widget_flow["flow"][0]
    target_edge = next(item for item in widget_flow["flow"] if item["function_name"] == "public_target")
    assert widget_root["function_type"] == "widget_function"
    assert target_edge["parent_qualified_name"] == widget_root["qualified_name"]
    assert target_edge["architecture_violations"] == []
    assert widget_flow["architecture_violation_count"] == 0


def test_private_function_calling_shared_function_is_allowed(tmp_path: Path) -> None:
    """Validate private-to-shared edges do not create architecture violations."""
    root = tmp_path
    pkg = root / "src" / "fabricops_kit"
    pkg.mkdir(parents=True)
    init_path = pkg / "__init__.py"
    init_path.write_text("from .public_root import public_root\n__all__ = ['public_root']\n", encoding="utf-8")
    (pkg / "public_root.py").write_text(
        "from .shared import reusable_helper\n\n"
        "def public_root():\n"
        "    _private_impl()\n\n"
        "def _private_impl():\n"
        "    reusable_helper()\n",
        encoding="utf-8",
    )
    (pkg / "shared.py").write_text("def reusable_helper():\n    return None\n", encoding="utf-8")

    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    public_root = payload["public_functions"][0]
    shared_row = next(item for item in public_root["flow"] if item["function_name"] == "reusable_helper")
    assert shared_row["architecture_violations"] == []
    assert shared_row["violation_types"] == []
    assert shared_row["violation_details"] == []
    assert public_root["architecture_violation_count"] == 0
    assert public_root["has_architecture_violation"] is False
    assert "architecture_violation" not in public_root["signals"]
    assert "architecture_violation" not in public_root["public_signals"]
    assert all(signal["signal"] != "architecture_violation" for signal in public_root["refactor_signals"])


def test_dashboard_signal_wording_columns_and_links(tmp_path: Path) -> None:
    """Validate focused dashboard wording, deterministic columns, and GitHub blob links."""
    root, pkg, init_path = write_project(tmp_path)
    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    html = dashboard.render_dashboard(payload)

    assert "Width &gt; 10 or Depth &gt; 5" in html

    assert "Signals highlight public callable flows that may need cleanup" not in html
    assert '<section class="flow-details signal-rules">' not in html
    assert "Signal rules and calculations" not in html
    for violation_type in ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5"]:
        assert violation_type in html
    assert "Type 6" not in html
    assert "Public function calls another public function directly." in html
    assert "Shared function calls a public function directly." in html
    assert "Private function calls a public function directly." in html
    assert "Shared function calls a private function from another file." in html
    assert "Private function calls a private function from another file." in html
    assert "Private function calls a shared function directly." not in html
    assert "Called by exactly one parent, not recursive" in html
    assert "Private function called by more than one distinct caller" in html
    assert "<th>Chip</th>" not in html
    assert "<th>Relevant section</th>" not in html
    assert "<th>Color</th>" not in html
    assert "<th>Where shown</th>" not in html
    assert '<span class="badge warn">Large width/depth</span>' in html
    assert '<span class="badge danger">Architecture violation</span>' in html
    assert '<span class="badge muted">Inline candidate</span>' in html
    assert '<span class="badge muted">Promote to shared</span>' in html
    for violation_type in range(1, 6):
        assert f'<span class="badge danger">Type {violation_type}</span>' in html
    assert '<span class="badge danger">Type 6</span>' not in html
    assert "Public function summary card signals" not in html
    assert "Public function table signals" in html
    assert "Call tree violation rules" in html
    assert "Selected callable inventory signals" in html
    assert '<details class="flow-details signal-explainer" open><summary>Public function table signals</summary>' in html
    assert '<details class="flow-details signal-explainer" open><summary>Call tree violation rules</summary>' in html
    assert '<details class="flow-details signal-explainer" open><summary>Selected callable inventory signals</summary>' in html
    assert '<div class="signal-row"><span class="badge warn">Large width/depth</span><span class="signal-text">Width &gt; 10 or Depth &gt; 5.</span></div>' in html
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

    assert "selected-function-strip" in html
    assert "flow-summary-card" not in html
    assert "flow-meta" not in html
    assert '<span class="metric-chip">Width ${esc(f.derived_width)}</span>' in html
    assert '<span class="metric-chip">Scope ${esc(f.derived_scope)}</span>' in html
    assert '<span class="metric-chip">Depth ${esc(f.derived_depth)}</span>' in html
    assert '<span class="metric-chip">Files ${esc((f.files_touched||[]).length)}</span>' in html
    assert '${badges(publicSignalsForFunction(f))}' in html
    assert "functionLink(f)}<div>${publicLifecycleBits(f)}</div></td><td>${esc(f.derived_width)}</td>" in html
    assert "<td>${badges(publicSignalsForFunction(f))}</td><td>${esc(f.source_path)} · ${githubLink(f)}</td>" in html
    assert '<th class="col-select">Select</th><th class="col-small"><button class="sort-button" data-inventory-sort="call_depth" type="button" title="Distance from the selected public callable root.">Call depth</button></th><th class="col-function"><button class="sort-button" data-inventory-sort="function_name" type="button">Function</button></th><th class="col-type"><button class="sort-button" data-inventory-sort="function_type" type="button">Type</button></th><th class="col-small"><button class="sort-button" data-inventory-sort="function_width" type="button" title="Number of direct package-local calls made by this function.">Width</button></th><th class="col-small"><button class="sort-button" data-inventory-sort="function_scope" type="button" title="Total downstream functions reached from this function.">Scope</button></th><th class="col-small"><button class="sort-button" data-inventory-sort="function_downstream_depth" type="button" title="Deepest downstream call path from this function.">Depth</button></th><th>Violation</th><th>Inline candidate</th><th>Promote to shared</th><th class="col-file"><button class="sort-button" data-inventory-sort="source_path" type="button">File</button></th>' in html
    assert "function inventoryDownstreamMetrics(flow,qualifiedName)" in html
    assert "function enrichInventoryRows(rows,flow)" in html
    assert "<td>${esc(n.call_depth)}</td><td>${functionLink(n)}</td><td>${esc(n.function_type)}<div>${isPublicCallableType(n.function_type)?'':liveImpactChip(n)}</div>" in html
    assert "<td>${esc(n.function_width)}</td><td>${esc(n.function_scope)}</td><td>${esc(n.function_downstream_depth)}</td><td>${violationBadges(n)}" in html
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
    assert "fabricops_public_function_call_flow_refactor_packet_v3" in html
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
    assert '<a class="nav-button" href="#selected-callable-inventory-heading">View callable inventory</a>' in html
    assert '<a class="nav-button" href="#selected-call-tree-heading">Back to call tree</a>' in html
    assert 'Go to selected callable inventory' not in html
    assert '<p><a class="section-jump source-link" href="#selected-call-tree-heading">Back to call tree</a></p>' not in html
    assert 'section-heading-row' in html
    assert 'id="treeDepthControls"' in html
    assert 'function selectedMaxCallDepth(flow)' in html
    assert 'function depthButtonValues(maxDepth)' not in html
    assert 'Expand ${d===maxDepth&&maxDepth>6?' not in html
    assert 'data-tree-depth-slider' in html
    assert 'type="range" min="1" max="${maxDepth}" value="${currentDepth}"' in html
    assert 'Min depth' in html
    assert 'Max depth' in html
    assert 'Depth ${currentDepth} of ${maxDepth}' in html
    assert 'data-tree-depth-action="all"' in html
    assert 'data-tree-depth-action="0"' in html
    assert 'data-tree-node-toggle' in html
    assert 'aria-expanded' in html
    assert 'function hiddenTreeStats(node)' in html
    assert 'function treeSummaryMeta(node)' in html
    assert 'class="tree-summary"' not in html
    assert 'class="tree-meta"' in html
    assert '`children ${stats.children}`' in html
    assert '`downstream ${stats.downstream}`' in html
    assert '`max depth ${stats.maxDepth}`' in html
    assert '`${stats.downstream} hidden`' in html
    assert '`violations ${stats.violations}`' in html
    assert 'title="${esc(summary)}"' in html
    assert 'function setTreeDepth(depth)' in html
    assert 'selectedTreeDepth=Math.min(2,Math.max(1,selectedMaxCallDepth(flow)))' in html
    assert "if(e.target.matches('[data-tree-depth-slider]'))setTreeDepth(Number(e.target.value))" in html
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
    html = dashboard.render_dashboard({
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
    assert "new Set(flow.filter(n=>n.parent_qualified_name===root).map(n=>n.qualified_name).filter(Boolean)).size" in html
    assert "derived_scope:scope||f.transitive_function_count||f.scope||0" in html
    assert "derived_depth:depths.length?Math.max(...depths):f.max_depth||f.depth||0" in html
    assert "const PUBLIC_CALLABLE_TYPES=new Set(['public_function','widget_function'])" in html
    assert "callerPublic=isPublicCallableType(pt)||pt==='public_dependency'" in html
    assert "calleePublic=isPublicCallableType(ct)||ct==='public_dependency'" in html
    assert "if(pt==='widget_function'&&calleePublic)return null" in html
    assert "return 'Type 1'" in html
    assert "return 'Type 2'" in html
    assert "return 'Type 3'" in html
    assert "return 'Type 4'" in html
    assert "return 'Type 5'" in html
    assert "return 'Type 6'" not in html
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

    html = dashboard.render_dashboard(payload)

    assert "loadDashboardBundle('../reference/_data/public-function-call-flows.json', '../reference/_data/generated-artifacts.json')" in html
    assert "public-function-call-flows-json" not in html
    assert "fabricops_public_function_call_flows_v2" not in html
    assert "selected-public-function-panel" in html
    assert "selected-call-tree" in html
    assert "function treeNode(root,node)" in html
    assert "seenEdges.has(edgeKey)" in html
    assert "function markAlreadyShownRows(rows)" in html
    assert "function dashboardTreeRows(flow)" in html
    assert "already shown above" in html
    assert "selectedCallableInventoryTable" in html
    assert "definedButNotUsedTable" in html
    assert "<th>Select</th><th>Function</th><th>File</th>" in html
    assert "<th>Select</th><th>Function</th><th>Reason</th><th>Suggested action</th><th>File</th>" not in html
    assert "functionLink(n)}</td><td>${esc(n.source_path)}</td>" in html
    assert "functionLink(n)}</td><td>${esc(n.reason)}</td><td>${esc(n.suggested_action)}</td><td>${esc(n.source_path)}</td>" not in html
    assert "Download Codex cleanup packet" in html
    assert html.count("Download Codex cleanup packet") == 1
    assert "Download a Codex/GPT-ready cleanup packet with a focused prompt before the evidence." in html
    assert "Downloaded Codex/GPT-ready cleanup packet." in html
    assert "Unused function cleanup" in html
    assert "Orphan function cleanup" not in html
    assert "Total functions" in html
    assert "Unused functions" in html
    assert "Orphan functions" not in html
    assert ">Select all</button>" in html
    assert ">Clear</button>" in html
    assert "Select all visible defined-but-not-used rows" not in html
    assert "Clear selected cleanup rows" not in html
    assert ">Export packet</button>" in html
    assert "Downloaded unused cleanup packet." in html
    assert "Download orphan cleanup packet" not in html
    assert "Export scope" in html
    assert "Full public-function flow" in html
    assert "Current scoped helper flow" in html
    assert "Visible inventory rows only" in html
    assert "Selected inventory rows only" in html
    assert "Cleanup mode" in html
    assert "Breaking cleanup" in html
    assert "Preserve compatibility" in html
    assert "Default:</strong> the packet includes a ready-to-paste prompt for the full public-function flow plus raw evidence." in html
    assert "Export scope controls what goes into the Codex packet, independent of the current inventory filter." in html
    assert "All ${exportedCount} functions in the selected public-function flow will be exported." in html
    assert "Only the ${exportedCount} functions in the current scoped helper branch will be exported." in html
    assert "Only the ${exportedCount} currently visible inventory rows will be exported." in html
    assert "Only the ${exportedCount} manually selected inventory rows will be exported." in html
    assert "functions will be exported" in html
    assert "getFunctionsForExportScope" in html
    assert "buildCleanupPacketFilename" in html
    assert "fabricops-${cleanupModeSlug(cleanupMode)}-cleanup-${String(publicFunctionName||'selected-public-function').replace(/[^A-Za-z0-9_]+/g,'-')}-${exportScopeSlug(exportScope)}-${functionCount}-functions.json" in html
    assert "exported_function_count:exportedFunctionCount" in html
    assert "exported_functions:exportedFunctions.map(packetFields)" in html
    assert "Included by full flow" in html
    assert "Visible in current scope: ${visibleCount} functions" in html
    assert "Included in export flow: ${exportedFunctions.length} functions" in html
    assert "Inventory is currently narrowed to this helper branch." in html
    assert "checkEnabled=exportScope()==='checked_functions_only'" in html
    assert "Export selected packet as YAML" not in html
    assert "Copy AI refactor prompt" not in html
    assert "showWorkflow" in html
    assert "if(e.target.closest('a'))return" in html


def test_dashboard_refactor_packet_wraps_evidence_with_scope_prompts(tmp_path: Path) -> None:
    """Validate all export scopes produce Codex-ready prompt branches."""
    root, pkg, init_path = write_project(tmp_path)
    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    html = dashboard.render_dashboard(payload)

    assert "return {codex_prompt:buildCodexPrompt(evidence),evidence_packet:evidence}" in html
    assert "schema:'fabricops_public_function_call_flow_refactor_packet_v3'" in html
    assert "selected_flow_summary" in html
    assert "deterministic_signal_rules" in html
    assert "architecture_violation_rules" in html
    assert "selected_flow_functions" in html
    assert "selected_inventory_assets" in html
    assert "omitted_inventory_assets" in html
    assert "instructions_for_ai" in html
    assert "Create a focused PR against main" in html
    assert "Selected public callable:" in html
    assert "cleanup_mode: ${mode}" in html
    assert "export_scope: ${scope}" in html
    assert "Expected touched files when available" in html
    assert "call graph JSON" not in html
    assert "Do not regenerate or commit generated docs, dashboard HTML, snapshots, navigation, individual function reference pages, or reference indexes unless explicitly requested" in html
    assert "Exception: when function-level source changes affect callable structure, source locations, public exports, helper relationships, architecture classification, or public function flow metrics" in html
    assert "PYTHONPATH=src python scripts/generate_public_function_call_flows_json.py" in html
    assert "Commit only the regenerated docs/reference/_data/public-function-call-flows.json architecture contract" in html
    assert "Mention any other stale generated docs/dashboard artifacts in the PR summary instead of committing them" in html
    assert "Do not add wrappers, aliases, adapters, resolver layers, or transitional shims" in html
    assert "Preserve public API behavior where practical for this cleanup mode" not in html
    assert "Run targeted tests first" in html
    assert "Acceptance criteria:" in html
    assert "clean the complete selected public callable flow" in html
    assert "clean only the current scoped helper branch" in html
    assert "Scoped/exported functions:" in html
    assert "clean only the currently visible inventory rows" in html
    assert "Visible/exported functions:" in html
    assert "clean only the manually selected inventory rows" in html
    assert "Selected/exported functions:" in html
    assert "Do not clean sibling helper branches unless required" in html
    assert "Do not clean hidden filtered rows or sibling helper branches" in html
    assert "Do not clean sibling functions, downstream helpers, or adjacent violations" in html
    assert "docs/assets/function-call-graph-dashboard.html" not in html

    assert "Backward compatibility applies to the selected public callable boundary" in html
    assert "not to its private or non-exported shared helper chain" in html
    assert "Private and non-exported shared helpers may be renamed, moved, merged, split, inlined, rewritten, deleted, or replaced" in html
    assert "An unchanged signature alone is insufficient" in html
    assert "Verify observable behaviour, accepted inputs, outputs, side effects, persisted contracts, and documented failure behaviour" in html
    assert "For a Live public callable, preserve the supported public contract" in html
    assert "Preview callables are not covered by Live backward-compatibility guarantees" in html
    assert "Discontinued callables do not imply current support" in html
    assert "identify each changed public contract clearly in the PR summary" in html
    assert "Internal helper changes alone are not public breaking changes" in html
    assert "Public compatibility is evaluated at the selected callable boundary" in html
    assert "Internal helper structure may change completely" in html
    assert "Preserve mode verifies inputs, outputs, side effects, persisted contracts, and errors, not only the signature" in html
    assert "Breaking mode identifies every intentionally changed public contract" in html
    assert "Obsolete wrappers, aliases, adapters, and shims are removed unless explicitly required" in html
    assert "supports_live_contract:!!n.supports_live_contract" in html
    assert "live_impact_level:n.live_impact_level" in html



def test_agents_backward_compatibility_policy_is_public_contract_scoped() -> None:
    """Verify repository compatibility guidance distinguishes public contracts from helper structure."""
    text = Path("AGENTS.md").read_text(encoding="utf-8")

    assert "## Backward compatibility and public contracts" in text
    assert "Backward compatibility applies to supported public callables" in text
    assert "It does not require preserving private or shared" in text
    assert "implementation structure" in text
    assert "The internal implementation may be replaced completely" in text
    assert "renamed, moved, merged, split, inlined" in text
    assert "Do not preserve obsolete internal wrappers, aliases, adapters, resolver layers" in text
    assert "An unchanged function signature alone does not prove backward compatibility" in text
    assert "observable behaviour, accepted inputs, return contracts, side effects" in text
    assert "persisted outputs, and failure behaviour" in text
    assert "Preview callables are not covered by Live backward-compatibility guarantees" in text
    assert "Discontinued callables do not imply current support" in text
    assert "Clearly identify every changed" in text
    assert "public contract in the PR summary" in text

def test_dashboard_can_embed_json_for_debug_mode(tmp_path: Path) -> None:
    """Validate optional standalone/debug mode can still embed JSON."""
    root, pkg, init_path = write_project(tmp_path)
    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)

    html = dashboard.render_dashboard(payload, embed_json=True)

    assert "public-function-call-flows-json" in html
    assert "fabricops_public_function_call_flows_v2" in html


def test_dashboard_lifecycle_and_live_contract_controls_render() -> None:
    """Verify dashboard exposes lifecycle filtering and Live-contract presentation."""
    html = dashboard.render_dashboard()

    assert 'id="lifecycleFilter"' in html
    assert '<option value="" selected>All</option>' in html
    assert '<option value="live">Live</option>' in html
    assert '<option value="preview">Preview</option>' in html
    assert '<option value="discontinued">Discontinued</option>' in html
    assert "lifecycleValue(f)==='live'" in html
    assert "s==='preview'" in html
    assert "s==='discontinued'" in html
    assert "Live since ${f.live_since}" in html
    assert "Discontinued in ${f.discontinued_in}" in html
    assert "humanizeValue(f.contract_classification)" in html
    assert "humanizeValue(f.contract_risk)" in html
    assert "helperDependencyLabel(f)" in html
    assert "Helpers supporting this Live function" in html
    assert "Helpers in this function flow" in html
    assert "Helpers in this historical flow" in html
    assert "live_critical_dependency_count" in html
    assert "This function is part of the supported FabricOps public contract" in html
    assert "This function is available for evaluation" in html
    assert "This function is no longer part of the current supported public contract" in html
    assert "Lifecycle data missing for public function" in html


def test_dashboard_live_critical_internal_helpers_and_exports_render() -> None:
    """Verify dashboard surfaces Live-impact helper details without relabelling helpers as public."""
    html = dashboard.render_dashboard()

    assert "Supports Live function" in html
    assert "Supports Live contract" not in html
    assert "Direct Live dependency" not in html
    assert "Transitive Live dependency" not in html
    assert "Preview-only internal" not in html
    assert '<span class="badge muted">Internal</span>' not in html
    assert "Highlight helpers supporting Live functions" in html
    assert "highlightLiveCriticalOnly" in html
    assert "direct_live_dependent_count" in html
    assert "transitive_live_dependent_count" in html
    assert "direct_live_dependents" in html
    assert "transitive_live_dependents" in html
    assert "lifecycle_status:f.lifecycle_status" in html
    assert "contract_classification:f.contract_classification" in html
    assert "contract_risk:f.contract_risk" in html
    assert "live_critical_dependency_count:f.live_critical_dependency_count" in html
    assert "live_impact_level:n.live_impact_level" in html
    assert "supports_live_contract:!!n.supports_live_contract" in html
    assert "Used by Live public functions: ${unique.join(', ')}" in html
    assert ".map(dependentFunctionName).filter(Boolean).sort()" in html
    assert "direct_live_dependents:n.direct_live_dependents||[]" in html
    assert "transitive_live_dependents:n.transitive_live_dependents||[]" in html
    assert "Architecture violations exist in this flow. Internal helper changes may affect the supported Live contract." in html
    assert "Architecture violations exist in this Preview flow. Review helper boundaries before further development or promotion to Live." in html
    assert "Architecture violations exist in this historical flow." in html
    assert "Public root" in html

def test_json_generator_writes_only_json(tmp_path: Path) -> None:
    """Validate the JSON writer does not create dashboard HTML."""
    root, pkg, init_path = write_project(tmp_path)
    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)
    data_path = tmp_path / "docs" / "reference" / "_data" / "public-function-call-flows.json"
    dashboard_path = tmp_path / "docs" / "assets" / "public-function-call-flows-dashboard.html"

    flows.write_json(payload, data_path=data_path)

    assert data_path.exists()
    assert not dashboard_path.exists()


def test_dashboard_generator_writes_only_dashboard_html(tmp_path: Path) -> None:
    """Validate the dashboard writer does not write JSON."""
    data_path = tmp_path / "docs" / "reference" / "_data" / "public-function-call-flows.json"
    dashboard_path = tmp_path / "docs" / "assets" / "public-function-call-flows-dashboard.html"

    dashboard.write_dashboard(dashboard_path=dashboard_path)

    assert dashboard_path.exists()
    assert not data_path.exists()
    assert "loadDashboardBundle('../reference/_data/public-function-call-flows.json', '../reference/_data/generated-artifacts.json')" in dashboard_path.read_text(encoding="utf-8")


def test_dashboard_generator_does_not_scan_source() -> None:
    """Validate dashboard generation has no source-scanning dependency."""
    assert not hasattr(dashboard, "discover_modules")
    assert not hasattr(dashboard, "build_payload")
    assert "loadDashboardBundle('../reference/_data/public-function-call-flows.json', '../reference/_data/generated-artifacts.json')" in dashboard.render_dashboard()


def test_generated_json_includes_source_traceability_fields(tmp_path: Path) -> None:
    """Validate source traceability fields are present in public and flow records."""
    root, pkg, init_path = write_project(tmp_path)
    payload = flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path)
    public_a = next(item for item in payload["public_functions"] if item["function_name"] == "public_a")
    flow_row = public_a["flow"][0]
    required_public_fields = {
        "function_name", "qualified_name", "source_path", "source_start_line", "source_end_line",
        "width", "scope", "depth", "files_touched", "refactor_signals",
    }
    required_flow_fields = {
        "function_name", "qualified_name", "source_path", "source_start_line", "source_end_line",
        "function_type", "parent_qualified_name", "architecture_violations", "violation_types",
        "violation_details",
    }

    assert required_public_fields <= public_a.keys()
    assert required_flow_fields <= flow_row.keys()


def test_json_output_is_deterministic_across_consecutive_writes(tmp_path: Path) -> None:
    """Validate JSON output is byte-stable across consecutive generator writes."""
    root, pkg, init_path = write_project(tmp_path)
    data_path = tmp_path / "public-function-call-flows.json"

    flows.write_json(flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path), data_path=data_path)
    first = data_path.read_text(encoding="utf-8")
    flows.write_json(flows.build_payload(root=root, pkg_dir=pkg, init_path=init_path), data_path=data_path)
    second = data_path.read_text(encoding="utf-8")

    assert first == second


def test_committed_json_matches_generator_output() -> None:
    """Validate committed call-flow JSON matches the generator payload."""
    expected = json.dumps(flows.build_payload(), indent=2, sort_keys=True) + "\n"
    actual = flows.DATA_PATH.read_text(encoding="utf-8")

    assert actual == expected
    assert "schema v1" not in actual.lower()


def test_callable_flow_docs_page_uses_deterministic_signal_rules() -> None:
    """Validate callable flow docs describe the deterministic V2 signal model."""
    docs = Path("docs/function-call-graph.md").read_text(encoding="utf-8")

    assert "#### Public-flow signals" in docs
    assert "Large width/depth | Width > 10 or Depth > 5" in docs
    assert "Architecture violation | Any Type 1 to Type 5 violation" in docs
    assert "#### Architecture violation types" in docs
    for violation_type in ["Type 1", "Type 2", "Type 3", "Type 4", "Type 5"]:
        assert violation_type in docs
    assert "Type 6" not in docs
    assert "Private implementation helpers may call shared reusable functions directly." in docs
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


def test_generated_artifact_metadata_preserves_entries_and_formats_sgt(tmp_path: Path) -> None:
    """Validate generated artifact metadata writes one key without deleting peers."""
    from datetime import UTC, datetime

    from scripts.generated_artifact_metadata import format_sgt_timestamp, update_generated_artifact_metadata

    metadata_path = tmp_path / "generated-artifacts.json"
    update_generated_artifact_metadata(
        "first",
        "First artifact",
        "scripts/first.py",
        "docs/first.json",
        metadata_path=metadata_path,
    )
    payload = update_generated_artifact_metadata(
        "second",
        "Second artifact",
        "scripts/second.py",
        "docs/second.json",
        metadata_path=metadata_path,
    )

    assert set(payload["artifacts"]) == {"first", "second"}
    assert payload["artifacts"]["first"]["label"] == "First artifact"
    assert format_sgt_timestamp(datetime(2026, 7, 6, 7, 26, tzinfo=UTC)) == "06 Jul 2026, 3:26 PM SGT"
    assert payload["artifacts"]["second"]["generated_at_sgt"].endswith(" SGT")


def test_generated_artifact_metadata_updates_existing_timestamp_in_normal_mode(tmp_path: Path) -> None:
    """Validate normal metadata mode refreshes the artifact timestamp."""
    from scripts.generated_artifact_metadata import update_generated_artifact_metadata

    metadata_path = tmp_path / "generated-artifacts.json"
    first = update_generated_artifact_metadata(
        "artifact",
        "Artifact",
        "scripts/generator.py",
        "docs/artifact.json",
        metadata_path=metadata_path,
    )
    first_timestamp = first["artifacts"]["artifact"]["generated_at_utc"]
    time.sleep(0.001)

    second = update_generated_artifact_metadata(
        "artifact",
        "Artifact",
        "scripts/generator.py",
        "docs/artifact.json",
        metadata_path=metadata_path,
    )

    assert second["artifacts"]["artifact"]["generated_at_utc"] != first_timestamp


def test_generated_artifact_metadata_preserve_mode_keeps_same_key_timestamp(tmp_path: Path, monkeypatch) -> None:
    """Validate preserve mode keeps existing timestamps for the updated artifact key."""
    from scripts.generated_artifact_metadata import PRESERVE_TIMESTAMPS_ENV, update_generated_artifact_metadata

    metadata_path = tmp_path / "generated-artifacts.json"
    first = update_generated_artifact_metadata(
        "artifact",
        "Artifact",
        "scripts/generator.py",
        "docs/artifact.json",
        metadata_path=metadata_path,
    )
    first_artifact = dict(first["artifacts"]["artifact"])
    monkeypatch.setenv(PRESERVE_TIMESTAMPS_ENV, "1")
    time.sleep(0.001)

    second = update_generated_artifact_metadata(
        "artifact",
        "Renamed artifact",
        "scripts/generator.py",
        "docs/artifact.json",
        metadata_path=metadata_path,
    )

    assert second["artifacts"]["artifact"]["generated_at_utc"] == first_artifact["generated_at_utc"]
    assert second["artifacts"]["artifact"]["generated_at_sgt"] == first_artifact["generated_at_sgt"]
    assert second["artifacts"]["artifact"]["label"] == "Renamed artifact"


def test_generated_artifact_metadata_preserve_mode_preserves_other_entries(tmp_path: Path, monkeypatch) -> None:
    """Validate preserve mode keeps unrelated artifact entries intact."""
    from scripts.generated_artifact_metadata import PRESERVE_TIMESTAMPS_ENV, update_generated_artifact_metadata

    metadata_path = tmp_path / "generated-artifacts.json"
    payload = update_generated_artifact_metadata("first", "First", "scripts/first.py", "docs/first.json", metadata_path=metadata_path)
    first_artifact = dict(payload["artifacts"]["first"])
    monkeypatch.setenv(PRESERVE_TIMESTAMPS_ENV, "1")

    updated = update_generated_artifact_metadata("second", "Second", "scripts/second.py", "docs/second.json", metadata_path=metadata_path)

    assert updated["artifacts"]["first"] == first_artifact
    assert set(updated["artifacts"]) == {"first", "second"}


def test_generated_artifact_metadata_preserve_mode_is_deterministic(tmp_path: Path, monkeypatch) -> None:
    """Validate CI preserve mode leaves metadata output stable for existing keys."""
    from scripts.generated_artifact_metadata import PRESERVE_TIMESTAMPS_ENV, update_generated_artifact_metadata

    metadata_path = tmp_path / "generated-artifacts.json"
    update_generated_artifact_metadata("artifact", "Artifact", "scripts/generator.py", "docs/artifact.json", metadata_path=metadata_path)
    monkeypatch.setenv(PRESERVE_TIMESTAMPS_ENV, "1")

    update_generated_artifact_metadata("artifact", "Artifact", "scripts/generator.py", "docs/artifact.json", metadata_path=metadata_path)
    first = metadata_path.read_text(encoding="utf-8")
    time.sleep(0.001)
    update_generated_artifact_metadata("artifact", "Artifact", "scripts/generator.py", "docs/artifact.json", metadata_path=metadata_path)
    second = metadata_path.read_text(encoding="utf-8")

    assert second == first


def test_public_call_flow_write_drops_stale_timestamps(tmp_path: Path) -> None:
    """Confirm call-flow JSON no longer preserves stale inline generated timestamps."""
    data_path = tmp_path / "public-function-call-flows.json"
    data_path.write_text(
        '{"metadata":{"generated_at_utc":"old","generated_at_sgt":"01 Jan 2000, 1:00 AM SGT"}}',
        encoding="utf-8",
    )
    payload = {"metadata": {"schema": "fabricops_public_function_call_flows_v2"}, "public_functions": []}

    flows.write_json(payload, data_path=data_path)

    written = data_path.read_text(encoding="utf-8")
    assert "generated_at_utc" not in written
    assert "generated_at_sgt" not in written


def test_dashboard_uses_shared_generated_artifact_metadata() -> None:
    """Ensure dashboard freshness does not depend on call-flow JSON metadata timestamps."""
    html = dashboard.render_dashboard()

    assert "generated-artifacts.json" in html
    assert "Call-flow data generated:" in html
    assert "Dashboard generated:" in html
    assert "DATA.metadata||{}).generated_at_sgt" not in html
