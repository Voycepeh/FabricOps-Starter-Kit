"""Behavioural tests for immutable Data Contract inventory snapshots."""

from __future__ import annotations

from datetime import datetime, timedelta
import importlib

import pytest

import fabricops_kit
from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
from fabricops_kit.widgets import widget_register_data_contract as public_widget
from fabricops_kit.widgets.widget_register_data_contract import (
    _agreement_details,
    _base_dataset_label,
    _dataset_options,
    _latest_catalogue_rows,
    _latest_snapshot,
    _normalize_initial_ids,
    _deduplicate_memberships,
)

pytestmark = pytest.mark.unit


def test_agreement_and_initial_identity_normalization():
    """Explicit IDs win and optional identities are trimmed and unique."""
    assert _agreement_details({"agreement_id": " state ", "agreement_name": "Customers"}, None) == (
        "state", "Customers",
    )
    assert _agreement_details({"agreement_id": "state"}, " explicit ")[0] == "explicit"
    assert _normalize_initial_ids([" one ", "two", "one", "", None]) == ["one", "two"]
    with pytest.raises(ValueError, match="valid agreement_id"):
        _agreement_details({}, " ")
    with pytest.raises(TypeError, match="non-string sequence"):
        _normalize_initial_ids("one")


def test_dataset_labels_remain_readable_unique_and_canonical():
    """Physical labels omit blanks and progressively disambiguate duplicate locations."""
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


def test_latest_catalogue_and_snapshot_resolution_are_deterministic(spark_session):
    """Newest observations and headers win with stable identity tie-breaking."""
    old = datetime(2026, 1, 1)
    new = datetime(2026, 2, 1)
    catalogue = spark_session.createDataFrame([
        ("one", "old", "dev", "Lakehouse", "raw", "sales", "orders", old),
        ("one", "new-a", "dev", "Lakehouse", "raw", "sales", "orders", new),
        ("one", "new-b", "dev", "Lakehouse", "raw", "sales", "orders", new),
        ("one", "prod", "prod", "Lakehouse", "raw", "sales", "orders", new),
    ], "metadata_table_key string, schema_fingerprint string, environment_name string, store_type string, layer string, schema_name string, table_name string, _committed_at timestamp")
    assert _latest_catalogue_rows(catalogue, "dev")[0]["schema_fingerprint"] == "new-b"
    memberships = spark_session.createDataFrame([
        ("snapshot-old", "agreement", "one", old), ("snapshot-a", "agreement", "one", new),
        ("snapshot-b", "agreement", "two", new), ("other", "other", "one", new),
    ], "contract_snapshot_id string, agreement_id string, metadata_table_key string, snapshot_saved_at timestamp")
    summary, rows = _latest_snapshot(memberships, "agreement")
    assert summary["contract_snapshot_id"] == "snapshot-b"
    assert [row["metadata_table_key"] for row in rows] == ["two"]
    assert _latest_snapshot(memberships, "missing") == (None, [])


def test_snapshot_memberships_do_not_combine_history_and_deduplicate(spark_session):
    """Only one requested snapshot contributes unique logical memberships."""
    frame = spark_session.createDataFrame([
        ("old", "one", "old-fp"), ("latest", "one", "fp"),
        ("latest", "one", "duplicate"), ("latest", "two", "two-fp"),
    ], "contract_snapshot_id string, metadata_table_key string, schema_fingerprint string")
    rows = _deduplicate_memberships([
        row.asDict(recursive=True) for row in frame.filter("contract_snapshot_id = 'latest'").collect()
    ])
    assert [row["metadata_table_key"] for row in rows] == ["one", "two"]


