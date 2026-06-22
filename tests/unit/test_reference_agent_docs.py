"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import ast
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
    "read_data",
    "write_data",
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
    return page_text.split(start, 1)[1].split(end, 1)[0]


def test_landing_page_counts_match_generated_stats() -> None:
    """Verify landing-page count text cannot drift from generated data."""
    stats = json.loads((REFERENCE_DIR / "_data" / "landing-stats.json").read_text(encoding="utf-8"))
    index_text = (ROOT / "docs" / "index.md").read_text(encoding="utf-8")

    expected = {
        "FABRICOPS_PUBLIC_FUNCTION_COUNT": f"{stats['public_function_count']} public Starter Kit functions",
        "FABRICOPS_INTERNAL_FUNCTION_COUNT": f"{stats['supporting_internal_function_count']} supporting internal functions",
        "FABRICOPS_METADATA_TABLE_COUNT": f"{stats['metadata_table_count']} metadata tables",
    }

    for token_name, expected_text in expected.items():
        assert _landing_token_text(index_text, token_name) == expected_text


def test_landing_stats_match_reference_sources() -> None:
    """Verify generated landing stats are derived from canonical reference sources."""
    stats = json.loads((REFERENCE_DIR / "_data" / "landing-stats.json").read_text(encoding="utf-8"))
    function_manifest = json.loads((REFERENCE_DIR / "_data" / "function-manifest.json").read_text(encoding="utf-8"))
    metadata_pages = sorted((REFERENCE_DIR / "metadata").glob("*.md"))
    exported_symbols = set(_exported_symbols())

    assert stats["public_function_count"] == len(exported_symbols)
    assert stats["supporting_internal_function_count"] == sum(
        1 for entry in function_manifest if entry.get("qualified_name") and entry.get("name") not in exported_symbols
    )
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
    assert "[Open the interactive Callable Flow Dashboard](../assets/callable-functions-dashboard.html)" in flow_text
    assert "## Callable helper summary" not in flow_text
    assert "## Internal helper nesting inventory" not in flow_text
    assert '<div class="callable-flow-table-wrap" markdown="0">' not in flow_text
    assert "refactor reason" not in flow_text.lower()

    dashboard_text = dashboard_path.read_text(encoding="utf-8")
    assert "Callable Inventory and Refactor Signals" in dashboard_text
    assert 'id="searchBox"' in dashboard_text
    assert 'id="typeFilter"' in dashboard_text
    assert 'id="signalFilter"' in dashboard_text
    assert 'id="reviewStatusFilter"' in dashboard_text
    assert 'id="moduleFilter"' not in dashboard_text
    assert 'id="priorityFilter"' not in dashboard_text
    assert 'id="searchScope"' not in dashboard_text
    assert 'id="quickFilters"' not in dashboard_text
    assert "Search callable name" in dashboard_text
    assert (
        "Search matches function names only. Use the filters below for function type and recommended action."
        not in dashboard_text
    )
    assert "Recommended action" in dashboard_text
    assert "Reset" in dashboard_text
    assert "refactor reason" not in dashboard_text.lower()
    assert "All recommended actions" in dashboard_text
    assert "Quick signal filters" not in dashboard_text
    assert "Easy cleanup" not in dashboard_text
    assert (
        "Most conservative: preserve public APIs and notebook-facing behavior. Recommend only safe internal cleanup."
        in dashboard_text
    )
    assert (
        "Balanced default: preserve external behavior, but allow internal helper names, signatures, and boundaries to change when justified."
        in dashboard_text
    )
    assert "Most flexible: breaking changes are allowed when they simplify new or experimental code." in dashboard_text
    assert "High review" not in dashboard_text
    assert "Medium review" not in dashboard_text
    assert 'id="summaryTree"' in dashboard_text
    assert "Function summary tree" in dashboard_text
    assert "Callable inventory" in dashboard_text
    assert "Total callables" in dashboard_text
    assert "Select visible" in dashboard_text
    assert "Clear selection" in dashboard_text
    assert "Copy JSON" in dashboard_text
    assert "Copy Markdown" in dashboard_text
    assert "Download JSON" in dashboard_text
    assert "fabricops_callable_refactor_packet" in dashboard_text
    assert "function refactorContext(callables)" in dashboard_text
    assert "const callables=selectedItems().map(exportItem)" in dashboard_text
    assert "callables, functions:callables" in dashboard_text
    assert "packet.callables.forEach" in dashboard_text
    assert "packet.functions.forEach" not in dashboard_text
    assert "const functions=selectedItems().map(exportItem)" not in dashboard_text
    assert "signal_reason" in dashboard_text
    assert "refactor_context" in dashboard_text
    assert "ai_prompt" in dashboard_text
    assert "selected_callable_count" in dashboard_text
    assert "planned_batch_count" in dashboard_text
    assert "batch_id" in dashboard_text
    assert "batch_scope" in dashboard_text
    assert "batch_strategy" in dashboard_text
    assert "completed_or_refactored_count" in dashboard_text
    assert "remaining_selected_count" in dashboard_text
    assert "remaining_selected_count:null" in dashboard_text
    assert "Remaining selected count: fill in after implementation" in dashboard_text
    assert "Remaining selected count: 0" not in dashboard_text
    assert "deferred_selected_callables" in dashboard_text
    assert "Deferred selected callables: none by default before implementation" in dashboard_text
    assert "function batchAccounting(callables)" in dashboard_text
    assert "batch_accounting" in dashboard_text
    assert "Batch accounting" in dashboard_text
    assert "Completion accounting required in PR description" in dashboard_text
    assert "how many callables were selected" in dashboard_text
    assert "how many are intended for the current batch" in dashboard_text
    assert "how many were actually refactored in the PR" in dashboard_text
    assert "Do not imply that all selected callables were refactored unless they were actually changed" in dashboard_text
    assert "If this PR handles only a subset, clearly label it as a batch" in dashboard_text
    assert "selected / handled / remaining counts" in dashboard_text
    assert "refactor_type" in dashboard_text
    assert "refactor_guidance" in dashboard_text
    assert "safety_constraints" in dashboard_text
    assert "expected_ai_output" in dashboard_text
    assert "planning_only" in dashboard_text
    assert "compatibility_mode" in dashboard_text
    assert "compatibility_instruction" in dashboard_text
    assert "stable_api_safe" in dashboard_text
    assert "internal_cleanup" in dashboard_text
    assert "development_breaking_allowed" in dashboard_text
    assert "Respect the compatibility mode" in dashboard_text
    assert "How signals are classified" in dashboard_text
    assert "Small helper or single-use utility" in dashboard_text
    assert "Callable layer" in dashboard_text
    assert "Unreachable" in dashboard_text
    assert "Classification pending" in dashboard_text
    assert "Architecture layer" in dashboard_text
    assert "Review status" in dashboard_text
    assert ".filter-panel" in dashboard_text
    assert "grid-template-columns: minmax(240px, 1.3fr)" in dashboard_text
    assert "@media (max-width: 1100px)" in dashboard_text
    assert "data.function_inventory" in dashboard_text
    assert "renderTreeSummary" in dashboard_text
    assert "data-tree" in dashboard_text
    assert "Cleanup opportunities" not in dashboard_text
    assert "Hygiene signals" not in dashboard_text
    assert "Inventory and stability" not in dashboard_text
    assert "fetch('../reference/_data/callable-flow.json')" in dashboard_text
    assert "Callers" in dashboard_text
    assert "Callees" in dashboard_text
    assert "Source" in dashboard_text
    assert "All callable kinds" in dashboard_text
    assert "Callable kind" in dashboard_text
    assert "unique(inventory.map(i=>i.callable_kind))" in dashboard_text
    assert "['function','class','method'].forEach" not in dashboard_text
    assert "Used by" in dashboard_text
    assert "Layer consistency" in dashboard_text
    assert "Utility but low reuse" in dashboard_text
    assert "Review the assigned callable layer against the usage evidence" in dashboard_text

    flow_data = json.loads(flow_data_path.read_text(encoding="utf-8"))
    assert set(flow_data) == {"generated_at", "function_inventory", "summary_counts"}

    summary_counts = flow_data["summary_counts"]
    assert {
        "total_callables",
        "total_functions",
        "function_type",
        "layer",
        "review_status",
        "callable_kind",
        "recommended_action",
        "layer_consistency",
    } <= set(summary_counts)
    assert set(summary_counts["function_type"]) == {"Public API", "Internal helper", "Utility"}
    assert set(summary_counts["review_status"]) == {
        "classified",
        "classification_pending",
        "implicit_lifecycle",
        "property_accessor",
        "unreachable",
    }
    assert summary_counts["layer"]["public"] == len(exported_symbols)
    assert summary_counts["total_callables"] == sum(summary_counts["function_type"].values())

    function_inventory = flow_data["function_inventory"]
    assert len(function_inventory) == summary_counts["total_callables"]
    assert {row["qualified_name"] for row in function_inventory}
    assert len({row["qualified_name"] for row in function_inventory}) == len(function_inventory)
    assert {"Public API", "Internal helper", "Utility"} <= {row["function_type"] for row in function_inventory}
    assert {"classified", "classification_pending", "implicit_lifecycle", "property_accessor", "unreachable"} <= {
        row["review_status"] for row in function_inventory
    }
    assert sum(1 for row in function_inventory if row["layer"] == "public") == summary_counts["layer"]["public"]
    assert sum(1 for row in function_inventory if row["layer"] == "internal") == summary_counts["layer"]["internal"]
    assert sum(1 for row in function_inventory if row["layer"] == "utility") == summary_counts["layer"]["utility"]
    assert (
        sum(1 for row in function_inventory if row["review_status"] == "unreachable")
        == summary_counts["review_status"]["unreachable"]
    )
    assert {row["function_name"] for row in function_inventory if row["layer"] == "public"} == exported_symbols
    assert summary_counts["recommended_action"] == {
        action: sum(1 for row in function_inventory if row["recommended_action"] == action)
        for action in sorted({row["recommended_action"] for row in function_inventory})
    }
    assert all(row["recommended_action"] for row in function_inventory)
    assert summary_counts["layer_consistency"] == {
        consistency: sum(1 for row in function_inventory if row["layer_consistency"] == consistency)
        for consistency in summary_counts["layer_consistency"]
    }
    assert any(
        row["function_type"] == "Utility"
        and row["used_by_count"] <= 1
        and row["layer_consistency"] == "questionable_utility"
        and "Utility but low reuse" in row["signals"]
        for row in function_inventory
    )
    lifecycle_names = {
        "DataAgreementConfig.__post_init__",
        "FrameworkConfig.__post_init__",
        "GovernanceConfig.__post_init__",
        "LineageConfig.__post_init__",
        "NotebookRuntimeConfig.__post_init__",
        "PathConfig.__post_init__",
        "QualityConfig.__post_init__",
        "FabricStore.__post_init__",
    }
    lifecycle_rows = {row["function_name"]: row for row in function_inventory if row["function_name"] in lifecycle_names}
    assert set(lifecycle_rows) == lifecycle_names
    assert all(row["function_type"] == "Internal helper" for row in lifecycle_rows.values())
    assert all(row["layer"] == "internal" for row in lifecycle_rows.values())
    assert all(row["review_status"] == "implicit_lifecycle" for row in lifecycle_rows.values())
    assert all(row["callable_kind"] == "implicit_lifecycle_method" for row in lifecycle_rows.values())
    assert all(row["recommended_action"] == "Keep lifecycle method" for row in lifecycle_rows.values())
    assert all("Utility but low reuse" not in row["signals"] for row in lifecycle_rows.values())
    root_row = next(
        row
        for row in function_inventory
        if row["qualified_name"] == "fabricops_kit.fabric_input_output.FabricStore.root"
    )
    assert root_row["function_name"] == "FabricStore.root"
    assert root_row["function_type"] == "Internal helper"
    assert root_row["layer"] == "internal"
    assert root_row["callable_kind"] == "property_accessor"
    assert root_row["review_status"] == "property_accessor"
    assert root_row["recommended_action"] == "Keep property accessor"
    assert root_row["layer_consistency"] == "property_accessor"
    assert "Utility but low reuse" not in root_row["signals"]
    assert root_row["recommended_action"] != "Orphaned callable"
    assert all(row["used_by_count"] == row["called_by_count"] for row in function_inventory)
    assert all(
        {
            "function_name",
            "qualified_name",
            "module",
            "function_type",
            "layer",
            "review_status",
            "review_status_label",
            "callable_kind",
            "visibility",
            "used_by_count",
            "called_by_count",
            "calls_count",
            "layer_consistency",
            "layer_consistency_label",
            "direct_internal_helpers",
            "deepest_call_chain_depth",
            "repeated_helper_count",
            "recommended_action",
            "priority",
            "callers",
            "callees",
            "source_path",
        }
        <= set(item)
        for item in function_inventory
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
            call_flow_pos = text.index('??? info "Uses ')
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
            assert "```text" not in text.split('??? info "Uses ', 1)[1].split("##", 1)[0], page


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

    assert text.count('??? info "Uses 11 internal helper functions"') == 1
    assert '??? example "View helper source by area"' not in implementation_section
    assert '??? example "Source code"' not in implementation_section
    assert "Internal helper count: 11" not in text
    assert 'class="reference-helper-groups"' not in implementation_section
    assert re.search(
        r'href="https://github\.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline\.py#L\d+(?:-L\d+)?"',
        implementation_section,
    )

    for helper_name in [
        "_guardrail_reason",
        "_dq_reason",
        "_freshness_reason",
        "_profile_behavior_reason",
        "_result_reason",
        "_result_status",
        "_schema_reason",
        "_next_action",
        "_result_can_continue",
        "_table_keys",
        "_yes_no",
    ]:
        assert f"><code>{helper_name}(...)</code></a>" in implementation_section


def test_display_guardrail_results_lists_nested_private_helpers() -> None:
    """Verify nested private helpers appear in callable helper chips."""
    text = (API_REFERENCE_DIR / "display_guardrail_results.md").read_text(encoding="utf-8")
    implementation_section = text.split("## See also", 1)[0]

    assert implementation_section.count('??? info "Uses 11 internal helper functions"') == 1
    assert '??? info "Internal helpers used:' not in implementation_section
    assert 'class="reference-helper-groups"' not in implementation_section
    assert (
        "Unique internal/private helpers: 11. Repeated calls may appear in multiple branches."
        not in implementation_section
    )
    assert '<div class="reference-call-tree" role="tree">' in implementation_section
    assert "### Refactor signals" not in implementation_section
    assert 'class="reference-call-tree-more"' not in implementation_section
    assert "```text" not in implementation_section

    for helper_name in [
        "build_guardrail_detail_rows",
        "_guardrail_reason",
        "_dq_reason",
        "_result_reason",
        "_freshness_reason",
        "_result_status",
        "_profile_behavior_reason",
        "_schema_reason",
        "_next_action",
        "_result_can_continue",
        "_table_keys",
        "_yes_no",
        "build_guardrail_summary_rows",
    ]:
        assert f"><code>{helper_name}(...)</code></a>" in implementation_section


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
        match = re.search(r'<div class="reference-call-tree" role="tree">(?P<body>.*?)</div>', text, re.DOTALL)
        assert match, page
        slug = page.stem
        first_row = match.group("body").split("\n", 2)[1]
        assert f'href="{slug}/"' not in match.group("body"), page
        assert f'href="../{slug}/"' not in first_row, page
        assert f"<code>{slug}(...)</code>" in first_row, page


def test_public_callable_call_tree_renders_before_description() -> None:
    """Verify public callable helper trees appear directly below the title."""
    text = (API_REFERENCE_DIR / "prepare_pipeline_table_configs.md").read_text(encoding="utf-8")
    title_index = text.index("# prepare_pipeline_table_configs")
    call_tree_index = text.index('??? info "Uses 4 internal helper functions"')
    description_index = text.index("Prepare source or target table configs for 02_pipeline.")
    chips_index = text.index('<span class="reference-chip">Module: <code>pipeline</code></span>')
    usage_index = text.index("**Used in notebooks:** `02_pipeline`")

    assert title_index < call_tree_index < description_index < chips_index < usage_index
    assert text.count('??? info "Uses 4 internal helper functions"') == 1


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
    assert "Calls 1 public function" in text
    assert "nested helper functions" in text
    assert '<a href="../api/reference/profile_dataframe/"><code>profile_dataframe</code></a>' in text


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
    from scripts.generate_function_reference import _architecture_dependency_signals, _dependency_review_signals

    assert _architecture_dependency_signals("public", "internal") == []
    assert _architecture_dependency_signals("public", "utility") == []
    assert _architecture_dependency_signals("public", "public") == ["public_calls_public"]
    assert _architecture_dependency_signals("internal", "utility") == []
    assert _architecture_dependency_signals("internal", "public") == ["internal_calls_public"]
    assert _architecture_dependency_signals("internal", "internal") == ["internal_calls_internal"]
    assert _architecture_dependency_signals("utility", "public") == ["utility_calls_project_callable"]
    assert _architecture_dependency_signals("utility", "internal") == ["utility_calls_project_callable"]
    assert _architecture_dependency_signals("utility", "utility") == ["utility_calls_project_callable"]
    assert _dependency_review_signals("classification_pending") == ["callee_classification_pending"]
    assert _dependency_review_signals("unreachable") == ["callee_unreachable"]
    assert _dependency_review_signals("classified") == []
