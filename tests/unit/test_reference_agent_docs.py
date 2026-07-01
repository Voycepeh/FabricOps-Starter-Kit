"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import ast
import html
import json
import subprocess
import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
REFERENCE_DIR = ROOT / "docs" / "reference"
REFERENCE_INDEX = REFERENCE_DIR / "index.md"
API_REFERENCE_DIR = ROOT / "docs" / "api" / "reference"
PLACEHOLDER = "Not documented yet"

CONFIG_MODEL_SYMBOLS = {
    "FabricStore",
    "PathConfig",
    "GovernanceConfig",
    "DataAgreementConfig",
    "FrameworkConfig",
    "ConfigSmokeCheckResult",
    "NotebookSetupContext",
}

CORE_CALLABLES = {
    "setup_notebook",
    "setup_metadata_tables",
    "read_lakehouse_table",
    "write_lakehouse_table",
    "profile_dataframe",
}
CORE_PAGE_SECTIONS = (
    "Signature",
    "Example usage",
)
CORE_AGENT_FIELDS = (
    "use_when",
    "do_not_use_when",
    "required_context",
    "inputs",
    "output",
    "side_effects",
    "verification",
)


def _section_text(page_text: str, section: str) -> str:
    marker = f"## {section}\n"
    assert marker in page_text
    after = page_text.split(marker, 1)[1]
    section = after.split("\n## ", 1)[0]
    section = section.split('\n<details class="reference-metadata-details">', 1)[0]
    return section.strip()


def _subsection_text(page_text: str, subsection: str) -> str:
    marker = f"### {subsection}\n"
    assert marker in page_text
    after = page_text.split(marker, 1)[1]
    return after.split("\n### ", 1)[0].strip()


def _normalize_whitespace(value: str) -> str:
    """Return text with formatter-introduced whitespace collapsed."""
    return " ".join(value.split())


def _remove_whitespace(value: str) -> str:
    """Return text with whitespace removed for formatted HTML/JS assertions."""
    return re.sub(r"\s+", "", value)


def _exported_symbols() -> list[str]:
    """Return exported public symbol names from the package root."""
    init_path = ROOT / "src" / "fabricops_kit" / "__init__.py"
    tree = ast.parse(init_path.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
        ):
            return [
                elt.value for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)
            ]
    raise AssertionError("Could not parse __all__")


def _landing_token_text(page_text: str, token_name: str) -> str:
    """Return generated landing page text wrapped by a count token."""
    start = f"<!-- {token_name} -->"
    end = f"<!-- /{token_name} -->"
    assert start in page_text
    assert end in page_text
    token_html = page_text.split(start, 1)[1].split(end, 1)[0]
    return html.unescape(re.sub(r"<[^>]+>", " ", token_html)).split()


def test_landing_page_counts_match_generated_stats() -> None:
    """Verify landing-page count text cannot drift from generated data."""
    stats = json.loads((REFERENCE_DIR / "_data" / "landing-stats.json").read_text(encoding="utf-8"))
    index_text = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")

    assert "<!-- FABRICOPS_PUBLIC_FUNCTION_COUNT --><strong>" in index_text
    assert "</strong><span> public callable functions</span><!-- /FABRICOPS_PUBLIC_FUNCTION_COUNT -->" in index_text
    assert "FABRICOPS_CALLABLE_RECORD_COUNT" in index_text
    assert "Function metrics are generated from the runtime inventory data." in index_text
    assert "283 supporting internal functions" not in index_text
    assert "supporting internal functions" not in index_text

    expected = {
        "FABRICOPS_PUBLIC_FUNCTION_COUNT": f"{stats['public_function_count']} public callable functions",
        "FABRICOPS_CALLABLE_RECORD_COUNT": (
            "Each public callable is documented as a standalone function, with supporting "
            "private functions, classes, and internal methods kept behind the scenes"
        ),
        "FABRICOPS_METADATA_TABLE_COUNT": f"{stats['metadata_table_count']} metadata tables",
    }

    for token_name, expected_text in expected.items():
        assert " ".join(_landing_token_text(index_text, token_name)) == expected_text


def test_landing_stats_match_reference_sources() -> None:
    """Verify generated landing stats are derived from canonical reference sources."""
    stats = json.loads((REFERENCE_DIR / "_data" / "landing-stats.json").read_text(encoding="utf-8"))
    callable_flow = json.loads((REFERENCE_DIR / "_data" / "function-call-graph.json").read_text(encoding="utf-8"))
    metadata_pages = sorted((REFERENCE_DIR / "metadata").glob("*.md"))

    summary_counts = callable_flow["summary_counts"]
    assert stats["public_function_count"] == summary_counts["public_api_surface"]["public_api_entrypoints"]
    assert stats["total_callable_records"] == summary_counts["total_callables"]
    metrics = summary_counts["callable_inventory_metrics"]
    assert stats["function_callable_count"] == summary_counts["callable_kind"]["function"]
    assert stats["supporting_function_count"] == metrics["supporting_functions"]
    assert stats["metadata_table_count"] == len(metadata_pages)


def test_generated_callable_surface_matches_all_exports() -> None:
    """Verify generated callable entries come from package __all__."""
    exported_symbols = set(_exported_symbols())
    config_model_symbols = {
        "FabricStore",
        "PathConfig",
        "GovernanceConfig",
        "DataAgreementConfig",
        "FrameworkConfig",
        "ConfigSmokeCheckResult",
        "NotebookSetupContext",
    }
    function_exported_symbols = exported_symbols - config_model_symbols
    removed_symbols = {
        "enforce_dq_rules",
        "get_selected_agreement",
    }
    automation_manifest = json.loads((REFERENCE_DIR / "_data" / "automation-manifest.json").read_text(encoding="utf-8"))
    function_manifest = json.loads((REFERENCE_DIR / "_data" / "function-manifest.json").read_text(encoding="utf-8"))
    callable_flow = json.loads((REFERENCE_DIR / "_data" / "function-call-graph.json").read_text(encoding="utf-8"))

    automation_callables = {entry["name"] for entry in automation_manifest if entry.get("type") == "callable"}
    function_callables = {
        entry["name"]
        for entry in function_manifest
        if entry.get("classification") == "Callable" and entry.get("docs_path", "").startswith("api/reference/")
    }
    page_callables = {path.stem for path in API_REFERENCE_DIR.glob("*.md")}

    assert automation_callables == exported_symbols
    class_callables = {
        entry["name"]
        for entry in function_manifest
        if entry.get("classification") == "Public class" and entry.get("docs_path", "").startswith("api/reference/")
    }

    assert function_callables == function_exported_symbols
    assert class_callables == config_model_symbols
    assert page_callables == exported_symbols
    public_inventory = {row["function_name"] for row in callable_flow["function_inventory"] if row["layer"] == "public"}
    assert public_inventory == function_exported_symbols
    assert not (removed_symbols & automation_callables)
    assert not (removed_symbols & function_callables)
    assert not (removed_symbols & page_callables)
    assert not (removed_symbols & public_inventory)


def test_public_config_classes_have_reference_taxonomy() -> None:
    """Verify public config classes are searchable and separate from public functions."""
    class_names = CONFIG_MODEL_SYMBOLS
    reference_index = REFERENCE_INDEX.read_text(encoding="utf-8")
    inventory_text = (ROOT / "docs" / "assets" / "function-call-graph-dashboard.html").read_text(encoding="utf-8")
    flow_data = json.loads((REFERENCE_DIR / "_data" / "function-call-graph.json").read_text(encoding="utf-8"))
    landing_stats = json.loads((REFERENCE_DIR / "_data" / "landing-stats.json").read_text(encoding="utf-8"))
    class_rows = {row["function_name"]: row for row in flow_data["function_inventory"] if row["layer"] == "class"}
    flow_names = {row["function_name"] for row in flow_data["public_entrypoint_flow"]}

    assert "search 25 public functions and 7 public classes" in reference_index
    assert '<option value="class">Classes</option>' not in inventory_text
    assert "Classes" in inventory_text
    assert set(class_rows) == class_names
    assert flow_data["summary_counts"]["public_api_surface"]["public_api_entrypoints"] == 25
    assert flow_data["summary_counts"]["public_classes"] == 7
    assert landing_stats["public_class_count"] == 7
    assert landing_stats["public_root_export_count"] == 32
    assert len(flow_data["public_entrypoint_flow"]) == 25
    assert not (class_names & flow_names)

    for name in class_names:
        page = API_REFERENCE_DIR / f"{name}.md"
        assert page.exists(), name
        page_text = page.read_text(encoding="utf-8")
        assert "Public config class" in page_text
        assert "Public Starter Kit function" not in page_text
        assert f'data-callable-name="{name}"' in reference_index
        assert 'data-function-type="public-class"' in reference_index
        assert class_rows[name]["function_type"] == "Public config class"
        assert class_rows[name]["callable_kind"] == "class"

def test_refactor_signals_do_not_treat_cross_module_helpers_as_wrong_area() -> None:
    """Verify cross-module helper usage is not itself a wrong-area refactor signal."""
    from scripts.generate_function_reference import _collect_refactor_signals, _render_refactor_signals

    root_qn = "fabricops_kit.pipeline.public_api"
    calls_by_qn = {
        root_qn: [
            "fabricops_kit.pipeline._load_metadata_rules",
            "fabricops_kit.metadata._load_metadata_table",
        ],
    }
    node_by_qn = {
        root_qn: {"callable_name": "public_api", "module_name": "pipeline", "exported": True},
        "fabricops_kit.pipeline._load_metadata_rules": {
            "callable_name": "_load_metadata_rules",
            "module_name": "pipeline",
            "exported": False,
        },
        "fabricops_kit.metadata._load_metadata_table": {
            "callable_name": "_load_metadata_table",
            "module_name": "metadata",
            "exported": False,
        },
    }
    module_data = {
        "pipeline": {"functions": {"_load_metadata_rules": "Load metadata rules for the callable."}},
        "metadata": {"functions": {"_load_metadata_table": "Load metadata table rows."}},
    }

    signal_data = _collect_refactor_signals(root_qn, calls_by_qn, node_by_qn, module_data)
    signals = "\n".join(_render_refactor_signals(signal_data, node_by_qn))

    assert "contains helpers from multiple modules" not in signals
    assert "- None detected from helper names, doc summaries, and module placement." in signals
    assert signal_data["possible_grouping_mismatches"] == []


def test_helper_area_mismatch_signal_requires_three_way_mismatch() -> None:
    """Verify wrong-area signals require name, summary, and grouping mismatch."""
    from scripts.generate_function_reference import _helper_area_mismatch_signal

    two_way_signal = _helper_area_mismatch_signal(
        "_metadata_check",
        "Validate required inputs before the workflow continues.",
        "Metadata loading",
    )
    three_way_signal = _helper_area_mismatch_signal(
        "_validate_inputs",
        "Evaluate configured rules for the callable.",
        "Metadata loading",
    )

    assert two_way_signal is None
    assert three_way_signal == ("Metadata loading", "Validation", "Rule evaluation")


def test_reference_agent_metadata_files_exist_and_are_valid_json() -> None:
    """Verify reference agent/automation metadata files exist and are valid json."""
    automation_manifest = REFERENCE_DIR / "_data" / "automation-manifest.json"
    function_manifest = REFERENCE_DIR / "_data" / "function-manifest.json"
    refactor_signals = REFERENCE_DIR / "_data" / "refactor-signals.json"
    callable_flow = REFERENCE_DIR / "_data" / "function-call-graph.json"

    assert automation_manifest.exists()
    assert function_manifest.exists()
    assert refactor_signals.exists()
    assert callable_flow.exists()
    assert json.loads(automation_manifest.read_text(encoding="utf-8"))
    assert json.loads(function_manifest.read_text(encoding="utf-8"))
    assert json.loads(refactor_signals.read_text(encoding="utf-8"))
    assert json.loads(callable_flow.read_text(encoding="utf-8"))


