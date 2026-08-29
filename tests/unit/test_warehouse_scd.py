"""Governed Fabric Warehouse SCD execution tests."""

from importlib import import_module
from inspect import signature
from types import SimpleNamespace

import pytest

io_shared = import_module("fabricops_kit.io.shared")
writer = import_module("fabricops_kit.io.write_warehouse_table")
pipeline_shared = import_module("fabricops_kit.pipeline.shared")


def _store():
    return SimpleNamespace(name="product", workspace_id="workspace", item_id="warehouse")


def _capture_sql(monkeypatch, frame, processing):
    observed = {"writes": []}
    monkeypatch.setattr(
        io_shared,
        "resolve_configured_warehouse_table",
        lambda *_args, **_kwargs: (_store(), "dbo", "customers", "product.dbo.customers"),
    )
    monkeypatch.setattr(
        io_shared,
        "write_warehouse_synapsesql",
        lambda _df, _store, name, **kwargs: observed["writes"].append((name, kwargs)),
    )
    monkeypatch.setattr(
        io_shared,
        "execute_warehouse_sql",
        lambda _spark, _store, sql, **_kwargs: observed.setdefault("sql", sql),
    )
    io_shared.execute_warehouse_processing(
        frame, schema="dbo", table_name="customers", target="warehouse", processing=processing
    )
    return observed


def test_scd1_generates_transactional_create_upsert_and_replay_safe_merge(monkeypatch, spark_session):
    """SCD1 uses create-or-MERGE SQL without source-absence deletion."""
    frame = spark_session.createDataFrame([(1, "Ada")], ["customer_id", "name"])
    observed = _capture_sql(monkeypatch, frame, {"load_strategy": "scd1", "key_columns": ["customer_id"]})

    assert observed["writes"][0][0].startswith("product.dbo._fabricops_scd_")
    assert observed["writes"][0][1]["mode"] == "overwrite"
    sql = observed["sql"]
    assert "BEGIN TRANSACTION" in sql and "COMMIT TRANSACTION" in sql
    assert "SELECT * INTO [dbo].[customers]" in sql
    assert "MERGE [dbo].[customers] AS target" in sql
    assert "WHEN NOT MATCHED BY TARGET THEN INSERT" in sql
    assert "target.[customer_id] = source.[customer_id]" not in sql.split("THEN UPDATE SET", 1)[1].split("WHEN", 1)[0]
    assert "WHEN NOT MATCHED BY SOURCE" not in sql
    assert "DROP TABLE [dbo].[_fabricops_scd_" in sql


def test_scd1_rejects_duplicate_incoming_keys_before_staging(monkeypatch, spark_session):
    """Duplicate SCD1 keys fail before a staging write."""
    frame = spark_session.createDataFrame([(1, "Ada"), (1, "Grace")], ["customer_id", "name"])
    monkeypatch.setattr(io_shared, "write_warehouse_synapsesql", lambda *_args, **_kwargs: pytest.fail("mutation"))
    with pytest.raises(ValueError, match="duplicate business keys"):
        io_shared.execute_warehouse_processing(
            frame, schema="dbo", table_name="customers", target="warehouse",
            processing={"load_strategy": "scd1", "key_columns": ["customer_id"]},
        )


def test_scd2_generates_atomic_history_safety_and_idempotency_checks(monkeypatch, spark_session):
    """SCD2 SQL atomically validates, closes, and inserts versions."""
    frame = spark_session.createDataFrame(
        [(1, "Ada", "2026-01-01", "2026-01-01", "9999-12-31", True)],
        ["customer_id", "name", "effective_at", "_effective_from", "_effective_to", "_is_current"],
    )
    observed = _capture_sql(
        monkeypatch, frame,
        {"load_strategy": "scd2", "key_columns": ["customer_id"], "effective_column": "effective_at"},
    )
    sql = observed["sql"]
    assert "moves backwards" in sql
    assert "multiple current records" in sql
    assert "UPDATE target SET target.[_effective_to] = source.[effective_at]" in sql
    assert "target.[_is_current] = 0" in sql
    assert "INSERT INTO [dbo].[customers]" in sql
    assert "target.[_is_current] = 1" in sql
    assert "target.[name]" in sql
    assert "target.[_effective_from] <> source.[_effective_from]" not in sql
    assert "BEGIN TRANSACTION" in sql and "ROLLBACK TRANSACTION" in sql


