"""Notebook promotion authority, exact Contracts and retained publication coordination.

Canonical Registry rows contain only immutable pipeline versions. Publication
claims retain the existing Serializable whole-table protocol in Metadata Files,
never in the Registry. They do not expire after a crashed writer.
"""
from __future__ import annotations

import hashlib
import json
from copy import deepcopy
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
ACTIVATION_TABLE = "METADATA_DATA_CONTRACT_ACTIVATION"
FABRIC_VALIDATION_PENDING = "Governed execution is unavailable: signed-in Fabric notebook identity, permissions, scheduling and concurrent publication validation are pending."
# Release gate, not a caller-configurable bypass. See the integration checklist.
FABRIC_GOVERNED_VALIDATED = False
OPERATION_FIELDS = (
    "operation_key", "table_id", "pipeline_role", "destination", "read_mode", "write_mode",
    "query_sha256", "incremental_target_table_id", "source_table_ids", "requested_schema",
)
RUN_PROVENANCE_FIELDS = (
    "execution_workspace_id", "pipeline_version", "promotion_id", "governed_notebook_id", "execution_identity", "run_schema_version",
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
    operations = deepcopy(value) if isinstance(value, list) else parse_metadata_json(value, field="operations_json")
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
        requested_schema = operation["requested_schema"]
        if requested_schema is not None and (not isinstance(requested_schema, str) or not requested_schema.strip()):
            raise ValueError("An operation schema must be an explicit nonblank name or None for its configured default.")
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

def resolve_activation_contract(activation, *, context, spark_session=None):
    """Resolve a separately frozen exact Contract; never copy its payload into Registry."""
    row = exact_record(metadata_records("METADATA_DATA_CONTRACT", context=context, spark_session=spark_session),
        contract_id=activation["contract_id"], contract_version=activation["contract_version"])
    if (row["table_id"] != activation["table_id"] or row["status"] != "frozen" or
            hashlib.sha256(row["contract_payload_json"].encode("utf-8")).hexdigest() != activation["payload_sha256"]):
        raise ValueError("Activated frozen Data Contract changed or does not match its Table ID.")
    return {**row, "contract_payload": parse_metadata_json(row["contract_payload_json"], field="contract_payload_json")}


def metadata_path(table, *, context):
    """Resolve canonical metadata independently of the execution workspace."""
    config, workspace, runtime = resolve_fabric_context(context=context)
    routed = {**runtime, "config": config, "scope_workspace_id": str(runtime.get("metadata_workspace_id") or workspace)}
    return resolve_configured_lakehouse_table("Metadata", table,
        metadata_table_physical_schema(config, table), context=routed)[3]


def validate_registry(rows):
    """Reject duplicate identities, active versions and incomplete frozen provenance."""
    identities, active, promotions, notebooks = set(), set(), set(), set()
    for row in rows:
        required = ("execution_workspace_id", "pipeline_id", "pipeline_version", "promotion_id", "status",
            "source_workspace_id", "source_notebook_id", "governed_notebook_id", "snapshot_uri", "snapshot_sha256",
            "source_snapshot_uri", "source_snapshot_sha256", "executable_sha256", "operations_json",
            "bindings_sha256", "parameters_json", "approval_id", "submission_id", "submission_sha256", "promoted_by", "promoted_at")
        if any(row.get(key) in (None, "") for key in required) or "record_type" in row:
            raise ValueError("Incompatible Pipeline Promotion Registry: complete immutable version and snapshot fields are required. Existing metadata is preserved.")
        validate_pipeline_id(row["pipeline_id"])
        if type(row["pipeline_version"]) is not int or row["pipeline_version"] < 1:
            raise ValueError("Pipeline version must be a positive integer.")
        key = row["execution_workspace_id"], row["pipeline_id"], row["pipeline_version"]
        notebook = row["execution_workspace_id"], row["governed_notebook_id"]
        if key in identities or row["promotion_id"] in promotions or notebook in notebooks:
            raise ValueError("Duplicate immutable Pipeline Promotion identity.")
        identities.add(key); promotions.add(row["promotion_id"]); notebooks.add(notebook)
        if row["status"] not in {"active", "superseded", "retired"}:
            raise ValueError("Unsupported Pipeline Promotion status.")
        if row["status"] == "active":
            if key[:2] in active:
                raise ValueError("Multiple active versions for one workspace/Pipeline ID.")
            active.add(key[:2])
        operations = activation_operations(row["operations_json"])
        if manifest_digest(operations) != row["bindings_sha256"]:
            raise ValueError("Pipeline Promotion operation binding digest changed.")
        parameters = parse_metadata_json(row["parameters_json"], field="parameters_json")
        if not isinstance(parameters, dict):
            raise ValueError("Pipeline parameters must be an exact object.")
        for field in ("snapshot_sha256", "source_snapshot_sha256", "executable_sha256", "bindings_sha256"):
            digest = row[field]
            if not isinstance(digest, str) or len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
                raise ValueError("Invalid Pipeline Promotion digest: " + field)
        if row["source_workspace_id"] == row["execution_workspace_id"] and row["source_notebook_id"] == row["governed_notebook_id"]:
            raise ValueError("Promotion requires a separate Governed notebook.")
    return rows


def validate_activations(rows):
    """Enforce one frozen Contract per physical workspace/Table ID, including aliases."""
    identities, bindings, ids, revisions = set(), set(), set(), set()
    for row in rows:
        identity = row.get("workspace_id"), row.get("table_id")
        destination = parse_metadata_json(row.get("destination_json"), field="destination_json")
        physical = normalized_destination(destination)
        if (not all(identity) or row.get("status") not in {"active", "superseded"} or type(row.get("revision")) is not int
                or row["revision"] < 1 or not row.get("activation_id") or not row.get("contract_id")
                or type(row.get("contract_version")) is not int or row["contract_version"] < 1
                or not row.get("payload_sha256") or not row.get("activated_by") or not row.get("activated_at")):
            raise ValueError("Incomplete active Data Contract identity.")
        if str(destination["workspace_id"]).casefold() != str(identity[0]).casefold():
            raise ValueError("Contract Activation must use the physical table workspace.")
        if (row["activation_id"] in ids or (*identity, row["revision"]) in revisions or
                row["status"] == "active" and (identity in identities or physical in bindings)):
            raise ValueError("Ambiguous Data Contract Activation identity or physical alias.")
        refs = [row.get(key) for key in ("agreement_id", "agreement_version", "agreement_sha256")]
        if any(refs) and not all(refs):
            raise ValueError("Incomplete Governance-owned Agreement–Contract association.")
        if row["status"] == "active":
            identities.add(identity); bindings.add(physical)
        ids.add(row["activation_id"]); revisions.add((*identity, row["revision"]))
    return rows


def read_registry(*, context, spark_session=None):
    """Read only validated per-version Pipeline Promotions; empty setup is valid."""
    return validate_registry(metadata_records(REGISTRY_TABLE, context=context, spark_session=spark_session))


def read_activations(*, context, spark_session=None):
    """Read independent Governance-owned physical Contract activations."""
    return [row for row in read_activation_history(context=context, spark_session=spark_session) if row["status"] == "active"]


def read_activation_history(*, context, spark_session=None):
    """Read immutable activation identities and retained superseded selections."""
    return validate_activations(metadata_records(ACTIVATION_TABLE, context=context, spark_session=spark_session))


def replace_metadata_transaction(txn, source_files, rows, *, schema, spark_session, path, marker):
    """Commit a pinned whole-table read and exact replacement, including phantom detection.

    Reuse the existing Delta optimistic transaction protocol. Never retry a stale
    human approval. Lost acknowledgements are resolved against a unique commit
    marker and exact versioned readback, never against a mutable latest snapshot.
    """
    from py4j.protocol import Py4JError
    spark, jvm = spark_session, spark_session._jvm
    delta = jvm.org.apache.spark.sql.delta
    frame = spark.createDataFrame(rows, schema)
    actions = jvm.java.util.ArrayList()
    added = txn.writeFiles(frame._jdf)
    for index in range(source_files.size()):
        actions.add(source_files.apply(index).remove())
    for index in range(added.size()):
        actions.add(added.apply(index))
    seq = jvm.scala.collection.JavaConverters.asScalaBufferConverter(actions).asScala().toSeq()
    option = jvm.scala.Option
    args = (jvm.org.apache.spark.sql.SaveMode.Overwrite, option.empty(), option.empty(), option.apply(canonical_pipeline_json(marker)))
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
        matches = [row.version for row in DeltaTable.forPath(spark, path).history().select("version", "userMetadata").collect()
            if row.userMetadata == canonical_pipeline_json(marker)]
        if len(matches) != 1:
            raise
        version = matches[0]
    actual = spark.read.format("delta").option("versionAsOf", version).load(path)
    if actual.schema.simpleString() != frame.schema.simpleString() or sorted(
            canonical_pipeline_json(pipeline_record_content(row.asDict(recursive=True))) for row in actual.collect()) != sorted(
            canonical_pipeline_json(pipeline_record_content(row.asDict(recursive=True))) for row in frame.collect()):
        raise RuntimeError("Metadata transaction committed but exact readback failed; inspect the committed version.")
    return version


def mutate_metadata(table, mutation, *, context, spark_session=None, operation_id=None, path=None, schema=None):
    """Apply a conditional mutation to the exact version tracked by Delta's read set."""
    spark = get_spark_session(spark_session, context=context)
    path = path or metadata_path(table, context=context)
    schema = schema or metadata_table_schema_registry()[table]
    log = spark._jvm.org.apache.spark.sql.delta.DeltaLog.forTable(spark._jsparkSession, path)
    txn = log.startTransaction()
    txn.readWholeTable()
    files = txn.filterFiles()
    if json.loads(txn.metadata().json())["metaData"]["configuration"].get("delta.isolationLevel") != "Serializable":
        raise ValueError("Governance mutations require Serializable Delta isolation; run fresh setup.")
    previous = [row.asDict(recursive=True) for row in spark.read.format("delta").option("versionAsOf", int(txn.readVersion())).load(path).collect()]
    if table == REGISTRY_TABLE:
        validate_registry(previous)
    elif table == ACTIVATION_TABLE:
        validate_activations(previous)
    proposed, result = mutation(deepcopy(previous))
    if table == REGISTRY_TABLE:
        validate_registry(proposed)
    elif table == ACTIVATION_TABLE:
        validate_activations(proposed)
    if proposed == previous:
        return result
    rows = [coerce_metadata_row_types(table, row) for row in proposed] if table else proposed
    replace_metadata_transaction(txn, files, rows, schema=schema, spark_session=spark, path=path,
        marker={"fabricops_operation_id": operation_id or str(uuid4()), "content_sha256": manifest_digest(rows)})
    return result


def publication_claim(owner, destination, *, context, spark_session=None, release=False):
    """Retain the existing exclusive writer protocol outside canonical Registry rows.

    The auxiliary Delta ledger in Metadata Files is runtime coordination, not a
    canonical metadata table. Contract Activation takes the same target claim so
    checking protection and admitting a writer cannot race. Interrupted claims
    never expire; reconcile the physical publication before explicit removal.
    """
    from pyspark.sql.types import StructType, StructField, StringType
    spark = get_spark_session(spark_session, context=context)
    root = metadata_path(REGISTRY_TABLE, context=context).split("/Tables/", 1)[0]
    path = root + "/Files/fabricops/publication_coordination"
    schema = StructType([StructField("target", StringType(), False), StructField("owner", StringType(), False)])
    from delta.tables import DeltaTable
    if not DeltaTable.isDeltaTable(spark, path):
        try:
            spark.createDataFrame([], schema).write.format("delta").mode("errorifexists").option("delta.isolationLevel", "Serializable").save(path)
        except Exception:
            if not DeltaTable.isDeltaTable(spark, path):
                raise
    target = canonical_pipeline_json(normalized_destination(destination))
    def mutate(rows):
        matches = [row for row in rows if row["target"] == target]
        if len(matches) > 1:
            raise RuntimeError("Duplicate publication claims; reconcile before publishing.")
        if matches and matches[0]["owner"] != owner:
            if release:
                return rows, None
            raise RuntimeError("Another operation holds this target's publication lease; finalize or reconcile the interrupted publication.")
        if release:
            return [row for row in rows if row["target"] != target], None
        return rows if matches else rows + [{"target": target, "owner": owner}], None
    return mutate_metadata(None, mutate, context=context, spark_session=spark, path=path, schema=schema)


def guard_ungoverned_write(plan, table_id, destination, *, spark_session=None):
    """Exclude competing publications and active Contract physical aliases."""
    publication_claim(plan.plan_id, destination, context=plan.runtime_context, spark_session=spark_session)
    try:
        rows = read_activations(context=plan.runtime_context, spark_session=spark_session)
        if any((row["workspace_id"].casefold() == destination["workspace_id"].casefold() and row["table_id"] == table_id)
                or normalized_destination(parse_metadata_json(row["destination_json"], field="destination_json")) == normalized_destination(destination)
                for row in rows):
            raise ValueError("Ungoverned cannot write a protected Table ID or physical destination alias.")
    except BaseException:
        publication_claim(plan.plan_id, destination, context=plan.runtime_context, spark_session=spark_session, release=True)
        raise
    plan.evidence.setdefault("publication_claims", []).append(dict(destination))
    plan.evidence["lease_token"] = plan.plan_id


def release_pipeline_lease(plan, *, spark_session=None):
    """Release only this finalized run's claims; never expire crashed writers."""
    if not plan.evidence.get("sealed"):
        raise ValueError("Finalize the execution before releasing its publication leases.")
    claims = plan.evidence.get("publication_claims", [])
    while claims:
        publication_claim(plan.plan_id, claims[0], context=plan.runtime_context, spark_session=spark_session, release=True)
        del claims[0]
    plan.evidence.pop("lease_token", None)
    plan.evidence.pop("publication_claims", None)


def set_table_contract_activation(table_id, contract_id, contract_version, *, expected_activation_id, activation_id,
                                  governance_confirmed, context, spark_session=None,
                                  expected_destination=None, expected_payload_sha256=None,
                                  agreement_id=None, agreement_version=None, expected_agreement_sha256=None):
    """Activate an exact frozen Contract with replay-safe CAS and physical protection."""
    if governance_confirmed is not True:
        raise ValueError("Explicit Governance confirmation is required; actual storage permissions authorize the mutation.")
    if not isinstance(activation_id, str) or not activation_id.strip():
        raise ValueError("A replay-safe activation_id is required.")
    config, workspace, runtime = resolve_fabric_context(context=context)
    contract = exact_record(metadata_records("METADATA_DATA_CONTRACT", context=context, spark_session=spark_session),
        contract_id=contract_id, contract_version=contract_version)
    if contract["status"] != "frozen" or contract["table_id"] != table_id or type(contract_version) is not int or contract_version < 1:
        raise ValueError("Activation requires the exact frozen Contract for this Table ID.")
    from fabricops_kit.pipeline.shared import resolve_catalogue_table_identity, pipeline_physical_bindings, validated_processing
    payload = parse_metadata_json(contract["contract_payload_json"], field="contract_payload_json")
    if payload.get("table", {}).get("table_id") != table_id:
        raise ValueError("Frozen payload Table ID does not match.")
    validated_processing(payload["table"].get("processing") or {})
    identity = resolve_catalogue_table_identity(config, workspace, table_id, context=context, spark_session=spark_session)
    destination = pipeline_physical_bindings({table_id: identity}, config=config, workspace_id=workspace)[table_id]
    if str(destination["workspace_id"]).casefold() != workspace.casefold():
        raise ValueError("Select the physical table workspace for Contract Activation.")
    if expected_destination is not None and normalized_destination(expected_destination) != normalized_destination(destination):
        raise ValueError("Physical Contract binding changed after review; refresh and review again.")
    payload_sha256 = hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest()
    if expected_payload_sha256 is not None and payload_sha256 != expected_payload_sha256:
        raise ValueError("Frozen Contract payload changed after review; activation rejected.")
    audit = build_runtime_audit_fields(config=config, active_workspace_id=workspace, runtime_context=runtime)
    record = dict(workspace_id=workspace, table_id=table_id, contract_id=contract_id, contract_version=contract_version,
        payload_sha256=payload_sha256, activation_id=activation_id,
        status="active", destination_json=canonical_pipeline_json(destination), activated_by=audit["_committed_by"],
        activated_at=datetime.now(UTC).replace(tzinfo=None), **audit)
    record.update(agreement_id=agreement_id, agreement_version=agreement_version, agreement_sha256=None)
    if agreement_id is not None or agreement_version is not None:
        agreement = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=context, spark_session=spark_session),
            agreement_id=agreement_id, agreement_version=agreement_version)
        validate_agreement(agreement)
        record["agreement_sha256"] = manifest_digest(agreement_definition(agreement))
        if record["agreement_sha256"] != expected_agreement_sha256:
            raise ValueError("Agreement changed after Contract review; refresh before activation.")
    check_contract_agreement(record, execution_workspace_id=workspace, context=context, spark_session=spark_session)
    owner = "activation:" + activation_id
    publication_claim(owner, destination, context=context, spark_session=spark_session)
    try:
        def mutate(rows):
            matches = [row for row in rows if (row["workspace_id"], row["table_id"]) == (workspace, table_id) and row["status"] == "active"]
            current = matches[0] if matches else None
            replay = [row for row in rows if row["activation_id"] == activation_id]
            if replay:
                if any(replay[0].get(key) != record[key] for key in ("workspace_id", "table_id", "contract_id", "contract_version", "payload_sha256", "destination_json", "agreement_id", "agreement_version", "agreement_sha256")):
                    raise ValueError("Activation operation ID was reused with different content.")
                return rows, replay[0]
            if (current["activation_id"] if current else None) != expected_activation_id:
                raise ValueError("Stale Contract Activation; refresh and review again.")
            record["revision"] = current["revision"] + 1 if current else 1
            if current:
                current["status"] = "superseded"
            result = rows + [record]
            validate_activations(result)
            return result, record
        return mutate_metadata(ACTIVATION_TABLE, mutate, context=context, spark_session=spark_session, operation_id=activation_id)
    finally:
        publication_claim(owner, destination, context=context, spark_session=spark_session, release=True)


