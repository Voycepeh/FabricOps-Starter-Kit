"""Notebook-facing, advisory Data Sensitivity Assessment."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping

from fabricops_kit.config.shared import GovernanceConfig, resolve_fabric_context
from fabricops_kit.data_contract.shared import (
    assessment_profile_evidence,
    assess_lineage_protection,
    assessment_contract_evidence,
    invoke_assessment_ai,
    sensitive_data_treatments_for_type,
    validate_sensitive_data_parameters,
)

_EMAIL = r"(?i)\b[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}\b"
_PHONE = r"\+\d[\d .()\-]{7,16}\d"
_CARD = r"(?<!\d)\d(?:[ -]?\d){12,18}(?!\d)"
_NRIC = r"(?i)\b[STFGM]\d{7}[A-Z]\b"
_PATTERNS = {"email": _EMAIL, "phone": _PHONE, "payment_card": _CARD, "nric_fin": _NRIC}


def _luhn(value):
    digits = [int(c) for c in value if c.isascii() and c.isdigit()]
    return len(set(digits)) > 1 and sum(
        (digit * 2 - 9 if digit > 4 else digit * 2) if index % 2 else digit
        for index, digit in enumerate(reversed(digits))
    ) % 10 == 0


def _identifier_checksum(value):
    value = value.upper()
    prefix, digits, suffix = value[0], value[1:8], value[8]
    total = sum(int(digit) * weight for digit, weight in zip(digits, (2, 7, 6, 5, 4, 3, 2)))
    offset, alphabet = {
        "S": (0, "JZIHGFEDCBA"), "T": (4, "JZIHGFEDCBA"),
        "F": (0, "XWUTRQPNMLK"), "G": (4, "XWUTRQPNMLK"),
        "M": (3, "KLJNPQRTUWX"),
    }[prefix]
    return alphabet[(total + offset) % 11] == suffix


def _value_signals(value, detectors):
    if value is None:
        return []
    matches = []
    for detector in detectors:
        check = {"payment_card": _luhn, "nric_fin": _identifier_checksum}.get(detector)
        candidates = re.finditer(_PATTERNS[detector], str(value), flags=re.ASCII)
        if any(check is None or check(candidate.group()) for candidate in candidates):
            matches.append(detector)
    return matches


def _spark_detector(sample, detector):
    from pyspark.sql import functions as F

    if detector not in {"payment_card", "nric_fin"}:
        return sample.rlike(_PATTERNS[detector])
    candidates = F.regexp_extract_all(sample, F.lit(_PATTERNS[detector]), 0)

    def valid_card(candidate):
        digits = F.regexp_replace(candidate, "[ -]", "")
        length = F.length(digits)

        def score(total, index):
            digit = F.substr(digits, index, F.lit(1)).cast("int")
            doubled = F.when(digit > 4, digit * 2 - 9).otherwise(digit * 2)
            return total + F.when((length - index) % 2 == 1, doubled).otherwise(digit)

        total = F.aggregate(F.sequence(F.lit(1), length), F.lit(0), score)
        return (~digits.rlike(r"^(\d)\1+$")) & (total % 10 == 0)

    def valid_identifier(candidate):
        value = F.upper(candidate)
        prefix = F.substring(value, 1, 1)
        total = sum(F.substring(value, index, 1).cast("int") * weight
                    for index, weight in enumerate((2, 7, 6, 5, 4, 3, 2), 2))
        offset = F.when(prefix.isin("T", "G"), 4).when(prefix == "M", 3).otherwise(0)
        alphabet = F.when(prefix.isin("S", "T"), "JZIHGFEDCBA").when(
            prefix == "M", "KLJNPQRTUWX").otherwise("XWUTRQPNMLK")
        return F.substr(alphabet, (total + offset) % 11 + 1, F.lit(1)) == F.substring(value, 9, 1)

    return F.exists(candidates, valid_card if detector == "payment_card" else valid_identifier)


def _scan(dataframe, columns, detectors, expected_rows):
    """Return aggregate detector counts in one Spark action."""
    if not columns or not detectors:
        return {}
    from pyspark.sql import functions as F

    names = set(dataframe.columns)
    if set(columns) - names or len(names) != len(dataframe.columns):
        raise ValueError("Scan DataFrame must contain the assessed columns with unique names.")
    checks = {}
    for name in columns:
        sample = F.col("`" + name.replace("`", "``") + "`").cast("string")
        for detector in detectors:
            checks[name, detector] = _spark_detector(sample, detector)
    row = dataframe.agg(F.count("*").alias("assessment_rows"), *[
        F.count(F.when(condition, 1)).alias(f"count_{index}") for index, condition in enumerate(checks.values())
    ]).first()
    if expected_rows is not None and row[0] != expected_rows:
        raise ValueError("The supplied scan DataFrame and statistical profile have different row counts.")
    return {key: int(row[index + 1]) for index, key in enumerate(checks)}


def assess_data_sensitivity(
    profile_result,
    description=None,
    column_definitions=None,
    target_classification=None,
    use_ai=False,
    *,
    dataframe=None,
    sensitive_linkage=None,
    context=None,
) -> dict:
    """Assess profile evidence and applicable Data Contract protections.

    Accept a table profile result, an orchestration profile result, or a single
    column profile row. Column definitions can be descriptions or objects with
    ``description`` and a policy-defined ``category``. An optional Spark DataFrame
    supplies explicit local scan evidence and must represent the assessed scope.
    AI assistance requires opt-in and configured access. The returned findings
    are advisory and preserve applicable minimum handling. Assessment does not
    modify data, Contracts or classifications.

    Parameters
    ----------
    profile_result : dict or pyspark.sql.Row
        A canonical column profile, a profile_table() result, or the profile_result
        from an orchestrated Read or Write.
    description : str, optional
        Current business description of the selected column or dataset.
    column_definitions : mapping, optional
        Column names mapped to draft descriptions or objects with a description
        and a configured category.
    target_classification : str, optional
        A configured label. A lower target can produce treatment recommendations.
    use_ai : bool, default=False
        Request optional assistance when the configured Fabric AI endpoint is approved.
    dataframe : pyspark.sql.DataFrame, optional
        Data within the assessed scope for explicit local detector and group checks.
    sensitive_linkage : bool, optional
        Dataset evidence that sensitive information can (True) or cannot
        (False) be attributed to individuals or a sensitive group. Omit when
        unknown. A negative declaration does not override scan findings.
    context : dict, optional
        Existing FabricOps notebook configuration and Metadata routing.

    Returns
    -------
    dict
        Findings include observed scope, nullable classification, approved
        dataset classification, minimum handling, review flags, provenance,
        and conditional treatments. The assessed classification describes the
        observed data. The approved classification remains a handling floor.

    Raises
    ------
    ValueError
        If definitions, target classification, profile coverage, or scan scope are invalid.

    Examples
    --------
    >>> assess_data_sensitivity(
    ...     {"COLUMN_NAME": "amount", "DATA_TYPE": "decimal(12,2)"},
    ...     description="Monthly staff base salary",
    ... )["human_review_required"]
    True

    """
    if context is None:
        try:
            config, _, runtime = resolve_fabric_context()
        except RuntimeError:
            config, runtime = None, None
    else:
        config, _, runtime = resolve_fabric_context(context=context)
    governance = getattr(config, "governance_config", None) or GovernanceConfig()
    policy = governance.sensitivity_assessment
    definitions = column_definitions or {}
    if not isinstance(definitions, Mapping) or any(not isinstance(name, str) or not name for name in definitions):
        raise ValueError("column_definitions must map column names to descriptions or category objects.")
    levels = governance.classification_levels
    rank = {level: i for i, level in enumerate(levels)}
    most_protective = next(reversed(rank))

    def highest(values):
        return max((value for value in values if value in rank), key=rank.get, default=None)

    if target_classification is not None and (not isinstance(target_classification, str) or target_classification not in rank):
        raise ValueError("target_classification must be a configured classification label.")
    profile, scope, asset, single, limitations = assessment_profile_evidence(profile_result, runtime)
    if sensitive_linkage is not None and (type(sensitive_linkage) is not bool or single):
        raise ValueError("sensitive_linkage must be a Boolean for a dataset assessment.")
    approved = assessment_contract_evidence(asset, runtime)
    if approved.get("unavailable"):
        limitations.append("approved_contract_unavailable")
    lineage = assess_lineage_protection(asset, scope, profile, runtime, rank)
    categories = policy["categories"]
    detectors = policy["detectors"]
    columns = {}
    source_columns = approved.get("columns", {})
    output_schema = bool(profile) and not single and scope["kind"] == "full_table"
    names = (profile if output_schema else
             dict.fromkeys([*profile, *definitions, *(source_columns if not single else ())]))
    treatment_provenance = scope.get("verified_treatment_contract")
    treatment_verified = bool(treatment_provenance) and all(
        treatment_provenance.get(key)
        and treatment_provenance[key] == approved.get("provenance", {}).get(key)
        for key in ("contract_id", "contract_version", "payload_sha256")
    )
    contract_has_treatment = any(item.get("treatment") for item in source_columns.values())
    for name in names:
        observed = profile.get(name, {})
        draft = definitions.get(name, {})
        if isinstance(draft, str):
            draft = {"description": draft}
        if not isinstance(draft, Mapping):
            raise ValueError("Each column definition must be a description or an object.")
        contract = source_columns.get(name, {})
        upstream = lineage.get(name, {})
        category = draft.get("category")
        if category is not None and (not isinstance(category, str) or category not in categories):
            raise ValueError("A column definition uses a category missing from the assessment policy.")
        rule = categories.get(category, {})
        label = contract.get("classification")
        inherited = upstream.get("classification")
        proposal = rule.get("classification")
        flags = []
        classification = label if label in rank else None
        method = "approved" if classification else "inconclusive"
        if label is not None:
            if observed.get("column_id") and contract.get("column_id") != observed["column_id"]:
                flags.append("approved_column_identity_unverified")
                classification = None
            if (observed.get("data_type") and contract.get("data_type")
                    and observed["data_type"] != contract["data_type"] and not contract.get("treatment")):
                flags.append("approved_column_type_changed")
                classification = None
            if label not in rank:
                flags.append("approved_label_outside_policy")
            if proposal in rank and label != proposal:
                flags.append("conflicting_classification")
            if inherited in rank and label != inherited:
                flags.append("conflicting_upstream_classification")
        treatment_unverified = bool(contract.get("treatment")) and not treatment_verified
        if treatment_unverified:
            flags.append("treatment_execution_unverified")
            classification = None
        if classification is None:
            classification = highest((inherited, proposal))
            method = ("inherited" if classification == inherited else "deterministic") if classification else "inconclusive"
        if upstream.get("review"):
            flags.append(upstream["review"])
        if not observed:
            flags.append("profile_evidence_unavailable")
        column_description = draft.get("description", description if single and description is not None else contract.get("description"))
        columns[name] = {
            "column_name": name, "data_type": observed.get("data_type") or contract.get("data_type"),
            "classification": classification, "assessment_method": method,
            "approved_classification": label, "inherited_classification": inherited,
            "deterministic_classification": proposal,
            "minimum_handling_classification": highest((
                classification, label, inherited, proposal, upstream.get("floor"),
                most_protective if label is not None and label not in rank else None,
                policy["suspected_handling"] if treatment_unverified else None,
            )),
            "category": category, "is_personal_data": rule.get("personal"),
            "is_sensitive_data": rule.get("sensitive"),
            "rationale": "Classification requires stronger evidence." if classification is None else
                {"approved": "Applicable active Data Contract.",
                 "inherited": "Verified value-preserving lineage.",
                 "deterministic": "Configured business category."}[method],
            "evidence": flags,
            "provenance": upstream.get("provenance") or (approved.get("provenance") if label else None),
            "observations": {key: observed[key] for key in ("row_count", "non_null_count", "distinct_count")
                             if observed.get(key) is not None},
            "business_definition_available": bool(column_description),
            "description": column_description,
        }
        if contract.get("pii_type") in {"direct", "indirect"}:
            columns[name]["guardrail_input_pii_type"] = contract["pii_type"]
            if scope.get("profile_subject") in {"supplied_dataframe", "prepared_input", "persisted_output", "physical_table"}:
                # Write-side PII metadata describes the input to treatment.
                columns[name]["is_sensitive_data"] = columns[name]["is_sensitive_data"] or None
            else:
                columns[name]["is_personal_data"] = True
                columns[name]["is_sensitive_data"] = True

    unresolved = [
        name for name, column in columns.items()
        if column["classification"] is None or column["evidence"]
    ]
    scannable = [
        name for name in unresolved if name in profile
        and str(profile[name].get("data_type") or "").lower().startswith(("string", "char", "varchar"))
    ]
    row_counts = {row["row_count"] for row in profile.values() if row.get("row_count") is not None}
    expected_rows = next(iter(row_counts)) if len(row_counts) == 1 else None
    scan_counts = _scan(dataframe, scannable, detectors, expected_rows) if dataframe is not None else {}
    for name, column in columns.items():
        observed = profile.get(name, {})
        positives = set()
        for value in observed.get("observed_values", []):
            positives.update(_value_signals(value, detectors))
        for detector in detectors:
            if scan_counts.get((name, detector), 0):
                positives.add(detector)
        if positives:
            column["evidence"].extend("pattern_match:" + detector for detector in sorted(positives))
            interpreted_contact = (positives <= {"email", "phone"}
                                   and column["category"] in {"business_contact", "personal_contact"})
            if not interpreted_contact:
                if column["classification"] and rank[column["classification"]] < rank[policy["suspected_handling"]]:
                    column["evidence"].append("contradictory_pattern_evidence")
                column["minimum_handling_classification"] = highest((
                    column["minimum_handling_classification"], policy["suspected_handling"],
                ))
        if detectors and (name, detectors[0]) in scan_counts:
            column["local_detector_counts"] = {detector: scan_counts[name, detector] for detector in detectors}
        column["human_review_required"] = column["classification"] is None or any(not code.startswith("pattern_match:") for code in column["evidence"])

    findings = []
    dataset_rule = None
    present = {column["category"] for column in columns.values()}
    for rule in policy["combinations"] if not single else ():
        if not set(rule["categories"]) <= present:
            continue
        if rule.get("requires_linkage") and sensitive_linkage is not True:
            if sensitive_linkage is None:
                findings.append({"code": "sensitive_linkage_unverified", "categories": rule["categories"],
                                 "human_review_required": True})
            continue
        findings.append({"code": "sensitive_combination", "categories": rule["categories"],
                         "classification": rule["classification"], "human_review_required": True})
        dataset_rule = highest((dataset_rule, rule["classification"]))
    if sensitive_linkage is True:
        dataset_rule = highest((dataset_rule, policy["suspected_handling"]))
        findings.append({"code": "identifiable_sensitive_information", "human_review_required": True})
    group_columns = [name for name, column in columns.items() if column["category"] == "quasi_identifier"]
    if not single and len(group_columns) >= 2:
        if dataframe is None or not set(group_columns) <= set(dataframe.columns):
            findings.append({"code": "joint_group_sizes_unverified", "human_review_required": True})
        else:
            from pyspark.sql import functions as F

            keys = [F.col("`" + name.replace("`", "``") + "`") for name in group_columns]
            threshold = policy["small_group_minimum"]
            grouped = dataframe.groupBy(*keys).agg(F.count("*").alias("_fabricops_group_size"))
            totals = grouped.agg(F.sum("_fabricops_group_size"),
                                 F.min("_fabricops_group_size")).first()
            if expected_rows is not None and (totals[0] or 0) != expected_rows:
                raise ValueError("The supplied scan DataFrame and statistical profile have different row counts.")
            if totals[1] is not None and totals[1] < threshold:
                dataset_rule = highest((dataset_rule, policy["suspected_handling"]))
                findings.append({"code": "small_joint_groups", "threshold": threshold, "human_review_required": True})
    if not single and any(value.get("population_changed") for value in lineage.values()):
        findings.append({"code": "changed_population", "human_review_required": True})
    limited_dataset = not single and scope["kind"] != "full_table"
    if limited_dataset:
        findings.append({"code": "limited_dataset_coverage", "human_review_required": True})

    ai_status = "disabled"
    ai_dataset = None
    if use_ai:
        table_description = approved.get("description") if description is None and not single else description
        ai_status, ai_dataset = invoke_assessment_ai(
            columns, findings, table_description if not single else None, scope, governance, runtime,
        )

    for column in columns.values():
        column.pop("description", None)
        if column["human_review_required"]:
            column["minimum_handling_classification"] = highest((
                column["minimum_handling_classification"], policy["unresolved_handling"],
            ))
    values = list(columns.values())
    approved_table = approved.get("classification") if not single else None
    if approved_table is not None and approved_table not in rank:
        findings.append({"code": "approved_label_outside_policy", "human_review_required": True})
    if contract_has_treatment and not treatment_verified and not single:
        findings.append({"code": "treatment_execution_unverified", "human_review_required": True})
    # The approved dataset label sets handling. An output with treatment rules
    # is assessed from its observed columns and contextual evidence.
    assessed = highest([approved_table if not contract_has_treatment else None,
                        dataset_rule, ai_dataset, *(c["classification"] for c in values)])
    unresolved_current = not values or any(c["classification"] is None for c in values)
    incomplete_classification = limited_dataset and (approved_table not in rank or contract_has_treatment)
    if ((unresolved_current or incomplete_classification)
            and assessed in rank and rank[assessed] < rank[policy["unresolved_handling"]]):
        assessed = None
    if not single and approved_table in rank and dataset_rule in rank and rank[dataset_rule] > rank[approved_table]:
        findings.append({"code": "contradictory_dataset_evidence", "human_review_required": True})
    floor = highest([
        assessed, approved_table, *(c["minimum_handling_classification"] for c in values),
        policy["suspected_handling"] if contract_has_treatment and not treatment_verified and not single else None,
        policy["unresolved_handling"] if unresolved_current or incomplete_classification or approved.get("unavailable") else None,
        most_protective if approved_table is not None and approved_table not in rank else None,
    ])
    treatments, residual = [], []
    if target_classification is not None:
        if assessed is None:
            residual.append("Treatment feasibility is undetermined while classification is unresolved.")
        elif rank[target_classification] < rank[assessed]:
            if unresolved_current or any(c["human_review_required"] for c in values):
                residual.append("Treatment feasibility is undetermined until unresolved findings are reviewed.")
            for column in values:
                level = column["minimum_handling_classification"]
                if column["classification"] is None or level not in rank or rank[level] <= rank[target_classification]:
                    continue
                name = column["column_name"]
                allowed = sensitive_data_treatments_for_type(column.get("data_type") or "")
                treatment = "mask" if column["is_personal_data"] and "mask" in allowed else "remove"
                params = {"scope": "column", "treatment": treatment}
                if treatment == "mask":
                    params.update(preserve_start=0, preserve_end=0, mask_character="*")
                treatments.append({
                    "column_name": name, "kind": "guardrail",
                    "parameters": validate_sensitive_data_parameters(params),
                    "rationale": "Review analytical utility and remaining disclosure risk.",
                })
            if dataset_rule or ai_dataset or approved_table:
                residual.append("Review dataset context and applicable approved protections after treatment.")
            if not treatments and not unresolved_current:
                residual.append("No column treatment addresses the remaining dataset findings.")
            residual.append("Reassess the actual transformed output before authorised classification review.")

    def indicator(field):
        flags = [c[field] for c in values]
        return True if True in flags else False if flags and all(flag is False for flag in flags) else None

    if dataframe is not None and unresolved and not scan_counts:
        limitations.append("no_local_detector_coverage")
    if scan_counts:
        scope["local_scan"] = {"columns": scannable, "detectors": list(detectors),
                               "coverage": "supplied_dataframe"}
    return {
        "table_id": asset.get("table_id"), "asset": asset, "scope": scope,
        "policy_fingerprint": hashlib.sha256(json.dumps([list(levels.items()), policy], sort_keys=True).encode()).hexdigest(),
        "classification": assessed, "approved_classification": approved_table,
        "minimum_handling_classification": floor,
        "target_classification": target_classification,
        "contains_personal_data": indicator("is_personal_data"),
        "contains_sensitive_data": indicator("is_sensitive_data"),
        "human_review_required": unresolved_current or bool(limitations)
        or any(c["human_review_required"] for c in values)
        or any(f.get("human_review_required") for f in findings),
        "columns": values, "dataset_findings": findings, "limitations": limitations,
        "recommended_treatments": treatments, "residual_risks": residual, "ai_status": ai_status,
    }
