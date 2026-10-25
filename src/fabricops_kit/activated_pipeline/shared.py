"""Data Contract approval, coordinated activation and environment execution."""
from __future__ import annotations

import hashlib
import json
from datetime import date
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema, metadata_table_schema_registry, coerce_metadata_row_types
from fabricops_kit.config.shared import resolve_fabric_context, get_store
from fabricops_kit.io import read_lakehouse_table
from fabricops_kit.io.shared import get_spark_session, resolve_configured_lakehouse_table
from fabricops_kit.pipeline.shared import PipelineExecutionPlan, canonical_candidate_json, pipeline_candidate, contract_guardrail_rows, resolve_pipeline_participants, pipeline_record_content



def manifest_digest(value):
    """Return the SHA-256 of the shared canonical candidate serialization."""
    return hashlib.sha256(canonical_candidate_json(value).encode("utf-8")).hexdigest()


def metadata_records(table, *, context, spark_session=None, run_id=None):
    """Read domain metadata through its configured owner schema."""
    config, _env, _runtime = resolve_fabric_context(context=context)
    frame = read_lakehouse_table(table, store="Metadata", schema=metadata_table_physical_schema(config, table),
                                spark_session=spark_session, context=context)
    if table == "METADATA_PIPELINE_RUN":
        from pyspark.sql import functions as F
        frame = frame.filter(F.col("environment_name") == _env)
        if run_id is not None:
            frame = frame.filter(F.col("run_id") == run_id)
    rows = [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in frame.collect()]
    if table == "METADATA_PIPELINE_RUN":
        from fabricops_kit.pipeline.shared import pipeline_run_result
        return [pipeline_run_result(row, context=context, spark_session=spark_session) for row in rows]
    return rows


def exact_record(rows, **identity):
    """Fail closed on missing or duplicated exact identities."""
    matches = [row for row in rows if all(row.get(key) == value for key, value in identity.items())]
    if len(matches) != 1:
        raise ValueError("Required exact metadata identity is missing or duplicated: " + ", ".join(identity))
    return matches[0]


def agreement_definition(row):
    """Retain exact Agreement content without mutable physical audit fields."""
    return {key: value.isoformat() if isinstance(value, date) else value
            for key, value in row.items() if not key.startswith("_")}


def validate_agreement(row):
    """Require an exact currently effective Agreement version."""
    today = date.today()
    start, end = (date.fromisoformat(str(row[key])[:10]) for key in ("start_date", "expiry_date"))
    if not start <= today <= end:
        raise ValueError("The exact Data Agreement version is not currently effective.")


def validate_manifest(row):
    """Validate immutable version content, candidate identity and exact contract hashes."""
    manifest = json.loads(row["manifest_json"])
    if manifest.get("format") != "fabricops.activated-pipeline.v1" or manifest_digest(manifest) != row["activated_pipeline_id"]:
        raise ValueError("Activated Pipeline manifest integrity mismatch.")
    for key in ("pipeline_id", "pipeline_name", "pipeline_version", "testing_run_id", "environment_name"):
        if manifest.get(key) != row[key]:
            raise ValueError("Activated Pipeline immutable identity mismatch.")
    candidate = manifest["candidate"]
    if manifest.get("physical_bindings") != candidate.get("physical_bindings"):
        raise ValueError("Activated Pipeline physical binding integrity mismatch.")
    if manifest_digest(candidate) != row["candidate_fingerprint"] or candidate["pipeline_id"] != row["pipeline_id"]:
        raise ValueError("Activated Pipeline candidate fingerprint mismatch.")
    agreement = manifest["agreement"]
    if any(agreement.get(key) != row[key] for key in ("agreement_id", "agreement_version")):
        raise ValueError("Activated Pipeline Agreement mismatch.")
    expected = {item["participant"]: item["contract"] for item in candidate["exact_contract_payloads"]}
    contracts = manifest["contracts"]
    if len(contracts) != len(expected) or {item["participant"] for item in contracts} != set(expected):
        raise ValueError("Activated Pipeline contract set mismatch.")
    for item in contracts:
        contract = item["definition"]
        actual = {"contract_id": contract["contract_id"], "contract_version": contract["contract_version"],
                  "payload_sha256": hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest()}
        participant = next(value for value in candidate["participants"] if value["participant"] == item["participant"])
        if contract["table_id"] != participant["table_id"]:
            raise ValueError("Approved global table identity mismatch.")
        if actual != expected[item["participant"]] or contract.get("status") != "frozen":
            raise ValueError("Activated Pipeline exact frozen contract mismatch.")
    return manifest


