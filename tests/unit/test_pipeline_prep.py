"""Tests for the public pipeline preparation boundary."""
# ruff: noqa: D103

from __future__ import annotations

from importlib import import_module
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.unit

read_module = import_module("fabricops_kit.pipeline.read_pipeline_prep")
shared_module = import_module("fabricops_kit.pipeline.shared")
warehouse_writer = import_module("fabricops_kit.io.write_warehouse_table")
write_module = import_module("fabricops_kit.pipeline.write_pipeline_prep")
lakehouse_writer = import_module("fabricops_kit.io.write_lakehouse_table")


def _identity(table_id="warehouse:source:dbo:student_source", *, store_type="warehouse"):
    return {
        "table_id": table_id,
        "store_type": store_type,
        "target": "source" if ":source:" in table_id else "unified",
        "schema": "dbo",
        "table_name": table_id.rsplit(":", 1)[-1],
        "load_strategy": "overwrite",
        "load_strategy_parameters_json": "{}",
    }


def _patch_source_identity(monkeypatch, identity=None):
    resolved = identity or _identity()
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(
        read_module,
        "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **_kwargs: resolved if table_id == resolved["table_id"] else pytest.fail(table_id),
    )
    monkeypatch.setattr(read_module, "persist_lineage_participation", lambda **_kwargs: "lineage-id")
    return resolved


def _patch_target_processing(monkeypatch, processing, *, store_type="lakehouse"):
    identity = _identity("lakehouse:unified:dbo:students", store_type=store_type)
    monkeypatch.setattr(write_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(write_module, "resolve_catalogue_table_identity", lambda *_args, **_kwargs: identity)
    monkeypatch.setattr(write_module, "catalogue_authored_processing", lambda value: {"load_strategy": value["load_strategy"]})
    monkeypatch.setattr(write_module, "resolve_table_processing_definition", lambda *_args, **_kwargs: processing)
    monkeypatch.setattr(write_module, "persist_lineage_participation", lambda **_kwargs: "lineage-id")
    monkeypatch.setattr(write_module, "resolve_direct_pii_columns", lambda *_args, **_kwargs: [])
    monkeypatch.setattr(write_module, "tokenise_direct_pii", lambda dataframe, **_kwargs: dataframe)
    monkeypatch.setattr(write_module, "resolve_target_audit_fields", lambda _context: {
        "_committed_at": "2026-08-22T00:00:00Z", "_committed_by": "engineer",
        "_activity_id": "activity", "_workspace_id": "workspace",
        "_notebook_id": "notebook", "_notebook_name": "02_pipeline",
    })
    return identity


def test_full_dataset_source_can_prepare_before_any_target_exists(monkeypatch):
    identity = _patch_source_identity(monkeypatch)
    lineage = []
    monkeypatch.setattr(read_module, "persist_lineage_participation", lambda **kwargs: lineage.append(kwargs))
    monkeypatch.setattr(read_module, "_observe_table_core", lambda *_args, **_kwargs: pytest.fail("observation"))
    monkeypatch.setattr(read_module, "_target_watermark", lambda *_args, **_kwargs: pytest.fail("checkpoint"))

    result = read_module.read_pipeline_prep(
        source_table_id=identity["table_id"],
        source_read_strategy="full_dataset",
    )

    assert result["source"]["table_id"] == identity["table_id"]
    assert result["source_processing"] == {"read_strategy": "full_dataset"}
    assert result["read_mode"] == "full_dataset"
    assert result["scope"] == {"type": "full_dataset"}
    assert "target" not in result
    assert "processing" not in result
    assert lineage == [{"table_id": identity["table_id"], "pipeline_role": "source", "context": {}}]


def test_read_prep_requires_source_table_id():
    with pytest.raises(TypeError, match="source_table_id"):
        read_module.read_pipeline_prep(source_read_strategy="full_dataset")


def test_read_prep_rejects_unknown_source_table_id(monkeypatch):
    lineage = []
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(
        read_module,
        "resolve_catalogue_table_identity",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(ValueError("No active registered Catalogue table")),
    )
    monkeypatch.setattr(read_module, "persist_lineage_participation", lambda **kwargs: lineage.append(kwargs))
    with pytest.raises(ValueError, match="No active registered Catalogue table"):
        read_module.read_pipeline_prep(source_table_id="wrong", source_read_strategy="full_dataset")
    assert lineage == []


def test_two_registered_sources_share_activity_lineage_context(monkeypatch):
    lineage = []
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "dev", {"activity_id": "activity"}))
    monkeypatch.setattr(
        read_module,
        "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **_kwargs: _identity(table_id),
    )
    monkeypatch.setattr(read_module, "persist_lineage_participation", lambda **kwargs: lineage.append(kwargs))
    for table_id in ("warehouse:source:dbo:a", "warehouse:source:dbo:b"):
        read_module.read_pipeline_prep(source_table_id=table_id, source_read_strategy="full_dataset")
    assert [row["table_id"] for row in lineage] == ["warehouse:source:dbo:a", "warehouse:source:dbo:b"]
    assert {row["context"]["activity_id"] for row in lineage} == {"activity"}


