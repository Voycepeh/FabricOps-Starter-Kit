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
from fabricops_kit.pipeline.shared import PipelineExecutionPlan, canonical_candidate_json, pipeline_candidate, contract_guardrail_rows, resolve_pipeline_participants



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
    """Revalidate committed complete Testing evidence independently of any widget."""
    config, env, runtime = resolve_fabric_context(context=context)
    run = exact_record(metadata_records("METADATA_PIPELINE_RUN", context=context, spark_session=spark_session), run_id=testing_run_id)
    if run.get("environment_name") != env:
        raise ValueError("Testing evidence must cover the activation environment; other environments are isolated.")
    candidate = json.loads(run["candidate_json"])
    if not candidate_fingerprint or candidate_fingerprint != run.get("candidate_fingerprint") or manifest_digest(candidate) != candidate_fingerprint:
        raise ValueError("Exact tested candidate fingerprint mismatch.")
    missing = sorted(item["table_id"] for item in candidate["participants"] if item.get("contract") is None)
    if missing:
        raise ValueError("Activation requires an exact frozen contract for every source and target. Missing contracts for table IDs: " + ", ".join(missing))
    if run.get("execution_mode") != "testing" or run.get("status") != "succeeded" or not run.get("completed_at"):
        raise ValueError("Activation requires a complete successful Testing run; Bootstrap and partial results cannot authorize it.")
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
            required_stages = {"Read"} if role == "source" else ({"Write", "Profile"} if summary.get("testing_writes") else {"Processing"})
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
            "testing_run_id": testing_run_id, "candidate": candidate, "physical_bindings": summary["physical_bindings"],
            "contracts": sorted(definitions, key=lambda item: item["participant"]),
            "agreement": agreement_definition(agreement),
            "warnings": ["Testing does not verify deployment permissions, target transactions or concurrent business writes."]
                        + [f"{key}: {stage['stage']} {stage['status']}" for key, operation in operations.items()
                           for stage in operation["stages"] if stage.get("status") in {"warning", "skipped"}]}

ACTIVATION_STATE_TABLE = "METADATA_ACTIVATION_STATE"


def empty_activation_state():
    """Return the initial central authority; only metadata setup creates this row."""
    return canonical_candidate_json({"format": "fabricops.activation-state.v1", "environments": {}})


def read_activation_state(*, context, spark_session=None):
    """Read one atomic authority snapshot; missing or duplicate authority fails closed."""
    row = exact_record(metadata_records(ACTIVATION_STATE_TABLE, context=context, spark_session=spark_session), authority_id="central")
    state = json.loads(row["snapshot_json"])
    if state.get("format") != "fabricops.activation-state.v1":
        raise ValueError("Unsupported activation authority format.")
    return row["token"], state


def environment_activation(state, environment):
    """Return an isolated environment's approved configurations and run reservations."""
    return state["environments"].setdefault(environment, {"revision": "initial", "pipelines": {}, "history": {}, "tables": {}, "runs": {}})


def commit_activation_state(state, *, expected_token, context, spark_session=None):
    """Compare-and-swap the existing singleton using one serializable Delta MERGE.

    Setup creates the singleton with the table, never by racing first insertions.
    Both activations and run reservations update this row. An overlapping update
    conflicts in Delta or raises inside the MERGE. No automatic activation retry.
    A lost acknowledgement is accepted only after exact token read-back.
    """
    from delta.tables import DeltaTable
    from uuid import uuid4
    config, env, runtime = resolve_fabric_context(context=context)
    spark = get_spark_session(spark_session)
    _store, _table, _schema, path = resolve_configured_lakehouse_table("Metadata", ACTIVATION_STATE_TABLE,
        metadata_table_physical_schema(config, ACTIVATION_STATE_TABLE), context=context)
    spark.sql("ALTER TABLE delta.`" + path.replace("`", "``") + "` SET TBLPROPERTIES ('delta.isolationLevel' = 'Serializable')")
    token = str(uuid4())
    row = {"authority_id": "central", "token": token, "snapshot_json": canonical_candidate_json(state),
           **build_runtime_audit_fields(config=config, env=env, runtime_context=runtime)}
    frame = spark.createDataFrame([coerce_metadata_row_types(ACTIVATION_STATE_TABLE, row)],
                                  schema=metadata_table_schema_registry()[ACTIVATION_STATE_TABLE])
    expected = "'" + expected_token.replace("'", "''") + "'"
    changes = {key: "source." + key for key in row if key != "authority_id"}
    changes["token"] = f"CASE WHEN target.token = {expected} THEN source.token ELSE CAST(raise_error('Stale activation revision; refresh') AS STRING) END"
    try:
        (DeltaTable.forPath(spark, path).alias("target")
         .merge(frame.alias("source"), "target.authority_id = source.authority_id")
         .whenMatchedUpdate(set=changes).execute())
    except Exception:
        observed, _state = read_activation_state(context=context, spark_session=spark_session)
        if observed != token:
            raise
    observed, _state = read_activation_state(context=context, spark_session=spark_session)
    if observed != token:
        raise RuntimeError("Activation state commit was not confirmed; refresh before retrying.")
    return token


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
    token, state = read_activation_state(context=context, spark_session=spark_session)
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
        proposed[pipeline_id] = row
    if not proposed:
        raise ValueError("Select at least one successful Testing candidate.")
    report = activation_impact(current, proposed)
    changed_destinations = [item["destination"] for table_id, item in report["tables"].items()
                            if table_id in report["changed_tables"]]
    for other in state["environments"].values():
        for run_id, run in other["runs"].items():
            if run.get("mode") == "testing" and any(destination in run.get("destinations", []) for destination in changed_destinations):
                report["blocking_conflicts"].append(f"Drain Testing execution reserving a proposed destination: {run_id}.")
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
    commit_activation_state(state, expected_token=token, context=context, spark_session=spark_session)
    return {"environment": report["environment"], "revision": current["revision"], "pipelines": proposed}


