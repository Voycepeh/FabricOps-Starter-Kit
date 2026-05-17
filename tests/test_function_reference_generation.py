from __future__ import annotations

import ast
from pathlib import Path

from scripts.generate_function_reference import main as generate_reference

ROOT = Path(__file__).resolve().parents[1]
INIT_FILE = ROOT / "src" / "fabricops_kit" / "__init__.py"
REFERENCE_FILE = ROOT / "docs" / "reference" / "index.md"
FUNCTION_USAGE_GUIDE_FILE = ROOT / "docs" / "reference" / "function-usage-guide.md"
DOCS_METADATA_FILE = ROOT / "src" / "fabricops_kit" / "docs_metadata.py"
CALLABLE_MAP_FILE = ROOT / "docs" / "reference" / "callable-map.md"


def public_exports() -> list[str]:
    tree = ast.parse(INIT_FILE.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "__all__" for t in node.targets):
            return [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant)]
    raise AssertionError("__all__ missing")


def metadata_literal(name: str) -> list[dict[str, object]]:
    tree = ast.parse(DOCS_METADATA_FILE.read_text(encoding="utf-8"))
    for node in tree.body:
        is_assign = isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
        is_annassign = isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name
        if (is_assign or is_annassign) and node.value is not None:
            return ast.literal_eval(node.value)
    raise AssertionError(f"{name} missing")


def notebook_source_text(path: str) -> str:
    import json

    notebook = json.loads((ROOT / path).read_text(encoding="utf-8"))
    return "\n".join("".join(cell.get("source", [])) for cell in notebook["cells"] if cell.get("cell_type") == "code")


def markdown_section(content: str, heading: str) -> str:
    start_token = f"## {heading}\n"
    start = content.find(start_token)
    if start < 0:
        return ""
    rest = content[start + len(start_token) :]
    next_idx = rest.find("\n## ")
    return rest if next_idx < 0 else rest[:next_idx]


def all_public_functions_section(content: str) -> str:
    """Return the rendered All public functions section body."""
    return markdown_section(content, "All public functions")


def test_reference_generator_runs_without_fabric_runtime() -> None:
    generate_reference()
    assert REFERENCE_FILE.exists()


def function_exports() -> list[str]:
    metadata_rows = metadata_literal("PUBLIC_SYMBOL_DOCS")
    return [row["symbol_name"] for row in metadata_rows if row.get("kind") == "function"]


def test_every_public_function_is_listed_exactly_once_in_function_catalogue() -> None:
    generate_reference()
    content = REFERENCE_FILE.read_text(encoding="utf-8")
    all_functions = all_public_functions_section(content)
    assert all_functions
    for name in function_exports():
        assert all_functions.count(f"<code>{name}</code>") == 1


def test_reference_contains_required_sections_and_no_notebook_segments() -> None:
    generate_reference()
    content = REFERENCE_FILE.read_text(encoding="utf-8")
    assert "## Start from the templates" not in content
    assert "## What runs where" not in content
    assert "## Find a callable" in content
    assert "## Function catalogue" in content
    assert "## Starter path functions" not in content
    assert "## Additional public functions" not in content


def test_reference_no_longer_contains_old_step_headings() -> None:
    generate_reference()
    content = REFERENCE_FILE.read_text(encoding="utf-8")
    assert "## Lifecycle flow" not in content
    assert "## Callable map by workflow step" not in content
    assert "## Step 1:" not in content
    assert "## Step 2A:" not in content


def test_function_catalogue_contains_compact_items_and_search_metadata() -> None:
    generate_reference()
    content = REFERENCE_FILE.read_text(encoding="utf-8")
    assert "## Function catalogue" in content
    assert '<div class="reference-catalogue-list">' in content
    assert '<table class="reference-catalogue-table">' not in content
    assert 'class="reference-catalogue-item"' in content
    assert '<a href="../api/reference/load_config/"><code>load_config</code></a>' in content
    assert "data-callable-row" in content
    assert "data-callable-name=" in content
    assert "data-callable-purpose=" in content
    assert 'href="../api/reference/review_dq_rule_deactivations/"' in content


