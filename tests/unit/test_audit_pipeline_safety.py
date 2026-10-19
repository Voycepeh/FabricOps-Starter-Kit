"""Behavioral regressions for the Ponytail public-function audit findings."""

from importlib import import_module
from pathlib import Path
from types import SimpleNamespace

import pytest

io = import_module("fabricops_kit.io.shared")
shared = import_module("fabricops_kit.pipeline.shared")


@pytest.mark.parametrize("sql", [
    "SELECT 1; DELETE FROM dbo.orders",
    "WITH rows AS (SELECT * FROM dbo.orders) DELETE FROM rows",
    "SELECT * INTO dbo.copy FROM dbo.orders",
    "SELECT NEXT VALUE FOR dbo.sequence",
    "SELECT 1 EXEC('DELETE FROM dbo.orders')",
    "WITH rows AS (SELECT * FROM dbo.orders) UPDATE rows SET id = 1",
    "SELECT 1 UPDATE STATISTICS dbo.orders",
    "SELECT 1 SELECT 2",
])
def test_warehouse_reader_rejects_mutations_before_connector(monkeypatch, sql):
    """A query labelled read-only must not delegate write statements."""
    reader = import_module("fabricops_kit.io.read_warehouse_query")
    monkeypatch.setattr(reader, "resolve_configured_warehouse_query_store", lambda *a, **k: object())
    monkeypatch.setattr(reader, "read_warehouse_synapsesql", lambda *a, **k: pytest.fail("connector reached"))
    with pytest.raises(ValueError):
        reader.read_warehouse_query(sql, spark_session=object())


@pytest.mark.parametrize("sql", [
    "-- comment\nSELECT 'DELETE; INTO' AS [update];",
    "SELECT N'DELETE; INTO' AS [update];",
    "WITH rows AS (SELECT 1 AS id) SELECT id FROM rows",
    "SELECT 1 UNION ALL SELECT 2",
    "SELECT 1 UNION (SELECT 2) INTERSECT SELECT 2",
    "SELECT (SELECT source.* FOR JSON PATH, WITHOUT_ARRAY_WRAPPER) FROM dbo.orders source",
])
def test_read_only_tsql_preserves_literals_identifiers_and_json(sql):
    """Quoted text and valid Fabric SQL constructs are not mutation keywords."""
    assert io.validate_select_query(sql) == sql


@pytest.mark.parametrize("failure", [False, True])
def test_excel_temporary_workbook_is_removed_after_parsing(monkeypatch, tmp_path, failure):
    """Success and parser errors both remove workbook bytes from the driver."""
    files = []
    factory = io.tempfile.NamedTemporaryFile
    monkeypatch.setattr(io.tempfile, "NamedTemporaryFile", lambda **kw: factory(dir=tmp_path, **kw))
    binary = SimpleNamespace()
    binary.option = lambda *a: binary
    binary.load = lambda *a: binary
    binary.count = lambda: 1
    binary.select = lambda *a: binary
    binary.collect = lambda: [(b"workbook-contents",)]
    spark = SimpleNamespace(read=SimpleNamespace(format=lambda *a: binary), createDataFrame=lambda value: value)

    def parse(path, **kwargs):
        files.append(Path(path))
        assert files[-1].read_bytes() == b"workbook-contents"
        if failure:
            raise ValueError("invalid workbook")
        return "parsed-data"

    monkeypatch.setattr(io, "_load_pandas", lambda: SimpleNamespace(read_excel=parse))
    if failure:
        with pytest.raises(ValueError, match="invalid workbook"):
            io.read_excel_file(spark, "source.xlsx", sheet_name=0, read_excel_kwargs={})
    else:
        assert io.read_excel_file(spark, "source.xlsx", sheet_name=0, read_excel_kwargs={}) == "parsed-data"
    assert files and not files[0].exists()


@pytest.mark.parametrize("strategy", ["scd1", "scd2"])
@pytest.mark.parametrize("backend", ["lakehouse", "warehouse"])
def test_scd_null_keys_are_rejected_before_any_mutation(monkeypatch, spark_session, strategy, backend):
    """A null key component must never reach the SCD merge or first-load write."""
    frame = spark_session.createDataFrame([(1, None, "new")], "id long, version long, name string")
    definition = {"load_strategy": strategy, "key_columns": ["id", "version"]}
    if strategy == "scd2":
        definition["effective_column"] = "id"
    if backend == "warehouse":
        monkeypatch.setattr(io, "write_warehouse_synapsesql", lambda *a, **k: pytest.fail("staged null key"))
        with pytest.raises(ValueError, match="null business keys"):
            io.execute_warehouse_processing(frame, schema="dbo", table_name="orders", store="Gold", processing=definition)
    else:
        from tests.unit.test_load_strategy_execution import _install_delta

        class NoDeltaAccess:
            @staticmethod
            def isDeltaTable(*args):
                pytest.fail("target accessed before key validation")

        _install_delta(monkeypatch, NoDeltaAccess)
        with pytest.raises(ValueError, match="null business keys"):
            shared.execute_lakehouse_processing(frame, schema="dbo", table_name="orders", store="Silver",
                                               processing=definition, scope={"type": "full_dataset"})


