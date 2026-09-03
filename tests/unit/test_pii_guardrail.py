"""Focused tests for Direct PII enforcement and protected token-vault behaviour."""
# ruff: noqa: D103

from __future__ import annotations

import json
from importlib import import_module
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.unit

check_module = import_module("fabricops_kit.pipeline.check_pii_guardrail")
security = import_module("fabricops_kit.security.shared")
write_module = import_module("fabricops_kit.pipeline.write_pipeline_prep")


def _direct(column_id: str = "column-email", column_name: str = "email") -> list[dict[str, str]]:
    return [{"column_id": column_id, "column_name": column_name}]


def test_no_direct_pii_classification_passes(spark_session):
    frame = spark_session.createDataFrame([("raw@example.test",)], ["email"])
    result = security.pii_guardrail_core(frame, direct_pii_columns=[], vault_rows=[])
    assert result["status"] == "passed"
    assert result["can_continue"] is True


def test_absent_direct_pii_column_passes(spark_session):
    frame = spark_session.createDataFrame([(1,)], ["customer_id"])
    result = security.pii_guardrail_core(frame, direct_pii_columns=_direct(), vault_rows=[])
    assert result["status"] == "passed"
    assert result["present_columns"] == []


def test_raw_direct_pii_blocks_but_approved_token_passes(spark_session):
    raw = spark_session.createDataFrame([("raw@example.test",)], ["email"])
    failed = security.pii_guardrail_core(raw, direct_pii_columns=_direct(), vault_rows=[])
    assert failed["status"] == "failed"
    assert failed["can_continue"] is False
    assert failed["untreated_columns"] == ["email"]

    tokenised = spark_session.createDataFrame([("fo_pii_v1_token",)], ["email"])
    passed = security.pii_guardrail_core(
        tokenised,
        direct_pii_columns=_direct(),
        vault_rows=[{
            "table_id": "table-a",
            "column_id": "column-email",
            "token": "fo_pii_v1_token",
            "original_value": "raw@example.test",
        }],
    )
    assert passed["status"] == "passed"


def test_warning_rule_uses_existing_continuation_semantics(spark_session):
    frame = spark_session.createDataFrame([("raw@example.test",)], ["email"])
    result = security.pii_guardrail_core(
        frame, direct_pii_columns=_direct(), vault_rows=[], severity="warning",
    )
    assert result["status"] == "warning"
    assert result["can_continue"] is True


def test_tokenisation_reuses_duplicates_preserves_null_and_isolates_columns_and_tables(
    monkeypatch, spark_session,
):
    vault: dict[str, list[dict]] = {}
    monkeypatch.setattr(security, "get_store", lambda *_args: SimpleNamespace(kind="lakehouse"))
    monkeypatch.setattr(security, "configured_lakehouse_schema", lambda *_args: "vault")
    monkeypatch.setattr(
        security,
        "build_runtime_audit_fields",
        lambda **_kwargs: {"_activity_id": "activity", "_committed_at": "now"},
    )

    def read_vault(table_name, **_kwargs):
        if table_name not in vault:
            raise RuntimeError("table not found")
        return spark_session.createDataFrame(vault[table_name])

    def write_vault(frame, table_name, **_kwargs):
        vault.setdefault(table_name, []).extend(row.asDict() for row in frame.collect())

    monkeypatch.setattr(security, "read_lakehouse_table_core", read_vault)
    monkeypatch.setattr(security, "write_lakehouse_table_core", write_vault)
    monkeypatch.setattr(security, "is_table_not_found_error", lambda exc: "not found" in str(exc))

    source = spark_session.createDataFrame(
        [("same@example.test", "same@example.test"), ("same@example.test", None)],
        ["email", "alternate_email"],
    )
    first = security.tokenise_direct_pii(
        source,
        config="config",
        env="dev",
        table_id="table-a",
        columns=_direct() + _direct("column-alt", "alternate_email"),
        spark_session=spark_session,
    )
    rows = first.collect()
    assert rows[0]["email"] == rows[1]["email"]
    assert rows[1]["alternate_email"] is None
    assert rows[0]["email"] != rows[0]["alternate_email"]
    assert "same@example.test" not in json.dumps([row.asDict() for row in rows])
    assert len(vault[security.token_vault_table_name("table-a")]) == 2

    replay = security.tokenise_direct_pii(
        source.select("email"),
        config="config",
        env="dev",
        table_id="table-a",
        columns=_direct(),
        spark_session=spark_session,
    )
    assert replay.first()["email"] == rows[0]["email"]
    assert len(vault[security.token_vault_table_name("table-a")]) == 2

    other = security.tokenise_direct_pii(
        source.select("email"),
        config="config",
        env="dev",
        table_id="table-b",
        columns=_direct(),
        spark_session=spark_session,
    )
    assert other.first()["email"] != rows[0]["email"]
    assert security.token_vault_table_name("table-a") != security.token_vault_table_name("table-b")


