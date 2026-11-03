"""Direct pipeline and table-contract activations in one transactional Registry."""
from __future__ import annotations

import hashlib
import json
from datetime import date, datetime, UTC
from uuid import uuid4

from fabricops_kit.config.audit import build_runtime_audit_fields
from fabricops_kit.config.metadata_schemas import (
    coerce_metadata_row_types, metadata_table_physical_schema, metadata_table_schema_registry, parse_metadata_json,
)
from fabricops_kit.config.shared import resolve_fabric_context
from fabricops_kit.io import read_lakehouse_table
from fabricops_kit.io.shared import get_spark_session, resolve_configured_lakehouse_table
from fabricops_kit.pipeline.shared import canonical_pipeline_json, pipeline_record_content, validate_pipeline_id, validate_pipeline_run

REGISTRY_TABLE = "METADATA_PIPELINE_REGISTRY"
DEPLOYMENT_PENDING = "Governed execution is unavailable: trusted deployment verification must be proven and integrated in the next PR."
OPERATION_FIELDS = (
    "operation_key", "table_id", "pipeline_role", "destination", "read_mode", "write_mode",
    "query_sha256", "incremental_target_table_id", "source_table_ids",
)
RUN_PROVENANCE_FIELDS = (
    "pipeline_activation_id", "deployment_id", "git_commit_sha", "deployment_verification_status", "run_schema_version",
)


def manifest_digest(value):
    """Hash canonical, timestamp-normalized retained metadata."""
    return hashlib.sha256(canonical_pipeline_json(pipeline_record_content(value)).encode("utf-8")).hexdigest()


def metadata_records(table, *, context, spark_session=None, run_id=None, all_workspaces=False):
    """Read metadata through its configured central owner, preserving execution scope."""
    config, workspace, runtime = resolve_fabric_context(context=context)
    routed = {**runtime, "config": config, "scope_workspace_id": str(runtime.get("metadata_workspace_id") or workspace)}
    frame = read_lakehouse_table(table, store="Metadata", schema=metadata_table_physical_schema(config, table),
        context={**routed, "_spark_session": spark_session, "_fabricops_suppress_io_log": True})
    if table == "METADATA_PIPELINE_RUN":
        from pyspark.sql import functions as F
        if not all_workspaces:
            frame = frame.filter(F.col("workspace_id") == workspace)
        if run_id is not None:
            frame = frame.filter(F.col("run_id") == run_id)
    rows = [row.asDict(recursive=True) if hasattr(row, "asDict") else dict(row) for row in frame.collect()]
    return [validate_pipeline_run(row) for row in rows] if table == "METADATA_PIPELINE_RUN" else rows


def exact_record(rows, **identity):
    """Reject missing or duplicated exact metadata identities."""
    matches = [row for row in rows if all(row.get(key) == value for key, value in identity.items())]
    if len(matches) != 1:
        raise ValueError("Required exact metadata identity is missing or duplicated: " + ", ".join(identity))
    return matches[0]


def agreement_definition(row):
    """Exclude mutable audit fields from frozen Agreement content."""
    return {key: value.isoformat() if isinstance(value, date) else value for key, value in row.items() if not key.startswith("_")}


def validate_agreement(row):
    """Preserve exact currently effective Agreement safeguards."""
    start, end = (date.fromisoformat(str(row[key])[:10]) for key in ("start_date", "expiry_date"))
    if not start <= date.today() <= end:
        raise ValueError("The exact Data Agreement version is not currently effective.")


def registry_record_id(kind, workspace_id, identity):
    """Build an unambiguous deterministic composite business key."""
    return kind + ":" + manifest_digest([workspace_id, identity])


def empty_pipeline_authority():
    """Return the setup-only control record; runtime never seeds missing authority."""
    return {"record_id": "central", "record_type": "control", "schema_version": 2,
        "token": str(uuid4()), "leases_json": "[]"}


def normalized_destination(destination):
    """Compare physical aliases independently of logical Table ID and case."""
    if not isinstance(destination, dict) or set(destination) != {"workspace_id", "item_id", "kind", "schema", "table_name"}:
        raise ValueError("A complete exact physical destination is required.")
    if any(not isinstance(destination.get(key), str) or not destination[key].strip()
           for key in ("workspace_id", "item_id", "kind", "table_name")):
        raise ValueError("Physical destination identifiers must be nonblank strings.")
    if destination["kind"] not in {"lakehouse", "warehouse"} or destination["schema"] is not None and not isinstance(destination["schema"], str):
        raise ValueError("Unsupported physical destination.")
    return tuple(str(destination.get(key) or "").strip().casefold()
        for key in ("workspace_id", "item_id", "kind", "schema", "table_name"))


