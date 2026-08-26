"""Validate glossary-backed documentation wording."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.generate_glossary_page import build_glossary_page

ROOT = Path(__file__).parents[2]
GLOSSARY_PATH = ROOT / "docs" / "reference" / "_data" / "glossary.json"
GLOSSARY_PAGE_PATH = ROOT / "docs" / "glossary.md"
REQUIRED_FIELDS = {
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
    "Governance concepts",
    "Engineering concepts",
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
EXPECTED_CATEGORY_BY_TERM = {
    "FabricOps Starter Kit": "FabricOps concepts",
    "metadata": "FabricOps concepts",
    "governance as code": "FabricOps concepts",
    "configuration-driven engineering": "FabricOps concepts",
    "data steward": "Governance concepts",
    "data agreement": "Governance concepts",
    "enrichment": "Governance concepts",
    "data sensitivity": "Governance concepts",
    "PII": "Governance concepts",
    "data access": "Governance concepts",
    "data quality": "Governance concepts",
    "guardrails": "Governance concepts",
    "enforcement": "Governance concepts",
    "guardrail result": "Governance concepts",
    "data contract": "Governance concepts",
    "access control": "Governance concepts",
    "row-level security": "Governance concepts",
    "object-level security": "Governance concepts",
    "Microsoft Fabric": "Engineering concepts",
    "workspace": "Engineering concepts",
    "Lakehouse": "Engineering concepts",
    "Warehouse": "Engineering concepts",
    "notebook": "Engineering concepts",
    "configuration": "Engineering concepts",
    "pipeline": "Engineering concepts",
    "PySpark": "Engineering concepts",
    "profile": "Engineering concepts",
    "schema": "Engineering concepts",
    "full dataset": "Engineering concepts",
    "incremental watermark": "Engineering concepts",
    "incremental partition": "Engineering concepts",
    "incremental subset": "Engineering concepts",
    "watermark": "Engineering concepts",
    "parallel processing": "Engineering concepts",
    "data modelling": "Engineering concepts",
    "partition": "Engineering concepts",
    "physical partitioning": "Engineering concepts",
    "append": "Engineering concepts",
    "overwrite": "Engineering concepts",
    "slowly changing dimensions": "Engineering concepts",
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
        assert str(entry["short_definition"]).strip(), entry["term"]
        assert str(entry["long_definition"]).strip(), entry["term"]


def test_glossary_terms_follow_workflow_categories() -> None:
    """Keep the public glossary aligned to FabricOps, Governance, and Engineering."""
    actual = {str(entry["term"]): str(entry["category"]) for entry in _glossary()}

    assert actual == EXPECTED_CATEGORY_BY_TERM


def test_generated_glossary_page_is_current() -> None:
    """Keep the committed human-facing glossary synchronized with its source."""
    assert GLOSSARY_PAGE_PATH.read_text(encoding="utf-8") == build_glossary_page()


def test_data_quality_is_a_governance_concept() -> None:
    """Keep Data Quality grouped with the governed expectations FabricOps applies."""
    data_quality = next(entry for entry in _glossary() if entry["term"] == "data quality")

    assert data_quality["category"] == "Governance concepts"


def test_glossary_has_no_duplicate_singular_plural_guardrail_entries() -> None:
    """Verify singular/plural variants are aliases, not duplicate canonical entries."""
    terms = {str(entry["term"]).lower() for entry in _glossary()}
    guardrails = next(entry for entry in _glossary() if entry["term"] == "guardrails")

    assert "guardrail" not in terms
    assert "guardrail" in guardrails["aliases"]


def test_policy_as_code_is_alias_of_governance_as_code() -> None:
    """Keep one canonical FabricOps concept for governance and policy as code."""
    entries = _glossary()
    terms = {str(entry["term"]) for entry in entries}
    governance_as_code = next(entry for entry in entries if entry["term"] == "governance as code")

    assert "policy as code" not in terms
    assert "policy as code" in governance_as_code["aliases"]
