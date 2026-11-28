"""Run the profile-only Data Sensitivity Assessment in the docs calculator."""

import csv
import io
import json
from types import SimpleNamespace

from fabricops_kit import GovernanceConfig, assess_data_sensitivity
from fabricops_kit.data_contract.shared import assessment_profile_evidence


DEFAULT = GovernanceConfig()
SAMPLE = {
    "profile_scope": "full_table",
    "profile": [
        {"column_name": "staff_number", "data_type": "int", "row_count": 120},
        {"column_name": "salary_band", "data_type": "string", "row_count": 120},
    ],
}
SAMPLE_DEFINITIONS = {
    "staff_number": {"description": "Internal staff number", "category": "institutional_identifier"},
    "salary_band": {"description": "Employment statistics grouped by salary band",
                    "category": "deidentified_employment_statistics"},
}
PROFILE_FIELDS = {
    "column_name", "data_type", "row_count", "non_null_count", "null_count", "distinct_count",
    "min_value", "max_value", "profile_snapshot_id", "profile_scope",
}


def _profile_payload(text, is_csv):
    if is_csv:
        rows = csv.DictReader(io.StringIO(text))
        if not rows.fieldnames or "column_name" not in {name.lower() for name in rows.fieldnames}:
            raise ValueError("CSV profiles need a COLUMN_NAME header.")
        payload = {"profile": [
            {key.lower(): value for key, value in row.items() if key is not None and value != ""}
            for row in rows
        ]}
        for row in payload["profile"]:
            if "row_count" in row:
                row["row_count"] = int(row["row_count"])
    else:
        payload = json.loads(text)
        if isinstance(payload, list):
            payload = {"profile": payload}
    return payload


def _local_profile(payload):
    columns, scope, _, single, _ = assessment_profile_evidence(payload, None)
    if not columns:
        raise ValueError("Provide a profile with at least one column.")
    if len(columns) > 500:
        raise ValueError("Use a profile with at most 500 columns.")
    # Retain the engine-selected values and scope after validating the uploaded snapshot.
    # The docs calculator cannot resolve physical asset identity or approve treatment.
    rows = [{key: value for key, value in column.items() if key in PROFILE_FIELDS}
            for column in columns.values()]
    extra_values = {
        name: column["observed_values"][sum(column.get(key) is not None for key in ("min_value", "max_value")):]
        for name, column in columns.items()
    }
    if not isinstance(scope["kind"], str):
        raise ValueError("PROFILE_SCOPE must be a string.")
    if single:
        return {"kind": "column", "profile": rows[0], "profile_scope": scope["kind"],
                "values": [{"value": value} for value in next(iter(extra_values.values()))]}
    return {"profile": rows, "profile_scope": scope["kind"], "frequency_profile": [
        {"column_name": name, "value": value} for name, values in extra_values.items() for value in values
    ]}


def _policy(config):
    return {"classification_levels": config.classification_levels,
            "sensitivity_assessment": config.sensitivity_assessment}


def _assess(profile, definitions, config, target=None):
    return assess_data_sensitivity(
        profile, column_definitions=definitions, target_classification=target, use_ai=False,
        context={"config": SimpleNamespace(governance_config=config), "scope_workspace_id": "docs"},
    )


def handle_message(request_json):
    """Return only the browser's JSON-serializable result."""
    request = json.loads(request_json)
    action = request["action"]
    if action == "load":
        example = request.get("example")
        profile = _local_profile(SAMPLE if example else _profile_payload(request["text"], request["csv"]))
        rows = profile["profile"]
        return json.dumps({
            "profile": json.dumps(profile),
            "columns": [{key: row.get(key) for key in ("column_name", "data_type")}
                        for row in (rows if isinstance(rows, list) else [rows])],
            "defaultPolicy": _policy(DEFAULT),
            "definitions": SAMPLE_DEFINITIONS if example else {},
        })

    settings = json.loads(request["policy"])
    allowed = {"classification_levels", "sensitivity_assessment", "sensitivity_rules"}
    if not isinstance(settings, dict) or settings.keys() - allowed:
        raise ValueError("Enter a JSON object containing the GovernanceConfig policy settings.")
    config = GovernanceConfig(**settings)
    if action == "policy":
        return json.dumps(_policy(config))
    profile = json.loads(request["profile"])
    definitions = request["definitions"]
    default_categories = DEFAULT.sensitivity_assessment["categories"]
    baseline = {
        name: {**definition, "category": definition.get("category")
               if definition.get("category") in default_categories else None}
        for name, definition in definitions.items()
    }
    return json.dumps({
        "default": _assess(profile, baseline, DEFAULT),
        "current": _assess(profile, definitions, config, request.get("target")),
    })
