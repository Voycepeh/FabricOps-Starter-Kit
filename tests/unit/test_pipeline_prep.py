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
freshness_module = import_module("fabricops_kit.pipeline.check_freshness")
source_drift_module = import_module("fabricops_kit.pipeline.check_source_drift")
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
    monkeypatch.setattr(read_module, "capture_source_observation", lambda **_k: "observation")
    return context


@pytest.mark.parametrize(
    ("store_type", "query", "reader_name"),
    [
        ("lakehouse", None, "read_lakehouse_table"),
        ("warehouse", None, "read_warehouse_table"),
        ("warehouse", "SELECT customer_id FROM dbo.orders", "read_warehouse_query"),
    ],
)
def test_pipeline_read_dispatches_source(monkeypatch, capsys, store_type, query, reader_name):
    identity = _identity(store_type=store_type)
    context = _patch_read(monkeypatch, identity)
    spark = object()
    calls = []
    for name in ("read_lakehouse_table", "read_warehouse_table", "read_warehouse_query"):
        monkeypatch.setattr(read_module, name, lambda *a, _name=name, **k: calls.append((_name, k)) or "frame")

    result = read_module.pipeline_read(table_id=identity["table_id"], query=query, spark_session=spark)

    assert result["table_id"] == identity["table_id"]
    assert [name for name, _kwargs in calls] == [reader_name]
    assert calls[0][1]["spark_session"] is spark
    assert "_fabricops_active_profile_registration" not in context
    output = capsys.readouterr().out
    assert "FabricOps Read" in output
    assert (
        f"1. Source → Object: {store_type.title()} | Store: source | Schema: dbo | Table: student_source"
        in output
    )
    assert f"   Identity → {identity['table_id']}" in output
    assert "2. Data Contract → none" in output
    assert f"3. Physical read → {reader_name}" in output
    assert "4. Source Observation → skipped; no selected Data Contract" in output
    assert "checks, profiling, transformations, and writes remain explicit" in output


def test_pipeline_read_physical_lakehouse_bootstraps_before_catalogue(monkeypatch):
    context = {}
    identity = {
        "table_id": "lakehouse:Bronze:demo:orders",
        "store_type": "lakehouse",
        "store_kind": "lakehouse",
        "store": "Bronze",
        "schema": "demo",
        "table_name": "orders",
    }
    spark = object()
    calls = []
    monkeypatch.setattr(read_module, "resolve_fabric_context", lambda: ("config", "dev", context))
    monkeypatch.setattr(read_module, "resolve_physical_table_identity", lambda *_a, **_k: identity)
    monkeypatch.setattr(
        read_module,
        "resolve_catalogue_table_identity",
        lambda *_a, **_k: pytest.fail("first physical read must not require Catalogue"),
    )
    monkeypatch.setattr(read_module, "resolve_pipeline_data_contract", lambda *_a, **_k: None)
    monkeypatch.setattr(
        read_module,
        "read_lakehouse_table",
        lambda *a, **k: calls.append((a, k)) or "frame",
    )

    result = read_module.pipeline_read(
        store="Bronze",
        schema="demo",
        table_name="orders",
        spark_session=spark,
        verbose=False,
    )

    assert result["table_id"] == identity["table_id"]
    assert calls == [(("orders",), {
        "store": "Bronze",
        "schema": "demo",
        "spark_session": spark,
        "context": {**context, "_fabricops_suppress_io_log": True},
    })]


