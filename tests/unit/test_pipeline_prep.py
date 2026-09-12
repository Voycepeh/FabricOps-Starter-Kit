"""Tests for governed pipeline read/write orchestration."""
# ruff: noqa: D103

from __future__ import annotations

from importlib import import_module
from inspect import signature

import pytest

pytestmark = pytest.mark.unit

io_package = import_module("fabricops_kit.io")
read_module = import_module("fabricops_kit.pipeline.pipeline_read")
shared_module = import_module("fabricops_kit.pipeline.shared")
write_module = import_module("fabricops_kit.pipeline.pipeline_write")
lakehouse_writer = import_module("fabricops_kit.io.write_lakehouse_table")
warehouse_writer = import_module("fabricops_kit.io.write_warehouse_table")


def _identity(table_id="warehouse:source:dbo:student_source", *, store_type="warehouse"):
    return {
        "table_id": table_id,
        "store_type": store_type,
        "store_kind": store_type,
        "target": "source" if ":source:" in table_id else "unified",
        "schema": "dbo",
        "table_name": table_id.rsplit(":", 1)[-1],
        "load_strategy": "overwrite",
        "load_strategy_parameters_json": "{}",
    }


def _audit():
    return {
        "_committed_at": "2026-08-22T00:00:00Z",
        "_committed_by": "engineer",
        "_activity_id": "activity",
        "_workspace_id": "workspace",
        "_notebook_id": "notebook",
        "_notebook_name": "02_pipeline",
    }


def _patch_read(monkeypatch, identity):
    context = {}
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "dev", context))
    monkeypatch.setattr(read_module, "resolve_catalogue_table_identity", lambda *_a, **_k: identity)
    monkeypatch.setattr(read_module, "resolve_pipeline_data_contract", lambda *_a, **_k: None)
    monkeypatch.setattr(read_module, "persist_lineage_participation", lambda **_k: None)
    return context


@pytest.mark.parametrize(
    ("store_type", "query", "reader_name"),
    [
        ("lakehouse", None, "read_lakehouse_table"),
        ("warehouse", None, "read_warehouse_table"),
        ("warehouse", "SELECT customer_id FROM dbo.orders", "read_warehouse_query"),
    ],
)
def test_pipeline_read_dispatches_source(monkeypatch, store_type, query, reader_name):
    identity = _identity(store_type=store_type)
    context = _patch_read(monkeypatch, identity)
    calls = []
    for name in ("read_lakehouse_table", "read_warehouse_table", "read_warehouse_query"):
        monkeypatch.setattr(read_module, name, lambda *a, _name=name, **k: calls.append(_name) or "frame")

    result = read_module.pipeline_read(table_id=identity["table_id"], query=query)

    assert result["table_id"] == identity["table_id"]
    assert calls == [reader_name]
    assert context["_fabricops_active_profile_registration"]["profile_role"] == "source"


def test_pipeline_read_rejects_identity_conflict():
    with pytest.raises(ValueError, match="Provide table_id or both target and table_name"):
        read_module.pipeline_read()
    with pytest.raises(ValueError, match="table_id cannot be combined"):
        read_module.pipeline_read(table_id="id", target="source")


def _patch_write(monkeypatch, *, store_type="lakehouse", strategy="append", context=None):
    context = context if context is not None else {}
    identity = _identity(f"{store_type}:unified:dbo:students", store_type=store_type)
    monkeypatch.setattr(write_module, "resolve_fabric_context", lambda: ("config", "dev", context))
    monkeypatch.setattr(
        write_module,
        "resolve_catalogue_table_identity",
        lambda _config, _env, table_id, **_k: {**identity, "table_id": table_id},
    )
    monkeypatch.setattr(write_module, "resolve_physical_table_identity", lambda *_a, **_k: identity)
    monkeypatch.setattr(
        write_module, "catalogue_authored_processing", lambda value: {"load_strategy": value["load_strategy"]}
    )
    monkeypatch.setattr(
        write_module, "resolve_table_processing_definition", lambda *_a, **_k: {"load_strategy": strategy}
    )
    monkeypatch.setattr(write_module, "resolve_target_audit_fields", lambda _context: _audit())
    monkeypatch.setattr(write_module, "add_target_audit_fields", lambda frame, _audit_values: frame)
    return identity, context


