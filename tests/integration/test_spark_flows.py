from __future__ import annotations

import pytest

from fabricops_kit.drift import validate_schema

pytestmark = pytest.mark.spark


def test_spark_schema_validation_allows_new_columns_in_monitoring_flow(spark_session):
    df = spark_session.createDataFrame([{"id": 1, "amount": 10.0, "extra": "new"}])
    schema_result = validate_schema(df, {"id": "bigint", "amount": "double"}, preset="allow_new_columns")

    assert schema_result["status"] == "warning"
    assert schema_result["can_continue"] is True
