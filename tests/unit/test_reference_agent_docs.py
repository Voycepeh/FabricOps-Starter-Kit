"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import ast
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).parents[2]
REFERENCE_DIR = ROOT / "docs" / "reference"
REFERENCE_INDEX = REFERENCE_DIR / "index.md"
API_REFERENCE_DIR = ROOT / "docs" / "api" / "reference"
PLACEHOLDER = "Not documented yet"
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
    assert "</strong><span> public callables</span><!-- /FABRICOPS_PUBLIC_FUNCTION_COUNT -->" in index_text
    assert "FABRICOPS_CALLABLE_RECORD_COUNT" in index_text
    assert "Callable metrics are generated from the callable inventory data." in index_text
    assert "283 supporting internal functions" not in index_text
    assert "supporting internal functions" not in index_text

    expected = {
        "FABRICOPS_PUBLIC_FUNCTION_COUNT": f"{stats['public_function_count']} public callables",
        "FABRICOPS_CALLABLE_RECORD_COUNT": (
            f"Supported by {stats['supporting_function_count']} functions and "
            f"{stats['non_function_record_count']} non-function records"
        ),
        "FABRICOPS_METADATA_TABLE_COUNT": f"{stats['metadata_table_count']} metadata tables",
    }

    for token_name, expected_text in expected.items():
        assert " ".join(_landing_token_text(index_text, token_name)) == expected_text


def test_landing_stats_match_reference_sources() -> None:
    """Verify generated landing stats are derived from canonical reference sources."""
    stats = json.loads((REFERENCE_DIR / "_data" / "landing-stats.json").read_text(encoding="utf-8"))
    callable_flow = json.loads((REFERENCE_DIR / "_data" / "callable-flow.json").read_text(encoding="utf-8"))
    metadata_pages = sorted((REFERENCE_DIR / "metadata").glob("*.md"))

    summary_counts = callable_flow["summary_counts"]
    assert stats["public_function_count"] == summary_counts["public_api_surface"]["public_api_entrypoints"]
    assert stats["total_callable_records"] == summary_counts["total_callables"]
    metrics = summary_counts["callable_inventory_metrics"]
    assert stats["function_callable_count"] == summary_counts["callable_kind"]["function"]
    assert stats["supporting_function_count"] == metrics["supporting_functions"]
    assert stats["non_function_record_count"] == metrics["non_function_records"]
    assert stats["metadata_table_count"] == len(metadata_pages)


def test_generated_callable_surface_matches_all_exports() -> None:
    """Verify generated callable entries come from package __all__."""
    exported_symbols = set(_exported_symbols())
    removed_symbols = {
        "enforce_dq_rules",
        "get_selected_agreement",
        "widget_select_agreement",
    }
    automation_manifest = json.loads((REFERENCE_DIR / "_data" / "automation-manifest.json").read_text(encoding="utf-8"))
    function_manifest = json.loads((REFERENCE_DIR / "_data" / "function-manifest.json").read_text(encoding="utf-8"))
    callable_flow = json.loads((REFERENCE_DIR / "_data" / "callable-flow.json").read_text(encoding="utf-8"))

    automation_callables = {entry["name"] for entry in automation_manifest if entry.get("type") == "callable"}
    function_callables = {
        entry["name"]
        for entry in function_manifest
        if entry.get("classification") == "Callable" and entry.get("docs_path", "").startswith("api/reference/")
    }
    page_callables = {path.stem for path in API_REFERENCE_DIR.glob("*.md")}

    assert automation_callables == exported_symbols
    assert function_callables == exported_symbols
    assert page_callables == exported_symbols
    public_inventory = {row["function_name"] for row in callable_flow["function_inventory"] if row["layer"] == "public"}
    assert public_inventory == exported_symbols
    assert not (removed_symbols & automation_callables)
    assert not (removed_symbols & function_callables)
    assert not (removed_symbols & page_callables)
    assert not (removed_symbols & public_inventory)


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
    callable_flow = REFERENCE_DIR / "_data" / "callable-flow.json"

    assert automation_manifest.exists()
    assert function_manifest.exists()
    assert refactor_signals.exists()
    assert callable_flow.exists()
    assert json.loads(automation_manifest.read_text(encoding="utf-8"))
    assert json.loads(function_manifest.read_text(encoding="utf-8"))
    assert json.loads(refactor_signals.read_text(encoding="utf-8"))
    assert json.loads(callable_flow.read_text(encoding="utf-8"))


