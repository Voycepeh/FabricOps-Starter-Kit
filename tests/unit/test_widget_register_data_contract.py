"""Behavioural tests for immutable Data Contract inventory snapshots."""

from __future__ import annotations

from datetime import datetime, timedelta
import importlib

import pytest

import fabricops_kit
from fabricops_kit.config.metadata_schemas import coerce_metadata_row_types, metadata_table_schema_registry
from fabricops_kit.widgets import widget_register_data_contract as public_widget
from fabricops_kit.widgets.widget_register_data_contract import (
    _agreement_details,
    _base_dataset_label,
    _dataset_options,
    _latest_catalogue_rows,
    _latest_inventory,
    _catalogue_schema_rows,
    _compare_schemas,
    _normalize_initial_ids,
    _deduplicate_memberships,
)

pytestmark = pytest.mark.unit


class _FakeWidget:
    """Small observable widget double matching controls used by the inventory."""

    def __init__(self, *args, value=None, options=None, **kwargs):
        self.children = tuple(args[0]) if args else ()
        self.description = kwargs.get("description", "")
        self.disabled = bool(kwargs.get("disabled", False))
        self.layout = kwargs.get("layout")
        self._value = value
        self._options = []
        self._observers = []
        self._click_handlers = []
        if options is not None:
            self.options = options

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new):
        old = self._value
        self._value = new
        if old != new:
            for callback in list(self._observers):
                callback({"name": "value", "old": old, "new": new})

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, new):
        self._options = list(new or [])
        values = [item[1] if isinstance(item, tuple) else item for item in self._options]
        if self._value not in values:
            self.value = values[0] if values else None

    def observe(self, callback, names=None):
        self._observers.append(callback)

    def on_click(self, callback):
        self._click_handlers.append(callback)

    def click(self):
        if not self.disabled:
            for callback in list(self._click_handlers):
                callback(self)


