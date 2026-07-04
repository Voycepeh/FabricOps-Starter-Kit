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
    import fabricops_kit

    return list(fabricops_kit.__all__)


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
    if any(path.exists() for path in candidates):
        return True
    generated_pages = {
        DOCS / "release-info.md",
    }
    return any(path in generated_pages for path in candidates)


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


def test_stale_pipeline_guardrail_links_do_not_return() -> None:
    """Verify removed pipeline guardrail pages are not linked by source or generated docs."""
    stale_patterns = [
        "how-fabricops-works/guardrails/pipeline-guardrails.md",
        "guardrails/pipeline-guardrails.md",
        "pipeline-guardrails.md",
    ]
    checked_roots = [DOCS, ROOT / "scripts"]
    offenders: list[str] = []

    for checked_root in checked_roots:
        for path in sorted(checked_root.rglob("*")):
            if path.is_dir() or path.suffix not in {".md", ".json", ".py", ".txt", ".yml", ".yaml"}:
                continue
            text = path.read_text(encoding="utf-8")
            for pattern in stale_patterns:
                if pattern in text:
                    offenders.append(f"{path.relative_to(ROOT)} -> {pattern}")

    assert offenders == []


def test_generated_github_links_use_main_not_local_sha() -> None:
    """Verify generated GitHub links do not point at local commit SHAs."""
    stale_sha_pattern = re.compile(r"https://github\.com/Voycepeh/FabricOps-Starter-Kit/blob/[0-9a-f]{40}/")
    offenders = [
        str(path.relative_to(ROOT))
        for path in sorted(DOCS.rglob("*.md"))
        if stale_sha_pattern.search(path.read_text(encoding="utf-8"))
    ]

    assert offenders == []


def test_generated_reference_includes_every_exported_public_callable_page() -> None:
    """Verify PR 555-style template filtering does not remove public pages."""
    env = {**os.environ, "PYTHONPATH": "src"}
    subprocess.run(["python", "scripts/generate_individual_function_reference_pages.py"], cwd=ROOT, env=env, check=True)

    import json

    inventory = json.loads((DOCS / "reference" / "_data" / "public-function-call-flows.json").read_text(encoding="utf-8"))
    public_functions = [str(row["function_name"]) for row in inventory["public_functions"]]
    missing = [name for name in public_functions if not (DOCS / "api" / "reference" / f"{name}.md").exists()]
    assert missing == []

    reference_index = (DOCS / "reference" / "index.md").read_text(encoding="utf-8")
    assert 'data-callable-name="display_guardrail_results"' in reference_index
    assert 'data-function-type="public-starter-kit"' in reference_index
    assert (DOCS / "api" / "reference" / "display_guardrail_results.md").exists()


def test_generated_relationship_links_respect_function_first_routes() -> None:
    """Verify generated docs no longer depend on public module pages."""
    reference_index = (DOCS / "reference" / "index.md").read_text(encoding="utf-8")

    assert (DOCS / "api" / "reference" / "display_guardrail_results.md").exists()
    assert not (DOCS / "api" / "modules" / "pipeline.md").exists()
    assert "api/modules" not in reference_index
