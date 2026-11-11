"""Tests for deterministic internal table identity resolution."""

from importlib import import_module

import fabricops_kit

module = import_module("fabricops_kit.pipeline.resolve_table_id")


def test_resolve_table_id_uses_physical_identity_without_catalogue(monkeypatch):
    """Physical coordinates resolve before a target or contract exists."""
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(
        module,
        "resolve_physical_table_identity",
        lambda config, active_workspace_id, **coordinates: {
            "table_id": "lakehouse||unified||demo||orders",
            **coordinates,
        },
    )

    result = module.resolve_table_id(store="Silver", schema="demo", table_name="orders")

    assert result == "lakehouse||unified||demo||orders"
    assert "resolve_table_id" not in fabricops_kit.__all__
    assert not hasattr(fabricops_kit, "resolve_table_id")