class FabricNotebookClient:
    """Signed-in Fabric notebook definitions with bounded long-running-operation polling."""

    def __init__(self):
        """Use the current Fabric identity; never accept a caller-supplied identity claim."""
        import notebookutils
        self.token = notebookutils.credentials.getToken("https://api.fabric.microsoft.com")
        if not self.token:
            raise RuntimeError("Fabric notebook verifier unavailable: no signed-in identity.")

    def request(self, method, path, body=None):
        """Call the fixed Fabric API, resolving documented operation result resources."""
        import time
        from urllib.request import Request, urlopen
        from urllib.parse import urlparse
        root = "https://api.fabric.microsoft.com/v1"
        def call(method, path, body=None):
            url = path if path.startswith("https://") else root + path
            parsed = urlparse(url)
            if parsed.scheme != "https" or parsed.netloc != "api.fabric.microsoft.com" or not parsed.path.startswith("/v1/"):
                raise RuntimeError("Unexpected Fabric operation URL.")
            request = Request(url, data=json.dumps(body).encode() if body is not None else None, method=method,
                headers={"Authorization": "Bearer " + self.token, "Content-Type": "application/json"})
            with urlopen(request, timeout=30) as response:
                raw = response.read()
                return response.status, dict(response.headers.items()), json.loads(raw) if raw else {}
        status, headers, payload = call(method, path, body)
        if status in {200, 201, 204}:
            return payload
        if status != 202:
            raise RuntimeError("Fabric API returned unexpected status.")
        def header(headers, name):
            return next((value for key, value in headers.items() if key.lower() == name.lower()), None)
        location = header(headers, "Location")
        operation_id = header(headers, "x-ms-operation-id")
        operation = "/operations/" + operation_id if operation_id else location
        if not operation:
            raise RuntimeError("Fabric API accepted without an operation identity; inspect staged artifacts.")
        for _ in range(90):
            delay = float(header(headers, "Retry-After") or 2)
            time.sleep(min(max(delay, 0), 10))
            status, headers, payload = call("GET", operation)
            if status != 200 or not isinstance(payload, dict):
                raise RuntimeError("Fabric operation verifier unavailable.")
            if payload.get("status") in {"Succeeded", "Completed"}:
                _, _, result = call("GET", operation.rstrip("/") + "/result")
                return result
            if payload.get("status") in {"Failed", "Cancelled"}:
                raise RuntimeError("Fabric notebook operation failed; inspect staged artifacts.")
        raise RuntimeError("Fabric notebook operation timed out; inspect staged artifacts before retrying.")

    def definition(self, workspace, notebook):
        """Retrieve the complete saved ipynb definition, rejecting ambiguous parts."""
        import base64
        from uuid import UUID
        workspace, notebook = str(UUID(workspace)), str(UUID(notebook))
        result = self.request("POST", f"/workspaces/{workspace}/notebooks/{notebook}/getDefinition?format=ipynb")
        parts = result.get("definition", {}).get("parts", [])
        notebooks = [part for part in parts if part.get("path") == "notebook-content.ipynb" and part.get("payloadType") == "InlineBase64"]
        if len(notebooks) != 1 or any(part.get("path") not in {"notebook-content.ipynb", ".platform"} for part in parts):
            raise RuntimeError("Fabric notebook definition missing or unsupported; verifier unavailable.")
        raw = base64.b64decode(notebooks[0]["payload"], validate=True)
        notebook_executable_digest(raw)
        return raw

    def find_named(self, workspace, name):
        """Recover a lost create acknowledgement by the unique immutable deployment name."""
        from uuid import UUID
        path, matches = f"/workspaces/{UUID(workspace)}/items?type=Notebook", []
        for _ in range(100):
            payload = self.request("GET", path)
            matches.extend(row["id"] for row in payload.get("value", []) if row.get("displayName") == name)
            path = payload.get("continuationUri")
            if not path:
                break
        else:
            raise RuntimeError("Notebook listing did not complete; deployment cannot safely retry.")
        if len(matches) > 1:
            raise RuntimeError("Duplicate staged deployment identities; reconcile before retrying.")
        return matches[0] if matches else None

    def create(self, workspace, name, snapshot, *, folder_id=None):
        """Create a distinct versioned notebook, optionally under the Governed folder."""
        import base64
        from uuid import UUID
        workspace = str(UUID(workspace))
        body = {"displayName": name, "definition": {"format": "ipynb", "parts": [{"path": "notebook-content.ipynb",
            "payload": base64.b64encode(snapshot).decode(), "payloadType": "InlineBase64"}]}}
        if folder_id:
            body["folderId"] = str(UUID(folder_id))
        result = self.request("POST", f"/workspaces/{workspace}/notebooks", body)
        if not result.get("id"):
            raise RuntimeError("Fabric created no identifiable Governed notebook; inspect staged artifacts.")
        return str(UUID(result["id"]))

    def update(self, workspace, notebook, snapshot):
        """Replace a definition only for an explicitly requested exact restoration."""
        import base64
        from uuid import UUID
        self.request("POST", f"/workspaces/{UUID(workspace)}/notebooks/{UUID(notebook)}/updateDefinition", {
            "definition": {"format": "ipynb", "parts": [{"path": "notebook-content.ipynb",
                "payload": base64.b64encode(snapshot).decode(), "payloadType": "InlineBase64"}]}})

    def governed_folder(self, workspace):
        """Find or create an organizational folder; it confers no permissions."""
        from uuid import UUID
        workspace = str(UUID(workspace))
        folders, path = [], f"/workspaces/{workspace}/folders"
        for _ in range(100):
            payload = self.request("GET", path)
            folders.extend(payload.get("value", []))
            path = payload.get("continuationUri")
            if not path:
                break
        else:
            raise RuntimeError("Fabric folder pagination did not complete.")
        matches = [row for row in folders if row.get("displayName") == "Governed" and not row.get("parentFolderId")]
        if len(matches) > 1:
            raise RuntimeError("Ambiguous Governed folder; reconcile before promotion.")
        if matches:
            return matches[0]["id"]
        result = self.request("POST", f"/workspaces/{workspace}/folders", {"displayName": "Governed"})
        if not result.get("id"):
            raise RuntimeError("Fabric did not return a Governed folder ID.")
        return result["id"]


