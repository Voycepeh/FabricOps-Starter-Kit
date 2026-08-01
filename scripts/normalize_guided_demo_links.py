"""Normalize stale guided-demo Markdown link targets after docs generation."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
DOCS_DIR = ROOT / "docs"

LINK_REPLACEMENTS = {
    "guided-demo/99-explore-via-notebooks.md": "guided-demo/99-explore-via-notebook.md",
    "../../guided-demo/run-pipeline.md": "../../guided-demo/02-run-pipeline.md",
    "../../guided-demo/review-guardrails.md": "../../guided-demo/03-enrich-guardrails.md",
    "run-environment-setup.md": "00B-run-environment-setup.md",
    "run-pipeline-with-guardrails.md": "04-run-pipeline-with-guardrails.md",
    "run-pipeline.md": "02-run-pipeline.md",
    "review-guardrails.md": "03-enrich-guardrails.md",
    "create-data-contract.md": "05-create-data-contract.md",
    "promote-to-production.md": "06-promote-to-production.md",
    "explore-metadata-outputs.md": "99-explore-via-notebook.md",
}

# Match only complete Markdown destinations. This prevents a valid target such as
# ``02-run-pipeline.md`` from being rewritten to ``02-02-run-pipeline.md``.
MARKDOWN_LINK_PATTERN = re.compile(r"(?P<prefix>\]\()(?P<target>[^)]+)(?P<suffix>\))")


def _replace_target(match: re.Match[str]) -> str:
    """Return a Markdown link with an exact stale destination normalized."""
    target = match.group("target")
    replacement = LINK_REPLACEMENTS.get(target, target)
    return f'{match.group("prefix")}{replacement}{match.group("suffix")}'


def normalize_links() -> list[Path]:
    """Replace exact stale guided-demo targets in Markdown documentation."""
    changed: list[Path] = []
    for path in DOCS_DIR.rglob("*.md"):
        original = path.read_text(encoding="utf-8")
        updated = MARKDOWN_LINK_PATTERN.sub(_replace_target, original)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(path.relative_to(ROOT))
    return changed


if __name__ == "__main__":
    for changed_path in normalize_links():
        print(f"Updated {changed_path}")