def activation_operations(value):
    """Validate the supported operation manifest, without inventing write scopes."""
    operations = parse_metadata_json(value, field="operations_json")
    if not isinstance(operations, list) or not operations:
        raise ValueError("Pipeline activation requires nonempty operation configuration.")
    keys, roles = set(), set()
    for operation in operations:
        if not isinstance(operation, dict) or set(operation) != set(OPERATION_FIELDS):
            raise ValueError("Unexpected or incomplete activated operation fields; write scopes are not supported.")
        key = operation["operation_key"]
        role, table_id = operation["pipeline_role"], operation["table_id"]
        if role not in {"source", "target"} or not isinstance(table_id, str) or not table_id or not isinstance(key, str) or not key.startswith(role + ":"):
            raise ValueError("Invalid activated table, role or operation key.")
        if key in keys or (table_id, role) in roles:
            raise ValueError("Duplicate activated operation membership.")
        keys.add(key)
        roles.add((table_id, role))
        normalized_destination(operation["destination"])
        read, write = operation["read_mode"], operation["write_mode"]
        if (role == "source" and (read not in {"full", "incremental"} or write is not None)
                or role == "target" and (write not in {"append_all", "append_new_only", "overwrite", "scd1", "scd2"} or read is not None)):
            raise ValueError("Unsupported activated read/write strategy.")
        sources = operation["source_table_ids"]
        if not isinstance(sources, list) or any(not isinstance(item, str) or not item for item in sources) or len(sources) != len(set(sources)):
            raise ValueError("Invalid activated source associations.")
        query = operation["query_sha256"]
        if query is not None and (not isinstance(query, str) or len(query) != 64 or any(ch not in "0123456789abcdef" for ch in query)):
            raise ValueError("Invalid activated query SHA256.")
    source_ids = {op["table_id"] for op in operations if op["pipeline_role"] == "source"}
    if any(set(op["source_table_ids"]) - source_ids for op in operations):
        raise ValueError("Activated write references a source outside its pipeline.")
    return operations


def registry_control(rows):
    """Require exactly one valid control row and unique deterministic business keys."""
    ids, business = set(), set()
    schema_fields = set(metadata_table_schema_registry()[REGISTRY_TABLE].fieldNames())
    for row in rows:
        if set(row) - schema_fields or row.get("schema_version") != 2:
            raise ValueError("Unsupported Registry schema; run setup migration first.")
        record_id, kind = row.get("record_id"), row.get("record_type")
        if not record_id or record_id in ids:
            raise ValueError("Missing or duplicate Registry record ID.")
        ids.add(record_id)
        common = {"record_id", "record_type", "schema_version"} | {key for key in row if key.startswith("_")}
        control_fields = {"token", "leases_json", "last_governance_change_id", "last_governance_audit_uri",
                          "migration_archive_uri", "migration_archive_sha256"}
        decision_fields = {"workspace_id", "activation_id", "status", "activated_at", "activated_by"}
        pipeline_fields = {"pipeline_id", "pipeline_name", "notebook_id", "git_repository", "git_commit_sha", "deployment_id",
                           "deployment_manifest_uri", "deployment_manifest_sha256", "verification_method", "operations_json",
                           "agreement_id", "agreement_version", "agreement_sha256"}
        contract_fields = {"table_id", "contract_id", "contract_version", "payload_sha256", "destination_json"}
        allowed = common | (control_fields if kind == "control" else decision_fields | (
            pipeline_fields if kind == "pipeline_activation" else contract_fields))
        if any(value is not None for key, value in row.items() if key not in allowed):
            raise ValueError("Registry fields do not belong to this record type.")
        if kind == "control":
            if record_id != "central" or not row.get("token"):
                raise ValueError("Invalid Registry control identity/token.")
            continue
        if kind not in {"pipeline_activation", "table_contract_activation"}:
            raise ValueError("Unknown Registry record type.")
        workspace = row.get("workspace_id")
        identity = row.get("pipeline_id") if kind == "pipeline_activation" else row.get("table_id")
        if not isinstance(workspace, str) or not workspace or not isinstance(identity, str) or not identity:
            raise ValueError("Activation requires workspace and logical identity.")
        if kind == "pipeline_activation":
            if validate_pipeline_id(identity) != identity:
                raise ValueError("Pipeline activation IDs must use canonical lowercase UUID spelling.")
            activation_operations(row.get("operations_json"))
        elif not row.get("contract_id") or type(row.get("contract_version")) is not int or row["contract_version"] < 1 or not row.get("payload_sha256"):
            raise ValueError("Incomplete exact Contract activation reference.")
        if kind == "table_contract_activation":
            normalized_destination(parse_metadata_json(row.get("destination_json"), field="destination_json"))
        key = (kind, workspace, identity)
        if key in business or record_id != registry_record_id(*key):
            raise ValueError("Ambiguous activation identity.")
        business.add(key)
        if row.get("status") not in {"active", "requires_reactivation"}:
            raise ValueError("Unsupported activation status.")
        if row["status"] == "active" and any(not row.get(field) for field in ("activation_id", "activated_at", "activated_by")):
            raise ValueError("Active records require exact decision provenance.")
        if row["status"] == "requires_reactivation" and any(row.get(field) is not None for field in ("activation_id", "activated_at", "activated_by")):
            raise ValueError("Migration candidates cannot assert activation provenance.")
    control = exact_record(rows, record_type="control", record_id="central")
    leases = parse_metadata_json(control.get("leases_json"), field="leases_json")
    if not isinstance(leases, list):
        raise ValueError("Registry leases must be an array.")
    lease_ids = set()
    for lease in leases:
        required = {"lease_id", "kind", "run_id", "pipeline_id", "workspace_id", "table_id", "destination"}
        if not isinstance(lease, dict) or set(lease) != required or lease["kind"] != "ungoverned_publication":
            raise ValueError("Unsupported or incomplete Registry lease; reconcile before use.")
        if any(not isinstance(lease[key], str) or not lease[key] for key in required - {"destination"}):
            raise ValueError("Invalid Registry lease identity.")
        if lease["lease_id"] in lease_ids:
            raise ValueError("Duplicate Registry lease.")
        lease_ids.add(lease["lease_id"])
        validate_pipeline_id(lease["pipeline_id"])
        normalized_destination(lease["destination"])
    return control


