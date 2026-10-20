"""Timezone semantics at Python, Spark, and metadata boundaries."""

from datetime import UTC, datetime
from importlib import import_module
import os
import time
from types import SimpleNamespace

import pytest

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.shared import (
    get_audit_timezone,
    metadata_timestamp_sort_key,
    normalize_audit_datetime,
)
from fabricops_kit.pipeline import shared

reader = import_module("fabricops_kit.pipeline.pipeline_read")


@pytest.fixture(params=["UTC", "Asia/Singapore", "America/New_York"])
def zone(request, spark_session):
    """Restore session state after each timezone scenario."""
    previous = spark_session.conf.get("spark.sql.session.timeZone")
    spark_session.conf.set("spark.sql.session.timeZone", request.param)
    yield request.param
    spark_session.conf.set("spark.sql.session.timeZone", previous)


@pytest.mark.parametrize("kind", ["timestamp", "timestamp_ntz"])
def test_observation_scope_and_bounded_read_preserve_timestamp_semantics(spark_session, zone, kind, monkeypatch):
    """Bootstrap and checkpoints keep bounds, nulls, and native timestamp meaning."""
    from tests.unit.test_incremental_pipeline import Frame, _configure_scope, _row

    value = datetime(2026, 10, 7, 10, 30, tzinfo=UTC if kind == "timestamp" else None)
    later = value.replace(minute=31)
    frame = spark_session.createDataFrame([(None,), (value,)], f"modified_at {kind}")
    observed = shared._observe_dataframe(frame, "modified_at", "modified_at", watermark_only=True)
    expected = "2026-10-07T10:30:00.000000" + ("Z" if kind == "timestamp" else "")
    assert observed[0]["max_change_value"] == expected
    _configure_scope(monkeypatch, [])
    evidence = Frame([{**observed[0], "partition_column": "modified_at", "change_column": "modified_at"}])
    scope = shared.resolve_incremental_source_scope(source_table_id="source-orders", target_table_id="target-a", observation=evidence)
    future = spark_session.createDataFrame([(later,)], frame.schema)
    assert reader._filter_lakehouse_incremental(frame.union(future), scope).count() == 2
    _configure_scope(monkeypatch, [_row(target="target-a", maximum=expected)])
    next_observed = shared._observe_dataframe(future, "modified_at", "modified_at", watermark_only=True)
    scope = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-a",
        observation=Frame([{**next_observed[0], "partition_column": "modified_at", "change_column": "modified_at"}]),
    )
    assert reader._filter_lakehouse_incremental(frame.union(future), scope).count() == 1


def test_audit_write_and_read_keep_the_same_instant(spark_session, zone, tmp_path):
    """Audit overrides, target literals and physical Parquet round trips agree."""
    from pyspark.sql import functions as F

    runtime = dict(workspace_id="workspace", workspace_name="workspace", notebook_id="notebook",
                   notebook_name="notebook", activity_id="activity", user_name="user")
    audit = build_runtime_audit_fields(
        config={"audit_timezone": zone}, committed_at="2026-10-07T10:30:00+08:00",
        metadata_lakehouse_name="metadata", runtime_context=runtime,
    )
    assert audit["_committed_at"].tzinfo is not None
    assert audit["_committed_at"].astimezone(UTC) == datetime(2026, 10, 7, 2, 30, tzinfo=UTC)
    frame = shared.add_target_audit_fields(spark_session.range(1), audit)
    path = str(tmp_path / "audit")
    frame.write.parquet(path)
    restored = spark_session.read.parquet(path)
    assert restored.select(F.unix_micros("_committed_at")).first()[0] == 1791340200000000
    assert shared._max_column_value(restored, "_committed_at") == audit["_committed_at"]


def test_config_dict_and_object_use_the_same_timezone():
    """Mapping config does not silently fall back to UTC."""
    for config in [{"audit_timezone": "Asia/Singapore"}, SimpleNamespace(audit_timezone="Asia/Singapore")]:
        assert get_audit_timezone(config) == "Asia/Singapore"
        assert normalize_audit_datetime("2026-10-07T10:30:00", config).utcoffset().total_seconds() == 28800
        assert normalize_audit_datetime("2026-10-07T02:30:00Z", config).hour == 10


