"""One-time retained-format migration; no legacy authorization engine is exposed."""
from __future__ import annotations

import hashlib
import json

from fabricops_kit.config.metadata_schemas import (
    AUDIT_SCHEMA_FIELDS, BINDING_FIELDS,
    build_metadata_schema, metadata_table_schema_registry,
)
from fabricops_kit.activated_pipeline.shared import (
    REGISTRY_TABLE, OPERATION_FIELDS, empty_pipeline_authority, registry_control, registry_record_id,
    manifest_digest, metadata_records, exact_record, agreement_definition, registry_path,
    write_governance_archive, replace_registry_transaction, ensure_registry_audit_receipts,
)
from fabricops_kit.pipeline.shared import (
    validate_pipeline_run, validate_pipeline_id, contract_guardrail_rows, pipeline_record_content, canonical_pipeline_json,
)

REGISTRATION_FIELDS = [("pipeline_id", "string", False), ("workspace_id", "string", False), ("notebook_id", "string", False),
                       ("notebook_name", "string", False), ("registered_at", "timestamp", False),
                       ("registered_by", "string", False), ("registration_status", "string", False), *AUDIT_SCHEMA_FIELDS]
APPROVAL_FIELDS = [("approval_id", "string", False),
                   ("pipeline_id", "string", False), ("workspace_id", "string", False),
                   ("pipeline_name", "string", False), ("pipeline_version", "string", False),
                   ("testing_run_id", "string", False), ("testing_evidence_sha256", "string", False),
                   ("agreement_id", "string", False), ("agreement_version", "string", False),
                   ("agreement_sha256", "string", False), ("warnings", "strings", False), *AUDIT_SCHEMA_FIELDS]
OWNERSHIP_FIELDS = [("workspace_id", "string", False), ("table_id", "string", False),
                    ("contract_id", "string", False), ("contract_version", "integer", False),
                    ("payload_sha256", "string", False), ("writer", "string"),
                    ("readers", "strings", False),
                    ("destination", {"struct": [(n,t,z) for n,t,z in BINDING_FIELDS if n != "table_id"]}, False)]
RESERVATION_FIELDS = [("workspace_id", "string", False), ("reservation_id", "string", False),
                      ("pipeline_id", "string", False), ("mode", "string", False),
                      ("tables", "strings", False), ("revision", "string"),
                      ("destinations", [(n,t,z) for n,t,z in BINDING_FIELDS if n != "table_id"])]


def _legacy_registry_schema():
    """Recognize only the supported pre-cutover singleton physical format."""
    return build_metadata_schema(REGISTRY_TABLE, [
        ("authority_id", "string", False), ("token", "string", False),
        ("registrations", REGISTRATION_FIELDS, False),
        ("revisions", [("workspace_id", "string", False), ("revision", "string", False)], False),
        ("approvals", APPROVAL_FIELDS, False),
        ("selections", [("workspace_id", "string", False), ("pipeline_id", "string", False), ("approval_id", "string", False)], False),
        ("table_ownership", OWNERSHIP_FIELDS, False), ("reservations", RESERVATION_FIELDS, False), *AUDIT_SCHEMA_FIELDS])

def _legacy_run_contracts(run, *, context, spark_session=None):
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
        selected = {key: contract[key] for key in ("contract_id", "contract_version", "table_id", "status", "contract_payload_json")}
        if table_id in contracts and contracts[table_id] != selected:
            raise ValueError("A run cannot select different contract versions for the same table.")
        contracts[table_id] = selected
    return contracts

def _legacy_testing_run_evidence(run, *, context, spark_session=None):
    """Require a finalized Test with complete table-level checks and exact diagnostics."""
    run = validate_pipeline_run(run)
    contracts = _legacy_run_contracts(run, context=context, spark_session=spark_session)
    if run["execution_mode"] != "testing" or run["status"] != "succeeded":
        raise ValueError("Activation requires a complete successful Testing run.")
    mappings = _legacy_pipeline_table_mappings(run)
    rules = {table_id: contract_guardrail_rows(contract, workspace_id=run["workspace_id"], table_id=table_id)
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
           or item.get("workspace_id") != run["workspace_id"] or any(
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

def _legacy_approval_record(row, *, context, spark_session=None):
    """Resolve a retained approved Test and verify its exact contracts and Agreement."""
    run = exact_record(metadata_records("METADATA_PIPELINE_RUN", context=context, spark_session=spark_session,
        run_id=row["testing_run_id"]), run_id=row["testing_run_id"])
    evidence, contracts = _legacy_testing_run_evidence(run, context=context, spark_session=spark_session)
    agreement = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=context, spark_session=spark_session),
                             agreement_id=row["agreement_id"], agreement_version=row["agreement_version"])
    if (manifest_digest(pipeline_record_content(evidence)) != row["testing_evidence_sha256"]
            or manifest_digest(agreement_definition(agreement)) != row["agreement_sha256"]
            or run["pipeline_id"] != row["pipeline_id"] or run["workspace_id"] != row["workspace_id"]):
        raise ValueError("Approved Test or Agreement changed; restore exact retained history.")
    return {**row, "operations": run["operations"], "contracts": contracts, "testing_run": run}

