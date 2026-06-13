from __future__ import annotations

import pytest

from fabricops_kit.data_profiling import profile_dataframe

pytestmark = [pytest.mark.unit, pytest.mark.spark]


def test_profile_dataframe_profiles_schema_nulls_distincts_min_and_max(spark_session):
    df = spark_session.createDataFrame(
        [(1, 10.0, "a", "skip"), (2, None, "b", "skip"), (3, 30.0, "b", "skip")],
        ["id", "amount", "category", "_pipeline_run_id"],
    )

    rows = {row["COLUMN_NAME"]: row.asDict() for row in profile_dataframe(df, "orders").collect()}

    assert set(rows) == {"id", "amount", "category"}
    assert rows["amount"]["TABLE_NAME"] == "orders"
    assert rows["amount"]["DATA_TYPE"] == "double"
    assert rows["amount"]["ROW_COUNT"] == 3
    assert rows["amount"]["NULL_COUNT"] == 1
    assert rows["amount"]["DISTINCT_COUNT"] == 2
    assert rows["amount"]["MIN_VALUE"] == "10.0"
    assert rows["amount"]["MAX_VALUE"] == "30.0"


def test_profile_dataframe_row_count_is_long_type(spark_session):
    df = spark_session.createDataFrame([(1, "a"), (2, "b")], ["id", "category"])

    profile = profile_dataframe(df, "orders")

    assert dict(profile.dtypes)["ROW_COUNT"] == "bigint"



def test_profile_dataframe_excludes_dq_technical_columns(spark_session):
    df = spark_session.createDataFrame(
        [
            {
                "order_id": "A",
                "amount": 10.0,
                "_dq_check_status": "warning",
                "_dq_failed_rules": "amount_positive",
            }
        ]
    )

    columns = {row["COLUMN_NAME"] for row in profile_dataframe(df, "orders").collect()}

    assert columns == {"order_id", "amount"}


def test_profile_dataframe_excludes_fabricops_and_dq_annotation_prefixes(spark_session):
    df = spark_session.createDataFrame(
        [(1, "ok", "warning", "rule", "run-1", "pipe")],
        "id int, status string, _dq_check_status string, _dq_failed_rules string, _fabricops_run_id string, _fabricops_pipeline_name string",
    )

    columns = {row["COLUMN_NAME"] for row in profile_dataframe(df, "orders").collect()}

    assert columns == {"id", "status"}