def tested_pipeline_manifest(*, testing_run_id, candidate_fingerprint, pipeline_name, pipeline_version,
                             agreement_id, agreement_version, context, spark_session=None):
    """Revalidate committed complete Test evidence before freezing approval."""
    config, env, runtime = resolve_fabric_context(context=context)
    from fabricops_kit.pipeline.shared import read_pipeline_registry, validate_pipeline_id
    run = exact_record(metadata_records("METADATA_PIPELINE_RUN", context=context, spark_session=spark_session,
                                       run_id=testing_run_id), run_id=testing_run_id)
    validate_pipeline_id(run.get("pipeline_id"))
    _authority_token, registrations = read_pipeline_registry(context=context, spark_session=spark_session)
    registration = exact_record(registrations, pipeline_id=run["pipeline_id"], environment_name=env)
    if registration["registration_status"] != "Active":
        raise ValueError("Activation requires an Active Engineering registration.")
    if run.get("environment_name") != env:
        raise ValueError("Testing evidence must cover the activation environment; other environments are isolated.")
    if not runtime.get("workspace_id") or run.get("_workspace_id") != runtime["workspace_id"]:
        raise ValueError("Testing must cover the current activation workspace.")
    candidate = json.loads(run["candidate_json"])
    if candidate.get("pipeline_id") != run["pipeline_id"]:
        raise ValueError("Testing candidate Pipeline UUID mismatch.")
    if not candidate_fingerprint or candidate_fingerprint != run.get("candidate_fingerprint") or manifest_digest(candidate) != candidate_fingerprint:
        raise ValueError("Exact tested candidate fingerprint mismatch.")
    missing = sorted(item["table_id"] for item in candidate["participants"] if item.get("contract") is None)
    if missing:
        raise ValueError("Activation requires an exact frozen contract for every source and target. Missing contracts for table IDs: " + ", ".join(missing))
    if run.get("execution_mode") != "testing" or run.get("status") != "succeeded" or not run.get("completed_at"):
        raise ValueError("Activation requires a complete successful Testing run; Bootstrap and partial results cannot authorize it.")
    if any(run.get("_" + key) != registration.get(key) for key in ("workspace_id", "notebook_id")):
        raise ValueError("Testing was not run by the current registered notebook; rerun Test after rebinding.")
    summary = json.loads(run["operation_summary_json"])
    operations = summary["operations"]
    expected = {f"{role}:{item['participant']}" for item in candidate["participants"] for role in item["roles"]}
    if summary.get("boundary_completed") is not True:
        raise ValueError("Testing requires a completed whole-run execution boundary.")
    if not isinstance(summary.get("physical_bindings"), dict) or summary["physical_bindings"] != candidate.get("physical_bindings"):
        raise ValueError("Testing destination bindings are missing or differ from the tested candidate; rerun Testing.")
    if summary.get("failures") or set(operations) != expected or not expected or any(
        item.get("status") != "succeeded" or not item.get("configuration_sha256") or not isinstance(item.get("configuration"), dict)
        or not item.get("stages") or any(stage.get("status") in {"blocked", "failed"} or stage.get("evaluation_status") == "not_fully_evaluated"
                                         for stage in item["stages"])
        or len({stage["stage"] for stage in item["stages"]}) != len(item["stages"])
        for item in operations.values()
    ):
        raise ValueError("Testing operation evidence is failed, incomplete or lacks processing configuration; rerun Testing.")
    contracts = metadata_records("METADATA_DATA_CONTRACT", context={**runtime, "config": config, "env": run["environment_name"]}, spark_session=spark_session)
    definitions, identities, frozen = [], {}, {}
    refs = {item["participant"]: item["contract"] for item in summary["frozen_contracts"]}
    missing = sorted(item["table_id"] for item in candidate["participants"] if not refs.get(item["participant"]))
    if missing:
        raise ValueError("Activation requires an exact frozen contract for every source and target. Missing contracts for table IDs: " + ", ".join(missing))
    for participant in candidate["participants"]:
        logical = participant["participant"]
        ref = refs[logical]
        contract = exact_record(contracts, contract_id=ref["contract_id"], contract_version=ref["contract_version"])
        if contract.get("status") != "frozen" or hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest() != ref["payload_sha256"]:
            raise ValueError("Frozen contract changed since Testing.")
        definition = {key: contract[key] for key in ("contract_id", "contract_version", "contract_payload_json", "status", "table_id", "environment_name")}
        definitions.append({"participant": logical, "definition": definition})
        table_id = contract["table_id"]
        binding = next(item for item in summary["frozen_contracts"] if item["participant"] == logical)
        if binding.get("table_id") != table_id:
            raise ValueError("Testing global table identity does not match the frozen contract.")
        identities[table_id] = {"logical_id": logical, "roles": participant["roles"], "store": "bound", "table_name": "bound"}
        frozen[table_id] = definition
    rule_sets = {item["participant"]: contract_guardrail_rows(item["definition"],
        environment_name=run["environment_name"], table_id=item["definition"]["table_id"]) for item in definitions}
    drift_sources = {logical for logical, rules in rule_sets.items() if any(rule["guardrail_type"] == "source_drift" for rule in rules)}
    labels = {"schema": "Schema", "grain": "Grain", "data_quality": "Data Quality", "freshness": "Freshness", "sensitive_data": "Sensitive Data"}
    for participant in candidate["participants"]:
        logical = participant["participant"]
        for role in participant["roles"]:
            operation = operations[f"{role}:{logical}"]
            required_stages = {"Read"} if role == "source" else {"Processing"}
            if role == "source" and operation["configuration"].get("read_mode") == "full":
                required_stages.add("Profile")
            for rule in rule_sets[logical]:
                kind = rule["guardrail_type"]
                if kind in {"schema", "grain", "data_quality"} or (role == "source" and kind == "freshness") or (role == "target" and kind == "sensitive_data"):
                    required_stages.add(labels[kind])
            if role == "target" and drift_sources.intersection(operation["configuration"].get("sources", [])):
                required_stages.add("Source Drift")
            stages = {stage["stage"]: stage for stage in operation["stages"]}
            skipped_freshness = any(rule["guardrail_type"] == "freshness" and rule.get("rule_type") == "skip" for rule in rule_sets[logical])
            if required_stages - set(stages) or any(
                stages[name].get("status") not in ({"passed", "warning", "skipped"} if name == "Freshness" and skipped_freshness else {"passed", "warning"})
                for name in required_stages
            ):
                raise ValueError("Required operation stages are missing or incomplete; isolated passing Guardrails cannot authorize activation.")
    plan = PipelineExecutionPlan("testing", env, str(runtime.get("notebook_id") or "review"), "review",
        canonical_candidate_json(identities), "{}", canonical_candidate_json(frozen), {**runtime, "_pipeline_bindings": summary["physical_bindings"]},
        pipeline_id=run["pipeline_id"], configuration_json=canonical_candidate_json(candidate["project_configuration"]))
    plan.evidence["operations"] = operations
    current, fingerprint, _bindings = pipeline_candidate(plan)
    if fingerprint != candidate_fingerprint or current != candidate:
        raise ValueError("Contracts or processing configuration differ from the tested candidate.")
    diagnostics = [row for row in metadata_records("METADATA_GUARDRAIL_RESULTS", context=context, spark_session=spark_session)
                   if row.get("run_id") == testing_run_id]
    diagnostics.sort(key=lambda item: item["guardrail_result_id"])
    if any(row.get("run_id") != testing_run_id for row in diagnostics):
        raise ValueError("Testing Guardrail diagnostics must reference the selected run.")
    if any(row.get("can_continue") is not True or row.get("execution_type") != "testing" for row in diagnostics):
        raise ValueError("Testing has blocking or invalid Guardrail diagnostics.")
    if any(row.get("environment_name") != env or any(
        row.get(key) != run.get(key) for key in ("_workspace_id", "_notebook_id", "_activity_id")
    ) for row in diagnostics):
        raise ValueError("Testing Guardrail provenance differs from the exact run.")
    from collections import Counter
    observed = Counter((row.get("table_id"), row.get("contract_id"), row.get("contract_version"),
                        row.get("guardrail_rule_id"), row.get("guardrail_version")) for row in diagnostics)
    expected_rules = Counter()
    for item in definitions:
        contract = item["definition"]
        roles = identities[contract["table_id"]]["roles"]
        for rule in contract_guardrail_rows(contract, environment_name=run["environment_name"], table_id=contract["table_id"]):
            kind = rule["guardrail_type"]
            count = len(roles) if kind in {"schema", "grain", "data_quality"} else 0
            if kind == "freshness" and "source" in roles and rule.get("rule_type") != "skip":
                count = 1
            if kind == "sensitive_data" and "target" in roles:
                count = 1
            if kind == "source_drift" and "source" in roles:
                count = sum(item["participant"] in operation["configuration"].get("sources", [])
                            for key, operation in operations.items() if key.startswith("target:"))
            key = (contract["table_id"], contract["contract_id"], contract["contract_version"],
                   rule["guardrail_rule_id"], rule.get("guardrail_version", 1))
            expected_rules[key] += count
    if any(observed[key] < count for key, count in expected_rules.items()):
        raise ValueError("Required exact rule-level Guardrail evidence is missing.")
    agreement = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=context, spark_session=spark_session),
                             agreement_id=agreement_id, agreement_version=agreement_version)
    validate_agreement(agreement)
    if not str(pipeline_name).strip() or not str(pipeline_version).strip():
        raise ValueError("Pipeline name and version are required.")
    return {"format": "fabricops.activated-pipeline.v1", "pipeline_id": run["pipeline_id"], "environment_name": env,
            "pipeline_name": str(pipeline_name).strip(), "pipeline_version": str(pipeline_version).strip(),
            "testing_run_id": testing_run_id, "testing_evidence": json.loads(json.dumps({**run, "guardrail_results": diagnostics}, default=lambda value: value.isoformat() if isinstance(value, date) else str(value))),
            "candidate": candidate, "physical_bindings": summary["physical_bindings"],
            "contracts": sorted(definitions, key=lambda item: item["participant"]),
            "agreement": agreement_definition(agreement),
            "warnings": ["Testing does not verify deployment permissions, target transactions or concurrent business writes."]
                        + [f"{key}: {stage['stage']} {stage['status']}" for key, operation in operations.items()
                           for stage in operation["stages"] if stage.get("status") in {"warning", "skipped"}]}