class _FakeOutput(_FakeWidget):
    """Output double supporting capture contexts and clearing."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def clear_output(self, wait=False):
        self.outputs = []


class _FakeLayout:
    """Record layout keyword arguments used by shared form helpers."""

    def __init__(self, **kwargs):
        self.kwargs = kwargs


class _FakeWidgets:
    """Widget module double for deterministic headless behavior tests."""

    Text = _FakeWidget
    Textarea = _FakeWidget
    Checkbox = _FakeWidget
    Select = _FakeWidget
    HTML = _FakeWidget
    Button = _FakeWidget
    Output = _FakeOutput
    VBox = _FakeWidget
    HBox = _FakeWidget
    GridBox = _FakeWidget
    Layout = _FakeLayout


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
        ("activity-old", "agreement", "one", old), ("activity-a", "agreement", "one", new),
        ("activity-b", "agreement", "two", new), ("other", "other", "one", new),
    ], "_activity_id string, agreement_id string, metadata_table_key string, _committed_at timestamp")
    summary, rows = _latest_inventory(memberships, "agreement")
    assert summary["activity_id"] == "activity-b"
    assert [row["metadata_table_key"] for row in rows] == ["two"]
    assert _latest_inventory(memberships, "missing") == (None, [])


def test_snapshot_memberships_do_not_combine_history_and_deduplicate(spark_session):
    """Only one requested snapshot contributes unique logical memberships."""
    frame = spark_session.createDataFrame([
        ("old", "one", "old-fp"), ("latest", "one", "fp"),
        ("latest", "one", "duplicate"), ("latest", "two", "two-fp"),
    ], "_activity_id string, metadata_table_key string, schema_fingerprint string")
    rows = _deduplicate_memberships([
        row.asDict(recursive=True) for row in frame.filter("_activity_id = 'latest'").collect()
    ])
    assert [row["metadata_table_key"] for row in rows] == ["one", "two"]


def test_schema_lookup_preserves_historical_snapshots_and_active_environment(spark_session):
    """A key and fingerprint recover complete schemas without crossing environments."""
    catalogue = spark_session.createDataFrame([
        ("table", "b", "old", "dev", "beta", "string"),
        ("table", "a", "old", "dev", "alpha", "long"),
        ("table", "a", "new", "dev", "alpha", "decimal"),
        ("table", "a", "old", "prod", "alpha", "long"),
    ], "metadata_table_key string, metadata_column_key string, schema_fingerprint string, environment_name string, column_name string, data_type string")
    assert _catalogue_schema_rows(catalogue, "dev", "table", "old") == [
        {"metadata_column_key": "a", "column_name": "alpha", "data_type": "long"},
        {"metadata_column_key": "b", "column_name": "beta", "data_type": "string"},
    ]
    assert _catalogue_schema_rows(catalogue, "dev", "table", "new") == [
        {"metadata_column_key": "a", "column_name": "alpha", "data_type": "decimal"},
    ]
    assert _catalogue_schema_rows(catalogue, None, "table", "old") == [
        {"metadata_column_key": "a", "column_name": "alpha", "data_type": "long"},
        {"metadata_column_key": "b", "column_name": "beta", "data_type": "string"},
    ]


def test_schema_comparison_uses_stable_keys_for_structural_differences():
    """Stable keys distinguish additions, removals, type changes, and renames."""
    difference = _compare_schemas(
        [
            {"metadata_column_key": "same", "column_name": "old_name", "data_type": "long"},
            {"metadata_column_key": "typed", "column_name": "amount", "data_type": "int"},
            {"metadata_column_key": "removed", "column_name": "legacy", "data_type": "string"},
        ],
        [
            {"metadata_column_key": "same", "column_name": "new_name", "data_type": "long"},
            {"metadata_column_key": "typed", "column_name": "amount", "data_type": "long"},
            {"metadata_column_key": "added", "column_name": "fresh", "data_type": "string"},
        ],
    )
    assert [row["metadata_column_key"] for row in difference["added_columns"]] == ["added"]
    assert [row["metadata_column_key"] for row in difference["removed_columns"]] == ["removed"]
    assert difference["changed_data_types"][0]["current_data_type"] == "long"
    assert difference["renamed_columns"] == [{
        "metadata_column_key": "same", "contracted_column_name": "old_name",
        "current_column_name": "new_name",
    }]


@pytest.fixture
def snapshot_runtime(monkeypatch, spark_session):
    """Provide real widgets and append-only in-memory metadata tables."""
    module = importlib.import_module("fabricops_kit.widgets.widget_register_data_contract")
    registry = metadata_table_schema_registry()
    catalogue = spark_session.createDataFrame([
        ("key-one", "col-id", "fp-old", "dev", "Lakehouse", "raw", "sales", "orders", "id", "int", datetime(2026, 1, 1)),
        ("key-one", "col-id", "fp-new", "dev", "Lakehouse", "raw", "sales", "orders", "id", "long", datetime(2026, 2, 1)),
        ("key-one", "col-name", "fp-new", "dev", "Lakehouse", "raw", "sales", "orders", "name", "string", datetime(2026, 2, 1)),
        ("key-two", "col-total", "fp-two", "dev", "Warehouse", "curated", "finance", "summary", "total", "decimal", datetime(2026, 2, 1)),
        ("key-three", "col-customer", "fp-three", "dev", "Lakehouse", "raw", "", "customers", "customer_id", "long", datetime(2026, 2, 1)),
        ("key-prod", "col-prod", "fp-prod", "prod", "Lakehouse", "raw", "sales", "prod", "id", "long", datetime(2026, 2, 1)),
    ], "metadata_table_key string, metadata_column_key string, schema_fingerprint string, environment_name string, store_type string, layer string, schema_name string, table_name string, column_name string, data_type string, _committed_at timestamp")
    tables = {
        "METADATA_DATA_CATALOGUE": catalogue,
        "METADATA_DATA_CONTRACT": spark_session.createDataFrame([], registry["METADATA_DATA_CONTRACT"]),
        "METADATA_ENRICHMENT": spark_session.createDataFrame([], registry["METADATA_ENRICHMENT"]),
    }
    writes: list[tuple[str, str, list[dict]]] = []
    tick = {"value": 0}

    monkeypatch.setattr(module, "resolve_fabric_context", lambda **_kwargs: ({"config": True}, "dev", {}))
    monkeypatch.setattr(module, "get_spark_session", lambda value=None: value or spark_session)
    monkeypatch.setattr(module, "require_ipywidgets", lambda: _FakeWidgets)
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
            "_metadata_lakehouse_name": "metadata", "_activity_id": f"activity-{tick['value']}",
        }

    monkeypatch.setattr(module, "write_lakehouse_table_core", write)
    monkeypatch.setattr(module, "build_runtime_audit_fields", audit)
    monkeypatch.setattr(module, "_display_widget", lambda *_args, **_kwargs: None)
    return module, tables, writes


def _seed_snapshot(spark, tables, snapshot_id, agreement_id, saved_at, keys):
    """Append one test snapshot directly to in-memory tables."""
    registry = metadata_table_schema_registry()
    audit = {
        "_committed_by": "seed", "_committed_at": saved_at,
        "_workspace_id": "w", "_workspace_name": "w", "_notebook_id": "n",
        "_notebook_name": "n", "_metadata_lakehouse_name": "m", "_activity_id": snapshot_id,
    }
    rows = [{
        "agreement_id": agreement_id, "metadata_table_key": key,
        "schema_fingerprint": f"fp-{key}", **audit,
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
    assert state["latest_activity_id"] is None
    assert state["inventory_metadata_ids"] == ["key-one"]
    assert state["inventory_count"] == 1
    assert state["unknown_initial_metadata_ids"] == ["key-prod", "unknown"]
    assert state["has_unsaved_changes"] is True
    assert writes == []
    assert state["get_snapshot"]() == {"header": None, "memberships": []}
    review = state["get_schema_review"]()[0]
    assert review["schema_status"] == "New"
    assert review["current_fingerprint"] == "fp-new"
    assert review["contracted_fingerprint"] is None
    assert [row["column_name"] for row in review["current_schema"]] == ["id", "name"]
    assert state["contract_schema_will_change"] is False


def test_schema_review_classifies_unchanged_additive_and_breaking_changes(
    snapshot_runtime, spark_session,
):
    """Review state classifies the v0.2.0 structural change boundary."""
    _module, tables, _writes = snapshot_runtime
    _seed_snapshot(spark_session, tables, "same", "unchanged", datetime(2026, 3, 1), ["key-two"])
    # The seed helper derives fp-key-two; align it to the current catalogue fingerprint.
    rows = [row.asDict(recursive=True) for row in tables["METADATA_DATA_CONTRACT"].collect()]
    rows[-1]["schema_fingerprint"] = "fp-two"
    tables["METADATA_DATA_CONTRACT"] = spark_session.createDataFrame(
        rows, metadata_table_schema_registry()["METADATA_DATA_CONTRACT"],
    )
    unchanged = public_widget(agreement_id="unchanged", spark_session=spark_session)
    assert unchanged["dataset_reviews"][0]["schema_status"] == "Unchanged"

    _seed_snapshot(spark_session, tables, "old", "changed", datetime(2026, 3, 2), ["key-one"])
    rows = [row.asDict(recursive=True) for row in tables["METADATA_DATA_CONTRACT"].collect()]
    rows[-1]["schema_fingerprint"] = "fp-old"
    tables["METADATA_DATA_CONTRACT"] = spark_session.createDataFrame(
        rows, metadata_table_schema_registry()["METADATA_DATA_CONTRACT"],
    )
    changed = public_widget(agreement_id="changed", spark_session=spark_session)
    review = changed["dataset_reviews"][0]
    assert review["schema_status"] == "Breaking schema change"
    assert review["contracted_schema"][0]["data_type"] == "int"
    assert review["current_fingerprint"] == "fp-new"
    assert review["schema_diff"]["changed_data_types"]
    assert changed["contract_schema_will_change"] is True
    assert "currently displayed schema version" in changed["_controls"]["contract_schema_warning"].value

    # Make the old type identical so only the newly observed name column is additive.
    catalogue_rows = [row.asDict(recursive=True) for row in tables["METADATA_DATA_CATALOGUE"].collect()]
    catalogue_rows[0]["data_type"] = "long"
    tables["METADATA_DATA_CATALOGUE"] = spark_session.createDataFrame(
        catalogue_rows, tables["METADATA_DATA_CATALOGUE"].schema,
    )
    additive = public_widget(agreement_id="changed", spark_session=spark_session)
    assert additive["dataset_reviews"][0]["schema_status"] == "Additive schema change"


def test_removed_column_is_breaking(snapshot_runtime, spark_session):
    """A contracted column absent from the current fingerprint is breaking."""
    _module, tables, _writes = snapshot_runtime
    extra = spark_session.createDataFrame([
        ("key-two", "old-extra", "fp-two-old", "dev", "Warehouse", "curated", "finance", "summary", "legacy", "string", datetime(2026, 1, 1)),
        ("key-two", "col-total", "fp-two-old", "dev", "Warehouse", "curated", "finance", "summary", "total", "decimal", datetime(2026, 1, 1)),
    ], tables["METADATA_DATA_CATALOGUE"].schema)
    tables["METADATA_DATA_CATALOGUE"] = tables["METADATA_DATA_CATALOGUE"].unionByName(extra)
    _seed_snapshot(spark_session, tables, "old", "agreement", datetime(2026, 3, 1), ["key-two"])
    rows = [row.asDict(recursive=True) for row in tables["METADATA_DATA_CONTRACT"].collect()]
    rows[-1]["schema_fingerprint"] = "fp-two-old"
    tables["METADATA_DATA_CONTRACT"] = spark_session.createDataFrame(
        rows, metadata_table_schema_registry()["METADATA_DATA_CONTRACT"],
    )
    state = public_widget(agreement_id="agreement", spark_session=spark_session)
    assert state["dataset_reviews"][0]["schema_status"] == "Breaking schema change"
    assert state["dataset_reviews"][0]["schema_diff"]["removed_columns"][0]["column_name"] == "legacy"


def test_contracted_schema_is_recovered_from_another_environment(
    snapshot_runtime, spark_session,
):
    """Contract history is resolved by table and fingerprint across environments."""
    _module, tables, _writes = snapshot_runtime
    catalogue_rows = [
        row.asDict(recursive=True)
        for row in tables["METADATA_DATA_CATALOGUE"].collect()
    ]
    for row in catalogue_rows:
        if row["metadata_table_key"] == "key-one" and row["schema_fingerprint"] == "fp-old":
            row["environment_name"] = "prod"
    tables["METADATA_DATA_CATALOGUE"] = spark_session.createDataFrame(
        catalogue_rows, tables["METADATA_DATA_CATALOGUE"].schema,
    )
    _seed_snapshot(spark_session, tables, "old", "agreement", datetime(2026, 3, 1), ["key-one"])
    contract_rows = [
        row.asDict(recursive=True)
        for row in tables["METADATA_DATA_CONTRACT"].collect()
    ]
    contract_rows[-1]["schema_fingerprint"] = "fp-old"
    tables["METADATA_DATA_CONTRACT"] = spark_session.createDataFrame(
        contract_rows, metadata_table_schema_registry()["METADATA_DATA_CONTRACT"],
    )

    review = public_widget(
        agreement_id="agreement", spark_session=spark_session,
    )["dataset_reviews"][0]
    assert review["contracted_schema"] == [{
        "metadata_column_key": "col-id", "column_name": "id", "data_type": "int",
    }]
    assert review["current_fingerprint"] == "fp-new"
    assert review["schema_status"] == "Breaking schema change"


def test_changed_fingerprint_is_not_classified_as_unchanged(
    snapshot_runtime, spark_session,
):
    """An unexplained fingerprint difference remains visible without ordinal metadata."""
    _module, tables, _writes = snapshot_runtime
    current_rows = [
        row.asDict(recursive=True)
        for row in tables["METADATA_DATA_CATALOGUE"].collect()
        if row.metadata_table_key == "key-one" and row.schema_fingerprint == "fp-new"
    ]
    reordered_snapshot = [
        {**row, "schema_fingerprint": "fp-order-old", "_committed_at": datetime(2026, 1, 15)}
        for row in current_rows
    ]
    tables["METADATA_DATA_CATALOGUE"] = tables["METADATA_DATA_CATALOGUE"].unionByName(
        spark_session.createDataFrame(reordered_snapshot, tables["METADATA_DATA_CATALOGUE"].schema),
    )
    _seed_snapshot(spark_session, tables, "old", "agreement", datetime(2026, 3, 1), ["key-one"])
    contract_rows = [
        row.asDict(recursive=True)
        for row in tables["METADATA_DATA_CONTRACT"].collect()
    ]
    contract_rows[-1]["schema_fingerprint"] = "fp-order-old"
    tables["METADATA_DATA_CONTRACT"] = spark_session.createDataFrame(
        contract_rows, metadata_table_schema_registry()["METADATA_DATA_CONTRACT"],
    )

    review = public_widget(
        agreement_id="agreement", spark_session=spark_session,
    )["dataset_reviews"][0]
    assert review["schema_diff"]["added_columns"] == []
    assert review["schema_diff"]["removed_columns"] == []
    assert review["schema_diff"]["changed_data_types"] == []
    assert review["schema_status"] == "Schema fingerprint changed"
    assert review["contract_schema_will_change"] is True


def test_latest_inventory_loads_without_combining_older_history(snapshot_runtime, spark_session):
    """Opening displays only the newest snapshot and keeps unavailable identities visible."""
    _module, tables, _writes = snapshot_runtime
    _seed_snapshot(spark_session, tables, "old", "agreement", datetime(2026, 1, 1), ["key-one"])
    _seed_snapshot(spark_session, tables, "latest", "agreement", datetime(2026, 2, 1), ["key-two", "historical-key"])
    state = public_widget(agreement_id="agreement", spark_session=spark_session)
    assert state["latest_activity_id"] == "latest"
    assert state["inventory_metadata_ids"] == ["historical-key", "key-two"]
    labels_by_key = {value: label for label, value in state["_controls"]["inventory"].options}
    assert "Unavailable catalogue dataset" in labels_by_key["historical-key"]
    assert [row["metadata_table_key"] for row in state["get_rows"]()] == ["historical-key", "key-two"]


def test_agreement_state_selection_reloads_inventory_and_disables_when_empty(
    snapshot_runtime, spark_session,
):
    """Changing the agreement selector reactively loads that agreement's latest snapshot."""
    _module, tables, writes = snapshot_runtime
    _seed_snapshot(spark_session, tables, "a", "agreement-a", datetime(2026, 1, 1), ["key-one"])
    _seed_snapshot(spark_session, tables, "b", "agreement-b", datetime(2026, 1, 2), ["key-two"])
    selector = _FakeWidgets.Select(options=[("Select", ""), ("A", "agreement-a"), ("B", "agreement-b")], value="")
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
    assert state["latest_activity_id"] == "a"
    assert state["inventory_metadata_ids"] == ["key-one", "key-three"]
    assert state["_controls"]["save"].disabled is False

    selector.value = "agreement-b"
    assert state["agreement_id"] == "agreement-b"
    assert state["latest_activity_id"] == "b"
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
    assert controls["available"].value is None
    assert controls["add"].disabled is True
    controls["inventory"].value = "key-one"
    controls["remove"].click()
    assert state["inventory_metadata_ids"] == ["key-two"]
    assert "key-one" in [value for _label, value in controls["available"].options]
    assert state["inventory_count"] == 1


