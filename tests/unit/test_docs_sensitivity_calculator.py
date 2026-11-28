"""Check the browser file and policy inputs against the FabricOps engine."""

import json

import pytest

from docs._tools.sensitivity_calculator import handle_message
from fabricops_kit import assess_data_sensitivity


def _message(**request):
    return json.loads(handle_message(json.dumps(request)))


def test_example_compares_the_dataset_combination_without_changing_column_labels():
    """Compare the combination rule at dataset and column level."""
    loaded = _message(action="load", example=True)
    edited = loaded["defaultPolicy"]
    edited["sensitivity_assessment"]["combinations"] = []
    result = _message(action="assess", profile=loaded["profile"], definitions=loaded["definitions"],
                      policy=json.dumps(edited))
    baseline = result["default"]
    current = result["current"]
    assert baseline["classification"] == "Confidential"
    assert current["classification"] == "Restricted"
    assert current["columns"] == baseline["columns"]
    assert {column["classification"] for column in current["columns"]} == {"Restricted"}


def test_json_snapshot_retains_engine_selected_frequency_and_scope():
    """Pass the same profile evidence as the notebook callable."""
    profile = {
        "profile_scope": "full_table",
        "profile": [{"COLUMN_NAME": "contact", "DATA_TYPE": "string", "PROFILE_SNAPSHOT_ID": "selected"}],
        "frequency_profile": [
            {"COLUMN_NAME": "contact", "VALUE": "person@example.com", "PROFILE_SNAPSHOT_ID": "selected"},
            {"COLUMN_NAME": "contact", "TABLE_ID": "table", "VALUE": "4111111111111111",
             "PROFILE_SNAPSHOT_ID": "other"},
        ],
    }
    definitions = {"contact": {"description": "Personal email"}}
    loaded = _message(action="load", text=json.dumps(profile), csv=False)
    result = _message(action="assess", profile=loaded["profile"], definitions=definitions,
                      policy=json.dumps(loaded["defaultPolicy"]))
    expected = assess_data_sensitivity(profile, column_definitions=definitions)
    assert result["current"] == expected
    assert expected["classification"] is None
    assert expected["minimum_handling_classification"] == "Confidential"
    assert expected["columns"][0]["evidence"] == ["pattern_match:email"]


def test_csv_uses_unknown_scope_when_profile_coverage_is_unspecified():
    """Leave missing CSV coverage open for review."""
    loaded = _message(action="load", text="COLUMN_NAME,DATA_TYPE,ROW_COUNT\nprice,int,4\n", csv=True)
    result = _message(action="assess", profile=loaded["profile"], definitions={
        "price": {"category": "authorised_public_release"},
    }, policy=json.dumps(loaded["defaultPolicy"]))["current"]
    assert result["scope"]["kind"] == "unknown"
    assert result["human_review_required"]


def test_mixed_profile_snapshots_are_rejected_before_assessment():
    """Reject rows from different snapshots before policy evaluation."""
    profile = [{"COLUMN_NAME": name, "PROFILE_SNAPSHOT_ID": name} for name in ("first", "second")]
    with pytest.raises(ValueError, match="more than one snapshot"):
        _message(action="load", text=json.dumps(profile), csv=False)
