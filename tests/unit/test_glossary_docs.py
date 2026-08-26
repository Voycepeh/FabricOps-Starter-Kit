"""Validate glossary-backed documentation wording."""

from __future__ import annotations

import json
import re
from pathlib import Path

from docs.glossary_tooltips import glossary_tooltip_definitions, resolve_glossary_links
from scripts.generate_glossary_page import DISPLAY_NAMES, build_glossary_page

ROOT = Path(__file__).parents[2]
DOCS_PATH = ROOT / "docs"
GLOSSARY_PATH = DOCS_PATH / "reference" / "_data" / "glossary.json"
GLOSSARY_PAGE_PATH = DOCS_PATH / "glossary.md"
GLOSSARY_REFERENCE_PATTERN = re.compile(r"glossary\.md#(?P<entry_id>[a-z0-9-]+)")
REQUIRED_FIELDS = {
    "id",
    "term",
    "aliases",
    "category",
    "short_definition",
    "long_definition",
    "preferred_usage",
    "avoid_usage",
}
REQUIRED_CATEGORIES = {
    "FabricOps concepts",
    "Microsoft Fabric concepts",
    "Data Governance concepts",
    "Data Engineering concepts",
}
REQUIRED_TERMS = {
    "FabricOps Starter Kit",
    "profile",
    "enrichment",
    "guardrails",
    "enforcement",
    "guardrail result",
    "data steward",
    "data agreement",
    "data contract",
    "metadata",
    "configuration-driven engineering",
    "governance as code",
    "data access",
    "data sensitivity",
    "PII",
    "Microsoft Fabric",
    "workspace",
    "Lakehouse",
    "Warehouse",
    "notebook",
    "pipeline",
    "PySpark",
    "parallel processing",
    "full dataset",
    "incremental watermark",
    "incremental partition",
    "incremental subset",
    "watermark",
    "slowly changing dimensions",
    "data modelling",
    "schema",
    "data quality",
    "partition",
    "physical partitioning",
    "append",
    "overwrite",
    "row-level security",
    "object-level security",
    "access control",
    "configuration",
}


def _glossary() -> list[dict[str, object]]:
    return json.loads(GLOSSARY_PATH.read_text(encoding="utf-8"))


def test_glossary_schema_categories_and_required_terms() -> None:
    """Verify the glossary source has the required schema and coverage."""
    entries = _glossary()
    terms = {str(entry["term"]) for entry in entries}
    categories = {str(entry["category"]) for entry in entries}

    assert categories == REQUIRED_CATEGORIES
    assert REQUIRED_TERMS <= terms
    for entry in entries:
        assert REQUIRED_FIELDS <= set(entry), entry.get("term")
        assert isinstance(entry["aliases"], list), entry["term"]
        assert str(entry["id"]).strip(), entry["term"]
        assert str(entry["short_definition"]).strip(), entry["term"]
        assert str(entry["long_definition"]).strip(), entry["term"]


def test_glossary_ids_are_unique_and_stable_keys() -> None:
    """Keep glossary IDs suitable for deterministic references from other docs."""
    entries = _glossary()
    ids = [str(entry["id"]) for entry in entries]

    assert len(ids) == len(set(ids))
    assert all(identifier == identifier.strip().lower() for identifier in ids)
    assert all(identifier and all(char.isalnum() or char == "-" for char in identifier) for identifier in ids)


def test_generated_glossary_page_is_current() -> None:
    """Keep the committed human-facing glossary synchronized with its source."""
    assert GLOSSARY_PAGE_PATH.read_text(encoding="utf-8") == build_glossary_page()


def test_glossary_tooltips_use_canonical_short_definitions() -> None:
    """Derive tooltip text from glossary data rather than hard-coded documentation prose."""
    definitions = glossary_tooltip_definitions()
    for entry in _glossary():
        entry_id = str(entry["id"])
        display_name = DISPLAY_NAMES.get(entry_id, str(entry["term"]))
        assert definitions[display_name] == str(entry["short_definition"])


def test_all_documented_glossary_ids_resolve() -> None:
    """Keep glossary references structural: every referenced ID must exist canonically."""
    valid_ids = {str(entry["id"]) for entry in _glossary()}
    unknown: list[tuple[str, str]] = []
    for path in DOCS_PATH.rglob("*.md"):
        for entry_id in GLOSSARY_REFERENCE_PATTERN.findall(path.read_text(encoding="utf-8")):
            if entry_id not in valid_ids:
                unknown.append((str(path.relative_to(ROOT)), entry_id))

    assert unknown == []


def test_glossary_reference_rendering_removes_duplicate_definition_and_link() -> None:
    """Render an ID-backed key-concept reference as a tooltip term, not another glossary link."""
    markdown = (
        "    [**Data Steward**](../glossary.md#data-steward) — locally copied definition.  \n"
        "A [Data Contract](glossary.md#data-contract) controls this table."
    )

    rendered = resolve_glossary_links(markdown)

    assert "glossary.md#" not in rendered
    assert "locally copied definition" not in rendered
    assert "**Data Steward**" in rendered
    assert "Data Contract controls this table" in rendered


def test_data_quality_is_a_data_governance_concept() -> None:
    """Keep Data Quality grouped with established Data Governance terminology."""
    data_quality = next(entry for entry in _glossary() if entry["term"] == "data quality")

    assert data_quality["category"] == "Data Governance concepts"


def test_glossary_has_no_duplicate_singular_plural_guardrail_entries() -> None:
    """Verify singular/plural variants are aliases, not duplicate canonical entries."""
    terms = {str(entry["term"]).lower() for entry in _glossary()}
    guardrails = next(entry for entry in _glossary() if entry["term"] == "guardrails")

    assert "guardrail" not in terms
    assert "guardrail" in guardrails["aliases"]


def test_policy_as_code_is_not_a_glossary_term_or_alias() -> None:
    """Keep Policy as Code out of the FabricOps glossary vocabulary."""
    entries = _glossary()
    terms = {str(entry["term"]).lower() for entry in entries}
    aliases = {str(alias).lower() for entry in entries for alias in entry["aliases"]}

    assert "policy as code" not in terms
    assert "policy as code" not in aliases
