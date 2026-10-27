"""Regression tests for target-aware incremental pipeline state."""
# ruff: noqa: D102, D103, D107

from __future__ import annotations

from datetime import UTC, datetime
from datetime import date as date_type
from importlib import import_module

import pytest

from fabricops_kit.pipeline import shared

read_module = import_module("fabricops_kit.pipeline.pipeline_read")


@pytest.fixture(autouse=True)
def resolved_reader_session(monkeypatch):
    """Provide a private session for tests with mocked physical readers."""
    session = object()
    monkeypatch.setattr(read_module, "get_spark_session", lambda *_args, **kwargs: session)


class Frame:
    """Small collectable test frame."""

    def __init__(self, rows=()):
        self.rows = list(rows)

    def collect(self):
        return self.rows


def _row(*, target: str, maximum: str, committed_at: int = 1):
    return {
        "observation_id": f"observation-{target}-{maximum}",
        "source_table_id": "source-orders",
        "target_table_id": target,
        "workspace_id": "dev",
        "partition_value": maximum,
        "row_count": 1,
        "min_change_value": maximum,
        "max_change_value": maximum,
        "content_fingerprint": f"hash-{maximum}",
        "is_present": True,
        "record_id": f"checkpoint-{target}-{maximum}",
        "record_type": "incremental_checkpoint", "status": "committed",
        "_committed_at": datetime(2026, 1, committed_at, tzinfo=UTC),
    }


def _receipt(target):
    return {"record_id": f"publication-{target}", "record_type": "publication_receipt", "status": "staged",
            "publication_id": f"publication-{target}", "publication_batch_id": "batch-a",
            "publication_activity_id": "run-a", "publication_at": datetime(2026, 1, 1, tzinfo=UTC),
            "publication_input_rows": 1, "publication_strategy": "append", "workspace_id": "dev",
            "target_table_id": target}


def _current(maximum: str):
    return Frame([{
        **_row(target="", maximum=maximum),
        "record_type": "source_observation", "status": "observed",
        "partition_column": "watermark",
        "change_column": "watermark",
    }])


def _configure_scope(monkeypatch, history):
    shared._PENDING_SOURCE_OBSERVATIONS.clear()
    shared._INCREMENTAL_SOURCE_SCOPES.clear()
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda context=None: (object(), "dev", {}))
    monkeypatch.setattr(
        shared,
        "build_runtime_audit_fields",
        lambda **kwargs: {"_activity_id": "run-1"},
    )
    monkeypatch.setattr(shared, "metadata_table_physical_schema", lambda *args: "engineering")
    monkeypatch.setattr(shared, "read_lakehouse_table", lambda *args, **kwargs: Frame(history))


def test_incremental_read_requires_target_before_context_resolution(monkeypatch):
    monkeypatch.setattr(
        read_module,
        "resolve_fabric_context",
        lambda: pytest.fail("target validation must happen before runtime access"),
    )
    with pytest.raises(ValueError, match="target_table_id is required"):
        read_module.pipeline_read(table_id="source-orders", read_mode="incremental")


def test_full_read_keeps_complete_read_contract(monkeypatch):
    identity = {
        "table_id": "source-orders",
        "store_type": "lakehouse",
        "store": "Bronze",
        "schema": "demo",
        "table_name": "orders",
    }
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(read_module, "resolve_catalogue_table_identity", lambda *args, **kwargs: identity)
    monkeypatch.setattr(read_module, "resolve_pipeline_data_contract", lambda *args, **kwargs: None)
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *args, **kwargs: "complete-frame")
    result = read_module.pipeline_read(table_id="source-orders", read_mode="full", verbose=False)
    assert result["dataframe"] == "complete-frame"
    assert result["read_mode"] == "full"
    assert result["should_process"] is True
    assert result["scope"] == {"type": "full", "first_run": False}


