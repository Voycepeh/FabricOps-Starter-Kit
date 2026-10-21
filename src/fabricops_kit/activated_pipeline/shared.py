"""Whole-pipeline approval, immutable manifests and deployment verification."""
from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path
from typing import Any

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import metadata_table_physical_schema, metadata_table_schema_registry, coerce_metadata_row_types
from fabricops_kit.config.shared import resolve_fabric_context, get_store
from fabricops_kit.io import read_lakehouse_table
from fabricops_kit.io.shared import get_spark_session, resolve_configured_lakehouse_table
from fabricops_kit.pipeline.shared import notebook_executable_fingerprint
from fabricops_kit.pipeline.shared import PipelineExecutionPlan, canonical_candidate_json, pipeline_candidate, contract_guardrail_rows, resolve_pipeline_participants

ACTIVATED_TABLE = "METADATA_ACTIVATED_PIPELINE"


def manifest_digest(value):
    """Return the SHA-256 of the shared canonical candidate serialization."""
    return hashlib.sha256(canonical_candidate_json(value).encode("utf-8")).hexdigest()


def metadata_records(table, *, context, spark_session=None):
    """Read domain metadata through its configured owner schema."""
    config, _env, _runtime = resolve_fabric_context(context=context)
    frame = read_lakehouse_table(table, store="Metadata", schema=metadata_table_physical_schema(config, table),
                                spark_session=spark_session, context=context)
    return [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in frame.collect()]


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
    for key in ("pipeline_id", "pipeline_name", "pipeline_version", "testing_run_id"):
        if manifest.get(key) != row[key]:
            raise ValueError("Activated Pipeline immutable identity mismatch.")
    candidate = manifest["candidate"]
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
        if actual != expected[item["participant"]] or contract.get("status") != "frozen":
            raise ValueError("Activated Pipeline exact frozen contract mismatch.")
    return manifest


