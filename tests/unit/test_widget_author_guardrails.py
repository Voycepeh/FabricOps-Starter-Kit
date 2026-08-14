"""Focused contracts for the lightweight guardrail authoring widget."""

import importlib
import json
import sys

import fabricops_kit
from fabricops_kit.pipeline.guardrails_shared import schema_check_core
from fabricops_kit.widgets import widget_author_dq_rules, widget_author_guardrails
from fabricops_kit.widgets.widget_author_guardrails import (
    CHANGE_BEHAVIOURS,
    _guardrail_records_from_selection,
)


def _install_fake_notebook_widgets(monkeypatch, *, auto_observe=False):
    """Install minimal ipywidgets/IPython fakes for widget unit tests."""
    import sys
    import types

    class Widget:
        def __init__(self, *args, **kwargs):
            self._observers = []
            options = kwargs.get("options", [])
            self.options = options
            if "value" in kwargs:
                self._value = kwargs["value"]
            elif options:
                first = options[0]
                self._value = first[1] if isinstance(first, tuple) and len(first) == 2 else first
            else:
                self._value = ""
            self.description = kwargs.get("description", "")
            self.layout = kwargs.get("layout") or types.SimpleNamespace(display="")
            self.button_style = kwargs.get("button_style", "")
            self.disabled = kwargs.get("disabled", False)
            self.rows = kwargs.get("rows", None)

        @property
        def value(self):
            return self._value

        @value.setter
        def value(self, value):
            previous = self._value
            self._value = value
            if auto_observe and previous != value:
                for callback in self._observers:
                    callback({"name": "value", "old": previous, "new": value})

        def observe(self, callback, names=None):
            self._observer = callback
            self._observers.append(callback)

        def on_click(self, callback):
            self._click = callback

        def add_class(self, _name):
            return None

    class Box(Widget):
        def __init__(self, children=None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.children = children or []

    fake_widgets = types.SimpleNamespace(
        Dropdown=Widget,
        Select=Widget,
        SelectMultiple=Widget,
        Textarea=Widget,
        Text=Widget,
        BoundedIntText=Widget,
        FloatText=Widget,
        ToggleButtons=Widget,
        Combobox=Widget,
        Checkbox=Widget,
        Button=Widget,
        HTML=Widget,
        VBox=Box,
        HBox=Box,
        GridBox=Box,
        Layout=lambda **kwargs: types.SimpleNamespace(**kwargs),
    )
    fake_display = types.SimpleNamespace(display=lambda *args, **kwargs: None)
    monkeypatch.setitem(sys.modules, "IPython", types.SimpleNamespace(display=fake_display))
    monkeypatch.setitem(sys.modules, "ipywidgets", fake_widgets)
    monkeypatch.setattr(
        "importlib.import_module",
        lambda name: fake_widgets if name == "ipywidgets" else __import__(name),
    )


def _state(existing=()):
    return {
        "environment_name": "dev",
        "dataset_name": "sales",
        "table_name": "orders",
        "metadata_table_key": "lakehouse.source.dbo.orders",
        "fabric_store_target": "source",
        "schema_name": "dbo",
        "columns": ["id", "updated_at", "snapshot_date", "extra"],
        "catalogue_profile_rows": [
            {"column_name": "id", "data_type": "bigint"},
            {"column_name": "updated_at", "data_type": "timestamp"},
        ],
        "existing_rules": list(existing),
    }


def _records(**overrides):
    values = dict(
        required_columns=["id"],
        freshness_column="updated_at",
        maximum_age=1,
        maximum_age_unit="Hours",
        change_behaviour="Incremental append",
        partition_column="snapshot_date",
        change_column="updated_at",
    )
    values.update(overrides)
    return _guardrail_records_from_selection(_state(), **values)


def test_public_surface_is_breaking_replacement():
    """Expose only the new authoring callable while retaining DQ authoring."""
    assert fabricops_kit.widget_author_guardrails is widget_author_guardrails
    assert widget_author_dq_rules is fabricops_kit.widget_author_dq_rules
    assert "widget_author_guardrails" in fabricops_kit.__all__
    assert "widget_author_schema_freshness_profile_rules" not in fabricops_kit.__all__
    assert not hasattr(fabricops_kit, "widget_author_schema_freshness_profile_rules")


def test_records_are_minimum_schema_canonical_duration_and_simple_changes():
    """Build the three canonical lightweight rule rows."""
    records = _records()
    schema, freshness, changes = records
    assert schema["rule_type"] == "minimum_required"
    assert json.loads(schema["rule_parameters_json"])["columns"] == ["id"]
    assert "extra" not in json.loads(schema["rule_parameters_json"])["columns"]
    assert json.loads(freshness["rule_parameters_json"]) == {
        "freshness_column": "updated_at",
        "maximum_age": 1.0,
        "maximum_age_unit": "hours",
    }
    params = json.loads(changes["rule_parameters_json"])
    assert params["source_pattern"] == "incremental_append"
    assert tuple(CHANGE_BEHAVIOURS) == ("No changes expected", "Incremental append", "Snapshot overwrite")


def test_each_section_persists_its_authored_failure_action():
    """Store each section's failure action through the canonical severity field."""
    records = _records(schema_severity="blocking", freshness_severity="warning", change_severity="blocking")

    assert {row["guardrail_type"]: row["severity"] for row in records} == {
        "schema": "blocking",
        "freshness": "warning",
        "change": "blocking",
    }


def test_change_behaviour_mapping():
    """Translate the three UI labels in one authoritative mapping."""
    expected = {
        "No changes expected": ("no_change_required", "snapshot"),
        "Incremental append": ("monitor_only", "incremental_append"),
        "Snapshot overwrite": ("monitor_only", "snapshot"),
    }
    for label, (intent, pattern) in expected.items():
        params = json.loads(_records(change_behaviour=label)[2]["rule_parameters_json"])
        assert (params["expected_change"], params["source_pattern"]) == (intent, pattern)


def test_minutes_hours_days_and_append_only_versioning():
    """Persist every duration unit and append deterministic versions."""
    for unit in ("Minutes", "Hours", "Days"):
        assert (
            json.loads(_records(maximum_age_unit=unit)[1]["rule_parameters_json"])["maximum_age_unit"] == unit.lower()
        )
    prior = _records()
    for row in prior:
        row["configuration_version"] = 4
    records = _guardrail_records_from_selection(
        _state(prior),
        required_columns=["id"],
        freshness_column="",
        maximum_age=1,
        maximum_age_unit="Days",
        change_behaviour="Snapshot overwrite",
    )
    assert {row["configuration_version"] for row in records} == {5}
    assert all(row["configuration_version"] == 4 for row in prior)
    assert all(row["metadata_table_key"] == "lakehouse.source.dbo.orders" for row in records)


def test_invalid_column_and_age_are_rejected():
    """Reject selections outside the catalogue and non-positive ages."""
    import pytest

    with pytest.raises(ValueError, match="positive"):
        _records(maximum_age=0)
    with pytest.raises(ValueError, match="selected table schema"):
        _records(required_columns=["missing"])


def test_two_persisted_saves_advance_the_local_version(monkeypatch):
    """Assign a distinct next version after every successful append."""
    _install_fake_notebook_widgets(monkeypatch)
    existing = [{"guardrail_type": "schema", "configuration_version": 3}]
    written = []
    module = sys.modules["fabricops_kit.widgets.widget_author_guardrails"]
    monkeypatch.setattr(module.shared, "_write_rule_records", lambda records, **_: written.append(records))

    widget = widget_author_guardrails(
        _state(existing), context={"config": object(), "env": "dev"}, spark_session=object()
    )
    first = widget["save"]()
    second = widget["save"]()

    assert [first[0]["configuration_version"], second[0]["configuration_version"]] == [4, 5]
    assert widget["version_state"]["persisted"] == 5
    assert "6" in widget["ui"].children[1].children[-1].value
    assert existing == [{"guardrail_type": "schema", "configuration_version": 3}]


def test_failure_actions_prepopulate_and_rebuild_from_existing_rules(monkeypatch):
    """Load section-specific failure actions and preserve them in rebuilt rows."""
    _install_fake_notebook_widgets(monkeypatch)
    existing = [
        {"guardrail_type": "schema", "configuration_version": 3, "severity": "warning"},
        {"guardrail_type": "freshness", "configuration_version": 3, "severity": "blocking"},
        {"guardrail_type": "change", "configuration_version": 3, "severity": "warning"},
    ]
    widget = widget_author_guardrails(_state(existing), context={"config": object(), "env": "dev"})

    controls = widget["controls"]
    assert controls["schema_failure_action"].value == "warning"
    assert controls["freshness_failure_action"].value == "blocking"
    assert controls["change_failure_action"].value == "warning"
    assert tuple(controls["schema_failure_action"].options) == (
        ("Block pipeline", "blocking"),
        ("Warn only", "warning"),
    )
    assert {row["guardrail_type"]: row["severity"] for row in widget["build_records"]()} == {
        "schema": "warning",
        "freshness": "blocking",
        "change": "warning",
    }


def test_schema_runtime_uses_authored_warning_severity():
    """Let an authored schema warning continue without a caller-side override."""

    class Frame:
        columns = []
        dtypes = []

    rules = _records(schema_severity="warning")
    result = schema_check_core(
        Frame(),
        rules_df=rules,
        dataset_name="sales",
        table_name="orders",
        metadata_table_key="lakehouse.source.dbo.orders",
    )

    assert result["status"] == "warning"
    assert result["severity"] == "warning"
    assert result["can_continue"] is True