def test_catalogue_selection_shows_exact_schema_before_add(snapshot_runtime, spark_session):
    """Each logical dataset appears once and selection exposes the schema to record."""
    _module, _tables, _writes = snapshot_runtime
    state = public_widget(agreement_id="agreement", spark_session=spark_session)
    controls = state["_controls"]
    option_keys = [value for _label, value in controls["available"].options]
    assert option_keys.count("key-one") == 1

    controls["available"].value = "key-one"
    selected = state["get_selected_dataset_review"]()
    assert selected["metadata_table_key"] == "key-one"
    assert selected["current_fingerprint"] == "fp-new"
    assert selected["contracted_fingerprint"] is None
    assert [row["column_name"] for row in selected["current_schema"]] == ["id", "name"]
    assert "Current columns:</b> 2" in controls["selected_schema"].value
    assert controls["add"].description == "Add table to contract"


def test_one_snapshot_cannot_write_competing_fingerprints_for_one_dataset(
    snapshot_runtime, spark_session,
):
    """A complete activity contains one row per agreement and logical dataset key."""
    _module, _tables, writes = snapshot_runtime
    state = public_widget(
        agreement_id="agreement", metadata_ids=["key-one"], spark_session=spark_session,
    )
    state["inventory_metadata_ids"] = ["key-one", "key-one"]
    state["_controls"]["save"].click()
    saved_rows = writes[0][2]
    assert [(row["metadata_table_key"], row["schema_fingerprint"]) for row in saved_rows] == [
        ("key-one", "fp-new"),
    ]