def test_incremental_pipeline_read_uses_processing_without_source_drift(monkeypatch):
    identity = {
        "table_id": "source-orders",
        "store_type": "lakehouse",
        "store": "Bronze",
        "schema": "demo",
        "table_name": "orders",
        "load_strategy": "append",
        "load_strategy_parameters_json": {'watermark_column': 'processed_at'},
    }
    captured = []
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(read_module, "resolve_catalogue_table_identity", lambda *a, **k: identity)
    monkeypatch.setattr(read_module, "resolve_pipeline_data_contract", lambda *a, **k: {"contract_payload": {"table": {"processing": {"load_strategy": "append", "watermark_column": "processed_at"}}}})
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **k: "complete-frame")
    monkeypatch.setattr(
        read_module,
        "capture_source_observation",
        lambda **kwargs: captured.append(kwargs) or "progress-observation",
    )
    monkeypatch.setattr(
        read_module,
        "resolve_incremental_source_scope",
        lambda **kwargs: {"type": "watermark", "first_run": False, "has_data": False},
    )
    monkeypatch.setattr(read_module, "_filter_lakehouse_incremental", lambda frame, scope: "empty-frame")

    result = read_module.pipeline_read(
        table_id="source-orders",
        read_mode="incremental",
        target_table_id="target-orders",
        verbose=False,
    )

    assert captured[0]["incremental_columns"] == ("processed_at", "processed_at")
    assert result["dataframe"] == "empty-frame"
    assert result["should_process"] is False


def test_first_incremental_run_bootstraps_with_complete_scope(monkeypatch):
    _configure_scope(monkeypatch, [])
    result = shared.resolve_incremental_source_scope(
        source_table_id="source-orders",
        target_table_id="target-a",
        observation=_current("120"),
    )
    assert result["type"] == "full"
    assert result["first_run"] is True
    assert result["has_data"] is True


def test_incremental_columns_come_from_processing_without_source_drift():
    identity = {
        "load_strategy": "append",
        "load_strategy_parameters_json": {'watermark_column': 'processed_at'},
    }

    assert shared.resolve_incremental_observation_columns(identity, None) == (
        "processed_at",
        "processed_at",
    )


def test_incremental_processing_column_can_differ_from_source_drift():
    contract = {
        "contract_payload": {
            "table": {
                "processing": {
                    "load_strategy": "append",
                    "watermark_column": "processed_at",
                }
            },
            "guardrails": [
                {
                    "guardrail_type": "source_drift",
                    "rule_parameters": {"change_column": "updated_at"},
                }
            ],
        }
    }

    assert shared.resolve_incremental_observation_columns({}, contract) == (
        "processed_at",
        "processed_at",
    )


def test_partition_only_incremental_processing_is_rejected():
    with pytest.raises(ValueError, match="unsupported fields: partition_column"):
        shared.validated_processing(
            {"load_strategy": "append", "partition_column": "business_date"}
        )


def test_incremental_observation_requires_governed_watermark():
    identity = {
        "load_strategy": "append",
        "load_strategy_parameters_json": {'partition_column': 'business_date'},
    }

    with pytest.raises(ValueError, match="requires a watermark_column or effective_column"):
        shared.resolve_incremental_observation_columns(identity, None)


def test_lakehouse_incremental_filter_is_strictly_after_watermark(spark_session):
    dataframe = spark_session.createDataFrame([(100,), (120,), (130,), (140,)], ["watermark"])

    result = read_module._filter_lakehouse_incremental(
        dataframe,
        {
            "type": "watermark",
            "first_run": False,
            "has_data": True,
            "column": "watermark",
            "after": "120",
            "through": "130",
        },
    )

    assert [row["watermark"] for row in result.collect()] == [130]


