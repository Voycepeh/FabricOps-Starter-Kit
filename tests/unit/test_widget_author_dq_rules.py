"""Focused contracts for standalone lightweight DQ authoring."""

import json
from types import SimpleNamespace

import pytest

from fabricops_kit.pipeline.guardrails_shared import DQ_RULE_TYPES
from fabricops_kit.widgets import shared
from fabricops_kit.widgets.widget_author_dq_rules import DQ_RULE_DEFINITIONS, _collect_parameters


FINAL_RULES = {
    "null_rate_below",
    "non_empty_string",
    "unique",
    "unique_combination",
    "accepted_values",
    "not_in_values",
    "between",
    "regex_match",
    "required_when",
    "value_when",
    "compare_columns",
}
REMOVED_RULES = {
    "not_null",
    "greater_than",
    "greater_than_or_equal",
    "less_than",
    "less_than_or_equal",
    "date_not_future",
    "date_between",
    "freshness",
    "max_age_days",
    "column_pair_equal",
    "column_a_gte_column_b",
    "column_a_gt_column_b",
    "expression_true",
}


def _state():
    return {
        "environment_name": "dev",
        "dataset_name": "sales",
        "table_name": "orders",
        "metadata_table_key": "lakehouse.silver.orders",
        "governance_mode": "ungoverned",
        "columns": ["student_id", "semester", "status"],
    }


def test_registry_is_exactly_the_lightweight_canonical_vocabulary():
    """Keep authoring and runtime aligned on the intentional breaking rule set."""
    assert set(DQ_RULE_DEFINITIONS) == FINAL_RULES == set(DQ_RULE_TYPES) == set(shared.DQ_RULE_TYPES)
    assert REMOVED_RULES.isdisjoint(DQ_RULE_DEFINITIONS)
    assert DQ_RULE_DEFINITIONS["unique_combination"]["column_selection"] == "group"
    assert DQ_RULE_DEFINITIONS["required_when"]["column_selection"] == "conditional"
    assert DQ_RULE_DEFINITIONS["compare_columns"]["column_selection"] == "ordered_pair"


def test_independent_unique_rules_create_one_record_per_column():
    """Keep independent uniqueness distinct from combined uniqueness."""
    records = shared._dq_records_from_selection(
        _state(), rule_type="unique", selected_columns=["student_id", "semester"]
    )
    assert [record["column_name"] for record in records] == ["student_id", "semester"]
    assert [json.loads(record["rule_parameters_json"])["columns"] for record in records] == [
        ["student_id"],
        ["semester"],
    ]


def test_group_and_ordered_rules_preserve_columns_and_deterministic_identity():
    """Store one logical rule and include columns and operator in its identity."""
    grouped = shared._dq_records_from_selection(
        _state(),
        rule_type="unique_combination",
        selected_columns=["student_id", "semester"],
        column_selection="group",
    )[0]
    compared = shared._dq_records_from_selection(
        _state(),
        rule_type="compare_columns",
        selected_columns=["student_id", "semester"],
        parameters={"operator": ">="},
        column_selection="ordered_pair",
    )[0]
    reversed_operator = shared._dq_records_from_selection(
        _state(),
        rule_type="compare_columns",
        selected_columns=["student_id", "semester"],
        parameters={"operator": "<="},
        column_selection="ordered_pair",
    )[0]

    assert json.loads(grouped["rule_parameters_json"])["columns"] == ["student_id", "semester"]
    assert json.loads(compared["rule_parameters_json"]) == {
        "columns": ["student_id", "semester"],
        "operator": ">=",
    }
    assert compared["rule_id"] != reversed_operator["rule_id"]


def test_between_collects_comparable_bounds_and_inclusivity():
    """Preserve numeric, date, one-sided, and inclusive/exclusive controls."""
    definition = DQ_RULE_DEFINITIONS["between"]
    controls = {
        "minimum_value": SimpleNamespace(value="2026-01-01"),
        "minimum_inclusive": SimpleNamespace(value=False),
        "maximum_value": SimpleNamespace(value=""),
        "maximum_inclusive": SimpleNamespace(value=True),
    }
    assert _collect_parameters(definition, controls) == {
        "minimum_value": "2026-01-01",
        "minimum_inclusive": False,
        "maximum_value": None,
        "maximum_inclusive": True,
    }
    controls["minimum_value"].value = ""
    with pytest.raises(ValueError, match="at least one"):
        _collect_parameters(definition, controls)


def test_structured_condition_and_value_parameters_are_canonical_scalars():
    """Store controlled condition fields without arbitrary SQL expressions."""
    definition = DQ_RULE_DEFINITIONS["value_when"]
    controls = {
        "condition_column": SimpleNamespace(value="status"),
        "condition_operator": SimpleNamespace(value="="),
        "condition_value": SimpleNamespace(value="Graduated"),
        "expected_value": SimpleNamespace(value="false"),
    }
    assert _collect_parameters(definition, controls) == {
        "condition_column": "status",
        "condition_operator": "=",
        "condition_value": "Graduated",
        "expected_value": False,
    }


def test_widget_changes_preview_only_until_explicit_save(monkeypatch):
    """Prevent target, rule, column, and parameter changes from writing metadata."""
    from tests.unit.test_widget_author_guardrails import _install_fake_notebook_widgets
    import fabricops_kit.widgets.widget_author_dq_rules as module

    _install_fake_notebook_widgets(monkeypatch, auto_observe=True)
    callbacks = {}
    writes = []

    def fake_targets(config, env, *, spark_session, widgets, on_change):
        state = {
            **_state(),
            "catalogue_profile_rows": [
                {"column_name": "student_id", "data_type": "string"},
                {"column_name": "semester", "data_type": "string"},
                {"column_name": "status", "data_type": "string"},
            ],
            "existing_rules": [],
        }
        callbacks["target"] = on_change
        on_change(state)
        return (
            state,
            widgets.Dropdown(options=["orders"]),
            {
                "target_summary": widgets.HTML(),
                "refresh_target": lambda: None,
            },
        )

    monkeypatch.setattr(module.shared, "_load_guardrail_authoring_targets", fake_targets)
    monkeypatch.setattr(module.shared, "_write_rule_records", lambda records, **kwargs: writes.append(records))

    widget = module.widget_author_dq_rules(spark_session=object(), context={"config": object(), "env": "dev"})
    widget["controls"]["parameter_controls"]["max_null_percent"].value = "5"
    widget["controls"]["rule_type"].value = "unique"
    next(iter(widget["controls"]["columns"].values())).value = False
    callbacks["target"](widget["state"])

    assert writes == []
    widget["save"]()
    assert len(writes) == 1
