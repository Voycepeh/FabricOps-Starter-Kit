"""Tests for the generated metadata reference model."""

from __future__ import annotations

from fabricops_kit.config.metadata_schemas import (
    CANONICAL_METADATA_TABLES,
    metadata_table_schema_registry,
)
from scripts import generate_individual_function_reference_pages as generator
from scripts.reference_docs_metadata import METADATA_REFERENCE_ORDER, METADATA_TABLE_MODELS


VALID_CARDINALITIES = {"1:1", "1:N", "N:1", "N:M"}


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
    assert '<div class="metadata-table-grid">' not in first_landing
    assert 'data-metadata-explorer' in first_landing
    assert '<nav class="metadata-explorer-fallback"' in first_landing
    assert "## Metadata relationships" in first_landing
    assert "View full schema" not in first_landing
    assert "## Data Agreement versus Data Contract" not in first_landing
    for table_name in CANONICAL_METADATA_TABLES:
        slug = table_name.lower()
        assert first_landing.count(f'href="{slug}/"') == 1
        assert f">{table_name}</a>" in first_landing
        page = first_pages[f"{slug}.md"]
        assert "## Writer functions" in page
        assert page.index("## Writer functions") < page.index("## Model")
        assert "## Used in Workflow Template" in page
        assert page.index("## Used in Workflow Template") < page.index("## Model")
        assert "## Model" in page
        assert "**Grain:**" in page
        assert "**Primary key:**" in page
        assert "**Relationships:**" in page
        assert "## Column summary" in page
        assert "| Total columns |" in page
        assert "| Business columns |" in page
        assert "| Audit columns |" in page
        assert "## Implemented schema" in page
        assert "| Column | Data type | Description |" in page
        assert "Managed by" not in page
        assert "captured" in page.lower()

    contract_page = first_pages["metadata_data_contract.md"]
    assert "[`widget_data_contract`](../../api/reference/widget_data_contract.md)" in contract_page
    assert "widget_register_data_contract.md" not in contract_page
    assert "[`01_governance`](https://github.com/Voycepeh/FabricOps-Starter-Kit/tree/main/templates/notebooks) — Data Contract authoring" in contract_page
    assert "`METADATA_DATA_AGREEMENT` **(N → 1)**" not in contract_page
    activated_page = first_pages["metadata_activation_state.md"]
    assert "`snapshot_json`" in activated_page and "`authority_id`" in activated_page
    assert "atomic central authority" in activated_page
    assert "via `agreement_id` + `agreement_version`" not in activated_page
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


def test_metadata_explorer_details_never_overlay_table_nodes() -> None:
    """Keep the diagram in its own scrollable region and the details panel below it."""
    from pathlib import Path

    root = Path(__file__).parents[2]
    script = (root / "docs/javascripts/metadata-explorer.js").read_text(encoding="utf-8")
    styles = (root / "docs/stylesheets/metadata-explorer.css").read_text(encoding="utf-8")
    assert 'class="metadata-explorer-viewport"' in script
    assert script.index('class="metadata-explorer-viewport"') < script.index('class="metadata-explorer-details"')
    assert '.metadata-explorer-layout{display:block' in styles
    assert '.metadata-explorer-viewport{max-width:100%;width:100%;overflow-x:auto' in styles
    assert '.metadata-explorer-details{position:static' in styles
    assert 'position:sticky' not in styles