def tested_pipeline_manifest(*, testing_run_id, candidate_fingerprint, pipeline_name, pipeline_version,
                             agreement_id, agreement_version, executable_path, context, spark_session=None):
    """Revalidate committed complete Testing evidence independently of any widget."""
    config, env, runtime = resolve_fabric_context(context=context)
    run = exact_record(metadata_records("METADATA_PIPELINE_RUN", context=context, spark_session=spark_session), run_id=testing_run_id)
    if run.get("execution_mode") != "testing" or run.get("status") != "succeeded" or not run.get("completed_at"):
        raise ValueError("Activation requires a complete successful Testing run; Bootstrap and partial results cannot authorize it.")
    candidate = json.loads(run["candidate_json"])
    if not candidate_fingerprint or candidate_fingerprint != run.get("candidate_fingerprint") or manifest_digest(candidate) != candidate_fingerprint:
        raise ValueError("Exact tested candidate fingerprint mismatch.")
    if notebook_executable_fingerprint(Path(executable_path).read_bytes()) != candidate["executable_sha256"]:
        raise ValueError("Project executable changed since Testing.")
    from fabricops_kit.pipeline.shared import deployed_notebook_fingerprint
    if deployed_notebook_fingerprint({"workspace_id": run["_workspace_id"], "notebook_id": run["_notebook_id"]}) != candidate["executable_sha256"]:
        raise ValueError("Deployed Testing notebook changed since Testing.")
    summary = json.loads(run["operation_summary_json"])
    operations = summary["operations"]
    expected = {f"{role}:{item['participant']}" for item in candidate["participants"] for role in item["roles"]}
    if summary.get("failures") or set(operations) != expected or not expected or any(
        item.get("status") != "succeeded" or not item.get("configuration_sha256") or not isinstance(item.get("configuration"), dict)
        or not item.get("stages") or any(stage.get("status") in {"blocked", "failed"} or stage.get("evaluation_status") == "not_fully_evaluated"
                                         for stage in item["stages"])
        for item in operations.values()
    ):
        raise ValueError("Testing operation evidence is failed, incomplete or lacks executable configuration; rerun Testing.")
    contracts = metadata_records("METADATA_DATA_CONTRACT", context={**runtime, "config": config, "env": run["environment_name"]}, spark_session=spark_session)
    definitions, identities, frozen = [], {}, {}
    refs = {item["participant"]: item["contract"] for item in summary["frozen_contracts"]}
    for participant in candidate["participants"]:
        logical = participant["participant"]
        ref = refs.get(logical)
        if not ref:
            raise ValueError("Activation requires an exact frozen contract for every source and target.")
        contract = exact_record(contracts, contract_id=ref["contract_id"], contract_version=ref["contract_version"], environment_name=run["environment_name"])
        if contract.get("status") != "frozen" or hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest() != ref["payload_sha256"]:
            raise ValueError("Frozen contract changed since Testing.")
        definition = {key: contract[key] for key in ("contract_id", "contract_version", "contract_payload_json", "status", "table_id", "environment_name")}
        definitions.append({"participant": logical, "definition": definition})
        table_id = contract["table_id"]
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
            required_stages = {"Read" if role == "source" else "Processing"}
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
    dependencies = {name: item["required"] for name, item in candidate["dependencies"].items()}
    plan = PipelineExecutionPlan("testing", env, str(runtime.get("notebook_id") or "review"), "review",
        canonical_candidate_json(identities), "{}", canonical_candidate_json(frozen), runtime,
        pipeline_id=run["pipeline_id"], executable_sha256=candidate["executable_sha256"], dependencies_json=canonical_candidate_json(dependencies), configuration_json=canonical_candidate_json(candidate["project_configuration"]))
    plan.evidence["operations"] = operations
    current, fingerprint, _bindings = pipeline_candidate(plan)
    if fingerprint != candidate_fingerprint or current != candidate:
        raise ValueError("Executable, dependencies, contracts or processing configuration differ from the tested candidate.")
    diagnostics = [row for row in metadata_records("METADATA_GUARDRAIL_RESULTS", context={**runtime, "config": config, "env": run["environment_name"]}, spark_session=spark_session)
                   if row.get("run_id") == testing_run_id]
    if any(row.get("can_continue") is not True or row.get("execution_type") != "testing" for row in diagnostics):
        raise ValueError("Testing has blocking or invalid Guardrail diagnostics.")
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
    return {"format": "fabricops.activated-pipeline.v1", "pipeline_id": run["pipeline_id"],
            "pipeline_name": str(pipeline_name).strip(), "pipeline_version": str(pipeline_version).strip(),
            "testing_run_id": testing_run_id, "candidate": candidate,
            "contracts": sorted(definitions, key=lambda item: item["participant"]),
            "agreement": agreement_definition(agreement),
            "warnings": ["Testing does not verify deployment permissions, target transactions or concurrent business writes."]
                        + [f"{key}: {stage['stage']} {stage['status']}" for key, operation in operations.items()
                           for stage in operation["stages"] if stage.get("status") in {"warning", "skipped"}]}


