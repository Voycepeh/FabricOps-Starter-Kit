"""Regression checks for the generated Function Reference landing page."""

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[2]
REFERENCE_PAGE = ROOT / "docs" / "reference" / "index.md"


def test_function_reference_uses_collapsible_groups() -> None:
    """Keep the generated catalogue grouped and avoid restoring the hierarchy diagram."""
    text = REFERENCE_PAGE.read_text(encoding="utf-8")

    assert "```mermaid" not in text
    assert 'data-callable-group="standard-orchestration"' in text
    assert 'data-callable-group="pipeline-capabilities"' in text
    assert 'data-callable-group="governance-metadata"' in text
    assert 'data-callable-group="access-consumption"' in text
    assert 'data-callable-group="foundational-io"' in text

    standard_open = re.search(
        r'<details class="reference-function-group" '
        r'data-callable-group="standard-orchestration" '
        r'data-default-open="true" open>',
        text,
    )
    assert standard_open is not None

    collapsed_groups = re.findall(
        r'<details class="reference-function-group" '
        r'data-callable-group="(?!standard-orchestration)([^"]+)" '
        r'data-default-open="false">',
        text,
    )
    assert len(collapsed_groups) == 4


def test_every_public_function_is_in_exactly_one_group() -> None:
    """Ensure new public functions cannot silently fall outside the grouped catalogue."""
    text = REFERENCE_PAGE.read_text(encoding="utf-8")

    rows = re.findall(r'data-callable-row="true" data-callable-name="([^"]+)"', text)
    assert rows
    assert len(rows) == len(set(rows))

    group_starts = list(
        re.finditer(r'<details class="reference-function-group"[^>]*>', text)
    )
    assert len(group_starts) == 5

    grouped_rows: list[str] = []
    for index, match in enumerate(group_starts):
        end = group_starts[index + 1].start() if index + 1 < len(group_starts) else len(text)
        body = text[match.end():end]
        grouped_rows.extend(
            re.findall(r'data-callable-row="true" data-callable-name="([^"]+)"', body)
        )

    assert sorted(grouped_rows) == sorted(rows)


def test_function_reference_links_keep_existing_targets() -> None:
    """Keep the stable page URL, individual function links, and call-flow link intact."""
    text = REFERENCE_PAGE.read_text(encoding="utf-8")

    assert "../assets/public-function-call-flows-dashboard.html" in text

    function_links = re.findall(
        r'class="reference-catalogue-item-title" href="../api/reference/([^/]+)/"',
        text,
    )
    assert function_links
    for function_name in function_links:
        assert (ROOT / "docs" / "api" / "reference" / f"{function_name}.md").exists()