def test_scd2_rejects_duplicate_keys_and_missing_lifecycle_columns(monkeypatch, spark_session):
    """Invalid SCD2 inputs fail before target mutation."""
    duplicate = spark_session.createDataFrame([(1, "a"), (1, "b")], ["customer_id", "effective_at"])
    with pytest.raises(ValueError, match="duplicate business keys"):
        io_shared.execute_warehouse_processing(
            duplicate, schema="dbo", table_name="customers", target="warehouse",
            processing={"load_strategy": "scd2", "key_columns": ["customer_id"], "effective_column": "effective_at"},
        )
    single = spark_session.createDataFrame([(1, "2026-01-01")], ["customer_id", "effective_at"])
    monkeypatch.setattr(
        io_shared, "resolve_configured_warehouse_table",
        lambda *_args, **_kwargs: (_store(), "dbo", "customers", "product.dbo.customers"),
    )
    monkeypatch.setattr(io_shared, "write_warehouse_synapsesql", lambda *_args, **_kwargs: None)
    with pytest.raises(ValueError, match="missing required columns"):
        io_shared.execute_warehouse_processing(
            single, schema="dbo", table_name="customers", target="warehouse",
            processing={"load_strategy": "scd2", "key_columns": ["customer_id"], "effective_column": "effective_at"},
        )


def test_staging_write_failure_attempts_cleanup(monkeypatch, spark_session):
    """A partially created staging table is cleaned after connector failure."""
    frame = spark_session.createDataFrame([(1, "Ada")], ["customer_id", "name"])
    statements = []
    monkeypatch.setattr(
        io_shared,
        "resolve_configured_warehouse_table",
        lambda *_args, **_kwargs: (_store(), "dbo", "customers", "product.dbo.customers"),
    )
    monkeypatch.setattr(
        io_shared,
        "write_warehouse_synapsesql",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("staging failed")),
    )
    monkeypatch.setattr(
        io_shared,
        "execute_warehouse_sql",
        lambda _spark, _store, sql, **_kwargs: statements.append(sql),
    )

    with pytest.raises(RuntimeError, match="staging failed"):
        io_shared.execute_warehouse_processing(
            frame, schema="dbo", table_name="customers", target="warehouse",
            processing={"load_strategy": "scd1", "key_columns": ["customer_id"]},
        )

    assert len(statements) == 1
    assert "DROP TABLE [dbo].[_fabricops_scd_" in statements[0]
    assert "fabricops_stage_cleanup_attempted" in statements[0]


def test_merge_failure_attempts_cleanup(monkeypatch, spark_session):
    """A failed transactional mutation gets a second cleanup attempt."""
    frame = spark_session.createDataFrame([(1, "Ada")], ["customer_id", "name"])
    statements = []
    monkeypatch.setattr(
        io_shared,
        "resolve_configured_warehouse_table",
        lambda *_args, **_kwargs: (_store(), "dbo", "customers", "product.dbo.customers"),
    )
    monkeypatch.setattr(io_shared, "write_warehouse_synapsesql", lambda *_args, **_kwargs: None)

    def execute(_spark, _store, sql, **_kwargs):
        statements.append(sql)
        if len(statements) == 1:
            raise RuntimeError("merge failed")

    monkeypatch.setattr(io_shared, "execute_warehouse_sql", execute)

    with pytest.raises(RuntimeError, match="merge failed"):
        io_shared.execute_warehouse_processing(
            frame, schema="dbo", table_name="customers", target="warehouse",
            processing={"load_strategy": "scd1", "key_columns": ["customer_id"]},
        )

    assert len(statements) == 2
    assert "BEGIN TRANSACTION" in statements[0]
    assert "fabricops_stage_cleanup_attempted" in statements[1]