def test_metadata_explorer_keeps_keys_readable_and_loads_canonical_details() -> None:
    """Selected nodes surface real cardinalities and reuse generated schema details."""
    from pathlib import Path

    root = Path(__file__).parents[2]
    js = (root / "docs/javascripts/metadata-explorer.js").read_text(encoding="utf-8")
    css = (root / "docs/stylesheets/metadata-explorer.css").read_text(encoding="utf-8")
    assert "cardinalityFrom" in js
    # The approved SVG replaces the former generated grid and floating labels.
    import xml.etree.ElementTree as ET

    diagram = root / "docs/assets/fabricops-metadata-approved.svg"
    svg_source = diagram.read_text(encoding="utf-8")
    svg = ET.fromstring(svg_source)
    links = svg.findall(".//{http://www.w3.org/2000/svg}a")
    assert len(links) == 13
    assert len({link.get("{http://www.w3.org/1999/xlink}href") for link in links}) == 13
    assert "metadata-explorer-approved-svg" in js
    assert "fabricops-metadata-approved.svg" in js
    assert ".metadata-explorer-approved-svg a.selected > rect" in css
    assert "const layoutOrder" not in js
    assert 'class: "metadata-explorer-cardinality"' not in js
    assert "white-space: normal" in css
    assert "overflow-wrap: anywhere" in css
    assert "DOMParser" in js and "fetch(url)" in js
    assert "sectionDetails(section)" in js
    assert 'document.createElement("details")' in js
    assert "metadata-explorer-viewport" in js
    assert "metadata-explorer-details" in js
    assert "data-reference-content" in js
    assert 'status && title === "ACTIVATED_PIPELINE"' in js
    assert '"metadata_pipeline_registry/"' in js
    assert "Proposed table; not yet implemented" not in js


def test_metadata_explorer_payload_matches_canonical_model(tmp_path, monkeypatch) -> None:
    """The on-page hover/relationship data is generated, never hand-authored."""
    import json
    import re

    landing = tmp_path / "metadata.md"
    monkeypatch.setattr(generator, "METADATA_REFERENCE_DIR", tmp_path / "metadata")
    monkeypatch.setattr(generator, "METADATA_REFERENCE_INDEX_PATH", landing)
    generator.generate_metadata_reference_pages()
    text = landing.read_text(encoding="utf-8")
    match = re.search(
        r'<script type="application/json" class="metadata-explorer-model">\s*(.*?)\s*</script>',
        text,
        re.DOTALL,
    )
    assert match is not None
    payload = json.loads(match.group(1))
    assert set(payload) == {name.removeprefix("METADATA_") for name in CANONICAL_METADATA_TABLES}
    for name, model in METADATA_TABLE_MODELS.items():
        entry = payload[name.removeprefix("METADATA_")]
        assert entry["purpose"] == model["purpose"]
        assert entry["grain"] == model["grain"]
        assert entry["primary_key"] == model["primary_key"]
        assert [
            (fk["local_field"], fk["referenced_table"], fk["referenced_field"])
            for fk in entry["foreign_keys"]
        ] == [
            (fk["local_field"], fk["referenced_table"], fk["referenced_field"])
            for fk in model["foreign_keys"]
        ]
    agreement_fk = payload["DATA_AGREEMENT"]["foreign_keys"]
    assert [fk["local_field"] for fk in agreement_fk] == [
        "provider_steward_id", "recipient_steward_id"
    ]


def test_metadata_explorer_compact_details_and_hover_summary() -> None:
    """Ensure the explorer does not regress to oversized admonitions or key-only lists."""
    from pathlib import Path

    root = Path(__file__).parents[2]
    js = (root / "docs/javascripts/metadata-explorer.js").read_text(encoding="utf-8")
    css = (root / "docs/stylesheets/metadata-explorer.css").read_text(encoding="utf-8")
    assert "canonicalModels = JSON.parse" in js
    assert "metadata-explorer-model" in js
    assert "mouseenter" in js and "focus" in js and "showTooltip" in js
    assert "model.grain" in js and "model.purpose" in js
    assert "keyJoinRows" in js and "fk.referenced_field" in js
    assert "logicalJoinKeys" in js
    assert "metadata-explorer-related-joins" in js
    assert "metadata-explorer-detail-quick" not in js
    assert "metadata-explorer-tooltip[hidden]" in css
    assert ".md-typeset .fabricops-metadata-explorer details.metadata-explorer-section" in css
    assert "background: transparent;" in css
    assert "font-size: 14px;" in css
