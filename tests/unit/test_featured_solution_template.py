from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

FEATURED_SOLUTION_PAGES = (
    ROOT / "docs/solutions/plug-and-play-data-pipelines.md",
    ROOT / "docs/solutions/production-table-to-data-agent.md",
    ROOT / "docs/solutions/ai-assisted-data-contract-authoring.md",
    ROOT / "docs/solutions/business-rules-to-data-quality.md",
    ROOT / "docs/solutions/effective-data-access.md",
)

REQUIRED_HEADINGS = (
    "## The problem",
    "## The solution",
    "## How it works",
    "## Under the hood",
    "## Example",
    "## Go deeper",
)


def test_featured_solution_pages_follow_shared_presentation_contract():
    for page in FEATURED_SOLUTION_PAGES:
        text = page.read_text(encoding="utf-8")

        heading_positions = [text.index(heading) for heading in REQUIRED_HEADINGS]
        assert heading_positions == sorted(heading_positions), page

        assert "fabricops-release-status--preview" in text, page
        assert "{ .fabricops-solution-hero }" in text, page
        assert "??? example" not in text, page
        assert "```mermaid" not in text, page

        under_hood = text[text.index("## Under the hood") : text.index("## Example")]
        example = text[text.index("## Example") : text.index("## Go deeper")]

        assert '<details class="fabricops-solution-details" markdown="1">' in under_hood, page
        assert '<details class="fabricops-solution-details" markdown="1">' in example, page
        assert ".svg){ .fabricops-solution-diagram }" in under_hood, page
