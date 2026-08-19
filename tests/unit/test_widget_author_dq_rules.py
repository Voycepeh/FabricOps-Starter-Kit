"""Focused contracts for standalone normalized DQ authoring."""

from __future__ import annotations

import inspect
import json
import sys
from types import SimpleNamespace

import pytest

from fabricops_kit.pipeline.guardrails_shared import DQ_RULE_TYPES
from fabricops_kit.widgets import guardrail_authoring_shared as authoring
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
        {
            "column_name": "student_id",
            "column_id": "col-student",
            "data_type": "string",
        },
        {
            "column_name": "semester",
            "column_id": "col-semester",
            "data_type": "string",
        },
        {
            "column_name": "status",
            "column_id": "col-status",
            "data_type": "string",
        },
        {
            "column_name": "score",
            "column_id": "col-score",
            "data_type": "double",
        },
    ]
    return {
        "environment_name": "dev",
        "table_id": "table-orders",
        "table_name": "orders",
        "columns": [row["column_name"] for row in rows],
        "column_ids": {row["column_name"]: row["column_id"] for row in rows},
        "catalogue_profile_rows": rows,
        "existing_rules": list(existing),
    }


def test_registry_is_exactly_the_runtime_rule_vocabulary():
    """Verify that DQ authoring definitions match the runtime rule vocabulary."""
    assert (
        set(DQ_RULE_DEFINITIONS)
        == FINAL_RULES
        == set(DQ_RULE_TYPES)
        == set(shared.DQ_RULE_TYPES)
    )
    for name, definition in DQ_RULE_DEFINITIONS.items():
        assert definition["rule_id"] == name
        assert definition["label"]
        assert definition["column_selection"] in {
            "independent",
            "group",
            "ordered_pair",
            "conditional",
        }
        assert int(definition.get("minimum_columns", 1)) >= 1
        assert isinstance(definition["parameters"], dict)


def test_rule_definitions_capture_required_parameter_contracts_and_defaults():
    """Verify that rule definitions capture parameter contracts and defaults."""
    assert DQ_RULE_DEFINITIONS["missing_values"]["parameters"][
        "maximum_null_percent"
    ] == {
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
    assert DQ_RULE_DEFINITIONS["value_range"]["at_least_one_of"] == (
        "minimum",
        "maximum",
    )


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
    assert _collect_parameters(definition, control) == {
        "maximum_null_percent": 5.0
    }


def test_authoring_widgets_are_independent_and_use_shared_private_storage_model():
    """Verify independent widget orchestration with shared private storage primitives."""
    from fabricops_kit.widgets import widget_author_dq_rules as public_callable

    dq_source = inspect.getsource(sys.modules[public_callable.__module__])
    assert "widget_author_guardrails(" not in dq_source
    assert "widget_select_guardrail_target" not in dq_source
    assert "authoring._canonicalize_records" in dq_source
    assert "shared._write_rule_records" in dq_source