def test_reference_includes_callable_finder_block() -> None:
    generate_reference()
    content = REFERENCE_FILE.read_text(encoding="utf-8")
    assert "## Find a callable" in content
    assert 'data-callable-finder' in content
    assert 'id="callable-finder-input"' in content
    assert 'data-callable-finder-empty' in content
    assert content.index("## Find a callable") < content.index("## Function catalogue")


def test_reference_callable_finder_exposes_only_public_role_filters() -> None:
    generate_reference()
    content = REFERENCE_FILE.read_text(encoding="utf-8")
    assert 'data-role-filter="essential"' in content
    assert 'data-role-filter="optional"' in content
    assert 'data-role-filter="internal"' not in content
    assert "Search callable functions" in content
    assert "<strong>Essential</strong>: Core functions used in the starter notebook flow." in content
    assert "<strong>Optional</strong>: Extra helper functions for advanced or situational use." in content


def test_callable_finder_js_uses_public_role_total_and_tokenized_matching() -> None:
    source = (ROOT / "docs/javascripts/callable-finder.js").read_text(encoding="utf-8")
    assert 'const publicRoles = new Set(["essential", "optional"]);' in source
    assert 'split(/[\\s_./-]+/)' in source
    assert 'queryTokens.every((queryToken) =>' in source
    assert 'if (isInPublicScope && roles.has(entry.role)) total += 1;' in source
    assert 'const show = isInPublicScope && score > 0 && roles.has(entry.role);' in source


def test_function_reference_tables_use_compact_module_links() -> None:
    generate_reference()
    content = REFERENCE_FILE.read_text(encoding="utf-8")
    assert 'class="reference-module-link"' in content
    assert '<div class="reference-catalogue-list">' in content
    assert 'api-chip api-chip-module api-chip-link' not in content


def test_non_starter_callable_still_appears_in_complete_catalogue() -> None:
    generate_reference()
    content = REFERENCE_FILE.read_text(encoding="utf-8")
    all_functions = all_public_functions_section(content)
    assert "<code>read_lakehouse_csv</code>" in all_functions


def test_reference_tables_include_mobile_friendly_classes_and_data_labels() -> None:
    generate_reference()
    content = FUNCTION_USAGE_GUIDE_FILE.read_text(encoding="utf-8")
    assert '<table class="reference-template-table">' in content
    assert 'data-label="Notebook"' in content
    assert 'data-label="Guided usage"' in content


def test_reference_html_tables_use_anchor_links_not_markdown_links() -> None:
    generate_reference()
    content = FUNCTION_USAGE_GUIDE_FILE.read_text(encoding="utf-8")
    assert '<td data-label="Full template"><a href="https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/templates/notebooks/00_env_config.ipynb">Open notebook</a></td>' in content
    assert 'step-02a-shared-runtime-config/FabricStore' not in content
    assert "[`Open notebook`](" not in content
    assert "<code>`00_env_config`</code>" not in content


def test_docs_metadata_matches_public_exports() -> None:
    exports = set(public_exports())
    metadata_symbols = {row["symbol_name"] for row in metadata_literal("PUBLIC_SYMBOL_DOCS")}
    assert exports == metadata_symbols


def test_public_reference_metadata_excludes_legacy_and_internal_symbols() -> None:
    metadata_symbols = {row["symbol_name"] for row in metadata_literal("PUBLIC_SYMBOL_DOCS")}
    assert "get_path" not in metadata_symbols
    assert "Housepath" not in metadata_symbols
    assert "_get_store" not in metadata_symbols


def test_reference_file_is_in_sync_with_generator() -> None:
    before = REFERENCE_FILE.read_text(encoding="utf-8")
    generate_reference()
    after = REFERENCE_FILE.read_text(encoding="utf-8")
    assert after == before


