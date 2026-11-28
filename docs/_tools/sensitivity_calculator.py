"""Profile CSV data and run Data Sensitivity Assessment in the docs calculator."""

import csv
import io
import json
import re
from datetime import date
from types import SimpleNamespace

from fabricops_kit import GovernanceConfig, assess_data_sensitivity
from fabricops_kit.data_contract.assess_data_sensitivity import assessment_value_signals
from fabricops_kit.data_contract.shared import assessment_profile_evidence


DEFAULT = GovernanceConfig()
PROFILE_FIELDS = {
    "column_name", "data_type", "row_count", "non_null_count", "null_count", "distinct_count",
    "min_value", "max_value", "profile_snapshot_id", "profile_scope",
}


# Exact header aliases provide draft business context, never approval.
HEADER_CATEGORIES = {
    "personal_email": "personal_contact", "personal_phone": "personal_contact",
    "staff_number": "institutional_identifier", "student_number": "institutional_identifier",
    "employee_id": "institutional_identifier", "student_id": "institutional_identifier",
    "salary": "payroll", "base_salary": "payroll", "monthly_salary": "payroll",
    "exam_marks": "academic_record", "exam_grade": "academic_record",
    "medical_diagnosis": "health_record", "admission_decision": "admissions_record",
    "employee_bank_account": "employee_bank_account", "vendor_bank_account": "vendor_bank_account",
    "internal_budget": "internal_budget", "operating_budget": "internal_budget",
    "credit_card_number": "payment_card", "nric": "personal_identifier", "passport_number": "personal_identifier",
}
VALUE_DETECTORS = ("email", "phone", "payment_card", "nric_fin")
INTEGER = re.compile(r"[+-]?(?:0|[1-9][0-9]*)")
DECIMAL = re.compile(r"[+-]?(?:0|[1-9][0-9]*)\.[0-9]+")
ISO_DATE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


def _value_type(value):
    if value.lower() in {"true", "false"}:
        return "boolean"
    if INTEGER.fullmatch(value):
        return "long"
    if DECIMAL.fullmatch(value):
        return "decimal"
    if ISO_DATE.fullmatch(value):
        try:
            date.fromisoformat(value)
            return "date"
        except ValueError:
            pass
    return "string"


def _csv_records(text):
    reader = csv.reader(io.StringIO(text.removeprefix("\ufeff")), strict=True)
    for record in reader:
        if record:
            yield record


def _dataset_profile(text):
    records = _csv_records(text)
    names = [name.strip() for name in next(records, [])]
    if not names or "" in names or len(names) != len(set(names)):
        raise ValueError("The CSV needs a header with non-empty, unique column names.")
    if len(names) > 500:
        raise ValueError("Use a CSV with at most 500 columns.")

    values = [set() for _ in names]
    counts = [0] * len(names)
    types = [set() for _ in names]
    witnesses = [{} for _ in names]
    pending = [dict.fromkeys(VALUE_DETECTORS) for _ in names]
    row_count = 0
    for row_count, record in enumerate(records, 1):
        if len(record) != len(names):
            raise ValueError(f"Data row {row_count} has {len(record)} fields. Expected {len(names)}.")
        for index, raw in enumerate(record):
            if not (value := raw.strip()):
                continue
            counts[index] += 1
            if value in values[index]:
                continue
            values[index].add(value)
            if "string" not in types[index]:
                types[index].add(_value_type(value))
            if pending[index]:
                for signal in assessment_value_signals(value, pending[index]):
                    witnesses[index][signal] = value
                    del pending[index][signal]
    if not row_count:
        raise ValueError("Add at least one data row to the CSV.")

    profile, frequency, definitions = [], [], {}
    for index, name in enumerate(names):
        observed = types[index]
        kind = next(iter(observed), "unknown") if len(observed) <= 1 else (
            "decimal" if observed == {"long", "decimal"} else "string"
        )
        profile.append({
            "column_name": name, "data_type": kind, "row_count": row_count,
            "non_null_count": counts[index], "null_count": row_count - counts[index],
            "distinct_count": len(values[index]),
        })
        # One witness per detected pattern fits within the engine's frequency evidence limit.
        for value in dict.fromkeys(witnesses[index].values()):
            frequency.append({"column_name": name, "value": value})
        normalised = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        readable = re.sub(r"[_-]+", " ", name)
        category = HEADER_CATEGORIES.get(normalised)
        description = f"Values for {readable}."
        if category:
            description += f" The header suggests {category.replace('_', ' ')}."
        definitions[name] = {"description": description, "category": category}

    return {"profile": profile, "frequency_profile": frequency,
            "profile_scope": "full_table"}, definitions


