"""Focused contracts for standalone normalized Guardrail authoring."""

from __future__ import annotations

import inspect
import json
import sys
import types

import pytest

import fabricops_kit
from fabricops_kit.widgets import shared as authoring
from fabricops_kit.widgets import widget_author_guardrails
from fabricops_kit.widgets.widget_author_guardrails import (
    CHANGE_BEHAVIOURS,
    _guardrail_records_from_selection,
    _render_guardrail_authoring,
)


OBSOLETE_GUARDRAIL_FIELDS = {
    "configuration_version", "metadata_table_key", "metadata_column_key", "dataset_name", "table_name",
    "column_name", "rule_key", "review_status", "review_state", "approval_required", "approval_bypassed",
    "requires_governance_review", "requires_post_review", "bypass_reason", "action_type", "source_notebook_type",
    "created_by_role",
}


def _install_fake_notebook_widgets(monkeypatch, *, auto_observe=False):
    """Install minimal ipywidgets/IPython fakes for widget unit tests."""

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
        Dropdown=Widget, Select=Widget, SelectMultiple=Widget, Textarea=Widget, Text=Widget,
        BoundedIntText=Widget, FloatText=Widget, ToggleButtons=Widget, Combobox=Widget,
        Checkbox=Widget, Button=Widget, HTML=Widget, VBox=Box, HBox=Box, GridBox=Box,
        Layout=lambda **kwargs: types.SimpleNamespace(**kwargs),
    )
    fake_display = types.SimpleNamespace(display=lambda *args, **kwargs: None)
    monkeypatch.setitem(sys.modules, "IPython", types.SimpleNamespace(display=fake_display))
    monkeypatch.setitem(sys.modules, "ipywidgets", fake_widgets)
    return fake_widgets


def _state(existing=()):
    rows = [
        {"table_id": "table-orders", "column_id": "col-id", "column_name": "id", "data_type": "bigint"},
        {"table_id": "table-orders", "column_id": "col-updated", "column_name": "updated_at", "data_type": "timestamp"},
        {"table_id": "table-orders", "column_id": "col-snapshot", "column_name": "snapshot_date", "data_type": "date"},
        {"table_id": "table-orders", "column_id": "col-extra", "column_name": "extra", "data_type": "string"},
    ]
    return {
        "environment_name": "dev",
        "table_id": "table-orders",
        "contract_id": "contract-orders",
        "contract_version": 2,
        "table_name": "orders",
        "store_type": "lakehouse",
        "layer": "source",
        "schema_name": "dbo",
        "columns": [row["column_name"] for row in rows],
        "column_ids": {row["column_name"]: row["column_id"] for row in rows},
        "catalogue_profile_rows": rows,
        "existing_rules": list(existing),
    }


def _records(**overrides):
    values = dict(
        required_columns=["id"], freshness_column="updated_at", maximum_age=1,
        maximum_age_unit="Hours", change_behaviour="Incremental append",
        partition_column="snapshot_date", change_column="updated_at",
    )
    values.update(overrides)
    return _guardrail_records_from_selection(_state(), **values)


def test_public_surface_keeps_two_standalone_authoring_widgets():
    """Verify that the public surface keeps only the two standalone widgets."""
    assert fabricops_kit.widget_author_guardrails is widget_author_guardrails
    assert callable(fabricops_kit.widget_author_dq_rules)
    assert "widget_select_guardrail_target" not in fabricops_kit.__all__
    assert not hasattr(fabricops_kit, "widget_select_guardrail_target")


def test_guardrail_records_use_only_stage4a_authoring_fields():
    """Verify that authored Guardrail rows use only the Stage 4A contract."""
    records = _records()
    expected = {
        "guardrail_rule_id", "guardrail_version", "contract_id", "contract_version", "column_id", "environment_name",
        "guardrail_type", "rule_id", "rule_type", "rule_parameters_json", "severity", "is_active",
    }
    assert all(set(row) == expected for row in records)
    assert all(row["contract_id"] == "contract-orders" and row["contract_version"] == 2 for row in records)
    assert all("table_id" not in row for row in records)
    assert all(not (set(row) & OBSOLETE_GUARDRAIL_FIELDS) for row in records)


