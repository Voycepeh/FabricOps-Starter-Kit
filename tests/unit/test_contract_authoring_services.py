"""Focused tests for UI-independent Data Contract authoring services."""

from __future__ import annotations

import pytest

from fabricops_kit.data_contract import shared as service


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
    draft = {"contract_id": "c", "contract_version": 2, "agreement_id": "a", "agreement_version": "1", "table_id": "t", "environment_name": "dev", "status": "draft"}
    catalogue = [{"table_id": "t", "environment_name": "dev", "metadata_level": "table"}]
    enrichment = [
        {"contract_id": "c", "contract_version": 2, "environment_name": "dev", "enrichment_level": "table", "enrichment_type": "Description"},
        {"contract_id": "c", "contract_version": 1, "environment_name": "dev", "enrichment_level": "table", "enrichment_type": "Description"},
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


def test_authoring_state_resolves_contract_identity_in_requested_environment(monkeypatch):
    """The same contract identity in another environment cannot leak into state."""
    contracts = [
        {"contract_id": "c", "contract_version": 2, "agreement_id": "dev-a", "agreement_version": "1", "table_id": "dev-t", "environment_name": "dev", "status": "draft"},
        {"contract_id": "c", "contract_version": 2, "agreement_id": "prod-a", "agreement_version": "1", "table_id": "prod-t", "environment_name": "prod", "status": "draft"},
    ]
    tables = {
        service.DATA_CONTRACT_TABLE: contracts,
        "METADATA_DATA_CATALOGUE": [
            {"table_id": "dev-t", "environment_name": "dev", "metadata_level": "table"},
            {"table_id": "prod-t", "environment_name": "prod", "metadata_level": "table"},
        ],
        service.ENRICHMENT_TABLE: [],
        service.GUARDRAIL_TABLE: [],
    }
    monkeypatch.setattr(service, "metadata_table_physical_schema", lambda *_args: "governance")
    monkeypatch.setattr(service, "read_lakehouse_table_core", lambda table, **_kwargs: tables[table])

    state = service.get_contract_authoring_state(
        config=object(), env="dev", spark_session=object(),
        contract_id="c", contract_version=2,
    )

    assert state["contract"]["agreement_id"] == "dev-a"
    assert state["table_id"] == "dev-t"


def test_draft_environment_must_match_authoring_environment():
    """Draft validation rejects cross-environment contract rows explicitly."""
    draft = {"contract_id": "c", "contract_version": 1, "agreement_id": "a", "agreement_version": "1", "table_id": "t", "environment_name": "prod", "status": "draft"}
    with pytest.raises(ValueError, match="environment_name"):
        service.validate_contract_draft(
            draft, catalogue_rows=[], enrichment_rows=[], guardrail_rows=[],
            environment_name="dev",
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
        draft={"contract_id": "c", "contract_version": 1, "environment_name": "dev", "status": "draft", "contract_payload_json": None},
        payload={"contract": {"contract_id": "c", "contract_version": 1}}, audit={"_activity_id": "freeze"},
    )
    assert frozen["status"] == "frozen"
    assert frozen["is_active"] is False
    assert '"contract_id":"c"' in frozen["contract_payload_json"]


def test_enrichment_model_is_descriptive_and_level_specific(monkeypatch):
    """Allow only the minimal table and column descriptive fields."""
    monkeypatch.setattr(service, "build_runtime_audit_fields", lambda **_kwargs: {})
    common = {"contract_id": "c", "contract_version": 1, "environment_name": "dev", "value": "value"}
    records = service.build_enrichment_records([
        {**common, "enrichment_level": "table", "enrichment_type": "Description"},
        {**common, "enrichment_level": "table", "enrichment_type": "Classification"},
        {**common, "enrichment_level": "column", "column_id": "col", "enrichment_type": "Classification"},
    ], env="dev")
    assert [row["enrichment_type"] for row in records] == ["Description", "Classification", "Classification"]
    with pytest.raises(ValueError, match="descriptive metadata only"):
        service.build_enrichment_records([{**common, "enrichment_level": "column", "column_id": "col", "enrichment_type": "Personal_identifier"}], env="dev")
    with pytest.raises(ValueError, match="Column enrichment_type"):
        service.build_enrichment_records([{**common, "enrichment_level": "column", "column_id": "col", "enrichment_type": "Sensitivity"}], env="dev")


def test_canonical_enrichment_state_removes_non_descriptive_rows():
    """Exclude old or unknown types from current authoring and frozen state."""
    rows = [
        {"enrichment_level": "column", "enrichment_type": "Description"},
        {"enrichment_level": "column", "enrichment_type": "Classification"},
        {"enrichment_level": "column", "enrichment_type": "Sensitivity"},
        {"enrichment_level": "column", "enrichment_type": "Personal_identifier"},
    ]
    assert [row["enrichment_type"] for row in service.canonical_enrichment_state(rows)] == ["Description", "Classification"]


@pytest.mark.parametrize("guardrail_type", ["schema", "freshness", "changes", "data_quality"])
@pytest.mark.parametrize("action", ["Warn", "Block"])
def test_guardrail_service_normalizes_all_supported_types_and_actions(
    monkeypatch, guardrail_type, action
):
    """All authoring subtypes use one exact-version Guardrail service contract."""
    monkeypatch.setattr(service, "build_runtime_audit_fields", lambda **_kwargs: {})
    row = service.canonical_guardrail_rule_record(
        {
            "guardrail_rule_id": "rule",
            "contract_id": "contract",
            "contract_version": 2,
            "environment_name": "dev",
            "guardrail_type": guardrail_type,
            "rule_id": "rule",
            "rule_type": "specific_rule",
            "rule_parameters_json": '{"threshold":1}',
            "action": action,
        },
        config=None,
        env="dev",
    )

    assert row["guardrail_type"] == guardrail_type
    assert row["action"] == action
    assert row["contract_id"] == "contract"
    assert row["contract_version"] == 2