def test_production_resolves_frozen_contract_enrichment(monkeypatch):
    frozen = {
        "contract_payload": {
            "enrichment": {"columns": [{
                "column_id": "column-email",
                "enrichment_type": "personal_identifier",
                "value": "direct PII",
            }]},
            "table": {"columns": [{"column_id": "column-email", "column_name": "email"}]},
        }
    }
    monkeypatch.setattr(security, "resolve_active_data_contract", lambda *_args, **_kwargs: frozen)
    monkeypatch.setattr(
        security,
        "read_lakehouse_table_core",
        lambda *_args, **_kwargs: pytest.fail("Production must not read mutable METADATA_ENRICHMENT"),
    )
    assert security.resolve_direct_pii_columns(
        "config", "prod", "table-a", spark_session=SimpleNamespace(),
    ) == _direct()


def test_write_preparation_tokenises_before_audit(monkeypatch, spark_session):
    identity = {
        "table_id": "lakehouse:unified:dbo:customers",
        "store_type": "lakehouse",
        "target": "unified",
        "schema": "dbo",
        "table_name": "customers",
        "load_strategy": "overwrite",
        "load_strategy_parameters_json": "{}",
    }
    monkeypatch.setattr(write_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(write_module, "resolve_catalogue_table_identity", lambda *_args, **_kwargs: identity)
    monkeypatch.setattr(write_module, "catalogue_authored_processing", lambda _value: {"load_strategy": "overwrite"})
    monkeypatch.setattr(write_module, "resolve_table_processing_definition", lambda *_args, **_kwargs: {"load_strategy": "overwrite"})
    monkeypatch.setattr(write_module, "resolve_direct_pii_columns", lambda *_args, **_kwargs: _direct())
    monkeypatch.setattr(
        write_module,
        "tokenise_direct_pii",
        lambda frame, **_kwargs: frame.withColumn(
            "email", __import__("pyspark.sql.functions", fromlist=["concat"]).concat(
                frame["email"],
                __import__("pyspark.sql.functions", fromlist=["lit"]).lit("-token"),
            ),
        ),
    )
    monkeypatch.setattr(write_module, "resolve_target_audit_fields", lambda _context: {"_activity_id": "activity"})
    monkeypatch.setattr(write_module, "add_target_audit_fields", lambda frame, _audit: frame)
    monkeypatch.setattr(write_module, "persist_lineage_participation", lambda **_kwargs: None)
    source = spark_session.createDataFrame([("raw",)], ["email"])
    result = write_module.write_pipeline_prep(
        source,
        target_table_id=identity["table_id"],
        source_preps=[{"read_mode": "full_dataset", "scope": {"type": "full_dataset"}}],
    )
    assert result["df"].first()["email"] == "raw-token"


def test_public_guardrail_persists_existing_rule_result(monkeypatch, spark_session):
    identity = {
        "table_id": "lakehouse:source:dbo:customers",
        "store_type": "lakehouse",
        "target": "source",
        "schema": "dbo",
        "table_name": "customers",
    }
    monkeypatch.setattr(check_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(check_module, "get_spark_session", lambda: spark_session)
    monkeypatch.setattr(check_module, "resolve_catalogue_table_identity", lambda *_args, **_kwargs: identity)
    monkeypatch.setattr(check_module, "get_store", lambda *_args: SimpleNamespace(kind="lakehouse", schema="dbo"))
    monkeypatch.setattr(check_module, "resolve_lakehouse_table_location", lambda *_args: ("customers", "dbo", "path"))
    monkeypatch.setattr(check_module, "resolve_direct_pii_columns", lambda *_args, **_kwargs: _direct())
    monkeypatch.setattr(check_module, "load_table_guardrail_rules", lambda *_args, **_kwargs: ["rule"])
    monkeypatch.setattr(check_module, "select_table_guardrail_rule", lambda *_args, **_kwargs: {
        "guardrail_rule_id": "pii-rule", "guardrail_version": 2,
        "severity": "warning", "rule_type": "direct_pii_tokenised",
    })
    monkeypatch.setattr(check_module, "load_token_vault_rows", lambda *_args, **_kwargs: [])
    persisted = []
    monkeypatch.setattr(check_module, "write_guardrail_result_row", lambda **kwargs: persisted.append(kwargs))
    frame = spark_session.createDataFrame([("raw@example.test",)], ["email"])
    result = check_module.check_pii_guardrail(identity["table_id"], dataframe=frame)
    assert result["status"] == "warning"
    assert persisted[0]["guardrail_type"] == "pii"
    assert persisted[0]["result"]["guardrail_rule_id"] == "pii-rule"
