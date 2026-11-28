"""Check the browser file and policy inputs against the FabricOps engine."""

import json
from pathlib import Path

import pytest

from docs._tools.sensitivity_calculator import handle_message
from fabricops_kit import GovernanceConfig, assess_data_sensitivity


SCENARIOS = json.loads(
    (Path(__file__).resolve().parents[2] / "docs" / "assets" / "sensitivity-scenarios.json").read_text()
)


def _message(**request):
    return json.loads(handle_message(json.dumps(request)))


def test_example_compares_the_dataset_combination_without_changing_column_labels():
    """Compare the combination rule at dataset and column level."""
    scenario = next(case for case in SCENARIOS if case["id"] == "T04")
    loaded = _message(action="load", text=json.dumps(scenario["profile"]), csv=False)
    edited = loaded["defaultPolicy"]
    edited["sensitivity_assessment"]["combinations"] = []
    edited["sensitivity_assessment"]["suspected_handling"] = "Restricted"
    result = _message(action="assess", profile=loaded["profile"], definitions=scenario["definitions"],
                      policy=json.dumps(edited), sensitiveLinkage=scenario["sensitiveLinkage"])
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


def test_library_includes_each_validation_case_and_all_default_categories():
    """Keep the selectable library complete and categories covered."""
    assert [case["id"] for case in SCENARIOS] == [
        *(f"C{number:02}" for number in range(1, 34)),
        *(f"T{number:02}" for number in range(1, 19)),
        "S01", "S02",
    ]
    categories = {definition["category"] for case in SCENARIOS
                  for definition in case["definitions"].values() if "category" in definition}
    assert set(GovernanceConfig().sensitivity_assessment["categories"]) == categories


@pytest.mark.parametrize("case", SCENARIOS, ids=[case["id"] for case in SCENARIOS])
def test_selectable_scenario_matches_browser_result(case):
    """Check each shipped profile with the same calculator entry points as the page."""
    loaded = _message(action="load", text=json.dumps(case["profile"]), csv=False)
    result = _message(action="assess", profile=loaded["profile"], definitions=case["definitions"],
                      policy=json.dumps(loaded["defaultPolicy"]), sensitiveLinkage=case.get("sensitiveLinkage"))
    assert result["current"] == result["default"]
    assert result["default"]["classification"] == case["expected"]["classification"]
    assert result["default"]["minimum_handling_classification"] == case["expected"]["handling"]
    if "spark" in case:
        assert result["default"]["human_review_required"]
        assert result["default"]["dataset_findings"][0]["code"] == "joint_group_sizes_unverified"


@pytest.mark.parametrize("case", [case for case in SCENARIOS if "spark" in case], ids=["S01", "S02"])
def test_scenario_spark_reference_matches_fabricops(case, spark_session):
    """Check that the displayed Spark reference comes from the same engine."""
    spark = case["spark"]
    dataframe = spark_session.createDataFrame(spark["rows"], list(case["definitions"]))
    result = assess_data_sensitivity(
        case["profile"], column_definitions=case["definitions"], dataframe=dataframe,
    )
    assert result["classification"] == spark["expected"]["classification"]
    assert result["minimum_handling_classification"] == spark["expected"]["handling"]