def notebook_executable_digest(raw):
    """Hash canonical code and behavior metadata, ignoring Markdown and execution outputs.

    Conservatively retain all notebook and code-cell metadata except execution
    timing and output UI state. Parameter-cell source and tags remain hashed.
    Imported packages and referenced notebooks are deliberately not frozen.
    """
    notebook = _strict_package_json(raw)
    if notebook.get("nbformat") != 4 or not isinstance(notebook.get("cells"), list):
        raise ValueError("A complete nbformat 4 ipynb snapshot is required.")
    code = []
    for cell in notebook["cells"]:
        if cell.get("cell_type") not in {"code", "markdown", "raw"}:
            raise ValueError("Unsupported notebook cell type.")
        if cell["cell_type"] == "code":
            source = cell.get("source")
            if isinstance(source, list) and all(isinstance(line, str) for line in source):
                source = "".join(source)
            if not isinstance(source, str):
                raise ValueError("Notebook code requires text source.")
            metadata = {key: value for key, value in cell.get("metadata", {}).items()
                if key not in {"execution", "collapsed", "scrolled", "ExecuteTime"}}
            code.append({"source": source.replace("\r\n", "\n"), "metadata": metadata})
    if not code:
        raise ValueError("Notebook snapshot requires executable code.")
    metadata = {key: value for key, value in notebook.get("metadata", {}).items() if key not in {"widgets", "signature"}}
    return manifest_digest({"code": code, "metadata": metadata, "nbformat": notebook["nbformat"]})


def notebook_implementation_digest(raw):
    """Verify the complete saved implementation while allowing transient execution output.

    Full archived bytes remain exact. Running a notebook may change code-cell
    outputs, execution counts and execution-only UI/timing metadata without
    changing its approved implementation. Markdown and all behavior metadata stay
    bound; imported dependencies remain outside the notebook snapshot.
    """
    notebook_executable_digest(raw)
    notebook = _strict_package_json(raw)
    for cell in notebook["cells"]:
        if cell["cell_type"] == "code":
            cell.pop("outputs", None)
            cell.pop("execution_count", None)
            cell["metadata"] = {key: value for key, value in cell.get("metadata", {}).items()
                if key not in {"execution", "collapsed", "scrolled", "ExecuteTime"}}
    notebook["metadata"] = {key: value for key, value in notebook.get("metadata", {}).items()
        if key not in {"widgets", "signature"}}
    return manifest_digest(notebook)


def promoted_notebook(raw, pipeline_id):
    """Freeze one saved Dry Run setup call, resolving preceding literal notebook constants.

    Saved constant references are replaced by exact approved literals in the
    cloned setup call, so parameter overrides cannot switch its mode or identity.
    Arbitrary expressions and conditional/nested setup calls remain unsupported.
    """
    import ast
    notebook = _strict_package_json(raw)
    found, parameters, constants = 0, None, {}
    for cell in notebook["cells"]:
        if cell.get("cell_type") != "code":
            continue
        source = "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
        if source.lstrip().startswith(("%%", "%", "!")):
            continue
        replacements = []
        for statement in ast.parse(source).body:
            calls = [node for node in ast.walk(statement) if isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name) and node.func.id == "setup_pipeline"]
            for call in calls:
                if call is not getattr(statement, "value", None):
                    raise ValueError("Promotion requires one unconditional module-level setup_pipeline call.")
                found += 1
                values = {kw.arg: kw.value for kw in call.keywords}
                if call.args or None in values or set(values) - {"pipeline_id", "pipeline_mode", "observe_source", "source_observation_days"}:
                    raise ValueError("Promotion requires literal setup_pipeline parameters without argument overrides.")
                try:
                    literal = {key: constants[node.id] if isinstance(node, ast.Name) else ast.literal_eval(node)
                        for key, node in values.items()}
                except (KeyError, ValueError, TypeError):
                    raise ValueError("Promotion requires literal setup_pipeline parameters or preceding saved literal constants.") from None
                if literal.get("pipeline_id") != pipeline_id or literal.get("pipeline_mode") != "Dry Run":
                    raise ValueError("Save the manually tested notebook with its stable Pipeline ID and literal Dry Run mode.")
                parameters = {"manual": literal.get("observe_source", False), "days": literal.get("source_observation_days")}
                for key, node in values.items():
                    if key == "pipeline_mode" or isinstance(node, ast.Name):
                        text = repr("Governed" if key == "pipeline_mode" else literal[key])
                        if key == "pipeline_mode":
                            text = '"Governed"'
                        replacements.append((node, text))
            # Only preceding module-level literal assignments can resolve names.
            targets = statement.targets if isinstance(statement, ast.Assign) else [statement.target] if isinstance(statement, ast.AnnAssign) else []
            for target in targets:
                if isinstance(target, ast.Name):
                    try:
                        constants[target.id] = ast.literal_eval(statement.value)
                    except (ValueError, TypeError):
                        constants.pop(target.id, None)
        encoded = source.encode()
        lines = encoded.splitlines(keepends=True)
        spans = [(sum(map(len, lines[:node.lineno-1])) + node.col_offset,
                  sum(map(len, lines[:node.end_lineno-1])) + node.end_col_offset, text.encode()) for node, text in replacements]
        for start, end, replacement in sorted(spans, reverse=True):
            encoded = encoded[:start] + replacement + encoded[end:]
        cell["source"] = encoded.decode()
    if found != 1:
        raise ValueError("Promotion requires exactly one literal setup_pipeline call.")
    return canonical_pipeline_json(notebook).encode(), parameters



