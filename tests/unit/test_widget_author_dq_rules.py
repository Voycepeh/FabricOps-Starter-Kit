"""Focused contracts for standalone normalized DQ authoring."""

from __future__ import annotations

import inspect
import importlib
import json
from types import SimpleNamespace

import pytest

from fabricops_kit.pipeline.shared import DQ_RULE_TYPES
from fabricops_kit.widgets import shared as authoring
from fabricops_kit.widgets import shared
from fabricops_kit.widgets.widget_author_dq_rules import (
    DQ_RULE_DEFINITIONS,
    _collect_parameters,
)


FINAL_RULES = {
    "missing_values",
    "blank_text",
    "unique_values",
    "unique_combination",
    "allowed_values",
    "blocked_values",
    "value_range",
    "text_pattern",
    "required_when",
    "conditional_value",
    "compare_columns",
}


def _state(existing=()):
    rows = [
        {"column_name": "student_id", "column_id": "col-student", "data_type": "string"},
        {"column_name": "semester", "column_id": "col-semester", "data_type": "string"},
        {"column_name": "status", "column_id": "col-status", "data_type": "string"},
        {"column_name": "score", "column_id": "col-score", "data_type": "double"},
    ]
    return {
        "environment_name": "dev",
        "table_id": "table-orders",
        "contract_id": "contract-orders",
        "contract_version": 2,
        "table_name": "orders",
        "columns": [row["column_name"] for row in rows],
        "column_ids": {row["column_name"]: row["column_id"] for row in rows},
        "catalogue_profile_rows": rows,
        "existing_rules": list(existing),
    }


def test_registry_is_exactly_the_runtime_rule_vocabulary():
    """Verify that DQ authoring definitions match the runtime rule vocabulary."""
    assert set(DQ_RULE_DEFINITIONS) == FINAL_RULES == set(DQ_RULE_TYPES) == set(shared.DQ_RULE_TYPES)
    for name, definition in DQ_RULE_DEFINITIONS.items():
        assert definition["rule_id"] == name
        assert definition["label"]
        assert definition["column_selection"] in {"independent", "group", "ordered_pair", "conditional"}
        assert int(definition.get("minimum_columns", 1)) >= 1
        assert isinstance(definition["parameters"], dict)


def test_rule_definitions_capture_required_parameter_contracts_and_defaults():
    """Verify that rule definitions capture parameter contracts and defaults."""
    assert DQ_RULE_DEFINITIONS["missing_values"]["parameters"]["maximum_null_percent"] == {
        "label": "Maximum null percent",
        "type": "number",
        "required": True,
        "default": 0,
        "minimum": 0,
        "maximum": 100,
    }
    assert DQ_RULE_DEFINITIONS["unique_combination"]["column_selection"] == "group"
    assert DQ_RULE_DEFINITIONS["unique_combination"]["minimum_columns"] == 2
    assert DQ_RULE_DEFINITIONS["compare_columns"]["column_selection"] == "ordered_pair"
    assert DQ_RULE_DEFINITIONS["compare_columns"]["maximum_columns"] == 2
    assert DQ_RULE_DEFINITIONS["required_when"]["column_selection"] == "conditional"
    assert DQ_RULE_DEFINITIONS["conditional_value"]["maximum_columns"] == 1
    assert DQ_RULE_DEFINITIONS["value_range"]["at_least_one_of"] == ("minimum", "maximum")


def test_parameter_conversion_and_validation_are_definition_driven():
    """Verify that parameter conversion and validation follow rule definitions."""
    definition = DQ_RULE_DEFINITIONS["value_range"]
    controls = {
        "minimum": SimpleNamespace(value="0"),
        "minimum_inclusive": SimpleNamespace(value=False),
        "maximum": SimpleNamespace(value="100"),
        "maximum_inclusive": SimpleNamespace(value=True),
    }
    assert _collect_parameters(definition, controls) == {
        "minimum": 0,
        "minimum_inclusive": False,
        "maximum": 100,
        "maximum_inclusive": True,
    }
    controls["minimum"].value = ""
    controls["maximum"].value = ""
    with pytest.raises(ValueError, match="at least one"):
        _collect_parameters(definition, controls)


