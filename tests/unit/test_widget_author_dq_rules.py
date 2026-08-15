"""Focused contracts for standalone DQ rule authoring."""

import json
from types import SimpleNamespace

from fabricops_kit.widgets import shared
from fabricops_kit.widgets.widget_author_dq_rules import DQ_RULE_DEFINITIONS, _collect_parameters


def _state():
    return {
        "environment_name": "dev",
        "dataset_name": "sales",
        "table_name": "orders",
        "metadata_table_key": "lakehouse.silver.orders",
        "governance_mode": "ungoverned",
        "columns": ["student_id", "semester", "status"],
    }


def test_registry_covers_the_canonical_dq_vocabulary():
    """Keep the widget registry aligned with every runtime-supported rule."""
    assert set(DQ_RULE_DEFINITIONS) == set(shared.DQ_RULE_TYPES)
    assert DQ_RULE_DEFINITIONS["unique_combination"]["column_selection"] == "group"
    assert DQ_RULE_DEFINITIONS["column_a_gte_column_b"]["column_selection"] == "ordered_pair"
    assert DQ_RULE_DEFINITIONS["expression_true"]["column_selection"] == "none"


def test_grouped_and_ordered_rules_create_one_canonical_record():
    """Preserve multi-column meaning instead of creating one rule per column."""
    for rule_type, mode in (("unique_combination", "group"), ("column_a_gte_column_b", "ordered_pair")):
        records = shared._dq_records_from_selection(
            _state(),
            rule_type=rule_type,
            selected_columns=["student_id", "semester"],
            column_selection=mode,
        )
        assert len(records) == 1
        assert records[0]["column_name"] == ""
        assert json.loads(records[0]["rule_parameters_json"])["columns"] == ["student_id", "semester"]


def test_expression_rule_creates_a_table_level_record_without_columns():
    """Represent expression_true using its canonical expression parameter."""
    records = shared._dq_records_from_selection(
        _state(),
        rule_type="expression_true",
        selected_columns=[],
        parameters={"expression": "student_id IS NOT NULL"},
        column_selection="none",
    )
    assert len(records) == 1
    assert json.loads(records[0]["rule_parameters_json"]) == {
        "columns": [],
        "expression": "student_id IS NOT NULL",
    }


def test_range_rules_accept_either_bound_and_reject_no_bounds():
    """Match the runtime min-value-or-max-value validation contract."""
    definition = DQ_RULE_DEFINITIONS["between"]
    assert _collect_parameters(
        definition,
        {"min_value": SimpleNamespace(value=""), "max_value": SimpleNamespace(value="100")},
    ) == {"min_value": None, "max_value": 100.0}
    assert _collect_parameters(
        DQ_RULE_DEFINITIONS["date_between"],
        {
            "min_value": SimpleNamespace(value="2026-01-01"),
            "max_value": SimpleNamespace(value=""),
        },
    ) == {"min_value": "2026-01-01", "max_value": None}

    try:
        _collect_parameters(
            definition,
            {"min_value": SimpleNamespace(value=""), "max_value": SimpleNamespace(value="")},
        )
    except ValueError as exc:
        assert "at least one" in str(exc)
    else:
        raise AssertionError("a range without either bound must be rejected")