@pytest.mark.parametrize("timezone", ["UTC", "Asia/Singapore"])
def test_timestamp_observation_uses_utc_instant_for_scope_and_metadata_round_trip(
    spark_session, monkeypatch, timezone
):
    from pyspark.sql import functions as F

    spark_session.conf.set("spark.sql.session.timeZone", timezone)
    instant = datetime(2026, 10, 7, 2, 30, tzinfo=UTC)
    frame = spark_session.createDataFrame([(instant,)], ["modified_datetime"])
    compact = shared._observe_dataframe(frame, "modified_datetime", "modified_datetime")
    assert compact[0]["max_change_value"] == "2026-10-07T02:30:00.000000Z"
    assert compact[0]["partition_value"] == "2026-10-07T02:30:00.000000Z"

    _configure_scope(monkeypatch, [])
    current = Frame([{
        **_row(target="", maximum=compact[0]["max_change_value"]),
        "partition_value": compact[0]["partition_value"],
        "watermark_type": "timestamp",
        "partition_column": "modified_datetime",
        "change_column": "modified_datetime",
        "record_type": "source_observation", "status": "observed",
    }])
    result = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-a", observation=current
    )
    assert result["through"] == "2026-10-07T02:30:00.000000Z"

    filtered = read_module._filter_lakehouse_incremental(
        frame.withColumn("later", F.lit(1)),
        {"type": "watermark", "has_data": True, "column": "modified_datetime",
         "after": "2026-10-07T02:29:59.000000Z",
         "through": "2026-10-07T02:30:00.000000Z"},
    )
    assert filtered.count() == 1


def test_legacy_naive_timestamp_watermark_is_rejected_for_explicit_recovery(monkeypatch):
    _configure_scope(monkeypatch, [_row(target="target-a", maximum="2026-10-06 01:10:00")])
    current = Frame([{
        **_row(target="", maximum="2026-10-07T02:30:00.000000Z"),
        "partition_column": "modified_datetime",
        "change_column": "modified_datetime",
        "record_type": "source_observation", "status": "observed",
    }])
    with pytest.raises(ValueError, match="explicit type.*migrate"):
        shared.resolve_incremental_source_scope(
            source_table_id="source-orders", target_table_id="target-a", observation=current
        )


def test_numeric_date_and_string_compaction_keep_native_values():
    from datetime import date

    compact = shared._compact_rows(Frame([
        {"partition_value": date_type(2026, 10, 7), "row_count": 1,
         "min_change_value": 42, "max_change_value": 42, "content_fingerprint": "x"},
        {"partition_value": "2026-10-07", "row_count": 1,
         "min_change_value": "batch-b", "max_change_value": "batch-b", "content_fingerprint": "y"},
    ]))
    assert compact[0]["partition_value"] == "2026-10-07"
    assert compact[0]["max_change_value"] == "42"
    assert compact[1]["max_change_value"] == "batch-b"


def test_warehouse_incremental_query_pushes_strict_watermark_predicate():
    query = read_module._warehouse_incremental_query(
        {"schema": "demo", "table_name": "orders"},
        {
            "type": "watermark",
            "first_run": False,
            "has_data": True,
            "column": "modified_at",
            "after": "2026-09-02 10:00:00",
            "through": "2026-09-03 10:00:00",
        },
    )

    assert query == (
        "SELECT * FROM [demo].[orders] "
        "WHERE [modified_at] > '2026-09-02 10:00:00' "
        "AND [modified_at] <= '2026-09-03 10:00:00'"
    )


def test_warehouse_timestamp_predicate_uses_canonical_utc_instant():
    query = read_module._warehouse_incremental_query(
        {"schema": "demo", "table_name": "orders"},
        {"type": "watermark", "has_data": True, "column": "modified_at",
         "after": "2026-10-07T02:30:00.000000Z",
         "through": "2026-10-07T02:31:00.000000Z"},
    )
    assert query.endswith("WHERE [modified_at] > '2026-10-07 02:30:00' AND [modified_at] <= '2026-10-07 02:31:00'")


def test_warehouse_incremental_query_short_circuits_no_new_data():
    query = read_module._warehouse_incremental_query(
        {"schema": "demo", "table_name": "orders"},
        {
            "type": "watermark",
            "first_run": False,
            "has_data": False,
            "column": "modified_at",
            "after": "2026-09-02 10:00:00",
        },
    )

    assert query == "SELECT * FROM [demo].[orders] WHERE 1 = 0"


