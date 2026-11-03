"""Promotion staging, cross-workspace routing, integrity and exact restoration."""
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import Mock
import hashlib
import json

import pytest

from fabricops_kit.activated_pipeline import shared as service
from fabricops_kit.pipeline import shared as pipeline
from tests.unit.test_activated_pipeline import PIPELINE_ID, notebook, operation, promotion


@pytest.fixture
def runtime(monkeypatch):
    """Keep domain logic real while replacing Fabric and physical metadata services."""
    context = {"config": {}, "scope_workspace_id": "PROD", "notebook_id": "governed-PROD-1", "user_id": "runtime-principal"}
    monkeypatch.setattr(service, "resolve_fabric_context", lambda context=None: (context["config"], context["scope_workspace_id"], context))
    spark = SimpleNamespace(_jvm=SimpleNamespace(org=SimpleNamespace(apache=SimpleNamespace(hadoop=SimpleNamespace(fs=SimpleNamespace(
        Path=lambda uri: SimpleNamespace(getFileSystem=lambda conf: SimpleNamespace(exists=lambda path: False))))))),
        _jsc=SimpleNamespace(hadoopConfiguration=lambda: None))
    monkeypatch.setattr(service, "get_spark_session", lambda *a, **kw: spark)
    monkeypatch.setattr(service, "metadata_path", lambda *a, **kw: "abfss://metadata/house/Tables/engineering/REGISTRY")
    monkeypatch.setattr(service, "build_runtime_audit_fields", lambda **kw: {"_committed_by": "governance"})
    client = Mock()
    monkeypatch.setattr(service, "FabricNotebookClient", lambda: client)
    files, calls = {}, []
    def file(uri, *, content=None, **kw):
        calls.append((uri, content))
        if content is not None:
            if uri in files:
                raise FileExistsError(uri)
            files[uri] = content
        if uri not in files:
            raise FileNotFoundError(uri)
        return files[uri]
    monkeypatch.setattr(service, "snapshot_file", file)
    return SimpleNamespace(context=context, spark=spark, client=client, files=files, file_calls=calls)


def staged_review(runtime):
    """Return an exact hashed human review of a new cross-workspace promotion."""
    raw = notebook()
    promoted, parameters = service.promoted_notebook(raw, PIPELINE_ID)
    row = promotion(workspace="PROD")
    for key in ("governed_notebook_id", "snapshot_uri", "source_snapshot_uri", "promoted_by", "promoted_at"):
        row.pop(key)
    row.update(source_workspace_id="DEV", source_notebook_id="development", snapshot_sha256=hashlib.sha256(promoted).hexdigest(),
        source_snapshot_sha256=hashlib.sha256(raw).hexdigest(), executable_sha256=service.notebook_executable_digest(promoted),
        parameters_json=json.dumps(parameters), bindings_sha256=service.manifest_digest([operation(workspace="PROD")]))
    review = dict(candidate=row, snapshot=promoted, source_snapshot=raw, context=runtime.context, expected_active_version=None, contracts={})
    review["review_sha256"] = service.promotion_review_digest(review)
    runtime.client.definition.return_value = promoted
    runtime.client.create.return_value = "separate-governed-notebook"
    return review


def stage_services(monkeypatch, records=None):
    """Keep review and sequencing while replacing only metadata/domain discovery."""
    monkeypatch.setattr(service, "read_registry", lambda **kw: records or [])
    monkeypatch.setattr(service, "resolve_promoted_operations", lambda ops, **kw: ops)
    monkeypatch.setattr(service, "reviewed_contracts", lambda *a, **kw: {})


def test_cross_workspace_stage_archives_full_notebooks_before_clone_and_commit(runtime, monkeypatch):
    """Verify cross workspace stage archives full notebooks before clone and commit."""
    review = staged_review(runtime)
    stage_services(monkeypatch)
    commits = []
    monkeypatch.setattr(service, "commit_pipeline_promotion", lambda row, **kw: commits.append(deepcopy(row)) or row)
    result = service.stage_pipeline_promotion(review, governance_confirmed=True)
    assert result["execution_workspace_id"] == "PROD"
    assert result["source_workspace_id"] == "DEV"
    assert result["governed_notebook_id"] != result["source_notebook_id"]
    assert runtime.files[result["snapshot_uri"]] == review["snapshot"]
    assert runtime.files[result["source_snapshot_uri"]] == review["source_snapshot"]
    runtime.client.create.assert_called_once()
    assert runtime.client.create.call_args.args[0] == "PROD"
    runtime.client.governed_folder.assert_not_called()
    assert len(commits) == 1


