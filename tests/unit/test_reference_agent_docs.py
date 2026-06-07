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
    "monitor_data_changes",
    "stop_if_failed",
    "enforce_dq_rules",
    "build_lineage_records",
    "record_table_governance",
}
CORE_PAGE_SECTIONS = (
    "Do not use this for",
    "Example",
    "Side effects",
    "Source code",
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
    return after.split("\n## ", 1)[0].strip()


def test_reference_ai_manifest_files_exist_and_are_valid_json() -> None:
    agent_manifest = REFERENCE_DIR / "agent-manifest.json"
    function_manifest = REFERENCE_DIR / "function-manifest.json"

    assert agent_manifest.exists()
    assert function_manifest.exists()
    assert json.loads(agent_manifest.read_text(encoding="utf-8"))
    assert json.loads(function_manifest.read_text(encoding="utf-8"))


def test_fabricops_skill_file_exists() -> None:
    assert (ROOT / "ai" / "skills" / "fabricops" / "SKILL.md").exists()


def test_every_callable_page_has_ai_reference_sections() -> None:
    callable_pages = sorted((REFERENCE_DIR / "callables").glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "## Use this when" in text, page
        assert "## Side effects" in text, page
        assert "## Source code" in text, page
        assert '<summary>AI implementation contract</summary>' in text, page


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


def test_every_internal_page_marks_direct_use_as_no() -> None:
    internal_pages = sorted((REFERENCE_DIR / "internal").glob("*.md"))

    assert internal_pages
    for page in internal_pages:
        text = page.read_text(encoding="utf-8")
        assert "## Direct use: No" in text, page


def test_github_source_url_uses_configured_source_ref(monkeypatch) -> None:
    monkeypatch.setenv("GITHUB_SOURCE_REF", "review-sha-123")

    from scripts.generate_function_reference import github_source_url

    assert github_source_url("src/fabricops_kit/config.py", 595, 704) == (
        "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/"
        "review-sha-123/src/fabricops_kit/config.py#L595-L704"
    )


def test_callable_pages_include_source_code_section_and_github_source_link() -> None:
    callable_pages = sorted((REFERENCE_DIR / "callables").glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "## Source code" in text, page
        assert "Show source code" in text, page
        assert "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/" in text, page
        assert "/src/fabricops_kit/" in text, page
        assert "#L" in text, page


def test_callable_pages_collapse_function_manifest_metadata() -> None:
    callable_pages = sorted((REFERENCE_DIR / "callables").glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "## Function manifest" not in text, page
        assert "<summary>Function manifest</summary>" in text, page
        assert "\n## Inbound references" not in text, page
        assert "\n## Outbound references" not in text, page


def test_setup_notebook_reference_uses_human_first_source_documentation() -> None:
    text = (REFERENCE_DIR / "callables" / "setup_notebook.md").read_text(encoding="utf-8")

    assert "../../api/modules/config/#setup_notebook" not in text
    assert "src/fabricops_kit/config.py#L595" in text
    assert "## Example\n\n```python\ncontext = setup_notebook" in text
    assert "## Inputs" in text
    assert "Parameter" in text
    assert "Required" in text
    assert "What it means" in text