def snapshot_file(uri, *, spark_session, content=None):
    """Read notebook bytes or write once and verify the exact archived bytes."""
    jvm = spark_session._jvm
    path = jvm.org.apache.hadoop.fs.Path(uri)
    fs = path.getFileSystem(spark_session._jsc.hadoopConfiguration())
    if content is not None:
        fs.mkdirs(path.getParent())
        stream = fs.create(path, False)
        try:
            stream.write(bytearray(content))
        finally:
            stream.close()
    output = jvm.java.io.ByteArrayOutputStream()
    stream = fs.open(path)
    try:
        jvm.org.apache.hadoop.io.IOUtils.copyBytes(stream, output, spark_session._jsc.hadoopConfiguration(), False)
        raw = bytes((int(value) & 255 for value in output.toByteArray()))
    finally:
        stream.close(); output.close()
    if content is not None and raw != content:
        raise RuntimeError("Notebook snapshot readback failed.")
    return raw


def resolve_promoted_operations(operations, *, context, spark_session=None):
    """Resolve original schema choices and operation references using destination configuration."""
    from fabricops_kit.pipeline.shared import resolve_physical_table_identity, pipeline_physical_bindings
    config, workspace, _ = resolve_fabric_context(context=context)
    resolved, table_ids = [], {}
    for op in activation_operations(operations):
        logical = op["operation_key"].split(":", 1)[1]
        if "/" not in logical:
            raise ValueError("Promotion requires a logical store/table operation key.")
        store, table = logical.split("/", 1)
        identity = resolve_physical_table_identity(config, workspace, store=store,
            schema=op["requested_schema"], table_name=table)
        destination_id = identity["table_id"]
        previous = table_ids.setdefault(op["table_id"], destination_id)
        if previous != destination_id:
            raise ValueError("Different destination schema choices split one participant identity; review separate participants.")
        binding = pipeline_physical_bindings({destination_id: identity}, config=config, workspace_id=workspace)[destination_id]
        resolved.append({**op, "table_id": destination_id, "destination": binding})
    for op in resolved:
        op["source_table_ids"] = sorted(table_ids[table_id] for table_id in op["source_table_ids"])
        target = op["incremental_target_table_id"]
        if target is not None:
            if target not in table_ids:
                raise ValueError("Incremental target must be a reviewed pipeline participant.")
            op["incremental_target_table_id"] = table_ids[target]
    return resolved


def reviewed_contracts(operations, *, context, spark_session=None):
    """Resolve every source and target Contract in its physical workspace, with exact bindings."""
    from fabricops_kit.pipeline.shared import validated_processing, contract_guardrail_rows
    from fabricops_kit.data_contract.shared import validate_contract_definitions
    activations = read_activations(context=context, spark_session=spark_session)
    contracts = {}
    for op in operations:
        active = exact_record(activations, workspace_id=op["destination"]["workspace_id"], table_id=op["table_id"])
        if normalized_destination(parse_metadata_json(active["destination_json"], field="destination_json")) != normalized_destination(op["destination"]):
            raise ValueError("Contract physical binding differs from the reviewed operation.")
        contract = resolve_activation_contract(active, context=context, spark_session=spark_session)
        validate_contract_definitions(contract["contract_payload"])
        contract_guardrail_rows(contract, workspace_id=active["workspace_id"], table_id=op["table_id"])
        if op["pipeline_role"] == "target" and validated_processing(contract["contract_payload"]["table"].get("processing") or {})["load_strategy"] != op["write_mode"]:
            raise ValueError("Active Contract write strategy differs from the promoted notebook.")
        _, execution_workspace, _ = resolve_fabric_context(context=context)
        check_contract_agreement(active, execution_workspace_id=execution_workspace, context=context, spark_session=spark_session)
        contracts[op["table_id"]] = contract
    return contracts


def commit_pipeline_promotion(candidate, *, expected_active_version, context, spark_session=None):
    """Atomically select a deployed version only under independently verified Governance approval."""
    verify_promotion_integrity(candidate, context=context, spark_session=spark_session)
    def mutate(rows):
        verify_registry_approval(candidate, context=context, spark_session=spark_session)
        replay = [row for row in rows if row["promotion_id"] == candidate["promotion_id"]]
        if replay:
            original = replay[0]
            if any(original.get(key) != value for key, value in candidate.items() if key != "status" and not key.startswith("_") and key not in {"promoted_at", "promoted_by"}):
                raise ValueError("Promotion operation ID was reused with different content.")
            return rows, original
        scoped = [row for row in rows if (row["execution_workspace_id"], row["pipeline_id"]) ==
            (candidate["execution_workspace_id"], candidate["pipeline_id"])]
        active = [row for row in scoped if row["status"] == "active"]
        if (active[0]["pipeline_version"] if active else None) != expected_active_version:
            raise ValueError("Stale Pipeline Promotion; refresh and review again.")
        version = max((row["pipeline_version"] for row in scoped), default=0) + 1
        if candidate["pipeline_version"] != version:
            raise ValueError("Stale candidate version; stage and review a fresh promotion.")
        for row in active:
            row["status"] = "superseded"
        return rows + [candidate], candidate
    return mutate_metadata(REGISTRY_TABLE, mutate, context=context, spark_session=spark_session, operation_id=candidate["promotion_id"])


# Submission packages carry content identity, never an attestation that testing was truthful.
PIPELINE_ACTIVATION_TABLE = "METADATA_PIPELINE_ACTIVATION"
SUBMISSION_FIELDS = {
    "format_version", "submission_id", "pipeline_id", "source_workspace_id", "source_notebook_id",
    "execution_workspace_id", "source_snapshot_sha256", "executed_snapshot_sha256", "source_executable_sha256",
    "snapshot_sha256", "executable_sha256", "executed_executable_sha256", "operations", "tested_operations", "parameters", "dry_run_id",
    "created_by", "created_at", "expected_active_version", "intent", "retained_promotion_id", "retained_version",
}


def _strict_package_json(raw):
    """Reject duplicate keys and nonfinite numbers before interpreting untrusted JSON."""
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate submission JSON key: " + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("Nonfinite submission number: " + value)
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)


def validate_submission(package):
    """Verify the complete portable saved/executed/submitted record without remote access.

    All claimed test outcomes and creator fields remain engineer-provided claims.
    Governance separately reviews those claims and authoritative active policies.
    """
    import base64
    from uuid import UUID
    package = _strict_package_json(package) if isinstance(package, (str, bytes)) else deepcopy(package)
    if not isinstance(package, dict) or set(package) != {
            "manifest", "source_notebook_base64", "executed_notebook_base64", "notebook_base64", "dry_run", "contracts", "submission_sha256"}:
        raise ValueError("Incomplete or unsupported portable submission package.")
    manifest = package["manifest"]
    if not isinstance(manifest, dict) or set(manifest) != SUBMISSION_FIELDS or manifest["format_version"] != 1:
        raise ValueError("Unsupported submission manifest fields or version.")
    UUID(manifest["submission_id"])
    validate_pipeline_id(manifest["pipeline_id"])
    for key in ("source_workspace_id", "source_notebook_id", "execution_workspace_id", "created_by", "created_at", "dry_run_id"):
        if not isinstance(manifest[key], str) or not manifest[key].strip():
            raise ValueError("Submission requires " + key)
    datetime.fromisoformat(manifest["created_at"].replace("Z", "+00:00"))
    if manifest["intent"] not in {"deploy", "rollback", "restore"}:
        raise ValueError("Unsupported submission intent.")
    expected = manifest["expected_active_version"]
    if expected is not None and (type(expected) is not int or expected < 1):
        raise ValueError("Invalid expected active version.")
    if manifest["intent"] != "deploy" and (not manifest["retained_promotion_id"] or
            type(manifest["retained_version"]) is not int or manifest["retained_version"] < 1):
        raise ValueError("Rollback/restoration requires exact retained promotion lineage.")
    source = base64.b64decode(package["source_notebook_base64"], validate=True)
    snapshot = base64.b64decode(package["notebook_base64"], validate=True)
    executed = base64.b64decode(package["executed_notebook_base64"], validate=True)
    if (hashlib.sha256(source).hexdigest() != manifest["source_snapshot_sha256"] or
            hashlib.sha256(executed).hexdigest() != manifest["executed_snapshot_sha256"] or
            notebook_executable_digest(executed) != manifest["executed_executable_sha256"] or
            manifest["executed_executable_sha256"] != manifest["source_executable_sha256"] or
            notebook_executable_digest(source) != manifest["source_executable_sha256"] or
            hashlib.sha256(snapshot).hexdigest() != manifest["snapshot_sha256"] or
            notebook_executable_digest(snapshot) != manifest["executable_sha256"]):
        raise ValueError("Submitted saved/executed notebook identity or digest mismatch.")
    promoted, parameters = promoted_notebook(source, manifest["pipeline_id"])
    if promoted != snapshot or parameters != manifest["parameters"]:
        raise ValueError("Promoted snapshot or behavior parameters differ from the saved candidate.")
    operations = activation_operations(manifest["operations"])
    tested = activation_operations(manifest["tested_operations"])
    if len(operations) != len(tested):
        raise ValueError("Submitted and executed operation membership differ.")
    mappings = {}
    by_key = {op["operation_key"]: op for op in operations}
    for op in tested:
        approved = by_key.get(op["operation_key"])
        fields = {"operation_key", "pipeline_role", "read_mode", "write_mode", "query_sha256", "requested_schema"}
        if approved is None or any(op[key] != approved[key] for key in fields):
            raise ValueError("Submitted behavior differs from recorded Dry Run operations.")
        if op["table_id"] in mappings and mappings[op["table_id"]] != approved["table_id"]:
            raise ValueError("Ambiguous destination Table ID mapping.")
        mappings[op["table_id"]] = approved["table_id"]
    for op in tested:
        approved = by_key[op["operation_key"]]
        if (sorted(mappings[t] for t in op["source_table_ids"]) != approved["source_table_ids"] or
                (mappings.get(op["incremental_target_table_id"]) if op["incremental_target_table_id"] else None)
                != approved["incremental_target_table_id"]):
            raise ValueError("Submitted source/target associations differ from testing.")
    run = validate_pipeline_run(package["dry_run"])
    if (run["status"] != "dry_run_completed" or run["execution_mode"] != "dry_run" or
            run["run_id"] != manifest["dry_run_id"] or run["pipeline_id"] != manifest["pipeline_id"] or
            run["workspace_id"] != manifest["source_workspace_id"] or run["boundary_completed"] is not True or
            not run["completed_at"] or run["failures"] or len(run["operations"]) != len(tested)):
        raise ValueError("Submission requires a complete, consistent recorded manual Dry Run.")
    tested_by_key = {op["operation_key"]: op for op in tested}
    for op in run["operations"]:
        if (op["status"] != "succeeded" or not op["stages"] or
                any(stage["status"] not in {"passed", "warning", "skipped"} or
                    stage.get("evaluation_status") == "not_fully_evaluated" for stage in op["stages"]) or
                any(op[key] != tested_by_key.get(op["operation_key"], {}).get(key)
                    for key in OPERATION_FIELDS if key != "requested_schema")):
            raise ValueError("Dry Run contains incomplete or inconsistent operation evidence.")
        if op["contract_id"] is not None:
            contract = package["contracts"].get(op["table_id"])
            if (not contract or contract["contract_id"] != op["contract_id"] or
                    contract["contract_version"] != op["contract_version"] or
                    hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest() != op["payload_sha256"]):
                raise ValueError("Dry Run Contract evidence is missing or inconsistent.")
    content = {key: value for key, value in package.items() if key != "submission_sha256"}
    if manifest_digest(content) != package["submission_sha256"]:
        raise ValueError("Complete submission canonical digest mismatch.")
    return package


