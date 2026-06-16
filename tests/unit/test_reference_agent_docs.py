"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import json
import re
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
    "enforce_freshness",
    "enforce_profile_behavior",
    "stop_if_failed",
    "enforce_dq_rules",
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
    section = section.split("\n<details class=\"reference-metadata-details\">", 1)[0]
    return section.strip()


def _subsection_text(page_text: str, subsection: str) -> str:
    marker = f"### {subsection}\n"
    assert marker in page_text
    after = page_text.split(marker, 1)[1]
    return after.split("\n### ", 1)[0].strip()


def test_reference_ai_manifest_files_exist_and_are_valid_json() -> None:
    """Verify reference ai manifest files exist and are valid json."""
    agent_manifest = REFERENCE_DIR / "agent-manifest.json"
    function_manifest = REFERENCE_DIR / "function-manifest.json"

    assert agent_manifest.exists()
    assert function_manifest.exists()
    assert json.loads(agent_manifest.read_text(encoding="utf-8"))
    assert json.loads(function_manifest.read_text(encoding="utf-8"))


def test_fabricops_skill_file_exists() -> None:
    """Verify fabricops skill file exists."""
    assert (ROOT / ".agents" / "skills" / "fabricops" / "SKILL.md").exists()


def test_every_callable_page_has_ai_reference_sections() -> None:
    """Verify every callable page has ai reference sections."""
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
        assert "**Used in templates:**" in text, page
        assert "## Relationships" in text, page
        assert "### Used by" in text, page
        assert "### Calls" in text, page
        assert "## Implementation details" in text, page
        assert "## Source link" not in text, page
        assert '??? example "Source code"' not in text, page
        assert '??? example "View helper source by area"' not in text, page
        assert text.count('<div class="reference-source-card" markdown="1">') == 1, page
        assert "## Nested helper functions" not in text, page
        assert "\n## Source\n" not in text, page
        assert "\n## What this is for\n" not in text, page
        assert "\n## When to use it\n" not in text, page
        assert "\n## Raises\n" not in text, page
        assert "\n## Side effects\n" not in text, page
        assert "## AI / machine-readable metadata" not in text, page
        assert "<summary>Machine-readable metadata / metadata details</summary>" in text, page


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
    assert """```python
setup_metadata_tables(
    spark=spark,
    config=CONFIG,
    env="Sandbox",
)
```""" in example

def test_core_agent_manifest_entries_have_non_placeholder_ai_fields() -> None:
    """Verify core agent manifest entries have non placeholder ai fields."""
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
    """Verify standalone internal pages are not generated by default."""
    internal_pages = sorted((REFERENCE_DIR / "internal").glob("*.md"))

    assert internal_pages == []


def test_callable_pages_embed_public_first_implementation_details() -> None:
    """Verify callable pages embed public first implementation details."""
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
            "## Relationships",
            "### Used by",
            "### Calls",
            "## Implementation details",
            '<summary>Machine-readable metadata / metadata details',
            "## See also",
        ]
        if "### Return interpretation" in text:
            ordered_markers.insert(ordered_markers.index("## Raises / Errors"), "### Return interpretation")
        if "### Common failure causes" in text:
            ordered_markers.insert(ordered_markers.index("## Relationships"), "### Common failure causes")
        positions = [text.index(marker) for marker in ordered_markers]
        assert positions == sorted(positions), page
        assert '??? info "Call flow"' in text, page
        assert "### Call flow" not in text, page
        assert "### Internal helpers used by this callable" not in text, page
        assert "Internal helpers used by this callable" not in text, page
        assert '??? info "Nested helper functions:' not in text, page
        assert '??? info "Internal helpers used:' in text, page
        assert 'class="reference-helper-groups"' in text, page
        source_card_pos = text.index('<div class="reference-source-card" markdown="1">')
        signature_pos = text.index("## Signature")
        implementation_pos = text.index("## Implementation details")
        call_flow_pos = text.index('??? info "Call flow"')
        assert source_card_pos < signature_pos < implementation_pos < call_flow_pos, page
        assert '??? example "View helper source by area"' not in text, page
        assert '??? example "Source code"' not in text, page
        assert "\n### `_" not in text, page
        assert "\n## `_" not in text, page
        assert implementation_pos < text.index("<summary>Machine-readable metadata / metadata details"), page



