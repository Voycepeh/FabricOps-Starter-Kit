"""Tests for environment-aware processing definition resolution."""
# ruff: noqa: D101, D102, D103, D107

from __future__ import annotations

from types import SimpleNamespace

import pytest

from fabricops_kit.pipeline import shared

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
        "contract_payload": {"table": {
            "table_id": "students",
            "processing": processing,
            "writer": {"notebook_id": "notebook-1", "notebook_name": "02_pipeline"},
        }},
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
    assert resolved == {
        "load_strategy": "overwrite",
        "source": "current_authoring",
        "processing_mode": "development_authoring",
        "authored_processing": {"load_strategy": "overwrite"},
        "governed_processing": None,
    }


def test_development_override_uses_frozen_contract(monkeypatch):
    monkeypatch.setattr(shared, "_resolve_data_contract_version", lambda *args, **kwargs: contract())
    resolved = shared.resolve_table_processing_definition(
        object(), "dev", "students",
        context={"data_contract_overrides": {"students": {"contract_id": "contract", "contract_version": 3}}},
        authored_processing={"load_strategy": "scd1", "key_columns": ["student_id"]},
    )
    assert resolved["load_strategy"] == "scd1"
    assert resolved["source"] == "data_contract"
    assert resolved["contract_version"] == 3
    assert resolved["processing_mode"] == "development_validation"
    assert resolved["authored_processing"] == resolved["governed_processing"]


@pytest.mark.parametrize(
    "authored",
    [
        {"load_strategy": "overwrite"},
        {"load_strategy": "scd1", "key_columns": ["other_id"]},
    ],
)
def test_development_override_rejects_engineering_processing_drift(monkeypatch, authored):
    monkeypatch.setattr(shared, "_resolve_data_contract_version", lambda *args, **kwargs: contract())
    with pytest.raises(ValueError, match="Processing mismatch detected.*Engineering proposes"):
        shared.resolve_table_processing_definition(
            object(), "dev", "students",
            context={"data_contract_overrides": {"students": {"contract_id": "contract", "contract_version": 3}}},
            authored_processing=authored,
        )


def test_development_current_authoring_requires_notebook_definition():
    with pytest.raises(ValueError, match="authored processing"):
        shared.resolve_table_processing_definition(object(), "dev", "students")


def test_production_uses_active_contract_and_never_reads_catalogue(monkeypatch):
    monkeypatch.setattr(shared, "resolve_active_data_contract", lambda *args, **kwargs: contract())
    monkeypatch.setattr(shared, "read_lakehouse_table_core", lambda *args, **kwargs: pytest.fail("Catalogue read"))
    resolved = shared.resolve_table_processing_definition(
        object(), "prod", "students",
        authored_processing={"load_strategy": "scd1", "key_columns": ["student_id"]},
    )
    assert resolved["load_strategy"] == "scd1"
    assert resolved["owner_notebook_id"] == "notebook-1"
    assert resolved["processing_mode"] == "production_enforcement"


def test_production_missing_active_contract_fails(monkeypatch):
    def fail(*args, **kwargs):
        raise ValueError("No active Data Contract")
    monkeypatch.setattr(shared, "resolve_active_data_contract", fail)
    with pytest.raises(ValueError, match="No active"):
        shared.resolve_table_processing_definition(
            object(), "prod", "students", authored_processing={"load_strategy": "overwrite"}
        )


@pytest.mark.parametrize("processing", [None, {}, {"load_strategy": "merge"}, {"load_strategy": "scd2", "key_columns": ["id"]}])
def test_production_rejects_missing_or_malformed_frozen_processing(monkeypatch, processing):
    frozen = contract()
    frozen["contract_payload"]["table"]["processing"] = processing
    monkeypatch.setattr(shared, "resolve_active_data_contract", lambda *args, **kwargs: frozen)
    with pytest.raises(ValueError):
        shared.resolve_table_processing_definition(
            object(), "prod", "students", authored_processing={"load_strategy": "overwrite"}
        )


def test_scd2_default_tracking_excludes_ingestion_and_audit_columns():
    tracked = shared.resolve_scd2_tracked_columns(
        ["student_id", "name", "status", "effective_at", "ingested_at_utc", "_fabricops_created_at", "loaded_at"],
        {"key_columns": ["student_id"], "effective_column": "effective_at"},
    )
    assert tracked == ["name", "status"]