@pytest.mark.parametrize(("previous", "upper", "expected_mode"), [
    (None, "2026-08-26 12:00", "full_dataset"),
    ("2026-08-26 12:00", "2026-08-26 12:00", "skip"),
    ("2026-08-26 10:00", "2026-08-26 12:00", "incremental_subset"),
])
def test_watermark_scope_is_bounded_by_target_state(monkeypatch, previous, upper, expected_mode):
    monkeypatch.setattr(read_module, "_target_watermark", lambda *_args, **_kwargs: previous)
    monkeypatch.setattr(read_module, "_source_upper_watermark", lambda *_args, **_kwargs: {
        "upper_watermark": upper, "data_type": "string", "row_count": 1,
        "non_null_count": 1, "distinct_count": 1,
    })
    monkeypatch.setattr(read_module, "_coerce_watermark_boundary", lambda value, *_args, **_kwargs: value)
    result = read_module._watermark_scope(
        {"table_id": "warehouse:source:dbo:bookings"}, {"store_kind": "lakehouse"}, "modified_datetime",
        config="config", env="dev", spark_session="spark", context={},
    )
    assert result["read_mode"] == expected_mode
    assert "candidate_checkpoint" not in result
    if previous is None:
        assert result["scope"] == {
            "type": "full_dataset",
            "watermark_column": "modified_datetime",
            "upper_bound": upper,
        }
    elif expected_mode == "incremental_subset":
        assert result["scope"]["lower_inclusive"] is False
        assert result["scope"]["upper_inclusive"] is True
        assert result["scope"]["lower_bound"] == previous
        assert result["scope"]["upper_bound"] == upper


def test_watermark_rejects_duplicate_values_that_can_hide_late_rows(monkeypatch):
    monkeypatch.setattr(read_module, "_target_watermark", lambda *_args, **_kwargs: "2026-08-26 10:00")
    monkeypatch.setattr(read_module, "_source_upper_watermark", lambda *_args, **_kwargs: {
        "upper_watermark": "2026-08-26 12:00", "data_type": "string", "row_count": 2,
        "non_null_count": 2, "distinct_count": 1,
    })
    with pytest.raises(ValueError, match="globally unique"):
        read_module._watermark_scope(
            {"table_id": "warehouse:source:dbo:bookings"}, {"store_kind": "lakehouse"}, "modified_datetime",
            config="config", env="dev", spark_session="spark", context={},
        )


def test_warehouse_target_watermark_uses_governed_target_query(monkeypatch):
    observed = {}

    class Row(dict):
        def asDict(self, recursive=False):
            return dict(self)

    class Frame:
        def collect(self):
            return [Row(target_watermark=200, row_count=5)]

    monkeypatch.setattr(
        read_module,
        "read_warehouse_query_core",
        lambda query, **kwargs: observed.update(query=query, kwargs=kwargs) or Frame(),
    )
    value = read_module._target_watermark(
        {"store_kind": "warehouse", "target": "product", "schema": "dbo", "table_name": "orders"},
        spark_session="spark",
        context={"activity_id": "activity"},
    )
    assert value == 200
    assert "MAX([_watermark_value]) AS target_watermark" in observed["query"]
    assert observed["kwargs"]["target"] == "product"


