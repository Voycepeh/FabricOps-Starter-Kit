"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import ast
import json
import os
import subprocess
import re
from pathlib import Path

import pytest

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
    import fabricops_kit

    return list(fabricops_kit.__all__)


def test_refactor_signals_do_not_treat_cross_module_helpers_as_wrong_area() -> None:
    """Verify cross-module helper usage is not itself a wrong-area refactor signal."""
    from scripts.generate_individual_function_reference_pages import _collect_refactor_signals, _render_refactor_signals

    root_qn = "fabricops_kit.pipeline.public_api"
    calls_by_qn = {
        root_qn: [
            "fabricops_kit.pipeline._load_metadata_rules",
            "fabricops_kit.widgets.shared._load_metadata_table",
        ],
    }
    node_by_qn = {
        root_qn: {"callable_name": "public_api", "module_name": "pipeline", "exported": True},
        "fabricops_kit.pipeline._load_metadata_rules": {
            "callable_name": "_load_metadata_rules",
            "module_name": "pipeline",
            "exported": False,
        },
        "fabricops_kit.widgets.shared._load_metadata_table": {
            "callable_name": "_load_metadata_table",
            "module_name": "widgets.shared",
            "exported": False,
        },
    }
    module_data = {
        "pipeline": {"functions": {"_load_metadata_rules": "Load metadata rules for the callable."}},
        "widgets.shared": {"functions": {"_load_metadata_table": "Load metadata table rows."}},
    }

    signal_data = _collect_refactor_signals(root_qn, calls_by_qn, node_by_qn, module_data)
    signals = "\n".join(_render_refactor_signals(signal_data, node_by_qn))

    assert "contains helpers from multiple modules" not in signals
    assert "- None detected from helper names, doc summaries, and module placement." in signals
    assert signal_data["possible_grouping_mismatches"] == []


def test_helper_area_mismatch_signal_requires_three_way_mismatch() -> None:
    """Verify wrong-area signals require name, summary, and grouping mismatch."""
    from scripts.generate_individual_function_reference_pages import _helper_area_mismatch_signal

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


def test_callable_flow_page_and_json_cover_public_surface() -> None:
    """Verify the standalone guide and v2 JSON contract cover the public surface."""
    flow_page = ROOT / "docs" / "function-call-graph.md"
    redirect_page = REFERENCE_DIR / "function-call-graph.md"
    flow_data_path = REFERENCE_DIR / "_data" / "public-function-call-flows.json"

    assert flow_page.exists()
    assert redirect_page.exists()
    assert flow_data_path.exists()

    flow_text = flow_page.read_text(encoding="utf-8")
    assert "# Function Call Graph" in flow_text
    assert "## 1. Repository Code" in flow_text
    assert "## 2. Agent reads context" in flow_text
    assert "## 3. Edit function source" in flow_text
    assert "## 4. Regenerate call flow" in flow_text
    assert "## 5. Dashboard & review" in flow_text
    assert 'href="assets/public-function-call-flows-dashboard.html"' in flow_text
    assert 'href="reference/_data/public-function-call-flows.json"' in flow_text

    redirect_text = redirect_page.read_text(encoding="utf-8")
    assert "../../function-call-graph/" in redirect_text

    data = json.loads(flow_data_path.read_text(encoding="utf-8"))
    assert data["public_functions"]
    assert data["defined_functions"]
    assert "defined_but_not_used" in data

    generator_path = ROOT / "scripts/generate_individual_function_reference_pages.py"
    generator_source = generator_path.read_text(encoding="utf-8")
    assert "FUNCTION_CALL_GRAPH_PAGE_PATH" not in generator_source
    assert "def _render_callable_flow_page" not in generator_source
    assert "docs/reference/function-call-graph.md" not in generator_source


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
    assert "setup_result = setup_metadata_tables" in example
    assert "spark=spark" in example
    assert "config=CONFIG" in example
    assert "env=ENVIRONMENT_NAME" in example
    assert "metadata_schema=METADATA_SCHEMA" in example


def test_write_io_reference_pages_render_docstring_examples(tmp_path, monkeypatch) -> None:
    """Verify IO reference pages render rich Examples sections from source docstrings."""
    import scripts.generate_individual_function_reference_pages as generator

    monkeypatch.setattr(generator, "REFERENCE_DATA_DIR", tmp_path / "reference-data")
    monkeypatch.setattr(generator, "REFERENCE_PATH", tmp_path / "reference" / "index.md")
    monkeypatch.setattr(generator, "CALLABLE_REFERENCE_DIR", tmp_path / "api" / "reference")
    monkeypatch.setattr(generator, "METADATA_REFERENCE_INDEX_PATH", tmp_path / "reference" / "metadata.md")
    monkeypatch.setattr(generator, "METADATA_REFERENCE_DIR", tmp_path / "reference" / "metadata")
    monkeypatch.setattr(generator, "update_generated_artifact_metadata", lambda **_kwargs: None)

    generator.main()

    lakehouse_page = (tmp_path / "api" / "reference" / "write_lakehouse_table.md").read_text(encoding="utf-8")
    warehouse_page = (tmp_path / "api" / "reference" / "write_warehouse_table.md").read_text(encoding="utf-8")

    lakehouse_example = _section_text(lakehouse_page, "Example usage")
    assert "COUNTRY_REGION_MAPPING" in lakehouse_example
    assert "millions of rows" in _normalize_whitespace(lakehouse_example)
    assert "repartition_by=32" in lakehouse_example
    assert 'repartition_by=["academic_year", "semester"]' in lakehouse_example
    assert 'partition_by=["academic_year"]' in lakehouse_example

    warehouse_example = _section_text(warehouse_page, "Example usage")
    assert "DIM_DEPARTMENT" in warehouse_example
    assert "FACT_TRANSACTIONS" in warehouse_example
    assert "millions of rows" in _normalize_whitespace(warehouse_page)
    assert "repartition_by=32" in warehouse_example
    assert "repartition_by=48" in warehouse_example
    assert "does not create physical Warehouse table partitions" in _normalize_whitespace(warehouse_page)