def test_profile_forwards_explicit_session_to_catalogue_and_reader(monkeypatch):
    """Explicit-session profiling must not depend on an unrelated active session."""
    module = import_module("fabricops_kit.pipeline.profile_table")
    session = object()
    identity = {"table_id": "orders", "store_kind": "lakehouse", "store": "Bronze", "schema": "dbo", "table_name": "orders"}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: (object(), "dev", {}))

    def resolve(*args, **kwargs):
        assert kwargs["spark_session"] is session
        return identity

    def physical_read(*args, **kwargs):
        assert kwargs["spark_session"] is session
        raise LookupError("stopped after forwarding")

    monkeypatch.setattr(module, "resolve_catalogue_table_identity", resolve)
    monkeypatch.setattr(module, "read_lakehouse_table", physical_read)
    with pytest.raises(LookupError, match="stopped after forwarding"):
        module.profile_table(table_id="orders", spark_session=session)


@pytest.mark.parametrize("size", [0, 1000])
def test_incremental_observation_is_one_typed_summary(spark_session, size):
    """Distinct watermark cardinality must not affect driver observation size."""
    frame = spark_session.range(size).withColumnRenamed("id", "sequence")
    rows = shared._observe_dataframe(frame, "sequence", "sequence", watermark_only=True)
    assert len(rows) == 1
    assert rows[0]["row_count"] == size
    assert rows[0]["max_change_value"] == (str(size - 1) if size else None)
    assert rows[0]["is_present"] is bool(size)
    sql = shared._warehouse_observation_query("dbo", "orders", "sequence", "sequence", watermark_only=True)
    assert "GROUP BY" not in sql and "STRING_AGG" not in sql


@pytest.mark.parametrize("with_baseline", [False, True])
def test_empty_source_capture_and_scope_preserve_accepted_progress(monkeypatch, spark_session, with_baseline):
    """Typed empty progress evidence skips work without advancing or erasing a baseline."""
    from tests.unit.test_incremental_pipeline import _configure_scope, _row
    from tests.unit.test_source_observation_commit import _audit

    identity = {"table_id": "source-orders", "store_kind": "lakehouse", "store": "Bronze", "schema": "dbo", "table_name": "orders"}
    monkeypatch.setattr(shared, "resolve_fabric_context", lambda: (object(), "dev", {}))
    monkeypatch.setattr(shared, "get_spark_session", lambda: spark_session)
    monkeypatch.setattr(shared, "resolve_physical_table_identity", lambda *a, **k: identity)
    monkeypatch.setattr(shared, "get_store", lambda *a, **k: SimpleNamespace(schema_enabled=False))
    monkeypatch.setattr(shared, "resolve_lakehouse_table_location", lambda *a: ("orders", "dbo", "path"))
    monkeypatch.setattr(shared, "load_table_guardrail_rules", lambda *a, **k: [])
    monkeypatch.setattr(shared, "build_runtime_audit_fields", lambda **k: _audit())
    evidence = shared.capture_source_observation(
        table_id="source-orders", dataframe=spark_session.range(0).withColumnRenamed("id", "sequence"),
        incremental_columns=("sequence", "sequence"), source_identity=identity,
    )
    assert evidence.first().row_count == 0
    history = [_row(target="target-a", maximum="100")] if with_baseline else []
    _configure_scope(monkeypatch, history)
    scope = shared.resolve_incremental_source_scope(source_table_id="source-orders", target_table_id="target-a", observation=evidence)
    assert scope["has_data"] is False
    assert scope.get("after") == ("100" if with_baseline else None)
    assert shared._PENDING_SOURCE_OBSERVATIONS[("dev", "run-1", "source-orders", "target-a")] == []


def test_timestamp_summary_resolves_an_incremental_scope(monkeypatch, spark_session):
    """The compact summary retains canonical timestamp evidence for scope resolution."""
    from datetime import UTC, datetime
    from tests.unit.test_incremental_pipeline import Frame, _configure_scope

    frame = spark_session.createDataFrame([(datetime(2026, 10, 7, 2, 30, tzinfo=UTC),)], ["modified_at"])
    rows = shared._observe_dataframe(frame, "modified_at", "modified_at", watermark_only=True)
    _configure_scope(monkeypatch, [])
    scope = shared.resolve_incremental_source_scope(source_table_id="source-orders", target_table_id="target-a", observation=Frame([
        {**rows[0], "partition_column": "modified_at", "change_column": "modified_at"},
    ]))
    assert scope["through"] == "2026-10-07T02:30:00.000000Z"
    assert scope["has_data"] is True


def test_source_free_target_reaches_physical_publication(monkeypatch):
    """The writer must accept the empty source list forwarded by public orchestration."""
    from tests.unit.test_pipeline_prep import _patch_write

    module = import_module("fabricops_kit.pipeline.pipeline_write")
    package = import_module("fabricops_kit.io")
    _patch_write(monkeypatch)
    writes, commits = [], []
    monkeypatch.setattr(package, "write_lakehouse_table", lambda *a, **k: writes.append(k))
    monkeypatch.setattr(shared, "commit_pipeline_write_success", lambda context: commits.append(context))
    result = module.pipeline_write(object(), store="Silver", schema="dbo", table_name="mapping", source_table_ids=[], verbose=False)
    assert result["strategy"] == "append"
    assert len(writes) == 1
    assert commits[0]["source_table_ids"] == []