def test_freshness_baseline_skips_before_observation_or_catalogue(monkeypatch):
    monkeypatch.setattr(freshness_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(freshness_module, "resolve_pipeline_data_contract", lambda *_a, **_k: None)
    monkeypatch.setattr(
        freshness_module,
        "get_current_freshness_evidence",
        lambda **_k: pytest.fail("baseline freshness must not require current-run evidence"),
    )
    monkeypatch.setattr(
        freshness_module,
        "resolve_catalogue_table_identity",
        lambda *_a, **_k: pytest.fail("baseline freshness must not require Catalogue"),
    )

    result = freshness_module.check_freshness("source-id", verbose=False)

    assert result["status"] == "skipped"
    assert result["reason"] == "No Data Contract selected; Development only."


def test_source_drift_baseline_skips_before_catalogue(monkeypatch):
    monkeypatch.setattr(source_drift_module, "resolve_fabric_context", lambda: ("config", "dev", {}))
    monkeypatch.setattr(source_drift_module, "resolve_pipeline_data_contract", lambda *_a, **_k: None)
    monkeypatch.setattr(
        source_drift_module,
        "resolve_catalogue_table_identity",
        lambda *_a, **_k: pytest.fail("baseline Source Drift must not require Catalogue"),
    )

    result = source_drift_module.check_source_drift(
        "source-id",
        target_table_id="target-id",
        verbose=False,
    )

    assert result["status"] == "skipped"
    assert result["source_table_id"] == "source-id"
    assert result["target_table_id"] == "target-id"


def test_pipeline_read_verbose_false_prints_nothing(monkeypatch, capsys):
    identity = _identity(store_type="lakehouse")
    _patch_read(monkeypatch, identity)
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **k: "frame")

    read_module.pipeline_read(table_id=identity["table_id"], verbose=False)

    assert capsys.readouterr().out == ""


def test_pipeline_read_captures_transient_observation_for_governed_source(monkeypatch):
    identity = _identity(store_type="lakehouse")
    _patch_read(monkeypatch, identity)
    monkeypatch.setattr(read_module, "resolve_pipeline_data_contract", lambda *_a, **_k: {"contract_id": "c"})
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **k: "frame")
    captured = []
    monkeypatch.setattr(read_module, "capture_source_observation", lambda **kwargs: captured.append(kwargs))
    read_module.pipeline_read(table_id=identity["table_id"], verbose=False)
    assert captured == [{"table_id": identity["table_id"], "dataframe": "frame"}]


@pytest.mark.parametrize("guardrail_type", ["schema", "freshness", "data_quality"])
def test_pipeline_read_does_not_require_source_drift(monkeypatch, guardrail_type):
    """A selected contract does not make Source Drift an implicit prerequisite."""
    identity = _identity(store_type="lakehouse")
    _patch_read(monkeypatch, identity)
    monkeypatch.setattr(
        read_module,
        "resolve_pipeline_data_contract",
        lambda *_a, **_k: {"guardrails": [{"guardrail_type": guardrail_type}]},
    )
    monkeypatch.setattr(read_module, "read_lakehouse_table", lambda *a, **k: "frame")
    monkeypatch.setattr(read_module, "capture_source_observation", lambda **_k: None)

    result = read_module.pipeline_read(table_id=identity["table_id"], verbose=False)

    assert result["dataframe"] == "frame"
    assert result["has_contract"] is True


def test_pipeline_read_rejects_identity_conflict():
    with pytest.raises(ValueError, match="Provide table_id or both store and table_name"):
        read_module.pipeline_read()
    with pytest.raises(ValueError, match="table_id cannot be combined"):
        read_module.pipeline_read(table_id="id", store="Bronze")


