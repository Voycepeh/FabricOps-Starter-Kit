"""Normalize guided-demo links after generated documentation is refreshed."""

from __future__ import annotations

from pathlib import Path


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


def normalize_links() -> list[Path]:
    """Replace stale guided-demo targets in Markdown documentation."""
    changed: list[Path] = []
    for path in DOCS_DIR.rglob("*.md"):
        original = path.read_text(encoding="utf-8")
        updated = original
        for stale, current in LINK_REPLACEMENTS.items():
            updated = updated.replace(stale, current)
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            changed.append(path.relative_to(ROOT))
    return changed


if __name__ == "__main__":
    for changed_path in normalize_links():
        print(f"Updated {changed_path}")