def test_generated_docs_are_multiline_readable_and_lf_safe() -> None:
    generate_reference()
    text = REFERENCE_FILE.read_text(encoding="utf-8")
    assert text.count("\n") > 20
    assert "\r\n" not in text


def test_callable_map_generated_with_required_sections() -> None:
    generate_reference()
    assert CALLABLE_MAP_FILE.exists()
    content = CALLABLE_MAP_FILE.read_text(encoding="utf-8")
    assert "# Callable Map" in content
    assert "## 1. Module dependency graph" in content
    assert "```mermaid" in content
    assert "## 2. Public callables by module" in content
    assert "## 3. Internal helper index" in content
    assert "## 4. Cross-module FabricOps calls" in content
    assert "## 5. Module dependency summary" in content


def test_callable_map_has_static_markdown_tables() -> None:
    generate_reference()
    content = CALLABLE_MAP_FILE.read_text(encoding="utf-8")
    assert "| Module | Public callable | Referenced by |" in content
    assert "| Module | Internal helper | Called by public callables |" in content
    assert "| Caller | Callee | Callee kind |" in content


def test_gen_ref_pages_has_no_html_callable_map_dependency() -> None:
    source = (ROOT / "docs" / "gen_ref_pages.py").read_text(encoding="utf-8")
    assert "callable-map.html" not in source


def test_gen_ref_pages_template_has_no_iframe_and_includes_relationship_table() -> None:
    source = (ROOT / "docs" / "gen_ref_pages.py").read_text(encoding="utf-8")
    assert "<iframe" not in source
    assert "| Relationship | Callables |" in source


def test_template_flow_symbols_are_exported() -> None:
    exports = set(public_exports())
    template_docs = metadata_literal("TEMPLATE_FLOW_DOCS")
    for notebook in template_docs:
        for segment in notebook["segments"]:
            for symbol in segment["symbols"]:
                assert symbol in exports




def test_mkdocs_gen_ref_pages_uses_static_analysis_not_package_import() -> None:
    gen_file = ROOT / "docs" / "gen_ref_pages.py"
    source = gen_file.read_text(encoding="utf-8")
    tree = ast.parse(source)

    assert 'from fabricops_kit' not in source
    assert 'importlib.import_module("fabricops_kit")' not in source

    called_read_literal = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == '_read_literal':
            called_read_literal = True
    assert called_read_literal


def test_template_flow_registry_matches_expected_symbol_sets() -> None:
    template_docs = metadata_literal("TEMPLATE_FLOW_DOCS")
    symbols_by_notebook: dict[str, set[str]] = {}
    for notebook in template_docs:
        symbols = symbols_by_notebook.setdefault(notebook["notebook_key"], set())
        for segment in notebook["segments"]:
            symbols.update(segment["symbols"])

    assert set(symbols_by_notebook) == {"00_env_config", "01_data_agreement", "02_ex", "03_pc"}
    assert {"setup_notebook", "load_config", "load_config"}.issubset(symbols_by_notebook["00_env_config"])
    assert {"draft_dq_rules", "review_dq_rules", "profile_dataframe"}.issubset(symbols_by_notebook["02_ex"])
    assert {"validate_dq_rules", "assert_dq_passed", "write_lakehouse_table"}.issubset(symbols_by_notebook["03_pc"])

def test_every_template_flow_notebook_mentions_multiple_registered_symbols() -> None:
    template_docs = metadata_literal("TEMPLATE_FLOW_DOCS")
    for notebook in template_docs:
        code = (ROOT / notebook["template_path"]).read_text(encoding="utf-8")
        mentioned = 0
        for segment in notebook["segments"]:
            for symbol in segment["symbols"]:
                if symbol in code:
                    mentioned += 1
        assert mentioned >= 3, f"Expected at least three template-flow symbols in {notebook['template_path']}"