def test_resolve_physical_table_identity_preserves_configured_store_case(monkeypatch):
    calls = []

    class Store:
        kind = "lakehouse"
        schema_enabled = True
        schema = "demo"
        key = "Bronze"

    def get_store(_config, _env, store):
        calls.append(store)
        if store != "Bronze":
            raise ValueError("store key case changed before lookup")
        return Store()

    monkeypatch.setattr(shared_module, "get_store", get_store)
    monkeypatch.setattr(
        shared_module,
        "resolve_lakehouse_table_location",
        lambda _store, table_name, schema: (table_name, schema, "/table/path"),
    )

    identity = shared_module.resolve_physical_table_identity(
        object(),
        "dev",
        store="Bronze",
        schema="demo",
        table_name="orders",
    )

    assert calls == ["Bronze"]
    assert identity["store"] == "Bronze"


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
    monkeypatch.setattr(write_module, "incremental_publication_scopes", lambda **kwargs: {})
    monkeypatch.setattr(write_module, "_target_has_activity", lambda **kwargs: False)
    monkeypatch.setattr(shared_module, "stage_pipeline_write_observations", lambda value: [])
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
    spark = object()
    persisted = []
    monkeypatch.setattr(write_module, "_persist_target_processing", lambda **kwargs: persisted.append(kwargs))
    events = []
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *a, **k: events.append("lakehouse"))
    monkeypatch.setattr(io_package, "write_warehouse_table", lambda *a, **k: events.append("warehouse"))
    monkeypatch.setattr(
        shared_module, "commit_pipeline_write_success", lambda value: events.append(("metadata", value))
    )
    result = write_module.pipeline_write(
        object(),
        store="Silver",
        schema="dbo",
        table_name="students",
        source_table_ids=["source-a", "source-b"],
        spark_session=spark,
    )

    assert result == {"table_id": identity["table_id"]}
    assert persisted[0]["spark_session"] is spark
    assert events[0] == writer
    assert events[1][0] == "metadata"
    assert events[1][1]["source_table_ids"] == ["source-a", "source-b"]
    assert "_fabricops_active_profile_registration" not in context
    assert "store_type" not in signature(write_module.pipeline_write).parameters
    output = capsys.readouterr().out
    assert "FabricOps Write" in output
    assert (
        f"1. Target → Object: {store_type.title()} | Store: unified | Schema: dbo | Table: students"
        in output
    )
    assert f"   Identity → {identity['table_id']}" in output
    assert f"2. Processing → {strategy.upper()} from resolved processing" in output
    assert "3. Scope → full dataset" in output
    assert "4. Audit + ownership → runtime audit fields applied; writer ownership validated" in output
    assert f"5. Physical publication → write_{store_type}_table" in output
    assert "6. Catalogue → resolved load strategy and parameters persisted" in output
    assert "7. Success metadata → Lineage and accepted Source Observation state committed" in output


def test_pipeline_write_does_not_run_source_drift(monkeypatch):
    """Source Drift remains an explicit notebook check."""
    _patch_write(monkeypatch)
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *args, **kwargs: None)
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: None)

    write_module.pipeline_write(object(), table_id="target", source_table_ids=["source"])

    assert not hasattr(write_module, "check_source_drift_for_target")
    assert not hasattr(write_module, "check_source_drift")


def test_pipeline_write_rejects_incremental_whole_table_overwrite(monkeypatch):
    """A partial incremental source cannot destructively replace a whole target."""
    _patch_write(monkeypatch, strategy="overwrite")
    monkeypatch.setattr(
        write_module,
        "incremental_publication_scopes",
        lambda **kwargs: {"source-a": {"first_run": False}},
    )
    monkeypatch.setattr(
        io_package,
        "write_lakehouse_table",
        lambda *args, **kwargs: pytest.fail("unsafe write must be rejected before publication"),
    )

    with pytest.raises(ValueError, match="whole-table overwrite"):
        write_module.pipeline_write(
            object(), table_id="target", source_table_ids=["source-a"]
        )


@pytest.mark.parametrize("target_has_rows", [False, True])
def test_incremental_append_bootstrap_requires_new_or_empty_target(
    monkeypatch, target_has_rows
):
    """Append bootstrap fails safely when an existing target already has data."""
    _patch_write(monkeypatch, strategy="append")
    monkeypatch.setattr(
        write_module,
        "incremental_publication_scopes",
        lambda **kwargs: {"source-a": {"first_run": True, "type": "full"}},
    )
    monkeypatch.setattr(write_module, "_target_has_rows", lambda **kwargs: target_has_rows)
    writes = []
    monkeypatch.setattr(
        io_package, "write_lakehouse_table", lambda *args, **kwargs: writes.append(kwargs)
    )
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: None)

    if target_has_rows:
        with pytest.raises(ValueError, match="requires a new or empty target"):
            write_module.pipeline_write(
                object(), table_id="target", source_table_ids=["source-a"]
            )
        assert writes == []
    else:
        write_module.pipeline_write(
            object(), table_id="target", source_table_ids=["source-a"], verbose=False
        )
        assert len(writes) == 1


