"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import pytest

import fabricops_kit.widgets.shared as agreement
import importlib

evidence = importlib.import_module("fabricops_kit.widgets.widget_render_agreement_evidence")
from tests.helpers import agreement_config, agreement_row, steward_row

pytestmark = pytest.mark.unit


def test_agreement_metadata_schemas_and_widget_fields_keep_only_supported_business_columns():
    """Verify agreement metadata schemas and widget fields keep only supported business columns."""
    config = agreement_config()

    steward_fields = agreement._get_widget_visible_fields(config, "data_steward_widget")
    agreement_fields = agreement._get_widget_visible_fields(config, "data_agreement_widget")

    assert set(agreement.DATA_AGREEMENT_EVIDENCE_FIELDS).issuperset({"agreement_id", "contract_version", "file_path"})
    assert {"recipient", "approved_usage_internal", "approved_usage_external", "approved_usage_research"}.issubset(agreement_fields)
    assert "approved_usage" not in agreement_fields
    assert "custom_fields_json" not in steward_fields + agreement_fields
    assert "agreement_id" not in agreement_fields


def test_steward_and_agreement_create_update_write_append_only_metadata(monkeypatch):
    """Verify steward and agreement create update write append only metadata."""
    audit_columns = agreement.STANDARD_RUNTIME_AUDIT_COLUMNS
    writes = []

    monkeypatch.setattr(agreement, "build_runtime_audit_fields", lambda **kwargs: {field: f"audit:{field}" for field in audit_columns})
    monkeypatch.setattr(agreement, "_list_data_stewards", lambda *args, **kwargs: [steward_row()])
    monkeypatch.setattr(agreement, "_generate_agreement_id", lambda *args, **kwargs: "DA-GENERATED")
    monkeypatch.setattr(agreement, "write_widget_metadata_row", lambda **kwargs: writes.append(kwargs))

    config = agreement_config(metadata_tables={"data_steward": "CUSTOM_STEWARD", "data_agreement": "CUSTOM_AGREEMENT"})
    steward = agreement._create_or_update_data_steward(
        spark=object(), config=config, env="dev", values=steward_row(), custom_fields={"group": "Shared Services"}
    )
    created = agreement._create_or_update_data_agreement(
        spark=object(), config=config, env="dev", values=agreement_row(), custom_fields={"consumer_group": "ODI"}
    )
    updated = agreement._create_or_update_data_agreement(
        spark=object(), config=config, env="dev", values=agreement_row(), selected_agreement=created
    )

    assert steward["custom_fields_json"]
    assert created["agreement_id"] == updated["agreement_id"] == "DA-GENERATED"
    assert (created["contract_version"], updated["contract_version"]) == ("1.0.0", "1.1.0")
    assert [write["table"] for write in writes] == ["CUSTOM_STEWARD", "CUSTOM_AGREEMENT", "CUSTOM_AGREEMENT"]
    assert all(write["env"] == "dev" for write in writes)


def test_agreement_validation_and_evidence_path_parsing_fail_before_writes(monkeypatch):
    """Verify agreement validation and evidence path parsing fail before writes."""
    monkeypatch.setattr(agreement, "_list_data_stewards", lambda *args, **kwargs: [steward_row()])
    monkeypatch.setattr(agreement, "write_widget_metadata_row", lambda **kwargs: pytest.fail("invalid data should not be written"))

    with pytest.raises(ValueError, match="steward_name"):
        agreement._create_or_update_data_steward(spark=object(), config=agreement_config(), env="dev", values=steward_row(steward_name=""))
    with pytest.raises(ValueError, match="recipient"):
        agreement._create_or_update_data_agreement(spark=object(), config=agreement_config(), env="dev", values=agreement_row(recipient=""))

    references = evidence._prepare_evidence_file_references("- Files/fabricops/evidence/a.pdf\n* Files/fabricops/evidence/b.docx\n")
    assert [item["file_name"] for item in references] == ["a.pdf", "b.docx"]
    with pytest.raises(ValueError, match="Files/"):
        evidence._prepare_evidence_file_references("Files/fabricops/evidence/a.pdf\n/tmp/local.pdf")


def test_stale_agreement_modules_are_removed_and_not_imported():
    """Verify stale agreement modules are removed from source ownership."""
    from pathlib import Path

    root = Path(__file__).parents[2]
    assert not (root / "src" / "fabricops_kit" / "data_agreement.py").exists()
    assert not (root / "src" / "fabricops_kit" / "agreement_selection_state.py").exists()

    scanned = [root / "src", root / "templates", root / "docs"]
    offenders = []
    for base in scanned:
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix not in {".py", ".md", ".yml", ".yaml", ".json", ".ipynb"}:
                continue
            text = path.read_text(encoding="utf-8")
            for fragment in (
                "fabricops_kit.data_agreement",
                "fabricops_kit.agreement_selection_state",
                "from .data_agreement",
                "agreement_selection_state import",
            ):
                if fragment in text:
                    offenders.append(f"{path.relative_to(root)} imports {fragment}")
    assert offenders == []