def export_pipeline_submission(dry_run, *, destination_workspace_id, context=None, spark_session=None):
    """Persist Engineering-owned complete evidence and return a portable JSON package."""
    import base64
    from fabricops_kit.pipeline.shared import PipelineSession
    if not isinstance(dry_run, PipelineSession) or dry_run.plan.execution_mode != "dry_run":
        raise ValueError("Engineering export requires a completed manual Dry Run.")
    plan = dry_run.plan
    if not plan.evidence.get("sealed") or plan.evidence["final_result"]["status"] != "dry_run_completed":
        raise ValueError("Complete and finalize the manual Dry Run before submission.")
    if plan.evidence.get("submission_persistence_failed"):
        plan.evidence["dry_run_evidence_uri"] = persist_engineering_dry_run(plan, spark_session=spark_session)
        plan.evidence.pop("submission_persistence_failed", None)
    raw = plan.evidence.get("notebook_snapshot")
    if raw is None:
        raise RuntimeError("No saved notebook was captured before execution; save and repeat the Dry Run.")
    current = FabricNotebookClient().definition(plan.workspace_id, plan.notebook_id)
    if notebook_executable_digest(current) != notebook_executable_digest(raw):
        raise ValueError("Saved executable notebook changed since execution; save and repeat the Dry Run.")
    executed, raw = raw, current
    snapshot, parameters = promoted_notebook(raw, plan.pipeline_id)
    if parameters != plan.evidence.get("source_observation_policy"):
        raise ValueError("Executed parameter overrides differ from the saved definition.")
    config, _, runtime = resolve_fabric_context(context=context or plan.runtime_context)
    routed = {**runtime, "config": config, "scope_workspace_id": destination_workspace_id,
        "metadata_workspace_id": runtime.get("metadata_workspace_id") or plan.workspace_id}
    from fabricops_kit.config.metadata_schemas import decode_metadata_row
    run = decode_metadata_row("METADATA_PIPELINE_RUN", plan.evidence["final_result"])
    tested = [{**{key: op[key] for key in OPERATION_FIELDS if key != "requested_schema"},
        "requested_schema": plan.evidence["operations"][op["operation_key"]]["requested_schema"]} for op in run["operations"]]
    rows = read_registry(context=routed, spark_session=spark_session)
    active = [row for row in rows if row["execution_workspace_id"] == destination_workspace_id
        and row["pipeline_id"] == plan.pipeline_id and row["status"] == "active"]
    audit = build_runtime_audit_fields(config=config, active_workspace_id=plan.workspace_id, runtime_context=runtime)
    manifest = dict(format_version=1, submission_id=str(uuid4()), pipeline_id=plan.pipeline_id,
        source_workspace_id=plan.workspace_id, source_notebook_id=plan.notebook_id,
        execution_workspace_id=destination_workspace_id, source_snapshot_sha256=hashlib.sha256(raw).hexdigest(),
        executed_snapshot_sha256=hashlib.sha256(executed).hexdigest(), executed_executable_sha256=notebook_executable_digest(executed),
        source_executable_sha256=notebook_executable_digest(raw),
        snapshot_sha256=hashlib.sha256(snapshot).hexdigest(), executable_sha256=notebook_executable_digest(snapshot),
        operations=resolve_promoted_operations(tested, context=routed, spark_session=spark_session), tested_operations=tested,
        parameters=parameters, dry_run_id=plan.plan_id, created_by=audit["_committed_by"], created_at=datetime.now(UTC).isoformat(),
        expected_active_version=active[0]["pipeline_version"] if active else None,
        intent="deploy", retained_promotion_id=None, retained_version=None)
    package = dict(manifest=manifest, source_notebook_base64=base64.b64encode(raw).decode(),
        executed_notebook_base64=base64.b64encode(executed).decode(),
        notebook_base64=base64.b64encode(snapshot).decode(), dry_run=run, contracts=json.loads(plan.contracts_json))
    package["submission_sha256"] = manifest_digest(package)
    package = validate_submission(canonical_pipeline_json(package))
    persist_engineering_submission(package, context=routed, spark_session=spark_session)
    return package


def persist_engineering_submission(package, *, context, spark_session=None):
    """Write once under explicitly Engineering-writable Files; never use shared staging."""
    package = validate_submission(package)
    root = metadata_path(REGISTRY_TABLE, context=context).split("/Tables/", 1)[0]
    uri = root + "/Files/fabricops/engineering/submissions/" + package["manifest"]["submission_id"] + ".json"
    spark = get_spark_session(spark_session, context=context)
    content = canonical_pipeline_json(package).encode()
    path = spark._jvm.org.apache.hadoop.fs.Path(uri)
    exists = path.getFileSystem(spark._jsc.hadoopConfiguration()).exists(path)
    if snapshot_file(uri, spark_session=spark, content=None if exists else content) != content:
        raise ValueError("Submission identity already contains different immutable content.")
    return uri


def validate_approvals(rows):
    """Reject ambiguous histories and mismatches between decisions and accepted packages."""
    ids, revisions, submissions = set(), set(), {}
    for row in rows:
        package = validate_submission(row["package_json"])
        manifest = package["manifest"]
        key = row["execution_workspace_id"], row["pipeline_id"], row["revision"]
        if (not row["approval_id"] or row["approval_id"] in ids or key in revisions or
                type(row["revision"]) is not int or row["revision"] < 1 or
                row["status"] not in {"imported", "approved", "rejected", "revoked"} or
                row["decision_kind"] != manifest["intent"] or
                any(row[key] != manifest[key] for key in ("submission_id", "pipeline_id", "execution_workspace_id", "expected_active_version")) or
                row["submission_sha256"] != package["submission_sha256"] or
                row.get("restores_promotion_id") != (manifest["retained_promotion_id"] if manifest["intent"] == "restore" else None) or
                not row["decided_by"] or not row["decided_at"]):
            raise ValueError("Invalid or ambiguous authoritative Governance decision history.")
        previous = submissions.setdefault(row["submission_id"], row["submission_sha256"])
        if previous != row["submission_sha256"]:
            raise ValueError("Accepted submission identity changed content.")
        policy = parse_metadata_json(row["policy_json"], field="policy_json")
        if not isinstance(policy, dict):
            raise ValueError("Review policy evidence must be an object.")
        ids.add(row["approval_id"]); revisions.add(key)
    for submission_id in submissions:
        events = sorted((row for row in rows if row["submission_id"] == submission_id), key=lambda row: row["revision"])
        if events[0]["status"] != "imported" or sum(row["status"] == "imported" for row in events) != 1:
            raise ValueError("Every decision requires one prior immutable Governance import.")
    return rows


def read_approvals(*, context, spark_session=None):
    """Read only Governance-controlled decisions; Registry status cannot grant approval."""
    return validate_approvals(metadata_records(PIPELINE_ACTIVATION_TABLE, context=context, spark_session=spark_session))


def import_pipeline_submission(package, *, context, spark_session=None):
    """Accept an immutable review copy using Governance's storage identity, without deployment."""
    package = validate_submission(package)
    manifest = package["manifest"]
    config, workspace, runtime = resolve_fabric_context(context=context)
    audit = build_runtime_audit_fields(config=config, active_workspace_id=workspace, runtime_context=runtime)
    def mutate(rows):
        validate_approvals(rows)
        matches = [row for row in rows if row["submission_id"] == manifest["submission_id"]]
        if matches:
            if any(row["submission_sha256"] != package["submission_sha256"] for row in matches):
                raise ValueError("An accepted submission is immutable; export a new submission identity.")
            return rows, min(matches, key=lambda row: row["revision"])
        revision = max((row["revision"] for row in rows if row["execution_workspace_id"] == manifest["execution_workspace_id"]
            and row["pipeline_id"] == manifest["pipeline_id"]), default=0) + 1
        row = dict(approval_id=str(uuid4()), submission_id=manifest["submission_id"], submission_sha256=package["submission_sha256"],
            execution_workspace_id=manifest["execution_workspace_id"], pipeline_id=manifest["pipeline_id"], revision=revision,
            status="imported", decision_kind=manifest["intent"], package_json=canonical_pipeline_json(package), policy_json="{}",
            expected_active_version=manifest["expected_active_version"],
            restores_promotion_id=manifest["retained_promotion_id"] if manifest["intent"] == "restore" else None,
            expires_at=None, decided_by=audit["_committed_by"], decided_at=datetime.now(UTC).replace(tzinfo=None),
            review_note="Untrusted Engineering claims; integrity verified, testing outcomes require independent review.", **audit)
        validate_approvals(rows + [row])
        return rows + [row], row
    return mutate_metadata(PIPELINE_ACTIVATION_TABLE, mutate, context=context, spark_session=spark_session)


