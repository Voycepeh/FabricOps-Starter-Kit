"""Focused contracts for the lightweight guardrail authoring widget."""

import importlib
import json
import sys

import fabricops_kit
from fabricops_kit.pipeline.guardrails_shared import schema_check_core
from fabricops_kit.widgets import widget_author_guardrails
from fabricops_kit.widgets.widget_author_dq_rules import widget_author_dq_rules
from fabricops_kit.widgets.widget_author_guardrails import (
    CHANGE_BEHAVIOURS,
    _guardrail_records_from_selection,
    _render_guardrail_authoring,
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
            {"column_name": "snapshot_date", "data_type": "date"},
            {"column_name": "extra", "data_type": "string"},
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
    assert callable(fabricops_kit.widget_author_dq_rules)
    assert widget_author_dq_rules.__name__ == "widget_author_dq_rules"
    assert "widget_author_guardrails" in fabricops_kit.__all__
    assert "widget_select_guardrail_target" not in fabricops_kit.__all__
    assert not hasattr(fabricops_kit, "widget_select_guardrail_target")
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

    widget = _render_guardrail_authoring(
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
    widget = _render_guardrail_authoring(_state(existing), context={"config": object(), "env": "dev"})

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


def test_schema_section_displays_catalogue_datatypes_and_persists_checked_columns(monkeypatch):
    """Show every canonical catalogue type and persist it only for checked columns."""
    _install_fake_notebook_widgets(monkeypatch)

    widget = _render_guardrail_authoring(_state(), context={"config": object(), "env": "dev"})
    controls = widget["controls"]

    assert list(controls["schema_rows"]) == ["id", "updated_at", "snapshot_date", "extra"]
    assert controls["schema_data_types"] == {
        "id": "bigint",
        "updated_at": "timestamp",
        "snapshot_date": "date",
        "extra": "string",
    }
    for name, row in controls["schema_rows"].items():
        assert name in row.children[1].value
        assert controls["schema_data_types"][name] in row.children[2].value

    controls["schema_columns"]["updated_at"].value = False
    schema_params = json.loads(widget["build_records"]()[0]["rule_parameters_json"])

    assert schema_params["columns"] == ["id", "snapshot_date", "extra"]
    assert schema_params["data_types"] == {
        "id": controls["schema_data_types"]["id"],
        "snapshot_date": controls["schema_data_types"]["snapshot_date"],
        "extra": controls["schema_data_types"]["extra"],
    }
    assert "updated_at" not in schema_params["data_types"]


def test_existing_schema_selection_and_severity_are_prepopulated(monkeypatch):
    """Load required columns and failure action while showing current catalogue types."""
    _install_fake_notebook_widgets(monkeypatch)
    existing = [
        {
            "guardrail_type": "schema",
            "configuration_version": 3,
            "severity": "warning",
            "rule_parameters_json": json.dumps(
                {"columns": ["id", "extra"], "data_types": {"id": "long", "extra": "string"}}
            ),
        }
    ]

    controls = _render_guardrail_authoring(_state(existing), context={"config": object(), "env": "dev"})["controls"]

    assert {name for name, checkbox in controls["schema_columns"].items() if checkbox.value} == {"id", "extra"}
    assert controls["schema_failure_action"].value == "warning"
    assert controls["schema_data_types"]["id"] == "bigint"


def test_minimum_required_schema_enforces_selected_columns_and_allows_extra_columns():
    """Retain missing-column and datatype enforcement without rejecting extras."""

    class Frame:
        def __init__(self, dtypes):
            self.dtypes = dtypes
            self.columns = [name for name, _ in dtypes]

    rule = _records()[0]

    missing = schema_check_core(
        Frame([("extra", "string")]),
        rules_df=[rule],
        dataset_name="sales",
        table_name="orders",
        metadata_table_key="lakehouse.source.dbo.orders",
    )
    mismatch = schema_check_core(
        Frame([("id", "string"), ("extra", "string")]),
        rules_df=[rule],
        dataset_name="sales",
        table_name="orders",
        metadata_table_key="lakehouse.source.dbo.orders",
    )
    matching_with_extra = schema_check_core(
        Frame([("id", "bigint"), ("extra", "string")]),
        rules_df=[rule],
        dataset_name="sales",
        table_name="orders",
        metadata_table_key="lakehouse.source.dbo.orders",
    )

    assert missing["missing_columns"] == ["id"]
    assert missing["can_continue"] is False
    assert mismatch["datatype_mismatches"] == [{"column": "id", "expected": "bigint", "actual": "string"}]
    assert mismatch["can_continue"] is False
    assert matching_with_extra["unexpected_columns"] == ["extra"]
    assert matching_with_extra["can_continue"] is True


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


def test_target_change_rerenders_without_committing(monkeypatch):
    """Commit once on initial construction but never as a target-change side effect."""
    _install_fake_notebook_widgets(monkeypatch)
    module = sys.modules["fabricops_kit.widgets.widget_author_guardrails"]
    callbacks = {}
    saves = []
    render_commit_values = []

    def fake_targets(config, env, *, spark_session, widgets, on_change):
        state = _state()
        callbacks["on_change"] = on_change
        on_change(state)
        return (
            state,
            widgets.Dropdown(options=["orders"]),
            {"target_summary": widgets.HTML(), "refresh_target": lambda: None},
        )

    def fake_render(state, *, spark_session, context, commit):
        render_commit_values.append(commit)

        def save():
            saves.append(state["table_name"])
            return [{"table_name": state["table_name"]}]

        return {"ui": module.shared.require_ipywidgets().VBox(), "save": save}

    monkeypatch.setattr(module.shared, "_load_guardrail_authoring_targets", fake_targets)
    monkeypatch.setattr(module, "_render_guardrail_authoring", fake_render)

    module.widget_author_guardrails(spark_session=object(), context={"config": object(), "env": "dev"}, commit=True)
    changed = _state()
    changed["table_name"] = "customers"
    callbacks["on_change"](changed)

    assert saves == ["orders"]
    assert render_commit_values == [False, False]