def test_successive_snapshots_append_complete_inventories_and_preserve_history(snapshot_runtime, spark_session):
    """Five, six, then four dataset saves remain immutable and resolve latest correctly."""
    _module, tables, writes = snapshot_runtime
    extra = spark_session.createDataFrame([
        (f"key-{index}", f"col-{index}", f"fp-{index}", "dev", "Lakehouse", "raw", "sales", f"table_{index}", "id", "long", datetime(2026, 2, 1))
        for index in range(4, 8)
    ], "metadata_table_key string, metadata_column_key string, schema_fingerprint string, environment_name string, store_type string, layer string, schema_name string, table_name string, column_name string, data_type string, _committed_at timestamp")
    tables["METADATA_DATA_CATALOGUE"] = tables["METADATA_DATA_CATALOGUE"].unionByName(extra)
    five = ["key-one", "key-two", "key-three", "key-4", "key-5"]
    state = public_widget(agreement_id="agreement", metadata_ids=five, spark_session=spark_session)
    state["_controls"]["save"].click()
    first_id = state["saved_activity_id"]
    state["inventory_metadata_ids"].append("key-6")
    state["_controls"]["save"].click()
    second_id = state["saved_activity_id"]
    state["inventory_metadata_ids"] = ["key-one", "key-two", "key-three", "key-4"]
    state["_controls"]["save"].click()
    third_id = state["saved_activity_id"]

    assert len({first_id, second_id, third_id}) == 3
    assert tables["METADATA_DATA_CONTRACT"].count() == 5 + 6 + 4
    assert state["latest_activity_id"] == third_id
    assert state["inventory_count"] == 4
    assert len(state["get_rows"]()) == 4
    assert {mode for _name, mode, _rows in writes} == {"append"}
    for snapshot_id, count in ((first_id, 5), (second_id, 6), (third_id, 4)):
        rows = [row for row in tables["METADATA_DATA_CONTRACT"].collect() if row._activity_id == snapshot_id]
        assert len(rows) == count
        assert len({row._committed_at for row in rows}) == 1