@pytest.mark.parametrize("failure", ["archive", "clone", "readback", "config", "contracts", "review"])
def test_staging_failures_never_switch_previous_authority(runtime, monkeypatch, failure):
    """Verify staging failures never switch previous authority."""
    review = staged_review(runtime)
    stage_services(monkeypatch)
    commit = Mock(side_effect=AssertionError("failed staging cannot change authority"))
    monkeypatch.setattr(service, "commit_pipeline_promotion", commit)
    if failure == "archive": monkeypatch.setattr(service, "snapshot_file", Mock(side_effect=OSError("archive unavailable")))
    if failure == "clone": runtime.client.create.side_effect = OSError("API unavailable")
    if failure == "readback": runtime.client.definition.return_value = notebook("x = 1")
    if failure == "config": monkeypatch.setattr(service, "resolve_promoted_operations", lambda ops, **kw: [operation(workspace="DEV")])
    if failure == "contracts": monkeypatch.setattr(service, "reviewed_contracts", lambda *a, **kw: {"orders": {"contract_id": "new", "contract_version": 2, "contract_payload_json": "{}"}})
    if failure == "review": review["snapshot"] += b" "
    with pytest.raises((OSError, RuntimeError, ValueError)):
        service.stage_pipeline_promotion(review, governance_confirmed=True)
    commit.assert_not_called()


def test_same_workspace_uses_governed_folder_and_new_item(runtime, monkeypatch):
    """Verify same workspace uses governed folder and new item."""
    review = staged_review(runtime)
    review["candidate"]["source_workspace_id"] = "PROD"
    review["review_sha256"] = service.promotion_review_digest(review)
    stage_services(monkeypatch)
    runtime.client.governed_folder.return_value = "folder"
    monkeypatch.setattr(service, "commit_pipeline_promotion", lambda row, **kw: row)
    result = service.stage_pipeline_promotion(review, governance_confirmed=True)
    runtime.client.governed_folder.assert_called_once_with("PROD")
    assert runtime.client.create.call_args.kwargs["folder_id"] == "folder"
    assert result["governed_notebook_id"] != "development"


def integrity_row(runtime):
    """Seed an archived promoted notebook and the physically saved equivalent."""
    raw, parameters = service.promoted_notebook(notebook(), PIPELINE_ID)
    row = promotion(workspace="PROD")
    row.update(snapshot_sha256=hashlib.sha256(raw).hexdigest(), executable_sha256=service.notebook_executable_digest(raw),
        bindings_sha256=service.manifest_digest([operation(workspace="PROD")]), parameters_json=json.dumps(parameters))
    runtime.files[row["snapshot_uri"]] = raw
    runtime.files[row["source_snapshot_uri"]] = notebook()
    row["source_snapshot_sha256"] = hashlib.sha256(notebook()).hexdigest()
    runtime.client.definition.return_value = raw
    return row


@pytest.mark.parametrize("failure", ["missing", "corrupt", "code", "binding", "api"])
def test_managed_integrity_fails_closed_for_each_unverifiable_boundary(runtime, monkeypatch, failure):
    """Verify managed integrity fails closed for each unverifiable boundary."""
    row = integrity_row(runtime)
    monkeypatch.setattr(service, "resolve_promoted_operations", lambda ops, **kw: ops)
    if failure == "missing": runtime.files.clear()
    if failure == "corrupt": runtime.files[row["snapshot_uri"]] += b" "
    if failure == "code": runtime.client.definition.return_value = notebook("x = 2")
    if failure == "binding": monkeypatch.setattr(service, "resolve_promoted_operations", lambda ops, **kw: [operation(workspace="DEV")])
    if failure == "api": runtime.client.definition.side_effect = RuntimeError("verifier unavailable")
    with pytest.raises((FileNotFoundError, RuntimeError)):
        service.verify_promotion_integrity(row, context=runtime.context)


def test_markdown_only_saved_edits_are_allowed_by_integrity(runtime, monkeypatch):
    """Verify markdown only saved edits are allowed by integrity."""
    row = integrity_row(runtime)
    saved = json.loads(runtime.client.definition.return_value)
    saved["cells"][0]["source"] = "Updated notes"
    runtime.client.definition.return_value = json.dumps(saved).encode()
    monkeypatch.setattr(service, "resolve_promoted_operations", lambda ops, **kw: ops)
    assert service.verify_promotion_integrity(row, context=runtime.context)


