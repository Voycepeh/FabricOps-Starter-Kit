"""Native widgets keep Governance decisions and Engineering deployment separate."""
# ruff: noqa: F811 -- shared pytest fixture imported for collection
import importlib
from unittest.mock import Mock

import pytest

from tests.unit.test_pipeline_handoff import authority, approved, package_candidate, deployment_io, resign


def render(monkeypatch, module, context):
    """Render actual ipywidgets while replacing only runtime services."""
    from IPython import display as ip
    monkeypatch.setattr(ip, "display", lambda *a, **kw: None)
    monkeypatch.setattr(module, "resolve_fabric_context", lambda context=None: ({}, context_value["scope_workspace_id"], context_value))
    context_value = context
    monkeypatch.setattr(module, "get_spark_session", lambda **kw: object())


def test_governance_reviews_saved_submission_without_file_transfer(authority, deployment_io, monkeypatch):
    """Opening and reviewing the actual widget never calls Engineering notebook APIs."""
    module = importlib.import_module("fabricops_kit.widgets.widget_activate_pipeline")
    render(monkeypatch, module, authority.gov)
    monkeypatch.setattr(module, "review_submission_policy", lambda *a, **kw: {"policy": "independently reviewed"})
    package = package_candidate()
    from fabricops_kit.activated_pipeline import shared as service
    service.persist_engineering_submission(package, context=authority.eng)
    ui = module.widget_activate_pipeline()
    ui["controls"]["submission"].value = package["manifest"]["submission_id"]
    assert authority.tables[module.read_registry.__globals__["REGISTRY_TABLE"]] == []
    assert ui["ready"] is False
    assert authority.tables[service.PIPELINE_ACTIVATION_TABLE] == []
    assert "import" not in ui["actions"] and "package" not in ui["controls"]
    deployment_io.client.definition.assert_not_called()
    assert ui["controls"]["decide"].disabled
    with pytest.raises(ValueError, match="Review"):
        ui["actions"]["decide"]()
    ui["actions"]["review"]()
    ui["controls"]["note"].value = "Reviewed code and test claims independently"
    ui["controls"]["confirm"].value = True
    result = ui["actions"]["decide"]()
    assert result["status"] == "approved" and result["_committed_by"] == "reviewer"
    assert authority.tables["METADATA_PIPELINE_REGISTRY"] == []
    assert not any(name in ui["actions"] for name in ("promote", "deploy"))


def test_governance_decision_change_invalidates_review(authority, deployment_io, monkeypatch):
    """A different candidate, decision or filter requires another review."""
    module = importlib.import_module("fabricops_kit.widgets.widget_activate_pipeline")
    render(monkeypatch, module, authority.gov)
    monkeypatch.setattr(module, "review_submission_policy", lambda *a, **kw: {"policy": "independently reviewed"})
    package = package_candidate()
    from fabricops_kit.activated_pipeline import shared as service
    service.persist_engineering_submission(package, context=authority.eng)
    ui = module.widget_activate_pipeline()
    ui["controls"]["submission"].value = package["manifest"]["submission_id"]
    ui["actions"]["review"]()
    ui["controls"]["confirm"].value = True
    assert not ui["controls"]["decide"].disabled
    ui["controls"]["decision"].value = "rejected"
    assert ui["state"]["review"] is None and ui["controls"]["decide"].disabled


def test_engineering_deployment_is_explicit_and_cannot_decide(authority, monkeypatch):
    """Engineering reviews persisted Governance authority in an independent widget session."""
    module = importlib.import_module("fabricops_kit.activated_pipeline.shared")
    decision = approved(authority)
    render(monkeypatch, module, authority.eng)
    deploy = Mock(return_value={"status": "active"})
    monkeypatch.setattr(module, "deploy_approved_submission", deploy)
    ui = module.display_pipeline_handoff(pipeline_id=decision["pipeline_id"])
    assert "export" not in ui["controls"]
    assert ui["controls"]["deploy"].disabled
    with pytest.raises(ValueError, match="Review"):
        ui["actions"]["deploy"]()
    ui["controls"]["approval"].value = decision["approval_id"]
    ui["actions"]["review"]()
    ui["controls"]["confirm"].value = True
    assert ui["actions"]["deploy"]()["status"] == "active"
    assert deploy.call_args.args == (decision["approval_id"],)
    assert "decide" not in ui["actions"]


def test_finalize_handoff_exports_once_and_reopens_same_package(authority, monkeypatch):
    """Repeated Finalize rendering reuses submission identity without creating notebooks."""
    from types import SimpleNamespace
    module = importlib.import_module("fabricops_kit.activated_pipeline.shared")
    render(monkeypatch, module, authority.eng)
    package = package_candidate()
    export = Mock(return_value=package)
    deploy = Mock()
    monkeypatch.setattr(module, "export_pipeline_submission", export)
    monkeypatch.setattr(module, "deploy_approved_submission", deploy)
    session = SimpleNamespace(plan=SimpleNamespace(evidence={}, pipeline_id=package["manifest"]["pipeline_id"]), spark=object())
    first = module.display_pipeline_handoff(dry_run=session, context=authority.eng)
    second = module.display_pipeline_handoff(dry_run=session, context=authority.eng)
    assert first["state"]["package"] == second["state"]["package"] == package
    assert package["manifest"]["submission_id"] in first["controls"]["submission"].value
    assert dict(second["controls"]["intent"].options)["Restore the active notebook"] == "restore"
    export.assert_called_once()
    deploy.assert_not_called()