@pytest.mark.parametrize("strategy", ["scd1", "scd2"])
def test_incremental_merge_bootstrap_uses_idempotent_processing(
    monkeypatch, spark_session, strategy
):
    """SCD bootstrap relies on the existing idempotent keyed merge semantics."""
    _patch_write(monkeypatch, strategy=strategy)
    processing = {"load_strategy": strategy, "key_columns": ["id"]}
    if strategy == "scd2":
        processing["effective_column"] = "effective_at"
    monkeypatch.setattr(
        write_module, "resolve_table_processing_definition", lambda *_args, **_kwargs: processing
    )
    monkeypatch.setattr(
        write_module,
        "incremental_publication_scopes",
        lambda **kwargs: {"source-a": {"first_run": True, "type": "full"}},
    )
    monkeypatch.setattr(
        write_module,
        "_target_has_rows",
        lambda **kwargs: pytest.fail("SCD bootstrap must use its keyed merge, not append safety"),
    )
    governed = []
    monkeypatch.setattr(
        shared_module,
        "execute_lakehouse_processing",
        lambda *args, **kwargs: governed.append(kwargs),
    )
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: None)

    frame = spark_session.createDataFrame(
        [(1, "2026-09-19")], "id long, effective_at string"
    )

    write_module.pipeline_write(
        frame, table_id="target", source_table_ids=["source-a"], verbose=False
    )

    assert governed[0]["processing"] is processing


def test_removed_partition_is_cleared_by_empty_partition_overwrite(
    monkeypatch, spark_session
):
    """Removal-only work publishes an empty replaceWhere scope before committing."""
    identity, _context = _patch_write(monkeypatch, strategy="overwrite")
    processing = {"load_strategy": "overwrite", "partition_column": "business_date"}
    monkeypatch.setattr(
        write_module, "resolve_table_processing_definition", lambda *_args, **_kwargs: processing
    )
    monkeypatch.setattr(
        write_module,
        "incremental_publication_scopes",
        lambda **kwargs: {
            "source-a": {
                "type": "partitions",
                "first_run": False,
                "column": "business_date",
                "values": ["2026-09-18"],
                "removed_values": ["2026-09-18"],
            }
        },
    )
    writes = []
    commits = []
    monkeypatch.setattr(
        io_package,
        "write_lakehouse_table",
        lambda frame, *args, **kwargs: writes.append((frame, kwargs)),
    )
    monkeypatch.setattr(
        shared_module, "commit_pipeline_write_success", lambda value: commits.append(value)
    )
    frame = spark_session.createDataFrame([], "business_date string, order_id long")

    write_module.pipeline_write(
        frame,
        table_id=identity["table_id"],
        source_table_ids=["source-a"],
        verbose=False,
    )
    write_module.pipeline_write(
        frame,
        table_id=identity["table_id"],
        source_table_ids=["source-a"],
        verbose=False,
    )

    assert len(writes) == 2
    assert writes[0][0].count() == 0
    assert writes[0][1]["mode"] == "overwrite"
    assert writes[0][1]["options"] == {
        "replaceWhere": "`_partition_bucket` IN ('2026-09-18')"
    }
    assert commits[0]["source_table_ids"] == ["source-a"]
    assert len(commits) == 2


