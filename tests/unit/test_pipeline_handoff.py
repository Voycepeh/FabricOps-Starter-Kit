"""Independent-session handoff and authoritative approval invariants.

Storage ACL fixtures are application simulations, never Fabric permission evidence.
"""
import base64
from copy import deepcopy
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest

from fabricops_kit.activated_pipeline import shared as service
from fabricops_kit.pipeline.shared import canonical_pipeline_json
from tests.unit.test_activated_pipeline import PIPELINE_ID, notebook, operation, promotion

POLICY_REVIEW = service.review_submission_policy


def package_candidate():
    """Build a complete portable candidate with saved code and recorded operations."""
    source = notebook()
    snapshot, parameters = service.promoted_notebook(source)
    op = operation()
    run_op = {key: value for key, value in op.items() if key != "requested_schema"}
    run_op.update(contract_id=None, contract_version=None, payload_sha256=None, status="succeeded",
        started_at="2026-11-01T00:00:00", completed_at="2026-11-01T00:01:00",
        stages=[{"stage": "write", "status": "passed", "evaluation_status": "fully_evaluated"}])
    run = dict(run_id="dry-run", pipeline_id=PIPELINE_ID, approval_id=None, activation_revision=None,
        execution_mode="dry_run", workspace_id="DEV", started_at="2026-11-01T00:00:00", completed_at="2026-11-01T00:01:00",
        status="dry_run_completed", boundary_completed=True, operations=[run_op], profiling=[], failures=[], warnings_json="[]",
        pipeline_version=None, promotion_id=None, governed_notebook_id=None,
        execution_identity="engineer", run_schema_version=3)
    manifest = dict(format_version=1, submission_id=str(uuid4()), pipeline_id=PIPELINE_ID,
        source_workspace_id="DEV", source_notebook_id=PIPELINE_ID, execution_workspace_id="DEV",
        source_snapshot_sha256=service.hashlib.sha256(source).hexdigest(), executed_snapshot_sha256=service.hashlib.sha256(source).hexdigest(),
        source_executable_sha256=service.notebook_executable_digest(source), executed_executable_sha256=service.notebook_executable_digest(source), snapshot_sha256=service.hashlib.sha256(snapshot).hexdigest(),
        executable_sha256=service.notebook_executable_digest(snapshot), operations=[op], tested_operations=[op], parameters=parameters,
        dry_run_id="dry-run", created_by="engineer", created_at="2026-11-01T00:01:00Z", expected_active_version=None,
        intent="deploy", retained_promotion_id=None, retained_version=None)
    package = dict(manifest=manifest, source_notebook_base64=base64.b64encode(source).decode(),
        executed_notebook_base64=base64.b64encode(source).decode(), notebook_base64=base64.b64encode(snapshot).decode(), dry_run=run, contracts={})
    package["submission_sha256"] = service.manifest_digest(package)
    return service.validate_submission(package)


def resign(package):
    """Recompute only content identity, without pretending to grant approval."""
    package["submission_sha256"] = service.manifest_digest({key: value for key, value in package.items() if key != "submission_sha256"})
    return package

def test_submission_preserves_a_registry_assigned_legacy_pipeline_id():
    """An existing Registry identity may differ from its original physical notebook ID."""
    package = package_candidate()
    package["manifest"]["pipeline_id"] = "00000000-0000-4000-8000-000000000099"
    package["dry_run"]["pipeline_id"] = package["manifest"]["pipeline_id"]
    resign(package)
    validated = service.validate_submission(package)
    assert validated["manifest"]["pipeline_id"] == "00000000-0000-4000-8000-000000000099"
    assert validated["manifest"]["source_notebook_id"] == PIPELINE_ID