@pytest.fixture
def snapshot_runtime(monkeypatch, spark_session):
    """Provide real widgets and append-only in-memory metadata tables."""
    module = importlib.import_module("fabricops_kit.widgets.widget_register_data_contract")
    registry = metadata_table_schema_registry()
    catalogue = spark_session.createDataFrame([
        ("key-one", "fp-old", "dev", "Lakehouse", "raw", "sales", "orders", datetime(2026, 1, 1)),
        ("key-one", "fp-new", "dev", "Lakehouse", "raw", "sales", "orders", datetime(2026, 2, 1)),
        ("key-two", "fp-two", "dev", "Warehouse", "curated", "finance", "summary", datetime(2026, 2, 1)),
        ("key-three", "fp-three", "dev", "Lakehouse", "raw", "", "customers", datetime(2026, 2, 1)),
        ("key-prod", "fp-prod", "prod", "Lakehouse", "raw", "sales", "prod", datetime(2026, 2, 1)),
    ], "metadata_table_key string, schema_fingerprint string, environment_name string, store_type string, layer string, schema_name string, table_name string, _committed_at timestamp")
    tables = {
        "METADATA_DATA_CATALOGUE": catalogue,
        "METADATA_DATA_CONTRACT": spark_session.createDataFrame([], registry["METADATA_DATA_CONTRACT"]),
    }
    writes: list[tuple[str, str, list[dict]]] = []
    tick = {"value": 0}

    monkeypatch.setattr(module, "resolve_fabric_context", lambda **_kwargs: ({"config": True}, "dev", {}))
    monkeypatch.setattr(module, "get_spark_session", lambda value=None: value or spark_session)
    monkeypatch.setattr(module, "read_lakehouse_table_core", lambda name, **_kwargs: tables[name])

    def write(frame, name, *, mode, **_kwargs):
        rows = [row.asDict(recursive=True) for row in frame.collect()]
        writes.append((name, mode, rows))
        tables[name] = tables[name].unionByName(frame)

    def audit(**_kwargs):
        tick["value"] += 1
        committed_at = datetime(2026, 7, 30, 12) + timedelta(seconds=tick["value"])
        return {
            "_committed_by": "tester", "_committed_at": committed_at,
            "_workspace_id": "workspace-id", "_workspace_name": "workspace",
            "_notebook_id": "notebook-id", "_notebook_name": "notebook",
            "_metadata_lakehouse_name": "metadata", "_activity_id": "activity-id",
        }

    monkeypatch.setattr(module, "write_lakehouse_table_core", write)
    monkeypatch.setattr(module, "build_runtime_audit_fields", audit)
    monkeypatch.setattr("IPython.display.display", lambda *_args, **_kwargs: None)
    return module, tables, writes


def _seed_snapshot(spark, tables, snapshot_id, agreement_id, saved_at, keys):
    """Append one test snapshot directly to in-memory tables."""
    registry = metadata_table_schema_registry()
    audit = {
        "_committed_by": "seed", "_committed_at": saved_at,
        "_workspace_id": "w", "_workspace_name": "w", "_notebook_id": "n",
        "_notebook_name": "n", "_metadata_lakehouse_name": "m", "_activity_id": "a",
    }
    rows = [{
        "contract_snapshot_id": snapshot_id, "agreement_id": agreement_id,
        "metadata_table_key": key, "schema_fingerprint": f"fp-{key}",
        "snapshot_saved_at": saved_at, **audit,
    } for key in keys]
    if rows:
        tables["METADATA_DATA_CONTRACT"] = tables["METADATA_DATA_CONTRACT"].unionByName(
            spark.createDataFrame(rows, registry["METADATA_DATA_CONTRACT"]),
        )


def test_no_snapshot_is_empty_and_initial_ids_extend_only_in_memory(snapshot_runtime, spark_session):
    """No history starts empty; valid caller IDs are unsaved additions only."""
    _module, _tables, writes = snapshot_runtime
    state = public_widget(
        agreement_id="agreement", metadata_ids=["key-one", "key-prod", "unknown"],
        spark_session=spark_session,
    )
    assert state["latest_snapshot_id"] is None
    assert state["inventory_metadata_ids"] == ["key-one"]
    assert state["inventory_count"] == 1
    assert state["unknown_initial_metadata_ids"] == ["key-prod", "unknown"]
    assert state["has_unsaved_changes"] is True
    assert writes == []
    assert state["get_snapshot"]() == {"header": None, "memberships": []}


def test_latest_snapshot_loads_without_combining_older_history(snapshot_runtime, spark_session):
    """Opening displays only the newest snapshot and keeps unavailable identities visible."""
    _module, tables, _writes = snapshot_runtime
    _seed_snapshot(spark_session, tables, "old", "agreement", datetime(2026, 1, 1), ["key-one"])
    _seed_snapshot(spark_session, tables, "latest", "agreement", datetime(2026, 2, 1), ["key-two", "historical-key"])
    state = public_widget(agreement_id="agreement", spark_session=spark_session)
    assert state["latest_snapshot_id"] == "latest"
    assert state["inventory_metadata_ids"] == ["historical-key", "key-two"]
    assert "Unavailable catalogue dataset" in dict(state["_controls"]["inventory"].options)["historical-key"]
    assert [row["metadata_table_key"] for row in state["get_rows"]()] == ["historical-key", "key-two"]