def test_missing_values_percentage_validation_has_clear_bounds():
    """Verify that percentage parameters enforce clear inclusive bounds."""
    definition = DQ_RULE_DEFINITIONS["missing_values"]
    control = {"maximum_null_percent": SimpleNamespace(value="101")}
    with pytest.raises(ValueError, match="at most 100"):
        _collect_parameters(definition, control)
    control["maximum_null_percent"].value = "-1"
    with pytest.raises(ValueError, match="at least 0"):
        _collect_parameters(definition, control)
    control["maximum_null_percent"].value = "5"
    assert _collect_parameters(definition, control) == {"maximum_null_percent": 5.0}


def test_independent_rules_create_one_canonical_row_per_selected_column():
    """Verify that independent rules create one canonical row per selected column."""
    records = authoring.dq_records_from_selection(
        _state(), rule_id="unique_values", selected_columns=["student_id", "semester"], column_selection="independent"
    )
    assert len(records) == 2
    assert [row["column_id"] for row in records] == ["col-student", "col-semester"]
    assert len({row["guardrail_rule_id"] for row in records}) == 2
    assert [json.loads(row["rule_parameters_json"])["columns"] for row in records] == [["student_id"], ["semester"]]
    assert all(row["contract_id"] == "contract-orders" and row["contract_version"] == 2 for row in records)
    assert all("table_id" not in row for row in records)
    assert all(row["rule_id"] == "unique_values" for row in records)


def test_independent_rule_identity_is_stable_across_parameter_versions():
    """Verify that independent rule identity is stable across parameter versions."""
    first = authoring.dq_records_from_selection(
        _state(), rule_id="missing_values", selected_columns=["student_id"], parameters={"maximum_null_percent": 0}
    )[0]
    existing = [{**first, "guardrail_version": 3}]
    second = authoring.dq_records_from_selection(
        _state(existing), rule_id="missing_values", selected_columns=["student_id"], parameters={"maximum_null_percent": 5}
    )[0]
    assert first["guardrail_rule_id"] == second["guardrail_rule_id"]
    assert second["guardrail_version"] == 4


def test_group_rule_creates_one_row_and_preserves_all_columns():
    """Verify that grouped rules preserve all selected columns in one row."""
    record = authoring.dq_records_from_selection(
        _state(), rule_id="unique_combination", selected_columns=["student_id", "semester"], column_selection="group"
    )[0]
    assert record["column_id"] == ""
    assert json.loads(record["rule_parameters_json"])["columns"] == ["student_id", "semester"]


def test_ordered_pair_preserves_left_right_order_and_operator_identity():
    """Verify that ordered-pair identity preserves left/right order and operator."""
    left_right = authoring.dq_records_from_selection(
        _state(), rule_id="compare_columns", selected_columns=["score", "semester"], parameters={"operator": ">="}, column_selection="ordered_pair"
    )[0]
    reversed_columns = authoring.dq_records_from_selection(
        _state(), rule_id="compare_columns", selected_columns=["semester", "score"], parameters={"operator": ">="}, column_selection="ordered_pair"
    )[0]
    changed_operator = authoring.dq_records_from_selection(
        _state(), rule_id="compare_columns", selected_columns=["score", "semester"], parameters={"operator": "<="}, column_selection="ordered_pair"
    )[0]
    assert json.loads(left_right["rule_parameters_json"]) == {"columns": ["score", "semester"], "operator": ">="}
    assert left_right["guardrail_rule_id"] != reversed_columns["guardrail_rule_id"]
    assert left_right["guardrail_rule_id"] != changed_operator["guardrail_rule_id"]


def test_conditional_rule_preserves_condition_and_target_relationship():
    """Verify that conditional rules preserve condition and target relationships."""
    record = authoring.dq_records_from_selection(
        _state(),
        rule_id="conditional_value",
        selected_columns=["student_id"],
        parameters={
            "condition_column": "status",
            "condition_operator": "=",
            "condition_value": "Graduated",
            "expected_value": "required",
        },
        column_selection="conditional",
    )[0]
    assert record["column_id"] == ""
    assert json.loads(record["rule_parameters_json"]) == {
        "columns": ["student_id"],
        "condition_column": "status",
        "condition_operator": "=",
        "condition_value": "Graduated",
        "expected_value": "required",
    }


def test_dq_records_contain_no_obsolete_stage4_fields():
    """Verify that DQ rows omit obsolete Stage 4 metadata fields."""
    obsolete = {
        "configuration_version", "metadata_table_key", "metadata_column_key", "dataset_name", "table_name",
        "column_name", "rule_key", "review_status", "review_state", "action_type", "source_notebook_type", "created_by_role",
    }
    records = authoring.dq_records_from_selection(
        _state(), rule_id="unique_values", selected_columns=["student_id", "semester"]
    )
    assert all(not (set(row) & obsolete) for row in records)