def test_empty_inventory_is_rejected_without_writing(snapshot_runtime, spark_session):
    """An empty inventory remains unsupported without creating a second metadata table."""
    _module, tables, writes = snapshot_runtime
    _seed_snapshot(spark_session, tables, "old", "agreement", datetime(2026, 1, 1), ["key-one"])
    state = public_widget(agreement_id="agreement", spark_session=spark_session)
    controls = state["_controls"]
    controls["inventory"].value = "key-one"
    controls["remove"].click()
    controls["save"].click()
    assert state["inventory_count"] == 0
    assert state["latest_activity_id"] == "old"
    assert tables["METADATA_DATA_CONTRACT"].count() == 1
    assert writes == []
    assert "at least one logical dataset" in controls["status"].value


def test_save_records_current_schema_and_preserves_unavailable_contract_version(
    snapshot_runtime, spark_session,
):
    """Available datasets advance while unavailable retained datasets keep their fingerprint."""
    _module, tables, _writes = snapshot_runtime
    _seed_snapshot(
        spark_session, tables, "old", "agreement", datetime(2026, 1, 1),
        ["key-one", "historical-key"],
    )
    state = public_widget(agreement_id="agreement", spark_session=spark_session)
    state["_controls"]["save"].click()
    saved = {row["metadata_table_key"]: row["schema_fingerprint"] for row in state["get_rows"]()}
    assert saved == {"key-one": "fp-new", "historical-key": "fp-historical-key"}