def test_agreement_state_selection_reloads_inventory_and_disables_when_empty(
    snapshot_runtime, spark_session,
):
    """Changing the agreement selector reactively loads that agreement's latest snapshot."""
    import ipywidgets as widgets

    _module, tables, writes = snapshot_runtime
    _seed_snapshot(spark_session, tables, "a", "agreement-a", datetime(2026, 1, 1), ["key-one"])
    _seed_snapshot(spark_session, tables, "b", "agreement-b", datetime(2026, 1, 2), ["key-two"])
    selector = widgets.Select(options=[("Select", ""), ("A", "agreement-a"), ("B", "agreement-b")], value="")
    agreement_state = {
        "existing_record": selector,
        "existing_records_by_id": {
            "agreement-a": {"agreement_id": "agreement-a", "agreement_name": "Agreement A"},
            "agreement-b": {"agreement_id": "agreement-b", "agreement_name": "Agreement B"},
        },
    }
    state = public_widget(
        agreement=agreement_state, metadata_ids=["key-three"],
        spark_session=spark_session,
    )
    assert state["agreement_id"] is None
    assert state["inventory_metadata_ids"] == []
    assert state["_controls"]["save"].disabled is True
    assert writes == []

    selector.value = "agreement-a"
    assert state["agreement_id"] == "agreement-a"
    assert state["agreement_label"] == "Agreement A"
    assert state["latest_snapshot_id"] == "a"
    assert state["inventory_metadata_ids"] == ["key-one", "key-three"]
    assert state["_controls"]["save"].disabled is False

    selector.value = "agreement-b"
    assert state["agreement_id"] == "agreement-b"
    assert state["latest_snapshot_id"] == "b"
    assert state["inventory_metadata_ids"] == ["key-two", "key-three"]


def test_inventory_add_remove_and_duplicate_prevention(snapshot_runtime, spark_session):
    """Catalogue additions and inventory removals update one unique in-memory list."""
    _module, _tables, _writes = snapshot_runtime
    state = public_widget(agreement_id="agreement", metadata_ids=["key-one"], spark_session=spark_session)
    controls = state["_controls"]
    controls["available"].value = "key-two"
    controls["add"].click()
    controls["add"].click()
    assert state["inventory_metadata_ids"] == ["key-one", "key-two"]
    controls["inventory"].value = "key-one"
    controls["remove"].click()
    assert state["inventory_metadata_ids"] == ["key-two"]
    assert "key-one" in [value for _label, value in controls["available"].options]
    assert state["inventory_count"] == 1


def test_successive_snapshots_append_complete_inventories_and_preserve_history(snapshot_runtime, spark_session):
    """Five, six, then four dataset saves remain immutable and resolve latest correctly."""
    _module, tables, writes = snapshot_runtime
    extra = spark_session.createDataFrame([
        (f"key-{index}", f"fp-{index}", "dev", "Lakehouse", "raw", "sales", f"table_{index}", datetime(2026, 2, 1))
        for index in range(4, 8)
    ], "metadata_table_key string, schema_fingerprint string, environment_name string, store_type string, layer string, schema_name string, table_name string, _committed_at timestamp")
    tables["METADATA_DATA_CATALOGUE"] = tables["METADATA_DATA_CATALOGUE"].unionByName(extra)
    five = ["key-one", "key-two", "key-three", "key-4", "key-5"]
    state = public_widget(agreement_id="agreement", metadata_ids=five, spark_session=spark_session)
    state["_controls"]["save"].click()
    first_id = state["saved_snapshot_id"]
    state["inventory_metadata_ids"].append("key-6")
    state["_controls"]["save"].click()
    second_id = state["saved_snapshot_id"]
    state["inventory_metadata_ids"] = ["key-one", "key-two", "key-three", "key-4"]
    state["_controls"]["save"].click()
    third_id = state["saved_snapshot_id"]

    assert len({first_id, second_id, third_id}) == 3
    assert tables["METADATA_DATA_CONTRACT"].count() == 5 + 6 + 4
    assert state["latest_snapshot_id"] == third_id
    assert state["inventory_count"] == 4
    assert len(state["get_rows"]()) == 4
    assert {mode for _name, mode, _rows in writes} == {"append"}
    for snapshot_id, count in ((first_id, 5), (second_id, 6), (third_id, 4)):
        rows = [row for row in tables["METADATA_DATA_CONTRACT"].collect() if row.contract_snapshot_id == snapshot_id]
        assert len(rows) == count
        assert {row._committed_at for row in rows} == {row.snapshot_saved_at for row in rows}


