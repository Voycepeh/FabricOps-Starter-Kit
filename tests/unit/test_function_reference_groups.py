"""Regression checks for the generated Function Reference catalogue."""

from pathlib import Path
import re

from fabricops_kit.public_api import PREVIEW_PUBLIC_API, RELEASE_PUBLIC_API, SUPPORTED_PUBLIC_API

ROOT = Path(__file__).resolve().parents[2]
REFERENCE_PAGE = ROOT / "docs" / "reference" / "index.md"
EXPECTED_GROUPS = [
    ("engineering", "Engineering Functions", [
        "setup_notebook", "setup_pipeline", "orchestrate_read", "profile_table",
        "orchestrate_write", "finalize_pipeline",
    ]),
    ("governance", "Governance Functions", [
        "setup_metadata_tables", "widget_data_steward", "widget_data_agreement",
        "widget_data_contract", "widget_activate_data_contract", "widget_activate_pipeline",
    ]),
    ("foundational-io", "Foundational I/O", [
        "read_lakehouse_csv", "read_lakehouse_excel", "read_lakehouse_json",
        "read_lakehouse_parquet", "read_lakehouse_table", "read_lakehouse_query", "read_warehouse_query",
        "read_warehouse_table", "write_lakehouse_file", "write_lakehouse_table", "write_warehouse_table",
    ]),
    ("demo", "Demo Only", ["orchestrate_demo_reset"]),
    ("preview", "Preview / In Development", [
        "scan_effective_access", "scan_workspace_access", "scan_sql_access",
        "scan_onelake_access", "create_data_agent",
    ]),
]


def test_function_reference_uses_ordered_collapsible_groups() -> None:
    """Keep exact catalogue order, counts and only Engineering expanded."""
    text = REFERENCE_PAGE.read_text(encoding="utf-8")
    assert "```mermaid" not in text
    groups = re.findall(
        r'<details class="reference-function-group" data-callable-group="([^"]+)" '
        r'data-default-open="([^"]+)"( open)?>(.*?)</details>', text, re.S,
    )
    assert [group[0] for group in groups] == [group[0] for group in EXPECTED_GROUPS]
    for (key, default_open, open_attribute, body), (expected_key, title, functions) in zip(groups, EXPECTED_GROUPS):
        assert key == expected_key
        assert default_open == ("true" if key == "engineering" else "false")
        assert bool(open_attribute) == (key == "engineering")
        assert f'class="reference-function-group-title">{title}</span>' in body
        count = len(functions)
        assert f'{count} {"function" if count == 1 else "functions"} ·' in body
        assert re.findall(r'data-callable-name="([^"]+)"', body) == functions
    assert "Optional standalone profiling" in groups[0][3]


def test_every_public_function_is_in_exactly_one_group() -> None:
    """Cover the actual public registry once and link to existing generated pages."""
    text = REFERENCE_PAGE.read_text(encoding="utf-8")
    rows = re.findall(r'data-callable-row="true" data-callable-name="([^"]+)"', text)
    expected = {qn.rsplit(".", 1)[-1] for qn in RELEASE_PUBLIC_API}
    assert len(rows) == len(set(rows)) == len(expected)
    assert set(rows) == expected
    function_links = re.findall(
        r'class="reference-catalogue-item-title" href="../api/reference/([^/]+)/"', text,
    )
    assert set(function_links) == expected
    for function_name in function_links:
        assert (ROOT / "docs" / "api" / "reference" / f"{function_name}.md").exists()


def test_grouping_preserves_individual_lifecycle_badges() -> None:
    """Governance and Demo groups must retain Preview functions as Preview."""
    text = REFERENCE_PAGE.read_text(encoding="utf-8")
    live_names = {qn.rsplit(".", 1)[-1] for qn in SUPPORTED_PUBLIC_API}
    preview_names = {qn.rsplit(".", 1)[-1] for qn in PREVIEW_PUBLIC_API}
    articles = re.findall(r'<article [^>]*data-callable-name="([^"]+)"[^>]*>(.*?)</article>', text, re.S)
    for name, body in articles:
        status = "live" if name in live_names else "preview"
        assert name in live_names | preview_names
        assert f'reference-lifecycle-{status}' in body
        assert f'reference-lifecycle-{"preview" if status == "live" else "live"}' not in body