def test_callable_flow_page_and_json_cover_public_surface() -> None:
    """Verify global callable flow docs and structured metadata are generated."""
    flow_page = REFERENCE_DIR / "callable-flow.md"
    flow_data_path = REFERENCE_DIR / "_data" / "callable-flow.json"
    dashboard_path = ROOT / "docs" / "assets" / "callable-functions-dashboard.html"
    exported_symbols = set(_exported_symbols())

    assert flow_page.exists()
    assert dashboard_path.exists()
    flow_text = flow_page.read_text(encoding="utf-8")
    assert "# Callable Flow Dashboard" in flow_text
    assert "## Why callable flow matters" in flow_text
    assert "## How the dashboard is generated" in flow_text
    assert "## Refactor signals" in flow_text
    assert "## Exporting an AI refactor prompt" in flow_text
    assert "[Architecture](../assets/callable-functions-dashboard.html)" in flow_text
    assert "[Inventory](../assets/callable-functions-inventory.html)" in flow_text
    assert "## Callable helper summary" not in flow_text
    assert "## Internal helper nesting inventory" not in flow_text
    assert '<div class="callable-flow-table-wrap" markdown="0">' not in flow_text
    assert "refactor reason" not in flow_text.lower()

    inventory_path = ROOT / "docs" / "assets" / "callable-functions-inventory.html"
    assert dashboard_path.exists()
    assert inventory_path.exists()
    dashboard_text = dashboard_path.read_text(encoding="utf-8")
    inventory_text = inventory_path.read_text(encoding="utf-8")
    reference_text = (REFERENCE_DIR / "index.md").read_text(encoding="utf-8")

    assert "Callable Architecture" in dashboard_text
    assert "High-level triage for notebook-facing public APIs, dependency depth, and architecture risk." in dashboard_text
    assert "Inventory" in dashboard_text
    assert "Decision mode: Public API Surface" in dashboard_text
    assert "publicSurfaceCards" in dashboard_text
    assert "publicCallableList" in dashboard_text
    assert "publicFlowDetails" in dashboard_text
    assert "buildFlowTree" in dashboard_text
    assert "callable-functions-inventory.html" in dashboard_text
    assert "data-public-flow" in dashboard_text
    assert 'href="${esc(flow.source_url' not in dashboard_text
    assert '<button type=\"button\" class=\"callable-button\" data-public-flow=\"${esc(f.qualified_name)}\"' in dashboard_text
    assert 'data-public-flow=\"${esc(f.qualified_name)}\"' in dashboard_text
    assert "decisionSearchBox" in dashboard_text
    assert "decisionModuleFilter" in dashboard_text
    assert "decisionRecommendationFilter" in dashboard_text
    assert "decisionWarningFilter" in dashboard_text
    assert "decisionMinDownstream" in dashboard_text
    assert "decisionMinDepth" in dashboard_text
    assert "Architecture finding count" in dashboard_text
    assert "Architecture violation count<select" not in dashboard_text
    assert '<option value="">All modules</option>' in dashboard_text
    assert '<option value="">All recommendations</option>' in dashboard_text
    assert '<option value="">All findings</option>' in dashboard_text
    assert '<select id="decisionMinDownstream"><option value="">All downstream counts</option></select>' in dashboard_text
    assert '<select id="decisionMinDepth"><option value="">All call depths</option></select>' in dashboard_text
    assert 'Architecture finding count<select id="decisionMinIssues"><option value="">All architecture findings</option></select>' in dashboard_text
    assert 'id="decisionMinDownstream" type="number"' not in dashboard_text
    assert 'id="decisionMinDepth" type="number"' not in dashboard_text
    assert 'id="decisionMinIssues" type="number"' not in dashboard_text
    assert "Architecture violation type<input" not in dashboard_text
    assert "resetDecisionFilters" in dashboard_text
    assert "compactList" in dashboard_text
    assert "compactBadges" in dashboard_text
    assert "<details class=\"inline-more\">" in dashboard_text
    assert "+${hidden.length} more" in dashboard_text
    assert "showAllPublicCallables" in dashboard_text
    assert "collapsedPublicList" in dashboard_text
    assert "scrollIntoView" in dashboard_text
    assert "Callable flow" in dashboard_text
    assert "Showing flow for" in dashboard_text
    assert "callable-flow-filter-banner" in dashboard_text
    assert "justify-content:space-between" in dashboard_text
    assert "callable-flow-reset-button" in dashboard_text
    assert "background:#15803d" in dashboard_text
    assert "Back to all public callables" in dashboard_text
    assert "showSelectedBanner=Boolean(state.collapsedPublicList&&active)" in dashboard_text
    assert 'id="backToAllPublicCallables"' in dashboard_text
    assert "reset.onclick=showAllPublicCallables" in dashboard_text
    assert "showAllPublicCallablesInline" not in dashboard_text
    assert "Show all public callables</button>`:'';const inline" not in dashboard_text
    assert ".surface-card strong{display:block;margin-bottom:.25rem;line-height:1" in dashboard_text
    assert ".surface-card span{display:block;line-height:1.2" in dashboard_text
    assert "<th>Public callable</th><th>Owner file</th><th>Module</th><th>Findings</th><th>Why review</th><th>Suggested action</th><th class=\"num\">Downstream</th><th class=\"num\">Depth</th>" in dashboard_text
    assert dashboard_text.index('id=\"selectedCount\"') < dashboard_text.index('id=\"publicFlowDetails\"')
    assert "Copy JSON" in dashboard_text
    assert "Copy Markdown" in dashboard_text
    assert "Download JSON" in dashboard_text
    assert "compatibilityMode" in dashboard_text
    assert "COMPATIBILITY_INSTRUCTIONS" in dashboard_text
    assert "function callableMarkdown(item)" in dashboard_text
    assert "function markdownPacket(packet)" in dashboard_text
    assert "Objective" in dashboard_text
    assert "Architecture intent" in dashboard_text
    assert "Compatibility mode" in dashboard_text
    assert "toolbar-card-grid" in dashboard_text
    assert "toolbar-card--selection" in dashboard_text
    assert "toolbar-card--compatibility" in dashboard_text
    assert "toolbar-card--prompt" in dashboard_text
    assert "toolbar-row--top" not in dashboard_text
    assert "Selected callables" in dashboard_text
    assert "Requested work" in dashboard_text
    assert "Output required from AI" in dashboard_text
    assert "Batch accounting" in dashboard_text
    assert "downstream_count" in dashboard_text
    assert "max_depth" in dashboard_text
    assert "modules_touched" in dashboard_text
    assert "architecture_violation_count" in dashboard_text
    assert "boundary_violations" not in dashboard_text
    assert "architecture_findings" in dashboard_text
    assert "flow_tree" in dashboard_text
    assert "internal_helper_cleanup_candidates" in dashboard_text
    assert "public_callable_findings" in dashboard_text
    assert "merge_shortening_candidate_count" in dashboard_text
    assert "planning_instructions" in dashboard_text
    assert "required_tests" in dashboard_text
    assert "function publicCallableFindingRows(flow)" in dashboard_text
    assert "publicFindings=publicCallableFindingRows(f)" in dashboard_text
    assert "#### Public callable findings" in dashboard_text
    assert "#### Architecture findings" in dashboard_text
    assert "#### Internal helper cleanup candidates" in dashboard_text
    assert "#### Full nested flow tree" in dashboard_text
    assert "helper_tags" in dashboard_text
    assert "Group functions by refactor action before proposing code changes." in dashboard_text
    assert "Identify helpers that can be merged into parent callables and helpers that should remain separate." in dashboard_text
    assert "Preserve public API behavior and avoid changing notebook-facing callable signatures unless compatibility mode explicitly allows it." in dashboard_text
    assert "Use public callable findings, architecture violation rows, internal helper cleanup candidates, and flow tree tags as grounding evidence." in dashboard_text
    assert "Propose an ordered implementation plan, list tests required before and after refactor, and call out migration risks." in dashboard_text
    assert "final_output_required" in dashboard_text
    assert "## Final output required" in dashboard_text
    assert "Write the final output as instructions that can be pasted into Codex, Claude Code, Cursor, or another coding agent." in dashboard_text
    assert "Produce a PR execution plan for a coding agent targeting the main branch." in dashboard_text
    assert "Preserve public API behavior and avoid changing notebook-facing callable signatures unless compatibility mode allows it." in dashboard_text
    assert "Group refactor actions by helper/function." in dashboard_text
    assert "Identify architecture violations to address." in dashboard_text
    assert "Identify helpers to merge, move, or keep." in dashboard_text
    assert "List implementation steps in order." in dashboard_text
    assert "List tests to add, update, and run." in dashboard_text
    assert "Define acceptance criteria." in dashboard_text
    assert "Call out risks and rollback notes." in dashboard_text
    assert "Do not write code yet and do not generate a patch." in dashboard_text
    assert dashboard_text.index("## Final output required") > dashboard_text.index("## Batch accounting")
    assert "Do not write code yet and do not generate a patch.\n`;" in dashboard_text
    assert "source_url:row.source_url||null" in dashboard_text
    assert "docs_url:row.docs_url||null" in dashboard_text
    assert "file_path:row.source_path||null" in dashboard_text
    assert "line_start:row.source_start_line||null" in dashboard_text
    assert "function moduleLink(module)" in dashboard_text
    assert "function moduleHref(module){return module?`../api/modules/${module}/`:''}" in dashboard_text
    assert "../../api/modules/${module}/" not in dashboard_text
    assert "GITHUB_SOURCE_BASE" in dashboard_text
    assert "return `${GITHUB_SOURCE_BASE}${path}${anchor}`" in dashboard_text
    assert "architectureViolationFlows=flows.filter" in dashboard_text
    assert "shortenableFlowCount=flows.filter" in dashboard_text
    assert "function architectureFindingRows(flow)" in dashboard_text
    assert "function architectureFindingCount(flow)" in dashboard_text
    assert "c.architecture_result==='Violation'||c.recommended_action==='Architecture violation'" in dashboard_text
    assert "function markdownLink(i,label)" in dashboard_text
    assert "cross_layer_issue_count" not in dashboard_text
    assert "direct callees" in dashboard_text
    assert "disabled>Copy JSON" in dashboard_text
    assert "disabled>Copy Markdown" in dashboard_text
    assert "disabled>Download JSON" in dashboard_text
    assert "location.reload" not in dashboard_text
    assert "decisionSearch:''" in dashboard_text
    assert "decisionDownstreamBand:''" in dashboard_text
    assert "const DOWNSTREAM_BANDS=" in dashboard_text
    assert "['downstream_0','0',v=>v===0]" in dashboard_text
    assert "['downstream_1_2','1–2',v=>v>=1&&v<=2]" in dashboard_text
    assert "['downstream_3_5','3–5',v=>v>=3&&v<=5]" in dashboard_text
    assert "['downstream_6_10','6–10',v=>v>=6&&v<=10]" in dashboard_text
    assert "['downstream_gt_10','>10',v=>v>10]" in dashboard_text
    assert "const DEPTH_BANDS=" in dashboard_text
    assert "['depth_0_1','0–1',v=>v>=0&&v<=1]" in dashboard_text
    assert "['depth_2_3','2–3',v=>v>=2&&v<=3]" in dashboard_text
    assert "['depth_4_5','4–5',v=>v>=4&&v<=5]" in dashboard_text
    assert "['depth_gte_6','>=6',v=>v>=6]" in dashboard_text
    assert "const ISSUE_BANDS=" in dashboard_text
    assert "['issues_0','No violations',v=>v===0]" in dashboard_text
    assert "['issues_1','1 violation',v=>v===1]" in dashboard_text
    assert "['issues_gte_2','2+ violations',v=>v>=2]" in dashboard_text
    assert "const ISSUE_BOOLEAN_BANDS=" in dashboard_text
    assert "['issues_gte_1','1+ violations',v=>v>=1]" in dashboard_text
    assert "function architectureViolationCount(flow)" in dashboard_text
    assert "if(typeof value==='boolean')return value?1:0" in dashboard_text
    assert "function issueBandsForRows(rows)" in dashboard_text
    assert "?ISSUE_BANDS:ISSUE_BOOLEAN_BANDS" in dashboard_text
    assert "function matchesBand(flow,bandValue,bands,metric)" in dashboard_text
    assert "function populateBandFilter(id,bands,rows,metric)" in dashboard_text
    assert "matchesBand(f,state.decisionDownstreamBand,DOWNSTREAM_BANDS,'downstream')" in dashboard_text
    assert "matchesBand(f,state.decisionDepthBand,DEPTH_BANDS,'depth')" in dashboard_text
    assert "matchesBand(f,state.decisionIssueBand,issueBandsForRows(publicEntryFlows),'issues')" in dashboard_text
    assert "['decisionMinDownstream','decisionDownstreamBand']" in dashboard_text
    assert "decisionDownstreamBand:'',decisionDepthBand:'',decisionIssueBand:'',collapsedPublicList:false" in dashboard_text
    assert "populateBandFilter('decisionMinDownstream',DOWNSTREAM_BANDS,publicEntryFlows,'downstream')" in dashboard_text
    assert "populateBandFilter('decisionMinDepth',DEPTH_BANDS,publicEntryFlows,'depth')" in dashboard_text
    assert "populateBandFilter('decisionMinIssues',issueBandsForRows(publicEntryFlows),publicEntryFlows,'issues')" in dashboard_text
    assert "function numericFilterValue(value)" not in dashboard_text
    assert "Number(e.target.value||0)" not in dashboard_text
    card_order = [
        dashboard_text.index("label:'Public callables scanned'"),
        dashboard_text.index("label:'High-priority public callables'"),
        dashboard_text.index("label:'Architecture violations'"),
        dashboard_text.index("label:'Long public flows'"),
        dashboard_text.index("label:'Public flows that can be shortened'"),
    ]
    assert card_order == sorted(card_order)
    assert "Notebook-facing APIs included in this decision view." in dashboard_text
    assert "Public APIs to review first." in dashboard_text
    assert "Public callable flows with architecture violations." in dashboard_text
    assert "Public callable flows whose depth exceeds the threshold." in dashboard_text
    assert "Public callable flows with internal helpers that may be simplified, merged, or moved closer to their caller." in dashboard_text
    assert "Clean public flows" not in dashboard_text
    assert "Public flows with warnings" not in dashboard_text
    assert "Callables flagged as single-use helper candidates" not in dashboard_text
    assert "label:'Merge candidates'" not in dashboard_text
    assert "value:s.merge_candidates" not in dashboard_text
    assert "305 Merge candidates" not in dashboard_text
    assert "Architecture metrics summarize public entrypoint flow risk. Use Inventory for helper-level cleanup details." in dashboard_text
    assert "Review detailed callable actions in Inventory" not in dashboard_text
    assert "architecture-cta" not in dashboard_text

    assert "dataLoadStatus" in dashboard_text
    assert "function callableFlowDataUrl()" in dashboard_text
    assert "referenceMarker='/reference/'" in dashboard_text
    assert "assetsMarker='/assets/'" in dashboard_text
    assert "+'_data/callable-flow.json'" in dashboard_text
    assert "+'reference/_data/callable-flow.json'" in dashboard_text
    assert "new URL('reference/_data/callable-flow.json',document.baseURI).href" in dashboard_text
    assert "Failed to load callable-flow data. Attempted URL:" in dashboard_text
    assert "HTTP status:" in dashboard_text
    assert "Error message:" in dashboard_text
    assert "function renderLoadedCount()" in dashboard_text
    assert "total callables; ${publicEntryFlows.length} public callables available; ${visibleFlows.length} rows after filters" in dashboard_text
    assert "renderLoadedCount();$('publicCallableList').innerHTML" in dashboard_text
    assert "architectureThresholds=data.architecture_thresholds||architectureThresholds" in dashboard_text
    assert "function longCallChainThreshold()" in dashboard_text
    assert "function largeDependencySurfaceThreshold()" in dashboard_text
    assert "long_call_chain_depth:null" in dashboard_text
    assert "large_dependency_surface:null" in dashboard_text
    assert "function positiveThreshold(value)" in dashboard_text
    assert "Number.isFinite(numeric)&&numeric>0?numeric:null" in dashboard_text
    assert "architecture_violation_count??0" in dashboard_text
    assert "down>=12" not in dashboard_text
    assert "Architecture violation: ${esc(n.violation_type)}" in dashboard_text
    assert "Helper-level architecture findings found" in dashboard_text
    assert "architectureFindings.length?architectureFindings" in dashboard_text
    assert "function whyReview(flow)" in dashboard_text
    assert "reasons.join(' ')" in dashboard_text
    assert "Contains ${violations} architecture violations." in dashboard_text
    assert "Depth is ${flow.max_depth}; threshold is >= ${longThreshold}." in dashboard_text
    assert "Has ${flow.downstream_count} downstream functions; threshold is >= ${largeThreshold}." in dashboard_text
    assert "Depth; long call chain threshold >= ${longThreshold}" in dashboard_text
    assert "longThreshold!==null" in dashboard_text
    assert "largeThreshold!==null" in dashboard_text
    assert "long call chain threshold unavailable" in dashboard_text
    assert "Contains ${flow.helper_cleanup_candidates} merge candidates inside this flow." in dashboard_text
    assert "deep cross-module helper chains" not in dashboard_text
    assert "inline single-use helper" not in dashboard_text

    assert "Callable Inventory" in inventory_text
    assert "Search/filter callables with maintainer-friendly role groups, reachability, and refactor signals." in inventory_text
    assert "Architecture" in inventory_text
    assert "callable-functions-dashboard.html" in inventory_text
    assert "inventorySummaryCards" in inventory_text
    assert "function renderInventoryCards()" in inventory_text
    assert "Modules" in inventory_text
    assert "Total callables" in inventory_text
    assert "Public API" in inventory_text
    assert "Supporting functions" in inventory_text
    assert "Private helpers to review" in inventory_text
    assert "Complete discovered callable inventory." in inventory_text
    assert "Internal functions behind the public API." in inventory_text
    assert "callable_inventory_metrics" in inventory_text
    assert "deep cross-module helper chains" not in inventory_text
    assert "inline single-use helper" not in inventory_text
    assert "Total discovered callable records" not in inventory_text
    assert "Function callables" not in inventory_text
    assert "Non-function callable records" not in inventory_text
    assert '<article class="surface-card ${esc(c.cls)}">' in inventory_text
    assert ".surface-card strong{display:block;margin-bottom:.25rem;line-height:1;font-size:1.45rem}" in inventory_text
    assert ".surface-card span{display:block;line-height:1.2;font-weight:700}" in inventory_text
    assert "function sourceCallableLink(i)" in inventory_text
    assert "class=\"source-link\" href=\"${esc(href)}\"" in inventory_text
    assert "if(i.source_url)return i.source_url" in inventory_text
    assert "const start=i.source_start_line" in inventory_text
    assert "#L${start}" in inventory_text
    assert "GITHUB_SOURCE_BASE" in inventory_text
    assert "Showing ${visibleRows.length} callable records of ${total} total discovered callable records." in inventory_text
    assert "Showing ${visibleRows.length} of ${inventory.length} discovered callables" not in inventory_text
    assert "Callable metrics are generated from the callable inventory data." in inventory_text
    assert "<td>${sourceCallableLink(i)}</td>" in inventory_text
    assert "data-select-row" in inventory_text
    assert "selectAllVisible" in inventory_text
    assert "copyJson" in inventory_text
    assert "copyMarkdown" in inventory_text
    assert "downloadJson" in inventory_text
    assert "searchBox" in inventory_text
    assert "moduleFilter" in inventory_text
    assert "roleGroupFilter" in inventory_text
    assert "reachabilityFilter" in inventory_text
    assert "signalFilter" in inventory_text
    assert "priorityFilter" in inventory_text
    assert "Advanced / Debug filters" in inventory_text
    assert "callableRoleFilter" in inventory_text
    assert "dependencyRoleFilter" in inventory_text
    assert "kindFilter" in inventory_text
    assert "typeFilter" in inventory_text
    assert "reviewStatusFilter" in inventory_text
    assert "minInboundFilter" in inventory_text
    assert "minOutboundFilter" in inventory_text
    assert "selectedCount" in inventory_text
    assert "compatibilityMode" in inventory_text
    assert "Select visible" in inventory_text
    assert "Clear selection" in inventory_text
    assert "Copy JSON" in inventory_text
    assert "Copy Markdown" in inventory_text
    assert "Download JSON" in inventory_text
    assert "selectedItems" in inventory_text
    assert "refactorPacket" in inventory_text
    assert "copyExport" in inventory_text
    assert "downloadJson" in inventory_text
    assert "COMPATIBILITY_INSTRUCTIONS" in inventory_text
    assert "function callableMarkdown(item)" in inventory_text
    assert "function markdownPacket(packet)" in inventory_text
    assert "Objective" in inventory_text
    assert "Architecture intent" in inventory_text
    assert "Compatibility mode" in inventory_text
    assert "toolbar-card-grid" in inventory_text
    assert "toolbar-card--selection" in inventory_text
    assert "toolbar-card--compatibility" in inventory_text
    assert "toolbar-card--prompt" in inventory_text
    assert "toolbar-row--top" not in inventory_text
    assert "Selected callables" in inventory_text
    assert "Requested work" in inventory_text
    assert "Output required from AI" in inventory_text
    assert "Batch accounting" in inventory_text
    assert "disabled>Copy JSON" in inventory_text
    assert "disabled>Copy Markdown" in inventory_text
    assert "disabled>Download JSON" in inventory_text
    assert "selectAllVisible" in inventory_text
    assert "$('selectAllVisible').onchange" in inventory_text
    assert "ROLE_GROUP_FILTER_OPTIONS" in inventory_text
    for role_group_label in [
        "Public entrypoint",
        "Workflow",
        "Resolver",
        "Normalizer",
        "Validator",
        "Adapter",
        "Utility",
        "Model class",
        "Registry builder",
        "Lifecycle method",
        "Property method",
        "Other",
    ]:
        assert role_group_label in inventory_text
    signal_options = inventory_text.split("const USER_FACING_RECOMMENDED_ACTIONS=", 1)[1].split(";", 1)[0]
    assert "Public API entrypoint" not in signal_options
    assert "Priority is generated from callable inventory signals, architecture findings" in inventory_text
    assert "strongest review/refactor signal; inspect first" in inventory_text
    assert "Findings / Signal" in inventory_text
    assert "Role group" in inventory_text
    assert "Role detail" in inventory_text
    assert "Suggested action" in inventory_text
    assert "Inbound" in inventory_text
    assert "Outbound" in inventory_text
    assert "Dependency role" in inventory_text
    assert "Kind / Layer" in inventory_text
    assert "<th>Debug details</th>" not in inventory_text
    assert "function debugCell" not in inventory_text
    assert "DISPLAY_LABEL_MAP" in inventory_text
    assert "tag,.badge" in inventory_text
    assert "priority-high" in inventory_text
    assert ".badge.issue" in inventory_text
    assert "displayLabel(i.recommended_action)" in inventory_text
    assert '<span class="reference-kpi-title">Modules</span>' in reference_text
    assert '<span class="reference-kpi-title">Total callables</span>' in reference_text
    assert '<span class="reference-kpi-title">Public API</span>' in reference_text
    assert '<span class="reference-kpi-title">Supporting functions</span>' in reference_text
    assert '<span class="reference-kpi-title">Private helpers to review</span>' in reference_text
    assert '<strong class="reference-kpi-value">21</strong>' in reference_text
    assert '<strong class="reference-kpi-value">303</strong>' in reference_text
    assert '<strong class="reference-kpi-value">26</strong>' in reference_text
    assert '<strong class="reference-kpi-value">50</strong>' in reference_text
    assert '<strong class="reference-kpi-value">227</strong>' in reference_text
    assert "Callable metrics are generated from the callable inventory data." in reference_text
    assert "270 Supporting internal functions" not in reference_text
    assert "Supporting internal functions" not in reference_text.split("## Find a function", 1)[0]

    home_text = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")
    assert "assets/callable-functions-dashboard.html" in home_text
    assert "assets/callable-functions-inventory.html" in home_text
    assert "Architecture" in home_text
    assert "Inventory" in home_text
    assert "High-level triage for notebook-facing public APIs, dependency depth, and architecture boundary risk." not in home_text or "Architecture" in home_text
    assert "Search/filter all callables, select rows, and export AI refactor packets." in home_text

    maintainer_text = (REFERENCE_DIR / "maintainer-guide.md").read_text(encoding="utf-8")
    assert "[Architecture](../assets/callable-functions-dashboard.html)" in maintainer_text
    assert "[Inventory](../assets/callable-functions-inventory.html)" in maintainer_text

    flow_data = json.loads(flow_data_path.read_text(encoding="utf-8"))
    assert set(flow_data) == {"function_inventory", "public_entrypoint_flow", "summary_counts", "architecture_thresholds"}
    assert flow_data["architecture_thresholds"] == {"long_call_chain_depth": 4, "large_dependency_surface": 10}

    summary_counts = flow_data["summary_counts"]
    assert {
        "total_callables",
        "function_type",
        "layer",
        "review_status",
        "callable_kind",
        "recommended_action",
        "callable_inventory_metrics",
        "callable_role_group",
    } <= set(summary_counts)
    assert set(summary_counts["function_type"]) == {"Public function", "Internal function"}
    assert set(summary_counts["review_status"]) == {
        "classified",
        "classification_pending",
        "implicit_lifecycle",
        "property_accessor",
        "unreachable",
    }
    assert summary_counts["layer"]["public"] == len(exported_symbols)
    assert summary_counts["callable_inventory_metrics"]["function_callables"] == sum(summary_counts["function_type"].values())
    assert summary_counts["callable_role_group"]

    public_api_surface = summary_counts["public_api_surface"]
    assert summary_counts["total_callables"] == len(flow_data["function_inventory"])
    assert summary_counts["callable_kind"]["function"] == 76
    assert summary_counts["private_helper_review"] == flow_data["summary_counts"]["callable_inventory_metrics"]["private_helpers_to_review"]
    assert flow_data["summary_counts"]["callable_inventory_metrics"]["non_function_records"] == 22
    assert flow_data["summary_counts"]["callable_inventory_metrics"]["hidden_private_helpers"] > 0
    assert {
        "public_api_entrypoints",
        "long_call_chains",
        "architecture_violations",
        "merge_candidates",
        "suggested_inline_or_privatize",
    } <= set(public_api_surface)


    public_flows = flow_data["public_entrypoint_flow"]
    assert len(public_flows) == summary_counts["layer"]["public"]
    assert len(public_flows) == public_api_surface["public_api_entrypoints"]
    assert public_api_surface["architecture_violations"] == sum(
        1 for flow in public_flows if flow["architecture_violation_count"]
    )
    assert public_api_surface["merge_candidates"] == sum(
        1 for flow in public_flows if flow["helper_cleanup_candidates"]
    )
    assert public_api_surface["merge_candidates"] < sum(
        flow["helper_cleanup_candidates"] for flow in public_flows
    )
    for flow in public_flows:
        assert "owner_file" in flow
        assert "private_helper_review_items" in flow
        assert "max_depth" in flow
        assert "downstream_count" in flow
        assert "children" not in flow
        for callee in [*flow["direct_callees"], *flow["transitive_callees"]]:
            assert "depth" in callee
            assert "parent_qualified_name" in callee
            assert "children" not in callee
            assert len(callee.get("path_examples", [])) <= 3
            assert "helper_cleanup_candidate" in callee

    function_inventory = flow_data["function_inventory"]
    assert len(function_inventory) == summary_counts["total_callables"]
    assert all(row["callable_role_group"] for row in function_inventory)
    assert all(row["callable_role_group_label"] for row in function_inventory)
    assert summary_counts["callable_role_group"] == {
        role_group: sum(1 for row in function_inventory if row["callable_role_group"] == role_group)
        for role_group in sorted({row["callable_role_group"] for row in function_inventory})
    }
    assert {row["qualified_name"] for row in function_inventory}
    assert len({row["qualified_name"] for row in function_inventory}) == len(function_inventory)
    assert {"Public function", "Internal function"} <= {row["function_type"] for row in function_inventory}
    assert {"classified", "classification_pending"} <= {
        row["review_status"] for row in function_inventory
    }
    assert sum(1 for row in function_inventory if row["layer"] == "public") == summary_counts["layer"]["public"]
    assert sum(1 for row in function_inventory if row["layer"] == "internal") == summary_counts["layer"]["internal"]
    assert summary_counts["review_status"]["unreachable"] == 0
    assert {row["function_name"] for row in function_inventory if row["layer"] == "public"} == exported_symbols
    assert summary_counts["recommended_action"] == {
        action: sum(1 for row in function_inventory if row["recommended_action"] == action)
        for action in sorted({row["recommended_action"] for row in function_inventory})
    }
    assert all(row["recommended_action"] for row in function_inventory)
    assert any(
        row["function_type"] == "Internal function"
        and row["called_by_count"] <= 1
        and "Possible inline/private helper" in row["signals"]
        for row in function_inventory
    )
    private_helper_rows = [row for row in function_inventory if row["layer"] == "private_helper"]
    assert private_helper_rows
    assert all(row["function_type"] == "Private helper" for row in private_helper_rows)
    assert all(row["function_name"].split(".")[-1].startswith("_") for row in private_helper_rows)
    assert all(row["architecture_signals"] == [] for row in private_helper_rows)
    assert all(row["owner_function"] or row["usage_scope"] == "unused" for row in private_helper_rows)
    assert all(row["owner_file"] for row in private_helper_rows)
    assert any(row["leaks_outside_owner_file"] for row in private_helper_rows)
    assert {"Keep private helper", "Merge into owner", "Rename to internal function", "Move closer to owner", "Remove redundant wrapper"} & {row["recommended_action"] for row in private_helper_rows}
    assert sum(1 for row in function_inventory if row["function_type"] == "Public function") == summary_counts["function_type"]["Public function"]
    assert sum(1 for row in function_inventory if row["function_type"] == "Internal function") == summary_counts["function_type"]["Internal function"]
    assert all(not callee["function_name"].split(".")[-1].startswith("_") for flow in public_flows for callee in flow["transitive_callees"])
    rows_by_qn = {row["qualified_name"]: row for row in function_inventory}
    assert "fabricops_kit.config.FrameworkConfig" not in rows_by_qn
    assert "fabricops_kit.io_core.FabricStore.root" not in rows_by_qn
    assert all(row["reachability_kind"] == "public_entrypoint" for row in function_inventory if row["layer"] == "public")
    assert all(row["review_status"] != "unreachable" for row in function_inventory)
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
        "reachability_kind",
        "reachability_label",
        "recommended_action",
        "priority",
        "signals",
        "called_by_count",
        "calls_count",
        "callers",
        "callees",
    }
    public_inventory_keys = expected_inventory_keys | {"docs_path", "docs_url"}
    assert all(set(item) == expected_inventory_keys or set(item) == public_inventory_keys for item in function_inventory)
    assert all({"function_type", "layer", "dependency_role", "callable_kind"} <= set(item) for item in function_inventory)

    callable_flow_text = (REFERENCE_DIR / "callable-flow.md").read_text(encoding="utf-8")
    assert "Public functions → Internal functions (supporting objects allowed)" in callable_flow_text
    assert "Public callables → Internal helpers → Utility callables" not in callable_flow_text
    assert "callable may call lower layers, but not the same layer or higher layers" not in callable_flow_text
    assert "Callable review is function-layer focused" in callable_flow_text
    assert "Internal-to-internal calls are valid" in callable_flow_text
    assert "Role group = broad job of the callable." in callable_flow_text
    assert "Findings / Signal = review hints or actions, not automatic refactor commands." in callable_flow_text
    assert "Priority = triage order, not a guarantee something must be changed." in callable_flow_text
    assert "compact dashboard contract data" in callable_flow_text
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
        "downstream_count",
        "max_depth",
        "modules_touched",
        "architecture_violation_count",
        "architecture_violation_breakdown",
        "helper_cleanup_candidates",
        "direct_callees",
        "transitive_callees",
        "private_helper_review_items",
    }
    expected_callee_keys = {
        "qualified_name",
        "function_name",
        "module",
        "depth",
        "function_type",
        "layer",
        "layer_group",
        "dependency_role",
        "edge_type",
        "parent_qualified_name",
        "caller_type",
        "callee_type",
        "architecture_result",
        "violation_type",
        "signals",
        "recommended_action",
        "downstream_count",
        "source_path",
        "source_url",
        "source_start_line",
        "source_end_line",
        "docs_path",
        "docs_url",
        "path_examples",
        "helper_cleanup_candidate",
    }
    assert all(set(flow) == expected_public_flow_keys for flow in public_flows)
    required_callee_keys = expected_callee_keys - {"docs_path", "docs_url"}
    assert all(required_callee_keys <= set(callee) <= expected_callee_keys for flow in public_flows for callee in flow["transitive_callees"])


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
        assert "Public Starter Kit function" in text, page
        assert "Module: <code>" in text, page
        assert "## Relationships" not in text, page
        assert "## Maintainer/developer implementation details" not in text, page
        assert "## Source link" not in text, page
        assert '??? example "Source code"' not in text, page
        assert '??? example "View helper source by area"' not in text, page
        assert '<div class="reference-source-card" markdown="1">' not in text, page
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
        assert '??? info "Internal helpers used:' not in text, page
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