@pytest.mark.parametrize("bootstrap", [False, True])
def test_warehouse_arrivals_after_observation_wait_for_next_batch(bootstrap):
    """Execute the generated numeric predicates after a new row arrives."""
    import sqlite3

    identity = {"schema": "main", "table_name": "orders"}
    scope = {"type": "full" if bootstrap else "watermark", "has_data": True,
             "column": "watermark", "through": "200"}
    if not bootstrap:
        scope["after"] = "100"
    with sqlite3.connect(":memory:") as connection:
        connection.execute("CREATE TABLE orders (watermark INTEGER)")
        connection.executemany("INSERT INTO orders VALUES (?)", [(None,), (100,), (150,), (200,), (250,)])
        first = connection.execute(read_module._warehouse_incremental_query(identity, scope)).fetchall()
        second = connection.execute(read_module._warehouse_incremental_query(identity, {
            "type": "watermark", "has_data": True, "column": "watermark",
            "after": "200", "through": "250",
        })).fetchall()
    assert set(first) == ({(None,), (100,), (150,), (200,)} if bootstrap else {(150,), (200,)})
    assert second == [(250,)]
    assert not set(first).intersection(second)


@pytest.mark.parametrize("bootstrap", [False, True])
def test_lakehouse_arrivals_after_observation_wait_for_next_batch(spark_session, bootstrap):
    """Bootstrap and incremental scopes both respect their observed upper bound."""
    frame = spark_session.createDataFrame([(None,), (100,), (150,), (200,), (250,)], "watermark long")
    scope = {"type": "full" if bootstrap else "watermark", "has_data": True,
             "column": "watermark", "through": "200"}
    if not bootstrap:
        scope["after"] = "100"
    first = {row.watermark for row in read_module._filter_lakehouse_incremental(frame, scope).collect()}
    second = {row.watermark for row in read_module._filter_lakehouse_incremental(frame, {
        "type": "watermark", "has_data": True, "column": "watermark", "after": "200", "through": "250",
    }).collect()}
    assert first == ({None, 100, 150, 200} if bootstrap else {150, 200})
    assert second == {250}
    assert not first.intersection(second)


def test_null_only_bootstrap_does_not_consume_later_non_null_arrivals(spark_session):
    """No observed non-null maximum must not become an unbounded bootstrap."""
    scope = {"type": "full", "has_data": True, "column": "watermark", "through": None}
    frame = spark_session.createDataFrame([(None,), (100,)], "watermark long")
    assert [row.watermark for row in read_module._filter_lakehouse_incremental(frame, scope).collect()] == [None]
    sql = read_module._warehouse_incremental_query({"schema": "demo", "table_name": "orders"}, scope)
    assert sql.endswith("WHERE [watermark] IS NULL")


@pytest.mark.parametrize("timezone", ["UTC", "Asia/Singapore"])
def test_timestamp_upper_and_lower_bounds_are_utc_instants(spark_session, timezone):
    """A session timezone must not move either edge of the observed interval."""
    from datetime import timedelta

    previous_timezone = spark_session.conf.get("spark.sql.session.timeZone")
    try:
        spark_session.conf.set("spark.sql.session.timeZone", timezone)
        upper = datetime(2026, 10, 7, 2, 30, tzinfo=UTC)
        frame = spark_session.createDataFrame([
            (upper - timedelta(seconds=1),), (upper,), (upper + timedelta(seconds=1),),
        ], ["modified_at"])
        result = read_module._filter_lakehouse_incremental(frame, {
            "type": "watermark", "has_data": True, "column": "modified_at",
            "after": "2026-10-07T02:29:59.000000Z", "through": "2026-10-07T02:30:00.000000Z",
        })
        assert result.count() == 1
        assert result.first().modified_at == upper.replace(tzinfo=None)
    finally:
        spark_session.conf.set("spark.sql.session.timeZone", previous_timezone)


