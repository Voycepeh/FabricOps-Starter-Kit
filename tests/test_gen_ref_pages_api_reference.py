from __future__ import annotations

import io
import runpy
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "docs" / "gen_ref_pages.py"


class _Recorder:
    def __init__(self) -> None:
        self.files: dict[str, io.StringIO] = {}

    def open(self, path: str, mode: str = "w"):
        buf = io.StringIO()
        self.files[path] = buf

        class _Ctx:
            def __enter__(self_nonlocal):
                return buf

            def __exit__(self_nonlocal, exc_type, exc, tb):
                return False

        return _Ctx()


def _run_gen_ref_pages() -> dict[str, str]:
    recorder = _Recorder()
    fake_module = types.SimpleNamespace(open=recorder.open)
    original = sys.modules.get("mkdocs_gen_files")
    sys.modules["mkdocs_gen_files"] = fake_module
    try:
        runpy.run_path(str(SCRIPT), run_name="__main__")
    finally:
        if original is not None:
            sys.modules["mkdocs_gen_files"] = original
        else:
            del sys.modules["mkdocs_gen_files"]
    return {path: buf.getvalue() for path, buf in recorder.files.items()}


def test_gen_ref_pages_generates_public_callable_pages_under_api_reference() -> None:
    outputs = _run_gen_ref_pages()
    assert "api/reference/load_config.md" in outputs
    assert "reference/load_config.md" not in outputs


def test_generated_primary_reference_links_use_api_reference_prefix() -> None:
    content = (ROOT / "docs" / "reference" / "index.md").read_text(encoding="utf-8")
    assert "../api/reference/" in content
    assert "./build_governance_classification_records/" not in content


def test_generated_module_pages_use_api_reference_prefix() -> None:
    import json
    manifest = json.loads((ROOT / "docs" / "reference" / "manifest.json").read_text(encoding="utf-8"))
    module_pages = [ROOT / "docs" / "api" / "modules" / f"{row['module_name']}.md" for row in manifest["modules"]]
    for path in module_pages:
        text = path.read_text(encoding="utf-8")
        assert "../../api/reference/" not in text


def test_generated_notebook_structure_pages_use_api_reference_prefix() -> None:
    notebook_pages = sorted((ROOT / "docs" / "notebook-structure").glob("*.md"))
    assert notebook_pages
    pages_with_callable_links = 0
    for path in notebook_pages:
        text = path.read_text(encoding="utf-8")
        if "../../api/reference/" in text:
            pages_with_callable_links += 1
        assert "../../reference/internal/" in text or "../../reference/" not in text
    assert pages_with_callable_links >= 1


def test_no_legacy_top_level_reference_callable_page_exists() -> None:
    outputs = _run_gen_ref_pages()
    assert "api/reference/load_config.md" in outputs
    assert "reference/load_config.md" not in outputs


def test_public_callable_page_enables_show_source_option() -> None:
    outputs = _run_gen_ref_pages()
    page = outputs["api/reference/read_lakehouse_table.md"]
    assert "::: fabricops_kit.fabric_input_output.read_lakehouse_table" in page
    assert "show_source: true" in page


def test_internal_helper_pages_are_generated_with_show_source_and_expected_paths() -> None:
    outputs = _run_gen_ref_pages()
    helper_page = outputs["api/reference/internal/fabric_input_output/_get_spark.md"]
    assert "# `_get_spark`" in helper_page
    assert "Internal helper notice" in helper_page
    assert "::: fabricops_kit.fabric_input_output._get_spark" in helper_page
    assert "show_source: true" in helper_page


def test_read_lakehouse_table_links_to_internal_helpers() -> None:
    outputs = _run_gen_ref_pages()
    page = outputs["api/reference/read_lakehouse_table.md"]
    assert "../internal/fabric_input_output/_get_spark/" in page
    assert "../internal/config/_get_store/" in page


def test_internal_helper_links_have_non_404_path_shape() -> None:
    outputs = _run_gen_ref_pages()
    page = outputs["api/reference/read_lakehouse_table.md"]
    assert "../internal/fabric_input_output/_get_spark/" in page
    assert "../internal/config/_get_store/" in page
    assert "../internal/_get_spark/" not in page
    assert "../internal/_get_store/" not in page


def test_internal_helper_links_point_to_existing_generated_pages() -> None:
    outputs = _run_gen_ref_pages()
    assert "api/reference/internal/fabric_input_output/_get_spark.md" in outputs
    assert "api/reference/internal/config/_get_store.md" in outputs


def test_gen_ref_pages_contains_no_iframe_or_callable_map_html() -> None:
    source = (ROOT / "docs" / "gen_ref_pages.py").read_text(encoding="utf-8")
    assert "<iframe" not in source
    assert "callable-map.html" not in source


def test_referenced_by_links_public_callables_when_possible() -> None:
    outputs = _run_gen_ref_pages()
    page = outputs["api/reference/load_config.md"]
    assert "| Referenced by |" in page
    assert "../" in page
