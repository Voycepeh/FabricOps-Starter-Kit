"""Validate glossary-backed documentation wording and chips."""

from __future__ import annotations

import json
import re
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
    "notebook registry", "agreement selection", "guardrail target selection", "profile mode", "static_data",
    "changing_data", "skip", "active pending governance review", "self-approved", "governance-approved",
    "superseded", "activation_state", "review_state", "run summary", "guardrail result", "lineage relationship",
    "data contract", "data agreement", "data steward", "agreement evidence", "ownership", "business meaning",
    "usage context", "sensitivity", "classification", "governance review", "approval", "rejection", "replacement",
    "deactivation", "lifecycle", "audit", "metadata", "evidence", "review history", "support readiness",
    "Microsoft Fabric", "workspace", "Governance workspace", "Engineering Dev workspace", "Engineering Prod workspace",
    "Lakehouse", "Warehouse", "source_lakehouse", "unified_lakehouse", "product_warehouse", "Fabric item target",
    "Fabric environment", "wheel", "notebook session", "Fabric notebook", "Spark session", "Delta table",
    "Lakehouse schema", "Files path", "table path", "pipeline", "runtime", "source", "target", "DataFrame",
    "schema", "freshness", "watermark", "DQ", "data quality rule", "lineage", "transformation",
    "deterministic logic", "row count", "null", "distinct value", "distribution", "partitioning", "repartitioning",
    "append", "overwrite", "CSV", "Excel", "Parquet", "JSON", "YAML", "configuration", "parameter", "flag",
    "dashboard", "METADATA_DATA_CATALOGUE", "METADATA_ENRICHMENT_RULES", "METADATA_GUARDRAIL_RULES",
    "METADATA_GUARDRAIL_RESULTS", "METADATA_PIPELINE_RUNS", "METADATA_DATA_LINEAGE_TABLE",
    "METADATA_NOTEBOOK_REGISTRY", "METADATA_DATA_ACCESS", "METADATA_DATA_AGREEMENTS",
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


def test_reference_usage_guidance_is_plain_readable_text() -> None:
    """Verify generated usage guidance does not leak bold markdown labels in details boxes."""
    pages = sorted((ROOT / "docs" / "api" / "reference").glob("*.md"))
    assert pages
    for page in pages:
        text = page.read_text(encoding="utf-8")
        if "## Usage guidance" in text:
            section = text.split("## Usage guidance", 1)[1].split("\n## ", 1)[0]
            assert "**Use when:**" not in section, page
            assert "**Do not use when:**" not in section, page
            assert "<summary>Usage guidance</summary>" not in section, page


def test_glossary_chips_render_outside_code_fences() -> None:
    """Verify glossary chips are rendered and not inserted inside fenced code."""
    pages = sorted((ROOT / "docs" / "api" / "reference").glob("*.md"))
    chip_pages = [page for page in pages if 'class="glossary-chip"' in page.read_text(encoding="utf-8")]
    assert chip_pages
    for page in chip_pages:
        text = page.read_text(encoding="utf-8")
        code_fences = re.findall(r"```.*?```", text, flags=re.DOTALL)
        assert all('class="glossary-chip"' not in fence for fence in code_fences), page
