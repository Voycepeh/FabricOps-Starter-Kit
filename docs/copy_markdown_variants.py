"""Publish raw Markdown variants alongside MkDocs HTML pages."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any


EXCLUDED_DIRS = {"assets", "javascripts", "stylesheets"}
ROOT_TEXT_FILES = {"llms.txt"}


def _is_public_markdown(path: Path, docs_dir: Path) -> bool:
    """Return whether ``path`` should be copied as a public Markdown variant."""

    if path.suffix != ".md" or not path.is_file():
        return False
    relative = path.relative_to(docs_dir)
    return not any(part in EXCLUDED_DIRS for part in relative.parts)


def on_post_build(config: Any) -> None:
    """Copy source Markdown files to the built site using their docs-relative paths.

    MkDocs renders ``docs/example.md`` as ``site/example/index.html``. Copying the
    original Markdown to ``site/example.md`` gives agents a clean text variant at
    the predictable sibling URL ``/example.md`` while preserving the normal HTML
    documentation site for people. Section index pages are also copied to a
    sibling path such as ``site/guide.md`` for the HTML URL ``/guide/``.
    """

    docs_dir = Path(config["docs_dir"]).resolve()
    site_dir = Path(config["site_dir"]).resolve()
    site_dir.mkdir(parents=True, exist_ok=True)

    for file_name in ROOT_TEXT_FILES:
        source_path = docs_dir / file_name
        if source_path.is_file():
            shutil.copy2(source_path, site_dir / file_name)

    for source_path in docs_dir.rglob("*.md"):
        if not _is_public_markdown(source_path, docs_dir):
            continue
        relative_path = source_path.relative_to(docs_dir)
        target_path = site_dir / relative_path
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)

        if relative_path.name == "index.md" and relative_path.parent != Path("."):
            sibling_target = site_dir / relative_path.parent.with_suffix(".md")
            shutil.copy2(source_path, sibling_target)