PIPELINE_AUTHORITY_TABLE = "METADATA_PIPELINE_REGISTRY"


def empty_pipeline_authority():
    """Return the setup-only initial native authority row without runtime audit fields."""
    return {"authority_id": "central", "token": "initial", **{key: [] for key in (
        "registrations", "revisions", "approvals", "selections", "table_ownership", "reservations", "profiling_claims")}}


def authority_records(*, context, spark_session=None):
    """Require exactly one complete Registry publication, never an implicit empty authority."""
    rows = metadata_records(PIPELINE_AUTHORITY_TABLE, context=context, spark_session=spark_session)
    if len(rows) != 1 or rows[0].get("authority_id") != "central" or not rows[0].get("token"):
        raise ValueError("Pipeline Registry authority is missing or duplicated; stop and reconcile metadata.")
    from fabricops_kit.config.metadata_schemas import metadata_table_field_names
    required = set(metadata_table_field_names(metadata_table_schema_registry()[PIPELINE_AUTHORITY_TABLE]))
    if required - set(rows[0]):
        raise ValueError("Incompatible Pipeline Registry; follow the joint redesign cutover before setup.")
    return rows[0]


def approval_record(row, *, context, spark_session=None):
    """Reconstruct a decision from exact retained definitions, Test diagnostics and Agreement."""
    from fabricops_kit.pipeline.shared import read_pipeline_definition, pipeline_definition_candidate
    definition = read_pipeline_definition(row["definition_id"], context=context, spark_session=spark_session)
    candidate = pipeline_definition_candidate(definition, context=context, spark_session=spark_session)
    run = exact_record(metadata_records("METADATA_PIPELINE_RUN", context=context, spark_session=spark_session,
        run_id=row["testing_run_id"]), run_id=row["testing_run_id"])
    diagnostics = sorted((item for item in metadata_records("METADATA_GUARDRAIL_RESULTS", context=context,
        spark_session=spark_session) if item.get("run_id") == row["testing_run_id"]), key=lambda item: item["guardrail_result_id"])
    evidence = json.loads(json.dumps({**run, "guardrail_results": diagnostics}, default=lambda value: value.isoformat() if isinstance(value, date) else str(value)))
    agreement = agreement_definition(exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=context,
        spark_session=spark_session), agreement_id=row["agreement_id"], agreement_version=row["agreement_version"]))
    if (manifest_digest(evidence) != row["testing_evidence_sha256"] or manifest_digest(agreement) != row["agreement_sha256"]
            or run["candidate_json"] != canonical_candidate_json(candidate)
            or run["pipeline_id"] != row["pipeline_id"] or run["environment_name"] != row["environment_name"]
            or definition["environment_name"] != row["environment_name"]):
        raise ValueError("Approved immutable references changed; restore the exact retained Test/Agreement/definition.")
    contracts = metadata_records("METADATA_DATA_CONTRACT", context=context, spark_session=spark_session)
    definitions = [{"participant": item["participant"], "definition": {
        key: exact_record(contracts, contract_id=item["contract_id"], contract_version=item["contract_version"])[key]
        for key in ("contract_id", "contract_version", "contract_payload_json", "status", "table_id", "environment_name")}}
        for item in definition["participants"]]
    manifest = {"format": "fabricops.activated-pipeline.v1", **{key: row[key] for key in (
        "pipeline_id", "pipeline_name", "pipeline_version", "testing_run_id", "environment_name")},
        "testing_evidence": evidence, "candidate": candidate, "physical_bindings": candidate["physical_bindings"],
        "contracts": definitions, "agreement": agreement, "warnings": row["warnings"]}
    result = {key: row[key] for key in ("pipeline_id", "pipeline_name", "pipeline_version", "testing_run_id",
        "environment_name", "agreement_id", "agreement_version")}
    result.update(activated_pipeline_id=row["approval_id"], candidate_fingerprint=definition["candidate_fingerprint"],
        manifest_json=canonical_candidate_json(manifest), is_active=True)
    # Preserve the domain-facing audit representation used by the approval widget.
    result.update({key: value.isoformat() if isinstance(value, date) else value for key, value in row.items() if key.startswith("_")})
    validate_manifest(result)
    return result