def test_incremental_watermark_requires_governed_target_identity(monkeypatch):
    identity = _patch_source_identity(monkeypatch)
    with pytest.raises(ValueError, match="target_table_id is required"):
        read_module.read_pipeline_prep(
            source_table_id=identity["table_id"],
            source_read_strategy="incremental_watermark",
            source_watermark_column="modified_datetime",
        )


def test_read_prep_uses_source_processing_from_change_check(monkeypatch):
    identity = _patch_source_identity(monkeypatch)
    observation = SimpleNamespace(sparkSession="spark")
    changes = {
        "table_id": identity["table_id"], "environment_name": "dev", "observation_id": "observation",
        "changed": True, "first_observation": False, "new_partitions": ["2026-08-22"],
        "changed_partitions": [], "removed_partitions": [], "reappeared_partitions": [],
        "partition_column": "snapshot_date", "load_strategy": "scd1",
    }
    target = _identity("lakehouse:unified:dbo:students", store_type="lakehouse")
    monkeypatch.setattr(
        read_module, "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **_kwargs: identity if table_id == identity["table_id"] else target,
    )
    monkeypatch.setattr(read_module, "get_spark_session", lambda: "spark")
    monkeypatch.setattr(read_module, "_target_partitions", lambda *args, **kwargs: {"2026-08-20": {"value": "2026-08-20", "committed_at": "then"}})
    monkeypatch.setattr(read_module, "_observe_table_core", lambda *args, **kwargs: observation)
    monkeypatch.setattr(read_module, "_observation_changes", lambda value, **_kwargs: changes if value is observation else pytest.fail())

    result = read_module.read_pipeline_prep(
        source_table_id=identity["table_id"],
        source_read_strategy="incremental_partition",
        target_table_id=target["table_id"],
        source_partition_column="snapshot_date",
    )

    assert result["changes"] is changes
    assert result["read_mode"] == "incremental_subset"
    assert result["scope"]["values"] == ["2026-08-22"]




@pytest.mark.parametrize(("strategy", "mode"), [("overwrite", "overwrite"), ("append", "append"), ("scd1", None)])
def test_write_prep_resolves_target_processing(monkeypatch, spark_session, strategy, mode):
    processing = {"load_strategy": strategy}
    if strategy == "scd1":
        processing["key_columns"] = ["student_id"]
    identity = _patch_target_processing(monkeypatch, processing)
    frame = spark_session.createDataFrame([(1, "active")], ["student_id", "status"])
    source_prep = {
        "source_processing": {"read_strategy": "full_dataset"},
        "read_mode": "full_dataset",
        "scope": {"type": "full_dataset"},
    }

    result = write_module.write_pipeline_prep(
        frame, target_table_id=identity["table_id"], source_preps=[source_prep]
    )

    assert result["target"] is identity
    assert result["processing"] is processing
    assert result["mode"] == mode
    assert result["load_strategy"] == strategy
    assert "_committed_at" in result["df"].columns


def test_write_prep_adds_scd2_lifecycle_for_warehouse(monkeypatch, spark_session):
    processing = {"load_strategy": "scd2", "key_columns": ["student_id"], "effective_column": "effective_at"}
    identity = _patch_target_processing(monkeypatch, processing, store_type="warehouse")
    frame = spark_session.createDataFrame([(1, "active", "2026-08-22")], ["student_id", "status", "effective_at"])
    result = write_module.write_pipeline_prep(
        frame,
        target_table_id=identity["table_id"],
        source_preps=[{"read_mode": "full_dataset", "scope": {"type": "full_dataset"}}],
    )
    assert result["mode"] is None
    assert result["target_kind"] == "warehouse"
    assert {"_effective_from", "_effective_to", "_is_current"} <= set(result["df"].columns)


