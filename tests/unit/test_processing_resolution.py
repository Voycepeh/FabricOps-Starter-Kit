"""Tests for environment-aware processing definition resolution."""
# ruff: noqa: D101, D102, D103, D107

from __future__ import annotations

from types import SimpleNamespace

import pytest

from fabricops_kit.pipeline import shared
from fabricops_kit.pipeline.read_pipeline_prep import _partition_scope

pytestmark = pytest.mark.unit


class Frame:
    def __init__(self, rows):
        self.rows = rows

    def collect(self):
        return [SimpleNamespace(**row) for row in self.rows]


def contract(strategy="scd1", *, version=3):
    processing = {"load_strategy": strategy}
    if strategy == "scd1":
        processing["key_columns"] = ["student_id"]
    return {
        "contract_id": "contract",
        "contract_version": version,
        "table_id": "students",
        "contract_payload": {"table": {"table_id": "students", "processing": processing}},
    }


def catalogue(strategy="overwrite"):
    return Frame([{
        "metadata_level": "table", "table_id": "students", "environment_name": "dev",
        "is_active": True, "load_strategy": strategy,
        "load_strategy_parameters_json": "{}",
    }])


def test_development_uses_current_notebook_authoring_without_catalogue(monkeypatch):
    monkeypatch.setattr(shared, "read_lakehouse_table_core", lambda *args, **kwargs: pytest.fail("Catalogue read"))
    resolved = shared.resolve_table_processing_definition(
        object(), "dev", "students", authored_processing={"load_strategy": "overwrite"}
    )
    assert resolved == {"load_strategy": "overwrite", "source": "current_authoring"}


def test_development_override_uses_frozen_contract(monkeypatch):
    monkeypatch.setattr(shared, "_resolve_data_contract_version", lambda *args, **kwargs: contract())
    resolved = shared.resolve_table_processing_definition(
        object(), "dev", "students",
        context={"data_contract_overrides": {"students": {"contract_id": "contract", "contract_version": 3}}},
        authored_processing={"load_strategy": "append"},
    )
    assert resolved["load_strategy"] == "scd1"
    assert resolved["source"] == "data_contract"
    assert resolved["contract_version"] == 3


def test_development_current_authoring_requires_notebook_definition():
    with pytest.raises(ValueError, match="authored processing"):
        shared.resolve_table_processing_definition(object(), "dev", "students")


def test_production_uses_active_contract_and_never_reads_catalogue(monkeypatch):
    monkeypatch.setattr(shared, "resolve_active_data_contract", lambda *args, **kwargs: contract())
    monkeypatch.setattr(shared, "read_lakehouse_table_core", lambda *args, **kwargs: pytest.fail("Catalogue read"))
    assert shared.resolve_table_processing_definition(object(), "prod", "students")["load_strategy"] == "scd1"


def test_production_missing_active_contract_fails(monkeypatch):
    def fail(*args, **kwargs):
        raise ValueError("No active Data Contract")
    monkeypatch.setattr(shared, "resolve_active_data_contract", fail)
    with pytest.raises(ValueError, match="No active"):
        shared.resolve_table_processing_definition(object(), "prod", "students")


@pytest.mark.parametrize("processing", [None, {}, {"load_strategy": "merge"}, {"load_strategy": "scd2", "key_columns": ["id"]}])
def test_production_rejects_missing_or_malformed_frozen_processing(monkeypatch, processing):
    frozen = contract()
    frozen["contract_payload"]["table"]["processing"] = processing
    monkeypatch.setattr(shared, "resolve_active_data_contract", lambda *args, **kwargs: frozen)
    with pytest.raises(ValueError):
        shared.resolve_table_processing_definition(object(), "prod", "students")


def changes(**overrides):
    return {
        "changed": True,
        "first_observation": False,
        "new_partitions": [],
        "changed_partitions": [],
        "removed_partitions": [],
        "reappeared_partitions": [],
        "partition_column": "business_date",
        **overrides,
    }


@pytest.mark.parametrize("strategy", ["overwrite", "append", "scd1", "scd2"])
def test_first_observation_is_full(strategy):
    assert _partition_scope(
        changes(first_observation=True), {"load_strategy": strategy, **processing_parameters(strategy)}, "business_date"
    )["read_mode"] == "full_dataset"


def processing_parameters(strategy):
    if strategy == "overwrite":
        return {"partition_column": "business_date"}
    if strategy == "scd1":
        return {"key_columns": ["student_id"]}
    if strategy == "scd2":
        return {"key_columns": ["student_id"], "effective_column": "modified_at"}
    return {}


def test_no_change_is_skip():
    assert _partition_scope(changes(changed=False), {"load_strategy": "append"}, "business_date")["read_mode"] == "skip"


@pytest.mark.parametrize("strategy", ["overwrite", "append", "scd1", "scd2"])
def test_new_partition_is_incremental(strategy):
    scope = _partition_scope(
        changes(new_partitions=["2026-08-21"]),
        {"load_strategy": strategy, **processing_parameters(strategy)}, "business_date",
    )
    assert scope == {"read_mode": "incremental_subset", "scope": {"type": "partition", "column": "business_date", "values": ["2026-08-21"]}}


@pytest.mark.parametrize("field", ["changed_partitions", "reappeared_partitions"])
def test_append_rejects_existing_partition_changes(field):
    with pytest.raises(ValueError, match="append is unsafe"):
        _partition_scope(changes(**{field: ["2026-08-21"]}), {"load_strategy": "append"}, "business_date")


@pytest.mark.parametrize("strategy", ["scd1", "scd2"])
def test_scd_existing_partition_change_is_incremental(strategy):
    scope = _partition_scope(
        changes(changed_partitions=["2026-08-21"]),
        {"load_strategy": strategy, **processing_parameters(strategy)}, "business_date",
    )
    assert scope["read_mode"] == "incremental_subset"


@pytest.mark.parametrize("strategy", ["append", "scd1", "scd2"])
def test_removed_partition_rejects_implicit_delete(strategy):
    with pytest.raises(ValueError, match="delete semantics"):
        _partition_scope(
            changes(removed_partitions=["2026-08-21"]),
            {"load_strategy": strategy, **processing_parameters(strategy)}, "business_date",
        )


def test_partition_strategy_requires_change_rule_on_same_column():
    with pytest.raises(ValueError, match="active change rule"):
        _partition_scope(changes(partition_column=None), {"load_strategy": "overwrite"}, "business_date")


def test_scd2_default_tracking_excludes_ingestion_and_audit_columns():
    tracked = shared.resolve_scd2_tracked_columns(
        ["student_id", "name", "status", "effective_at", "ingested_at_utc", "_fabricops_created_at", "loaded_at"],
        {"key_columns": ["student_id"], "effective_column": "effective_at"},
    )
    assert tracked == ["name", "status"]