def read_registry(*, context, spark_session=None):
    """Return a validated current Registry snapshot; never recover authority implicitly."""
    rows = metadata_records(REGISTRY_TABLE, context=context, spark_session=spark_session)
    registry_control(rows)
    return rows


def registry_path(*, context):
    """Resolve the single central Metadata Registry path."""
    config, workspace, runtime = resolve_fabric_context(context=context)
    routed = {**runtime, "config": config, "scope_workspace_id": str(runtime.get("metadata_workspace_id") or workspace)}
    return resolve_configured_lakehouse_table("Metadata", REGISTRY_TABLE,
        metadata_table_physical_schema(config, REGISTRY_TABLE), context=routed)[3]


def write_governance_archive(payload, *, path, spark_session, archive_uri=None):
    """Create an immutable checksummed audit file outside the canonical SQL tables."""
    body = canonical_pipeline_json(pipeline_record_content(payload))
    digest = hashlib.sha256(body.encode("utf-8")).hexdigest()
    root = path.split("/Tables/", 1)[0] + "/Files/fabricops/governance" if "/Tables/" in path else path + "_governance_audit"
    uri = archive_uri or root + "/" + str(uuid4()) + ".json"
    jvm = spark_session._jvm
    file = jvm.org.apache.hadoop.fs.Path(uri)
    fs = file.getFileSystem(spark_session._jsc.hadoopConfiguration())
    fs.mkdirs(file.getParent())
    if not fs.exists(file):
        stream = fs.create(file, False)
        try:
            stream.write(bytearray(body.encode("utf-8")))
        finally:
            stream.close()
    # Read back actual bytes; a failed archive must not authorize a commit.
    reader = jvm.java.io.ByteArrayOutputStream()
    source = fs.open(file)
    try:
        jvm.org.apache.hadoop.io.IOUtils.copyBytes(source, reader, spark_session._jsc.hadoopConfiguration(), False)
        actual = bytes((int(v) & 255 for v in reader.toByteArray()))
    finally:
        source.close()
        reader.close()
    if hashlib.sha256(actual).hexdigest() != digest:
        raise RuntimeError("Governance archive readback failed.")
    return uri, digest



def read_governance_archive(uri, *, spark_session):
    """Read exact durable archive/receipt bytes through the configured Hadoop filesystem."""
    jvm = spark_session._jvm
    file = jvm.org.apache.hadoop.fs.Path(uri)
    fs = file.getFileSystem(spark_session._jsc.hadoopConfiguration())
    if not fs.exists(file):
        return None
    reader = jvm.java.io.ByteArrayOutputStream()
    source = fs.open(file)
    try:
        jvm.org.apache.hadoop.io.IOUtils.copyBytes(source, reader, spark_session._jsc.hadoopConfiguration(), False)
        return bytes((int(value) & 255 for value in reader.toByteArray()))
    finally:
        source.close()
        reader.close()


def registry_business_digest(rows):
    """Hash the complete canonical business rows, including explicit physical nulls."""
    fields = metadata_table_schema_registry()[REGISTRY_TABLE].fieldNames()
    business = [coerce_metadata_row_types(REGISTRY_TABLE, {name: row.get(name) for name in fields})
        for row in rows if row["record_type"] != "control"]
    return manifest_digest(sorted(business, key=lambda row: row["record_id"]))


