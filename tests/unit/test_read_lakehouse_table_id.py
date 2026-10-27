"""Regression coverage for cached Lakehouse table identities during profiling."""

from importlib import import_module
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


@pytest.mark.parametrize("kind_field", ["store_type", "store_kind"])
def test_table_id_reader_resolves_catalogue_and_pipeline_cached_identifiers(monkeypatch, kind_field):
    """Scheduled profiling may receive either Catalogue or runtime identity shapes."""
    reader_module = import_module("fabricops_kit.io.read_lakehouse_table")
    shared = import_module("fabricops_kit.pipeline.shared")
    table_id = "orders-table-id"
    identity = {
        "table_id": table_id, "store": "Source", "schema": "demo",
        "table_name": "orders", kind_field: "lakehouse",
    }
    context = {"config": object(), "scope_workspace_id": "poc", "_pipeline_identities": {table_id: identity}}
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda **_kwargs: (context["config"], "poc", context))
    location = Mock(return_value=(object(), "orders", "demo", "abfss://test/orders"))
    monkeypatch.setattr(reader_module, "resolve_configured_lakehouse_table", location)
    session = object()
    monkeypatch.setattr(reader_module, "get_spark_session", lambda **_kwargs: session)
    read_delta = Mock(return_value=SimpleNamespace())
    monkeypatch.setattr(reader_module, "read_delta_path", read_delta)

    frame = reader_module.read_lakehouse_table(table_id=table_id, context=context)

    assert frame._fabricops_table_id == table_id
    location.assert_called_once_with("Source", "orders", "demo", context=context)
    read_delta.assert_called_once_with(session, "abfss://test/orders", options={})


@pytest.mark.parametrize("kind_field", ["store_type", "store_kind"])
def test_table_id_reader_still_rejects_non_lakehouse_tables(monkeypatch, kind_field):
    """Supporting runtime identity shape must not allow Warehouse Delta reads."""
    reader_module = import_module("fabricops_kit.io.read_lakehouse_table")
    shared = import_module("fabricops_kit.pipeline.shared")
    table_id = "warehouse-table-id"
    context = {
        "config": object(), "scope_workspace_id": "poc",
        "_pipeline_identities": {table_id: {
            "table_id": table_id, "store": "Gold", "schema": "demo",
            "table_name": "orders", kind_field: "warehouse",
        }},
    }
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda **_kwargs: (context["config"], "poc", context))

    with pytest.raises(ValueError, match="does not identify a Lakehouse table"):
        reader_module.read_lakehouse_table(table_id=table_id, context=context)
