"""Tests for the table-specific PII token-map support writer."""
# ruff: noqa: D103

from __future__ import annotations

from importlib import import_module

import pytest

pytestmark = pytest.mark.unit

module = import_module("fabricops_kit.pipeline.write_pii_token_map")


def _patch_runtime(monkeypatch):
    identity = {
        "table_id": "lakehouse:unified:dbo:students",
        "table_name": "students",
        "schema": "dbo",
        "target": "unified",
        "store_type": "lakehouse",
    }
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: ("config", "dev", {"activity_id": "activity"}))
    monkeypatch.setattr(
        module,
        "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **_kwargs: identity if table_id == identity["table_id"] else pytest.fail(table_id),
    )
    monkeypatch.setattr(
        module,
        "resolve_configured_lakehouse_table",
        lambda target, table_name, schema, **_kwargs: (
            object(),
            table_name,
            schema or "fabricops_support",
            f"abfss://support/Tables/{schema or 'fabricops_support'}/{table_name}",
        ),
    )
    monkeypatch.setattr(
        module,
        "resolve_target_audit_fields",
        lambda _context: {
            "_committed_at": "2026-09-04T00:00:00Z",
            "_committed_by": "engineer",
            "_activity_id": "activity",
            "_workspace_id": "workspace",
            "_notebook_id": "notebook",
            "_notebook_name": "02_pipeline",
        },
    )
    return identity


def test_write_pii_token_map_writes_deduplicated_mapping(monkeypatch, spark_session):
    identity = _patch_runtime(monkeypatch)
    captured = {}
    monkeypatch.setattr(
        module,
        "_upsert_token_map",
        lambda frame, path: captured.update(frame=frame, path=path) or "created",
    )
    frame = spark_session.createDataFrame(
        [
            ("alice@example.com", "tok_alice"),
            ("alice@example.com", "tok_alice"),
            ("bob@example.com", "tok_bob"),
        ],
        ["email_address", "email_token"],
    )

    result = module.write_pii_token_map(
        frame,
        table_id=identity["table_id"],
        column_id="column-email",
        original_column="email_address",
        token_column="email_token",
        target="pii_support",
        schema="secure",
    )

    assert result["action"] == "created"
    assert result["target"] == "pii_support"
    assert result["schema"] == "secure"
    assert result["table_name"].startswith("students__")
    assert result["table_name"].endswith("__pii_token_map")
    assert captured["path"].endswith("/secure/" + result["table_name"])
    rows = captured["frame"].select(
        "table_id", "column_id", "original_value", "token_value", "original_data_type"
    ).orderBy("original_value").collect()
    assert [(row["original_value"], row["token_value"]) for row in rows] == [
        ("alice@example.com", "tok_alice"),
        ("bob@example.com", "tok_bob"),
    ]
    assert {row["table_id"] for row in rows} == {identity["table_id"]}
    assert {row["column_id"] for row in rows} == {"column-email"}
    assert {row["original_data_type"] for row in rows} == {"string"}
    assert "_activity_id" in captured["frame"].columns


def test_write_pii_token_map_rejects_missing_mapping_column(monkeypatch, spark_session):
    identity = _patch_runtime(monkeypatch)
    frame = spark_session.createDataFrame([("alice@example.com",)], ["email_address"])

    with pytest.raises(ValueError, match="email_token"):
        module.write_pii_token_map(
            frame,
            table_id=identity["table_id"],
            column_id="column-email",
            original_column="email_address",
            token_column="email_token",
        )


def test_write_pii_token_map_rejects_null_mapping_values(monkeypatch, spark_session):
    identity = _patch_runtime(monkeypatch)
    frame = spark_session.createDataFrame(
        [("alice@example.com", "tok_alice"), (None, "tok_missing")],
        "email_address string, email_token string",
    )

    with pytest.raises(ValueError, match="non-null"):
        module.write_pii_token_map(
            frame,
            table_id=identity["table_id"],
            column_id="column-email",
            original_column="email_address",
            token_column="email_token",
        )


def test_write_pii_token_map_requires_one_to_one_mapping(monkeypatch, spark_session):
    identity = _patch_runtime(monkeypatch)
    frame = spark_session.createDataFrame(
        [
            ("alice@example.com", "tok_a"),
            ("alice@example.com", "tok_b"),
        ],
        ["email_address", "email_token"],
    )

    with pytest.raises(ValueError, match="multiple token values"):
        module.write_pii_token_map(
            frame,
            table_id=identity["table_id"],
            column_id="column-email",
            original_column="email_address",
            token_column="email_token",
        )


def test_write_pii_token_map_requires_unique_tokens(monkeypatch, spark_session):
    identity = _patch_runtime(monkeypatch)
    frame = spark_session.createDataFrame(
        [
            ("alice@example.com", "tok_shared"),
            ("bob@example.com", "tok_shared"),
        ],
        ["email_address", "email_token"],
    )

    with pytest.raises(ValueError, match="multiple original values"):
        module.write_pii_token_map(
            frame,
            table_id=identity["table_id"],
            column_id="column-email",
            original_column="email_address",
            token_column="email_token",
        )


def test_token_map_table_name_is_stable_and_table_specific():
    first = module._token_map_table_name("lakehouse:unified:dbo:students", "students")
    second = module._token_map_table_name("lakehouse:other:dbo:students", "students")
    assert first == module._token_map_table_name("lakehouse:unified:dbo:students", "students")
    assert first != second