def test_new_dataset_without_current_fingerprint_is_rejected(snapshot_runtime, spark_session):
    """Catalogue membership alone cannot create a contract row with an empty schema version."""
    _module, tables, writes = snapshot_runtime
    rows = [row.asDict(recursive=True) for row in tables["METADATA_DATA_CATALOGUE"].collect()]
    rows.append({
        **rows[0], "metadata_table_key": "invalid", "metadata_column_key": "invalid-col",
        "schema_fingerprint": "", "column_name": "id", "_committed_at": datetime(2026, 4, 1),
    })
    tables["METADATA_DATA_CATALOGUE"] = spark_session.createDataFrame(
        rows, tables["METADATA_DATA_CATALOGUE"].schema,
    )
    state = public_widget(
        agreement_id="agreement", metadata_ids=["invalid"], spark_session=spark_session,
    )
    state["_controls"]["save"].click()
    assert writes == []
    assert "valid current catalogue schema fingerprint" in state["_controls"]["status"].value


def test_other_agreements_and_historical_rows_are_unchanged(snapshot_runtime, spark_session):
    """Saving one agreement only appends and never mutates existing rows."""
    _module, tables, _writes = snapshot_runtime
    _seed_snapshot(spark_session, tables, "a-old", "agreement", datetime(2026, 1, 1), ["key-one"])
    _seed_snapshot(spark_session, tables, "b-old", "other", datetime(2026, 1, 1), ["key-two"])
    original = {(row._activity_id, row.agreement_id, row.metadata_table_key) for row in tables["METADATA_DATA_CONTRACT"].collect()}
    state = public_widget(agreement_id="agreement", spark_session=spark_session)
    state["_controls"]["save"].click()
    after = {(row._activity_id, row.agreement_id, row.metadata_table_key) for row in tables["METADATA_DATA_CONTRACT"].collect()}
    assert original <= after
    assert ("b-old", "other", "key-two") in after