def test_enforce_profile_behavior_reference_uses_distinct_blocks_and_responsive_helpers() -> None:
    """Verify enforce profile behavior reference uses distinct blocks and responsive helpers."""
    text = (API_REFERENCE_DIR / "enforce_profile_behavior.md").read_text(encoding="utf-8")

    assert 'class="reference-api-definition"' in _section_text(text, "Signature")
    example = _section_text(text, "Example usage")
    assert 'class="reference-example-usage"' in example
    assert "dataframe=df" in example
    assert 'dataset_name="sales_orders"' in example
    assert 'table_name="orders_raw"' in example
    assert 'profile_mode="changing_data"' in example
    assert '<table class="reference-function-table">' not in _section_text(text, "Implementation details")
    for area in (
        "Metadata loading",
        "Rule parsing",
        "Profile comparison",
        "Column handling",
    ):
        assert f"<h4>{area}</h4>" in text
    for helper_name in (
        "_is_missing_table_error",
        "_normalize_profile",
        "_catalogue_value",
        "_guardrail_exclude_columns",
    ):
        assert 'class="reference-helper-chip"' in text
        assert f"<code>{helper_name}</code>" in text
        assert re.search(
            rf'<a class="reference-helper-chip" href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/[^"]+#L\d+(?:-L\d+)?"><code>{helper_name}</code></a>',
            text,
        )

def test_enforce_dq_rules_large_helper_set_is_grouped_by_area() -> None:
    """Verify enforce dq rules large helper set is grouped by area."""
    text = (API_REFERENCE_DIR / "enforce_dq_rules.md").read_text(encoding="utf-8")

    assert '<table class="reference-function-table">' not in _section_text(text, "Implementation details")
    assert "enforce_dq_rules(...)" in text
    assert "Expanded internal helper tree is available in Implementation details." in text
    assert text.index('<div class="reference-source-card" markdown="1">') < text.index("## Signature")
    assert text.index("## Implementation details") < text.index('??? info "Call flow"')
    assert '??? example "View helper source by area"' not in text


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


