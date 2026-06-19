"""Regression checks for generated documentation links."""

from __future__ import annotations

import ast
import os
import re
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).parents[2]
DOCS = ROOT / "docs"


def _exported_symbols() -> list[str]:
    """Return exported public symbol names from the package root."""
    tree = ast.parse((ROOT / "src" / "fabricops_kit" / "__init__.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets):
            return [elt.value for elt in node.value.elts if isinstance(elt, ast.Constant) and isinstance(elt.value, str)]
    raise AssertionError("Could not parse __all__")


def _local_link_target_exists(markdown_path: Path, href: str) -> bool:
    """Return whether a local generated docs link resolves to an existing page."""
    parsed = urlparse(href)
    if parsed.scheme or parsed.netloc or href.startswith(("mailto:", "#")):
        return True
    if "github.com/Voycepeh/FabricOps-Starter-Kit/blob/" in href:
        return True
    raw_path = unquote(parsed.path)
    if not raw_path:
        return True
    if markdown_path.parent == DOCS / "api" / "reference" and raw_path.startswith("../"):
        sibling_slug = raw_path.removeprefix("../").strip("/")
        sibling_page = markdown_path.parent / f"{sibling_slug}.md"
        if sibling_page.exists():
            return True
    candidate = (markdown_path.parent / raw_path).resolve()
    docs_root = DOCS.resolve()
    try:
        candidate.relative_to(docs_root)
    except ValueError:
        return True
    candidates = [candidate]
    if candidate.suffix == "":
        candidates.extend([candidate.with_suffix(".md"), candidate / "index.md"])
    elif candidate.suffix == ".html":
        candidates.append(candidate.with_suffix(".md"))
    return any(path.exists() for path in candidates)


def test_generated_docs_local_links_resolve() -> None:
    """Verify generated Markdown and inline HTML links resolve locally."""
    link_pattern = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|href=[\"']([^\"']+)[\"']")
    broken: list[str] = []
    for markdown_path in sorted(DOCS.rglob("*.md")):
        text = markdown_path.read_text(encoding="utf-8")
        for match in link_pattern.finditer(text):
            href = match.group(1) or match.group(2) or ""
            if not _local_link_target_exists(markdown_path, href):
                broken.append(f"{markdown_path.relative_to(ROOT)} -> {href}")
    assert broken == []


def test_generated_github_links_use_main_not_local_sha() -> None:
    """Verify generated GitHub links do not point at local commit SHAs."""
    stale_sha_pattern = re.compile(
        r"https://github\.com/Voycepeh/FabricOps-Starter-Kit/blob/[0-9a-f]{40}/"
    )
    offenders = [
        str(path.relative_to(ROOT))
        for path in sorted(DOCS.rglob("*.md"))
        if stale_sha_pattern.search(path.read_text(encoding="utf-8"))
    ]

    assert offenders == []


def test_generated_reference_includes_every_exported_public_callable_page() -> None:
    """Verify PR 555-style template filtering does not remove public pages."""
    env = {**os.environ, "PYTHONPATH": "src"}
    subprocess.run(["python", "scripts/generate_function_reference.py"], cwd=ROOT, env=env, check=True)

    missing = [name for name in _exported_symbols() if not (DOCS / "api" / "reference" / f"{name}.md").exists()]
    assert missing == []

    reference_index = (DOCS / "reference" / "index.md").read_text(encoding="utf-8")
    assert 'data-callable-name="display_guardrail_results"' in reference_index
    assert 'data-function-type-filter="composable" checked' in reference_index
    assert (DOCS / "api" / "reference" / "display_guardrail_results.md").exists()


def test_generated_relationship_links_respect_public_and_internal_routes() -> None:
    """Verify public callables link to public pages and private helpers stay chips."""
    pipeline_page = (DOCS / "api" / "modules" / "pipeline.md").read_text(encoding="utf-8")

    assert 'href="../reference/display_guardrail_results/"' in pipeline_page
    assert 'href="../reference/_rows_for_display/"' not in pipeline_page
    assert '<span class="reference-chip"><code>_rows_for_display</code></span>' in pipeline_page
    assert 'href="../reference/build_guardrail_summary_rows/"' not in pipeline_page
    assert 'href="../reference/build_guardrail_detail_rows/"' not in pipeline_page
