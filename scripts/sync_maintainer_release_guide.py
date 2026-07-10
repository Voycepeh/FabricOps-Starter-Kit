"""Synchronize the human maintainer release guide from the release skill."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = ROOT / ".agents" / "skills" / "fabricops-release" / "SKILL.md"
DOC_PATH = ROOT / "docs" / "maintainer" / "index.md"
START = "<!-- FABRICOPS-RELEASE-SKILL-CONTENT:START -->"
END = "<!-- FABRICOPS-RELEASE-SKILL-CONTENT:END -->"
INTRO = """# FabricOps Maintainer Release Guide

This page publishes the same operational workflow used by the `FabricOps Release Maintainer` AI skill. The canonical workflow source is [`.agents/skills/fabricops-release/SKILL.md`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/.agents/skills/fabricops-release/SKILL.md); run [`scripts/sync_maintainer_release_guide.py`](https://github.com/Voycepeh/FabricOps-Starter-Kit/blob/main/scripts/sync_maintainer_release_guide.py) after editing the skill.

"""


def skill_body() -> str:
    """Return the canonical skill workflow body without YAML front matter."""
    text = SKILL_PATH.read_text(encoding="utf-8")
    if text.startswith("---\n"):
        _, _, remainder = text.partition("\n---\n")
        text = remainder.lstrip()
    # Drop the first H1 because the docs page provides the page title.
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        if lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines).strip() + "\n"


def rendered_doc() -> str:
    """Render the synchronized docs page content."""
    return f"{INTRO}{START}\n\n{skill_body()}\n{END}\n"


def main() -> int:
    """Write the synchronized maintainer release guide."""
    DOC_PATH.write_text(rendered_doc(), encoding="utf-8")
    print(f"Synchronized {DOC_PATH.relative_to(ROOT)} from {SKILL_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