def ensure_registry_audit_receipts(rows, *, path, spark_session):
    """Retain commit proof outside Delta log retention; recover only from exact history.

    A failed post-commit receipt write never rolls back authority or permits replay.
    The next setup/mutation repairs it from the recorded committed version before
    advancing the audit root. Missing history or conflicting receipts fail closed.
    """
    control = registry_control(rows)
    references = [
        ("migration", control.get("migration_archive_uri"), None),
        ("governance", control.get("last_governance_audit_uri"), control.get("last_governance_change_id")),
    ]
    for kind, uri, change_id in references:
        if not uri:
            if change_id:
                raise ValueError("Governance audit identity has no archive.")
            continue
        raw = read_governance_archive(uri, spark_session=spark_session)
        if raw is None:
            raise RuntimeError("Referenced governance archive is missing; restore exact retained audit.")
        digest = hashlib.sha256(raw).hexdigest()
        archive = parse_metadata_json(raw.decode("utf-8"), field="governance archive")
        if kind == "migration":
            if archive.get("format") != "fabricops-registry-cutover-v2" or digest != control.get("migration_archive_sha256"):
                raise ValueError("Migration archive content changed.")
        elif archive.get("change_id") != change_id or registry_business_digest(archive["after"]) != registry_business_digest(rows):
            raise ValueError("Committed governance audit does not match current activations.")
        receipt_uri = uri + ".committed.json"
        recorded = read_governance_archive(receipt_uri, spark_session=spark_session)
        if recorded is not None:
            receipt = parse_metadata_json(recorded.decode("utf-8"), field="governance receipt")
            if (receipt.get("kind") != kind or receipt.get("archive_uri") != uri
                    or receipt.get("archive_sha256") != digest or receipt.get("change_id") != change_id
                    or type(receipt.get("committed_version")) is not int
                    or kind == "governance" and receipt.get("business_sha256") != registry_business_digest(rows)):
                raise ValueError("Conflicting committed governance receipt.")
            continue
        from delta.tables import DeltaTable
        matches = []
        for row in DeltaTable.forPath(spark_session, path).history().select("version", "userMetadata").collect():
            try:
                marker = json.loads(row.userMetadata or "")
            except (ValueError, TypeError):
                continue
            if isinstance(marker, dict) and (kind == "migration" and marker.get("migration_archive_uri") == uri
                    and marker.get("fabricops_registry_migration") == 2 or kind == "governance"
                    and marker.get("governance_audit_uri") == uri and marker.get("fabricops_registry_change") == change_id):
                matches.append(row.version)
        if len(matches) != 1:
            raise RuntimeError("Cannot establish exact governance commit receipt; retain/restore history and inspect before mutation.")
        version = matches[0]
        history = DeltaTable.forPath(spark_session, path).history().where("version = " + str(version)).select("userMetadata").first()
        marker = json.loads(history.userMetadata)
        recorded_digest = marker.get("migration_archive_sha256" if kind == "migration" else "governance_audit_sha256")
        if recorded_digest != digest:
            raise ValueError("Governance archive checksum differs from the committed transaction.")
        committed = [row.asDict(recursive=True) for row in spark_session.read.format("delta").option(
            "versionAsOf", version).load(path).collect()]
        actual = registry_control(committed)
        if (kind == "migration" and actual.get("migration_archive_uri") != uri or
                kind == "governance" and (actual.get("last_governance_change_id") != change_id or
                    registry_business_digest(committed) != registry_business_digest(rows))):
            raise ValueError("Governance commit state differs from its retained audit reference.")
        receipt = {"kind": kind, "archive_uri": uri, "archive_sha256": digest, "change_id": change_id,
            "committed_version": int(version), "business_sha256": registry_business_digest(committed)}
        write_governance_archive(receipt, path=path, spark_session=spark_session, archive_uri=receipt_uri)

