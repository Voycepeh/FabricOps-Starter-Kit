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
    def paths(schema, prefix=""):
        result = set()
        for field in getattr(schema, "fields", []):
            path = prefix + field.name
            result.add(path)
            dtype = field.dataType
            if hasattr(dtype, "elementType"):
                result.update(paths(dtype.elementType, path + "[]."))
            elif hasattr(dtype, "fields"):
                result.update(paths(dtype, path + "."))
        return result
    return {name: paths(schema) for name, schema in metadata_table_schema_registry().items()}



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
        writer_section = page.split("## Writer functions", 1)[1].split(
            "## Used in Workflow Template", 1
        )[0]
        assert "No public writer function" not in writer_section
        assert "../../api/reference/" in writer_section
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
    activated_page = first_pages["metadata_pipeline_registry.md"]
    assert "`approvals`" in activated_page and "`authority_id`" in activated_page
    assert "atomic native authority" in activated_page
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
    assert len(links) == 12
    assert len({link.get("{http://www.w3.org/1999/xlink}href") for link in links}) == 12
    assert "metadata-explorer-approved-svg" in js
    assert "fabricops-metadata-approved.svg" in js
    assert ".metadata-explorer-approved-svg a.selected > rect" in css
    assert "const layoutOrder" not in js
    assert 'class: "metadata-explorer-cardinality"' not in js
    assert "white-space: normal" in css
    assert "overflow-wrap: anywhere" in css
    assert "DOMParser" in js and "fetch(url)" in js
    assert "sectionDetails(implemented)" in js
    assert 'document.createElement("section")' in js
    assert "metadata-explorer-viewport" in js
    assert "metadata-explorer-details" in js
    assert "scrollIntoView" in js
    assert "data-reference-content" in js
    assert 'status && title === "ACTIVATED_PIPELINE"' not in js
    assert '["ACTIVATED_PIPELINE", "governance"' not in js
    assert "metadata-explorer-reference-label" in js
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
    public_names = generator.public_callable_names()
    for name, model in METADATA_TABLE_MODELS.items():
        entry = payload[name.removeprefix("METADATA_")]
        assert entry["purpose"] == model["purpose"]
        assert entry["grain"] == model["grain"]
        assert entry["primary_key"] == model["primary_key"]
        assert entry["write_entrypoints"]
        assert all(name in public_names for name in entry["write_entrypoints"])
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
    assert ".metadata-explorer-implemented-schema" in css
    assert "metadata-explorer-detail-facts" in css
    assert "font-size: 14px;" in css


def test_metadata_explorer_writer_and_schema_display() -> None:
    """Ensure table click focuses scan-first summary and shows the full schema."""
    from pathlib import Path

    root = Path(__file__).parents[2]
    js = (root / "docs/javascripts/metadata-explorer.js").read_text(encoding="utf-8")
    css = (root / "docs/stylesheets/metadata-explorer.css").read_text(encoding="utf-8")
    assert 'section.heading === "Implemented schema"' in js
    assert 'sectionDetails(implemented)' in js
    assert 'detail.scrollIntoView({' in js
    assert 'detail.focus({ preventScroll: true })' in js
    assert 'select("DATA_AGREEMENT")' in js
    assert 'select(name, { focusDetails: true })' in js
    assert "model.write_entrypoints" in js
    assert "Written via" in js
    assert "Used in Workflow Template" not in js
    assert "metadata-explorer-summary" in js
    assert "metadata-explorer-detail-facts" in css
    assert ".metadata-explorer-implemented-schema" in css
    assert ".metadata-explorer-reference-content" in css
    assert 'document.createElement("details")' not in js


def test_audited_metadata_writers_cover_all_tables() -> None:
    """Entry points are public and do not confuse read-only effective access with persistence."""
    from scripts.reference_docs_metadata import METADATA_EXPLORER_WRITE_ENTRYPOINTS

    assert set(METADATA_EXPLORER_WRITE_ENTRYPOINTS) == set(CANONICAL_METADATA_TABLES)
    assert all(METADATA_EXPLORER_WRITE_ENTRYPOINTS.values())
    assert set(METADATA_EXPLORER_WRITE_ENTRYPOINTS["METADATA_DATA_PROFILED"]) >= {
        "orchestrate_read", "orchestrate_write", "profile_table"
    }
    assert "finalize_pipeline" in METADATA_EXPLORER_WRITE_ENTRYPOINTS["METADATA_PIPELINE_RUN"]
    assert "setup_pipeline" in METADATA_EXPLORER_WRITE_ENTRYPOINTS["METADATA_PIPELINE_REGISTRY"]
    assert "scan_effective_access" not in METADATA_EXPLORER_WRITE_ENTRYPOINTS["METADATA_DATA_ACCESS"]
    assert set(METADATA_EXPLORER_WRITE_ENTRYPOINTS["METADATA_DATA_ACCESS"]) == {
        "scan_workspace_access", "scan_onelake_access", "scan_sql_access"
    }