def test_schema_selection_serializes_required_columns_and_current_types():
    """Verify that Schema rules persist required columns and current data types."""
    schema = _records(required_columns=["id", "extra"])[0]
    assert schema["guardrail_type"] == "schema"
    assert schema["rule_id"] == "schema"
    assert schema["rule_type"] == "minimum_required"
    assert json.loads(schema["rule_parameters_json"]) == {
        "columns": ["id", "extra"], "data_types": {"extra": "string", "id": "bigint"},
    }


def test_freshness_uses_runtime_parameter_vocabulary_and_failure_severity():
    """Verify that Freshness rules use the runtime parameter vocabulary."""
    freshness = _records(maximum_age=24, maximum_age_unit="Hours", freshness_severity="warning")[1]
    assert freshness["rule_type"] == "max_age"
    assert freshness["severity"] == "warning"
    assert json.loads(freshness["rule_parameters_json"]) == {
        "freshness_column": "updated_at", "maximum_age": 24.0, "maximum_age_unit": "hours",
    }
    assert freshness["column_id"] == ""


def test_freshness_can_be_disabled_without_removing_logical_rule():
    """Verify that Freshness can be disabled while preserving its logical row."""
    freshness = _records(freshness_column="")[1]
    assert freshness["rule_id"] == "freshness"
    assert freshness["rule_type"] == "skip"
    assert json.loads(freshness["rule_parameters_json"])["freshness_column"] == ""


def test_change_behaviours_preserve_existing_runtime_contract():
    """Verify that Changes behaviour labels preserve the existing runtime contract."""
    expected = {
        "No changes expected": ("no_change_required", "snapshot"),
        "Incremental append": ("monitor_only", "incremental_append"),
        "Snapshot overwrite": ("monitor_only", "snapshot"),
    }
    assert tuple(CHANGE_BEHAVIOURS) == tuple(expected)
    for label, (expected_change, source_pattern) in expected.items():
        change = _records(change_behaviour=label)[2]
        params = json.loads(change["rule_parameters_json"])
        assert change["rule_id"] == "changes"
        assert change["rule_type"] == expected_change
        assert params["expected_change"] == expected_change
        assert params["source_pattern"] == source_pattern
        assert params["partition_column"] == "snapshot_date"
        assert params["change_column"] == "updated_at"


def test_invalid_columns_age_and_failure_action_fail_clearly():
    """Verify that invalid Guardrail inputs fail with clear validation errors."""
    with pytest.raises(ValueError, match="positive"):
        _records(maximum_age=0)
    with pytest.raises(ValueError, match="selected table schema"):
        _records(required_columns=["missing"])
    with pytest.raises(ValueError, match="Failure action"):
        _records(schema_severity="error")


def test_rule_identity_is_stable_while_guardrail_version_advances():
    """Verify stable logical identity across Guardrail versions."""
    first = _records(guardrail_version=1)
    second = _records(guardrail_version=2, maximum_age=48)
    assert [row["guardrail_rule_id"] for row in first] == [row["guardrail_rule_id"] for row in second]
    assert {row["guardrail_version"] for row in first} == {1}
    assert {row["guardrail_version"] for row in second} == {2}


def test_column_name_to_column_id_resolution_is_canonical():
    """Verify that visible column names resolve through canonical Catalogue IDs."""
    assert authoring._column_id_for_name(_state(), "updated_at") == "col-updated"
    with pytest.raises(ValueError, match="column_id"):
        authoring._column_id_for_name(_state(), "missing")


