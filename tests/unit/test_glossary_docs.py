"""Validate glossary-backed documentation wording."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).parents[2]
GLOSSARY_PATH = ROOT / "docs" / "reference" / "_data" / "glossary.json"
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
    "Microsoft Fabric basics",
    "Data engineering basics",
    "Security and access basics",
    "File and configuration basics",
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
    "incremental load",
    "slowly changing dimensions",
    "data modelling",
    "schema",
    "data quality",
    "partitioning",
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

    assert REQUIRED_CATEGORIES <= categories
    assert REQUIRED_TERMS <= terms
    for entry in entries:
        assert REQUIRED_FIELDS <= set(entry), entry.get("term")
        assert isinstance(entry["aliases"], list), entry["term"]
        assert str(entry["short_definition"]).strip(), entry["term"]
        assert str(entry["long_definition"]).strip(), entry["term"]


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