@pytest.mark.parametrize("change", ["changed", "deleted"])
def test_pending_submission_is_rechecked_before_review(authority, deployment_io, monkeypatch, change):
    """A file changed/deleted after refresh cannot silently become the reviewed copy."""
    import json
    from fabricops_kit.activated_pipeline import shared as service
    module = importlib.import_module("fabricops_kit.widgets.widget_activate_pipeline")
    package = package_candidate()
    uri = service.persist_engineering_submission(package, context=authority.eng)
    render(monkeypatch, module, authority.gov)
    ui = module.widget_activate_pipeline()
    ui["controls"]["submission"].value = package["manifest"]["submission_id"]
    if change == "changed":
        package["manifest"]["created_at"] = "2026-11-02T00:01:00Z"
        deployment_io.files[uri] = json.dumps(resign(package)).encode()
    else:
        del deployment_io.files[uri]
    with pytest.raises((ValueError, KeyError, FileNotFoundError)):
        ui["actions"]["review"]()
    assert authority.tables[service.PIPELINE_ACTIVATION_TABLE] == []
    assert ui["controls"]["decide"].disabled


def test_governance_decides_review_copy_after_engineering_file_changes(authority, deployment_io, monkeypatch):
    """The protected review copy, not the Engineering file, controls approval."""
    import json
    from fabricops_kit.activated_pipeline import shared as service
    module = importlib.import_module("fabricops_kit.widgets.widget_activate_pipeline")
    package = package_candidate()
    original_sha = package["submission_sha256"]
    uri = service.persist_engineering_submission(package, context=authority.eng)
    render(monkeypatch, module, authority.gov)
    monkeypatch.setattr(module, "review_submission_policy", lambda *a, **kw: {"policy": "independently reviewed"})
    ui = module.widget_activate_pipeline()
    ui["controls"]["submission"].value = package["manifest"]["submission_id"]
    ui["actions"]["review"]()
    package["manifest"]["created_at"] = "2026-11-02T00:01:00Z"
    deployment_io.files[uri] = json.dumps(resign(package)).encode()
    ui["controls"]["note"].value = "Reviewed protected snapshot"
    ui["controls"]["confirm"].value = True
    result = ui["actions"]["decide"]()
    assert result["submission_sha256"] == original_sha
    assert json.loads(result["package_json"])["submission_sha256"] == original_sha
    assert result["status"] == "approved"
    deployment_io.client.create.assert_not_called()


def test_submission_discovery_reports_bad_files_without_hiding_valid_packages(authority, deployment_io):
    """Discovery reads the configured Files location and creates no approval authority."""
    from uuid import uuid4
    from fabricops_kit.activated_pipeline import shared as service
    assert service.list_pipeline_submissions(context=authority.gov) == {"submissions": [], "errors": []}
    package = package_candidate()
    uri = service.persist_engineering_submission(package, context=authority.eng)
    bad_uri = uri.rsplit("/", 1)[0] + "/" + str(uuid4()) + ".json"
    deployment_io.files[bad_uri] = b"not valid JSON"
    listing = service.list_pipeline_submissions(context=authority.gov)
    assert listing["submissions"] == [package]
    assert len(listing["errors"]) == 1
    assert authority.tables[service.PIPELINE_ACTIVATION_TABLE] == []


def test_recovery_requests_appear_directly_in_governance(authority, deployment_io, monkeypatch):
    """Engineering recovery submission becomes selectable without download/import."""
    from fabricops_kit.activated_pipeline import shared as service
    decision = approved(authority)
    row = service.deploy_approved_submission(decision["approval_id"], context=authority.eng)
    request = service.export_retained_submission(row["promotion_id"], intent="restore", context=authority.eng)
    module = importlib.import_module("fabricops_kit.widgets.widget_activate_pipeline")
    render(monkeypatch, module, authority.gov)
    ui = module.widget_activate_pipeline()
    ui["controls"]["submission"].value = request["manifest"]["submission_id"]
    assert ui["state"]["pending"][request["manifest"]["submission_id"]]["manifest"]["intent"] == "restore"
    assert not any(r["submission_id"] == request["manifest"]["submission_id"] for r in authority.tables[service.PIPELINE_ACTIVATION_TABLE])


def test_unavailable_pending_store_does_not_block_revocation(authority, monkeypatch):
    """Storage discovery errors are visible while protected decisions remain manageable."""
    from types import SimpleNamespace
    from fabricops_kit.activated_pipeline import shared as service
    decision = approved(authority)
    module = importlib.import_module("fabricops_kit.widgets.widget_activate_pipeline")
    render(monkeypatch, module, authority.gov)
    class UnavailablePath:
        def __init__(self, _uri): pass
        def getFileSystem(self, _config): raise PermissionError("Files unavailable")
    spark = SimpleNamespace(_jvm=SimpleNamespace(org=SimpleNamespace(apache=SimpleNamespace(hadoop=SimpleNamespace(fs=SimpleNamespace(Path=UnavailablePath))))),
        _jsc=SimpleNamespace(hadoopConfiguration=lambda: None))
    monkeypatch.setattr(service, "get_spark_session", lambda *a, **kw: spark)
    monkeypatch.setattr(service, "metadata_path", lambda *a, **kw: "abfss://metadata/lakehouse/Tables/engineering/registry")
    ui = module.widget_activate_pipeline()
    assert ui["state"]["submission_errors"][0]["error"] == "PermissionError"
    ui["controls"]["submission"].value = decision["submission_id"]
    ui["controls"]["decision"].value = "revoked"
    ui["actions"]["review"]()
    ui["controls"]["note"].value = "Revoke the protected decision"
    ui["controls"]["confirm"].value = True
    assert ui["actions"]["decide"]()["status"] == "revoked"
