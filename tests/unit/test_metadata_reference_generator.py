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


def test_metadata_reference_generation_uses_model_and_is_deterministic(tmp_path, monkeypatch) -> None:
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
    for table_name in CANONICAL_METADATA_TABLES:
        slug = table_name.lower()
        assert first_landing.count(f"## [{table_name}](metadata/{slug}.md)") == 1
        page = first_pages[f"{slug}.md"]
        assert "## Model" in page
        assert "**Grain:**" in page
        assert "**Primary key:**" in page
        assert "**Relationships:**" in page
        assert "## Implemented schema" in page
        assert "| Column | Data type | Managed by | Description |" in page

    generator.generate_metadata_reference_pages()
    assert landing.read_text(encoding="utf-8") == first_landing
    assert {
        path.name: path.read_text(encoding="utf-8")
        for path in sorted(metadata_dir.glob("*.md"))
    } == first_pages
    assert len(first_pages) == len(CANONICAL_METADATA_TABLES)