def test_removed_partition_rejects_non_reconciling_strategy(monkeypatch):
    """A strategy that cannot clear stale rows must not accept removal progress."""
    _patch_write(monkeypatch, strategy="append")
    monkeypatch.setattr(
        write_module,
        "incremental_publication_scopes",
        lambda **kwargs: {
            "source-a": {
                "type": "partitions",
                "first_run": False,
                "column": "business_date",
                "removed_values": ["2026-09-18"],
            }
        },
    )
    monkeypatch.setattr(
        io_package,
        "write_lakehouse_table",
        lambda *args, **kwargs: pytest.fail("unsafe removal must not publish"),
    )
    monkeypatch.setattr(
        shared_module,
        "commit_pipeline_write_success",
        lambda value: pytest.fail("unsafe removal must not commit progress"),
    )

    with pytest.raises(ValueError, match="require governed partition-scoped overwrite"):
        write_module.pipeline_write(
            object(), table_id="target", source_table_ids=["source-a"]
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
    monkeypatch.setattr(
        write_module, "metadata_table_schema_registry", lambda: {"METADATA_DATA_CATALOGUE": "catalogue-schema"}
    )
    monkeypatch.setattr(write_module, "metadata_table_physical_schema", lambda *_args: None)
    monkeypatch.setattr(
        write_module, "resolve_configured_lakehouse_table", lambda *_a, **_k: (None, None, None, "/metadata/catalogue")
    )

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
    ("store_type", "expected_path"),
    [
        ("lakehouse", "execute_lakehouse_processing"),
        ("warehouse", "execute_warehouse_processing"),
    ],
)
def test_pipeline_write_reports_governed_scd_route(monkeypatch, capsys, store_type, expected_path):
    identity, _ = _patch_write(monkeypatch, store_type=store_type, strategy="scd1")
    processing = {"load_strategy": "scd1", "key_columns": ["id"]}
    monkeypatch.setattr(write_module, "resolve_table_processing_definition", lambda *_a, **_k: processing)
    monkeypatch.setattr(shared_module, "execute_lakehouse_processing", lambda *a, **k: None)
    monkeypatch.setattr(io_shared, "execute_warehouse_processing", lambda *a, **k: None)
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: None)

    write_module.pipeline_write(object(), table_id=identity["table_id"], source_table_ids=["source-a"])

    output = capsys.readouterr().out
    assert "2. Processing → SCD1 from resolved processing" in output
    assert f"5. Physical publication → {expected_path}" in output


def test_pipeline_write_verbose_false_suppresses_output_and_low_level_lakehouse_verbose(monkeypatch, capsys):
    identity, _ = _patch_write(monkeypatch)
    writer_kwargs = []
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *a, **k: writer_kwargs.append(k))
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: None)

    write_module.pipeline_write(object(), table_id=identity["table_id"], source_table_ids=["source-a"], verbose=False)

    assert capsys.readouterr().out == ""
    assert writer_kwargs[0]["verbose"] is False


def test_pipeline_write_table_id_form_and_conflicting_forms(monkeypatch):
    identity, _ = _patch_write(monkeypatch)
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *a, **k: None)
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: None)
    result = write_module.pipeline_write(object(), table_id=identity["table_id"], source_table_ids=["source-a"])
    assert result["table_id"] == identity["table_id"]
    with pytest.raises(ValueError, match="table_id cannot be combined"):
        write_module.pipeline_write(object(), table_id="id", store="Silver")


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


@pytest.mark.parametrize("strategy", ["append", "overwrite", "scd1", "scd2"])
def test_pipeline_write_retry_uses_activity_marker_and_replays_metadata(
    monkeypatch, spark_session, strategy
):
    """Row-producing retries skip physical work and replay metadata safely."""
    identity, context = _patch_write(monkeypatch, strategy=strategy)
    processing = {"load_strategy": strategy}
    if strategy in {"scd1", "scd2"}:
        processing["key_columns"] = ["id"]
    if strategy == "scd2":
        processing["effective_column"] = "effective_at"
    monkeypatch.setattr(
        write_module, "resolve_table_processing_definition", lambda *_args, **_kwargs: processing
    )
    marker = {"present": False}
    physical = []
    finalizations = []
    catalogue = []
    monkeypatch.setattr(
        write_module, "_target_has_activity", lambda **_kwargs: marker["present"]
    )

    def publish(*_args, **_kwargs):
        physical.append(strategy)
        marker["present"] = True

    monkeypatch.setattr(io_package, "write_lakehouse_table", publish)
    monkeypatch.setattr(shared_module, "execute_lakehouse_processing", publish)
    monkeypatch.setattr(
        write_module, "_persist_target_processing", lambda **_kwargs: catalogue.append(strategy)
    )

    def finalize(_value):
        finalizations.append(strategy)
        if len(finalizations) == 1:
            raise RuntimeError("injected metadata failure")

    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", finalize)
    frame = spark_session.createDataFrame([(1, "2026-01-01")], ["id", "effective_at"])

    with pytest.raises(RuntimeError, match="injected metadata failure"):
        write_module.pipeline_write(
            frame, table_id=identity["table_id"], source_table_ids=["source-a"], verbose=False
        )
    write_module.pipeline_write(
        frame, table_id=identity["table_id"], source_table_ids=["source-a"], verbose=False
    )
    write_module.pipeline_write(
        frame, table_id=identity["table_id"], source_table_ids=["source-a"], verbose=False
    )

    assert physical == [strategy]
    assert catalogue == [strategy, strategy, strategy]
    assert finalizations == [strategy, strategy, strategy]
    assert "_fabricops_active_profile_registration" not in context


