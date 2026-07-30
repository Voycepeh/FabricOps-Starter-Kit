"""Behavioural tests for minimal Data Contract registration."""

from __future__ import annotations

from datetime import date, datetime
import importlib

import pytest

import fabricops_kit
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
from fabricops_kit.widgets import widget_register_data_contract as public_widget
from fabricops_kit.widgets.widget_register_data_contract import (
    _agreement_details,
    _base_dataset_label,
    _contract_id,
    _dataset_options,
    _latest_catalogue_rows,
    _normalize_initial_ids,
)

pytestmark = pytest.mark.unit


def test_agreement_resolution_accepts_state_explicit_id_and_precedence():
    """Agreement state is canonical, while a non-empty explicit ID wins."""
    assert _agreement_details({"agreement_id": " agreement-1 ", "agreement_name": "Customers"}, None) == (
        "agreement-1", "Customers",
    )
    assert _agreement_details(None, " agreement-2 ") == ("agreement-2", "agreement-2")
    assert _agreement_details({"agreement_id": "state-id"}, " explicit-id ")[0] == "explicit-id"


def test_agreement_resolution_supports_selected_widget_state_and_rejects_missing():
    """The selected agreement record is resolved locally without a metadata read."""
    class Selection:
        value = " agreement-3 "

    state = {
        "existing_record": Selection(),
        "existing_records_by_id": {"agreement-3": {"agreement_id": " agreement-3 ", "agreement_name": "Orders"}},
    }
    # Selection values are normally canonical keys; direct fallback still trims.
    state["existing_record"].value = "agreement-3"
    assert _agreement_details(state, None) == ("agreement-3", "Orders")
    with pytest.raises(ValueError, match="valid agreement_id is required"):
        _agreement_details({}, "  ")


def test_initial_ids_are_trimmed_deduplicated_and_require_a_sequence():
    """Initial selection normalization never creates identities."""
    assert _normalize_initial_ids([" one ", "two", "one", "", None]) == ["one", "two"]
    with pytest.raises(TypeError, match="non-string sequence"):
        _normalize_initial_ids("one")


def test_dataset_labels_omit_blank_schema_and_disambiguate_progressively():
    """Physical labels stay readable and canonical keys remain selector values."""
    rows = [
        {"metadata_table_key": "key-a", "store_type": "Lakehouse", "layer": "raw", "schema_name": "sales", "table_name": "orders"},
        {"metadata_table_key": "key-b", "store_type": "Warehouse", "layer": "raw", "schema_name": "sales", "table_name": "orders"},
        {"metadata_table_key": "key-c", "store_type": "Lakehouse", "layer": "raw", "schema_name": "", "table_name": "customers"},
    ]
    options = _dataset_options(rows)
    assert _base_dataset_label(rows[2]) == "raw / customers"
    assert ("Lakehouse — raw / sales / orders", "key-a") in options
    assert ("Warehouse — raw / sales / orders", "key-b") in options
    assert {value for _label, value in options} == {"key-a", "key-b", "key-c"}


def test_final_label_fallback_is_deterministic_and_does_not_collapse_keys():
    """Equal store coordinates gain a stable shortened-key suffix."""
    rows = [
        {"metadata_table_key": "logical-dataset-aaaaaaaa", "store_type": "Lakehouse", "layer": "raw", "schema_name": "sales", "table_name": "orders"},
        {"metadata_table_key": "logical-dataset-bbbbbbbb", "store_type": "Lakehouse", "layer": "raw", "schema_name": "sales", "table_name": "orders"},
    ]
    first = _dataset_options(rows)
    assert first == _dataset_options(list(reversed(rows)))
    assert len(first) == 2
    assert all("…" in label for label, _value in first)


def test_latest_catalogue_observation_is_active_environment_only_and_deterministic(spark_session):
    """History does not duplicate options and newest commit wins with stable ties."""
    old = datetime(2026, 1, 1)
    new = datetime(2026, 2, 1)
    frame = spark_session.createDataFrame([
        ("one", "old", "dev", "Lakehouse", "raw", "sales", "orders", old),
        ("one", "new-a", "dev", "Lakehouse", "raw", "sales", "orders", new),
        ("one", "new-b", "dev", "Lakehouse", "raw", "sales", "orders", new),
        ("one", "prod", "prod", "Lakehouse", "raw", "sales", "orders", new),
        ("two", "second", "dev", "Warehouse", "curated", "finance", "summary", new),
    ], "metadata_table_key string, schema_fingerprint string, environment_name string, store_type string, layer string, schema_name string, table_name string, _committed_at timestamp")
    rows = _latest_catalogue_rows(frame, "dev")
    assert [row["metadata_table_key"] for row in rows] == ["one", "two"]
    assert rows[0]["schema_fingerprint"] == "new-b"


