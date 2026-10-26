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
from fabricops_kit.pipeline.shared import PipelineExecutionPlan, canonical_pipeline_json, validate_pipeline_run, contract_guardrail_rows, resolve_pipeline_participants, pipeline_record_content



def manifest_digest(value):
    """Hash canonical metadata for retained result integrity and reviewed approval identity."""
    return hashlib.sha256(canonical_pipeline_json(pipeline_record_content(value)).encode("utf-8")).hexdigest()


def metadata_records(table, *, context, spark_session=None, run_id=None):
    """Read domain metadata through its configured owner schema."""
    config, _env, _runtime = resolve_fabric_context(context=context)
    frame = read_lakehouse_table(table, store="Metadata", schema=metadata_table_physical_schema(config, table),
                                context={**(context or {}), "_spark_session": spark_session})
    if table == "METADATA_PIPELINE_RUN":
        from pyspark.sql import functions as F
        frame = frame.filter(F.col("environment_name") == _env)
        if run_id is not None:
            frame = frame.filter(F.col("run_id") == run_id)
    rows = [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in frame.collect()]
    if table == "METADATA_PIPELINE_RUN":
        return [validate_pipeline_run(row) for row in rows]
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


def run_contracts(run, *, context, spark_session=None):
    """Resolve each exact table contract recorded by an actual operation."""
    rows = metadata_records("METADATA_DATA_CONTRACT", context=context, spark_session=spark_session)
    missing = sorted({item["table_id"] for item in run["operations"] if not item.get("contract_id")})
    if missing:
        raise ValueError("Activation requires an exact frozen contract for every source and target. Missing contracts for table IDs: " + ", ".join(missing))
    contracts = {}
    for operation in run["operations"]:
        table_id = operation["table_id"]
        if not operation.get("contract_id"):
            raise ValueError("Activation requires an exact frozen contract for every source and target. Missing contracts for table IDs: " + table_id)
        contract = exact_record(rows, contract_id=operation["contract_id"], contract_version=operation["contract_version"])
        if (contract["table_id"] != table_id or contract["status"] != "frozen"
                or hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest() != operation["payload_sha256"]):
            raise ValueError("Frozen contract changed since Testing.")
        selected = {key: contract[key] for key in ("contract_id", "contract_version", "table_id", "status", "contract_payload_json", "environment_name")}
        if table_id in contracts and contracts[table_id] != selected:
            raise ValueError("A run cannot select different contract versions for the same table.")
        contracts[table_id] = selected
    return contracts


def testing_run_evidence(run, *, context, spark_session=None):
    """Require a finalized Test with complete table-level checks and exact diagnostics."""
    validate_pipeline_run(run)
    contracts = run_contracts(run, context=context, spark_session=spark_session)
    if run["execution_mode"] != "testing" or run["status"] != "succeeded":
        raise ValueError("Activation requires a complete successful Testing run.")
    mappings = pipeline_table_mappings(run)
    rules = {table_id: contract_guardrail_rows(contract, environment_name=run["environment_name"], table_id=table_id)
             for table_id, contract in contracts.items()}
    drift_sources = {table_id for table_id, entries in rules.items() if any(rule["guardrail_type"] == "source_drift" for rule in entries)}
    labels = {"schema": "Schema", "grain": "Grain", "data_quality": "Data Quality", "freshness": "Freshness", "sensitive_data": "Sensitive Data"}
    for operation in run["operations"]:
        role, table_id = operation["pipeline_role"], operation["table_id"]
        required = {"Read"} if role == "source" else {"Processing"}
        if role == "source" and operation["read_mode"] == "full":
            required.add("Profile")
        for rule in rules[table_id]:
            kind = rule["guardrail_type"]
            if kind in {"schema", "grain", "data_quality"} or (role == "source" and kind == "freshness") or (role == "target" and kind == "sensitive_data"):
                required.add(labels[kind])
        if role == "target" and drift_sources.intersection(operation["source_table_ids"]):
            required.add("Source Drift")
        stages = {stage["stage"]: stage for stage in operation["stages"]}
        skipped_freshness = any(rule["guardrail_type"] == "freshness" and rule.get("rule_type") == "skip" for rule in rules[table_id])
        if required - set(stages) or any(stages[name]["status"] not in (
                {"passed", "warning", "skipped"} if name == "Freshness" and skipped_freshness else {"passed", "warning"}) for name in required):
            raise ValueError("Required operation stages are missing or incomplete; rerun complete Testing.")
        if role == "target" and any(source not in mappings or "source" not in mappings[source]["roles"] for source in operation["source_table_ids"]):
            raise ValueError("Write references a source outside this Test run.")
    diagnostics = sorted((item for item in metadata_records("METADATA_GUARDRAIL_RESULTS", context=context, spark_session=spark_session)
                          if item.get("run_id") == run["run_id"]), key=lambda item: item["guardrail_result_id"])
    if len({item["guardrail_result_id"] for item in diagnostics}) != len(diagnostics):
        raise ValueError("Duplicate Testing Guardrail results.")
    if any(item.get("can_continue") is not True or item.get("execution_type") != "testing"
           or item.get("environment_name") != run["environment_name"] or any(
               item.get(key) != run.get(key) for key in ("_workspace_id", "_notebook_id", "_activity_id")) for item in diagnostics):
        raise ValueError("Testing Guardrail diagnostics are blocking or have invalid run provenance.")
    from collections import Counter
    observed = Counter((item.get("table_id"), item.get("contract_id"), item.get("contract_version"),
                        item.get("guardrail_rule_id"), item.get("guardrail_version")) for item in diagnostics)
    expected = Counter()
    for table_id, contract in contracts.items():
        roles = mappings[table_id]["roles"]
        for rule in rules[table_id]:
            kind = rule["guardrail_type"]
            count = len(roles) if kind in {"schema", "grain", "data_quality"} else 0
            if kind == "freshness" and "source" in roles and rule.get("rule_type") != "skip":
                count = 1
            if kind == "sensitive_data" and "target" in roles:
                count = 1
            if kind == "source_drift" and "source" in roles:
                count = sum(table_id in operation["source_table_ids"] for operation in run["operations"] if operation["pipeline_role"] == "target")
            expected[(table_id, contract["contract_id"], contract["contract_version"], rule["guardrail_rule_id"], rule.get("guardrail_version", 1))] += count
    if observed != expected:
        raise ValueError("Required exact rule-level Guardrail evidence is missing.")
    return {"run": run, "guardrail_results": diagnostics}, contracts