def test_metadata_explorer_full_text_and_prominent_navigation() -> None:
    """Full table descriptions remain readable and the architecture map is discoverable."""
    from pathlib import Path

    root = Path(__file__).parents[2]
    script = (root / "docs/javascripts/metadata-explorer.js").read_text(encoding="utf-8")
    styles = (root / "docs/stylesheets/metadata-explorer.css").read_text(encoding="utf-8")
    homepage = (root / "docs/index.md").read_text(encoding="utf-8")
    how_it_works = (root / "docs/how-fabricops-works.md").read_text(encoding="utf-8")

    assert 'description.textContent = model.purpose' in script
    assert 'escapeHtml(model.purpose || status || "")' in script
    assert 'brief(model.purpose' not in script
    assert 'One row represents' in script
    assert 'overflow-wrap: anywhere;' in styles
    assert 'width: min(430px' in styles
    assert 'class="fabricops-metadata-preview" href="reference/metadata/"' in homepage
    assert 'src="assets/fabricops-metadata-approved.svg"' in homepage
    assert 'class="fabricops-metadata-preview fabricops-metadata-preview--compact"' in how_it_works
    assert 'href="../reference/metadata/"' in how_it_works
    assert 'src="../assets/fabricops-metadata-approved.svg"' in how_it_works
    assert ".fabricops-metadata-preview__image" in styles
    assert "## The Big Picture" in how_it_works
    assert how_it_works.index('class="fabricops-metadata-preview') < how_it_works.index("## Workspace Architecture")


def test_metadata_table_summaries_remain_human_readable_and_detailed_notes_preserved() -> None:
    """Reader-facing summaries should be concise without losing technical reference detail."""
    from pathlib import Path

    root = Path(__file__).parents[2]
    for table_name, model in METADATA_TABLE_MODELS.items():
        purpose = model["purpose"]
        grain = model["grain"]
        assert len(purpose) <= 190, (table_name, purpose)
        assert len(grain) <= 125, (table_name, grain)
        assert "immutable frozen table definition" not in purpose.lower()
        page = (root / "docs/reference/metadata" / f"{table_name.lower()}.md").read_text(
            encoding="utf-8"
        )
        assert f"\n\n{purpose}\n\n## Writer functions" in page
        assert f"**Grain:** {grain}" in page
        notes = model.get("implementation_notes")
        if notes:
            assert f"**Implementation details:** {notes}" in page
        else:
            assert "**Implementation details:**" not in page


def test_generated_svg_preserves_layout_and_has_explicit_cardinality_for_all_relationships() -> None:
    """Show actual table-to-table relationships, not arrowheads or phantom self-links."""
    from pathlib import Path
    import xml.etree.ElementTree as ET

    root = Path(__file__).parents[2]
    svg = root / "docs/assets/fabricops-metadata-approved.svg"
    layout = root / "docs/assets/fabricops-metadata-layout.svg"
    generator_script = root / "scripts/generate_metadata_erd_svg.mjs"
    assert svg.is_file() and layout.is_file() and generator_script.is_file()
    svg_tree = ET.parse(svg)
    namespace = "{http://www.w3.org/2000/svg}"
    titles = [
        node.text
        for node in svg_tree.findall(f".//{namespace}a/{namespace}title")
    ]
    assert len(titles) == len(CANONICAL_METADATA_TABLES) == 12
    assert set(titles) == {
        f"Open metadata documentation: {name.removeprefix('METADATA_')}"
        for name in CANONICAL_METADATA_TABLES
    }

    connectors = svg_tree.findall(
        f".//{namespace}g[@id='metadata-er-relationships']/{namespace}g"
    )
    assert len(connectors) >= 14
    actual = {
        (edge.get("data-from"), edge.get("data-to")): edge
        for edge in connectors
    }
    assert len(actual) == len(connectors)
    assert all(source != target for source, target in actual)
    assert all(edge.get("data-cardinality") in {"1:N", "N:M"} for edge in connectors)
    assert all(edge.find(f"{namespace}path") is not None for edge in connectors)
    assert ("PIPELINE_REGISTRY", "PIPELINE_RUN") in actual
    assert ("PIPELINE_RUN", "DATA_CONTRACT") in actual
    assert actual[("PIPELINE_REGISTRY", "PIPELINE_RUN")].get("data-kind") == "nested"
    assert actual[("DATA_AGREEMENT", "PIPELINE_REGISTRY")].get("data-cardinality") == "1:N"
    assert actual[("PIPELINE_REGISTRY", "PIPELINE_RUN")].get("data-cardinality") == "1:N"
    assert actual[("PIPELINE_REGISTRY", "DATA_CONTRACT")].get("data-cardinality") == "N:M"
    assert actual[("PIPELINE_RUN", "DATA_CONTRACT")].get("data-cardinality") == "N:M"
    assert all(edge.get("data-cardinality") == "1:N" for edge in connectors if edge.get("data-kind") == "physical")
    assert all("arrow" not in (edge.find(f"{namespace}title").text or "").lower() for edge in connectors)
    assert "stroke-dasharray" not in svg.read_text(encoding="utf-8")
    registry = next(a for a in svg_tree.findall(f".//{namespace}a")
                    if a.find(f"{namespace}title").text.endswith("PIPELINE_REGISTRY"))
    assert registry.get("transform") is None
    assert registry.find(f"{namespace}rect").get("y") == "78"
    assert "Engineering home" in svg.read_text(encoding="utf-8")
    # Keep design asset, generated output and canonical reference in sync.
    script = generator_script.read_text(encoding="utf-8")
    assert "renderMetadataSvg(layout, models)" in script
    assert "--check" in script
    assert "Missing FK connector" in script
    assert "Unexpected approved diagram table count" not in script