def validate_authority_collections(row):
    """Reject duplicate, incomplete or foreign native authority members before use."""
    from fabricops_kit.pipeline.shared import validate_pipeline_registrations
    validate_pipeline_registrations(row["registrations"])
    keys = {
        "revisions": ("environment_name",), "approvals": ("approval_id",),
        "selections": ("environment_name", "pipeline_id"), "table_ownership": ("environment_name", "table_id"),
        "reservations": ("environment_name", "reservation_id"), "profiling_claims": ("claim_key",),
    }
    for collection, fields in keys.items():
        values = [tuple(item.get(key) for key in fields) for item in row[collection]]
        if any(any(value is None or value == "" for value in key) for key in values) or len(values) != len(set(values)):
            raise ValueError("Duplicate or incomplete Pipeline Registry fact; reconcile metadata.")
    environments = {item["environment_name"] for item in row["revisions"]}
    for collection in ("approvals", "selections", "table_ownership", "reservations"):
        if any(item["environment_name"] not in environments for item in row[collection]):
            raise ValueError("Pipeline Registry member has no exact environment revision.")
    approvals = {item["approval_id"]: item for item in row["approvals"]}
    labels = [(item["environment_name"], item["pipeline_id"], item["pipeline_version"]) for item in row["approvals"]]
    if len(labels) != len(set(labels)):
        raise ValueError("Pipeline version contents are immutable; duplicate approval label.")
    for item in row["selections"]:
        approval = approvals.get(item["approval_id"])
        if not approval or any(approval[key] != item[key] for key in ("pipeline_id", "environment_name")):
            raise ValueError("Incomplete Registry selection; exact approval is missing.")
    for item in row["reservations"]:
        if item["mode"] not in {"live", "rebind"} or not item.get("pipeline_id"):
            raise ValueError("Invalid Registry execution reservation.")
        if item["mode"] == "live" and not item.get("revision"):
            raise ValueError("Live reservation requires its pinned revision.")
    for item in row["profiling_claims"]:
        if not item.get("token") or not item.get("execution_id") or not item.get("expires_at"):
            raise ValueError("Incomplete renewable profiling claim.")


def read_pipeline_authority(*, context, spark_session=None):
    """Decode native facts from one atomic Registry snapshot and validate every reference."""
    row = authority_records(context=context, spark_session=spark_session)
    state = {"environments": {}, "registrations": row["registrations"], "profiling_claims": {}}
    validate_authority_collections(row)
    for revision in row["revisions"]:
        environment_activation(state, revision["environment_name"])["revision"] = revision["revision"]
    for approval in row["approvals"]:
        # Each environment resolves its own Run history, including during another environment's mutation.
        _config, _env, runtime = resolve_fabric_context(context=context)
        scoped = {**runtime, "config": _config, "env": approval["environment_name"]}
        item = approval_record(approval, context=scoped, spark_session=spark_session)
        environment_activation(state, approval["environment_name"])["history"][approval["approval_id"]] = item
    for selection in row["selections"]:
        current = environment_activation(state, selection["environment_name"])
        item = current["history"].get(selection["approval_id"])
        if not item or item["pipeline_id"] != selection["pipeline_id"]:
            raise ValueError("Incomplete Registry selection; exact approval is missing.")
        current["pipelines"][selection["pipeline_id"]] = item
    for item in row["table_ownership"]:
        environment_activation(state, item["environment_name"])["tables"][item["table_id"]] = {
            key: value for key, value in item.items() if key not in {"table_id", "environment_name"}}
    for item in row["reservations"]:
        environment_activation(state, item["environment_name"])["runs"][item["reservation_id"]] = {
            key: value for key, value in item.items() if key not in {"environment_name", "reservation_id"} and value is not None}
    state["profiling_claims"] = {item["claim_key"]: {key: value for key, value in item.items() if value is not None}
                                for item in row["profiling_claims"]}
    return row["token"], state