def replace_registry_transaction(txn, source_files, rows, *, spark_session, path, recovery, schema_change=False):
    """Stage and commit all Registry files in a pinned whole-table Delta transaction."""
    from pyspark.sql.types import StructType
    from py4j.protocol import Py4JError
    spark, jvm = spark_session, spark_session._jvm
    delta = jvm.org.apache.spark.sql.delta
    schema = metadata_table_schema_registry()[REGISTRY_TABLE]
    frame = spark.createDataFrame([coerce_metadata_row_types(REGISTRY_TABLE, row) for row in rows], schema)
    stage = path + "_activation_staging/" + str(uuid4())
    stage_path = jvm.org.apache.hadoop.fs.Path(stage)
    fs = stage_path.getFileSystem(spark._jsc.hadoopConfiguration())
    try:
        frame.write.mode("errorifexists").parquet(stage)
        replacement = spark.read.schema(schema).parquet(stage)
        if schema_change:
            metadata = json.loads(txn.metadata().json())
            # Reuse existing top-level column mapping identities; Delta allocates
            # identities for the new fields when updateMetadata validates them.
            old_schema = StructType.fromJson(json.loads(metadata["metaData"]["schemaString"]))
            old = {field.name: field for field in old_schema.fields}
            metadata["metaData"]["schemaString"] = StructType([
                old[field.name] if field.name in old and old[field.name].dataType == field.dataType else field
                for field in schema.fields]).json()
            metadata["metaData"]["configuration"]["delta.isolationLevel"] = "Serializable"
            txn.updateMetadata(delta.actions.Action.fromJson(json.dumps(metadata)), False)
        added = txn.writeFiles(replacement._jdf)
        actions = jvm.java.util.ArrayList()
        for index in range(source_files.size()):
            actions.add(source_files.apply(index).remove())
        for index in range(added.size()):
            actions.add(added.apply(index))
        seq = jvm.scala.collection.JavaConverters.asScalaBufferConverter(actions).asScala().toSeq()
        option = jvm.scala.Option
        args = (jvm.org.apache.spark.sql.SaveMode.Overwrite, option.empty(), option.empty(),
                option.apply(canonical_pipeline_json(recovery)))
        try:
            operation = delta.DeltaOperations.Write(*args, option.empty(), option.empty(), option.empty())
        except Py4JError as exc:
            if "Constructor org.apache.spark.sql.delta.DeltaOperations$Write" not in str(exc) or "does not exist" not in str(exc):
                raise
            operation = delta.DeltaOperations.Write(*args)
        try:
            version = int(txn.commit(seq, operation))
        except Exception:
            from delta.tables import DeltaTable
            commits = [row.asDict() for row in DeltaTable.forPath(spark, path).history().select("version", "userMetadata").collect()]
            matching = [row["version"] for row in commits if row["userMetadata"] == canonical_pipeline_json(recovery)]
            if len(matching) != 1:
                raise
            version = matching[0]
        committed = spark.read.format("delta").option("versionAsOf", version).load(path)
        if committed.schema.simpleString() != replacement.schema.simpleString():
            raise RuntimeError("Registry committed but schema readback failed; inspect history.")
        actual = [row.asDict(recursive=True) for row in committed.collect()]
        wanted = [row.asDict(recursive=True) for row in replacement.collect()]
        if sorted(canonical_pipeline_json(pipeline_record_content(row)) for row in actual) != sorted(
                canonical_pipeline_json(pipeline_record_content(row)) for row in wanted):
            raise RuntimeError("Registry committed but exact readback failed; inspect history.")
        registry_control(actual)
        return version
    finally:
        fs.delete(stage_path, True)