def test_empty_inventory_is_rejected_without_writing(snapshot_runtime, spark_session):
    """An empty inventory remains unsupported without creating a second metadata table."""
    _module, tables, writes = snapshot_runtime
    _seed_snapshot(spark_session, tables, "old", "agreement", datetime(2026, 1, 1), ["key-one"])
    state = public_widget(agreement_id="agreement", spark_session=spark_session)
    state["inventory_metadata_ids"] = []
    state["_controls"]["save"].click()
    assert state["inventory_count"] == 0
    assert state["latest_snapshot_id"] == "old"
    assert tables["METADATA_DATA_CONTRACT"].count() == 1
    assert writes == []
    assert "at least one logical dataset" in state["_controls"]["status"].value


def test_other_agreements_and_historical_rows_are_unchanged(snapshot_runtime, spark_session):
    """Saving one agreement only appends and never mutates existing rows."""
    _module, tables, _writes = snapshot_runtime
    _seed_snapshot(spark_session, tables, "a-old", "agreement", datetime(2026, 1, 1), ["key-one"])
    _seed_snapshot(spark_session, tables, "b-old", "other", datetime(2026, 1, 1), ["key-two"])
    original = {(row.contract_snapshot_id, row.agreement_id, row.metadata_table_key) for row in tables["METADATA_DATA_CONTRACT"].collect()}
    state = public_widget(agreement_id="agreement", spark_session=spark_session)
    state["_controls"]["save"].click()
    after = {(row.contract_snapshot_id, row.agreement_id, row.metadata_table_key) for row in tables["METADATA_DATA_CONTRACT"].collect()}
    assert original <= after
    assert ("b-old", "other", "key-two") in after


def test_html_values_are_escaped(snapshot_runtime, spark_session):
    """Agreement and catalogue metadata cannot inject notebook HTML."""
    _module, tables, _writes = snapshot_runtime
    tables["METADATA_DATA_CATALOGUE"] = spark_session.createDataFrame([
        ("html", "fp", "dev", "Lakehouse", "<b>raw</b>", "sales", "orders", datetime(2026, 1, 1)),
    ], "metadata_table_key string, schema_fingerprint string, environment_name string, store_type string, layer string, schema_name string, table_name string, _committed_at timestamp")
    state = public_widget(
        agreement={"agreement_id": "agreement", "agreement_name": "<script>alert(1)</script>"},
        spark_session=spark_session,
    )
    assert "<script>" not in state["_controls"]["agreement"].value
    assert "&lt;script&gt;" in state["_controls"]["agreement"].value
    assert "<b>raw</b>" in dict(state["_controls"]["available"].options)["html"]


def test_missing_widgets_is_actionable_and_non_destructive(monkeypatch, capsys):
    """Missing optional UI support returns before metadata reads or writes."""
    module = importlib.import_module("fabricops_kit.widgets.widget_register_data_contract")
    monkeypatch.setattr(module, "require_ipywidgets", lambda: (_ for _ in ()).throw(ModuleNotFoundError("Install widgets.")))
    state = public_widget(agreement_id="agreement", metadata_ids=["one"])
    assert state["get_rows"]() == []
    assert state["get_snapshot"]() == {"header": None, "memberships": []}
    assert "Install widgets" in state["error"]
    assert "inventory unavailable" in capsys.readouterr().out


def test_public_exports_expose_preview_callable():
    """Normal public paths expose the snapshot inventory callable."""
    assert fabricops_kit.widget_register_data_contract is public_widget
    assert "fabricops_kit.widgets.widget_register_data_contract.widget_register_data_contract" in importlib.import_module(
        "fabricops_kit.public_api"
    ).PREVIEW_PUBLIC_API
