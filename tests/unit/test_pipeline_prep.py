"""Tests for governed pipeline read/write orchestration."""
# ruff: noqa: D103

from __future__ import annotations

from importlib import import_module
from inspect import signature

import pytest

pytestmark = pytest.mark.unit

io_package = import_module("fabricops_kit.io")
io_shared = import_module("fabricops_kit.io.shared")
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
        "store": "source" if ":source:" in table_id else "unified",
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
    ("store_type", "query", "reader_name", "message"),
    [
        ("lakehouse", None, "read_lakehouse_table", "Lakehouse table 'source.dbo.student_source' → read_lakehouse_table"),
        ("warehouse", None, "read_warehouse_table", "Warehouse table 'source.dbo.student_source' → read_warehouse_table"),
        ("warehouse", "SELECT customer_id FROM dbo.orders", "read_warehouse_query", "Warehouse query on 'source.dbo.student_source' → read_warehouse_query"),
    ],
)
def test_pipeline_read_dispatches_source(monkeypatch, capsys, store_type, query, reader_name, message):
    identity = _identity(store_type=store_type)
    context = _patch_read(monkeypatch, identity)
    calls = []
    for name in ("read_lakehouse_table", "read_warehouse_table", "read_warehouse_query"):
        monkeypatch.setattr(read_module, name, lambda *a, _name=name, **k: calls.append(_name) or "frame")

    result = read_module.pipeline_read(table_id=identity["table_id"], query=query)

    assert result["table_id"] == identity["table_id"]
    assert calls == [reader_name]
    assert "_fabricops_active_profile_registration" not in context
    assert capsys.readouterr().out.strip() == f"FabricOps Read → {message}"


def test_pipeline_read_verbose_false_prints_nothing(monkeypatch, capsys):
    identity = _identity(store_type="lakehouse")
    _patch_read(monkeypatch, identity)
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **k: "frame")

    read_module.pipeline_read(table_id=identity["table_id"], verbose=False)

    assert capsys.readouterr().out == ""


def test_pipeline_read_rejects_identity_conflict():
    with pytest.raises(ValueError, match="Provide table_id or both store and table_name"):
        read_module.pipeline_read()
    with pytest.raises(ValueError, match="table_id cannot be combined"):
        read_module.pipeline_read(table_id="id", store="source")


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
    monkeypatch.setattr(write_module, "_persist_target_processing", lambda **_kwargs: None)
    return identity, context


@pytest.mark.parametrize(
    ("store_type", "strategy", "writer"),
    [
        ("lakehouse", "append", "lakehouse"),
        ("lakehouse", "overwrite", "lakehouse"),
        ("warehouse", "append", "warehouse"),
        ("warehouse", "overwrite", "warehouse"),
    ],
)
def test_pipeline_write_resolves_identity_dispatches_and_commits_after_success(
    monkeypatch, capsys, store_type, strategy, writer
):
    identity, context = _patch_write(monkeypatch, store_type=store_type, strategy=strategy)
    events = []
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *a, **k: events.append("lakehouse"))
    monkeypatch.setattr(io_package, "write_warehouse_table", lambda *a, **k: events.append("warehouse"))
    monkeypatch.setattr(
        shared_module, "commit_pipeline_write_success", lambda value: events.append(("metadata", value))
    )
    result = write_module.pipeline_write(
        object(), store="unified", schema="dbo", table_name="students",
        source_table_ids=["source-a", "source-b"],
    )

    assert result == {"table_id": identity["table_id"]}
    assert events[0] == writer
    assert events[1][0] == "metadata"
    assert events[1][1]["source_table_ids"] == ["source-a", "source-b"]
    assert "_fabricops_active_profile_registration" not in context
    assert "store_type" not in signature(write_module.pipeline_write).parameters
    assert capsys.readouterr().out.strip() == (
        f"FabricOps Write → {store_type.title()} table 'unified.dbo.students' → {strategy} → write_{store_type}_table"
    )


def test_pipeline_write_persists_resolved_target_processing(monkeypatch, spark_session):
    """Persist the resolved processing definition after the physical target succeeds."""
    identity, _context = _patch_write(monkeypatch, strategy="scd1")
    processing = {"load_strategy": "scd1", "key_columns": ["id"]}
    persisted = []
    monkeypatch.setattr(write_module, "resolve_table_processing_definition", lambda *_a, **_k: processing)
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *a, **k: None)
    monkeypatch.setattr(shared_module, "execute_lakehouse_processing", lambda *a, **k: None)
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: None)
    monkeypatch.setattr(write_module, "_persist_target_processing", lambda **kwargs: persisted.append(kwargs))
    dataframe = spark_session.createDataFrame([(1,)], ["id"])

    write_module.pipeline_write(
        dataframe,
        table_id=identity["table_id"],
        source_table_ids=["source-a"],
    )

    assert persisted[0]["identity"] == identity
    assert persisted[0]["processing"] is processing
    assert persisted[0]["dataframe"] is dataframe