def test_exact_restoration_preserves_changed_copy_before_update(runtime, monkeypatch):
    """Verify exact restoration preserves changed copy before update."""
    row = integrity_row(runtime)
    archived = runtime.files[row["snapshot_uri"]]
    changed = notebook("changed = True")
    runtime.client.definition.side_effect = [changed, archived, archived]
    monkeypatch.setattr(service, "read_registry", lambda **kw: [deepcopy(row)])
    monkeypatch.setattr(service, "resolve_promoted_operations", lambda ops, **kw: ops)
    def update(workspace, notebook_id, raw):
        assert raw == archived
        assert changed in runtime.files.values(), "preserve before replacing code"
    runtime.client.update.side_effect = update
    result = service.restore_promoted_notebook(PIPELINE_ID, workspace_id="PROD", expected_active_version=1,
        governance_confirmed=True, context=runtime.context)
    assert runtime.files[result["preserved_copy_uri"]] == changed
    assert result["promotion_id"] == row["promotion_id"]
    assert result["ready"] is False


def test_restoration_never_overwrites_when_changed_copy_cannot_be_retained(runtime, monkeypatch):
    """Verify restoration never overwrites when changed copy cannot be retained."""
    row = integrity_row(runtime)
    monkeypatch.setattr(service, "read_registry", lambda **kw: [row])
    monkeypatch.setattr(service, "resolve_promoted_operations", lambda ops, **kw: ops)
    original = service.snapshot_file
    monkeypatch.setattr(service, "snapshot_file", lambda uri, **kw: original(uri, **kw) if kw.get("content") is None else (_ for _ in ()).throw(OSError("permission denied")))
    with pytest.raises(OSError, match="permission"):
        service.restore_promoted_notebook(PIPELINE_ID, workspace_id="PROD", expected_active_version=1,
            governance_confirmed=True, context=runtime.context)
    runtime.client.update.assert_not_called()


def test_old_admitted_run_can_finish_but_immutable_row_cannot_change(runtime, monkeypatch):
    """Verify old admitted run can finish but immutable row cannot change."""
    row = integrity_row(runtime)
    monkeypatch.setattr(service, "FABRIC_GOVERNED_VALIDATED", True)  # exercise logic behind the release gate only
    plan = pipeline.PipelineExecutionPlan("governed", "PROD", row["governed_notebook_id"], "run", "{}", "{}", "{}", runtime.context,
        pipeline_id=PIPELINE_ID, pipeline_version=1, promotion_id=row["promotion_id"], governed_notebook_id=row["governed_notebook_id"])
    plan.evidence["promotion"] = deepcopy(row)
    row["status"] = "superseded"
    monkeypatch.setattr(service, "read_registry", lambda **kw: [deepcopy(row)])
    monkeypatch.setattr(service, "resolve_promoted_operations", lambda ops, **kw: ops)
    service.verify_governed_plan(plan)
    row["executable_sha256"] = "e"*64
    with pytest.raises(RuntimeError, match="immutable approval changed"):
        service.verify_governed_plan(plan)


def test_new_start_against_superseded_notebook_rejects_before_api(runtime, monkeypatch):
    """Verify new start against superseded notebook rejects before api."""
    row = promotion(2, workspace="PROD")
    monkeypatch.setattr(service, "FABRIC_GOVERNED_VALIDATED", True)
    monkeypatch.setattr(service, "read_registry", lambda **kw: [row])
    with pytest.raises(RuntimeError, match="stale schedule|superseded"):
        service.build_governed_pipeline_plan(pipeline_id=PIPELINE_ID, context=runtime.context)
    runtime.client.definition.assert_not_called()


def test_destination_configuration_resolves_physical_workspace_and_item():
    """Promotion resolves the destination's store mapping, including intentional remote stores."""
    from fabricops_kit.config import FabricStore, FrameworkConfig, PathConfig
    metadata = FabricStore(workspace_id="CENTRAL", item_id="metadata", kind="lakehouse", schema_enabled=True, schema="engineering")
    config = FrameworkConfig(path_config=PathConfig(paths={
        "DEV": {"Silver": FabricStore(workspace_id="DEV", item_id="dev-item", kind="lakehouse", schema_enabled=True, schema="demo"), "Metadata": metadata},
        "PROD": {"Silver": FabricStore(workspace_id="REMOTE", item_id="approved-item", kind="lakehouse", schema_enabled=True, schema="demo"), "Metadata": metadata},
    }))
    identity = pipeline.resolve_physical_table_identity(config, "DEV", store="Silver", schema="demo", table_name="orders")
    op = operation(); op["table_id"] = identity["table_id"]
    resolved = service.resolve_promoted_operations([op], context={"config": config, "scope_workspace_id": "PROD"})
    assert resolved[0]["destination"] == {"workspace_id": "REMOTE", "item_id": "approved-item", "kind": "lakehouse", "schema": "demo", "table_name": "orders"}
    assert resolved[0]["table_id"] == identity["table_id"]
    with pytest.raises(ValueError, match="not found"):
        service.resolve_promoted_operations([op], context={"config": config, "scope_workspace_id": "MISSING"})


