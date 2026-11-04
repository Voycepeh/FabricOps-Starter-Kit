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
            "bindings_sha256", "parameters_json", "promoted_by", "promoted_at")
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
        refs = [row.get(key) for key in ("agreement_id", "agreement_version", "agreement_sha256")]
        if any(refs) and not all(refs):
            raise ValueError("Incomplete exact Agreement reference.")
    return rows


def validate_activations(rows):
    """Enforce one frozen Contract per physical workspace/Table ID, including aliases."""
    identities, bindings, ids = set(), set(), set()
    for row in rows:
        identity = row.get("workspace_id"), row.get("table_id")
        destination = parse_metadata_json(row.get("destination_json"), field="destination_json")
        physical = normalized_destination(destination)
        if (not all(identity) or row.get("status") != "active" or type(row.get("revision")) is not int
                or row["revision"] < 1 or not row.get("activation_id") or not row.get("contract_id")
                or type(row.get("contract_version")) is not int or row["contract_version"] < 1
                or not row.get("payload_sha256") or not row.get("activated_by") or not row.get("activated_at")):
            raise ValueError("Incomplete active Data Contract identity.")
        if str(destination["workspace_id"]).casefold() != str(identity[0]).casefold():
            raise ValueError("Contract Activation must use the physical table workspace.")
        if identity in identities or physical in bindings or row["activation_id"] in ids:
            raise ValueError("Ambiguous Data Contract Activation identity or physical alias.")
        identities.add(identity); bindings.add(physical); ids.add(row["activation_id"])
    return rows


def read_registry(*, context, spark_session=None):
    """Read only validated per-version Pipeline Promotions; empty setup is valid."""
    return validate_registry(metadata_records(REGISTRY_TABLE, context=context, spark_session=spark_session))


def read_activations(*, context, spark_session=None):
    """Read independent Governance-owned physical Contract activations."""
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
                                  expected_destination=None, expected_payload_sha256=None):
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
    owner = "activation:" + activation_id
    publication_claim(owner, destination, context=context, spark_session=spark_session)
    try:
        def mutate(rows):
            matches = [row for row in rows if (row["workspace_id"], row["table_id"]) == (workspace, table_id)]
            current = matches[0] if matches else None
            replay = [row for row in rows if row["activation_id"] == activation_id]
            if replay:
                if current is None or replay[0] is not current or any(current.get(key) != record[key]
                        for key in ("contract_id", "contract_version", "payload_sha256", "destination_json")):
                    raise ValueError("Activation operation ID was reused with different content.")
                return rows, current
            if (current["activation_id"] if current else None) != expected_activation_id:
                raise ValueError("Stale Contract Activation; refresh and review again.")
            record["revision"] = current["revision"] + 1 if current else 1
            result = [row for row in rows if row is not current] + [record]
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
    notebook = json.loads(raw)
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


def promoted_notebook(raw, pipeline_id):
    """Freeze one saved Dry Run setup call, resolving preceding literal notebook constants.

    Saved constant references are replaced by exact approved literals in the
    cloned setup call, so parameter overrides cannot switch its mode or identity.
    Arbitrary expressions and conditional/nested setup calls remain unsupported.
    """
    import ast
    notebook = json.loads(raw)
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
        contracts[op["table_id"]] = contract
    return contracts


def check_promotion_agreement(candidate, *, context, spark_session=None):
    """Validate exact Agreement content and effectiveness when an Agreement is attached."""
    refs = [candidate.get(key) for key in ("agreement_id", "agreement_version", "agreement_sha256")]
    if not any(refs):
        if candidate.get("operations_json") is not None:
            operations = activation_operations(candidate["operations_json"])
            if any(op["destination"]["workspace_id"] != candidate.get("execution_workspace_id") for op in operations):
                raise ValueError("Cross-workspace data operations require an exact effective Data Agreement.")
        return
    if not all(refs):
        raise ValueError("Incomplete exact Data Agreement reference.")
    row = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=context, spark_session=spark_session),
        agreement_id=refs[0], agreement_version=refs[1])
    validate_agreement(row)
    if manifest_digest(agreement_definition(row)) != refs[2]:
        raise ValueError("Exact Data Agreement content changed.")


