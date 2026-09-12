"""Tests for the public pipeline preparation boundary."""
# ruff: noqa: D103

from __future__ import annotations

from importlib import import_module
from types import SimpleNamespace

import pytest

pytestmark = pytest.mark.unit

read_module = import_module("fabricops_kit.pipeline.pipeline_read")
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
    context = {}
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "dev", context))
    monkeypatch.setattr(
        read_module,
        "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **_kwargs: resolved if table_id == resolved["table_id"] else pytest.fail(table_id),
    )
    monkeypatch.setattr(read_module, "persist_lineage_participation", lambda **_kwargs: "lineage-id")
    return resolved, context


def _patch_target_processing(monkeypatch, processing, *, store_type="lakehouse"):
    identity = _identity("lakehouse:unified:dbo:students", store_type=store_type)
    monkeypatch.setattr(write_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(write_module, "resolve_catalogue_table_identity", lambda *_args, **_kwargs: identity)
    monkeypatch.setattr(write_module, "catalogue_authored_processing", lambda value: {"load_strategy": value["load_strategy"]})
    monkeypatch.setattr(write_module, "resolve_table_processing_definition", lambda *_args, **_kwargs: processing)
    monkeypatch.setattr(write_module, "resolve_target_audit_fields", lambda _context: {
        "_committed_at": "2026-08-22T00:00:00Z", "_committed_by": "engineer",
        "_activity_id": "activity", "_workspace_id": "workspace",
        "_notebook_id": "notebook", "_notebook_name": "02_pipeline",
    })
    return identity


@pytest.mark.parametrize(
    ("store_type", "query", "reader_name"),
    [("lakehouse", None, "read_lakehouse_table"),
     ("warehouse", None, "read_warehouse_table"),
     ("warehouse", "SELECT customer_id FROM dbo.orders", "read_warehouse_query")],
)
def test_pipeline_read_dispatches_and_preserves_governed_context(monkeypatch, store_type, query, reader_name):
    identity = _identity(store_type=store_type)
    identity, context = _patch_source_identity(monkeypatch, identity)
    calls = []
    lineage = []
    for name in ("read_lakehouse_table", "read_warehouse_table", "read_warehouse_query"):
        monkeypatch.setattr(read_module, name, lambda *args, _name=name, **kwargs: calls.append((_name, args, kwargs)) or "frame")
    monkeypatch.setattr(read_module, "persist_lineage_participation", lambda **kwargs: lineage.append(kwargs))

    result = read_module.pipeline_read(table_id=identity["table_id"], query=query)

    assert result == {"dataframe": "frame", "table_id": identity["table_id"], "is_query": query is not None}
    assert [call[0] for call in calls] == [reader_name]
    assert lineage == [{"table_id": identity["table_id"], "pipeline_role": "source", "context": {}}]
    assert context["_fabricops_active_profile_registration"] == {"profile_role": "source", "table": identity}


def test_pipeline_read_resolves_physical_identity_and_infers_store(monkeypatch):
    identity = _identity(store_type="warehouse")
    context = {}
    resolved = []
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "dev", context))
    monkeypatch.setattr(read_module, "resolve_physical_table_identity", lambda *args, **kwargs: resolved.append(kwargs) or identity)
    monkeypatch.setattr(read_module, "read_warehouse_table", lambda *args, **kwargs: "frame")
    monkeypatch.setattr(read_module, "persist_lineage_participation", lambda **kwargs: None)

    result = read_module.pipeline_read(target="source", schema="dbo", table_name="student_source")

    assert result["table_id"] == identity["table_id"]
    assert resolved == [{"target": "source", "schema": "dbo", "table_name": "student_source"}]
    assert "store_type" not in __import__("inspect").signature(read_module.pipeline_read).parameters


def test_pipeline_read_rejects_query_for_lakehouse_before_side_effects(monkeypatch):
    _identity_value, context = _patch_source_identity(monkeypatch, _identity(store_type="lakehouse"))
    lineage = []
    monkeypatch.setattr(read_module, "persist_lineage_participation", lambda **kwargs: lineage.append(kwargs))
    with pytest.raises(ValueError, match="configured Warehouse source"):
        read_module.pipeline_read(table_id="warehouse:source:dbo:student_source", query="SELECT 1")
    assert lineage == []
    assert context == {}