def environment_activation(state, environment):
    """Return an isolated environment's approved configurations and run reservations."""
    return state["environments"].setdefault(environment, {"revision": "initial", "pipelines": {}, "history": {}, "tables": {}, "runs": {}})


def pipeline_authority_row(state, *, context, spark_session=None):
    """Encode related facts as typed collections; no operational document is persisted."""
    from fabricops_kit.pipeline.shared import pipeline_definition_row
    row = empty_pipeline_authority()
    row["registrations"] = state.get("registrations", [])
    row["profiling_claims"] = list(state.get("profiling_claims", {}).values())
    for environment, current in sorted(state["environments"].items()):
        row["revisions"].append({"environment_name": environment, "revision": current["revision"]})
        for approval_id, item in sorted(current["history"].items()):
            manifest = validate_manifest(item)
            definition = pipeline_definition_row(manifest["candidate"], environment=environment, fingerprint=item["candidate_fingerprint"])
            row["approvals"].append({key: item[key] for key in (
                "pipeline_id", "environment_name", "pipeline_name", "pipeline_version", "testing_run_id", "agreement_id", "agreement_version")}
                | {"approval_id": approval_id, "definition_id": definition["definition_id"],
                    "testing_evidence_sha256": manifest_digest(manifest["testing_evidence"]),
                    "agreement_sha256": manifest_digest(manifest["agreement"]), "warnings": manifest["warnings"]}
                | {key: value for key, value in item.items() if key.startswith("_")})
        row["selections"].extend({"environment_name": environment, "pipeline_id": key, "approval_id": item["activated_pipeline_id"]}
            for key, item in sorted(current["pipelines"].items()))
        row["table_ownership"].extend({"environment_name": environment, "table_id": key, **item}
            for key, item in sorted(current["tables"].items()))
        row["reservations"].extend({"environment_name": environment, "reservation_id": key, **item}
            for key, item in sorted(current["runs"].items()))
    return row


def commit_pipeline_authority(state, *, expected_token, context, spark_session=None):
    """CAS the sole Registry row, confirming exact content after a lost acknowledgement.

    One matched-only MERGE updates all collections and the token together. There
    are no child inserts, deletes, or per-update DDL. A stale token raises within
    the transaction. Missing authority cannot be recreated by a runtime writer.
    """
    from delta.tables import DeltaTable
    from uuid import uuid4
    config, env, runtime = resolve_fabric_context(context=context)
    table = PIPELINE_AUTHORITY_TABLE
    previous = authority_records(context=context, spark_session=spark_session)
    row = pipeline_authority_row(state, context=context, spark_session=spark_session)
    # History is append-only even for unrelated registration/profiling mutations.
    old = {item["approval_id"]: item for item in previous["approvals"]}
    wanted = coerce_metadata_row_types(table, row)
    validate_authority_collections(wanted)
    new = {item["approval_id"]: item for item in wanted["approvals"]}
    if any(pipeline_record_content(new.get(key)) != pipeline_record_content(value) for key, value in old.items()):
        raise ValueError("Approved decision history is immutable and retained.")
    old_bindings = {(item["pipeline_id"], item["environment_name"]) for item in previous["registrations"]}
    new_bindings = {(item["pipeline_id"], item["environment_name"]) for item in wanted["registrations"]}
    if old_bindings - new_bindings:
        raise ValueError("Permanent pipeline registrations must be retained; retire explicitly.")
    # New references must already be sealed and reconstruct exactly before authority publication.
    for approval in wanted["approvals"]:
        if approval["approval_id"] not in old:
            scoped = {**runtime, "config": config, "env": approval["environment_name"]}
            approval_record(approval, context=scoped, spark_session=spark_session)
    for current in state["environments"].values():
        if current["pipelines"]:
            impact = activation_impact(current, {})
            if impact["tables"] != current["tables"] or impact["blocking_conflicts"]:
                raise ValueError("Registry selections and table ownership are inconsistent.")
    wanted.update(token=str(uuid4()), **build_runtime_audit_fields(config=config, env=env, runtime_context=runtime))
    spark = get_spark_session(spark_session)
    _store, _table, _schema, path = resolve_configured_lakehouse_table("Metadata", table,
        metadata_table_physical_schema(config, table), context=context)
    frame = spark.createDataFrame([coerce_metadata_row_types(table, wanted)], metadata_table_schema_registry()[table])
    expected = "'" + expected_token.replace("'", "''") + "'"
    changes = {key: "source.`" + key + "`" for key in wanted if key != "authority_id"}
    changes["token"] = f"CASE WHEN target.token = {expected} THEN source.token ELSE CAST(raise_error('Stale Pipeline Registry authority; refresh') AS STRING) END"
    try:
        (DeltaTable.forPath(spark, path).alias("target")
         .merge(frame.alias("source"), "target.authority_id = source.authority_id")
         .whenMatchedUpdate(set=changes).execute())
    except Exception:
        observed = authority_records(context=context, spark_session=spark_session)
        if pipeline_record_content(observed) != pipeline_record_content(coerce_metadata_row_types(table, wanted)):
            raise
    observed = authority_records(context=context, spark_session=spark_session)
    if pipeline_record_content(observed) != pipeline_record_content(coerce_metadata_row_types(table, wanted)):
        raise RuntimeError("Registry authority publication was not confirmed; inspect before retrying.")
    return wanted["token"]


