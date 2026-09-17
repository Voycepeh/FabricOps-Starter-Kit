"""Tests for consistent write destination output."""

from importlib import import_module


class _Frame:
    write = object()


def test_lakehouse_and_warehouse_writers_print_consistent_destinations(monkeypatch, capsys):
    """Both public table writers should announce their resolved destination before writing."""
    lakehouse = import_module("fabricops_kit.io.write_lakehouse_table")
    warehouse = import_module("fabricops_kit.io.write_warehouse_table")
    frame = _Frame()

    monkeypatch.setattr(
        lakehouse,
        "resolve_configured_lakehouse_table",
        lambda *_args, **_kwargs: (object(), "products", "demo", "abfss://workspace/item/Tables/demo/products"),
    )
    monkeypatch.setattr(lakehouse, "write_delta_path", lambda *_args, **_kwargs: None)

    monkeypatch.setattr(
        warehouse,
        "resolve_configured_warehouse_table",
        lambda *_args, **_kwargs: (object(), "demo", "order_history", "Gold.demo.order_history"),
    )
    monkeypatch.setattr(warehouse, "write_warehouse_synapsesql", lambda *_args, **_kwargs: None)

    lakehouse.write_lakehouse_table(frame, "products", store="Bronze", schema="demo")
    warehouse.write_warehouse_table(frame, "demo", "order_history", store="Gold")

    assert capsys.readouterr().out.splitlines() == [
        "Writing Lakehouse table to abfss://workspace/item/Tables/demo/products",
        "Writing Warehouse table to Gold.demo.order_history",
    ]