def commit_registry(rows, *, expected_token, context, spark_session=None, governance_change=False):
    """CAS the complete Registry under Serializable isolation, archiving governance changes.

    The transaction tracks a whole-table read so blind inserts and phantom records
    conflict. A stale human review is never silently replayed. Lost acknowledgements
    are resolved by a unique transaction marker and exact versioned readback.
    """
    from copy import deepcopy
    spark = get_spark_session(spark_session, context=context)
    path = registry_path(context=context)
    log = spark._jvm.org.apache.spark.sql.delta.DeltaLog.forTable(spark._jsparkSession, path)
    txn = log.startTransaction()
    txn.readWholeTable()
    files = txn.filterFiles()
    if json.loads(txn.metadata().json())["metaData"]["configuration"].get("delta.isolationLevel") != "Serializable":
        raise ValueError("Registry requires Serializable isolation; run setup before mutation.")
    previous = [row.asDict(recursive=True) for row in spark.read.format("delta").option("versionAsOf", int(txn.readVersion())).load(path).collect()]
    old = registry_control(previous)
    proposed = deepcopy(rows)
    control = registry_control(proposed)
    if old["token"] != expected_token or control["token"] != expected_token:
        raise ValueError("Stale Pipeline Registry; refresh and review again.")
    if not governance_change and any(control.get(key) != old.get(key) for key in ("last_governance_change_id", "last_governance_audit_uri")):
        raise ValueError("Lease mutations cannot rewrite governance audit references.")
    if any(control.get(key) != old.get(key) for key in ("migration_archive_uri", "migration_archive_sha256")):
        raise ValueError("Migration archive references are immutable.")
    ensure_registry_audit_receipts(previous, path=path, spark_session=spark)
    old_business = [row for row in previous if row["record_type"] != "control"]
    new_business = [row for row in proposed if row["record_type"] != "control"]
    if pipeline_record_content(sorted(old_business, key=lambda row: row["record_id"])) != pipeline_record_content(sorted(new_business, key=lambda row: row["record_id"])) and not governance_change:
        raise ValueError("Activation changes require a governance audit transaction.")
    leases = parse_metadata_json(old["leases_json"], field="leases_json")
    changed = {row["record_id"] for row in old_business + new_business
        if next((r for r in old_business if r["record_id"] == row["record_id"]), None) !=
           next((r for r in new_business if r["record_id"] == row["record_id"]), None)}
    for row in old_business + new_business:
        if row["record_id"] in changed and any(lease["workspace_id"] == row["workspace_id"] and (
                lease["pipeline_id"] == row.get("pipeline_id") or lease["table_id"] == row.get("table_id")) for lease in leases):
            raise ValueError("Drain affected executions before changing activation.")
    config, workspace, runtime = resolve_fabric_context(context=context)
    audit = build_runtime_audit_fields(config=config, active_workspace_id=str(runtime.get("metadata_workspace_id") or workspace), runtime_context=runtime)
    change_id = str(uuid4())
    audit_digest = None
    if governance_change:
        uri, audit_digest = write_governance_archive({"change_id": change_id, "before": old_business, "after": new_business,
            "actor": audit, "source_token": old["token"], "source_version": int(txn.readVersion()),
            "previous_governance_audit_uri": old.get("last_governance_audit_uri"),
            "previous_governance_change_id": old.get("last_governance_change_id")}, path=path, spark_session=spark)
        control.update(last_governance_change_id=change_id, last_governance_audit_uri=uri)
    control.update(token=str(uuid4()), **audit)
    registry_control(proposed)
    replace_registry_transaction(txn, files, proposed, spark_session=spark, path=path,
        recovery={"fabricops_registry_change": change_id, "token": control["token"],
                  "governance_audit_uri": control.get("last_governance_audit_uri"),
                  "governance_audit_sha256": audit_digest})
    ensure_registry_audit_receipts(proposed, path=path, spark_session=spark)
    return control["token"]


def resolve_activation_contract(activation, *, context, spark_session=None):
    """Resolve a separately frozen exact Contract; never copy its payload into Registry."""
    row = exact_record(metadata_records("METADATA_DATA_CONTRACT", context=context, spark_session=spark_session),
        contract_id=activation["contract_id"], contract_version=activation["contract_version"])
    if (row["table_id"] != activation["table_id"] or row["status"] != "frozen" or
            hashlib.sha256(row["contract_payload_json"].encode("utf-8")).hexdigest() != activation["payload_sha256"]):
        raise ValueError("Activated frozen Data Contract changed or does not match its Table ID.")
    return {**row, "contract_payload": parse_metadata_json(row["contract_payload_json"], field="contract_payload_json")}


def review_pipeline_activation(candidate, *, context, spark_session=None):
    """Validate direct operation/Contract/Agreement pointers; deployment assurance stays blocked."""
    _, workspace, _ = resolve_fabric_context(context=context)
    if candidate.get("workspace_id") != workspace:
        raise ValueError("Pipeline activation must target the selected execution workspace.")
    validate_pipeline_id(candidate.get("pipeline_id"))
    operations = activation_operations(candidate.get("operations_json"))
    rows = read_registry(context=context, spark_session=spark_session)
    agreement = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=context, spark_session=spark_session),
        agreement_id=candidate.get("agreement_id"), agreement_version=candidate.get("agreement_version"))
    validate_agreement(agreement)
    if manifest_digest(agreement_definition(agreement)) != candidate.get("agreement_sha256"):
        raise ValueError("Exact Data Agreement changed.")
    destinations, writers = {}, {}
    for row in rows:
        if row["record_type"] == "pipeline_activation" and row["status"] == "active" and row["record_id"] != candidate.get("record_id"):
            for op in activation_operations(row["operations_json"]):
                if op["pipeline_role"] == "target":
                    writers[normalized_destination(op["destination"])] = row["pipeline_id"]
    for op in operations:
        active = exact_record(rows, record_type="table_contract_activation", workspace_id=workspace, table_id=op["table_id"])
        if active["status"] != "active":
            raise ValueError("Every pipeline participant requires an independently activated Data Contract.")
        contract = resolve_activation_contract(active, context=context, spark_session=spark_session)
        destination = normalized_destination(op["destination"])
        previous = destinations.setdefault(destination, op["table_id"])
        if previous != op["table_id"]:
            raise ValueError("Physical destination aliases require reconciliation.")
        if op["pipeline_role"] == "target":
            processing = contract["contract_payload"].get("table", {}).get("processing", {})
            if processing.get("load_strategy") != op["write_mode"]:
                raise ValueError("Activated write strategy differs from frozen Contract.")
            if destination in writers:
                raise ValueError("Multiple governed writers remain blocked until writer-scoped publication is implemented.")
    return {"ready": False, "blocking_conflicts": [DEPLOYMENT_PENDING],
        "token": registry_control(rows)["token"], "operations": operations}


