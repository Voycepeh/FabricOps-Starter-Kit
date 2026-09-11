"""Tests for deterministic public table identity resolution."""

from importlib import import_module

import fabricops_kit

module = import_module("fabricops_kit.pipeline.resolve_table_id")


def test_resolve_table_id_uses_physical_identity_without_catalogue(monkeypatch):
    """Physical coordinates resolve before a target or contract exists."""
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(
        module,
        "resolve_physical_table_identity",
        lambda config, env, **coordinates: {
            "table_id": "lakehouse||unified||demo||orders",
            **coordinates,
        },
    )

    result = module.resolve_table_id(target="unified", schema="demo", table_name="orders")

    assert result == "lakehouse||unified||demo||orders"
    assert fabricops_kit.resolve_table_id is module.resolve_table_id