def manifest_table_mappings(manifest):
    """Extract global table/contract identities and read/write roles from a manifest."""
    roles = {item["participant"]: item["roles"] for item in manifest["candidate"]["participants"]}
    mappings = {}
    for item in manifest["contracts"]:
        definition = item["definition"]
        table_id = definition["table_id"]
        if table_id in mappings:
            raise ValueError("Duplicate global table identity in approved participants.")
        mappings[table_id] = {"destination": manifest["physical_bindings"][table_id], "contract_id": definition["contract_id"], "contract_version": definition["contract_version"],
                              "payload_sha256": hashlib.sha256(definition["contract_payload_json"].encode()).hexdigest(),
                              "roles": sorted(roles[item["participant"]])}
    if len(mappings) != len(roles):
        raise ValueError("Every participant must have one exact frozen contract.")
    return mappings


def activation_impact(current, proposed):
    """Calculate conservative dependencies and validate the entire resulting release.

    Direct references to changed contracts/ownership require replacement tests.
    Propagation continues when a replacement changes a downstream table mapping;
    unchanged output expectations stop propagation. No inferred compatibility.
    """
    active = current["pipelines"]
    resulting = {**active, **proposed}
    mappings = {key: manifest_table_mappings(validate_manifest(row)) for key, row in resulting.items()}
    tables, blockers = {}, []
    for pipeline_id, refs in mappings.items():
        for table_id, ref in refs.items():
            identity = {key: ref[key] for key in ("contract_id", "contract_version", "payload_sha256")}
            table = tables.setdefault(table_id, {**identity, "destination": ref["destination"], "writer": None, "readers": []})
            if table["destination"] != ref["destination"]:
                blockers.append(f"Conflicting physical destination for {table_id}: {pipeline_id}.")
            if any(table[key] != identity[key] for key in identity):
                blockers.append(f"Conflicting contract versions for {table_id}: {pipeline_id}.")
            if "target" in ref["roles"]:
                if table["writer"] is not None and table["writer"] != pipeline_id:
                    blockers.append(f"Competing writer for {table_id}: {table['writer']} and {pipeline_id}.")
                table["writer"] = pipeline_id
            if "source" in ref["roles"]:
                table["readers"].append(pipeline_id)
    destinations = {}
    for table_id, table in tables.items():
        destination = canonical_candidate_json(table["destination"])
        previous = destinations.setdefault(destination, table_id)
        if previous != table_id:
            blockers.append(f"Conflicting table identities share a physical destination: {previous} and {table_id}.")
    old = current["tables"]
    changed = {key for key in set(old) | set(tables) if
               {field: old.get(key, {}).get(field) for field in ("contract_id", "contract_version", "payload_sha256", "writer", "destination")} !=
               {field: tables.get(key, {}).get(field) for field in ("contract_id", "contract_version", "payload_sha256", "writer", "destination")}}
    affected = {pipeline_id for pipeline_id, row in active.items()
                if changed.intersection(manifest_table_mappings(validate_manifest(row)))}
    missing = affected - set(proposed)
    blockers += [f"Missing replacement Testing candidate: {key}." for key in sorted(missing)]
    touched = affected | set(proposed)
    busy = [run_id for run_id, run in current["runs"].items()
            if run["pipeline_id"] in touched or changed.intersection(run.get("tables", []))]
    blockers += [f"Drain running execution before cutover: {key}." for key in busy]
    relationships = [{"table_id": table_id, "writer": table["writer"], "readers": sorted(table["readers"])}
                     for table_id, table in tables.items() if table["writer"] or table["readers"]]
    return {"dependencies": relationships, "changed_tables": sorted(changed), "affected_pipelines": sorted(affected),
            "missing_pipelines": sorted(missing), "blocking_conflicts": sorted(set(blockers)),
            "tables": tables, "current_tables": old, "ready": not blockers,
            "selected_pipelines": sorted(proposed), "current_revision": current["revision"]}


def review_pipeline_release(requests, *, context, spark_session=None):
    """Revalidate every Testing candidate and compute environment-specific readiness."""
    config, env, runtime = resolve_fabric_context(context=context)
    token, state = read_pipeline_authority(context=context, spark_session=spark_session)
    current = environment_activation(state, env)
    proposed = {}
    for request in requests:
        manifest = tested_pipeline_manifest(**request, context=context, spark_session=spark_session)
        pipeline_id = manifest["pipeline_id"]
        if pipeline_id in proposed:
            raise ValueError("Select one Testing candidate per pipeline.")
        row = {key: manifest[key] for key in ("pipeline_id", "pipeline_name", "pipeline_version", "testing_run_id")}
        row.update(activated_pipeline_id=manifest_digest(manifest), agreement_id=manifest["agreement"]["agreement_id"],
                   agreement_version=manifest["agreement"]["agreement_version"], candidate_fingerprint=manifest_digest(manifest["candidate"]),
                   manifest_json=canonical_candidate_json(manifest), is_active=True, environment_name=env,
                   **{key: value.isoformat() if isinstance(value, date) else value
                      for key, value in build_runtime_audit_fields(config=config, env=env, runtime_context=runtime).items()})
        for previous in current["history"].values():
            if previous["pipeline_id"] == pipeline_id and previous["pipeline_version"] == row["pipeline_version"] and previous["activated_pipeline_id"] != row["activated_pipeline_id"]:
                raise ValueError("Pipeline version contents are immutable; choose a new version.")
        row = current["history"].get(row["activated_pipeline_id"], row)
        proposed[pipeline_id] = row
    if not proposed:
        raise ValueError("Select at least one successful Testing candidate.")
    report = activation_impact(current, proposed)
    report["ready"] = not report["blocking_conflicts"]
    return token, state, proposed, {**report, "environment": env}


