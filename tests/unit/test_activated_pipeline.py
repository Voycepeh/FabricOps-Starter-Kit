"""Direct activation validation and mandatory fail-closed deployment assurance."""
from copy import deepcopy
from datetime import date, timedelta
from types import SimpleNamespace
from uuid import uuid4
import json

import pytest

from fabricops_kit.activated_pipeline import shared as service

PIPELINE_ID = "4c7ae400-85ab-4023-9427-e8fde20bd596"


def operation(role="target", table="orders", mode="overwrite"):
    """Build one representative supported operation configuration."""
    return dict(operation_key=role + ":Silver/" + table, table_id=table, pipeline_role=role,
        destination=dict(workspace_id="DEV", item_id="item", kind="lakehouse", schema="demo", table_name=table),
        read_mode="full" if role == "source" else None, write_mode=mode if role == "target" else None,
        query_sha256=None, incremental_target_table_id=None, source_table_ids=[])


def contract_candidate(workspace="DEV", table="orders"):
    """Build an explicitly non-authorizing table candidate."""
    return dict(record_id=service.registry_record_id("table_contract_activation", workspace, table),
        record_type="table_contract_activation", schema_version=2, workspace_id=workspace,
        table_id=table, status="requires_reactivation", contract_id="contract", contract_version=1,
        payload_sha256="a" * 64,
        destination_json=json.dumps({**operation(table=table)["destination"], "workspace_id": workspace}))


def test_registry_has_three_scalar_record_types_and_no_lifecycle_arrays():
    """Canonical authority exposes SQL scalars, not obsolete collections."""
    from fabricops_kit.config.metadata_schemas import metadata_table_schema_registry
    schema = metadata_table_schema_registry()[service.REGISTRY_TABLE]
    assert not {"registrations", "approvals", "selections", "revisions", "table_ownership", "reservations"} & set(schema.fieldNames())
    assert all(not hasattr(field.dataType, "fields") and not hasattr(field.dataType, "elementType") for field in schema)
    assert len(metadata_table_schema_registry()) == 12
    assert service.registry_control([service.empty_pipeline_authority()])["leases_json"] == "[]"


@pytest.mark.parametrize("defect", ["missing_control", "duplicate_control", "business_duplicate", "wrong_key", "candidate_authority", "unknown_kind", "bad_json"])
def test_registry_rejects_ambiguous_authority(defect):
    """Malformed state never authorizes or implicitly seeds records."""
    rows = [service.empty_pipeline_authority(), contract_candidate()]
    if defect == "missing_control":
        rows = rows[1:]
    elif defect == "duplicate_control":
        rows.append(deepcopy(rows[0]))
    elif defect == "business_duplicate":
        rows.append(deepcopy(rows[1]))
    elif defect == "wrong_key":
        rows[1]["record_id"] = "other"
    elif defect == "candidate_authority":
        rows[1]["activation_id"] = str(uuid4())
    elif defect == "unknown_kind":
        rows[1]["record_type"] = "approval"
    else:
        rows[0]["leases_json"] = "not-json"
    with pytest.raises(ValueError):
        service.registry_control(rows)


@pytest.mark.parametrize("defect", ["duplicate", "strategy", "scope", "alias", "unbound_source"])
def test_activation_manifest_rejects_unsupported_or_ambiguous_operations(defect):
    """Descriptors keep real writer strategies and reject unenforced scope claims."""
    operations = [operation()]
    if defect == "duplicate":
        operations.append(operation())
    elif defect == "strategy":
        operations[0]["write_mode"] = "merge"
    elif defect == "scope":
        operations[0]["write_scope"] = "trust-me"
    elif defect == "alias":
        operations[0]["destination"]["extra"] = "ignored"
    else:
        operations[0]["source_table_ids"] = ["missing"]
    with pytest.raises(ValueError):
        service.activation_operations(json.dumps(operations))


def test_independent_contract_candidates_are_workspace_table_scoped():
    """No pipeline activation or global frozen-status fallback is needed."""
    rows = [service.empty_pipeline_authority(), contract_candidate(), contract_candidate("OTHER")]
    assert service.registry_control(rows)
    assert rows[1]["record_id"] != rows[2]["record_id"]


def test_governed_setup_and_forged_plan_fail_before_metadata_or_publication(monkeypatch):
    """Self-reported Git/deployment fields cannot bypass the pending security gate."""
    monkeypatch.setattr(service, "read_registry", lambda **kw: pytest.fail("no admission mutation permitted"))
    with pytest.raises(RuntimeError, match="trusted deployment verification"):
        service.build_governed_pipeline_plan(pipeline_id=PIPELINE_ID, context={})
    forged = SimpleNamespace(execution_mode="governed", permits_persistence=True, pipeline_activation_id="fake", git_commit_sha="a" * 40, deployment_verification_status="verified")
    with pytest.raises(RuntimeError, match="trusted deployment verification"):
        service.verify_governed_plan(forged)
    from fabricops_kit.pipeline.shared import persistence_permitted
    with pytest.raises(RuntimeError, match="trusted deployment verification"):
        persistence_permitted({"execution_plan": forged})


def test_agreement_effectiveness_is_preserved():
    """Expired and future Agreements cannot be silently accepted."""
    today = date.today()
    service.validate_agreement({"start_date": today, "expiry_date": today})
    with pytest.raises(ValueError, match="effective"):
        service.validate_agreement({"start_date": today - timedelta(days=10), "expiry_date": today - timedelta(days=1)})


