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
    "What this is for and when to use it",
    "When not to use it",
    "Example",
    "Errors and side effects",
    "Source",
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
    assert (ROOT / "ai" / "skills" / "fabricops" / "SKILL.md").exists()


def test_every_callable_page_has_ai_reference_sections() -> None:
    callable_pages = sorted((REFERENCE_DIR / "callables").glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "## What this is for and when to use it" in text, page
        assert "## When not to use it" in text, page
        assert "## Errors and side effects" in text, page
        assert "## Source" in text, page
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


def test_callable_pages_include_source_section_and_github_source_link() -> None:
    callable_pages = sorted((REFERENCE_DIR / "callables").glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "## Source" in text, page
        assert "Show source code" in text, page
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
    assert "src/fabricops_kit/config.py#L595" in text
    assert "## Example\n\n```python\ncontext = setup_notebook" in text
    first_metadata = text.index("<summary>AI / machine-readable metadata")
    for marker in ("## What this is for and when to use it", "## When not to use it", "## Example", "## Errors and side effects"):
        assert text.index(marker) < first_metadata
    assert "## AI / machine-readable metadata" not in text
    assert "- Starting a FabricOps notebook from 00_env_config" in text
    assert "- Validating configured environment targets before downstream helpers run" in text
    assert "- Capturing runtime metadata for later lineage, review, or handover steps" in text
    assert "## Inputs" in text
    assert "Parameter" in text
    assert "Required" in text
    assert "Meaning" in text
    assert "Show source code" in text