def test_write_prep_partition_state_requires_no_completion_layer(monkeypatch, spark_session):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "scd1", "key_columns": ["student_id"]})
    frame = spark_session.createDataFrame([(1, "2026-08-31")], ["student_id", "snapshot_date"])
    source_prep = {
        "source_processing": {"read_strategy": "incremental_partition", "partition_column": "snapshot_date"},
        "observation": SimpleNamespace(),
        "changes": {
            "table_id": "source",
            "environment_name": "dev",
            "observation_id": "observation-1",
        },
        "read_mode": "incremental_subset",
        "scope": {"type": "partition", "column": "snapshot_date", "values": ["2026-08-31"]},
    }
    result = write_module.write_pipeline_prep(
        frame, target_table_id=identity["table_id"], source_preps=[source_prep]
    )
    assert "completion" not in result
    assert result["df"].select("_partition_bucket").first()[0] == "2026-08-31"


def test_write_prep_supports_multiple_source_scope_for_scd(monkeypatch, spark_session):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "scd1", "key_columns": ["student_id"]})
    frame = spark_session.createDataFrame([(1,)], ["student_id"])
    source_preps = [
        {"read_mode": "full_dataset", "scope": {"type": "full_dataset"}},
        {"read_mode": "incremental_subset", "scope": {
            "type": "partition", "column": "snapshot_date", "values": ["2026-08-31"],
        }},
    ]
    result = write_module.write_pipeline_prep(
        frame, target_table_id=identity["table_id"], source_preps=source_preps
    )
    assert result["scope"] == {
        "read_mode": "incremental_subset",
        "scope": {"type": "multiple_sources"},
    }


@pytest.mark.parametrize(
    "source_prep",
    [
        {
            "source_processing": {"read_strategy": "incremental_partition", "partition_column": "snapshot_date"},
            "read_mode": "incremental_subset",
            "scope": {"type": "partition", "column": "snapshot_date", "values": ["2026-08-31"]},
        },
        {
            "source_processing": {"read_strategy": "incremental_watermark", "watermark_column": "modified_at"},
            "read_mode": "incremental_subset",
            "scope": {
                "type": "watermark",
                "column": "modified_at",
                "lower_bound": 2,
                "upper_bound": 3,
                "lower_inclusive": False,
                "upper_inclusive": True,
            },
        },
    ],
    ids=["partition", "watermark"],
)
def test_write_prep_rejects_partial_warehouse_overwrite(monkeypatch, spark_session, source_prep):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "overwrite"}, store_type="warehouse")
    frame = spark_session.createDataFrame([(1,)], ["student_id"])

    with pytest.raises(ValueError, match="Incremental source processing cannot use unrestricted overwrite"):
        write_module.write_pipeline_prep(
            frame, target_table_id=identity["table_id"], source_preps=[source_prep]
        )


def test_write_prep_allows_full_dataset_warehouse_overwrite(monkeypatch, spark_session):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "overwrite"}, store_type="warehouse")
    frame = spark_session.createDataFrame([(1,)], ["student_id"])

    result = write_module.write_pipeline_prep(
        frame,
        target_table_id=identity["table_id"],
        source_preps=[{
            "source_processing": {"read_strategy": "full_dataset"},
            "read_mode": "full_dataset",
            "scope": {"type": "full_dataset"},
        }],
    )

    assert result["mode"] == "overwrite"
    assert result["options"] == {}


def test_write_prep_keeps_lakehouse_partition_overwrite_scoped(monkeypatch, spark_session):
    processing = {"load_strategy": "overwrite", "partition_column": "snapshot_date"}
    identity = _patch_target_processing(monkeypatch, processing)
    frame = spark_session.createDataFrame([(1, "2026-08-31")], ["student_id", "snapshot_date"])

    result = write_module.write_pipeline_prep(
        frame,
        target_table_id=identity["table_id"],
        source_preps=[{
            "source_processing": {"read_strategy": "incremental_partition", "partition_column": "snapshot_date"},
            "read_mode": "incremental_subset",
            "scope": {"type": "partition", "column": "snapshot_date", "values": ["2026-08-31"]},
        }],
    )

    assert result["mode"] == "overwrite"
    assert result["options"] == {"replaceWhere": "`_partition_bucket` IN ('2026-08-31')"}
    assert result["df"].select("_partition_bucket").first()[0] == "2026-08-31"