def review_submission_policy(package, *, context, spark_session=None):
    """Independently verify configured bindings, frozen Contracts and Agreement associations."""
    package = validate_submission(package)
    manifest = package["manifest"]
    routed = {**context, "scope_workspace_id": manifest["execution_workspace_id"]}
    operations = manifest["operations"]
    if resolve_promoted_operations(operations, context=routed, spark_session=spark_session) != operations:
        raise ValueError("Submitted physical bindings differ from Governance's configured destination.")
    if manifest["intent"] in {"rollback", "restore"}:
        retained = exact_record(read_registry(context=routed, spark_session=spark_session),
            execution_workspace_id=manifest["execution_workspace_id"], pipeline_id=manifest["pipeline_id"],
            pipeline_version=manifest["retained_version"], promotion_id=manifest["retained_promotion_id"])
        verify_registry_approval(retained, context=routed, spark_session=spark_session, captured=True)
        if (any(retained[key] != manifest[key] for key in ("snapshot_sha256", "source_snapshot_sha256", "executable_sha256",
                "source_workspace_id", "source_notebook_id")) or
                activation_operations(retained["operations_json"]) != operations or
                parse_metadata_json(retained["parameters_json"], field="parameters_json") != manifest["parameters"] or
                manifest["intent"] == "restore" and (retained["status"] != "active" or
                    manifest["expected_active_version"] != retained["pipeline_version"])):
            raise ValueError("Recovery submission differs from the exact retained approved implementation.")
    contracts = reviewed_contracts(operations, context=routed, spark_session=spark_session)
    policy = {}
    for operation in operations:
        activation = exact_record(read_activations(context=routed, spark_session=spark_session),
            workspace_id=operation["destination"]["workspace_id"], table_id=operation["table_id"])
        check_contract_agreement(activation, execution_workspace_id=manifest["execution_workspace_id"],
            context=routed, spark_session=spark_session)
        contract = contracts[operation["table_id"]]
        policy[operation["operation_key"]] = {key: activation.get(key) for key in
            ("activation_id", "contract_id", "contract_version", "payload_sha256", "agreement_id", "agreement_version", "agreement_sha256")}
        if contract["contract_id"] != activation["contract_id"]:
            raise ValueError("Contract changed during policy review.")
    return policy


def decide_pipeline_submission(submission_id, *, status, expected_revision, policy, review_note,
                               context, governance_confirmed=False, expires_at=None, spark_session=None):
    """Append a conditional Governance decision; never create or update Engineering notebooks."""
    if type(expected_revision) is not int or expected_revision < 1:
        raise ValueError("An exact positive Governance review revision is required.")
    if governance_confirmed is not True or status not in {"approved", "rejected", "revoked"} or not str(review_note).strip():
        raise ValueError("Review, supply a decision note and explicitly confirm the Governance decision.")
    rows = read_approvals(context=context, spark_session=spark_session)
    matches = [row for row in rows if row["submission_id"] == submission_id]
    if not matches:
        raise ValueError("Import the submission into Governance-controlled metadata first.")
    imported = min(matches, key=lambda row: row["revision"])
    if status == "approved" and review_submission_policy(imported["package_json"], context=context, spark_session=spark_session) != policy:
        raise ValueError("Policy changed after review; review the current Contracts and Agreements again.")
    if expires_at is not None:
        expires_at = datetime.fromisoformat(str(expires_at).replace("Z", "+00:00")) if not isinstance(expires_at, datetime) else expires_at
        expires_at = expires_at.astimezone(UTC).replace(tzinfo=None) if expires_at.tzinfo else expires_at
        if expires_at <= datetime.now(UTC).replace(tzinfo=None):
            raise ValueError("Approval expiration must be in the future.")
    config, workspace, runtime = resolve_fabric_context(context=context)
    audit = build_runtime_audit_fields(config=config, active_workspace_id=workspace, runtime_context=runtime)
    if status == "approved" and audit["_committed_by"] == validate_submission(imported["package_json"])["manifest"]["created_by"]:
        raise ValueError("An independent Governance reviewer must approve the submission; self-approval is prohibited.")
    def mutate(current):
        validate_approvals(current)
        scoped = [row for row in current if row["execution_workspace_id"] == imported["execution_workspace_id"] and row["pipeline_id"] == imported["pipeline_id"]]
        if max(row["revision"] for row in scoped) != expected_revision:
            raise ValueError("Stale or conflicting Governance review; refresh before deciding.")
        latest = max((row for row in scoped if row["submission_id"] == submission_id), key=lambda row: row["revision"])
        if status == "revoked" and latest["status"] != "approved":
            raise ValueError("Only an approved submission can be revoked.")
        row = {**imported, **audit, "approval_id": str(uuid4()), "revision": expected_revision + 1,
            "status": status, "policy_json": canonical_pipeline_json(policy), "expires_at": expires_at,
            "decided_by": audit["_committed_by"], "decided_at": datetime.now(UTC).replace(tzinfo=None), "review_note": str(review_note).strip()}
        validate_approvals(current + [row])
        return current + [row], row
    return mutate_metadata(PIPELINE_ACTIVATION_TABLE, mutate, context=context, spark_session=spark_session)


def authoritative_approval(approval_id, *, context, spark_session=None, captured=False):
    """Resolve an exact effective Governance authority; never trust an Engineering row."""
    rows = read_approvals(context=context, spark_session=spark_session)
    approval = exact_record(rows, approval_id=approval_id, status="approved")
    latest = max((row for row in rows if row["submission_id"] == approval["submission_id"]), key=lambda row: row["revision"])
    if latest["approval_id"] != approval_id:
        raise ValueError("Approval was revoked or replaced by a later decision.")
    expires = approval.get("expires_at")
    if expires is not None:
        expires = datetime.fromisoformat(expires.replace("Z", "+00:00")) if isinstance(expires, str) else expires
        expires = expires.astimezone(UTC).replace(tzinfo=None) if expires.tzinfo else expires
        if expires <= datetime.now(UTC).replace(tzinfo=None):
            raise ValueError("Governance approval has expired.")
    if not captured and approval["decision_kind"] != "restore":
        approved = [row for row in rows if row["execution_workspace_id"] == approval["execution_workspace_id"]
            and row["pipeline_id"] == approval["pipeline_id"] and row["status"] == "approved" and row["decision_kind"] != "restore"]
        if max(approved, key=lambda row: row["revision"])["approval_id"] != approval_id:
            raise ValueError("Approval was superseded by a newer approved implementation.")
    return approval


def verify_registry_approval(row, *, context, spark_session=None, captured=False):
    """Bind all deployment authority to the exact package retained by Governance."""
    approval = authoritative_approval(row["approval_id"], context=context, spark_session=spark_session, captured=captured)
    package = validate_submission(approval["package_json"])
    manifest = package["manifest"]
    if (approval["decision_kind"] == "restore" or row["submission_id"] != manifest["submission_id"] or
            row["submission_sha256"] != package["submission_sha256"] or
            any(row[key] != manifest[key] for key in ("pipeline_id", "execution_workspace_id", "source_workspace_id", "source_notebook_id",
                "snapshot_sha256", "source_snapshot_sha256", "executable_sha256")) or
            activation_operations(row["operations_json"]) != manifest["operations"] or
            parse_metadata_json(row["parameters_json"], field="parameters_json") != manifest["parameters"] or
            row["bindings_sha256"] != manifest_digest(manifest["operations"])):
        raise ValueError("Engineering deployment differs from authoritative Governance approval.")
    return approval, package


def export_retained_submission(promotion_id, *, intent, context, spark_session=None):
    """Submit rollback or exact restoration of a retained version for a new Governance decision."""
    if intent not in {"rollback", "restore"}:
        raise ValueError("Select rollback or restoration.")
    config, workspace, runtime = resolve_fabric_context(context=context)
    rows = read_registry(context=context, spark_session=spark_session)
    row = exact_record(rows, promotion_id=promotion_id, execution_workspace_id=workspace)
    _, package = verify_registry_approval(row, context=context, spark_session=spark_session, captured=True)
    active = exact_record(rows, execution_workspace_id=workspace, pipeline_id=row["pipeline_id"], status="active")
    if intent == "restore" and active["promotion_id"] != promotion_id:
        raise ValueError("Restoration targets the currently intended active version only.")
    audit = build_runtime_audit_fields(config=config, active_workspace_id=workspace, runtime_context=runtime)
    manifest = package["manifest"]
    manifest.update(submission_id=str(uuid4()), created_by=audit["_committed_by"], created_at=datetime.now(UTC).isoformat(),
        expected_active_version=active["pipeline_version"], intent=intent, retained_promotion_id=promotion_id, retained_version=row["pipeline_version"])
    package["submission_sha256"] = manifest_digest({key: value for key, value in package.items() if key != "submission_sha256"})
    persist_engineering_submission(package, context=context, spark_session=spark_session)
    return package