def commit_pipeline_promotion(candidate, *, expected_active_version, context, spark_session=None):
    """Atomically supersede and insert an immutable version, rejecting racing/stale approval."""
    def mutate(rows):
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


def prepare_pipeline_promotion(dry_run, *, destination_workspace_id, expected_active_version, agreement_id=None,
                               agreement_version=None, context=None, spark_session=None):
    """Build a reviewable destination-bound candidate from a completed manual Dry Run."""
    from fabricops_kit.pipeline.shared import PipelineSession, pipeline_run_row
    if not isinstance(dry_run, PipelineSession) or dry_run.plan.execution_mode != "dry_run":
        raise ValueError("Promotion requires the manually executed Dry Run session.")
    plan = dry_run.plan
    if not plan.evidence.get("sealed") or plan.evidence["final_result"]["status"] != "dry_run_completed":
        raise ValueError("Complete and finalize the manual Dry Run before promotion.")
    raw = plan.evidence.get("notebook_snapshot")
    if raw is None:
        raise RuntimeError("Dry Run has no saved notebook verification; save and repeat the manual Dry Run in Fabric.")
    client = FabricNotebookClient()
    current = client.definition(plan.workspace_id, plan.notebook_id)
    if notebook_executable_digest(current) != notebook_executable_digest(raw):
        raise RuntimeError("Saved notebook code changed after the manual Dry Run; rerun before promotion.")
    promoted, parameters = promoted_notebook(current, plan.pipeline_id)
    if parameters != plan.evidence.get("source_observation_policy"):
        raise ValueError("Dry Run parameter overrides differ from the saved notebook.")
    config, _, runtime = resolve_fabric_context(context=context or plan.runtime_context)
    destination = {**runtime, "config": config, "scope_workspace_id": destination_workspace_id,
        "metadata_workspace_id": runtime.get("metadata_workspace_id") or plan.workspace_id}
    observed = pipeline_run_row(plan, status="dry_run_completed")
    from fabricops_kit.config.metadata_schemas import decode_metadata_row
    observed = decode_metadata_row("METADATA_PIPELINE_RUN", observed)
    operations = []
    for op in observed["operations"]:
        recorded = plan.evidence["operations"][op["operation_key"]]
        if "requested_schema" not in recorded:
            raise ValueError("Manual Dry Run is missing the original schema choice; execute the complete pipeline before review.")
        operations.append({**{key: op[key] for key in OPERATION_FIELDS if key != "requested_schema"},
            "requested_schema": recorded["requested_schema"]})
    operations = resolve_promoted_operations(operations, context=destination, spark_session=spark_session)
    contracts = reviewed_contracts(operations, context=destination, spark_session=spark_session)
    rows = read_registry(context=destination, spark_session=spark_session)
    scoped = [row for row in rows if (row["execution_workspace_id"], row["pipeline_id"]) == (destination_workspace_id, plan.pipeline_id)]
    active = [row for row in scoped if row["status"] == "active"]
    if (active[0]["pipeline_version"] if active else None) != expected_active_version:
        raise ValueError("Stale Pipeline Promotion; refresh and review again.")
    candidate = dict(execution_workspace_id=destination_workspace_id, pipeline_id=plan.pipeline_id,
        pipeline_version=max((row["pipeline_version"] for row in scoped), default=0)+1, promotion_id=str(uuid4()),
        source_workspace_id=plan.workspace_id, source_notebook_id=plan.notebook_id, status="active",
        snapshot_sha256=hashlib.sha256(promoted).hexdigest(), source_snapshot_sha256=hashlib.sha256(current).hexdigest(),
        executable_sha256=notebook_executable_digest(promoted), operations_json=canonical_pipeline_json(operations),
        bindings_sha256=manifest_digest(operations), parameters_json=canonical_pipeline_json(parameters),
        agreement_id=agreement_id, agreement_version=agreement_version, agreement_sha256=None, restored_from_version=None)
    identical = [row["pipeline_version"] for row in scoped if row["executable_sha256"] == candidate["executable_sha256"]]
    candidate["restored_from_version"] = max(identical) if identical else None
    if agreement_id is not None:
        agreement = exact_record(metadata_records("METADATA_DATA_AGREEMENT", context=destination, spark_session=spark_session),
            agreement_id=agreement_id, agreement_version=agreement_version)
        candidate["agreement_sha256"] = manifest_digest(agreement_definition(agreement))
    check_promotion_agreement(candidate, context=destination, spark_session=spark_session)
    # Review object is hashed and revalidated before any remote mutation.
    review = dict(candidate=candidate, source_snapshot=current, snapshot=promoted, context=destination,
        expected_active_version=expected_active_version, contracts={key: {name: row[name] for name in
            ("contract_id", "contract_version", "contract_payload_json")} for key, row in contracts.items()})
    review["review_sha256"] = promotion_review_digest(review)
    return review


