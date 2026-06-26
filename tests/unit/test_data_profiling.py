"""Test FabricOps behavior and reference contracts."""

from __future__ import annotations

import pytest

from fabricops_kit.data_profiling import profile_dataframe

pytestmark = [pytest.mark.unit, pytest.mark.spark]


def test_profile_dataframe_profiles_schema_nulls_distincts_min_and_max(spark_session):
    """Verify profile dataframe profiles schema nulls distincts min and max."""
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
    """Verify profile dataframe row count is long type."""
    df = spark_session.createDataFrame([(1, "a"), (2, "b")], ["id", "category"])

    profile = profile_dataframe(df, "orders")

    assert dict(profile.dtypes)["ROW_COUNT"] == "bigint"



def test_profile_dataframe_excludes_dq_technical_columns(spark_session):
    """Verify profile dataframe excludes dq technical columns."""
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
    """Verify profile dataframe excludes fabricops and dq annotation prefixes."""
    df = spark_session.createDataFrame(
        [(1, "ok", "warning", "rule", "run-1", "pipe")],
        "id int, status string, _dq_check_status string, _dq_failed_rules string, _fabricops_run_id string, _fabricops_pipeline_name string",
    )

    columns = {row["COLUMN_NAME"] for row in profile_dataframe(df, "orders").collect()}

    assert columns == {"id", "status"}


def test_profile_dataframe_public_import_and_signature_are_stable():
    """Verify profile dataframe root import and public signature remain stable."""
    import inspect

    from fabricops_kit import profile_dataframe as root_profile_dataframe

    assert root_profile_dataframe is profile_dataframe
    assert str(inspect.signature(profile_dataframe)) == "(df, table_name: 'str', *, exclude_columns=None, run_timestamp_timezone: 'str | None' = None, config: 'Any' = None, include_distributions: 'bool' = False, distribution_columns: 'list[str] | set[str] | tuple[str, ...] | None' = None, distribution_bin_edges: 'dict[str, list[float]] | None' = None, categorical_categories: 'dict[str, list[str]] | None' = None, categorical_top_n: 'int' = 20)"


def test_profile_dataframe_numeric_distribution_behavior(spark_session):
    """Verify numeric profiling distribution output."""
    import json

    df = spark_session.createDataFrame([(1, 5.0), (2, 15.0), (3, 25.0)], ["id", "amount"])

    rows = {row["COLUMN_NAME"]: row.asDict() for row in profile_dataframe(
        df,
        "orders",
        include_distributions=True,
        distribution_columns=["amount"],
        distribution_bin_edges={"amount": [0.0, 10.0, 20.0, 30.0]},
    ).collect()}

    assert rows["amount"]["DISTRIBUTION_TYPE"] == "numeric"
    assert json.loads(rows["amount"]["DISTRIBUTION_JSON"]) == {"bin_edges": [0.0, 10.0, 20.0, 30.0], "bin_counts": [1, 1, 1]}
    assert rows["id"]["DISTRIBUTION_TYPE"] is None


def test_profile_dataframe_categorical_distribution_behavior(spark_session):
    """Verify categorical profiling distribution output."""
    import json

    df = spark_session.createDataFrame([("open",), ("open",), ("closed",), ("new",)], ["status"])

    row = profile_dataframe(
        df,
        "orders",
        include_distributions=True,
        categorical_categories={"status": ["open", "closed"]},
    ).collect()[0].asDict()

    assert row["DISTRIBUTION_TYPE"] == "categorical"
    assert json.loads(row["DISTRIBUTION_JSON"]) == {
        "category_counts": {"closed": 1, "open": 2},
        "new_categories": ["new"],
        "other_count": 1,
    }


def test_profile_dataframe_selected_columns_behavior(spark_session):
    """Verify explicit excluded columns are not profiled."""
    df = spark_session.createDataFrame([(1, 10.0, "open")], ["id", "amount", "status"])

    columns = {row["COLUMN_NAME"] for row in profile_dataframe(df, "orders", exclude_columns=["id"]).collect()}

    assert columns == {"amount", "status"}


def test_profile_dataframe_min_max_supported_type_behavior(spark_session):
    """Verify unsupported complex types omit min and max values."""
    from fabricops_kit.data_profiling.shared import is_min_max_supported_type

    assert is_min_max_supported_type("string") is True
    assert is_min_max_supported_type("array<string>") is False

    df = spark_session.createDataFrame([(["a"],), (["b"],)], "tags array<string>")

    row = profile_dataframe(df, "orders").collect()[0].asDict()

    assert row["MIN_VALUE"] is None
    assert row["MAX_VALUE"] is None


def test_profile_dataframe_audit_timestamp_timezone_behavior(spark_session):
    """Verify audit timezone validation and timestamp expression behavior."""
    from types import SimpleNamespace

    from fabricops_kit.config import get_audit_timezone

    assert get_audit_timezone(SimpleNamespace(audit_timezone="UTC")) == "UTC"

    df = spark_session.createDataFrame([(1,)], ["id"])
    row = profile_dataframe(df, "orders", run_timestamp_timezone="UTC").collect()[0]

    assert row["RUN_TIMESTAMP"] is not None
    with pytest.raises(ValueError, match="Invalid FABRICOPS_AUDIT_TIMEZONE"):
        profile_dataframe(df, "orders", run_timestamp_timezone="NotATimezone").collect()


def test_profile_dataframe_empty_column_behavior_raises(spark_session):
    """Verify all-technical DataFrames raise the supported empty-profile error."""
    df = spark_session.createDataFrame([("run-1", "ok")], ["_pipeline_run_id", "_dq_check_status"])

    with pytest.raises(ValueError, match="No eligible non-technical columns"):
        profile_dataframe(df, "orders")


def test_profile_dataframe_package_import():
    """Verify package-level public import works after module migration."""
    from fabricops_kit.data_profiling import profile_dataframe as package_profile_dataframe

    assert package_profile_dataframe is profile_dataframe