def test_write_prep_keeps_lakehouse_watermark_overwrite_scoped_and_replay_safe(monkeypatch, spark_session):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "overwrite"})
    frame = spark_session.createDataFrame([(1, 150), (2, 200)], ["student_id", "modified_at"])
    source_prep = {
        "source_processing": {"read_strategy": "incremental_watermark", "watermark_column": "modified_at"},
        "read_mode": "incremental_subset",
        "scope": {
            "type": "watermark", "column": "modified_at", "lower_bound": 100, "upper_bound": 200,
            "lower_inclusive": False, "upper_inclusive": True,
        },
    }

    first = write_module.write_pipeline_prep(
        frame, target_table_id=identity["table_id"], source_preps=[source_prep]
    )
    replay = write_module.write_pipeline_prep(
        frame, target_table_id=identity["table_id"], source_preps=[source_prep]
    )

    expected = {"replaceWhere": "`_watermark_value` > 100 AND `_watermark_value` <= 200"}
    assert first["mode"] == replay["mode"] == "overwrite"
    assert first["options"] == replay["options"] == expected


@pytest.mark.parametrize(
    "store_type",
    ["lakehouse", "warehouse"],
)
def test_write_prep_allows_first_watermark_population_overwrite(monkeypatch, spark_session, store_type):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "overwrite"}, store_type=store_type)
    frame = spark_session.createDataFrame([(1, 180), (2, 200)], ["student_id", "modified_at"])

    result = write_module.write_pipeline_prep(
        frame,
        target_table_id=identity["table_id"],
        source_preps=[{
            "source_processing": {"read_strategy": "incremental_watermark", "watermark_column": "modified_at"},
            "read_mode": "full_dataset",
            "scope": {"type": "full_dataset", "watermark_column": "modified_at", "upper_bound": 200},
        }],
    )

    assert result["mode"] == "overwrite"
    assert result["options"] == {}
    assert result["scope"]["read_mode"] == "full_dataset"


@pytest.mark.parametrize(
    "source_prep",
    [
        {
            "source_processing": {"read_strategy": "incremental_watermark", "watermark_column": "modified_at"},
            "read_mode": "full_dataset",
            "scope": {"type": "full_dataset", "watermark_column": "wrong_column", "upper_bound": 200},
        },
        {
            "source_processing": {"read_strategy": "incremental_watermark", "watermark_column": "modified_at"},
            "read_mode": "full_dataset",
            "scope": {"type": "full_dataset", "watermark_column": "modified_at"},
        },
        {
            "source_processing": {"read_strategy": "incremental_watermark", "watermark_column": "modified_at"},
            "read_mode": "incremental_subset",
            "scope": {
                "type": "watermark", "column": "modified_at", "lower_bound": 100, "upper_bound": 200,
                "lower_inclusive": True, "upper_inclusive": True,
            },
        },
    ],
    ids=["invalid-first-run-column", "missing-first-run-upper", "inclusive-lower"],
)
def test_write_prep_rejects_watermark_overwrite_without_canonical_scope(monkeypatch, source_prep):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "overwrite"})
    with pytest.raises(ValueError, match="cannot use unrestricted overwrite"):
        write_module.write_pipeline_prep(
            SimpleNamespace(columns=["student_id", "modified_at"]),
            target_table_id=identity["table_id"],
            source_preps=[source_prep],
        )


def test_write_prep_rejects_partition_overwrite_without_affected_values(monkeypatch):
    identity = _patch_target_processing(
        monkeypatch, {"load_strategy": "overwrite", "partition_column": "snapshot_date"}
    )
    with pytest.raises(ValueError, match="cannot use unrestricted overwrite"):
        write_module.write_pipeline_prep(
            SimpleNamespace(columns=["student_id", "snapshot_date"]),
            target_table_id=identity["table_id"],
            source_preps=[{
                "source_processing": {
                    "read_strategy": "incremental_partition", "partition_column": "snapshot_date",
                },
                "read_mode": "incremental_subset",
                "scope": {"type": "partition", "column": "snapshot_date", "values": []},
            }],
        )