def test_target_resolver_joins_latest_profile_snapshot_to_catalogue(monkeypatch):
    """Verify that target resolution joins the latest profile snapshot to Catalogue."""
    widgets = _install_fake_notebook_widgets(monkeypatch)
    catalogue = [
        {
            "metadata_level": "table", "table_id": "table-orders", "column_id": "", "environment_name": "dev",
            "store_type": "lakehouse", "layer": "silver", "schema_name": "dbo", "table_name": "orders",
        },
        *[
            {
                "metadata_level": "column", "table_id": "table-orders", "column_id": column_id,
                "column_name": column_name, "environment_name": "dev",
            }
            for column_id, column_name in (("col-a", "a"), ("col-b", "b"), ("col-c", "obsolete_c"))
        ],
    ]
    profiles = [
        {
            "profile_id": f"old-{column_id}", "profile_snapshot_id": "snapshot-1", "table_id": "table-orders",
            "column_id": column_id, "environment_name": "dev", "data_type": "string",
            "_committed_at": "2026-01-01T00:00:00Z",
        }
        for column_id in ("col-a", "col-c")
    ] + [
        {
            "profile_id": f"new-{column_id}", "profile_snapshot_id": "snapshot-2", "table_id": "table-orders",
            "column_id": column_id, "environment_name": "dev", "data_type": "string",
            "_committed_at": "2026-02-01T00:00:00Z",
        }
        for column_id in ("col-a", "col-b")
    ]
    rules = [{"contract_id": "contract-orders", "contract_version": 2, "environment_name": "dev", "guardrail_type": "schema"}]
    contracts = [{"contract_id": "contract-orders", "contract_version": 2, "table_id": "table-orders"}]

    def fake_read(config, env, table_name, *, spark_session):
        return {
            authoring.CATALOGUE_TABLE: catalogue,
            authoring.PROFILED_TABLE: profiles,
            authoring.GUARDRAIL_TABLE: rules,
            authoring.DATA_CONTRACT_TABLE: contracts,
        }[table_name]

    monkeypatch.setattr(authoring, "read_metadata_table_or_empty", fake_read)
    state, _, _ = authoring.load_guardrail_authoring_targets(
        object(), "dev", spark_session=object(), widgets=widgets
    )

    assert state["table_id"] == "table-orders"
    assert state["profile_snapshot_id"] == "snapshot-2"
    assert state["columns"] == ["a", "b"]
    assert state["column_ids"] == {"a": "col-a", "b": "col-b"}
    assert state["existing_rules"] == rules
    assert "metadata_table_key" not in state


def test_widget_preview_uses_new_metadata_vocabulary(monkeypatch):
    """Verify that the widget preview exposes only normalized metadata vocabulary."""
    _install_fake_notebook_widgets(monkeypatch)
    widget = _render_guardrail_authoring(_state(), context={"config": object(), "env": "dev"})
    preview = widget["controls"]["preview"].value
    assert '"contract_id": "contract-orders"' in preview
    assert '"contract_version": 2' in preview
    assert '"guardrail_version": 1' in preview
    for field in OBSOLETE_GUARDRAIL_FIELDS:
        assert f'"{field}"' not in preview


def test_widget_save_uses_shared_canonical_writer_and_advances_version(monkeypatch):
    """Verify that saving uses the shared writer and advances Guardrail version."""
    _install_fake_notebook_widgets(monkeypatch)
    saved = []
    monkeypatch.setattr(authoring, "canonicalize_records", lambda records, **kwargs: [dict(row) for row in records])
    monkeypatch.setattr(authoring, "write_rule_records", lambda records, **kwargs: saved.append([dict(row) for row in records]))
    widget = _render_guardrail_authoring(
        _state(), spark_session=object(), context={"config": object(), "env": "dev"}
    )
    first = widget["save"]()
    second = widget["save"]()
    assert len(saved) == 2
    assert {row["guardrail_version"] for row in first} == {1}
    assert {row["guardrail_version"] for row in second} == {2}


def test_authoring_widgets_do_not_depend_on_each_other_or_public_target_selector():
    """Verify that the standalone widgets do not depend on each other or old selector."""
    guardrail_source = inspect.getsource(sys.modules["fabricops_kit.widgets.widget_author_guardrails"])
    assert "widget_author_dq_rules(" not in guardrail_source
    assert "widget_select_guardrail_target" not in guardrail_source