def test_widget_uses_visible_checkboxes_and_dynamic_parameters(monkeypatch):
    """Verify visible column checkboxes and dynamic rule parameter controls."""
    from tests.unit.test_widget_author_guardrails import _install_fake_notebook_widgets

    module = importlib.import_module("fabricops_kit.widgets.widget_author_dq_rules")
    widgets = _install_fake_notebook_widgets(monkeypatch, auto_observe=True)

    def fake_targets(config, env, *, spark_session, widgets, on_change):
        state = _state()
        on_change(state)
        return state, widgets.Dropdown(options=[("orders", "table-orders")]), {
            "target_summary": widgets.HTML(), "refresh_target": lambda: None,
        }

    monkeypatch.setattr(module.authoring, "load_guardrail_authoring_targets", fake_targets)
    widget = module.widget_author_dq_rules(spark_session=object(), context={"config": object(), "env": "dev"})
    controls = widget["controls"]
    assert list(controls["columns"]) == _state()["columns"]
    assert "maximum_null_percent" in controls["parameter_controls"]
    controls["rule_type"].value = "allowed_values"
    assert set(controls["parameter_controls"]) == {"allowed_values"}
    assert list(controls["columns"]) == _state()["columns"]
    assert isinstance(widgets, SimpleNamespace)


def test_widget_preview_shows_multiple_independent_rows_and_only_canonical_fields(monkeypatch):
    """Verify multiple independent preview rows with canonical fields only."""
    from tests.unit.test_widget_author_guardrails import _install_fake_notebook_widgets

    module = importlib.import_module("fabricops_kit.widgets.widget_author_dq_rules")
    _install_fake_notebook_widgets(monkeypatch)

    def fake_targets(config, env, *, spark_session, widgets, on_change):
        state = _state()
        on_change(state)
        return state, widgets.Dropdown(options=[("orders", "table-orders")]), {
            "target_summary": widgets.HTML(), "refresh_target": lambda: None,
        }

    monkeypatch.setattr(module.authoring, "load_guardrail_authoring_targets", fake_targets)
    widget = module.widget_author_dq_rules(
        spark_session=object(), context={"config": object(), "env": "dev"},
        rule_type="unique_values", selected_columns=["student_id", "semester"],
    )
    rows = widget["build_records"]()
    assert len(rows) == 2
    preview = widget["controls"]["preview"].value
    assert preview.count('"guardrail_rule_id"') == 2
    assert preview.count('"guardrail_version"') == 2
    assert '"column_id": "col-student"' in preview
    assert '"configuration_version"' not in preview
    assert '"metadata_table_key"' not in preview


def test_widget_save_uses_same_canonical_guardrail_writer(monkeypatch):
    """Verify that the DQ widget uses the shared canonical Guardrail writer."""
    from tests.unit.test_widget_author_guardrails import _install_fake_notebook_widgets

    module = importlib.import_module("fabricops_kit.widgets.widget_author_dq_rules")
    _install_fake_notebook_widgets(monkeypatch)
    saved = []

    def fake_targets(config, env, *, spark_session, widgets, on_change):
        state = _state()
        on_change(state)
        return state, widgets.Dropdown(options=[("orders", "table-orders")]), {
            "target_summary": widgets.HTML(), "refresh_target": lambda: None,
        }

    monkeypatch.setattr(module.authoring, "load_guardrail_authoring_targets", fake_targets)
    monkeypatch.setattr(module.authoring, "canonicalize_records", lambda records, **kwargs: records)
    monkeypatch.setattr(module.authoring, "write_rule_records", lambda records, **kwargs: saved.append(records))
    widget = module.widget_author_dq_rules(
        spark_session=object(), context={"config": object(), "env": "dev"},
        rule_type="unique_values", selected_columns=["student_id"],
    )
    widget["save"]()
    assert len(saved) == 1
    assert saved[0][0]["column_id"] == "col-student"
    assert saved[0][0]["guardrail_version"] == 1


def test_authoring_widgets_are_independent_and_use_shared_storage_model():
    """Verify independent widget orchestration with shared storage primitives."""
    module = importlib.import_module("fabricops_kit.widgets.widget_author_dq_rules")
    dq_source = inspect.getsource(module)
    assert "widget_author_guardrails(" not in dq_source
    assert "widget_select_guardrail_target" not in dq_source
    assert "authoring.canonicalize_records" in dq_source
    assert "authoring.write_rule_records" in dq_source