@pytest.fixture
def authority(monkeypatch):
    """Simulate separate identities and I/O, leaving approval logic real."""
    tables = {service.PIPELINE_ACTIVATION_TABLE: [], service.REGISTRY_TABLE: []}
    gov = {"config": {}, "scope_workspace_id": "GOV", "user_id": "reviewer"}
    eng = {"config": {}, "scope_workspace_id": "DEV", "user_id": "engineer"}
    monkeypatch.setattr(service, "resolve_fabric_context", lambda context=None: (context["config"], context["scope_workspace_id"], context))
    monkeypatch.setattr(service, "build_runtime_audit_fields", lambda **kw: {"_committed_by": kw["runtime_context"]["user_id"]})
    monkeypatch.setattr(service, "metadata_records", lambda table, **kw: deepcopy(tables.get(table, [])))
    def mutate(table, action, *, context, **kw):
        if table == service.PIPELINE_ACTIVATION_TABLE and context["user_id"] != "reviewer":
            raise PermissionError("Fabric ACL simulation: Engineering has no Governance write access")
        proposed, result = action(deepcopy(tables[table]))
        tables[table] = deepcopy(proposed)
        return result
    monkeypatch.setattr(service, "mutate_metadata", mutate)
    monkeypatch.setattr(service, "review_submission_policy", lambda *args, **kw: {"policy": "independently reviewed"})
    return SimpleNamespace(tables=tables, gov=gov, eng=eng)


def approved(authority, package=None):
    """Import in Governance's independent session and append an explicit decision."""
    package = package or package_candidate()
    imported = service.import_pipeline_submission(canonical_pipeline_json(package), context=authority.gov)
    rows = authority.tables[service.PIPELINE_ACTIVATION_TABLE]
    return service.decide_pipeline_submission(imported["submission_id"], status="approved",
        expected_revision=max(row["revision"] for row in rows), policy={"policy": "independently reviewed"},
        review_note="Reviewed saved code and test claims independently", governance_confirmed=True, context=authority.gov)


def authorized_row(approval):
    """Construct the deployment evidence covered by one exact Governance approval."""
    package = service.validate_submission(approval["package_json"])
    manifest = package["manifest"]
    row = promotion()
    for key in ("agreement_id", "agreement_version", "agreement_sha256"):
        row.pop(key, None)
    row.update({key: manifest[key] for key in ("pipeline_id", "execution_workspace_id", "source_workspace_id", "source_notebook_id",
        "snapshot_sha256", "source_snapshot_sha256", "executable_sha256", "submission_id")})
    row.update(approval_id=approval["approval_id"], submission_sha256=package["submission_sha256"],
        operations_json=canonical_pipeline_json(manifest["operations"]), bindings_sha256=service.manifest_digest(manifest["operations"]),
        parameters_json=canonical_pipeline_json(manifest["parameters"]))
    return row


def test_portable_package_roundtrip_has_no_python_session():
    """A different process can validate all package content using only JSON."""
    candidate = package_candidate()
    assert service.validate_submission(canonical_pipeline_json(candidate)) == candidate
    assert candidate["manifest"]["source_snapshot_sha256"] != candidate["manifest"]["snapshot_sha256"]
    assert "session" not in canonical_pipeline_json(candidate)


@pytest.mark.parametrize("field", ["manifest", "notebook_base64", "source_notebook_base64", "dry_run", "contracts"])
def test_changed_or_incomplete_package_rejects(field):
    """Every component is bound by the complete digest and required structure."""
    package = package_candidate()
    package.pop(field)
    with pytest.raises(ValueError):
        service.validate_submission(package)


@pytest.mark.parametrize("change", ["execution", "saved", "operations", "result", "parameters"])
def test_rehashing_inconsistent_claims_does_not_validate_them(change):
    """Internal consistency must hold even when an engineer recomputes all content hashes."""
    package = package_candidate()
    if change == "execution": package["manifest"]["executed_snapshot_sha256"] = "f" * 64
    if change == "saved": package["source_notebook_base64"] = base64.b64encode(notebook("x = 2")).decode()
    if change == "operations": package["manifest"]["operations"][0]["write_mode"] = "scd1"
    if change == "result": package["dry_run"]["operations"][0]["stages"] = []
    if change == "parameters": package["manifest"]["parameters"]["manual"] = True
    with pytest.raises(ValueError):
        service.validate_submission(resign(package))


def test_duplicate_json_keys_reject():
    """JSON parsers must not silently choose one competing identity."""
    with pytest.raises(ValueError, match="Duplicate"):
        service.validate_submission('{"manifest":{},"manifest":{}}')