def test_cleanup_failure_preserves_original_mutation_error(monkeypatch, spark_session):
    """Cleanup failure never replaces the original Warehouse mutation error."""
    frame = spark_session.createDataFrame([(1, "Ada")], ["customer_id", "name"])
    calls = []
    monkeypatch.setattr(
        io_shared,
        "resolve_configured_warehouse_table",
        lambda *_args, **_kwargs: (_store(), "dbo", "customers", "product.dbo.customers"),
    )
    monkeypatch.setattr(io_shared, "write_warehouse_synapsesql", lambda *_args, **_kwargs: None)

    def execute(_spark, _store, _sql, **_kwargs):
        calls.append("execute")
        if len(calls) == 1:
            raise RuntimeError("original merge failure")
        raise RuntimeError("cleanup failure")

    monkeypatch.setattr(io_shared, "execute_warehouse_sql", execute)

    with pytest.raises(RuntimeError, match="original merge failure"):
        io_shared.execute_warehouse_processing(
            frame, schema="dbo", table_name="customers", target="warehouse",
            processing={"load_strategy": "scd1", "key_columns": ["customer_id"]},
        )
    assert calls == ["execute", "execute"]


def test_writer_scd_completion_is_strictly_after_mutation(monkeypatch):
    """Successful mutation precedes completion exactly once."""
    events = []
    monkeypatch.setattr(writer, "validate_dataframe_writer", lambda _df: None)
    monkeypatch.setattr(writer, "repartition_dataframe_for_write", lambda df, _value: df)
    monkeypatch.setattr(writer, "execute_warehouse_processing", lambda *_args, **_kwargs: events.append("merge"))
    monkeypatch.setattr(pipeline_shared, "complete_source_processing", lambda *_args, **_kwargs: events.append("complete"))
    writer.write_warehouse_table(
        object(), "dbo", "customers", mode=None, load_strategy="scd1",
        load_strategy_parameters={"key_columns": ["customer_id"]}, completion_context={"sources": []},
    )
    assert events == ["merge", "complete"]


def test_writer_scd_failures_preserve_completion_boundary(monkeypatch):
    """Mutation failure prevents source completion."""
    monkeypatch.setattr(writer, "validate_dataframe_writer", lambda _df: None)
    monkeypatch.setattr(writer, "repartition_dataframe_for_write", lambda df, _value: df)
    monkeypatch.setattr(
        writer, "execute_warehouse_processing",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("merge failed")),
    )
    monkeypatch.setattr(
        pipeline_shared, "complete_source_processing", lambda *_args, **_kwargs: pytest.fail("completion called")
    )
    with pytest.raises(RuntimeError, match="merge failed"):
        writer.write_warehouse_table(
            object(), "dbo", "customers", mode=None, load_strategy="scd1",
            load_strategy_parameters={"key_columns": ["customer_id"]}, completion_context={"sources": []},
        )


def test_writer_surfaces_completion_failure_after_successful_scd(monkeypatch):
    """Completion errors remain visible after target success."""
    events = []
    monkeypatch.setattr(writer, "validate_dataframe_writer", lambda _df: None)
    monkeypatch.setattr(writer, "repartition_dataframe_for_write", lambda df, _value: df)
    monkeypatch.setattr(writer, "execute_warehouse_processing", lambda *_args, **_kwargs: events.append("merge"))
    monkeypatch.setattr(
        pipeline_shared, "complete_source_processing",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("checkpoint failed")),
    )
    with pytest.raises(RuntimeError, match="checkpoint failed"):
        writer.write_warehouse_table(
            object(), "dbo", "customers", mode=None, load_strategy="scd2",
            load_strategy_parameters={"key_columns": ["customer_id"], "effective_column": "effective_at"},
            completion_context={"sources": []},
        )
    assert events == ["merge"]


def test_writer_contract_and_contradictory_scd_mode(monkeypatch):
    """The public required signature stays fixed and SCD rejects write modes."""
    required = [name for name, parameter in signature(writer.write_warehouse_table).parameters.items()
                if parameter.default is parameter.empty]
    assert required == ["df", "schema", "table_name"]
    monkeypatch.setattr(writer, "validate_dataframe_writer", lambda _df: None)
    monkeypatch.setattr(writer, "repartition_dataframe_for_write", lambda df, _value: df)
    with pytest.raises(ValueError, match="mode must be None"):
        writer.write_warehouse_table(
            object(), "dbo", "customers", mode="append", load_strategy="scd1",
            load_strategy_parameters={"key_columns": ["customer_id"]},
        )