def commit_pipeline_activation(row, *, expected_active_id, context, spark_session=None):
    """Use one serializable Delta MERGE for immutable versions and active switching."""
    from delta.tables import DeltaTable
    config, _env, _runtime = resolve_fabric_context(context=context)
    spark = get_spark_session(spark_session)
    _store, _table, _schema, path = resolve_configured_lakehouse_table("Metadata", ACTIVATED_TABLE,
        metadata_table_physical_schema(config, ACTIVATED_TABLE), context=context)
    quoted_path = path.replace("`", "``")
    # Serializable predicate conflict detection includes concurrent first insertions.
    spark.sql(f"ALTER TABLE delta.`{quoted_path}` SET TBLPROPERTIES ('delta.isolationLevel' = 'Serializable')")
    source = spark.createDataFrame([coerce_metadata_row_types(ACTIVATED_TABLE, row)], schema=metadata_table_schema_registry()[ACTIVATED_TABLE])
    def literal(value):
        return "'" + str(value).replace("'", "''") + "'"
    pipeline = literal(row["pipeline_id"])
    expected = literal(expected_active_id or "")
    active = "true" if row["is_active"] else "false"
    # Never update immutable version fields; conflicting contents or a stale switch abort atomically.
    selected = literal(row["activated_pipeline_id"])
    # Guard an expected active row even after concurrent deactivation, and guard
    # selecting/deactivating that same version against its changed active state.
    expected_selected_state = "target.is_active = true" if expected_active_id == row["activated_pipeline_id"] else "target.is_active = false"
    check = f"CASE WHEN target.manifest_json = source.manifest_json AND {expected_selected_state} THEN {active} ELSE CAST(raise_error('Immutable version collision or stale activation state') AS BOOLEAN) END"
    deactivate = f"CASE WHEN target.activated_pipeline_id = {expected} AND target.is_active = true THEN false ELSE CAST(raise_error('Concurrent activation or explicit switching required') AS BOOLEAN) END"
    audit_columns = [key for key in metadata_table_schema_registry()[ACTIVATED_TABLE].fieldNames() if key.startswith("_") and key in row]
    audit_literals = {key: (f"CAST({literal(row[key])} AS TIMESTAMP)" if key == "_committed_at" else literal(row[key]))
                      for key in audit_columns}
    (DeltaTable.forPath(spark, path).alias("target")
     .merge(source.alias("source"), f"target.pipeline_id = {pipeline} AND target.pipeline_version = source.pipeline_version")
     .whenMatchedUpdate(set={"is_active": check, **{key: "source." + key for key in audit_columns}})
     .whenNotMatchedInsertAll()
     .whenNotMatchedBySourceUpdate(condition=f"target.pipeline_id = {pipeline} AND (target.is_active = true OR target.activated_pipeline_id = {expected}) AND target.activated_pipeline_id <> {selected}", set={"is_active": deactivate, **audit_literals})
     .execute())


def activation_version(activated_pipeline_id, *, context, spark_session=None, require_active=True):
    """Resolve an exact approved version without choosing a newer version."""
    row = exact_record(metadata_records(ACTIVATED_TABLE, context=context, spark_session=spark_session), activated_pipeline_id=activated_pipeline_id)
    if require_active and row.get("is_active") is not True:
        raise ValueError("The saved Activated Pipeline version is inactive; switch explicitly.")
    if require_active:
        active = [item for item in metadata_records(ACTIVATED_TABLE, context=context, spark_session=spark_session)
                  if item.get("pipeline_id") == row["pipeline_id"] and item.get("is_active") is True]
        if len(active) != 1:
            raise ValueError("Activated Pipeline integrity error: multiple active versions.")
    validate_manifest(row)
    return row


def approve_pipeline(*, manifest, governance_confirmed, expected_active_id, context, spark_session=None):
    """Commit explicit Governance confirmation with no deployment or publication."""
    if governance_confirmed is not True:
        raise ValueError("Explicit Governance confirmation is required.")
    config, env, runtime = resolve_fabric_context(context=context)
    existing = metadata_records(ACTIVATED_TABLE, context=context, spark_session=spark_session)
    versions = [row for row in existing if row["pipeline_id"] == manifest["pipeline_id"]]
    active = [row for row in versions if row.get("is_active") is True]
    if len(active) > 1 or (active[0]["activated_pipeline_id"] if active else None) != expected_active_id:
        raise ValueError("Active pipeline changed or explicit switching is required.")
    identifier = manifest_digest(manifest)
    same_version = [row for row in versions if row["pipeline_version"] == manifest["pipeline_version"]]
    if same_version and (len(same_version) != 1 or same_version[0]["activated_pipeline_id"] != identifier):
        raise ValueError("Pipeline version contents are immutable; choose a new version.")
    row = {key: manifest[key] for key in ("pipeline_id", "pipeline_name", "pipeline_version", "testing_run_id")}
    row.update(activated_pipeline_id=identifier, agreement_id=manifest["agreement"]["agreement_id"],
               agreement_version=manifest["agreement"]["agreement_version"], candidate_fingerprint=manifest_digest(manifest["candidate"]),
               manifest_json=canonical_candidate_json(manifest), is_active=True,
               **build_runtime_audit_fields(config=config, env=env, runtime_context=runtime))
    commit_pipeline_activation(row, expected_active_id=expected_active_id, context=context, spark_session=spark_session)
    return row