def test_target_processing_catalogue_row_contains_strategy_and_parameters(monkeypatch):
    """Write only governed processing fields into the target's table-level Catalogue row."""
    import json
    import sys
    import types

    rows = []

    class Source:
        def alias(self, _name):
            return self

    class Spark:
        def createDataFrame(self, values, *, schema):
            rows.extend(values)
            assert schema == "catalogue-schema"
            return Source()

    class DataFrame:
        sparkSession = Spark()

    class Merge:
        def alias(self, _name):
            return self

        def merge(self, *_args):
            return self

        def whenMatchedUpdate(self, **_kwargs):
            return self

        def whenNotMatchedInsertAll(self):
            return self

        def execute(self):
            return None

    tables_module = types.ModuleType("delta.tables")
    tables_module.DeltaTable = type("DeltaTable", (), {"forPath": staticmethod(lambda *_args: Merge())})
    monkeypatch.setitem(sys.modules, "delta", types.ModuleType("delta"))
    monkeypatch.setitem(sys.modules, "delta.tables", tables_module)
    monkeypatch.setattr(write_module, "coerce_metadata_row_types", lambda _table, row: row)
    monkeypatch.setattr(write_module, "metadata_table_schema_registry", lambda: {"METADATA_DATA_CATALOGUE": "catalogue-schema"})
    monkeypatch.setattr(write_module, "metadata_table_physical_schema", lambda *_args: None)
    monkeypatch.setattr(write_module, "resolve_configured_lakehouse_table", lambda *_a, **_k: (None, None, None, "/metadata/catalogue"))

    write_module._persist_target_processing(
        identity=_identity("lakehouse:unified:dbo:students", store_type="lakehouse"),
        processing={
            "load_strategy": "scd2",
            "key_columns": ["id"],
            "effective_column": "effective_at",
            "source": "data_contract",
            "contract_id": "contract-id",
        },
        audit=_audit(),
        config={},
        env="dev",
        dataframe=DataFrame(),
    )

    assert rows[0]["metadata_level"] == "table"
    assert rows[0]["load_strategy"] == "scd2"
    assert json.loads(rows[0]["load_strategy_parameters_json"]) == {
        "effective_column": "effective_at",
        "key_columns": ["id"],
    }


@pytest.mark.parametrize(
    ("store_type", "expected"),
    [
        ("lakehouse", "Lakehouse table 'unified.dbo.students' → SCD1 → governed Delta merge"),
        ("warehouse", "Warehouse table 'unified.dbo.students' → SCD1 → governed Warehouse merge"),
    ],
)
def test_pipeline_write_reports_governed_scd_route(monkeypatch, capsys, store_type, expected):
    identity, _ = _patch_write(monkeypatch, store_type=store_type, strategy="scd1")
    processing = {"load_strategy": "scd1", "key_columns": ["id"]}
    monkeypatch.setattr(write_module, "resolve_table_processing_definition", lambda *_a, **_k: processing)
    monkeypatch.setattr(shared_module, "execute_lakehouse_processing", lambda *a, **k: None)
    monkeypatch.setattr(io_shared, "execute_warehouse_processing", lambda *a, **k: None)
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: None)

    write_module.pipeline_write(object(), table_id=identity["table_id"], source_table_ids=["source-a"])

    assert capsys.readouterr().out.strip() == f"FabricOps Write → {expected}"


def test_pipeline_write_verbose_false_suppresses_output_and_low_level_lakehouse_verbose(monkeypatch, capsys):
    identity, _ = _patch_write(monkeypatch)
    writer_kwargs = []
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *a, **k: writer_kwargs.append(k))
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: None)

    write_module.pipeline_write(
        object(), table_id=identity["table_id"], source_table_ids=["source-a"], verbose=False
    )

    assert capsys.readouterr().out == ""
    assert writer_kwargs[0]["verbose"] is False


def test_pipeline_write_table_id_form_and_conflicting_forms(monkeypatch):
    identity, _ = _patch_write(monkeypatch)
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *a, **k: None)
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: None)
    result = write_module.pipeline_write(object(), table_id=identity["table_id"], source_table_ids=["source-a"])
    assert result["table_id"] == identity["table_id"]
    with pytest.raises(ValueError, match="table_id cannot be combined"):
        write_module.pipeline_write(object(), table_id="id", store="unified")


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
    for name in ("check_schema", "check_dq", "check_sensitive_data", "profile_table"):
        assert not hasattr(write_module, name)
