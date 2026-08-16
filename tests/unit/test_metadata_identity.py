"""Tests for stable Stage 2 table and column identities."""

from fabricops_kit.config.metadata_identity import _build_column_id, _build_table_id


def test_table_id_is_normalized_and_deterministic():
    """Logical table identity is stable across cosmetic input differences."""
    assert _build_table_id("Lakehouse", " Silver ", "DBO", " Orders ") == _build_table_id(
        "lakehouse", "silver", "dbo", "orders"
    )


def test_environment_is_not_part_of_table_id_contract():
    """The helper accepts only logical asset coordinates, not environment."""
    development = _build_table_id("lakehouse", "silver", "dbo", "orders")
    production = _build_table_id("lakehouse", "silver", "dbo", "orders")
    assert development == production


def test_column_id_is_stable_within_parent_table():
    """A column identity is derived from its stable parent table and name."""
    table_id = _build_table_id("lakehouse", "silver", "dbo", "orders")
    assert _build_column_id(table_id, "Order_ID") == _build_column_id(table_id, " order_id ")
    assert _build_column_id(table_id, "order_id") != _build_column_id(table_id, "amount")