def test_generated_svg_check_ignores_windows_line_endings_but_detects_real_drift(tmp_path) -> None:
    """A Windows CRLF checkout must validate without concealing actual SVG differences."""
    import shutil
    import subprocess
    from pathlib import Path

    import pytest

    node = shutil.which("node")
    if not node:
        pytest.skip("Node.js is required to execute the SVG generator")

    source_root = Path(__file__).parents[2]
    paths = (
        "scripts/generate_metadata_erd_svg.mjs",
        "docs/assets/fabricops-metadata-layout.svg",
        "docs/assets/fabricops-metadata-approved.svg",
        "docs/reference/metadata.md",
    )
    for relative in paths:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        raw = (source_root / relative).read_bytes().replace(b"\r\n", b"\n")
        target.write_bytes(raw.replace(b"\n", b"\r\n"))

    command = [node, str(tmp_path / paths[0]), "--check"]
    first = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
    assert first.returncode == 0, first.stdout + first.stderr

    target = tmp_path / "docs/assets/fabricops-metadata-approved.svg"
    corrupted = target.read_bytes().replace(b"DATA_AGREEMENT", b"DATA_AGREEMENX", 1)
    target.write_bytes(corrupted)
    second = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True)
    assert second.returncode != 0
    assert "diagram drift" in second.stderr


def test_metadata_relationship_reference_label_does_not_overlap_table_name() -> None:
    """Identity references are plain labels with enough room at all widths."""
    from pathlib import Path

    root = Path(__file__).parents[2]
    js = (root / "docs/javascripts/metadata-explorer.js").read_text(encoding="utf-8")
    css = (root / "docs/stylesheets/metadata-explorer.css").read_text(encoding="utf-8")

    assert "const referenceOnly = !edge[2];" in js
    assert "metadata-explorer-reference-label" in js
    assert "Application-enforced identity reference" in js
    assert "grid-template-columns: 94px minmax(140px, 195px)" in css
    assert "grid-template-columns: 94px minmax(0,1fr)" in css
    assert ".metadata-explorer-reference-label {" in css
    assert "justify-self: start;" in css
    assert "max-width: 100%;" in css


def test_metadata_explorer_navigation_matches_canonical_svg() -> None:
    """Removed tables and stale relationship counts must not disable the interactive SVG."""
    import re
    import xml.etree.ElementTree as ET
    from pathlib import Path

    root = Path(__file__).parents[2]
    js = (root / "docs/javascripts/metadata-explorer.js").read_text(encoding="utf-8")
    definitions = js.split("const definitions = [", 1)[1].split("\n  ];", 1)[0]
    names = re.findall(r'^    \["([A-Z_]+)"', definitions, re.MULTILINE)
    assert len(names) == len(set(names)) == len(CANONICAL_METADATA_TABLES)
    assert set(names) == {name.removeprefix("METADATA_") for name in CANONICAL_METADATA_TABLES}
    links = js.split("const links = [", 1)[1].split("\n  ];", 1)[0]
    relationships = set(re.findall(r'^    \["([A-Z_]+)", "([A-Z_]+)", "([1NM:]+)"', links, re.MULTILINE))
    svg = ET.parse(root / "docs/assets/fabricops-metadata-approved.svg")
    edges = svg.findall(".//{http://www.w3.org/2000/svg}g[@class='metadata-er-relationship']")
    assert relationships == {(edge.get("data-from"), edge.get("data-to"), edge.get("data-cardinality")) for edge in edges}
    assert "Object.keys(buttons).length !== definitions.length" in js
    assert "ACTIVATION_STATE" not in js
