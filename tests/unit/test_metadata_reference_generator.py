"""Focused checks for generated metadata reference pages."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from fabricops_kit.config.metadata_schemas import (
    AUDIT_SCHEMA_FIELDS,
    CANONICAL_METADATA_TABLES,
    metadata_table_schema_registry,
    metadata_table_schema_rows,
)
from scripts import generate_individual_function_reference_pages as generator


ROOT = Path(__file__).resolve().parents[2]
METADATA_DIR = ROOT / "docs" / "reference" / "metadata"
METADATA_INDEX = ROOT / "docs" / "reference" / "metadata.md"
PUBLIC_LINK_PATTERN = re.compile(r"\[\`([a-zA-Z0-9_]+)\`\]\(\.\./\.\./api/reference/([a-zA-Z0-9_]+)\.md\)")


def _page_path(table_name: str) -> Path:
    return METADATA_DIR / f"{table_name.lower()}.md"


def _schema_rows_from_page(table_name: str) -> list[dict[str, str]]:
    """Return generated schema rows parsed from one metadata page."""
    rows = []
    in_schema = False
    for line in _page_path(table_name).read_text(encoding="utf-8").splitlines():
        if line == "## Implemented schema":
            in_schema = True
            continue
        if in_schema and line.startswith("## "):
            break
        if not in_schema or not line.startswith("| `"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        rows.append(
            {
                "name": cells[0].strip("`"),
                "type": cells[1].strip("`"),
                "managed_by": cells[2],
                "description": cells[3],
            }
        )
    return rows


def test_metadata_reference_contract_covers_canonical_registry() -> None:
    """Every canonical metadata table must exist in the registry and owner contract."""
    registry = metadata_table_schema_registry()
    _purposes, owner_contract = generator.parse_metadata_reference_contract()

    assert list(CANONICAL_METADATA_TABLES)
    assert set(CANONICAL_METADATA_TABLES).issubset(registry)
    assert set(CANONICAL_METADATA_TABLES).issubset(owner_contract)


def test_metadata_reference_pages_only_exist_for_canonical_tables() -> None:
    """Generated metadata pages should exist once per canonical table and no more."""
    expected = {f"{table_name.lower()}.md" for table_name in CANONICAL_METADATA_TABLES}
    actual = {path.name for path in METADATA_DIR.glob("*.md")}

    assert actual == expected


def test_generated_metadata_pages_match_registry_order_and_types() -> None:
    """Every schema field should render once, in registry order, with stable type labels."""
    registry = metadata_table_schema_registry()

    for table_name in CANONICAL_METADATA_TABLES:
        expected_rows = metadata_table_schema_rows(registry[table_name])
        rendered_rows = _schema_rows_from_page(table_name)

        assert [row["name"] for row in rendered_rows] == [row["name"] for row in expected_rows]
        assert [row["type"] for row in rendered_rows] == [row["type"] for row in expected_rows]
        assert len(rendered_rows) == len(expected_rows)
        assert len({row["name"] for row in rendered_rows}) == len(expected_rows)


def test_generated_metadata_pages_drop_nullable_and_respect_audit_fields() -> None:
    """Metadata schema pages should omit Nullable and only show audit fields when implemented."""
    audit_fields = [name for name, _kind, _nullable in AUDIT_SCHEMA_FIELDS]
    registry = metadata_table_schema_registry()

    for table_name in CANONICAL_METADATA_TABLES:
        text = _page_path(table_name).read_text(encoding="utf-8")
        rendered_field_names = [row["name"] for row in _schema_rows_from_page(table_name)]
        schema_field_names = [row["name"] for row in metadata_table_schema_rows(registry[table_name])]

        assert "| Column | Data type | Managed by | Description |" in text
        assert "Nullable" not in text
        for audit_field in audit_fields:
            if audit_field in schema_field_names:
                assert audit_field in rendered_field_names
            else:
                assert audit_field not in rendered_field_names


def test_metadata_owner_rendering_links_public_functions_and_shows_internal_sources() -> None:
    """Public owners should link to callable pages and internal owners should stay as code."""
    _purposes, owner_contract = generator.parse_metadata_reference_contract()
    public_callable_set = generator.public_callable_names()

    steward_owner = generator._metadata_managed_by(
        "METADATA_DATA_STEWARD",
        "steward_id",
        column_owners=owner_contract,
        public_callable_set=public_callable_set,
    )
    audit_owner = generator._metadata_managed_by(
        "METADATA_DATA_STEWARD",
        "_committed_at",
        column_owners=owner_contract,
        public_callable_set=public_callable_set,
    )

    assert "[`widget_render_data_steward`](../../api/reference/widget_render_data_steward.md)" in steward_owner
    assert "`fabricops_kit.widgets.widget_render_data_steward._create_or_update_data_steward`" in steward_owner
    assert "`fabricops_kit.config.audit.build_runtime_audit_fields`" in audit_owner


def test_metadata_reference_contract_rejects_missing_source_callable() -> None:
    """Invalid callable owner mappings should fail clearly."""
    public_callable_set = generator.public_callable_names()

    try:
        generator._render_metadata_owner(
            "fabricops_kit.widgets.shared.not_a_real_callable",
            public_callable_set=public_callable_set,
        )
    except RuntimeError as exc:
        assert "Metadata owner callable does not exist in source" in str(exc)
    else:  # pragma: no cover - defensive failure branch
        raise AssertionError("Expected missing metadata owner callable to raise RuntimeError.")


def test_metadata_pages_render_valid_public_owner_links() -> None:
    """Every rendered public owner link should resolve to a known generated callable page."""
    public_callable_set = generator.public_callable_names()
    text = "\n".join(path.read_text(encoding="utf-8") for path in METADATA_DIR.glob("*.md"))
    matches = PUBLIC_LINK_PATTERN.findall(text)

    assert matches
    for label, target in matches:
        assert label == target
        assert target in public_callable_set
        assert (ROOT / "docs" / "api" / "reference" / f"{target}.md").exists()


def test_metadata_reference_generation_is_deterministic_for_metadata_docs() -> None:
    """Regenerating metadata docs twice should produce byte-identical metadata pages."""
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src"), "FABRICOPS_PRESERVE_GENERATED_ARTIFACT_TIMESTAMPS": "1"}
    before = {
        str(path.relative_to(ROOT)): path.read_text(encoding="utf-8")
        for path in [METADATA_INDEX, *sorted(METADATA_DIR.glob("*.md"))]
    }

    subprocess.run(
        [sys.executable, "scripts/generate_individual_function_reference_pages.py"],
        cwd=ROOT,
        env=env,
        check=True,
    )
    after = {
        str(path.relative_to(ROOT)): path.read_text(encoding="utf-8")
        for path in [METADATA_INDEX, *sorted(METADATA_DIR.glob("*.md"))]
    }

    assert before == after
