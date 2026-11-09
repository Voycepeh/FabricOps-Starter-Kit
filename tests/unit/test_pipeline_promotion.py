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
    from tests.unit.test_pipeline_handoff import package_candidate, resign
    package = package_candidate()
    manifest = package["manifest"]
    manifest.update(execution_workspace_id="PROD", expected_active_version=1, intent="restore", retained_promotion_id="promotion-PROD-1", retained_version=1)
    manifest["operations"] = [operation(workspace="PROD")]
    resign(package)
    monkeypatch.setattr(service, "verify_registry_approval", lambda *a, **kw: ({}, package))
    monkeypatch.setattr(service, "authoritative_approval", lambda *a, **kw: {"decision_kind": "restore", "package_json": json.dumps(package)})
    monkeypatch.setattr(service, "review_submission_policy", lambda *a, **kw: {})
    return SimpleNamespace(context=context, spark=spark, client=client, files=files, file_calls=calls)


def integrity_row(runtime):
    """Seed an archived promoted notebook and the physically saved equivalent."""
    raw, parameters = service.promoted_notebook(notebook())
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


def test_markdown_edits_preserve_executable_snapshot_integrity(runtime, monkeypatch):
    """Verify markdown only saved edits are allowed by integrity."""
    row = integrity_row(runtime)
    saved = json.loads(runtime.client.definition.return_value)
    saved["cells"][0]["source"] = "Updated notes"
    runtime.client.definition.return_value = json.dumps(saved).encode()
    monkeypatch.setattr(service, "resolve_promoted_operations", lambda ops, **kw: ops)
    assert service.verify_promotion_integrity(row, context=runtime.context) == [operation(workspace="PROD")]


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
        approval_id="recovery-approval", context=runtime.context)
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
            approval_id="recovery-approval", context=runtime.context)
    runtime.client.update.assert_not_called()


def test_old_admitted_run_can_finish_but_immutable_row_cannot_change(runtime, monkeypatch):
    """Verify old admitted run can finish but immutable row cannot change."""
    row = integrity_row(runtime)
    monkeypatch.setattr(service, "FABRIC_GOVERNED_VALIDATED", True)  # exercise logic behind the release gate only
    plan = pipeline.PipelineExecutionPlan("governed", "PROD", row["governed_notebook_id"], "run", "{}", "{}", "{}", runtime.context,
        pipeline_id=PIPELINE_ID, pipeline_version=1, promotion_id=row["promotion_id"], governed_notebook_id=row["governed_notebook_id"])
    plan.evidence["promotion"] = deepcopy(row)
    plan.evidence["contract_activations"] = []
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
    source = 'PIPELINE_MODE = "Dry Run"\npipeline = setup_pipeline(pipeline_mode=PIPELINE_MODE)\n'
    promoted, parameters = service.promoted_notebook(notebook(source))
    saved = json.loads(promoted)["cells"][1]["source"]
    assert "pipeline_id" not in saved
    assert 'pipeline_mode="Governed"' in saved
    assert parameters == {}


def test_cross_workspace_data_access_requires_an_effective_agreement():
    """An omitted Agreement cannot authorize physical data access in another workspace."""
    with pytest.raises(ValueError, match="effective Agreement"):
        service.check_contract_agreement({"workspace_id": "REMOTE"}, execution_workspace_id="PROD", context={})
