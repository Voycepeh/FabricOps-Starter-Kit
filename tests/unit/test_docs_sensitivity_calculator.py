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


def test_applied_policy_replaces_the_default_assessment():
    """Apply one policy at a time to the same profile and definitions."""
    scenario = next(case for case in SCENARIOS if case["id"] == "T04")
    loaded = _message(action="load", text=json.dumps(scenario["profile"]), csv=False)
    request = {"action": "assess", "profile": loaded["profile"], "definitions": scenario["definitions"],
               "sensitiveLinkage": scenario["sensitiveLinkage"]}
    default = _message(**request, policy=json.dumps(loaded["defaultPolicy"]))
    edited = loaded["defaultPolicy"]
    edited["sensitivity_assessment"]["combinations"] = []
    edited["sensitivity_assessment"]["suspected_handling"] = "Restricted"
    applied = _message(**request, policy=json.dumps(edited))
    assert default["classification"] == "Confidential"
    assert applied["classification"] == "Restricted"
    assert applied["columns"] == default["columns"]
    assert {column["classification"] for column in applied["columns"]} == {"Restricted"}


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
    assert result == expected
    assert expected["classification"] is None
    assert expected["minimum_handling_classification"] == "Confidential"
    assert expected["columns"][0]["evidence"] == ["pattern_match:email"]


def test_csv_profiles_rows_and_scans_values_beyond_the_first_five():
    """Build deterministic statistics and apply the engine to rare value matches."""
    rows = [f"{index},record-{index}," for index in range(1, 10)]
    rows.append('10,"Synthetic note, contact person@example.org",2000-01-01')
    csv_text = "\ufeffmonthly_salary,remarks,start_date\n" + "\n".join(rows)
    loaded = _message(action="dataset", text=csv_text)
    assert loaded["columns"] == [
        {"column_name": "monthly_salary", "data_type": "long", "row_count": 10, "null_count": 0, "distinct_count": 10},
        {"column_name": "remarks", "data_type": "string", "row_count": 10, "null_count": 0, "distinct_count": 10},
        {"column_name": "start_date", "data_type": "date", "row_count": 10, "null_count": 9, "distinct_count": 1},
    ]
    definitions = loaded["definitions"]
    assert definitions["monthly_salary"]["category"] == "payroll"
    assert definitions["remarks"]["category"] is None
    assert "header suggests payroll" in definitions["monthly_salary"]["description"]
    result = _message(action="assess", profile=loaded["profile"], definitions=definitions,
                      policy=json.dumps(loaded["defaultPolicy"]))
    assert result["classification"] == "Confidential"
    assert result["scope"]["kind"] == "full_table"
    assert result["columns"][0]["is_personal_data"] is True
    remarks = result["columns"][1]
    assert remarks["evidence"] == ["pattern_match:email"]
    assert remarks["classification"] is None
    assert remarks["minimum_handling_classification"] == "Confidential"
    assert remarks["is_personal_data"] is None
    assert "person@example.org" not in json.dumps(result)


def test_csv_profiling_preserves_identifier_strings_and_mixed_numeric_types():
    """Count distinct input values without coercing leading zeroes."""
    loaded = _message(action="dataset", text="account,balance,empty\n001,50, \n001,12.50,\n002,-8,\n")
    assert [row["data_type"] for row in loaded["columns"]] == ["string", "decimal", "unknown"]
    assert [row["distinct_count"] for row in loaded["columns"]] == [2, 3, 0]


@pytest.mark.parametrize(("text", "match"), [
    ("name,name\na,b", "unique column names"),
    ("name,email\na", "Expected 2"),
    ("name,email", "one data row"),
])
def test_dataset_rejects_malformed_csv(text, match):
    """Keep missing data, duplicate columns, and uneven rows out of assessment."""
    with pytest.raises(ValueError, match=match):
        _message(action="dataset", text=text)


@pytest.mark.parametrize(("text", "csv_input"), [
    ('{"email": {"description": "Official address", "category": "business_contact"}}', False),
    ("column_name,description,category\nemail,Official address,business_contact", True),
])
def test_dictionary_applies_explicit_definitions_to_the_dataset(text, csv_input):
    """Use user-supplied context to distinguish work contact and possible PII."""
    loaded = _message(action="dataset", text="email\nperson@example.org\n")
    definitions = _message(action="dictionary", text=text, csv=csv_input, columns=["email"],
                           categories=["business_contact"])["definitions"]
    result = _message(action="assess", profile=loaded["profile"], definitions=definitions,
                      policy=json.dumps(loaded["defaultPolicy"]))
    assert result["classification"] == "Restricted"
    assert result["columns"][0]["is_personal_data"] is True


def test_dictionary_requires_matching_columns_and_categories():
    """Reject stale dictionary names and unsupported policy categories."""
    request = {"action": "dictionary", "csv": False, "columns": ["email"], "categories": ["business_contact"]}
    with pytest.raises(ValueError, match="does not match"):
        _message(**request, text='{"contact": "Official address"}')
    with pytest.raises(ValueError, match="configured business category"):
        _message(**request, text='{"email": {"description": "Business email", "category": "unknown"}}')


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
    assert result["classification"] == case["expected"]["classification"]
    assert result["minimum_handling_classification"] == case["expected"]["handling"]
    if "spark" in case:
        assert result["human_review_required"]
        assert result["dataset_findings"][0]["code"] == "joint_group_sizes_unverified"


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