def deploy_approved_submission(approval_id, *, context, spark_session=None):
    """Engineering clones the exact approved snapshot, verifies it and conditionally selects a new version."""
    import base64
    from uuid import NAMESPACE_URL, uuid5
    approval = authoritative_approval(approval_id, context=context, spark_session=spark_session)
    package = validate_submission(approval["package_json"])
    manifest = package["manifest"]
    _, workspace, runtime = resolve_fabric_context(context=context)
    if workspace != manifest["execution_workspace_id"]:
        raise ValueError("Deploy from the exact authorized Engineering execution workspace.")
    if manifest["intent"] == "restore":
        return restore_promoted_notebook(manifest["pipeline_id"], workspace_id=workspace,
            expected_active_version=manifest["expected_active_version"], approval_id=approval_id,
            context=context, spark_session=spark_session)
    review_submission_policy(package, context=context, spark_session=spark_session)
    rows = read_registry(context=context, spark_session=spark_session)
    promotion_id = str(uuid5(NAMESPACE_URL, "fabricops:deployment:" + approval_id))
    replay = [row for row in rows if row["promotion_id"] == promotion_id]
    if replay:
        verify_registry_approval(replay[0], context=context, spark_session=spark_session)
        verify_promotion_integrity(replay[0], context=context, spark_session=spark_session)
        return replay[0]
    scoped = [row for row in rows if row["pipeline_id"] == manifest["pipeline_id"] and row["execution_workspace_id"] == workspace]
    active = [row for row in scoped if row["status"] == "active"]
    if (active[0]["pipeline_version"] if active else None) != manifest["expected_active_version"]:
        raise ValueError("Stale approved deployment; submit the current expected version for a new review.")
    version = max((row["pipeline_version"] for row in scoped), default=0) + 1
    if manifest["intent"] == "rollback":
        retained = exact_record(rows, promotion_id=manifest["retained_promotion_id"], pipeline_version=manifest["retained_version"],
            execution_workspace_id=workspace, pipeline_id=manifest["pipeline_id"])
        if any(retained[key] != manifest[key] for key in ("snapshot_sha256", "executable_sha256")):
            raise ValueError("Rollback must match the exact retained approved implementation.")
    source = base64.b64decode(package["source_notebook_base64"], validate=True)
    snapshot = base64.b64decode(package["notebook_base64"], validate=True)
    spark = get_spark_session(spark_session, context=context)
    root = metadata_path(REGISTRY_TABLE, context=context).split("/Tables/", 1)[0]
    root += "/Files/fabricops/engineering/pipeline_snapshots/" + promotion_id
    candidate = {key: manifest[key] for key in ("execution_workspace_id", "pipeline_id", "source_workspace_id", "source_notebook_id",
        "source_snapshot_sha256", "snapshot_sha256", "executable_sha256", "submission_id")}
    candidate.update(pipeline_version=version, promotion_id=promotion_id, status="active", approval_id=approval_id,
        submission_sha256=package["submission_sha256"], operations_json=canonical_pipeline_json(manifest["operations"]),
        bindings_sha256=manifest_digest(manifest["operations"]), parameters_json=canonical_pipeline_json(manifest["parameters"]),
        restored_from_version=manifest["retained_version"] if manifest["intent"] == "rollback" else None)
    for field, content, name in (("source_snapshot_uri", source, "source.ipynb"), ("snapshot_uri", snapshot, "notebook.ipynb")):
        uri = root + "/" + name
        path = spark._jvm.org.apache.hadoop.fs.Path(uri)
        exists = path.getFileSystem(spark._jsc.hadoopConfiguration()).exists(path)
        if snapshot_file(uri, spark_session=spark, content=None if exists else content) != content:
            raise ValueError("Existing immutable Engineering snapshot changed.")
        candidate[field] = uri
    client = FabricNotebookClient()
    name = f'Governed {manifest["pipeline_id"]} {promotion_id}'
    staged_id = client.find_named(workspace, name)
    if not staged_id:
        staged_id = client.create(workspace, name, snapshot, folder_id=client.governed_folder(workspace))
    candidate["governed_notebook_id"] = staged_id
    if client.definition(workspace, staged_id) != snapshot:
        raise RuntimeError("Complete deployed notebook definition differs from the approved snapshot; previous version remains active.")
    audit = build_runtime_audit_fields(config=runtime["config"], active_workspace_id=workspace, runtime_context=runtime)
    candidate.update(promoted_by=audit["_committed_by"], promoted_at=datetime.now(UTC).replace(tzinfo=None), **audit)
    verify_registry_approval(candidate, context=context, spark_session=spark)
    return commit_pipeline_promotion(candidate, expected_active_version=manifest["expected_active_version"], context=context, spark_session=spark)


def check_contract_agreement(activation, *, execution_workspace_id, context, spark_session=None):
    """Enforce Governance's Agreement association for the exact active physical Contract."""
    refs = [activation.get(key) for key in ("agreement_id", "agreement_version", "agreement_sha256")]
    if not any(refs):
        if activation["workspace_id"] != execution_workspace_id:
            raise ValueError("Cross-workspace operations require an effective Agreement associated with the active Contract.")
        return
    if not all(refs):
        raise ValueError("Incomplete Governance-owned Agreement–Contract association.")
    row = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=context, spark_session=spark_session),
        agreement_id=refs[0], agreement_version=refs[1])
    validate_agreement(row)
    if manifest_digest(agreement_definition(row)) != refs[2]:
        raise ValueError("Associated Agreement content changed.")


def verify_promotion_integrity(row, *, context, spark_session=None, captured=False):
    """Verify archive, saved notebook, exact bindings and Agreement before managed work.

    Saved-definition verification is subject to TOCTOU. It cannot attest the
    executing kernel or prevent privileged direct Spark bypass. The release gate
    remains closed until the signed-in integration checklist has been completed.
    """
    _, approved_package = verify_registry_approval(row, context=context, spark_session=spark_session, captured=captured)
    import base64
    spark = get_spark_session(spark_session, context=context)
    try:
        raw = snapshot_file(row["snapshot_uri"], spark_session=spark)
        source = snapshot_file(row["source_snapshot_uri"], spark_session=spark)
    except Exception as exc:
        raise RuntimeError("Governed notebook archive is missing or unreadable; restore the exact retained files before retrying.") from exc
    if (raw != base64.b64decode(approved_package["notebook_base64"], validate=True) or
            source != base64.b64decode(approved_package["source_notebook_base64"], validate=True) or
            hashlib.sha256(raw).hexdigest() != row["snapshot_sha256"]
            or hashlib.sha256(source).hexdigest() != row["source_snapshot_sha256"]
            or notebook_executable_digest(raw) != row["executable_sha256"]):
        raise RuntimeError("Governed integrity mismatch: immutable notebook snapshot is missing or corrupt.")
    try:
        saved = FabricNotebookClient().definition(row["execution_workspace_id"], row["governed_notebook_id"])
    except Exception as exc:
        raise RuntimeError("Governed notebook verifier unavailable: cannot read the saved definition.") from exc
    if notebook_implementation_digest(saved) != notebook_implementation_digest(raw) or notebook_executable_digest(saved) != row["executable_sha256"]:
        raise RuntimeError("Governed integrity mismatch: saved code or parameters changed. Restore the exact snapshot or Dry Run and promote a new version.")
    operations = activation_operations(row["operations_json"])
    if manifest_digest(operations) != row["bindings_sha256"] or resolve_promoted_operations(operations, context=context, spark_session=spark) != operations:
        raise RuntimeError("Governed integrity mismatch: physical binding or destination configuration drift.")
    return operations


def build_governed_pipeline_plan(*, pipeline_id, context=None, spark_session=None):
    """Admit only the active physical notebook, pinning version and exact current Contracts."""
    validate_pipeline_id(pipeline_id)
    if not FABRIC_GOVERNED_VALIDATED:
        raise RuntimeError(FABRIC_VALIDATION_PENDING)
    from types import MappingProxyType
    from fabricops_kit.pipeline.shared import PipelineExecutionPlan, resolve_pipeline_participants, pipeline_physical_bindings
    config, workspace, runtime = resolve_fabric_context(context=context)
    principal = runtime.get("user_id") or runtime.get("user_name")
    if not principal or principal == "unknown":
        raise RuntimeError("Governed admission requires an actual runtime execution identity.")
    rows = read_registry(context=context, spark_session=spark_session)
    row = exact_record(rows, execution_workspace_id=workspace, pipeline_id=pipeline_id, status="active")
    if row["governed_notebook_id"] != runtime.get("notebook_id"):
        raise RuntimeError("Governed start rejected: stale schedule or superseded notebook version.")
    operations = verify_promotion_integrity(row, context=context, spark_session=spark_session, captured=True)
    contracts = reviewed_contracts(operations, context=context, spark_session=spark_session)
    participants = {"source": [], "target": []}
    for op in operations:
        store, table = op["operation_key"].split(":", 1)[1].split("/", 1)
        participants[op["pipeline_role"]].append(dict(store=store, table_name=table, schema=op["requested_schema"],
            logical_id=op["operation_key"].split(":", 1)[1], table_id=op["table_id"]))
    identities = resolve_pipeline_participants(config, workspace, sources=participants["source"], targets=participants["target"],
        context=context, spark_session=spark_session)
    bindings = pipeline_physical_bindings(identities, config=config, workspace_id=workspace)
    if any(bindings[op["table_id"]] != op["destination"] for op in operations):
        raise RuntimeError("Governed integrity mismatch: ambiguous physical participants.")
    run_context = MappingProxyType({**runtime, "config": config, "scope_workspace_id": workspace,
        "_pipeline_spark": spark_session, "_pipeline_bindings": bindings})
    selections = {key: {"contract_id": value["contract_id"], "contract_version": value["contract_version"]} for key, value in contracts.items()}
    plan = PipelineExecutionPlan("governed", workspace, row["governed_notebook_id"], str(uuid4()),
        canonical_pipeline_json(identities), canonical_pipeline_json(selections), canonical_pipeline_json(contracts), run_context,
        pipeline_id=pipeline_id, pipeline_version=row["pipeline_version"], promotion_id=row["promotion_id"],
        governed_notebook_id=row["governed_notebook_id"], activated_operations_json=row["operations_json"])
    plan.evidence["promotion"] = deepcopy(row)
    plan.evidence["governance_approval"] = deepcopy(verify_registry_approval(row, context=context, spark_session=spark_session, captured=True)[0])
    plan.evidence["contract_activations"] = [exact_record(read_activations(context=context, spark_session=spark_session),
        workspace_id=op["destination"]["workspace_id"], table_id=op["table_id"]) for op in operations]
    plan.evidence["approved_parameters"] = parse_metadata_json(row["parameters_json"], field="parameters_json")
    return plan


def verify_governed_plan(plan, *, spark_session=None):
    """Reverify the captured immutable version, allowing already admitted superseded runs to finish."""
    if not FABRIC_GOVERNED_VALIDATED:
        raise RuntimeError(FABRIC_VALIDATION_PENDING)
    from fabricops_kit.pipeline.shared import PipelineExecutionPlan
    if not isinstance(plan, PipelineExecutionPlan) or not plan.promotion_id or not plan.evidence.get("promotion"):
        raise RuntimeError("Governed managed operation has no captured Pipeline Promotion.")
    rows = read_registry(context=plan.runtime_context, spark_session=spark_session)
    row = exact_record(rows, execution_workspace_id=plan.workspace_id, pipeline_id=plan.pipeline_id,
        pipeline_version=plan.pipeline_version, promotion_id=plan.promotion_id, governed_notebook_id=plan.notebook_id)
    retained = plan.evidence["promotion"]
    if row["status"] not in {"active", "superseded"} or any(row.get(key) != value for key, value in retained.items() if key != "status"):
        raise RuntimeError("Governed captured immutable approval changed or was retired.")
    verify_promotion_integrity(row, context=plan.runtime_context, spark_session=spark_session, captured=True)
    for activation in plan.evidence["contract_activations"]:
        check_contract_agreement(activation, execution_workspace_id=plan.workspace_id, context=plan.runtime_context, spark_session=spark_session)
    for contract in json.loads(plan.contracts_json).values():
        resolve_activation_contract({**contract, "payload_sha256": hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest()},
            context=plan.runtime_context, spark_session=spark_session)