def validate_testing_destinations(plan, *, spark_session=None, require_reservation=True):
    """Prevent explicitly authorized Testing writes to any Live-owned destination."""
    _token, state = read_activation_state(context=plan.runtime_context, spark_session=spark_session)
    targets = {key for key, item in json.loads(plan.participants_json).items() if "target" in item["roles"]}
    bindings = plan.runtime_context["_pipeline_bindings"]
    from fabricops_kit.pipeline.shared import pipeline_physical_bindings
    physical = pipeline_physical_bindings(json.loads(plan.participants_json), config=plan.runtime_context["config"], environment=plan.environment)
    if physical != bindings:
        raise ValueError("Testing physical destinations changed; create a new plan and review them again.")
    for current in state["environments"].values():
        for table_id in targets:
            if any(item.get("destination") == bindings[table_id] for item in current["tables"].values()):
                raise ValueError("Testing cannot write Live-owned destinations: " + table_id)
    if require_reservation:
        current = environment_activation(state, plan.environment)
        reservation = current["runs"].get(plan.plan_id)
        expected_destinations = [bindings[key] for key in sorted(targets)]
        if not reservation or reservation.get("mode") != "testing" or reservation.get("destinations") != expected_destinations:
            raise ValueError("Testing write reservation is missing or changed; create a new run.")
    return targets


def reserve_testing_destinations(plan, *, spark_session=None):
    """Reserve Testing destinations against activation until the boundary completes."""
    targets = validate_testing_destinations(plan, spark_session=spark_session, require_reservation=False)
    token, state = read_activation_state(context=plan.runtime_context, spark_session=spark_session)
    bindings = plan.runtime_context["_pipeline_bindings"]
    destinations = [bindings[key] for key in sorted(targets)]
    if any(item.get("destination") in destinations
           for other in state["environments"].values() for item in other["tables"].values()):
        raise ValueError("Testing destination became Live-owned; choose a separate destination.")
    current = environment_activation(state, plan.environment)
    if any(destination in run.get("destinations", []) for destination in destinations
           for other in state["environments"].values() for run in other["runs"].values()):
        raise ValueError("Testing destination is reserved by a running execution.")
    current["runs"][plan.plan_id] = {"pipeline_id": plan.pipeline_id, "tables": sorted(targets),
                                  "destinations": destinations, "mode": "testing"}
    commit_activation_state(state, expected_token=token, context=plan.runtime_context, spark_session=spark_session)
    plan.evidence["lease_token"] = plan.plan_id


def release_pipeline_lease(plan, *, spark_session=None):
    """Release only this completed run's reservation; failed release remains fail-closed."""
    for _attempt in range(5):
        token, state = read_activation_state(context=plan.runtime_context, spark_session=spark_session)
        current = environment_activation(state, plan.environment)
        if current["runs"].pop(plan.plan_id, None) is None:
            return
        try:
            commit_activation_state(state, expected_token=token, context=plan.runtime_context, spark_session=spark_session)
            plan.evidence.pop("lease_token", None)
            return
        except Exception:
            if _attempt == 4:
                raise


def activation_version(activated_pipeline_id, *, context, spark_session=None, require_active=True):
    """Resolve an immutable approval from the environment's atomic authority."""
    _config, env, _runtime = resolve_fabric_context(context=context)
    _token, state = read_activation_state(context=context, spark_session=spark_session)
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
    token, state = read_activation_state(context=context, spark_session=spark_session)
    current = environment_activation(state, env)
    approved = current["pipelines"].get(pipeline_id)
    if not approved:
        raise ValueError("No approved pipeline configuration for this environment and pipeline_id.")
    integrity = activation_impact(current, {})
    if integrity["tables"] != current["tables"] or integrity["blocking_conflicts"]:
        raise ValueError("Activation snapshot has inconsistent table mappings or ownership.")
    manifest = validate_manifest(approved)
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
    commit_activation_state(state, expected_token=token, context=context, spark_session=spark_session)
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
    _token, state = read_activation_state(context=plan.runtime_context, spark_session=spark_session)
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
    _token, state = read_activation_state(context={"config": config, "env": env}, spark_session=spark_session)
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
