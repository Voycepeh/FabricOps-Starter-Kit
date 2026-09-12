"""Focused tests for the consolidated profiling API."""

from __future__ import annotations

import importlib
import inspect

import pytest

from fabricops_kit import profile_table


def _rows(dataframe):
    return {row["COLUMN_NAME"]: row.asDict() for row in dataframe.collect()}


def test_profile_table_public_signature_and_removed_symbols():
    """Expose only the consolidated signature."""
    import fabricops_kit
    import fabricops_kit.pipeline as pipeline

    assert str(inspect.signature(profile_table)) == (
        "(*, dataframe=None, target: 'str | None' = None, schema: 'str | None' = None, "
        "table_name: 'str | None' = None, table_id: 'str | None' = None, frequency_columns=None, "
        "frequency_top_n: 'int | None' = None, frequency_max_distinct_percent: 'float | None' = 80.0)"
    )
    for name in ("profile_dataframe", "profile_frequency_distribution", "profile_and_register_table"):
        assert not hasattr(fabricops_kit, name)
        assert not hasattr(pipeline, name)


def test_dataframe_only_profiles_without_metadata_writes_and_prints(spark_session, monkeypatch, capsys):
    """Keep identity-free profiling entirely non-persistent."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    source = spark_session.createDataFrame([(1, "A"), (2, "A"), (None, None)], ["amount", "status"])
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: pytest.fail("must not resolve metadata"))
    monkeypatch.setattr(module, "write_lakehouse_table_core", lambda *a, **k: pytest.fail("must not write"))

    result = profile_table(dataframe=source, frequency_columns=["status"])

    assert set(result) == {"profile", "frequency_profile"}
    assert _rows(result["profile"])["amount"]["ROW_COUNT"] == 3
    frequency = result["frequency_profile"].collect()
    assert {(row.VALUE, row.FREQUENCY_COUNT) for row in frequency} == {(None, 1), ("A", 2)}
    assert "No Data Catalogue or profiling metadata will be persisted" in capsys.readouterr().out


def test_dataframe_only_raw_file_shape_does_not_invent_identity(spark_session):
    """Return canonical statistics without identity columns for raw file data."""
    source = spark_session.createDataFrame([("file-row",)], ["raw_value"])
    result = profile_table(dataframe=source, frequency_columns=[])
    assert result["profile"].columns == [
        "COLUMN_NAME", "DATA_TYPE", "ROW_COUNT", "NON_NULL_COUNT", "NULL_COUNT", "NULL_PERCENT",
        "DISTINCT_COUNT", "DISTINCT_PERCENT", "MEAN", "STDDEV", "MIN_VALUE", "PERCENTILE_25",
        "MEDIAN", "PERCENTILE_75", "MAX_VALUE",
    ]
    assert result["frequency_profile"] is None


@pytest.mark.parametrize(
    "kwargs,message",
    [
        ({}, "Provide dataframe"),
        ({"table_id": "x", "target": "source", "table_name": "orders"}, "cannot be combined"),
        ({"target": "source"}, "both target and table_name"),
    ],
)
def test_profile_table_rejects_invalid_identity_forms(kwargs, message):
    """Reject conflicting, incomplete, or absent inputs."""
    with pytest.raises(ValueError, match=message):
        profile_table(**kwargs)


def test_dataframe_plus_identity_does_not_reread(spark_session, monkeypatch, capsys):
    """Associate the supplied frame with identity without a physical read."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    source = spark_session.createDataFrame([(1,)], ["value"])
    identity = {"table_id": "lakehouse||source||dbo||orders", "target": "source", "schema": "dbo", "table_name": "orders", "store_kind": "lakehouse"}
    monkeypatch.setattr(module, "resolve_fabric_context", lambda: ({}, "dev", {}))
    monkeypatch.setattr(module, "resolve_catalogue_table_identity", lambda *a, **k: dict(identity))
    monkeypatch.setattr(module, "read_lakehouse_table", lambda *a, **k: pytest.fail("must not reread"))
    monkeypatch.setattr(module, "_canonical_profiled_dataframe", lambda profile, **k: profile)
    monkeypatch.setattr(module, "write_lakehouse_table_core", lambda *a, **k: None)
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *a: None)
    monkeypatch.setattr(module, "_replace_frequency_rows", lambda **k: None)
    monkeypatch.setattr(module, "_catalogue_dataframe_from_profiled", lambda *a, **k: object())
    monkeypatch.setattr(module, "_upsert_catalogue_identities", lambda **k: None)

    result = profile_table(dataframe=source, table_id=identity["table_id"], frequency_columns=[])

    assert result["profile"].count() == 1
    assert "profiling supplied DataFrame against governed table" in capsys.readouterr().out


def test_profile_catalogue_refresh_preserves_target_processing(monkeypatch):
    """Keep table processing fields when structural profiling supplies null values."""
    module = importlib.import_module("fabricops_kit.pipeline.profile_table")
    updates = []

    class Merge:
        def alias(self, _name):
            return self

        def merge(self, *_args):
            return self

        def whenMatchedUpdate(self, *, set):
            updates.append(set)
            return self

        def whenNotMatchedInsertAll(self):
            return self

        def whenNotMatchedBySourceUpdate(self, **_kwargs):
            return self

        def execute(self):
            return None

    class Catalogue:
        def select(self, *_columns):
            return self

        def first(self):
            return {"environment_name": "dev", "table_id": "target-id"}

        def alias(self, _name):
            return self

    import sys
    import types

    delta_module = types.ModuleType("delta")
    tables_module = types.ModuleType("delta.tables")
    tables_module.DeltaTable = type("DeltaTable", (), {"forPath": staticmethod(lambda *_args: Merge())})
    monkeypatch.setitem(sys.modules, "delta", delta_module)
    monkeypatch.setitem(sys.modules, "delta.tables", tables_module)
    monkeypatch.setattr(module, "resolve_configured_lakehouse_table", lambda *_a, **_k: (None, None, None, "/metadata/catalogue"))
    monkeypatch.setattr(module, "metadata_table_physical_schema", lambda *_a: None)

    module._upsert_catalogue_identities(
        catalogue_df=Catalogue(), config={}, env="dev", spark_session=object()
    )

    assert updates[0]["load_strategy"] == "coalesce(source.load_strategy, target.load_strategy)"
    assert updates[0]["load_strategy_parameters_json"] == (
        "coalesce(source.load_strategy_parameters_json, target.load_strategy_parameters_json)"
    )