def guard_governed_write(plan, destination, *, spark_session=None):
    """Use the same exclusive physical target claim across old and new admitted versions."""
    verify_governed_plan(plan, spark_session=spark_session)
    publication_claim(plan.plan_id, destination, context=plan.runtime_context, spark_session=spark_session)
    plan.evidence.setdefault("publication_claims", []).append(dict(destination))
    plan.evidence["lease_token"] = plan.plan_id


def restore_promoted_notebook(pipeline_id, *, workspace_id, expected_active_version, approval_id,
                              context, spark_session=None):
    """Preserve the changed copy, restore the exact active archive, and verify saved readback."""
    import base64
    approval = authoritative_approval(approval_id, context=context, spark_session=spark_session)
    package = validate_submission(approval["package_json"])
    manifest = package["manifest"]
    if approval["decision_kind"] != "restore":
        raise ValueError("A separate exact Governance restoration authorization is required.")
    row = exact_record(read_registry(context=context, spark_session=spark_session), execution_workspace_id=workspace_id,
        pipeline_id=pipeline_id, pipeline_version=expected_active_version, status="active")
    verify_registry_approval(row, context=context, spark_session=spark_session, captured=True)
    if (manifest["retained_promotion_id"] != row["promotion_id"] or manifest["retained_version"] != row["pipeline_version"] or
            manifest["execution_workspace_id"] != workspace_id or
            any(row[key] != manifest[key] for key in ("snapshot_sha256", "source_snapshot_sha256", "executable_sha256")) or
            activation_operations(row["operations_json"]) != manifest["operations"] or
            parse_metadata_json(row["parameters_json"], field="parameters_json") != manifest["parameters"]):
        raise ValueError("Restoration authorization does not cover this exact active deployment.")
    spark = get_spark_session(spark_session, context=context)
    try:
        raw = snapshot_file(row["snapshot_uri"], spark_session=spark)
        source = snapshot_file(row["source_snapshot_uri"], spark_session=spark)
    except Exception as exc:
        raise RuntimeError("Governed notebook archive is missing or unreadable; restore the exact retained files before retrying.") from exc
    if (hashlib.sha256(raw).hexdigest() != row["snapshot_sha256"]
            or hashlib.sha256(source).hexdigest() != row["source_snapshot_sha256"]
            or notebook_executable_digest(raw) != row["executable_sha256"]):
        raise RuntimeError("Cannot restore a missing or corrupt archived snapshot.")
    operations = activation_operations(row["operations_json"])
    if resolve_promoted_operations(operations, context=context, spark_session=spark) != operations:
        raise RuntimeError("Resolve destination configuration drift before exact restoration.")
    review_submission_policy(package, context=context, spark_session=spark)
    client = FabricNotebookClient()
    changed = client.definition(workspace_id, row["governed_notebook_id"])
    uri = row["snapshot_uri"].rsplit("/", 1)[0] + "/repairs/" + approval_id + ".modified.ipynb"
    receipt_uri = uri.removesuffix(".modified.ipynb") + ".json"
    def exists(location):
        path = spark._jvm.org.apache.hadoop.fs.Path(location)
        return path.getFileSystem(spark._jsc.hadoopConfiguration()).exists(path)
    if exists(receipt_uri):
        receipt = _strict_package_json(snapshot_file(receipt_uri, spark_session=spark))
        if (receipt["restoration_approval_id"] != approval_id or receipt["promotion_id"] != row["promotion_id"] or
                receipt["pipeline_version"] != row["pipeline_version"] or receipt["snapshot_sha256"] != row["snapshot_sha256"]):
            raise ValueError("Restoration receipt differs from the authorized implementation.")
        if notebook_implementation_digest(changed) != notebook_implementation_digest(raw):
            raise ValueError("Restoration authorization was already used; request a fresh decision for new modifications.")
        verify_promotion_integrity(row, context=context, spark_session=spark, captured=True)
        return receipt
    if exists(uri):
        preserved = snapshot_file(uri, spark_session=spark)
        if changed not in (preserved, raw):
            raise ValueError("Notebook changed after recovery staging; request a fresh restoration decision.")
    else:
        snapshot_file(uri, spark_session=spark, content=changed)
    # An intervening promotion cancels repair before updating any physical notebook.
    exact_record(read_registry(context=context, spark_session=spark), execution_workspace_id=workspace_id,
        pipeline_id=pipeline_id, pipeline_version=expected_active_version, status="active")
    authoritative_approval(approval_id, context=context, spark_session=spark)
    verify_registry_approval(row, context=context, spark_session=spark, captured=True)
    client.update(workspace_id, row["governed_notebook_id"], raw)
    actual = client.definition(workspace_id, row["governed_notebook_id"])
    if actual != raw or notebook_executable_digest(actual) != row["executable_sha256"]:
        raise RuntimeError("Restoration readback failed; Governed remains blocked by integrity mismatch.")
    verify_promotion_integrity(row, context=context, spark_session=spark, captured=True)
    _, _, runtime = resolve_fabric_context(context=context)
    audit = build_runtime_audit_fields(config=runtime["config"], active_workspace_id=workspace_id, runtime_context=runtime)
    receipt = {"restoration_approval_id": approval_id, "promotion_id": row["promotion_id"], "pipeline_version": row["pipeline_version"],
        "preserved_copy_uri": uri, "receipt_uri": receipt_uri, "snapshot_sha256": row["snapshot_sha256"],
        "restored_by": audit["_committed_by"], "restored_at": datetime.now(UTC).isoformat(),
        "ready": FABRIC_GOVERNED_VALIDATED, "blocking_reason": None if FABRIC_GOVERNED_VALIDATED else FABRIC_VALIDATION_PENDING}
    snapshot_file(receipt_uri, spark_session=spark, content=canonical_pipeline_json(receipt).encode())
    return receipt


def resolve_active_consumer_contract(config, active_workspace_id, table_id, *, spark_session=None, destination=None):
    """Require one approved physical consumer binding and its exact effective Agreement."""
    from fabricops_kit.pipeline.shared import resolve_catalogue_table_identity, pipeline_physical_bindings
    context = {"config": config, "scope_workspace_id": active_workspace_id}
    if destination is None:
        identity = resolve_catalogue_table_identity(config, active_workspace_id, table_id, context=context, spark_session=spark_session)
        destination = pipeline_physical_bindings({table_id: identity}, config=config, workspace_id=active_workspace_id)[table_id]
    physical = normalized_destination(destination)
    activation = exact_record(read_activations(context=context, spark_session=spark_session),
        workspace_id=destination["workspace_id"], table_id=table_id)
    if normalized_destination(parse_metadata_json(activation["destination_json"], field="destination_json")) != physical:
        raise ValueError("Consumer physical binding differs from the activated Contract; review the configured table before provisioning.")
    contract = resolve_activation_contract(activation, context=context, spark_session=spark_session)
    check_contract_agreement(activation, execution_workspace_id=active_workspace_id, context=context, spark_session=spark_session)
    if not activation.get("agreement_id"):
        raise ValueError("Consumer provisioning requires an effective Governance-owned Agreement–Contract association.")
    return {**contract, "agreement_id": activation["agreement_id"], "agreement_version": activation["agreement_version"]}


def persist_engineering_dry_run(plan, *, spark_session=None):
    """Retain serializable Engineering test claims before the notebook session ends.

    The saved definition is captured at plan creation. Export separately verifies
    it still equals the current saved source; neither record attests kernel code.
    """
    import base64
    from uuid import NAMESPACE_URL, uuid5
    raw = plan.evidence.get("notebook_snapshot")
    if raw is None:
        raise RuntimeError("Dry Run has no saved definition; portable submission is unavailable.")
    from fabricops_kit.config.metadata_schemas import decode_metadata_row
    run = decode_metadata_row("METADATA_PIPELINE_RUN", plan.evidence["final_result"])
    record = dict(format_version=1, submission_id=str(uuid5(NAMESPACE_URL, "fabricops:dry-run:" + plan.plan_id)),
        pipeline_id=plan.pipeline_id, source_workspace_id=plan.workspace_id, source_notebook_id=plan.notebook_id,
        source_notebook_base64=base64.b64encode(raw).decode(), source_snapshot_sha256=hashlib.sha256(raw).hexdigest(),
        executable_sha256=notebook_executable_digest(raw), dry_run=run, contracts=json.loads(plan.contracts_json),
        operations=[{**{key: op[key] for key in OPERATION_FIELDS if key != "requested_schema"},
            "requested_schema": plan.evidence["operations"][op["operation_key"]]["requested_schema"]} for op in run["operations"]],
        parameters=plan.evidence["source_observation_policy"],
        created_by=plan.runtime_context.get("user_id") or plan.runtime_context.get("user_name"),
        created_at=run["completed_at"])
    if not record["created_by"]:
        raise ValueError("Persistent Dry Run evidence requires a signed-in creator identity.")
    record["manifest_sha256"] = manifest_digest(record)
    uri = metadata_path(REGISTRY_TABLE, context=plan.runtime_context).split("/Tables/", 1)[0]
    uri += "/Files/fabricops/engineering/dry_runs/" + record["submission_id"] + ".json"
    spark = get_spark_session(spark_session, context=plan.runtime_context)
    path = spark._jvm.org.apache.hadoop.fs.Path(uri)
    exists = path.getFileSystem(spark._jsc.hadoopConfiguration()).exists(path)
    content = canonical_pipeline_json(record).encode()
    if snapshot_file(uri, spark_session=spark, content=None if exists else content) != content:
        raise RuntimeError("Persisted Engineering Dry Run identity changed content.")
    return uri