def _legacy_pipeline_table_mappings(run):
    """Collect table contracts and physical bindings directly from operation facts."""
    mappings = {}
    for operation in run["operations"]:
        ref = {key: operation[key] for key in ("contract_id", "contract_version", "payload_sha256", "destination")}
        previous = mappings.setdefault(operation["table_id"], {**ref, "roles": []})
        if any(previous[key] != value for key, value in ref.items()):
            raise ValueError("Conflicting table contracts or destinations inside one run.")
        previous["roles"].append(operation["pipeline_role"])
    return mappings

def migrate_registry(*, table, context, spark_session):
    """Idempotently archive and replace supported legacy authority without authorizing candidates."""
    if not hasattr(table, "schema"):
        return table, None
    expected = metadata_table_schema_registry()[REGISTRY_TABLE]
    if table.schema.simpleString() == expected.simpleString():
        rows = [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in table.collect()]
        control = registry_control(rows)
        if control.get("migration_archive_uri") or control.get("last_governance_audit_uri"):
            ensure_registry_audit_receipts(rows, path=registry_path(context=context), spark_session=spark_session)
        return table, None
    if table.schema.simpleString() != _legacy_registry_schema().simpleString():
        raise ValueError("Unsupported Registry layout/extensions; reconcile before automatic migration.")
    spark, path = spark_session, registry_path(context=context)
    log = spark._jvm.org.apache.spark.sql.delta.DeltaLog.forTable(spark._jsparkSession, path)
    txn = log.startTransaction()
    txn.readWholeTable()
    files = txn.filterFiles()
    version = int(txn.readVersion())
    source = spark.read.format("delta").option("versionAsOf", version).load(path)
    if source.schema.simpleString() == expected.simpleString():
        registry_control([row.asDict(recursive=True) for row in source.collect()])
        return source, None
    if source.schema.simpleString() != _legacy_registry_schema().simpleString():
        raise ValueError("Registry schema changed during migration; refresh setup.")
    raw = [row.asDict(recursive=True) for row in source.collect()]
    if len(raw) != 1 or raw[0]["authority_id"] != "central" or not raw[0]["token"]:
        raise ValueError("Legacy Registry singleton is missing or duplicated.")
    old = raw[0]
    for name in ("registrations", "revisions", "approvals", "selections", "table_ownership", "reservations"):
        if not isinstance(old[name], list) or any(not isinstance(row, dict) for row in old[name]):
            raise ValueError("Invalid legacy collection: " + name)
    if old["reservations"]:
        raise ValueError("Drain and reconcile every legacy reservation before migration; none may be cleared automatically.")
    identities = {
        "registrations": ("workspace_id", "pipeline_id"), "revisions": ("workspace_id",),
        "approvals": ("approval_id",), "selections": ("workspace_id", "pipeline_id"),
        "table_ownership": ("workspace_id", "table_id")}
    for name, fields in identities.items():
        keys = [tuple(row.get(field) for field in fields) for row in old[name]]
        if any(not all(key) for key in keys) or len(keys) != len(set(keys)):
            raise ValueError("Ambiguous or duplicate legacy " + name)
    labels = [(row["workspace_id"], row["pipeline_id"], row["pipeline_version"]) for row in old["approvals"]]
    if len(labels) != len(set(labels)):
        raise ValueError("Conflicting retained approval version labels.")
    for registration in old["registrations"]:
        if validate_pipeline_id(registration["pipeline_id"]) != registration["pipeline_id"]:
            raise ValueError("Legacy Pipeline ID is not canonical lowercase.")
        if registration["registration_status"] not in {"Active", "Retired"}:
            raise ValueError("Unknown legacy registration status.")
    workspaces = {row["workspace_id"] for row in old["revisions"]}
    if any(row["workspace_id"] not in workspaces for name in ("approvals", "selections", "table_ownership") for row in old[name]):
        raise ValueError("Legacy member has no exact workspace revision.")
    # Validate every retained approval, including nonselected historical evidence.
    approvals = {}
    for approval in old["approvals"]:
        native = {key: value for key, value in approval.items() if not key.startswith("_") and key != "approval_id"}
        if manifest_digest(native) != approval["approval_id"]:
            raise ValueError("Legacy approval identity/content mismatch.")
        scoped = {**context, "scope_workspace_id": approval["workspace_id"],
                  "metadata_workspace_id": context.get("metadata_workspace_id") or context["scope_workspace_id"]}
        approvals[approval["approval_id"]] = _legacy_approval_record(approval, context=scoped, spark_session=spark)
    audit = {name: old[name] for name, *_ in AUDIT_SCHEMA_FIELDS}
    candidates, derived = [], {}
    for selection in old["selections"]:
        approval = approvals.get(selection["approval_id"])
        workspace, pipeline_id = selection["workspace_id"], selection["pipeline_id"]
        if not approval or approval["workspace_id"] != workspace or approval["pipeline_id"] != pipeline_id:
            raise ValueError("Legacy selection/approval identity mismatch.")
        registration = exact_record(old["registrations"], workspace_id=workspace, pipeline_id=pipeline_id)
        run = approval["testing_run"]
        if registration["registration_status"] != "Active" or run.get("_notebook_id") != registration["notebook_id"] or run.get("_workspace_id") != workspace:
            raise ValueError("Selected legacy notebook binding changed; reconcile before migration.")
        candidates.append({**audit, "record_id": registry_record_id("pipeline_activation", workspace, pipeline_id),
            "record_type": "pipeline_activation", "schema_version": 2, "workspace_id": workspace,
            "pipeline_id": pipeline_id, "pipeline_name": approval["pipeline_name"], "notebook_id": registration["notebook_id"],
            "status": "requires_reactivation", "operations_json": canonical_pipeline_json([
                {field: op.get(field) for field in OPERATION_FIELDS} for op in approval["operations"]]),
            **{key: approval[key] for key in ("agreement_id", "agreement_version", "agreement_sha256")}})
        for table_id, mapping in _legacy_pipeline_table_mappings(run).items():
            key = (workspace, table_id)
            ref = {field: mapping[field] for field in ("contract_id", "contract_version", "payload_sha256", "destination")}
            table_ref = derived.setdefault(key, {**ref, "writer": None, "readers": []})
            if any(table_ref[field] != ref[field] for field in ref):
                raise ValueError("Conflicting selected Contract versions or destinations; reconcile explicitly.")
            if "target" in mapping["roles"]:
                if table_ref["writer"] is not None and table_ref["writer"] != pipeline_id:
                    raise ValueError("Ambiguous legacy multiwriter authority.")
                table_ref["writer"] = pipeline_id
            if "source" in mapping["roles"]:
                table_ref["readers"].append(pipeline_id)
    for value in derived.values():
        value["readers"].sort()
    ownership = {(row["workspace_id"], row["table_id"]): {key: value for key, value in row.items()
        if key not in {"workspace_id", "table_id"}} for row in old["table_ownership"]}
    if ownership != derived:
        raise ValueError("Legacy ownership does not exactly match selected operations; reconcile explicitly.")
    for (workspace, table_id), ref in sorted(derived.items()):
        candidates.append({**audit, "record_id": registry_record_id("table_contract_activation", workspace, table_id),
            "record_type": "table_contract_activation", "schema_version": 2, "workspace_id": workspace,
            "table_id": table_id, "status": "requires_reactivation",
            "destination_json": canonical_pipeline_json(ref["destination"]),
            **{key: ref[key] for key in ("contract_id", "contract_version", "payload_sha256")}})
    from fabricops_kit import __version__
    archive_payload = {"format": "fabricops-registry-cutover-v2", "package_version": __version__, "source_path": path,
        "source_version": version, "source_metadata": json.loads(txn.metadata().json()),
        "source_schema": source.schema.jsonValue(), "rows": raw,
        "registration_ids": [{"pipeline_id": row["pipeline_id"], "workspace_id": row["workspace_id"],
            "notebook_id": row["notebook_id"], "registration_status": row["registration_status"]} for row in old["registrations"]]}
    uri, digest = write_governance_archive(archive_payload, path=path, spark_session=spark)
    control = {**empty_pipeline_authority(), **audit, "migration_archive_uri": uri, "migration_archive_sha256": digest}
    rows = [control, *candidates]
    registry_control(rows)
    committed = replace_registry_transaction(txn, files, rows, spark_session=spark, path=path, schema_change=True,
        recovery={"fabricops_registry_migration": 2, "source_version": version, "migration_archive_uri": uri,
            "migration_archive_sha256": digest, "token": control["token"]})
    ensure_registry_audit_receipts(rows, path=path, spark_session=spark)
    return spark.read.format("delta").load(path), {
        "pre_upgrade_version": version, "upgrade_version": committed, "migration_archive_uri": uri,
        "migration_archive_sha256": digest, "requires_reactivation": [row["record_id"] for row in candidates],
        "registration_ids": archive_payload["registration_ids"]}