@pytest.mark.parametrize(("store_type", "writer"), [("lakehouse", "lakehouse"), ("warehouse", "warehouse")])
def test_pipeline_write_resolves_identity_dispatches_and_commits_after_success(
    monkeypatch, store_type, writer
):
    identity, context = _patch_write(monkeypatch, store_type=store_type)
    events = []
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *a, **k: events.append("lakehouse"))
    monkeypatch.setattr(io_package, "write_warehouse_table", lambda *a, **k: events.append("warehouse"))
    monkeypatch.setattr(
        shared_module, "commit_pipeline_write_success", lambda value: events.append(("metadata", value))
    )
    result = write_module.pipeline_write(
        object(), target="unified", schema="dbo", table_name="students",
        source_table_ids=["source-a", "source-b"],
    )

    assert result == {"table_id": identity["table_id"]}
    assert events[0] == writer
    assert events[1][0] == "metadata"
    assert events[1][1]["source_table_ids"] == ["source-a", "source-b"]
    assert context["_fabricops_active_profile_registration"]["profile_role"] == "target"
    assert "store_type" not in signature(write_module.pipeline_write).parameters


def test_pipeline_write_table_id_form_and_conflicting_forms(monkeypatch):
    identity, _ = _patch_write(monkeypatch)
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *a, **k: None)
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: None)
    result = write_module.pipeline_write(object(), table_id=identity["table_id"], source_table_ids=["source-a"])
    assert result["table_id"] == identity["table_id"]
    with pytest.raises(ValueError, match="table_id cannot be combined"):
        write_module.pipeline_write(object(), table_id="id", target="unified")


@pytest.mark.parametrize("strategy", ["scd1", "scd2"])
def test_pipeline_write_routes_scd_to_governed_processing(monkeypatch, spark_session, strategy):
    identity, _ = _patch_write(monkeypatch, strategy=strategy)
    processing = {"load_strategy": strategy, "key_columns": ["id"]}
    if strategy == "scd2":
        processing["effective_column"] = "effective_at"
    monkeypatch.setattr(write_module, "resolve_table_processing_definition", lambda *_a, **_k: processing)
    physical = []
    governed = []
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *a, **k: physical.append(1))
    monkeypatch.setattr(shared_module, "execute_lakehouse_processing", lambda *a, **k: governed.append(k))
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: None)
    frame = spark_session.createDataFrame([(1, "2026-01-01")], ["id", "effective_at"])

    write_module.pipeline_write(frame, table_id=identity["table_id"], source_table_ids=["source-a"])

    assert not physical
    assert governed[0]["processing"] is processing


def test_pipeline_write_failure_does_not_commit_or_establish_profile(monkeypatch):
    _identity_value, context = _patch_write(monkeypatch)
    commits = []
    monkeypatch.setattr(
        io_package, "write_lakehouse_table", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("failed"))
    )
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: commits.append(value))
    with pytest.raises(RuntimeError, match="failed"):
        write_module.pipeline_write(object(), table_id="id", source_table_ids=["source-a"])
    assert commits == []
    assert "_fabricops_active_profile_registration" not in context


def test_pipeline_write_requires_explicit_sources(monkeypatch):
    _patch_write(monkeypatch)
    with pytest.raises(ValueError, match="source_table_ids must identify"):
        write_module.pipeline_write(object(), table_id="id")


def test_two_targets_commit_only_their_exact_source_subsets(monkeypatch):
    _identity_value, _context = _patch_write(monkeypatch)
    commits = []
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *a, **k: None)
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: commits.append(value))

    write_module.pipeline_write(object(), table_id="target-1", source_table_ids=["source-a", "source-b"])
    write_module.pipeline_write(object(), table_id="target-2", source_table_ids=["source-b"])

    assert [value["source_table_ids"] for value in commits] == [["source-a", "source-b"], ["source-b"]]
    assert [value["target_table_id"] for value in commits] == ["target-1", "target-2"]


def test_repeated_writes_do_not_inherit_prior_sources(monkeypatch):
    _identity_value, _context = _patch_write(monkeypatch)
    commits = []
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *a, **k: None)
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: commits.append(value))

    write_module.pipeline_write(object(), table_id="target-1", source_table_ids=["source-a"])
    write_module.pipeline_write(object(), table_id="target-1", source_table_ids=["source-c"])

    assert [value["source_table_ids"] for value in commits] == [["source-a"], ["source-c"]]


def test_foundational_writers_exclude_governed_parameters():
    governed = {"load_strategy", "load_strategy_parameters", "processing_scope", "success_context"}
    assert governed.isdisjoint(signature(lakehouse_writer.write_lakehouse_table).parameters)
    assert governed.isdisjoint(signature(warehouse_writer.write_warehouse_table).parameters)
    assert not hasattr(lakehouse_writer, "commit_pipeline_write_success")
    assert not hasattr(warehouse_writer, "commit_pipeline_write_success")


def test_pipeline_write_does_not_own_visible_checks():
    for name in ("check_schema", "check_dq", "check_sensitive_data", "profile_and_register_table"):
        assert not hasattr(write_module, name)