def test_docstring_intro_and_notes_are_extracted_without_summary_duplication() -> None:
    """Verify rich intro text is separated from summary lines and Notes content is preserved."""
    from scripts.generate_individual_function_reference_pages import _docstring_intro, _docstring_sections, _extended_docstring_intro

    doc = """Write a DataFrame to a configured Fabric warehouse target.

    Preserve the richer introductory guidance after the short summary.
    This paragraph should remain visible on the generated page.

    Parameters
    ----------
    df : pyspark.sql.DataFrame
        Data to publish.

    Notes
    -----
    | Column | Meaning |
    | --- | --- |
    | `append` | Adds rows |
    """

    assert _docstring_intro(doc).startswith("Write a DataFrame")
    extended = _extended_docstring_intro(doc)
    assert "Write a DataFrame to a configured Fabric warehouse target." not in extended
    assert "Preserve the richer introductory guidance" in extended
    assert "This paragraph should remain visible" in extended
    assert "| Column | Meaning |" in _docstring_sections(doc)["notes"]


def test_write_warehouse_reference_page_renders_docstring_intro_and_notes(tmp_path, monkeypatch) -> None:
    """Verify generated callable pages include extended docstring intro and Notes content."""
    import scripts.generate_individual_function_reference_pages as generator

    monkeypatch.setattr(generator, "REFERENCE_DATA_DIR", tmp_path / "reference-data")
    monkeypatch.setattr(generator, "REFERENCE_PATH", tmp_path / "reference" / "index.md")
    monkeypatch.setattr(generator, "CALLABLE_REFERENCE_DIR", tmp_path / "api" / "reference")
    monkeypatch.setattr(generator, "METADATA_REFERENCE_INDEX_PATH", tmp_path / "reference" / "metadata.md")
    monkeypatch.setattr(generator, "METADATA_REFERENCE_DIR", tmp_path / "reference" / "metadata")
    monkeypatch.setattr(generator, "update_generated_artifact_metadata", lambda **_kwargs: None)

    generator.main()

    warehouse_page = (tmp_path / "api" / "reference" / "write_warehouse_table.md").read_text(encoding="utf-8")
    profile_page = (tmp_path / "api" / "reference" / "profile_dataframe.md").read_text(encoding="utf-8")

    normalized_warehouse_page = _normalize_whitespace(warehouse_page)
    assert "writes a Spark DataFrame to a Fabric Warehouse" in normalized_warehouse_page
    assert warehouse_page.count("``write_warehouse_table`` writes a Spark DataFrame to a Fabric Warehouse") == 1
    assert "Parallel processing and write concurrency" in warehouse_page
    assert "Spark distributed processing" in warehouse_page
    assert "does not create physical Warehouse table partitions" in normalized_warehouse_page
    assert "does not implement a separate temporary staging cleanup step" in normalized_warehouse_page
    notes = _section_text(warehouse_page, "Notes")
    assert "No ``partition_by`` for Warehouse" in notes
    assert "## Parameters" in warehouse_page
    assert "## Returns" in warehouse_page
    assert "## Raises / Errors" in warehouse_page
    assert "## Usage notes" in warehouse_page
    assert "View on GitHub" in warehouse_page
    assert "## Notes" not in profile_page


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
    from scripts.generate_individual_function_reference_pages import _indent_markdown

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
    from scripts.generate_individual_function_reference_pages import generate_internal_reference_pages

    monkeypatch.delenv("FABRICOPS_GENERATE_INTERNAL_REFERENCE_PAGES", raising=False)
    assert not generate_internal_reference_pages()

    monkeypatch.setenv("FABRICOPS_GENERATE_INTERNAL_REFERENCE_PAGES", "true")
    assert generate_internal_reference_pages()


def test_github_source_url_defaults_to_main(monkeypatch) -> None:
    """Verify github source url defaults to the reachable main branch."""
    monkeypatch.delenv("GITHUB_SOURCE_REF", raising=False)
    monkeypatch.delenv("FABRICOPS_SOURCE_REF", raising=False)

    from scripts.generate_individual_function_reference_pages import github_source_url

    assert github_source_url("src/fabricops_kit/config.py", 595, 704) == (
        "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/config.py#L595-L704"
    )