@pytest.mark.parametrize("value", ["2026-03-08T02:30:00", "2026-11-01T01:30:00"])
def test_ambiguous_or_nonexistent_audit_times_need_an_offset(value):
    """An offset is required when a local clock cannot identify one instant."""
    with pytest.raises(ValueError, match="daylight-saving"):
        normalize_audit_datetime(value, {"audit_timezone": "America/New_York"})


def test_freshness_compares_instants_and_uses_the_configured_clock(monkeypatch):
    """Equal instants with different offsets receive the same freshness result."""
    config = {"audit_timezone": "Asia/Singapore"}
    monkeypatch.setattr(shared, "get_current_audit_timestamp", lambda passed, **kw: "2026-10-07T10:30:00+08:00" if passed == config else pytest.fail("wrong clock"))
    for latest in ["2026-10-07T02:30:00Z", "2026-10-07T10:30:00+08:00", "2026-10-07T10:30:00"]:
        assert shared.freshness_check_core([{"modified": latest}], "modified", 0, config=config)["status"] == "passed"
    assert shared.freshness_check_core([{"modified": "2026-10-07T02:29:59Z"}], "modified", 0, config=config)["status"] == "failed"


def test_freshness_duration_across_daylight_saving_uses_elapsed_time():
    """A fall-back hour is elapsed time even when the wall clocks are equal."""
    rule = {"table_id": "orders", "guardrail_type": "freshness", "is_active": True,
            "rule_parameters_json": '{"freshness_column":"modified","maximum_age":30,"maximum_age_unit":"minutes"}'}
    result = shared.freshness_check_core(
        [{"modified": "2026-11-01T01:30:00-04:00"}], rules_df=[rule], table_id="orders",
        reference_date="2026-11-01T01:30:00-05:00", config={"audit_timezone": "America/New_York"},
    )
    assert result["status"] == "failed"


def test_metadata_selection_orders_offsets_by_instant():
    """Governance and widget selectors agree on the most recent record."""
    from fabricops_kit.data_contract.shared import _latest
    from fabricops_kit.widgets.widget_data_contract import _latest as widget_latest

    rows = [{"id": "one", "_committed_at": "2026-10-07T10:30:00+08:00", "value": "old"},
            {"id": "one", "_committed_at": "2026-10-07T03:00:00Z", "value": "new"}]
    assert _latest(rows, ("id",))[0]["value"] == "new"
    assert widget_latest(rows, "id")[0]["value"] == "new"
    assert metadata_timestamp_sort_key("2026-10-07T10:30:00+08:00") == metadata_timestamp_sort_key("2026-10-07T02:30:00Z")


def test_spark_collection_is_independent_of_python_process_timezone(spark_session, monkeypatch):
    """PySpark's naive collected datetimes are process-local, not always UTC."""
    original = os.environ.get("TZ")
    try:
        monkeypatch.setenv("TZ", "America/Los_Angeles")
        time.tzset()
        value = datetime(2026, 11, 1, 9, 30, tzinfo=UTC)
        frame = spark_session.createDataFrame([(value,)], "modified timestamp")
        rows = shared._observe_dataframe(frame, "modified", "modified", watermark_only=True)
        assert rows[0]["max_change_value"] == "2026-11-01T09:30:00.000000Z"
        assert shared._max_column_value(frame, "modified") == value
        assert metadata_timestamp_sort_key(frame.first()[0]) == metadata_timestamp_sort_key(value)
    finally:
        if original is None:
            os.environ.pop("TZ", None)
        else:
            os.environ["TZ"] = original
        time.tzset()