def test_same_source_resolves_isolated_target_watermarks(monkeypatch):
    _configure_scope(monkeypatch, [_row(target="target-a", maximum="120"), _row(target="target-b", maximum="100")])
    target_a = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-a", observation=_current("120")
    )
    target_b = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-b", observation=_current("120")
    )
    assert target_a["after"] == "120"
    assert target_a["has_data"] is False
    assert target_b["after"] == "100"
    assert target_b["through"] == "120"
    assert target_b["has_data"] is True


def test_next_activity_recovers_staged_progress_from_materialized_target(monkeypatch):
    """A new scheduled activity accepts durable prior evidence before scoping."""
    staged_a = {
        **_row(target="target-a", maximum="120"),
        "_activity_id": "run-a",
        "record_type": "incremental_checkpoint", "status": "staged",
        "publication_id": "publication-target-a",
    }
    staged_b = {
        **_row(target="target-b", maximum="90"),
        "_activity_id": "run-a",
        "record_type": "incremental_checkpoint", "status": "staged",
        "publication_id": "publication-target-b",
    }
    history = [staged_a, staged_b, _receipt("target-a"), _receipt("target-b")]
    _configure_scope(monkeypatch, history)
    monkeypatch.setattr(
        shared, "build_runtime_audit_fields", lambda **kwargs: {"_activity_id": "run-b"}
    )
    monkeypatch.setattr(
        shared,
        "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **_kwargs: {"table_id": table_id},
    )
    monkeypatch.setattr(
        shared,
        "_physical_target_has_publication",
        lambda identity, receipt, **_kwargs: identity["table_id"] == "target-a" and receipt["activity_id"] == "run-a",
    )
    merged = []
    monkeypatch.setattr(
        shared,
        "_merge_source_observation_records",
        lambda records, **_kwargs: merged.extend(records),
    )
    shared._PENDING_SOURCE_OBSERVATIONS.clear()
    shared._PENDING_SOURCE_DRIFT_OBSERVATIONS.clear()
    shared._INCREMENTAL_SOURCE_SCOPES.clear()

    scope_a = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-a", observation=_current("130")
    )
    scope_b = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-b", observation=_current("130")
    )

    assert scope_a["after"] == "120"
    assert scope_a["through"] == "130"
    assert scope_b["first_run"] is True
    assert {(row["target_table_id"], row["status"]) for row in merged} == {
        ("target-a", "committed")
    }


def test_numeric_watermarks_are_ordered_numerically(monkeypatch):
    _configure_scope(monkeypatch, [_row(target="target-a", maximum="9")])
    result = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-a", observation=_current("100")
    )
    assert result["has_data"] is True
    assert result["after"] == "9"
    assert result["through"] == "100"


def test_project_query_cannot_bypass_incremental_contract():
    with pytest.raises(ValueError, match="query cannot be combined"):
        read_module.pipeline_read(
            table_id="source-orders",
            query="SELECT * FROM dbo.orders",
            read_mode="incremental",
            target_table_id="target-a",
        )


def test_multiple_incremental_sources_are_staged_independently(monkeypatch):
    _configure_scope(monkeypatch, [])
    shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-a", observation=_current("120")
    )
    current_payments = Frame([
        {
            **_row(target="", maximum="55"),
            "source_table_id": "source-payments",
            "record_type": "source_observation", "status": "observed",
            "partition_column": "watermark",
            "change_column": "watermark",
        }
    ])
    shared.resolve_incremental_source_scope(
        source_table_id="source-payments", target_table_id="target-a", observation=current_payments
    )
    assert set(
        shared.incremental_publication_scopes(
            workspace_id="dev",
            activity_id="run-1",
            target_table_id="target-a",
            source_table_ids=["source-orders", "source-payments", "source-products"],
        ).keys()
    ) == {"source-orders", "source-payments"}