def test_pipeline_read_rejects_incomplete_or_conflicting_identity():
    with pytest.raises(ValueError, match="Provide table_id or both target and table_name"):
        read_module.pipeline_read()
    with pytest.raises(ValueError, match="table_id cannot be combined"):
        read_module.pipeline_read(table_id="id", target="source")


def test_pipeline_read_does_not_own_visible_engineering_checks_or_profiling():
    for name in (
        "observe_table", "check_freshness", "check_source_stability", "check_schema",
        "check_dq", "profile_and_register_table", "profile_dataframe",
    ):
        assert not hasattr(read_module, name)


@pytest.mark.parametrize(("strategy", "mode"), [("overwrite", "overwrite"), ("append", "append"), ("scd1", None)])
def test_write_prep_resolves_target_processing(monkeypatch, spark_session, strategy, mode):
    processing = {"load_strategy": strategy}
    if strategy == "scd1":
        processing["key_columns"] = ["student_id"]
    identity = _patch_target_processing(monkeypatch, processing)
    frame = spark_session.createDataFrame([(1, "active")], ["student_id", "status"])
    source_prep = {"table_id": "warehouse:source:dbo:students", "source": {}}

    result = write_module.write_pipeline_prep(
        frame, target_table_id=identity["table_id"], source_preps=[source_prep]
    )

    assert result["target"] is identity
    assert result["processing"] is processing
    assert result["mode"] == mode
    assert result["load_strategy"] == strategy
    assert "_committed_at" in result["df"].columns
    assert result["success_context"] == {
        "target_table_id": identity["table_id"],
        "source_table_ids": [source_prep["table_id"]],
        "activity_id": "activity",
        "notebook_name": "02_pipeline",
        "notebook_id": "notebook",
    }
    assert not hasattr(write_module, "persist_lineage_participation")


def test_first_development_write_resolves_physical_target_without_catalogue(monkeypatch, spark_session):
    identity = _patch_target_processing(monkeypatch, {"load_strategy": "append"})
    identity["store_kind"] = identity["store_type"]
    monkeypatch.setattr(write_module, "resolve_physical_table_identity", lambda *_args, **_kwargs: identity)
    monkeypatch.setattr(
        write_module,
        "resolve_catalogue_table_identity",
        lambda *_args, **_kwargs: pytest.fail("first write must not require Catalogue registration"),
    )

    result = write_module.write_pipeline_prep(
        spark_session.createDataFrame([(1,)], ["id"]),
        target="unified",
        schema="dbo",
        table_name="students",
        load_strategy="append",
        source_preps=[{"table_id": "source", "source": {}}],
    )

    assert result["target"]["table_id"] == identity["table_id"]
    assert result["load_strategy"] == "append"


def test_write_prep_accepts_engineering_authored_processing():
    from inspect import signature

    parameters = signature(write_module.write_pipeline_prep).parameters
    assert "load_strategy" in parameters
    assert "load_strategy_parameters" in parameters


def test_write_prep_adds_scd2_lifecycle_for_warehouse(monkeypatch, spark_session):
    processing = {"load_strategy": "scd2", "key_columns": ["student_id"], "effective_column": "effective_at"}
    identity = _patch_target_processing(monkeypatch, processing, store_type="warehouse")
    frame = spark_session.createDataFrame([(1, "active", "2026-08-22")], ["student_id", "status", "effective_at"])
    result = write_module.write_pipeline_prep(
        frame,
        target_table_id=identity["table_id"],
        source_preps=[{"table_id": "warehouse:source:dbo:students", "source": {}}],
    )
    assert result["mode"] is None
    assert result["target_kind"] == "warehouse"
    assert {"_effective_from", "_effective_to", "_is_current"} <= set(result["df"].columns)