def test_write_prep_keeps_lakehouse_full_dataset_overwrite(monkeypatch, spark_session):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "overwrite"})
    frame = spark_session.createDataFrame([(1,)], ["student_id"])

    result = write_module.write_pipeline_prep(
        frame,
        target_table_id=identity["table_id"],
        source_preps=[{
            "source_processing": {"read_strategy": "full_dataset"},
            "read_mode": "full_dataset",
            "scope": {"type": "full_dataset"},
        }],
    )

    assert result["mode"] == "overwrite"
    assert result["options"] == {}


def test_write_prep_rejects_incremental_partition_append(monkeypatch, spark_session):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "append"})
    frame = spark_session.createDataFrame([(1,)], ["student_id"])

    result = write_module.write_pipeline_prep(
        frame,
        target_table_id=identity["table_id"],
        source_preps=[{
            "read_mode": "incremental_subset",
            "scope": {"type": "partition", "column": "snapshot_date", "values": ["2026-08-31"]},
        }],
    )

    assert result["mode"] == "append"


def test_write_prep_rejects_unsafe_incremental_watermark_append(monkeypatch):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "append"})
    frame = SimpleNamespace(columns=["student_id", "modified_at"])
    with pytest.raises(ValueError, match="unsafe.*deterministic row identity"):
        write_module.write_pipeline_prep(
            frame,
            target_table_id=identity["table_id"],
            source_preps=[{
                "source_processing": {"read_strategy": "incremental_watermark", "watermark_column": "modified_at"},
                "read_mode": "incremental_subset",
                "scope": {"type": "watermark", "column": "modified_at", "lower_bound": 1, "upper_bound": 2},
            }],
        )


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        ([(1, 180)], "reaches 180.*captured upper watermark is 200"),
        ([], "transformed output is empty"),
    ],
    ids=["maximum-below-upper", "empty-output"],
)
def test_write_prep_rejects_watermark_output_that_cannot_advance_target(
    monkeypatch, spark_session, rows, message
):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "scd1", "key_columns": ["student_id"]})
    frame = spark_session.createDataFrame(rows, "student_id long, modified_at long")
    monkeypatch.setattr(write_module, "resolve_target_audit_fields", lambda _context: pytest.fail("audit"))

    with pytest.raises(ValueError, match=message):
        write_module.write_pipeline_prep(
            frame,
            target_table_id=identity["table_id"],
            source_preps=[{
                "source_processing": {"read_strategy": "incremental_watermark", "watermark_column": "modified_at"},
                "read_mode": "incremental_subset",
                "scope": {"type": "watermark", "column": "modified_at", "lower_bound": 100, "upper_bound": 200},
            }],
        )


@pytest.mark.parametrize(
    ("rows", "message"),
    [
        ([(1, 180)], "reaches 180.*captured upper watermark is 200"),
        ([], "transformed output is empty"),
    ],
    ids=["maximum-below-upper", "empty-output"],
)
def test_first_watermark_population_rejects_output_that_cannot_advance_target(
    monkeypatch, spark_session, rows, message
):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "scd1", "key_columns": ["student_id"]})
    frame = spark_session.createDataFrame(rows, "student_id long, modified_at long")
    monkeypatch.setattr(write_module, "resolve_target_audit_fields", lambda _context: pytest.fail("audit"))

    with pytest.raises(ValueError, match=message):
        write_module.write_pipeline_prep(
            frame,
            target_table_id=identity["table_id"],
            source_preps=[{
                "source_processing": {"read_strategy": "incremental_watermark", "watermark_column": "modified_at"},
                "read_mode": "full_dataset",
                "scope": {"type": "full_dataset", "watermark_column": "modified_at", "upper_bound": 200},
            }],
        )