def bound_pipeline_participants(*, sources, targets, context, spark_session=None):
    """Capture explicit physical bindings independently of portable candidate identity."""
    config, env, runtime = resolve_fabric_context(context=context)
    identities = resolve_pipeline_participants(config, env, sources=sources, targets=targets, context=runtime, spark_session=spark_session)
    result = {}
    for table_id, item in identities.items():
        store = get_store(config, env, item["store"])
        result[item["logical_id"]] = {"table_id": table_id, "store": item["store"], "schema": item.get("schema"),
            "table_name": item["table_name"], "roles": sorted(item["roles"]), "workspace_id": store.workspace_id,
            "item_id": store.item_id, "kind": store.kind}
    return result


def load_live_deployment(*, deployment_path, pipeline_id, sources, targets, activated_pipeline_id=None,
                         replace_selection=False, context, spark_session=None):
    """Verify packaged approval, deployment bindings and a persisted exact selection."""
    config, env, runtime = resolve_fabric_context(context=context)
    root = Path(deployment_path).resolve(strict=True)
    bindings = json.loads((root / "deployment.json").read_text())
    package = json.loads((root / "approved.json").read_text())
    manifest = validate_manifest(package)
    if manifest["pipeline_id"] != pipeline_id or bindings.get("pipeline_id") != pipeline_id:
        raise ValueError("Deployment pipeline identity mismatch.")
    authority_context = {**runtime, "config": config, "env": bindings["authority_environment"]}
    approved = activation_version(package["activated_pipeline_id"], context=authority_context, spark_session=spark_session)
    if approved["manifest_json"] != package["manifest_json"]:
        raise ValueError("Packaged manifest does not match Governance approval.")
    current_agreement = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=authority_context, spark_session=spark_session),
        agreement_id=approved["agreement_id"], agreement_version=approved["agreement_version"])
    validate_agreement(current_agreement)
    if agreement_definition(current_agreement) != manifest["agreement"]:
        raise ValueError("Exact approved Agreement content changed.")
    actual = bound_pipeline_participants(sources=sources, targets=targets, context=context, spark_session=spark_session)
    if bindings.get("environment_name") != env or bindings.get("notebook_id") != runtime.get("notebook_id") or bindings.get("workspace_id") != runtime.get("workspace_id") or bindings.get("participants") != actual:
        raise ValueError("Deployment/environment bindings mismatch.")
    if set(actual) != {item["participant"] for item in manifest["candidate"]["participants"]}:
        raise ValueError("Approved pipeline participants mismatch.")
    for item in manifest["candidate"]["participants"]:
        if sorted(item["roles"]) != actual[item["participant"]]["roles"]:
            raise ValueError("Approved pipeline role mismatch.")
    executable = root / "executable.bin"
    if notebook_executable_fingerprint(executable.read_bytes()) != manifest["candidate"]["executable_sha256"]:
        raise ValueError("Deployed executable identity mismatch.")
    from fabricops_kit.pipeline.shared import deployed_notebook_fingerprint
    if deployed_notebook_fingerprint(runtime) != manifest["candidate"]["executable_sha256"]:
        raise ValueError("Actual Fabric notebook differs from the approved deployed executable.")
    selection_path = root / (hashlib.sha256((pipeline_id + "\0" + env).encode()).hexdigest() + ".selection.json")
    if selection_path.exists():
        selected = json.loads(selection_path.read_text())
        if activated_pipeline_id is None:
            activated_pipeline_id = selected.get("activated_pipeline_id")
        elif selected.get("activated_pipeline_id") != activated_pipeline_id and not replace_selection:
            raise ValueError("Saved selection differs; explicitly replace the selection to switch versions.")
    elif activated_pipeline_id is None:
        raise ValueError("No saved Live selection; explicitly select an activated version once.")
    if activated_pipeline_id != approved["activated_pipeline_id"]:
        raise ValueError("Saved Live selection does not match the deployed approved version.")
    selection = canonical_candidate_json({"activated_pipeline_id": activated_pipeline_id, "pipeline_id": pipeline_id, "environment_name": env})
    if not selection_path.exists():
        with selection_path.open("x") as handle:
            handle.write(selection)
    elif replace_selection:
        temporary = selection_path.with_suffix(".tmp")
        temporary.write_text(selection)
        temporary.replace(selection_path)
    return approved, manifest, actual, bindings