def promotion_review_digest(review):
    """Bind approval to the displayed code, operations, Contracts and expected active version."""
    return manifest_digest({"candidate": review["candidate"], "expected_active_version": review["expected_active_version"],
        "contracts": review["contracts"], "source_sha256": hashlib.sha256(review["source_snapshot"]).hexdigest(),
        "snapshot_sha256": hashlib.sha256(review["snapshot"]).hexdigest()})


def stage_pipeline_promotion(review, *, governance_confirmed=False, spark_session=None):
    """Archive, clone, verify, then atomically switch authority; failed staging never deactivates old code."""
    if governance_confirmed is not True or promotion_review_digest(review) != review.get("review_sha256"):
        raise ValueError("Review the exact candidate and explicitly confirm Pipeline Promotion.")
    context, candidate = review["context"], deepcopy(review["candidate"])
    if (hashlib.sha256(review["snapshot"]).hexdigest() != candidate["snapshot_sha256"]
            or hashlib.sha256(review["source_snapshot"]).hexdigest() != candidate["source_snapshot_sha256"]
            or notebook_executable_digest(review["snapshot"]) != candidate["executable_sha256"]):
        raise ValueError("Reviewed notebook bytes differ from the declared snapshot hashes.")
    _, workspace, runtime = resolve_fabric_context(context=context)
    if workspace != candidate["execution_workspace_id"]:
        raise ValueError("Destination execution workspace changed after review.")
    rows = read_registry(context=context, spark_session=spark_session)
    replay = [row for row in rows if row["promotion_id"] == candidate["promotion_id"]]
    if replay:
        # Lost acknowledgement: only the same immutable request may recover success.
        if any(replay[0].get(key) != value for key, value in candidate.items() if key != "status"):
            raise ValueError("Promotion ID was reused with different content.")
        return replay[0]
    operations = activation_operations(candidate["operations_json"])
    resolved = resolve_promoted_operations(operations, context=context, spark_session=spark_session)
    if resolved != operations or manifest_digest(operations) != candidate["bindings_sha256"]:
        raise ValueError("Destination configuration drift after review.")
    contracts = reviewed_contracts(operations, context=context, spark_session=spark_session)
    actual = {key: {name: row[name] for name in ("contract_id", "contract_version", "contract_payload_json")} for key, row in contracts.items()}
    if actual != review["contracts"]:
        raise ValueError("Active Contracts changed after review; review the new versions.")
    check_promotion_agreement(candidate, context=context, spark_session=spark_session)
    if candidate.get("restored_from_version") is not None:
        previous = exact_record(rows, execution_workspace_id=workspace, pipeline_id=candidate["pipeline_id"],
            pipeline_version=candidate["restored_from_version"])
        if previous["pipeline_version"] >= candidate["pipeline_version"] or previous["executable_sha256"] != candidate["executable_sha256"]:
            raise ValueError("Implementation lineage must identify the exact retained prior implementation.")
    spark = get_spark_session(spark_session, context=context)
    root = metadata_path(REGISTRY_TABLE, context=context).split("/Tables/", 1)[0]
    root += f'/Files/fabricops/pipeline_snapshots/{workspace}/{candidate["pipeline_id"]}/v{candidate["pipeline_version"]}/{candidate["promotion_id"]}'
    for field, content, name in (("source_snapshot_uri", review["source_snapshot"], "source.ipynb"), ("snapshot_uri", review["snapshot"], "notebook.ipynb")):
        uri = root + "/" + name
        # Resumable staging may read an existing identical file, never overwrite it.
        jpath = spark._jvm.org.apache.hadoop.fs.Path(uri)
        exists = jpath.getFileSystem(spark._jsc.hadoopConfiguration()).exists(jpath)
        actual = snapshot_file(uri, spark_session=spark, content=None if exists else content)
        if actual != content:
            raise RuntimeError("Existing immutable notebook archive differs; inspect staged artifacts.")
        candidate[field] = uri
    client = FabricNotebookClient()
    # Preserve the staged item ID on lost-ack retry; no silent item replacement.
    staged_id = review.get("staged_notebook_id")
    if not staged_id:
        folder = client.governed_folder(workspace) if workspace == candidate["source_workspace_id"] else None
        staged_id = client.create(workspace, f'Governed {candidate["pipeline_id"]} v{candidate["pipeline_version"]} {candidate["promotion_id"]}',
            review["snapshot"], folder_id=folder)
        review["staged_notebook_id"] = staged_id
    candidate["governed_notebook_id"] = staged_id
    retrieved = client.definition(workspace, staged_id)
    if notebook_executable_digest(retrieved) != candidate["executable_sha256"]:
        raise RuntimeError("Cloned Governed notebook readback changed executable content; old version remains active.")
    audit = build_runtime_audit_fields(config=runtime["config"], active_workspace_id=workspace, runtime_context=runtime)
    candidate.update(promoted_by=audit["_committed_by"], promoted_at=datetime.now(UTC).replace(tzinfo=None), **audit)
    return commit_pipeline_promotion(candidate, expected_active_version=review["expected_active_version"], context=context, spark_session=spark)