def tested_pipeline_run(*, testing_run_id, pipeline_name, pipeline_version, agreement_id, agreement_version, context, spark_session=None):
    """Review an exact retained Test run; no separate configuration is created."""
    config, env, runtime = resolve_fabric_context(context=context)
    from fabricops_kit.pipeline.shared import read_pipeline_registry, validate_pipeline_id
    run = exact_record(metadata_records("METADATA_PIPELINE_RUN", context=context, spark_session=spark_session,
                                       run_id=testing_run_id), run_id=testing_run_id)
    validate_pipeline_id(run["pipeline_id"])
    _token, registrations = read_pipeline_registry(context=context, spark_session=spark_session)
    registration = exact_record(registrations, pipeline_id=run["pipeline_id"], environment_name=env)
    if registration["registration_status"] != "Active" or run["environment_name"] != env:
        raise ValueError("Testing requires the Active registration in the activation environment.")
    if any(run.get("_" + key) != registration[key] for key in ("workspace_id", "notebook_id")):
        raise ValueError("Testing was not run by the current registered notebook; rerun Test after rebinding.")
    evidence, contracts = testing_run_evidence(run, context=context, spark_session=spark_session)
    agreement = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=context, spark_session=spark_session),
                             agreement_id=agreement_id, agreement_version=agreement_version)
    validate_agreement(agreement)
    if not str(pipeline_name).strip() or not str(pipeline_version).strip():
        raise ValueError("Pipeline name and version are required.")
    native = {"pipeline_id": run["pipeline_id"], "environment_name": env,
        "pipeline_name": str(pipeline_name).strip(), "pipeline_version": str(pipeline_version).strip(),
        "testing_run_id": testing_run_id, "testing_evidence_sha256": manifest_digest(pipeline_record_content(evidence)),
        "agreement_id": agreement_id, "agreement_version": agreement_version,
        "agreement_sha256": manifest_digest(agreement_definition(agreement)),
        "warnings": ["Approval validates table contracts and operation modes, not notebook transformation code."]}
    native["approval_id"] = manifest_digest(native)
    native.update(**build_runtime_audit_fields(config=config, env=env, runtime_context=runtime))
    return {**native, "operations": run["operations"], "contracts": contracts, "testing_run": run}


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
    """Resolve a retained approved Test and verify its exact contracts and Agreement."""
    run = exact_record(metadata_records("METADATA_PIPELINE_RUN", context=context, spark_session=spark_session,
        run_id=row["testing_run_id"]), run_id=row["testing_run_id"])
    evidence, contracts = testing_run_evidence(run, context=context, spark_session=spark_session)
    agreement = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=context, spark_session=spark_session),
                             agreement_id=row["agreement_id"], agreement_version=row["agreement_version"])
    if (manifest_digest(pipeline_record_content(evidence)) != row["testing_evidence_sha256"]
            or manifest_digest(agreement_definition(agreement)) != row["agreement_sha256"]
            or run["pipeline_id"] != row["pipeline_id"] or run["environment_name"] != row["environment_name"]):
        raise ValueError("Approved Test or Agreement changed; restore exact retained history.")
    return {**row, "operations": run["operations"], "contracts": contracts, "testing_run": run}


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
    from fabricops_kit.config.metadata_schemas import APPROVAL_FIELDS
    row = empty_pipeline_authority()
    row["registrations"] = state.get("registrations", [])
    row["profiling_claims"] = list(state.get("profiling_claims", {}).values())
    for environment, current in sorted(state["environments"].items()):
        row["revisions"].append({"environment_name": environment, "revision": current["revision"]})
        for approval_id, item in sorted(current["history"].items()):
            row["approvals"].append({key: item[key] for key, *_rest in APPROVAL_FIELDS})
        row["selections"].extend({"environment_name": environment, "pipeline_id": key, "approval_id": item["approval_id"]}
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
    spark = get_spark_session(spark_session, context=context)
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


def pipeline_table_mappings(run):
    """Collect table contracts and physical bindings directly from operation facts."""
    mappings = {}
    for operation in run["operations"]:
        ref = {key: operation[key] for key in ("contract_id", "contract_version", "payload_sha256", "destination")}
        previous = mappings.setdefault(operation["table_id"], {**ref, "roles": []})
        if any(previous[key] != value for key, value in ref.items()):
            raise ValueError("Conflicting table contracts or destinations inside one run.")
        previous["roles"].append(operation["pipeline_role"])
    return mappings


def activation_impact(current, proposed):
    """Calculate conservative dependencies and validate the entire resulting release.

    Direct references to changed contracts/ownership require replacement tests.
    Propagation continues when a replacement changes a downstream table mapping;
    unchanged output expectations stop propagation. No inferred compatibility.
    """
    active = current["pipelines"]
    resulting = {**active, **proposed}
    mappings = {key: pipeline_table_mappings(row) for key, row in resulting.items()}
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
    for table in tables.values():
        table["readers"].sort()
    destinations = {}
    for table_id, table in tables.items():
        destination = canonical_pipeline_json(table["destination"])
        previous = destinations.setdefault(destination, table_id)
        if previous != table_id:
            blockers.append(f"Conflicting table identities share a physical destination: {previous} and {table_id}.")
    old = current["tables"]
    changed = {key for key in set(old) | set(tables) if
               {field: old.get(key, {}).get(field) for field in ("contract_id", "contract_version", "payload_sha256", "writer", "destination")} !=
               {field: tables.get(key, {}).get(field) for field in ("contract_id", "contract_version", "payload_sha256", "writer", "destination")}}
    affected = {pipeline_id for pipeline_id, row in active.items()
                if changed.intersection(pipeline_table_mappings(row))}
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
        row = tested_pipeline_run(**request, context=context, spark_session=spark_session)
        pipeline_id = row["pipeline_id"]
        if pipeline_id in proposed:
            raise ValueError("Select one Testing run per pipeline.")
        for previous in current["history"].values():
            if previous["pipeline_id"] == pipeline_id and previous["pipeline_version"] == row["pipeline_version"] and previous["approval_id"] != row["approval_id"]:
                raise ValueError("Pipeline version contents are immutable; choose a new version.")
        row = current["history"].get(row["approval_id"], row)
        proposed[pipeline_id] = row
    if not proposed:
        raise ValueError("Select at least one successful Testing candidate.")
    report = activation_impact(current, proposed)
    report["ready"] = not report["blocking_conflicts"]
    report["review_digest"] = manifest_digest({key: row["approval_id"] for key, row in proposed.items()})
    return token, state, proposed, {**report, "environment": env}


def approve_pipeline_release(requests, *, expected_token, expected_review_digest, governance_confirmed=False, context=None, spark_session=None):
    """Revalidate and publish the complete release in one authority transaction."""
    if governance_confirmed is not True:
        raise ValueError("Explicit Governance approval of the complete release is required.")
    token, state, proposed, report = review_pipeline_release(requests, context=context, spark_session=spark_session)
    if token != expected_token:
        raise ValueError("Activation state changed; refresh and review the release again.")
    if report["review_digest"] != expected_review_digest:
        raise ValueError("Reviewed Test results or Agreement changed; refresh and review before approval.")
    if not report["ready"]:
        raise ValueError(" ".join(report["blocking_conflicts"]))
    current = environment_activation(state, report["environment"])
    current["pipelines"].update(proposed)
    current["history"].update({row["approval_id"]: row for row in proposed.values()})
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


def activation_version(approval_id, *, context, spark_session=None, require_active=True):
    """Resolve an immutable approval from the environment's atomic authority."""
    _config, env, _runtime = resolve_fabric_context(context=context)
    _token, state = read_pipeline_authority(context=context, spark_session=spark_session)
    current = environment_activation(state, env)
    matches = [row for row in (current["pipelines"] if require_active else current["history"]).values()
               if row["approval_id"] == approval_id]
    if len(matches) != 1:
        raise ValueError("Approved version is missing or inactive in this environment.")
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
    tested_run = approved["testing_run"]
    if any(tested_run.get("_" + key) != registration[key] for key in ("workspace_id", "notebook_id")):
        raise ValueError("Registered notebook changed since the approved Test; rerun Test and approve the new binding before Live.")
    agreement = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=context, spark_session=spark_session),
        agreement_id=approved["agreement_id"], agreement_version=approved["agreement_version"])
    validate_agreement(agreement)
    mappings = pipeline_table_mappings(approved)
    logical = {item["table_id"]: item["operation_key"].split(":", 1)[1] for item in approved["operations"]}
    identities = resolve_pipeline_participants(config, env,
        sources=[{"table_id": key, "logical_id": logical[key]} for key, item in mappings.items() if "source" in item["roles"]],
        targets=[{"table_id": key, "logical_id": logical[key]} for key, item in mappings.items() if "target" in item["roles"]],
        context=runtime, spark_session=spark_session)
    contracts = {key: {**value, "contract_payload": json.loads(value["contract_payload_json"])} for key, value in approved["contracts"].items()}
    physical = pipeline_physical_bindings(identities, config=config, environment=env)
    if physical != {key: item["destination"] for key, item in mappings.items()} or {
            key: sorted(item["roles"]) for key, item in identities.items()} != {key: sorted(item["roles"]) for key, item in mappings.items()}:
        raise ValueError("Live tables or physical destinations differ from the approved Test run.")
    plan = PipelineExecutionPlan("live", env, str(runtime.get("notebook_id") or ""), str(uuid4()), canonical_pipeline_json(identities),
        "{}", canonical_pipeline_json(contracts), MappingProxyType({**runtime, "config": config, "env": env,
            "_pipeline_spark": spark_session, "_pipeline_bindings": physical}), pipeline_id=pipeline_id,
        approval_id=approved["approval_id"], approved_operations_json=json.dumps(approved["operations"], default=str),
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
    """Verify the pinned approval, exact table contracts, destinations and reservation."""
    _token, state = read_pipeline_authority(context=plan.runtime_context, spark_session=spark_session)
    current = environment_activation(state, plan.environment)
    lease = current["runs"].get(plan.plan_id)
    if not lease or lease.get("revision") != plan.activation_revision or lease.get("pipeline_id") != plan.pipeline_id:
        raise ValueError("Live run has no valid pinned activation reservation.")
    approved = current["history"].get(plan.approval_id)
    active = current["pipelines"].get(plan.pipeline_id)
    if not approved or not active or active["approval_id"] != plan.approval_id:
        raise ValueError("Pinned pipeline is no longer active; stop this run.")
    from fabricops_kit.pipeline.shared import pipeline_physical_bindings
    physical = pipeline_physical_bindings(json.loads(plan.participants_json), config=plan.runtime_context["config"], environment=plan.environment)
    if physical != {key: item["destination"] for key, item in pipeline_table_mappings(approved).items()}:
        raise ValueError("Live destinations changed during execution.")
    pinned = json.loads(plan.contracts_json)
    if any(any(pinned[table_id][key] != contract[key] for key in ("contract_id", "contract_version", "contract_payload_json"))
           for table_id, contract in approved["contracts"].items()):
        raise ValueError("Live table contracts differ from approval.")
    agreement = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=plan.runtime_context, spark_session=spark_session),
        agreement_id=approved["agreement_id"], agreement_version=approved["agreement_version"])
    validate_agreement(agreement)


def resolve_approved_consumer_contract(config, env, table_id, *, spark_session=None):
    """Resolve the single approved table mapping in an environment's revision."""
    _token, state = read_pipeline_authority(context={"config": config, "env": env}, spark_session=spark_session)
    current = environment_activation(state, env)
    matches = []
    for row in current["pipelines"].values():
        contract = row["contracts"].get(table_id)
        if contract:
            matches.append({**contract, "contract_payload": json.loads(contract["contract_payload_json"]),
                            "agreement_id": row["agreement_id"], "agreement_version": row["agreement_version"]})
    if not matches or any(item != matches[0] for item in matches):
        raise ValueError("No unambiguous active pipeline contract and Agreement cover this consumer table.")
    return matches[0]