def test_incremental_read_parameters_override_missing_catalogue_watermark(monkeypatch):
    identity = {
        "table_id": "source-orders",
        "store_type": "lakehouse",
        "store": "Bronze",
        "schema": "demo",
        "table_name": "orders",
        "load_strategy": "append",
        "load_strategy_parameters_json": {},
    }
    captured = []
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(read_module, "resolve_catalogue_table_identity", lambda *a, **k: identity)
    monkeypatch.setattr(read_module, "resolve_pipeline_data_contract", lambda *a, **k: None)
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **k: "frame")
    monkeypatch.setattr(read_module, "capture_source_observation",
                        lambda **kwargs: captured.append(kwargs) or "observation")
    monkeypatch.setattr(read_module, "resolve_incremental_source_scope",
                        lambda **kwargs: {"type": "full", "first_run": True, "has_data": True})
    monkeypatch.setattr(read_module, "_filter_lakehouse_incremental", lambda frame, scope: frame)
    result = read_module.pipeline_read(
        table_id="source-orders",
        read_mode="incremental",
        read_parameters={"watermark_column": "modified_datetime"},
        target_table_id="target-orders",
        verbose=False,
    )
    assert captured[0]["incremental_columns"] == ("modified_datetime", "modified_datetime")
    assert result["should_process"] is True


def test_incremental_parameters_reject_selected_contract_conflict():
    contract = {"contract_payload": {"table": {"processing": {
        "load_strategy": "append", "watermark_column": "governed_date"
    }}}}
    with pytest.raises(ValueError, match="conflicts with selected Data Contract"):
        read_module._resolve_requested_incremental_columns(
            {}, contract, {"watermark_column": "another_date"}
        )


@pytest.mark.parametrize("parameters", [
    {"watermark_column": ""},
    {"watermark_column": 12},
    {"partition_column": "day"},
])
def test_incremental_parameters_reject_invalid_shape_before_runtime(monkeypatch, parameters):
    monkeypatch.setattr(read_module, "resolve_fabric_context",
                        lambda: pytest.fail("must reject before context resolution"))
    with pytest.raises(ValueError):
        read_module.pipeline_read(
            table_id="source-orders", target_table_id="target-orders",
            read_mode="incremental", read_parameters=parameters,
        )


def test_recovery_uses_validated_physical_target_without_catalogue(monkeypatch):
    """A staged successful target publication can recover without a contract."""
    history = [{
        **_row(target="target-a", maximum="120"),
        "_activity_id": "run-a",
        "record_type": "incremental_checkpoint", "status": "staged",
        "publication_id": "publication-target-a",
    }]
    history.append(_receipt("target-a"))
    _configure_scope(monkeypatch, history)
    identity = {
        "table_id": "target-a", "store": "Silver", "schema": "demo",
        "table_name": "inventory_movements", "store_kind": "lakehouse",
    }
    monkeypatch.setitem(shared._CURRENT_TABLE_IDENTITIES, "target-a", identity)
    monkeypatch.setattr(
        shared, "resolve_physical_table_identity", lambda *args, **kwargs: identity
    )
    monkeypatch.setattr(
        shared, "resolve_catalogue_table_identity",
        lambda *args, **kwargs: pytest.fail("target must not require Catalogue activation"),
    )
    monkeypatch.setattr(
        shared, "_physical_target_has_publication", lambda *args, **kwargs: True
    )
    merged = []
    monkeypatch.setattr(
        shared, "_merge_source_observation_records",
        lambda records, **kwargs: merged.extend(records),
    )
    scope = shared.resolve_incremental_source_scope(
        source_table_id="source-orders", target_table_id="target-a",
        observation=_current("130"),
    )
    assert scope["after"] == "120"
    assert scope["first_run"] is False
    assert [row["status"] for row in merged] == ["committed", "committed"]


def test_legacy_activity_only_staging_is_never_automatically_recovered(monkeypatch):
    """An old activity marker cannot attest any particular staged source state."""
    history = [{**_row(target='target-a', maximum='120'),
                'observation_status': 'observed', '_activity_id': 'reused-activity'}]
    _configure_scope(monkeypatch, history)
    monkeypatch.setattr(shared, 'resolve_catalogue_table_identity', lambda *a, **kw: {'table_id': 'target-a'})
    monkeypatch.setattr(shared, '_physical_target_has_publication', lambda *a, **kw: pytest.fail('legacy evidence has no batch proof'))
    monkeypatch.setattr(shared, '_merge_source_observation_records', lambda records, **kw: None)
    with pytest.raises(RuntimeError, match="Unsupported legacy"):
        shared.resolve_incremental_source_scope(source_table_id='source-orders', target_table_id='target-a', observation=_current('130'))


