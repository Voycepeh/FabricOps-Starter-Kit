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
    "Data governance concepts",
    "Microsoft Fabric concepts",
    "Data engineering concepts",
    "File and configuration concepts",
    "Metadata table names",
}
REQUIRED_TERMS = {
    "FabricOps Starter Kit", "profile", "source data", "pipeline output", "target DataFrame", "target table",
    "enrichment", "guardrails", "enforcement", "can_continue", "metadata lakehouse", "metadata tables",
    "notebook registry", "notebook template", "agreement selection", "guardrail target selection", "profile mode", "static_data",
    "changing_data", "skip", "active pending governance review", "self-approved", "governance-approved",
    "superseded", "activation_state", "review_state", "run summary", "guardrail result", "lineage relationship",
    "data contract", "data agreement", "data steward", "ownership", "business meaning",
    "usage context", "sensitivity", "classification", "governance review", "approval", "rejection", "replacement",
    "deactivation", "lifecycle", "audit", "metadata", "evidence", "review history", "support readiness",
    "Microsoft Fabric", "workspace", "Governance workspace", "Engineering Dev workspace", "Engineering Prod workspace",
    "Lakehouse", "Warehouse", "source_lakehouse", "unified_lakehouse", "product_warehouse", "Fabric item target",
    "Fabric environment", "wheel", "notebook session", "Fabric notebook", "Spark session", "Delta table",
    "Lakehouse schema", "Files path", "table path", "pipeline", "runtime", "source", "target", "DataFrame",
    "schema", "freshness", "watermark", "DQ", "data quality rule", "lineage", "transformation",
    "deterministic logic", "row count", "null", "distinct value", "distribution", "partitioning", "repartitioning",
    "append", "overwrite", "CSV", "Excel", "Parquet", "JSON", "YAML", "configuration", "parameter", "flag",
    "dashboard", "METADATA_DATA_CATALOGUE", "METADATA_GUARDRAIL_RESULTS",
    "METADATA_DATA_ACCESS", "METADATA_DATA_AGREEMENTS",
    "METADATA_DATA_STEWARDS", "METADATA_AGREEMENT_EVIDENCE",
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


def test_notebook_template_is_not_alias_for_notebook_registry() -> None:
    """Verify notebook templates and the notebook registry are separate concepts."""
    entries = _glossary()
    terms = {str(entry["term"]) for entry in entries}
    registry = next(entry for entry in entries if entry["term"] == "notebook registry")

    assert "notebook template" in terms
    assert "notebook template" not in registry["aliases"]