def test_callable_flow_page_and_json_cover_public_surface() -> None:
    """Verify callable flow docs, dashboards, and data contracts are generated."""
    flow_page = REFERENCE_DIR / "function-call-graph.md"
    flow_data_path = REFERENCE_DIR / "_data" / "function-call-graph.json"
    dashboard_path = ROOT / "docs" / "assets" / "function-call-graph-dashboard.html"
    inventory_path = ROOT / "docs" / "assets" / "function-inventory.html"
    exported_symbols = set(_exported_symbols())
    config_model_symbols = {
        "FabricStore",
        "PathConfig",
        "GovernanceConfig",
        "DataAgreementConfig",
        "FrameworkConfig",
        "ConfigSmokeCheckResult",
        "NotebookSetupContext",
    }
    function_exported_symbols = exported_symbols - config_model_symbols

    assert flow_page.exists()
    assert dashboard_path.exists()
    assert not inventory_path.exists()

    flow_text = flow_page.read_text(encoding="utf-8")
    assert "# Function Call Graph" in flow_text
    assert "> **First make it exist. Then make it good.**" in flow_text
    assert "## How it works" in flow_text
    assert "## 1. Repository code" in flow_text
    assert "## 2. Scan and analyze" in flow_text
    assert "## 3. Enforce architecture" in flow_text
    assert "### What the dashboard signals" in flow_text
    assert "### Too many helpers" in flow_text
    assert "### Too many steps" in flow_text
    assert "## 4. Function Call Graph Dashboard" in flow_text
    assert "## 5. AI refactor packets" in flow_text
    assert "## Preferred callable file pattern" not in flow_text
    assert not (ROOT / "docs" / "reference" / "callable-architecture.md").exists()

    expected_flow_images = [
        "../assets/fabricops-call-graph-setup.png",
        "../assets/fabricops-bad-example-large-surface-area.png",
        "../assets/fabricops-bad-example-nested-functions.png",
        "../assets/fabricops-call-graph-dashboard.png",
        "../assets/fabricops-call-graph-ai-refactor-package.png",
        "../assets/fabricops-call-graph-ai-refactor-package%282%29.png",
    ]
    for expected_image in expected_flow_images:
        assert expected_image in flow_text

    expected_flow_phrases = [
        "Repository Code → Scan & Analyze → Enforce Architecture → Dashboard → AI Refactor Packets",
        "What the dashboard signals",
        "Broken rule | An architecture rule is broken",
        "Shared helper | The helper is used by more than one public function",
        "Maintainability signal | The code may still be valid",
        "Open architecture dashboard",
    ]
    for expected_phrase in expected_flow_phrases:
        assert expected_phrase in flow_text

    assert "fabricops-bad-example-pointless-wrapper-functions.png" not in flow_text
    assert "fabricops-bad-example-function-dependancy.png" not in flow_text
    assert "fabricops-select-refactor-candidates.png" not in flow_text
    assert "fabricops-select-refactor-candidates-prompt-export.png" not in flow_text
    assert "[Function Call Graph Dashboard](../assets/function-call-graph-dashboard.html)" in flow_text
    assert "[Function Call Graph Dashboard runtime inventory](../assets/function-call-graph-dashboard.html#runtime-inventory)" in flow_text
    assert "[function-call-graph.json](_data/function-call-graph.json)" in flow_text
    assert "fabricops_runtime_refactor_packet" in flow_text
    assert "selected architecture scope" in flow_text
    assert "## Callable helper summary" not in flow_text
    assert "## Implementation helper nesting inventory" not in flow_text
    assert '<div class="callable-flow-table-wrap" markdown="0">' not in flow_text
    assert "refactor reason" not in flow_text.lower()
    for stale_flow_phrase in [
        "Decision mode",
        "quick filter",
        "Architecture inventory",
        "callable refactor packet",
        "Exporting an AI refactor prompt",
    ]:
        assert stale_flow_phrase not in flow_text

    dashboard_text = dashboard_path.read_text(encoding="utf-8")
    compact_dashboard_text = "".join(dashboard_text.split())
    compact_dashboard_text = compact_dashboard_text.replace('"', "'")
    normalized_dashboard_text = _normalize_whitespace(dashboard_text)
    inventory_text = dashboard_text
    compact_inventory_text = "".join(inventory_text.split())
    compact_inventory_text = compact_inventory_text.replace('"', "'")
    normalized_inventory_text = _normalize_whitespace(inventory_text)
    combined_dashboard_assets = dashboard_text + inventory_text
    assert "function-inventory.html" not in combined_dashboard_assets
    assert "Remove orphaned asset" not in combined_dashboard_assets
    assert "Unreachable runtime asset" not in dashboard_text
    assert "No static path found" not in dashboard_text
    assert "safe to delete" not in combined_dashboard_assets
    assert "The scanner could not trace this asset back to a public FabricOps function. This is not proof that the asset is unused or safe to " in combined_dashboard_assets
    assert "safe to '+'delete" in combined_dashboard_assets
    assert "runtime-inventory" in dashboard_text
    assert "Clear search" in dashboard_text
    assert "Clear table filters" not in dashboard_text
    assert "Clear all filters" not in dashboard_text
    assert "Show all runtime assets" in dashboard_text
    assert "Current scope:" in dashboard_text
    assert "scopeBannerName" in dashboard_text
    assert "scopeBannerHelp" in dashboard_text
    assert "function scopeHelpText()" in dashboard_text
    assert "function renderScopeBanner()" in dashboard_text
    assert "renderScopeBanner();const scoped=inventory.filter(rowInSelectedScope)" in dashboard_text
    assert "function scrollToRuntimeInventory()" in dashboard_text
    assert "document.getElementById('runtime-inventory')" in dashboard_text
    assert "scrollIntoView({behavior:'smooth',block:'start'})" in dashboard_text
    assert "function setArchitectureScope(scope,options={})" in dashboard_text
    assert "if(options.scroll!==false)scrollToRuntimeInventory()" in dashboard_text
    assert "currentScope.kind==='public_callable'&&i.qualified_name===currentScope.qualified_name?'scope-highlight':''" in dashboard_text
    assert "rowReachability(r)==='unreachable_runtime_asset'" in dashboard_text
    assert "showAllRuntimeAssets" in dashboard_text
    assert "$('showAllRuntimeAssets').onclick=()=>setArchitectureScope({kind:'all',label:'All runtime assets',qualified_name:''})" in dashboard_text
    assert "state.search=''" in dashboard_text
    assert "Object.assign(state,{search:'',typeFilter:'all',reachabilityFilter:'all',healthFilter:'all',actionFilter:'all'})" not in dashboard_text
    assert "$('focusFilter').value='all'" not in dashboard_text
    assert dashboard_text.count('<section class="export-toolbar" aria-label="Advanced cleanup and export actions" hidden>') == 0
    assert dashboard_text.count('<section class="export-toolbar"') == 1
    assert dashboard_text.count('<section class="export-toolbar">') == 1
    assert dashboard_text.index('id="runtime-inventory"') < dashboard_text.index('<section class="export-toolbar">')

    for text in (dashboard_text, inventory_text):
        assert "function-call-graph.json" in text
        assert "Download JSON" in text
        assert "Download YAML" in text
        assert "Copy JSON" not in text
        assert "Copy YAML" not in text
        assert "function yamlPacket(packet)" in text
        assert "function markdownPacket(packet)" not in text
        assert "compatibilityMode" in text
        assert "Preserve backwards compatibility" in text
        assert "Allow breaking changes" in text
        assert "ai_prompt" in text.replace(" ", "") or "ai_prompt" in text

    assert "openFunctionCallGraphJson" in dashboard_text
    assert "data-public-flow" in dashboard_text
    assert "publicCallableList" in dashboard_text
    assert "publicFlowDetails" in dashboard_text
    assert "Selected public function flow" in dashboard_text
    assert dashboard_text.index("Selected public function flow") < dashboard_text.index("Selected scope runtime inventory")
    assert "publicSearchHaystack" in dashboard_text
    assert "read_lakehouse" in (ROOT / "docs" / "reference" / "_data" / "function-call-graph.json").read_text(encoding="utf-8")
    assert "publicEntryFlows=(Array.isArray(data.public_flows)&&data.public_flows.length?data.public_flows:" in dashboard_text
    assert "derivePublicFlowsFromInventory(inventory)" in dashboard_text
    assert "Public flow details were not found, so this table is using public callable inventory rows." in dashboard_text
    assert "Detailed call flow was not available for this public function." in dashboard_text
    assert "renderPublicCallableList()" in dashboard_text
    assert "renderFlowDetails()" in dashboard_text
    assert "Loading function call graph data..." in dashboard_text
    assert "renderLoadStatus(`Loaded ${inventory.length} total functions; ${publicEntryFlows.length} public functions available; ${visibleFlows.length} rows after filters.${warning}`)" in dashboard_text
    assert "Runtime inventory" in dashboard_text
    assert "Cannot trace back to a public function" in dashboard_text
    assert "Unreachable runtime asset" not in dashboard_text
    assert "No static path found" not in dashboard_text
    assert "downloadPacket" in dashboard_text
    assert "functionbuildCleanupPacketFilename(selectedFunctionName,extension)" in compact_dashboard_text
    assert "cleanupPacketTimestamp" in dashboard_text
    assert "selectedFlowName()" in dashboard_text
    assert "replace(/[^A-Za-z0-9_.-]/g" in compact_dashboard_text
    assert "fabricops-function-call-graph-cleanup-packet__${safeName}__" in dashboard_text
    assert "fabricops-function-call-graph-cleanup-packet.${isYaml" not in dashboard_text
    assert "fabricops_public_callable_flow_cleanup_packet" in dashboard_text
    assert "selectedFlow" in dashboard_text
    assert "compat-mode-safe" in dashboard_text
    assert "compat-mode-breaking" in dashboard_text
    assert "architecture_violation_count" in dashboard_text
    assert "architecture_findings" in dashboard_text
    assert "flow_tree" in dashboard_text
    assert "review_for_merge_helpers" in dashboard_text
    assert "public_callable_findings" in dashboard_text
    assert "review_for_merge_count" in dashboard_text
    assert "requested_work" in dashboard_text
    assert "safety_constraints" in dashboard_text
    assert "function publicCallableFindingRows(flow)" in dashboard_text
    assert "flow-summary-card" in dashboard_text
    assert "flow-key-signals" in dashboard_text
    assert "flow-next-step" in dashboard_text
    assert "functionflowHealth(flow,architectureFindings,mergeCandidates)" in compact_dashboard_text
    assert "functionflowReason(flow,architectureFindings,mergeCandidates)" in compact_dashboard_text
    assert "functionflowNextStepLabel(flow,architectureFindings=[],mergeCandidates=[]" in compact_dashboard_text
    assert "functionflowNextStep(flow,architectureFindings,mergeCandidates)" in compact_dashboard_text
    assert "returnlabel" in compact_dashboard_text
    assert "functionflowSignalChips(flow,architectureFindings,mergeCandidates)" in compact_dashboard_text
    assert "Public callable findings</h3>" not in dashboard_text
    assert "Architecture findings inside this flow" not in dashboard_text
    assert "Implementation helper cleanup candidates</h3>" not in dashboard_text
    assert "helper_tags" in dashboard_text
    assert "Inspect the selected public function and its function call graph." in dashboard_text
    assert "Resolve true cross-file private dependency violations first." in dashboard_text
    assert "For same-file private dependencies, treat as warning only." in dashboard_text
    assert "Merge or inline helpers only when readability improves." in dashboard_text
    assert "Preserve notebook-facing behavior." in dashboard_text
    assert "Return summary, changed functions, tests, risks, and skipped items." in dashboard_text
    assert "Do not casually change public function signatures." in dashboard_text
    assert "source_url:row.source_url||null" in compact_dashboard_text
    assert "docs_url:row.docs_url||null" in compact_dashboard_text
    assert "file_path:row.source_path||null" in compact_dashboard_text
    assert "line_start:row.source_start_line||null" in compact_dashboard_text
    assert "function moduleLink(module)" in dashboard_text
    assert re.search(r"function moduleHref\(module\)\s*\{\s*return ['\"]{2};?\s*\}", dashboard_text)
    assert "../api/modules/${module}/" not in dashboard_text
    assert "../../api/modules/${module}/" not in dashboard_text
    assert "GITHUB_SOURCE_BASE" in dashboard_text
    assert "return`${GITHUB_SOURCE_BASE}${path}${anchor}`" in compact_dashboard_text
    assert "architectureViolationFlows=flows.filter" in compact_dashboard_text
    assert "function architectureFindingRows(flow)" in dashboard_text
    assert "function architectureFindingCount(flow)" in dashboard_text
    assert "c.architecture_result==='Violation'||c.recommended_action==='Brokenrule'" in compact_dashboard_text
    assert "functionmarkdownLink(i,label)" in compact_dashboard_text
    assert "cross_layer_issue_count" not in dashboard_text
    header_order = [
        compact_dashboard_text.index("data-sort-key='callable'>Function"),
        compact_dashboard_text.index("data-sort-key='width'>Width"),
        compact_dashboard_text.index("data-sort-key='scope'>Scope"),
        compact_dashboard_text.index("data-sort-key='depth'>Depth"),
        compact_dashboard_text.index("data-sort-key='recommendation'>Recommendation"),
        compact_dashboard_text.index("data-sort-key='signals'>Signals"),
        compact_dashboard_text.index("<th>Summary</th>"),
    ]
    assert header_order == sorted(header_order)
    assert "No review flags detected." in dashboard_text
    assert "Review helper placement" not in dashboard_text
    assert "Review nested helpers" in dashboard_text
    assert "Finding note" not in dashboard_text
    assert "Fix architecture issue" in dashboard_text
    assert "Keep public" not in dashboard_text
    assert "No action needed" not in dashboard_text
    assert "disabled>CopyJSON" not in compact_dashboard_text
    assert "disabled>DownloadJSON" in compact_dashboard_text
    assert "disabled>CopyYAML" not in compact_dashboard_text
    assert "disabled>DownloadYAML" in compact_dashboard_text
    assert "location.reload" not in dashboard_text
    assert "publicSearch:''" in compact_dashboard_text
    assert "quickFilter:'all'" not in compact_dashboard_text
    assert "constDOWNSTREAM_BANDS=" not in compact_dashboard_text
    assert "constDEPTH_BANDS=" not in compact_dashboard_text
    assert "constISSUE_BANDS=" not in compact_dashboard_text
    assert "constISSUE_BOOLEAN_BANDS=" not in compact_dashboard_text
    assert "function architectureViolationCount(flow)" in dashboard_text
    assert "if(typeofvalue==='boolean')returnvalue?1:0" not in compact_dashboard_text
    assert "function issueBandsForRows(rows)" not in dashboard_text
    assert "?ISSUE_BANDS:ISSUE_BOOLEAN_BANDS" not in compact_dashboard_text
    assert "functionmatchesBand(flow,bandValue,bands,metric)" not in compact_dashboard_text
    assert "function populateBandFilter" not in dashboard_text
    assert "matchesBand(f,state.publicDownstreamBand" not in dashboard_text
    assert "matchesBand(f,state.publicDepthBand" not in dashboard_text
    assert "matchesBand(f,state.publicIssueBand" not in dashboard_text
    assert "['publicMinDownstream','publicDownstreamBand']" not in dashboard_text
    assert "quickFilter:'all',sortKey:'callable',sortDirection:'asc'" not in compact_dashboard_text
    assert "populateBandFilter('publicMinDownstream'" not in dashboard_text
    assert "populateBandFilter('publicMinDepth'" not in dashboard_text
    assert "populateBandFilter('publicMinIssues'" not in dashboard_text
    assert "function numericFilterValue(value)" not in dashboard_text
    assert "Number(e.target.value||0)" not in dashboard_text
    assert "functionsortValue(flow,key){if(key==='callable')returntext(flow.function_name).toLowerCase();if(key==='width')returnNumber(flow.width??0);if(key==='scope')returnNumber(flow.scope??flow.scope_asset_count??0);if(key==='depth')returnNumber(flow.max_depth??0);if(key==='recommendation')returnsuggestedActionLabel(flow).toLowerCase();if(key==='signals')returnflowSignals(flow).join('').toLowerCase();" in compact_dashboard_text
    assert "if(key==='downstream')" not in compact_dashboard_text
    assert "if(key==='next_step')" not in compact_dashboard_text
    assert "if(key==='findings')" not in compact_dashboard_text
    card_order = [
        compact_dashboard_text.index("label:'Publiccallables'"),
        compact_dashboard_text.index("label:'Brokenrules'"),
        compact_dashboard_text.index("label:'Reviewcandidates'"),
    ]
    assert card_order == sorted(card_order)
    assert "Notebook-facing APIs scanned in this review workspace." in dashboard_text
    assert "No architecture violations found." in dashboard_text
    assert "High-priority public callables" not in dashboard_text
    assert "Long public flows" not in dashboard_text
    assert "Public flows that can be shortened" not in dashboard_text
    assert "Public APIs to review first." not in dashboard_text
    assert "Public callable flows whose depth exceeds the threshold." not in dashboard_text
    assert "Public callable flows with internal helpers that may be simplified, merged, or moved closer to their caller." not in dashboard_text
    assert "Clean public flows" not in dashboard_text
    assert "Public flows with warnings" not in dashboard_text
    assert "Callables flagged as single-use helper candidates" not in dashboard_text
    assert "label:'Merge candidates'" not in dashboard_text
    assert "value:s.merge_candidates" not in dashboard_text
    assert "305 Merge candidates" not in dashboard_text
    assert "Review architecture scopes, search for risks, and inspect the selected function call graph when available. Width is direct calls; scope is total runtime assets in the selected scope." in normalized_dashboard_text
    assert "Review detailed callable actions in Inventory" not in dashboard_text
    assert "architecture-cta" not in dashboard_text

    assert "dataLoadStatus" in dashboard_text
    assert "function functionCallGraphDataUrl()" in dashboard_text
    assert "referenceMarker='/reference/'" in compact_dashboard_text
    assert "assetsMarker='/assets/'" in compact_dashboard_text
    assert "+'_data/function-call-graph.json'" in compact_dashboard_text
    assert "+'reference/_data/function-call-graph.json'" in compact_dashboard_text
    assert "newURL('reference/_data/function-call-graph.json',document.baseURI).href" in compact_dashboard_text
    assert "Failed to load function call graph data. Attempted URL:" in dashboard_text
    assert "HTTP status:" in dashboard_text
    assert "Error message:" in dashboard_text
    assert "function renderLoadedCount()" in dashboard_text
    assert "total functions; ${publicEntryFlows.length} public functions available; ${visibleFlows.length} rows after filters" in dashboard_text
    assert "renderLoadedCount();constallRuntimeCount=inventory.length" in compact_dashboard_text
    assert "architectureThresholds=data.architecture_thresholds||architectureThresholds" in compact_dashboard_text
    assert "function longCallChainThreshold()" in dashboard_text
    assert "function largeDependencySurfaceThreshold()" in dashboard_text
    assert "long_call_chain_depth:null" in compact_dashboard_text
    assert "large_dependency_surface:null" in compact_dashboard_text
    assert "function positiveThreshold(value)" in dashboard_text
    assert "Number.isFinite(numeric)&&numeric>0?numeric:null" in compact_dashboard_text
    assert "architecture_violation_count??0" in compact_dashboard_text
    assert "down>=12" not in dashboard_text
    assert "Violation reason" in dashboard_text
    assert "Helper-level architecture findings found" not in dashboard_text
    assert "No architecture violations found in this graph." in dashboard_text
    assert "function flowSignals(flow)" in dashboard_text
    assert "grid-template-columns:repeat(3,minmax(0,1fr))" in compact_dashboard_text
    assert "overflow-x:auto" in compact_dashboard_text
    assert "grid-template-columns:repeat(3,minmax(13rem,1fr))" in compact_dashboard_text

    assert "function hasArchitectureViolation(flow)" in dashboard_text
    assert "function isGraphReviewCandidate(flow)" in dashboard_text
    assert "function publicCallableSeverity(flow)" in dashboard_text
    assert "Review candidates" in dashboard_text
    assert "flows.filter(isGraphReviewCandidate).length" in compact_dashboard_text
    assert "external_dependents_count||0)>0)signals.push('Sharedhelper')" in compact_dashboard_text
    assert "if(isGraphReviewCandidate(flow))return'Reviewnestedhelpers'" in compact_dashboard_text
    assert "Shareddependency','Maybecombine'].includes" not in compact_dashboard_text
    assert "severity-${severity}-row" in dashboard_text
    assert "severity-review-row" in dashboard_text
    assert "severity-architecture-row" in dashboard_text
    assert "function summaryRow(flow)" in dashboard_text
    assert "openSummaryFlow:''" in compact_dashboard_text
    assert "constopen=state.openSummaryFlow===flow.qualified_name" in compact_dashboard_text
    assert "aria-expanded='${open?'true':'false'}'" in compact_dashboard_text
    assert "state.openSummaryFlow=state.openSummaryFlow===summaryToggle.dataset.summaryToggle?'':summaryToggle.dataset.summaryToggle" in compact_dashboard_text
    assert "state.activePublicFlow=row.dataset.publicFlowRow;state.selectedFlow=row.dataset.publicFlowRow;state.collapsedPublicList=true" in compact_dashboard_text
    assert "state.openSummaryFlow=row.dataset.publicFlowRow" not in compact_dashboard_text
    assert "state.activePublicFlow===flow.qualified_name" not in compact_dashboard_text
    assert "data-summary-toggle" in dashboard_text
    assert "View summary" in dashboard_text
    assert "Width:${esc(flow.width??0)}directcall(s)" in compact_dashboard_text
    assert "Scope:${esc(flow.scope??flow.scope_asset_count??0)}runtimeasset(s)" in compact_dashboard_text
    assert "Width(directcalls)" in compact_dashboard_text
    assert "Scope(runtimeassets)" in compact_dashboard_text
    assert "Depth:${esc(flow.max_depth||0)}" in compact_dashboard_text
    assert "No decision findings." not in dashboard_text
    assert "Preserve backwards compatibility" in dashboard_text
    assert "Selected cleanup should preserve existing public callable behavior and avoid breaking current users." in dashboard_text
    assert "Copy JSON" not in dashboard_text
    assert "Download JSON" in dashboard_text
    assert "Copy YAML" not in dashboard_text
    assert "Download YAML" in dashboard_text
    assert "Copy flow Markdown" not in dashboard_text
    assert "function markdownPacket(packet)" not in dashboard_text
    assert "function yamlPacket(packet)" in dashboard_text
    assert "publicCallableSeverity(f)==='architecture'" in compact_dashboard_text
    assert "Maybe combine" in dashboard_text
    assert "Review helper" in dashboard_text
    assert "Review helpers" in dashboard_text
    assert "reasons.join('')" not in compact_dashboard_text
    assert "Contains ${violations} architecture violations." not in dashboard_text
    assert "Depth is ${flow.max_depth}; threshold is >= ${longThreshold}." not in dashboard_text
    assert "Has ${flow.downstream_count} downstream functions; threshold is >= ${largeThreshold}." not in dashboard_text
    assert "downstream functions, threshold >= ${largeThreshold}" not in dashboard_text
    assert "Width ${flow.width??flow.direct_call_count??0} direct call(s), threshold > ${largeThreshold}" in dashboard_text
    assert "Width is greater than 10. Width means direct calls from this public callable." in flow_text
    assert "Too many steps threshold >= " in dashboard_text
    assert "longThreshold!==null" in compact_dashboard_text
    assert "largeThreshold!==null" in compact_dashboard_text
    assert "(flow.width||0)>largeThreshold" in compact_dashboard_text
    assert "(flow.downstream_count||0)>=largeThreshold" not in compact_dashboard_text
    assert "Maybecombinehelpers:${esc(mergeCandidateCount(flow))}" in compact_dashboard_text
    assert "deep cross-module helper chains" not in dashboard_text
    assert "inline single-use helper" not in dashboard_text
    assert "Helper suggestions are review hints, not automatic judgments." in dashboard_text
    assert "Helper suggestions are review hints, not automatic judgments." in inventory_text
    assert "function timesUsedLabel(count)" in inventory_text
    assert "Times used:" in inventory_text
    assert "Used once" in inventory_text
    assert "Used several times" in inventory_text
    assert "one call site" not in inventory_text
    assert "Call sites:" not in inventory_text

    assert "Runtime inventory" in inventory_text
    assert "The Runtime inventory focuses on src/fabricops_kit runtime code assets that are reachable from public callables or template runtime references." in normalized_inventory_text
    assert "Generated at:" in inventory_text
    assert "Generated at:</strong>" in inventory_text
    assert "SGT" in inventory_text
    assert " UTC" not in inventory_text
    assert "Data source:" in inventory_text
    assert "function-call-graph.json" in inventory_text
    assert "Date.now" not in inventory_text
    assert "Function Call Graph" in inventory_text
    assert "function-call-graph-dashboard.html" in inventory_text
    assert "callable-page-nav" in inventory_text
    assert "header-action" not in inventory_text
    assert "<aclass='callable-page-tabis-active'href='function-call-graph-dashboard.html'aria-current='page'>FunctionCallGraph</a>" in compact_inventory_text
    assert "<aclass='callable-page-tab'href='function-call-graph-dashboard.html#runtime-inventory'>Runtimeinventory</a>" in compact_inventory_text
    assert "<aid='openFunctionCallGraphJson'class='callable-page-action'href='../reference/_data/function-call-graph.json'>OpenJSONdata</a>" in compact_inventory_text
    assert "<aclass='callable-page-action'href='../'>BacktoDocs</a>" in compact_inventory_text
    for common_shell in [compact_dashboard_text, compact_inventory_text]:
        assert "body{margin:0;font-family:Inter,system-ui,sans-serif;background:#f8fafc;color:#0f172a" in common_shell
        assert "header,main{box-sizing:border-box;max-width:1480px;margin:0auto;padding:1rem" in common_shell
        assert "header{background:#fff;border-bottom:1pxsolid#dbe3ef" in common_shell
        assert "headerh1{margin:" in common_shell
        assert "headerp{margin:" in common_shell and "color:#475569" in common_shell
    assert "inventorySummaryCards" in inventory_text
    assert "function renderInventoryCards()" in inventory_text
    for generated_text in [dashboard_text, inventory_text, flow_text]:
        assert "Internal helper" not in generated_text
        assert "Internal function" not in generated_text
    assert "Shared helpers" in inventory_text
    assert "Private helpers" in inventory_text
    assert "Non functions" not in inventory_text
    assert "Suggested cleanup" not in inventory_text
    assert "Public callables" in inventory_text
    for scope_label in [
        "All runtime assets",
        "Others / Cannot trace back to a public function",
        "Runtime assets",
        "Needs review",
        "Cannot trace back to a public function",
        "Selected for export",
    ]:
        assert scope_label in inventory_text
    assert "The Runtime inventory focuses on src/fabricops_kit runtime code assets that are reachable from public callables or template runtime references." in normalized_inventory_text
    assert "Use this runtime inventory to inspect deduplicated src/fabricops_kit code assets that support public callables and template runtime flows." in normalized_inventory_text
    assert "Architecture inventory" not in inventory_text
    assert "giant review table" not in inventory_text
    assert '<article class="surface-card ${esc(c.cls)}">' in inventory_text
    assert ".surface-cardstrong{display:block" in compact_inventory_text
    assert ".surface-cardspan{display:block" in compact_inventory_text
    assert "function sourceCallableLink(i)" in inventory_text
    assert 'class="source-link" href="${esc(href)}"' in inventory_text
    assert "if(i.source_url)returni.source_url" in compact_inventory_text
    assert "conststart=i.source_start_line" in compact_inventory_text
    assert "#L${start}" in inventory_text
    assert "Showing ${visibleRows.length} runtime inventory records in ${currentScope.label} of ${total} scoped runtime assets." in normalized_inventory_text
    assert "Function metrics are generated from the runtime inventory data." not in normalized_inventory_text
    assert "<tdclass='col-callable'>${sourceCallableLink(i)}</td>" in compact_inventory_text
    assert "class='callable-review-table'data-table-controls='excel'" in compact_inventory_text
    assert "callable-review-table-wrap" in inventory_text
    assert "<thclass='col-file-area'>Sourcefile</th><thclass='col-callable'>Itemname</th><thclass='col-item-type'>Itemtype</th><thclass='col-usage-scope'>Usagescope</th><thclass='col-health'>Health</th><thclass='col-recommended-action'>Recommendedaction</th><thclass='col-details'>Details</th>" in compact_inventory_text
    assert "healthBadge(i)" in inventory_text
    assert "actionBadge(i)" in inventory_text
    assert "usageBadge(i)" in inventory_text
    assert "data-inventory-row" in inventory_text
    assert "data-select-row" not in inventory_text
    assert "selectAllVisible" not in inventory_text
    assert "copyJson" not in inventory_text
    assert "downloadJson" in inventory_text
    assert "copyYaml" not in inventory_text
    assert "downloadYaml" in inventory_text
    assert "searchBox" in inventory_text
    assert "Search runtime inventory" in inventory_text
    assert "Runtime inventory focus <select" not in inventory_text
    assert 'id="runtimeInventory_focusFilter"' not in inventory_text
    assert 'id="runtimeInventory_typeFilter"' not in inventory_text
    assert 'id="runtimeInventory_reachabilityFilter"' not in inventory_text
    assert 'id="runtimeInventory_healthFilter"' not in inventory_text
    assert 'id="runtimeInventory_actionFilter"' not in inventory_text
    assert "Suggested cleanup" not in inventory_text
    assert "Non functions" not in inventory_text
    assert "Cannot trace back to a public function" in inventory_text
    assert "Recommended action" in inventory_text
    assert "Reached from public flow" not in inventory_text
    assert "reachable_from_public_runtime" in inventory_text
    assert "unreachable_runtime_asset" in inventory_text
    assert "function buildFlowSignals(flows)" in inventory_text
    assert "function matchesFilters(i)" in inventory_text
    assert "function supportFocus(i)" in inventory_text
    assert "function rank(i)" in inventory_text
    assert "state.quickFilter" not in compact_inventory_text
    assert "function matchesQuickFilter(i)" not in inventory_text
    assert "function updateQuickFilterChips()" not in inventory_text
    assert 'data-quick-filter=' not in inventory_text
    assert "resetAll(document)" not in inventory_text
    assert "selectedItems()" in inventory_text
    for removed_filter in [
        "moduleFilter",
        "roleGroupFilter",
        "signalFilter",
        "priorityFilter",
        "Advanced / Debug filters",
        "callableRoleFilter",
        "dependencyRoleFilter",
        "kindFilter",
        "reviewStatusFilter",
        "minInboundFilter",
        "minOutboundFilter",
    ]:
        assert removed_filter not in inventory_text
    assert "selectedCount" in inventory_text
    assert "compatibilityMode" in inventory_text
    assert "COMPATIBILITY_MODES" in inventory_text
    assert "CLEANUP_MODE_GUIDANCE" not in inventory_text
    assert "Preserve backwards compatibility" in inventory_text
    assert "Allow breaking changes" in inventory_text
    assert "Selected cleanup should preserve existing public callable behavior and avoid breaking current users." in inventory_text
    assert "Selected cleanup may propose cleaner breaking changes when they improve the callable architecture." in inventory_text
    assert "promptInstruction" in inventory_text
    assert "ai_prompt:cleanupPrompt()" in compact_inventory_text
    assert "Public callable review" not in inventory_text
    assert "Internal cleanup" not in inventory_text
    assert "AI cleanup packet" not in inventory_text
    assert "compat-mode-safe" in inventory_text
    assert "compat-mode-breaking" in inventory_text
    assert "Select visible" in inventory_text
    assert "Clear selection" in inventory_text
    assert "Copy JSON" not in inventory_text
    assert "Download JSON" in inventory_text
    assert "Copy YAML" not in inventory_text
    assert "Download YAML" in inventory_text
    assert "selectedItems" in inventory_text
    assert "refactorPacket" in inventory_text
    assert "fabricops_runtime_refactor_packet" in inventory_text
    assert "selected_inventory_assets" in inventory_text
    assert "selection_context" in inventory_text
    assert "related_public_flows" in inventory_text
    assert "related_architecture_findings" in inventory_text
    assert "functionbuildInventoryFilename(functionCount,extension)" in compact_inventory_text
    assert "fabricops-runtime-refactor-packet__${functionCount}_assets__" in inventory_text
    assert "buildInventoryFilename((packet.selected_inventory_assets||[]).length" in compact_inventory_text
    assert "fabricops-runtime-inventory-cleanup-packet.${isYaml" not in inventory_text
    assert "source_file" in inventory_text
    assert "item_name" in inventory_text
    assert "reachability" in inventory_text
    assert "action_details" in inventory_text
    assert "data-select-row" not in inventory_text

    # Compatibility modes and selected-callable/code-asset packet paths remain available,
    # but the test intentionally avoids exact prose, CSS, and private JS helper names.
    assert combined_dashboard_assets.count("Preserve backwards compatibility") >= 2
    assert combined_dashboard_assets.count("Allow breaking changes") >= 2
    assert "compatibility_mode" in combined_dashboard_assets
    assert "function downloadPacket(format)" in combined_dashboard_assets

    flow_data = json.loads(flow_data_path.read_text(encoding="utf-8"))
    assert set(flow_data) == {
        "metadata",
        "function_inventory",
        "public_entrypoint_flow",
        "public_flows",
        "summary_counts",
        "architecture_thresholds",
        "inventory_row_count",
        "unique_inventory_identity_count",
        "duplicate_inventory_identity_count",
    }
    assert flow_data["metadata"]["generated_at_utc"].endswith("Z")
    assert flow_data["metadata"]["data_source"] == "function-call-graph.json"

    summary_counts = flow_data["summary_counts"]
    public_api_surface = summary_counts["public_api_surface"]
    assert flow_data["public_flows"]
    assert flow_data["public_flows"] == flow_data["public_entrypoint_flow"]
    assert flow_data["inventory_row_count"] == len(flow_data["function_inventory"])
    assert flow_data["unique_inventory_identity_count"] == len(flow_data["function_inventory"])
    assert flow_data["duplicate_inventory_identity_count"] == 0
    assert any("read" in flow["function_name"].lower() for flow in flow_data["public_flows"])
    assert summary_counts["total_callables"] == len(flow_data["function_inventory"])
    assert summary_counts["callable_kind"]["function"] == 132
    assert summary_counts["public_classes"] == 7
    assert summary_counts["callable_inventory_metrics"]["public_classes"] == 7
    assert summary_counts["private_helper_review"] == flow_data["summary_counts"]["callable_inventory_metrics"]["private_helpers_to_review"]
    assert flow_data["summary_counts"]["callable_inventory_metrics"]["hidden_private_helpers"] > 0
    assert {
        "public_api_entrypoints",
        "long_call_chains",
        "architecture_violations",
        "review_for_merge_helpers",
        "suggested_helper_review",
    } <= set(public_api_surface)


    public_flows = flow_data["public_entrypoint_flow"]
    function_inventory = flow_data["function_inventory"]

    assert summary_counts["layer"]["public"] == len(function_exported_symbols)
    assert set(summary_counts["function_type"]) == {"Public function", "Shared helper", "Public config class"}
    assert summary_counts["callable_inventory_metrics"]["function_callables"] == (
        summary_counts["function_type"]["Public function"] + summary_counts["function_type"]["Shared helper"]
    )
    assert public_api_surface["public_api_entrypoints"] == len(public_flows)
    assert public_api_surface["architecture_violations"] == sum(
        1 for flow in public_flows if flow["architecture_violation_count"]
    )
    assert public_api_surface["review_for_merge_helpers"] == sum(
        1 for flow in public_flows if flow["helper_cleanup_candidates"]
    )

    public_inventory = {row["function_name"] for row in function_inventory if row["layer"] == "public"}
    public_callable_inventory = {row["function_name"] for row in function_inventory if row["function_type"] == "Public function" or row.get("layer") == "public" or row.get("reachability_kind") == "public_entrypoint"}
    assert {"read_lakehouse_table", "read_lakehouse_csv", "profile_dataframe"} <= public_callable_inventory
    assert public_inventory == function_exported_symbols
    assert len(function_inventory) == summary_counts["total_callables"]
    assert function_inventory
    assert {row["qualified_name"] for row in function_inventory}
    assert len({row["qualified_name"] for row in function_inventory}) == len(function_inventory)
    stable_identities = {
        (
            row["source_path"],
            row["qualified_name"],
            row["source_start_line"],
            row["source_end_line"],
        )
        for row in function_inventory
    }
    assert len(stable_identities) == len(function_inventory)
    inventory_metrics = summary_counts["callable_inventory_metrics"]
    assert inventory_metrics["inventory_row_count"] == len(function_inventory)
    assert inventory_metrics["unique_inventory_identity_count"] == len(function_inventory)
    assert inventory_metrics["duplicate_inventory_identity_count"] == 0
    assert all(str(row["source_path"]).startswith("src/fabricops_kit/") for row in function_inventory)
    assert all(
        not str(row["source_path"]).startswith(("tests/", "docs/", "scripts/", "notebooks/", "templates/"))
        for row in function_inventory
    )
    inventory_names = {row["function_name"] for row in function_inventory}
    assert "_module_name" not in inventory_names
    assert "_public_exports" not in inventory_names
    assert "_template_called_fabricops_functions" not in inventory_names
    assert "_code_from_notebook" not in inventory_names
    for test_only_helper in [
        "_module_name",
        "_public_exports",
        "_template_called_fabricops_functions",
        "_code_from_notebook",
    ]:
        assert test_only_helper not in dashboard_text
        assert test_only_helper not in inventory_text
    assert all(row["callable_kind"] in {"function", "class"} for row in function_inventory)
    assert "supporting_object" not in {row["layer"] for row in function_inventory}
    assert all(row["recommended_action"] for row in function_inventory)

    private_helper_rows = [row for row in function_inventory if row["layer"] == "private_helper"]
    assert private_helper_rows
    assert all(row["function_type"] == "Private helper" for row in private_helper_rows)
    assert all(row["function_name"].split(".")[-1].startswith("_") for row in private_helper_rows)
    assert all(row["architecture_signals"] == [] for row in private_helper_rows)
    assert all(row["owner_function"] or row["usage_scope"] == "unused" for row in private_helper_rows)
    assert all(row["owner_file"] for row in private_helper_rows)
    assert any(row["leaks_outside_owner_file"] for row in private_helper_rows)
    assert {"Keep private helper", "Merge into owner", "Rename to shared helper", "Move closer to owner", "Verify possible orphan"} & {row["recommended_action"] for row in private_helper_rows}
    unreachable_rows = [row for row in function_inventory if row.get("reachability") == "unreachable_runtime_asset"]
    assert unreachable_rows
    assert all(row["recommended_action"] == "Verify possible orphan" for row in unreachable_rows)
    assert all(row["review_status_label"] == "Cannot trace back to a public function" for row in unreachable_rows)
    assert sum(1 for row in function_inventory if row["function_type"] == "Public function") == summary_counts["function_type"]["Public function"]
    assert sum(1 for row in function_inventory if row["function_type"] == "Shared helper") == summary_counts["function_type"]["Shared helper"]
    assert any(
        callee["function_type"] == "Private helper"
        for flow in public_flows
        for callee in flow["transitive_callees"]
    )
    rows_by_qn = {row["qualified_name"]: row for row in function_inventory}
    assert "fabricops_kit.config.FrameworkConfig" not in rows_by_qn
    assert "fabricops_kit.config.FabricStore.root" not in rows_by_qn
    assert all(row["reachability_kind"] == "public_entrypoint" for row in function_inventory if row["layer"] == "public")
    assert all(row["review_status"] != "unreachable" for row in function_inventory)
    expected_runtime_chains = {
        "fabricops_kit.io.shared.write_lakehouse_table_core": {
            "fabricops_kit.io.shared.validate_dataframe_writer",
            "fabricops_kit.io.shared.resolve_configured_lakehouse_table",
            "fabricops_kit.io.shared.normalize_write_mode",
            "fabricops_kit.io.shared.write_delta_path",
        },
        "fabricops_kit.io.shared.read_lakehouse_table_core": {
            "fabricops_kit.io.shared.resolve_configured_lakehouse_table",
            "fabricops_kit.io.shared.read_delta_path",
        },
        "fabricops_kit.io.shared.resolve_configured_lakehouse_table": {
            "fabricops_kit.io.shared.resolve_target_store",
            "fabricops_kit.io.shared.resolve_lakehouse_table_location",
        },
        "fabricops_kit.io.shared.resolve_configured_file_path": {
            "fabricops_kit.io.shared.resolve_target_store",
            "fabricops_kit.io.shared.resolve_lakehouse_file_location",
        },
    }
    for caller_qn, expected_callees in expected_runtime_chains.items():
        matching_flows = [
            flow for flow in public_flows
            if caller_qn in {row["qualified_name"] for row in flow["transitive_callees"]}
        ]
        observed = {
            row["qualified_name"]
            for flow in matching_flows
            for row in flow["transitive_callees"]
        }
        assert expected_callees <= observed
    known_symbols = {
        "resolve_lakehouse_file_location",
        "resolve_lakehouse_table_location",
        "resolve_target_store",
        "validate_dataframe_writer",
        "write_delta_path",
        "write_lakehouse_table_core",
        "write_warehouse_synapsesql",
        "read_lakehouse_table_core",
        "read_delta_path",
        "resolve_configured_lakehouse_table",
        "resolve_configured_file_path",
        "resolve_configured_warehouse_table",
    }
    for name in known_symbols:
        rows = [row for row in function_inventory if row["function_name"] == name]
        assert rows
        assert all(row["function_type"] != "Unknown" for row in rows)
    expected_inventory_keys = {
        "qualified_name",
        "function_name",
        "module",
        "source_path",
        "owner_file",
        "source_url",
        "source_start_line",
        "source_end_line",
        "function_type",
        "layer",
        "review_status",
        "review_status_label",
        "callable_kind",
        "callable_role",
        "callable_role_group",
        "callable_role_group_label",
        "callable_role_detail",
        "callable_role_detail_label",
        "dependency_role",
        "owner_qualified_name",
        "owner_function",
        "owner_module",
        "owner_file",
        "leaks_outside_owner_file",
        "usage_scope",
        "usage_scope_label",
        "architecture_signals",
        "review_signals",
        "reachability",
        "reachability_kind",
        "reachability_label",
        "recommended_action",
        "priority",
        "signals",
        "called_by_count",
        "call_site_count",
        "recursive",
        "repeated_within_single_caller",
        "calls_count",
        "callers",
        "callees",
    }
    public_inventory_keys = expected_inventory_keys | {"docs_path", "docs_url"}
    assert all(set(item) == expected_inventory_keys or set(item) == public_inventory_keys for item in function_inventory)
    assert all({"function_type", "layer", "dependency_role", "callable_kind"} <= set(item) for item in function_inventory)

    callable_flow_text = (REFERENCE_DIR / "function-call-graph.md").read_text(encoding="utf-8")
    assert "First make it exist. Then make it good." in callable_flow_text
    assert "AI generated code can work correctly but still leave behind messy integration patterns" in callable_flow_text
    assert "What the dashboard signals" in callable_flow_text
    assert "Too many helpers" in callable_flow_text
    assert "Long nested chains" in callable_flow_text
    assert "Function Call Graph Dashboard" in callable_flow_text
    assert "Open architecture dashboard" in callable_flow_text
    assert "focused cleanup packets as JSON or YAML" in callable_flow_text
    assert "fabricops_runtime_refactor_packet" in callable_flow_text
    assert "selected inventory assets" in callable_flow_text
    assert "Pointless wrapper functions" not in callable_flow_text
    assert "Public callable dependencies" not in callable_flow_text
    assert "Public callables → Shared helpers → Utility callables" not in callable_flow_text
    assert "Internal-to-internal calls are valid" not in callable_flow_text
    assert "Role group = broad job of the callable." not in callable_flow_text
    serialized_flow = json.dumps(flow_data)
    for legacy_name in ["cross_layer", "deep_chain", "inline_candidate", "used_by_count", "change_risk", "refined_recommended_action"]:
        assert legacy_name not in serialized_flow

    expected_public_flow_keys = {
        "qualified_name",
        "function_name",
        "module",
        "docs_path",
        "docs_url",
        "source_path",
        "owner_file",
        "source_url",
        "source_start_line",
        "source_end_line",
        "priority",
        "recommended_simplification_action",
        "warnings",
        "width",
        "direct_call_count",
        "scope",
        "scope_asset_count",
        "downstream_count",
        "max_depth",
        "modules_touched",
        "source_python_files",
        "architecture_violation_count",
        "architecture_violation_breakdown",
        "helper_cleanup_candidates",
        "direct_callees",
        "transitive_callees",
        "private_helper_review_items",
        "external_dependents_count",
        "end_node_count",
    }
    assert all(set(flow) == expected_public_flow_keys for flow in public_flows)
    assert all(flow["source_python_files"] for flow in public_flows)
    assert all(path.endswith(".py") for flow in public_flows for path in flow["source_python_files"])
    assert any(
        callee["architecture_result"] in {"Warning", "Violation"}
        for flow in public_flows
        for callee in flow["transitive_callees"]
    )


