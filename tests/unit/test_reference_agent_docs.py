from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
REFERENCE_DIR = ROOT / "docs" / "reference"
API_REFERENCE_DIR = ROOT / "docs" / "api" / "reference"
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


def _subsection_text(page_text: str, subsection: str) -> str:
    marker = f"### {subsection}\n"
    assert marker in page_text
    after = page_text.split(marker, 1)[1]
    return after.split("\n### ", 1)[0].strip()


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
    callable_pages = sorted(API_REFERENCE_DIR.glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "## When to use this" in text, page
        assert "## At a glance" in text, page
        assert "## Used in templates" in text, page
        assert "## Used by" in text, page
        assert "## Calls" in text, page
        assert "## Function details and source" in text, page
        assert "### Function details" in text, page
        assert "### Parameters" in text, page
        assert "### Returns" in text, page
        assert "### Notes" in text, page
        assert "### Example" in text, page
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
        page = API_REFERENCE_DIR / f"{callable_name}.md"
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
    callable_pages = sorted(API_REFERENCE_DIR.glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        ordered_markers = [
            "## When to use this",
            "## At a glance",
            "## Used in templates",
            "## Used by",
            "## Calls",
            "## Function details and source",
            "### Function details",
            "### Parameters",
            "### Returns",
            "### Notes",
            "### Example",
            "### Public callable source code",
            "## Internal implementation summary",
        ]
        if "## Purpose" in text:
            ordered_markers.insert(0, "## Purpose")
        for optional_marker in ("### Return interpretation", "### Common failure causes"):
            if optional_marker in text:
                ordered_markers.insert(ordered_markers.index("### Notes"), optional_marker)
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
    text = (API_REFERENCE_DIR / "enforce_dq_rules.md").read_text(encoding="utf-8")

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
    callable_pages = sorted(API_REFERENCE_DIR.glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "### Public callable source code" in text, page
        assert "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/" in text, page
        assert "/src/fabricops_kit/" in text, page
        assert "#L" in text, page


def test_callable_pages_collapse_ai_machine_metadata() -> None:
    callable_pages = sorted(API_REFERENCE_DIR.glob("*.md"))

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
    text = (API_REFERENCE_DIR / "setup_notebook.md").read_text(encoding="utf-8")

    assert "../../api/modules/config/#setup_notebook" not in text
    assert "src/fabricops_kit/config.py#L" in text
    assert "setup_notebook on GitHub" in text
    assert "### Example\n\n```python\ncontext = setup_notebook" in text
    first_metadata = text.index("<summary>AI / machine-readable metadata")
    for marker in ("## At a glance", "### Parameters", "### Returns"):
        assert text.index(marker) < first_metadata
    assert "## AI / machine-readable metadata" not in text
    assert "- Starting a FabricOps notebook from 00_env_config" in text
    assert "- Validating configured environment targets before downstream helpers run" in text
    assert "- Capturing runtime metadata for later lineage, review, or handover steps" in text
    assert "### Parameters" in text
    assert "`config` :" in text
    assert ", required" in text or ", optional" in text
    assert "### Public callable source code" in text


def test_public_callables_have_one_canonical_full_content_page() -> None:
    manifest = json.loads((REFERENCE_DIR / "function-manifest.json").read_text(encoding="utf-8"))
    public_names = sorted({entry["name"] for entry in manifest if entry.get("classification") == "Callable"})

    assert public_names
    for name in public_names:
        canonical_page = API_REFERENCE_DIR / f"{name}.md"
        legacy_page = REFERENCE_DIR / "callables" / f"{name}.md"
        assert canonical_page.exists(), name
        assert not legacy_page.exists(), f"{legacy_page} duplicates canonical full-content page"
        text = canonical_page.read_text(encoding="utf-8")
        assert "## At a glance" in text, canonical_page
        assert "## Internal implementation summary" in text, canonical_page

    generated_pages = sorted(page.stem for page in API_REFERENCE_DIR.glob("*.md"))
    assert generated_pages == public_names


def test_generated_manifests_point_public_callables_to_canonical_api_reference() -> None:
    function_manifest = json.loads((REFERENCE_DIR / "function-manifest.json").read_text(encoding="utf-8"))
    agent_manifest = json.loads((REFERENCE_DIR / "agent-manifest.json").read_text(encoding="utf-8"))

    for entry in function_manifest:
        if entry.get("classification") == "Callable":
            assert entry["docs_path"] == f"api/reference/{entry['name']}.md"
        elif entry.get("docs_path") is not None:
            assert entry["docs_path"].startswith("reference/internal/")

    for entry in agent_manifest:
        if entry.get("type") == "callable":
            assert entry["docs_path"] == f"api/reference/{entry['name']}.md"
        elif entry.get("docs_path") is not None:
            assert entry["docs_path"].startswith("reference/internal/")



def test_glossary_page_exists_and_includes_required_terms() -> None:
    glossary_page = REFERENCE_DIR / "glossary.md"
    glossary_source = REFERENCE_DIR / "glossary.json"
    required_terms = {
        "profile behavior",
        "accepted catalogue profile evidence",
        "baseline profile",
        "stage",
        "profile behavior check",
        "guardrail",
        "can_continue",
        "append",
        "overwrite",
        "skip",
        "metadata lakehouse",
        "catalogue evidence",
        "source table",
        "target table",
        "notebook template",
    }

    assert glossary_page.exists()
    assert glossary_source.exists()
    glossary_entries = json.loads(glossary_source.read_text(encoding="utf-8"))
    terms = {entry["term"] for entry in glossary_entries}
    assert required_terms <= terms

    glossary_text = glossary_page.read_text(encoding="utf-8")
    for term in required_terms:
        assert f"## {term}" in glossary_text
    assert "**Plain language:**" in glossary_text


def test_enforce_profile_behavior_renders_glossary_backed_api_guidance() -> None:
    function_manifest = json.loads((REFERENCE_DIR / "function-manifest.json").read_text(encoding="utf-8"))
    entry = next(item for item in function_manifest if item["name"] == "enforce_profile_behavior")
    text = (API_REFERENCE_DIR / "enforce_profile_behavior.md").read_text(encoding="utf-8")

    assert "profile behavior" in entry["glossary_terms"]
    assert "can_continue" in entry["glossary_terms"]
    assert "### Key terms" in text
    assert "**Profile behavior:** The expected way a table is loaded." in text
    assert "**can_continue:** A returned true/false value that tells downstream code whether the pipeline should keep running." in text
    assert "See the [full glossary](../../reference/glossary/)" in text
    assert "previously approved as append-only" in text
    assert "overwrite could remove existing history" in text
    assert "If can_continue is false, review whether the behavior change is intentional before writing the table." in text
    assert "The part of the pipeline being checked, such as source or target." in text


def test_public_callable_pages_do_not_repeat_intro_as_exact_purpose() -> None:
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
    forbidden = (
        "This API reference documents the callable summarized above",
        "Interpret the returned value according to the Returns section above",
        "No common failure causes are documented beyond the Errors section",
    )
    for page in sorted(API_REFERENCE_DIR.glob("*.md")):
        text = page.read_text(encoding="utf-8")
        for phrase in forbidden:
            assert phrase not in text, page

def test_template_usage_metadata_renders_from_structured_reference_model() -> None:
    function_manifest = json.loads((REFERENCE_DIR / "function-manifest.json").read_text(encoding="utf-8"))
    agent_manifest = json.loads((REFERENCE_DIR / "agent-manifest.json").read_text(encoding="utf-8"))
    dependency_metadata = json.loads((REFERENCE_DIR / "dependency-metadata.json").read_text(encoding="utf-8"))
    reference_index = (REFERENCE_DIR / "index.md").read_text(encoding="utf-8")

    function_by_name = {entry["name"]: entry for entry in function_manifest}
    agent_by_name = {entry["name"]: entry for entry in agent_manifest if entry.get("type") == "callable"}
    dependency_by_name = {entry["callable"]: entry for entry in dependency_metadata["callables"].values()}

    for callable_name in ("enforce_freshness", "enforce_profile_behavior"):
        assert function_by_name[callable_name]["used_in_templates"] == ["02_pipeline"]
        assert agent_by_name[callable_name]["used_in_templates"] == ["02_pipeline"]
        assert dependency_by_name[callable_name]["used_in_templates"] == ["02_pipeline"]

        article_start = reference_index.index(f'data-callable-name="{callable_name}"')
        article_end = reference_index.index("</article>", article_start)
        article = reference_index[article_start:article_end]
        assert '<p class="reference-catalogue-item-used-in"><strong>Used in:</strong> 02_pipeline</p>' in article
        assert article.count("Used in:") == 1
        assert "Outbound" in article or "Inbound" in article

        detail_text = (API_REFERENCE_DIR / f"{callable_name}.md").read_text(encoding="utf-8")
        assert "## Used in templates" in detail_text
        used_in_section = _section_text(detail_text, "Used in templates")
        assert used_in_section.count("`02_pipeline`") == 1


def test_callable_parameters_render_as_definition_list_not_table() -> None:
    text = (API_REFERENCE_DIR / "enforce_profile_behavior.md").read_text(encoding="utf-8")
    parameters = _subsection_text(text, "Parameters")

    assert "| Parameter | Required | Meaning |" not in parameters
    assert "<table" not in parameters
    assert '<div class="module-table-scroll reference-input-table">' not in parameters
    assert "`dataset_name` : `str`, required" in parameters
    assert ": Dataset name used to find matching catalogue evidence." in parameters
    assert "`stage` : `str`, required" in parameters
    assert ": The part of the pipeline being checked, such as source or target." in parameters
    assert "`exclude_run_id` : `str | None`, optional" in parameters


def test_enforce_profile_behavior_preserves_relationship_sections_after_readability_changes() -> None:
    text = (API_REFERENCE_DIR / "enforce_profile_behavior.md").read_text(encoding="utf-8")

    used_by = _section_text(text, "Used by")
    calls = _section_text(text, "Calls")
    assert "fabricops_kit.pipeline.run_table_guardrails" in used_by
    assert "fabricops_kit.data_profiling.profile_dataframe" in calls
    assert "fabricops_kit.fabric_input_output.read_lakehouse_table" in calls

def test_generated_public_callable_links_use_canonical_route() -> None:
    generated_markdown = [
        REFERENCE_DIR / "index.md",
        REFERENCE_DIR / "template-function-map.md",
        *sorted((ROOT / "docs" / "api" / "modules").glob("*.md")),
        *sorted(API_REFERENCE_DIR.glob("*.md")),
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in generated_markdown if path.exists())

    assert "/reference/callables/" not in combined
    assert "../callables/" not in combined
    combined_without_glossary_links = combined.replace("../../reference/glossary/", "")
    assert "../../reference/" not in combined_without_glossary_links
    assert "api/reference/" in combined
    assert "../api/reference/enforce_dq_rules/" in combined
    assert "../reference/enforce_dq_rules/" in combined


def test_enforce_dq_rules_canonical_page_section_order_and_no_old_helper_dump() -> None:
    text = (API_REFERENCE_DIR / "enforce_dq_rules.md").read_text(encoding="utf-8")
    ordered_markers = [
        "## When to use this",
        "## At a glance",
        "## Used in templates",
        "## Used by",
        "## Calls",
        "## Function details and source",
        "### Function details",
        "### Public callable source code",
        "## Internal implementation summary",
        '<summary>AI / machine-readable metadata',
    ]
    if "## Purpose" in text:
        ordered_markers.insert(0, "## Purpose")

    assert [text.index(marker) for marker in ordered_markers] == sorted(text.index(marker) for marker in ordered_markers)
    assert "Internal helpers used by this callable" not in text