def test_engineering_can_read_but_cannot_write_governance_authority(authority):
    """The storage boundary, simulated here, denies Engineering decision mutations."""
    package = package_candidate()
    with pytest.raises(PermissionError):
        service.import_pipeline_submission(package, context=authority.eng)
    decision = approved(authority, package)
    assert service.authoritative_approval(decision["approval_id"], context=authority.eng) == decision
    with pytest.raises(PermissionError):
        service.decide_pipeline_submission(package["manifest"]["submission_id"], status="revoked", expected_revision=2,
            policy={}, review_note="Forged", governance_confirmed=True, context=authority.eng)


def test_governance_import_and_approval_never_open_source_or_deploy(authority, monkeypatch):
    """Governance needs neither an Engineering notebook API nor a Python session."""
    monkeypatch.setattr(service, "FabricNotebookClient", Mock(side_effect=AssertionError("Governance must not call Engineering APIs")))
    decision = approved(authority)
    assert decision["status"] == "approved"
    assert authority.tables[service.REGISTRY_TABLE] == []


def test_accepted_content_is_immutable_and_prior_approval_does_not_cover_change(authority):
    """Even a newly signed content digest cannot mutate an accepted identity."""
    package = package_candidate()
    decision = approved(authority, package)
    package["manifest"]["created_by"] = "different-engineer"
    resign(package)
    with pytest.raises(ValueError, match="immutable"):
        service.import_pipeline_submission(package, context=authority.gov)
    row = authorized_row(decision)
    row["submission_sha256"] = package["submission_sha256"]
    with pytest.raises(ValueError, match="differs"):
        service.verify_registry_approval(row, context=authority.eng)


@pytest.mark.parametrize("field", ["approval_id", "snapshot_sha256", "source_snapshot_sha256", "executable_sha256", "submission_id", "parameters_json", "operations_json"])
def test_registry_edits_cannot_manufacture_approval(authority, field):
    """An active Engineering row cannot authorize unrelated content or behavior."""
    row = authorized_row(approved(authority))
    row[field] = "{}" if field.endswith("json") else "forged"
    with pytest.raises((ValueError, KeyError)):
        service.verify_registry_approval(row, context=authority.eng)


def test_stale_review_revocation_and_supersession_reject(authority):
    """History is append-only, and new decisions cannot reuse a stale revision."""
    decision = approved(authority)
    with pytest.raises(ValueError, match="Stale"):
        service.decide_pipeline_submission(decision["submission_id"], status="revoked", expected_revision=1,
            policy={}, review_note="stale", governance_confirmed=True, context=authority.gov)
    newer = approved(authority)
    with pytest.raises(ValueError, match="superseded"):
        service.authoritative_approval(decision["approval_id"], context=authority.eng)
    assert service.authoritative_approval(decision["approval_id"], context=authority.eng, captured=True) == decision
    service.decide_pipeline_submission(newer["submission_id"], status="revoked", expected_revision=4,
        policy={}, review_note="Policy revoked", governance_confirmed=True, context=authority.gov)
    with pytest.raises(ValueError, match="revoked"):
        service.authoritative_approval(newer["approval_id"], context=authority.eng)
    assert len(authority.tables[service.PIPELINE_ACTIVATION_TABLE]) == 5


def test_unknown_and_unapproved_candidate_cannot_deploy(authority, monkeypatch):
    """Backend deployment checks authoritative approval independently of widget visibility."""
    imported = service.import_pipeline_submission(package_candidate(), context=authority.gov)
    monkeypatch.setattr(service, "FabricNotebookClient", Mock(side_effect=AssertionError("Unapproved candidate cannot create an item")))
    with pytest.raises(ValueError):
        service.deploy_approved_submission(imported["approval_id"], context=authority.eng)


def test_governance_operator_cannot_deploy_into_engineering(authority):
    """A Governance context cannot issue the Engineering-controlled deployment action."""
    decision = approved(authority)
    with pytest.raises(ValueError, match="Engineering execution workspace"):
        service.deploy_approved_submission(decision["approval_id"], context=authority.gov)