def approve_pipeline_release(requests, *, expected_token, governance_confirmed=False, context=None, spark_session=None):
    """Revalidate and publish the complete release in one authority transaction."""
    if governance_confirmed is not True:
        raise ValueError("Explicit Governance approval of the complete release is required.")
    token, state, proposed, report = review_pipeline_release(requests, context=context, spark_session=spark_session)
    if token != expected_token:
        raise ValueError("Activation state changed; refresh and review the release again.")
    if not report["ready"]:
        raise ValueError(" ".join(report["blocking_conflicts"]))
    current = environment_activation(state, report["environment"])
    current["pipelines"].update(proposed)
    current["history"].update({row["activated_pipeline_id"]: row for row in proposed.values()})
    current["tables"] = report["tables"]
    current["revision"] = manifest_digest({"previous": current["revision"], "pipelines": current["pipelines"]})
    commit_pipeline_authority(state, expected_token=token, context=context, spark_session=spark_session)
    return {"environment": report["environment"], "revision": current["revision"], "pipelines": proposed}


def release_pipeline_lease(plan, *, spark_session=None):
    """Release only this completed run's reservation; failed release remains fail-closed."""
    for _attempt in range(5):
        token, state = read_pipeline_authority(context=plan.runtime_context, spark_session=spark_session)
        current = environment_activation(state, plan.environment)
        lease = current["runs"].get(plan.plan_id)
        if lease is None:
            return
        if lease.get("pipeline_id") != plan.pipeline_id or lease.get("revision") != plan.activation_revision:
            raise ValueError("Reservation belongs to another execution; inspect before release.")
        del current["runs"][plan.plan_id]
        try:
            commit_pipeline_authority(state, expected_token=token, context=plan.runtime_context, spark_session=spark_session)
            plan.evidence.pop("lease_token", None)
            return
        except Exception:
            if _attempt == 4:
                raise


def reserve_pipeline_rebind(pipeline_id, *, context, spark_session=None):
    """Block new Live reservations while an idle pipeline changes notebook owner."""
    from uuid import uuid4
    _config, env, _runtime = resolve_fabric_context(context=context)
    token, state = read_pipeline_authority(context=context, spark_session=spark_session)
    current = environment_activation(state, env)
    if any(run["pipeline_id"] == pipeline_id for run in current["runs"].values()):
        raise ValueError("Drain active Live runs or another rebind before changing notebook ownership.")
    lease_id = str(uuid4())
    current["runs"][lease_id] = {"pipeline_id": pipeline_id, "tables": [], "mode": "rebind"}
    commit_pipeline_authority(state, expected_token=token, context=context, spark_session=spark_session)
    return lease_id


def release_pipeline_rebind(pipeline_id, lease_id, *, context, spark_session=None):
    """Remove exactly the rebind barrier created by this registration attempt."""
    _config, env, _runtime = resolve_fabric_context(context=context)
    for attempt in range(5):
        token, state = read_pipeline_authority(context=context, spark_session=spark_session)
        current = environment_activation(state, env)
        if current["runs"].get(lease_id) != {"pipeline_id": pipeline_id, "tables": [], "mode": "rebind"}:
            raise ValueError("Pipeline rebind reservation changed; inspect Pipeline Registry before retrying.")
        del current["runs"][lease_id]
        try:
            commit_pipeline_authority(state, expected_token=token, context=context, spark_session=spark_session)
            return
        except Exception:
            if attempt == 4:
                raise


def activation_version(activated_pipeline_id, *, context, spark_session=None, require_active=True):
    """Resolve an immutable approval from the environment's atomic authority."""
    _config, env, _runtime = resolve_fabric_context(context=context)
    _token, state = read_pipeline_authority(context=context, spark_session=spark_session)
    current = environment_activation(state, env)
    matches = [row for row in (current["pipelines"] if require_active else current["history"]).values()
               if row["activated_pipeline_id"] == activated_pipeline_id]
    if len(matches) != 1:
        raise ValueError("Approved version is missing or inactive in this environment.")
    validate_manifest(matches[0])
    return matches[0]