def test_write_prep_preserves_target_partition_overwrite(monkeypatch, spark_session):
    processing = {"load_strategy": "overwrite", "partition_column": "business_date"}
    identity = _patch_target_processing(monkeypatch, processing)
    frame = spark_session.createDataFrame([(1, "2026-09-09"), (2, "2026-09-10")], ["id", "business_date"])

    result = write_module.write_pipeline_prep(
        frame,
        target_table_id=identity["table_id"],
        source_preps=[{"table_id": "warehouse:source:dbo:orders", "source": {}}],
    )

    assert set(result["scope"]["values"]) == {"2026-09-09", "2026-09-10"}
    assert {row["_partition_bucket"] for row in result["df"].select("_partition_bucket").collect()} == {
        "2026-09-09", "2026-09-10",
    }
    assert "replaceWhere" in result["options"]


def test_contract_target_accepts_owner_name_after_notebook_id_changes(monkeypatch, spark_session):
    processing = {
        "load_strategy": "append", "source": "data_contract",
        "contract_id": "contract", "contract_version": 3,
        "owner_notebook_id": "development-notebook-id", "owner_notebook_name": "02_pipeline",
    }
    identity = _patch_target_processing(monkeypatch, processing)
    result = write_module.write_pipeline_prep(
        spark_session.createDataFrame([(1,)], ["id"]),
        target_table_id=identity["table_id"],
        source_preps=[{"table_id": "source", "source": {}}],
    )
    assert result["load_strategy"] == "append"
    assert result["load_strategy_parameters"] == {}


def test_contract_target_rejects_conflicting_writer(monkeypatch, spark_session):
    processing = {
        "load_strategy": "append", "source": "data_contract",
        "contract_id": "contract", "contract_version": 3,
        "owner_notebook_id": "notebook", "owner_notebook_name": "other_pipeline",
    }
    identity = _patch_target_processing(monkeypatch, processing)
    with pytest.raises(ValueError, match="[Oo]ne owning pipeline/notebook writer"):
        write_module.write_pipeline_prep(
            spark_session.createDataFrame([(1,)], ["id"]),
            target_table_id=identity["table_id"],
            source_preps=[{"table_id": "source", "source": {}}],
        )


def test_lakehouse_writer_exposes_scd_strategy_without_fake_append_mode(monkeypatch):
    calls = []
    monkeypatch.setattr(lakehouse_writer, "validate_dataframe_writer", lambda _df: None)
    shared = import_module("fabricops_kit.pipeline.shared")
    monkeypatch.setattr(shared, "execute_lakehouse_processing", lambda *args, **kwargs: calls.append((args, kwargs)))
    lakehouse_writer.write_lakehouse_table(
        object(), "students", mode=None, load_strategy="scd1",
        load_strategy_parameters={"key_columns": ["student_id"]},
        processing_scope={"type": "full_dataset"},
    )
    assert calls[0][1]["processing"] == {"load_strategy": "scd1", "key_columns": ["student_id"]}
    with pytest.raises(ValueError, match="mode must be None"):
        lakehouse_writer.write_lakehouse_table(
            object(), "students", mode="append", load_strategy="scd1",
            load_strategy_parameters={"key_columns": ["student_id"]},
            processing_scope={"type": "full_dataset"},
        )









def test_partition_retry_compares_with_last_successful_observation():
    history = [
        {"observation_id": "successful", "source_table_id": "source", "target_table_id": "target", "environment_name": "dev", "observation_status": "committed", "_notebook_name": "02_pipeline", "_committed_at": 1},
        {"observation_id": "failed-run", "source_table_id": "source", "target_table_id": "target", "environment_name": "dev", "observation_status": "observed", "_notebook_name": "02_pipeline", "_committed_at": 2},
    ]
    previous = import_module("fabricops_kit.pipeline.check_source_stability")._previous_observation(
        history, source_table_id="source", target_table_id="target", notebook_name="02_pipeline",
        environment_name="dev", committed_at=3,
        observation_id="successful",
    )
    assert [row["observation_id"] for row in previous] == ["successful"]




def test_public_writers_accept_post_write_success_context():
    """Writers own successful metadata commit after physical publication."""
    import inspect

    assert "success_context" in inspect.signature(lakehouse_writer.write_lakehouse_table).parameters
    assert "success_context" in inspect.signature(warehouse_writer.write_warehouse_table).parameters