def test_full_deployment_readback_retry_and_distinct_identities(authority, monkeypatch):
    """Exact snapshots deploy once; retry uses persisted authority and immutable deployment identity."""
    decision = approved(authority)
    package = service.validate_submission(decision["package_json"])
    snapshot = base64.b64decode(package["notebook_base64"])
    client = Mock()
    client.find_named.return_value = None
    client.create.return_value = "new-engineering-notebook"
    client.definition.return_value = snapshot
    monkeypatch.setattr(service, "FabricNotebookClient", lambda: client)
    files = {}
    class Path:
        def __init__(self, uri): self.uri = uri
        def getName(self): return self.uri.rsplit("/", 1)[-1]
        def getFileSystem(self, _config):
            def list_status(directory):
                prefix = directory.uri.rstrip("/") + "/"
                return [SimpleNamespace(isFile=lambda: True, getPath=lambda uri=uri: Path(uri))
                    for uri in files if uri.startswith(prefix) and "/" not in uri[len(prefix):]]
            return SimpleNamespace(exists=lambda path: path.uri in files or any(uri.startswith(path.uri.rstrip("/") + "/") for uri in files),
                listStatus=list_status)
    spark = SimpleNamespace(_jvm=SimpleNamespace(org=SimpleNamespace(apache=SimpleNamespace(hadoop=SimpleNamespace(fs=SimpleNamespace(Path=Path))))),
        _jsc=SimpleNamespace(hadoopConfiguration=lambda: None))
    monkeypatch.setattr(service, "get_spark_session", lambda *a, **kw: spark)
    monkeypatch.setattr(service, "metadata_path", lambda *a, **kw: "abfss://metadata/lakehouse/Tables/engineering/registry")
    def file(uri, *, content=None, **kw):
        if content is not None:
            assert uri not in files
            files[uri] = content
        return files[uri]
    monkeypatch.setattr(service, "snapshot_file", file)
    monkeypatch.setattr(service, "resolve_promoted_operations", lambda ops, **kw: ops)
    row = service.deploy_approved_submission(decision["approval_id"], context=authority.eng)
    assert row["approval_id"] == decision["approval_id"] != row["promotion_id"]
    assert row["_committed_by"] == "engineer" and decision["_committed_by"] == "reviewer"
    assert files[row["snapshot_uri"]] == snapshot
    assert service.deploy_approved_submission(decision["approval_id"], context=authority.eng) == row
    client.create.assert_called_once()
    # Runtime freeze ignores Markdown, outputs, execution counts and cell identities.
    import json
    changed = json.loads(snapshot)
    changed["cells"][0]["source"] = "Revised Markdown"
    changed["cells"].insert(0, {"cell_type": "markdown", "source": "More notes", "metadata": {}})
    code = next(cell for cell in changed["cells"] if cell["cell_type"] == "code")
    code.update(outputs=[{"output_type": "stream", "name": "stdout", "text": "New run output"}], execution_count=99, id="new-cell-id")
    code["metadata"]["execution"] = {"duration": 999}
    client.definition.return_value = json.dumps(changed).encode()
    service.verify_promotion_integrity(row, context=authority.eng)
    code["source"] += "\nx = 2"
    client.definition.return_value = json.dumps(changed).encode()
    with pytest.raises(RuntimeError, match="integrity mismatch"):
        service.verify_promotion_integrity(row, context=authority.eng)


def test_agreement_association_not_engineering_registry_is_authority(monkeypatch):
    """Cross-workspace operations fail closed without the active Contract's exact Agreement."""
    activation = {"workspace_id": "OTHER"}
    with pytest.raises(ValueError, match="Agreement"):
        service.check_contract_agreement(activation, execution_workspace_id="DEV", context={})
    today = datetime.now(UTC).date()
    agreement = {"agreement_id": "terms", "agreement_version": "1", "start_date": today, "expiry_date": today}
    monkeypatch.setattr(service, "metadata_records", lambda *a, **kw: [agreement])
    activation.update(agreement_id="terms", agreement_version="1", agreement_sha256=service.manifest_digest(service.agreement_definition(agreement)))
    service.check_contract_agreement(activation, execution_workspace_id="DEV", context={})
    agreement["expiry_date"] = "2000-01-01"
    with pytest.raises(ValueError, match="effective"):
        service.check_contract_agreement(activation, execution_workspace_id="DEV", context={})


