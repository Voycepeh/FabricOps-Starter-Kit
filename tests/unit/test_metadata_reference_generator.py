"""Tests for the generated metadata reference model."""

from __future__ import annotations

from fabricops_kit.config.metadata_schemas import CANONICAL_METADATA_TABLES, metadata_table_schema_registry
from scripts import generate_individual_function_reference_pages as generator
from scripts.reference_docs_metadata import METADATA_REFERENCE_ORDER, METADATA_TABLE_MODELS


VALID_CARDINALITIES = {"1:1", "1:N", "N:1"}


def _schema_fields() -> dict[str, set[str]]:
    return {
        table_name: set(schema.fieldNames())
        for table_name, schema in metadata_table_schema_registry().items()
    }


def test_metadata_model_contract_matches_implemented_schema() -> None:
    """Ensure configured model keys and relationships match implemented schemas."""
    canonical = list(CANONICAL_METADATA_TABLES)
    fields = _schema_fields()
    assert set(METADATA_TABLE_MODELS) == set(canonical)
    assert len(METADATA_REFERENCE_ORDER) == len(canonical)
    assert set(METADATA_REFERENCE_ORDER) == set(canonical)

    for table_name in canonical:
        model = METADATA_TABLE_MODELS[table_name]
        assert model["purpose"].strip()
        assert model["grain"].strip()
        for field_name in model["primary_key"]:
            assert field_name in fields[table_name]
        for foreign_key in model["foreign_keys"]:
            assert foreign_key["local_field"] in fields[table_name]
            assert foreign_key["referenced_table"] in fields
            assert foreign_key["referenced_field"] in fields[foreign_key["referenced_table"]]
            assert foreign_key["cardinality"] in VALID_CARDINALITIES
            assert foreign_key["statement"].strip()
        for relationship in model["relationships"]:
            assert relationship["cardinality"] in VALID_CARDINALITIES
            assert relationship["statement"].strip()
            if related_table := relationship.get("related_table"):
                assert related_table in fields
                assert set(relationship.get("fields", [])) <= fields[table_name]


def test_metadata_reference_generation_uses_model_and_is_deterministic(tmp_path, monkeypatch) -> None:
    """Ensure generated metadata docs use the model and remain deterministic."""
    metadata_dir = tmp_path / "metadata"
    landing = tmp_path / "metadata.md"
    monkeypatch.setattr(generator, "METADATA_REFERENCE_DIR", metadata_dir)
    monkeypatch.setattr(generator, "METADATA_REFERENCE_INDEX_PATH", landing)

    generator.generate_metadata_reference_pages()
    first_landing = landing.read_text(encoding="utf-8")
    first_pages = {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(metadata_dir.glob("*.md"))
    }

    assert '<div class="grid cards"' not in first_landing
    assert '<div class="metadata-table-grid">' in first_landing
    assert "grid-template-columns: 1fr;" in first_landing
    assert "repeat(2, minmax(0, 1fr))" not in first_landing
    assert "Relationships" in first_landing
    assert "Used by" not in first_landing
    assert "0 tables" not in first_landing
    assert "No downstream tables." not in first_landing
    assert all(cardinality in first_landing for cardinality in ("1 → N", "1 → 1", "N → 1"))
    assert "View full schema" not in first_landing
    assert "## Data Agreement versus Data Contract" not in first_landing
    assert "METADATA_DATA_CATALOGUE.table_id" not in first_landing
    assert "metadata/metadata_data_profiled_frequency" not in first_landing
    for table_name in CANONICAL_METADATA_TABLES:
        slug = table_name.lower()
        assert first_landing.count(f'href="{slug}/"') == 1
        assert first_landing.count(f'>{table_name}</span>') == 1
        page = first_pages[f"{slug}.md"]
        assert "## Writer functions" in page
        assert page.index("## Writer functions") < page.index("## Model")
        assert "## Related templates / solutions" in page
        assert page.index("## Related templates / solutions") < page.index("## Model")
        assert "## Model" in page
        assert "**Grain:**" in page
        assert "**Primary key:**" in page
        assert "**Relationships:**" in page
        assert "## Column summary" in page
        assert "| Total columns |" in page
        assert "| Business columns |" in page
        assert "| Audit columns |" in page
        assert "## Implemented schema" in page
        assert "| Column | Data type | Managed by | Description |" in page

    catalogue_card = first_landing.split(
        'aria-label="Open METADATA_DATA_CATALOGUE schema">', 1
    )[1].split("</a>", 1)[0]
    assert catalogue_card.count(">METADATA_DATA_PROFILED</code>") == 1
    assert ">METADATA_DATA_CONTRACT</code>" in catalogue_card

    profiled_card = first_landing.split(
        'aria-label="Open METADATA_DATA_PROFILED schema">', 1
    )[1].split("</a>", 1)[0]
    assert ">METADATA_DATA_CATALOGUE</code>" in profiled_card
    assert ">METADATA_DATA_PROFILED_FREQUENCY</code>" in profiled_card
    assert 'href="metadata_data_profiled_frequency/"' in first_landing

    contract_page = first_pages["metadata_data_contract.md"]
    assert "[`widget_register_data_contract`](../../api/reference/widget_register_data_contract.md)" in contract_page
    assert "[`01_governance`](../../notebook-templates.md) — Contract registration" in contract_page
    assert contract_page.count("`METADATA_DATA_AGREEMENT` **(N → 1)**") == 1
    assert "via `agreement_id` + `agreement_version`" in contract_page
    assert "`METADATA_DATA_CATALOGUE` **(N → 1)**" in contract_page
    assert "via `table_id`" in contract_page
    assert "METADATA_DATA_AGREEMENT.agreement_id" not in contract_page
    assert "monotonically increasing" not in contract_page

    generator.generate_metadata_reference_pages()
    assert landing.read_text(encoding="utf-8") == first_landing
    assert {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(metadata_dir.glob("*.md"))
    } == first_pages
    assert len(first_pages) == len(CANONICAL_METADATA_TABLES)