@pytest.mark.parametrize("sql", [
    "SELECT TOP 10 * FROM OPENROWSET(BULK 'https://example.invalid/orders.parquet') AS data",
    "SELECT * FROM dbo.orders OPTION (USE HINT('DISABLE_RESULT_SET_CACHE'))",
])
def test_read_only_fabric_sql_features_remain_accepted(sql):
    """Fabric external reads and result cache hints remain supported."""
    from fabricops_kit.io.shared import validate_select_query

    assert validate_select_query(sql) == sql


@pytest.mark.parametrize("sql", ["SELECT 1 USE other_database", "SELECT 1 BULK INSERT dbo.orders FROM 'file'", "SELECT 1 OPTION (USE HINT('safe')); DELETE FROM dbo.orders"])
def test_contextual_sql_keywords_do_not_allow_mutations(sql):
    """Keyword exceptions cannot admit another command or mutation."""
    from fabricops_kit.io.shared import validate_select_query

    with pytest.raises(ValueError):
        validate_select_query(sql)


def test_freshness_chooses_the_latest_instant_from_mixed_offsets():
    """Maximum ISO text is not necessarily the latest instant."""
    result = shared.freshness_check_core(
        [{"modified": "2026-10-07T10:30:00+08:00"}, {"modified": "2026-10-07T03:00:00Z"}],
        "modified", 0, reference_date="2026-10-07T03:00:00Z",
    )
    assert result["status"] == "passed"


def test_ntz_profile_retains_wall_clock_minimum_and_maximum(spark_session, zone):
    """Profiling NTZ timestamps does not lose bounds or apply session offsets."""
    frame = spark_session.createDataFrame(
        [(datetime(2026, 10, 7, 10, 30),), (datetime(2026, 10, 7, 11, 30),)], "modified timestamp_ntz"
    )
    profile = shared.build_profile_dataframe(frame).first()
    assert profile.MIN_VALUE == "2026-10-07 10:30:00"
    assert profile.MAX_VALUE == "2026-10-07 11:30:00"


def test_coverage_gate_uses_latest_instant_across_offsets():
    """An older success cannot override a newer blocking Guardrail result."""
    from fabricops_kit.pipeline.check_guardrail_coverage import _latest_can_continue
    rows = [{"status": "passed", "can_continue": True, "_committed_at": "2026-10-07T10:30:00+08:00"},
            {"status": "failed", "can_continue": False, "_committed_at": "2026-10-07T03:00:00Z"}]
    assert not _latest_can_continue(rows)


def test_warehouse_bounds_normalize_all_explicit_offsets():
    """Z, positive, and negative offsets express the same Warehouse instant."""
    for value in ["2026-10-07T02:30:00Z", "2026-10-07T10:30:00+08:00", "2026-10-06T22:30:00-04:00"]:
        assert reader._warehouse_watermark_literal(value) == "2026-10-07 02:30:00"


def test_profile_audit_uses_instant_type_even_with_ntz_session_default(spark_session, monkeypatch):
    """Metadata timestamp type must not depend on the business timestamp default."""
    profiler = import_module("fabricops_kit.pipeline.profile_table")
    previous = spark_session.conf.get("spark.sql.timestampType")
    audit = {"_committed_at": datetime(2026, 10, 7, 10, 30, tzinfo=UTC)}
    for name in ["_committed_by", "_workspace_id", "_workspace_name", "_notebook_id", "_notebook_name", "_metadata_lakehouse_name", "_activity_id"]:
        audit[name] = "value"
    monkeypatch.setattr(profiler, "build_runtime_audit_fields", lambda **kw: audit)
    try:
        spark_session.conf.set("spark.sql.timestampType", "TIMESTAMP_NTZ")
        columns = profiler._audit_literal_columns(config={}, env="dev", runtime_context={})
        frame = spark_session.range(1).select(columns["_committed_at"].alias("_committed_at"))
        assert frame.schema["_committed_at"].dataType.typeName() == "timestamp"
        assert shared._max_column_value(frame, "_committed_at") == audit["_committed_at"]
    finally:
        spark_session.conf.set("spark.sql.timestampType", previous)