def verify_promotion_integrity(row, *, context, spark_session=None):
    """Verify archive, saved notebook, exact bindings and Agreement before managed work.

    Saved-definition verification is subject to TOCTOU. It cannot attest the
    executing kernel or prevent privileged direct Spark bypass. The release gate
    remains closed until the signed-in integration checklist has been completed.
    """
    spark = get_spark_session(spark_session, context=context)
    try:
        raw = snapshot_file(row["snapshot_uri"], spark_session=spark)
        source = snapshot_file(row["source_snapshot_uri"], spark_session=spark)
    except Exception as exc:
        raise RuntimeError("Governed notebook archive is missing or unreadable; restore the exact retained files before retrying.") from exc
    if (hashlib.sha256(raw).hexdigest() != row["snapshot_sha256"]
            or hashlib.sha256(source).hexdigest() != row["source_snapshot_sha256"]
            or notebook_executable_digest(raw) != row["executable_sha256"]):
        raise RuntimeError("Governed integrity mismatch: immutable notebook snapshot is missing or corrupt.")
    try:
        saved = FabricNotebookClient().definition(row["execution_workspace_id"], row["governed_notebook_id"])
    except Exception as exc:
        raise RuntimeError("Governed notebook verifier unavailable: cannot read the saved definition.") from exc
    if notebook_executable_digest(saved) != row["executable_sha256"]:
        raise RuntimeError("Governed integrity mismatch: saved code or parameters changed. Restore the exact snapshot or Dry Run and promote a new version.")
    operations = activation_operations(row["operations_json"])
    if manifest_digest(operations) != row["bindings_sha256"] or resolve_promoted_operations(operations, context=context, spark_session=spark) != operations:
        raise RuntimeError("Governed integrity mismatch: physical binding or destination configuration drift.")
    check_promotion_agreement(row, context=context, spark_session=spark)
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
    operations = verify_promotion_integrity(row, context=context, spark_session=spark_session)
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
    verify_promotion_integrity(row, context=plan.runtime_context, spark_session=spark_session)
    for contract in json.loads(plan.contracts_json).values():
        resolve_activation_contract({**contract, "payload_sha256": hashlib.sha256(contract["contract_payload_json"].encode()).hexdigest()},
            context=plan.runtime_context, spark_session=spark_session)