def build_governed_pipeline_plan(*, pipeline_id, context=None, spark_session=None):
    """Fail before admission, Run persistence or publication while deployment assurance is pending."""
    validate_pipeline_id(pipeline_id)
    raise RuntimeError(DEPLOYMENT_PENDING)


def verify_governed_plan(plan, *, spark_session=None):
    """Reject forged or retained Governed/Live plans before controlled execution."""
    raise RuntimeError(DEPLOYMENT_PENDING)


def guard_ungoverned_write(plan, table_id, destination, *, spark_session=None):
    """Pin an unprotected target for the run, excluding racing Contract activation.

    The Serializable Registry control token excludes concurrent managed writers
    to this physical target. A crashed run requires explicit reconciliation.
    """
    rows = read_registry(context=plan.runtime_context, spark_session=spark_session)
    control = registry_control(rows)
    physical = normalized_destination(destination)
    for row in rows:
        # Candidates preserve protection of former governed targets during cutover.
        if row["record_type"] == "table_contract_activation" and row["workspace_id"] == plan.workspace_id and row["table_id"] == table_id:
            raise ValueError("Ungoverned cannot write a protected Table ID; use Governed after verified reactivation.")
        if row["record_type"] == "pipeline_activation":
            if any((row["workspace_id"] == plan.workspace_id and op["table_id"] == table_id or
                    normalized_destination(op["destination"]) == physical) for op in activation_operations(row["operations_json"])):
                raise ValueError("Ungoverned cannot write a governed physical destination or alias.")
    # Independent Contract activation protects physical aliases as well as IDs.
    for row in rows:
        if row["record_type"] == "table_contract_activation":
            binding = parse_metadata_json(row["destination_json"], field="destination_json")
            if normalized_destination(binding) == physical:
                raise ValueError("Ungoverned cannot write a protected physical destination alias.")
    leases = parse_metadata_json(control["leases_json"], field="leases_json")
    lease_id = manifest_digest([plan.plan_id, table_id, destination])
    if any(lease["lease_id"] == lease_id for lease in leases):
        plan.evidence["lease_token"] = plan.plan_id
        return
    # The existing Serializable Registry control CAS provides a distributed
    # publication mutex, including physical aliases and writers in other workspaces.
    if any(normalized_destination(lease["destination"]) == physical for lease in leases):
        raise RuntimeError("Another pipeline holds this target's publication lease. Finalize that run "
                           "or reconcile its interrupted publication before retrying.")
    leases.append({"lease_id": lease_id, "kind": "ungoverned_publication", "run_id": plan.plan_id,
        "pipeline_id": plan.pipeline_id, "workspace_id": plan.workspace_id, "table_id": table_id, "destination": destination})
    control["leases_json"] = canonical_pipeline_json(leases)
    commit_registry(rows, expected_token=control["token"], context=plan.runtime_context, spark_session=spark_session)
    plan.evidence["lease_token"] = plan.plan_id


def release_pipeline_lease(plan, *, spark_session=None):
    """Release only the completed caller's policy leases; never expire a crashed run."""
    if not plan.evidence.get("sealed"):
        raise ValueError("Finalize the execution before releasing its policy leases.")
    rows = read_registry(context=plan.runtime_context, spark_session=spark_session)
    control = registry_control(rows)
    leases = parse_metadata_json(control["leases_json"], field="leases_json")
    own = [lease for lease in leases if lease["run_id"] == plan.plan_id]
    if any(lease["pipeline_id"] != plan.pipeline_id or lease["workspace_id"] != plan.workspace_id for lease in own):
        raise ValueError("Policy lease belongs to another execution.")
    if own:
        control["leases_json"] = canonical_pipeline_json([lease for lease in leases if lease["run_id"] != plan.plan_id])
        commit_registry(rows, expected_token=control["token"], context=plan.runtime_context, spark_session=spark_session)
    plan.evidence.pop("lease_token", None)


