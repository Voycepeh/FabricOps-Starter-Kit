from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
REFERENCE_DIR = ROOT / "docs" / "reference"
PLACEHOLDER = "Not documented yet"
CORE_CALLABLES = {
    "setup_notebook",
    "setup_metadata_tables",
    "widget_select_agreement",
    "get_selected_agreement",
    "read_lakehouse_table",
    "write_lakehouse_table",
    "read_lakehouse_csv",
    "read_lakehouse_parquet",
    "read_lakehouse_excel",
    "read_warehouse_table",
    "write_warehouse_table",
    "profile_dataframe",
    "validate_schema",
    "enforce_freshness",
    "enforce_profile_behavior",
    "stop_if_failed",
    "enforce_dq_rules",
    "build_lineage_records",
    "record_table_governance",
}
CORE_PAGE_SECTIONS = (
    "Purpose",
    "At a glance",
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
    section = section.split("\n<details class=\"reference-metadata-details\">", 1)[0]
    return section.strip()


def test_reference_ai_manifest_files_exist_and_are_valid_json() -> None:
    agent_manifest = REFERENCE_DIR / "agent-manifest.json"
    function_manifest = REFERENCE_DIR / "function-manifest.json"

    assert agent_manifest.exists()
    assert function_manifest.exists()
    assert json.loads(agent_manifest.read_text(encoding="utf-8"))
    assert json.loads(function_manifest.read_text(encoding="utf-8"))


def test_fabricops_skill_file_exists() -> None:
    assert (ROOT / ".agents" / "skills" / "fabricops" / "SKILL.md").exists()


def test_every_callable_page_has_ai_reference_sections() -> None:
    callable_pages = sorted((REFERENCE_DIR / "callables").glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "## Purpose" in text, page
        assert "## At a glance" in text, page
        assert "## Used by" in text, page
        assert "## Calls" in text, page
        assert "## Callable implementation" in text, page
        assert "### Function details" in text, page
        assert "### Parameters" in text, page
        assert "### Returns" in text, page
        assert "### Notes" in text, page
        assert "### Public callable source code" in text, page
        assert "## Internal implementation summary" in text, page
        assert "## Nested helper functions" not in text, page
        assert "## Source" not in text, page
        assert "\n## What this is for\n" not in text, page
        assert "\n## When to use it\n" not in text, page
        assert "\n## Raises\n" not in text, page
        assert "\n## Side effects\n" not in text, page
        assert "## AI / machine-readable metadata" not in text, page
        assert "<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>" in text, page


def test_core_callable_pages_have_non_placeholder_ai_guidance() -> None:
    for callable_name in sorted(CORE_CALLABLES):
        page = REFERENCE_DIR / "callables" / f"{callable_name}.md"
        text = page.read_text(encoding="utf-8")
        for section in CORE_PAGE_SECTIONS:
            section_text = _section_text(text, section)
            assert section_text
            assert PLACEHOLDER not in section_text, f"{page} has placeholder in {section}"


def test_core_agent_manifest_entries_have_non_placeholder_ai_fields() -> None:
    manifest = json.loads((REFERENCE_DIR / "agent-manifest.json").read_text(encoding="utf-8"))
    by_name = {entry["name"]: entry for entry in manifest if entry.get("type") == "callable"}

    assert CORE_CALLABLES <= set(by_name)
    for callable_name in sorted(CORE_CALLABLES):
        entry = by_name[callable_name]
        for field in CORE_AGENT_FIELDS:
            value = entry[field]
            assert value
            assert value != PLACEHOLDER, f"{callable_name}.{field} is placeholder"


def test_standalone_internal_pages_are_not_generated_by_default() -> None:
    internal_pages = sorted((REFERENCE_DIR / "internal").glob("*.md"))

    assert internal_pages == []


def test_callable_pages_embed_public_first_implementation_details() -> None:
    callable_pages = sorted((REFERENCE_DIR / "callables").glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        ordered_markers = [
            "## Purpose",
            "## At a glance",
            "## Used by",
            "## Calls",
            "## Callable implementation",
            "### Function details",
            "### Parameters",
            "### Returns",
            "### Notes",
            "### Public callable source code",
            "## Internal implementation summary",
        ]
        positions = [text.index(marker) for marker in ordered_markers]
        assert positions == sorted(positions), page
        assert '??? info "Call flow"' in text, page
        assert "### Call flow" not in text, page
        assert "### Internal helpers used by this callable" not in text, page
        assert "Internal helpers used by this callable" not in text, page
        assert '??? info "Nested helper functions:' not in text, page
        assert '??? info "Internal helpers used:' in text, page
        assert "Area" in text and "Helpers" in text and "What they do" in text, page
        public_source_pos = text.index("### Public callable source code")
        internal_summary_pos = text.index("## Internal implementation summary")
        call_flow_pos = text.index('??? info "Call flow"')
        assert public_source_pos < internal_summary_pos < call_flow_pos, page
        if '??? info "Internal helpers used: 0"' not in text:
            assert '??? example "View helper source by area"' in text, page
            assert text.index('??? example "View helper source by area"') > internal_summary_pos, page
            first_helper_code = text.index("```python", text.index('??? example "View helper source by area"'))
            assert first_helper_code > text.index('??? example "View helper source by area"'), page
        assert "\n### `_" not in text, page
        assert "\n## `_" not in text, page
        assert internal_summary_pos < text.index("<summary>AI / machine-readable metadata"), page


def test_enforce_dq_rules_large_helper_set_is_grouped_by_area() -> None:
    text = (REFERENCE_DIR / "callables" / "enforce_dq_rules.md").read_text(encoding="utf-8")

    assert '??? info "Internal helpers used: 16"' in text
    assert "This callable uses 16 internal helpers for" in text
    for area in (
        "Audit timestamp",
        "Metadata loading",
        "Validation",
        "Rule parsing",
        "Rule evaluation",
    ):
        assert f'<td data-label="Area">{area}</td>' in text
        assert f'??? example "{area} helpers"' in text
    assert "Expanded internal helper tree is available in the internal implementation summary." in text
    assert text.index("### Public callable source code") < text.index("## Internal implementation summary")
    assert text.index("## Internal implementation summary") < text.index('??? info "Call flow"')
    assert text.index('??? info "Call flow"') < text.index('??? info "Internal helpers used: 16"')
    assert text.index('??? example "View helper source by area"') < text.index('??? example "Audit timestamp helpers"')


def test_indent_markdown_indents_multiline_items_and_blank_lines() -> None:
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
    from scripts.generate_function_reference import generate_internal_reference_pages

    monkeypatch.delenv("FABRICOPS_GENERATE_INTERNAL_REFERENCE_PAGES", raising=False)
    assert not generate_internal_reference_pages()

    monkeypatch.setenv("FABRICOPS_GENERATE_INTERNAL_REFERENCE_PAGES", "true")
    assert generate_internal_reference_pages()


def test_github_source_url_uses_configured_source_ref(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_SOURCE_REF", "review-sha-123")

    from scripts.generate_function_reference import github_source_url

    assert github_source_url("src/fabricops_kit/config.py", 595, 704) == (
        "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/"
        "review-sha-123/src/fabricops_kit/config.py#L595-L704"
    )


def test_callable_pages_include_source_section_and_github_source_link() -> None:
    callable_pages = sorted((REFERENCE_DIR / "callables").glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "### Public callable source code" in text, page
        assert "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/" in text, page
        assert "/src/fabricops_kit/" in text, page
        assert "#L" in text, page


def test_callable_pages_collapse_ai_machine_metadata() -> None:
    callable_pages = sorted((REFERENCE_DIR / "callables").glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "\n## Function manifest" not in text, page
        assert "\n## AI implementation contract" not in text, page
        assert "\n## Inbound references" not in text, page
        assert "\n## Outbound references" not in text, page
        assert "<details" in text, page
        assert "<details open" not in text, page
        assert "<summary>AI / machine-readable metadata — skip this if you are reading the docs normally</summary>" in text, page
        metadata_start = text.index("<summary>AI / machine-readable metadata")
        metadata_end = text.index("</details>", metadata_start)
        metadata = text[metadata_start:metadata_end]
        assert "### Function manifest" in metadata, page
        assert "### AI implementation contract" in metadata, page
        assert "### Inbound references" in metadata, page
        assert "### Outbound references" in metadata, page
        assert "### Raw source metadata" in metadata, page


def test_setup_notebook_reference_uses_human_first_source_documentation() -> None:
    text = (REFERENCE_DIR / "callables" / "setup_notebook.md").read_text(encoding="utf-8")

    assert "../../api/modules/config/#setup_notebook" not in text
    assert "src/fabricops_kit/config.py#L" in text
    assert "setup_notebook on GitHub" in text
    assert "**Example:**\n\n```python\ncontext = setup_notebook" in text
    first_metadata = text.index("<summary>AI / machine-readable metadata")
    for marker in ("## Purpose", "## At a glance", "### Parameters", "### Returns"):
        assert text.index(marker) < first_metadata
    assert "## AI / machine-readable metadata" not in text
    assert "- Starting a FabricOps notebook from 00_env_config" in text
    assert "- Validating configured environment targets before downstream helpers run" in text
    assert "- Capturing runtime metadata for later lineage, review, or handover steps" in text
    assert "### Parameters" in text
    assert "Parameter" in text
    assert "Required" in text
    assert "Meaning" in text
    assert "### Public callable source code" in text