def test_first_watermark_population_accepts_output_at_captured_upper(monkeypatch, spark_session):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "scd1", "key_columns": ["student_id"]})
    frame = spark_session.createDataFrame([(1, 180), (2, 200)], ["student_id", "modified_at"])

    result = write_module.write_pipeline_prep(
        frame,
        target_table_id=identity["table_id"],
        source_preps=[{
            "source_processing": {"read_strategy": "incremental_watermark", "watermark_column": "modified_at"},
            "read_mode": "full_dataset",
            "scope": {"type": "full_dataset", "watermark_column": "modified_at", "upper_bound": 200},
        }],
    )

    assert result["scope"]["read_mode"] == "full_dataset"
    assert result["scope"]["scope"]["upper_bound"] == 200
    assert result["df"].agg({"_watermark_value": "max"}).collect()[0][0] == 200


def test_write_prep_rejects_skipped_source(monkeypatch, spark_session):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "append"})
    frame = spark_session.createDataFrame([(1,)], ["student_id"])

    with pytest.raises(ValueError, match="non-skipped canonical read_mode"):
        write_module.write_pipeline_prep(
            frame,
            target_table_id=identity["table_id"],
            source_preps=[{"read_mode": "skip", "scope": {"type": "skip"}}],
        )


def test_lakehouse_writer_exposes_scd_strategy_without_fake_append_mode(monkeypatch):
    calls = []
    monkeypatch.setattr(lakehouse_writer, "validate_dataframe_writer", lambda _df: None)
    shared = import_module("fabricops_kit.pipeline.shared")
    monkeypatch.setattr(shared, "execute_lakehouse_processing", lambda *args, **kwargs: calls.append((args, kwargs)))
    lakehouse_writer.write_lakehouse_table(
        object(), "students", mode=None, load_strategy="scd1",
        load_strategy_parameters={"key_columns": ["student_id"]},
        processing_scope={"read_mode": "full_dataset", "scope": {"type": "full_dataset"}},
    )
    assert calls[0][1]["processing"] == {"load_strategy": "scd1", "key_columns": ["student_id"]}
    with pytest.raises(ValueError, match="mode must be None"):
        lakehouse_writer.write_lakehouse_table(
            object(), "students", mode="append", load_strategy="scd1",
            load_strategy_parameters={"key_columns": ["student_id"]},
            processing_scope={"read_mode": "full_dataset", "scope": {"type": "full_dataset"}},
        )









def test_partition_retry_compares_with_last_successful_observation():
    history = [
        {"observation_id": "successful", "table_id": "source", "environment_name": "dev", "_committed_at": 1},
        {"observation_id": "failed-run", "table_id": "source", "environment_name": "dev", "_committed_at": 2},
    ]
    previous = import_module("fabricops_kit.pipeline.check_changes")._previous_observation(
        history, table_id="source", environment_name="dev", committed_at=3,
        observation_id="successful",
    )
    assert [row["observation_id"] for row in previous] == ["successful"]




def test_target_partitions_absent_returns_empty(monkeypatch):
    monkeypatch.setattr(
        read_module, "read_lakehouse_table_core",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(Exception("Table or view not found")),
    )
    monkeypatch.setattr(read_module, "is_table_not_found_error", lambda _exc: True)
    assert read_module._target_partitions(
        {"store_kind": "lakehouse", "target": "unified", "schema": "dbo", "table_name": "students"},
        spark_session="spark", context={},
    ) == {}


def test_target_partitions_returns_persisted_state(monkeypatch, spark_session):
    target = spark_session.createDataFrame(
        [("2026-08-30", "2026-08-31T00:00:00"), ("2026-08-31", "2026-09-01T00:00:00")],
        ["_partition_bucket", "_committed_at"],
    )
    monkeypatch.setattr(read_module, "read_lakehouse_table_core", lambda *_args, **_kwargs: target)
    state = read_module._target_partitions(
        {"store_kind": "lakehouse", "target": "unified", "schema": "dbo", "table_name": "students"},
        spark_session=spark_session, context={},
    )
    assert set(state) == {"2026-08-30", "2026-08-31"}