def test_callable_pages_hide_source_cards_from_public_reference() -> None:
    """Verify callable pages hide source cards from the public reference."""
    callable_pages = sorted(API_REFERENCE_DIR.glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "## Source link" not in text, page
        assert '<div class="reference-source-card" markdown="1">' not in text, page
        assert "View on GitHub" not in text, page
        assert "Source file path:" not in text, page
        assert "GitHub source URL:" not in text, page


def test_display_guardrail_results_uses_one_clickable_call_tree() -> None:
    """Verify display guardrail results renders one linked helper call tree."""
    text = (API_REFERENCE_DIR / "display_guardrail_results.md").read_text(encoding="utf-8")
    implementation_section = text.split("## See also", 1)[0]

    assert text.count('??? info "Downstream callables: 2"') == 1
    assert "Dependency data is generated from the callable architecture inventory." in implementation_section
    assert '??? example "View helper source by area"' not in implementation_section
    assert '??? example "Source code"' not in implementation_section
    assert "Internal helper count: 11" not in text
    assert 'class="reference-helper-groups"' not in implementation_section
    assert re.search(
        r'href="https://github\.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline\.py#L\d+(?:-L\d+)?"',
        implementation_section,
    )

    for helper_name in ["build_guardrail_detail_rows", "build_guardrail_summary_rows"]:
        assert f"><code>{helper_name}(...)</code></a>" in implementation_section
    assert "_guardrail_reason" not in implementation_section


def test_display_guardrail_results_lists_nested_private_helpers() -> None:
    """Verify nested private helpers appear in callable helper chips."""
    text = (API_REFERENCE_DIR / "display_guardrail_results.md").read_text(encoding="utf-8")
    implementation_section = text.split("## See also", 1)[0]

    assert implementation_section.count('??? info "Downstream callables: 2"') == 1
    assert '??? info "Internal helpers used:' not in implementation_section
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
    assert "_guardrail_reason" not in implementation_section


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
    callable_flow = json.loads((REFERENCE_DIR / "_data" / "callable-flow.json").read_text(encoding="utf-8"))
    flow = next(
        item
        for item in callable_flow["public_entrypoint_flow"]
        if item["function_name"] == "display_guardrail_results"
    )
    reference_index = REFERENCE_INDEX.read_text(encoding="utf-8")
    detail_page = (API_REFERENCE_DIR / "display_guardrail_results.md").read_text(encoding="utf-8")

    assert flow["downstream_count"] == 2
    assert 'data-callable-name="display_guardrail_results"' in reference_index
    assert "Downstream callables: 2" in reference_index
    assert '??? info "Downstream callables: 2"' in detail_page
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
    chips_index = text.index('<span class="reference-chip">Module: <code>pipeline</code></span>')
    usage_index = text.index("**Used in notebooks:** `02_pipeline`")

    assert title_index < description_index < chips_index < usage_index
    assert '??? info "Downstream callables:' not in text


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


def test_module_badges_pluralize_external_module_counts() -> None:
    """Verify module overview badges use singular labels for one external module."""
    module_text = (ROOT / "docs" / "api" / "modules" / "guardrails.md").read_text(encoding="utf-8")

    assert "Used by 1 external module" in module_text
    assert "Used by 1 external modules" not in module_text
    assert "Uses 3 external modules" in module_text


def test_setup_notebook_reference_uses_human_first_source_documentation() -> None:
    """Verify setup notebook reference uses human first source documentation."""
    text = (API_REFERENCE_DIR / "setup_notebook.md").read_text(encoding="utf-8")

    assert "../../api/modules/config/#setup_notebook" not in text
    assert "View on GitHub" not in text
    assert text.count('<div class="reference-source-card" markdown="1">') == 0
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

    assert public_names
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
    assert generated_pages == public_names


def test_generated_manifests_point_public_callables_to_canonical_api_reference() -> None:
    """Verify generated manifests point public callables to canonical api reference."""
    function_manifest = json.loads((REFERENCE_DIR / "_data" / "function-manifest.json").read_text(encoding="utf-8"))
    automation_manifest = json.loads((REFERENCE_DIR / "_data" / "automation-manifest.json").read_text(encoding="utf-8"))

    for entry in function_manifest:
        if entry.get("classification") == "Callable":
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
    assert "      - Callable Functions Flow: reference/callable-flow.md" in mkdocs_text
    assert "      - Implementation Appendix:" in mkdocs_text
    assert "      # AUTO-GENERATED-MODULES-END" in mkdocs_text
    assert "api/modules/config.md" in mkdocs_text
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
        ("Public", "Supporting object", "Allowed"),
        ("Internal", "Supporting object", "Allowed"),
    ]
    for caller, callee, result in allowed:
        assert generator._classify_architecture_edge(caller, callee)["result"] == result

    for caller, callee in [("Public", "Public"), ("Internal", "Public")]:
        edge = generator._classify_architecture_edge(caller, callee)
        assert edge["result"] == "Violation"
        assert edge["violation_type"] == f"{caller} -> {callee}"

    assert generator._display_label("Cross-layer dependency") == "Architecture violation"
    assert generator._display_label("Deep chain") == "Long call chain"
    assert generator._display_label("Single-use helper candidate") == "Merge candidate"