def test_github_source_url_uses_configured_source_ref(monkeypatch) -> None:
    """Verify github source url uses an explicitly configured reachable source ref."""
    monkeypatch.setenv("GITHUB_SOURCE_REF", "review-sha-123")

    from scripts.generate_individual_function_reference_pages import github_source_url

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

    assert "## Call-flow summary" in implementation_section
    assert "- Downstream callables:" in implementation_section
    assert "Open Preview call flow" in implementation_section
    assert '??? example "View helper source by area"' not in implementation_section
    assert '??? example "Source code"' not in implementation_section
    assert "Implementation helper count: 11" not in text
    assert 'class="reference-helper-groups"' not in implementation_section
    assert re.search(
        r'href="https://github\.com/Voycepeh/FabricOps-Starter-Kit/blob/main/src/fabricops_kit/pipeline/(?:display_guardrail_results|shared)\.py#L\d+(?:-L\d+)?"',
        implementation_section,
    )

    assert "View on GitHub" in implementation_section
    assert "public-function-call-flows-dashboard.html?function=display_guardrail_results" in implementation_section


def test_dashboard_focus_links_escape_api_reference_route() -> None:
    """Verify generated reference links resolve to MkDocs assets, not api assets."""
    callable_pages = sorted(API_REFERENCE_DIR.glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "/api/assets/public-function-call-flows-dashboard.html" not in text, page
        assert 'href="../../assets/public-function-call-flows-dashboard.html' not in text, page
        if "Open focused call flow in dashboard" in text:
            assert "../../../assets/public-function-call-flows-dashboard.html?function=" in text, page


def test_display_guardrail_results_lists_nested_private_helpers() -> None:
    """Verify nested private helpers appear in callable helper chips."""
    text = (API_REFERENCE_DIR / "display_guardrail_results.md").read_text(encoding="utf-8")
    implementation_section = text.split("## See also", 1)[0]

    assert "## Call-flow summary" in implementation_section
    assert "- Shared helpers:" in implementation_section
    assert "- Private helpers:" in implementation_section
    assert '??? info "Implementation helpers used:' not in implementation_section
    assert 'class="reference-helper-groups"' not in implementation_section
    assert '<div class="reference-call-tree" role="tree" data-callable-architecture-flow="true">' not in implementation_section
    assert "### Refactor signals" not in implementation_section
    assert 'class="reference-call-tree-more"' not in implementation_section
    assert "```text" not in implementation_section

    assert "View on GitHub" in implementation_section
    assert "public-function-call-flows-dashboard.html?function=display_guardrail_results" in implementation_section


def _reference_call_tree_rows(text: str) -> list[str]:
    """Return normalized callable names and prefixes from a generated call tree."""
    rows = []
    for prefix, name in re.findall(
        r'<div class="reference-call-tree-row" role="treeitem"><span class="reference-call-tree-prefix">(?P<prefix>.*?)</span>.*?<code>(?P<name>[^(<]+)\(\.\.\.\)</code>.*?</div>',
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
    pytest.skip("callable graph JSON is no longer owned by the individual function page generator")
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
    title_index = text.index("# `prepare_pipeline_table_configs`")
    description_index = text.index("Prepare source or target table configs for 02_pipeline.")
    source_index = text.index('<div class="reference-source-card" markdown="1">')
    usage_index = text.index("**Used in notebooks:** `02_pipeline`")

    assert title_index < description_index < source_index < usage_index
    assert "## Call-flow summary" in text
    assert "Open Preview call flow" in text


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
    example = _section_text(text, "Example usage")
    assert "CONTEXT = setup_notebook" in example
    assert "required_targets=" in example
    for marker in ("## Signature", "## Parameters", "## Returns"):
        assert marker in text
    assert "## AI / machine-readable metadata" not in text
    assert "Machine-readable metadata / metadata details" not in text
    assert "Use this in the setup notebook to capture and render the key runtime information" in text
    assert "This helps confirm the active environment, configured stores, notebook context, and runtime values" in text
    assert "## Parameters" in text
    assert "| `config` |" in text
    assert "| Yes |" in text or "| No |" in text
    assert "## Source link" not in text


def test_public_callable_usage_notes_are_family_standardized() -> None:
    """Verify generated Usage notes come from path-first family defaults and overrides."""
    io_text = (API_REFERENCE_DIR / "read_lakehouse_table.md").read_text(encoding="utf-8")
    widget_text = (API_REFERENCE_DIR / "widget_author_dq_rules.md").read_text(encoding="utf-8")
    pipeline_text = (API_REFERENCE_DIR / "profile_dataframe.md").read_text(encoding="utf-8")
    setup_text = (API_REFERENCE_DIR / "setup_metadata_tables.md").read_text(encoding="utf-8")
    config_text = (API_REFERENCE_DIR / "prepare_pipeline_table_configs.md").read_text(encoding="utf-8")

    for text in (io_text, widget_text, pipeline_text, setup_text, config_text):
        assert "## Usage notes" in text
        assert "### Use when" not in text
        assert "### Do not use when" not in text
        assert "### Additional context" not in text

    assert "Fabric notebooks can only attach to one lakehouse or warehouse at a time" in io_text
    assert "front-end notebook interface so users can enter metadata in a guided way" in widget_text
    assert "standard Starter Kit pipeline flow" in pipeline_text
    assert "profile of the data so downstream users can review the dataset consistently" in pipeline_text
    assert "configured metadata lakehouse using predefined Starter Kit schemas" in setup_text
    assert "standard pipeline table-config pattern, not for ad hoc reads or writes" in config_text


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


def test_concept_pages_link_back_to_key_callable_references() -> None:
    """Verify user-guide pages link back to key callable references."""
    environment_config = (ROOT / "docs" / "guided-demo" / "run-environment-setup.md").read_text(encoding="utf-8")
    agreement_setup = (ROOT / "docs" / "guided-demo" / "create-agreement.md").read_text(encoding="utf-8")
    pipeline_execution = (ROOT / "docs" / "guided-demo" / "run-pipeline.md").read_text(encoding="utf-8")
    governance_review = (ROOT / "docs" / "guided-demo" / "review-guardrails.md").read_text(encoding="utf-8")
    metadata_tables_path = ROOT / "docs" / "reference" / "metadata.md"
    metadata_tables = metadata_tables_path.read_text(encoding="utf-8")
    lineage_table = (ROOT / "docs" / "reference" / "metadata" / "metadata_data_lineage_table.md").read_text(
        encoding="utf-8"
    )

    assert "metadata setup cell" in environment_config
    assert "DATA_AGREEMENT_CONFIG" in agreement_setup
    assert "source and target table settings" in pipeline_execution
    assert "schema, freshness, profile behavior, and active DQ rules" in pipeline_execution
    assert "Select the governed table context" in governance_review
    assert "Approve, reject, replace, deactivate" in governance_review
    if "setup_metadata_tables" in metadata_tables:
        assert "[`setup_metadata_tables`](../api/reference/setup_metadata_tables.md)" in metadata_tables
    assert "[`profile_and_register_dataframe`](../../api/reference/profile_and_register_dataframe.md)" in lineage_table


def test_metadata_reference_overview_renders_model_diagram() -> None:
    """Verify the metadata overview keeps the model diagram near the top."""
    metadata_tables_path = ROOT / "docs" / "reference" / "metadata.md"
    asset_path = ROOT / "docs" / "assets" / "fabricops-metadata-model.png"
    text = metadata_tables_path.read_text(encoding="utf-8")
    image_reference = "../assets/fabricops-metadata-model.png"

    assert asset_path.exists()
    assert "The diagram below shows how the FabricOps metadata tables relate to one another" in text
    assert f"![FabricOps metadata model]({image_reference})" in text
    assert (metadata_tables_path.parent / image_reference).resolve() == asset_path.resolve()
    assert text.index("FabricOps metadata tables describe") < text.index(image_reference)
    assert text.index(image_reference) < text.index("<div class=\"grid cards\" markdown>")

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


def test_template_called_callable_parameters_render_as_api_table() -> None:
    """Verify template-called callable parameters render as api table."""
    text = (API_REFERENCE_DIR / "profile_dataframe.md").read_text(encoding="utf-8")
    parameters = _section_text(text, "Parameters")

    assert "| Parameter | Type | Required | Description |" in parameters
    assert "| `df` |" in parameters
    assert "| `approximate_distinct` |" in parameters


def test_internalized_enforce_profile_behavior_preserves_no_page_contract() -> None:
    """Verify internalized enforce_profile_behavior is not rendered as a public page."""
    assert not (API_REFERENCE_DIR / "enforce_profile_behavior.md").exists()


def test_reference_nav_preserves_existing_user_facing_entries() -> None:
    """Verify generated reference pages remain in the existing sidebar locations."""
    mkdocs_text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "  - Reference:" not in mkdocs_text
    assert (
        "  - Templates: notebook-templates-implementation-guide/index.md" in mkdocs_text
    )
    assert "  - List of Metadata Tables:" in mkdocs_text
    assert "      - Overview: reference/metadata.md" in mkdocs_text
    assert "  - List of Functions: reference/index.md" in mkdocs_text
    assert "  - List of DQ Rules:" in mkdocs_text
    assert "      - Overview: reference/dq-rules/index.md" in mkdocs_text
    assert not re.search(r"^  - Glossary: reference/glossary\.md$", mkdocs_text, re.MULTILINE)
    assert not re.search(r"^  - Function & DQ Rules Reference:$", mkdocs_text, re.MULTILINE)
    assert "api/reference/" not in mkdocs_text

    public_functions = [
        str(row["function_name"])
        for row in json.loads((REFERENCE_DIR / "_data" / "public-function-call-flows.json").read_text(encoding="utf-8"))["public_functions"]
    ]
    missing = [name for name in public_functions if not (API_REFERENCE_DIR / f"{name}.md").exists()]
    assert missing == []


def test_maintainer_nav_parks_internal_reference_helpers() -> None:
    """Verify maintainer-facing helper docs are parked under maintainer references."""
    mkdocs_text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")

    assert "Functions by Modules" not in mkdocs_text
    assert "  - Maintainer References:" in mkdocs_text
    assert "reference/maintainer-guide.md" not in mkdocs_text
    assert "reference/glossary.md" not in mkdocs_text
    assert "      - Function Call Graph: reference/function-call-graph.md" in mkdocs_text
    assert "      - Implementation Appendix:" in mkdocs_text
    assert "      # AUTO-GENERATED-MODULES-END" in mkdocs_text
    assert "api/modules/config.md" not in mkdocs_text
    assert "api/modules/" not in mkdocs_text
    assert "api/reference/" not in mkdocs_text


def test_callable_layer_dependency_rule_matrix() -> None:
    """Verify callable layer dependency rules match the architecture matrix."""
    from scripts.generate_individual_function_reference_pages import (
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
    import scripts.generate_individual_function_reference_pages as generator

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

    import scripts.generate_individual_function_reference_pages as generator

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

    import scripts.generate_individual_function_reference_pages as generator

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
    import scripts.generate_individual_function_reference_pages as generator

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


def test_callable_inventory_item_type_counts_match_filter_keys() -> None:
    """Verify item type filter keys match generated function-level inventory records."""
    pytest.skip("callable graph JSON is no longer owned by the individual function page generator")
    flow_data = json.loads(
        (ROOT / "docs" / "reference" / "_data" / "function-call-graph.json").read_text(encoding="utf-8")
    )
    inventory = flow_data["function_inventory"]

    expected_counts = {
        "public": flow_data["summary_counts"]["layer"]["public"],
        "internal": flow_data["summary_counts"]["layer"]["internal"],
        "private_helper": flow_data["summary_counts"]["callable_inventory_metrics"]["hidden_private_helpers"],
    }
    actual_counts = {key: sum(1 for row in inventory if row["layer"] == key) for key in expected_counts}

    assert actual_counts == expected_counts
    assert any(row.get("reachability") == "unreachable_runtime_asset" for row in inventory)
    assert all(row.get("source_path", "").startswith("src/fabricops_kit/") for row in inventory)
    assert "supporting_object" not in {row["layer"] for row in inventory}
    assert all(row["function_type"] != "Non functions" for row in inventory)


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
    const makeCell = (text, filterValue) => ({
      textContent: text,
      innerText: text,
      dataset: filterValue === undefined ? {} : {filterValue},
    });
    const sourceRow = {
      cells:[
        makeCell('src/fabricops_kit/widgets/shared.py Finding: Reason: Evidence: Notes: Cleanup action:', 'src/fabricops_kit/widgets/shared.py'),
        makeCell('build_metadata', 'build_metadata'),
        makeCell('Public function', 'Public function'),
      ],
      matches(selector){ return false; },
    };
    const otherSourceRow = {
      cells:[makeCell('src/fabricops_kit/io.py', 'src/fabricops_kit/io.py'), makeCell('read_table', 'read_table'), makeCell('Shared helper', 'Shared helper')],
      matches(selector){ return false; },
    };
    const detailRow = {
      cells:[makeCell('Finding: Reason: Evidence: Notes: Cleanup action:')],
      matches(selector){ return selector === '[data-details-row]'; },
    };
    const blankRow = {
      cells:[makeCell('', ''), makeCell('unnamed', 'unnamed'), makeCell('Private helper', 'Private helper')],
      matches(selector){ return false; },
    };
    const table = {
      dataset:{tableControls:'excel'},
      tHead:{rows:[{cells:[{}, {}, {}]}]},
      tBodies:[{rows:[sourceRow, detailRow, otherSourceRow]}],
    };
    const values = t.uniqueValues(table, 0);
    assert(values.includes('src/fabricops_kit/widgets/shared.py'), 'source file filter includes raw source path');
    assert(values.includes('src/fabricops_kit/io.py'), 'source file filter includes second raw source path');
    assert(!values.some((value) => /Finding:|Reason:|Evidence:|Notes:|Cleanup action:/.test(value)), 'source file filter excludes details text');
    assert(!values.includes('(blank)'), 'source file filter excludes blank when no raw source file is blank');
    assert(t.filterableRows(table).length === 2, 'expanded details rows are not filterable rows');
    assert(t.rowMatchesFilter(sourceRow,{column:0,kind:'values',values:new Set(['src/fabricops_kit/widgets/shared.py'])}), 'raw source file filtering works');
    const blankTable = {dataset:{tableControls:'excel'}, tHead:{rows:[{cells:[{}, {}, {}]}]}, tBodies:[{rows:[sourceRow, blankRow]}]};
    const blankValues = t.uniqueValues(blankTable, 0);
    assert(blankValues.includes('(blank)'), 'blank filter appears for true blank raw values');
    assert(t.rowMatchesFilter(blankRow,{column:0,kind:'values',values:new Set(['(blank)'])}), 'blank raw values filter correctly');
    sourceRow.dataset = {inventoryRow:'source'};
    otherSourceRow.dataset = {inventoryRow:'other'};
    blankRow.dataset = {inventoryRow:'blank'};
    assert(t.getVisibleRowKeys(table).join(',') === 'source,other', 'visible row keys follow unfiltered rows');
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
    import scripts.generate_individual_function_reference_pages as generator

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
    import scripts.generate_individual_function_reference_pages as generator

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
    import scripts.generate_individual_function_reference_pages as generator

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
    import scripts.generate_individual_function_reference_pages as generator

    public_qn = "fabricops_kit.pipeline.guardrails_shared.run_table_guardrails"
    workflow_qn = "fabricops_kit.pipeline.guardrails_shared._run_table_guardrails_workflow"
    core_qn = "fabricops_kit.profiling.profile_dataframe_core"
    private_core_qn = "fabricops_kit.profiling._profile_dataframe_core"
    distribution_qn = "fabricops_kit.profiling.build_distribution_summaries"
    categorical_qn = "fabricops_kit.profiling.build_categorical_distribution"
    other_public_qn = "fabricops_kit.other.other_public"
    node_by_qn = {
        public_qn: {"callable_name": "run_table_guardrails", "module_name": "pipeline", "callable_kind": "function"},
        other_public_qn: {"callable_name": "other_public", "module_name": "other", "callable_kind": "function"},
        workflow_qn: {"callable_name": "_run_table_guardrails_workflow", "module_name": "pipeline", "callable_kind": "function"},
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
        _flow_test_inventory_row(public_qn, "run_table_guardrails", "pipeline", "public"),
        _flow_test_inventory_row(other_public_qn, "other_public", "other", "public"),
        _flow_test_inventory_row(workflow_qn, "_run_table_guardrails_workflow", "pipeline", "private_helper", owner=public_qn),
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
    import scripts.generate_individual_function_reference_pages as generator

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
    import scripts.generate_individual_function_reference_pages as generator

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


def test_callable_flow_simple_classification_detects_shared_internal_reuse() -> None:
    """Verify shared internal helpers are identified from reuse across public callables."""
    import scripts.generate_individual_function_reference_pages as generator

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
    import scripts.generate_individual_function_reference_pages as generator

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


def test_split_pipeline_public_callables_keep_ast_definition_owner_files() -> None:
    """Verify split pipeline public callables use AST definition source ownership."""
    import scripts.generate_individual_function_reference_pages as generator

    module_data = {
        generator.source_module_name(path): generator.parse_module(path)
        for path in generator.source_module_paths()
    }
    expected_paths = {
        "display_guardrail_results": "src/fabricops_kit/pipeline/display_guardrail_results.py",
        "prepare_pipeline_table_configs": "src/fabricops_kit/pipeline/prepare_pipeline_table_configs.py",
        "profile_dataframe": "src/fabricops_kit/pipeline/profile_dataframe.py",
        "run_table_guardrails": "src/fabricops_kit/pipeline/run_table_guardrails.py",
        "profile_and_register_dataframe": "src/fabricops_kit/pipeline/profile_and_register_dataframe.py",
    }

    for function_name, expected_path in expected_paths.items():
        qn = f"fabricops_kit.pipeline.{function_name}"
        assert generator._callable_flow_source_path(qn, module_data) == expected_path

    wrong_profile_owner = "src/fabricops_kit/pipeline/profile_dataframe.py"
    for function_name, expected_path in expected_paths.items():
        if function_name != "profile_dataframe":
            qn = f"fabricops_kit.pipeline.{function_name}"
            assert generator._callable_flow_source_path(qn, module_data) != wrong_profile_owner


def test_generated_inventory_split_pipeline_public_callables_have_owner_files() -> None:
    """Verify generated inventory rows preserve split pipeline public callable owner files."""
    pytest.skip("callable graph JSON is no longer owned by the individual function page generator")
    flow_data = json.loads(
        (ROOT / "docs" / "reference" / "_data" / "function-call-graph.json").read_text(encoding="utf-8")
    )
    rows_by_name = {
        row["function_name"]: row
        for row in flow_data["function_inventory"]
        if row.get("module", "").startswith("pipeline") and row.get("layer") == "public"
    }
    expected_paths = {
        "display_guardrail_results": "src/fabricops_kit/pipeline/display_guardrail_results.py",
        "prepare_pipeline_table_configs": "src/fabricops_kit/pipeline/prepare_pipeline_table_configs.py",
        "profile_dataframe": "src/fabricops_kit/pipeline/profile_dataframe.py",
        "run_table_guardrails": "src/fabricops_kit/pipeline/run_table_guardrails.py",
        "profile_and_register_dataframe": "src/fabricops_kit/pipeline/profile_and_register_dataframe.py",
        "write_pipeline_run_summary": "src/fabricops_kit/pipeline/write_pipeline_run_summary.py",
    }

    for function_name, expected_path in expected_paths.items():
        row = rows_by_name[function_name]
        assert row["source_path"] == expected_path
        assert row["owner_file"] == expected_path

    wrong_profile_owner = "src/fabricops_kit/pipeline/profile_dataframe.py"
    wrongly_owned = [
        name
        for name, row in rows_by_name.items()
        if name != "profile_dataframe" and row["source_path"] == wrong_profile_owner
    ]
    assert wrongly_owned == []


def test_generated_dashboard_split_pipeline_scopes_are_not_sibling_grouped() -> None:
    """Verify dashboard public flows scope split pipeline callables independently."""
    pytest.skip("dashboard/callable graph JSON is no longer owned by the individual function page generator")
    flow_data = json.loads(
        (ROOT / "docs" / "reference" / "_data" / "function-call-graph.json").read_text(encoding="utf-8")
    )
    flows_by_name = {flow["function_name"]: flow for flow in flow_data["public_entrypoint_flow"]}
    inventory_by_qn = {row["qualified_name"]: row for row in flow_data["function_inventory"]}
    split_names = {
        "display_guardrail_results",
        "prepare_pipeline_table_configs",
        "profile_dataframe",
        "run_table_guardrails",
        "profile_and_register_dataframe",
        "write_pipeline_run_summary",
    }

    for name in split_names:
        flow = flows_by_name[name]
        asset_qns = {flow["qualified_name"], *(callee["qualified_name"] for callee in flow["transitive_callees"])}
        sibling_qns = {flows_by_name[sibling]["qualified_name"] for sibling in split_names - {name}}
        assert asset_qns.isdisjoint(sibling_qns), name
        assert flow["scope"] == len(asset_qns)
        assert flow["scope_asset_count"] == len(asset_qns)
        assert all(inventory_by_qn[qn]["source_path"] for qn in asset_qns if qn in inventory_by_qn)

    profile_assets = {
        flows_by_name["profile_dataframe"]["qualified_name"],
        *(callee["qualified_name"] for callee in flows_by_name["profile_dataframe"]["transitive_callees"]),
    }
    assert flows_by_name["prepare_pipeline_table_configs"]["qualified_name"] not in profile_assets
    assert flows_by_name["display_guardrail_results"]["qualified_name"] not in profile_assets
    assert flows_by_name["run_table_guardrails"]["qualified_name"] not in profile_assets


def test_generated_public_callable_scope_counts_match_exact_flow_assets() -> None:
    """Verify selected public callable helper data matches exact public flow assets."""
    pytest.skip("callable graph JSON is no longer owned by the individual function page generator")
    flow_data = json.loads(
        (ROOT / "docs" / "reference" / "_data" / "function-call-graph.json").read_text(encoding="utf-8")
    )
    flows_by_qn = {flow["qualified_name"]: flow for flow in flow_data["public_entrypoint_flow"]}
    expected_counts = {
        "fabricops_kit.pipeline.display_guardrail_results": 15,
        "fabricops_kit.pipeline.prepare_pipeline_table_configs": 5,
        "fabricops_kit.pipeline.profile_dataframe": 11,
        "fabricops_kit.pipeline.run_table_guardrails": 120,
        "fabricops_kit.io.read_warehouse_query.read_warehouse_query": 13,
        "fabricops_kit.io.read_lakehouse_table.read_lakehouse_table": 17,
    }
    for qn, expected_count in expected_counts.items():
        flow = flows_by_qn[qn]
        flow_assets = {flow["qualified_name"], *(row["qualified_name"] for row in flow["transitive_callees"])}
        assert flow["scope"] == expected_count
        assert len(flow_assets) == flow["scope"]

    forbidden = {
        "fabricops_kit.pipeline.display_guardrail_results": {
            "fabricops_kit.pipeline.prepare_pipeline_table_configs",
            "fabricops_kit.pipeline.profile_dataframe",
            "fabricops_kit.pipeline.run_table_guardrails",
            "fabricops_kit.pipeline.profile_and_register_dataframe",
            "fabricops_kit.pipeline.write_pipeline_run_summary",
        },
        "fabricops_kit.pipeline.profile_dataframe": {
            "fabricops_kit.pipeline.display_guardrail_results",
            "fabricops_kit.pipeline.prepare_pipeline_table_configs",
            "fabricops_kit.pipeline.run_table_guardrails",
            "fabricops_kit.pipeline.profile_and_register_dataframe",
            "fabricops_kit.pipeline.write_pipeline_run_summary",
        },
    }
    for qn, siblings in forbidden.items():
        flow = flows_by_qn[qn]
        flow_assets = {flow["qualified_name"], *(row["qualified_name"] for row in flow["transitive_callees"])}
        assert flow_assets.isdisjoint(siblings)


def test_shared_call_graph_renderer_includes_source_type_and_architecture_flags() -> None:
    """Verify the shared call-tree renderer enriches function docs and dashboard trees."""
    from scripts import generate_individual_function_reference_pages as generator

    root_qn = "fabricops_kit.pipeline.display_guardrail_results.display_guardrail_results"
    shared_qn = "fabricops_kit.pipeline.shared._display_guardrail_results_workflow"
    private_qn = "fabricops_kit.pipeline.shared._guardrail_reason"
    node_by_qn = {
        root_qn: {
            "callable_name": "display_guardrail_results",
            "module_name": "pipeline.display_guardrail_results",
            "exported": True,
            "callable_kind": "function",
        },
        shared_qn: {
            "callable_name": "_display_guardrail_results_workflow",
            "module_name": "pipeline.shared",
            "exported": False,
            "callable_kind": "function",
        },
        private_qn: {
            "callable_name": "_guardrail_reason",
            "module_name": "pipeline.shared",
            "exported": False,
            "callable_kind": "function",
        },
    }
    rendered = "\n".join(
        generator._render_clickable_call_tree(
            root_qn,
            {root_qn: [shared_qn], shared_qn: [private_qn]},
            node_by_qn,
            {},
        )
    )
    flow_rendered = "\n".join(
        generator._render_callable_architecture_flow_tree(
            {
                "qualified_name": root_qn,
                "function_name": "display_guardrail_results",
                "source_path": "src/fabricops_kit/pipeline/display_guardrail_results.py",
                "function_type": "Public function",
                "architecture_violation_count": 1,
                "transitive_callees": [
                    {
                        "qualified_name": shared_qn,
                        "function_name": "_display_guardrail_results_workflow",
                        "source_path": "src/fabricops_kit/pipeline/shared.py",
                        "function_type": "Shared helper",
                        "parent_qualified_name": root_qn,
                        "depth": 1,
                    },
                    {
                        "qualified_name": private_qn,
                        "function_name": "_guardrail_reason",
                        "source_path": "src/fabricops_kit/pipeline/shared.py",
                        "function_type": "Private helper",
                        "parent_qualified_name": shared_qn,
                        "depth": 2,
                        "architecture_result": "Violation",
                    },
                ],
            },
            node_by_qn,
            {},
        )
    )

    assert "[pipeline/display_guardrail_results.py]" in rendered
    assert "display_guardrail_results(...)" in rendered
    assert "[public callable]" in rendered
    assert "[pipeline/shared.py]" in rendered
    assert "_display_guardrail_results_workflow(...)" in rendered
    assert "[private helper]" in rendered
    assert "[violation]" not in flow_rendered
    assert "[architecture violation]" not in flow_rendered


def test_read_lakehouse_table_public_flow_uses_reference_dependency_tree_source() -> None:
    """Verify read_lakehouse_table selected-flow data is built from callable dependencies."""
    import scripts.generate_individual_function_reference_pages as generator

    public_qn = "fabricops_kit.io.read_lakehouse_table.read_lakehouse_table"
    helper_qns = [
        "fabricops_kit.io.shared.get_spark_session",
        "fabricops_kit.io.shared.read_delta_path",
        "fabricops_kit.io.shared.resolve_configured_lakehouse_table",
        "fabricops_kit.io.shared.resolve_lakehouse_table_location",
        "fabricops_kit.io.shared.normalize_table_name",
        "fabricops_kit.io.shared.resolve_target_store",
    ]
    node_by_qn = {
        public_qn: {
            "callable_name": "read_lakehouse_table",
            "module_name": "io.read_lakehouse_table",
            "callable_kind": "function",
            "is_underscore": False,
        },
        **{
            qn: {
                "callable_name": qn.rsplit(".", 1)[-1],
                "module_name": "io.shared",
                "callable_kind": "function",
                "is_underscore": False,
            }
            for qn in helper_qns
        },
    }
    calls_by_qn = {
        public_qn: [
            "fabricops_kit.io.shared.get_spark_session",
            "fabricops_kit.io.shared.resolve_configured_lakehouse_table",
            "fabricops_kit.io.shared.read_delta_path",
        ],
        "fabricops_kit.io.shared.resolve_configured_lakehouse_table": [
            "fabricops_kit.io.shared.resolve_lakehouse_table_location",
            "fabricops_kit.io.shared.normalize_table_name",
        ],
        "fabricops_kit.io.shared.resolve_lakehouse_table_location": [
            "fabricops_kit.io.shared.resolve_target_store",
        ],
        **{qn: [] for qn in helper_qns if qn not in {
            "fabricops_kit.io.shared.resolve_configured_lakehouse_table",
            "fabricops_kit.io.shared.resolve_lakehouse_table_location",
        }},
    }
    function_inventory = [
        {
            "qualified_name": public_qn,
            "function_name": "read_lakehouse_table",
            "module": "io.read_lakehouse_table",
            "layer": "public",
            "function_type": "Public function",
            "callable_kind": "function",
        },
        *[
            {
                "qualified_name": qn,
                "function_name": qn.rsplit(".", 1)[-1],
                "module": "io.shared",
                "layer": "internal",
                "function_type": "Shared helper",
                "callable_kind": "function",
            }
            for qn in helper_qns
        ],
    ]

    flows = generator._build_public_entrypoint_flow([public_qn], calls_by_qn, node_by_qn, {}, function_inventory)
    flow = flows[0]

    assert flow["function_name"] == "read_lakehouse_table"
    assert flow["qualified_name"] == "fabricops_kit.io.read_lakehouse_table.read_lakehouse_table"
    downstream_names = {row["function_name"] for row in flow["transitive_callees"]}
    assert {
        "get_spark_session",
        "read_delta_path",
        "resolve_configured_lakehouse_table",
        "resolve_lakehouse_table_location",
        "normalize_table_name",
        "resolve_target_store",
    } <= downstream_names
    assert {
        "fabricops_kit.io.read_lakehouse_table.read_lakehouse_table",
        "io.read_lakehouse_table.read_lakehouse_table",
        "read_lakehouse_table",
    } <= set(generator._public_flow_selection_keys(flow))


def test_retired_focused_call_graph_entrypoint_is_removed() -> None:
    """Verify the retired v1-only call graph entrypoint is no longer available."""
    import scripts.generate_individual_function_reference_pages as generator

    assert not hasattr(generator, "generate_function_call_graph_artifacts")
    assert not (ROOT / "scripts" / "generate_function_call_graph.py").exists()