def guard_governed_write(plan, destination, *, spark_session=None):
    """Use the same exclusive physical target claim across old and new admitted versions."""
    verify_governed_plan(plan, spark_session=spark_session)
    publication_claim(plan.plan_id, destination, context=plan.runtime_context, spark_session=spark_session)
    plan.evidence.setdefault("publication_claims", []).append(dict(destination))
    plan.evidence["lease_token"] = plan.plan_id


def restore_promoted_notebook(pipeline_id, *, workspace_id, expected_active_version, governance_confirmed,
                              context, spark_session=None):
    """Preserve the changed copy, restore the exact active archive, and verify saved readback."""
    if governance_confirmed is not True:
        raise ValueError("Review and explicitly confirm exact notebook restoration.")
    row = exact_record(read_registry(context=context, spark_session=spark_session), execution_workspace_id=workspace_id,
        pipeline_id=pipeline_id, pipeline_version=expected_active_version, status="active")
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
    check_promotion_agreement(row, context=context, spark_session=spark)
    client = FabricNotebookClient()
    changed = client.definition(workspace_id, row["governed_notebook_id"])
    uri = row["snapshot_uri"].rsplit("/", 1)[0] + "/repairs/" + str(uuid4()) + ".ipynb"
    snapshot_file(uri, spark_session=spark, content=changed)
    # An intervening promotion cancels repair before updating any physical notebook.
    exact_record(read_registry(context=context, spark_session=spark), execution_workspace_id=workspace_id,
        pipeline_id=pipeline_id, pipeline_version=expected_active_version, status="active")
    client.update(workspace_id, row["governed_notebook_id"], raw)
    actual = client.definition(workspace_id, row["governed_notebook_id"])
    if notebook_executable_digest(actual) != row["executable_sha256"]:
        raise RuntimeError("Restoration readback failed; Governed remains blocked by integrity mismatch.")
    verify_promotion_integrity(row, context=context, spark_session=spark)
    return {"promotion_id": row["promotion_id"], "pipeline_version": row["pipeline_version"], "preserved_copy_uri": uri,
        "ready": FABRIC_GOVERNED_VALIDATED, "blocking_reason": None if FABRIC_GOVERNED_VALIDATED else FABRIC_VALIDATION_PENDING}


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
    agreements = {(row["agreement_id"], row["agreement_version"], row["agreement_sha256"]) for row in read_registry(context=context, spark_session=spark_session)
        if row["status"] == "active" and row.get("agreement_id") and any(op["table_id"] == table_id
            and normalized_destination(op["destination"]) == physical for op in activation_operations(row["operations_json"]))}
    if len(agreements) != 1:
        raise ValueError("No unambiguous active pipeline Agreement covers this consumer physical binding.")
    agreement_id, version, digest = next(iter(agreements))
    check_promotion_agreement(dict(agreement_id=agreement_id, agreement_version=version, agreement_sha256=digest), context=context, spark_session=spark_session)
    return {**contract, "agreement_id": agreement_id, "agreement_version": version}
