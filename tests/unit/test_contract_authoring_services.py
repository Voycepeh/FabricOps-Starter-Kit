"""Focused tests for UI-independent Data Contract authoring services."""

from __future__ import annotations

import pytest

from fabricops_kit import contract_authoring as service


def test_exact_contract_version_and_environment_isolation():
    """Rows are isolated by contract version and environment."""
    rows = [
        {"contract_id": "c", "contract_version": 1, "environment_name": "dev", "value": "one"},
        {"contract_id": "c", "contract_version": 2, "environment_name": "dev", "value": "two"},
        {"contract_id": "c", "contract_version": 2, "environment_name": "prod", "value": "prod"},
    ]
    assert service.contract_version_records(
        rows, contract_id="c", contract_version=2, environment_name="dev"
    ) == [rows[1]]


@pytest.mark.parametrize("contract_id,version", [("", 1), ("c", 0), ("c", "bad")])
def test_invalid_contract_identity_is_rejected(contract_id, version):
    """Missing and malformed contract identities fail clearly."""
    with pytest.raises(ValueError):
        service.validate_contract_identity(contract_id, version)


def test_enrichment_build_preserves_exact_owner_and_column(monkeypatch):
    """Enrichment preserves its exact contract and Catalogue ownership."""
    monkeypatch.setattr(service, "build_runtime_audit_fields", lambda **kwargs: {"_activity_id": "a"})
    rows = service.build_enrichment_records([{
        "contract_id": "contract-orders", "contract_version": 3,
        "environment_name": "dev", "enrichment_level": "column",
        "column_id": "col-id", "enrichment_type": "Description", "value": "Identifier",
    }], env="dev")
    assert rows[0]["contract_id"] == "contract-orders"
    assert rows[0]["contract_version"] == 3
    assert rows[0]["column_id"] == "col-id"
    with pytest.raises(ValueError, match="environment"):
        service.build_enrichment_records([{**rows[0], "environment_name": "prod"}], env="dev")


def test_draft_validation_returns_only_owned_governance_rows():
    """Draft state excludes other versions and environments."""
    draft = {"contract_id": "c", "contract_version": 2, "agreement_id": "a", "agreement_version": "1", "table_id": "t", "status": "draft"}
    catalogue = [{"table_id": "t", "environment_name": "dev", "metadata_level": "table"}]
    enrichment = [
        {"contract_id": "c", "contract_version": 2, "environment_name": "dev"},
        {"contract_id": "c", "contract_version": 1, "environment_name": "dev"},
    ]
    guardrails = [
        {"contract_id": "c", "contract_version": 2, "environment_name": "dev"},
        {"contract_id": "c", "contract_version": 2, "environment_name": "prod"},
    ]
    state = service.validate_contract_draft(
        draft, catalogue_rows=catalogue, enrichment_rows=enrichment,
        guardrail_rows=guardrails, environment_name="dev",
    )
    assert state["enrichment"] == [enrichment[0]]
    assert state["guardrails"] == [guardrails[0]]
    with pytest.raises(ValueError, match="draft"):
        service.validate_contract_draft(
            {**draft, "status": "frozen"}, catalogue_rows=catalogue,
            enrichment_rows=[], guardrail_rows=[], environment_name="dev",
        )


def test_guardrail_save_uses_metadata_target(monkeypatch):
    """Guardrail persistence routes through the metadata target."""
    writes = []
    monkeypatch.setattr(service, "canonical_guardrail_rule_record", lambda row, **kwargs: dict(row))
    monkeypatch.setattr(service, "coerce_metadata_row_types", lambda _table, row: row)
    monkeypatch.setattr(service, "metadata_table_physical_schema", lambda *_args: "governance")
    monkeypatch.setattr(service, "write_lakehouse_table_core", lambda *args, **kwargs: writes.append((args, kwargs)))
    spark = type("Spark", (), {"createDataFrame": lambda self, rows: rows})()
    record = {"contract_id": "c", "contract_version": 2, "environment_name": "dev"}
    assert service.save_guardrails([record], config=object(), env="dev", spark_session=spark) == [record]
    assert writes[0][1]["target"] == "metadata"
    assert writes[0][1]["schema"] == "governance"


def test_freeze_record_is_immutable_payload_transition():
    """Freezing serializes the payload and closes the draft."""
    frozen = service.freeze_contract_record(
        draft={"contract_id": "c", "contract_version": 1, "status": "draft", "contract_payload_json": None},
        payload={"contract": {"contract_id": "c", "contract_version": 1}}, audit={"_activity_id": "freeze"},
    )
    assert frozen["status"] == "frozen"
    assert frozen["is_active"] is False
    assert '"contract_id":"c"' in frozen["contract_payload_json"]