def resolve_active_consumer_contract(config, active_workspace_id, table_id, *, spark_session=None):
    """Resolve an independent Contract with unambiguous effective Agreement context."""
    context = {"config": config, "scope_workspace_id": active_workspace_id}
    rows = read_registry(context=context, spark_session=spark_session)
    activation = exact_record(rows, record_type="table_contract_activation", workspace_id=active_workspace_id, table_id=table_id)
    if activation["status"] != "active":
        raise ValueError("Consumer table has no active Data Contract.")
    contract = resolve_activation_contract(activation, context=context, spark_session=spark_session)
    agreements = {(row["agreement_id"], row["agreement_version"], row["agreement_sha256"]) for row in rows
        if row["record_type"] == "pipeline_activation" and row["status"] == "active" and row["workspace_id"] == active_workspace_id
        and any(op["table_id"] == table_id for op in activation_operations(row["operations_json"]))}
    if len(agreements) != 1:
        raise ValueError("No unambiguous active pipeline Agreement covers this consumer table; Contract activation alone grants no consumer permission.")
    agreement_id, version, digest = next(iter(agreements))
    agreement = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=context, spark_session=spark_session),
        agreement_id=agreement_id, agreement_version=version)
    validate_agreement(agreement)
    if manifest_digest(agreement_definition(agreement)) != digest:
        raise ValueError("Consumer Agreement changed.")
    return {**contract, "agreement_id": agreement_id, "agreement_version": version}


def set_table_contract_activation(table_id, contract_id, contract_version, *, expected_token, governance_confirmed,
                                  context, spark_session=None):
    """Activate an exact frozen Contract independently, draining affected policy leases."""
    if governance_confirmed is not True:
        raise ValueError("Explicit Governance confirmation is required.")
    config, workspace, runtime = resolve_fabric_context(context=context)
    rows = read_registry(context=context, spark_session=spark_session)
    control = registry_control(rows)
    if expected_token != control["token"]:
        raise ValueError("Stale Pipeline Registry; refresh and review again.")
    contract = exact_record(metadata_records("METADATA_DATA_CONTRACT", context=context, spark_session=spark_session),
        contract_id=contract_id, contract_version=contract_version)
    if contract["status"] != "frozen" or contract["table_id"] != table_id or type(contract_version) is not int:
        raise ValueError("Activation requires the exact frozen Contract for this Table ID.")
    from fabricops_kit.pipeline.shared import resolve_catalogue_table_identity, pipeline_physical_bindings
    from fabricops_kit.pipeline.shared import validated_processing
    payload = parse_metadata_json(contract["contract_payload_json"], field="contract_payload_json")
    if payload.get("table", {}).get("table_id") != table_id:
        raise ValueError("Frozen payload Table ID does not match.")
    processing = validated_processing(payload["table"].get("processing") or {})
    identity = resolve_catalogue_table_identity(config, workspace, table_id,
        context={**runtime, "scope_workspace_id": runtime.get("metadata_workspace_id") or workspace}, spark_session=spark_session)
    destination = pipeline_physical_bindings({table_id: identity}, config=config, workspace_id=workspace)[table_id]
    leases = parse_metadata_json(control["leases_json"], field="leases_json")
    if any((lease["workspace_id"] == workspace and lease["table_id"] == table_id) or
           normalized_destination(lease["destination"]) == normalized_destination(destination) for lease in leases):
        raise ValueError("Drain affected executions before Contract activation.")
    for row in rows:
        if (row["record_type"] == "table_contract_activation"
                and (row["workspace_id"], row["table_id"]) != (workspace, table_id)):
            binding = parse_metadata_json(row["destination_json"], field="destination_json")
            if normalized_destination(binding) == normalized_destination(destination):
                raise ValueError("Conflicting activation Table IDs or environments alias one physical destination.")
    # Validate all affected active descriptors; never silently change their strategy.
    for row in rows:
        if row["record_type"] == "pipeline_activation" and row["status"] == "active" and row["workspace_id"] == workspace:
            for op in activation_operations(row["operations_json"]):
                if op["table_id"] == table_id and (
                        normalized_destination(op["destination"]) != normalized_destination(destination) or
                        op["pipeline_role"] == "target" and op["write_mode"] != processing["load_strategy"]):
                    raise ValueError("Contract activation conflicts with an active pipeline; coordinate replacement.")
    record_id = registry_record_id("table_contract_activation", workspace, table_id)
    audit = build_runtime_audit_fields(config=config, active_workspace_id=str(runtime.get("metadata_workspace_id") or workspace), runtime_context=runtime)
    record = {"record_id": record_id, "record_type": "table_contract_activation", "schema_version": 2,
        "workspace_id": workspace, "table_id": table_id, "activation_id": str(uuid4()), "status": "active",
        "activated_at": datetime.now(UTC).replace(tzinfo=None), "activated_by": audit["_committed_by"],
        "contract_id": contract_id, "contract_version": contract_version,
        "payload_sha256": hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest(),
        "destination_json": canonical_pipeline_json(destination), **audit}
    resulting = [row for row in rows if row["record_id"] != record_id] + [record]
    commit_registry(resulting, expected_token=expected_token, context=context, spark_session=spark_session, governance_change=True)
    return record