@pytest.fixture
def deployment_io(authority, monkeypatch):
    """Replace Fabric and Hadoop transport while retaining complete approval/deployment logic."""
    files, saved, names = {}, {}, {}
    class Path:
        def __init__(self, uri): self.uri = uri
        def getName(self): return self.uri.rsplit("/", 1)[-1]
        def getFileSystem(self, _config):
            def list_status(directory):
                prefix = directory.uri.rstrip("/") + "/"
                return [SimpleNamespace(isFile=lambda: True, getPath=lambda uri=uri: Path(uri))
                    for uri in files if uri.startswith(prefix) and "/" not in uri[len(prefix):]]
            return SimpleNamespace(exists=lambda path: path.uri in files or any(uri.startswith(path.uri.rstrip("/") + "/") for uri in files),
                listStatus=list_status)
    spark = SimpleNamespace(_jvm=SimpleNamespace(org=SimpleNamespace(apache=SimpleNamespace(hadoop=SimpleNamespace(fs=SimpleNamespace(Path=Path))))),
        _jsc=SimpleNamespace(hadoopConfiguration=lambda: None))
    monkeypatch.setattr(service, "get_spark_session", lambda *a, **kw: spark)
    monkeypatch.setattr(service, "metadata_path", lambda *a, **kw: "abfss://metadata/lakehouse/Tables/engineering/registry")
    def file(uri, *, content=None, **kw):
        if content is not None:
            if uri in files: raise FileExistsError(uri)
            files[uri] = content
        return files[uri]
    monkeypatch.setattr(service, "snapshot_file", file)
    monkeypatch.setattr(service, "resolve_promoted_operations", lambda ops, **kw: ops)
    client = Mock()
    def create(workspace, name, raw, **kwargs):
        notebook_id = "governed-" + str(len(saved) + 1)
        names[name] = notebook_id
        saved[notebook_id] = raw
        return notebook_id
    client.find_named.side_effect = lambda workspace, name: names.get(name)
    client.create.side_effect = create
    client.definition.side_effect = lambda workspace, notebook_id: saved[notebook_id]
    client.update.side_effect = lambda workspace, notebook_id, raw: saved.update({notebook_id: raw})
    monkeypatch.setattr(service, "FabricNotebookClient", lambda: client)
    return SimpleNamespace(files=files, saved=saved, names=names, client=client)


def test_rollback_requires_a_new_decision_and_allocates_a_new_version(authority, deployment_io):
    """Returning to retained code never reactivates an old immutable deployment row."""
    first = approved(authority)
    previous = service.deploy_approved_submission(first["approval_id"], context=authority.eng)
    request = service.export_retained_submission(previous["promotion_id"], intent="rollback", context=authority.eng)
    imported = service.import_pipeline_submission(request, context=authority.gov)
    with pytest.raises(ValueError):
        service.deploy_approved_submission(imported["approval_id"], context=authority.eng)
    decision = approved(authority, request)
    current = service.deploy_approved_submission(decision["approval_id"], context=authority.eng)
    assert current["pipeline_version"] == 2 and current["restored_from_version"] == 1
    assert current["governed_notebook_id"] != previous["governed_notebook_id"]
    assert authority.tables[service.REGISTRY_TABLE][0]["status"] == "superseded"
    assert previous["snapshot_uri"] == authority.tables[service.REGISTRY_TABLE][0]["snapshot_uri"]


def test_restoration_needs_separate_authority_and_preserves_modified_content(authority, deployment_io):
    """A recovery decision repairs exact current content without allocating another intended version."""
    decision = approved(authority)
    row = service.deploy_approved_submission(decision["approval_id"], context=authority.eng)
    with pytest.raises(ValueError, match="restoration authorization"):
        service.restore_promoted_notebook(PIPELINE_ID, workspace_id="DEV", expected_active_version=1,
            approval_id=decision["approval_id"], context=authority.eng)
    request = service.export_retained_submission(row["promotion_id"], intent="restore", context=authority.eng)
    recovery = approved(authority, request)
    changed = notebook("modified = True")
    deployment_io.saved[row["governed_notebook_id"]] = changed
    result = service.deploy_approved_submission(recovery["approval_id"], context=authority.eng)
    assert deployment_io.files[result["preserved_copy_uri"]] == changed
    assert result["promotion_id"] == row["promotion_id"] and result["pipeline_version"] == 1
    assert len(authority.tables[service.REGISTRY_TABLE]) == 1
    assert deployment_io.saved[row["governed_notebook_id"]] == deployment_io.files[row["snapshot_uri"]]