def _dictionary(text, is_csv, names, categories):
    if is_csv:
        records = _csv_records(text)
        headings = [heading.strip().lower() for heading in next(records, [])]
        required = {"column_name", "description"}
        if len(headings) != len(set(headings)) or not required <= set(headings) or set(headings) - (required | {"category"}):
            raise ValueError("Dictionary CSV needs column_name and description headers. Category is optional.")
        entries = {}
        for row in records:
            if len(row) != len(headings):
                raise ValueError("Every dictionary row must match its headers.")
            entry = dict(zip(headings, row))
            name = entry.pop("column_name").strip()
            if name in entries:
                raise ValueError("The dictionary contains duplicate column names.")
            if not entry.get("category"):
                entry.pop("category", None)
            entries[name] = entry
    else:
        entries = json.loads(text.removeprefix("\ufeff"))
        if not isinstance(entries, dict):
            raise ValueError("Dictionary JSON must map column names to descriptions or objects.")

    result = {}
    allowed = set(names)
    for name, entry in entries.items():
        if name not in allowed:
            raise ValueError(f"Dictionary column {name!r} does not match a dataset column.")
        if isinstance(entry, str):
            entry = {"description": entry}
        if (not isinstance(entry, dict) or set(entry) - {"description", "category"}
                or not isinstance(entry.get("description"), str)
                or ("category" in entry and (not isinstance(entry["category"], str) or entry["category"] not in categories))):
            raise ValueError("Dictionary entries need a description and may use a configured business category.")
        result[name] = entry
    if not result:
        raise ValueError("The dictionary has no column descriptions.")
    return result


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


def _assess(profile, definitions, config, target=None, *, sensitive_linkage=None):
    return assess_data_sensitivity(
        profile, column_definitions=definitions, target_classification=target, use_ai=False,
        sensitive_linkage=sensitive_linkage,
        context={"config": SimpleNamespace(governance_config=config), "scope_workspace_id": "docs"},
    )


def handle_message(request_json):
    """Return only the browser's JSON-serializable result."""
    request = json.loads(request_json)
    action = request["action"]
    if action == "dictionary":
        return json.dumps({"definitions": _dictionary(
            request["text"], request["csv"], request["columns"], request["categories"],
        )})
    if action in {"load", "dataset"}:
        definitions = {}
        if action == "dataset":
            payload, definitions = _dataset_profile(request["text"])
            scope = request.get("profileScope", "full_table")
            if scope not in {"full_table", "bounded_selection"}:
                raise ValueError("CSV assessment scope must be a full table or a bounded selection.")
            if request.get("columnOnly"):
                if len(payload["profile"]) != 1:
                    raise ValueError("A column assessment requires exactly one column.")
                payload = {**payload, "kind": "column", "profile": payload["profile"][0]}
            payload["profile_scope"] = scope
        else:
            payload = json.loads(request["text"])
            if isinstance(payload, list):
                payload = {"profile": payload}
        profile = _local_profile(payload)
        rows = profile["profile"]
        return json.dumps({
            "profile": json.dumps(profile),
            "columns": [
                {key: row[key] for key in ("column_name", "data_type", "row_count", "null_count", "distinct_count")
                 if key in row} for row in (rows if isinstance(rows, list) else [rows])
            ],
            "definitions": definitions,
            "columnOnly": "kind" in profile,
            "defaultPolicy": _policy(DEFAULT),
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
    return json.dumps(_assess(
        profile, definitions, config, request.get("target"), sensitive_linkage=request.get("sensitiveLinkage"),
    ))