def build_live_pipeline_plan(*, pipeline_id, context=None, spark_session=None):
    """Pin approval and reserve a Live run atomically against coordinated cutover."""
    from types import MappingProxyType
    from uuid import uuid4
    from fabricops_kit.pipeline.shared import persist_pipeline_run, pipeline_physical_bindings
    config, env, runtime = resolve_fabric_context(context=context)
    from fabricops_kit.pipeline.shared import read_pipeline_registry, validate_pipeline_id
    pipeline_id = validate_pipeline_id(pipeline_id)
    _registration_token, registrations = read_pipeline_registry(context=context, spark_session=spark_session)
    registration = exact_record(registrations, pipeline_id=pipeline_id, environment_name=env)
    if registration["registration_status"] != "Active" or any(
        registration[key] != runtime.get(key) for key in ("workspace_id", "notebook_id")
    ):
        raise ValueError("Live caller does not own the Active Engineering notebook binding.")
    token, state = read_pipeline_authority(context=context, spark_session=spark_session)
    if token != _registration_token:
        raise ValueError("Pipeline binding changed during Live admission; retry setup.")
    current = environment_activation(state, env)
    if any(run["pipeline_id"] == pipeline_id and run.get("mode") == "rebind"
           for run in current["runs"].values()):
        raise ValueError("Pipeline notebook rebinding is in progress; retry Live setup afterward.")
    approved = current["pipelines"].get(pipeline_id)
    if not approved:
        raise ValueError("No approved pipeline configuration for this environment and pipeline_id.")
    integrity = activation_impact(current, {})
    if integrity["tables"] != current["tables"] or integrity["blocking_conflicts"]:
        raise ValueError("Pipeline Registry has inconsistent table mappings or ownership.")
    manifest = validate_manifest(approved)
    if any(manifest["testing_evidence"].get("_" + key) != registration[key] for key in ("workspace_id", "notebook_id")):
        raise ValueError("Registered notebook changed since the approved Test; rerun Test and approve the new binding before Live.")
    validate_agreement(manifest["agreement"])
    participants = manifest["candidate"]["participants"]
    identities = resolve_pipeline_participants(config, env,
        sources=[{"table_id": item["table_id"], "logical_id": item["participant"]} for item in participants if "source" in item["roles"]],
        targets=[{"table_id": item["table_id"], "logical_id": item["participant"]} for item in participants if "target" in item["roles"]],
        context=runtime, spark_session=spark_session)
    definitions = {item["definition"]["table_id"]: item["definition"] for item in manifest["contracts"]}
    expected = {item["participant"]: sorted(item["roles"]) for item in manifest["candidate"]["participants"]}
    if {item["logical_id"]: sorted(item["roles"]) for item in identities.values()} != expected or set(identities) != set(definitions):
        raise ValueError("Live table identities or participant roles differ from approval.")
    contracts = {key: {**definitions[key], "contract_payload": json.loads(definitions[key]["contract_payload_json"])} for key in identities}
    physical = pipeline_physical_bindings(identities, config=config, environment=env)
    if physical != manifest["physical_bindings"]:
        raise ValueError("Live physical destinations differ from the tested approved environment bindings.")
    plan = PipelineExecutionPlan("live", env, str(runtime.get("notebook_id") or ""), str(uuid4()), canonical_candidate_json(identities),
        "{}", canonical_candidate_json(contracts), MappingProxyType({**runtime, "config": config, "env": env, "_pipeline_spark": spark_session, "_pipeline_bindings": physical}),
        pipeline_id=pipeline_id, configuration_json=canonical_candidate_json(manifest["candidate"]["project_configuration"]),
        activated_pipeline_id=approved["activated_pipeline_id"], approved_candidate_json=canonical_candidate_json(manifest["candidate"]),
        activation_revision=current["revision"])
    current["runs"][plan.plan_id] = {"pipeline_id": pipeline_id, "tables": sorted(identities), "destinations": list(physical.values()), "revision": current["revision"], "mode": "live"}
    commit_pipeline_authority(state, expected_token=token, context=context, spark_session=spark_session)
    plan.evidence["lease_token"] = plan.plan_id
    try:
        verify_live_plan(plan, spark_session=spark_session)
        persist_pipeline_run(plan, spark_session=spark_session)
    except BaseException:
        release_pipeline_lease(plan, spark_session=spark_session)
        raise
    return plan


def verify_live_plan(plan, *, spark_session=None):
    """Check pinned Data Contract approval and reservation without switching runs."""
    from dataclasses import replace
    _token, state = read_pipeline_authority(context=plan.runtime_context, spark_session=spark_session)
    current = environment_activation(state, plan.environment)
    lease = current["runs"].get(plan.plan_id)
    if not lease or lease.get("revision") != plan.activation_revision:
        raise ValueError("Live run has no valid pinned activation reservation.")
    approved = current["history"].get(plan.activated_pipeline_id)
    if not approved or approved["candidate_fingerprint"] != manifest_digest(json.loads(plan.approved_candidate_json)):
        raise ValueError("Pinned approval is unavailable or corrupt.")
    active = current["pipelines"].get(plan.pipeline_id)
    if not active or active["activated_pipeline_id"] != plan.activated_pipeline_id:
        raise ValueError("Pinned pipeline is no longer active; stop this run.")
    manifest = validate_manifest(approved)
    from fabricops_kit.pipeline.shared import pipeline_physical_bindings
    physical = pipeline_physical_bindings(json.loads(plan.participants_json), config=plan.runtime_context["config"], environment=plan.environment)
    if physical != manifest["physical_bindings"]:
        raise ValueError("Live destinations changed during execution.")
    agreement = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=plan.runtime_context, spark_session=spark_session),
                             agreement_id=approved["agreement_id"], agreement_version=approved["agreement_version"])
    validate_agreement(agreement)
    if agreement_definition(agreement) != manifest["agreement"]:
        raise ValueError("Approved Data Agreement content changed.")
    journal = {item["operation"]: {"status": "not_started", "configuration": item["configuration"],
               "configuration_sha256": item["configuration_sha256"]} for item in manifest["candidate"]["operations"]}
    check = replace(plan, evidence={**plan.evidence, "operations": journal})
    candidate, fingerprint, _bindings = pipeline_candidate(check)
    if candidate != manifest["candidate"] or fingerprint != approved["candidate_fingerprint"]:
        raise ValueError("Live contracts or transformation configuration differs from approval.")


def resolve_approved_consumer_contract(config, env, table_id, *, spark_session=None):
    """Resolve the single approved table mapping in an environment's revision."""
    _token, state = read_pipeline_authority(context={"config": config, "env": env}, spark_session=spark_session)
    current = environment_activation(state, env)
    matches = []
    for row in current["pipelines"].values():
        manifest = validate_manifest(row)
        for item in manifest["contracts"]:
            definition = item["definition"]
            if definition["table_id"] == table_id:
                matches.append({**definition, "contract_payload": json.loads(definition["contract_payload_json"]),
                                "agreement_id": row["agreement_id"], "agreement_version": row["agreement_version"]})
    if not matches or any(item != matches[0] for item in matches):
        raise ValueError("No unambiguous active pipeline contract and Agreement cover this consumer table.")
    return matches[0]