@pytest.mark.parametrize("failure", ["archive", "create", "readback"])
def test_staging_failures_never_change_active_registry(authority, deployment_io, monkeypatch, failure):
    """Backend failure before full verification preserves prior immutable deployment state."""
    decision = approved(authority)
    row = service.deploy_approved_submission(decision["approval_id"], context=authority.eng)
    request = service.export_retained_submission(row["promotion_id"], intent="rollback", context=authority.eng)
    newer = approved(authority, request)
    before = deepcopy(authority.tables[service.REGISTRY_TABLE])
    if failure == "archive": monkeypatch.setattr(service, "snapshot_file", Mock(side_effect=OSError("archive unavailable")))
    if failure == "create": deployment_io.client.create.side_effect = OSError("Fabric denied")
    if failure == "readback": deployment_io.client.definition.side_effect = lambda *a: notebook("altered = True")
    with pytest.raises((RuntimeError, OSError)):
        service.deploy_approved_submission(newer["approval_id"], context=authority.eng)
    assert authority.tables[service.REGISTRY_TABLE] == before


def test_approval_alone_does_not_deactivate_current_deployment(authority, deployment_io):
    """Current approved code remains executable while a newly approved candidate awaits deployment."""
    first = approved(authority)
    row = service.deploy_approved_submission(first["approval_id"], context=authority.eng)
    request = service.export_retained_submission(row["promotion_id"], intent="rollback", context=authority.eng)
    approved(authority, request)
    assert authority.tables[service.REGISTRY_TABLE][0]["status"] == "active"
    assert service.verify_promotion_integrity(row, context=authority.eng, captured=True)


def test_expired_and_rejected_authority_fail_closed(authority):
    """Persisted status or elapsed approval lifetime independently blocks deployment."""
    decision = approved(authority)
    authority.tables[service.PIPELINE_ACTIVATION_TABLE][-1]["expires_at"] = datetime(2000, 1, 1)
    with pytest.raises(ValueError, match="expired"):
        service.deploy_approved_submission(decision["approval_id"], context=authority.eng)
    package = package_candidate()
    imported = service.import_pipeline_submission(package, context=authority.gov)
    rejected = service.decide_pipeline_submission(imported["submission_id"], status="rejected", expected_revision=3,
        policy={}, review_note="Insufficient testing claims", governance_confirmed=True, context=authority.gov)
    with pytest.raises(ValueError):
        service.deploy_approved_submission(rejected["approval_id"], context=authority.eng)


def test_saved_output_changes_remain_distinct_from_executed_saved_definition():
    """Complete hashes retain both snapshots while the executed behavior must remain identical."""
    import json
    package = package_candidate()
    saved = json.loads(base64.b64decode(package["source_notebook_base64"]))
    saved["cells"][0]["source"] = "Updated review notes after the Dry Run"
    raw = json.dumps(saved).encode()
    promoted, _ = service.promoted_notebook(raw)
    package["source_notebook_base64"] = base64.b64encode(raw).decode()
    package["notebook_base64"] = base64.b64encode(promoted).decode()
    package["manifest"].update(source_snapshot_sha256=service.hashlib.sha256(raw).hexdigest(),
        snapshot_sha256=service.hashlib.sha256(promoted).hexdigest())
    assert service.validate_submission(resign(package))["manifest"]["executed_snapshot_sha256"] != package["manifest"]["source_snapshot_sha256"]


def test_durable_dry_run_does_not_serialize_the_python_session(authority, deployment_io):
    """Captured evidence is complete JSON even when the live journal contains Python-only objects."""
    import json
    package = package_candidate()
    manifest = package["manifest"]
    plan = SimpleNamespace(plan_id="dry-run", pipeline_id=PIPELINE_ID, workspace_id="DEV", notebook_id="development",
        runtime_context=authority.eng, evidence={"notebook_snapshot": base64.b64decode(package["executed_notebook_base64"]),
            "final_result": package["dry_run"], "operations": {op["operation_key"]: op for op in manifest["tested_operations"]},
            "source_observation_policy": manifest["parameters"], "session": object()}, contracts_json="{}")
    uri = service.persist_engineering_dry_run(plan)
    retained = json.loads(deployment_io.files[uri])
    assert retained["dry_run"]["run_id"] == "dry-run"
    assert "session" not in retained
    assert retained["manifest_sha256"] == service.manifest_digest({key: value for key, value in retained.items() if key != "manifest_sha256"})
    assert base64.b64decode(retained["source_notebook_base64"]) == plan.evidence["notebook_snapshot"]