def test_html_values_are_escaped(snapshot_runtime, spark_session):
    """Agreement and catalogue metadata cannot inject notebook HTML."""
    _module, tables, _writes = snapshot_runtime
    tables["METADATA_DATA_CATALOGUE"] = spark_session.createDataFrame([
        ("html", "html-col", "fp", "dev", "Lakehouse", "<b>raw</b>", "sales", "orders", "<img>", "string", datetime(2026, 1, 1)),
    ], "metadata_table_key string, metadata_column_key string, schema_fingerprint string, environment_name string, store_type string, layer string, schema_name string, table_name string, column_name string, data_type string, _committed_at timestamp")
    state = public_widget(
        agreement={"agreement_id": "agreement", "agreement_name": "<script>alert(1)</script>"},
        spark_session=spark_session,
    )
    assert "<script>" not in state["_controls"]["agreement"].value
    assert "&lt;script&gt;" in state["_controls"]["agreement"].value
    labels_by_key = {value: label for label, value in state["_controls"]["available"].options}
    assert "<b>raw</b>" in labels_by_key["html"]


def test_enrichment_editor_uses_stable_identities_and_separate_save(snapshot_runtime, spark_session):
    """Descriptions survive fingerprints and only changed current fields append."""
    _module, tables, writes = snapshot_runtime
    registry = metadata_table_schema_registry()
    audit = {
        "_committed_by": "seed", "_committed_at": datetime(2026, 7, 1),
        "_workspace_id": "w", "_workspace_name": "w", "_notebook_id": "n",
        "_notebook_name": "n", "_metadata_lakehouse_name": "m", "_activity_id": "enrich-old",
    }
    rows = [
        {"enrichment_rule_id": "table-v1", "enrichment_rule_version": "1", "enrichment_rule_key": "table-key",
         "metadata_table_key": "key-one", "metadata_column_key": "", "table_name": "orders",
         "column_name": "", "enrichment_scope": "table", "business_description": "Orders table",
         "activation_state": "active", "is_active": True, **audit},
        {"enrichment_rule_id": "column-v1", "enrichment_rule_version": "1", "enrichment_rule_key": "column-key",
         "metadata_table_key": "key-one", "metadata_column_key": "col-id", "table_name": "orders",
         "column_name": "id", "enrichment_scope": "column", "column_description": "Stable identifier",
         "activation_state": "active", "is_active": True, **audit},
    ]
    tables["METADATA_ENRICHMENT"] = spark_session.createDataFrame(
        [coerce_metadata_row_types("METADATA_ENRICHMENT", row) for row in rows],
        registry["METADATA_ENRICHMENT"],
    )
    state = public_widget(agreement_id="agreement", spark_session=spark_session)
    state["_controls"]["available"].value = "key-one"
    assert state["selected_table_enrichment"]["business_description"] == "Orders table"
    editor = {row["metadata_column_key"]: row for row in state["get_enrichment_editor_rows"]()}
    assert editor["col-id"]["business_description"] == "Stable identifier"
    assert editor["col-name"]["business_description"] == ""
    state["_controls"]["table_description"].value = "Orders for reporting <safe>"
    state["_controls"]["save_descriptions"].click()
    enrichment_writes = [rows for name, _mode, rows in writes if name == "METADATA_ENRICHMENT"]
    assert len(enrichment_writes) == 1
    assert len(enrichment_writes[0]) == 1
    saved = enrichment_writes[0][0]
    assert saved["business_description"] == "Orders for reporting <safe>"
    assert saved["column_description"] in (None, "")
    assert saved["_committed_by"] == "tester"
    assert state["last_enrichment_save_result"]["table_saved"] is True