def test_newer_pending_read_is_rejected_without_replacing_checkpoint(monkeypatch):
    _configure_scope(monkeypatch, [])
    key = ('dev', 'run-1', 'source-orders', 'target-a')
    shared.resolve_incremental_source_scope(source_table_id='source-orders', target_table_id='target-a', observation=_current('12'))
    pending = shared._PENDING_SOURCE_OBSERVATIONS[key]
    with pytest.raises(RuntimeError, match='already awaiting publication'):
        shared.resolve_incremental_source_scope(source_table_id='source-orders', target_table_id='target-a', observation=_current('16'))
    assert shared._PENDING_SOURCE_OBSERVATIONS[key] == pending
    assert shared._INCREMENTAL_SOURCE_SCOPES[key]['through'] == '12'
    # Re-reading the same state is unambiguous and remains supported.
    shared.resolve_incremental_source_scope(source_table_id='source-orders', target_table_id='target-a', observation=_current('12'))


def test_read_during_write_cannot_be_replaced_by_a_third_read(monkeypatch):
    _configure_scope(monkeypatch, [])
    key = ('dev', 'run-1', 'source-orders', 'target-a')
    shared.resolve_incremental_source_scope(source_table_id='source-orders', target_table_id='target-a', observation=_current('12'))
    monkeypatch.setitem(shared._ACTIVE_PUBLICATION_SOURCES, key, list(shared._PENDING_SOURCE_OBSERVATIONS[key]))
    shared.resolve_incremental_source_scope(source_table_id='source-orders', target_table_id='target-a', observation=_current('16'))
    with pytest.raises(RuntimeError, match='already awaiting publication'):
        shared.resolve_incremental_source_scope(source_table_id='source-orders', target_table_id='target-a', observation=_current('20'))
    assert shared._INCREMENTAL_SOURCE_SCOPES[key]['through'] == '16'


def test_empty_scope_does_not_block_new_data(monkeypatch):
    _configure_scope(monkeypatch, [_row(target='target-a', maximum='12')])
    shared.resolve_incremental_source_scope(source_table_id='source-orders', target_table_id='target-a', observation=_current('12'))
    next_scope = shared.resolve_incremental_source_scope(source_table_id='source-orders', target_table_id='target-a', observation=_current('16'))
    assert next_scope['has_data']
    assert next_scope['after'] == '12'
    assert next_scope['through'] == '16'


def test_recovered_pending_state_does_not_block_new_data(monkeypatch):
    history = []
    _configure_scope(monkeypatch, history)
    shared.resolve_incremental_source_scope(source_table_id='source-orders', target_table_id='target-a', observation=_current('12'))
    # Recovery or finalization accepted this pending state before the next Read.
    history.append({**_row(target='target-a', maximum='12'), 'partition_column': 'watermark', 'change_column': 'watermark'})
    scope = shared.resolve_incremental_source_scope(source_table_id='source-orders', target_table_id='target-a', observation=_current('16'))
    assert scope['after'] == '12'
    assert scope['through'] == '16'


@pytest.mark.parametrize("field,value", [("change_column", "different_column"), ("watermark_type", "timestamp_ntz")])
def test_pending_read_cannot_change_watermark_meaning_at_same_bounds(monkeypatch, field, value):
    _configure_scope(monkeypatch, [])
    key = ("dev", "run-1", "source-orders", "target-a")
    pending = shared.observation_rows(_current("12"))
    shared._PENDING_SOURCE_OBSERVATIONS[key] = pending
    with pytest.raises(RuntimeError, match="already awaiting publication"):
        shared._ensure_unambiguous_source_observation(key, [{**pending[0], field: value}])
    assert shared._PENDING_SOURCE_OBSERVATIONS[key] == pending
