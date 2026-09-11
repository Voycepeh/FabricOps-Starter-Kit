"""Focused tests for normal governed physical source reads."""
# ruff: noqa: D103

from __future__ import annotations

import importlib

import pytest

from fabricops_kit.config import FabricStore


def test_lakehouse_reader_uses_resolved_delta_path(monkeypatch):
    owner = importlib.import_module("fabricops_kit.io.read_lakehouse_table")
    calls = []
    monkeypatch.setattr(
        owner,
        "resolve_configured_lakehouse_table",
        lambda *args, **kwargs: (object(), "orders", None, "resolved://orders"),
    )
    monkeypatch.setattr(owner, "get_spark_session", lambda spark: spark)
    monkeypatch.setattr(
        owner, "read_delta_path", lambda spark, path, *, options=None: calls.append((path, options)) or "frame"
    )

    assert owner.read_lakehouse_table("orders", spark_session=object(), versionAsOf=3) == "frame"
    assert calls == [("resolved://orders", {"versionAsOf": 3})]


def test_warehouse_reader_uses_resolved_object_name(monkeypatch):
    owner = importlib.import_module("fabricops_kit.io.read_warehouse_table")
    store = FabricStore(env="dev", workspace_id="w", item_id="i", name="warehouse", kind="warehouse")
    calls = []
    monkeypatch.setattr(
        owner,
        "resolve_configured_warehouse_table",
        lambda *args, **kwargs: (store, "dbo", "Bookings", "warehouse.dbo.Bookings"),
    )
    monkeypatch.setattr(owner, "get_spark_session", lambda spark: spark)
    monkeypatch.setattr(
        owner,
        "read_warehouse_synapsesql",
        lambda spark, resolved_store, target, *, options=None: calls.append((resolved_store, target, options)) or "frame",
    )

    assert owner.read_warehouse_table("dbo", "Bookings", spark_session=object(), timeout=30) == "frame"
    assert calls == [(store, "warehouse.dbo.Bookings", {"timeout": 30})]


def test_lakehouse_table_id_read_tags_dataframe_for_profile_safety(monkeypatch):
    owner = importlib.import_module("fabricops_kit.io.read_lakehouse_table")

    class Frame:
        pass

    frame = Frame()
    context_module = importlib.import_module("fabricops_kit.config.shared")
    shared_module = importlib.import_module("fabricops_kit.pipeline.shared")
    monkeypatch.setattr(context_module, "resolve_fabric_context", lambda **_kwargs: ("config", "dev", {}))
    monkeypatch.setattr(shared_module, "resolve_catalogue_table_identity", lambda *_args, **_kwargs: {
        "table_id": "source-id", "store_type": "lakehouse", "table_name": "orders",
        "target": "source", "schema": None,
    })
    monkeypatch.setattr(
        owner, "resolve_configured_lakehouse_table",
        lambda *args, **kwargs: (object(), "orders", None, "resolved://orders"),
    )
    monkeypatch.setattr(owner, "get_spark_session", lambda spark: spark)
    monkeypatch.setattr(owner, "read_delta_path", lambda *_args, **_kwargs: frame)

    result = owner.read_lakehouse_table(table_id="source-id", spark_session=object())

    assert result._fabricops_table_id == "source-id"


def test_source_read_apis_have_no_processing_scope():
    from inspect import signature
    from fabricops_kit import read_lakehouse_table, read_warehouse_table

    assert "processing_scope" not in signature(read_lakehouse_table).parameters
    assert "processing_scope" not in signature(read_warehouse_table).parameters