def test_fabric_definition_decoder_rejects_ambiguous_or_extra_parts():
    """Only one complete supported ipynb definition may authorize notebook verification."""
    import base64
    client = object.__new__(service.FabricNotebookClient)
    workspace = "00000000-0000-4000-8000-000000000001"
    notebook_id = "00000000-0000-4000-8000-000000000002"
    part = {"path": "notebook-content.ipynb", "payloadType": "InlineBase64", "payload": base64.b64encode(notebook()).decode()}
    client.request = Mock(return_value={"definition": {"parts": [part]}})
    assert client.definition(workspace, notebook_id) == notebook()
    for parts in ([], [part, part], [part, {"path": "unverified.py"}]):
        client.request.return_value = {"definition": {"parts": parts}}
        with pytest.raises(RuntimeError, match="missing or unsupported"):
            client.definition(workspace, notebook_id)


def test_fabric_long_running_request_fetches_operation_result(monkeypatch):
    """A successful 202 operation fetches its documented result before using the definition."""
    from urllib import request
    import time
    responses = iter([(202, {"Location": "https://api.fabric.microsoft.com/v1/operations/op", "Retry-After": "0"}, {}),
        (200, {}, {"status": "Succeeded"}), (200, {}, {"definition": {"parts": []}})])
    calls = []
    class Response:
        def __enter__(self):
            self.status, self.headers, self.body = next(responses)
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return json.dumps(self.body).encode()
    monkeypatch.setattr(request, "urlopen", lambda req, **kw: calls.append((req.method, req.full_url)) or Response())
    monkeypatch.setattr(time, "sleep", lambda delay: None)
    client = object.__new__(service.FabricNotebookClient); client.token = "test-runtime-token"
    assert client.request("POST", "/workspaces/test/notebooks/test/getDefinition") == {"definition": {"parts": []}}
    assert calls[-1] == ("GET", "https://api.fabric.microsoft.com/v1/operations/op/result")


def test_fabric_rejects_foreign_operation_location_before_sending_token(monkeypatch):
    """Fabric long-running operation locations cannot redirect credentials to another host."""
    from urllib import request
    import time
    class Response:
        status = 202
        headers = {"Location": "https://other.example/v1/operation", "Retry-After": "0"}
        def __enter__(self): return self
        def __exit__(self, *args): return False
        def read(self): return b"{}"
    calls = []
    monkeypatch.setattr(request, "urlopen", lambda req, **kw: calls.append(req.full_url) or Response())
    monkeypatch.setattr(time, "sleep", lambda delay: None)
    client = object.__new__(service.FabricNotebookClient); client.token = "test-token"
    with pytest.raises(RuntimeError, match="Unexpected Fabric operation URL"):
        client.request("POST", "/workspaces/test/notebooks")
    assert len(calls) == 1


def test_standard_template_saved_constants_are_frozen_in_cloned_setup():
    """Saved literal scaffold constants become exact startup literals in the Governed copy."""
    source = f'PIPELINE_ID = "{PIPELINE_ID}"\nPIPELINE_MODE = "Dry Run"\npipeline = setup_pipeline(pipeline_id=PIPELINE_ID, pipeline_mode=PIPELINE_MODE)\nPIPELINE_ID = pipeline.pipeline_id\n'
    promoted, parameters = service.promoted_notebook(notebook(source), PIPELINE_ID)
    saved = json.loads(promoted)["cells"][1]["source"]
    assert f"pipeline_id='{PIPELINE_ID}'" in saved
    assert 'pipeline_mode="Governed"' in saved
    assert parameters == {"manual": False, "days": None}


def test_cross_workspace_data_access_requires_an_effective_agreement():
    """An omitted Agreement cannot authorize physical data access in another workspace."""
    candidate = promotion(workspace="PROD")
    candidate["operations_json"] = json.dumps([operation(workspace="REMOTE")])
    with pytest.raises(ValueError, match="exact effective Data Agreement"):
        service.check_promotion_agreement(candidate, context={})