def build_live_pipeline_plan(*, deployment_path, pipeline_id, sources, targets, activated_pipeline_id=None,
                             replace_selection=False, configuration=None, context=None, spark_session=None):
    """Resolve a saved approved deployment into a new immutable unattended Live run."""
    from types import MappingProxyType
    from uuid import uuid4
    from fabricops_kit.pipeline.shared import persist_pipeline_run
    config, env, runtime = resolve_fabric_context(context=context)
    approved, manifest, bindings, deployment = load_live_deployment(deployment_path=deployment_path, pipeline_id=pipeline_id,
        sources=sources, targets=targets, activated_pipeline_id=activated_pipeline_id, replace_selection=replace_selection,
        context=context, spark_session=spark_session)
    identities = resolve_pipeline_participants(config, env, sources=sources, targets=targets, context=runtime, spark_session=spark_session)
    definitions = {item["participant"]: item["definition"] for item in manifest["contracts"]}
    contracts = {table_id: {**definitions[item["logical_id"]],
        "contract_payload": json.loads(definitions[item["logical_id"]]["contract_payload_json"])} for table_id, item in identities.items()}
    dependencies = {name: item["required"] for name, item in manifest["candidate"]["dependencies"].items()}
    run_context = {**runtime, "config": config, "env": env, "_pipeline_deployment_path": str(Path(deployment_path).resolve()),
                   "_pipeline_sources": sources, "_pipeline_targets": targets}
    plan = PipelineExecutionPlan("live", env, str(runtime["notebook_id"]), str(uuid4()), canonical_candidate_json(identities),
        "{}", canonical_candidate_json(contracts), MappingProxyType(run_context), pipeline_id=pipeline_id,
        executable_sha256=manifest["candidate"]["executable_sha256"], dependencies_json=canonical_candidate_json(dependencies),
        configuration_json=canonical_candidate_json(configuration),
        activated_pipeline_id=approved["activated_pipeline_id"], approved_candidate_json=canonical_candidate_json(manifest["candidate"]))
    verify_live_plan(plan, spark_session=spark_session)
    persist_pipeline_run(plan, spark_session=spark_session)
    return plan


def verify_live_plan(plan, *, spark_session=None):
    """Recheck approval, deployment and executable/dependency identity before execution."""
    from dataclasses import replace
    if not plan.activated_pipeline_id or not plan.approved_candidate_json:
        raise ValueError("Live requires an approved Activated Pipeline manifest.")
    runtime = plan.runtime_context
    _approved, manifest, _actual, _bindings = load_live_deployment(
        deployment_path=runtime["_pipeline_deployment_path"], pipeline_id=plan.pipeline_id,
        sources=runtime["_pipeline_sources"], targets=runtime["_pipeline_targets"],
        context=runtime, spark_session=spark_session)
    if canonical_candidate_json(manifest["candidate"]) != plan.approved_candidate_json:
        raise ValueError("Approved candidate changed during this Live run.")
    journal = {item["operation"]: {"status": "not_started", "configuration": item["configuration"],
                "configuration_sha256": item["configuration_sha256"]} for item in manifest["candidate"]["operations"]}
    check = replace(plan, evidence={**plan.evidence, "operations": journal})
    candidate, fingerprint, _bindings = pipeline_candidate(check)
    if candidate != manifest["candidate"] or fingerprint != manifest_digest(manifest["candidate"]):
        raise ValueError("Live executable, dependencies, contracts or configuration identity mismatch.")


def resolve_approved_consumer_contract(config, env, table_id, *, spark_session=None):
    """Resolve reusable contract/Agreement context through an active pipeline manifest."""
    matches = []
    for row in metadata_records(ACTIVATED_TABLE, context={"config": config, "env": env}, spark_session=spark_session):
        if row.get("is_active") is not True:
            continue
        manifest = validate_manifest(row)
        for item in manifest["contracts"]:
            definition = item["definition"]
            if definition["table_id"] == table_id:
                matches.append({**definition, "contract_payload": json.loads(definition["contract_payload_json"]),
                    "agreement_id": row["agreement_id"], "agreement_version": row["agreement_version"]})
    if not matches or any(item != matches[0] for item in matches):
        raise ValueError("No unambiguous active pipeline approval covers this consumer table.")
    return matches[0]