def test_github_source_url_uses_configured_source_ref(monkeypatch) -> None:
    """Verify github source url uses configured source ref."""
    monkeypatch.setenv("GITHUB_SOURCE_REF", "review-sha-123")

    from scripts.generate_function_reference import github_source_url

    assert github_source_url("src/fabricops_kit/config.py", 595, 704) == (
        "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/"
        "review-sha-123/src/fabricops_kit/config.py#L595-L704"
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


def test_callable_pages_include_one_top_source_card_and_github_source_link() -> None:
    """Verify callable pages include one top source card and github source link."""
    callable_pages = sorted(API_REFERENCE_DIR.glob("*.md"))

    assert callable_pages
    for page in callable_pages:
        text = page.read_text(encoding="utf-8")
        assert "## Source link" not in text, page
        assert text.count('<div class="reference-source-card" markdown="1">') == 1, page
        source_start = text.index('<div class="reference-source-card" markdown="1">')
        source_end = text.index("</div>", source_start)
        source_card = text[source_start:source_end]
        assert source_start < text.index("## Signature"), page
        assert "**Source**" in source_card, page
        assert "View on GitHub" in source_card, page
        assert "https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/" in source_card, page
        assert "/src/fabricops_kit/" in source_card, page
        assert "#L" in source_card, page


def test_callable_pages_collapse_ai_machine_metadata() -> None:
    """Verify callable pages collapse ai machine metadata."""
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
        assert "<summary>Machine-readable metadata / metadata details</summary>" in text, page
        metadata_start = text.index("<summary>Machine-readable metadata / metadata details")
        metadata_end = text.index("</details>", metadata_start)
        metadata = text[metadata_start:metadata_end]
        assert "### Function manifest" in metadata, page
        assert "### AI implementation contract" in metadata, page
        assert "### Inbound references" in metadata, page
        assert "### Outbound references" in metadata, page
        assert "### Raw source metadata" in metadata, page


def test_setup_notebook_reference_uses_human_first_source_documentation() -> None:
    """Verify setup notebook reference uses human first source documentation."""
    text = (API_REFERENCE_DIR / "setup_notebook.md").read_text(encoding="utf-8")

    assert "../../api/modules/config/#setup_notebook" not in text
    assert "src/fabricops_kit/config.py#L" in text
    assert "View on GitHub" in text
    assert text.count('<div class="reference-source-card" markdown="1">') == 1
    assert "## Example usage" in text
    assert "context = setup_notebook" in _section_text(text, "Example usage")
    first_metadata = text.index("<summary>Machine-readable metadata / metadata details")
    for marker in ("## Signature", "## Parameters", "## Returns"):
        assert text.index(marker) < first_metadata
    assert "## AI / machine-readable metadata" not in text
    assert "- Starting a FabricOps notebook from 00_env_config" in text
    assert "- Validating configured environment targets before downstream helpers run" in text
    assert "- Capturing runtime metadata for later lineage, review, or handover steps" in text
    assert "## Parameters" in text
    assert "| `config` |" in text
    assert "| Yes |" in text or "| No |" in text
    assert "## Source link" not in text


def test_public_callables_have_one_canonical_full_content_page() -> None:
    """Verify public callables have one canonical full content page."""
    manifest = json.loads((REFERENCE_DIR / "function-manifest.json").read_text(encoding="utf-8"))
    public_names = sorted({entry["name"] for entry in manifest if entry.get("classification") == "Callable"})

    assert public_names
    for name in public_names:
        canonical_page = API_REFERENCE_DIR / f"{name}.md"
        legacy_page = REFERENCE_DIR / "callables" / f"{name}.md"
        assert canonical_page.exists(), name
        assert not legacy_page.exists(), f"{legacy_page} duplicates canonical full-content page"
        text = canonical_page.read_text(encoding="utf-8")
        assert "## Relationships" in text, canonical_page
        assert "## Implementation details" in text, canonical_page

    generated_pages = sorted(page.stem for page in API_REFERENCE_DIR.glob("*.md"))
    assert generated_pages == public_names


def test_generated_manifests_point_public_callables_to_canonical_api_reference() -> None:
    """Verify generated manifests point public callables to canonical api reference."""
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
    """Verify glossary page exists and includes required terms."""
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



def test_public_callable_records_have_real_metadata_backed_guidance() -> None:
    """Verify public callable records have real metadata backed guidance."""
    function_manifest = json.loads((REFERENCE_DIR / "function-manifest.json").read_text(encoding="utf-8"))
    public_records = [entry for entry in function_manifest if entry.get("classification") == "Callable"]

    assert public_records
    for entry in public_records:
        assert entry.get("expanded_purpose"), entry["name"]
        assert entry.get("when_to_use"), entry["name"]
        assert entry.get("return_interpretation"), entry["name"]
        assert entry.get("common_failure_causes"), entry["name"]


def test_callable_pages_with_glossary_terms_render_shared_key_terms() -> None:
    """Verify callable pages with glossary terms render shared key terms."""
    function_manifest = json.loads((REFERENCE_DIR / "function-manifest.json").read_text(encoding="utf-8"))
    glossary_entries = json.loads((REFERENCE_DIR / "glossary.json").read_text(encoding="utf-8"))
    glossary = {entry["term"]: entry["plain_language_definition"] for entry in glossary_entries}

    for entry in function_manifest:
        if entry.get("classification") != "Callable" or not entry.get("glossary_terms"):
            continue
        text = (API_REFERENCE_DIR / f"{entry['name']}.md").read_text(encoding="utf-8")
        key_terms = _section_text(text, "Glossary")
        for term in entry["glossary_terms"]:
            label = term if "_" in term else term.capitalize()
            assert f"**{label}:** {glossary[term]}" in key_terms, entry["name"]

def test_enforce_profile_behavior_renders_glossary_backed_api_guidance() -> None:
    """Verify enforce profile behavior renders glossary backed api guidance."""
    function_manifest = json.loads((REFERENCE_DIR / "function-manifest.json").read_text(encoding="utf-8"))
    entry = next(item for item in function_manifest if item["name"] == "enforce_profile_behavior")
    text = (API_REFERENCE_DIR / "enforce_profile_behavior.md").read_text(encoding="utf-8")

    assert "profile behavior" in entry["glossary_terms"]
    assert "can_continue" in entry["glossary_terms"]
    assert "## Glossary" in text
    assert "<summary>Glossary terms</summary>" in text
    assert "**Profile behavior:** The expected way a table profile should behave over time." in text
    assert "**can_continue:** A returned true/false value that tells downstream code whether the pipeline should keep running." in text
    assert "See the [full glossary](../../../reference/glossary/)" in text
    assert "full-table static data changes unexpectedly" in text
    assert "previous watermark group changes or disappears" in text
    assert "If can_continue is false, review whether the behavior change is intentional before writing the table." in text
    assert "The part of the pipeline being checked, such as source or target." in text


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
    function_manifest = json.loads((REFERENCE_DIR / "function-manifest.json").read_text(encoding="utf-8"))
    agent_manifest = json.loads((REFERENCE_DIR / "agent-manifest.json").read_text(encoding="utf-8"))
    function_by_name = {entry["name"]: entry for entry in function_manifest if entry.get("classification") == "Callable"}
    agent_by_name = {entry["name"]: entry for entry in agent_manifest if entry.get("type") == "callable"}

    related_guides = function_by_name["run_table_guardrails"]["related_guides"]
    assert related_guides == [
        {"title": "Pipeline Guardrails", "path": "../../how-fabricops-works/pipeline-guardrails.md"}
    ]
    assert agent_by_name["run_table_guardrails"]["related_guides"] == related_guides

    text = (API_REFERENCE_DIR / "run_table_guardrails.md").read_text(encoding="utf-8")
    assert "## See also" in text
    assert "- [Pipeline Guardrails](../../how-fabricops-works/pipeline-guardrails.md)" in text
    assert text.index("## Implementation details") < text.index("## See also")


def test_concept_pages_link_back_to_key_callable_references() -> None:
    """Verify concept pages link back to key callable references."""
    notebook_templates = (ROOT / "docs" / "how-fabricops-works" / "notebook-templates.md").read_text(encoding="utf-8")
    pipeline_guardrails = (ROOT / "docs" / "how-fabricops-works" / "pipeline-guardrails.md").read_text(encoding="utf-8")
    governance_review = (ROOT / "docs" / "how-fabricops-works" / "governance-review.md").read_text(encoding="utf-8")
    metadata_tables = (ROOT / "docs" / "how-fabricops-works" / "metadata-tables.md").read_text(encoding="utf-8")

    assert "[setup_notebook](../api/reference/setup_notebook/)" in notebook_templates
    assert "[prepare_pipeline_table_configs](../api/reference/prepare_pipeline_table_configs/)" in notebook_templates
    assert "[widget_select_guardrail_target](../api/reference/widget_select_guardrail_target/)" in notebook_templates
    assert "[run_table_guardrails](../api/reference/run_table_guardrails/)" in pipeline_guardrails
    assert "[enforce_profile_behavior](../api/reference/enforce_profile_behavior/)" in pipeline_guardrails
    assert "[stop_if_failed](../api/reference/stop_if_failed/)" in pipeline_guardrails
    assert "[widget_select_guardrail_target](../api/reference/widget_select_guardrail_target/)" in governance_review
    assert "[widget_review_guardrail_governance](../api/reference/widget_review_guardrail_governance/)" in governance_review
    assert "[setup_metadata_tables](../api/reference/setup_metadata_tables/)" in metadata_tables
    assert "[write_pipeline_lineage](../api/reference/write_pipeline_lineage/)" in metadata_tables


def test_template_usage_metadata_renders_from_structured_reference_model() -> None:
    """Verify template usage metadata renders from structured reference model."""
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
        assert "**Used in templates:**" in detail_text
        assert detail_text.count("`02_pipeline`") == 1


def test_callable_parameters_render_as_api_table() -> None:
    """Verify callable parameters render as api table."""
    text = (API_REFERENCE_DIR / "enforce_profile_behavior.md").read_text(encoding="utf-8")
    parameters = _section_text(text, "Parameters")

    assert "| Parameter | Type | Required | Description |" in parameters
    assert "| `dataset_name` | `str` | Yes | Dataset name used to find matching catalogue evidence. |" in parameters
    assert "| `stage` | `str` | Yes | The part of the pipeline being checked, such as source or target. |" in parameters
    assert r"| `exclude_run_id` | `str \| None` | No |" in parameters


def test_enforce_profile_behavior_preserves_relationship_sections_after_readability_changes() -> None:
    """Verify enforce profile behavior preserves relationship sections after readability changes."""
    text = (API_REFERENCE_DIR / "enforce_profile_behavior.md").read_text(encoding="utf-8")

    used_by = _section_text(text, "Used by")
    calls = _section_text(text, "Calls")
    assert "fabricops_kit.pipeline.run_table_guardrails" in used_by
    assert "fabricops_kit.data_profiling.profile_dataframe" in calls
    assert "fabricops_kit.fabric_input_output.read_lakehouse_table" in calls


def test_mkdocs_nav_registers_callable_pages_under_function_list() -> None:
    """Verify mkdocs nav registers callable pages under function list."""
    mkdocs_text = (ROOT / "mkdocs.yml").read_text(encoding="utf-8")
    function_manifest = json.loads((REFERENCE_DIR / "function-manifest.json").read_text(encoding="utf-8"))
    public_names = sorted(entry["name"] for entry in function_manifest if entry.get("classification") == "Callable")

    assert "      - List of functions:\n          - Overview: reference/index.md" in mkdocs_text
    assert "          # AUTO-GENERATED-FUNCTIONS-START" in mkdocs_text
    assert "          # AUTO-GENERATED-FUNCTIONS-END" in mkdocs_text
    for name in public_names:
        assert f"          - {name}: api/reference/{name}.md" in mkdocs_text


def test_generated_public_callable_links_use_canonical_route() -> None:
    """Verify generated public callable links use canonical route."""
    generated_markdown = [
        REFERENCE_DIR / "index.md",
        REFERENCE_DIR / "template-function-map.md",
        *sorted((ROOT / "docs" / "api" / "modules").glob("*.md")),
        *sorted(API_REFERENCE_DIR.glob("*.md")),
    ]
    combined = "\n".join(path.read_text(encoding="utf-8") for path in generated_markdown if path.exists())

    assert "/reference/callables/" not in combined
    assert "../callables/" not in combined
    combined_without_glossary_links = combined.replace("../../../reference/glossary/", "")
    assert "api/reference/" in combined_without_glossary_links
    assert "../api/reference/enforce_dq_rules/" in combined
    assert "../../reference/enforce_dq_rules/" in combined
    assert "api/modules/reference/" not in combined
    assert 'href="../reference/enforce_dq_rules/"' not in combined


def test_enforce_dq_rules_canonical_page_section_order_and_no_old_helper_dump() -> None:
    """Verify enforce dq rules canonical page section order and no old helper dump."""
    text = (API_REFERENCE_DIR / "enforce_dq_rules.md").read_text(encoding="utf-8")
    ordered_markers = [
        "## Signature",
        "## Example usage",
        "## Parameters",
        "## Returns",
        "## Raises / Errors",
        "## Relationships",
        "### Used by",
        "### Calls",
        "## Implementation details",
        '<summary>Machine-readable metadata / metadata details',
        "## See also",
    ]
    assert [text.index(marker) for marker in ordered_markers] == sorted(text.index(marker) for marker in ordered_markers)
    assert "Internal helpers used by this callable" not in text