def test_contract_identity_is_deterministic_and_environment_independent():
    """Dev and Prod observations of one logical key map to one membership."""
    assert _contract_id("agreement", "logical-key") == _contract_id("agreement", "logical-key")
    assert _contract_id("agreement", "logical-key") != _contract_id("agreement", "other-key")
    assert "dev" not in _contract_id("agreement", "logical-key")


@pytest.fixture
def contract_widget_runtime(monkeypatch, spark_session):
    """Provide real widgets with in-memory Spark metadata tables."""
    module = importlib.import_module("fabricops_kit.widgets.widget_register_data_contract")
    catalogue = spark_session.createDataFrame([
        ("key-one", "fp-old", "dev", "Lakehouse", "raw", "sales", "orders", datetime(2026, 1, 1)),
        ("key-one", "fp-new", "dev", "Lakehouse", "raw", "sales", "orders", datetime(2026, 2, 1)),
        ("key-two", "fp-two", "dev", "Warehouse", "curated", "finance", "summary", datetime(2026, 2, 1)),
        ("key-prod", "fp-prod", "prod", "Lakehouse", "raw", "sales", "prod_only", datetime(2026, 2, 1)),
    ], "metadata_table_key string, schema_fingerprint string, environment_name string, store_type string, layer string, schema_name string, table_name string, _committed_at timestamp")
    contract_schema = metadata_table_schema_registry()["METADATA_DATA_CONTRACT"]
    tables = {
        "METADATA_DATA_CATALOGUE": catalogue,
        "METADATA_DATA_CONTRACT": spark_session.createDataFrame([], contract_schema),
    }

    monkeypatch.setattr(module, "resolve_fabric_context", lambda **_kwargs: ({"config": True}, "dev", {}))
    monkeypatch.setattr(module, "get_spark_session", lambda value=None: value or spark_session)
    monkeypatch.setattr(module, "read_lakehouse_table_core", lambda name, **_kwargs: tables[name])

    def write(frame, name, **_kwargs):
        tables[name] = frame

    monkeypatch.setattr(module, "write_lakehouse_table_core", write)
    monkeypatch.setattr(module, "get_current_audit_timestamp", lambda **_kwargs: "2026-07-30T12:00:00+00:00")
    monkeypatch.setattr(module, "build_runtime_audit_fields", lambda **_kwargs: {
        "_committed_by": "tester", "_committed_at": datetime(2026, 7, 30, 12),
        "_workspace_id": "workspace-id", "_workspace_name": "workspace",
        "_notebook_id": "notebook-id", "_notebook_name": "notebook",
        "_metadata_lakehouse_name": "metadata", "_activity_id": "activity-id",
    })
    monkeypatch.setattr("IPython.display.display", lambda *_args, **_kwargs: None)
    return module, tables


def test_widget_filters_initial_selection_and_returns_clear_state(contract_widget_runtime, spark_session):
    """Only active-environment catalogue identities are available and writable."""
    _module, _tables = contract_widget_runtime
    state = public_widget(
        agreement_id=" agreement-1 ", metadata_ids=[" key-one ", "unknown", "key-prod"],
        spark_session=spark_session,
    )
    assert state["environment_name"] == "dev"
    assert set(state["available_metadata_ids"]) == {"key-one", "key-two"}
    assert state["selected_metadata_ids"] == ["key-one"]
    assert state["unknown_initial_metadata_ids"] == ["unknown", "key-prod"]
    assert state["saved_metadata_ids"] == []
    assert set(state["_controls"]) >= {"datasets", "save", "status"}


def test_save_writes_minimal_audited_rows_and_get_rows(contract_widget_runtime, spark_session):
    """Save writes one latest-fingerprint draft per selected logical key."""
    _module, tables = contract_widget_runtime
    state = public_widget(
        agreement_id="agreement-1", metadata_ids=["key-one", "key-two"],
        spark_session=spark_session,
    )
    state["_controls"]["save"].click()
    rows = sorted(state["get_rows"](), key=lambda row: row["metadata_table_key"])
    assert [row["metadata_table_key"] for row in rows] == ["key-one", "key-two"]
    assert rows[0]["schema_fingerprint"] == "fp-new"
    assert all(row["contract_version"] == "1" for row in rows)
    assert all(row["contract_status"] == "draft" for row in rows)
    assert all(row["effective_from"] == date(2026, 7, 30) for row in rows)
    assert all(row["effective_to"] is None and row["contract_payload_json"] == "{}" for row in rows)
    assert all(row["_committed_by"] == "tester" and row["_activity_id"] == "activity-id" for row in rows)
    assert state["saved_contract_ids"] == [_contract_id("agreement-1", key) for key in ["key-one", "key-two"]]
    assert "Saved 2 logical datasets" in state["_controls"]["status"].value
    assert tables["METADATA_DATA_CONTRACT"].count() == 2


