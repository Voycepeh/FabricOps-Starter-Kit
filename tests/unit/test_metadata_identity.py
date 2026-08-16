"""Tests for internal stable Stage 2 table and column identity helpers."""

from fabricops_kit.config.shared import build_column_id, build_table_id


def test_table_id_is_normalized_and_deterministic():
    """Logical table identity is stable across cosmetic input differences."""
    assert build_table_id("Lakehouse", " Silver ", "DBO", " Orders ") == build_table_id(
        "lakehouse", "silver", "dbo", "orders"
    )


def test_environment_is_not_part_of_table_id_contract():
    """The helper accepts only logical asset coordinates, not environment."""
    development = build_table_id("lakehouse", "silver", "dbo", "orders")
    production = build_table_id("lakehouse", "silver", "dbo", "orders")

    assert development == production


def test_column_id_is_stable_within_table_identity():
    """Column identity derives from table identity plus normalized column name."""
    table_id = build_table_id("warehouse", "product", "dbo", "student")

    assert build_column_id(table_id, " Student_ID ") == build_column_id(table_id, "student_id")
    assert build_column_id(table_id, "student_id") != build_column_id(table_id, "programme")