def test_restoration_retry_is_audited_and_cannot_reuse_authority_for_new_edits(authority, deployment_io):
    """Recovery receipts survive independent retries and preserve the first modified copy."""
    decision = approved(authority)
    row = service.deploy_approved_submission(decision["approval_id"], context=authority.eng)
    request = service.export_retained_submission(row["promotion_id"], intent="restore", context=authority.eng)
    recovery = approved(authority, request)
    deployment_io.saved[row["governed_notebook_id"]] = notebook("first_modified = True")
    result = service.deploy_approved_submission(recovery["approval_id"], context=authority.eng)
    assert result["restored_by"] == "engineer" and result["receipt_uri"] in deployment_io.files
    count = deployment_io.client.update.call_count
    assert service.deploy_approved_submission(recovery["approval_id"], context=authority.eng) == result
    assert deployment_io.client.update.call_count == count
    deployment_io.saved[row["governed_notebook_id"]] = notebook("later_modified = True")
    with pytest.raises(ValueError, match="already used"):
        service.deploy_approved_submission(recovery["approval_id"], context=authority.eng)


def test_registry_commit_backend_requires_physical_readback_itself(authority, deployment_io):
    """Calling the low-level commit service cannot bypass complete deployed-item verification."""
    decision = approved(authority)
    row = authorized_row(decision)
    package = service.validate_submission(decision["package_json"])
    deployment_io.files[row["snapshot_uri"]] = base64.b64decode(package["notebook_base64"])
    deployment_io.files[row["source_snapshot_uri"]] = base64.b64decode(package["source_notebook_base64"])
    deployment_io.saved[row["governed_notebook_id"]] = notebook("unapproved = True")
    with pytest.raises(RuntimeError, match="integrity mismatch"):
        service.commit_pipeline_promotion(row, expected_active_version=None, context=authority.eng)
    assert authority.tables[service.REGISTRY_TABLE] == []


@pytest.mark.parametrize("mutation", ["code", "parameters", "tags", "dependencies"])
def test_runtime_output_changes_do_not_break_the_approved_implementation(authority, deployment_io, mutation):
    """Manual execution may save new output while static notebook and behavior integrity remain exact."""
    import json
    decision = approved(authority)
    row = service.deploy_approved_submission(decision["approval_id"], context=authority.eng)
    saved = json.loads(deployment_io.saved[row["governed_notebook_id"]])
    saved["cells"][1]["outputs"] = [{"output_type": "stream", "name": "stdout", "text": "new run output"}]
    saved["cells"][1]["execution_count"] = 8
    saved["cells"][1]["metadata"]["execution"] = {"time": "later"}
    deployment_io.saved[row["governed_notebook_id"]] = json.dumps(saved).encode()
    assert service.verify_promotion_integrity(row, context=authority.eng)
    if mutation == "code":
        saved["cells"][1]["source"] += "\nunapproved = True"
    elif mutation == "parameters":
        saved["cells"][1]["source"] = saved["cells"][1]["source"].replace('"Governed"', '"Ungoverned"')
    elif mutation == "tags":
        saved["cells"][1]["metadata"]["tags"] = []
    else:
        saved["metadata"]["dependencies"] = {"lakehouse": "unapproved"}
    deployment_io.saved[row["governed_notebook_id"]] = json.dumps(saved).encode()
    with pytest.raises(RuntimeError, match="integrity mismatch"):
        service.verify_promotion_integrity(row, context=authority.eng)


def test_governance_policy_review_rejects_fabricated_recovery_lineage(authority, deployment_io, monkeypatch):
    """An internally consistent package cannot invent a previously approved deployment."""
    decision = approved(authority)
    row = service.deploy_approved_submission(decision["approval_id"], context=authority.eng)
    package = service.export_retained_submission(row["promotion_id"], intent="rollback", context=authority.eng)
    package["manifest"]["retained_promotion_id"] = "fabricated"
    with pytest.raises(ValueError, match="missing or duplicated"):
        POLICY_REVIEW(resign(package), context=authority.gov)
