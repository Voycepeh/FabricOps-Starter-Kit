"""Warehouse type normalization tests for profile_table internals."""

from fabricops_kit.pipeline.profile_table import _warehouse_type_name


def test_warehouse_money_types_keep_decimal_precision_and_scale():
    """Treat Warehouse money types as numeric canonical decimal types."""
    assert _warehouse_type_name(
        {
            "DATA_TYPE": "money",
            "NUMERIC_PRECISION": 19,
            "NUMERIC_SCALE": 4,
        }
    ) == "decimal(19,4)"
    assert _warehouse_type_name(
        {
            "DATA_TYPE": "smallmoney",
            "NUMERIC_PRECISION": 10,
            "NUMERIC_SCALE": 4,
        }
    ) == "decimal(10,4)"