def test_resave_add_and_deselect_preserve_required_rows(contract_widget_runtime, spark_session):
    """Draft replacement is agreement-scoped and never removes non-draft rows."""
    _module, tables = contract_widget_runtime
    schema = metadata_table_schema_registry()["METADATA_DATA_CONTRACT"]
    base = {
        "schema_fingerprint": "fp", "contract_version": "1", "effective_from": date(2026, 1, 1),
        "effective_to": None, "contract_payload_json": "{}", "_committed_by": "old",
        "_committed_at": datetime(2026, 1, 1), "_workspace_id": "w", "_workspace_name": "w",
        "_notebook_id": "n", "_notebook_name": "n", "_metadata_lakehouse_name": "m", "_activity_id": "a",
    }
    tables["METADATA_DATA_CONTRACT"] = spark_session.createDataFrame([
        {**base, "contract_id": "existing", "agreement_id": "agreement-1", "metadata_table_key": "key-one", "contract_status": "draft"},
        {**base, "contract_id": "approved", "agreement_id": "agreement-1", "metadata_table_key": "legacy", "contract_status": "approved"},
        {**base, "contract_id": "other", "agreement_id": "agreement-2", "metadata_table_key": "other", "contract_status": "draft"},
    ], schema)
    state = public_widget(agreement_id="agreement-1", metadata_ids=["key-one"], spark_session=spark_session)
    state["_controls"]["save"].click()
    assert tables["METADATA_DATA_CONTRACT"].count() == 3
    state["_controls"]["datasets"].value = ("key-one", "key-two")
    state["_controls"]["save"].click()
    assert tables["METADATA_DATA_CONTRACT"].count() == 4
    state["_controls"]["datasets"].value = ("key-two",)
    state["_controls"]["save"].click()
    rows = [row.asDict() for row in tables["METADATA_DATA_CONTRACT"].collect()]
    assert {(row["agreement_id"], row["metadata_table_key"], row["contract_status"]) for row in rows} == {
        ("agreement-1", "key-two", "draft"),
        ("agreement-1", "legacy", "approved"),
        ("agreement-2", "other", "draft"),
    }


def test_empty_catalogue_is_non_breaking_and_does_not_save_implicitly(contract_widget_runtime, spark_session):
    """An empty catalogue explains the prerequisite and waits for explicit save."""
    _module, tables = contract_widget_runtime
    tables["METADATA_DATA_CATALOGUE"] = tables["METADATA_DATA_CATALOGUE"].limit(0)
    state = public_widget(agreement_id="agreement-1", spark_session=spark_session)
    assert state["available_metadata_ids"] == []
    assert "No registered datasets" in state["_controls"]["status"].value
    assert tables["METADATA_DATA_CONTRACT"].count() == 0


def test_missing_ipywidgets_is_actionable_and_non_destructive(monkeypatch, capsys):
    """Missing optional UI support returns before context reads or writes."""
    module = importlib.import_module("fabricops_kit.widgets.widget_register_data_contract")
    monkeypatch.setattr(module, "require_ipywidgets", lambda: (_ for _ in ()).throw(ModuleNotFoundError("Install widgets.")))
    state = public_widget(agreement_id="agreement-1", metadata_ids=["one"])
    assert state["agreement_id"] == "agreement-1"
    assert state["unknown_initial_metadata_ids"] == ["one"]
    assert state["get_rows"]() == []
    assert "Install widgets" in state["error"]
    assert "registration unavailable" in capsys.readouterr().out


def test_public_exports_expose_preview_callable():
    """Normal package paths expose one public callable without aliases."""
    assert fabricops_kit.widget_register_data_contract is public_widget
    assert "fabricops_kit.widgets.widget_register_data_contract.widget_register_data_contract" in importlib.import_module(
        "fabricops_kit.public_api"
    ).PREVIEW_PUBLIC_API