def test_refactor_signals_json_includes_run_table_guardrails() -> None:
    """Verify structured refactor signals are generated for public guardrail orchestration."""
    signal_path = REFERENCE_DIR / "_data" / "refactor-signals.json"
    signals = json.loads(signal_path.read_text(encoding="utf-8"))
    guardrail_signals = signals["run_table_guardrails"]

    assert guardrail_signals["qualified_name"].endswith(".run_table_guardrails")
    assert guardrail_signals["unique_internal_helper_count"] > 0
    assert {
        "qualified_name",
        "unique_internal_helper_count",
        "repeated_helpers",
        "deep_call_chains",
        "single_delegate_helpers",
        "possible_grouping_mismatches",
    } <= set(guardrail_signals)
    assert guardrail_signals["repeated_helpers"]
    assert guardrail_signals["single_delegate_helpers"]
    assert all(
        {"helper", "qualified_name", "branch_count"} <= set(item) for item in guardrail_signals["repeated_helpers"]
    )


def test_fabricops_skill_file_exists() -> None:
    """Verify fabricops skill file exists."""
    assert (ROOT / ".agents" / "skills" / "fabricops" / "SKILL.md").exists()
    assert not (ROOT / ".automation tools" / "skills" / "fabricops" / "SKILL.md").exists()