def test_generated_notebook_detail_pages_exist_with_expected_content() -> None:
    generate_reference()
    expected = {
        "docs/notebook-structure/00-env-config.md": [
            "# `00_env_config`",
            "Open template notebook",
            "00_env_config.ipynb",
            "## Segment 2: Define environment targets and notebook policy",
            "## Segment 3: Set AI, quality, governance, and lineage defaults",
            "## Segment 4: Assemble and validate framework config",
            "## Segment 5: Run startup checks and show resolved paths",
            "<code>load_config</code>",
            "Why it is commonly used here",
            "../../api/reference/",
            "../../api/modules/",
        ],
        "docs/notebook-structure/02-exploration.md": [
            "# `02_ex_<agreement>_<topic>`",
            "Open template notebook",
            "02_ex_agreement_topic.ipynb",
            "## Segment 2: Profile source and capture evidence",
            "## Segment 3: AI-assisted drafting (advisory only)",
            "<code>draft_dq_rules</code>",
            "../../api/reference/",
            "../../api/modules/",
        ],
        "docs/notebook-structure/03-pipeline-contract.md": [
            "# `03_pc_<agreement>_<pipeline>`",
            "Open template notebook",
            "03_pc_agreement_pipeline_template.ipynb",
            "## Segment 4: Run DQ, split outputs, and publish",
            "## Optional profiling, drift, governance, lineage, and handover",
            "<code>enforce_dq</code>",
            "../../api/reference/",
            "../../api/modules/",
        ],
    }
    for path, checks in expected.items():
        content = (ROOT / path).read_text(encoding="utf-8")
        for marker in checks:
            assert marker in content
        assert 'href="../reference/' not in content
        assert 'href="../api/reference/' not in content
        assert '/step-' not in content
        assert 'href="../api/modules/' not in content


def test_no_generated_public_callable_markdown_files_committed() -> None:
    public_reference_files = sorted(
        path.name
        for path in (ROOT / "docs" / "reference").glob("*.md")
        if path.name != "index.md"
    )
    assert public_reference_files == ["callable-map.md", "function-usage-guide.md"]


def test_reference_links_to_flat_public_callable_pages() -> None:
    generate_reference()
    content = REFERENCE_FILE.read_text(encoding="utf-8")
    assert 'href="../api/reference/review_dq_rule_deactivations/"' in content
    assert 'href="../api/reference/load_config/"' in content
    assert "reference/step-" not in content
    assert "../api/reference/" in content


def test_mkdocs_reference_generator_writes_public_callable_pages_without_workflow_steps() -> None:
    source = (ROOT / "docs" / "gen_ref_pages.py").read_text(encoding="utf-8")
    assert "WORKFLOW_STEP_DOCS" not in source
    assert "reference/step-" not in source
    assert 'doc_path = f"api/reference/{symbol_name}.md"' in source
    assert "PUBLIC_SYMBOL_DOCS" in source
    assert 'row.get("kind") not in {"function", "class"}' in source


def test_generated_module_and_notebook_pages_link_to_public_callable_urls() -> None:
    generate_reference()
    environment_config = (ROOT / "docs/api/modules/config.md").read_text(encoding="utf-8")
    notebook_page = (ROOT / "docs/notebook-structure/00-env-config.md").read_text(encoding="utf-8")
    assert "../../reference/load_config/" in environment_config
    assert "../../api/reference/load_config/" in notebook_page
    assert "reference/step-" not in environment_config
    assert "reference/step-" not in notebook_page


def test_housepath_reference_page_is_generated_by_mkdocs_script() -> None:
    source = (ROOT / "docs" / "gen_ref_pages.py").read_text(encoding="utf-8")
    metadata_rows = metadata_literal("PUBLIC_SYMBOL_DOCS")
    housepath = next(row for row in metadata_rows if row["symbol_name"] == "FabricStore")
    assert housepath["kind"] == "class"
    assert 'if row.get("kind") not in {"function", "class"}:' in source