def test_target_partitions_rejects_populated_legacy_target(monkeypatch, spark_session):
    target = spark_session.createDataFrame([(1,)], ["student_id"])
    monkeypatch.setattr(read_module, "read_lakehouse_table_core", lambda *_args, **_kwargs: target)
    with pytest.raises(ValueError, match="migrate or rebuild.*incremental_partition"):
        read_module._target_partitions(
            {"store_kind": "lakehouse", "target": "unified", "schema": "dbo", "table_name": "students"},
            spark_session=spark_session, context={},
        )


def test_lakehouse_target_partitions_rejects_null_bucket(monkeypatch, spark_session):
    target = spark_session.createDataFrame(
        [(None, "2026-09-01T00:00:00"), ("2026-08-31", "2026-09-01T00:00:00")],
        ["_partition_bucket", "_committed_at"],
    )
    monkeypatch.setattr(read_module, "read_lakehouse_table_core", lambda *_args, **_kwargs: target)
    with pytest.raises(ValueError, match="null _partition_bucket values.*migrate or rebuild"):
        read_module._target_partitions(
            {"store_kind": "lakehouse", "target": "unified", "schema": "dbo", "table_name": "students"},
            spark_session=spark_session, context={},
        )


def test_warehouse_target_partitions_rejects_null_bucket(monkeypatch):
    class Row(dict):
        def asDict(self, recursive=False):
            return dict(self)

    class Frame:
        def collect(self):
            return [Row(partition_bucket=None, committed_at="2026-09-01T00:00:00", row_count=1)]

    monkeypatch.setattr(read_module, "read_warehouse_query_core", lambda *_args, **_kwargs: Frame())
    with pytest.raises(ValueError, match="null _partition_bucket values.*migrate or rebuild"):
        read_module._target_partitions(
            {"store_kind": "warehouse", "target": "product", "schema": "dbo", "table_name": "students"},
            spark_session="spark", context={},
        )


def test_first_partition_population_persists_bucket(monkeypatch, spark_session):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "overwrite"})
    frame = spark_session.createDataFrame([(1, "2026-08-31")], ["student_id", "snapshot_date"])
    source = {
        "source_processing": {"read_strategy": "incremental_partition", "partition_column": "snapshot_date"},
        "read_mode": "full_dataset",
        "scope": {"type": "full_dataset", "partition_column": "snapshot_date", "values": ["2026-08-31"], "target_state_empty": True},
    }
    result = write_module.write_pipeline_prep(frame, target_table_id=identity["table_id"], source_preps=[source])
    assert result["options"] == {}
    assert result["df"].select("_partition_bucket").first()[0] == "2026-08-31"


def test_partition_write_rejects_reserved_or_missing_bucket_source(monkeypatch, spark_session):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "scd1", "key_columns": ["student_id"]})
    source = {
        "source_processing": {"read_strategy": "incremental_partition", "partition_column": "snapshot_date"},
        "read_mode": "incremental_subset",
        "scope": {"type": "partition", "column": "snapshot_date", "values": ["2026-08-31"]},
    }
    with pytest.raises(ValueError, match="retained through transformation"):
        write_module.write_pipeline_prep(
            spark_session.createDataFrame([(1,)], ["student_id"]), target_table_id=identity["table_id"], source_preps=[source]
        )
    with pytest.raises(ValueError, match="reserved FabricOps technical column"):
        write_module.write_pipeline_prep(
            spark_session.createDataFrame([(1, "2026-08-31", "x")], ["student_id", "snapshot_date", "_partition_bucket"]),
            target_table_id=identity["table_id"], source_preps=[source],
        )


def test_public_writers_have_no_completion_context():
    """Persistent checkpoint completion is not part of either writer API."""
    import inspect

    assert "completion_context" not in inspect.signature(lakehouse_writer.write_lakehouse_table).parameters
    assert "completion_context" not in inspect.signature(warehouse_writer.write_warehouse_table).parameters