def test_callable_architecture_validation_rejects_private_visible_rows(monkeypatch, tmp_path) -> None:
    """Verify callable architecture validation fails when private helpers surface."""
    import scripts.validate_callable_architecture as validator

    flow = {
        "function_inventory": [
            {
                "qualified_name": "fabricops_kit.example._private_helper",
                "function_name": "_private_helper",
                "function_type": "Internal function",
                "layer": "internal",
                "callable_kind": "function",
            }
        ],
        "summary_counts": {
            "function_type": {"Internal function": 1},
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

    assert any("Private helper is counted as Public/Internal" in failure for failure in failures)


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
            "function_type": {"Public function": 0, "Internal function": 0},
            "layer": {"public": 0, "internal": 0},
            "public_api_surface": {"public_api_entrypoints": 0, "architecture_violations": 0},
            "callable_inventory_metrics": {"function_callables": 0, "private_helpers_to_review": 1},
        },
        "public_entrypoint_flow": [],
    }
    dashboard = tmp_path / "dashboard.html"
    inventory = tmp_path / "inventory.html"
    dashboard.write_text("Architecture violations", encoding="utf-8")
    inventory.write_text("Private helper", encoding="utf-8")
    monkeypatch.setattr(validator, "DASHBOARD_PATH", dashboard)
    monkeypatch.setattr(validator, "INVENTORY_PATH", inventory)
    monkeypatch.setattr(validator, "_source_failures", lambda: [])

    assert validator._failures(flow) == []


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
    node_by_qn = {
        "fabricops_kit.public_api.public_api": {"callable_name": "public_api", "module_name": "public_api", "callable_kind": "function", "is_underscore": False},
        "fabricops_kit.public_api._helper": {"callable_name": "_helper", "module_name": "public_api", "callable_kind": "function", "is_underscore": True},
    }
    calls_by_qn = {"fabricops_kit.public_api.public_api": ["fabricops_kit.public_api._helper"], "fabricops_kit.public_api._helper": []}
    inventory = [
        {"qualified_name": public_qns[0], "function_name": "public_api", "module": "public_api", "layer": "public", "function_type": "Public function", "callable_kind": "function"},
        {"qualified_name": "fabricops_kit.public_api._helper", "function_name": "_helper", "module": "public_api", "layer": "private_helper", "function_type": "Private helper", "callable_kind": "function", "owner_qualified_name": public_qns[0]},
    ]

    flows = generator._build_public_entrypoint_flow(public_qns, calls_by_qn, node_by_qn, {}, inventory)

    assert flows[0]["owner_file"] == "src/fabricops_kit/public_api.py"
    assert [item["function_name"] for item in flows[0]["private_helper_review_items"]] == ["_helper"]