def test_notebook_structure_overview_links_to_notebook_detail_pages() -> None:
    text = (ROOT / "docs/notebook-structure.md").read_text(encoding="utf-8")
    assert "notebook-structure/00-env-config.md" in text
    assert "notebook-structure/02-exploration.md" in text
    assert "notebook-structure/03-pipeline-contract.md" in text


def test_function_usage_guide_contains_orientation_sections() -> None:
    generate_reference()
    content = FUNCTION_USAGE_GUIDE_FILE.read_text(encoding="utf-8")
    assert "# Function Usage Guide" in content
    assert "## Start from the templates" in content
    assert "## What runs where" in content


def test_notebook_pages_use_notebook_first_intro_and_table_headings() -> None:
    generate_reference()
    notebook_pages = [
        ROOT / "docs" / "notebook-structure" / "00-env-config.md",
        ROOT / "docs" / "notebook-structure" / "02-exploration.md",
        ROOT / "docs" / "notebook-structure" / "03-pipeline-contract.md",
    ]
    for page in notebook_pages:
        content = page.read_text(encoding="utf-8")
        assert "Use this page to understand the purpose and segment flow of this notebook template." in content
        assert "Callable" in content
        assert "Why it is commonly used here" in content
        assert "Function / class" not in content
        assert "functions used here per segment" not in content


def test_function_catalogue_excludes_supporting_classes_and_keeps_enforcement_callable() -> None:
    generate_reference()
    content = REFERENCE_FILE.read_text(encoding="utf-8")
    all_functions = all_public_functions_section(content)
    assert 'data-callable-name="DQEnforcementResult"' not in all_functions
    assert "<code>DQEnforcementResult</code>" not in all_functions
    assert 'data-callable-name="enforce_dq"' in all_functions


def test_function_catalogue_excludes_housepath_and_keeps_load_config() -> None:
    generate_reference()
    content = REFERENCE_FILE.read_text(encoding="utf-8")
    all_functions = all_public_functions_section(content)
    assert 'data-callable-name="FabricStore"' not in all_functions
    assert "<code>FabricStore</code>" not in all_functions
    assert 'data-callable-name="load_config"' in all_functions


def test_dq_review_functions_share_data_quality_public_module_group() -> None:
    generate_reference()
    content = REFERENCE_FILE.read_text(encoding="utf-8")
    assert 'data-callable-name="review_dq_rules" data-callable-module="data_quality"' in content
    assert 'data-callable-name="review_dq_rule_deactivations" data-callable-module="data_quality"' in content


def test_module_callable_tables_exclude_supporting_data_structures() -> None:
    generate_reference()
    data_quality_page = (ROOT / "docs/api/modules/data_quality.md").read_text(encoding="utf-8")
    fabric_io_page = (ROOT / "docs/api/modules/fabric_input_output.md").read_text(encoding="utf-8")

    assert "| [`DQEnforcementResult`]" not in data_quality_page
    assert "| [`FabricStore`]" not in fabric_io_page
    assert "| [`enforce_dq`]" in data_quality_page


def test_read_lakehouse_table_reference_excludes_legacy_housepath_tokens() -> None:
    generate_reference()
    callable_page = (ROOT / "docs" / "api" / "reference" / "read_lakehouse_table.md").read_text(encoding="utf-8")
    assert "Housepath" not in callable_page
    assert "get_path" not in callable_page


def test_read_lakehouse_table_reference_uses_config_env_target_example() -> None:
    generate_reference()
    callable_page = (ROOT / "docs" / "api" / "reference" / "read_lakehouse_table.md").read_text(encoding="utf-8")
    assert 'read_lakehouse_table(CONFIG, ENV, "source", "RAW_ORDERS")' in callable_page
    assert "| [`load_config`]" in (ROOT / "docs/api/modules/config.md").read_text(encoding="utf-8")
