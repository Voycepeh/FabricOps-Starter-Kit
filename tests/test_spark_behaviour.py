from __future__ import annotations

import json

import pytest

pytest.importorskip("pyspark")
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

from fabricops_kit.data_quality import _latest_dq_rule_versions, enforce_dq
from fabricops_kit import validate_schema
from fabricops_kit.metadata import build_metadata_column_key, build_metadata_table_key

pytestmark = pytest.mark.spark


def test_enforce_dq_preserves_schema_and_quarantines_nulls(spark_session):
    schema = StructType([
        StructField("id", IntegerType(), False),
        StructField("status", StringType(), True),
    ])
    df = spark_session.createDataFrame([(1, "ok"), (2, None)], schema=schema)
    rules = [
        {
            "rule_id": "status_not_null",
            "rule_type": "not_null",
            "columns": ["status"],
            "severity": "error",
            "description": "Status is required.",
        }
    ]

    result = enforce_dq(df, table_name="orders", rules=rules, row_id_columns=["id"], dq_run_id="dq-run")

    assert result.valid_rows.columns[-2:] == ["id", "status"]
    assert result.valid_rows.schema["id"].dataType == IntegerType()
    assert result.valid_rows.schema["status"].dataType == StringType()
    assert [row.id for row in result.valid_rows.orderBy("id").collect()] == [1]

    quarantine = result.quarantine_rows.orderBy("id").collect()
    assert [(row.id, row.dq_run_id) for row in quarantine] == [(2, "dq-run")]
    failures = result.failure_rows.orderBy("rule_id").collect()
    assert [(row.rule_id, row.failed_columns, row.dq_run_id) for row in failures] == [
        ("status_not_null", "status", "dq-run")
    ]


def test_latest_dq_rule_versions_use_deterministic_tie_breaker(spark_session):
    rule = {
        "rule_id": "status_not_null",
        "rule_type": "not_null",
        "columns": ["status"],
        "severity": "error",
        "description": "Status is required.",
    }
    rows = [
        {
            "table_name": "orders",
            "rule_key": "orders|status_not_null|not_null|status",
            "action_ts": "2026-06-05T00:00:00+00:00",
            "action_type": "approved",
            "action_by": "a",
            "rule_source": "widget",
            "rule_json": json.dumps(rule),
            "is_active": True,
        },
        {
            "table_name": "orders",
            "rule_key": "orders|status_not_null|not_null|status",
            "action_ts": "2026-06-05T00:00:00+00:00",
            "action_type": "deactivated",
            "action_by": "a",
            "rule_source": "widget",
            "rule_json": json.dumps({**rule, "description": "Deactivated"}),
            "is_active": False,
        },
    ]

    latest = _latest_dq_rule_versions(spark_session.createDataFrame(rows), "orders").collect()

    assert len(latest) == 1
    assert latest[0].action_type == "deactivated"


def test_validate_schema_detects_added_spark_column(spark_session):
    df = spark_session.createDataFrame(
        [(1, "ok")],
        schema="id int, status string",
    )

    result = validate_schema(
        df,
        {"id": "int"},
        preset="strict",
    )

    assert result["status"] == "failed"
    assert result["unexpected_columns"] == ["status"]


def test_metadata_hash_generation_is_deterministic():
    assert build_metadata_table_key("DEV", "Sales", "Orders") == build_metadata_table_key("dev", "sales", "orders")
    assert build_metadata_column_key("DEV", "Sales", "Orders", "OrderID") == build_metadata_column_key(
        "dev", "sales", "orders", "orderid"
    )