def test_removed_enrichment_rows_are_scoped_read_only_and_escaped(snapshot_runtime, spark_session):
    """Only the contracted/current difference appears with catalogue observation time."""
    _module, tables, _writes = snapshot_runtime
    extra = spark_session.createDataFrame([
        ("key-one", "col-removed", "fp-old", "dev", "Lakehouse", "raw", "sales", "orders", "legacy", "string", datetime(2026, 1, 20)),
        ("key-one", "col-historical", "fp-ancient", "dev", "Lakehouse", "raw", "sales", "orders", "ancient", "string", datetime(2025, 1, 1)),
    ], tables["METADATA_DATA_CATALOGUE"].schema)
    tables["METADATA_DATA_CATALOGUE"] = tables["METADATA_DATA_CATALOGUE"].unionByName(extra)
    _seed_snapshot(spark_session, tables, "old", "agreement", datetime(2026, 3, 1), ["key-one"])
    contract_rows = [row.asDict(recursive=True) for row in tables["METADATA_DATA_CONTRACT"].collect()]
    contract_rows[-1]["schema_fingerprint"] = "fp-old"
    tables["METADATA_DATA_CONTRACT"] = spark_session.createDataFrame(
        contract_rows, metadata_table_schema_registry()["METADATA_DATA_CONTRACT"],
    )
    state = public_widget(agreement_id="agreement", spark_session=spark_session)
    assert state["show_removed_columns"] is False
    assert state["removed_column_rows"][0]["metadata_column_key"] == "col-removed"
    assert state["removed_column_rows"][0]["editable"] is False
    assert state["removed_column_rows"][0]["last_observed"] == datetime(2026, 1, 20)
    assert all(row["metadata_column_key"] != "col-historical" for row in state["removed_column_rows"])
    state["_controls"]["show_removed_columns"].value = True
    assert state["show_removed_columns"] is True


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