def test_ungoverned_protection_includes_reactivation_candidates(monkeypatch):
    """Migration pauses Governed without opening former protected tables."""
    rows = [service.empty_pipeline_authority(), contract_candidate()]
    monkeypatch.setattr(service, "read_registry", lambda **kw: rows)
    plan = SimpleNamespace(runtime_context={"config": {}}, workspace_id="DEV", pipeline_id=PIPELINE_ID, plan_id="run", evidence={})
    with pytest.raises(ValueError, match="protected Table ID"):
        service.guard_ungoverned_write(plan, "orders", operation()["destination"])


def test_no_obsolete_lifecycle_functions_remain():
    """The new model has no wrappers for the retired approval/rebind engine."""
    for name in ("approve_pipeline_release", "review_pipeline_release", "tested_pipeline_run",
                 "activation_version", "workspace_activation", "reserve_pipeline_rebind", "release_pipeline_rebind"):
        assert not hasattr(service, name)


def test_public_contract_activation_keeps_target_and_metadata_workspace_distinct(monkeypatch):
    """Governance may select an Engineering workspace without rerouting central storage."""
    from fabricops_kit import activate_data_contract
    from fabricops_kit.config import shared as config
    captured = {}
    monkeypatch.setattr(config, "resolve_fabric_context", lambda: ({}, "governance-workspace",
        {"metadata_workspace_id": "central-metadata"}))
    def save(*args, **kwargs):
        captured.update(kwargs)
        return {"status": "active"}
    monkeypatch.setattr(service, "set_table_contract_activation", save)
    assert activate_data_contract("orders", "contract", 1, workspace_id="engineering-workspace",
        expected_token="reviewed", governance_confirmed=True)["status"] == "active"
    assert captured["context"]["scope_workspace_id"] == "engineering-workspace"
    assert captured["context"]["metadata_workspace_id"] == "central-metadata"


def test_migrated_source_binding_protects_its_original_physical_alias(monkeypatch):
    """Protected read participants cannot be overwritten under a different Table ID."""
    row = dict(record_id=service.registry_record_id("pipeline_activation", "DEV", PIPELINE_ID),
        record_type="pipeline_activation", schema_version=2, workspace_id="DEV", pipeline_id=PIPELINE_ID,
        status="requires_reactivation", operations_json=json.dumps([operation("source")]))
    rows = [service.empty_pipeline_authority(), row]
    monkeypatch.setattr(service, "read_registry", lambda **kw: rows)
    plan = SimpleNamespace(runtime_context={"config": {}}, workspace_id="DEV", pipeline_id=PIPELINE_ID,
        plan_id="alias-run", evidence={})
    with pytest.raises(ValueError, match="alias"):
        service.guard_ungoverned_write(plan, "alias", operation()["destination"])


@pytest.mark.parametrize("alias", [False, True])
def test_foreign_contract_binding_needs_no_foreign_workspace_config(monkeypatch, alias):
    """Frozen physical bindings protect aliases without foreign Catalogue/config reads."""
    from fabricops_kit.pipeline import shared as pipeline
    row = contract_candidate("PROD")
    rows = [service.empty_pipeline_authority(), row]
    monkeypatch.setattr(service, "read_registry", lambda **kw: rows)
    monkeypatch.setattr(pipeline, "resolve_catalogue_table_identity", lambda *a, **kw: pytest.fail("do not re-resolve frozen binding"))
    monkeypatch.setattr(pipeline, "pipeline_physical_bindings", lambda *a, **kw: pytest.fail("do not require foreign configuration"))
    commits = []
    monkeypatch.setattr(service, "commit_registry", lambda *a, **kw: commits.append(a))
    plan = SimpleNamespace(runtime_context={"config": {}, "scope_workspace_id": "DEV"}, workspace_id="DEV",
        pipeline_id=PIPELINE_ID, plan_id="local-run", evidence={})
    destination = json.loads(row["destination_json"]) if alias else operation(table="unrelated")["destination"]
    if alias:
        with pytest.raises(ValueError, match="physical destination alias"):
            service.guard_ungoverned_write(plan, "unrelated", destination)
        assert not commits
    else:
        service.guard_ungoverned_write(plan, "unrelated", destination)
        assert len(commits) == 1 and plan.evidence["lease_token"] == "local-run"


@pytest.mark.parametrize("value", [None, "{}", "not-json"])
def test_contract_activation_rejects_missing_or_invalid_frozen_binding(value):
    """Missing physical evidence must never bypass alias protection."""
    row = {**contract_candidate(), "destination_json": value}
    with pytest.raises(ValueError):
        service.registry_control([service.empty_pipeline_authority(), row])


def test_target_lease_excludes_another_run_and_physical_alias(monkeypatch):
    """A published hash snapshot remains protected until finalization releases the lease."""
    rows = [service.empty_pipeline_authority()]
    monkeypatch.setattr(service, 'read_registry', lambda **kw: rows)
    monkeypatch.setattr(service, 'commit_registry', lambda *a, **kw: None)
    def plan(run):
        return SimpleNamespace(runtime_context={}, workspace_id='DEV', pipeline_id=PIPELINE_ID, plan_id=run, evidence={})
    first = plan('first')
    service.guard_ungoverned_write(first, 'orders', operation()['destination'])
    service.guard_ungoverned_write(first, 'orders', operation()['destination'])
    with pytest.raises(RuntimeError, match='publication lease'):
        service.guard_ungoverned_write(plan('second'), 'physical-alias', operation()['destination'])
    service.guard_ungoverned_write(plan('second'), 'other', operation(table='other')['destination'])
