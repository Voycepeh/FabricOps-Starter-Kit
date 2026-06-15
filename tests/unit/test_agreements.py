"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import pytest

import fabricops_kit.data_agreement as agreement
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

    monkeypatch.setattr(agreement, "_build_runtime_audit_fields", lambda **kwargs: {field: f"audit:{field}" for field in audit_columns})
    monkeypatch.setattr(agreement, "_list_data_stewards", lambda *args, **kwargs: [steward_row()])
    monkeypatch.setattr(agreement, "_generate_agreement_id", lambda: "DA-GENERATED")
    monkeypatch.setattr(agreement, "_write_row", lambda **kwargs: writes.append(kwargs))

    config = agreement_config(metadata_tables={"data_steward": "CUSTOM_STEWARD", "data_agreement": "CUSTOM_AGREEMENT"})
    steward = agreement._create_or_update_data_steward(
        spark=object(), config=config, env_name="dev", values=steward_row(), custom_fields={"group": "Shared Services"}
    )
    created = agreement._create_or_update_data_agreement(
        spark=object(), config=config, env_name="dev", values=agreement_row(), custom_fields={"consumer_group": "ODI"}
    )
    updated = agreement._create_or_update_data_agreement(
        spark=object(), config=config, env_name="dev", values=agreement_row(), selected_agreement=created
    )

    assert steward["custom_fields_json"]
    assert created["agreement_id"] == updated["agreement_id"] == "DA-GENERATED"
    assert (created["contract_version"], updated["contract_version"]) == ("1.0.0", "1.1.0")
    assert [write["table"] for write in writes] == ["CUSTOM_STEWARD", "CUSTOM_AGREEMENT", "CUSTOM_AGREEMENT"]
    assert all(write["env_name"] == "dev" for write in writes)


def test_agreement_validation_and_evidence_path_parsing_fail_before_writes(monkeypatch):
    """Verify agreement validation and evidence path parsing fail before writes."""
    monkeypatch.setattr(agreement, "_list_data_stewards", lambda *args, **kwargs: [steward_row()])
    monkeypatch.setattr(agreement, "_write_row", lambda **kwargs: pytest.fail("invalid data should not be written"))

    with pytest.raises(ValueError, match="steward_name"):
        agreement._create_or_update_data_steward(spark=object(), config=agreement_config(), env_name="dev", values=steward_row(steward_name=""))
    with pytest.raises(ValueError, match="recipient"):
        agreement._create_or_update_data_agreement(spark=object(), config=agreement_config(), env_name="dev", values=agreement_row(recipient=""))

    references = agreement._prepare_evidence_file_references("- Files/fabricops/evidence/a.pdf\n* Files/fabricops/evidence/b.docx\n")
    assert [item["file_name"] for item in references] == ["a.pdf", "b.docx"]
    with pytest.raises(ValueError, match="Files/"):
        agreement._prepare_evidence_file_references("Files/fabricops/evidence/a.pdf\n/tmp/local.pdf")