@pytest.mark.parametrize("strategy", ["append", "overwrite", "scd1", "scd2"])
def test_no_marker_publication_can_be_safely_reevaluated(monkeypatch, spark_session, strategy):
    """Empty or no-op publications may repeat because they have no duplicate side effect."""
    identity, _context = _patch_write(monkeypatch, strategy=strategy)
    processing = {"load_strategy": strategy}
    if strategy in {"scd1", "scd2"}:
        processing["key_columns"] = ["id"]
    if strategy == "scd2":
        processing["effective_column"] = "effective_at"
    monkeypatch.setattr(
        write_module, "resolve_table_processing_definition", lambda *_args, **_kwargs: processing
    )
    monkeypatch.setattr(write_module, "_target_has_activity", lambda **_kwargs: False)
    physical = []
    monkeypatch.setattr(
        io_package, "write_lakehouse_table", lambda *_args, **_kwargs: physical.append(strategy)
    )
    monkeypatch.setattr(
        shared_module, "execute_lakehouse_processing", lambda *_args, **_kwargs: physical.append(strategy)
    )
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda _value: None)
    frame = spark_session.createDataFrame([], "id long, effective_at string")

    write_module.pipeline_write(
        frame, table_id=identity["table_id"], source_table_ids=["source-a"], verbose=False
    )
    write_module.pipeline_write(
        frame, table_id=identity["table_id"], source_table_ids=["source-a"], verbose=False
    )

    assert physical == [strategy, strategy]


def test_failed_physical_publication_does_not_finalize_metadata(monkeypatch):
    _patch_write(monkeypatch, strategy="append")
    finalizations = []
    monkeypatch.setattr(
        io_package,
        "write_lakehouse_table",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("physical failure")),
    )
    monkeypatch.setattr(
        shared_module, "commit_pipeline_write_success", lambda value: finalizations.append(value)
    )

    with pytest.raises(RuntimeError, match="physical failure"):
        write_module.pipeline_write(object(), table_id="target", source_table_ids=["source-a"])

    assert finalizations == []

def test_pipeline_write_requires_explicit_sources(monkeypatch):
    _patch_write(monkeypatch)
    with pytest.raises(ValueError, match="source_table_ids must identify"):
        write_module.pipeline_write(object(), table_id="id")


def test_two_targets_commit_only_their_exact_source_subsets(monkeypatch):
    _identity_value, _context = _patch_write(monkeypatch)
    commits = []
    writes = []
    monkeypatch.setattr(
        write_module,
        "_target_has_activity",
        lambda **kwargs: kwargs["identity"]["table_id"] == "target-1",
    )
    monkeypatch.setattr(io_package, "write_lakehouse_table", lambda *a, **k: writes.append(a))
    monkeypatch.setattr(shared_module, "commit_pipeline_write_success", lambda value: commits.append(value))

    write_module.pipeline_write(object(), table_id="target-1", source_table_ids=["source-a", "source-b"])
    write_module.pipeline_write(object(), table_id="target-2", source_table_ids=["source-b"])

    assert [value["source_table_ids"] for value in commits] == [["source-a", "source-b"], ["source-b"]]
    assert [value["target_table_id"] for value in commits] == ["target-1", "target-2"]
    assert len(writes) == 1


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
    for name in (
        "check_schema",
        "check_dq",
        "check_sensitive_data",
        "check_source_drift_for_target",
        "profile_table",
    ):
        assert not hasattr(write_module, name)