def test_every_callable_page_has_curated_public_reference_sections() -> None:
    """Verify every callable page has curated public reference sections."""
    callable_pages = sorted(API_REFERENCE_DIR.glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "## Signature" in text, page
        assert "## Parameters" in text, page
        assert "## Returns" in text, page
        assert "## Raises / Errors" in text, page
        assert "## Example usage" in text, page
        assert "## See also" in text, page
        assert "**Used in notebooks:**" in text, page
        if page.stem in CONFIG_MODEL_SYMBOLS:
            assert "Public config class" in text, page
            assert "Public Starter Kit function" not in text, page
        else:
            assert "Public Starter Kit function" in text, page
        assert "## Relationships" not in text, page
        assert "## Maintainer/developer implementation details" not in text, page
        assert "## Source link" not in text, page
        assert '??? example "Source code"' not in text, page
        assert '??? example "View helper source by area"' not in text, page
        assert "## Nested helper functions" not in text, page
        assert "\n## Source\n" not in text, page
        assert "\n## What this is for\n" not in text, page
        assert "\n## When to use it\n" not in text, page
        assert "\n## Raises\n" not in text, page
        assert "\n## Side effects\n" not in text, page
        assert "## AI / machine-readable metadata" not in text, page
        assert "<summary>Machine-readable metadata / metadata details</summary>" not in text, page
        assert "### Implementation contract" not in text, page
        assert "Source file path:" not in text, page


def test_core_callable_pages_have_non_placeholder_ai_guidance() -> None:
    """Verify core callable pages have non placeholder ai guidance."""
    for callable_name in sorted(CORE_CALLABLES):
        page = API_REFERENCE_DIR / f"{callable_name}.md"
        text = page.read_text(encoding="utf-8")
        for section in CORE_PAGE_SECTIONS:
            section_text = _section_text(text, section)
            assert section_text
            assert PLACEHOLDER not in section_text, f"{page} has placeholder in {section}"


def test_setup_metadata_tables_reference_uses_keyword_only_example() -> None:
    """Verify setup metadata tables reference uses keyword only example."""
    text = (API_REFERENCE_DIR / "setup_metadata_tables.md").read_text(encoding="utf-8")

    assert "## At a glance" not in text
    assert "## Purpose" not in text
    assert "## Related guides" not in text
    assert "## See also" in text
    assert "Used by: Not documented yet" not in text
    assert "setup_metadata_tables(CONFIG" not in text
    assert "spark_session=spark" not in _section_text(text, "Example usage")
    example = _section_text(text, "Example usage")
    assert 'class="reference-example-usage"' in example
    assert (
        """```python
setup_metadata_tables(
    spark=spark,
    config=CONFIG,
    env="Sandbox",
)
```"""
        in example
    )


def test_core_automation_manifest_entries_have_non_placeholder_agent_fields() -> None:
    """Verify core agent/automation metadata entries have non placeholder agent/automation metadata fields."""
    manifest = json.loads((REFERENCE_DIR / "_data" / "automation-manifest.json").read_text(encoding="utf-8"))
    by_name = {entry["name"]: entry for entry in manifest if entry.get("type") == "callable"}

    assert CORE_CALLABLES <= set(by_name)
    for callable_name in sorted(CORE_CALLABLES):
        entry = by_name[callable_name]
        for field in CORE_AGENT_FIELDS:
            value = entry[field]
            assert value
            assert value != PLACEHOLDER, f"{callable_name}.{field} is placeholder"


def test_standalone_internal_pages_are_not_generated_by_default() -> None:
    """Verify standalone internal pages are not generated by default."""
    internal_pages = sorted((REFERENCE_DIR / "internal").glob("*.md"))

    assert internal_pages == []


def test_callable_pages_embed_title_first_collapsed_call_flow() -> None:
    """Verify callable pages keep the collapsed helper flow immediately after the title."""
    callable_pages = sorted(API_REFERENCE_DIR.glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        ordered_markers = [
            "## Signature",
            "## Example usage",
            "## Parameters",
            "## Returns",
            "## Raises / Errors",
            "## See also",
        ]
        if "### Return interpretation" in text:
            ordered_markers.insert(ordered_markers.index("## Raises / Errors"), "### Return interpretation")
        if "### Common failure causes" in text:
            ordered_markers.insert(ordered_markers.index("## See also"), "### Common failure causes")
        positions = [text.index(marker) for marker in ordered_markers]
        assert positions == sorted(positions), page
        assert '??? info "Maintainer/developer call flow"' not in text, page
        assert "Maintainer/developer implementation details" not in text, page
        assert "Machine-readable metadata / metadata details" not in text, page
        assert "### Refactor signals" not in text, page
        assert "Unique internal/private helpers:" not in text, page
        assert "Internal/private helpers shown here are implementation details, not public API" not in text, page
        assert '??? info "Nested helper functions:' not in text, page
        assert '??? info "Implementation helpers used:' not in text, page
        assert 'class="reference-helper-groups"' not in text, page
        assert '??? example "View helper source by area"' not in text, page
        assert '??? example "Source code"' not in text, page
        assert "\n### `_" not in text, page
        assert "\n## `_" not in text, page
        if 'class="reference-call-tree"' in text:
            call_flow_pos = text.index('??? info "Downstream callables: ')
            first_description_pos = min(
                position
                for marker in (
                    '<p class="reference-catalogue-item-meta reference-catalogue-item-badges">',
                    "**Used in notebooks:**",
                    "## Signature",
                )
                for position in [text.index(marker)]
            )
            assert text.index("# ") < call_flow_pos < first_description_pos, page
            assert "```text" not in text.split('??? info "Downstream callables: ', 1)[1].split("##", 1)[0], page


def test_internalized_enforce_profile_behavior_has_no_standalone_page() -> None:
    """Verify internalized enforce_profile_behavior has no standalone page after audit."""
    assert not (API_REFERENCE_DIR / "enforce_profile_behavior.md").exists()


def test_indent_markdown_indents_multiline_items_and_blank_lines() -> None:
    """Verify indent markdown indents multiline items and blank lines."""
    from scripts.generate_function_reference import _indent_markdown

    assert _indent_markdown(["first", "", "```python\nprint('x')\n\nprint('y')\n```"], spaces=2) == [
        "  first",
        "",
        "  ```python",
        "  print('x')",
        "",
        "  print('y')",
        "  ```",
    ]


def test_internal_reference_page_generation_flag(monkeypatch) -> None:
    """Verify internal reference page generation flag."""
    from scripts.generate_function_reference import generate_internal_reference_pages

    monkeypatch.delenv("FABRICOPS_GENERATE_INTERNAL_REFERENCE_PAGES", raising=False)
    assert not generate_internal_reference_pages()

    monkeypatch.setenv("FABRICOPS_GENERATE_INTERNAL_REFERENCE_PAGES", "true")
    assert generate_internal_reference_pages()


def test_github_source_url_defaults_to_main(monkeypatch) -> None:
    """Verify github source url defaults to the reachable main branch."""
    monkeypatch.delenv("GITHUB_SOURCE_REF", raising=False)
    monkeypatch.delenv("FABRICOPS_SOURCE_REF", raising=False)

    from scripts.generate_function_reference import github_source_url

    assert github_source_url("src/fabricops_kit/config.py", 595, 704) == (
        "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L595-L704"
    )


def test_github_source_url_uses_configured_source_ref(monkeypatch) -> None:
    """Verify github source url uses an explicitly configured reachable source ref."""
    monkeypatch.setenv("GITHUB_SOURCE_REF", "review-sha-123")

    from scripts.generate_function_reference import github_source_url

    assert github_source_url("src/fabricops_kit/config.py", 595, 704) == (
        "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/review-sha-123/src/fabricops_kit/config.py#L595-L704"
    )


def test_missing_examples_are_plain_text_not_python_code() -> None:
    """Verify missing examples are plain text not python code."""
    callable_pages = sorted(API_REFERENCE_DIR.glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        if "## Example usage" not in text:
            continue
        example = _section_text(text, "Example usage")
        assert "```python\nNot documented yet\n```" not in example, page
        if "Example usage not documented yet." in example:
            assert "```python" not in example, page


def test_callable_pages_show_source_cards_in_public_reference() -> None:
    """Verify callable pages show source cards in the public reference."""
    callable_pages = sorted(API_REFERENCE_DIR.glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "## Source link" not in text, page
        assert "View on GitHub" in text, page
        assert '<div class="reference-source-card" markdown="1">' in text, page
        assert "Source file path:" not in text, page
        assert "GitHub source URL:" not in text, page


def test_display_guardrail_results_uses_one_clickable_call_tree() -> None:
    """Verify display guardrail results renders one linked helper call tree."""
    text = (API_REFERENCE_DIR / "display_guardrail_results.md").read_text(encoding="utf-8")
    implementation_section = text.split("## See also", 1)[0]

    assert text.count('??? info "Downstream callables: 14"') == 1
    assert "Dependency data is generated from the callable architecture inventory." in implementation_section
    assert '??? example "View helper source by area"' not in implementation_section
    assert '??? example "Source code"' not in implementation_section
    assert "Implementation helper count: 11" not in text
    assert 'class="reference-helper-groups"' not in implementation_section
    assert re.search(
        r'href="https://github\.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/(?:display_guardrail_results|shared)\.py#L\d+(?:-L\d+)?"',
        implementation_section,
    )

    for helper_name in ["build_guardrail_detail_rows", "build_guardrail_summary_rows"]:
        assert f"><code>{helper_name}(...)</code></a>" in implementation_section
    assert "><code>_guardrail_reason(...)</code></a>" in implementation_section


def test_display_guardrail_results_lists_nested_private_helpers() -> None:
    """Verify nested private helpers appear in callable helper chips."""
    text = (API_REFERENCE_DIR / "display_guardrail_results.md").read_text(encoding="utf-8")
    implementation_section = text.split("## See also", 1)[0]

    assert implementation_section.count('??? info "Downstream callables: 14"') == 1
    assert '??? info "Implementation helpers used:' not in implementation_section
    assert 'class="reference-helper-groups"' not in implementation_section
    assert (
        "Unique internal/private helpers: 11. Repeated calls may appear in multiple branches."
        not in implementation_section
    )
    assert '<div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">' in implementation_section
    assert "### Refactor signals" not in implementation_section
    assert 'class="reference-call-tree-more"' not in implementation_section
    assert "```text" not in implementation_section

    for helper_name in ["build_guardrail_detail_rows", "build_guardrail_summary_rows"]:
        assert f"><code>{helper_name}(...)</code></a>" in implementation_section
    assert "><code>_guardrail_reason(...)</code></a>" in implementation_section


def _reference_call_tree_rows(text: str) -> list[str]:
    """Return normalized callable names and prefixes from a generated call tree."""
    rows = []
    for prefix, name in re.findall(
        r'<div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">(?P<prefix>.*?)</span>.*?<code>(?P<name>[^(<]+)\(\.\.\.\)</code></(?:a|div)>',
        text,
    ):
        rows.append(f"{prefix}{name}")
    return rows


def _dashboard_flow_tree_rows(flow: dict[str, object]) -> list[str]:
    """Return normalized callable names and prefixes from callable-flow JSON."""
    root_qn = str(flow["qualified_name"])
    by_parent: dict[str, list[dict[str, object]]] = {}
    for row in flow.get("transitive_callees", []):
        assert isinstance(row, dict)
        parent = str(row.get("parent_qualified_name") or root_qn)
        by_parent.setdefault(parent, []).append(row)
    rows = [str(flow["function_name"])]

    def sort_key(row: dict[str, object]) -> tuple[int, str, str, str]:
        return (
            int(row.get("depth") or 0),
            str(row.get("module") or ""),
            str(row.get("function_name") or "").lower(),
            str(row.get("qualified_name") or ""),
        )

    def visit(parent_qn: str, prefix: str, ancestors: set[str]) -> None:
        children = sorted(by_parent.get(parent_qn, []), key=sort_key)
        for index, child in enumerate(children):
            child_qn = str(child.get("qualified_name") or "")
            connector = "└── " if index == len(children) - 1 else "├── "
            rows.append(f"{prefix}{connector}{child['function_name']}")
            if child_qn and child_qn not in ancestors:
                extension = "    " if index == len(children) - 1 else "│   "
                visit(child_qn, prefix + extension, ancestors | {child_qn})

    visit(root_qn, "", {root_qn})
    return rows


def test_display_guardrail_results_dependency_count_matches_callable_architecture_inventory() -> None:
    """Verify display_guardrail_results uses one canonical dependency inventory everywhere."""
    callable_flow = json.loads((REFERENCE_DIR / "_data" / "function-call-graph.json").read_text(encoding="utf-8"))
    flow = next(
        item
        for item in callable_flow["public_entrypoint_flow"]
        if item["function_name"] == "display_guardrail_results"
    )
    reference_index = REFERENCE_INDEX.read_text(encoding="utf-8")
    detail_page = (API_REFERENCE_DIR / "display_guardrail_results.md").read_text(encoding="utf-8")

    assert flow["width"] == 1
    assert flow["scope"] == 15
    assert flow["downstream_count"] == 14
    assert any(callee["function_type"] == "Private helper" for callee in flow["transitive_callees"])
    assert 'data-callable-name="display_guardrail_results"' in reference_index
    assert "Downstream callables: 14" in reference_index
    assert '??? info "Downstream callables: 14"' in detail_page
    assert _reference_call_tree_rows(detail_page) == _dashboard_flow_tree_rows(flow)


def test_removed_aggregate_governance_wrapper_pages_are_absent() -> None:
    """Verify removed aggregate governance wrapper pages are no longer generated."""
    assert not (API_REFERENCE_DIR / "widget_author_guardrail_rules.md").exists()
    assert not (API_REFERENCE_DIR / "widget_review_table_governance.md").exists()


def test_clickable_call_tree_does_not_link_root_to_nested_self_page() -> None:
    """Verify root call-tree labels are plain text rather than nested self links."""
    callable_pages = sorted(API_REFERENCE_DIR.glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        match = re.search(r'<div class="reference-call-tree" role="tree"[^>]*>(?P<body>.*?)</div>', text, re.DOTALL)
        if not match:
            continue
        slug = page.stem
        first_row = match.group("body").split("\n", 2)[1]
        assert f'href="{slug}/"' not in match.group("body"), page
        assert f'href="../{slug}/"' not in first_row, page
        assert f"<code>{slug}(...)</code>" in first_row, page


def test_public_callable_call_tree_renders_before_description() -> None:
    """Verify public callable helper trees appear directly below the title."""
    text = (API_REFERENCE_DIR / "prepare_pipeline_table_configs.md").read_text(encoding="utf-8")
    title_index = text.index("# prepare_pipeline_table_configs")
    description_index = text.index("Prepare source or target table configs for 02_pipeline.")
    source_index = text.index('<div class="reference-source-card" markdown="1">')
    usage_index = text.index("**Used in notebooks:** `02_pipeline`")

    assert title_index < description_index < source_index < usage_index
    assert '??? info "Downstream callables:' in text


def test_callable_pages_omit_machine_metadata_from_public_reference() -> None:
    """Verify callable pages omit machine metadata from public pages."""
    callable_pages = sorted(API_REFERENCE_DIR.glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "\n## Function manifest" not in text, page
        assert "\n## Implementation contract" not in text, page
        assert "\n## Inbound references" not in text, page
        assert "\n## Outbound references" not in text, page
        assert "<summary>Machine-readable metadata / metadata details</summary>" not in text, page
        assert "### Function manifest" not in text, page
        assert "### Implementation contract" not in text, page
        assert "### Raw source metadata" not in text, page


def test_function_catalogue_uses_simplified_callable_flow_chips() -> None:
    """Verify catalogue cards expose simplified callable flow chips."""
    text = REFERENCE_INDEX.read_text(encoding="utf-8")
    assert "Inbound" not in text
    assert "Outbound" not in text
    assert "incoming" not in text.lower()
    assert "outgoing" not in text.lower()
    assert "Used in notebooks:" in text
    assert "Used in 1 notebook" not in text
    assert "Used by 1 public function" not in text
    assert "internal helpers" not in text
    assert "Calls 1 public function" not in text
    assert "nested helper functions" not in text
    assert "Downstream callables:" in text
    assert "Dependency data is generated from the callable architecture inventory." in text
    assert 'href="../api/reference/profile_dataframe/"' in text
    assert "<code>profile_dataframe</code>" in text


def test_module_pages_are_removed_from_public_docs_output() -> None:
    """Verify module pages are removed from public docs output."""
    assert not (ROOT / "docs" / "api" / "modules" / "guardrails.md").exists()


def test_setup_notebook_reference_uses_human_first_source_documentation() -> None:
    """Verify setup notebook reference uses human first source documentation."""
    text = (API_REFERENCE_DIR / "setup_notebook.md").read_text(encoding="utf-8")

    assert "../../api/modules/config/#setup_notebook" not in text
    assert "View on GitHub" in text
    assert text.count('<div class="reference-source-card" markdown="1">') == 1
    assert "## Example usage" in text
    assert "context = setup_notebook" in _section_text(text, "Example usage")
    for marker in ("## Signature", "## Parameters", "## Returns"):
        assert marker in text
    assert "## AI / machine-readable metadata" not in text
    assert "Machine-readable metadata / metadata details" not in text
    assert "- Starting a FabricOps notebook from 00_env_config" in text
    assert "- Validating configured environment targets before downstream helpers run" in text
    assert "- Capturing runtime metadata for later lineage, review, or handover steps" in text
    assert "## Parameters" in text
    assert "| `config` |" in text
    assert "| Yes |" in text or "| No |" in text
    assert "## Source link" not in text


def test_public_callables_have_one_canonical_full_content_page() -> None:
    """Verify public callables have one canonical full content page."""
    manifest = json.loads((REFERENCE_DIR / "_data" / "function-manifest.json").read_text(encoding="utf-8"))
    public_names = sorted({entry["name"] for entry in manifest if entry.get("classification") == "Callable"})
    public_class_names = sorted({entry["name"] for entry in manifest if entry.get("classification") == "Public class"})

    assert public_names
    assert public_class_names
    for name in public_names:
        canonical_page = API_REFERENCE_DIR / f"{name}.md"
        legacy_page = REFERENCE_DIR / "callables" / f"{name}.md"
        assert canonical_page.exists(), name
        assert not legacy_page.exists(), f"{legacy_page} duplicates canonical full-content page"
        text = canonical_page.read_text(encoding="utf-8")
        assert "## Relationships" not in text, canonical_page
        assert "## Maintainer/developer implementation details" not in text, canonical_page
        assert "**Used in notebooks:**" in text, canonical_page

    generated_pages = sorted(page.stem for page in API_REFERENCE_DIR.glob("*.md"))
    assert generated_pages == sorted([*public_names, *public_class_names])


def test_generated_manifests_point_public_callables_to_canonical_api_reference() -> None:
    """Verify generated manifests point public callables to canonical api reference."""
    function_manifest = json.loads((REFERENCE_DIR / "_data" / "function-manifest.json").read_text(encoding="utf-8"))
    automation_manifest = json.loads((REFERENCE_DIR / "_data" / "automation-manifest.json").read_text(encoding="utf-8"))

    for entry in function_manifest:
        if entry.get("classification") in {"Callable", "Public class"}:
            assert entry["docs_path"] == f"api/reference/{entry['name']}.md"
        elif entry.get("docs_path") is not None:
            assert entry["docs_path"].startswith("reference/internal/")

    for entry in automation_manifest:
        if entry.get("type") == "callable":
            assert entry["docs_path"] == f"api/reference/{entry['name']}.md"
        elif entry.get("docs_path") is not None:
            assert entry["docs_path"].startswith("reference/internal/")


def test_glossary_page_exists_and_includes_required_terms() -> None:
    """Verify glossary page exists and includes required terms."""
    glossary_page = REFERENCE_DIR / "glossary.md"
    glossary_source = REFERENCE_DIR / "_data" / "glossary.json"
    required_terms = {
        "profile",
        "enrichment",
        "guardrails",
        "enforcement",
        "metadata lakehouse",
        "source data",
        "pipeline output",
        "target DataFrame",
        "target table",
        "profile mode",
        "static_data",
        "changing_data",
        "skip",
        "can_continue",
    }

    assert glossary_page.exists()
    assert glossary_source.exists()
    glossary_entries = json.loads(glossary_source.read_text(encoding="utf-8"))
    terms = {entry["term"] for entry in glossary_entries}
    assert required_terms <= terms

    glossary_text = glossary_page.read_text(encoding="utf-8")
    for term in required_terms:
        assert f"<h2>{term}</h2>".lower() in glossary_text.lower()
    assert "Searchable source of truth" in glossary_text


def test_public_callable_records_have_real_metadata_backed_guidance() -> None:
    """Verify public callable records have real metadata backed guidance."""
    function_manifest = json.loads((REFERENCE_DIR / "_data" / "function-manifest.json").read_text(encoding="utf-8"))
    public_records = [entry for entry in function_manifest if entry.get("classification") == "Callable"]

    assert public_records
    for entry in public_records:
        assert entry.get("expanded_purpose"), entry["name"]
        assert entry.get("when_to_use"), entry["name"]
        assert entry.get("return_interpretation"), entry["name"]
        assert entry.get("common_failure_causes"), entry["name"]


def test_callable_pages_with_glossary_terms_render_shared_key_terms() -> None:
    """Verify callable pages with glossary terms render shared key terms."""
    function_manifest = json.loads((REFERENCE_DIR / "_data" / "function-manifest.json").read_text(encoding="utf-8"))
    glossary_entries = json.loads((REFERENCE_DIR / "_data" / "glossary.json").read_text(encoding="utf-8"))
    glossary = {entry["term"]: entry["short_definition"] for entry in glossary_entries}
    for item in glossary_entries:
        for alias in item.get("aliases", []):
            glossary[alias] = item["short_definition"]

    for entry in function_manifest:
        if entry.get("classification") != "Callable" or not entry.get("glossary_terms"):
            continue
        text = (API_REFERENCE_DIR / f"{entry['name']}.md").read_text(encoding="utf-8")
        key_terms = _section_text(text, "Glossary")
        for term in entry["glossary_terms"]:
            assert 'class="glossary-chip"' in key_terms, entry["name"]
            assert glossary[term] in key_terms, entry["name"]


def test_internalized_enforce_profile_behavior_keeps_manifest_metadata_without_page() -> None:
    """Verify internalized enforce_profile_behavior remains metadata-only."""
    function_manifest = json.loads((REFERENCE_DIR / "_data" / "function-manifest.json").read_text(encoding="utf-8"))
    entry = next(item for item in function_manifest if item["name"] == "enforce_profile_behavior")
    assert entry["classification"] == "Internal"
    assert entry["used_in_templates"] == []
    assert entry["docs_path"] is None
    assert not (API_REFERENCE_DIR / "enforce_profile_behavior.md").exists()


def test_public_callable_pages_do_not_repeat_intro_as_exact_purpose() -> None:
    """Verify public callable pages do not repeat intro as exact purpose."""
    for page in sorted(API_REFERENCE_DIR.glob("*.md")):
        text = page.read_text(encoding="utf-8")
        lines = text.splitlines()
        intro = next(line.strip() for line in lines[1:] if line.strip())
        if "## Purpose" not in text:
            continue
        purpose = _section_text(text, "Purpose")
        assert purpose.strip() != intro, page
        assert purpose.count(intro) == 0, page


def test_public_callable_pages_do_not_render_generic_filler_sections() -> None:
    """Verify public callable pages do not render generic filler sections."""
    forbidden = (
        "This API reference documents the callable summarized above",
        "Interpret the returned value according to the Returns section above",
        "No common failure causes are documented beyond the Errors section",
    )
    for page in sorted(API_REFERENCE_DIR.glob("*.md")):
        text = page.read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase not in text, page


def test_related_guides_metadata_renders_before_template_and_call_graph_sections() -> None:
    """Verify related guides metadata renders before template and call graph sections."""
    function_manifest = json.loads((REFERENCE_DIR / "_data" / "function-manifest.json").read_text(encoding="utf-8"))
    automation_manifest = json.loads((REFERENCE_DIR / "_data" / "automation-manifest.json").read_text(encoding="utf-8"))
    function_by_name = {
        entry["name"]: entry for entry in function_manifest if entry.get("classification") == "Callable"
    }
    automation_by_name = {entry["name"]: entry for entry in automation_manifest if entry.get("type") == "callable"}

    related_guides = function_by_name["run_table_guardrails"]["related_guides"]
    assert related_guides == [
        {"title": "Pipeline Execution", "path": "../../notebook-templates-implementation-guide/pipeline-execution.md"}
    ]
    assert automation_by_name["run_table_guardrails"]["related_guides"] == related_guides

    text = (API_REFERENCE_DIR / "run_table_guardrails.md").read_text(encoding="utf-8")
    assert "## See also" in text
    assert "- [Pipeline Execution](../../notebook-templates-implementation-guide/pipeline-execution.md)" in text
    assert text.index("## Raises / Errors") < text.index("## See also")
    assert "## Maintainer/developer implementation details" not in text


def test_concept_pages_link_back_to_key_callable_references() -> None:
    """Verify user-guide pages link back to key callable references."""
    environment_config = (
        ROOT / "docs" / "notebook-templates-implementation-guide" / "environment-config.md"
    ).read_text(encoding="utf-8")
    agreement_setup = (ROOT / "docs" / "notebook-templates-implementation-guide" / "agreement-setup.md").read_text(
        encoding="utf-8"
    )
    pipeline_execution = (
        ROOT / "docs" / "notebook-templates-implementation-guide" / "pipeline-execution.md"
    ).read_text(encoding="utf-8")
    governance_review = (ROOT / "docs" / "notebook-templates-implementation-guide" / "governance-review.md").read_text(
        encoding="utf-8"
    )
    metadata_tables = (ROOT / "docs" / "reference" / "metadata.md").read_text(encoding="utf-8")
    lineage_table = (ROOT / "docs" / "reference" / "metadata" / "metadata_data_lineage_table.md").read_text(
        encoding="utf-8"
    )

    assert "[`setup_notebook`](../api/reference/setup_notebook.md)" in environment_config
    assert "[`setup_metadata_tables`](../api/reference/setup_metadata_tables.md)" in environment_config
    assert "[`widget_render_data_steward`](../api/reference/widget_render_data_steward.md)" in agreement_setup
    assert (
        "[`prepare_pipeline_table_configs`](../api/reference/prepare_pipeline_table_configs.md)" in pipeline_execution
    )
    guardrail_target = "run_table_guardrails"
    guardrail_link = f"[`run_table_guardrails`](../api/reference/{guardrail_target}.md)"
    assert guardrail_link in pipeline_execution
    assert "[`widget_select_guardrail_target`](../api/reference/widget_select_guardrail_target.md)" in governance_review
    assert (
        "[`widget_author_schema_freshness_profile_rules`](../api/reference/widget_author_schema_freshness_profile_rules.md)"
        in governance_review
    )
    assert "[`widget_author_dq_rules`](../api/reference/widget_author_dq_rules.md)" in governance_review
    assert (
        "[`widget_review_guardrail_governance`](../api/reference/widget_review_guardrail_governance.md)"
        in governance_review
    )
    if "setup_metadata_tables" in metadata_tables:
        assert "[`setup_metadata_tables`](../api/reference/setup_metadata_tables.md)" in metadata_tables
    assert "[`write_pipeline_lineage`](../../api/reference/write_pipeline_lineage.md)" in lineage_table


def test_template_usage_metadata_renders_from_structured_reference_model() -> None:
    """Verify template usage metadata renders from direct template calls only."""
    function_manifest = json.loads((REFERENCE_DIR / "_data" / "function-manifest.json").read_text(encoding="utf-8"))
    automation_manifest = json.loads((REFERENCE_DIR / "_data" / "automation-manifest.json").read_text(encoding="utf-8"))
    reference_index = (REFERENCE_DIR / "index.md").read_text(encoding="utf-8")

    function_by_name = {entry["name"]: entry for entry in function_manifest}
    automation_by_name = {entry["name"]: entry for entry in automation_manifest if entry.get("type") == "callable"}

    for callable_name in ("run_table_guardrails", "profile_dataframe"):
        if callable_name == "run_table_guardrails":
            assert callable_name in function_by_name
            continue
        assert function_by_name[callable_name]["used_in_templates"]
        assert automation_by_name[callable_name]["used_in_templates"]
        assert f'data-callable-name="{callable_name}"' in reference_index

    for callable_name in ("enforce_freshness", "enforce_profile_behavior"):
        assert function_by_name[callable_name]["used_in_templates"] == []
        assert f'data-callable-name="{callable_name}"' not in reference_index


def test_template_function_map_page_stays_removed() -> None:
    """Verify the intentionally deleted template function map page stays removed."""
    reference_index = (REFERENCE_DIR / "index.md").read_text(encoding="utf-8")

    assert not (REFERENCE_DIR / "template-function-map.md").exists()
    assert "template-function-map.md" not in reference_index
    assert '<section class="template-function-group">' not in reference_index


def _direct_public_notebook_calls(path: Path, public_names: set[str]) -> set[str]:
    """Return direct public FabricOps calls from a notebook's code cells."""
    notebook = json.loads(path.read_text(encoding="utf-8"))
    code = "\n".join(
        "".join(cell.get("source", "")) for cell in notebook.get("cells", []) if cell.get("cell_type") == "code"
    )
    parseable_code = "\n".join(
        f"# {line}" if line.lstrip().startswith(("%", "!")) else line for line in code.splitlines()
    )
    tree = ast.parse(parseable_code)
    imported_public_by_name = {
        alias.asname or alias.name: alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith("fabricops_kit")
        for alias in node.names
        if alias.name in public_names
    }
    package_aliases = {
        alias.asname or alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
        if alias.name == "fabricops_kit"
    }
    direct_public_calls = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in imported_public_by_name:
            direct_public_calls.add(imported_public_by_name[node.func.id])
        elif (
            isinstance(node.func, ast.Attribute)
            and node.func.attr in public_names
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in package_aliases
        ):
            direct_public_calls.add(node.func.attr)
    return direct_public_calls


def test_used_in_templates_metadata_matches_direct_ast_notebook_usage() -> None:
    """Verify used-in-template metadata derives from direct AST notebook calls."""
    function_manifest = json.loads((REFERENCE_DIR / "_data" / "function-manifest.json").read_text(encoding="utf-8"))
    public_names = {entry["name"] for entry in function_manifest if entry.get("classification") == "Callable"}
    expected_by_name = {name: set() for name in public_names}

    for path in sorted((ROOT / "templates" / "notebooks").glob("*.ipynb")):
        for public_name in _direct_public_notebook_calls(path, public_names):
            if public_name in expected_by_name:
                expected_by_name[public_name].add(path.stem)

    order = {
        "00_env_config": 0,
        "01_agreement": 1,
        "02_pipeline": 2,
        "03_governance": 3,
        "99_explore": 4,
        "example_pipeline_demo": 5,
        "example_dq_rule_smoke_test": 6,
    }
    for entry in function_manifest:
        if entry.get("classification") != "Callable":
            continue
        expected = sorted(
            expected_by_name[entry["name"]], key=lambda notebook: (order.get(notebook, len(order)), notebook)
        )
        assert entry["used_in_templates"] == expected


def test_template_called_callable_parameters_render_as_api_table() -> None:
    """Verify template-called callable parameters render as api table."""
    text = (API_REFERENCE_DIR / "profile_dataframe.md").read_text(encoding="utf-8")
    parameters = _section_text(text, "Parameters")

    assert "| Parameter | Type | Required | Description |" in parameters
    assert "| `df` |" in parameters
    assert "| `table_name` |" in parameters


def test_internalized_enforce_profile_behavior_preserves_no_page_contract() -> None:
    """Verify internalized enforce_profile_behavior is not rendered as a public page."""
    assert not (API_REFERENCE_DIR / "enforce_profile_behavior.md").exists()


def test_reference_nav_preserves_existing_user_facing_entries() -> None:
    """Verify generated reference pages remain in the existing sidebar locations."""
    mkdocs_text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "  - Reference:" not in mkdocs_text
    assert (
        "  - Notebook Templates Implementation Guide: notebook-templates-implementation-guide/index.md" in mkdocs_text
    )
    assert "  - List of Metadata Tables:" in mkdocs_text
    assert "      - Overview: reference/metadata.md" in mkdocs_text
    assert "  - List of Functions: reference/index.md" in mkdocs_text
    assert "  - List of DQ Rules:" in mkdocs_text
    assert "      - Overview: reference/dq-rules/index.md" in mkdocs_text
    assert not re.search(r"^  - Glossary: reference/glossary\.md$", mkdocs_text, re.MULTILINE)
    assert not re.search(r"^  - Function & DQ Rules Reference:$", mkdocs_text, re.MULTILINE)
    assert "api/reference/" not in mkdocs_text

    missing = [name for name in _exported_symbols() if not (API_REFERENCE_DIR / f"{name}.md").exists()]
    assert missing == []


def test_maintainer_nav_parks_internal_reference_helpers() -> None:
    """Verify maintainer-facing helper docs are parked under Maintainer Guide."""
    mkdocs_text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Functions by Modules" not in mkdocs_text
    assert "  - Maintainer Guide:" in mkdocs_text
    assert "      - Glossary: reference/glossary.md" in mkdocs_text
    assert "      - Function Call Graph: reference/function-call-graph.md" in mkdocs_text
    assert "      - Implementation Appendix:" in mkdocs_text
    assert "      # AUTO-GENERATED-MODULES-END" in mkdocs_text
    assert "api/modules/config.md" not in mkdocs_text
    assert "api/modules/" not in mkdocs_text
    assert "api/reference/" not in mkdocs_text


def test_callable_layer_dependency_rule_matrix() -> None:
    """Verify callable layer dependency rules match the architecture matrix."""
    from scripts.generate_function_reference import (
        _architecture_dependency_signals,
        _dependency_review_signals,
        _role_dependency_signals,
    )

    assert _architecture_dependency_signals("public", "internal") == []
    assert _architecture_dependency_signals("public", "public") == ["public_calls_public"]
    assert _architecture_dependency_signals("internal", "public") == ["internal_calls_public"]
    assert _architecture_dependency_signals("internal", "internal") == []
    assert _architecture_dependency_signals("public", "supporting_object") == []
    assert _architecture_dependency_signals("internal", "supporting_object") == []
    assert _dependency_review_signals("classification_pending") == ["callee_classification_pending"]
    assert _dependency_review_signals("unreachable") == ["callee_unreachable"]
    assert _dependency_review_signals("classified") == []
    assert _role_dependency_signals("internal_workflow", "utility_function") == ["allowed_internal_role_call"]
    assert _role_dependency_signals("internal_workflow", "internal_validator") == ["allowed_internal_role_call"]
    assert _role_dependency_signals("internal_workflow", "internal_resolver") == ["allowed_internal_role_call"]
    assert _role_dependency_signals("internal_workflow", "config_model_class") == ["allowed_internal_role_call"]
    assert _role_dependency_signals("internal_workflow", "internal_workflow") == ["internal_workflow_calls_internal_workflow"]
    assert _role_dependency_signals("utility_function", "internal_workflow") == ["utility_calls_workflow"]
    assert _role_dependency_signals("internal_validator", "internal_workflow") == ["validator_calls_workflow"]
    assert _role_dependency_signals("utility_validator", "internal_workflow") == ["validator_calls_workflow"]
    assert _role_dependency_signals("internal_resolver", "internal_workflow") == ["resolver_calls_workflow"]


def test_callable_architecture_layer_rules_and_labels():
    """Verify callable architecture labels and layer rule helpers."""
    import scripts.generate_function_reference as generator

    allowed = [
        ("Public", "Internal", "Allowed"),
        ("Internal", "Internal", "Allowed"),
        ("Public", "Private helper", "Allowed"),
        ("Private helper", "Private helper", "Allowed"),
        ("Public", "Supporting object", "Allowed"),
        ("Internal", "Supporting object", "Allowed"),
    ]
    for caller, callee, result in allowed:
        assert generator._classify_architecture_edge(caller, callee)["result"] == result

    for caller, callee in [("Public", "Public"), ("Internal", "Public")]:
        edge = generator._classify_architecture_edge(caller, callee)
        assert edge == {"result": "Allowed", "violation_type": ""}

    assert set(generator.ARCHITECTURE_WARNING_TYPES) == {"Same-file private dependency"}
    assert set(generator.ARCHITECTURE_VIOLATION_TYPES) == {
        "Public function calls public function",
        "Shared helper calls public function",
        "Cross-file private dependency",
    }

    import scripts.validate_callable_architecture as validator

    assert validator.CALLABLE_FILE_PATTERN == "Public callable file -> domain shared helper -> same-file private helper"
    assert "src/fabricops_kit/io/shared.py" in validator.DOMAIN_SHARED_HELPER_FILES
    assert "src/fabricops_kit/widgets/shared.py" in validator.DOMAIN_SHARED_HELPER_FILES

    assert generator._display_label("Cross-layer dependency") == "Broken rule"
    assert generator._display_label("Deep chain") == "Too many steps"
    assert generator._display_label("Single-use helper candidate") == "Maybe combine"


def test_callable_architecture_validation_rejects_private_visible_rows(monkeypatch, tmp_path) -> None:
    """Verify callable architecture validation fails when private helpers surface."""
    import scripts.validate_callable_architecture as validator

    flow = {
        "function_inventory": [
            {
                "qualified_name": "fabricops_kit.example._private_helper",
                "function_name": "_private_helper",
                "function_type": "Shared helper",
                "layer": "internal",
                "callable_kind": "function",
            }
        ],
        "summary_counts": {
            "function_type": {"Shared helper": 1},
            "layer": {"internal": 1},
            "public_api_surface": {"public_api_entrypoints": 0},
            "callable_inventory_metrics": {"total_callables": 1},
        },
        "public_entrypoint_flow": [],
    }
    dashboard = tmp_path / "dashboard.html"
    inventory = tmp_path / "inventory.html"
    dashboard.write_text("", encoding="utf-8")
    inventory.write_text("", encoding="utf-8")
    monkeypatch.setattr(validator, "DASHBOARD_PATH", dashboard)
    monkeypatch.setattr(validator, "INVENTORY_PATH", inventory)
    monkeypatch.setattr(validator, "_source_failures", lambda: [])

    failures = validator._failures(flow)

    assert any("Private helper is counted as Public/Shared helper" in failure for failure in failures)


def test_callable_architecture_validation_allows_private_helper_review_rows(monkeypatch, tmp_path) -> None:
    """Verify review-only private helpers can appear without affecting architecture counts."""
    import scripts.validate_callable_architecture as validator

    flow = {
        "function_inventory": [
            {
                "qualified_name": "fabricops_kit.example._private_helper",
                "function_name": "_private_helper",
                "function_type": "Private helper",
                "layer": "private_helper",
                "callable_kind": "function",
                "architecture_signals": [],
                "recommended_action": "Keep private helper",
            }
        ],
        "summary_counts": {
            "function_type": {"Public function": 0, "Shared helper": 0},
            "layer": {"public": 0, "internal": 0},
            "public_api_surface": {"public_api_entrypoints": 0, "architecture_violations": 0},
            "callable_inventory_metrics": {"function_callables": 0, "private_helpers_to_review": 1},
        },
        "public_entrypoint_flow": [],
    }
    dashboard = tmp_path / "dashboard.html"
    inventory = tmp_path / "inventory.html"
    dashboard.write_text("Broken rules", encoding="utf-8")
    inventory.write_text("Private helper", encoding="utf-8")
    monkeypatch.setattr(validator, "DASHBOARD_PATH", dashboard)
    monkeypatch.setattr(validator, "INVENTORY_PATH", inventory)
    monkeypatch.setattr(validator, "_source_failures", lambda: [])

    assert validator._failures(flow) == []



def test_callable_architecture_validation_allows_public_config_classes(monkeypatch, tmp_path) -> None:
    """Verify public config classes are visible inventory items but not functions."""
    import scripts.validate_callable_architecture as validator

    public_qn = "fabricops_kit.example.public_api"
    class_qn = "fabricops_kit.config.shared.FabricStore"
    flow = {
        "function_inventory": [
            {
                "qualified_name": public_qn,
                "function_name": "public_api",
                "function_type": "Public function",
                "layer": "public",
                "callable_kind": "function",
            },
            {
                "qualified_name": class_qn,
                "function_name": "FabricStore",
                "function_type": "Public config class",
                "layer": "class",
                "callable_kind": "class",
            },
        ],
        "summary_counts": {
            "function_type": {"Public function": 1, "Shared helper": 0, "Public config class": 1},
            "layer": {"public": 1, "internal": 0},
            "public_api_surface": {"public_api_entrypoints": 1, "architecture_violations": 0},
            "callable_inventory_metrics": {
                "function_callables": 1,
                "private_helpers_to_review": 0,
                "public_classes": 1,
            },
        },
        "public_entrypoint_flow": [
            {"qualified_name": public_qn, "architecture_violation_count": 0, "direct_callees": [], "transitive_callees": []}
        ],
    }
    dashboard = tmp_path / "dashboard.html"
    inventory = tmp_path / "inventory.html"
    dashboard.write_text("Broken rules", encoding="utf-8")
    inventory.write_text("FabricStore Public config class Classes", encoding="utf-8")
    monkeypatch.setattr(validator, "DASHBOARD_PATH", dashboard)
    monkeypatch.setattr(validator, "INVENTORY_PATH", inventory)
    monkeypatch.setattr(validator, "_source_failures", lambda: [])

    assert validator._failures(flow) == []


def test_callable_architecture_validation_rejects_unclassified_supporting_object(monkeypatch, tmp_path) -> None:
    """Verify unsupported non-callable objects still fail generated validation."""
    import scripts.validate_callable_architecture as validator

    flow = {
        "function_inventory": [
            {
                "qualified_name": "fabricops_kit.example.Model",
                "function_name": "Model",
                "function_type": "Supporting object",
                "layer": "supporting_object",
                "callable_kind": "class",
            },
        ],
        "summary_counts": {
            "function_type": {"Public function": 0, "Shared helper": 0, "Supporting object": 1},
            "layer": {"public": 0, "internal": 0},
            "public_api_surface": {"public_api_entrypoints": 0, "architecture_violations": 0},
            "callable_inventory_metrics": {
                "function_callables": 0,
                "private_helpers_to_review": 0,
                "public_classes": 0,
            },
        },
        "public_entrypoint_flow": [],
    }
    dashboard = tmp_path / "dashboard.html"
    inventory = tmp_path / "inventory.html"
    dashboard.write_text("Broken rules", encoding="utf-8")
    inventory.write_text("", encoding="utf-8")
    monkeypatch.setattr(validator, "DASHBOARD_PATH", dashboard)
    monkeypatch.setattr(validator, "INVENTORY_PATH", inventory)
    monkeypatch.setattr(validator, "_source_failures", lambda: [])

    failures = validator._failures(flow)

    assert any("Non Public/Shared helper function type" in failure for failure in failures)
    assert any("Supporting object emitted as architecture inventory row" in failure for failure in failures)

def test_callable_graph_resolves_relative_import_alias_forms() -> None:
    """Verify callable graph resolution handles explicit and module relative imports."""
    import ast

    import scripts.generate_function_reference as generator

    tree = ast.parse(
        "from .shared import get_spark_session\n"
        "from . import shared\n"
        "from .shared import _private_helper\n"
    )
    module_aliases, symbol_aliases = generator.parse_import_aliases(tree.body)
    package_modules = {"io.shared"}

    assert symbol_aliases["get_spark_session"] == ".shared.get_spark_session"
    assert module_aliases["shared"] == ".shared"
    assert symbol_aliases["_private_helper"] == ".shared._private_helper"
    assert generator.resolve_call_target(
        "io.read_lakehouse_csv",
        "get_spark_session",
        module_aliases,
        symbol_aliases,
        set(),
        {},
        package_modules,
    ) == ("fabricops_kit.io.shared.get_spark_session", "cross_module", "shared_helper")
    assert generator.resolve_call_target(
        "io.read_lakehouse_csv",
        "shared.get_spark_session",
        module_aliases,
        symbol_aliases,
        set(),
        {},
        package_modules,
    ) == ("fabricops_kit.io.shared.get_spark_session", "cross_module", "shared_helper")
    assert generator.resolve_call_target(
        "io.read_lakehouse_csv",
        "_private_helper",
        module_aliases,
        symbol_aliases,
        set(),
        {},
        package_modules,
    ) == ("fabricops_kit.io.shared._private_helper", "cross_module", "private_helper")


def test_callable_graph_collects_simple_dispatch_map_function_values() -> None:
    """Verify simple dispatch maps surface callable object values as local calls."""
    import ast

    import scripts.generate_function_reference as generator

    node = ast.parse(
        "def public_entrypoint(kind):\n"
        "    handlers = {'a': helper, 'b': shared.helper}\n"
        "    return handlers[kind]()\n"
    ).body[0]

    calls = generator.collect_function_calls(node)

    assert {"raw_name": "helper", "call_type": "dispatch_map"} in calls
    assert {"raw_name": "shared.helper", "call_type": "dispatch_map"} in calls


def test_callable_architecture_validation_allows_private_helpers_in_public_flow(monkeypatch, tmp_path) -> None:
    """Verify generated validation accepts public flows with visible private helpers."""
    import scripts.validate_callable_architecture as validator

    public_qn = "fabricops_kit.example.public_api"
    first_helper_qn = "fabricops_kit.example._helper"
    second_helper_qn = "fabricops_kit.example._nested_helper"
    flow = {
        "function_inventory": [
            {"qualified_name": public_qn, "function_name": "public_api", "function_type": "Public function", "layer": "public", "callable_kind": "function"},
            {"qualified_name": first_helper_qn, "function_name": "_helper", "function_type": "Private helper", "layer": "private_helper", "callable_kind": "function", "architecture_signals": [], "recommended_action": "Keep private helper"},
            {"qualified_name": second_helper_qn, "function_name": "_nested_helper", "function_type": "Private helper", "layer": "private_helper", "callable_kind": "function", "architecture_signals": [], "recommended_action": "Keep private helper"},
        ],
        "summary_counts": {
            "function_type": {"Public function": 1, "Shared helper": 0},
            "layer": {"public": 1, "internal": 0},
            "public_api_surface": {"public_api_entrypoints": 1, "architecture_violations": 0},
            "callable_inventory_metrics": {"function_callables": 1, "private_helpers_to_review": 2},
        },
        "public_entrypoint_flow": [
            {
                "qualified_name": public_qn,
                "direct_callees": [
                    {"qualified_name": first_helper_qn, "function_name": "_helper", "function_type": "Private helper", "layer": "private_helper", "callee_type": "Private helper", "architecture_result": "Allowed"}
                ],
                "transitive_callees": [
                    {"qualified_name": first_helper_qn, "function_name": "_helper", "function_type": "Private helper", "layer": "private_helper", "callee_type": "Private helper", "parent_qualified_name": public_qn, "architecture_result": "Allowed"},
                    {"qualified_name": second_helper_qn, "function_name": "_nested_helper", "function_type": "Private helper", "layer": "private_helper", "callee_type": "Private helper", "parent_qualified_name": first_helper_qn, "architecture_result": "Allowed"},
                ],
            }
        ],
    }
    dashboard = tmp_path / "dashboard.html"
    inventory = tmp_path / "inventory.html"
    dashboard.write_text("Broken rules", encoding="utf-8")
    inventory.write_text("Private helper", encoding="utf-8")
    monkeypatch.setattr(validator, "DASHBOARD_PATH", dashboard)
    monkeypatch.setattr(validator, "INVENTORY_PATH", inventory)
    monkeypatch.setattr(validator, "_source_failures", lambda: [])

    assert validator._failures(flow) == []


def test_callable_architecture_validation_rejects_supporting_objects_in_public_flow(monkeypatch, tmp_path) -> None:
    """Verify generated validation still rejects supporting objects in public flows."""
    import scripts.validate_callable_architecture as validator

    flow = {
        "function_inventory": [
            {"qualified_name": "fabricops_kit.example.public_api", "function_name": "public_api", "function_type": "Public function", "layer": "public", "callable_kind": "function"},
        ],
        "summary_counts": {
            "function_type": {"Public function": 1, "Shared helper": 0},
            "layer": {"public": 1, "internal": 0},
            "public_api_surface": {"public_api_entrypoints": 1, "architecture_violations": 0},
            "callable_inventory_metrics": {"function_callables": 1, "private_helpers_to_review": 0},
        },
        "public_entrypoint_flow": [
            {
                "qualified_name": "fabricops_kit.example.public_api",
                "direct_callees": [],
                "transitive_callees": [
                    {"qualified_name": "fabricops_kit.example.Model", "function_name": "Model", "function_type": "Supporting object", "layer": "supporting_object", "callee_type": "Supporting object", "architecture_result": "Allowed"}
                ],
            }
        ],
    }
    dashboard = tmp_path / "dashboard.html"
    inventory = tmp_path / "inventory.html"
    dashboard.write_text("Broken rules", encoding="utf-8")
    inventory.write_text("", encoding="utf-8")
    monkeypatch.setattr(validator, "DASHBOARD_PATH", dashboard)
    monkeypatch.setattr(validator, "INVENTORY_PATH", inventory)
    monkeypatch.setattr(validator, "_source_failures", lambda: [])

    failures = validator._failures(flow)

    assert any("Supporting object surfaced in public flow" in failure for failure in failures)
    assert any("Non callable-layer callee type" in failure for failure in failures)



def test_callable_architecture_validation_accepts_new_violation_types(monkeypatch, tmp_path) -> None:
    """Verify generated validation accepts only the PR 723 architecture violation model."""
    import scripts.validate_callable_architecture as validator

    public_qn = "fabricops_kit.example.public_api"
    public_target_qn = "fabricops_kit.example.other_public"
    shared_qn = "fabricops_kit.example.shared_helper"
    private_qn = "fabricops_kit.example._private_helper"
    single_qn = "fabricops_kit.example.single_use_helper"
    nested_qn = "fabricops_kit.example.nested_helper"
    violation_types = list(validator.ALLOWED_ARCHITECTURE_VIOLATION_TYPES)
    flow = {
        "function_inventory": [
            {"qualified_name": public_qn, "function_name": "public_api", "function_type": "Public function", "layer": "public", "callable_kind": "function"},
            {"qualified_name": public_target_qn, "function_name": "other_public", "function_type": "Public function", "layer": "public", "callable_kind": "function"},
            {"qualified_name": shared_qn, "function_name": "shared_helper", "function_type": "Shared helper", "layer": "internal", "callable_kind": "function"},
            {"qualified_name": single_qn, "function_name": "single_use_helper", "function_type": "Shared helper", "layer": "internal", "callable_kind": "function"},
            {"qualified_name": nested_qn, "function_name": "nested_helper", "function_type": "Shared helper", "layer": "internal", "callable_kind": "function"},
            {"qualified_name": private_qn, "function_name": "_private_helper", "function_type": "Private helper", "layer": "private_helper", "callable_kind": "function", "architecture_signals": [], "recommended_action": "Keep private helper"},
        ],
        "summary_counts": {
            "function_type": {"Public function": 2, "Shared helper": 3},
            "layer": {"public": 2, "internal": 3},
            "public_api_surface": {"public_api_entrypoints": 2, "architecture_violations": 1},
            "callable_inventory_metrics": {"function_callables": 5, "private_helpers_to_review": 1},
        },
        "public_entrypoint_flow": [
            {
                "qualified_name": public_qn,
                "architecture_violation_count": len(violation_types),
                "direct_callees": [],
                "transitive_callees": [
                    {"qualified_name": f"{shared_qn}.{index}", "function_name": f"callee_{index}", "function_type": "Shared helper", "layer": "internal", "callee_type": "Shared helper", "architecture_result": "Violation", "violation_type": violation_type}
                    for index, violation_type in enumerate(violation_types)
                ],
            },
            {
                "qualified_name": public_target_qn,
                "architecture_violation_count": 0,
                "direct_callees": [],
                "transitive_callees": [],
            },
        ],
    }
    dashboard = tmp_path / "dashboard.html"
    inventory = tmp_path / "inventory.html"
    dashboard.write_text("Broken rules", encoding="utf-8")
    inventory.write_text("", encoding="utf-8")
    monkeypatch.setattr(validator, "DASHBOARD_PATH", dashboard)
    monkeypatch.setattr(validator, "INVENTORY_PATH", inventory)
    monkeypatch.setattr(validator, "_source_failures", lambda: [])

    assert validator._failures(flow) == []


def test_callable_architecture_validation_rejects_legacy_violation_types(monkeypatch, tmp_path) -> None:
    """Verify legacy Public/Internal boundary wording still fails validation."""
    import scripts.validate_callable_architecture as validator

    public_qn = "fabricops_kit.example.public_api"
    flow = {
        "function_inventory": [
            {"qualified_name": public_qn, "function_name": "public_api", "function_type": "Public function", "layer": "public", "callable_kind": "function"},
        ],
        "summary_counts": {
            "function_type": {"Public function": 1, "Shared helper": 0},
            "layer": {"public": 1, "internal": 0},
            "public_api_surface": {"public_api_entrypoints": 1, "architecture_violations": 1},
            "callable_inventory_metrics": {"function_callables": 1, "private_helpers_to_review": 0},
        },
        "public_entrypoint_flow": [
            {
                "qualified_name": public_qn,
                "architecture_violation_count": 1,
                "direct_callees": [],
                "transitive_callees": [
                    {"qualified_name": "fabricops_kit.example.other_public", "function_name": "other_public", "function_type": "Public function", "layer": "public", "callee_type": "Public", "architecture_result": "Violation", "violation_type": "Public -> Public"},
                ],
            }
        ],
    }
    dashboard = tmp_path / "dashboard.html"
    inventory = tmp_path / "inventory.html"
    dashboard.write_text("Broken rules", encoding="utf-8")
    inventory.write_text("", encoding="utf-8")
    monkeypatch.setattr(validator, "DASHBOARD_PATH", dashboard)
    monkeypatch.setattr(validator, "INVENTORY_PATH", inventory)
    monkeypatch.setattr(validator, "_source_failures", lambda: [])

    failures = validator._failures(flow)

    assert any("Legacy architecture violation type emitted" in failure for failure in failures)

def test_callable_architecture_validation_allows_same_file_private_helper(monkeypatch, tmp_path) -> None:
    """Verify a public owner can call a private helper in the same file."""
    import scripts.validate_callable_architecture as validator

    src = tmp_path / "src" / "fabricops_kit"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text('__all__ = ["public_api"]\nfrom .public_api import public_api\n', encoding="utf-8")
    (src / "public_api.py").write_text('def public_api():\n    return _helper()\n\ndef _helper():\n    return 1\n', encoding="utf-8")
    plan = tmp_path / "plan.json"
    plan.write_text('{"migration_files": {}, "facade_files": ["src/fabricops_kit/__init__.py"]}', encoding="utf-8")
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "SRC_DIR", src)
    monkeypatch.setattr(validator, "OWNERSHIP_PLAN_PATH", plan)

    assert validator._source_failures() == []


def test_callable_architecture_validation_rejects_private_helper_import(monkeypatch, tmp_path) -> None:
    """Verify private helpers cannot be imported outside their owner file."""
    import scripts.validate_callable_architecture as validator

    src = tmp_path / "src" / "fabricops_kit"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text('__all__ = ["public_api"]\nfrom .public_api import public_api\n', encoding="utf-8")
    (src / "public_api.py").write_text('def public_api():\n    return _helper()\n\ndef _helper():\n    return 1\n', encoding="utf-8")
    (src / "other.py").write_text('from fabricops_kit.public_api import _helper\n\ndef internal_use():\n    return _helper()\n', encoding="utf-8")
    plan = tmp_path / "plan.json"
    plan.write_text('{"migration_files": {}, "facade_files": ["src/fabricops_kit/__init__.py"]}', encoding="utf-8")
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "SRC_DIR", src)
    monkeypatch.setattr(validator, "OWNERSHIP_PLAN_PATH", plan)

    failures = validator._source_failures()

    assert any("Private helper imported outside owner file" in failure for failure in failures)
    assert any("Private helper called outside owner file" in failure for failure in failures)


def test_callable_architecture_validation_requires_internal_shared_logic(monkeypatch, tmp_path) -> None:
    """Verify cross-public-file shared logic cannot remain underscore-prefixed."""
    import scripts.validate_callable_architecture as validator

    src = tmp_path / "src" / "fabricops_kit"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text('__all__ = ["public_a", "public_b"]\n', encoding="utf-8")
    (src / "public_a.py").write_text('from fabricops_kit.shared import _shared\n\ndef public_a():\n    return _shared()\n', encoding="utf-8")
    (src / "public_b.py").write_text('from fabricops_kit.shared import _shared\n\ndef public_b():\n    return _shared()\n', encoding="utf-8")
    (src / "shared.py").write_text('def _shared():\n    return 1\n', encoding="utf-8")
    plan = tmp_path / "plan.json"
    plan.write_text('{"migration_files": {}, "facade_files": ["src/fabricops_kit/__init__.py"]}', encoding="utf-8")
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "SRC_DIR", src)
    monkeypatch.setattr(validator, "OWNERSHIP_PLAN_PATH", plan)

    failures = validator._source_failures()

    assert any("Shared helper is underscore-prefixed" in failure for failure in failures)


def test_callable_architecture_validation_rejects_multiple_public_functions_per_file(monkeypatch, tmp_path) -> None:
    """Verify public function owner files expose only one public function."""
    import scripts.validate_callable_architecture as validator

    src = tmp_path / "src" / "fabricops_kit"
    src.mkdir(parents=True)
    (src / "__init__.py").write_text('__all__ = ["public_a", "public_b"]\n', encoding="utf-8")
    (src / "owners.py").write_text('def public_a():\n    return 1\n\ndef public_b():\n    return 2\n', encoding="utf-8")
    plan = tmp_path / "plan.json"
    plan.write_text('{"migration_files": {}, "facade_files": ["src/fabricops_kit/__init__.py"]}', encoding="utf-8")
    monkeypatch.setattr(validator, "ROOT", tmp_path)
    monkeypatch.setattr(validator, "SRC_DIR", src)
    monkeypatch.setattr(validator, "OWNERSHIP_PLAN_PATH", plan)

    failures = validator._source_failures()

    assert any("Public function file contains multiple public functions" in failure for failure in failures)


def test_public_api_surface_records_owner_file_and_private_helper_items() -> None:
    """Verify public flow records expose owner files and private helper review items."""
    import scripts.generate_function_reference as generator

    public_qns = ["fabricops_kit.public_api.public_api"]
    first_helper_qn = "fabricops_kit.public_api._helper"
    second_helper_qn = "fabricops_kit.public_api._nested_helper"
    node_by_qn = {
        "fabricops_kit.public_api.public_api": {"callable_name": "public_api", "module_name": "public_api", "callable_kind": "function", "is_underscore": False},
        first_helper_qn: {"callable_name": "_helper", "module_name": "public_api", "callable_kind": "function", "is_underscore": True},
        second_helper_qn: {"callable_name": "_nested_helper", "module_name": "public_api", "callable_kind": "function", "is_underscore": True},
    }
    calls_by_qn = {
        "fabricops_kit.public_api.public_api": [first_helper_qn],
        first_helper_qn: [second_helper_qn],
        second_helper_qn: [],
    }
    inventory = [
        {"qualified_name": public_qns[0], "function_name": "public_api", "module": "public_api", "layer": "public", "function_type": "Public function", "callable_kind": "function"},
        {"qualified_name": first_helper_qn, "function_name": "_helper", "module": "public_api", "layer": "private_helper", "function_type": "Private helper", "callable_kind": "function", "owner_qualified_name": public_qns[0], "dependency_role": "utility", "used_by_count": 1},
        {"qualified_name": second_helper_qn, "function_name": "_nested_helper", "module": "public_api", "layer": "private_helper", "function_type": "Private helper", "callable_kind": "function", "owner_qualified_name": public_qns[0], "dependency_role": "normalizer", "used_by_count": 1},
    ]

    flows = generator._build_public_entrypoint_flow(public_qns, calls_by_qn, node_by_qn, {}, inventory)
    flow = flows[0]
    transitive_by_qn = {row["qualified_name"]: row for row in flow["transitive_callees"]}

    assert flow["owner_file"] == "src/fabricops_kit/public_api.py"
    assert [item["function_name"] for item in flow["private_helper_review_items"]] == ["_helper", "_nested_helper"]
    assert first_helper_qn in transitive_by_qn
    assert second_helper_qn in transitive_by_qn
    assert [row["qualified_name"] for row in flow["direct_callees"]] == [first_helper_qn]
    assert transitive_by_qn[second_helper_qn]["parent_qualified_name"] == first_helper_qn
    assert flow["downstream_callable_count"] == 2
    assert flow["maximum_chain_depth"] == 2
    assert transitive_by_qn[first_helper_qn]["function_type"] == "Private helper"
    assert transitive_by_qn[first_helper_qn]["layer_group"] == "Private helper"
    assert transitive_by_qn[first_helper_qn]["simple_classification"] == "Private helper"
    assert "dependency_role" not in transitive_by_qn[first_helper_qn]
    assert flow["architecture_violation_count"] == 0
    assert all(row["architecture_result"] == "Warning" for row in flow["transitive_callees"])
    assert {row["violation_type"] for row in flow["transitive_callees"]} == {"Same-file private dependency"}


def test_callable_dashboard_shared_helper_public_function_is_violation() -> None:
    """Verify dashboard architecture rules do not allow shared helpers to call public functions."""
    dashboard_text = (ROOT / "docs" / "assets" / "function-call-graph-dashboard.html").read_text(encoding="utf-8")
    compact_dashboard_text = _remove_whitespace(dashboard_text).replace('"', "'")

    assert "Shared helper calls public function" in dashboard_text
    assert "['Sharedhelper','Publicfunction','Brokenrule']" in compact_dashboard_text
    assert "['Sharedhelper','Publicfunction','Allowed']" not in compact_dashboard_text
    assert "hasArchitectureViolation(flow)&&isGraphReviewCandidate(flow)" not in compact_dashboard_text


def test_callable_dashboard_flow_tree_exports_simple_classification_chips() -> None:
    """Verify dashboard flow rendering uses one simple classification badge."""
    dashboard_text = (ROOT / "docs" / "assets" / "function-call-graph-dashboard.html").read_text(encoding="utf-8")

    assert "Public function" in dashboard_text
    assert "Shared helper" in dashboard_text
    assert "Private helper" in dashboard_text
    compact_dashboard_text = _remove_whitespace(dashboard_text).replace('"', "'")

    assert ("simple_classification:'Publicfunction'" in compact_dashboard_text or 'simple_classification:"Publicfunction"' in compact_dashboard_text)
    assert ("consttype=n.simple_classification||'Unknown'" in compact_dashboard_text or 'consttype=n.simple_classification||"Unknown"' in compact_dashboard_text)
    assert "dependency_role:n.dependency_role||null" not in compact_dashboard_text
    assert "label(n.dependency_role)" not in dashboard_text
    assert "flow-tree-main" in dashboard_text
    assert "flow-tree-details" in dashboard_text
    assert "flow-tree-detail-strip" in dashboard_text
    assert "flow-tree-detail-chip" in dashboard_text
    assert "flow-tree-detail-grid" not in dashboard_text
    assert "flowTreeDetailRows(n)" in dashboard_text
    assert "Called inside this flow by count" not in dashboard_text
    assert "Calls inside this flow count" not in dashboard_text
    assert "Used outside this flow count" not in dashboard_text
    assert "End node status" not in dashboard_text
    assert "Source module" not in dashboard_text
    assert "Called by" in dashboard_text
    assert "Used outside" in dashboard_text
    assert "Maybe combine" in dashboard_text
    assert "Violation reason" in dashboard_text
    assert "Warning reason" in dashboard_text
    assert "Path example" in dashboard_text
    assert "node-signals" not in dashboard_text
    assert "called by count" not in dashboard_text.lower()
    assert "<th>Called by</th>" not in dashboard_text
    assert '<span class="badge muted">${esc(type)}</span>' in dashboard_text
    compact = _remove_whitespace(dashboard_text)
    assert "<spanclass=\"badgemuted\">end</span>" not in compact
    assert "functionflowTreeStatusChips(n)" in compact
    assert "Maybecombine" in compact


def test_global_table_controls_asset_supports_excel_style_table_menus() -> None:
    """Verify the shared table utility exposes site-wide Excel-style table controls."""
    script = (ROOT / "docs" / "javascripts" / "table-controls.js").read_text(encoding="utf-8")
    styles = (ROOT / "docs" / "stylesheets" / "table-controls.css").read_text(encoding="utf-8")
    mkdocs_text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    dashboard_text = (ROOT / "docs" / "assets" / "function-call-graph-dashboard.html").read_text(encoding="utf-8")

    assert "javascripts/table-controls.js" in mkdocs_text
    assert "stylesheets/table-controls.css" in mkdocs_text
    assert "../javascripts/table-controls.js" in dashboard_text
    assert "../stylesheets/table-controls.css" in dashboard_text
    assert 'data-table-controls="excel"' in dashboard_text
    assert "querySelectorAll('table[data-table-controls=\"excel\"]')" in script
    assert "function enhance(table)" in script
    assert "isOptInTable" in script
    assert "fo-table-menu-button" in script
    assert "Sort A to Z" in script
    assert "Sort Z to A" in script
    assert "Sort smallest to largest" in script
    assert "Sort largest to smallest" in script
    assert "Clear sort" in script
    assert "Search values" in script
    assert "Select all" in script
    assert "Value" not in script or "fo-value-list" in script
    assert "Equals" in script
    assert "Greater than" in script
    assert "Less than" in script
    assert "Between" in script
    assert "Clear filter" in script
    assert "Reset column filters" in script
    assert "Clear table filters" not in script
    assert "Clear all filters" not in script
    assert "rowMatchesFilter" in script
    assert "cfg.filters.values" in script
    assert "left.index - right.index" in script
    assert "Number.isFinite" in script
    assert "(blank)" in script
    assert "fo-filter-active" in script
    assert "fo-sort-active" in script
    assert "Escape" in script
    assert "function resetAll" in script
    assert "cfg.filters.clear()" in script
    assert 'querySelectorAll("table").forEach(enhanceTable)' not in script
    assert "@media(max-width:720px)" in styles
    assert "bottom:.5rem!important" in styles



def test_callable_inventory_dashboard_dynamic_table_contract() -> None:
    """Verify inventory dashboard renders dynamic rows, KPIs, statuses, and scoped controls."""
    inventory_text = (ROOT / "docs" / "assets" / "function-call-graph-dashboard.html").read_text(encoding="utf-8")
    compact_inventory_text = _remove_whitespace(inventory_text).replace('"', "'")

    assert "function functionCallGraphDataUrl()" in inventory_text
    assert "constpath=window.location.pathname" in compact_inventory_text
    assert "reference/_data/function-call-graph.json" in inventory_text
    assert "newURL('reference/_data/function-call-graph.json',document.baseURI).href" in compact_inventory_text
    assert "Loading function call graph data..." in inventory_text
    assert "Loaded ${inventory.length} runtime inventory records" in inventory_text
    assert "No function-level code assets found for the current search or column filters." in inventory_text
    assert "No selected function-level code assets. Clear the Selected focus or select visible rows first." not in inventory_text
    assert "Runtime inventory data is missing from function-call-graph.json. Regenerate the function call graph export." in inventory_text
    assert "Failed to load function call graph data. URL:" in inventory_text
    assert "function-call-graph.json" in inventory_text
    assert "updateFunctionCallGraphDataLink(attemptedUrl)" in inventory_text
    assert "Error: ${error&&error.message?error.message:String(error)}" in inventory_text
    assert "did not include a function_inventory array" not in inventory_text
    assert "inventoryDataMissing=true" in compact_inventory_text
    assert "inventory=data.function_inventory" in compact_inventory_text
    assert "function yamlPacket(packet)" in inventory_text
    assert 'id="runtimeInventory_inventorySummaryCards"' in inventory_text
    assert "function canonicalNonFunctionCount()" not in inventory_text
    assert "non_function_records" not in inventory_text
    assert "supporting_objects" not in inventory_text
    assert "supporting_object" not in inventory_text
    assert "nonFunctionCount=canonicalNonFunctionCount()" not in compact_inventory_text
    assert "const ITEM_TYPE_LABELS={public:'Public callable',class:'Classes',internal:'Shared helper',private_helper:'Private helper'}" in inventory_text
    assert '<option value="supporting_object">Non functions</option>' not in inventory_text
    assert "if(state.typeFilter!=='all'&&itemTypeKey(i)!==state.typeFilter)return false" not in inventory_text
    assert "if(state.focusFilter==='actionable'&&state.typeFilter==='all'&&!q&&!supportFocus(i))return false" not in inventory_text
    assert "if(state.focusFilter==='selected'&&state.selected.size===0)return 'No selected function-level code assets. Clear the Selected focus or select visible rows first.'" not in inventory_text
    for label in [
        "Runtime assets",
        "Needs review",
        "Cannot trace back to a public function",
        "Selected for export",
        "All runtime assets",
        "Others / Cannot trace back to a public function",
    ]:
        assert label in inventory_text
    assert 'data-table-controls="excel"' in inventory_text
    assert "max-width:100%;overflow-x:auto" in compact_inventory_text
    assert ".callable-review-table{width:100%;table-layout:auto" in compact_inventory_text
    assert "col-recommended-action" in compact_inventory_text
    assert "col-details" in compact_inventory_text
    assert "details-toggle" in compact_inventory_text
    assert "details-panel" in compact_inventory_text
    assert ".details-row{display:none}" in compact_inventory_text
    assert ".details-row.is-open{display:table-row}" in compact_inventory_text
    assert ".details-panel{max-width:100%;padding:.85rem1rem" in compact_inventory_text
    assert "data-details-toggle" in inventory_text
    assert "detailsRow(i)" in inventory_text
    assert 'colspan="7"' in inventory_text
    assert "<thclass='col-recommended-action'>Recommendedaction</th>" in compact_inventory_text
    assert "<thclass='col-details'>Details</th>" in compact_inventory_text
    assert "<strong>Finding:</strong>" in inventory_text
    assert "<strong>Reason:</strong>" in inventory_text
    assert "<strong>Evidence:</strong>" in inventory_text
    assert "<strong>Notes:</strong>" in inventory_text
    assert "<strong>Cleanup action:</strong>" in inventory_text
    assert "Codebase note" not in inventory_text
    assert "<thclass='col-suggested-action'>Suggestedcleanupaction</th>" not in compact_inventory_text
    assert "<thclass='col-code-role'>Coderole</th>" not in compact_inventory_text
    assert "<thclass='col-flow'>Reachedfrompublicflow</th>" not in compact_inventory_text
    assert "Copy JSON" not in inventory_text
    assert "Download JSON" in inventory_text
    assert "Copy YAML" not in inventory_text
    assert "Download YAML" in inventory_text
    assert "Copy Markdown" not in inventory_text
    assert "function markdownPacket(packet)" not in inventory_text
    assert "function yamlPacket(packet)" in inventory_text
    assert "source_file" in inventory_text
    assert "item_name" in inventory_text
    assert "item_type" in inventory_text
    assert "reachability" in inventory_text
    assert "health" in inventory_text
    assert "recommended_action" in inventory_text
    assert "action_details" in inventory_text
    assert re.search(r"\$\(['\"]inventoryBody['\"]\)\.innerHTML\s*=\s*visibleRows\s*\.map", inventory_text)
    assert re.search(
        r"window\.FabricOpsTableControls\.enhance\(\s*document\.querySelector\(['\"]table\[data-table-controls=\"excel\"\]['\"]\s*,?\s*\)\s*,?\s*\)",
        inventory_text,
    )
    assert "enhanceAll(document)" not in inventory_text


def test_callable_inventory_selected_focus_empty_state_is_removed() -> None:
    """Verify separate Selected focus empty-state copy is removed with dropdown filters."""
    inventory_text = (ROOT / "docs" / "assets" / "function-call-graph-dashboard.html").read_text(encoding="utf-8")

    assert "No selected function-level code assets. Clear the Selected focus or select visible rows first." not in inventory_text
    assert "state.focusFilter==='selected'&&state.selected.size===0" not in inventory_text
    assert "state.focusFilter==='selected'&&!state.selected.has(i.qualified_name)" not in inventory_text


def test_callable_inventory_item_type_counts_match_filter_keys() -> None:
    """Verify item type filter keys match generated function-level inventory records."""
    flow_data = json.loads((ROOT / "docs" / "reference" / "_data" / "function-call-graph.json").read_text(encoding="utf-8"))
    inventory = flow_data["function_inventory"]

    expected_counts = {
        "public": 25,
        "internal": 107,
        "private_helper": 232,
    }
    actual_counts = {key: sum(1 for row in inventory if row["layer"] == key) for key in expected_counts}

    assert actual_counts == expected_counts
    assert any(row.get("reachability") == "unreachable_runtime_asset" for row in inventory)
    assert all(row.get("source_path", "").startswith("src/fabricops_kit/") for row in inventory)
    assert "supporting_object" not in {row["layer"] for row in inventory}
    assert all(row["function_type"] != "Non functions" for row in inventory)

def test_callable_inventory_html_keeps_yaml_newlines_escaped() -> None:
    """Verify inventory YAML helpers emit escaped JavaScript newline strings."""
    inventory_text = (ROOT / "docs" / "assets" / "function-call-graph-dashboard.html").read_text(encoding="utf-8")

    assert "join('\\n')" in inventory_text
    assert "yamlValue(packet)+'\\n'" in inventory_text
    assert "join('\n')" not in inventory_text
    assert "yamlValue(packet)+'\n'" not in inventory_text


def test_callable_inventory_generated_html_smoke_contract() -> None:
    """Verify generated inventory HTML keeps required entrypoints and no broken YAML strings."""
    inventory_text = (ROOT / "docs" / "assets" / "function-call-graph-dashboard.html").read_text(encoding="utf-8")

    assert "function canonicalNonFunctionCount()" not in inventory_text
    assert "function loadData()" in inventory_text
    assert "loadData();" in inventory_text
    assert "join('\n')" not in inventory_text
    assert "yamlValue(packet)+'\n'" not in inventory_text


def test_table_controls_are_opt_in_and_safe_for_dynamic_rows() -> None:
    """Verify table controls stay scoped and refresh existing controls without duplicates."""
    script = (ROOT / "docs" / "javascripts" / "table-controls.js").read_text(encoding="utf-8")

    assert 'table[data-table-controls="excel"]' in script
    assert "if (!isOptInTable(table)) return" in script
    assert "cfg.originalRows = currentRows(table)" in script
    assert 'th.querySelector(":scope > .table-header-cell")' in script
    assert 'headerCell.querySelector(":scope > .fo-table-menu-button")' in script
    assert 'table-header-label' in script
    assert 'filter-trigger' in script
    assert 'querySelectorAll("table")' not in script


def test_global_table_controls_keep_filter_menu_inside_viewport() -> None:
    """Verify right-edge table filter menus are clamped inside the viewport."""
    node_script = """
    const menu = {
      offsetWidth: 256,
      offsetHeight: 240,
      style: {},
      getBoundingClientRect(){ return {width: 256, height: 240}; },
    };
    global.window = {innerWidth: 320, innerHeight: 600};
    global.document = {
      addEventListener(){},
      querySelectorAll(){return []},
      body:{appendChild(){}},
      documentElement:{clientWidth: 320, clientHeight: 600},
    };
    require('./docs/javascripts/table-controls.js');
    const t = window.FabricOpsTableControls._test;
    function assert(condition, message){ if(!condition){ throw new Error(message); } }
    const rightEdgeButton = {getBoundingClientRect(){ return {left: 292, right: 312, bottom: 40}; }};
    t.positionMenu(rightEdgeButton, menu);
    const left = Number.parseFloat(menu.style.left);
    assert(left >= 8, 'menu left is clamped to viewport margin');
    assert(left + 256 <= 312, 'menu flips left from right-edge trigger');
    assert(left + 256 <= 320 - 8, 'menu stays inside right viewport margin');
    assert(menu.style.top === '44px', 'menu keeps the configured side offset below the trigger');
    """
    subprocess.run(["node", "-e", node_script], cwd=ROOT, check=True)

def test_global_table_controls_core_sort_and_filter_helpers() -> None:
    """Exercise shared table utility helpers for sort and filter behavior."""
    node_script = """
    global.window = {};
    global.document = {addEventListener(){}, querySelectorAll(){return []}, body:{appendChild(){}}};
    require('./docs/javascripts/table-controls.js');
    const t = window.FabricOpsTableControls._test;
    function assert(condition, message){ if(!condition){ throw new Error(message); } }
    assert(t.compareValues('Alpha','Beta',false) < 0, 'text sort ascending');
    assert(t.compareValues('Beta','Alpha',false) > 0, 'text sort descending');
    assert(t.compareValues('2','10',true) < 0, 'numeric sort ascending');
    assert(t.compareValues('10','2',true) > 0, 'numeric sort descending');
    assert(t.displayValue('') === '(blank)', 'blank value filtering');
    const row = {cells:[{textContent:'Healthy'}, {textContent:'7'}, {textContent:''}, {textContent:'Public'}]};
    assert(t.rowMatchesFilter(row,{column:0,kind:'values',values:new Set(['Healthy'])}), 'value checkbox filtering');
    assert(t.rowMatchesFilter(row,{column:1,kind:'numeric',operator:'greater',a:'5'}), 'numeric condition filtering');
    assert(t.rowMatchesFilter(row,{column:1,kind:'numeric',operator:'between',a:'5',b:'8'}), 'numeric between filtering');
    assert(t.rowMatchesFilter(row,{column:2,kind:'values',values:new Set(['(blank)'])}), 'blank value filtering');
    assert(t.rowMatchesFilter(row,{column:3,kind:'values',values:new Set(['Public'])}) && t.rowMatchesFilter(row,{column:0,kind:'values',values:new Set(['Healthy'])}), 'multiple column filters AND logic');
    """
    subprocess.run(["node", "-e", node_script], cwd=ROOT, check=True)


def _flow_test_inventory_row(qn: str, name: str, module: str, layer: str, *, owner: str | None = None, used_by_count: int = 1) -> dict[str, object]:
    """Return a minimal callable-flow inventory row for architecture tests."""
    function_type = {
        "public": "Public function",
        "internal": "Shared helper",
        "private_helper": "Private helper",
    }[layer]
    row: dict[str, object] = {
        "qualified_name": qn,
        "function_name": name,
        "module": module,
        "layer": layer,
        "function_type": function_type,
        "callable_kind": "function",
        "used_by_count": used_by_count,
        "call_site_count": 1,
        "recursive": False,
        "repeated_within_single_caller": False,
        "signals": [],
    }
    if owner:
        row["owner_qualified_name"] = owner
    return row


def test_refactor_inventory_distinguishes_single_repeated_recursive_and_heavy_helpers() -> None:
    """Verify helper cleanup suggestions use call-site-aware labels."""
    import scripts.generate_function_reference as generator

    public_qn = "fabricops_kit.alpha.public_alpha"
    public_b = "fabricops_kit.beta.public_beta"
    public_c = "fabricops_kit.gamma.public_gamma"
    public_d = "fabricops_kit.delta.public_delta"
    public_e = "fabricops_kit.epsilon.public_epsilon"
    public_f = "fabricops_kit.zeta.public_zeta"
    once = "fabricops_kit.alpha._once_helper"
    repeated = "fabricops_kit.alpha._repeated_helper"
    recursive = "fabricops_kit.alpha._recursive_helper"
    heavy = "fabricops_kit.shared._shared_helper"
    qns = [public_qn, public_b, public_c, public_d, public_e, public_f, once, repeated, recursive, heavy]
    node_by_qn = {
        qn: {
            "callable_name": qn.rsplit(".", 1)[1],
            "module_name": qn.rsplit(".", 1)[0].replace("fabricops_kit.", ""),
            "callable_kind": "function",
        }
        for qn in qns
    }
    calls_by_qn = {
        public_qn: [once, repeated, repeated, recursive, heavy],
        public_b: [heavy],
        public_c: [heavy],
        public_d: [heavy],
        public_e: [heavy],
        public_f: [heavy],
        once: [],
        repeated: [],
        recursive: [recursive],
        heavy: [],
    }

    _, inventory, _ = generator._build_refactor_inventory(
        [public_qn, public_b, public_c, public_d, public_e, public_f],
        [],
        calls_by_qn,
        node_by_qn,
        {},
    )
    by_qn = {row["qualified_name"]: row for row in inventory}

    assert by_qn[once]["call_site_count"] == 1
    assert by_qn[once]["recursive"] is False
    assert "Maybe combine" in by_qn[once]["signals"]
    assert "Used by one function" in by_qn[once]["signals"]
    assert by_qn[repeated]["call_site_count"] == 2
    assert by_qn[repeated]["repeated_within_single_caller"] is True
    assert "Used several times in one function" in by_qn[repeated]["signals"]
    assert "Maybe combine" not in by_qn[repeated]["signals"]
    assert by_qn[recursive]["recursive"] is True
    assert "Recursive helper" in by_qn[recursive]["signals"]
    assert "Maybe combine" not in by_qn[recursive]["signals"]
    assert by_qn[heavy]["inbound_count"] == 6
    assert "Heavily used helper" in by_qn[heavy]["signals"]

def test_callable_flow_allows_two_layer_local_private_and_shared_internal_calls() -> None:
    """Verify allowed public/private/shared-internal paths are not architecture findings."""
    import scripts.generate_function_reference as generator

    public_qn = "fabricops_kit.alpha.public_alpha"
    private_qn = "fabricops_kit.alpha._local_helper"
    nested_private_qn = "fabricops_kit.alpha._nested_local_helper"
    shared_qn = "fabricops_kit.shared.shared_helper"
    other_public_qn = "fabricops_kit.beta.public_beta"
    node_by_qn = {
        public_qn: {"callable_name": "public_alpha", "module_name": "alpha", "callable_kind": "function"},
        private_qn: {"callable_name": "_local_helper", "module_name": "alpha", "callable_kind": "function"},
        nested_private_qn: {"callable_name": "_nested_local_helper", "module_name": "alpha", "callable_kind": "function"},
        shared_qn: {"callable_name": "shared_helper", "module_name": "shared", "callable_kind": "function"},
        other_public_qn: {"callable_name": "public_beta", "module_name": "beta", "callable_kind": "function"},
    }
    calls_by_qn = {
        public_qn: [private_qn, shared_qn],
        private_qn: [nested_private_qn, shared_qn],
        nested_private_qn: [],
        shared_qn: [],
        other_public_qn: [shared_qn],
    }
    inventory = [
        _flow_test_inventory_row(public_qn, "public_alpha", "alpha", "public"),
        _flow_test_inventory_row(other_public_qn, "public_beta", "beta", "public"),
        _flow_test_inventory_row(private_qn, "_local_helper", "alpha", "private_helper", owner=public_qn),
        _flow_test_inventory_row(nested_private_qn, "_nested_local_helper", "alpha", "private_helper", owner=public_qn),
        _flow_test_inventory_row(shared_qn, "shared_helper", "shared", "internal", used_by_count=2),
    ]

    flow = generator._build_public_entrypoint_flow([public_qn, other_public_qn], calls_by_qn, node_by_qn, {}, inventory)[0]

    assert flow["architecture_violation_count"] == 0
    rows = {row["qualified_name"]: row for row in flow["transitive_callees"]}
    assert rows[private_qn]["architecture_result"] == "Warning"
    assert rows[private_qn]["violation_type"] == "Same-file private dependency"
    assert rows[nested_private_qn]["architecture_result"] == "Warning"
    assert rows[shared_qn]["architecture_result"] == "Allowed"


def test_callable_flow_allows_single_use_internal_helper_cleanup_candidate() -> None:
    """Verify single-use shared/internal helpers are cleanup candidates, not violations."""
    import scripts.generate_function_reference as generator

    public_qn = "fabricops_kit.alpha.public_alpha"
    internal_qn = "fabricops_kit.shared.single_use_helper"
    node_by_qn = {
        public_qn: {"callable_name": "public_alpha", "module_name": "alpha", "callable_kind": "function"},
        internal_qn: {"callable_name": "single_use_helper", "module_name": "shared", "callable_kind": "function"},
    }
    calls_by_qn = {public_qn: [internal_qn], internal_qn: []}
    inventory = [
        _flow_test_inventory_row(public_qn, "public_alpha", "alpha", "public"),
        _flow_test_inventory_row(internal_qn, "single_use_helper", "shared", "internal", used_by_count=1),
    ]

    flow = generator._build_public_entrypoint_flow([public_qn], calls_by_qn, node_by_qn, {}, inventory)[0]
    row = flow["transitive_callees"][0]

    assert flow["architecture_violation_count"] == 0
    assert row["architecture_result"] == "Allowed"
    assert row["violation_type"] == ""
    assert row["helper_cleanup_candidate"] is True


def test_callable_flow_flags_nested_internal_helper_chain_violation() -> None:
    """Verify hidden internal/private chains beneath public callables are findings."""
    import scripts.generate_function_reference as generator

    public_qn = "fabricops_kit.guardrails.run_table_guardrails"
    workflow_qn = "fabricops_kit.guardrails._run_table_guardrails_workflow"
    core_qn = "fabricops_kit.profiling.profile_dataframe_core"
    private_core_qn = "fabricops_kit.profiling._profile_dataframe_core"
    distribution_qn = "fabricops_kit.profiling.build_distribution_summaries"
    categorical_qn = "fabricops_kit.profiling.build_categorical_distribution"
    other_public_qn = "fabricops_kit.other.other_public"
    node_by_qn = {
        public_qn: {"callable_name": "run_table_guardrails", "module_name": "guardrails", "callable_kind": "function"},
        other_public_qn: {"callable_name": "other_public", "module_name": "other", "callable_kind": "function"},
        workflow_qn: {"callable_name": "_run_table_guardrails_workflow", "module_name": "guardrails", "callable_kind": "function"},
        core_qn: {"callable_name": "profile_dataframe_core", "module_name": "profiling", "callable_kind": "function"},
        private_core_qn: {"callable_name": "_profile_dataframe_core", "module_name": "profiling", "callable_kind": "function"},
        distribution_qn: {"callable_name": "build_distribution_summaries", "module_name": "profiling", "callable_kind": "function"},
        categorical_qn: {"callable_name": "build_categorical_distribution", "module_name": "profiling", "callable_kind": "function"},
    }
    calls_by_qn = {
        public_qn: [workflow_qn],
        workflow_qn: [core_qn],
        core_qn: [private_core_qn],
        private_core_qn: [distribution_qn],
        distribution_qn: [categorical_qn],
        categorical_qn: [],
        other_public_qn: [core_qn],
    }
    inventory = [
        _flow_test_inventory_row(public_qn, "run_table_guardrails", "guardrails", "public"),
        _flow_test_inventory_row(other_public_qn, "other_public", "other", "public"),
        _flow_test_inventory_row(workflow_qn, "_run_table_guardrails_workflow", "guardrails", "private_helper", owner=public_qn),
        _flow_test_inventory_row(core_qn, "profile_dataframe_core", "profiling", "internal", used_by_count=2),
        _flow_test_inventory_row(private_core_qn, "_profile_dataframe_core", "profiling", "private_helper", owner=core_qn),
        _flow_test_inventory_row(distribution_qn, "build_distribution_summaries", "profiling", "private_helper", owner=core_qn),
        _flow_test_inventory_row(categorical_qn, "build_categorical_distribution", "profiling", "internal", used_by_count=1),
    ]

    flow = generator._build_public_entrypoint_flow([public_qn, other_public_qn], calls_by_qn, node_by_qn, {}, inventory)[0]
    rows = {row["qualified_name"]: row for row in flow["transitive_callees"]}

    assert flow["architecture_violation_count"] == 0
    assert rows[private_core_qn]["architecture_result"] == "Warning"
    assert rows[private_core_qn]["violation_type"] == "Same-file private dependency"
    assert rows[distribution_qn]["architecture_result"] == "Warning"
    assert rows[distribution_qn]["violation_type"] == "Same-file private dependency"


def test_callable_flow_flags_private_helper_reused_across_public_callables() -> None:
    """Verify reused private helpers are findings instead of hidden shared dependencies."""
    import scripts.generate_function_reference as generator

    public_a = "fabricops_kit.alpha.public_alpha"
    public_b = "fabricops_kit.beta.public_beta"
    private_qn = "fabricops_kit.alpha._shared_private"
    node_by_qn = {
        public_a: {"callable_name": "public_alpha", "module_name": "alpha", "callable_kind": "function"},
        public_b: {"callable_name": "public_beta", "module_name": "beta", "callable_kind": "function"},
        private_qn: {"callable_name": "_shared_private", "module_name": "alpha", "callable_kind": "function"},
    }
    calls_by_qn = {public_a: [private_qn], public_b: [private_qn], private_qn: []}
    inventory = [
        _flow_test_inventory_row(public_a, "public_alpha", "alpha", "public"),
        _flow_test_inventory_row(public_b, "public_beta", "beta", "public"),
        _flow_test_inventory_row(private_qn, "_shared_private", "alpha", "private_helper", owner=public_a),
    ]

    flows = generator._build_public_entrypoint_flow([public_a, public_b], calls_by_qn, node_by_qn, {}, inventory)

    rows_by_flow = [{row["qualified_name"]: row for row in flow["transitive_callees"]} for flow in flows]

    assert [flow["architecture_violation_count"] for flow in flows] == [0, 1]
    assert rows_by_flow[0][private_qn]["architecture_result"] == "Warning"
    assert rows_by_flow[0][private_qn]["violation_type"] == "Same-file private dependency"
    assert rows_by_flow[1][private_qn]["architecture_result"] == "Violation"
    assert rows_by_flow[1][private_qn]["violation_type"] == "Cross-file private dependency"


def test_callable_flow_ignores_call_graph_self_edges() -> None:
    """Verify self-edges do not render as normal caller relationships."""
    import scripts.generate_function_reference as generator

    public_qn = "fabricops_kit.alpha.public_alpha"
    other_public_qn = "fabricops_kit.other.other_public"
    helper_qn = "fabricops_kit.shared.shared_helper"
    node_by_qn = {
        public_qn: {"callable_name": "public_alpha", "module_name": "alpha", "callable_kind": "function"},
        other_public_qn: {"callable_name": "other_public", "module_name": "other", "callable_kind": "function"},
        helper_qn: {"callable_name": "shared_helper", "module_name": "shared", "callable_kind": "function"},
    }
    calls_by_qn = {public_qn: [helper_qn], other_public_qn: [helper_qn], helper_qn: [helper_qn]}
    inventory = [
        _flow_test_inventory_row(public_qn, "public_alpha", "alpha", "public"),
        _flow_test_inventory_row(other_public_qn, "other_public", "other", "public"),
        _flow_test_inventory_row(helper_qn, "shared_helper", "shared", "internal", used_by_count=2),
    ]

    flow = generator._build_public_entrypoint_flow([public_qn, other_public_qn], calls_by_qn, node_by_qn, {}, inventory)[0]

    assert [row["qualified_name"] for row in flow["transitive_callees"]] == [helper_qn]
    assert flow["transitive_callees"][0]["parent_qualified_name"] == public_qn


def test_callable_flow_generated_docs_hide_fine_grained_taxonomy_badges() -> None:
    """Verify generated callable-flow docs do not render maintainer taxonomy badges."""
    dashboard_text = (ROOT / "docs" / "assets" / "function-call-graph-dashboard.html").read_text(encoding="utf-8")
    callable_flow_text = (REFERENCE_DIR / "function-call-graph.md").read_text(encoding="utf-8")
    banned_labels = [
        "Public Api",
        "Internal Resolver",
        "Utility Function",
        "Internal Workflow",
        "Internal Adapter",
        "Utility Validator",
        "Audit Time Utility",
    ]

    for label_text in banned_labels:
        assert label_text not in dashboard_text
        assert label_text not in callable_flow_text


def test_callable_flow_simple_classification_detects_shared_internal_reuse() -> None:
    """Verify shared internal helpers are identified from reuse across public callables."""
    import scripts.generate_function_reference as generator

    public_a = "fabricops_kit.alpha.public_alpha"
    public_b = "fabricops_kit.beta.public_beta"
    shared_qn = "fabricops_kit.shared.shared_helper"
    single_qn = "fabricops_kit.shared.single_use_helper"
    node_by_qn = {
        public_a: {"callable_name": "public_alpha", "module_name": "alpha", "callable_kind": "function"},
        public_b: {"callable_name": "public_beta", "module_name": "beta", "callable_kind": "function"},
        shared_qn: {"callable_name": "shared_helper", "module_name": "shared", "callable_kind": "function"},
        single_qn: {"callable_name": "single_use_helper", "module_name": "shared", "callable_kind": "function"},
    }
    calls_by_qn = {public_a: [shared_qn, single_qn], public_b: [shared_qn], shared_qn: [], single_qn: []}
    inventory = [
        _flow_test_inventory_row(public_a, "public_alpha", "alpha", "public"),
        _flow_test_inventory_row(public_b, "public_beta", "beta", "public"),
        _flow_test_inventory_row(shared_qn, "shared_helper", "shared", "internal", used_by_count=2),
        _flow_test_inventory_row(single_qn, "single_use_helper", "shared", "internal", used_by_count=1),
    ]

    flow = generator._build_public_entrypoint_flow([public_a, public_b], calls_by_qn, node_by_qn, {}, inventory)[0]
    rows = {row["qualified_name"]: row for row in flow["transitive_callees"]}

    assert rows[shared_qn]["simple_classification"] == "Shared helper"
    assert rows[shared_qn]["architecture_result"] == "Allowed"
    assert rows[single_qn]["simple_classification"] == "Unknown"
    assert rows[single_qn]["violation_type"] == ""
    assert rows[shared_qn]["called_inside_flow_by"] == 1
    assert rows[shared_qn]["calls_inside_flow"] == 0
    assert rows[shared_qn]["used_outside_flow"] == 1
    assert rows[shared_qn]["is_end_node"] is True
    assert flow["external_dependents_count"] == 1


def test_callable_flow_private_helper_containment_uses_owner_file() -> None:
    """Verify private helper containment is based on the owning public callable."""
    import scripts.generate_function_reference as generator

    public_a = "fabricops_kit.alpha.public_alpha"
    public_b = "fabricops_kit.beta.public_beta"
    private_a = "fabricops_kit.alpha._private_alpha"
    node_by_qn = {
        public_a: {"callable_name": "public_alpha", "module_name": "alpha", "callable_kind": "function"},
        public_b: {"callable_name": "public_beta", "module_name": "beta", "callable_kind": "function"},
        private_a: {"callable_name": "_private_alpha", "module_name": "alpha", "callable_kind": "function"},
    }
    calls_by_qn = {public_a: [private_a], public_b: [private_a], private_a: []}
    inventory = [
        _flow_test_inventory_row(public_a, "public_alpha", "alpha", "public"),
        _flow_test_inventory_row(public_b, "public_beta", "beta", "public"),
        _flow_test_inventory_row(private_a, "_private_alpha", "alpha", "private_helper", owner=public_a),
    ]

    flows = generator._build_public_entrypoint_flow([public_a, public_b], calls_by_qn, node_by_qn, {}, inventory)
    rows_by_flow = [{row["qualified_name"]: row for row in flow["transitive_callees"]} for flow in flows]

    assert rows_by_flow[0][private_a]["simple_classification"] == "Private helper"
    assert rows_by_flow[0][private_a]["architecture_result"] == "Warning"
    assert rows_by_flow[0][private_a]["violation_type"] == "Same-file private dependency"
    assert rows_by_flow[0][private_a]["used_outside_flow"] == 1
    assert rows_by_flow[1][private_a]["simple_classification"] == "Private helper"
    assert rows_by_flow[1][private_a]["architecture_result"] == "Violation"
    assert rows_by_flow[1][private_a]["violation_type"] == "Cross-file private dependency"
